"""
Atlas OS Evaluation Pipeline

Measure "Atlas-ness" of language models.
"""

from .scenarios import (
    EvalScenario,
    ScenarioCategory,
    get_scenarios,
    get_scenario_by_id,
    SCENARIOS,
)

from .runner import (
    EvalResult,
    EvalReport,
    EvalRunner,
    run_evaluation,
    save_report,
    load_report,
    list_reports,
)

__all__ = [
    # Scenarios
    "EvalScenario",
    "ScenarioCategory",
    "get_scenarios",
    "get_scenario_by_id",
    "SCENARIOS",
    # Runner
    "EvalResult",
    "EvalReport",
    "EvalRunner",
    "run_evaluation",
    "save_report",
    "load_report",
    "list_reports",
]
