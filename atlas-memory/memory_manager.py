#!/usr/bin/env python3
"""
Atlas Memory Manager
Hybrid markdown + SQLite memory system with semantic search.

Features:
1. Semantic Memory Search (embeddings-based)
2. Rolling Summaries (context compression)
3. Hybrid Search (vector + keyword)
4. Soul Tools (structured identity management)
5. Automatic Fact Extraction
"""

import sqlite3
import json
import os
import struct
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import openai

# Configuration
DB_PATH = Path(__file__).parent / "atlas_memory.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
MEMORY_MD = Path(__file__).parent.parent / "MEMORY.md"
SOUL_MD = Path(__file__).parent.parent / "SOUL.md"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
CHARS_PER_TOKEN = 4

# Vector search weights
VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3
MIN_SCORE_THRESHOLD = 0.35


def get_openai_client():
    """Get OpenAI client from environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return openai.OpenAI(api_key=api_key)


def estimate_tokens(text: str) -> int:
    """Estimate token count from text."""
    return len(text) // CHARS_PER_TOKEN


def serialize_embedding(embedding: List[float]) -> bytes:
    """Serialize embedding to bytes for SQLite storage."""
    return struct.pack(f'{len(embedding)}f', *embedding)


def deserialize_embedding(data: bytes) -> List[float]:
    """Deserialize embedding from bytes."""
    count = len(data) // 4
    return list(struct.unpack(f'{count}f', data))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class AtlasMemory:
    """Atlas Memory Manager with hybrid markdown + SQLite storage."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._openai = None
    
    def _init_schema(self):
        """Initialize database schema."""
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        self.conn.executescript(schema)
        self.conn.commit()
    
    @property
    def openai(self):
        """Lazy-load OpenAI client."""
        if self._openai is None:
            self._openai = get_openai_client()
        return self._openai
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        response = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIMENSIONS
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        response = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
            dimensions=EMBEDDING_DIMENSIONS
        )
        return [d.embedding for d in response.data]
    
    # ==================== FACT METHODS ====================
    
    def save_fact(self, category: str, subject: str, content: str, source: str = "manual") -> int:
        """Save or update a fact."""
        cursor = self.conn.cursor()
        
        # Check if fact exists
        cursor.execute(
            "SELECT id FROM facts WHERE category = ? AND subject = ?",
            (category, subject)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                """UPDATE facts SET content = ?, source = ?, 
                   updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') 
                   WHERE id = ?""",
                (content, source, existing['id'])
            )
            fact_id = existing['id']
        else:
            cursor.execute(
                "INSERT INTO facts (category, subject, content, source) VALUES (?, ?, ?, ?)",
                (category, subject, content, source)
            )
            fact_id = cursor.lastrowid
        
        self.conn.commit()
        
        # Embed the fact asynchronously
        self._embed_fact(fact_id, category, subject, content)
        
        return fact_id
    
    def _embed_fact(self, fact_id: int, category: str, subject: str, content: str):
        """Generate and store embedding for a fact."""
        try:
            text = f"{category}: {subject} - {content}"
            embedding = self.embed(text)
            embedding_bytes = serialize_embedding(embedding)
            
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO fact_embeddings (fact_id, embedding) 
                   VALUES (?, ?)""",
                (fact_id, embedding_bytes)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[Memory] Failed to embed fact {fact_id}: {e}")
    
    def get_all_facts(self) -> List[Dict]:
        """Get all facts."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, category, subject, content, source, created_at, updated_at FROM facts ORDER BY category, subject"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def search_facts_hybrid(self, query: str, limit: int = 10) -> List[Dict]:
        """Hybrid semantic + keyword search for facts."""
        results = {}
        
        # Handle empty query
        if not query or not query.strip():
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, category, subject, content FROM facts ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )
            return [{'id': r['id'], 'category': r['category'], 'subject': r['subject'], 
                     'content': r['content'], 'combined_score': 0.0} for r in cursor.fetchall()]
        
        # Keyword search using FTS5
        cursor = self.conn.cursor()
        
        # Escape special FTS5 characters and wrap in quotes for phrase search
        safe_query = query.replace('"', '""')
        try:
            cursor.execute(
                """SELECT f.id, f.category, f.subject, f.content, 
                          bm25(facts_fts) as keyword_score
                   FROM facts_fts 
                   JOIN facts f ON facts_fts.rowid = f.id
                   WHERE facts_fts MATCH ?
                   LIMIT ?""",
                (f'"{safe_query}"', limit * 2)
            )
        except Exception:
            # If FTS fails, fall back to LIKE search
            cursor.execute(
                """SELECT f.id, f.category, f.subject, f.content, 0.5 as keyword_score
                   FROM facts f
                   WHERE f.content LIKE ? OR f.subject LIKE ? OR f.category LIKE ?
                   LIMIT ?""",
                (f'%{query}%', f'%{query}%', f'%{query}%', limit * 2)
            )
        for row in cursor.fetchall():
            results[row['id']] = {
                'id': row['id'],
                'category': row['category'],
                'subject': row['subject'],
                'content': row['content'],
                'keyword_score': abs(row['keyword_score']),  # BM25 returns negative
                'vector_score': 0.0
            }
        
        # Vector search
        try:
            query_embedding = self.embed(query)
            
            cursor.execute(
                """SELECT fe.fact_id, fe.embedding, f.category, f.subject, f.content
                   FROM fact_embeddings fe
                   JOIN facts f ON fe.fact_id = f.id"""
            )
            
            for row in cursor.fetchall():
                fact_embedding = deserialize_embedding(row['embedding'])
                similarity = cosine_similarity(query_embedding, fact_embedding)
                
                if row['fact_id'] in results:
                    results[row['fact_id']]['vector_score'] = similarity
                elif similarity > MIN_SCORE_THRESHOLD:
                    results[row['fact_id']] = {
                        'id': row['fact_id'],
                        'category': row['category'],
                        'subject': row['subject'],
                        'content': row['content'],
                        'keyword_score': 0.0,
                        'vector_score': similarity
                    }
        except Exception as e:
            print(f"[Memory] Vector search failed: {e}")
        
        # Combine scores and sort
        for r in results.values():
            r['combined_score'] = (
                VECTOR_WEIGHT * r['vector_score'] + 
                KEYWORD_WEIGHT * r['keyword_score']
            )
        
        sorted_results = sorted(
            results.values(), 
            key=lambda x: x['combined_score'], 
            reverse=True
        )
        
        return sorted_results[:limit]
    
    # ==================== SOUL METHODS ====================
    
    def soul_set(self, aspect: str, content: str) -> int:
        """Set or update a soul aspect."""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO soul (aspect, content) VALUES (?, ?)
               ON CONFLICT(aspect) DO UPDATE SET 
               content = excluded.content,
               updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')""",
            (aspect, content)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def soul_get(self, aspect: str) -> Optional[Dict]:
        """Get a soul aspect."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, aspect, content, created_at, updated_at FROM soul WHERE aspect = ?",
            (aspect,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def soul_list(self) -> List[Dict]:
        """List all soul aspects."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, aspect, content, created_at, updated_at FROM soul ORDER BY aspect"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def soul_delete(self, aspect: str) -> bool:
        """Delete a soul aspect."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM soul WHERE aspect = ?", (aspect,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_soul_context(self) -> str:
        """Get formatted soul context for agent."""
        aspects = self.soul_list()
        if not aspects:
            return ""
        
        lines = ["## Soul Aspects"]
        for a in aspects:
            lines.append(f"- **{a['aspect']}**: {a['content']}")
        return "\n".join(lines)
    
    # ==================== MESSAGE METHODS ====================
    
    def save_message(self, role: str, content: str, session_id: str = "main") -> int:
        """Save a conversation message."""
        token_count = estimate_tokens(content)
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO messages (role, content, session_id, token_count) 
               VALUES (?, ?, ?, ?)""",
            (role, content, session_id, token_count)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def embed_message(self, message_id: int):
        """Generate and store embedding for a message."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        if not row:
            return
        
        try:
            embedding = self.embed(row['content'])
            embedding_bytes = serialize_embedding(embedding)
            cursor.execute(
                """INSERT OR REPLACE INTO message_embeddings (message_id, embedding)
                   VALUES (?, ?)""",
                (message_id, embedding_bytes)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[Memory] Failed to embed message {message_id}: {e}")
    
    def search_messages(self, query: str, session_id: str = None, limit: int = 10) -> List[Dict]:
        """Semantic search over past messages."""
        try:
            query_embedding = self.embed(query)
        except Exception as e:
            print(f"[Memory] Failed to embed query: {e}")
            return []
        
        cursor = self.conn.cursor()
        
        if session_id:
            cursor.execute(
                """SELECT me.message_id, me.embedding, m.role, m.content, m.timestamp
                   FROM message_embeddings me
                   JOIN messages m ON me.message_id = m.id
                   WHERE m.session_id = ?
                   ORDER BY m.id DESC LIMIT 500""",
                (session_id,)
            )
        else:
            cursor.execute(
                """SELECT me.message_id, me.embedding, m.role, m.content, m.timestamp
                   FROM message_embeddings me
                   JOIN messages m ON me.message_id = m.id
                   ORDER BY m.id DESC LIMIT 500"""
            )
        
        results = []
        for row in cursor.fetchall():
            msg_embedding = deserialize_embedding(row['embedding'])
            similarity = cosine_similarity(query_embedding, msg_embedding)
            if similarity > MIN_SCORE_THRESHOLD:
                results.append({
                    'id': row['message_id'],
                    'role': row['role'],
                    'content': row['content'],
                    'timestamp': row['timestamp'],
                    'similarity': similarity
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    # ==================== SUMMARY METHODS ====================
    
    def get_rolling_summary(self, session_id: str = "main") -> Optional[str]:
        """Get the most recent rolling summary for a session."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT content FROM summaries 
               WHERE session_id = ? 
               ORDER BY end_message_id DESC LIMIT 1""",
            (session_id,)
        )
        row = cursor.fetchone()
        return row['content'] if row else None
    
    def save_summary(self, session_id: str, start_id: int, end_id: int, content: str) -> int:
        """Save a rolling summary."""
        token_count = estimate_tokens(content)
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO summaries (session_id, start_message_id, end_message_id, content, token_count)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, start_id, end_id, content, token_count)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    # ==================== MIGRATION METHODS ====================
    
    def migrate_memory_md(self):
        """Migrate MEMORY.md content to facts table."""
        if not MEMORY_MD.exists():
            print("[Memory] MEMORY.md not found, skipping migration")
            return
        
        content = MEMORY_MD.read_text()
        
        # Parse markdown sections as facts
        current_category = "general"
        current_subject = ""
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('## '):
                current_category = line[3:].strip()
            elif line.startswith('### '):
                current_subject = line[4:].strip()
            elif line.startswith('- **') and '**:' in line:
                # Format: - **Subject**: Content
                parts = line[4:].split('**:', 1)
                if len(parts) == 2:
                    subject = parts[0].strip()
                    fact_content = parts[1].strip()
                    self.save_fact(current_category, subject, fact_content, "migration")
            elif line.startswith('- ') and len(line) > 2:
                # Format: - Content
                fact_content = line[2:].strip()
                if fact_content:
                    self.save_fact(current_category, current_subject, fact_content, "migration")
        
        print(f"[Memory] Migrated MEMORY.md to facts table")
    
    def migrate_soul_md(self):
        """Migrate SOUL.md to soul aspects."""
        if not SOUL_MD.exists():
            print("[Memory] SOUL.md not found, skipping migration")
            return
        
        content = SOUL_MD.read_text()
        
        # Store entire SOUL.md as core identity
        self.soul_set("core_identity", content[:2000])  # First 2000 chars
        
        # Extract specific sections
        current_section = ""
        section_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section and section_content:
                    self.soul_set(
                        current_section.lower().replace(' ', '_'),
                        '\n'.join(section_content)
                    )
                current_section = line[3:].strip()
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            self.soul_set(
                current_section.lower().replace(' ', '_'),
                '\n'.join(section_content)
            )
        
        print(f"[Memory] Migrated SOUL.md to soul aspects")
    
    def sync_daily_logs(self):
        """Sync daily log markdown files to database."""
        if not MEMORY_DIR.exists():
            print("[Memory] Memory directory not found")
            return
        
        cursor = self.conn.cursor()
        
        for md_file in MEMORY_DIR.glob("*.md"):
            if md_file.name.startswith("20"):  # Date-formatted files
                date = md_file.stem
                content = md_file.read_text()
                
                cursor.execute(
                    """INSERT INTO daily_logs (date, file_path, content) VALUES (?, ?, ?)
                       ON CONFLICT(date) DO UPDATE SET 
                       content = excluded.content,
                       updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')""",
                    (date, str(md_file), content)
                )
        
        self.conn.commit()
        print(f"[Memory] Synced daily logs to database")
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# ==================== CLI INTERFACE ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Memory Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize database")
    
    # Migrate command
    subparsers.add_parser("migrate", help="Migrate from markdown files")
    
    # Fact commands
    fact_parser = subparsers.add_parser("fact", help="Fact operations")
    fact_sub = fact_parser.add_subparsers(dest="fact_cmd")
    
    fact_add = fact_sub.add_parser("add", help="Add a fact")
    fact_add.add_argument("category")
    fact_add.add_argument("subject")
    fact_add.add_argument("content")
    
    fact_list = fact_sub.add_parser("list", help="List all facts")
    
    fact_search = fact_sub.add_parser("search", help="Search facts")
    fact_search.add_argument("query")
    
    # Soul commands
    soul_parser = subparsers.add_parser("soul", help="Soul operations")
    soul_sub = soul_parser.add_subparsers(dest="soul_cmd")
    
    soul_set = soul_sub.add_parser("set", help="Set a soul aspect")
    soul_set.add_argument("aspect")
    soul_set.add_argument("content")
    
    soul_get = soul_sub.add_parser("get", help="Get a soul aspect")
    soul_get.add_argument("aspect")
    
    soul_list = soul_sub.add_parser("list", help="List all soul aspects")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search messages")
    search_parser.add_argument("query")
    
    args = parser.parse_args()
    
    memory = AtlasMemory()
    
    if args.command == "init":
        print("Database initialized")
    
    elif args.command == "migrate":
        memory.migrate_memory_md()
        memory.migrate_soul_md()
        memory.sync_daily_logs()
        print("Migration complete")
    
    elif args.command == "fact":
        if args.fact_cmd == "add":
            fact_id = memory.save_fact(args.category, args.subject, args.content)
            print(f"Fact saved with ID: {fact_id}")
        elif args.fact_cmd == "list":
            facts = memory.get_all_facts()
            for f in facts:
                print(f"[{f['category']}] {f['subject']}: {f['content']}")
        elif args.fact_cmd == "search":
            results = memory.search_facts_hybrid(args.query)
            for r in results:
                print(f"[{r['combined_score']:.2f}] [{r['category']}] {r['subject']}: {r['content']}")
    
    elif args.command == "soul":
        if args.soul_cmd == "set":
            memory.soul_set(args.aspect, args.content)
            print(f"Soul aspect '{args.aspect}' set")
        elif args.soul_cmd == "get":
            aspect = memory.soul_get(args.aspect)
            if aspect:
                print(f"{aspect['aspect']}: {aspect['content']}")
            else:
                print("Aspect not found")
        elif args.soul_cmd == "list":
            aspects = memory.soul_list()
            for a in aspects:
                print(f"- {a['aspect']}: {a['content'][:100]}...")
    
    elif args.command == "search":
        results = memory.search_messages(args.query)
        for r in results:
            print(f"[{r['similarity']:.2f}] [{r['role']}] {r['content'][:100]}...")
    
    memory.close()


if __name__ == "__main__":
    main()
