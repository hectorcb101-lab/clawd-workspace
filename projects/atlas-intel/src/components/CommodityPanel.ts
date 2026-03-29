// ============================================================================
// Atlas Intel — Commodity Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { CommodityData } from '@/types/index';

// ---------------------------------------------------------------------------
// Mock commodity data with realistic prices
// ---------------------------------------------------------------------------

interface CommodityGroup {
  title: string;
  icon: string;
  items: CommodityData[];
}

function generateCommodityData(): CommodityGroup[] {
  const jitter = (base: number, pct: number): number => {
    const dir = Math.random() > 0.5 ? 1 : -1;
    return parseFloat((dir * base * (Math.random() * pct) / 100).toFixed(2));
  };

  return [
    {
      title: 'ENERGY',
      icon: '⛽',
      items: [
        { name: 'Crude Oil (WTI)',   price: 78.60,  change: jitter(78.60, 1.5),   unit: '$/bbl',   category: 'energy' },
        { name: 'Crude Oil (Brent)', price: 82.35,  change: jitter(82.35, 1.4),   unit: '$/bbl',   category: 'energy' },
        { name: 'Natural Gas',       price: 2.85,   change: jitter(2.85, 2.5),    unit: '$/MMBtu', category: 'energy' },
        { name: 'Coal (Newcastle)',  price: 135.20, change: jitter(135.20, 1.0),  unit: '$/ton',   category: 'energy' },
        { name: 'Gasoline (RBOB)',   price: 2.28,   change: jitter(2.28, 1.8),    unit: '$/gal',   category: 'energy' },
      ],
    },
    {
      title: 'METALS',
      icon: '🥇',
      items: [
        { name: 'Gold',         price: 2_680.30, change: jitter(2_680.30, 0.8), unit: '$/oz',  category: 'metals' },
        { name: 'Silver',       price: 31.45,    change: jitter(31.45, 1.2),    unit: '$/oz',  category: 'metals' },
        { name: 'Copper',       price: 4.32,     change: jitter(4.32, 1.3),     unit: '$/lb',  category: 'metals' },
        { name: 'Platinum',     price: 1_025.80, change: jitter(1_025.80, 1.0), unit: '$/oz',  category: 'metals' },
        { name: 'Palladium',    price: 985.40,   change: jitter(985.40, 1.5),   unit: '$/oz',  category: 'metals' },
        { name: 'Iron Ore',     price: 118.60,   change: jitter(118.60, 1.1),   unit: '$/ton', category: 'metals' },
      ],
    },
    {
      title: 'AGRICULTURE',
      icon: '🌾',
      items: [
        { name: 'Wheat',     price: 5.82,   change: jitter(5.82, 1.5),   unit: '$/bu',  category: 'agriculture' },
        { name: 'Corn',      price: 4.45,   change: jitter(4.45, 1.3),   unit: '$/bu',  category: 'agriculture' },
        { name: 'Soybeans',  price: 12.18,  change: jitter(12.18, 1.0),  unit: '$/bu',  category: 'agriculture' },
        { name: 'Rice',      price: 15.30,  change: jitter(15.30, 0.8),  unit: '$/cwt', category: 'agriculture' },
        { name: 'Coffee',    price: 225.60, change: jitter(225.60, 2.0), unit: '¢/lb',  category: 'agriculture' },
        { name: 'Sugar',     price: 22.40,  change: jitter(22.40, 1.5),  unit: '¢/lb',  category: 'agriculture' },
      ],
    },
  ];
}

// ---------------------------------------------------------------------------
// CommodityPanel
// ---------------------------------------------------------------------------

export class CommodityPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private listEl!: HTMLElement;
  private data: CommodityGroup[] = [];

  constructor() {
    super({
      id: 'commodities',
      title: 'COMMODITIES',
      icon: '🛢️',
      description: 'Global commodity prices across energy, metals, and agriculture',
      defaultOpen: false,
    });

    this.listEl = h('div', { class: 'commodity-list' });
    replaceChildren(this.body, this.listEl);
    this.render();
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    if (this.data.length === 0) {
      replaceChildren(
        this.listEl,
        h('div', { class: 'commodity-empty' }, 'Awaiting commodity data…'),
      );
      this.setFooter('No data');
      return;
    }

    const sections = this.data.map(group => this.renderGroup(group));
    replaceChildren(this.listEl, ...sections);

    const total = this.data.reduce((n, g) => n + g.items.length, 0);
    this.setBadge(total);
    this.setFooter(`${total} commodities · Updated just now`);
  }

  private renderGroup(group: CommodityGroup): HTMLElement {
    const header = h(
      'div',
      { class: 'commodity-group-header' },
      h('span', null, group.icon),
      h('span', null, ` ${group.title}`),
    );

    const rows = group.items.map(item => this.renderItem(item));

    return h('div', { class: 'commodity-group' }, header, ...rows);
  }

  private renderItem(item: CommodityData): HTMLElement {
    const isPositive = item.change >= 0;
    const changeClass = isPositive ? 'change-positive' : 'change-negative';
    const sign = isPositive ? '+' : '';
    const pct = (item.change / item.price) * 100;

    const name = h('span', { class: 'commodity-name' }, item.name);
    const price = h('span', { class: 'commodity-price' }, `${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${item.unit}`);
    const change = h(
      'span',
      { class: `commodity-change ${changeClass}` },
      `${sign}${item.change.toFixed(2)} (${sign}${pct.toFixed(2)}%)`,
    );

    return h(
      'div',
      { class: 'commodity-item' },
      h('div', { class: 'commodity-item-left' }, name),
      h('div', { class: 'commodity-item-right' }, price, change),
    );
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
      this.setFooter('Fetching commodity data…');
      // In production, fetch from real APIs
      this.data = generateCommodityData();
      this.render();
    } catch {
      this.setFooter('Commodity data fetch failed');
    }
  }
}
