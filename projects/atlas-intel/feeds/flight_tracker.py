#!/usr/bin/env python3
"""
Atlas Intel Live Flight Tracker
Fetches real-time aircraft positions from OpenSky Network API
Produces dashboard-ready JSON for 3D globe visualization

FREE API - No authentication required
Rate limit: 10 seconds between requests (anonymous)
"""

import json
import logging
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("ERROR: requests module not found. Install with: pip3 install requests")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENSKY_API_URL = "https://opensky-network.org/api/states/all"
RATE_LIMIT_SECONDS = 10  # OpenSky anonymous rate limit

OUTPUT_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data")
OUTPUT_LIVE = OUTPUT_DIR / "flight_live.json"
OUTPUT_STATUS = OUTPUT_DIR / "flight_status.json"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# MILITARY DETECTION DATABASE
# ============================================================================

# Known military callsign prefixes (US, NATO, and other countries)
MILITARY_CALLSIGN_PREFIXES = {
    # United States
    "RCH", "REACH",      # C-17, C-5, C-130 transport
    "DUKE",              # C-17 special ops
    "EVAC",              # Medical evacuation
    "FORTE",             # RQ-4 Global Hawk recon
    "HOMER",             # Tanker
    "CHIEF",             # VIP transport
    "KING",              # HC-130 rescue
    "SPAR",              # Special Air Mission
    "VALOR",             # Training
    "VIPER",             # Fighter
    "GRIZZLY",           # C-130
    "PAT",               # Training
    "METAL",             # Cargo
    "KNIFE",             # Special ops
    "NAVY",              # USN
    "ARMY",              # USA
    "AIR",               # USAF (e.g., AIR FORCE ONE)
    "COAST",             # USCG
    "BLUE",              # Training
    "RED",               # Aggressor training
    "HAWG",              # A-10
    "JOSA",              # Training
    "TABOO",             # E-3 AWACS
    "PITCH",             # Tanker
    "QUID",              # Tanker
    "EXXON",             # Tanker
    "SHELL",             # Tanker
    "MOBIL",             # Tanker
    "TEXACO",            # Tanker
    "LAGR",              # C-130
    "TAMP",              # Tanker
    
    # NATO & European
    "NATO",              # NATO
    "RAVEN",             # RAF
    "TARTAN",            # RAF
    "STATIC",            # RAF tanker
    "ASCOT",             # RAF transport
    "RRR",               # RAF
    "RAFAIR",            # RAF
    "CHAOS",             # Luftwaffe tanker
    "TIGER",             # NATO Tiger Meet
    "WITCH",             # RAF
    "VENOM",             # RAF
    "PANTHER",           # German
    "COBRA",             # Belgian
    "LION",              # Netherlands
    "EAGLE",             # NATO
    "HAWK",              # Multiple countries
    
    # Russian
    "RFF",               # Russian Air Force
    "RSD",               # Russian State
    "CTM",               # Charter (often military)
    "CNV",               # Russian Navy
    
    # Other
    "RSAF",              # Saudi Arabia
    "HADES",             # Surveillance
    "MAGE",              # Surveillance
    "JAKE",              # Training
}

# Military ICAO24 hex ranges (examples - not comprehensive)
# Format: (start_hex, end_hex, country)
MILITARY_ICAO24_RANGES = [
    # United States (AE prefix)
    ("ae0000", "afffff", "United States"),
    
    # United Kingdom (43c000-43dfff)
    ("43c000", "43dfff", "United Kingdom"),
    
    # Russia (150000-1fffff)
    ("150000", "1fffff", "Russia"),
    
    # China (780000-7fffff)
    ("780000", "7fffff", "China"),
    
    # India (800000-83ffff)
    ("800000", "83ffff", "India"),
    
    # France (380000-3bffff)
    ("380000", "3bffff", "France"),
    
    # Germany (3c0000-3fffff)
    ("3c0000", "3fffff", "Germany"),
]

# Known military aircraft types by ICAO type code
MILITARY_AIRCRAFT_TYPES = {
    "C130": "C-130 Hercules",
    "C17": "C-17 Globemaster III",
    "C5": "C-5 Galaxy",
    "KC135": "KC-135 Stratotanker",
    "KC10": "KC-10 Extender",
    "KC46": "KC-46 Pegasus",
    "E3": "E-3 Sentry (AWACS)",
    "E8": "E-8 JSTARS",
    "RQ4": "RQ-4 Global Hawk",
    "MQ9": "MQ-9 Reaper",
    "F15": "F-15 Eagle",
    "F16": "F-16 Fighting Falcon",
    "F18": "F/A-18 Hornet",
    "F22": "F-22 Raptor",
    "F35": "F-35 Lightning II",
    "A10": "A-10 Thunderbolt II",
    "B52": "B-52 Stratofortress",
    "B1": "B-1 Lancer",
    "B2": "B-2 Spirit",
    "P8": "P-8 Poseidon",
    "RC135": "RC-135 Rivet Joint",
    "U2": "U-2 Dragon Lady",
}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================================================
# AIRCRAFT TRACKING STATE
# ============================================================================

class AircraftTracker:
    """Tracks aircraft positions and detects anomalies"""
    
    def __init__(self):
        # Track aircraft history for anomaly detection
        self.aircraft_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.last_fetch_time = None
        
    def fetch_all_aircraft(self, max_retries: int = 1) -> dict | None:
        """Fetch all aircraft from OpenSky Network API with retry logic"""
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Fetching aircraft data from {OPENSKY_API_URL} (attempt {attempt}/{max_retries})")
                response = requests.get(OPENSKY_API_URL, timeout=15)
                
                if response.status_code == 429:
                    logger.warning("Rate limit hit (429) - OpenSky Network is throttling requests")
                    if attempt < max_retries:
                        logger.info("Waiting 30 seconds before retry...")
                        time.sleep(30)
                        continue
                    return None
                
                if response.status_code != 200:
                    logger.error(f"API returned status {response.status_code}: {response.text[:200]}")
                    return None
                
                data = response.json()
                logger.info(f"✓ Received data from OpenSky Network (time: {data.get('time')}, states: {len(data.get('states', [])) if data.get('states') else 0})")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout after 60 seconds (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    logger.info("Retrying in 10 seconds...")
                    time.sleep(10)
                    continue
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(10)
                    continue
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return None
        
        return None
    
    def categorize_aircraft(self, callsign: str | None, icao24: str, origin_country: str) -> tuple[str, str | None]:
        """
        Categorize aircraft and detect type
        Returns: (category, aircraft_type)
        Categories: military, commercial, cargo, private, helicopter, unknown
        """
        # Check military callsign prefixes
        if callsign:
            callsign_upper = callsign.strip().upper()
            
            # Check for military prefixes
            for prefix in MILITARY_CALLSIGN_PREFIXES:
                if callsign_upper.startswith(prefix):
                    # Try to identify aircraft type
                    aircraft_type = None
                    for type_code, type_name in MILITARY_AIRCRAFT_TYPES.items():
                        if type_code.upper() in callsign_upper:
                            aircraft_type = type_name
                            break
                    
                    return "military", aircraft_type
            
            # Commercial airlines (IATA 3-letter + flight number)
            if len(callsign_upper) >= 3 and callsign_upper[:3].isalpha() and callsign_upper[3:].isdigit():
                # Common cargo airline codes
                cargo_codes = {"FDX", "UPS", "ABX", "GTI", "SWN", "CKS", "FWI", "NCR"}
                if callsign_upper[:3] in cargo_codes:
                    return "cargo", None
                return "commercial", None
            
            # Cargo indicators
            if any(cargo in callsign_upper for cargo in ["CARGO", "FREIGHT", "FDX", "UPS"]):
                return "cargo", None
        
        # Check ICAO24 military ranges
        icao24_lower = icao24.lower()
        for start_hex, end_hex, country in MILITARY_ICAO24_RANGES:
            if start_hex <= icao24_lower <= end_hex:
                return "military", None
        
        # Helicopter indicators (very rough heuristic)
        # In reality, would need aircraft type database
        
        # Default categorization
        if callsign and len(callsign.strip()) > 0:
            # Has callsign, probably commercial or private
            return "commercial", None
        
        return "unknown", None
    
    def detect_circling(self, icao24: str, heading: float | None, lat: float, lon: float) -> bool:
        """
        Detect if aircraft is circling (heading changes > 270° in recent history)
        """
        if heading is None:
            return False
        
        history = self.aircraft_history[icao24]
        history.append({
            "heading": heading,
            "lat": lat,
            "lon": lon,
            "time": time.time()
        })
        
        if len(history) < 5:
            return False
        
        # Check heading changes over last 5 samples (roughly 5 minutes at 1 sample/min)
        recent = list(history)[-5:]
        total_heading_change = 0
        
        for i in range(1, len(recent)):
            prev_heading = recent[i-1]["heading"]
            curr_heading = recent[i]["heading"]
            
            # Calculate smallest angle between headings
            diff = abs(curr_heading - prev_heading)
            if diff > 180:
                diff = 360 - diff
            
            total_heading_change += diff
        
        # If total heading change > 270° in 5 samples, probably circling
        return total_heading_change > 270
    
    def detect_anomalies(self, aircraft_list: list[dict]) -> list[dict]:
        """Detect anomalous aircraft behavior"""
        anomalies = []
        
        for aircraft in aircraft_list:
            icao24 = aircraft["icao24"]
            callsign = aircraft.get("callsign")
            lat = aircraft["lat"]
            lon = aircraft["lon"]
            alt = aircraft.get("alt")
            heading = aircraft.get("heading")
            category = aircraft["category"]
            
            # Circling detection
            if self.detect_circling(icao24, heading, lat, lon):
                anomalies.append({
                    "type": "circling",
                    "callsign": callsign or icao24,
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "description": f"Aircraft {callsign or icao24} detected circling at {lat:.2f}, {lon:.2f}"
                })
            
            # Altitude anomalies
            if alt is not None:
                # Very high altitude (above 45,000 ft / 13,716 m) - possible recon
                if alt > 13716:
                    anomalies.append({
                        "type": "high_altitude",
                        "callsign": callsign or icao24,
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "description": f"High altitude flight {callsign or icao24} at {alt:.0f}m ({alt*3.28084:.0f}ft)"
                    })
                
                # Very low altitude (below 1,000 ft / 305 m) and not on ground
                if alt < 305 and not aircraft.get("on_ground", False):
                    anomalies.append({
                        "type": "low_altitude",
                        "callsign": callsign or icao24,
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "description": f"Low altitude flight {callsign or icao24} at {alt:.0f}m ({alt*3.28084:.0f}ft)"
                    })
            
            # Military aircraft in unusual locations (could add geofencing logic)
            if category == "military":
                # This is a placeholder - could add specific conflict zone checks
                pass
        
        return anomalies
    
    def process_opensky_data(self, data: dict) -> tuple[list[dict], list[dict], int]:
        """
        Process OpenSky API response
        Returns: (aircraft_list, military_aircraft, total_tracked)
        """
        if not data or "states" not in data or data["states"] is None:
            logger.warning("No aircraft data in API response")
            return [], [], 0
        
        states = data["states"]
        logger.info(f"Processing {len(states)} aircraft states")
        
        aircraft_list = []
        military_aircraft = []
        
        for state in states:
            # OpenSky state vector format (17 fields):
            # 0: icao24, 1: callsign, 2: origin_country, 3: time_position, 4: last_contact,
            # 5: longitude, 6: latitude, 7: baro_altitude, 8: on_ground, 9: velocity,
            # 10: true_track, 11: vertical_rate, 12: sensors, 13: geo_altitude, 14: squawk, 15: spi, 16: position_source
            
            if len(state) < 17:
                continue
            
            icao24 = state[0]
            callsign = state[1].strip() if state[1] else None
            origin_country = state[2] or "Unknown"
            longitude = state[5]
            latitude = state[6]
            baro_altitude = state[7]  # meters
            on_ground = state[8] or False
            velocity = state[9]  # m/s
            true_track = state[10]  # degrees
            vertical_rate = state[11]  # m/s
            geo_altitude = state[13]  # meters
            
            # Skip aircraft without position
            if longitude is None or latitude is None:
                continue
            
            # Use geo_altitude if baro_altitude not available
            altitude = baro_altitude if baro_altitude is not None else geo_altitude
            
            # Categorize aircraft
            category, aircraft_type = self.categorize_aircraft(callsign, icao24, origin_country)
            
            # Convert velocity from m/s to knots (if available)
            speed_knots = velocity * 1.94384 if velocity is not None else None
            
            # Build aircraft object
            aircraft = {
                "icao24": icao24,
                "callsign": callsign,
                "lat": latitude,
                "lon": longitude,
                "alt": altitude,  # meters
                "speed": round(speed_knots, 1) if speed_knots is not None else None,  # knots
                "heading": round(true_track, 1) if true_track is not None else None,  # degrees
                "vertical_rate": vertical_rate,  # m/s
                "on_ground": on_ground,
                "category": category,
                "origin_country": origin_country,
            }
            
            if aircraft_type:
                aircraft["aircraft_type"] = aircraft_type
            
            aircraft_list.append(aircraft)
            
            # Separate military aircraft
            if category == "military":
                military_aircraft.append(aircraft)
        
        logger.info(f"Processed: {len(aircraft_list)} total, {len(military_aircraft)} military")
        
        return aircraft_list, military_aircraft, len(aircraft_list)
    
    def generate_flight_routes(self, aircraft_list: list[dict], limit: int = 100) -> list[dict]:
        """
        Generate flight routes for visualization (origin -> destination arcs)
        Since we don't have route info from OpenSky, we'll generate synthetic routes
        based on current positions and headings for visualization purposes
        """
        routes = []
        
        # Take sample of aircraft (prioritize military and high-value)
        sample = []
        
        # First add all military
        sample.extend([a for a in aircraft_list if a["category"] == "military"])
        
        # Then add commercial up to limit
        commercial = [a for a in aircraft_list if a["category"] == "commercial"]
        sample.extend(commercial[:limit - len(sample)])
        
        # Generate synthetic routes (in real system, would need flight plan database)
        for aircraft in sample[:limit]:
            lat = aircraft["lat"]
            lon = aircraft["lon"]
            heading = aircraft.get("heading")
            
            if heading is None:
                continue
            
            # Estimate destination based on heading (very rough approximation)
            # In production, would use actual flight plan data
            distance_deg = 20  # ~2000km range
            
            import math
            heading_rad = math.radians(heading)
            dest_lat = lat + (distance_deg * math.cos(heading_rad))
            dest_lon = lon + (distance_deg * math.sin(heading_rad))
            
            # Clamp to valid ranges
            dest_lat = max(-90, min(90, dest_lat))
            dest_lon = ((dest_lon + 180) % 360) - 180
            
            # Color based on category
            color_map = {
                "military": "#ff0000",  # red
                "commercial": "#ffd700",  # gold
                "cargo": "#00ff00",  # green
                "private": "#0080ff",  # blue
                "unknown": "#808080",  # gray
            }
            
            routes.append({
                "origin": {"lat": lat, "lng": lon},
                "destination": {"lat": dest_lat, "lng": dest_lon},
                "color": color_map.get(aircraft["category"], "#808080")
            })
        
        return routes
    
    def write_outputs(self, aircraft_list: list[dict], military_aircraft: list[dict], 
                      total_tracked: int, anomalies: list[dict]):
        """Write both JSON output files"""
        
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Write flight_live.json (new detailed format)
        live_data = {
            "status": "ONLINE",
            "tracked": total_tracked,
            "anomalies": len(anomalies),
            "lastUpdate": now,
            "aircraft": aircraft_list,
            "military_aircraft": military_aircraft,
            "anomalies_list": anomalies
        }
        
        try:
            # Check size before writing
            json_str = json.dumps(live_data, indent=2)
            size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
            
            if size_mb > 5:
                logger.warning(f"flight_live.json is {size_mb:.2f}MB, trimming aircraft list")
                # Trim aircraft list, keep all military
                commercial_count = len([a for a in aircraft_list if a["category"] != "military"])
                trim_ratio = 4.5 / size_mb  # Aim for 4.5MB
                keep_commercial = int(commercial_count * trim_ratio)
                
                aircraft_list_trimmed = military_aircraft.copy()
                aircraft_list_trimmed.extend([a for a in aircraft_list if a["category"] != "military"][:keep_commercial])
                
                live_data["aircraft"] = aircraft_list_trimmed
                live_data["tracked"] = len(aircraft_list_trimmed)
                json_str = json.dumps(live_data, indent=2)
            
            with open(OUTPUT_LIVE, "w") as f:
                f.write(json_str)
            
            logger.info(f"✓ Wrote {OUTPUT_LIVE} ({len(json_str.encode('utf-8')) / 1024:.1f} KB)")
        
        except Exception as e:
            logger.error(f"Failed to write {OUTPUT_LIVE}: {e}")
        
        # 2. Write flight_status.json (backward compatible format)
        # Generate flight routes for visualization
        routes = self.generate_flight_routes(aircraft_list, limit=100)
        
        status_data = {
            "status": "ONLINE",
            "tracked": total_tracked,
            "anomalies": len(anomalies),
            "flights": routes
        }
        
        try:
            with open(OUTPUT_STATUS, "w") as f:
                f.write(json.dumps(status_data, indent=2))
            
            logger.info(f"✓ Wrote {OUTPUT_STATUS}")
        
        except Exception as e:
            logger.error(f"Failed to write {OUTPUT_STATUS}: {e}")

# ============================================================================
# TEST/DEMO MODE
# ============================================================================

def generate_sample_data() -> dict:
    """Generate sample aircraft data for testing when API is unavailable"""
    import random
    
    logger.info("Generating sample aircraft data for demonstration")
    
    sample_callsigns = [
        ("BAW123", "commercial", "United Kingdom", 51.5, -0.12),
        ("UAL456", "commercial", "United States", 40.7, -74.0),
        ("RCH234", "military", "United States", 35.0, 33.0),
        ("FORTE12", "military", "United States", 45.0, 35.0),
        ("FDX789", "cargo", "United States", 35.2, -89.9),
        ("UPS101", "cargo", "United States", 38.9, -77.0),
        ("AFR447", "commercial", "France", 48.8, 2.3),
        ("DLH400", "commercial", "Germany", 50.0, 8.5),
        ("RRR1234", "military", "United Kingdom", 51.0, -1.0),
        ("DUKE01", "military", "United States", 36.0, -115.0),
    ]
    
    states = []
    
    for i, (callsign, category, country, base_lat, base_lon) in enumerate(sample_callsigns):
        # Add some randomness to positions
        lat = base_lat + random.uniform(-2, 2)
        lon = base_lon + random.uniform(-2, 2)
        
        # Generate realistic flight parameters
        if category == "military":
            alt = random.uniform(8000, 12000)  # Military often fly higher
            speed = random.uniform(400, 600)
        else:
            alt = random.uniform(9000, 11000)  # Commercial cruise altitude
            speed = random.uniform(400, 500)
        
        heading = random.uniform(0, 360)
        
        # OpenSky state vector format
        state = [
            f"abc{i:04d}",  # icao24
            callsign,        # callsign
            country,         # origin_country
            time.time(),     # time_position
            time.time(),     # last_contact
            lon,             # longitude
            lat,             # latitude
            alt,             # baro_altitude (meters)
            False,           # on_ground
            speed / 1.94384, # velocity (m/s)
            heading,         # true_track
            random.uniform(-5, 5),  # vertical_rate
            None,            # sensors
            alt,             # geo_altitude
            None,            # squawk
            False,           # spi
            0                # position_source
        ]
        states.append(state)
    
    # Add more random commercial flights
    for i in range(50):
        lat = random.uniform(-60, 60)
        lon = random.uniform(-180, 180)
        alt = random.uniform(9000, 11000)
        speed = random.uniform(400, 500)
        heading = random.uniform(0, 360)
        
        state = [
            f"xyz{i:04d}",
            f"COM{random.randint(100, 999)}",
            random.choice(["United States", "United Kingdom", "France", "Germany", "Japan"]),
            time.time(),
            time.time(),
            lon,
            lat,
            alt,
            False,
            speed / 1.94384,
            heading,
            random.uniform(-5, 5),
            None,
            alt,
            None,
            False,
            0
        ]
        states.append(state)
    
    return {
        "time": int(time.time()),
        "states": states
    }

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def fetch_flightradar24(regions=None) -> dict | None:
    """
    Fetch aircraft from FlightRadar24 public feed as fallback.
    Converts FR24 format to OpenSky-compatible format.
    FR24 public feed fields per aircraft:
      [0]=icao24, [1]=lat, [2]=lon, [3]=heading, [4]=altitude(ft),
      [5]=speed(kts), [6]=squawk, [7]=radar, [8]=type, [9]=registration,
      [10]=timestamp, [11]=origin, [12]=destination, [13]=callsign,
      [14]=?, [15]=?, [16]=airline, [17]=on_ground, [18]=vspeed
    """
    if regions is None:
        # Cover key areas globally (lamax, lamin, lomin, lomax, limit)
        regions = [
            (70, 35, -15, 40, 1500),     # Europe
            (35, 10, 25, 65, 500),        # Middle East
            (55, 10, 95, 145, 800),       # East Asia / Pacific
            (55, 25, -130, -60, 1500),    # North America
            (10, -35, -80, -35, 300),     # South America
            (35, 0, -20, 55, 300),        # Africa
        ]
    
    all_states = []
    for lamax, lamin, lomin, lomax, limit in regions:
        try:
            url = (
                f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js"
                f"?faa=1&satellite=1&mlat=1&adsb=1&gnd=0&air=1"
                f"&vehicles=0&estimated=0&gliders=0&stats=0"
                f"&maxage=14400&limit={limit}"
                f"&bounds={lamax},{lamin},{lomin},{lomax}"
            )
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            if resp.status_code != 200:
                logger.warning(f"FR24 returned {resp.status_code} for region")
                continue
            
            data = resp.json()
            for key, val in data.items():
                if not isinstance(val, list) or len(val) < 14:
                    continue
                
                # FR24 feed format:
                # [0]=icao24, [1]=lat, [2]=lon, [3]=heading, [4]=altitude_ft,
                # [5]=speed_kts, [6]=squawk, [7]=radar, [8]=aircraft_type,
                # [9]=registration, [10]=timestamp, [11]=origin_airport,
                # [12]=dest_airport, [13]=flight_number, [14]=?, [15]=?,
                # [16]=callsign, [17]=on_ground, [18]=vspeed
                icao24 = str(val[0]).lower() if val[0] else key
                try:
                    lat = float(val[1]) if val[1] not in (None, '') else None
                    lon = float(val[2]) if val[2] not in (None, '') else None
                    heading = float(val[3]) if val[3] not in (None, '') else 0
                    alt_ft = float(val[4]) if val[4] not in (None, '') else None
                    speed_kts = float(val[5]) if val[5] not in (None, '') else None
                except (ValueError, TypeError):
                    continue
                callsign = str(val[16]).strip() if len(val) > 16 and val[16] else (
                    str(val[13]).strip() if len(val) > 13 and val[13] else "")
                on_ground = bool(val[17]) if len(val) > 17 else False
                try:
                    vspeed = float(val[18]) if len(val) > 18 and val[18] not in (None, '') else 0
                except (ValueError, TypeError):
                    vspeed = 0
                
                if not lat or not lon:
                    continue
                
                # Convert to OpenSky state vector format
                alt_m = (alt_ft * 0.3048) if alt_ft else None
                speed_ms = (speed_kts * 0.514444) if speed_kts else None
                vspeed_ms = (vspeed * 0.00508) if vspeed else 0  # ft/min to m/s
                
                state = [
                    icao24, callsign, "", int(time.time()), int(time.time()),
                    lon, lat, alt_m, on_ground, speed_ms, heading, vspeed_ms,
                    None, alt_m, None, False, 0
                ]
                all_states.append(state)
            
            time.sleep(0.3)  # Rate limit between regions
            
        except Exception as e:
            logger.warning(f"FR24 region fetch failed: {e}")
            continue
    
    if all_states:
        logger.info(f"✓ FR24 fallback: fetched {len(all_states)} aircraft across {len(regions)} regions")
        return {"time": int(time.time()), "states": all_states}
    
    return None


def run_once(use_sample_data: bool = False):
    """Run a single fetch cycle"""
    logger.info("=" * 60)
    logger.info("Atlas Intel Flight Tracker - Single Run")
    if use_sample_data:
        logger.info("MODE: Sample Data (Demo)")
    logger.info("=" * 60)
    
    tracker = AircraftTracker()
    
    # Fetch data — try OpenSky first, then FR24, then sample
    if use_sample_data:
        data = generate_sample_data()
    else:
        data = tracker.fetch_all_aircraft()
        
        if data is None:
            logger.info("OpenSky failed — trying FlightRadar24 fallback...")
            data = fetch_flightradar24()
    
    if data is None:
        logger.error("All live sources failed - falling back to sample data")
        data = generate_sample_data()
    
    # Process data
    aircraft_list, military_aircraft, total_tracked = tracker.process_opensky_data(data)
    
    if total_tracked == 0:
        logger.warning("No aircraft tracked")
        # Write empty status
        tracker.write_outputs([], [], 0, [])
        return False
    
    # Detect anomalies
    anomalies = tracker.detect_anomalies(aircraft_list)
    
    logger.info(f"Detected {len(anomalies)} anomalies")
    
    # Write outputs
    tracker.write_outputs(aircraft_list, military_aircraft, total_tracked, anomalies)
    
    logger.info("=" * 60)
    logger.info("Summary:")
    logger.info(f"  Total aircraft: {total_tracked}")
    logger.info(f"  Military: {len(military_aircraft)}")
    logger.info(f"  Anomalies: {len(anomalies)}")
    logger.info(f"  Outputs: {OUTPUT_LIVE}, {OUTPUT_STATUS}")
    logger.info("=" * 60)
    
    return True

def run_continuous(interval: int = 15, use_sample_data: bool = False):
    """
    Run continuous monitoring daemon
    Args:
        interval: seconds between updates (minimum 10 due to OpenSky rate limit)
        use_sample_data: use sample data instead of live API
    """
    if interval < RATE_LIMIT_SECONDS and not use_sample_data:
        logger.warning(f"Interval {interval}s is below rate limit {RATE_LIMIT_SECONDS}s, using {RATE_LIMIT_SECONDS}s")
        interval = RATE_LIMIT_SECONDS
    
    logger.info("=" * 60)
    logger.info("Atlas Intel Flight Tracker - Continuous Mode")
    if use_sample_data:
        logger.info("MODE: Sample Data (Demo)")
    logger.info(f"Update interval: {interval} seconds")
    logger.info(f"OpenSky API: {OPENSKY_API_URL}")
    logger.info(f"Outputs: {OUTPUT_LIVE}, {OUTPUT_STATUS}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    tracker = AircraftTracker()
    cycle = 0
    
    while True:
        try:
            cycle += 1
            logger.info(f"\n--- Cycle {cycle} ---")
            
            # Fetch data
            if use_sample_data:
                data = generate_sample_data()
            else:
                data = tracker.fetch_all_aircraft()
                
                # Fallback chain: OpenSky → FR24 → sample
                if data is None:
                    logger.info("OpenSky failed — trying FlightRadar24 fallback...")
                    data = fetch_flightradar24()
                
                if data is None:
                    logger.warning("All live sources failed, using sample data for this cycle")
                    data = generate_sample_data()
            
            if data is not None:
                # Process data
                aircraft_list, military_aircraft, total_tracked = tracker.process_opensky_data(data)
                
                # Detect anomalies
                anomalies = tracker.detect_anomalies(aircraft_list)
                
                # Write outputs
                tracker.write_outputs(aircraft_list, military_aircraft, total_tracked, anomalies)
                
                logger.info(f"Cycle {cycle} complete: {total_tracked} aircraft, {len(military_aircraft)} military, {len(anomalies)} anomalies")
            else:
                logger.error(f"Cycle {cycle} failed: no data received")
            
            # Wait for next cycle
            logger.info(f"Waiting {interval} seconds until next update...")
            time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Shutdown requested by user")
            logger.info(f"Completed {cycle} cycles")
            logger.info("=" * 60)
            break
        
        except Exception as e:
            logger.error(f"Error in cycle {cycle}: {e}", exc_info=True)
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "continuous":
            # Continuous mode
            interval = 15
            use_sample = False
            
            for arg in sys.argv[2:]:
                if arg == "sample":
                    use_sample = True
                else:
                    try:
                        interval = int(arg)
                    except ValueError:
                        print(f"Invalid argument: {arg}")
                        sys.exit(1)
            
            run_continuous(interval=interval, use_sample_data=use_sample)
        
        elif sys.argv[1] == "sample":
            # Single run with sample data
            success = run_once(use_sample_data=True)
            sys.exit(0 if success else 1)
        
        elif sys.argv[1] == "help":
            print("Atlas Intel Flight Tracker")
            print()
            print("Usage:")
            print("  python3 flight_tracker.py                 # Run once with live API data")
            print("  python3 flight_tracker.py sample          # Run once with sample data")
            print("  python3 flight_tracker.py continuous      # Run continuously (15s interval)")
            print("  python3 flight_tracker.py continuous 30   # Custom interval (seconds)")
            print("  python3 flight_tracker.py continuous sample  # Continuous with sample data")
            print("  python3 flight_tracker.py help            # Show this help")
            print()
            print("Outputs:")
            print(f"  {OUTPUT_LIVE}")
            print(f"  {OUTPUT_STATUS}")
            print()
            print("Data source: OpenSky Network (https://opensky-network.org)")
            print("Rate limit: 10 seconds between requests (anonymous)")
            print()
            print("Note: If API is unreachable, automatically falls back to sample data")
            sys.exit(0)
        
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Run 'python3 flight_tracker.py help' for usage")
            sys.exit(1)
    
    else:
        # Default: single run
        success = run_once()
        sys.exit(0 if success else 1)
