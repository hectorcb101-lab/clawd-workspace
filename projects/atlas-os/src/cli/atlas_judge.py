#!/usr/bin/env python3
"""
Atlas Judgment Layer CLI

Usage:
    atlas-judge principles list [--category CAT]
    atlas-judge principle show <id>
    atlas-judge principle add --category CAT --content CONTENT --rationale RATIONALE
    atlas-judge principle update <id> [--content CONTENT] [--rationale RATIONALE]
    atlas-judge principle add-example <id> --example EXAMPLE
    atlas-judge principle deactivate <id>
    atlas-judge consult <situation>
    atlas-judge apply <principle_id> --situation SIT --decision DEC
    atlas-judge outcome <application_id> --result RESULT [--notes NOTES]
    atlas-judge stats
    atlas-judge export
    atlas-judge seed [--force]
"""
import sys
import argparse
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(src_dir))

from judgment.storage import JudgmentStorage
from judgment.models import (
    Principle, PrincipleApplication, PrincipleCategory, 
    PrincipleSource, ApplicationOutcome
)
from judgment.seed import seed_principles
from judgment.export import export_to_markdown
from judgment.integration import (
    sync_with_self_awareness, 
    get_principles_for_task,
    format_principles_for_context
)
from judgment.learning import JudgmentLearner, run_learning_cycle


def main():
    parser = argparse.ArgumentParser(
        description="Atlas Judgment Layer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ─────────────────────────────────────────────────────────────
    # principles list
    # ─────────────────────────────────────────────────────────────
    list_parser = subparsers.add_parser("principles", help="List principles")
    list_parser.add_argument("action", choices=["list"], nargs="?", default="list")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--all", "-a", action="store_true", help="Include inactive")
    
    # ─────────────────────────────────────────────────────────────
    # principle show/add/update/deactivate
    # ─────────────────────────────────────────────────────────────
    principle_parser = subparsers.add_parser("principle", help="Manage a principle")
    principle_subparsers = principle_parser.add_subparsers(dest="action")
    
    # show
    show_parser = principle_subparsers.add_parser("show", help="Show principle details")
    show_parser.add_argument("id", help="Principle ID")
    
    # add
    add_parser = principle_subparsers.add_parser("add", help="Add new principle")
    add_parser.add_argument("--category", "-c", required=True, 
                           choices=["decision", "metacognitive", "priority", "escalation"])
    add_parser.add_argument("--content", required=True, help="The principle itself")
    add_parser.add_argument("--rationale", "-r", required=True, help="Why this principle")
    add_parser.add_argument("--keywords", "-k", help="Comma-separated keywords")
    add_parser.add_argument("--priority", "-p", type=int, default=5, help="Priority 1-10")
    
    # update
    update_parser = principle_subparsers.add_parser("update", help="Update principle")
    update_parser.add_argument("id", help="Principle ID")
    update_parser.add_argument("--content", help="New content")
    update_parser.add_argument("--rationale", help="New rationale")
    update_parser.add_argument("--confidence", type=float, help="New confidence 0-1")
    update_parser.add_argument("--priority", type=int, help="New priority 1-10")
    
    # add-example
    example_parser = principle_subparsers.add_parser("add-example", help="Add example")
    example_parser.add_argument("id", help="Principle ID")
    example_parser.add_argument("--example", "-e", required=True, help="Example text")
    example_parser.add_argument("--counter", action="store_true", help="Counter-example")
    
    # deactivate
    deact_parser = principle_subparsers.add_parser("deactivate", help="Deactivate principle")
    deact_parser.add_argument("id", help="Principle ID")
    
    # ─────────────────────────────────────────────────────────────
    # consult
    # ─────────────────────────────────────────────────────────────
    consult_parser = subparsers.add_parser("consult", help="Get relevant principles")
    consult_parser.add_argument("situation", help="Describe the situation")
    consult_parser.add_argument("--limit", "-l", type=int, default=5, help="Max results")
    
    # ─────────────────────────────────────────────────────────────
    # apply
    # ─────────────────────────────────────────────────────────────
    apply_parser = subparsers.add_parser("apply", help="Log principle application")
    apply_parser.add_argument("principle_id", help="Principle ID")
    apply_parser.add_argument("--situation", "-s", required=True, help="What situation")
    apply_parser.add_argument("--how", required=True, help="How principle was applied")
    apply_parser.add_argument("--decision", "-d", required=True, help="Decision made")
    
    # ─────────────────────────────────────────────────────────────
    # outcome
    # ─────────────────────────────────────────────────────────────
    outcome_parser = subparsers.add_parser("outcome", help="Log application outcome")
    outcome_parser.add_argument("application_id", type=int, help="Application ID")
    outcome_parser.add_argument("--result", "-r", required=True,
                               choices=["success", "partial", "failure"])
    outcome_parser.add_argument("--notes", "-n", default="", help="Outcome notes")
    
    # ─────────────────────────────────────────────────────────────
    # stats
    # ─────────────────────────────────────────────────────────────
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    
    # ─────────────────────────────────────────────────────────────
    # export
    # ─────────────────────────────────────────────────────────────
    export_parser = subparsers.add_parser("export", help="Export to JUDGMENT.md")
    
    # ─────────────────────────────────────────────────────────────
    # seed
    # ─────────────────────────────────────────────────────────────
    seed_parser = subparsers.add_parser("seed", help="Seed initial principles")
    seed_parser.add_argument("--force", "-f", action="store_true", 
                            help="Overwrite existing")
    
    # ─────────────────────────────────────────────────────────────
    # sync (with self-awareness)
    # ─────────────────────────────────────────────────────────────
    sync_parser = subparsers.add_parser("sync", help="Sync with self-awareness")
    
    # ─────────────────────────────────────────────────────────────
    # task (get principles for a specific task)
    # ─────────────────────────────────────────────────────────────
    task_parser = subparsers.add_parser("task", help="Get principles for a task")
    task_parser.add_argument("description", help="Task description")
    task_parser.add_argument("--type", "-t", help="Task type (coding, research, etc.)")
    task_parser.add_argument("--stakes", "-s", default="medium",
                            choices=["low", "medium", "high", "critical"])
    
    # ─────────────────────────────────────────────────────────────
    # learn (run learning cycle)
    # ─────────────────────────────────────────────────────────────
    learn_parser = subparsers.add_parser("learn", help="Run learning analysis")
    learn_parser.add_argument("--auto-update", "-a", action="store_true",
                             help="Auto-update confidence scores")
    
    # ─────────────────────────────────────────────────────────────
    # effectiveness (show principle effectiveness)
    # ─────────────────────────────────────────────────────────────
    eff_parser = subparsers.add_parser("effectiveness", help="Show principle effectiveness")
    eff_parser.add_argument("principle_id", nargs="?", help="Specific principle (or all)")
    
    # ─────────────────────────────────────────────────────────────
    # review (show principles needing review)
    # ─────────────────────────────────────────────────────────────
    review_parser = subparsers.add_parser("review", help="Show principles needing review")
    
    # ─────────────────────────────────────────────────────────────
    # calibrate (log prediction for calibration)
    # ─────────────────────────────────────────────────────────────
    cal_parser = subparsers.add_parser("calibrate", help="Log prediction for calibration")
    cal_parser.add_argument("--domain", "-d", required=True, help="Domain (research, coding, etc.)")
    cal_parser.add_argument("--prediction", "-p", required=True, help="What you predicted")
    cal_parser.add_argument("--confidence", "-c", type=float, required=True, help="Confidence 0-1")
    cal_parser.add_argument("--outcome", "-o", required=True, help="What actually happened")
    cal_parser.add_argument("--correct", action="store_true", help="Was prediction correct?")
    
    # ─────────────────────────────────────────────────────────────
    # calibration (show calibration analysis)
    # ─────────────────────────────────────────────────────────────
    cal_analysis_parser = subparsers.add_parser("calibration", help="Show calibration analysis")
    cal_analysis_parser.add_argument("--domain", "-d", help="Filter by domain")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    storage = JudgmentStorage()
    
    try:
        if args.command == "principles":
            cmd_list_principles(storage, args)
        elif args.command == "principle":
            if args.action == "show":
                cmd_show_principle(storage, args)
            elif args.action == "add":
                cmd_add_principle(storage, args)
            elif args.action == "update":
                cmd_update_principle(storage, args)
            elif args.action == "add-example":
                cmd_add_example(storage, args)
            elif args.action == "deactivate":
                cmd_deactivate_principle(storage, args)
            else:
                principle_parser.print_help()
        elif args.command == "consult":
            cmd_consult(storage, args)
        elif args.command == "apply":
            cmd_apply(storage, args)
        elif args.command == "outcome":
            cmd_outcome(storage, args)
        elif args.command == "stats":
            cmd_stats(storage)
        elif args.command == "export":
            cmd_export(storage)
        elif args.command == "seed":
            cmd_seed(storage, args)
        elif args.command == "sync":
            cmd_sync(storage)
        elif args.command == "task":
            cmd_task(args)
        elif args.command == "learn":
            cmd_learn(storage, args)
        elif args.command == "effectiveness":
            cmd_effectiveness(storage, args)
        elif args.command == "review":
            cmd_review(storage)
        elif args.command == "calibrate":
            cmd_calibrate(storage, args)
        elif args.command == "calibration":
            cmd_calibration(storage, args)
        else:
            parser.print_help()
    finally:
        storage.close()


def cmd_list_principles(storage: JudgmentStorage, args):
    """List all principles."""
    category = None
    if args.category:
        try:
            category = PrincipleCategory(args.category)
        except ValueError:
            print(f"Invalid category: {args.category}")
            print(f"Valid: {', '.join(c.value for c in PrincipleCategory)}")
            return
    
    principles = storage.list_principles(
        category=category,
        active_only=not args.all
    )
    
    if not principles:
        print("No principles found.")
        return
    
    print(f"\n🏛️ Atlas Judgment Layer — {len(principles)} principles\n")
    
    current_cat = None
    for p in principles:
        if p.category != current_cat:
            current_cat = p.category
            cat_emoji = {"decision": "🎯", "metacognitive": "🧠", 
                        "priority": "📊", "escalation": "⚡"}.get(p.category.value, "•")
            print(f"\n{cat_emoji} {p.category.value.upper()}")
            print("-" * 40)
        
        status = "✓" if p.active else "✗"
        eff = p.effectiveness
        eff_str = f"{eff*100:.0f}%" if eff else "—"
        
        print(f"  {status} {p.id}: {_truncate(p.content, 50)}")
        print(f"      conf: {p.confidence*100:.0f}% | prio: {p.priority} | eff: {eff_str} ({p.applications_count} uses)")
    
    print()


def cmd_show_principle(storage: JudgmentStorage, args):
    """Show detailed principle."""
    p = storage.get_principle(args.id)
    if not p:
        print(f"Principle {args.id} not found.")
        return
    
    status = "Active ✓" if p.active else "Inactive ✗"
    
    print(f"\n{'='*60}")
    print(f"  {p.id} ({status})")
    print(f"  Category: {p.category.value}")
    print(f"{'='*60}\n")
    
    print(f"📜 PRINCIPLE:")
    print(f"   {p.content}\n")
    
    print(f"💡 RATIONALE:")
    print(f"   {p.rationale}\n")
    
    if p.examples:
        print(f"✅ EXAMPLES:")
        for ex in p.examples:
            print(f"   • {ex}")
        print()
    
    if p.counter_examples:
        print(f"❌ COUNTER-EXAMPLES:")
        for ex in p.counter_examples:
            print(f"   • {ex}")
        print()
    
    if p.keywords:
        print(f"🏷️  KEYWORDS: {', '.join(p.keywords)}\n")
    
    eff = p.effectiveness
    eff_str = f"{eff*100:.0f}%" if eff else "insufficient data"
    
    print(f"📊 STATS:")
    print(f"   Confidence: {p.confidence*100:.0f}%")
    print(f"   Priority: {p.priority}/10")
    print(f"   Applications: {p.applications_count}")
    print(f"   Successes: {p.success_count}")
    print(f"   Effectiveness: {eff_str}")
    print(f"   Source: {p.source.value}")
    print(f"   Created: {p.created_at.strftime('%Y-%m-%d')}")
    print()


def cmd_add_principle(storage: JudgmentStorage, args):
    """Add new principle."""
    principle_id = storage.get_next_principle_id()
    
    keywords = []
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    
    principle = Principle(
        id=principle_id,
        category=PrincipleCategory(args.category),
        content=args.content,
        rationale=args.rationale,
        keywords=keywords,
        source=PrincipleSource.MANUAL,
        priority=args.priority,
    )
    
    storage.save_principle(principle)
    print(f"✅ Created principle: {principle_id}")
    print(f"   {args.content[:60]}...")


def cmd_update_principle(storage: JudgmentStorage, args):
    """Update existing principle."""
    p = storage.get_principle(args.id)
    if not p:
        print(f"Principle {args.id} not found.")
        return
    
    updated = False
    if args.content:
        p.content = args.content
        updated = True
    if args.rationale:
        p.rationale = args.rationale
        updated = True
    if args.confidence is not None:
        p.confidence = max(0, min(1, args.confidence))
        updated = True
    if args.priority is not None:
        p.priority = max(1, min(10, args.priority))
        updated = True
    
    if updated:
        storage.save_principle(p)
        print(f"✅ Updated principle: {args.id}")
    else:
        print("Nothing to update.")


def cmd_add_example(storage: JudgmentStorage, args):
    """Add example to principle."""
    p = storage.get_principle(args.id)
    if not p:
        print(f"Principle {args.id} not found.")
        return
    
    if args.counter:
        p.counter_examples.append(args.example)
        print(f"✅ Added counter-example to {args.id}")
    else:
        p.examples.append(args.example)
        print(f"✅ Added example to {args.id}")
    
    storage.save_principle(p)


def cmd_deactivate_principle(storage: JudgmentStorage, args):
    """Deactivate a principle."""
    p = storage.get_principle(args.id)
    if not p:
        print(f"Principle {args.id} not found.")
        return
    
    storage.deactivate_principle(args.id)
    print(f"✅ Deactivated principle: {args.id}")


def cmd_consult(storage: JudgmentStorage, args):
    """Get relevant principles for a situation."""
    # Simple keyword extraction from situation
    words = args.situation.lower().split()
    # Filter to meaningful words
    stop_words = {"i", "am", "the", "a", "an", "to", "for", "of", "and", "or", "is", "it", "this", "that"}
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    if not keywords:
        keywords = words[:5]  # Fallback to first words
    
    results = storage.search_principles(keywords)[:args.limit]
    
    if not results:
        # Fallback: show top priority principles
        results = storage.list_principles()[:args.limit]
    
    print(f"\n🔍 Consulting judgment layer for: \"{args.situation}\"\n")
    print(f"Relevant principles ({len(results)}):\n")
    
    for i, p in enumerate(results, 1):
        print(f"{i}. [{p.id}] {p.content}")
        print(f"   → {_truncate(p.rationale, 70)}")
        if p.examples:
            print(f"   e.g., {p.examples[0]}")
        print()


def cmd_apply(storage: JudgmentStorage, args):
    """Log a principle application."""
    p = storage.get_principle(args.principle_id)
    if not p:
        print(f"Principle {args.principle_id} not found.")
        return
    
    application = PrincipleApplication(
        id=None,
        principle_id=args.principle_id,
        situation=args.situation,
        how_applied=args.how,
        decision_made=args.decision,
    )
    
    app_id = storage.save_application(application)
    print(f"✅ Logged application: #{app_id}")
    print(f"   Principle: {args.principle_id}")
    print(f"   Situation: {_truncate(args.situation, 50)}")
    print(f"\n   To log outcome: atlas-judge outcome {app_id} --result success|partial|failure")


def cmd_outcome(storage: JudgmentStorage, args):
    """Log outcome of an application."""
    outcome = ApplicationOutcome(args.result)
    
    try:
        storage.update_application_outcome(
            args.application_id,
            outcome,
            args.notes
        )
        print(f"✅ Logged outcome for application #{args.application_id}: {args.result}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_stats(storage: JudgmentStorage):
    """Show judgment layer statistics."""
    stats = storage.get_stats()
    
    print("\n📊 Atlas Judgment Layer Statistics\n")
    print("=" * 40)
    
    print(f"\nPrinciples:")
    print(f"   Total: {stats['principles']['total']}")
    print(f"   Active: {stats['principles']['active']}")
    print(f"   By category:")
    for cat, count in stats['principles']['by_category'].items():
        print(f"      {cat}: {count}")
    
    print(f"\nApplications: {stats['applications']}")
    print(f"Calibration records: {stats['calibration_records']}")
    
    # Show effectiveness of principles with enough data
    principles = storage.list_principles()
    effective = [(p.id, p.effectiveness) for p in principles if p.effectiveness is not None]
    
    if effective:
        print(f"\nPrinciple Effectiveness:")
        for pid, eff in sorted(effective, key=lambda x: x[1], reverse=True):
            print(f"   {pid}: {eff*100:.0f}%")
    
    print()


def cmd_export(storage: JudgmentStorage):
    """Export to JUDGMENT.md."""
    path = export_to_markdown(storage)
    print(f"✅ Exported to {path}")


def cmd_seed(storage: JudgmentStorage, args):
    """Seed initial principles."""
    result = seed_principles(storage, force=args.force)
    print(f"✅ Seeded {result['seeded']} principles")
    if result['skipped']:
        print(f"   Skipped {result['skipped']} existing (use --force to overwrite)")
    
    # Auto-export after seeding
    path = export_to_markdown(storage)
    print(f"✅ Exported to {path}")


def cmd_learn(storage: JudgmentStorage, args):
    """Run learning analysis cycle."""
    print("\n📚 Running Learning Cycle...\n")
    
    results = run_learning_cycle(storage, auto_update=args.auto_update)
    
    # Summary
    summary = results["summary"]
    print(f"📊 Last 30 days: {summary.get('applications', 0)} applications")
    if summary.get("overall_success_rate"):
        print(f"   Overall success rate: {summary['overall_success_rate']*100:.0f}%")
    if summary.get("most_used_principle"):
        print(f"   Most used: {summary['most_used_principle']} ({summary['most_used_count']}x)")
    
    # Effectiveness breakdown
    print(f"\n{'='*50}\n")
    print("Principle Effectiveness:\n")
    
    for analysis in results["effectiveness"]:
        status = analysis.get("status", "unknown")
        status_emoji = {
            "highly_effective": "🟢",
            "effective": "🟡", 
            "mixed": "🟠",
            "ineffective": "🔴",
            "insufficient_data": "⚪",
            "no_data": "⚫"
        }.get(status, "❓")
        
        score_str = ""
        if analysis.get("effectiveness_score") is not None:
            score_str = f" ({analysis['effectiveness_score']*100:.0f}%)"
        
        print(f"  {status_emoji} {analysis['principle_id']}: {status}{score_str}")
    
    # Confidence updates
    if results["confidence_updates"]:
        print(f"\n{'='*50}")
        print("\n✅ Confidence Updates Applied:\n")
        for update in results["confidence_updates"]:
            print(f"  {update['principle_id']}: {update['old_confidence']*100:.0f}% → {update['new_confidence']*100:.0f}%")
    
    # Needs review
    if results["needs_review"]:
        print(f"\n{'='*50}")
        print("\n⚠️ Principles Needing Review:\n")
        for item in results["needs_review"]:
            print(f"  🔸 {item['principle_id']}: {item.get('recommendation', 'Review needed')}")
    
    print()


def cmd_effectiveness(storage: JudgmentStorage, args):
    """Show principle effectiveness."""
    learner = JudgmentLearner(storage)
    
    if args.principle_id:
        # Single principle
        analysis = learner.analyze_principle_effectiveness(args.principle_id)
        
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        print(f"\n📊 Effectiveness Analysis: {args.principle_id}\n")
        print("=" * 50)
        
        if analysis.get("status") in ["no_data", "insufficient_data"]:
            print(f"\n{analysis['message']}")
            return
        
        print(f"\nContent: {analysis.get('principle_content', 'N/A')}")
        print(f"\nApplications: {analysis['applications']}")
        print(f"Evaluated: {analysis['evaluated']}")
        print(f"\nOutcomes:")
        for outcome, count in analysis.get("outcomes", {}).items():
            if count > 0:
                print(f"  {outcome}: {count}")
        
        print(f"\nEffectiveness Score: {analysis['effectiveness_score']*100:.0f}%")
        print(f"Status: {analysis['status']}")
        print(f"\n💡 {analysis['recommendation']}")
        
        print(f"\nConfidence: {analysis['current_confidence']*100:.0f}% → suggested {analysis['suggested_confidence']*100:.0f}%")
    else:
        # All principles
        print("\n📊 Effectiveness Overview\n")
        print("=" * 50)
        
        for analysis in learner.get_all_effectiveness():
            status = analysis.get("status", "unknown")
            status_emoji = {
                "highly_effective": "🟢",
                "effective": "🟡", 
                "mixed": "🟠",
                "ineffective": "🔴",
                "insufficient_data": "⚪",
                "no_data": "⚫"
            }.get(status, "❓")
            
            if analysis.get("effectiveness_score") is not None:
                print(f"\n{status_emoji} {analysis['principle_id']}")
                print(f"   Score: {analysis['effectiveness_score']*100:.0f}% | Status: {status}")
                print(f"   Apps: {analysis['evaluated']} evaluated | Confidence: {analysis.get('current_confidence', 0)*100:.0f}%")
            else:
                print(f"\n{status_emoji} {analysis['principle_id']}: {analysis.get('message', status)}")
    
    print()


def cmd_review(storage: JudgmentStorage):
    """Show principles needing review."""
    learner = JudgmentLearner(storage)
    needs_review = learner.get_principles_needing_review()
    
    if not needs_review:
        print("\n✅ No principles currently need review.\n")
        return
    
    print(f"\n⚠️ Principles Needing Review ({len(needs_review)})\n")
    print("=" * 50)
    
    for item in needs_review:
        status_emoji = "🔴" if item.get("status") == "ineffective" else "🟠"
        print(f"\n{status_emoji} {item['principle_id']}")
        print(f"   Status: {item.get('status')}")
        print(f"   Score: {item.get('effectiveness_score', 0)*100:.0f}%")
        print(f"   Recommendation: {item.get('recommendation')}")
    
    print()


def cmd_calibrate(storage: JudgmentStorage, args):
    """Log a prediction for calibration tracking."""
    learner = JudgmentLearner(storage)
    
    record_id = learner.log_prediction(
        domain=args.domain,
        prediction=args.prediction,
        confidence=args.confidence,
        actual_outcome=args.outcome,
        correct=args.correct
    )
    
    emoji = "✅" if args.correct else "❌"
    print(f"\n{emoji} Logged calibration record #{record_id}")
    print(f"   Domain: {args.domain}")
    print(f"   Prediction: {args.prediction}")
    print(f"   Confidence: {args.confidence*100:.0f}%")
    print(f"   Outcome: {args.outcome}")
    print(f"   Correct: {args.correct}")
    print()


def cmd_calibration(storage: JudgmentStorage, args):
    """Show calibration analysis."""
    learner = JudgmentLearner(storage)
    analysis = learner.get_calibration_analysis(domain=args.domain)
    
    print("\n🎯 Calibration Analysis\n")
    print("=" * 50)
    
    if analysis.get("status") == "insufficient_data":
        print(f"\n{analysis['message']}")
        print(f"Total predictions: {analysis.get('total', 0)}")
        print("\nLog more predictions with: atlas-judge calibrate ...")
        return
    
    status_emoji = {
        "well_calibrated": "🟢",
        "slightly_miscalibrated": "🟡",
        "poorly_calibrated": "🔴"
    }.get(analysis["status"], "❓")
    
    print(f"\n{status_emoji} Status: {analysis['status']}")
    print(f"   {analysis['message']}")
    print(f"\nTotal predictions: {analysis['total_predictions']}")
    print(f"Overall accuracy: {analysis['overall_accuracy']*100:.0f}%")
    print(f"Average calibration error: {analysis['average_calibration_error']*100:.0f}%")
    
    if analysis.get("buckets"):
        print("\nBy confidence bucket:")
        for bucket in analysis["buckets"]:
            direction = "↑" if bucket["error"] > 0 else "↓" if bucket["error"] < 0 else "="
            print(f"   {bucket['range']}: expected {bucket['expected']*100:.0f}%, actual {bucket['actual']*100:.0f}% {direction} ({bucket['samples']} samples)")
    
    print()


def cmd_sync(storage: JudgmentStorage):
    """Sync with self-awareness system."""
    from judgment.integration import get_self_awareness_patterns
    
    print("\n🔄 Syncing with Self-Awareness system...\n")
    
    # Show what patterns exist
    patterns = get_self_awareness_patterns()
    
    if patterns:
        print("📊 Detected Patterns:")
        for p in patterns:
            sig_emoji = "🚨" if p.get("significance") == "high" else "⚠️"
            if p["type"] == "correction_pattern":
                print(f"   {sig_emoji} {p['category']}: {p['count']} corrections")
            elif p["type"] == "failure_pattern":
                print(f"   {sig_emoji} {p['category']}: {p['failure_rate']*100:.0f}% failure rate ({p['failures']}/{p['total']})")
        print()
    
    results = sync_with_self_awareness(storage)
    
    print(f"   Patterns found: {results['patterns_found']}")
    print(f"   Principles proposed: {results['principles_proposed']}")
    print(f"   Principles updated: {results['principles_updated']}")
    
    if results['principles_proposed'] > 0:
        print(f"\n✅ Created {results['principles_proposed']} new principle(s) from patterns")
        # Re-export
        from judgment.export import export_to_markdown
        export_to_markdown(storage)
        print("   Updated JUDGMENT.md")
    elif patterns:
        print("\n   (Patterns exist but no new principles needed - may already be covered)")


def cmd_task(args):
    """Get principles relevant to a specific task."""
    print(f"\n🎯 Principles for: \"{args.description}\"")
    print(f"   Type: {args.type or 'unspecified'} | Stakes: {args.stakes}\n")
    
    principles = get_principles_for_task(
        args.description,
        task_type=args.type,
        stakes=args.stakes
    )
    
    if not principles:
        print("   No highly relevant principles found.")
        print("   Consider consulting general principles: atlas-judge principles list")
        return
    
    print("-" * 50)
    for p, score in principles:
        cat_emoji = {"decision": "🎯", "metacognitive": "🧠", 
                    "priority": "📊", "escalation": "⚡"}.get(p.category.value, "•")
        print(f"\n{cat_emoji} [{p.id}] (relevance: {score:.2f})")
        print(f"   {p.content}")
        if p.examples:
            print(f"   → {p.examples[0]}")
    
    print("\n" + "-" * 50)
    print("\nTo log using a principle:")
    print(f"  atlas-judge apply PRINC-XXX -s \"{_truncate(args.description, 30)}\" --how \"...\" -d \"...\"")


def _truncate(s: str, length: int) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= length:
        return s
    return s[:length-3] + "..."


if __name__ == "__main__":
    main()
