#!/usr/bin/env python3
"""
AI News Articles via Exa Search
Fetches actual news articles about AI developments
"""

import subprocess
import json
from datetime import datetime, timezone

def run_exa_search(query, num_results=5):
    """Run Exa web search via mcporter."""
    try:
        cmd = [
            'mcporter', 'call', 'exa.web_search_exa',
            f'query={query}',
            f'numResults={num_results}'
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode
    except Exception as e:
        print(f"Exa error: {e}")
        return None, -1


def parse_exa_results(output):
    """Parse Exa output into structured articles."""
    if not output:
        return []
    
    articles = []
    current = {}
    
    for line in output.split('\n'):
        line = line.strip()
        
        if line.startswith('Title:'):
            if current and 'title' in current:
                articles.append(current)
            current = {'title': line.replace('Title:', '').strip()}
        
        elif line.startswith('Author:'):
            current['author'] = line.replace('Author:', '').strip()
        
        elif line.startswith('Published Date:'):
            current['date'] = line.replace('Published Date:', '').strip()
        
        elif line.startswith('URL:'):
            current['url'] = line.replace('URL:', '').strip()
        
        elif line.startswith('Text:'):
            current['text'] = line.replace('Text:', '').strip()[:500]
    
    if current and 'title' in current:
        articles.append(current)
    
    return articles


def collect_ai_articles():
    """Collect AI news articles from multiple queries."""
    print("📰 Collecting AI news articles via Exa...")
    
    queries = [
        "AI artificial intelligence news breakthrough today",
        "OpenAI Anthropic Claude GPT news",
        "large language model LLM research",
        "AI startup funding announcement",
    ]
    
    results = {
        'collection_time': datetime.now(timezone.utc).isoformat(),
        'source': 'exa_ai_articles',
        'articles': [],
        'by_query': {}
    }
    
    seen_urls = set()
    
    for query in queries:
        print(f"  🔍 {query[:40]}...")
        output, code = run_exa_search(query, num_results=3)
        
        if code == 0 and output:
            articles = parse_exa_results(output)
            results['by_query'][query] = articles
            
            # Add unique articles to main list
            for article in articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    results['articles'].append(article)
    
    results['status'] = 'success' if results['articles'] else 'failed'
    results['article_count'] = len(results['articles'])
    
    print(f"✅ Collected {len(results['articles'])} unique AI articles")
    return results


def format_articles_summary(data):
    """Format articles into readable summary."""
    lines = ["📰 **AI NEWS ARTICLES**", ""]
    
    for article in data.get('articles', [])[:5]:
        title = article.get('title', 'Untitled')
        url = article.get('url', '')
        author = article.get('author', '')
        date = article.get('date', '')[:10] if article.get('date') else ''
        
        lines.append(f"**{title}**")
        if author:
            lines.append(f"By {author} | {date}")
        if url:
            lines.append(f"🔗 {url}")
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    data = collect_ai_articles()
    print("\n" + "="*60)
    print(format_articles_summary(data))
    print("="*60)
    print("\nFull data:")
    print(json.dumps(data, indent=2, default=str))
