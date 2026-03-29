// ============================================================================
// Atlas Intel — D3.js 7-Day Timeline Chart
// ============================================================================
//
// SVG-based responsive timeline showing events over the past 7 days,
// color-coded by severity. Hover tooltips show event details.
// Uses D3.js for scales, axes, and DOM manipulation.
// ============================================================================

import * as d3 from 'd3';
import type { TimelineEvent, SeverityLevel } from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MARGIN = { top: 20, right: 20, bottom: 30, left: 16 };
const CIRCLE_RADIUS = 5;
const CIRCLE_RADIUS_HOVER = 8;
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  critical: '#ff1744',
  high:     '#ff5252',
  elevated: '#ffc107',
  guarded:  '#29b6f6',
  low:      '#00e676',
};

const SEVERITY_ORDER: Record<SeverityLevel, number> = {
  critical: 0,
  high:     1,
  elevated: 2,
  guarded:  3,
  low:      4,
};

// ---------------------------------------------------------------------------
// TimelineChart
// ---------------------------------------------------------------------------

export class TimelineChart {
  private container: HTMLElement;
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private g: d3.Selection<SVGGElement, unknown, null, undefined>;
  private tooltip: HTMLElement;
  private xScale!: d3.ScaleTime<number, number>;
  private yScale!: d3.ScalePoint<string>;
  private events: TimelineEvent[] = [];
  private resizeObserver: ResizeObserver | null = null;
  private width = 0;
  private height = 0;

  constructor(container: HTMLElement) {
    this.container = container;

    // Create SVG
    this.svg = d3
      .select(container)
      .append('svg')
      .attr('class', 'timeline-chart')
      .style('width', '100%')
      .style('height', '100%')
      .style('overflow', 'visible');

    this.g = this.svg.append('g')
      .attr('transform', `translate(${MARGIN.left},${MARGIN.top})`);

    // Create tooltip
    this.tooltip = document.createElement('div');
    this.tooltip.className = 'timeline-tooltip';
    Object.assign(this.tooltip.style, {
      position: 'absolute',
      display: 'none',
      pointerEvents: 'none',
      background: 'rgba(10, 12, 18, 0.95)',
      border: '1px solid rgba(255, 255, 255, 0.15)',
      borderRadius: '4px',
      padding: '8px 10px',
      fontSize: '11px',
      color: '#e0e0e0',
      fontFamily: 'var(--font-mono, monospace)',
      zIndex: '9999',
      maxWidth: '260px',
      lineHeight: '1.4',
      boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
    });
    container.style.position = 'relative';
    container.appendChild(this.tooltip);

    // Setup layers
    this.g.append('g').attr('class', 'grid-lines');
    this.g.append('g').attr('class', 'x-axis');
    this.g.append('g').attr('class', 'events-layer');

    // Observe resize
    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(container);

    this.resize();
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /**
   * Set the timeline data and re-render.
   */
  setData(events: TimelineEvent[]): void {
    this.events = events;
    this.renderChart();
  }

  /**
   * Clean up DOM elements, observers, and event listeners.
   */
  destroy(): void {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
    this.tooltip.remove();
    this.svg.remove();
  }

  // ── Sizing ────────────────────────────────────────────────────────────────

  private resize(): void {
    const rect = this.container.getBoundingClientRect();
    this.width = Math.max(100, rect.width - MARGIN.left - MARGIN.right);
    this.height = Math.max(60, rect.height - MARGIN.top - MARGIN.bottom);

    this.svg
      .attr('viewBox', `0 0 ${rect.width} ${rect.height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    this.renderChart();
  }

  // ── Render ────────────────────────────────────────────────────────────────

  private renderChart(): void {
    if (this.width <= 0 || this.height <= 0) return;

    this.setupScales();
    this.renderGridLines();
    this.renderXAxis();
    this.renderEvents();
  }

  private setupScales(): void {
    const now = Date.now();
    const sevenDaysAgo = now - SEVEN_DAYS_MS;

    this.xScale = d3.scaleTime()
      .domain([new Date(sevenDaysAgo), new Date(now)])
      .range([0, this.width]);

    // Y-axis: distribute severity levels evenly
    const severityLevels: SeverityLevel[] = ['critical', 'high', 'elevated', 'guarded', 'low'];
    this.yScale = d3.scalePoint<string>()
      .domain(severityLevels)
      .range([CIRCLE_RADIUS + 2, this.height - CIRCLE_RADIUS - 2])
      .padding(0.3);
  }

  private renderGridLines(): void {
    const gridGroup = this.g.select<SVGGElement>('.grid-lines');
    gridGroup.selectAll('*').remove();

    // Vertical day markers
    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;
    for (let i = 1; i <= 7; i++) {
      const dayTime = now - i * dayMs;
      const x = this.xScale(new Date(dayTime));
      gridGroup.append('line')
        .attr('x1', x)
        .attr('x2', x)
        .attr('y1', 0)
        .attr('y2', this.height)
        .attr('stroke', 'rgba(255,255,255,0.06)')
        .attr('stroke-dasharray', '2,3');
    }

    // Horizontal severity lanes
    const severities: SeverityLevel[] = ['critical', 'high', 'elevated', 'guarded', 'low'];
    for (const sev of severities) {
      const y = this.yScale(sev) ?? 0;
      gridGroup.append('line')
        .attr('x1', 0)
        .attr('x2', this.width)
        .attr('y1', y)
        .attr('y2', y)
        .attr('stroke', `${SEVERITY_COLORS[sev]}15`)
        .attr('stroke-width', 1);

      // Severity label
      gridGroup.append('text')
        .attr('x', -2)
        .attr('y', y)
        .attr('dy', '0.35em')
        .attr('text-anchor', 'end')
        .attr('fill', `${SEVERITY_COLORS[sev]}80`)
        .attr('font-size', '7px')
        .attr('font-family', 'var(--font-mono, monospace)')
        .text(sev.charAt(0).toUpperCase());
    }
  }

  private renderXAxis(): void {
    const axisGroup = this.g.select<SVGGElement>('.x-axis');
    axisGroup.selectAll('*').remove();

    const xAxis = d3.axisBottom(this.xScale)
      .ticks(7)
      .tickFormat((d) => {
        const date = d as Date;
        return d3.timeFormat('%b %d')(date);
      })
      .tickSize(-this.height)
      .tickPadding(8);

    axisGroup
      .attr('transform', `translate(0,${this.height})`)
      .call(xAxis)
      .call(g => {
        g.select('.domain').attr('stroke', 'rgba(255,255,255,0.1)');
        g.selectAll('.tick line')
          .attr('stroke', 'rgba(255,255,255,0.04)')
          .attr('stroke-dasharray', '1,2');
        g.selectAll('.tick text')
          .attr('fill', 'rgba(255,255,255,0.4)')
          .attr('font-size', '9px')
          .attr('font-family', 'var(--font-mono, monospace)');
      });
  }

  private renderEvents(): void {
    const eventsLayer = this.g.select<SVGGElement>('.events-layer');
    eventsLayer.selectAll('*').remove();

    // Filter to events within the 7-day window
    const now = Date.now();
    const cutoff = now - SEVEN_DAYS_MS;
    const visible = this.events
      .filter(e => e.timestamp >= cutoff && e.timestamp <= now)
      .sort((a, b) => {
        // Render lower severity first so critical dots render on top
        const aSev = a.severity ?? 'low';
        const bSev = b.severity ?? 'low';
        return SEVERITY_ORDER[bSev] - SEVERITY_ORDER[aSev];
      });

    // Data join
    const circles = eventsLayer
      .selectAll<SVGCircleElement, TimelineEvent>('circle')
      .data(visible, (d) => `${d.timestamp}-${d.label}`);

    // Enter
    circles
      .enter()
      .append('circle')
      .attr('cx', d => this.xScale(new Date(d.timestamp)))
      .attr('cy', d => this.yScale(d.severity ?? 'low') ?? this.height / 2)
      .attr('r', 0)
      .attr('fill', d => SEVERITY_COLORS[d.severity ?? 'low'])
      .attr('fill-opacity', 0.8)
      .attr('stroke', d => SEVERITY_COLORS[d.severity ?? 'low'])
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1.5)
      .style('cursor', 'pointer')
      .on('mouseenter', (_event: MouseEvent, d: TimelineEvent) => {
        this.showTooltip(_event, d);
        d3.select(_event.currentTarget as SVGCircleElement)
          .transition()
          .duration(150)
          .attr('r', CIRCLE_RADIUS_HOVER)
          .attr('fill-opacity', 1)
          .attr('stroke-width', 2);
      })
      .on('mousemove', (_event: MouseEvent) => {
        this.moveTooltip(_event);
      })
      .on('mouseleave', (_event: MouseEvent) => {
        this.hideTooltip();
        d3.select(_event.currentTarget as SVGCircleElement)
          .transition()
          .duration(200)
          .attr('r', CIRCLE_RADIUS)
          .attr('fill-opacity', 0.8)
          .attr('stroke-width', 1.5);
      })
      .transition()
      .duration(300)
      .attr('r', CIRCLE_RADIUS);

    // Exit
    circles
      .exit()
      .transition()
      .duration(200)
      .attr('r', 0)
      .remove();

    // Event count annotation
    eventsLayer.append('text')
      .attr('x', this.width)
      .attr('y', -6)
      .attr('text-anchor', 'end')
      .attr('fill', 'rgba(255,255,255,0.3)')
      .attr('font-size', '9px')
      .attr('font-family', 'var(--font-mono, monospace)')
      .text(`${visible.length} events / 7d`);
  }

  // ── Tooltip ───────────────────────────────────────────────────────────────

  private showTooltip(event: MouseEvent, d: TimelineEvent): void {
    const severity = d.severity ?? 'low';
    const color = SEVERITY_COLORS[severity];
    const time = new Date(d.timestamp);
    const timeStr = d3.timeFormat('%b %d, %H:%M UTC')(time);

    this.tooltip.innerHTML = [
      `<div style="color:${color};font-weight:700;margin-bottom:3px">`,
      `  ${severity.toUpperCase()} ${d.type ? `· ${d.type.toUpperCase()}` : ''}`,
      `</div>`,
      `<div style="margin-bottom:3px">${this.escapeHtml(d.label)}</div>`,
      d.country
        ? `<div style="opacity:0.6;font-size:10px">📍 ${this.escapeHtml(d.country)}</div>`
        : '',
      `<div style="opacity:0.5;font-size:10px;margin-top:2px">🕐 ${timeStr}</div>`,
    ].join('');

    this.tooltip.style.display = 'block';
    this.moveTooltip(event);
  }

  private moveTooltip(event: MouseEvent): void {
    const containerRect = this.container.getBoundingClientRect();
    const x = event.clientX - containerRect.left + 12;
    const y = event.clientY - containerRect.top - 10;

    // Prevent overflow on the right
    const tipWidth = this.tooltip.offsetWidth;
    const adjustedX = x + tipWidth > containerRect.width
      ? x - tipWidth - 24
      : x;

    this.tooltip.style.left = `${adjustedX}px`;
    this.tooltip.style.top = `${y}px`;
  }

  private hideTooltip(): void {
    this.tooltip.style.display = 'none';
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}
