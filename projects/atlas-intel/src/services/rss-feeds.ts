// ============================================================================
// Atlas Intel — RSS Feed Aggregator
// ============================================================================

import type { NewsItem, FeedDefinition } from '@/types/index';
import { FEEDS } from '@/config/feeds';
import { uid } from '@/utils/dom-utils';

// ---------------------------------------------------------------------------
// RSS proxy response shapes
// ---------------------------------------------------------------------------

interface Rss2JsonItem {
  title?: string;
  link?: string;
  pubDate?: string;
  description?: string;
  author?: string;
  categories?: string[];
}

interface Rss2JsonResponse {
  status: string;
  items?: Rss2JsonItem[];
}

// ---------------------------------------------------------------------------
// Aggregator
// ---------------------------------------------------------------------------

class RSSAggregator {
  private items: NewsItem[] = [];
  private velocity = new Map<string, number[]>(); // entity → timestamps of mentions
  private fetchInProgress = false;

  // ── Public API ──────────────────────────────────────────────────────────

  /** Fetch all configured feeds via CORS proxy, merge, deduplicate, sort. */
  async fetchAll(): Promise<NewsItem[]> {
    if (this.fetchInProgress) return this.items;
    this.fetchInProgress = true;

    try {
      const results = await Promise.allSettled(
        FEEDS.map(feed => this.fetchFeed(feed)),
      );

      const newItems = results
        .filter(
          (r): r is PromiseFulfilledResult<NewsItem[]> =>
            r.status === 'fulfilled',
        )
        .flatMap(r => r.value);

      this.items = this.mergeAndDeduplicate(newItems);
      this.updateVelocity();
      return this.items;
    } finally {
      this.fetchInProgress = false;
    }
  }

  /** Return the current cached item list (no network call). */
  getItems(): NewsItem[] {
    return this.items;
  }

  /** Filter items by feed category string (e.g. 'cyber', 'defense'). */
  getByCategory(category: string): NewsItem[] {
    // Map feed names to their categories for lookup
    const feedCategoryMap = new Map<string, string>();
    for (const feed of FEEDS) {
      feedCategoryMap.set(feed.name, feed.category);
    }
    return this.items.filter(item => {
      const feedCat = feedCategoryMap.get(item.source);
      return feedCat === category;
    });
  }

  /** Filter items by ThreatCategory (assigned by threat classifier). */
  getByThreatCategory(category: string): NewsItem[] {
    return this.items.filter(item => item.threatCategory === category);
  }

  /**
   * Return the mention velocity for an entity (mentions per hour, last 6 h).
   * Higher values indicate trending / spike.
   */
  getVelocity(entity: string): number {
    const timestamps = this.velocity.get(entity.toLowerCase());
    if (!timestamps || timestamps.length === 0) return 0;

    const sixHoursAgo = Date.now() - 6 * 3600_000;
    const recent = timestamps.filter(t => t >= sixHoursAgo);
    if (recent.length === 0) return 0;

    // Mentions per hour over the window
    const windowHours =
      Math.max(1, (Date.now() - Math.min(...recent)) / 3600_000);
    return recent.length / windowHours;
  }

  /** Return the top N trending entities by velocity. */
  getTopEntities(n = 10): { entity: string; velocity: number }[] {
    const entries: { entity: string; velocity: number }[] = [];
    for (const [entity] of this.velocity) {
      entries.push({ entity, velocity: this.getVelocity(entity) });
    }
    return entries
      .sort((a, b) => b.velocity - a.velocity)
      .slice(0, n);
  }

  // ── Single feed fetch ───────────────────────────────────────────────────

  private async fetchFeed(feed: FeedDefinition): Promise<NewsItem[]> {
    const proxyUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(feed.url)}`;

    try {
      const resp = await fetch(proxyUrl, { signal: AbortSignal.timeout(10_000) });
      if (!resp.ok) return [];

      const data: Rss2JsonResponse = await resp.json();
      if (data.status !== 'ok' || !data.items) return [];

      return data.items.map((item): NewsItem => ({
        id: uid(),
        title: (item.title || '').trim(),
        url: item.link || '',
        source: feed.name,
        sourceTier: feed.tier,
        timestamp: new Date(item.pubDate || Date.now()).getTime(),
        propagandaRisk: feed.propagandaRisk || false,
      }));
    } catch {
      // Network error, timeout, or parse failure — silently skip
      return [];
    }
  }

  // ── Deduplication ───────────────────────────────────────────────────────

  private mergeAndDeduplicate(incoming: NewsItem[]): NewsItem[] {
    // Build a map keyed by normalised title for fast de-dup
    const seen = new Map<string, NewsItem>();

    // Process existing items first (they keep their IDs)
    for (const item of this.items) {
      const key = this.normTitle(item.title);
      if (key && !seen.has(key)) {
        seen.set(key, item);
      }
    }

    // Merge incoming — prefer item with highest-tier source (lower number)
    for (const item of incoming) {
      const key = this.normTitle(item.title);
      if (!key) continue;

      const existing = seen.get(key);
      if (!existing) {
        seen.set(key, item);
      } else if (item.sourceTier < existing.sourceTier) {
        // Higher tier source wins, keep the newer ID
        seen.set(key, { ...item, id: existing.id });
      }
    }

    // Sort newest first
    return Array.from(seen.values()).sort(
      (a, b) => b.timestamp - a.timestamp,
    );
  }

  /** Normalise a headline for dedup comparison. */
  private normTitle(title: string): string {
    return title
      .toLowerCase()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  // ── Velocity tracking ──────────────────────────────────────────────────

  private updateVelocity(): void {
    const now = Date.now();
    const sixHoursAgo = now - 6 * 3600_000;

    // Extract simple "entities" (capitalised multi-word tokens) from titles
    for (const item of this.items) {
      if (item.timestamp < sixHoursAgo) continue;

      const entities = this.extractEntities(item.title);
      for (const entity of entities) {
        const key = entity.toLowerCase();
        let timestamps = this.velocity.get(key);
        if (!timestamps) {
          timestamps = [];
          this.velocity.set(key, timestamps);
        }
        timestamps.push(item.timestamp);
      }
    }

    // Prune stale entries older than 6 h
    for (const [key, timestamps] of this.velocity) {
      const fresh = timestamps.filter(t => t >= sixHoursAgo);
      if (fresh.length === 0) {
        this.velocity.delete(key);
      } else {
        this.velocity.set(key, fresh);
      }
    }
  }

  /**
   * Cheap entity extraction — pull out capitalised bigrams/trigrams that
   * appear entity-like (country names, org names, people).
   */
  private extractEntities(title: string): string[] {
    const entities: string[] = [];
    // Match sequences of 2–4 capitalised words
    const regex = /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b/g;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(title)) !== null) {
      entities.push(match[1]);
    }
    // Also capture ALL-CAPS acronyms (NATO, IAEA, etc.)
    const acroRegex = /\b([A-Z]{2,6})\b/g;
    while ((match = acroRegex.exec(title)) !== null) {
      entities.push(match[1]);
    }
    return entities;
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const rssAggregator = new RSSAggregator();
