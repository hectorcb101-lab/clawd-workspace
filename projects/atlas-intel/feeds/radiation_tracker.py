#!/usr/bin/env python3
"""
Radiation Monitoring Tracker for Atlas Intel
Data source: Safecast API - global crowdsourced radiation measurements
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

# Safecast API endpoints - major regions of interest
SAFECAST_REGIONS = [
    {"name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503, "distance": 50000},
    {"name": "Fukushima, Japan", "lat": 37.4201, "lon": 140.4777, "distance": 50000},
    {"name": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050, "distance": 50000},
    {"name": "London, UK", "lat": 51.5074, "lon": -0.1278, "distance": 50000},
    {"name": "New York, USA", "lat": 40.7128, "lon": -74.0060, "distance": 50000},
    {"name": "Los Angeles, USA", "lat": 34.0522, "lon": -118.2437, "distance": 50000},
    {"name": "Paris, France", "lat": 48.8566, "lon": 2.3522, "distance": 50000},
    {"name": "Kyiv, Ukraine", "lat": 50.4501, "lon": 30.5234, "distance": 50000},
]

# Anomaly threshold (µSv/h)
ANOMALY_THRESHOLD = 0.5

def fetch_safecast_data(region: Dict) -> List[Dict]:
    """
    Fetch radiation measurements from Safecast API for a specific region
    API docs: https://github.com/Safecast/safecastapi
    """
    try:
        url = "https://api.safecast.org/measurements.json"
        params = {
            "latitude": region["lat"],
            "longitude": region["lon"],
            "distance": region["distance"],
            "limit": 100,
            "order": "created_at desc"
        }
        
        headers = {
            'User-Agent': 'Atlas-Intel-Monitor/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Fetched {len(data)} measurements from {region['name']}")
        
        return data
        
    except Exception as e:
        print(f"✗ Error fetching data for {region['name']}: {e}")
        return []

def process_measurements(measurements: List[Dict], region_name: str) -> List[Dict]:
    """Process raw Safecast measurements into station format"""
    stations = []
    
    for m in measurements:
        try:
            # Safecast value is in CPM (counts per minute) for Geiger counters
            # or µSv/h for direct radiation measurements
            value = m.get("value")
            unit = m.get("unit", "CPM")
            
            # Convert CPM to µSv/h if needed (rough approximation: CPM / 334)
            if unit == "cpm" or unit == "CPM":
                value_usv = value / 334.0 if value else 0
                unit = "µSv/h"
            else:
                value_usv = value if value else 0
            
            # Skip invalid measurements
            if value_usv is None or value_usv < 0:
                continue
            
            lat = m.get("latitude")
            lon = m.get("longitude")
            
            if lat is None or lon is None:
                continue
            
            station = {
                "lat": float(lat),
                "lon": float(lon),
                "lng": float(lon),  # Both lon and lng fields as requested
                "value": round(value_usv, 4),
                "unit": unit,
                "location": m.get("location_name") or region_name,
                "device": m.get("device_type_name") or m.get("sensor_type") or "Unknown",
                "last_reading": m.get("captured_at") or m.get("created_at") or datetime.now(timezone.utc).isoformat(),
                "status": "anomaly" if value_usv > ANOMALY_THRESHOLD else "normal"
            }
            
            stations.append(station)
            
        except Exception as e:
            print(f"  Skipping measurement due to error: {e}")
            continue
    
    return stations

def generate_radiation_data():
    """Generate radiation monitoring data from Safecast API"""
    
    print("Radiation Tracker - Fetching data from Safecast API...")
    
    all_stations = []
    
    # Fetch data from multiple regions
    for region in SAFECAST_REGIONS:
        measurements = fetch_safecast_data(region)
        stations = process_measurements(measurements, region["name"])
        all_stations.extend(stations)
    
    # Remove duplicates (same location, keep latest)
    unique_stations = {}
    for station in all_stations:
        key = (station["lat"], station["lon"])
        if key not in unique_stations:
            unique_stations[key] = station
        else:
            # Keep the one with more recent reading
            if station["last_reading"] > unique_stations[key]["last_reading"]:
                unique_stations[key] = station
    
    stations_list = list(unique_stations.values())
    
    # Calculate statistics
    anomaly_count = sum(1 for s in stations_list if s["status"] == "anomaly")
    max_reading = max([s["value"] for s in stations_list], default=0.0)
    
    output = {
        "stations": stations_list,
        "count": len(stations_list),
        "anomalies": anomaly_count,
        "max_reading": round(max_reading, 4),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    return output

def main():
    """Main execution"""
    print("Radiation Monitoring Tracker - Starting...")
    
    # Generate data
    data = generate_radiation_data()
    
    # Ensure output directory exists
    output_path = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/radiation_live.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Radiation data written to {output_path}")
    print(f"  Stations tracked: {data['count']}")
    print(f"  Anomalies detected: {data['anomalies']}")
    print(f"  Max reading: {data['max_reading']} µSv/h")
    
    return data

if __name__ == "__main__":
    main()
