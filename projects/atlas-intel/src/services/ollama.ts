// ============================================================================
// Atlas Intel — Ollama Local AI Integration
// ============================================================================

import type { AIProvider, AIConfig } from '@/types/index';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface OllamaModel {
  name: string;
  size: number;
  modified: string;
}

// ---------------------------------------------------------------------------
// OllamaService
// ---------------------------------------------------------------------------

class OllamaService {
  private endpoint: string;
  private model: string = 'llama3';
  private available = false;
  private models: OllamaModel[] = [];

  constructor() {
    this.endpoint = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434';
  }

  // -------------------------------------------------------------------------
  // Discovery
  // -------------------------------------------------------------------------

  /** Check if Ollama is running and discover available models */
  async discover(): Promise<boolean> {
    try {
      const resp = await fetch(`${this.endpoint}/api/tags`, {
        signal: AbortSignal.timeout(3000),
      });

      if (!resp.ok) {
        this.available = false;
        return false;
      }

      const data = await resp.json();
      this.models = (data.models || []).map((m: Record<string, unknown>) => ({
        name: m.name as string,
        size: m.size as number,
        modified: m.modified_at as string,
      }));

      this.available = this.models.length > 0;

      // Auto-select the best available model from a preferred list
      if (this.available) {
        const preferred = ['llama3.1', 'llama3', 'mistral', 'gemma2'];
        this.model =
          preferred.find((p) =>
            this.models.some((m) => m.name.startsWith(p)),
          ) || this.models[0].name;
      }

      return this.available;
    } catch {
      this.available = false;
      return false;
    }
  }

  // -------------------------------------------------------------------------
  // Chat / Completion
  // -------------------------------------------------------------------------

  /** Chat completion via the OpenAI-compatible endpoint */
  async chat(
    messages: Array<{ role: string; content: string }>,
    options?: { temperature?: number; maxTokens?: number },
  ): Promise<string | null> {
    if (!this.available) return null;

    try {
      const resp = await fetch(`${this.endpoint}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: this.model,
          messages,
          temperature: options?.temperature ?? 0.3,
          max_tokens: options?.maxTokens ?? 2048,
          stream: false,
        }),
        signal: AbortSignal.timeout(30_000),
      });

      if (!resp.ok) return null;

      const data = await resp.json();
      return data.choices?.[0]?.message?.content || null;
    } catch {
      return null;
    }
  }

  /** Simple single-prompt completion (wraps chat) */
  async complete(
    prompt: string,
    options?: { temperature?: number },
  ): Promise<string | null> {
    return this.chat([{ role: 'user', content: prompt }], options);
  }

  // -------------------------------------------------------------------------
  // Embeddings
  // -------------------------------------------------------------------------

  /**
   * Generate embeddings via Ollama's native /api/embeddings endpoint.
   * Falls back to null if the model doesn't support embeddings.
   */
  async embeddings(
    text: string,
    model?: string,
  ): Promise<number[] | null> {
    if (!this.available) return null;

    try {
      const resp = await fetch(`${this.endpoint}/api/embeddings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: model || 'nomic-embed-text',
          prompt: text,
        }),
        signal: AbortSignal.timeout(15_000),
      });

      if (!resp.ok) return null;

      const data = await resp.json();
      return data.embedding || null;
    } catch {
      return null;
    }
  }

  // -------------------------------------------------------------------------
  // Structured output helpers
  // -------------------------------------------------------------------------

  /**
   * Ask the model to return JSON. Wraps the prompt with a system message
   * instructing strict JSON output, then parses the result.
   */
  async json<T = unknown>(
    prompt: string,
    options?: { temperature?: number; maxTokens?: number },
  ): Promise<T | null> {
    const messages = [
      {
        role: 'system',
        content:
          'You are a data extraction assistant. Respond ONLY with valid JSON, no markdown, no commentary.',
      },
      { role: 'user', content: prompt },
    ];

    const raw = await this.chat(messages, options);
    if (!raw) return null;

    try {
      // Strip markdown code fences if the model wrapped its response
      const cleaned = raw
        .replace(/^```(?:json)?\s*/i, '')
        .replace(/\s*```$/i, '')
        .trim();
      return JSON.parse(cleaned) as T;
    } catch {
      return null;
    }
  }

  /**
   * Summarize text with an optional system-level persona.
   */
  async summarize(
    text: string,
    options?: {
      maxSentences?: number;
      persona?: string;
      temperature?: number;
    },
  ): Promise<string | null> {
    const sentences = options?.maxSentences ?? 3;
    const persona =
      options?.persona ||
      'You are a concise OSINT analyst. Summarize the following in plain language.';

    return this.chat(
      [
        { role: 'system', content: persona },
        {
          role: 'user',
          content: `Summarize the following in at most ${sentences} sentences:\n\n${text}`,
        },
      ],
      { temperature: options?.temperature ?? 0.2, maxTokens: 512 },
    );
  }

  // -------------------------------------------------------------------------
  // Health & diagnostics
  // -------------------------------------------------------------------------

  /** Lightweight health check — pings the Ollama root endpoint */
  async ping(): Promise<boolean> {
    try {
      const resp = await fetch(this.endpoint, {
        signal: AbortSignal.timeout(2000),
      });
      return resp.ok;
    } catch {
      return false;
    }
  }

  /** Return a diagnostic snapshot */
  diagnostics(): {
    endpoint: string;
    available: boolean;
    model: string;
    modelCount: number;
  } {
    return {
      endpoint: this.endpoint,
      available: this.available,
      model: this.model,
      modelCount: this.models.length,
    };
  }

  // -------------------------------------------------------------------------
  // Getters & Setters
  // -------------------------------------------------------------------------

  get isAvailable(): boolean {
    return this.available;
  }

  get currentModel(): string {
    return this.model;
  }

  get availableModels(): OllamaModel[] {
    return this.models;
  }

  setModel(name: string): void {
    this.model = name;
  }

  setEndpoint(url: string): void {
    this.endpoint = url;
    this.available = false;
    this.models = [];
  }

  /** Build an AIConfig snapshot for persistence */
  toConfig(): AIConfig {
    return {
      provider: 'ollama' as AIProvider,
      model: this.model,
      endpoint: this.endpoint,
    };
  }

  /** Restore from a persisted AIConfig */
  fromConfig(config: AIConfig): void {
    if (config.endpoint) this.endpoint = config.endpoint;
    if (config.model) this.model = config.model;
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const ollama = new OllamaService();
