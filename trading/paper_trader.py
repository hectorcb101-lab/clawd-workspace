#!/usr/bin/env python3
"""
Paper Trading System
Track hypothetical trades to build intuition and verify edge
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pathlib import Path

TRADES_FILE = Path("/home/ubuntu/clawd/trading/paper_trades/trades.json")
INITIAL_BANKROLL = 100.0  # Simulated $100

def load_trades() -> Dict:
    """Load existing trades"""
    if TRADES_FILE.exists():
        with open(TRADES_FILE) as f:
            return json.load(f)
    return {
        "initial_bankroll": INITIAL_BANKROLL,
        "current_bankroll": INITIAL_BANKROLL,
        "trades": [],
        "stats": {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "pending": 0,
            "total_pnl": 0.0
        }
    }

def save_trades(data: Dict):
    """Save trades to file"""
    TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRADES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_kelly(p_true: float, p_market: float) -> float:
    """Half-Kelly position sizing"""
    if p_true <= p_market:
        return 0
    kelly = (p_true - p_market) / (1 - p_market)
    return min(kelly / 2, 0.25)  # Half-Kelly, max 25%

def place_trade(
    market: str,
    side: str,  # "YES" or "NO"
    entry_price: float,
    my_probability: float,
    reasoning: str,
    confidence: int = 3  # 1-5 scale
) -> Dict:
    """
    Place a paper trade
    
    Args:
        market: Market question/description
        side: "YES" or "NO"
        entry_price: Current market price (0-1)
        my_probability: My estimated true probability (0-1)
        reasoning: Why I think I have edge
        confidence: 1-5 confidence scale
    """
    data = load_trades()
    bankroll = data["current_bankroll"]
    
    # Calculate position size using Kelly
    market_prob = entry_price if side == "YES" else (1 - entry_price)
    kelly_fraction = calculate_kelly(my_probability, market_prob)
    
    # Adjust for confidence
    confidence_multiplier = confidence / 5
    position_fraction = kelly_fraction * confidence_multiplier
    
    # Size the trade
    position_size = bankroll * position_fraction
    shares = position_size / entry_price if entry_price > 0 else 0
    
    trade = {
        "id": len(data["trades"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market": market,
        "side": side,
        "entry_price": entry_price,
        "my_probability": my_probability,
        "kelly_fraction": kelly_fraction,
        "position_fraction": position_fraction,
        "position_size": round(position_size, 2),
        "shares": round(shares, 4),
        "reasoning": reasoning,
        "confidence": confidence,
        "status": "OPEN",
        "exit_price": None,
        "pnl": None,
        "resolution": None
    }
    
    # Update bankroll (reserve position size)
    data["current_bankroll"] = round(bankroll - position_size, 2)
    data["trades"].append(trade)
    data["stats"]["total_trades"] += 1
    data["stats"]["pending"] += 1
    
    save_trades(data)
    
    return trade

def resolve_trade(trade_id: int, outcome: str, exit_price: Optional[float] = None) -> Dict:
    """
    Resolve a trade
    
    Args:
        trade_id: Trade ID to resolve
        outcome: "WIN" or "LOSS" (or "PUSH" for cancelled)
        exit_price: Optional exit price if closed early
    """
    data = load_trades()
    
    for trade in data["trades"]:
        if trade["id"] == trade_id and trade["status"] == "OPEN":
            if outcome == "WIN":
                # Full payout
                pnl = trade["shares"] * 1.0 - trade["position_size"]
                trade["exit_price"] = 1.0
                data["stats"]["wins"] += 1
            elif outcome == "LOSS":
                # Lose position
                pnl = -trade["position_size"]
                trade["exit_price"] = 0.0
                data["stats"]["losses"] += 1
            else:  # PUSH
                pnl = 0
                trade["exit_price"] = trade["entry_price"]
            
            trade["status"] = "CLOSED"
            trade["pnl"] = round(pnl, 2)
            trade["resolution"] = outcome
            trade["resolved_at"] = datetime.now(timezone.utc).isoformat()
            
            data["current_bankroll"] = round(data["current_bankroll"] + trade["position_size"] + pnl, 2)
            data["stats"]["pending"] -= 1
            data["stats"]["total_pnl"] = round(data["stats"]["total_pnl"] + pnl, 2)
            
            save_trades(data)
            return trade
    
    return {"error": f"Trade {trade_id} not found or already closed"}

def get_portfolio() -> Dict:
    """Get current portfolio status"""
    data = load_trades()
    
    open_trades = [t for t in data["trades"] if t["status"] == "OPEN"]
    closed_trades = [t for t in data["trades"] if t["status"] == "CLOSED"]
    
    win_rate = data["stats"]["wins"] / max(1, data["stats"]["wins"] + data["stats"]["losses"])
    
    return {
        "initial_bankroll": data["initial_bankroll"],
        "current_bankroll": data["current_bankroll"],
        "unrealised_exposure": sum(t["position_size"] for t in open_trades),
        "total_pnl": data["stats"]["total_pnl"],
        "return_pct": ((data["current_bankroll"] + sum(t["position_size"] for t in open_trades)) / data["initial_bankroll"] - 1) * 100,
        "total_trades": data["stats"]["total_trades"],
        "open_trades": len(open_trades),
        "closed_trades": len(closed_trades),
        "wins": data["stats"]["wins"],
        "losses": data["stats"]["losses"],
        "win_rate": round(win_rate * 100, 1),
        "open_positions": open_trades
    }

def show_status():
    """Display portfolio status"""
    portfolio = get_portfolio()
    
    print("=" * 60)
    print("PAPER TRADING PORTFOLIO")
    print("=" * 60)
    print(f"Initial Bankroll:  ${portfolio['initial_bankroll']:.2f}")
    print(f"Current Bankroll:  ${portfolio['current_bankroll']:.2f}")
    print(f"Open Exposure:     ${portfolio['unrealised_exposure']:.2f}")
    print(f"Total P&L:         ${portfolio['total_pnl']:+.2f}")
    print(f"Return:            {portfolio['return_pct']:+.1f}%")
    print("-" * 60)
    print(f"Total Trades:      {portfolio['total_trades']}")
    print(f"Open Positions:    {portfolio['open_trades']}")
    print(f"Closed Trades:     {portfolio['closed_trades']}")
    print(f"Win/Loss:          {portfolio['wins']}/{portfolio['losses']}")
    print(f"Win Rate:          {portfolio['win_rate']}%")
    print("=" * 60)
    
    if portfolio['open_positions']:
        print("\nOPEN POSITIONS:")
        for t in portfolio['open_positions']:
            print(f"  #{t['id']} | {t['side']} @ ${t['entry_price']:.3f} | ${t['position_size']:.2f}")
            print(f"       {t['market'][:60]}...")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_status()
    elif sys.argv[1] == "status":
        show_status()
    else:
        print("Usage: python3 paper_trader.py [status]")
