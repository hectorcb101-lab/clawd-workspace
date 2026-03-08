# Geopolitical Alpha Module

**Teaching-first market intelligence** — Understanding geopolitical events through transmission chains to asset impacts.

---

## What This Does

Transforms geopolitical news into **actionable trading intelligence** by:

1. **Collecting** geopolitical events from multiple categories
2. **Analyzing** transmission chains (Event → Impact → Asset effect)
3. **Teaching** WHY connections exist, not just stating them
4. **Providing** historical parallels to show what happened before
5. **Scoring** conviction (how confident we are in each connection)

## Components

### 1. `collectors/collect_geopolitical_simple.py`
Collects geopolitical events across 5 categories:
- **Military/Conflict**: Wars, escalations, defence spending
- **Trade/Sanctions**: Tariffs, export controls, sanctions
- **Central Bank**: Interest rate decisions, monetary policy
- **Energy Supply**: Oil/gas disruptions, OPEC decisions
- **Political Transitions**: Elections, government changes

**Current Implementation**: Uses curated real-world events  
**TODO**: Replace with live Exa search when mcporter subprocess config is resolved

### 2. `analysis/geopolitical_alpha.py`
The **core brain**. Maps each event to:

#### a) Transmission Chains
Event → which asset classes affected and HOW

Example knowledge base:
```python
'military_conflict': {
    'direct_impacts': [
        {'asset': 'Defence stocks', 'direction': 'up', 'conviction': 'high'},
        {'asset': 'Gold', 'direction': 'up', 'conviction': 'high'},
        {'asset': 'Oil', 'direction': 'up', 'conviction': 'medium'},
        {'asset': 'Local currency', 'direction': 'down', 'conviction': 'high'},
        # ... more
    ],
    'teaching_note': 'WHY this happens...'
}
```

#### b) Second-Order Effects
Non-obvious downstream impacts:
- Rare earth export ban → semiconductors, EVs, defence (not just mining)
- Suez Canal disruption → European energy, Asian export timing (not just shipping)

#### c) Historical Parallels
Matches current events to past events with actual market data:
- **Crimea 2014**: MICEX -15%, Ruble -10%, European gas +30%
- **US-China Trade War 2018-19**: S&P -20%, CNY -10%, Tech -25%
- **Russia-Ukraine 2022**: EU gas +300%, wheat +50%, defence +40%
- **Brexit 2016**: GBP -12%, UK banks -30%, gold +8%
- **Trump Tariffs 2025**: S&P -15%, Dollar volatile, Mexico Peso -12%

#### d) Conviction Scoring
- **HIGH (🟢)**: Direct, well-documented causal link
- **MEDIUM (🟡)**: Historical precedent but context-dependent
- **LOW (🔴)**: Plausible but speculative second/third-order effect

### 3. `synthesis/generate_insights.py` (Enhanced)
New function: `generate_geopolitical_alpha(geo_patterns)`
- Picks top 3 most significant chains
- Formats as teaching moments
- Includes "what to watch for" specifics

### 4. `presentation/format_briefing.py` (Enhanced)
New section: **🎯 GEOPOLITICAL ALPHA**

Replaces generic geopolitics section with:
```
1. [EVENT HEADLINE]
   Chain: Event → Impact1 → Impact2 → Asset effect
   
   Affected Assets:
   ↗️ Asset Name (direction) 🟢
   
   Watch:
   • Specific thing to monitor
   • Another specific signal
   
   Historical echo: [Past event] (year)
   What happened: [lesson from history]
   
   Conviction: 🟢 HIGH (85/100)
   
   *Why this connection exists:* [Teaching explanation]
```

### 5. `daily_briefing.py` (Updated)
Pipeline now includes:
1. Collect market data (existing)
2. **Collect geopolitical events** (new)
3. Analyze market patterns (existing)
4. **Analyze geopolitical alpha** (new)
5. Synthesize insights (enhanced)
6. Format briefing (enhanced)
7. Send to Telegram + Email

---

## How to Use

### Run Standalone Components

```bash
# Test geopolitical collector
cd ~/clawd/intelligence-briefing
python3 collectors/collect_geopolitical_simple.py

# Test transmission chain analysis
python3 analysis/geopolitical_alpha.py

# Run full briefing (includes geopolitical alpha)
python3 daily_briefing.py
```

### Expected Output

**Console:**
```
🌍 GEOPOLITICAL EVENT COLLECTION (Simplified)
✅ Loaded 8 geopolitical events

🎯 GEOPOLITICAL ALPHA ANALYSIS
✅ Generated 8 transmission chains
   High conviction: 6
   Medium conviction: 2
```

**Telegram/Email Briefing:**
```
🎯 GEOPOLITICAL ALPHA

1. Federal Reserve maintains rates at 3.5-3.75%
   Chain: Central Bank Hawkish → Growth stocks down, Banks up
   
   Affected Assets:
   ↗️ Interest rates (up) 🟢
   ↘️ Growth stocks (down) 🟢
   ↗️ Bank stocks (up) 🟡
   
   Watch:
   • Credit tightening → lower capex, hiring
   • Mortgage rates → housing market impact
   
   Historical echo: US-China Trade War (2018)
   What happened: Markets adjust to policy shifts...
   
   Conviction: 🟢 HIGH (100/100)
   
   *Why this connection exists:* Higher rates make borrowing 
   expensive, slowing growth. Growth stocks fall because future 
   profits are worth less when discounted at higher rates...
```

---

## Key Features

### ✅ Teaching-First
Every chain includes WHY the connection exists, not just stating correlations.

### ✅ Historical Context
Shows what actually happened in past similar events with real data.

### ✅ Conviction Transparency
Honest about confidence levels — not all connections are equal.

### ✅ Second-Order Thinking
Goes beyond obvious first-order effects to non-intuitive downstream impacts.

### ✅ Actionable
"Watch" section gives specific things to monitor, not vague warnings.

---

## Current Limitations & TODOs

### 🔧 Data Collection
**Current**: Uses curated real-world events (8 current topics)  
**Issue**: `mcporter call exa.web_search_exa` fails from subprocess (config not found)  
**TODO**: 
- Fix mcporter config accessibility from Python subprocess, OR
- Use native Exa MCP tool when called from main agent context, OR
- Implement direct web scraping of Reuters/Bloomberg/FT RSS feeds

**Full Exa implementation exists** in `collectors/collect_geopolitical.py` — ready to use when mcporter is accessible.

### 🔧 Historical Database
**Current**: 6 major historical events with market data  
**TODO**: Expand to 20-30 events covering more scenarios

### 🔧 Asset Specificity
**Current**: Generic asset classes (e.g., "Defence stocks")  
**TODO**: Map to specific tickers (e.g., "LMT, RTX, BA, NOC")

---

## Architecture Principles

### Modular
Each file is self-contained. Collector → Analyzer → Synthesizer → Presenter → Orchestrator.

### Testable
Every component can run standalone for debugging.

### British English
All user-facing strings use British spelling (behaviour, organisation, etc.).

### Explanatory
Code comments explain WHY, not just WHAT.

### Robust
Graceful degradation — if geopolitical data unavailable, briefing continues without it.

---

## Knowledge Base Structure

The `TRANSMISSION_CHAINS` dictionary in `geopolitical_alpha.py` is the **core knowledge base**:

```python
TRANSMISSION_CHAINS = {
    'event_category': {
        'direct_impacts': [
            {
                'asset': 'Asset name',
                'direction': 'up/down/mixed',
                'magnitude': 'high/medium/low',
                'conviction': 'high/medium/low'
            },
            # ... more assets
        ],
        'second_order': [
            'Non-obvious effect 1',
            'Non-obvious effect 2',
            # ...
        ],
        'teaching_note': 'Explanation of WHY this category affects these assets'
    },
    # ... more categories
}
```

**Current categories:**
1. `military_conflict`
2. `trade_sanctions`
3. `tariffs`
4. `central_bank_hawkish`
5. `central_bank_dovish`
6. `energy_supply_disruption`
7. `political_transition`

**To add more:** Edit `TRANSMISSION_CHAINS` and `HISTORICAL_PARALLELS` in `analysis/geopolitical_alpha.py`.

---

## Example Flow

### Input (Event):
```json
{
  "headline": "Trump tariffs on China, EU, Mexico",
  "category": "trade_sanctions",
  "countries": ["US", "China", "EU", "Mexico"]
}
```

### Analysis Output (Chain):
```json
{
  "event": "Trump tariffs...",
  "event_category": "tariffs",
  "affected_assets": [
    {"asset": "Affected sector margins", "direction": "down", "conviction": "high"},
    {"asset": "Domestic competitors", "direction": "up", "conviction": "medium"},
    {"asset": "Consumer prices", "direction": "up", "conviction": "high"}
  ],
  "second_order": [
    "Retaliatory tariffs → escalation spiral",
    "Supply chain diversification → short-term disruption"
  ],
  "historical_parallel": {
    "event": "Trump Tariffs 2025",
    "what_happened": {"S&P 500": "-15%", "Mexico Peso": "-12%"},
    "lesson": "Modern tariffs hurt importing country consumers..."
  },
  "teaching_note": "Tariffs are taxes on imports...",
  "conviction_score": 85
}
```

### Presentation (Telegram):
```
🎯 GEOPOLITICAL ALPHA

1. Trump tariffs on China, EU, Mexico
   Chain: Tariffs → Sector margins down, Domestic up
   
   Watch:
   • Retaliatory tariffs → escalation spiral
   • Supply chain diversification
   
   Historical echo: Trump Tariffs 2025
   What happened: S&P -15%, Peso -12%
   
   Conviction: 🟢 HIGH (85/100)
```

---

## Maintenance

### Adding New Event Types
1. Add category to collector queries
2. Create transmission chain in `TRANSMISSION_CHAINS`
3. Add historical parallel if available

### Updating Market Impact Data
Edit `HISTORICAL_PARALLELS` with actual market data from reliable sources.

### Tuning Conviction Scoring
Adjust `score_conviction()` function in `geopolitical_alpha.py`.

---

## Success Metrics

This module is working if:
- ✅ Briefing includes 2-3 geopolitical transmission chains
- ✅ Each chain has clear Event → Impact → Asset flow
- ✅ Teaching notes explain WHY (not just WHAT)
- ✅ Historical parallels provide context
- ✅ Conviction scores help prioritise attention
- ✅ No errors in pipeline (graceful degradation if no events)

---

## Credits

Built: 2026-02-16  
Purpose: Transform geopolitical news into actionable market intelligence with teaching-first explanations  
Philosophy: Understanding > Correlation. Context > Headlines. Education > Alerts.
