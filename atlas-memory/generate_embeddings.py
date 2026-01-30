#!/usr/bin/env python3
"""
Generate embeddings for all facts that don't have them yet.
Uses OpenAI's text-embedding-3-small model.
"""
import sqlite3
import os
import struct
from pathlib import Path

DB_PATH = Path(__file__).parent / "atlas_memory.db"

def get_embedding(text: str) -> list[float]:
    """Get embedding from OpenAI API."""
    import urllib.request
    import json
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        # Try loading from clawdbot env
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
        "input": text[:8000]  # Truncate if too long
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

def embedding_to_blob(embedding: list[float]) -> bytes:
    """Convert embedding list to blob for storage."""
    return struct.pack(f'{len(embedding)}f', *embedding)

def blob_to_embedding(blob: bytes) -> list[float]:
    """Convert blob back to embedding list."""
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def generate_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Find facts without embeddings
    cur.execute("""
        SELECT f.id, f.category, f.subject, f.content 
        FROM facts f
        LEFT JOIN fact_embeddings fe ON f.id = fe.fact_id
        WHERE fe.id IS NULL
    """)
    facts = cur.fetchall()
    
    print(f"Found {len(facts)} facts without embeddings")
    
    generated = 0
    for fact_id, category, subject, content in facts:
        # Create searchable text
        text = f"{category} | {subject} | {content}"
        
        try:
            embedding = get_embedding(text)
            blob = embedding_to_blob(embedding)
            
            cur.execute("""
                INSERT INTO fact_embeddings (fact_id, embedding)
                VALUES (?, ?)
            """, (fact_id, blob))
            
            generated += 1
            if generated % 50 == 0:
                print(f"  Generated {generated}/{len(facts)} embeddings...")
                conn.commit()
        except Exception as e:
            print(f"  Error on fact {fact_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Generated {generated} embeddings")

if __name__ == '__main__':
    generate_all()
