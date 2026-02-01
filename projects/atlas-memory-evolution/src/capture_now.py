#!/usr/bin/env python3
"""
Capture Now
===========
Log the current moment - what I'm doing, thinking, building.

Quick capture for important events without ceremony.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from event_schema import Event, EventType
from event_log import get_log


def capture(event_type: str, content: str, source: str = "atlas"):
    """Capture a single event right now."""
    log = get_log()
    
    type_map = {
        "thought": EventType.LEARNING,
        "learn": EventType.LEARNING,
        "learning": EventType.LEARNING,
        "decide": EventType.DECISION,
        "decision": EventType.DECISION,
        "do": EventType.TOOL_CALL,
        "action": EventType.TOOL_CALL,
        "in": EventType.MESSAGE_IN,
        "out": EventType.MESSAGE_OUT,
        "error": EventType.ERROR,
    }
    
    etype = type_map.get(event_type.lower(), EventType.LEARNING)
    
    event = Event(
        type=etype,
        source=source,
        content={"text": content, "captured_at": datetime.now(timezone.utc).isoformat()}
    )
    
    event_id = log.append(event)
    return event_id


def main():
    parser = argparse.ArgumentParser(description="Capture an event right now")
    parser.add_argument("type", help="Event type: thought, learn, decide, do, in, out, error")
    parser.add_argument("content", help="What happened / what you learned / what you decided")
    parser.add_argument("--source", "-s", default="atlas", help="Source")
    
    args = parser.parse_args()
    
    event_id = capture(args.type, args.content, args.source)
    print(f"✅ Captured: {event_id}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Quick interactive mode
        print("Quick Capture Mode")
        print("==================")
        print("Type: thought, learn, decide, do, in, out, error")
        print()
        
        etype = input("Type: ").strip() or "thought"
        content = input("Content: ").strip()
        
        if content:
            event_id = capture(etype, content)
            print(f"\n✅ Captured: {event_id}")
        else:
            print("No content provided.")
