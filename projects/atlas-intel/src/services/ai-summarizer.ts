// ============================================================================
// Atlas Intel — AI Summarizer Service (4-tier provider chain)
// ============================================================================

import type { AIProvider, AIBrief, NewsItem } from '@/types/index';

// ---------------------------------------------------------------------------
// Options
// ---------------------------------------------------------------------------

interface SummarizerOptions {
  maxHeadlines?: number;  // default 20
  language?: string;      // default 'en'
  cacheTTL?: number;      // default 3600000 (1h)
}

// ---------------------------------------------------------------------------
// Deduplication helpers
// ---------------------------------------------------------------------------

/** Jaccard similarity between two strings (word-level) */
function jaccardSimilarity(a: string, b: string): number {
  const setA = new Set(a.toLowerCase().split(/\s+/));
  const setB = new Set(b.toLowerCase().split(/\s+/));
  const intersection = new Set([...setA].filter(x => setB.has(x)));
  const union = new Set([...setA, ...setB]);
  if (union.size === 0) return 0;
  return intersection.size / union.size;
}

/** Deduplicate headlines with Jaccard > 0.6 (keeps earliest occurrence) */
function deduplicateHeadlines(items: NewsItem[]): NewsItem[] {
  const result: NewsItem[] = [];

  for (const item of items) {
    const isDuplicate = result.some(
      existing => jaccardSimilarity(existing.title, item.title) > 0.6,
    );
    if (!isDuplicate) {
      result.push(item);
    }
  }

  return result;
}

// ---------------------------------------------------------------------------
// AISummarizer
// ---------------------------------------------------------------------------

class AISummarizer {
  private providerChain: AIProvider[] = ['ollama', 'groq', 'openrouter', 'browser-t5'];
  private cache = new Map<string, AIBrief>();

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Generate a World Brief from headlines */
  async generateWorldBrief(
    headlines: NewsItem[],
    options?: SummarizerOptions,
  ): Promise<AIBrief> {
    const deduped = deduplicateHeadlines(headlines);
    const cacheKey = `world-brief:${deduped.slice(0, 5).map(h => h.id).join(',')}`;
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < (options?.cacheTTL || 3_600_000)) {
      return cached;
    }

    const prompt = this.buildWorldBriefPrompt(
      deduped.slice(0, options?.maxHeadlines || 20),
      options?.language,
    );

    for (const provider of this.providerChain) {
      try {
        const text = await this.callProvider(provider, prompt);
        if (text) {
          const citations = this.extractCitationIndices(text);
          const brief: AIBrief = {
            text,
            citations,
            provider,
            timestamp: Date.now(),
          };
          this.cache.set(cacheKey, brief);
          return brief;
        }
      } catch {
        continue;
      }
    }

    return {
      text: 'Unable to generate brief. All AI providers unavailable.',
      citations: [],
      provider: 'browser-t5',
      timestamp: Date.now(),
    };
  }

  /** Generate country intelligence brief */
  async generateCountryBrief(
    country: string,
    headlines: NewsItem[],
    options?: SummarizerOptions,
  ): Promise<AIBrief> {
    const countryHeadlines = headlines.filter(
      h =>
        h.country?.toLowerCase() === country.toLowerCase() ||
        h.countries?.some(c => c.toLowerCase() === country.toLowerCase()),
    );
    const deduped = deduplicateHeadlines(countryHeadlines);
    const cacheKey = `country-brief:${country}:${deduped.slice(0, 5).map(h => h.id).join(',')}`;
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < (options?.cacheTTL || 3_600_000)) {
      return cached;
    }

    const prompt = this.buildCountryBriefPrompt(
      country,
      deduped.slice(0, options?.maxHeadlines || 20),
      options?.language,
    );

    for (const provider of this.providerChain) {
      try {
        const text = await this.callProvider(provider, prompt);
        if (text) {
          const citations = this.extractCitationIndices(text);
          const brief: AIBrief = {
            text,
            citations,
            provider,
            timestamp: Date.now(),
            country,
          };
          this.cache.set(cacheKey, brief);
          return brief;
        }
      } catch {
        continue;
      }
    }

    return {
      text: `Unable to generate brief for ${country}. All AI providers unavailable.`,
      citations: [],
      provider: 'browser-t5',
      timestamp: Date.now(),
      country,
    };
  }

  /** Update the provider fallback chain */
  setProviderChain(chain: AIProvider[]): void {
    this.providerChain = chain;
  }

  /** Clear the in-memory cache */
  clearCache(): void {
    this.cache.clear();
  }

  // -------------------------------------------------------------------------
  // Prompt builders
  // -------------------------------------------------------------------------

  private buildWorldBriefPrompt(headlines: NewsItem[], language?: string): string {
    const lang = language || 'en';
    const numbered = headlines
      .map((h, i) => `[${i + 1}] ${h.title} (${h.source}${h.country ? `, ${h.country}` : ''})`)
      .join('\n');

    return [
      'You are an intelligence analyst. Produce a concise WORLD BRIEF summarising the most significant global developments from the following headlines.',
      '',
      'Rules:',
      '- Write 3-5 short paragraphs, each covering a distinct theme or region.',
      '- Reference headlines by number in square brackets, e.g. [1][3].',
      '- Lead with the highest-impact items (conflict, security, nuclear, major geopolitical shifts).',
      '- Maintain a neutral, professional tone.',
      '- Do NOT invent facts not present in the headlines.',
      `- Respond in language code: ${lang}.`,
      '',
      'HEADLINES:',
      numbered,
      '',
      'WORLD BRIEF:',
    ].join('\n');
  }

  private buildCountryBriefPrompt(
    country: string,
    headlines: NewsItem[],
    language?: string,
  ): string {
    const lang = language || 'en';
    const numbered = headlines
      .map((h, i) => `[${i + 1}] ${h.title} (${h.source})`)
      .join('\n');

    return [
      `You are an intelligence analyst. Produce a focused COUNTRY BRIEF for ${country} from the following headlines.`,
      '',
      'Rules:',
      '- Write 2-4 short paragraphs covering security, political, and economic developments.',
      '- Reference headlines by number in square brackets, e.g. [1][3].',
      '- Highlight any escalation patterns or de-escalation signals.',
      '- Maintain a neutral, professional tone.',
      '- Do NOT invent facts not present in the headlines.',
      `- Respond in language code: ${lang}.`,
      '',
      'HEADLINES:',
      numbered,
      '',
      'COUNTRY BRIEF:',
    ].join('\n');
  }

  // -------------------------------------------------------------------------
  // Citation extraction
  // -------------------------------------------------------------------------

  /** Extract [1], [2] etc. citation indices from generated text */
  private extractCitationIndices(text: string): number[] {
    const matches = text.matchAll(/\[(\d+)\]/g);
    const indices = new Set<number>();
    for (const m of matches) {
      indices.add(parseInt(m[1], 10));
    }
    return [...indices].sort((a, b) => a - b);
  }

  // -------------------------------------------------------------------------
  // Provider dispatch
  // -------------------------------------------------------------------------

  private async callProvider(provider: AIProvider, prompt: string): Promise<string | null> {
    switch (provider) {
      case 'ollama':
        return this.callOllama(prompt);
      case 'groq':
        return this.callGroq(prompt);
      case 'openrouter':
        return this.callOpenRouter(prompt);
      case 'browser-t5':
        // browser-t5 is handled by the ml-worker pipeline; not callable here
        return null;
    }
  }

  // -------------------------------------------------------------------------
  // Provider implementations
  // -------------------------------------------------------------------------

  private async callOllama(prompt: string): Promise<string | null> {
    const endpoint = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434';
    const resp = await fetch(`${endpoint}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
      }),
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    return data.choices?.[0]?.message?.content || null;
  }

  private async callGroq(prompt: string): Promise<string | null> {
    const apiKey = import.meta.env.VITE_GROQ_API_KEY;
    if (!apiKey) return null;

    const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'llama-3.1-70b-versatile',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
        max_tokens: 1024,
      }),
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    return data.choices?.[0]?.message?.content || null;
  }

  private async callOpenRouter(prompt: string): Promise<string | null> {
    const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
    if (!apiKey) return null;

    const resp = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
        'X-Title': 'Atlas Intel',
      },
      body: JSON.stringify({
        model: 'meta-llama/llama-3.1-70b-instruct',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
        max_tokens: 1024,
      }),
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    return data.choices?.[0]?.message?.content || null;
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const aiSummarizer = new AISummarizer();
