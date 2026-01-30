#!/usr/bin/env python3
"""
Query the atlas memory database.
This is the primary interface for memory recall.
"""
import sqlite3
import os
import struct
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "atlas_memory.db"

def get_embedding(text: str) -> list[float]:
    """Get embedding from OpenAI API."""
    import urllib.request
    import json
    
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

def blob_to_embedding(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = sum(x*x for x in a) ** 0.5
    norm_b = sum(x*x for x in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0

def semantic_search(query: str, limit: int = 10, min_score: float = 0.3) -> list[dict]:
    """Search facts by semantic similarity."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get query embedding
    query_emb = get_embedding(query)
    
    # Get all facts with embeddings
    cur.execute("""
        SELECT f.id, f.category, f.subject, f.content, f.source, fe.embedding
        FROM facts f
        JOIN fact_embeddings fe ON f.id = fe.fact_id
    """)
    
    results = []
    for fact_id, category, subject, content, source, emb_blob in cur.fetchall():
        fact_emb = blob_to_embedding(emb_blob)
        score = cosine_similarity(query_emb, fact_emb)
        
        if score >= min_score:
            results.append({
                'id': fact_id,
                'category': category,
                'subject': subject,
                'content': content,
                'source': source,
                'score': score
            })
    
    conn.close()
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]

def keyword_search(query: str, limit: int = 10) -> list[dict]:
    """Search facts by keyword (FTS5)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Escape special FTS5 characters and wrap in quotes
    safe_query = '"' + query.replace('"', '""') + '"'
    
    # Use FTS5 match
    try:
        cur.execute("""
            SELECT f.id, f.category, f.subject, f.content, f.source
            FROM facts f
            JOIN facts_fts fts ON f.id = fts.rowid
            WHERE facts_fts MATCH ?
            LIMIT ?
        """, (safe_query, limit))
    except sqlite3.OperationalError:
        # FTS query failed, return empty
        conn.close()
        return []
    
    results = []
    for fact_id, category, subject, content, source in cur.fetchall():
        results.append({
            'id': fact_id,
            'category': category,
            'subject': subject,
            'content': content,
            'source': source,
            'score': 1.0  # FTS doesn't give similarity scores
        })
    
    conn.close()
    return results

def search_daily_logs(query: str, limit: int = 5) -> list[dict]:
    """Search daily log content."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Simple LIKE search
    cur.execute("""
        SELECT date, file_path, content
        FROM daily_logs
        WHERE content LIKE ?
        ORDER BY date DESC
        LIMIT ?
    """, (f'%{query}%', limit))
    
    results = []
    for date, path, content in cur.fetchall():
        # Extract relevant snippet
        idx = content.lower().find(query.lower())
        start = max(0, idx - 100)
        end = min(len(content), idx + len(query) + 100)
        snippet = content[start:end]
        
        results.append({
            'date': date,
            'path': path,
            'snippet': f"...{snippet}..."
        })
    
    conn.close()
    return results

def hybrid_search(query: str, limit: int = 10) -> list[dict]:
    """Combine semantic and keyword search."""
    semantic = semantic_search(query, limit=limit)
    keyword = keyword_search(query, limit=limit)
    
    # Merge results, preferring semantic
    seen_ids = set()
    results = []
    
    for r in semantic:
        results.append(r)
        seen_ids.add(r['id'])
    
    for r in keyword:
        if r['id'] not in seen_ids:
            r['score'] = 0.5  # Lower score for keyword-only
            results.append(r)
    
    return results[:limit]

def main():
    import json
    
    if len(sys.argv) < 2:
        print("Usage: query.py <search_query> [--limit N] [--mode semantic|keyword|hybrid]")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = 10
    mode = 'hybrid'
    
    # Parse args
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--limit' and i+1 < len(sys.argv):
            limit = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--mode' and i+1 < len(sys.argv):
            mode = sys.argv[i+1]
            i += 2
        else:
            i += 1
    
    if mode == 'semantic':
        results = semantic_search(query, limit)
    elif mode == 'keyword':
        results = keyword_search(query, limit)
    else:
        results = hybrid_search(query, limit)
    
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
