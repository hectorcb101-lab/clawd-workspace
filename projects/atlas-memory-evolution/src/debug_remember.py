#!/usr/bin/env python3
import sys
from pathlib import Path

# Same setup as atlas_memory.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
print(f"Path: {sys.path[0]}")

# Now cd to the src directory
import os
os.chdir(str(Path(__file__).resolve().parent))

from event_log import get_log
from event_schema import EventType, Event
from extractor import run_extraction

# Log event
log = get_log()
event = Event(
    type=EventType.LEARNING,
    content={"summary": "DEBUG_REMEMBER_TEST_555", "details": None},
    source="debug"
)
event_id = log.append(event)
print(f"Logged: {event_id}")

# Run extraction with debug
print("Running extraction...")
result = run_extraction()
print(f"Result: {result}")

# Check facts
facts_file = Path("../data/knowledge/facts.jsonl")
if "DEBUG_REMEMBER_TEST_555" in facts_file.read_text():
    print("✅ Found in facts!")
else:
    print("❌ Not in facts")
