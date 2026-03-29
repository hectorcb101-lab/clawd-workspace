// ============================================================================
// Atlas Intel — Infrastructure Cascade Analysis Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, uid } from '@/utils/dom-utils';
import type { CascadeDomain, CascadeAlert, SeverityLevel } from '@/types/index';

// ---------------------------------------------------------------------------
// Domain definitions — multi-domain infrastructure model
// ---------------------------------------------------------------------------

type DomainStatus = 'normal' | 'degraded' | 'critical';

interface CascadeDomainState extends CascadeDomain {
  score: number;       // 0–100 health score (100 = fully operational)
  events: string[];    // recent events affecting this domain
}

const DOMAIN_COLORS: Record<DomainStatus, string> = {
  normal: 'var(--severity-low, #00e676)',
  degraded: 'var(--severity-elevated, #ffc107)',
  critical: 'var(--severity-critical, #ff1744)',
};

const DOMAIN_ICONS: Record<string, string> = {
  Power: '⚡',
  Comms: '📡',
  Transport: '🚛',
  Water: '💧',
  Fuel: '⛽',
  Financial: '🏦',
  Healthcare: '🏥',
};

// ---------------------------------------------------------------------------
// Initial domain graph — Power → Comms → Transport cascade chain
// ---------------------------------------------------------------------------

function buildDomainGraph(): CascadeDomainState[] {
  return [
    {
      name: 'Power',
      status: 'normal',
      dependencies: [],
      score: 95,
      events: [],
    },
    {
      name: 'Comms',
      status: 'normal',
      dependencies: ['Power'],
      score: 92,
      events: [],
    },
    {
      name: 'Transport',
      status: 'normal',
      dependencies: ['Power', 'Comms'],
      score: 88,
      events: [],
    },
    {
      name: 'Water',
      status: 'normal',
      dependencies: ['Power'],
      score: 96,
      events: [],
    },
    {
      name: 'Fuel',
      status: 'normal',
      dependencies: ['Power', 'Transport'],
      score: 90,
      events: [],
    },
    {
      name: 'Financial',
      status: 'normal',
      dependencies: ['Power', 'Comms'],
      score: 94,
      events: [],
    },
    {
      name: 'Healthcare',
      status: 'normal',
      dependencies: ['Power', 'Water', 'Transport'],
      score: 91,
      events: [],
    },
  ];
}

// ---------------------------------------------------------------------------
// CascadePanel
// ---------------------------------------------------------------------------

export class CascadePanel extends Panel {
  private domains: CascadeDomainState[] = [];
  private alerts: CascadeAlert[] = [];
  private chainEl!: HTMLElement;
  private alertListEl!: HTMLElement;
  private scoreEl!: HTMLElement;
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor() {
    super({
      id: 'cascade',
      title: 'CASCADE ANALYSIS',
      icon: '🔗',
      description: 'Multi-domain infrastructure cascade detection and analysis',
      defaultOpen: false,
    });

    this.domains = buildDomainGraph();
    this.buildUI();
    this.simulateEvents();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    // Overall cascade score
    this.scoreEl = h('div', { class: 'cascade-score-section' });

    // Domain chain visualization
    this.chainEl = h('div', { class: 'cascade-chain' });

    // Alert list
    const alertHeader = h('div', { class: 'cascade-section-header' }, 'CASCADE ALERTS');
    this.alertListEl = h('div', { class: 'cascade-alert-list' });

    replaceChildren(this.body, this.scoreEl, this.chainEl, alertHeader, this.alertListEl);
    this.render();
  }

  // ── Cascade detection engine ──────────────────────────────────────────────

  private detectCascades(): void {
    // Propagate status through dependency graph
    for (const domain of this.domains) {
      domain.status = this.scoreToStatus(domain.score);
    }

    // Check for cascade effects: if a dependency is degraded/critical,
    // downstream domains get impacted
    let changed = true;
    let iterations = 0;

    while (changed && iterations < 10) {
      changed = false;
      iterations++;

      for (const domain of this.domains) {
        for (const depName of domain.dependencies) {
          const dep = this.domains.find(d => d.name === depName);
          if (!dep) continue;

          if (dep.status === 'critical' && domain.status !== 'critical') {
            // Critical upstream = degrade downstream heavily
            domain.score = Math.min(domain.score, 35);
            domain.status = this.scoreToStatus(domain.score);
            changed = true;
          } else if (dep.status === 'degraded' && domain.status === 'normal') {
            // Degraded upstream = partial impact
            domain.score = Math.min(domain.score, 65);
            domain.status = this.scoreToStatus(domain.score);
            changed = true;
          }
        }
      }
    }

    // Generate alerts for detected cascades
    this.generateAlerts();
  }

  private generateAlerts(): void {
    const criticalDomains = this.domains.filter(d => d.status === 'critical');
    const degradedDomains = this.domains.filter(d => d.status === 'degraded');

    // Find cascade chains
    for (const crit of criticalDomains) {
      const downstreamAffected = this.domains.filter(
        d => d.dependencies.includes(crit.name) && d.status !== 'normal',
      );

      if (downstreamAffected.length > 0) {
        const chain = [crit.name, ...downstreamAffected.map(d => d.name)];
        const existingAlert = this.alerts.find(
          a => a.chain.join('→') === chain.join('→'),
        );

        if (!existingAlert) {
          const severity: SeverityLevel =
            downstreamAffected.some(d => d.status === 'critical') ? 'critical' : 'high';

          this.alerts.unshift({
            id: `cascade-${uid()}`,
            chain,
            severity,
            timestamp: Date.now(),
            description:
              `${crit.name} failure cascading to ${downstreamAffected.map(d => d.name).join(', ')}`,
          });
        }
      }
    }

    // Trim old alerts
    if (this.alerts.length > 20) this.alerts.length = 20;

    // Count for degraded-only chains
    for (const deg of degradedDomains) {
      const downstream = this.domains.filter(
        d => d.dependencies.includes(deg.name) && d.status !== 'normal',
      );
      if (downstream.length > 0) {
        const chain = [deg.name, ...downstream.map(d => d.name)];
        const existingAlert = this.alerts.find(
          a => a.chain.join('→') === chain.join('→'),
        );
        if (!existingAlert) {
          this.alerts.unshift({
            id: `cascade-${uid()}`,
            chain,
            severity: 'elevated',
            timestamp: Date.now(),
            description:
              `${deg.name} degradation impacting ${downstream.map(d => d.name).join(', ')}`,
          });
        }
      }
    }
  }

  private scoreToStatus(score: number): DomainStatus {
    if (score <= 40) return 'critical';
    if (score <= 70) return 'degraded';
    return 'normal';
  }

  private getOverallScore(): number {
    const total = this.domains.reduce((sum, d) => sum + d.score, 0);
    return Math.round(total / this.domains.length);
  }

  // ── Simulation (mock events) ──────────────────────────────────────────────

  private simulateEvents(): void {
    // Introduce some initial realistic degradation
    const power = this.domains.find(d => d.name === 'Power')!;
    power.score = 62;
    power.events.push('Regional grid instability reported — Eastern sector');

    const comms = this.domains.find(d => d.name === 'Comms')!;
    comms.events.push('Subsea cable maintenance — capacity reduced 15%');
    comms.score = 78;

    this.detectCascades();
  }

  // ── Render ────────────────────────────────────────────────────────────────

  protected render(): void {
    this.renderScore();
    this.renderDomainChain();
    this.renderAlerts();

    const alertCount = this.alerts.filter(
      a => a.severity === 'critical' || a.severity === 'high',
    ).length;
    this.setBadge(alertCount);
    this.setFooter(
      `${this.domains.length} domains · ${this.alerts.length} alerts · Updated ${new Date().toISOString().slice(11, 19)}Z`,
    );
  }

  private renderScore(): void {
    const score = this.getOverallScore();
    const status = this.scoreToStatus(score);
    const color = DOMAIN_COLORS[status];

    replaceChildren(
      this.scoreEl,
      h(
        'div',
        {
          class: 'cascade-overall',
          style: `border-left:3px solid ${color};padding:8px 12px;margin-bottom:10px;`,
        },
        h('span', { class: 'cascade-overall-label' }, 'INFRASTRUCTURE HEALTH'),
        h(
          'span',
          {
            class: 'cascade-overall-score',
            style: `color:${color};font-size:1.4rem;font-weight:bold;margin-left:12px;`,
          },
          `${score}%`,
        ),
        h(
          'span',
          {
            class: 'cascade-overall-status',
            style: `color:${color};margin-left:8px;text-transform:uppercase;font-size:0.6rem;letter-spacing:0.1em;`,
          },
          status,
        ),
      ),
    );
  }

  private renderDomainChain(): void {
    const elements: (HTMLElement | string)[] = [];

    for (let i = 0; i < this.domains.length; i++) {
      const domain = this.domains[i];
      const color = DOMAIN_COLORS[domain.status];
      const icon = DOMAIN_ICONS[domain.name] ?? '◆';

      const domainEl = h(
        'div',
        {
          class: `cascade-domain cascade-${domain.status}`,
          style: `border:1px solid ${color};padding:6px 10px;border-radius:4px;display:inline-flex;align-items:center;gap:6px;`,
          title: `${domain.name}: ${domain.score}% — ${domain.events.join('; ') || 'No incidents'}`,
        },
        h('span', { class: 'cascade-domain-icon' }, icon),
        h(
          'div',
          { class: 'cascade-domain-info' },
          h('div', { class: 'cascade-domain-name', style: `color:${color};font-weight:bold;font-size:0.65rem;` }, domain.name),
          h(
            'div',
            { class: 'cascade-domain-score', style: 'font-size:0.55rem;opacity:0.7;' },
            `${domain.score}% · ${domain.status.toUpperCase()}`,
          ),
        ),
      );

      elements.push(domainEl);

      // Show dependency arrows between related domains
      if (i < this.domains.length - 1) {
        const nextDomain = this.domains[i + 1];
        const hasDep = nextDomain.dependencies.includes(domain.name);
        const arrowColor = hasDep
          ? (domain.status === 'critical' ? '#ff1744' : domain.status === 'degraded' ? '#ffc107' : '#555')
          : '#333';

        elements.push(
          h(
            'span',
            {
              class: 'cascade-arrow',
              style: `color:${arrowColor};margin:0 4px;font-size:0.8rem;`,
            },
            hasDep ? '→' : '·',
          ),
        );
      }
    }

    replaceChildren(this.chainEl, ...elements);
  }

  private renderAlerts(): void {
    if (this.alerts.length === 0) {
      replaceChildren(
        this.alertListEl,
        h('div', { class: 'cascade-no-alerts' }, 'No cascade alerts. Infrastructure nominal.'),
      );
      return;
    }

    const SEVERITY_COLORS: Record<SeverityLevel, string> = {
      critical: '#ff1744',
      high: '#ff6d00',
      elevated: '#ffc107',
      guarded: '#29b6f6',
      low: '#00e676',
    };

    const alertEls = this.alerts.slice(0, 10).map(alert => {
      const color = SEVERITY_COLORS[alert.severity];

      const chainStr = alert.chain.join(' → ');
      const chainEl = h(
        'div',
        { class: 'cascade-alert-chain', style: `color:${color};font-weight:bold;font-size:0.6rem;` },
        chainStr,
      );

      const descEl = h(
        'div',
        { class: 'cascade-alert-desc', style: 'font-size:0.55rem;opacity:0.8;margin-top:2px;' },
        alert.description,
      );

      const sevBadge = h(
        'span',
        {
          class: `cascade-alert-severity`,
          style: `background:${color};color:#000;padding:1px 5px;border-radius:2px;font-size:0.5rem;font-weight:bold;text-transform:uppercase;`,
        },
        alert.severity,
      );

      return h(
        'div',
        {
          class: 'cascade-alert-item',
          style: `border-left:2px solid ${color};padding:4px 8px;margin-bottom:4px;`,
        },
        h('div', { style: 'display:flex;justify-content:space-between;align-items:center;' }, chainEl, sevBadge),
        descEl,
      );
    });

    replaceChildren(this.alertListEl, ...alertEls);
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
    // Re-evaluate cascades every 30 seconds
    this.refreshTimer = setInterval(() => {
      this.detectCascades();
      this.render();
    }, 30_000);
  }

  protected onClose(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  async refresh(): Promise<void> {
    this.detectCascades();
    this.render();
  }
}
