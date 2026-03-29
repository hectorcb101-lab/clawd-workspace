// ============================================================================
// Atlas Intel — Country Intelligence Dossier (Full-Screen Brief)
// ============================================================================
//
// Opens as a full-screen overlay presenting a comprehensive intelligence
// brief for a selected country: instability ring, component bars, AI brief,
// headlines, active signals, timeline placeholder, and infrastructure exposure.
// ============================================================================

import { Panel } from '@/components/Panel';
import { ciiEngine } from '@/services/cii-scoring';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import type {
  CountryScore,
  SeverityLevel,
  Signal,
} from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RING_RADIUS = 54;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  critical: '#ff3333',
  high:     '#ff8800',
  elevated: '#ffd700',
  guarded:  '#4488ff',
  low:      '#00ff66',
};

// ---------------------------------------------------------------------------
// CountryBriefPage
// ---------------------------------------------------------------------------

export class CountryBriefPage extends Panel {
  private overlay: HTMLElement | null = null;
  private currentCode: string | null = null;
  private signals: Signal[] = [];

  constructor() {
    super({
      id: 'country-brief',
      title: 'COUNTRY BRIEF',
      icon: '📋',
      description: 'Full country intelligence dossier',
      defaultOpen: false,
    });
  }

  // -------------------------------------------------------------------------
  // Show / Hide
  // -------------------------------------------------------------------------

  /**
   * Open the full-screen country brief for a given country code.
   */
  show(countryCode: string): void {
    this.currentCode = countryCode.toUpperCase();

    // Remove any existing overlay
    this.hide();

    // Build and mount
    this.overlay = this.buildOverlay();
    document.body.appendChild(this.overlay);
  }

  /**
   * Close the country brief overlay.
   */
  hide(): void {
    if (this.overlay) {
      this.overlay.remove();
      this.overlay = null;
    }
    this.currentCode = null;
  }

  /**
   * Inject external signal data (from the signal engine) for display.
   */
  setSignals(signals: Signal[]): void {
    this.signals = signals;
  }

  // -------------------------------------------------------------------------
  // Build Overlay
  // -------------------------------------------------------------------------

  private buildOverlay(): HTMLElement {
    const score = this.currentCode
      ? ciiEngine.getScore(this.currentCode)
      : undefined;

    const countryName = score?.name ?? this.currentCode ?? 'Unknown';
    const countryFlag = score?.flag ?? '🏳️';

    // --- Header ---
    const header = this.buildHeader(countryFlag, countryName);

    // --- Left column ---
    const leftCol = h('div', null,
      this.buildInstabilityRing(score),
      this.buildComponentBars(score),
      this.buildAIBrief(),
      this.buildHeadlines(score),
    );

    // --- Right column ---
    const rightCol = h('div', null,
      this.buildActiveSignals(),
      this.buildTimeline(),
      this.buildInfrastructure(),
    );

    // --- Two-column grid ---
    const grid = h('div', { class: 'brief-grid' }, leftCol, rightCol);

    // --- Overlay ---
    const overlay = h(
      'div',
      { class: 'country-brief' },
      header,
      grid,
    );

    // Close on Escape key
    const onKey = (e: Event) => {
      if ((e as KeyboardEvent).key === 'Escape') {
        this.hide();
        document.removeEventListener('keydown', onKey);
      }
    };
    document.addEventListener('keydown', onKey);

    return overlay;
  }

  // -------------------------------------------------------------------------
  // Header
  // -------------------------------------------------------------------------

  private buildHeader(flag: string, name: string): HTMLElement {
    const title = h(
      'h2',
      null,
      h('span', { style: 'font-size:1.6rem;margin-right:10px' }, flag),
      name,
    );

    // Export buttons
    const exportJson = h(
      'button',
      {
        class: 'export-btn',
        style: this.exportBtnStyle(),
        onClick: () => this.exportJSON(),
      },
      '⬇ JSON',
    );

    const exportCsv = h(
      'button',
      {
        class: 'export-btn',
        style: this.exportBtnStyle(),
        onClick: () => this.exportCSV(),
      },
      '⬇ CSV',
    );

    const printBtn = h(
      'button',
      {
        class: 'export-btn',
        style: this.exportBtnStyle(),
        onClick: () => window.print(),
      },
      '🖨 Print',
    );

    const closeBtn = h(
      'button',
      {
        class: 'close-btn',
        style: 'background:none;border:1px solid var(--border);border-radius:2px;color:var(--text-secondary);font-size:1rem;cursor:pointer;padding:4px 10px',
        onClick: () => this.hide(),
      },
      '✕',
    );

    const controls = h(
      'div',
      { style: 'display:flex;align-items:center;gap:8px' },
      exportJson,
      exportCsv,
      printBtn,
      closeBtn,
    );

    return h('div', { class: 'brief-header' }, title, controls);
  }

  // -------------------------------------------------------------------------
  // Instability Ring (SVG)
  // -------------------------------------------------------------------------

  private buildInstabilityRing(score?: CountryScore): HTMLElement {
    const value = score?.score ?? 0;
    const severity = ciiEngine.getSeverity(value);
    const color = SEVERITY_COLORS[severity];
    const offset = RING_CIRCUMFERENCE - (value / 100) * RING_CIRCUMFERENCE;

    const section = h('div', { class: 'brief-section' });
    section.innerHTML = `
      <h3>INSTABILITY INDEX</h3>
      <div class="instability-ring">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle cx="70" cy="70" r="${RING_RADIUS}"
            fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10" />
          <circle cx="70" cy="70" r="${RING_RADIUS}"
            fill="none" stroke="${color}" stroke-width="10"
            stroke-dasharray="${RING_CIRCUMFERENCE}"
            stroke-dashoffset="${offset}"
            stroke-linecap="round"
            style="transition: stroke-dashoffset 1s ease">
            <animate attributeName="stroke-dashoffset"
              from="${RING_CIRCUMFERENCE}" to="${offset}"
              dur="1.2s" fill="freeze" />
          </circle>
        </svg>
        <div class="ring-value" style="color:${color}">
          ${value}
          <span class="ring-label">${severity.toUpperCase()}</span>
        </div>
      </div>
    `;

    return section;
  }

  // -------------------------------------------------------------------------
  // Component Bars
  // -------------------------------------------------------------------------

  private buildComponentBars(score?: CountryScore): HTMLElement {
    const components = [
      { label: 'Unrest',      value: score?.unrest ?? 0 },
      { label: 'Security',    value: score?.security ?? 0 },
      { label: 'Information', value: score?.information ?? 0 },
      { label: 'Overall',     value: score?.score ?? 0 },
    ];

    const bars = components.map((comp) => {
      const severity = ciiEngine.getSeverity(comp.value);
      const color = SEVERITY_COLORS[severity];

      return h('div', { class: 'component-bar' },
        h('span', { class: 'label' }, comp.label),
        h('div', { class: 'bar' },
          h('div', {
            class: 'bar-fill',
            style: `width:${comp.value}%;background:${color}`,
          }),
        ),
        h('span', { class: 'value', style: `color:${color}` }, String(comp.value)),
      );
    });

    const section = h('div', { class: 'brief-section' },
      h('h3', null, 'COMPONENT SCORES'),
      ...bars,
    );

    return section;
  }

  // -------------------------------------------------------------------------
  // AI Intelligence Brief
  // -------------------------------------------------------------------------

  private buildAIBrief(): HTMLElement {
    const section = h('div', { class: 'brief-section' },
      h('h3', null, 'AI INTELLIGENCE BRIEF'),
      h('div', { class: 'ai-brief', id: `ai-brief-${this.currentCode}` },
        h('div', {
          style: 'color:var(--text-dim);font-size:0.68rem;font-style:italic',
        }, 'AI brief generation available. Click "Generate Brief" to produce an intelligence summary from current data.'),
        h('button', {
          style: this.exportBtnStyle() + ';margin-top:10px',
          onClick: () => this.requestAIBrief(),
        }, '🤖 Generate Brief'),
      ),
    );

    return section;
  }

  // -------------------------------------------------------------------------
  // Headlines
  // -------------------------------------------------------------------------

  private buildHeadlines(score?: CountryScore): HTMLElement {
    const headlines = score?.headlines ?? [];

    // Pad with placeholder if fewer than 8
    const items: HTMLElement[] = [];
    const displayHeadlines = headlines.slice(0, 8);

    for (let i = 0; i < displayHeadlines.length; i++) {
      const item = displayHeadlines[i];
      items.push(
        h('div', { class: 'news-item' },
          h('div', { class: 'headline' },
            h('a', { href: item.url, target: '_blank', rel: 'noopener' },
              item.title,
            ),
          ),
          h('div', { class: 'meta' },
            h('span', { class: 'source' }, item.source),
            h('span', null, timeAgo(item.timestamp)),
            item.threatCategory
              ? h('span', { class: `threat-badge ${item.threatCategory}` }, item.threatCategory)
              : null,
          ),
        ),
      );
    }

    if (items.length === 0) {
      items.push(
        h('div', {
          style: 'color:var(--text-dim);font-size:0.68rem;font-style:italic;padding:8px 0',
        }, 'No recent headlines for this country.'),
      );
    }

    const section = h('div', { class: 'brief-section' },
      h('h3', null, 'TOP HEADLINES'),
      ...items,
    );

    return section;
  }

  // -------------------------------------------------------------------------
  // Active Signals
  // -------------------------------------------------------------------------

  private buildActiveSignals(): HTMLElement {
    const countrySignals = this.signals.filter(
      (s) => s.countries?.includes(this.currentCode ?? ''),
    );

    let content: HTMLElement;
    if (countrySignals.length > 0) {
      const chips = countrySignals.map((signal) =>
        h('span', {
          class: `signal-chip ${signal.severity}`,
          title: signal.description,
        },
          h('span', null, this.signalIcon(signal.type)),
          h('span', null, signal.title),
        ),
      );
      content = h('div', { style: 'display:flex;flex-wrap:wrap;gap:4px' }, ...chips);
    } else {
      content = h('div', {
        style: 'color:var(--text-dim);font-size:0.68rem;font-style:italic',
      }, 'No active signals for this country.');
    }

    return h('div', { class: 'brief-section' },
      h('h3', null, 'ACTIVE SIGNALS'),
      content,
    );
  }

  // -------------------------------------------------------------------------
  // 7-Day Timeline (D3.js Placeholder)
  // -------------------------------------------------------------------------

  private buildTimeline(): HTMLElement {
    const timelineContainer = h('div', {
      id: `timeline-${this.currentCode}`,
      style: 'width:100%;height:120px;background:rgba(255,255,255,0.02);border:1px dashed var(--border);border-radius:4px;display:flex;align-items:center;justify-content:center',
    },
      h('span', {
        style: 'color:var(--text-dim);font-size:0.6rem;letter-spacing:0.05em',
      }, '7-DAY EVENT TIMELINE · D3.js visualization'),
    );

    return h('div', { class: 'brief-section' },
      h('h3', null, '7-DAY TIMELINE'),
      timelineContainer,
    );
  }

  // -------------------------------------------------------------------------
  // Infrastructure Exposure
  // -------------------------------------------------------------------------

  private buildInfrastructure(): HTMLElement {
    const infraCategories = [
      { icon: '🔌', label: 'Subsea Cables', status: 'Monitoring' },
      { icon: '⚡', label: 'Power Grid',    status: 'Normal' },
      { icon: '🛢️', label: 'Pipelines',     status: 'Normal' },
      { icon: '🌐', label: 'Internet',      status: 'Normal' },
      { icon: '✈️',  label: 'Airports',      status: 'Operational' },
      { icon: '🚢', label: 'Ports',         status: 'Operational' },
    ];

    const rows = infraCategories.map((cat) => {
      const statusColor = cat.status === 'Normal' || cat.status === 'Operational'
        ? 'var(--green)'
        : cat.status === 'Monitoring'
          ? 'var(--amber)'
          : 'var(--red)';

      return h('div', {
        style: 'display:flex;align-items:center;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03)',
      },
        h('span', { style: 'font-size:0.68rem;color:var(--text-primary)' },
          `${cat.icon} ${cat.label}`,
        ),
        h('span', {
          style: `font-size:0.6rem;font-weight:600;color:${statusColor}`,
        }, cat.status),
      );
    });

    return h('div', { class: 'brief-section' },
      h('h3', null, 'INFRASTRUCTURE EXPOSURE'),
      ...rows,
    );
  }

  // -------------------------------------------------------------------------
  // Export Functions
  // -------------------------------------------------------------------------

  private exportJSON(): void {
    if (!this.currentCode) return;
    const score = ciiEngine.getScore(this.currentCode);
    if (!score) return;

    const data = {
      country: score.code,
      name: score.name,
      score: score.score,
      unrest: score.unrest,
      security: score.security,
      information: score.information,
      trend: score.trend,
      trendDelta: score.trendDelta,
      isConflictZone: score.isConflictZone,
      headlines: score.headlines.map((h) => ({
        title: h.title,
        source: h.source,
        url: h.url,
        timestamp: h.timestamp,
        threatCategory: h.threatCategory,
      })),
      exportedAt: new Date().toISOString(),
    };

    this.downloadFile(
      `atlas-intel-${score.code}-${Date.now()}.json`,
      JSON.stringify(data, null, 2),
      'application/json',
    );
  }

  private exportCSV(): void {
    if (!this.currentCode) return;
    const score = ciiEngine.getScore(this.currentCode);
    if (!score) return;

    const rows = [
      ['Field', 'Value'],
      ['Country', score.name],
      ['Code', score.code],
      ['Score', String(score.score)],
      ['Unrest', String(score.unrest)],
      ['Security', String(score.security)],
      ['Information', String(score.information)],
      ['Trend', score.trend],
      ['Trend Delta', String(score.trendDelta)],
      ['Conflict Zone', String(score.isConflictZone)],
      ['', ''],
      ['Headlines', ''],
      ...score.headlines.map((h) => [h.title, h.source]),
    ];

    const csv = rows.map((r) => r.map((c) => `"${c}"`).join(',')).join('\n');

    this.downloadFile(
      `atlas-intel-${score.code}-${Date.now()}.csv`,
      csv,
      'text/csv',
    );
  }

  private downloadFile(filename: string, content: string, mime: string): void {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  // -------------------------------------------------------------------------
  // AI Brief Request
  // -------------------------------------------------------------------------

  private requestAIBrief(): void {
    // Dispatch event so the AI service can pick it up
    const event = new CustomEvent('atlas:request-ai-brief', {
      bubbles: true,
      detail: {
        countryCode: this.currentCode,
        targetElementId: `ai-brief-${this.currentCode}`,
      },
    });
    document.dispatchEvent(event);

    // Show loading state
    const briefEl = this.overlay?.querySelector(`#ai-brief-${this.currentCode}`);
    if (briefEl) {
      replaceChildren(
        briefEl as HTMLElement,
        h('div', {
          style: 'color:var(--accent);font-size:0.68rem;font-style:italic',
        }, '⏳ Generating intelligence brief…'),
      );
    }
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  /** Map signal type to a compact icon. */
  private signalIcon(type: string): string {
    const icons: Record<string, string> = {
      'convergence':           '🔀',
      'triangulation':         '📐',
      'velocity-spike':        '⚡',
      'prediction-leading':    '🔮',
      'news-leads-markets':    '📈',
      'market-move-explained': '💹',
      'silent-divergence':     '🔇',
      'sector-cascade':        '🌊',
      'flow-drop':             '📉',
      'flow-price-divergence': '↕️',
      'geographic-convergence': '🗺️',
      'military-surge':        '⚔️',
    };
    return icons[type] ?? '🔔';
  }

  /** Shared inline style for export buttons. */
  private exportBtnStyle(): string {
    return 'padding:5px 12px;background:var(--accent-faint);border:1px solid var(--accent-dim);border-radius:3px;color:var(--accent);font-family:var(--font);font-size:0.6rem;letter-spacing:0.05em;cursor:pointer';
  }
}
