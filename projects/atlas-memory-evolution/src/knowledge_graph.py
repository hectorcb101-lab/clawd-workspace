#!/usr/bin/env python3
"""
Atlas Knowledge Graph
=====================
Phase 3: Connect facts with entities and relationships.

The graph structure:
- Entities: People, projects, concepts, tools, preferences
- Relationships: created, knows, prefers, decided, learned, uses
- Facts: Connected to entities they mention

This enables queries like:
- "What does Finn prefer?" → All preference facts linked to Finn
- "What did I build?" → All projects linked to Atlas via 'created'
- "When does Finn work?" → Preference facts about work schedule
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
import hashlib

sys.path.insert(0, str(Path(__file__).parent))


# === Data Structures ===

@dataclass
class Entity:
    """A node in the knowledge graph."""
    id: str                          # Lowercase canonical name
    entity_type: str                 # person, project, concept, tool, preference_topic
    name: str                        # Display name
    aliases: Set[str] = field(default_factory=set)
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_seen: str = ""
    last_updated: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "name": self.name,
            "aliases": list(self.aliases),
            "attributes": self.attributes,
            "first_seen": self.first_seen,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Entity':
        return cls(
            id=d["id"],
            entity_type=d["entity_type"],
            name=d["name"],
            aliases=set(d.get("aliases", [])),
            attributes=d.get("attributes", {}),
            first_seen=d.get("first_seen", ""),
            last_updated=d.get("last_updated", "")
        )


@dataclass
class Relationship:
    """An edge in the knowledge graph."""
    source_id: str                   # Entity id
    rel_type: str                    # prefers, created, knows, uses, learned, decided
    target_id: str                   # Entity id or fact id
    context: str = ""                # Additional context
    timestamp: str = ""
    source_event_id: str = ""        # Which event this came from
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_id,
            "rel_type": self.rel_type,
            "target": self.target_id,
            "context": self.context,
            "timestamp": self.timestamp,
            "source_event_id": self.source_event_id
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Relationship':
        return cls(
            source_id=d["source"],
            rel_type=d["rel_type"],
            target_id=d["target"],
            context=d.get("context", ""),
            timestamp=d.get("timestamp", ""),
            source_event_id=d.get("source_event_id", "")
        )


@dataclass
class Fact:
    """A fact in the knowledge graph, linked to entities."""
    id: str
    category: str                    # preference, decision, learning, technical
    subject: str
    content: str
    confidence: float = 1.0
    timestamp: str = ""
    source_event_id: str = ""
    linked_entities: List[str] = field(default_factory=list)  # Entity IDs
    
    # For semantic search
    question_forms: List[str] = field(default_factory=list)  # Questions this fact answers
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "subject": self.subject,
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "source_event_id": self.source_event_id,
            "linked_entities": self.linked_entities,
            "question_forms": self.question_forms
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Fact':
        return cls(
            id=d["id"],
            category=d["category"],
            subject=d["subject"],
            content=d["content"],
            confidence=d.get("confidence", 1.0),
            timestamp=d.get("timestamp", ""),
            source_event_id=d.get("source_event_id", ""),
            linked_entities=d.get("linked_entities", []),
            question_forms=d.get("question_forms", [])
        )


# === Knowledge Graph ===

class KnowledgeGraph:
    """
    The knowledge graph - entities, relationships, and facts.
    
    Storage: JSON files for simplicity (can migrate to SQLite if needed)
    """
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "graph"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.facts: Dict[str, Fact] = {}
        
        self._load()
    
    # === Persistence ===
    
    def _load(self):
        """Load graph from disk."""
        # Entities
        entities_file = self.data_dir / "entities.json"
        if entities_file.exists():
            with open(entities_file) as f:
                data = json.load(f)
                self.entities = {k: Entity.from_dict(v) for k, v in data.items()}
        
        # Relationships
        rels_file = self.data_dir / "relationships.jsonl"
        if rels_file.exists():
            self.relationships = []
            with open(rels_file) as f:
                for line in f:
                    if line.strip():
                        self.relationships.append(Relationship.from_dict(json.loads(line)))
        
        # Facts
        facts_file = self.data_dir / "facts.jsonl"
        if facts_file.exists():
            self.facts = {}
            with open(facts_file) as f:
                for line in f:
                    if line.strip():
                        fact = Fact.from_dict(json.loads(line))
                        self.facts[fact.id] = fact
    
    def save(self):
        """Save graph to disk."""
        # Entities
        entities_file = self.data_dir / "entities.json"
        with open(entities_file, 'w') as f:
            json.dump({k: v.to_dict() for k, v in self.entities.items()}, f, indent=2)
        
        # Relationships
        rels_file = self.data_dir / "relationships.jsonl"
        with open(rels_file, 'w') as f:
            for rel in self.relationships:
                f.write(json.dumps(rel.to_dict()) + "\n")
        
        # Facts
        facts_file = self.data_dir / "facts.jsonl"
        with open(facts_file, 'w') as f:
            for fact in self.facts.values():
                f.write(json.dumps(fact.to_dict()) + "\n")
    
    # === Entity Management ===
    
    def add_entity(self, entity_type: str, name: str, aliases: List[str] = None) -> Entity:
        """Add or update an entity."""
        entity_id = self._normalize_id(name)
        now = datetime.now(timezone.utc).isoformat()
        
        if entity_id in self.entities:
            # Update existing
            entity = self.entities[entity_id]
            if aliases:
                entity.aliases.update(aliases)
            entity.last_updated = now
        else:
            # Create new
            entity = Entity(
                id=entity_id,
                entity_type=entity_type,
                name=name,
                aliases=set(aliases or []),
                first_seen=now,
                last_updated=now
            )
            self.entities[entity_id] = entity
        
        return entity
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name or alias."""
        entity_id = self._normalize_id(name)
        
        # Direct lookup
        if entity_id in self.entities:
            return self.entities[entity_id]
        
        # Search aliases
        for entity in self.entities.values():
            if entity_id in {self._normalize_id(a) for a in entity.aliases}:
                return entity
        
        return None
    
    def _normalize_id(self, name: str) -> str:
        """Normalize a name to an entity ID."""
        return name.lower().strip()
    
    # === Relationship Management ===
    
    def add_relationship(
        self, 
        source: str, 
        rel_type: str, 
        target: str,
        context: str = "",
        source_event_id: str = ""
    ) -> Relationship:
        """Add a relationship between entities."""
        rel = Relationship(
            source_id=self._normalize_id(source),
            rel_type=rel_type,
            target_id=self._normalize_id(target),
            context=context,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_event_id=source_event_id
        )
        self.relationships.append(rel)
        return rel
    
    def get_relationships(
        self, 
        source: str = None, 
        rel_type: str = None, 
        target: str = None
    ) -> List[Relationship]:
        """Query relationships with optional filters."""
        results = self.relationships
        
        if source:
            source_id = self._normalize_id(source)
            results = [r for r in results if r.source_id == source_id]
        
        if rel_type:
            results = [r for r in results if r.rel_type == rel_type]
        
        if target:
            target_id = self._normalize_id(target)
            results = [r for r in results if r.target_id == target_id]
        
        return results
    
    # === Fact Management ===
    
    def add_fact(
        self,
        category: str,
        subject: str,
        content: str,
        linked_entities: List[str] = None,
        question_forms: List[str] = None,
        source_event_id: str = ""
    ) -> Fact:
        """Add a fact to the graph."""
        # Generate ID from content hash
        fact_id = hashlib.md5(f"{category}:{subject}:{content}".encode()).hexdigest()[:12]
        
        # Check for duplicate
        if fact_id in self.facts:
            return self.facts[fact_id]
        
        fact = Fact(
            id=fact_id,
            category=category,
            subject=subject,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_event_id=source_event_id,
            linked_entities=[self._normalize_id(e) for e in (linked_entities or [])],
            question_forms=question_forms or []
        )
        
        self.facts[fact_id] = fact
        return fact
    
    def get_facts_for_entity(self, entity_name: str) -> List[Fact]:
        """Get all facts linked to an entity."""
        entity_id = self._normalize_id(entity_name)
        return [f for f in self.facts.values() if entity_id in f.linked_entities]
    
    def get_facts_by_category(self, category: str) -> List[Fact]:
        """Get facts by category."""
        return [f for f in self.facts.values() if f.category == category]
    
    # === Graph Queries ===
    
    def query_preferences(self, entity_name: str) -> List[Fact]:
        """Get all preferences for an entity."""
        entity_id = self._normalize_id(entity_name)
        
        # Get facts linked to entity with category=preference
        direct_facts = [
            f for f in self.facts.values()
            if entity_id in f.linked_entities and f.category == "preference"
        ]
        
        # Also check relationships with rel_type=prefers
        pref_rels = self.get_relationships(source=entity_name, rel_type="prefers")
        rel_facts = []
        for rel in pref_rels:
            if rel.target_id in self.facts:
                rel_facts.append(self.facts[rel.target_id])
        
        return direct_facts + rel_facts
    
    def query_by_question(self, question: str) -> List[Fact]:
        """
        Find facts that answer a question.
        
        This is the key to Phase 4 - smart retrieval.
        For now, simple keyword matching on question_forms.
        """
        question_lower = question.lower()
        
        # Query expansion: replace pronouns with known entities
        # "I" / "my" → "finn" (when Atlas is asking about Finn)
        # "you" → "atlas" (when Finn is asking about Atlas)
        question_lower = question_lower.replace(" i ", " finn ")
        question_lower = question_lower.replace(" my ", " finn ")
        question_lower = question_lower.replace("do i ", "does finn ")
        question_lower = question_lower.replace("am i ", "is finn ")
        
        question_words = set(question_lower.split())
        
        results = []
        for fact in self.facts.values():
            score = 0
            
            # Check question forms (high weight - 10x)
            for qf in fact.question_forms:
                qf_words = set(qf.lower().split())
                overlap = len(question_words & qf_words)
                if overlap >= 2:
                    score = max(score, overlap * 10)  # 10x weight for question matches
            
            # Check content (lower weight - 1x)
            content_words = set(fact.content.lower().split())
            overlap = len(question_words & content_words)
            if overlap >= 2:
                score = max(score, overlap)  # 1x weight for content matches
            
            if score > 0:
                results.append((score, fact))
        
        # Dedupe and sort
        seen = set()
        unique_results = []
        for score, fact in sorted(results, key=lambda x: x[0], reverse=True):
            if fact.id not in seen:
                seen.add(fact.id)
                unique_results.append(fact)
        
        return unique_results[:10]
    
    # === Stats ===
    
    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        entity_types = {}
        for e in self.entities.values():
            entity_types[e.entity_type] = entity_types.get(e.entity_type, 0) + 1
        
        rel_types = {}
        for r in self.relationships:
            rel_types[r.rel_type] = rel_types.get(r.rel_type, 0) + 1
        
        fact_categories = {}
        for f in self.facts.values():
            fact_categories[f.category] = fact_categories.get(f.category, 0) + 1
        
        return {
            "entities": len(self.entities),
            "entity_types": entity_types,
            "relationships": len(self.relationships),
            "rel_types": rel_types,
            "facts": len(self.facts),
            "fact_categories": fact_categories,
            "facts_with_questions": sum(1 for f in self.facts.values() if f.question_forms)
        }


# === Extraction Enhancement ===

class GraphExtractor:
    """
    Enhanced extraction that builds the knowledge graph.
    
    Key improvements over Phase 2 extractor:
    1. Better entity recognition (not sentence fragments)
    2. Relationship extraction
    3. Question form generation for facts
    4. Entity linking for all facts
    """
    
    # Known entities (bootstrap)
    KNOWN_PEOPLE = {"finn", "atlas", "anthropic"}
    KNOWN_PROJECTS = {"msc", "six nations", "polymarket", "memory system", "clawdbot", "socialflow"}
    KNOWN_CONCEPTS = {"work schedule", "learning style", "communication"}
    
    # Question patterns for different fact types
    QUESTION_GENERATORS = {
        "preference": [
            "what does {subject} prefer",
            "how does {subject} like",
            "when does {subject}",
            "what are {subject}'s preferences",
        ],
        "decision": [
            "what did {subject} decide",
            "why did {subject}",
            "what was decided about",
        ],
        "learning": [
            "what did {subject} learn",
            "what was discovered about",
        ],
        "technical": [
            "how does {subject} work",
            "what is {subject}",
        ]
    }
    
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
    
    def extract_from_text(
        self, 
        text: str, 
        context: str = "",
        source_event_id: str = ""
    ) -> Tuple[List[Entity], List[Relationship], List[Fact]]:
        """Extract entities, relationships, and facts from text."""
        entities = []
        relationships = []
        facts = []
        
        # 1. Extract entities
        entities = self._extract_entities(text)
        
        # 2. Extract facts with entity linking
        facts = self._extract_facts(text, entities, source_event_id)
        
        # 3. Extract relationships
        relationships = self._extract_relationships(text, entities, source_event_id)
        
        return entities, relationships, facts
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text."""
        entities = []
        text_lower = text.lower()
        
        # Check known people
        for person in self.KNOWN_PEOPLE:
            if person in text_lower:
                entity = self.graph.add_entity("person", person.title())
                entities.append(entity)
        
        # Check known projects
        for project in self.KNOWN_PROJECTS:
            if project in text_lower:
                entity = self.graph.add_entity("project", project.title())
                entities.append(entity)
        
        # Check known concepts
        for concept in self.KNOWN_CONCEPTS:
            if concept in text_lower:
                entity = self.graph.add_entity("concept", concept.title())
                entities.append(entity)
        
        return entities
    
    def _extract_facts(
        self, 
        text: str, 
        entities: List[Entity],
        source_event_id: str
    ) -> List[Fact]:
        """Extract facts and link to entities."""
        facts = []
        text_lower = text.lower()
        entity_ids = [e.id for e in entities]
        
        # Preference patterns
        pref_patterns = [
            (r'prefers?\s+(.+?)(?:\s+(?:compared|over|instead|rather))', "preference"),
            (r'(?:likes?|loves?|enjoys?)\s+(.+?)(?:\.|$)', "preference"),
            (r'(?:hates?|dislikes?|avoids?)\s+(.+?)(?:\.|$)', "preference"),
        ]
        
        for pattern, category in pref_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Determine subject (who has this preference)
                subject = "finn" if "finn" in entity_ids else "atlas"
                
                fact = self.graph.add_fact(
                    category=category,
                    subject=subject,
                    content=text,  # Store full text for context
                    linked_entities=entity_ids,
                    question_forms=self._generate_questions(category, subject, text),
                    source_event_id=source_event_id
                )
                facts.append(fact)
        
        return facts
    
    def _extract_relationships(
        self, 
        text: str, 
        entities: List[Entity],
        source_event_id: str
    ) -> List[Relationship]:
        """Extract relationships between entities."""
        relationships = []
        
        # "X prefers Y" → X --prefers--> (fact about Y)
        # "X built Y" → X --created--> Y
        # "X knows Y" → X --knows--> Y
        
        # For now, simple pattern matching
        # TODO: Use LLM for complex relationship extraction
        
        return relationships
    
    def _generate_questions(self, category: str, subject: str, content: str) -> List[str]:
        """Generate question forms that this fact answers."""
        questions = []
        
        templates = self.QUESTION_GENERATORS.get(category, [])
        for template in templates:
            try:
                q = template.format(subject=subject)
                questions.append(q)
            except KeyError:
                pass
        
        # Add content-specific questions
        content_lower = content.lower()
        
        # Work/schedule related
        if any(w in content_lower for w in ["work", "morning", "night", "schedule", "early", "late"]):
            questions.extend([
                f"when does {subject} work",
                f"when does {subject} prefer to work",
                f"what time does {subject} work",
                f"{subject} work schedule",
                f"{subject} work hours",
                f"is {subject} a night owl",
                f"is {subject} an early bird",
            ])
        
        # Learning related
        if any(w in content_lower for w in ["learn", "study", "visual", "practice"]):
            questions.extend([
                f"how does {subject} learn",
                f"what is {subject}'s learning style",
            ])
        
        return questions


# === CLI ===

def main():
    """CLI for knowledge graph operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Knowledge Graph")
    parser.add_argument("command", choices=[
        "stats", "entities", "rels", "facts", 
        "add-entity", "add-rel", "add-fact",
        "query", "prefs"
    ])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--type", "-t", help="Entity/relationship type")
    parser.add_argument("--source", "-s", help="Source entity")
    parser.add_argument("--target", help="Target entity")
    
    args = parser.parse_args()
    
    graph = KnowledgeGraph()
    
    if args.command == "stats":
        stats = graph.stats()
        print("📊 Knowledge Graph Stats\n")
        print(f"Entities: {stats['entities']}")
        for t, c in stats['entity_types'].items():
            print(f"  {t}: {c}")
        print(f"\nRelationships: {stats['relationships']}")
        for t, c in stats['rel_types'].items():
            print(f"  {t}: {c}")
        print(f"\nFacts: {stats['facts']}")
        for t, c in stats['fact_categories'].items():
            print(f"  {t}: {c}")
        print(f"\nFacts with question forms: {stats['facts_with_questions']}")
    
    elif args.command == "entities":
        for entity in graph.entities.values():
            print(f"[{entity.entity_type}] {entity.name}")
            if entity.aliases:
                print(f"  aliases: {', '.join(entity.aliases)}")
    
    elif args.command == "rels":
        rels = graph.get_relationships(source=args.source, rel_type=args.type, target=args.target)
        for r in rels:
            print(f"{r.source_id} --{r.rel_type}--> {r.target_id}")
            if r.context:
                print(f"  context: {r.context}")
    
    elif args.command == "facts":
        for fact in graph.facts.values():
            print(f"[{fact.category}] {fact.subject}")
            print(f"  {fact.content[:80]}...")
            if fact.question_forms:
                print(f"  questions: {fact.question_forms[:2]}...")
            print()
    
    elif args.command == "add-entity":
        if len(args.args) < 2:
            print("Usage: add-entity <type> <name>")
            return 1
        entity = graph.add_entity(args.args[0], args.args[1])
        graph.save()
        print(f"Added: [{entity.entity_type}] {entity.name}")
    
    elif args.command == "query":
        if not args.args:
            print("Usage: query <question>")
            return 1
        question = " ".join(args.args)
        results = graph.query_by_question(question)
        print(f"Found {len(results)} facts:\n")
        for fact in results:
            print(f"[{fact.category}] {fact.subject}")
            print(f"  {fact.content[:100]}...")
            print()
    
    elif args.command == "prefs":
        if not args.args:
            print("Usage: prefs <entity>")
            return 1
        entity = args.args[0]
        prefs = graph.query_preferences(entity)
        print(f"Preferences for {entity}:\n")
        for p in prefs:
            print(f"  • {p.content[:80]}...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
