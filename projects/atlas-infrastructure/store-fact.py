#!/usr/bin/env python3
"""
Store Fact - Quick fact storage for Atlas

Store a fact in atlas-memory database for future recall.

Usage:
    python store-fact.py "Category" "Subject" "Content"
    
Examples:
    python store-fact.py "Finn Preferences" "Communication" "Prefers concise responses, no fluff"
    python store-fact.py "Technical Learning" "Clawdbot" "NO_REPLY is a special token that suppresses output"
    python store-fact.py "Self Insight" "Identity" "I exist as a series of runs sharing files"
"""

import sys
import sqlite3
from datetime import datetime
from pathlib import Path

ATLAS_MEMORY_DB = Path.home() / "clawd" / "atlas-memory" / "atlas_memory.db"

def store_fact(category: str, subject: str, content: str, source: str = "manual"):
    """Store a fact in the atlas-memory database."""
    if not ATLAS_MEMORY_DB.exists():
        print(f"Error: Database not found at {ATLAS_MEMORY_DB}")
        return False
    
    conn = sqlite3.connect(ATLAS_MEMORY_DB)
    cur = conn.cursor()
    
    # Check for duplicates (same category + subject + similar content)
    cur.execute('''
        SELECT id, content FROM facts 
        WHERE category = ? AND subject = ?
    ''', (category, subject))
    
    existing = cur.fetchall()
    for row in existing:
        if content.lower() in row[1].lower() or row[1].lower() in content.lower():
            print(f"⚠️  Similar fact already exists (id={row[0]})")
            print(f"   Existing: {row[1][:80]}...")
            conn.close()
            return False
    
    # Insert new fact
    cur.execute('''
        INSERT INTO facts (category, subject, content, source)
        VALUES (?, ?, ?, ?)
    ''', (category, subject, content, source))
    
    fact_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Stored fact #{fact_id}")
    print(f"   Category: {category}")
    print(f"   Subject: {subject}")
    print(f"   Content: {content[:80]}{'...' if len(content) > 80 else ''}")
    
    return True

def list_categories():
    """List all existing categories."""
    if not ATLAS_MEMORY_DB.exists():
        return []
    
    conn = sqlite3.connect(ATLAS_MEMORY_DB)
    cur = conn.cursor()
    categories = [row[0] for row in cur.execute('SELECT DISTINCT category FROM facts')]
    conn.close()
    return categories

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExisting categories:")
        for cat in list_categories():
            print(f"  • {cat}")
        return
    
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print("Categories:")
        for cat in list_categories():
            print(f"  • {cat}")
        return
    
    if len(sys.argv) < 4:
        print("Usage: python store-fact.py \"Category\" \"Subject\" \"Content\"")
        return
    
    category = sys.argv[1]
    subject = sys.argv[2]
    content = sys.argv[3]
    
    store_fact(category, subject, content)

if __name__ == "__main__":
    main()
