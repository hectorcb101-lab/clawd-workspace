#!/usr/bin/env python3
"""
Atlas Memory System
===================
The unified interface to Atlas's memory.

This is the main entry point for all memory operations.
"""

import sys
from pathlib import Path

# .resolve() follows symlinks to get actual source directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from event_schema import Event, EventType, message_in, message_out, tool_call, learning, decision
from event_log import get_log
from session_logger import get_session_logger, log_in, log_out, log_learn, log_decide
from conversation_ingester import ConversationIngester, ingest_all_daily_logs
from extractor import run_extraction, KnowledgeStore
from knowledge_query import KnowledgeQuery
from knowledge_graph import KnowledgeGraph, GraphExtractor
from semantic_search import SemanticSearch


class AtlasMemory:
    """
    Unified memory interface.
    
    Usage:
        memory = AtlasMemory()
        
        # Log events
        memory.log_message("Hello", direction="in", user="Finn")
        memory.log_learning("Something important")
        
        # Query
        facts = memory.search("topic")
        entities = memory.get_entities()
        
        # Sync
        memory.sync()  # Ingest + extract
    """
    
    def __init__(self):
        self.event_log = get_log()
        self.session_logger = get_session_logger()
        self.ingester = ConversationIngester()
        self.knowledge = KnowledgeQuery()
        self.graph = KnowledgeGraph()
        self.graph_extractor = GraphExtractor(self.graph)
        self.semantic_search = SemanticSearch(self.graph)
    
    # === Logging ===
    
    def log_message(self, text: str, direction: str = "out", user: str = None) -> str:
        """Log a message."""
        if direction == "in":
            return self.session_logger.log_message_in(text, user=user)
        else:
            return self.session_logger.log_message_out(text)
    
    def log_learning(self, summary: str, details: str = None) -> str:
        """Log something learned."""
        return self.session_logger.log_learning(summary, details)
    
    def log_decision(self, what: str, why: str) -> str:
        """Log a decision."""
        return self.session_logger.log_decision(what, why)
    
    def log_tool(self, name: str, params: dict, result=None) -> str:
        """Log a tool call."""
        return self.session_logger.log_tool(name, params, result)
    
    # === Querying ===
    
    def search(self, query: str, limit: int = 10) -> list:
        """Search facts using Phase 4 semantic search."""
        # Use semantic search (falls back to fast mode if embeddings not ready)
        search_results = self.semantic_search.search(query, limit=limit)
        
        # Convert to dict format for compatibility
        results = []
        for r in search_results:
            results.append({
                'category': r.fact.category,
                'subject': r.fact.subject,
                'content': r.fact.content,
                'question_forms': r.fact.question_forms,
                'linked_entities': r.fact.linked_entities,
                'score': r.total_score
            })
        
        # Fall back to keyword search if few results
        if len(results) < 3:
            keyword_results = self.knowledge.search_facts(query, limit=limit)
            seen_content = {r['content'][:50] for r in results}
            for kr in keyword_results:
                if kr.get('content', '')[:50] not in seen_content:
                    results.append(kr)
                    if len(results) >= limit:
                        break
        
        return results
    
    def get_facts_about(self, subject: str) -> list:
        """Get facts about a subject."""
        return self.knowledge.get_facts_about(subject)
    
    def get_entities(self, entity_type: str = None) -> list:
        """Get entities."""
        return self.knowledge.list_entities(entity_type)
    
    def get_learnings(self, limit: int = 10) -> list:
        """Get recent learnings."""
        return self.knowledge.get_recent_learnings(limit)
    
    def get_decisions(self, limit: int = 10) -> list:
        """Get decisions."""
        return self.knowledge.get_decisions(limit)
    
    def summary(self) -> str:
        """Get knowledge summary."""
        return self.knowledge.summarize()
    
    # === Sync ===
    
    def sync(self) -> dict:
        """
        Full sync: ingest daily logs + run extraction.
        
        Call this periodically (heartbeat) to keep memory up to date.
        """
        # Ingest new daily logs
        ingested = ingest_all_daily_logs()
        
        # Run extraction
        extraction_stats = run_extraction()
        
        # Reload knowledge query
        self.knowledge = KnowledgeQuery()
        
        return {
            "ingested_from_logs": ingested,
            "events_processed": extraction_stats["events"],
            "facts_extracted": extraction_stats["facts"],
            "entities_found": extraction_stats["entities"]
        }
    
    # === Stats ===
    
    def stats(self) -> dict:
        """Get memory system stats."""
        event_stats = self.event_log.get_stats()
        knowledge_stats = KnowledgeStore().get_stats()
        
        return {
            "events": {
                "hot": event_stats["hot_events"],
                "files": event_stats["hot_files"] + event_stats["warm_files"] + event_stats["cold_files"],
                "size_kb": event_stats["total_size_bytes"] / 1024
            },
            "knowledge": knowledge_stats
        }


# Global instance
_memory: AtlasMemory = None

def get_memory() -> AtlasMemory:
    """Get global memory instance."""
    global _memory
    if _memory is None:
        _memory = AtlasMemory()
    return _memory


# Quick access functions
def remember(summary: str, details: str = None) -> str:
    """Quick: Log a learning and add to graph with question forms."""
    memory = get_memory()
    
    # Log to event log
    event_id = memory.log_learning(summary, details)
    
    # Also add to knowledge graph with question forms
    from migrate_to_graph import extract_entities_from_text, generate_question_forms
    
    content = summary if not details else f"{summary}. {details}"
    
    # Determine category based on content
    content_lower = content.lower()
    if any(w in content_lower for w in ["prefer", "like", "want", "hate", "avoid"]):
        category = "preference"
    elif any(w in content_lower for w in ["decided", "will", "chose", "going to"]):
        category = "decision"
    else:
        category = "learning"
    
    # Determine subject (who this is about)
    if "finn" in content_lower:
        subject = "finn"
    elif "atlas" in content_lower or "i " in content_lower:
        subject = "atlas"
    else:
        subject = "general"
    
    # Extract entities and generate questions
    linked = extract_entities_from_text(content)
    questions = generate_question_forms(category, subject, content)
    
    # Add to graph
    memory.graph.add_fact(
        category=category,
        subject=subject,
        content=content,
        linked_entities=linked,
        question_forms=questions,
        source_event_id=event_id
    )
    memory.graph.save()
    
    # Also run standard extraction for backward compat
    run_extraction()
    
    return event_id

def recall(query: str, limit: int = 5) -> list:
    """Quick: Search memory."""
    return get_memory().search(query, limit)

def sync() -> dict:
    """Quick: Sync memory."""
    return get_memory().sync()


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Memory System")
    parser.add_argument("command", choices=["sync", "stats", "search", "remember", "summary", "index"])
    parser.add_argument("args", nargs="*", help="Command arguments")
    
    args = parser.parse_args()
    memory = get_memory()
    
    if args.command == "sync":
        print("🔄 Syncing memory...")
        result = memory.sync()
        print(f"✅ Sync complete:")
        print(f"   Ingested from logs: {result['ingested_from_logs']}")
        print(f"   Events processed: {result['events_processed']}")
        print(f"   Facts extracted: {result['facts_extracted']}")
        print(f"   Entities found: {result['entities_found']}")
    
    elif args.command == "stats":
        stats = memory.stats()
        print("📊 Memory Stats")
        print(f"\nEvents:")
        print(f"  Hot: {stats['events']['hot']}")
        print(f"  Files: {stats['events']['files']}")
        print(f"  Size: {stats['events']['size_kb']:.1f} KB")
        print(f"\nKnowledge:")
        for k, v in stats['knowledge'].items():
            print(f"  {k}: {v}")
    
    elif args.command == "search":
        if not args.args:
            print("Usage: atlas_memory.py search <query>")
            return 1
        query = " ".join(args.args)
        results = memory.search(query)
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"[{r['category']}] {r['subject'][:50]}")
            print(f"  {r['content'][:80]}...")
            print()
    
    elif args.command == "remember":
        if not args.args:
            print("Usage: atlas_memory.py remember <something to remember>")
            return 1
        text = " ".join(args.args)
        # Use remember() function which also runs extraction
        event_id = remember(text)
        print(f"✅ Remembered: {event_id}")
    
    elif args.command == "summary":
        print(memory.summary())
    
    elif args.command == "index":
        print("🔄 Indexing facts for semantic search...")
        memory.semantic_search.index_all_facts()
        print("✅ Indexing complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
