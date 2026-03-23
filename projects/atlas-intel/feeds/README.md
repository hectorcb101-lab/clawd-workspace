# Atlas Intel Feed Monitors

Event-driven intelligence feeds that monitor global events, economic indicators, and corporate signals.

## Feed Scripts

### 1. GDELT Global Event Monitor
**File:** `gdelt_monitor.py`

Monitors GDELT API for significant geopolitical events:
- Military movements, sanctions, trade disputes
- Energy events (oil, natural gas, nuclear)
- Political instability (protests, coups, terrorism)
- Economic crises

**Configuration:**
- **Tracked themes:** MILITARY, SANCTIONS, TRADE_DISPUTE, OIL, NATURAL_GAS, NUCLEAR, PROTEST, COUP, TERROR, ECON_CRISIS
- **Goldstein threshold:** |5.0| (high-impact events only)
- **Poll interval:** 15 minutes
- **Output:** `logs/gdelt_events.jsonl`
- **Process log:** `logs/gdelt_monitor.log`

**Usage:**
```bash
cd /home/ubuntu/clawd/projects/atlas-intel
source .venv/bin/activate
python feeds/gdelt_monitor.py
```

**API:** https://api.gdeltproject.org/api/v2/doc/doc

---

### 2. Economic Feeds Monitor
**File:** `economic_feeds.py`

Tracks economic indicators and corporate events:

1. **Shipping Rates**
   - Baltic Dry Index (BDI) - global trade indicator
   - Freightos Baltic Index (FBX) - container shipping
   - Sources: Trading Economics (web scraping), Yahoo Finance

2. **SEC 8-K Filings**
   - Material corporate events (8-K filings)
   - Tracks 24 major S&P 100 companies
   - Full-text search via SEC EDGAR API

**Configuration:**
- **Poll interval:** Daily (24 hours)
- **Output:** `logs/economic_events.jsonl`
- **Process log:** `logs/economic_feeds.log`

**Usage:**
```bash
cd /home/ubuntu/clawd/projects/atlas-intel
source .venv/bin/activate
python feeds/economic_feeds.py
```

**APIs:**
- SEC EDGAR: https://efts.sec.gov/LATEST/search-index
- Trading Economics: https://tradingeconomics.com/commodity/baltic
- Yahoo Finance: via `yfinance` library

---

## Data Pipeline

All feeds follow the same pipeline:

1. **Fetch** data from external APIs/sources
2. **Filter** for significance (Goldstein scale, materiality)
3. **Embed** content using Gemini embedding model (3072-dim)
4. **Store** in Supabase vector DB with metadata
5. **Log** events to JSONL for audit trail

**Storage Schema:**
- `source_type`: 'gdelt_event', 'economic_indicator', 'sec_filing'
- `content_text`: Full text description
- `metadata`: JSON with event details
- `embedding`: 3072-dim vector for similarity search
- `source_id`: Unique identifier (URL, accession number, etc.)

---

## Embedding & Storage

Both feeds use the shared `atlas_intel` infrastructure:

```python
from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding

# Generate embedding
embedding = embed_text(content_text)

# Store with metadata
result = store_embedding(
    source_type="gdelt_event",  # or "economic_indicator", "sec_filing"
    content=content_text,
    metadata={"key": "value"},
    embedding=embedding,
    source_id="unique_id",
)
```

---

## Deployment

### Background Services (systemd)

Create service files for continuous monitoring:

**GDELT Monitor:**
```bash
sudo tee /etc/systemd/system/atlas-gdelt-monitor.service << EOF
[Unit]
Description=Atlas Intel GDELT Event Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clawd/projects/atlas-intel
ExecStart=/home/ubuntu/clawd/projects/atlas-intel/.venv/bin/python feeds/gdelt_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable atlas-gdelt-monitor
sudo systemctl start atlas-gdelt-monitor
```

**Economic Feeds:**
```bash
sudo tee /etc/systemd/system/atlas-economic-feeds.service << EOF
[Unit]
Description=Atlas Intel Economic Feeds Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clawd/projects/atlas-intel
ExecStart=/home/ubuntu/clawd/projects/atlas-intel/.venv/bin/python feeds/economic_feeds.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable atlas-economic-feeds
sudo systemctl start atlas-economic-feeds
```

### Manual Testing

Test single poll cycle without entering infinite loop:

```python
from feeds.gdelt_monitor import poll_gdelt
events_found = poll_gdelt()
print(f"Found {events_found} significant events")
```

```python
from feeds.economic_feeds import poll_economic_feeds
events_found = poll_economic_feeds()
print(f"Stored {events_found} economic indicators")
```

---

## Dependencies

Installed in `.venv`:
- `requests` - HTTP client
- `yfinance` - Yahoo Finance API
- `google-generativeai` - Gemini embeddings
- `supabase` - Vector storage
- `numpy` - Array operations

---

## Rate Limits & Considerations

**GDELT API:**
- Rate limit: ~10 requests/minute
- Timeout: 30 seconds
- Retry: Built-in error handling

**SEC EDGAR:**
- Rate limit: 10 requests/second
- User-Agent required
- Delay between company queries: 150ms

**Trading Economics:**
- Web scraping (no official API)
- May change HTML structure
- Fallback to Yahoo Finance

---

## Logs & Monitoring

**Process logs:**
- `logs/gdelt_monitor.log` - GDELT polling activity
- `logs/economic_feeds.log` - Economic feeds activity

**Event logs (JSONL):**
- `logs/gdelt_events.jsonl` - Stored GDELT events
- `logs/economic_events.jsonl` - Stored economic indicators

**Log rotation:** Recommended via logrotate for long-running deployments.

---

## Future Enhancements

- [ ] GDELT GEO API integration for geographic event mapping
- [ ] Freightos Baltic Index (FBX) API integration
- [ ] Earnings call transcript NLP (beyond 8-K filings)
- [ ] Real-time signal correlation with market data
- [ ] Alert webhooks for critical events
- [ ] Historical backfill for trend analysis
