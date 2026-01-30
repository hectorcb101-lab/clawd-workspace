#!/usr/bin/env python3
"""
Yahoo Finance CLI using yfinance library.
Uses inline dependencies for automatic installation.
"""

import sys
import subprocess

# Install yfinance if not available
try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "yfinance", "-q"])
    import yfinance as yf

def get_price(symbol):
    """Get current stock price."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    if not info:
        print(f"❌ No data found for {symbol}")
        return
    
    price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
    change = info.get('regularMarketChangePercent', 0)
    
    emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
    
    print(f"\n{emoji} **{symbol.upper()}**")
    print(f"Price: ${price:,.2f}" if isinstance(price, (int, float)) else f"Price: {price}")
    print(f"Change: {change:+.2f}%" if isinstance(change, (int, float)) else f"Change: {change}")
    print(f"Market Cap: ${info.get('marketCap', 0):,.0f}" if info.get('marketCap') else "")
    print(f"Volume: {info.get('volume', 0):,}" if info.get('volume') else "")

def get_quote(symbol):
    """Get detailed quote."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    if not info:
        print(f"❌ No data found for {symbol}")
        return
    
    print(f"\n📊 **{symbol.upper()} - {info.get('longName', 'N/A')}**\n")
    print(f"Price: ${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}")
    print(f"Change: {info.get('regularMarketChangePercent', 0):+.2f}%")
    print(f"Day Range: ${info.get('dayLow', 'N/A')} - ${info.get('dayHigh', 'N/A')}")
    print(f"52 Week: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"Volume: {info.get('volume', 'N/A'):,}" if isinstance(info.get('volume'), int) else f"Volume: N/A")
    print(f"Market Cap: ${info.get('marketCap', 0):,.0f}" if info.get('marketCap') else "Market Cap: N/A")
    print(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
    print(f"EPS: ${info.get('trailingEps', 'N/A')}")

def search_symbol(query):
    """Search for a symbol (basic implementation)."""
    print(f"\n🔍 Searching for: {query}")
    print("Try specific symbols like: AAPL, MSFT, TSLA, BTC-USD, ^GSPC")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  yf.py <SYMBOL>           # Quick price")
        print("  yf.py price <SYMBOL>     # Quick price")
        print("  yf.py quote <SYMBOL>     # Detailed quote")
        print("  yf.py search <QUERY>     # Search symbol")
        print("\nExamples:")
        print("  yf.py AAPL")
        print("  yf.py quote TSLA")
        print("  yf.py BTC-USD")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ['price', 'quote', 'search']:
        if len(sys.argv) < 3:
            print(f"❌ Missing symbol/query for {command}")
            sys.exit(1)
        symbol = sys.argv[2]
    else:
        symbol = command
        command = 'price'
    
    try:
        if command == 'price':
            get_price(symbol)
        elif command == 'quote':
            get_quote(symbol)
        elif command == 'search':
            search_symbol(symbol)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
