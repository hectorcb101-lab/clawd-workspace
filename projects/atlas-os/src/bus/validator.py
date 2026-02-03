"""
Atlas OS Event Validator

Validates events conform to schema and training data quality standards.
"""

from typing import Tuple, List
from .schema import AtlasEvent, EventType, TrainingFormat, TrainingMeta


class ValidationError:
    """Single validation error."""
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


def validate_event(event: AtlasEvent) -> Tuple[bool, List[ValidationError]]:
    """
    Validate an event conforms to schema.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not event.id:
        errors.append(ValidationError("id", "Event ID is required"))
    
    if not event.timestamp:
        errors.append(ValidationError("timestamp", "Timestamp is required"))
    
    if not event.type:
        errors.append(ValidationError("type", "Event type is required"))
    
    if not event.source:
        errors.append(ValidationError("source", "Event source is required"))
    
    # Summary should be present and meaningful
    if not event.summary:
        errors.append(ValidationError("summary", "Summary is required", "warning"))
    elif len(event.summary) < 10:
        errors.append(ValidationError("summary", "Summary too short (< 10 chars)", "warning"))
    
    # Type-specific validation
    if event.type == EventType.CORRECTION:
        errors.extend(_validate_correction(event))
    elif event.type == EventType.OUTCOME:
        errors.extend(_validate_outcome(event))
    elif event.type == EventType.JUDGMENT_APPLY:
        errors.extend(_validate_judgment(event))
    elif event.type == EventType.TRAINING_EXAMPLE:
        errors.extend(_validate_training_example(event))
    
    # Training metadata validation
    if event.training.usable:
        errors.extend(_validate_training_meta(event))
    
    is_valid = not any(e.severity == "error" for e in errors)
    return is_valid, errors


def _validate_correction(event: AtlasEvent) -> List[ValidationError]:
    """Validate correction event data."""
    errors = []
    data = event.data
    
    if not data.get("context"):
        errors.append(ValidationError("data.context", "Correction needs context"))
    
    if not data.get("rejected"):
        errors.append(ValidationError("data.rejected", "Correction needs rejected response"))
    
    if not data.get("chosen"):
        errors.append(ValidationError("data.chosen", "Correction needs chosen response"))
    
    # Quality checks
    if data.get("rejected") == data.get("chosen"):
        errors.append(ValidationError("data", "Rejected and chosen are identical", "warning"))
    
    if len(data.get("context", "")) < 20:
        errors.append(ValidationError("data.context", "Context too short for training", "warning"))
    
    return errors


def _validate_outcome(event: AtlasEvent) -> List[ValidationError]:
    """Validate outcome event data."""
    errors = []
    data = event.data
    
    if not data.get("task"):
        errors.append(ValidationError("data.task", "Outcome needs task description"))
    
    if data.get("result") not in ["success", "partial", "failure"]:
        errors.append(ValidationError("data.result", "Invalid result value"))
    
    return errors


def _validate_judgment(event: AtlasEvent) -> List[ValidationError]:
    """Validate judgment event data."""
    errors = []
    data = event.data
    
    if not data.get("situation"):
        errors.append(ValidationError("data.situation", "Judgment needs situation"))
    
    if not data.get("reasoning"):
        errors.append(ValidationError("data.reasoning", "Judgment needs reasoning"))
    
    if not data.get("decision"):
        errors.append(ValidationError("data.decision", "Judgment needs decision"))
    
    # Quality checks
    if len(data.get("reasoning", "")) < 50:
        errors.append(ValidationError("data.reasoning", "Reasoning too short for training", "warning"))
    
    return errors


def _validate_training_example(event: AtlasEvent) -> List[ValidationError]:
    """Validate training example event data."""
    errors = []
    data = event.data
    
    if not data.get("instruction"):
        errors.append(ValidationError("data.instruction", "Training example needs instruction"))
    
    if not data.get("response"):
        errors.append(ValidationError("data.response", "Training example needs response"))
    
    # Quality checks
    if len(data.get("response", "")) < 50:
        errors.append(ValidationError("data.response", "Response too short", "warning"))
    
    return errors


def _validate_training_meta(event: AtlasEvent) -> List[ValidationError]:
    """Validate training metadata."""
    errors = []
    meta = event.training
    
    if meta.format == TrainingFormat.NONE:
        errors.append(ValidationError("training.format", "Usable event has no format"))
    
    if meta.quality < 1 or meta.quality > 5:
        errors.append(ValidationError("training.quality", "Quality must be 1-5", "warning"))
    
    return errors


def assess_training_quality(event: AtlasEvent) -> Tuple[int, List[str]]:
    """
    Assess the quality of an event for training purposes.
    
    Returns:
        (quality_score_1_5, list_of_suggestions)
    """
    suggestions = []
    score = 3  # Start at baseline
    
    if not event.training.usable:
        return 0, ["Event not marked as training-usable"]
    
    data = event.data
    
    # Check richness of context
    context_len = len(data.get("context", "") or data.get("situation", "") or "")
    if context_len > 200:
        score += 1
        suggestions.append("✓ Rich context")
    elif context_len < 50:
        score -= 1
        suggestions.append("⚠ Add more context")
    
    # Check explanation/reasoning
    explanation = data.get("explanation", "") or data.get("reasoning", "") or ""
    if len(explanation) > 100:
        score += 1
        suggestions.append("✓ Good explanation")
    elif not explanation:
        score -= 1
        suggestions.append("⚠ Add explanation/reasoning")
    
    # Check for tags
    if event.tags:
        suggestions.append("✓ Has tags")
    else:
        suggestions.append("⚠ Consider adding tags")
    
    # Clamp score
    score = max(1, min(5, score))
    
    return score, suggestions


if __name__ == "__main__":
    from .schema import correction_event, outcome_event
    
    # Test validation
    print("Testing event validation...\n")
    
    # Good correction
    good = correction_event(
        context="User asked me to delete important files without backup",
        rejected="Sure, I'll delete them right away",
        chosen="Before deleting, let me create a backup first. Should I proceed?",
        explanation="Always confirm destructive operations and suggest safety measures",
        category="process",
        severity="major"
    )
    is_valid, errors = validate_event(good)
    print(f"Good correction: valid={is_valid}")
    for e in errors:
        print(f"  {e}")
    
    quality, suggestions = assess_training_quality(good)
    print(f"  Training quality: {quality}/5")
    for s in suggestions:
        print(f"    {s}")
    
    print()
    
    # Bad correction (missing data)
    from .schema import AtlasEvent, EventType, EventSource
    bad = AtlasEvent(
        type=EventType.CORRECTION,
        source=EventSource.MANUAL,
        summary="Bad",
        data={}
    )
    is_valid, errors = validate_event(bad)
    print(f"Bad correction: valid={is_valid}")
    for e in errors:
        print(f"  {e}")
