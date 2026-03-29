// ============================================================================
// Atlas Intel — MapContainer
// Orchestrates 2D/3D map engine switching, layers, time filters, regions,
// marker popups, and auto-center on first load.
// ============================================================================

import type {
  MapEngine,
  MapMarker,
  Coordinates,
  TimeRange,
  RegionName,
  LayerCategory,
  MarkerKind,
} from '@/types/index';
import { h, timeAgo } from '@/utils/dom-utils';
import { GlobeMap } from '@/components/GlobeMap';
import { FlatMap } from '@/components/FlatMap';
import { MAP_LAYERS, DEFAULT_ENABLED_LAYERS } from '@/config/map-layer-definitions';

// ---------------------------------------------------------------------------
// Regional Presets
// ---------------------------------------------------------------------------

const REGIONAL_PRESETS: Record<RegionName, Coordinates & { zoom: number }> = {
  global:           { lat: 20,  lng: 0,    alt: 2.5, zoom: 2 },
  americas:         { lat: 20,  lng: -90,  alt: 1.5, zoom: 3 },
  europe:           { lat: 50,  lng: 15,   alt: 1.2, zoom: 4 },
  mena:             { lat: 28,  lng: 42,   alt: 1.2, zoom: 4 },
  asia:             { lat: 30,  lng: 105,  alt: 1.5, zoom: 3 },
  africa:           { lat: 5,   lng: 20,   alt: 1.5, zoom: 3 },
  oceania:          { lat: -25, lng: 140,  alt: 1.5, zoom: 3 },
  'latin-america':  { lat: -10, lng: -55,  alt: 1.5, zoom: 3 },
};

// ---------------------------------------------------------------------------
// Time range durations (ms)
// ---------------------------------------------------------------------------

const TIME_RANGE_MS: Record<TimeRange, number> = {
  '1h':  3_600_000,
  '6h':  21_600_000,
  '24h': 86_400_000,
  '48h': 172_800_000,
  '7d':  604_800_000,
};

// ---------------------------------------------------------------------------
// Time range labels for buttons
// ---------------------------------------------------------------------------

const TIME_RANGES: TimeRange[] = ['1h', '6h', '24h', '48h', '7d'];

// ---------------------------------------------------------------------------
// Region names for buttons
// ---------------------------------------------------------------------------

const REGION_NAMES: { key: RegionName; label: string }[] = [
  { key: 'global',         label: 'Global' },
  { key: 'americas',       label: 'Americas' },
  { key: 'europe',         label: 'Europe' },
  { key: 'mena',           label: 'MENA' },
  { key: 'asia',           label: 'Asia' },
  { key: 'africa',         label: 'Africa' },
  { key: 'oceania',        label: 'Oceania' },
  { key: 'latin-america',  label: 'LatAm' },
];

// ---------------------------------------------------------------------------
// Timezone → region mapping for auto-center
// ---------------------------------------------------------------------------

const TZ_REGION_MAP: Record<string, RegionName> = {
  'America/New_York':       'americas',
  'America/Chicago':        'americas',
  'America/Denver':         'americas',
  'America/Los_Angeles':    'americas',
  'America/Toronto':        'americas',
  'America/Vancouver':      'americas',
  'America/Mexico_City':    'latin-america',
  'America/Bogota':         'latin-america',
  'America/Lima':           'latin-america',
  'America/Santiago':       'latin-america',
  'America/Buenos_Aires':   'latin-america',
  'America/Sao_Paulo':      'latin-america',
  'Europe/London':          'europe',
  'Europe/Paris':           'europe',
  'Europe/Berlin':          'europe',
  'Europe/Rome':            'europe',
  'Europe/Madrid':          'europe',
  'Europe/Moscow':          'europe',
  'Europe/Warsaw':          'europe',
  'Europe/Istanbul':        'mena',
  'Asia/Dubai':             'mena',
  'Asia/Riyadh':            'mena',
  'Asia/Tehran':            'mena',
  'Africa/Cairo':           'mena',
  'Asia/Jerusalem':         'mena',
  'Asia/Kolkata':           'asia',
  'Asia/Shanghai':          'asia',
  'Asia/Tokyo':             'asia',
  'Asia/Seoul':             'asia',
  'Asia/Singapore':         'asia',
  'Asia/Hong_Kong':         'asia',
  'Asia/Bangkok':           'asia',
  'Asia/Jakarta':           'asia',
  'Africa/Lagos':           'africa',
  'Africa/Nairobi':         'africa',
  'Africa/Johannesburg':    'africa',
  'Africa/Casablanca':      'africa',
  'Australia/Sydney':       'oceania',
  'Australia/Melbourne':    'oceania',
  'Australia/Perth':        'oceania',
  'Pacific/Auckland':       'oceania',
};

// ---------------------------------------------------------------------------
// Layer categories order for sidebar
// ---------------------------------------------------------------------------

const CATEGORY_ORDER: { key: LayerCategory; label: string }[] = [
  { key: 'military',       label: 'Military' },
  { key: 'maritime',       label: 'Maritime' },
  { key: 'aviation',       label: 'Aviation' },
  { key: 'seismic',        label: 'Seismic' },
  { key: 'cyber',          label: 'Cyber' },
  { key: 'civil',          label: 'Civil' },
  { key: 'infrastructure', label: 'Infrastructure' },
  { key: 'environmental',  label: 'Environmental' },
  { key: 'economic',       label: 'Economic' },
  { key: 'nuclear',        label: 'Nuclear' },
  { key: 'space',          label: 'Space' },
];

// ---------------------------------------------------------------------------
// Marker kind → human-readable label
// ---------------------------------------------------------------------------

const KIND_LABELS: Record<MarkerKind, string> = {
  vessel:         'Vessel',
  flight:         'Flight',
  earthquake:     'Earthquake',
  fire:           'Fire',
  cyber:          'Cyber Event',
  protest:        'Protest',
  radiation:      'Radiation',
  base:           'Military Base',
  nuclear:        'Nuclear Site',
  webcam:         'Webcam',
  infrastructure: 'Infrastructure',
  'gps-jam':      'GPS Jamming',
  satellite:      'Satellite',
  chokepoint:     'Chokepoint',
  cable:          'Subsea Cable',
  pipeline:       'Pipeline',
  'trade-route':  'Trade Route',
};

// ============================================================================
// MapContainer class
// ============================================================================

export class MapContainer {
  private container: HTMLElement;
  private mapWrapper: HTMLElement;
  private globe: GlobeMap | null = null;
  private flatMap: FlatMap | null = null;
  private engine: MapEngine = '3d';
  private markers: MapMarker[] = [];
  private enabledLayers: Set<string>;
  private layerSidebar: HTMLElement | null = null;
  private layerSidebarOpen = false;
  private timeRange: TimeRange = '24h';
  private activeRegion: RegionName = 'global';
  private activePopup: HTMLElement | null = null;
  private coordsOverlay: HTMLElement | null = null;
  private markerClickHandler: ((e: Event) => void) | null = null;
  private countryClickHandler: ((e: Event) => void) | null = null;

  // Button references for active-state management
  private timeButtons: Map<TimeRange, HTMLElement> = new Map();
  private regionButtons: Map<RegionName, HTMLElement> = new Map();
  private engineButtons: { btn3d: HTMLElement | null; btn2d: HTMLElement | null } = {
    btn3d: null,
    btn2d: null,
  };

  constructor(container: HTMLElement) {
    this.container = container;
    this.enabledLayers = new Set(DEFAULT_ENABLED_LAYERS);
    this.mapWrapper = h('div', {
      class: 'globe-container',
      style: 'width:100%;height:100%;position:relative',
    });
    this.container.appendChild(this.mapWrapper);
    this.buildControls();
    this.setupEventListeners();
  }

  // =========================================================================
  // Controls — build all UI overlays
  // =========================================================================

  private buildControls(): void {
    // ── 1. 2D/3D toggle (top right) ──────────────────────────────────────
    const btn3d = h('button', {
      class: 'active',
      onClick: () => this.switchEngine('3d'),
    }, '3D');
    const btn2d = h('button', {
      onClick: () => this.switchEngine('2d'),
    }, '2D');

    this.engineButtons.btn3d = btn3d;
    this.engineButtons.btn2d = btn2d;

    const toggle = h('div', { class: 'map-toggle' }, btn3d, btn2d);
    this.container.appendChild(toggle);

    // ── 2. Layer toggle button (top left) ────────────────────────────────
    const layerBtn = h('button', {
      class: 'layer-toggle-btn',
      title: 'Toggle layers',
      onClick: () => this.toggleLayerSidebar(),
    }, '☰');
    this.container.appendChild(layerBtn);

    // ── 3. Layer sidebar ─────────────────────────────────────────────────
    this.layerSidebar = this.buildLayerSidebar();
    this.container.appendChild(this.layerSidebar);

    // ── 4. Time filter buttons (top center) ──────────────────────────────
    const timeFilter = h('div', { class: 'time-filter' });

    for (const range of TIME_RANGES) {
      const btn = h('button', {
        class: range === this.timeRange ? 'active' : '',
        onClick: () => this.setTimeRange(range),
      }, range.toUpperCase());
      this.timeButtons.set(range, btn);
      timeFilter.appendChild(btn);
    }

    this.container.appendChild(timeFilter);

    // ── 5. Regional preset buttons (bottom center) ───────────────────────
    const regionBar = h('div', { class: 'region-presets' });

    for (const { key, label } of REGION_NAMES) {
      const btn = h('button', {
        class: key === this.activeRegion ? 'active' : '',
        onClick: () => this.flyToRegion(key),
      }, label);
      this.regionButtons.set(key, btn);
      regionBar.appendChild(btn);
    }

    this.container.appendChild(regionBar);

    // ── 6. Coordinates overlay (top left, below layer btn) ───────────────
    this.coordsOverlay = h('div', {
      class: 'coordinates-overlay',
      style: 'top:52px;left:12px',
    }, '0.0000°N  0.0000°E');
    this.container.appendChild(this.coordsOverlay);
  }

  // =========================================================================
  // Layer Sidebar
  // =========================================================================

  private buildLayerSidebar(): HTMLElement {
    const sidebar = h('div', { class: 'layer-sidebar' });

    // Search / filter input
    const searchInput = h('input', {
      class: 'search-input',
      type: 'text',
      placeholder: 'Filter layers…',
    }) as HTMLInputElement;

    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase();
      const items = sidebar.querySelectorAll('.layer-item') as NodeListOf<HTMLElement>;
      const headers = sidebar.querySelectorAll('[data-category-header]') as NodeListOf<HTMLElement>;

      // Show/hide items based on query
      for (const item of items) {
        const name = item.dataset.layerName || '';
        item.style.display = name.includes(query) ? '' : 'none';
      }

      // Show/hide category headers: show if any child item is visible
      for (const header of headers) {
        const cat = header.dataset.categoryHeader!;
        const catItems = sidebar.querySelectorAll(
          `.layer-item[data-category="${cat}"]`,
        ) as NodeListOf<HTMLElement>;
        const anyVisible = Array.from(catItems).some((i) => i.style.display !== 'none');
        header.style.display = anyVisible ? '' : 'none';
      }
    });

    sidebar.appendChild(searchInput);

    // Group layers by category
    for (const { key: category, label } of CATEGORY_ORDER) {
      const categoryLayers = MAP_LAYERS.filter((l) => l.category === category);
      if (categoryLayers.length === 0) continue;

      // Category header
      const header = h('div', {
        'data-category-header': category,
        style:
          'padding:8px 12px 4px;font-size:0.55rem;letter-spacing:0.12em;' +
          'color:var(--accent-dim);text-transform:uppercase;border-bottom:1px solid var(--border)',
      }, label);
      sidebar.appendChild(header);

      // Layer items
      for (const layer of categoryLayers) {
        const isEnabled = this.enabledLayers.has(layer.id);

        const checkbox = h('input', {
          type: 'checkbox',
          ...(isEnabled ? { checked: true } : {}),
        }) as HTMLInputElement;
        if (isEnabled) checkbox.checked = true;

        const item = h('div', {
          class: `layer-item${isEnabled ? ' active' : ''}`,
          'data-layer-id': layer.id,
          'data-layer-name': layer.name.toLowerCase(),
          'data-category': category,
          onClick: () => {
            this.toggleLayer(layer.id);
            const nowEnabled = this.enabledLayers.has(layer.id);
            checkbox.checked = nowEnabled;
            if (nowEnabled) {
              item.classList.add('active');
            } else {
              item.classList.remove('active');
            }
          },
        },
          checkbox,
          h('span', null, layer.icon),
          h('span', null, layer.name),
        );

        sidebar.appendChild(item);
      }
    }

    return sidebar;
  }

  /** Toggle layer sidebar open/closed */
  toggleLayerSidebar(): void {
    this.layerSidebarOpen = !this.layerSidebarOpen;

    if (this.layerSidebar) {
      if (this.layerSidebarOpen) {
        this.layerSidebar.classList.add('open');
      } else {
        this.layerSidebar.classList.remove('open');
      }
    }
  }

  // =========================================================================
  // Event Listeners — marker click popup, country click, coordinates tracking
  // =========================================================================

  private setupEventListeners(): void {
    // ── Marker click → inspect popup ─────────────────────────────────────
    this.markerClickHandler = (e: Event) => {
      const marker = (e as CustomEvent<MapMarker>).detail;
      if (!marker) return;
      this.showMarkerPopup(marker);
    };
    window.addEventListener('atlas:marker-click', this.markerClickHandler);

    // ── Country click → dispatch atlas:country-click ─────────────────────
    // The FlatMap's MapLibre instance fires click events on the map.
    // We listen for them and resolve country from the click position.
    this.countryClickHandler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.country) {
        window.dispatchEvent(
          new CustomEvent('atlas:country-click', {
            detail: { country: detail.country, coords: detail.coords },
          }),
        );
      }
    };
    window.addEventListener('atlas:map-click', this.countryClickHandler);

    // ── Track mouse/camera position for coordinates overlay ──────────────
    this.container.addEventListener('mousemove', (e: MouseEvent) => {
      this.updateCoordsFromMouse(e);
    });

    // ── Close popup on Escape ────────────────────────────────────────────
    window.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        this.closePopup();
      }
    });
  }

  // =========================================================================
  // Initialization
  // =========================================================================

  async init(engine?: MapEngine): Promise<void> {
    if (engine) this.engine = engine;

    // Update toggle button state
    this.updateEngineButtons();

    if (this.engine === '3d') {
      this.globe = new GlobeMap(this.mapWrapper);
      await this.globe.init();
    } else {
      this.flatMap = new FlatMap(this.mapWrapper);
      await this.flatMap.init();
    }

    // Auto-center based on user timezone
    this.autoCenterOnTimezone();

    this.updateMarkers();

    // Setup map click handler for country detection (2D only)
    this.setupMapClickHandler();
  }

  // =========================================================================
  // Auto-center on first load based on browser timezone
  // =========================================================================

  private autoCenterOnTimezone(): void {
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;

      // Direct match
      if (tz && TZ_REGION_MAP[tz]) {
        const region = TZ_REGION_MAP[tz];
        this.flyToRegion(region);
        return;
      }

      // Prefix match: try the continent portion
      if (tz) {
        const prefix = tz.split('/')[0];
        if (prefix === 'America') {
          this.flyToRegion('americas');
          return;
        }
        if (prefix === 'Europe') {
          this.flyToRegion('europe');
          return;
        }
        if (prefix === 'Asia') {
          this.flyToRegion('asia');
          return;
        }
        if (prefix === 'Africa') {
          this.flyToRegion('africa');
          return;
        }
        if (prefix === 'Australia' || prefix === 'Pacific') {
          this.flyToRegion('oceania');
          return;
        }
      }
    } catch {
      // Intl not available — fall through to global
    }

    // Default: global
    this.flyToRegion('global');
  }

  // =========================================================================
  // Map click handler — country resolution for 2D mode
  // =========================================================================

  private setupMapClickHandler(): void {
    if (!this.flatMap) return;

    const mapInstance = this.flatMap.getMapInstance();
    if (!mapInstance) return;

    mapInstance.on('click', (e) => {
      // Check if the click was on a country fill layer
      const features = mapInstance.queryRenderedFeatures(e.point);
      if (features && features.length > 0) {
        // Look for a country-like feature (admin boundary or fill layer)
        for (const feature of features) {
          const props = feature.properties;
          if (!props) continue;

          // Common property names for country in various tile sets
          const country =
            props['name'] ||
            props['NAME'] ||
            props['name_en'] ||
            props['NAME_EN'] ||
            props['admin'] ||
            props['ADMIN'] ||
            props['iso_a2'] ||
            props['ISO_A2'] ||
            null;

          if (country && typeof country === 'string') {
            window.dispatchEvent(
              new CustomEvent('atlas:country-click', {
                detail: {
                  country,
                  coords: { lat: e.lngLat.lat, lng: e.lngLat.lng },
                },
              }),
            );
            break;
          }
        }
      }
    });
  }

  // =========================================================================
  // Engine switching (2D ↔ 3D)
  // =========================================================================

  async switchEngine(engine: MapEngine): Promise<void> {
    if (engine === this.engine) return;

    // Save current view state
    const coords = this.getCenter();

    // Destroy current engine
    this.destroyCurrentEngine();
    this.engine = engine;

    // Update toggle buttons
    this.updateEngineButtons();

    // Init new engine and restore view
    if (engine === '3d') {
      this.globe = new GlobeMap(this.mapWrapper);
      await this.globe.init();
      this.globe.flyTo(coords);
    } else {
      this.flatMap = new FlatMap(this.mapWrapper);
      await this.flatMap.init();
      this.flatMap.flyTo(coords);
      this.setupMapClickHandler();
    }

    this.updateMarkers();

    // Close any open popup on engine switch
    this.closePopup();

    window.dispatchEvent(
      new CustomEvent('atlas:engine-changed', { detail: engine }),
    );
  }

  private updateEngineButtons(): void {
    const { btn3d, btn2d } = this.engineButtons;
    if (btn3d) {
      if (this.engine === '3d') {
        btn3d.classList.add('active');
      } else {
        btn3d.classList.remove('active');
      }
    }
    if (btn2d) {
      if (this.engine === '2d') {
        btn2d.classList.add('active');
      } else {
        btn2d.classList.remove('active');
      }
    }
  }

  // =========================================================================
  // Markers
  // =========================================================================

  /** Set all markers (from data feeds) */
  setMarkers(markers: MapMarker[]): void {
    this.markers = markers;
    this.updateMarkers();
  }

  private updateMarkers(): void {
    const cutoff = this.getTimeCutoff();

    const filtered = this.markers.filter((m) => {
      // Check if marker's kind matches an enabled layer
      const layer = MAP_LAYERS.find((l) => l.markerKind === m.kind);
      if (layer && !this.enabledLayers.has(layer.id)) return false;

      // Check time range
      if (m.timestamp) {
        if (m.timestamp < cutoff) return false;
      }

      return true;
    });

    if (this.globe) this.globe.setMarkers(filtered);
    if (this.flatMap) this.flatMap.setMarkers(filtered);
  }

  private getTimeCutoff(): number {
    return Date.now() - (TIME_RANGE_MS[this.timeRange] || 86_400_000);
  }

  // =========================================================================
  // Layers
  // =========================================================================

  /** Toggle a layer on/off */
  toggleLayer(layerId: string): void {
    if (this.enabledLayers.has(layerId)) {
      this.enabledLayers.delete(layerId);
    } else {
      this.enabledLayers.add(layerId);
    }
    this.updateMarkers();

    window.dispatchEvent(
      new CustomEvent('atlas:layer-toggled', {
        detail: { layerId, enabled: this.enabledLayers.has(layerId) },
      }),
    );
  }

  /** Get enabled layer IDs */
  getEnabledLayers(): string[] {
    return Array.from(this.enabledLayers);
  }

  // =========================================================================
  // Time Range
  // =========================================================================

  /** Set the active time range and update markers */
  setTimeRange(range: TimeRange): void {
    this.timeRange = range;

    // Update button active states
    for (const [r, btn] of this.timeButtons) {
      if (r === range) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }

    this.updateMarkers();

    window.dispatchEvent(
      new CustomEvent('atlas:time-range-changed', { detail: range }),
    );
  }

  // =========================================================================
  // Navigation
  // =========================================================================

  /** Fly to coordinates */
  flyTo(coords: Coordinates, zoom?: number): void {
    if (this.globe) this.globe.flyTo(coords);
    if (this.flatMap) this.flatMap.flyTo(coords, zoom);
  }

  /** Get current center coordinates */
  getCenter(): Coordinates {
    if (this.globe) return this.globe.getPointOfView();
    if (this.flatMap) return this.flatMap.getCenter();
    return { lat: 20, lng: 0, alt: 2.5 };
  }

  /** Fly to a regional preset */
  flyToRegion(region: RegionName): void {
    const preset = REGIONAL_PRESETS[region];
    if (!preset) return;

    this.activeRegion = region;

    // Update button active states
    for (const [r, btn] of this.regionButtons) {
      if (r === region) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }

    if (this.globe) {
      this.globe.flyTo({ lat: preset.lat, lng: preset.lng, alt: preset.alt });
    }
    if (this.flatMap) {
      this.flatMap.flyTo({ lat: preset.lat, lng: preset.lng }, preset.zoom);
    }

    window.dispatchEvent(
      new CustomEvent('atlas:region-changed', { detail: region }),
    );
  }

  /** Get current engine */
  getEngine(): MapEngine {
    return this.engine;
  }

  /** Access underlying GlobeMap instance */
  getGlobe(): GlobeMap | null {
    return this.globe;
  }

  /** Access underlying FlatMap instance */
  getFlatMap(): FlatMap | null {
    return this.flatMap;
  }

  // =========================================================================
  // Marker Inspect Popup
  // =========================================================================

  private showMarkerPopup(marker: MapMarker): void {
    // Close any existing popup
    this.closePopup();

    // Build popup content
    const kindLabel = KIND_LABELS[marker.kind] || marker.kind;
    const timestampStr = marker.timestamp ? timeAgo(marker.timestamp) : '—';

    // Title row
    const titleEl = h('div', { class: 'popup-title' },
      `${kindLabel}${marker.label ? ': ' + marker.label : ''}`,
    );

    // Row helper
    const row = (label: string, value: string) =>
      h('div', { class: 'popup-row' },
        h('span', { class: 'popup-label' }, label),
        h('span', null, value),
      );

    // Build data rows
    const rows: HTMLElement[] = [
      row('ID', marker.id),
      row('Position', `${marker.lat.toFixed(4)}°, ${marker.lng.toFixed(4)}°`),
      row('Type', kindLabel),
      row('Time', timestampStr),
    ];

    // Add extra data fields if present
    if (marker.data) {
      for (const [key, value] of Object.entries(marker.data)) {
        if (value != null) {
          rows.push(row(key, String(value)));
        }
      }
    }

    // Close button
    const closeBtn = h('button', {
      style:
        'position:absolute;top:4px;right:6px;background:none;border:none;' +
        'color:var(--text-secondary);font-size:1rem;cursor:pointer;line-height:1',
      onClick: () => this.closePopup(),
    }, '×');

    // Assemble popup
    const popup = h('div', { class: 'marker-popup' },
      closeBtn,
      titleEl,
      ...rows,
    );

    // Position the popup relative to the container
    // We place it near the top-center of the map, offset slightly
    // For precise positioning we'd need screen coords from the engine;
    // for now, we use a fixed position strategy that works with both engines.
    this.positionPopup(popup, marker);

    this.container.appendChild(popup);
    this.activePopup = popup;
  }

  private positionPopup(popup: HTMLElement, marker: MapMarker): void {
    // Try to get screen-space position from the map engine
    if (this.flatMap) {
      const mapInstance = this.flatMap.getMapInstance();
      if (mapInstance) {
        const point = mapInstance.project([marker.lng, marker.lat]);
        popup.style.left = `${Math.min(point.x, this.container.clientWidth - 340)}px`;
        popup.style.top = `${Math.max(10, point.y - 120)}px`;
        return;
      }
    }

    // For 3D globe or fallback: position at a fixed spot near top-right
    popup.style.right = '60px';
    popup.style.top = '60px';
    popup.style.left = 'auto';
  }

  private closePopup(): void {
    if (this.activePopup) {
      this.activePopup.remove();
      this.activePopup = null;
    }
  }

  // =========================================================================
  // Coordinates Overlay — update from mouse position
  // =========================================================================

  private updateCoordsFromMouse(e: MouseEvent): void {
    if (!this.coordsOverlay) return;

    if (this.flatMap) {
      const mapInstance = this.flatMap.getMapInstance();
      if (mapInstance) {
        const rect = this.mapWrapper.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Only update if mouse is within the map wrapper
        if (x >= 0 && y >= 0 && x <= rect.width && y <= rect.height) {
          const lngLat = mapInstance.unproject([x, y]);
          this.coordsOverlay.textContent = formatCoords(lngLat.lat, lngLat.lng);
        }
        return;
      }
    }

    if (this.globe) {
      // For the globe, show the current camera center
      const pov = this.globe.getPointOfView();
      this.coordsOverlay.textContent = formatCoords(pov.lat, pov.lng);
    }
  }

  // =========================================================================
  // Destroy
  // =========================================================================

  private destroyCurrentEngine(): void {
    if (this.globe) {
      this.globe.destroy();
      this.globe = null;
    }
    if (this.flatMap) {
      this.flatMap.destroy();
      this.flatMap = null;
    }

    // Clear the map wrapper DOM (the engines append to it)
    this.mapWrapper.innerHTML = '';
  }

  /** Full teardown — call when the MapContainer is removed from the DOM */
  destroy(): void {
    // Remove event listeners
    if (this.markerClickHandler) {
      window.removeEventListener('atlas:marker-click', this.markerClickHandler);
      this.markerClickHandler = null;
    }
    if (this.countryClickHandler) {
      window.removeEventListener('atlas:map-click', this.countryClickHandler);
      this.countryClickHandler = null;
    }

    // Close popup
    this.closePopup();

    // Destroy engines
    this.destroyCurrentEngine();

    // Clear all button references
    this.timeButtons.clear();
    this.regionButtons.clear();
    this.engineButtons = { btn3d: null, btn2d: null };

    // Clear DOM
    this.container.innerHTML = '';
  }
}

// ===========================================================================
// Standalone helpers
// ===========================================================================

/** Format lat/lng to a compact display string */
function formatCoords(lat: number, lng: number): string {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}°${latDir}  ${Math.abs(lng).toFixed(4)}°${lngDir}`;
}
