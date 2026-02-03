"""
Learning module for the Judgment Layer.
Tracks effectiveness, updates confidence, identifies what's working.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from .storage import JudgmentStorage
from .models import Principle, PrincipleApplication, ApplicationOutcome, CalibrationRecord


class JudgmentLearner:
    """
    Analyzes principle effectiveness and updates confidence scores.
    """
    
    def __init__(self, storage: JudgmentStorage):
        self.storage = storage
    
    def analyze_principle_effectiveness(self, principle_id: str) -> Dict:
        """
        Analyze how effective a principle has been.
        """
        principle = self.storage.get_principle(principle_id)
        if not principle:
            return {"error": f"Principle {principle_id} not found"}
        
        applications = self.storage.get_applications(principle_id=principle_id, limit=100)
        
        if not applications:
            return {
                "principle_id": principle_id,
                "applications": 0,
                "status": "no_data",
                "message": "No applications recorded yet"
            }
        
        # Count outcomes
        outcomes = {"success": 0, "partial": 0, "failure": 0, "unknown": 0}
        for app in applications:
            outcomes[app.outcome.value] += 1
        
        evaluated = outcomes["success"] + outcomes["partial"] + outcomes["failure"]
        
        if evaluated < 3:
            return {
                "principle_id": principle_id,
                "applications": len(applications),
                "evaluated": evaluated,
                "status": "insufficient_data",
                "message": f"Need at least 3 evaluated applications (have {evaluated})"
            }
        
        # Calculate effectiveness
        # Success = 1.0, Partial = 0.5, Failure = 0.0
        score = (outcomes["success"] + outcomes["partial"] * 0.5) / evaluated
        
        # Determine status
        if score >= 0.8:
            status = "highly_effective"
            recommendation = "Principle is working well. Consider increasing confidence."
        elif score >= 0.6:
            status = "effective"
            recommendation = "Principle is helpful. Continue using."
        elif score >= 0.4:
            status = "mixed"
            recommendation = "Principle has mixed results. Review examples and consider refinement."
        else:
            status = "ineffective"
            recommendation = "Principle may not be helping. Consider deactivating or major revision."
        
        return {
            "principle_id": principle_id,
            "principle_content": principle.content[:50] + "...",
            "applications": len(applications),
            "evaluated": evaluated,
            "outcomes": outcomes,
            "effectiveness_score": round(score, 2),
            "status": status,
            "recommendation": recommendation,
            "current_confidence": principle.confidence,
            "suggested_confidence": self._suggest_confidence(score, evaluated, principle.confidence)
        }
    
    def _suggest_confidence(self, effectiveness: float, sample_size: int, current: float) -> float:
        """
        Suggest updated confidence based on effectiveness and sample size.
        Moves gradually toward effectiveness score, weighted by sample size.
        """
        # Weight increases with sample size, maxes at 0.5 (we never fully trust data over design)
        weight = min(0.5, sample_size / 20)
        
        # Blend current confidence with effectiveness
        suggested = current * (1 - weight) + effectiveness * weight
        
        # Clamp to reasonable range
        return round(max(0.3, min(0.95, suggested)), 2)
    
    def get_all_effectiveness(self) -> List[Dict]:
        """
        Get effectiveness analysis for all active principles.
        """
        principles = self.storage.list_principles(active_only=True)
        results = []
        
        for p in principles:
            analysis = self.analyze_principle_effectiveness(p.id)
            results.append(analysis)
        
        # Sort by status priority (ineffective first, then by score)
        status_order = {"ineffective": 0, "mixed": 1, "insufficient_data": 2, 
                       "no_data": 3, "effective": 4, "highly_effective": 5}
        results.sort(key=lambda x: (status_order.get(x.get("status"), 3), 
                                    x.get("effectiveness_score", 0)))
        
        return results
    
    def update_principle_confidence(self, principle_id: str, auto: bool = False) -> Dict:
        """
        Update a principle's confidence based on its effectiveness.
        
        Args:
            principle_id: The principle to update
            auto: If True, apply automatically. If False, just suggest.
        """
        analysis = self.analyze_principle_effectiveness(principle_id)
        
        if "error" in analysis or analysis.get("status") in ["no_data", "insufficient_data"]:
            return {"updated": False, "reason": analysis.get("message", "Cannot update")}
        
        principle = self.storage.get_principle(principle_id)
        old_confidence = principle.confidence
        new_confidence = analysis["suggested_confidence"]
        
        if abs(new_confidence - old_confidence) < 0.05:
            return {
                "updated": False,
                "reason": "Confidence already aligned with effectiveness",
                "current": old_confidence
            }
        
        if auto:
            principle.confidence = new_confidence
            self.storage.save_principle(principle)
            return {
                "updated": True,
                "principle_id": principle_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "effectiveness": analysis["effectiveness_score"]
            }
        else:
            return {
                "updated": False,
                "suggestion": {
                    "principle_id": principle_id,
                    "current_confidence": old_confidence,
                    "suggested_confidence": new_confidence,
                    "effectiveness": analysis["effectiveness_score"],
                    "sample_size": analysis["evaluated"]
                }
            }
    
    def get_principles_needing_review(self) -> List[Dict]:
        """
        Get principles that need human review (ineffective or mixed results).
        """
        all_effectiveness = self.get_all_effectiveness()
        return [e for e in all_effectiveness 
                if e.get("status") in ["ineffective", "mixed"]]
    
    def get_learning_summary(self, days: int = 30) -> Dict:
        """
        Get a summary of what we've learned over a time period.
        """
        # Get all applications in time period
        all_apps = self.storage.get_applications(limit=500)
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_apps = [a for a in all_apps if a.applied_at >= cutoff]
        
        if not recent_apps:
            return {
                "period_days": days,
                "applications": 0,
                "message": "No applications in this period"
            }
        
        # Aggregate stats
        by_principle = {}
        outcomes_total = {"success": 0, "partial": 0, "failure": 0, "unknown": 0}
        
        for app in recent_apps:
            pid = app.principle_id
            if pid not in by_principle:
                by_principle[pid] = {"count": 0, "success": 0, "failure": 0}
            by_principle[pid]["count"] += 1
            if app.outcome == ApplicationOutcome.SUCCESS:
                by_principle[pid]["success"] += 1
                outcomes_total["success"] += 1
            elif app.outcome == ApplicationOutcome.FAILURE:
                by_principle[pid]["failure"] += 1
                outcomes_total["failure"] += 1
            else:
                outcomes_total[app.outcome.value] += 1
        
        # Find most/least used
        most_used = max(by_principle.items(), key=lambda x: x[1]["count"]) if by_principle else None
        
        # Calculate overall success rate
        evaluated = outcomes_total["success"] + outcomes_total["partial"] + outcomes_total["failure"]
        overall_rate = (outcomes_total["success"] + outcomes_total["partial"] * 0.5) / evaluated if evaluated > 0 else None
        
        return {
            "period_days": days,
            "applications": len(recent_apps),
            "evaluated": evaluated,
            "outcomes": outcomes_total,
            "overall_success_rate": round(overall_rate, 2) if overall_rate else None,
            "principles_used": len(by_principle),
            "most_used_principle": most_used[0] if most_used else None,
            "most_used_count": most_used[1]["count"] if most_used else 0
        }
    
    # ─────────────────────────────────────────────────────────────
    # Calibration
    # ─────────────────────────────────────────────────────────────
    
    def log_prediction(
        self, 
        domain: str,
        prediction: str, 
        confidence: float,
        actual_outcome: str,
        correct: bool
    ) -> int:
        """
        Log a prediction and its outcome for calibration tracking.
        """
        record = CalibrationRecord(
            id=None,
            domain=domain,
            prediction=prediction,
            confidence=confidence,
            actual_outcome=actual_outcome,
            correct=correct
        )
        return self.storage.save_calibration(record)
    
    def get_calibration_analysis(self, domain: Optional[str] = None) -> Dict:
        """
        Analyze calibration - are my confidence levels accurate?
        """
        stats = self.storage.get_calibration_stats(domain)
        
        if stats["total"] < 10:
            return {
                "status": "insufficient_data",
                "total": stats["total"],
                "message": "Need at least 10 predictions for calibration analysis"
            }
        
        # Analyze each bucket
        calibration_errors = []
        for bucket_range, bucket_data in stats["buckets"].items():
            if bucket_data["total"] >= 3 and bucket_data["accuracy"] is not None:
                # Expected accuracy is midpoint of range
                range_parts = bucket_range.split("-")
                expected = (float(range_parts[0]) + float(range_parts[1])) / 2
                actual = bucket_data["accuracy"]
                error = actual - expected
                calibration_errors.append({
                    "range": bucket_range,
                    "expected": expected,
                    "actual": round(actual, 2),
                    "error": round(error, 2),
                    "samples": bucket_data["total"]
                })
        
        # Determine overall calibration
        if not calibration_errors:
            return {
                "status": "insufficient_data",
                "message": "Not enough data in any confidence bucket"
            }
        
        avg_error = sum(abs(e["error"]) for e in calibration_errors) / len(calibration_errors)
        
        if avg_error < 0.1:
            status = "well_calibrated"
            message = "Confidence levels are accurate"
        elif avg_error < 0.2:
            status = "slightly_miscalibrated"
            message = "Minor adjustments needed"
        else:
            status = "poorly_calibrated"
            # Determine direction
            avg_signed_error = sum(e["error"] for e in calibration_errors) / len(calibration_errors)
            if avg_signed_error > 0:
                message = "Tends to be UNDERCONFIDENT - predictions are better than confidence suggests"
            else:
                message = "Tends to be OVERCONFIDENT - predictions are worse than confidence suggests"
        
        return {
            "status": status,
            "message": message,
            "total_predictions": stats["total"],
            "overall_accuracy": round(stats["overall_accuracy"], 2),
            "average_calibration_error": round(avg_error, 2),
            "buckets": calibration_errors
        }


def run_learning_cycle(storage: JudgmentStorage, auto_update: bool = False) -> Dict:
    """
    Run a full learning cycle:
    1. Analyze all principle effectiveness
    2. Update confidence scores (if auto)
    3. Flag principles needing review
    4. Return summary
    """
    learner = JudgmentLearner(storage)
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "effectiveness": [],
        "confidence_updates": [],
        "needs_review": [],
        "summary": {}
    }
    
    # Analyze all
    all_effectiveness = learner.get_all_effectiveness()
    results["effectiveness"] = all_effectiveness
    
    # Update confidence if auto
    if auto_update:
        for analysis in all_effectiveness:
            if analysis.get("status") in ["effective", "highly_effective", "ineffective", "mixed"]:
                update = learner.update_principle_confidence(analysis["principle_id"], auto=True)
                if update.get("updated"):
                    results["confidence_updates"].append(update)
    
    # Get needs review
    results["needs_review"] = learner.get_principles_needing_review()
    
    # Get summary
    results["summary"] = learner.get_learning_summary()
    
    return results


if __name__ == "__main__":
    storage = JudgmentStorage()
    learner = JudgmentLearner(storage)
    
    print("\n📊 Learning Analysis\n")
    print("=" * 50)
    
    summary = learner.get_learning_summary()
    print(f"\nLast 30 days: {summary['applications']} applications")
    if summary.get("overall_success_rate"):
        print(f"Overall success rate: {summary['overall_success_rate']*100:.0f}%")
    
    print("\n" + "=" * 50)
    print("\nPrinciple Effectiveness:\n")
    
    for analysis in learner.get_all_effectiveness():
        status_emoji = {
            "highly_effective": "🟢",
            "effective": "🟡", 
            "mixed": "🟠",
            "ineffective": "🔴",
            "insufficient_data": "⚪",
            "no_data": "⚫"
        }.get(analysis.get("status"), "❓")
        
        print(f"{status_emoji} {analysis['principle_id']}: {analysis.get('status', 'unknown')}")
        if analysis.get("effectiveness_score") is not None:
            print(f"   Score: {analysis['effectiveness_score']*100:.0f}% ({analysis['evaluated']} evaluated)")
    
    storage.close()
