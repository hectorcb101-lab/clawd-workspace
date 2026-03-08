#!/usr/bin/env python3
"""
Geopolitical Event Collector
Collects major geopolitical developments using Exa search
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def run_exa_search(query, num_results=10):
    """Execute Exa search via mcporter."""
    try:
        import os
        
        cmd = [
            'mcporter', 'call', 'exa.web_search_exa',
            f'query={query}',
            f'numResults={num_results}'
        ]
        
        # Ensure HOME is set for mcporter to find its config
        env = os.environ.copy()
        if 'HOME' not in env:
            env['HOME'] = '/home/ubuntu'
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode == 0 and result.stdout:
            return result.stdout
        else:
            if result.stderr:
                print(f"⚠️ Exa search error for '{query}': {result.stderr[:100]}", file=sys.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ Exa search timeout for query: {query}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️ Error in Exa search: {e}", file=sys.stderr)
        return None

def parse_exa_output(output):
    """Parse Exa text output into structured results."""
    if not output:
        return []
    
    results = []
    current = {}
    
    for line in output.split('\n'):
        line = line.strip()
        
        if line.startswith('Title:'):
            if current and 'title' in current:
                results.append(current)
            current = {'title': line.replace('Title:', '').strip()}
        
        elif line.startswith('Author:'):
            current['author'] = line.replace('Author:', '').strip()
        
        elif line.startswith('Published Date:'):
            current['publishedDate'] = line.replace('Published Date:', '').strip()
        
        elif line.startswith('URL:'):
            current['url'] = line.replace('URL:', '').strip()
        
        elif line.startswith('Text:'):
            current['text'] = line.replace('Text:', '').strip()
        
        elif line.startswith('Score:'):
            try:
                current['score'] = float(line.replace('Score:', '').strip())
            except:
                current['score'] = 0.5
    
    if current and 'title' in current:
        results.append(current)
    
    return results

def extract_event_data(result, category):
    """Extract structured event data from Exa result."""
    event = {
        'headline': result.get('title', 'Unknown'),
        'category': category,
        'countries': extract_countries(result),
        'date': result.get('publishedDate', datetime.utcnow().isoformat()),
        'source_url': result.get('url', ''),
        'summary': result.get('text', '')[:300] + '...' if result.get('text') else result.get('title', ''),
        'score': result.get('score', 0)
    }
    return event

def extract_countries(result):
    """Extract country mentions from title and text."""
    # Common country and region keywords
    countries_regions = [
        'US', 'USA', 'United States', 'America', 'China', 'Russia', 'Iran', 'Israel',
        'Ukraine', 'Europe', 'EU', 'UK', 'Britain', 'France', 'Germany', 'Japan',
        'India', 'Taiwan', 'Korea', 'Mexico', 'Canada', 'Saudi Arabia', 'Turkey',
        'Middle East', 'Asia', 'OPEC'
    ]
    
    text = f"{result.get('title', '')} {result.get('text', '')}"
    
    mentioned = []
    for country in countries_regions:
        if country.lower() in text.lower():
            mentioned.append(country)
    
    return mentioned[:3]  # Top 3 mentions

def collect_military_conflict():
    """Collect military/conflict events."""
    print("🪖 Collecting military/conflict events...")
    
    queries = [
        "military conflict war escalation",
        "armed forces deployment combat operations",
        "defence spending military buildup"
    ]
    
    all_results = []
    for query in queries:
        output = run_exa_search(query, num_results=5)
        if output:
            results = parse_exa_output(output)
            all_results.extend(results)
    
    # Deduplicate by URL and extract
    seen_urls = set()
    events = []
    
    for result in all_results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            events.append(extract_event_data(result, 'military_conflict'))
    
    return sorted(events, key=lambda x: x['score'], reverse=True)[:5]

def collect_trade_sanctions():
    """Collect trade policy/tariff/sanctions events."""
    print("⚖️ Collecting trade/sanctions events...")
    
    queries = [
        "tariffs trade policy sanctions",
        "export controls trade restrictions",
        "trade war tariff announcement"
    ]
    
    all_results = []
    for query in queries:
        output = run_exa_search(query, num_results=5)
        if output:
            results = parse_exa_output(output)
            all_results.extend(results)
    
    seen_urls = set()
    events = []
    
    for result in all_results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            events.append(extract_event_data(result, 'trade_sanctions'))
    
    return sorted(events, key=lambda x: x['score'], reverse=True)[:5]

def collect_central_bank():
    """Collect central bank policy signals."""
    print("🏦 Collecting central bank events...")
    
    queries = [
        "Federal Reserve interest rate policy",
        "ECB BOE central bank monetary policy",
        "interest rate decision central bank"
    ]
    
    all_results = []
    for query in queries:
        output = run_exa_search(query, num_results=5)
        if output:
            results = parse_exa_output(output)
            all_results.extend(results)
    
    seen_urls = set()
    events = []
    
    for result in all_results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            events.append(extract_event_data(result, 'central_bank'))
    
    return sorted(events, key=lambda x: x['score'], reverse=True)[:5]

def collect_energy_supply():
    """Collect energy/commodity supply disruptions."""
    print("⚡ Collecting energy supply events...")
    
    queries = [
        "oil gas supply disruption pipeline",
        "energy infrastructure OPEC production",
        "commodity supply chain disruption"
    ]
    
    all_results = []
    for query in queries:
        output = run_exa_search(query, num_results=5)
        if output:
            results = parse_exa_output(output)
            all_results.extend(results)
    
    seen_urls = set()
    events = []
    
    for result in all_results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            events.append(extract_event_data(result, 'energy_supply'))
    
    return sorted(events, key=lambda x: x['score'], reverse=True)[:5]

def collect_political_transitions():
    """Collect elections/political transitions."""
    print("🗳️ Collecting political transition events...")
    
    queries = [
        "election results government change",
        "political transition leadership change",
        "policy announcement government reform"
    ]
    
    all_results = []
    for query in queries:
        output = run_exa_search(query, num_results=5)
        if output:
            results = parse_exa_output(output)
            all_results.extend(results)
    
    seen_urls = set()
    events = []
    
    for result in all_results:
        url = result.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            events.append(extract_event_data(result, 'political_transition'))
    
    return sorted(events, key=lambda x: x['score'], reverse=True)[:5]

def collect_geopolitical_events():
    """Main collection function - gathers events from all categories."""
    print("=" * 60)
    print("🌍 GEOPOLITICAL EVENT COLLECTION")
    print("=" * 60)
    
    all_events = []
    
    # Collect from each category
    all_events.extend(collect_military_conflict())
    all_events.extend(collect_trade_sanctions())
    all_events.extend(collect_central_bank())
    all_events.extend(collect_energy_supply())
    all_events.extend(collect_political_transitions())
    
    # Sort by score (relevance) and recency
    all_events.sort(key=lambda x: x['score'], reverse=True)
    
    result = {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'source': 'exa_geopolitical',
        'events': all_events[:15]  # Top 15 most relevant events
    }
    
    print(f"\n✅ Collected {len(result['events'])} geopolitical events")
    
    # Cache results
    cache_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/geopolitical_events.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

if __name__ == "__main__":
    data = collect_geopolitical_events()
    print(json.dumps(data, indent=2))
