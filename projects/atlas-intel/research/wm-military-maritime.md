# World Monitor Intelligence Extraction Report
**Military Tracking, Maritime Intelligence, Orbital Surveillance & Hotspots**

Generated: 2026-03-23  
Purpose: Extract data sources, APIs, algorithms, and features for Atlas Intel dashboard replication  
Focus: **FREE APIs only** — paid alternatives noted where applicable

---

## Executive Summary

World Monitor uses a multi-layered intelligence approach combining:
- **AIS maritime tracking** via AISStream (WebSocket, requires API key)
- **Aircraft tracking** via OpenSky Network (FREE with registration)
- **Satellite orbital surveillance** via CelesTrak TLEs (FREE, public NORAD data)
- **News correlation** for activity scoring (RSS feeds, public)
- **Geospatial analysis** with custom algorithms for surge detection, chokepoint monitoring, and hotspot scoring

All core data sources have FREE tiers suitable for prototype implementation.

---

## 1. FREE Data Sources & APIs

### 1.1 Aircraft Tracking (Military Aviation)

**OpenSky Network**  
- **URL**: https://opensky-network.org  
- **Cost**: FREE with registration  
- **Auth**: OAuth2 client credentials flow  
- **API Endpoints**:
  - Account registration: Free account at opensky-network.org
  - Create API client in account settings → `OPENSKY_CLIENT_ID` + `OPENSKY_CLIENT_SECRET`
  - OAuth2 flow for Bearer tokens (30-min expiry, cached)
  
- **What You Get**:
  - ADS-B transponder data (position, altitude, speed, heading)
  - ICAO hex codes (aircraft identifier)
  - Callsigns (e.g., RCH, REACH, DUKE, VIPER)
  - Real-time position updates
  - 20-point position history over 5-minute windows

- **Limitations**:
  - **Blocks cloud provider IPs** (Vercel, Railway, AWS) — requires relay server with credentials
  - No classified military aircraft (no public transponders)
  - Coverage depends on ground receiver network (excellent in Europe/US, patchy elsewhere)

- **Implementation Note**: World Monitor uses a Railway relay server to proxy requests with credentials. Alternative: VPS with residential IP for direct API access.

---

### 1.2 Maritime Tracking (AIS)

**AISStream**  
- **URL**: Not directly specified, but World Monitor uses WebSocket relay  
- **Cost**: API key required (pricing not stated — **needs investigation**)  
- **Protocol**: WebSocket for real-time vessel position streaming  
- **What You Get**:
  - MMSI (Maritime Mobile Service Identity) numbers
  - Vessel names, positions (lat/lng)
  - Ship type codes (cargo, tanker, military, etc.)
  - Callsigns
  - Real-time position updates via WebSocket

- **Alternative FREE Options** (not used by World Monitor, but viable):
  - **MarineTraffic API** (limited free tier)
  - **VesselFinder API** (limited free tier)
  - **AIS data from public receivers** (requires hardware/access)

- **Relay Architecture**: World Monitor uses Railway relay to avoid cloud IP blocks:
  ```
  Browser → Railway Relay (Node.js) → AISStream WebSocket → Browser
  ```

---

### 1.3 Satellite Tracking (Orbital Surveillance)

**CelesTrak TLEs (Two-Line Element Sets)**  
- **URL**: https://celestrak.org  
- **Cost**: **100% FREE** — public NORAD orbital data  
- **Update Frequency**: Every 2 hours  
- **Groups Fetched**:
  - `military` group (~21 satellites)
  - `resource` group (~164 satellites)
  - After filtering: 80-120 intelligence-relevant satellites

- **What You Get**:
  - Two-Line Element Sets (TLE format) for orbital propagation
  - Satellite name, NORAD ID, orbital parameters
  - Epoch time (TLE generation timestamp)

- **Client-Side Propagation**:
  - Uses `satellite.js` library (v6) for SGP4/SDP4 orbital math
  - Propagate position every 3 seconds client-side (zero server cost)
  - 15-point orbit trails (1 per minute, looking back 15 minutes)

- **Tracked Satellites**:
  - **Chinese recon**: YAOGAN, GAOFEN, JILIN (SAR + Optical)
  - **Russian recon**: COSMOS 24xx/25xx (Military)
  - **Commercial SAR**: COSMO-SKYMED, TERRASAR, PAZ, SAR-LUPE, ICEYE
  - **Commercial optical**: WORLDVIEW, SKYSAT, PLEIADES, KOMPSAT
  - **EU/civil**: SENTINEL (SAR: Sentinel-1, Optical: Sentinel-2)
  - **Military**: SAPPHIRE, PRAETORIAN

- **Propagation Algorithm**:
  ```
  1. Parse TLEs into SatRec objects (cached until TLEs refresh)
  2. For each satellite: propagate() → eciToGeodetic() → lat/lng/alt
  3. Run every 3 seconds via setInterval (LEO satellites move ~23km in 3s)
  ```

- **Cost Breakdown**:
  - CelesTrak API: **FREE**
  - Client-side SGP4 propagation: **FREE** (browser CPU)
  - Server-side: Redis cache (single key, ~50KB, 4h TTL) — negligible cost

---

### 1.4 News Feeds (RSS)

**World Monitor Approach**: Scrapes RSS feeds from public news sources  
- **Relay Required**: Some RSS feeds block cloud IPs (uses Railway relay with user-agent spoofing)
- **Feeds Used**: Not enumerated in docs, but likely:
  - Al Jazeera, BBC, Reuters, AP, local/regional news
  - Defense/military-focused outlets (Defense News, Jane's, etc.)

**Implementation for Atlas Intel**:
- **NewsAPI.org** (FREE tier: 100 requests/day, 1-month archive)
- **RSS feeds** (direct scraping where allowed)
- **Google News RSS** (free, no API key required)

---

### 1.5 Chokepoint Traffic Data

**IMF PortWatch**  
- **URL**: https://portwatch.imf.org  
- **Cost**: **FREE** — public IMF data  
- **What You Get**:
  - Weekly vessel transit counts per chokepoint
  - Tanker vs. cargo breakdowns
  - 180-day historical time series

**AISStream (real-time counter)**  
- Same as maritime tracking above
- 24-hour crossing counter per chokepoint

**CorridorRisk**  
- Risk intelligence (not detailed in docs — **needs investigation**)

---

### 1.6 Space Launch Infrastructure

**CelesTrak (launch sites)**  
- **URL**: https://celestrak.org  
- **Cost**: **FREE**  
- **What You Get**:
  - Launch facility locations (Kennedy, Vandenberg, Baikonur, Jiuquan, etc.)
  - Operator info (NASA, SpaceX, Roscosmos, CNSA, ESA, etc.)
  - Activity levels (manually curated in World Monitor docs)

---

## 2. Algorithms & Detection Logic

### 2.1 Military Surge Detection

**Purpose**: Detect significant increases in military aircraft activity above normal baselines.

**Theater Classification** (5 theaters for surge analysis):
- Middle East (Persian Gulf, Levant)
- Eastern Europe (Ukraine, Baltics, Black Sea)
- Western Europe (Central Europe, North Sea)
- Pacific (East Asia, Southeast Asia)
- Horn of Africa (Red Sea, East Africa)

**Aircraft Classification** (callsign pattern matching):

| Type            | Callsign Patterns                      | Significance               |
|-----------------|----------------------------------------|----------------------------|
| **Transport**   | RCH, REACH, MOOSE, HERKY, EVAC, DUSTOFF | Airlift, troop movement    |
| **Fighter**     | VIPER, EAGLE, RAPTOR, STRIKE           | Combat air patrol          |
| **Reconnaissance** | SIGNT, COBRA, RIVET, JSTARS          | Intelligence gathering     |

**Baseline Calculation**:
- Rolling 48-hour activity baseline per theater
- Minimum 6 data samples required
- Default baselines when data insufficient: 3 transport, 2 fighter, 1 recon
- Activity below 50% of baseline = stand-down

**Surge Detection Algorithm**:
```python
surge_ratio = current_count / baseline
surge_triggered = (
    ratio >= 2.0 AND
    transport >= 5 AND
    fighters >= 4
)
```

**Surge Severity Levels**:
- **Critical**: 4x baseline or higher (major deployment)
- **High**: 3x baseline (significant increase)
- **Medium**: 2x baseline (elevated activity)

**Signal Output** (`military_surge`):
- Location: Theater centroid coordinates
- Message: "Military Transport Surge in [Theater]: [X] aircraft (baseline: [Y])"
- Details: Aircraft types, nearby bases (150km radius), top callsigns
- Confidence: 0.6-0.9 based on surge ratio

---

### 2.2 Foreign Military Presence Detection

**Purpose**: Detect military aircraft from one nation appearing in geopolitically sensitive regions outside normal operating range.

**Sensitive Regions** (18 tracked):

| Region                   | Sensitivity | Monitored For                    |
|--------------------------|-------------|----------------------------------|
| **Taiwan Strait**        | Critical    | PLAAF activity, US transits      |
| **Persian Gulf**         | Critical    | Iranian, US, Gulf state activity |
| **Baltic Sea**           | High        | Russian activity near NATO       |
| **Black Sea**            | High        | NATO recon, Russian activity     |
| **South China Sea**      | High        | PLAAF patrols, US FONOPs         |
| **Korean Peninsula**     | High        | DPRK activity, US-ROK exercises  |
| **Eastern Mediterranean**| Medium      | Russian naval aviation, NATO     |
| **Arctic**               | Medium      | Russian bomber patrols           |

**Detection Logic**:
1. Identify all military aircraft within region boundary
2. Group aircraft by operating nation
3. Exclude "home region" operators (e.g., Russian VKS in Baltic excluded from alert)
4. Apply concentration thresholds (typically 2-3 aircraft per operator)

**Critical Combinations** (trigger critical severity):
- PLAAF in Taiwan Strait (potential invasion rehearsal)
- Russian VKS in Arctic (nuclear bomber patrols)
- USAF in Persian Gulf (potential strike package)

**Signal Output** (`foreign_military_presence`):
- Title: "Foreign Military Presence: [Region]"
- Details: "[Operator] aircraft detected: [count] [types]"
- Severity: Critical/High/Medium based on combination
- Confidence: 0.7-0.95 based on aircraft count and type diversity

---

### 2.3 Strike Capability Assessment

**Purpose**: Assess whether forces in a theater constitute an offensive strike package (combination of assets required for sustained combat).

**Strike-Capable Criteria**:
- Aerial refueling tankers (KC-135, KC-10, A330 MRTT)
- Airborne command and control (E-3 AWACS, E-7 Wedgetail)
- Combat aircraft (fighters, strike aircraft)

**Per-Theater Thresholds**:

| Theater          | Min Tankers | Min AWACS | Min Fighters |
|------------------|-------------|-----------|--------------|
| Iran Theater     | 10          | 2         | 30           |
| Taiwan Strait    | 5           | 1         | 20           |
| Korean Peninsula | 4           | 1         | 15           |
| Baltic/Black Sea | 3-4         | 1         | 10-15        |
| Israel/Gaza      | 2           | 1         | 8            |

**Output**: When all three criteria met, theater flagged as **STRIKE CAPABLE** → forces sufficient for sustained offensive operations.

---

### 2.4 Strategic Posture Analysis

**Purpose**: At-a-glance situational awareness of global force concentrations across 9 theaters.

**Strategic Theaters** (9 for posture analysis):
1. Iran Theater (20N-42N, 30E-65E)
2. Taiwan Strait (18N-30N, 115E-130E)
3. Korean Peninsula (33N-43N, 124E-132E)
4. Baltic Theater (52N-65N, 10E-32E)
5. Black Sea (40N-48N, 26E-42E)
6. South China Sea (5N-25N, 105E-121E)
7. Eastern Mediterranean (33N-37N, 25E-37E)
8. Israel/Gaza (29N-33N, 33E-36E)
9. Yemen/Red Sea (11N-22N, 32E-54E)

**Posture Levels**:

| Level        | Indicator | Criteria                      | Meaning                       |
|--------------|-----------|-------------------------------|-------------------------------|
| **Normal**   | NORM      | Below elevated threshold      | Routine peacetime activity    |
| **Elevated** | ELEV      | At/above elevated threshold   | Increased activity, exercises |
| **Critical** | CRIT      | At/above critical threshold   | Major deployment, crisis      |

**Example Thresholds**:
- Iran Theater: Elevated = 50 aircraft, Critical = 100 aircraft
- Taiwan Strait: Elevated = 30 aircraft, Critical = 60 aircraft

**Trend Detection** (rolling historical data):
- **Increasing**: Current activity >10% higher than previous period
- **Stable**: Within +/-10%
- **Decreasing**: >10% lower

**Server-Side Caching** (Redis):
- Active cache: 5 minutes (matches OpenSky refresh rate)
- Stale cache: 1 hour (fallback when upstream APIs fail)

---

### 2.5 Military Vessel Identification

**MMSI Analysis** (Maritime Mobile Service Identity):
- MMSI encodes flag state (country code)
- System maintains 150+ country code mappings

**Example MID Ranges**:

| MID Range | Country | Notes               |
|-----------|---------|---------------------|
| 338-339   | USA     | US Navy, Coast Guard|
| 273       | Russia  | Russian Navy        |
| 412-414   | China   | PLAN vessels        |
| 232-235   | UK      | Royal Navy          |
| 226-228   | France  | Marine Nationale    |

**Known Vessel Database** (50+ named vessels):

| Category            | Tracked Vessels                                    |
|---------------------|----------------------------------------------------|
| **US Carriers**     | All 11 Nimitz/Ford-class (CVN-68 through CVN-78)   |
| **UK Carriers**     | HMS Queen Elizabeth (R08), HMS Prince of Wales (R09)|
| **Chinese Carriers**| Liaoning (16), Shandong (17), Fujian (18)          |
| **Russian Carrier** | Admiral Kuznetsov                                  |
| **Destroyers**      | USS Zumwalt (DDG-1000), HMS Defender (D36)         |
| **Research/Intel**  | USNS Victorious (T-AGOS-19), USNS Impeccable      |

**Vessel Classification Algorithm**:
1. Check vessel name against known database (hull numbers + ship names)
2. Fall back to AIS ship type code if name match fails
3. Apply MMSI pattern matching for country/operator identification
4. For naval-prefix vessels (USS, HMS, HMCS, HMAS, INS, JS, ROKS, TCG), infer military status

**Callsign Patterns**: Known military callsign prefixes (NAVY, GUARD, etc.) provide secondary identification.

---

### 2.6 Naval Chokepoint Monitoring

**12 Critical Maritime Chokepoints**:

| Chokepoint        | Strategic Significance           |
|-------------------|----------------------------------|
| Strait of Hormuz  | 20% of global oil transits       |
| Suez Canal        | Europe-Asia shipping             |
| Strait of Malacca | Primary Asia-Pacific oil route   |
| Bab el-Mandeb     | Red Sea access, Houthi activity  |
| Panama Canal      | Americas east-west transit       |
| Taiwan Strait     | Cross-strait tensions            |
| Cape of Good Hope | Suez bypass route for VLCCs      |
| Strait of Gibraltar| Atlantic-Mediterranean gateway  |
| Bosporus          | Black Sea access                 |
| Korea Strait      | Japan-Korea trade                |
| Dover Strait      | World's busiest shipping lane    |
| Kerch Strait      | Russia-controlled, Azov access   |
| Lombok Strait     | Malacca bypass for tankers       |

**Detection**: Configurable radius per chokepoint → proximity alerts when military vessels enter.

---

### 2.7 Naval Base Proximity Monitoring

**12 Major Naval Installations Tracked**:
- Norfolk (USA) — Atlantic Fleet HQ
- Pearl Harbor (USA) — Pacific Fleet base
- Sevastopol (Russia) — Black Sea Fleet
- Qingdao (China) — North Sea Fleet
- Yokosuka (Japan) — US 7th Fleet

**Detection**: Vessels within 50km of these bases flagged → unusual activity pattern detection.

---

### 2.8 Vessel Position History

**Position Trails**:
- 30-point history per MMSI
- 10-minute cleanup interval for stale data
- Trail visualization on map for recent movement

**Purpose**: Enable detection of loitering, circling, or anomalous behavior patterns.

---

### 2.9 Maritime Density Analysis

**Grid-Based Aggregation**:
- Vessel positions aggregated into 2-degree grid
- Each cell tracks:
  - Current vessel count
  - Historical baseline (30-minute rolling window)
  - Change percentage from baseline

**Alert Triggers**: Density changes of +/-30% → potential congestion, diversions, or blockades.

---

### 2.10 Dark Ship Detection

**Purpose**: Monitor for AIS gaps (vessels stopping transmission).

**Detection Logic**:
- AIS gap exceeding 60 minutes in monitored regions
- Potential indicators:
  - Sanctions evasion (ship-to-ship transfers)
  - Illegal fishing
  - Military activity
  - Equipment failure

**Output**: Vessels reappearing after gaps flagged for session duration.

---

### 2.11 Aircraft Enrichment (Wingbits)

**Purpose**: Enhance aircraft tracking with detailed info beyond transponder data.

**What Wingbits Provides** (per aircraft):
- Registration (tail number, e.g., N12345)
- Owner (legal owner)
- Operator (operating entity)
- Manufacturer (Boeing, Lockheed Martin, etc.)
- Model (specific aircraft model)
- Built Year (manufacture year)

**Military Classification Algorithm**:

**Confirmed Military** (owner/operator match):
- Government: "United States Air Force", "Department of Defense", "Royal Air Force"
- International: "NATO", "Ministry of Defence", "Bundeswehr"

**Likely Military** (operator ICAO codes):
- `AIO` (Air Mobility Command), `RRR` (Royal Air Force), `GAF` (German Air Force)
- `RCH` (REACH flights), `CNV` (Convoy flights), `DOD` (Department of Defense)

**Possible Military** (defense contractors):
- Northrop Grumman, Lockheed Martin, General Atomics, Raytheon, Boeing Defense, L3Harris

**Aircraft Type Matching**:
- Transport: C-17, C-130, C-5, KC-135, KC-46
- Reconnaissance: RC-135, U-2, RQ-4, E-3, E-8
- Combat: F-15, F-16, F-22, F-35, B-52, B-2
- European: Eurofighter, Typhoon, Rafale, Tornado, Gripen

**Confidence Levels**:
- **Confirmed**: Direct military owner/operator match (green badge)
- **Likely**: Military ICAO code or aircraft type (yellow badge)
- **Possible**: Defense contractor ownership (gray badge)
- **Civilian**: No military indicators (no badge)

**Caching Strategy**:
- Server-side: HTTP Cache-Control headers (24-hour max-age)
- Client-side: 1-hour local cache per aircraft
- Batch optimization: Up to 20 aircraft per API call

**Note**: Wingbits is a **paid service** — pricing not disclosed in docs. **Alternative**: Build custom enrichment database from public sources (FAA registry, Wikipedia lists, Jane's, etc.).

---

### 2.12 Hotspot Activity Scoring

**Purpose**: Dynamic hotspot detection with real-time activity scoring based on news correlation.

**Multi-Component Approach** (4 weighted components):

| Component                  | Weight | Data Source               | What It Measures                    |
|----------------------------|--------|---------------------------|-------------------------------------|
| **News Activity**          | 35%    | RSS feeds                 | Matching news count, breaking flags, velocity |
| **CII Contribution**       | 25%    | Country Instability Index | Instability score of associated country |
| **Geographic Convergence** | 25%    | Multi-source events       | Event type diversity in geographic cell |
| **Military Activity**      | 15%    | OpenSky/AIS               | Flights + vessels within 200km      |

**Score Calculation**:
```python
static_baseline = hotspot.baselineRisk  # 1-5 per hotspot
dynamic_score = (
    news_component × 0.35 +
    cii_component × 0.25 +
    geo_component × 0.25 +
    military_component × 0.15
)
proximity_boost = hotspot_proximity_multiplier  # 1.0-2.0

final_score = (static_baseline × 0.30 + dynamic_score × 0.70) × proximity_boost
```

**Trend Detection**:
- 48-point history (24 hours at 30-minute intervals) per hotspot
- Linear regression calculates slope
- **Rising**: Slope > +0.1 points per interval
- **Falling**: Slope < -0.1 points per interval
- **Stable**: Slope within ±0.1

**Activity Levels** (visual indicators):

| Level        | Criteria                         | Visual       |
|--------------|----------------------------------|--------------|
| **Low**      | <3 matches, normal velocity      | Gray marker  |
| **Elevated** | 3-6 matches OR elevated velocity | Yellow pulse |
| **High**     | >6 matches OR spike velocity     | Red pulse    |

**Escalation Signals** (`hotspot_escalation`):
- Emitted when final score exceeds threshold (typically 60)
- Cooldown: At least 2 hours since last signal for this hotspot
- Conditions: Trend is rising OR score is critical (>80)

---

## 3. Key Features & Implementation Patterns

### 3.1 WebSocket Architecture (Real-Time Streaming)

**AIS Data Flow**:
```
AISStream → WebSocket Relay (Railway) → Browser
```

- **Connection**: Automatic reconnection on disconnection (30-second backoff)
- **Lifecycle**: WebSocket disconnects when Ships layer disabled (resource conservation)
- **Client-Side**: Browser maintains WebSocket connection, receives position updates

**Implementation for Atlas Intel**:
- Railway relay server (Node.js) with WebSocket support
- Alternative: VPS with WebSocket server + Redis pub/sub for scaling

---

### 3.2 Railway Relay Server Pattern

**Purpose**: Bypass cloud provider IP blocks for APIs that restrict Vercel/AWS/Cloudflare Workers.

**Relay Functions**:

| Endpoint        | Purpose           | Authentication          |
|-----------------|-------------------|-------------------------|
| `/` (WebSocket) | AIS vessel stream | AISStream API key       |
| `/opensky`      | Military aircraft | OAuth2 Bearer token     |
| `/rss`          | Blocked RSS feeds | User-agent spoofing     |
| `/health`       | Status check      | None                    |

**Environment Variables** (Railway):
- `AISSTREAM_API_KEY` — AIS data access
- `OPENSKY_CLIENT_ID` — OAuth2 client ID
- `OPENSKY_CLIENT_SECRET` — OAuth2 client secret

**Why Railway?**
- Residential IP ranges (not blocked like cloud providers)
- WebSocket support for persistent connections
- Global edge deployment (low latency)
- Free tier sufficient for moderate traffic

**Alternative for Atlas Intel**: VPS (DigitalOcean, Linode, Hetzner) with Nginx reverse proxy.

---

### 3.3 Client-Side SGP4 Propagation

**Cost Optimization Pattern**: Ship TLE data to browser, do orbital math client-side → zero ongoing server cost for real-time movement.

**Implementation**:
- Library: `satellite.js` (v6) for SGP4/SDP4 orbital propagation
- Propagation frequency: Every 3 seconds (LEO satellites move ~23km in 3s)
- **Key insight**: TLE data changes slowly (every 2h), but positions change every second → propagate locally

**Performance**:
- Parse TLEs once (expensive, cached until refresh)
- Propagate positions every 3s (cheap, runs in browser)
- 15-point orbit trails (1 per minute, looking back 15 min)

---

### 3.4 Redis Caching Strategy

**Pattern**: Aggressive caching with stale-while-revalidate fallback.

**Satellite TLEs**:
- Key: `intelligence:satellites:tle:v1`
- TTL: 4 hours
- Writer: Railway relay (2h cycle)
- Shape: `{ satellites: SatelliteTLE[], fetchedAt: number }`

**Strategic Posture**:
- Active cache: 5 minutes (matches OpenSky refresh rate)
- Stale cache: 1 hour (fallback when upstream APIs fail)

**Aircraft Enrichment**:
- Server-side: HTTP Cache-Control (24-hour max-age)
- Client-side: 1-hour local cache per aircraft
- Batch optimization: Up to 20 aircraft per API call

---

### 3.5 News Correlation Pattern

**Purpose**: Provide context for military alerts by correlating with breaking news.

**Flow**:
1. Generate military alert (surge, foreign presence, etc.)
2. Identify countries involved (aircraft operators, region countries)
3. Check focal points for those countries
4. If news correlation exists, attach headlines + evidence

**Example Output**:
```
MILITARY AIRLIFT SURGE: Middle East Theater
Current: 8 transport aircraft (2.5x baseline)

NEWS CORRELATION:
Iran: "Iran protests continue amid military..."
-> Iran appears in both news (12) and map signals (9)
```

---

### 3.6 Circuit Breaker Pattern

**Purpose**: Prevent cascading failures when upstream APIs are down.

**Client-Side Fetch Circuit Breaker**:
- 3 consecutive failures trigger 10-minute cooldown
- Cached data continues to be used during cooldown
- Prevents hammering APIs during outages

---

### 3.7 Globe-Only Rendering

**Orbital Surveillance Design Decision**: Satellites rendered ONLY on 3D globe (not flat map).

**Rationale**: Orbital mechanics don't translate meaningfully to flat map projection.

**Rendering Details**:
- `htmlAltitude = altitude_km / 6371` (Earth radius = 6371km, globe.gl uses normalized units)
- Marker size: 4px with 6px glow
- Trail rendering: `pathsData` with `pathPointAlt` for 3D orbit paths
- Footprint: Surface-level marker (`htmlAltitude = 0`) with 12px translucent ring

---

## 4. Data Formats & Schemas

### 4.1 TLE Format (Two-Line Element Set)

**Example**:
```
ISS (ZARYA)
1 25544U 98067A   21275.51782528  .00016717  00000-0  10270-3 0  9005
2 25544  51.6412 210.1434 0004012  25.1635  45.9124 15.48919393302367
```

**Line 0**: Satellite name  
**Line 1**: Catalog number, classification, launch year, epoch, drag terms  
**Line 2**: Inclination, RAAN, eccentricity, argument of perigee, mean anomaly, mean motion

**Parsed by**: `satellite.js` library → `SatRec` objects for propagation.

---

### 4.2 AIS Message Format

**MMSI Structure**:
- First 3 digits: MID (Maritime Identification Digit) — country code
- Example: 338xxxxxx = USA, 273xxxxxx = Russia, 412xxxxxx = China

**Ship Type Codes** (AIS):
- 30: Fishing
- 35: Military ops
- 50-59: Passenger
- 60-69: Cargo
- 70-79: Tanker
- 80-89: Other

**Position Message**:
- Latitude/longitude (decimal degrees)
- Speed over ground (knots)
- Course over ground (degrees)
- Heading (degrees)
- Timestamp (UTC)

---

### 4.3 OpenSky ADS-B Response

**Fields**:
- `icao24`: ICAO 24-bit address (hex, e.g., "a1b2c3")
- `callsign`: Aircraft callsign (e.g., "RCH123")
- `origin_country`: Country of registration
- `time_position`: Last position update timestamp
- `last_contact`: Last contact timestamp
- `longitude`, `latitude`: Position (decimal degrees)
- `baro_altitude`: Barometric altitude (meters)
- `on_ground`: Boolean
- `velocity`: Ground speed (m/s)
- `true_track`: Heading (degrees)

---

### 4.4 Military Surge Signal Schema

```json
{
  "type": "military_surge",
  "location": {
    "lat": 25.0,
    "lng": 55.0
  },
  "message": "Military Transport Surge in Middle East Theater: 8 aircraft (baseline: 3.2)",
  "details": {
    "theater": "Middle East",
    "current_count": 8,
    "baseline": 3.2,
    "surge_ratio": 2.5,
    "aircraft_types": {
      "transport": 5,
      "fighter": 2,
      "reconnaissance": 1
    },
    "top_callsigns": ["RCH123", "REACH456"],
    "nearby_bases": ["Al Udeid Air Base", "Al Dhafra Air Base"]
  },
  "confidence": 0.85,
  "severity": "HIGH"
}
```

---

### 4.5 Hotspot Escalation Signal Schema

```json
{
  "type": "hotspot_escalation",
  "location": {
    "lat": 33.8869,
    "lng": 35.5131
  },
  "hotspot_id": "beirut",
  "hotspot_name": "Beirut",
  "score": 72.5,
  "trend": "rising",
  "components": {
    "news_activity": 0.8,
    "cii_contribution": 0.6,
    "geographic_convergence": 0.7,
    "military_activity": 0.5
  },
  "confidence": 0.88,
  "why_it_matters": "Geopolitical hotspot showing significant escalation based on news activity, country instability, geographic convergence, and military presence",
  "actionable_insight": "Increase monitoring priority; assess downstream impacts on infrastructure, markets, and regional stability"
}
```

---

## 5. Implementation Roadmap for Atlas Intel

### Phase 1: Core Data Ingestion (FREE APIs)

**Week 1-2: OpenSky Aircraft Tracking**
1. Register for free OpenSky account
2. Set up OAuth2 client credentials
3. Deploy Railway relay server (or VPS alternative)
4. Implement callsign pattern matching (Transport/Fighter/Recon)
5. Build 20-point position history per aircraft
6. Test with Western Europe theater (good ADS-B coverage)

**Week 3-4: CelesTrak Satellite Tracking**
1. Fetch TLEs from CelesTrak (military + resource groups)
2. Implement TLE parsing + filtering (80-120 satellites)
3. Integrate `satellite.js` for SGP4 propagation
4. Build 3s client-side propagation loop
5. Render on 3D globe (altitude, trails, footprints)

**Week 5-6: Maritime Tracking (AIS)**
1. Investigate AISStream API pricing (if prohibitive, use MarineTraffic/VesselFinder free tier)
2. Set up WebSocket relay for AIS stream
3. Implement MMSI country code mapping (150+ countries)
4. Build known vessel database (carriers, destroyers, research vessels)
5. Implement 30-point position history per vessel

---

### Phase 2: Detection Algorithms

**Week 7-8: Military Surge Detection**
1. Define 5 theaters for surge analysis (Middle East, Eastern Europe, Pacific, etc.)
2. Implement 48-hour rolling baseline per theater
3. Build aircraft classification (Transport/Fighter/Recon)
4. Implement surge algorithm (2x baseline + thresholds)
5. Generate `military_surge` signals with confidence scoring

**Week 9-10: Foreign Presence Detection**
1. Define 18 sensitive regions (Taiwan Strait, Persian Gulf, etc.)
2. Implement exclusion logic (home region operators)
3. Build critical combination matrix (PLAAF/Taiwan, etc.)
4. Generate `foreign_military_presence` signals

**Week 11-12: Strike Capability Assessment**
1. Define per-theater thresholds (tankers, AWACS, fighters)
2. Implement asset detection (KC-135, E-3, F-15, etc.)
3. Build STRIKE CAPABLE flag logic
4. Integrate with posture analysis panel

---

### Phase 3: Hotspot Scoring & Correlation

**Week 13-14: Hotspot Activity Scoring**
1. Define hotspot keywords per region
2. Implement news correlation (RSS feeds via NewsAPI or Google News RSS)
3. Build 4-component scoring algorithm (News 35%, CII 25%, Geo 25%, Military 15%)
4. Implement 48-point trend detection (linear regression)
5. Generate `hotspot_escalation` signals

**Week 15-16: News Correlation Engine**
1. Aggregate RSS feeds (Al Jazeera, BBC, Reuters, etc.)
2. Implement keyword matching + velocity analysis
3. Build news correlation layer (attach headlines to military signals)
4. Test cross-layer correlation (news + surge + foreign presence)

---

### Phase 4: Advanced Features

**Week 17-18: Chokepoint Monitoring**
1. Define 12 chokepoints with detection radii
2. Integrate IMF PortWatch for weekly transit counts
3. Implement real-time AIS-based 24h counter
4. Build 180-day time-series charts (TradingView lightweight-charts)

**Week 19-20: Maritime Density + Dark Ships**
1. Implement 2-degree grid for density analysis
2. Build 30-minute rolling window baseline
3. Implement +/-30% change alerts
4. Build dark ship detection (60-min AIS gap)

**Week 21-22: Naval Base Proximity**
1. Define 12 major naval installations (Norfolk, Pearl Harbor, etc.)
2. Implement 50km proximity alerts
3. Build naval vessel classification (Carrier/Destroyer/Frigate/Submarine)
4. Integrate with strategic posture analysis

---

### Phase 5: Polish & Optimization

**Week 23-24: Caching & Performance**
1. Implement Redis caching (active 5min, stale 1h)
2. Build circuit breaker for upstream API failures
3. Optimize client-side propagation (satellite.js)
4. Implement batch API calls (aircraft enrichment)

**Week 25-26: UI/UX**
1. Build 3D globe renderer (globe.gl or Cesium.js)
2. Implement regional focus navigation (8 presets)
3. Build posture analysis panel (9 theaters)
4. Implement map pinning for persistent monitoring

---

## 6. Cost Analysis (FREE vs PAID)

### FREE Tier (Prototype)

| Data Source         | Cost  | Limitations                                       |
|---------------------|-------|---------------------------------------------------|
| OpenSky Network     | $0    | Cloud IP blocks (needs relay), 30-min rate limit  |
| CelesTrak TLEs      | $0    | 2h update frequency, no classified satellites     |
| IMF PortWatch       | $0    | Weekly data only                                  |
| NewsAPI.org         | $0    | 100 requests/day, 1-month archive                 |
| Google News RSS     | $0    | No API limits, parsing required                   |
| Railway (relay)     | $0    | Free tier: 500h/month, 512MB RAM                  |
| Redis (Upstash)     | $0    | Free tier: 10K requests/day                       |

**Total: $0/month** for prototype with 100-500 concurrent users.

---

### PAID Services (Optional Upgrades)

| Service             | Cost        | What You Get                                |
|---------------------|-------------|---------------------------------------------|
| AISStream           | Unknown     | Real-time AIS WebSocket stream              |
| Wingbits            | Unknown     | Aircraft enrichment (owner, operator, etc.) |
| MarineTraffic API   | $99/month   | Real-time AIS, vessel details, port calls   |
| FlightRadar24 API   | $500/month  | Commercial ADS-B with global coverage       |
| Maxar/Planet        | Enterprise  | Actual satellite imagery (SAR/optical)      |

**Alternative FREE Approaches**:
- **AIS**: Use free tier from VesselFinder or public AIS receivers
- **Aircraft enrichment**: Build custom database from FAA registry, Wikipedia, Jane's
- **Satellite imagery**: Use Sentinel Hub (ESA Copernicus data, free for research)

---

## 7. Recommended Tech Stack for Atlas Intel

### Backend
- **Node.js** (Railway relay server)
- **Redis** (Upstash for caching)
- **PostgreSQL** (historical data, baselines)

### Frontend
- **React/Next.js** (map-based UI)
- **globe.gl** or **Cesium.js** (3D globe for satellites)
- **Leaflet** or **Mapbox GL JS** (2D map for vessels/aircraft)
- **TradingView Lightweight Charts** (time-series for chokepoints)
- **satellite.js** (client-side SGP4 propagation)

### APIs
- **OpenSky Network** (aircraft)
- **CelesTrak** (satellites)
- **NewsAPI.org** or Google News RSS (news correlation)
- **IMF PortWatch** (chokepoint traffic)

### Infrastructure
- **Railway** (relay server for API proxying)
- **Vercel** (frontend hosting + edge functions)
- **Upstash Redis** (caching layer)

---

## 8. Gaps & Missing Data (Needs Investigation)

### Not Documented / Unclear:
1. **AISStream pricing** — API key required, but cost not disclosed
2. **CorridorRisk** — Mentioned for chokepoint risk intelligence, but no details
3. **Wingbits pricing** — Aircraft enrichment service, cost not disclosed
4. **Country Instability Index (CII)** — Used in hotspot scoring, but source/methodology not explained
5. **Focal Point Detector** — Mentioned for news correlation, but implementation not detailed
6. **Aircraft ICAO hex ranges** — Military hex code blocks by country (not enumerated)
7. **Vessel AIS ship type codes** — Full list not provided (only examples)

### Recommended Actions:
- **AISStream**: Contact for pricing → if prohibitive, use MarineTraffic free tier
- **Wingbits**: Evaluate cost → if expensive, build custom enrichment DB
- **CII**: Research public instability indices (GPI, Fragile States Index, etc.)
- **Aircraft ICAO hex**: Scrape from public sources (Wikipedia, planespotters.net)

---

## 9. Key Takeaways for Atlas Intel

### ✅ Fully Replicable with FREE APIs:
- OpenSky aircraft tracking (with relay server)
- CelesTrak satellite orbital surveillance
- IMF PortWatch chokepoint traffic
- News correlation via NewsAPI/Google News RSS
- Client-side SGP4 propagation (zero server cost)
- Redis caching for performance

### ⚠️ Needs Investigation/Cost Evaluation:
- AISStream (real-time AIS) — pricing unclear
- Wingbits (aircraft enrichment) — pricing unclear
- MarineTraffic/VesselFinder as alternatives

### 🚀 Quick Wins (Low-Hanging Fruit):
1. **Satellite tracking** — CelesTrak + satellite.js = fully free, impressive visual
2. **OpenSky aircraft tracking** — Free after relay setup, rich data
3. **News correlation** — Google News RSS = free + unlimited
4. **Hotspot scoring** — Pure algorithm, no paid APIs required

### 📊 Complexity Assessment:
- **Easy**: CelesTrak satellites, news RSS, hotspot scoring
- **Medium**: OpenSky aircraft, surge detection, chokepoint monitoring
- **Hard**: AIS maritime (if AISStream costly), strike capability assessment, cross-layer correlation

---

## 10. Next Steps

1. **Register for OpenSky** (free account)
2. **Test CelesTrak TLE fetch** (prototype satellite tracking)
3. **Investigate AISStream pricing** (or evaluate MarineTraffic free tier)
4. **Deploy Railway relay** (or VPS alternative for API proxying)
5. **Build MVP with 3 layers**: Satellites (CelesTrak), Aircraft (OpenSky), News (RSS)
6. **Implement surge detection** (5 theaters, 48h baseline)
7. **Add hotspot scoring** (4-component algorithm)

---

**Report Compiled**: 2026-03-23  
**Sources**: World Monitor documentation (military-tracking.md, maritime-intelligence.md, orbital-surveillance.md, hotspots.md)  
**Status**: ✅ Complete — All 4 pages crawled and analyzed  
**FREE API Viability**: HIGH — Core features fully implementable with free data sources  
**Estimated Development Time**: 26 weeks (6 months) for full feature parity  
**Recommended MVP Timeline**: 6-8 weeks (Phases 1-2: data ingestion + detection algorithms)
