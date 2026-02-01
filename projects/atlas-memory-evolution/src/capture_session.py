#!/usr/bin/env python3
"""
Session Capture
===============
Capture the current session's conversation in real-time.

Called at start of each session to begin capturing.
Called at end (or periodically) to flush captured events.

Usage:
    # At session start
    python3 capture_session.py start "telegram" "main"
    
    # Log a message
    python3 capture_session.py message "in" "Finn" "Hello Atlas"
    python3 capture_session.py message "out" "" "Hello Finn!"
    
    # At session end
    python3 capture_session.py end
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from event_schema import Event, EventType, message_in, message_out, learning, decision
from event_log import get_log
from extractor import run_extraction

SESSION_STATE_FILE = Path(__file__).parent.parent / "data" / "current_session.json"


def load_session() -> dict:
    """Load current session state."""
    if SESSION_STATE_FILE.exists():
        try:
            return json.loads(SESSION_STATE_FILE.read_text())
        except:
            pass
    return {"active": False, "messages": [], "session_id": None}


def save_session(state: dict):
    """Save session state."""
    SESSION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_STATE_FILE.write_text(json.dumps(state, indent=2))


def start_session(source: str = "telegram", session_type: str = "main"):
    """Start capturing a new session."""
    event_log = get_log()
    
    # Create session start event
    event = Event(
        type=EventType.SESSION_START,
        source=source,
        content={
            "session_type": session_type,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
    )
    event_log.append(event)
    
    # Save session state
    save_session({
        "active": True,
        "session_id": event.id,
        "source": source,
        "started_at": event.timestamp if isinstance(event.timestamp, str) else event.timestamp.isoformat(),
        "messages": []
    })
    
    print(f"✅ Session started: {event.id}")
    return event.id


def capture_message(direction: str, user: str, text: str):
    """Capture a message in the current session."""
    event_log = get_log()
    session = load_session()
    
    if direction == "in":
        event = message_in(text, source=session.get("source", "telegram"), user=user or None)
    else:
        event = message_out(text, source=session.get("source", "telegram"))
    
    event_log.append(event)
    
    # Track in session
    session["messages"].append({
        "direction": direction,
        "user": user,
        "text": text[:100] + "..." if len(text) > 100 else text,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    save_session(session)
    
    return event.id


def end_session(reason: str = "normal"):
    """End the current session."""
    event_log = get_log()
    session = load_session()
    
    if not session.get("active"):
        print("No active session to end")
        return
    
    # Create session end event
    event = Event(
        type=EventType.SESSION_END,
        source=session.get("source", "unknown"),
        content={
            "session_id": session.get("session_id"),
            "reason": reason,
            "message_count": len(session.get("messages", [])),
            "duration_seconds": None  # Could calculate from started_at
        }
    )
    event_log.append(event)
    
    # Run extraction to process new events
    print("🧠 Running extraction...")
    stats = run_extraction()
    print(f"   Extracted {stats['facts']} facts, {stats['entities']} entities")
    
    # Clear session
    save_session({"active": False, "messages": [], "session_id": None})
    
    print(f"✅ Session ended: {session.get('session_id')}")


def capture_learning(summary: str, details: str = None):
    """Capture a learning event."""
    event_log = get_log()
    event = learning(summary, details)
    event_log.append(event)
    return event.id


def capture_decision(what: str, why: str):
    """Capture a decision event."""
    event_log = get_log()
    event = decision(what, why)
    event_log.append(event)
    return event.id


def get_status():
    """Get current session status."""
    session = load_session()
    return {
        "active": session.get("active", False),
        "session_id": session.get("session_id"),
        "source": session.get("source"),
        "started_at": session.get("started_at"),
        "message_count": len(session.get("messages", []))
    }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  capture_session.py start [source] [type]")
        print("  capture_session.py message <in|out> <user> <text>")
        print("  capture_session.py learn <summary> [details]")
        print("  capture_session.py decide <what> <why>")
        print("  capture_session.py end [reason]")
        print("  capture_session.py status")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        source = sys.argv[2] if len(sys.argv) > 2 else "telegram"
        session_type = sys.argv[3] if len(sys.argv) > 3 else "main"
        start_session(source, session_type)
    
    elif cmd == "message":
        if len(sys.argv) < 5:
            print("Usage: capture_session.py message <in|out> <user> <text>")
            return 1
        direction = sys.argv[2]
        user = sys.argv[3]
        text = sys.argv[4]
        event_id = capture_message(direction, user, text)
        print(f"Captured: {event_id}")
    
    elif cmd == "learn":
        if len(sys.argv) < 3:
            print("Usage: capture_session.py learn <summary> [details]")
            return 1
        summary = sys.argv[2]
        details = sys.argv[3] if len(sys.argv) > 3 else None
        event_id = capture_learning(summary, details)
        print(f"Captured: {event_id}")
    
    elif cmd == "decide":
        if len(sys.argv) < 4:
            print("Usage: capture_session.py decide <what> <why>")
            return 1
        what = sys.argv[2]
        why = sys.argv[3]
        event_id = capture_decision(what, why)
        print(f"Captured: {event_id}")
    
    elif cmd == "end":
        reason = sys.argv[2] if len(sys.argv) > 2 else "normal"
        end_session(reason)
    
    elif cmd == "status":
        status = get_status()
        print(f"Session active: {status['active']}")
        if status['active']:
            print(f"  ID: {status['session_id']}")
            print(f"  Source: {status['source']}")
            print(f"  Started: {status['started_at']}")
            print(f"  Messages: {status['message_count']}")


if __name__ == "__main__":
    sys.exit(main() or 0)
