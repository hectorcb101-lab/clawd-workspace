"""
Atlas Memory Evolution — Event Log
===================================
Append-only event log with compression and archival.

Design principles:
- Append-only: Never modify past events
- Durable: Events survive crashes
- Compressed: Old events are gzipped
- Queryable: Can retrieve events by time range
"""

import os
import json
import gzip
import glob
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Iterator, Callable
from dataclasses import dataclass
import threading
import fcntl

from event_schema import Event, EventType


@dataclass
class EventLogConfig:
    """Configuration for the event log."""
    
    # Base directory for all log files
    base_dir: str = "/home/ubuntu/clawd/projects/atlas-memory-evolution/data/events"
    
    # How many events before rotating to a new file
    events_per_file: int = 1000
    
    # How old before compressing (in days)
    compress_after_days: int = 1
    
    # How old before moving to cold storage (in days)
    archive_after_days: int = 7
    
    # File naming pattern
    file_prefix: str = "events"


class EventLog:
    """
    Append-only event log with automatic rotation and compression.
    
    File structure:
    data/events/
    ├── hot/
    │   └── events_2026-02-01_001.jsonl  (current, uncompressed)
    ├── warm/
    │   └── events_2026-01-30_001.jsonl.gz  (compressed)
    └── cold/
        └── events_2026-01-15_001.jsonl.gz  (archived)
    """
    
    def __init__(self, config: EventLogConfig = None):
        self.config = config or EventLogConfig()
        self._setup_directories()
        self._lock = threading.Lock()
        self._current_file = None
        self._current_count = 0
        self._init_current_file()
    
    def _setup_directories(self):
        """Create directory structure."""
        for tier in ["hot", "warm", "cold"]:
            path = Path(self.config.base_dir) / tier
            path.mkdir(parents=True, exist_ok=True)
    
    def _get_current_date(self) -> str:
        """Get current date string."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _get_next_file_number(self, date: str, tier: str = "hot") -> int:
        """Get the next file number for a given date."""
        pattern = f"{self.config.file_prefix}_{date}_*.jsonl*"
        path = Path(self.config.base_dir) / tier
        existing = list(path.glob(pattern))
        
        if not existing:
            return 1
        
        numbers = []
        for f in existing:
            try:
                # Extract number from filename like events_2026-02-01_003.jsonl
                num = int(f.stem.split("_")[-1].replace(".jsonl", ""))
                numbers.append(num)
            except (ValueError, IndexError):
                continue
        
        return max(numbers) + 1 if numbers else 1
    
    def _init_current_file(self):
        """Initialize or find the current hot file."""
        date = self._get_current_date()
        hot_dir = Path(self.config.base_dir) / "hot"
        
        # Find existing file for today
        pattern = f"{self.config.file_prefix}_{date}_*.jsonl"
        existing = sorted(hot_dir.glob(pattern))
        
        if existing:
            # Use the latest file
            self._current_file = existing[-1]
            # Count existing events
            with open(self._current_file, 'r') as f:
                self._current_count = sum(1 for _ in f)
            
            # If it's full, start a new one
            if self._current_count >= self.config.events_per_file:
                self._rotate_file()
        else:
            # Start a new file
            num = 1
            self._current_file = hot_dir / f"{self.config.file_prefix}_{date}_{num:03d}.jsonl"
            self._current_count = 0
    
    def _rotate_file(self):
        """Start a new file."""
        date = self._get_current_date()
        num = self._get_next_file_number(date, "hot")
        hot_dir = Path(self.config.base_dir) / "hot"
        self._current_file = hot_dir / f"{self.config.file_prefix}_{date}_{num:03d}.jsonl"
        self._current_count = 0
    
    def append(self, event: Event) -> str:
        """
        Append an event to the log.
        Returns the event ID.
        """
        with self._lock:
            # Check if we need to rotate (new day or file full)
            current_date = self._get_current_date()
            file_date = self._current_file.stem.split("_")[1] if self._current_file else None
            
            if file_date != current_date or self._current_count >= self.config.events_per_file:
                self._rotate_file()
            
            # Append with file locking for safety
            with open(self._current_file, 'a') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(event.to_json() + "\n")
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            self._current_count += 1
            return event.id
    
    def log(self, event: Event) -> str:
        """Alias for append()."""
        return self.append(event)
    
    def query(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        event_types: List[EventType] = None,
        source: str = None,
        limit: int = None
    ) -> Iterator[Event]:
        """
        Query events with filters.
        
        Args:
            start_time: Only events after this time
            end_time: Only events before this time
            event_types: Filter by event type(s)
            source: Filter by source
            limit: Maximum events to return
        """
        count = 0
        
        # Get all relevant files (hot + warm + cold)
        for tier in ["cold", "warm", "hot"]:  # Oldest first
            tier_path = Path(self.config.base_dir) / tier
            files = sorted(tier_path.glob(f"{self.config.file_prefix}_*.jsonl*"))
            
            for file_path in files:
                for event in self._read_file(file_path):
                    # Apply filters
                    if start_time:
                        event_time = datetime.fromisoformat(event.timestamp)
                        if event_time < start_time:
                            continue
                    
                    if end_time:
                        event_time = datetime.fromisoformat(event.timestamp)
                        if event_time > end_time:
                            continue
                    
                    if event_types and event.type not in event_types:
                        continue
                    
                    if source and event.source != source:
                        continue
                    
                    yield event
                    count += 1
                    
                    if limit and count >= limit:
                        return
    
    def _read_file(self, file_path: Path) -> Iterator[Event]:
        """Read events from a file (handles both compressed and uncompressed)."""
        is_compressed = str(file_path).endswith('.gz')
        
        open_func = gzip.open if is_compressed else open
        mode = 'rt' if is_compressed else 'r'
        
        try:
            with open_func(file_path, mode) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            yield Event.from_json(line)
                        except (json.JSONDecodeError, KeyError) as e:
                            # Skip malformed lines
                            continue
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    def compress_old_files(self):
        """Compress files older than compress_after_days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.config.compress_after_days)
        hot_dir = Path(self.config.base_dir) / "hot"
        warm_dir = Path(self.config.base_dir) / "warm"
        
        for file_path in hot_dir.glob(f"{self.config.file_prefix}_*.jsonl"):
            # Skip current file
            if file_path == self._current_file:
                continue
            
            # Check file date
            try:
                date_str = file_path.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                
                if file_date < cutoff:
                    # Compress and move to warm
                    compressed_path = warm_dir / (file_path.name + ".gz")
                    
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    # Remove original
                    file_path.unlink()
                    print(f"Compressed: {file_path.name} -> {compressed_path.name}")
            
            except (ValueError, IndexError):
                continue
    
    def archive_old_files(self):
        """Move very old files to cold storage."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.config.archive_after_days)
        warm_dir = Path(self.config.base_dir) / "warm"
        cold_dir = Path(self.config.base_dir) / "cold"
        
        for file_path in warm_dir.glob(f"{self.config.file_prefix}_*.jsonl.gz"):
            try:
                date_str = file_path.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                
                if file_date < cutoff:
                    # Move to cold
                    cold_path = cold_dir / file_path.name
                    file_path.rename(cold_path)
                    print(f"Archived: {file_path.name} -> cold/")
            
            except (ValueError, IndexError):
                continue
    
    def get_stats(self) -> dict:
        """Get statistics about the event log."""
        stats = {
            "hot_files": 0,
            "warm_files": 0,
            "cold_files": 0,
            "hot_events": 0,
            "total_size_bytes": 0
        }
        
        for tier in ["hot", "warm", "cold"]:
            tier_path = Path(self.config.base_dir) / tier
            files = list(tier_path.glob(f"{self.config.file_prefix}_*"))
            stats[f"{tier}_files"] = len(files)
            
            for f in files:
                stats["total_size_bytes"] += f.stat().st_size
        
        # Count hot events
        stats["hot_events"] = self._current_count
        
        return stats


# Global instance for easy access
_default_log: Optional[EventLog] = None


def get_log() -> EventLog:
    """Get or create the default event log."""
    global _default_log
    if _default_log is None:
        _default_log = EventLog()
    return _default_log


def log_event(event: Event) -> str:
    """Log an event to the default log."""
    return get_log().append(event)


if __name__ == "__main__":
    print("Testing Event Log...")
    
    # Import schema helpers
    from event_schema import message_in, message_out, tool_call, learning
    
    # Create a test log
    config = EventLogConfig(
        base_dir="/home/ubuntu/clawd/projects/atlas-memory-evolution/data/events"
    )
    log = EventLog(config)
    
    # Log some test events
    print("\n--- Logging test events ---")
    
    e1 = message_in("Hello Atlas!", source="telegram", user="Finn")
    id1 = log.append(e1)
    print(f"Logged message_in: {id1}")
    
    e2 = message_out("Hello Finn! How can I help?", source="telegram")
    id2 = log.append(e2)
    print(f"Logged message_out: {id2}")
    
    e3 = tool_call("exec", {"command": "ls -la"})
    id3 = log.append(e3)
    print(f"Logged tool_call: {id3}")
    
    e4 = learning("Event log system works", "Successfully tested append and query")
    id4 = log.append(e4)
    print(f"Logged learning: {id4}")
    
    # Query events
    print("\n--- Querying events ---")
    events = list(log.query(limit=10))
    print(f"Found {len(events)} events")
    
    for e in events:
        print(f"  [{e.type.value}] {e.source}: {e.content}")
    
    # Stats
    print("\n--- Log stats ---")
    stats = log.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n✅ Event Log tests passed!")
