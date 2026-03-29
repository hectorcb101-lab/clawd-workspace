#!/usr/bin/env python3
"""
NASA FIRMS Wildfire Tracker
Fetches active fire data from NASA FIRMS and generates JSON feed for Atlas Intel dashboard.
"""

import requests
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data sources (in order of preference)
DATA_SOURCES = [
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/VIIRS_SNPP_NRT/world/1",
    "https://firms.modaps.eosdis.nasa.gov/api/country/csv/VIIRS_SNPP_NRT/world/1"
]

# Configuration
OUTPUT_PATH = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/wildfire_live.json")
MAX_FIRES = 2000
CLUSTER_THRESHOLD = 0.5  # degrees


def fetch_firms_data() -> str:
    """Fetch CSV data from NASA FIRMS, trying sources in order."""
    for url in DATA_SOURCES:
        try:
            logger.info(f"Attempting to fetch data from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got actual CSV data (not an error page)
            if response.text and ('latitude' in response.text.lower() or 'lat' in response.text.lower()):
                logger.info(f"Successfully fetched data from: {url}")
                return response.text
            else:
                logger.warning(f"Response doesn't look like CSV data from: {url}")
                
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch from {url}: {e}")
            continue
    
    raise Exception("Failed to fetch data from all FIRMS sources")


def parse_csv_to_fires(csv_data: str) -> List[Dict[str, Any]]:
    """Parse CSV data into fire objects."""
    fires = []
    reader = csv.DictReader(csv_data.strip().split('\n'))
    
    for row in reader:
        try:
            # Handle different CSV column naming conventions
            lat = float(row.get('latitude') or row.get('lat') or row.get('Lat'))
            lon = float(row.get('longitude') or row.get('lon') or row.get('Lon'))
            
            # Parse brightness/FRP
            brightness = float(row.get('brightness') or row.get('bright_ti4') or row.get('Brightness') or 0)
            frp = float(row.get('frp') or row.get('FRP') or row.get('Fire Radiative Power') or brightness)
            
            # Parse confidence
            confidence = str(row.get('confidence') or row.get('Confidence') or 'unknown')
            
            # Parse satellite
            satellite = str(row.get('satellite') or row.get('Satellite') or row.get('instrument') or 'VIIRS')
            
            # Parse acquisition time
            acq_date = row.get('acq_date') or row.get('Date') or ''
            acq_time = row.get('acq_time') or row.get('Time') or ''
            detected = f"{acq_date} {acq_time}".strip() if acq_date else datetime.utcnow().isoformat()
            
            # Parse scan and track
            scan = float(row.get('scan') or row.get('Scan') or 0)
            track = float(row.get('track') or row.get('Track') or 0)
            
            fire = {
                "lat": lat,
                "lon": lon,
                "lng": lon,  # Include both lon and lng as requested
                "frp": frp,
                "confidence": confidence,
                "satellite": satellite,
                "name": f"Fire at ({lat:.2f}, {lon:.2f})",
                "detected": detected,
                "brightness": brightness,
                "scan": scan,
                "track": track
            }
            
            fires.append(fire)
            
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"Skipping row due to parse error: {e}")
            continue
    
    logger.info(f"Parsed {len(fires)} fires from CSV data")
    return fires


def cluster_fires(fires: List[Dict[str, Any]], threshold: float = CLUSTER_THRESHOLD) -> int:
    """
    Count fire clusters using simple proximity-based clustering.
    Fires within `threshold` degrees are considered part of the same cluster.
    """
    if not fires:
        return 0
    
    # Simple grid-based clustering
    grid = defaultdict(list)
    
    for fire in fires:
        # Round coordinates to cluster threshold
        grid_lat = round(fire['lat'] / threshold)
        grid_lon = round(fire['lon'] / threshold)
        grid[(grid_lat, grid_lon)].append(fire)
    
    num_clusters = len(grid)
    logger.info(f"Identified {num_clusters} fire clusters")
    return num_clusters


def generate_feed(fires: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate the final JSON feed with statistics."""
    
    # Sort by FRP descending
    fires_sorted = sorted(fires, key=lambda f: f['frp'], reverse=True)
    
    # Limit to top N fires
    fires_limited = fires_sorted[:MAX_FIRES]
    
    # Calculate statistics
    max_frp = max((f['frp'] for f in fires_limited), default=0.0)
    clusters = cluster_fires(fires_limited)
    
    feed = {
        "fires": fires_limited,
        "count": len(fires_limited),
        "clusters": clusters,
        "max_frp": max_frp,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return feed


def main():
    """Main execution flow."""
    try:
        logger.info("Starting NASA FIRMS wildfire tracker")
        
        # Fetch data
        csv_data = fetch_firms_data()
        
        # Parse fires
        fires = parse_csv_to_fires(csv_data)
        
        if not fires:
            logger.error("No fires parsed from CSV data")
            return
        
        # Generate feed
        feed = generate_feed(fires)
        
        # Ensure output directory exists
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON output
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(feed, f, indent=2)
        
        logger.info(f"Successfully generated wildfire feed: {OUTPUT_PATH}")
        logger.info(f"Total fires: {feed['count']}, Clusters: {feed['clusters']}, Max FRP: {feed['max_frp']:.2f} MW")
        
    except Exception as e:
        logger.error(f"Failed to generate wildfire feed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
