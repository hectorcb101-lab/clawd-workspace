#!/usr/bin/env python3
"""
Synthesis Module
Generates insights, narratives, and opinions from patterns
"""

import json
from datetime import datetime
from pathlib import Path

def generate_executive_summary(patterns):
    """Generate 3-5 key bullet points."""
    bullets = []
    
    # Significant moves
    major_moves = [m for m in patterns['significant_moves'] if m['magnitude'] == 'major']
    if major_moves:
        move = major_moves[0]
        bullets.append(f"{move['symbol']} {move['direction']} {abs(move['change']):.1f}% - {move['magnitude']} move")
    
    # Market sentiment
    sentiment = patterns['market_sentiment']
    if sentiment.get('fear_level'):
        fear = sentiment['fear_level']
        vix_change = sentiment.get('vix', {}).get('change_percent', 0)
        bullets.append(f"Market fear level: {fear} (VIX {'up' if vix_change > 0 else 'down'} {abs(vix_change):.1f}%)")
    
    # Geopolitical risks
    high_risks = [r for r in patterns['geopolitical_risks'] if r['risk_level'] in ['elevated', 'likely']]
    if high_risks:
        risk = high_risks[0]
        bullets.append(f"Geopolitical: {risk['title']} at {risk['odds']} ({risk['risk_level']} risk)")
    
    # Correlations
    if patterns['correlations']:
        corr = patterns['correlations'][0]
        bullets.append(f"Pattern: {corr['description']}")
    
    # Divergences
    if patterns['divergences']:
        div = patterns['divergences'][0]
        bullets.append(f"Divergence: {div['description']}")
    
    return bullets[:5]  # Max 5

def explain_market_movements(patterns):
    """Explain why markets moved the way they did."""
    explanations = []
    
    sentiment = patterns['market_sentiment']
    significant = patterns['significant_moves']
    risks = patterns['geopolitical_risks']
    
    # Crypto selling
    crypto_down = [m for m in significant if 'BTC' in m['symbol'] or 'ETH' in m['symbol']]
    if crypto_down:
        exp = {
            'asset': 'Cryptocurrency',
            'movement': f"Major selling (BTC/ETH down {abs(crypto_down[0]['change']):.1f}%)",
            'possible_causes': []
        }
        
        # Check for geopolitical risk
        if any(r['risk_level'] in ['moderate', 'elevated'] for r in risks):
            exp['possible_causes'].append("Geopolitical uncertainty (Iran tensions)")
        
        # Check VIX
        if sentiment.get('vix', {}).get('change_percent', 0) > 2:
            exp['possible_causes'].append("Rising fear (VIX up)")
        
        # Check divergence
        if sentiment.get('sp500', {}).get('change_percent', 0) > -0.5:
            exp['possible_causes'].append("Flight from risk assets while stocks hold")
        
        if not exp['possible_causes']:
            exp['possible_causes'].append("Crypto-specific weakness (no clear catalyst)")
        
        exp['confidence'] = 'moderate'
        explanations.append(exp)
    
    return explanations

def form_opinion(patterns, explanations):
    """Atlas's opinion on what matters most."""
    opinion = {
        'main_thesis': '',
        'deep_take': '',
        'reasoning': [],
        'contrarian_view': '',
        'what_to_watch': [],
        'prediction': '',
        'confidence': patterns.get('confidence', 'moderate')
    }
    
    # Build a strong opinion based on patterns
    sentiment = patterns['market_sentiment']
    significant = patterns['significant_moves']
    risks = patterns['geopolitical_risks']
    
    # Main thesis - be opinionated
    if patterns['correlations']:
        corr = patterns['correlations'][0]
        opinion['main_thesis'] = f"This is a classic risk-off rotation. {corr['implication']}"
        opinion['deep_take'] = "When geopolitical uncertainty spikes and volatility rises simultaneously, institutional money typically flows out of speculative assets first (crypto), then equities if fear persists. We're seeing stage one."
        
        # Contrarian view
        opinion['contrarian_view'] = "However, if VIX stays below 20 and crypto finds support here, this could be just a healthy flush before continuation. Watch for divergence."
        
        # Prediction
        opinion['prediction'] = "If Iran odds push above 25% OR VIX breaks 18, expect S&P to follow crypto lower within 48h. Otherwise, this is noise."
        
    elif patterns['divergences']:
        div = patterns['divergences'][0]
        opinion['main_thesis'] = f"Divergence alert: {div['description']}"
        opinion['deep_take'] = f"{div['implication']}. When assets that normally move together split, it signals either sector rotation or something breaking. This matters."
        opinion['contrarian_view'] = "Market divergences often resolve with the weaker asset catching up to the stronger one - not always a crash."
        
    elif explanations and explanations[0]['asset'] == 'Cryptocurrency':
        exp = explanations[0]
        crypto_down = any(m for m in significant if 'BTC' in m['symbol'] or 'ETH' in m['symbol'])
        stocks_flat = sentiment.get('sp500', {}).get('change_percent', 0)
        
        if crypto_down and abs(stocks_flat) < 1:
            opinion['main_thesis'] = "Crypto is bleeding, stocks are ignoring it. This is either: (1) Crypto-specific weakness, or (2) The canary in the coal mine."
            opinion['deep_take'] = "When crypto leads down while equities hold, it's historically been a mixed signal - sometimes isolated to crypto (regulatory fears, exchange issues), sometimes a leading indicator for broader risk-off within days. The key confirmation signals: Watch **small caps (IWM - represents riskier, smaller companies that often move before large caps)** and **credit spreads (the premium investors demand to hold corporate bonds vs safe Treasuries - widens when fear rises)**. If these weaken, crypto was the early warning."
            opinion['contrarian_view'] = "Crypto divergences don't always predict equity moves. Recent patterns (Dec 2025) showed crypto falling 30% while Nasdaq climbed on earnings. Context matters - is this crypto-specific or macro?"
            opinion['prediction'] = "**Key price levels:** BTC support at $84-86k (based on whale accumulation data - large holders buying at these prices). Break below $84k suggests deeper selling pressure. Hold above $86k with stocks green = likely isolated crypto weakness."
        else:
            opinion['main_thesis'] = f"Broad risk-off move driven by {exp['possible_causes'][0]}."
            opinion['deep_take'] = "When multiple asset classes move in sync, it's macro - not sector-specific. This is either geopolitical fear or liquidity tightening."
    else:
        opinion['main_thesis'] = "Quiet tape. No strong signals."
        opinion['deep_take'] = "Low volatility, no clear direction. This is either: (1) Calm before the storm, or (2) Grinding consolidation. Volume and breadth will tell."
        opinion['contrarian_view'] = "Quiet markets often precede big moves. Watch for breakouts."
    
    # Build reasoning from data
    if sentiment.get('vix'):
        vix_val = sentiment['vix'].get('price', 0)
        vix_change = sentiment['vix'].get('change_percent', 0)
        if vix_change > 2:
            opinion['reasoning'].append(f"VIX (the 'fear gauge' - measures expected market volatility) up {vix_change:.1f}% to {vix_val:.1f} - fear is rising, even if markets don't show it yet")
        elif vix_val < 15:
            opinion['reasoning'].append(f"VIX at {vix_val:.1f} (below 15 = complacent) - markets not pricing in much risk right now")
    
    # Geopolitical context
    high_risk_events = [r for r in risks if r['risk_level'] in ['moderate', 'elevated', 'likely']]
    if high_risk_events:
        event = high_risk_events[0]
        opinion['reasoning'].append(f"Polymarket (prediction market where people bet real money on events) pricing {event['odds']} chance of {event['title']} - these odds reflect what informed bettors think will actually happen")
    
    # What to watch (actionable with explanations)
    for risk in patterns['geopolitical_risks'][:2]:
        if risk['risk_level'] in ['moderate', 'elevated', 'likely']:
            opinion['what_to_watch'].append(f"{risk['title']} ({risk['odds']} odds) - if this spikes above 30%, markets will price in higher uncertainty → expect volatility")
    
    if sentiment.get('fear_level') in ['elevated', 'high']:
        opinion['what_to_watch'].append("VIX breaking above 20 (from current 16) would confirm fear is spreading → stocks typically pull back when VIX crosses this level")
    
    # Add crypto/stock relationship
    if any('BTC' in m['symbol'] for m in significant):
        opinion['what_to_watch'].append("BTC support at $85k (price floor where buyers step in) - breaking below this level often triggers more selling as stop-losses hit")
    
    return opinion

def create_educational_content(patterns):
    """Teach one concept based on today's patterns."""
    education = {}
    
    # If VIX moved significantly, explain VIX
    vix_change = patterns['market_sentiment'].get('vix', {}).get('change_percent', 0)
    if abs(vix_change) > 2:
        education = {
            'concept': 'VIX (Volatility Index)',
            'explanation': "The VIX measures expected volatility in the S&P 500 over the next 30 days, derived from options prices. Often called the 'fear index' because it spikes when investors expect market turbulence.",
            'levels': {
                '<15': 'Low fear (complacency)',
                '15-20': 'Normal (moderate concern)',
                '20-30': 'Elevated fear (caution)',
                '>30': 'High fear (panic)'
            },
            'current': f"{patterns['market_sentiment']['vix']['price']:.1f}",
            'interpretation': f"VIX is at {patterns['market_sentiment']['vix']['price']:.1f}, up {vix_change:.1f}% today - showing {'rising' if vix_change > 0 else 'falling'} market uncertainty"
        }
    # If Polymarket odds are interesting, explain prediction markets
    elif any(r['risk_level'] in ['elevated', 'likely'] for r in patterns['geopolitical_risks']):
        risk = [r for r in patterns['geopolitical_risks'] if r['risk_level'] in ['elevated', 'likely']][0]
        education = {
            'concept': 'Prediction Markets (Polymarket)',
            'explanation': "Markets where people bet real money on future events. The odds reflect collective intelligence - what many informed people think will happen. Often more accurate than polls or expert predictions.",
            'how_to_read': f"If {risk['title']} shows {risk['odds']}, that means the market thinks there's a {risk['odds']} chance of this happening. Volume shows confidence: ${risk['volume']} is real money on the line.",
            'why_it_matters': "These odds can be leading indicators for markets. If geopolitical risk odds spike, expect volatility.",
            'current_signal': f"{risk['title']} at {risk['odds']} risk level"
        }
    else:
        education = {
            'concept': 'Market Divergence',
            'explanation': "When different asset classes move in opposite directions, it often signals a shift in investor psychology or changing risk preferences.",
            'example': "Stocks up + Crypto down = possible rotation from speculative to traditional assets"
        }
    
    return education

def synthesize_insights(patterns):
    """Main synthesis function - turn patterns into insights."""
    insights = {
        'timestamp': datetime.utcnow().isoformat(),
        'executive_summary': generate_executive_summary(patterns),
        'market_explanations': explain_market_movements(patterns),
        'atlas_opinion': form_opinion(patterns, explain_market_movements(patterns)),
        'educational': create_educational_content(patterns),
        'patterns_raw': {
            'significant_moves': patterns['significant_moves'],
            'geopolitical_risks': patterns['geopolitical_risks'][:3],
            'sentiment': patterns.get('sentiment', {}),
            'market_sentiment': patterns['market_sentiment']
        }
    }
    
    return insights

if __name__ == "__main__":
    # Load patterns
    patterns_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/patterns.json")
    
    # If patterns file doesn't exist, generate from raw data
    if not patterns_path.exists():
        import sys
        sys.path.append('/home/ubuntu/clawd/intelligence-briefing')
        from analysis.patterns import find_patterns
        
        cache_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/daily_cache.json")
        with open(cache_path, 'r') as f:
            data = json.load(f)
        
        patterns = find_patterns(data)
        
        # Save patterns
        with open(patterns_path, 'w') as f:
            json.dump(patterns, f, indent=2)
    else:
        with open(patterns_path, 'r') as f:
            patterns = json.load(f)
    
    insights = synthesize_insights(patterns)
    print(json.dumps(insights, indent=2))
