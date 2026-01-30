#!/usr/bin/env python3
"""
X/Twitter Data Collection via bird CLI
Collects news, trending topics, and sentiment from X
"""

import subprocess
import json
import os
from datetime import datetime

# Set auth tokens
os.environ['AUTH_TOKEN'] = 'cd8d2c9353c747711c2bff02a017219bf000add6'
os.environ['CT0'] = 'f4ac87d75e426d8c928186078d4416530f722917009df49ff29bac2d280d5f993af2c5e9af3440803e23cb006b194041a487ff9e8eb0182e6f82cbf37bb06bce293e997e76fae47fefd24732e91842d1'


def run_bird(args):
    """Run bird command and return output."""
    try:
        cmd = ['bird'] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=os.environ
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return None, -1
    except Exception as e:
        print(f"Error: {e}")
        return None, -1


def collect_news():
    """Collect AI-curated news from X."""
    print("📰 Collecting X news...")
    output, code = run_bird(['news', '-n', '10', '--plain'])
    
    if code != 0:
        return {"status": "failed", "error": "bird news failed"}
    
    return {
        "status": "success",
        "type": "news",
        "raw": output
    }


def collect_home_timeline():
    """Collect home timeline for sentiment."""
    print("🏠 Collecting home timeline...")
    output, code = run_bird(['home', '-n', '15', '--plain'])
    
    if code != 0:
        return {"status": "failed", "error": "bird home failed"}
    
    return {
        "status": "success",
        "type": "home",
        "raw": output
    }


def search_topic(query, n=5):
    """Search X for a specific topic."""
    print(f"🔍 Searching X: {query}")
    output, code = run_bird(['search', query, '-n', str(n), '--plain'])
    
    if code != 0:
        return {"status": "failed", "query": query}
    
    return {
        "status": "success",
        "query": query,
        "raw": output
    }


def collect_all_x_data():
    """Collect all X data for briefing."""
    print("🐦 Starting X data collection...")
    
    results = {
        "collection_time": datetime.utcnow().isoformat(),
        "source": "x_twitter",
        "data": {}
    }
    
    # Collect news
    news = collect_news()
    results["data"]["news"] = news
    
    # Collect home timeline
    home = collect_home_timeline()
    results["data"]["home"] = home
    
    # Search key topics
    topics = [
        "AI artificial intelligence",
        "crypto bitcoin",
        "stock market",
        "geopolitics conflict"
    ]
    
    results["data"]["searches"] = {}
    for topic in topics:
        search_result = search_topic(topic, n=5)
        results["data"]["searches"][topic] = search_result
    
    # Determine overall status
    success_count = sum(1 for k, v in results["data"].items() 
                       if isinstance(v, dict) and v.get("status") == "success")
    
    results["status"] = "success" if success_count >= 2 else "partial" if success_count > 0 else "failed"
    
    print(f"✅ X collection complete: {results['status']}")
    return results


if __name__ == "__main__":
    data = collect_all_x_data()
    print(json.dumps(data, indent=2))
