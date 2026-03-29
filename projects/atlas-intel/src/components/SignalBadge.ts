// ============================================================================
// Atlas Intel — Signal Badge Component
// Displays signal count in the top bar; opens detail modal on click
// ============================================================================

import { h, timeAgo } from '@/utils/dom-utils';
import { signalEngine } from '@/services/signal-engine';
import type { Signal, SeverityLevel } from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SEVERITY_ORDER: SeverityLevel[] = ['critical', 'high', 'elevated', 'guarded', 'low'];

const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  critical: 'var(--severity-critical)',
  high: 'var(--severity-high)',
  elevated: 'var(--severity-elevated)',
  guarded: 'var(--severity-guarded)',
  low: 'var(--severity-low)',
};

const SEVERITY_LABELS: Record<SeverityLevel, string> = {
  critical: 'CRITICAL',
  high: 'HIGH',
  elevated: 'ELEVATED',
  guarded: 'GUARDED',
  low: 'LOW',
};

const TYPE_ICONS: Record<string, string> = {
  'convergence': '⊕',
  'triangulation': '△',
  'velocity-spike': '⚡',
  'prediction-leading': '🎯',
  'news-leads-markets': '📰',
  'market-move-explained': '💹',
  'silent-divergence': '🔇',
  'sector-cascade': '🔗',
  'flow-drop': '📉',
  'flow-price-divergence': '⇅',
  'geographic-convergence': '🌐',
  'military-surge': '✈',
};

const TYPE_LABELS: Record<string, string> = {
  'convergence': 'CONVERGENCE',
  'triangulation': 'TRIANGULATION',
  'velocity-spike': 'VELOCITY SPIKE',
  'prediction-leading': 'PREDICTION LEADING',
  'news-leads-markets': 'NEWS → MARKETS',
  'market-move-explained': 'MARKET EXPLAINED',
  'silent-divergence': 'SILENT DIVERGENCE',
  'sector-cascade': 'SECTOR CASCADE',
  'flow-drop': 'FLOW DROP',
  'flow-price-divergence': 'FLOW DIVERGENCE',
  'geographic-convergence': 'GEO CONVERGENCE',
  'military-surge': 'MILITARY SURGE',
};

// ---------------------------------------------------------------------------
// Signal Badge
// ---------------------------------------------------------------------------

export class SignalBadge {
  private el: HTMLElement;
  private countEl: HTMLElement;
  private modal: HTMLElement | null = null;
  private escHandler: ((e: KeyboardEvent) => void) | null = null;
  private pulseTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    // Count indicator
    this.countEl = h('span', {
      class: 'signal-badge-count',
      style:
        'display:none;position:absolute;top:-4px;right:-4px;' +
        'min-width:16px;height:16px;padding:0 4px;' +
        'background:var(--severity-critical);color:#000;' +
        'font-size:0.55rem;font-weight:700;line-height:16px;' +
        'text-align:center;border-radius:8px;letter-spacing:0;',
    });

    // Main badge button
    this.el = h(
      'button',
      {
        class: 'signal-badge',
        title: 'Signal Intelligence — click to view active signals',
        style:
          'position:relative;display:inline-flex;align-items:center;gap:5px;' +
          'background:transparent;border:1px solid var(--border-strong);' +
          'border-radius:3px;padding:4px 8px;cursor:pointer;' +
          'color:var(--text-secondary);font-family:inherit;font-size:0.6rem;' +
          'letter-spacing:0.08em;transition:all 0.2s;',
        onClick: () => this.openModal(),
      },
      h('span', { style: 'font-size:0.7rem;' }, '◉'),
      h('span', null, 'SIGNALS'),
      this.countEl,
    );

    // Hover effects via events (no external CSS dependency)
    this.el.addEventListener('mouseenter', () => {
      this.el.style.borderColor = 'var(--amber)';
      this.el.style.color = 'var(--amber)';
    });
    this.el.addEventListener('mouseleave', () => {
      this.el.style.borderColor = 'var(--border-strong)';
      this.el.style.color = 'var(--text-secondary)';
    });
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  get element(): HTMLElement {
    return this.el;
  }

  /** Refresh the badge count from the signal engine. */
  update(): void {
    const count = signalEngine.getSignalCount();
    this.countEl.textContent = count > 0 ? String(count) : '';
    this.countEl.style.display = count > 0 ? 'inline-flex' : 'none';

    // Pulse badge for critical signals
    const hasCritical = signalEngine.getBySeverity('critical').length > 0;
    if (hasCritical && !this.pulseTimer) {
      this.el.style.borderColor = 'var(--severity-critical)';
      this.el.style.color = 'var(--severity-critical)';
      this.pulseTimer = setInterval(() => {
        const current = this.el.style.opacity;
        this.el.style.opacity = current === '0.5' ? '1' : '0.5';
      }, 600);
    } else if (!hasCritical && this.pulseTimer) {
      clearInterval(this.pulseTimer);
      this.pulseTimer = null;
      this.el.style.opacity = '1';
      this.el.style.borderColor = 'var(--border-strong)';
      this.el.style.color = 'var(--text-secondary)';
    }

    // Also refresh the open modal if it exists
    if (this.modal) this.refreshModalContent();
  }

  destroy(): void {
    this.closeModal();
    if (this.pulseTimer) {
      clearInterval(this.pulseTimer);
      this.pulseTimer = null;
    }
    this.el.remove();
  }

  // -------------------------------------------------------------------------
  // Modal
  // -------------------------------------------------------------------------

  private openModal(): void {
    if (this.modal) {
      this.closeModal();
      return;
    }

    // Escape key handler
    this.escHandler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') this.closeModal();
    };
    document.addEventListener('keydown', this.escHandler);

    // Backdrop
    const backdrop = h('div', {
      class: 'signal-modal-backdrop',
      style:
        'position:fixed;inset:0;background:rgba(0,0,0,0.7);' +
        'backdrop-filter:blur(4px);z-index:9998;',
      onClick: () => this.closeModal(),
    });

    // Modal container
    const modalContent = h('div', {
      class: 'signal-modal-body',
      style: 'flex:1;overflow-y:auto;padding:16px;',
    });

    // Header
    const header = h(
      'div',
      {
        style:
          'display:flex;justify-content:space-between;align-items:center;' +
          'padding:12px 16px;border-bottom:1px solid rgba(0,255,204,0.15);',
      },
      h(
        'div',
        { style: 'display:flex;align-items:center;gap:8px;' },
        h('span', { style: 'font-size:1rem;' }, '◉'),
        h('span', {
          style:
            'font-size:0.75rem;font-weight:600;letter-spacing:0.12em;' +
            'color:var(--text-primary);',
        }, 'SIGNAL INTELLIGENCE'),
        h('span', {
          style:
            'font-size:0.6rem;color:var(--text-dim);letter-spacing:0.06em;',
        }, `${signalEngine.getSignalCount()} ACTIVE`),
      ),
      h('button', {
        style:
          'background:transparent;border:none;color:var(--text-secondary);' +
          'font-size:1.1rem;cursor:pointer;padding:4px 8px;' +
          'border-radius:3px;transition:color 0.2s;',
        title: 'Close',
        onClick: (e: Event) => {
          e.stopPropagation();
          this.closeModal();
        },
      }, '✕'),
    );

    // Summary bar
    const summaryBar = this.buildSummaryBar();

    // Assemble modal
    const modal = h(
      'div',
      {
        class: 'signal-modal',
        style:
          'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
          'width:min(680px,90vw);max-height:80vh;' +
          'background:var(--bg-secondary);border:1px solid var(--border-strong);' +
          'border-radius:6px;display:flex;flex-direction:column;' +
          'box-shadow:0 24px 80px rgba(0,0,0,0.6);z-index:9999;' +
          'font-family:inherit;',
        onClick: (e: Event) => e.stopPropagation(),
      },
      header,
      summaryBar,
      modalContent,
    );

    this.modal = modal;
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);

    // Populate signal rows
    this.refreshModalContent();
  }

  private closeModal(): void {
    if (this.escHandler) {
      document.removeEventListener('keydown', this.escHandler);
      this.escHandler = null;
    }

    // Remove backdrop
    const backdrop = document.querySelector('.signal-modal-backdrop');
    if (backdrop) backdrop.remove();

    // Remove modal
    if (this.modal) {
      this.modal.remove();
      this.modal = null;
    }
  }

  private refreshModalContent(): void {
    if (!this.modal) return;

    const body = this.modal.querySelector('.signal-modal-body') as HTMLElement;
    if (!body) return;

    // Clear existing content
    body.innerHTML = '';

    const signals = signalEngine.getSorted();

    if (signals.length === 0) {
      body.appendChild(
        h('div', {
          style:
            'text-align:center;padding:40px 20px;color:var(--text-dim);' +
            'font-size:0.65rem;letter-spacing:0.06em;',
        },
          h('div', { style: 'font-size:1.5rem;margin-bottom:12px;opacity:0.3;' }, '◎'),
          h('div', null, 'NO ACTIVE SIGNALS'),
          h('div', {
            style: 'margin-top:8px;font-size:0.55rem;color:var(--text-dim);',
          }, 'Signals will appear when cross-stream patterns are detected.'),
        ),
      );
      return;
    }

    // Group signals by severity
    for (const severity of SEVERITY_ORDER) {
      const group = signals.filter(s => s.severity === severity);
      if (group.length === 0) continue;

      // Section header
      const sectionHeader = h(
        'div',
        {
          style:
            'display:flex;align-items:center;gap:6px;padding:8px 0 4px;' +
            'margin-top:8px;border-bottom:1px solid rgba(255,255,255,0.06);',
        },
        h('span', {
          style:
            `width:8px;height:8px;border-radius:50%;background:${SEVERITY_COLORS[severity]};` +
            'display:inline-block;flex-shrink:0;',
        }),
        h('span', {
          style:
            `font-size:0.55rem;font-weight:600;letter-spacing:0.1em;` +
            `color:${SEVERITY_COLORS[severity]};`,
        }, `${SEVERITY_LABELS[severity]} (${group.length})`),
      );
      body.appendChild(sectionHeader);

      // Signal rows
      for (const signal of group) {
        body.appendChild(this.buildSignalRow(signal));
      }
    }

    // Update the active count in header
    const countEl = this.modal.querySelector(
      '.signal-modal div:first-child span:last-child',
    );
    if (countEl) {
      countEl.textContent = `${signals.length} ACTIVE`;
    }
  }

  // -------------------------------------------------------------------------
  // Summary Bar
  // -------------------------------------------------------------------------

  private buildSummaryBar(): HTMLElement {
    const signals = signalEngine.getSignals();

    const countBySeverity = (sev: SeverityLevel) =>
      signals.filter(s => s.severity === sev).length;

    const pills: HTMLElement[] = SEVERITY_ORDER.map(sev => {
      const count = countBySeverity(sev);
      return h(
        'span',
        {
          style:
            `display:inline-flex;align-items:center;gap:3px;padding:2px 6px;` +
            `border-radius:2px;font-size:0.5rem;letter-spacing:0.06em;` +
            `background:${count > 0 ? SEVERITY_COLORS[sev] : 'var(--bg-tertiary)'};` +
            `color:${count > 0 ? '#000' : 'var(--text-dim)'};` +
            `font-weight:${count > 0 ? '700' : '400'};`,
        },
        `${SEVERITY_LABELS[sev]} ${count}`,
      );
    });

    return h(
      'div',
      {
        style:
          'display:flex;gap:6px;padding:8px 16px;' +
          'border-bottom:1px solid rgba(255,255,255,0.06);' +
          'flex-wrap:wrap;',
      },
      ...pills,
    );
  }

  // -------------------------------------------------------------------------
  // Signal Row Builder
  // -------------------------------------------------------------------------

  private buildSignalRow(signal: Signal): HTMLElement {
    const color = SEVERITY_COLORS[signal.severity];
    const typeIcon = TYPE_ICONS[signal.type] ?? '●';
    const typeLabel = TYPE_LABELS[signal.type] ?? signal.type.toUpperCase();

    // Type badge
    const typeBadge = h(
      'span',
      {
        style:
          `display:inline-flex;align-items:center;gap:3px;` +
          `padding:2px 6px;border-radius:2px;font-size:0.5rem;` +
          `letter-spacing:0.06em;font-weight:600;` +
          `background:rgba(0,255,204,0.08);color:var(--text-secondary);` +
          `border:1px solid rgba(0,255,204,0.12);`,
      },
      h('span', null, typeIcon),
      h('span', null, typeLabel),
    );

    // Severity dot
    const severityDot = h('span', {
      style:
        `width:6px;height:6px;border-radius:50%;background:${color};` +
        'display:inline-block;flex-shrink:0;',
    });

    // Title
    const titleEl = h('span', {
      style:
        'font-size:0.62rem;font-weight:500;color:var(--text-primary);' +
        'letter-spacing:0.03em;line-height:1.3;',
    }, signal.title);

    // Timestamp
    const timeEl = h('span', {
      style: 'font-size:0.5rem;color:var(--text-dim);white-space:nowrap;flex-shrink:0;',
    }, timeAgo(signal.timestamp));

    // Header row: severity dot + title + time
    const headerRow = h(
      'div',
      {
        style: 'display:flex;align-items:flex-start;gap:6px;',
      },
      severityDot,
      h('div', { style: 'flex:1;min-width:0;' },
        h('div', { style: 'display:flex;align-items:center;gap:6px;flex-wrap:wrap;' },
          titleEl,
          timeEl,
        ),
      ),
    );

    // Description
    const descEl = h('div', {
      style:
        'font-size:0.55rem;color:var(--text-secondary);line-height:1.5;' +
        'margin:4px 0 6px 12px;',
    }, signal.description);

    // Entity chips
    const entityChips: HTMLElement[] = [];
    if (signal.entities && signal.entities.length > 0) {
      for (const entity of signal.entities.slice(0, 8)) {
        entityChips.push(
          h('span', {
            style:
              'display:inline-block;padding:1px 5px;border-radius:2px;' +
              'font-size:0.48rem;letter-spacing:0.05em;' +
              'background:rgba(0,255,204,0.06);color:var(--text-secondary);' +
              'border:1px solid rgba(0,255,204,0.1);',
          }, entity),
        );
      }
    }

    // Country chips
    if (signal.countries && signal.countries.length > 0) {
      for (const country of signal.countries.slice(0, 6)) {
        entityChips.push(
          h('span', {
            style:
              'display:inline-block;padding:1px 5px;border-radius:2px;' +
              'font-size:0.48rem;letter-spacing:0.05em;' +
              'background:rgba(255,215,0,0.06);color:var(--amber);' +
              'border:1px solid rgba(255,215,0,0.12);',
          }, country),
        );
      }
    }

    // Source list
    const sourceChips: HTMLElement[] = [];
    for (const source of signal.sources.slice(0, 5)) {
      sourceChips.push(
        h('span', {
          style:
            'font-size:0.46rem;color:var(--text-dim);letter-spacing:0.04em;',
        }, source),
      );
    }

    const sourcesRow = signal.sources.length > 0
      ? h(
          'div',
          {
            style:
              'display:flex;align-items:center;gap:4px;margin-left:12px;' +
              'flex-wrap:wrap;',
          },
          h('span', {
            style: 'font-size:0.46rem;color:var(--text-dim);letter-spacing:0.06em;',
          }, 'SRC:'),
          ...sourceChips,
        )
      : null;

    // Tags row (entities + countries)
    const tagsRow = entityChips.length > 0
      ? h(
          'div',
          {
            style:
              'display:flex;align-items:center;gap:3px;margin-left:12px;' +
              'flex-wrap:wrap;',
          },
          ...entityChips,
        )
      : null;

    // TTL remaining indicator
    const elapsed = Date.now() - signal.timestamp;
    const remaining = Math.max(0, signal.ttl - elapsed);
    const remainingMin = Math.ceil(remaining / 60_000);
    const ttlEl = h('span', {
      style:
        `font-size:0.45rem;color:var(--text-dim);margin-left:12px;` +
        `letter-spacing:0.04em;opacity:0.6;`,
    }, `TTL: ${remainingMin}m`);

    // Assemble the signal row
    const row = h(
      'div',
      {
        class: 'signal-row',
        style:
          `padding:8px 0;margin:2px 0;` +
          `border-left:2px solid ${color};padding-left:10px;` +
          'transition:background 0.15s;cursor:default;',
      },
      h('div', {
        style: 'display:flex;align-items:center;gap:6px;margin-bottom:4px;',
      }, typeBadge),
      headerRow,
      descEl,
      tagsRow,
      sourcesRow,
      ttlEl,
    );

    // Hover highlight
    row.addEventListener('mouseenter', () => {
      row.style.background = 'rgba(0,255,204,0.03)';
    });
    row.addEventListener('mouseleave', () => {
      row.style.background = 'transparent';
    });

    return row;
  }
}
