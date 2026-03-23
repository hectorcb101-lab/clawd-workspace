-- Atlas Intel Database Schema
-- Multimodal Intelligence Platform
-- Created: 2026-03-23

-- Enable pgvector extension for embeddings
create extension if not exists vector;

-- Core embeddings table (multimodal)
-- Stores embeddings from various sources: videos, vessels, satellite imagery, CCTV, news, audio, documents
create table embeddings (
  id uuid primary key default gen_random_uuid(),
  source_type text not null, -- 'x_video', 'ais_vessel', 'satellite', 'cctv', 'news', 'audio', 'document'
  source_id text, -- external ID (tweet ID, vessel MMSI, etc.)
  content_text text, -- optional text representation
  media_url text, -- URL to raw media in Supabase Storage
  embedding vector(3072), -- Gemini embedding-exp dimensions
  metadata jsonb default '{}', -- flexible metadata (timestamps, geo coords, vessel info, etc.)
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Signal phrases extracted from speeches/announcements
-- Tracks important market-moving statements and their context
create table signal_phrases (
  id uuid primary key default gen_random_uuid(),
  phrase text not null,
  source_embedding_id uuid references embeddings(id),
  context text, -- surrounding context
  speaker text, -- who said it
  event_type text, -- 'fed_speech', 'press_conference', 'earnings_call', 'political'
  detected_at timestamptz not null,
  market_reaction jsonb, -- { asset: 'SPY', change_pct: -1.2, timeframe: '1h' }
  sentiment_score float, -- -1 (bearish) to 1 (bullish)
  created_at timestamptz default now()
);

-- Market reactions linked to signals (for ML training)
-- Captures price movements following signal detection
create table market_reactions (
  id uuid primary key default gen_random_uuid(),
  signal_phrase_id uuid references signal_phrases(id),
  asset text not null, -- 'SPY', 'BTC', 'OIL', etc.
  price_before float,
  price_after float,
  change_pct float,
  timeframe text, -- '1h', '4h', '1d'
  measured_at timestamptz,
  created_at timestamptz default now()
);

-- Feed sources and their health
-- Monitors status and reliability of data sources
create table feed_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  feed_type text not null, -- 'x_api', 'ais_stream', 'satellite', 'cctv', 'news'
  config jsonb default '{}',
  last_poll_at timestamptz,
  status text default 'active',
  error_count int default 0,
  created_at timestamptz default now()
);

-- Indexes for performance
create index idx_embeddings_source on embeddings(source_type);
-- Note: pgvector indexes limited to 2000 dims on Supabase free tier
-- Vector search still works without index (sequential scan), index added when we scale
-- create index idx_embeddings_vector on embeddings using hnsw (embedding vector_cosine_ops);
create index idx_signals_event on signal_phrases(event_type);
create index idx_signals_sentiment on signal_phrases(sentiment_score);
create index idx_reactions_asset on market_reactions(asset);

-- Optional: Add RLS policies (uncomment if needed)
-- alter table embeddings enable row level security;
-- alter table signal_phrases enable row level security;
-- alter table market_reactions enable row level security;
-- alter table feed_sources enable row level security;
