// ============================================================================
// Atlas Intel — Climate Anomaly Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { ClimateAnomaly } from '@/types/index';

// ---------------------------------------------------------------------------
// Mock realistic climate anomaly data
// ---------------------------------------------------------------------------

function getMockAnomalyData(): ClimateAnomaly[] {
  const now = Date.now();
  return [
    // Temperature anomalies (°C deviation from 1991–2020 baseline)
    { zone: 'Arctic',              type: 'temperature',    deviation: +3.8,  baseline: -12.0, current: -8.2,  timestamp: now },
    { zone: 'North America',       type: 'temperature',    deviation: +1.2,  baseline: 14.5,  current: 15.7,  timestamp: now },
    { zone: 'Europe',              type: 'temperature',    deviation: +1.9,  baseline: 11.3,  current: 13.2,  timestamp: now },
    { zone: 'Central Asia',        type: 'temperature',    deviation: +2.1,  baseline: 8.6,   current: 10.7,  timestamp: now },
    { zone: 'East Asia',           type: 'temperature',    deviation: +0.8,  baseline: 13.2,  current: 14.0,  timestamp: now },
    { zone: 'Tropics',             type: 'temperature',    deviation: +0.6,  baseline: 26.8,  current: 27.4,  timestamp: now },
    { zone: 'Southern Hemisphere', type: 'temperature',    deviation: -0.3,  baseline: 14.1,  current: 13.8,  timestamp: now },

    // Precipitation anomalies (% deviation from baseline)
    { zone: 'Arctic',              type: 'precipitation',  deviation: +18.0, baseline: 22,    current: 26,    timestamp: now },
    { zone: 'North America',       type: 'precipitation',  deviation: -8.5,  baseline: 76,    current: 69.5,  timestamp: now },
    { zone: 'Europe',              type: 'precipitation',  deviation: +12.3, baseline: 68,    current: 76.4,  timestamp: now },
    { zone: 'Central Asia',        type: 'precipitation',  deviation: -22.0, baseline: 35,    current: 27.3,  timestamp: now },
    { zone: 'East Asia',           type: 'precipitation',  deviation: +6.4,  baseline: 110,   current: 117,   timestamp: now },
    { zone: 'Tropics',             type: 'precipitation',  deviation: -5.2,  baseline: 180,   current: 170.6, timestamp: now },
    { zone: 'Southern Hemisphere', type: 'precipitation',  deviation: +3.1,  baseline: 85,    current: 87.6,  timestamp: now },
  ];
}

// ---------------------------------------------------------------------------
// Zone icons
// ---------------------------------------------------------------------------

const ZONE_ICONS: Record<string, string> = {
  'Arctic': '🧊',
  'North America': '🌎',
  'Europe': '🌍',
  'Central Asia': '🏔️',
  'East Asia': '🌏',
  'Tropics': '🌴',
  'Southern Hemisphere': '🌐',
};

// ---------------------------------------------------------------------------
// ClimateAnomalyPanel
// ---------------------------------------------------------------------------

export class ClimateAnomalyPanel extends Panel {
  private data: ClimateAnomaly[] = [];
  private tempSection!: HTMLElement;
  private precipSection!: HTMLElement;

  constructor() {
    super({
      id: 'climate',
      title: 'CLIMATE ANOMALIES',
      icon: '🌡️',
      description: 'Temperature and precipitation anomalies by global zone',
      defaultOpen: false,
    });

    this.data = getMockAnomalyData();
    this.buildUI();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    const tempHeader = h(
      'div',
      { class: 'climate-section-header', style: 'margin-bottom:6px;' },
      '🌡️ TEMPERATURE ANOMALIES (°C vs baseline)',
    );
    this.tempSection = h('div', { class: 'climate-temp-section' });

    const precipHeader = h(
      'div',
      { class: 'climate-section-header', style: 'margin-top:12px;margin-bottom:6px;' },
      '🌧️ PRECIPITATION ANOMALIES (% vs baseline)',
    );
    this.precipSection = h('div', { class: 'climate-precip-section' });

    replaceChildren(this.body, tempHeader, this.tempSection, precipHeader, this.precipSection);
    this.render();
  }

  // ── Color coding ──────────────────────────────────────────────────────────

  private getTemperatureColor(deviation: number): string {
    if (deviation >= 3.0) return '#ff1744';      // extreme hot
    if (deviation >= 2.0) return '#ff5252';      // very hot
    if (deviation >= 1.0) return '#ff8a65';      // hot
    if (deviation >= 0.3) return '#ffab91';      // warm
    if (deviation > -0.3) return '#90a4ae';      // near normal
    if (deviation > -1.0) return '#80cbc4';      // cool
    if (deviation > -2.0) return '#4dd0e1';      // cold
    return '#1de9b6';                             // extreme cold
  }

  private getPrecipitationColor(deviation: number): string {
    if (deviation >= 15) return '#2196f3';        // very wet
    if (deviation >= 5) return '#64b5f6';         // wet
    if (deviation > -5) return '#90a4ae';         // near normal
    if (deviation > -15) return '#ffab91';        // dry
    return '#ff5252';                              // very dry
  }

  private getAnomalyLabel(deviation: number, type: 'temperature' | 'precipitation'): string {
    const abs = Math.abs(deviation);
    if (type === 'temperature') {
      if (abs < 0.3) return 'NORMAL';
      if (abs < 1.0) return deviation > 0 ? 'WARM' : 'COOL';
      if (abs < 2.0) return deviation > 0 ? 'HOT' : 'COLD';
      if (abs < 3.0) return deviation > 0 ? 'VERY HOT' : 'VERY COLD';
      return deviation > 0 ? 'EXTREME HOT' : 'EXTREME COLD';
    } else {
      if (abs < 5) return 'NORMAL';
      if (abs < 15) return deviation > 0 ? 'WET' : 'DRY';
      if (abs < 25) return deviation > 0 ? 'VERY WET' : 'VERY DRY';
      return deviation > 0 ? 'EXTREME WET' : 'EXTREME DRY';
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────

  protected render(): void {
    this.renderTemperature();
    this.renderPrecipitation();

    const extremeCount = this.data.filter(d => {
      if (d.type === 'temperature') return Math.abs(d.deviation) >= 2.0;
      return Math.abs(d.deviation) >= 15;
    }).length;

    this.setBadge(extremeCount);
    this.setFooter(`${this.data.length} observations · ${extremeCount} extreme anomalies`);
  }

  private renderTemperature(): void {
    const tempData = this.data.filter(d => d.type === 'temperature');

    // Sort by deviation descending (hottest first)
    tempData.sort((a, b) => b.deviation - a.deviation);

    // Max bar scale
    const maxDev = Math.max(...tempData.map(d => Math.abs(d.deviation)));

    const rows = tempData.map(d => this.buildAnomalyRow(d, maxDev, 'temperature'));
    replaceChildren(this.tempSection, ...rows);
  }

  private renderPrecipitation(): void {
    const precipData = this.data.filter(d => d.type === 'precipitation');

    // Sort by absolute deviation descending
    precipData.sort((a, b) => Math.abs(b.deviation) - Math.abs(a.deviation));

    const maxDev = Math.max(...precipData.map(d => Math.abs(d.deviation)));

    const rows = precipData.map(d => this.buildAnomalyRow(d, maxDev, 'precipitation'));
    replaceChildren(this.precipSection, ...rows);
  }

  private buildAnomalyRow(
    d: ClimateAnomaly,
    maxDev: number,
    type: 'temperature' | 'precipitation',
  ): HTMLElement {
    const color = type === 'temperature'
      ? this.getTemperatureColor(d.deviation)
      : this.getPrecipitationColor(d.deviation);

    const icon = ZONE_ICONS[d.zone] ?? '🌐';
    const label = this.getAnomalyLabel(d.deviation, type);
    const barWidth = Math.max(3, (Math.abs(d.deviation) / maxDev) * 100);
    const isPositive = d.deviation >= 0;
    const unit = type === 'temperature' ? '°C' : '%';
    const sign = d.deviation > 0 ? '+' : '';

    // Deviation bar (centered — grows left for negative, right for positive)
    const barContainer = h(
      'div',
      {
        class: 'climate-bar-container',
        style: 'flex:1;height:12px;display:flex;align-items:center;position:relative;',
      },
    );

    // Simple directional bar
    const bar = h('div', {
      class: 'climate-bar',
      style: `width:${barWidth}%;height:10px;background:${color};border-radius:2px;` +
        (isPositive ? 'margin-left:auto;' : 'margin-right:auto;'),
    });
    barContainer.appendChild(bar);

    const zoneEl = h(
      'span',
      { class: 'climate-zone', style: 'width:120px;font-size:0.6rem;display:flex;align-items:center;gap:4px;' },
      h('span', null, icon),
      h('span', null, d.zone),
    );

    const deviationEl = h(
      'span',
      {
        class: 'climate-deviation',
        style: `color:${color};font-weight:bold;font-size:0.7rem;width:55px;text-align:right;`,
      },
      `${sign}${d.deviation.toFixed(1)}${unit}`,
    );

    const labelEl = h(
      'span',
      {
        class: 'climate-label',
        style: `color:${color};font-size:0.45rem;font-weight:bold;letter-spacing:0.08em;width:70px;text-align:center;`,
      },
      label,
    );

    const currentEl = h(
      'span',
      { class: 'climate-current', style: 'font-size:0.5rem;opacity:0.5;width:65px;text-align:right;' },
      `${d.current.toFixed(1)} / ${d.baseline.toFixed(1)}`,
    );

    return h(
      'div',
      {
        class: 'climate-row',
        style: 'display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);',
        title: `${d.zone}: ${sign}${d.deviation.toFixed(1)}${unit} (current: ${d.current.toFixed(1)}, baseline: ${d.baseline.toFixed(1)})`,
      },
      zoneEl,
      barContainer,
      deviationEl,
      labelEl,
      currentEl,
    );
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
  }

  async refresh(): Promise<void> {
    this.data = getMockAnomalyData();
    this.render();
  }
}
