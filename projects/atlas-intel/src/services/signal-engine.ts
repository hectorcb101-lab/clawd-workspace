// ============================================================================
// Atlas Intel — Signal Intelligence Engine
// Detects cross-stream correlations across news, markets, and military data
// ============================================================================

import type { Signal, SignalType, NewsItem, SeverityLevel, SourceTier } from '@/types/index';
import { findEntitiesByKeyword } from '@/config/entities';
import { uid } from '@/utils/dom-utils';

// ---------------------------------------------------------------------------
// TTLs per signal type (ms)
// ---------------------------------------------------------------------------

const SIGNAL_TTLS: Record<SignalType, number> = {
  'convergence': 3600_000,
  'triangulation': 1800_000,
  'velocity-spike': 900_000,
  'prediction-leading': 7200_000,
  'news-leads-markets': 3600_000,
  'market-move-explained': 7200_000,
  'silent-divergence': 14400_000,
  'sector-cascade': 3600_000,
  'flow-drop': 3600_000,
  'flow-price-divergence': 7200_000,
  'geographic-convergence': 3600_000,
  'military-surge': 1800_000,
};

// ---------------------------------------------------------------------------
// Source tier weighting
// ---------------------------------------------------------------------------

const TIER_WEIGHT: Record<SourceTier, number> = { 1: 1.0, 2: 0.8, 3: 0.5, 4: 0.2 };

// ---------------------------------------------------------------------------
// Detection thresholds
// ---------------------------------------------------------------------------

const VELOCITY_SPIKE_THRESHOLD = 5; // headlines/min for a single entity
const CONVERGENCE_MIN_SOURCES = 2; // independent sources reporting same entity
const TRIANGULATION_MIN_TIER12 = 3; // tier 1-2 sources on same topic
const MILITARY_SURGE_THRESHOLD = 8; // military items in a region within window
const CONVERGENCE_WINDOW = 1800_000; // 30 min window for convergence
const GEO_CONVERGENCE_RADIUS = 5; // degrees lat/lng for geographic clustering
const SECTOR_CASCADE_MIN = 3; // min items in same sector to trigger cascade

// ---------------------------------------------------------------------------
// Severity keywords for scoring
// ---------------------------------------------------------------------------

const CRITICAL_KEYWORDS = [
  'nuclear', 'icbm', 'chemical weapon', 'biological weapon', 'wmd',
  'article 5', 'declaration of war', 'martial law', 'invasion',
  'nuclear launch', 'defcon', 'strategic strike', 'mass casualty',
];

const HIGH_KEYWORDS = [
  'airstrike', 'missile strike', 'bombing', 'assassination', 'coup',
  'carrier strike group', 'mobilization', 'escalation', 'blockade',
  'cyber attack', 'infrastructure attack', 'no-fly zone', 'ultimatum',
  'troops deployed', 'emergency session', 'sanctions', 'ceasefire violated',
];

const ELEVATED_KEYWORDS = [
  'military exercise', 'naval deployment', 'troop movement', 'arms deal',
  'diplomatic crisis', 'embassy closure', 'border tension', 'protest',
  'unrest', 'drone', 'interception', 'warning', 'skirmish', 'incursion',
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Extract matched entity IDs from news title + summary text. */
function extractEntities(text: string): string[] {
  const entities = findEntitiesByKeyword(text);
  // Also search within individual words for shorter entity matches
  const words = text.split(/\s+/);
  for (const word of words) {
    if (word.length >= 3) {
      const matches = findEntitiesByKeyword(word);
      for (const m of matches) {
        if (!entities.find(e => e.id === m.id)) {
          entities.push(m);
        }
      }
    }
  }
  return [...new Set(entities.map(e => e.id))];
}

/** Score severity from text content based on keyword matches. */
function scoreSeverity(text: string): SeverityLevel {
  const lower = text.toLowerCase();

  for (const kw of CRITICAL_KEYWORDS) {
    if (lower.includes(kw)) return 'critical';
  }
  for (const kw of HIGH_KEYWORDS) {
    if (lower.includes(kw)) return 'high';
  }
  for (const kw of ELEVATED_KEYWORDS) {
    if (lower.includes(kw)) return 'elevated';
  }
  return 'guarded';
}

/** Compute weighted confidence from source tiers. */
function tierConfidence(tiers: SourceTier[]): number {
  if (tiers.length === 0) return 0;
  const sum = tiers.reduce((acc, t) => acc + TIER_WEIGHT[t], 0);
  return Math.min(1, sum / tiers.length);
}

/** Upgrade severity one level based on confidence. */
function upgradeSeverity(base: SeverityLevel, confidence: number): SeverityLevel {
  if (confidence < 0.7) return base;
  const order: SeverityLevel[] = ['low', 'guarded', 'elevated', 'high', 'critical'];
  const idx = order.indexOf(base);
  return idx < order.length - 1 ? order[idx + 1] : base;
}

/** Build a composite text blob from a news item for analysis. */
function newsText(item: NewsItem): string {
  return `${item.title} ${item.summary ?? ''}`.trim();
}

/** Group items by a key derived from each item. */
function groupBy<T>(items: T[], keyFn: (item: T) => string): Map<string, T[]> {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const key = keyFn(item);
    if (!key) continue;
    const arr = map.get(key);
    if (arr) arr.push(item);
    else map.set(key, [item]);
  }
  return map;
}

// ---------------------------------------------------------------------------
// Military data shape (generic, since militaryData is unknown[])
// ---------------------------------------------------------------------------

interface MilitaryItem {
  type?: string;
  region?: string;
  lat?: number;
  lng?: number;
  callsign?: string;
  country?: string;
  timestamp?: number;
}

// ---------------------------------------------------------------------------
// Signal Engine
// ---------------------------------------------------------------------------

class SignalEngine {
  private signals: Signal[] = [];
  private seen = new Map<string, number>(); // dedup key → timestamp

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /**
   * Process a batch of news + market + military data to detect signals.
   * Returns only the NEW signals generated by this analysis pass.
   */
  analyze(
    news: NewsItem[],
    marketData?: unknown[],
    militaryData?: unknown[],
  ): Signal[] {
    this.evictExpired();

    const newSignals: Signal[] = [];

    // 1. Velocity Spike: headline velocity > threshold
    newSignals.push(...this.detectVelocitySpikes(news));

    // 2. Convergence: multiple sources reporting same entity/event
    newSignals.push(...this.detectConvergence(news));

    // 3. Triangulation: 3+ independent tier-1/2 sources on same topic
    newSignals.push(...this.detectTriangulation(news));

    // 4. Geographic Convergence: multiple items clustering in same region
    newSignals.push(...this.detectGeographicConvergence(news));

    // 5. Sector Cascade: many items in same threat category
    newSignals.push(...this.detectSectorCascade(news));

    // 6. Military Surge: spike in military flights/vessels in a region
    newSignals.push(...this.detectMilitarySurge(militaryData));

    // 7. Propaganda flagging from state media convergence
    newSignals.push(...this.detectPropagandaConvergence(news));

    // Deduplicate against existing signals
    const unique = newSignals.filter(s => !this.isDuplicate(s));
    this.signals.push(...unique);

    return unique;
  }

  getSignals(): Signal[] {
    return [...this.signals];
  }

  getSignalCount(): number {
    return this.signals.length;
  }

  getByType(type: SignalType): Signal[] {
    return this.signals.filter(s => s.type === type);
  }

  getBySeverity(severity: SeverityLevel): Signal[] {
    return this.signals.filter(s => s.severity === severity);
  }

  /** Get signals sorted by severity (critical first) then recency. */
  getSorted(): Signal[] {
    const order: Record<SeverityLevel, number> = {
      critical: 0, high: 1, elevated: 2, guarded: 3, low: 4,
    };
    return [...this.signals].sort((a, b) => {
      const sevDiff = order[a.severity] - order[b.severity];
      if (sevDiff !== 0) return sevDiff;
      return b.timestamp - a.timestamp; // newer first within same severity
    });
  }

  clear(): void {
    this.signals = [];
    this.seen.clear();
  }

  // -------------------------------------------------------------------------
  // Detection: Velocity Spike
  // -------------------------------------------------------------------------

  /**
   * Detect when headline volume about a specific entity or topic
   * spikes above a threshold within a short window.
   */
  private detectVelocitySpikes(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const window = 300_000; // 5 min
    const recent = news.filter(n => now - n.timestamp < window);

    if (recent.length === 0) return signals;

    // Check explicit velocity field first
    const highVelocity = recent.filter(n => (n.velocity ?? 0) >= VELOCITY_SPIKE_THRESHOLD);
    if (highVelocity.length > 0) {
      // Group high-velocity items by primary entity
      const entityGroups = new Map<string, NewsItem[]>();
      for (const item of highVelocity) {
        const entities = extractEntities(newsText(item));
        const primary = entities[0] ?? 'unknown';
        const group = entityGroups.get(primary);
        if (group) group.push(item);
        else entityGroups.set(primary, [item]);
      }

      for (const [entityId, items] of entityGroups) {
        const combinedText = items.map(i => newsText(i)).join(' ');
        const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];
        const sources = [...new Set(items.map(i => i.source))];
        const maxVelocity = Math.max(...items.map(i => i.velocity ?? 0));

        signals.push(this.createSignal({
          type: 'velocity-spike',
          title: `Velocity spike: ${entityId} (${maxVelocity.toFixed(1)}/min)`,
          description: `${items.length} headlines in ${window / 60_000}min window about ${entityId}. ` +
            `Peak velocity: ${maxVelocity.toFixed(1)} items/min. ` +
            `Top headline: "${items[0].title}"`,
          severity: upgradeSeverity(scoreSeverity(combinedText), tierConfidence(items.map(i => i.sourceTier))),
          countries: [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))],
          entities: allEntities,
          sources,
        }));
      }
    }

    // Fallback: count-based velocity (many headlines about same entity)
    const entityCounts = new Map<string, NewsItem[]>();
    for (const item of recent) {
      const entities = extractEntities(newsText(item));
      for (const eid of entities) {
        const group = entityCounts.get(eid);
        if (group) group.push(item);
        else entityCounts.set(eid, [item]);
      }
    }

    for (const [entityId, items] of entityCounts) {
      const rate = items.length / (window / 60_000); // items per minute
      if (rate >= VELOCITY_SPIKE_THRESHOLD && !highVelocity.length) {
        const combinedText = items.map(i => newsText(i)).join(' ');
        const sources = [...new Set(items.map(i => i.source))];

        signals.push(this.createSignal({
          type: 'velocity-spike',
          title: `Velocity spike: ${entityId} (${rate.toFixed(1)}/min)`,
          description: `${items.length} headlines in ${window / 60_000}min about ${entityId}. ` +
            `Computed rate: ${rate.toFixed(1)}/min. Sources: ${sources.join(', ')}`,
          severity: scoreSeverity(combinedText),
          countries: [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))],
          entities: [entityId, ...new Set(items.flatMap(i => extractEntities(newsText(i))).filter(e => e !== entityId))],
          sources,
        }));
      }
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Convergence
  // -------------------------------------------------------------------------

  /**
   * Multiple independent sources reporting on the same entity or event
   * within a convergence window.
   */
  private detectConvergence(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const recent = news.filter(n => now - n.timestamp < CONVERGENCE_WINDOW);

    // Group by primary entity
    const entityGroups = new Map<string, NewsItem[]>();
    for (const item of recent) {
      const entities = extractEntities(newsText(item));
      for (const eid of entities) {
        const group = entityGroups.get(eid);
        if (group) group.push(item);
        else entityGroups.set(eid, [item]);
      }
    }

    for (const [entityId, items] of entityGroups) {
      const uniqueSources = [...new Set(items.map(i => i.source))];
      if (uniqueSources.length < CONVERGENCE_MIN_SOURCES) continue;

      // Require at least one tier 1-2 source for credibility
      const hasTrustedSource = items.some(i => i.sourceTier <= 2);
      if (!hasTrustedSource && uniqueSources.length < 3) continue;

      const combinedText = items.map(i => newsText(i)).join(' ');
      const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];
      const countries = [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))];
      const tiers = items.map(i => i.sourceTier);
      const baseSeverity = scoreSeverity(combinedText);

      signals.push(this.createSignal({
        type: 'convergence',
        title: `Convergence: ${entityId} across ${uniqueSources.length} sources`,
        description: `${uniqueSources.length} independent sources reporting on ${entityId} within ` +
          `${CONVERGENCE_WINDOW / 60_000}min. Sources: ${uniqueSources.join(', ')}. ` +
          `Key headline: "${items[0].title}"`,
        severity: upgradeSeverity(baseSeverity, tierConfidence(tiers)),
        countries,
        entities: allEntities,
        sources: uniqueSources,
      }));
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Triangulation
  // -------------------------------------------------------------------------

  /**
   * 3+ independent tier-1 or tier-2 sources reporting on the same topic.
   * Higher confidence than general convergence — confirms event veracity.
   */
  private detectTriangulation(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const recent = news.filter(n => now - n.timestamp < CONVERGENCE_WINDOW && n.sourceTier <= 2);

    // Group by primary entity (only tier 1-2 sources)
    const entityGroups = new Map<string, NewsItem[]>();
    for (const item of recent) {
      const entities = extractEntities(newsText(item));
      for (const eid of entities) {
        const group = entityGroups.get(eid);
        if (group) group.push(item);
        else entityGroups.set(eid, [item]);
      }
    }

    for (const [entityId, items] of entityGroups) {
      const uniqueSources = [...new Set(items.map(i => i.source))];
      if (uniqueSources.length < TRIANGULATION_MIN_TIER12) continue;

      const combinedText = items.map(i => newsText(i)).join(' ');
      const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];
      const countries = [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))];
      const baseSeverity = scoreSeverity(combinedText);

      // Triangulated signals are always at least 'elevated'
      const severity: SeverityLevel = baseSeverity === 'guarded' || baseSeverity === 'low'
        ? 'elevated'
        : baseSeverity;

      signals.push(this.createSignal({
        type: 'triangulation',
        title: `Triangulated: ${entityId} confirmed by ${uniqueSources.length} tier-1/2 sources`,
        description: `${uniqueSources.length} high-credibility sources independently confirm activity ` +
          `involving ${entityId}. Sources: ${uniqueSources.join(', ')}. ` +
          `This meets the triangulation threshold for verified intelligence.`,
        severity,
        countries,
        entities: allEntities,
        sources: uniqueSources,
      }));
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Geographic Convergence
  // -------------------------------------------------------------------------

  /**
   * Multiple events from different categories clustering in the same
   * geographic area, suggesting a developing situation.
   */
  private detectGeographicConvergence(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const geoTagged = news.filter(
      n => n.lat != null && n.lng != null && now - n.timestamp < CONVERGENCE_WINDOW,
    );

    if (geoTagged.length < 3) return signals;

    // Grid-based clustering (rounded to GEO_CONVERGENCE_RADIUS degrees)
    const clusters = new Map<string, NewsItem[]>();
    for (const item of geoTagged) {
      const cellLat = Math.round(item.lat! / GEO_CONVERGENCE_RADIUS) * GEO_CONVERGENCE_RADIUS;
      const cellLng = Math.round(item.lng! / GEO_CONVERGENCE_RADIUS) * GEO_CONVERGENCE_RADIUS;
      const key = `${cellLat},${cellLng}`;
      const cluster = clusters.get(key);
      if (cluster) cluster.push(item);
      else clusters.set(key, [item]);
    }

    for (const [cellKey, items] of clusters) {
      // Require multiple distinct threat categories for true convergence
      const categories = new Set(items.map(i => i.threatCategory).filter(Boolean));
      if (categories.size < 2 || items.length < 3) continue;

      const combinedText = items.map(i => newsText(i)).join(' ');
      const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];
      const countries = [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))];
      const sources = [...new Set(items.map(i => i.source))];
      const [lat, lng] = cellKey.split(',').map(Number);

      signals.push(this.createSignal({
        type: 'geographic-convergence',
        title: `Geographic convergence near ${lat}°, ${lng}° — ${categories.size} domains`,
        description: `${items.length} events across ${categories.size} threat categories ` +
          `(${[...categories].join(', ')}) clustering within ${GEO_CONVERGENCE_RADIUS}° of ` +
          `${lat}°N ${lng}°E. This geographic concentration suggests a developing multi-domain situation.`,
        severity: upgradeSeverity(scoreSeverity(combinedText), tierConfidence(items.map(i => i.sourceTier))),
        countries,
        entities: allEntities,
        sources,
      }));
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Sector Cascade
  // -------------------------------------------------------------------------

  /**
   * Surge of news items within a single threat category, suggesting
   * a cascade or rapidly evolving situation in one domain.
   */
  private detectSectorCascade(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const recent = news.filter(n => n.threatCategory && now - n.timestamp < CONVERGENCE_WINDOW);

    const byCategory = groupBy(recent, n => n.threatCategory ?? '');

    for (const [category, items] of byCategory) {
      if (items.length < SECTOR_CASCADE_MIN) continue;

      const uniqueSources = [...new Set(items.map(i => i.source))];
      // Need at least 2 independent sources to avoid single-source flooding
      if (uniqueSources.length < 2) continue;

      const combinedText = items.map(i => newsText(i)).join(' ');
      const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];
      const countries = [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))];

      signals.push(this.createSignal({
        type: 'sector-cascade',
        title: `Sector cascade: ${category} — ${items.length} items in ${CONVERGENCE_WINDOW / 60_000}min`,
        description: `${items.length} reports in the "${category}" domain from ${uniqueSources.length} ` +
          `sources within ${CONVERGENCE_WINDOW / 60_000}min. Countries involved: ` +
          `${countries.length > 0 ? countries.join(', ') : 'global'}. ` +
          `This volume suggests a rapidly developing ${category} situation.`,
        severity: scoreSeverity(combinedText),
        countries,
        entities: allEntities,
        sources: uniqueSources,
      }));
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Military Surge
  // -------------------------------------------------------------------------

  /**
   * Spike in military flights/vessels within a regional cluster.
   * Processes generic unknown[] data with defensive type checks.
   */
  private detectMilitarySurge(data?: unknown[]): Signal[] {
    const signals: Signal[] = [];
    if (!data || data.length === 0) return signals;

    // Defensively cast and validate each item
    const items: MilitaryItem[] = [];
    for (const raw of data) {
      if (typeof raw !== 'object' || raw === null) continue;
      const obj = raw as Record<string, unknown>;
      items.push({
        type: typeof obj.type === 'string' ? obj.type : undefined,
        region: typeof obj.region === 'string' ? obj.region : undefined,
        lat: typeof obj.lat === 'number' ? obj.lat : undefined,
        lng: typeof obj.lng === 'number' ? obj.lng : undefined,
        callsign: typeof obj.callsign === 'string' ? obj.callsign : undefined,
        country: typeof obj.country === 'string' ? obj.country : undefined,
        timestamp: typeof obj.timestamp === 'number' ? obj.timestamp : undefined,
      });
    }

    if (items.length === 0) return signals;

    // Cluster by named region
    const byRegion = groupBy(items, i => i.region ?? 'unknown');
    for (const [region, regionItems] of byRegion) {
      if (regionItems.length < MILITARY_SURGE_THRESHOLD) continue;

      const types = [...new Set(regionItems.map(i => i.type).filter(Boolean))];
      const countries = [...new Set(regionItems.map(i => i.country).filter(Boolean) as string[])];
      const callsigns = regionItems.map(i => i.callsign).filter(Boolean).slice(0, 5);

      // More types = higher severity (mixed military activity is more concerning)
      let severity: SeverityLevel = 'elevated';
      if (regionItems.length >= MILITARY_SURGE_THRESHOLD * 3) severity = 'critical';
      else if (regionItems.length >= MILITARY_SURGE_THRESHOLD * 2) severity = 'high';

      signals.push(this.createSignal({
        type: 'military-surge',
        title: `Military surge: ${region} — ${regionItems.length} tracks`,
        description: `${regionItems.length} military assets detected in ${region} region. ` +
          `Types: ${types.join(', ') || 'unspecified'}. ` +
          `Countries: ${countries.join(', ') || 'unknown'}. ` +
          (callsigns.length > 0 ? `Notable callsigns: ${callsigns.join(', ')}.` : ''),
        severity,
        countries,
        entities: countries.flatMap(c => extractEntities(c)),
        sources: ['adsb-exchange', 'military-tracker'],
      }));
    }

    // Also cluster by geographic grid for items without named regions
    const unregioned = items.filter(i => !i.region && i.lat != null && i.lng != null);
    if (unregioned.length >= MILITARY_SURGE_THRESHOLD) {
      const geoClusters = new Map<string, MilitaryItem[]>();
      for (const item of unregioned) {
        const cellLat = Math.round(item.lat! / GEO_CONVERGENCE_RADIUS) * GEO_CONVERGENCE_RADIUS;
        const cellLng = Math.round(item.lng! / GEO_CONVERGENCE_RADIUS) * GEO_CONVERGENCE_RADIUS;
        const key = `${cellLat},${cellLng}`;
        const cluster = geoClusters.get(key);
        if (cluster) cluster.push(item);
        else geoClusters.set(key, [item]);
      }

      for (const [cellKey, clusterItems] of geoClusters) {
        if (clusterItems.length < MILITARY_SURGE_THRESHOLD) continue;
        const [lat, lng] = cellKey.split(',').map(Number);
        const countries = [...new Set(clusterItems.map(i => i.country).filter(Boolean) as string[])];

        signals.push(this.createSignal({
          type: 'military-surge',
          title: `Military surge near ${lat}°N ${lng}°E — ${clusterItems.length} tracks`,
          description: `${clusterItems.length} military assets concentrated near ` +
            `${lat}°N ${lng}°E without named region classification. ` +
            `Countries involved: ${countries.join(', ') || 'unknown'}.`,
          severity: clusterItems.length >= MILITARY_SURGE_THRESHOLD * 2 ? 'high' : 'elevated',
          countries,
          entities: countries.flatMap(c => extractEntities(c)),
          sources: ['adsb-exchange', 'military-tracker'],
        }));
      }
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Detection: Propaganda Convergence
  // -------------------------------------------------------------------------

  /**
   * Detect when multiple state-media / propaganda-flagged sources
   * push the same narrative simultaneously — potential info op.
   */
  private detectPropagandaConvergence(news: NewsItem[]): Signal[] {
    const signals: Signal[] = [];
    const now = Date.now();
    const propagandaItems = news.filter(
      n => n.propagandaRisk && now - n.timestamp < CONVERGENCE_WINDOW,
    );

    if (propagandaItems.length < 2) return signals;

    // Group by primary entity
    const entityGroups = new Map<string, NewsItem[]>();
    for (const item of propagandaItems) {
      const entities = extractEntities(newsText(item));
      for (const eid of entities) {
        const group = entityGroups.get(eid);
        if (group) group.push(item);
        else entityGroups.set(eid, [item]);
      }
    }

    for (const [entityId, items] of entityGroups) {
      const uniqueSources = [...new Set(items.map(i => i.source))];
      if (uniqueSources.length < 2) continue;

      const countries = [...new Set(items.flatMap(i => i.countries ?? (i.country ? [i.country] : [])))];
      const allEntities = [...new Set(items.flatMap(i => extractEntities(newsText(i))))];

      signals.push(this.createSignal({
        type: 'convergence',
        title: `⚠ Propaganda convergence: ${entityId} — ${uniqueSources.length} state-media sources`,
        description: `${uniqueSources.length} propaganda-flagged sources are pushing a coordinated ` +
          `narrative about ${entityId}: ${uniqueSources.join(', ')}. ` +
          `Treat with heightened skepticism. Cross-reference with tier-1 sources recommended.`,
        severity: 'elevated',
        countries,
        entities: allEntities,
        sources: uniqueSources,
      }));
    }

    return signals;
  }

  // -------------------------------------------------------------------------
  // Signal Creation
  // -------------------------------------------------------------------------

  private createSignal(params: {
    type: SignalType;
    title: string;
    description: string;
    severity: SeverityLevel;
    countries?: string[];
    entities?: string[];
    sources: string[];
  }): Signal {
    return {
      id: uid(),
      type: params.type,
      title: params.title,
      description: params.description,
      severity: params.severity,
      timestamp: Date.now(),
      countries: params.countries?.length ? params.countries : undefined,
      entities: params.entities?.length ? params.entities : undefined,
      sources: params.sources,
      ttl: SIGNAL_TTLS[params.type],
    };
  }

  // -------------------------------------------------------------------------
  // Dedup + Eviction
  // -------------------------------------------------------------------------

  private isDuplicate(signal: Signal): boolean {
    // Dedup by type + normalized title (ignore velocity numbers / timestamps)
    const normalizedTitle = signal.title.replace(/[\d.]+/g, '#').toLowerCase();
    const key = `${signal.type}:${normalizedTitle}`;
    const existing = this.seen.get(key);
    if (existing && Date.now() - existing < SIGNAL_TTLS[signal.type]) return true;
    this.seen.set(key, Date.now());
    return false;
  }

  private evictExpired(): void {
    const now = Date.now();
    this.signals = this.signals.filter(s => now - s.timestamp < s.ttl);

    // Purge old dedup keys (anything older than max TTL)
    for (const [key, ts] of this.seen) {
      if (now - ts > 14400_000) this.seen.delete(key);
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton Export
// ---------------------------------------------------------------------------

export const signalEngine = new SignalEngine();
