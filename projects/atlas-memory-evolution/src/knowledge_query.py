#!/usr/bin/env python3
"""
Atlas Knowledge Query
=====================
Query the extracted knowledge - facts, entities, relationships.

This is how I actually USE my memory.
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent))

from extractor import KnowledgeStore, ExtractedFact, ExtractedEntity


class KnowledgeQuery:
    """
    Query interface for extracted knowledge.
    
    Supports:
    - Keyword search across facts
    - Entity lookup
    - Category filtering
    - Recency filtering
    """
    
    def __init__(self):
        self.store = KnowledgeStore()
        self._load_facts()
    
    def _load_facts(self):
        """Load all facts into memory for searching."""
        self.facts: List[Dict] = []
        facts_file = self.store.base_dir / "facts.jsonl"
        
        if facts_file.exists():
            with open(facts_file) as f:
                for line in f:
                    try:
                        self.facts.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
    
    def search_facts(
        self, 
        query: str, 
        category: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search facts by keyword.
        
        Args:
            query: Search terms
            category: Filter by category (learning, decision, preference)
            limit: Max results
        """
        query_terms = query.lower().split()
        results = []
        
        for fact in self.facts:
            # Category filter
            if category and fact.get("category") != category:
                continue
            
            # Score based on term matches
            text = f"{fact.get('subject', '')} {fact.get('content', '')}".lower()
            score = sum(1 for term in query_terms if term in text)
            
            if score > 0:
                results.append((score, fact))
        
        # Sort by score, take top N
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]
    
    def get_entity(self, name: str) -> Optional[ExtractedEntity]:
        """Look up an entity by name."""
        key = name.lower()
        return self.store.entities.get(key)
    
    def list_entities(self, entity_type: str = None) -> List[ExtractedEntity]:
        """List all entities, optionally filtered by type."""
        entities = list(self.store.entities.values())
        
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
        
        return entities
    
    def get_facts_about(self, subject: str) -> List[Dict]:
        """Get all facts related to a subject."""
        subject_lower = subject.lower()
        return [
            f for f in self.facts
            if subject_lower in f.get('subject', '').lower()
            or subject_lower in f.get('content', '').lower()
        ]
    
    def get_recent_learnings(self, limit: int = 5) -> List[Dict]:
        """Get most recent learnings."""
        learnings = [f for f in self.facts if f.get('category') == 'learning']
        # Sort by timestamp descending
        learnings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return learnings[:limit]
    
    def get_decisions(self, limit: int = 10) -> List[Dict]:
        """Get all decisions."""
        decisions = [f for f in self.facts if f.get('category') == 'decision']
        decisions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return decisions[:limit]
    
    def get_preferences(self) -> List[Dict]:
        """Get all preferences."""
        return [f for f in self.facts if f.get('category') == 'preference']
    
    def summarize(self) -> str:
        """Get a summary of stored knowledge."""
        stats = self.store.get_stats()
        
        categories = {}
        for f in self.facts:
            cat = f.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        entity_types = {}
        for e in self.store.entities.values():
            et = e.entity_type
            entity_types[et] = entity_types.get(et, 0) + 1
        
        lines = [
            "📚 **Knowledge Summary**",
            "",
            f"**Facts:** {stats['facts']}",
        ]
        
        for cat, count in sorted(categories.items()):
            lines.append(f"  - {cat}: {count}")
        
        lines.extend([
            "",
            f"**Entities:** {stats['entities']}",
        ])
        
        for et, count in sorted(entity_types.items()):
            lines.append(f"  - {et}: {count}")
        
        lines.extend([
            "",
            f"**Events processed:** {stats['processed_events']}"
        ])
        
        return "\n".join(lines)


def main():
    """CLI interface for knowledge queries."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Atlas knowledge")
    parser.add_argument("command", choices=["search", "entity", "entities", "about", "learnings", "decisions", "summary"])
    parser.add_argument("query", nargs="?", help="Search query or entity name")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--type", "-t", help="Entity type filter")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    
    args = parser.parse_args()
    
    kq = KnowledgeQuery()
    
    if args.command == "search":
        if not args.query:
            print("Usage: knowledge_query.py search <query>")
            return 1
        
        results = kq.search_facts(args.query, category=args.category, limit=args.limit)
        print(f"Found {len(results)} facts:\n")
        for r in results:
            print(f"[{r['category']}] {r['subject']}")
            print(f"  {r['content'][:100]}...")
            print()
    
    elif args.command == "entity":
        if not args.query:
            print("Usage: knowledge_query.py entity <name>")
            return 1
        
        entity = kq.get_entity(args.query)
        if entity:
            print(f"Entity: {entity.name}")
            print(f"  Type: {entity.entity_type}")
            print(f"  First seen: {entity.first_seen}")
            if entity.aliases:
                print(f"  Aliases: {', '.join(entity.aliases)}")
        else:
            print(f"Entity '{args.query}' not found")
    
    elif args.command == "entities":
        entities = kq.list_entities(entity_type=args.type)
        print(f"Found {len(entities)} entities:\n")
        for e in entities:
            print(f"  [{e.entity_type}] {e.name}")
    
    elif args.command == "about":
        if not args.query:
            print("Usage: knowledge_query.py about <subject>")
            return 1
        
        facts = kq.get_facts_about(args.query)
        print(f"Found {len(facts)} facts about '{args.query}':\n")
        for f in facts[:args.limit]:
            print(f"  - {f['content'][:80]}...")
    
    elif args.command == "learnings":
        learnings = kq.get_recent_learnings(limit=args.limit)
        print(f"Recent learnings ({len(learnings)}):\n")
        for l in learnings:
            print(f"  • {l['subject']}")
    
    elif args.command == "decisions":
        decisions = kq.get_decisions(limit=args.limit)
        print(f"Decisions ({len(decisions)}):\n")
        for d in decisions:
            print(f"  • {d['content'][:80]}...")
    
    elif args.command == "summary":
        print(kq.summarize())
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
