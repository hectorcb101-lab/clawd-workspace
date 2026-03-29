// ============================================================================
// Atlas Intel — Country Instability Index (CII) Scoring Engine
// ============================================================================

import type { CountryScore, NewsItem, Trend, SeverityLevel } from '@/types/index';
import { MONITORED_COUNTRIES } from '@/config/countries';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CIIState {
  scores: Map<string, CountryScore>;
  history: Map<string, number[]>; // last 24h scores per country
  startTime: number;
  isLearning: boolean;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Weighted components that make up the composite CII score. */
const WEIGHTS = { unrest: 0.4, security: 0.3, information: 0.3 };

/** 15-minute learning period after cold-start — scores are tentative. */
const LEARNING_PERIOD = 15 * 60 * 1000;

/** Max history entries per country (one per update cycle ≈ 24h at 2-min ticks). */
const MAX_HISTORY = 720;

/** Trend threshold — score must shift ±5 to register as rising/falling. */
const TREND_THRESHOLD = 5;

// ---------------------------------------------------------------------------
// Keyword Sets for Component Scoring
// ---------------------------------------------------------------------------

const UNREST_KEYWORDS = [
  'protest', 'riot', 'unrest', 'demonstration', 'civil disorder',
  'uprising', 'strike', 'clashes', 'tear gas', 'crackdown',
  'opposition', 'dissent', 'rally', 'march', 'mob',
  'looting', 'barricade', 'coup', 'revolution', 'insurrection',
  'martial law', 'curfew', 'state of emergency',
];

const SECURITY_KEYWORDS = [
  'military', 'airstrike', 'bombing', 'conflict', 'war',
  'troops', 'soldiers', 'missile', 'drone strike', 'artillery',
  'offensive', 'invasion', 'occupation', 'shelling', 'ceasefire',
  'escalation', 'deployment', 'incursion', 'combat', 'casualt',
  'killed', 'wounded', 'attack', 'explosion', 'terrorism',
  'militant', 'insurgent', 'guerrilla', 'ambush', 'IED',
  'defense', 'defence', 'naval', 'air force', 'army',
];

const INFORMATION_KEYWORDS = [
  'propaganda', 'disinformation', 'misinformation', 'fake news',
  'information warfare', 'psyop', 'influence operation',
  'troll farm', 'bot network', 'state media', 'censorship',
  'internet shutdown', 'blackout', 'media crackdown',
  'narrative', 'hybrid warfare', 'cyber attack', 'hack',
  'breach', 'espionage', 'intelligence', 'surveillance',
];

// ---------------------------------------------------------------------------
// CII Engine
// ---------------------------------------------------------------------------

class CIIEngine {
  private state: CIIState;

  constructor() {
    this.state = {
      scores: new Map(),
      history: new Map(),
      startTime: Date.now(),
      isLearning: true,
    };
    this.initializeCountries();
  }

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  /** Seed every monitored country with its baseline (floor) score. */
  private initializeCountries(): void {
    for (const country of MONITORED_COUNTRIES) {
      const initial: CountryScore = {
        code: country.code,
        name: country.name,
        flag: country.flag,
        score: country.floorScore,
        unrest: 0,
        security: 0,
        information: 0,
        trend: 'stable',
        trendDelta: 0,
        headlines: [],
        isConflictZone: country.isConflictZone,
        floorScore: country.floorScore,
      };
      this.state.scores.set(country.code, initial);
      this.state.history.set(country.code, [country.floorScore]);
    }
  }

  // -------------------------------------------------------------------------
  // Main Update Cycle
  // -------------------------------------------------------------------------

  /**
   * Ingest new data and recalculate every country's CII score.
   *
   * @param news       Latest news items (should already be deduped)
   * @param unrestData Optional supplementary protest / civil-disorder feed
   * @param militaryData Optional supplementary military-event feed
   */
  update(
    news: NewsItem[],
    unrestData?: unknown[],
    militaryData?: unknown[],
  ): void {
    // Check learning-mode expiry
    if (this.state.isLearning && Date.now() - this.state.startTime > LEARNING_PERIOD) {
      this.state.isLearning = false;
    }

    // Build per-country news buckets
    const buckets = this.bucketByCountry(news);

    for (const country of MONITORED_COUNTRIES) {
      const code = country.code;
      const countryNews = buckets.get(code) ?? [];

      // --- Component scores (0-100 each) ---
      const unrest = this.calcUnrest(code, countryNews, unrestData);
      const security = this.calcSecurity(code, countryNews, militaryData);
      const information = this.calcInformation(code, countryNews);

      // --- Weighted composite ---
      let raw =
        unrest * WEIGHTS.unrest +
        security * WEIGHTS.security +
        information * WEIGHTS.information;

      // --- Contextual boosts ---
      raw += this.contextualBoost(code, countryNews);

      // --- Apply conflict-zone floor ---
      raw = Math.max(raw, country.floorScore);

      // --- Clamp 0-100 ---
      const score = Math.round(Math.min(100, Math.max(0, raw)));

      // --- Trend ---
      const { trend, delta } = this.calcTrend(code, score);

      // --- Top headlines (most recent 3) ---
      const headlines = countryNews
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, 3);

      // --- Store ---
      const entry: CountryScore = {
        code,
        name: country.name,
        flag: country.flag,
        score,
        unrest: Math.round(unrest),
        security: Math.round(security),
        information: Math.round(information),
        trend,
        trendDelta: delta,
        headlines,
        isConflictZone: country.isConflictZone,
        floorScore: country.floorScore,
      };
      this.state.scores.set(code, entry);

      // --- History ---
      const hist = this.state.history.get(code) ?? [];
      hist.push(score);
      if (hist.length > MAX_HISTORY) hist.shift();
      this.state.history.set(code, hist);
    }
  }

  // -------------------------------------------------------------------------
  // Component Calculators
  // -------------------------------------------------------------------------

  /** Calculate unrest component (0-100). */
  private calcUnrest(
    _code: string,
    news: NewsItem[],
    unrestData?: unknown[],
  ): number {
    // Count keyword matches across all news for this country
    let count = 0;
    for (const item of news) {
      const text = `${item.title} ${item.summary ?? ''}`.toLowerCase();
      for (const kw of UNREST_KEYWORDS) {
        if (text.includes(kw)) {
          count++;
          break; // one match per item is enough
        }
      }
      // Boost for items explicitly tagged as unrest
      if (item.threatCategory === 'unrest') count += 1;
    }

    // Supplementary unrest data (ACLED, etc.) adds to count
    if (unrestData) count += unrestData.length;

    // Log scale: 20 events ≈ 100 score
    return this.logScale(count, 20);
  }

  /** Calculate security component (0-100). */
  private calcSecurity(
    _code: string,
    news: NewsItem[],
    militaryData?: unknown[],
  ): number {
    let count = 0;
    for (const item of news) {
      const text = `${item.title} ${item.summary ?? ''}`.toLowerCase();
      for (const kw of SECURITY_KEYWORDS) {
        if (text.includes(kw)) {
          count++;
          break;
        }
      }
      // Boost for threat categories that map to security
      if (
        item.threatCategory === 'military' ||
        item.threatCategory === 'conflict' ||
        item.threatCategory === 'terrorism'
      ) {
        count += 1;
      }
      // High threat-score items contribute more
      if (item.threatScore && item.threatScore >= 70) count += 1;
    }

    if (militaryData) count += militaryData.length;

    // Log scale: 15 events ≈ 100 score
    return this.logScale(count, 15);
  }

  /** Calculate information component (0-100). */
  private calcInformation(_code: string, news: NewsItem[]): number {
    let count = 0;

    // Keyword matches
    for (const item of news) {
      const text = `${item.title} ${item.summary ?? ''}`.toLowerCase();
      for (const kw of INFORMATION_KEYWORDS) {
        if (text.includes(kw)) {
          count++;
          break;
        }
      }
      // Propaganda risk flag from the news pipeline
      if (item.propagandaRisk) count += 2;

      // Cyber-tagged items
      if (item.threatCategory === 'cyber') count += 1;
    }

    // News velocity component: high volume of any news ≈ information saturation
    // velocity measures articles-per-hour for this country
    const velocityScore = this.velocityComponent(news);

    // Combine keyword hits (log-scaled out of 12) with velocity (weighted lower)
    const keywordPart = this.logScale(count, 12);
    return Math.min(100, keywordPart * 0.7 + velocityScore * 0.3);
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  /**
   * Logarithmic scaling to prevent media-bias skew.
   * Converts a raw event count to a 0-100 score.
   */
  private logScale(count: number, maxExpected: number): number {
    if (count <= 0) return 0;
    return Math.min(100, (Math.log(count + 1) / Math.log(maxExpected + 1)) * 100);
  }

  /**
   * News velocity — how rapidly articles are arriving.
   * Returns 0-100 score based on articles-per-hour.
   */
  private velocityComponent(news: NewsItem[]): number {
    if (news.length === 0) return 0;

    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    const recentCount = news.filter((n) => n.timestamp >= oneHourAgo).length;

    // Use explicit velocity field if available (average across items)
    const avgVelocity =
      news.reduce((sum, n) => sum + (n.velocity ?? 0), 0) / news.length;

    // Combine: articles in last hour (log-scaled out of 30) + avg velocity signal
    const countScore = this.logScale(recentCount, 30);
    const velScore = Math.min(100, avgVelocity * 10); // velocity 10+ ≈ 100

    return countScore * 0.6 + velScore * 0.4;
  }

  /**
   * Contextual boosts applied on top of the weighted composite.
   * - Hotspot country: +10 (active conflict zone)
   * - High-urgency news: +5 (any item with threatScore ≥ 80)
   * - Focal-point surge: +8 (≥5 articles in last 2 hours)
   */
  private contextualBoost(code: string, news: NewsItem[]): number {
    let boost = 0;

    // Hotspot boost — conflict zones get a persistent bump
    const country = MONITORED_COUNTRIES.find((c) => c.code === code);
    if (country?.isConflictZone) boost += 10;

    // High-urgency news boost
    const hasUrgent = news.some((n) => n.threatScore != null && n.threatScore >= 80);
    if (hasUrgent) boost += 5;

    // Focal-point surge: lots of recent articles
    const twoHoursAgo = Date.now() - 2 * 60 * 60 * 1000;
    const recentCount = news.filter((n) => n.timestamp >= twoHoursAgo).length;
    if (recentCount >= 5) boost += 8;

    return boost;
  }

  /**
   * Bucket news items by country code.
   * Uses the `country` field, `countries` array, and title/summary alias matching.
   */
  private bucketByCountry(news: NewsItem[]): Map<string, NewsItem[]> {
    const buckets = new Map<string, NewsItem[]>();

    for (const item of news) {
      const codes = new Set<string>();

      // Direct country field
      if (item.country) {
        const upper = item.country.toUpperCase();
        if (this.state.scores.has(upper)) codes.add(upper);
      }

      // Countries array
      if (item.countries) {
        for (const c of item.countries) {
          const upper = c.toUpperCase();
          if (this.state.scores.has(upper)) codes.add(upper);
        }
      }

      // Alias matching in title + summary
      const text = `${item.title} ${item.summary ?? ''}`.toLowerCase();
      for (const country of MONITORED_COUNTRIES) {
        if (codes.has(country.code)) continue; // already matched
        // Check name
        if (text.includes(country.name.toLowerCase())) {
          codes.add(country.code);
          continue;
        }
        // Check aliases
        for (const alias of country.aliases) {
          if (text.includes(alias)) {
            codes.add(country.code);
            break;
          }
        }
      }

      // Drop into buckets
      for (const code of codes) {
        const arr = buckets.get(code) ?? [];
        arr.push(item);
        buckets.set(code, arr);
      }
    }

    return buckets;
  }

  // -------------------------------------------------------------------------
  // Trend Calculation
  // -------------------------------------------------------------------------

  /**
   * Compare current score to historical score ~24h ago.
   * Rising if delta > 5, Falling if delta < -5, else Stable.
   */
  private calcTrend(
    code: string,
    currentScore: number,
  ): { trend: Trend; delta: number } {
    const hist = this.state.history.get(code) ?? [];

    // Target: the score from ~720 ticks ago (24h at 2-min intervals).
    // Fall back to oldest available if history is shorter.
    const refIndex = Math.max(0, hist.length - MAX_HISTORY);
    const refScore = hist[refIndex] ?? currentScore;

    const delta = Math.round(currentScore - refScore);

    let trend: Trend = 'stable';
    if (delta > TREND_THRESHOLD) trend = 'rising';
    else if (delta < -TREND_THRESHOLD) trend = 'falling';

    return { trend, delta };
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Get severity level from a numeric score. */
  getSeverity(score: number): SeverityLevel {
    if (score >= 81) return 'critical';
    if (score >= 66) return 'high';
    if (score >= 46) return 'elevated';
    if (score >= 26) return 'guarded';
    return 'low';
  }

  /** Get all country scores sorted by score descending. */
  getScores(): CountryScore[] {
    return Array.from(this.state.scores.values()).sort(
      (a, b) => b.score - a.score,
    );
  }

  /** Get score for a specific country code. */
  getScore(code: string): CountryScore | undefined {
    return this.state.scores.get(code.toUpperCase());
  }

  /** Is the engine still in its cold-start learning period? */
  get isLearning(): boolean {
    if (
      this.state.isLearning &&
      Date.now() - this.state.startTime > LEARNING_PERIOD
    ) {
      this.state.isLearning = false;
    }
    return this.state.isLearning;
  }

  /** Elapsed milliseconds since engine started. */
  get uptime(): number {
    return Date.now() - this.state.startTime;
  }
}

// ---------------------------------------------------------------------------
// Singleton Export
// ---------------------------------------------------------------------------

export const ciiEngine = new CIIEngine();
