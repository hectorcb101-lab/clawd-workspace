// ============================================================================
// Atlas Intel — RSS Feed Definitions
// ============================================================================

import type { FeedDefinition } from '@/types/index';

export const FEEDS: FeedDefinition[] = [
  // -------------------------------------------------------------------------
  // Breaking / Wire Services (Tier 1)
  // -------------------------------------------------------------------------
  {
    name: 'Reuters — World',
    url: 'https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best',
    category: 'breaking',
    tier: 1,
    language: 'en',
  },
  {
    name: 'AP News — Top Stories',
    url: 'https://rsshub.app/apnews/topics/apf-topnews',
    category: 'breaking',
    tier: 1,
    language: 'en',
  },
  {
    name: 'AFP — English',
    url: 'https://www.afp.com/en/rss-feeds',
    category: 'breaking',
    tier: 1,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Major Outlets (Tier 1–2)
  // -------------------------------------------------------------------------
  {
    name: 'BBC News — World',
    url: 'https://feeds.bbci.co.uk/news/world/rss.xml',
    category: 'major-outlets',
    tier: 1,
    language: 'en',
  },
  {
    name: 'CNN — World',
    url: 'http://rss.cnn.com/rss/edition_world.rss',
    category: 'major-outlets',
    tier: 1,
    language: 'en',
  },
  {
    name: 'Al Jazeera — English',
    url: 'https://www.aljazeera.com/xml/rss/all.xml',
    category: 'major-outlets',
    tier: 1,
    language: 'en',
  },
  {
    name: 'New York Times — World',
    url: 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    category: 'major-outlets',
    tier: 1,
    language: 'en',
  },
  {
    name: 'The Guardian — World',
    url: 'https://www.theguardian.com/world/rss',
    category: 'major-outlets',
    tier: 1,
    language: 'en',
  },
  {
    name: 'Deutsche Welle — English',
    url: 'https://rss.dw.com/rdf/rss-en-all',
    category: 'major-outlets',
    tier: 2,
    language: 'en',
  },
  {
    name: 'France 24 — English',
    url: 'https://www.france24.com/en/rss',
    category: 'major-outlets',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Defense / Military (Tier 2)
  // -------------------------------------------------------------------------
  {
    name: 'Defense One',
    url: 'https://www.defenseone.com/rss/',
    category: 'defense',
    tier: 2,
    language: 'en',
  },
  {
    name: 'The War Zone',
    url: 'https://www.thedrive.com/the-war-zone/feed',
    category: 'defense',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Janes — News',
    url: 'https://www.janes.com/feeds/news',
    category: 'defense',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Defense News',
    url: 'https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml',
    category: 'defense',
    tier: 2,
    language: 'en',
  },
  {
    name: 'USNI News',
    url: 'https://news.usni.org/feed',
    category: 'defense',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Breaking Defense',
    url: 'https://breakingdefense.com/feed/',
    category: 'defense',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Geopolitics (Tier 2)
  // -------------------------------------------------------------------------
  {
    name: 'Foreign Policy',
    url: 'https://foreignpolicy.com/feed/',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },
  {
    name: 'The Diplomat',
    url: 'https://thediplomat.com/feed/',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },
  {
    name: 'War on the Rocks',
    url: 'https://warontherocks.com/feed/',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },
  {
    name: 'ISW — Institute for the Study of War',
    url: 'https://www.understandingwar.org/rss.xml',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },
  {
    name: 'CSIS — Analysis',
    url: 'https://www.csis.org/analysis/feed',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Brookings Institution',
    url: 'https://www.brookings.edu/feed/',
    category: 'geopolitics',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Cyber Security (Tier 2–3)
  // -------------------------------------------------------------------------
  {
    name: 'The Record by Recorded Future',
    url: 'https://therecord.media/feed/',
    category: 'cyber',
    tier: 2,
    language: 'en',
  },
  {
    name: 'BleepingComputer',
    url: 'https://www.bleepingcomputer.com/feed/',
    category: 'cyber',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Krebs on Security',
    url: 'https://krebsonsecurity.com/feed/',
    category: 'cyber',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Dark Reading',
    url: 'https://www.darkreading.com/rss.xml',
    category: 'cyber',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Threat Post',
    url: 'https://threatpost.com/feed/',
    category: 'cyber',
    tier: 3,
    language: 'en',
  },
  {
    name: 'The Hacker News',
    url: 'https://feeds.feedburner.com/TheHackersNews',
    category: 'cyber',
    tier: 3,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Markets / Finance (Tier 2)
  // -------------------------------------------------------------------------
  {
    name: 'Bloomberg — Markets',
    url: 'https://feeds.bloomberg.com/markets/news.rss',
    category: 'markets',
    tier: 2,
    language: 'en',
  },
  {
    name: 'CNBC — World',
    url: 'https://www.cnbc.com/id/100727362/device/rss/rss.html',
    category: 'markets',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Financial Times — World',
    url: 'https://www.ft.com/rss/home',
    category: 'markets',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Wall Street Journal — World',
    url: 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
    category: 'markets',
    tier: 2,
    language: 'en',
  },
  {
    name: 'MarketWatch — Top Stories',
    url: 'http://feeds.marketwatch.com/marketwatch/topstories/',
    category: 'markets',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Energy (Tier 2–3)
  // -------------------------------------------------------------------------
  {
    name: 'OilPrice.com',
    url: 'https://oilprice.com/rss/main',
    category: 'energy',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Rigzone — News',
    url: 'https://www.rigzone.com/news/rss/rigzone_latest.aspx',
    category: 'energy',
    tier: 3,
    language: 'en',
  },
  {
    name: 'Energy Intelligence',
    url: 'https://www.energyintel.com/rss',
    category: 'energy',
    tier: 2,
    language: 'en',
  },
  {
    name: 'S&P Global — Commodities',
    url: 'https://www.spglobal.com/commodityinsights/en/rss-feed/all',
    category: 'energy',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Aviation (Tier 2–3)
  // -------------------------------------------------------------------------
  {
    name: 'Aviation Week',
    url: 'https://aviationweek.com/rss.xml',
    category: 'aviation',
    tier: 2,
    language: 'en',
  },
  {
    name: 'FlightGlobal',
    url: 'https://www.flightglobal.com/rss',
    category: 'aviation',
    tier: 2,
    language: 'en',
  },
  {
    name: 'The Aviation Herald',
    url: 'https://avherald.com/h?list=0&feed=1',
    category: 'aviation',
    tier: 3,
    language: 'en',
  },
  {
    name: 'Simple Flying',
    url: 'https://simpleflying.com/feed/',
    category: 'aviation',
    tier: 3,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Science / Space (Tier 3)
  // -------------------------------------------------------------------------
  {
    name: 'SpaceNews',
    url: 'https://spacenews.com/feed/',
    category: 'science-space',
    tier: 3,
    language: 'en',
  },
  {
    name: 'NASA — Breaking News',
    url: 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
    category: 'science-space',
    tier: 3,
    language: 'en',
  },
  {
    name: 'Ars Technica — Science',
    url: 'https://feeds.arstechnica.com/arstechnica/science',
    category: 'science-space',
    tier: 3,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Nuclear / Arms Control (Tier 2)
  // -------------------------------------------------------------------------
  {
    name: 'Arms Control Association',
    url: 'https://www.armscontrol.org/rss.xml',
    category: 'nuclear-arms',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Nuclear Threat Initiative (NTI)',
    url: 'https://www.nti.org/rss/all/',
    category: 'nuclear-arms',
    tier: 2,
    language: 'en',
  },
  {
    name: 'SIPRI — News',
    url: 'https://www.sipri.org/rss.xml',
    category: 'nuclear-arms',
    tier: 2,
    language: 'en',
  },
  {
    name: 'Federation of American Scientists',
    url: 'https://fas.org/feed/',
    category: 'nuclear-arms',
    tier: 2,
    language: 'en',
  },

  // -------------------------------------------------------------------------
  // Regional (Tier 2–4) — propaganda risk flagged where applicable
  // -------------------------------------------------------------------------
  {
    name: 'TASS — English',
    url: 'https://tass.com/rss/v2.xml',
    category: 'regional',
    tier: 3,
    language: 'en',
    region: 'russia',
    propagandaRisk: true,
  },
  {
    name: 'Xinhua — English',
    url: 'https://rsshub.app/xinhua/english',
    category: 'regional',
    tier: 3,
    language: 'en',
    region: 'china',
    propagandaRisk: true,
  },
  {
    name: 'RT — English',
    url: 'https://www.rt.com/rss/',
    category: 'regional',
    tier: 4,
    language: 'en',
    region: 'russia',
    propagandaRisk: true,
  },
  {
    name: 'Al Mayadeen — English',
    url: 'https://english.almayadeen.net/rss',
    category: 'regional',
    tier: 3,
    language: 'en',
    region: 'mena',
    propagandaRisk: true,
  },
  {
    name: 'South China Morning Post',
    url: 'https://www.scmp.com/rss/91/feed',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'asia',
  },
  {
    name: 'Times of Israel',
    url: 'https://www.timesofisrael.com/feed/',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'mena',
  },
  {
    name: 'Kyiv Independent',
    url: 'https://kyivindependent.com/feed/',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'europe',
  },
  {
    name: 'Nikkei Asia',
    url: 'https://asia.nikkei.com/rss',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'asia',
  },
  {
    name: 'The Hindu — International',
    url: 'https://www.thehindu.com/news/international/feeder/default.rss',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'asia',
  },
  {
    name: 'Haaretz',
    url: 'https://www.haaretz.com/cmlink/1.4599085',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'mena',
  },
  {
    name: 'NK News — North Korea',
    url: 'https://www.nknews.org/feed/',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'asia',
  },
  {
    name: 'KCNA Watch',
    url: 'https://kcnawatch.org/feed/',
    category: 'regional',
    tier: 3,
    language: 'en',
    region: 'asia',
    propagandaRisk: true,
  },
  {
    name: 'Iran International',
    url: 'https://www.iranintl.com/en/feed',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'mena',
  },
  {
    name: 'Middle East Eye',
    url: 'https://www.middleeasteye.net/rss',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'mena',
  },
  {
    name: 'The Moscow Times',
    url: 'https://www.themoscowtimes.com/rss/news',
    category: 'regional',
    tier: 2,
    language: 'en',
    region: 'russia',
  },
];

/**
 * Unique feed categories derived from FEEDS array.
 */
export const FEED_CATEGORIES: string[] = [
  ...new Set(FEEDS.map((f) => f.category)),
].sort();
