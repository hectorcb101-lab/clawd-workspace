// ============================================================================
// Atlas Intel — Data Bridge Service
// Fetches JSON data from the Python FastAPI backend and manages polling,
// caching, circuit-breaking, and subscriber notifications per data source.
// ============================================================================

import { CircuitBreaker, safeFetchJSON } from '@/utils/circuit-breaker';
import type { DataStatus } from '@/types/index';

const BASE_URL = import.meta.env.VITE_DATA_BRIDGE_URL || '';

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

interface DataSourceConfig {
  endpoint: string;
  interval: number;   // ms between polls
  critical: boolean;  // whether failure should be flagged prominently
}

/**
 * All 23 data sources served by the FastAPI backend.
 * Intervals are tuned per source: high-frequency live feeds poll faster,
 * static reference data polls infrequently.
 */
const DATA_SOURCES: Record<string, DataSourceConfig> = {
  // — Live / high-frequency feeds —
  vessels:            { endpoint: '/api/data/vessel_live.json',          interval: 60_000,   critical: true  },
  flights:            { endpoint: '/api/data/flight_live.json',          interval: 30_000,   critical: true  },
  military:           { endpoint: '/api/data/military_live.json',        interval: 30_000,   critical: true  },
  earthquakes:        { endpoint: '/api/data/earthquake_live.json',      interval: 60_000,   critical: true  },
  cyber:              { endpoint: '/api/data/cyber_threats_live.json',   interval: 60_000,   critical: true  },
  news:               { endpoint: '/api/data/news_live.json',            interval: 30_000,   critical: true  },
  webcams:            { endpoint: '/api/data/webcam_live.json',          interval: 120_000,  critical: false },
  wildfires:          { endpoint: '/api/data/wildfire_live.json',        interval: 120_000,  critical: false },
  radiation:          { endpoint: '/api/data/radiation_live.json',       interval: 120_000,  critical: true  },
  satellites:         { endpoint: '/api/data/satellite_live.json',       interval: 60_000,   critical: false },
  unrest:             { endpoint: '/api/data/unrest_live.json',          interval: 60_000,   critical: true  },
  infrastructure:     { endpoint: '/api/data/infrastructure_live.json',  interval: 120_000,  critical: false },
  gps_jamming:        { endpoint: '/api/data/gps_jamming_live.json',     interval: 60_000,   critical: true  },
  cables:             { endpoint: '/api/data/cable_health_live.json',    interval: 120_000,  critical: false },

  // — Alerts / analytical —
  alerts:             { endpoint: '/api/data/alerts.json',               interval: 30_000,   critical: true  },
  geopolitical:       { endpoint: '/api/data/geopolitical.json',         interval: 300_000,  critical: false },

  // — Reference / static data (poll infrequently) —
  military_bases:     { endpoint: '/api/data/military_bases.json',       interval: 600_000,  critical: false },
  nuclear_sites:      { endpoint: '/api/data/nuclear_sites.json',        interval: 600_000,  critical: false },
  pipelines:          { endpoint: '/api/data/pipelines.json',            interval: 600_000,  critical: false },
  trade_routes:       { endpoint: '/api/data/trade_routes.json',         interval: 600_000,  critical: false },
  commodities:        { endpoint: '/api/data/commodities_data.json',     interval: 300_000,  critical: false },
  airports:           { endpoint: '/api/data/airports.json',             interval: 600_000,  critical: false },
  military_callsigns: { endpoint: '/api/data/military_callsigns.json',  interval: 600_000,  critical: false },
};

// ---------------------------------------------------------------------------
// DataBridge
// ---------------------------------------------------------------------------

class DataBridge {
  private breakers = new Map<string, CircuitBreaker>();
  private cache = new Map<string, { data: unknown; timestamp: number }>();
  private timers = new Map<string, ReturnType<typeof setInterval>>();
  private listeners = new Map<string, Set<(data: unknown) => void>>();
  private statusMap = new Map<string, DataStatus>();

  constructor() {
    // Pre-initialise a circuit breaker and status entry for every source
    for (const [source, cfg] of Object.entries(DATA_SOURCES)) {
      this.breakers.set(
        source,
        new CircuitBreaker({
          maxFailures: cfg.critical ? 5 : 3,
          resetTimeout: cfg.critical ? 30_000 : 60_000,
          timeout: 15_000,
          retries: cfg.critical ? 2 : 1,
        }),
      );

      this.statusMap.set(source, {
        source,
        status: 'unavailable',
        lastUpdated: 0,
        count: 0,
      });
    }
  }

  // -------------------------------------------------------------------------
  // Fetch
  // -------------------------------------------------------------------------

  /**
   * Fetch a specific data source.
   * Returns cached data on failure, or `null` if nothing is available.
   */
  async fetch<T>(source: string): Promise<T | null> {
    const cfg = DATA_SOURCES[source];
    if (!cfg) {
      console.warn(`[DataBridge] Unknown source: ${source}`);
      return null;
    }

    const breaker = this.breakers.get(source)!;
    const url = `${BASE_URL}${cfg.endpoint}`;
    const data = await safeFetchJSON<T>(url, breaker);

    if (data !== null) {
      // Successful fetch — update cache, status, and notify listeners
      const now = Date.now();
      const count = Array.isArray(data) ? data.length : 1;
      this.cache.set(source, { data, timestamp: now });
      this.statusMap.set(source, {
        source,
        status: 'live',
        lastUpdated: now,
        count,
      });
      this.notify(source, data);
      return data;
    }

    // Fetch failed — fall back to cache
    const cached = this.cache.get(source);
    if (cached) {
      this.statusMap.set(source, {
        source,
        status: 'cached',
        lastUpdated: cached.timestamp,
        count: Array.isArray(cached.data) ? cached.data.length : 1,
      });
      return cached.data as T;
    }

    // Nothing available at all
    this.statusMap.set(source, {
      source,
      status: 'unavailable',
      lastUpdated: 0,
      count: 0,
    });
    return null;
  }

  // -------------------------------------------------------------------------
  // Subscribe
  // -------------------------------------------------------------------------

  /**
   * Subscribe to data updates for a source.
   * Returns an unsubscribe function.
   */
  on(source: string, callback: (data: unknown) => void): () => void {
    if (!this.listeners.has(source)) {
      this.listeners.set(source, new Set());
    }
    this.listeners.get(source)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(source)?.delete(callback);
    };
  }

  // -------------------------------------------------------------------------
  // Polling
  // -------------------------------------------------------------------------

  /** Start polling for a single source. */
  startPolling(source: string): void {
    const cfg = DATA_SOURCES[source];
    if (!cfg) {
      console.warn(`[DataBridge] Cannot poll unknown source: ${source}`);
      return;
    }

    // Don't start duplicate timers
    if (this.timers.has(source)) return;

    // Fetch immediately, then at interval
    void this.fetch(source);
    const timer = setInterval(() => void this.fetch(source), cfg.interval);
    this.timers.set(source, timer);
  }

  /** Stop polling for a single source. */
  stopPolling(source: string): void {
    const timer = this.timers.get(source);
    if (timer) {
      clearInterval(timer);
      this.timers.delete(source);
    }
  }

  /** Start polling for all sources. */
  startAll(): void {
    for (const source of Object.keys(DATA_SOURCES)) {
      this.startPolling(source);
    }
  }

  /** Stop polling for all sources. */
  stopAll(): void {
    for (const source of this.timers.keys()) {
      this.stopPolling(source);
    }
  }

  // -------------------------------------------------------------------------
  // Status
  // -------------------------------------------------------------------------

  /** Get status of all data sources. */
  getStatus(): DataStatus[] {
    return Array.from(this.statusMap.values());
  }

  /** Get status of a single data source. */
  getSourceStatus(source: string): DataStatus | null {
    return this.statusMap.get(source) ?? null;
  }

  // -------------------------------------------------------------------------
  // Cache Access
  // -------------------------------------------------------------------------

  /** Get cached data without triggering a fetch. */
  getCached<T>(source: string): T | null {
    const entry = this.cache.get(source);
    return entry ? (entry.data as T) : null;
  }

  /** Get the age (ms) of cached data, or Infinity if not cached. */
  getCacheAge(source: string): number {
    const entry = this.cache.get(source);
    return entry ? Date.now() - entry.timestamp : Infinity;
  }

  // -------------------------------------------------------------------------
  // Introspection
  // -------------------------------------------------------------------------

  /** List all known source names. */
  get sources(): string[] {
    return Object.keys(DATA_SOURCES);
  }

  /** Check whether a source is currently being polled. */
  isPolling(source: string): boolean {
    return this.timers.has(source);
  }

  /** Get config for a source. */
  getConfig(source: string): DataSourceConfig | null {
    return DATA_SOURCES[source] ?? null;
  }

  // -------------------------------------------------------------------------
  // Internals
  // -------------------------------------------------------------------------

  /** Notify all subscribers for a source with fresh data. */
  private notify(source: string, data: unknown): void {
    const subs = this.listeners.get(source);
    if (!subs || subs.size === 0) return;

    for (const cb of subs) {
      try {
        cb(data);
      } catch (err) {
        console.error(`[DataBridge] Listener error for "${source}":`, err);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const dataBridge = new DataBridge();
export { DATA_SOURCES };
export type { DataSourceConfig };
