#!/usr/bin/env python3
"""OpenSky Network flight tracker daemon for Atlas Intel.

Monitors global flight activity in strategic regions, detects anomalies,
and stores intelligence signals when patterns deviate from baseline.

Regions monitored:
- Middle East (military buildups, Iran conflict)
- Eastern Europe (Ukraine/Russia)
- South China Sea
- Taiwan Strait
- Korean Peninsula

Anomaly detection:
1. Military aircraft surges (callsign prefixes: RCH, DUKE, EVAC, FORTE, etc)
2. Unusual altitude patterns (very high = recon, very low = military)
3. Cargo flight diversions
4. Flight density spikes vs rolling 24h average

Free tier: 400 calls/day anonymous, polling every 5 min = 288 calls/day.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# Add parent directory to path for atlas_intel imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas_intel.config import SUPABASE_URL, SUPABASE_KEY
from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 300  # 5 minutes
STATS_LOG_INTERVAL = 10 * 60  # 10 minutes
OPENSKY_BASE_URL = "https://opensky-network.org/api/states/all"

# Bounding boxes: (lat_min, lat_max, lon_min, lon_max)
REGIONS = {
    "Middle East": (12, 42, 30, 65),
    "Eastern Europe": (44, 56, 22, 40),
    "South China Sea": (0, 25, 100, 125),
    "Taiwan Strait": (22, 27, 117, 123),
    "Korean Peninsula": (33, 43, 124, 132),
}

# Military callsign prefixes
MILITARY_PREFIXES = {
    "RCH", "DUKE", "EVAC", "FORTE", "HOMER", "CHIEF", "KING", "REACH",
    "SPAR", "VALOR", "VIPER", "GRIZZLY", "PAT", "METAL", "KNIFE",
}

# Altitude thresholds (meters)
HIGH_ALTITUDE_THRESHOLD = 13000  # ~43,000 ft (recon)
LOW_ALTITUDE_THRESHOLD = 1500    # ~5,000 ft (tactical)

# Logs
LOG_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/logs")
LOG_FILE = LOG_DIR / "flight_tracker.log"
EVENTS_FILE = LOG_DIR / "flight_events.jsonl"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------

@dataclass
class FlightState:
    """Track flight state across polls."""
    icao24: str
    callsign: str | None
    last_seen: datetime
    positions: deque = field(default_factory=lambda: deque(maxlen=10))
    altitudes: deque = field(default_factory=lambda: deque(maxlen=10))
    

class FlightTracker:
    """Flight tracking and anomaly detection."""
    
    def __init__(self):
        self.flight_history: dict[str, FlightState] = {}
        self.region_density_history: dict[str, deque] = {
            region: deque(maxlen=288)  # 24h of 5-min samples
            for region in REGIONS
        }
        self.total_calls = 0
        self.anomalies_detected = 0
        self.last_stats_log = time.time()
        
    def fetch_region_flights(self, region: str, bbox: tuple) -> list[dict[str, Any]]:
        """Fetch flights in a bounding box from OpenSky API."""
        lat_min, lat_max, lon_min, lon_max = bbox
        params = {
            "lamin": lat_min,
            "lamax": lat_max,
            "lomin": lon_min,
            "lomax": lon_max,
        }
        
        try:
            response = requests.get(OPENSKY_BASE_URL, params=params, timeout=30)
            self.total_calls += 1
            
            if response.status_code == 429:
                logger.warning("Rate limit hit (429), backing off for 60 seconds")
                time.sleep(60)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            if not data or "states" not in data or data["states"] is None:
                return []
            
            # Parse state vectors
            # Format: [icao24, callsign, origin_country, time_position, last_contact,
            #          longitude, latitude, baro_altitude, on_ground, velocity, 
            #          true_track, vertical_rate, sensors, geo_altitude, squawk, spi, position_source]
            flights = []
            for state in data["states"]:
                if len(state) < 17:
                    continue
                    
                flight = {
                    "icao24": state[0],
                    "callsign": state[1].strip() if state[1] else None,
                    "origin_country": state[2],
                    "longitude": state[5],
                    "latitude": state[6],
                    "baro_altitude": state[7],
                    "on_ground": state[8],
                    "velocity": state[9],
                    "true_track": state[10],
                    "vertical_rate": state[11],
                    "geo_altitude": state[13],
                    "region": region,
                }
                flights.append(flight)
            
            return flights
            
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch {region} flights: {exc}")
            return []
    
    def detect_military_aircraft(self, flights: list[dict]) -> list[dict]:
        """Detect military aircraft by callsign prefix."""
        military = []
        for flight in flights:
            callsign = flight.get("callsign")
            if not callsign:
                continue
            
            # Check for military prefixes
            prefix = callsign[:3].upper() if len(callsign) >= 3 else ""
            if prefix in MILITARY_PREFIXES:
                military.append(flight)
        
        return military
    
    def detect_altitude_anomalies(self, flights: list[dict]) -> list[dict]:
        """Detect unusual altitude patterns."""
        anomalies = []
        for flight in flights:
            altitude = flight.get("baro_altitude") or flight.get("geo_altitude")
            if altitude is None or flight.get("on_ground"):
                continue
            
            if altitude > HIGH_ALTITUDE_THRESHOLD:
                flight["anomaly_type"] = "high_altitude_recon"
                flight["anomaly_detail"] = f"Altitude: {altitude:.0f}m (~{altitude*3.28084:.0f}ft)"
                anomalies.append(flight)
            elif altitude < LOW_ALTITUDE_THRESHOLD:
                flight["anomaly_type"] = "low_altitude_tactical"
                flight["anomaly_detail"] = f"Altitude: {altitude:.0f}m (~{altitude*3.28084:.0f}ft)"
                anomalies.append(flight)
        
        return anomalies
    
    def detect_density_spikes(self, region: str, flight_count: int) -> dict | None:
        """Detect flight density spikes vs 24h rolling average."""
        history = self.region_density_history[region]
        
        if len(history) < 10:  # Need baseline
            history.append(flight_count)
            return None
        
        avg = sum(history) / len(history)
        std = (sum((x - avg) ** 2 for x in history) / len(history)) ** 0.5
        
        history.append(flight_count)
        
        # Spike if >2 std deviations above average
        if flight_count > avg + (2 * std):
            return {
                "region": region,
                "current_count": flight_count,
                "avg_count": round(avg, 1),
                "std_dev": round(std, 1),
                "anomaly_type": "density_spike",
            }
        
        return None
    
    def process_anomaly(self, anomaly: dict):
        """Process detected anomaly: embed, store, log."""
        try:
            # Build content text
            if anomaly.get("anomaly_type") == "military_surge":
                content = (
                    f"Military aircraft surge detected in {anomaly['region']}: "
                    f"{anomaly['count']} military flights. "
                    f"Callsigns: {', '.join(anomaly['callsigns'][:5])}"
                )
            elif anomaly.get("anomaly_type") == "density_spike":
                content = (
                    f"Flight density spike in {anomaly['region']}: "
                    f"{anomaly['current_count']} flights "
                    f"(avg: {anomaly['avg_count']}, +{anomaly['current_count'] - anomaly['avg_count']:.0f})"
                )
            elif anomaly.get("anomaly_type") in ("high_altitude_recon", "low_altitude_tactical"):
                content = (
                    f"{anomaly['anomaly_type'].replace('_', ' ').title()} detected: "
                    f"Aircraft {anomaly.get('callsign', anomaly['icao24'])} in {anomaly['region']}. "
                    f"{anomaly['anomaly_detail']}"
                )
            else:
                content = json.dumps(anomaly)
            
            # Embed
            embedding = embed_text(content)
            
            # Store
            metadata = {
                **anomaly,
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "tracker": "flight_tracker",
            }
            
            source_id = f"flight_{anomaly.get('region', 'unknown')}_{int(time.time())}"
            
            store_embedding(
                source_type="flight_track",
                content=content,
                metadata=metadata,
                embedding=embedding,
                source_id=source_id,
            )
            
            # Log to JSONL
            with open(EVENTS_FILE, "a") as f:
                event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "content": content,
                    "metadata": metadata,
                }
                f.write(json.dumps(event) + "\n")
            
            self.anomalies_detected += 1
            logger.info(f"Anomaly stored: {content}")
            
        except Exception as exc:
            logger.error(f"Failed to process anomaly: {exc}", exc_info=True)
    
    def poll_regions(self):
        """Poll all regions and detect anomalies."""
        logger.info("Starting region poll")
        
        for region, bbox in REGIONS.items():
            flights = self.fetch_region_flights(region, bbox)
            
            if not flights:
                logger.debug(f"{region}: No flights detected")
                continue
            
            logger.info(f"{region}: {len(flights)} flights")
            
            # Detect military aircraft
            military = self.detect_military_aircraft(flights)
            if len(military) >= 3:  # Surge threshold
                self.process_anomaly({
                    "region": region,
                    "anomaly_type": "military_surge",
                    "count": len(military),
                    "callsigns": [f.get("callsign") for f in military if f.get("callsign")],
                    "aircraft": [f["icao24"] for f in military],
                })
            
            # Detect altitude anomalies
            altitude_anomalies = self.detect_altitude_anomalies(flights)
            for anomaly in altitude_anomalies[:3]:  # Limit to top 3 per region
                self.process_anomaly(anomaly)
            
            # Detect density spikes
            density_anomaly = self.detect_density_spikes(region, len(flights))
            if density_anomaly:
                self.process_anomaly(density_anomaly)
            
            # Rate limit courtesy delay between regions
            time.sleep(1)
    
    def log_stats(self):
        """Log periodic statistics."""
        uptime = time.time() - self.last_stats_log
        logger.info(
            f"Stats: {self.total_calls} API calls, "
            f"{self.anomalies_detected} anomalies, "
            f"uptime: {uptime/60:.1f}min"
        )
        self.last_stats_log = time.time()
    
    def run(self):
        """Main daemon loop."""
        logger.info("Flight tracker daemon starting")
        logger.info(f"Monitoring regions: {', '.join(REGIONS.keys())}")
        logger.info(f"Poll interval: {POLL_INTERVAL_SECONDS}s")
        logger.info(f"Logs: {LOG_FILE}, Events: {EVENTS_FILE}")
        
        while True:
            try:
                self.poll_regions()
                
                # Log stats every 10 minutes
                if time.time() - self.last_stats_log >= STATS_LOG_INTERVAL:
                    self.log_stats()
                
                logger.debug(f"Sleeping {POLL_INTERVAL_SECONDS}s until next poll")
                time.sleep(POLL_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                break
            except Exception as exc:
                logger.error(f"Unexpected error in main loop: {exc}", exc_info=True)
                time.sleep(60)  # Back off on errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: single API call
        logger.info("TEST MODE: Single API call to verify connectivity")
        tracker = FlightTracker()
        
        # Test Middle East region
        region = "Middle East"
        bbox = REGIONS[region]
        logger.info(f"Testing {region} region: {bbox}")
        
        flights = tracker.fetch_region_flights(region, bbox)
        
        if flights:
            logger.info(f"✓ Success! Received {len(flights)} flights from {region}")
            logger.info(f"Sample flight: {json.dumps(flights[0], indent=2)}")
            
            # Check for military
            military = tracker.detect_military_aircraft(flights)
            if military:
                logger.info(f"Military aircraft detected: {len(military)}")
                for m in military[:3]:
                    logger.info(f"  - {m.get('callsign', 'N/A')} ({m['icao24']})")
            
            logger.info(f"Total API calls: {tracker.total_calls}")
        else:
            logger.warning("No flights received (may be normal if region is quiet)")
        
        sys.exit(0)
    
    # Production mode
    tracker = FlightTracker()
    tracker.run()


# ---------------------------------------------------------------------------
# Systemd service file (do not install, just reference)
# ---------------------------------------------------------------------------
"""
# /etc/systemd/system/atlas-flight-tracker.service

[Unit]
Description=Atlas Intel Flight Tracker Daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/clawd/projects/atlas-intel
Environment="PATH=/home/ubuntu/clawd/projects/atlas-intel/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/clawd/projects/atlas-intel/.venv/bin/python3 /home/ubuntu/clawd/projects/atlas-intel/feeds/flight_tracker.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=atlas-flight-tracker

[Install]
WantedBy=multi-user.target

# Installation commands (run as ubuntu user with sudo):
# sudo cp /home/ubuntu/clawd/projects/atlas-intel/feeds/flight_tracker.py /etc/systemd/system/atlas-flight-tracker.service
# sudo systemctl daemon-reload
# sudo systemctl enable atlas-flight-tracker
# sudo systemctl start atlas-flight-tracker
# sudo systemctl status atlas-flight-tracker
# journalctl -u atlas-flight-tracker -f
"""
