"""
Atlas OS Quality Assessment

Auto-scoring, LLM-as-judge, and conversation ingestion.
"""

from .scorer import (
    ResponseScorer,
    QualityScore,
    score_response,
    score_and_capture,
    get_scorer,
)

from .llm_judge import (
    LLMJudge,
    JudgeScore,
    judge_response,
    get_judge,
)

from .ingester import (
    ConversationIngester,
    CapturedExample,
    run_ingestion,
    get_ingestion_stats,
)

from .calibration import (
    CalibrationTracker,
    Prediction,
    log_prediction,
    resolve_prediction,
    get_calibration_stats,
    get_tracker,
)

__all__ = [
    # Scorer
    "ResponseScorer",
    "QualityScore",
    "score_response",
    "score_and_capture",
    "get_scorer",
    # Judge
    "LLMJudge",
    "JudgeScore",
    "judge_response",
    "get_judge",
    # Ingester
    "ConversationIngester",
    "CapturedExample",
    "run_ingestion",
    "get_ingestion_stats",
    # Calibration
    "CalibrationTracker",
    "Prediction",
    "log_prediction",
    "resolve_prediction",
    "get_calibration_stats",
    "get_tracker",
]
