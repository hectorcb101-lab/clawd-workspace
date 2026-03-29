# Atlas Intel Static Data Extraction - Complete

**Date:** 2026-03-23  
**Source:** `/tmp/worldmonitor/src/config/` + `/tmp/worldmonitor/shared/`  
**Destination:** `/home/ubuntu/clawd/projects/atlas-intel/dashboard/data/`

## ✅ All 7 Files Created & Validated

### 1. military_bases.json
- **210 military bases** from bases-expanded.ts
- Covers: US-NATO (112), UK (38), Russia (17), India (13), France (12), China (8), Italy (5), UAE (4), Japan (1)
- 68 countries represented
- Fields: id, name, lat, lon, type, country, arm, status

### 2. pipelines.json
- **17 major pipelines** (12 oil, 5 gas)
- Major routes: Keystone, Druzhba, BTC, ESPO, TurkStream, Yamal-Europe
- Fields: id, name, type, status, points (coordinates), capacity, length, operator, countries

### 3. trade_routes.json
- **21 global trade routes** (13 container, 7 energy, 1 bulk)
- Key routes: China-Europe (Suez), Gulf-Asia oil, Qatar LNG, TransAtlantic
- Fields: id, name, from, to, category, status, volume, waypoints

### 4. airports.json
- **30 major international airports**
- Coverage: Americas (9), Europe (5), APAC (7), MENA (7), Africa (2)
- Fields: iata, icao, name, city, country, lat, lon, region

### 5. military_callsigns.json
- **11 US military callsign patterns** (REACH, SAM, FORTE, RAPTOR, etc.)
- **6 NATO/Allied patterns** (RAF, NATO, FAF, GAF, IAF)
- **7 ICAO hex ranges** for aircraft identification
- **4 military hotspots** (INDO-PACIFIC, CENTCOM, EUCOM, ARCTIC)
- **2 query regions** for tracking
- Fields: pattern, operator, aircraft_type, description, hex ranges, hotspots

### 6. nuclear_sites.json
- **5 nuclear sites** (Natanz, Fordow, Bushehr, Dimona, Yongbyon)
- **18 gamma irradiator facilities** (sample from 124 total)
- Fields: name/city, country, lat, lon, type, status

### 7. commodities_data.json
- **12 commodities** (Gold, Oil, Gas, VIX, etc.)
- **16 stocks** (SPX, AAPL, MSFT, NVDA, Nifty, Sensex, etc.)
- **4 ETFs** (Bitcoin spot ETFs: IBIT, FBTC, ARKB, GBTC)
- **2 crypto** (BTC, ETH)
- Fields: symbol/ticker, name, display, issuer

## Validation Results

All files pass JSON validation:
```
✓ military_bases.json is valid JSON
✓ pipelines.json is valid JSON
✓ trade_routes.json is valid JSON
✓ airports.json is valid JSON
✓ military_callsigns.json is valid JSON
✓ nuclear_sites.json is valid JSON
✓ commodities_data.json is valid JSON
```

## Notes

- This is **pure data extraction** — no Python scripts, only JSON
- All coordinates use decimal degrees (lat, lon)
- Status fields preserved from source (active, controversial, planned, operating)
- Pipeline points are coordinate arrays for map rendering
- Trade routes reference waypoints by ID (not expanded coordinates)
- Military callsign patterns are regex-compatible strings
- No files outside `dashboard/data/` were modified

## Next Steps (For Atlas Intel Dashboard)

These JSON files can now be:
1. Imported directly into the dashboard frontend
2. Used for map layer rendering (Leaflet/Mapbox)
3. Referenced for filtering and search
4. Updated independently from live data feeds

---

**Task Status:** COMPLETE ✅  
**All 7 JSON files exist in dashboard/data/ and are valid.**
