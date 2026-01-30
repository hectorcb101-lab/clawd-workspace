#!/usr/bin/env python3
"""
Trade Monitor - Check current prices for open positions
"""

import requests
import json
from datetime import datetime, timezone
from pathlib import Path

TRADES_FILE = Path("/home/ubuntu/clawd/trading/paper_trades/trades.json")

# Map our trade descriptions to search terms
MARKET_SEARCH = {
    "Russia x Ukraine ceasefire by March 31, 2026?": "russia ukraine ceasefire",
    "Will China invade Taiwan by end of 2026?": "china invade taiwan 2026",
    "No change in Fed interest rates after January 2026 meeting?": "fed january 2026"
}

def search_market(query: str):
    """Search for a market by query"""
    try:
        resp = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={"limit": 50, "active": "true"},
            timeout=30
        )
        markets = resp.json()
        
        for m in markets:
            q = m.get('question', '').lower()
            if all(word in q for word in query.lower().split()):
                op = m.get('outcomePrices', '[]')
                if isinstance(op, str):
                    op = json.loads(op)
                return {
                    'question': m.get('question'),
                    'yes_price': float(op[0]) if op and op[0] else 0,
                    'no_price': float(op[1]) if len(op) > 1 and op[1] else 0,
                    'volume': m.get('volume', 0)
                }
    except Exception as e:
        print(f"Error searching: {e}")
    return None

def monitor_positions():
    """Monitor all open positions"""
    if not TRADES_FILE.exists():
        print("No trades file found")
        return
    
    with open(TRADES_FILE) as f:
        data = json.load(f)
    
    open_trades = [t for t in data['trades'] if t['status'] == 'OPEN']
    
    print("=" * 70)
    print(f"POSITION MONITOR - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    print(f"Bankroll: ${data['current_bankroll']:.2f} | Exposure: ${sum(t['position_size'] for t in open_trades):.2f}")
    print("=" * 70)
    
    for trade in open_trades:
        search_term = MARKET_SEARCH.get(trade['market'], trade['market'].split('?')[0])
        current = search_market(search_term)
        
        print(f"\n#{trade['id']} | {trade['side']} @ ${trade['entry_price']:.3f} | Size: ${trade['position_size']:.2f}")
        print(f"Market: {trade['market'][:60]}...")
        
        if current:
            current_price = current['yes_price'] if trade['side'] == 'YES' else current['no_price']
            price_change = current_price - trade['entry_price']
            pnl_estimate = price_change * trade['shares']
            
            print(f"Current: YES ${current['yes_price']:.3f} | NO ${current['no_price']:.3f}")
            print(f"Your side: ${current_price:.3f} ({price_change:+.3f})")
            print(f"Unrealised P&L: ${pnl_estimate:+.2f}")
        else:
            print("Could not fetch current price")
        
        print(f"Reasoning: {trade['reasoning'][:80]}...")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    monitor_positions()
