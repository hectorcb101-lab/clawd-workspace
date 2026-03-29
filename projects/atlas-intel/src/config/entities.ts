// ============================================================================
// Atlas Intel — Entity Registry
// ============================================================================

import type { Entity } from '@/types/index';

// ---------------------------------------------------------------------------
// Entity Definitions
// ---------------------------------------------------------------------------

export const ENTITIES: Entity[] = [
  // =========================================================================
  // STATE ACTORS
  // =========================================================================
  {
    id: 'us',
    name: 'United States',
    aliases: ['USA', 'US', 'America', 'Washington', 'United States of America'],
    type: 'state',
    sector: 'government',
    keywords: ['white house', 'state department', 'pentagon', 'capitol hill', 'oval office'],
  },
  {
    id: 'cn',
    name: 'China',
    aliases: ['PRC', 'Beijing', "People's Republic of China"],
    type: 'state',
    sector: 'government',
    keywords: ['ccp', 'politburo', 'great hall', 'zhongnanhai', 'communist party'],
  },
  {
    id: 'ru',
    name: 'Russia',
    aliases: ['Russian Federation', 'Moscow'],
    type: 'state',
    sector: 'government',
    keywords: ['kremlin', 'duma', 'russian government'],
  },
  {
    id: 'gb',
    name: 'United Kingdom',
    aliases: ['UK', 'Britain', 'Great Britain', 'England'],
    type: 'state',
    sector: 'government',
    keywords: ['downing street', 'parliament', 'whitehall', 'westminster'],
  },
  {
    id: 'fr',
    name: 'France',
    aliases: ['French Republic', 'Paris'],
    type: 'state',
    sector: 'government',
    keywords: ['elysee', 'quai d\'orsay', 'national assembly'],
  },
  {
    id: 'de',
    name: 'Germany',
    aliases: ['Federal Republic of Germany', 'Berlin', 'Deutschland'],
    type: 'state',
    sector: 'government',
    keywords: ['bundestag', 'bundeswehr', 'chancellery'],
  },
  {
    id: 'jp',
    name: 'Japan',
    aliases: ['Tokyo', 'Nippon'],
    type: 'state',
    sector: 'government',
    keywords: ['diet', 'kantei', 'jsdf'],
  },
  {
    id: 'in',
    name: 'India',
    aliases: ['Republic of India', 'New Delhi', 'Bharat'],
    type: 'state',
    sector: 'government',
    keywords: ['lok sabha', 'rajya sabha', 'south block'],
  },
  {
    id: 'pk',
    name: 'Pakistan',
    aliases: ['Islamic Republic of Pakistan', 'Islamabad'],
    type: 'state',
    sector: 'government',
    keywords: ['rawalpindi', 'isi', 'national assembly'],
  },
  {
    id: 'il',
    name: 'Israel',
    aliases: ['State of Israel', 'Tel Aviv', 'Jerusalem'],
    type: 'state',
    sector: 'government',
    keywords: ['knesset', 'mossad', 'shin bet'],
  },
  {
    id: 'ir',
    name: 'Iran',
    aliases: ['Islamic Republic of Iran', 'Tehran', 'Persia'],
    type: 'state',
    sector: 'government',
    keywords: ['supreme leader', 'majlis', 'guardian council'],
  },
  {
    id: 'sa',
    name: 'Saudi Arabia',
    aliases: ['Kingdom of Saudi Arabia', 'KSA', 'Riyadh'],
    type: 'state',
    sector: 'government',
    keywords: ['house of saud', 'vision 2030', 'neom'],
  },
  {
    id: 'tr',
    name: 'Turkey',
    aliases: ['Republic of Türkiye', 'Türkiye', 'Ankara'],
    type: 'state',
    sector: 'government',
    keywords: ['grand national assembly', 'akp'],
  },
  {
    id: 'kp',
    name: 'North Korea',
    aliases: ['DPRK', 'Pyongyang', "Democratic People's Republic of Korea"],
    type: 'state',
    sector: 'government',
    keywords: ['korean workers party', 'juche', 'yongbyon'],
  },
  {
    id: 'kr',
    name: 'South Korea',
    aliases: ['Republic of Korea', 'ROK', 'Seoul'],
    type: 'state',
    sector: 'government',
    keywords: ['blue house', 'yongsan'],
  },
  {
    id: 'ua',
    name: 'Ukraine',
    aliases: ['Kyiv', 'Kiev'],
    type: 'state',
    sector: 'government',
    keywords: ['verkhovna rada', 'bankova'],
  },
  {
    id: 'sy',
    name: 'Syria',
    aliases: ['Syrian Arab Republic', 'Damascus'],
    type: 'state',
    sector: 'government',
    keywords: ['baath', 'assad regime'],
  },
  {
    id: 'ye',
    name: 'Yemen',
    aliases: ['Republic of Yemen', 'Sanaa', "Sana'a", 'Aden'],
    type: 'state',
    sector: 'government',
    keywords: ['yemeni government'],
  },

  // =========================================================================
  // MILITARY
  // =========================================================================
  {
    id: 'nato',
    name: 'NATO',
    aliases: ['North Atlantic Treaty Organization', 'Atlantic Alliance'],
    type: 'military',
    keywords: ['article 5', 'collective defense', 'saceur', 'shape', 'allied command'],
  },
  {
    id: 'us-military',
    name: 'US Military',
    aliases: [
      'USAF', 'US Navy', 'US Army', 'USMC', 'CENTCOM', 'EUCOM', 'INDOPACOM',
      'United States Armed Forces', 'US Air Force', 'US Marine Corps',
      'AFRICOM', 'SOCOM', 'STRATCOM', 'SPACECOM',
    ],
    type: 'military',
    country: 'US',
    keywords: [
      'b-52', 'carrier strike group', 'f-35', 'f-22', 'global hawk',
      'uss', 'fort liberty', 'camp lejeune', 'joint chiefs',
    ],
  },
  {
    id: 'pla',
    name: 'PLA',
    aliases: [
      "People's Liberation Army", 'PLAN', 'PLAAF', 'PLARF',
      "People's Liberation Army Navy", "People's Liberation Army Air Force",
      'PLA Rocket Force',
    ],
    type: 'military',
    country: 'CN',
    keywords: ['j-20', 'type 055', 'df-41', 'liaoning', 'shandong', 'fujian', 'eastern theater command'],
  },
  {
    id: 'ru-military',
    name: 'Russian Armed Forces',
    aliases: ['VKS', 'VMF', 'Russian Navy', 'Russian Air Force', 'Spetsnaz'],
    type: 'military',
    country: 'RU',
    keywords: ['su-57', 'kalibr', 's-400', 's-300', 'iskander', 'admiral kuznetsov', 'topol'],
  },
  {
    id: 'idf',
    name: 'IDF',
    aliases: ['Israel Defense Forces', 'Israeli Military', 'Tzahal'],
    type: 'military',
    country: 'IL',
    keywords: ['iron dome', 'merkava', 'david\'s sling', 'arrow', 'iron beam', 'sayeret matkal'],
  },
  {
    id: 'irgc',
    name: 'IRGC',
    aliases: ['Islamic Revolutionary Guard Corps', 'Quds Force', 'Pasdaran', 'Sepah'],
    type: 'military',
    country: 'IR',
    keywords: ['shaheed', 'ballistic missile', 'fateh', 'emad', 'proxy forces'],
  },
  {
    id: 'wagner',
    name: 'Wagner Group',
    aliases: ['Wagner PMC', 'Africa Corps', 'Wagner'],
    type: 'military',
    country: 'RU',
    keywords: ['pmc', 'private military', 'prigozhin', 'africa corps'],
  },
  {
    id: 'hezbollah',
    name: 'Hezbollah',
    aliases: ['Hizballah', 'Party of God'],
    type: 'military',
    country: 'LB',
    keywords: ['nasrallah', 'dahiyeh', 'radwan force', 'southern lebanon'],
  },
  {
    id: 'hamas',
    name: 'Hamas',
    aliases: ['Islamic Resistance Movement', 'Izz ad-Din al-Qassam Brigades'],
    type: 'military',
    country: 'PS',
    keywords: ['al-qassam', 'gaza', 'sinwar', 'haniyeh'],
  },
  {
    id: 'houthis',
    name: 'Houthis',
    aliases: ['Ansar Allah', 'Ansarallah', 'Houthi Movement'],
    type: 'military',
    country: 'YE',
    keywords: ['red sea attacks', 'bab el-mandeb', 'anti-ship missile'],
  },

  // =========================================================================
  // CORPORATIONS — Defense
  // =========================================================================
  {
    id: 'lockheed-martin',
    name: 'Lockheed Martin',
    aliases: ['LMT', 'Lockheed'],
    type: 'corporation',
    sector: 'defense',
    country: 'US',
    keywords: ['f-35', 'f-22', 'c-130', 'sikorsky', 'skunk works', 'thaad'],
  },
  {
    id: 'raytheon',
    name: 'Raytheon',
    aliases: ['RTX', 'Raytheon Technologies', 'Pratt & Whitney'],
    type: 'corporation',
    sector: 'defense',
    country: 'US',
    keywords: ['patriot missile', 'stinger', 'tomahawk', 'sm-3'],
  },
  {
    id: 'boeing',
    name: 'Boeing',
    aliases: ['BA', 'Boeing Defense'],
    type: 'corporation',
    sector: 'defense',
    country: 'US',
    keywords: ['b-52', 'f-15', 'p-8', 'kc-46', 'apache', '737', '787'],
  },
  {
    id: 'northrop-grumman',
    name: 'Northrop Grumman',
    aliases: ['NOC', 'Northrop'],
    type: 'corporation',
    sector: 'defense',
    country: 'US',
    keywords: ['b-21', 'b-2', 'global hawk', 'james webb'],
  },
  {
    id: 'bae-systems',
    name: 'BAE Systems',
    aliases: ['BAE'],
    type: 'corporation',
    sector: 'defense',
    country: 'GB',
    keywords: ['tempest', 'typhoon', 'astute class', 'dreadnought'],
  },
  {
    id: 'general-dynamics',
    name: 'General Dynamics',
    aliases: ['GD', 'GDLS', 'Electric Boat'],
    type: 'corporation',
    sector: 'defense',
    country: 'US',
    keywords: ['abrams', 'stryker', 'virginia class', 'columbia class', 'gulfstream'],
  },

  // =========================================================================
  // CORPORATIONS — Energy
  // =========================================================================
  {
    id: 'aramco',
    name: 'Aramco',
    aliases: ['Saudi Aramco', 'Saudi Arabian Oil Company'],
    type: 'corporation',
    sector: 'energy',
    country: 'SA',
    keywords: ['ghawar', 'ras tanura', 'abqaiq'],
  },
  {
    id: 'gazprom',
    name: 'Gazprom',
    aliases: ['Gazprom Neft'],
    type: 'corporation',
    sector: 'energy',
    country: 'RU',
    keywords: ['nord stream', 'power of siberia', 'yamal'],
  },
  {
    id: 'cnooc',
    name: 'CNOOC',
    aliases: ['China National Offshore Oil Corporation'],
    type: 'corporation',
    sector: 'energy',
    country: 'CN',
    keywords: ['south china sea oil', 'offshore drilling'],
  },
  {
    id: 'shell',
    name: 'Shell',
    aliases: ['Royal Dutch Shell', 'Shell plc'],
    type: 'corporation',
    sector: 'energy',
    country: 'NL',
    keywords: ['lng', 'prelude', 'north sea'],
  },
  {
    id: 'exxonmobil',
    name: 'ExxonMobil',
    aliases: ['Exxon', 'XOM', 'Exxon Mobil'],
    type: 'corporation',
    sector: 'energy',
    country: 'US',
    keywords: ['permian basin', 'guyana', 'beaumont'],
  },
  {
    id: 'bp',
    name: 'BP',
    aliases: ['British Petroleum', 'BP plc'],
    type: 'corporation',
    sector: 'energy',
    country: 'GB',
    keywords: ['north sea', 'thunder horse', 'azeri'],
  },

  // =========================================================================
  // CORPORATIONS — Technology / Semiconductor
  // =========================================================================
  {
    id: 'tsmc',
    name: 'TSMC',
    aliases: ['Taiwan Semiconductor', 'Taiwan Semiconductor Manufacturing Company'],
    type: 'corporation',
    sector: 'semiconductor',
    country: 'TW',
    keywords: ['3nm', '5nm', 'chip fabrication', 'foundry'],
  },
  {
    id: 'samsung',
    name: 'Samsung',
    aliases: ['Samsung Electronics', 'Samsung Semiconductor'],
    type: 'corporation',
    sector: 'semiconductor',
    country: 'KR',
    keywords: ['memory chips', 'hbm', 'nand', 'foundry'],
  },
  {
    id: 'intel',
    name: 'Intel',
    aliases: ['Intel Corporation', 'INTC'],
    type: 'corporation',
    sector: 'semiconductor',
    country: 'US',
    keywords: ['chips act', 'fab', 'x86', 'foundry'],
  },
  {
    id: 'nvidia',
    name: 'Nvidia',
    aliases: ['NVDA', 'Nvidia Corporation'],
    type: 'corporation',
    sector: 'semiconductor',
    country: 'US',
    keywords: ['gpu', 'a100', 'h100', 'cuda', 'ai chips'],
  },

  // =========================================================================
  // CORPORATIONS — Space
  // =========================================================================
  {
    id: 'spacex',
    name: 'SpaceX',
    aliases: ['Space Exploration Technologies'],
    type: 'corporation',
    sector: 'space',
    country: 'US',
    keywords: ['falcon 9', 'starship', 'raptor', 'boca chica', 'cape canaveral'],
  },
  {
    id: 'starlink',
    name: 'Starlink',
    aliases: ['Starlink Internet'],
    type: 'corporation',
    sector: 'space',
    country: 'US',
    keywords: ['satellite internet', 'leo constellation', 'low earth orbit'],
  },

  // =========================================================================
  // ORGANIZATIONS — International
  // =========================================================================
  {
    id: 'un',
    name: 'United Nations',
    aliases: ['UN'],
    type: 'organization',
    keywords: ['security council', 'general assembly', 'unsc', 'unga', 'un charter'],
  },
  {
    id: 'eu',
    name: 'European Union',
    aliases: ['EU', 'Brussels'],
    type: 'organization',
    keywords: ['european commission', 'european council', 'european parliament', 'eurozone'],
  },
  {
    id: 'iaea',
    name: 'IAEA',
    aliases: ['International Atomic Energy Agency'],
    type: 'organization',
    keywords: ['nuclear inspections', 'safeguards', 'nuclear watchdog'],
  },
  {
    id: 'who',
    name: 'WHO',
    aliases: ['World Health Organization'],
    type: 'organization',
    keywords: ['pandemic', 'health emergency', 'pheic', 'global health'],
  },
  {
    id: 'unhcr',
    name: 'UNHCR',
    aliases: ['UN Refugee Agency', 'United Nations High Commissioner for Refugees'],
    type: 'organization',
    keywords: ['refugees', 'displaced persons', 'asylum'],
  },
  {
    id: 'icc',
    name: 'ICC',
    aliases: ['International Criminal Court', 'The Hague'],
    type: 'organization',
    keywords: ['war crimes', 'crimes against humanity', 'genocide', 'arrest warrant'],
  },
  {
    id: 'opcw',
    name: 'OPCW',
    aliases: ['Organisation for the Prohibition of Chemical Weapons'],
    type: 'organization',
    keywords: ['chemical weapons', 'cwc', 'nerve agent', 'chemical attack'],
  },
  {
    id: 'wto',
    name: 'WTO',
    aliases: ['World Trade Organization'],
    type: 'organization',
    keywords: ['tariffs', 'trade disputes', 'trade sanctions'],
  },
  {
    id: 'imf',
    name: 'IMF',
    aliases: ['International Monetary Fund'],
    type: 'organization',
    keywords: ['bailout', 'special drawing rights', 'sdr', 'debt relief'],
  },
  {
    id: 'world-bank',
    name: 'World Bank',
    aliases: ['IBRD', 'International Bank for Reconstruction and Development'],
    type: 'organization',
    keywords: ['development loans', 'poverty reduction'],
  },
  {
    id: 'opec',
    name: 'OPEC',
    aliases: ['Organization of the Petroleum Exporting Countries', 'OPEC+'],
    type: 'organization',
    keywords: ['oil production', 'oil cartel', 'production cuts', 'oil quota'],
  },
  {
    id: 'brics',
    name: 'BRICS',
    aliases: ['BRICS+'],
    type: 'organization',
    keywords: ['new development bank', 'brics expansion', 'multipolar'],
  },
  {
    id: 'g7',
    name: 'G7',
    aliases: ['Group of Seven', 'G-7'],
    type: 'organization',
    keywords: ['g7 summit', 'industrialized nations'],
  },
  {
    id: 'asean',
    name: 'ASEAN',
    aliases: ['Association of Southeast Asian Nations'],
    type: 'organization',
    keywords: ['southeast asia', 'asean summit', 'asean way'],
  },
  {
    id: 'african-union',
    name: 'African Union',
    aliases: ['AU'],
    type: 'organization',
    keywords: ['addis ababa', 'african peace', 'au summit'],
  },
  {
    id: 'icrc',
    name: 'Red Cross',
    aliases: ['ICRC', 'International Committee of the Red Cross', 'Red Crescent'],
    type: 'organization',
    keywords: ['humanitarian aid', 'geneva conventions', 'humanitarian law'],
  },

  // =========================================================================
  // LEADERS
  // =========================================================================
  {
    id: 'biden',
    name: 'Joe Biden',
    aliases: ['Biden', 'President Biden', 'POTUS'],
    type: 'leader',
    country: 'US',
    keywords: ['white house', 'oval office', 'us president'],
  },
  {
    id: 'putin',
    name: 'Vladimir Putin',
    aliases: ['Putin', 'President Putin'],
    type: 'leader',
    country: 'RU',
    keywords: ['kremlin', 'russian president'],
  },
  {
    id: 'xi-jinping',
    name: 'Xi Jinping',
    aliases: ['Xi', 'President Xi', 'General Secretary Xi'],
    type: 'leader',
    country: 'CN',
    keywords: ['ccp chairman', 'chinese president', 'paramount leader'],
  },
  {
    id: 'zelensky',
    name: 'Volodymyr Zelensky',
    aliases: ['Zelensky', 'Zelenskyy', 'President Zelensky'],
    type: 'leader',
    country: 'UA',
    keywords: ['ukrainian president', 'bankova'],
  },
  {
    id: 'netanyahu',
    name: 'Benjamin Netanyahu',
    aliases: ['Netanyahu', 'Bibi', 'PM Netanyahu'],
    type: 'leader',
    country: 'IL',
    keywords: ['israeli prime minister', 'likud'],
  },
  {
    id: 'khamenei',
    name: 'Ali Khamenei',
    aliases: ['Khamenei', 'Supreme Leader Khamenei', 'Ayatollah Khamenei'],
    type: 'leader',
    country: 'IR',
    keywords: ['supreme leader', 'rahbar'],
  },
  {
    id: 'kim-jong-un',
    name: 'Kim Jong Un',
    aliases: ['Kim', 'Chairman Kim', 'Marshal Kim'],
    type: 'leader',
    country: 'KP',
    keywords: ['north korean leader', 'supreme commander'],
  },
  {
    id: 'modi',
    name: 'Narendra Modi',
    aliases: ['Modi', 'PM Modi', 'Prime Minister Modi'],
    type: 'leader',
    country: 'IN',
    keywords: ['indian prime minister', 'bjp'],
  },
  {
    id: 'erdogan',
    name: 'Recep Tayyip Erdogan',
    aliases: ['Erdogan', 'Erdoğan', 'President Erdogan'],
    type: 'leader',
    country: 'TR',
    keywords: ['turkish president', 'akp'],
  },
  {
    id: 'mbs',
    name: 'Mohammed bin Salman',
    aliases: ['MBS', 'Crown Prince Mohammed', 'Prince Mohammed'],
    type: 'leader',
    country: 'SA',
    keywords: ['saudi crown prince', 'vision 2030'],
  },
  {
    id: 'macron',
    name: 'Emmanuel Macron',
    aliases: ['Macron', 'President Macron'],
    type: 'leader',
    country: 'FR',
    keywords: ['french president', 'elysee'],
  },
  {
    id: 'scholz',
    name: 'Olaf Scholz',
    aliases: ['Scholz', 'Chancellor Scholz'],
    type: 'leader',
    country: 'DE',
    keywords: ['german chancellor', 'spd'],
  },

  // =========================================================================
  // GROUPS — Terrorist / Insurgent
  // =========================================================================
  {
    id: 'isis',
    name: 'ISIS',
    aliases: [
      'Islamic State', 'ISIL', 'IS', 'Daesh', 'Islamic State of Iraq and Syria',
      'Islamic State of Iraq and the Levant',
    ],
    type: 'group',
    keywords: ['caliphate', 'isis-k', 'islamic state', 'wilayat'],
  },
  {
    id: 'al-qaeda',
    name: 'Al-Qaeda',
    aliases: ['AQ', 'al-Qa\'ida', 'AQAP', 'AQIM', 'Al Qaeda'],
    type: 'group',
    keywords: ['jihad', 'arabian peninsula', 'islamic maghreb'],
  },
  {
    id: 'al-shabaab',
    name: 'Al-Shabaab',
    aliases: ['Harakat al-Shabaab al-Mujahideen', 'al Shabaab'],
    type: 'group',
    country: 'SO',
    keywords: ['somalia', 'mogadishu', 'horn of africa'],
  },
  {
    id: 'boko-haram',
    name: 'Boko Haram',
    aliases: ['Jamā\'at Ahl as-Sunnah lid-Da\'wah wa\'l-Jihād', 'ISWAP'],
    type: 'group',
    country: 'NG',
    keywords: ['lake chad', 'northeast nigeria', 'maiduguri'],
  },
  {
    id: 'taliban',
    name: 'Taliban',
    aliases: ['Islamic Emirate of Afghanistan', 'Afghan Taliban', 'IEA'],
    type: 'group',
    country: 'AF',
    keywords: ['kabul', 'kandahar', 'sharia', 'afghan government'],
  },
];

// ---------------------------------------------------------------------------
// Entity Map — id → Entity
// ---------------------------------------------------------------------------

export const ENTITY_MAP: Map<string, Entity> = new Map(
  ENTITIES.map((e) => [e.id, e]),
);

// ---------------------------------------------------------------------------
// Search Utilities
// ---------------------------------------------------------------------------

/**
 * Find entities whose name, aliases, or keywords match the given text
 * (case-insensitive substring search).
 */
export function findEntitiesByKeyword(text: string): Entity[] {
  const lower = text.toLowerCase();
  return ENTITIES.filter((entity) => {
    if (entity.name.toLowerCase().includes(lower)) return true;
    if (entity.aliases.some((a) => a.toLowerCase().includes(lower))) return true;
    if (entity.keywords.some((k) => k.toLowerCase().includes(lower))) return true;
    return false;
  });
}

/**
 * Find all entities belonging to a given sector (case-insensitive).
 */
export function findEntitiesBySector(sector: string): Entity[] {
  const lower = sector.toLowerCase();
  return ENTITIES.filter((e) => e.sector?.toLowerCase() === lower);
}
