"""
Atlas Self-Awareness System - Pattern Analyzer

Identifies patterns in outcomes and corrections:
- Failure clustering (what keeps going wrong?)
- Strength detection (what am I good at?)
- Trend computation (am I improving?)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json

from .database import db_session
from .models import PatternType, PatternStatus, Priority


def compute_trends(period_type: str = 'week', lookback: int = 4) -> List[Dict[str, Any]]:
    """
    Compute success rate trends over time periods.
    
    Args:
        period_type: 'day', 'week', or 'month'
        lookback: How many periods to look back
    
    Returns:
        List of trend data per task type
    """
    # Calculate period boundaries
    now = datetime.utcnow()
    
    if period_type == 'day':
        delta = timedelta(days=1)
        sql_format = '%Y-%m-%d'
    elif period_type == 'week':
        delta = timedelta(weeks=1)
        sql_format = '%Y-%W'  # Year-Week
    else:  # month
        delta = timedelta(days=30)
        sql_format = '%Y-%m'
    
    with db_session() as conn:
        # Get all outcomes grouped by task type and period
        rows = conn.execute(f"""
            SELECT 
                task_type,
                strftime('{sql_format}', created_at) as period,
                outcome,
                COUNT(*) as count
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type, period, outcome
            ORDER BY task_type, period
        """, (f'-{lookback * 7 if period_type == "week" else lookback} days',)).fetchall()
        
        # Build trend data
        task_periods = defaultdict(lambda: defaultdict(lambda: {'success': 0, 'failure': 0, 'partial': 0, 'unknown': 0, 'total': 0}))
        
        for row in rows:
            task = row['task_type']
            period = row['period']
            outcome = row['outcome']
            count = row['count']
            
            task_periods[task][period][outcome] = count
            task_periods[task][period]['total'] += count
        
        # Calculate success rates and trends
        trends = []
        for task_type, periods in task_periods.items():
            sorted_periods = sorted(periods.items())
            
            period_data = []
            for period, counts in sorted_periods:
                total = counts['total']
                if total > 0:
                    # Success rate: success + 0.5*partial
                    rate = (counts['success'] + 0.5 * counts['partial']) / total
                else:
                    rate = None
                
                period_data.append({
                    'period': period,
                    'total': total,
                    'success': counts['success'],
                    'failure': counts['failure'],
                    'partial': counts['partial'],
                    'success_rate': rate
                })
            
            # Calculate trend direction
            if len(period_data) >= 2:
                recent = [p for p in period_data[-2:] if p['success_rate'] is not None]
                if len(recent) == 2:
                    change = recent[1]['success_rate'] - recent[0]['success_rate']
                    trend_direction = 'improving' if change > 0.05 else ('declining' if change < -0.05 else 'stable')
                else:
                    trend_direction = 'insufficient_data'
                    change = None
            else:
                trend_direction = 'insufficient_data'
                change = None
            
            trends.append({
                'task_type': task_type,
                'period_type': period_type,
                'periods': period_data,
                'trend': trend_direction,
                'change': change,
                'total_outcomes': sum(p['total'] for p in period_data)
            })
        
        return trends


def detect_failure_patterns(min_occurrences: int = 2, days: int = 30) -> List[Dict[str, Any]]:
    """
    Detect recurring failure patterns.
    
    Looks for:
    - Same task type failing multiple times
    - Similar notes/context in failures
    - Correction clusters
    """
    patterns = []
    
    with db_session() as conn:
        # 1. Task types with high failure rates
        failure_rates = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failures,
                SUM(CASE WHEN outcome = 'partial' THEN 1 ELSE 0 END) as partials
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING total >= ?
        """, (f'-{days} days', min_occurrences)).fetchall()
        
        for row in failure_rates:
            total = row['total']
            failures = row['failures']
            partials = row['partials']
            
            # Failure rate = failures + 0.5*partials (partial = half failure)
            failure_rate = (failures + 0.5 * partials) / total if total > 0 else 0
            
            if failure_rate > 0.3 and failures >= min_occurrences:  # 30%+ failure rate
                # Get recent failure examples
                examples = conn.execute("""
                    SELECT notes, context, created_at
                    FROM outcomes
                    WHERE task_type = ? AND outcome IN ('failure', 'partial')
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (row['task_type'],)).fetchall()
                
                patterns.append({
                    'pattern_type': 'high_failure_rate',
                    'task_type': row['task_type'],
                    'description': f"High failure rate in {row['task_type']} tasks",
                    'failure_rate': failure_rate,
                    'total_attempts': total,
                    'failures': failures,
                    'partials': partials,
                    'severity': 'high' if failure_rate > 0.5 else 'medium',
                    'examples': [dict(e) for e in examples],
                    'confidence': min(0.9, 0.5 + (failures / 10))  # More failures = more confident
                })
        
        # 2. Correction clusters by type
        correction_clusters = conn.execute("""
            SELECT 
                correction_type,
                COALESCE(task_type, 'unclassified') as task_type,
                COUNT(*) as count,
                GROUP_CONCAT(user_signal, ' | ') as signals
            FROM corrections
            WHERE created_at >= datetime('now', ?)
            GROUP BY correction_type, task_type
            HAVING count >= ?
        """, (f'-{days} days', min_occurrences)).fetchall()
        
        for row in correction_clusters:
            patterns.append({
                'pattern_type': 'correction_cluster',
                'correction_type': row['correction_type'],
                'task_type': row['task_type'],
                'description': f"Recurring {row['correction_type']} corrections in {row['task_type']}",
                'count': row['count'],
                'severity': 'high' if row['count'] >= 5 else ('medium' if row['count'] >= 3 else 'low'),
                'signals': row['signals'].split(' | ')[:5] if row['signals'] else [],
                'confidence': min(0.9, 0.4 + (row['count'] / 10))
            })
        
        # 3. Major corrections (always significant)
        major_corrections = conn.execute("""
            SELECT 
                user_signal,
                lesson,
                task_type,
                correction_type,
                created_at
            FROM corrections
            WHERE severity = 'major'
            AND created_at >= datetime('now', ?)
            ORDER BY created_at DESC
        """, (f'-{days} days',)).fetchall()
        
        if major_corrections:
            patterns.append({
                'pattern_type': 'major_corrections',
                'description': f"Major corrections requiring attention",
                'count': len(major_corrections),
                'severity': 'high',
                'corrections': [dict(c) for c in major_corrections],
                'confidence': 0.9
            })
    
    # Sort by severity and confidence
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    patterns.sort(key=lambda p: (severity_order.get(p.get('severity', 'low'), 3), -p.get('confidence', 0)))
    
    return patterns


def detect_strength_patterns(min_occurrences: int = 3, days: int = 30) -> List[Dict[str, Any]]:
    """
    Detect areas of strength.
    
    Looks for:
    - Task types with high success rates
    - Consistent high-confidence successes
    - Improvement trends
    """
    patterns = []
    
    with db_session() as conn:
        # Task types with high success rates
        success_rates = conn.execute("""
            SELECT 
                task_type,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                AVG(CASE WHEN outcome = 'success' THEN confidence ELSE NULL END) as avg_confidence
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
            GROUP BY task_type
            HAVING total >= ?
        """, (f'-{days} days', min_occurrences)).fetchall()
        
        for row in success_rates:
            total = row['total']
            successes = row['successes']
            success_rate = successes / total if total > 0 else 0
            avg_conf = row['avg_confidence'] or 0
            
            if success_rate >= 0.7:  # 70%+ success rate
                patterns.append({
                    'pattern_type': 'high_success_rate',
                    'task_type': row['task_type'],
                    'description': f"Strong performance in {row['task_type']} tasks",
                    'success_rate': success_rate,
                    'total_attempts': total,
                    'successes': successes,
                    'avg_confidence': avg_conf,
                    'strength_level': 'excellent' if success_rate >= 0.9 else ('strong' if success_rate >= 0.8 else 'good'),
                    'confidence': min(0.9, 0.5 + (successes / 20))
                })
    
    # Check for improvement trends (task types getting better)
    trends = compute_trends(period_type='week', lookback=4)
    for trend in trends:
        if trend['trend'] == 'improving' and trend['change'] and trend['change'] > 0.1:
            patterns.append({
                'pattern_type': 'improving_trend',
                'task_type': trend['task_type'],
                'description': f"Improving at {trend['task_type']} (+{trend['change']:.0%} over recent weeks)",
                'change': trend['change'],
                'strength_level': 'improving',
                'confidence': 0.7 if trend['total_outcomes'] >= 5 else 0.5
            })
    
    # Sort by success rate and confidence
    patterns.sort(key=lambda p: (-p.get('success_rate', 0), -p.get('confidence', 0)))
    
    return patterns


def run_full_analysis(days: int = 30) -> Dict[str, Any]:
    """
    Run complete pattern analysis.
    
    Returns comprehensive analysis including:
    - Failure patterns
    - Strength patterns
    - Trends
    - Summary stats
    """
    with db_session() as conn:
        # Basic counts
        outcome_count = conn.execute(
            "SELECT COUNT(*) FROM outcomes WHERE created_at >= datetime('now', ?)",
            (f'-{days} days',)
        ).fetchone()[0]
        
        correction_count = conn.execute(
            "SELECT COUNT(*) FROM corrections WHERE created_at >= datetime('now', ?)",
            (f'-{days} days',)
        ).fetchone()[0]
    
    failure_patterns = detect_failure_patterns(days=days)
    strength_patterns = detect_strength_patterns(days=days)
    trends = compute_trends(period_type='week', lookback=4)
    
    # Overall health score (0-100)
    # Based on: success rate, correction frequency, trend direction
    health_factors = []
    
    # Factor 1: Overall success rate
    with db_session() as conn:
        overall = conn.execute("""
            SELECT 
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failures,
                COUNT(*) as total
            FROM outcomes
            WHERE created_at >= datetime('now', ?)
        """, (f'-{days} days',)).fetchone()
        
        if overall['total'] > 0:
            success_rate = overall['successes'] / overall['total']
            health_factors.append(success_rate * 40)  # Max 40 points
        
        # Factor 2: Correction frequency (fewer = better)
        if outcome_count > 0:
            correction_ratio = correction_count / outcome_count
            correction_score = max(0, 30 - (correction_ratio * 100))  # Max 30 points
            health_factors.append(correction_score)
        
        # Factor 3: Trend direction
        improving_count = sum(1 for t in trends if t['trend'] == 'improving')
        declining_count = sum(1 for t in trends if t['trend'] == 'declining')
        if trends:
            trend_score = 30 * (improving_count - declining_count + len(trends)) / (2 * len(trends))
            health_factors.append(max(0, min(30, trend_score)))
    
    health_score = sum(health_factors) if health_factors else None
    
    return {
        'period_days': days,
        'outcome_count': outcome_count,
        'correction_count': correction_count,
        'failure_patterns': failure_patterns,
        'strength_patterns': strength_patterns,
        'trends': trends,
        'health_score': round(health_score, 1) if health_score else None,
        'analyzed_at': datetime.utcnow().isoformat()
    }


def save_patterns_to_db(patterns: List[Dict[str, Any]], pattern_type: str) -> int:
    """Save detected patterns to the database."""
    saved = 0
    
    with db_session() as conn:
        for p in patterns:
            # Check if similar pattern exists
            existing = conn.execute("""
                SELECT id FROM patterns 
                WHERE description = ? AND status = 'active'
            """, (p['description'],)).fetchone()
            
            if existing:
                # Update existing
                conn.execute("""
                    UPDATE patterns 
                    SET last_seen = datetime('now'),
                        occurrence_count = occurrence_count + 1,
                        updated_at = datetime('now'),
                        confidence = ?
                    WHERE id = ?
                """, (p.get('confidence', 0.5), existing['id']))
            else:
                # Insert new
                conn.execute("""
                    INSERT INTO patterns (pattern_type, description, task_types, 
                                         first_seen, last_seen, confidence)
                    VALUES (?, ?, ?, datetime('now'), datetime('now'), ?)
                """, (
                    pattern_type,
                    p['description'],
                    p.get('task_type', ''),
                    p.get('confidence', 0.5)
                ))
                saved += 1
    
    return saved


def get_active_patterns() -> List[Dict[str, Any]]:
    """Get all active patterns from the database."""
    with db_session() as conn:
        rows = conn.execute("""
            SELECT * FROM patterns 
            WHERE status = 'active'
            ORDER BY pattern_type, confidence DESC
        """).fetchall()
        return [dict(row) for row in rows]
