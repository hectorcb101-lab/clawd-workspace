// ============================================================================
// Atlas Intel — DEFCON / PizzInt Status Indicator
// ============================================================================
//
// Standalone component (not a Panel) that calculates and displays a DEFCON
// readiness level (1–5) based on a composite PizzInt-style score derived from
// CII averages, signal criticality, theater posture, and convergence alerts.
// Designed for the top bar: compact, color-coded, auto-updating every 30s.
// ============================================================================

import { h } from '@/utils/dom-utils';
import { ciiEngine } from '@/services/cii-scoring';
import { signalEngine } from '@/services/signal-engine';
import { theaterPosture } from '@/services/theater-posture';
import type { PizzIntStatus, TheaterPosture as TheaterPostureData } from '@/types/index';
import type { ConvergenceAlert } from '@/services/convergence';

// ---------------------------------------------------------------------------
// DEFCON Configuration
// ---------------------------------------------------------------------------

interface DefconLevel {
  level: number;
  label: string;
  description: string;
  color: string;
  bgColor: string;
}

const DEFCON_LEVELS: DefconLevel[] = [
  {
    level: 1,
    label: 'DEFCON 1',
    description: 'MAXIMUM READINESS',
    color: '#ff1744',
    bgColor: 'rgba(255, 23, 68, 0.2)',
  },
  {
    level: 2,
    label: 'DEFCON 2',
    description: 'ARMED FORCES READY',
    color: '#ff6d00',
    bgColor: 'rgba(255, 109, 0, 0.15)',
  },
  {
    level: 3,
    label: 'DEFCON 3',
    description: 'INCREASE READINESS',
    color: '#ffc107',
    bgColor: 'rgba(255, 193, 7, 0.12)',
  },
  {
    level: 4,
    label: 'DEFCON 4',
    description: 'ABOVE NORMAL',
    color: '#29b6f6',
    bgColor: 'rgba(41, 182, 246, 0.1)',
  },
  {
    level: 5,
    label: 'DEFCON 5',
    description: 'LOWEST READINESS',
    color: '#00e676',
    bgColor: 'rgba(0, 230, 118, 0.08)',
  },
];

/** Auto-refresh interval in ms. */
const UPDATE_INTERVAL = 30_000;

// ---------------------------------------------------------------------------
// Scoring weights for composite PizzInt score
// ---------------------------------------------------------------------------

/** CII average score: 40% of composite. */
const W_CII = 0.40;

/** Critical signals impact: 25% of composite. */
const W_SIGNALS = 0.25;

/** Theater posture (elevated theaters): 20% of composite. */
const W_THEATER = 0.20;

/** Convergence + breaking news: 15% of composite. */
const W_CONVERGENCE = 0.15;

// ---------------------------------------------------------------------------
// DefconIndicator
// ---------------------------------------------------------------------------

export class DefconIndicator {
  private el: HTMLElement;
  private levelEl: HTMLElement;
  private labelEl: HTMLElement;
  private timer: ReturnType<typeof setInterval> | null = null;

  // External data injected by the orchestrator
  private postures: TheaterPostureData[] = [];
  private convergenceAlerts: ConvergenceAlert[] = [];
  private breakingNewsCount = 0;

  private currentStatus: PizzIntStatus;

  constructor() {
    // Build DOM
    this.levelEl = h('span', {
      class: 'defcon-level',
      style: 'font-weight:900;font-size:13px;font-family:var(--font-mono, monospace)',
    });

    this.labelEl = h('span', {
      class: 'defcon-label',
      style: 'font-size:9px;letter-spacing:1px;opacity:0.8',
    });

    this.el = h('div', {
      class: 'defcon-indicator defcon-5',
      style: 'display:inline-flex;align-items:center;gap:6px;'
        + 'padding:4px 10px;border-radius:4px;cursor:default;'
        + 'border:1px solid rgba(255,255,255,0.1);'
        + 'transition:background 0.3s, border-color 0.3s',
      title: 'PizzInt Readiness Level',
    }, this.levelEl, this.labelEl);

    // Initial state
    this.currentStatus = {
      level: 5,
      label: 'DEFCON 5',
      description: 'LOWEST READINESS',
      timestamp: Date.now(),
    };

    this.calculate();
    this.renderLevel();
    this.startAutoUpdate();
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /** Get the root DOM element for mounting in the top bar. */
  get element(): HTMLElement {
    return this.el;
  }

  /** Get current PizzInt status. */
  get status(): PizzIntStatus {
    return { ...this.currentStatus };
  }

  /** Push external data that the indicator cannot fetch on its own. */
  updateData(data: {
    postures?: TheaterPostureData[];
    convergenceAlerts?: ConvergenceAlert[];
    breakingNewsCount?: number;
  }): void {
    if (data.postures !== undefined) this.postures = data.postures;
    if (data.convergenceAlerts !== undefined) this.convergenceAlerts = data.convergenceAlerts;
    if (data.breakingNewsCount !== undefined) this.breakingNewsCount = data.breakingNewsCount;

    this.calculate();
    this.renderLevel();
  }

  /** Force a recalculation and re-render. */
  refresh(): void {
    this.calculate();
    this.renderLevel();
  }

  /** Clean up timers. */
  destroy(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.el.remove();
  }

  // ── PizzInt Score Calculation ─────────────────────────────────────────────

  private calculate(): void {
    const pizzIntScore = this.computePizzIntScore();
    const defcon = this.scoreToDefcon(pizzIntScore);
    const level = DEFCON_LEVELS[defcon - 1];

    this.currentStatus = {
      level: defcon,
      label: level.label,
      description: level.description,
      timestamp: Date.now(),
    };
  }

  /**
   * Compute a 0–100 PizzInt composite score from multiple intelligence streams.
   */
  private computePizzIntScore(): number {
    // --- CII average (0–100) ---
    const scores = ciiEngine.getScores();
    const ciiAvg = scores.length > 0
      ? scores.reduce((sum, s) => sum + s.score, 0) / scores.length
      : 0;

    // --- Critical & high signals (0–100) ---
    const criticalSignals = signalEngine.getBySeverity('critical').length;
    const highSignals = signalEngine.getBySeverity('high').length;
    const signalScore = Math.min(100, criticalSignals * 25 + highSignals * 10);

    // --- Theater posture (0–100) ---
    const elevatedTheaters = theaterPosture.countElevatedTheaters(this.postures);
    const totalTheaters = 9; // 9 operational theaters
    const theaterScore = Math.min(100, (elevatedTheaters / totalTheaters) * 100 * 2);
    // Scaled ×2 so that 5/9 theaters elevated = 100

    // --- Convergence + breaking news (0–100) ---
    const convergenceCount = this.convergenceAlerts.length;
    const breakingCount = this.breakingNewsCount;
    const convergenceScore = Math.min(100, convergenceCount * 15 + breakingCount * 10);

    // --- Weighted composite ---
    const composite =
      ciiAvg * W_CII +
      signalScore * W_SIGNALS +
      theaterScore * W_THEATER +
      convergenceScore * W_CONVERGENCE;

    return Math.round(Math.min(100, Math.max(0, composite)));
  }

  /**
   * Map PizzInt score to DEFCON level.
   *  - >= 90 → DEFCON 1 (maximum readiness)
   *  - >= 75 → DEFCON 2
   *  - >= 55 → DEFCON 3
   *  - >= 35 → DEFCON 4
   *  -  < 35 → DEFCON 5 (lowest readiness)
   */
  private scoreToDefcon(score: number): number {
    if (score >= 90) return 1;
    if (score >= 75) return 2;
    if (score >= 55) return 3;
    if (score >= 35) return 4;
    return 5;
  }

  // ── Rendering ─────────────────────────────────────────────────────────────

  private renderLevel(): void {
    const level = DEFCON_LEVELS[this.currentStatus.level - 1];

    // Update text
    this.levelEl.textContent = String(this.currentStatus.level);
    this.levelEl.style.color = level.color;

    this.labelEl.textContent = level.label;
    this.labelEl.style.color = level.color;

    // Update container styles
    this.el.style.background = level.bgColor;
    this.el.style.borderColor = `${level.color}60`;
    this.el.title = `${level.label} — ${level.description}`;

    // Swap CSS class for external styling hooks
    for (let i = 1; i <= 5; i++) {
      this.el.classList.remove(`defcon-${i}`);
    }
    this.el.classList.add(`defcon-${this.currentStatus.level}`);

    // Pulse animation for DEFCON 1 or 2
    if (this.currentStatus.level <= 2) {
      this.el.style.animation = 'defcon-pulse 1.5s ease-in-out infinite';
    } else {
      this.el.style.animation = 'none';
    }
  }

  // ── Auto-update ───────────────────────────────────────────────────────────

  private startAutoUpdate(): void {
    this.timer = setInterval(() => {
      this.calculate();
      this.renderLevel();
    }, UPDATE_INTERVAL);
  }
}
