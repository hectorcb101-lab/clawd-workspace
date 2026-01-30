#!/usr/bin/env python3
"""
Presentation Module
Formats insights into a beautiful Telegram briefing
"""

import json
from datetime import datetime
from pathlib import Path
import pytz

def format_briefing(insights):
    """Format insights into Telegram-ready briefing."""
    
    # Header - use London timezone for Finn
    london_tz = pytz.timezone('Europe/London')
    now = datetime.now(london_tz)
    briefing = f"""🌍 **INTELLIGENCE BRIEFING**
{now.strftime('%A, %B %d, %Y')} | Past 24 Hours

"""
    
    # Executive Summary
    briefing += "📊 **EXECUTIVE SUMMARY**\n"
    for bullet in insights['executive_summary']:
        briefing += f"• {bullet}\n"
    briefing += "\n"
    
    # Market Movements
    briefing += "🎯 **MARKET MOVEMENTS**\n\n"
    
    # Significant moves
    moves = insights['patterns_raw']['significant_moves']
    if moves:
        for move in moves[:4]:  # Top 4
            emoji = "📈" if move['direction'] == 'up' else "📉"
            briefing += f"{emoji} **{move['symbol']}**: "
            briefing += f"${move['price']:,.2f} " if isinstance(move['price'], (int, float)) else f"{move['price']} "
            briefing += f"({move['change']:+.1f}%)"
            # Add chart link
            briefing += f" [📊](https://finance.yahoo.com/quote/{move['symbol']})\n"
        briefing += "\n"
    
    # Market Explanations
    if insights['market_explanations']:
        exp = insights['market_explanations'][0]
        briefing += f"**{exp['asset']}:** {exp['movement']}\n"
        briefing += f"*Possible causes:*\n"
        for cause in exp['possible_causes'][:3]:
            briefing += f"  • {cause}\n"
        briefing += "\n"
    
    # Geopolitical Developments
    briefing += "⚡ **GEOPOLITICAL LANDSCAPE**\n\n"
    risks = insights['patterns_raw']['geopolitical_risks']
    for risk in risks[:3]:
        emoji = "🔴" if risk['risk_level'] in ['elevated', 'likely'] else "🟡" if risk['risk_level'] == 'moderate' else "🟢"
        briefing += f"{emoji} **{risk['title']}**\n"
        briefing += f"   Odds: {risk['odds']} | Volume: ${risk['volume']}\n"
        briefing += f"   Risk level: {risk['risk_level']}\n\n"
    
    # Market Sentiment
    if 'sentiment' in insights.get('patterns_raw', {}):
        sentiment_data = insights['patterns_raw']['sentiment']
        if sentiment_data.get('data'):
            briefing += "📰 **MARKET SENTIMENT**\n\n"
            
            for topic in sentiment_data['data']:
                emoji_map = {
                    'bullish': '🟢',
                    'bearish': '🔴',
                    'fearful': '🟡',
                    'neutral': '⚪'
                }
                emoji = emoji_map.get(topic['sentiment'], '⚪')
                
                briefing += f"{emoji} **{topic['topic']}**: {topic['sentiment'].upper()}\n"
                if topic.get('sample_headlines'):
                    briefing += f"   *\"{topic['sample_headlines'][0]}\"*\n"
            
            briefing += "\n"
    
    # Atlas's Analysis
    briefing += "💡 **ATLAS'S ANALYSIS**\n\n"
    opinion = insights.get('atlas_opinion') or insights.get('ariadne_opinion', {})
    
    briefing += f"**My take:** {opinion['main_thesis']}\n\n"
    
    if opinion.get('deep_take'):
        briefing += f"{opinion['deep_take']}\n\n"
    
    if opinion.get('reasoning'):
        briefing += f"**Why this matters:**\n"
        for reason in opinion['reasoning'][:3]:
            briefing += f"  • {reason}\n"
        briefing += "\n"
    
    if opinion.get('contrarian_view'):
        briefing += f"**Contrarian angle:** {opinion['contrarian_view']}\n\n"
    
    if opinion.get('prediction'):
        briefing += f"**Watch for:** {opinion['prediction']}\n\n"
    
    briefing += f"**Confidence:** {opinion['confidence']}\n\n"
    
    # What to Watch
    if opinion['what_to_watch']:
        briefing += "📈 **WHAT TO WATCH TODAY**\n"
        for item in opinion['what_to_watch'][:3]:
            briefing += f"  • {item}\n"
        briefing += "\n"
    
    # Educational Content
    briefing += "📚 **LEARN: "
    edu = insights['educational']
    briefing += f"{edu['concept']}**\n\n"
    briefing += f"{edu['explanation']}\n\n"
    
    if 'interpretation' in edu:
        briefing += f"*Today:* {edu['interpretation']}\n\n"
    elif 'current_signal' in edu:
        briefing += f"*Current signal:* {edu['current_signal']}\n\n"
    
    # Further Reading (simple search links)
    briefing += "🔍 **FURTHER READING**\n"
    
    # Add search links for top geopolitical risks
    top_risks = [r for r in opinion['what_to_watch'][:2]]
    if top_risks:
        for item in top_risks:
            # Clean up the watch item to make a good search query
            search_query = item.split('(')[0].strip().replace('...?', '').split('→')[0].strip()
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            briefing += f"  • [{search_query}]({search_url})\n"
    
    # Add link to top moving asset if crypto/major move
    if insights['market_explanations']:
        exp = insights['market_explanations'][0]
        asset_name = exp['asset']
        search_query = f"{asset_name} news today"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&tbm=nws"
        briefing += f"  • [{asset_name} latest news]({search_url})\n"
    
    briefing += "\n"
    
    # Quick Reference Glossary
    briefing += "📖 **QUICK REFERENCE**\n"
    briefing += "*Key terms used in this briefing:*\n"
    briefing += "• **VIX**: 'Fear gauge' - measures expected market volatility (higher = more fear)\n"
    briefing += "• **Support level**: Price where buyers typically step in to prevent further drops\n"
    briefing += "• **Credit spreads**: Premium for corporate bonds vs safe Treasuries (widens when fear rises)\n"
    briefing += "• **Small caps (IWM)**: Smaller, riskier companies that often move before large stocks\n"
    briefing += "• **Polymarket**: Prediction market where people bet real money on future events\n"
    briefing += "\n"
    
    # Footer
    briefing += "---\n"
    briefing += "*Carrying the weight so you don't have to*\n"
    briefing += f"🏛️ Atlas | {now.strftime('%H:%M')} London\n"
    briefing += "_Your Titan in the machine_"
    
    return briefing

def save_briefing(briefing_text, insights):
    """Save briefing to archive."""
    today = datetime.utcnow().strftime('%Y-%m-%d')
    archive_dir = Path("/home/ubuntu/clawd/intelligence-briefing/data/history")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Save formatted text
    text_path = archive_dir / f"{today}_briefing.txt"
    with open(text_path, 'w') as f:
        f.write(briefing_text)
    
    # Save insights JSON
    json_path = archive_dir / f"{today}_insights.json"
    with open(json_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    return text_path, json_path

if __name__ == "__main__":
    # Load insights
    import sys
    sys.path.append('/home/ubuntu/clawd/intelligence-briefing')
    
    # Generate fresh insights
    from collectors.collect_data import collect_all_data
    from analysis.patterns import find_patterns
    from synthesis.generate_insights import synthesize_insights
    
    print("Generating complete briefing...")
    
    # Pipeline
    data = collect_all_data()
    patterns = find_patterns(data)
    insights = synthesize_insights(patterns)
    
    # Format
    briefing = format_briefing(insights)
    
    # Save
    text_path, json_path = save_briefing(briefing, insights)
    
    print(f"\n✅ Briefing saved to: {text_path}\n")
    print("=" * 60)
    print(briefing)
    print("=" * 60)
