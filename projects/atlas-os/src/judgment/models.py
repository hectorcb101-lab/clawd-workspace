"""
Data models for the Judgment Layer.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PrincipleCategory(Enum):
    DECISION = "decision"           # How to choose actions
    METACOGNITIVE = "metacognitive" # How to think about thinking
    PRIORITY = "priority"           # What matters most when
    ESCALATION = "escalation"       # When to act vs. ask


class PrincipleSource(Enum):
    SEED = "seed"               # Initial principles from design
    CORRECTION = "correction"   # Derived from user correction
    INSIGHT = "insight"         # Derived from self-awareness insight
    REFLECTION = "reflection"   # From periodic self-reflection
    MANUAL = "manual"           # Manually added


class ApplicationOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    UNKNOWN = "unknown"


@dataclass
class Principle:
    """A judgment principle that guides decision-making."""
    id: str                                    # PRINC-NNN
    category: PrincipleCategory
    content: str                               # The principle itself
    rationale: str                             # Why this principle exists
    examples: List[str] = field(default_factory=list)
    counter_examples: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)  # For retrieval
    source: PrincipleSource = PrincipleSource.MANUAL
    source_id: Optional[str] = None            # Link to originating event
    confidence: float = 0.5                    # How proven (0.0-1.0)
    priority: int = 5                          # For conflict resolution (1-10)
    applications_count: int = 0
    success_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    
    @property
    def effectiveness(self) -> Optional[float]:
        """Success rate if enough applications."""
        if self.applications_count < 3:
            return None
        return self.success_count / self.applications_count
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "content": self.content,
            "rationale": self.rationale,
            "examples": self.examples,
            "counter_examples": self.counter_examples,
            "keywords": self.keywords,
            "source": self.source.value,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "priority": self.priority,
            "applications_count": self.applications_count,
            "success_count": self.success_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "active": self.active,
        }


@dataclass
class PrincipleApplication:
    """Record of applying a principle to a situation."""
    id: Optional[int]
    principle_id: str
    situation: str                             # What was I facing?
    how_applied: str                           # What did the principle suggest?
    decision_made: str                         # What did I actually do?
    outcome: ApplicationOutcome = ApplicationOutcome.UNKNOWN
    outcome_notes: str = ""
    applied_at: datetime = field(default_factory=datetime.utcnow)
    evaluated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "principle_id": self.principle_id,
            "situation": self.situation,
            "how_applied": self.how_applied,
            "decision_made": self.decision_made,
            "outcome": self.outcome.value,
            "outcome_notes": self.outcome_notes,
            "applied_at": self.applied_at.isoformat(),
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
        }


@dataclass
class CalibrationRecord:
    """Track predictions vs. outcomes for confidence calibration."""
    id: Optional[int]
    domain: str                                # research, coding, planning, etc.
    prediction: str                            # What I predicted
    confidence: float                          # How confident I was (0.0-1.0)
    actual_outcome: str                        # What actually happened
    correct: bool
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "actual_outcome": self.actual_outcome,
            "correct": self.correct,
            "recorded_at": self.recorded_at.isoformat(),
        }
