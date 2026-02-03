# Prediction Market Arbitrage Bot

## Status: ⏸️ Paused

**Started:** 2026-02-02  
**Owner:** Atlas (for Finn)  
**Capital:** $50  
**Mode:** Auto-execution

---

## Quick Summary

Automated arbitrage bot that:
1. Monitors Polymarket (via Jupiter/Solana) and Kalshi
2. Matches identical events across platforms
3. Detects price discrepancies (arb opportunities)
4. Auto-executes when profit threshold met
5. Tracks positions through resolution

---

## Progress

- [x] Research Jupiter-Polymarket integration
- [x] Research Kalshi API
- [x] Draft architecture
- [x] Got Jupiter API key from Finn
- [ ] Choose second platform (not Kalshi - US only)
- [ ] Get credentials for second platform
- [ ] Get Solana wallet keypair from Finn
- [ ] Build Jupiter API client
- [ ] Build second platform API client
- [ ] Implement event matcher
- [ ] Implement arbitrage detector
- [ ] Implement executors
- [ ] Paper trading test
- [ ] Go live with $50

---

## Blockers

**Need to resolve:**
1. **Second platform choice** — Kalshi is US-only, Finn can't sign up
   - Options: Smarkets (UK), Betfair, or Drift Protocol (Solana)
2. Solana wallet keypair (dedicated wallet for arb)
3. Second platform API credentials

**Have:**
- Jupiter API key: ✅ stored in `config/credentials.yaml`

---

## Key Finding

Jupiter announced Polymarket integration **today** (Feb 2, 2026). API is in beta. This is bleeding edge — expect some rough edges but also less competition for arb opportunities.

---

## Next Actions

1. Finn provides wallet + Kalshi creds
2. Atlas builds data pipeline (fetchers + matcher)
3. Validate with paper trading
4. Deploy with real capital

---

## Links

- [Jupiter Prediction API Docs](https://dev.jup.ag/api-reference/prediction)
- [Kalshi API Docs](https://docs.kalshi.com/)
- [Architecture](./ARCHITECTURE.md)
