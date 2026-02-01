"""Atlas Self-Awareness System - Core Package"""

from .database import init_database, get_stats
from .models import (
    OutcomeEvent, CorrectionEvent, Pattern, Insight,
    Outcome, FeedbackSource, CorrectionType, Severity,
    PatternType, PatternStatus, InsightType, Priority
)
from .classifier import classify_task, suggest_task_type, get_all_task_types
from .logger import (
    log_outcome, log_correction,
    get_recent_outcomes, get_recent_corrections,
    get_outcome_summary, get_correction_summary
)
from .analyzer import (
    compute_trends, detect_failure_patterns, detect_strength_patterns,
    run_full_analysis, save_patterns_to_db, get_active_patterns
)
from .query import (
    query_strengths, query_weaknesses, query_blind_spots,
    query_progress, query_natural
)
from .insights import (
    generate_insights, save_insights, get_pending_insights,
    mark_surfaced, get_insight_for_task, run_insight_check,
    format_insight_for_display
)

__all__ = [
    # Database
    'init_database', 'get_stats',
    # Models
    'OutcomeEvent', 'CorrectionEvent', 'Pattern', 'Insight',
    'Outcome', 'FeedbackSource', 'CorrectionType', 'Severity',
    'PatternType', 'PatternStatus', 'InsightType', 'Priority',
    # Classifier
    'classify_task', 'suggest_task_type', 'get_all_task_types',
    # Logger
    'log_outcome', 'log_correction',
    'get_recent_outcomes', 'get_recent_corrections',
    'get_outcome_summary', 'get_correction_summary',
    # Analyzer
    'compute_trends', 'detect_failure_patterns', 'detect_strength_patterns',
    'run_full_analysis', 'save_patterns_to_db', 'get_active_patterns',
]
