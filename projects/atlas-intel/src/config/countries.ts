// ============================================================================
// Atlas Intel — Monitored Countries Configuration
// ============================================================================

// @/types/index (relatively: ../types/index)
import type { MonitoredCountry } from '@/types/index';

// ---------------------------------------------------------------------------
// Monitored Countries — 24 Key Geopolitical Hotspots
// ---------------------------------------------------------------------------

export const MONITORED_COUNTRIES: MonitoredCountry[] = [
  // ---- Conflict Zones ----
  {
    code: 'UA',
    name: 'Ukraine',
    flag: '🇺🇦',
    aliases: ['ukr', 'ukrainian', 'kyiv', 'kiev', 'zelensky'],
    isConflictZone: true,
    floorScore: 55,
    region: 'europe',
  },
  {
    code: 'RU',
    name: 'Russia',
    flag: '🇷🇺',
    aliases: ['russian', 'moscow', 'kremlin', 'putin'],
    isConflictZone: true,
    floorScore: 45,
    region: 'europe',
  },
  {
    code: 'IL',
    name: 'Israel',
    flag: '🇮🇱',
    aliases: ['israeli', 'tel aviv', 'jerusalem', 'idf', 'netanyahu'],
    isConflictZone: true,
    floorScore: 50,
    region: 'mena',
  },
  {
    code: 'PS',
    name: 'Palestine',
    flag: '🇵🇸',
    aliases: ['palestinian', 'gaza', 'west bank', 'hamas'],
    isConflictZone: true,
    floorScore: 55,
    region: 'mena',
  },
  {
    code: 'SY',
    name: 'Syria',
    flag: '🇸🇾',
    aliases: ['syrian', 'damascus', 'assad'],
    isConflictZone: true,
    floorScore: 50,
    region: 'mena',
  },
  {
    code: 'YE',
    name: 'Yemen',
    flag: '🇾🇪',
    aliases: ['yemeni', 'sanaa', 'houthi', 'ansar allah'],
    isConflictZone: true,
    floorScore: 50,
    region: 'mena',
  },
  {
    code: 'MM',
    name: 'Myanmar',
    flag: '🇲🇲',
    aliases: ['burmese', 'burma', 'naypyidaw'],
    isConflictZone: true,
    floorScore: 45,
    region: 'asia',
  },
  {
    code: 'SD',
    name: 'Sudan',
    flag: '🇸🇩',
    aliases: ['sudanese', 'khartoum', 'rsf'],
    isConflictZone: true,
    floorScore: 50,
    region: 'africa',
  },
  {
    code: 'SO',
    name: 'Somalia',
    flag: '🇸🇴',
    aliases: ['somali', 'mogadishu', 'al-shabaab'],
    isConflictZone: true,
    floorScore: 45,
    region: 'africa',
  },

  // ---- Non-Conflict Hotspots ----
  {
    code: 'CN',
    name: 'China',
    flag: '🇨🇳',
    aliases: ['chinese', 'beijing', 'prc', 'xi jinping'],
    isConflictZone: false,
    floorScore: 30,
    region: 'asia',
  },
  {
    code: 'TW',
    name: 'Taiwan',
    flag: '🇹🇼',
    aliases: ['taiwanese', 'taipei', 'roc'],
    isConflictZone: false,
    floorScore: 35,
    region: 'asia',
  },
  {
    code: 'IR',
    name: 'Iran',
    flag: '🇮🇷',
    aliases: ['iranian', 'tehran', 'persian', 'irgc'],
    isConflictZone: false,
    floorScore: 40,
    region: 'mena',
  },
  {
    code: 'KP',
    name: 'North Korea',
    flag: '🇰🇵',
    aliases: ['dprk', 'pyongyang', 'kim jong un'],
    isConflictZone: false,
    floorScore: 40,
    region: 'asia',
  },
  {
    code: 'KR',
    name: 'South Korea',
    flag: '🇰🇷',
    aliases: ['korean', 'seoul', 'rok'],
    isConflictZone: false,
    floorScore: 15,
    region: 'asia',
  },
  {
    code: 'JP',
    name: 'Japan',
    flag: '🇯🇵',
    aliases: ['japanese', 'tokyo'],
    isConflictZone: false,
    floorScore: 10,
    region: 'asia',
  },
  {
    code: 'IN',
    name: 'India',
    flag: '🇮🇳',
    aliases: ['indian', 'delhi', 'new delhi', 'modi'],
    isConflictZone: false,
    floorScore: 25,
    region: 'asia',
  },
  {
    code: 'PK',
    name: 'Pakistan',
    flag: '🇵🇰',
    aliases: ['pakistani', 'islamabad'],
    isConflictZone: false,
    floorScore: 30,
    region: 'asia',
  },
  {
    code: 'SA',
    name: 'Saudi Arabia',
    flag: '🇸🇦',
    aliases: ['saudi', 'riyadh', 'mbs'],
    isConflictZone: false,
    floorScore: 20,
    region: 'mena',
  },
  {
    code: 'TR',
    name: 'Turkey',
    flag: '🇹🇷',
    aliases: ['turkish', 'ankara', 'istanbul', 'erdogan'],
    isConflictZone: false,
    floorScore: 25,
    region: 'mena',
  },
  {
    code: 'PL',
    name: 'Poland',
    flag: '🇵🇱',
    aliases: ['polish', 'warsaw'],
    isConflictZone: false,
    floorScore: 15,
    region: 'europe',
  },
  {
    code: 'DE',
    name: 'Germany',
    flag: '🇩🇪',
    aliases: ['german', 'berlin'],
    isConflictZone: false,
    floorScore: 10,
    region: 'europe',
  },
  {
    code: 'GB',
    name: 'United Kingdom',
    flag: '🇬🇧',
    aliases: ['british', 'uk', 'london', 'england'],
    isConflictZone: false,
    floorScore: 10,
    region: 'europe',
  },
  {
    code: 'US',
    name: 'United States',
    flag: '🇺🇸',
    aliases: ['american', 'usa', 'washington', 'white house', 'pentagon'],
    isConflictZone: false,
    floorScore: 15,
    region: 'americas',
  },
  {
    code: 'ET',
    name: 'Ethiopia',
    flag: '🇪🇹',
    aliases: ['ethiopian', 'addis ababa', 'tigray'],
    isConflictZone: false,
    floorScore: 35,
    region: 'africa',
  },
];

// ---------------------------------------------------------------------------
// Alias Map — maps every alias (lowercased) → country code
// ---------------------------------------------------------------------------

export const COUNTRY_ALIAS_MAP: Map<string, string> = new Map(
  MONITORED_COUNTRIES.flatMap((c) =>
    c.aliases.map((alias) => [alias.toLowerCase(), c.code] as [string, string]),
  ),
);

// ---------------------------------------------------------------------------
// Lookup Helpers
// ---------------------------------------------------------------------------

/** Find a monitored country by its ISO 3166-1 alpha-2 code (case-insensitive). */
export function getCountryByCode(code: string): MonitoredCountry | undefined {
  const upper = code.toUpperCase();
  return MONITORED_COUNTRIES.find((c) => c.code === upper);
}

/** Find a monitored country by any of its aliases (case-insensitive). */
export function getCountryByAlias(alias: string): MonitoredCountry | undefined {
  const code = COUNTRY_ALIAS_MAP.get(alias.toLowerCase());
  return code ? getCountryByCode(code) : undefined;
}

// ---------------------------------------------------------------------------
// Conflict Zones — country codes currently flagged as active conflict zones
// ---------------------------------------------------------------------------

export const CONFLICT_ZONES: string[] = MONITORED_COUNTRIES
  .filter((c) => c.isConflictZone)
  .map((c) => c.code);
