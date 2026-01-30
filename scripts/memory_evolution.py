#!/usr/bin/env python3
"""
Memory Evolution System - A-Mem Pattern
Memories that evolve, connect, and form a knowledge graph.

Based on:
- A-Mem: Agentic Memory (arxiv.org/abs/2502.12110)
- Zettelkasten method for interconnected knowledge
"""

import sqlite3
import json
import os
import struct
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import urllib.request

CLAWD_DIR = Path(__file__).parent.parent
DB_PATH = CLAWD_DIR / "atlas-memory" / "atlas_memory.db"

# Link types (inspired by Zettelkasten)
LINK_TYPES = {
    'related': 'Loosely related concepts',
    'extends': 'Builds upon / elaborates',
    'contradicts': 'Conflicts with',
    'supports': 'Provides evidence for',
    'refines': 'More specific version of',
    'causes': 'Leads to / causes',
    'example': 'Is an example of'
}


class MemoryEvolution:
    """
    The A-Mem Pattern - memories that evolve and connect.
    
    Key operations:
    1. Add with auto-linking (find related memories)
    2. Evolve existing memories (update when new info arrives)
    3. Find connections (multi-hop traversal)
    4. Prune obsolete (remove outdated info)
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Memory links table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_fact_id INTEGER NOT NULL,
                target_fact_id INTEGER NOT NULL,
                link_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                bidirectional INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                last_strengthened TEXT,
                FOREIGN KEY (source_fact_id) REFERENCES facts(id),
                FOREIGN KEY (target_fact_id) REFERENCES facts(id),
                UNIQUE(source_fact_id, target_fact_id, link_type)
            )
        """)
        
        # Memory evolution history
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_evolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id INTEGER NOT NULL,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                old_content TEXT,
                new_content TEXT,
                trigger TEXT,
                FOREIGN KEY (fact_id) REFERENCES facts(id)
            )
        """)
        
        # Create index for faster link queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_links_source 
            ON memory_links(source_fact_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_links_target 
            ON memory_links(target_fact_id)
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== EMBEDDING UTILITIES ====================
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API."""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            env_file = Path.home() / '.clawdbot' / '.env'
            if env_file.exists():
                for line in env_file.read_text().split('\n'):
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"\'')
                        break
        
        if not api_key:
            raise ValueError("No OPENAI_API_KEY found")
        
        data = json.dumps({
            "model": "text-embedding-3-small",
            "input": text[:8000]
        }).encode()
        
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result['data'][0]['embedding']
    
    def _embedding_to_blob(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for storage."""
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    def _blob_to_embedding(self, blob: bytes) -> List[float]:
        """Convert stored bytes back to embedding list."""
        n = len(blob) // 4
        return list(struct.unpack(f'{n}f', blob))
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = sum(x*x for x in a) ** 0.5
        norm_b = sum(x*x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    # ==================== ADD WITH LINKS ====================
    
    def add_with_links(
        self,
        category: str,
        subject: str,
        content: str,
        source: str = "memory_evolution",
        auto_link: bool = True,
        link_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Add a new fact and automatically link to related facts.
        
        Returns the new fact ID and created links.
        """
        result = {
            'fact_id': None,
            'links_created': [],
            'related_facts': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Add the fact
        cur.execute("""
            INSERT INTO facts (category, subject, content, source)
            VALUES (?, ?, ?, ?)
        """, (category, subject, content, source))
        
        fact_id = cur.lastrowid
        result['fact_id'] = fact_id
        
        # Generate and store embedding
        try:
            embedding = self._get_embedding(f"{subject}: {content}")
            emb_blob = self._embedding_to_blob(embedding)
            
            cur.execute("""
                INSERT INTO fact_embeddings (fact_id, embedding)
                VALUES (?, ?)
            """, (fact_id, emb_blob))
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")
            embedding = None
        
        conn.commit()
        
        # Auto-link to related facts
        if auto_link and embedding:
            related = self._find_related_facts_by_embedding(
                embedding, 
                exclude_id=fact_id,
                threshold=link_threshold,
                limit=5
            )
            result['related_facts'] = related
            
            for rel in related:
                link_type = self._determine_link_type(content, rel['content'])
                link = self.create_link(
                    fact_id, 
                    rel['id'], 
                    link_type,
                    strength=rel['similarity']
                )
                if link:
                    result['links_created'].append(link)
        
        conn.close()
        return result
    
    def _find_related_facts_by_embedding(
        self,
        query_embedding: List[float],
        exclude_id: Optional[int] = None,
        threshold: float = 0.5,
        limit: int = 10
    ) -> List[Dict]:
        """Find facts similar to the query embedding."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Get all facts with embeddings
        cur.execute("""
            SELECT f.id, f.category, f.subject, f.content, fe.embedding
            FROM facts f
            JOIN fact_embeddings fe ON f.id = fe.fact_id
            WHERE f.id != ?
        """, (exclude_id or -1,))
        
        results = []
        for fact_id, category, subject, content, emb_blob in cur.fetchall():
            fact_emb = self._blob_to_embedding(emb_blob)
            similarity = self._cosine_similarity(query_embedding, fact_emb)
            
            if similarity >= threshold:
                results.append({
                    'id': fact_id,
                    'category': category,
                    'subject': subject,
                    'content': content,
                    'similarity': similarity
                })
        
        conn.close()
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def _determine_link_type(
        self,
        source_content: str,
        target_content: str
    ) -> str:
        """
        Determine the type of link between two pieces of content.
        Uses simple heuristics; could be enhanced with LLM.
        """
        source_lower = source_content.lower()
        target_lower = target_content.lower()
        
        # Check for contradiction indicators
        contradiction_words = ['however', 'but', 'contrary', 'unlike', 'opposite']
        if any(w in source_lower for w in contradiction_words):
            if any(word in target_lower for word in source_lower.split()[:5]):
                return 'contradicts'
        
        # Check for extension/elaboration
        elaboration_words = ['furthermore', 'additionally', 'also', 'building on']
        if any(w in source_lower for w in elaboration_words):
            return 'extends'
        
        # Check for example
        example_words = ['for example', 'such as', 'instance', 'specifically']
        if any(w in source_lower for w in example_words):
            return 'example'
        
        # Check for causation
        causal_words = ['because', 'therefore', 'thus', 'leads to', 'results in']
        if any(w in source_lower for w in causal_words):
            return 'causes'
        
        # Check for support
        support_words = ['supports', 'confirms', 'validates', 'proves']
        if any(w in source_lower for w in support_words):
            return 'supports'
        
        # Default to related
        return 'related'
    
    # ==================== LINK MANAGEMENT ====================
    
    def create_link(
        self,
        source_id: int,
        target_id: int,
        link_type: str,
        strength: float = 0.5,
        bidirectional: bool = True
    ) -> Optional[Dict]:
        """Create a link between two facts."""
        if link_type not in LINK_TYPES:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO memory_links 
                (source_fact_id, target_fact_id, link_type, strength, bidirectional)
                VALUES (?, ?, ?, ?, ?)
            """, (source_id, target_id, link_type, strength, int(bidirectional)))
            
            link_id = cur.lastrowid
            conn.commit()
            
            return {
                'id': link_id,
                'source': source_id,
                'target': target_id,
                'type': link_type,
                'strength': strength
            }
            
        except sqlite3.IntegrityError:
            # Link already exists, strengthen it
            cur.execute("""
                UPDATE memory_links 
                SET strength = MIN(strength + 0.1, 1.0),
                    last_strengthened = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                WHERE source_fact_id = ? AND target_fact_id = ? AND link_type = ?
            """, (source_id, target_id, link_type))
            conn.commit()
            return None
        
        finally:
            conn.close()
    
    def get_links(self, fact_id: int, direction: str = 'both') -> List[Dict]:
        """Get all links for a fact."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        links = []
        
        if direction in ('both', 'outgoing'):
            cur.execute("""
                SELECT ml.id, ml.target_fact_id, ml.link_type, ml.strength,
                       f.subject, f.content
                FROM memory_links ml
                JOIN facts f ON ml.target_fact_id = f.id
                WHERE ml.source_fact_id = ?
            """, (fact_id,))
            
            for row in cur.fetchall():
                links.append({
                    'link_id': row[0],
                    'direction': 'outgoing',
                    'fact_id': row[1],
                    'type': row[2],
                    'strength': row[3],
                    'subject': row[4],
                    'content': row[5][:200]
                })
        
        if direction in ('both', 'incoming'):
            cur.execute("""
                SELECT ml.id, ml.source_fact_id, ml.link_type, ml.strength,
                       f.subject, f.content, ml.bidirectional
                FROM memory_links ml
                JOIN facts f ON ml.source_fact_id = f.id
                WHERE ml.target_fact_id = ? AND ml.bidirectional = 1
            """, (fact_id,))
            
            for row in cur.fetchall():
                links.append({
                    'link_id': row[0],
                    'direction': 'incoming',
                    'fact_id': row[1],
                    'type': row[2],
                    'strength': row[3],
                    'subject': row[4],
                    'content': row[5][:200]
                })
        
        conn.close()
        return links
    
    # ==================== MEMORY EVOLUTION ====================
    
    def evolve_memories(
        self,
        new_info: str,
        context: str = "",
        update_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Update existing memories when new information arrives.
        The A-Mem evolution pattern.
        """
        result = {
            'affected_memories': [],
            'updated': [],
            'new_links': []
        }
        
        # Find memories that might be affected
        try:
            new_embedding = self._get_embedding(new_info)
        except Exception as e:
            return {'error': str(e)}
        
        affected = self._find_related_facts_by_embedding(
            new_embedding,
            threshold=update_threshold,
            limit=10
        )
        result['affected_memories'] = affected
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        for memory in affected:
            # Check if this new info should update the memory
            if self._should_update(memory['content'], new_info):
                # Merge information
                updated_content = self._merge_information(
                    memory['content'],
                    new_info,
                    context
                )
                
                # Log evolution
                cur.execute("""
                    INSERT INTO memory_evolutions 
                    (fact_id, old_content, new_content, trigger)
                    VALUES (?, ?, ?, ?)
                """, (memory['id'], memory['content'], updated_content, new_info[:500]))
                
                # Update the fact
                cur.execute("""
                    UPDATE facts SET content = ? WHERE id = ?
                """, (updated_content, memory['id']))
                
                result['updated'].append({
                    'id': memory['id'],
                    'subject': memory['subject'],
                    'old': memory['content'][:200],
                    'new': updated_content[:200]
                })
        
        conn.commit()
        conn.close()
        
        return result
    
    def _should_update(self, existing: str, new_info: str) -> bool:
        """Determine if new info should update existing memory."""
        # Don't update if new info is too short
        if len(new_info) < 20:
            return False
        
        # Don't update if existing is much longer (probably more complete)
        if len(existing) > len(new_info) * 3:
            return False
        
        # Check for new information (simple heuristic)
        existing_words = set(existing.lower().split())
        new_words = set(new_info.lower().split())
        
        new_unique = new_words - existing_words
        
        # If at least 30% of new info words are unique, worth updating
        return len(new_unique) / len(new_words) > 0.3 if new_words else False
    
    def _merge_information(
        self,
        existing: str,
        new_info: str,
        context: str = ""
    ) -> str:
        """Merge new information into existing memory."""
        # Simple merge strategy: append with attribution
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        
        merged = existing.rstrip()
        
        if not merged.endswith('.'):
            merged += '.'
        
        merged += f"\n\n[Updated {timestamp}] {new_info}"
        
        if context:
            merged += f" (Context: {context})"
        
        return merged
    
    # ==================== CONNECTION DISCOVERY ====================
    
    def find_connections(
        self,
        fact_id: int,
        max_hops: int = 3,
        min_strength: float = 0.3
    ) -> List[Dict]:
        """
        Discover all connected facts (multi-hop traversal).
        BFS through the knowledge graph.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        visited = {fact_id}
        to_visit = [(fact_id, 0)]  # (fact_id, hops)
        connections = []
        
        while to_visit:
            current_id, hops = to_visit.pop(0)
            
            if hops >= max_hops:
                continue
            
            # Get direct links
            cur.execute("""
                SELECT ml.target_fact_id, ml.link_type, ml.strength,
                       f.subject, f.content
                FROM memory_links ml
                JOIN facts f ON ml.target_fact_id = f.id
                WHERE ml.source_fact_id = ? AND ml.strength >= ?
            """, (current_id, min_strength))
            
            for target_id, link_type, strength, subject, content in cur.fetchall():
                if target_id not in visited:
                    visited.add(target_id)
                    
                    connections.append({
                        'fact_id': target_id,
                        'subject': subject,
                        'content': content[:200],
                        'link_type': link_type,
                        'strength': strength,
                        'hops': hops + 1,
                        'path_from': current_id
                    })
                    
                    to_visit.append((target_id, hops + 1))
            
            # Also check bidirectional incoming links
            cur.execute("""
                SELECT ml.source_fact_id, ml.link_type, ml.strength,
                       f.subject, f.content
                FROM memory_links ml
                JOIN facts f ON ml.source_fact_id = f.id
                WHERE ml.target_fact_id = ? 
                  AND ml.bidirectional = 1 
                  AND ml.strength >= ?
            """, (current_id, min_strength))
            
            for source_id, link_type, strength, subject, content in cur.fetchall():
                if source_id not in visited:
                    visited.add(source_id)
                    
                    connections.append({
                        'fact_id': source_id,
                        'subject': subject,
                        'content': content[:200],
                        'link_type': f"{link_type} (reverse)",
                        'strength': strength,
                        'hops': hops + 1,
                        'path_from': current_id
                    })
                    
                    to_visit.append((source_id, hops + 1))
        
        conn.close()
        
        # Sort by hops, then strength
        connections.sort(key=lambda x: (x['hops'], -x['strength']))
        return connections
    
    # ==================== PRUNING ====================
    
    def prune_obsolete(self, days_old: int = 90) -> Dict[str, Any]:
        """Remove outdated or low-value memories."""
        result = {
            'weak_links_removed': 0,
            'orphan_facts_flagged': 0
        }
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Remove weak links that haven't been strengthened recently
        cur.execute("""
            DELETE FROM memory_links
            WHERE strength < 0.2
              AND (last_strengthened IS NULL 
                   OR last_strengthened < datetime('now', ?))
        """, (f'-{days_old} days',))
        
        result['weak_links_removed'] = cur.rowcount
        
        # Find orphan facts (no links, no recent access)
        # Don't delete, just flag for review
        cur.execute("""
            SELECT f.id, f.subject
            FROM facts f
            LEFT JOIN memory_links ml1 ON f.id = ml1.source_fact_id
            LEFT JOIN memory_links ml2 ON f.id = ml2.target_fact_id
            WHERE ml1.id IS NULL AND ml2.id IS NULL
              AND f.created_at < datetime('now', ?)
        """, (f'-{days_old} days',))
        
        orphans = cur.fetchall()
        result['orphan_facts_flagged'] = len(orphans)
        result['orphans'] = [{'id': o[0], 'subject': o[1]} for o in orphans[:10]]
        
        conn.commit()
        conn.close()
        
        return result
    
    # ==================== STATISTICS ====================
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        stats = {}
        
        cur.execute("SELECT COUNT(*) FROM facts")
        stats['total_facts'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM memory_links")
        stats['total_links'] = cur.fetchone()[0]
        
        cur.execute("""
            SELECT link_type, COUNT(*) 
            FROM memory_links 
            GROUP BY link_type
        """)
        stats['links_by_type'] = dict(cur.fetchall())
        
        cur.execute("SELECT AVG(strength) FROM memory_links")
        stats['avg_link_strength'] = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM memory_evolutions")
        stats['total_evolutions'] = cur.fetchone()[0]
        
        # Most connected facts
        cur.execute("""
            SELECT f.id, f.subject, COUNT(ml.id) as link_count
            FROM facts f
            LEFT JOIN memory_links ml ON f.id = ml.source_fact_id 
                                      OR f.id = ml.target_fact_id
            GROUP BY f.id
            ORDER BY link_count DESC
            LIMIT 5
        """)
        stats['most_connected'] = [
            {'id': r[0], 'subject': r[1], 'links': r[2]}
            for r in cur.fetchall()
        ]
        
        conn.close()
        return stats


# ==================== CLI INTERFACE ====================

def main():
    import sys
    
    mem = MemoryEvolution()
    
    if len(sys.argv) < 2:
        print("Usage: memory_evolution.py <command> [args]")
        print("Commands:")
        print("  add <category> <subject> <content> - Add fact with auto-linking")
        print("  link <source_id> <target_id> <type> - Create manual link")
        print("  links <fact_id>                    - Show links for fact")
        print("  connections <fact_id> [max_hops]   - Find all connections")
        print("  evolve <new_info> [context]        - Evolve affected memories")
        print("  prune [days]                       - Prune old weak links")
        print("  stats                              - Show graph statistics")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'add' and len(sys.argv) >= 5:
        result = mem.add_with_links(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))
    
    elif cmd == 'link' and len(sys.argv) >= 5:
        link = mem.create_link(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        print(json.dumps(link, indent=2) if link else "Link already exists")
    
    elif cmd == 'links' and len(sys.argv) >= 3:
        links = mem.get_links(int(sys.argv[2]))
        print(json.dumps(links, indent=2))
    
    elif cmd == 'connections' and len(sys.argv) >= 3:
        max_hops = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        connections = mem.find_connections(int(sys.argv[2]), max_hops)
        print(json.dumps(connections, indent=2))
    
    elif cmd == 'evolve' and len(sys.argv) >= 3:
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        result = mem.evolve_memories(sys.argv[2], context)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'prune':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        result = mem.prune_obsolete(days)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'stats':
        stats = mem.get_graph_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print("Invalid command or arguments")


if __name__ == "__main__":
    main()
