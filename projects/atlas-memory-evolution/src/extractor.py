#!/usr/bin/env python3
"""
Atlas Knowledge Extractor
=========================
Extracts structured knowledge from raw events.

Takes events → produces facts, entities, relationships.
This is where raw logs become usable memory.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from event_schema import Event, EventType
from event_log import get_log


@dataclass
class ExtractedFact:
    """A fact extracted from an event."""
    category: str           # preference, decision, learning, person, project, technical
    subject: str            # What/who this is about
    content: str            # The actual fact
    confidence: float       # 0-1 how confident we are
    source_event_id: str    # Which event this came from
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "subject": self.subject,
            "content": self.content,
            "confidence": self.confidence,
            "source_event_id": self.source_event_id,
            "timestamp": self.timestamp
        }


@dataclass  
class ExtractedEntity:
    """An entity (person, project, concept) extracted from events."""
    entity_type: str        # person, project, concept, tool, location
    name: str               # Canonical name
    aliases: List[str]      # Other names/references
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_seen: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "name": self.name,
            "aliases": self.aliases,
            "attributes": self.attributes,
            "first_seen": self.first_seen
        }


@dataclass
class ExtractedRelationship:
    """A relationship between entities."""
    source_entity: str      # Entity name
    relationship: str       # Type of relationship
    target_entity: str      # Entity name
    context: str = ""       # Additional context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_entity,
            "relationship": self.relationship,
            "target": self.target_entity,
            "context": self.context
        }


class RuleBasedExtractor:
    """
    Extracts knowledge using pattern matching and heuristics.
    
    This is the fast, cheap extractor. Use for high-volume, low-complexity events.
    For complex extraction, use the LLM-based extractor.
    """
    
    # Patterns for entity recognition
    PERSON_PATTERNS = [
        r'\b(Finn|Atlas|Anthropic|Claude)\b',
        r'user[:\s]+([A-Z][a-z]+)',
        r'from[:\s]+([A-Z][a-z]+)',
    ]
    
    PROJECT_PATTERNS = [
        r'(Six Nations|MSc|Polymarket|memory system|event log)',
        r'project[:\s]+([^\.,]+)',
        r'building[:\s]+([^\.,]+)',
    ]
    
    DECISION_PATTERNS = [
        r'decided to (.+?)(?:\.|$)',
        r'will (.+?)(?:\.|$)',
        r'chose (.+?)(?:\.|$)',
        r'going to (.+?)(?:\.|$)',
    ]
    
    LEARNING_PATTERNS = [
        r'learned that (.+?)(?:\.|$)',
        r'realized (.+?)(?:\.|$)',
        r'discovered (.+?)(?:\.|$)',
        r'found out (.+?)(?:\.|$)',
    ]
    
    PREFERENCE_PATTERNS = [
        r'prefers? (.+?)(?:\.|$)',
        r'wants? (.+?)(?:\.|$)',
        r'likes? (.+?)(?:\.|$)',
        r'should always (.+?)(?:\.|$)',
    ]
    
    def extract_from_event(self, event: Event) -> Tuple[List[ExtractedFact], List[ExtractedEntity], List[ExtractedRelationship]]:
        """Extract all knowledge from a single event."""
        facts = []
        entities = []
        relationships = []
        
        # Get text content
        text = self._get_event_text(event)
        if not text:
            return facts, entities, relationships
        
        # Extract based on event type
        if event.type == EventType.LEARNING:
            facts.extend(self._extract_learnings(event, text))
            
        elif event.type == EventType.DECISION:
            facts.extend(self._extract_decisions(event, text))
            
        elif event.type in (EventType.MESSAGE_IN, EventType.MESSAGE_OUT):
            # Extract entities mentioned
            entities.extend(self._extract_entities(text, event.timestamp))
            # Extract any embedded facts
            facts.extend(self._extract_embedded_facts(event, text))
            
        # Always try to extract entities
        entities.extend(self._extract_entities(text, event.timestamp))
        
        # Dedupe entities by name
        seen = set()
        unique_entities = []
        for e in entities:
            if e.name.lower() not in seen:
                seen.add(e.name.lower())
                unique_entities.append(e)
        
        return facts, unique_entities, relationships
    
    def _get_event_text(self, event: Event) -> str:
        """Extract searchable text from event content."""
        content = event.content
        
        if isinstance(content, str):
            return content
        
        if isinstance(content, dict):
            # Try common keys
            for key in ['text', 'summary', 'content', 'what', 'message']:
                if key in content:
                    return str(content[key])
            
            # Stringify the whole thing
            return json.dumps(content)
        
        return str(content)
    
    def _extract_learnings(self, event: Event, text: str) -> List[ExtractedFact]:
        """Extract learning facts."""
        facts = []
        
        summary = event.content.get('summary', text)
        details = event.content.get('details', '')
        
        fact = ExtractedFact(
            category="learning",
            subject=summary[:50],
            content=f"{summary}. {details}".strip(),
            confidence=0.8,
            source_event_id=event.id
        )
        facts.append(fact)
        
        return facts
    
    def _extract_decisions(self, event: Event, text: str) -> List[ExtractedFact]:
        """Extract decision facts."""
        facts = []
        
        what = event.content.get('what', text)
        why = event.content.get('why', '')
        
        fact = ExtractedFact(
            category="decision",
            subject=what[:50],
            content=f"Decision: {what}. Reason: {why}".strip(),
            confidence=0.9,
            source_event_id=event.id
        )
        facts.append(fact)
        
        return facts
    
    def _extract_embedded_facts(self, event: Event, text: str) -> List[ExtractedFact]:
        """Extract facts embedded in messages."""
        facts = []
        
        # Look for preferences
        for pattern in self.PREFERENCE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = ExtractedFact(
                    category="preference",
                    subject="User preference",
                    content=match.strip(),
                    confidence=0.6,
                    source_event_id=event.id
                )
                facts.append(fact)
        
        # Look for decisions
        for pattern in self.DECISION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 10:  # Filter noise
                    fact = ExtractedFact(
                        category="decision",
                        subject="Mentioned decision",
                        content=match.strip(),
                        confidence=0.5,
                        source_event_id=event.id
                    )
                    facts.append(fact)
        
        return facts
    
    def _extract_entities(self, text: str, timestamp: str) -> List[ExtractedEntity]:
        """Extract entities from text."""
        entities = []
        
        # Find people
        for pattern in self.PERSON_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 1:  # Filter single chars
                    entity = ExtractedEntity(
                        entity_type="person",
                        name=match,
                        aliases=[],
                        first_seen=timestamp
                    )
                    entities.append(entity)
        
        # Find projects
        for pattern in self.PROJECT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 3:
                    entity = ExtractedEntity(
                        entity_type="project",
                        name=match.strip(),
                        aliases=[],
                        first_seen=timestamp
                    )
                    entities.append(entity)
        
        return entities


class KnowledgeStore:
    """
    Stores extracted knowledge.
    
    For now, uses JSON files. Later, can migrate to proper graph DB.
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or "/home/ubuntu/clawd/projects/atlas-memory-evolution/data/knowledge")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.facts_file = self.base_dir / "facts.jsonl"
        self.entities_file = self.base_dir / "entities.json"
        self.relationships_file = self.base_dir / "relationships.jsonl"
        
        # Load existing entities
        self.entities: Dict[str, ExtractedEntity] = self._load_entities()
        self._processed_events: set = self._load_processed()
    
    def _load_entities(self) -> Dict[str, ExtractedEntity]:
        """Load existing entities."""
        if self.entities_file.exists():
            with open(self.entities_file) as f:
                data = json.load(f)
                return {
                    name: ExtractedEntity(**e) 
                    for name, e in data.items()
                }
        return {}
    
    def _load_processed(self) -> set:
        """Load IDs of already-processed events."""
        processed_file = self.base_dir / "processed_events.json"
        if processed_file.exists():
            with open(processed_file) as f:
                return set(json.load(f))
        return set()
    
    def _save_processed(self):
        """Save processed event IDs."""
        processed_file = self.base_dir / "processed_events.json"
        with open(processed_file, 'w') as f:
            json.dump(list(self._processed_events), f)
    
    def is_processed(self, event_id: str) -> bool:
        """Check if event was already processed."""
        return event_id in self._processed_events
    
    def mark_processed(self, event_id: str):
        """Mark event as processed."""
        self._processed_events.add(event_id)
        self._save_processed()
    
    def add_fact(self, fact: ExtractedFact):
        """Add a fact to storage."""
        with open(self.facts_file, 'a') as f:
            f.write(json.dumps(fact.to_dict()) + "\n")
    
    def add_entity(self, entity: ExtractedEntity):
        """Add or update an entity."""
        key = entity.name.lower()
        
        if key in self.entities:
            # Merge
            existing = self.entities[key]
            existing.aliases = list(set(existing.aliases + entity.aliases))
            existing.attributes.update(entity.attributes)
        else:
            self.entities[key] = entity
        
        # Save
        with open(self.entities_file, 'w') as f:
            json.dump({k: v.to_dict() for k, v in self.entities.items()}, f, indent=2)
    
    def add_relationship(self, rel: ExtractedRelationship):
        """Add a relationship."""
        with open(self.relationships_file, 'a') as f:
            f.write(json.dumps(rel.to_dict()) + "\n")
    
    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        facts_count = 0
        if self.facts_file.exists():
            with open(self.facts_file) as f:
                facts_count = sum(1 for _ in f)
        
        rels_count = 0
        if self.relationships_file.exists():
            with open(self.relationships_file) as f:
                rels_count = sum(1 for _ in f)
        
        return {
            "facts": facts_count,
            "entities": len(self.entities),
            "relationships": rels_count,
            "processed_events": len(self._processed_events)
        }


def run_extraction(limit: int = None):
    """Run extraction on unprocessed events."""
    log = get_log()
    extractor = RuleBasedExtractor()
    store = KnowledgeStore()
    
    stats = {"events": 0, "facts": 0, "entities": 0, "relationships": 0}
    
    for event in log.query(limit=limit):
        if store.is_processed(event.id):
            continue
        
        facts, entities, relationships = extractor.extract_from_event(event)
        
        for fact in facts:
            store.add_fact(fact)
            stats["facts"] += 1
        
        for entity in entities:
            store.add_entity(entity)
            stats["entities"] += 1
        
        for rel in relationships:
            store.add_relationship(rel)
            stats["relationships"] += 1
        
        store.mark_processed(event.id)
        stats["events"] += 1
    
    return stats


if __name__ == "__main__":
    print("Atlas Knowledge Extractor")
    print("=" * 40)
    
    # Run extraction
    print("\n--- Running extraction ---")
    stats = run_extraction()
    
    print(f"\nProcessed {stats['events']} events:")
    print(f"  Facts extracted:         {stats['facts']}")
    print(f"  Entities recognized:     {stats['entities']}")
    print(f"  Relationships found:     {stats['relationships']}")
    
    # Show storage stats
    print("\n--- Knowledge Store ---")
    store = KnowledgeStore()
    store_stats = store.get_stats()
    for k, v in store_stats.items():
        print(f"  {k}: {v}")
    
    print("\n✅ Extraction complete!")
