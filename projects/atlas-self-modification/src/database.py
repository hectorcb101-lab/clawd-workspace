"""
Database setup and schema for Atlas Self-Modification System.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

# Database location
DB_PATH = Path(__file__).parent.parent / "data" / "modifications.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Modification Requests - proposed changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modification_requests (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL CHECK(source IN ('insight', 'correction', 'pattern', 'manual')),
            source_id TEXT,
            target_file TEXT NOT NULL,
            target_section TEXT,
            modification_type TEXT NOT NULL CHECK(modification_type IN ('append', 'edit', 'delete', 'restructure')),
            content TEXT NOT NULL,
            reason TEXT NOT NULL,
            evidence TEXT,
            risk_level TEXT NOT NULL CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
            risk_score INTEGER NOT NULL DEFAULT 0,
            confidence REAL NOT NULL DEFAULT 0.5 CHECK(confidence >= 0.0 AND confidence <= 1.0),
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'applied', 'rejected', 'rolled_back', 'expired')),
            requires_approval INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            applied_at TEXT,
            applied_by TEXT CHECK(applied_by IN ('auto', 'human', NULL)),
            rejected_reason TEXT,
            effectiveness_score REAL,
            evaluation_deadline TEXT
        )
    """)
    
    # Modification Logs - applied changes with diffs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modification_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            before_content TEXT NOT NULL,
            after_content TEXT NOT NULL,
            diff TEXT NOT NULL,
            git_commit_hash TEXT,
            applied_at TEXT NOT NULL,
            reverted_at TEXT,
            revert_reason TEXT,
            FOREIGN KEY (modification_id) REFERENCES modification_requests(id)
        )
    """)
    
    # Modification Rules - auto-proposal triggers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modification_rules (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            trigger_type TEXT NOT NULL CHECK(trigger_type IN ('correction_type', 'insight_type', 'pattern', 'keyword')),
            trigger_match TEXT NOT NULL,
            target_file TEXT NOT NULL,
            target_section TEXT,
            action_template TEXT NOT NULL,
            risk_level TEXT NOT NULL DEFAULT 'medium' CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
            auto_apply INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_triggered_at TEXT,
            trigger_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    # Outcome tracking - did the modification help?
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modification_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modification_id TEXT NOT NULL,
            outcome_type TEXT NOT NULL CHECK(outcome_type IN ('error_count', 'user_feedback', 'self_assessment')),
            metric_name TEXT NOT NULL,
            before_value REAL,
            after_value REAL,
            measurement_date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (modification_id) REFERENCES modification_requests(id)
        )
    """)
    
    # Indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_status ON modification_requests(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_target ON modification_requests(target_file)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_created ON modification_requests(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_modification ON modification_logs(modification_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_trigger ON modification_rules(trigger_type, trigger_match)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_modification ON modification_outcomes(modification_id)")
    
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get database statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Request counts by status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM modification_requests 
        GROUP BY status
    """)
    stats['requests_by_status'] = dict(cursor.fetchall())
    
    # Total requests
    cursor.execute("SELECT COUNT(*) FROM modification_requests")
    stats['total_requests'] = cursor.fetchone()[0]
    
    # Applied modifications
    cursor.execute("SELECT COUNT(*) FROM modification_logs WHERE reverted_at IS NULL")
    stats['active_modifications'] = cursor.fetchone()[0]
    
    # Rollbacks
    cursor.execute("SELECT COUNT(*) FROM modification_logs WHERE reverted_at IS NOT NULL")
    stats['rollbacks'] = cursor.fetchone()[0]
    
    # Active rules
    cursor.execute("SELECT COUNT(*) FROM modification_rules WHERE active = 1")
    stats['active_rules'] = cursor.fetchone()[0]
    
    conn.close()
    return stats


if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print(f"Database created at: {DB_PATH}")
    stats = get_stats()
    print(f"Stats: {stats}")
