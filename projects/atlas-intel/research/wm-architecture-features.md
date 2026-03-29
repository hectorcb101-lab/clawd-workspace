# World Monitor: Architecture & Features Intelligence

**Research Date:** 2026-03-23  
**Purpose:** Extract UI patterns, features, and design decisions from World Monitor for Atlas Intel dashboard implementation  
**Tech Stack Relevance:** Features compatible with globe.gl + Three.js

---

## Executive Summary

World Monitor is a vanilla TypeScript intelligence dashboard with dual rendering engines (3D globe via globe.gl/Three.js and 2D flat map via deck.gl/MapLibre). The platform demonstrates sophisticated patterns in:
- Client-side intelligence analysis (no framework overhead)
- Progressive disclosure and smart clustering
- Multi-source data correlation
- Graceful degradation and offline capabilities
- Panel-based UI with drag-and-drop layouts

**Key Takeaway:** They've built a production-grade intelligence platform on the exact stack we're using (globe.gl + Three.js), validating our architecture choice and providing proven patterns.

---

## Map Engine Architecture

### Dual Engine System (Switchable at Runtime)

**3D Globe Engine (globe.gl + Three.js)** — photorealistic Earth rendering
- Earth textures: topographic-bathymetric day surface (`earth-topo-bathy.jpg`)
- Specular water map for ocean reflections
- Starfield night-sky background
- **Atmosphere shader:** Fresnel limb-glow effect (atmospheric scattering at globe edge)
- **Auto-rotation:** Slow rotation when idle, pauses on interaction, resumes after 60s inactivity
- **HTML marker layer:** 28+ data categories rendered as HTML elements pinned to geographic coordinates
- **Geopolitical polygon overlays:** Korean DMZ and boundary polygons rendered directly on globe
- **Debounced marker flush:** Rapid data updates coalesced via `debounceFlushMarkers()` to prevent Three.js scene graph crashes
- **Configurable render quality:** 5 pixel-ratio presets (Auto, Eco 1×, Sharp 1.5×, 4K 2×, Insane 3×)
- **Desktop-optimized defaults:** 
  - High-performance GPU requested (`powerPreference: 'high-performance'`)
  - Logarithmic depth buffer disabled (saves shader overhead)
  - Auto-rotation and camera damping disabled when idle (prevents continuous render loop)
- **Background pause:** WebGL render loop pauses entirely when window loses focus or globe panel hidden
  - Data updates queued while paused, flushed in single batch when visible again
- **Beta indicator:** Pulsing cyan "BETA" badge when globe active

**2D Flat Map Engine (deck.gl + MapLibre GL JS)** — WebGL-accelerated 2D
- Layer types: `GeoJsonLayer`, `ScatterplotLayer`, `PathLayer`, `IconLayer`, `TextLayer`, `PolygonLayer`, `ArcLayer`, `HeatmapLayer`
- **Smart clustering:** Supercluster at low zoom, expands on zoom in
- **Progressive disclosure:** Detail layers appear only when zoomed in
- **Zoom-adaptive opacity:** Markers fade from 0.2 at world view to 1.0 at street level
- **Label deconfliction:** Overlapping labels suppressed by priority
- **Day/night overlay:** Terminator line divides map (updates every 5 minutes)

**Shared Capabilities (Both Engines):**
- 45 data layers from single shared catalog (`map-layer-definitions.ts`)
- 8 regional presets (Global, Americas, Europe, MENA, Asia, Africa, Oceania, Latin America)
- Time filtering (1h, 6h, 24h, 48h, 7d)
- URL state sharing (map center, zoom, active layers, time range)
- Mobile touch gestures:
  - Single-finger pan with inertial velocity (0.92 decay factor, 4-entry circular touch history)
  - Two-finger pinch-to-zoom with center-point preservation
  - Bottom-sheet popups with drag-to-dismiss
  - 8px movement threshold prevents accidental interaction
- **Timezone-based region detection:** Auto-centers on user region via `Intl.DateTimeFormat().resolvedOptions().timeZone`
- **Mobile GPS auto-center:** Browser geolocation API (5s timeout) centers map on GPS coordinates at zoom level 6

### Map Tile Providers (Flat Map)

Multiple providers selectable at runtime, persisted in localStorage:

| Provider | Description | Cost | Default |
|----------|-------------|------|---------|
| **OpenFreeMap** | Free OSM tiles, Dark/Positron styles | Free | Yes (no config) |
| **CARTO** | Dark Matter and Voyager GL styles | Free tier | No |
| **PMTiles (self-hosted)** | Vector tiles as single `.pmtiles` archive via HTTP Range requests (~50-200KB per pan/zoom) | Self-hosted | Yes (if `VITE_PMTILES_URL` set) |
| **Auto** | PMTiles with OpenFreeMap fallback (after 2+ tile failures or 10s timeout) | Self-hosted | No |

**Map Themes:** Per-provider theming (independent of app theme)
- PMTiles: Black, Dark, Grayscale, Light, White
- OpenFreeMap: Dark, Positron
- CARTO: Dark Matter, Voyager, Positron
- **Overlay paint adaptation:** Country highlight/hover colors adapt to map theme
- **Fallback behavior:** Auto-switches to OpenFreeMap on PMTiles failure

### Performance Optimizations

**Debounced Marker Flush** — prevents Three.js crashes during high-frequency data refresh
```typescript
// PATTERN: Coalesce rapid marker updates
debounceFlushMarkers() // batches scene graph updates
```

**Background Pause** — eliminates idle GPU load
- WebGL render loop stops when window unfocused
- Three.js animation loop cancelled
- Auto-rotate disabled
- Data updates queued, flushed on visibility

**Progressive Disclosure** — detail layers appear only when zoomed in
- Prevents overwhelming users at world view
- Zoom-adaptive opacity (0.2 → 1.0)

**Smart Clustering** — Supercluster with adaptive thresholds
- Grouping logic:
  - **Protests:** Cluster within same country only (riots sorted first, high severity prioritized)
  - **Tech HQs:** Cluster within same city (Big Tech → unicorns → public companies)
  - **Tech Events:** Cluster within same location (sorted by date, soonest first)

---

## UI Components & Features

### Panel System

**Draggable, Collapsible Panels** with persistence
- **Drag-to-reorder:** Grab panel header, drag to new position, auto-save to LocalStorage
- **Panel visibility:** Toggle panels on/off via Settings menu
  - Hidden panels: Don't render, don't fetch data
  - Visible panels: Full functionality
  - Collapsed panels: Header only, data still refreshes
- **Panel state persistence:** Order, visibility, collapsed state survive browser restarts

**Panel Base Class Pattern** (vanilla TypeScript, no framework)
```typescript
class Panel {
  render() // lifecycle method
  destroy() // cleanup
  setContent(html) // debounced (150ms) innerHTML update
  // Event delegation on stable container element
}
```

**Event Delegation Pattern** (critical for debounced content updates)
```typescript
// WRONG — listener destroyed on next setContent()
this.content.querySelector('.btn')?.addEventListener('click', handler);

// CORRECT — survives innerHTML replacement
this.content.addEventListener('click', (e) => {
  if (e.target.closest('.btn')) handler(e);
});
```

**Activity Tracking** — "new item" indicators with IntersectionObserver
| Indicator | Duration | Purpose |
|-----------|----------|---------|
| **NEW tag** | 2 minutes | Badge on new items |
| **Glow highlight** | 30 seconds | Subtle animation |
| **Panel badge** | Until viewed | Count of new items in collapsed panels |

**Automatic "Seen" Detection:**
- Panel >50% visible for >500ms → items marked "seen"
- Scrolling progressively marks visible items
- Per-panel independent state

### Command Palette (Cmd+K)

Universal search for navigating entire application:
- **Map navigation:** Jump to any region (Global, MENA, Europe, Asia-Pacific, Americas, Africa, Oceania)
- **Layer presets:** Military, Finance, Infrastructure, Intel, All, None, Minimal
- **Individual layers:** 30+ toggleable layers
- **All panels:** Every panel searchable by name and keywords
- **Country briefs:** Search country name to open intelligence brief or navigate map
- **Time range:** Filter events by 1h, 6h, 24h, 48h, 7d
- **View controls:** Dark/light mode, fullscreen, settings, refresh all

### Source Filtering

**SOURCES button** — global source management modal
- Search filter by name
- Individual toggle (click to enable/disable)
- Bulk actions: "Select All" / "Select None"
- Counter display: "45/77 enabled"
- Persistence: LocalStorage
- **Filtering at fetch time** (not display time) — reduces bandwidth and API calls
- Disabled sources affect all news panels simultaneously

### Marker Clustering

Dense regions use intelligent clustering to prevent visual clutter:
- Markers within pixel radius (adaptive to zoom) merge into cluster badges
- Cluster badges show count
- Clicking cluster opens popup listing all grouped items
- Zooming in reduces cluster radius, eventually showing individual markers

**Grouping Logic Examples:**
- **Protests:** Cluster within same country only (riots sorted first, high severity prioritized)
- **Tech HQs:** Cluster within same city (Big Tech → unicorns → public companies)
- **Tech Events:** Cluster within same location (sorted by date, soonest first)

### Map Controls & Interaction

**Map Marker Design:**
- Infrastructure markers (nuclear, economic centers, ports) display **without labels** to reduce clutter
- Full information via interaction:
  - **Hidden label layers:** Nuclear facilities, economic centers, protests, military bases
  - **Visible label layers:** Hotspots, conflicts

**Shareable Links** — view state encoded in URL
| Parameter | Description |
|-----------|-------------|
| `lat`, `lon` | Map center coordinates |
| `zoom` | Zoom level (1-10) |
| `time` | Active time filter (1h, 6h, 24h, 7d) |
| `view` | Preset view (global, us, mena) |
| `layers` | Comma-separated enabled layer IDs |

Example: `?lat=38.9&lon=-77&zoom=6&layers=bases,conflicts,hotspots`

---

## Data Layers (45+ Categories)

### Geopolitical Intelligence

| Layer | Description |
|-------|-------------|
| **Conflicts** | Active conflict zones with involved parties and status |
| **Hotspots** | Intelligence hotspots with activity levels based on news correlation |
| **Sanctions** | Countries under economic sanctions regimes |
| **Protests** | Live social unrest events from ACLED and GDELT |

### Military & Strategic

| Layer | Description |
|-------|-------------|
| **Military Bases** | 226 global installations from 9 operators |
| **Nuclear Facilities** | Power plants, weapons labs, enrichment sites |
| **Gamma Irradiators** | IAEA-tracked Category 1-3 radiation sources |
| **APT Groups** | State-sponsored cyber threat actors with geographic attribution |
| **Spaceports** | 12 major launch facilities (NASA, SpaceX, Roscosmos, CNSA, ESA, ISRO, JAXA) |
| **Critical Minerals** | Strategic mineral deposits (lithium, cobalt, rare earths) with operator info |

### Infrastructure

| Layer | Description |
|-------|-------------|
| **Undersea Cables** | 86 submarine cable routes worldwide |
| **Pipelines** | 88 operating oil & gas pipelines |
| **Internet Outages** | Network disruptions via Cloudflare Radar |
| **AI Datacenters** | 313 AI compute clusters (Epoch AI dataset) |

### Transport

| Layer | Description |
|-------|-------------|
| **Ships (AIS)** | Live vessel tracking via AIS with 62 strategic ports |
| **Delays** | FAA airport delay status and ground stops |

### Natural Events

| Layer | Description |
|-------|-------------|
| **Natural** | USGS earthquakes (M4.5+) + NASA EONET events (storms, wildfires, volcanoes, floods) |
| **Weather** | NWS severe weather warnings |

### Overlays & Labels

| Layer | Description |
|-------|-------------|
| **Day/Night** | Real-time solar terminator overlay (updates every 5 minutes) |
| **Economic** | Tabbed panel: FRED indicators, EIA oil analytics, USASpending.gov contracts |
| **Countries** | Country boundary labels |
| **Waterways** | Strategic waterways and chokepoints |
| **Trade Routes** | 19 global trade routes with multi-segment arcs through chokepoints |
| **Fires (FIRMS)** | NASA FIRMS satellite fire detection (VIIRS thermal hotspots) |

### Webcams

| Layer | Description |
|-------|-------------|
| **Live Webcams** | 22 live streams across 5 geopolitical regions with automatic fallback handling |

---

## Intelligence Panels

### Core Intelligence

| Panel | Purpose |
|-------|---------|
| **AI Strategic Posture** | Theater-level military aggregation with strike capability analysis |
| **Strategic Risk Overview** | Composite risk score combining all intelligence modules |
| **Country Instability Index** | Real-time stability scores for 24 monitored countries |
| **Infrastructure Cascade** | Dependency analysis for cables, pipelines, and chokepoints |
| **Live Intelligence** | GDELT-powered topic feeds (Military, Cyber, Nuclear, Sanctions) |
| **Intel Feed** | Curated defense and security news sources |
| **Country Brief** | AI-generated country profiles with key indicators, risk factors, recent developments |

### Specialized Monitoring

| Panel | Purpose |
|-------|---------|
| **Aviation Intelligence** | 6-tab panel (Ops, Flights, Airlines, Tracking, News, Prices) with NOTAM closure detection across 111 airports |
| **Climate Anomalies** | Temperature/precipitation deviations across 15 zones using Open-Meteo ERA5 data |
| **Displacement Tracking** | UN OCHA HAPI refugee, asylum seeker, IDP data with origin/host country perspectives |
| **Gulf Economies** | Indices, currencies, oil data for 6 GCC countries |
| **WTO Trade Policy** | Active trade restrictions, tariff trends, bilateral trade flows, SPS/TBT barriers |
| **Central Banks & BIS** | Policy rates and monetary decisions from 13 central banks |
| **Market Watchlist** | User-defined stock/commodity/crypto symbol lists (up to 50 symbols) |

### Regional Intelligence

| Panel | Coverage | Key Topics |
|-------|----------|-----------|
| **Middle East** | MENA region | Israel-Gaza, Iran, Gulf states, Red Sea |
| **Africa** | Sub-Saharan Africa | Sahel instability, coups, insurgencies, resources |
| **Latin America** | Central & South America | Venezuela, drug trafficking, regional politics |
| **Asia-Pacific** | East & Southeast Asia | China-Taiwan, Korean peninsula, ASEAN |
| **Energy & Resources** | Global | Oil markets, nuclear, mining, energy security |

---

## Live News Streams

Embedded YouTube live streams with **YouTube IFrame Player API** (not raw iframe):

**Channels:** Bloomberg, Sky News, Euronews, DW News, France 24, Al Arabiya, Al Jazeera

**Features:**
- **Channel switcher:** One-click switching
- **Live indicator:** Blinking dot shows stream status, click to pause/play
- **Mute toggle:** Audio control (muted by default)
- **Double-width panel:** Larger video player

**Performance Benefits of IFrame API:**
| Feature | Benefit |
|---------|---------|
| **Persistent player** | No iframe reload on mute/play/channel change |
| **API control** | Direct `playVideo()`, `pauseVideo()`, `mute()` calls |
| **Reduced bandwidth** | Same stream continues across state changes |
| **Faster switching** | Channel changes via `loadVideoById()` |

**Idle Detection:**
| Trigger | Action |
|---------|--------|
| **Tab hidden** | Stream pauses (Visibility API) |
| **5 min idle** | Stream pauses (no mouse/keyboard activity) |
| **User returns** | Stream resumes automatically |
| **Manual pause** | User intent tracked separately |

---

## Market Data & Analysis

**Stock Tracking:**
- Major indices and tech stocks via Finnhub (Yahoo Finance backup)
- **Sector Heatmap:** Visual sector performance (11 SPDR sectors)
- **Market Watchlist:** User-defined symbols (up to 50)

**Commodities:**
- Oil, gold, natural gas, copper, VIX
- **Oil Analytics:** EIA data (WTI/Brent prices, US production, US inventory with weekly changes)

**Crypto:**
- Bitcoin, Ethereum, Solana via CoinGecko
- **BTC ETF Tracker:** ETF flows tracking
- **Stablecoins:** Market monitoring

**Economic Indicators:**
- Fed data via FRED (assets, rates, yields)
- **Government Spending:** USASpending.gov recent federal contracts and awards

**Prediction Markets:**
- Polymarket integration for event probability tracking
- Correlation analysis with news events
- **Geopolitical filtering:** Keywords-based inclusion/exclusion to focus on relevant markets

---

## Design Principles & Patterns

### Core Philosophy

| Principle | Implementation |
|-----------|----------------|
| **Speed over perfection** | Keyword classifier instant; LLM refines asynchronously. Users never wait. |
| **Assume failure** | Per-feed circuit breakers (5-min cooldowns), AI fallback chain (Ollama → Groq → OpenRouter → browser T5) |
| **Show what you can't see** | Intelligence gap tracker explicitly reports data source outages |
| **Browser-first compute** | Analysis (clustering, instability scoring, surge detection) runs client-side |
| **Local-first geolocation** | Browser-side ray-casting against GeoJSON polygons (sub-ms, zero API dependency, works offline) |
| **Multi-signal correlation** | Focal points require convergence across news + military + markets + protests before critical alert |
| **Geopolitical grounding** | Hard-coded conflict zones, baseline country risk, strategic chokepoints prevent false alerts |
| **Defense in depth** | CORS origin allowlist, domain-allowlisted RSS proxy, server-side API key isolation |
| **Cache everything, trust nothing** | 3-tier caching (in-memory → Redis → upstream) with stale-on-error fallback |
| **Bandwidth efficiency** | Gzip compression (80% reduction), content-hash static assets (1-year immutable cache) |
| **Baseline-aware alerting** | Trending keywords use rolling 2-hour windows against 7-day baselines |
| **Contract-first APIs** | Proto definitions with field validation, HTTP annotations, code generation |
| **Run anywhere** | Same codebase → 5 variants (geopolitical, tech, finance, commodity, happy) |
| **Graceful degradation** | Every feature degrades when dependencies unavailable. Missing API keys skip source, don't crash. |
| **Multi-source corroboration** | Critical signals use multiple independent sources (ACLED + GDELT for protests, Haversine deduplication) |
| **No framework overhead** | Vanilla TypeScript with direct DOM manipulation, event delegation, custom Panel/VirtualList classes |
| **Type-safe data flow** | Discriminated unions (`_kind` field), proto-generated typed clients/servers, exhaustive switch matching |

### Intelligence Analysis Tradecraft

**Structured Analytic Techniques (SATs):**
- Country Instability Index decomposes "instability" into 4 weighted components (unrest, conflict, security, info velocity)
- Strategic Risk Score decomposes geopolitical risk into convergence, CII, infrastructure, theater, breaking news

**Analysis of Competing Hypotheses (ACH):**
- Multi-source corroboration requirement (news + military + markets + protests) before critical alert
- No single data stream drives critical alert alone

**Intelligence Gap Awareness:**
- Data freshness tracker reports "what can't be seen"
- 31 sources with status categorization (fresh, stale, very_stale, no_data, error, disabled)
- Two sources (GDELT, RSS) flagged as `requiredForRisk` — absence degrades CII scoring
- Critical source outage displayed prominently, not silently omitted

**Source Credibility Weighting:**
- 4-tier hierarchy (wire services → major outlets → specialty → aggregators)
- State-affiliated sources tagged with propaganda risk indicators
- Higher-tier sources carry more weight in focal point detection

**Temporal Context:**
- Welford's online baseline computation provides context
- "50 military flights" is meaningless without knowing 7-day baseline is 15 (3.3σ above normal)

**Kill Chain Awareness:**
- Breaking News Alert Pipeline 5-origin design:
  1. RSS alerts (initial detection)
  2. Keyword spikes (confirm emerging narratives)
  3. Hotspot escalation (corroborating signals)
  4. Military surge (corroborating signals)
  5. OREF sirens (ground truth)

### Algorithmic Design Decisions

**Logarithmic vs. Linear Protest Scoring:**
- Democracies: `log(protestCount)` — routine protests don't indicate instability
- Authoritarian states: Linear scaling — each event significant

**Welford's Online Algorithm for Baselines:**
- Running mean and M2 (sum of squared deviations) updated in O(1) time and O(1) space
- Tracks baselines for hundreds of event-type × region × weekday × month combinations
- No raw observation storage required

**H3 Hexagonal Grid for GPS Jamming:**
- Hexagonal grids (H3 resolution 4, ~22km edge) instead of rectangular lat/lon cells
- Benefits: Uniform adjacency (6 neighbors vs 4/8), equal area at any latitude, no meridian convergence distortion

**Cosine-Latitude-Corrected Distance:**
- Equirectangular approximation with `cos(lat)` longitude correction instead of full Haversine
- <0.5% error at distances involved (50–600km), ~10× faster
- Important when computing distances against 500+ infrastructure assets per event

**Negative Caching:**
- When upstream API returns error, cache failure state for defined period (5 min UCDP, 30s Polymarket)
- Prevents thundering-herd effects on downed APIs
- Provides clear signal to intelligence gap tracker

**O(1) Inflection Suffix Matching:**
- Keyword-matching pipeline checks English inflection suffixes (`-ing`, `-ed`, `-tion`, `-ment`)
- Converted from Array (O(n) `.some()`) to Set (O(1) `.has()`)
- Eliminates linear scan on every word of every headline

**Stack-Safe Array Operations:**
- `Math.min(...array)` and `Math.max(...array)` spread patterns limited by V8 argument stack (~65,535 entries)
- Large news clusters overflow stack → `Infinity` / `-Infinity`, corrupting timestamps
- Replaced with `Array.prototype.reduce` loops (O(1) stack space)

---

## TypeScript Architecture Patterns

### Vanilla TypeScript (No Framework)

**Why no framework:**
- **Bundle size:** Dashboard loads dozens of data layers, ML models, live video. Every KB of framework overhead competes with intelligence data.
- **DOM control:** Panel system manipulates `innerHTML` directly with debounced content replacement. Framework virtual DOM diffing would fight this.
- **WebView compatibility:** Tauri desktop app runs in WKWebView (macOS) and WebKitGTK (Linux) with idiosyncratic behavior.
- **Long-term simplicity:** No framework version upgrades, no breaking API migrations, no adapter libraries.

**Framework gap filled by:**
| Concern | Solution |
|---------|----------|
| Component model | `Panel` base class with lifecycle methods (`render`, `destroy`), debounced content updates, event delegation |
| State management | `localStorage` for user preferences, `CustomEvent` dispatch for inter-panel communication |
| Routing | URL query parameters (`?view=`, `?c=`, `?layers=`) parsed at startup; `history.pushState` for deep links |
| Reactivity | `SmartPollLoop` and `RefreshScheduler` classes with named refresh runners, visibility-aware scheduling |
| Virtual scrolling | Custom `VirtualList` with DOM element pooling, top/bottom spacer divs, `requestAnimationFrame`-batched scroll |

### Discriminated Union Marker System

All map markers carry `_kind` discriminant field:
```typescript
type MapMarker =
  | { _kind: 'conflict'; lat: number; lon: number; severity: string; ... }
  | { _kind: 'flight'; lat: number; lon: number; callsign: string; ... }
  | { _kind: 'vessel'; lat: number; lon: number; mmsi: number; ... }
  | { _kind: 'protest'; lat: number; lon: number; crowd_size: number; ... }
  // ... 15+ additional marker kinds
```

**Benefits:**
- Exhaustive `switch` matching in rendering pipeline — TypeScript compiler verifies every marker kind handled
- Adding new kind produces compile errors at every unhandled site
- Marker data serializable to/from JSON (IndexedDB persistence, Web Worker transfer) without custom logic
- Same marker objects flow through clustering, tooltip generation, layer filtering without type casting

---

## API & Data Pipeline

### Proto-First API Contracts

Entire API surface defined in Protocol Buffer (`.proto`) files using [sebuf](https://github.com/SebastienMelki/sebuf):
- Code generation produces TypeScript clients, server handler stubs, OpenAPI 3.1.0 docs from single source
- **24 service domains:** aviation, climate, conflict, cyber, displacement, economic, infrastructure, intelligence, maritime, market, military, news, prediction, research, seismology, supply-chain, trade, unrest, wildfire, giving, positive-events
- **Field validation:** `buf.validate` constraints (e.g., latitude ∈ [−90, 90]) generated automatically
- **Breaking changes:** Caught at CI time via `buf breaking` against main branch

**Code generation pipeline:**
```bash
# Makefile drives buf generate with 3 custom sebuf protoc plugins:
protoc-gen-ts-client → typed fetch-based client classes (src/generated/client/)
protoc-gen-ts-server → handler interfaces and route descriptors (src/generated/server/)
protoc-gen-openapiv3 → OpenAPI 3.1.0 specs in YAML and JSON (docs/api/)
```

**Edge gateway:**
- Single Vercel Edge Function (`api/[domain]/v1/[rpc].ts`) imports all 22 `createServiceRoutes()` functions
- Flat `Map<string, handler>` router
- Every RPC is POST endpoint at static path (e.g., `POST /api/aviation/v1/list-airport-delays`)
- CORS enforcement, top-level error boundary, rate-limit support
- Same router runs locally via Vite dev-server plugin with HMR

### Bootstrap Hydration

**Eliminates cold-start latency** by pre-fetching 38 datasets in single Redis pipeline call:
- **Fast tier** (s-maxage=1200, 20 min): earthquakes, outages, serviceStatuses, macroSignals, chokepoints, marketQuotes, commodityQuotes, positiveGeoEvents, riskScores, flightDelays, insights, predictions, iranEvents
- **Slow tier** (s-maxage=7200, 2 hours): bisPolicy, bisExchange, bisCredit, minerals, giving, sectors, etfFlows, shippingRates, wildfires, climateAnomalies, cyberThreats, techReadiness, theaterPosture, naturalEvents, cryptoQuotes, gulfQuotes, stablecoinMarkets, unrestEvents, ucdpEvents

**Pattern:**
```
Page Load → parallel fetch ─┬─ /api/bootstrap?tier=fast  (800ms timeout)
                             └─ /api/bootstrap?tier=slow  (800ms timeout)
```

**Edge function:** Reads all keys in single Upstash Redis pipeline — one HTTP round-trip for up to 38 keys

**Panel consumption:**
- Results stored in in-memory `hydrationCache` Map
- Panels call `getHydratedData(key)` → returns pre-fetched data, evicts from cache (one-time read)
- Panels finding hydrated data skip initial API call, render instantly
- Panels mounting after hydration consumed fall back to normal fetch cycle

**Negative sentinel caching:**
- When Redis key contains no data, bootstrap stores `__WM_NEG__` sentinel
- Consumers distinguish "data not yet loaded" (key absent) vs. "data source empty" (negative sentinel)
- Prevents unnecessary RPC fallback calls

**Selective fetching:**
- Clients can request custom subset via `?keys=earthquakes,flightDelays,insights`

**Result:** Converts 38 independent API calls into exactly 2, cutting first-meaningful-paint time by 2–4 seconds

### SmartPollLoop — Adaptive Data Refresh

Core refresh orchestration primitive used by all data-fetching panels:

**Adaptive behaviors:**
- **Exponential backoff:** Consecutive failures multiply poll interval by `backoffMultiplier` (default 2×), up to 4× base interval
- **Hidden-tab throttle:** When `document.visibilityState` is `hidden`, poll interval × `hiddenMultiplier` (default 5×)
  - Panel polling every 60s slows to every 5 min when tab backgrounded
- **Manual trigger:** `handle.triggerNow()` forces immediate poll regardless of current interval
- **Attempt tracking:** Consecutive failure counter feeds into circuit breaker. After `maxAttempts` failures, poll loop stops.
- **Reason tagging:** Each poll carries `SmartPollReason` (`'interval'`, `'resume'`, `'manual'`, `'startup'`)

**Panel integration:**
- Panels create `SmartPollLoop` in constructor with base interval and callback
- Call `handle.start()` on mount, `handle.stop()` on destroy
- Loop paused automatically when panel collapsed or scrolled out of view (IntersectionObserver)
- Resumed when panel reappears

### Railway Seed Data Pipeline

**21 Railway cron jobs** continuously refresh Redis cache with pre-computed data:
- Seeds run every 5–15 minutes (configurable per source)
- Write both canonical domain key (for RPC handlers) and bootstrap key (for page-load hydration)
- Dual-key strategy ensures bootstrap hydration and RPC handlers agree on data format/freshness

**Examples:**
| Seed Script | Data Source | Update Frequency | Bootstrap Key |
|-------------|-------------|------------------|---------------|
| `seed-earthquakes` | USGS M4.5+ | 5 min | `seismology:earthquakes:v1` |
| `seed-market-quotes` | Yahoo Finance | 5 min | `market:stocks-bootstrap:v1` |
| `seed-cyber-threats` | Feodo, URLhaus, C2Intel, OTX, AbuseIPDB | 10 min | `cyber:threats-bootstrap:v2` |
| `seed-insights` | Groq LLM world brief + top stories | 10 min | `news:insights:v1` |

**In-flight promise coalescing:**
- `cachedFetchJson` uses in-flight promise map
- If seed run overlaps previous run still writing, concurrent write deduplicated
- First request creates and registers Promise, all concurrent requests for same key await that Promise
- Prevents cache stampede

**Failure handling:**
- Failed seed runs log errors but never corrupt existing cached data
- Previous cache entry persists until successful run replaces it

---

## Mobile Experience

### First-Time Mobile Welcome

Modal on first mobile visit:
- Simplified view notice
- Navigation tip (regional views, marker interaction)
- "Don't show again" checkbox (localStorage persistence)

### Mobile-First Design (screens <768px or touch devices)

**Layout changes:**
- **Compact map:** Reduced height (40vh) to show more panels
- **Single-column layout:** Panels stack vertically
- **Hidden map labels:** All marker labels hidden to reduce clutter
- **Fixed layer set:** Layer toggle buttons hidden, curated set enabled by default
- **Simplified controls:** Map resize handle and pin button hidden
- **Touch-optimized markers:** Expanded touch targets (44px)
- **Hidden DEFCON indicator:** Pentagon Pizza Index hidden
- **Hidden FOCUS selector:** Regional focus buttons hidden (use preset views)
- **Compact header:** Social link shows X logo instead of username text

### Mobile Default Layers

Curated set focuses on essential intelligence:
- **Enabled:** Conflicts, Hotspots, Sanctions, Outages, Natural, Weather
- **Disabled:** Military bases, nuclear, spaceports, minerals, cables, pipelines, datacenters, AIS vessels, military flights, protests, economic centers

**Rationale:** Provides situational awareness without overwhelming interface or consuming excessive data/battery

---

## Offline ML Capabilities

Browser-side machine learning works without server connection:
- **Threat Classification:** 3-stage pipeline (keyword pre-filter → browser ML model → optional LLM refinement)
- **Headline Scoring:** ML-based importance scoring for priority rendering
- **Entity Extraction:** Client-side NER for countries, organizations, key figures

**Benefits:**
- Models run entirely in browser via Web Workers
- Intelligence analysis capabilities offline or without API keys
- Zero network dependency for core analysis

---

## Platform Variants (Same Codebase)

World Monitor runs **5 specialized variants** from single codebase:

| Variant | URL | Focus | Layers |
|---------|-----|-------|--------|
| **🌍 World Monitor** | worldmonitor.app | Geopolitical intelligence, military, conflict, infrastructure security | 29 geopolitical + military + infrastructure |
| **💻 Tech Monitor** | tech.worldmonitor.app | Tech sector intelligence, AI/startup ecosystems, cloud, tech events | 12 startup/cloud/cyber |
| **😊 Happy Monitor** | happy.worldmonitor.app | Positive news, global progress, science breakthroughs, conservation | 5 positive-events/conservation |
| **💰 Finance Monitor** | finance.worldmonitor.app | Global markets, stock exchanges, central banks, commodities, forex, crypto | 15 exchange/banking/trade |
| **⛏️ Commodity Monitor** | commodity.worldmonitor.app | Commodity markets, mining sites, processing plants, supply chains | Mining/metals/energy |

**Variant switcher** in header allows seamless navigation while preserving map position and panel config

---

## Cool UI Effects & Patterns

### Visual Design Elements

**Atmosphere Shader (3D Globe):**
- Fresnel limb-glow effect simulates atmospheric scattering at globe edge
- Photorealistic day/night transition

**Day/Night Terminator:**
- Real-time solar terminator overlay (updates every 5 minutes)
- Divides map into sunlit and dark hemispheres

**Beta Indicator:**
- Pulsing cyan "BETA" badge when globe active
- Signals newer feature

**Cluster Badges:**
- Count display on grouped markers
- Click to expand into popup listing all grouped items

**Glow Highlight:**
- 30-second subtle animation on new items
- Draws attention without being intrusive

**NEW Tag:**
- 2-minute badge on newly-arrived items
- Clear visual signal of fresh data

### Interaction Patterns

**Inertial Pan:**
- Single-finger pan with velocity continuation
- 0.92 decay factor, 4-entry circular touch history
- Natural, physics-based feel

**Bottom-Sheet Popups:**
- Drag-to-dismiss
- Mobile-native pattern

**8px Movement Threshold:**
- Prevents accidental interaction during taps
- Distinguishes tap from drag

**Progressive Disclosure:**
- Detail layers appear only when zoomed in
- Prevents overwhelming at world view

**Zoom-Adaptive Opacity:**
- Markers fade from 0.2 at world view to 1.0 at street level
- Subtle visual hierarchy

**Label Deconfliction:**
- Overlapping labels suppressed by priority
- Highest-severity first

---

## Key Takeaways for Atlas Intel

### Architecture Validation

✅ **globe.gl + Three.js is production-proven** for intelligence dashboards  
✅ **Vanilla TypeScript** (no framework) viable for complex applications  
✅ **Panel-based UI** with drag-and-drop provides excellent UX  
✅ **Client-side intelligence** (clustering, scoring, surge detection) scales well

### Must-Implement Features

**High Priority:**
1. **Dual engine support** (3D globe + 2D flat map) with runtime switching
2. **Smart clustering** with context-aware grouping logic
3. **Debounced marker flush** to prevent Three.js crashes during rapid updates
4. **Background pause** — stop WebGL render loop when window unfocused
5. **Bootstrap hydration** — pre-fetch datasets in single batch call
6. **SmartPollLoop** — adaptive data refresh with backoff and visibility awareness
7. **Panel system** with drag-to-reorder, collapse, visibility toggles
8. **Command palette (Cmd+K)** for universal navigation
9. **Activity tracking** — NEW tags, glow highlights, panel badges
10. **Shareable links** — encode map state in URL

**Medium Priority:**
1. **Event delegation pattern** for panels (survives innerHTML updates)
2. **Discriminated union markers** (`_kind` field) for type safety
3. **Progressive disclosure** — detail layers appear only when zoomed in
4. **Zoom-adaptive opacity** (0.2 → 1.0)
5. **Mobile-first design** with curated layer set, compact layout
6. **Touch gestures** — inertial pan, pinch-zoom, bottom-sheet popups
7. **Timezone-based region detection** for auto-centering
8. **Source filtering** modal with search, bulk actions, persistence
9. **Map theme switching** (dark, light, grayscale variants)
10. **Negative caching** to prevent thundering-herd on downed APIs

**Low Priority (Polish):**
1. Atmosphere shader for 3D globe
2. Day/night terminator overlay
3. Live news streams with idle detection
4. Variant switcher for specialized views
5. Beta indicator badge
6. Label deconfliction by priority

### Design Patterns to Adopt

**Graceful Degradation:**
- Missing API keys skip source, don't crash
- Failed upstream APIs serve stale cached data
- Browser-side ML works without server

**Intelligence Gap Awareness:**
- Explicitly report data source outages
- Status categorization (fresh, stale, very_stale, no_data, error, disabled)
- Flag sources as `requiredForRisk`

**Multi-Source Corroboration:**
- Critical signals require convergence across independent sources
- ACLED + GDELT for protests (Haversine deduplication)
- No single data stream drives critical alert alone

**Baseline-Aware Alerting:**
- Rolling 2-hour windows against 7-day baselines
- Welford's online algorithm for O(1) time and space
- "50 flights" meaningless without knowing baseline is 15

**Local-First Geolocation:**
- Browser-side ray-casting against GeoJSON polygons
- Sub-millisecond response, zero API dependency, works offline

### Performance Optimizations to Copy

1. **Debounced marker flush** — batch scene graph updates
2. **Background pause** — stop render loop when unfocused, queue updates, flush on visibility
3. **In-flight promise coalescing** — deduplicate concurrent cache misses
4. **Progressive disclosure** — detail layers only when zoomed in
5. **Zoom-adaptive opacity** — fade markers 0.2 → 1.0
6. **Smart clustering** — adaptive thresholds by zoom level
7. **Bootstrap hydration** — pre-fetch 38 datasets in 2 parallel calls
8. **SmartPollLoop** — exponential backoff, hidden-tab throttle
9. **Negative caching** — cache failure state to prevent hammering downed APIs
10. **O(1) inflection suffix matching** — Set instead of Array for keyword normalization
11. **Stack-safe array operations** — reduce instead of spread for large arrays
12. **Virtual scrolling** — DOM element pooling, spacer divs, `requestAnimationFrame` batching

---

## Implementation Roadmap for Atlas Intel

### Phase 1: Core Architecture (Week 1-2)
- [ ] Implement Panel base class with event delegation
- [ ] Discriminated union marker system (`_kind` field)
- [ ] Debounced marker flush for Three.js
- [ ] Background pause (WebGL render loop)
- [ ] Bootstrap hydration (batch data fetch)
- [ ] SmartPollLoop with adaptive refresh

### Phase 2: UI Components (Week 3-4)
- [ ] Command palette (Cmd+K) for navigation
- [ ] Panel drag-and-drop reordering
- [ ] Panel collapse/visibility toggles
- [ ] Activity tracking (NEW tags, glow highlights)
- [ ] Shareable links (URL state encoding)
- [ ] Source filtering modal

### Phase 3: Map Features (Week 5-6)
- [ ] Dual engine support (3D globe + 2D flat map)
- [ ] Smart clustering with context-aware grouping
- [ ] Progressive disclosure (zoom-based layer visibility)
- [ ] Zoom-adaptive opacity (0.2 → 1.0)
- [ ] Day/night terminator overlay
- [ ] Regional presets (8 views)

### Phase 4: Mobile & Polish (Week 7-8)
- [ ] Mobile-first design (compact layout, curated layers)
- [ ] Touch gestures (inertial pan, pinch-zoom, bottom-sheet)
- [ ] Timezone-based region detection
- [ ] Map theme switching (dark, light, grayscale)
- [ ] First-time mobile welcome modal
- [ ] Label deconfliction by priority

### Phase 5: Intelligence Features (Week 9-10)
- [ ] Multi-source corroboration system
- [ ] Intelligence gap awareness tracker
- [ ] Baseline-aware alerting (Welford's algorithm)
- [ ] Local-first geolocation (GeoJSON ray-casting)
- [ ] Browser-side ML capabilities
- [ ] Negative caching for failed APIs

---

## Technical Debt & Lessons Learned

### Things They Got Right

✅ **Vanilla TypeScript decision** — no framework overhead, full DOM control, long-term simplicity  
✅ **Discriminated unions** — type safety + serialization + exhaustive checking  
✅ **Event delegation** — survives debounced innerHTML updates  
✅ **Background pause** — eliminates idle GPU load  
✅ **Bootstrap hydration** — eliminates cold-start waterfall  
✅ **SmartPollLoop** — adaptive to network conditions and visibility  
✅ **Proto-first APIs** — single source of truth prevents schema drift  
✅ **Intelligence gap awareness** — explicitly reports what can't be seen  
✅ **Multi-source corroboration** — no single source drives critical alerts

### Things to Improve

❌ **Stack overflow on large arrays** — needed to replace spread with reduce  
❌ **O(n) inflection suffix matching** — converted Array to Set for O(1)  
❌ **No offline map tiles initially** — added service worker caching  
❌ **Monolithic edge function** — split into 22 per-domain functions  
❌ **Cold start latency** — added bootstrap hydration

### Warnings for Our Implementation

⚠️ **Three.js scene graph crashes** — debounce marker updates  
⚠️ **WebGL continuous render loop** — pause when idle/backgrounded  
⚠️ **Event listeners on innerHTML** — use event delegation on stable container  
⚠️ **V8 argument stack limit** — use reduce for large arrays, not spread  
⚠️ **Cache stampede** — use in-flight promise coalescing  
⚠️ **Thundering herd on API failures** — implement negative caching  
⚠️ **Mobile touch targets** — 44px minimum, 8px movement threshold  
⚠️ **Missing intelligence gaps** — explicitly track and report data source outages

---

## Conclusion

World Monitor demonstrates that **globe.gl + Three.js** is production-ready for intelligence dashboards handling dozens of data layers, thousands of markers, and real-time updates. Their vanilla TypeScript approach validates our architecture choice and proves complex applications don't need framework overhead.

**Key validation:** They're running the exact stack we chose (globe.gl + Three.js) with sophisticated features (smart clustering, progressive disclosure, multi-source correlation) at production scale across 5 platform variants. This confirms our architecture can scale to meet Atlas Intel requirements.

**Biggest wins to steal:**
1. Debounced marker flush (prevents Three.js crashes)
2. Background pause (eliminates idle GPU load)
3. Bootstrap hydration (eliminates cold-start waterfall)
4. SmartPollLoop (adaptive refresh)
5. Panel system with event delegation
6. Command palette (Cmd+K)
7. Intelligence gap awareness
8. Multi-source corroboration

**Next steps:** Implement Phase 1 (core architecture) focusing on Panel system, discriminated unions, debounced marker flush, background pause, and bootstrap hydration. These foundational patterns unlock everything else.
