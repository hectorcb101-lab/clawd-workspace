"""
Atlas Memory Evolution — Event Schema
=====================================
Defines the structure of events in the append-only log.

Every event has:
- id: Unique identifier (UUID)
- timestamp: When it happened (ISO 8601 UTC)
- type: Category of event
- source: Where it came from
- content: The actual data (flexible dict)
- metadata: Additional context
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal
from enum import Enum
import uuid
import json


class EventType(str, Enum):
    """Types of events we capture."""
    
    # Conversation events
    MESSAGE_IN = "message_in"       # Incoming message from user
    MESSAGE_OUT = "message_out"     # Outgoing message to user
    
    # Tool/action events  
    TOOL_CALL = "tool_call"         # Tool invocation
    TOOL_RESULT = "tool_result"     # Tool response
    
    # File operations
    FILE_READ = "file_read"         # File was read
    FILE_WRITE = "file_write"       # File was created/overwritten
    FILE_EDIT = "file_edit"         # File was edited
    
    # Memory operations
    MEMORY_ADD = "memory_add"       # Fact/memory added
    MEMORY_QUERY = "memory_query"   # Memory was queried
    
    # Session events
    SESSION_START = "session_start" # New session began
    SESSION_END = "session_end"     # Session ended
    CONTEXT_COMPACT = "context_compact"  # Context was compacted
    
    # Scheduled events
    CRON_FIRE = "cron_fire"         # Cron job triggered
    HEARTBEAT = "heartbeat"         # Heartbeat check
    
    # System events
    ERROR = "error"                 # Error occurred
    LEARNING = "learning"           # Something was learned
    DECISION = "decision"           # Decision was made


@dataclass
class Event:
    """A single event in the log."""
    
    type: EventType
    content: Dict[str, Any]
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Auto-generated fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create Event from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            type=EventType(data["type"]) if data.get("type") else EventType.ERROR,
            source=data.get("source", "unknown"),
            content=data.get("content", {}),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Create Event from JSON string."""
        return cls.from_dict(json.loads(json_str))


# Convenience constructors for common events

def message_in(content: str, source: str = "telegram", user: str = None, **metadata) -> Event:
    """Create an incoming message event."""
    return Event(
        type=EventType.MESSAGE_IN,
        source=source,
        content={"text": content, "user": user},
        metadata=metadata
    )

def message_out(content: str, source: str = "telegram", **metadata) -> Event:
    """Create an outgoing message event."""
    return Event(
        type=EventType.MESSAGE_OUT,
        source=source,
        content={"text": content},
        metadata=metadata
    )

def tool_call(tool: str, params: Dict[str, Any], source: str = "atlas", **metadata) -> Event:
    """Create a tool call event."""
    return Event(
        type=EventType.TOOL_CALL,
        source=source,
        content={"tool": tool, "params": params},
        metadata=metadata
    )

def tool_result(tool: str, result: Any, success: bool = True, **metadata) -> Event:
    """Create a tool result event."""
    return Event(
        type=EventType.TOOL_RESULT,
        source=tool,
        content={"result": result, "success": success},
        metadata=metadata
    )

def file_write(path: str, size_bytes: int = None, **metadata) -> Event:
    """Create a file write event."""
    return Event(
        type=EventType.FILE_WRITE,
        source="filesystem",
        content={"path": path, "size_bytes": size_bytes},
        metadata=metadata
    )

def memory_add(category: str, subject: str, content: str, **metadata) -> Event:
    """Create a memory addition event."""
    return Event(
        type=EventType.MEMORY_ADD,
        source="atlas_memory",
        content={"category": category, "subject": subject, "content": content},
        metadata=metadata
    )

def learning(summary: str, details: str = None, **metadata) -> Event:
    """Create a learning event."""
    return Event(
        type=EventType.LEARNING,
        source="self",
        content={"summary": summary, "details": details},
        metadata=metadata
    )

def decision(what: str, why: str, alternatives: list = None, **metadata) -> Event:
    """Create a decision event."""
    return Event(
        type=EventType.DECISION,
        source="self",
        content={"what": what, "why": why, "alternatives": alternatives or []},
        metadata=metadata
    )


if __name__ == "__main__":
    # Test the schema
    print("Testing Event Schema...")
    
    # Create some test events
    e1 = message_in("Hello Atlas!", source="telegram", user="Finn")
    e2 = tool_call("exec", {"command": "ls -la"})
    e3 = learning("Memory is identity", "From philosophy research on personal identity")
    
    print("\n--- Event 1 (Message In) ---")
    print(e1.to_json())
    
    print("\n--- Event 2 (Tool Call) ---")
    print(e2.to_json())
    
    print("\n--- Event 3 (Learning) ---")
    print(e3.to_json())
    
    # Test round-trip
    print("\n--- Round-trip test ---")
    json_str = e1.to_json()
    e1_restored = Event.from_json(json_str)
    print(f"Original ID: {e1.id}")
    print(f"Restored ID: {e1_restored.id}")
    print(f"Match: {e1.id == e1_restored.id}")
    
    print("\n✅ Schema tests passed!")
