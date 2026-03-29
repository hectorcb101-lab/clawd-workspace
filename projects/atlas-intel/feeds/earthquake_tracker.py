#!/usr/bin/env python3
"""
Earthquake Tracker Feed - Atlas Intel
Fetches earthquake data from USGS GeoJSON feeds
Outputs to earthquake_live.json with frontend-compatible schema
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuration
USGS_ALL_DAY = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
USGS_SIGNIFICANT_MONTH = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
OUTPUT_PATH = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/earthquake_live.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [EARTHQUAKE] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_json(url: str, timeout: int = 30) -> Any:
    """Fetch JSON from URL with error handling"""
    try:
        req = Request(url, headers={'User-Agent': 'Atlas-Intel/1.0'})
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
        return None
    except URLError as e:
        logger.error(f"URL error fetching {url}: {e.reason}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def categorize_magnitude(mag: float) -> str:
    """Categorize earthquake by magnitude"""
    if mag >= 7.0:
        return "great"
    elif mag >= 6.0:
        return "major"
    elif mag >= 5.0:
        return "strong"
    elif mag >= 4.0:
        return "moderate"
    elif mag >= 3.0:
        return "light"
    else:
        return "minor"


def parse_usgs_geojson(data: Dict) -> List[Dict[str, Any]]:
    """Parse USGS GeoJSON format into frontend-compatible schema"""
    if not data or 'features' not in data:
        return []
    
    earthquakes = []
    for feature in data['features']:
        try:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [0, 0, 0])
            
            # Extract required fields
            lon = float(coords[0]) if len(coords) > 0 else 0.0
            lat = float(coords[1]) if len(coords) > 1 else 0.0
            depth = float(coords[2]) if len(coords) > 2 else 0.0
            magnitude = float(props.get('mag', 0))
            
            # Convert USGS timestamp (milliseconds) to ISO string
            timestamp_ms = props.get('time', 0)
            time_iso = datetime.fromtimestamp(
                timestamp_ms / 1000, 
                tz=timezone.utc
            ).isoformat()
            
            # Build earthquake object matching frontend schema
            eq = {
                "lat": lat,
                "lon": lon,
                "lng": lon,  # Duplicate field for frontend compatibility
                "magnitude": magnitude,
                "depth": depth,
                "place": props.get('place', 'Unknown location'),
                "time": time_iso,
                "url": props.get('url', ''),
                "tsunami": bool(props.get('tsunami', 0)),
                "felt": int(props.get('felt', 0)) if props.get('felt') else 0,
                "significance": int(props.get('sig', 0)),
                "category": categorize_magnitude(magnitude),
                "id": feature.get('id', 'unknown')
            }
            
            earthquakes.append(eq)
            
        except (ValueError, KeyError, TypeError, IndexError) as e:
            logger.debug(f"Skipping malformed earthquake record: {e}")
            continue
    
    return earthquakes


def fetch_earthquakes() -> Dict[str, Any]:
    """Fetch and aggregate earthquake data from USGS feeds"""
    logger.info("Fetching earthquake data from USGS...")
    
    # Fetch all earthquakes from past 24 hours
    all_day_data = fetch_json(USGS_ALL_DAY)
    all_day_quakes = parse_usgs_geojson(all_day_data) if all_day_data else []
    logger.info(f"Fetched {len(all_day_quakes)} earthquakes (all magnitudes, past 24h)")
    
    # Fetch significant earthquakes from past month
    significant_data = fetch_json(USGS_SIGNIFICANT_MONTH)
    significant_quakes = parse_usgs_geojson(significant_data) if significant_data else []
    logger.info(f"Fetched {len(significant_quakes)} significant earthquakes (past 30 days)")
    
    # Combine and deduplicate by ID
    all_quakes_dict = {eq['id']: eq for eq in all_day_quakes}
    for eq in significant_quakes:
        if eq['id'] not in all_quakes_dict:
            all_quakes_dict[eq['id']] = eq
    
    # Convert to list and sort by magnitude (descending)
    earthquakes_list = sorted(
        all_quakes_dict.values(),
        key=lambda x: x['magnitude'],
        reverse=True
    )
    
    # Calculate statistics
    max_magnitude = max((eq['magnitude'] for eq in earthquakes_list), default=0.0)
    
    # Count significant events (magnitude >= 4.5 or significance >= 600)
    significant_count = sum(
        1 for eq in earthquakes_list
        if eq['magnitude'] >= 4.5 or eq['significance'] >= 600
    )
    
    # Build output matching frontend schema
    output = {
        "earthquakes": earthquakes_list,
        "count": len(earthquakes_list),
        "max_magnitude": max_magnitude,
        "significant_count": significant_count,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    return output


def fetch_and_save():
    """Main fetch and save routine"""
    try:
        output = fetch_earthquakes()
        
        # Write to file
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"✓ Saved {output['count']} earthquakes to {OUTPUT_PATH}")
        logger.info(f"  Max magnitude: {output['max_magnitude']:.1f}")
        logger.info(f"  Significant events: {output['significant_count']}")
        
        # Log size check
        output_size = len(json.dumps(output))
        logger.info(f"  Output size: {output_size / 1024:.1f} KB")
        
    except Exception as e:
        logger.error(f"Failed to fetch and save: {e}", exc_info=True)
        raise


def run_continuous(interval: int = 600):
    """Run continuously with specified interval (default 10 minutes)"""
    logger.info(f"Starting continuous mode with {interval}s interval")
    
    while True:
        try:
            fetch_and_save()
        except Exception as e:
            logger.error(f"Error in fetch cycle: {e}", exc_info=True)
        
        logger.info(f"Sleeping for {interval} seconds...")
        time.sleep(interval)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 600
        run_continuous(interval)
    else:
        fetch_and_save()
