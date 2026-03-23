#!/usr/bin/env python3
"""Test both feed monitors with a single poll cycle."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("ATLAS INTEL FEED MONITORS - TEST RUN")
print("=" * 70)

print("\n[1/2] Testing GDELT Monitor...")
print("-" * 70)
try:
    from feeds.gdelt_monitor import poll_gdelt
    events = poll_gdelt()
    print(f"✓ GDELT Monitor: {events} events detected")
except Exception as exc:
    print(f"✗ GDELT Monitor failed: {exc}")
    import traceback
    traceback.print_exc()

print("\n[2/2] Testing Economic Feeds Monitor...")
print("-" * 70)
try:
    from feeds.economic_feeds import poll_economic_feeds
    events = poll_economic_feeds()
    print(f"✓ Economic Feeds Monitor: {events} events detected")
except Exception as exc:
    print(f"✗ Economic Feeds Monitor failed: {exc}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nCheck logs:")
print("  - logs/gdelt_events.jsonl")
print("  - logs/economic_events.jsonl")
print("  - logs/gdelt_monitor.log")
print("  - logs/economic_feeds.log")
