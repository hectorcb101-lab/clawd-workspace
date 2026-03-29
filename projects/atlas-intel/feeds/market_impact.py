#!/usr/bin/env python3
"""Market impact correlation engine for Atlas Intel.

Tracks real-time market data and correlates with geopolitical events.
Uses yfinance for market data (free, no API key needed).

Tracked assets:
- VIX (volatility index)
- Oil futures (CL=F)
- Gold (GC=F)
- Defense ETF (ITA)
- S&P 500 (^GSPC)

Free tier: yfinance unlimited (Yahoo Finance data).
"""

from __future__ import annotations

import json
import logging
import sys
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yfinance as yf

# Add parent directory to path for atlas_intel imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 300  # 5 minutes

# Market symbols to track
MARKET_SYMBOLS = {
    "VIX": "^VIX",         # Volatility index
    "OIL": "CL=F",         # Crude oil futures
    "GOLD": "GC=F",        # Gold futures
    "DEFENSE": "ITA",      # iShares U.S. Aerospace & Defense ETF
    "SP500": "^GSPC",      # S&P 500
}

# Thresholds for significant changes
SIGNIFICANT_CHANGE_PCT = 1.5  # 1.5% change is significant

# Logs and output
LOG_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/logs")
OUTPUT_DIR = Path("/home/ubuntu/clawd/projects/atlas-intel/dashboard/data")
LOG_FILE = LOG_DIR / "market_impact.log"
EVENTS_FILE = LOG_DIR / "market_events.jsonl"
OUTPUT_FILE = OUTPUT_DIR / "market_status.json"
GEO_EVENTS_FILE = OUTPUT_DIR / "geopolitical.json"
MILITARY_FILE = OUTPUT_DIR / "military_status.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Market tracking
# ---------------------------------------------------------------------------

@dataclass
class MarketSnapshot:
    """Market data snapshot."""
    symbol: str
    value: float
    change_pct: float
    timestamp: datetime


@dataclass
class Correlation:
    """Market-event correlation."""
    event: str
    market_impact: str
    timestamp: datetime


class MarketTracker:
    """Track market data and correlate with geopolitical events."""
    
    def __init__(self):
        self.market_history: dict[str, deque] = {
            symbol: deque(maxlen=288)  # 24h of 5-min samples
            for symbol in MARKET_SYMBOLS.keys()
        }
        self.correlations: list[Correlation] = []
        self.last_geo_check = datetime.now(timezone.utc)
        
    def fetch_market_data(self) -> dict[str, MarketSnapshot]:
        """Fetch current market data using yfinance."""
        snapshots = {}
        
        for name, symbol in MARKET_SYMBOLS.items():
            try:
                ticker = yf.Ticker(symbol)
                
                # Get recent data (last 2 days to calculate change)
                hist = ticker.history(period="2d", interval="1d")
                
                if hist.empty or len(hist) < 1:
                    logger.warning(f"No data for {symbol}")
                    continue
                
                # Get current price (latest close)
                current_price = hist['Close'].iloc[-1]
                
                # Calculate change percentage
                if len(hist) >= 2:
                    prev_price = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                else:
                    change_pct = 0.0
                
                snapshot = MarketSnapshot(
                    symbol=symbol,
                    value=float(current_price),
                    change_pct=float(change_pct),
                    timestamp=datetime.now(timezone.utc),
                )
                
                snapshots[name] = snapshot
                
                logger.info(f"{name} ({symbol}): ${current_price:.2f} ({change_pct:+.2f}%)")
                
                # Store in history
                self.market_history[name].append(snapshot)
                
                # Rate limit courtesy
                time.sleep(0.5)
                
            except Exception as exc:
                logger.error(f"Failed to fetch {symbol}: {exc}")
        
        return snapshots
    
    def load_geopolitical_events(self) -> list[dict]:
        """Load recent geopolitical events from other feeds."""
        events = []
        
        # Load from geopolitical feed
        try:
            if GEO_EVENTS_FILE.exists():
                with open(GEO_EVENTS_FILE, "r") as f:
                    geo_data = json.load(f)
                
                if isinstance(geo_data, list):
                    for item in geo_data:
                        if "timestamp" in item:
                            event_time = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                            # Only consider events from last hour
                            if (datetime.now(timezone.utc) - event_time).total_seconds() < 3600:
                                events.append(item)
        except Exception as exc:
            logger.debug(f"Could not load geopolitical events: {exc}")
        
        # Load from military tracker
        try:
            if MILITARY_FILE.exists():
                with open(MILITARY_FILE, "r") as f:
                    mil_data = json.load(f)
                
                if "hotspots" in mil_data:
                    for hotspot in mil_data["hotspots"]:
                        if hotspot.get("intensity") in ["HIGH", "CRITICAL"]:
                            events.append({
                                "type": "military_hotspot",
                                "region": hotspot.get("region"),
                                "intensity": hotspot.get("intensity"),
                                "timestamp": mil_data.get("last_update", datetime.now(timezone.utc).isoformat()),
                            })
        except Exception as exc:
            logger.debug(f"Could not load military events: {exc}")
        
        return events
    
    def correlate_with_events(self, snapshots: dict[str, MarketSnapshot]):
        """Correlate market changes with geopolitical events."""
        # Load recent geopolitical events
        events = self.load_geopolitical_events()
        
        if not events:
            logger.debug("No recent geopolitical events to correlate")
            return
        
        # Check for significant market movements
        significant_changes = []
        for name, snapshot in snapshots.items():
            if abs(snapshot.change_pct) >= SIGNIFICANT_CHANGE_PCT:
                significant_changes.append((name, snapshot))
        
        if not significant_changes:
            logger.debug("No significant market changes")
            return
        
        # Create correlations for each significant change + recent event
        for event in events:
            for name, snapshot in significant_changes:
                event_desc = event.get("region", event.get("type", "Unknown event"))
                market_impact = f"{name} {snapshot.change_pct:+.1f}%"
                
                correlation = Correlation(
                    event=event_desc,
                    market_impact=market_impact,
                    timestamp=datetime.now(timezone.utc),
                )
                
                self.correlations.append(correlation)
                logger.info(f"Correlation: {event_desc} → {market_impact}")
                
                # Log to events file
                self.log_correlation(correlation)
        
        # Keep only last 50 correlations
        self.correlations = self.correlations[-50:]
    
    def generate_output(self, snapshots: dict[str, MarketSnapshot]):
        """Generate JSON output for dashboard."""
        markets_dict = {}
        
        for name, snapshot in snapshots.items():
            markets_dict[name] = {
                "value": round(snapshot.value, 2),
                "change_pct": round(snapshot.change_pct, 2),
            }
        
        # Recent correlations (last 10)
        correlations_list = [
            {
                "event": c.event,
                "market_impact": c.market_impact,
                "timestamp": c.timestamp.isoformat(),
            }
            for c in self.correlations[-10:]
        ]
        
        output = {
            "status": "online",
            "markets": markets_dict,
            "correlations": correlations_list,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }
        
        # Write to dashboard JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Output written to {OUTPUT_FILE}")
    
    def log_correlation(self, correlation: Correlation):
        """Log correlation to JSONL file."""
        with open(EVENTS_FILE, "a") as f:
            event_data = {
                "timestamp": correlation.timestamp.isoformat(),
                "event": correlation.event,
                "market_impact": correlation.market_impact,
            }
            f.write(json.dumps(event_data) + "\n")
    
    def poll(self):
        """Main polling cycle."""
        logger.info("Starting market poll")
        
        # Fetch market data
        snapshots = self.fetch_market_data()
        
        if not snapshots:
            logger.warning("No market data fetched")
            return
        
        # Correlate with geopolitical events
        self.correlate_with_events(snapshots)
        
        # Generate output
        self.generate_output(snapshots)
        
        logger.info(f"Poll complete: {len(snapshots)} markets tracked, {len(self.correlations)} total correlations")
    
    def run(self):
        """Main daemon loop."""
        logger.info("Market tracker daemon starting")
        logger.info(f"Tracking {len(MARKET_SYMBOLS)} market symbols")
        logger.info(f"Poll interval: {POLL_INTERVAL_SECONDS}s")
        
        while True:
            try:
                self.poll()
                
                logger.debug(f"Sleeping {POLL_INTERVAL_SECONDS}s until next poll")
                time.sleep(POLL_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                break
            except Exception as exc:
                logger.error(f"Unexpected error in main loop: {exc}", exc_info=True)
                time.sleep(60)  # Back off on errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tracker = MarketTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("TEST MODE: Single poll")
        tracker.poll()
        logger.info(f"Test complete. Output: {OUTPUT_FILE}")
    else:
        tracker.run()
