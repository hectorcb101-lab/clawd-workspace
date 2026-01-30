#!/usr/bin/env python3
"""
Atlas Memory Integration Layer

Provides high-level functions for integrating Atlas Memory
into Clawdbot's active workflow.
"""

import json
import sys
import os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from memory_manager import AtlasMemory

DB_PATH = Path(__file__).parent / "atlas_memory.db"


def get_memory():
    """Get memory manager instance."""
    return AtlasMemory(str(DB_PATH))


# ==================== FACT OPERATIONS ====================

def fact_add(category: str, subject: str, content: str, source: str = "conversation"):
    """Add a fact to memory."""
    m = get_memory()
    try:
        fact_id = m.save_fact(category, subject, content, source)
        return {"success": True, "fact_id": fact_id}
    finally:
        m.close()


def fact_search(query: str, limit: int = 5):
    """Search facts using hybrid search."""
    m = get_memory()
    try:
        results = m.search_facts_hybrid(query, limit)
        return {"success": True, "results": results}
    finally:
        m.close()


def fact_list(category: str = None):
    """List all facts, optionally filtered by category."""
    m = get_memory()
    try:
        facts = m.get_all_facts()
        if category:
            facts = [f for f in facts if f['category'].lower() == category.lower()]
        return {"success": True, "facts": facts}
    finally:
        m.close()


def fact_delete(fact_id: int):
    """Delete a fact by ID."""
    m = get_memory()
    try:
        deleted = m.delete_fact(fact_id)
        return {"success": deleted}
    finally:
        m.close()


# ==================== SOUL OPERATIONS ====================

def soul_set(aspect: str, content: str):
    """Set or update a soul aspect."""
    m = get_memory()
    try:
        m.soul_set(aspect, content)
        return {"success": True, "aspect": aspect}
    finally:
        m.close()


def soul_get(aspect: str):
    """Get a soul aspect."""
    m = get_memory()
    try:
        result = m.soul_get(aspect)
        if result:
            return {"success": True, "aspect": result}
        return {"success": False, "error": "Aspect not found"}
    finally:
        m.close()


def soul_list():
    """List all soul aspects."""
    m = get_memory()
    try:
        aspects = m.soul_list()
        return {"success": True, "aspects": aspects}
    finally:
        m.close()


def soul_delete(aspect: str):
    """Delete a soul aspect."""
    m = get_memory()
    try:
        deleted = m.soul_delete(aspect)
        return {"success": deleted}
    finally:
        m.close()


# ==================== MESSAGE OPERATIONS ====================

def message_save(role: str, content: str, session_id: str = "main", embed: bool = True):
    """Save a message and optionally embed it."""
    m = get_memory()
    try:
        msg_id = m.save_message(role, content, session_id)
        if embed:
            m.embed_message(msg_id)
        return {"success": True, "message_id": msg_id}
    finally:
        m.close()


def message_search(query: str, session_id: str = None, limit: int = 5):
    """Search past messages semantically."""
    m = get_memory()
    try:
        results = m.search_messages(query, session_id, limit)
        return {"success": True, "results": results}
    finally:
        m.close()


# ==================== CONTEXT GENERATION ====================

def get_relevant_context(query: str, include_soul: bool = True, include_facts: bool = True,
                         include_messages: bool = True, fact_limit: int = 5, msg_limit: int = 3):
    """
    Get relevant context for a query.
    Returns combined context from facts, soul, and past messages.
    """
    m = get_memory()
    try:
        context_parts = []
        
        # Soul context
        if include_soul:
            soul_ctx = m.get_soul_context()
            if soul_ctx:
                context_parts.append(soul_ctx)
        
        # Relevant facts
        if include_facts:
            facts = m.search_facts_hybrid(query, fact_limit)
            if facts:
                lines = ["## Relevant Facts"]
                for f in facts:
                    if f['subject']:
                        lines.append(f"- **{f['category']}/{f['subject']}**: {f['content']}")
                    else:
                        lines.append(f"- **{f['category']}**: {f['content']}")
                context_parts.append("\n".join(lines))
        
        # Relevant past messages
        if include_messages:
            messages = m.search_messages(query, limit=msg_limit)
            if messages:
                lines = ["## Relevant Past Conversations"]
                for msg in messages:
                    role = "User" if msg['role'] == 'user' else "Atlas"
                    lines.append(f"- [{role}] {msg['content'][:200]}...")
                context_parts.append("\n".join(lines))
        
        return {
            "success": True,
            "context": "\n\n".join(context_parts) if context_parts else ""
        }
    finally:
        m.close()


# ==================== AUTO FACT EXTRACTION ====================

def extract_facts_from_text(text: str, context: str = ""):
    """
    Placeholder for auto fact extraction.
    In production, this would use an LLM to extract facts.
    For now, returns empty - extraction happens at the agent level.
    """
    return {"success": True, "facts": [], "note": "Use agent-level extraction"}


# ==================== CLI ====================

def main():
    """CLI interface for integration testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Memory Integration")
    parser.add_argument("command", choices=[
        "fact-add", "fact-search", "fact-list", "fact-delete",
        "soul-set", "soul-get", "soul-list", "soul-delete",
        "msg-save", "msg-search", "context"
    ])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = None
    
    if args.command == "fact-add" and len(args.args) >= 3:
        result = fact_add(args.args[0], args.args[1], args.args[2])
    elif args.command == "fact-search" and len(args.args) >= 1:
        result = fact_search(args.args[0])
    elif args.command == "fact-list":
        result = fact_list(args.args[0] if args.args else None)
    elif args.command == "fact-delete" and len(args.args) >= 1:
        result = fact_delete(int(args.args[0]))
    elif args.command == "soul-set" and len(args.args) >= 2:
        result = soul_set(args.args[0], args.args[1])
    elif args.command == "soul-get" and len(args.args) >= 1:
        result = soul_get(args.args[0])
    elif args.command == "soul-list":
        result = soul_list()
    elif args.command == "soul-delete" and len(args.args) >= 1:
        result = soul_delete(args.args[0])
    elif args.command == "msg-save" and len(args.args) >= 2:
        result = message_save(args.args[0], args.args[1])
    elif args.command == "msg-search" and len(args.args) >= 1:
        result = message_search(args.args[0])
    elif args.command == "context" and len(args.args) >= 1:
        result = get_relevant_context(args.args[0])
    else:
        print("Invalid command or missing arguments")
        parser.print_help()
        return
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result)


if __name__ == "__main__":
    main()
