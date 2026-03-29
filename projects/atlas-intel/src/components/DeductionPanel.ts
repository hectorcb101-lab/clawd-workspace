// ============================================================================
// Atlas Intel — AI Deduction & Forecasting Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import type { AIProvider, AIBrief, NewsItem, CacheEntry } from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CACHE_KEY = 'atlas:deduction-cache';
const CACHE_TTL = 60 * 60 * 1000; // 1 hour
const COOLDOWN_MS = 5_000;
const MAX_CONTEXT_HEADLINES = 15;

// ---------------------------------------------------------------------------
// Provider configuration
// ---------------------------------------------------------------------------

interface ProviderConfig {
  name: AIProvider;
  label: string;
  endpoint: string;
  model: string;
}

const PROVIDER_CHAIN: ProviderConfig[] = [
  {
    name: 'ollama',
    label: 'Ollama (Local)',
    endpoint: 'http://localhost:11434/api/generate',
    model: 'mistral',
  },
  {
    name: 'groq',
    label: 'Groq',
    endpoint: 'https://api.groq.com/openai/v1/chat/completions',
    model: 'mixtral-8x7b-32768',
  },
  {
    name: 'openrouter',
    label: 'OpenRouter',
    endpoint: 'https://openrouter.ai/api/v1/chat/completions',
    model: 'mistralai/mistral-7b-instruct',
  },
];

// ---------------------------------------------------------------------------
// Shared headline store (populated by other panels via events)
// ---------------------------------------------------------------------------

const headlineStore: NewsItem[] = [];

function pushHeadlines(items: NewsItem[]): void {
  for (const item of items) {
    if (!headlineStore.find(h => h.id === item.id)) {
      headlineStore.push(item);
    }
  }
  // Keep only the most recent 200
  headlineStore.sort((a, b) => b.timestamp - a.timestamp);
  if (headlineStore.length > 200) headlineStore.length = 200;
}

// Listen for headline pushes from other panels
document.addEventListener('wm:headlines', ((e: CustomEvent) => {
  if (Array.isArray(e.detail?.items)) {
    pushHeadlines(e.detail.items);
  }
}) as EventListener);

// ---------------------------------------------------------------------------
// DeductionPanel
// ---------------------------------------------------------------------------

export class DeductionPanel extends Panel {
  private inputEl!: HTMLTextAreaElement;
  private submitBtn!: HTMLButtonElement;
  private resultEl!: HTMLElement;
  private providerLabel!: HTMLElement;
  private cooldownActive = false;

  constructor() {
    super({
      id: 'deduction',
      title: 'AI DEDUCTION',
      icon: '🧠',
      description: 'AI-powered deduction and forecasting from aggregated intelligence',
      defaultOpen: false,
    });

    this.buildUI();
    this.listenForContextEvents();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    // Text area for free-form prompts
    this.inputEl = h('textarea', {
      class: 'deduction-input',
      placeholder: 'Enter a geopolitical question or scenario for AI analysis…',
    }) as unknown as HTMLTextAreaElement;

    // Submit button
    this.submitBtn = h(
      'button',
      {
        class: 'deduction-submit',
        onClick: () => this.handleSubmit(),
      },
      '▶ ANALYZE',
    ) as unknown as HTMLButtonElement;

    // Provider indicator
    this.providerLabel = h('span', { class: 'deduction-provider' }, '');

    const controls = h(
      'div',
      { class: 'deduction-controls' },
      this.submitBtn,
      this.providerLabel,
    );

    // Results area
    this.resultEl = h('div', { class: 'deduction-result' });

    replaceChildren(this.body, this.inputEl, controls, this.resultEl);
  }

  // ── Context building ──────────────────────────────────────────────────────

  private buildNewsContext(): string {
    const recent = headlineStore
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, MAX_CONTEXT_HEADLINES);

    if (recent.length === 0) {
      return 'No recent headlines available.';
    }

    return recent
      .map((item, i) => `[${i + 1}] ${item.title} (${item.source}, ${timeAgo(item.timestamp)})`)
      .join('\n');
  }

  // ── Cross-panel context events ────────────────────────────────────────────

  private listenForContextEvents(): void {
    document.addEventListener('wm:deduct-context', ((e: CustomEvent) => {
      const context = e.detail?.text ?? '';
      if (context && this.inputEl) {
        this.inputEl.value = context;
        if (this.isOpen) {
          this.handleSubmit();
        }
      }
    }) as EventListener);
  }

  // ── Submission handling ───────────────────────────────────────────────────

  private async handleSubmit(): Promise<void> {
    const query = this.inputEl.value.trim();
    if (!query || this.cooldownActive) return;

    // Check cache first
    const cached = this.getCachedResult(query);
    if (cached) {
      this.displayResult(cached);
      return;
    }

    // Activate cooldown
    this.startCooldown();
    this.setFooter('Analyzing…');
    this.providerLabel.textContent = 'Connecting…';

    const newsContext = this.buildNewsContext();
    const systemPrompt =
      'You are Atlas Intel, a geopolitical intelligence analyst. ' +
      'Provide concise, analytical assessments. Cite headline numbers [N] when referencing news. ' +
      'Structure your response with key findings and confidence levels.';

    const userPrompt =
      `RECENT INTELLIGENCE:\n${newsContext}\n\nANALYSIS REQUEST:\n${query}`;

    // Try provider chain
    for (const provider of PROVIDER_CHAIN) {
      try {
        const result = await this.callProvider(provider, systemPrompt, userPrompt);
        if (result) {
          const brief: AIBrief = {
            text: result,
            citations: this.extractCitations(result),
            provider: provider.name,
            timestamp: Date.now(),
          };

          this.cacheResult(query, brief);
          this.displayResult(brief);
          return;
        }
      } catch {
        // Try next provider
        continue;
      }
    }

    // All providers failed
    this.providerLabel.textContent = '✗ All providers failed';
    replaceChildren(
      this.resultEl,
      h('div', { class: 'deduction-error' }, 'All AI providers are unavailable. Check network connectivity and API keys.'),
    );
    this.setFooter('Analysis failed');
  }

  // ── Provider calls ────────────────────────────────────────────────────────

  private async callProvider(
    provider: ProviderConfig,
    system: string,
    user: string,
  ): Promise<string | null> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15_000);

    try {
      if (provider.name === 'ollama') {
        return await this.callOllama(provider, system, user, controller.signal);
      } else {
        return await this.callOpenAICompat(provider, system, user, controller.signal);
      }
    } finally {
      clearTimeout(timeout);
    }
  }

  private async callOllama(
    provider: ProviderConfig,
    system: string,
    user: string,
    signal: AbortSignal,
  ): Promise<string | null> {
    const res = await fetch(provider.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: provider.model,
        prompt: `${system}\n\n${user}`,
        stream: false,
      }),
      signal,
    });

    if (!res.ok) return null;
    const data = await res.json();
    return data.response ?? null;
  }

  private async callOpenAICompat(
    provider: ProviderConfig,
    system: string,
    user: string,
    signal: AbortSignal,
  ): Promise<string | null> {
    const apiKey =
      provider.name === 'groq'
        ? (localStorage.getItem('atlas:groq-key') ?? '')
        : (localStorage.getItem('atlas:openrouter-key') ?? '');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

    const res = await fetch(provider.endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: provider.model,
        messages: [
          { role: 'system', content: system },
          { role: 'user', content: user },
        ],
        max_tokens: 1024,
        temperature: 0.3,
      }),
      signal,
    });

    if (!res.ok) return null;
    const data = await res.json();
    return data.choices?.[0]?.message?.content ?? null;
  }

  // ── Citation extraction ───────────────────────────────────────────────────

  private extractCitations(text: string): number[] {
    const matches = text.match(/\[(\d+)\]/g) ?? [];
    const nums = matches.map(m => parseInt(m.replace(/[[\]]/g, ''), 10));
    return [...new Set(nums)].sort((a, b) => a - b);
  }

  // ── Result display ────────────────────────────────────────────────────────

  private displayResult(brief: AIBrief): void {
    const providerNames: Record<AIProvider, string> = {
      ollama: '🟢 Ollama (Local)',
      groq: '⚡ Groq',
      openrouter: '🌐 OpenRouter',
      'browser-t5': '🧪 Browser T5',
    };

    this.providerLabel.textContent = providerNames[brief.provider] ?? brief.provider;

    // Format text with citation highlights
    const formatted = brief.text.replace(
      /\[(\d+)\]/g,
      '<span class="ai-citation">[$1]</span>',
    );

    const briefEl = h('div', { class: 'ai-brief' });
    briefEl.innerHTML = formatted;

    // Citation list
    const citationEls: HTMLElement[] = [];
    if (brief.citations.length > 0) {
      const citationHeader = h('div', { class: 'ai-citation-header' }, 'SOURCES CITED:');
      citationEls.push(citationHeader);

      for (const num of brief.citations) {
        const headline = headlineStore[num - 1];
        if (headline) {
          citationEls.push(
            h(
              'div',
              { class: 'ai-citation-item' },
              h('span', { class: 'ai-citation-num' }, `[${num}]`),
              h('span', null, headline.title),
            ),
          );
        }
      }
    }

    const timestampEl = h(
      'div',
      { class: 'ai-timestamp' },
      `Generated ${timeAgo(brief.timestamp)}`,
    );

    replaceChildren(this.resultEl, briefEl, ...citationEls, timestampEl);
    this.setFooter(`Analysis complete · ${providerNames[brief.provider]}`);
  }

  // ── Cooldown ──────────────────────────────────────────────────────────────

  private startCooldown(): void {
    this.cooldownActive = true;
    this.submitBtn.setAttribute('disabled', '');
    this.submitBtn.textContent = '⏳ WAIT…';

    setTimeout(() => {
      this.cooldownActive = false;
      this.submitBtn.removeAttribute('disabled');
      this.submitBtn.textContent = '▶ ANALYZE';
    }, COOLDOWN_MS);
  }

  // ── Cache (localStorage, 1h TTL) ─────────────────────────────────────────

  private getCacheKey(query: string): string {
    return `${CACHE_KEY}:${query.toLowerCase().trim().replace(/\s+/g, '-').slice(0, 80)}`;
  }

  private getCachedResult(query: string): AIBrief | null {
    try {
      const raw = localStorage.getItem(this.getCacheKey(query));
      if (!raw) return null;

      const entry: CacheEntry<AIBrief> = JSON.parse(raw);
      if (Date.now() - entry.timestamp > entry.ttl) {
        localStorage.removeItem(this.getCacheKey(query));
        return null;
      }

      return entry.data;
    } catch {
      return null;
    }
  }

  private cacheResult(query: string, brief: AIBrief): void {
    try {
      const entry: CacheEntry<AIBrief> = {
        data: brief,
        timestamp: Date.now(),
        ttl: CACHE_TTL,
      };
      localStorage.setItem(this.getCacheKey(query), JSON.stringify(entry));
    } catch {
      // localStorage full — ignore
    }
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
  }

  protected render(): void {
    // Initial state — nothing extra to render
  }

  async refresh(): Promise<void> {
    // No periodic refresh needed
  }
}
