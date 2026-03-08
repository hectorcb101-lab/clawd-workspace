#!/usr/bin/env python3
"""
Geopolitical Alpha Analysis Module
Maps geopolitical events → transmission chains → affected assets
Includes historical parallels, second-order effects, conviction scoring
"""

import json
from datetime import datetime
from pathlib import Path

# Knowledge Base: Event Category → Asset Impact Mappings
TRANSMISSION_CHAINS = {
    'military_conflict': {
        'direct_impacts': [
            {'asset': 'Defence stocks', 'direction': 'up', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Oil (Brent/WTI)', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Gold', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'CHF (Swiss Franc)', 'direction': 'up', 'magnitude': 'low', 'conviction': 'medium'},
            {'asset': 'JPY (Japanese Yen)', 'direction': 'up', 'magnitude': 'low', 'conviction': 'medium'},
            {'asset': 'US Treasuries', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Local currency (conflict zone)', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Regional equities', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'}
        ],
        'second_order': [
            'Shipping insurance premiums rise if conflict affects trade routes',
            'European energy costs spike if Russia/Middle East involved',
            'Rare earth/critical mineral supply disruption if major producer involved',
            'Refugee flows → political pressure in neighbouring countries',
            'Cyber warfare spillover → tech security spending ↑'
        ],
        'teaching_note': 'Military conflicts trigger flight-to-safety: investors sell risky assets (stocks, crypto) and buy safe havens (gold, government bonds, stable currencies). Defence contractors benefit from increased military spending. Energy prices spike if conflict affects production/transit regions.'
    },
    
    'trade_sanctions': {
        'direct_impacts': [
            {'asset': 'Sanctioned country FX', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Sanctioned exports', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Alternative suppliers', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Commodity affected', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'}
        ],
        'second_order': [
            'Black market premium emerges for sanctioned goods',
            'Shipping reroutes → longer delivery times, higher costs',
            'Financial system fragmentation → alternative payment systems grow',
            'Supply chain reshoring accelerates → capex for domestic production',
            'Diplomatic alliances shift → trade bloc formation'
        ],
        'teaching_note': 'Sanctions cut off a country from global markets, collapsing their currency and exports. BUT: alternative suppliers benefit (e.g., UAE replaces Russian oil), and sanctioned countries develop workarounds (parallel payment systems, friendly intermediaries). The effectiveness depends on enforcement and alternatives available.'
    },
    
    'tariffs': {
        'direct_impacts': [
            {'asset': 'Affected sector margins', 'direction': 'down', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Domestic competitors', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Consumer prices', 'direction': 'up', 'magnitude': 'low', 'conviction': 'high'},
            {'asset': 'Exporting country currency', 'direction': 'down', 'magnitude': 'low', 'conviction': 'medium'},
            {'asset': 'Importing country currency', 'direction': 'up', 'magnitude': 'low', 'conviction': 'low'}
        ],
        'second_order': [
            'Retaliatory tariffs → escalation spiral',
            'Supply chain diversification → short-term disruption, long-term resilience',
            'Input cost inflation for downstream industries',
            'Political pressure from affected industries → policy uncertainty',
            'Negotiation leverage shifts in other trade areas'
        ],
        'teaching_note': 'Tariffs are taxes on imports. They make foreign goods more expensive, helping domestic producers compete BUT raising costs for consumers and companies that rely on those imports. E.g., steel tariffs help US steel mills but hurt US car makers. Markets hate tariffs because they reduce efficiency, raise inflation, and invite retaliation.'
    },
    
    'central_bank_hawkish': {
        'direct_impacts': [
            {'asset': 'Interest rates', 'direction': 'up', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Growth stocks', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Bank stocks', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Currency', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Government bonds (prices)', 'direction': 'down', 'magnitude': 'medium', 'conviction': 'high'}
        ],
        'second_order': [
            'Credit tightening → harder for companies to borrow → lower capex, hiring',
            'Mortgage rates ↑ → housing market slows → construction, furniture, appliances ↓',
            'Debt servicing costs ↑ for highly leveraged companies → default risk ↑',
            'Currency strength hurts exporters → trade balance shifts',
            'EM currencies weaken (capital flows to higher-yielding developed markets)'
        ],
        'teaching_note': 'Hawkish = central bank fighting inflation by raising rates or reducing money supply. Higher rates make borrowing expensive, slowing growth. Growth stocks (tech, startups) fall because their future profits are worth less when discounted at higher rates. Banks benefit from higher interest margins. The currency strengthens as foreign money flows in for higher yields.'
    },
    
    'central_bank_dovish': {
        'direct_impacts': [
            {'asset': 'Interest rates', 'direction': 'down', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Growth stocks', 'direction': 'up', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Bank stocks', 'direction': 'down', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Currency', 'direction': 'down', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Government bonds (prices)', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'}
        ],
        'second_order': [
            'Easy money → asset inflation (stocks, housing, crypto)',
            'Zombie companies survive (cheap debt keeps unprofitable firms alive)',
            'Currency devaluation → imported inflation',
            'Savers hurt (lower interest on deposits) → consumption vs saving trade-off',
            'Wealth inequality ↑ (asset owners benefit more than wage earners)'
        ],
        'teaching_note': 'Dovish = central bank prioritising growth over inflation, cutting rates or printing money. Cheap money fuels risk assets (stocks, crypto, property) because borrowing is easy and cash yields nothing. The currency weakens as capital seeks better returns elsewhere. Banks suffer from compressed interest margins.'
    },
    
    'energy_supply_disruption': {
        'direct_impacts': [
            {'asset': 'Oil/Gas prices', 'direction': 'up', 'magnitude': 'high', 'conviction': 'high'},
            {'asset': 'Transport costs', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Renewable energy stocks', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Energy-intensive sectors', 'direction': 'down', 'magnitude': 'medium', 'conviction': 'high'},
            {'asset': 'Energy producers', 'direction': 'up', 'magnitude': 'high', 'conviction': 'high'}
        ],
        'second_order': [
            'Inflation spike → central banks forced to act → rates ↑',
            'Energy security becomes priority → long-term infrastructure investment',
            'Geopolitical leverage shifts to energy exporters',
            'Consumer discretionary spending ↓ (energy bills eat into budgets)',
            'Petrochemical, fertiliser, aluminium production curtailed → price spikes'
        ],
        'teaching_note': 'Energy is the foundation of everything. When supply is disrupted (war, OPEC cuts, pipeline damage), prices spike. This flows through the entire economy: transport (airlines, shipping), manufacturing (chemicals, steel), consumers (petrol, heating). Energy-intensive industries get squeezed first. Renewable/alternative energy becomes more attractive.'
    },
    
    'political_transition': {
        'direct_impacts': [
            {'asset': 'Policy-sensitive sectors', 'direction': 'mixed', 'magnitude': 'medium', 'conviction': 'medium'},
            {'asset': 'Currency', 'direction': 'mixed', 'magnitude': 'medium', 'conviction': 'low'},
            {'asset': 'Volatility', 'direction': 'up', 'magnitude': 'medium', 'conviction': 'high'}
        ],
        'second_order': [
            'Regulatory uncertainty → investment freeze until policy clarity',
            'Fiscal policy shifts → deficit spending vs austerity',
            'Foreign relations reset → trade agreements, military alliances',
            'Internal stability risk → protests, strikes, capital flight',
            'Policy continuity vs disruption → markets hate uncertainty'
        ],
        'teaching_note': 'Elections and government changes create uncertainty. Markets generally dislike uncertainty. The impact depends on: (1) How radical is the change? (2) Which sectors win/lose under new policies? (3) Economic competence of new leadership? E.g., pro-business government → stocks ↑, progressive government → healthcare/green energy ↑ but fossil fuels ↓.'
    }
}

# Historical Parallels Database
HISTORICAL_PARALLELS = {
    'Crimea 2014': {
        'event': 'Russia annexes Crimea, sanctions imposed',
        'date': '2014-03-18',
        'market_impacts': {
            'MICEX (Russian stocks)': '-15%',
            'Russian Ruble': '-10%',
            'Oil (Brent)': 'Flat initially, then -50% by end 2014 (separate supply factors)',
            'European natural gas': '+30%',
            'Gold': '+8%'
        },
        'lesson': 'Sanctions hit the sanctioned economy hard but global spillover limited. Energy prices spiked only where supply directly affected. Gold rallied on uncertainty.'
    },
    
    'US-China Trade War 2018-19': {
        'event': 'Escalating tariffs between US and China',
        'date': '2018-07-06',
        'market_impacts': {
            'S&P 500': '-20% peak to trough (Q4 2018)',
            'Chinese Yuan': '-10%',
            'Soybeans': '-20% (China stopped buying US)',
            'US Tech stocks': '-25% (supply chain fears)',
            'Vietnam stocks': '+15% (supply chain diversion)'
        },
        'lesson': 'Trade wars hurt both sides but create winners elsewhere. Supply chains shifted to Vietnam/Mexico. Currency depreciation partially offset tariff pain. Markets fell on escalation, rallied on détente signals.'
    },
    
    'COVID Supply Chains 2020': {
        'event': 'Global supply chain breakdown',
        'date': '2020-03-15',
        'market_impacts': {
            'Shipping costs (Baltic Dry)': '+500%',
            'Semiconductor shortage': 'Auto production -30% in 2021',
            'Freight/logistics stocks': '+200%',
            'Container shipping': '+400%'
        },
        'lesson': 'Supply shocks create extreme price dislocations. Long lead-time goods (chips) face multi-year shortages. Transport infrastructure became the bottleneck. Resilience > efficiency became priority.'
    },
    
    'Russia-Ukraine 2022': {
        'event': 'Full-scale invasion of Ukraine',
        'date': '2022-02-24',
        'market_impacts': {
            'European natural gas': '+300%',
            'Wheat': '+50%',
            'Russian Ruble': 'Crashed to 120/$, recovered to 60/$ (capital controls)',
            'Defence stocks (US/EU)': '+40%',
            'European stocks': '-20%',
            'Gold': '+15%'
        },
        'lesson': 'Energy dependence = strategic vulnerability. Sanctions can be circumvented (Russia selling oil via India/China). Commodity exporters (wheat, fertiliser) have immense leverage. War accelerates structural shifts (EU energy transition).'
    },
    
    'Brexit Vote 2016': {
        'event': 'UK votes to leave EU',
        'date': '2016-06-23',
        'market_impacts': {
            'GBP (Pound Sterling)': '-12% overnight',
            'FTSE 250 (UK mid-cap)': '-14%',
            'UK Banks': '-30%',
            'Gold': '+8%',
            'US Treasuries': 'Flight to safety rally'
        },
        'lesson': 'Political shocks cause currency collapse if they threaten economic integration. Domestic-focused companies (FTSE 250) hurt more than multinationals (FTSE 100). Uncertainty persists for years → prolonged discount.'
    },
    
    'Trump Tariffs 2025': {
        'event': 'Broad tariffs on China, EU, Mexico',
        'date': '2025-01-20',
        'market_impacts': {
            'S&P 500': '-15% (tariff escalation phase)',
            'DXY (Dollar Index)': 'Volatile (+5% then -3%)',
            'China A-shares': '-8%',
            'Mexico Peso': '-12%',
            'US Retailers': '-20% (import cost fears)'
        },
        'lesson': 'Modern tariffs hurt importing country consumers and companies reliant on global supply chains. Dollar strength from safe-haven flows but weakens if recession fears dominate. Retaliation risk keeps volatility elevated.'
    }
}

def classify_event_category(event):
    """Classify event into transmission chain category."""
    category = event['category']
    headline = event['headline'].lower()
    summary = event['summary'].lower()
    
    # Map collector categories to transmission chain keys
    if category == 'military_conflict':
        return 'military_conflict'
    elif category == 'trade_sanctions':
        # Distinguish between sanctions and tariffs
        if 'tariff' in headline or 'tariff' in summary:
            return 'tariffs'
        else:
            return 'trade_sanctions'
    elif category == 'central_bank':
        # Determine hawkish vs dovish
        hawkish_keywords = ['raise', 'hike', 'tighten', 'hawkish', 'inflation']
        dovish_keywords = ['cut', 'lower', 'ease', 'dovish', 'stimulus']
        
        text = f"{headline} {summary}"
        hawkish_score = sum(1 for kw in hawkish_keywords if kw in text)
        dovish_score = sum(1 for kw in dovish_keywords if kw in text)
        
        if hawkish_score > dovish_score:
            return 'central_bank_hawkish'
        elif dovish_score > hawkish_score:
            return 'central_bank_dovish'
        else:
            return 'central_bank_hawkish'  # Default to hawkish in 2026 environment
    elif category == 'energy_supply':
        return 'energy_supply_disruption'
    elif category == 'political_transition':
        return 'political_transition'
    else:
        return 'political_transition'  # Default

def find_historical_parallel(event, chain_category):
    """Find the most relevant historical parallel."""
    countries = event.get('countries', [])
    
    # Simple matching logic - can be enhanced
    if chain_category == 'military_conflict':
        if any(c in ['Russia', 'Ukraine'] for c in countries):
            return HISTORICAL_PARALLELS['Russia-Ukraine 2022']
        else:
            return HISTORICAL_PARALLELS['Crimea 2014']
    
    elif chain_category == 'trade_sanctions':
        if any(c in ['Russia'] for c in countries):
            return HISTORICAL_PARALLELS['Crimea 2014']
        elif any(c in ['China', 'US', 'USA'] for c in countries):
            return HISTORICAL_PARALLELS['US-China Trade War 2018-19']
        else:
            return HISTORICAL_PARALLELS['Russia-Ukraine 2022']
    
    elif chain_category == 'tariffs':
        if any(c in ['China', 'Mexico', 'EU', 'Europe'] for c in countries):
            return HISTORICAL_PARALLELS['Trump Tariffs 2025']
        else:
            return HISTORICAL_PARALLELS['US-China Trade War 2018-19']
    
    elif chain_category in ['central_bank_hawkish', 'central_bank_dovish']:
        # No perfect parallel, return trade war as it had CB component
        return HISTORICAL_PARALLELS['US-China Trade War 2018-19']
    
    elif chain_category == 'energy_supply_disruption':
        return HISTORICAL_PARALLELS['Russia-Ukraine 2022']
    
    elif chain_category == 'political_transition':
        if any(c in ['UK', 'Britain', 'EU', 'Europe'] for c in countries):
            return HISTORICAL_PARALLELS['Brexit Vote 2016']
        else:
            return HISTORICAL_PARALLELS['Trump Tariffs 2025']
    
    # Default
    return HISTORICAL_PARALLELS['Russia-Ukraine 2022']

def build_transmission_chain(event):
    """Build transmission chain from event to asset impacts."""
    chain_category = classify_event_category(event)
    chain_data = TRANSMISSION_CHAINS[chain_category]
    
    # Build transmission path steps
    transmission_path = [
        f"Event: {event['headline'][:80]}",
        f"Category: {chain_category.replace('_', ' ').title()}",
        f"Transmission: {chain_data['teaching_note'][:100]}..."
    ]
    
    # Get historical parallel
    historical = find_historical_parallel(event, chain_category)
    
    # Build affected assets with specific details
    affected_assets = []
    for impact in chain_data['direct_impacts']:
        asset_entry = {
            'asset': impact['asset'],
            'direction': impact['direction'],
            'magnitude': impact['magnitude'],
            'conviction': impact['conviction'],
            'rationale': f"Historical precedent: {chain_category.replace('_', ' ')} typically affects this asset class"
        }
        affected_assets.append(asset_entry)
    
    # Build the complete chain
    chain = {
        'event': event['headline'],
        'event_date': event.get('date', ''),
        'event_category': chain_category,
        'countries': event.get('countries', []),
        'transmission_path': transmission_path,
        'affected_assets': affected_assets[:6],  # Top 6 assets
        'second_order': chain_data['second_order'][:3],  # Top 3 second-order effects
        'historical_parallel': {
            'event': historical['event'],
            'date': historical['date'],
            'what_happened': historical['market_impacts'],
            'lesson': historical['lesson']
        },
        'teaching_note': chain_data['teaching_note'],
        'source_url': event.get('source_url', '')
    }
    
    return chain

def score_conviction(chain):
    """Calculate overall conviction score for the chain."""
    # Weight by conviction levels
    conviction_weights = {'high': 3, 'medium': 2, 'low': 1}
    
    total_weight = 0
    for asset in chain['affected_assets']:
        conviction = asset.get('conviction', 'medium')
        total_weight += conviction_weights.get(conviction, 2)
    
    # Normalize to 0-100
    max_possible = len(chain['affected_assets']) * 3
    score = (total_weight / max_possible * 100) if max_possible > 0 else 50
    
    # Adjust based on number of high-conviction impacts
    high_conviction_count = sum(1 for a in chain['affected_assets'] if a.get('conviction') == 'high')
    if high_conviction_count >= 3:
        score = min(score + 15, 100)
    
    return score

def analyze_geopolitical_alpha(events_data):
    """Main analysis function - generates transmission chains for geopolitical events."""
    print("=" * 60)
    print("🎯 GEOPOLITICAL ALPHA ANALYSIS")
    print("=" * 60)
    
    events = events_data.get('events', [])
    
    if not events:
        print("⚠️ No geopolitical events to analyze")
        return {
            'status': 'no_events',
            'timestamp': datetime.utcnow().isoformat(),
            'chains': []
        }
    
    chains = []
    
    for event in events[:10]:  # Analyze top 10 events
        chain = build_transmission_chain(event)
        chain['conviction_score'] = score_conviction(chain)
        chains.append(chain)
    
    # Sort by conviction score
    chains.sort(key=lambda x: x['conviction_score'], reverse=True)
    
    result = {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'chains': chains,
        'summary': {
            'total_events': len(events),
            'chains_generated': len(chains),
            'high_conviction': len([c for c in chains if c['conviction_score'] >= 70]),
            'medium_conviction': len([c for c in chains if 40 <= c['conviction_score'] < 70]),
            'low_conviction': len([c for c in chains if c['conviction_score'] < 40])
        }
    }
    
    print(f"✅ Generated {len(chains)} transmission chains")
    print(f"   High conviction: {result['summary']['high_conviction']}")
    print(f"   Medium conviction: {result['summary']['medium_conviction']}")
    
    return result

if __name__ == "__main__":
    # Load geopolitical events
    events_path = Path("/home/ubuntu/clawd/intelligence-briefing/data/cache/geopolitical_events.json")
    
    if not events_path.exists():
        print("⚠️ No geopolitical events file found. Run collect_geopolitical.py first.")
        import sys
        sys.exit(1)
    
    with open(events_path, 'r') as f:
        events_data = json.load(f)
    
    alpha = analyze_geopolitical_alpha(events_data)
    print(json.dumps(alpha, indent=2))
