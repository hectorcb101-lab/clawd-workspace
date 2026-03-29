// ============================================================================
// Atlas Intel — Browser-Side ML via Web Worker (transformers.js)
// ============================================================================

// ---------------------------------------------------------------------------
// MLWorkerService
// ---------------------------------------------------------------------------

class MLWorkerService {
  private worker: Worker | null = null;
  private ready = false;
  private pending = new Map<
    string,
    { resolve: (v: unknown) => void; reject: (e: Error) => void; timer: ReturnType<typeof setTimeout> }
  >();
  private enabled = false;
  private initPromise: Promise<boolean> | null = null;

  /** Timeout for individual inference requests (ms) */
  private readonly REQUEST_TIMEOUT = 120_000;

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  /** Initialize the ML worker (lazy, idempotent) */
  async init(): Promise<boolean> {
    if (this.worker) return this.ready;
    if (!this.enabled) return false;

    // Deduplicate concurrent init() calls
    if (this.initPromise) return this.initPromise;

    this.initPromise = this._init();
    return this.initPromise;
  }

  private async _init(): Promise<boolean> {
    try {
      // Build inline worker — runs transformers.js in a dedicated thread
      const workerCode = `
        let pipeline = null;
        let embedder = null;
        let sentimentPipeline = null;
        let nerPipeline = null;
        let classifierPipeline = null;

        self.onmessage = async function(e) {
          const { id, type, payload } = e.data;

          try {
            // Lazy-load transformers.js on first request
            if (!pipeline) {
              const mod = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.0');
              pipeline = mod.pipeline;
            }

            let result;

            switch (type) {
              case 'embeddings': {
                if (!embedder) {
                  embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
                }
                const output = await embedder(payload, {
                  pooling: 'mean',
                  normalize: true,
                });
                result = Array.from(output.data);
                break;
              }

              case 'sentiment': {
                if (!sentimentPipeline) {
                  sentimentPipeline = await pipeline(
                    'sentiment-analysis',
                    'Xenova/distilbert-base-uncased-finetuned-sst-2-english',
                  );
                }
                result = await sentimentPipeline(payload);
                break;
              }

              case 'ner': {
                if (!nerPipeline) {
                  nerPipeline = await pipeline(
                    'token-classification',
                    'Xenova/bert-base-NER',
                  );
                }
                result = await nerPipeline(payload);
                break;
              }

              case 'classify': {
                if (!classifierPipeline) {
                  classifierPipeline = await pipeline(
                    'zero-shot-classification',
                    'Xenova/nli-deberta-v3-xsmall',
                  );
                }
                result = await classifierPipeline(payload.text, payload.labels);
                break;
              }

              default:
                throw new Error('Unknown ML task type: ' + type);
            }

            self.postMessage({ id, type, result });
          } catch (error) {
            self.postMessage({ id, type, error: error.message || String(error) });
          }
        };
      `;

      const blob = new Blob([workerCode], { type: 'application/javascript' });
      const url = URL.createObjectURL(blob);
      this.worker = new Worker(url, { type: 'module' });

      this.worker.onmessage = (e: MessageEvent) => {
        const { id, result, error } = e.data;
        const entry = this.pending.get(id);
        if (!entry) return;

        clearTimeout(entry.timer);
        this.pending.delete(id);

        if (error) {
          entry.reject(new Error(error));
        } else {
          entry.resolve(result);
        }
      };

      this.worker.onerror = (ev: ErrorEvent) => {
        console.error('[MLWorker] Worker error:', ev.message);
      };

      // Clean up the blob URL (worker keeps its reference)
      URL.revokeObjectURL(url);

      this.ready = true;
      return true;
    } catch (err) {
      console.error('[MLWorker] Init failed:', err);
      this.ready = false;
      return false;
    }
  }

  // -------------------------------------------------------------------------
  // Internal messaging
  // -------------------------------------------------------------------------

  /** Send a typed request to the worker and await the response */
  private async request<T>(type: string, payload: unknown): Promise<T> {
    if (!this.worker || !this.ready) {
      // Attempt auto-init
      const ok = await this.init();
      if (!ok) throw new Error('ML worker not initialized');
    }

    const id = crypto.randomUUID?.() || Math.random().toString(36).slice(2);

    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`ML request timed out (${type})`));
      }, this.REQUEST_TIMEOUT);

      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject, timer });
      this.worker!.postMessage({ id, type, payload });
    });
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /**
   * Get embeddings for text.
   * Returns a 384-dimensional normalized vector (all-MiniLM-L6-v2).
   */
  async embed(text: string): Promise<number[]> {
    return this.request<number[]>('embeddings', text);
  }

  /**
   * Batch embed multiple texts.
   * Runs sequentially to avoid overwhelming the worker.
   */
  async embedBatch(texts: string[]): Promise<number[][]> {
    const results: number[][] = [];
    for (const text of texts) {
      results.push(await this.embed(text));
    }
    return results;
  }

  /** Sentiment analysis → [{label: 'POSITIVE'|'NEGATIVE', score: 0-1}] */
  async sentiment(
    text: string,
  ): Promise<Array<{ label: string; score: number }>> {
    return this.request<Array<{ label: string; score: number }>>(
      'sentiment',
      text,
    );
  }

  /** Named entity recognition */
  async ner(
    text: string,
  ): Promise<Array<{ entity: string; score: number; word: string }>> {
    return this.request<Array<{ entity: string; score: number; word: string }>>(
      'ner',
      text,
    );
  }

  /** Zero-shot classification against a set of candidate labels */
  async classify(
    text: string,
    labels: string[],
  ): Promise<{ labels: string[]; scores: number[] }> {
    return this.request<{ labels: string[]; scores: number[] }>('classify', {
      text,
      labels,
    });
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  setEnabled(v: boolean): void {
    this.enabled = v;
  }

  get isReady(): boolean {
    return this.ready;
  }

  get isEnabled(): boolean {
    return this.enabled;
  }

  /** How many requests are currently in-flight */
  get pendingCount(): number {
    return this.pending.size;
  }

  /** Tear down the worker and release resources */
  destroy(): void {
    for (const [, entry] of this.pending) {
      clearTimeout(entry.timer);
      entry.reject(new Error('ML worker destroyed'));
    }
    this.pending.clear();

    this.worker?.terminate();
    this.worker = null;
    this.ready = false;
    this.initPromise = null;
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const mlWorker = new MLWorkerService();
