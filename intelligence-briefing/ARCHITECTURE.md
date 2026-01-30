# Intelligence Briefing System - Architecture

**Status:** 🏗️ Building MVP
**Started:** 2026-01-25 22:24 UTC

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DAILY BRIEFING SYSTEM                    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │   CRON JOB      │
                    │   7 AM London   │
                    └─────────────────┘
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│                  DATA COLLECTION LAYER                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Polymarket  │  │Yahoo Finance │  │  X/Twitter   │    │
│  │  (trends)    │  │(prices, VIX) │  │  (via bird)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  Exa Search  │  │  Web Fetch   │                       │
│  │ (deep news)  │  │  (articles)  │                       │
│  └──────────────┘  └──────────────┘                       │
└────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  • Normalize data formats                                  │
│  • Calculate price changes (%)                             │
│  • Detect anomalies (>2% moves)                            │
│  • Timestamp all events                                    │
│  • Store in JSON (daily cache)                             │
└────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│                  PATTERN RECOGNITION ENGINE                 │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Correlation Detection:                                    │
│  • Price movements across assets                           │
│  • Polymarket odds changes → Market reactions              │
│  • X trends → Price movements (lag analysis)               │
│                                                             │
│  Anomaly Detection:                                        │
│  • Outlier price movements                                 │
│  • Unusual volume spikes                                   │
│  • Sentiment shifts                                        │
│                                                             │
│  Confidence Scoring:                                       │
│  • High: Multiple sources confirm pattern                  │
│  • Moderate: Plausible correlation                         │
│  • Low: Weak signal, watching                              │
└────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│                  SYNTHESIS ENGINE                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  • Connect dots across sources                             │
│  • Build narrative (what → why → so what)                  │
│  • Generate insights (not just facts)                      │
│  • Form opinions with reasoning                            │
│  • Educational content (teach concepts)                    │
└────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Format for Telegram:                                      │
│  • Executive summary (3-5 bullets)                         │
│  • Market movements (with context)                         │
│  • Geopolitical events                                     │
│  • Pattern recognition section                             │
│  • Atlas's analysis                                      │
│  • What to watch today                                     │
└────────────────────────────────────────────────────────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │  Send to Finn   │
                    │   via Telegram  │
                    └─────────────────┘
```

## Component Details

### 1. Data Collection Module
**File:** `intelligence-briefing/collectors/collect_data.py`

**Functions:**
- `collect_polymarket_data()` → Trending markets, odds changes
- `collect_finance_data()` → Major indices, crypto, VIX
- `collect_twitter_data()` → Trending topics (placeholder - needs bird skill integration)
- `collect_news_data()` → Deep search via Exa

**Output:** JSON file with timestamped data

### 2. Processing Module
**File:** `intelligence-briefing/processing/process_data.py`

**Functions:**
- `normalize_data(raw_data)` → Consistent format
- `calculate_changes(current, previous)` → % changes
- `detect_anomalies(data)` → Outliers, significant moves
- `store_cache(data)` → Save for historical comparison

### 3. Pattern Recognition Module
**File:** `intelligence-briefing/analysis/patterns.py`

**Functions:**
- `find_correlations(data)` → Cross-asset patterns
- `analyze_sentiment_impact()` → Polymarket/X → Markets
- `detect_leading_indicators()` → What predicts what?
- `assign_confidence(pattern)` → High/Moderate/Low

### 4. Synthesis Module
**File:** `intelligence-briefing/synthesis/generate_insights.py`

**Functions:**
- `build_narrative(patterns, data)` → Story from data
- `generate_executive_summary()` → Top 3-5 points
- `explain_causality(pattern)` → Why did this happen?
- `form_opinion(data)` → Atlas's take
- `create_educational_content()` → Teach one concept

### 5. Presentation Module
**File:** `intelligence-briefing/presentation/format_briefing.py`

**Functions:**
- `format_for_telegram(insights)` → Markdown formatting
- `add_emojis()` → Visual clarity
- `create_sections()` → Structured output
- `validate_length()` → Not too long

### 6. Main Orchestrator
**File:** `intelligence-briefing/daily_briefing.py`

**Main flow:**
```python
def generate_daily_briefing():
    # 1. Collect data
    raw_data = collect_all_data()
    
    # 2. Process
    processed = process_data(raw_data)
    
    # 3. Find patterns
    patterns = analyze_patterns(processed)
    
    # 4. Generate insights
    insights = synthesize_insights(patterns, processed)
    
    # 5. Format
    briefing = format_briefing(insights)
    
    # 6. Send
    send_to_telegram(briefing)
    
    # 7. Save for history
    save_to_archive(processed, insights)
```

## Data Storage

```
intelligence-briefing/
├── data/
│   ├── cache/
│   │   └── daily_cache.json       # Today's raw data
│   ├── history/
│   │   └── YYYY-MM-DD.json        # Historical data
│   └── patterns/
│       └── learned_patterns.json   # Discovered patterns
├── collectors/
├── processing/
├── analysis/
├── synthesis/
├── presentation/
└── daily_briefing.py
```

## Error Handling

**Graceful Degradation:**
- If Polymarket fails → Use other sources, note in briefing
- If Yahoo Finance fails → Use cached data, mark as stale
- If X/Twitter unavailable → Focus on market data
- If Exa fails → Use direct web fetch

**Fallback:**
- Always generate something (even if limited)
- Clearly state what data sources are available
- Never fail silently

## Automation

**Cron Schedule:**
```bash
# Daily briefing: 7:00 AM London time (GMT/BST aware)
0 7 * * * /path/to/daily_briefing.py

# Weekly deep-dive: Sunday 8:00 AM
0 8 * * 0 /path/to/weekly_briefing.py
```

**Using Clawdbot cron:**
```bash
clawdbot cron add \
  --schedule "0 7 * * *" \
  --timezone "Europe/London" \
  --task "Generate and send daily intelligence briefing" \
  --contextMessages 0
```

## Quality Metrics (Self-Improvement)

**Track:**
- Which patterns Finn reacts to (message responses)
- Which sections he reads (engagement time if available)
- Prediction accuracy (did our patterns hold?)
- Feedback (explicit or implicit)

**Adapt:**
- Emphasize topics Finn engages with
- Reduce noise on ignored patterns
- Improve prediction models
- Refine confidence scoring

## MVP Scope (Tomorrow Morning)

**Must Have:**
- ✅ Collect Polymarket trending data
- ✅ Collect Yahoo Finance data (indices, BTC, major stocks)
- ✅ Detect significant price movements (>2%)
- ✅ Basic pattern recognition (cross-asset correlations)
- ✅ Simple narrative generation
- ✅ Telegram formatting
- ✅ Send to Finn

**Nice to Have (Later):**
- X/Twitter integration (needs bird skill work)
- Deep Exa research on major events
- Advanced ML pattern recognition
- Historical comparison graphs
- Sentiment analysis

## Timeline

- **22:30 UTC:** Build data collectors
- **23:00 UTC:** Build processing pipeline
- **23:30 UTC:** Build pattern recognition
- **00:00 UTC:** Build synthesis
- **00:30 UTC:** Test MVP
- **01:00 UTC:** Deploy cron job
- **07:00 UTC (Next Day):** First briefing sent

---

**Status: Architecture complete. Now building collectors...**
