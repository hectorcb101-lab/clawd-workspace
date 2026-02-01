#!/usr/bin/env python3
"""
Conversation Ingester
=====================
Reads conversation history and ingests it into the event log.

This is how I capture real conversations without modifying Clawdbot.
Can be run periodically to capture new messages.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Set, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from event_schema import Event, EventType, message_in, message_out
from event_log import get_log


class ConversationIngester:
    """
    Ingests conversations from various sources into the event log.
    
    Tracks what's already been ingested to avoid duplicates.
    """
    
    def __init__(self):
        self.event_log = get_log()
        self.state_file = Path(__file__).parent.parent / "data" / "ingester_state.json"
        self.ingested_hashes: Set[str] = self._load_state()
    
    def _load_state(self) -> Set[str]:
        """Load set of already-ingested message hashes."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    return set(data.get("ingested_hashes", []))
            except (json.JSONDecodeError, KeyError):
                pass
        return set()
    
    def _save_state(self):
        """Save ingested hashes to avoid re-ingesting."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                "ingested_hashes": list(self.ingested_hashes),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
    
    def _hash_message(self, content: str, timestamp: str = None) -> str:
        """Create a hash to identify unique messages."""
        data = f"{content}:{timestamp or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def ingest_message(
        self, 
        content: str, 
        direction: str,  # "in" or "out"
        source: str = "telegram",
        user: str = None,
        timestamp: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Ingest a single message if not already ingested.
        Returns event ID if ingested, None if duplicate.
        """
        msg_hash = self._hash_message(content, timestamp)
        
        if msg_hash in self.ingested_hashes:
            return None  # Already ingested
        
        # Create appropriate event
        if direction == "in":
            event = message_in(content, source=source, user=user, **(metadata or {}))
        else:
            event = message_out(content, source=source, **(metadata or {}))
        
        # Override timestamp if provided
        if timestamp:
            event.timestamp = timestamp
        
        # Log it
        event_id = self.event_log.append(event)
        
        # Mark as ingested
        self.ingested_hashes.add(msg_hash)
        self._save_state()
        
        return event_id
    
    def ingest_conversation(self, messages: List[Dict[str, Any]], source: str = "telegram") -> int:
        """
        Ingest a list of messages.
        
        Expected format:
        [
            {"role": "user", "content": "...", "timestamp": "..."},
            {"role": "assistant", "content": "...", "timestamp": "..."},
            ...
        ]
        
        Returns count of new messages ingested.
        """
        ingested_count = 0
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp")
            user = msg.get("user")
            
            # Skip empty messages
            if not content or not content.strip():
                continue
            
            # Determine direction
            direction = "in" if role in ("user", "human") else "out"
            
            # Ingest
            event_id = self.ingest_message(
                content=content,
                direction=direction,
                source=source,
                user=user,
                timestamp=timestamp
            )
            
            if event_id:
                ingested_count += 1
        
        return ingested_count
    
    def ingest_from_file(self, file_path: str, source: str = "file") -> int:
        """
        Ingest messages from a JSON file.
        """
        with open(file_path) as f:
            data = json.load(f)
        
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict) and "messages" in data:
            messages = data["messages"]
        else:
            raise ValueError(f"Unknown format in {file_path}")
        
        return self.ingest_conversation(messages, source)
    
    def ingest_daily_log(self, log_path: str) -> int:
        """
        Ingest key events from a daily markdown log.
        Extracts headers and significant content.
        """
        ingested = 0
        
        with open(log_path) as f:
            content = f.read()
        
        # Extract date from filename
        filename = Path(log_path).stem  # e.g., "2026-02-01"
        
        # Find all headers and their content
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section
                if current_section and section_content:
                    summary = f"{current_section}: {' '.join(section_content)[:200]}"
                    event = Event(
                        type=EventType.LEARNING,
                        source="daily_log",
                        content={
                            "date": filename,
                            "section": current_section,
                            "summary": summary
                        }
                    )
                    
                    # Check if already ingested
                    msg_hash = self._hash_message(summary, filename)
                    if msg_hash not in self.ingested_hashes:
                        self.event_log.append(event)
                        self.ingested_hashes.add(msg_hash)
                        ingested += 1
                
                current_section = line[3:].strip()
                section_content = []
            elif line.strip() and current_section:
                section_content.append(line.strip())
        
        # Save final section
        if current_section and section_content:
            summary = f"{current_section}: {' '.join(section_content)[:200]}"
            msg_hash = self._hash_message(summary, filename)
            if msg_hash not in self.ingested_hashes:
                event = Event(
                    type=EventType.LEARNING,
                    source="daily_log",
                    content={
                        "date": filename,
                        "section": current_section,
                        "summary": summary
                    }
                )
                self.event_log.append(event)
                self.ingested_hashes.add(msg_hash)
                ingested += 1
        
        self._save_state()
        return ingested
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            "total_ingested": len(self.ingested_hashes),
            "state_file": str(self.state_file)
        }


def ingest_all_daily_logs():
    """Ingest all daily log files."""
    ingester = ConversationIngester()
    memory_dir = Path("/home/ubuntu/clawd/memory")
    
    total = 0
    for log_file in sorted(memory_dir.glob("2026-*.md")):
        if log_file.name.count("-") == 2:  # Only date files like 2026-01-30.md
            count = ingester.ingest_daily_log(str(log_file))
            if count > 0:
                print(f"  {log_file.name}: {count} events")
            total += count
    
    return total


if __name__ == "__main__":
    print("Testing Conversation Ingester...")
    
    ingester = ConversationIngester()
    
    # Test single message ingestion
    print("\n--- Ingesting test messages ---")
    
    id1 = ingester.ingest_message("Hello, this is a test", "in", user="Finn")
    print(f"Message 1: {id1 or 'already ingested'}")
    
    id2 = ingester.ingest_message("I received your test message", "out")
    print(f"Message 2: {id2 or 'already ingested'}")
    
    # Try duplicate
    id3 = ingester.ingest_message("Hello, this is a test", "in", user="Finn")
    print(f"Duplicate: {id3 or 'already ingested'}")
    
    # Test conversation ingestion
    print("\n--- Ingesting conversation ---")
    convo = [
        {"role": "user", "content": "What's the weather?", "user": "Finn"},
        {"role": "assistant", "content": "I'll check for you..."},
        {"role": "user", "content": "Thanks!"},
    ]
    count = ingester.ingest_conversation(convo, source="test")
    print(f"Ingested {count} new messages from conversation")
    
    # Stats
    print("\n--- Stats ---")
    stats = ingester.get_stats()
    print(f"  Total ingested: {stats['total_ingested']}")
    
    # Ingest real daily logs
    print("\n--- Ingesting daily logs ---")
    log_count = ingest_all_daily_logs()
    print(f"Total from daily logs: {log_count}")
    
    print("\n✅ Conversation Ingester tests passed!")
