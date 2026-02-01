"""
Repository layer for Atlas Self-Modification System.
Handles all database operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from .database import get_connection, init_database
from .models import (
    ModificationRequest, ModificationLog, ModificationRule, ModificationOutcome,
    Status, RiskLevel, Source, ModificationType, TriggerType, OutcomeType
)


class ModificationRepository:
    """Repository for modification requests."""
    
    def __init__(self):
        init_database()
    
    def save(self, modification: ModificationRequest) -> str:
        """Save a modification request."""
        conn = get_connection()
        cursor = conn.cursor()
        
        d = modification.to_dict()
        
        cursor.execute("""
            INSERT OR REPLACE INTO modification_requests (
                id, source, source_id, target_file, target_section,
                modification_type, content, reason, evidence,
                risk_level, risk_score, confidence, status, requires_approval,
                created_at, updated_at, applied_at, applied_by,
                rejected_reason, effectiveness_score, evaluation_deadline
            ) VALUES (
                :id, :source, :source_id, :target_file, :target_section,
                :modification_type, :content, :reason, :evidence,
                :risk_level, :risk_score, :confidence, :status, :requires_approval,
                :created_at, :updated_at, :applied_at, :applied_by,
                :rejected_reason, :effectiveness_score, :evaluation_deadline
            )
        """, d)
        
        conn.commit()
        conn.close()
        
        return modification.id
    
    def get(self, modification_id: str) -> Optional[ModificationRequest]:
        """Get a modification by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_requests WHERE id = ?",
            (modification_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ModificationRequest.from_row(dict(row))
        return None
    
    def list_by_status(self, status: Optional[Status] = None, limit: int = 50) -> List[ModificationRequest]:
        """List modifications, optionally filtered by status."""
        conn = get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM modification_requests WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status.value, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM modification_requests ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationRequest.from_row(dict(row)) for row in rows]
    
    def list_pending(self, limit: int = 50) -> List[ModificationRequest]:
        """List pending modifications."""
        return self.list_by_status(Status.PENDING, limit)
    
    def list_by_file(self, file_path: str, limit: int = 50) -> List[ModificationRequest]:
        """List modifications for a specific file."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_requests WHERE target_file = ? ORDER BY created_at DESC LIMIT ?",
            (file_path, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationRequest.from_row(dict(row)) for row in rows]
    
    def update_status(self, modification_id: str, status: Status, **kwargs) -> bool:
        """Update modification status with optional fields."""
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = ['status = ?', 'updated_at = ?']
        values = [status.value, datetime.now().isoformat()]
        
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f'{key} = ?')
                if hasattr(value, 'isoformat'):
                    values.append(value.isoformat())
                elif hasattr(value, 'value'):
                    values.append(value.value)
                else:
                    values.append(value)
        
        values.append(modification_id)
        
        cursor.execute(
            f"UPDATE modification_requests SET {', '.join(updates)} WHERE id = ?",
            values
        )
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def expire_stale(self, days: int = 14) -> int:
        """Expire modifications pending for too long."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            UPDATE modification_requests 
            SET status = 'expired', updated_at = ?
            WHERE status = 'pending' AND created_at < ?
        """, (datetime.now().isoformat(), cutoff))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected


class LogRepository:
    """Repository for modification logs."""
    
    def __init__(self):
        init_database()
    
    def save(self, log: ModificationLog) -> int:
        """Save a modification log."""
        conn = get_connection()
        cursor = conn.cursor()
        
        d = log.to_dict()
        
        cursor.execute("""
            INSERT INTO modification_logs (
                modification_id, file_path, before_content, after_content,
                diff, git_commit_hash, applied_at, reverted_at, revert_reason
            ) VALUES (
                :modification_id, :file_path, :before_content, :after_content,
                :diff, :git_commit_hash, :applied_at, :reverted_at, :revert_reason
            )
        """, d)
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_by_modification(self, modification_id: str) -> Optional[ModificationLog]:
        """Get log for a modification."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_logs WHERE modification_id = ? ORDER BY applied_at DESC LIMIT 1",
            (modification_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ModificationLog.from_row(dict(row))
        return None
    
    def list_for_file(self, file_path: str, limit: int = 20) -> List[ModificationLog]:
        """List logs for a specific file."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_logs WHERE file_path = ? ORDER BY applied_at DESC LIMIT ?",
            (file_path, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationLog.from_row(dict(row)) for row in rows]
    
    def list_active(self, limit: int = 50) -> List[ModificationLog]:
        """List active (not reverted) logs."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_logs WHERE reverted_at IS NULL ORDER BY applied_at DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationLog.from_row(dict(row)) for row in rows]
    
    def mark_reverted(self, modification_id: str, reason: str) -> bool:
        """Mark a log as reverted."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE modification_logs 
            SET reverted_at = ?, revert_reason = ?
            WHERE modification_id = ? AND reverted_at IS NULL
        """, (datetime.now().isoformat(), reason, modification_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0


class RuleRepository:
    """Repository for modification rules."""
    
    def __init__(self):
        init_database()
    
    def save(self, rule: ModificationRule) -> str:
        """Save a modification rule."""
        conn = get_connection()
        cursor = conn.cursor()
        
        d = rule.to_dict()
        
        cursor.execute("""
            INSERT OR REPLACE INTO modification_rules (
                id, name, description, trigger_type, trigger_match,
                target_file, target_section, action_template,
                risk_level, auto_apply, active, created_at,
                last_triggered_at, trigger_count
            ) VALUES (
                :id, :name, :description, :trigger_type, :trigger_match,
                :target_file, :target_section, :action_template,
                :risk_level, :auto_apply, :active, :created_at,
                :last_triggered_at, :trigger_count
            )
        """, d)
        
        conn.commit()
        conn.close()
        
        return rule.id
    
    def get(self, rule_id: str) -> Optional[ModificationRule]:
        """Get a rule by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM modification_rules WHERE id = ?", (rule_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ModificationRule.from_row(dict(row))
        return None
    
    def list_active(self) -> List[ModificationRule]:
        """List active rules."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM modification_rules WHERE active = 1 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationRule.from_row(dict(row)) for row in rows]
    
    def find_matching(self, trigger_type: TriggerType, value: str) -> List[ModificationRule]:
        """Find rules matching a trigger."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM modification_rules 
            WHERE active = 1 AND trigger_type = ? AND ? LIKE '%' || trigger_match || '%'
        """, (trigger_type.value, value))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationRule.from_row(dict(row)) for row in rows]
    
    def record_trigger(self, rule_id: str) -> None:
        """Record that a rule was triggered."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE modification_rules 
            SET last_triggered_at = ?, trigger_count = trigger_count + 1
            WHERE id = ?
        """, (datetime.now().isoformat(), rule_id))
        
        conn.commit()
        conn.close()
    
    def set_active(self, rule_id: str, active: bool) -> bool:
        """Enable or disable a rule."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE modification_rules SET active = ? WHERE id = ?",
            (1 if active else 0, rule_id)
        )
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0


class OutcomeRepository:
    """Repository for modification outcomes."""
    
    def __init__(self):
        init_database()
    
    def save(self, outcome: ModificationOutcome) -> int:
        """Save an outcome record."""
        conn = get_connection()
        cursor = conn.cursor()
        
        d = outcome.to_dict()
        
        cursor.execute("""
            INSERT INTO modification_outcomes (
                modification_id, outcome_type, metric_name,
                before_value, after_value, measurement_date, notes
            ) VALUES (
                :modification_id, :outcome_type, :metric_name,
                :before_value, :after_value, :measurement_date, :notes
            )
        """, d)
        
        outcome_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return outcome_id
    
    def list_for_modification(self, modification_id: str) -> List[ModificationOutcome]:
        """List outcomes for a modification."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM modification_outcomes WHERE modification_id = ? ORDER BY measurement_date DESC",
            (modification_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ModificationOutcome.from_row(dict(row)) for row in rows]
