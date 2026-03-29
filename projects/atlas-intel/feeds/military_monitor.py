#!/usr/bin/env python3
"""
Military Activity Monitor for Atlas Intel
Aggregates military movements from multiple sources and produces intelligence summaries.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from math import radians, cos, sin, asin, sqrt
import urllib.request
import urllib.parse
import urllib.error

# Paths
VESSEL_DATA_PATH = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/vessel_live.json"
FLIGHT_DATA_PATH = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/flight_live.json"
OUTPUT_PATH = "/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/military_live.json"

# Known hotspots
HOTSPOTS = [
    {"name": "South China Sea — Spratly Islands", "lat": 10.0, "lon": 114.0, "radius_km": 500},
    {"name": "Taiwan Strait", "lat": 24.5, "lon": 120.0, "radius_km": 200},
    {"name": "Black Sea — Crimea", "lat": 44.5, "lon": 33.5, "radius_km": 300},
    {"name": "Persian Gulf — Strait of Hormuz", "lat": 26.5, "lon": 56.5, "radius_km": 400},
    {"name": "Red Sea — Bab-el-Mandeb", "lat": 12.6, "lon": 43.3, "radius_km": 300},
    {"name": "Baltic Sea — Kaliningrad", "lat": 54.7, "lon": 20.5, "radius_km": 250},
    {"name": "Korean Peninsula — DMZ Waters", "lat": 38.0, "lon": 127.5, "radius_km": 200},
    {"name": "Arctic — Northern Sea Route", "lat": 75.0, "lon": 90.0, "radius_km": 800},
]

# Known major military vessels database
KNOWN_VESSELS = {
    "US": {
        "carriers": [
            {"name": "USS Gerald R. Ford", "mmsi": "369970000", "class": "Ford-class"},
            {"name": "USS George H.W. Bush", "mmsi": "369970450", "class": "Nimitz-class"},
            {"name": "USS Harry S. Truman", "mmsi": "369970500", "class": "Nimitz-class"},
            {"name": "USS Dwight D. Eisenhower", "mmsi": "369970800", "class": "Nimitz-class"},
            {"name": "USS Carl Vinson", "mmsi": "369970700", "class": "Nimitz-class"},
            {"name": "USS Abraham Lincoln", "mmsi": "368962000", "class": "Nimitz-class"},
            {"name": "USS Ronald Reagan", "mmsi": "369970760", "class": "Nimitz-class"},
            {"name": "USS George Washington", "mmsi": "369970730", "class": "Nimitz-class"},
            {"name": "USS John C. Stennis", "mmsi": "369970740", "class": "Nimitz-class"},
            {"name": "USS Theodore Roosevelt", "mmsi": "369970710", "class": "Nimitz-class"},
        ],
        "cruisers": ["USS Shiloh", "USS Lake Erie", "USS Chancellorsville", "USS Antietam"],
        "destroyers": ["USS Barry", "USS Porter", "USS Carney", "USS Arleigh Burke"],
    },
    "RU": {
        "flagships": [
            {"name": "Admiral Kuznetsov", "type": "aircraft_carrier", "class": "Kuznetsov-class"},
            {"name": "Marshal Ustinov", "type": "cruiser", "class": "Slava-class"},
            {"name": "Varyag", "type": "cruiser", "class": "Slava-class"},
            {"name": "Admiral Gorshkov", "type": "frigate", "class": "Gorshkov-class"},
        ],
    },
    "CN": {
        "carriers": [
            {"name": "Liaoning", "hull": "16", "class": "Kuznetsov-class (modified)"},
            {"name": "Shandong", "hull": "17", "class": "Type 002"},
            {"name": "Fujian", "hull": "18", "class": "Type 003"},
        ],
        "destroyers": ["Nanchang", "Lhasa", "Dalian", "Yinchuan"],
    },
    "GB": {
        "carriers": [
            {"name": "HMS Queen Elizabeth", "class": "Queen Elizabeth-class"},
            {"name": "HMS Prince of Wales", "class": "Queen Elizabeth-class"},
        ],
        "destroyers": ["HMS Daring", "HMS Dauntless", "HMS Diamond", "HMS Dragon"],
    },
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points on Earth in kilometers."""
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return R * c


def is_military_mmsi(mmsi) -> bool:
    """Check if MMSI indicates a military/government vessel."""
    if not mmsi:
        return False
    
    # Convert to string if it's an integer
    mmsi_str = str(mmsi)
    
    if len(mmsi_str) < 3:
        return False
    
    # Military vessels often use specific MMSI ranges
    # 369970000-369999999: US military
    # 002XXXXXX-009XXXXXX: Various navies
    first_three = mmsi_str[:3]
    
    if mmsi_str.startswith("369970") or mmsi_str.startswith("369990"):
        return True
    if first_three in ["002", "003", "004", "005", "006", "007", "008", "009"]:
        return True
    
    return False


def is_military_vessel_name(name: str) -> bool:
    """Check if vessel name indicates military vessel."""
    if not name:
        return False
    
    name_lower = name.lower()
    military_indicators = [
        "uss ", "hms ", "ins ", "rfs ", "plan ", "ijn ",
        "carrier", "destroyer", "frigate", "corvette", "cruiser",
        "submarine", "patrol", "warship", "navy", "naval",
        "admiral", "general", "marshall", "fleet",
    ]
    
    return any(indicator in name_lower for indicator in military_indicators)


def classify_vessel_type(vessel: Dict) -> str:
    """Classify military vessel type."""
    name = vessel.get("name", "").lower()
    
    if "carrier" in name or "cvn" in name:
        return "aircraft_carrier"
    elif "destroyer" in name or "ddg" in name:
        return "destroyer"
    elif "cruiser" in name or "cg" in name:
        return "cruiser"
    elif "frigate" in name or "ffg" in name:
        return "frigate"
    elif "submarine" in name or "ssn" in name or "ssbn" in name:
        return "submarine"
    elif "patrol" in name or "corvette" in name:
        return "patrol_vessel"
    elif "amphibious" in name or "lhd" in name or "lpd" in name:
        return "amphibious"
    else:
        return "military_vessel"


def get_region(lat: float, lon: float) -> str:
    """Determine geographic region from coordinates."""
    if lat > 60:
        return "Arctic"
    elif lat < -60:
        return "Antarctic"
    elif -10 <= lat <= 30 and 30 <= lon <= 80:
        return "Indian Ocean"
    elif 0 <= lat <= 25 and 95 <= lon <= 125:
        return "South China Sea"
    elif 20 <= lat <= 45 and 115 <= lon <= 145:
        return "Western Pacific"
    elif -40 <= lat <= 0 and 100 <= lon <= 180:
        return "Southwest Pacific"
    elif 30 <= lat <= 50 and -130 <= lon <= -115:
        return "Northeast Pacific"
    elif 40 <= lat <= 50 and 26 <= lon <= 42:
        return "Black Sea"
    elif 24 <= lat <= 30 and 48 <= lon <= 61:
        return "Persian Gulf"
    elif 10 <= lat <= 20 and 40 <= lon <= 45:
        return "Red Sea"
    elif 30 <= lat <= 50 and -10 <= lon <= 40:
        return "Mediterranean"
    elif 35 <= lat <= 65 and -10 <= lon <= 30:
        return "North Atlantic"
    elif 50 <= lat <= 70 and 10 <= lon <= 30:
        return "Baltic Sea"
    else:
        return "Unknown"


def load_vessel_data() -> List[Dict]:
    """Load and filter military vessels from vessel_live.json."""
    try:
        if not os.path.exists(VESSEL_DATA_PATH):
            return []
        
        with open(VESSEL_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        vessels = data.get('vessels', [])
        military_vessels = []
        
        for vessel in vessels:
            # Check if vessel is military
            mmsi = vessel.get('mmsi', '')
            name = vessel.get('name', '')
            vessel_type = vessel.get('type', '')
            
            if vessel_type == 'military' or is_military_mmsi(mmsi) or is_military_vessel_name(name):
                lat = vessel.get('lat')
                lon = vessel.get('lon')
                
                if lat is not None and lon is not None:
                    military_vessel = {
                        "name": name or f"MMSI {mmsi}",
                        "mmsi": str(mmsi) if mmsi else "",
                        "type": classify_vessel_type(vessel),
                        "flag": vessel.get('flag', 'XX'),
                        "lat": lat,
                        "lon": lon,
                        "speed": vessel.get('speed', 0),
                        "heading": vessel.get('heading', 0) if vessel.get('heading') is not None else 0,
                        "region": get_region(lat, lon),
                        "class": "Unknown",
                    }
                    military_vessels.append(military_vessel)
        
        return military_vessels
    
    except Exception as e:
        print(f"Error loading vessel data: {e}")
        return []


def load_flight_data() -> List[Dict]:
    """Load military aircraft from flight_live.json."""
    try:
        if not os.path.exists(FLIGHT_DATA_PATH):
            return []
        
        with open(FLIGHT_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        # Extract military_aircraft section if it exists
        military_aircraft = data.get('military_aircraft', [])
        return military_aircraft
    
    except Exception as e:
        print(f"Error loading flight data: {e}")
        return []


def fetch_gdelt_events() -> List[Dict]:
    """Fetch recent military events from GDELT API."""
    events = []
    
    try:
        query = "military OR naval OR troops OR deployment OR warship"
        params = {
            'query': query,
            'mode': 'artlist',
            'format': 'json',
            'sourcelang': 'eng',
            'maxrecords': '50',
            'timespan': '24h',
        }
        
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Atlas-Intel/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        articles = data.get('articles', [])
        
        for article in articles[:20]:  # Limit to 20 events
            # Try to extract location from article
            # GDELT doesn't always provide coords, so this is best-effort
            title = article.get('title', '')
            url = article.get('url', '')
            seendate = article.get('seendate', '')
            
            # Parse seendate (format: YYYYMMDDTHHmmssZ)
            try:
                event_time = datetime.strptime(seendate, '%Y%m%dT%H%M%SZ')
                event_time_str = event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            except:
                event_time_str = datetime.now(timezone.utc).isoformat()
            
            # Simple heuristic geolocation based on keywords in title
            lat, lon = extract_location_from_text(title)
            
            if lat is not None and lon is not None:
                event = {
                    "time": event_time_str,
                    "type": "naval_movement" if "naval" in title.lower() or "ship" in title.lower() else "military_activity",
                    "description": title[:200],
                    "lat": lat,
                    "lon": lon,
                    "severity": assess_severity(title),
                    "source_url": url,
                }
                events.append(event)
    
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"GDELT API rate limit reached - will retry on next cycle")
        else:
            print(f"GDELT API HTTP error {e.code}: {e}")
    except Exception as e:
        print(f"Error fetching GDELT events: {e}")
    
    return events


def extract_location_from_text(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract approximate location from text using keyword matching."""
    text_lower = text.lower()
    
    # Location keywords mapped to approximate coordinates
    locations = {
        "south china sea": (10.0, 114.0),
        "spratly": (10.0, 114.0),
        "taiwan strait": (24.5, 120.0),
        "taiwan": (24.5, 120.0),
        "black sea": (44.5, 33.5),
        "crimea": (44.5, 33.5),
        "persian gulf": (26.5, 56.5),
        "strait of hormuz": (26.5, 56.5),
        "hormuz": (26.5, 56.5),
        "red sea": (20.0, 40.0),
        "yemen": (15.0, 44.0),
        "baltic": (58.0, 20.0),
        "korea": (38.0, 127.5),
        "korean": (38.0, 127.5),
        "ukraine": (49.0, 32.0),
        "syria": (35.0, 38.0),
        "mediterranean": (35.0, 18.0),
        "arctic": (75.0, 90.0),
    }
    
    for keyword, (lat, lon) in locations.items():
        if keyword in text_lower:
            return lat, lon
    
    return None, None


def assess_severity(text: str) -> str:
    """Assess event severity from text."""
    text_lower = text.lower()
    
    high_severity = ["attack", "strike", "missile", "combat", "conflict", "war", "explosion"]
    notable_severity = ["deployment", "exercise", "maneuver", "drill", "transit"]
    
    if any(word in text_lower for word in high_severity):
        return "high"
    elif any(word in text_lower for word in notable_severity):
        return "notable"
    else:
        return "routine"


def detect_naval_groups(vessels: List[Dict]) -> List[Dict]:
    """Detect groups of vessels within 50km of each other."""
    groups = []
    grouped_vessels = set()
    
    for i, vessel1 in enumerate(vessels):
        if i in grouped_vessels:
            continue
        
        group = [vessel1]
        lat1, lon1 = vessel1['lat'], vessel1['lon']
        
        for j, vessel2 in enumerate(vessels):
            if i == j or j in grouped_vessels:
                continue
            
            lat2, lon2 = vessel2['lat'], vessel2['lon']
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            
            if distance <= 50:  # Within 50km
                group.append(vessel2)
                grouped_vessels.add(j)
        
        if len(group) >= 2:  # At least 2 vessels
            grouped_vessels.add(i)
            
            # Calculate center point
            center_lat = sum(v['lat'] for v in group) / len(group)
            center_lon = sum(v['lon'] for v in group) / len(group)
            
            # Determine group name
            flags = list(set(v['flag'] for v in group))
            primary_flag = flags[0] if flags else "XX"
            
            vessel_names = [v['name'] for v in group[:5]]  # Max 5 names
            
            # Detect carrier groups
            has_carrier = any(v['type'] == 'aircraft_carrier' for v in group)
            group_type = "Carrier Strike Group" if has_carrier else "Naval Group"
            
            # Determine heading (average)
            avg_heading = sum(v['heading'] for v in group) / len(group)
            heading_str = heading_to_direction(avg_heading)
            
            naval_group = {
                "name": f"{primary_flag} {group_type}",
                "vessels": vessel_names,
                "center_lat": round(center_lat, 2),
                "center_lon": round(center_lon, 2),
                "heading": heading_str,
                "region": get_region(center_lat, center_lon),
                "threat_level": "normal",
                "activity": "routine patrol",
            }
            groups.append(naval_group)
    
    return groups


def heading_to_direction(heading: float) -> str:
    """Convert heading degrees to cardinal direction."""
    if heading < 0:
        heading += 360
    
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((heading + 22.5) / 45) % 8
    return directions[index]


def analyze_hotspots(vessels: List[Dict], events: List[Dict]) -> List[Dict]:
    """Analyze activity in known hotspot regions."""
    hotspot_data = []
    
    for hotspot in HOTSPOTS:
        hs_lat, hs_lon, radius = hotspot['lat'], hotspot['lon'], hotspot['radius_km']
        
        # Count vessels in hotspot
        assets_in_hotspot = []
        for vessel in vessels:
            distance = haversine_distance(hs_lat, hs_lon, vessel['lat'], vessel['lon'])
            if distance <= radius:
                asset = {
                    "type": "naval",
                    "name": vessel['name'],
                    "flag": vessel['flag'],
                    "lat": vessel['lat'],
                    "lon": vessel['lon'],
                }
                assets_in_hotspot.append(asset)
        
        # Count recent events in hotspot
        events_in_hotspot = []
        for event in events:
            if event.get('lat') and event.get('lon'):
                distance = haversine_distance(hs_lat, hs_lon, event['lat'], event['lon'])
                if distance <= radius:
                    events_in_hotspot.append(event)
        
        if assets_in_hotspot or events_in_hotspot:
            # Assess threat level
            asset_count = len(assets_in_hotspot)
            event_count = len(events_in_hotspot)
            high_severity_events = sum(1 for e in events_in_hotspot if e.get('severity') == 'high')
            
            if high_severity_events > 0 or asset_count > 10:
                threat_level = "critical"
            elif asset_count > 5 or event_count > 2:
                threat_level = "elevated"
            elif asset_count > 2:
                threat_level = "notable"
            else:
                threat_level = "normal"
            
            # Generate description
            vessel_summary = {}
            for asset in assets_in_hotspot:
                flag = asset['flag']
                vessel_summary[flag] = vessel_summary.get(flag, 0) + 1
            
            desc_parts = []
            for flag, count in sorted(vessel_summary.items(), key=lambda x: x[1], reverse=True):
                desc_parts.append(f"{count} {flag} vessels")
            
            description = f"Active monitoring — {', '.join(desc_parts[:3])}"
            if event_count > 0:
                description += f" — {event_count} recent events"
            
            hotspot_entry = {
                "name": hotspot['name'],
                "lat": hs_lat,
                "lon": hs_lon,
                "radius_km": radius,
                "threat_level": threat_level,
                "assets_count": asset_count,
                "description": description,
                "assets": assets_in_hotspot[:20],  # Limit to 20 assets
            }
            hotspot_data.append(hotspot_entry)
    
    return hotspot_data


def generate_military_report() -> Dict:
    """Generate complete military activity report."""
    print("Loading vessel data...")
    military_vessels = load_vessel_data()
    
    print("Loading flight data...")
    military_aircraft = load_flight_data()
    
    print("Fetching GDELT events...")
    recent_events = fetch_gdelt_events()
    
    print("Detecting naval groups...")
    naval_groups = detect_naval_groups(military_vessels)
    
    print("Analyzing hotspots...")
    hotspots = analyze_hotspots(military_vessels, recent_events)
    
    # Generate summary
    summary = {
        "total_assets": len(military_vessels) + len(military_aircraft),
        "naval_vessels": len(military_vessels),
        "military_aircraft": len(military_aircraft),
        "ground_forces": 0,  # Not tracked yet
        "hotspots": len(hotspots),
    }
    
    report = {
        "status": "ONLINE",
        "lastUpdate": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "naval_groups": naval_groups,
        "hotspots": hotspots,
        "military_vessels": military_vessels[:500],  # Limit to 500 vessels to keep under 2MB
        "military_aircraft": military_aircraft[:200],  # Limit to 200 aircraft
        "recent_events": recent_events[:50],  # Limit to 50 events
    }
    
    return report


def write_output(report: Dict):
    """Write report to output file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        
        # Write JSON
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report written to {OUTPUT_PATH}")
        print(f"Total assets: {report['summary']['total_assets']}")
        print(f"Naval vessels: {report['summary']['naval_vessels']}")
        print(f"Military aircraft: {report['summary']['military_aircraft']}")
        print(f"Hotspots: {report['summary']['hotspots']}")
        print(f"Naval groups: {len(report['naval_groups'])}")
        print(f"Recent events: {len(report['recent_events'])}")
        
    except Exception as e:
        print(f"Error writing output: {e}")


def run_once():
    """Run one monitoring cycle."""
    print(f"=== Military Activity Monitor - {datetime.now(timezone.utc).isoformat()} ===")
    report = generate_military_report()
    write_output(report)
    print("=== Complete ===\n")


def run_continuous(interval: int = 60):
    """Run monitoring continuously."""
    print(f"Starting continuous monitoring (interval: {interval}s)")
    while True:
        try:
            run_once()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            break
        except Exception as e:
            print(f"Error in monitoring cycle: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        run_continuous(interval)
    else:
        run_once()
