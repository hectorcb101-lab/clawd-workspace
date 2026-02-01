"""
Data models for Atlas Self-Modification System.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class Source(Enum):
    INSIGHT = "insight"
    CORRECTION = "correction"
    PATTERN = "pattern"
    MANUAL = "manual"


class ModificationType(Enum):
    APPEND = "append"
    EDIT = "edit"
    DELETE = "delete"
    RESTRUCTURE = "restructure"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"
    EXPIRED = "expired"


class AppliedBy(Enum):
    AUTO = "auto"
    HUMAN = "human"


class TriggerType(Enum):
    CORRECTION_TYPE = "correction_type"
    INSIGHT_TYPE = "insight_type"
    PATTERN = "pattern"
    KEYWORD = "keyword"


class OutcomeType(Enum):
    ERROR_COUNT = "error_count"
    USER_FEEDBACK = "user_feedback"
    SELF_ASSESSMENT = "self_assessment"


def generate_modification_id() -> str:
    """Generate a unique modification ID."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    # Get next sequence number for today
    from .database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM modification_requests WHERE id LIKE ?",
        (f"MOD-{date_str}-%",)
    )
    count = cursor.fetchone()[0] + 1
    conn.close()
    
    return f"MOD-{date_str}-{count:03d}"


def generate_rule_id() -> str:
    """Generate a unique rule ID."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    from .database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM modification_rules WHERE id LIKE ?",
        (f"RULE-{date_str}-%",)
    )
    count = cursor.fetchone()[0] + 1
    conn.close()
    
    return f"RULE-{date_str}-{count:03d}"


@dataclass
class ModificationRequest:
    """A proposed modification to a file."""
    
    target_file: str
    modification_type: ModificationType
    content: str
    reason: str
    source: Source = Source.MANUAL
    source_id: Optional[str] = None
    target_section: Optional[str] = None
    evidence: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_score: int = 0
    confidence: float = 0.5
    status: Status = Status.PENDING
    requires_approval: bool = True
    id: str = field(default_factory=generate_modification_id)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
    applied_by: Optional[AppliedBy] = None
    rejected_reason: Optional[str] = None
    effectiveness_score: Optional[float] = None
    evaluation_deadline: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        d = {
            'id': self.id,
            'source': self.source.value,
            'source_id': self.source_id,
            'target_file': self.target_file,
            'target_section': self.target_section,
            'modification_type': self.modification_type.value,
            'content': self.content,
            'reason': self.reason,
            'evidence': self.evidence,
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'confidence': self.confidence,
            'status': self.status.value,
            'requires_approval': 1 if self.requires_approval else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'applied_by': self.applied_by.value if self.applied_by else None,
            'rejected_reason': self.rejected_reason,
            'effectiveness_score': self.effectiveness_score,
            'evaluation_deadline': self.evaluation_deadline.isoformat() if self.evaluation_deadline else None,
        }
        return d
    
    @classmethod
    def from_row(cls, row: dict) -> 'ModificationRequest':
        """Create from database row."""
        return cls(
            id=row['id'],
            source=Source(row['source']),
            source_id=row['source_id'],
            target_file=row['target_file'],
            target_section=row['target_section'],
            modification_type=ModificationType(row['modification_type']),
            content=row['content'],
            reason=row['reason'],
            evidence=row['evidence'],
            risk_level=RiskLevel(row['risk_level']),
            risk_score=row['risk_score'],
            confidence=row['confidence'],
            status=Status(row['status']),
            requires_approval=bool(row['requires_approval']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            applied_at=datetime.fromisoformat(row['applied_at']) if row['applied_at'] else None,
            applied_by=AppliedBy(row['applied_by']) if row['applied_by'] else None,
            rejected_reason=row['rejected_reason'],
            effectiveness_score=row['effectiveness_score'],
            evaluation_deadline=datetime.fromisoformat(row['evaluation_deadline']) if row['evaluation_deadline'] else None,
        )


@dataclass
class ModificationLog:
    """Record of an applied modification with diff."""
    
    modification_id: str
    file_path: str
    before_content: str
    after_content: str
    diff: str
    applied_at: datetime = field(default_factory=datetime.now)
    git_commit_hash: Optional[str] = None
    reverted_at: Optional[datetime] = None
    revert_reason: Optional[str] = None
    id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'modification_id': self.modification_id,
            'file_path': self.file_path,
            'before_content': self.before_content,
            'after_content': self.after_content,
            'diff': self.diff,
            'git_commit_hash': self.git_commit_hash,
            'applied_at': self.applied_at.isoformat(),
            'reverted_at': self.reverted_at.isoformat() if self.reverted_at else None,
            'revert_reason': self.revert_reason,
        }
    
    @classmethod
    def from_row(cls, row: dict) -> 'ModificationLog':
        """Create from database row."""
        return cls(
            id=row['id'],
            modification_id=row['modification_id'],
            file_path=row['file_path'],
            before_content=row['before_content'],
            after_content=row['after_content'],
            diff=row['diff'],
            git_commit_hash=row['git_commit_hash'],
            applied_at=datetime.fromisoformat(row['applied_at']),
            reverted_at=datetime.fromisoformat(row['reverted_at']) if row['reverted_at'] else None,
            revert_reason=row['revert_reason'],
        )


@dataclass
class ModificationRule:
    """Rule for auto-proposing modifications."""
    
    name: str
    trigger_type: TriggerType
    trigger_match: str
    target_file: str
    action_template: str
    description: Optional[str] = None
    target_section: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    auto_apply: bool = False
    active: bool = True
    id: str = field(default_factory=generate_rule_id)
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'trigger_type': self.trigger_type.value,
            'trigger_match': self.trigger_match,
            'target_file': self.target_file,
            'target_section': self.target_section,
            'action_template': self.action_template,
            'risk_level': self.risk_level.value,
            'auto_apply': 1 if self.auto_apply else 0,
            'active': 1 if self.active else 0,
            'created_at': self.created_at.isoformat(),
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'trigger_count': self.trigger_count,
        }
    
    @classmethod
    def from_row(cls, row: dict) -> 'ModificationRule':
        """Create from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            trigger_type=TriggerType(row['trigger_type']),
            trigger_match=row['trigger_match'],
            target_file=row['target_file'],
            target_section=row['target_section'],
            action_template=row['action_template'],
            risk_level=RiskLevel(row['risk_level']),
            auto_apply=bool(row['auto_apply']),
            active=bool(row['active']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_triggered_at=datetime.fromisoformat(row['last_triggered_at']) if row['last_triggered_at'] else None,
            trigger_count=row['trigger_count'],
        )


@dataclass
class ModificationOutcome:
    """Tracks whether a modification was effective."""
    
    modification_id: str
    outcome_type: OutcomeType
    metric_name: str
    measurement_date: datetime = field(default_factory=datetime.now)
    before_value: Optional[float] = None
    after_value: Optional[float] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'modification_id': self.modification_id,
            'outcome_type': self.outcome_type.value,
            'metric_name': self.metric_name,
            'before_value': self.before_value,
            'after_value': self.after_value,
            'measurement_date': self.measurement_date.isoformat(),
            'notes': self.notes,
        }
    
    @classmethod
    def from_row(cls, row: dict) -> 'ModificationOutcome':
        """Create from database row."""
        return cls(
            id=row['id'],
            modification_id=row['modification_id'],
            outcome_type=OutcomeType(row['outcome_type']),
            metric_name=row['metric_name'],
            before_value=row['before_value'],
            after_value=row['after_value'],
            measurement_date=datetime.fromisoformat(row['measurement_date']),
            notes=row['notes'],
        )
