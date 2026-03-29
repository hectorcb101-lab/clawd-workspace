// ============================================================================
// Atlas Intel — CII Panel (Country Instability Index)
// ============================================================================

import { Panel } from '@/components/Panel';
import { ciiEngine } from '@/services/cii-scoring';
import { h } from '@/utils/dom-utils';
import type { CountryScore, SeverityLevel } from '@/types/index';

// ---------------------------------------------------------------------------
// CII Panel
// ---------------------------------------------------------------------------

export class CIIPanel extends Panel {
  constructor() {
    super({
      id: 'cii',
      title: 'INSTABILITY INDEX',
      icon: '⚡',
      description: 'Country Instability Index — 24 monitored countries',
      defaultOpen: false,
    });
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  protected render(): void {
    const scores = ciiEngine.getScores();
    this.body.innerHTML = '';

    // Learning-mode banner
    if (ciiEngine.isLearning) {
      const elapsed = Math.floor(ciiEngine.uptime / 1000);
      const remaining = Math.max(0, 900 - elapsed); // 15 min = 900s
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;

      const banner = h(
        'div',
        {
          class: 'cii-learning',
          style:
            'padding:8px 10px;margin-bottom:8px;background:rgba(255,215,0,0.08);' +
            'border:1px solid rgba(255,215,0,0.25);border-radius:3px;' +
            'font-size:0.6rem;color:var(--amber);display:flex;' +
            'align-items:center;gap:6px;letter-spacing:0.05em;',
        },
        h('span', null, '◉'),
        h(
          'span',
          null,
          `LEARNING MODE — calibrating scores (${mins}:${String(secs).padStart(2, '0')} remaining)`,
        ),
      );
      this.body.appendChild(banner);
    }

    // Country rows
    scores.forEach((cs, i) => {
      const severity = ciiEngine.getSeverity(cs.score);
      const row = this.buildCountryRow(cs, i + 1, severity);
      this.body.appendChild(row);
    });

    // Badge = count of high + critical countries
    const alertCount = scores.filter((s) => s.score >= 66).length;
    this.setBadge(alertCount);

    // Footer timestamp
    this.setFooter(`Updated ${new Date().toISOString().slice(11, 19)}Z`);
  }

  // -------------------------------------------------------------------------
  // Country Row Builder
  // -------------------------------------------------------------------------

  private buildCountryRow(
    cs: CountryScore,
    rank: number,
    severity: SeverityLevel,
  ): HTMLElement {
    // --- Rank ---
    const rankEl = h('span', { class: 'rank' }, String(rank));

    // --- Flag ---
    const flagEl = h('span', { class: 'flag' }, cs.flag);

    // --- Name ---
    const nameEl = h('span', { class: 'name' }, cs.name);

    // --- Score (color-coded by severity) ---
    const scoreEl = h(
      'span',
      { class: `score ${severity}` },
      String(cs.score),
    );

    // --- Bar ---
    const barFill = h('div', {
      class: 'bar-fill',
      style: `width:${cs.score}%;background:${this.severityColor(cs.score)}`,
    });
    const barContainer = h('div', { class: 'bar-container' }, barFill);

    // --- Trend arrow ---
    let trendChar: string;
    let trendClass: string;
    if (cs.trend === 'rising') {
      trendChar = '▲';
      trendClass = 'trend rising';
    } else if (cs.trend === 'falling') {
      trendChar = '▼';
      trendClass = 'trend falling';
    } else {
      trendChar = '─';
      trendClass = 'trend stable';
    }
    const deltaText =
      cs.trendDelta !== 0
        ? ` ${cs.trendDelta > 0 ? '+' : ''}${cs.trendDelta}`
        : '';
    const trendEl = h(
      'span',
      { class: trendClass, title: `Δ${deltaText}` },
      trendChar,
    );

    // --- Breakdown tooltip text ---
    const breakdownText = `U:${cs.unrest} S:${cs.security} I:${cs.information}`;
    const breakdownEl = h(
      'span',
      { class: 'cii-breakdown' },
      breakdownText,
    );

    // --- Assemble row ---
    const row = h(
      'div',
      {
        class: 'cii-country',
        title: `${cs.name} — CII ${cs.score} (${breakdownText})`,
        onClick: () => {
          document.dispatchEvent(
            new CustomEvent('atlas:country-click', {
              detail: { code: cs.code, name: cs.name },
            }),
          );
        },
      },
      rankEl,
      flagEl,
      nameEl,
      scoreEl,
      barContainer,
      trendEl,
      breakdownEl,
    );

    return row;
  }

  // -------------------------------------------------------------------------
  // Severity Color
  // -------------------------------------------------------------------------

  private severityColor(score: number): string {
    if (score >= 81) return 'var(--severity-critical)';
    if (score >= 66) return 'var(--severity-high)';
    if (score >= 46) return 'var(--severity-elevated)';
    if (score >= 26) return 'var(--severity-guarded)';
    return 'var(--severity-low)';
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  protected onOpen(): void {
    this.render();
  }

  async refresh(): Promise<void> {
    this.render();
  }
}
