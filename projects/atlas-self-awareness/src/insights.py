"""
Atlas Self-Awareness System - Proactive Insight Engine

Generates and surfaces insights without being asked.
This is how I notice things about myself before they become problems.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from .database import db_session
from .analyzer import (
    detect_failure_patterns, detect_strength_patterns,
    compute_trends, run_full_analysis
)
from .query import query_blind_spots
from .models import InsightType, Priority


def generate_insights(days: int = 30, force: bool = False) -> List[Dict[str, Any]]:
    """
    Generate new insights based on current data.
    
    Checks for:
    - New failure patterns
    - Declining trends
    - Blind spots
    - Milestones (improvements)
    - Warnings (about to repeat mistakes)
    """
    insights = []
    
    # Get current analysis
    failure_patterns = detect_failure_patterns(days=days)
    strength_patterns = detect_strength_patterns(days=days)
    trends = compute_trends(period_type='week', lookback=4)
    blind_spots = query_blind_spots(days=days)['blind_spots']
    
    with db_session() as conn:
        # Check what insights we've already surfaced recently
        recent_insights = conn.execute("""
            SELECT message FROM insights 
            WHERE created_at >= datetime('now', '-7 days')
        """).fetchall()
        recent_messages = {r['message'] for r in recent_insights}
        
        # 1. High-severity failure patterns → Critical insights
        for p in failure_patterns:
            if p.get('severity') == 'high':
                message = f"🚨 High failure rate in {p.get('task_type', 'unknown')}: {p['description']}"
                if message not in recent_messages or force:
                    insights.append({
                        'type': InsightType.WARNING.value,
                        'priority': Priority.HIGH.value,
                        'message': message,
                        'evidence': json.dumps(p),
                        'actionable': True,
                        'suggested_action': f"Review recent {p.get('task_type', '')} tasks and identify root cause"
                    })
        
        # 2. Declining trends → Regression warnings
        for t in trends:
            if t['trend'] == 'declining' and t.get('change') and t['change'] < -0.15:
                message = f"📉 Performance declining in {t['task_type']} ({t['change']:.0%} over recent weeks)"
                if message not in recent_messages or force:
                    insights.append({
                        'type': InsightType.REGRESSION.value,
                        'priority': Priority.MEDIUM.value,
                        'message': message,
                        'evidence': json.dumps(t),
                        'actionable': True,
                        'suggested_action': f"Investigate what changed in {t['task_type']} workflow"
                    })
        
        # 3. Improving trends → Positive reinforcement
        for t in trends:
            if t['trend'] == 'improving' and t.get('change') and t['change'] > 0.15:
                message = f"📈 Great progress in {t['task_type']}! (+{t['change']:.0%} improvement)"
                if message not in recent_messages or force:
                    insights.append({
                        'type': InsightType.IMPROVEMENT.value,
                        'priority': Priority.LOW.value,
                        'message': message,
                        'evidence': json.dumps(t),
                        'actionable': False,
                        'suggested_action': None
                    })
        
        # 4. Blind spots → Self-awareness gaps
        for b in blind_spots:
            if b['type'] == 'overconfidence':
                message = f"⚠️ Possible overconfidence in {b['task_type']}: self-assessment higher than user feedback"
                priority = Priority.HIGH.value
            elif b['type'] == 'uncertain_assessment':
                message = f"❓ Low confidence in {b['task_type']} outcomes - need clearer success criteria"
                priority = Priority.MEDIUM.value
            else:
                message = f"🔍 Blind spot: {b['description']}"
                priority = Priority.LOW.value
            
            if message not in recent_messages or force:
                insights.append({
                    'type': InsightType.BLIND_SPOT.value,
                    'priority': priority,
                    'message': message,
                    'evidence': json.dumps(b),
                    'actionable': True,
                    'suggested_action': b.get('suggestion', 'Investigate and address')
                })
        
        # 5. Major corrections not yet processed
        unprocessed_major = conn.execute("""
            SELECT c.* FROM corrections c
            LEFT JOIN insights i ON i.evidence LIKE '%' || c.id || '%'
            WHERE c.severity = 'major'
            AND c.created_at >= datetime('now', '-7 days')
            AND i.id IS NULL
        """).fetchall()
        
        for c in unprocessed_major:
            message = f"🚨 Major correction received: \"{c['user_signal'][:50]}...\""
            insights.append({
                'type': InsightType.WARNING.value,
                'priority': Priority.CRITICAL.value,
                'message': message,
                'evidence': json.dumps({'correction_id': c['id'], 'lesson': c['lesson']}),
                'actionable': True,
                'suggested_action': c['lesson'] or "Review and learn from this correction"
            })
        
        # 6. Milestone detection (e.g., 10 successes in a row)
        streak_check = conn.execute("""
            SELECT task_type, COUNT(*) as streak
            FROM (
                SELECT task_type, outcome,
                       ROW_NUMBER() OVER (PARTITION BY task_type ORDER BY created_at DESC) as rn
                FROM outcomes
                WHERE created_at >= datetime('now', '-30 days')
            )
            WHERE outcome = 'success' AND rn <= 10
            GROUP BY task_type
            HAVING streak >= 5
        """).fetchall()
        
        for s in streak_check:
            message = f"🎯 {s['streak']}-success streak in {s['task_type']}!"
            if message not in recent_messages or force:
                insights.append({
                    'type': InsightType.TIP.value,
                    'priority': Priority.LOW.value,
                    'message': message,
                    'evidence': json.dumps({'task_type': s['task_type'], 'streak': s['streak']}),
                    'actionable': False,
                    'suggested_action': None
                })
    
    # Sort by priority
    priority_order = {
        Priority.CRITICAL.value: 0,
        Priority.HIGH.value: 1,
        Priority.MEDIUM.value: 2,
        Priority.LOW.value: 3
    }
    insights.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return insights


def save_insights(insights: List[Dict[str, Any]]) -> int:
    """Save generated insights to database."""
    saved = 0
    
    with db_session() as conn:
        for i in insights:
            # Check for duplicates
            existing = conn.execute("""
                SELECT id FROM insights 
                WHERE message = ? AND created_at >= datetime('now', '-1 day')
            """, (i['message'],)).fetchone()
            
            if not existing:
                conn.execute("""
                    INSERT INTO insights (insight_type, message, evidence, priority,
                                         actionable, suggested_action)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    i['type'],
                    i['message'],
                    i.get('evidence'),
                    i['priority'],
                    1 if i.get('actionable') else 0,
                    i.get('suggested_action')
                ))
                saved += 1
    
    return saved


def get_pending_insights(limit: int = 10) -> List[Dict[str, Any]]:
    """Get insights that haven't been surfaced yet."""
    with db_session() as conn:
        rows = conn.execute("""
            SELECT * FROM insights
            WHERE surfaced = 0
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def mark_surfaced(insight_ids: List[int]) -> int:
    """Mark insights as surfaced."""
    if not insight_ids:
        return 0
    
    with db_session() as conn:
        placeholders = ','.join('?' * len(insight_ids))
        conn.execute(f"""
            UPDATE insights
            SET surfaced = 1, surfaced_at = datetime('now')
            WHERE id IN ({placeholders})
        """, insight_ids)
        return len(insight_ids)


def get_insight_for_task(task_type: str) -> Optional[Dict[str, Any]]:
    """
    Get relevant insight before starting a task.
    
    This is the "right before you repeat a mistake" intervention.
    """
    with db_session() as conn:
        # Check for recent failures in this task type
        recent_failures = conn.execute("""
            SELECT COUNT(*) as count FROM outcomes
            WHERE task_type = ? 
            AND outcome IN ('failure', 'partial')
            AND created_at >= datetime('now', '-7 days')
        """, (task_type,)).fetchone()
        
        if recent_failures['count'] >= 2:
            # Get the pattern
            pattern = conn.execute("""
                SELECT notes FROM outcomes
                WHERE task_type = ?
                AND outcome = 'failure'
                ORDER BY created_at DESC
                LIMIT 1
            """, (task_type,)).fetchone()
            
            return {
                'type': 'pre_task_warning',
                'message': f"⚠️ Heads up: {recent_failures['count']} recent issues with {task_type}",
                'detail': pattern['notes'] if pattern else None,
                'task_type': task_type
            }
        
        # Check for relevant corrections
        correction = conn.execute("""
            SELECT user_signal, lesson FROM corrections
            WHERE task_type = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (task_type,)).fetchone()
        
        if correction:
            return {
                'type': 'reminder',
                'message': f"💡 Remember: {correction['lesson'] or correction['user_signal'][:50]}",
                'task_type': task_type
            }
    
    return None


def run_insight_check() -> Dict[str, Any]:
    """
    Run a full insight check - suitable for heartbeat integration.
    
    Returns summary of what was found and any critical items.
    """
    # Generate new insights
    insights = generate_insights(days=30)
    
    # Save them
    saved = save_insights(insights)
    
    # Get pending (including just-saved)
    pending = get_pending_insights(limit=5)
    
    # Identify critical/high priority
    critical = [i for i in pending if i['priority'] in ('critical', 'high')]
    
    return {
        'new_insights': len(insights),
        'saved': saved,
        'pending_count': len(pending),
        'critical_count': len(critical),
        'critical_insights': critical,
        'should_alert': len(critical) > 0,
        'checked_at': datetime.utcnow().isoformat()
    }


def format_insight_for_display(insight: Dict[str, Any]) -> str:
    """Format an insight for human-readable display."""
    priority_emoji = {
        'critical': '🚨',
        'high': '⚠️',
        'medium': '📋',
        'low': '💡'
    }
    
    emoji = priority_emoji.get(insight.get('priority', 'low'), '•')
    message = insight.get('message', 'Unknown insight')
    
    lines = [f"{emoji} {message}"]
    
    if insight.get('suggested_action'):
        lines.append(f"   → {insight['suggested_action']}")
    
    return '\n'.join(lines)
