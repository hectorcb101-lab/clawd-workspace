# Atlas Intel

**Multimodal Intelligence Platform**

Real-time intelligence gathering and analysis from diverse data sources: X/Twitter, AIS vessel tracking, satellite imagery, CCTV, news feeds, audio, and documents.

---

## Overview

Atlas Intel is a multimodal intelligence platform that:
1. **Ingests** data from multiple sources (social media, maritime tracking, satellite, CCTV, news)
2. **Embeds** content using Gemini's multimodal embedding model (3072 dimensions)
3. **Detects** market-moving signals from speeches, announcements, and events
4. **Links** signals to market reactions for ML training
5. **Tracks** feed health and reliability

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Data Sources                           │
├───────────┬──────────┬───────────┬──────────┬───────────────┤
│  X/Twitter│   AIS    │ Satellite │   CCTV   │  News/Audio   │
│   Videos  │ Vessels  │  Imagery  │ Footage  │   Documents   │
└─────┬─────┴────┬─────┴─────┬─────┴────┬─────┴───────┬───────┘
      │          │           │          │             │
      ▼          ▼           ▼          ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Ingestion Pipelines                         │
│  • X API stream  • AIS WebSocket  • Satellite API            │
│  • CCTV feeds    • News RSS       • Audio transcription      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Gemini Embedding                           │
│          (3072-dimensional multimodal vectors)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Supabase (PostgreSQL + pgvector)            │
│  • embeddings table (vector search)                          │
│  • signal_phrases (NLP extraction)                           │
│  • market_reactions (ML training)                            │
│  • feed_sources (health monitoring)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               Intelligence Layer                             │
│  • Semantic search  • Signal detection  • Market analysis    │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Tables
1. **`embeddings`** — Core multimodal embeddings
2. **`signal_phrases`** — Extracted market-moving phrases
3. **`market_reactions`** — Price movements post-signal
4. **`feed_sources`** — Source health monitoring

See `schema.sql` for full DDL.

---

## Storage Buckets

1. **`raw-media`** (public) — Raw ingested media (videos, audio, images)
2. **`processed`** (private) — Processed outputs (transcripts, reports)

See `storage-buckets.md` for details.

---

## Setup

### Prerequisites
- Python 3.12+
- Supabase account (free tier)
- Google AI API key (for Gemini embeddings)

### Installation

1. **Create Supabase project** (see `SETUP.md`)
2. **Install dependencies:**
   ```bash
   pip install supabase python-dotenv google-generativeai
   ```
3. **Configure credentials:**
   ```bash
   # Edit /home/ubuntu/clawd/config/supabase-atlas-intel.env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   GOOGLE_AI_API_KEY=your_gemini_api_key
   ```
4. **Run schema:**
   ```bash
   # Copy schema.sql into Supabase SQL Editor and run
   ```

---

## Usage Examples

### Ingest X Video
```python
from supabase import create_client
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('/home/ubuntu/clawd/config/supabase-atlas-intel.env')

# Initialize clients
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))

# Upload video
with open('fed_speech.mp4', 'rb') as f:
    supabase.storage.from_('raw-media').upload('x_videos/video123.mp4', f)

# Generate embedding
model = genai.GenerativeModel('models/embedding-exp')
video_url = supabase.storage.from_('raw-media').get_public_url('x_videos/video123.mp4')
embedding = model.embed_content(content=video_url, task_type="retrieval_document")

# Store in database
supabase.table('embeddings').insert({
    "source_type": "x_video",
    "source_id": "1234567890",
    "content_text": "Fed announces rate cut",
    "media_url": video_url,
    "embedding": embedding['embedding'],
    "metadata": {
        "author": "@finlay_mckie",
        "timestamp": "2026-03-23T10:00:00Z",
        "geo": {"lat": 51.5, "lon": -0.1}
    }
}).execute()
```

### Search Similar Content
```python
# Generate query embedding
query = "federal reserve interest rate decision"
query_embedding = model.embed_content(content=query, task_type="retrieval_query")

# Search (using custom function, see SETUP.md)
results = supabase.rpc('match_embeddings', {
    'query_embedding': query_embedding['embedding'],
    'match_threshold': 0.7,
    'match_count': 10
}).execute()

for result in results.data:
    print(f"{result['source_type']}: {result['content_text']} (similarity: {result['similarity']})")
```

### Detect Signal Phrases
```python
# Extract phrases from transcript
import re

transcript = "The Federal Reserve has decided to maintain interest rates at current levels..."
signal_keywords = ["rate cut", "rate hike", "inflation", "recession", "quantitative easing"]

detected_phrases = []
for keyword in signal_keywords:
    if keyword.lower() in transcript.lower():
        # Extract context (50 chars before/after)
        match = re.search(f'.{{0,50}}{keyword}.{{0,50}}', transcript, re.IGNORECASE)
        if match:
            detected_phrases.append({
                "phrase": keyword,
                "context": match.group(),
                "speaker": "Jerome Powell",
                "event_type": "fed_speech",
                "detected_at": "2026-03-23T10:00:00Z"
            })

# Store signals
for phrase_data in detected_phrases:
    supabase.table('signal_phrases').insert(phrase_data).execute()
```

---

## Data Sources

### Planned Integrations
- **X/Twitter:** API v2 stream (filtered by keywords/accounts)
- **AIS:** MarineTraffic or VesselFinder WebSocket
- **Satellite:** Planet Labs, Sentinel Hub
- **CCTV:** Custom feeds (ports, warehouses)
- **News:** RSS feeds (Reuters, Bloomberg, FT)
- **Audio:** Fed speeches, earnings calls (via YouTube/transcription APIs)

---

## Roadmap

- [ ] Build X ingestion pipeline
- [ ] Integrate Gemini multimodal embeddings
- [ ] Implement signal detection NLP
- [ ] Set up market data feeds (Yahoo Finance, Alpha Vantage)
- [ ] Build dashboard (Streamlit/Gradio)
- [ ] Train ML model (signal → reaction prediction)
- [ ] Add real-time alerting (Telegram/email)

---

## New Frontend (v2.0)

A modular **Vite + TypeScript** frontend replaces the previous Streamlit/Gradio dashboard with a full interactive intelligence UI featuring a 3D globe, live maps, and real-time data panels.

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js     | 18+     |
| npm          | 9+      |
| Python       | 3.11+   |

### Quick Start

```bash
# Install frontend dependencies
npm install

# Download globe textures and GeoJSON data
mkdir -p public/textures
curl -L -o public/textures/earth-topo.jpg https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg
curl -L -o public/textures/earth-water.png https://unpkg.com/three-globe/example/img/earth-water.png
curl -L -o public/textures/night-sky.png https://unpkg.com/three-globe/example/img/night-sky.png
curl -L -o public/countries.geojson https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson

# Start both servers (recommended)
bash scripts/dev.sh

# OR start separately:
python dashboard/server.py &     # Backend on :8000
npm run dev                      # Frontend on :5173
```

### Frontend Architecture

```
src/
├── components/    # 26 UI components (panels, maps, globe, indicators)
├── services/      # 14 data & intelligence services
├── config/        # Static configuration (countries, entities, feeds, geo data)
├── utils/         # DOM helpers, circuit breaker, sanitization
└── main.ts        # Entry point
```

- **`src/components/`** — Modular UI: 3D globe, deck.gl map overlays, intelligence panels, threat indicators, timeline, and chat interface.
- **`src/services/`** — Data layer: WebSocket bridges, AIS vessel tracking, signal detection, market analysis, feed health monitoring, and AI provider integrations (Ollama, Groq, OpenRouter).
- **`src/config/`** — Static data: country definitions, entity databases, intelligence feeds, and geo-coordinates.
- **`src/utils/`** — Shared utilities: DOM manipulation, circuit breaker pattern for resilient API calls, and HTML sanitization via DOMPurify.

### Environment Variables

Copy `.env.example` and fill in your keys:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description |
|----------|-------------|
| `VITE_OLLAMA_URL` | Local Ollama endpoint (default: `http://localhost:11434`) |
| `VITE_GROQ_API_KEY` | Groq API key for fast inference |
| `VITE_OPENROUTER_API_KEY` | OpenRouter API key |
| `VITE_DATA_BRIDGE_URL` | Python backend URL (default: `http://localhost:8000`) |
| `VITE_MAPLIBRE_STYLE` | MapLibre tile style URL |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key |

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with HMR on `:5173` |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Preview the production build locally |
| `npm run typecheck` | Run TypeScript type checking (`tsc --noEmit`) |

---

## Security

- ✅ Service role key stored securely (`600` permissions)
- ✅ `.env` file in `.gitignore`
- ⚠️ Consider enabling RLS (Row Level Security) on tables
- ⚠️ Rotate API keys every 90 days

---

## License

Private project for Finn McKie / Atlas OS.

---

**Created:** 2026-03-23  
**Status:** Setup phase  
**By:** Atlas (Subagent)
