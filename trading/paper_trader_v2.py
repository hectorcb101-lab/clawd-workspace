#!/usr/bin/env python3
"""
Paper Trading System v2
Now with realistic execution: spreads, fees, slippage
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

TRADES_FILE = Path("/home/ubuntu/clawd/trading/paper_trades/trades_v2.json")
INITIAL_BANKROLL = 100.0
POLYMARKET_FEE = 0.01  # 1% fee assumption

def load_trades() -> Dict:
    if TRADES_FILE.exists():
        with open(TRADES_FILE) as f:
            return json.load(f)
    return {
        "initial_bankroll": INITIAL_BANKROLL,
        "current_bankroll": INITIAL_BANKROLL,
        "trades": [],
        "stats": {"total_trades": 0, "wins": 0, "losses": 0, "pending": 0, "total_pnl": 0.0, "total_fees": 0.0}
    }

def save_trades(data: Dict):
    TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRADES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_market_data(slug: str) -> Optional[Dict]:
    """Get real order book data"""
    try:
        resp = requests.get(
            f"https://gamma-api.polymarket.com/markets",
            params={"slug": slug, "limit": 1},
            timeout=30
        )
        markets = resp.json()
        if markets:
            m = markets[0]
            return {
                'question': m.get('question', ''),
                'bestBid': float(m.get('bestBid', 0) or 0),
                'bestAsk': float(m.get('bestAsk', 0) or 0),
                'spread': float(m.get('bestAsk', 0) or 0) - float(m.get('bestBid', 0) or 0),
                'volume': float(m.get('volume', 0) or 0),
                'liquidity': float(m.get('liquidity', 0) or 0)
            }
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
    return None

def estimate_slippage(position_size: float, liquidity: float) -> float:
    """Estimate slippage based on position size vs liquidity"""
    if liquidity <= 0:
        return 0.01  # 1% default
    impact_ratio = position_size / liquidity
    # Rough model: 0.1% slippage per 1% of liquidity taken
    return min(impact_ratio * 0.1, 0.05)  # Cap at 5%

def calculate_kelly(p_true: float, p_market: float, include_costs: bool = True) -> float:
    """Kelly with cost adjustment"""
    if p_true <= p_market:
        return 0
    
    # Adjust for fees
    if include_costs:
        # Fees reduce effective edge
        effective_edge = (p_true - p_market) - POLYMARKET_FEE
        if effective_edge <= 0:
            return 0
        kelly = effective_edge / (1 - p_market)
    else:
        kelly = (p_true - p_market) / (1 - p_market)
    
    return min(kelly / 2, 0.20)  # Half-Kelly, max 20%

def place_trade(
    market_slug: str,
    side: str,
    my_probability: float,
    reasoning: str,
    confidence: int = 3
) -> Dict:
    """Place trade with realistic execution"""
    
    # Get real market data
    market = get_market_data(market_slug)
    if not market:
        return {"error": f"Could not fetch market data for {market_slug}"}
    
    data = load_trades()
    bankroll = data["current_bankroll"]
    
    # Determine execution price (we pay the ask when buying)
    if side == "YES":
        entry_price = market['bestAsk']  # We buy at ask
        market_prob = entry_price
    else:
        # Buying NO means selling YES, or buying the NO side
        # NO price = 1 - YES price, but we pay ask
        entry_price = 1 - market['bestBid']  # NO ask ≈ 1 - YES bid
        market_prob = entry_price
    
    # Calculate Kelly with costs
    kelly_fraction = calculate_kelly(my_probability, market_prob, include_costs=True)
    
    if kelly_fraction <= 0:
        return {
            "error": "No edge after costs",
            "my_prob": my_probability,
            "market_prob": market_prob,
            "fees": POLYMARKET_FEE,
            "message": "Edge is smaller than transaction costs. No trade."
        }
    
    # Size the position
    confidence_mult = confidence / 5
    position_fraction = kelly_fraction * confidence_mult
    gross_position = bankroll * position_fraction
    
    # Calculate costs
    slippage = estimate_slippage(gross_position, market['liquidity'])
    slippage_cost = gross_position * slippage
    fee_cost = gross_position * POLYMARKET_FEE
    total_costs = slippage_cost + fee_cost
    
    # Net position after costs
    net_position = gross_position - total_costs
    effective_entry = entry_price * (1 + slippage)  # Worse price due to slippage
    shares = net_position / effective_entry if effective_entry > 0 else 0
    
    trade = {
        "id": len(data["trades"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_slug": market_slug,
        "market": market['question'],
        "side": side,
        "my_probability": my_probability,
        "market_probability": market_prob,
        "edge_gross": round((my_probability - market_prob) * 100, 2),
        "edge_net": round((my_probability - market_prob - POLYMARKET_FEE - slippage) * 100, 2),
        "entry_price_quote": entry_price,
        "entry_price_effective": round(effective_entry, 4),
        "slippage_pct": round(slippage * 100, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "position_gross": round(gross_position, 2),
        "slippage_cost": round(slippage_cost, 2),
        "fee_cost": round(fee_cost, 2),
        "total_costs": round(total_costs, 2),
        "position_net": round(net_position, 2),
        "shares": round(shares, 4),
        "reasoning": reasoning,
        "confidence": confidence,
        "status": "OPEN",
        "pnl": None
    }
    
    data["current_bankroll"] = round(bankroll - gross_position, 2)
    data["trades"].append(trade)
    data["stats"]["total_trades"] += 1
    data["stats"]["pending"] += 1
    data["stats"]["total_fees"] += total_costs
    
    save_trades(data)
    return trade

def resolve_trade(trade_id: int, outcome: str) -> Dict:
    """Resolve with realistic settlement"""
    data = load_trades()
    
    for trade in data["trades"]:
        if trade["id"] == trade_id and trade["status"] == "OPEN":
            if outcome == "WIN":
                # Payout = shares * $1.00 (no fee on settlement typically)
                gross_payout = trade["shares"] * 1.0
                pnl = gross_payout - trade["position_gross"]
                data["stats"]["wins"] += 1
            else:
                pnl = -trade["position_gross"]
                data["stats"]["losses"] += 1
            
            trade["status"] = "CLOSED"
            trade["pnl"] = round(pnl, 2)
            trade["resolution"] = outcome
            trade["resolved_at"] = datetime.now(timezone.utc).isoformat()
            
            data["current_bankroll"] = round(
                data["current_bankroll"] + trade["position_gross"] + pnl, 2
            )
            data["stats"]["pending"] -= 1
            data["stats"]["total_pnl"] = round(data["stats"]["total_pnl"] + pnl, 2)
            
            save_trades(data)
            return trade
    
    return {"error": f"Trade {trade_id} not found or already closed"}

def show_status():
    data = load_trades()
    open_trades = [t for t in data["trades"] if t["status"] == "OPEN"]
    
    print("=" * 70)
    print("PAPER TRADING v2 - WITH REALISTIC COSTS")
    print("=" * 70)
    print(f"Initial:     ${data['initial_bankroll']:.2f}")
    print(f"Bankroll:    ${data['current_bankroll']:.2f}")
    print(f"Exposure:    ${sum(t['position_gross'] for t in open_trades):.2f}")
    print(f"Total Fees:  ${data['stats']['total_fees']:.2f}")
    print(f"Net P&L:     ${data['stats']['total_pnl']:+.2f}")
    print("-" * 70)
    print(f"Trades: {data['stats']['total_trades']} | Open: {len(open_trades)} | W/L: {data['stats']['wins']}/{data['stats']['losses']}")
    print("=" * 70)
    
    if open_trades:
        print("\nOPEN POSITIONS:")
        for t in open_trades:
            print(f"\n#{t['id']} | {t['side']} {t['market'][:50]}...")
            print(f"   Entry: ${t['entry_price_effective']:.4f} (quoted ${t['entry_price_quote']:.4f} + {t['slippage_pct']}% slip)")
            print(f"   Size: ${t['position_gross']:.2f} gross → ${t['position_net']:.2f} net")
            print(f"   Edge: {t['edge_gross']}% gross → {t['edge_net']}% net (after costs)")
            print(f"   Shares: {t['shares']:.4f} | Max payout: ${t['shares']:.2f}")

if __name__ == "__main__":
    show_status()
