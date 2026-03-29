#!/usr/bin/env python3
"""Geopolitical news feed collector for Atlas Intel.

Searches for maritime chokepoint, energy, sanctions, and conflict news
via Exa (mcporter), outputs structured events to dashboard/data/geopolitical.json,
and stores embeddings in Supabase.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Ensure atlas_intel package is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from atlas_intel.embedder import embed_text
from atlas_intel.store import store_embedding

logger = logging.getLogger("atlas_intel.geopolitical_feed")

DATA_DIR = PROJECT_ROOT / "dashboard" / "data"
OUTPUT_FILE = DATA_DIR / "geopolitical.json"

# Search topics tuned for maritime/energy intelligence
SEARCH_QUERIES = [
    "Strait of Hormuz shipping disruption military",
    "Suez Canal blockage shipping delay",
    "shipping disruptions maritime chokepoint closure",
    "oil supply disruption OPEC production cut",
    "sanctions oil shipping trade restrictions",
    "military conflict near shipping lanes naval",
    "trade war tariffs shipping commodities",
    "central bank interest rate decision oil prices",
    "Bab el-Mandeb Houthi Red Sea shipping",
    "Malacca Strait maritime security",
]

# Region detection keywords
REGION_MAP = {
    "hormuz": "Strait of Hormuz",
    "persian gulf": "Strait of Hormuz",
    "suez": "Suez Canal",
    "red sea": "Bab-el-Mandeb",
    "bab el-mandeb": "Bab-el-Mandeb",
    "bab-el-mandeb": "Bab-el-Mandeb",
    "houthi": "Bab-el-Mandeb",
    "malacca": "Strait of Malacca",
    "singapore": "Strait of Malacca",
    "panama": "Panama Canal",
    "turkish strait": "Turkish Straits",
    "bosphorus": "Turkish Straits",
    "dardanelles": "Turkish Straits",
    "danish strait": "Danish Straits",
}

COMMODITY_KEYWORDS = {
    "oil": "crude_oil",
    "crude": "crude_oil",
    "petroleum": "crude_oil",
    "lng": "natural_gas",
    "natural gas": "natural_gas",
    "grain": "grain",
    "wheat": "grain",
    "container": "containers",
    "shipping": "shipping",
    "gold": "gold",
}

SEVERITY_KEYWORDS = {
    "critical": ("closure", "blockade", "war", "attack", "strike", "bomb", "explosion", "sunk"),
    "high": ("disruption", "sanctions", "military", "conflict", "threat", "escalat", "suspend"),
    "medium": ("delay", "reroute", "tension", "warning", "buildup", "exercise", "tariff"),
    "low": ("monitor", "report", "analysis", "forecast", "decision", "policy"),
}


def run_exa_search(query: str, num_results: int = 5) -> str | None:
    """Execute Exa search via mcporter."""
    try:
        env = os.environ.copy()
        env.setdefault("HOME", "/home/ubuntu")
        env.setdefault("MCPORTER_CONFIG", "/home/ubuntu/clawd/config/mcporter.json")
        result = subprocess.run(
            ["mcporter", "call", "exa", "web_search_exa",
             f"query={query}", f"numResults={num_results}"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        return result.stdout if result.returncode == 0 and result.stdout else None
    except Exception as e:
        logger.warning("Exa search failed for %r: %s", query, e)
        return None


def parse_exa_output(output: str) -> list[dict]:
    """Parse mcporter Exa text output into result dicts."""
    if not output:
        return []
    results = []
    current: dict = {}
    collecting_highlights = False

    for line in output.split("\n"):
        stripped = line.strip()

        if stripped.startswith("Title:"):
            if current.get("title"):
                results.append(current)
            current = {"title": stripped[6:].strip()}
            collecting_highlights = False
        elif stripped.startswith("URL:"):
            current["url"] = stripped[4:].strip()
            collecting_highlights = False
        elif stripped.startswith("Published Date:") or stripped.startswith("Published:"):
            val = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
            current["published"] = val
            collecting_highlights = False
        elif stripped.startswith("Score:"):
            try:
                current["score"] = float(stripped[6:].strip())
            except ValueError:
                pass
            collecting_highlights = False
        elif stripped.startswith("Highlights:"):
            current.setdefault("text", "")
            collecting_highlights = True
        elif stripped.startswith("---"):
            collecting_highlights = False
        elif collecting_highlights and stripped:
            current["text"] = (current.get("text", "") + " " + stripped).strip()
        elif stripped.startswith("Author:"):
            current["author"] = stripped[7:].strip()

    if current.get("title"):
        results.append(current)
    return results


def detect_regions(text: str) -> list[str]:
    lower = text.lower()
    return list({v for k, v in REGION_MAP.items() if k in lower})


def detect_commodities(text: str) -> list[str]:
    lower = text.lower()
    return sorted({v for k, v in COMMODITY_KEYWORDS.items() if k in lower})


def detect_severity(text: str) -> str:
    lower = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return level
    return "low"


def event_id(title: str, url: str) -> str:
    return hashlib.sha256(f"{title}|{url}".encode()).hexdigest()[:16]


def collect_events() -> list[dict]:
    """Run all searches and return structured events."""
    seen_urls: set[str] = set()
    events: list[dict] = []

    for query in SEARCH_QUERIES:
        output = run_exa_search(query, num_results=5)
        for r in parse_exa_output(output):
            url = r.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            full_text = f"{r.get('title', '')} {r.get('text', '')}"
            regions = detect_regions(full_text)
            commodities = detect_commodities(full_text)
            severity = detect_severity(full_text)

            events.append({
                "id": event_id(r.get("title", ""), url),
                "title": r.get("title", ""),
                "summary": (r.get("text", "") or r.get("title", ""))[:500],
                "regions": regions,
                "commodities": commodities,
                "severity": severity,
                "source_url": url,
                "published": r.get("published", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "score": r.get("score", 0),
            })

    # Sort by severity then score
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    events.sort(key=lambda e: (sev_order.get(e["severity"], 4), -e.get("score", 0)))
    return events[:30]


def embed_and_store(events: list[dict]) -> int:
    """Embed events and store in Supabase. Returns count stored."""
    stored = 0
    for ev in events:
        try:
            text = f"{ev['title']}. {ev['summary']}"
            embedding = embed_text(text)
            store_embedding(
                source_type="geopolitical_event",
                content=text,
                metadata={
                    "regions": ev["regions"],
                    "commodities": ev["commodities"],
                    "severity": ev["severity"],
                    "source_url": ev["source_url"],
                    "event_id": ev["id"],
                },
                embedding=embedding,
                source_id=ev["id"],
            )
            stored += 1
        except Exception as e:
            logger.warning("Failed to embed/store event %s: %s", ev["id"], e)
    return stored


def save_output(events: list[dict]) -> None:
    """Write geopolitical.json for dashboard consumption."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "status": "online",
        "updated": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events),
        "events": events,
    }
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    logger.info("Wrote %d events to %s", len(events), OUTPUT_FILE)


def run() -> None:
    """Main entry point: collect, embed, save."""
    logger.info("Starting geopolitical feed collection")
    events = collect_events()
    logger.info("Collected %d events", len(events))

    if events:
        stored = embed_and_store(events)
        logger.info("Embedded and stored %d events", stored)

    save_output(events)
    logger.info("Geopolitical feed complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    run()
