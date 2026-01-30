#!/usr/bin/env python3
"""
Deep Research Module
Comprehensive research on any topic using Exa + X
"""

import subprocess
import json
import sys
import os
from datetime import datetime, timezone

# Bird auth
os.environ['AUTH_TOKEN'] = 'cd8d2c9353c747711c2bff02a017219bf000add6'
os.environ['CT0'] = 'f4ac87d75e426d8c928186078d4416530f722917009df49ff29bac2d280d5f993af2c5e9af3440803e23cb006b194041a487ff9e8eb0182e6f82cbf37bb06bce293e997e76fae47fefd24732e91842d1'


def exa_search(query, num_results=5):
    """Search via Exa for articles and papers."""
    try:
        cmd = ['mcporter', 'call', 'exa.web_search_exa', 
               f'query={query}', f'numResults={num_results}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def exa_research(query, num_results=5):
    """Deep research via Exa (longer content)."""
    try:
        cmd = ['mcporter', 'call', 'exa.research_exa',
               f'query={query}', f'numResults={num_results}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def x_search(query, n=10):
    """Search X/Twitter for opinions and discussions."""
    try:
        cmd = ['bird', 'search', query, '-n', str(n), '--plain']
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              timeout=30, env=os.environ)
        return result.stdout if result.returncode == 0 else None
    except:
        return None


def deep_research(topic, context=""):
    """
    Perform comprehensive research on a topic.
    
    Args:
        topic: The research topic
        context: Additional context (e.g., "for MSc AI", "for trading")
    
    Returns:
        dict with research findings
    """
    print(f"🔬 Starting deep research: {topic}")
    
    results = {
        'topic': topic,
        'context': context,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sources': {},
        'summary': ''
    }
    
    # 1. General web search
    print("  📰 Searching web articles...")
    web = exa_search(f"{topic} {context} latest news explained", 5)
    if web:
        results['sources']['web_articles'] = web
    
    # 2. Academic/research papers
    print("  📚 Searching academic papers...")
    papers = exa_search(f"{topic} research paper arxiv 2025 2026", 5)
    if papers:
        results['sources']['papers'] = papers
    
    # 3. Technical tutorials/guides
    print("  🛠️ Searching tutorials...")
    tutorials = exa_search(f"{topic} tutorial guide how to learn", 3)
    if tutorials:
        results['sources']['tutorials'] = tutorials
    
    # 4. Expert opinions on X
    print("  🐦 Searching X for expert opinions...")
    x_results = x_search(f"{topic}", 10)
    if x_results:
        results['sources']['x_opinions'] = x_results
    
    # 5. Deep research (if available)
    print("  🔬 Running deep research...")
    deep = exa_research(f"{topic} comprehensive overview", 3)
    if deep:
        results['sources']['deep_research'] = deep
    
    results['status'] = 'success' if results['sources'] else 'failed'
    print(f"✅ Research complete: {len(results['sources'])} source types found")
    
    return results


def format_research_brief(results):
    """Format research results into a readable brief."""
    lines = [
        f"# Research Brief: {results['topic']}",
        f"*Generated: {results['timestamp'][:10]}*",
        "",
    ]
    
    if results.get('context'):
        lines.append(f"**Context:** {results['context']}")
        lines.append("")
    
    # Web articles
    if 'web_articles' in results['sources']:
        lines.append("## 📰 Key Articles")
        lines.append(results['sources']['web_articles'][:2000])
        lines.append("")
    
    # Papers
    if 'papers' in results['sources']:
        lines.append("## 📚 Research Papers")
        lines.append(results['sources']['papers'][:2000])
        lines.append("")
    
    # Tutorials
    if 'tutorials' in results['sources']:
        lines.append("## 🛠️ Learning Resources")
        lines.append(results['sources']['tutorials'][:1500])
        lines.append("")
    
    # X opinions
    if 'x_opinions' in results['sources']:
        lines.append("## 🐦 Expert Opinions (X)")
        lines.append(results['sources']['x_opinions'][:2000])
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: deep_research.py <topic> [context]")
        sys.exit(1)
    
    topic = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    results = deep_research(topic, context)
    brief = format_research_brief(results)
    
    print("\n" + "="*60)
    print(brief)
    print("="*60)
    
    # Save to file
    safe_topic = topic.replace(' ', '_').replace('/', '-')[:50]
    output_path = f"/home/ubuntu/clawd/research/briefs/{safe_topic}_{datetime.now().strftime('%Y%m%d')}.md"
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(brief)
    
    print(f"\n📁 Saved to: {output_path}")
