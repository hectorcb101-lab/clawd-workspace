// ============================================================================
// Atlas Intel — Market Data Service
// ============================================================================

import type { MarketItem, MarketComposite } from '@/types/index';

// ---------------------------------------------------------------------------
// Realistic base prices for major instruments
// ---------------------------------------------------------------------------

interface InstrumentBase {
  ticker: string;
  name: string;
  basePrice: number;
  volatility: number;       // typical % move range
  currency?: string;
  exchange?: string;
  group: 'index' | 'crypto' | 'commodity';
}

const INSTRUMENTS: InstrumentBase[] = [
  // ── Indices ────────────────────────────────────────────────────────────
  { ticker: 'SPX',    name: 'S&P 500',            basePrice: 5_680.25,  volatility: 0.8,  currency: 'USD', exchange: 'NYSE',     group: 'index' },
  { ticker: 'DJIA',   name: 'Dow Jones',           basePrice: 42_150.80, volatility: 0.7,  currency: 'USD', exchange: 'NYSE',     group: 'index' },
  { ticker: 'NDX',    name: 'NASDAQ 100',          basePrice: 20_340.60, volatility: 1.1,  currency: 'USD', exchange: 'NASDAQ',   group: 'index' },
  { ticker: 'FTSE',   name: 'FTSE 100',            basePrice: 8_425.30,  volatility: 0.6,  currency: 'GBP', exchange: 'LSE',      group: 'index' },
  { ticker: 'DAX',    name: 'DAX 40',              basePrice: 18_910.45, volatility: 0.9,  currency: 'EUR', exchange: 'XETRA',    group: 'index' },
  { ticker: 'N225',   name: 'Nikkei 225',          basePrice: 38_450.20, volatility: 1.0,  currency: 'JPY', exchange: 'TSE',      group: 'index' },
  { ticker: 'SHCOMP', name: 'Shanghai Composite',  basePrice: 3_120.80,  volatility: 0.8,  currency: 'CNY', exchange: 'SSE',      group: 'index' },
  { ticker: 'HSI',    name: 'Hang Seng',           basePrice: 17_640.50, volatility: 1.2,  currency: 'HKD', exchange: 'HKEX',     group: 'index' },
  { ticker: 'KOSPI',  name: 'KOSPI',               basePrice: 2_685.40,  volatility: 0.9,  currency: 'KRW', exchange: 'KRX',      group: 'index' },
  { ticker: 'ASX',    name: 'ASX 200',             basePrice: 7_920.15,  volatility: 0.6,  currency: 'AUD', exchange: 'ASX',      group: 'index' },
  { ticker: 'SENSEX', name: 'BSE Sensex',          basePrice: 73_850.90, volatility: 0.8,  currency: 'INR', exchange: 'BSE',      group: 'index' },
  { ticker: 'MOEX',   name: 'MOEX Russia',         basePrice: 3_280.60,  volatility: 1.5,  currency: 'RUB', exchange: 'MOEX',     group: 'index' },

  // ── Crypto ─────────────────────────────────────────────────────────────
  { ticker: 'BTC',    name: 'Bitcoin',             basePrice: 97_420.00, volatility: 3.0,  currency: 'USD', group: 'crypto' },
  { ticker: 'ETH',    name: 'Ethereum',            basePrice: 3_680.50,  volatility: 3.5,  currency: 'USD', group: 'crypto' },
  { ticker: 'SOL',    name: 'Solana',              basePrice: 178.40,    volatility: 5.0,  currency: 'USD', group: 'crypto' },

  // ── Commodities ────────────────────────────────────────────────────────
  { ticker: 'XAU',    name: 'Gold',                basePrice: 2_680.30,  volatility: 0.8,  currency: 'USD', group: 'commodity' },
  { ticker: 'XAG',    name: 'Silver',              basePrice: 31.45,     volatility: 1.2,  currency: 'USD', group: 'commodity' },
  { ticker: 'CL',     name: 'Crude Oil (WTI)',     basePrice: 78.60,     volatility: 1.5,  currency: 'USD', group: 'commodity' },
  { ticker: 'NG',     name: 'Natural Gas',         basePrice: 2.85,      volatility: 2.5,  currency: 'USD', group: 'commodity' },
  { ticker: 'HG',     name: 'Copper',              basePrice: 4.32,      volatility: 1.3,  currency: 'USD', group: 'commodity' },
];

// ---------------------------------------------------------------------------
// Market Data Service
// ---------------------------------------------------------------------------

class MarketDataService {
  private items: MarketItem[] = [];
  private composite: MarketComposite = { score: 50, signals: [], timestamp: 0 };

  /** Fetch market data (placeholder with realistic mock data) */
  async fetch(): Promise<MarketItem[]> {
    // In production, this would call real APIs (Yahoo Finance, CoinGecko, etc.)
    // For now, generate realistic mock data with small random fluctuations
    this.items = this.generateMarketData();
    this.calculateComposite();
    return this.items;
  }

  private generateMarketData(): MarketItem[] {
    return INSTRUMENTS.map(inst => {
      // Random change within volatility band, slightly biased to cluster near 0
      const direction = Math.random() > 0.5 ? 1 : -1;
      const magnitude = Math.random() * inst.volatility;
      const changePercent = parseFloat((direction * magnitude).toFixed(2));
      const change = parseFloat((inst.basePrice * changePercent / 100).toFixed(2));
      const price = parseFloat((inst.basePrice + change).toFixed(2));

      return {
        ticker: inst.ticker,
        name: inst.name,
        price,
        change,
        changePercent,
        currency: inst.currency,
        exchange: inst.exchange,
      };
    });
  }

  private calculateComposite(): void {
    // 7-signal market composite score → 0 to 100 (50 = neutral)
    const signals: string[] = [];
    let score = 50;

    const indices = this.items.filter(i =>
      INSTRUMENTS.find(b => b.ticker === i.ticker)?.group === 'index',
    );
    const crypto = this.items.filter(i =>
      INSTRUMENTS.find(b => b.ticker === i.ticker)?.group === 'crypto',
    );
    const gold = this.items.find(i => i.ticker === 'XAU');
    const oil = this.items.find(i => i.ticker === 'CL');

    // Signal 1: Average index change direction
    const avgIndexChange = indices.reduce((s, i) => s + i.changePercent, 0) / (indices.length || 1);
    if (avgIndexChange > 0.3) {
      score += 8;
      signals.push('Indices broadly positive');
    } else if (avgIndexChange < -0.3) {
      score -= 8;
      signals.push('Indices broadly negative');
    }

    // Signal 2: Volatility (spread of changes)
    const changes = indices.map(i => i.changePercent);
    const maxSpread = Math.max(...changes) - Math.min(...changes);
    if (maxSpread > 2.5) {
      score -= 6;
      signals.push(`High dispersion (${maxSpread.toFixed(1)}% spread)`);
    }

    // Signal 3: Crypto direction
    const avgCryptoChange = crypto.reduce((s, i) => s + i.changePercent, 0) / (crypto.length || 1);
    if (avgCryptoChange > 1) {
      score += 5;
      signals.push('Crypto risk-on');
    } else if (avgCryptoChange < -1) {
      score -= 5;
      signals.push('Crypto risk-off');
    }

    // Signal 4: Gold direction (risk indicator — gold up = fear)
    if (gold) {
      if (gold.changePercent > 0.5) {
        score -= 4;
        signals.push('Gold rising (risk aversion)');
      } else if (gold.changePercent < -0.5) {
        score += 3;
        signals.push('Gold declining (risk appetite)');
      }
    }

    // Signal 5: Oil direction
    if (oil) {
      if (oil.changePercent > 1.5) {
        score -= 3;
        signals.push('Oil spiking (supply concern)');
      } else if (oil.changePercent < -1.5) {
        score += 2;
        signals.push('Oil declining');
      }
    }

    // Signal 6: Number of indices declining
    const declining = indices.filter(i => i.changePercent < 0).length;
    if (declining >= indices.length * 0.75) {
      score -= 7;
      signals.push(`${declining}/${indices.length} indices declining`);
    } else if (declining <= indices.length * 0.25) {
      score += 5;
      signals.push(`${indices.length - declining}/${indices.length} indices advancing`);
    }

    // Signal 7: Max single decline
    const maxDecline = Math.min(...changes, 0);
    if (maxDecline < -2) {
      score -= 5;
      const worst = indices.reduce((a, b) => a.changePercent < b.changePercent ? a : b);
      signals.push(`Sharp drop: ${worst.name} ${maxDecline.toFixed(1)}%`);
    }

    // Clamp score to [0, 100]
    score = Math.max(0, Math.min(100, Math.round(score)));

    this.composite = {
      score,
      signals,
      timestamp: Date.now(),
    };
  }

  getItems(): MarketItem[] {
    return this.items;
  }

  getComposite(): MarketComposite {
    return this.composite;
  }

  /** Get items by group */
  getIndices(): MarketItem[] {
    return this.items.filter(i =>
      INSTRUMENTS.find(b => b.ticker === i.ticker)?.group === 'index',
    );
  }

  getCrypto(): MarketItem[] {
    return this.items.filter(i =>
      INSTRUMENTS.find(b => b.ticker === i.ticker)?.group === 'crypto',
    );
  }

  getCommodities(): MarketItem[] {
    return this.items.filter(i =>
      INSTRUMENTS.find(b => b.ticker === i.ticker)?.group === 'commodity',
    );
  }
}

export const marketData = new MarketDataService();
