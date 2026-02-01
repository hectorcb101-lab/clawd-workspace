#!/usr/bin/env python3
"""
Atlas Events CLI
================
Simple interface for logging and querying events.

Usage:
    atlas_events log <type> <content>
    atlas_events query [--type TYPE] [--limit N] [--since HOURS]
    atlas_events stats
    atlas_events compress
"""

import sys
import json
import argparse
from datetime import datetime, timezone, timedelta

# Add parent to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from event_schema import Event, EventType, message_in, message_out, tool_call, learning, decision, memory_add
from event_log import EventLog, EventLogConfig, get_log


def cmd_log(args):
    """Log an event."""
    log = get_log()
    
    # Parse content as JSON if possible
    try:
        content = json.loads(args.content)
    except json.JSONDecodeError:
        content = {"text": args.content}
    
    # Create event
    try:
        event_type = EventType(args.type)
    except ValueError:
        print(f"Unknown event type: {args.type}")
        print(f"Valid types: {[e.value for e in EventType]}")
        return 1
    
    event = Event(
        type=event_type,
        source=args.source or "cli",
        content=content,
        metadata={"via": "atlas_events cli"}
    )
    
    event_id = log.append(event)
    print(f"✅ Logged event: {event_id}")
    return 0


def cmd_query(args):
    """Query events."""
    log = get_log()
    
    # Build filters
    start_time = None
    if args.since:
        start_time = datetime.now(timezone.utc) - timedelta(hours=args.since)
    
    event_types = None
    if args.type:
        try:
            event_types = [EventType(args.type)]
        except ValueError:
            print(f"Unknown event type: {args.type}")
            return 1
    
    # Query
    events = list(log.query(
        start_time=start_time,
        event_types=event_types,
        source=args.source,
        limit=args.limit or 20
    ))
    
    if not events:
        print("No events found.")
        return 0
    
    print(f"Found {len(events)} events:\n")
    
    for e in events:
        ts = e.timestamp.split("T")[1].split(".")[0]  # Just time
        date = e.timestamp.split("T")[0]
        content_preview = str(e.content)[:60] + "..." if len(str(e.content)) > 60 else str(e.content)
        print(f"[{date} {ts}] {e.type.value:15} | {e.source:12} | {content_preview}")
    
    return 0


def cmd_stats(args):
    """Show event log statistics."""
    log = get_log()
    stats = log.get_stats()
    
    print("📊 Event Log Statistics\n")
    print(f"  Hot files:    {stats['hot_files']}")
    print(f"  Warm files:   {stats['warm_files']}")
    print(f"  Cold files:   {stats['cold_files']}")
    print(f"  Hot events:   {stats['hot_events']}")
    print(f"  Total size:   {stats['total_size_bytes'] / 1024:.1f} KB")
    
    return 0


def cmd_compress(args):
    """Compress old event files."""
    log = get_log()
    
    print("Compressing old files...")
    log.compress_old_files()
    
    print("Archiving very old files...")
    log.archive_old_files()
    
    print("✅ Done")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Atlas Events CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log an event")
    log_parser.add_argument("type", help="Event type")
    log_parser.add_argument("content", help="Event content (text or JSON)")
    log_parser.add_argument("--source", "-s", help="Event source")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query events")
    query_parser.add_argument("--type", "-t", help="Filter by event type")
    query_parser.add_argument("--source", "-s", help="Filter by source")
    query_parser.add_argument("--since", type=int, help="Events from last N hours")
    query_parser.add_argument("--limit", "-n", type=int, help="Max events to return")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Compress command
    subparsers.add_parser("compress", help="Compress old files")
    
    args = parser.parse_args()
    
    if args.command == "log":
        return cmd_log(args)
    elif args.command == "query":
        return cmd_query(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "compress":
        return cmd_compress(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
