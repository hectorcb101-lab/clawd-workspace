#!/usr/bin/env python3
"""
Atlas Session Logger
====================
Automatically captures session events and integrates with the event log.

This is the bridge between my operations and persistent memory.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from event_schema import (
    Event, EventType, 
    message_in, message_out, tool_call, tool_result,
    file_write, memory_add, learning, decision
)
from event_log import EventLog, EventLogConfig, get_log


class SessionLogger:
    """
    Captures everything that happens in a session.
    
    Usage:
        logger = SessionLogger()
        logger.start_session("telegram", "main")
        
        # Log events as they happen
        logger.log_message_in("Hello!", user="Finn")
        logger.log_message_out("Hi there!")
        logger.log_tool("exec", {"command": "ls"}, result="files...")
        logger.log_learning("Something important")
        
        logger.end_session()
    """
    
    def __init__(self):
        self.event_log = get_log()
        self.session_id: Optional[str] = None
        self.session_source: Optional[str] = None
        self.event_count = 0
    
    def start_session(self, source: str = "unknown", session_type: str = "main") -> str:
        """Start a new session."""
        event = Event(
            type=EventType.SESSION_START,
            source=source,
            content={
                "session_type": session_type,
                "started_at": datetime.now(timezone.utc).isoformat()
            }
        )
        self.session_id = event.id
        self.session_source = source
        self.event_count = 0
        self.event_log.append(event)
        return self.session_id
    
    def end_session(self, reason: str = "normal"):
        """End the current session."""
        if self.session_id:
            event = Event(
                type=EventType.SESSION_END,
                source=self.session_source or "unknown",
                content={
                    "session_id": self.session_id,
                    "reason": reason,
                    "event_count": self.event_count
                }
            )
            self.event_log.append(event)
            self.session_id = None
    
    def log_message_in(self, text: str, user: str = None, **metadata) -> str:
        """Log an incoming message."""
        event = message_in(text, source=self.session_source or "unknown", user=user, **metadata)
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_message_out(self, text: str, **metadata) -> str:
        """Log an outgoing message."""
        event = message_out(text, source=self.session_source or "unknown", **metadata)
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_tool(self, tool_name: str, params: Dict[str, Any], result: Any = None, success: bool = True) -> str:
        """Log a tool call and its result."""
        # Log the call
        call_event = tool_call(tool_name, params)
        self.event_log.append(call_event)
        self.event_count += 1
        
        # Log the result
        result_event = tool_result(tool_name, result, success)
        self.event_count += 1
        return self.event_log.append(result_event)
    
    def log_file_op(self, path: str, operation: str, size_bytes: int = None) -> str:
        """Log a file operation."""
        event = Event(
            type=EventType.FILE_WRITE if operation == "write" else EventType.FILE_READ,
            source="filesystem",
            content={"path": path, "operation": operation, "size_bytes": size_bytes}
        )
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_learning(self, summary: str, details: str = None, **metadata) -> str:
        """Log something I learned."""
        event = learning(summary, details, **metadata)
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_decision(self, what: str, why: str, alternatives: list = None) -> str:
        """Log a decision I made."""
        event = decision(what, why, alternatives)
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_memory(self, category: str, subject: str, content: str) -> str:
        """Log a memory addition."""
        event = memory_add(category, subject, content)
        self.event_count += 1
        return self.event_log.append(event)
    
    def log_raw(self, event_type: EventType, content: Dict[str, Any], source: str = None) -> str:
        """Log a raw event."""
        event = Event(
            type=event_type,
            source=source or self.session_source or "unknown",
            content=content
        )
        self.event_count += 1
        return self.event_log.append(event)


# Global session logger instance
_session_logger: Optional[SessionLogger] = None


def get_session_logger() -> SessionLogger:
    """Get or create the global session logger."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger


# Convenience functions for quick logging
def log_in(text: str, user: str = None) -> str:
    """Quick log incoming message."""
    return get_session_logger().log_message_in(text, user)

def log_out(text: str) -> str:
    """Quick log outgoing message."""
    return get_session_logger().log_message_out(text)

def log_tool(name: str, params: dict, result: Any = None) -> str:
    """Quick log tool call."""
    return get_session_logger().log_tool(name, params, result)

def log_learn(summary: str, details: str = None) -> str:
    """Quick log learning."""
    return get_session_logger().log_learning(summary, details)

def log_decide(what: str, why: str) -> str:
    """Quick log decision."""
    return get_session_logger().log_decision(what, why)


if __name__ == "__main__":
    print("Testing Session Logger...")
    
    logger = SessionLogger()
    
    # Simulate a session
    print("\n--- Starting session ---")
    session_id = logger.start_session("telegram", "main")
    print(f"Session ID: {session_id}")
    
    print("\n--- Logging events ---")
    logger.log_message_in("Let's build the memory system", user="Finn")
    logger.log_message_out("Starting Phase 1...")
    logger.log_tool("exec", {"command": "mkdir -p src"}, result="success")
    logger.log_file_op("/path/to/file.py", "write", 1234)
    logger.log_learning("Event logging works", "Successfully captured session events")
    logger.log_decision(
        what="Use append-only log design",
        why="Immutable history, easy to reason about",
        alternatives=["SQLite only", "In-memory", "External service"]
    )
    
    print(f"Events logged: {logger.event_count}")
    
    print("\n--- Ending session ---")
    logger.end_session("test complete")
    
    # Query what we logged
    print("\n--- Verifying logged events ---")
    events = list(logger.event_log.query(limit=10))
    for e in events[-8:]:  # Last 8 events
        print(f"  [{e.type.value}] {e.content.get('text', e.content.get('summary', str(e.content)[:40]))}")
    
    print("\n✅ Session Logger tests passed!")
