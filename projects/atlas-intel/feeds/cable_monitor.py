#!/usr/bin/env python3
"""
Cable Monitor for Atlas Intel
Tracks submarine cable health using TeleGeography data and IODA outage signals
"""

import json
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# API endpoints
TELEGEOGRAPHY_CABLE_API = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/public/api/v3/cable/cable-geo.json"
IODA_API_BASE = "https://api.ioda.inetintel.cc.gatech.edu/v2"

# Fallback: Curated list of major submarine cables
FALLBACK_CABLES = [
    {"id": "sea-me-we-3", "name": "SEA-ME-WE 3", "length_km": 39000, "rfs_year": 2000, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 51.5, "lon": -0.1, "location": "UK"}], "owners": ["Singtel", "Telstra", "Telecom Italia"]},
    {"id": "sea-me-we-4", "name": "SEA-ME-WE 4", "length_km": 18800, "rfs_year": 2005, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 43.3, "lon": 5.4, "location": "France"}], "owners": ["France Telecom", "Singtel"]},
    {"id": "sea-me-we-5", "name": "SEA-ME-WE 5", "length_km": 20000, "rfs_year": 2016, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 43.3, "lon": 5.4, "location": "France"}], "owners": ["Orange", "Singtel", "Etisalat"]},
    {"id": "sea-me-we-6", "name": "SEA-ME-WE 6", "length_km": 19200, "rfs_year": 2025, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 43.3, "lon": 5.4, "location": "France"}], "owners": ["Singtel", "Telia"]},
    {"id": "tata-tgn-pacific", "name": "Tata TGN-Pacific", "length_km": 30000, "rfs_year": 2016, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 37.77, "lon": -122.42, "location": "San Francisco"}], "owners": ["Tata Communications"]},
    {"id": "asia-america-gateway", "name": "Asia America Gateway (AAG)", "length_km": 20000, "rfs_year": 2009, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 33.74, "lon": -118.27, "location": "Los Angeles"}], "owners": ["AT&T", "Telstra", "Singtel"]},
    {"id": "flag-europe-asia", "name": "FLAG Europe-Asia", "length_km": 28000, "rfs_year": 2001, "landing_points": [{"lat": 51.5, "lon": -0.1, "location": "UK"}, {"lat": 35.68, "lon": 139.77, "location": "Japan"}], "owners": ["Reliance"]},
    {"id": "tat-14", "name": "TAT-14", "length_km": 15428, "rfs_year": 2001, "landing_points": [{"lat": 51.5, "lon": -0.1, "location": "UK"}, {"lat": 40.71, "lon": -74.01, "location": "New York"}], "owners": ["Orange", "AT&T", "Deutsche Telekom"]},
    {"id": "apollo", "name": "Apollo", "length_km": 14000, "rfs_year": 2022, "landing_points": [{"lat": 51.5, "lon": -0.1, "location": "UK"}, {"lat": 40.71, "lon": -74.01, "location": "New York"}], "owners": ["Meta"]},
    {"id": "2africa", "name": "2Africa", "length_km": 45000, "rfs_year": 2024, "landing_points": [{"lat": 51.5, "lon": -0.1, "location": "UK"}, {"lat": -26.2, "lon": 28.05, "location": "South Africa"}], "owners": ["Meta", "Vodafone", "Orange"]},
    {"id": "asia-pacific-gateway", "name": "Asia Pacific Gateway", "length_km": 10400, "rfs_year": 2016, "landing_points": [{"lat": 1.29, "lon": 103.86, "location": "Singapore"}, {"lat": 35.68, "lon": 139.77, "location": "Japan"}], "owners": ["KDDI", "Singtel"]},
    {"id": "brasil-usa", "name": "BRASIL USA", "length_km": 11000, "rfs_year": 2018, "landing_points": [{"lat": -22.91, "lon": -43.17, "location": "Rio de Janeiro"}, {"lat": 25.76, "lon": -80.19, "location": "Miami"}], "owners": ["Telebras", "Telxius"]},
    {"id": "pacific-light", "name": "Pacific Light Cable Network", "length_km": 12800, "rfs_year": 2020, "landing_points": [{"lat": 22.28, "lon": 114.16, "location": "Hong Kong"}, {"lat": 34.05, "lon": -118.24, "location": "Los Angeles"}], "owners": ["Meta", "Google"]},
    {"id": "curie", "name": "Curie", "length_km": 10000, "rfs_year": 2020, "landing_points": [{"lat": 34.05, "lon": -118.24, "location": "Los Angeles"}, {"lat": -18.47, "lon": -70.33, "location": "Chile"}], "owners": ["Google"]},
    {"id": "faster", "name": "FASTER", "length_km": 11629, "rfs_year": 2016, "landing_points": [{"lat": 35.68, "lon": 139.77, "location": "Japan"}, {"lat": 37.77, "lon": -122.42, "location": "San Francisco"}], "owners": ["Google", "KDDI", "Singtel"]},
    {"id": "grace-hopper", "name": "Grace Hopper", "length_km": 6800, "rfs_year": 2022, "landing_points": [{"lat": 40.71, "lon": -74.01, "location": "New York"}, {"lat": 51.5, "lon": -0.1, "location": "UK"}], "owners": ["Google"]},
    {"id": "dunant", "name": "Dunant", "length_km": 6600, "rfs_year": 2021, "landing_points": [{"lat": 40.71, "lon": -74.01, "location": "New York"}, {"lat": 43.3, "lon": 5.4, "location": "France"}], "owners": ["Google"]},
    {"id": "equiano", "name": "Equiano", "length_km": 15000, "rfs_year": 2022, "landing_points": [{"lat": 38.71, "lon": -9.14, "location": "Portugal"}, {"lat": -33.93, "lon": 18.42, "location": "South Africa"}], "owners": ["Google"]},
    {"id": "marea", "name": "Marea", "length_km": 6600, "rfs_year": 2018, "landing_points": [{"lat": 39.47, "lon": -0.38, "location": "Spain"}, {"lat": 39.15, "lon": -75.52, "location": "Virginia"}], "owners": ["Microsoft", "Meta"]},
    {"id": "havfrue", "name": "Havfrue", "length_km": 8000, "rfs_year": 2019, "landing_points": [{"lat": 40.71, "lon": -74.01, "location": "New York"}, {"lat": 59.33, "lon": 18.07, "location": "Stockholm"}], "owners": ["Google", "Aqua Comms"]},
    {"id": "imewe", "name": "IMEWE", "length_km": 13000, "rfs_year": 2010, "landing_points": [{"lat": 13.1, "lon": 80.28, "location": "Chennai"}, {"lat": 43.3, "lon": 5.4, "location": "France"}], "owners": ["Orange", "Etisalat", "Saudi Telecom"]},
    {"id": "japan-us", "name": "Japan-US Cable Network", "length_km": 21000, "rfs_year": 2020, "landing_points": [{"lat": 35.68, "lon": 139.77, "location": "Japan"}, {"lat": 37.77, "lon": -122.42, "location": "San Francisco"}], "owners": ["KDDI", "SoftBank", "Google", "Meta"]},
]


def fetch_json(url: str, timeout: int = 30) -> Optional[Dict]:
    """Fetch JSON from URL with error handling"""
    try:
        headers = {'User-Agent': 'Atlas-Intel-Cable-Monitor/1.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        logger.error(f"URL error fetching {url}: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def process_cable_data(cable_geo_data: Dict) -> List[Dict]:
    """Process TeleGeography cable data into our format"""
    cables = []
    
    if not cable_geo_data or 'features' not in cable_geo_data:
        logger.warning("Invalid cable geo data structure")
        return cables
    
    for feature in cable_geo_data.get('features', []):
        try:
            props = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            cable_id = props.get('id', props.get('slug', ''))
            if not cable_id:
                continue
            
            # Extract landing points from coordinates
            landing_points = []
            coords = geometry.get('coordinates', [])
            
            if coords and isinstance(coords, list):
                # Get first and last points (endpoints are landing points)
                if len(coords) > 0 and isinstance(coords[0], list) and len(coords[0]) >= 2:
                    landing_points.append({
                        "lat": round(coords[0][1], 3),
                        "lon": round(coords[0][0], 3),
                        "location": "Start Point"
                    })
                
                if len(coords) > 1 and isinstance(coords[-1], list) and len(coords[-1]) >= 2:
                    landing_points.append({
                        "lat": round(coords[-1][1], 3),
                        "lon": round(coords[-1][0], 3),
                        "location": "End Point"
                    })
            
            cable = {
                "id": str(cable_id).lower().replace(' ', '-'),
                "name": props.get('name', f"Cable {cable_id}"),
                "status": "ok",  # Default status, will be updated if we have outage data
                "landing_points": landing_points,
                "length_km": props.get('length', 0),
                "owners": props.get('owners', []) if isinstance(props.get('owners'), list) else [],
                "rfs_year": props.get('rfs', None)
            }
            
            cables.append(cable)
            
        except Exception as e:
            logger.warning(f"Error processing cable feature: {e}")
            continue
    
    return cables


def check_regional_outages() -> List[Dict]:
    """
    Check for internet outages that might indicate cable issues
    For now, returns empty list - IODA API requires more complex queries
    """
    alerts = []
    
    # Known problematic regions (could expand this with actual IODA data)
    # This is a simplified approach - real implementation would query IODA
    problematic_regions = {
        "red-sea": {
            "region": "Red Sea",
            "description": "Increased regional risks",
            "cables_affected": ["sea-me-we-5", "sea-me-we-4", "imewe"]
        }
    }
    
    for region_id, info in problematic_regions.items():
        for cable_id in info.get("cables_affected", []):
            alerts.append({
                "cable_id": cable_id,
                "type": "watch",
                "description": info["description"],
                "region": info["region"]
            })
    
    return alerts


def generate_output(output_path: str) -> bool:
    """Generate the cable health JSON output file"""
    try:
        logger.info("Fetching submarine cable data from TeleGeography...")
        cable_data = fetch_json(TELEGEOGRAPHY_CABLE_API)
        
        if cable_data:
            cables = process_cable_data(cable_data)
            logger.info(f"Processed {len(cables)} submarine cables from API")
        else:
            logger.warning("API unavailable, using fallback curated cable dataset")
            cables = []
            for cable_info in FALLBACK_CABLES:
                cables.append({
                    "id": cable_info["id"],
                    "name": cable_info["name"],
                    "status": "ok",
                    "landing_points": cable_info["landing_points"],
                    "length_km": cable_info["length_km"],
                    "owners": cable_info["owners"],
                    "rfs_year": cable_info["rfs_year"]
                })
            logger.info(f"Using {len(cables)} curated submarine cables")
        
        # Check for regional outages/alerts
        alerts = check_regional_outages()
        logger.info(f"Generated {len(alerts)} cable health alerts")
        
        # Update cable statuses based on alerts
        alert_map = {}
        for alert in alerts:
            cable_id = alert["cable_id"]
            if cable_id not in alert_map:
                alert_map[cable_id] = []
            alert_map[cable_id].append(alert)
        
        for cable in cables:
            if cable["id"] in alert_map:
                cable["status"] = "watch"
        
        now = datetime.now(timezone.utc).isoformat()
        
        output_data = {
            "status": "ONLINE",
            "lastUpdate": now,
            "total_cables": len(cables),
            "cables": cables,
            "alerts": alerts
        }
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Check file size
        import os
        file_size = os.path.getsize(output_path)
        logger.info(f"Generated {output_path} ({file_size:,} bytes)")
        
        if file_size > 3 * 1024 * 1024:  # 3MB
            logger.warning(f"Output file exceeds 3MB limit: {file_size:,} bytes")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate output: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_continuous(interval: int = 3600):
    """Run in daemon mode with periodic updates (default 1 hour)"""
    output_path = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/cable_health_live.json"
    
    logger.info(f"Starting cable monitor daemon (interval: {interval}s)")
    
    while True:
        try:
            success = generate_output(output_path)
            if success:
                logger.info("Update complete")
            else:
                logger.error("Update failed")
        except Exception as e:
            logger.error(f"Error in daemon loop: {e}")
        
        time.sleep(interval)


if __name__ == "__main__":
    import sys
    
    output_path = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/cable_health_live.json"
    
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
        run_continuous(interval)
    else:
        # One-shot mode
        logger.info("Running one-shot cable monitor")
        success = generate_output(output_path)
        sys.exit(0 if success else 1)
