// ============================================================================
// Atlas Intel — Major Pipeline Data
// ============================================================================

import type { PipelineData } from '@/types/index';

export const PIPELINES: PipelineData[] = [
  // -------------------------------------------------------------------------
  // Nord Stream 1 — Russia to Germany via Baltic Sea (gas)
  // -------------------------------------------------------------------------
  {
    name: 'Nord Stream 1',
    type: 'gas',
    capacity: '55 bcm/yr',
    points: [
      [59.95, 30.25],   // Vyborg, Russia
      [59.80, 28.50],   // Gulf of Finland
      [59.50, 24.80],   // North of Estonia
      [58.00, 20.00],   // Central Baltic
      [55.50, 14.50],   // Bornholm area
      [54.40, 13.10],   // Greifswald approach
      [54.14, 13.38],   // Lubmin, Germany
    ],
  },

  // -------------------------------------------------------------------------
  // Nord Stream 2 — Russia to Germany via Baltic Sea (gas)
  // -------------------------------------------------------------------------
  {
    name: 'Nord Stream 2',
    type: 'gas',
    capacity: '55 bcm/yr',
    points: [
      [60.03, 29.18],   // Ust-Luga, Russia
      [59.70, 27.50],   // Gulf of Finland
      [59.20, 23.50],   // South of Finland
      [57.50, 19.80],   // East of Gotland
      [55.30, 15.50],   // South of Bornholm
      [54.30, 13.50],   // Lubmin approach
      [54.14, 13.38],   // Lubmin, Germany
    ],
  },

  // -------------------------------------------------------------------------
  // TurkStream — Russia to Turkey via Black Sea (gas)
  // -------------------------------------------------------------------------
  {
    name: 'TurkStream',
    type: 'gas',
    capacity: '31.5 bcm/yr',
    points: [
      [44.60, 37.85],   // Anapa, Russia
      [43.80, 36.50],   // Black Sea (NE)
      [43.00, 34.00],   // Central Black Sea
      [42.20, 31.50],   // Southern Black Sea
      [41.70, 29.50],   // Kıyıköy approach
      [41.64, 28.10],   // Kıyıköy, Turkey
    ],
  },

  // -------------------------------------------------------------------------
  // Druzhba — Russia to Europe via Belarus/Poland/Ukraine (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Druzhba Pipeline',
    type: 'oil',
    capacity: '1.2 mbd',
    points: [
      [54.95, 52.45],   // Almetyevsk, Russia
      [53.90, 49.10],   // Samara region
      [53.20, 45.00],   // Penza region
      [52.60, 39.60],   // Bryansk approach
      [53.10, 34.30],   // Bryansk, Russia
      [53.70, 30.35],   // Mozyr, Belarus (junction)
      // Northern branch
      [52.10, 23.70],   // Brest, Belarus
      [52.40, 20.90],   // Płock, Poland
      [52.50, 14.55],   // Schwedt, Germany
    ],
  },

  // -------------------------------------------------------------------------
  // BTC — Baku–Tbilisi–Ceyhan (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Baku-Tbilisi-Ceyhan (BTC)',
    type: 'oil',
    capacity: '1.2 mbd',
    points: [
      [40.37, 49.85],   // Sangachal, Azerbaijan
      [40.70, 47.80],   // Western Azerbaijan
      [41.20, 45.50],   // Georgia border
      [41.69, 44.80],   // Tbilisi, Georgia
      [41.60, 43.50],   // Western Georgia
      [41.10, 43.00],   // Turkey border
      [40.20, 40.50],   // Erzurum region
      [39.00, 37.50],   // Eastern Anatolia
      [37.50, 36.00],   // Osmaniye region
      [36.83, 35.82],   // Ceyhan, Turkey
    ],
  },

  // -------------------------------------------------------------------------
  // TANAP — Trans-Anatolian Natural Gas Pipeline
  // -------------------------------------------------------------------------
  {
    name: 'TANAP',
    type: 'gas',
    capacity: '16 bcm/yr',
    points: [
      [40.37, 49.85],   // Sangachal, Azerbaijan
      [41.20, 45.50],   // Georgia
      [41.69, 44.80],   // Tbilisi
      [41.20, 43.10],   // Turkey border
      [40.00, 40.50],   // Erzurum, Turkey
      [39.50, 37.50],   // Sivas region
      [39.90, 32.85],   // Eskişehir region
      [40.20, 29.00],   // İpsala/Greece border
    ],
  },

  // -------------------------------------------------------------------------
  // TAP — Trans-Adriatic Pipeline (gas)
  // -------------------------------------------------------------------------
  {
    name: 'TAP',
    type: 'gas',
    capacity: '10 bcm/yr',
    points: [
      [40.20, 29.00],   // Turkey-Greece border
      [40.85, 24.00],   // Thessaloniki region
      [40.65, 20.85],   // Kastoria, Greece
      [40.50, 20.10],   // Albania border
      [40.95, 19.80],   // Albania
      [40.70, 19.40],   // Fier, Albania (shore)
      [41.00, 18.50],   // Adriatic Sea
      [41.10, 17.20],   // Southern Adriatic
      [40.83, 16.87],   // San Foca, Italy
    ],
  },

  // -------------------------------------------------------------------------
  // Kirkuk–Ceyhan (East–West) Pipeline (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Kirkuk-Ceyhan Pipeline',
    type: 'oil',
    capacity: '1.6 mbd',
    points: [
      [35.47, 44.39],   // Kirkuk, Iraq
      [36.30, 43.50],   // Northern Iraq
      [36.85, 42.50],   // Mosul area
      [37.10, 41.20],   // Iraq-Turkey border
      [37.80, 40.20],   // SE Turkey
      [38.50, 38.00],   // Eastern Turkey
      [37.50, 36.00],   // Osmaniye
      [36.83, 35.82],   // Ceyhan terminal, Turkey
    ],
  },

  // -------------------------------------------------------------------------
  // ESPO — East Siberia–Pacific Ocean Pipeline (oil)
  // -------------------------------------------------------------------------
  {
    name: 'ESPO Pipeline',
    type: 'oil',
    capacity: '1.6 mbd',
    points: [
      [56.85, 105.75],  // Taishet, Siberia
      [55.50, 109.00],  // Bratsk region
      [52.50, 113.50],  // Chita region
      [51.80, 118.00],  // Zabaykalsk region
      [50.50, 125.00],  // Amur region
      [48.50, 131.90],  // Khabarovsk region
      [47.30, 134.50],  // Southern Khabarovsk
      [46.90, 135.10],  // Kozmino approach
      [42.75, 133.04],  // Kozmino, Primorsky
    ],
  },

  // -------------------------------------------------------------------------
  // Keystone XL — Canada to US Gulf Coast (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Keystone XL',
    type: 'oil',
    capacity: '830 kbd',
    points: [
      [52.27, -110.00], // Hardisty, Alberta
      [50.50, -109.00], // Southern Alberta
      [49.00, -108.50], // US-Canada border
      [48.00, -107.50], // Montana
      [45.50, -105.50], // Montana/S. Dakota border
      [42.50, -101.00], // Nebraska Sandhills
      [40.80, -99.00],  // Central Nebraska
      [39.50, -97.50],  // Kansas
      [37.00, -97.00],  // S Kansas / Cushing area
      [36.00, -97.00],  // Cushing, Oklahoma
      [33.00, -97.00],  // North Texas
      [29.90, -95.50],  // Houston/Port Arthur, TX
    ],
  },

  // -------------------------------------------------------------------------
  // Trans Mountain — Alberta to BC coast (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Trans Mountain Pipeline',
    type: 'oil',
    capacity: '890 kbd',
    points: [
      [53.55, -113.49], // Edmonton, Alberta
      [52.90, -115.00], // Jasper approach
      [52.15, -116.60], // Rocky Mountains
      [51.40, -117.50], // BC interior
      [51.05, -118.80], // Kamloops approach
      [50.68, -120.33], // Kamloops, BC
      [49.90, -121.50], // Fraser Valley
      [49.24, -122.98], // Burnaby, BC
    ],
  },

  // -------------------------------------------------------------------------
  // TAPI — Turkmenistan–Afghanistan–Pakistan–India (gas)
  // -------------------------------------------------------------------------
  {
    name: 'TAPI Pipeline',
    type: 'gas',
    capacity: '33 bcm/yr',
    points: [
      [38.50, 62.60],   // Galkynysh, Turkmenistan
      [36.70, 63.50],   // Southern Turkmenistan
      [35.90, 63.80],   // Afghan border
      [34.50, 65.50],   // Central Afghanistan
      [32.50, 66.00],   // Kandahar region
      [30.50, 66.50],   // Quetta, Pakistan
      [28.50, 68.50],   // Sindh, Pakistan
      [27.00, 69.50],   // Multan region
      [25.50, 70.00],   // India border approach
      [24.87, 71.00],   // Fazilka, India
    ],
  },

  // -------------------------------------------------------------------------
  // Power of Siberia — Russia to China (gas)
  // -------------------------------------------------------------------------
  {
    name: 'Power of Siberia',
    type: 'gas',
    capacity: '38 bcm/yr',
    points: [
      [62.50, 114.00],  // Chayandinskoye field, Yakutia
      [60.00, 118.00],  // Central Yakutia
      [56.00, 121.00],  // Lena River crossing
      [53.00, 127.00],  // Amur Oblast
      [50.40, 128.50],  // Blagoveshchensk, Russia
      [50.27, 127.53],  // Heihe, China (border crossing)
      [48.00, 125.00],  // Heilongjiang, China
      [45.75, 126.65],  // Harbin, China
      [41.80, 123.40],  // Shenyang, China
      [40.00, 117.00],  // Hebei, China
      [39.90, 116.40],  // Beijing approach
    ],
  },

  // -------------------------------------------------------------------------
  // Yamal–Europe — Russia to Europe via Belarus/Poland (gas)
  // -------------------------------------------------------------------------
  {
    name: 'Yamal-Europe Pipeline',
    type: 'gas',
    capacity: '33 bcm/yr',
    points: [
      [67.50, 72.00],   // Yamal Peninsula origin
      [63.00, 65.00],   // Western Siberia
      [58.00, 56.00],   // Perm region
      [55.80, 49.00],   // Kazan area
      [55.00, 42.00],   // Central Russia
      [54.50, 34.00],   // Smolensk region
      [53.90, 30.35],   // Belarus (Minsk region)
      [53.10, 27.55],   // Minsk, Belarus
      [52.50, 23.70],   // Brest, Belarus
      [52.20, 21.00],   // Warsaw, Poland
      [52.50, 14.55],   // Frankfurt (Oder) / Mallnow, Germany
    ],
  },

  // -------------------------------------------------------------------------
  // Strait of Hormuz Undersea Infrastructure (oil)
  // -------------------------------------------------------------------------
  {
    name: 'Strait of Hormuz Oil Transit',
    type: 'oil',
    capacity: '21 mbd transit',
    points: [
      [29.50, 49.50],   // Kuwait / N Persian Gulf
      [28.50, 50.50],   // Bahrain area
      [27.00, 51.50],   // Qatar / UAE area
      [26.20, 52.50],   // Abu Dhabi coastline
      [26.00, 55.00],   // Fujairah approach
      [26.50, 56.30],   // Strait of Hormuz (narrow)
      [25.50, 57.00],   // Gulf of Oman (west)
      [24.50, 58.50],   // Gulf of Oman (east)
      [23.50, 60.00],   // Arabian Sea approach
    ],
  },

  // -------------------------------------------------------------------------
  // South Caucasus Pipeline (Baku–Tbilisi–Erzurum / SCP)
  // -------------------------------------------------------------------------
  {
    name: 'South Caucasus Pipeline (SCP)',
    type: 'gas',
    capacity: '25 bcm/yr',
    points: [
      [40.37, 49.85],   // Sangachal, Azerbaijan
      [40.80, 48.00],   // Central Azerbaijan
      [41.10, 46.00],   // Western Azerbaijan
      [41.70, 44.80],   // Tbilisi, Georgia
      [41.20, 43.10],   // Turkey border
      [39.90, 41.27],   // Erzurum, Turkey
    ],
  },
];
