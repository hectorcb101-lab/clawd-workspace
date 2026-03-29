// ============================================================================
// Atlas Intel — Master Type Definitions
// ============================================================================

// ---------------------------------------------------------------------------
// Map & Geo
// ---------------------------------------------------------------------------

export interface Coordinates {
  lat: number;
  lng: number;
  alt?: number;
}

export type MarkerKind =
  | 'vessel'
  | 'flight'
  | 'earthquake'
  | 'fire'
  | 'cyber'
  | 'protest'
  | 'radiation'
  | 'base'
  | 'nuclear'
  | 'webcam'
  | 'infrastructure'
  | 'gps-jam'
  | 'satellite'
  | 'chokepoint'
  | 'cable'
  | 'pipeline'
  | 'trade-route';

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  kind: MarkerKind;
  label?: string;
  data?: Record<string, unknown>;
  timestamp?: number;
}

export type MapEngine = '3d' | '2d';
export type RenderQuality = 'auto' | 'eco' | 'sharp' | '4k';
export type TileProvider = 'openfreemap' | 'carto';
export type MapTheme = 'dark' | 'light';

// ---------------------------------------------------------------------------
// Regional Presets
// ---------------------------------------------------------------------------

export interface RegionPreset {
  name: string;
  lat: number;
  lng: number;
  zoom: number;
  altitude?: number;
}

export type RegionName =
  | 'global'
  | 'americas'
  | 'europe'
  | 'mena'
  | 'asia'
  | 'africa'
  | 'oceania'
  | 'latin-america';

// ---------------------------------------------------------------------------
// Time Filtering
// ---------------------------------------------------------------------------

export type TimeRange = '1h' | '6h' | '24h' | '48h' | '7d';

// ---------------------------------------------------------------------------
// Layers
// ---------------------------------------------------------------------------

export type LayerCategory =
  | 'military'
  | 'maritime'
  | 'aviation'
  | 'seismic'
  | 'cyber'
  | 'civil'
  | 'infrastructure'
  | 'environmental'
  | 'economic'
  | 'nuclear'
  | 'space';

export interface LayerDefinition {
  id: string;
  name: string;
  icon: string;
  category: LayerCategory;
  defaultEnabled: boolean;
  markerKind?: MarkerKind;
  dataSource?: string;
  refreshInterval?: number;
}

// ---------------------------------------------------------------------------
// News
// ---------------------------------------------------------------------------

export type SourceTier = 1 | 2 | 3 | 4;

export type ThreatCategory =
  | 'military'
  | 'conflict'
  | 'cyber'
  | 'nuclear'
  | 'unrest'
  | 'economic'
  | 'terrorism'
  | 'health'
  | 'climate'
  | 'energy'
  | 'space'
  | 'maritime'
  | 'aviation'
  | 'infrastructure';

export interface NewsItem {
  id: string;
  title: string;
  url: string;
  source: string;
  sourceTier: SourceTier;
  timestamp: number;
  country?: string;
  countries?: string[];
  lat?: number;
  lng?: number;
  threatCategory?: ThreatCategory;
  threatScore?: number;
  summary?: string;
  propagandaRisk?: boolean;
  velocity?: number;
}

// ---------------------------------------------------------------------------
// Country Instability Index
// ---------------------------------------------------------------------------

export type Trend = 'rising' | 'stable' | 'falling';
export type SeverityLevel = 'critical' | 'high' | 'elevated' | 'guarded' | 'low';

export interface CountryScore {
  code: string;
  name: string;
  flag: string;
  score: number;
  unrest: number;
  security: number;
  information: number;
  trend: Trend;
  trendDelta: number;
  headlines: NewsItem[];
  isConflictZone: boolean;
  floorScore: number;
}

// ---------------------------------------------------------------------------
// Signals
// ---------------------------------------------------------------------------

export type SignalType =
  | 'convergence'
  | 'triangulation'
  | 'velocity-spike'
  | 'prediction-leading'
  | 'news-leads-markets'
  | 'market-move-explained'
  | 'silent-divergence'
  | 'sector-cascade'
  | 'flow-drop'
  | 'flow-price-divergence'
  | 'geographic-convergence'
  | 'military-surge';

export interface Signal {
  id: string;
  type: SignalType;
  title: string;
  description: string;
  severity: SeverityLevel;
  timestamp: number;
  countries?: string[];
  entities?: string[];
  sources: string[];
  ttl: number;
}

// ---------------------------------------------------------------------------
// Theater Posture
// ---------------------------------------------------------------------------

export type PostureLevel = 'CRIT' | 'HIGH' | 'ELEVATED' | 'NORMAL';

export interface TheaterPosture {
  id: string;
  name: string;
  region: Coordinates;
  posture: PostureLevel;
  militaryFlights: number;
  navalVessels: number;
  recentEvents: string[];
  trend: Trend;
  lastUpdated: number;
}

// ---------------------------------------------------------------------------
// Live Channels
// ---------------------------------------------------------------------------

export interface LiveChannel {
  id: string;
  name: string;
  youtubeId: string;
  category?: string;
  language?: string;
}

// ---------------------------------------------------------------------------
// Webcams
// ---------------------------------------------------------------------------

export interface Webcam {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  thumbUrl: string;
  streamUrl: string;
  pinned?: boolean;
}

// ---------------------------------------------------------------------------
// Markets
// ---------------------------------------------------------------------------

export interface MarketItem {
  ticker: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  currency?: string;
  exchange?: string;
}

export interface MarketComposite {
  score: number;
  signals: string[];
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Prediction Markets
// ---------------------------------------------------------------------------

export interface PredictionContract {
  id: string;
  question: string;
  probability: number;
  volume: number;
  url: string;
  category?: string;
}

// ---------------------------------------------------------------------------
// Entities
// ---------------------------------------------------------------------------

export type EntityType =
  | 'state'
  | 'military'
  | 'corporation'
  | 'organization'
  | 'leader'
  | 'group';

export interface Entity {
  id: string;
  name: string;
  aliases: string[];
  type: EntityType;
  country?: string;
  sector?: string;
  keywords: string[];
}

// ---------------------------------------------------------------------------
// Country Config
// ---------------------------------------------------------------------------

export interface MonitoredCountry {
  code: string;
  name: string;
  flag: string;
  aliases: string[];
  isConflictZone: boolean;
  floorScore: number;
  region: string;
}

// ---------------------------------------------------------------------------
// Geo Config — Hotspots, Bases, Nuclear Sites, Infrastructure
// ---------------------------------------------------------------------------

export interface Hotspot {
  name: string;
  lat: number;
  lng: number;
  radius: number;
}

export interface MilitaryBase {
  name: string;
  lat: number;
  lng: number;
  country: string;
  type: string;
  branch?: string;
}

export interface NuclearSite {
  name: string;
  lat: number;
  lng: number;
  country: string;
  type: 'power' | 'research' | 'weapons' | 'enrichment' | 'waste';
  status: string;
}

export interface SubseaCable {
  name: string;
  points: [number, number][];
  owners?: string[];
  length_km?: number;
}

export interface Waterway {
  name: string;
  lat: number;
  lng: number;
  type: 'strait' | 'canal' | 'passage';
}

export interface PipelineData {
  name: string;
  points: [number, number][];
  type: 'oil' | 'gas';
  capacity?: string;
}

export interface TradeRoute {
  name: string;
  points: [number, number][];
  type: string;
}

// ---------------------------------------------------------------------------
// AI
// ---------------------------------------------------------------------------

export type AIProvider = 'ollama' | 'groq' | 'openrouter' | 'browser-t5';

export interface AIConfig {
  provider: AIProvider;
  model?: string;
  endpoint?: string;
  apiKey?: string;
}

export interface AIBrief {
  text: string;
  citations: number[];
  provider: AIProvider;
  timestamp: number;
  country?: string;
}

// ---------------------------------------------------------------------------
// Data Bridge
// ---------------------------------------------------------------------------

export interface DataBridgeConfig {
  endpoint: string;
  interval: number;
}

export interface DataStatus {
  source: string;
  status: 'live' | 'cached' | 'unavailable';
  lastUpdated: number;
  count: number;
}

// ---------------------------------------------------------------------------
// Convergence
// ---------------------------------------------------------------------------

export interface ConvergenceCell {
  lat: number;
  lng: number;
  types: Set<string>;
  events: number;
  score: number;
}

// ---------------------------------------------------------------------------
// Cascade
// ---------------------------------------------------------------------------

export interface CascadeDomain {
  name: string;
  status: 'normal' | 'degraded' | 'critical';
  dependencies: string[];
}

export interface CascadeAlert {
  id: string;
  chain: string[];
  severity: SeverityLevel;
  timestamp: number;
  description: string;
}

// ---------------------------------------------------------------------------
// Cache
// ---------------------------------------------------------------------------

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export type CacheTier = 'memory' | 'localStorage' | 'indexedDB';

// ---------------------------------------------------------------------------
// DEFCON / PizzInt
// ---------------------------------------------------------------------------

export interface PizzIntStatus {
  level: number;
  label: string;
  description: string;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Risk
// ---------------------------------------------------------------------------

export interface CachedRiskScores {
  ciiAvg: number;
  convergenceAlerts: number;
  postureAlerts: number;
  cascadeAlerts: number;
  overall: SeverityLevel;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------

export interface AppSettings {
  mapEngine: MapEngine;
  renderQuality: RenderQuality;
  tileProvider: TileProvider;
  mapTheme: MapTheme;
  aiProvider: AIProvider;
  ollamaEndpoint: string;
  language: string;
  enableML: boolean;
  enableHeadlineMemory: boolean;
  enableScanlines: boolean;
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

export interface PanelConfig {
  id: string;
  title: string;
  icon: string;
  description: string;
  defaultOpen: boolean;
  position?: { x: number; y: number };
}

// ---------------------------------------------------------------------------
// URL State
// ---------------------------------------------------------------------------

export interface URLState {
  lat?: number;
  lng?: number;
  zoom?: number;
  layers?: string[];
  timeRange?: TimeRange;
  engine?: MapEngine;
  panel?: string;
  country?: string;
}

// ---------------------------------------------------------------------------
// Breaking News
// ---------------------------------------------------------------------------

export type AlertOrigin =
  | 'rss-critical'
  | 'keyword-spike'
  | 'hotspot-escalation'
  | 'military-surge'
  | 'oref-siren';

export interface BreakingAlert {
  id: string;
  title: string;
  source: string;
  origin: AlertOrigin;
  timestamp: number;
  severity: SeverityLevel;
}

// ---------------------------------------------------------------------------
// Displacement
// ---------------------------------------------------------------------------

export interface DisplacementData {
  country: string;
  refugees: number;
  idps: number;
  returnees: number;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Climate
// ---------------------------------------------------------------------------

export interface ClimateAnomaly {
  zone: string;
  type: 'temperature' | 'precipitation';
  deviation: number;
  baseline: number;
  current: number;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Airline Intelligence
// ---------------------------------------------------------------------------

export interface AirlineIntel {
  airport: string;
  code: string;
  status: 'normal' | 'delays' | 'disrupted' | 'closed';
  delayMinutes?: number;
  flights: number;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Timeline
// ---------------------------------------------------------------------------

export interface TimelineEvent {
  timestamp: number;
  type: string;
  label: string;
  severity?: SeverityLevel;
  country?: string;
}

// ---------------------------------------------------------------------------
// Feed Config
// ---------------------------------------------------------------------------

export interface FeedDefinition {
  url: string;
  name: string;
  category: string;
  tier: SourceTier;
  language?: string;
  propagandaRisk?: boolean;
  region?: string;
}

// ---------------------------------------------------------------------------
// Commodity
// ---------------------------------------------------------------------------

export interface CommodityData {
  name: string;
  price: number;
  change: number;
  unit: string;
  category: 'energy' | 'metals' | 'agriculture';
}

// ---------------------------------------------------------------------------
// Energy
// ---------------------------------------------------------------------------

export interface EnergyData {
  type: 'oil' | 'gas' | 'coal' | 'nuclear' | 'renewable';
  production: number;
  consumption: number;
  price: number;
  unit: string;
}

// ---------------------------------------------------------------------------
// ML Worker Messages
// ---------------------------------------------------------------------------

export interface MLRequest {
  type: 'embeddings' | 'sentiment' | 'ner' | 'classify';
  payload: unknown;
}

export interface MLResponse {
  type: string;
  result: unknown;
  error?: string;
}

// ---------------------------------------------------------------------------
// Headline Memory (RAG)
// ---------------------------------------------------------------------------

export interface HeadlineVector {
  id: string;
  headline: string;
  embedding: Float32Array;
  timestamp: number;
  source: string;
}
