# Atlas Intel Flight Tracker

Real-time global aircraft tracking feed for the Atlas Intel dashboard.

## Overview

Fetches live aircraft positions from the **OpenSky Network** free API and generates dashboard-ready JSON files for the 3D globe visualization.

- **Tracks**: ~5000+ aircraft globally
- **Categorizes**: Commercial, cargo, military, private, helicopter, unknown
- **Detects**: Military aircraft, anomalies (circling, unusual altitude)
- **Outputs**: Two JSON formats (live positions + backward-compatible routes)

## Data Source

- **API**: OpenSky Network (https://opensky-network.org)
- **Endpoint**: `https://opensky-network.org/api/states/all`
- **Authentication**: None required (anonymous)
- **Rate Limit**: 10 seconds between requests
- **Coverage**: Global, real-time ADS-B data

## Outputs

### 1. flight_live.json (Detailed Format)

Individual aircraft positions for live tracking:

```json
{
  "status": "ONLINE",
  "tracked": 5000,
  "anomalies": 12,
  "lastUpdate": "2026-03-23T22:00:00Z",
  "aircraft": [
    {
      "icao24": "abc123",
      "callsign": "BAW123",
      "lat": 51.5,
      "lon": -0.12,
      "alt": 9500,
      "speed": 450,
      "heading": 270,
      "vertical_rate": 0,
      "on_ground": false,
      "category": "commercial",
      "origin_country": "United Kingdom"
    }
  ],
  "military_aircraft": [
    {
      "icao24": "ae1234",
      "callsign": "RCH234",
      "lat": 35.0,
      "lon": 33.0,
      "alt": 11000,
      "speed": 480,
      "heading": 90,
      "category": "military",
      "origin_country": "United States",
      "aircraft_type": "C-17 Globemaster III"
    }
  ],
  "anomalies_list": [
    {
      "type": "circling",
      "callsign": "ABC123",
      "lat": 51.5,
      "lon": -0.12,
      "alt": 3000,
      "description": "Aircraft ABC123 detected circling at 51.50, -0.12"
    }
  ]
}
```

### 2. flight_status.json (Backward Compatible)

Flight routes for arc visualization:

```json
{
  "status": "ONLINE",
  "tracked": 5000,
  "anomalies": 12,
  "flights": [
    {
      "origin": {"lat": 51.5, "lng": -0.1},
      "destination": {"lat": 40.7, "lng": -74.0},
      "color": "#ffd700"
    }
  ]
}
```

## Aircraft Categories

1. **Military**: Detected by callsign prefix (RCH, DUKE, FORTE, etc.) or ICAO24 hex range
2. **Commercial**: Regular airline flights
3. **Cargo**: Freight carriers (FDX, UPS, etc.)
4. **Private**: General aviation
5. **Helicopter**: Rotorcraft (heuristic-based)
6. **Unknown**: Unable to categorize

## Military Detection

### Callsign Prefixes

US Military:
- `RCH/REACH` - C-17, C-5, C-130 transport
- `DUKE` - C-17 special ops
- `EVAC` - Medical evacuation
- `FORTE` - RQ-4 Global Hawk recon
- `SPAR` - Special Air Mission
- `NAVY`, `ARMY`, `AIR` - Service branches

NATO/European:
- `NATO` - NATO operations
- `ASCOT` - RAF transport
- `RRR` - RAF
- `CHAOS` - Luftwaffe tanker

Russian:
- `RFF` - Russian Air Force
- `CTM` - Charter (often military)

### ICAO24 Hex Ranges

- `ae0000-afffff` - United States
- `43c000-43dfff` - United Kingdom (military subset)
- `150000-1fffff` - Russia
- `780000-7fffff` - China

## Anomaly Detection

1. **Circling**: Heading changes > 270° in 5 samples (~5 minutes)
2. **High Altitude**: Above 45,000 ft (13,716m) - possible reconnaissance
3. **Low Altitude**: Below 1,000 ft (305m) while airborne - tactical operations
4. **Conflict Zones**: (Placeholder for geofencing logic)

## Usage

### Single Run (Default)

Fetch once and exit:

```bash
python3 flight_tracker.py
```

### Single Run with Sample Data

Test with synthetic data (when API unavailable):

```bash
python3 flight_tracker.py sample
```

### Continuous Mode

Run as daemon (15-second interval):

```bash
python3 flight_tracker.py continuous
```

Custom interval (minimum 10 seconds):

```bash
python3 flight_tracker.py continuous 30
```

Continuous with sample data:

```bash
python3 flight_tracker.py continuous sample
```

## Error Handling

- **API Timeout**: Retries once after 10 seconds
- **Rate Limit (429)**: Waits 30 seconds before retry
- **Network Errors**: Logs error and falls back to sample data
- **JSON Too Large**: Auto-trims commercial aircraft to stay under 5MB

## Network Restrictions

If OpenSky API is unreachable (firewall/proxy restrictions):

1. Script automatically falls back to sample data
2. Logs warning: "API failed, using sample data for this cycle"
3. Use `sample` mode explicitly for testing

## Dependencies

- Python 3.7+
- `requests` library (only external dependency)

Install:
```bash
pip3 install requests
```

## File Locations

```
/home/ubuntu/clawd/projects/atlas-intel/
├── feeds/
│   └── flight_tracker.py          # This script
└── dashboard/
    └── data/
        ├── flight_live.json        # Live aircraft positions
        └── flight_status.json      # Flight routes (backward compat)
```

## Systemd Service (Optional)

For production deployment as daemon:

```ini
[Unit]
Description=Atlas Intel Flight Tracker
After=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clawd/projects/atlas-intel
ExecStart=/usr/bin/python3 /home/ubuntu/clawd/projects/atlas-intel/feeds/flight_tracker.py continuous 15
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

## Logging

Logs to stdout with timestamps:

```
2026-03-23 22:55:56,404 [INFO] ============================================================
2026-03-23 22:55:56,404 [INFO] Atlas Intel Flight Tracker - Single Run
2026-03-23 22:55:56,405 [INFO] Processing 5234 aircraft states
2026-03-23 22:55:56,405 [INFO] Processed: 5234 total, 23 military
2026-03-23 22:55:56,406 [INFO] ✓ Wrote flight_live.json (2.1 MB)
2026-03-23 22:55:56,406 [INFO] ✓ Wrote flight_status.json
2026-03-23 22:55:56,406 [INFO]   Total aircraft: 5234
2026-03-23 22:55:56,406 [INFO]   Military: 23
2026-03-23 22:55:56,406 [INFO]   Anomalies: 8
```

## Performance

- **API Response Time**: 5-30 seconds (varies by OpenSky load)
- **Processing Time**: <1 second for 5000 aircraft
- **Output File Size**: 1-4 MB (flight_live.json), <100 KB (flight_status.json)
- **Memory Usage**: ~50-100 MB

## Known Limitations

1. **Routes are synthetic**: OpenSky doesn't provide flight plans, so destination is estimated from heading
2. **Aircraft type detection**: Limited to military callsign matching
3. **Helicopter detection**: No reliable method without external database
4. **Historical tracking**: Limited to last 50 positions per aircraft in memory

## Future Enhancements

- [ ] Integrate flight plan database for real routes
- [ ] Aircraft type database (ICAO type codes → names)
- [ ] Conflict zone geofencing
- [ ] Persistent history database
- [ ] Multiple API source fallback (ADS-B Exchange, etc.)
- [ ] Websocket streaming for real-time updates

## Troubleshooting

### OpenSky API not responding

**Symptom**: Timeout errors, "Failed to fetch aircraft data"

**Solutions**:
1. Check network connectivity: `curl -I https://opensky-network.org/api/states/all`
2. Verify no firewall blocking outbound HTTPS
3. Use sample mode for testing: `python3 flight_tracker.py sample`
4. Script auto-falls back to sample data in continuous mode

### Output files not updating

**Check**:
```bash
ls -lh /home/ubuntu/clawd/projects/atlas-intel/dashboard/data/flight*.json
cat /home/ubuntu/clawd/projects/atlas-intel/dashboard/data/flight_status.json
```

### JSON file too large

Script auto-trims commercial aircraft to stay under 5MB while keeping all military.

## Credits

- Data: OpenSky Network (https://opensky-network.org)
- Project: Atlas Intel (Palantir-style intelligence dashboard)
- Author: Atlas AI Assistant
- Date: 2026-03-23
