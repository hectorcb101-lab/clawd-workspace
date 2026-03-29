// ============================================================================
// Atlas Intel — Strategic Theater Posture Assessment
// ============================================================================
//
// Monitors 9 operational theaters worldwide, counting military assets in each
// theater's radius and correlating with news severity to produce a real-time
// posture level (CRIT / HIGH / ELEVATED / NORMAL) with trend tracking.
// ============================================================================

import type {
  TheaterPosture,
  PostureLevel,
  Trend,
  NewsItem,
  Coordinates,
} from '@/types/index';

// ---------------------------------------------------------------------------
// Theater Definitions
// ---------------------------------------------------------------------------

interface TheaterDef {
  id: string;
  name: string;
  center: Coordinates;
  radius: number; // degrees
}

const THEATERS: TheaterDef[] = [
  { id: 'taiwan-strait',     name: 'Taiwan Strait',          center: { lat: 23.5, lng: 119 },  radius: 3 },
  { id: 'persian-gulf',      name: 'Persian Gulf',           center: { lat: 26,   lng: 52 },   radius: 4 },
  { id: 'baltic-sea',        name: 'Baltic Sea',             center: { lat: 57,   lng: 20 },   radius: 4 },
  { id: 'black-sea',         name: 'Black Sea',              center: { lat: 43,   lng: 34 },   radius: 3 },
  { id: 'korean-peninsula',  name: 'Korean Peninsula',       center: { lat: 37,   lng: 127 },  radius: 3 },
  { id: 'south-china-sea',   name: 'South China Sea',        center: { lat: 14,   lng: 114 },  radius: 5 },
  { id: 'east-med',          name: 'Eastern Mediterranean',  center: { lat: 34,   lng: 33 },   radius: 3 },
  { id: 'horn-of-africa',    name: 'Horn of Africa',         center: { lat: 10,   lng: 48 },   radius: 5 },
  { id: 'arctic',            name: 'Arctic',                 center: { lat: 75,   lng: 40 },   radius: 10 },
];

// ---------------------------------------------------------------------------
// Trend history window
// ---------------------------------------------------------------------------

/** How far back (ms) to look for trend comparison. */
const TREND_WINDOW = 60 * 60 * 1000; // 1 hour

/** Max snapshots retained per theater. */
const MAX_HISTORY = 60;

// ---------------------------------------------------------------------------
// TheaterPostureEngine
// ---------------------------------------------------------------------------

export class TheaterPostureEngine {
  /** Historical posture snapshots keyed by theater id. */
  private history: Map<string, Array<{ level: PostureLevel; timestamp: number }>> = new Map();

  constructor() {
    // Initialise history buckets
    for (const t of THEATERS) {
      this.history.set(t.id, []);
    }
  }

  // -------------------------------------------------------------------------
  // Main Assessment
  // -------------------------------------------------------------------------

  /**
   * Assess posture for all 9 theaters.
   *
   * @param militaryFlights  Array of flight objects with at least { lat, lng }
   * @param vessels          Array of vessel objects with at least { lat, lng }
   * @param news             Recent news items (used for severity escalation)
   */
  assess(
    militaryFlights: Array<{ lat: number; lng: number; [k: string]: unknown }>,
    vessels: Array<{ lat: number; lng: number; [k: string]: unknown }>,
    news: NewsItem[],
  ): TheaterPosture[] {
    const now = Date.now();
    const results: TheaterPosture[] = [];

    for (const theater of THEATERS) {
      // --- Count military assets within the theater radius ---
      const flightsInRange = this.countInRadius(militaryFlights, theater);
      const vesselsInRange = this.countInRadius(vessels, theater);
      const totalAssets = flightsInRange + vesselsInRange;

      // --- Collect recent news events that geo-match the theater ---
      const theaterNews = this.matchNews(news, theater);
      const hasHighNews = theaterNews.some(
        (n) => n.threatScore != null && n.threatScore >= 70,
      );
      const hasCriticalNews = theaterNews.some(
        (n) => n.threatScore != null && n.threatScore >= 85,
      );

      // --- Recent event titles (top 5) ---
      const recentEvents = theaterNews
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, 5)
        .map((n) => n.title);

      // --- Determine posture level ---
      const posture = this.determinePosture(
        totalAssets,
        hasCriticalNews,
        hasHighNews,
      );

      // --- Track trend ---
      const trend = this.updateTrend(theater.id, posture, now);

      results.push({
        id: theater.id,
        name: theater.name,
        region: theater.center,
        posture,
        militaryFlights: flightsInRange,
        navalVessels: vesselsInRange,
        recentEvents,
        trend,
        lastUpdated: now,
      });
    }

    return results;
  }

  // -------------------------------------------------------------------------
  // Posture Determination
  // -------------------------------------------------------------------------

  /**
   * Determine posture level from asset count + news severity.
   *
   * - >=10 assets + critical news → CRIT
   * - >=5 assets + high news → HIGH
   * - >=2 assets → ELEVATED
   * - else → NORMAL
   */
  private determinePosture(
    assets: number,
    hasCriticalNews: boolean,
    hasHighNews: boolean,
  ): PostureLevel {
    if (assets >= 10 && hasCriticalNews) return 'CRIT';
    if (assets >= 5 && hasHighNews) return 'HIGH';
    if (assets >= 2) return 'ELEVATED';
    return 'NORMAL';
  }

  // -------------------------------------------------------------------------
  // Trend Tracking
  // -------------------------------------------------------------------------

  /**
   * Compare current posture to the posture ~1h ago to derive a trend.
   * Records the current posture in the history buffer.
   */
  private updateTrend(
    theaterId: string,
    currentPosture: PostureLevel,
    now: number,
  ): Trend {
    const hist = this.history.get(theaterId) ?? [];

    // Determine reference posture from ~1h ago
    const cutoff = now - TREND_WINDOW;
    const refEntry = hist.find((h) => h.timestamp <= cutoff);
    const refPosture = refEntry?.level ?? currentPosture;

    // Push current snapshot
    hist.push({ level: currentPosture, timestamp: now });

    // Trim history
    while (hist.length > MAX_HISTORY) hist.shift();
    this.history.set(theaterId, hist);

    // Compare numeric rank
    const currentRank = this.postureRank(currentPosture);
    const refRank = this.postureRank(refPosture);

    if (currentRank > refRank) return 'rising';
    if (currentRank < refRank) return 'falling';
    return 'stable';
  }

  /** Numeric rank for posture levels (higher = more severe). */
  private postureRank(level: PostureLevel): number {
    switch (level) {
      case 'CRIT':     return 4;
      case 'HIGH':     return 3;
      case 'ELEVATED': return 2;
      case 'NORMAL':   return 1;
    }
  }

  // -------------------------------------------------------------------------
  // Geo Matching
  // -------------------------------------------------------------------------

  /**
   * Count items that fall within a theater's radius (simple Euclidean
   * distance in degree space — sufficient for strategic-level detection).
   */
  private countInRadius(
    items: Array<{ lat: number; lng: number }>,
    theater: TheaterDef,
  ): number {
    let count = 0;
    for (const item of items) {
      const dLat = item.lat - theater.center.lat;
      const dLng = item.lng - theater.center.lng;
      const dist = Math.sqrt(dLat * dLat + dLng * dLng);
      if (dist <= theater.radius) count++;
    }
    return count;
  }

  /**
   * Match news items to a theater by their geo coordinates OR by
   * checking if the theater name appears in the headline.
   */
  private matchNews(news: NewsItem[], theater: TheaterDef): NewsItem[] {
    const matched: NewsItem[] = [];
    const nameLower = theater.name.toLowerCase();

    for (const item of news) {
      // Geo match
      if (item.lat != null && item.lng != null) {
        const dLat = item.lat - theater.center.lat;
        const dLng = item.lng - theater.center.lng;
        const dist = Math.sqrt(dLat * dLat + dLng * dLng);
        if (dist <= theater.radius) {
          matched.push(item);
          continue;
        }
      }

      // Title/summary keyword match
      const text = `${item.title} ${item.summary ?? ''}`.toLowerCase();
      if (text.includes(nameLower)) {
        matched.push(item);
      }
    }

    return matched;
  }

  // -------------------------------------------------------------------------
  // Public Helpers
  // -------------------------------------------------------------------------

  /** Get theater definitions (read-only). */
  getTheaters(): readonly TheaterDef[] {
    return THEATERS;
  }

  /** Get a specific theater by ID. */
  getTheater(id: string): TheaterDef | undefined {
    return THEATERS.find((t) => t.id === id);
  }

  /** Count theaters at HIGH or above from a posture array. */
  countElevatedTheaters(postures: TheaterPosture[]): number {
    return postures.filter(
      (p) => p.posture === 'CRIT' || p.posture === 'HIGH',
    ).length;
  }
}

// ---------------------------------------------------------------------------
// Singleton Export
// ---------------------------------------------------------------------------

export const theaterPosture = new TheaterPostureEngine();
