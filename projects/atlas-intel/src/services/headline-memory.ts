// ============================================================================
// Atlas Intel — Client-Side RAG with IndexedDB Vector Store
// ============================================================================

import type { HeadlineVector } from '@/types/index';
import { mlWorker } from './ml-worker';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DB_NAME = 'atlas-headline-memory';
const DB_VERSION = 1;
const STORE_NAME = 'vectors';
const MAX_ENTRIES = 5000;
const EVICTION_BATCH = 500; // Remove this many when we hit the cap

// ---------------------------------------------------------------------------
// HeadlineMemory
// ---------------------------------------------------------------------------

class HeadlineMemory {
  private db: IDBDatabase | null = null;
  private enabled = false;

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  /** Open (or create) the IndexedDB database */
  async init(): Promise<boolean> {
    if (!this.enabled) return false;
    if (this.db) return true;

    return new Promise<boolean>((resolve) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);

      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('source', 'source', { unique: false });
        }
      };

      req.onsuccess = () => {
        this.db = req.result;

        // Handle unexpected close (e.g. storage pressure)
        this.db.onclose = () => {
          this.db = null;
        };

        resolve(true);
      };

      req.onerror = () => {
        console.error('[HeadlineMemory] Failed to open IndexedDB:', req.error);
        resolve(false);
      };
    });
  }

  // -------------------------------------------------------------------------
  // Store
  // -------------------------------------------------------------------------

  /** Store a headline with its embedding vector */
  async store(headline: string, source: string): Promise<void> {
    if (!this.db || !mlWorker.isReady) return;

    try {
      const embedding = await mlWorker.embed(headline);

      const vector: HeadlineVector = {
        id: crypto.randomUUID(),
        headline,
        embedding: new Float32Array(embedding),
        timestamp: Date.now(),
        source,
      };

      await this.put(vector);
      await this.evictIfNeeded();
    } catch (err) {
      console.error('[HeadlineMemory] Failed to store headline:', err);
    }
  }

  /** Store multiple headlines in a batch */
  async storeBatch(
    items: Array<{ headline: string; source: string }>,
  ): Promise<number> {
    if (!this.db || !mlWorker.isReady) return 0;

    let stored = 0;

    for (const item of items) {
      try {
        const embedding = await mlWorker.embed(item.headline);

        const vector: HeadlineVector = {
          id: crypto.randomUUID(),
          headline: item.headline,
          embedding: new Float32Array(embedding),
          timestamp: Date.now(),
          source: item.source,
        };

        await this.put(vector);
        stored++;
      } catch {
        // Skip individual failures
      }
    }

    await this.evictIfNeeded();
    return stored;
  }

  // -------------------------------------------------------------------------
  // Search
  // -------------------------------------------------------------------------

  /** Semantic search by cosine similarity against the query */
  async search(
    query: string,
    topK?: number,
  ): Promise<Array<{ headline: string; score: number; source: string; timestamp: number }>> {
    if (!this.db || !mlWorker.isReady) return [];

    try {
      const queryEmbed = new Float32Array(await mlWorker.embed(query));
      const all = await this.getAll();

      const results = all
        .map((v) => ({
          headline: v.headline,
          score: cosineSimilarity(queryEmbed, v.embedding),
          source: v.source,
          timestamp: v.timestamp,
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, topK || 10);

      return results;
    } catch (err) {
      console.error('[HeadlineMemory] Search failed:', err);
      return [];
    }
  }

  /**
   * Find headlines similar to a given headline (dedup / clustering).
   * Returns matches above the similarity threshold.
   */
  async findSimilar(
    headline: string,
    threshold = 0.85,
  ): Promise<Array<{ headline: string; score: number; source: string }>> {
    const results = await this.search(headline, 20);
    return results.filter((r) => r.score >= threshold);
  }

  // -------------------------------------------------------------------------
  // Read helpers
  // -------------------------------------------------------------------------

  /** Get total number of stored vectors */
  async count(): Promise<number> {
    if (!this.db) return 0;

    return new Promise<number>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.count();

      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  /** Get the most recent N headlines (no embedding search) */
  async recent(n = 20): Promise<Array<{ headline: string; source: string; timestamp: number }>> {
    if (!this.db) return [];

    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const index = store.index('timestamp');

      // Walk backwards (newest first)
      const req = index.openCursor(null, 'prev');
      const results: Array<{ headline: string; source: string; timestamp: number }> = [];

      req.onsuccess = () => {
        const cursor = req.result;
        if (cursor && results.length < n) {
          const v = cursor.value as HeadlineVector;
          results.push({
            headline: v.headline,
            source: v.source,
            timestamp: v.timestamp,
          });
          cursor.continue();
        } else {
          resolve(results);
        }
      };

      req.onerror = () => reject(req.error);
    });
  }

  /** Get unique sources and their counts */
  async sourceCounts(): Promise<Map<string, number>> {
    if (!this.db) return new Map();

    const all = await this.getAll();
    const counts = new Map<string, number>();

    for (const v of all) {
      counts.set(v.source, (counts.get(v.source) || 0) + 1);
    }

    return counts;
  }

  // -------------------------------------------------------------------------
  // Maintenance
  // -------------------------------------------------------------------------

  /** Clear all stored vectors */
  async clear(): Promise<void> {
    if (!this.db) return;

    return new Promise<void>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const req = store.clear();

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  /** Delete entries older than a given age (ms) */
  async pruneOlderThan(maxAgeMs: number): Promise<number> {
    if (!this.db) return 0;

    const cutoff = Date.now() - maxAgeMs;

    return new Promise<number>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const index = store.index('timestamp');

      // Range: everything from 0 up to the cutoff timestamp
      const range = IDBKeyRange.upperBound(cutoff, false);
      const req = index.openCursor(range);
      let deleted = 0;

      req.onsuccess = () => {
        const cursor = req.result;
        if (cursor) {
          cursor.delete();
          deleted++;
          cursor.continue();
        } else {
          resolve(deleted);
        }
      };

      req.onerror = () => reject(req.error);
    });
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  setEnabled(v: boolean): void {
    this.enabled = v;
  }

  get isInitialized(): boolean {
    return this.db !== null;
  }

  /** Close the database connection */
  close(): void {
    this.db?.close();
    this.db = null;
  }

  /** Completely destroy the database */
  async destroy(): Promise<void> {
    this.close();

    return new Promise<void>((resolve, reject) => {
      const req = indexedDB.deleteDatabase(DB_NAME);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  // -------------------------------------------------------------------------
  // IDB primitives
  // -------------------------------------------------------------------------

  /** Put a single vector into the store */
  private put(vector: HeadlineVector): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);

      // IndexedDB cannot store Float32Array directly in all browsers;
      // serialize embedding as a regular array for portability
      const serializable = {
        ...vector,
        embedding: Array.from(vector.embedding),
      };

      const req = store.put(serializable);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  /** Get all vectors from the store */
  private getAll(): Promise<HeadlineVector[]> {
    return new Promise<HeadlineVector[]>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.getAll();

      req.onsuccess = () => {
        // Rehydrate Float32Array from the stored plain arrays
        const vectors: HeadlineVector[] = (req.result || []).map(
          (raw: Omit<HeadlineVector, 'embedding'> & { embedding: ArrayLike<number> }) => ({
            ...raw,
            embedding: new Float32Array(raw.embedding),
          }),
        );
        resolve(vectors);
      };

      req.onerror = () => reject(req.error);
    });
  }

  /** LRU eviction: remove oldest entries when count exceeds MAX_ENTRIES */
  private async evictIfNeeded(): Promise<void> {
    if (!this.db) return;

    const total = await this.count();
    if (total <= MAX_ENTRIES) return;

    // Remove the oldest EVICTION_BATCH entries
    return new Promise<void>((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const index = store.index('timestamp');

      const req = index.openCursor(null, 'next'); // oldest first
      let removed = 0;
      const toRemove = Math.min(EVICTION_BATCH, total - MAX_ENTRIES + EVICTION_BATCH);

      req.onsuccess = () => {
        const cursor = req.result;
        if (cursor && removed < toRemove) {
          cursor.delete();
          removed++;
          cursor.continue();
        } else {
          resolve();
        }
      };

      req.onerror = () => reject(req.error);
    });
  }
}

// ---------------------------------------------------------------------------
// Cosine similarity
// ---------------------------------------------------------------------------

function cosineSimilarity(a: Float32Array, b: Float32Array): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  return dot / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-8);
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

export const headlineMemory = new HeadlineMemory();
