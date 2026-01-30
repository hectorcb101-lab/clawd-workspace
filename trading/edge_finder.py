#!/usr/bin/env python3
"""
Edge Finder - Looking for behavioral biases
Based on TRADING_MASTERY framework
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict

GAMMA_API = "https://gamma-api.polymarket.com"

def get_markets(limit: int = 200) -> List[Dict]:
    """Fetch markets"""
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"limit": limit, "active": "true", "closed": "false"},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_longshot_bias(markets: List[Dict]) -> List[Dict]:
    """
    Find overpriced longshots (betting against the crowd)
    Research shows: low-probability outcomes are systematically overpriced
    Edge: Sell (bet NO on) longshots priced above true value
    """
    opportunities = []
    
    for market in markets:
        try:
            outcome_prices = market.get('outcomePrices', [])
            volume = float(market.get('volume', 0) or 0)
            
            if len(outcome_prices) < 2 or volume < 10000:  # Skip low volume
                continue
            
            yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
            
            # Longshot = YES priced between 1-15%
            # Research shows these are often overpriced by 2-5%
            if 0.01 <= yes_price <= 0.15:
                # Estimate true probability (conservative: assume 50% of the bias)
                # If priced at 10%, true prob might be ~7%
                estimated_true = yes_price * 0.7  # 30% overpricing assumption
                edge = yes_price - estimated_true
                
                opportunities.append({
                    'type': 'LONGSHOT_BIAS',
                    'action': 'SELL_YES / BUY_NO',
                    'market': market.get('question', ''),
                    'slug': market.get('slug', ''),
                    'yes_price': yes_price,
                    'estimated_true': estimated_true,
                    'edge_estimate': edge,
                    'volume': volume,
                    'category': market.get('category', 'Unknown')
                })
                
        except (ValueError, TypeError):
            continue
    
    return sorted(opportunities, key=lambda x: x['edge_estimate'], reverse=True)

def analyze_favourite_longshot(markets: List[Dict]) -> List[Dict]:
    """
    Find underpriced favourites
    The flip side: high-probability outcomes are sometimes underpriced
    """
    opportunities = []
    
    for market in markets:
        try:
            outcome_prices = market.get('outcomePrices', [])
            volume = float(market.get('volume', 0) or 0)
            
            if len(outcome_prices) < 2 or volume < 10000:
                continue
            
            yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
            
            # Favourites = YES priced between 85-95%
            if 0.85 <= yes_price <= 0.95:
                # These might be underpriced by 1-3%
                estimated_true = min(0.98, yes_price * 1.03)
                edge = estimated_true - yes_price
                
                opportunities.append({
                    'type': 'FAVOURITE_UNDERPRICED',
                    'action': 'BUY_YES',
                    'market': market.get('question', ''),
                    'slug': market.get('slug', ''),
                    'yes_price': yes_price,
                    'estimated_true': estimated_true,
                    'edge_estimate': edge,
                    'volume': volume,
                    'category': market.get('category', 'Unknown')
                })
                
        except (ValueError, TypeError):
            continue
    
    return sorted(opportunities, key=lambda x: x['edge_estimate'], reverse=True)

def analyze_volume_signals(markets: List[Dict]) -> List[Dict]:
    """
    High volume often indicates informed trading
    Look for markets with unusual volume patterns
    """
    # Calculate volume statistics
    volumes = [float(m.get('volume', 0) or 0) for m in markets if m.get('volume')]
    if not volumes:
        return []
    
    avg_volume = sum(volumes) / len(volumes)
    
    high_volume = []
    for market in markets:
        try:
            volume = float(market.get('volume', 0) or 0)
            if volume > avg_volume * 3:  # 3x average volume
                outcome_prices = market.get('outcomePrices', [])
                yes_price = float(outcome_prices[0]) if outcome_prices and outcome_prices[0] else 0
                
                high_volume.append({
                    'type': 'HIGH_VOLUME_SIGNAL',
                    'market': market.get('question', ''),
                    'volume': volume,
                    'volume_ratio': volume / avg_volume,
                    'yes_price': yes_price,
                    'category': market.get('category', 'Unknown')
                })
        except (ValueError, TypeError):
            continue
    
    return sorted(high_volume, key=lambda x: x['volume_ratio'], reverse=True)[:10]

def run_analysis():
    """Full edge analysis"""
    print("=" * 70)
    print(f"EDGE FINDER - {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)
    
    markets = get_markets(200)
    print(f"\nAnalysing {len(markets)} markets...\n")
    
    # Longshot bias
    print("[1] LONGSHOT BIAS (sell overpriced low-probability outcomes)")
    print("-" * 70)
    longshots = analyze_longshot_bias(markets)
    if longshots:
        for opp in longshots[:5]:
            print(f"• {opp['market'][:55]}...")
            print(f"  YES @ ${opp['yes_price']:.2f} | Est. True: {opp['estimated_true']:.2f} | Edge: {opp['edge_estimate']:.2f}")
            print(f"  Volume: ${opp['volume']:,.0f} | Category: {opp['category']}")
            print()
    else:
        print("  No clear longshot bias opportunities\n")
    
    # Favourite underpricing
    print("[2] FAVOURITE UNDERPRICING (buy high-probability outcomes)")
    print("-" * 70)
    favourites = analyze_favourite_longshot(markets)
    if favourites:
        for opp in favourites[:5]:
            print(f"• {opp['market'][:55]}...")
            print(f"  YES @ ${opp['yes_price']:.2f} | Est. True: {opp['estimated_true']:.2f} | Edge: {opp['edge_estimate']:.2f}")
            print(f"  Volume: ${opp['volume']:,.0f} | Category: {opp['category']}")
            print()
    else:
        print("  No clear favourite opportunities\n")
    
    # Volume signals
    print("[3] HIGH VOLUME SIGNALS (informed trading indicator)")
    print("-" * 70)
    high_vol = analyze_volume_signals(markets)
    if high_vol:
        for sig in high_vol[:5]:
            print(f"• {sig['market'][:55]}...")
            print(f"  Volume: ${sig['volume']:,.0f} ({sig['volume_ratio']:.1f}x average)")
            print(f"  Current YES: ${sig['yes_price']:.2f} | Category: {sig['category']}")
            print()
    else:
        print("  No unusual volume signals\n")
    
    print("=" * 70)
    print("Analysis complete. Remember: These are estimates, not certainties.")
    print("Use half-Kelly sizing. Never risk more than you can lose.")
    print("=" * 70)
    
    return {
        'longshots': longshots,
        'favourites': favourites,
        'volume_signals': high_vol
    }

if __name__ == "__main__":
    results = run_analysis()
    
    # Save results
    with open('/home/ubuntu/clawd/trading/logs/edge_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
