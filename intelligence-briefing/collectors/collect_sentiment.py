#!/usr/bin/env python3
"""
Market Sentiment Collection via Exa Search
Analyzes sentiment from recent news headlines
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def analyze_sentiment(text):
    """Sentiment analysis using keyword scoring."""
    
    bullish = ['rally', 'surge', 'soar', 'breakthrough', 'gains', 'profit', 'bullish', 
               'optimistic', 'strong', 'recovery', 'breakout', 'rising', 'higher', 'bounce']
    
    bearish = ['crash', 'plunge', 'drop', 'fall', 'decline', 'bearish', 'pessimistic',
               'weak', 'trouble', 'concern', 'warning', 'losing', 'losses', 'lower', 'slump']
    
    fearful = ['fear', 'panic', 'volatile', 'uncertain', 'risk', 'danger', 'warning', 
               'crisis', 'threat', 'anxious', 'worried']
    
    text_lower = text.lower()
    
    bull_score = sum(1 for word in bullish if word in text_lower)
    bear_score = sum(1 for word in bearish if word in text_lower)
    fear_score = sum(1 for word in fearful if text_lower)
    
    if bear_score > bull_score:
        return 'bearish'
    elif bull_score > bear_score:
        return 'bullish'
    elif fear_score > 0:
        return 'fearful'
    return 'neutral'

def search_topic(query):
    """Search Exa for topic and parse results."""
    try:
        cmd = ['mcporter', 'call', 'exa.web_search_exa', f'query={query}', 'numResults=5']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode != 0:
            return []
        
        # Parse output
        articles = []
        lines = result.stdout.split('\n')
        current = {}
        
        for line in lines:
            if line.startswith('Title:'):
                if current:
                    articles.append(current)
                current = {'title': line.replace('Title:', '').strip()}
            elif line.startswith('URL:') and current:
                current['url'] = line.replace('URL:', '').strip()
        
        if current:
            articles.append(current)
        
        return articles
        
    except Exception as e:
        print(f"Error searching {query}: {e}")
        return []

def collect_sentiment():
    """Collect sentiment across key topics."""
    print("🔍 Collecting market sentiment...")
    
    topics = [
        {'name': 'Crypto', 'query': 'bitcoin crypto today'},
        {'name': 'Stocks', 'query': 'stock market today'},
        {'name': 'Geopolitics', 'query': 'Iran geopolitical'}
    ]
    
    results = []
    
    for topic in topics:
        articles = search_topic(topic['query'])
        
        if not articles:
            continue
        
        sentiments = []
        for article in articles[:3]:
            title = article.get('title', '')
            sentiment = analyze_sentiment(title)
            sentiments.append(sentiment)
            
        # Count sentiments
        from collections import Counter
        counts = Counter(sentiments)
        
        # Aggregate
        if counts:
            aggregate = counts.most_common(1)[0][0]
        else:
            aggregate = 'neutral'
        
        results.append({
            'topic': topic['name'],
            'sentiment': aggregate,
            'breakdown': dict(counts),
            'sample_headlines': [a['title'][:100] for a in articles[:2]]
        })
    
    return {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'source': 'sentiment',
        'data': results
    }

if __name__ == "__main__":
    data = collect_sentiment()
    print(json.dumps(data, indent=2))
