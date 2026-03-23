#!/usr/bin/env python3
"""GDELT Global Event Monitor for Atlas Intel.

Monitors GDELT API for significant geopolitical events:
- Military movements, sanctions, trade disputes
- Energy events (oil, natural gas, nuclear)
- Political instability (protests, coups)

Filters by Goldstein scale (|score| > 5) and tracks high-impact themes.
"""

from __future__ import annotations

import json
import logging
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


# GDELT API endpoints
GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_GEO_API = "https://api.gdeltproject.org/api/v2/geo/geo"

# High-impact themes to track
TRACKED_THEMES = [
    "MILITARY",
    "SANCTIONS",
    "TRADE_DISPUTE",
    "OIL",
    "NATURAL_GAS",
    "NUCLEAR",
    "PROTEST",
    "COUP",
    "TERROR",
    "ECON_CRISIS",
]

# Goldstein scale threshold (absolute value)
GOLDSTEIN_THRESHOLD = 5.0

# Polling interval (seconds) - 15 minutes
POLL_INTERVAL = 15 * 60

# Log paths
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
EVENT_LOG = LOG_DIR / "gdelt_events.jsonl"
PROCESS_LOG = LOG_DIR / "gdelt_monitor.log"

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


def fetch_gdelt_articles(
    query: str,
    mode: str = "ArtList",
    max_records: int = 250,
    timespan: str = "15m",
) -> list[dict[str, Any]]:
    """Fetch articles from GDELT DOC API.
    
    Args:
        query: Search query (theme, keyword, or combination)
        mode: API mode (ArtList, TimelineVol, etc.)
        max_records: Maximum articles to return
        timespan: Time window (15m, 1h, 24h, etc.)
    
    Returns:
        List of article dicts with title, url, domain, language, etc.
    """
    params = {
        "query": query,
        "mode": mode,
        "format": "json",
        "maxrecords": max_records,
        "timespan": timespan,
    }
    
    try:
        response = requests.get(GDELT_DOC_API, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # DOC API returns articles in 'articles' field
        return data.get("articles", [])
    except requests.RequestException as exc:
        logger.error(f"GDELT DOC API request failed: {exc}")
        return []
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse GDELT response: {exc}")
        return []


def calculate_significance_score(article: dict[str, Any]) -> float:
    """Calculate a significance score for an article.
    
    Uses tone (avg sentiment), socialimage (virality), and domain rank.
    Higher absolute tone values = more significant.
    
    Returns:
        Significance score (0-100+)
    """
    tone = abs(float(article.get("tone", 0)))
    social_image = int(article.get("socialimage", 0))
    domain_rank = 100 - min(int(article.get("domain_rank", 100)), 100)  # Invert so lower rank = higher score
    
    # Weighted combination
    score = (tone * 2) + (social_image / 10) + (domain_rank / 2)
    return round(score, 2)


def extract_themes(article: dict[str, Any]) -> list[str]:
    """Extract tracked themes from article metadata.
    
    GDELT includes theme tags in the 'themes' field.
    """
    themes_str = article.get("themes", "")
    if not themes_str:
        return []
    
    found_themes = []
    for theme in TRACKED_THEMES:
        if theme in themes_str.upper():
            found_themes.append(theme)
    
    return found_themes


def filter_significant_events(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter articles for high-significance events.
    
    Criteria:
    - Contains at least one tracked theme
    - Significance score > GOLDSTEIN_THRESHOLD (using tone as proxy)
    - Published within timespan
    """
    significant = []
    
    for article in articles:
        themes = extract_themes(article)
        if not themes:
            continue
        
        sig_score = calculate_significance_score(article)
        
        # Use absolute tone as proxy for Goldstein scale (impact magnitude)
        tone = abs(float(article.get("tone", 0)))
        
        if tone > GOLDSTEIN_THRESHOLD or sig_score > 20:
            article["tracked_themes"] = themes
            article["significance_score"] = sig_score
            significant.append(article)
    
    return significant


def process_event(article: dict[str, Any]) -> dict[str, Any]:
    """Process a significant event: embed and store.
    
    Args:
        article: GDELT article dict
    
    Returns:
        Event record with embedding_id
    """
    # Construct content summary
    title = article.get("title", "")
    url = article.get("url", "")
    domain = article.get("domain", "")
    seendate = article.get("seendate", "")
    themes = article.get("tracked_themes", [])
    sig_score = article.get("significance_score", 0)
    tone = article.get("tone", 0)
    
    content_text = f"""
GDELT Event Alert
Title: {title}
Source: {domain}
URL: {url}
Date: {seendate}
Themes: {', '.join(themes)}
Tone: {tone} (negative = conflict/crisis)
Significance: {sig_score}
    """.strip()
    
    # Generate embedding
    try:
        embedding = embed_text(content_text)
    except Exception as exc:
        logger.error(f"Embedding failed for article '{title}': {exc}")
        return {}
    
    # Store in vector DB
    metadata = {
        "title": title,
        "url": url,
        "domain": domain,
        "seendate": seendate,
        "themes": themes,
        "tone": float(tone),
        "significance_score": sig_score,
        "language": article.get("language", ""),
        "socialimage": article.get("socialimage", 0),
    }
    
    try:
        result = store_embedding(
            source_type="gdelt_event",
            content=content_text,
            metadata=metadata,
            embedding=embedding,
            source_id=url,  # Use URL as unique source identifier
        )
        
        event_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "embedding_id": result.get("id"),
            "title": title,
            "url": url,
            "themes": themes,
            "significance_score": sig_score,
            "tone": float(tone),
        }
        
        # Log to JSONL
        with EVENT_LOG.open("a") as f:
            f.write(json.dumps(event_record) + "\n")
        
        logger.info(f"Stored event: {title} (themes: {', '.join(themes)}, score: {sig_score})")
        return event_record
        
    except Exception as exc:
        logger.error(f"Failed to store event '{title}': {exc}")
        return {}


def poll_gdelt() -> int:
    """Poll GDELT for new significant events.
    
    Returns:
        Number of new events detected
    """
    logger.info("Polling GDELT for significant events...")
    
    new_events = 0
    
    # Query each tracked theme
    for theme in TRACKED_THEMES:
        logger.debug(f"Querying theme: {theme}")
        articles = fetch_gdelt_articles(
            query=theme,
            timespan="15m",  # Last 15 minutes
            max_records=50,
        )
        
        if not articles:
            logger.debug(f"No articles found for theme: {theme}")
            continue
        
        # Filter for significance
        significant = filter_significant_events(articles)
        logger.info(f"Found {len(significant)} significant events for theme: {theme}")
        
        # Process each event
        for article in significant:
            event = process_event(article)
            if event:
                new_events += 1
        
        # Rate limit between queries
        time.sleep(2)
    
    logger.info(f"Polling complete. {new_events} new events stored.")
    return new_events


def run_monitor():
    """Run the GDELT monitor in polling loop."""
    logger.info("Starting GDELT Event Monitor...")
    logger.info(f"Tracking themes: {', '.join(TRACKED_THEMES)}")
    logger.info(f"Goldstein threshold: |{GOLDSTEIN_THRESHOLD}|")
    logger.info(f"Poll interval: {POLL_INTERVAL // 60} minutes")
    
    while True:
        try:
            poll_gdelt()
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user.")
            break
        except Exception as exc:
            logger.error(f"Unexpected error during polling: {exc}", exc_info=True)
        
        logger.info(f"Next poll in {POLL_INTERVAL // 60} minutes...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_monitor()
