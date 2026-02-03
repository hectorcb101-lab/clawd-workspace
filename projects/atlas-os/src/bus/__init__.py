"""
Atlas OS Integration Bus

Central event routing for all Atlas systems.
"""

from .schema import (
    AtlasEvent,
    EventType,
    EventSource,
    TrainingFormat,
    TrainingMeta,
    correction_event,
    outcome_event,
    judgment_event,
    instruction_event,
)

from .router import (
    EventBus,
    get_bus,
    emit,
)

from .validator import (
    validate_event,
    assess_training_quality,
    ValidationError,
)

__all__ = [
    # Schema
    "AtlasEvent",
    "EventType", 
    "EventSource",
    "TrainingFormat",
    "TrainingMeta",
    # Factory functions
    "correction_event",
    "outcome_event",
    "judgment_event",
    "instruction_event",
    # Router
    "EventBus",
    "get_bus",
    "emit",
    # Validator
    "validate_event",
    "assess_training_quality",
    "ValidationError",
]
