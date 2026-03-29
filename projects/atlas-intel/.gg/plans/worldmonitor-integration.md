# Atlas Intel ← WorldMonitor Feature Integration Plan

## Current State

**Atlas Intel** is a Python/HTML intelligence platform with:
- A 3D globe (globe.gl) dashboard served via FastAPI (`dashboard/server.py`)
- Monolithic `app.js` (90KB) + `index.html` (48KB) + `styles.css` (31KB)
- 40+ Python feed trackers (`feeds/`) writing JSON to `dashboard/data/`
- Supabase/pgvector backend for embeddings + signal detection
- ~21 data layers (vessels, flights, military, earthquakes, cyber, etc.)

**WorldMonitor** is a Vanilla TypeScript/Vite intelligence platform with:
- Dual map engine: 3D globe (globe.gl) + 2D flat map (deck.gl + MapLibre)
- 37 panel components, 45+ data layers, 435+ RSS feeds
- Country Instability Index (CII), AI summarization, threat classification
- Live news channels (YouTube embeds), live webcams
- Strategic posture assessment, geographic convergence detection
- Local AI via Ollama, browser-side ML via Transformers.js/ONNX
- Finance radar, prediction markets, commodity tracking

---

## Architecture Decision

**Migrate Atlas Intel from monolithic HTML/JS to a Vite + TypeScript project** that mirrors WorldMonitor's architecture. This gives us:
- Proper module system, type safety, hot reload
- Same component patterns (Panel base class, services, config)
- Both 2D and 3D map engines
- Local AI model integration (Ollama)

### New Project Structure
```
atlas-intel/
├── src/
│   ├── main.ts                    # Entry point
│   ├── App.ts                     # App controller
│   ├── types/
│   │   └── index.ts               # All TypeScript types
│   ├── config/
│   │   ├── feeds.ts               # RSS feed definitions
│   │   ├── geo.ts                 # Hotspots, bases, nuclear sites, cables
│   │   ├── pipelines.ts           # Pipeline data
│   │   ├── countries.ts           # Country metadata + alias maps
│   │   ├── entities.ts            # Entity registry (66+ entities)
│   │   └── map-layer-definitions.ts
│   ├── components/
│   │   ├── Panel.ts               # Base panel class
│   │   ├── MapContainer.ts        # Map engine switcher (2D/3D)
│   │   ├── GlobeMap.ts            # 3D globe (globe.gl + Three.js)
│   │   ├── FlatMap.ts             # 2D map (deck.gl + MapLibre)
│   │   ├── CIIPanel.ts            # Country Instability Index
│   │   ├── CountryBriefPage.ts    # Full country intelligence dossier
│   │   ├── InsightsPanel.ts       # AI World Brief / Insights
│   │   ├── LiveNewsPanel.ts       # Live news channel embeds
│   │   ├── LiveWebcamsPanel.ts    # CCTV/webcam streams
│   │   ├── NewsPanel.ts           # News feed aggregation
│   │   ├── StrategicPosturePanel.ts # Theater posture assessment
│   │   ├── StrategicRiskPanel.ts  # Risk overview dashboard
│   │   ├── MarketPanel.ts         # Finance/market data
│   │   ├── CommodityPanel.ts      # Commodity tracking
│   │   ├── PredictionPanel.ts     # Prediction markets
│   │   ├── CascadePanel.ts        # Infrastructure cascade analysis
│   │   ├── DeductionPanel.ts      # AI forecasting panel
│   │   ├── MonitorPanel.ts        # Custom keyword monitors
│   │   ├── SignalBadge.ts         # Intelligence findings badge
│   │   ├── DefconIndicator.ts     # DEFCON status indicator
│   │   ├── EnergyPanel.ts         # Energy complex
│   │   ├── DisplacementPanel.ts   # UNHCR displacement data
│   │   ├── ClimateAnomalyPanel.ts # Climate anomalies
│   │   ├── AirlineIntelPanel.ts   # Airline/flight intelligence
│   │   └── TimelineChart.ts       # D3.js 7-day timeline
│   ├── services/
│   │   ├── data-bridge.ts         # Fetch from Python data_bridge JSONs
│   │   ├── rss-feeds.ts           # RSS feed aggregator
│   │   ├── cii-scoring.ts         # Country Instability Index algorithm
│   │   ├── signal-engine.ts       # Cross-stream correlation engine
│   │   ├── entity-registry.ts     # Entity knowledge base (66+ entities)
│   │   ├── threat-classifier.ts   # 3-tier threat classification
│   │   ├── convergence.ts         # Geographic convergence detection
│   │   ├── ai-summarizer.ts       # 4-tier AI summarization chain
│   │   ├── ollama.ts              # Ollama local AI integration
│   │   ├── breaking-news.ts       # Breaking news alert pipeline
│   │   ├── market-data.ts         # Market/finance data service
│   │   ├── theater-posture.ts     # Strategic theater assessment
│   │   ├── ml-worker.ts           # Browser-side ML (Transformers.js)
│   │   ├── headline-memory.ts     # Client-side RAG (IndexedDB vectors)
│   │   └── cache.ts               # 3-tier caching
│   ├── utils/
│   │   ├── dom-utils.ts           # h(), replaceChildren() helpers
│   │   ├── country-detection.ts   # Local GeoJSON point-in-polygon
│   │   ├── sanitize.ts            # DOMPurify wrappers
│   │   └── circuit-breaker.ts     # Fetch with circuit breaking
│   └── styles/
│       ├── main.css               # Primary dark theme
│       ├── panels.css             # Panel-specific styles
│       └── map.css                # Map styles
├── public/
│   ├── textures/                  # Globe textures (earth, water, night sky)
│   └── countries.geojson          # Country boundaries
├── api/                           # Vercel-style edge functions (optional)
├── feeds/                         # Existing Python feed trackers
├── atlas_intel/                   # Existing Python intelligence layer
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

---

## Feature Implementation Plan (30 Tasks)

### Phase 1: Foundation (Tasks 1-5)

#### Task 1: Initialize Vite + TypeScript project
- Create `package.json` with deps: `vite`, `typescript`, `globe.gl`, `three`, `deck.gl`, `maplibre-gl`, `d3`, `dompurify`, `marked`
- Create `vite.config.ts`, `tsconfig.json`, `index.html` entry
- Set up `@/` path alias
- Port CSS variables and dark theme from existing `styles.css`

#### Task 2: Core types and configuration
- Create `src/types/index.ts` with all interfaces: `NewsItem`, `CountryScore`, `MapMarker`, `TheaterPosture`, `Signal`, `LiveChannel`, `PizzIntStatus`, `CachedRiskScores`, etc.
- Create `src/config/countries.ts` — 24 monitored countries with alias maps
- Create `src/config/entities.ts` — 66+ entity registry
- Create `src/config/geo.ts` — port hotspots, military bases, nuclear sites, cables, waterways from existing `dashboard/data/` JSONs

#### Task 3: Base Panel system + App shell
- Create `src/components/Panel.ts` — base class with open/close, title, badge, draggable header
- Create `src/App.ts` — main app controller with panel registry, refresh scheduler
- Create `src/main.ts` — entry point, clock, top bar, system status
- Port the top bar layout (logo, classification badge, UTC clock, DEFCON indicator, status dots)

#### Task 4: Data bridge service (Python → TypeScript)
- Create `src/services/data-bridge.ts` that fetches JSON from `dashboard/data/*.json` endpoints
- FastAPI `server.py` already serves these; create typed fetch wrappers for each data type
- Add polling with configurable intervals per data source
- Add circuit breaker pattern for failed fetches

#### Task 5: Utility layer
- `src/utils/dom-utils.ts` — `h()`, `replaceChildren()`, `rawHtml()` hyperscript helpers
- `src/utils/circuit-breaker.ts` — fetch with retry, timeout, circuit break
- `src/utils/sanitize.ts` — DOMPurify wrappers
- `src/utils/country-detection.ts` — ray-casting point-in-polygon from GeoJSON

### Phase 2: Dual Map Engine (Tasks 6-9)

#### Task 6: 3D Globe (globe.gl + Three.js)
- Create `src/components/GlobeMap.ts`
- Earth textures: topo-bathy day surface, specular water map, night-sky starfield
- Atmosphere: Fresnel limb-glow shader (`#4466cc`)
- Auto-rotation: rotate when idle, pause on interaction, resume after 60s
- HTML marker layer with `_kind` discriminator
- Debounced marker flush for high-frequency updates
- Configurable render quality (Auto/Eco/Sharp/4K)
- Background pause when tab not visible
- Port existing globe initialization from `app.js`

#### Task 7: 2D Flat Map (deck.gl + MapLibre GL)
- Create `src/components/FlatMap.ts`
- Layer types: GeoJsonLayer, ScatterplotLayer, PathLayer, IconLayer, TextLayer, ArcLayer, HeatmapLayer
- Smart clustering via Supercluster
- Progressive disclosure (detail layers appear on zoom)
- Zoom-adaptive opacity (0.2 at world → 1.0 at street)
- Day/night terminator overlay
- Tile providers: OpenFreeMap (default), CARTO
- Dark/light themes per provider

#### Task 8: MapContainer + unified layer system
- Create `src/components/MapContainer.ts` — switches between 3D globe and 2D flat map
- 2D/3D toggle button in UI (matching WorldMonitor's toggle)
- Create `src/config/map-layer-definitions.ts` — unified layer catalog consumed by both engines
- 45+ layers: conflicts, military bases, nuclear sites, undersea cables, pipelines, flights, vessels, fires, protests, earthquakes, cyber, GPS jamming, webcams, infrastructure, trade routes, chokepoints, etc.
- Layer toggle sidebar with search, checkboxes, icons
- URL state sharing: `?lat=X&lon=Y&zoom=Z&layers=A,B,C&timeRange=7d`

#### Task 9: Map features + interactions
- 8 regional presets (Global, Americas, Europe, MENA, Asia, Africa, Oceania, Latin America)
- Time filtering (1h, 6h, 24h, 48h, 7d)
- Click-to-inspect popups for all marker types
- Timezone-based auto-center on first load
- Country click → open Country Brief page
- Cmd+K navigation palette

### Phase 3: Intelligence & Analysis (Tasks 10-16)

#### Task 10: Country Instability Index (CII)
- Create `src/services/cii-scoring.ts`
  - 3 components: Unrest (40%), Security (30%), Information (30%)
  - Log scaling for high-volume countries (media bias prevention)
  - Conflict zone floor scores (Ukraine 55, Syria 50, Yemen 50, etc.)
  - Contextual boosts: hotspot activity (+10), news urgency (+5), focal point (+8)
  - 24-hour trend detection (rising/stable/falling)
  - 15-minute learning mode warmup
- Create `src/components/CIIPanel.ts` — country list with scores, bars, trends, share buttons
  - Color-coded severity levels (Critical 81-100 red, High 66-80 orange, etc.)
  - Component breakdown (U:82 C:100 S:40 I:80 format)

#### Task 11: Country Brief / Intelligence Dossier page
- Create `src/components/CountryBriefPage.ts`
- Two-column layout:
  - **Left:** Instability Index ring (animated SVG 0-100), 4 component bars, intelligence brief (AI-generated), top 8 headlines
  - **Right:** Active Signals chips, 7-day timeline (D3.js), prediction markets, infrastructure exposure (600km radius)
- AI brief generation with citation anchors [1]-[8]
- Export: JSON, CSV, PNG, Print/PDF
- Headline relevance filtering with negative-match algorithm

#### Task 12: Signal Intelligence Engine
- Create `src/services/signal-engine.ts`
  - 12 signal types: Convergence, Triangulation, Velocity Spike, Prediction Leading, News Leads Markets, Market Move Explained, Silent Divergence, Sector Cascade, Flow Drop, Flow-Price Divergence, Geographic Convergence, Military Surge
  - Entity-aware correlation (66 entities with aliases, keywords, sectors)
  - Source tier ranking (Tier 1-4)
  - Signal deduplication with type-specific TTLs
  - Propaganda risk indicators for state media
- Create `src/components/SignalBadge.ts` — header badge with count + modal detail

#### Task 13: Geographic Convergence Detection
- Create `src/services/convergence.ts`
  - 1°×1° grid-based event clustering
  - 4 event types: protests, military flights, naval vessels, earthquakes
  - Convergence scoring: `type_score = types × 25 + min(25, total × 2)`
  - Alert thresholds: 4 types = Critical, 3 types = High

#### Task 14: Strategic Theater Posture Assessment
- Create `src/services/theater-posture.ts`
  - 9 operational theaters: Taiwan Strait, Persian Gulf, Baltic, Black Sea, Korean Peninsula, South China Sea, Eastern Mediterranean, Horn of Africa, Arctic
  - Posture levels: CRIT / HIGH / ELEVATED / NORMAL
  - Military flight + naval vessel correlation
  - Vessel augmentation with USNI fleet data
- Create `src/components/StrategicPosturePanel.ts` — theater cards with status, vessel counts, trend

#### Task 15: AI Insights / World Brief Panel
- Create `src/services/ai-summarizer.ts`
  - 4-tier provider chain: Ollama (local) → Groq → OpenRouter → Browser T5
  - Headline deduplication (Jaccard similarity > 0.6)
  - Redis/localStorage caching
  - Language-aware output
- Create `src/components/InsightsPanel.ts` — World Brief, focal point detection
- Create `src/components/DeductionPanel.ts` — AI forecasting with news context injection

#### Task 16: Threat Classification Pipeline
- Create `src/services/threat-classifier.ts`
  - Stage 1: Keyword classifier (~120 threat keywords, 14 categories)
  - Stage 2: Browser-side ML (Transformers.js NER + sentiment)
  - Stage 3: LLM classifier (batched, cached 24h)
  - Hybrid: keyword results shown instantly, ML/LLM refine async

### Phase 4: Live Feeds & News (Tasks 17-20)

#### Task 17: RSS Feed Aggregator
- Create `src/services/rss-feeds.ts`
  - 435+ curated feeds across 15 categories
  - Source tier ranking + propaganda risk tagging
  - Cluster merging (group similar headlines)
  - Velocity tracking (mentions/hour)
- Create `src/components/NewsPanel.ts` — scrollable news feed with threat badges, source tiers

#### Task 18: Live News Channels (CCTV/TV)
- Create `src/components/LiveNewsPanel.ts`
  - YouTube iframe player with channel switching
  - Channels: Bloomberg, SkyNews, Euronews, DW, CNBC, CNN, France 24, Al Arabiya, Al Jazeera
  - Mute/unmute, live indicator
  - Custom channel management (add/remove/reorder)
  - Channel count badge

#### Task 19: Live Webcams Panel
- Create `src/components/LiveWebcamsPanel.ts`
  - Curated strategic location webcams
  - Thumbnail previews, click to expand
  - Pin favorites
- Create `src/components/PinnedWebcamsPanel.ts`

#### Task 20: Breaking News Alert Pipeline
- Create `src/services/breaking-news.ts`
  - 5 alert origins: RSS critical, keyword spike, hotspot escalation, military surge, OREF siren
  - Per-event dedup (30-min TTL), global 60s cooldown
  - Recency gate (drop items >15 min old)
  - Source tier gating
  - Desktop notification + audio alert + banner

### Phase 5: Finance & Markets (Tasks 21-23)

#### Task 21: Market Data Panel
- Create `src/services/market-data.ts` — fetch stock indices, crypto, commodities
- Create `src/components/MarketPanel.ts`
  - 92 stock exchanges with live data
  - 7-signal market composite score
  - Market-news correlation display

#### Task 22: Commodity & Energy Panels
- Create `src/components/CommodityPanel.ts` — commodity news, gold/silver, energy/resources
- Create `src/components/EnergyPanel.ts` — oil, gas, pipeline flow tracking
- Commodity map layers: mining sites, processing plants, ports, hubs, critical minerals

#### Task 23: Prediction Markets Panel
- Create `src/components/PredictionPanel.ts`
  - Polymarket integration (top contracts by volume)
  - Probability bars + external links
  - Correlation with news signals

### Phase 6: Local AI & ML (Tasks 24-26)

#### Task 24: Ollama Local AI Integration
- Create `src/services/ollama.ts`
  - Auto-discover local Ollama endpoint
  - OpenAI-compatible `/v1/chat/completions` API
  - Model selection (auto-detect available models)
  - Use for: World Brief, Country Intelligence Brief, Deduction & Forecasting
  - Settings UI for endpoint configuration

#### Task 25: Browser-Side ML (Transformers.js/ONNX)
- Create `src/services/ml-worker.ts` — Web Worker for ML inference
  - Embeddings: all-MiniLM-L6-v2 (384-dim) for headline similarity
  - Sentiment analysis
  - NER (named entity recognition)
  - Topic classification
  - Lazy loading, worker isolation
- Create `src/services/headline-memory.ts`
  - Client-side RAG: IndexedDB vector store (5,000 cap, LRU eviction)
  - Cosine similarity search
  - Opt-in via settings toggle

#### Task 26: AI Deduction & Forecasting Panel
- Create `src/components/DeductionPanel.ts`
  - Free-text query input + geographic context
  - `buildNewsContext()` — inject 15 most recent headlines
  - Provider chain: Ollama → Groq → OpenRouter
  - Redis/localStorage caching (1h TTL)
  - Cross-panel integration (any panel can dispatch `wm:deduct-context` event)
  - 5-second cooldown between submissions

### Phase 7: Additional Panels (Tasks 27-29)

#### Task 27: Infrastructure Cascade Analysis
- Create `src/components/CascadePanel.ts`
  - Multi-domain cascade detection (power → comms → transport)
  - Infrastructure proximity analysis
  - Cascade scoring and alert generation

#### Task 28: Displacement, Climate, Airline Intelligence
- Create `src/components/DisplacementPanel.ts` — UNHCR displacement data
- Create `src/components/ClimateAnomalyPanel.ts` — temperature/precip anomalies by zone
- Create `src/components/AirlineIntelPanel.ts` — airport ops, flight delays, airline status

#### Task 29: Strategic Risk Overview
- Create `src/components/StrategicRiskPanel.ts`
  - Composite risk overview combining CII, convergence, cascades, posture
  - Learning mode indicator
  - Data freshness badges (live/cached/unavailable)

### Phase 8: Polish & Integration (Task 30)

#### Task 30: Panel layout, drag-drop, settings, responsive
- Draggable panel layout with configurable positions
- "ADD PANEL" button — available panels picker
- Settings panel: render quality, tile provider, map theme, AI provider, language
- Keyboard shortcuts (Cmd+K search, layer toggles)
- Mobile responsive (touch gestures, bottom sheets)
- URL state persistence
- DEFCON indicator with PizzInt-style calculation
- Export capabilities (JSON, CSV, PNG)
- Print/PDF support for briefs

---

## Data Flow

```
Python Feed Trackers (feeds/*.py)
        │
        ▼ write JSON files
dashboard/data/*.json
        │
        ▼ HTTP GET (FastAPI server.py)
TypeScript data-bridge.ts
        │
        ▼ typed data
Services (cii-scoring, signal-engine, convergence, etc.)
        │
        ▼ processed intelligence
Panels (CIIPanel, InsightsPanel, StrategicPosturePanel, etc.)
        │
        ▼ render
MapContainer (3D Globe / 2D Flat Map) + Side Panels
```

---

## Key Dependencies

```json
{
  "globe.gl": "^2.45.0",
  "three": "^0.170.0",
  "deck.gl": "^9.2.6",
  "maplibre-gl": "^5.16.0",
  "d3": "^7.9.0",
  "dompurify": "^3.1.7",
  "marked": "^17.0.3",
  "onnxruntime-web": "^1.23.2",
  "@xenova/transformers": "^2.17.0",
  "supercluster": "^8.0.1"
}
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Globe.gl + Three.js bundle size (>2MB) | Code splitting, lazy load globe only when 3D mode active |
| ONNX models large (~50MB) | Lazy load only when ML features enabled; opt-in setting |
| Rate limiting on free APIs | Circuit breakers, caching, graceful degradation |
| Python data_bridge dependency | JSON file interface = loose coupling; can swap to direct API later |
| Browser memory with 45+ layers | Progressive disclosure, visibility-aware polling, deactivate hidden panels |

---

## Verification Criteria

- [ ] Both 3D globe and 2D flat map render with all data layers
- [ ] CII scores calculate correctly for 24 countries
- [ ] Live news channels play and switch correctly
- [ ] AI summarization works via Ollama (local) with fallback chain
- [ ] Signal engine detects cross-stream correlations
- [ ] Country brief page shows full intelligence dossier
- [ ] All existing feed data (vessels, flights, military, etc.) displays on both map engines
- [ ] URL state sharing works (copy URL → same view)
- [ ] Mobile responsive with touch gestures
