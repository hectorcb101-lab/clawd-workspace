#!/usr/bin/env python3
"""
Research Tiers System
QS (Quick Scan), DD (Deep Dive), EX (Exhaustive)
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Config
OBSIDIAN_VAULT = "/home/ubuntu/clawd/obsidian-vault"
RESEARCH_FOLDER = f"{OBSIDIAN_VAULT}/Research"
BRIEFS_FOLDER = "/home/ubuntu/clawd/research/briefs"
TRACKING_FILE = "/home/ubuntu/clawd/research/tracking.json"

# Bird auth
os.environ['AUTH_TOKEN'] = 'cd8d2c9353c747711c2bff02a017219bf000add6'
os.environ['CT0'] = 'f4ac87d75e426d8c928186078d4416530f722917009df49ff29bac2d280d5f993af2c5e9af3440803e23cb006b194041a487ff9e8eb0182e6f82cbf37bb06bce293e997e76fae47fefd24732e91842d1'

# Category detection keywords
CATEGORY_KEYWORDS = {
    'AI-ML': ['ai', 'machine learning', 'ml', 'neural', 'llm', 'gpt', 'claude', 'model', 'deep learning', 'transformer'],
    'Quantum': ['quantum', 'qubit', 'qml', 'superposition', 'entanglement'],
    'Space': ['space', 'nasa', 'rocket', 'mars', 'satellite', 'orbit', 'exoplanet', 'astrophysics'],
    'Finance': ['trading', 'quant', 'stock', 'market', 'finance', 'algorithm trading', 'backtest', 'portfolio'],
    'Tech': ['software', 'programming', 'framework', 'tool', 'api', 'cloud'],
    'Academic': ['msc', 'course', 'university', 'exam', 'study', 'research paper'],
}


def detect_category(topic):
    """Auto-detect category from topic keywords."""
    topic_lower = topic.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in topic_lower for kw in keywords):
            return category
    return 'Other'


def exa_search(query, num_results=5):
    """Search via Exa."""
    try:
        cmd = ['mcporter', 'call', 'exa.web_search_exa', 
               f'query={query}', f'numResults={num_results}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def x_search(query, n=10):
    """Search X/Twitter."""
    try:
        cmd = ['bird', 'search', query, '-n', str(n), '--plain']
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              timeout=30, env=os.environ)
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def quick_scan(topic):
    """QS: Quick Scan - 5-8 sources, chat only."""
    print(f"⚡ Quick Scan: {topic}")
    
    results = {
        'tier': 'QS',
        'topic': topic,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sources': {}
    }
    
    # News only (5 results)
    print("  📰 Searching news...")
    news = exa_search(f"{topic} news latest", 5)
    if news:
        results['sources']['news'] = news
    
    # X hot takes (5 results)
    print("  🐦 Checking X...")
    x = x_search(topic, 5)
    if x:
        results['sources']['x'] = x
    
    results['status'] = 'success' if results['sources'] else 'failed'
    return results


def deep_dive(topic):
    """DD: Deep Dive - 15-20 sources, saves to Obsidian."""
    print(f"🔬 Deep Dive: {topic}")
    
    results = {
        'tier': 'DD',
        'topic': topic,
        'category': detect_category(topic),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sources': {}
    }
    
    # News (5)
    print("  📰 Searching news...")
    news = exa_search(f"{topic} news latest 2026", 5)
    if news:
        results['sources']['news'] = news
    
    # Academic papers (5)
    print("  📚 Searching papers...")
    papers = exa_search(f"{topic} research paper arxiv 2025 2026", 5)
    if papers:
        results['sources']['papers'] = papers
    
    # Tutorials (5)
    print("  🛠️ Searching tutorials...")
    tutorials = exa_search(f"{topic} tutorial guide how to learn", 5)
    if tutorials:
        results['sources']['tutorials'] = tutorials
    
    # X experts (10)
    print("  🐦 Checking X experts...")
    x = x_search(f"{topic}", 10)
    if x:
        results['sources']['x_experts'] = x
    
    results['status'] = 'success' if results['sources'] else 'failed'
    return results


def exhaustive(topic):
    """EX: Exhaustive - 30+ sources across parallel searches."""
    print(f"🔥 Exhaustive Research: {topic}")
    
    results = {
        'tier': 'EX',
        'topic': topic,
        'category': detect_category(topic),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sources': {}
    }
    
    # Agent 1: News & developments (8)
    print("  📰 [1/5] News & developments...")
    news = exa_search(f"{topic} news latest breaking 2026", 8)
    if news:
        results['sources']['news'] = news
    
    # Agent 2: Academic papers (8)
    print("  📚 [2/5] Academic papers...")
    papers = exa_search(f"{topic} research paper arxiv academic 2025 2026", 8)
    if papers:
        results['sources']['papers'] = papers
    
    # Agent 3: Tutorials & courses (6)
    print("  🎓 [3/5] Tutorials & courses...")
    tutorials = exa_search(f"{topic} tutorial course learn beginner advanced", 6)
    if tutorials:
        results['sources']['tutorials'] = tutorials
    
    # Agent 4: X sentiment (15)
    print("  🐦 [4/5] X sentiment & experts...")
    x = x_search(f"{topic}", 15)
    if x:
        results['sources']['x_sentiment'] = x
    
    # Agent 5: Tools & frameworks (6)
    print("  🛠️ [5/5] Tools & frameworks...")
    tools = exa_search(f"{topic} tools framework library github", 6)
    if tools:
        results['sources']['tools'] = tools
    
    results['status'] = 'success' if results['sources'] else 'failed'
    return results


def generate_frontmatter(results):
    """Generate Obsidian frontmatter."""
    tags = [results['tier'].lower(), results.get('category', 'other').lower()]
    topic_tags = results['topic'].lower().split()[:3]
    tags.extend([t for t in topic_tags if len(t) > 3])
    
    return f"""---
type: research
tier: {results['tier']}
topic: "{results['topic']}"
category: {results.get('category', 'Other')}
date: {results['timestamp'][:10]}
status: {'tracking' if results['tier'] == 'EX' else 'complete'}
tags: [{', '.join(tags)}]
---

"""


def save_to_obsidian(results, content):
    """Save research to Obsidian vault."""
    category = results.get('category', 'Other')
    folder = Path(RESEARCH_FOLDER) / category
    folder.mkdir(parents=True, exist_ok=True)
    
    date_str = results['timestamp'][:10]
    topic_slug = results['topic'].replace(' ', '-').replace('/', '-')[:40]
    filename = f"{date_str}_{topic_slug}.md"
    
    filepath = folder / filename
    
    full_content = generate_frontmatter(results) + content
    
    with open(filepath, 'w') as f:
        f.write(full_content)
    
    print(f"  📁 Saved to Obsidian: {filepath}")
    return str(filepath)


def add_to_tracking(topic, category):
    """Add topic to weekly tracking (EX only)."""
    try:
        with open(TRACKING_FILE, 'r') as f:
            tracking = json.load(f)
    except:
        tracking = {"topics": [], "config": {"defaultFrequency": "weekly"}}
    
    # Check if already tracking
    existing = [t for t in tracking['topics'] if t['name'].lower() == topic.lower()]
    if existing:
        print(f"  📡 Already tracking: {topic}")
        return
    
    tracking['topics'].append({
        "name": topic,
        "category": category,
        "started": datetime.now(timezone.utc).isoformat()[:10],
        "frequency": "weekly",
        "lastCheck": datetime.now(timezone.utc).isoformat()[:10],
        "alerts": True
    })
    tracking['lastUpdated'] = datetime.now(timezone.utc).isoformat()
    
    with open(TRACKING_FILE, 'w') as f:
        json.dump(tracking, f, indent=2)
    
    print(f"  📡 Added to weekly tracking: {topic}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: research_tiers.py <QS|DD|EX> <topic>")
        sys.exit(1)
    
    tier = sys.argv[1].upper()
    topic = ' '.join(sys.argv[2:])
    
    if tier == 'QS':
        results = quick_scan(topic)
    elif tier == 'DD':
        results = deep_dive(topic)
    elif tier == 'EX':
        results = exhaustive(topic)
        add_to_tracking(topic, results.get('category', 'Other'))
    else:
        print(f"Unknown tier: {tier}")
        sys.exit(1)
    
    print(f"\n✅ {tier} complete: {len(results['sources'])} source types")
    print(json.dumps(results, indent=2, default=str))
