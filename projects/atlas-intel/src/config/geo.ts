// ============================================================================
// Atlas Intel — Geo Configuration
// Hotspots, Military Bases, Nuclear Sites, Chokepoints, Waterways, Cities
// ============================================================================

import type {
  Hotspot,
  MilitaryBase,
  NuclearSite,
  Waterway,
  Coordinates,
} from '@/types/index';

// ---------------------------------------------------------------------------
// HOTSPOTS — Key global flashpoints & areas of strategic concern
// ---------------------------------------------------------------------------

export const HOTSPOTS: Hotspot[] = [
  // --- Active Conflict Zones ---
  { name: 'Ukraine Frontlines (East)',   lat: 48.50,  lng: 37.80,  radius: 3.0 },
  { name: 'Ukraine Frontlines (South)',  lat: 46.80,  lng: 33.50,  radius: 2.5 },
  { name: 'Gaza Strip',                  lat: 31.35,  lng: 34.31,  radius: 0.5 },
  { name: 'Golan Heights',               lat: 33.20,  lng: 35.80,  radius: 0.8 },
  { name: 'Southern Lebanon',            lat: 33.30,  lng: 35.40,  radius: 1.0 },
  { name: 'Red Sea / Houthi Zone',       lat: 14.50,  lng: 42.50,  radius: 3.0 },

  // --- High-Tension Flashpoints ---
  { name: 'Taiwan Strait',               lat: 24.00,  lng: 119.50, radius: 2.5 },
  { name: 'South China Sea',             lat: 12.00,  lng: 114.00, radius: 5.0 },
  { name: 'Korean DMZ',                  lat: 37.95,  lng: 127.00, radius: 1.5 },
  { name: 'Strait of Hormuz',            lat: 26.50,  lng: 56.50,  radius: 1.5 },

  // --- Strategic Waterways & Seas ---
  { name: 'Baltic Sea (NATO Flank)',     lat: 56.00,  lng: 18.00,  radius: 4.0 },
  { name: 'Black Sea',                   lat: 43.50,  lng: 34.00,  radius: 3.5 },
  { name: 'Persian Gulf',                lat: 27.00,  lng: 51.00,  radius: 3.0 },
  { name: 'Eastern Mediterranean',       lat: 34.50,  lng: 33.00,  radius: 3.0 },
  { name: 'Bab-el-Mandeb',              lat: 12.60,  lng: 43.30,  radius: 1.5 },

  // --- Emerging / Simmering ---
  { name: 'Suwalki Gap (NATO)',          lat: 54.10,  lng: 23.00,  radius: 1.5 },
  { name: 'Kaliningrad Exclave',         lat: 54.70,  lng: 20.50,  radius: 1.5 },
  { name: 'Kashmir LoC',                lat: 34.50,  lng: 75.50,  radius: 2.0 },
  { name: 'Sahel Region',               lat: 15.00,  lng: 2.00,   radius: 5.0 },
  { name: 'Horn of Africa',             lat: 8.00,   lng: 46.00,  radius: 4.0 },
];

// ---------------------------------------------------------------------------
// CHOKEPOINTS — Critical maritime chokepoints
// ---------------------------------------------------------------------------

export const CHOKEPOINTS: Waterway[] = [
  { name: 'Strait of Hormuz',     lat: 26.50,   lng: 56.50,    type: 'strait' },
  { name: 'Suez Canal',           lat: 30.50,   lng: 32.50,    type: 'canal' },
  { name: 'Strait of Malacca',    lat: 2.50,    lng: 100.00,   type: 'strait' },
  { name: 'Panama Canal',         lat: 9.00,    lng: -79.50,   type: 'canal' },
  { name: 'Bab-el-Mandeb',        lat: 12.60,   lng: 43.30,    type: 'strait' },
  { name: 'Danish Straits',       lat: 56.00,   lng: 12.00,    type: 'strait' },
  { name: 'Turkish Straits',      lat: 41.00,   lng: 29.00,    type: 'strait' },
  { name: 'Strait of Gibraltar',  lat: 35.96,   lng: -5.50,    type: 'strait' },
  { name: 'English Channel',      lat: 50.50,   lng: 1.00,     type: 'passage' },
  { name: 'Cape of Good Hope',    lat: -34.35,  lng: 18.50,    type: 'passage' },
  { name: 'Taiwan Strait',        lat: 24.00,   lng: 119.50,   type: 'strait' },
  { name: 'Lombok Strait',        lat: -8.40,   lng: 115.70,   type: 'strait' },
];

// ---------------------------------------------------------------------------
// WATERWAYS — Alias for CHOKEPOINTS (same data, exported separately)
// ---------------------------------------------------------------------------

export const WATERWAYS: Waterway[] = CHOKEPOINTS;

// ---------------------------------------------------------------------------
// MILITARY BASES — Top ~50 strategically significant overseas bases
// ---------------------------------------------------------------------------

export const MILITARY_BASES: MilitaryBase[] = [
  // === United States / NATO ===
  // -- Europe --
  { name: 'Ramstein Air Base',              lat: 49.4430, lng:   7.6006, country: 'Germany',        type: 'us-nato', branch: 'Air Force' },
  { name: 'Spangdahlem Air Base',           lat: 49.9726, lng:   6.6925, country: 'Germany',        type: 'us-nato', branch: 'Air Force' },
  { name: 'USAG Stuttgart (EUCOM HQ)',      lat: 48.7823, lng:   9.1770, country: 'Germany',        type: 'us-nato', branch: 'Army' },
  { name: 'USAG Grafenwöhr',               lat: 49.7173, lng:  11.9064, country: 'Germany',        type: 'us-nato', branch: 'Army' },
  { name: 'Landstuhl Regional Medical Ctr', lat: 49.4131, lng:   7.5702, country: 'Germany',        type: 'us-nato', branch: 'Army' },
  { name: 'Aviano Air Base',               lat: 46.0706, lng:  12.5947, country: 'Italy',          type: 'us-nato', branch: 'Air Force' },
  { name: 'NSA Naples',                    lat: 40.8333, lng:  14.2500, country: 'Italy',          type: 'us-nato', branch: 'Navy' },
  { name: 'Naval Station Rota',            lat: 36.6224, lng:  -6.3586, country: 'Spain',          type: 'us-nato', branch: 'Navy' },
  { name: 'RAF Lakenheath',                lat: 52.4175, lng:   0.5221, country: 'UK',             type: 'us-nato', branch: 'Air Force' },
  { name: 'RAF Mildenhall',                lat: 52.3614, lng:   0.4864, country: 'UK',             type: 'us-nato', branch: 'Air Force' },
  { name: 'Camp Bondsteel',                lat: 42.3667, lng:  21.1333, country: 'Kosovo',         type: 'us-nato', branch: 'Army' },
  { name: 'Lajes Field',                   lat: 38.7617, lng: -27.0886, country: 'Portugal',       type: 'us-nato', branch: 'Air Force' },

  // -- Middle East / Central Asia --
  { name: 'Incirlik Air Base',             lat: 37.0021, lng:  35.4259, country: 'Turkey',         type: 'us-nato', branch: 'Air Force' },
  { name: 'Al Udeid Air Base',             lat: 25.1173, lng:  51.3150, country: 'Qatar',          type: 'us-nato', branch: 'Air Force' },
  { name: 'Al Dhafra Air Base',            lat: 24.2400, lng:  54.5510, country: 'UAE',            type: 'us-nato', branch: 'Air Force' },
  { name: 'Camp Arifjan',                  lat: 28.8751, lng:  48.1589, country: 'Kuwait',         type: 'us-nato', branch: 'Army' },
  { name: 'Ali Al Salem Air Base',         lat: 29.3487, lng:  47.5235, country: 'Kuwait',         type: 'us-nato', branch: 'Air Force' },
  { name: 'Naval Support Activity Bahrain',lat: 26.2086, lng:  50.6097, country: 'Bahrain',        type: 'us-nato', branch: 'Navy' },
  { name: 'Prince Sultan Air Base',        lat: 24.0769, lng:  47.5640, country: 'Saudi Arabia',   type: 'us-nato', branch: 'Air Force' },
  { name: 'Ain Assad Air Base',            lat: 33.7986, lng:  42.4391, country: 'Iraq',           type: 'us-nato', branch: 'Combined' },

  // -- Indo-Pacific --
  { name: 'Yokosuka Naval Base',           lat: 35.2835, lng: 139.6680, country: 'Japan',          type: 'us-nato', branch: 'Navy' },
  { name: 'Yokota Air Base',               lat: 35.7485, lng: 139.3485, country: 'Japan',          type: 'us-nato', branch: 'Air Force' },
  { name: 'Kadena Air Base',               lat: 26.3516, lng: 127.7694, country: 'Japan',          type: 'us-nato', branch: 'Air Force' },
  { name: 'Marine Corps Base Camp Butler', lat: 26.4843, lng: 127.9550, country: 'Japan',          type: 'us-nato', branch: 'Marines' },
  { name: 'Camp Humphreys (USFK HQ)',     lat: 36.9651, lng: 127.0330, country: 'South Korea',    type: 'us-nato', branch: 'Army' },
  { name: 'Osan Air Base',                lat: 37.0910, lng: 127.0310, country: 'South Korea',    type: 'us-nato', branch: 'Air Force' },
  { name: 'Andersen Air Force Base',       lat: 13.5840, lng: 144.9243, country: 'Guam',           type: 'us-nato', branch: 'Air Force' },
  { name: 'Joint Region Marianas',         lat: 13.4505, lng: 144.7937, country: 'Guam',           type: 'us-nato', branch: 'Navy' },
  { name: 'Clark Air Base (EDCA)',         lat: 15.1860, lng: 120.5600, country: 'Philippines',    type: 'us-nato', branch: 'Air Force' },

  // -- Africa --
  { name: 'Camp Lemonnier',                lat: 11.5436, lng:  43.1486, country: 'Djibouti',       type: 'us-nato', branch: 'Navy' },

  // -- Diego Garcia --
  { name: 'NSF Diego Garcia',             lat: -7.3133, lng:  72.4111, country: 'BIOT',           type: 'us-nato', branch: 'Navy' },

  // === Russia ===
  { name: 'Kaliningrad Naval Base',        lat: 54.7104, lng:  20.4522, country: 'Russia',         type: 'russia', branch: 'Navy' },
  { name: 'Sevastopol Naval Base',         lat: 44.6167, lng:  33.5254, country: 'Crimea',         type: 'russia', branch: 'Navy' },
  { name: 'Tartus Naval Facility',         lat: 34.9150, lng:  35.8740, country: 'Syria',          type: 'russia', branch: 'Navy' },
  { name: 'Hmeimim Air Base',             lat: 35.4110, lng:  35.9450, country: 'Syria',          type: 'russia', branch: 'Air Force' },
  { name: 'Russian 102nd Military Base',   lat: 40.7900, lng:  43.8250, country: 'Armenia',        type: 'russia', branch: 'Combined' },
  { name: 'Kant Air Base',                lat: 42.8530, lng:  74.8460, country: 'Kyrgyzstan',     type: 'russia', branch: 'Air Force' },
  { name: 'Baikonur Cosmodrome',           lat: 45.9640, lng:  63.3050, country: 'Kazakhstan',     type: 'russia', branch: 'Space' },
  { name: 'Russian 201st Military Base',   lat: 38.5360, lng:  68.7800, country: 'Tajikistan',     type: 'russia', branch: 'Combined' },

  // === China ===
  { name: 'PLA Support Base Djibouti',    lat: 11.5915, lng:  43.0602, country: 'Djibouti',       type: 'china', branch: 'Navy' },
  { name: 'Ream Naval Base (access)',      lat: 10.5034, lng: 103.6090, country: 'Cambodia',       type: 'china', branch: 'Navy' },
  { name: 'Fiery Cross Reef',             lat:  9.5458, lng: 112.8875, country: 'Disputed (SCS)', type: 'china', branch: 'Combined' },
  { name: 'Subi Reef',                    lat: 10.9236, lng: 114.0847, country: 'Disputed (SCS)', type: 'china', branch: 'Combined' },
  { name: 'Mischief Reef',                lat:  9.9000, lng: 115.5333, country: 'Disputed (SCS)', type: 'china', branch: 'Combined' },
  { name: 'Woody Island (Paracel)',        lat: 16.8344, lng: 112.3397, country: 'Disputed (SCS)', type: 'china', branch: 'Combined' },

  // === United Kingdom ===
  { name: 'RAF Akrotiri',                 lat: 34.5900, lng:  32.9870, country: 'Cyprus',         type: 'uk', branch: 'Air Force' },
  { name: 'HMS Jufair',                   lat: 26.2050, lng:  50.6150, country: 'Bahrain',        type: 'uk', branch: 'Navy' },
  { name: 'RAF Gibraltar',                lat: 36.1521, lng:  -5.3445, country: 'Gibraltar',      type: 'uk', branch: 'Air Force' },

  // === France ===
  { name: 'French Forces Djibouti (Héron)',lat: 11.5566, lng:  43.1442, country: 'Djibouti',       type: 'france', branch: 'Navy' },
  { name: 'Abu Dhabi French Base',         lat: 24.5215, lng:  54.3961, country: 'UAE',            type: 'france', branch: 'Combined' },
];

// ---------------------------------------------------------------------------
// NUCLEAR SITES — Key weapons, enrichment, research & power facilities
// ---------------------------------------------------------------------------

export const NUCLEAR_SITES: NuclearSite[] = [
  // === Iran ===
  { name: 'Natanz Enrichment Facility',           lat: 33.72,  lng:  51.72, country: 'Iran',          type: 'enrichment', status: 'active' },
  { name: 'Fordow Enrichment Facility',            lat: 34.69,  lng:  50.99, country: 'Iran',          type: 'enrichment', status: 'active' },
  { name: 'Bushehr Nuclear Power Plant',           lat: 28.84,  lng:  50.88, country: 'Iran',          type: 'power',      status: 'active' },
  { name: 'Isfahan Nuclear Technology Center',     lat: 32.65,  lng:  51.68, country: 'Iran',          type: 'research',   status: 'active' },
  { name: 'Arak Heavy Water Reactor',             lat: 34.05,  lng:  49.25, country: 'Iran',          type: 'research',   status: 'active' },

  // === Israel ===
  { name: 'Dimona Nuclear Research Center',        lat: 31.00,  lng:  35.14, country: 'Israel',        type: 'weapons',    status: 'active' },

  // === North Korea ===
  { name: 'Yongbyon Nuclear Complex',              lat: 39.79,  lng: 125.76, country: 'North Korea',   type: 'weapons',    status: 'active' },
  { name: 'Punggye-ri Nuclear Test Site',          lat: 41.28,  lng: 129.10, country: 'North Korea',   type: 'weapons',    status: 'demolished' },

  // === Pakistan ===
  { name: 'Kahuta (KRL)',                          lat: 33.59,  lng:  73.39, country: 'Pakistan',      type: 'enrichment', status: 'active' },
  { name: 'Khushab Nuclear Complex',               lat: 32.02,  lng:  72.22, country: 'Pakistan',      type: 'weapons',    status: 'active' },
  { name: 'Pakistan Institute of Nuclear Science', lat: 33.65,  lng:  73.02, country: 'Pakistan',      type: 'research',   status: 'active' },

  // === India ===
  { name: 'Bhabha Atomic Research Centre',         lat: 19.01,  lng:  72.92, country: 'India',         type: 'research',   status: 'active' },
  { name: 'Tarapur Nuclear Power Plant',           lat: 19.83,  lng:  72.63, country: 'India',         type: 'power',      status: 'active' },
  { name: 'Kudankulam Nuclear Power Plant',        lat:  8.17,  lng:  77.71, country: 'India',         type: 'power',      status: 'active' },
  { name: 'Pokhran Nuclear Test Site',             lat: 26.73,  lng:  71.75, country: 'India',         type: 'weapons',    status: 'inactive' },

  // === Russia ===
  { name: 'Sarov (Arzamas-16)',                   lat: 54.93,  lng:  43.32, country: 'Russia',        type: 'weapons',    status: 'active' },
  { name: 'Mayak Nuclear Complex',                 lat: 55.72,  lng:  60.80, country: 'Russia',        type: 'enrichment', status: 'active' },
  { name: 'Seversk (Tomsk-7)',                     lat: 56.60,  lng:  84.88, country: 'Russia',        type: 'enrichment', status: 'active' },
  { name: 'Zheleznogorsk (Krasnoyarsk-26)',       lat: 56.25,  lng:  93.53, country: 'Russia',        type: 'weapons',    status: 'active' },
  { name: 'Novaya Zemlya Test Site',               lat: 73.37,  lng:  54.97, country: 'Russia',        type: 'weapons',    status: 'standby' },
  { name: 'Kursk Nuclear Power Plant',             lat: 51.67,  lng:  35.60, country: 'Russia',        type: 'power',      status: 'active' },
  { name: 'Novovoronezh Nuclear Power Plant',      lat: 51.27,  lng:  39.22, country: 'Russia',        type: 'power',      status: 'active' },

  // === United States ===
  { name: 'Los Alamos National Laboratory',        lat: 35.84,  lng:-106.29, country: 'USA',           type: 'weapons',    status: 'active' },
  { name: 'Lawrence Livermore National Lab',        lat: 37.69,  lng:-121.70, country: 'USA',           type: 'weapons',    status: 'active' },
  { name: 'Pantex Plant',                          lat: 35.32,  lng:-101.95, country: 'USA',           type: 'weapons',    status: 'active' },
  { name: 'Y-12 National Security Complex',        lat: 36.00,  lng: -84.25, country: 'USA',           type: 'weapons',    status: 'active' },
  { name: 'Savannah River Site',                   lat: 33.34,  lng: -81.74, country: 'USA',           type: 'weapons',    status: 'active' },
  { name: 'Hanford Site',                          lat: 46.55,  lng:-119.49, country: 'USA',           type: 'waste',      status: 'cleanup' },
  { name: 'Idaho National Laboratory',             lat: 43.52,  lng:-112.94, country: 'USA',           type: 'research',   status: 'active' },
  { name: 'Nevada National Security Site',         lat: 37.00,  lng:-116.05, country: 'USA',           type: 'weapons',    status: 'standby' },

  // === China ===
  { name: 'Lop Nur Nuclear Test Site',             lat: 41.55,  lng:  88.73, country: 'China',         type: 'weapons',    status: 'inactive' },
  { name: 'China Academy of Engineering Physics',  lat: 31.48,  lng: 104.74, country: 'China',         type: 'weapons',    status: 'active' },
  { name: 'Lanzhou Gaseous Diffusion Plant',       lat: 36.09,  lng: 103.60, country: 'China',         type: 'enrichment', status: 'active' },
  { name: 'Qinshan Nuclear Power Plant',           lat: 30.44,  lng: 120.96, country: 'China',         type: 'power',      status: 'active' },
  { name: 'Daya Bay Nuclear Power Plant',          lat: 22.60,  lng: 114.55, country: 'China',         type: 'power',      status: 'active' },

  // === France ===
  { name: 'Commissariat à l\'Énergie Atomique (Valduc)', lat: 47.49, lng:  4.77, country: 'France', type: 'weapons', status: 'active' },
  { name: 'La Hague Reprocessing Plant',           lat: 49.68,  lng:  -1.88, country: 'France',        type: 'enrichment', status: 'active' },
  { name: 'Tricastin Enrichment Site',             lat: 44.33,  lng:   4.73, country: 'France',        type: 'enrichment', status: 'active' },

  // === United Kingdom ===
  { name: 'AWE Aldermaston',                      lat: 51.37,  lng:  -1.15, country: 'UK',            type: 'weapons',    status: 'active' },
  { name: 'Sellafield (Windscale)',                lat: 54.42,  lng:  -3.50, country: 'UK',            type: 'enrichment', status: 'active' },
  { name: 'HMNB Clyde (Faslane)',                  lat: 56.07,  lng:  -4.82, country: 'UK',            type: 'weapons',    status: 'active' },

  // === Ukraine ===
  { name: 'Zaporizhzhia Nuclear Power Plant',      lat: 47.51,  lng:  34.58, country: 'Ukraine',       type: 'power',      status: 'occupied' },
  { name: 'Chernobyl Exclusion Zone',              lat: 51.39,  lng:  30.10, country: 'Ukraine',       type: 'waste',      status: 'decommissioned' },

  // === Other ===
  { name: 'Barakah Nuclear Power Plant',           lat: 23.96,  lng:  52.26, country: 'UAE',           type: 'power',      status: 'active' },
  { name: 'Rokkasho Reprocessing Plant',           lat: 40.96,  lng: 141.33, country: 'Japan',         type: 'enrichment', status: 'active' },
  { name: 'Yucca Mountain Repository',             lat: 36.84,  lng:-116.43, country: 'USA',           type: 'waste',      status: 'suspended' },
];

// ---------------------------------------------------------------------------
// CITIES — Key reference points for map navigation & trade route rendering
// ---------------------------------------------------------------------------

export const CITIES: Record<string, Coordinates> = {
  // From dashboard/app.js
  london:         { lat: 51.5074, lng:  -0.1278 },
  newyork:        { lat: 40.7128, lng: -74.0060 },
  dubai:          { lat: 25.2048, lng:  55.2708 },
  singapore:      { lat:  1.3521, lng: 103.8198 },
  tokyo:          { lat: 35.6762, lng: 139.6503 },
  washington:     { lat: 38.9072, lng: -77.0369 },
  ukraine:        { lat: 48.3794, lng:  31.1656 },
  taiwan:         { lat: 23.6978, lng: 120.9605 },
  hormuz:         { lat: 26.5000, lng:  56.5000 },
  southchinasea:  { lat: 12.0000, lng: 114.0000 },

  // Extended key cities
  moscow:         { lat: 55.7558, lng:  37.6173 },
  beijing:        { lat: 39.9042, lng: 116.4074 },
  tehran:         { lat: 35.6892, lng:  51.3890 },
  jerusalem:      { lat: 31.7683, lng:  35.2137 },
  pyongyang:      { lat: 39.0392, lng: 125.7625 },
  seoul:          { lat: 37.5665, lng: 126.9780 },
  delhi:          { lat: 28.6139, lng:  77.2090 },
  istanbul:       { lat: 41.0082, lng:  28.9784 },
  cairo:          { lat: 30.0444, lng:  31.2357 },
  berlin:         { lat: 52.5200, lng:  13.4050 },
  paris:          { lat: 48.8566, lng:   2.3522 },
  brussels:       { lat: 50.8503, lng:   4.3517 },

  // Key port / trade cities
  shanghai:       { lat: 31.2304, lng: 121.4737 },
  rotterdam:      { lat: 51.9244, lng:   4.4777 },
  losangeles:     { lat: 33.9425, lng:-118.4081 },
  busan:          { lat: 35.1796, lng: 129.0756 },
  mumbai:         { lat: 19.0760, lng:  72.8777 },
  riyadh:         { lat: 24.7136, lng:  46.6753 },
  djibouti:       { lat: 11.5880, lng:  43.1450 },
  capetown:       { lat:-33.9249, lng:  18.4241 },
  sydney:         { lat:-33.8688, lng: 151.2093 },
};
