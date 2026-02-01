"""
Atlas Self-Awareness System - Event Logger

Functions for logging outcomes and corrections to the database.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from .database import db_session, init_database, get_stats
from .models import (
    OutcomeEvent, CorrectionEvent, Outcome, FeedbackSource,
    CorrectionType, Severity
)
from .classifier import classify_task


def log_outcome(
    task_type: str,
    outcome: str,
    confidence: float = 0.5,
    feedback_source: str = "self",
    task_subtype: Optional[str] = None,
    event_id: Optional[str] = None,
    notes: Optional[str] = None,
    context: Optional[str] = None,
    auto_classify: bool = False
) -> int:
    """
    Log a task outcome.
    
    Args:
        task_type: Category of task (coding, research, etc.)
        outcome: Result (success, failure, partial, unknown)
        confidence: How confident in this classification (0.0-1.0)
        feedback_source: Who determined outcome (self, user, system)
        task_subtype: More specific category
        event_id: Link to memory system event
        notes: Additional notes about what happened
        context: Context about the task
        auto_classify: If True, attempt to classify task_type from notes/context
    
    Returns:
        ID of the logged outcome
    """
    # Auto-classify if requested and task_type is generic
    if auto_classify and task_type in ("unknown", "task") and (notes or context):
        classified_type, classified_subtype, _ = classify_task(notes or "", context)
        if classified_type != "unknown":
            task_type = classified_type
            if classified_subtype and not task_subtype:
                task_subtype = classified_subtype
    
    event = OutcomeEvent(
        task_type=task_type,
        outcome=Outcome(outcome),
        confidence=confidence,
        feedback_source=FeedbackSource(feedback_source),
        task_subtype=task_subtype,
        event_id=event_id,
        notes=notes,
        context=context
    )
    
    with db_session() as conn:
        cursor = conn.execute("""
            INSERT INTO outcomes (event_id, outcome, task_type, task_subtype, 
                                 confidence, feedback_source, notes, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.outcome.value,
            event.task_type,
            event.task_subtype,
            event.confidence,
            event.feedback_source.value,
            event.notes,
            event.context
        ))
        return cursor.lastrowid


def log_correction(
    user_signal: str,
    correction_type: str,
    severity: str = "moderate",
    original_event_id: Optional[str] = None,
    lesson: Optional[str] = None,
    task_type: Optional[str] = None,
    auto_classify: bool = False
) -> int:
    """
    Log a correction (when Finn corrects me).
    
    Args:
        user_signal: What Finn said (the correction)
        correction_type: Type of correction (factual, approach, style, other)
        severity: How significant (minor, moderate, major)
        original_event_id: Link to the original event that was corrected
        lesson: What I learned from this
        task_type: Category of task being corrected
        auto_classify: If True, attempt to classify task_type from user_signal
    
    Returns:
        ID of the logged correction
    """
    # Auto-classify if requested
    if auto_classify and not task_type:
        classified_type, _, _ = classify_task(user_signal)
        if classified_type != "unknown":
            task_type = classified_type
    
    event = CorrectionEvent(
        user_signal=user_signal,
        correction_type=CorrectionType(correction_type),
        severity=Severity(severity),
        original_event_id=original_event_id,
        lesson=lesson,
        task_type=task_type
    )
    
    with db_session() as conn:
        cursor = conn.execute("""
            INSERT INTO corrections (original_event_id, correction_type, severity,
                                    user_signal, lesson, task_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.original_event_id,
            event.correction_type.value,
            event.severity.value,
            event.user_signal,
            event.lesson,
            event.task_type
        ))
        return cursor.lastrowid


def get_recent_outcomes(limit: int = 10, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent outcomes, optionally filtered by task type."""
    with db_session() as conn:
        if task_type:
            rows = conn.execute("""
                SELECT * FROM outcomes 
                WHERE task_type = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (task_type, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM outcomes 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)).fetchall()
        
        return [dict(row) for row in rows]


def get_recent_corrections(limit: int = 10, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get recent corrections, optionally filtered by task type."""
    with db_session() as conn:
        if task_type:
            rows = conn.execute("""
                SELECT * FROM corrections 
                WHERE task_type = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (task_type, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM corrections 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)).fetchall()
        
        return [dict(row) for row in rows]


def get_outcome_summary(days: int = 7) -> Dict[str, Any]:
    """Get summary of outcomes over the past N days."""
    with db_session() as conn:
        # Overall counts
        overall = conn.execute("""
            SELECT 
                outcome,
                COUNT(*) as count
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY outcome
        """, (f'-{days} days',)).fetchall()
        
        # By task type
        by_type = conn.execute("""
            SELECT 
                task_type,
                outcome,
                COUNT(*) as count
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type, outcome
            ORDER BY task_type, outcome
        """, (f'-{days} days',)).fetchall()
        
        # Build summary
        summary = {
            'period_days': days,
            'overall': {row['outcome']: row['count'] for row in overall},
            'by_task_type': {}
        }
        
        for row in by_type:
            task = row['task_type']
            if task not in summary['by_task_type']:
                summary['by_task_type'][task] = {}
            summary['by_task_type'][task][row['outcome']] = row['count']
        
        # Calculate success rate
        total = sum(summary['overall'].values())
        successes = summary['overall'].get('success', 0)
        partials = summary['overall'].get('partial', 0)
        if total > 0:
            summary['success_rate'] = (successes + (partials * 0.5)) / total
        else:
            summary['success_rate'] = None
        
        return summary


def get_correction_summary(days: int = 7) -> Dict[str, Any]:
    """Get summary of corrections over the past N days."""
    with db_session() as conn:
        # By type
        by_type = conn.execute("""
            SELECT 
                correction_type,
                COUNT(*) as count
            FROM corrections
            WHERE created_at >= datetime('now', ?)
            GROUP BY correction_type
        """, (f'-{days} days',)).fetchall()
        
        # By severity
        by_severity = conn.execute("""
            SELECT 
                severity,
                COUNT(*) as count
            FROM corrections
            WHERE created_at >= datetime('now', ?)
            GROUP BY severity
        """, (f'-{days} days',)).fetchall()
        
        # By task type
        by_task = conn.execute("""
            SELECT 
                COALESCE(task_type, 'unclassified') as task_type,
                COUNT(*) as count
            FROM corrections
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
        """, (f'-{days} days',)).fetchall()
        
        return {
            'period_days': days,
            'by_type': {row['correction_type']: row['count'] for row in by_type},
            'by_severity': {row['severity']: row['count'] for row in by_severity},
            'by_task_type': {row['task_type']: row['count'] for row in by_task},
            'total': sum(row['count'] for row in by_type)
        }
