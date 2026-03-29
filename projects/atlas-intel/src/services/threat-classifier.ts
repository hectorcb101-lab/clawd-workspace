// ============================================================================
// Atlas Intel — 3-Tier Threat Classifier
// ============================================================================

import type { ThreatCategory, NewsItem } from '@/types/index';

// ---------------------------------------------------------------------------
// Classification result
// ---------------------------------------------------------------------------

interface Classification {
  category: ThreatCategory;
  confidence: number;   // 0–1
  keywords: string[];   // matched keywords
}

// ---------------------------------------------------------------------------
// Stage 1: ~120+ threat keywords across 14 categories
// ---------------------------------------------------------------------------

const THREAT_KEYWORDS: Record<ThreatCategory, string[]> = {
  military: [
    'missile', 'airstrike', 'troops', 'deployment', 'fighter jet', 'bomber',
    'warship', 'ammunition', 'military exercise', 'arms deal', 'mobilization',
    'artillery', 'armored vehicle', 'special forces', 'air defense',
  ],
  conflict: [
    'casualties', 'frontline', 'offensive', 'ceasefire', 'shelling',
    'invasion', 'war crime', 'combatants', 'siege', 'counterattack',
    'territorial control', 'escalation', 'armed clash', 'crossfire',
  ],
  cyber: [
    'hack', 'breach', 'ransomware', 'ddos', 'malware', 'phishing',
    'zero-day', 'cyber attack', 'data leak', 'vulnerability',
    'threat actor', 'APT', 'botnet', 'exploit',
  ],
  nuclear: [
    'nuclear', 'enrichment', 'uranium', 'warhead', 'ICBM',
    'nonproliferation', 'plutonium', 'centrifuge', 'nuclear test',
    'radioactive', 'fissile material', 'nuclear reactor', 'dirty bomb',
  ],
  unrest: [
    'protest', 'riot', 'demonstration', 'uprising', 'tear gas',
    'martial law', 'curfew', 'civil unrest', 'looting', 'general strike',
    'water cannon', 'barricade', 'dissent', 'crackdown',
  ],
  economic: [
    'sanctions', 'tariff', 'trade war', 'embargo', 'debt crisis',
    'inflation', 'currency collapse', 'default', 'recession',
    'capital flight', 'bank run', 'economic shock', 'devaluation',
  ],
  terrorism: [
    'terror', 'bombing', 'IED', 'hostage', 'extremist', 'jihad',
    'suicide attack', 'car bomb', 'lone wolf', 'radicalization',
    'insurgency', 'militant', 'terrorist cell', 'mass shooting',
  ],
  health: [
    'pandemic', 'outbreak', 'epidemic', 'quarantine', 'WHO',
    'variant', 'vaccine', 'pathogen', 'biosafety', 'infection rate',
    'lockdown', 'public health emergency', 'contagion', 'mortality rate',
  ],
  climate: [
    'hurricane', 'typhoon', 'flood', 'drought', 'wildfire', 'heatwave',
    'tornado', 'tsunami', 'landslide', 'glacier melt', 'monsoon',
    'extreme weather', 'sea level rise', 'climate emergency',
  ],
  energy: [
    'pipeline', 'oil spill', 'OPEC', 'blackout', 'refinery', 'LNG',
    'energy crisis', 'fuel shortage', 'grid failure', 'natural gas',
    'power plant', 'oil price', 'energy security', 'brownout',
  ],
  space: [
    'satellite', 'orbital', 'space debris', 'launch', 'ASAT',
    'space weapon', 'reentry', 'space station', 'rocket', 'constellation',
    'GPS disruption', 'space situational awareness',
  ],
  maritime: [
    'piracy', 'seizure', 'naval blockade', 'shipping lane', 'port closure',
    'maritime incident', 'vessel seized', 'smuggling', 'coast guard',
    'freedom of navigation', 'strait closure', 'cargo interdiction',
  ],
  aviation: [
    'no-fly zone', 'airspace closure', 'hijack', 'NOTAM', 'crash',
    'flight diversion', 'midair', 'drone incursion', 'grounding',
    'air traffic control', 'emergency landing', 'bird strike',
  ],
  infrastructure: [
    'bridge collapse', 'dam failure', 'power outage', 'sabotage',
    'cable cut', 'rail derailment', 'explosion', 'structural failure',
    'water contamination', 'telecom outage', 'supply chain disruption',
  ],
};

// ---------------------------------------------------------------------------
// Pre-compiled regex map (built once at module load)
// ---------------------------------------------------------------------------

const KEYWORD_PATTERNS: Map<ThreatCategory, { keyword: string; regex: RegExp }[]> = new Map();

for (const [category, keywords] of Object.entries(THREAT_KEYWORDS) as [ThreatCategory, string[]][]) {
  const patterns = keywords.map(kw => ({
    keyword: kw,
    // Word-boundary match, case-insensitive
    regex: new RegExp(`\\b${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i'),
  }));
  KEYWORD_PATTERNS.set(category, patterns);
}

// ---------------------------------------------------------------------------
// Confidence weights
// ---------------------------------------------------------------------------

/** Base confidence for a single keyword hit */
const BASE_CONFIDENCE = 0.35;

/** Additional confidence per extra keyword (diminishing) */
const EXTRA_KEYWORD_BOOST = 0.12;

/** Boost when NewsItem already has a matching threatCategory */
const EXISTING_CATEGORY_BOOST = 0.25;

/** Maximum confidence cap */
const MAX_CONFIDENCE = 0.98;

// ---------------------------------------------------------------------------
// ThreatClassifier
// ---------------------------------------------------------------------------

class ThreatClassifier {
  // -----------------------------------------------------------------------
  // Stage 1: Keyword classification (instant, regex-based)
  // -----------------------------------------------------------------------

  /** Return all matching categories for a given text, sorted by confidence */
  classifyByKeyword(text: string): Classification[] {
    const results: Classification[] = [];

    for (const [category, patterns] of KEYWORD_PATTERNS) {
      const matched: string[] = [];

      for (const { keyword, regex } of patterns) {
        if (regex.test(text)) {
          matched.push(keyword);
        }
      }

      if (matched.length > 0) {
        const confidence = Math.min(
          MAX_CONFIDENCE,
          BASE_CONFIDENCE + (matched.length - 1) * EXTRA_KEYWORD_BOOST,
        );
        results.push({ category, confidence, keywords: matched });
      }
    }

    // Sort descending by confidence, then by keyword count as tiebreaker
    results.sort((a, b) => b.confidence - a.confidence || b.keywords.length - a.keywords.length);

    return results;
  }

  // -----------------------------------------------------------------------
  // Stage 2: Classify a single NewsItem
  // -----------------------------------------------------------------------

  /** Classify a news item — returns the highest-confidence match */
  classify(item: NewsItem): Classification {
    const text = `${item.title} ${item.summary || ''}`;
    const matches = this.classifyByKeyword(text);

    // If the item already has a threatCategory, boost that match or create one
    if (item.threatCategory) {
      const existing = matches.find(m => m.category === item.threatCategory);
      if (existing) {
        existing.confidence = Math.min(MAX_CONFIDENCE, existing.confidence + EXISTING_CATEGORY_BOOST);
        // Re-sort after boosting
        matches.sort((a, b) => b.confidence - a.confidence || b.keywords.length - a.keywords.length);
      } else {
        // No keyword hit but has existing category — add it with moderate confidence
        matches.unshift({
          category: item.threatCategory,
          confidence: 0.50,
          keywords: [],
        });
      }
    }

    // Return the top match, or a fallback
    if (matches.length > 0) {
      return matches[0];
    }

    // No classification possible
    return {
      category: 'conflict',  // generic fallback
      confidence: 0.1,
      keywords: [],
    };
  }

  // -----------------------------------------------------------------------
  // Stage 3: Batch classification
  // -----------------------------------------------------------------------

  /** Classify multiple items. Returns a Map keyed by item.id */
  classifyBatch(items: NewsItem[]): Map<string, Classification> {
    const results = new Map<string, Classification>();

    for (const item of items) {
      results.set(item.id, this.classify(item));
    }

    return results;
  }

  // -----------------------------------------------------------------------
  // Utility
  // -----------------------------------------------------------------------

  /** Get all categories that match a text above a confidence threshold */
  classifyAll(text: string, minConfidence = 0.3): Classification[] {
    return this.classifyByKeyword(text).filter(c => c.confidence >= minConfidence);
  }

  /** Check if text is related to a specific threat category */
  isCategory(text: string, category: ThreatCategory): boolean {
    const patterns = KEYWORD_PATTERNS.get(category);
    if (!patterns) return false;
    return patterns.some(({ regex }) => regex.test(text));
  }

  /** Get all available categories */
  get categories(): ThreatCategory[] {
    return [...KEYWORD_PATTERNS.keys()];
  }

  /** Get the keyword list for a category */
  getKeywords(category: ThreatCategory): string[] {
    return THREAT_KEYWORDS[category] || [];
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export type { Classification };
export const threatClassifier = new ThreatClassifier();
