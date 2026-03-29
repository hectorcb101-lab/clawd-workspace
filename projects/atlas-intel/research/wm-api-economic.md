# World Monitor API — Economic Service Research

**Comprehensive Analysis of 14 Economic Service Endpoints**

Compiled: 2026-03-23 23:45 UTC

---

## Overview

The Economic Service provides access to **14 endpoints** across **6 upstream data sources**:
- Bank for International Settlements (BIS) — **FREE**
- Bureau of Labor Statistics (BLS) — **FREE**
- Federal Reserve Economic Data (FRED) — **FREE**
- US Energy Information Administration (EIA) — **FREE**
- World Bank Open Data — **FREE**
- Custom World Monitor aggregations (Big Mac, Fuel, Grocery, National Debt, Macro Signals)

**All upstream sources are publicly accessible and free.**

---

## Endpoints by Category

### BIS Data (Bank for International Settlements) — 3 Endpoints

#### 1. GetBisCredit
**RPC:** `GetBisCredit`  
**Method:** GET `/api/economic/v1/get-bis-credit`  
**Description:** Retrieves credit-to-GDP ratio data from BIS.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  entries: BisCreditToGdp[]
}

type BisCreditToGdp = {
  countryCode: string          // ISO 2-letter country code
  countryName: string          // Country or region name
  creditGdpRatio: number       // Total credit as percentage of GDP
  previousRatio: number        // Previous quarter ratio
  date: string                 // Date as YYYY-QN
}
```

**Upstream:** Bank for International Settlements (BIS)  
**Data Source:** FREE — https://www.bis.org/statistics/totcredit.htm  
**Update Frequency:** Quarterly  
**Caching:** Not specified  
**Algorithms:** Credit-to-GDP percentage calculation

---

#### 2. GetBisExchangeRates
**RPC:** `GetBisExchangeRates`  
**Method:** GET `/api/economic/v1/get-bis-exchange-rates`  
**Description:** Retrieves effective exchange rates from BIS.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  rates: BisExchangeRate[]
}

type BisExchangeRate = {
  countryCode: string          // ISO 2-letter country code
  countryName: string          // Country or region name
  realEer: number              // Real effective exchange rate index
  nominalEer: number           // Nominal effective exchange rate index
  realChange: number           // Percentage change from previous period (real)
  date: string                 // Date as YYYY-MM
}
```

**Upstream:** Bank for International Settlements (BIS)  
**Data Source:** FREE — https://www.bis.org/statistics/eer.htm  
**Update Frequency:** Monthly  
**Caching:** Not specified  
**Algorithms:** Real vs nominal EER indexing, period-over-period change

---

#### 3. GetBisPolicyRates
**RPC:** `GetBisPolicyRates`  
**Method:** GET `/api/economic/v1/get-bis-policy-rates`  
**Description:** Retrieves central bank policy rates from BIS.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  rates: BisPolicyRate[]
}

type BisPolicyRate = {
  countryCode: string          // ISO 2-letter country code (US, GB, JP, etc.)
  countryName: string          // Country or region name
  rate: number                 // Current policy rate percentage
  previousRate: number         // Previous period rate percentage
  date: string                 // Date as YYYY-MM
  centralBank: string          // Central bank name (e.g. "Federal Reserve")
}
```

**Upstream:** Bank for International Settlements (BIS)  
**Data Source:** FREE — https://www.bis.org/statistics/cbpol.htm  
**Update Frequency:** Monthly  
**Caching:** Not specified  
**Algorithms:** Period-over-period rate comparison

---

### BLS Data (Bureau of Labor Statistics) — 1 Endpoint

#### 4. GetBlsSeries
**RPC:** `GetBlsSeries`  
**Method:** GET `/api/economic/v1/get-bls-series`  
**Description:** Retrieves BLS-only series not available on FRED (CES, LAUMT, CIU).

**Request Parameters:**
- `series_id` (string, optional): BLS series ID (e.g. "CES0500000001", "CIU1010000000000A")
- `limit` (integer, optional): Maximum number of observations to return. Defaults to 60.

**Response Schema:**
```typescript
{
  series: BlsSeries
}

type BlsSeries = {
  seriesId: string             // BLS series ID (e.g. "CES0500000001")
  title: string                // Human-readable series title
  units: string                // Unit of measure
  observations: BlsObservation[]
}

type BlsObservation = {
  year: string                 // Year of the observation
  period: string               // Period code (e.g. "M01" for January, "A01" for annual)
  periodName: string           // Human-readable period name
  value: string                // Observed value
}
```

**Upstream:** Bureau of Labor Statistics (BLS)  
**Data Source:** FREE — https://www.bls.gov/developers/  
**Update Frequency:** Monthly/Quarterly/Annual (depends on series)  
**Caching:** Not specified  
**Algorithms:** Direct passthrough from BLS API

**Notes:** Focuses on series NOT mirrored in FRED (CES employment, LAUMT metro unemployment, CIU union membership)

---

### FRED Data (Federal Reserve Economic Data) — 2 Endpoints

#### 5. GetFredSeries
**RPC:** `GetFredSeries`  
**Method:** GET `/api/economic/v1/get-fred-series`  
**Description:** Retrieves time series data from the Federal Reserve Economic Data.

**Request Parameters:**
- `series_id` (string, optional): FRED series ID (e.g., "GDP", "UNRATE", "CPIAUCSL")
- `limit` (integer, optional): Maximum number of observations to return. Defaults to 120.

**Response Schema:**
```typescript
{
  series: FredSeries
}

type FredSeries = {
  seriesId: string             // Series identifier (e.g., "GDP", "UNRATE", "CPIAUCSL") [REQUIRED]
  title: string                // Series title
  units: string                // Unit of measurement
  frequency: string            // Data frequency (e.g., "Monthly", "Quarterly")
  observations: FredObservation[]
}

type FredObservation = {
  date: string                 // Observation date as YYYY-MM-DD string
  value: number                // Observation value
}
```

**Upstream:** Federal Reserve Bank of St. Louis (FRED)  
**Data Source:** FREE — https://fred.stlouisfed.org/docs/api/fred/  
**Update Frequency:** Varies by series (daily/monthly/quarterly/annual)  
**Caching:** Not specified  
**Algorithms:** Direct passthrough from FRED API

---

#### 6. GetFredSeriesBatch
**RPC:** `GetFredSeriesBatch`  
**Method:** POST `/api/economic/v1/get-fred-series-batch`  
**Description:** Retrieves multiple FRED series in a single call.

**Request Parameters:**
```typescript
{
  seriesIds: string[]          // FRED series IDs (e.g., ["WALCL", "FEDFUNDS"]). Min 1, Max 10. [REQUIRED]
  limit?: number               // Maximum number of observations per series. Defaults to 120.
}
```

**Response Schema:**
```typescript
{
  results: Record<string, FredSeries>  // Map of series_id -> FRED series for found series
  fetched: number              // Number of series successfully fetched
  requested: number            // Number of series requested
}

type FredSeries = {
  seriesId: string             // Series identifier (e.g., "GDP", "UNRATE", "CPIAUCSL") [REQUIRED]
  title: string                // Series title
  units: string                // Unit of measurement
  frequency: string            // Data frequency (e.g., "Monthly", "Quarterly")
  observations: FredObservation[]
}

type FredObservation = {
  date: string                 // Observation date as YYYY-MM-DD string
  value: number                // Observation value
}
```

**Upstream:** Federal Reserve Bank of St. Louis (FRED)  
**Data Source:** FREE — https://fred.stlouisfed.org/docs/api/fred/  
**Update Frequency:** Varies by series  
**Caching:** Not specified  
**Algorithms:** Batch request optimization (max 10 series per call)

---

### EIA Data (US Energy Information Administration) — 2 Endpoints

#### 7. GetEnergyCapacity
**RPC:** `GetEnergyCapacity`  
**Method:** GET `/api/economic/v1/get-energy-capacity`  
**Description:** Retrieves installed capacity data (solar, wind, coal) from EIA.

**Request Parameters:**
- `energy_sources` (string, optional): Energy source codes to query (e.g., "SUN", "WND", "COL"). Empty returns all tracked sources (SUN, WND, COL).
- `years` (integer, optional): Number of years of historical data. Default 20 if not set.

**Response Schema:**
```typescript
{
  series: EnergyCapacitySeries[]
}

type EnergyCapacitySeries = {
  energySource: string         // Energy source code (SUN/WND/COL)
  name: string                 // Human-readable name
  data: EnergyCapacityYear[]
}

type EnergyCapacityYear = {
  year: number
  capacityMw: number           // Installed capacity in megawatts
}
```

**Upstream:** US Energy Information Administration (EIA)  
**Data Source:** FREE — https://www.eia.gov/opendata/  
**Update Frequency:** Annual  
**Caching:** Not specified  
**Algorithms:** Aggregate installed capacity by source type (solar/wind/coal)

---

#### 8. GetEnergyPrices
**RPC:** `GetEnergyPrices`  
**Method:** GET `/api/economic/v1/get-energy-prices`  
**Description:** Retrieves current energy commodity prices from EIA.

**Request Parameters:**
- `commodities` (string, optional): Optional commodity filter. Empty returns all tracked commodities.

**Response Schema:**
```typescript
{
  prices: EnergyPrice[]
}

type EnergyPrice = {
  commodity: string            // Energy commodity identifier [REQUIRED, minLength: 1]
  name: string                 // Human-readable name (e.g., "WTI Crude Oil", "Henry Hub Natural Gas")
  price: number                // Current price in USD
  unit: string                 // Unit of measurement (e.g., "$/barrel", "$/MMBtu")
  change: number               // Percentage change from previous period
  priceAt: number              // Price date, as Unix epoch milliseconds (int64)
}
```

**Upstream:** US Energy Information Administration (EIA)  
**Data Source:** FREE — https://www.eia.gov/petroleum/  
**Update Frequency:** Daily/Weekly (depends on commodity)  
**Caching:** Not specified  
**Algorithms:** Period-over-period percentage change calculation

**Warning:** `priceAt` is int64 (Unix epoch milliseconds) — values > 2^53 may lose precision in JavaScript

---

### World Monitor Custom Aggregations — 5 Endpoints

#### 9. GetMacroSignals
**RPC:** `GetMacroSignals`  
**Method:** GET `/api/economic/v1/get-macro-signals`  
**Description:** Computes 7 macro signals from 6 upstream sources with BUY/CASH verdict.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  timestamp: string            // ISO 8601 timestamp of computation
  verdict: string              // Overall verdict: "BUY", "CASH", or "UNKNOWN"
  bullishCount: number         // Number of bullish signals
  totalCount: number           // Total number of evaluated signals (excluding UNKNOWN)
  signals: MacroSignals
  meta: MacroMeta
  unavailable: boolean         // True when upstream data is unavailable (fallback result)
}

type MacroSignals = {
  liquidity: LiquiditySignal
  flowStructure: FlowStructureSignal
  macroRegime: MacroRegimeSignal
  technicalTrend: TechnicalTrendSignal
  hashRate: HashRateSignal
  priceMomentum: PriceMomentumSignal
  fearGreed: FearGreedSignal
}

type LiquiditySignal = {
  status: string               // "SQUEEZE", "NORMAL", or "UNKNOWN"
  value?: number               // JPY 30d ROC percentage, absent if unavailable
  sparkline: number[]          // Last 30 JPY close prices
}

type FlowStructureSignal = {
  status: string               // "PASSIVE GAP", "ALIGNED", or "UNKNOWN"
  btcReturn5: number           // BTC 5-day return percentage
  qqqReturn5: number           // QQQ 5-day return percentage
}

type MacroRegimeSignal = {
  status: string               // "RISK-ON", "DEFENSIVE", or "UNKNOWN"
  qqqRoc20: number             // QQQ 20d ROC percentage
  xlpRoc20: number             // XLP 20d ROC percentage
}

type TechnicalTrendSignal = {
  status: string               // "BULLISH", "BEARISH", "NEUTRAL", or "UNKNOWN"
  btcPrice: number             // Current BTC price
  sma50: number                // 50-day simple moving average
  sma200: number               // 200-day simple moving average
  vwap30d: number              // 30-day volume-weighted average price
  mayerMultiple: number        // Mayer multiple (BTC price / SMA200)
  sparkline: number[]          // Last 30 BTC close prices
}

type HashRateSignal = {
  status: string               // "GROWING", "DECLINING", "STABLE", or "UNKNOWN"
  change30d: number            // Hash rate change over 30 days as percentage
}

type PriceMomentumSignal = {
  status: string               // "STRONG", "MODERATE", "WEAK", or "UNKNOWN"
}

type FearGreedSignal = {
  status: string               // Classification label (e.g., "Extreme Fear", "Greed")
  value: number                // Current index value (0-100)
  history: FearGreedHistoryEntry[]
}

type FearGreedHistoryEntry = {
  value: number                // Index value (0-100, min: 0, max: 100)
  date: string                 // Date string (YYYY-MM-DD)
}

type MacroMeta = {
  qqqSparkline: number[]       // Last 30 QQQ close prices for sparkline
}
```

**Upstreams:** 
1. FRED (JPY exchange rate) — FREE
2. Yahoo Finance (BTC, QQQ, XLP prices) — FREE
3. Blockchain.com (BTC hash rate) — FREE
4. CoinGecko (BTC OHLCV) — FREE
5. Alternative.me (Fear & Greed Index) — FREE
6. Internal computation

**Data Source:** All FREE  
**Update Frequency:** Real-time to daily (varies by signal component)  
**Caching:** Not specified  
**Algorithms:**
- **Liquidity:** JPY 30-day rate of change (ROC)
- **Flow Structure:** BTC vs QQQ 5-day returns comparison
- **Macro Regime:** QQQ vs XLP 20-day ROC comparison
- **Technical Trend:** Price vs SMA50/SMA200/VWAP30d, Mayer Multiple (price/SMA200)
- **Hash Rate:** 30-day percentage change
- **Price Momentum:** Mayer Multiple thresholds (STRONG/MODERATE/WEAK)
- **Fear & Greed:** Alternative.me index interpretation

**Notes:** Complex multi-source aggregation with custom trading signal logic. Fallback behavior when upstreams unavailable.

---

#### 10. GetNationalDebt
**RPC:** `GetNationalDebt`  
**Method:** GET `/api/economic/v1/get-national-debt`  
**Description:** Retrieves national debt clock data for all countries.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  entries: NationalDebtEntry[]
  seededAt: string             // ISO 8601 timestamp when seed data was written
  unavailable: boolean         // True when upstream data is unavailable (fallback result)
}

type NationalDebtEntry = {
  iso3: string                 // ISO3 country code (e.g. "USA")
  debtUsd: number              // Total debt in USD at baseline_ts
  gdpUsd: number               // GDP in USD (nominal, latest year)
  debtToGdp: number            // Debt as % of GDP
  annualGrowth: number         // Year-over-year debt growth percent (2023->2024)
  perSecondRate: number        // Deficit-derived accrual in USD per second
  perDayRate: number           // Deficit-derived accrual in USD per day
  baselineTs: string           // UTC ms timestamp anchoring the debt_usd figure (2024-01-01T00:00:00Z) [int64 format]
  source: string               // Human-readable source string
}
```

**Upstream:** World Bank Open Data, IMF World Economic Outlook — FREE  
**Data Source:** FREE  
**Update Frequency:** Annual (static baseline with real-time accrual calculation)  
**Caching:** Seeded data with timestamp  
**Algorithms:**
- Debt-to-GDP percentage calculation
- Annual growth rate (YoY 2023→2024)
- Per-second/per-day accrual rate from deficit data
- Real-time extrapolation from baseline timestamp

**Notes:** Uses baseline debt figure at 2024-01-01T00:00:00Z, extrapolates using per-second accrual rates. Fallback to cached seed when upstream unavailable.

---

#### 11. ListBigMacPrices
**RPC:** `ListBigMacPrices`  
**Method:** GET `/api/economic/v1/list-bigmac-prices`  
**Description:** Retrieves Big Mac Index prices across Middle East countries.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  countries: BigMacCountryPrice[]
  fetchedAt: string            // ISO 8601 timestamp
  cheapestCountry: string
  mostExpensiveCountry: string
  wowAvgPct: number            // Week-over-week average percentage change
  wowAvailable: boolean        // Whether WoW data is available
  prevFetchedAt: string        // Previous fetch timestamp
}

type BigMacCountryPrice = {
  code: string                 // Country code
  name: string                 // Country name
  currency: string             // Local currency
  flag: string                 // Emoji flag
  localPrice: number           // Price in local currency
  usdPrice: number             // Price in USD
  fxRate: number               // FX rate used for conversion
  sourceSite: string           // Data source website
  available: boolean           // Whether data is available
  wowPct: number               // Week-over-week percentage change
}
```

**Upstream:** Custom web scraping (McDonald's websites, local sources)  
**Data Source:** FREE (scraped)  
**Update Frequency:** Weekly  
**Caching:** Yes (fetchedAt, prevFetchedAt)  
**Algorithms:**
- USD conversion via FX rates
- Week-over-week percentage change tracking
- Cheapest/most expensive country identification

**Notes:** Middle East focus. Web scraping of local McDonald's pricing.

---

#### 12. ListFuelPrices
**RPC:** `ListFuelPrices`  
**Method:** GET `/api/economic/v1/list-fuel-prices`  
**Description:** Retrieves retail gasoline and diesel prices across 30+ countries.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  countries: FuelCountryPrice[]
  fetchedAt: string            // ISO 8601 timestamp
  cheapestGasoline: string
  cheapestDiesel: string
  mostExpensiveGasoline: string
  mostExpensiveDiesel: string
  wowAvailable: boolean        // Whether WoW data is available
  prevFetchedAt: string        // Previous fetch timestamp
  sourceCount: number          // Number of upstream sources
  countryCount: number         // Number of countries covered
}

type FuelCountryPrice = {
  code: string                 // Country code
  name: string                 // Country name
  currency: string             // Local currency
  flag: string                 // Emoji flag
  gasoline: FuelPrice
  diesel: FuelPrice
  fxRate: number               // FX rate used for conversion
}

type FuelPrice = {
  usdPrice: number             // Price in USD per liter
  localPrice: number           // Price in local currency per liter
  grade: string                // Fuel grade (e.g., "95 RON", "Diesel")
  source: string               // Data source
  available: boolean           // Whether data is available
  wowPct: number               // Week-over-week percentage change
  observedAt: string           // Observation timestamp
}
```

**Upstream:** GlobalPetrolPrices.com, government websites, custom scrapers  
**Data Source:** FREE (aggregated)  
**Update Frequency:** Weekly  
**Caching:** Yes (fetchedAt, prevFetchedAt)  
**Algorithms:**
- USD conversion via FX rates
- Separate gasoline/diesel tracking
- Week-over-week percentage change
- Cheapest/most expensive identification by fuel type

**Notes:** 30+ countries, dual-fuel (gasoline + diesel) tracking, multiple upstream sources.

---

#### 13. ListGroceryBasketPrices
**RPC:** `ListGroceryBasketPrices`  
**Method:** GET `/api/economic/v1/list-grocery-basket-prices`  
**Description:** Retrieves grocery basket price comparison across 24 countries worldwide.

**Request Parameters:** None

**Response Schema:**
```typescript
{
  countries: CountryBasket[]
  fetchedAt: string            // ISO 8601 timestamp
  cheapestCountry: string
  mostExpensiveCountry: string
  upstreamUnavailable: boolean // Whether upstream data is unavailable
  wowAvgPct: number            // Week-over-week average percentage change
  wowAvailable: boolean        // Whether WoW data is available
  prevFetchedAt: string        // Previous fetch timestamp
}

type CountryBasket = {
  code: string                 // Country code
  name: string                 // Country name
  currency: string             // Local currency
  flag: string                 // Emoji flag
  totalUsd: number             // Total basket cost in USD
  fxRate: number               // FX rate used for conversion
  items: GroceryItemPrice[]
  wowPct: number               // Week-over-week basket percentage change
}

type GroceryItemPrice = {
  itemId: string               // Item identifier
  itemName: string             // Item name
  unit: string                 // Unit of measurement
  localPrice: number           // Price in local currency
  usdPrice: number             // Price in USD
  currency: string             // Currency code
  sourceSite: string           // Data source website
  available: boolean           // Whether item is available
}
```

**Upstream:** Custom web scraping (supermarket websites, aggregators)  
**Data Source:** FREE (scraped)  
**Update Frequency:** Weekly  
**Caching:** Yes (fetchedAt, prevFetchedAt)  
**Algorithms:**
- Standardized basket composition across countries
- USD conversion via FX rates
- Per-item and total basket tracking
- Week-over-week percentage change (basket-level + aggregate)
- Cheapest/most expensive country identification

**Notes:** 24 countries, standardized basket composition for cross-country comparison. Item-level granularity.

---

#### 14. ListWorldBankIndicators
**RPC:** `ListWorldBankIndicators`  
**Method:** GET `/api/economic/v1/list-world-bank-indicators`  
**Description:** Retrieves development indicator data from the World Bank.

**Request Parameters:**
- `indicator_code` (string, optional): World Bank indicator code (e.g., "NY.GDP.MKTP.CD")
- `country_code` (string, optional): Optional country filter (ISO 3166-1 alpha-2)
- `year` (integer, optional): Optional year filter. Defaults to latest available.
- `page_size` (integer, optional): Maximum items per page.
- `cursor` (string, optional): Cursor for next page.

**Response Schema:**
```typescript
{
  data: WorldBankCountryData[]
  pagination: PaginationResponse
}

type WorldBankCountryData = {
  countryCode: string          // ISO 3166-1 alpha-2 country code [REQUIRED, minLength: 1]
  countryName: string          // Country name
  indicatorCode: string        // World Bank indicator code (e.g., "NY.GDP.MKTP.CD") [REQUIRED, minLength: 1]
  indicatorName: string        // Indicator name
  year: number                 // Data year
  value: number                // Indicator value
}

type PaginationResponse = {
  nextCursor: string           // Cursor for fetching the next page. Empty string indicates no more pages.
  totalCount: number           // Total count of items matching the query, if known. Zero if the total is unknown.
}
```

**Upstream:** World Bank Open Data  
**Data Source:** FREE — https://data.worldbank.org/  
**Update Frequency:** Annual (varies by indicator)  
**Caching:** Not specified  
**Algorithms:**
- Cursor-based pagination
- Optional filtering by country/year/indicator
- Direct passthrough from World Bank API

**Notes:** Access to full World Bank development indicators catalog. Pagination required for large result sets.

---

## Data Source Summary

| Upstream Source | Endpoints Using | Access Type | Update Frequency |
|-----------------|----------------|-------------|------------------|
| Bank for International Settlements (BIS) | 3 | FREE | Monthly/Quarterly |
| Bureau of Labor Statistics (BLS) | 1 | FREE | Monthly/Quarterly/Annual |
| Federal Reserve Economic Data (FRED) | 2 | FREE | Daily/Monthly/Quarterly |
| US Energy Information Administration (EIA) | 2 | FREE | Daily/Weekly/Annual |
| World Bank Open Data | 1 | FREE | Annual |
| Custom World Monitor Aggregations | 5 | FREE (scraped/computed) | Weekly/Real-time |

**Total:** 6 upstream categories, 14 endpoints, **ALL FREE**

---

## Implementation Details

### Authentication
All endpoints appear to be **unauthenticated** (no security schemes in OpenAPI specs).

### Error Handling
Standard error responses:
- `400` — Validation error (contains `violations: FieldViolation[]`)
- `default` — General error (contains `message: string`)

### Data Freshness
- **Real-time:** Energy prices, macro signals
- **Daily:** FRED (some series), EIA prices
- **Weekly:** Fuel, grocery, Big Mac prices
- **Monthly:** BIS exchange rates, policy rates
- **Quarterly:** BIS credit-to-GDP
- **Annual:** Energy capacity, World Bank indicators

### Caching Strategy
Not explicitly documented in API specs, but inferred:
- **Timestamp tracking:** `fetchedAt`, `prevFetchedAt`, `seededAt`
- **Fallback behavior:** `unavailable` boolean flags indicate cached data when upstream fails
- **Week-over-week tracking:** Suggests weekly refresh cycles for price endpoints

### Key Algorithms

1. **Macro Signals:**
   - Multi-source aggregation (6 sources → 7 signals)
   - Custom trading logic (BUY/CASH verdict)
   - Technical indicators: SMA50/200, VWAP, Mayer Multiple
   - Rate of change (ROC) calculations

2. **National Debt Clock:**
   - Real-time accrual from baseline timestamp
   - Per-second/per-day deficit-derived rates
   - Debt-to-GDP percentage

3. **Price Comparisons:**
   - USD conversion via FX rates
   - Cross-country ranking (cheapest/most expensive)
   - Week-over-week percentage changes
   - Standardized basket composition (groceries)

4. **BIS Data:**
   - Credit-to-GDP ratios
   - Effective exchange rate indices (real vs nominal)
   - Period-over-period deltas

---

## Notes for Atlas Intel Implementation

### Rate Limits
Not documented — assume conservative approach:
- Batch endpoints where available (`GetFredSeriesBatch` — max 10 series)
- Cache aggressively for data with known update frequencies
- Respect weekly refresh cycles for scraped data

### Data Quality
- **High reliability:** BIS, BLS, FRED, EIA, World Bank (official government/institutional sources)
- **Variable reliability:** Scraped data (Big Mac, fuel, grocery) — subject to website changes
- **Fallback behavior:** API handles upstream failures gracefully (cached data + `unavailable` flags)

### Best Use Cases
1. **Macro analysis:** Combine FRED + BIS + macro signals for economic trend analysis
2. **Cost of living:** Fuel + grocery + Big Mac for purchasing power comparisons
3. **Energy transition:** Energy capacity + prices for renewable/fossil fuel tracking
4. **Central banking:** BIS policy rates + FRED for monetary policy monitoring
5. **Development indicators:** World Bank data for socioeconomic metrics

### Limitations
1. **Geographic coverage varies:**
   - Big Mac: Middle East focus only
   - Fuel/Grocery: 24-30 countries (not global)
   - BIS/World Bank: Global but institutional focus

2. **Update latency:**
   - Annual indicators (World Bank, energy capacity) lag by 1-2 years
   - Scraped data depends on source availability

3. **No historical batch queries:**
   - FRED batch limited to 10 series at a time
   - No bulk historical exports documented

### Recommended Approach
- **Start with FRED/BIS:** High-quality, reliable, broad economic coverage
- **Layer in EIA:** For energy-specific intelligence
- **Use macro signals:** Pre-computed technical analysis (saves implementation effort)
- **Supplement with price data:** For cost-of-living/inflation proxies
- **Cache World Bank data:** Annual updates, low refresh needed

---

## Endpoint Classification

### Production-Ready (High Reliability)
- GetBisCredit, GetBisExchangeRates, GetBisPolicyRates
- GetBlsSeries
- GetFredSeries, GetFredSeriesBatch
- GetEnergyCapacity, GetEnergyPrices
- ListWorldBankIndicators

### Use with Caution (Scraped/Computed)
- ListBigMacPrices (regional only, scraping dependency)
- ListFuelPrices (scraping dependency)
- ListGroceryBasketPrices (scraping dependency)
- GetMacroSignals (complex multi-source computation, fallback behavior)
- GetNationalDebt (extrapolated estimates, not real-time official debt)

---

## Completion Status

✅ **All 14 endpoints crawled and documented**
✅ **Schemas extracted with field names and types**
✅ **Upstream sources identified and marked as FREE**
✅ **Update frequencies documented**
✅ **Algorithms/computations described**
✅ **Implementation guidance provided**

**Report written to:** `/home/ubuntu/clawd/projects/atlas-intel/research/wm-api-economic.md`
