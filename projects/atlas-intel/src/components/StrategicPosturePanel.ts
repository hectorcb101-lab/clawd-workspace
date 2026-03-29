// ============================================================================
// Atlas Intel — Strategic Posture Panel
// ============================================================================
//
// Displays real-time theater posture assessments across 9 operational theaters.
// Each theater card shows posture level, asset counts, recent events, and trend.
// Clicking a theater dispatches a map navigation event.
// ============================================================================

import { Panel } from '@/components/Panel';
import { theaterPosture } from '@/services/theater-posture';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import type { TheaterPosture, PostureLevel, Trend } from '@/types/index';

// ---------------------------------------------------------------------------
// StrategicPosturePanel
// ---------------------------------------------------------------------------

export class StrategicPosturePanel extends Panel {
  private postures: TheaterPosture[] = [];

  constructor() {
    super({
      id: 'strategic-posture',
      title: 'THEATER POSTURE',
      icon: '🎯',
      description: 'Strategic theater posture assessment across 9 operational theaters',
      defaultOpen: false,
    });
  }

  // -------------------------------------------------------------------------
  // Data Update
  // -------------------------------------------------------------------------

  /**
   * Push new posture data into the panel and re-render.
   */
  update(postures: TheaterPosture[]): void {
    this.postures = postures;

    // Badge: count of theaters at HIGH or above
    const alertCount = theaterPosture.countElevatedTheaters(postures);
    this.setBadge(alertCount);

    this.render();
  }

  // -------------------------------------------------------------------------
  // Refresh — called externally on data cycle
  // -------------------------------------------------------------------------

  override async refresh(): Promise<void> {
    // Re-render with whatever data we have; the orchestrator feeds us via update()
    this.render();
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  protected override render(): void {
    if (this.postures.length === 0) {
      replaceChildren(
        this.body,
        h('div', { class: 'empty-state', style: 'text-align:center;padding:20px;color:var(--text-dim);font-size:0.7rem' },
          'Awaiting theater posture data…',
        ),
      );
      return;
    }

    const cards = this.postures.map((posture) => this.renderTheaterCard(posture));
    replaceChildren(this.body, ...cards);

    // Footer: last updated timestamp
    const latest = Math.max(...this.postures.map((p) => p.lastUpdated));
    this.setFooter(`Updated ${timeAgo(latest)} · ${this.postures.length} theaters`);
  }

  // -------------------------------------------------------------------------
  // Theater Card
  // -------------------------------------------------------------------------

  private renderTheaterCard(posture: TheaterPosture): HTMLElement {
    // --- Posture badge ---
    const levelClass = this.postureClass(posture.posture);
    const badge = h(
      'span',
      { class: `posture-level ${levelClass}` },
      posture.posture,
    );

    // --- Theater name ---
    const name = h('div', { class: 'theater-name' }, posture.name, ' ', badge);

    // --- Stats row ---
    const trendSymbol = this.trendSymbol(posture.trend);
    const trendClass = posture.trend;

    const stats = h(
      'div',
      { class: 'stats' },
      h('span', null, `✈ ${posture.militaryFlights} flights`),
      h('span', null, `🚢 ${posture.navalVessels} vessels`),
      h('span', null, `📰 ${posture.recentEvents.length} events`),
      h('span', { class: `trend ${trendClass}`, style: this.trendColor(posture.trend) }, trendSymbol),
    );

    // --- Recent events (compact list) ---
    let eventsEl: HTMLElement | null = null;
    if (posture.recentEvents.length > 0) {
      const eventItems = posture.recentEvents.slice(0, 3).map((title) =>
        h('div', {
          style: 'font-size:0.58rem;color:var(--text-dim);padding:1px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%',
        }, `· ${title}`),
      );
      eventsEl = h('div', { style: 'margin-top:4px' }, ...eventItems);
    }

    // --- Card container ---
    const card = h(
      'div',
      {
        class: 'theater-card',
        style: 'cursor:pointer',
        onClick: () => this.onTheaterClick(posture),
      },
      name,
      stats,
      ...(eventsEl ? [eventsEl] : []),
    );

    return card;
  }

  // -------------------------------------------------------------------------
  // Event Dispatch
  // -------------------------------------------------------------------------

  /**
   * Dispatch a custom event when a theater card is clicked, allowing
   * the map to fly to the theater's center coordinates.
   */
  private onTheaterClick(posture: TheaterPosture): void {
    const event = new CustomEvent('atlas:theater-click', {
      bubbles: true,
      detail: {
        theaterId: posture.id,
        name: posture.name,
        lat: posture.region.lat,
        lng: posture.region.lng,
        posture: posture.posture,
      },
    });
    document.dispatchEvent(event);
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  /** Map posture level to CSS class. */
  private postureClass(level: PostureLevel): string {
    switch (level) {
      case 'CRIT':     return 'crit';
      case 'HIGH':     return 'high';
      case 'ELEVATED': return 'elevated';
      case 'NORMAL':   return 'normal';
    }
  }

  /** Map trend to arrow symbol. */
  private trendSymbol(trend: Trend): string {
    switch (trend) {
      case 'rising':  return '▲';
      case 'falling': return '▼';
      case 'stable':  return '─';
    }
  }

  /** Inline trend color for the symbol. */
  private trendColor(trend: Trend): string {
    switch (trend) {
      case 'rising':  return 'color:var(--red)';
      case 'falling': return 'color:var(--green)';
      case 'stable':  return 'color:var(--text-dim)';
    }
  }
}
