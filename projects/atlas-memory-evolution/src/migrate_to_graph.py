#!/usr/bin/env python3
"""
Migrate existing facts to the knowledge graph with:
1. Proper entity linking
2. Question forms for semantic retrieval
"""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from knowledge_graph import KnowledgeGraph, Entity, Fact


# Known entities for linking
KNOWN_ENTITIES = {
    "person": ["finn", "atlas", "anthropic", "claude"],
    "project": [
        "msc", "six nations", "polymarket", "memory system", "clawdbot", 
        "socialflow", "event log", "knowledge graph", "intelligence briefing",
        "yahoo finance", "reddit", "kanban"
    ],
    "concept": [
        "work schedule", "learning style", "communication", "engineering",
        "preferences", "memory", "chess"
    ],
    "tool": [
        "telegram", "email", "google workspace", "exa", "mcporter"
    ]
}


def extract_entities_from_text(text: str) -> list:
    """Find which known entities are mentioned in text."""
    text_lower = text.lower()
    found = []
    
    for entity_type, entities in KNOWN_ENTITIES.items():
        for entity in entities:
            if entity in text_lower:
                found.append(entity)
    
    return found


def generate_question_forms(category: str, subject: str, content: str) -> list:
    """Generate questions this fact might answer."""
    questions = []
    content_lower = content.lower()
    
    # Category-based questions
    if category == "preference":
        questions.extend([
            f"what does {subject} prefer",
            f"what are {subject}'s preferences",
            f"how does {subject} like",
        ])
    elif category == "decision":
        questions.extend([
            f"what did {subject} decide",
            f"why did {subject}",
        ])
    elif category == "learning":
        questions.extend([
            f"what did I learn",
            f"what was learned about",
        ])
    
    # Content-based questions
    
    # Work/schedule - be VERY precise, only match schedule-related contexts
    work_schedule_phrases = [
        "prefer to work", "prefer working", "work schedule", "work hours",
        "early morning", "late at night", "night owl", "early bird", 
        "morning person", "work late", "work early"
    ]
    if any(phrase in content_lower for phrase in work_schedule_phrases):
        questions.extend([
            "when does finn work",
            "when does finn prefer to work", 
            "what time does finn work",
            "work schedule",
            "work hours",
            "night owl",
            "early bird",
            "morning person",
        ])
    
    # Learning style
    if any(w in content_lower for w in ["learn", "study", "visual", "practice", "understand"]):
        questions.extend([
            "how does finn learn",
            "learning style",
            "how to teach finn",
        ])
    
    # Communication
    if any(w in content_lower for w in ["email", "telegram", "file", "send", "message", "communication"]):
        questions.extend([
            "how to send files to finn",
            "communication preferences",
            "how to contact finn",
        ])
    
    # Chess
    if "chess" in content_lower:
        questions.extend([
            "does finn play chess",
            "finn chess",
            "tactics",
        ])
    
    # British/UK
    if any(w in content_lower for w in ["british", "uk", "england", "london"]):
        questions.extend([
            "where is finn from",
            "finn location",
            "timezone",
        ])
    
    return list(set(questions))  # Dedupe


def migrate_facts():
    """Migrate facts from old format to knowledge graph."""
    
    # Load existing facts
    old_facts_file = Path(__file__).parent.parent / "data" / "knowledge" / "facts.jsonl"
    if not old_facts_file.exists():
        print("No existing facts found")
        return
    
    graph = KnowledgeGraph()
    
    # First, add all known entities
    for entity_type, entities in KNOWN_ENTITIES.items():
        for entity in entities:
            graph.add_entity(entity_type, entity.title())
    
    # Process each fact
    migrated = 0
    skipped = 0
    
    with open(old_facts_file) as f:
        for line in f:
            if not line.strip():
                continue
            
            try:
                old_fact = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            
            content = old_fact.get("content", "")
            subject = old_fact.get("subject", "")
            category = old_fact.get("category", "learning")
            
            # Skip garbage (sentence fragments that got extracted as entities)
            if len(content) < 20 or len(subject) > 100:
                skipped += 1
                continue
            
            # Extract entities mentioned
            linked = extract_entities_from_text(f"{subject} {content}")
            
            # Generate question forms
            questions = generate_question_forms(category, subject, content)
            
            # Add to graph
            fact = graph.add_fact(
                category=category,
                subject=subject,
                content=content,
                linked_entities=linked,
                question_forms=questions,
                source_event_id=old_fact.get("source_event_id", "")
            )
            
            migrated += 1
    
    # Save the graph
    graph.save()
    
    print(f"Migration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped: {skipped}")
    print(f"\nGraph stats: {graph.stats()}")


if __name__ == "__main__":
    migrate_facts()
