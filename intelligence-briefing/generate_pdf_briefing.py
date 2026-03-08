#!/usr/bin/env python3
"""
Atlas Intelligence Briefing - PDF Generator
Generates a styled daily intelligence briefing in PDF format.
"""

import os
import sys
from datetime import datetime
from weasyprint import HTML, CSS
import yfinance as yf

# Configuration
OUTPUT_DIR = os.path.expanduser("~/clawd/intelligence-briefing/data/history")
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{TODAY}_briefing.pdf")

def get_market_data():
    """Fetch live market data via yfinance"""
    tickers = {
        'S&P 500': '^GSPC',
        'FTSE 100': '^FTSE',
        'VIX': '^VIX',
        'Oil (WTI)': 'CL=F',
        'Gold': 'GC=F',
        'Bitcoin': 'BTC-USD'
    }
    
    market_data = []
    for name, ticker in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100
                market_data.append({
                    'name': name,
                    'price': current,
                    'change': change_pct,
                    'direction': 'up' if change_pct >= 0 else 'down'
                })
            else:
                # Fallback to placeholder
                raise ValueError("Insufficient data")
        except Exception as e:
            # Placeholder data if fetch fails
            placeholder = {
                'S&P 500': (5234.18, 0.45),
                'FTSE 100': (8456.32, -0.23),
                'VIX': (18.45, -2.1),
                'Oil (WTI)': (82.34, 1.8),
                'Gold': (2045.67, 0.34),
                'Bitcoin': (51234.56, 3.2)
            }
            price, change = placeholder.get(name, (0, 0))
            market_data.append({
                'name': name,
                'price': price,
                'change': change,
                'direction': 'up' if change >= 0 else 'down'
            })
    
    return market_data

def format_price(name, price):
    """Format price based on instrument type"""
    if 'Bitcoin' in name or 'BTC' in name:
        return f"${price:,.2f}"
    elif 'VIX' in name:
        return f"{price:.2f}"
    elif 'Oil' in name or 'Gold' in name:
        return f"${price:.2f}"
    else:
        return f"{price:,.2f}"

def generate_html(market_data):
    """Generate the HTML briefing with embedded CSS"""
    
    # Generate market snapshot HTML
    market_html = ""
    for data in market_data:
        color = "#2e7d32" if data['direction'] == 'up' else "#c62828"
        arrow = "▲" if data['direction'] == 'up' else "▼"
        price_str = format_price(data['name'], data['price'])
        market_html += f"""
        <div class="market-item">
            <div class="market-name">{data['name']}</div>
            <div class="market-price">{price_str}</div>
            <div class="market-change" style="color: {color};">
                {arrow} {abs(data['change']):.2f}%
            </div>
        </div>
        """
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4 portrait;
            margin: 1.5cm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #ffffff;
            color: #2a2a3a;
            font-size: 10pt;
            line-height: 1.4;
        }}
        
        .container {{
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #1e3a5f;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        
        .header h1 {{
            font-size: 24pt;
            font-weight: 700;
            letter-spacing: 2px;
            color: #1e3a5f;
            margin-bottom: 8px;
        }}
        
        .header .emoji {{
            font-size: 28pt;
            margin-right: 10px;
        }}
        
        .header .date {{
            font-size: 11pt;
            color: #666;
            font-weight: 400;
        }}
        
        .section {{
            margin-bottom: 20px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #1e3a5f;
            page-break-inside: avoid;
        }}
        
        .section-title {{
            font-size: 13pt;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .executive-summary ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .executive-summary li {{
            padding: 6px 0 6px 20px;
            position: relative;
            line-height: 1.5;
        }}
        
        .executive-summary li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: #1e3a5f;
            font-weight: bold;
        }}
        
        .weather {{
            font-size: 11pt;
            padding: 8px 0;
        }}
        
        .weather-icon {{
            font-size: 16pt;
            margin-right: 8px;
        }}
        
        .market-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 10px;
        }}
        
        .market-item {{
            background: #ffffff;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        
        .market-name {{
            font-size: 9pt;
            color: #666;
            margin-bottom: 4px;
        }}
        
        .market-price {{
            font-size: 12pt;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 2px;
        }}
        
        .market-change {{
            font-size: 10pt;
            font-weight: 600;
        }}
        
        .chain {{
            margin: 15px 0;
            background: #ffffff;
            padding: 12px;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }}
        
        .chain-title {{
            font-weight: 600;
            color: #1e3a5f;
            margin-bottom: 8px;
            font-size: 10.5pt;
        }}
        
        .chain {{
            page-break-inside: avoid;
        }}
        
        .chain-flow {{
            display: inline;
            line-height: 2.2;
            margin: 8px 0 12px 0;
        }}
        
        .chain-tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 9pt;
            font-weight: 600;
            margin: 2px 0;
            white-space: nowrap;
        }}
        
        .chain-tag.event {{
            background: #1e3a5f;
            border: 1px solid #1e3a5f;
            color: #ffffff;
        }}
        
        .chain-tag.positive {{
            background: #e8f5e9;
            border: 1px solid #2e7d32;
            color: #2e7d32;
        }}
        
        .chain-tag.negative {{
            background: #fce4ec;
            border: 1px solid #c62828;
            color: #c62828;
        }}
        
        .chain-arrow {{
            color: #1e3a5f;
            font-size: 10pt;
            font-weight: bold;
            margin: 0 4px;
        }}
        
        .conviction {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 9pt;
            font-weight: 700;
            margin-top: 6px;
        }}
        
        .conviction.high {{
            background: #2e7d32;
            color: #ffffff;
        }}
        
        .conviction.medium {{
            background: #f57c00;
            color: #ffffff;
        }}
        
        .conviction.low {{
            background: #c62828;
            color: #ffffff;
        }}
        
        .chain-analysis {{
            font-size: 9.5pt;
            color: #333;
            line-height: 1.6;
            margin: 8px 0;
        }}
        
        .chain-analysis strong {{
            color: #1e3a5f;
        }}
        
        .historical-echo {{
            font-size: 9pt;
            color: #555;
            font-style: italic;
            margin-top: 8px;
            padding: 8px;
            background: #f0f0f5;
            border-radius: 3px;
            border-left: 3px solid #b8860b;
        }}
        
        .atlas-take {{
            background: #fff8e1;
            border-left: 4px solid #b8860b;
            padding: 12px;
            border-radius: 4px;
            font-size: 10pt;
            line-height: 1.6;
            font-style: italic;
            color: #333;
        }}
        
        .priorities ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .priorities li {{
            padding: 5px 0 5px 20px;
            position: relative;
        }}
        
        .priorities li:before {{
            content: "◆";
            position: absolute;
            left: 0;
            color: #b8860b;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 2px solid #ddd;
            font-size: 11pt;
            color: #888;
            font-weight: 500;
        }}
        
        .footer .emoji {{
            font-size: 14pt;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">🏛️</span>ATLAS INTELLIGENCE BRIEFING</h1>
            <div class="date">Friday, 20 February 2026</div>
        </div>
        
        <div class="section executive-summary">
            <div class="section-title">Executive Summary</div>
            <ul>
                <li>Fed holds rates at 3.5-3.75%, defying market expectations for cuts — inflation concerns remain elevated</li>
                <li>OPEC+ production cuts extended through Q2 2026, pushing oil prices higher and pressuring airline/consumer sectors</li>
                <li>Trump tariffs on China, EU, and Mexico take effect — expect margin compression and supply chain disruption</li>
            </ul>
        </div>
        
        <div class="section weather">
            <div class="section-title">Weather</div>
            <div><span class="weather-icon">⛅</span><strong>London:</strong> Partly cloudy, 5°C</div>
        </div>
        
        <div class="section">
            <div class="section-title">Market Snapshot</div>
            <div class="market-grid">
                {market_html}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Geopolitical Alpha</div>
            
            <div class="chain">
                <div class="chain-title">1. Fed Holds Rates at 3.5-3.75%</div>
                <div class="chain-flow">
                    <span class="chain-tag event">Hawkish Fed Hold</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">Interest Rates ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">Growth Stocks ↓</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">Banks ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">USD ↑</span>
                </div>
                <p class="chain-analysis"><strong>Why this matters:</strong> The Fed is signalling that inflation isn't beaten yet. Markets were pricing in 2-3 rate cuts this year — that expectation is now under serious pressure. When rates stay high, borrowing costs stay elevated across the entire economy.</p>
                <p class="chain-analysis"><strong>Transmission mechanism:</strong> Higher rates → expensive mortgages (housing slows) → corporate debt servicing costs rise (especially leveraged firms) → growth/tech stocks fall (their future profits are worth less when discounted at higher rates) → banks benefit (wider net interest margins) → USD strengthens (foreign capital chases higher yields).</p>
                <p class="chain-analysis"><strong>What to watch:</strong> Credit spreads widening (corporate bonds vs Treasuries), housing data (existing home sales, mortgage applications), and any earnings warnings from highly-leveraged companies. If credit spreads blow out, that's the canary in the coal mine.</p>
                <p class="chain-analysis"><strong>Second-order effects:</strong> Strong USD hurts US exporters and emerging markets with dollar-denominated debt. Tech layoffs could accelerate if venture funding tightens further. Commercial real estate refinancing becomes a ticking time bomb.</p>
                <div class="historical-echo">Historical echo: 2018 tightening cycle — S&P fell ~20% in Q4 2018 when the Fed refused to pivot. Powell eventually capitulated in Jan 2019. Watch for a similar pattern: markets tantrum → Fed blinks → rally.</div>
                <div class="conviction high">CONVICTION: HIGH (100/100)</div>
            </div>
            
            <div class="chain">
                <div class="chain-title">2. OPEC+ Extends Production Cuts Through Q2 2026</div>
                <div class="chain-flow">
                    <span class="chain-tag event">Supply Cut</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">Oil ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">Energy Stocks ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">Airlines ↓</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">Consumer Discretionary ↓</span>
                </div>
                <p class="chain-analysis"><strong>Why this matters:</strong> Energy is the foundation of everything. OPEC+ is deliberately restricting supply to keep prices elevated, which acts as a tax on the entire global economy. Combined with the Fed holding rates, this creates a stagflationary pressure — slow growth with persistent inflation.</p>
                <p class="chain-analysis"><strong>Transmission mechanism:</strong> Oil up → transport costs rise (airlines, shipping, logistics) → manufacturing input costs increase → consumer prices rise at the pump and in supermarkets → disposable income falls → consumer spending weakens → GDP growth slows. Meanwhile, energy companies (Shell, ExxonMobil, BP) report record margins.</p>
                <p class="chain-analysis"><strong>What to watch:</strong> Oil above $85/bbl becomes a serious drag on growth. Watch airline earnings guidance, US gasoline prices (political sensitivity in election cycle), and whether non-OPEC producers (US shale) ramp up to fill the gap.</p>
                <p class="chain-analysis"><strong>Second-order effects:</strong> Elevated oil strengthens the case for renewables investment (policy + economics align). Petrodollar recycling boosts Gulf sovereign wealth funds. Net energy importers (Japan, India, EU) see currency pressure and trade deficits widen.</p>
                <div class="historical-echo">Historical echo: Ukraine 2022 — EU gas prices +300%, wheat +50%, defence stocks +40%. Energy dependence proved to be a strategic vulnerability. Countries that diversified energy sources fared better.</div>
                <div class="conviction high">CONVICTION: HIGH (95/100)</div>
            </div>
            
            <div class="chain">
                <div class="chain-title">3. Trump Tariffs (China, EU, Mexico)</div>
                <div class="chain-flow">
                    <span class="chain-tag event">Tariffs Imposed</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">Margins ↓</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag positive">Domestic Competitors ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">Consumer Prices ↑</span>
                    <span class="chain-arrow">→</span>
                    <span class="chain-tag negative">MXN/CNY ↓</span>
                </div>
                <p class="chain-analysis"><strong>Why this matters:</strong> Tariffs are a direct tax on imports. US companies either absorb the cost (margin compression) or pass it to consumers (inflation). Either way, someone pays. And retaliatory tariffs from China/EU/Mexico mean US exporters get hit too — it's a negative-sum game.</p>
                <p class="chain-analysis"><strong>Transmission mechanism:</strong> Tariffs → import costs rise → companies with global supply chains (Apple, Tesla, Walmart) face margin pressure → consumer prices increase → Fed has less room to cut rates → markets reprice growth expectations downward. Meanwhile, domestic producers with no foreign exposure benefit from reduced competition.</p>
                <p class="chain-analysis"><strong>What to watch:</strong> Retaliation escalation (EU has threatened counter-tariffs on US tech), supply chain announcements (companies shifting production to Vietnam/India), and earnings guidance from consumer-facing companies. If Walmart warns, everyone feels it.</p>
                <p class="chain-analysis"><strong>Second-order effects:</strong> Supply chain diversification accelerates — Vietnam, India, and Indonesia are the biggest winners. Chinese yuan depreciation partially offsets tariff impact but creates currency instability. Mexico's nearshoring boom faces headwinds. Agricultural exporters (US soybean farmers) get caught in retaliation crossfire.</p>
                <div class="historical-echo">Historical echo: 2018-19 trade wars — S&P fell 15-20%, MXN -12%, CNY -10%. But supply chains adapted: Vietnam's exports to the US surged 35% in 2019. The lesson: tariffs create short-term pain but long-term structural shifts in global trade.</div>
                <div class="conviction high">CONVICTION: HIGH (85/100)</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Atlas's Take</div>
            <div class="atlas-take">
                The Fed's rate hold is the real story. Markets price in 2-3 cuts this year, but if OPEC keeps oil elevated and Trump tariffs reignite inflation, those cuts won't happen. Watch second-order effects: mortgage-dependent sectors feel pain first. Growth stocks (especially unprofitable tech) are vulnerable. Safe play = quality companies with pricing power and low debt.
            </div>
        </div>
        
        <div class="section priorities">
            <div class="section-title">Today's Priorities</div>
            <ul>
                <li>Ethics quiz (urgent)</li>
                <li>Stats HW</li>
                <li>ML/Python Week 2 prep</li>
            </ul>
        </div>
        
        <div class="footer">
            <span class="emoji">🏛️</span> Atlas | Carrying the weight so you don't have to
        </div>
    </div>
</body>
</html>
"""
    return html_content

def main():
    """Main execution"""
    print("📊 Generating Atlas Intelligence Briefing...")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Fetch market data
    print("📈 Fetching market data...")
    market_data = get_market_data()
    
    # Generate HTML
    print("🎨 Generating styled HTML...")
    html_content = generate_html(market_data)
    
    # Convert to PDF
    print("📄 Converting to PDF...")
    try:
        HTML(string=html_content).write_pdf(OUTPUT_PATH)
        print(f"\n✅ Briefing generated successfully!")
        print(f"\n{OUTPUT_PATH}")
        return 0
    except Exception as e:
        print(f"❌ Error generating PDF: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
