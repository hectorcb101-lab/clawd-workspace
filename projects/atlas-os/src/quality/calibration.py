"""
Atlas OS Calibration Tracker

Track predictions with confidence levels and measure accuracy over time.
Improves Atlas's uncertainty calibration.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import sqlite3


DB_PATH = Path.home() / "clawd" / "projects" / "atlas-os" / "data" / "calibration.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            reasoning TEXT,
            actual_outcome TEXT,
            correct INTEGER,
            created_at TEXT NOT NULL,
            resolved_at TEXT
        )
    """)
    conn.commit()
    return conn


@dataclass
class Prediction:
    """A prediction with confidence level."""
    domain: str  # e.g., "code_works", "task_time", "user_preference"
    prediction: str
    confidence: float  # 0.0 - 1.0
    reasoning: Optional[str] = None
    actual_outcome: Optional[str] = None
    correct: Optional[bool] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None


class CalibrationTracker:
    """
    Tracks predictions and measures calibration.
    
    Usage:
        tracker = CalibrationTracker()
        
        # Log a prediction
        pred_id = tracker.predict(
            domain="task_completion",
            prediction="This will take about 30 minutes",
            confidence=0.7,
            reasoning="Based on similar tasks"
        )
        
        # Later, record outcome
        tracker.resolve(pred_id, "Took 25 minutes", correct=True)
        
        # Check calibration
        stats = tracker.get_calibration()
    """
    
    def __init__(self):
        self.conn = get_connection()
    
    def predict(
        self,
        domain: str,
        prediction: str,
        confidence: float,
        reasoning: str = None,
    ) -> int:
        """Log a prediction with confidence level."""
        confidence = max(0.0, min(1.0, confidence))
        
        cursor = self.conn.execute("""
            INSERT INTO predictions (domain, prediction, confidence, reasoning, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (domain, prediction, confidence, reasoning, datetime.now().isoformat()))
        self.conn.commit()
        
        return cursor.lastrowid
    
    def resolve(
        self,
        prediction_id: int,
        actual_outcome: str,
        correct: bool,
    ) -> bool:
        """Record the actual outcome of a prediction."""
        self.conn.execute("""
            UPDATE predictions
            SET actual_outcome = ?, correct = ?, resolved_at = ?
            WHERE id = ?
        """, (actual_outcome, 1 if correct else 0, datetime.now().isoformat(), prediction_id))
        self.conn.commit()
        return True
    
    def get_pending(self, limit: int = 20) -> List[Prediction]:
        """Get predictions awaiting resolution."""
        rows = self.conn.execute("""
            SELECT * FROM predictions
            WHERE actual_outcome IS NULL
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [self._row_to_prediction(r) for r in rows]
    
    def get_calibration(self, domain: str = None) -> Dict[str, Any]:
        """
        Calculate calibration statistics.
        
        Good calibration: When you say 70% confident, you're right ~70% of the time.
        """
        query = """
            SELECT confidence, correct
            FROM predictions
            WHERE correct IS NOT NULL
        """
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        rows = self.conn.execute(query, params).fetchall()
        
        if not rows:
            return {
                "total_predictions": 0,
                "calibration": None,
                "message": "No resolved predictions yet"
            }
        
        # Bucket by confidence level
        buckets = {
            "0-20%": {"count": 0, "correct": 0},
            "20-40%": {"count": 0, "correct": 0},
            "40-60%": {"count": 0, "correct": 0},
            "60-80%": {"count": 0, "correct": 0},
            "80-100%": {"count": 0, "correct": 0},
        }
        
        for row in rows:
            conf = row["confidence"]
            correct = row["correct"]
            
            if conf < 0.2:
                bucket = "0-20%"
            elif conf < 0.4:
                bucket = "20-40%"
            elif conf < 0.6:
                bucket = "40-60%"
            elif conf < 0.8:
                bucket = "60-80%"
            else:
                bucket = "80-100%"
            
            buckets[bucket]["count"] += 1
            buckets[bucket]["correct"] += correct
        
        # Calculate accuracy per bucket
        for bucket, data in buckets.items():
            if data["count"] > 0:
                data["accuracy"] = round(data["correct"] / data["count"], 2)
            else:
                data["accuracy"] = None
        
        # Calculate overall calibration error
        # (difference between confidence and actual accuracy)
        total_error = 0
        total_count = 0
        for row in rows:
            total_error += abs(row["confidence"] - row["correct"])
            total_count += 1
        
        avg_calibration_error = round(total_error / total_count, 3) if total_count > 0 else None
        
        # Overall accuracy
        total_correct = sum(r["correct"] for r in rows)
        overall_accuracy = round(total_correct / len(rows), 2)
        
        return {
            "total_predictions": len(rows),
            "overall_accuracy": overall_accuracy,
            "calibration_error": avg_calibration_error,
            "buckets": buckets,
            "interpretation": self._interpret_calibration(avg_calibration_error),
        }
    
    def _interpret_calibration(self, error: float) -> str:
        """Interpret calibration error."""
        if error is None:
            return "Not enough data"
        elif error < 0.1:
            return "Excellent - well calibrated"
        elif error < 0.2:
            return "Good - minor adjustments needed"
        elif error < 0.3:
            return "Fair - tendency to over/under-confidence"
        else:
            return "Poor - significant miscalibration"
    
    def get_by_domain(self) -> Dict[str, Dict]:
        """Get calibration stats broken down by domain."""
        domains = self.conn.execute("""
            SELECT DISTINCT domain FROM predictions WHERE correct IS NOT NULL
        """).fetchall()
        
        return {
            row["domain"]: self.get_calibration(row["domain"])
            for row in domains
        }
    
    def _row_to_prediction(self, row: sqlite3.Row) -> Prediction:
        return Prediction(
            id=row["id"],
            domain=row["domain"],
            prediction=row["prediction"],
            confidence=row["confidence"],
            reasoning=row["reasoning"],
            actual_outcome=row["actual_outcome"],
            correct=bool(row["correct"]) if row["correct"] is not None else None,
            created_at=row["created_at"],
            resolved_at=row["resolved_at"],
        )


# Convenience functions
_tracker: Optional[CalibrationTracker] = None


def get_tracker() -> CalibrationTracker:
    global _tracker
    if _tracker is None:
        _tracker = CalibrationTracker()
    return _tracker


def log_prediction(
    domain: str,
    prediction: str,
    confidence: float,
    reasoning: str = None,
) -> int:
    """Log a prediction."""
    return get_tracker().predict(domain, prediction, confidence, reasoning)


def resolve_prediction(prediction_id: int, outcome: str, correct: bool) -> bool:
    """Resolve a prediction."""
    return get_tracker().resolve(prediction_id, outcome, correct)


def get_calibration_stats(domain: str = None) -> Dict[str, Any]:
    """Get calibration statistics."""
    return get_tracker().get_calibration(domain)


if __name__ == "__main__":
    print("Testing Calibration Tracker...\n")
    
    tracker = CalibrationTracker()
    
    # Log some test predictions
    p1 = tracker.predict("code", "This code will work first try", 0.8, "Simple function")
    p2 = tracker.predict("time", "Task will take 30 min", 0.6, "Based on complexity")
    p3 = tracker.predict("code", "This will have a bug", 0.3, "Complex logic")
    
    # Resolve them
    tracker.resolve(p1, "Had a typo", correct=False)
    tracker.resolve(p2, "Took 25 min", correct=True)
    tracker.resolve(p3, "Worked fine", correct=False)  # Predicted bug but none
    
    # Check calibration
    stats = tracker.get_calibration()
    print(f"Calibration Stats:")
    print(json.dumps(stats, indent=2))
