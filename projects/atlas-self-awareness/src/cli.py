#!/usr/bin/env python3
"""
Atlas Self-Awareness System - CLI

Usage:
    atlas-self init                          Initialize database
    atlas-self stats                         Show current statistics
    atlas-self log-outcome <args>            Log a task outcome
    atlas-self log-correction <args>         Log a correction
    atlas-self recent [outcomes|corrections] Show recent events
    atlas-self summary [--days N]            Show summary over time period
    atlas-self classify <description>        Test task classification
    atlas-self types                         List all task types
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_database, get_stats
from src.logger import (
    log_outcome, log_correction,
    get_recent_outcomes, get_recent_corrections,
    get_outcome_summary, get_correction_summary
)
from src.classifier import classify_task, suggest_task_type, get_all_task_types, get_subtypes
from src.analyzer import (
    compute_trends, detect_failure_patterns, detect_strength_patterns,
    run_full_analysis, save_patterns_to_db, get_active_patterns
)
from src.query import (
    query_strengths, query_weaknesses, query_blind_spots,
    query_progress, query_natural
)
from src.insights import (
    generate_insights, save_insights, get_pending_insights,
    mark_surfaced, run_insight_check, format_insight_for_display
)


def cmd_init(args):
    """Initialize the database."""
    init_database()


def cmd_stats(args):
    """Show current statistics."""
    stats = get_stats()
    
    print("\n📊 Atlas Self-Awareness Stats")
    print("=" * 40)
    print(f"  Total outcomes:     {stats['total_outcomes']}")
    
    if stats.get('outcomes_by_type'):
        for outcome, count in stats['outcomes_by_type'].items():
            emoji = {'success': '✅', 'failure': '❌', 'partial': '⚡', 'unknown': '❓'}.get(outcome, '•')
            print(f"    {emoji} {outcome}: {count}")
    
    print(f"  Total corrections:  {stats['total_corrections']}")
    print(f"  Active patterns:    {stats['active_patterns']}")
    print(f"  Pending insights:   {stats['pending_insights']}")
    print()


def cmd_log_outcome(args):
    """Log a task outcome."""
    outcome_id = log_outcome(
        task_type=args.task_type,
        outcome=args.outcome,
        confidence=args.confidence,
        feedback_source=args.source,
        task_subtype=args.subtype,
        notes=args.notes,
        context=args.context,
        auto_classify=args.auto
    )
    
    emoji = {'success': '✅', 'failure': '❌', 'partial': '⚡', 'unknown': '❓'}.get(args.outcome, '•')
    print(f"{emoji} Logged outcome #{outcome_id}: {args.task_type} → {args.outcome}")
    if args.notes:
        print(f"   Notes: {args.notes}")


def cmd_log_correction(args):
    """Log a correction."""
    correction_id = log_correction(
        user_signal=args.signal,
        correction_type=args.type,
        severity=args.severity,
        lesson=args.lesson,
        task_type=args.task_type,
        auto_classify=args.auto
    )
    
    emoji = {'minor': '📝', 'moderate': '⚠️', 'major': '🚨'}.get(args.severity, '•')
    print(f"{emoji} Logged correction #{correction_id}: {args.type} ({args.severity})")
    print(f"   Signal: \"{args.signal}\"")
    if args.lesson:
        print(f"   Lesson: {args.lesson}")


def cmd_recent(args):
    """Show recent events."""
    event_type = args.type or 'outcomes'
    limit = args.limit or 10
    
    if event_type == 'outcomes':
        events = get_recent_outcomes(limit=limit, task_type=args.task_type)
        print(f"\n📋 Recent Outcomes ({len(events)}):")
        print("-" * 60)
        for e in events:
            emoji = {'success': '✅', 'failure': '❌', 'partial': '⚡', 'unknown': '❓'}.get(e['outcome'], '•')
            subtype = f" ({e['task_subtype']})" if e.get('task_subtype') else ""
            conf = f" [{e['confidence']:.0%}]" if e.get('confidence') else ""
            print(f"  {emoji} {e['task_type']}{subtype} → {e['outcome']}{conf}")
            if e.get('notes'):
                print(f"      {e['notes'][:60]}...")
            print(f"      {e['created_at']}")
            print()
    
    elif event_type == 'corrections':
        events = get_recent_corrections(limit=limit, task_type=args.task_type)
        print(f"\n📋 Recent Corrections ({len(events)}):")
        print("-" * 60)
        for e in events:
            emoji = {'minor': '📝', 'moderate': '⚠️', 'major': '🚨'}.get(e['severity'], '•')
            task = f" [{e['task_type']}]" if e.get('task_type') else ""
            print(f"  {emoji} {e['correction_type']} ({e['severity']}){task}")
            print(f"      Signal: \"{e['user_signal']}\"")
            if e.get('lesson'):
                print(f"      Lesson: {e['lesson']}")
            print(f"      {e['created_at']}")
            print()


def cmd_summary(args):
    """Show summary over time period."""
    days = args.days or 7
    
    # Outcomes summary
    outcome_summary = get_outcome_summary(days=days)
    print(f"\n📊 Summary ({days} days)")
    print("=" * 50)
    
    print("\n🎯 Outcomes:")
    if outcome_summary['overall']:
        total = sum(outcome_summary['overall'].values())
        for outcome, count in outcome_summary['overall'].items():
            emoji = {'success': '✅', 'failure': '❌', 'partial': '⚡', 'unknown': '❓'}.get(outcome, '•')
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {emoji} {outcome}: {count} ({pct:.1f}%)")
        
        if outcome_summary.get('success_rate') is not None:
            print(f"\n  Success rate: {outcome_summary['success_rate']:.1%}")
    else:
        print("  No outcomes logged yet")
    
    if outcome_summary.get('by_task_type'):
        print("\n  By task type:")
        for task, outcomes in outcome_summary['by_task_type'].items():
            total = sum(outcomes.values())
            successes = outcomes.get('success', 0)
            rate = successes / total if total > 0 else 0
            print(f"    • {task}: {total} total, {rate:.0%} success")
    
    # Corrections summary
    correction_summary = get_correction_summary(days=days)
    print("\n⚡ Corrections:")
    if correction_summary['total'] > 0:
        print(f"  Total: {correction_summary['total']}")
        
        if correction_summary.get('by_severity'):
            print("  By severity:")
            for severity, count in correction_summary['by_severity'].items():
                emoji = {'minor': '📝', 'moderate': '⚠️', 'major': '🚨'}.get(severity, '•')
                print(f"    {emoji} {severity}: {count}")
        
        if correction_summary.get('by_type'):
            print("  By type:")
            for ctype, count in correction_summary['by_type'].items():
                print(f"    • {ctype}: {count}")
    else:
        print("  No corrections logged yet")
    
    print()


def cmd_classify(args):
    """Test task classification."""
    description = ' '.join(args.description)
    task_type, subtype, confidence = classify_task(description)
    
    print(f"\n🔍 Classification: \"{description}\"")
    print("-" * 50)
    print(f"  Task type: {task_type}")
    if subtype:
        print(f"  Subtype:   {subtype}")
    print(f"  Confidence: {confidence:.0%}")
    
    suggestions = suggest_task_type(description)
    if len(suggestions) > 1:
        print("\n  Other possibilities:")
        for task, conf in suggestions[1:]:
            print(f"    • {task} ({conf:.0%})")
    print()


def cmd_types(args):
    """List all task types."""
    print("\n📋 Task Types:")
    print("-" * 40)
    for task_type in get_all_task_types():
        subtypes = get_subtypes(task_type)
        if subtypes:
            print(f"  • {task_type}")
            for st in subtypes:
                print(f"      - {st}")
        else:
            print(f"  • {task_type}")
    print()


def cmd_analyze(args):
    """Run full pattern analysis."""
    days = args.days or 30
    
    print(f"\n🔍 Running analysis ({days} days)...")
    print("=" * 50)
    
    analysis = run_full_analysis(days=days)
    
    # Health score
    if analysis['health_score'] is not None:
        score = analysis['health_score']
        if score >= 80:
            emoji = "🟢"
            status = "Excellent"
        elif score >= 60:
            emoji = "🟡"
            status = "Good"
        elif score >= 40:
            emoji = "🟠"
            status = "Needs attention"
        else:
            emoji = "🔴"
            status = "Concerning"
        print(f"\n{emoji} Health Score: {score}/100 ({status})")
    
    print(f"\n📊 Data: {analysis['outcome_count']} outcomes, {analysis['correction_count']} corrections")
    
    # Failure patterns
    if analysis['failure_patterns']:
        print(f"\n⚠️ Failure Patterns ({len(analysis['failure_patterns'])}):")
        print("-" * 40)
        for p in analysis['failure_patterns'][:5]:
            severity_emoji = {'high': '🚨', 'medium': '⚠️', 'low': '📝'}.get(p.get('severity', 'low'), '•')
            print(f"  {severity_emoji} {p['description']}")
            if 'failure_rate' in p:
                print(f"      Failure rate: {p['failure_rate']:.0%} ({p['failures']}/{p['total_attempts']})")
            if 'count' in p and 'correction_type' in p:
                print(f"      Occurrences: {p['count']}")
            if p.get('signals'):
                print(f"      Examples: \"{p['signals'][0][:50]}...\"")
            print()
    else:
        print("\n✅ No significant failure patterns detected")
    
    # Strength patterns
    if analysis['strength_patterns']:
        print(f"\n💪 Strengths ({len(analysis['strength_patterns'])}):")
        print("-" * 40)
        for p in analysis['strength_patterns'][:5]:
            level_emoji = {'excellent': '⭐', 'strong': '💪', 'good': '👍', 'improving': '📈'}.get(p.get('strength_level', 'good'), '•')
            print(f"  {level_emoji} {p['description']}")
            if 'success_rate' in p:
                print(f"      Success rate: {p['success_rate']:.0%} ({p['successes']}/{p['total_attempts']})")
            if 'change' in p:
                print(f"      Improvement: +{p['change']:.0%}")
            print()
    else:
        print("\n📊 Not enough data to identify strengths yet")
    
    # Trends
    if analysis['trends']:
        print(f"\n📈 Trends by Task Type:")
        print("-" * 40)
        for t in analysis['trends']:
            trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️', 'insufficient_data': '❓'}.get(t['trend'], '•')
            print(f"  {trend_emoji} {t['task_type']}: {t['trend']}")
            if t['periods']:
                latest = t['periods'][-1]
                if latest['success_rate'] is not None:
                    print(f"      Latest: {latest['success_rate']:.0%} success ({latest['total']} attempts)")
        print()
    
    # Save patterns if requested
    if args.save:
        saved_failures = save_patterns_to_db(analysis['failure_patterns'], 'failure')
        saved_strengths = save_patterns_to_db(analysis['strength_patterns'], 'strength')
        print(f"💾 Saved {saved_failures} failure patterns, {saved_strengths} strength patterns")


def cmd_patterns(args):
    """Show detected patterns."""
    pattern_type = args.type
    
    if pattern_type == 'failures':
        patterns = detect_failure_patterns(days=args.days or 30)
        title = "Failure Patterns"
        emoji_map = {'high': '🚨', 'medium': '⚠️', 'low': '📝'}
    elif pattern_type == 'strengths':
        patterns = detect_strength_patterns(days=args.days or 30)
        title = "Strength Patterns"
        emoji_map = {'excellent': '⭐', 'strong': '💪', 'good': '👍', 'improving': '📈'}
    else:
        patterns = get_active_patterns()
        title = "Active Patterns (from DB)"
        emoji_map = {}
    
    print(f"\n🔍 {title}:")
    print("=" * 50)
    
    if not patterns:
        print("  No patterns found")
        return
    
    for p in patterns:
        severity = p.get('severity') or p.get('strength_level') or p.get('pattern_type', '')
        emoji = emoji_map.get(severity, '•')
        print(f"\n  {emoji} {p.get('description', 'Unknown pattern')}")
        
        if 'task_type' in p:
            print(f"      Task type: {p['task_type']}")
        if 'failure_rate' in p:
            print(f"      Failure rate: {p['failure_rate']:.0%}")
        if 'success_rate' in p:
            print(f"      Success rate: {p['success_rate']:.0%}")
        if 'count' in p:
            print(f"      Occurrences: {p['count']}")
        if 'confidence' in p:
            print(f"      Confidence: {p['confidence']:.0%}")
    print()


def cmd_trends(args):
    """Show trends over time."""
    period = args.period or 'week'
    lookback = args.lookback or 4
    task_type = args.task_type
    
    trends = compute_trends(period_type=period, lookback=lookback)
    
    if task_type:
        trends = [t for t in trends if t['task_type'] == task_type]
    
    print(f"\n📈 Trends ({period}ly, {lookback} periods):")
    print("=" * 50)
    
    if not trends:
        print("  No trend data available")
        return
    
    for t in trends:
        trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️', 'insufficient_data': '❓'}.get(t['trend'], '•')
        print(f"\n  {trend_emoji} {t['task_type']}")
        print(f"      Trend: {t['trend']}")
        if t['change']:
            print(f"      Change: {t['change']:+.0%}")
        print(f"      Total outcomes: {t['total_outcomes']}")
        
        if t['periods'] and args.verbose:
            print("      Periods:")
            for p in t['periods']:
                rate = f"{p['success_rate']:.0%}" if p['success_rate'] is not None else "N/A"
                print(f"        {p['period']}: {rate} ({p['total']} attempts)")
    print()


def cmd_strengths(args):
    """What am I good at?"""
    result = query_strengths(days=args.days or 30)
    
    print("\n💪 What Am I Good At?")
    print("=" * 50)
    print(f"\n{result['summary']}")
    
    if result['strengths']:
        print("\nStrength Patterns:")
        for s in result['strengths'][:5]:
            level = s.get('strength_level', 'good')
            emoji = {'excellent': '⭐', 'strong': '💪', 'good': '👍', 'improving': '📈'}.get(level, '•')
            print(f"  {emoji} {s['description']}")
            if 'success_rate' in s:
                print(f"      {s['success_rate']:.0%} success ({s['successes']}/{s['total_attempts']})")
    
    if result['top_performers']:
        print("\nTop Performing Areas:")
        for t in result['top_performers'][:5]:
            rate = t['successes'] / t['total'] if t['total'] > 0 else 0
            print(f"  • {t['task_type']}: {rate:.0%} ({t['total']} attempts)")
    print()


def cmd_weaknesses(args):
    """What do I struggle with?"""
    result = query_weaknesses(days=args.days or 30)
    
    print("\n⚠️ What Do I Struggle With?")
    print("=" * 50)
    print(f"\n{result['summary']}")
    
    if result['failure_patterns']:
        print("\nFailure Patterns:")
        for p in result['failure_patterns'][:5]:
            severity = p.get('severity', 'low')
            emoji = {'high': '🚨', 'medium': '⚠️', 'low': '📝'}.get(severity, '•')
            print(f"  {emoji} {p['description']}")
    
    if result['weak_areas']:
        print("\nWeak Areas:")
        for w in result['weak_areas'][:5]:
            failures = w['failures'] + w['partials'] * 0.5
            print(f"  • {w['task_type']}: {w['failures']} failures, {w['partials']} partials")
    
    if result['correction_types']:
        print("\nCorrection Types:")
        for ctype, count in result['correction_types'].items():
            print(f"  • {ctype}: {count}")
    print()


def cmd_blind_spots(args):
    """What am I missing about myself?"""
    result = query_blind_spots(days=args.days or 30)
    
    print("\n🔍 What Are My Blind Spots?")
    print("=" * 50)
    print(f"\n{result['summary']}")
    
    if result['blind_spots']:
        print(f"\nFound {result['count']} blind spot(s):")
        for b in result['blind_spots']:
            type_emoji = {
                'uncertain_assessment': '❓',
                'outcome_unclear': '🌫️',
                'overconfidence': '📈',
                'underconfidence': '📉',
                'unlogged_failures': '📝'
            }.get(b['type'], '•')
            
            print(f"\n  {type_emoji} {b['description']}")
            if b.get('suggestion'):
                print(f"      → {b['suggestion']}")
    else:
        print("\n  ✅ No obvious blind spots detected!")
    print()


def cmd_progress(args):
    """Am I getting better?"""
    result = query_progress(task_type=args.task_type, days=args.days or 30)
    
    print(f"\n📈 {result['query']}")
    print("=" * 50)
    print(f"\n{result['summary']}")
    
    if result['improving']:
        print("\n🟢 Improving:")
        for t in result['improving']:
            change = f" (+{t['change']:.0%})" if t.get('change') else ""
            print(f"  • {t['task_type']}{change}")
    
    if result['declining']:
        print("\n🔴 Declining:")
        for t in result['declining']:
            change = f" ({t['change']:.0%})" if t.get('change') else ""
            print(f"  • {t['task_type']}{change}")
    
    if result['stable']:
        print("\n🟡 Stable:")
        for t in result['stable']:
            print(f"  • {t['task_type']}")
    print()


def cmd_ask(args):
    """Ask a natural language question about myself."""
    question = ' '.join(args.question)
    result = query_natural(question, days=args.days or 30)
    
    print(f"\n🧠 \"{question}\"")
    print("=" * 50)
    
    if result.get('note'):
        print(f"\n⚠️ {result['note']}")
    
    if result.get('detected_query_type'):
        print(f"\nDetected query type: {result['detected_query_type']}")
    
    # Display based on what was returned
    if result.get('summary'):
        print(f"\n{result['summary']}")
    
    if result.get('health_score'):
        print(f"\nHealth Score: {result['health_score']}/100")
    
    if result.get('strengths'):
        print(f"\nStrengths: {len(result['strengths'])} identified")
    
    if result.get('failure_patterns'):
        print(f"Failure patterns: {len(result['failure_patterns'])} found")
    
    if result.get('blind_spots'):
        print(f"Blind spots: {len(result['blind_spots'])} detected")
    
    print()


def cmd_insights(args):
    """Show pending insights."""
    if args.generate:
        print("\n🔄 Generating insights...")
        insights = generate_insights(days=args.days or 30, force=args.force)
        saved = save_insights(insights)
        print(f"   Generated {len(insights)} insights, saved {saved} new")
    
    pending = get_pending_insights(limit=args.limit or 10)
    
    print(f"\n💡 Pending Insights ({len(pending)}):")
    print("=" * 50)
    
    if not pending:
        print("\n  ✅ No pending insights!")
        return
    
    ids_shown = []
    for i in pending:
        print(f"\n{format_insight_for_display(i)}")
        print(f"   [{i['insight_type']}] Created: {i['created_at']}")
        ids_shown.append(i['id'])
    
    if args.mark_seen and ids_shown:
        marked = mark_surfaced(ids_shown)
        print(f"\n✓ Marked {marked} insights as seen")
    
    print()


def cmd_check(args):
    """Run insight check (for heartbeat integration)."""
    print("\n🔍 Running insight check...")
    
    result = run_insight_check()
    
    print(f"\n📊 Results:")
    print(f"   New insights generated: {result['new_insights']}")
    print(f"   Saved to database: {result['saved']}")
    print(f"   Total pending: {result['pending_count']}")
    print(f"   Critical/High priority: {result['critical_count']}")
    
    if result['should_alert']:
        print("\n🚨 ALERT - Critical insights require attention:")
        for i in result['critical_insights']:
            print(f"\n{format_insight_for_display(i)}")
    else:
        print("\n✅ No critical insights")
    
    # Output for heartbeat parsing
    if args.json:
        import json
        print(f"\n---JSON---\n{json.dumps(result, default=str)}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Atlas Self-Awareness System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.set_defaults(func=cmd_init)
    
    # stats
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # log-outcome
    outcome_parser = subparsers.add_parser('log-outcome', help='Log a task outcome')
    outcome_parser.add_argument('task_type', help='Type of task (coding, research, etc.)')
    outcome_parser.add_argument('outcome', choices=['success', 'failure', 'partial', 'unknown'],
                               help='Outcome of the task')
    outcome_parser.add_argument('--confidence', '-c', type=float, default=0.5,
                               help='Confidence in this classification (0.0-1.0)')
    outcome_parser.add_argument('--source', '-s', choices=['self', 'user', 'system'],
                               default='self', help='Source of feedback')
    outcome_parser.add_argument('--subtype', help='Task subtype')
    outcome_parser.add_argument('--notes', '-n', help='Notes about the outcome')
    outcome_parser.add_argument('--context', help='Context about the task')
    outcome_parser.add_argument('--auto', '-a', action='store_true',
                               help='Auto-classify from notes/context')
    outcome_parser.set_defaults(func=cmd_log_outcome)
    
    # log-correction
    correction_parser = subparsers.add_parser('log-correction', help='Log a correction')
    correction_parser.add_argument('signal', help='What the user said (the correction)')
    correction_parser.add_argument('--type', '-t', choices=['factual', 'approach', 'style', 'other'],
                                  default='other', help='Type of correction')
    correction_parser.add_argument('--severity', '-s', choices=['minor', 'moderate', 'major'],
                                  default='moderate', help='Severity of the correction')
    correction_parser.add_argument('--lesson', '-l', help='What was learned')
    correction_parser.add_argument('--task-type', help='Task type being corrected')
    correction_parser.add_argument('--auto', '-a', action='store_true',
                                  help='Auto-classify task type from signal')
    correction_parser.set_defaults(func=cmd_log_correction)
    
    # recent
    recent_parser = subparsers.add_parser('recent', help='Show recent events')
    recent_parser.add_argument('type', nargs='?', choices=['outcomes', 'corrections'],
                              help='Type of events to show')
    recent_parser.add_argument('--limit', '-l', type=int, default=10,
                              help='Number of events to show')
    recent_parser.add_argument('--task-type', '-t', help='Filter by task type')
    recent_parser.set_defaults(func=cmd_recent)
    
    # summary
    summary_parser = subparsers.add_parser('summary', help='Show summary')
    summary_parser.add_argument('--days', '-d', type=int, default=7,
                               help='Number of days to summarize')
    summary_parser.set_defaults(func=cmd_summary)
    
    # classify
    classify_parser = subparsers.add_parser('classify', help='Test task classification')
    classify_parser.add_argument('description', nargs='+', help='Task description')
    classify_parser.set_defaults(func=cmd_classify)
    
    # types
    types_parser = subparsers.add_parser('types', help='List all task types')
    types_parser.set_defaults(func=cmd_types)
    
    # analyze
    analyze_parser = subparsers.add_parser('analyze', help='Run full pattern analysis')
    analyze_parser.add_argument('--days', '-d', type=int, default=30,
                               help='Number of days to analyze')
    analyze_parser.add_argument('--save', '-s', action='store_true',
                               help='Save detected patterns to database')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # patterns
    patterns_parser = subparsers.add_parser('patterns', help='Show detected patterns')
    patterns_parser.add_argument('type', nargs='?', choices=['failures', 'strengths', 'all'],
                                default='all', help='Type of patterns to show')
    patterns_parser.add_argument('--days', '-d', type=int, default=30,
                                help='Number of days to analyze')
    patterns_parser.set_defaults(func=cmd_patterns)
    
    # trends
    trends_parser = subparsers.add_parser('trends', help='Show trends over time')
    trends_parser.add_argument('--period', '-p', choices=['day', 'week', 'month'],
                              default='week', help='Period type')
    trends_parser.add_argument('--lookback', '-l', type=int, default=4,
                              help='Number of periods to look back')
    trends_parser.add_argument('--task-type', '-t', help='Filter by task type')
    trends_parser.add_argument('--verbose', '-v', action='store_true',
                              help='Show detailed period breakdown')
    trends_parser.set_defaults(func=cmd_trends)
    
    # strengths
    strengths_parser = subparsers.add_parser('strengths', help='What am I good at?')
    strengths_parser.add_argument('--days', '-d', type=int, default=30,
                                 help='Number of days to analyze')
    strengths_parser.set_defaults(func=cmd_strengths)
    
    # weaknesses
    weaknesses_parser = subparsers.add_parser('weaknesses', help='What do I struggle with?')
    weaknesses_parser.add_argument('--days', '-d', type=int, default=30,
                                  help='Number of days to analyze')
    weaknesses_parser.set_defaults(func=cmd_weaknesses)
    
    # blind-spots
    blind_spots_parser = subparsers.add_parser('blind-spots', help='What am I missing?')
    blind_spots_parser.add_argument('--days', '-d', type=int, default=30,
                                   help='Number of days to analyze')
    blind_spots_parser.set_defaults(func=cmd_blind_spots)
    
    # progress
    progress_parser = subparsers.add_parser('progress', help='Am I getting better?')
    progress_parser.add_argument('--task-type', '-t', help='Filter by task type')
    progress_parser.add_argument('--days', '-d', type=int, default=30,
                                help='Number of days to analyze')
    progress_parser.set_defaults(func=cmd_progress)
    
    # ask (natural language)
    ask_parser = subparsers.add_parser('ask', help='Ask a question about myself')
    ask_parser.add_argument('question', nargs='+', help='Natural language question')
    ask_parser.add_argument('--days', '-d', type=int, default=30,
                           help='Number of days to analyze')
    ask_parser.set_defaults(func=cmd_ask)
    
    # insights
    insights_parser = subparsers.add_parser('insights', help='Show pending insights')
    insights_parser.add_argument('--generate', '-g', action='store_true',
                                help='Generate new insights first')
    insights_parser.add_argument('--force', '-f', action='store_true',
                                help='Force regeneration even if recent')
    insights_parser.add_argument('--days', '-d', type=int, default=30,
                                help='Days to analyze for generation')
    insights_parser.add_argument('--limit', '-l', type=int, default=10,
                                help='Max insights to show')
    insights_parser.add_argument('--mark-seen', '-m', action='store_true',
                                help='Mark shown insights as surfaced')
    insights_parser.set_defaults(func=cmd_insights)
    
    # check (heartbeat integration)
    check_parser = subparsers.add_parser('check', help='Run insight check (for heartbeat)')
    check_parser.add_argument('--json', '-j', action='store_true',
                             help='Output JSON for parsing')
    check_parser.set_defaults(func=cmd_check)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
