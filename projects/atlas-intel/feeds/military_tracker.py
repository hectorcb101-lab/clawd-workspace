#!/usr/bin/env python3
"""Military activity aggregator for Atlas Intel.

Aggregates military signals from multiple sources:
- ACLED armed conflict events
- GDELT military-tagged events (GoldsteinScale < -5)
- Cross-reference with flight tracker military detections

Free tier: ACLED API free (registration required), GDELT free (unlimited).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

# Add parent directory to path for atlas_intel imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 600  # 10 minutes
ACLED_API_URL = "https://api.acleddata.com/acled/read"
GDELT_API_URL = "http://api.gdeltproject.org/api/v2/doc/doc"

# ACLED API credentials (set via environment or config)
ACLED_EMAIL = os.getenv("ACLED_EMAIL", "")
ACLED_KEY = os.getenv("ACLED_KEY", "")

# Conflict regions
REGIONS = {
    "Eastern Ukraine": {"lat": 48.5, "lng": 37.0, "bbox": (44, 52, 22, 40)},
    "Gaza": {"lat": 31.5, "lng": 34.5, "bbox": (31, 32, 34, 35)},
    "Syria": {"lat": 35.0, "lng": 38.0, "bbox": (32, 37, 36, 42)},
    "Yemen": {"lat": 15.5, "lng": 44.0, "bbox": (12, 19, 42, 54)},
    "Korean Peninsula": {"lat": 38.5, "lng": 127.0, "bbox": (33, 43, 124, 132)},
    "Taiwan Strait": {"lat": 24.5, "lng": 120.0, "bbox": (22, 27, 117, 123)},
    "South China Sea": {"lat": 12.0, "lng": 113.0, "bbox": (0, 25, 100, 125)},
}

# Intensity thresholds
INTENSITY_THRESHOLDS = {
    "LOW": 1,
    "MEDIUM": 5,
    "HIGH": 15,
    "CRITICAL": 30,
}

# Logs and output
LOG_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/logs")
OUTPUT_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data")
LOG_FILE = LOG_DIR / "military_tracker.log"
EVENTS_FILE = LOG_DIR / "military_events.jsonl"
OUTPUT_FILE = OUTPUT_DIR / "military_status.json"
FLIGHT_DATA_FILE = OUTPUT_DIR / "flight_status.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
# Military event tracking
# ---------------------------------------------------------------------------

@dataclass
class MilitaryEvent:
    """Military event data container."""
    source: str
    region: str
    lat: float
    lng: float
    event_type: str
    details: str
    timestamp: datetime
    intensity: str = "MEDIUM"


class MilitaryTracker:
    """Track and aggregate military activity signals."""
    
    def __init__(self):
        self.events: list[MilitaryEvent] = []
        self.hotspots: dict[str, list[MilitaryEvent]] = defaultdict(list)
        self.total_events = 0
        
    def fetch_acled_events(self) -> list[MilitaryEvent]:
        """Fetch armed conflict events from ACLED API."""
        events = []
        
        if not ACLED_EMAIL or not ACLED_KEY:
            logger.warning("ACLED credentials not set (ACLED_EMAIL, ACLED_KEY). Skipping ACLED fetch.")
            return events
        
        try:
            # Fetch events from last 7 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)
            
            params = {
                "key": ACLED_KEY,
                "email": ACLED_EMAIL,
                "event_date": f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
                "event_date_where": "BETWEEN",
                "limit": 500,
            }
            
            response = requests.get(ACLED_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "data" not in data:
                logger.warning("No data field in ACLED response")
                return events
            
            for item in data["data"]:
                # Extract relevant fields
                lat = float(item.get("latitude", 0))
                lng = float(item.get("longitude", 0))
                event_type = item.get("event_type", "unknown")
                notes = item.get("notes", "")
                timestamp = datetime.fromisoformat(item.get("event_date", "2024-01-01"))
                
                # Determine region
                region = self.get_region(lat, lng)
                if not region:
                    continue
                
                event = MilitaryEvent(
                    source="ACLED",
                    region=region,
                    lat=lat,
                    lng=lng,
                    event_type=event_type,
                    details=notes[:200],  # Truncate
                    timestamp=timestamp,
                )
                events.append(event)
            
            logger.info(f"Fetched {len(events)} ACLED events")
            
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch ACLED data: {exc}")
        except Exception as exc:
            logger.error(f"Error processing ACLED data: {exc}")
        
        return events
    
    def fetch_gdelt_events(self) -> list[MilitaryEvent]:
        """Fetch military-tagged events from GDELT."""
        events = []
        
        try:
            # Search for military-related events from last 24 hours
            query = "military OR conflict OR armed OR troops OR deployment"
            
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 250,
                "format": "json",
                "timespan": "24h",
            }
            
            response = requests.get(GDELT_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "articles" not in data:
                logger.warning("No articles field in GDELT response")
                return events
            
            # Process articles and extract geolocation if available
            for article in data["articles"]:
                title = article.get("title", "")
                url = article.get("url", "")
                seendate = article.get("seendate", "")
                
                # For GDELT, we don't get precise lat/lng easily
                # Use general region coordinates
                # In production, you'd use GDELT GKG for precise locations
                
                # Simple heuristic: check title for region keywords
                region = self.infer_region_from_text(title)
                if not region:
                    continue
                
                region_data = REGIONS[region]
                
                event = MilitaryEvent(
                    source="GDELT",
                    region=region,
                    lat=region_data["lat"],
                    lng=region_data["lng"],
                    event_type="military_news",
                    details=title[:200],
                    timestamp=datetime.now(timezone.utc),
                )
                events.append(event)
            
            logger.info(f"Fetched {len(events)} GDELT events")
            
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch GDELT data: {exc}")
        except Exception as exc:
            logger.error(f"Error processing GDELT data: {exc}")
        
        return events
    
    def fetch_flight_tracker_events(self) -> list[MilitaryEvent]:
        """Cross-reference with flight tracker military detections."""
        events = []
        
        try:
            if not FLIGHT_DATA_FILE.exists():
                logger.debug("Flight data file not found")
                return events
            
            with open(FLIGHT_DATA_FILE, "r") as f:
                flight_data = json.load(f)
            
            # Check for military aircraft in regions
            # This is a simplified example - in production you'd parse more detailed flight events
            if flight_data.get("status") == "online":
                logger.info("Cross-referenced with flight tracker (no specific events extracted in this example)")
            
        except Exception as exc:
            logger.error(f"Error reading flight tracker data: {exc}")
        
        return events
    
    def get_region(self, lat: float, lng: float) -> str | None:
        """Determine which region a lat/lng belongs to."""
        for region_name, region_data in REGIONS.items():
            bbox = region_data["bbox"]
            lat_min, lat_max, lon_min, lon_max = bbox
            if lat_min <= lat <= lat_max and lon_min <= lng <= lon_max:
                return region_name
        return None
    
    def infer_region_from_text(self, text: str) -> str | None:
        """Infer region from text keywords."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["ukraine", "kyiv", "donbas", "crimea"]):
            return "Eastern Ukraine"
        elif any(word in text_lower for word in ["gaza", "israel", "hamas"]):
            return "Gaza"
        elif any(word in text_lower for word in ["syria", "damascus", "aleppo"]):
            return "Syria"
        elif any(word in text_lower for word in ["yemen", "houthi", "sanaa"]):
            return "Yemen"
        elif any(word in text_lower for word in ["north korea", "south korea", "korean"]):
            return "Korean Peninsula"
        elif any(word in text_lower for word in ["taiwan", "strait"]):
            return "Taiwan Strait"
        elif any(word in text_lower for word in ["south china sea", "spratly"]):
            return "South China Sea"
        
        return None
    
    def aggregate_hotspots(self):
        """Aggregate events into regional hotspots."""
        self.hotspots.clear()
        
        for event in self.events:
            self.hotspots[event.region].append(event)
    
    def calculate_intensity(self, event_count: int) -> str:
        """Calculate intensity level based on event count."""
        if event_count >= INTENSITY_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif event_count >= INTENSITY_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif event_count >= INTENSITY_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_output(self):
        """Generate JSON output for dashboard."""
        hotspot_list = []
        
        for region, region_events in self.hotspots.items():
            if not region_events:
                continue
            
            event_count = len(region_events)
            intensity = self.calculate_intensity(event_count)
            
            # Get representative location
            region_data = REGIONS.get(region, {"lat": 0, "lng": 0})
            
            # Aggregate event details
            event_types = set(e.event_type for e in region_events)
            details = f"{event_count} events: {', '.join(list(event_types)[:3])}"
            
            hotspot_list.append({
                "region": region,
                "lat": region_data["lat"],
                "lng": region_data["lng"],
                "intensity": intensity,
                "type": "armed_conflict",
                "details": details,
                "event_count": event_count,
            })
        
        # Sort by intensity
        intensity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        hotspot_list.sort(key=lambda x: intensity_order.get(x["intensity"], 0), reverse=True)
        
        output = {
            "status": "online",
            "events": self.total_events,
            "hotspots": hotspot_list,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }
        
        # Write to dashboard JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Output written to {OUTPUT_FILE}")
    
    def log_event(self, event: MilitaryEvent):
        """Log event to JSONL file."""
        with open(EVENTS_FILE, "a") as f:
            event_data = {
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "region": event.region,
                "lat": event.lat,
                "lng": event.lng,
                "event_type": event.event_type,
                "details": event.details,
                "intensity": event.intensity,
            }
            f.write(json.dumps(event_data) + "\n")
    
    def poll(self):
        """Main polling cycle."""
        logger.info("Starting military tracker poll")
        
        # Fetch from all sources
        acled_events = self.fetch_acled_events()
        gdelt_events = self.fetch_gdelt_events()
        flight_events = self.fetch_flight_tracker_events()
        
        # Combine all events
        self.events = acled_events + gdelt_events + flight_events
        self.total_events = len(self.events)
        
        logger.info(f"Total events: {self.total_events} (ACLED: {len(acled_events)}, GDELT: {len(gdelt_events)}, Flight: {len(flight_events)})")
        
        # Log individual events
        for event in self.events:
            self.log_event(event)
        
        # Aggregate into hotspots
        self.aggregate_hotspots()
        
        # Generate output
        self.generate_output()
        
        logger.info(f"Poll complete: {len(self.hotspots)} hotspots identified")
    
    def run(self):
        """Main daemon loop."""
        logger.info("Military tracker daemon starting")
        logger.info(f"Monitoring {len(REGIONS)} regions")
        logger.info(f"Poll interval: {POLL_INTERVAL_SECONDS}s")
        
        while True:
            try:
                self.poll()
                
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
    tracker = MilitaryTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("TEST MODE: Single poll")
        tracker.poll()
        logger.info(f"Test complete. Output: {OUTPUT_FILE}")
    else:
        tracker.run()
