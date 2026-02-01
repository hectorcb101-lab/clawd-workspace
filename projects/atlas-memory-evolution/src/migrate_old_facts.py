#!/usr/bin/env python3
"""
Migrate facts from old atlas_memory.db into new event system.
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from event_log import get_log
from event_schema import EventType, Event

def migrate():
    old_db = Path("/home/ubuntu/clawd/atlas-memory/atlas_memory.db")
    if not old_db.exists():
        print("❌ Old database not found")
        return
    
    conn = sqlite3.connect(old_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, category, subject, content, source, created_at 
        FROM facts ORDER BY created_at
    """)
    facts = cursor.fetchall()
    
    print(f"📦 Found {len(facts)} facts to migrate")
    
    log = get_log()
    migrated = 0
    
    for fact in facts:
        event = Event(
            type=EventType.LEARNING,
            content={
                "summary": f"[{fact['category']}] {fact['subject']}",
                "details": fact['content'],
                "category": fact['category'],
                "subject": fact['subject'],
            },
            source="migration:atlas_memory.db",
            metadata={
                "original_id": fact['id'],
                "original_source": fact['source'],
                "migrated": True
            }
        )
        
        if fact['created_at']:
            event.timestamp = fact['created_at']
        
        log.append(event)
        migrated += 1
        
        if migrated % 100 == 0:
            print(f"  Migrated {migrated}/{len(facts)}...")
    
    conn.close()
    print(f"✅ Migrated {migrated} facts as learning events")
    
    print("\n🔄 Running extraction...")
    from extractor import run_extraction
    stats = run_extraction()
    print(f"✅ Extraction: {stats}")

if __name__ == "__main__":
    migrate()
