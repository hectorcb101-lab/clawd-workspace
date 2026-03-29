#!/usr/bin/env python3
"""
Atlas Intel — Live News Feed Tracker
Fetches breaking news from multiple free RSS/API sources.
Outputs news_live.json with geolocated news events for globe display.

Sources (all free):
- GDELT Project (global event data)
- Google News RSS (headlines by region)
- Al Jazeera RSS
- BBC RSS
- Reuters RSS
"""

import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [NEWS] %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "dashboard" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ========== RSS FEEDS ==========
RSS_FEEDS = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "https://www.rss-bridge.org/bridge01/?action=display&bridge=Reuters&feed=world&format=Atom",
    "NPR World": "https://feeds.npr.org/1004/rss.xml",
    "France24": "https://www.france24.com/en/rss",
}

# ========== GDELT ==========
GDELT_API = "http://api.gdeltproject.org/api/v2/doc/doc"

# ========== GEOLOCATIONS FOR NEWS KEYWORDS ==========
# Map common location keywords to approximate coordinates
LOCATION_MAP = {
    # Countries
    "ukraine": (48.38, 31.17), "russia": (55.75, 37.62), "china": (39.90, 116.41),
    "taiwan": (25.03, 121.57), "israel": (31.77, 35.21), "gaza": (31.35, 34.31),
    "iran": (35.69, 51.39), "north korea": (39.03, 125.75), "south korea": (37.57, 126.98),
    "japan": (35.68, 139.65), "india": (28.61, 77.21), "pakistan": (33.69, 73.04),
    "syria": (33.51, 36.31), "iraq": (33.31, 44.37), "yemen": (15.37, 44.21),
    "lebanon": (33.89, 35.50), "turkey": (39.93, 32.85), "egypt": (30.04, 31.24),
    "saudi arabia": (24.71, 46.68), "afghanistan": (34.53, 69.17),
    "united states": (38.91, -77.04), "us": (38.91, -77.04), "america": (38.91, -77.04),
    "united kingdom": (51.51, -0.13), "uk": (51.51, -0.13), "britain": (51.51, -0.13),
    "france": (48.86, 2.35), "germany": (52.52, 13.41), "italy": (41.90, 12.50),
    "spain": (40.42, -3.70), "poland": (52.23, 21.01), "romania": (44.43, 26.10),
    "mexico": (19.43, -99.13), "brazil": (23.55, -46.63), "argentina": (-34.60, -58.38),
    "colombia": (4.71, -74.07), "venezuela": (10.49, -66.90),
    "nigeria": (9.08, 7.49), "south africa": (-33.93, 18.42), "ethiopia": (9.03, 38.75),
    "kenya": (-1.29, 36.82), "sudan": (15.59, 32.53), "libya": (32.90, 13.18),
    "australia": (-33.87, 151.21), "indonesia": (-6.21, 106.85),
    "philippines": (14.60, 120.98), "vietnam": (21.03, 105.85), "thailand": (13.76, 100.50),
    "myanmar": (16.87, 96.20), "malaysia": (3.14, 101.69), "singapore": (1.35, 103.82),
    # Cities
    "kyiv": (50.45, 30.52), "moscow": (55.76, 37.62), "beijing": (39.90, 116.41),
    "taipei": (25.03, 121.57), "jerusalem": (31.77, 35.23), "tehran": (35.69, 51.39),
    "pyongyang": (39.03, 125.75), "washington": (38.91, -77.04), "london": (51.51, -0.13),
    "paris": (48.86, 2.35), "berlin": (52.52, 13.41), "brussels": (50.85, 4.35),
    "new york": (40.71, -74.01), "pentagon": (38.87, -77.06), "kremlin": (55.75, 37.62),
    "white house": (38.90, -77.04), "nato": (50.88, 4.42),
    "strait of hormuz": (26.57, 56.25), "south china sea": (14.50, 114.00),
    "taiwan strait": (24.50, 119.50), "suez canal": (30.43, 32.34),
    "crimea": (44.95, 34.10), "donbas": (48.00, 37.80), "kharkiv": (49.99, 36.23),
}

# Keywords for categorising news
CATEGORY_KEYWORDS = {
    "conflict": ["war", "attack", "bomb", "missile", "strike", "military", "troops", "combat", "battle", "killed", "casualties", "airstrike", "invasion", "shelling"],
    "geopolitical": ["sanctions", "diplomacy", "summit", "treaty", "alliance", "nato", "un", "g7", "g20", "trade war", "tariff", "embargo"],
    "terrorism": ["terror", "terrorist", "isis", "al-qaeda", "extremist", "bombing", "hostage"],
    "economic": ["economy", "inflation", "recession", "gdp", "central bank", "interest rate", "stock market", "oil price", "energy crisis"],
    "humanitarian": ["refugee", "famine", "humanitarian", "aid", "disaster", "flood", "earthquake", "drought", "displacement"],
    "cyber": ["cyber", "hack", "ransomware", "data breach", "cybersecurity"],
    "nuclear": ["nuclear", "uranium", "enrichment", "missile test", "icbm", "warhead"],
    "protest": ["protest", "demonstration", "riot", "unrest", "civil", "uprising"],
}


def geolocate_article(title: str, description: str = "") -> tuple[float, float] | None:
    """Try to extract location from article text."""
    text = f"{title} {description}".lower()
    for location, coords in sorted(LOCATION_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if location in text:
            return coords
    return None


def categorise_article(title: str, description: str = "") -> str:
    """Categorise article by content."""
    text = f"{title} {description}".lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"


def severity_from_category(category: str, title: str) -> str:
    """Estimate severity."""
    title_lower = title.lower()
    if any(w in title_lower for w in ["breaking", "urgent", "emergency", "killed", "attack", "war"]):
        return "critical"
    if category in ("conflict", "terrorism", "nuclear"):
        return "high"
    if category in ("geopolitical", "protest", "cyber"):
        return "medium"
    return "low"


def fetch_rss_feed(name: str, url: str) -> list:
    """Fetch and parse an RSS feed."""
    articles = []
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "AtlasIntel/1.0"})
        if resp.status_code != 200:
            logger.warning(f"{name}: HTTP {resp.status_code}")
            return []

        root = ET.fromstring(resp.content)

        # Handle RSS 2.0
        items = root.findall('.//item')
        # Handle Atom
        if not items:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            items = root.findall('.//atom:entry', ns)

        for item in items[:30]:  # Max 30 per feed
            title = ""
            desc = ""
            link = ""
            pub_date = ""

            # RSS 2.0
            t = item.find('title')
            if t is not None and t.text:
                title = t.text.strip()
            d = item.find('description')
            if d is not None and d.text:
                desc = re.sub(r'<[^>]+>', '', d.text).strip()[:300]
            l = item.find('link')
            if l is not None and l.text:
                link = l.text.strip()
            p = item.find('pubDate')
            if p is not None and p.text:
                pub_date = p.text.strip()

            # Atom fallback
            if not title:
                t = item.find('{http://www.w3.org/2005/Atom}title')
                if t is not None and t.text:
                    title = t.text.strip()
            if not link:
                l = item.find('{http://www.w3.org/2005/Atom}link')
                if l is not None:
                    link = l.get('href', '')
            if not desc:
                s = item.find('{http://www.w3.org/2005/Atom}summary')
                if s is not None and s.text:
                    desc = re.sub(r'<[^>]+>', '', s.text).strip()[:300]

            if not title:
                continue

            coords = geolocate_article(title, desc)
            category = categorise_article(title, desc)
            severity = severity_from_category(category, title)

            article = {
                "title": title,
                "description": desc[:200],
                "source": name,
                "url": link,
                "published": pub_date,
                "category": category,
                "severity": severity,
            }

            if coords:
                article["lat"] = coords[0]
                article["lon"] = coords[1]
                article["lng"] = coords[1]
                article["geolocated"] = True
            else:
                article["geolocated"] = False

            articles.append(article)

    except Exception as e:
        logger.warning(f"{name}: {e}")

    return articles


def fetch_gdelt_news() -> list:
    """Fetch recent news from GDELT API."""
    articles = []
    queries = [
        "military OR conflict OR attack",
        "protest OR unrest OR riot",
        "nuclear OR missile OR weapons",
        "sanctions OR diplomacy OR summit",
    ]

    for query in queries:
        try:
            params = {
                "query": query,
                "mode": "artlist",
                "maxrecords": 50,
                "format": "json",
                "sort": "datedesc",
                "timespan": "24h",
            }
            resp = requests.get(GDELT_API, params=params, timeout=15)
            if resp.status_code != 200:
                continue

            data = resp.json()
            for art in data.get("articles", [])[:30]:
                title = art.get("title", "")
                url = art.get("url", "")
                domain = art.get("domain", "")
                seendate = art.get("seendate", "")

                if not title:
                    continue

                coords = geolocate_article(title)
                category = categorise_article(title)
                severity = severity_from_category(category, title)

                article = {
                    "title": title,
                    "description": "",
                    "source": f"GDELT ({domain})",
                    "url": url,
                    "published": seendate,
                    "category": category,
                    "severity": severity,
                }

                if coords:
                    article["lat"] = coords[0]
                    article["lon"] = coords[1]
                    article["lng"] = coords[1]
                    article["geolocated"] = True
                else:
                    article["geolocated"] = False

                articles.append(article)

            time.sleep(0.5)

        except Exception as e:
            logger.warning(f"GDELT query '{query[:30]}': {e}")

    return articles


def main():
    logger.info("=== Atlas Intel News Tracker ===")

    all_articles = []

    # Fetch RSS feeds
    for name, url in RSS_FEEDS.items():
        logger.info(f"Fetching {name}...")
        articles = fetch_rss_feed(name, url)
        all_articles.extend(articles)
        logger.info(f"  → {len(articles)} articles")
        time.sleep(0.3)

    # Fetch GDELT
    logger.info("Fetching GDELT news...")
    gdelt = fetch_gdelt_news()
    all_articles.extend(gdelt)
    logger.info(f"  → {len(gdelt)} articles from GDELT")

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for a in all_articles:
        title_key = re.sub(r'[^a-z0-9]', '', a["title"].lower())[:60]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(a)

    # Separate geolocated vs non-geolocated
    geolocated = [a for a in unique if a.get("geolocated")]
    non_geo = [a for a in unique if not a.get("geolocated")]

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    geolocated.sort(key=lambda a: severity_order.get(a["severity"], 4))
    non_geo.sort(key=lambda a: severity_order.get(a["severity"], 4))

    # Stats
    by_category = {}
    by_severity = {}
    by_source = {}
    for a in unique:
        by_category[a["category"]] = by_category.get(a["category"], 0) + 1
        by_severity[a["severity"]] = by_severity.get(a["severity"], 0) + 1
        src = a["source"].split(" (")[0]
        by_source[src] = by_source.get(src, 0) + 1

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(unique),
        "geolocated_count": len(geolocated),
        "breaking_count": sum(1 for a in unique if a["severity"] == "critical"),
        "by_category": by_category,
        "by_severity": by_severity,
        "by_source": by_source,
        "geolocated_articles": geolocated[:200],
        "headlines": non_geo[:100],
    }

    out_path = DATA_DIR / "news_live.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"\n=== NEWS FEED COMPLETE ===")
    logger.info(f"Total unique articles: {len(unique)}")
    logger.info(f"Geolocated: {len(geolocated)}")
    logger.info(f"Breaking/Critical: {output['breaking_count']}")
    logger.info(f"By category: {json.dumps(by_category)}")
    logger.info(f"By source: {json.dumps(by_source)}")
    logger.info(f"Output: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
