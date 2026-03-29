// ============================================================================
// Atlas Intel — Energy Complex Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { EnergyData } from '@/types/index';

// ---------------------------------------------------------------------------
// Extended energy data with sub-types
// ---------------------------------------------------------------------------

interface EnergyInstrument extends EnergyData {
  name: string;
  change: number;
  benchmark?: string;
}

interface EnergyGroup {
  title: string;
  icon: string;
  items: EnergyInstrument[];
}

function jitter(base: number, pct: number): number {
  const dir = Math.random() > 0.5 ? 1 : -1;
  return parseFloat((dir * base * (Math.random() * pct) / 100).toFixed(2));
}

function generateEnergyData(): EnergyGroup[] {
  return [
    {
      title: 'OIL',
      icon: '🛢️',
      items: [
        {
          name: 'Brent Crude',
          type: 'oil',
          benchmark: 'ICE',
          price: 82.35,
          change: jitter(82.35, 1.5),
          unit: '$/bbl',
          production: 101.2,
          consumption: 102.8,
        },
        {
          name: 'WTI Crude',
          type: 'oil',
          benchmark: 'NYMEX',
          price: 78.60,
          change: jitter(78.60, 1.5),
          unit: '$/bbl',
          production: 13.3,
          consumption: 20.1,
        },
        {
          name: 'Dubai Crude',
          type: 'oil',
          benchmark: 'DME',
          price: 80.15,
          change: jitter(80.15, 1.3),
          unit: '$/bbl',
          production: 0,
          consumption: 0,
        },
        {
          name: 'OPEC Basket',
          type: 'oil',
          benchmark: 'OPEC',
          price: 81.90,
          change: jitter(81.90, 1.2),
          unit: '$/bbl',
          production: 27.0,
          consumption: 0,
        },
      ],
    },
    {
      title: 'NATURAL GAS',
      icon: '🔥',
      items: [
        {
          name: 'Henry Hub',
          type: 'gas',
          benchmark: 'NYMEX',
          price: 2.85,
          change: jitter(2.85, 2.5),
          unit: '$/MMBtu',
          production: 103.5,
          consumption: 89.2,
        },
        {
          name: 'TTF (Dutch)',
          type: 'gas',
          benchmark: 'ICE',
          price: 34.20,
          change: jitter(34.20, 2.0),
          unit: '€/MWh',
          production: 0,
          consumption: 45.8,
        },
        {
          name: 'JKM (Asian LNG)',
          type: 'gas',
          benchmark: 'Platts',
          price: 12.80,
          change: jitter(12.80, 1.8),
          unit: '$/MMBtu',
          production: 0,
          consumption: 0,
        },
      ],
    },
    {
      title: 'COAL & SOLID FUELS',
      icon: '⚫',
      items: [
        {
          name: 'Newcastle Coal',
          type: 'coal',
          benchmark: 'ICE',
          price: 135.20,
          change: jitter(135.20, 1.0),
          unit: '$/ton',
          production: 8_700,
          consumption: 8_500,
        },
        {
          name: 'Rotterdam Coal',
          type: 'coal',
          benchmark: 'ICE',
          price: 118.50,
          change: jitter(118.50, 1.2),
          unit: '$/ton',
          production: 0,
          consumption: 0,
        },
      ],
    },
    {
      title: 'NUCLEAR & URANIUM',
      icon: '☢️',
      items: [
        {
          name: 'Uranium (U₃O₈)',
          type: 'nuclear',
          benchmark: 'Spot',
          price: 82.50,
          change: jitter(82.50, 1.5),
          unit: '$/lb',
          production: 58_000,
          consumption: 62_500,
        },
        {
          name: 'SWU (Enrichment)',
          type: 'nuclear',
          benchmark: 'Spot',
          price: 168.00,
          change: jitter(168.00, 0.8),
          unit: '$/SWU',
          production: 0,
          consumption: 0,
        },
      ],
    },
    {
      title: 'RENEWABLES & POWER',
      icon: '⚡',
      items: [
        {
          name: 'EU Carbon (EUA)',
          type: 'renewable',
          benchmark: 'ICE',
          price: 65.30,
          change: jitter(65.30, 2.0),
          unit: '€/ton',
          production: 0,
          consumption: 0,
        },
        {
          name: 'German Power (Base)',
          type: 'renewable',
          benchmark: 'EEX',
          price: 72.80,
          change: jitter(72.80, 2.5),
          unit: '€/MWh',
          production: 520,
          consumption: 495,
        },
        {
          name: 'PJM Power (US)',
          type: 'renewable',
          benchmark: 'PJM',
          price: 38.50,
          change: jitter(38.50, 3.0),
          unit: '$/MWh',
          production: 0,
          consumption: 0,
        },
      ],
    },
  ];
}

// ---------------------------------------------------------------------------
// EnergyPanel
// ---------------------------------------------------------------------------

export class EnergyPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private listEl!: HTMLElement;
  private data: EnergyGroup[] = [];

  constructor() {
    super({
      id: 'energy',
      title: 'ENERGY COMPLEX',
      icon: '⚡',
      description: 'Global energy markets: oil benchmarks, natural gas, coal, nuclear, and power',
      defaultOpen: false,
    });

    this.listEl = h('div', { class: 'energy-list' });
    replaceChildren(this.body, this.listEl);
    this.render();
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    if (this.data.length === 0) {
      replaceChildren(
        this.listEl,
        h('div', { class: 'energy-empty' }, 'Awaiting energy data…'),
      );
      this.setFooter('No data');
      return;
    }

    const sections = this.data.map(group => this.renderGroup(group));
    replaceChildren(this.listEl, ...sections);

    const total = this.data.reduce((n, g) => n + g.items.length, 0);
    this.setBadge(total);
    this.setFooter(`${total} instruments · Updated just now`);
  }

  private renderGroup(group: EnergyGroup): HTMLElement {
    const header = h(
      'div',
      { class: 'energy-group-header' },
      h('span', null, group.icon),
      h('span', null, ` ${group.title}`),
    );

    const rows = group.items.map(item => this.renderItem(item));
    return h('div', { class: 'energy-group' }, header, ...rows);
  }

  private renderItem(item: EnergyInstrument): HTMLElement {
    const isPositive = item.change >= 0;
    const changeClass = isPositive ? 'change-positive' : 'change-negative';
    const sign = isPositive ? '+' : '';
    const pct = item.price !== 0 ? (item.change / item.price) * 100 : 0;

    // Name + benchmark
    const nameEl = h('span', { class: 'energy-name' }, item.name);
    const benchEl = item.benchmark
      ? h('span', { class: 'energy-benchmark' }, item.benchmark)
      : null;

    // Price + change
    const priceEl = h(
      'span',
      { class: 'energy-price' },
      `${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${item.unit}`,
    );
    const changeEl = h(
      'span',
      { class: `energy-change ${changeClass}` },
      `${sign}${item.change.toFixed(2)} (${sign}${pct.toFixed(2)}%)`,
    );

    // Production vs consumption indicator
    let balanceEl: HTMLElement | null = null;
    if (item.production > 0 && item.consumption > 0) {
      const ratio = item.production / item.consumption;
      const balanceLabel = ratio >= 1.0 ? 'SURPLUS' : 'DEFICIT';
      const balanceClass = ratio >= 1.0 ? 'balance-surplus' : 'balance-deficit';
      balanceEl = h(
        'span',
        { class: `energy-balance ${balanceClass}` },
        `${balanceLabel} ${((ratio - 1) * 100).toFixed(1)}%`,
      );
    }

    const leftChildren: (Node | string)[] = [nameEl];
    if (benchEl) leftChildren.push(benchEl);

    const rightChildren: (Node | string)[] = [priceEl, changeEl];
    if (balanceEl) rightChildren.push(balanceEl);

    return h(
      'div',
      { class: 'energy-item' },
      h('div', { class: 'energy-item-left' }, ...leftChildren),
      h('div', { class: 'energy-item-right' }, ...rightChildren),
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
      this.setFooter('Fetching energy data…');
      this.data = generateEnergyData();
      this.render();
    } catch {
      this.setFooter('Energy data fetch failed');
    }
  }
}
