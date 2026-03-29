# World Monitor API Reference: Market, Military & Maritime Services

**Crawled:** 2026-03-23  
**Total Endpoints:** 25 (15 Market, 8 Military, 2 Maritime)

---

## MARKET SERVICE (15 endpoints)

### 1. AnalyzeStock
**RPC:** `MarketService.AnalyzeStock`  
**Method:** GET `/api/market/v1/analyze-stock`  
**Description:** Premium stock analysis report with technicals, news, and AI synthesis.

**Request Parameters:**
- `symbol` (string, optional): Ticker symbol
- `name` (string, optional): Company name
- `include_news` (boolean, optional): Include news summary

**Response Schema:** `AnalyzeStockResponse`
- `available` (boolean)
- `symbol`, `name`, `display`, `currency` (string)
- `currentPrice`, `changePercent`, `signalScore` (double)
- `signal`, `trendStatus`, `volumeStatus`, `macdStatus`, `rsiStatus` (string)
- `summary`, `action`, `confidence`, `technicalSummary`, `newsSummary`, `whyNow` (string)
- `bullishFactors`, `riskFactors` (string[])
- `supportLevels`, `resistanceLevels` (double[])
- `headlines` (StockAnalysisHeadline[])
- `ma5`, `ma10`, `ma20`, `ma60`, `biasMa5`, `biasMa10`, `biasMa20`, `volumeRatio5d`, `rsi12`, `macdDif`, `macdDea`, `macdBar`, `stopLoss`, `takeProfit` (double)
- `provider`, `model`, `engineVersion`, `generatedAt`, `analysisId` (string)
- `analysisAt` (int64)
- `fallback`, `newsSearched` (boolean)

**Upstream Source:** Not explicitly stated (premium analysis engine)  
**Free/Paid:** Premium (requires backend analysis)  
**Caching:** None mentioned  
**Algorithms:** AI-powered technical analysis + news synthesis

---

### 2. BacktestStock
**RPC:** `MarketService.BacktestStock`  
**Method:** GET `/api/market/v1/backtest-stock`  
**Description:** Replays premium stock-analysis signals over recent price history.

**Request Parameters:**
- `symbol` (string, optional): Ticker symbol
- `name` (string, optional): Company name
- `eval_window_days` (int32, optional): Evaluation window in days

**Response Schema:** `BacktestStockResponse`
- `available` (boolean)
- `symbol`, `name`, `display`, `currency`, `engineVersion`, `generatedAt` (string)
- `evalWindowDays`, `evaluationsRun`, `actionableEvaluations` (int32)
- `winRate`, `directionAccuracy`, `avgSimulatedReturnPct`, `cumulativeSimulatedReturnPct`, `latestSignalScore` (double)
- `latestSignal`, `summary` (string)
- `evaluations` (BacktestStockEvaluation[])
  - `analysisAt` (int64)
  - `signal`, `analysisId`, `outcome` (string)
  - `signalScore`, `entryPrice`, `exitPrice`, `simulatedReturnPct`, `stopLoss`, `takeProfit` (double)
  - `directionCorrect` (boolean)

**Upstream Source:** Historical price data + analysis engine  
**Free/Paid:** Premium (requires historical analysis)  
**Caching:** None mentioned  
**Algorithms:** Backtesting signals with simulated trades

---

### 3. GetCountryStockIndex
**RPC:** `MarketService.GetCountryStockIndex`  
**Method:** GET `/api/market/v1/get-country-stock-index`  
**Description:** Retrieves the primary stock index for a country from Yahoo Finance.

**Request Parameters:**
- `country_code` (string, optional): ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "JP")

**Response Schema:** `GetCountryStockIndexResponse`
- `available` (boolean)
- `code`, `symbol`, `indexName`, `currency`, `fetchedAt` (string)
- `price`, `weekChangePercent` (double)

**Upstream Source:** Yahoo Finance  
**Free/Paid:** **FREE** (Yahoo Finance public API)  
**Caching:** Not specified  
**Algorithms:** Country-to-index mapping lookup

---

### 4. GetSectorSummary
**RPC:** `MarketService.GetSectorSummary`  
**Method:** GET `/api/market/v1/get-sector-summary`  
**Description:** Retrieves market sector performance data from Finnhub.

**Request Parameters:**
- `period` (string, optional): Time period (e.g., "1d", "1w", "1m"), defaults to "1d"

**Response Schema:** `GetSectorSummaryResponse`
- `sectors` (SectorPerformance[])
  - `symbol` (string, required)
  - `name` (string)
  - `change` (double)

**Upstream Source:** Finnhub  
**Free/Paid:** Requires FINNHUB_API_KEY (may have free tier)  
**Caching:** Not specified  
**Algorithms:** Sector aggregation

---

### 5. GetStockAnalysisHistory
**RPC:** `MarketService.GetStockAnalysisHistory`  
**Method:** GET `/api/market/v1/get-stock-analysis-history`  
**Description:** Retrieves shared premium stock analysis history from the backend store.

**Request Parameters:**
- `symbols` (string, optional): Comma-separated ticker symbols
- `limit_per_symbol` (int32, optional): Max snapshots per symbol
- `include_news` (boolean, optional): Include news data

**Response Schema:** `GetStockAnalysisHistoryResponse`
- `items` (StockAnalysisHistoryItem[])
  - `symbol` (string)
  - `snapshots` (AnalyzeStockResponse[])

**Upstream Source:** Backend analysis store  
**Free/Paid:** Premium (stored analysis history)  
**Caching:** Backend store acts as cache  
**Algorithms:** Historical snapshot retrieval

---

### 6. ListAiTokens
**RPC:** `MarketService.ListAiTokens`  
**Method:** GET `/api/market/v1/list-ai-tokens`  
**Description:** Retrieves AI-sector crypto token prices and changes.

**Request Parameters:** None

**Response Schema:** `ListAiTokensResponse`
- `tokens` (CryptoQuote[])
  - `symbol` (string, required)
  - `name`, `price`, `change`, `change7d` (double)
  - `sparkline` (double[])

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** Token category filtering

---

### 7. ListCommodityQuotes
**RPC:** `MarketService.ListCommodityQuotes`  
**Method:** GET `/api/market/v1/list-commodity-quotes`  
**Description:** Retrieves commodity market quotes (gold, oil, etc.) from Yahoo Finance.

**Request Parameters:**
- `symbols` (string, optional): Comma-separated commodity symbols (e.g., "GC=F,CL=F")

**Response Schema:** `ListCommodityQuotesResponse`
- `quotes` (CommodityQuote[])
  - `symbol` (string, required)
  - `name`, `display` (string)
  - `price`, `change` (double)
  - `sparkline` (double[])

**Upstream Source:** Yahoo Finance  
**Free/Paid:** **FREE** (Yahoo Finance public API)  
**Caching:** Not specified  
**Algorithms:** Commodity quote lookup

---

### 8. ListCryptoQuotes
**RPC:** `MarketService.ListCryptoQuotes`  
**Method:** GET `/api/market/v1/list-crypto-quotes`  
**Description:** Retrieves cryptocurrency quotes from CoinGecko.

**Request Parameters:**
- `coin_ids` (string, optional): Comma-separated CoinGecko IDs (e.g., "bitcoin,ethereum")

**Response Schema:** `ListCryptoQuotesResponse`
- `quotes` (CryptoQuote[])
  - `symbol` (string, required)
  - `name` (string)
  - `price`, `change`, `change7d` (double)
  - `sparkline` (double[])

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** Direct CoinGecko API passthrough

---

### 9. ListCryptoSectors
**RPC:** `MarketService.ListCryptoSectors`  
**Method:** GET `/api/market/v1/list-crypto-sectors`  
**Description:** Retrieves crypto sector performance data.

**Request Parameters:** None

**Response Schema:** `ListCryptoSectorsResponse`
- `sectors` (CryptoSector[])
  - `name` (string)
  - `marketCapUsd`, `change24h` (double)

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** Sector aggregation from CoinGecko

---

### 10. ListDefiTokens
**RPC:** `MarketService.ListDefiTokens`  
**Method:** GET `/api/market/v1/list-defi-tokens`  
**Description:** Retrieves DeFi crypto token prices and changes.

**Request Parameters:** None

**Response Schema:** `ListDefiTokensResponse`
- `tokens` (CryptoQuote[])

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** DeFi category filtering

---

### 11. ListEtfFlows
**RPC:** `MarketService.ListEtfFlows`  
**Method:** GET `/api/market/v1/list-etf-flows`  
**Description:** Retrieves ETF flow data (inflows/outflows).

**Request Parameters:**
- `period` (string, optional): Time period (e.g., "1d", "1w", "1m")

**Response Schema:** `ListEtfFlowsResponse`
- `flows` (EtfFlow[])
  - `symbol`, `name` (string)
  - `flowUsd`, `assetsUsd`, `changePercent` (double)

**Upstream Source:** Not explicitly stated (likely proprietary or premium provider)  
**Free/Paid:** Likely premium (ETF flow data is specialized)  
**Caching:** Not specified  
**Algorithms:** ETF flow aggregation

---

### 12. ListGulfQuotes
**RPC:** `MarketService.ListGulfQuotes`  
**Method:** GET `/api/market/v1/list-gulf-quotes`  
**Description:** Retrieves Gulf region market quotes (indices, currencies, oil).

**Request Parameters:** None

**Response Schema:** `ListGulfQuotesResponse`
- `quotes` (GulfQuote[])
  - `symbol`, `name`, `flag`, `country`, `type` (string)
  - `price`, `change` (double)
  - `sparkline` (double[])
- `rateLimited` (boolean)

**Upstream Source:** Not explicitly stated (likely regional market data provider)  
**Free/Paid:** Not specified  
**Caching:** Not specified  
**Algorithms:** Gulf region quote aggregation

---

### 13. ListMarketQuotes
**RPC:** `MarketService.ListMarketQuotes`  
**Method:** GET `/api/market/v1/list-market-quotes`  
**Description:** Retrieves stock and index quotes.

**Request Parameters:**
- `symbols` (string, optional): Ticker symbols (e.g., ["AAPL", "^GSPC"]). Empty returns defaults.

**Response Schema:** `ListMarketQuotesResponse`
- `quotes` (MarketQuote[])
  - `symbol` (string, required)
  - `name`, `display` (string)
  - `price`, `change` (double)
  - `sparkline` (double[])
- `finnhubSkipped` (boolean)
- `skipReason` (string)
- `rateLimited` (boolean)

**Upstream Source:** Finnhub + Yahoo Finance (fallback)  
**Free/Paid:** **Finnhub requires API key** (free tier available), Yahoo Finance is FREE  
**Caching:** Not specified  
**Algorithms:** Multi-source quote aggregation with fallback

---

### 14. ListOtherTokens
**RPC:** `MarketService.ListOtherTokens`  
**Method:** GET `/api/market/v1/list-other-tokens`  
**Description:** Retrieves other/trending crypto token prices and changes.

**Request Parameters:** None

**Response Schema:** `ListOtherTokensResponse`
- `tokens` (CryptoQuote[])

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** Trending/other category filtering

---

### 15. ListStablecoinMarkets
**RPC:** `MarketService.ListStablecoinMarkets`  
**Method:** GET `/api/market/v1/list-stablecoin-markets`  
**Description:** Retrieves stablecoin peg health and market data from CoinGecko.

**Request Parameters:**
- `coins` (string, optional): CoinGecko IDs (e.g., "tether,usd-coin"). Empty returns defaults.

**Response Schema:** `ListStablecoinMarketsResponse`
- `timestamp` (string)
- `summary` (StablecoinSummary)
  - `totalMarketCap`, `totalVolume24h` (double)
  - `coinCount`, `depeggedCount` (int32)
  - `healthStatus` (string: "HEALTHY" | "CAUTION" | "WARNING")
- `stablecoins` (Stablecoin[])
  - `id`, `symbol` (string, required)
  - `name`, `image`, `pegStatus` (string)
  - `price`, `deviation`, `marketCap`, `volume24h`, `change24h`, `change7d` (double)

**Upstream Source:** CoinGecko  
**Free/Paid:** **FREE** (CoinGecko free API)  
**Caching:** Not specified  
**Algorithms:** Peg deviation calculation (distance from $1.00)

---

## MILITARY SERVICE (8 endpoints)

### 16. GetAircraftDetails
**RPC:** `MilitaryService.GetAircraftDetails`  
**Method:** GET `/api/military/v1/get-aircraft-details`  
**Description:** Retrieves Wingbits aircraft enrichment data for a single ICAO24 hex.

**Request Parameters:**
- `icao24` (string, optional): ICAO 24-bit hex address (lowercase)

**Response Schema:** `GetAircraftDetailsResponse`
- `details` (AircraftDetails)
  - `icao24`, `registration`, `manufacturerIcao`, `manufacturerName`, `model`, `typecode`, `serialNumber`, `icaoAircraftType`, `operator`, `operatorCallsign`, `operatorIcao`, `owner`, `built`, `engines`, `categoryDescription` (string)
- `configured` (boolean)

**Upstream Source:** Wingbits API (ecs-api.wingbits.com)  
**Free/Paid:** Requires WINGBITS_API_KEY (paid service)  
**Caching:** Not specified  
**Algorithms:** ICAO24 lookup enrichment

---

### 17. GetAircraftDetailsBatch
**RPC:** `MilitaryService.GetAircraftDetailsBatch`  
**Method:** POST `/api/military/v1/get-aircraft-details-batch`  
**Description:** Retrieves Wingbits aircraft enrichment data for multiple ICAO24 hexes.

**Request Parameters:**
- `icao24s` (string[], required): Array of ICAO 24-bit hex addresses (lowercase). Max 20, min 1.

**Response Schema:** `GetAircraftDetailsBatchResponse`
- `results` (map<string, AircraftDetails>): Map of icao24 -> aircraft details
- `fetched`, `requested` (int32)
- `configured` (boolean)

**Upstream Source:** Wingbits API  
**Free/Paid:** Requires WINGBITS_API_KEY (paid service)  
**Caching:** Not specified  
**Algorithms:** Batch ICAO24 lookup

---

### 18. GetTheaterPosture
**RPC:** `MilitaryService.GetTheaterPosture`  
**Method:** GET `/api/military/v1/get-theater-posture`  
**Description:** Retrieves military posture assessments for geographic theaters.

**Request Parameters:**
- `theater` (string, optional): Theater name (e.g., "indo-pacific", "european", "middle-east"). Empty for all theaters.

**Response Schema:** `GetTheaterPostureResponse`
- `theaters` (TheaterPosture[])
  - `theater`, `postureLevel` (string)
  - `activeFlights`, `trackedVessels` (int32)
  - `activeOperations` (string[])
  - `assessedAt` (int64)

**Upstream Source:** Aggregated from OpenSky + Wingbits + internal assessment  
**Free/Paid:** Mixed (OpenSky is FREE, Wingbits requires API key)  
**Caching:** Not specified  
**Algorithms:** Theater posture aggregation and assessment

---

### 19. GetUSNIFleetReport
**RPC:** `MilitaryService.GetUSNIFleetReport`  
**Method:** GET `/api/military/v1/get-usni-fleet-report`  
**Description:** Retrieves the latest parsed USNI Fleet Tracker report.

**Request Parameters:**
- `force_refresh` (boolean, optional): Bypass cache and fetch fresh data from USNI

**Response Schema:** `GetUSNIFleetReportResponse`
- `report` (USNIFleetReport)
  - `articleUrl`, `articleDate`, `articleTitle` (string)
  - `battleForceSummary` (BattleForceSummary)
    - `totalShips`, `deployed`, `underway` (int32)
  - `vessels` (USNIVessel[])
    - `name`, `hullNumber` (string, required)
    - `vesselType`, `region`, `deploymentStatus`, `homePort`, `strikeGroup`, `activityDescription`, `articleUrl`, `articleDate` (string)
    - `regionLat`, `regionLon` (double)
  - `strikeGroups` (USNIStrikeGroup[])
    - `name`, `carrier`, `airWing`, `destroyerSquadron` (string)
    - `escorts` (string[])
  - `regions` (string[])
  - `parsingWarnings` (string[])
  - `timestamp` (int64)
- `cached`, `stale` (boolean)
- `error` (string)

**Upstream Source:** USNI Fleet Tracker (news.usni.org)  
**Free/Paid:** **FREE** (publicly available USNI articles)  
**Caching:** Yes (with stale flag on fetch failure)  
**Algorithms:** Article parsing, vessel extraction, region mapping

---

### 20. GetWingbitsLiveFlight
**RPC:** `MilitaryService.GetWingbitsLiveFlight`  
**Method:** GET `/api/military/v1/get-wingbits-live-flight`  
**Description:** Retrieves real-time position data from the Wingbits ECS network for a single aircraft.

**Request Parameters:**
- `icao24` (string, optional): ICAO 24-bit hex address (lowercase, 6 characters)

**Response Schema:** `GetWingbitsLiveFlightResponse`
- `flight` (WingbitsLiveFlight)
  - `icao24`, `callsign`, `registration`, `model`, `operator` (string)
  - `lat`, `lon`, `altitude`, `speed`, `heading`, `verticalRate` (double)
  - `onGround` (boolean)
  - `lastSeen` (int64)
  - **Schedule fields:** `depIata`, `arrIata`, `depTimeUtc`, `arrTimeUtc`, `depEstimatedUtc`, `arrEstimatedUtc`, `flightStatus`, `arrTerminal` (string)
  - `depDelayedMin`, `arrDelayedMin`, `flightDurationMin` (int32)
  - **Photo fields:** `photoUrl`, `photoLink`, `photoCredit` (string)
  - **Airline fields:** `callsignIata`, `airlineName` (string)

**Upstream Source:** Wingbits ECS API (ecs-api.wingbits.com/v1/flights) + Planespotters.net (photos)  
**Free/Paid:** Requires WINGBITS_API_KEY (paid service)  
**Caching:** Not specified  
**Algorithms:** Live flight tracking + schedule enrichment + photo lookup

---

### 21. GetWingbitsStatus
**RPC:** `MilitaryService.GetWingbitsStatus`  
**Method:** GET `/api/military/v1/get-wingbits-status`  
**Description:** Checks whether the Wingbits enrichment API is configured.

**Request Parameters:** None

**Response Schema:** `GetWingbitsStatusResponse`
- `configured` (boolean)

**Upstream Source:** Internal config check  
**Free/Paid:** N/A (status check)  
**Caching:** N/A  
**Algorithms:** Environment variable check

---

### 22. ListMilitaryBases
**RPC:** `MilitaryService.ListMilitaryBases`  
**Method:** GET `/api/military/v1/list-military-bases`  
**Description:** Retrieves military bases within a bounding box, with server-side clustering.

**Request Parameters:**
- `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` (double, optional): Bounding box
- `zoom` (int32, optional): Zoom level for clustering
- `type`, `kind`, `country` (string, optional): Filters

**Response Schema:** `ListMilitaryBasesResponse`
- `bases` (MilitaryBaseEntry[])
  - `id`, `name`, `kind`, `countryIso2`, `type`, `branch`, `status` (string)
  - `latitude`, `longitude` (double)
  - `tier` (int32)
  - `catAirforce`, `catNaval`, `catNuclear`, `catSpace`, `catTraining` (boolean)
- `clusters` (MilitaryBaseCluster[])
  - `latitude`, `longitude` (double)
  - `count`, `expansionZoom` (int32)
  - `dominantType` (string)
- `totalInView` (int32)
- `truncated` (boolean)

**Upstream Source:** Internal military base database (likely OpenStreetMap + curated sources)  
**Free/Paid:** **FREE** (public military base locations)  
**Caching:** Not specified  
**Algorithms:** Geospatial bounding box query + clustering

---

### 23. ListMilitaryFlights
**RPC:** `MilitaryService.ListMilitaryFlights`  
**Method:** GET `/api/military/v1/list-military-flights`  
**Description:** Retrieves tracked military aircraft from OpenSky and Wingbits.

**Request Parameters:**
- `page_size` (int32, optional): Max items per page (1-100)
- `cursor` (string, optional): Pagination cursor
- `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` (double, optional): Bounding box
- `operator`, `aircraft_type` (string, optional): Filters

**Response Schema:** `ListMilitaryFlightsResponse`
- `flights` (MilitaryFlight[])
  - `id` (string, required)
  - `callsign`, `hexCode`, `registration`, `aircraftModel`, `operatorCountry`, `origin`, `destination`, `squawk`, `note`, `analysisId` (string)
  - `aircraftType` (enum: FIGHTER | BOMBER | TRANSPORT | TANKER | AWACS | RECONNAISSANCE | HELICOPTER | DRONE | PATROL | SPECIAL_OPS | VIP | UNKNOWN)
  - `operator` (enum: USAF | USN | USMC | USA | RAF | RN | FAF | GAF | PLAAF | PLAN | VKS | IAF | NATO | OTHER)
  - `location` (GeoCoordinates)
  - `altitude`, `heading`, `speed`, `verticalRate` (double)
  - `onGround`, `isInteresting` (boolean)
  - `lastSeenAt`, `firstSeenAt` (int64)
  - `confidence` (enum: LOW | MEDIUM | HIGH)
  - `enrichment` (FlightEnrichment)
- `clusters` (MilitaryFlightCluster[])
  - `id`, `name`, `dominantOperator`, `activityType` (string)
  - `location` (GeoCoordinates)
  - `flightCount` (int32)
  - `flights` (MilitaryFlight[])
- `pagination` (PaginationResponse)

**Upstream Source:** OpenSky Network (FREE) + Wingbits (paid)  
**Free/Paid:** Mixed (OpenSky is FREE, Wingbits requires API key for enrichment)  
**Caching:** Not specified  
**Algorithms:** Military aircraft filtering + clustering + enrichment

---

## MARITIME SERVICE (2 endpoints)

### 24. GetVesselSnapshot
**RPC:** `MaritimeService.GetVesselSnapshot`  
**Method:** GET `/api/maritime/v1/get-vessel-snapshot`  
**Description:** Retrieves a point-in-time view of AIS vessel traffic and disruptions.

**Request Parameters:**
- `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` (double, optional): Bounding box

**Response Schema:** `GetVesselSnapshotResponse`
- `snapshot` (VesselSnapshot)
  - `snapshotAt` (int64)
  - `densityZones` (AisDensityZone[])
    - `id` (string, required)
    - `name`, `note` (string)
    - `location` (GeoCoordinates)
    - `intensity` (double, 0-100)
    - `deltaPct` (double)
    - `shipsPerDay` (int32)
  - `disruptions` (AisDisruption[])
    - `id` (string, required)
    - `name`, `region`, `description` (string)
    - `type` (enum: GAP_SPIKE | CHOKEPOINT_CONGESTION)
    - `severity` (enum: LOW | ELEVATED | HIGH)
    - `location` (GeoCoordinates)
    - `changePct` (double)
    - `windowHours`, `darkShips`, `vesselCount` (int32)

**Upstream Source:** AIS tracking network (likely MarineTraffic or similar)  
**Free/Paid:** Likely paid (AIS data is typically commercial)  
**Caching:** Not specified  
**Algorithms:** AIS traffic density analysis + disruption detection

---

### 25. ListNavigationalWarnings
**RPC:** `MaritimeService.ListNavigationalWarnings`  
**Method:** GET `/api/maritime/v1/list-navigational-warnings`  
**Description:** Retrieves active maritime safety warnings from NGA.

**Request Parameters:**
- `page_size` (int32, optional): Max items per page (1-100)
- `cursor` (string, optional): Pagination cursor
- `area` (string, optional): Area filter (e.g., "NAVAREA IV", "Persian Gulf")

**Response Schema:** `ListNavigationalWarningsResponse`
- `warnings` (NavigationalWarning[])
  - `id`, `title`, `text`, `area`, `authority` (string)
  - `location` (GeoCoordinates)
  - `issuedAt`, `expiresAt` (int64)
- `pagination` (PaginationResponse)

**Upstream Source:** NGA (National Geospatial-Intelligence Agency)  
**Free/Paid:** **FREE** (NGA publishes warnings publicly)  
**Caching:** Not specified  
**Algorithms:** NGA warning scraping + geospatial indexing

---

## Summary: Free vs Paid Data Sources

### ✅ FREE Data Sources
1. **Yahoo Finance** (GetCountryStockIndex, ListCommodityQuotes)
2. **CoinGecko** (ListAiTokens, ListCryptoQuotes, ListCryptoSectors, ListDefiTokens, ListOtherTokens, ListStablecoinMarkets)
3. **OpenSky Network** (ListMilitaryFlights — partial)
4. **USNI Fleet Tracker** (GetUSNIFleetReport)
5. **NGA** (ListNavigationalWarnings)
6. **OpenStreetMap/Curated** (ListMilitaryBases)

### 💰 PAID Data Sources
1. **Finnhub** (ListMarketQuotes, GetSectorSummary — requires API key)
2. **Wingbits** (GetAircraftDetails, GetAircraftDetailsBatch, GetWingbitsLiveFlight, ListMilitaryFlights enrichment — requires API key)
3. **AIS Networks** (GetVesselSnapshot — likely commercial)
4. **Premium Analysis Engine** (AnalyzeStock, BacktestStock, GetStockAnalysisHistory)
5. **ETF Flow Providers** (ListEtfFlows — likely premium)

### ⚠️ UNSPECIFIED
- ListGulfQuotes (likely regional provider)

---

## Key Implementation Details

### Caching Strategy
- **USNIFleetReport:** Explicit caching with `force_refresh` param and `stale` flag
- **Most endpoints:** No explicit caching documented (likely HTTP-level caching)

### Rate Limiting
- **ListMarketQuotes:** Includes `rateLimited` boolean flag
- **ListGulfQuotes:** Includes `rateLimited` boolean flag
- **Finnhub:** Has rate limits (not documented in schemas)

### Pagination
- **ListMilitaryFlights, ListNavigationalWarnings:** Use cursor-based pagination
- **PaginationResponse schema:** `nextCursor` (string), `totalCount` (int32)

### Error Handling
- All endpoints return `ValidationError` (400) for bad requests
- `ValidationError` contains `FieldViolation[]` with `field` and `description`
- Generic `Error` schema for 500-level errors

### Geospatial Queries
- **Bounding box pattern:** `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` (consistent across endpoints)
- **GeoCoordinates schema:** `latitude` (-90 to 90), `longitude` (-180 to 180)

### Clustering
- **ListMilitaryBases:** Server-side clustering with `expansionZoom`
- **ListMilitaryFlights:** Cluster response with `dominantOperator` and `activityType`

---

## Notes
- **AI-Powered Features:** AnalyzeStock and BacktestStock use LLM-based analysis (provider/model fields)
- **Military Data Confidence:** Uses 3-level confidence system (LOW | MEDIUM | HIGH)
- **Stablecoin Health:** Custom peg deviation algorithm with severity classification
- **Fleet Tracking:** USNI article parsing with structured vessel extraction
- **Aviation Enrichment:** Multi-source (Wingbits + Planespotters + schedule APIs)

**End of Report**
