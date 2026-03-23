#!/usr/bin/env python3
"""NASA FIRMS Thermal Anomaly Monitor for Atlas Intel.

Monitors thermal hotspots near critical energy infrastructure using NASA's
Fire Information for Resource Management System (FIRMS).

Features:
- Multi-country monitoring (SAU, IRN, UKR, RUS, ARE, KWT, SGP)
- Proximity detection to known refineries/ports (10km radius)
- Fire intensity analysis (FRP > 100 MW = significant fire)
- Cluster detection (3+ hotspots within 5km)
- New hotspot detection in previously cold areas
- Embedding storage in Atlas Intel vector store

Setup:
1. Register for free FIRMS API key at: https://firms.modaps.eosdis.nasa.gov/api/area/
2. Set environment variable: export FIRMS_API_KEY="your_key_here"
   Or add to /home/ubuntu/clawd/config/supabase-atlas-intel.env

Run every 6 hours via cron (FIRMS updates ~every 3 hours).

Test mode: python3 thermal_monitor.py --test
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import urlopen

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas_intel.config import load_config
from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# NASA FIRMS API endpoint
FIRMS_API_BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

# Get API key from environment or config
import os
FIRMS_API_KEY = os.getenv("FIRMS_API_KEY")
if not FIRMS_API_KEY:
    # Try loading from supabase config file
    from dotenv import dotenv_values
    config_path = Path("/home/ubuntu/clawd/config/supabase-atlas-intel.env")
    if config_path.exists():
        env_vals = dotenv_values(str(config_path))
        FIRMS_API_KEY = env_vals.get("FIRMS_API_KEY", "")

# Data source
DATASET = "VIIRS_SNPP_NRT"  # Near Real-Time VIIRS data

# Days of data to fetch (1 = last 24 hours)
LOOKBACK_DAYS = 1

# Regional bounding boxes (west, south, east, north)
# Format: {name: (min_lon, min_lat, max_lon, max_lat)}
MONITORED_REGIONS = {
    "persian_gulf": (46.0, 23.0, 56.0, 31.0),  # SAU, ARE, IRN, KWT
    "russia_west": (38.0, 45.0, 55.0, 53.0),  # RUS western refineries
    "ukraine": (22.0, 44.0, 40.0, 52.0),  # UKR
    "singapore": (103.0, 1.0, 104.5, 1.5),  # SGP
}

# Detection thresholds
PROXIMITY_THRESHOLD_KM = 10.0  # Alert if within 10km of facility
SIGNIFICANT_FRP_MW = 100.0  # Fire Radiative Power > 100 MW = major fire
CLUSTER_MIN_HOTSPOTS = 3  # 3+ hotspots = cluster
CLUSTER_RADIUS_KM = 5.0  # Cluster detection radius

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "thermal_monitor.log"
EVENTS_FILE = LOG_DIR / "thermal_events.jsonl"
HISTORICAL_FILE = LOG_DIR / "thermal_history.json"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Known Facilities (lat, lon, name)
# ---------------------------------------------------------------------------

class Facility(NamedTuple):
    name: str
    lat: float
    lon: float
    country: str


KNOWN_FACILITIES = [
    Facility("Abqaiq", 25.93, 49.68, "SAU"),
    Facility("Ras_Tanura", 26.63, 50.16, "SAU"),
    Facility("Ghawar", 25.38, 49.47, "SAU"),
    Facility("Jubail", 26.28, 50.21, "SAU"),
    Facility("Ruwais_UAE", 24.09, 52.07, "ARE"),
    Facility("Ras_Laffan_Qatar", 25.29, 51.53, "QAT"),  # Swapped coords
    Facility("Jurong_Island_SG", 1.27, 103.73, "SGP"),
    Facility("Volgograd_RUS", 48.38, 44.52, "RUS"),
    Facility("Saratov_RUS", 50.30, 40.13, "RUS"),
    Facility("Atyrau_KAZ", 47.10, 51.88, "KAZ"),
    Facility("Abadan_IRN", 30.45, 49.19, "IRN"),
    Facility("Rasht_IRN", 37.28, 49.58, "IRN"),
]


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Hotspot(NamedTuple):
    """FIRMS thermal hotspot data point."""
    latitude: float
    longitude: float
    brightness: float  # Brightness temperature (Kelvin)
    scan: float  # Pixel size (km)
    track: float  # Pixel size (km)
    acq_date: str  # Acquisition date (YYYY-MM-DD)
    acq_time: str  # Acquisition time (HHMM)
    satellite: str  # Satellite identifier
    confidence: str  # Confidence level (low/nominal/high)
    version: str  # Version number
    bright_t31: float  # Brightness temperature I-4
    frp: float  # Fire Radiative Power (MW)
    daynight: str  # D=day, N=night


class ThermalAnomaly(NamedTuple):
    """Detected thermal anomaly event."""
    hotspot: Hotspot
    anomaly_type: str  # proximity, high_frp, cluster, new_area
    facility: Facility | None
    distance_km: float | None
    cluster_size: int | None
    severity: str  # low, medium, high, critical


# ---------------------------------------------------------------------------
# Geometry Utils
# ---------------------------------------------------------------------------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in kilometers using Haversine formula."""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0  # Earth radius in km

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)

    a = sin(dLat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dLon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# ---------------------------------------------------------------------------
# Test Mode / Mock Data
# ---------------------------------------------------------------------------

def _generate_mock_hotspots(region_name: str, bbox: tuple[float, float, float, float]) -> list[Hotspot]:
    """Generate mock hotspot data for testing."""
    import random
    from datetime import datetime, timedelta
    
    mock_hotspots = []
    
    # Generate a few hotspots near known facilities
    if region_name == "persian_gulf":
        # Create hotspot near Abqaiq (high FRP - should trigger proximity + high FRP alerts)
        mock_hotspots.append(Hotspot(
            latitude=25.94,  # Very close to Abqaiq (25.93, 49.68)
            longitude=49.69,
            brightness=350.0,
            scan=0.5,
            track=0.5,
            acq_date=(datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d"),
            acq_time=(datetime.now() - timedelta(hours=2)).strftime("%H%M"),
            satellite="N",
            confidence="high",
            version="2.0NRT",
            bright_t31=320.0,
            frp=250.0,  # High FRP
            daynight="D",
        ))
        
        # Create cluster of hotspots (should trigger cluster alert)
        base_lat, base_lon = 26.60, 50.15  # Near Ras Tanura
        for i in range(4):
            mock_hotspots.append(Hotspot(
                latitude=base_lat + random.uniform(-0.02, 0.02),
                longitude=base_lon + random.uniform(-0.02, 0.02),
                brightness=320.0 + random.uniform(-10, 10),
                scan=0.5,
                track=0.5,
                acq_date=(datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d"),
                acq_time=(datetime.now() - timedelta(hours=1)).strftime("%H%M"),
                satellite="N",
                confidence="nominal",
                version="2.0NRT",
                bright_t31=310.0,
                frp=80.0 + random.uniform(-20, 20),
                daynight="D",
            ))
    
    if region_name == "singapore":
        # New area hotspot (not near any known facility)
        mock_hotspots.append(Hotspot(
            latitude=1.35,
            longitude=103.85,
            brightness=340.0,
            scan=0.5,
            track=0.5,
            acq_date=datetime.now().strftime("%Y-%m-%d"),
            acq_time=datetime.now().strftime("%H%M"),
            satellite="N",
            confidence="high",
            version="2.0NRT",
            bright_t31=325.0,
            frp=150.0,
            daynight="N",
        ))
    
    logger.info(f"Generated {len(mock_hotspots)} mock hotspots for {region_name}")
    return mock_hotspots


# ---------------------------------------------------------------------------
# FIRMS API Client
# ---------------------------------------------------------------------------

def fetch_firms_data(region_name: str, bbox: tuple[float, float, float, float], days: int = 1, test_mode: bool = False) -> list[Hotspot]:
    """Fetch FIRMS data for a specific bounding box.
    
    Args:
        region_name: Human-readable region name
        bbox: (west, south, east, north) bounding box coordinates
        days: Number of days to look back (1-10)
        test_mode: If True, return mock data instead of hitting API
    
    Returns:
        List of Hotspot objects
    """
    if test_mode:
        return _generate_mock_hotspots(region_name, bbox)
    
    if not FIRMS_API_KEY:
        logger.error("FIRMS_API_KEY not set. Register at https://firms.modaps.eosdis.nasa.gov/api/area/")
        logger.error("Set via: export FIRMS_API_KEY=your_key or add to supabase-atlas-intel.env")
        return []
    
    # Format: /MAP_KEY/DATASET/west,south,east,north/days
    bbox_str = ",".join(str(coord) for coord in bbox)
    url = f"{FIRMS_API_BASE}/{FIRMS_API_KEY}/{DATASET}/{bbox_str}/{days}"
    
    try:
        logger.info(f"Fetching FIRMS data: {region_name} (bbox: {bbox_str}, last {days} days)")
        with urlopen(url, timeout=30) as response:
            data = response.read().decode("utf-8")
        
        # Parse CSV
        reader = csv.DictReader(StringIO(data))
        hotspots = []
        
        for row in reader:
            try:
                hotspot = Hotspot(
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    brightness=float(row["brightness"]),
                    scan=float(row["scan"]),
                    track=float(row["track"]),
                    acq_date=row["acq_date"],
                    acq_time=row["acq_time"],
                    satellite=row["satellite"],
                    confidence=row["confidence"],
                    version=row["version"],
                    bright_t31=float(row["bright_t31"]),
                    frp=float(row["frp"]),
                    daynight=row["daynight"],
                )
                hotspots.append(hotspot)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping malformed row: {e}")
                continue
        
        logger.info(f"Retrieved {len(hotspots)} hotspots for {region_name}")
        return hotspots
    
    except HTTPError as e:
        if e.code == 404:
            logger.info(f"No data available for {region_name}")
            return []
        else:
            logger.error(f"HTTP error fetching {region_name}: {e}")
            raise
    except Exception as e:
        logger.error(f"Error fetching FIRMS data for {region_name}: {e}")
        raise


# ---------------------------------------------------------------------------
# Anomaly Detection
# ---------------------------------------------------------------------------

def detect_proximity_anomalies(hotspots: list[Hotspot]) -> list[ThermalAnomaly]:
    """Detect hotspots within 10km of known facilities."""
    anomalies = []
    
    for hotspot in hotspots:
        for facility in KNOWN_FACILITIES:
            distance = haversine_distance(
                hotspot.latitude, hotspot.longitude,
                facility.lat, facility.lon
            )
            
            if distance <= PROXIMITY_THRESHOLD_KM:
                # Determine severity based on distance and FRP
                if distance < 1.0 and hotspot.frp > 500:
                    severity = "critical"
                elif distance < 3.0 and hotspot.frp > 200:
                    severity = "high"
                elif hotspot.frp > SIGNIFICANT_FRP_MW:
                    severity = "high"
                else:
                    severity = "medium"
                
                anomaly = ThermalAnomaly(
                    hotspot=hotspot,
                    anomaly_type="proximity",
                    facility=facility,
                    distance_km=round(distance, 2),
                    cluster_size=None,
                    severity=severity,
                )
                anomalies.append(anomaly)
                break  # Only count nearest facility
    
    return anomalies


def detect_high_frp_events(hotspots: list[Hotspot]) -> list[ThermalAnomaly]:
    """Detect significant fire events (FRP > 100 MW)."""
    anomalies = []
    
    for hotspot in hotspots:
        if hotspot.frp > SIGNIFICANT_FRP_MW:
            # Determine severity
            if hotspot.frp > 500:
                severity = "critical"
            elif hotspot.frp > 300:
                severity = "high"
            else:
                severity = "medium"
            
            anomaly = ThermalAnomaly(
                hotspot=hotspot,
                anomaly_type="high_frp",
                facility=None,
                distance_km=None,
                cluster_size=None,
                severity=severity,
            )
            anomalies.append(anomaly)
    
    return anomalies


def detect_clusters(hotspots: list[Hotspot]) -> list[ThermalAnomaly]:
    """Detect clusters: 3+ hotspots within 5km."""
    if len(hotspots) < CLUSTER_MIN_HOTSPOTS:
        return []
    
    anomalies = []
    processed = set()
    
    for i, hotspot in enumerate(hotspots):
        if i in processed:
            continue
        
        # Find nearby hotspots
        cluster = [hotspot]
        for j, other in enumerate(hotspots):
            if i == j or j in processed:
                continue
            
            distance = haversine_distance(
                hotspot.latitude, hotspot.longitude,
                other.latitude, other.longitude
            )
            
            if distance <= CLUSTER_RADIUS_KM:
                cluster.append(other)
        
        # Check if cluster meets threshold
        if len(cluster) >= CLUSTER_MIN_HOTSPOTS:
            # Calculate average FRP for severity
            avg_frp = sum(h.frp for h in cluster) / len(cluster)
            
            if len(cluster) >= 10 or avg_frp > 300:
                severity = "critical"
            elif len(cluster) >= 5 or avg_frp > 150:
                severity = "high"
            else:
                severity = "medium"
            
            anomaly = ThermalAnomaly(
                hotspot=hotspot,  # Use first hotspot as reference
                anomaly_type="cluster",
                facility=None,
                distance_km=None,
                cluster_size=len(cluster),
                severity=severity,
            )
            anomalies.append(anomaly)
            
            # Mark cluster members as processed
            for idx, h in enumerate(hotspots):
                if h in cluster:
                    processed.add(idx)
    
    return anomalies


def detect_new_areas(hotspots: list[Hotspot]) -> list[ThermalAnomaly]:
    """Detect new hotspots in previously cold areas.
    
    Compares current hotspots against historical data.
    """
    anomalies = []
    
    # Load historical hotspot locations
    historical_locations = load_historical_locations()
    
    for hotspot in hotspots:
        location_key = f"{round(hotspot.latitude, 2)},{round(hotspot.longitude, 2)}"
        
        if location_key not in historical_locations:
            # This is a new area
            if hotspot.frp > 50:  # Only flag significant new events
                severity = "high" if hotspot.frp > 200 else "medium"
                
                anomaly = ThermalAnomaly(
                    hotspot=hotspot,
                    anomaly_type="new_area",
                    facility=None,
                    distance_km=None,
                    cluster_size=None,
                    severity=severity,
                )
                anomalies.append(anomaly)
    
    return anomalies


# ---------------------------------------------------------------------------
# Historical Data Management
# ---------------------------------------------------------------------------

def load_historical_locations() -> set[str]:
    """Load historical hotspot locations from file."""
    if not HISTORICAL_FILE.exists():
        return set()
    
    try:
        with open(HISTORICAL_FILE) as f:
            data = json.load(f)
            return set(data.get("locations", []))
    except Exception as e:
        logger.warning(f"Error loading historical data: {e}")
        return set()


def update_historical_locations(hotspots: list[Hotspot]) -> None:
    """Update historical hotspot locations."""
    existing = load_historical_locations()
    
    for hotspot in hotspots:
        location_key = f"{round(hotspot.latitude, 2)},{round(hotspot.longitude, 2)}"
        existing.add(location_key)
    
    # Save back to file
    try:
        with open(HISTORICAL_FILE, "w") as f:
            json.dump({
                "locations": list(existing),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving historical data: {e}")


# ---------------------------------------------------------------------------
# Event Processing
# ---------------------------------------------------------------------------

def process_anomaly(anomaly: ThermalAnomaly) -> None:
    """Process detected anomaly: embed, store, and log."""
    
    # Generate event description
    desc_parts = [
        f"Thermal anomaly detected: {anomaly.anomaly_type}",
        f"Location: {anomaly.hotspot.latitude:.4f}, {anomaly.hotspot.longitude:.4f}",
        f"FRP: {anomaly.hotspot.frp:.1f} MW",
        f"Brightness: {anomaly.hotspot.brightness:.1f}K",
        f"Time: {anomaly.hotspot.acq_date} {anomaly.hotspot.acq_time}",
        f"Satellite: {anomaly.hotspot.satellite}",
        f"Confidence: {anomaly.hotspot.confidence}",
    ]
    
    if anomaly.facility:
        desc_parts.append(f"Near facility: {anomaly.facility.name} ({anomaly.distance_km}km away)")
    
    if anomaly.cluster_size:
        desc_parts.append(f"Cluster size: {anomaly.cluster_size} hotspots")
    
    desc_parts.append(f"Severity: {anomaly.severity}")
    
    event_text = " | ".join(desc_parts)
    
    # Create metadata
    metadata = {
        "lat": anomaly.hotspot.latitude,
        "lon": anomaly.hotspot.longitude,
        "frp": anomaly.hotspot.frp,
        "brightness": anomaly.hotspot.brightness,
        "acq_date": anomaly.hotspot.acq_date,
        "acq_time": anomaly.hotspot.acq_time,
        "satellite": anomaly.hotspot.satellite,
        "confidence": anomaly.hotspot.confidence,
        "anomaly_type": anomaly.anomaly_type,
        "severity": anomaly.severity,
    }
    
    if anomaly.facility:
        metadata["facility_name"] = anomaly.facility.name
        metadata["facility_country"] = anomaly.facility.country
        metadata["distance_km"] = anomaly.distance_km
    
    if anomaly.cluster_size:
        metadata["cluster_size"] = anomaly.cluster_size
    
    # Generate embedding
    try:
        embedding = embed_text(event_text)
        
        # Store in vector database
        store_embedding(
            source_type="thermal_anomaly",
            content=event_text,
            metadata=metadata,
            embedding=embedding,
        )
        
        logger.info(f"Stored anomaly: {anomaly.anomaly_type} - {anomaly.severity}")
    except Exception as e:
        logger.error(f"Error embedding/storing anomaly: {e}")
    
    # Log to JSONL
    try:
        event_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_text": event_text,
            "metadata": metadata,
        }
        
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(event_record) + "\n")
    except Exception as e:
        logger.error(f"Error logging to JSONL: {e}")


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main(test_mode: bool = False) -> None:
    """Main monitoring loop.
    
    Args:
        test_mode: If True, use mock data instead of real API calls
    """
    logger.info("=" * 80)
    logger.info(f"NASA FIRMS Thermal Anomaly Monitor - Starting {'(TEST MODE)' if test_mode else ''}")
    logger.info("=" * 80)
    
    if test_mode:
        logger.info("Running in test mode with mock data")
    elif not FIRMS_API_KEY:
        logger.error("No FIRMS_API_KEY configured. Use --test for test mode or set API key.")
        logger.error("Register at: https://firms.modaps.eosdis.nasa.gov/api/area/")
        return
    
    all_hotspots = []
    all_anomalies = []
    
    # Fetch data for each monitored region
    for region_name, bbox in MONITORED_REGIONS.items():
        try:
            hotspots = fetch_firms_data(region_name, bbox, LOOKBACK_DAYS, test_mode=test_mode)
            all_hotspots.extend(hotspots)
        except Exception as e:
            logger.error(f"Failed to fetch data for {region_name}: {e}")
            continue
    
    if not all_hotspots:
        logger.info("No hotspots detected in monitored regions")
        return
    
    logger.info(f"Total hotspots retrieved: {len(all_hotspots)}")
    
    # Run detection algorithms
    logger.info("Running anomaly detection...")
    
    proximity_anomalies = detect_proximity_anomalies(all_hotspots)
    logger.info(f"Proximity anomalies: {len(proximity_anomalies)}")
    
    high_frp_anomalies = detect_high_frp_events(all_hotspots)
    logger.info(f"High FRP events: {len(high_frp_anomalies)}")
    
    cluster_anomalies = detect_clusters(all_hotspots)
    logger.info(f"Cluster events: {len(cluster_anomalies)}")
    
    new_area_anomalies = detect_new_areas(all_hotspots)
    logger.info(f"New area events: {len(new_area_anomalies)}")
    
    # Combine and deduplicate
    all_anomalies = list({
        (a.hotspot.latitude, a.hotspot.longitude, a.hotspot.acq_time): a
        for a in proximity_anomalies + high_frp_anomalies + cluster_anomalies + new_area_anomalies
    }.values())
    
    logger.info(f"Total unique anomalies: {len(all_anomalies)}")
    
    # Process each anomaly
    for anomaly in all_anomalies:
        process_anomaly(anomaly)
    
    # Update historical data
    update_historical_locations(all_hotspots)
    
    logger.info("=" * 80)
    logger.info(f"Monitoring complete. Detected {len(all_anomalies)} anomalies.")
    logger.info("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NASA FIRMS Thermal Anomaly Monitor")
    parser.add_argument("--test", action="store_true", help="Run in test mode with mock data")
    args = parser.parse_args()
    
    try:
        main(test_mode=args.test)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
