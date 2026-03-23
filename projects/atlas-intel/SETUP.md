# Atlas Intel - Supabase Setup Guide

## Project Overview
Atlas Intel is a multimodal intelligence platform that processes and embeds data from multiple sources (X/Twitter videos, AIS vessel tracking, satellite imagery, CCTV, news, audio, documents) for market signal detection and analysis.

---

## Step 1: Create Supabase Project

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Sign in (or create account) using **hectorcb101@gmail.com** (Atlas's Google account)
3. Click **"New project"**
4. Fill in the details:
   - **Name:** `atlas-intel`
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose closest to your primary location (e.g., `eu-west-2` for UK)
   - **Pricing Plan:** **Free** (includes 500MB database, 1GB storage, 2GB bandwidth)
5. Click **"Create new project"** and wait ~2 minutes for provisioning

---

## Step 2: Run Database Schema

1. In your Supabase project dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy the entire contents of `schema.sql` (in this directory)
4. Paste into the SQL Editor
5. Click **"Run"** (or press `Ctrl+Enter`)
6. Verify all tables and indexes were created:
   - `embeddings`
   - `signal_phrases`
   - `market_reactions`
   - `feed_sources`

**Expected output:** Success messages for each CREATE statement

---

## Step 3: Create Storage Buckets

1. In Supabase dashboard, go to **Storage** (left sidebar)
2. Click **"Create a new bucket"**

### Bucket 1: raw-media
- **Name:** `raw-media`
- **Public bucket:** ✅ (if you need public URLs for media)
- **File size limit:** Default (50MB)
- **Allowed MIME types:** Leave empty (allow all) or specify: `video/*`, `audio/*`, `image/*`, `application/pdf`
- Click **"Create bucket"**

### Bucket 2: processed
- **Name:** `processed`
- **Public bucket:** ❌ (keep private)
- **File size limit:** Default
- **Allowed MIME types:** Leave empty or specify: `text/*`, `application/json`, `image/*`
- Click **"Create bucket"**

---

## Step 4: Retrieve API Credentials

1. In Supabase dashboard, go to **Settings** → **API** (left sidebar)
2. You'll see:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **API Keys:**
     - `anon` `public` — safe for client-side use
     - `service_role` `secret` — **NEVER expose publicly**

3. Copy all three values

---

## Step 5: Save Credentials

Run this command on your server (replace with actual values):

```bash
cat > /home/ubuntu/clawd/config/supabase-atlas-intel.env << 'EOF'
# Supabase Atlas Intel Credentials
# Created: 2026-03-23
# NEVER commit this file to git!

SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database direct connection (optional, for advanced use)
# SUPABASE_DB_URL=postgresql://postgres:[YOUR_PASSWORD]@db.YOUR_PROJECT_ID.supabase.co:5432/postgres
EOF

chmod 600 /home/ubuntu/clawd/config/supabase-atlas-intel.env
```

---

## Step 6: Verify Installation

```bash
# Check Python client is installed
python3 -c "import supabase; print('Supabase client installed:', supabase.__version__)"

# Test connection (replace with your actual URL and key)
python3 << 'PYTEST'
import os
from supabase import create_client

# Load credentials
url = "YOUR_SUPABASE_URL"
key = "YOUR_ANON_KEY"

supabase = create_client(url, key)

# Test query
result = supabase.table('feed_sources').select("*").limit(1).execute()
print("✅ Connection successful!")
print(f"Tables accessible: {result}")
PYTEST
```

---

## Usage Examples

### Python Client

```python
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/ubuntu/clawd/config/supabase-atlas-intel.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service_role for backend

supabase = create_client(url, key)

# Insert an embedding
data = supabase.table('embeddings').insert({
    "source_type": "x_video",
    "source_id": "1234567890",
    "content_text": "Fed announces rate cut",
    "media_url": "https://...",
    "embedding": [0.1, 0.2, ...],  # 3072 dimensions
    "metadata": {
        "author": "@finlay_mckie",
        "timestamp": "2026-03-23T10:00:00Z",
        "geo": {"lat": 51.5, "lon": -0.1}
    }
}).execute()

# Search by similarity (requires pgvector)
from supabase.lib.client_options import ClientOptions

# Vector search example
query_embedding = [0.15, 0.22, ...]  # Your query vector
results = supabase.rpc('match_embeddings', {
    'query_embedding': query_embedding,
    'match_threshold': 0.8,
    'match_count': 10
}).execute()

# Upload to storage
with open('video.mp4', 'rb') as f:
    supabase.storage.from_('raw-media').upload('x_videos/video123.mp4', f)
```

### Vector Search Function (Optional)

If you want semantic search, add this function via SQL Editor:

```sql
create or replace function match_embeddings (
  query_embedding vector(3072),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  source_type text,
  content_text text,
  similarity float
)
language sql stable
as $$
  select
    embeddings.id,
    embeddings.source_type,
    embeddings.content_text,
    1 - (embeddings.embedding <=> query_embedding) as similarity
  from embeddings
  where 1 - (embeddings.embedding <=> query_embedding) > match_threshold
  order by embeddings.embedding <=> query_embedding
  limit match_count;
$$;
```

---

## Security Checklist

- ✅ `service_role` key saved to `/home/ubuntu/clawd/config/supabase-atlas-intel.env` (600 permissions)
- ✅ `config/supabase-atlas-intel.env` added to `.gitignore`
- ✅ Never use `service_role` key in client-side code
- ✅ Consider enabling Row Level Security (RLS) on tables if multi-tenant
- ✅ Regularly rotate API keys (every 90 days recommended)

---

## Free Tier Limits

- **Database:** 500 MB
- **Storage:** 1 GB
- **Bandwidth:** 2 GB/month
- **Edge Functions:** 500K invocations/month
- **Realtime:** 200 concurrent connections

Monitor usage in **Settings** → **Billing**

---

## Troubleshooting

### "extension vector does not exist"
- pgvector should be enabled by default on Supabase
- If not, contact Supabase support

### "permission denied for schema public"
- Check you're using correct API key
- Service role has full access, anon key respects RLS

### Storage upload fails
- Check bucket exists and is correctly named
- Verify file size under 50MB (free tier limit)
- Check MIME type restrictions on bucket

---

## Next Steps

1. Build ingestion pipelines for each source type (X, AIS, satellite, etc.)
2. Integrate Gemini embedding API for vector generation
3. Set up signal detection logic (NLP on speeches/announcements)
4. Build market reaction tracking system
5. Create dashboards/API for intelligence queries

---

**Setup completed:** [Date]  
**By:** Atlas (Subagent)  
**Project:** Atlas Intel - Multimodal Intelligence Platform
