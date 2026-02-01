"""
Atlas Self-Awareness System - Database Layer

SQLite database for storing outcomes, corrections, patterns, and insights.
Designed for my own use - optimised for querying and analysis.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

# Database location
DB_PATH = Path(__file__).parent.parent / "data" / "self_awareness.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for dict-like access."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session():
    """Context manager for database sessions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize the database schema."""
    with db_session() as conn:
        # Outcomes table - task results with outcome classification
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                outcome TEXT NOT NULL CHECK(outcome IN ('success', 'failure', 'partial', 'unknown')),
                task_type TEXT NOT NULL,
                task_subtype TEXT,
                confidence REAL DEFAULT 0.5 CHECK(confidence >= 0.0 AND confidence <= 1.0),
                feedback_source TEXT NOT NULL CHECK(feedback_source IN ('self', 'user', 'system')),
                notes TEXT,
                context TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Corrections table - when Finn corrects me
        conn.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_event_id TEXT,
                correction_type TEXT NOT NULL CHECK(correction_type IN ('factual', 'approach', 'style', 'other')),
                severity TEXT NOT NULL CHECK(severity IN ('minor', 'moderate', 'major')),
                user_signal TEXT NOT NULL,
                lesson TEXT,
                task_type TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Patterns table - identified recurring patterns
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL CHECK(pattern_type IN ('failure', 'strength')),
                description TEXT NOT NULL,
                task_types TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'resolved', 'monitoring')),
                confidence REAL DEFAULT 0.5,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Pattern occurrences - links patterns to specific events
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pattern_occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id INTEGER NOT NULL,
                event_type TEXT NOT NULL CHECK(event_type IN ('outcome', 'correction')),
                event_ref_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (pattern_id) REFERENCES patterns(id)
            )
        """)
        
        # Insights table - generated insights for surfacing
        conn.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL CHECK(insight_type IN ('blind_spot', 'improvement', 'regression', 'tip', 'warning')),
                message TEXT NOT NULL,
                evidence TEXT,
                priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                surfaced INTEGER DEFAULT 0,
                surfaced_at TEXT,
                actionable INTEGER DEFAULT 1,
                suggested_action TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Trends table - aggregated statistics over time
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                period_type TEXT NOT NULL CHECK(period_type IN ('day', 'week', 'month')),
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                total_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                partial_count INTEGER DEFAULT 0,
                unknown_count INTEGER DEFAULT 0,
                success_rate REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(task_type, period_type, period_start)
            )
        """)
        
        # Create indexes for common queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_task_type ON outcomes(task_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_outcome ON outcomes(outcome)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_created_at ON outcomes(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_corrections_task_type ON corrections(task_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_corrections_created_at ON corrections(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_status ON patterns(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_insights_priority ON insights(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_insights_surfaced ON insights(surfaced)")
        
        print(f"✓ Database initialized at {DB_PATH}")


def get_stats() -> dict:
    """Get basic statistics about the database."""
    with db_session() as conn:
        stats = {}
        
        # Count outcomes
        result = conn.execute("SELECT COUNT(*) as count FROM outcomes").fetchone()
        stats['total_outcomes'] = result['count']
        
        # Outcome breakdown
        result = conn.execute("""
            SELECT outcome, COUNT(*) as count 
            FROM outcomes 
            GROUP BY outcome
        """).fetchall()
        stats['outcomes_by_type'] = {row['outcome']: row['count'] for row in result}
        
        # Count corrections
        result = conn.execute("SELECT COUNT(*) as count FROM corrections").fetchone()
        stats['total_corrections'] = result['count']
        
        # Count patterns
        result = conn.execute("SELECT COUNT(*) as count FROM patterns WHERE status = 'active'").fetchone()
        stats['active_patterns'] = result['count']
        
        # Count insights
        result = conn.execute("SELECT COUNT(*) as count FROM insights WHERE surfaced = 0").fetchone()
        stats['pending_insights'] = result['count']
        
        return stats


if __name__ == "__main__":
    init_database()
    print("\nCurrent stats:")
    stats = get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
