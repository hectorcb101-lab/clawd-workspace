# Atlas Intelligence Briefing System

Professional daily intelligence briefings in PDF format.

## Overview

Generates a styled, dark-themed intelligence briefing combining:
- Live market data (via yfinance)
- Geopolitical analysis with visual transmission chains
- Weather, priorities, and executive summaries
- Bloomberg-terminal inspired design aesthetic

## Usage

```bash
cd ~/clawd/intelligence-briefing
python3 generate_pdf_briefing.py
```

Output: `~/clawd/intelligence-briefing/data/history/YYYY-MM-DD_briefing.pdf`

## Features

- **Dark theme** (#1a1a2e background) with Atlas branding
- **Live market data** for S&P 500, FTSE 100, VIX, Oil, Gold, Bitcoin
- **Visual transmission chains** showing geopolitical event → impact flows
- **Colour-coded conviction scores** (green=high, yellow=medium, red=low)
- **Red/green market indicators** for up/down moves
- **A4 portrait** format optimized for printing or digital viewing

## Technical Stack

- **WeasyPrint** - HTML to PDF conversion
- **yfinance** - Live market data (with fallback to placeholders)
- **CSS Grid/Flexbox** - Responsive layout
- **Google Fonts** ready (currently uses system fonts)

## Design Philosophy

Professional, information-dense, Bloomberg-terminal aesthetic:
- Clean typography and spacing
- High contrast for readability
- Visual hierarchy with colour coding
- Classical/Titan branding (🏛️ Atlas)

## Future Integration

Ready for daily cron job automation:
```bash
0 8 * * * cd ~/clawd/intelligence-briefing && python3 generate_pdf_briefing.py
```

## Dependencies

```bash
pip3 install weasyprint yfinance
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2
```

---

**Atlas | Carrying the weight so you don't have to** 🏛️
