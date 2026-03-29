# World Monitor Intelligence Extract: Natural Disasters & Infrastructure

**Crawl Date:** 2026-03-23  
**Source:** World Monitor Documentation  
**Focus:** Free data sources, algorithms, features for Atlas Intel replication

---

## Executive Summary

World Monitor combines multiple authoritative data sources (GDACS, NASA EONET, USGS, NGA, ACLED, GDELT, OpenSky, AIS) with intelligent correlation algorithms to provide real-time disaster monitoring, infrastructure cascade analysis, and multi-source convergence detection. Most core data sources are **FREE** and publicly accessible.

---

## 1. Natural Disaster Tracking

### 1.1 Data Sources (FREE)

#### GDACS (Global Disaster Alert and Coordination System)
- **What:** UN-backed disaster alert system with official severity assessments
- **API/Access:** https://gdacs.org/ (free API available)
- **Coverage:** Global
- **Update Frequency:** Real-time
- **Data Types:**

| Event Type | Code | Sources | Detection Method |
|------------|------|---------|------------------|
| Earthquake | EQ | USGS, EMSC | Seismograph network |
| Flood | FL | Satellite imagery | MODIS, VIIRS, SAR |
| Tropical Cyclone | TC | NOAA, JMA | Satellite + weather models |
| Volcano | VO | Smithsonian GVP | Thermal + SO2 emissions |
| Wildfire | WF | MODIS, VIIRS | Thermal anomalies |
| Drought | DR | Multiple | Precipitation + soil moisture |

**Alert Levels:**
- **Red (Critical):** Significant humanitarian impact expected
- **Orange (Alert):** Moderate impact, monitoring required
- **Green (Advisory):** Minor event, localized impact

#### NASA EONET (Earth Observatory Natural Event Tracker)
- **What:** Near-real-time natural event detection from satellite observation
- **API:** https://eonet.gsfc.nasa.gov/api/v3/events (FREE, no key required)
- **Coverage:** Global
- **Update Frequency:** Varies by event type (see table below)

| Category | Detection Method | Typical Delay | Update Frequency |
|----------|------------------|---------------|------------------|
| Severe Storms | GOES/Himawari imagery | Minutes | Real-time |
| Wildfires | MODIS thermal anomalies | 4-6 hours | 4-6 hours |
| Volcanoes | Thermal + SO2 emissions | Hours | Hourly |
| Floods | SAR imagery + gauges | Hours to days | Daily |
| Sea/Lake Ice | Passive microwave | Daily | Daily |
| Dust/Haze | Aerosol optical depth | Hours | Hourly |

**Data Format:** JSON with geometry (point/polygon), timestamp, sources, categories

#### USGS Earthquake Feeds
- **API:** https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php (FREE)
- **Update Frequency:** Real-time (1-2 minute latency)
- **Thresholds Used:** M4.5+ globally, lower threshold for populated areas
- **Data Format:** GeoJSON with magnitude, depth, location, time

### 1.2 Algorithms: Multi-Source Deduplication

**Problem:** GDACS and EONET often report the same event

**Solution:** Spatial-temporal clustering
```
IF (distance < 100km) AND (time_delta < 48 hours) THEN
  - Merge as single event
  - GDACS severity takes precedence (human-verified)
  - EONET geometry provides more precise coordinates
  - Show both source attributions
END
```

**Implementation Notes:**
- Use Haversine distance for geographic proximity
- Maintain source provenance in merged records
- Priority: human verification > automated detection

### 1.3 Filtering Logic (Anti-Noise)

**Wildfires:**
- Only events < 48 hours old
- **Rationale:** Older fires are either contained or well-known

**Earthquakes:**
- M4.5+ globally
- Lower threshold for populated areas (can use population density data)

**Storms:**
- Only named storms OR those with active warnings
- Filters out tropical disturbances that don't develop

**Implementation:** Time-based TTL + magnitude/severity thresholds

---

## 2. Infrastructure Cascade Analysis

### 2.1 Dependency Graph Model

**Node Types (350 total):**

| Type | Count | Examples |
|------|-------|----------|
| Undersea Cables | 86 | MAREA, FLAG Europe-Asia, SEA-ME-WE 6 |
| Pipelines | 88 | Nord Stream, Trans-Siberian, Keystone |
| Ports | 62 | Singapore, Rotterdam, Shenzhen |
| Chokepoints | 9 | Suez, Hormuz, Malacca, Gibraltar, Bosphorus |
| Countries | 105 | End nodes representing national impact |

**Data Sources:**
- **Submarine Cable Map:** https://www.submarinecablemap.com/ (FREE, API available)
- **TeleGeography:** https://github.com/telegeography/www.submarinecablemap.com (FREE, open data)
- **Pipeline data:** Public infrastructure databases (OpenStreetMap, government disclosures)

### 2.2 Cascade Calculation Algorithm

**Breadth-First Propagation:**
```
1. Start at source node (e.g., "cable:marea")
2. For each dependent node:
   impact = edge_strength × disruption_level × (1 - redundancy)
3. Categorize impact:
   - Critical: impact > 0.8
   - High: impact > 0.5
   - Medium: impact > 0.2
   - Low: impact ≤ 0.2
4. Recurse to depth 3 (prevent infinite loops)
```

**Key Parameters:**
- **edge_strength:** Dependency weight (0-1, based on traffic share)
- **disruption_level:** Severity of incident (0-1)
- **redundancy:** Availability of alternative routes (0-1)

**Output Example:**
```
MAREA Cable Disruption:
Source: MAREA (US ↔ Spain, 200 Tbps)
Countries Affected: 4
- Spain: Medium (redundancy via other Atlantic cables)
- Portugal: Low (secondary landing)
- France: Low (alternative routes via UK)
- US: Low (high redundancy)
Alternative Routes: TAT-14 (35%), Hibernia (22%), AEConnect (18%)
```

### 2.3 Redundancy Modeling

**Redundancy Score Calculation:**
```
redundancy = 1 - (primary_capacity / total_capacity)

Where:
- primary_capacity = capacity of disrupted route
- total_capacity = sum of all routes serving the same endpoints
```

**Alternative Route Discovery:**
- Graph traversal to find paths between same endpoints
- Capacity percentage = route_capacity / sum(all_alternative_capacities)

### 2.4 Undersea Cable Activity Monitoring

#### Data Sources (FREE)

**NGA (National Geospatial-Intelligence Agency) Maritime Warnings:**
- **Access:** https://msi.nga.mil/NavWarnings (FREE, public)
- **Coverage:** Global (NAVAREA I-XXI)
- **Update Frequency:** Real-time (when issued)
- **Data Type:** NAVAREA warnings with coordinates, cable operations, repair ships

#### Detection Algorithm

**Keyword Filtering:**
```python
cable_keywords = [
    "CABLE", "CABLESHIP", "SUBMARINE CABLE", 
    "FIBER OPTIC", "CABLE REPAIR"
]

fault_keywords = [
    "FAULT", "BREAK", "DAMAGE", "OUTAGE"
]

# Parse NGA warnings
for warning in nga_warnings:
    if any(keyword in warning.text for keyword in cable_keywords):
        coords = parse_coordinates(warning.text)  # DMS or decimal
        cable = match_nearest_cable(coords, radius=5_degrees)
        
        severity = "FAULT" if any(k in warning.text for k in fault_keywords) else "MAINTENANCE"
        
        emit_alert(cable, coords, severity, warning)
```

**Coordinate Parsing:**
- Supports DMS (degrees-minutes-seconds) and decimal formats
- Match to nearest cable route within 5° radius

**Alert Types:**

| Type | Trigger | Map Display |
|------|---------|-------------|
| Cable Advisory | Cable-related NAVAREA warning | Yellow marker |
| Repair Ship | Cableship name detected | Ship icon with status |

**Repair Ship Extraction:**
```
Known cableships: CS Reliance, Cable Innovator, CS Sovereign, etc.
Extract: Vessel name, Status (en route/on station), Location, Associated cable
```

---

## 3. Geographic Convergence Detection

### 3.1 Algorithm Overview

**Concept:** When 3+ independent data streams converge on the same geographic area within 24 hours, it signals a significant event.

**Grid Resolution:** 1° × 1° cells (approximately 111km × 111km at equator)

### 3.2 Event Types Tracked

| Event Type | Source | Detection Method |
|------------|--------|------------------|
| Protests | ACLED/GDELT | Direct geolocation |
| Military Flights | OpenSky | ADS-B position |
| Naval Vessels | AIS stream | Ship position |
| Earthquakes | USGS | Epicenter location |

**Data Sources (FREE):**
- **ACLED:** https://acleddata.com/ (FREE with registration)
- **GDELT:** https://www.gdeltproject.org/ (FREE, no key)
- **OpenSky:** https://opensky-network.org/apidoc/ (FREE, rate-limited)
- **AIS:** https://www.aishub.net/ or MarineTraffic (FREE tier available)
- **USGS:** https://earthquake.usgs.gov/earthquakes/feed/ (FREE)

### 3.3 Convergence Scoring

**Formula:**
```
type_score = event_types × 25      # Max 100 (4 types)
count_boost = min(25, total_events × 2)
convergence_score = min(100, type_score + count_boost)
```

**Alert Thresholds:**

| Types Converging | Score Range | Alert Level |
|------------------|-------------|-------------|
| 4 types | 80-100 | Critical |
| 3 types (high count) | 60-80 | High |
| 3 types (low count) | 40-60 | Medium |

**Example:**
```
Taiwan Strait Buildup:
Cell: 25°N, 121°E
Events: Military flights (3), Naval vessels (2), Protests (1)
Score: 75 + 12 = 87 (Critical)
Signal: "Geographic Convergence (3 types) - military flights, naval vessels, protests"
```

### 3.4 Implementation Notes

**Grid Cell Indexing:**
```python
def get_cell(lat, lon):
    return (floor(lat), floor(lon))

# Maintain dict of cells with event counts
cells = defaultdict(lambda: {
    'protests': 0,
    'military_flights': 0,
    'naval_vessels': 0,
    'earthquakes': 0,
    'timestamp': None
})
```

**Time Window:** 24 hours (events older than 24h removed from cell counts)

---

## 4. Signal Intelligence & Correlation

### 4.1 News Source Ranking

**Tier System (Authority-Based):**

| Tier | Sources | Characteristics |
|------|---------|-----------------|
| Tier 1 | Reuters, AP, AFP, Bloomberg, White House, Pentagon | Wire services + official government |
| Tier 2 | BBC, Guardian, NPR, Al Jazeera, CNBC, Financial Times | Major outlets, high editorial standards |
| Tier 3 | Defense One, Bellingcat, Foreign Policy, MIT Tech Review | Domain specialists |
| Tier 4 | Hacker News, The Verge, VentureBeat | Aggregators, tech media |

**Implementation:** When multiple sources report same story, display lowest tier (most authoritative) as primary.

### 4.2 Source Type Classification (Triangulation)

**Categories:**
- **Wire:** Reuters, AP, AFP, Bloomberg
- **Gov:** White House, Pentagon, State Dept, Fed, SEC
- **Intel:** Defense One, Bellingcat, Krebs
- **Mainstream:** BBC, Guardian, NPR, Al Jazeera
- **Market:** CNBC, MarketWatch, Financial Times
- **Tech:** Hacker News, Ars Technica, MIT Tech Review

**Triangulation Signal:**
Triggered when Wire + Gov + Intel sources all report the same event within 30 minutes.
**Confidence:** 95% (gold standard for breaking news)

### 4.3 Propaganda Risk Indicators

**High Risk (State Media):**
- Xinhua (China), TASS (Russia), RT (Russia), CGTN (China), PressTV (Iran)

**Medium Risk (State-Funded):**
- Al Jazeera (Qatar), TRT World (Turkey)

**Display:** Visual badges (⚠ State Media, ! Caution) next to source names

**Rationale:** Include state media for signal value (reveals government priorities), but flag for context.

### 4.4 Signal Types & Detection

**12 Distinct Signal Types:**

#### News Signals

**◉ Convergence**
- **Trigger:** 3+ source types report same story within 30 minutes
- **Algorithm:** 
  ```
  IF unique_source_types >= 3 AND max_time_delta <= 30_minutes THEN
    emit("Convergence", confidence=85%)
  ```

**△ Triangulation**
- **Trigger:** Wire + Gov + Intel sources align
- **Confidence:** 95%

**🔥 Velocity Spike**
- **Trigger:** Topic mention rate doubles with 6+ sources/hour
- **Algorithm:**
  ```
  current_rate = mentions_last_hour / 1
  baseline_rate = mentions_previous_24h / 24
  
  IF (current_rate >= 2 × baseline_rate) AND (sources_count >= 6) THEN
    emit("Velocity Spike", confidence=80%)
  ```

#### Market Signals

**🔮 Prediction Leading**
- **Trigger:** Prediction market moves 5%+ with low news coverage
- **Data Source:** Polymarket API (FREE), Manifold Markets
- **Algorithm:**
  ```
  IF (market_move >= 0.05) AND (news_velocity < threshold) THEN
    emit("Prediction Leading", confidence=70%)
  ```

**📰 News Leads Markets**
- **Trigger:** High news velocity without corresponding market move
- **Algorithm:**
  ```
  IF (news_velocity > threshold) AND (market_move < 0.02) THEN
    emit("News Leads Markets", confidence=65%)
  ```

**✓ Market Move Explained**
- **Trigger:** Market moves 2%+ with correlated news coverage
- **Algorithm:** Entity correlation (see below)

**📊 Silent Divergence**
- **Trigger:** Market moves 2%+ with NO correlated news after entity search
- **Signal:** Possible insider knowledge or algorithm-driven

**📈 Sector Cascade**
- **Trigger:** Multiple related sectors moving in same direction
- **Algorithm:**
  ```
  sector_moves = {sector: price_change for sector in sectors}
  correlated = [s for s in sectors if correlation(s, target_sector) > 0.7]
  
  IF len(correlated) >= 3 AND all_same_direction THEN
    emit("Sector Cascade")
  ```

#### Infrastructure Signals

**🛢 Flow Drop**
- **Trigger:** Pipeline flow disruption keywords detected
- **Keywords:** pipeline explosion, pipeline leak, pipeline attack, gas flow, supply disruption

**🔁 Flow-Price Divergence**
- **Trigger:** Pipeline disruption news without corresponding oil price move
- **Algorithm:**
  ```
  IF (flow_drop_detected) AND (oil_price_change < $1.50) THEN
    emit("Flow-Price Divergence", confidence=75%)
  ```

#### Geopolitical Signals

**🌍 Geographic Convergence**
- **Trigger:** 3+ event types in same 1°×1° grid cell
- **See section 3.3 for full algorithm**

**🔺 Hotspot Escalation**
- **Trigger:** Multi-component score exceeds threshold with rising trend
- **Components:** News velocity, CII (Civil Instability Index), convergence, military activity

**✈ Military Surge**
- **Trigger:** Transport/fighter activity 2× baseline in theater
- **Data Source:** OpenSky ADS-B (FREE)

### 4.5 Entity-Aware Correlation

**Entity Knowledge Base:**
- **Size:** 66 entities (companies, countries, commodities, crypto)
- **Types:** company (38), index (3), sector (5), commodity (6), crypto (3), country (11)

**Entity Structure:**
```json
{
  "id": "NVDA",
  "name": "Nvidia",
  "type": "company",
  "sector": "semiconductors",
  "aliases": ["nvidia", "nvda", "jensen huang"],
  "keywords": ["H100", "A100", "CUDA", "AI chips"],
  "related": ["AVGO", "TSM", "ASML"],
  "country": "US"
}
```

**Matching Algorithm:**
```
1. Market move detected (e.g., AVGO +2.5%)
2. Entity lookup: AVGO → broadcom
3. Build search terms: 
   - Aliases: ["Broadcom", "AVGO"]
   - Keywords: ["AI chips", "semiconductors", "VMware"]
   - Related: ["nvidia", "intel", "amd"]
4. Scan all news clusters for matches
5. Score confidence:
   - Alias match (exact name): 95%
   - Keyword match (topic): 70%
   - Related entity match: 60%
6. Result: "Market Move Explained" or "Silent Divergence"
```

### 4.6 Signal Deduplication

**TTL (Time-to-Live) by Signal Type:**

| Signal Type | TTL | Rationale |
|-------------|-----|-----------|
| Silent Divergence | 6 hours | Market moves persist |
| Flow-Price Divergence | 6 hours | Energy events unfold slowly |
| Explained Market Move | 6 hours | Same correlation shouldn't repeat |
| Prediction Leading | 2 hours | Prediction markets update frequently |
| Other signals | 30 minutes | Default for fast-moving events |

**Deduplication Keys:**
- Market signals: Use symbol-only (e.g., `silent_divergence:AVGO`)
- News signals: Use topic hash
- Geographic signals: Use cell coordinates

---

## 5. Implementation Roadmap for Atlas Intel

### 5.1 Immediate (Phase 1) - FREE APIs Only

**Natural Disasters:**
- [ ] Integrate NASA EONET API (https://eonet.gsfc.nasa.gov/api/v3/events)
- [ ] Integrate USGS Earthquake Feed (https://earthquake.usgs.gov/earthquakes/feed/)
- [ ] Implement spatial-temporal deduplication (100km, 48hr)
- [ ] Apply filtering logic (wildfires < 48h, earthquakes M4.5+)

**Infrastructure:**
- [ ] Pull submarine cable data from TeleGeography GitHub
- [ ] Build dependency graph (cables → countries)
- [ ] Implement cascade calculation algorithm
- [ ] Monitor NGA maritime warnings for cable advisories

**Convergence:**
- [ ] Integrate ACLED (FREE with registration)
- [ ] Integrate GDELT (FREE, no key)
- [ ] Implement 1°×1° grid cell tracking
- [ ] Calculate convergence scores

**Signals:**
- [ ] Build entity knowledge base (start with top 20 companies)
- [ ] Implement news velocity spike detection
- [ ] Add source tier ranking system

### 5.2 Short-Term (Phase 2) - Enhanced Features

**Advanced Correlation:**
- [ ] Entity-aware market-news correlation
- [ ] Triangulation detection (Wire + Gov + Intel)
- [ ] Flow-price divergence for energy

**Geopolitical:**
- [ ] Military flight tracking (OpenSky FREE tier)
- [ ] Hotspot escalation scoring
- [ ] Regional convergence alerts

### 5.3 Future (Phase 3) - Paid APIs & Advanced Features

**Consider if budget allows:**
- GDACS API (may have premium tier)
- Enhanced AIS coverage (MarineTraffic premium)
- Prediction market APIs (Polymarket, Kalshi)

---

## 6. Key Learnings & Design Patterns

### 6.1 Multi-Source Deduplication Pattern

**Best Practice:** When combining multiple authoritative sources:
1. Use spatial-temporal clustering (distance + time window)
2. Maintain source provenance (show all sources)
3. Priority hierarchy: human-verified > automated detection
4. Geometry from most precise source

### 6.2 Signal Confidence Scoring

**Components:**
- Match quality (95% exact, 70% keyword, 60% related)
- Source tier (Tier 1 > Tier 2 > Tier 3)
- Correlation strength (multiple sources > single source)
- Time freshness (recent > stale)

### 6.3 Anti-Noise Filtering

**Strategies:**
- Time-based TTL (wildfires < 48h)
- Magnitude thresholds (earthquakes M4.5+)
- Named events only (storms)
- Deduplication with type-specific TTL

### 6.4 Cascade Modeling

**Formula:**
```
impact = edge_strength × disruption_level × (1 - redundancy)
```

**Key insight:** Redundancy is critical for realistic impact assessment.

---

## 7. Data Source Quick Reference

### FREE APIs (No Key Required)
- NASA EONET: https://eonet.gsfc.nasa.gov/api/v3/events
- USGS Earthquakes: https://earthquake.usgs.gov/earthquakes/feed/
- GDELT: https://www.gdeltproject.org/
- NGA Maritime Warnings: https://msi.nga.mil/NavWarnings
- TeleGeography Cable Map: https://github.com/telegeography/www.submarinecablemap.com

### FREE APIs (Registration Required)
- ACLED: https://acleddata.com/
- OpenSky: https://opensky-network.org/apidoc/
- AIS Hub: https://www.aishub.net/

### Potential Paid (Note for Alternatives)
- GDACS: Verify if premium tier exists
- Enhanced AIS: MarineTraffic, VesselFinder
- Prediction Markets: Polymarket (FREE for reads, paid for trades)

---

## 8. Algorithms Summary

### Spatial-Temporal Clustering
```python
def is_duplicate(event1, event2):
    distance = haversine(event1.coords, event2.coords)
    time_delta = abs(event1.timestamp - event2.timestamp)
    return distance < 100_km and time_delta < 48_hours
```

### Convergence Scoring
```python
type_score = len(event_types) * 25
count_boost = min(25, total_events * 2)
convergence_score = min(100, type_score + count_boost)
```

### Cascade Impact
```python
def calculate_impact(edge_strength, disruption_level, redundancy):
    return edge_strength * disruption_level * (1 - redundancy)
```

### Velocity Spike
```python
current_rate = mentions_last_hour
baseline_rate = mentions_previous_24h / 24
if current_rate >= 2 * baseline_rate and sources >= 6:
    emit_signal("Velocity Spike")
```

### Entity Correlation
```python
def correlate_market_news(symbol, news_clusters):
    entity = lookup_entity(symbol)
    search_terms = entity.aliases + entity.keywords + entity.related
    
    for cluster in news_clusters:
        for term in search_terms:
            if term in cluster.headline.lower():
                return ("Explained", cluster, confidence_score(term))
    
    return ("Silent Divergence", None, 0)
```

---

## 9. Next Steps for Atlas Intel

1. **Set up data pipelines** for NASA EONET, USGS, GDELT (all FREE)
2. **Build grid cell tracker** for geographic convergence
3. **Implement entity knowledge base** (start small, expand iteratively)
4. **Create signal detection engine** with deduplication logic
5. **Design dashboard UI** showing convergence zones, cascade impacts, signal alerts

**Estimated Development Time (Phase 1):** 2-3 weeks for core features with FREE APIs.

---

**End of Report**
