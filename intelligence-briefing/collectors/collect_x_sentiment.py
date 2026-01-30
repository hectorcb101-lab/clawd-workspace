#!/usr/bin/env python3
"""
Social Sentiment Collection via Exa Search
Collects trending topics and sentiment analysis from news and social discussion
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def run_mcporter(tool, args):
    """Run mcporter command and return JSON output."""
    try:
        cmd = ['mcporter', 'call', f'exa.{tool}'] + args + ['--output', 'json']
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Try to parse JSON from output
            try:
                # Exa returns results as text, try to extract JSON
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('{') or line.startswith('['):
                        return json.loads(line)
                # If no JSON found, return raw
                return {"raw": result.stdout, "status": "success"}
            except:
                return {"raw": result.stdout, "status": "success"}
        else:
            return {"status": "failed", "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def analyze_sentiment(text):
    """Simple sentiment analysis using keyword scoring."""
    
    # Bullish/Positive keywords
    bullish_words = [
        'bullish', 'buy', 'buying', 'long', 'calls', 'moon', 'pump', 'breakout', 
        'rally', 'surge', 'soaring', 'optimistic', 'confident', 'upbeat',
        'strength', 'strong', 'winning', 'gains', 'profit', 'higher', 'rising',
        'recovery', 'bounce', 'breakthrough', 'positive', 'good news'
    ]
    
    # Bearish/Negative keywords
    bearish_words = [
        'bearish', 'sell', 'selling', 'short', 'puts', 'dump', 'crash', 'breakdown',
        'collapse', 'plunge', 'falling', 'pessimistic', 'worried', 'concern',
        'weakness', 'weak', 'losing', 'losses', 'lower', 'drop', 'decline',
        'slump', 'downturn', 'trouble', 'negative', 'bad news'
    ]
    
    # Fear/Uncertainty keywords
    fear_words = [
        'fear', 'scared', 'panic', 'uncertain', 'anxiety', 'anxious', 'worried',
        'risk', 'danger', 'warning', 'alert', 'concerned', 'nervous', 'volatile',
        'volatility', 'unstable', 'crisis', 'threat'
    ]
    
    text_lower = text.lower()
    
    bullish_score = sum(1 for word in bullish_words if word in text_lower)
    bearish_score = sum(1 for word in bearish_words if word in text_lower)
    fear_score = sum(1 for word in fear_words if word in text_lower)
    
    total = bullish_score + bearish_score + fear_score
    
    if total == 0:
        return {'sentiment': 'neutral', 'confidence': 'low', 'scores': {}}
    
    # Calculate scores
    sentiment_scores = {
        'bullish': bullish_score,
        'bearish': bearish_score,
        'fear': fear_score
    }
    
    # Determine dominant sentiment
    if bullish_score > bearish_score and bullish_score > fear_score:
        sentiment = 'bullish'
    elif bearish_score > bullish_score and bearish_score > fear_score:
        sentiment = 'bearish'
    elif fear_score > 0 and (bearish_score > 0 or fear_score >= bullish_score):
        sentiment = 'fearful'
    else:
        sentiment = 'mixed'
    
    confidence = 'high' if total >= 5 else 'moderate' if total >= 3 else 'low'
    
    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'scores': sentiment_scores,
        'total_signals': total
    }

def search_topic_sentiment(topic, category='news'):
    """Search for sentiment on a specific topic."""
    print(f"🔍 Searching {category} for: {topic}")
    
    # Yesterday for filtering
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    args = [
        f'query={topic}',
        'numResults=5'
    ]
    
    # Simple web search (most reliable)
    result = run_mcporter('web_search_exa', args)
    return result

def collect_sentiment():
    """Collect sentiment on key topics."""
    print("🔍 Collecting market sentiment from web sources...")
    
    # Topics to track
    topics = [
        {
            'name': 'Crypto Markets',
            'query': 'bitcoin OR crypto crash OR rally today'
        },
        {
            'name': 'Stock Markets',
            'query': 'stock market OR SPY OR nasdaq today'
        },
        {
            'name': 'Geopolitics',
            'query': 'Iran OR geopolitical risk OR conflict'
        }
    ]
    
    sentiment_data = []
    
    for topic_config in topics:
        result = search_topic_sentiment(topic_config['query'])
        
        if result.get('status') == 'failed':
            print(f"⚠️ Failed to fetch {topic_config['name']}")
            continue
        
        # Extract and analyze articles
        topic_sentiment = {
            'topic': topic_config['name'],
            'articles': [],
            'aggregate_sentiment': 'neutral',
            'sentiment_breakdown': {}
        }
        
        # Parse raw output if JSON parsing failed
        raw_text = result.get('raw', '')
        if raw_text:
            # Extract title and text from raw output
            lines = raw_text.split('\n')
            current_article = {}
            
            for line in lines:
                if line.startswith('Title:'):
                    if current_article and 'title' in current_article:
                        # Analyze and store previous article
                        combined_text = current_article.get('title', '') + ' ' + current_article.get('text', '')
                        sentiment = analyze_sentiment(combined_text)
                        
                        topic_sentiment['articles'].append({
                            'title': current_article['title'][:150],
                            'sentiment': sentiment['sentiment'],
                            'confidence': sentiment['confidence'],
                            'url': current_article.get('url', '')
                        })
                    
                    current_article = {'title': line.replace('Title:', '').strip()}
                
                elif line.startswith('URL:'):
                    current_article['url'] = line.replace('URL:', '').strip()
                
                elif line.startswith('Text:'):
                    current_article['text'] = line.replace('Text:', '').strip()[:500]
            
            # Don't forget last article
            if current_article and 'title' in current_article:
                combined_text = current_article.get('title', '') + ' ' + current_article.get('text', '')
                sentiment = analyze_sentiment(combined_text)
                
                topic_sentiment['articles'].append({
                    'title': current_article['title'][:150],
                    'sentiment': sentiment['sentiment'],
                    'confidence': sentiment['confidence'],
                    'url': current_article.get('url', '')
                })
        
        # Aggregate sentiment for topic
        if topic_sentiment['articles']:
            from collections import Counter
            sentiments = [a['sentiment'] for a in topic_sentiment['articles']]
            sentiment_counts = Counter(sentiments)
            
            most_common = sentiment_counts.most_common(1)[0][0]
            topic_sentiment['aggregate_sentiment'] = most_common
            topic_sentiment['sentiment_breakdown'] = dict(sentiment_counts)
        
        if topic_sentiment['articles']:  # Only add if we got data
            sentiment_data.append(topic_sentiment)
    
    return {
        'status': 'success' if sentiment_data else 'partial',
        'timestamp': datetime.now().isoformat(),
        'source': 'web_sentiment',
        'data': sentiment_data
    }

if __name__ == "__main__":
    data = collect_sentiment()
    print(json.dumps(data, indent=2))
