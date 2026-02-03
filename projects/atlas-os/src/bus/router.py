"""
Atlas OS Event Router (Integration Bus)

Central hub that receives events from all Atlas systems and routes them
to registered subscribers. This enables automatic data flow between:
- Self-awareness → Training capture
- Judgment → Memory
- Modifications → Logging
- etc.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional
from collections import defaultdict
import threading

from .schema import AtlasEvent, EventType, TrainingFormat
from .validator import validate_event, ValidationError


# Type alias for event handlers
EventHandler = Callable[[AtlasEvent], None]


class EventBus:
    """
    Central event routing system for Atlas OS.
    
    Usage:
        bus = EventBus()
        bus.subscribe(EventType.CORRECTION, my_handler)
        bus.subscribe("*", log_all_events)  # Wildcard
        bus.emit(correction_event(...))
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._log_dir = log_dir or Path.home() / "clawd" / "projects" / "atlas-os" / "data" / "events"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
        # Auto-subscribe the event logger
        self.subscribe("*", self._log_event)
        
        # Auto-subscribe training capture
        self.subscribe("*", self._capture_training)
    
    def subscribe(self, event_type: str | EventType, handler: EventHandler) -> None:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: EventType enum, string, or "*" for all events
            handler: Function that takes an AtlasEvent
        """
        key = event_type.value if isinstance(event_type, EventType) else event_type
        with self._lock:
            self._subscribers[key].append(handler)
    
    def unsubscribe(self, event_type: str | EventType, handler: EventHandler) -> None:
        """Remove a handler from an event type."""
        key = event_type.value if isinstance(event_type, EventType) else event_type
        with self._lock:
            if handler in self._subscribers[key]:
                self._subscribers[key].remove(handler)
    
    def emit(self, event: AtlasEvent, validate: bool = True) -> None:
        """
        Emit an event to all relevant subscribers.
        
        Args:
            event: The event to emit
            validate: Whether to validate the event (default True)
        
        Calls handlers for:
        1. Exact event type match
        2. Wildcard ("*") subscribers
        """
        # Validate event if requested
        if validate:
            is_valid, errors = validate_event(event)
            if not is_valid:
                # Log validation errors but still emit (don't break the system)
                error_msgs = [str(e) for e in errors if e.severity == "error"]
                if error_msgs:
                    print(f"⚠️ Event validation errors for {event.id}: {'; '.join(error_msgs)}")
        
        with self._lock:
            handlers = (
                self._subscribers.get(event.type.value, []) +
                self._subscribers.get("*", [])
            )
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def _log_event(self, event: AtlasEvent) -> None:
        """Log all events to daily JSONL file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self._log_dir / f"events-{date_str}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(event.to_json() + "\n")
    
    def _capture_training(self, event: AtlasEvent) -> None:
        """Auto-capture training-ready events."""
        if not event.training.usable:
            return
        
        training_dir = Path.home() / "clawd" / "training-data"
        
        if event.training.format == TrainingFormat.DPO:
            # Correction → DPO format
            month = datetime.now().strftime("%Y-%m")
            out_dir = training_dir / "corrections" / month
            out_dir.mkdir(parents=True, exist_ok=True)
            
            dpo_entry = {
                "id": event.id,
                "timestamp": event.timestamp,
                "prompt": event.data.get("context", ""),
                "chosen": event.data.get("chosen", ""),
                "rejected": event.data.get("rejected", ""),
                "meta": {
                    "explanation": event.data.get("explanation", ""),
                    "category": event.data.get("category", ""),
                    "severity": event.data.get("severity", ""),
                    "quality": event.training.quality
                }
            }
            
            with open(out_dir / "corrections.jsonl", "a") as f:
                f.write(json.dumps(dpo_entry) + "\n")
        
        elif event.training.format == TrainingFormat.SFT:
            # Instruction → SFT format
            month = datetime.now().strftime("%Y-%m")
            out_dir = training_dir / "instructions" / month
            out_dir.mkdir(parents=True, exist_ok=True)
            
            sft_entry = {
                "id": event.id,
                "timestamp": event.timestamp,
                "messages": []
            }
            
            if event.data.get("system"):
                sft_entry["messages"].append({
                    "role": "system",
                    "content": event.data["system"]
                })
            
            sft_entry["messages"].append({
                "role": "user", 
                "content": event.data.get("instruction", event.data.get("task", ""))
            })
            sft_entry["messages"].append({
                "role": "assistant",
                "content": event.data.get("response", event.data.get("approach", ""))
            })
            sft_entry["meta"] = {
                "quality": event.training.quality,
                "tags": event.tags
            }
            
            with open(out_dir / "sft_pairs.jsonl", "a") as f:
                f.write(json.dumps(sft_entry) + "\n")
        
        elif event.training.format == TrainingFormat.REASONING:
            # Judgment → Reasoning traces
            month = datetime.now().strftime("%Y-%m")
            out_dir = training_dir / "judgments" / month
            out_dir.mkdir(parents=True, exist_ok=True)
            
            reasoning_entry = {
                "id": event.id,
                "timestamp": event.timestamp,
                "situation": event.data.get("situation", ""),
                "reasoning": event.data.get("reasoning", ""),
                "decision": event.data.get("decision", ""),
                "principles": event.data.get("principles_consulted", []),
                "outcome": event.data.get("outcome"),
                "meta": {
                    "quality": event.training.quality
                }
            }
            
            with open(out_dir / "reasoning.jsonl", "a") as f:
                f.write(json.dumps(reasoning_entry) + "\n")
    
    def get_stats(self) -> dict:
        """Get event statistics."""
        stats = {"total_events": 0, "by_date": {}, "by_type": defaultdict(int)}
        
        for log_file in self._log_dir.glob("events-*.jsonl"):
            date = log_file.stem.replace("events-", "")
            count = 0
            with open(log_file) as f:
                for line in f:
                    count += 1
                    try:
                        evt = json.loads(line)
                        stats["by_type"][evt.get("type", "unknown")] += 1
                    except:
                        pass
            stats["by_date"][date] = count
            stats["total_events"] += count
        
        stats["by_type"] = dict(stats["by_type"])
        return stats


# Global singleton instance
_bus: Optional[EventBus] = None


def get_bus() -> EventBus:
    """Get the global event bus instance."""
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus


def emit(event: AtlasEvent) -> None:
    """Convenience function to emit to global bus."""
    get_bus().emit(event)


if __name__ == "__main__":
    from .schema import correction_event, outcome_event
    
    # Test the bus
    bus = get_bus()
    
    # Add a test subscriber
    def test_handler(event: AtlasEvent):
        print(f"Received: {event.type.value} - {event.summary}")
    
    bus.subscribe("*", test_handler)
    
    # Emit test events
    print("\nEmitting correction...")
    bus.emit(correction_event(
        context="Asked about the time",
        rejected="I don't know the time",
        chosen="The current time is 00:35 UTC",
        explanation="Should use available info"
    ))
    
    print("\nEmitting outcome...")
    bus.emit(outcome_event(
        task="Create roadmap document",
        result="success",
        approach="Used markdown with clear sections",
        feedback="Finn approved",
        learnings="Break large plans into phases"
    ))
    
    print("\nStats:")
    print(json.dumps(bus.get_stats(), indent=2))
