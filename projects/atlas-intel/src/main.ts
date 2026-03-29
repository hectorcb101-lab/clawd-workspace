// ============================================================================
// Atlas Intel — Entry Point
// Wires together all panels, services, map, and DEFCON indicator.
// ============================================================================

import '@/styles/main.css';
import '@/styles/panels.css';
import '@/styles/map.css';
import { App } from '@/App';

// Import all panels
import { CIIPanel } from '@/components/CIIPanel';
import { NewsPanel } from '@/components/NewsPanel';
import { LiveNewsPanel } from '@/components/LiveNewsPanel';
import { InsightsPanel } from '@/components/InsightsPanel';
import { DeductionPanel } from '@/components/DeductionPanel';
import { StrategicPosturePanel } from '@/components/StrategicPosturePanel';
import { StrategicRiskPanel } from '@/components/StrategicRiskPanel';
import { MarketPanel } from '@/components/MarketPanel';
import { CommodityPanel } from '@/components/CommodityPanel';
import { EnergyPanel } from '@/components/EnergyPanel';
import { PredictionPanel } from '@/components/PredictionPanel';
import { LiveWebcamsPanel } from '@/components/LiveWebcamsPanel';
import { MonitorPanel } from '@/components/MonitorPanel';
import { CascadePanel } from '@/components/CascadePanel';
import { DisplacementPanel } from '@/components/DisplacementPanel';
import { ClimateAnomalyPanel } from '@/components/ClimateAnomalyPanel';
import { AirlineIntelPanel } from '@/components/AirlineIntelPanel';
import { CountryBriefPage } from '@/components/CountryBriefPage';
import { SettingsPanel } from '@/components/SettingsPanel';

// Import services for startup
import { dataBridge } from '@/services/data-bridge';
import '@/services/rss-feeds';
import { ciiEngine } from '@/services/cii-scoring';
import { signalEngine } from '@/services/signal-engine';
import '@/services/threat-classifier';
import { breakingNews } from '@/services/breaking-news';
import { ollama } from '@/services/ollama';
import { DefconIndicator } from '@/components/DefconIndicator';
import { MapContainer } from '@/components/MapContainer';
import { Panel } from '@/components/Panel';

import type { MapMarker, MarkerKind, NewsItem } from '@/types/index';

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (!root) throw new Error('Root element #app not found');

const app = new App(root);

// Create map container
const mapEl = app.getMapContainer();
const mapContainer = new MapContainer(mapEl);

// Register all panels with staggered positions
const panels: Panel[] = [
  new CIIPanel(),
  new NewsPanel(),
  new LiveNewsPanel(),
  new InsightsPanel(),
  new DeductionPanel(),
  new StrategicPosturePanel(),
  new StrategicRiskPanel(),
  new MarketPanel(),
  new CommodityPanel(),
  new EnergyPanel(),
  new PredictionPanel(),
  new LiveWebcamsPanel(),
  new MonitorPanel(),
  new CascadePanel(),
  new DisplacementPanel(),
  new ClimateAnomalyPanel(),
  new AirlineIntelPanel(),
  new SettingsPanel(),
];

panels.forEach((panel, i) => {
  // Stagger panel positions across a grid
  panel.setPosition(50 + (i % 4) * 320, 60 + Math.floor(i / 4) * 30);
  // Inject app reference into SettingsPanel
  if (panel instanceof SettingsPanel) {
    (panel as SettingsPanel).setApp(app);
  }
  app.registerPanel(panel);
});

// Country brief page (special — full screen overlay)
const countryBrief = new CountryBriefPage();
app.registerPanel(countryBrief);

// DEFCON indicator
const defcon = new DefconIndicator();

// ---------------------------------------------------------------------------
// Marker Store — central registry of markers by data source
// ---------------------------------------------------------------------------

const markerStore = new Map<string, MapMarker[]>();

/** Merge all source marker arrays and push to the map. */
function flushMarkersToMap(): void {
  const all: MapMarker[] = [];
  for (const markers of markerStore.values()) {
    all.push(...markers);
  }
  mapContainer.setMarkers(all);
}

// ---------------------------------------------------------------------------
// Source → MapMarker[] converters
// ---------------------------------------------------------------------------

/** Helper: safe numeric extraction. */
function num(v: unknown): number {
  return typeof v === 'number' ? v : 0;
}

/** Helper: safe ISO / epoch → ms timestamp. */
function toTs(v: unknown): number {
  if (typeof v === 'number') return v > 1e12 ? v : v * 1000;
  if (typeof v === 'string') return new Date(v).getTime() || Date.now();
  return Date.now();
}

/** Generic record type from JSON. */
type Rec = Record<string, unknown>;

/**
 * Convert raw JSON from a data source to MapMarker[].
 * Each source has a different envelope/shape.
 */
function convertToMarkers(source: string, raw: unknown): MapMarker[] {
  const data = raw as Rec;

  switch (source) {
    // — Vessels ---------------------------------------------------------------
    case 'vessels': {
      const vessels = (data.vessels ?? data) as Rec[];
      if (!Array.isArray(vessels)) return [];
      return vessels.map((v, i) => ({
        id: `vessel-${v.mmsi ?? i}`,
        lat: num(v.lat),
        lng: num(v.lon ?? v.lng),
        kind: 'vessel' as MarkerKind,
        label: (v.name as string) || `MMSI ${v.mmsi}`,
        timestamp: toTs(v.last_seen),
        data: v,
      }));
    }

    // — Flights ---------------------------------------------------------------
    case 'flights': {
      const aircraft = (data.aircraft ?? data) as Rec[];
      if (!Array.isArray(aircraft)) return [];
      return aircraft.map((a, i) => ({
        id: `flight-${a.icao24 ?? i}`,
        lat: num(a.lat),
        lng: num(a.lon ?? a.lng),
        kind: 'flight' as MarkerKind,
        label: (a.callsign as string) || (a.icao24 as string) || `Flight ${i}`,
        timestamp: toTs(data.lastUpdate),
        data: a,
      }));
    }

    // — Military --------------------------------------------------------------
    case 'military': {
      const markers: MapMarker[] = [];
      const vessels = (data.military_vessels ?? []) as Rec[];
      const aircraft = (data.military_aircraft ?? []) as Rec[];
      const groups = (data.naval_groups ?? []) as Rec[];

      for (const v of vessels) {
        markers.push({
          id: `mil-v-${v.mmsi ?? v.name}`,
          lat: num(v.lat),
          lng: num(v.lon ?? v.lng),
          kind: 'vessel' as MarkerKind,
          label: (v.name as string) || `MMSI ${v.mmsi}`,
          timestamp: toTs(data.lastUpdate),
          data: { ...v, military: true },
        });
      }

      for (const a of aircraft) {
        markers.push({
          id: `mil-a-${a.icao24 ?? a.callsign}`,
          lat: num(a.lat),
          lng: num(a.lon ?? a.lng),
          kind: 'flight' as MarkerKind,
          label: (a.callsign as string) || (a.icao24 as string) || 'Military Aircraft',
          timestamp: toTs(data.lastUpdate),
          data: { ...a, military: true },
        });
      }

      // Naval groups as cluster markers at their center position
      for (const g of groups) {
        markers.push({
          id: `mil-ng-${g.name}`,
          lat: num(g.center_lat),
          lng: num(g.center_lon),
          kind: 'vessel' as MarkerKind,
          label: (g.name as string) || 'Naval Group',
          timestamp: toTs(data.lastUpdate),
          data: { ...g, military: true, isGroup: true },
        });
      }

      return markers;
    }

    // — Earthquakes -----------------------------------------------------------
    case 'earthquakes': {
      const quakes = (data.earthquakes ?? data) as Rec[];
      if (!Array.isArray(quakes)) return [];
      return quakes.map((q) => ({
        id: `eq-${q.id ?? `${q.lat}-${q.lon}`}`,
        lat: num(q.lat),
        lng: num(q.lng ?? q.lon),
        kind: 'earthquake' as MarkerKind,
        label: `M${q.magnitude} — ${q.place ?? 'Unknown'}`,
        timestamp: toTs(q.time),
        data: q,
      }));
    }

    // — Cyber threats ---------------------------------------------------------
    case 'cyber': {
      const threats = (data.threats ?? data) as Rec[];
      if (!Array.isArray(threats)) return [];
      return threats.map((t, i) => ({
        id: `cyber-${t.ip ?? i}`,
        lat: num(t.lat),
        lng: num(t.lng ?? t.lon),
        kind: 'cyber' as MarkerKind,
        label: `${t.type} — ${t.country ?? 'Unknown'}`,
        timestamp: toTs(t.first_seen ?? t.last_seen),
        data: t,
      }));
    }

    // — Webcams ---------------------------------------------------------------
    case 'webcams': {
      const cams = (data.webcams ?? data) as Rec[];
      if (!Array.isArray(cams)) return [];
      return cams.map((c) => ({
        id: `webcam-${c.id}`,
        lat: num(c.lat),
        lng: num(c.lng ?? c.lon),  // webcams use 'lng' primarily
        kind: 'webcam' as MarkerKind,
        label: (c.title as string) || (c.city as string) || 'Webcam',
        timestamp: toTs(c.last_updated),
        data: c,
      }));
    }

    // — Wildfires -------------------------------------------------------------
    case 'wildfires': {
      const fires = (data.fires ?? data) as Rec[];
      if (!Array.isArray(fires)) return [];
      return fires.map((f, i) => ({
        id: `fire-${i}-${f.lat}-${f.lon}`,
        lat: num(f.lat),
        lng: num(f.lng ?? f.lon),
        kind: 'fire' as MarkerKind,
        label: (f.name as string) || `Fire (FRP ${f.frp})`,
        timestamp: toTs(f.detected),
        data: f,
      }));
    }

    // — Radiation -------------------------------------------------------------
    case 'radiation': {
      const stations = (data.stations ?? data) as Rec[];
      if (!Array.isArray(stations)) return [];
      return stations.map((s, i) => ({
        id: `rad-${i}-${s.lat}-${s.lon}`,
        lat: num(s.lat),
        lng: num(s.lng ?? s.lon),
        kind: 'radiation' as MarkerKind,
        label: `${s.location ?? 'Station'} — ${s.value}${s.unit ?? ''}`,
        timestamp: toTs(s.last_reading),
        data: s,
      }));
    }

    // — Unrest / protests -----------------------------------------------------
    case 'unrest': {
      const events = (data.events ?? data) as Rec[];
      if (!Array.isArray(events)) return [];
      return events.map((e, i) => ({
        id: `unrest-${i}-${e.lat}-${e.lon}`,
        lat: num(e.lat),
        lng: num(e.lng ?? e.lon),
        kind: 'protest' as MarkerKind,
        label: (e.title as string) || `${e.type} — ${e.country}`,
        timestamp: toTs(e.date),
        data: e,
      }));
    }

    // — Infrastructure --------------------------------------------------------
    case 'infrastructure': {
      const sites = (data.sites ?? data) as Rec[];
      if (!Array.isArray(sites)) return [];
      return sites.map((s) => ({
        id: `infra-${s.name}`,
        lat: num(s.lat),
        lng: num(s.lng ?? s.lon),
        kind: 'infrastructure' as MarkerKind,
        label: (s.name as string) || 'Infrastructure',
        timestamp: toTs(s.last_check),
        data: s,
      }));
    }

    // — GPS Jamming -----------------------------------------------------------
    case 'gps_jamming': {
      const zones = (data.zones ?? data) as Rec[];
      if (!Array.isArray(zones)) return [];
      return zones.map((z, i) => ({
        id: `gps-${i}-${z.region}`,
        lat: num(z.lat),
        lng: num(z.lng ?? z.lon),
        kind: 'gps-jam' as MarkerKind,
        label: `${z.region} — ${z.intensity}`,
        timestamp: toTs(z.last_detected),
        data: z,
      }));
    }

    // — Satellites ------------------------------------------------------------
    case 'satellites': {
      const sats = (data.satellites ?? data) as Rec[];
      if (!Array.isArray(sats)) return [];
      return sats.map((s) => ({
        id: `sat-${s.norad_id ?? s.name}`,
        lat: num(s.lat),
        lng: num(s.lon),  // satellites use 'lon' only
        kind: 'satellite' as MarkerKind,
        label: (s.name as string) || `NORAD ${s.norad_id}`,
        timestamp: toTs(data.lastUpdate),
        data: s,
      }));
    }

    default:
      return [];
  }
}

// ---------------------------------------------------------------------------
// Initialize
// ---------------------------------------------------------------------------

async function init(): Promise<void> {
  // Discover AI capabilities
  const ollamaAvailable = await ollama.discover().catch(() => false);
  
  // Set AI status dot based on Ollama availability
  // Green if available, amber (warning) if not — never red on init
  app.setStatusDot('ai', ollamaAvailable ? 'online' : 'warning');

  // Initialize map (3D by default)
  await mapContainer.init(app.getSettings().mapEngine);

  // Start data bridge polling
  dataBridge.startAll();

  // Request notification permission for breaking news
  breakingNews.requestPermission();

  // -------------------------------------------------------------------------
  // Wire map-bound data sources → marker store → mapContainer.setMarkers()
  // -------------------------------------------------------------------------

  const MAP_SOURCES = [
    'vessels', 'flights', 'military', 'earthquakes', 'cyber',
    'webcams', 'wildfires', 'radiation', 'unrest',
    'infrastructure', 'gps_jamming', 'satellites',
  ] as const;

  for (const source of MAP_SOURCES) {
    dataBridge.on(source, (raw) => {
      try {
        const markers = convertToMarkers(source, raw);
        markerStore.set(source, markers);
        flushMarkersToMap();
      } catch (err) {
        console.error(`[Atlas] Failed to convert "${source}" to markers:`, err);
      }
    });
  }

  // -------------------------------------------------------------------------
  // Wire news data → CII, signals, breaking news, and open panels
  // -------------------------------------------------------------------------

  dataBridge.on('news', (data) => {
    const raw = data as Rec;
    const articles = (raw.geolocated_articles ?? raw.articles ?? data) as Rec[];
    if (!Array.isArray(articles)) return;

    // Feed analytical engines
    ciiEngine.update(articles as unknown as NewsItem[]);
    signalEngine.analyze(articles as unknown as NewsItem[]);
    breakingNews.check(articles as unknown as NewsItem[]);

    // Refresh any news-related panels that are open
    for (const panel of app.getAllPanels()) {
      if (panel.isOpen) {
        const id = panel.config.id;
        if (
          id === 'news' || id === 'insights' || id === 'cii' ||
          id === 'live-news' || id === 'deduction' || id === 'strategic-risk'
        ) {
          panel.refresh();
        }
      }
    }
  });

  // -------------------------------------------------------------------------
  // Wire alerts to DEFCON indicator
  // -------------------------------------------------------------------------

  dataBridge.on('alerts', () => {
    defcon.refresh();
  });

  // -------------------------------------------------------------------------
  // DOM event listeners
  // -------------------------------------------------------------------------

  // Listen for country clicks on the map
  window.addEventListener('atlas:country-click', ((e: CustomEvent) => {
    countryBrief.show(e.detail.code);
  }) as EventListener);

  // Listen for breaking news events
  window.addEventListener('atlas:breaking', ((e: CustomEvent) => {
    app.showBreakingBanner(e.detail);
  }) as EventListener);

  // -------------------------------------------------------------------------
  // Periodic refresh cycle (every 60s)
  // -------------------------------------------------------------------------

  setInterval(() => {
    defcon.refresh();

    for (const panel of app.getAllPanels()) {
      if (panel.isOpen) panel.refresh();
    }
  }, 60_000);

  // Start the app (sets MAP dot to online, refreshes panels)
  await app.start();

  console.log('[Atlas Intel] Initialized — all systems operational');
}

init().catch(console.error);

// ---------------------------------------------------------------------------
// Panel picker
// ---------------------------------------------------------------------------

const addPanelBtn = document.querySelector('.add-panel-btn');
if (addPanelBtn) {
  addPanelBtn.addEventListener('click', () => {
    showPanelPicker(panels);
  });
}

function showPanelPicker(allPanels: Panel[]): void {
  // Remove any existing picker
  document.querySelector('.panel-picker')?.remove();

  const backdrop = document.createElement('div');
  backdrop.className = 'panel-picker';

  const box = document.createElement('div');
  box.className = 'picker-box';

  const title = document.createElement('h3');
  title.textContent = 'Open Panel';
  title.style.cssText = 'margin:0 0 12px;font-size:13px;letter-spacing:1px;color:var(--accent)';
  box.appendChild(title);

  for (const panel of allPanels) {
    const row = document.createElement('div');
    row.className = 'picker-item';
    row.textContent = `${panel.config.icon} ${panel.config.title}`;
    row.style.cssText =
      'padding:6px 10px;cursor:pointer;border-radius:4px;font-size:12px;'
      + 'transition:background 0.15s';
    row.addEventListener('mouseenter', () => {
      row.style.background = 'rgba(255,255,255,0.05)';
    });
    row.addEventListener('mouseleave', () => {
      row.style.background = '';
    });
    row.addEventListener('click', () => {
      panel.toggle();
      backdrop.remove();
    });
    box.appendChild(row);
  }

  backdrop.appendChild(box);

  // Close on backdrop click
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) backdrop.remove();
  });

  document.body.appendChild(backdrop);
}

// ---------------------------------------------------------------------------
// HMR (Vite)
// ---------------------------------------------------------------------------

if (import.meta.hot) {
  import.meta.hot.accept();
}

// ---------------------------------------------------------------------------
// Debug handle — accessible via __atlas in the browser console
// ---------------------------------------------------------------------------

((window as unknown) as Record<string, unknown>).__atlas = { app, mapContainer, defcon };
