// ============================================================================
// Atlas Intel — Strategic Risk Overview Panel
// ============================================================================
//
// Composite risk overview combining CII averages, convergence alerts,
// theater posture, and cascade analysis into a single severity assessment.
// Shows data freshness badges per source and a learning-mode banner.
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import { ciiEngine } from '@/services/cii-scoring';
import { theaterPosture } from '@/services/theater-posture';
import { dataBridge } from '@/services/data-bridge';
import type {
  CachedRiskScores,
  SeverityLevel,
  DataStatus,
  TheaterPosture as TheaterPostureData,
} from '@/types/index';
import type { ConvergenceAlert } from '@/services/convergence';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  critical: 'var(--severity-critical, #ff1744)',
  high:     'var(--severity-high, #ff5252)',
  elevated: 'var(--severity-elevated, #ffc107)',
  guarded:  'var(--severity-guarded, #29b6f6)',
  low:      'var(--severity-low, #00e676)',
};

const SEVERITY_LABELS: Record<SeverityLevel, string> = {
  critical: 'CRITICAL',
  high:     'HIGH',
  elevated: 'ELEVATED',
  guarded:  'GUARDED',
  low:      'LOW',
};

const STATUS_COLORS: Record<DataStatus['status'], string> = {
  live:        '#00e676',
  cached:      '#ffc107',
  unavailable: '#ff1744',
};

const STATUS_ICONS: Record<DataStatus['status'], string> = {
  live:        '●',
  cached:      '◐',
  unavailable: '○',
};

/** Learning period matches CII engine (15 minutes). */
const LEARNING_PERIOD_MS = 15 * 60 * 1000;

/** Auto-refresh interval. */
const REFRESH_INTERVAL = 30_000;

/** Data sources we track for freshness. */
const TRACKED_SOURCES = ['news', 'military', 'flights', 'vessels', 'earthquakes'];

// ---------------------------------------------------------------------------
// StrategicRiskPanel
// ---------------------------------------------------------------------------

export class StrategicRiskPanel extends Panel {
  private riskScores: CachedRiskScores | null = null;
  private convergenceAlerts: ConvergenceAlert[] = [];
  private postures: TheaterPostureData[] = [];
  private cascadeAlertCount = 0;
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  // DOM refs
  private bannerEl!: HTMLElement;
  private overallEl!: HTMLElement;
  private metricsEl!: HTMLElement;
  private freshnessEl!: HTMLElement;

  constructor() {
    super({
      id: 'strategic-risk',
      title: 'STRATEGIC RISK',
      icon: '🛡️',
      description: 'Composite strategic risk overview across all intelligence domains',
      defaultOpen: false,
    });

    this.buildUI();
    this.startAutoRefresh();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    // Learning mode banner (hidden by default)
    this.bannerEl = h('div', {
      class: 'risk-learning-banner',
      style: 'display:none;padding:6px 10px;background:rgba(255,193,7,0.15);'
        + 'border:1px solid rgba(255,193,7,0.4);border-radius:4px;'
        + 'font-size:11px;color:#ffc107;margin-bottom:8px;text-align:center',
    }, '⏳ LEARNING MODE — System warming up, scores are tentative');

    // Overall severity display
    this.overallEl = h('div', {
      class: 'risk-overall',
      style: 'text-align:center;margin-bottom:12px',
    });

    // Metric cards grid
    this.metricsEl = h('div', {
      class: 'risk-metrics',
      style: 'display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px',
    });

    // Data freshness badges
    this.freshnessEl = h('div', {
      class: 'risk-freshness',
      style: 'display:flex;flex-wrap:wrap;gap:6px;justify-content:center',
    });

    replaceChildren(
      this.body,
      this.bannerEl,
      this.overallEl,
      this.metricsEl,
      this.freshnessEl,
    );

    this.render();
  }

  // ── Data update ───────────────────────────────────────────────────────────

  /**
   * Push fresh risk data into the panel. Called by the orchestrator.
   */
  updateRisk(data: {
    convergenceAlerts?: ConvergenceAlert[];
    postures?: TheaterPostureData[];
    cascadeAlertCount?: number;
  }): void {
    if (data.convergenceAlerts !== undefined) {
      this.convergenceAlerts = data.convergenceAlerts;
    }
    if (data.postures !== undefined) {
      this.postures = data.postures;
    }
    if (data.cascadeAlertCount !== undefined) {
      this.cascadeAlertCount = data.cascadeAlertCount;
    }

    this.recalculate();
    this.render();
  }

  override async refresh(): Promise<void> {
    this.recalculate();
    this.render();
  }

  // ── Composite risk calculation ────────────────────────────────────────────

  private recalculate(): void {
    const scores = ciiEngine.getScores();
    const ciiAvg = scores.length > 0
      ? Math.round(scores.reduce((sum, s) => sum + s.score, 0) / scores.length)
      : 0;

    const convergenceCount = this.convergenceAlerts.length;

    const postureHighCount = theaterPosture.countElevatedTheaters(this.postures);

    const cascadeCount = this.cascadeAlertCount;

    // Composite severity: weighted formula
    const composite = this.computeComposite(
      ciiAvg,
      convergenceCount,
      postureHighCount,
      cascadeCount,
    );

    const overall = this.compositeToSeverity(composite);

    this.riskScores = {
      ciiAvg,
      convergenceAlerts: convergenceCount,
      postureAlerts: postureHighCount,
      cascadeAlerts: cascadeCount,
      overall,
      timestamp: Date.now(),
    };

    this.setBadge(
      overall === 'critical' ? 1 : overall === 'high' ? 1 : 0,
    );
  }

  /**
   * Weighted composite score (0–100).
   *  - CII average:          40% weight
   *  - Convergence alerts:   20% weight (each alert adds 15, capped at 100)
   *  - Theater posture:      25% weight (each elevated theater adds 20, capped at 100)
   *  - Cascade alerts:       15% weight (each alert adds 20, capped at 100)
   */
  private computeComposite(
    ciiAvg: number,
    convergence: number,
    posture: number,
    cascade: number,
  ): number {
    const ciiComponent = ciiAvg;
    const convComponent = Math.min(100, convergence * 15);
    const postComponent = Math.min(100, posture * 20);
    const cascComponent = Math.min(100, cascade * 20);

    return Math.round(
      ciiComponent * 0.4 +
      convComponent * 0.2 +
      postComponent * 0.25 +
      cascComponent * 0.15,
    );
  }

  private compositeToSeverity(score: number): SeverityLevel {
    if (score >= 80) return 'critical';
    if (score >= 60) return 'high';
    if (score >= 40) return 'elevated';
    if (score >= 20) return 'guarded';
    return 'low';
  }

  // ── Render ────────────────────────────────────────────────────────────────

  protected override render(): void {
    // Learning banner
    const isLearning = ciiEngine.isLearning;
    this.bannerEl.style.display = isLearning ? 'block' : 'none';

    if (isLearning) {
      const elapsed = ciiEngine.uptime;
      const remaining = Math.max(0, Math.ceil((LEARNING_PERIOD_MS - elapsed) / 60_000));
      this.bannerEl.textContent = `⏳ LEARNING MODE — ${remaining}m remaining, scores are tentative`;
    }

    // Overall severity
    this.renderOverall();

    // Metric cards
    this.renderMetrics();

    // Freshness badges
    this.renderFreshness();

    // Footer
    if (this.riskScores) {
      this.setFooter(`Updated ${timeAgo(this.riskScores.timestamp)}`);
    }
  }

  private renderOverall(): void {
    const severity = this.riskScores?.overall ?? 'low';
    const color = SEVERITY_COLORS[severity];
    const label = SEVERITY_LABELS[severity];
    const composite = this.riskScores
      ? this.computeComposite(
          this.riskScores.ciiAvg,
          this.riskScores.convergenceAlerts,
          this.riskScores.postureAlerts,
          this.riskScores.cascadeAlerts,
        )
      : 0;

    const badge = h('div', {
      style: `display:inline-flex;align-items:center;justify-content:center;`
        + `width:64px;height:64px;border-radius:50%;`
        + `border:3px solid ${color};font-size:20px;font-weight:700;`
        + `color:${color};font-family:var(--font-mono, monospace)`,
    }, String(composite));

    const labelEl = h('div', {
      style: `margin-top:6px;font-size:14px;font-weight:700;`
        + `letter-spacing:2px;color:${color}`,
    }, label);

    const sublabel = h('div', {
      style: 'margin-top:2px;font-size:10px;opacity:0.6',
    }, 'COMPOSITE THREAT LEVEL');

    replaceChildren(this.overallEl, badge, labelEl, sublabel);
  }

  private renderMetrics(): void {
    const scores = this.riskScores;
    const cards = [
      {
        label: 'CII AVG',
        value: scores ? String(scores.ciiAvg) : '—',
        icon: '📊',
        color: scores ? SEVERITY_COLORS[ciiEngine.getSeverity(scores.ciiAvg)] : '#555',
      },
      {
        label: 'CONVERGENCE',
        value: scores ? String(scores.convergenceAlerts) : '—',
        icon: '🔀',
        color: scores && scores.convergenceAlerts > 0
          ? SEVERITY_COLORS['elevated'] : '#555',
      },
      {
        label: 'THEATERS',
        value: scores ? `${scores.postureAlerts} HIGH+` : '—',
        icon: '🎯',
        color: scores && scores.postureAlerts > 0
          ? SEVERITY_COLORS['high'] : '#555',
      },
      {
        label: 'CASCADE',
        value: scores ? String(scores.cascadeAlerts) : '—',
        icon: '🔗',
        color: scores && scores.cascadeAlerts > 0
          ? SEVERITY_COLORS['high'] : '#555',
      },
    ];

    const cardEls = cards.map(card =>
      h('div', {
        class: 'risk-metric-card',
        style: `background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);`
          + `border-left:3px solid ${card.color};border-radius:4px;padding:8px 10px`,
      },
        h('div', {
          style: 'font-size:10px;opacity:0.5;margin-bottom:4px;letter-spacing:1px',
        }, card.label),
        h('div', {
          style: `font-size:20px;font-weight:700;color:${card.color};`
            + 'font-family:var(--font-mono, monospace)',
        }, `${card.icon} ${card.value}`),
      ),
    );

    replaceChildren(this.metricsEl, ...cardEls);
  }

  private renderFreshness(): void {
    const statuses = dataBridge.getStatus();

    const badges = TRACKED_SOURCES.map(sourceName => {
      const ds = statuses.find(s => s.source === sourceName);
      const status: DataStatus['status'] = ds ? ds.status : 'unavailable';
      const lastUpdated = ds ? ds.lastUpdated : 0;
      const color = STATUS_COLORS[status];
      const icon = STATUS_ICONS[status];
      const label = sourceName.toUpperCase();
      const age = lastUpdated > 0 ? timeAgo(lastUpdated) : 'n/a';

      return h('div', {
        class: `freshness-badge freshness-${status}`,
        style: `display:inline-flex;align-items:center;gap:4px;`
          + `padding:3px 8px;border-radius:3px;font-size:9px;`
          + `border:1px solid ${color}40;background:${color}10;`
          + `color:${color};letter-spacing:0.5px`,
        title: `${label}: ${status} — ${age}`,
      },
        h('span', null, icon),
        h('span', null, label),
      );
    });

    replaceChildren(this.freshnessEl, ...badges);
  }

  // ── Auto-refresh ──────────────────────────────────────────────────────────

  private startAutoRefresh(): void {
    this.refreshTimer = setInterval(() => {
      this.recalculate();
      this.render();
    }, REFRESH_INTERVAL);
  }

  protected override onOpen(): void {
    this.recalculate();
    this.render();
  }

  override destroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    super.destroy();
  }
}
