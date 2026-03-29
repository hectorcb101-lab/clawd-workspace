// ============================================================================
// Atlas Intel — Breaking News Alert Pipeline
// ============================================================================

import type { BreakingAlert, AlertOrigin, SeverityLevel, NewsItem } from '@/types/index';
import { uid } from '@/utils/dom-utils';

// ---------------------------------------------------------------------------
// Critical keyword sets used for alert evaluation
// ---------------------------------------------------------------------------

const BREAKING_PREFIXES = [
  'breaking',
  'breaking news',
  'urgent',
  'flash',
  'just in',
  'alert',
  'developing',
];

/** Keywords that indicate critical severity when paired with tier-1 source. */
const CRITICAL_KEYWORDS = [
  'nuclear strike', 'nuclear attack', 'nuclear detonation', 'nuclear test',
  'declaration of war', 'martial law', 'coup', 'invasion',
  'chemical attack', 'chemical weapons',
  'assassination', 'head of state killed',
  'icbm launch', 'ballistic missile launch',
  'reactor meltdown', 'dirty bomb',
];

/** Keywords that indicate high severity. */
const HIGH_KEYWORDS = [
  'airstrike', 'missile strike', 'ground offensive', 'ceasefire collapse',
  'troops deployed', 'military mobilization', 'border incursion',
  'terror attack', 'mass casualty', 'hostage', 'embassy attack',
  'cyber attack', 'infrastructure attack', 'grid down', 'blackout',
  'sanctions', 'naval blockade', 'no-fly zone',
  'earthquake', 'tsunami warning', 'pandemic declared',
  'siren', 'air raid', 'rocket attack', 'drone strike',
];

/** Keywords that indicate elevated severity. */
const ELEVATED_KEYWORDS = [
  'military exercise', 'troop buildup', 'escalation', 'tensions',
  'protest', 'riot', 'unrest', 'explosion', 'shooting',
  'summit', 'emergency meeting', 'un security council',
  'data breach', 'ransomware', 'oil spill', 'pipeline shutdown',
];

// ---------------------------------------------------------------------------
// Service
// ---------------------------------------------------------------------------

class BreakingNewsService {
  private alerts: BreakingAlert[] = [];
  private seen = new Map<string, number>(); // dedup key → timestamp
  private lastAlert = 0; // global cooldown timestamp
  private listeners: ((alert: BreakingAlert) => void)[] = [];

  // ── Public API ──────────────────────────────────────────────────────────

  /**
   * Evaluate an array of news items and emit alerts for any that qualify.
   * Enforces a 60-second global cooldown between alert batches.
   */
  check(items: NewsItem[]): BreakingAlert[] {
    const now = Date.now();

    // Global cooldown — avoid alert fatigue
    if (now - this.lastAlert < 60_000) return [];

    const newAlerts: BreakingAlert[] = [];

    for (const item of items) {
      // Skip items older than 15 minutes
      if (now - item.timestamp > 900_000) continue;

      const alert = this.evaluateItem(item);
      if (alert && !this.isDuplicate(alert)) {
        newAlerts.push(alert);
        this.seen.set(this.dedupKey(alert), now);
      }
    }

    if (newAlerts.length > 0) {
      this.lastAlert = now;
      this.alerts.push(...newAlerts);

      // Trim alert history to last 200
      if (this.alerts.length > 200) {
        this.alerts = this.alerts.slice(-200);
      }

      // Notify listeners & desktop
      for (const alert of newAlerts) {
        this.notify(alert);
        this.showBanner(alert);
        for (const fn of this.listeners) {
          try { fn(alert); } catch { /* listener error — skip */ }
        }
      }
    }

    // Prune stale dedup entries (> 30 min)
    this.pruneSeenMap(now);

    return newAlerts;
  }

  /** Subscribe to breaking alerts. Returns an unsubscribe function. */
  onAlert(fn: (alert: BreakingAlert) => void): () => void {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter(l => l !== fn);
    };
  }

  /** Return all stored alerts (newest first). */
  getAlerts(): BreakingAlert[] {
    return [...this.alerts].reverse();
  }

  /** Request browser notification permission (call on user gesture). */
  requestPermission(): void {
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  // ── Evaluation — 5 alert origins ────────────────────────────────────────

  private evaluateItem(item: NewsItem): BreakingAlert | null {
    const titleLower = item.title.toLowerCase();

    // Origin 1: "BREAKING" / "URGENT" in the headline
    const breakingMatch = this.checkBreakingPrefix(titleLower);
    if (breakingMatch) {
      return this.buildAlert(item, 'rss-critical', this.classifySeverity(titleLower, item));
    }

    // Origin 2: Tier-1 source with critical keywords
    if (item.sourceTier === 1) {
      const severity = this.classifySeverity(titleLower, item);
      if (severity === 'critical' || severity === 'high') {
        return this.buildAlert(item, 'rss-critical', severity);
      }
    }

    // Origin 3: Keyword spike — multiple critical keywords in one headline
    const criticalHits = CRITICAL_KEYWORDS.filter(kw => titleLower.includes(kw));
    if (criticalHits.length >= 1) {
      return this.buildAlert(item, 'keyword-spike', 'critical');
    }

    const highHits = HIGH_KEYWORDS.filter(kw => titleLower.includes(kw));
    if (highHits.length >= 2) {
      return this.buildAlert(item, 'keyword-spike', 'high');
    }

    // Origin 4: Hotspot escalation — item tagged with high threat score
    if (item.threatScore !== undefined && item.threatScore >= 0.85) {
      const severity: SeverityLevel = item.threatScore >= 0.95 ? 'critical' : 'high';
      return this.buildAlert(item, 'hotspot-escalation', severity);
    }

    // Origin 5: Military surge — military category items from tier 1–2
    if (
      item.threatCategory === 'military' &&
      item.sourceTier <= 2 &&
      this.hasMilitaryUrgency(titleLower)
    ) {
      return this.buildAlert(item, 'military-surge', 'high');
    }

    return null;
  }

  // ── Helpers ─────────────────────────────────────────────────────────────

  private checkBreakingPrefix(titleLower: string): boolean {
    return BREAKING_PREFIXES.some(prefix => {
      // Match at start, or after common punctuation: "🔴 BREAKING:"
      const idx = titleLower.indexOf(prefix);
      return idx >= 0 && idx <= 10;
    });
  }

  private classifySeverity(titleLower: string, item: NewsItem): SeverityLevel {
    // Check critical keywords first
    for (const kw of CRITICAL_KEYWORDS) {
      if (titleLower.includes(kw)) return 'critical';
    }

    // High keywords
    const highCount = HIGH_KEYWORDS.filter(kw => titleLower.includes(kw)).length;
    if (highCount >= 1 && item.sourceTier <= 2) return 'high';
    if (highCount >= 2) return 'high';

    // Elevated keywords
    const elevatedCount = ELEVATED_KEYWORDS.filter(kw => titleLower.includes(kw)).length;
    if (elevatedCount >= 1) return 'elevated';

    // Tier-1 breaking still gets elevated minimum
    if (item.sourceTier === 1) return 'elevated';

    return 'guarded';
  }

  private hasMilitaryUrgency(titleLower: string): boolean {
    const urgentTerms = [
      'deployed', 'mobiliz', 'launch', 'intercept', 'scrambl',
      'offensive', 'incursion', 'strike', 'shot down', 'engaged',
    ];
    return urgentTerms.some(term => titleLower.includes(term));
  }

  private buildAlert(
    item: NewsItem,
    origin: AlertOrigin,
    severity: SeverityLevel,
  ): BreakingAlert {
    return {
      id: uid(),
      title: item.title,
      source: item.source,
      origin,
      timestamp: item.timestamp,
      severity,
    };
  }

  // ── Deduplication ───────────────────────────────────────────────────────

  private dedupKey(alert: BreakingAlert): string {
    // Normalise title for dedup
    return alert.title
      .toLowerCase()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 80);
  }

  private isDuplicate(alert: BreakingAlert): boolean {
    const key = this.dedupKey(alert);
    const prev = this.seen.get(key);
    // 30-minute TTL for dedup
    return !!prev && Date.now() - prev < 1_800_000;
  }

  private pruneSeenMap(now: number): void {
    for (const [key, ts] of this.seen) {
      if (now - ts > 1_800_000) {
        this.seen.delete(key);
      }
    }
  }

  // ── Notifications ───────────────────────────────────────────────────────

  /** Show a desktop notification (if permission granted). */
  private notify(alert: BreakingAlert): void {
    if (typeof Notification === 'undefined') return;
    if (Notification.permission !== 'granted') return;

    const severityIcon: Record<SeverityLevel, string> = {
      critical: '🔴',
      high: '🟠',
      elevated: '🟡',
      guarded: '🔵',
      low: '🟢',
    };

    const icon = severityIcon[alert.severity] || '⚡';

    try {
      new Notification(`${icon} BREAKING — ${alert.severity.toUpperCase()}`, {
        body: alert.title,
        icon: '/textures/icon.png',
        tag: `atlas-breaking-${alert.id}`,
        requireInteraction: alert.severity === 'critical',
      });
    } catch {
      // Notification API may fail in some contexts — ignore
    }
  }

  /** Dispatch a custom DOM event so App.ts can show a banner overlay. */
  showBanner(alert: BreakingAlert): void {
    window.dispatchEvent(
      new CustomEvent('atlas:breaking', { detail: alert }),
    );
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const breakingNews = new BreakingNewsService();
