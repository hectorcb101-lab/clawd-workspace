"""
Atlas Self-Awareness System - Query Interface

Natural language queries about my own performance and patterns.
This is how I ask questions about myself.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .database import db_session, get_stats
from .analyzer import (
    detect_failure_patterns, detect_strength_patterns,
    compute_trends, run_full_analysis
)
from .logger import get_outcome_summary, get_correction_summary


def query_strengths(days: int = 30, min_attempts: int = 3) -> Dict[str, Any]:
    """
    What am I good at?
    
    Returns strength analysis with evidence.
    """
    patterns = detect_strength_patterns(min_occurrences=min_attempts, days=days)
    
    # Get raw success data
    with db_session() as conn:
        top_performers = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                ROUND(AVG(confidence), 2) as avg_confidence
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING total >= ?
            ORDER BY (successes * 1.0 / total) DESC
            LIMIT 10
        """, (f'-{days} days', min_attempts)).fetchall()
    
    return {
        'query': 'What am I good at?',
        'period_days': days,
        'strengths': patterns,
        'top_performers': [dict(r) for r in top_performers],
        'summary': _summarize_strengths(patterns),
        'queried_at': datetime.utcnow().isoformat()
    }


def query_weaknesses(days: int = 30, min_attempts: int = 2) -> Dict[str, Any]:
    """
    What do I struggle with?
    
    Returns failure patterns and weak areas.
    """
    patterns = detect_failure_patterns(min_occurrences=min_attempts, days=days)
    
    # Get raw failure data
    with db_session() as conn:
        weak_areas = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failures,
                SUM(CASE WHEN outcome = 'partial' THEN 1 ELSE 0 END) as partials
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING failures > 0 OR partials > 0
            ORDER BY (failures + partials * 0.5) DESC
            LIMIT 10
        """, (f'-{days} days',)).fetchall()
        
        # Recent corrections
        corrections = conn.execute("""
            SELECT correction_type, COUNT(*) as count
            FROM corrections
            WHERE created_at >= datetime('now', ?)
            GROUP BY correction_type
            ORDER BY count DESC
        """, (f'-{days} days',)).fetchall()
    
    return {
        'query': 'What do I struggle with?',
        'period_days': days,
        'failure_patterns': patterns,
        'weak_areas': [dict(r) for r in weak_areas],
        'correction_types': {r['correction_type']: r['count'] for r in corrections},
        'summary': _summarize_weaknesses(patterns),
        'queried_at': datetime.utcnow().isoformat()
    }


def query_blind_spots(days: int = 30) -> Dict[str, Any]:
    """
    What am I missing? What don't I know about myself?
    
    Identifies gaps in self-awareness:
    - Task types with no outcomes logged
    - Low-confidence assessments
    - Areas with no recent activity
    - Potential biases in self-assessment
    """
    blind_spots = []
    
    with db_session() as conn:
        # 1. Low confidence outcomes (uncertain self-assessment)
        low_confidence = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM outcomes
            WHERE confidence < 0.5
            AND created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING count >= 2
        """, (f'-{days} days',)).fetchall()
        
        if low_confidence:
            for r in low_confidence:
                blind_spots.append({
                    'type': 'uncertain_assessment',
                    'description': f"Uncertain about {r['task_type']} outcomes (avg confidence: {r['avg_confidence']:.0%})",
                    'task_type': r['task_type'],
                    'count': r['count'],
                    'suggestion': f"Pay more attention to {r['task_type']} outcomes, seek clearer feedback"
                })
        
        # 2. High unknown rate (can't tell if success or failure)
        unknown_heavy = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'unknown' THEN 1 ELSE 0 END) as unknowns
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING unknowns > 0 AND (unknowns * 1.0 / total) > 0.3
        """, (f'-{days} days',)).fetchall()
        
        if unknown_heavy:
            for r in unknown_heavy:
                rate = r['unknowns'] / r['total']
                blind_spots.append({
                    'type': 'outcome_unclear',
                    'description': f"Can't determine outcomes for {r['task_type']} ({rate:.0%} unknown)",
                    'task_type': r['task_type'],
                    'unknown_rate': rate,
                    'suggestion': f"Establish clearer success criteria for {r['task_type']}"
                })
        
        # 3. Self-assessment vs user feedback discrepancy
        discrepancy = conn.execute("""
            SELECT 
                o.task_type,
                SUM(CASE WHEN o.feedback_source = 'self' AND o.outcome = 'success' THEN 1 ELSE 0 END) as self_success,
                SUM(CASE WHEN o.feedback_source = 'user' AND o.outcome = 'success' THEN 1 ELSE 0 END) as user_success,
                SUM(CASE WHEN o.feedback_source = 'self' THEN 1 ELSE 0 END) as self_total,
                SUM(CASE WHEN o.feedback_source = 'user' THEN 1 ELSE 0 END) as user_total
            FROM outcomes o
            WHERE o.created_at >= datetime('now', ?)
            GROUP BY o.task_type
            HAVING self_total >= 3 AND user_total >= 2
        """, (f'-{days} days',)).fetchall()
        
        for r in discrepancy:
            if r['self_total'] > 0 and r['user_total'] > 0:
                self_rate = r['self_success'] / r['self_total']
                user_rate = r['user_success'] / r['user_total']
                gap = self_rate - user_rate
                
                if gap > 0.2:  # I think I'm doing better than Finn says
                    blind_spots.append({
                        'type': 'overconfidence',
                        'description': f"May be overconfident in {r['task_type']} (self: {self_rate:.0%}, user: {user_rate:.0%})",
                        'task_type': r['task_type'],
                        'self_success_rate': self_rate,
                        'user_success_rate': user_rate,
                        'gap': gap,
                        'suggestion': f"Calibrate expectations for {r['task_type']}, seek more user feedback"
                    })
                elif gap < -0.2:  # I'm being too hard on myself
                    blind_spots.append({
                        'type': 'underconfidence',
                        'description': f"May be underconfident in {r['task_type']} (self: {self_rate:.0%}, user: {user_rate:.0%})",
                        'task_type': r['task_type'],
                        'self_success_rate': self_rate,
                        'user_success_rate': user_rate,
                        'gap': gap,
                        'suggestion': f"Give myself more credit for {r['task_type']}"
                    })
        
        # 4. Correction patterns not reflected in outcomes
        correction_tasks = conn.execute("""
            SELECT DISTINCT task_type FROM corrections
            WHERE task_type IS NOT NULL
            AND created_at >= datetime('now', ?)
        """, (f'-{days} days',)).fetchall()
        
        correction_task_types = {r['task_type'] for r in correction_tasks}
        
        outcome_tasks = conn.execute("""
            SELECT DISTINCT task_type FROM outcomes
            WHERE outcome = 'failure'
            AND created_at >= datetime('now', ?)
        """, (f'-{days} days',)).fetchall()
        
        outcome_task_types = {r['task_type'] for r in outcome_tasks}
        
        # Corrections without corresponding failure logs
        unlogged = correction_task_types - outcome_task_types
        if unlogged:
            for task in unlogged:
                blind_spots.append({
                    'type': 'unlogged_failures',
                    'description': f"Corrections in {task} but no failures logged",
                    'task_type': task,
                    'suggestion': f"Log failures in {task} more consistently"
                })
    
    return {
        'query': 'What are my blind spots?',
        'period_days': days,
        'blind_spots': blind_spots,
        'count': len(blind_spots),
        'summary': _summarize_blind_spots(blind_spots),
        'queried_at': datetime.utcnow().isoformat()
    }


def query_progress(task_type: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    Am I getting better?
    
    Shows improvement or regression over time.
    """
    trends = compute_trends(period_type='week', lookback=max(4, days // 7))
    
    if task_type:
        trends = [t for t in trends if t['task_type'] == task_type]
    
    # Categorize trends
    improving = [t for t in trends if t['trend'] == 'improving']
    declining = [t for t in trends if t['trend'] == 'declining']
    stable = [t for t in trends if t['trend'] == 'stable']
    
    return {
        'query': f'Am I getting better{" at " + task_type if task_type else ""}?',
        'period_days': days,
        'improving': improving,
        'declining': declining,
        'stable': stable,
        'all_trends': trends,
        'summary': _summarize_progress(improving, declining, stable),
        'queried_at': datetime.utcnow().isoformat()
    }


def query_natural(question: str, days: int = 30) -> Dict[str, Any]:
    """
    Natural language query interface.
    
    Parses a question and routes to the appropriate query function.
    """
    question_lower = question.lower()
    
    # Pattern matching for common questions
    patterns = [
        (r'(what am i|my) (good at|strengths?|best at)', 'strengths'),
        (r'(what do i|where do i) (struggle|fail|weak)', 'weaknesses'),
        (r'(blind spot|missing|don\'t know|gap)', 'blind_spots'),
        (r'(getting better|improving|progress|trend)', 'progress'),
        (r'(how am i doing|overall|health|status)', 'health'),
    ]
    
    query_type = None
    for pattern, qtype in patterns:
        if re.search(pattern, question_lower):
            query_type = qtype
            break
    
    # Extract task type if mentioned
    task_type = None
    for known_type in ['coding', 'research', 'communication', 'planning', 'memory']:
        if known_type in question_lower:
            task_type = known_type
            break
    
    # Route to appropriate function
    if query_type == 'strengths':
        result = query_strengths(days=days)
    elif query_type == 'weaknesses':
        result = query_weaknesses(days=days)
    elif query_type == 'blind_spots':
        result = query_blind_spots(days=days)
    elif query_type == 'progress':
        result = query_progress(task_type=task_type, days=days)
    elif query_type == 'health':
        result = run_full_analysis(days=days)
    else:
        # Default: general analysis
        result = run_full_analysis(days=days)
        result['note'] = "Couldn't parse specific question, showing general analysis"
    
    result['original_question'] = question
    result['detected_query_type'] = query_type
    
    return result


# Summary generators

def _summarize_strengths(patterns: List[Dict]) -> str:
    if not patterns:
        return "Not enough data to identify clear strengths yet. Keep logging outcomes!"
    
    top = patterns[0]
    if 'success_rate' in top:
        return f"Strongest area: {top['task_type']} ({top['success_rate']:.0%} success rate)"
    elif 'change' in top:
        return f"Most improved: {top['task_type']} (+{top['change']:.0%})"
    return f"Key strength: {top['description']}"


def _summarize_weaknesses(patterns: List[Dict]) -> str:
    if not patterns:
        return "No significant failure patterns detected. Either doing well or need more data!"
    
    high_severity = [p for p in patterns if p.get('severity') == 'high']
    if high_severity:
        return f"⚠️ {len(high_severity)} high-severity issue(s): {high_severity[0]['description']}"
    
    return f"Found {len(patterns)} pattern(s) to watch. Top: {patterns[0]['description']}"


def _summarize_blind_spots(blind_spots: List[Dict]) -> str:
    if not blind_spots:
        return "No obvious blind spots detected. Good self-awareness!"
    
    types = set(b['type'] for b in blind_spots)
    
    if 'overconfidence' in types:
        return "⚠️ Possible overconfidence in some areas. Calibration needed."
    if 'uncertain_assessment' in types:
        return "Some outcomes have low confidence. Seek clearer feedback."
    
    return f"Found {len(blind_spots)} blind spot(s) to address."


def _summarize_progress(improving: List, declining: List, stable: List) -> str:
    if not improving and not declining and not stable:
        return "Not enough trend data yet. Need more time and outcomes."
    
    if improving and not declining:
        tasks = ', '.join(t['task_type'] for t in improving[:3])
        return f"📈 Improving in: {tasks}"
    elif declining and not improving:
        tasks = ', '.join(t['task_type'] for t in declining[:3])
        return f"📉 Declining in: {tasks}"
    elif improving and declining:
        return f"Mixed: {len(improving)} improving, {len(declining)} declining"
    else:
        return "Stable performance across tracked areas"
