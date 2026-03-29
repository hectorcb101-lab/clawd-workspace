// ============================================================================
// Atlas Intel — Prediction Markets Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { PredictionContract } from '@/types/index';

// ---------------------------------------------------------------------------
// Sort options
// ---------------------------------------------------------------------------

type SortKey = 'volume' | 'probability';

// ---------------------------------------------------------------------------
// Mock prediction contracts — realistic geopolitical questions
// ---------------------------------------------------------------------------

function generatePredictions(): PredictionContract[] {
  return [
    {
      id: 'pred-01',
      question: 'Will there be a ceasefire in Ukraine before July 2026?',
      probability: 0.12,
      volume: 8_420_000,
      url: 'https://polymarket.com',
      category: 'Conflict',
    },
    {
      id: 'pred-02',
      question: 'Will China impose a naval blockade on Taiwan in 2026?',
      probability: 0.04,
      volume: 5_150_000,
      url: 'https://polymarket.com',
      category: 'Geopolitics',
    },
    {
      id: 'pred-03',
      question: 'Will the US Federal Reserve cut rates in Q2 2026?',
      probability: 0.62,
      volume: 12_300_000,
      url: 'https://polymarket.com',
      category: 'Economics',
    },
    {
      id: 'pred-04',
      question: 'Will Iran reach nuclear breakout capability in 2026?',
      probability: 0.18,
      volume: 3_800_000,
      url: 'https://polymarket.com',
      category: 'Nuclear',
    },
    {
      id: 'pred-05',
      question: 'Will North Korea conduct a nuclear test in 2026?',
      probability: 0.15,
      volume: 2_940_000,
      url: 'https://polymarket.com',
      category: 'Nuclear',
    },
    {
      id: 'pred-06',
      question: 'Will oil exceed $100/bbl before December 2026?',
      probability: 0.28,
      volume: 6_780_000,
      url: 'https://polymarket.com',
      category: 'Energy',
    },
    {
      id: 'pred-07',
      question: 'Will there be a major cyberattack on US infrastructure in 2026?',
      probability: 0.35,
      volume: 4_120_000,
      url: 'https://polymarket.com',
      category: 'Cyber',
    },
    {
      id: 'pred-08',
      question: 'Will Turkey invoke NATO Article 5 by end of 2026?',
      probability: 0.02,
      volume: 1_560_000,
      url: 'https://polymarket.com',
      category: 'Geopolitics',
    },
    {
      id: 'pred-09',
      question: 'Will Bitcoin exceed $150,000 in 2026?',
      probability: 0.38,
      volume: 15_200_000,
      url: 'https://polymarket.com',
      category: 'Economics',
    },
    {
      id: 'pred-10',
      question: 'Will Russia use a tactical nuclear weapon in 2026?',
      probability: 0.03,
      volume: 7_900_000,
      url: 'https://polymarket.com',
      category: 'Nuclear',
    },
    {
      id: 'pred-11',
      question: 'Will a new pandemic be declared by the WHO in 2026?',
      probability: 0.08,
      volume: 3_250_000,
      url: 'https://polymarket.com',
      category: 'Health',
    },
    {
      id: 'pred-12',
      question: 'Will the Suez Canal be blocked for >48h in 2026?',
      probability: 0.14,
      volume: 2_680_000,
      url: 'https://polymarket.com',
      category: 'Maritime',
    },
    {
      id: 'pred-13',
      question: 'Will Venezuela invade Guyana (Essequibo) in 2026?',
      probability: 0.05,
      volume: 1_920_000,
      url: 'https://polymarket.com',
      category: 'Conflict',
    },
    {
      id: 'pred-14',
      question: 'Will the EU impose new sanctions on China in 2026?',
      probability: 0.42,
      volume: 4_500_000,
      url: 'https://polymarket.com',
      category: 'Geopolitics',
    },
    {
      id: 'pred-15',
      question: 'Will a major sovereign debt default occur in 2026?',
      probability: 0.22,
      volume: 3_100_000,
      url: 'https://polymarket.com',
      category: 'Economics',
    },
  ];
}

// ---------------------------------------------------------------------------
// PredictionPanel
// ---------------------------------------------------------------------------

export class PredictionPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private listEl!: HTMLElement;
  private sortBarEl!: HTMLElement;
  private contracts: PredictionContract[] = [];
  private sortKey: SortKey = 'volume';

  constructor() {
    super({
      id: 'predictions',
      title: 'PREDICTION MARKETS',
      icon: '🎯',
      description: 'Geopolitical prediction contracts with probability and volume data',
      defaultOpen: false,
    });

    this.buildUI();
    this.render();
  }

  // ── UI scaffolding ──────────────────────────────────────────────────────

  private buildUI(): void {
    this.sortBarEl = h('div', { class: 'prediction-sort-bar' });
    this.listEl = h('div', { class: 'prediction-list' });
    replaceChildren(this.body, this.sortBarEl, this.listEl);
    this.renderSortBar();
  }

  private renderSortBar(): void {
    const volBtn = h(
      'button',
      {
        class: `filter-btn${this.sortKey === 'volume' ? ' active' : ''}`,
        onClick: () => this.setSort('volume'),
      },
      '↕ Volume',
    );
    const probBtn = h(
      'button',
      {
        class: `filter-btn${this.sortKey === 'probability' ? ' active' : ''}`,
        onClick: () => this.setSort('probability'),
      },
      '↕ Probability',
    );
    replaceChildren(this.sortBarEl, volBtn, probBtn);
  }

  private setSort(key: SortKey): void {
    this.sortKey = key;
    this.renderSortBar();
    this.render();
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    if (this.contracts.length === 0) {
      replaceChildren(
        this.listEl,
        h('div', { class: 'prediction-empty' }, 'Awaiting prediction data…'),
      );
      this.setFooter('No data');
      return;
    }

    const sorted = [...this.contracts].sort((a, b) => {
      if (this.sortKey === 'volume') return b.volume - a.volume;
      return b.probability - a.probability;
    });

    const elements = sorted.map(c => this.renderContract(c));
    replaceChildren(this.listEl, ...elements);

    this.setBadge(this.contracts.length);
    this.setFooter(`${this.contracts.length} contracts · Sorted by ${this.sortKey}`);
  }

  private renderContract(contract: PredictionContract): HTMLElement {
    const pct = Math.round(contract.probability * 100);
    const volStr = this.formatVolume(contract.volume);

    // Probability bar colour: green if >60%, yellow 30-60%, red <30%
    let barColor = '#f44336';
    if (pct >= 60) barColor = '#00e676';
    else if (pct >= 30) barColor = '#ffeb3b';

    // Question text
    const question = h('div', { class: 'prediction-question' }, contract.question);

    // Category badge
    const categoryBadge = contract.category
      ? h('span', { class: 'prediction-category' }, contract.category)
      : null;

    // Probability bar
    const bar = h(
      'div',
      { class: 'prediction-bar-track' },
      h('div', {
        class: 'prediction-bar-fill',
        style: `width:${pct}%;background:${barColor}`,
      }),
    );

    const probLabel = h('span', { class: 'prediction-prob' }, `${pct}%`);

    const barRow = h(
      'div',
      { class: 'prediction-bar-row' },
      bar,
      probLabel,
    );

    // Meta: volume + link
    const volEl = h('span', { class: 'prediction-volume' }, `Vol: $${volStr}`);
    const linkEl = h(
      'a',
      {
        class: 'prediction-link',
        href: contract.url,
        target: '_blank',
        rel: 'noopener noreferrer',
      },
      '↗ View',
    );

    const metaChildren: (Node | string)[] = [volEl];
    if (categoryBadge) metaChildren.push(categoryBadge);
    metaChildren.push(linkEl);

    const meta = h('div', { class: 'prediction-meta' }, ...metaChildren);

    return h(
      'div',
      { class: 'prediction-item' },
      question,
      barRow,
      meta,
    );
  }

  private formatVolume(v: number): string {
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
    return String(v);
  }

  // ── Auto-refresh ────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.doRefresh();
    this.refreshTimer = setInterval(() => this.doRefresh(), 300_000);
  }

  protected onClose(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  async refresh(): Promise<void> {
    await this.doRefresh();
  }

  private async doRefresh(): Promise<void> {
    try {
      this.setFooter('Fetching predictions…');
      // In production, fetch from Polymarket / Metaculus APIs
      this.contracts = generatePredictions();
      this.render();
    } catch {
      this.setFooter('Prediction data fetch failed');
    }
  }
}
