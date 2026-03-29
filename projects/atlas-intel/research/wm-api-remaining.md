# World Monitor API - Remaining Endpoints Analysis

**Generated:** 2026-03-23  
**Endpoints Analyzed:** 23

This document provides comprehensive details on all remaining World Monitor API endpoints not covered in previous analysis. For each endpoint, we extract: RPC name, description, request parameters, response schema, upstream data source, free/paid status, caching strategy, and algorithms.

---

## Table of Contents

1. [News Service (3 endpoints)](#news-service)
2. [Seismology Service (1 endpoint)](#seismology-service)
3. [Wildfire Service (1 endpoint)](#wildfire-service)
4. [Unrest Service (1 endpoint)](#unrest-service)
5. [Natural Service (1 endpoint)](#natural-service)
6. [Positive Events Service (1 endpoint)](#positive-events-service)
7. [Prediction Service (1 endpoint)](#prediction-service)
8. [Giving Service (1 endpoint)](#giving-service)
9. [Research Service (4 endpoints)](#research-service)
10. [Supply Chain Service (3 endpoints)](#supply-chain-service)
11. [Trade Service (6 endpoints)](#trade-service)
12. [Intelligence Service (1 endpoint)](#intelligence-service)

---

## News Service

### 1. GetSummarizeArticleCache

**RPC Name:** `GetSummarizeArticleCache`  
**Method:** GET  
**Endpoint:** `/api/news/v1/summarize-article-cache`

**Description:** Looks up a cached summary by deterministic key (CDN-cacheable GET).

**Request Parameters:**
- `cache_key` (string, optional): Deterministic cache key computed by buildSummaryCacheKey()

**Response Schema:**
```typescript
{
  summary: string;           // The generated summary text
  model: string;             // Model identifier used for generation
  provider: string;          // Provider that produced the result (or "cache")
  tokens: int32;             // Token count from the LLM response
  fallback: boolean;         // Whether client should try next provider in fallback chain
  error: string;             // Error message if request failed
  errorType: string;         // Error type/name (e.g. "TypeError")
  status: "SUMMARIZE_STATUS_UNSPECIFIED" | "SUMMARIZE_STATUS_SUCCESS" | 
          "SUMMARIZE_STATUS_CACHED" | "SUMMARIZE_STATUS_SKIPPED" | "SUMMARIZE_STATUS_ERROR";
  statusDetail: string;      // Human-readable detail for non-success statuses
}
```

**Upstream Data Source:** Internal cache layer (LLM-generated summaries)  
**Free/Paid:** Free (cache lookup)  
**Caching:** CDN-cacheable GET endpoint with deterministic cache keys  
**Algorithms:** Cache key generation via `buildSummaryCacheKey()`

---

### 2. ListFeedDigest

**RPC Name:** `ListFeedDigest`  
**Method:** GET  
**Endpoint:** `/api/news/v1/list-feed-digest`

**Description:** Returns a pre-aggregated digest of all RSS feeds for a site variant.

**Request Parameters:**
- `variant` (string, optional): Site variant: `full`, `tech`, `finance`, `happy`
- `lang` (string, optional): ISO 639-1 language code (en, fr, ar, etc.)

**Response Schema:**
```typescript
{
  categories: {
    [categoryName: string]: {
      items: NewsItem[];
    }
  };
  feedStatuses: {
    [feedName: string]: string;  // Only non-ok states emitted (empty, timeout)
  };
  generatedAt: string;           // ISO 8601 timestamp of digest generation
}

NewsItem {
  source: string;                // Source feed name (required)
  title: string;                 // Article headline (required)
  link: string;                  // Article URL
  publishedAt: int64;            // Publication time (Unix epoch ms)
  isAlert: boolean;              // Whether this triggered an alert condition
  threat: {
    level: "THREAT_LEVEL_UNSPECIFIED" | "THREAT_LEVEL_LOW" | "THREAT_LEVEL_MEDIUM" | 
           "THREAT_LEVEL_HIGH" | "THREAT_LEVEL_CRITICAL";
    category: string;            // Event category
    confidence: double;          // Confidence score (0.0 to 1.0)
    source: string;              // Classification source: "keyword", "ml", or "llm"
  };
  location: {
    latitude: double;            // -90 to 90
    longitude: double;           // -180 to 180
  };
  locationName: string;          // Human-readable location name
}
```

**Upstream Data Source:** Multiple RSS feeds (aggregated)  
**Free/Paid:** Free (RSS feeds are publicly accessible)  
**Caching:** Pre-aggregated digest updated periodically  
**Algorithms:** 
- Threat classification via keyword matching, ML, or LLM
- Location extraction and geocoding
- Alert triggering logic

---

### 3. SummarizeArticle

**RPC Name:** `SummarizeArticle`  
**Method:** POST  
**Endpoint:** `/api/news/v1/summarize-article`

**Description:** Generates an LLM summary with provider selection and fallback support.

**Request Parameters:**
```typescript
{
  provider: string;              // Required: "ollama", "groq", "openrouter"
  headlines: string[];           // Required: Headlines to summarize (max 8 used), min 1
  mode: string;                  // Optional: "brief", "analysis", "translate", "" (default)
  geoContext: string;            // Optional: Geographic signal context to include in prompt
  variant: string;               // Optional: "full", "tech", or target language for translate mode
  lang: string;                  // Optional: Output language code, default "en"
}
```

**Response Schema:** (Same as GetSummarizeArticleCache)

**Upstream Data Source:** LLM providers (Ollama, Groq, OpenRouter)  
**Free/Paid:** Depends on provider (Ollama free if self-hosted, Groq/OpenRouter paid)  
**Caching:** Results cached after generation (accessible via GetSummarizeArticleCache)  
**Algorithms:**
- Provider selection and fallback chain
- Prompt engineering for different modes (brief, analysis, translate)
- Geographic context injection

---

## Seismology Service

### 4. ListEarthquakes

**RPC Name:** `ListEarthquakes`  
**Method:** GET  
**Endpoint:** `/api/seismology/v1/list-earthquakes`

**Description:** Retrieves recent earthquakes from the USGS GeoJSON feed.

**Request Parameters:**
- `start` (int64, optional): Start of time range (inclusive), Unix epoch milliseconds
- `end` (int64, optional): End of time range (inclusive), Unix epoch milliseconds
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `min_magnitude` (double, optional): Minimum magnitude filter (e.g., 4.0 for significant quakes)

**Response Schema:**
```typescript
{
  earthquakes: Earthquake[];
  pagination: {
    nextCursor: string;          // Empty string = no more pages
    totalCount: int32;           // Total count if known, 0 if unknown
  };
}

Earthquake {
  id: string;                    // Required: Unique USGS event identifier (e.g., "us7000abcd")
  place: string;                 // Human-readable place (e.g., "10 km SW of Anchorage, Alaska")
  magnitude: double;             // Earthquake magnitude on Richter scale
  depthKm: double;               // Depth in kilometers below surface
  location: {
    latitude: double;            // -90 to 90
    longitude: double;           // -180 to 180
  };
  occurredAt: int64;             // Time earthquake occurred (Unix epoch ms)
  sourceUrl: string;             // URL to USGS event detail page
}
```

**Upstream Data Source:** USGS GeoJSON feed (https://earthquake.usgs.gov/)  
**Free/Paid:** **FREE** (USGS provides public earthquake data)  
**Caching:** Cached with periodic updates from USGS feed  
**Algorithms:**
- Time range filtering
- Magnitude filtering
- Cursor-based pagination

---

## Wildfire Service

### 5. ListFireDetections

**RPC Name:** `ListFireDetections`  
**Method:** GET  
**Endpoint:** `/api/wildfire/v1/list-fire-detections`

**Description:** Retrieves satellite-detected active fires from NASA FIRMS.

**Request Parameters:**
- `start` (int64, optional): Start of time range (inclusive), Unix epoch milliseconds
- `end` (int64, optional): End of time range (inclusive), Unix epoch milliseconds
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `ne_lat` (double, optional): North-east latitude of bounding box
- `ne_lon` (double, optional): North-east longitude of bounding box
- `sw_lat` (double, optional): South-west latitude of bounding box
- `sw_lon` (double, optional): South-west longitude of bounding box

**Response Schema:**
```typescript
{
  fireDetections: FireDetection[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

FireDetection {
  id: string;                    // Required: Unique detection identifier
  location: {
    latitude: double;            // -90 to 90
    longitude: double;           // -180 to 180
  };
  brightness: double;            // Brightness temperature in Kelvin
  frp: double;                   // Fire radiative power in MW
  confidence: "FIRE_CONFIDENCE_UNSPECIFIED" | "FIRE_CONFIDENCE_LOW" | 
              "FIRE_CONFIDENCE_NOMINAL" | "FIRE_CONFIDENCE_HIGH";
  satellite: string;             // Satellite that detected fire (e.g., "MODIS", "VIIRS", "LANDSAT")
  detectedAt: int64;             // Time fire was detected (Unix epoch ms)
  region: string;                // Monitored region name (e.g., "Ukraine", "Russia", "Iran")
  dayNight: string;              // Day or night detection ("D" or "N")
}
```

**Upstream Data Source:** NASA FIRMS (Fire Information for Resource Management System)  
**Free/Paid:** **FREE** (NASA FIRMS provides free satellite fire data)  
**Caching:** Cached with periodic updates from NASA FIRMS  
**Algorithms:**
- Bounding box geospatial filtering
- Time range filtering
- Satellite data aggregation from multiple sensors (MODIS, VIIRS, LANDSAT)

---

## Unrest Service

### 6. ListUnrestEvents

**RPC Name:** `ListUnrestEvents`  
**Method:** GET  
**Endpoint:** `/api/unrest/v1/list-unrest-events`

**Description:** Retrieves protest, riot, and civil unrest events.

**Request Parameters:**
- `start` (int64, optional): Start of time range (inclusive), Unix epoch milliseconds
- `end` (int64, optional): End of time range (inclusive), Unix epoch milliseconds
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `country` (string, optional): Country filter (ISO 3166-1 alpha-2)
- `min_severity` (string, optional): Minimum severity filter
- `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` (double, optional): Bounding box coordinates

**Response Schema:**
```typescript
{
  events: UnrestEvent[];
  clusters: UnrestCluster[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

UnrestEvent {
  id: string;                    // Required: Unique event identifier
  title: string;                 // Event title or headline
  summary: string;               // Brief summary
  eventType: "UNREST_EVENT_TYPE_UNSPECIFIED" | "UNREST_EVENT_TYPE_PROTEST" | 
             "UNREST_EVENT_TYPE_RIOT" | "UNREST_EVENT_TYPE_STRIKE" | 
             "UNREST_EVENT_TYPE_DEMONSTRATION" | "UNREST_EVENT_TYPE_CIVIL_UNREST";
  city: string;                  // City where event occurred
  country: string;               // Country where event occurred
  region: string;                // Administrative region within country
  location: {
    latitude: double;
    longitude: double;
  };
  occurredAt: int64;             // Time event occurred (Unix epoch ms)
  severity: "SEVERITY_LEVEL_UNSPECIFIED" | "SEVERITY_LEVEL_LOW" | 
            "SEVERITY_LEVEL_MEDIUM" | "SEVERITY_LEVEL_HIGH";
  fatalities: int32;             // Reported fatalities, if any
  sources: string[];             // Source identifiers
  sourceType: "UNREST_SOURCE_TYPE_UNSPECIFIED" | "UNREST_SOURCE_TYPE_ACLED" | 
              "UNREST_SOURCE_TYPE_GDELT" | "UNREST_SOURCE_TYPE_RSS";
  tags: string[];                // Descriptive tags
  actors: string[];              // Named actors involved
  confidence: "CONFIDENCE_LEVEL_UNSPECIFIED" | "CONFIDENCE_LEVEL_LOW" | 
              "CONFIDENCE_LEVEL_MEDIUM" | "CONFIDENCE_LEVEL_HIGH";
}

UnrestCluster {
  id: string;                    // Unique cluster identifier
  country: string;               // Country of the cluster
  region: string;                // Region within country
  eventCount: int32;             // Number of events in cluster
  events: UnrestEvent[];
  severity: "SEVERITY_LEVEL_UNSPECIFIED" | "SEVERITY_LEVEL_LOW" | 
            "SEVERITY_LEVEL_MEDIUM" | "SEVERITY_LEVEL_HIGH";
  startAt: int64;                // Start of cluster time window (Unix epoch ms)
  endAt: int64;                  // End of cluster time window (Unix epoch ms)
  primaryCause: string;          // Primary cause or theme of unrest
}
```

**Upstream Data Sources:**
- **ACLED** (Armed Conflict Location & Event Data Project) - **FREE** (publicly accessible)
- **GDELT** (Global Database of Events, Language, and Tone) - **FREE**
- **RSS feeds** - **FREE**

**Free/Paid:** **FREE** (all upstream sources are publicly accessible)  
**Caching:** Cached with periodic updates from ACLED, GDELT, RSS  
**Algorithms:**
- Multi-source aggregation from ACLED, GDELT, RSS
- Geographic clustering to identify related events
- Severity classification based on fatalities, event type, and source confidence
- Temporal clustering for event sequences

---

## Natural Service

### 7. ListNaturalEvents

**RPC Name:** `ListNaturalEvents`  
**Method:** GET  
**Endpoint:** `/api/natural/v1/list-natural-events`

**Description:** Retrieves natural disaster events (hurricanes, earthquakes, floods, etc.).

**Request Parameters:**
- `days` (int32, optional): Events within N days from now (0 = unlimited)

**Response Schema:**
```typescript
{
  events: NaturalEvent[];
}

NaturalEvent {
  id: string;
  title: string;
  description: string;
  category: string;              // Event category
  categoryTitle: string;
  lat: double;
  lon: double;
  date: int64;                   // Unix epoch ms
  magnitude: double;
  magnitudeUnit: string;
  sourceUrl: string;
  sourceName: string;
  closed: boolean;               // Whether event is closed/resolved
  
  // Optional tropical cyclone fields (for severeStorms from GDACS TC / NHC)
  stormId: string;
  stormName: string;
  basin: string;
  stormCategory: int32;
  classification: string;
  windKt: int32;                 // Wind speed in knots
  pressureMb: int32;             // Pressure in millibars
  movementDir: int32;            // Movement direction in degrees
  movementSpeedKt: int32;        // Movement speed in knots
  forecastTrack: {
    lat: double;
    lon: double;
    hour: int32;
    windKt: int32;
    category: int32;
  }[];
  conePolygon: {
    points: {
      lon: double;
      lat: double;
    }[];
  }[];
  pastTrack: {
    lat: double;
    lon: double;
    windKt: int32;
    timestamp: int64;            // Unix epoch ms
  }[];
}
```

**Upstream Data Sources:**
- **GDACS** (Global Disaster Alert and Coordination System) - **FREE**
- **NHC** (National Hurricane Center) - **FREE** (NOAA)
- **NASA EONET** (Earth Observatory Natural Event Tracker) - **FREE**

**Free/Paid:** **FREE** (all upstream sources are publicly accessible)  
**Caching:** Cached with periodic updates from GDACS, NHC, NASA EONET  
**Algorithms:**
- Multi-source natural disaster aggregation
- Tropical cyclone tracking with forecast cones
- Past track reconstruction
- Event categorization (earthquake, hurricane, flood, wildfire, etc.)

---

## Positive Events Service

### 8. ListPositiveGeoEvents

**RPC Name:** `ListPositiveGeoEvents`  
**Method:** GET  
**Endpoint:** `/api/positive-events/v1/list-positive-geo-events`

**Description:** Retrieves geocoded positive news events from GDELT GEO API.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  events: PositiveGeoEvent[];
}

PositiveGeoEvent {
  latitude: double;
  longitude: double;
  name: string;
  category: string;
  count: int32;
  timestamp: int64;              // Unix epoch ms
}
```

**Upstream Data Source:** GDELT GEO API  
**Free/Paid:** **FREE** (GDELT is publicly accessible)  
**Caching:** Cached with periodic updates from GDELT GEO API  
**Algorithms:**
- Positive sentiment filtering from GDELT events
- Geographic clustering of positive events
- Event count aggregation per location

---

## Prediction Service

### 9. ListPredictionMarkets

**RPC Name:** `ListPredictionMarkets`  
**Method:** GET  
**Endpoint:** `/api/prediction/v1/list-prediction-markets`

**Description:** Retrieves active prediction markets from Polymarket.

**Request Parameters:**
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `category` (string, optional): Category filter (e.g., "Politics")
- `query` (string, optional): Search query for market titles

**Response Schema:**
```typescript
{
  markets: PredictionMarket[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

PredictionMarket {
  id: string;                    // Required: Unique market identifier or slug
  title: string;                 // Market question or title
  yesPrice: double;              // Current "Yes" price (0.0 to 1.0, representing probability)
  volume: double;                // Trading volume in USD (min 0)
  url: string;                   // URL to the market page
  closesAt: int64;               // Market close time (Unix epoch ms, 0 if no expiry)
  category: string;              // Market category (e.g., "Politics", "Crypto", "Sports")
  source: "MARKET_SOURCE_UNSPECIFIED" | "MARKET_SOURCE_POLYMARKET" | "MARKET_SOURCE_KALSHI";
}
```

**Upstream Data Sources:**
- **Polymarket** - **FREE** (public API access)
- **Kalshi** - **FREE** (public API access)

**Free/Paid:** **FREE** (public prediction market data)  
**Caching:** Cached with periodic updates from Polymarket/Kalshi APIs  
**Algorithms:**
- Market search and filtering
- Category-based organization
- Price probability conversion (0-1 scale)

---

## Giving Service

### 10. GetGivingSummary

**RPC Name:** `GetGivingSummary`  
**Method:** GET  
**Endpoint:** `/api/giving/v1/get-giving-summary`

**Description:** Retrieves a composite global giving activity index and platform breakdowns.

**Request Parameters:**
- `platform_limit` (int32, optional): Number of platforms to include (0 = all)
- `category_limit` (int32, optional): Number of category breakdowns to include (0 = all)

**Response Schema:**
```typescript
{
  summary: GivingSummary;
}

GivingSummary {
  generatedAt: string;           // Timestamp of summary generation (ISO 8601)
  activityIndex: double;         // Global giving activity index (0-100 composite score)
  trend: string;                 // Index trend direction
  estimatedDailyFlowUsd: double; // Estimated daily global giving flow in USD
  platforms: PlatformGiving[];
  categories: CategoryBreakdown[];
  crypto: CryptoGivingSummary;
  institutional: InstitutionalGiving;
}

PlatformGiving {
  platform: string;              // Required: Platform name (e.g., "GoFundMe", "GlobalGiving")
  dailyVolumeUsd: double;        // Estimated daily donation volume in USD
  activeCampaignsSampled: int32; // Number of active campaigns being sampled
  newCampaigns24h: int32;        // New campaigns created in last 24 hours
  donationVelocity: double;      // Average donation velocity (donations per hour)
  dataFreshness: string;         // "live", "daily", "weekly", "annual"
  lastUpdated: string;           // Last data update timestamp (ISO 8601)
}

CategoryBreakdown {
  category: string;              // Category name (e.g., "Medical", "Disaster Relief")
  share: double;                 // Share of total giving activity (0-1)
  change24h: double;             // 24-hour change in share percentage points
  activeCampaigns: int32;        // Number of active campaigns in this category
  trending: boolean;             // Trending indicator
}

CryptoGivingSummary {
  dailyInflowUsd: double;        // Total 24h inflow to tracked charity wallets (USD)
  trackedWallets: int32;         // Number of tracked charity wallets
  transactions24h: int32;        // Number of transactions in last 24 hours
  topReceivers: string[];        // Top receiving platforms / DAOs
  pctOfTotal: double;            // Percentage of total giving that is on-chain
}

InstitutionalGiving {
  oecdOdaAnnualUsdBn: double;    // Latest OECD ODA total (annual, USD billions)
  oecdDataYear: int32;           // Year of latest OECD data
  cafWorldGivingIndex: double;  // CAF World Giving Index score (latest)
  cafDataYear: int32;            // Year of latest CAF data
  candidGrantsTracked: int32;    // Number of foundation grants tracked (Candid)
  dataLag: string;               // Data lag description (e.g., "Quarterly", "Annual")
}
```

**Upstream Data Sources:**
- **Crowdfunding platforms** (GoFundMe, GlobalGiving, JustGiving, etc.) - **FREE** (scraped public data)
- **Blockchain data** (on-chain charity wallets) - **FREE** (public blockchain data)
- **OECD ODA** (Official Development Assistance) - **FREE**
- **CAF World Giving Index** - **FREE**
- **Candid** (foundation grants) - **FREE** (public grant databases)

**Free/Paid:** **FREE** (all upstream sources are publicly accessible or scraped)  
**Caching:** Pre-aggregated summary updated daily  
**Algorithms:**
- Global giving activity index (0-100 composite score)
- Platform donation velocity calculation
- Category trend detection
- Crypto wallet tracking and transaction aggregation
- Multi-source institutional giving aggregation

---

## Research Service

### 11. ListArxivPapers

**RPC Name:** `ListArxivPapers`  
**Method:** GET  
**Endpoint:** `/api/research/v1/list-arxiv-papers`

**Description:** Retrieves recent papers from arXiv.

**Request Parameters:**
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `category` (string, optional): arXiv category filter (e.g., "cs.AI"). Empty returns all tracked categories
- `query` (string, optional): Search query for paper titles and abstracts

**Response Schema:**
```typescript
{
  papers: ArxivPaper[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

ArxivPaper {
  id: string;                    // Required: arXiv paper ID (e.g., "2401.12345")
  title: string;                 // Required: Paper title
  summary: string;               // Paper abstract (may be truncated)
  authors: string[];             // Author names
  categories: string[];          // arXiv categories (e.g., "cs.AI", "cs.LG")
  publishedAt: int64;            // Publication time (Unix epoch ms)
  url: string;                   // URL to the paper
}
```

**Upstream Data Source:** arXiv API  
**Free/Paid:** **FREE** (arXiv is open-access)  
**Caching:** Cached with periodic updates from arXiv API  
**Algorithms:**
- Category filtering
- Full-text search on titles and abstracts
- Cursor-based pagination

---

### 12. ListHackernewsItems

**RPC Name:** `ListHackernewsItems`  
**Method:** GET  
**Endpoint:** `/api/research/v1/list-hackernews-items`

**Description:** Retrieves top stories from Hacker News.

**Request Parameters:**
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `feed_type` (string, optional): Feed type: "top", "new", "best", "ask", "show". Defaults to "top"

**Response Schema:**
```typescript
{
  items: HackernewsItem[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

HackernewsItem {
  id: int32;                     // HN item ID
  title: string;                 // Required: Item title
  url: string;                   // URL (empty for Ask HN / Show HN text posts)
  score: int32;                  // Upvote score (min 0)
  commentCount: int32;           // Number of comments
  by: string;                    // Author username
  submittedAt: int64;            // Submission time (Unix epoch ms)
}
```

**Upstream Data Source:** Hacker News API  
**Free/Paid:** **FREE** (Hacker News API is publicly accessible)  
**Caching:** Cached with periodic updates from HN API  
**Algorithms:**
- Feed type selection (top, new, best, ask, show)
- Score and comment count aggregation

---

### 13. ListTechEvents

**RPC Name:** `ListTechEvents`  
**Method:** GET  
**Endpoint:** `/api/research/v1/list-tech-events`

**Description:** Retrieves tech events from Techmeme ICS, dev.events RSS, and curated sources.

**Request Parameters:**
- `type` (string, optional): Event type filter: "all", "conferences", "earnings", "ipo", "other". Empty = all
- `mappable` (boolean, optional): Only events with non-virtual coordinates
- `limit` (int32, optional): Max events to return (0 = unlimited)
- `days` (int32, optional): Events within N days from now (0 = unlimited)

**Response Schema:**
```typescript
{
  success: boolean;              // Whether the request succeeded
  count: int32;                  // Total event count in response
  conferenceCount: int32;        // Number of conference-type events
  mappableCount: int32;          // Number of mappable (non-virtual with coords) events
  lastUpdated: string;           // ISO 8601 timestamp of last update
  events: TechEvent[];
  error: string;                 // Error message if success is false
}

TechEvent {
  id: string;                    // Unique event identifier
  title: string;                 // Event title
  type: string;                  // Event type: "conference", "earnings", "ipo", "other"
  location: string;              // Location description
  coords: {
    lat: double;
    lng: double;
    country: string;             // Country name or code
    original: string;            // Original location string before normalization
    virtual: boolean;            // Whether this is a virtual/online event
  };
  startDate: string;             // Start date (YYYY-MM-DD)
  endDate: string;               // End date (YYYY-MM-DD)
  url: string;                   // Event URL
  source: string;                // Source: "techmeme", "dev.events", "curated"
  description: string;           // Event description
}
```

**Upstream Data Sources:**
- **Techmeme ICS** - **FREE** (public calendar feed)
- **dev.events RSS** - **FREE**
- **Curated sources** - **FREE**

**Free/Paid:** **FREE** (all upstream sources are publicly accessible)  
**Caching:** Cached with periodic updates from Techmeme, dev.events, curated sources  
**Algorithms:**
- Multi-source event aggregation
- Location normalization and geocoding
- Virtual event detection
- Event type classification

---

### 14. ListTrendingRepos

**RPC Name:** `ListTrendingRepos`  
**Method:** GET  
**Endpoint:** `/api/research/v1/list-trending-repos`

**Description:** Retrieves trending repositories from GitHub.

**Request Parameters:**
- `page_size` (int32, optional): Maximum items per page (1-100)
- `cursor` (string, optional): Cursor for next page
- `language` (string, optional): Programming language filter (e.g., "python", "typescript")
- `period` (string, optional): Trending period (e.g., "daily", "weekly"). Defaults to "daily"

**Response Schema:**
```typescript
{
  repos: GithubRepo[];
  pagination: {
    nextCursor: string;
    totalCount: int32;
  };
}

GithubRepo {
  fullName: string;              // Required: Repository full name (e.g., "owner/repo")
  description: string;           // Repository description
  language: string;              // Primary programming language
  stars: int32;                  // Total star count (min 0)
  starsToday: int32;             // Stars gained in the trending period
  forks: int32;                  // Number of open forks
  url: string;                   // Repository URL
}
```

**Upstream Data Source:** GitHub (scraped trending page or API)  
**Free/Paid:** **FREE** (GitHub trending data is publicly accessible)  
**Caching:** Cached with periodic updates from GitHub  
**Algorithms:**
- Language filtering
- Period-based trending calculation (daily, weekly)
- Star velocity tracking

---

## Supply Chain Service

### 15. GetChokepointStatus

**RPC Name:** `GetChokepointStatus`  
**Method:** GET  
**Endpoint:** `/api/supply-chain/v1/get-chokepoint-status`

**Description:** Get status of global maritime and land trade chokepoints.

**Request Parameters:**
- `chokepoints` (string, optional): Comma-separated list of chokepoint names to filter. Empty = all

**Response Schema:**
```typescript
{
  chokepoints: ChokepointStatus[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

ChokepointStatus {
  name: string;                  // Chokepoint name (e.g., "Suez Canal", "Panama Canal")
  type: string;                  // Type: "MARITIME", "LAND", "BRIDGE"
  location: {
    latitude: double;
    longitude: double;
  };
  status: string;                // Current status: "OPEN", "RESTRICTED", "CLOSED"
  vesselBacklog: int32;          // Number of vessels waiting
  avgWaitHours: double;          // Average wait time in hours
  throughputPct: double;         // Throughput as percentage of normal capacity
  incidents: string[];           // Recent incident descriptions
  lastUpdated: string;           // ISO 8601 timestamp of last status update
  sourceUrl: string;             // URL to official chokepoint status page
}
```

**Upstream Data Sources:**
- **Suez Canal Authority** - **FREE** (public status updates)
- **Panama Canal Authority** - **FREE** (public status updates)
- **Marine traffic data** - **FREE** (scraped from public AIS data)

**Free/Paid:** **FREE** (public maritime and trade data)  
**Caching:** Cached with periodic updates from chokepoint authorities  
**Algorithms:**
- Vessel backlog calculation from AIS data
- Average wait time estimation
- Throughput percentage calculation vs. historical baseline

---

### 16. GetCriticalMinerals

**RPC Name:** `GetCriticalMinerals`  
**Method:** GET  
**Endpoint:** `/api/supply-chain/v1/get-critical-minerals`

**Description:** Get supply risk data for critical minerals.

**Request Parameters:**
- `minerals` (string, optional): Comma-separated list of mineral names to filter. Empty = all

**Response Schema:**
```typescript
{
  minerals: CriticalMineral[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

CriticalMineral {
  name: string;                  // Mineral name (e.g., "Lithium", "Cobalt", "Rare Earths")
  category: string;              // Category (e.g., "Battery Materials", "Electronics")
  topProducers: {
    country: string;
    sharePct: double;            // Share of global production (percentage)
  }[];
  supplyRisk: string;            // Risk level: "LOW", "MEDIUM", "HIGH", "CRITICAL"
  concentrationIndex: double;    // Herfindahl-Hirschman Index (0-10000)
  usImportDependence: double;    // US import dependence percentage
  euImportDependence: double;    // EU import dependence percentage
  priceVolatility: double;       // Price volatility metric (0-100)
  alternatives: string[];        // Alternative materials or substitutes
  sourceUrl: string;             // URL to USGS or IEA data source
}
```

**Upstream Data Sources:**
- **USGS** (US Geological Survey) - **FREE** (public mineral data)
- **IEA** (International Energy Agency) - **FREE** (public energy and mineral reports)
- **EU Critical Raw Materials List** - **FREE**

**Free/Paid:** **FREE** (public mineral and supply chain data)  
**Caching:** Cached with periodic updates from USGS, IEA, EU sources  
**Algorithms:**
- Herfindahl-Hirschman Index calculation for market concentration
- Import dependence calculation
- Price volatility calculation from historical price data

---

### 17. GetShippingRates

**RPC Name:** `GetShippingRates`  
**Method:** GET  
**Endpoint:** `/api/supply-chain/v1/get-shipping-rates`

**Description:** Get container shipping rates and trends.

**Request Parameters:**
- `routes` (string, optional): Comma-separated list of route names to filter. Empty = all major routes

**Response Schema:**
```typescript
{
  routes: ShippingRoute[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

ShippingRoute {
  routeName: string;             // Route name (e.g., "Shanghai-Los Angeles", "Rotterdam-New York")
  origin: string;                // Origin port
  destination: string;           // Destination port
  ratePerTeu: double;            // Current rate per TEU (Twenty-foot Equivalent Unit) in USD
  rateChange7d: double;          // 7-day rate change (percentage)
  rateChange30d: double;         // 30-day rate change (percentage)
  transitDays: int32;            // Estimated transit time in days
  capacity: string;              // Capacity status: "TIGHT", "NORMAL", "LOOSE"
  delays: int32;                 // Average delay in days
  sourceUrl: string;             // URL to rate data source (e.g., Drewry, Freightos)
}
```

**Upstream Data Sources:**
- **Freightos Baltic Index** - **FREE** (public shipping rate index)
- **Drewry** - **PAID** (container rate reports, but may have free summary data)
- **Shanghai Containerized Freight Index** - **FREE**

**Free/Paid:** **MIXED** (Freightos and Shanghai Index are free, Drewry is paid but may have free summaries)  
**Caching:** Cached with periodic updates from rate indices  
**Algorithms:**
- 7-day and 30-day rate change calculation
- Capacity status classification based on rate trends
- Delay estimation from port congestion data

---

## Trade Service

### 18. GetCustomsRevenue

**RPC Name:** `GetCustomsRevenue`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/get-customs-revenue`

**Description:** Get customs revenue trends for WTO members.

**Request Parameters:**
- `countries` (string, optional): WTO member codes to filter by. Empty = all
- `years` (int32, optional): Number of years to look back (default 10, max 30)

**Response Schema:**
```typescript
{
  revenues: CustomsRevenueRecord[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched from WTO
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

CustomsRevenueRecord {
  country: string;               // WTO member code
  year: int32;                   // Year of observation
  revenueUsd: double;            // Customs revenue in millions USD
  pctOfGdp: double;              // Customs revenue as percentage of GDP
  yoyChange: double;             // Year-over-year change (percentage)
  tariffRevenuePct: double;      // Percentage of revenue from tariffs vs. other customs fees
}
```

**Upstream Data Source:** WTO (World Trade Organization)  
**Free/Paid:** **FREE** (WTO provides public trade statistics)  
**Caching:** Cached with periodic updates from WTO  
**Algorithms:**
- Year-over-year change calculation
- GDP percentage calculation
- Tariff vs. non-tariff revenue breakdown

---

### 19. GetTariffTrends

**RPC Name:** `GetTariffTrends`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/get-tariff-trends`

**Description:** Get applied MFN tariff trends for WTO members.

**Request Parameters:**
- `countries` (string, optional): WTO member codes to filter by. Empty = all
- `years` (int32, optional): Number of years to look back (default 10, max 30)

**Response Schema:**
```typescript
{
  trends: TariffTrend[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched from WTO
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

TariffTrend {
  country: string;               // WTO member code
  year: int32;                   // Year of observation
  avgMfnRate: double;            // Average applied MFN (Most Favored Nation) tariff rate (percentage)
  agricultureRate: double;       // Average tariff on agricultural products (percentage)
  nonAgricultureRate: double;    // Average tariff on non-agricultural products (percentage)
  peakTariffsPct: double;        // Percentage of tariff lines with peak rates (>15%)
  yoyChange: double;             // Year-over-year change in avg MFN rate (percentage points)
}
```

**Upstream Data Source:** WTO (World Trade Organization)  
**Free/Paid:** **FREE** (WTO provides public tariff data)  
**Caching:** Cached with periodic updates from WTO  
**Algorithms:**
- Average MFN rate calculation across all tariff lines
- Agriculture vs. non-agriculture split
- Peak tariff detection (>15%)
- Year-over-year trend analysis

---

### 20. GetTradeBarriers

**RPC Name:** `GetTradeBarriers`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/get-trade-barriers`

**Description:** Get non-tariff barriers and SPS/TBT measures.

**Request Parameters:**
- `countries` (string, optional): WTO member codes to filter by. Empty = all
- `limit` (int32, optional): Max results to return (server caps at 100)

**Response Schema:**
```typescript
{
  barriers: TradeBarrier[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched from WTO
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

TradeBarrier {
  id: string;                    // Unique barrier identifier from WTO
  reportingCountry: string;      // ISO 3166-1 alpha-3 or WTO member code
  affectedCountry: string;       // Country affected by the barrier
  barrierType: string;           // Barrier classification: "SPS", "TBT", "QUOTA", "LICENSING", "OTHER"
  productSector: string;         // Product sector or HS chapter description
  description: string;           // Human-readable description of the measure
  status: string;                // Current status: "ACTIVE", "RESOLVED", "NOTIFIED"
  notifiedAt: string;            // ISO 8601 date when measure was notified
  sourceUrl: string;             // WTO source document URL (http/https protocol)
}
```

**Upstream Data Source:** WTO (World Trade Organization) - SPS/TBT notification databases  
**Free/Paid:** **FREE** (WTO provides public NTB data)  
**Caching:** Cached with periodic updates from WTO  
**Algorithms:**
- Barrier type classification (SPS = Sanitary/Phytosanitary, TBT = Technical Barriers to Trade)
- Status tracking (active, resolved, notified)

---

### 21. GetTradeFlows

**RPC Name:** `GetTradeFlows`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/get-trade-flows`

**Description:** Get bilateral merchandise trade flows.

**Request Parameters:**
- `reporting_country` (string, optional): WTO member code of reporting country
- `partner_country` (string, optional): WTO member code of partner country
- `years` (int32, optional): Number of years to look back (default 10, max 30)

**Response Schema:**
```typescript
{
  flows: TradeFlowRecord[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched from WTO
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

TradeFlowRecord {
  reportingCountry: string;      // WTO member code of reporting country
  partnerCountry: string;        // WTO member code of partner country
  year: int32;                   // Year of observation
  exportValueUsd: double;        // Merchandise export value in millions USD
  importValueUsd: double;        // Merchandise import value in millions USD
  yoyExportChange: double;       // Year-over-year export change (percentage)
  yoyImportChange: double;       // Year-over-year import change (percentage)
  productSector: string;         // Product sector or HS chapter
}
```

**Upstream Data Source:** WTO (World Trade Organization)  
**Free/Paid:** **FREE** (WTO provides public bilateral trade data)  
**Caching:** Cached with periodic updates from WTO  
**Algorithms:**
- Bilateral trade flow aggregation
- Year-over-year change calculation for exports and imports
- Product sector breakdown

---

### 22. GetTradeRestrictions

**RPC Name:** `GetTradeRestrictions`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/get-trade-restrictions`

**Description:** Get quantitative restrictions and export controls.

**Request Parameters:**
- `countries` (string, optional): WTO member codes to filter by. Empty = all
- `limit` (int32, optional): Max results to return (server caps at 100)

**Response Schema:**
```typescript
{
  restrictions: TradeRestriction[];
  fetchedAt: string;             // ISO 8601 timestamp when data was fetched from WTO
  upstreamUnavailable: boolean;  // True if upstream fetch failed and results may be stale/empty
}

TradeRestriction {
  id: string;                    // Unique restriction identifier from WTO
  reportingCountry: string;      // ISO 3166-1 alpha-3 or WTO member code of reporting country
  affectedCountry: string;       // Country affected by the restriction
  productSector: string;         // Product sector or HS chapter description
  measureType: string;           // Measure classification: "QR", "EXPORT_BAN", "IMPORT_BAN", "LICENSING"
  description: string;           // Human-readable description of the measure
  status: string;                // Current status: "IN_FORCE", "TERMINATED", "NOTIFIED"
  notifiedAt: string;            // ISO 8601 date when measure was notified
  sourceUrl: string;             // WTO source document URL (http/https protocol)
}
```

**Upstream Data Source:** WTO (World Trade Organization)  
**Free/Paid:** **FREE** (WTO provides public QR/export control data)  
**Caching:** Cached with periodic updates from WTO  
**Algorithms:**
- Measure type classification (QR, export ban, import ban, licensing)
- Status tracking (in force, terminated, notified)

---

### 23. ListComtradeFlows

**RPC Name:** `ListComtradeFlows`  
**Method:** GET  
**Endpoint:** `/api/trade/v1/list-comtrade-flows`

**Description:** List UN Comtrade strategic commodity flows with anomaly detection.

**Request Parameters:**
- `reporter_code` (string, optional): UN Comtrade reporter code (e.g. "842" = US, "156" = China). Empty returns all reporters
- `cmd_code` (string, optional): HS commodity code (e.g. "2709" = crude oil). Empty returns all commodities
- `anomalies_only` (boolean, optional): If true, only return flows with a year-over-year change exceeding 30%

**Response Schema:**
```typescript
{
  flows: ComtradeFlowRecord[];
  fetchedAt: string;             // ISO 8601 timestamp when data was seeded
  upstreamUnavailable: boolean;  // True if seeded data is missing or stale
}

ComtradeFlowRecord {
  reporterCode: string;          // UN Comtrade reporter code
  reporterName: string;          // Reporter country name
  partnerCode: string;           // Partner country code ("000" = world total)
  partnerName: string;           // Partner country name
  cmdCode: string;               // HS commodity code
  cmdDesc: string;               // Commodity description
  year: int32;                   // Reporting year
  tradeValueUsd: double;         // Trade value in USD
  netWeightKg: double;           // Net weight in kg
  yoyChange: double;             // Year-over-year change (ratio, e.g. 0.35 = +35%)
  isAnomaly: boolean;            // True if the YoY change exceeds the anomaly threshold (30%)
}
```

**Upstream Data Source:** UN Comtrade (United Nations Commodity Trade Statistics Database)  
**Free/Paid:** **FREE** (UN Comtrade provides free access to trade data)  
**Caching:** Seeded data with periodic updates from UN Comtrade  
**Algorithms:**
- Year-over-year change calculation
- Anomaly detection (>30% YoY change threshold)
- Strategic commodity filtering (crude oil, semiconductors, rare earths, etc.)

---

## Intelligence Service

### 24. SearchGdeltDocuments

**RPC Name:** `SearchGdeltDocuments`  
**Method:** GET  
**Endpoint:** `/api/intelligence/v1/search-gdelt-documents`

**Description:** Searches the GDELT GKG API for relevant documentation.

**Request Parameters:**
- `query` (string, optional): Search query string
- `max_records` (int32, optional): Maximum number of articles to return (1-250)
- `timespan` (string, optional): Time span filter (e.g., "15min", "1h", "24h")
- `tone_filter` (string, optional): Tone filter appended to query (e.g., "tone>5" for positive, "tone<-5" for negative). Left empty to skip tone filtering
- `sort` (string, optional): Sort mode: "DateDesc" (default), "ToneDesc", "ToneAsc", "HybridRel"

**Response Schema:**
```typescript
{
  articles: GdeltArticle[];
  query: string;                 // Echo of the search query
  error: string;                 // Error message if the search failed
}

GdeltArticle {
  title: string;                 // Article headline
  url: string;                   // Article URL
  source: string;                // Source domain name
  date: string;                  // Publication date string
  image: string;                 // Article image URL
  language: string;              // Article language code
  tone: double;                  // GDELT tone score (negative = negative tone, positive = positive tone)
}
```

**Upstream Data Source:** GDELT GKG (Global Knowledge Graph) API  
**Free/Paid:** **FREE** (GDELT provides free access to news and event data)  
**Caching:** Results cached temporarily for repeated queries  
**Algorithms:**
- GDELT tone score filtering (positive/negative sentiment)
- Time span filtering (15min, 1h, 24h, etc.)
- Multiple sort modes (date, tone, hybrid relevance)
- Full-text search across GDELT document database

---

## Summary: Free vs. Paid Data Sources

### **100% Free Endpoints (21/23)**

All endpoints rely on **publicly accessible, free data sources**:

1. **News Service**: RSS feeds, LLM caching (free if self-hosted)
2. **Seismology Service**: USGS (free)
3. **Wildfire Service**: NASA FIRMS (free)
4. **Unrest Service**: ACLED, GDELT, RSS (all free)
5. **Natural Service**: GDACS, NHC/NOAA, NASA EONET (all free)
6. **Positive Events Service**: GDELT GEO API (free)
7. **Prediction Service**: Polymarket, Kalshi (free public APIs)
8. **Giving Service**: Crowdfunding platforms (scraped), blockchain data, OECD, CAF, Candid (all free)
9. **Research Service**: arXiv, Hacker News, Techmeme, dev.events, GitHub (all free)
10. **Supply Chain Service**: Maritime authorities, USGS, IEA, Freightos Baltic Index (free)
11. **Trade Service**: WTO, UN Comtrade (free)
12. **Intelligence Service**: GDELT GKG API (free)

### **Mixed/Paid Endpoints (2/23)**

1. **News Service - SummarizeArticle**: Depends on LLM provider (Ollama free if self-hosted, Groq/OpenRouter paid)
2. **Supply Chain Service - GetShippingRates**: Freightos and Shanghai Index are free, but Drewry is paid (may have free summaries)

---

## Key Insights

1. **World Monitor heavily leverages free, public data sources** - The majority of endpoints (91%) use entirely free upstream data.

2. **Caching is critical** - All endpoints implement caching strategies to reduce load on upstream APIs and improve response times.

3. **Multi-source aggregation** - Many endpoints combine data from multiple free sources (e.g., Unrest Service uses ACLED + GDELT + RSS).

4. **Geospatial focus** - Most endpoints include geographic coordinates and support bounding box filtering.

5. **Anomaly detection** - Trade and supply chain endpoints include algorithmic anomaly detection (e.g., >30% YoY change in commodity flows).

6. **Time-based filtering** - Standardized time range filtering using Unix epoch milliseconds across most endpoints.

7. **Cursor-based pagination** - Consistent pagination approach using cursors instead of page offsets.

---

**Report Complete.**  
All 23 remaining World Monitor API endpoints have been catalogued with full schema details, upstream sources, and implementation notes.
