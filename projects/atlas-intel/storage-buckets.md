# Atlas Intel - Storage Buckets Configuration

## Overview
Two storage buckets are required for Atlas Intel's multimodal intelligence platform.

---

## Bucket 1: `raw-media`

**Purpose:** Store raw ingested media from all sources

### Configuration
- **Name:** `raw-media`
- **Access:** Public (recommended for easy URL access)
- **File Size Limit:** 50MB (free tier default)
- **Allowed MIME Types:**
  - `video/*` (X videos, CCTV footage)
  - `audio/*` (speeches, announcements, calls)
  - `image/*` (satellite imagery, screenshots)
  - `application/pdf` (documents, reports)

### Directory Structure
```
raw-media/
├── x_videos/           # Twitter/X video clips
├── ais_vessel/         # Vessel tracking data (CSV, images)
├── satellite/          # Satellite imagery
├── cctv/               # CCTV footage
├── news/               # News articles, PDFs
├── audio/              # Speech recordings, calls
└── documents/          # PDFs, reports, transcripts
```

### Sample Upload (Python)
```python
from supabase import create_client
import os

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Upload video
with open('fed_speech.mp4', 'rb') as f:
    supabase.storage.from_('raw-media').upload(
        'audio/fed_speech_2026-03-23.mp4',
        f,
        file_options={"content-type": "video/mp4"}
    )

# Get public URL
url = supabase.storage.from_('raw-media').get_public_url('audio/fed_speech_2026-03-23.mp4')
print(f"Media URL: {url}")
```

---

## Bucket 2: `processed`

**Purpose:** Store processed/derived data (transcripts, embeddings, analysis)

### Configuration
- **Name:** `processed`
- **Access:** Private (internal use only)
- **File Size Limit:** 50MB
- **Allowed MIME Types:**
  - `text/*` (transcripts, extracted text)
  - `application/json` (structured data, metadata)
  - `image/*` (extracted frames, thumbnails)

### Directory Structure
```
processed/
├── transcripts/        # Audio/video transcripts
├── frames/             # Extracted video frames
├── embeddings/         # Exported embedding vectors (backup)
├── reports/            # Generated intelligence reports
└── analysis/           # ML outputs, signal detection results
```

### Sample Upload (Python)
```python
import json

# Store transcript
transcript = {
    "source_id": "1234567890",
    "speaker": "Jerome Powell",
    "text": "The Federal Reserve has decided to...",
    "timestamp": "2026-03-23T10:00:00Z",
    "detected_signals": ["rate cut", "inflation target"]
}

supabase.storage.from_('processed').upload(
    'transcripts/fed_speech_1234567890.json',
    json.dumps(transcript).encode('utf-8'),
    file_options={"content-type": "application/json"}
)
```

---

## Bucket Policies (Optional RLS)

If you want granular access control, create these policies via Supabase dashboard:

### raw-media (Public Read)
```sql
create policy "Public read access"
on storage.objects for select
using ( bucket_id = 'raw-media' );

create policy "Authenticated upload"
on storage.objects for insert
with check ( bucket_id = 'raw-media' and auth.role() = 'authenticated' );
```

### processed (Private)
```sql
create policy "Authenticated full access"
on storage.objects for all
using ( bucket_id = 'processed' and auth.role() = 'authenticated' );
```

---

## File Naming Conventions

### Videos
- Format: `{source_type}_{source_id}_{timestamp}.{ext}`
- Example: `x_video_1234567890_2026-03-23T10-00-00Z.mp4`

### Audio
- Format: `{event_type}_{speaker}_{date}.{ext}`
- Example: `fed_speech_powell_2026-03-23.mp3`

### Transcripts
- Format: `{source_type}_{source_id}.json`
- Example: `x_video_1234567890.json`

### Images
- Format: `{source_type}_{location}_{timestamp}.{ext}`
- Example: `satellite_blacksea_2026-03-23T12-00-00Z.jpg`

---

## Storage Limits (Free Tier)

- **Total Storage:** 1 GB
- **Bandwidth:** 2 GB/month
- **File Size:** 50 MB per file

### Optimization Tips
1. Compress videos before upload (H.264, medium quality)
2. Use thumbnails for preview (store full images only when needed)
3. Delete old raw media after processing (keep only embeddings)
4. Archive to external storage (S3, Google Cloud Storage) for long-term retention

---

## Monitoring Usage

```python
# Check storage usage (requires direct DB query or API)
# Supabase dashboard: Settings → Usage

import requests

url = f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/storage_usage"
headers = {
    "apikey": os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}"
}
response = requests.get(url, headers=headers)
print(response.json())
```

---

**Created:** 2026-03-23  
**By:** Atlas (Subagent)  
**Project:** Atlas Intel
