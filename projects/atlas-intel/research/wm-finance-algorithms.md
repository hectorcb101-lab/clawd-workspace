# World Monitor Intelligence Extraction
## Finance Data, Algorithms & AI Techniques

**Date:** 2026-03-23  
**Purpose:** Comprehensive extraction of World Monitor's data sources, algorithms, and features for Atlas Intel dashboard replication  
**Focus:** Free APIs and replicable techniques

---

## 📊 FREE Data Sources & APIs

### Market Data (Yahoo Finance - FREE)
**Base:** Yahoo Finance API (no key required)
- **Endpoint pattern:** Yahoo Finance chart/history endpoints
- **Symbols supported:**
  - Index symbols: `^GSPC`, `^DJI`, `^IXIC`
  - Stock tickers: `AAPL`, `BRK-B`, `NVDA`
  - Commodities: `GC=F` (gold), `CL=F` (crude oil)
  - Crypto pairs: `BTC-USD`, `ETH-USD`
- **Data available:**
  - Daily OHLCV bars (price + volume)
  - 5-day chart data
  - Historical data for backtesting
  - Real-time quotes
- **Update frequency:** Real-time during market hours
- **Storage format:** localStorage as `wm-market-watchlist-v1` (max 50 symbols)

### FRED Economic Data (FREE)
**API:** Federal Reserve Economic Data  
**Endpoint:** FRED API (free registration)
- **Series tracked:**
  - Deep Sea Freight PPI: `PCU483111483111`
  - Freight Transportation Index: `TSIFRGHT`
- **Cache TTL:** 1 hour
- **Release cadence:** Weekly
- **Output:** Sparklines (24 months history)

### Energy Data (FREE)
**API:** U.S. Energy Information Administration (EIA)  
**Base URL:** EIA API (free registration required)
- **Series:**
  - WTI Crude spot price ($/bbl) - Weekly
  - Brent Crude spot price ($/bbl) - Weekly
  - US crude oil production (Mbbl/d) - Weekly
  - US commercial crude stocks - Weekly
- **Cache TTL:** 30 minutes client-side
- **Trend detection:** ±0.5% threshold for rising/falling flags

### Cryptocurrency (CoinGecko - FREE)
**API:** CoinGecko Public API  
**Endpoint:** `https://api.coingecko.com/api/v3/`
- **Coins tracked:** USDT, USDC, DAI, FDUSD, USDe
- **Data points:**
  - Current price
  - Market cap
  - 24h volume
  - Peg deviation from $1.00
- **Cache TTL:** 2 minutes
- **Health thresholds:**
  - ON PEG: ≤0.5% deviation (green)
  - SLIGHT DEPEG: 0.5-1.0% (yellow)
  - DEPEGGED: >1.0% (red)

### Bitcoin Blockchain (FREE)
**API:** mempool.space  
**Endpoint:** `https://mempool.space/api/`
- **Data available:**
  - Mining hashrate (30-day trend)
  - Block difficulty
  - Mempool size
  - Fee estimates
- **Update frequency:** Real-time
- **No authentication required**

### Bitcoin Fear & Greed (FREE)
**API:** alternative.me  
**Endpoint:** `https://api.alternative.me/fng/`
- **Data:** Sentiment index (0-100)
- **Threshold:** >50 = bullish signal
- **Update frequency:** Daily
- **No key required**

### BIS Central Bank Data (FREE)
**API:** Bank for International Settlements  
**Base:** BIS Statistics API
- **Datasets:**
  1. Policy Rates - Central bank policy rates across major economies
  2. Real Effective Exchange Rates (REER) - Trade-weighted currency indices
  3. Credit-to-GDP - Total credit to non-financial sector as % GDP
- **Cache TTL:** 30 minutes per dataset
- **Circuit breakers:** Independent per dataset
- **Output format:** Sorted tables with spark bars

### WTO Trade Data (FREE-ish)
**API:** WTO Trade Data Services  
**Note:** Basic access is free, some endpoints may require registration
- **Data views:**
  - Trade restrictions (imposing/affected countries, product categories)
  - Tariff rates (bilateral trends, historical datapoints)
  - Bilateral trade flows (volume, YoY change)
  - SPS/TBT barriers (sanitary, phytosanitary, technical)
- **Cache TTL:** 30 minutes
- **Graceful degradation:** `upstreamUnavailable` signaling

### US Treasury Revenue (FREE)
**API:** US Treasury Monthly Treasury Statement  
**Source:** Railway seed (no auth required)
- **Data:** Monthly customs duties revenue
- **Includes:** Fiscal-year-to-date totals, YoY comparison
- **Format:** Monthly table with fiscal year summaries
- **Historical context:** Pre-2025 ~$7B/month → 2025-2026 $27-31B/month

### WorldPop Population Data (FREE for API)
**API:** WorldPop API  
**Base:** Population density grids
- **Use case:** Population exposure estimation for events
- **Batching:** Max 10 parallel requests
- **Radii used:**
  - Conflicts: 50km
  - Earthquakes: 100km
  - Floods: 100km
  - Wildfires: 30km

### Alternative Finance Data Sources (FREE)
- **GDELT:** Goldstein Political Relations (GPR) API - bilateral tension tracking
- **Google News RSS:** Stock news fallback (no auth)
- **PizzINT API:** Foot traffic at military/intelligence locations (check if free tier exists)

---

## 🧮 Core Algorithms & Scoring Formulas

### 1. Market Radar Signal (BUY/CASH Verdict)

**Algorithm:** Composite of 7 independent signals  
**Sources:** 100% free APIs (Yahoo Finance, mempool.space, alternative.me)

**Formula:**
```
verdict = BUY if (bullish_signals / known_signals) ≥ 0.57
         CASH otherwise

Signals with unknown data excluded from denominator
```

**Signal Components:**

| Signal | Computation | Bullish When |
|--------|------------|--------------|
| **Liquidity** | JPY/USD 30-day ROC | ROC > -2% (no yen squeeze) |
| **Flow Structure** | BTC 5-day return vs QQQ 5-day | Gap < 5% (aligned) |
| **Macro Regime** | QQQ 20-day ROC vs XLP 20-day | QQQ outperforming (risk-on) |
| **Technical Trend** | BTC vs SMA50 + 30-day VWAP | Above both |
| **Hash Rate** | Bitcoin hashrate 30-day change | Growing > 3% |
| **Mining Cost** | BTC price vs hashrate-implied cost | Price > $60K |
| **Fear & Greed** | alternative.me index | Value > 50 |

**VWAP Calculation:**
```javascript
// Volume-Weighted Average Price (30-day window)
// Pairs with null price OR volume are excluded together
VWAP = Σ(price × volume) / Σ(volume)  // last 30 trading days
```

**Mayer Multiple:**
```javascript
Mayer Multiple = BTC_price / SMA200
// Thresholds:
// > 2.4 = overheating
// < 0.8 = deep undervaluation
```

### 2. Country Instability Index (CII)

**Scale:** 0-100  
**Formula:** 40% baseline + 60% event score

**Component Breakdown:**

| Component | Weight | Calculation |
|-----------|--------|-------------|
| **Baseline risk** | 40% | Pre-configured (0-50 scale) per country |
| **Event score** | 60% | Blend of Unrest (25%), Conflict (30%), Security (20%), Info (25%) |

**Unrest Score (0-100):**
```javascript
// Base calculation (capped at 50)
base = (multiplier < 0.7) ? log2_dampening(count) : linear(count)

// Boosts
protest_fatality_boost = min(30, fatalities_weighted)
outage_boost = {
  TOTAL: 30,
  MAJOR: 15,
  PARTIAL: 5
}
max_outage_boost = 50

unrest_score = min(100, base + fatality_boost + outage_boost)
```

**Conflict Score (0-100):**
```javascript
// Weighted ACLED events (capped at 50)
acled_score = min(50, battles×3 + explosions×4 + civilian_violence×5)

// Fatality score (up to 40)
fatality_score = min(40, sqrt(fatalities))

// Boosts
civilian_boost = min(10, civilian_targeting_events)
iran_strike_boost = min(50, severity_weighted_strikes)

// Israel-specific OREF alerts
oref_boost = min(50, 25 + (active_alerts × 5))

// 24-hour history boost
if (alerts_24h >= 10) boost += 10
else if (alerts_24h >= 3) boost += 5

conflict_score = min(100, acled + fatality + boosts)
```

**Security Score (0-100):**
```javascript
// GPS/GNSS jamming (capped at 35)
jamming_score = Σ(hex_jamming_severity)
// High (>10%): 5pts/hex
// Medium (2-10%): 2pts/hex
// Low (0-2%): hidden

max_jamming_score = 35
```

**Floors:**
- UCDP active war: ≥70
- UCDP minor conflict: ≥50
- Do-not-travel advisory: ≥60
- Reconsider travel: ≥50

**Boosts:**
```javascript
advisory_boost = {
  do_not_travel: +15,
  reconsider: +10,
  caution: +5
}

oref_blend_boost = active_alerts ? +15 : (history_count >= 10 ? +10 : +5)
climate_severity_boost = min(15, climate_score)
cyber_threats_boost = min(10, cyber_score)
wildfire_boost = min(8, wildfire_severity)
```

### 3. Hotspot Escalation Scoring

**Scale:** 0-100  
**Formula:** Normalized blend of 4 signals

```javascript
escalation_score = 
  (news_activity × 0.35) +
  (country_instability × 0.25) +
  (geo_convergence_alerts × 0.25) +
  (military_activity × 0.15)

// Each component normalized to 0-100
```

**Trend Detection:**
- Linear regression on 48-hour history
- Signal cooldown: 2 hours to prevent alert fatigue

### 4. Geographic Convergence Detection

**Grid:** 1°×1° lat/lon cells  
**Window:** 24 hours  
**Threshold:** 3+ distinct event types in same cell

**Scoring:**
```javascript
convergence_score = 
  (event_type_diversity × 25) + 
  (event_count × 2)

// Alert fires when score exceeds threshold
```

**Event types:** protests, military flights, vessels, earthquakes, outages, displacement

### 5. Strategic Risk Score

**Scale:** 0-100  
**Formula:**
```javascript
strategic_risk = 
  (convergence_score × 0.30) +
  (cii_risk_score × 0.50) +
  (infra_score × 0.20) +
  theater_boost +  // 0-25
  breaking_boost   // 0-15
```

**Sub-scores:**

**Convergence Score:**
```javascript
convergence_score = min(100, convergence_alert_count × 25)
```

**CII Risk Score:**
```javascript
// Top 5 countries by CII, weighted
weights = [0.40, 0.25, 0.20, 0.10, 0.05]
cii_risk = Σ(top5_cii × weights) + elevated_bonus

elevated_bonus = min(20, elevated_count × 5)  // countries with CII > 50
```

**Infrastructure Score:**
```javascript
infra_score = min(100, cascade_alert_count × 25)
```

**Theater Boost:**
```javascript
theater_boost = Σ(theater_scores)  // capped at 25

per_theater_score = min(10, floor((aircraft + vessels) / 5))
if (strike_capable) per_theater_score += 5  // tanker + AWACS + fighters
if (posture_stale) per_theater_score /= 2
```

**Breaking Boost:**
```javascript
breaking_boost = min(15, breaking_alert_severity)
// Critical: +15, High: +8
// Expires after 30 minutes
```

**Trend Classification:**
```javascript
if (delta >= 3) trend = "escalating"
else if (delta <= -3) trend = "de-escalating"
else trend = "stable"

// Learning period: 15 minutes after panel init (suppress CII spike alerts)
```

### 6. Undersea Cable Health Score

**Scale:** 0-100  
**Formula:** Time-decayed signal weighting

```javascript
// Signal weight with exponential time decay
λ = ln(2) / 168  // 7-day half-life

signal_weight = severity × exp(-λ × age_hours)

health_score = max(0, 100 - Σ(signal_weights) × 100)
```

**Severities:**
- `operator_fault` (cable damage): 1.0
- `cable_advisory` (repair, warnings): 0.6

**Geographic matching:** 50km radius, cosine-latitude-corrected equirectangular approximation

**Cache strategy:**
- Redis: 6h TTL (complete), 10min TTL (partial)
- In-memory fallback serves stale data when Redis unavailable

### 7. Infrastructure Cascade Model

**Algorithm:** Breadth-First Search (BFS), depth ≤ 3

```javascript
disruption_event → affected_node → cascade_propagation(BFS, depth≤3)
                                    ↓
                         ┌──────────┴──────────┐
                         ▼                     ▼
                  direct_impact         indirect_impact
                  (cable cut)        (countries served)

impact_strength = edge_weight × disruption_level × (1 - redundancy)
```

**Strategic chokepoint dependencies:**
- **Strait of Hormuz:** 80% Japan oil, 70% S.Korea, 60% India, 40% China
- **Suez Canal:** EU-Asia trade (Germany, Italy, UK, China)
- **Malacca Strait:** 80% China oil transit

**Port weights:**
- Oil/LNG terminals: 0.9 (critical)
- Container ports: 0.7
- Naval bases: 0.4 (geopolitical)

### 8. Headline Scoring Algorithm

**Purpose:** Rank news by geopolitical significance

**Formula:**
```javascript
headline_score = 
  category_base_score +
  (keyword_matches × per_match_bonus) +
  source_confirmation_boost +
  theater_posture_boost -
  demotion_penalty
```

**Scoring tiers:**

| Category | Base | Per-Match | Keywords |
|----------|------|-----------|----------|
| **Violence** | +100 | +25 | killed, dead, death, shot, casualty, massacre, crackdown |
| **Military** | +80 | +20 | war, invasion, airstrike, missile, troops, combat, fleet |
| **Unrest** | +40 | +15 | protest, uprising, riot, demonstration, revolution |
| **Flashpoint** | — | +20 | iran, russia, china, taiwan, ukraine, israel, gaza, north korea, syria, yemen, hamas, hezbollah, nato, kremlin |
| **Crisis** | — | +10 | sanctions, escalation, breaking, urgent, humanitarian |

**Boosts:**
```javascript
source_confirmation_boost = additional_sources × 10

theater_posture_boost = (theater_elevated) ? keyword_relevance_score : 0
```

**Demotions:**
```javascript
corporate_keywords = ["CEO", "earnings", "stock", "startup", "revenue"]
if (headline.includes(corporate_keywords)) score -= 20
```

### 9. Keyword Spike Detection

**Window:** 2-hour current activity vs 7-day baseline  
**Thresholds:**

```javascript
spike_fires = 
  (current_count > min_spike_count) &&           // > 5 mentions
  (current_count > baseline × spike_multiplier) && // > 3× baseline
  (source_diversity >= 2) &&                     // ≥ 2 RSS sources
  (time_since_last_spike > cooldown)            // 30 min cooldown
```

**Tokenization:**
- CVE identifiers: `CVE-2024-xxxxx`
- APT/FIN threat actors
- 12 compound terms for world leaders (e.g., "Xi Jinping", "Kim Jong Un")

**Registry cap:** 10,000 entries, LRU eviction

### 10. Temporal Baseline Anomaly Detection

**Algorithm:** Welford's online method for streaming mean/variance

```javascript
// Z-score calculation
z_score = (observation - baseline_mean) / baseline_stddev

// Thresholds
if (z_score >= 3.0) severity = "critical"
else if (z_score >= 2.0) severity = "medium"
else if (z_score >= 1.5) severity = "low"
```

**Requirements:**
- Minimum 10 historical samples before reporting anomalies
- Separate baselines per weekday and month
- 90-day rolling window
- Redis storage with streaming computation

### 11. Breaking News Alert Pipeline

**Sources:** 5 independent alert origins

**Deduplication logic:**
```javascript
// Per-event dedup
alert_key = content_hash(alert)
if (seen_within_30_min(alert_key)) suppress()

// Global cooldown
if (time_since_last_alert < 60_seconds) suppress()

// Recency gate
if (event_age > 15_minutes) drop()

// Source tier gating
if (source_tier >= 3 && classification.source === 'keyword') suppress()
```

**User sensitivity:**
- `critical-only`: Only critical severity fires
- `critical-and-high`: Both critical and high fire

### 12. Focal Point Scoring

**Formula:**
```javascript
focal_score = news_score + signal_score + correlation_bonus

// News Score (0-40)
news_score = 
  min(20, mention_count × 4) +
  min(10, news_velocity × 2) +
  (avg_confidence × 10)

// Signal Score (0-40)
signal_score = 
  (signal_types.count × 10) +
  min(15, signal_count × 3) +
  (high_severity_count × 5)

// Correlation Bonus (0-20)
correlation_bonus = 
  (appears_in_news_and_signals ? 10 : 0) +
  (keywords_match_signal_types ? 5 : 0) +
  (related_entities_have_signals ? 5 : 0)
```

**Urgency levels:**
- **Critical:** Score > 70 OR ≥3 signal types (red badge)
- **Elevated:** Score > 50 OR ≥2 signal types (orange badge)
- **Watch:** Default (yellow badge)

### 13. BTC ETF Flow Estimation

**Note:** This is an APPROXIMATION (real flow data requires expensive subscriptions)

**Algorithm:**
```javascript
// 10 ETFs tracked via Yahoo Finance 5-day chart
// IBIT, FBTC, ARKB, BITB, GBTC, HODL, BRRR, EZBC, BTCO, BTCW

price_change = daily_close - previous_close
direction = sign(price_change)
volume_ratio = current_volume / trailing_avg_volume

flow_estimate = volume × price × direction × 0.1
```

**Cache:** 15 minutes

---

## 🤖 AI & ML Techniques

### 1. LLM Summarization Chain

**Tier 1: Ollama / LM Studio** (Local, FREE)
- Endpoint: `/v1/chat/completions` (OpenAI-compatible)
- Auto-discovered model
- No cloud dependency
- Temperature: 0.3

**Tier 2: Groq** (Cloud, FREE tier)
- Model: Llama 3.1 8B / Llama 3.3 70B
- Temperature: 0.3
- Fast inference (~2s)
- Rate limited

**Tier 3: OpenRouter** (Cloud, PAID)
- Multi-model fallback
- Llama 3.3 70B
- ~3s latency

**Tier 4: Browser T5** (Local, FREE)
- Transformers.js (ONNX)
- ~60MB model
- No network required
- ~5-10s inference
- Limited to 512 token context

**Pre-processing:**
```javascript
// Jaccard similarity deduplication
for each pair of headlines:
  if word_overlap_similarity > 0.6:
    merge_near_duplicates()

// Reduces prompt size by 20-40%
```

**Cache strategy:**
```javascript
cache_key = `summary:v3:${mode}:${variant}:${lang}:${hash}`
cache_ttl = 24_hours  // Redis
```

### 2. Threat Classification Pipeline

**3-stage cascade:**

**Stage 1: Keyword Classifier** (instant)
- Source: `'keyword'`
- ~120 threat keywords
- 5 severity tiers (critical → high → medium → low → info)
- 14 event categories
- Word-boundary regex matching
- Variant-specific keyword sets

**Stage 2: Browser ML** (async, FREE)
- Source: `'ml'`
- Transformers.js (ONNX)
- NER (Named Entity Recognition)
- Sentiment analysis
- Topic classification
- No server dependency

**Stage 3: LLM Classifier** (batched async)
- Source: `'llm'`
- Groq Llama 3.1 8B (temp 0) or Ollama
- Batched parallel RPCs
- Redis cache (24h TTL)
- 500-series error → automatic pause + exponential backoff
- Overrides keyword only if confidence higher

**Result fusion:**
```javascript
// Classification includes source tag
classification = {
  severity: "critical" | "high" | "medium" | "low" | "info",
  category: "conflict" | "protest" | ...,
  confidence: 0-1,
  source: "keyword" | "ml" | "llm"
}

// Downstream consumers weight by source
```

### 3. Browser-Side ML Models

**All via Transformers.js + ONNX Runtime Web**

| Model | Task | Size | Use |
|-------|------|------|-----|
| **T5-small** | Summarization | ~60MB | Offline brief generation |
| **all-MiniLM-L6-v2** | Embeddings | — | Semantic similarity |
| **DistilBERT** | Sentiment | ~67MB | News tone classification |
| **NER pipeline** | Entity extraction | — | Country/org/leader extraction |

**Lazy loading:**
```javascript
// Models download on first use
// Progress indicator during download
// IndexedDB cache for instant subsequent loads
// 30-second timeout per inference
```

**Worker isolation:**
```javascript
// All ML in Web Worker
// Main thread stays responsive
// Automatic cleanup on errors
```

### 4. Headline Memory (RAG)

**Client-side semantic search - 100% local**

**Ingestion:**
```javascript
RSS_parse → isHeadlineMemoryEnabled() → ML_Worker
                                        ↓
                              ONNX_embeddings
                              all-MiniLM-L6-v2
                              384-dim float32
                                        ↓
                              IndexedDB_store
                              5000_vector_cap
                              LRU by ingestAt
```

**Search:**
```javascript
query → embed(query) → cosine_similarity(query_vec, all_stored_vecs)
     → rank by score
     → filter by minScore threshold
     → return topK results (1-20)

// Multiple queries (up to 5) → max score per record
```

**Deduplication:** Content hash before embedding

### 5. Deduction Engine

**Purpose:** AI geopolitical analysis & forecasting

**Pipeline:**
```javascript
1. Analyst enters free-text query + optional geo context
2. buildNewsContext() pulls 15 most recent headlines
3. Context prepended: "Recent News:\n- Headline (Source)"
4. Send to deductSituation RPC
5. LLM chain (Groq/OpenRouter/custom)
6. System prompt: "senior geopolitical intelligence analyst"
7. Temperature 0.3, max 1500 tokens
8. Strip <think> tags (defense-in-depth)
9. Redis cache 1h: `deduct:situation:v1:{hash}`
```

**Cross-panel integration:**
```javascript
// Any panel can dispatch
document.dispatchEvent({
  type: 'wm:deduct-context',
  detail: { query, geoContext, autoSubmit }
})

// 5-second cooldown between auto-submits
```

### 6. Hybrid News Clustering

**Two-stage approach:**

**Stage 1: Jaccard Similarity** (fast)
```javascript
// N-gram overlap
threshold = 0.4
// Runs on every refresh
```

**Stage 2: Semantic Similarity** (ML-refined)
```javascript
// Cosine similarity on embeddings
threshold = 0.78
// Merges textually different but semantically identical
// Example: "NATO expands missile shield" + "Alliance deploys air defense"
```

**Velocity tracking:**
```javascript
sources_per_hour = cluster.sources.length / time_window_hours

if (sources_per_hour > threshold && tier_1_or_2_sources) {
  flag_as_breaking_alert()
}
```

### 7. Entity Cross-Referencing

**Entity Registry:** 66+ entities with aliases

**Index types:**
- **ID index:** Direct lookup (`entity:us` → United States)
- **Alias index:** Name variants ("America", "USA", "United States")
- **Keyword index:** Contextual ("Pentagon", "White House" → US)
- **Sector index:** Domain grouping ("military", "energy", "tech")
- **Type index:** Category ("country", "organization", "leader")

**Matching:**
```javascript
// Word-boundary regex (prevent "Iran" matching "Ukraine")
confidence_scores = {
  exact_name_match: 1.0,
  alias_match: 0.85-0.95,
  keyword_match: 0.7
}

// Multi-source convergence detection
if (entity in news AND entity in military AND entity in markets) {
  escalate_prominence()
}
```

### 8. Country Detection (Local-First)

**Algorithm:** Ray-casting polygon intersection

**Steps:**
```javascript
1. Bounding box pre-filter
   [minLon, minLat, maxLon, maxLat]
   if (point outside bbox) reject()

2. Ray-casting
   ray from point along +x axis
   count polygon edge intersections
   odd = inside, even = outside

3. MultiPolygon support
   (for non-contiguous territories: US/Alaska/Hawaii, Indonesia)

// Sub-millisecond response, no network
```

**Fallback chain:**
1. GeoJSON polygon (~200 countries)
2. Hardcoded rectangular bboxes
3. Network reverse-geocoding (last resort)

---

## 🎯 Key Features We Can Replicate

### 1. Market Radar (FREE)
✅ **Can build with:**
- Yahoo Finance API (BTC, QQQ, XLP, JPY/USD)
- mempool.space API (hashrate)
- alternative.me API (Fear & Greed)

**Implementation:**
```javascript
// 7 signals, each returns bullish/bearish
// Compute VWAP, SMA50, SMA200, ROC
// verdict = bullish_count / known_signals >= 0.57 ? "BUY" : "CASH"
```

### 2. Country Instability Scoring (PARTIAL)
✅ **Can build baseline with:**
- ACLED API (conflict events) - FREE tier
- Travel advisory data (State Dept) - FREE
- News keyword analysis - FREE
- GDELT - FREE

❌ **Need paid/alternative for:**
- GPS jamming data (specialized)
- OREF alerts (specific to Israel, check if public API)

### 3. Stablecoin Monitoring (FREE)
✅ **Can build with:**
- CoinGecko API
- 2-minute polling
- Peg deviation calculation

### 4. BTC ETF Flow Estimation (FREE)
✅ **Can build with:**
- Yahoo Finance 5-day charts
- Volume ratio calculation
- Direction estimation

### 5. Economic Indicators (FREE/FREEMIUM)
✅ **Can build with:**
- FRED API (freight, shipping)
- EIA API (energy)
- BIS API (central bank rates, REER, credit-to-GDP)
- WTO API (trade restrictions, tariffs)

### 6. AI Summarization (FREE)
✅ **Can build with:**
- Ollama (local, 100% free)
- Groq free tier (Llama 3.1 8B)
- Transformers.js browser fallback (T5-small)

**Implementation:**
- Jaccard dedup headlines
- 4-tier fallback chain
- Redis caching
- Variant-aware prompting

### 7. Threat Classification (FREE)
✅ **Can build with:**
- Keyword classifier (instant)
- Transformers.js NER + sentiment (browser)
- Groq LLM classifier (batched)

### 8. Browser ML Pipeline (FREE)
✅ **Can build with:**
- Transformers.js + ONNX
- Models: T5-small, all-MiniLM-L6-v2, DistilBERT
- Web Worker isolation
- IndexedDB caching

### 9. Headline Memory/RAG (FREE)
✅ **Can build with:**
- all-MiniLM-L6-v2 embeddings (ONNX)
- IndexedDB storage (5000 vector cap)
- Cosine similarity search
- 100% client-side

### 10. Breaking News Alerts (FREE)
✅ **Can build with:**
- RSS parsing
- Keyword spike detection
- Multi-source dedup
- Cooldown logic

---

## ⚠️ Paid/Specialized Data (Find FREE Alternatives)

### Paid Sources Used by WM:
1. **Wingbits API** (aircraft enrichment) - PAID
   - Alternative: ADS-B Exchange API (check free tier), OpenSky Network (FREE)

2. **PizzINT API** (military foot traffic) - CHECK IF FREE TIER
   - Alternative: Public military base activity data sources?

3. **USNI Fleet Reports** (naval deployments) - SUBSCRIPTION
   - Alternative: Public AIS data + open-source OSINT?

4. **Premium WTO endpoints** - MAY REQUIRE PAID ACCESS
   - Alternative: Basic WTO data is free, use that tier

5. **GPS jamming data** - SPECIALIZED
   - Alternative: Crowdsourced GNSS interference reports?

6. **NGA Navigational Warnings** - CHECK IF FREE
   - Alternative: NOAA navigational warnings (FREE)

7. **Finnhub** - FREEMIUM (has free tier)
   - Use free tier, supplement with Yahoo Finance

### Infrastructure Data:
- **Undersea cables:** TeleGeography (check if public data available)
- **Pipelines:** Public pipeline registries
- **Military bases:** Open-source OSINT databases

---

## 📐 Data Formats & Schemas

### Market Watchlist Storage
```javascript
localStorage['wm-market-watchlist-v1'] = JSON.stringify({
  symbols: [
    "AAPL",
    "BTC-USD",
    "^GSPC",
    "GC=F",
    "TSLA|Tesla Inc"  // pipe-separated label
  ]
})
// Max 50 symbols, deduplicated
```

### News Classification
```javascript
{
  severity: "critical" | "high" | "medium" | "low" | "info",
  category: "conflict" | "protest" | "disaster" | "diplomatic" | 
            "economic" | "terrorism" | "cyber" | "health" | 
            "environmental" | "military" | "crime" | "infrastructure" | 
            "tech" | "general",
  confidence: 0.0-1.0,
  source: "keyword" | "ml" | "llm"
}
```

### Signal Aggregation
```javascript
{
  country: "US",
  signals: [
    {
      type: "military_flight" | "military_vessel" | "protest" | 
            "internet_outage" | "earthquake" | "wildfire" | 
            "ais_disruption" | "keyword_spike",
      severity: "low" | "medium" | "high" | "critical",
      lat: 40.7128,
      lon: -74.0060,
      metadata: { ... }
    }
  ],
  timestamp: ISO8601
}
```

### Headline Memory Vector
```javascript
{
  id: "hash",
  title: "headline text",
  source: "Reuters",
  publishedAt: ISO8601,
  url: "https://...",
  location: ["US", "China"],
  embedding: Float32Array(384),  // all-MiniLM-L6-v2
  ingestedAt: timestamp
}
// IndexedDB, 5000 cap, LRU eviction
```

### Stock Analysis (Premium)
```javascript
{
  analysisId: "uuid",
  symbol: "AAPL",
  analysisAt: ISO8601,
  signal: "BUY" | "SELL" | "HOLD" | "CASH",
  signalScore: 0-100,
  currentPrice: 175.43,
  stopLoss: 170.00,
  takeProfit: 185.00,
  engineVersion: "v2.1",
  
  technicals: {
    ma_stack: "bullish" | "bearish" | "neutral",
    bias_vs_sma50: number,
    bias_vs_sma100: number,
    volume_pattern: "accumulation" | "distribution" | "neutral",
    macd_state: "bullish" | "bearish" | "neutral",
    rsi: number,
    rsi_state: "overbought" | "oversold" | "neutral"
  },
  
  factors: {
    bullish: ["SMA stack aligned", "Volume increasing", ...],
    risk: ["RSI overbought", "Resistance at $180", ...]
  }
}
```

### Cache Keys
```javascript
// Redis TTL patterns
"summary:v3:{mode}:{variant}:{lang}:{hash}" // 24h
"news:insights:v1" // bootstrap hydration
"deduct:situation:v1:{hash}" // 1h
"wto_trade" // 30min
"treasury_revenue" // 30min
"bis_policy_rates" // 30min
"bis_exchange_rates" // 30min
"bis_credit" // 30min
```

---

## 🔧 Implementation Priorities for Atlas Intel

### Phase 1: Core Free Data (IMMEDIATE)
1. **Market Radar** - Yahoo Finance + mempool.space + alternative.me
2. **Stablecoin Monitor** - CoinGecko
3. **Economic Dashboard** - FRED + EIA + BIS
4. **AI Summarization** - Ollama local + Groq fallback

### Phase 2: Scoring & Algorithms (WEEK 1)
1. **Headline Scoring** - Keyword-based ranking
2. **Keyword Spike Detection** - 2h window vs 7d baseline
3. **Threat Classification** - 3-stage pipeline

### Phase 3: ML Enhancement (WEEK 2)
1. **Browser ML** - Transformers.js (T5, DistilBERT, MiniLM)
2. **Headline Memory** - Client-side RAG with embeddings
3. **Sentiment Analysis** - Browser-based

### Phase 4: Advanced Features (WEEK 3+)
1. **Country Instability** - ACLED + travel advisories + GDELT
2. **Breaking News Alerts** - Multi-source fusion
3. **Focal Point Detection** - Entity cross-referencing

### Phase 5: Premium (OPTIONAL)
1. **Stock Analysis** - Moving averages, MACD, RSI, volume patterns
2. **Backtesting** - Historical analysis validation

---

## 💡 Key Takeaways

### What Makes World Monitor Powerful:
1. **100% free core data** - Yahoo Finance, FRED, EIA, CoinGecko, mempool.space
2. **Local-first ML** - Browser models eliminate API costs
3. **Multi-tier fallbacks** - Ollama → Groq → OpenRouter → Browser
4. **Smart caching** - Redis + localStorage minimize redundant calls
5. **Signal fusion** - Cross-stream correlation finds patterns
6. **Time-decay algorithms** - Recent signals weighted higher
7. **Deduplication everywhere** - Headlines, alerts, embeddings

### Critical Implementation Details:
1. **VWAP calculation** - Exclude null pairs TOGETHER to prevent index misalignment
2. **Z-score anomaly** - Need ≥10 samples before reporting
3. **Jaccard before embeddings** - Fast dedup before expensive ML
4. **Word-boundary regex** - Prevent "Iran" matching "Ukraine"
5. **Circuit breakers** - Auto-pause on 500-series errors
6. **Cooldowns** - 30min-6h depending on signal type
7. **Source tier gating** - Only Tier 1-2 sources bypass LLM gate

### Architecture Principles:
1. **Graceful degradation** - Every feature has a fallback
2. **Cache-first** - Serve stale data rather than blank screens
3. **Worker isolation** - ML in Web Workers, main thread responsive
4. **Progressive enhancement** - Keyword → ML → LLM
5. **Local-first** - Browser ML, IndexedDB, localStorage
6. **Event-driven** - CustomEvents for cross-panel integration

---

## 🚀 Next Steps

1. **Validate free API access:**
   - Yahoo Finance (unlimited?)
   - FRED (registration required, check rate limits)
   - EIA (registration required, check rate limits)
   - CoinGecko (free tier limits?)
   - BIS (check if public API exists)
   - WTO (confirm free tier)

2. **Set up local inference:**
   - Install Ollama
   - Pull Llama 3.1 8B
   - Test summarization endpoint

3. **Prototype Market Radar:**
   - Fetch 7 signals from free APIs
   - Compute VWAP, ROC, comparisons
   - Output BUY/CASH verdict

4. **Build headline scorer:**
   - Keyword tier system
   - Test with sample headlines
   - Validate ranking

5. **Integrate Transformers.js:**
   - Load T5-small for summarization
   - Load all-MiniLM-L6-v2 for embeddings
   - Test browser inference speed

---

**Generated:** 2026-03-23T23:34 UTC  
**Source pages:** finance-data.md, algorithms.md, ai-intelligence.md, premium-finance.md  
**Extraction depth:** Comprehensive - all algorithms, APIs, and data formats documented
