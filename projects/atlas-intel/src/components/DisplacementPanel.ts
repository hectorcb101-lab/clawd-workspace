// ============================================================================
// Atlas Intel — UNHCR Displacement Data Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { DisplacementData } from '@/types/index';

// ---------------------------------------------------------------------------
// Mock realistic displacement data (UNHCR mid-2024 estimates)
// ---------------------------------------------------------------------------

function getMockDisplacementData(): DisplacementData[] {
  const now = Date.now();
  return [
    { country: 'Syria',               refugees: 6_800_000,  idps: 6_900_000,  returnees: 380_000,  timestamp: now },
    { country: 'Ukraine',             refugees: 6_300_000,  idps: 5_100_000,  returnees: 120_000,  timestamp: now },
    { country: 'Afghanistan',         refugees: 5_700_000,  idps: 3_200_000,  returnees: 210_000,  timestamp: now },
    { country: 'Venezuela',           refugees: 5_400_000,  idps: 0,          returnees: 15_000,   timestamp: now },
    { country: 'South Sudan',         refugees: 2_300_000,  idps: 2_200_000,  returnees: 340_000,  timestamp: now },
    { country: 'Myanmar',             refugees: 1_300_000,  idps: 1_900_000,  returnees: 5_000,    timestamp: now },
    { country: 'Somalia',             refugees: 800_000,    idps: 3_800_000,  returnees: 95_000,   timestamp: now },
    { country: 'DR Congo',            refugees: 940_000,    idps: 6_900_000,  returnees: 180_000,  timestamp: now },
    { country: 'Sudan',               refugees: 1_100_000,  idps: 7_700_000,  returnees: 42_000,   timestamp: now },
    { country: 'Central African Rep.', refugees: 740_000,   idps: 510_000,    returnees: 88_000,   timestamp: now },
    { country: 'Eritrea',             refugees: 580_000,    idps: 0,          returnees: 0,        timestamp: now },
    { country: 'Burundi',             refugees: 390_000,    idps: 82_000,     returnees: 195_000,  timestamp: now },
    { country: 'Iraq',                refugees: 310_000,    idps: 1_200_000,  returnees: 4_900_000, timestamp: now },
    { country: 'Nigeria',             refugees: 420_000,    idps: 3_600_000,  returnees: 210_000,  timestamp: now },
    { country: 'Ethiopia',            refugees: 260_000,    idps: 4_400_000,  returnees: 310_000,  timestamp: now },
    { country: 'Yemen',               refugees: 60_000,     idps: 4_500_000,  returnees: 27_000,   timestamp: now },
    { country: 'Colombia',            refugees: 290_000,    idps: 6_800_000,  returnees: 12_000,   timestamp: now },
  ];
}

// ---------------------------------------------------------------------------
// DisplacementPanel
// ---------------------------------------------------------------------------

export class DisplacementPanel extends Panel {
  private data: DisplacementData[] = [];
  private summaryEl!: HTMLElement;
  private listEl!: HTMLElement;

  constructor() {
    super({
      id: 'displacement',
      title: 'DISPLACEMENT',
      icon: '🏚️',
      description: 'Global displacement data — refugees, IDPs, and returnees',
      defaultOpen: false,
    });

    this.data = getMockDisplacementData();
    this.buildUI();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    this.summaryEl = h('div', { class: 'displacement-summary' });
    this.listEl = h('div', { class: 'displacement-list' });

    replaceChildren(this.body, this.summaryEl, this.listEl);
    this.render();
  }

  // ── Formatting ────────────────────────────────────────────────────────────

  private formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return String(n);
  }

  private formatNumberFull(n: number): string {
    return n.toLocaleString();
  }

  // ── Render ────────────────────────────────────────────────────────────────

  protected render(): void {
    this.renderSummary();
    this.renderList();
    this.setBadge(this.data.length);
    this.setFooter(`${this.data.length} countries tracked · Source: UNHCR estimates`);
  }

  private renderSummary(): void {
    const totalRefugees = this.data.reduce((sum, d) => sum + d.refugees, 0);
    const totalIDPs = this.data.reduce((sum, d) => sum + d.idps, 0);
    const totalReturnees = this.data.reduce((sum, d) => sum + d.returnees, 0);
    const totalDisplaced = totalRefugees + totalIDPs;

    replaceChildren(
      this.summaryEl,
      h(
        'div',
        { class: 'displacement-total' },
        h(
          'div',
          {
            class: 'displacement-total-number',
            style: 'font-size:1.6rem;font-weight:bold;color:var(--severity-critical, #ff1744);',
          },
          this.formatNumber(totalDisplaced),
        ),
        h(
          'div',
          {
            class: 'displacement-total-label',
            style: 'font-size:0.6rem;opacity:0.7;letter-spacing:0.1em;',
          },
          'TOTAL DISPLACED PERSONS',
        ),
      ),
      h(
        'div',
        {
          class: 'displacement-breakdown',
          style: 'display:flex;gap:16px;margin-top:8px;',
        },
        this.buildStatBox('Refugees', totalRefugees, '#ff6d00'),
        this.buildStatBox('IDPs', totalIDPs, '#ffc107'),
        this.buildStatBox('Returnees', totalReturnees, '#00e676'),
      ),
    );
  }

  private buildStatBox(label: string, value: number, color: string): HTMLElement {
    return h(
      'div',
      {
        class: 'displacement-stat',
        style: 'flex:1;text-align:center;',
      },
      h(
        'div',
        { style: `font-size:0.95rem;font-weight:bold;color:${color};` },
        this.formatNumber(value),
      ),
      h(
        'div',
        { style: 'font-size:0.5rem;opacity:0.6;letter-spacing:0.08em;margin-top:2px;' },
        label.toUpperCase(),
      ),
    );
  }

  private renderList(): void {
    // Sort by total displaced (refugees + IDPs) descending
    const sorted = [...this.data].sort(
      (a, b) => (b.refugees + b.idps) - (a.refugees + a.idps),
    );

    const maxDisplaced = sorted[0].refugees + sorted[0].idps;

    const rows = sorted.map((d, i) => {
      const totalDisplaced = d.refugees + d.idps;
      const barWidth = Math.max(2, (totalDisplaced / maxDisplaced) * 100);

      // Bar segments: refugees (orange) + IDPs (yellow)
      const refugeePct = d.refugees / totalDisplaced * 100;
      const idpPct = d.idps / totalDisplaced * 100;

      const bar = h(
        'div',
        {
          class: 'displacement-bar',
          style: `width:${barWidth}%;height:14px;display:flex;border-radius:2px;overflow:hidden;margin:3px 0;`,
        },
        h('div', {
          class: 'displacement-bar-refugees',
          style: `width:${refugeePct}%;background:#ff6d00;`,
          title: `Refugees: ${this.formatNumberFull(d.refugees)}`,
        }),
        h('div', {
          class: 'displacement-bar-idps',
          style: `width:${idpPct}%;background:#ffc107;`,
          title: `IDPs: ${this.formatNumberFull(d.idps)}`,
        }),
      );

      const rank = h(
        'span',
        { class: 'displacement-rank', style: 'width:18px;opacity:0.4;font-size:0.55rem;' },
        String(i + 1),
      );

      const country = h(
        'span',
        { class: 'displacement-country', style: 'width:110px;font-size:0.6rem;font-weight:bold;' },
        d.country,
      );

      const numbers = h(
        'div',
        { class: 'displacement-numbers', style: 'font-size:0.5rem;opacity:0.65;display:flex;gap:8px;' },
        h('span', { style: 'color:#ff6d00;' }, `REF: ${this.formatNumber(d.refugees)}`),
        h('span', { style: 'color:#ffc107;' }, `IDP: ${this.formatNumber(d.idps)}`),
        d.returnees > 0
          ? h('span', { style: 'color:#00e676;' }, `RET: ${this.formatNumber(d.returnees)}`)
          : null,
      );

      return h(
        'div',
        {
          class: 'displacement-row',
          title: `${d.country}: ${this.formatNumberFull(d.refugees)} refugees, ${this.formatNumberFull(d.idps)} IDPs`,
          style: 'padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);',
        },
        h(
          'div',
          { style: 'display:flex;align-items:center;gap:6px;' },
          rank,
          country,
          h(
            'span',
            { style: 'font-size:0.65rem;margin-left:auto;font-weight:bold;' },
            this.formatNumber(totalDisplaced),
          ),
        ),
        bar,
        numbers,
      );
    });

    // Legend
    const legend = h(
      'div',
      {
        class: 'displacement-legend',
        style: 'display:flex;gap:12px;margin-bottom:8px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.06);',
      },
      h(
        'span',
        { style: 'font-size:0.5rem;display:flex;align-items:center;gap:3px;' },
        h('span', { style: 'width:8px;height:8px;background:#ff6d00;border-radius:1px;display:inline-block;' }),
        'Refugees',
      ),
      h(
        'span',
        { style: 'font-size:0.5rem;display:flex;align-items:center;gap:3px;' },
        h('span', { style: 'width:8px;height:8px;background:#ffc107;border-radius:1px;display:inline-block;' }),
        'IDPs',
      ),
      h(
        'span',
        { style: 'font-size:0.5rem;display:flex;align-items:center;gap:3px;' },
        h('span', { style: 'width:8px;height:8px;background:#00e676;border-radius:1px;display:inline-block;' }),
        'Returnees',
      ),
    );

    replaceChildren(this.listEl, legend, ...rows);
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
  }

  async refresh(): Promise<void> {
    this.data = getMockDisplacementData();
    this.render();
  }
}
