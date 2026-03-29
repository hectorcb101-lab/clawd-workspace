# World Monitor Intelligence Extract: Cyber, Webcams & Risk Scoring

**Research Date:** 2025-03-23  
**Purpose:** Extract free data sources, APIs, algorithms, and features from World Monitor documentation for Atlas Intel dashboard implementation.

---

## Executive Summary

World Monitor uses a comprehensive multi-source architecture combining:
- **26 free data sources** for cyber threats, natural disasters, protests, conflicts, advisories
- **Server-side aggregation** to reduce client load (single digest API vs 25+ individual feeds)
- **Dual-source validation** (ACLED + GDELT for protests, multiple sources for disasters)
- **Real-time scoring algorithms** for Country Instability Index (CII) with regime-aware dampening
- **Geographic convergence detection** to identify multi-event hotspots
- **Tiered caching** (Redis server-side + client-side memory caches)

**Key Insight:** Most data sources are FREE but require API keys. Core innovation is in the *aggregation, deduplication, and scoring algorithms* rather than proprietary data.

---

## 🔴 FREE Data Sources & APIs

### Cyber Threat Intelligence

| Source | Type | API Endpoint | Update Frequency | FREE Tier |
|--------|------|--------------|------------------|-----------|
| **Feodo Tracker** (abuse.ch) | C2 Servers | `https://feodotracker.abuse.ch/downloads/ipblocklist.csv` | Real-time | ✅ Fully free |
| **URLhaus** (abuse.ch) | Malware Hosts | `https://urlhaus.abuse.ch/downloads/csv/` | Real-time | ✅ Fully free |
| **C2IntelFeeds** | C2 Servers | Community-sourced feeds (GitHub repos) | Varies | ✅ Fully free |
| **AlienVault OTX** | Mixed IOCs | `https://otx.alienvault.com/api/v1/pulses/` | Real-time | ✅ Free (API key required) |
| **AbuseIPDB** | Malicious IPs | `https://api.abuseipdb.com/api/v2/blacklist` | Real-time | ✅ Free tier (1000/day) |
| **Ransomware.live** | Ransomware Groups | RSS/API feeds from ransomware tracker | Real-time | ✅ Fully free |

**Geolocation Enrichment:**
- **ipinfo.io** (free tier: 50,000 requests/month)
- **freeipapi.com** (fallback, fully free)
- Cached for 24 hours in Redis
- Concurrent enrichment: 16 parallel lookups, 12s timeout, max 250 IPs per run

**IOC Classification:**
- `c2_server`, `malware_host`, `phishing`, `malicious_url`
- Four severity levels (rendered as color-coded dots on globe)
- 10-minute cache, 14-day rolling window, max 500 IOCs displayed

### Natural Disasters

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **USGS Earthquakes** | M4.5+ global | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson` | 5 minutes | ✅ Fully free |
| **GDACS** | UN disaster alerts | `https://www.gdacs.org/xml/rss.xml` | Real-time | ✅ Fully free |
| **NASA EONET** | Earth observation events | `https://eonet.gsfc.nasa.gov/api/v3/events` | Real-time | ✅ Fully free |

**Event Types:** Earthquakes, floods, cyclones, volcanoes, wildfires, droughts  
**Deduplication:** Haversine distance on 0.1° grid (~10km)  
**Filtering:** 
- GDACS: Red/Orange alerts only (Green excluded)
- EONET: Wildfires within 48 hours only
- EONET earthquakes excluded (USGS provides better seismic data)

### Conflict & Protest Data

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **ACLED** | Conflicts, protests, riots | `https://api.acleddata.com/` | Daily | ✅ Free (API key required) |
| **GDELT** | Geospatial events | `http://data.gdeltproject.org/events/` | 15 minutes | ✅ Fully free |
| **UCDP** | Armed conflicts | `https://ucdp.uu.se/downloads/` | Weekly | ✅ Fully free |

**Dual-Source Protest Tracking:**
- ACLED: 30-day window, tokenized API, Redis cached (10-min TTL)
- GDELT: 7-day window, filtered to protest keywords, mention count ≥5
- **Haversine deduplication** on 0.1° grid, same-day matching
- ACLED events take priority (higher editorial confidence)

**Severity Classification:**
- **High:** Fatalities present or riot/clash keywords
- **Medium:** Standard protest/demonstration  
- **Low:** Default

**Regime-Aware Scoring:**
- **Democratic countries:** Logarithmic scaling (routine protests don't trigger instability)
- **Authoritarian states:** Linear scaling (every protest is significant)

### Security Advisories

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **US State Dept** | Travel advisories | RSS feed | Daily | ✅ Fully free |
| **Australia DFAT** | Smartraveller | RSS feed | Daily | ✅ Fully free |
| **UK FCDO** | Travel advice | RSS feed | Daily | ✅ Fully free |
| **New Zealand MFAT** | Travel advisories | RSS feed | Daily | ✅ Fully free |
| **CDC Travel Notices** | Health advisories | RSS feed | Daily | ✅ Fully free |
| **ECDC** | Epidemiological updates | RSS feed | Daily | ✅ Fully free |
| **WHO News** | Health emergencies | RSS feed | Daily | ✅ Fully free |

**Advisory Levels (Ranked):**
1. Do-Not-Travel (4)
2. Reconsider Travel (3)
3. Exercise Caution (2)
4. Normal (1)
5. Info (0)

**Country Extraction:** 265-entry country name map (generated from GeoJSON + aliases)

**CII Integration:**
- Do-Not-Travel → +15 points
- Reconsider → +10 points
- Caution → +5 points
- **Consensus bonus:** ≥3 governments → +5, ≥2 → +3
- **Score floor:** DNT forces minimum CII score of 60; Reconsider forces 50

### GPS/GNSS Jamming

| Source | Coverage | Data Format | Update Frequency | FREE Tier |
|--------|----------|-------------|------------------|-----------|
| **gpsjam.org** | Global ADS-B analysis | H3 hex grid | Real-time | ✅ Fully free |

**Detection Method:** ADS-B transponder data showing GPS anomalies  
**Grid:** H3 resolution-4 hexagonal cells  
**Threshold:** Minimum 3 aircraft per cell (statistical noise filter)

**Classification:**

| Level | Bad Aircraft % | Map Color |
|-------|----------------|-----------|
| Low | 0-2% | Hidden |
| Medium | 2-10% | Amber |
| High | >10% | Red |

**Region Tagging:** 12 conflict zones (Iran-Iraq, Levant, Ukraine-Russia, Baltic, Mediterranean, Black Sea, Arctic, Caucasus, Central Asia, Horn of Africa, Korean Peninsula, South China Sea)

**CII Integration:** Up to 35 points: `min(35, highCount × 5 + mediumCount × 2)`

### Airport Delays & NOTAM

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **FAA ASWS** | 14 US hubs | `https://nasstatus.faa.gov/api/airport-status-information` | Real-time XML | ✅ Fully free |
| **AviationStack** | 40 international | `http://api.aviationstack.com/v1/flights` | Real-time | ⚠️ Free tier (500/month) |
| **ICAO NOTAM** | 46 MENA airports | ICAO API (requires credentials) | Real-time | ❌ Requires partnership |

**Severity Thresholds:**
- **Minor:** ≥15min avg delay or ≥15% delayed flights
- **Moderate:** ≥30min/30%
- **Major:** ≥45min/45%
- **Severe:** ≥60min/60%
- **Closure:** ≥80% cancellation rate with ≥10 flights

**NOTAM Closure Detection:**
- ICAO Q-codes: `FA`, `AH`, `AL`, `AW`, `AC`, `AM` + qualifiers `LC`, `AS`, `AU`, `XX`, `AW`
- Regex keywords: `AD CLSD`, `AIRPORT CLOSED`, `AIRSPACE CLOSED`

**Cache:** 30 minutes in Redis

### Webcams (Visual Intelligence)

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **Windy Webcams API** | ~65,000 cameras | `https://api.windy.com/webcams/api/v3/` | 5-15 min | ⚠️ Free tier (requires key) |

**API Key:** Required from [api.windy.com](https://api.windy.com)

**Seed-Time Fields (bulk fetch with `include=location,categories`):**
- `webcamId`, `title`, `location.latitude`, `location.longitude`
- `location.country`, `location.region`, `categories`, `status`

**On-Demand Fields (per-camera fetch with `include=images,urls`):**
- `images.current.preview` (latest still image URL)
- `images.current.thumbnail` (smaller thumbnail)
- `urls.player` (embeddable timelapse player)
- `lastUpdatedOn` (timestamp)

**Free Tier Limitations:**
- Image token URLs expire after 10 minutes
- Bounding-box queries capped at 10,000 results per request
- Rate limits apply

**⚠️ CRITICAL LIMITATION:** Windy does NOT provide live video streams. Most webcams capture still images every 5-15 minutes. The "player" is a timelapse of recent snapshots (24-72 hours), not a live feed.

**Caching Strategy:**
- **Redis geo + metadata:** 24 hours
- **Redis viewport responses:** 24 hours (clustered results per map view)
- **Redis image lookups:** 5 minutes
- **Client image cache:** 9 minutes (in-memory Map)
- **Pinned webcams:** localStorage (permanent, user-managed)

**Alternative Sources (Future Phases):**
- **US DOT 511 State APIs:** Tens of thousands of traffic cameras (free with state keys, still images every 30-60s)
- **OpenWebcamDB:** ~2,052 cameras (free tier: 50 requests/day)
- **YouTube Live:** Already integrated for 22 strategic locations (Middle East, Europe, Americas, Asia-Pacific)

### Market Intelligence

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **CoinGecko** | Crypto prices | `https://api.coingecko.com/api/v3/` | Real-time | ✅ Free tier (50 calls/min) |
| **Yahoo Finance** | Stocks, commodities | `https://query1.finance.yahoo.com/v8/finance/chart/` | Real-time | ✅ Fully free (unofficial) |
| **Polymarket** | Prediction markets | `https://gamma-api.polymarket.com/` | Real-time | ✅ Free (but Cloudflare JA3 blocks server-side) |

**Polymarket Cloudflare Bypass (4-tier strategy):**
1. **Bootstrap hydration:** Redis-cached data embedded at page load (zero-network)
2. **Sebuf RPC:** Server-side Redis query (sub-100ms)
3. **Browser-direct:** Browser TLS fingerprint passes Cloudflare
4. **Tauri native TLS:** Rust `reqwest` TLS fingerprint differs from Node.js

**Smart Filtering:**
- Exclude sports/entertainment (100+ keywords: NBA, NFL, Oscar, Grammy)
- Require price divergence from 50% or volume >$50K
- Ranked by 24h trading volume

### Climate Data

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **Open-Meteo ERA5** | Global reanalysis | `https://archive-api.open-meteo.com/v1/archive` | Hourly | ✅ Fully free |

**Anomaly Detection:**
- 15 conflict-prone/disaster-prone zones monitored
- 30-day baseline computed
- Current conditions compared vs baseline

**Severity Classification:**

| Severity | Temperature Deviation | Precipitation Deviation |
|----------|----------------------|-------------------------|
| Extreme | >5°C above baseline | >80mm/day above baseline |
| Moderate | >3°C above baseline | >40mm/day above baseline |
| Normal | Within expected range | Within expected range |

**CII Integration:** Climate anomalies amplify CII scores for affected countries (stress as conflict accelerant)

### Displacement Tracking

| Source | Coverage | API Endpoint | Update Frequency | FREE Tier |
|--------|----------|--------------|------------------|-----------|
| **UN OCHA HAPI** | Refugees, IDPs | `https://hapi.humdata.org/api/v1/` | Monthly | ✅ Fully free |

**Data Types:** Refugees, asylum seekers, internally displaced persons (IDPs)

**Crisis Badges:**
- >1 million displaced: Red
- >500,000 displaced: Orange

**CII Integration:** Outflow feeds into CII as lagging instability indicator

---

## 🧮 Algorithms & Scoring

### Country Instability Index (CII)

**Monitored Countries (Tier 1):** 24 strategically significant countries across Americas, Europe, Middle East, Asia-Pacific

**Three Component Scores:**

| Component | Weight | Data Sources | Measures |
|-----------|--------|--------------|----------|
| **Unrest** | 40% | ACLED protests, GDELT events | Civil unrest intensity, fatalities, event severity |
| **Security** | 30% | Military flights, naval vessels | Unusual military activity patterns |
| **Information** | 30% | News velocity, alert clusters | Media attention intensity and acceleration |

**Scoring Algorithm:**

```javascript
// Unrest Score
base = min(50, protest_count × 8)
fatality_boost = min(30, total_fatalities × 5)
severity_boost = min(20, high_severity_count × 10)
unrest = min(100, base + fatality_boost + severity_boost)

// Security Score
flight_score = min(50, military_flights × 3)
vessel_score = min(30, naval_vessels × 5)
security = min(100, flight_score + vessel_score)

// Information Score
base = min(40, news_count × 5)
velocity_boost = min(40, avg_velocity × 10)
alert_boost = 20 if any_alert else 0
information = min(100, base + velocity_boost + alert_boost)

// Final CII
CII = round(unrest × 0.4 + security × 0.3 + information × 0.3)
```

**Bias Prevention - Log Scaling for High-Volume Countries:**

```javascript
if (newsVolume > threshold) {
  dampingFactor = 1 / (1 + log10(newsVolume / threshold))
  score = rawScore × dampingFactor
}
```

**Prevents:** US with 50 routine news mentions from outscoring Ukraine with 10 combat mentions

**Conflict Zone Floor Scores (Minimum Guarantees):**

| Country | Floor | Rationale |
|---------|-------|-----------|
| Ukraine | 55 | Active war with Russia |
| Syria | 50 | Ongoing civil war |
| Yemen | 50 | Ongoing civil war |
| Myanmar | 45 | Military coup, civil conflict |
| Israel | 45 | Active Gaza conflict |

**Contextual Score Boosts (Max +23 points):**

| Boost Type | Max Points | Condition | Purpose |
|------------|------------|-----------|---------|
| Hotspot Activity | 10 | Events near defined hotspots | Localized escalation |
| News Urgency | 5 | Information ≥50 | High media attention |
| Focal Point | 8 | AI focal point detection | Multi-source convergence |

**Instability Levels:**

| Level | Score Range | Visual | Meaning |
|-------|-------------|--------|---------|
| **Critical** | 81-100 | Red | Active crisis or major escalation |
| **High** | 66-80 | Orange | Significant instability requiring close monitoring |
| **Elevated** | 51-65 | Yellow | Above-normal activity patterns |
| **Normal** | 31-50 | Gray | Baseline geopolitical activity |
| **Low** | 0-30 | Green | Unusually quiet period |

**Trend Detection (24-hour changes):**
- **Rising:** Score increased ≥5 points (escalating)
- **Stable:** Change within ±5 points (steady state)
- **Falling:** Score decreased ≥5 points (de-escalation)

### Server-Side CII Computation

**Endpoint:** `/api/risk-scores` (`get-risk-scores.ts`)

**Process:**
1. Fetch ACLED data (7-day window: protests/riots/battles/explosions/civilian-violence)
2. Fetch auxiliary sources from Redis (UCDP conflicts, outages, climate, cyber, fires, GPS jamming, Iran events, OREF alerts)
3. Compute CII for 24 Tier 1 countries using same formulas as frontend
4. Derive strategic risk from weighted top-5 CII scores
5. Cache in Redis (10-min TTL, 1-hour stale fallback)

**CII Calculation Formula:**

```javascript
// Baseline Risk (0-50 points) - Static geopolitical risk
baseline = {
  "Syria": 50, "Ukraine": 50, "Yemen": 50,
  "Myanmar": 45, "North Korea": 45, "Cuba": 45,
  "Iran": 40, "Israel": 40, "Pakistan": 35, "Venezuela": 35,
  // ... (see full table below)
}

// Event Score (weighted sub-components)
unrest = protest_events × dampening_factor + fatality_boost + outage_boost
conflict = (battles × 3 + explosions × 4 + civilian_violence × 5) + fatalities^0.5 + iran_strikes + oref_alerts
security = (gps_high_count × 5 + gps_medium_count × 2) capped at 35
information = 0 // Reserved for future (no server-side news data)

event_score = (unrest × 0.25 + conflict × 0.30 + security × 0.20 + information × 0.25)

// Final CII
CII = (baseline × 0.4 + event_score × 0.6) + supplemental_boosts
CII = max(CII, floor_scores) // Apply minimum guarantees
```

**Baseline Risk Levels:**

| Countries | Baseline | Rationale |
|-----------|----------|-----------|
| Syria, Ukraine, Yemen | 50 | Active conflict zones |
| Myanmar, North Korea, Cuba | 45 | Civil unrest, authoritarian |
| Iran, Israel, Pakistan, Venezuela, Mexico | 35-40 | Regional tensions, organized crime |
| Taiwan, Saudi Arabia, Turkey, Russia, China, India | 20-35 | Moderate instability |
| Brazil, Mexico | 15-35 | Variable instability |
| Germany, UK, US, France, Poland, UAE | 5-10 | Stable/low risk |

**Event Significance Multipliers:**

| Multiplier | Countries | Rationale |
|------------|-----------|-----------|
| 3.0x | North Korea | Any visible unrest highly unusual |
| 2.0-2.5x | China, Russia, Iran, Saudi Arabia, Cuba | Authoritarian states suppress protests |
| 1.5-1.8x | Taiwan, Pakistan, Myanmar, Venezuela, UAE | Regional flashpoints |
| 1.0-1.2x | Mexico, Turkey | Moderate significance |
| 0.5-0.8x | US, UK, France, Germany, Poland, Ukraine, Syria, Yemen, Israel, India, Brazil | Protests routine or already in floors |

**Floor Scores (Minimum Guarantees):**

| Floor Type | Threshold | Trigger |
|------------|-----------|---------|
| UCDP active war | ≥70 | UCDP intensity level 2+ |
| UCDP minor conflict | ≥50 | UCDP intensity level 1 |
| Advisory do-not-travel | ≥60 | UA, SY, YE, MM |
| Advisory reconsider | ≥50 | IL, IR, PK, VE, CU, MX |

**Supplemental Boosts:**
- Advisory boost: +15 (DNT) / +10 (Reconsider) / +5 (Caution)
- OREF blend (IL only): +15 (active alerts) + history tiers
- Climate anomalies: +15 max
- Cyber threats: +10 max
- Wildfires: +8 max

### Strategic Risk Score

**Composite Risk Score (0-100):**

| Component | Weight | Calculation |
|-----------|--------|-------------|
| Convergence | 40% | `min(100, convergence_zones × 20)` |
| CII Deviation | 35% | `min(100, avg_deviation × 2)` |
| Infrastructure | 25% | `min(100, incidents × 25)` |

**Strategic Risk Derivation from CII:**

```javascript
// Weighted average of top 5 CII scores
weights = [1.0, 0.85, 0.70, 0.55, 0.40] // Total: 3.5
strategic_risk = (Σ CII[i] × weights[i]) / 3.5 × 0.7 + 15
```

**Risk Levels:**

| Score | Level | Trend | Meaning |
|-------|-------|-------|---------|
| 70-100 | **Critical** | Escalating | Multiple converging crises |
| 50-69 | **Elevated** | Stable | Heightened global tension |
| 30-49 | **Moderate** | Stable | Normal fluctuation |
| 0-29 | **Low** | De-escalating | Unusually quiet period |

**Unified Alert System:**
- **Temporal deduplication:** Alerts within 2 hours may merge
- **Spatial deduplication:** Alerts within 200km may merge
- **Country deduplication:** Alerts affecting same country may merge

**Alert Priority:**

| Priority | Criteria |
|----------|----------|
| **Critical** | CII critical level, convergence ≥80, cascade critical impact |
| **High** | CII high level, convergence ≥60, cascade affecting ≥5 countries |
| **Medium** | CII change ≥10 points, convergence ≥40 |
| **Low** | Minor changes and low-impact events |

### Geographic Convergence Detection

**Purpose:** Identify hotspots where multiple event types occur simultaneously (e.g., protest + outage + cyber attack in same location)

**Algorithm:**
1. Collect events from all sources with geographic coordinates
2. Grid the world into H3 hexagonal cells
3. Count event types per cell
4. Score cells: `convergence_score = event_types × 20` (capped at 100)
5. Classify convergence zones: ≥80 Critical, ≥60 High, ≥40 Medium

**Feeds into Strategic Risk:** Convergence zones weighted 40% in composite score

---

## 🏗️ Architecture Patterns

### Server-Side Feed Aggregation

**Problem:** Each client browser independently fetching 25+ RSS feeds → 25,000 edge invocations per 1,000 concurrent users

**Solution:** Single server-side digest API

```
Client (1 RPC call) → listFeedDigest → Redis check (digest:v1:{variant}:{lang})
                                              │
                                    ┌─────────┴─── HIT → return cached digest
                                    │
                                    ▼ MISS
                           ┌─────────────────────────┐
                           │  buildDigest()           │
                           │  20 concurrent fetches   │
                           │  8s per-feed timeout     │
                           │  25s overall deadline    │
                           └────────┬────────────────┘
                                    │
                              ┌─────┴─────┐
                              │ Per-feed   │ ← cached 600s per URL
                              │ Redis      │
                              └─────┬─────┘
                                    │
                                    ▼
                           ┌─────────────────────────┐
                           │  Categorized digest      │
                           │  Cached 900s (15 min)    │
                           │  Per-item keyword class. │
                           └─────────────────────────┘
```

**Cache Keys:**
- Digest: `news:digest:v1:{variant}:{lang}` (900s TTL)
- Per-feed: Individual URL (600s TTL)
- In-memory fallback: Capped at 50 entries (last-known-good data)

**Item Limits:**
- 5 items per feed
- 20 items per category

**XML Parsing:** Edge-runtime-compatible (regex-based, no DOM parser), handles both RSS `<item>` and Atom `<entry>`

### Tiered Caching Strategy

**Three-Layer Cache:**

| Layer | Scope | TTL | Key Format |
|-------|-------|-----|------------|
| **Redis — geo + metadata** | Seeded indices | 24 hours | `webcam:cameras:geo:{version}`, `webcam:cameras:meta:{version}` |
| **Redis — viewport responses** | Clustered map results | 24 hours | `webcam:resp:{version}:{zoom}:{quantizedBbox}` |
| **Redis — image lookups** | Per-webcam image/player URLs | 5 minutes | `webcam:image:{webcamId}` |
| **Client — image cache** | In-memory Map in browser | 9 minutes | webcamId |
| **Client — pinned store** | localStorage (permanent) | None (user-managed) | `wm-pinned-webcams` |

**Expected Latency Behavior:**
1. **First map viewport change:** Server performs Redis geo search, builds clustered response, caches (24h TTL). Subsequent identical viewports instant.
2. **First webcam click:** Server calls Windy API (external round-trip), caches for 5 min server-side. Client also caches for 9 min → re-clicking same webcam instant.
3. **Pinning webcam:** Iframe loads from Windy CDN (external round-trip). Browser handles iframe caching.

**Redis Ephemerality:** Data does not survive container rebuilds. After stack rebuild, seeder must re-run to repopulate indices.

### Source Credibility & Feed Tiering

**Tier Classification:**

| Tier | Description | Examples |
|------|-------------|----------|
| **Tier 1** | Wire services, official government | Reuters, AP, BBC, DOD |
| **Tier 2** | Major established outlets | CNN, NYT, The Guardian, Al Jazeera |
| **Tier 3** | Specialized/niche outlets | Defense One, Breaking Defense, The War Zone |
| **Tier 4** | Aggregators and blogs | Google News, individual analyst blogs |

**Flags:**
- **Propaganda risk rating**
- **State affiliation flag** (RT, Xinhua, IRNA visually tagged)

**Confidence Weighting:** Tier 1 breaking alert carries more weight than Tier 4 blog post in focal point detection algorithm

### Telegram OSINT Feed

**Architecture:** GramJS MTProto client on Railway relay

**26 Curated Channels:**

| Tier | Channels |
|------|----------|
| **Tier 1** | VahidOnline (Iran politics) |
| **Tier 2** | Abu Ali Express, Aurora Intel, BNO News, Clash Report, DeepState, Defender Dome, Iran International, LiveUAMap, OSINTdefender, OSINT Updates, Ukraine Air Force (kpszsu), Povitryani Tryvoha |
| **Tier 3** | Bellingcat, CyberDetective, GeopoliticalCenter, Middle East Spectator, Middle East Now Breaking, NEXTA, OSINT Industries, OsintOps News, OSINT Live, OsintTV, The Spectator Index, War Monitor, WFWitness |

**Polling:**
- 60-second cycle (sequential channel polling)
- 15-second timeout per channel
- 3-minute hard timeout for entire cycle
- Stuck-poll guard: Force-clear mutex after 3.5 minutes
- FLOOD_WAIT errors stop cycle early (don't propagate to remaining channels)

**Data Processing:**
- Deduplicated by message ID
- Filtered: Exclude media-only posts (images without text)
- Truncated: 800 characters max
- Buffer: Rolling 200-item window
- Startup delay: 60 seconds (prevents `AUTH_KEY_DUPLICATED` errors during Railway container restarts)

**Topic Classification:** breaking, conflict, alerts, osint, politics, middleeast (at query time via `/telegram/feed` relay endpoint)

### OREF Rocket Alert Integration

**Data Source:** Israel's Home Front Command (Pikud HaOref) alert system

**Challenge:** Akamai WAF protection blocks most programmatic access

**Bypass Method:** 
- `curl` (not Node.js fetch, which is JA3-blocked)
- Residential proxy with Israeli exit IP
- Polling every 5 minutes

**Bootstrap Strategy (2-phase):**
1. **Phase 1:** Load from Redis (filter entries >7 days old)
2. **Phase 2:** If Redis empty, fetch from upstream OREF API with exponential backoff (up to 3 attempts: 3s/6s/12s + jitter)

**Data Processing:**
- Alert history persisted to Redis with dirty-flag deduplication
- Wave detection: Group siren records by timestamp → identify distinct attack waves
- Timestamp conversion: Israel-local → UTC with DST-aware offset
- **1,480 Hebrew→English location translations:** Auto-generated dictionary from `pikud-haoref-api` `cities.json`
- Unicode bidirectional control characters stripped via `sanitizeHebrew()` before translation

**CII Integration:**
- Active alerts: `25 + min(25, alertCount × 5)` (up to +50 points)
- Rolling 24h history: 3-9 alerts → +5, 10+ → +10 to blended score
- Sustained multi-wave barrages drive Israel CII significantly higher than isolated alerts

### Learning Mode (15-Minute Warmup)

**Problem:** New users see flood of false-positive alerts during system calibration

**Solution:** 15-minute warmup period where scores calculated but alerts suppressed

**Why 15 minutes?** Real-world testing showed CII scores stabilize after 10-20 minutes of data collection.

**Behavior:**

```
Minutes 0-15: Learning Mode Active
  - CII scores calculated and displayed (dimmed 60% opacity)
  - Trend detection active (stores baseline)
  - All CII-related alerts suppressed
  - Progress bar fills as time elapses

After 15 minutes: Learning Complete
  - Full opacity scores
  - Alert generation enabled (threshold ≥10 point change)
  - "All data sources active" status shown
```

**Visual Indicators:**
- **CII Panel:** Yellow banner with progress bar and countdown timer
- **Strategic Risk Overview:** "Learning Mode - Xm until reliable" status
- **Score Display:** Scores at 60% opacity (dimmed)

**Note:** Server-side pre-computation now provides immediate scores to new users. Learning Mode primarily affects client-side dynamic adjustments and alert generation.

---

## 🎯 Features We Can Replicate

### Priority 1: Free & High-Value

1. **Cyber Threat Layer**
   - FREE sources: Feodo Tracker, URLhaus, C2IntelFeeds, AlienVault OTX, AbuseIPDB, Ransomware.live
   - Geolocation via ipinfo.io (50K/month free) + freeipapi.com fallback
   - 16 parallel enrichment, 12s timeout, 250 IPs/run
   - 10-min cache, 14-day rolling window, max 500 IOCs
   - **IMPLEMENT:** Color-coded scatter dots on globe, severity classification

2. **Natural Disaster Monitoring**
   - FREE sources: USGS (M4.5+ earthquakes), GDACS (UN alerts), NASA EONET
   - Haversine deduplication on 0.1° grid
   - GDACS Red/Orange only, EONET wildfires <48h
   - **IMPLEMENT:** Merged disaster layer with severity classification

3. **Dual-Source Protest Tracking**
   - FREE: ACLED (API key required) + GDELT (fully free)
   - Haversine deduplication, ACLED priority
   - Regime-aware scoring (log for democracies, linear for authoritarian)
   - **IMPLEMENT:** Protest severity heatmap with fatality overlay

4. **Security Advisory Aggregation**
   - FREE: 7 government advisory feeds (US/AU/UK/NZ) + 4 health agencies
   - Advisory level ranking (DNT → Reconsider → Caution)
   - Consensus bonus (≥3 governments → +5 points)
   - **IMPLEMENT:** Advisory panel with colored badges, country flags, severity filters

5. **GPS/GNSS Jamming Layer**
   - FREE: gpsjam.org (ADS-B analysis)
   - H3 hex grid, 3-aircraft minimum threshold
   - High (>10%) / Medium (2-10%) classification
   - 12 region tags
   - **IMPLEMENT:** Jamming heatmap with region filters

6. **Airport Delay Monitoring**
   - FREE: FAA ASWS (14 US hubs)
   - PARTIAL: AviationStack (500/month free tier for 40 international)
   - Severity thresholds: Minor (15min/15%) → Severe (60min/60%)
   - 30-min Redis cache
   - **IMPLEMENT:** Delay severity panel with probabilistic simulation fallback

7. **Climate Anomaly Detection**
   - FREE: Open-Meteo ERA5
   - 30-day baseline, 15 monitored zones
   - Extreme (>5°C / >80mm) / Moderate (>3°C / >40mm)
   - **IMPLEMENT:** Climate anomaly map with severity overlay

8. **Displacement Tracking**
   - FREE: UN OCHA HAPI
   - Origins (outflow) vs Hosts (intake)
   - Crisis badges: >1M (red), >500K (orange)
   - **IMPLEMENT:** Displacement panel with origin/host dual-view

9. **Prediction Markets**
   - FREE: Polymarket Gamma API (browser-direct bypass)
   - 4-tier fetch strategy (bootstrap → RPC → browser → Tauri)
   - Smart filtering: Exclude sports (100+ keywords), require volume >$50K
   - **IMPLEMENT:** Geopolitical markets panel with volume ranking

10. **Crypto Intelligence**
    - FREE: CoinGecko (50 calls/min), Yahoo Finance (unofficial)
    - BTC ETF flows, stablecoin peg health, Fear & Greed Index
    - **IMPLEMENT:** Crypto dashboard with sparklines, donut gauges

### Priority 2: Requires Paid APIs (Find Alternatives)

1. **Live Webcams**
   - ⚠️ Windy API (free tier but limited, 10-min token expiry, NOT live video)
   - **ALTERNATIVE:** YouTube Live streams (22 strategic locations already integrated)
   - **FUTURE:** US DOT 511 state traffic cameras (free with state keys, 30-60s refresh)

2. **AviationStack**
   - ⚠️ Free tier: 500 requests/month (40 airports → 12.5 requests/airport/month)
   - **ALTERNATIVE:** FAA ASWS (14 US hubs, fully free) + probabilistic simulation for international

3. **ICAO NOTAM**
   - ❌ Requires partnership/credentials
   - **ALTERNATIVE:** FAA ASWS for US, simulate NOTAM closures for MENA airports

### Priority 3: Complex but High-Impact

1. **Country Instability Index (CII)**
   - Combine ACLED + GDELT protests with regime-aware dampening
   - Log scaling for high-volume countries (bias prevention)
   - Conflict zone floor scores (Ukraine 55, Syria/Yemen 50, Myanmar/Israel 45)
   - Contextual boosts: Hotspot (+10), News urgency (+5), Focal point (+8)
   - **IMPLEMENT:** Real-time CII dashboard with trend detection (Rising/Stable/Falling)

2. **Strategic Risk Score**
   - Composite: Convergence (40%) + CII Deviation (35%) + Infrastructure (25%)
   - Weighted top-5 CII scores
   - Unified alert system: Temporal (2h), spatial (200km), country deduplication
   - Alert priority: Critical/High/Medium/Low
   - **IMPLEMENT:** Strategic Risk Overview with composite scoring

3. **Geographic Convergence Detection**
   - H3 hexagonal grid
   - Count event types per cell
   - Score: `event_types × 20` (capped at 100)
   - Classify: ≥80 Critical, ≥60 High, ≥40 Medium
   - **IMPLEMENT:** Convergence heatmap on globe

4. **Server-Side Feed Aggregation**
   - Single digest API vs 25+ individual feeds
   - 20 concurrent fetches, 8s timeout per feed, 25s overall deadline
   - Categorized digest cached 900s, per-feed cached 600s
   - In-memory fallback (50 entries)
   - **IMPLEMENT:** News digest API with keyword classification

5. **Telegram OSINT Feed**
   - GramJS MTProto client, 26 curated channels
   - 60s cycle, 15s timeout/channel, 3min hard timeout
   - Stuck-poll guard, FLOOD_WAIT early exit
   - Deduplication, media-only filtering, 800-char truncation
   - **IMPLEMENT:** OSINT panel with topic classification (breaking/conflict/alerts)

---

## ⚠️ Known Limitations & Workarounds

### Webcam Layer

**CRITICAL LIMITATION:** Windy does NOT provide live video streams. Most webcams are still images captured every 5-15 minutes. The "player" is a timelapse of recent snapshots (24-72 hours), not live.

**Workarounds:**
- Use YouTube Live for critical locations (22 strategic cities)
- US DOT 511 state traffic cameras (30-60s refresh, still images)
- OpenWebcamDB (2,052 cameras, 50 req/day free tier)
- TrafficLand (25K cameras with HLS, requires business coordination)

**Other Issues:**
- Image token URLs expire after 10 minutes → re-fetch needed
- Free tier attribution required
- Bounding-box queries capped at 10K/request → adaptive quadrant splitting needed
- No status filtering → offline cameras may show broken previews

### Redis Ephemerality

**Problem:** Redis data does not survive container rebuilds. After 24h TTL expiry or stack rebuild, webcam layer goes blank.

**Workarounds:**
- **Railway cron:** Schedule seeder every 12-18 hours (ahead of 24h TTL)
- Manual re-seed: Run `scripts/seed-webcams.mjs` or `scripts/run-seeders.sh`

### Polymarket Cloudflare JA3 Blocking

**Problem:** Cloudflare TLS fingerprinting blocks all server-side requests to Polymarket API.

**4-Tier Bypass:**
1. Bootstrap hydration (zero-network, Redis-cached)
2. Sebuf RPC (server-side Redis query)
3. **Browser-direct fetch** (browser TLS passes Cloudflare) ✅
4. Tauri native TLS (Rust `reqwest` fingerprint differs from Node.js)

**Implementation:** Use browser-direct fetch as primary, cache successful state, skip fallback tiers on subsequent requests.

### AviationStack Rate Limits

**Problem:** Free tier limited to 500 requests/month. 40 airports → 12.5 requests/airport/month.

**Workarounds:**
- Use FAA ASWS for 14 US hubs (fully free)
- Probabilistic simulated delays for international (demonstration mode)
- Cache results for 30 minutes

### ICAO NOTAM Access

**Problem:** Requires partnership/credentials, not publicly available.

**Workarounds:**
- FAA ASWS for US airports
- Simulate NOTAM closures for MENA airports (keyword-based detection from GDELT/ACLED)

---

## 📊 Data Formats & Schemas

### Cyber Threat IOC Format

```json
{
  "ioc": "192.0.2.1",
  "type": "c2_server" | "malware_host" | "phishing" | "malicious_url",
  "severity": 1 | 2 | 3 | 4,
  "source": "feodo" | "urlhaus" | "otx" | "abuseipdb" | "c2intelfeed" | "ransomware.live",
  "lat": 37.7749,
  "lng": -122.4194,
  "country": "US",
  "city": "San Francisco",
  "timestamp": "2025-03-23T23:00:00Z",
  "cache_ttl": 86400 // 24 hours
}
```

### Natural Disaster Event Format

```json
{
  "id": "usgs_earthquake_123",
  "type": "earthquake" | "flood" | "cyclone" | "volcano" | "wildfire" | "drought",
  "severity": "red" | "orange" | "green",
  "magnitude": 5.2, // For earthquakes
  "lat": 35.6762,
  "lng": 139.6503,
  "location": "Tokyo, Japan",
  "source": "USGS" | "GDACS" | "NASA_EONET",
  "timestamp": "2025-03-23T22:45:00Z",
  "dedupe_grid": "0.1deg" // Haversine 0.1° grid cell
}
```

### Protest Event Format

```json
{
  "id": "acled_protest_456",
  "type": "protest" | "riot" | "clash",
  "severity": "high" | "medium" | "low",
  "fatalities": 3,
  "lat": 50.4501,
  "lng": 30.5234,
  "country": "Ukraine",
  "city": "Kyiv",
  "source": "ACLED" | "GDELT",
  "validated": true, // ACLED priority or GDELT mention ≥30
  "timestamp": "2025-03-23T20:00:00Z",
  "regime_type": "democratic" | "authoritarian",
  "scaling": "logarithmic" | "linear"
}
```

### Security Advisory Format

```json
{
  "country": "Ukraine",
  "level": 4, // Do-Not-Travel (4) → Reconsider (3) → Caution (2) → Normal (1) → Info (0)
  "level_text": "Do Not Travel",
  "sources": ["US", "AU", "UK"], // Government codes
  "consensus_bonus": 5, // ≥3 governments → +5, ≥2 → +3
  "cii_boost": 15, // Do-Not-Travel → +15, Reconsider → +10, Caution → +5
  "cii_floor": 60, // DNT forces min 60, Reconsider forces min 50
  "timestamp": "2025-03-23T18:00:00Z"
}
```

### GPS Jamming Format

```json
{
  "h3_cell": "844c89fffffffff",
  "level": "high" | "medium" | "low",
  "bad_aircraft_pct": 15.3,
  "total_aircraft": 47,
  "bad_aircraft": 7,
  "region": "Levant" | "Ukraine-Russia" | "Baltic" | ...,
  "lat": 31.7683, // H3 cell centroid
  "lng": 35.2137,
  "country": "Israel",
  "cii_contribution": 35, // High × 5 = 5, capped at 35
  "timestamp": "2025-03-23T23:00:00Z"
}
```

### CII Score Format

```json
{
  "country": "Ukraine",
  "score": 87,
  "level": "critical" | "high" | "elevated" | "normal" | "low",
  "trend": "rising" | "stable" | "falling",
  "change_24h": 12, // +12 points in 24 hours
  "components": {
    "unrest": 65, // 40% weight
    "security": 42, // 30% weight
    "information": 78 // 30% weight
  },
  "boosts": {
    "hotspot": 10,
    "news_urgency": 5,
    "focal_point": 8
  },
  "floor": 55, // Conflict zone floor
  "baseline": 50, // Static baseline
  "event_score": 124, // Before boosts/floors
  "final_cii": 87, // After all adjustments
  "timestamp": "2025-03-23T23:00:00Z"
}
```

### Webcam Format

```json
{
  "webcamId": "1234567890",
  "title": "Jerusalem - Western Wall",
  "lat": 31.7767,
  "lng": 35.2345,
  "country": "Israel",
  "region": "Jerusalem District",
  "category": "city" | "traffic" | "landscape" | "beach" | ...,
  "status": "active" | "inactive",
  "preview_url": "https://images.windy.com/...", // Expires 10 min
  "thumbnail_url": "https://images.windy.com/...",
  "player_url": "https://www.windy.com/webcams/...",
  "lastUpdated": "2025-03-23T22:50:00Z",
  "timelapse_hours": 72, // NOT live video
  "cache_ttl": 300 // 5 minutes
}
```

---

## 🔑 Key Takeaways for Atlas Intel

### What to Build Immediately

1. **Cyber Threat Layer:** 6 free sources, ipinfo.io geolocation, 10-min cache, color-coded severity dots
2. **Natural Disaster Monitoring:** USGS + GDACS + NASA EONET, Haversine deduplication, severity filtering
3. **Dual-Source Protest Tracking:** ACLED + GDELT, regime-aware scoring, fatality overlay
4. **Security Advisory Panel:** 7 government feeds, advisory level ranking, consensus bonus
5. **GPS Jamming Heatmap:** gpsjam.org, H3 hex grid, region tagging
6. **Airport Delay Panel:** FAA ASWS (14 US hubs), probabilistic simulation for international
7. **Climate Anomaly Map:** Open-Meteo ERA5, 30-day baseline, severity classification
8. **Prediction Markets:** Polymarket browser-direct fetch, smart filtering, volume ranking

### Architecture Patterns to Adopt

1. **Server-Side Aggregation:** Single digest API vs per-client feed fan-out
2. **Tiered Caching:** Redis (geo/metadata/viewport) + client (in-memory) + localStorage
3. **Dual-Source Validation:** ACLED + GDELT, USGS + GDACS + EONET
4. **Haversine Deduplication:** 0.1° grid (~10km) for protest/disaster events
5. **Regime-Aware Scoring:** Log dampening for democracies, linear for authoritarian states
6. **Learning Mode:** 15-min warmup to suppress false-positive alerts
7. **Source Tiering:** Tier 1 (wire services) > Tier 2 (major outlets) > Tier 3 (specialized) > Tier 4 (aggregators)
8. **Cloudflare JA3 Bypass:** Browser-direct fetch for Polymarket, Tauri native TLS fallback

### Algorithms to Implement

1. **CII Scoring:** Unrest (40%) + Security (30%) + Information (30%) with log scaling, floor scores, contextual boosts
2. **Strategic Risk:** Convergence (40%) + CII Deviation (35%) + Infrastructure (25%)
3. **Geographic Convergence:** H3 hex grid, event type counting, score = `types × 20` (capped 100)
4. **Alert Deduplication:** Temporal (2h), spatial (200km), country-based merging
5. **Trend Detection:** ±5 point threshold for rising/stable/falling classification

### Data Sources to Avoid (Paid/Complex)

1. **ICAO NOTAM:** Requires partnership → Use FAA ASWS + simulation
2. **AviationStack (beyond free tier):** 500/month limit → Use FAA + simulation
3. **Live video webcams:** Windy only provides timelapse stills → Use YouTube Live
4. **TrafficLand:** 25K cameras but requires business coordination → Future phase

### Free API Keys Needed

| Service | Free Tier | Key URL |
|---------|-----------|---------|
| **ACLED** | Daily updates | https://developer.acleddata.com/ |
| **AlienVault OTX** | 1000s of IOCs | https://otx.alienvault.com/api |
| **AbuseIPDB** | 1000 requests/day | https://www.abuseipdb.com/api |
| **ipinfo.io** | 50,000 requests/month | https://ipinfo.io/signup |
| **Windy Webcams** | 10,000 results/request | https://api.windy.com/ |
| **AviationStack** | 500 requests/month | https://aviationstack.com/product |
| **CoinGecko** | 50 calls/min | https://www.coingecko.com/en/api |

### No API Key Required (Fully Free)

- USGS Earthquakes
- GDACS
- NASA EONET
- GDELT
- UCDP
- gpsjam.org
- FAA ASWS
- Open-Meteo ERA5
- UN OCHA HAPI
- Yahoo Finance (unofficial)
- Feodo Tracker
- URLhaus
- C2IntelFeeds
- Ransomware.live
- Government advisory RSS feeds
- Health agency RSS feeds

---

## 📝 Implementation Roadmap

### Phase 1: Core Intelligence Layers (Week 1-2)

1. ✅ Set up Redis caching infrastructure (tiered: geo/viewport/image/client)
2. ✅ Implement Cyber Threat Layer (6 sources, ipinfo.io geolocation, 10-min cache)
3. ✅ Implement Natural Disaster Layer (USGS + GDACS + EONET, Haversine dedup)
4. ✅ Implement Dual-Source Protest Tracking (ACLED + GDELT, regime-aware scoring)
5. ✅ Implement Security Advisory Panel (7 gov feeds, advisory ranking, consensus bonus)
6. ✅ Implement GPS Jamming Layer (gpsjam.org, H3 hex grid, region tagging)

### Phase 2: Risk Scoring & Convergence (Week 3-4)

1. ✅ Implement CII scoring algorithm (Unrest + Security + Information components)
2. ✅ Implement log scaling for high-volume countries (bias prevention)
3. ✅ Implement conflict zone floor scores (Ukraine 55, Syria/Yemen 50, etc.)
4. ✅ Implement contextual boosts (Hotspot +10, News urgency +5, Focal point +8)
5. ✅ Implement Geographic Convergence Detection (H3 grid, event type counting)
6. ✅ Implement Strategic Risk Score (Convergence 40% + CII Deviation 35% + Infrastructure 25%)

### Phase 3: Infrastructure Monitoring (Week 5-6)

1. ✅ Implement Airport Delay Panel (FAA ASWS for US, probabilistic simulation for international)
2. ✅ Implement Climate Anomaly Detection (Open-Meteo ERA5, 30-day baseline)
3. ✅ Implement Displacement Tracking (UN OCHA HAPI, origin/host dual-view)
4. ✅ Implement Prediction Markets (Polymarket browser-direct fetch, smart filtering)
5. ✅ Implement Crypto Intelligence (CoinGecko + Yahoo Finance, sparklines, donut gauges)

### Phase 4: Advanced Features (Week 7-8)

1. ✅ Implement Server-Side Feed Aggregation (single digest API, 20 concurrent fetches)
2. ✅ Implement Telegram OSINT Feed (GramJS MTProto, 26 channels, topic classification)
3. ✅ Implement Unified Alert System (temporal/spatial/country deduplication)
4. ✅ Implement Learning Mode (15-min warmup, alert suppression, dimmed scores)
5. ✅ Implement Webcam Layer (Windy API, YouTube Live fallback, pinned panel)

### Phase 5: Optimization & Polish (Week 9-10)

1. ✅ Set up Railway cron for periodic seeding (webcams, advisories, OSINT)
2. ✅ Implement in-memory fallback caches (50 entries, last-known-good data)
3. ✅ Implement source credibility tiering (Tier 1-4, propaganda flags)
4. ✅ Implement trend detection (Rising/Stable/Falling, ±5 point threshold)
5. ✅ Implement alert priority classification (Critical/High/Medium/Low)

---

## 🔗 Reference URLs

- **World Monitor Docs:** https://worldmonitor.app/docs/
- **ACLED API:** https://developer.acleddata.com/
- **GDELT:** http://data.gdeltproject.org/
- **USGS Earthquakes:** https://earthquake.usgs.gov/earthquakes/feed/
- **GDACS:** https://www.gdacs.org/
- **NASA EONET:** https://eonet.gsfc.nasa.gov/
- **gpsjam.org:** https://gpsjam.org/
- **FAA ASWS:** https://nasstatus.faa.gov/
- **Open-Meteo:** https://open-meteo.com/
- **UN OCHA HAPI:** https://hapi.humdata.org/
- **Windy Webcams API:** https://api.windy.com/webcams/docs
- **ipinfo.io:** https://ipinfo.io/
- **AlienVault OTX:** https://otx.alienvault.com/
- **AbuseIPDB:** https://www.abuseipdb.com/
- **Feodo Tracker:** https://feodotracker.abuse.ch/
- **URLhaus:** https://urlhaus.abuse.ch/
- **CoinGecko:** https://www.coingecko.com/en/api
- **Polymarket Gamma API:** https://gamma-api.polymarket.com/

---

**End of Intelligence Extract**
