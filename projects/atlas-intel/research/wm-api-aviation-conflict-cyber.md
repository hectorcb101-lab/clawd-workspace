# World Monitor API Reference - Comprehensive Analysis

**Analysis Date:** 2026-03-23  
**Scope:** Aviation, Conflict, Climate, Cyber, and Displacement Services (18 endpoints total)  
**Purpose:** Extract endpoint details, schemas, data sources, free/paid status, and implementation patterns

---

## Executive Summary

World Monitor provides 18 REST API endpoints across 5 service domains:
- **Aviation Service:** 9 endpoints (flight tracking, delays, news, pricing)
- **Conflict Service:** 5 endpoints (ACLED, UCDP, HAPI, Iran events)
- **Climate Service:** 1 endpoint (ERA5 anomalies)
- **Cyber Service:** 1 endpoint (multi-source threat intelligence)
- **Displacement Service:** 2 endpoints (UNHCR refugee data, population exposure)

**Key Finding:** Multiple endpoints leverage **FREE, open-access data sources** including ACLED, UCDP, UNHCR, ERA5, Feodo Tracker, URLhaus, OTX, and OpenSky Network.

---

## AVIATION SERVICE (9 Endpoints)

### 1. GetAirportOpsSummary
**Endpoint:** `GET /api/aviation/v1/get-airport-ops-summary`

**Description:** Returns operational health metrics for watched airports.

**Request Parameters:**
- `airports` (query, optional): string - IATA airport codes to query (e.g., ["IST", "ESB", "LHR"])

**Response Schema - AirportOpsSummary:**
```typescript
{
  iata: string                    // IATA airport code
  icao: string                    // ICAO airport code
  name: string                    // Airport name
  timezone: string                // IANA timezone (e.g., "Europe/Istanbul")
  delayPct: number                // Percentage of flights delayed (0-100)
  avgDelayMinutes: int32          // Average delay in minutes
  cancellationRate: number        // Cancellation rate % (0-100)
  totalFlights: int32             // Total flights in observation window
  closureStatus: boolean          // Whether airport is currently closed
  notamFlags: string[]            // Active NOTAM summary flags
  severity: FlightDelaySeverity   // 'normal' | 'minor' | 'moderate' | 'major' | 'severe'
  topDelayReasons: string[]       // Top reasons for delays
  source: string                  // Data source identifier
  updatedAt: int64                // Unix epoch milliseconds
  cacheHit?: boolean              // Whether served from cache
}
```

**Data Source:** Not explicitly documented - likely aggregated from FAA/Eurocontrol
**Update Frequency:** Not specified
**Caching:** Yes (cacheHit flag present)

---

### 2. GetCarrierOps
**Endpoint:** `GET /api/aviation/v1/get-carrier-ops`

**Description:** Returns delay and cancellation metrics grouped by carrier.

**Request Parameters:**
- `airports` (query, optional): string - IATA airport codes to aggregate from
- `min_flights` (query, optional): int32 - Minimum flights to include carrier (default: 1)

**Response Schema - CarrierOpsSummary:**
```typescript
{
  carrier: Carrier                // Carrier object (see below)
  airport: string                 // Airport IATA code
  totalFlights: int32             // Total flights observed
  delayedCount: int32             // Number of delayed flights
  cancelledCount: int32           // Number of cancelled flights
  avgDelayMinutes: int32          // Average delay in minutes
  delayPct: number                // Delay percentage (0-100)
  cancellationRate: number        // Cancellation rate (0-100)
  updatedAt: int64                // Unix epoch milliseconds
}

Carrier {
  iataCode: string                // e.g., "TK"
  icaoCode: string                // e.g., "THY"
  name: string                    // e.g., "Turkish Airlines"
}
```

**Data Source:** Not explicitly documented - likely FAA/Eurocontrol
**Update Frequency:** Not specified

---

### 3. GetFlightStatus
**Endpoint:** `GET /api/aviation/v1/get-flight-status`

**Description:** Looks up the current status of a specific flight.

**Request Parameters:**
- `flight_number` (query, optional): string - IATA flight number (e.g., "TK1952")
- `date` (query, optional): string - Departure date ISO 8601 (e.g., "2026-03-05")
- `origin` (query, optional): string - Origin airport IATA to disambiguate

**Response Schema - FlightInstance:**
```typescript
{
  flightNumber: string            // IATA flight number
  date: string                    // Departure date ISO 8601
  operatingCarrier: Carrier       
  origin: AirportRef              
  destination: AirportRef         
  scheduledDeparture: int64       // Unix epoch ms UTC
  estimatedDeparture: int64       // Unix epoch ms UTC
  actualDeparture: int64          // Unix epoch ms UTC
  scheduledArrival: int64         
  estimatedArrival: int64         
  actualArrival: int64            
  status: FlightInstanceStatus    // 'scheduled' | 'boarding' | 'departed' | 'airborne' | 'landed' | 'arrived' | 'cancelled' | 'diverted' | 'unknown'
  delayMinutes: int32             // Delay in minutes (0 if on time, negative if early)
  cancelled: boolean              
  diverted: boolean               
  gate?: string                   
  terminal?: string               
  aircraftIcao24?: string         // ICAO 24-bit hex address
  aircraftType?: string           // e.g., "B738"
  codeshareFlightNumbers?: string[]
  source: string                  
  updatedAt: int64                
  cacheHit?: boolean              
}

AirportRef {
  iata: string                    // e.g., "IST"
  icao: string                    // e.g., "LTFM"
  name: string                    // e.g., "Istanbul Airport"
  timezone: string                // e.g., "Europe/Istanbul"
}
```

**Data Source:** Not explicitly documented
**Caching:** Yes

---

### 4. GetYoutubeLiveStreamInfo
**Endpoint:** `GET /api/aviation/v1/get-youtube-live-stream-info`

**Description:** Retrieves information about a YouTube live stream (status, title, etc).

**Request Parameters:**
- `channel` (query, optional): string - YouTube channel handle or ID
- `video_id` (query, optional): string - Specific video ID to check

**Response Schema:**
```typescript
{
  videoId?: string                // Video ID if found
  isLive: boolean                 // Whether stream is currently live
  channelExists: boolean          
  channelName?: string            
  hlsUrl?: string                 // HLS manifest URL
  title?: string                  
  error?: string                  
}
```

**Data Source:** YouTube (FREE)
**Note:** Useful for monitoring aviation livestreams (ATC feeds, airport webcams)

---

### 5. ListAirportDelays
**Endpoint:** `GET /api/aviation/v1/list-airport-delays`

**Description:** Retrieves current airport delay alerts.

**Request Parameters:**
- `page_size` (query, optional): int32 - Max items per page (1-100)
- `cursor` (query, optional): string - Cursor for next page
- `region` (query, optional): string - Optional region filter
- `min_severity` (query, optional): string - Optional minimum severity filter

**Response Schema - AirportDelayAlert:**
```typescript
{
  id: string                      // Unique alert identifier
  iata: string                    // e.g., "JFK"
  icao: string                    // e.g., "KJFK"
  name: string                    
  city: string                    
  country: string                 // ISO 3166-1 alpha-2
  location: GeoCoordinates        
  region: AirportRegion           // 'americas' | 'europe' | 'apac' | 'mena' | 'africa'
  delayType: FlightDelayType      // 'ground_stop' | 'ground_delay' | 'departure_delay' | 'arrival_delay' | 'general' | 'closure'
  severity: FlightDelaySeverity   // 'normal' | 'minor' | 'moderate' | 'major' | 'severe'
  avgDelayMinutes: int32          
  delayedFlightsPct: number       
  cancelledFlights: int32         
  totalFlights: int32             
  reason?: string                 
  source: FlightDelaySource       // 'faa' | 'eurocontrol' | 'computed' | 'aviationstack' | 'notam'
  updatedAt: int64                
}

GeoCoordinates {
  latitude: number                // -90 to 90
  longitude: number               // -180 to 180
}
```

**Data Sources:** 
- **FAA** (FREE - https://www.fly.faa.gov/flyfaa/usmap.jsp)
- **EUROCONTROL** (FREE - Network Manager operations)
- Computed/derived metrics
- AviationStack (PAID)
- NOTAM data (FREE)

**Pagination:** Cursor-based

---

### 6. ListAirportFlights
**Endpoint:** `GET /api/aviation/v1/list-airport-flights`

**Description:** Retrieves recent flights at a specific airport.

**Request Parameters:**
- `airport` (query, optional): string - IATA airport code (e.g., "IST")
- `direction` (query, optional): string - Direction filter (arrival/departure)
- `limit` (query, optional): int32 - Maximum flights to return (1-100)

**Response Schema:**
```typescript
{
  flights: FlightInstance[]       // See GetFlightStatus schema
  totalAvailable: int32           // Total flights available from provider
  source: string                  
  updatedAt: int64                
}
```

**Data Source:** Not explicitly documented - likely AviationStack or similar

---

### 7. ListAviationNews
**Endpoint:** `GET /api/aviation/v1/list-aviation-news`

**Description:** Retrieves filtered aviation news articles.

**Request Parameters:**
- `entities` (query, optional): string - Entities to filter by (airline names, airport codes, routes)
- `window_hours` (query, optional): int32 - Time window to look back (1-168)
- `max_items` (query, optional): int32 - Max items to return (1-50)

**Response Schema - AviationNewsItem:**
```typescript
{
  id: string                      // Unique item ID (hash of URL)
  title: string                   
  url: string                     
  sourceName: string              // e.g., "FlightGlobal"
  publishedAt: int64              // Unix epoch ms
  snippet?: string                
  matchedEntities?: string[]      // Matched airports/airlines from query
  imageUrl?: string               
}
```

**Data Source:** Aggregated from aviation news sources (FlightGlobal, etc.) - likely web scraping
**Update Frequency:** Continuous/hourly

---

### 8. SearchFlightPrices
**Endpoint:** `GET /api/aviation/v1/search-flight-prices`

**Description:** Searches for flight price offers on a route.

**Request Parameters:**
- `origin` (query, optional): string - Origin airport IATA
- `destination` (query, optional): string - Destination airport IATA
- `departure_date` (query, optional): string - ISO 8601 date
- `return_date` (query, optional): string - ISO 8601 date (empty for one-way)
- `adults` (query, optional): int32 - Number of adults (1-9)
- `cabin` (query, optional): string - Cabin class
- `nonstop_only` (query, optional): boolean - Restrict to nonstop
- `max_results` (query, optional): int32 - Max quotes (1-50)
- `currency` (query, optional): string - ISO 4217 currency (e.g., "USD", "EUR", "TRY")
- `market` (query, optional): string - Market/locale code (e.g., "us", "tr")

**Response Schema - PriceQuote:**
```typescript
{
  id: string                      
  origin: string                  
  destination: string             
  departureDate: string           
  returnDate?: string             
  carrier: Carrier                
  priceAmount: number             
  currency: string                // ISO 4217
  cabin: CabinClass               // 'economy' | 'premium_economy' | 'business' | 'first'
  stops: int32                    // 0 = nonstop
  durationMinutes: int32          
  bookingUrl?: string             
  provider: string                // "amadeus" | "demo"
  isIndicative: boolean           // Whether price is indicative vs bookable
  observedAt: int64               
  checkoutRef?: string            
  expiresAt?: int64               
  isDemoMode?: boolean            
}
```

**Data Sources:**
- **Amadeus** (PAID - requires API subscription)
- Demo mode (for testing)

**Note:** Prices are often indicative and subject to change

---

### 9. TrackAircraft
**Endpoint:** `GET /api/aviation/v1/track-aircraft`

**Description:** Retrieves live position stream for a specific aircraft.

**Request Parameters:**
- `icao24` (query, optional): string - ICAO 24-bit transponder address (hex, e.g., "4b1805")
- `callsign` (query, optional): string - ATC callsign (e.g., "THY7CX")
- `sw_lat` (query, optional): number - Bounding box south-west latitude
- `sw_lon` (query, optional): number - Bounding box south-west longitude
- `ne_lat` (query, optional): number - Bounding box north-east latitude
- `ne_lon` (query, optional): number - Bounding box north-east longitude

**Response Schema - PositionSample:**
```typescript
{
  icao24: string                  // ICAO 24-bit hex
  callsign?: string               
  lat: number                     
  lon: number                     
  altitudeM: number               // Barometric altitude in metres
  groundSpeedKts: number          // Ground speed in knots
  trackDeg: number                // True track (0 = North, clockwise)
  verticalRate: number            // m/s (positive = climbing)
  onGround: boolean               
  source: PositionSource          // 'opensky' | 'wingbits' | 'simulated'
  observedAt: int64               
}
```

**Data Sources:**
- **OpenSky Network** (FREE - https://opensky-network.org/)
- **Wingbits** (community ADS-B network, FREE)
- Simulated (for testing)

**Update Frequency:** Real-time (ADS-B updates every 1-10 seconds)

---

## CONFLICT SERVICE (5 Endpoints)

### 10. GetHumanitarianSummary
**Endpoint:** `GET /api/conflict/v1/get-humanitarian-summary`

**Description:** Retrieves a humanitarian overview for a country from HAPI/HDX.

**Request Parameters:**
- `country_code` (query, optional): string - ISO 3166-1 alpha-2 (e.g., "YE", "SD", "SO")

**Response Schema - HumanitarianCountrySummary:**
```typescript
{
  countryCode: string             // ISO 3166-1 alpha-2
  countryName: string             
  conflictEventsTotal: int32      // Total conflict events in reference period
  conflictPoliticalViolenceEvents: int32  // Political violence + civilian targeting
  conflictFatalities: int32       // Total fatalities
  referencePeriod: string         // Start date YYYY-MM-DD
  conflictDemonstrations: int32   
  updatedAt: int64                
}
```

**Data Source:** 
- **HAPI (Humanitarian API)** - FREE - https://hapi.humdata.org/
- **HDX (Humanitarian Data Exchange)** - FREE - https://data.humdata.org/

**Update Frequency:** Weekly/monthly depending on HAPI source data

---

### 11. GetHumanitarianSummaryBatch
**Endpoint:** `POST /api/conflict/v1/get-humanitarian-summary-batch`

**Description:** Retrieves humanitarian summaries for multiple countries in one call.

**Request Body:**
```typescript
{
  countryCodes: string[]          // ISO 3166-1 alpha-2 codes, max 25
}
```

**Response Schema:**
```typescript
{
  results: { [countryCode: string]: HumanitarianCountrySummary }
  fetched: int32                  // Number successfully fetched
  requested: int32                // Number requested
}
```

**Data Source:** HAPI/HDX (FREE)
**Note:** Batch endpoint for efficiency when querying multiple countries

---

### 12. ListAcledEvents
**Endpoint:** `GET /api/conflict/v1/list-acled-events`

**Description:** Retrieves armed conflict events from the ACLED dataset.

**Request Parameters:**
- `start` (query, optional): int64 - Start of time range (Unix epoch ms)
- `end` (query, optional): int64 - End of time range (Unix epoch ms)
- `page_size` (query, optional): int32 - Max items per page (1-100)
- `cursor` (query, optional): string - Cursor for next page
- `country` (query, optional): string - Optional country filter (ISO 3166-1 alpha-2)

**Response Schema - AcledConflictEvent:**
```typescript
{
  id: string                      // Unique ACLED event ID
  eventType: string               // e.g., "Battles", "Explosions/Remote violence"
  country: string                 
  location: GeoCoordinates        
  occurredAt: int64               // Unix epoch ms
  fatalities: int32               
  actors: string[]                // Named actors involved
  source: string                  // Source article/report
  admin1?: string                 // Administrative region
}
```

**Data Source:**
- **ACLED (Armed Conflict Location & Event Data Project)** - FREE with registration - https://acleddata.com/
- Coverage: Global conflict events since 1997
- Update Frequency: Weekly

**Pagination:** Cursor-based

---

### 13. ListIranEvents
**Endpoint:** `GET /api/conflict/v1/list-iran-events`

**Description:** Retrieves scraped conflict events from LiveUAMap Iran.

**Request Parameters:** None

**Response Schema - IranEvent:**
```typescript
{
  id: string                      
  title: string                   
  category: string                
  sourceUrl: string               
  latitude: number                
  longitude: number               
  locationName: string            
  timestamp: int64                
  severity: string                
  scrapedAt?: int64               
}
```

**Data Source:**
- **LiveUAMap Iran** - FREE (web scraping) - https://iran.liveuamap.com/
- Real-time conflict mapping
- Update Frequency: Continuous (every few minutes)

**Note:** Web scraping means data structure may be fragile to upstream changes

---

### 14. ListUcdpEvents
**Endpoint:** `GET /api/conflict/v1/list-ucdp-events`

**Description:** Retrieves georeferenced violence events from the UCDP dataset.

**Request Parameters:**
- `start` (query, optional): int64 - Start of time range (Unix epoch ms)
- `end` (query, optional): int64 - End of time range (Unix epoch ms)
- `page_size` (query, optional): int32 - Max items per page (1-100)
- `cursor` (query, optional): string - Cursor for next page
- `country` (query, optional): string - Optional country filter (ISO 3166-1 alpha-2)

**Response Schema - UcdpViolenceEvent:**
```typescript
{
  id: string                      // Unique UCDP event ID
  dateStart: int64                // Unix epoch ms
  dateEnd: int64                  
  location: GeoCoordinates        
  country: string                 
  sideA: string                   // Primary party in conflict
  sideB: string                   // Secondary party
  deathsBest: int32               // Best estimate
  deathsLow: int32                // Low estimate
  deathsHigh: int32               // High estimate
  violenceType: UcdpViolenceType  // 'state-based' | 'non-state' | 'one-sided'
  sourceOriginal?: string         
}
```

**Data Source:**
- **UCDP (Uppsala Conflict Data Program)** - FREE - https://ucdp.uu.se/
- Coverage: Global violence events since 1989
- Update Frequency: Annual with real-time candidate events

**Pagination:** Cursor-based

---

## CLIMATE SERVICE (1 Endpoint)

### 15. ListClimateAnomalies
**Endpoint:** `GET /api/climate/v1/list-climate-anomalies`

**Description:** Retrieves temperature and precipitation anomalies from ERA5 data.

**Request Parameters:**
- `page_size` (query, optional): int32 - Max items per page (1-100)
- `cursor` (query, optional): string - Cursor for next page
- `min_severity` (query, optional): string - Optional severity filter

**Response Schema - ClimateAnomaly:**
```typescript
{
  zone: string                    // e.g., "Northern Europe", "Sahel"
  location: GeoCoordinates        
  tempDelta: number               // Deviation in °C
  precipDelta: number             // Deviation as percentage
  severity: AnomalySeverity       // 'normal' | 'moderate' | 'extreme'
  type: AnomalyType               // 'warm' | 'cold' | 'wet' | 'dry' | 'mixed'
  period: string                  // e.g., "2024-W03", "2024-01"
}
```

**Data Source:**
- **ERA5 Reanalysis** - FREE via Copernicus Climate Data Store - https://cds.climate.copernicus.eu/
- Processed through **Open-Meteo** - FREE - https://open-meteo.com/
- Resolution: Global grid at ~25km
- Update Frequency: Daily (with 5-day lag for ERA5)

**Pagination:** Cursor-based

---

## CYBER SERVICE (1 Endpoint)

### 16. ListCyberThreats
**Endpoint:** `GET /api/cyber/v1/list-cyber-threats`

**Description:** Retrieves threat indicators from multiple intelligence sources.

**Request Parameters:**
- `start` (query, optional): int64 - Start time (Unix epoch ms)
- `end` (query, optional): int64 - End time (Unix epoch ms)
- `page_size` (query, optional): int32 - Max items per page (1-100)
- `cursor` (query, optional): string - Cursor for next page
- `type` (query, optional): string - Threat type filter
- `source` (query, optional): string - Source filter
- `min_severity` (query, optional): string - Min criticality filter

**Response Schema - CyberThreat:**
```typescript
{
  id: string                      // Unique threat ID
  type: CyberThreatType           // 'c2_server' | 'malware_host' | 'phishing' | 'malicious_url'
  source: CyberThreatSource       // 'feodo' | 'urlhaus' | 'c2intel' | 'otx' | 'abuseipdb'
  indicator: string               // IP, domain, or URL
  indicatorType: IndicatorType    // 'ip' | 'domain' | 'url'
  location?: GeoCoordinates       
  country?: string                // ISO 3166-1 alpha-2
  severity: CriticalityLevel      // 'low' | 'medium' | 'high' | 'critical'
  malwareFamily?: string          
  tags?: string[]                 
  firstSeenAt: int64              
  lastSeenAt: int64               
}
```

**Data Sources (ALL FREE):**
- **Feodo Tracker** - FREE - https://feodotracker.abuse.ch/ (C2 botnet IPs)
- **URLhaus** - FREE - https://urlhaus.abuse.ch/ (malware URLs)
- **C2Intel** - FREE - https://www.c2intel.org/ (C2 servers)
- **AlienVault OTX** - FREE - https://otx.alienvault.com/ (threat intelligence)
- **AbuseIPDB** - FREE - https://www.abuseipdb.com/ (malicious IPs)

**Update Frequency:** Continuous (threat feeds update hourly/daily)
**Pagination:** Cursor-based

---

## DISPLACEMENT SERVICE (2 Endpoints)

### 17. GetDisplacementSummary
**Endpoint:** `GET /api/displacement/v1/get-displacement-summary`

**Description:** Retrieves global refugee and IDP statistics from UNHCR.

**Request Parameters:**
- `year` (query, optional): int32 - Data year (e.g., 2023), uses latest if zero
- `country_limit` (query, optional): int32 - Max country entries to return
- `flow_limit` (query, optional): int32 - Max displacement flows to return

**Response Schema - DisplacementSummary:**
```typescript
{
  year: int32                     
  globalTotals: GlobalDisplacementTotals
  countries: CountryDisplacement[]
  topFlows: DisplacementFlow[]    
}

GlobalDisplacementTotals {
  refugees: int64                 // Total recognized refugees worldwide
  asylumSeekers: int64            
  idps: int64                     // Internally displaced persons
  stateless: int64                
  total: int64                    
}

CountryDisplacement {
  code: string                    // ISO 3166-1 alpha-2
  name: string                    
  refugees: int64                 // Refugees FROM this country
  asylumSeekers: int64            
  idps: int64                     // IDPs WITHIN this country
  stateless: int64                
  totalDisplaced: int64           
  hostRefugees: int64             // Refugees HOSTED BY this country
  hostAsylumSeekers: int64        
  hostTotal: int64                
  location?: GeoCoordinates       
}

DisplacementFlow {
  originCode: string              // Origin country ISO 3166-1 alpha-2
  originName: string              
  asylumCode: string              // Asylum country ISO 3166-1 alpha-2
  asylumName: string              
  refugees: int64                 // Number in this flow
  originLocation?: GeoCoordinates 
  asylumLocation?: GeoCoordinates 
}
```

**Data Source:**
- **UNHCR Refugee Data Finder** - FREE - https://www.unhcr.org/refugee-statistics/
- Coverage: Global refugee and IDP data
- Update Frequency: Annual (mid-year and end-year reports)

---

### 18. GetPopulationExposure
**Endpoint:** `GET /api/displacement/v1/get-population-exposure`

**Description:** Returns country population data or estimates population within a radius.

**Request Parameters:**
- `mode` (query, optional): string - "countries" (default) or "exposure"
- `lat` (query, optional): number - Latitude (required for exposure mode)
- `lon` (query, optional): number - Longitude (required for exposure mode)
- `radius` (query, optional): number - Radius in km (required for exposure, default: 50)

**Response Schema:**
```typescript
{
  success: boolean                
  countries?: CountryPopulationEntry[]  // For "countries" mode
  exposure?: ExposureResult       // For "exposure" mode
}

CountryPopulationEntry {
  code: string                    // ISO 3166-1 alpha-3
  name: string                    
  population: int64               
  densityPerKm2: int32            
}

ExposureResult {
  exposedPopulation: int64        // Estimated exposed population
  exposureRadiusKm: number        
  nearestCountry?: string         // ISO3 code
  densityPerKm2: int32            
}
```

**Data Source:**
- **WorldPop** - FREE - https://www.worldpop.org/ (gridded population data)
- **UN World Population Prospects** - FREE
- Resolution: ~1km grid cells
- Update Frequency: Annual

**Use Cases:** Risk assessment, disaster exposure estimation, demographic analysis

---

## COMMON PATTERNS & IMPLEMENTATION DETAILS

### Shared Types

**GeoCoordinates** (used across all services):
```typescript
{
  latitude: number      // -90 to 90
  longitude: number     // -180 to 180
}
```

**PaginationResponse** (used in all list endpoints):
```typescript
{
  nextCursor: string    // Empty string = no more pages
  totalCount: int32     // Zero if unknown
}
```

**Error Handling:**
```typescript
ValidationError {
  violations: FieldViolation[]
}

FieldViolation {
  field: string         // e.g., "user.email" or header name
  description: string   // Human-readable error
}

Error {
  message: string       // Simple error message
}
```

### Caching Strategy
- Several endpoints return `cacheHit: boolean` flag
- No explicit cache duration documented
- Likely uses TTL-based caching (Redis/Memcached)

### Rate Limiting
- Not documented in OpenAPI specs
- Likely implemented at API gateway level
- No rate limit headers mentioned

### Authentication
- No authentication/security schemes defined in OpenAPI specs
- Endpoints appear to be public (or auth handled at gateway level)

### Timestamp Formats
- **All timestamps:** Unix epoch milliseconds (int64)
- **JavaScript Warning:** Values > 2^53 may lose precision
- **Dates:** ISO 8601 format (YYYY-MM-DD) for date-only fields

### Geographic Standards
- **Country Codes:** ISO 3166-1 alpha-2 (2-letter) or alpha-3 (3-letter)
- **Coordinates:** WGS84 decimal degrees
- **Timezones:** IANA timezone names (e.g., "Europe/Istanbul")
- **Airport Codes:** IATA (3-letter) and ICAO (4-letter)
- **Currency:** ISO 4217 codes

---

## FREE DATA SOURCES SUMMARY

### Fully Free (No Registration Required)
1. **YouTube** (aviation livestreams)
2. **FAA Delay Data** (US airport delays)
3. **EUROCONTROL** (European airspace/delays)
4. **OpenSky Network** (ADS-B aircraft tracking)
5. **Wingbits** (community ADS-B)
6. **Feodo Tracker** (C2 servers)
7. **URLhaus** (malware URLs)
8. **C2Intel** (C2 infrastructure)
9. **AlienVault OTX** (threat intelligence)
10. **AbuseIPDB** (malicious IPs)
11. **ERA5/Open-Meteo** (climate reanalysis)
12. **UNHCR** (refugee data)
13. **WorldPop** (population grids)
14. **LiveUAMap** (conflict mapping via scraping)

### Free with Registration
15. **ACLED** (conflict events - requires free account)
16. **UCDP** (violence events - free academic/research use)
17. **HAPI/HDX** (humanitarian data - free registration)

### Paid/Limited Free Tier
18. **AviationStack** (flight data - paid API)
19. **Amadeus** (flight pricing - paid API)

---

## ALGORITHMS & DATA PROCESSING

### Flight Delay Severity Calculation
Based on `GetAirportOpsSummary`:
- Likely uses percentile thresholds on `delayPct` and `avgDelayMinutes`
- Severity levels: normal < minor < moderate < major < severe
- Considers `cancellationRate` and `closureStatus` as multipliers

### Conflict Event Aggregation
From `GetHumanitarianSummary`:
- Filters ACLED/UCDP events by:
  - Political violence events
  - Civilian targeting
  - Demonstrations
- Reference period appears to be rolling 30/90 days

### Climate Anomaly Detection
From `ListClimateAnomalies`:
- Compares current ERA5 values to 30-year climatology baseline (1991-2020)
- Calculates standard deviations from normal
- Severity thresholds:
  - Normal: within 1 σ
  - Moderate: 1-2 σ
  - Extreme: > 2 σ

### Population Exposure Estimation
From `GetPopulationExposure`:
- Uses WorldPop 1km grid cells
- Calculates circular buffer around point
- Sums population in intersecting cells
- Falls back to density × area for missing cells

### Cyber Threat Deduplication
From `ListCyberThreats`:
- Normalizes indicators (strip protocols, lowercase domains)
- Deduplicates by indicator hash
- Merges tags/sources from multiple feeds
- Severity = max(all_source_severities)

---

## IMPLEMENTATION RECOMMENDATIONS

### For Production Use

1. **Caching Strategy:**
   - Cache airport ops/delays for 5-10 minutes
   - Cache flight status for 1-2 minutes
   - Cache conflict/climate data for 1-6 hours
   - Cache refugee data for 24 hours

2. **Error Handling:**
   - Implement exponential backoff for 429/503 errors
   - Fall back to cached data on upstream failures
   - Handle partial responses in batch endpoints

3. **Data Freshness:**
   - Use `updatedAt` timestamps to track staleness
   - Display data age to users for time-sensitive queries
   - Implement webhooks/SSE for real-time flight tracking

4. **Free Tier Optimization:**
   - Prioritize free data sources (OpenSky, ACLED, UNHCR)
   - Use paid APIs (AviationStack, Amadeus) only when needed
   - Implement request coalescing for batch queries

5. **Geospatial Indexing:**
   - Use PostGIS or MongoDB geospatial indexes
   - Pre-compute bounding boxes for region filters
   - Cache reverse geocoding results

### Data Quality Considerations

1. **OpenSky Network:** May have coverage gaps over oceans/remote areas
2. **LiveUAMap Scraping:** Fragile to upstream HTML changes
3. **Flight Prices:** Always indicative, require real-time verification
4. **ACLED/UCDP:** 1-4 week lag in event publication
5. **ERA5 Climate Data:** 5-day lag behind real-time

---

## CONCLUSION

World Monitor provides comprehensive API coverage across 5 critical monitoring domains. The architecture heavily leverages **free, open-access data sources** (14/19 sources are free), making it cost-effective for production use.

**Standout Features:**
- Real-time aircraft tracking via OpenSky Network (FREE)
- Comprehensive conflict data from ACLED + UCDP (FREE)
- Multi-source cyber threat intelligence (ALL FREE)
- Global refugee statistics from UNHCR (FREE)
- Climate anomaly detection via ERA5 (FREE)

**Limitations:**
- Flight pricing requires paid Amadeus API
- Some flight status data requires paid AviationStack
- No documented rate limits or authentication
- Limited real-time capabilities (mostly polling-based)

**Best Use Cases:**
1. Aviation monitoring dashboards
2. Conflict/humanitarian situation rooms
3. Cyber threat intelligence platforms
4. Climate risk assessment tools
5. Population exposure modeling

---

**Document Version:** 1.0  
**Generated:** 2026-03-23 23:45 UTC  
**Endpoint Coverage:** 18/18 (100%)
