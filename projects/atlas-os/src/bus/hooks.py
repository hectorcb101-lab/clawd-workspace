"""
Atlas OS Integration Hooks

Easy-to-use functions for other Atlas systems to emit events.
Import these in atlas-self, atlas-judge, etc. to connect to the bus.
"""

import sys
from pathlib import Path
from typing import Optional, Literal

# Ensure bus module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from bus import emit, correction_event, outcome_event, judgment_event, instruction_event


def log_correction(
    context: str,
    wrong: str,
    right: str,
    why: str = "",
    category: str = "other",
    severity: str = "moderate"
) -> str:
    """
    Log a correction to the event bus.
    
    Called when Finn corrects Atlas or Atlas recognises a mistake.
    Automatically captured as DPO training data.
    
    Returns: event ID
    """
    event = correction_event(
        context=context,
        rejected=wrong,
        chosen=right,
        explanation=why,
        category=category,
        severity=severity
    )
    emit(event)
    return event.id


def log_outcome(
    task: str,
    result: Literal["success", "partial", "failure"],
    how: str = "",
    feedback: str = "",
    learned: str = ""
) -> str:
    """
    Log a task outcome to the event bus.
    
    Called after completing a significant task.
    Successful outcomes captured as SFT training data.
    
    Returns: event ID
    """
    event = outcome_event(
        task=task,
        result=result,
        approach=how,
        feedback=feedback,
        learnings=learned
    )
    emit(event)
    return event.id


def log_judgment(
    situation: str,
    principles: list[str],
    reasoning: str,
    decision: str,
    outcome: Optional[str] = None
) -> str:
    """
    Log a judgment application to the event bus.
    
    Called when Atlas consults judgment principles for a decision.
    Captured as reasoning traces for training.
    
    Returns: event ID
    """
    event = judgment_event(
        situation=situation,
        principles=principles,
        reasoning=reasoning,
        decision=decision,
        outcome=outcome
    )
    emit(event)
    return event.id


def log_good_response(
    prompt: str,
    response: str,
    system_prompt: str = "",
    quality: int = 4,
    tags: list[str] = None
) -> str:
    """
    Log a high-quality response as an SFT example.
    
    Called when a response is particularly good and worth training on.
    
    Returns: event ID
    """
    event = instruction_event(
        instruction=prompt,
        response=response,
        system=system_prompt,
        quality=quality,
        tags=tags or []
    )
    emit(event)
    return event.id


# Convenience aliases
correction = log_correction
outcome = log_outcome
judgment = log_judgment
good_response = log_good_response


if __name__ == "__main__":
    # Test the hooks
    print("Testing hooks...")
    
    eid = log_correction(
        context="User asked to delete a file",
        wrong="rm -rf file.txt",
        right="trash file.txt",
        why="Prefer recoverable deletion",
        category="process"
    )
    print(f"Logged correction: {eid}")
    
    eid = log_outcome(
        task="Created Atlas OS roadmap",
        result="success",
        how="Phased approach with clear milestones",
        feedback="Finn approved",
        learned="Plan before execute"
    )
    print(f"Logged outcome: {eid}")
    
    eid = log_judgment(
        situation="Should I start building immediately or plan first?",
        principles=["complexity-matching", "reversibility"],
        reasoning="Large project, many components, need clear architecture",
        decision="Plan first, create roadmap",
        outcome="success"
    )
    print(f"Logged judgment: {eid}")
    
    print("\n✅ All hooks working!")
