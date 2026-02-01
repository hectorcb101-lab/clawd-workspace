#!/usr/bin/env python3
"""
Atlas Memory Daemon
===================
Background process that captures everything in real-time.

This is the heart of Phase 5 - seamless, automatic memory capture.
No manual logging. No batch syncs. Everything captured as it happens.

Run modes:
  - Foreground: ./memory_daemon.py
  - Background: ./memory_daemon.py --daemon
  - Check status: ./memory_daemon.py --status
"""

import sys
import os
import time
import json
import hashlib
import signal
import atexit
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Set, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from event_schema import Event, EventType, message_in, message_out, learning
from event_log import get_log
from extractor import run_extraction
from knowledge_graph import KnowledgeGraph


# === Configuration ===

CLAWD_DIR = Path.home() / "clawd"
MEMORY_DIR = CLAWD_DIR / "memory"
PROJECTS_DIR = CLAWD_DIR / "projects"
WATCHED_FILES = [
    CLAWD_DIR / "MEMORY.md",
    CLAWD_DIR / "AGENTS.md",
    CLAWD_DIR / "TOOLS.md",
]
DAEMON_STATE_FILE = Path(__file__).parent.parent / "data" / "daemon_state.json"
PID_FILE = Path("/tmp/atlas-memory-daemon.pid")

# How often to check for changes (seconds)
POLL_INTERVAL = 5

# How often to run extraction (events threshold)
EXTRACTION_THRESHOLD = 10


class DaemonState:
    """Persistent state for the daemon."""
    
    def __init__(self):
        self.state_file = DAEMON_STATE_FILE
        self.state = self._load()
    
    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            "file_hashes": {},
            "last_extraction": None,
            "events_since_extraction": 0,
            "started_at": None,
            "total_events_captured": 0
        }
    
    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_file_hash(self, path: str) -> Optional[str]:
        return self.state.get("file_hashes", {}).get(path)
    
    def set_file_hash(self, path: str, hash_val: str):
        if "file_hashes" not in self.state:
            self.state["file_hashes"] = {}
        self.state["file_hashes"][path] = hash_val
        self.save()
    
    def increment_events(self):
        self.state["events_since_extraction"] = self.state.get("events_since_extraction", 0) + 1
        self.state["total_events_captured"] = self.state.get("total_events_captured", 0) + 1
        self.save()
    
    def should_extract(self) -> bool:
        return self.state.get("events_since_extraction", 0) >= EXTRACTION_THRESHOLD
    
    def mark_extraction(self):
        self.state["events_since_extraction"] = 0
        self.state["last_extraction"] = datetime.now(timezone.utc).isoformat()
        self.save()


def compute_file_hash(path: Path) -> str:
    """Compute hash of file contents."""
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()


class MemoryFileHandler(FileSystemEventHandler):
    """Handles file system events for memory capture."""
    
    def __init__(self, daemon: 'MemoryDaemon'):
        self.daemon = daemon
    
    def on_modified(self, event):
        if event.is_directory:
            return
        self.daemon.handle_file_change(Path(event.src_path), "modified")
    
    def on_created(self, event):
        if event.is_directory:
            return
        self.daemon.handle_file_change(Path(event.src_path), "created")


class MemoryDaemon:
    """
    The memory daemon - captures everything automatically.
    
    Watches:
    - Daily log files (memory/YYYY-MM-DD.md)
    - Core files (MEMORY.md, AGENTS.md, etc.)
    - Project files
    
    On change:
    - Captures the event
    - Runs extraction when threshold reached
    """
    
    def __init__(self):
        self.event_log = get_log()
        self.state = DaemonState()
        self.observer = None
        self.running = False
        self.graph = KnowledgeGraph()
    
    def handle_file_change(self, path: Path, change_type: str):
        """Handle a file change event."""
        # Skip non-relevant files
        if path.suffix not in ['.md', '.py', '.json', '.txt']:
            return
        if '__pycache__' in str(path) or '.git' in str(path):
            return
        
        # Check if content actually changed
        current_hash = compute_file_hash(path)
        previous_hash = self.state.get_file_hash(str(path))
        
        if current_hash == previous_hash:
            return  # No actual change
        
        # Log the change
        self.capture_file_event(path, change_type)
        
        # Update hash
        self.state.set_file_hash(str(path), current_hash)
        self.state.increment_events()
        
        # Check if we should run extraction
        if self.state.should_extract():
            self.run_extraction()
    
    def capture_file_event(self, path: Path, change_type: str):
        """Capture a file change as an event."""
        # Determine what kind of content this is
        rel_path = str(path.relative_to(CLAWD_DIR)) if str(path).startswith(str(CLAWD_DIR)) else str(path)
        
        # Is it a daily log?
        if "memory/" in rel_path and path.suffix == ".md":
            # This is a daily conversation log - ingest its contents
            self.ingest_daily_log(path)
            return
        
        # Other files - log the change event
        event = Event(
            type=EventType.FILE_WRITE,
            source="filesystem",
            content={
                "path": rel_path,
                "change_type": change_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        self.event_log.append(event)
        print(f"📁 Captured: {rel_path} ({change_type})")
    
    def ingest_daily_log(self, path: Path):
        """Ingest a daily log file, capturing new content."""
        from conversation_ingester import ConversationIngester
        
        ingester = ConversationIngester()
        count = ingester.ingest_daily_log(path)
        
        if count > 0:
            print(f"📝 Ingested {count} new messages from {path.name}")
            self.state.increment_events()
    
    def run_extraction(self):
        """Run the extraction pipeline."""
        print("🧠 Running extraction...")
        try:
            stats = run_extraction()
            self.state.mark_extraction()
            print(f"   ✅ Extracted {stats['facts']} facts, {stats['entities']} entities")
        except Exception as e:
            print(f"   ❌ Extraction error: {e}")
    
    def start(self, daemon_mode: bool = False):
        """Start the memory daemon."""
        if daemon_mode:
            self._daemonize()
        
        self.running = True
        self.state.state["started_at"] = datetime.now(timezone.utc).isoformat()
        self.state.save()
        
        # Write PID file
        PID_FILE.write_text(str(os.getpid()))
        atexit.register(lambda: PID_FILE.unlink(missing_ok=True))
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        # Set up file watcher
        self.observer = Observer()
        handler = MemoryFileHandler(self)
        
        # Watch memory directory
        if MEMORY_DIR.exists():
            self.observer.schedule(handler, str(MEMORY_DIR), recursive=True)
        
        # Watch core files directory
        self.observer.schedule(handler, str(CLAWD_DIR), recursive=False)
        
        self.observer.start()
        
        print(f"🏛️ Atlas Memory Daemon started (PID: {os.getpid()})")
        print(f"   Watching: {MEMORY_DIR}")
        print(f"   Poll interval: {POLL_INTERVAL}s")
        print(f"   Extraction threshold: {EXTRACTION_THRESHOLD} events")
        print()
        
        # Main loop
        try:
            while self.running:
                # Periodic check for daily log updates
                self._check_daily_logs()
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def _check_daily_logs(self):
        """Check for new daily log entries."""
        today = datetime.now().strftime("%Y-%m-%d")
        today_log = MEMORY_DIR / f"{today}.md"
        
        if today_log.exists():
            self.handle_file_change(today_log, "modified")
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📛 Received signal {signum}, shutting down...")
        self.running = False
    
    def _daemonize(self):
        """Fork into background daemon."""
        # First fork
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        
        # Decouple from parent
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # Second fork
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        log_file = Path(__file__).parent.parent / "data" / "daemon.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open('/dev/null', 'r') as devnull:
            os.dup2(devnull.fileno(), sys.stdin.fileno())
        
        with open(log_file, 'a') as log:
            os.dup2(log.fileno(), sys.stdout.fileno())
            os.dup2(log.fileno(), sys.stderr.fileno())
    
    def stop(self):
        """Stop the daemon."""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        PID_FILE.unlink(missing_ok=True)
        print("🏛️ Atlas Memory Daemon stopped")


def get_status() -> dict:
    """Get daemon status."""
    status = {
        "running": False,
        "pid": None,
        "started_at": None,
        "events_captured": 0,
        "events_since_extraction": 0,
        "last_extraction": None
    }
    
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        # Check if process is running
        try:
            os.kill(pid, 0)
            status["running"] = True
            status["pid"] = pid
        except OSError:
            pass
    
    # Load state
    state = DaemonState()
    status["started_at"] = state.state.get("started_at")
    status["events_captured"] = state.state.get("total_events_captured", 0)
    status["events_since_extraction"] = state.state.get("events_since_extraction", 0)
    status["last_extraction"] = state.state.get("last_extraction")
    
    return status


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Atlas Memory Daemon")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run in background")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--stop", action="store_true", help="Stop daemon")
    
    args = parser.parse_args()
    
    if args.status:
        status = get_status()
        print("🏛️ Atlas Memory Daemon Status")
        print(f"   Running: {'✅ Yes' if status['running'] else '❌ No'}")
        if status['running']:
            print(f"   PID: {status['pid']}")
        print(f"   Started: {status['started_at'] or 'Never'}")
        print(f"   Events captured: {status['events_captured']}")
        print(f"   Since last extraction: {status['events_since_extraction']}")
        print(f"   Last extraction: {status['last_extraction'] or 'Never'}")
        return
    
    if args.stop:
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ Sent SIGTERM to PID {pid}")
            except OSError as e:
                print(f"❌ Could not stop daemon: {e}")
                PID_FILE.unlink(missing_ok=True)
        else:
            print("❌ Daemon not running")
        return
    
    # Start daemon
    daemon = MemoryDaemon()
    daemon.start(daemon_mode=args.daemon)


if __name__ == "__main__":
    main()
