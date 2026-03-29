// ============================================================================
// Atlas Intel — Map Layer Definitions
// ============================================================================

import type { LayerCategory, LayerDefinition } from '@/types/index';

// ---------------------------------------------------------------------------
// All layer definitions (45+)
// ---------------------------------------------------------------------------

export const MAP_LAYERS: LayerDefinition[] = [
  // ── Military ─────────────────────────────────────────────────────────────
  {
    id: 'conflicts',
    name: 'Active Conflicts',
    icon: '⚔️',
    category: 'military',
    defaultEnabled: true,
    dataSource: 'acled',
    refreshInterval: 300_000,
  },
  {
    id: 'military-flights',
    name: 'Military Flights',
    icon: '🛩️',
    category: 'military',
    defaultEnabled: true,
    markerKind: 'flight',
    dataSource: 'adsb-mil',
    refreshInterval: 30_000,
  },
  {
    id: 'military-bases',
    name: 'Military Bases',
    icon: '🏛️',
    category: 'military',
    defaultEnabled: false,
    markerKind: 'base',
    dataSource: 'static-bases',
  },
  {
    id: 'military-vessels',
    name: 'Military Vessels',
    icon: '🚢',
    category: 'military',
    defaultEnabled: true,
    markerKind: 'vessel',
    dataSource: 'ais-mil',
    refreshInterval: 60_000,
  },
  {
    id: 'military-callsigns',
    name: 'Military Callsigns',
    icon: '📡',
    category: 'military',
    defaultEnabled: false,
    dataSource: 'adsb-mil',
    refreshInterval: 30_000,
  },

  // ── Maritime ─────────────────────────────────────────────────────────────
  {
    id: 'vessels',
    name: 'Vessel Traffic',
    icon: '🚢',
    category: 'maritime',
    defaultEnabled: false,
    markerKind: 'vessel',
    dataSource: 'ais-exchange',
    refreshInterval: 60_000,
  },
  {
    id: 'naval-activity',
    name: 'Naval Activity',
    icon: '⚓',
    category: 'maritime',
    defaultEnabled: true,
    markerKind: 'vessel',
    dataSource: 'ais-mil',
    refreshInterval: 60_000,
  },
  {
    id: 'shipping-lanes',
    name: 'Shipping Lanes',
    icon: '🛳️',
    category: 'maritime',
    defaultEnabled: false,
    markerKind: 'trade-route',
    dataSource: 'static-shipping',
  },
  {
    id: 'chokepoints',
    name: 'Maritime Chokepoints',
    icon: '🔒',
    category: 'maritime',
    defaultEnabled: true,
    markerKind: 'chokepoint',
    dataSource: 'static-chokepoints',
  },

  // ── Aviation ─────────────────────────────────────────────────────────────
  {
    id: 'commercial-flights',
    name: 'Commercial Flights',
    icon: '✈️',
    category: 'aviation',
    defaultEnabled: false,
    markerKind: 'flight',
    dataSource: 'adsb-exchange',
    refreshInterval: 30_000,
  },
  {
    id: 'aviation-military-flights',
    name: 'Military Aviation',
    icon: '🛩️',
    category: 'aviation',
    defaultEnabled: true,
    markerKind: 'flight',
    dataSource: 'adsb-mil',
    refreshInterval: 30_000,
  },
  {
    id: 'notams',
    name: 'NOTAMs',
    icon: '⚠️',
    category: 'aviation',
    defaultEnabled: false,
    dataSource: 'faa-notam',
    refreshInterval: 600_000,
  },
  {
    id: 'restricted-airspace',
    name: 'Restricted Airspace',
    icon: '🚫',
    category: 'aviation',
    defaultEnabled: false,
    dataSource: 'faa-tfr',
    refreshInterval: 600_000,
  },

  // ── Seismic ──────────────────────────────────────────────────────────────
  {
    id: 'earthquakes',
    name: 'Earthquakes',
    icon: '🌍',
    category: 'seismic',
    defaultEnabled: true,
    markerKind: 'earthquake',
    dataSource: 'usgs',
    refreshInterval: 120_000,
  },
  {
    id: 'tsunamis',
    name: 'Tsunami Alerts',
    icon: '🌊',
    category: 'seismic',
    defaultEnabled: true,
    dataSource: 'noaa-tsunami',
    refreshInterval: 300_000,
  },
  {
    id: 'volcanoes',
    name: 'Volcanic Activity',
    icon: '🌋',
    category: 'seismic',
    defaultEnabled: false,
    dataSource: 'smithsonian-gvp',
    refreshInterval: 600_000,
  },

  // ── Cyber ────────────────────────────────────────────────────────────────
  {
    id: 'cyber-threats',
    name: 'Cyber Threats',
    icon: '💻',
    category: 'cyber',
    defaultEnabled: true,
    markerKind: 'cyber',
    dataSource: 'cyber-feeds',
    refreshInterval: 300_000,
  },
  {
    id: 'gps-jamming',
    name: 'GPS Jamming',
    icon: '📍',
    category: 'cyber',
    defaultEnabled: true,
    markerKind: 'gps-jam',
    dataSource: 'gpsjam',
    refreshInterval: 300_000,
  },
  {
    id: 'dns-attacks',
    name: 'DNS Attacks',
    icon: '🌐',
    category: 'cyber',
    defaultEnabled: false,
    markerKind: 'cyber',
    dataSource: 'cyber-feeds',
    refreshInterval: 300_000,
  },

  // ── Civil ────────────────────────────────────────────────────────────────
  {
    id: 'protests',
    name: 'Protests & Demonstrations',
    icon: '✊',
    category: 'civil',
    defaultEnabled: true,
    markerKind: 'protest',
    dataSource: 'acled',
    refreshInterval: 300_000,
  },
  {
    id: 'displacement',
    name: 'Population Displacement',
    icon: '🏃',
    category: 'civil',
    defaultEnabled: false,
    dataSource: 'unhcr',
    refreshInterval: 3_600_000,
  },
  {
    id: 'refugees',
    name: 'Refugee Flows',
    icon: '🧳',
    category: 'civil',
    defaultEnabled: false,
    dataSource: 'unhcr',
    refreshInterval: 3_600_000,
  },
  {
    id: 'unrest',
    name: 'Civil Unrest Index',
    icon: '🔥',
    category: 'civil',
    defaultEnabled: false,
    dataSource: 'acled',
    refreshInterval: 600_000,
  },

  // ── Infrastructure ───────────────────────────────────────────────────────
  {
    id: 'undersea-cables',
    name: 'Undersea Cables',
    icon: '🔌',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'cable',
    dataSource: 'static-cables',
  },
  {
    id: 'cable-health',
    name: 'Cable Health Monitor',
    icon: '🩺',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'cable',
    dataSource: 'cable-monitor',
    refreshInterval: 300_000,
  },
  {
    id: 'power-grid',
    name: 'Power Grid Status',
    icon: '⚡',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'infrastructure',
    dataSource: 'power-outage',
    refreshInterval: 300_000,
  },
  {
    id: 'telecom',
    name: 'Telecom Infrastructure',
    icon: '📶',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'infrastructure',
    dataSource: 'downdetector',
    refreshInterval: 300_000,
  },
  {
    id: 'pipelines',
    name: 'Oil & Gas Pipelines',
    icon: '🛢️',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'pipeline',
    dataSource: 'static-pipelines',
  },
  {
    id: 'dams',
    name: 'Dams & Reservoirs',
    icon: '🏗️',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'infrastructure',
    dataSource: 'static-dams',
  },

  // ── Environmental ────────────────────────────────────────────────────────
  {
    id: 'wildfires',
    name: 'Wildfires',
    icon: '🔥',
    category: 'environmental',
    defaultEnabled: true,
    markerKind: 'fire',
    dataSource: 'firms-nasa',
    refreshInterval: 300_000,
  },
  {
    id: 'fires',
    name: 'Active Fire Detections',
    icon: '🔥',
    category: 'environmental',
    defaultEnabled: false,
    markerKind: 'fire',
    dataSource: 'firms-nasa',
    refreshInterval: 300_000,
  },
  {
    id: 'climate-anomalies',
    name: 'Climate Anomalies',
    icon: '🌡️',
    category: 'environmental',
    defaultEnabled: false,
    dataSource: 'noaa-climate',
    refreshInterval: 3_600_000,
  },
  {
    id: 'storms',
    name: 'Tropical Storms & Cyclones',
    icon: '🌀',
    category: 'environmental',
    defaultEnabled: true,
    dataSource: 'noaa-nhc',
    refreshInterval: 600_000,
  },
  {
    id: 'floods',
    name: 'Flood Alerts',
    icon: '🌊',
    category: 'environmental',
    defaultEnabled: false,
    dataSource: 'gdacs',
    refreshInterval: 600_000,
  },

  // ── Economic ─────────────────────────────────────────────────────────────
  {
    id: 'trade-routes',
    name: 'Major Trade Routes',
    icon: '🚢',
    category: 'economic',
    defaultEnabled: false,
    markerKind: 'trade-route',
    dataSource: 'static-trade-routes',
  },
  {
    id: 'ports',
    name: 'Ports & Terminals',
    icon: '🏭',
    category: 'economic',
    defaultEnabled: false,
    markerKind: 'infrastructure',
    dataSource: 'static-ports',
  },
  {
    id: 'exchanges',
    name: 'Stock Exchanges',
    icon: '📈',
    category: 'economic',
    defaultEnabled: false,
    dataSource: 'static-exchanges',
  },
  {
    id: 'sanctions',
    name: 'Sanctions Zones',
    icon: '🚫',
    category: 'economic',
    defaultEnabled: false,
    dataSource: 'ofac',
    refreshInterval: 86_400_000,
  },

  // ── Nuclear ──────────────────────────────────────────────────────────────
  {
    id: 'nuclear-sites',
    name: 'Nuclear Facilities',
    icon: '☢️',
    category: 'nuclear',
    defaultEnabled: false,
    markerKind: 'nuclear',
    dataSource: 'static-nuclear',
  },
  {
    id: 'radiation',
    name: 'Radiation Monitoring',
    icon: '☢️',
    category: 'nuclear',
    defaultEnabled: false,
    markerKind: 'radiation',
    dataSource: 'radmon',
    refreshInterval: 600_000,
  },
  {
    id: 'enrichment',
    name: 'Enrichment Facilities',
    icon: '⚛️',
    category: 'nuclear',
    defaultEnabled: false,
    markerKind: 'nuclear',
    dataSource: 'static-nuclear',
  },

  // ── Space ────────────────────────────────────────────────────────────────
  {
    id: 'satellites',
    name: 'Active Satellites',
    icon: '🛰️',
    category: 'space',
    defaultEnabled: false,
    markerKind: 'satellite',
    dataSource: 'celestrak',
    refreshInterval: 600_000,
  },
  {
    id: 'debris',
    name: 'Space Debris',
    icon: '🪨',
    category: 'space',
    defaultEnabled: false,
    markerKind: 'satellite',
    dataSource: 'celestrak',
    refreshInterval: 3_600_000,
  },
  {
    id: 'launches',
    name: 'Rocket Launches',
    icon: '🚀',
    category: 'space',
    defaultEnabled: false,
    dataSource: 'launch-library',
    refreshInterval: 3_600_000,
  },
  {
    id: 'solar-weather',
    name: 'Solar Weather',
    icon: '☀️',
    category: 'space',
    defaultEnabled: false,
    dataSource: 'noaa-swpc',
    refreshInterval: 900_000,
  },
  {
    id: 'internet-outages',
    name: 'Internet Outages',
    icon: '🌐',
    category: 'infrastructure',
    defaultEnabled: false,
    markerKind: 'infrastructure',
    dataSource: 'ioda',
    refreshInterval: 300_000,
  },
];

// ---------------------------------------------------------------------------
// Default enabled layers
// ---------------------------------------------------------------------------

export const DEFAULT_ENABLED_LAYERS: string[] = MAP_LAYERS
  .filter((l) => l.defaultEnabled)
  .map((l) => l.id);

// ---------------------------------------------------------------------------
// Lookup helpers
// ---------------------------------------------------------------------------

/** Return all layers belonging to a given category. */
export function getLayersByCategory(category: LayerCategory): LayerDefinition[] {
  return MAP_LAYERS.filter((l) => l.category === category);
}

/** Return a single layer by its unique id, or undefined. */
export function getLayerById(id: string): LayerDefinition | undefined {
  return MAP_LAYERS.find((l) => l.id === id);
}
