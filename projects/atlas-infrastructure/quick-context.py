#!/usr/bin/env python3
"""
Quick Context - Fast session startup for Atlas

Surfaces the most relevant context for a new session:
- Recent memory entries
- Active exploration items
- Pending learnings to review
- Soul aspects summary
- Key facts

Run at session start to reduce ramp-up time.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

CLAWD_ROOT = Path.home() / "clawd"
MEMORY_DIR = CLAWD_ROOT / "memory"
ATLAS_MEMORY_DB = CLAWD_ROOT / "atlas-memory" / "atlas_memory.db"
LEARNINGS_DIR = CLAWD_ROOT / ".learnings"

def get_recent_memory_files(days=3):
    """Get memory files from the last N days."""
    files = []
    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = MEMORY_DIR / filename
        if filepath.exists():
            files.append((date.strftime('%Y-%m-%d'), filepath))
    return files

def get_exploration_status():
    """Get current exploration queue from exploration.md."""
    exp_file = MEMORY_DIR / "exploration.md"
    if not exp_file.exists():
        return []
    
    content = exp_file.read_text()
    # Find unchecked items
    items = []
    for line in content.split('\n'):
        if line.strip().startswith('- [ ]'):
            items.append(line.strip()[6:])
    return items[:5]  # Top 5

def get_soul_summary():
    """Get soul aspects from atlas-memory."""
    if not ATLAS_MEMORY_DB.exists():
        return {}
    
    conn = sqlite3.connect(ATLAS_MEMORY_DB)
    cur = conn.cursor()
    aspects = {}
    for row in cur.execute('SELECT aspect, substr(content, 1, 150) FROM soul'):
        aspects[row[0]] = row[1] + '...' if len(row[1]) >= 150 else row[1]
    conn.close()
    return aspects

def get_recent_facts(limit=5):
    """Get most recently added facts."""
    if not ATLAS_MEMORY_DB.exists():
        return []
    
    conn = sqlite3.connect(ATLAS_MEMORY_DB)
    cur = conn.cursor()
    facts = []
    for row in cur.execute('''
        SELECT category, subject, substr(content, 1, 100) 
        FROM facts ORDER BY created_at DESC LIMIT ?
    ''', (limit,)):
        facts.append(f"[{row[0]}] {row[1]}: {row[2]}")
    conn.close()
    return facts

def get_pending_learnings():
    """Check for unreviewed learnings."""
    learnings_file = LEARNINGS_DIR / "LEARNINGS.md"
    if not learnings_file.exists():
        return 0
    
    content = learnings_file.read_text()
    # Count entries (rough estimate by counting IDs)
    return content.count('LRN-')

def main():
    print("=" * 60)
    print("ATLAS QUICK CONTEXT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Recent memory
    print("\n📅 RECENT MEMORY FILES")
    for date, filepath in get_recent_memory_files():
        size = filepath.stat().st_size
        print(f"  {date}: {size:,} bytes")
    
    # Exploration queue
    print("\n🔍 EXPLORATION QUEUE (top 5)")
    items = get_exploration_status()
    if items:
        for item in items:
            print(f"  • {item}")
    else:
        print("  (none pending)")
    
    # Soul summary
    print("\n🧠 SOUL ASPECTS")
    aspects = get_soul_summary()
    for aspect, content in aspects.items():
        print(f"  {aspect}:")
        print(f"    {content[:80]}...")
    
    # Recent facts
    print("\n📚 RECENT FACTS")
    facts = get_recent_facts()
    if facts:
        for fact in facts:
            print(f"  • {fact[:70]}...")
    else:
        print("  (none stored)")
    
    # Learnings
    print("\n📝 LEARNINGS")
    count = get_pending_learnings()
    print(f"  {count} entries in LEARNINGS.md")
    
    print("\n" + "=" * 60)
    print("Ready to go. 🏛️")

if __name__ == "__main__":
    main()
