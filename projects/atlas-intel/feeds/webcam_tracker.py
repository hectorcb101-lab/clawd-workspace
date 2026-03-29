#!/usr/bin/env python3
"""
Atlas Intel — Webcam Tracker
Fetches global webcam data from Windy Webcams API v3.
Outputs webcam_live.json with camera locations, previews, and player URLs.

Strategy:
- Seed: Fetch webcams across strategic regions (conflict zones, capitals, key infrastructure)
- On-demand: Frontend requests fresh image URLs when user clicks a webcam marker
- Image tokens expire after 10 minutes (free tier), so we re-fetch on demand

API: https://api.windy.com/webcams/api/v3/webcams
Auth: X-WINDY-API-KEY header
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

# Try requests
try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [WEBCAM] %(message)s')
logger = logging.getLogger(__name__)

# --- Config ---
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "dashboard" / "data"
ENV_FILE = PROJECT_DIR / ".env"

# Load API key
API_KEY = os.environ.get("WINDY_WEBCAM_API_KEY", "")
if not API_KEY and ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("WINDY_WEBCAM_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not API_KEY:
    logger.error("No WINDY_WEBCAM_API_KEY found in environment or .env file")
    sys.exit(1)

BASE_URL = "https://api.windy.com/webcams/api/v3/webcams"
HEADERS = {"X-WINDY-API-KEY": API_KEY}

# Strategic regions to seed webcams from
# Format: (name, lat, lng, radius_km, limit)
STRATEGIC_REGIONS = [
    # Major world capitals & cities
    ("London", 51.5074, -0.1278, 30, 50),
    ("Washington DC", 38.9072, -77.0369, 30, 40),
    ("Moscow", 55.7558, 37.6173, 30, 40),
    ("Beijing", 39.9042, 116.4074, 30, 30),
    ("Tokyo", 35.6762, 139.6503, 30, 30),
    ("Paris", 48.8566, 2.3522, 30, 30),
    ("Berlin", 52.5200, 13.4050, 30, 30),
    ("Kyiv", 50.4501, 30.5234, 50, 40),
    ("Taipei", 25.0330, 121.5654, 30, 30),
    ("Seoul", 37.5665, 126.9780, 30, 30),
    ("Tel Aviv", 32.0853, 34.7818, 30, 30),
    ("Istanbul", 41.0082, 28.9784, 30, 30),
    ("Dubai", 25.2048, 55.2708, 30, 20),
    ("New York", 40.7128, -74.0060, 30, 40),
    ("Singapore", 1.3521, 103.8198, 20, 20),

    # Conflict zones & hotspots
    ("Ukraine - Odesa", 46.4825, 30.7233, 80, 30),
    ("Ukraine - Kharkiv", 49.9935, 36.2304, 80, 20),
    ("Gaza Region", 31.3547, 34.3088, 50, 15),
    ("Strait of Hormuz", 26.5667, 56.2500, 100, 15),
    ("South China Sea - Hainan", 18.2, 109.5, 100, 15),
    ("Taiwan Strait", 24.5, 119.5, 100, 20),

    # Critical infrastructure
    ("Suez Canal", 30.4278, 32.3442, 30, 15),
    ("Panama Canal", 9.0800, -79.6800, 20, 10),
    ("Strait of Malacca", 2.5, 101.5, 100, 15),
    ("Gibraltar", 36.1408, -5.3536, 30, 10),
    ("Bosphorus", 41.1194, 29.0750, 20, 15),

    # Military bases & ports
    ("Norfolk VA", 36.8508, -76.2859, 30, 15),
    ("San Diego", 32.7157, -117.1611, 30, 15),
    ("Pearl Harbor", 21.3500, -157.9500, 30, 10),
    ("Ramstein", 49.4369, 7.6003, 30, 10),
    ("Diego Garcia", -7.3195, 72.4229, 50, 5),
    ("Guam", 13.4443, 144.7937, 30, 10),
    ("Yokosuka", 35.2833, 139.6667, 20, 10),

    # Additional coverage
    ("Sydney", 33.8688, 151.2093, 30, 20),
    ("Mumbai", 19.0760, 72.8777, 30, 15),
    ("Cape Town", -33.9249, 18.4241, 30, 15),
    ("Rio de Janeiro", -22.9068, -43.1729, 30, 15),
    ("Arctic - Svalbard", 78.2, 15.6, 50, 5),
]


def fetch_webcams_nearby(lat: float, lng: float, radius_km: int, limit: int = 50) -> list:
    """Fetch webcams near a coordinate."""
    params = {
        "lang": "en",
        "limit": limit,
        "offset": 0,
        "nearby": f"{lat},{lng},{radius_km}",
        "include": "location,categories,images,player",
    }
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("webcams", [])
        else:
            logger.warning(f"API returned {resp.status_code}: {resp.text[:200]}")
            return []
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return []


def categorize_webcam(cam: dict) -> str:
    """Classify webcam by strategic relevance."""
    categories = [c.get("id", "") for c in cam.get("categories", [])]
    title = cam.get("title", "").lower()

    if any(c in categories for c in ["traffic", "road"]):
        return "traffic"
    elif any(c in categories for c in ["harbor", "port", "ship"]):
        return "maritime"
    elif any(c in categories for c in ["airport", "airfield"]):
        return "aviation"
    elif any(c in categories for c in ["city", "square", "building"]):
        return "urban"
    elif any(c in categories for c in ["landscape", "mountain", "coast", "beach"]):
        return "landscape"
    elif any(c in categories for c in ["weather", "meteo"]):
        return "weather"
    elif any(word in title for word in ["military", "base", "navy", "army", "air force", "port", "harbor"]):
        return "military"
    elif any(word in title for word in ["border", "crossing", "checkpoint"]):
        return "border"
    else:
        return "general"


def process_webcam(cam: dict, region_name: str) -> dict:
    """Process a raw webcam into our format."""
    location = cam.get("location", {})
    images = cam.get("images", {})
    current = images.get("current", {})
    daylight = images.get("daylight", {})
    player = cam.get("player", {})

    return {
        "id": cam.get("webcamId"),
        "title": cam.get("title", "Unknown"),
        "status": cam.get("status", "unknown"),
        "lat": location.get("latitude", 0),
        "lng": location.get("longitude", 0),
        "city": location.get("city", ""),
        "region": location.get("region", ""),
        "country": location.get("country", ""),
        "country_code": location.get("country_code", ""),
        "continent": location.get("continent", ""),
        "category": categorize_webcam(cam),
        "categories": [c.get("id", "") for c in cam.get("categories", [])],
        "strategic_region": region_name,
        "last_updated": cam.get("lastUpdatedOn", ""),
        "view_count": cam.get("viewCount", 0),
        "images": {
            "preview": current.get("preview", ""),
            "thumbnail": current.get("thumbnail", ""),
            "icon": current.get("icon", ""),
            "daylight_preview": daylight.get("preview", ""),
            "daylight_thumbnail": daylight.get("thumbnail", ""),
        },
        "player": {
            "day": player.get("day", ""),
            "month": player.get("month", ""),
            "live": player.get("live", ""),
        },
    }


def seed_all_regions() -> dict:
    """Fetch webcams from all strategic regions."""
    all_webcams = {}
    stats = {
        "total": 0,
        "by_region": {},
        "by_category": {},
        "by_country": {},
        "active": 0,
        "inactive": 0,
    }

    for region_name, lat, lng, radius, limit in STRATEGIC_REGIONS:
        logger.info(f"Fetching webcams near {region_name} ({lat}, {lng}, {radius}km)...")
        cams = fetch_webcams_nearby(lat, lng, radius, limit)
        region_count = 0

        for cam in cams:
            cam_id = cam.get("webcamId")
            if cam_id and cam_id not in all_webcams:
                processed = process_webcam(cam, region_name)
                all_webcams[cam_id] = processed
                region_count += 1

                # Stats
                cat = processed["category"]
                country = processed["country"]
                stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
                stats["by_country"][country] = stats["by_country"].get(country, 0) + 1
                if processed["status"] == "active":
                    stats["active"] += 1
                else:
                    stats["inactive"] += 1

        stats["by_region"][region_name] = region_count
        logger.info(f"  → {len(cams)} fetched, {region_count} new (deduped)")

        # Rate limiting — be nice to the API
        time.sleep(0.5)

    stats["total"] = len(all_webcams)
    return {
        "webcams": list(all_webcams.values()),
        "stats": stats,
    }


def main():
    """Main entry point."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=== Atlas Intel Webcam Tracker ===")
    logger.info(f"Seeding from {len(STRATEGIC_REGIONS)} strategic regions...")

    result = seed_all_regions()

    # Sort by view count (most popular first)
    result["webcams"].sort(key=lambda w: w.get("view_count", 0), reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "windy_webcams_api_v3",
        "total_webcams": result["stats"]["total"],
        "active": result["stats"]["active"],
        "inactive": result["stats"]["inactive"],
        "regions_seeded": len(STRATEGIC_REGIONS),
        "stats": result["stats"],
        "webcams": result["webcams"],
    }

    out_path = DATA_DIR / "webcam_live.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"\n=== WEBCAM SEED COMPLETE ===")
    logger.info(f"Total webcams: {result['stats']['total']}")
    logger.info(f"Active: {result['stats']['active']}, Inactive: {result['stats']['inactive']}")
    logger.info(f"Categories: {json.dumps(result['stats']['by_category'], indent=2)}")
    logger.info(f"Output: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
