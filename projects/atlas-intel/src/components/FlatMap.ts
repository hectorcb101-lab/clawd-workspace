// ============================================================================
// Atlas Intel — 2D Flat Map Component (deck.gl + MapLibre GL)
// ============================================================================

import type {
  MapMarker,
  MarkerKind,
  Coordinates,
  TileProvider,
  MapTheme,
} from '@/types/index';
import { debounce } from '@/utils/dom-utils';

// ---------------------------------------------------------------------------
// Lazy-loaded module caches — enables Vite code-splitting
// ---------------------------------------------------------------------------

let maplibregl: typeof import('maplibre-gl') | null = null;

async function loadMapLibre() {
  if (!maplibregl) {
    maplibregl = await import('maplibre-gl');
    // Side-effect: inject maplibre CSS into <head>
    await import('maplibre-gl/dist/maplibre-gl.css');
  }
  return maplibregl;
}

// We import deck.gl sub-packages on demand instead of the umbrella package
// so the bundler can tree-shake unused layers.

// ---------------------------------------------------------------------------
// Tile Provider URLs
// ---------------------------------------------------------------------------

const TILE_PROVIDERS: Record<TileProvider, Record<MapTheme, string>> = {
  openfreemap: {
    dark: 'https://tiles.openfreemap.org/styles/dark',
    light: 'https://tiles.openfreemap.org/styles/bright',
  },
  carto: {
    dark: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    light: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
  },
};

// ---------------------------------------------------------------------------
// Marker color palette by kind
// ---------------------------------------------------------------------------

const MARKER_COLORS: Record<MarkerKind | string, [number, number, number, number]> = {
  vessel:         [68, 136, 255, 200],
  flight:         [255, 215, 0, 200],
  earthquake:     [255, 136, 0, 200],
  fire:           [255, 68, 0, 200],
  cyber:          [68, 170, 255, 200],
  protest:        [255, 215, 0, 200],
  radiation:      [255, 0, 255, 200],
  base:           [255, 51, 51, 200],
  nuclear:        [255, 0, 255, 200],
  webcam:         [0, 255, 102, 200],
  infrastructure: [0, 255, 204, 200],
  'gps-jam':      [255, 136, 0, 200],
  satellite:      [150, 150, 255, 200],
  chokepoint:     [255, 200, 60, 200],
  cable:          [0, 200, 255, 200],
  pipeline:       [200, 120, 60, 200],
  'trade-route':  [120, 200, 120, 200],
};

const DEFAULT_COLOR: [number, number, number, number] = [200, 200, 200, 200];

// ---------------------------------------------------------------------------
// Solar position helpers for day/night terminator
// ---------------------------------------------------------------------------

/** Degrees → radians */
function deg2rad(d: number): number {
  return (d * Math.PI) / 180;
}

/** Radians → degrees */
function rad2deg(r: number): number {
  return (r * 180) / Math.PI;
}

/**
 * Compute the sub-solar point (lat/lng where the Sun is directly overhead)
 * for a given Date using a simplified astronomical model.
 */
function subSolarPoint(date: Date): { lat: number; lng: number } {
  const JD =
    date.getTime() / 86400000 + 2440587.5; // Julian date
  const n = JD - 2451545.0; // days since J2000.0

  // Mean longitude of the Sun (degrees)
  const L = (280.46 + 0.9856474 * n) % 360;
  // Mean anomaly (degrees)
  const g = deg2rad(((357.528 + 0.9856003 * n) % 360 + 360) % 360);

  // Ecliptic longitude (degrees)
  const lambda = deg2rad(L + 1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g));

  // Obliquity of the ecliptic
  const epsilon = deg2rad(23.439 - 0.0000004 * n);

  // Solar declination (latitude)
  const declination = rad2deg(Math.asin(Math.sin(epsilon) * Math.sin(lambda)));

  // Equation of time (minutes) — simplified
  const eqTime =
    -1.915 * Math.sin(g) -
    0.02 * Math.sin(2 * g) +
    2.466 * Math.sin(2 * lambda) -
    0.053 * Math.sin(4 * lambda);

  // Hour angle of the Sun → sub-solar longitude
  const minutesUTC =
    date.getUTCHours() * 60 + date.getUTCMinutes() + date.getUTCSeconds() / 60;
  const solarNoonOffset = 720 - minutesUTC - eqTime; // minutes from solar noon
  const lng = solarNoonOffset / 4; // 1 degree = 4 minutes

  return {
    lat: declination,
    lng: ((lng + 540) % 360) - 180, // normalize to [-180, 180]
  };
}

/**
 * Build a GeoJSON Polygon approximating the nighttime hemisphere.
 * The polygon follows the terminator line where solar altitude = 0.
 */
function buildTerminatorGeoJSON(date: Date): GeoJSON.Feature {
  const sun = subSolarPoint(date);
  const sunLatRad = deg2rad(sun.lat);
  const sunLngDeg = sun.lng;

  // Sample terminator at 1° longitude resolution
  const coords: [number, number][] = [];

  for (let i = 0; i <= 360; i++) {
    const lng = -180 + i;
    const lngRad = deg2rad(lng - sunLngDeg);

    // Terminator latitude: where solar elevation = 0
    // tan(lat) = -cos(hourAngle) / tan(declination)
    // Simplified: lat = atan(-cos(lngDiff) / tan(decl))
    let lat: number;
    if (Math.abs(sun.lat) < 0.1) {
      // Near equinox — smoothly interpolate to avoid discontinuity
      // Use linear blend: at decl=0 the terminator is a vertical great circle
      const tanDecl = Math.tan(deg2rad(Math.max(Math.abs(sun.lat), 0.01))) * Math.sign(sun.lat || 1);
      lat = rad2deg(Math.atan(-Math.cos(lngRad) / tanDecl));
    } else {
      lat = rad2deg(Math.atan(-Math.cos(lngRad) / Math.tan(sunLatRad)));
    }

    lat = Math.max(-90, Math.min(90, lat));
    coords.push([lng, lat]);
  }

  // Close the polygon by sweeping along the bottom or top edge.
  // If Sun is in the northern hemisphere, the night side is below the terminator.
  const nightIsBelow = sun.lat >= 0;

  const polygon: [number, number][] = [];

  if (nightIsBelow) {
    // Night polygon: terminator → bottom edge at -90
    polygon.push(...coords);
    polygon.push([180, -90]);
    polygon.push([-180, -90]);
  } else {
    // Night polygon: terminator → top edge at 90
    polygon.push(...coords);
    polygon.push([180, 90]);
    polygon.push([-180, 90]);
  }

  // Close the ring
  polygon.push(polygon[0]);

  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Polygon',
      coordinates: [polygon],
    },
  };
}

// ---------------------------------------------------------------------------
// FlatMap class
// ---------------------------------------------------------------------------

export class FlatMap {
  private container: HTMLElement;
  private map: InstanceType<typeof import('maplibre-gl').Map> | null = null;
  private deckOverlay: import('@deck.gl/mapbox').MapboxOverlay | null = null;
  private markers: MapMarker[] = [];
  private tileProvider: TileProvider = 'openfreemap';
  private theme: MapTheme = 'dark';
  private resizeHandler: (() => void) | null = null;
  private terminatorTimer: ReturnType<typeof setInterval> | null = null;
  private terminatorEnabled = false;
  private pendingMarkers: MapMarker[] | null = null;
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private visibilityHandler: (() => void) | null = null;

  // Cache the ScatterplotLayer constructor so we don't re-import every update
  private ScatterplotLayerCtor: typeof import('@deck.gl/layers').ScatterplotLayer | null = null;
  private GeoJsonLayerCtor: typeof import('@deck.gl/layers').GeoJsonLayer | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  /**
   * Asynchronously load MapLibre + deck.gl and initialize the map.
   * All heavy libraries are dynamically imported for code splitting.
   */
  async init(options?: {
    tileProvider?: TileProvider;
    theme?: MapTheme;
    center?: Coordinates;
    zoom?: number;
  }): Promise<void> {
    // Load MapLibre and deck.gl overlay in parallel
    const [ml, { MapboxOverlay }, { ScatterplotLayer, GeoJsonLayer }] =
      await Promise.all([
        loadMapLibre(),
        import('@deck.gl/mapbox'),
        import('@deck.gl/layers'),
      ]);

    // Cache layer constructors for later use
    this.ScatterplotLayerCtor = ScatterplotLayer;
    this.GeoJsonLayerCtor = GeoJsonLayer;

    if (options?.tileProvider) this.tileProvider = options.tileProvider;
    if (options?.theme) this.theme = options.theme;

    const styleUrl = TILE_PROVIDERS[this.tileProvider][this.theme];
    const center = options?.center ?? { lat: 20, lng: 0 };
    const zoom = options?.zoom ?? 2;

    // Create MapLibre map
    this.map = new ml.Map({
      container: this.container,
      style: styleUrl,
      center: [center.lng, center.lat],
      zoom,
      minZoom: 1,
      maxZoom: 18,
      attributionControl: false,
    } as ConstructorParameters<typeof ml.Map>[0]);

    // Navigation & scale controls
    this.map.addControl(
      new ml.NavigationControl({ showCompass: true }),
      'bottom-right',
    );
    this.map.addControl(
      new ml.ScaleControl({ maxWidth: 100, unit: 'metric' }),
      'bottom-left',
    );

    // deck.gl interleaved overlay
    this.deckOverlay = new MapboxOverlay({
      interleaved: true,
      layers: [],
    });
    this.map.addControl(this.deckOverlay as unknown as import('maplibre-gl').IControl);

    // Resize handling
    this.resizeHandler = debounce(() => this.map?.resize(), 200);
    window.addEventListener('resize', this.resizeHandler);

    // Visibility handling — pause rendering when tab hidden
    this.visibilityHandler = () => {
      // MapLibre auto-pauses rendering when the canvas is not visible,
      // but we can avoid unnecessary deck.gl layer updates.
    };
    document.addEventListener('visibilitychange', this.visibilityHandler);

    // Re-render deck layers when the map moves (zoom-adaptive opacity)
    this.map.on('moveend', () => this.rebuildLayers());

    // Wait for the map style to fully load
    await new Promise<void>((resolve) => {
      this.map!.on('load', () => resolve());
    });
  }

  // -------------------------------------------------------------------------
  // Markers
  // -------------------------------------------------------------------------

  /**
   * Set markers with debounced flush (≤1 deck.gl update per 100 ms).
   * Callers may invoke this rapidly (e.g. on every WebSocket message).
   */
  setMarkers(markers: MapMarker[]): void {
    this.pendingMarkers = markers;

    if (!this.flushTimer) {
      this.flushTimer = setTimeout(() => {
        this.flushMarkers();
        this.flushTimer = null;
      }, 100);
    }
  }

  private flushMarkers(): void {
    if (!this.pendingMarkers) return;
    this.markers = this.pendingMarkers;
    this.pendingMarkers = null;
    this.rebuildLayers();
  }

  // -------------------------------------------------------------------------
  // Layer building
  // -------------------------------------------------------------------------

  /** Rebuild all deck.gl layers (markers + optional terminator) */
  private rebuildLayers(): void {
    if (!this.deckOverlay || !this.ScatterplotLayerCtor) return;

    const layers: InstanceType<typeof this.ScatterplotLayerCtor | typeof this.GeoJsonLayerCtor>[] = [];

    // --- Terminator overlay ---
    if (this.terminatorEnabled && this.GeoJsonLayerCtor) {
      const terminatorFeature = buildTerminatorGeoJSON(new Date());
      layers.push(
        new this.GeoJsonLayerCtor({
          id: 'terminator',
          // GeoJsonLayer accepts a single Feature — cast through unknown
          data: terminatorFeature as unknown as GeoJSON.Feature[],
          getFillColor: [0, 0, 30, 80],
          getLineColor: [100, 100, 180, 120],
          lineWidthMinPixels: 1,
          stroked: true,
          filled: true,
          pickable: false,
        }),
      );
    }

    // --- Marker scatterplot ---
    if (this.markers.length > 0) {
      const zoom = this.map?.getZoom() ?? 2;

      // Zoom-adaptive opacity: faint at world level, solid when zoomed in
      const opacity = Math.min(1, 0.3 + (zoom - 1) * 0.05);

      // Zoom-adaptive radius: smaller circles at low zoom to avoid overlap
      const radiusScale = Math.max(1, Math.min(10, zoom * 0.8));

      layers.push(
        new this.ScatterplotLayerCtor({
          id: 'markers-scatter',
          data: this.markers,
          getPosition: (d: MapMarker) => [d.lng, d.lat],
          getRadius: 4000 / radiusScale,
          getFillColor: (d: MapMarker) => getMarkerColor(d.kind),
          getLineColor: [255, 255, 255, 80],
          lineWidthMinPixels: 1,
          radiusMinPixels: 3,
          radiusMaxPixels: 15,
          radiusUnits: 'meters' as const,
          opacity,
          pickable: true,
          autoHighlight: true,
          highlightColor: [255, 255, 255, 80],
          onClick: (info: { object?: MapMarker }) => {
            if (info.object) {
              window.dispatchEvent(
                new CustomEvent('atlas:marker-click', { detail: info.object }),
              );
            }
          },
          onHover: (info: { object?: MapMarker; x?: number; y?: number }) => {
            if (this.container) {
              this.container.style.cursor = info.object ? 'pointer' : '';
            }
            if (info.object) {
              window.dispatchEvent(
                new CustomEvent('atlas:marker-hover', { detail: info.object }),
              );
            }
          },
          updateTriggers: {
            getPosition: this.markers.length,
            getFillColor: this.markers.length,
          },
        }),
      );
    }

    this.deckOverlay.setProps({ layers });
  }

  // -------------------------------------------------------------------------
  // Day/Night Terminator
  // -------------------------------------------------------------------------

  /** Enable the day/night terminator overlay, updated every 60 seconds */
  addTerminator(): void {
    this.terminatorEnabled = true;
    this.rebuildLayers();

    // Update terminator position every 60 seconds
    if (!this.terminatorTimer) {
      this.terminatorTimer = setInterval(() => {
        if (this.terminatorEnabled) {
          this.rebuildLayers();
        }
      }, 60_000);
    }
  }

  /** Disable the day/night terminator overlay */
  removeTerminator(): void {
    this.terminatorEnabled = false;

    if (this.terminatorTimer) {
      clearInterval(this.terminatorTimer);
      this.terminatorTimer = null;
    }

    this.rebuildLayers();
  }

  // -------------------------------------------------------------------------
  // Camera / Navigation
  // -------------------------------------------------------------------------

  /** Smoothly fly to coordinates with optional zoom level */
  flyTo(coords: Coordinates, zoom?: number): void {
    this.map?.flyTo({
      center: [coords.lng, coords.lat],
      zoom: zoom ?? 6,
      duration: 1500,
      essential: true,
    });
  }

  /** Instantly jump to coordinates (no animation) */
  jumpTo(coords: Coordinates, zoom?: number): void {
    this.map?.jumpTo({
      center: [coords.lng, coords.lat],
      zoom: zoom ?? this.map.getZoom(),
    });
  }

  /** Get the current map center */
  getCenter(): Coordinates {
    const center = this.map?.getCenter();
    return {
      lat: center?.lat ?? 0,
      lng: center?.lng ?? 0,
    };
  }

  /** Get the current zoom level */
  getZoom(): number {
    return this.map?.getZoom() ?? 2;
  }

  /** Get current map bounds as [sw, ne] */
  getBounds(): { sw: Coordinates; ne: Coordinates } | null {
    const b = this.map?.getBounds();
    if (!b) return null;
    return {
      sw: { lat: b.getSouth(), lng: b.getWest() },
      ne: { lat: b.getNorth(), lng: b.getEast() },
    };
  }

  // -------------------------------------------------------------------------
  // Style / Theme
  // -------------------------------------------------------------------------

  /** Switch tile provider and/or theme at runtime */
  setStyle(provider: TileProvider, theme: MapTheme): void {
    this.tileProvider = provider;
    this.theme = theme;
    const url = TILE_PROVIDERS[provider][theme];
    this.map?.setStyle(url);

    // After style change, re-add the deck overlay control
    // MapLibre removes controls when style changes — re-add after a tick
    this.map?.once('styledata', () => {
      this.rebuildLayers();
    });
  }

  /** Get current tile provider */
  getTileProvider(): TileProvider {
    return this.tileProvider;
  }

  /** Get current theme */
  getTheme(): MapTheme {
    return this.theme;
  }

  // -------------------------------------------------------------------------
  // Advanced — direct access
  // -------------------------------------------------------------------------

  /** Access the underlying MapLibre Map instance (escape hatch) */
  getMapInstance(): InstanceType<typeof import('maplibre-gl').Map> | null {
    return this.map;
  }

  /** Access the deck.gl MapboxOverlay (escape hatch for custom layers) */
  getDeckOverlay(): import('@deck.gl/mapbox').MapboxOverlay | null {
    return this.deckOverlay;
  }

  // -------------------------------------------------------------------------
  // Cleanup
  // -------------------------------------------------------------------------

  /** Tear down everything: timers, listeners, map, overlay */
  destroy(): void {
    // Clear pending flush timer
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }

    // Clear terminator timer
    if (this.terminatorTimer) {
      clearInterval(this.terminatorTimer);
      this.terminatorTimer = null;
    }

    // Remove global listeners
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
      this.resizeHandler = null;
    }

    if (this.visibilityHandler) {
      document.removeEventListener('visibilitychange', this.visibilityHandler);
      this.visibilityHandler = null;
    }

    // Destroy deck.gl overlay
    if (this.deckOverlay) {
      this.deckOverlay.finalize();
      this.deckOverlay = null;
    }

    // Destroy MapLibre map
    if (this.map) {
      this.map.remove();
      this.map = null;
    }

    // Clear cached constructors
    this.ScatterplotLayerCtor = null;
    this.GeoJsonLayerCtor = null;

    // Clear DOM
    this.markers = [];
    this.container.innerHTML = '';
  }
}

// ---------------------------------------------------------------------------
// Standalone helper (avoids `this` in hot-path data accessor)
// ---------------------------------------------------------------------------

function getMarkerColor(kind: MarkerKind | string): [number, number, number, number] {
  return MARKER_COLORS[kind] ?? DEFAULT_COLOR;
}
