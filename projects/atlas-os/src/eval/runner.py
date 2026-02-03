"""
Atlas OS Evaluation Runner

Run evaluation scenarios against an LLM and score the results.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .scenarios import EvalScenario, get_scenarios, ScenarioCategory

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import LLMInterface, Message, GenerateConfig, create_adapter


@dataclass
class EvalResult:
    """Result from a single evaluation."""
    scenario_id: str
    scenario_name: str
    category: str
    
    # Response
    response: str
    response_length: int
    
    # Scores (0-100)
    content_score: int = 0  # Based on should_contain/should_not_contain
    length_score: int = 0   # Based on max/min length
    overall_score: int = 0
    
    # Details
    matched_positive: List[str] = field(default_factory=list)
    matched_negative: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    # Metadata
    model: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvalReport:
    """Full evaluation report."""
    model: str
    timestamp: str
    results: List[EvalResult]
    
    # Aggregate scores
    overall_score: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    
    # Summary
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    
    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "timestamp": self.timestamp,
            "overall_score": round(self.overall_score, 1),
            "category_scores": {k: round(v, 1) for k, v in self.category_scores.items()},
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "results": [r.to_dict() for r in self.results],
        }


class EvalRunner:
    """
    Run evaluation scenarios against an LLM.
    
    Usage:
        runner = EvalRunner(llm)
        report = runner.run_all()
        print(f"Score: {report.overall_score}/100")
    """
    
    def __init__(
        self,
        llm: LLMInterface,
        system_prompt: Optional[str] = None,
    ):
        self.llm = llm
        self.system_prompt = system_prompt or self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        return """You are Atlas, a personal AI assistant.

Core traits:
- Direct and concise, no filler phrases
- Has opinions and expresses them thoughtfully
- Uses British English spelling
- Honest about uncertainty
- Engineering mindset: asks why before how
- Respectful but will push back when needed

Be helpful, genuine, and resourceful."""
    
    def run_scenario(self, scenario: EvalScenario) -> EvalResult:
        """Run a single evaluation scenario."""
        # Build messages
        messages = []
        system = scenario.system_prompt or self.system_prompt
        if system:
            messages.append(Message.system(system))
        messages.append(Message.user(scenario.prompt))
        
        # Generate response
        config = GenerateConfig(
            max_tokens=1024,
            temperature=0.3,  # Lower temp for more consistent eval
        )
        
        try:
            result = self.llm.generate(messages, config)
            response = result.content.strip()
        except Exception as e:
            response = f"[ERROR: {e}]"
        
        # Score the response
        return self._score_response(scenario, response)
    
    def _score_response(self, scenario: EvalScenario, response: str) -> EvalResult:
        """Score a response against scenario criteria."""
        result = EvalResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            category=scenario.category.value,
            response=response,
            response_length=len(response),
            model=self.llm.model_id,
            timestamp=datetime.now().isoformat(),
        )
        
        response_lower = response.lower()
        
        # Check positive matches (should_contain)
        positive_matches = 0
        for term in scenario.should_contain:
            if term.lower() in response_lower:
                result.matched_positive.append(term)
                positive_matches += 1
        
        if scenario.should_contain:
            result.content_score = int((positive_matches / len(scenario.should_contain)) * 100)
        else:
            result.content_score = 100  # No requirements = pass
        
        # Check negative matches (should_not_contain)
        negative_penalty = 0
        for term in scenario.should_not_contain:
            if term.lower() in response_lower:
                result.matched_negative.append(term)
                negative_penalty += 20  # Each negative match costs 20 points
        
        result.content_score = max(0, result.content_score - negative_penalty)
        
        # Length scoring
        result.length_score = 100
        if scenario.max_length and len(response) > scenario.max_length:
            excess = len(response) - scenario.max_length
            penalty = min(50, excess // 10)  # Penalize for excess length
            result.length_score -= penalty
            result.notes.append(f"Response too long ({len(response)} > {scenario.max_length})")
        
        if scenario.min_length and len(response) < scenario.min_length:
            shortfall = scenario.min_length - len(response)
            penalty = min(50, shortfall // 10)
            result.length_score -= penalty
            result.notes.append(f"Response too short ({len(response)} < {scenario.min_length})")
        
        # Overall score (weighted average)
        result.overall_score = int(
            result.content_score * 0.7 +
            result.length_score * 0.3
        )
        
        # Add notes
        if result.matched_negative:
            result.notes.append(f"Matched unwanted terms: {result.matched_negative}")
        
        if scenario.should_contain and not result.matched_positive:
            result.notes.append("No expected terms found")
        
        return result
    
    def run_all(
        self,
        category: Optional[ScenarioCategory] = None,
        scenario_ids: Optional[List[str]] = None,
    ) -> EvalReport:
        """Run all scenarios and generate report."""
        scenarios = get_scenarios(category, scenario_ids)
        
        results = []
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            results.append(result)
        
        return self._generate_report(results)
    
    def _generate_report(self, results: List[EvalResult]) -> EvalReport:
        """Generate evaluation report from results."""
        report = EvalReport(
            model=self.llm.model_id,
            timestamp=datetime.now().isoformat(),
            results=results,
        )
        
        if not results:
            return report
        
        # Calculate overall score
        scores = [r.overall_score for r in results]
        report.overall_score = sum(scores) / len(scores)
        
        # Calculate category scores
        category_results = {}
        for r in results:
            if r.category not in category_results:
                category_results[r.category] = []
            category_results[r.category].append(r.overall_score)
        
        report.category_scores = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_results.items()
        }
        
        # Count pass/fail/warning
        for r in results:
            if r.overall_score >= 70:
                report.passed += 1
            elif r.overall_score >= 50:
                report.warnings += 1
            else:
                report.failed += 1
        
        return report


def run_evaluation(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    category: Optional[str] = None,
    verbose: bool = False,
) -> EvalReport:
    """
    Convenience function to run evaluation.
    
    Args:
        provider: LLM provider (default from config)
        model: Model name
        category: Filter to specific category
        verbose: Print progress
    
    Returns:
        EvalReport with results
    """
    llm = create_adapter(provider, model)
    
    if verbose:
        print(f"Running evaluation on {llm.provider}/{llm.model_id}...")
    
    runner = EvalRunner(llm)
    
    cat = ScenarioCategory(category) if category else None
    report = runner.run_all(category=cat)
    
    return report


# Results storage
RESULTS_DIR = Path.home() / "clawd" / "projects" / "atlas-os" / "data" / "eval"


def save_report(report: EvalReport, name: Optional[str] = None) -> Path:
    """Save evaluation report to disk."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if name:
        filename = f"{name}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_clean = report.model.replace("/", "_").replace(":", "_")
        filename = f"eval_{model_clean}_{timestamp}.json"
    
    path = RESULTS_DIR / filename
    with open(path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    
    return path


def load_report(path: Path) -> EvalReport:
    """Load evaluation report from disk."""
    with open(path) as f:
        data = json.load(f)
    
    results = [EvalResult(**r) for r in data.pop("results", [])]
    return EvalReport(results=results, **data)


def list_reports() -> List[Path]:
    """List saved evaluation reports."""
    if not RESULTS_DIR.exists():
        return []
    return sorted(RESULTS_DIR.glob("eval_*.json"), reverse=True)
