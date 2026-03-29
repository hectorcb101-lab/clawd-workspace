#!/usr/bin/env python3
"""Validate that all feed outputs match the required format"""

import json
import sys
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data")

def validate_radiation():
    """Validate radiation_live.json"""
    with open(DATA_DIR / "radiation_live.json") as f:
        data = json.load(f)
    
    assert data["status"] in ["ONLINE", "DEGRADED"], "Invalid status"
    assert "lastUpdate" in data, "Missing lastUpdate"
    assert "summary" in data, "Missing summary"
    assert all(k in data["summary"] for k in ["total_stations", "anomaly_count", "elevated_count", "spike_count"]), "Invalid summary"
    assert "observations" in data, "Missing observations"
    
    if data["observations"]:
        obs = data["observations"][0]
        required = ["id", "source", "location", "country", "lat", "lon", "value", "unit", "severity", "baseline", "delta", "z_score"]
        assert all(k in obs for k in required), f"Missing fields in observation: {set(required) - set(obs.keys())}"
    
    print(f"✓ radiation_live.json: {len(data['observations'])} observations, status={data['status']}")
    return True

def validate_earthquake():
    """Validate earthquake_live.json"""
    with open(DATA_DIR / "earthquake_live.json") as f:
        data = json.load(f)
    
    assert data["status"] in ["ONLINE", "DEGRADED"], "Invalid status"
    assert "lastUpdate" in data, "Missing lastUpdate"
    assert "count" in data, "Missing count"
    assert "significant" in data, "Missing significant"
    assert "earthquakes" in data, "Missing earthquakes"
    
    if data["earthquakes"]:
        eq = data["earthquakes"][0]
        required = ["id", "magnitude", "place", "lat", "lon", "depth_km", "time", "tsunami", "felt", "significance", "alert"]
        assert all(k in eq for k in required), f"Missing fields in earthquake: {set(required) - set(eq.keys())}"
    
    print(f"✓ earthquake_live.json: {data['count']} earthquakes, {data['significant']} significant")
    return True

def validate_gps_jamming():
    """Validate gps_jamming_live.json"""
    with open(DATA_DIR / "gps_jamming_live.json") as f:
        data = json.load(f)
    
    assert data["status"] in ["ONLINE", "DEGRADED"], "Invalid status"
    assert "lastUpdate" in data, "Missing lastUpdate"
    assert "stats" in data, "Missing stats"
    assert all(k in data["stats"] for k in ["total_zones", "high_count", "medium_count"]), "Invalid stats"
    assert "zones" in data, "Missing zones"
    
    if data["zones"]:
        zone = data["zones"][0]
        required = ["lat", "lon", "level", "region", "description", "radius_km"]
        assert all(k in zone for k in required), f"Missing fields in zone: {set(required) - set(zone.keys())}"
    
    print(f"✓ gps_jamming_live.json: {len(data['zones'])} zones, {data['stats']['high_count']} high intensity")
    return True

def check_file_sizes():
    """Ensure no file exceeds 2MB"""
    for json_file in [DATA_DIR / f for f in ["radiation_live.json", "earthquake_live.json", "gps_jamming_live.json"]]:
        size_mb = json_file.stat().st_size / (1024 * 1024)
        assert size_mb < 2, f"{json_file.name} exceeds 2MB: {size_mb:.2f}MB"
        print(f"✓ {json_file.name}: {size_mb*1024:.1f}KB (under 2MB limit)")
    return True

if __name__ == "__main__":
    try:
        validate_radiation()
        validate_earthquake()
        validate_gps_jamming()
        check_file_sizes()
        print("\n✅ All validations passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
