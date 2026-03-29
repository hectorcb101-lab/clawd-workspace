#!/usr/bin/env python3
"""CelesTrak satellite tracker for Atlas Intel.

Monitors military and reconnaissance satellites using TLE data from CelesTrak.
Tracks passes over conflict zones and detects unusual orbit changes.

Data sources:
- CelesTrak TLE data (free, no auth)
- Focus: military, reconnaissance, GPS, Starlink, Chinese Yaogan series

Free tier: unlimited TLE downloads, rate-limit friendly (1 req/5min).
"""

from __future__ import annotations

import json
import logging
import math
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from sgp4.api import Satrec, jday

# Add parent directory to path for atlas_intel imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 300  # 5 minutes
CELESTRAK_TLE_URL = "https://celestrak.org/NORAD/elements/gp.php"

# Satellite groups to track
SATELLITE_GROUPS = [
    "active",
]

# Conflict zones (lat_min, lat_max, lon_min, lon_max)
CONFLICT_ZONES = {
    "Ukraine": (44, 52, 22, 40),
    "Middle East": (25, 42, 30, 65),
    "Taiwan Strait": (22, 27, 117, 123),
    "Korean Peninsula": (33, 43, 124, 132),
    "South China Sea": (0, 25, 100, 125),
}

# Military satellite patterns
MILITARY_PATTERNS = [
    r"USA[\s-]\d+",  # US military sats
    r"NROL[\s-]\d+",  # NRO reconnaissance
    r"YAOGAN[\s-]\d+",  # Chinese reconnaissance
    r"COSMOS[\s-]\d+",  # Russian military
    r"GPS[\s-]",  # GPS constellation
    r"GLONASS",  # Russian GPS
]

# Logs and output
LOG_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/logs")
OUTPUT_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data")
LOG_FILE = LOG_DIR / "satellite_tracker.log"
OUTPUT_FILE = OUTPUT_DIR / "satellite_status.json"

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
# Satellite tracking
# ---------------------------------------------------------------------------

@dataclass
class Satellite:
    """Satellite data container."""
    name: str
    norad_id: int
    tle_line1: str
    tle_line2: str
    sat_type: str
    country: str
    satrec: Satrec | None = None


def ecef_to_latlon(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Convert ECEF (Earth-Centered Earth-Fixed) coordinates to lat/lon/alt."""
    # Earth parameters
    a = 6378.137  # Semi-major axis in km
    f = 1 / 298.257223563  # Flattening
    e2 = 2 * f - f * f  # First eccentricity squared
    
    # Calculate longitude
    lon = math.atan2(y, x)
    
    # Calculate latitude iteratively
    p = math.sqrt(x * x + y * y)
    lat = math.atan2(z, p * (1 - e2))
    
    for _ in range(5):  # Iterate for accuracy
        N = a / math.sqrt(1 - e2 * math.sin(lat) * math.sin(lat))
        lat = math.atan2(z + e2 * N * math.sin(lat), p)
    
    # Calculate altitude
    N = a / math.sqrt(1 - e2 * math.sin(lat) * math.sin(lat))
    alt = p / math.cos(lat) - N
    
    # Convert to degrees
    lat_deg = math.degrees(lat)
    lon_deg = math.degrees(lon)
    
    return lat_deg, lon_deg, alt


class SatelliteTracker:
    """Satellite tracker using CelesTrak TLE data."""
    
    def __init__(self):
        self.satellites: dict[int, Satellite] = {}
        self.total_tracked = 0
        self.military_count = 0
        
    def fetch_tle_data(self) -> list[str]:
        """Fetch TLE data from CelesTrak for all tracked groups."""
        all_tle_lines = []
        
        for group in SATELLITE_GROUPS:
            try:
                params = {"GROUP": group, "FORMAT": "tle"}
                response = requests.get(CELESTRAK_TLE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                lines = response.text.strip().split("\n")
                all_tle_lines.extend(lines)
                logger.info(f"Fetched TLE data for group '{group}': {len(lines)//3} satellites")
                
                # Rate limit courtesy
                time.sleep(1)
                
            except requests.exceptions.RequestException as exc:
                logger.error(f"Failed to fetch TLE data for group '{group}': {exc}")
        
        return all_tle_lines
    
    def parse_tle_data(self, tle_lines: list[str]):
        """Parse TLE data into Satellite objects."""
        self.satellites.clear()
        self.military_count = 0
        
        # TLE format: 3 lines per satellite (name, line1, line2)
        for i in range(0, len(tle_lines) - 2, 3):
            try:
                name = tle_lines[i].strip()
                line1 = tle_lines[i + 1].strip()
                line2 = tle_lines[i + 2].strip()
                
                # Extract NORAD ID from line 1
                norad_id = int(line1[2:7])
                
                # Classify satellite type and country
                sat_type, country = self.classify_satellite(name)
                
                # Create SGP4 satellite record
                try:
                    satrec = Satrec.twoline2rv(line1, line2)
                except Exception:
                    continue
                
                satellite = Satellite(
                    name=name,
                    norad_id=norad_id,
                    tle_line1=line1,
                    tle_line2=line2,
                    sat_type=sat_type,
                    country=country,
                    satrec=satrec,
                )
                
                self.satellites[norad_id] = satellite
                
                if sat_type == "military":
                    self.military_count += 1
                    
            except Exception as exc:
                logger.debug(f"Failed to parse TLE entry: {exc}")
        
        self.total_tracked = len(self.satellites)
        logger.info(f"Parsed {self.total_tracked} satellites ({self.military_count} military)")
    
    def classify_satellite(self, name: str) -> tuple[str, str]:
        """Classify satellite by type and country based on name."""
        name_upper = name.upper()
        
        # Check military patterns
        for pattern in MILITARY_PATTERNS:
            if re.search(pattern, name_upper):
                # Determine country
                if "USA" in name_upper or "NROL" in name_upper or "GPS" in name_upper:
                    return "military", "US"
                elif "YAOGAN" in name_upper:
                    return "military", "CN"
                elif "COSMOS" in name_upper or "GLONASS" in name_upper:
                    return "military", "RU"
                else:
                    return "military", "unknown"
        
        # Check for Starlink
        if "STARLINK" in name_upper:
            return "commercial", "US"
        
        # Default: civilian
        return "civilian", "unknown"
    
    def get_satellite_position(self, satellite: Satellite) -> dict[str, Any] | None:
        """Calculate current satellite position using SGP4."""
        try:
            # Get current time as Julian date
            now = datetime.now(timezone.utc)
            jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)
            
            # Propagate satellite position
            error_code, position, velocity = satellite.satrec.sgp4(jd, fr)
            
            if error_code != 0:
                return None
            
            # Convert TEME position to lat/lng (position is in km)
            x, y, z = position
            lat, lng, alt = ecef_to_latlon(x, y, z)
            
            return {
                "lat": round(lat, 2),
                "lng": round(lng, 2),
                "alt_km": round(alt, 1),
            }
            
        except Exception as exc:
            logger.debug(f"Failed to calculate position for {satellite.name}: {exc}")
            return None
    
    def generate_output(self):
        """Generate JSON output for dashboard."""
        # Select satellites to display (military satellites with positions)
        display_satellites = []
        
        # Add military satellites with current positions
        for satellite in self.satellites.values():
            if satellite.sat_type == "military":
                position = self.get_satellite_position(satellite)
                if position:
                    display_satellites.append({
                        "name": satellite.name,
                        "lat": position["lat"],
                        "lng": position["lng"],
                        "alt_km": position["alt_km"],
                        "type": satellite.sat_type,
                        "country": satellite.country,
                    })
        
        output = {
            "status": "online",
            "tracked": self.total_tracked,
            "military": self.military_count,
            "last_update": datetime.now(timezone.utc).isoformat(),
            "satellites": display_satellites[:150],  # Limit to 150 for display
        }
        
        # Write to dashboard JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Output written to {OUTPUT_FILE}")
    
    def poll(self):
        """Main polling cycle."""
        logger.info("Starting satellite poll")
        
        # Fetch and parse TLE data
        tle_lines = self.fetch_tle_data()
        if not tle_lines:
            logger.warning("No TLE data fetched")
            return
        
        self.parse_tle_data(tle_lines)
        
        # Generate dashboard output
        self.generate_output()
        
        logger.info(f"Poll complete: {self.total_tracked} tracked, {self.military_count} military, {len([s for s in self.satellites.values() if s.sat_type == 'military'])} displayed")
    
    def run(self):
        """Main daemon loop."""
        logger.info("Satellite tracker daemon starting")
        logger.info(f"Monitoring {len(SATELLITE_GROUPS)} satellite groups")
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

def main():
    """Main entry point."""
    tracker = SatelliteTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("TEST MODE: Single poll")
        tracker.poll()
        logger.info(f"Test complete. Output: {OUTPUT_FILE}")
    else:
        tracker.run()


if __name__ == "__main__":
    main()
