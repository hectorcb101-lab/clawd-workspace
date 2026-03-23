#!/usr/bin/env python3
"""
AI News Collection via Exa Search
Pulls from AI-focused sources for quality AI news.
"""

import subprocess
import json
from datetime import datetime, timedelta

# Curated AI domains for higher quality results
AI_DOMAINS = [
    "techcrunch.com", "theverge.com", "arstechnica.com",
    "venturebeat.com", "wired.com", "theneurondaily.com",
    "artificialintelligence-news.com", "deepmind.google",
    "openai.com/blog", "anthropic.com", "huggingface.co/blog",
    "arxiv.org"
]

# Key topics to track
AI_TOPICS = [
    "large language model breakthrough",
    "AI regulation policy",
    "AI startup funding",
    "foundation model release",
    "AI safety alignment research"
]


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


def collect_ai_headlines():
    """Collect major AI news headlines."""
    print("🤖 Collecting AI headlines...")
    return exa_search("artificial intelligence news today major announcement", num_results=8, hours_back=24)


def collect_ai_research():
    """Collect notable AI research papers and breakthroughs."""
    print("📄 Collecting AI research...")
    return exa_search("new AI research paper breakthrough model", num_results=5, hours_back=72)


def collect_ai_industry():
    """Collect AI industry/business news."""
    print("💼 Collecting AI industry news...")
    return exa_search("AI company funding acquisition partnership deal", num_results=5, hours_back=48)


def collect_all_ai_news():
    """Collect all AI news for briefing."""
    print("🧠 Starting AI news collection via Exa...")

    results = {
        "collection_time": datetime.utcnow().isoformat(),
        "source": "exa_search",
        "data": {}
    }

    results["data"]["headlines"] = collect_ai_headlines()
    results["data"]["research"] = collect_ai_research()
    results["data"]["industry"] = collect_ai_industry()

    # Topic-specific deep dives
    results["data"]["topics"] = {}
    for topic in AI_TOPICS:
        results["data"]["topics"][topic] = exa_search(topic, num_results=3, hours_back=48)

    success_count = sum(1 for k, v in results["data"].items()
                       if isinstance(v, dict) and v.get("status") == "success")

    results["status"] = "success" if success_count >= 2 else "partial" if success_count > 0 else "failed"

    print(f"✅ AI news collection complete: {results['status']}")
    return results


if __name__ == "__main__":
    data = collect_all_ai_news()
    print(json.dumps(data, indent=2, default=str))
