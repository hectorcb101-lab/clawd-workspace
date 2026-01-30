#!/usr/bin/env python3
"""
Self-Improvement Engine for Atlas
Implements Gödel Agent pattern: self-referential recursive improvement
"""
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

CLAWD_DIR = Path(__file__).parent.parent
DB_PATH = CLAWD_DIR / "atlas-memory" / "atlas_memory.db"
AGENTS_MD = CLAWD_DIR / "AGENTS.md"
LEARNINGS_DIR = CLAWD_DIR / ".learnings"

def get_db():
    return sqlite3.connect(DB_PATH)

def log_improvement(category: str, trigger: str, before: str, after: str, confidence: float):
    """Log a self-improvement action to the database."""
    conn = get_db()
    cur = conn.cursor()
    
    # Create improvements table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS self_improvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            category TEXT NOT NULL,
            trigger TEXT NOT NULL,
            before_state TEXT,
            after_state TEXT,
            confidence REAL,
            verified INTEGER DEFAULT 0
        )
    """)
    
    cur.execute("""
        INSERT INTO self_improvements (category, trigger, before_state, after_state, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (category, trigger, before, after, confidence))
    
    conn.commit()
    conn.close()
    print(f"✅ Logged improvement: {category}")

def add_learning_to_agents(section: str, content: str):
    """Add a learning to AGENTS.md under the specified section."""
    agents_content = AGENTS_MD.read_text()
    
    # Find the section and add content
    section_marker = f"## {section}"
    if section_marker in agents_content:
        # Find end of section (next ## or end of file)
        start = agents_content.find(section_marker)
        next_section = agents_content.find("\n## ", start + 1)
        
        if next_section == -1:
            next_section = len(agents_content)
        
        # Insert before next section
        insert_point = next_section
        new_content = agents_content[:insert_point] + f"\n{content}\n" + agents_content[insert_point:]
        
        AGENTS_MD.write_text(new_content)
        print(f"✅ Added learning to AGENTS.md section: {section}")
        return True
    
    print(f"⚠️ Section not found: {section}")
    return False

def add_fact(category: str, subject: str, content: str, source: str = "self_improvement"):
    """Add a fact to the memory database."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO facts (category, subject, content, source)
        VALUES (?, ?, ?, ?)
    """, (category, subject, content, source))
    
    fact_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Added fact #{fact_id}: {subject}")
    return fact_id

def detect_correction(user_message: str) -> bool:
    """Detect if a message is a correction."""
    correction_triggers = [
        "no,", "no ", "wrong", "actually", "instead", 
        "that's not", "don't do", "never do", "always do",
        "you should", "you shouldn't", "incorrect"
    ]
    lower = user_message.lower()
    return any(trigger in lower for trigger in correction_triggers)

def extract_correction_learning(user_message: str, context: str = "") -> dict:
    """Extract the learning from a correction."""
    # This would ideally use LLM to extract, but we can do basic extraction
    return {
        "trigger": user_message,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }

def record_capability_gap(capability: str, context: str):
    """Record when we hit a capability gap to address later."""
    gaps_file = LEARNINGS_DIR / "CAPABILITY_GAPS.md"
    gaps_file.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {timestamp} - {capability}\n{context}\n**Status:** Open\n"
    
    if gaps_file.exists():
        content = gaps_file.read_text()
    else:
        content = "# Capability Gaps\n\nThings I need to learn or build.\n"
    
    gaps_file.write_text(content + entry)
    print(f"✅ Recorded capability gap: {capability}")

def get_improvement_stats() -> dict:
    """Get statistics on self-improvements made."""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM self_improvements")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM self_improvements WHERE verified = 1")
        verified = cur.fetchone()[0]
        
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM self_improvements 
            GROUP BY category
        """)
        by_category = dict(cur.fetchall())
        
        return {
            "total_improvements": total,
            "verified_improvements": verified,
            "by_category": by_category
        }
    except:
        return {"total_improvements": 0, "verified_improvements": 0, "by_category": {}}
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: self_improve.py <command> [args]")
        print("Commands:")
        print("  log <category> <trigger> <before> <after> <confidence>")
        print("  add_fact <category> <subject> <content>")
        print("  gap <capability> <context>")
        print("  stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "log" and len(sys.argv) >= 7:
        log_improvement(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], float(sys.argv[6]))
    elif cmd == "add_fact" and len(sys.argv) >= 5:
        add_fact(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "gap" and len(sys.argv) >= 4:
        record_capability_gap(sys.argv[2], sys.argv[3])
    elif cmd == "stats":
        stats = get_improvement_stats()
        print(json.dumps(stats, indent=2))
    else:
        print("Invalid command or arguments")
        sys.exit(1)
