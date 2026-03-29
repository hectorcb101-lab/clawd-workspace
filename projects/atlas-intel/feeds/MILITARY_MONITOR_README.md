# Military Activity Monitor

Intelligence aggregation system for Atlas Intel dashboard that monitors and correlates military movements from multiple sources.

## Overview

The Military Activity Monitor aggregates:
- **Naval vessels** from vessel tracking data (AIS)
- **Military aircraft** from flight tracking data
- **Military events** from GDELT news API
- **Naval group detection** (vessels within 50km proximity)
- **Hotspot monitoring** for 8 strategic regions

## Output

Generates: `/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/military_live.json`

Current metrics:
- 104 military vessels tracked
- 4 military aircraft tracked
- 25 naval groups detected
- 1 active hotspot (Baltic Sea)
- ~29KB JSON output (well under 2MB limit)

## Usage

### Single Run
```bash
python3 military_monitor.py
```

### Continuous Monitoring (daemon mode)
```bash
python3 military_monitor.py --continuous 60
```

Where `60` is the interval in seconds (default: 60).

## Detection Methods

### Military Vessels
- **MMSI ranges**: 369970000-369999999 (US), 002000000-009999999 (various navies)
- **Name patterns**: USS, HMS, INS, RFS, PLAN, warship, destroyer, carrier, patrol, etc.
- **Type classification**: Automatically classifies as carrier, destroyer, cruiser, frigate, etc.

### Naval Groups
- Detects vessels within 50km of each other
- Identifies carrier strike groups (when carrier + escorts detected)
- Calculates center point and average heading

### Hotspots (8 regions monitored)
1. South China Sea — Spratly Islands
2. Taiwan Strait
3. Black Sea — Crimea
4. Persian Gulf — Strait of Hormuz
5. Red Sea — Bab-el-Mandeb
6. Baltic Sea — Kaliningrad
7. Korean Peninsula — DMZ Waters
8. Arctic — Northern Sea Route

### Threat Level Assessment
- **normal**: 1-2 assets, no recent events
- **notable**: 3-5 assets
- **elevated**: 6-10 assets or 2+ recent events
- **critical**: 10+ assets or high-severity events

## Data Sources

1. **Vessel tracking**: `/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/vessel_live.json`
2. **Flight tracking**: `/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/flight_live.json`
3. **GDELT API**: https://api.gdeltproject.org/api/v2/doc/doc
   - Query: `military OR naval OR troops OR deployment OR warship`
   - Timespan: 24h
   - Max records: 50

## Known Vessel Database

Includes reference data for major military vessels:
- **US**: 10 carriers (Ford, Nimitz-class), cruisers, destroyers
- **Russia**: Admiral Kuznetsov, Slava-class cruisers, Gorshkov-class frigates
- **China**: Liaoning, Shandong, Fujian carriers + Type 055 destroyers
- **UK**: HMS Queen Elizabeth, HMS Prince of Wales, Type 45 destroyers

## Dependencies

- Python 3 (stdlib only)
- `requests` library (for GDELT API)

## Error Handling

- Gracefully handles missing input files (vessel/flight data)
- GDELT API rate limiting handled with retry on next cycle
- Vessel data type conversion (MMSI as integer → string)
- Invalid coordinates filtered out

## Notes

- GDELT API may rate-limit; events will be empty until limit resets
- Vessel detection relies on name/MMSI patterns; may have false positives
- Geographic regions use simple lat/lon boundary checks
- Event geolocation uses keyword matching (approximate)
