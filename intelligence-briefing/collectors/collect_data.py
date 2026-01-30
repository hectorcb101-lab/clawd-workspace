#!/usr/bin/env python3
"""
Data Collection Module
Collects data from Polymarket, Yahoo Finance, and other sources
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return None, -1
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return None, -1

def collect_polymarket_data():
    """Collect trending markets from Polymarket."""
    print("📊 Collecting Polymarket data...")
    
    cmd = "cd /home/ubuntu/clawd/skills/polymarket && python3 scripts/polymarket.py trending 2>&1"
    output, code = run_command(cmd)
    
    if code != 0 or not output:
        return {"status": "failed", "data": None}
    
    # Parse the output (basic text parsing)
    markets = []
    current_market = {}
    
    for line in output.split('\n'):
        if line.startswith('🎯 **'):
            if current_market:
                markets.append(current_market)
            current_market = {
                "title": line.replace('🎯 **', '').replace('**', '').strip(),
                "markets": []
            }
        elif 'Total Volume:' in line:
            volume = line.split('$')[-1].strip() if '$' in line else "Unknown"
            current_market['volume'] = volume
        elif '•' in line and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                question = parts[0].replace('•', '').strip()
                odds = parts[1].strip()
                current_market.get('markets', []).append({
                    "question": question,
                    "odds": odds
                })
    
    if current_market:
        markets.append(current_market)
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "polymarket",
        "data": markets[:5]  # Top 5 markets
    }

def collect_finance_data():
    """Collect financial data from Yahoo Finance."""
    print("💰 Collecting market data...")
    
    symbols = [
        "^GSPC",   # S&P 500
        "^DJI",    # Dow Jones
        "^IXIC",   # NASDAQ
        "^VIX",    # VIX (volatility)
        "BTC-USD", # Bitcoin
        "ETH-USD", # Ethereum
        "GC=F",    # Gold
        "CL=F",    # Crude Oil
    ]
    
    data = []
    for symbol in symbols:
        cmd = f"python3 /home/ubuntu/clawd/skills/yahoo-finance/yf.py {symbol} 2>&1"
        output, code = run_command(cmd)
        
        if code == 0 and output:
            # Parse the output
            lines = output.strip().split('\n')
            parsed = {"symbol": symbol}
            
            for line in lines:
                if 'Price:' in line:
                    price = line.split('Price:')[-1].strip().replace('$', '').replace(',', '')
                    try:
                        parsed['price'] = float(price)
                    except:
                        parsed['price'] = price
                elif 'Change:' in line:
                    change = line.split('Change:')[-1].strip().replace('%', '')
                    try:
                        parsed['change_percent'] = float(change)
                    except:
                        parsed['change_percent'] = 0.0
            
            if 'price' in parsed:
                data.append(parsed)
    
    return {
        "status": "success" if data else "partial",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "yahoo_finance",
        "data": data
    }

def collect_sentiment_data():
    """Collect market sentiment from news."""
    print("🔍 Collecting market sentiment...")
    
    cmd = "python3 /home/ubuntu/clawd/intelligence-briefing/collectors/collect_sentiment.py 2>&1"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse JSON output - look for the JSON block
            lines = result.stdout.strip().split('\n')
            json_started = False
            json_lines = []
            
            for line in lines:
                if line.startswith('{'):
                    json_started = True
                if json_started:
                    json_lines.append(line)
            
            if json_lines:
                try:
                    return json.loads('\n'.join(json_lines))
                except:
                    pass
        
        print(f"⚠️ Sentiment collection failed: {result.stderr}", file=sys.stderr)
        return {"status": "failed", "data": []}
    except Exception as e:
        print(f"⚠️ Sentiment error: {e}", file=sys.stderr)
        return {"status": "failed", "data": []}

def collect_x_data():
    """Collect X/Twitter data via bird CLI."""
    print("🐦 Collecting X/Twitter data...")
    
    try:
        cmd = "python3 /home/ubuntu/clawd/intelligence-briefing/collectors/collect_x.py 2>&1"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse JSON output
            lines = result.stdout.strip().split('\n')
            json_started = False
            json_lines = []
            
            for line in lines:
                if line.startswith('{'):
                    json_started = True
                if json_started:
                    json_lines.append(line)
            
            if json_lines:
                try:
                    return json.loads('\n'.join(json_lines))
                except:
                    pass
        
        print(f"⚠️ X collection failed: {result.stderr}", file=sys.stderr)
        return {"status": "failed", "data": {}}
    except Exception as e:
        print(f"⚠️ X error: {e}", file=sys.stderr)
        return {"status": "failed", "data": {}}


def collect_ai_news():
    """Collect curated AI news from top accounts and searches."""
    print("🤖 Collecting curated AI news...")
    
    try:
        cmd = "python3 /home/ubuntu/clawd/intelligence-briefing/collectors/collect_ai_news.py 2>&1"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120  # Longer timeout for multiple API calls
        )
        
        if result.returncode == 0:
            # Parse JSON output - find the "Full data:" section
            output = result.stdout
            if 'Full data:' in output:
                json_part = output.split('Full data:')[1].strip()
                try:
                    return json.loads(json_part)
                except:
                    pass
            
            # Fallback: try to find any JSON
            lines = output.strip().split('\n')
            json_started = False
            json_lines = []
            
            for line in lines:
                if line.startswith('{'):
                    json_started = True
                if json_started:
                    json_lines.append(line)
            
            if json_lines:
                try:
                    return json.loads('\n'.join(json_lines))
                except:
                    pass
        
        print(f"⚠️ AI news collection failed: {result.stderr}", file=sys.stderr)
        return {"status": "failed", "data": {}}
    except Exception as e:
        print(f"⚠️ AI news error: {e}", file=sys.stderr)
        return {"status": "failed", "data": {}}


def collect_ai_articles():
    """Collect AI news articles via Exa search."""
    print("📰 Collecting AI news articles...")
    
    try:
        cmd = "python3 /home/ubuntu/clawd/intelligence-briefing/collectors/collect_ai_articles.py 2>&1"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            output = result.stdout
            if 'Full data:' in output:
                json_part = output.split('Full data:')[1].strip()
                try:
                    return json.loads(json_part)
                except:
                    pass
        
        print(f"⚠️ AI articles collection failed", file=sys.stderr)
        return {"status": "failed", "articles": []}
    except Exception as e:
        print(f"⚠️ AI articles error: {e}", file=sys.stderr)
        return {"status": "failed", "articles": []}


def collect_all_data():
    """Collect data from all sources."""
    print("🔄 Starting data collection...")
    
    results = {
        "collection_time": datetime.utcnow().isoformat(),
        "sources": {}
    }
    
    # Polymarket
    pm_data = collect_polymarket_data()
    results["sources"]["polymarket"] = pm_data
    
    # Finance
    finance_data = collect_finance_data()
    results["sources"]["finance"] = finance_data
    
    # X/Twitter (general)
    x_data = collect_x_data()
    results["sources"]["x_twitter"] = x_data
    
    # AI News (curated X accounts)
    ai_news = collect_ai_news()
    results["sources"]["ai_news"] = ai_news
    
    # AI Articles (via Exa)
    ai_articles = collect_ai_articles()
    results["sources"]["ai_articles"] = ai_articles
    
    # Sentiment (web-based fallback)
    sentiment_data = collect_sentiment_data()
    results["sources"]["sentiment"] = sentiment_data
    
    # Save to cache
    cache_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/daily_cache.json")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Data collection complete. Cached at {cache_path}")
    return results

if __name__ == "__main__":
    data = collect_all_data()
    print(json.dumps(data, indent=2))
