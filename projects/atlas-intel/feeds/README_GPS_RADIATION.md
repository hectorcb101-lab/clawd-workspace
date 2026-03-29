# GPS Jamming & Radiation Tracking Feeds

Two new data feeds for the Atlas Intel dashboard.

## Scripts Created

### 1. GPS Jamming Tracker
**Script:** `feeds/gps_tracker.py`  
**Output:** `dashboard/data/gps_jamming_live.json`

**Data Source:**
- Primary: OSINT-derived estimates from known active jamming zones
- Attempted scraping: GPSJam.org (accessible but no structured API)

**Coverage:**
- Eastern Mediterranean (Russian/Syrian EW operations)
- Ukraine/Russia Border (critical intensity)
- Baltic States (Russian jamming)
- Northern Iraq/Turkey Border
- South China Sea

**Output Schema:**
```json
{
  "zones": [
    {
      "lat": float,
      "lon": float,
      "lng": float,
      "intensity": "low|medium|high|critical",
      "region": string,
      "source": "OSINT-derived estimate",
      "description": string,
      "last_detected": ISO8601,
      "radius_km": float
    }
  ],
  "count": int,
  "high_intensity": int,
  "generated_at": ISO8601
}
```

**Current Stats:**
- 5 jamming zones tracked
- 2 high-intensity zones
- All marked as OSINT-derived estimates

---

### 2. Radiation Monitoring Tracker
**Script:** `feeds/radiation_tracker.py`  
**Output:** `dashboard/data/radiation_live.json`

**Data Source:**
- Safecast API (https://api.safecast.org) - real crowdsourced radiation data
- 8 major regions: Tokyo, Fukushima, Berlin, London, New York, LA, Paris, Kyiv

**Features:**
- Fetches real-time measurements from Safecast network
- Converts CPM to µSv/h when needed
- Flags anomalies (readings > 0.5 µSv/h)
- Deduplicates stations by location

**Output Schema:**
```json
{
  "stations": [
    {
      "lat": float,
      "lon": float,
      "lng": float,
      "value": float,
      "unit": "µSv/h",
      "location": string,
      "device": string,
      "last_reading": ISO8601,
      "status": "normal|anomaly"
    }
  ],
  "count": int,
  "anomalies": int,
  "max_reading": float,
  "generated_at": ISO8601
}
```

**Current Stats:**
- 84 radiation stations tracked
- 4 anomalies detected
- Max reading: 30.3 µSv/h
- Real data from Safecast API

---

## Usage

Both scripts are standalone and can be run directly:

```bash
# Activate venv
cd /home/ubuntu/clawd/projects/atlas-intel
source .venv/bin/activate

# Run GPS tracker
python feeds/gps_tracker.py

# Run radiation tracker
python feeds/radiation_tracker.py
```

Both scripts automatically create output directories and write JSON to `dashboard/data/`.

---

## Dependencies

Already installed in project venv:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing (GPS tracker)

---

## Data Quality

**GPS Jamming:**
- OSINT-derived estimates based on known conflict zones
- Source field clearly marked
- Conservative intensity ratings
- Geographic coverage of major hotspots

**Radiation:**
- Real-time data from Safecast crowdsourced network
- 200+ measurements processed per run
- Deduplicated by location
- Anomaly detection with conservative threshold

---

## Integration Notes

Both outputs include:
- **Dual longitude fields:** `lon` and `lng` for compatibility
- **ISO8601 timestamps:** UTC timezone
- **Standard schema:** Consistent structure for dashboard parsing
- **Metadata:** Generation time, counts, statistics

Ready for dashboard integration.
