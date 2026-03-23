#!/usr/bin/env python3
"""
X/Twitter & Social Media Collection via Exa Search
Replaces bird CLI (cookie-auth, unreliable) with Exa web search.
"""

import subprocess
import json
from datetime import datetime, timedelta


def exa_search(query, num_results=5, hours_back=24):
    """Search via Exa through mcporter."""
    try:
        start_date = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        cmd = [
            "mcporter", "call", "exa.web_search_exa",
            f"query={query}",
            f"numResults={num_results}",
            f"startPublishedDate={start_date}",
            "type=auto"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"status": "success", "raw": result.stdout}
        return {"status": "failed", "error": result.stderr[:200]}
    except Exception as e:
        return {"status": "failed", "error": str(e)[:200]}


def collect_news():
    """Collect trending news and social discourse."""
    print("📰 Collecting news via Exa...")
    return exa_search("breaking news today world events", num_results=8, hours_back=24)


def collect_social_sentiment():
    """Collect social media sentiment on markets."""
    print("📊 Collecting market sentiment...")
    return exa_search("stock market sentiment analysis today twitter", num_results=5, hours_back=24)


def search_topic(query, n=5):
    """Search for a specific topic."""
    print(f"🔍 Searching: {query}")
    return exa_search(query, num_results=n, hours_back=48)


def collect_all_x_data():
    """Collect all social/news data for briefing."""
    print("🌐 Starting Exa-powered news collection...")

    results = {
        "collection_time": datetime.utcnow().isoformat(),
        "source": "exa_search",
        "data": {}
    }

    # General news
    results["data"]["news"] = collect_news()

    # Market sentiment
    results["data"]["sentiment"] = collect_social_sentiment()

    # Topic searches
    topics = [
        "AI artificial intelligence breakthrough",
        "crypto bitcoin ethereum market",
        "stock market rally crash",
        "geopolitics conflict sanctions"
    ]

    results["data"]["searches"] = {}
    for topic in topics:
        results["data"]["searches"][topic] = search_topic(topic, n=5)

    success_count = sum(1 for k, v in results["data"].items()
                       if isinstance(v, dict) and v.get("status") == "success")

    results["status"] = "success" if success_count >= 2 else "partial" if success_count > 0 else "failed"

    print(f"✅ Collection complete: {results['status']}")
    return results


if __name__ == "__main__":
    data = collect_all_x_data()
    print(json.dumps(data, indent=2, default=str))
