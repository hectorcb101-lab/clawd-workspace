# New Atlas Intel Feed Modules

Three new data feed modules have been built for the Atlas Intel intelligence dashboard.

## Created Feeds

### 1. satellite_tracker.py
**Purpose:** Track satellites using CelesTrak TLE data

**Features:**
- Fetches TLE data from CelesTrak (free, no auth needed)
- Tracks 14,000+ satellites including military, GPS, Starlink, and Chinese Yaogan series
- Uses SGP4 library to propagate orbits and calculate current lat/lng/altitude
- Identifies 386+ military satellites
- Monitors passes over conflict zones

**Output:** `/dashboard/data/satellite_status.json`
```json
{
  "status": "online",
  "tracked": 14771,
  "military": 386,
  "last_update": "ISO_TIMESTAMP",
  "satellites": [
    {
      "name": "USA-326",
      "lat": 35.2,
      "lng": -118.5,
      "alt_km": 420,
      "type": "military",
      "country": "US"
    }
  ]
}
```

**Run:**
```bash
# Test mode (single poll)
python3 feeds/satellite_tracker.py test

# Daemon mode (continuous polling every 5 min)
python3 feeds/satellite_tracker.py
```

---

### 2. military_tracker.py
**Purpose:** Aggregate military activity signals from multiple sources

**Features:**
- Pulls from ACLED API for armed conflict events (requires free registration)
- Pulls from GDELT for military-tagged events
- Cross-references with flight tracker military detections
- Aggregates events into regional hotspots with intensity ratings
- Monitors 7 conflict regions globally

**Output:** `/dashboard/data/military_status.json`
```json
{
  "status": "online",
  "events": 23,
  "hotspots": [
    {
      "region": "Eastern Ukraine",
      "lat": 48.5,
      "lng": 37.0,
      "intensity": "HIGH",
      "type": "armed_conflict",
      "details": "23 events: military_news, armed_conflict",
      "event_count": 23
    }
  ],
  "last_update": "ISO_TIMESTAMP"
}
```

**Configuration (optional):**
Set environment variables for ACLED API:
```bash
export ACLED_EMAIL="your@email.com"
export ACLED_KEY="your_api_key"
```

**Run:**
```bash
# Test mode (single poll)
python3 feeds/military_tracker.py test

# Daemon mode (continuous polling every 10 min)
python3 feeds/military_tracker.py
```

---

### 3. market_impact.py
**Purpose:** Real-time market correlation engine

**Features:**
- Uses yfinance library (free, no API key needed)
- Tracks VIX, oil futures (CL=F), gold (GC=F), defense ETF (ITA), S&P500 (^GSPC)
- Calculates percentage changes
- Correlates significant market movements with geopolitical events
- Monitors market reactions to global events

**Output:** `/dashboard/data/market_status.json`
```json
{
  "status": "online",
  "markets": {
    "VIX": {"value": 26.15, "change_pct": -2.35},
    "OIL": {"value": 89.04, "change_pct": 0.0},
    "GOLD": {"value": 4411.7, "change_pct": 0.0},
    "DEFENSE": {"value": 223.35, "change_pct": 0.35},
    "SP500": {"value": 6581.0, "change_pct": 1.15}
  },
  "correlations": [
    {
      "event": "Hormuz tension",
      "market_impact": "Oil +2.1%",
      "timestamp": "ISO_TIMESTAMP"
    }
  ],
  "last_update": "ISO_TIMESTAMP"
}
```

**Run:**
```bash
# Test mode (single poll)
python3 feeds/market_impact.py test

# Daemon mode (continuous polling every 5 min)
python3 feeds/market_impact.py
```

---

## Installation

Required packages (already installed):
```bash
pip install sgp4 yfinance
```

## Feed Patterns

All feeds follow the same pattern as existing feeds (flight_tracker.py):
- ✅ Main class with polling logic
- ✅ Error handling (API failures don't crash the feed)
- ✅ Logging to stdout with timestamps
- ✅ Test mode for single-poll verification
- ✅ Daemon mode for continuous monitoring
- ✅ JSON output to dashboard/data/
- ✅ JSONL event logging to logs/

## File Structure

```
/home/ubuntu/clawd/projects/atlas-intel/
├── feeds/
│   ├── satellite_tracker.py    (new)
│   ├── military_tracker.py     (new)
│   ├── market_impact.py        (new)
│   ├── flight_tracker.py       (existing)
│   └── ...
├── dashboard/data/
│   ├── satellite_status.json   (new)
│   ├── military_status.json    (new)
│   ├── market_status.json      (new)
│   └── ...
└── logs/
    ├── satellite_tracker.log   (new)
    ├── satellite_events.jsonl  (new)
    ├── military_tracker.log    (new)
    ├── military_events.jsonl   (new)
    ├── market_impact.log       (new)
    └── market_events.jsonl     (new)
```

## Status

✅ **All feeds operational and tested**
✅ **Valid JSON output produced**
✅ **Executable standalone**
✅ **Free APIs only (no paid keys required)**
✅ **Following existing code patterns**

---

*Built: 2026-03-23*
