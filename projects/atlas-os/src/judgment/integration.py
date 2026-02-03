"""
Integration between Judgment Layer and other Atlas systems.
- Self-Awareness: patterns/insights → principle proposals
- Self-Modification: principles → behavior modifications
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

# Add paths for other Atlas systems
sys.path.insert(0, str(Path.home() / "clawd" / "projects" / "atlas-self-awareness" / "src"))
sys.path.insert(0, str(Path.home() / "clawd" / "projects" / "atlas-self-modification" / "src"))

from .storage import JudgmentStorage
from .models import Principle, PrincipleCategory, PrincipleSource


def get_self_awareness_patterns() -> List[dict]:
    """
    Get patterns from self-awareness that might inform principles.
    Returns patterns with high occurrence or significance.
    """
    import sqlite3
    
    db_path = Path.home() / "clawd" / "projects" / "atlas-self-awareness" / "data" / "self_awareness.db"
    
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        patterns = []
        
        # Query for recurring corrections
        rows = conn.execute("""
            SELECT correction_type, COUNT(*) as count, 
                   GROUP_CONCAT(lesson, ' | ') as lessons
            FROM corrections
            GROUP BY correction_type
            HAVING count >= 2
            ORDER BY count DESC
        """).fetchall()
        
        for row in rows:
            patterns.append({
                "type": "correction_pattern",
                "category": row["correction_type"],
                "count": row["count"],
                "lessons": row["lessons"],
                "significance": "high" if row["count"] >= 3 else "medium"
            })
        
        # Query for task type failures
        rows = conn.execute("""
            SELECT task_type, 
                   SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failures,
                   COUNT(*) as total
            FROM outcomes
            GROUP BY task_type
            HAVING total >= 3
        """).fetchall()
        
        for row in rows:
            if row["total"] > 0:
                failure_rate = row["failures"] / row["total"]
                if failure_rate >= 0.3:  # 30%+ failure rate
                    patterns.append({
                        "type": "failure_pattern",
                        "category": row["task_type"],
                        "failure_rate": failure_rate,
                        "total": row["total"],
                        "failures": row["failures"],
                        "significance": "high" if failure_rate >= 0.5 else "medium"
                    })
        
        conn.close()
        return patterns
        
    except Exception as e:
        print(f"Warning: Could not read self-awareness data: {e}")
        return []


def propose_principle_from_pattern(pattern: dict, storage: JudgmentStorage) -> Optional[str]:
    """
    Propose a new principle based on a detected pattern.
    Returns the principle ID if created, None if not applicable.
    """
    if pattern["type"] == "correction_pattern":
        # Check if we already have a principle for this
        existing = storage.search_principles([pattern["category"]])
        if existing:
            # Might update existing instead of creating new
            return None
        
        # Create principle from correction pattern
        content = f"When working on {pattern['category']} tasks, apply lessons learned from past corrections."
        rationale = f"Detected {pattern['count']} corrections in this area. Lessons: {pattern['lessons'][:200]}"
        
        principle_id = storage.get_next_principle_id()
        principle = Principle(
            id=principle_id,
            category=PrincipleCategory.METACOGNITIVE,
            content=content,
            rationale=rationale,
            keywords=[pattern["category"], "correction", "learning"],
            source=PrincipleSource.INSIGHT,
            confidence=0.5,  # Start lower, needs validation
            priority=6,
        )
        storage.save_principle(principle)
        return principle_id
    
    elif pattern["type"] == "failure_pattern":
        content = f"Before {pattern['category']} tasks, pause and plan — this is a weak area with {pattern['failure_rate']*100:.0f}% failure rate."
        rationale = f"Self-awareness detected systematic failures in {pattern['category']} ({pattern['failures']}/{pattern['total']} failed)."
        
        principle_id = storage.get_next_principle_id()
        principle = Principle(
            id=principle_id,
            category=PrincipleCategory.DECISION,
            content=content,
            rationale=rationale,
            keywords=[pattern["category"], "weakness", "planning"],
            source=PrincipleSource.INSIGHT,
            confidence=0.6,
            priority=7,
        )
        storage.save_principle(principle)
        return principle_id
    
    return None


def sync_with_self_awareness(storage: JudgmentStorage) -> dict:
    """
    Sync judgment layer with self-awareness insights.
    - Check for new patterns
    - Propose principles for significant patterns
    - Update principle confidence based on outcomes
    """
    results = {
        "patterns_found": 0,
        "principles_proposed": 0,
        "principles_updated": 0,
    }
    
    patterns = get_self_awareness_patterns()
    results["patterns_found"] = len(patterns)
    
    for pattern in patterns:
        if pattern.get("significance") == "high":
            principle_id = propose_principle_from_pattern(pattern, storage)
            if principle_id:
                results["principles_proposed"] += 1
    
    return results


def get_principles_for_task(task_description: str, task_type: str = None, stakes: str = "medium") -> List[Tuple[Principle, float]]:
    """
    Get relevant principles for a task with relevance scores.
    
    Args:
        task_description: What the task is
        task_type: Optional type (coding, research, communication, etc.)
        stakes: low/medium/high/critical
        
    Returns:
        List of (Principle, relevance_score) tuples, sorted by relevance
    """
    storage = JudgmentStorage()
    
    # Extract keywords from description
    words = task_description.lower().split()
    stop_words = {"i", "am", "the", "a", "an", "to", "for", "of", "and", "or", "is", "it", "this", "that", "need", "want", "should"}
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Add task type as keyword if provided
    if task_type:
        keywords.append(task_type.lower())
    
    # Get all active principles
    all_principles = storage.list_principles(active_only=True)
    
    scored = []
    for p in all_principles:
        score = 0.0
        
        # Keyword matching
        principle_text = f"{p.content} {p.rationale} {' '.join(p.keywords)}".lower()
        for kw in keywords:
            if kw in principle_text:
                score += 0.2
        
        # Stakes matching for escalation principles
        if p.category == PrincipleCategory.ESCALATION:
            if stakes in ["high", "critical"]:
                score += 0.3
        
        # Priority weighting
        score += p.priority * 0.05
        
        # Confidence weighting
        score += p.confidence * 0.1
        
        # Effectiveness bonus (if we have data)
        if p.effectiveness and p.effectiveness > 0.7:
            score += 0.2
        
        if score > 0:
            scored.append((p, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    
    storage.close()
    return scored[:5]  # Top 5


def format_principles_for_context(principles: List[Tuple[Principle, float]]) -> str:
    """
    Format principles for inclusion in decision-making context.
    Returns a concise string suitable for system prompt or thinking.
    """
    if not principles:
        return ""
    
    lines = ["**Relevant Judgment Principles:**"]
    for p, score in principles:
        lines.append(f"- [{p.id}] {p.content}")
        if p.examples:
            lines.append(f"  → e.g., {p.examples[0]}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test integration
    storage = JudgmentStorage()
    
    print("Testing self-awareness sync...")
    results = sync_with_self_awareness(storage)
    print(f"  Patterns found: {results['patterns_found']}")
    print(f"  Principles proposed: {results['principles_proposed']}")
    
    print("\nTesting principle retrieval...")
    principles = get_principles_for_task(
        "I need to send an important email to a professor",
        task_type="communication",
        stakes="high"
    )
    print(format_principles_for_context(principles))
    
    storage.close()
