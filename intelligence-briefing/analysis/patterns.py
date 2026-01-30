#!/usr/bin/env python3
"""
Pattern Recognition Module
Finds correlations, anomalies, and non-obvious connections
"""

import json
from datetime import datetime
from pathlib import Path

def detect_significant_moves(finance_data, threshold=2.0):
    """Detect price movements above threshold percentage."""
    significant = []
    
    for asset in finance_data.get('data', []):
        change = abs(asset.get('change_percent', 0))
        if change >= threshold:
            significant.append({
                'symbol': asset['symbol'],
                'price': asset.get('price'),
                'change': asset.get('change_percent'),
                'direction': 'up' if asset.get('change_percent', 0) > 0 else 'down',
                'magnitude': 'major' if change >= 5 else 'notable'
            })
    
    return significant

def analyze_market_sentiment(finance_data):
    """Analyze overall market sentiment from VIX and indices."""
    vix = None
    sp500 = None
    btc = None
    
    for asset in finance_data.get('data', []):
        symbol = asset['symbol']
        if symbol == '^VIX':
            vix = asset
        elif symbol == '^GSPC':
            sp500 = asset
        elif symbol == 'BTC-USD':
            btc = asset
    
    sentiment = {
        'vix': vix,
        'sp500': sp500,
        'btc': btc,
        'assessment': 'neutral'
    }
    
    if vix:
        vix_level = vix.get('price', 20)
        if vix_level < 15:
            sentiment['fear_level'] = 'low'
            sentiment['assessment'] = 'complacent'
        elif vix_level < 20:
            sentiment['fear_level'] = 'moderate'
            sentiment['assessment'] = 'neutral'
        elif vix_level < 30:
            sentiment['fear_level'] = 'elevated'
            sentiment['assessment'] = 'cautious'
        else:
            sentiment['fear_level'] = 'high'
            sentiment['assessment'] = 'fearful'
    
    return sentiment

def find_divergences(finance_data):
    """Find divergences between asset classes."""
    divergences = []
    
    sp500 = None
    btc = None
    gold = None
    
    for asset in finance_data.get('data', []):
        symbol = asset['symbol']
        if symbol == '^GSPC':
            sp500 = asset
        elif symbol == 'BTC-USD':
            btc = asset
        elif symbol == 'GC=F':
            gold = asset
    
    # Check stock vs crypto divergence
    if sp500 and btc:
        sp_change = sp500.get('change_percent', 0)
        btc_change = btc.get('change_percent', 0)
        
        # Significant divergence if opposite directions or big magnitude difference
        if (sp_change > 1 and btc_change < -2) or (sp_change < -1 and btc_change > 2):
            divergences.append({
                'type': 'stocks_vs_crypto',
                'description': f"Stocks {'up' if sp_change > 0 else 'down'} {abs(sp_change):.1f}% while BTC {'up' if btc_change > 0 else 'down'} {abs(btc_change):.1f}%",
                'significance': 'notable',
                'implication': 'Risk-on/risk-off rotation or crypto-specific news'
            })
    
    return divergences

def correlate_polymarket_markets(polymarket_data):
    """Extract geopolitical risks from Polymarket."""
    risks = []
    
    for market in polymarket_data.get('data', [])[:3]:  # Top 3 markets
        title = market.get('title', '')
        volume = market.get('volume', '0')
        
        # Extract key odds
        key_market = None
        if market.get('markets'):
            key_market = market['markets'][0]  # First market usually most important
        
        if key_market:
            question = key_market.get('question', '')
            odds = key_market.get('odds', '0%')
            
            try:
                odds_value = float(odds.replace('%', ''))
            except:
                odds_value = 0
            
            # Classify risk level
            if odds_value > 50:
                risk_level = 'likely'
            elif odds_value > 25:
                risk_level = 'elevated'
            elif odds_value > 10:
                risk_level = 'moderate'
            else:
                risk_level = 'low'
            
            risks.append({
                'title': title,
                'question': question,
                'odds': odds,
                'odds_numeric': odds_value,
                'risk_level': risk_level,
                'volume': volume
            })
    
    return risks

def find_patterns(data):
    """Main pattern recognition function."""
    patterns = {
        'timestamp': datetime.utcnow().isoformat(),
        'significant_moves': [],
        'market_sentiment': {},
        'sentiment': {},
        'divergences': [],
        'geopolitical_risks': [],
        'correlations': [],
        'confidence': 'moderate'
    }
    
    finance_data = data['sources'].get('finance', {})
    polymarket_data = data['sources'].get('polymarket', {})
    sentiment_data = data['sources'].get('sentiment', {})
    
    # Detect significant moves
    patterns['significant_moves'] = detect_significant_moves(finance_data)
    
    # Analyze market sentiment
    patterns['market_sentiment'] = analyze_market_sentiment(finance_data)
    
    # Store sentiment data
    patterns['sentiment'] = sentiment_data
    
    # Find divergences
    patterns['divergences'] = find_divergences(finance_data)
    
    # Extract geopolitical risks
    patterns['geopolitical_risks'] = correlate_polymarket_markets(polymarket_data)
    
    # Cross-correlate (basic version)
    # If high geopolitical risk + elevated VIX = confident correlation
    vix_up = False
    geo_risk_elevated = False
    
    if patterns['market_sentiment'].get('vix'):
        vix_change = patterns['market_sentiment']['vix'].get('change_percent', 0)
        vix_up = vix_change > 2
    
    for risk in patterns['geopolitical_risks']:
        if risk['risk_level'] in ['elevated', 'likely']:
            geo_risk_elevated = True
            break
    
    if vix_up and geo_risk_elevated:
        patterns['correlations'].append({
            'type': 'geopolitical_risk_vix',
            'description': 'VIX rising alongside elevated geopolitical risk (Polymarket)',
            'confidence': 'high',
            'implication': 'Markets pricing in uncertainty from geopolitical events'
        })
        patterns['confidence'] = 'high'
    
    return patterns

if __name__ == "__main__":
    # Load cached data
    cache_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/daily_cache.json")
    with open(cache_path, 'r') as f:
        data = json.load(f)
    
    patterns = find_patterns(data)
    print(json.dumps(patterns, indent=2))
