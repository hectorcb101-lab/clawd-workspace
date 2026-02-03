# Prediction Market Arbitrage Bot - Architecture

## Overview

Automated arbitrage between **Polymarket** (via Jupiter on Solana) and **Kalshi** (direct API).

**Capital:** $50 initial  
**Mode:** Full auto-execution  
**User:** Finn McKie

---

## Data Sources

### Jupiter Prediction API (Polymarket on Solana)
- **Base URL:** `https://prediction-market-api.jup.ag`
- **Status:** Beta (announced 2026-02-02)
- **Auth:** API key via https://portal.jup.ag
- **Key Endpoints:**
  - `GET /api/v1/events` — List all events
  - `GET /api/v1/events/search?query=` — Search events
  - `GET /api/v1/events/{eventId}/markets` — Get markets for event
  - `GET /api/v1/markets/{marketId}` — Market details + pricing
  - `POST /api/v1/orders` — Create order (returns unsigned tx)
  - `GET /api/v1/orderbook/{marketId}` — Order book depth
  - `GET /api/v1/trading-status` — Exchange status

**Execution Flow:**
1. Call API to get unsigned transaction
2. Sign with Solana wallet (Phantom keypair)
3. Submit signed transaction to Solana RPC

### Kalshi API
- **Base URL:** `https://trading-api.kalshi.com/trade-api/v2`
- **Demo URL:** `https://demo-api.kalshi.co/trade-api/v2`
- **Auth:** API key + secret (HMAC signature)
- **Python SDK:** `pip install kalshi-python`
- **Key Endpoints:**
  - `GET /events` — List events
  - `GET /markets` — List markets
  - `GET /markets/{ticker}` — Market details
  - `GET /markets/{ticker}/orderbook` — Order book
  - `POST /portfolio/orders` — Place order
  - `GET /portfolio/positions` — Current positions

---

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARBITRAGE ENGINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Jupiter    │    │    Event     │    │    Kalshi    │      │
│  │   Fetcher    │───▶│   Matcher    │◀───│   Fetcher    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────┐                             │
│                    │  Opportunity │                             │
│                    │   Detector   │                             │
│                    └──────────────┘                             │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────┐                             │
│                    │  Checklist   │                             │
│                    │  Validator   │                             │
│                    └──────────────┘                             │
│                             │                                   │
│                             ▼                                   │
│         ┌──────────────────┴──────────────────┐                │
│         ▼                                      ▼                │
│  ┌──────────────┐                      ┌──────────────┐        │
│  │   Jupiter    │                      │    Kalshi    │        │
│  │   Executor   │                      │   Executor   │        │
│  └──────────────┘                      └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │   Position   │
                    │   Tracker    │
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │  Settlement  │
                    │   Monitor    │
                    └──────────────┘
```

---

## Event Matching Algorithm

Events across platforms won't have identical names. Need semantic matching:

```python
def match_events(jupiter_events, kalshi_events):
    matches = []
    for j_event in jupiter_events:
        for k_event in kalshi_events:
            # Extract key attributes
            j_title = normalize(j_event['title'])
            k_title = normalize(k_event['title'])
            
            # Check resolution date match (must be same)
            if j_event['end_date'] != k_event['close_time']:
                continue
            
            # Semantic similarity (embeddings or fuzzy match)
            similarity = compare(j_title, k_title)
            if similarity > 0.85:
                matches.append({
                    'jupiter': j_event,
                    'kalshi': k_event,
                    'confidence': similarity
                })
    
    return matches
```

**Matching criteria:**
1. Resolution date must match exactly
2. Event type/category should align
3. Title similarity > 85%
4. Manual review for edge cases initially

---

## Arbitrage Detection

```python
def detect_arbitrage(jupiter_market, kalshi_market):
    # Get best prices from order books
    j_yes_ask = jupiter_market['orderbook']['yes']['best_ask']
    j_no_ask = jupiter_market['orderbook']['no']['best_ask']
    k_yes_ask = kalshi_market['orderbook']['yes']['best_ask']
    k_no_ask = kalshi_market['orderbook']['no']['best_ask']
    
    # Check for arb: YES on one + NO on other < $1
    arb1 = j_yes_ask + k_no_ask  # YES Jupiter, NO Kalshi
    arb2 = k_yes_ask + j_no_ask  # YES Kalshi, NO Jupiter
    
    opportunities = []
    
    if arb1 < 1.0:
        gross_profit = 1.0 - arb1
        opportunities.append({
            'type': 'jupiter_yes_kalshi_no',
            'gross_profit_pct': gross_profit * 100,
            'jupiter_side': 'YES',
            'jupiter_price': j_yes_ask,
            'kalshi_side': 'NO',
            'kalshi_price': k_no_ask
        })
    
    if arb2 < 1.0:
        gross_profit = 1.0 - arb2
        opportunities.append({
            'type': 'kalshi_yes_jupiter_no',
            'gross_profit_pct': gross_profit * 100,
            'kalshi_side': 'YES',
            'kalshi_price': k_yes_ask,
            'jupiter_side': 'NO',
            'jupiter_price': j_no_ask
        })
    
    return opportunities
```

---

## Fee Structure

### Jupiter/Polymarket (via Solana)
- Trading fee: ~1% (estimate, verify)
- Solana transaction fee: ~0.000005 SOL (~$0.001)
- No withdrawal fee (native Solana)

### Kalshi
- Trading fee: $0.01-0.07 per contract (varies by market)
- No deposit/withdrawal fees for ACH
- Wire transfer: $25 withdrawal fee

### Net Profit Calculation
```python
def calculate_net_profit(opportunity, position_size):
    gross_profit = opportunity['gross_profit_pct'] / 100 * position_size
    
    # Fees
    jupiter_fee = position_size * 0.01  # 1% estimate
    kalshi_fee = (position_size / opportunity['kalshi_price']) * 0.03  # ~$0.03 avg
    solana_tx_fee = 0.002  # ~2 transactions
    
    total_fees = jupiter_fee + kalshi_fee + solana_tx_fee
    net_profit = gross_profit - total_fees
    
    return {
        'gross': gross_profit,
        'fees': total_fees,
        'net': net_profit,
        'net_pct': (net_profit / position_size) * 100
    }
```

---

## Risk Controls

### Position Limits
```python
MAX_POSITION_SIZE = 50  # Total capital
MAX_SINGLE_TRADE = 25   # Max per opportunity
MAX_OPEN_POSITIONS = 3  # Concurrent arbs
MIN_NET_PROFIT_PCT = 2.0  # Minimum edge after fees
```

### Execution Safety
1. **Atomic execution check:** If first leg fails, don't execute second
2. **Slippage buffer:** 0.2% cushion on fill prices
3. **Liquidity check:** Verify order book depth before execution
4. **Time guards:** Don't trade within 1h of resolution (liquidity dries up)

### Platform Health
- Check `trading-status` endpoints before trades
- Monitor for exchange announcements
- Pause on any API errors

---

## Execution Flow

```python
async def execute_arbitrage(opportunity, position_size):
    # 1. Pre-flight checks
    assert position_size <= MAX_SINGLE_TRADE
    assert opportunity['net_profit_pct'] >= MIN_NET_PROFIT_PCT
    assert check_liquidity(opportunity, position_size)
    
    # 2. Execute less liquid leg first (usually Jupiter)
    jupiter_order = await jupiter_executor.place_order(
        market_id=opportunity['jupiter_market_id'],
        side=opportunity['jupiter_side'],
        amount=position_size / opportunity['jupiter_price'],
        slippage=0.02
    )
    
    if not jupiter_order.filled:
        log_error("Jupiter leg failed, aborting")
        return None
    
    # 3. Execute second leg immediately
    kalshi_order = await kalshi_executor.place_order(
        ticker=opportunity['kalshi_ticker'],
        side=opportunity['kalshi_side'],
        contracts=int(position_size / opportunity['kalshi_price']),
        type='market'
    )
    
    if not kalshi_order.filled:
        log_error("CRITICAL: Kalshi leg failed, need manual intervention")
        alert_finn("Arbitrage leg 2 failed - manual action needed")
        return None
    
    # 4. Record position
    position = create_position(
        jupiter_order=jupiter_order,
        kalshi_order=kalshi_order,
        expected_profit=opportunity['net_profit']
    )
    
    return position
```

---

## Monitoring & Alerts

### Real-time Monitoring
- Position P&L tracking
- Platform health status
- Upcoming resolutions

### Alert Triggers (→ Telegram)
- New opportunity found (above threshold)
- Trade executed (with details)
- Resolution approaching (<24h)
- Error/failure conditions
- Position settled

---

## File Structure

```
projects/prediction-arb/
├── ARCHITECTURE.md          # This file
├── PROJECT.md               # Status and progress
├── config/
│   ├── settings.yaml        # Thresholds, limits
│   └── credentials.yaml     # API keys (gitignored)
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── fetchers/
│   │   ├── jupiter.py       # Jupiter API client
│   │   └── kalshi.py        # Kalshi API client
│   ├── matching/
│   │   └── event_matcher.py # Semantic event matching
│   ├── detection/
│   │   └── arbitrage.py     # Opportunity detection
│   ├── execution/
│   │   ├── jupiter_exec.py  # Solana transaction signing
│   │   └── kalshi_exec.py   # Kalshi order placement
│   ├── monitoring/
│   │   ├── positions.py     # Position tracking
│   │   └── alerts.py        # Telegram notifications
│   └── utils/
│       ├── checklist.py     # Full checklist validation
│       └── logging.py       # Structured logging
├── data/
│   ├── matched_events.json  # Cached event matches
│   └── positions.json       # Open/closed positions
└── tests/
    └── ...
```

---

## Development Phases

### Phase 1: Data Pipeline (Day 1-2)
- [ ] Jupiter API client + event fetching
- [ ] Kalshi API client + event fetching
- [ ] Event matching algorithm
- [ ] Basic opportunity detection

### Phase 2: Execution (Day 3-4)
- [ ] Solana wallet integration (sign transactions)
- [ ] Kalshi order placement
- [ ] Atomic execution with rollback handling
- [ ] Position tracking

### Phase 3: Monitoring (Day 5)
- [ ] Telegram alerts
- [ ] Position P&L dashboard
- [ ] Resolution monitoring

### Phase 4: Go Live (Day 6+)
- [ ] Paper trading validation
- [ ] $50 live deployment
- [ ] Monitor and tune thresholds

---

## Required Credentials

From Finn:
1. **Solana wallet keypair** (JSON file or base58 private key)
2. **Kalshi API credentials** (from https://kalshi.com/account/api)
3. **Jupiter API key** (from https://portal.jup.ag) — may not be required for beta

---

## Known Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Resolution ambiguity | Medium | High | Manual review of matched events |
| API rate limiting | Low | Medium | Backoff + caching |
| Execution slippage | Medium | Low | Slippage buffer, liquidity check |
| Platform downtime | Low | High | Health checks, pause on errors |
| Leg 2 failure | Low | Critical | Alert + manual intervention |

---

## Notes

- Jupiter Prediction API just launched (Feb 2, 2026) — expect bugs
- Geographic restrictions: Jupiter Predictions not available in US
- Start with high-confidence event matches only
- Log everything for post-mortem analysis
