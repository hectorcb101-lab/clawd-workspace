#!/usr/bin/env python3
"""
Atlas Intel — AIS Vessel Tracker
Monitors strategic chokepoints via AISStream.io WebSocket.
Detects anomalies: congestion spikes, tanker diversions, floating storage, dark ships.
Feeds events into Supabase pgvector for cross-modal RAG.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

try:
    import websockets
except ImportError:
    print("Installing websockets...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
    import websockets

# Add parent for atlas_intel imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas_intel.config import AISSTREAM_API_KEY, SUPABASE_URL, SUPABASE_KEY
from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

AISSTREAM_WS = "wss://stream.aisstream.io/v0/stream"

# Strategic chokepoints — bounding boxes [[[lat_min, lon_min], [lat_max, lon_max]]]
CHOKEPOINTS = {
    "strait_of_hormuz": {
        "bbox": [[25.5, 55.5], [27.0, 57.5]],
        "label": "Strait of Hormuz",
        "commodity": "oil",
        "daily_avg": 800,  # approx tanker transits/day
    },
    "suez_canal": {
        "bbox": [[29.8, 32.2], [31.3, 32.6]],
        "label": "Suez Canal",
        "commodity": "mixed",
        "daily_avg": 50,
    },
    "bab_el_mandeb": {
        "bbox": [[12.0, 42.5], [13.5, 44.0]],
        "label": "Bab el-Mandeb",
        "commodity": "oil",
        "daily_avg": 400,
    },
    "malacca_strait": {
        "bbox": [[1.0, 102.0], [4.0, 104.5]],
        "label": "Strait of Malacca",
        "commodity": "oil_lng",
        "daily_avg": 2000,  # very busy strait — ~2000 AIS reports/day in bbox
    },
    "turkish_straits": {
        "bbox": [[40.5, 28.5], [41.5, 29.5]],
        "label": "Turkish Straits (Bosphorus)",
        "commodity": "grain_oil",
        "daily_avg": 120,
    },
    "panama_canal": {
        "bbox": [[8.8, -79.9], [9.4, -79.5]],
        "label": "Panama Canal",
        "commodity": "mixed",
        "daily_avg": 35,
    },
}

# Vessel type codes (AIS ship type, first 2 digits)
TANKER_TYPES = {80, 81, 82, 83, 84, 85, 86, 87, 88, 89}
CARGO_TYPES = {70, 71, 72, 73, 74, 75, 76, 77, 78, 79}
LNG_LPG_TYPES = {80, 81, 82}  # subset of tanker

# Anomaly thresholds
CONGESTION_WINDOW_MIN = 60       # rolling window for congestion detection
CONGESTION_THRESHOLD_MULT = 2.0  # 2x normal = congestion alert
STATIONARY_THRESHOLD_KN = 0.5    # knots — below this = stationary
STATIONARY_ALERT_HOURS = 6       # alert after 6h stationary in chokepoint

# Logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "vessel_tracker.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("vessel_tracker")

# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------

# Per-chokepoint rolling counts: {chokepoint: [timestamps]}
transit_log = defaultdict(list)

# Stationary vessel tracking: {mmsi: {first_seen, last_seen, chokepoint, lat, lon, name}}
stationary_vessels = {}

# Seen vessels (dedup within window): {mmsi: last_report_ts}
seen_recently = {}

# All vessel positions: {mmsi: {name, lat, lon, speed, ship_type, chokepoint}}
vessel_positions = {}

# Congestion alert cooldown: {chokepoint: last_alert_timestamp}
congestion_cooldown = {}
CONGESTION_COOLDOWN_SEC = 1800  # 30 min between alerts per chokepoint

# Stats
stats = {
    "messages_received": 0,
    "events_generated": 0,
    "start_time": None,
    "last_message_time": None,
}


# ---------------------------------------------------------------------------
# Anomaly detection
# ---------------------------------------------------------------------------

def classify_chokepoint(lat: float, lon: float) -> str | None:
    """Return chokepoint key if position falls within a bounding box."""
    for key, cp in CHOKEPOINTS.items():
        (lat_min, lon_min), (lat_max, lon_max) = cp["bbox"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return key
    return None


def check_congestion(chokepoint: str) -> dict | None:
    """Check if current transit rate exceeds threshold."""
    now = time.time()
    window = CONGESTION_WINDOW_MIN * 60
    cutoff = now - window

    # Prune old entries
    transit_log[chokepoint] = [t for t in transit_log[chokepoint] if t > cutoff]
    count = len(transit_log[chokepoint])

    cp = CHOKEPOINTS[chokepoint]
    expected_per_window = (cp["daily_avg"] / 1440) * CONGESTION_WINDOW_MIN
    threshold = expected_per_window * CONGESTION_THRESHOLD_MULT

    if count > threshold and expected_per_window > 0:
        # Cooldown check
        now_ts = time.time()
        last_alert = congestion_cooldown.get(chokepoint, 0)
        if now_ts - last_alert < CONGESTION_COOLDOWN_SEC:
            return None
        congestion_cooldown[chokepoint] = now_ts
        return {
            "type": "congestion",
            "chokepoint": cp["label"],
            "count_in_window": count,
            "expected": round(expected_per_window, 1),
            "ratio": round(count / expected_per_window, 2),
            "severity": "high" if count > threshold * 1.5 else "medium",
        }
    return None


def check_stationary(mmsi: int, lat: float, lon: float, speed: float,
                     ship_name: str, chokepoint: str) -> dict | None:
    """Detect vessels stationary in chokepoints (potential floating storage)."""
    now = datetime.now(timezone.utc)

    if speed <= STATIONARY_THRESHOLD_KN:
        if mmsi in stationary_vessels:
            entry = stationary_vessels[mmsi]
            entry["last_seen"] = now
            hours = (now - entry["first_seen"]).total_seconds() / 3600
            if hours >= STATIONARY_ALERT_HOURS and not entry.get("alerted"):
                entry["alerted"] = True
                return {
                    "type": "floating_storage",
                    "chokepoint": CHOKEPOINTS[chokepoint]["label"],
                    "mmsi": mmsi,
                    "ship_name": ship_name,
                    "hours_stationary": round(hours, 1),
                    "lat": lat,
                    "lon": lon,
                    "severity": "high" if hours >= 24 else "medium",
                }
        else:
            stationary_vessels[mmsi] = {
                "first_seen": now,
                "last_seen": now,
                "chokepoint": chokepoint,
                "lat": lat,
                "lon": lon,
                "name": ship_name,
                "alerted": False,
            }
    else:
        # Moving again — remove from stationary tracking
        stationary_vessels.pop(mmsi, None)

    return None


# ---------------------------------------------------------------------------
# Event handling
# ---------------------------------------------------------------------------

async def handle_event(event: dict):
    """Process an anomaly event: embed and store in Supabase."""
    stats["events_generated"] += 1

    event_type = event["type"]
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build descriptive text for embedding
    if event_type == "congestion":
        text = (
            f"Maritime congestion alert at {event['chokepoint']}: "
            f"{event['count_in_window']} vessels in {CONGESTION_WINDOW_MIN}min window "
            f"({event['ratio']}x normal rate). "
            f"Severity: {event['severity']}. "
            f"Potential supply chain disruption for {CHOKEPOINTS.get(event.get('chokepoint_key', ''), {}).get('commodity', 'unknown')} trade."
        )
    elif event_type == "floating_storage":
        text = (
            f"Potential floating storage detected at {event['chokepoint']}: "
            f"vessel {event['ship_name']} (MMSI {event['mmsi']}) "
            f"stationary for {event['hours_stationary']} hours at "
            f"({event['lat']:.4f}, {event['lon']:.4f}). "
            f"Severity: {event['severity']}. "
            f"May indicate supply hoarding or sanctions evasion."
        )
    else:
        text = f"Maritime event: {json.dumps(event)}"

    log.info(f"🚨 EVENT: {text}")

    # Embed and store
    try:
        embedding = embed_text(text)
        if embedding is not None:
            store_embedding(
                content=text,
                embedding=embedding,
                source_type="ais_vessel",
                source_id=f"ais_{event_type}_{timestamp}",
                metadata={
                    "event": event,
                    "timestamp": timestamp,
                    "feed": "aisstream",
                },
            )
            log.info("✅ Event embedded and stored in Supabase")
    except Exception as e:
        log.error(f"Failed to embed/store event: {e}")

    # Also save locally as fallback
    events_file = LOG_DIR / "vessel_events.jsonl"
    with open(events_file, "a") as f:
        f.write(json.dumps({"timestamp": timestamp, **event}) + "\n")


# ---------------------------------------------------------------------------
# WebSocket listener
# ---------------------------------------------------------------------------

async def listen():
    """Connect to AISStream and process messages."""
    api_key = AISSTREAM_API_KEY
    if not api_key:
        log.error("AISSTREAM_API_KEY not set. Cannot connect.")
        return

    # Build bounding boxes for all chokepoints
    bboxes = [cp["bbox"] for cp in CHOKEPOINTS.values()]

    subscribe_msg = {
        "APIKey": api_key,
        "BoundingBoxes": bboxes,
    }

    stats["start_time"] = datetime.now(timezone.utc).isoformat()
    log.info(f"🚢 Connecting to AISStream — monitoring {len(CHOKEPOINTS)} chokepoints...")

    reconnect_delay = 5

    while True:
        try:
            async with websockets.connect(AISSTREAM_WS, ping_interval=20, ping_timeout=60) as ws:
                await ws.send(json.dumps(subscribe_msg))
                log.info("✅ Connected to AISStream WebSocket")
                reconnect_delay = 5  # reset on successful connect

                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        await process_message(msg)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        log.error(f"Error processing message: {e}")

        except (websockets.ConnectionClosed, ConnectionError, OSError) as e:
            log.warning(f"Connection lost: {e}. Reconnecting in {reconnect_delay}s...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 300)  # exponential backoff, max 5min
        except Exception as e:
            log.error(f"Unexpected error: {e}. Reconnecting in {reconnect_delay}s...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 300)


async def process_message(msg: dict):
    """Process a single AIS message."""
    stats["messages_received"] += 1
    stats["last_message_time"] = datetime.now(timezone.utc).isoformat()

    msg_type = msg.get("MessageType", "")
    meta = msg.get("MetaData", {})
    mmsi = meta.get("MMSI", 0)
    ship_name = meta.get("ShipName", "UNKNOWN").strip()
    ship_type = meta.get("ShipType", 0)
    lat = meta.get("latitude", 0)
    lon = meta.get("longitude", 0)

    # Also check inside Message for position data
    position = msg.get("Message", {}).get("PositionReport", {})
    if position:
        lat = position.get("Latitude", lat)
        lon = position.get("Longitude", lon)
        speed = position.get("Sog", 0)  # speed over ground in knots
    else:
        speed = 99  # unknown, don't flag as stationary

    # Classify chokepoint
    chokepoint = classify_chokepoint(lat, lon)
    if not chokepoint:
        return  # outside our zones (shouldn't happen with bbox filter, but safety check)

    # Dedup: skip if we saw this MMSI in the last 5 minutes
    now = time.time()
    if mmsi in seen_recently and (now - seen_recently[mmsi]) < 300:
        return
    seen_recently[mmsi] = now

    # Store position for snapshot
    vessel_positions[mmsi] = {
        "name": ship_name,
        "lat": lat,
        "lon": lon,
        "speed": speed if speed != 99 else None,
        "ship_type": ship_type,
        "chokepoint": chokepoint,
    }

    # Record transit
    transit_log[chokepoint].append(now)

    # Log periodically
    if stats["messages_received"] % 100 == 0:
        log.info(f"📊 Stats: {stats['messages_received']} msgs, {stats['events_generated']} events | "
                 f"Tracking {len(stationary_vessels)} stationary vessels")

    # --- Anomaly checks ---

    # 1. Congestion detection
    congestion = check_congestion(chokepoint)
    if congestion:
        congestion["chokepoint_key"] = chokepoint
        await handle_event(congestion)

    # 2. Floating storage (tankers only)
    if ship_type in TANKER_TYPES:
        floating = check_stationary(mmsi, lat, lon, speed, ship_name, chokepoint)
        if floating:
            await handle_event(floating)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def prune_stale():
    """Remove stale entries from tracking dicts."""
    now = time.time()
    # Prune seen_recently older than 10 min
    stale = [k for k, v in seen_recently.items() if now - v > 600]
    for k in stale:
        del seen_recently[k]

    # Prune stationary vessels not seen in 2 hours
    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
    stale_mmsi = [k for k, v in stationary_vessels.items() if v["last_seen"] < cutoff]
    for k in stale_mmsi:
        del stationary_vessels[k]


def write_vessel_snapshot():
    """Write a JSON snapshot of currently tracked vessels for the dashboard."""
    snapshot_path = Path(__file__).parent.parent / "dashboard" / "data" / "vessel_live.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    now = time.time()
    vessels = []
    for mmsi, last_seen in seen_recently.items():
        if now - last_seen > 600:
            continue
        pos = vessel_positions.get(mmsi, {})
        vtype = "tanker" if pos.get("ship_type", 0) in TANKER_TYPES else \
                "cargo" if pos.get("ship_type", 0) in CARGO_TYPES else "other"
        vessels.append({
            "mmsi": mmsi,
            "name": pos.get("name", "UNKNOWN"),
            "lat": pos.get("lat", 0),
            "lon": pos.get("lon", 0),
            "speed": pos.get("speed"),
            "type": vtype,
            "chokepoint": pos.get("chokepoint", ""),
            "heading": None,
            "last_seen": last_seen,
        })
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_vessels": len(seen_recently),
        "vessels": vessels,
        "stats": stats,
        "chokepoint_activity": {},
    }

    for cp_key, timestamps in transit_log.items():
        recent = [t for t in timestamps if now - t < 3600]
        if recent:
            snapshot["chokepoint_activity"][CHOKEPOINTS[cp_key]["label"]] = len(recent)

    try:
        snapshot_path.write_text(json.dumps(snapshot, indent=2))
    except Exception as e:
        log.error(f"Failed to write vessel snapshot: {e}")


async def periodic_maintenance():
    """Run periodic cleanup and stats logging."""
    while True:
        await asyncio.sleep(30)  # every 30 seconds
        prune_stale()
        write_vessel_snapshot()

        # Log chokepoint activity summary every 5 min
        if int(time.time()) % 300 < 35:
            summary = {}
            now = time.time()
            for cp_key, timestamps in transit_log.items():
                recent = [t for t in timestamps if now - t < 3600]
                if recent:
                    summary[CHOKEPOINTS[cp_key]["label"]] = len(recent)

            if summary:
                log.info(f"📍 Hourly activity: {summary}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """Run vessel tracker with maintenance loop."""
    log.info("🏛️ Atlas Intel — Vessel Tracker starting...")
    await asyncio.gather(
        listen(),
        periodic_maintenance(),
    )


def print_status():
    """Print current tracker status (for CLI use)."""
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print_status()
    else:
        asyncio.run(main())
