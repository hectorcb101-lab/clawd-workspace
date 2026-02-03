"""
Atlas OS Event Schema

Canonical format for all events flowing through the integration bus.
Designed to be both useful now AND training-ready for future fine-tuning.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
import json
import uuid


class EventType(str, Enum):
    # Self-awareness events
    CORRECTION = "correction"
    OUTCOME = "outcome"
    PATTERN = "pattern"
    INSIGHT = "insight"
    
    # Judgment events
    JUDGMENT_CONSULT = "judgment_consult"
    JUDGMENT_APPLY = "judgment_apply"
    JUDGMENT_OUTCOME = "judgment_outcome"
    
    # Modification events
    MOD_PROPOSE = "mod_propose"
    MOD_APPROVE = "mod_approve"
    MOD_APPLY = "mod_apply"
    MOD_ROLLBACK = "mod_rollback"
    
    # Memory events
    MEMORY_FACT = "memory_fact"
    MEMORY_ENTITY = "memory_entity"
    MEMORY_RELATION = "memory_relation"
    
    # Training events
    TRAINING_EXAMPLE = "training_example"
    TRAINING_PREFERENCE = "training_preference"
    
    # Session events
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    MESSAGE = "message"


class EventSource(str, Enum):
    SELF_AWARENESS = "atlas-self"
    JUDGMENT = "atlas-judge"
    MODIFICATION = "atlas-mod"
    MEMORY = "atlas-mem"
    TRAINING = "atlas-train"
    MANUAL = "manual"
    SESSION = "session"


class TrainingFormat(str, Enum):
    SFT = "sft"           # Supervised fine-tuning (instruction-response)
    DPO = "dpo"           # Direct preference optimisation (chosen/rejected)
    REASONING = "reasoning"  # Chain-of-thought / reasoning traces
    NONE = "none"         # Not usable for training


@dataclass
class TrainingMeta:
    """Metadata for training data extraction."""
    usable: bool = False
    format: TrainingFormat = TrainingFormat.NONE
    quality: int = 0  # 1-5 scale, 0 = not assessed
    exported: bool = False
    export_id: Optional[str] = None


@dataclass
class AtlasEvent:
    """
    Canonical event format for Atlas OS.
    
    All systems emit events in this format to the integration bus.
    The bus routes them to subscribers (training capture, memory, etc).
    """
    
    # Identity
    id: str = field(default_factory=lambda: f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Classification
    type: EventType = EventType.MESSAGE
    source: EventSource = EventSource.MANUAL
    
    # Content
    summary: str = ""  # Human-readable summary
    data: dict = field(default_factory=dict)  # Structured data specific to event type
    
    # Context
    session_id: Optional[str] = None
    related_events: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    # Training metadata
    training: TrainingMeta = field(default_factory=TrainingMeta)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialisation."""
        d = asdict(self)
        d['type'] = self.type.value
        d['source'] = self.source.value
        d['training']['format'] = self.training.format.value
        return d
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, d: dict) -> 'AtlasEvent':
        """Create from dictionary."""
        d['type'] = EventType(d['type'])
        d['source'] = EventSource(d['source'])
        if 'training' in d:
            d['training']['format'] = TrainingFormat(d['training']['format'])
            d['training'] = TrainingMeta(**d['training'])
        return cls(**d)
    
    @classmethod
    def from_json(cls, s: str) -> 'AtlasEvent':
        """Create from JSON string."""
        return cls.from_dict(json.loads(s))


# Event factory functions for common event types

def correction_event(
    context: str,
    rejected: str,
    chosen: str,
    explanation: str = "",
    category: str = "other",
    severity: str = "moderate"
) -> AtlasEvent:
    """Create a correction event (preference pair)."""
    return AtlasEvent(
        type=EventType.CORRECTION,
        source=EventSource.SELF_AWARENESS,
        summary=f"Correction: {explanation[:100]}..." if len(explanation) > 100 else f"Correction: {explanation}",
        data={
            "context": context,
            "rejected": rejected,
            "chosen": chosen,
            "explanation": explanation,
            "category": category,
            "severity": severity
        },
        training=TrainingMeta(
            usable=True,
            format=TrainingFormat.DPO,
            quality=4 if severity == "major" else 3
        )
    )


def outcome_event(
    task: str,
    result: Literal["success", "partial", "failure"],
    approach: str = "",
    feedback: str = "",
    learnings: str = ""
) -> AtlasEvent:
    """Create an outcome event."""
    return AtlasEvent(
        type=EventType.OUTCOME,
        source=EventSource.SELF_AWARENESS,
        summary=f"Outcome ({result}): {task[:80]}...",
        data={
            "task": task,
            "result": result,
            "approach": approach,
            "feedback": feedback,
            "learnings": learnings
        },
        training=TrainingMeta(
            usable=result == "success",
            format=TrainingFormat.SFT if result == "success" else TrainingFormat.NONE,
            quality=4 if result == "success" else 0
        )
    )


def judgment_event(
    situation: str,
    principles: list[str],
    reasoning: str,
    decision: str,
    outcome: Optional[str] = None
) -> AtlasEvent:
    """Create a judgment application event."""
    return AtlasEvent(
        type=EventType.JUDGMENT_APPLY,
        source=EventSource.JUDGMENT,
        summary=f"Judgment: {decision[:80]}...",
        data={
            "situation": situation,
            "principles_consulted": principles,
            "reasoning": reasoning,
            "decision": decision,
            "outcome": outcome
        },
        training=TrainingMeta(
            usable=True,
            format=TrainingFormat.REASONING,
            quality=4
        )
    )


def instruction_event(
    instruction: str,
    response: str,
    system: str = "",
    quality: int = 4,
    tags: list[str] = None
) -> AtlasEvent:
    """Create an instruction-response pair event (SFT example)."""
    return AtlasEvent(
        type=EventType.TRAINING_EXAMPLE,
        source=EventSource.TRAINING,
        summary=f"SFT: {instruction[:80]}...",
        data={
            "system": system,
            "instruction": instruction,
            "response": response
        },
        tags=tags or [],
        training=TrainingMeta(
            usable=True,
            format=TrainingFormat.SFT,
            quality=quality
        )
    )


if __name__ == "__main__":
    # Test event creation
    evt = correction_event(
        context="User asked for weather",
        rejected="I don't have access to weather data",
        chosen="Let me check the weather for you",
        explanation="Atlas should be proactive about using available tools",
        category="process",
        severity="moderate"
    )
    print("Sample correction event:")
    print(json.dumps(evt.to_dict(), indent=2))
