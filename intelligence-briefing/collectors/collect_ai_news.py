#!/usr/bin/env python3
"""
AI News Collection - Curated Sources
Pulls from top AI accounts and targeted searches for quality AI news
"""

import subprocess
import json
import os
from datetime import datetime, timezone

# Auth tokens
os.environ['AUTH_TOKEN'] = 'cd8d2c9353c747711c2bff02a017219bf000add6'
os.environ['CT0'] = 'f4ac87d75e426d8c928186078d4416530f722917009df49ff29bac2d280d5f993af2c5e9af3440803e23cb006b194041a487ff9e8eb0182e6f82cbf37bb06bce293e997e76fae47fefd24732e91842d1'

# Curated AI thought leaders and news accounts
AI_ACCOUNTS = [
    # AI Labs & Companies
    "@AnthropicAI",      # Claude
    "@OpenAI",           # GPT
    "@GoogleDeepMind",   # Gemini/DeepMind
    "@xaboratory",       # xAI / Grok
    "@MetaAI",           # Llama
    
    # Key Researchers & Thought Leaders
    "@AndrewYNg",        # Andrew Ng - DeepLearning.AI
    "@ylecun",           # Yann LeCun - Meta AI
    "@kabornik",         # Andrej Karpathy
    "@sama",             # Sam Altman
    "@AmandaAskell",     # Anthropic alignment
    "@DarioAmodei",      # Anthropic CEO
    
    # AI News & Analysis
    "@TheAIGRID",        # AI news aggregator
    "@ai_breakfast",     # AI morning news
    "@_akhaliq",         # ML papers/news
    
    # Tools & Dev
    "@LangChainAI",      # LangChain
    "@llaboratories",    # AI tooling
]

# Targeted search queries for breaking news
AI_SEARCH_QUERIES = [
    "Claude Anthropic new",
    "GPT-5 OR GPT5 OR o3",
    "Gemini Google new model",
    "AI breakthrough research",
    "LLM benchmark SOTA",
]


def run_bird(args):
    """Run bird command and return output."""
    try:
        cmd = ['bird'] + args + ['--plain']
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


def get_account_tweets(handle, n=3):
    """Get recent tweets from an account."""
    output, code = run_bird(['user-tweets', handle, '-n', str(n)])
    if code != 0:
        return None
    return output


def search_ai_news(query, n=5):
    """Search for AI news on a topic."""
    output, code = run_bird(['search', query, '-n', str(n)])
    if code != 0:
        return None
    return output


def parse_tweets(raw_output):
    """Parse bird output into structured tweets."""
    if not raw_output:
        return []
    
    tweets = []
    current = {}
    
    for line in raw_output.split('\n'):
        line = line.strip()
        
        if line.startswith('@') and ' (' in line and '):' in line:
            # New tweet starting
            if current and 'handle' in current:
                tweets.append(current)
            
            # Parse handle and name
            parts = line.split(' (')
            handle = parts[0]
            name_rest = parts[1] if len(parts) > 1 else ""
            name = name_rest.split('):')[0] if '):' in name_rest else ""
            
            current = {
                'handle': handle,
                'name': name,
                'text': '',
                'url': '',
                'date': ''
            }
            
            # Get tweet text (after the ): )
            if '):' in line:
                text_start = line.index('):') + 2
                current['text'] = line[text_start:].strip()
        
        elif line.startswith('date:'):
            current['date'] = line.replace('date:', '').strip()
        
        elif line.startswith('url:'):
            current['url'] = line.replace('url:', '').strip()
        
        elif line.startswith('─') or line == '':
            continue
        
        elif current and 'handle' in current and not line.startswith(('PHOTO:', 'VIDEO:', '>')):
            # Continuation of tweet text
            if current['text']:
                current['text'] += ' ' + line
            else:
                current['text'] = line
    
    # Don't forget last tweet
    if current and 'handle' in current:
        tweets.append(current)
    
    return tweets


def collect_ai_news():
    """Collect comprehensive AI news from curated sources."""
    print("🤖 Collecting AI news from curated sources...")
    
    results = {
        'collection_time': datetime.now(timezone.utc).isoformat(),
        'source': 'ai_news_curated',
        'accounts': {},
        'searches': {},
        'highlights': []
    }
    
    # Collect from key accounts (top 8 to keep it fast)
    priority_accounts = AI_ACCOUNTS[:8]
    
    for handle in priority_accounts:
        print(f"  📡 {handle}...")
        raw = get_account_tweets(handle, n=3)
        if raw:
            tweets = parse_tweets(raw)
            if tweets:
                results['accounts'][handle] = tweets
    
    # Targeted searches
    for query in AI_SEARCH_QUERIES[:3]:  # Top 3 searches
        print(f"  🔍 Searching: {query[:30]}...")
        raw = search_ai_news(query, n=5)
        if raw:
            tweets = parse_tweets(raw)
            if tweets:
                results['searches'][query] = tweets
    
    # Extract highlights (most important items)
    all_tweets = []
    for handle, tweets in results['accounts'].items():
        for t in tweets:
            t['source'] = handle
            all_tweets.append(t)
    
    # Prioritize tweets from major labs
    major_labs = ['@AnthropicAI', '@OpenAI', '@GoogleDeepMind', '@AndrewYNg', '@sama']
    highlights = [t for t in all_tweets if t.get('source') in major_labs][:5]
    results['highlights'] = highlights
    
    # Status
    account_count = len(results['accounts'])
    search_count = len(results['searches'])
    results['status'] = 'success' if account_count >= 3 else 'partial' if account_count > 0 else 'failed'
    
    print(f"✅ AI news collected: {account_count} accounts, {search_count} searches")
    return results


def format_ai_news_summary(data):
    """Format AI news into readable summary for briefing."""
    lines = ["🤖 **AI NEWS HIGHLIGHTS**", ""]
    
    # Highlights from major sources
    if data.get('highlights'):
        for tweet in data['highlights'][:5]:
            handle = tweet.get('source', tweet.get('handle', ''))
            text = tweet.get('text', '')[:200]
            url = tweet.get('url', '')
            
            if text:
                lines.append(f"**{handle}**")
                lines.append(f"{text}")
                if url:
                    lines.append(f"🔗 {url}")
                lines.append("")
    
    # Search findings
    if data.get('searches'):
        lines.append("📰 **BREAKING**")
        for query, tweets in list(data['searches'].items())[:2]:
            if tweets:
                t = tweets[0]
                lines.append(f"• {t.get('text', '')[:150]}")
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    data = collect_ai_news()
    print("\n" + "="*60)
    print(format_ai_news_summary(data))
    print("="*60)
    print("\nFull data:")
    print(json.dumps(data, indent=2, default=str))
