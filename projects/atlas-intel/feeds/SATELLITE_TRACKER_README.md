# Satellite Tracker

Real-time satellite position tracker using CelesTrak TLE data and SGP4 propagation.

## Output

**File:** `dashboard/data/satellite_live.json`

**Format:**
```json
{
  "status": "ONLINE",
  "tracked": 420,
  "lastUpdate": "2026-03-23T22:53:57.619+00:00",
  "categories": {
    "military": 60,
    "communications": 85,
    "navigation": 54,
    "weather": 30,
    "science": 11,
    "starlink": 150,
    "other": 30
  },
  "satellites": [...],
  "notable": [...],
  "military_sats": [...]
}
```

## Usage

**One-shot mode** (generate once):
```bash
cd /home/ubuntu/clawd/projects/atlas-intel
.venv/bin/python3 feeds/satellite_tracker.py
```

**Continuous mode** (daemon, updates every 120s):
```bash
.venv/bin/python3 feeds/satellite_tracker.py continuous 120
```

## Features

- ✅ Tracks ~420-500 satellites across all categories
- ✅ Real SGP4 propagation to current time
- ✅ CelesTrak TLE data (free, no API key)
- ✅ 2-hour TLE caching (rate-limit friendly)
- ✅ Military satellite identification (USA, COSMOS, YAOGAN, OFEK, NROL)
- ✅ Notable satellites: ISS, Tiangong, Hubble
- ✅ Orbit classification: LEO, MEO, GEO, HEO
- ✅ Country/operator identification
- ✅ Output < 3MB (currently ~133KB)

## Data Sources

CelesTrak groups fetched:
- `stations` - Space stations (ISS, Tiangong, etc.)
- `starlink` - Starlink constellation (sampled to 150)
- `gps-ops` - GPS, GLONASS, Galileo, BeiDou
- `military` - Classified military satellites
- `weather` - NOAA, GOES, MetOp, Fengyun
- `resource` - Landsat, Sentinel
- `geo` - Geostationary communications

## Performance

- **First run:** ~12s (fetch TLEs from CelesTrak)
- **Subsequent runs:** ~0.5s (uses cached TLEs)
- **TLE cache:** 2 hours
- **Output size:** 133KB (420 satellites)
