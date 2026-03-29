#!/usr/bin/env python3
"""
Civil Unrest Monitor Feed
Aggregates protest, riot, and demonstration data from ACLED and GDELT
Output: unrest_live.json
"""

import json
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
import os

# Output file path
OUTPUT_FILE = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/unrest_live.json"

# Sample fallback data
FALLBACK_DATA = {
    "status": "DEGRADED",
    "lastUpdate": None,
    "summary": {"total_events": 25, "protests": 20, "riots": 3, "strikes": 2},
    "events": [
        {
            "id": "sample-001",
            "type": "protest",
            "date": "2026-03-23",
            "country": "France",
            "location": "Paris",
            "lat": 48.86,
            "lon": 2.35,
            "fatalities": 0,
            "description": "Sample protest event (fallback data)",
            "source": "sample",
            "size_estimate": "medium"
        }
    ],
    "hotspots": [
        {
            "country": "France",
            "event_count": 10,
            "trend": "stable",
            "primary_cause": "economic"
        }
    ]
}

def log(msg: str):
    """Log with timestamp"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] {msg}", flush=True)

def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Optional[Dict]:
    """Fetch JSON from URL with error handling"""
    try:
        req = Request(url, headers=headers or {})
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except (URLError, HTTPError, json.JSONDecodeError, Exception) as e:
        log(f"Error fetching {url}: {e}")
        return None

def fetch_gdelt() -> List[Dict[str, Any]]:
    """Fetch protest/riot events from GDELT"""
    log("Fetching from GDELT...")
    
    # GDELT API - search for protest, riot, demonstration keywords
    query_params = {
        "query": "protest OR riot OR demonstration",
        "mode": "artlist",
        "format": "json",
        "maxrecords": "50",
        "sourcelang": "eng"
    }
    
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?{urlencode(query_params)}"
    data = fetch_json(url, timeout=20)
    
    events = []
    if data and data.get("articles"):
        for i, article in enumerate(data["articles"][:40]):
            # Extract location from article (GDELT provides country/location in some articles)
            title = article.get("title", "")
            url_src = article.get("url", "")
            
            # Try to extract country/location from title
            location, country, lat, lon = extract_location_from_text(title)
            
            # Determine event type from title
            event_type = "protest"
            if "riot" in title.lower():
                event_type = "riot"
            elif "strike" in title.lower():
                event_type = "strike"
            elif "demonstration" in title.lower():
                event_type = "demonstration"
            
            events.append({
                "id": f"gdelt-{article.get('seendate', '')}_{i}",
                "type": event_type,
                "date": article.get("seendate", datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"))[:8],  # YYYYMMDD
                "country": country,
                "location": location,
                "lat": lat,
                "lon": lon,
                "fatalities": 0,
                "description": title[:200],
                "source": "GDELT",
                "size_estimate": "unknown"
            })
    
    log(f"Fetched {len(events)} events from GDELT")
    return events

def extract_location_from_text(text: str) -> tuple:
    """Extract location info from text (very basic heuristic)"""
    # Common country/city mappings
    locations = {
        "paris": ("Paris", "France", 48.86, 2.35),
        "france": ("France", "France", 48.86, 2.35),
        "london": ("London", "United Kingdom", 51.5, -0.1),
        "berlin": ("Berlin", "Germany", 52.5, 13.4),
        "madrid": ("Madrid", "Spain", 40.4, -3.7),
        "rome": ("Rome", "Italy", 41.9, 12.5),
        "athens": ("Athens", "Greece", 37.98, 23.73),
        "delhi": ("Delhi", "India", 28.6, 77.2),
        "mumbai": ("Mumbai", "India", 19.08, 72.88),
        "beijing": ("Beijing", "China", 39.9, 116.4),
        "hong kong": ("Hong Kong", "Hong Kong", 22.3, 114.2),
        "tokyo": ("Tokyo", "Japan", 35.68, 139.65),
        "seoul": ("Seoul", "South Korea", 37.5, 127.0),
        "bangkok": ("Bangkok", "Thailand", 13.75, 100.5),
        "cairo": ("Cairo", "Egypt", 30.05, 31.25),
        "nairobi": ("Nairobi", "Kenya", -1.29, 36.82),
        "lagos": ("Lagos", "Nigeria", 6.45, 3.4),
        "buenos aires": ("Buenos Aires", "Argentina", -34.6, -58.4),
        "santiago": ("Santiago", "Chile", -33.45, -70.67),
        "mexico city": ("Mexico City", "Mexico", 19.43, -99.13),
        "new york": ("New York", "United States", 40.71, -74.01),
        "washington": ("Washington", "United States", 38.9, -77.0),
        "los angeles": ("Los Angeles", "United States", 34.05, -118.24),
    }
    
    text_lower = text.lower()
    for key, (location, country, lat, lon) in locations.items():
        if key in text_lower:
            return location, country, lat, lon
    
    # Default to unknown location
    return "Unknown", "Unknown", 0, 0

def fetch_acled() -> List[Dict[str, Any]]:
    """Fetch protest events from ACLED (requires API key, may fail)"""
    log("Attempting to fetch from ACLED...")
    
    # ACLED requires registration for API key
    # This is a placeholder - will likely fail without valid credentials
    # Format: https://api.acleddata.com/acled/read?terms=accept&limit=200
    
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%Y-%m-%d")
    
    # Try without key (may fail)
    params = {
        "terms": "accept",
        "limit": "100",
        "event_type": "Protests",
        "event_date": date_str,
        "event_date_where": ">="
    }
    
    url = f"https://api.acleddata.com/acled/read?{urlencode(params)}"
    data = fetch_json(url, timeout=20)
    
    events = []
    if data and data.get("data"):
        for event in data["data"][:50]:
            events.append({
                "id": f"acled-{event.get('event_id_cnty', '')}",
                "type": event.get("event_type", "protest").lower(),
                "date": event.get("event_date", date_str),
                "country": event.get("country", "Unknown"),
                "location": event.get("location", "Unknown"),
                "lat": float(event.get("latitude", 0)),
                "lon": float(event.get("longitude", 0)),
                "fatalities": int(event.get("fatalities", 0)),
                "description": event.get("notes", "")[:200],
                "source": "ACLED",
                "size_estimate": "large" if int(event.get("fatalities", 0)) > 5 else "medium"
            })
    
    log(f"Fetched {len(events)} events from ACLED")
    return events

def generate_hotspots(events: List[Dict]) -> List[Dict[str, Any]]:
    """Generate hotspot summary by country"""
    country_counts = {}
    
    for event in events:
        country = event.get("country", "Unknown")
        if country != "Unknown":
            if country not in country_counts:
                country_counts[country] = {"count": 0, "types": {}}
            country_counts[country]["count"] += 1
            event_type = event.get("type", "protest")
            country_counts[country]["types"][event_type] = country_counts[country]["types"].get(event_type, 0) + 1
    
    hotspots = []
    for country, data in sorted(country_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:15]:
        primary_type = max(data["types"].items(), key=lambda x: x[1])[0] if data["types"] else "protest"
        
        hotspots.append({
            "country": country,
            "event_count": data["count"],
            "trend": "increasing" if data["count"] > 5 else "stable",
            "primary_cause": "political" if primary_type == "riot" else "economic"
        })
    
    return hotspots

def collect_data() -> Dict[str, Any]:
    """Collect data from all sources"""
    log("Starting unrest data collection...")
    
    events = []
    
    # Try GDELT (more reliable, no key required)
    try:
        events.extend(fetch_gdelt())
    except Exception as e:
        log(f"GDELT failed: {e}")
    
    # Try ACLED (likely to fail without API key)
    try:
        acled_events = fetch_acled()
        events.extend(acled_events)
    except Exception as e:
        log(f"ACLED failed (expected without API key): {e}")
    
    # If all sources failed, use fallback
    if not events:
        log("All sources failed, using fallback data")
        result = FALLBACK_DATA.copy()
        result["lastUpdate"] = datetime.now(timezone.utc).isoformat()
        return result
    
    # Count event types
    type_counts = {"protests": 0, "riots": 0, "strikes": 0, "demonstrations": 0}
    for event in events:
        event_type = event.get("type", "protest")
        if event_type in type_counts:
            type_counts[event_type] += 1
        elif event_type == "demonstration":
            type_counts["protests"] += 1  # Count demonstrations as protests
        else:
            type_counts["protests"] += 1
    
    hotspots = generate_hotspots(events)
    
    output = {
        "status": "ONLINE",
        "lastUpdate": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_events": len(events),
            "protests": type_counts["protests"] + type_counts["demonstrations"],
            "riots": type_counts["riots"],
            "strikes": type_counts["strikes"]
        },
        "events": events[:100],  # Limit to 100
        "hotspots": hotspots
    }
    
    log(f"Collection complete: {len(events)} total events, {len(hotspots)} hotspots")
    return output

def write_output(data: Dict[str, Any]):
    """Write JSON output to file"""
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Check size (limit to 2MB)
        size_bytes = len(json_str.encode('utf-8'))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > 2.0:
            log(f"WARNING: Output size {size_mb:.2f}MB exceeds 2MB limit, truncating...")
            while size_mb > 2.0 and len(data["events"]) > 20:
                data["events"] = data["events"][:-10]
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        log(f"Output written to {OUTPUT_FILE} ({size_mb:.2f}MB)")
    except Exception as e:
        log(f"ERROR writing output: {e}")
        sys.exit(1)

def run_once():
    """Run a single data collection cycle"""
    data = collect_data()
    write_output(data)

def run_continuous(interval: int = 600):
    """Run continuously with specified interval (seconds)"""
    log(f"Starting continuous mode (interval: {interval}s)")
    
    while True:
        try:
            run_once()
        except Exception as e:
            log(f"ERROR in collection cycle: {e}")
        
        log(f"Sleeping for {interval}s...")
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 600
        run_continuous(interval)
    else:
        run_once()
