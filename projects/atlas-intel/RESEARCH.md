# Atlas Intel: Open-Source Tools & APIs Research

**Generated:** 2026-03-23  
**Purpose:** Comprehensive reference for multimodal intelligence platform integration

---

## 🚀 Recommended Build Order

**WEEK 1 - Core Infrastructure:**
1. **Loughran-McDonald Sentiment Lists** → Direct CSV download, plug-and-play
2. **FinBERT** → HuggingFace API, ready for production
3. **yfinance** → Already available, extend coverage
4. **FRED API** → Essential macro data, simple REST API

**WEEK 2 - Alternative Data:**
5. **AISStream.io** → Free WebSocket, real vessel tracking
6. **OpenSky Network** → Academic API for flight data
7. **NASA FIRMS** → Fire/thermal detection near refineries
8. **Alpha Vantage** → Price data fallback (500 calls/day free)

**WEEK 3 - Advanced Signals:**
9. **Gemini Embedding API** → Multimodal embeddings for correlation analysis
10. **Sentinel Hub** → Satellite imagery (EU Copernicus, free tier)
11. **OBSYD architecture** → Learn from their chokepoint/correlation patterns

**DON'T BUILD (YET):**
- GeoSentinel → Impressive but massive scope, overkill for MVP
- MiroFish → Experimental, compute-heavy, not production-ready
- ADS-B Exchange → Requires commercial license, expensive
- IMF PortWatch → 3-5 day lag makes it less useful for real-time signals

---

## 1. Financial NLP Databases & Lexicons

### Loughran-McDonald Sentiment Word Lists ⭐ USE NOW

**URL:** https://sraf.nd.edu/loughranmcdonald-master-dictionary/

**Download URLs:**
- CSV: https://drive.google.com/file/d/1cfg_w3USlRFS97wo7XQmYnuzhpmzboAY/view?usp=sharing
- XLSX: https://docs.google.com/spreadsheets/d/1y2LVPvRqdggmIhSnHQcEZA5lYbe3vS5w/edit?usp=sharing

**What it provides:**
- 7 sentiment categories: negative, positive, uncertainty, litigious, strong modal, weak modal, constraining
- ~2,300 financial context words (extended from 2of12inf dictionary)
- Complexity/readability scoring (2024 JFQA measure)
- Word frequency across 10-K filings and earnings calls
- Year-tagged additions/removals (tracks evolution since 1993)

**Free tier:** Free for academic research. Commercial license required (contact loughranmcdonald@gmail.com)

**Integration:**
```python
import pandas as pd
lm_dict = pd.read_csv('LM_MasterDictionary_1993-2024.csv')
negative_words = lm_dict[lm_dict['Negative'] > 0]['Word'].tolist()
```

**Python module available:** Included in download package (loads dictionary + sentiment components)

**Setup complexity:** Easy (1 CSV file, no API)

**How it connects:** Score 10-K filings, earnings call transcripts, Fed minutes, analyst reports for sentiment shifts → market reaction prediction

**Verdict:** ✅ **USE NOW** - Industry standard, immediate value, zero dependencies

---

### FinBERT ⭐ USE NOW

**URL:** https://huggingface.co/ProsusAI/finbert

**What it provides:**
- Pre-trained BERT fine-tuned on Financial PhraseBank dataset
- 3-class classification: positive/negative/neutral sentiment
- Softmax confidence scores per label
- Handles financial jargon (trained on finance domain corpus)

**Free tier:** HuggingFace Inference API free tier (1,000 requests/day). Unlimited if self-hosted.

**API endpoint:**
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

text = "Revenue exceeded expectations but margins declined"
inputs = tokenizer(text, return_tensors="pt", padding=True)
outputs = model(**inputs)
predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
# Returns: [positive_prob, negative_prob, neutral_prob]
```

**Setup complexity:** Easy (pip install transformers, 3 lines of code)

**How it connects:** Real-time sentiment scoring of news, 10-Ks, Twitter, analyst notes → feed into trade signal generation

**Verdict:** ✅ **USE NOW** - Battle-tested, cited in 1900+ papers, production-ready

---

### Harvard General Inquirer / LIWC Financial Adaptations 🔍 INTEGRATE LATER

**Status:** Harvard GI is public domain (inquirer.jar available), but financial adaptations are scattered across academic papers. No single authoritative download.

**What exists:**
- Harvard GI base: 11,788 words, 182 categories (including Positiv/Negativ)
- LIWC-22: Commercial license ($90), includes financial/work categories
- Academic papers adapt GI for finance (e.g., Tetlock 2007 used GI negative words)

**Free tier:** Harvard GI base is free. LIWC requires purchase.

**Practical reality:** Loughran-McDonald supersedes Harvard GI for finance (GI has false positives like "tax" flagged negative in general context but neutral in 10-Ks)

**Verdict:** ⏸️ **SKIP** - Loughran-McDonald already covers this better for financial text

---

### Fed Hawkish-Dovish Scoring (Embedding Axis / Jay Alfaras) 🔍 INTEGRATE LATER

**Background:** Research by Bybee, Kelly, Manela (2020) and extensions use word embeddings to measure Fed policy stance along hawkish-dovish axis.

**Key paper:** "The Structure of Economic News" - constructs semantic axis from FOMC statements

**What it does:**
- Projects Fed statements onto hawkish (rate hikes, inflation concern) ↔ dovish (accommodation, stimulus) axis
- Uses word2vec or GloVe embeddings trained on Fed corpus
- Tracks semantic drift over time

**Jay Alfaras work:** Could not locate specific public implementation from Jay Alfaras. May be proprietary research.

**DIY approach:**
1. Train word2vec on Fed speeches/FOMC minutes corpus
2. Define anchor words: hawkish = ["hike", "tighten", "inflation"] vs dovish = ["accommodation", "stimulus", "dovish"]
3. Project documents onto this axis using cosine similarity

**Setup complexity:** Medium (requires NLP pipeline, corpus collection, embedding training)

**Verdict:** 🔄 **INTEGRATE LATER** - Valuable for macro signals, but requires custom implementation. Not a plug-and-play API.

---

### Open-Source Phrase → Market Reaction Datasets 🔍 INTEGRATE LATER

**Status:** No comprehensive public dataset found. Academic datasets typically require IRB approval or are institution-locked.

**Closest alternatives:**
1. **FinancePhrase (LREC 2020):** Financial phrase corpus, not linked to market reactions
2. **Financial Sentiment Analysis datasets:** Twitter financial sentiment (NASDAQ/S&P500 mentions) available on Kaggle
3. **DIY approach:** Build from:
   - Combine Loughran-McDonald scores with price movements (yfinance)
   - Scrape 8-K filings + intraday price reactions
   - Earnings call transcripts (FactSet has API, expensive) + post-earnings drift

**Verdict:** 📊 **BUILD CUSTOM** - No ready-made solution. Combine L-M dictionary + yfinance to build training corpus.

---

## 2. Vessel & Maritime Tracking (Free APIs)

### AISStream.io ⭐ USE NOW

**URL:** https://aisstream.io

**What it provides:**
- Real-time AIS vessel positions via WebSocket
- Global coverage (terrestrial + satellite AIS)
- Ship metadata: MMSI, IMO, vessel type, dimensions, destination, ETA
- Message types: position reports, static data, voyage info

**Free tier:**
- **Unlimited WebSocket connections**
- Real-time streaming (1-5 second updates per vessel)
- Requires free API key (sign up at aisstream.io)

**API Example:**
```python
import websockets
import json

async def connect_ais():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {
            "APIKey": "YOUR_KEY_HERE",
            "BoundingBoxes": [[[29.0, 47.0], [30.0, 48.0]]]  # Bosphorus Strait
        }
        await websocket.send(json.dumps(subscribe_message))
        
        async for message in websocket:
            ais_message = json.loads(message)
            print(ais_message['MetaData']['ShipName'], ais_message['Message']['PositionReport'])
```

**Setup complexity:** Easy (WebSocket client, 10 lines of code)

**Use case for Atlas Intel:**
- Track oil tankers through Strait of Hormuz, Suez Canal, Malacca Strait
- Detect floating storage (vessels stationary 7+ days)
- Ship-to-ship (STS) transfer detection
- Voyage time estimation (origin → destination)

**Limitations:**
- Terrestrial coverage ~50km from coast (gaps in open ocean)
- Vessels can disable AIS transponders (spoofing/dark ships)
- No cargo volume data (only vessel class/DWT estimation)

**Verdict:** ✅ **USE NOW** - Best free real-time maritime data. OBSYD uses this as primary source.

---

### AISHub 🔄 INTEGRATE LATER

**URL:** https://www.aishub.net

**What it provides:**
- HTTP API for global AIS snapshots (polling, not streaming)
- Contributor network (requires reciprocal data sharing OR subscription)

**Free tier:**
- Free if you contribute AIS data from your own receiver
- Otherwise: subscription required (~€50/month)

**API format:** REST, JSON or CSV

**Verdict:** 🔄 **INTEGRATE LATER** - Use as fallback if AISStream fails. Requires contribution or payment for full access.

---

### MarineTraffic Free Tier ⏸️ SKIP

**URL:** https://www.marinetraffic.com (now acquired by Kpler)

**Status:** Kpler now owns MarineTraffic. Free tier severely limited.

**What it provides (commercial):**
- Real-time AIS, predictive ETAs, port call events
- Historical voyage data back to 2010
- Ship-to-ship transfer detection

**Free tier:** Web UI only, no free API access. API starts at $500+/month.

**Verdict:** ⏸️ **SKIP** - Too expensive. Use AISStream instead.

---

### IMF PortWatch 🔄 INTEGRATE LATER

**URL:** https://portwatch.imf.org

**What it provides:**
- Chokepoint transit counts (Hormuz, Suez, Malacca, Panama, Bab el-Mandeb, Turkish Straits)
- Historical baseline comparisons (e.g., "Suez transits down 40% vs 3-year average")
- Disruption event annotations (Suez blockage, Houthi attacks, etc.)

**Free tier:** Public dashboard, unclear if API available. May require manual scraping.

**Update frequency:** Daily, but **3-5 day publication lag**

**Use case:** Macro disruption signals (e.g., Red Sea rerouting → Brent price impact)

**Limitations:**
- Lag makes it less useful for real-time trading
- Transit counts, not cargo volumes

**Verdict:** 🔄 **INTEGRATE LATER** - Useful for weekly macro reports, not day trading. OBSYD already includes this.

---

### OBSYD Project ⭐ ARCHITECTURE REVIEW

**URL:** https://github.com/jo20ow/Obsyd  
**Live Demo:** https://obsyd.dev

**What it is:**
- Open-source energy market intelligence dashboard
- Built with FastAPI + React + deck.gl
- MIT License (free to fork/modify)

**Architecture highlights:**

**Backend:**
- Dual AIS ingestion: AISStream (WebSocket primary) + AISHub (HTTP fallback)
- SQLite + WAL mode for storage (single-writer, sufficient for moderate traffic)
- APScheduler for 20+ periodic data jobs
- Signal engine: rule-based heuristics (e.g., "Suez traffic down 30% + Brent up 5% → alert")

**Data pipeline:**
1. **Vessel enrichment:** MMSI → ship class (VLCC/Suezmax/Aframax), DWT estimation from dimensions
2. **Geofence zones:** 6 chokepoints (Hormuz, Suez, Malacca, Panama, Cape of Good Hope, Houston)
3. **Floating storage detection:** Vessels stationary 7+ days within geofence
4. **Voyage tracking:** Zone-to-zone transit matrix (e.g., Persian Gulf → Rotterdam)
5. **Correlation engine:** Pearson r between chokepoint traffic and Brent price (lag optimization up to 7 days)
6. **Rerouting index:** Cape vs Suez traffic ratio (detects Red Sea disruptions)

**Data sources:**
- AISStream (real-time AIS)
- AISHub (fallback AIS)
- IMF PortWatch (chokepoint transits)
- EIA API (US crude inventories, refinery utilization, SPR)
- FRED API (historical oil prices, DXY, yields)
- yfinance (live commodity futures: CL=F, BZ=F, NG=F, GC=F)
- NASA FIRMS (thermal hotspots near refineries)
- Finnhub (energy news headlines)

**What we can reuse:**
- Geofence zone logic (chokepoint definitions)
- Vessel classification heuristics (AIS dimensions → ship type)
- Correlation engine approach (traffic vs price with lag optimization)
- Anomaly detection rules (e.g., "Cushing drawdown + backwardation → bullish signal")
- API key management strategy (graceful degradation if keys missing)

**Limitations (OBSYD openly admits):**
- No satellite AIS (gaps in ocean coverage)
- Vessel counts, not cargo volumes (barrels unknown)
- yfinance unofficial (may lag or fail)
- SQLite not suitable for high-concurrency

**Verdict:** 🛠️ **ARCHITECTURE GOLD MINE** - Don't reinvent the wheel. Fork specific modules (geofence logic, correlation engine). Already production-proven.

---

### UN Comtrade (Trade Flow Data) 🔄 INTEGRATE LATER

**URL:** https://comtradeplus.un.org

**What it provides:**
- Official UN trade statistics (imports/exports by commodity and country)
- Monthly/annual granularity
- Free API access

**API:** REST, JSON

**Limitations:**
- 1-3 month lag (official statistics are slow)
- Not useful for real-time trading

**Verdict:** 🔄 **INTEGRATE LATER** - Background macro data only. Too slow for signals.

---

## 3. Flight Tracking (Free APIs)

### OpenSky Network ⭐ USE NOW (Academic)

**URL:** https://opensky-network.org  
**API Docs:** https://openskynetwork.github.io/opensky-api/

**What it provides:**
- Real-time ADS-B flight positions (state vectors)
- ICAO 24-bit aircraft address, callsign, latitude, longitude, altitude, velocity, heading
- Historical data access via Trino (SQL queries)
- 15-second state vector validity (if no update, aircraft dropped from API)

**Free tier:**
- **Anonymous users:** 400 API calls/day, rate limit 10 calls/10 seconds
- **Registered users (free):** 4,000 API calls/day
- **Academic credentials:** Unlimited API access + full Trino database

**API Example:**
```bash
# All current flights
curl "https://opensky-network.org/api/states/all"

# Flights in bounding box (lat/lon)
curl "https://opensky-network.org/api/states/all?lmin=45.8389&lmax=47.8229&lomin=5.9962&lomax=10.5226"
```

**Setup complexity:** Easy (REST API, no authentication required for basic tier)

**Use case for Atlas Intel:**
- Track military cargo flights (C-17, C-130) → troop movements
- Executive jets near oil fields/refineries → M&A activity
- Tanker aircraft (KC-135, KC-46) → military readiness signals
- Flight density over conflict zones

**Signals that matter:**
- **Military cargo spike** → geopolitical tension (e.g., US cargo flights to Middle East)
- **Executive jets** → M&A or emergency board meetings (e.g., NetJets to Houston refinery → acquisition rumor)
- **Tanker flights** → Pre-deployment refueling (precedes conflicts)

**Limitations:**
- ADS-B requires line-of-sight (gaps over oceans)
- Military aircraft can disable transponders
- No passenger manifests or cargo data

**Citation requirement:**
```
Matthias Schäfer et al., "Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research," 
IPSN 2014, pp. 83-94
```

**Verdict:** ✅ **USE NOW** - Best free flight data. Apply for academic account if affiliated with university.

---

### ADS-B Exchange ⏸️ SKIP (Commercial Required)

**URL:** https://www.adsbexchange.com/data/

**What it provides:**
- Largest **unfiltered** ADS-B network (includes military, FAA blocklist, VIP aircraft)
- 2 Hz position updates (twice per second)
- Historical data available

**Free tier:** Enthusiast use only (personal, non-commercial). No bulk access.

**Commercial tier:** Required for any business use. Pricing not public (contact for quote, likely $1,000+/month).

**Verdict:** ⏸️ **SKIP** - OpenSky provides sufficient coverage for free. ADS-B Exchange's unique value (unfiltered military) requires expensive license.

---

### FlightRadar24 Free Tier ⏸️ SKIP

**URL:** https://www.flightradar24.com

**Free tier:** Web UI only, no API. Commercial API extremely expensive ($$$).

**Verdict:** ⏸️ **SKIP** - No free API. OpenSky is superior alternative.

---

## 4. Satellite & Earth Observation (Free)

### NASA FIRMS (Fire Information for Resource Management System) ⭐ USE NOW

**URL:** https://firms.modaps.eosdis.nasa.gov/api/

**What it provides:**
- Thermal hotspot detection from MODIS (Terra/Aqua) and VIIRS (NOAA-20, Suomi NPP)
- Fire radiative power (FRP) in MW
- Latitude, longitude, confidence level, brightness temperature
- Near real-time (NRT): 3-hour latency. Standard: 1-2 month latency.

**Free tier:** Free with NASA Earthdata account (register at earthdata.nasa.gov)

**API Example:**
```bash
# Active fires in bounding box (last 24h)
curl "https://firms.modaps.eosdis.nasa.gov/api/area/csv/YOUR_MAP_KEY/VIIRS_SNPP_NRT/29.0,47.0,31.0,49.0/1"

# Returns CSV: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp
```

**Setup complexity:** Easy (REST API, CSV output)

**Use case for Atlas Intel:**
- **Refinery fires** → production disruption (e.g., thermal spike at Cushing, OK)
- **Oil field flaring** → production levels (more flaring = more output)
- **Pipeline explosions** → supply chain disruptions
- **Conflict zones** → battles near oil infrastructure

**Limitations:**
- Clouds block thermal detection
- Low spatial resolution (375m for VIIRS, 1km for MODIS)
- False positives (gas flares vs fires)

**Verdict:** ✅ **USE NOW** - Unique refinery/conflict signal. OBSYD already integrates this.

---

### Sentinel Hub (EU Copernicus) 🔄 INTEGRATE LATER

**URL:** https://docs.sentinel-hub.com/api/latest/

**What it provides:**
- Multispectral satellite imagery (Sentinel-1 SAR, Sentinel-2 optical, Sentinel-3 ocean)
- Process API: custom band combinations, indices (NDVI, NDWI, etc.)
- 5-day revisit time (Sentinel-2), 6-day (Sentinel-1)

**Free tier:**
- Trial account: 3 months, limited requests
- Copernicus Data Space: Free access, but requires cloud processing setup (AWS/GCS)

**API Example (pseudo):**
```python
# Sentinel-2 true color image
evalscript = """
//VERSION=3
function setup() {return {input: ["B04", "B03", "B02"], output: {bands: 3}}}
function evaluatePixel(sample) {return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02]}
"""
# Call Process API with AOI + time range
```

**Setup complexity:** Medium (requires evalscripts, cloud infra knowledge)

**Use case for Atlas Intel:**
- **SAR backscatter** → Cushing tank levels (OBSYD's experimental approach)
- **Optical imagery** → Port congestion (container stacking density)
- **Oil slick detection** → Pipeline leaks, tanker spills

**Limitations:**
- Cloud cover blocks optical imagery
- SAR requires expert interpretation
- Processing compute costs (even if data is free)

**Verdict:** 🔄 **INTEGRATE LATER** - Powerful but complex. Start with NASA FIRMS (simpler), graduate to Sentinel.

---

### NASA GIBS (Global Imagery Browse Services) 🔄 INTEGRATE LATER

**URL:** https://gibs.earthdata.nasa.gov

**What it provides:**
- Pre-rendered satellite imagery tiles (daily mosaics)
- Supports WMTS, WMS standards (easy map integration)
- 1,000+ imagery layers (MODIS, VIIRS, Landsat, etc.)

**Free tier:** Completely free, no API key required

**Use case:** Background map layers (e.g., show thermal hotspots on NASA daily imagery)

**Verdict:** 🔄 **INTEGRATE LATER** - Nice-to-have for visualization, not primary signal source.

---

### Planet Free Tier ⏸️ SKIP

**URL:** https://www.planet.com

**Free tier:** Education/Research program (must apply, approval required). Otherwise commercial only.

**What it provides:**
- 3m resolution daily imagery (180+ satellites)
- Sub-daily revisits

**Limitations:**
- Free tier very restrictive (limited AOI, must justify research use)
- Commercial pricing starts at $10,000s/year

**Verdict:** ⏸️ **SKIP** - Too expensive. Sentinel-2 (10m resolution, free) is sufficient.

---

### What's Actually Useful vs Noise?

**USEFUL FOR MARKET SIGNALS:**
- ✅ NASA FIRMS thermal hotspots → refinery fires, oil field production
- ✅ Sentinel-1 SAR → Cushing tank levels (experimental but promising per OBSYD)
- ✅ AIS + optical imagery → Port congestion (e.g., Shanghai container backlog)

**NOISE / LOW SIGNAL:**
- ❌ Daily satellite mosaics → Too slow for trading (use for research only)
- ❌ Cloud-free optical imagery → Weather-dependent, unreliable
- ❌ General environmental monitoring → Not actionable for finance

---

## 5. CCTV & Visual Intelligence

### GeoSentinel Project ⏸️ SKIP (Impressive but Overkill)

**URL:** https://github.com/h9zdev/GeoSentinel

**What it is:**
- Geospatial monitoring platform combining AIS, ADS-B, CCTV, satellite tracking, dark web search, OSINT
- Built with Python (Flask), deck.gl, TomTom Maps, Ollama (local LLM)
- **Creative Commons Non-Commercial license** (can't use commercially without permission)

**Features:**
- Live CCTV feeds overlaid on 3D globe
- Flight + vessel tracking (similar to OBSYD but broader scope)
- Criminal search, traffic cameras, satellite tracking
- Dark web search via TOR integration
- GeoSential AI assistant for automated tracking

**Data sources:**
- TomTom Maps (requires API key)
- AISstream.io (vessel tracking)
- ADSB.one (flight tracking)
- OpenCellID (cell tower locations)
- OpenSky Network (flight metadata)
- Traffic camera APIs (public webcams)

**Architecture:**
- Monolithic Flask app (not microservices)
- Real-time WebSocket updates
- 3D globe with deck.gl + Mapbox

**What's impressive:**
- Integration breadth (CCTV + satellite + flights + vessels + dark web)
- UI/UX polish (better than most OSINT tools)
- YOLO-based aerial segmentation

**Practical feasibility for Atlas Intel:**

**❌ DON'T USE DIRECTLY:**
1. **License issue:** Non-commercial CC BY-NC 4.0 → can't use in trading platform without explicit permission
2. **Scope creep:** CCTV feeds, criminal search, WiFi geolocation are tangential to commodity trading
3. **Setup complexity:** Requires TomTom API, Mapbox token, Ollama, TOR daemon, multiple API keys
4. **Maintenance burden:** 10,000+ lines of code, tightly coupled architecture

**✅ CONCEPTS TO BORROW:**
1. **Port webcam monitoring:** Track vessel queues at key ports (Houston, Rotterdam, Singapore)
2. **Traffic camera analysis:** Refinery access road congestion → production activity
3. **Multi-source correlation:** Combine CCTV + AIS + flight data for richer context

**Practical implementation:**
- **Week 1:** Manual monitoring of Houston ship channel webcam (https://porthouston.com/cameras/)
- **Month 3:** Automate screenshot capture + YOLO vessel counting
- **Don't build:** Full GeoSentinel clone (90% of features are irrelevant)

**Verdict:** ⏸️ **SKIP DIRECT INTEGRATION** - Too broad, license restrictions, overkill for MVP. Cherry-pick concepts (port webcams) only.

---

### Public Traffic Camera APIs 🔄 INTEGRATE LATER

**Examples:**
- **Port of Houston:** https://porthouston.com/cameras/ (public webcams)
- **TomTom Traffic API:** Real-time traffic flow data (free tier: 2,500 requests/day)
- **Open511:** Road events API (US/Canada)

**Use case:**
- Refinery access road congestion → production ramp-up
- Port vessel queues → loading delays

**Setup complexity:** Easy (public webcams) to Medium (TomTom API integration)

**Verdict:** 🔄 **INTEGRATE LATER** - Low-hanging fruit after core data sources established. Start with Houston port webcam.

---

### Practical Feasibility Assessment

**IS VISUAL INTELLIGENCE ACTUALLY USEFUL?**

**YES (with caveats):**
- Port congestion is a **leading indicator** (e.g., Shanghai backlog → shipping delays → supply chain impact)
- Refinery activity visible from traffic/parking lot density (e.g., shift workers → utilization rate)
- Thermal detection (FIRMS) already provides refinery fire signals

**NO (for most CCTV):**
- Manual webcam monitoring doesn't scale
- YOLO vessel counting requires compute + engineering effort
- Most public cameras have poor coverage (e.g., no Strait of Hormuz webcam)

**VERDICT:** 🎯 **USEFUL BUT NICHE** - Worth 10% of effort, not 50%. Focus on:
1. NASA FIRMS thermal detection (already implemented by OBSYD)
2. AIS-based port congestion (vessel count in geofence)
3. Manual monitoring of 3-5 key webcams (Houston, Rotterdam, Singapore)

Don't build computer vision pipeline until core AIS/flight/price data is working.

---

## 6. Market Data (Free APIs)

### Yahoo Finance (yfinance) ⭐ USE NOW

**What it provides:**
- Historical OHLCV data (stocks, commodities, crypto, indices)
- 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo intervals
- Intraday data (up to 7 days for 1m interval, 60 days for 5m)
- Fundamental data (P/E, dividend yield, market cap, etc.)

**Free tier:** Unlimited (unofficial API, no rate limits enforced)

**Python library:**
```python
import yfinance as yf

# Commodity futures
brent = yf.Ticker("BZ=F")  # Brent Crude
wti = yf.Ticker("CL=F")    # WTI Crude
natgas = yf.Ticker("NG=F") # Natural Gas

# Historical data
df = brent.history(period="1y", interval="1d")
```

**Limitations:**
- Unofficial (Yahoo can break API anytime)
- ~15 min delay on quotes (not true real-time)
- Occasional outages
- No options chain for commodities

**Verdict:** ✅ **USE NOW** - Already available, widely used. Keep Alpha Vantage as backup.

---

### Alpha Vantage ⭐ USE NOW (Backup)

**URL:** https://www.alphavantage.co/documentation/

**What it provides:**
- Stock, forex, crypto, commodities time series
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- Fundamental data (income statement, balance sheet, cash flow)
- Economic indicators (GDP, CPI, unemployment)

**Free tier:**
- 25 API calls/day (severely limited)
- 5 API requests/minute

**Premium tier:**
- $49.99/month: 1,200 calls/day
- $249.99/month: 30,000 calls/day
- $499.99/month: 60,000 calls/day + realtime US stocks

**API Example:**
```bash
# Brent Crude Oil daily prices
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=BRENT&apikey=YOUR_KEY"

# Technical indicator (RSI)
curl "https://www.alphavantage.co/query?function=RSI&symbol=CL&interval=daily&time_period=14&apikey=YOUR_KEY"
```

**Setup complexity:** Easy (REST API, JSON)

**Verdict:** ✅ **USE NOW** - Free tier useful as yfinance backup. Premium tier if yfinance breaks.

---

### FRED (Federal Reserve Economic Data) ⭐ USE NOW

**URL:** https://fred.stlouisfed.org/docs/api/fred/

**What it provides:**
- 818,000+ US economic time series (GDP, inflation, employment, interest rates, etc.)
- Historical data back to 1776 (for some series)
- Energy data (WTI spot price, natural gas price, crude oil inventories)

**Free tier:** Free API key, no rate limits published

**API Example:**
```bash
# WTI Crude Oil spot price
curl "https://api.stlouisfed.org/fred/series/observations?series_id=DCOILWTICO&api_key=YOUR_KEY&file_type=json"

# US Crude Oil Inventories (EIA)
curl "https://api.stlouisfed.org/fred/series/observations?series_id=WCESTUS1&api_key=YOUR_KEY&file_type=json"
```

**Key series for Atlas Intel:**
- `DCOILWTICO` - WTI Crude Oil spot price
- `DCOILBRENTEU` - Brent Crude Oil spot price
- `WCESTUS1` - US Ending Stocks of Crude Oil
- `DGS10` - 10-Year Treasury Constant Maturity Rate
- `DEXCHUS` - China / US Foreign Exchange Rate

**Setup complexity:** Easy (REST API, JSON/XML)

**Verdict:** ✅ **USE NOW** - Essential for macro context. Zero reason not to use.

---

### CoinGecko (Crypto) 🔄 INTEGRATE LATER

**URL:** https://www.coingecko.com/en/api

**What it provides:**
- Cryptocurrency prices (20,000+ coins)
- Market cap, volume, price change %
- Historical data

**Free tier:**
- 30 calls/minute
- No API key required for public endpoints

**API Example:**
```bash
# Bitcoin price
curl "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
```

**Verdict:** 🔄 **INTEGRATE LATER** - Only relevant if crypto correlation to oil prices emerges (weak historically).

---

## 7. Gemini Embedding Model

### Google Gemini Multimodal Embeddings ⭐ USE NOW

**URL:** https://ai.google.dev/gemini-api/docs/embeddings

**Model name:** `text-embedding-004` (text only) or `embedding-001` (multimodal - deprecated)

**NEW MULTIMODAL MODEL (2024):**
- **Model:** `models/text-embedding-004` (text optimized)
- **Multimodal support:** Currently text-only. Multimodal embeddings (image/video/audio) were in `embedding-001` (now deprecated).
- **Dimensions:** 768 (configurable: 256, 512, 768)

**IMPORTANT:** As of 2024, Google has not released a production multimodal embedding model for Gemini API. Multimodal capabilities exist in Gemini 2.0 Flash (inference), but embeddings are text-only.

**API Documentation:**
- Text embeddings: https://ai.google.dev/gemini-api/docs/embeddings
- Multimodal inference (not embeddings): https://ai.google.dev/gemini-api/docs/vision

**Free Tier (Gemini API):**
- Free tier: 1,500 requests/day
- Rate limit: 60 requests/minute

**API Example (Text Embeddings):**
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

result = genai.embed_content(
    model="models/text-embedding-004",
    content="Brent crude oil prices rose 3% following OPEC production cuts",
    task_type="retrieval_document"
)

embedding = result['embedding']  # 768-dimensional vector
```

**Task types:**
- `retrieval_document` - For indexing documents
- `retrieval_query` - For search queries
- `semantic_similarity` - For comparing texts
- `classification` - For classification tasks

**Supported Input Formats (text-embedding-004):**
- Text only (plain text, markdown)
- Max input: 2,048 tokens per request

**Use Case for Atlas Intel:**
1. **Semantic search:** Embed news articles, 10-K filings, Fed statements → retrieve relevant docs for market events
2. **Correlation analysis:** Embed AIS voyage descriptions ("VLCC from Persian Gulf to Rotterdam") + embed news ("Suez Canal disruption") → find semantic matches
3. **Clustering:** Group similar market events (e.g., "refinery fire" vs "pipeline explosion" vs "hurricane shutdown")

**⚠️ Multimodal Limitation:**
Current Gemini API does NOT support multimodal embeddings (text + image + video + audio in single vector). For multimodal:
- Use Gemini 2.0 Flash for inference (describe image → text)
- Embed the text description with `text-embedding-004`
- OR wait for Google to release multimodal embedding model

**Alternative for Multimodal Embeddings:**
- **OpenAI CLIP:** Image + text embeddings (open-source)
- **ImageBind (Meta):** 6 modalities (image, text, audio, depth, thermal, IMU)

**Verdict:** ✅ **USE NOW (Text)** - Excellent for semantic search of news/filings. ⏸️ **WAIT (Multimodal)** - Not available yet in production API.

---

## 8. MiroFish Assessment

### MiroFish - Multi-Agent Swarm Intelligence Engine ⏸️ SKIP

**URL:** https://github.com/666ghj/MiroFish

**What it claims:**
- "Predicting Anything" via multi-agent simulation
- Constructs "parallel digital world" from seed information (news, policies, financial signals)
- Thousands of autonomous agents with memory + behavior logic simulate future scenarios
- Use cases: Public opinion prediction, novel plot generation, financial forecasting

**Architecture:**
- Multi-agent system powered by LLMs (Qwen, OpenAI-compatible APIs)
- GraphRAG for knowledge graph construction
- Zep Cloud for agent memory
- Dual-platform parallel simulation
- Report generation via specialized agent with tool access

**Tech Stack:**
- Backend: Python (FastAPI, Pydantic, APScheduler)
- Frontend: React 19 + Vite + Tailwind CSS 4
- LLM: Alibaba Qwen-plus (recommended), supports any OpenAI SDK-compatible API
- Memory: Zep Cloud (free tier: sufficient for small simulations)

**Demo Results:**
- Wuhan University public opinion prediction (see demo: https://666ghj.github.io/mirofish-demo/)
- Red Dream lost ending prediction (based on first 80 chapters)

**Can it actually do financial prediction?**

**❌ NO (not production-ready):**

1. **Experimental stage:** Project launched Feb 2025, still in active development
2. **No financial validation:** Demos focus on social media sentiment and fiction, not financial markets
3. **Computational cost:** Requires spinning up 1,000s of LLM agents → expensive API bills (Qwen-plus alone costs ~¥0.1/1000 tokens)
4. **Non-deterministic:** Agent interactions are stochastic, reproducibility unclear
5. **Latency:** Simulations take minutes to hours (not suitable for real-time trading)
6. **Black box:** No interpretability (how did agents decide X?)

**Compute Requirements:**
- Minimum: 10-40 rounds of simulation (demo uses this)
- Recommended: 100+ rounds for stability
- Each round = 1,000s of LLM API calls
- Example cost estimate: 40 rounds × 1,000 agents × 500 tokens/agent × $0.0005/1000 tokens = $10/simulation (rough)

**Is it production-ready?**

**NO:**
- Alpha stage (not even beta)
- No backtesting framework
- No financial benchmarks (e.g., "predicted oil price ±5% accuracy 60% of time")
- Requires deep LLM expertise to tune agent behaviors
- Docker deployment provided, but assumes you know how to scale

**Honest Verdict:**

**⏸️ SKIP FOR NOW, WATCH CLOSELY:**

- **Cool concept:** Multi-agent futures forecasting is intellectually interesting
- **Not practical:** Too experimental, too slow, too expensive, unvalidated for finance
- **Better alternatives exist:** Traditional econometric models (ARIMA, GARCH), ML models (XGBoost, LSTMs) have decades of financial backtesting

**When to revisit:**
1. Wait 12 months for project maturity
2. Look for published financial backtests (e.g., "MiroFish predicted 2023 oil price with X accuracy")
3. When LLM inference costs drop 10x (e.g., local Llama 4 on H100)

**What to use instead:**
- Correlation analysis (OBSYD's approach: chokepoint traffic vs Brent price)
- Time series forecasting (ARIMA, Prophet, LSTM)
- Sentiment → price regressions (Loughran-McDonald scores → stock returns)

---

## Summary: What to Integrate

| Tool/API | Verdict | Integration Timeline | Priority |
|----------|---------|----------------------|----------|
| **Loughran-McDonald** | ✅ USE NOW | Week 1 | HIGH |
| **FinBERT** | ✅ USE NOW | Week 1 | HIGH |
| **yfinance** | ✅ USE NOW | Day 1 (already available) | HIGH |
| **FRED API** | ✅ USE NOW | Week 1 | HIGH |
| **AISStream.io** | ✅ USE NOW | Week 2 | HIGH |
| **OpenSky Network** | ✅ USE NOW | Week 2 | HIGH |
| **NASA FIRMS** | ✅ USE NOW | Week 2 | MEDIUM |
| **Alpha Vantage** | ✅ USE NOW | Week 2 (backup) | MEDIUM |
| **Gemini Embeddings** | ✅ USE NOW | Week 3 | MEDIUM |
| **OBSYD Architecture** | 🛠️ LEARN FROM | Week 3 (study code) | HIGH |
| **Sentinel Hub** | 🔄 LATER | Month 2+ | LOW |
| **IMF PortWatch** | 🔄 LATER | Month 2+ | LOW |
| **Port Webcams** | 🔄 LATER | Month 3+ | LOW |
| **CoinGecko** | 🔄 LATER | If needed | LOW |
| **AISHub** | 🔄 LATER | If AISStream fails | LOW |
| **Harvard GI / LIWC** | ⏸️ SKIP | L-M is better | N/A |
| **Jay Alfaras Fed Model** | 🔄 LATER | Custom build | LOW |
| **GeoSentinel** | ⏸️ SKIP | Too broad | N/A |
| **ADS-B Exchange** | ⏸️ SKIP | Too expensive | N/A |
| **MarineTraffic** | ⏸️ SKIP | Too expensive | N/A |
| **Planet Satellite** | ⏸️ SKIP | Too expensive | N/A |
| **MiroFish** | ⏸️ SKIP | Not ready | N/A |

---

## Appendix: API Key Setup Checklist

**WEEK 1 SETUP:**
```bash
# Free registrations (no payment required)
1. AISStream.io → https://aisstream.io (instant)
2. OpenSky Network → https://opensky-network.org/user/registration (instant)
3. NASA Earthdata → https://urs.earthdata.nasa.gov/users/new (instant)
4. FRED → https://fredaccount.stlouisfed.org/apikeys (instant)
5. Alpha Vantage → https://www.alphavantage.co/support/#api-key (instant)
6. Google AI (Gemini) → https://aistudio.google.com/app/apikey (instant)

# Downloads (no auth required)
7. Loughran-McDonald dictionary → CSV from Google Drive
8. FinBERT → pip install transformers (downloads from HuggingFace)
```

**Environment variables:**
```bash
export AISSTREAM_API_KEY="your_key"
export OPENSKY_USER="your_username"
export OPENSKY_PASS="your_password"
export FIRMS_MAP_KEY="your_key"
export FRED_API_KEY="your_key"
export ALPHA_VANTAGE_KEY="your_key"
export GOOGLE_API_KEY="your_key"
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-23  
**Compiled by:** Atlas Research Sub-Agent  
**Next Review:** After MVP launch (3 months)
