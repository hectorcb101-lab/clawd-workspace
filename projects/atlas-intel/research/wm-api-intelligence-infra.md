# World Monitor API Reference: Intelligence & Infrastructure Services

**Compiled:** 2026-03-23  
**Total Endpoints:** 23 (14 Intelligence, 9 Infrastructure)  
**Source:** https://worldmonitor.app/docs/api-reference/

---

## Table of Contents

### Intelligence Service (14 endpoints)
1. [ClassifyEvent](#1-classifyevent)
2. [DeductSituation](#2-deductsituation)
3. [GetCompanyEnrichment](#3-getcompanyenrichment)
4. [GetCountryFacts](#4-getcountryfacts)
5. [GetCountryIntelBrief](#5-getcountryintelbrief)
6. [GetGdeltTopicTimeline](#6-getgdelttopictimeline)
7. [GetPizzintStatus](#7-getpizzintstatus)
8. [GetRiskScores](#8-getriskscores)
9. [ListCompanySignals](#9-listcompanysignals)
10. [ListGpsInterference](#10-listgpsinterference)
11. [ListOrefAlerts](#11-listorefalerts)
12. [ListSatellites](#12-listsatellites)
13. [ListSecurityAdvisories](#13-listsecurityadvisories)
14. [ListTelegramFeed](#14-listtelegramfeed)

### Infrastructure Service (9 endpoints)
15. [GetBootstrapData](#15-getbootstrapdata)
16. [GetCableHealth](#16-getcablehealth)
17. [GetIpGeo](#17-getipgeo)
18. [GetTemporalBaseline](#18-gettemporalbaseline)
19. [ListInternetDdosAttacks](#19-listinternetddosattacks)
20. [ListInternetOutages](#20-listinternetoutages)
21. [ListInternetTrafficAnomalies](#21-listinternettrafficanomalies)
22. [ListServiceStatuses](#22-listservicestatuses)
23. [ListTemporalAnomalies](#23-listtemporalanomalies)

---

## Intelligence Service Endpoints

### 1. ClassifyEvent

**RPC:** `IntelligenceService.ClassifyEvent`  
**Method:** GET  
**Path:** `/api/intelligence/v1/classify-event`  
**Description:** Analyzes a news event using AI models.

**Request Parameters:**
- `title` (string, optional) — Event title or headline
- `description` (string, optional) — Event description or body text
- `source` (string, optional) — Event source (e.g., "reuters", "acled")
- `country` (string, optional) — Country context (ISO 3166-1 alpha-2)

**Response Schema:** `ClassifyEventResponse`
```yaml
classification:
  category: string          # e.g., "military", "economic", "social"
  subcategory: string
  severity: enum            # SEVERITY_LEVEL_LOW | MEDIUM | HIGH
  confidence: number        # 0.0 to 1.0
  analysis: string          # Brief AI-generated analysis
  entities: array<string>   # Related entities identified
```

**Upstream Data Source:** AI model (internal LLM inference)  
**Free/Paid:** Not specified (likely API-key gated)  
**Caching:** Not specified  
**Algorithms:** AI classification model (NLP-based event taxonomy)

---

### 2. DeductSituation

**RPC:** `IntelligenceService.DeductSituation`  
**Method:** POST  
**Path:** `/api/intelligence/v1/deduct-situation`  
**Description:** Performs broad situational analysis using LLMs.

**Request Body:**
```yaml
query: string         # Analysis query
geoContext: string    # Geographic context
```

**Response Schema:** `DeductSituationResponse`
```yaml
analysis: string      # AI-generated situational analysis
model: string         # Model used for generation
provider: string      # AI provider
```

**Upstream Data Source:** LLM provider (unspecified, likely OpenAI/Anthropic/Google)  
**Free/Paid:** Not specified (likely paid LLM inference)  
**Caching:** Not specified  
**Algorithms:** Situational reasoning via LLM prompting

---

### 3. GetCompanyEnrichment

**RPC:** `IntelligenceService.GetCompanyEnrichment`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-company-enrichment`  
**Description:** Aggregates company data from multiple public sources (GitHub, SEC, HN).

**Request Parameters:**
- `domain` (string, optional) — Company domain
- `name` (string, optional) — Company name

**Response Schema:** `GetCompanyEnrichmentResponse`
```yaml
company:
  name: string
  domain: string
  description: string
  location: string
  website: string
  founded: int32

github:
  publicRepos: int32
  followers: int32
  avatarUrl: string

techStack: array
  - name: string
    category: string
    confidence: float

secFilings:
  totalFilings: int32
  recentFilings: array
    - form: string
      fileDate: string
      description: string

hackerNewsMentions: array
  - title: string
    url: string
    points: int32
    comments: int32
    createdAtMs: int64

enrichedAtMs: int64
sources: array<string>  # Successfully reached sources
```

**Upstream Data Sources:**
- **GitHub API** (FREE: public repos, org data)
- **SEC EDGAR API** (FREE: public filings)
- **Hacker News Algolia API** (FREE: mentions, discussions)

**Free/Paid:** All upstream sources are FREE  
**Caching:** Yes (evidenced by `enrichedAtMs` timestamp)  
**Algorithms:** Multi-source aggregation, tech stack inference (likely from GitHub repo languages/dependencies)

---

### 4. GetCountryFacts

**RPC:** `IntelligenceService.GetCountryFacts`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-country-facts`  
**Description:** Retrieves factual country data from RestCountries and Wikipedia.

**Request Parameters:**
- `country_code` (string, optional) — ISO 3166-1 alpha-2

**Response Schema:** `GetCountryFactsResponse`
```yaml
headOfState: string
headOfStateTitle: string
wikipediaSummary: string
wikipediaThumbnailUrl: string
population: int64
capital: string
languages: array<string>
currencies: array<string>
areaSqKm: double
countryName: string
```

**Upstream Data Sources:**
- **RestCountries API** (FREE: population, capital, languages, currencies, area)
- **Wikipedia API** (FREE: head of state, summary, thumbnail)

**Free/Paid:** All FREE  
**Caching:** Not specified (likely cached due to static nature)  
**Algorithms:** REST API aggregation

---

### 5. GetCountryIntelBrief

**RPC:** `IntelligenceService.GetCountryIntelBrief`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-country-intel-brief`  
**Description:** Generates a strategic brief for a specific country.

**Request Parameters:**
- `country_code` (string, optional) — ISO 3166-1 alpha-2

**Response Schema:** `GetCountryIntelBriefResponse`
```yaml
countryCode: string
countryName: string
brief: string         # AI-generated intelligence brief text
model: string         # AI model used for generation
generatedAt: int64    # Unix epoch milliseconds
```

**Upstream Data Source:** LLM (AI generation)  
**Free/Paid:** Likely paid (LLM inference cost)  
**Caching:** Likely cached (indicated by `generatedAt` timestamp)  
**Algorithms:** LLM-based intelligence synthesis

---

### 6. GetGdeltTopicTimeline

**RPC:** `IntelligenceService.GetGdeltTopicTimeline`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-gdelt-topic-timeline`  
**Description:** Retrieves tone and volume timelines for a GDELT intel topic.

**Request Parameters:**
- `topic` (string, optional) — Topic ID: military, cyber, nuclear, sanctions, intelligence, maritime

**Response Schema:** `GetGdeltTopicTimelineResponse`
```yaml
topic: string
tone: array<GdeltTimelinePoint>
  - date: string       # e.g., "20240101T000000"
    value: double      # Tone value
vol: array<GdeltTimelinePoint>
  - date: string
    value: double      # Volume value
fetchedAt: string      # ISO timestamp
error: string          # Error message if fetch failed
```

**Upstream Data Source:** **GDELT Project** (FREE: global event database)  
**Free/Paid:** FREE (GDELT is open data)  
**Caching:** Yes (indicated by `fetchedAt`)  
**Algorithms:** GDELT tone/volume extraction for predefined topics

---

### 7. GetPizzintStatus

**RPC:** `IntelligenceService.GetPizzintStatus`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-pizzint-status`  
**Description:** Retrieves Pentagon Pizza Index and GDELT tension data.

**Request Parameters:**
- `include_gdelt` (boolean, optional) — Include GDELT tension pairs

**Response Schema:** `GetPizzintStatusResponse`
```yaml
pizzint:
  defconLevel: int32           # 1-5
  defconLabel: string
  aggregateActivity: double
  activeSpikes: int32
  locationsMonitored: int32
  locationsOpen: int32
  updatedAt: int64
  dataFreshness: enum          # FRESH | STALE
  locations: array<PizzintLocation>
    - placeId: string          # Google Places ID
      name: string
      address: string
      currentPopularity: int32  # 0-200+
      percentageOfUsual: int32
      isSpike: boolean
      spikeMagnitude: double
      dataSource: string
      recordedAt: string       # ISO 8601
      dataFreshness: enum
      isClosedNow: boolean
      lat: double
      lng: double

tensionPairs: array<GdeltTensionPair>
  - id: string
    countries: array<string>   # ISO 3166-1 alpha-2
    label: string              # e.g., "US-China"
    score: double              # 0-100
    trend: enum                # RISING | STABLE | FALLING
    changePercent: double
    region: string
```

**Upstream Data Sources:**
- **Google Places API** (PAID: live popularity data for DC pizza locations)
- **GDELT Project** (FREE: bilateral tension scores)

**Free/Paid:** Mixed (Google Places = PAID, GDELT = FREE)  
**Caching:** Yes (indicated by `updatedAt`, `dataFreshness`)  
**Algorithms:** 
- Pizza Index: Live popularity monitoring + spike detection (z-score/baseline comparison)
- GDELT tension: Bilateral event aggregation

---

### 8. GetRiskScores

**RPC:** `IntelligenceService.GetRiskScores`  
**Method:** GET  
**Path:** `/api/intelligence/v1/get-risk-scores`  
**Description:** Retrieves composite risk scores and strategic assessments.

**Request Parameters:**
- `region` (string, optional) — Optional region filter (returns all if empty)

**Response Schema:** `GetRiskScoresResponse`
```yaml
ciiScores: array<CiiScore>
  - region: string
    staticBaseline: double     # 0-100
    dynamicScore: double       # 0-100
    combinedScore: double      # 0-100
    trend: enum                # RISING | STABLE | FALLING
    components:
      newsActivity: double     # 0-100
      ciiContribution: double  # 0-100
      geoConvergence: double   # 0-100
      militaryActivity: double # 0-100
    computedAt: int64

strategicRisks: array<StrategicRisk>
  - region: string
    level: enum                # SEVERITY_LEVEL_LOW | MEDIUM | HIGH
    score: double              # 0-100
    factors: array<string>
    trend: enum
```

**Upstream Data Source:** Internal composite index (aggregates news, GDELT, military activity)  
**Free/Paid:** Not specified (likely uses free sources internally)  
**Caching:** Yes (indicated by `computedAt`)  
**Algorithms:** Composite Instability Index (CII) — weighted combination of:
- News activity volume
- GDELT event density
- Geographic convergence (clustered events)
- Military activity signals

---

### 9. ListCompanySignals

**RPC:** `IntelligenceService.ListCompanySignals`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-company-signals`  
**Description:** Discovers activity signals for a company from public sources.

**Request Parameters:**
- `company` (string, optional)
- `domain` (string, optional)

**Response Schema:** `ListCompanySignalsResponse`
```yaml
company: string
domain: string
signals: array<CompanySignal>
  - type: string               # "Hiring", "Product Launch", "Expansion"
    title: string
    url: string
    source: string
    sourceTier: int32          # 1 = authoritative, 5 = low confidence
    timestampMs: int64
    strength: string           # "Strong", "Emerging"
    engagement:
      points: int32
      comments: int32
      stars: int32
      forks: int32
      mentions: int32

summary:
  totalSignals: int32
  byType: map<string, int32>
  strongestSignal: CompanySignal
  signalDiversity: int32

discoveredAtMs: int64
```

**Upstream Data Sources:**
- **GitHub API** (FREE: stars, forks, releases)
- **Hacker News** (FREE: mentions, engagement)
- **LinkedIn/Glassdoor** (likely scraped or API access if available)
- **Product Hunt** (FREE API: launches, upvotes)

**Free/Paid:** Mostly FREE (public APIs)  
**Caching:** Yes (indicated by `discoveredAtMs`)  
**Algorithms:** 
- Signal classification (NLP/keyword-based)
- Source tier ranking (data quality assessment)
- Engagement aggregation

---

### 10. ListGpsInterference

**RPC:** `IntelligenceService.ListGpsInterference`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-gps-interference`  
**Description:** Retrieves detected GPS/GNSS interference data (jamming).

**Request Parameters:**
- `region` (string, optional) — Optional region filter

**Response Schema:** `ListGpsInterferenceResponse`
```yaml
hexes: array<GpsJamHex>
  - h3: string (required)      # H3 index
    lat: double
    lon: double
    level: enum                # LOW | MEDIUM | HIGH
    npAvg: double              # Avg Navigation Precision (lower = more interference)
    sampleCount: int32
    aircraftCount: int32       # Unique aircraft reporting in hex

stats:
  totalHexes: int32
  highCount: int32
  mediumCount: int32

source: string
fetchedAt: int64
```

**Upstream Data Source:** **ADS-B Exchange / OpenSky Network** (FREE: aircraft transponder data with GPS precision metrics)  
**Free/Paid:** FREE  
**Caching:** Yes (indicated by `fetchedAt`)  
**Algorithms:**
- H3 hexagonal binning (geospatial aggregation)
- Navigation Precision (NP) averaging
- Interference level classification (thresholds on NP)

---

### 11. ListOrefAlerts

**RPC:** `IntelligenceService.ListOrefAlerts`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-oref-alerts`  
**Description:** Retrieves Israeli Home Front Command alerts (Red Alerts).

**Request Parameters:**
- `mode` (string, optional) — MODE_UNSPECIFIED defaults to active alerts

**Response Schema:** `ListOrefAlertsResponse`
```yaml
configured: boolean
alerts: array<OrefAlert>
  - id: string
    cat: string
    title: string
    data: array<string>
    desc: string
    timestampMs: int64

history: array<OrefWave>
  - alerts: array<OrefAlert>
    timestampMs: int64

historyCount24h: int32
totalHistoryCount: int32
timestampMs: int64
error: string
```

**Upstream Data Source:** **Israeli Home Front Command (Oref)** — Real-time alert API (FREE, public safety data)  
**Free/Paid:** FREE  
**Caching:** Not specified (likely real-time with historical buffering)  
**Algorithms:** Wave detection (temporal clustering of concurrent alerts)

---

### 12. ListSatellites

**RPC:** `IntelligenceService.ListSatellites`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-satellites`  
**Description:** Retrieves current orbital positions and metadata.

**Request Parameters:**
- `country` (string, optional) — Filter by country code (returns all if empty)

**Response Schema:** `ListSatellitesResponse`
```yaml
satellites: array<Satellite>
  - id: string (required)      # NORAD identifier (e.g., "25544")
    name: string
    country: string            # ISO country code
    type: string               # "sar", "optical", "military"
    alt: double                # Altitude in km
    velocity: double           # km/s
    inclination: double        # degrees
    line1: string              # TLE line 1
    line2: string              # TLE line 2
```

**Upstream Data Source:** **Space-Track.org / CelesTrak** (FREE: NORAD Two-Line Element sets)  
**Free/Paid:** FREE (requires Space-Track.org account for bulk access)  
**Caching:** Likely cached (TLEs updated daily/hourly)  
**Algorithms:** TLE parsing, orbital propagation (SGP4/SDP4)

---

### 13. ListSecurityAdvisories

**RPC:** `IntelligenceService.ListSecurityAdvisories`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-security-advisories`  
**Description:** Retrieves pre-seeded travel and health advisories.

**Request Parameters:** None

**Response Schema:** `ListSecurityAdvisoriesResponse`
```yaml
advisories: array<SecurityAdvisoryItem>
  - title: string
    link: string
    pubDate: string
    source: string
    sourceCountry: string
    level: string
    country: string

byCountry: map<string, string>
```

**Upstream Data Sources:**
- **UK FCDO Travel Advice** (FREE: RSS feed)
- **US State Dept Travel Advisories** (FREE: API/RSS)
- **CDC Health Notices** (FREE: RSS)

**Free/Paid:** FREE  
**Caching:** Yes (indicated by "pre-seeded")  
**Algorithms:** RSS/API aggregation, country mapping

---

### 14. ListTelegramFeed

**RPC:** `IntelligenceService.ListTelegramFeed`  
**Method:** GET  
**Path:** `/api/intelligence/v1/list-telegram-feed`  
**Description:** Retrieves real-time OSINT messages from monitored Telegram channels.

**Request Parameters:**
- `limit` (int32, optional) — Max messages to return (default 50)
- `topic` (string, optional) — Filter by topic (e.g., "military", "cyber")
- `channel` (string, optional) — Filter by channel ID or name

**Response Schema:** `ListTelegramFeedResponse`
```yaml
enabled: boolean
messages: array<TelegramMessage>
  - id: string
    channelId: string
    channelName: string
    text: string               # Sanitized message content
    timestampMs: int64
    mediaUrls: array<string>   # Images, videos
    sourceUrl: string          # Link to original post
    topic: string              # Auto-classified topic

count: int32
error: string
```

**Upstream Data Source:** **Telegram Bot API / MTProto** (FREE for bots, requires API credentials)  
**Free/Paid:** FREE (requires Telegram API setup)  
**Caching:** Not specified (likely real-time with buffering)  
**Algorithms:**
- Content sanitization
- Topic classification (NLP-based keyword matching or ML classifier)

---

## Infrastructure Service Endpoints

### 15. GetBootstrapData

**RPC:** `InfrastructureService.GetBootstrapData`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/get-bootstrap-data`  
**Description:** Fetches multiple data points from the system cache in a single call.

**Request Parameters:**
- `tier` (string, optional) — Predefined tiers or specific keys
- `keys` (string, optional)

**Response Schema:** `GetBootstrapDataResponse`
```yaml
data: map<string, string>     # Keys to JSON-encoded data strings
missing: array<string>         # Keys not found in cache
```

**Upstream Data Source:** Internal cache (aggregates multiple endpoints)  
**Free/Paid:** N/A (caching layer)  
**Caching:** Yes (entire purpose is cache retrieval)  
**Algorithms:** Cache key-value lookup

---

### 16. GetCableHealth

**RPC:** `InfrastructureService.GetCableHealth`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/get-cable-health`  
**Description:** Computes health status for submarine cables from NGA maritime warning signals.

**Request Parameters:** None

**Response Schema:** `GetCableHealthResponse`
```yaml
generatedAt: int64
cables: map<string, CableHealthRecord>
  - status: enum               # OK | DEGRADED | FAULT
    score: double              # 0.0 = healthy, 1.0 = fault
    confidence: double         # 0.0–1.0
    lastUpdated: int64
    evidence: array<CableHealthEvidence>
      - source: string         # "NGA"
        summary: string
        ts: int64
```

**Upstream Data Source:** **NGA (National Geospatial-Intelligence Agency) Maritime Safety Warnings** (FREE: public NAVAREA warnings)  
**Free/Paid:** FREE  
**Caching:** Yes (indicated by `generatedAt`)  
**Algorithms:**
- Maritime warning parsing (NAVAREA/NAVTEX)
- Cable proximity analysis (geographic matching)
- Health scoring (evidence aggregation)

---

### 17. GetIpGeo

**RPC:** `InfrastructureService.GetIpGeo`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/get-ip-geo`  
**Description:** Retrieves geographic information based on the caller's IP address.

**Request Parameters:** None (uses caller's IP)

**Response Schema:** `GetIpGeoResponse`
```yaml
country: string               # ISO 3166-1 alpha-2
region: string                # Region or city
city: string
```

**Upstream Data Source:** **MaxMind GeoLite2** or **Cloudflare IP Geolocation** (FREE: GeoLite2, Cloudflare Workers)  
**Free/Paid:** FREE  
**Caching:** Not specified (geolocation is fast, likely minimal caching)  
**Algorithms:** IP-to-geo database lookup

---

### 18. GetTemporalBaseline

**RPC:** `InfrastructureService.GetTemporalBaseline`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/get-temporal-baseline`  
**Description:** Retrieves historical baseline data for a specific signal.

**Request Parameters:**
- `type` (string, optional) — Activity type: military_flights, vessels, protests, news, ais_gaps, satellite_fires
- `region` (string, optional) — Geographic region (default "global")
- `count` (double, optional) — Current observed count to compare against baseline

**Response Schema:** `GetTemporalBaselineResponse`
```yaml
anomaly:
  zScore: double               # Std deviations from mean
  severity: string             # "critical", "high", "medium", "normal"
  multiplier: double           # Current/baseline ratio

baseline:
  mean: double
  stdDev: double
  sampleCount: int32

learning: boolean              # True if insufficient samples
sampleCount: int32
samplesNeeded: int32
error: string
```

**Upstream Data Source:** Internal historical database (aggregates observations over time)  
**Free/Paid:** N/A (internal service)  
**Caching:** Yes (baseline statistics are incrementally updated)  
**Algorithms:**
- **Welford's online algorithm** (running mean/variance calculation)
- **Z-score anomaly detection**
- Severity classification (thresholds on z-score)

---

### 19. ListInternetDdosAttacks

**RPC:** `InfrastructureService.ListInternetDdosAttacks`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/list-internet-ddos-attacks`  
**Description:** Retrieves L3/L4 DDoS attack summaries from Cloudflare Radar.

**Request Parameters:** None

**Response Schema:** `ListInternetDdosAttacksResponse`
```yaml
protocol: array<DdosAttackSummaryEntry>
  - label: string              # "TCP", "UDP"
    percentage: float          # 0–100

vector: array<DdosAttackSummaryEntry>
  - label: string              # "networkFlood"
    percentage: float

dateRangeStart: string         # ISO 8601
dateRangeEnd: string

topTargetLocations: array<DdosLocationHit>
  - countryCode: string
    countryName: string
    percentage: float          # 0-100
    latitude: float
    longitude: float
```

**Upstream Data Source:** **Cloudflare Radar API** (FREE: DDoS attack telemetry)  
**Free/Paid:** FREE  
**Caching:** Likely cached (indicated by date range)  
**Algorithms:** Protocol/vector breakdown aggregation

---

### 20. ListInternetOutages

**RPC:** `InfrastructureService.ListInternetOutages`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/list-internet-outages`  
**Description:** Retrieves detected internet outages from Cloudflare Radar.

**Request Parameters:**
- `start` (int64, optional) — Unix epoch milliseconds
- `end` (int64, optional) — Unix epoch milliseconds
- `page_size` (int32, optional)
- `cursor` (string, optional)
- `country` (string, optional) — ISO 3166-1 alpha-2

**Response Schema:** `ListInternetOutagesResponse`
```yaml
outages: array<InternetOutage>
  - id: string (required)
    title: string
    link: string
    description: string
    detectedAt: int64
    country: string
    region: string
    location:
      latitude: double         # -90 to 90
      longitude: double        # -180 to 180
    severity: enum             # PARTIAL | MAJOR | TOTAL
    categories: array<string>
    cause: string
    outageType: string
    endedAt: int64             # 0 if ongoing

pagination:
  nextCursor: string
  totalCount: int32
```

**Upstream Data Source:** **Cloudflare Radar API** (FREE: outage detection)  
**Free/Paid:** FREE  
**Caching:** Not specified (likely minimal for real-time data)  
**Algorithms:** BGP route withdrawal detection, traffic drop analysis

---

### 21. ListInternetTrafficAnomalies

**RPC:** `InfrastructureService.ListInternetTrafficAnomalies`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/list-internet-traffic-anomalies`  
**Description:** Retrieves traffic anomaly events from Cloudflare Radar.

**Request Parameters:**
- `country` (string, optional) — ISO 3166-1 alpha-2 filter

**Response Schema:** `ListInternetTrafficAnomaliesResponse`
```yaml
anomalies: array<TrafficAnomaly>
  - uuid: string
    type: string               # "ANOMALY_DNS", "ANOMALY_BGP"
    status: string             # "ONGOING" | "HISTORICAL"
    startDate: int64
    endDate: int64             # 0 if ongoing
    asn: string
    asnName: string
    locationCode: string       # ISO 3166-1 alpha-2
    locationName: string
    latitude: float
    longitude: float

totalCount: int32
```

**Upstream Data Source:** **Cloudflare Radar API** (FREE: traffic anomaly detection)  
**Free/Paid:** FREE  
**Caching:** Not specified  
**Algorithms:** DNS/BGP anomaly detection (Cloudflare's internal ML models)

---

### 22. ListServiceStatuses

**RPC:** `InfrastructureService.ListServiceStatuses`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/list-service-statuses`  
**Description:** Retrieves operational status of monitored external services.

**Request Parameters:**
- `status` (string, optional) — Filter by status

**Response Schema:** `ListServiceStatusesResponse`
```yaml
statuses: array<ServiceStatus>
  - id: string
    name: string
    status: enum               # OPERATIONAL | DEGRADED | PARTIAL_OUTAGE | MAJOR_OUTAGE | MAINTENANCE
    description: string
    url: string
    checkedAt: int64
    latencyMs: int32
```

**Upstream Data Source:** Internal uptime monitoring (ping/HTTP checks)  
**Free/Paid:** N/A (internal service)  
**Caching:** Not specified (likely real-time)  
**Algorithms:** HTTP health checks, latency measurement

---

### 23. ListTemporalAnomalies

**RPC:** `InfrastructureService.ListTemporalAnomalies`  
**Method:** GET  
**Path:** `/api/infrastructure/v1/list-temporal-anomalies`  
**Description:** Returns server-computed temporal anomalies for news and satellite_fires.

**Request Parameters:** None

**Response Schema:** `ListTemporalAnomaliesResponse`
```yaml
anomalies: array<TemporalAnomaly>
  - type: string
    region: string
    currentCount: int32
    expectedCount: int32
    zScore: double
    severity: string
    multiplier: double
    message: string

trackedTypes: array<string>
computedAt: string
```

**Upstream Data Source:** Internal baseline tracking (news feeds, satellite fire data)  
**Free/Paid:** N/A (internal aggregation of free sources: GDELT for news, FIRMS for fires)  
**Caching:** Yes (indicated by `computedAt`)  
**Algorithms:**
- Z-score anomaly detection
- Baseline comparison (leverages GetTemporalBaseline internally)

---

## Summary Tables

### Free vs Paid Data Sources

| Category | Free Sources | Paid/Mixed Sources |
|----------|-------------|-------------------|
| **Intelligence** | GDELT, GitHub, HN, SEC EDGAR, RestCountries, Wikipedia, Israeli Oref, Space-Track, UK/US Travel Advisories, Telegram Bot API | Google Places API (Pizza Index), LLM inference (ClassifyEvent, DeductSituation, GetCountryIntelBrief) |
| **Infrastructure** | Cloudflare Radar (DDoS, outages, anomalies), ADS-B Exchange, NGA Maritime Warnings, MaxMind GeoLite2, FIRMS (fires) | None explicitly mentioned |

### Caching Strategy

All endpoints with timestamps (`fetchedAt`, `generatedAt`, `computedAt`, `enrichedAtMs`) indicate caching:
- **Intelligence:** Company enrichment, GDELT timelines, Pizza Index, risk scores, company signals, GPS interference
- **Infrastructure:** Bootstrap data, cable health, temporal baselines, all Cloudflare Radar endpoints

### Key Algorithms

| Endpoint | Algorithm/Technique |
|----------|-------------------|
| **ClassifyEvent** | NLP event classification (LLM-based) |
| **DeductSituation** | LLM situational reasoning |
| **GetCompanyEnrichment** | Multi-source REST aggregation, tech stack inference |
| **GetGdeltTopicTimeline** | GDELT time-series extraction |
| **GetPizzintStatus** | Live popularity monitoring, spike detection (z-score) |
| **GetRiskScores** | Composite Instability Index (CII): weighted multi-source aggregation |
| **ListCompanySignals** | Signal classification, source tier ranking |
| **ListGpsInterference** | H3 geospatial binning, NP averaging |
| **GetCableHealth** | Maritime warning parsing, cable proximity analysis |
| **GetTemporalBaseline** | Welford's algorithm (online mean/variance), z-score anomaly detection |
| **ListInternetOutages** | BGP route withdrawal, traffic drop analysis |

---

## Implementation Notes

1. **Authentication:** Not specified in schemas (likely API key via header)
2. **Rate Limiting:** Not documented (assume standard REST best practices)
3. **Error Handling:** Consistent schema with `ValidationError` and generic `Error` types
4. **Pagination:** Only `ListInternetOutages` has explicit cursor-based pagination
5. **Field Precision:** Multiple warnings about int64 fields losing precision in JavaScript (use string representation or BigInt)
6. **Data Freshness:** Explicitly tracked via `dataFreshness` enum in Pizza Index
7. **Historical Data:** Some endpoints support time ranges (`ListInternetOutages`), most return latest/cached

---

**End of Report**
