// ============================================================================
// Atlas Intel — Geographic Convergence Detection
// ============================================================================
//
// Detects geographic clustering of disparate event types within 1°×1° grid
// cells. When protests, military flights, naval vessels, and seismic activity
// converge in the same cell, the score rises — signalling potential escalation.
// ============================================================================

import type { ConvergenceCell, SeverityLevel } from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Recognised event types for convergence analysis. */
const CONVERGENCE_TYPES = new Set([
  'protest',
  'military-flight',
  'naval-vessel',
  'earthquake',
]);

/** Minimum convergence score required to emit a cell. */
const DEFAULT_THRESHOLD = 50;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ConvergenceEvent {
  lat: number;
  lng: number;
  type: string;
  timestamp: number;
}

export type AlertLevel = 'Critical' | 'High' | 'Elevated';

export interface ConvergenceAlert {
  cell: ConvergenceCell;
  level: AlertLevel;
}

// ---------------------------------------------------------------------------
// Internal grid accumulator
// ---------------------------------------------------------------------------

interface GridAccumulator {
  lat: number;
  lng: number;
  types: Set<string>;
  events: number;
}

// ---------------------------------------------------------------------------
// ConvergenceDetector
// ---------------------------------------------------------------------------

export class ConvergenceDetector {
  private threshold: number;

  constructor(threshold: number = DEFAULT_THRESHOLD) {
    this.threshold = threshold;
  }

  // -------------------------------------------------------------------------
  // Core Analysis
  // -------------------------------------------------------------------------

  /**
   * Analyze an array of geo-located events and return convergence cells
   * that exceed the scoring threshold.
   *
   * Grid key: `Math.floor(lat):Math.floor(lng)` — yielding 1°×1° cells.
   */
  analyze(events: ConvergenceEvent[]): ConvergenceCell[] {
    const grid = new Map<string, GridAccumulator>();

    // --- Bucket events into grid cells ---
    for (const event of events) {
      // Only consider recognised convergence types
      if (!CONVERGENCE_TYPES.has(event.type)) continue;

      const key = this.gridKey(event.lat, event.lng);

      let cell = grid.get(key);
      if (!cell) {
        cell = {
          lat: Math.floor(event.lat) + 0.5, // cell center
          lng: Math.floor(event.lng) + 0.5,
          types: new Set(),
          events: 0,
        };
        grid.set(key, cell);
      }

      cell.types.add(event.type);
      cell.events++;
    }

    // --- Score each cell and filter ---
    const results: ConvergenceCell[] = [];

    for (const acc of grid.values()) {
      const score = this.score(acc.types, acc.events);

      if (score > this.threshold) {
        results.push({
          lat: acc.lat,
          lng: acc.lng,
          types: acc.types,
          events: acc.events,
          score,
        });
      }
    }

    // Sort highest score first
    results.sort((a, b) => b.score - a.score);

    return results;
  }

  // -------------------------------------------------------------------------
  // Scoring
  // -------------------------------------------------------------------------

  /**
   * Convergence score for a single grid cell.
   *
   * `type_score = types.size * 25 + Math.min(25, total * 2)`
   *
   * - 4 distinct types → base 100 (maximum diversity).
   * - Event volume adds up to 25 bonus points.
   */
  private score(types: Set<string>, total: number): number {
    return types.size * 25 + Math.min(25, total * 2);
  }

  // -------------------------------------------------------------------------
  // Alert Classification
  // -------------------------------------------------------------------------

  /**
   * Determine alert level from a convergence cell based on distinct type count.
   *
   * - 4 types → Critical
   * - 3 types → High
   * - 2 types → Elevated
   */
  getAlertLevel(cell: ConvergenceCell): AlertLevel {
    if (cell.types.size >= 4) return 'Critical';
    if (cell.types.size >= 3) return 'High';
    return 'Elevated';
  }

  /**
   * Map a ConvergenceCell's alert level to the standard severity system.
   */
  getSeverity(cell: ConvergenceCell): SeverityLevel {
    if (cell.types.size >= 4) return 'critical';
    if (cell.types.size >= 3) return 'high';
    return 'elevated';
  }

  /**
   * Convenience: analyze events and produce fully classified alerts.
   */
  detectAlerts(events: ConvergenceEvent[]): ConvergenceAlert[] {
    const cells = this.analyze(events);
    return cells.map((cell) => ({
      cell,
      level: this.getAlertLevel(cell),
    }));
  }

  // -------------------------------------------------------------------------
  // Utilities
  // -------------------------------------------------------------------------

  /** Generate the grid key for a coordinate pair. */
  private gridKey(lat: number, lng: number): string {
    return `${Math.floor(lat)}:${Math.floor(lng)}`;
  }

  /** Update the scoring threshold at runtime. */
  setThreshold(value: number): void {
    this.threshold = value;
  }

  /** Get the current threshold. */
  getThreshold(): number {
    return this.threshold;
  }
}

// ---------------------------------------------------------------------------
// Singleton Export
// ---------------------------------------------------------------------------

export const convergenceDetector = new ConvergenceDetector();
