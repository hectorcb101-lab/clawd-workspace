#!/usr/bin/env python3
"""
CLI for Atlas Self-Modification System.

Usage:
    atlas-mod propose <file> --content "..." --reason "..."
    atlas-mod list [--status pending|approved|applied|rejected]
    atlas-mod show <id>
    atlas-mod apply <id>
    atlas-mod approve <id>
    atlas-mod reject <id> --reason "..."
    atlas-mod rollback <id> --reason "..."
    atlas-mod history [--file <path>] [--days N]
    atlas-mod stats
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.service import get_service, ModificationService
from src.models import Status, ModificationType, Source, RiskLevel, AppliedBy


def format_modification(mod, verbose: bool = False) -> str:
    """Format a modification for display."""
    status_emoji = {
        Status.PENDING: "⏳",
        Status.APPROVED: "✅",
        Status.APPLIED: "🟢",
        Status.REJECTED: "❌",
        Status.ROLLED_BACK: "⏪",
        Status.EXPIRED: "⌛",
    }
    
    risk_emoji = {
        RiskLevel.LOW: "🟢",
        RiskLevel.MEDIUM: "🟡",
        RiskLevel.HIGH: "🟠",
        RiskLevel.CRITICAL: "🔴",
    }
    
    lines = [
        f"{status_emoji.get(mod.status, '?')} {mod.id}",
        f"   Target: {mod.target_file}",
        f"   Type: {mod.modification_type.value} | Risk: {risk_emoji.get(mod.risk_level, '?')} {mod.risk_level.value} ({mod.risk_score})",
        f"   Status: {mod.status.value}",
        f"   Created: {mod.created_at.strftime('%Y-%m-%d %H:%M')}",
    ]
    
    if verbose:
        lines.append(f"   Reason: {mod.reason}")
        if mod.target_section:
            lines.append(f"   Section: {mod.target_section}")
        if mod.source != Source.MANUAL:
            lines.append(f"   Source: {mod.source.value} ({mod.source_id})")
        lines.append(f"   Confidence: {mod.confidence:.0%}")
        if mod.requires_approval:
            lines.append(f"   ⚠️  Requires approval")
        if mod.applied_at:
            lines.append(f"   Applied: {mod.applied_at.strftime('%Y-%m-%d %H:%M')} by {mod.applied_by.value if mod.applied_by else 'unknown'}")
        if mod.rejected_reason:
            lines.append(f"   Rejection: {mod.rejected_reason}")
        lines.append(f"   Content preview: {mod.content[:100]}...")
    
    return "\n".join(lines)


def cmd_propose(args, svc: ModificationService):
    """Propose a new modification."""
    try:
        mod_type = ModificationType(args.type)
    except ValueError:
        print(f"❌ Invalid modification type: {args.type}")
        print(f"   Valid types: append, edit, delete, restructure")
        sys.exit(1)
    
    try:
        mod, explanation = svc.propose(
            target_file=args.file,
            modification_type=mod_type,
            content=args.content,
            reason=args.reason,
            target_section=args.section,
            evidence=args.evidence,
            confidence=args.confidence,
        )
        
        print(f"✅ Modification proposed: {mod.id}")
        print()
        print(format_modification(mod, verbose=True))
        print()
        print("Risk Assessment:")
        print(explanation)
        print()
        
        if mod.requires_approval:
            print(f"⚠️  This modification requires approval.")
            print(f"   Run: atlas-mod approve {mod.id}")
        else:
            print(f"Ready to apply.")
            print(f"   Run: atlas-mod apply {mod.id}")
    
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_list(args, svc: ModificationService):
    """List modifications."""
    status = None
    if args.status:
        try:
            status = Status(args.status)
        except ValueError:
            print(f"❌ Invalid status: {args.status}")
            sys.exit(1)
    
    mods = svc.list_all(status=status, limit=args.limit)
    
    if not mods:
        print("No modifications found.")
        return
    
    print(f"Found {len(mods)} modification(s):\n")
    for mod in mods:
        print(format_modification(mod, verbose=args.verbose))
        print()


def cmd_show(args, svc: ModificationService):
    """Show modification details."""
    try:
        details = svc.show(args.id)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    mod = details['modification']
    log = details['log']
    
    print(format_modification(mod, verbose=True))
    print()
    print("Risk Assessment:")
    print(details['risk_explanation'])
    print()
    
    if log:
        print("Application Log:")
        print(f"   Applied: {log.applied_at.strftime('%Y-%m-%d %H:%M')}")
        if log.git_commit_hash:
            print(f"   Git commit: {log.git_commit_hash[:8]}")
        if log.reverted_at:
            print(f"   Reverted: {log.reverted_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Revert reason: {log.revert_reason}")
        print()
        print("Diff:")
        print(log.diff)
    
    if details['outcomes']:
        print("\nOutcomes:")
        for outcome in details['outcomes']:
            print(f"   {outcome.metric_name}: {outcome.before_value} → {outcome.after_value}")


def cmd_apply(args, svc: ModificationService):
    """Apply a modification."""
    try:
        log = svc.apply(args.id, by=AppliedBy.HUMAN)
        
        print(f"✅ Modification applied: {args.id}")
        print()
        print("Changes made:")
        print(log.diff)
        
        if log.git_commit_hash:
            print(f"\nGit commit: {log.git_commit_hash[:8]}")
    
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_approve(args, svc: ModificationService):
    """Approve a modification."""
    try:
        svc.approve(args.id)
        print(f"✅ Modification approved: {args.id}")
        print(f"   Run: atlas-mod apply {args.id}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_reject(args, svc: ModificationService):
    """Reject a modification."""
    try:
        svc.reject(args.id, args.reason)
        print(f"❌ Modification rejected: {args.id}")
        print(f"   Reason: {args.reason}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_rollback(args, svc: ModificationService):
    """Rollback a modification."""
    try:
        svc.rollback(args.id, args.reason)
        print(f"⏪ Modification rolled back: {args.id}")
        print(f"   Reason: {args.reason}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_history(args, svc: ModificationService):
    """Show modification history."""
    mods = svc.get_history(
        file_path=args.file,
        days=args.days,
        limit=args.limit
    )
    
    if not mods:
        print("No modifications in history.")
        return
    
    print(f"Modification history ({len(mods)} entries):\n")
    for mod in mods:
        print(format_modification(mod, verbose=args.verbose))
        print()


def cmd_stats(args, svc: ModificationService):
    """Show statistics."""
    stats = svc.stats()
    
    print("📊 Atlas Self-Modification Statistics")
    print("=" * 40)
    print(f"Total requests: {stats.get('total_requests', 0)}")
    print(f"Active modifications: {stats.get('active_modifications', 0)}")
    print(f"Rollbacks: {stats.get('rollbacks', 0)}")
    print(f"Active rules: {stats.get('active_rules', 0)}")
    print()
    
    by_status = stats.get('requests_by_status', {})
    if by_status:
        print("By status:")
        for status, count in by_status.items():
            print(f"   {status}: {count}")


def cmd_from_correction(args, svc: ModificationService):
    """Create proposal from a correction."""
    from .integration import propose_from_correction
    
    mod, msg = propose_from_correction(args.id)
    if mod:
        print(f"✅ {msg}")
        print()
        print(format_modification(mod, verbose=True))
    else:
        print(f"❌ {msg}")
        sys.exit(1)


def cmd_from_insight(args, svc: ModificationService):
    """Create proposal from an insight."""
    from .integration import propose_from_insight
    
    mod, msg = propose_from_insight(args.id)
    if mod:
        print(f"✅ {msg}")
        print()
        print(format_modification(mod, verbose=True))
    else:
        print(f"❌ {msg}")
        sys.exit(1)


def cmd_process(args, svc: ModificationService):
    """Process pending corrections and insights."""
    from .integration import (
        process_pending_corrections, process_pending_insights,
        get_unprocessed_corrections, get_unprocessed_insights
    )
    
    if args.source in ('corrections', 'all'):
        corrections = get_unprocessed_corrections(args.limit)
        print(f"Found {len(corrections)} corrections with lessons")
        
        if corrections and not args.dry_run:
            results = process_pending_corrections(args.limit)
            for corr_id, msg in results:
                print(f"  [{corr_id}] {msg}")
        elif corrections:
            for c in corrections:
                print(f"  [{c.id}] {c.correction_type.value}: {c.lesson[:60]}...")
    
    if args.source in ('insights', 'all'):
        insights = get_unprocessed_insights(args.limit)
        print(f"Found {len(insights)} actionable insights")
        
        if insights and not args.dry_run:
            results = process_pending_insights(args.limit)
            for ins_id, msg in results:
                print(f"  [{ins_id}] {msg}")
        elif insights:
            for i in insights:
                print(f"  [{i.id}] {i.insight_type.value}: {i.message[:60]}...")


def cmd_rules(args, svc: ModificationService):
    """Manage modification rules."""
    from .repository import RuleRepository
    from .models import ModificationRule, TriggerType, RiskLevel
    
    rules_repo = RuleRepository()
    
    if args.rules_action == 'list':
        rules = rules_repo.list_active()
        if not rules:
            print("No active rules.")
            return
        
        print(f"Active rules ({len(rules)}):\n")
        for rule in rules:
            print(f"📋 {rule.id}: {rule.name}")
            print(f"   Trigger: {rule.trigger_type.value} = '{rule.trigger_match}'")
            print(f"   Target: {rule.target_file}")
            if rule.target_section:
                print(f"   Section: {rule.target_section}")
            print(f"   Auto-apply: {'Yes' if rule.auto_apply else 'No'}")
            print(f"   Triggered: {rule.trigger_count} times")
            print()
    
    elif args.rules_action == 'add':
        try:
            trigger_type = TriggerType(args.trigger_type)
        except ValueError:
            print(f"❌ Invalid trigger type: {args.trigger_type}")
            print(f"   Valid: correction_type, insight_type, pattern, keyword")
            sys.exit(1)
        
        rule = ModificationRule(
            name=args.name,
            trigger_type=trigger_type,
            trigger_match=args.trigger_match,
            target_file=args.target_file,
            action_template=args.template,
            description=args.description,
            target_section=args.section,
            auto_apply=args.auto_apply,
        )
        
        rule_id = rules_repo.save(rule)
        print(f"✅ Rule created: {rule_id}")
    
    elif args.rules_action == 'disable':
        if rules_repo.set_active(args.rule_id, False):
            print(f"✅ Rule disabled: {args.rule_id}")
        else:
            print(f"❌ Rule not found: {args.rule_id}")
            sys.exit(1)
    
    elif args.rules_action == 'enable':
        if rules_repo.set_active(args.rule_id, True):
            print(f"✅ Rule enabled: {args.rule_id}")
        else:
            print(f"❌ Rule not found: {args.rule_id}")
            sys.exit(1)


def cmd_pending(args, svc: ModificationService):
    """Show pending modifications (shortcut for list --status pending)."""
    mods = svc.list_pending(limit=args.limit)
    
    if not mods:
        print("No pending modifications. 👍")
        return
    
    print(f"⏳ {len(mods)} pending modification(s):\n")
    for mod in mods:
        print(format_modification(mod, verbose=True))
        print()
        if mod.requires_approval:
            print(f"   → atlas-mod approve {mod.id}")
        else:
            print(f"   → atlas-mod apply {mod.id}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Atlas Self-Modification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  atlas-mod propose AGENTS.md --type append --content "New rule" --reason "Adding rule"
  atlas-mod list --status pending
  atlas-mod show MOD-20260201-001
  atlas-mod approve MOD-20260201-001
  atlas-mod apply MOD-20260201-001
  atlas-mod rollback MOD-20260201-001 --reason "Didn't help"
  atlas-mod stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # propose
    p_propose = subparsers.add_parser('propose', help='Propose a new modification')
    p_propose.add_argument('file', help='Target file path')
    p_propose.add_argument('--type', '-t', default='append', 
                          choices=['append', 'edit', 'delete', 'restructure'],
                          help='Modification type')
    p_propose.add_argument('--content', '-c', required=True, help='Content to add/change')
    p_propose.add_argument('--reason', '-r', required=True, help='Reason for modification')
    p_propose.add_argument('--section', '-s', help='Target section within file')
    p_propose.add_argument('--evidence', '-e', help='Evidence supporting this change')
    p_propose.add_argument('--confidence', type=float, default=0.5, help='Confidence (0.0-1.0)')
    
    # list
    p_list = subparsers.add_parser('list', help='List modifications')
    p_list.add_argument('--status', choices=['pending', 'approved', 'applied', 'rejected', 'rolled_back', 'expired'])
    p_list.add_argument('--limit', type=int, default=20)
    p_list.add_argument('--verbose', '-v', action='store_true')
    
    # pending (shortcut)
    p_pending = subparsers.add_parser('pending', help='Show pending modifications')
    p_pending.add_argument('--limit', type=int, default=20)
    
    # show
    p_show = subparsers.add_parser('show', help='Show modification details')
    p_show.add_argument('id', help='Modification ID')
    
    # apply
    p_apply = subparsers.add_parser('apply', help='Apply a modification')
    p_apply.add_argument('id', help='Modification ID')
    
    # approve
    p_approve = subparsers.add_parser('approve', help='Approve a modification')
    p_approve.add_argument('id', help='Modification ID')
    
    # reject
    p_reject = subparsers.add_parser('reject', help='Reject a modification')
    p_reject.add_argument('id', help='Modification ID')
    p_reject.add_argument('--reason', '-r', required=True, help='Reason for rejection')
    
    # rollback
    p_rollback = subparsers.add_parser('rollback', help='Rollback a modification')
    p_rollback.add_argument('id', help='Modification ID')
    p_rollback.add_argument('--reason', '-r', required=True, help='Reason for rollback')
    
    # history
    p_history = subparsers.add_parser('history', help='Show modification history')
    p_history.add_argument('--file', '-f', help='Filter by file')
    p_history.add_argument('--days', '-d', type=int, default=30, help='Days to look back')
    p_history.add_argument('--limit', type=int, default=20)
    p_history.add_argument('--verbose', '-v', action='store_true')
    
    # stats
    p_stats = subparsers.add_parser('stats', help='Show statistics')
    
    # from-correction
    p_from_corr = subparsers.add_parser('from-correction', help='Create proposal from correction')
    p_from_corr.add_argument('id', type=int, help='Correction ID from self-awareness')
    
    # from-insight
    p_from_ins = subparsers.add_parser('from-insight', help='Create proposal from insight')
    p_from_ins.add_argument('id', type=int, help='Insight ID from self-awareness')
    
    # process
    p_process = subparsers.add_parser('process', help='Process pending corrections/insights')
    p_process.add_argument('--source', choices=['corrections', 'insights', 'all'], default='all')
    p_process.add_argument('--limit', type=int, default=10)
    p_process.add_argument('--dry-run', action='store_true', help='Show what would be processed')
    
    # rules
    p_rules = subparsers.add_parser('rules', help='Manage modification rules')
    rules_sub = p_rules.add_subparsers(dest='rules_action')
    
    rules_list = rules_sub.add_parser('list', help='List active rules')
    
    rules_add = rules_sub.add_parser('add', help='Add a new rule')
    rules_add.add_argument('--name', '-n', required=True, help='Rule name')
    rules_add.add_argument('--trigger-type', '-t', required=True,
                          choices=['correction_type', 'insight_type', 'pattern', 'keyword'])
    rules_add.add_argument('--trigger-match', '-m', required=True, help='Value to match')
    rules_add.add_argument('--target-file', '-f', required=True, help='Target file')
    rules_add.add_argument('--template', required=True, help='Action template')
    rules_add.add_argument('--description', '-d', help='Rule description')
    rules_add.add_argument('--section', '-s', help='Target section')
    rules_add.add_argument('--auto-apply', action='store_true', help='Enable auto-apply')
    
    rules_disable = rules_sub.add_parser('disable', help='Disable a rule')
    rules_disable.add_argument('rule_id', help='Rule ID')
    
    rules_enable = rules_sub.add_parser('enable', help='Enable a rule')
    rules_enable.add_argument('rule_id', help='Rule ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    svc = get_service()
    
    commands = {
        'propose': cmd_propose,
        'list': cmd_list,
        'pending': cmd_pending,
        'show': cmd_show,
        'apply': cmd_apply,
        'approve': cmd_approve,
        'reject': cmd_reject,
        'rollback': cmd_rollback,
        'history': cmd_history,
        'stats': cmd_stats,
        'from-correction': cmd_from_correction,
        'from-insight': cmd_from_insight,
        'process': cmd_process,
        'rules': cmd_rules,
    }
    
    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args, svc)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
