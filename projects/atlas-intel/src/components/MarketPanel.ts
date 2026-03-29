// ============================================================================
// Atlas Intel — Market Data Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import { marketData } from '@/services/market-data';
import type { MarketItem, MarketComposite } from '@/types/index';

// ---------------------------------------------------------------------------
// Composite score colour mapping
// ---------------------------------------------------------------------------

function compositeColor(score: number): string {
  if (score >= 70) return '#00e676';   // green — risk-on
  if (score >= 55) return '#66bb6a';   // light green
  if (score >= 45) return '#ffeb3b';   // neutral yellow
  if (score >= 30) return '#ff9800';   // orange — cautious
  return '#f44336';                     // red — risk-off
}

function compositeLabel(score: number): string {
  if (score >= 70) return 'RISK-ON';
  if (score >= 55) return 'POSITIVE';
  if (score >= 45) return 'NEUTRAL';
  if (score >= 30) return 'CAUTIOUS';
  return 'RISK-OFF';
}

// ---------------------------------------------------------------------------
// MarketPanel
// ---------------------------------------------------------------------------

export class MarketPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private compositeEl!: HTMLElement;
  private listEl!: HTMLElement;

  constructor() {
    super({
      id: 'markets',
      title: 'MARKETS',
      icon: '📈',
      description: 'Global market indices, crypto, and commodities with composite risk score',
      defaultOpen: false,
    });

    this.buildUI();
    this.render();
  }

  // ── UI scaffolding ──────────────────────────────────────────────────────

  private buildUI(): void {
    this.compositeEl = h('div', { class: 'market-composite' });
    this.listEl = h('div', { class: 'market-list' });
    replaceChildren(this.body, this.compositeEl, this.listEl);
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    const items = marketData.getItems();
    const composite = marketData.getComposite();

    this.renderComposite(composite);
    this.renderGroups(items);

    if (items.length > 0) {
      this.setBadge(items.length);
      this.setFooter(`${items.length} instruments · Updated ${timeAgo(composite.timestamp)}`);
    } else {
      this.setFooter('Awaiting market data…');
    }
  }

  private renderComposite(c: MarketComposite): void {
    const color = compositeColor(c.score);
    const label = compositeLabel(c.score);

    const scoreEl = h(
      'div',
      { class: 'composite-score', style: `color:${color}` },
      h('span', { class: 'composite-value' }, String(c.score)),
      h('span', { class: 'composite-label' }, label),
    );

    const signalList = c.signals.length > 0
      ? h(
          'div',
          { class: 'composite-signals' },
          ...c.signals.map(s => h('div', { class: 'composite-signal' }, `• ${s}`)),
        )
      : h('div', { class: 'composite-signals' }, 'No active signals');

    replaceChildren(this.compositeEl, scoreEl, signalList);
  }

  private renderGroups(items: MarketItem[]): void {
    if (items.length === 0) {
      replaceChildren(
        this.listEl,
        h('div', { class: 'market-empty' }, 'No market data. Refresh to load…'),
      );
      return;
    }

    const indices = marketData.getIndices();
    const crypto = marketData.getCrypto();
    const commodities = marketData.getCommodities();

    const sections: (Node | string)[] = [];

    if (indices.length > 0) {
      sections.push(this.renderGroup('INDICES', indices));
    }
    if (crypto.length > 0) {
      sections.push(this.renderGroup('CRYPTO', crypto));
    }
    if (commodities.length > 0) {
      sections.push(this.renderGroup('COMMODITIES', commodities));
    }

    replaceChildren(this.listEl, ...sections);
  }

  private renderGroup(title: string, items: MarketItem[]): HTMLElement {
    const header = h('div', { class: 'market-group-header' }, title);
    const rows = items.map(item => this.renderItem(item));
    return h('div', { class: 'market-group' }, header, ...rows);
  }

  private renderItem(item: MarketItem): HTMLElement {
    const isPositive = item.change >= 0;
    const changeClass = isPositive ? 'change-positive' : 'change-negative';
    const sign = isPositive ? '+' : '';

    const ticker = h('span', { class: 'market-ticker' }, item.ticker);
    const name = h('span', { class: 'market-name' }, item.name);
    const price = h('span', { class: 'market-price' }, this.formatPrice(item));
    const change = h(
      'span',
      { class: `market-change ${changeClass}` },
      `${sign}${item.change.toFixed(2)} (${sign}${item.changePercent.toFixed(2)}%)`,
    );

    return h(
      'div',
      { class: 'market-item' },
      h('div', { class: 'market-item-left' }, ticker, name),
      h('div', { class: 'market-item-right' }, price, change),
    );
  }

  private formatPrice(item: MarketItem): string {
    if (item.price >= 10_000) return item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (item.price >= 100) return item.price.toFixed(2);
    if (item.price >= 1) return item.price.toFixed(2);
    return item.price.toFixed(4);
  }

  // ── Auto-refresh every 5 min ───────────────────────────────────────────

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
      this.setFooter('Fetching market data…');
      await marketData.fetch();
      this.render();
    } catch {
      this.setFooter('Market data fetch failed');
    }
  }
}
