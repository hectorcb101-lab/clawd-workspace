#!/usr/bin/env python3
"""
Polymarket Arbitrage & Edge Scanner
Finds opportunities based on the TRADING_MASTERY framework
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import sys

GAMMA_API = "https://gamma-api.polymarket.com"

def get_markets(limit: int = 100, active: bool = True) -> List[Dict]:
    """Fetch active markets from Polymarket"""
    params = {
        "limit": limit,
        "active": str(active).lower(),
        "closed": "false"
    }
    try:
        resp = requests.get(f"{GAMMA_API}/markets", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching markets: {e}", file=sys.stderr)
        return []

def get_event_markets(slug: str) -> Optional[Dict]:
    """Get all markets for a specific event"""
    try:
        resp = requests.get(f"{GAMMA_API}/events/{slug}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching event {slug}: {e}", file=sys.stderr)
        return None

def find_same_market_arbitrage(markets: List[Dict]) -> List[Dict]:
    """
    Find markets where YES + NO < 1.00 (guaranteed profit)
    This is the simplest arbitrage - buy both sides for less than $1
    """
    opportunities = []
    
    for market in markets:
        try:
            # Get YES and NO prices
            outcomes = market.get('outcomes', [])
            outcome_prices = market.get('outcomePrices', [])
            
            if len(outcome_prices) >= 2:
                yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
                no_price = float(outcome_prices[1]) if outcome_prices[1] else 0
                
                total_cost = yes_price + no_price
                
                # Arbitrage exists if total < 1.00
                if total_cost < 0.99:  # 1% threshold for fees
                    profit_pct = (1.0 - total_cost) * 100
                    opportunities.append({
                        'type': 'SAME_MARKET_ARB',
                        'market': market.get('question', 'Unknown'),
                        'slug': market.get('slug', ''),
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'total_cost': total_cost,
                        'profit_pct': profit_pct,
                        'volume': market.get('volume', 0)
                    })
        except (ValueError, TypeError, IndexError) as e:
            continue
    
    return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)

def find_mispriced_certainties(markets: List[Dict]) -> List[Dict]:
    """
    Find near-certain outcomes priced below 0.98 (potential edge)
    Or near-impossible outcomes priced above 0.02
    """
    opportunities = []
    
    for market in markets:
        try:
            outcome_prices = market.get('outcomePrices', [])
            end_date = market.get('endDate', '')
            
            if len(outcome_prices) >= 2:
                yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
                no_price = float(outcome_prices[1]) if outcome_prices[1] else 0
                
                # Near certainty but not quite at 1.0 - potential last-second edge
                if 0.95 <= yes_price < 0.98:
                    opportunities.append({
                        'type': 'CERTAINTY_DISCOUNT',
                        'market': market.get('question', 'Unknown'),
                        'side': 'YES',
                        'price': yes_price,
                        'implied_edge': (1.0 - yes_price) * 100,
                        'end_date': end_date,
                        'volume': market.get('volume', 0)
                    })
                
                if 0.95 <= no_price < 0.98:
                    opportunities.append({
                        'type': 'CERTAINTY_DISCOUNT',
                        'market': market.get('question', 'Unknown'),
                        'side': 'NO',
                        'price': no_price,
                        'implied_edge': (1.0 - no_price) * 100,
                        'end_date': end_date,
                        'volume': market.get('volume', 0)
                    })
                    
        except (ValueError, TypeError, IndexError):
            continue
    
    return sorted(opportunities, key=lambda x: x['implied_edge'], reverse=True)

def find_multi_outcome_arbitrage(event: Dict) -> Optional[Dict]:
    """
    For multi-outcome events, check if sum of all YES prices < 1.0
    Example: "Who wins the election?" with 5 candidates
    If sum of all YES prices < 1.0, buy all for guaranteed profit
    """
    markets = event.get('markets', [])
    
    if len(markets) < 2:
        return None
    
    total_yes = 0
    outcomes = []
    
    for market in markets:
        try:
            outcome_prices = market.get('outcomePrices', [])
            if outcome_prices:
                yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
                total_yes += yes_price
                outcomes.append({
                    'question': market.get('question', ''),
                    'yes_price': yes_price
                })
        except (ValueError, TypeError):
            continue
    
    if total_yes < 0.98 and len(outcomes) > 1:  # 2% threshold
        return {
            'type': 'MULTI_OUTCOME_ARB',
            'event': event.get('title', 'Unknown'),
            'slug': event.get('slug', ''),
            'total_yes': total_yes,
            'profit_pct': (1.0 - total_yes) * 100,
            'num_outcomes': len(outcomes),
            'outcomes': outcomes[:5]  # Top 5 for display
        }
    
    return None

def calculate_kelly(p_true: float, p_market: float) -> float:
    """
    Kelly criterion for binary prediction market
    f* = (p_true - p_market) / (1 - p_market)
    Returns recommended fraction of bankroll
    """
    if p_true <= p_market:
        return 0  # No edge
    
    kelly = (p_true - p_market) / (1 - p_market)
    half_kelly = kelly / 2  # Use half-Kelly for safety
    return min(half_kelly, 0.25)  # Cap at 25% of bankroll

def scan_all():
    """Run full market scan"""
    print("=" * 60)
    print(f"POLYMARKET SCANNER - {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Fetch markets
    print("\n[1] Fetching active markets...")
    markets = get_markets(limit=200)
    print(f"    Found {len(markets)} active markets")
    
    # Same-market arbitrage
    print("\n[2] Scanning for same-market arbitrage (YES + NO < 1.0)...")
    arb_opps = find_same_market_arbitrage(markets)
    if arb_opps:
        print(f"    🎯 FOUND {len(arb_opps)} ARBITRAGE OPPORTUNITIES:")
        for opp in arb_opps[:5]:
            print(f"       • {opp['market'][:50]}...")
            print(f"         YES: ${opp['yes_price']:.3f} + NO: ${opp['no_price']:.3f} = ${opp['total_cost']:.3f}")
            print(f"         Profit: {opp['profit_pct']:.2f}%")
    else:
        print("    No same-market arbitrage found (market is efficient)")
    
    # Near-certainty discounts
    print("\n[3] Scanning for mispriced certainties (95-98% outcomes)...")
    cert_opps = find_mispriced_certainties(markets)
    if cert_opps:
        print(f"    📊 FOUND {len(cert_opps)} POTENTIAL EDGES:")
        for opp in cert_opps[:5]:
            print(f"       • {opp['market'][:50]}...")
            print(f"         {opp['side']} @ ${opp['price']:.3f} (implied edge: {opp['implied_edge']:.1f}%)")
    else:
        print("    No mispriced certainties found")
    
    # Summary
    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print(f"Markets scanned: {len(markets)}")
    print(f"Arbitrage opportunities: {len(arb_opps)}")
    print(f"Certainty discounts: {len(cert_opps)}")
    print("=" * 60)
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'markets_scanned': len(markets),
        'arbitrage': arb_opps,
        'certainties': cert_opps
    }

if __name__ == "__main__":
    results = scan_all()
    
    # Save results
    with open('/home/ubuntu/clawd/trading/logs/scan_latest.json', 'w') as f:
        json.dump(results, f, indent=2)
