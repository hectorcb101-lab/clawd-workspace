// ============================================================================
// Atlas Intel — Airline / Flight Intelligence Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { AirlineIntel } from '@/types/index';

// ---------------------------------------------------------------------------
// Mock realistic airport data (15+ major airports)
// ---------------------------------------------------------------------------

function getMockAirportData(): AirlineIntel[] {
  const now = Date.now();
  return [
    { airport: 'London Heathrow',         code: 'LHR', status: 'delays',    delayMinutes: 35,  flights: 1284, timestamp: now },
    { airport: 'Dubai International',     code: 'DXB', status: 'normal',    delayMinutes: 0,   flights: 1108, timestamp: now },
    { airport: 'John F. Kennedy',         code: 'JFK', status: 'delays',    delayMinutes: 22,  flights: 945,  timestamp: now },
    { airport: 'Los Angeles Intl',        code: 'LAX', status: 'normal',    delayMinutes: 0,   flights: 1012, timestamp: now },
    { airport: 'Paris Charles de Gaulle', code: 'CDG', status: 'disrupted', delayMinutes: 85,  flights: 1065, timestamp: now },
    { airport: 'Frankfurt am Main',       code: 'FRA', status: 'normal',    delayMinutes: 0,   flights: 892,  timestamp: now },
    { airport: 'Istanbul',                code: 'IST', status: 'normal',    delayMinutes: 0,   flights: 1245, timestamp: now },
    { airport: 'Singapore Changi',        code: 'SIN', status: 'normal',    delayMinutes: 0,   flights: 764,  timestamp: now },
    { airport: 'Tokyo Haneda',            code: 'HND', status: 'delays',    delayMinutes: 18,  flights: 835,  timestamp: now },
    { airport: 'Beijing Capital',         code: 'PEK', status: 'normal',    delayMinutes: 0,   flights: 951,  timestamp: now },
    { airport: 'O\'Hare International',   code: 'ORD', status: 'delays',    delayMinutes: 42,  flights: 1156, timestamp: now },
    { airport: 'Amsterdam Schiphol',      code: 'AMS', status: 'normal',    delayMinutes: 0,   flights: 876,  timestamp: now },
    { airport: 'Hong Kong Intl',          code: 'HKG', status: 'normal',    delayMinutes: 0,   flights: 612,  timestamp: now },
    { airport: 'Sydney Kingsford Smith',  code: 'SYD', status: 'normal',    delayMinutes: 0,   flights: 584,  timestamp: now },
    { airport: 'São Paulo Guarulhos',     code: 'GRU', status: 'delays',    delayMinutes: 28,  flights: 672,  timestamp: now },
    { airport: 'Moscow Sheremetyevo',     code: 'SVO', status: 'disrupted', delayMinutes: 120, flights: 410,  timestamp: now },
    { airport: 'Ben Gurion',              code: 'TLV', status: 'closed',    delayMinutes: 0,   flights: 0,    timestamp: now },
    { airport: 'Cairo International',     code: 'CAI', status: 'normal',    delayMinutes: 0,   flights: 348,  timestamp: now },
    { airport: 'Indira Gandhi Intl',      code: 'DEL', status: 'delays',    delayMinutes: 15,  flights: 926,  timestamp: now },
    { airport: 'Doha Hamad Intl',         code: 'DOH', status: 'normal',    delayMinutes: 0,   flights: 568,  timestamp: now },
  ];
}

// ---------------------------------------------------------------------------
// Status configuration
// ---------------------------------------------------------------------------

type AirportStatus = 'normal' | 'delays' | 'disrupted' | 'closed';

const STATUS_CONFIG: Record<AirportStatus, { color: string; bg: string; label: string; icon: string }> = {
  normal:    { color: '#00e676', bg: 'rgba(0,230,118,0.10)',   label: 'NORMAL',    icon: '✈' },
  delays:    { color: '#ffc107', bg: 'rgba(255,193,7,0.10)',   label: 'DELAYS',    icon: '⏱' },
  disrupted: { color: '#ff6d00', bg: 'rgba(255,109,0,0.10)',   label: 'DISRUPTED', icon: '⚠' },
  closed:    { color: '#ff1744', bg: 'rgba(255,23,68,0.10)',   label: 'CLOSED',    icon: '🚫' },
};

// ---------------------------------------------------------------------------
// AirlineIntelPanel
// ---------------------------------------------------------------------------

export class AirlineIntelPanel extends Panel {
  private data: AirlineIntel[] = [];
  private summaryEl!: HTMLElement;
  private listEl!: HTMLElement;

  constructor() {
    super({
      id: 'airline-intel',
      title: 'AIRLINE INTEL',
      icon: '✈️',
      description: 'Global airport status, delays, and flight intelligence',
      defaultOpen: false,
    });

    this.data = getMockAirportData();
    this.buildUI();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    this.summaryEl = h('div', { class: 'airline-summary' });
    this.listEl = h('div', { class: 'airline-list' });

    replaceChildren(this.body, this.summaryEl, this.listEl);
    this.render();
  }

  // ── Render ────────────────────────────────────────────────────────────────

  protected render(): void {
    this.renderSummary();
    this.renderList();

    const alertCount = this.data.filter(
      d => d.status === 'disrupted' || d.status === 'closed',
    ).length;
    this.setBadge(alertCount);
    this.setFooter(
      `${this.data.length} airports · ${alertCount} disrupted/closed · Updated ${new Date().toISOString().slice(11, 19)}Z`,
    );
  }

  private renderSummary(): void {
    const total = this.data.length;
    const normalCount = this.data.filter(d => d.status === 'normal').length;
    const delayCount = this.data.filter(d => d.status === 'delays').length;
    const disruptedCount = this.data.filter(d => d.status === 'disrupted').length;
    const closedCount = this.data.filter(d => d.status === 'closed').length;
    const totalFlights = this.data.reduce((sum, d) => sum + d.flights, 0);

    replaceChildren(
      this.summaryEl,
      h(
        'div',
        {
          class: 'airline-stats',
          style: 'display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;',
        },
        this.buildStatPill('NORMAL', normalCount, STATUS_CONFIG.normal.color),
        this.buildStatPill('DELAYS', delayCount, STATUS_CONFIG.delays.color),
        this.buildStatPill('DISRUPTED', disruptedCount, STATUS_CONFIG.disrupted.color),
        this.buildStatPill('CLOSED', closedCount, STATUS_CONFIG.closed.color),
      ),
      h(
        'div',
        {
          class: 'airline-flight-total',
          style: 'font-size:0.55rem;opacity:0.6;margin-bottom:6px;',
        },
        `${totalFlights.toLocaleString()} tracked flights across ${total} airports`,
      ),
    );
  }

  private buildStatPill(label: string, count: number, color: string): HTMLElement {
    return h(
      'div',
      {
        class: 'airline-stat-pill',
        style: `display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border:1px solid ${color};border-radius:3px;font-size:0.55rem;`,
      },
      h('span', { style: `color:${color};font-weight:bold;font-size:0.7rem;` }, String(count)),
      h('span', { style: `color:${color};opacity:0.8;letter-spacing:0.05em;` }, label),
    );
  }

  private renderList(): void {
    // Sort: closed first, then disrupted, then delays, then normal
    const statusOrder: Record<AirportStatus, number> = {
      closed: 0,
      disrupted: 1,
      delays: 2,
      normal: 3,
    };

    const sorted = [...this.data].sort((a, b) => {
      const orderDiff = statusOrder[a.status] - statusOrder[b.status];
      if (orderDiff !== 0) return orderDiff;
      return b.flights - a.flights;
    });

    const rows = sorted.map(airport => this.buildAirportRow(airport));
    replaceChildren(this.listEl, ...rows);
  }

  private buildAirportRow(airport: AirlineIntel): HTMLElement {
    const config = STATUS_CONFIG[airport.status];

    // Status badge
    const statusBadge = h(
      'span',
      {
        class: `airline-status airline-status-${airport.status}`,
        style: `background:${config.bg};color:${config.color};padding:2px 6px;border-radius:2px;font-size:0.5rem;font-weight:bold;letter-spacing:0.06em;min-width:60px;text-align:center;display:inline-block;`,
      },
      `${config.icon} ${config.label}`,
    );

    // IATA code
    const codeEl = h(
      'span',
      {
        class: 'airline-code',
        style: 'font-weight:bold;font-size:0.7rem;width:32px;color:var(--cyan, #00bcd4);font-family:monospace;',
      },
      airport.code,
    );

    // Airport name
    const nameEl = h(
      'span',
      {
        class: 'airline-name',
        style: 'font-size:0.6rem;flex:1;',
      },
      airport.airport,
    );

    // Delay info
    const delayEl = airport.delayMinutes && airport.delayMinutes > 0
      ? h(
          'span',
          {
            class: 'airline-delay',
            style: `color:${config.color};font-size:0.55rem;font-weight:bold;width:45px;text-align:right;`,
          },
          `+${airport.delayMinutes}m`,
        )
      : h('span', { style: 'width:45px;' });

    // Flight count
    const flightEl = h(
      'span',
      {
        class: 'airline-flights',
        style: 'font-size:0.5rem;opacity:0.5;width:50px;text-align:right;',
      },
      airport.flights > 0 ? `${airport.flights} flt` : '—',
    );

    return h(
      'div',
      {
        class: `airline-row airline-row-${airport.status}`,
        style: `display:flex;align-items:center;gap:8px;padding:5px 4px;border-bottom:1px solid rgba(255,255,255,0.04);border-left:2px solid ${config.color};`,
        title: `${airport.airport} (${airport.code}) — ${config.label}${airport.delayMinutes ? `, avg delay ${airport.delayMinutes}min` : ''}, ${airport.flights} flights`,
      },
      codeEl,
      nameEl,
      statusBadge,
      delayEl,
      flightEl,
    );
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
  }

  async refresh(): Promise<void> {
    this.data = getMockAirportData();
    this.render();
  }
}
