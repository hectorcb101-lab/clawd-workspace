"""
Integration with Atlas Self-Awareness System.

Connects insights and corrections to modification proposals.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .models import (
    ModificationRequest, ModificationRule, ModificationType, Source, RiskLevel,
    TriggerType, generate_modification_id
)
from .service import get_service
from .repository import RuleRepository

# Self-awareness database
AWARENESS_DB = Path.home() / "clawd" / "projects" / "atlas-self-awareness" / "data" / "self_awareness.db"


class CorrectionType(Enum):
    """Mirror of self-awareness CorrectionType."""
    FACTUAL = "factual"
    APPROACH = "approach"
    STYLE = "style"
    OTHER = "other"


class InsightType(Enum):
    """Mirror of self-awareness InsightType."""
    BLIND_SPOT = "blind_spot"
    IMPROVEMENT = "improvement"
    REGRESSION = "regression"
    TIP = "tip"
    WARNING = "warning"


class Priority(Enum):
    """Mirror of self-awareness Priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Correction:
    """Correction from self-awareness system."""
    id: int
    user_signal: str
    correction_type: CorrectionType
    severity: str
    lesson: Optional[str]
    task_type: Optional[str]
    created_at: str


@dataclass
class Insight:
    """Insight from self-awareness system."""
    id: int
    insight_type: InsightType
    message: str
    priority: Priority
    evidence: Optional[str]
    suggested_action: Optional[str]
    surfaced: bool
    created_at: str


# Template mappings for different correction types
CORRECTION_TEMPLATES = {
    CorrectionType.STYLE: {
        'target_file': 'AGENTS.md',
        'target_section': 'Communication Preferences',
        'template': """**Added {date} from correction:**
> "{signal}"

Rule: {lesson}
""",
    },
    CorrectionType.APPROACH: {
        'target_file': 'AGENTS.md', 
        'target_section': None,  # Determined by task_type
        'template': """**Updated {date} from correction:**
Lesson learned: {lesson}

Context: {signal}
""",
    },
    CorrectionType.FACTUAL: {
        'target_file': 'TOOLS.md',
        'target_section': None,
        'template': """**Corrected {date}:**
{lesson}

(Was: {signal})
""",
    },
    CorrectionType.OTHER: {
        'target_file': 'AGENTS.md',
        'target_section': None,
        'template': """**Note {date}:**
{lesson}

Context: {signal}
""",
    },
}

# Template mappings for different insight types
INSIGHT_TEMPLATES = {
    InsightType.BLIND_SPOT: {
        'target_file': 'AGENTS.md',
        'target_section': 'Known Issues',
        'template': """**Added {date} from blind spot detection:**
{message}

Evidence: {evidence}

Suggested action: {action}
""",
    },
    InsightType.WARNING: {
        'target_file': 'HEARTBEAT.md',
        'target_section': 'Active Warnings',
        'template': """### ⚠️ Warning ({date})
{message}

Action: {action}
""",
    },
    InsightType.REGRESSION: {
        'target_file': 'AGENTS.md',
        'target_section': 'Known Issues',
        'template': """**Regression detected {date}:**
{message}

Evidence: {evidence}

Mitigation: {action}
""",
    },
    InsightType.TIP: {
        'target_file': 'TOOLS.md',
        'target_section': None,
        'template': """**Tip discovered {date}:**
{message}

{action}
""",
    },
    InsightType.IMPROVEMENT: {
        'target_file': None,  # Don't auto-modify for improvements
        'target_section': None,
        'template': None,
    },
}


def get_awareness_connection() -> Optional[sqlite3.Connection]:
    """Get connection to self-awareness database."""
    if not AWARENESS_DB.exists():
        return None
    conn = sqlite3.connect(str(AWARENESS_DB))
    conn.row_factory = sqlite3.Row
    return conn


def get_unprocessed_corrections(limit: int = 20) -> List[Correction]:
    """Get corrections that haven't been turned into modifications yet."""
    conn = get_awareness_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        # Get corrections not yet linked to a modification
        cursor.execute("""
            SELECT id, user_signal, correction_type, severity, lesson, task_type, created_at
            FROM corrections
            WHERE lesson IS NOT NULL
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [
            Correction(
                id=row['id'],
                user_signal=row['user_signal'],
                correction_type=CorrectionType(row['correction_type']),
                severity=row['severity'],
                lesson=row['lesson'],
                task_type=row['task_type'],
                created_at=row['created_at'],
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_unprocessed_insights(limit: int = 20) -> List[Insight]:
    """Get actionable insights that haven't been surfaced."""
    conn = get_awareness_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, insight_type, message, priority, evidence, suggested_action, surfaced, created_at
            FROM insights
            WHERE actionable = 1
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [
            Insight(
                id=row['id'],
                insight_type=InsightType(row['insight_type']),
                message=row['message'],
                priority=Priority(row['priority']),
                evidence=row['evidence'],
                suggested_action=row['suggested_action'],
                surfaced=bool(row['surfaced']),
                created_at=row['created_at'],
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_correction(correction_id: int) -> Optional[Correction]:
    """Get a specific correction by ID."""
    conn = get_awareness_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_signal, correction_type, severity, lesson, task_type, created_at FROM corrections WHERE id = ?",
            (correction_id,)
        )
        row = cursor.fetchone()
        if row:
            return Correction(
                id=row['id'],
                user_signal=row['user_signal'],
                correction_type=CorrectionType(row['correction_type']),
                severity=row['severity'],
                lesson=row['lesson'],
                task_type=row['task_type'],
                created_at=row['created_at'],
            )
        return None
    finally:
        conn.close()


def get_insight(insight_id: int) -> Optional[Insight]:
    """Get a specific insight by ID."""
    conn = get_awareness_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, insight_type, message, priority, evidence, suggested_action, surfaced, created_at FROM insights WHERE id = ?",
            (insight_id,)
        )
        row = cursor.fetchone()
        if row:
            return Insight(
                id=row['id'],
                insight_type=InsightType(row['insight_type']),
                message=row['message'],
                priority=Priority(row['priority']),
                evidence=row['evidence'],
                suggested_action=row['suggested_action'],
                surfaced=bool(row['surfaced']),
                created_at=row['created_at'],
            )
        return None
    finally:
        conn.close()


def propose_from_correction(correction_id: int) -> Tuple[Optional[ModificationRequest], str]:
    """
    Create a modification proposal from a correction.
    
    Returns:
        (ModificationRequest, message) or (None, error_message)
    """
    correction = get_correction(correction_id)
    if not correction:
        return None, f"Correction not found: {correction_id}"
    
    if not correction.lesson:
        return None, f"Correction {correction_id} has no lesson to apply"
    
    # Get template for this correction type
    template_config = CORRECTION_TEMPLATES.get(correction.correction_type)
    if not template_config:
        return None, f"No template for correction type: {correction.correction_type.value}"
    
    # Generate content from template
    date = datetime.now().strftime("%Y-%m-%d")
    content = template_config['template'].format(
        date=date,
        signal=correction.user_signal[:200],  # Truncate long signals
        lesson=correction.lesson,
    )
    
    # Determine confidence based on severity
    confidence_map = {
        'minor': 0.6,
        'moderate': 0.7,
        'major': 0.85,
    }
    confidence = confidence_map.get(correction.severity, 0.7)
    
    # Create proposal
    svc = get_service()
    mod, explanation = svc.propose(
        target_file=template_config['target_file'],
        modification_type=ModificationType.APPEND,
        content=content,
        reason=f"From correction: {correction.user_signal[:100]}",
        source=Source.CORRECTION,
        source_id=str(correction.id),
        target_section=template_config['target_section'],
        evidence=f"User correction on {correction.created_at}: {correction.user_signal}",
        confidence=confidence,
    )
    
    return mod, f"Proposed {mod.id} from correction {correction_id}"


def propose_from_insight(insight_id: int) -> Tuple[Optional[ModificationRequest], str]:
    """
    Create a modification proposal from an insight.
    
    Returns:
        (ModificationRequest, message) or (None, error_message)
    """
    insight = get_insight(insight_id)
    if not insight:
        return None, f"Insight not found: {insight_id}"
    
    # Get template for this insight type
    template_config = INSIGHT_TEMPLATES.get(insight.insight_type)
    if not template_config or not template_config['target_file']:
        return None, f"Insight type {insight.insight_type.value} doesn't generate modifications"
    
    # Generate content from template
    date = datetime.now().strftime("%Y-%m-%d")
    content = template_config['template'].format(
        date=date,
        message=insight.message,
        evidence=insight.evidence or "N/A",
        action=insight.suggested_action or "Review and address",
    )
    
    # Determine confidence based on priority
    confidence_map = {
        Priority.LOW: 0.5,
        Priority.MEDIUM: 0.65,
        Priority.HIGH: 0.8,
        Priority.CRITICAL: 0.9,
    }
    confidence = confidence_map.get(insight.priority, 0.65)
    
    # Create proposal
    svc = get_service()
    mod, explanation = svc.propose(
        target_file=template_config['target_file'],
        modification_type=ModificationType.APPEND,
        content=content,
        reason=f"From insight: {insight.message[:100]}",
        source=Source.INSIGHT,
        source_id=str(insight.id),
        target_section=template_config['target_section'],
        evidence=insight.evidence or f"Insight generated: {insight.message}",
        confidence=confidence,
    )
    
    return mod, f"Proposed {mod.id} from insight {insight_id}"


def check_rules_for_correction(correction: Correction) -> List[ModificationRequest]:
    """Check if any rules match this correction and generate proposals."""
    rules = RuleRepository()
    matching = rules.find_matching(TriggerType.CORRECTION_TYPE, correction.correction_type.value)
    
    proposals = []
    svc = get_service()
    
    for rule in matching:
        # Apply template
        date = datetime.now().strftime("%Y-%m-%d")
        content = rule.action_template.format(
            date=date,
            signal=correction.user_signal[:200],
            lesson=correction.lesson or "",
            type=correction.correction_type.value,
        )
        
        mod, _ = svc.propose(
            target_file=rule.target_file,
            modification_type=ModificationType.APPEND,
            content=content,
            reason=f"Rule {rule.id} triggered by correction",
            source=Source.PATTERN,
            source_id=rule.id,
            target_section=rule.target_section,
            evidence=f"Rule matched correction type: {correction.correction_type.value}",
            confidence=0.7,
        )
        
        # Record trigger
        rules.record_trigger(rule.id)
        proposals.append(mod)
    
    return proposals


def check_rules_for_insight(insight: Insight) -> List[ModificationRequest]:
    """Check if any rules match this insight and generate proposals."""
    rules = RuleRepository()
    matching = rules.find_matching(TriggerType.INSIGHT_TYPE, insight.insight_type.value)
    
    proposals = []
    svc = get_service()
    
    for rule in matching:
        date = datetime.now().strftime("%Y-%m-%d")
        content = rule.action_template.format(
            date=date,
            message=insight.message,
            evidence=insight.evidence or "",
            action=insight.suggested_action or "",
            priority=insight.priority.value,
        )
        
        mod, _ = svc.propose(
            target_file=rule.target_file,
            modification_type=ModificationType.APPEND,
            content=content,
            reason=f"Rule {rule.id} triggered by insight",
            source=Source.PATTERN,
            source_id=rule.id,
            target_section=rule.target_section,
            evidence=f"Rule matched insight type: {insight.insight_type.value}",
            confidence=0.7,
        )
        
        rules.record_trigger(rule.id)
        proposals.append(mod)
    
    return proposals


def process_pending_corrections(limit: int = 10) -> List[Tuple[int, str]]:
    """Process unprocessed corrections and generate proposals."""
    corrections = get_unprocessed_corrections(limit)
    results = []
    
    for correction in corrections:
        mod, msg = propose_from_correction(correction.id)
        if mod:
            results.append((correction.id, f"✅ {msg}"))
        else:
            results.append((correction.id, f"⚠️ {msg}"))
    
    return results


def process_pending_insights(limit: int = 10) -> List[Tuple[int, str]]:
    """Process unprocessed insights and generate proposals."""
    insights = get_unprocessed_insights(limit)
    results = []
    
    for insight in insights:
        mod, msg = propose_from_insight(insight.id)
        if mod:
            results.append((insight.id, f"✅ {msg}"))
        else:
            results.append((insight.id, f"⏭️ {msg}"))
    
    return results
