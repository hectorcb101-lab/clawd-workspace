"""
Atlas Self-Awareness System - Data Models

Dataclasses for outcomes, corrections, patterns, and insights.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum


class Outcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class FeedbackSource(Enum):
    SELF = "self"      # I determined the outcome
    USER = "user"      # Finn told me
    SYSTEM = "system"  # Tool/system feedback


class CorrectionType(Enum):
    FACTUAL = "factual"    # Wrong information
    APPROACH = "approach"  # Wrong method/strategy
    STYLE = "style"        # Tone, format, presentation
    OTHER = "other"


class Severity(Enum):
    MINOR = "minor"      # Small issue, easily fixed
    MODERATE = "moderate" # Notable mistake
    MAJOR = "major"      # Significant failure


class PatternType(Enum):
    FAILURE = "failure"
    STRENGTH = "strength"


class PatternStatus(Enum):
    ACTIVE = "active"       # Still happening
    RESOLVED = "resolved"   # Fixed
    MONITORING = "monitoring"  # Watching


class InsightType(Enum):
    BLIND_SPOT = "blind_spot"   # Something I'm missing
    IMPROVEMENT = "improvement"  # Getting better at something
    REGRESSION = "regression"    # Getting worse
    TIP = "tip"                 # Helpful suggestion
    WARNING = "warning"         # About to repeat a mistake


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OutcomeEvent:
    """Record of a task outcome."""
    task_type: str
    outcome: Outcome
    confidence: float = 0.5
    feedback_source: FeedbackSource = FeedbackSource.SELF
    task_subtype: Optional[str] = None
    event_id: Optional[str] = None
    notes: Optional[str] = None
    context: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        # Convert string values to enums if needed
        if isinstance(self.outcome, str):
            self.outcome = Outcome(self.outcome)
        if isinstance(self.feedback_source, str):
            self.feedback_source = FeedbackSource(self.feedback_source)
        # Clamp confidence
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            'event_id': self.event_id,
            'outcome': self.outcome.value,
            'task_type': self.task_type,
            'task_subtype': self.task_subtype,
            'confidence': self.confidence,
            'feedback_source': self.feedback_source.value,
            'notes': self.notes,
            'context': self.context,
        }


@dataclass
class CorrectionEvent:
    """Record of when Finn corrected me."""
    user_signal: str
    correction_type: CorrectionType
    severity: Severity = Severity.MODERATE
    original_event_id: Optional[str] = None
    lesson: Optional[str] = None
    task_type: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.correction_type, str):
            self.correction_type = CorrectionType(self.correction_type)
        if isinstance(self.severity, str):
            self.severity = Severity(self.severity)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion."""
        return {
            'original_event_id': self.original_event_id,
            'correction_type': self.correction_type.value,
            'severity': self.severity.value,
            'user_signal': self.user_signal,
            'lesson': self.lesson,
            'task_type': self.task_type,
        }


@dataclass
class Pattern:
    """An identified recurring pattern (failure or strength)."""
    pattern_type: PatternType
    description: str
    task_types: List[str] = field(default_factory=list)
    occurrence_count: int = 1
    status: PatternStatus = PatternStatus.ACTIVE
    confidence: float = 0.5
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.pattern_type, str):
            self.pattern_type = PatternType(self.pattern_type)
        if isinstance(self.status, str):
            self.status = PatternStatus(self.status)
        if not self.first_seen:
            self.first_seen = datetime.utcnow().isoformat()
        if not self.last_seen:
            self.last_seen = self.first_seen


@dataclass
class Insight:
    """A generated insight to surface."""
    insight_type: InsightType
    message: str
    priority: Priority = Priority.MEDIUM
    evidence: Optional[str] = None
    actionable: bool = True
    suggested_action: Optional[str] = None
    surfaced: bool = False
    surfaced_at: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.insight_type, str):
            self.insight_type = InsightType(self.insight_type)
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)
