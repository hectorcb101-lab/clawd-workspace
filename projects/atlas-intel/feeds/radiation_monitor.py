#!/usr/bin/env python3
"""
Radiation Monitor Feed - Atlas Intel
Fetches radiation data from EPA RadNet and Safecast APIs
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuration
EPA_RADNET_URL = "https://ofmpub.epa.gov/enviro/efservice/getRadNetData/rows/0:100/JSON"
SAFECAST_URL = "https://api.safecast.org/measurements.json?distance=100000&latitude=37&longitude=-122&order=created_at+desc&limit=100"
OUTPUT_PATH = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/radiation_live.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [RADIATION] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_json(url: str, timeout: int = 15) -> Any:
    """Fetch JSON from URL with error handling"""
    try:
        req = Request(url, headers={'User-Agent': 'Atlas-Intel/1.0'})
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError) as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def fetch_epa_radnet() -> List[Dict[str, Any]]:
    """Fetch EPA RadNet data"""
    data = fetch_json(EPA_RADNET_URL)
    if not data:
        return []
    
    observations = []
    for item in data:
        try:
            # EPA RadNet returns various radiation measurements
            # We focus on gamma readings (typical unit: CPM or µR/h)
            obs = {
                "id": f"epa_{item.get('STATION_ID', 'unknown')}_{int(time.time())}",
                "source": "EPA RadNet",
                "location": item.get('CITY_NAME', 'Unknown'),
                "country": "US",
                "lat": float(item.get('LATITUDE', 0)),
                "lon": float(item.get('LONGITUDE', 0)),
                "value": float(item.get('RESULT', 0)) * 10,  # Convert to nSv/h approximation
                "unit": "nSv/h",
                "severity": "normal",
                "baseline": 40.0,
                "delta": 0.0,
                "z_score": 0.0
            }
            
            # Calculate anomaly metrics
            obs["delta"] = obs["value"] - obs["baseline"]
            obs["z_score"] = obs["delta"] / max(obs["baseline"] * 0.2, 1)
            
            # Determine severity
            if obs["z_score"] > 3:
                obs["severity"] = "spike"
            elif obs["z_score"] > 1.5:
                obs["severity"] = "elevated"
            
            observations.append(obs)
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"Skipping malformed EPA record: {e}")
            continue
    
    return observations


def fetch_safecast() -> List[Dict[str, Any]]:
    """Fetch Safecast data"""
    data = fetch_json(SAFECAST_URL)
    if not data:
        return []
    
    observations = []
    for item in data:
        try:
            # Safecast returns CPM (counts per minute) - convert to nSv/h
            # Rough conversion: 1 CPM ≈ 0.0029 µSv/h = 2.9 nSv/h for typical detectors
            cpm = float(item.get('value', 0))
            nsv_h = cpm * 2.9
            
            obs = {
                "id": f"safecast_{item.get('id', 'unknown')}",
                "source": "Safecast",
                "location": f"{item.get('location_name', 'Unknown Location')}",
                "country": "Unknown",
                "lat": float(item.get('latitude', 0)),
                "lon": float(item.get('longitude', 0)),
                "value": nsv_h,
                "unit": "nSv/h",
                "severity": "normal",
                "baseline": 40.0,
                "delta": 0.0,
                "z_score": 0.0
            }
            
            # Calculate anomaly metrics
            obs["delta"] = obs["value"] - obs["baseline"]
            obs["z_score"] = obs["delta"] / max(obs["baseline"] * 0.2, 1)
            
            # Determine severity
            if obs["z_score"] > 3:
                obs["severity"] = "spike"
            elif obs["z_score"] > 1.5:
                obs["severity"] = "elevated"
            
            observations.append(obs)
        except (ValueError, KeyError, TypeError) as e:
            logger.debug(f"Skipping malformed Safecast record: {e}")
            continue
    
    return observations


def aggregate_observations(epa_obs: List[Dict], safecast_obs: List[Dict]) -> Dict[str, Any]:
    """Combine and analyze observations from both sources"""
    all_obs = epa_obs + safecast_obs
    
    # Calculate summary statistics
    anomaly_count = sum(1 for o in all_obs if o["z_score"] > 1.5)
    elevated_count = sum(1 for o in all_obs if o["severity"] == "elevated")
    spike_count = sum(1 for o in all_obs if o["severity"] == "spike")
    
    return {
        "status": "ONLINE" if all_obs else "DEGRADED",
        "lastUpdate": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_stations": len(all_obs),
            "anomaly_count": anomaly_count,
            "elevated_count": elevated_count,
            "spike_count": spike_count
        },
        "observations": all_obs[:100]  # Limit to 100 most recent
    }


def fetch_and_save():
    """Main fetch and save routine"""
    logger.info("Fetching radiation data...")
    
    # Fetch from both sources
    epa_obs = fetch_epa_radnet()
    logger.info(f"Fetched {len(epa_obs)} EPA RadNet observations")
    
    safecast_obs = fetch_safecast()
    logger.info(f"Fetched {len(safecast_obs)} Safecast observations")
    
    # Aggregate and format
    output = aggregate_observations(epa_obs, safecast_obs)
    
    # Ensure output size is reasonable
    output_json = json.dumps(output, indent=2)
    if len(output_json) > 2 * 1024 * 1024:  # 2MB limit
        logger.warning("Output exceeds 2MB, truncating observations")
        output["observations"] = output["observations"][:50]
        output_json = json.dumps(output, indent=2)
    
    # Write to file
    try:
        with open(OUTPUT_PATH, 'w') as f:
            f.write(output_json)
        logger.info(f"Saved {len(output['observations'])} observations to {OUTPUT_PATH}")
        logger.info(f"Summary: {output['summary']}")
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")


def run_continuous(interval: int = 900):
    """Run continuously with specified interval (default 15 minutes)"""
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
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 900
        run_continuous(interval)
    else:
        fetch_and_save()
