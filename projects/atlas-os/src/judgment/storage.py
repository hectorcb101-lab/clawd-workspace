"""
SQLite storage for the Judgment Layer.
Integrated with Atlas OS Event Bus for training data capture.
"""
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from .models import (
    Principle, PrincipleApplication, CalibrationRecord,
    PrincipleCategory, PrincipleSource, ApplicationOutcome
)

# Add Atlas OS bus to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def _emit_judgment_to_bus(situation: str, principles: list, reasoning: str, decision: str, outcome: str = None):
    """Emit judgment application to Atlas OS Event Bus (non-blocking, fail-safe)."""
    try:
        from bus.hooks import log_judgment
        log_judgment(
            situation=situation,
            principles=principles,
            reasoning=reasoning,
            decision=decision,
            outcome=outcome
        )
    except Exception:
        pass  # Don't let bus errors break judgment layer

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "judgment.db"


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def init_schema(conn: sqlite3.Connection):
    """Initialize database schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS principles (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            rationale TEXT NOT NULL,
            examples TEXT DEFAULT '[]',
            counter_examples TEXT DEFAULT '[]',
            keywords TEXT DEFAULT '[]',
            source TEXT DEFAULT 'manual',
            source_id TEXT,
            confidence REAL DEFAULT 0.5,
            priority INTEGER DEFAULT 5,
            applications_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            active INTEGER DEFAULT 1
        );
        
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            principle_id TEXT NOT NULL,
            situation TEXT NOT NULL,
            how_applied TEXT NOT NULL,
            decision_made TEXT NOT NULL,
            outcome TEXT DEFAULT 'unknown',
            outcome_notes TEXT DEFAULT '',
            applied_at TEXT NOT NULL,
            evaluated_at TEXT,
            FOREIGN KEY (principle_id) REFERENCES principles(id)
        );
        
        CREATE TABLE IF NOT EXISTS calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            actual_outcome TEXT NOT NULL,
            correct INTEGER NOT NULL,
            recorded_at TEXT NOT NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_applications_principle 
            ON applications(principle_id);
        CREATE INDEX IF NOT EXISTS idx_applications_outcome 
            ON applications(outcome);
        CREATE INDEX IF NOT EXISTS idx_calibration_domain 
            ON calibration(domain);
    """)
    conn.commit()


class JudgmentStorage:
    """Storage operations for the Judgment Layer."""
    
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = get_connection(db_path)
    
    def close(self):
        self.conn.close()
    
    # ─────────────────────────────────────────────────────────────
    # Principles
    # ─────────────────────────────────────────────────────────────
    
    def save_principle(self, principle: Principle) -> str:
        """Save or update a principle."""
        principle.updated_at = datetime.utcnow()
        
        self.conn.execute("""
            INSERT OR REPLACE INTO principles 
            (id, category, content, rationale, examples, counter_examples,
             keywords, source, source_id, confidence, priority,
             applications_count, success_count, created_at, updated_at, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            principle.id,
            principle.category.value,
            principle.content,
            principle.rationale,
            json.dumps(principle.examples),
            json.dumps(principle.counter_examples),
            json.dumps(principle.keywords),
            principle.source.value,
            principle.source_id,
            principle.confidence,
            principle.priority,
            principle.applications_count,
            principle.success_count,
            principle.created_at.isoformat(),
            principle.updated_at.isoformat(),
            1 if principle.active else 0,
        ))
        self.conn.commit()
        return principle.id
    
    def get_principle(self, principle_id: str) -> Optional[Principle]:
        """Get a principle by ID."""
        row = self.conn.execute(
            "SELECT * FROM principles WHERE id = ?", (principle_id,)
        ).fetchone()
        
        if not row:
            return None
        return self._row_to_principle(row)
    
    def list_principles(
        self, 
        category: Optional[PrincipleCategory] = None,
        active_only: bool = True
    ) -> List[Principle]:
        """List principles with optional filters."""
        query = "SELECT * FROM principles WHERE 1=1"
        params = []
        
        if active_only:
            query += " AND active = 1"
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        query += " ORDER BY priority DESC, created_at ASC"
        
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_principle(row) for row in rows]
    
    def search_principles(self, keywords: List[str]) -> List[Principle]:
        """Search principles by keywords."""
        # Simple keyword matching - could be improved with FTS
        all_principles = self.list_principles()
        results = []
        
        for principle in all_principles:
            score = 0
            text = f"{principle.content} {principle.rationale} {' '.join(principle.keywords)}".lower()
            for kw in keywords:
                if kw.lower() in text:
                    score += 1
            if score > 0:
                results.append((score, principle))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results]
    
    def get_next_principle_id(self) -> str:
        """Generate next principle ID."""
        row = self.conn.execute(
            "SELECT COUNT(*) as count FROM principles"
        ).fetchone()
        count = row["count"] + 1
        return f"PRINC-{count:03d}"
    
    def deactivate_principle(self, principle_id: str):
        """Deactivate a principle (soft delete)."""
        self.conn.execute(
            "UPDATE principles SET active = 0, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), principle_id)
        )
        self.conn.commit()
    
    def _row_to_principle(self, row: sqlite3.Row) -> Principle:
        """Convert database row to Principle object."""
        return Principle(
            id=row["id"],
            category=PrincipleCategory(row["category"]),
            content=row["content"],
            rationale=row["rationale"],
            examples=json.loads(row["examples"]),
            counter_examples=json.loads(row["counter_examples"]),
            keywords=json.loads(row["keywords"]),
            source=PrincipleSource(row["source"]),
            source_id=row["source_id"],
            confidence=row["confidence"],
            priority=row["priority"],
            applications_count=row["applications_count"],
            success_count=row["success_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            active=bool(row["active"]),
        )
    
    # ─────────────────────────────────────────────────────────────
    # Applications
    # ─────────────────────────────────────────────────────────────
    
    def save_application(self, application: PrincipleApplication) -> int:
        """Save a principle application record."""
        cursor = self.conn.execute("""
            INSERT INTO applications 
            (principle_id, situation, how_applied, decision_made,
             outcome, outcome_notes, applied_at, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            application.principle_id,
            application.situation,
            application.how_applied,
            application.decision_made,
            application.outcome.value,
            application.outcome_notes,
            application.applied_at.isoformat(),
            application.evaluated_at.isoformat() if application.evaluated_at else None,
        ))
        self.conn.commit()
        
        # Update principle application count
        self.conn.execute("""
            UPDATE principles 
            SET applications_count = applications_count + 1,
                updated_at = ?
            WHERE id = ?
        """, (datetime.utcnow().isoformat(), application.principle_id))
        self.conn.commit()
        
        # Emit to Atlas OS Event Bus (for training data capture)
        _emit_judgment_to_bus(
            situation=application.situation,
            principles=[application.principle_id],
            reasoning=application.how_applied,
            decision=application.decision_made,
            outcome=application.outcome.value if application.outcome != ApplicationOutcome.UNKNOWN else None
        )
        
        return cursor.lastrowid
    
    def update_application_outcome(
        self, 
        application_id: int, 
        outcome: ApplicationOutcome,
        notes: str = ""
    ):
        """Update the outcome of an application."""
        now = datetime.utcnow().isoformat()
        
        # Get the application first
        row = self.conn.execute(
            "SELECT principle_id, outcome FROM applications WHERE id = ?",
            (application_id,)
        ).fetchone()
        
        if not row:
            raise ValueError(f"Application {application_id} not found")
        
        old_outcome = ApplicationOutcome(row["outcome"])
        principle_id = row["principle_id"]
        
        # Update application
        self.conn.execute("""
            UPDATE applications 
            SET outcome = ?, outcome_notes = ?, evaluated_at = ?
            WHERE id = ?
        """, (outcome.value, notes, now, application_id))
        
        # Update principle success count if outcome changed to success
        if outcome == ApplicationOutcome.SUCCESS and old_outcome != ApplicationOutcome.SUCCESS:
            self.conn.execute("""
                UPDATE principles 
                SET success_count = success_count + 1, updated_at = ?
                WHERE id = ?
            """, (now, principle_id))
        elif old_outcome == ApplicationOutcome.SUCCESS and outcome != ApplicationOutcome.SUCCESS:
            self.conn.execute("""
                UPDATE principles 
                SET success_count = success_count - 1, updated_at = ?
                WHERE id = ?
            """, (now, principle_id))
        
        self.conn.commit()
    
    def get_applications(
        self, 
        principle_id: Optional[str] = None,
        limit: int = 50
    ) -> List[PrincipleApplication]:
        """Get application records."""
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        
        if principle_id:
            query += " AND principle_id = ?"
            params.append(principle_id)
        
        query += " ORDER BY applied_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_application(row) for row in rows]
    
    def _row_to_application(self, row: sqlite3.Row) -> PrincipleApplication:
        """Convert database row to PrincipleApplication object."""
        return PrincipleApplication(
            id=row["id"],
            principle_id=row["principle_id"],
            situation=row["situation"],
            how_applied=row["how_applied"],
            decision_made=row["decision_made"],
            outcome=ApplicationOutcome(row["outcome"]),
            outcome_notes=row["outcome_notes"],
            applied_at=datetime.fromisoformat(row["applied_at"]),
            evaluated_at=datetime.fromisoformat(row["evaluated_at"]) if row["evaluated_at"] else None,
        )
    
    # ─────────────────────────────────────────────────────────────
    # Calibration
    # ─────────────────────────────────────────────────────────────
    
    def save_calibration(self, record: CalibrationRecord) -> int:
        """Save a calibration record."""
        cursor = self.conn.execute("""
            INSERT INTO calibration 
            (domain, prediction, confidence, actual_outcome, correct, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record.domain,
            record.prediction,
            record.confidence,
            record.actual_outcome,
            1 if record.correct else 0,
            record.recorded_at.isoformat(),
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_calibration_stats(self, domain: Optional[str] = None) -> dict:
        """Get calibration statistics."""
        query = "SELECT confidence, correct FROM calibration WHERE 1=1"
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        rows = self.conn.execute(query, params).fetchall()
        
        if not rows:
            return {"total": 0, "buckets": {}}
        
        # Group by confidence buckets (0-0.2, 0.2-0.4, etc.)
        buckets = {f"{i/10:.1f}-{(i+2)/10:.1f}": {"total": 0, "correct": 0} 
                   for i in range(0, 10, 2)}
        
        for row in rows:
            conf = row["confidence"]
            bucket_key = f"{int(conf * 5) * 2 / 10:.1f}-{(int(conf * 5) * 2 + 2) / 10:.1f}"
            if bucket_key in buckets:
                buckets[bucket_key]["total"] += 1
                if row["correct"]:
                    buckets[bucket_key]["correct"] += 1
        
        # Calculate accuracy per bucket
        for bucket in buckets.values():
            if bucket["total"] > 0:
                bucket["accuracy"] = bucket["correct"] / bucket["total"]
            else:
                bucket["accuracy"] = None
        
        return {
            "total": len(rows),
            "overall_accuracy": sum(r["correct"] for r in rows) / len(rows),
            "buckets": buckets
        }
    
    # ─────────────────────────────────────────────────────────────
    # Stats
    # ─────────────────────────────────────────────────────────────
    
    def get_stats(self) -> dict:
        """Get overall judgment layer statistics."""
        principles = self.list_principles(active_only=False)
        active_principles = [p for p in principles if p.active]
        
        apps_row = self.conn.execute(
            "SELECT COUNT(*) as count FROM applications"
        ).fetchone()
        
        cal_row = self.conn.execute(
            "SELECT COUNT(*) as count FROM calibration"
        ).fetchone()
        
        return {
            "principles": {
                "total": len(principles),
                "active": len(active_principles),
                "by_category": {
                    cat.value: len([p for p in active_principles if p.category == cat])
                    for cat in PrincipleCategory
                }
            },
            "applications": apps_row["count"],
            "calibration_records": cal_row["count"],
        }
