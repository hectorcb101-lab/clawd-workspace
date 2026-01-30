#!/usr/bin/env python3
"""
Migrate all markdown memory files into the SQLite database.
"""
import sqlite3
import os
import re
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "atlas_memory.db"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
MEMORY_MD = Path(__file__).parent.parent / "MEMORY.md"

def get_conn():
    return sqlite3.connect(DB_PATH)

def parse_memory_md(content: str) -> list[dict]:
    """Extract facts from MEMORY.md structured content."""
    facts = []
    current_section = ""
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Track section headers
        if line.startswith('## '):
            current_section = line[3:].strip()
        elif line.startswith('### '):
            subsection = line[4:].strip()
            current_section = subsection
        
        # Extract bullet points as facts
        if line.startswith('- **') and ':**' in line:
            # Format: - **Key:** Value
            match = re.match(r'- \*\*(.+?):\*\*\s*(.+)', line)
            if match:
                key, value = match.groups()
                facts.append({
                    'category': current_section or 'general',
                    'subject': key,
                    'content': value,
                    'source': 'migration:MEMORY.md'
                })
        elif line.startswith('- '):
            # Simple bullet point
            content = line[2:].strip()
            if content and current_section:
                facts.append({
                    'category': current_section,
                    'subject': '',
                    'content': content,
                    'source': 'migration:MEMORY.md'
                })
        
        i += 1
    
    return facts

def parse_daily_log(filepath: Path) -> dict:
    """Parse a daily log file."""
    content = filepath.read_text()
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath.name)
    date = date_match.group(1) if date_match else filepath.stem
    
    return {
        'date': date,
        'file_path': str(filepath),
        'content': content
    }

def extract_facts_from_daily(content: str, date: str) -> list[dict]:
    """Extract notable facts from daily logs."""
    facts = []
    
    # Look for key patterns
    patterns = [
        (r'## (.+?) - (.+)', 'event'),  # ## Time - Event
        (r'\*\*(.+?):\*\*\s*(.+)', 'detail'),  # **Key:** Value
        (r'✅\s*(.+)', 'completed'),  # ✅ Completed item
    ]
    
    for pattern, category in patterns:
        for match in re.finditer(pattern, content):
            if category == 'event':
                facts.append({
                    'category': f'daily:{date}',
                    'subject': match.group(1),
                    'content': match.group(2),
                    'source': f'migration:memory/{date}.md'
                })
            elif category == 'detail':
                facts.append({
                    'category': f'daily:{date}',
                    'subject': match.group(1),
                    'content': match.group(2),
                    'source': f'migration:memory/{date}.md'
                })
            elif category == 'completed':
                facts.append({
                    'category': 'completed_tasks',
                    'subject': date,
                    'content': match.group(1),
                    'source': f'migration:memory/{date}.md'
                })
    
    return facts

def migrate():
    conn = get_conn()
    cur = conn.cursor()
    
    migrated = {'facts': 0, 'daily_logs': 0}
    
    # 1. Migrate MEMORY.md
    if MEMORY_MD.exists():
        print(f"Migrating {MEMORY_MD}...")
        content = MEMORY_MD.read_text()
        facts = parse_memory_md(content)
        
        for fact in facts:
            try:
                cur.execute("""
                    INSERT INTO facts (category, subject, content, source)
                    VALUES (?, ?, ?, ?)
                """, (fact['category'], fact['subject'], fact['content'], fact['source']))
                migrated['facts'] += 1
            except sqlite3.IntegrityError:
                pass  # Skip duplicates
        
        # Also store the full content as a daily log entry
        cur.execute("""
            INSERT OR REPLACE INTO daily_logs (date, file_path, content)
            VALUES (?, ?, ?)
        """, ('MEMORY', str(MEMORY_MD), content))
    
    # 2. Migrate daily log files
    if MEMORY_DIR.exists():
        for filepath in sorted(MEMORY_DIR.glob('*.md')):
            print(f"Migrating {filepath.name}...")
            log = parse_daily_log(filepath)
            
            # Store full content
            cur.execute("""
                INSERT OR REPLACE INTO daily_logs (date, file_path, content)
                VALUES (?, ?, ?)
            """, (log['date'], log['file_path'], log['content']))
            migrated['daily_logs'] += 1
            
            # Extract and store facts
            facts = extract_facts_from_daily(log['content'], log['date'])
            for fact in facts:
                try:
                    cur.execute("""
                        INSERT INTO facts (category, subject, content, source)
                        VALUES (?, ?, ?, ?)
                    """, (fact['category'], fact['subject'], fact['content'], fact['source']))
                    migrated['facts'] += 1
                except:
                    pass
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration complete:")
    print(f"   - {migrated['facts']} facts extracted")
    print(f"   - {migrated['daily_logs']} daily logs indexed")
    
    return migrated

if __name__ == '__main__':
    migrate()
