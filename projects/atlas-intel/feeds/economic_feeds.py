#!/usr/bin/env python3
"""Economic Feeds Monitor for Atlas Intel.

Tracks economic indicators and corporate events:
1. Shipping rates (Baltic Dry Index, Freightos Baltic Index)
2. SEC EDGAR 8-K filings (material corporate events)

Polls daily and stores significant changes/events.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding


# SEC EDGAR API
SEC_SEARCH_API = "https://efts.sec.gov/LATEST/search-index"

# Major companies to track (S&P 100 subset for MVP)
TRACKED_COMPANIES = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD",
    "BAC", "XOM", "CVX", "ABBV", "PFE", "KO", "PEP", "COST",
]

# Polling interval (seconds) - daily
POLL_INTERVAL = 24 * 60 * 60

# Log paths
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
EVENT_LOG = LOG_DIR / "economic_events.jsonl"
PROCESS_LOG = LOG_DIR / "economic_feeds.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(PROCESS_LOG),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def fetch_baltic_dry_index() -> dict[str, Any] | None:
    """Fetch Baltic Dry Index from Trading Economics.
    
    Uses web scraping since no direct API access.
    Falls back to trying Yahoo Finance ticker ^BDI.
    
    Returns:
        Dict with {value, date, change_pct} or None on failure
    """
    # Try Trading Economics first (web scraping)
    url = "https://tradingeconomics.com/commodity/baltic"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Look for price data in HTML (pattern matching)
        # Trading Economics typically has: <span id="p">VALUE</span>
        match = re.search(r'<span[^>]*id=["\']p["\'][^>]*>([0-9,\.]+)</span>', html)
        if match:
            value_str = match.group(1).replace(",", "")
            value = float(value_str)
            
            return {
                "index": "Baltic Dry Index",
                "ticker": "BDI",
                "value": value,
                "date": datetime.now(timezone.utc).isoformat(),
                "source": "Trading Economics",
            }
    except Exception as exc:
        logger.warning(f"Failed to scrape Baltic Dry Index from Trading Economics: {exc}")
    
    # Fallback: try yfinance
    try:
        import yfinance as yf
        ticker = yf.Ticker("^BDI")
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            latest = hist.iloc[-1]
            return {
                "index": "Baltic Dry Index",
                "ticker": "^BDI",
                "value": float(latest["Close"]),
                "date": datetime.now(timezone.utc).isoformat(),
                "source": "Yahoo Finance",
            }
    except Exception as exc:
        logger.warning(f"Failed to fetch Baltic Dry Index from Yahoo Finance: {exc}")
    
    logger.error("All Baltic Dry Index sources failed")
    return None


def fetch_shipping_rates() -> list[dict[str, Any]]:
    """Fetch shipping rate indicators.
    
    Returns:
        List of shipping rate dicts
    """
    rates = []
    
    # Baltic Dry Index
    bdi = fetch_baltic_dry_index()
    if bdi:
        rates.append(bdi)
    
    # Try to fetch Freightos Baltic Index (FBX) - not commonly available on free APIs
    # For MVP, we'll track via web scraping if needed in future iterations
    
    return rates


def fetch_sec_8k_filings(
    ticker: str,
    days_back: int = 1,
) -> list[dict[str, Any]]:
    """Fetch recent 8-K filings for a company from SEC EDGAR.
    
    Args:
        ticker: Company ticker symbol
        days_back: How many days back to search
    
    Returns:
        List of filing dicts
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        "q": ticker,
        "dateRange": "custom",
        "startdt": start_date.strftime("%Y-%m-%d"),
        "enddt": end_date.strftime("%Y-%m-%d"),
        "forms": "8-K",  # Material events only
    }
    
    headers = {
        "User-Agent": "Atlas Intel Monitor (contact@example.com)",  # SEC requires user agent
    }
    
    try:
        response = requests.get(SEC_SEARCH_API, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        filings = data.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}) for hit in filings]
        
    except requests.RequestException as exc:
        logger.error(f"SEC EDGAR request failed for {ticker}: {exc}")
        return []
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse SEC response for {ticker}: {exc}")
        return []


def process_shipping_rate(rate_data: dict[str, Any]) -> dict[str, Any]:
    """Process shipping rate update: embed and store.
    
    Args:
        rate_data: Shipping rate dict
    
    Returns:
        Event record with embedding_id
    """
    index_name = rate_data.get("index", "Unknown")
    value = rate_data.get("value", 0)
    source = rate_data.get("source", "Unknown")
    date = rate_data.get("date", "")
    
    content_text = f"""
Economic Indicator Update
Indicator: {index_name}
Value: {value}
Source: {source}
Date: {date}

The {index_name} is a key shipping cost indicator that reflects global trade activity and supply chain conditions.
    """.strip()
    
    # Generate embedding
    try:
        embedding = embed_text(content_text)
    except Exception as exc:
        logger.error(f"Embedding failed for {index_name}: {exc}")
        return {}
    
    # Store in vector DB
    metadata = {
        "indicator": index_name,
        "ticker": rate_data.get("ticker", ""),
        "value": float(value),
        "source": source,
        "timestamp": date,
    }
    
    try:
        result = store_embedding(
            source_type="economic_indicator",
            content=content_text,
            metadata=metadata,
            embedding=embedding,
            source_id=f"{index_name}_{date}",
        )
        
        event_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "embedding_id": result.get("id"),
            "indicator": index_name,
            "value": float(value),
            "source": source,
        }
        
        # Log to JSONL
        with EVENT_LOG.open("a") as f:
            f.write(json.dumps(event_record) + "\n")
        
        logger.info(f"Stored shipping rate: {index_name} = {value}")
        return event_record
        
    except Exception as exc:
        logger.error(f"Failed to store shipping rate '{index_name}': {exc}")
        return {}


def process_sec_filing(filing: dict[str, Any], ticker: str) -> dict[str, Any]:
    """Process SEC 8-K filing: embed and store.
    
    Args:
        filing: SEC filing dict
        ticker: Company ticker
    
    Returns:
        Event record with embedding_id
    """
    company_name = filing.get("display_names", [ticker])[0] if filing.get("display_names") else ticker
    file_date = filing.get("file_date", "")
    description = filing.get("items", "Material event")
    filing_url = filing.get("file_num", "")
    
    # Construct filing URL if we have accession number
    accession = filing.get("adsh", "")
    if accession:
        # Format: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=XXXX&type=8-K&dateb=&owner=exclude&count=40
        filing_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K"
    
    content_text = f"""
SEC 8-K Filing Alert
Company: {company_name} ({ticker})
Filed: {file_date}
Items: {description}
URL: {filing_url}

An 8-K filing indicates a material corporate event that may impact market perception.
    """.strip()
    
    # Generate embedding
    try:
        embedding = embed_text(content_text)
    except Exception as exc:
        logger.error(f"Embedding failed for {ticker} 8-K filing: {exc}")
        return {}
    
    # Store in vector DB
    metadata = {
        "company": company_name,
        "ticker": ticker,
        "file_date": file_date,
        "items": description,
        "url": filing_url,
        "accession": accession,
    }
    
    try:
        result = store_embedding(
            source_type="sec_filing",
            content=content_text,
            metadata=metadata,
            embedding=embedding,
            source_id=accession or f"{ticker}_{file_date}",
        )
        
        event_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "embedding_id": result.get("id"),
            "company": company_name,
            "ticker": ticker,
            "file_date": file_date,
            "items": description,
        }
        
        # Log to JSONL
        with EVENT_LOG.open("a") as f:
            f.write(json.dumps(event_record) + "\n")
        
        logger.info(f"Stored SEC filing: {ticker} on {file_date}")
        return event_record
        
    except Exception as exc:
        logger.error(f"Failed to store SEC filing for {ticker}: {exc}")
        return {}


def poll_economic_feeds() -> int:
    """Poll economic data sources for updates.
    
    Returns:
        Number of new events stored
    """
    logger.info("Polling economic feeds...")
    
    new_events = 0
    
    # 1. Shipping rates
    logger.info("Fetching shipping rates...")
    rates = fetch_shipping_rates()
    for rate in rates:
        event = process_shipping_rate(rate)
        if event:
            new_events += 1
    
    # 2. SEC 8-K filings
    logger.info(f"Checking SEC 8-K filings for {len(TRACKED_COMPANIES)} companies...")
    for ticker in TRACKED_COMPANIES:
        filings = fetch_sec_8k_filings(ticker, days_back=1)
        
        if filings:
            logger.info(f"Found {len(filings)} new 8-K filings for {ticker}")
            
            for filing in filings:
                event = process_sec_filing(filing, ticker)
                if event:
                    new_events += 1
        
        # Rate limit SEC requests (10 requests/second limit)
        time.sleep(0.15)
    
    logger.info(f"Economic feeds polling complete. {new_events} new events stored.")
    return new_events


def run_monitor():
    """Run the economic feeds monitor in polling loop."""
    logger.info("Starting Economic Feeds Monitor...")
    logger.info(f"Tracking {len(TRACKED_COMPANIES)} companies for 8-K filings")
    logger.info(f"Tracking shipping rates: Baltic Dry Index")
    logger.info(f"Poll interval: {POLL_INTERVAL // 3600} hours")
    
    while True:
        try:
            poll_economic_feeds()
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user.")
            break
        except Exception as exc:
            logger.error(f"Unexpected error during polling: {exc}", exc_info=True)
        
        logger.info(f"Next poll in {POLL_INTERVAL // 3600} hours...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_monitor()
