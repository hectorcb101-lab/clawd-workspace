// ============================================================================
// Atlas Intel — 3-Tier Cache Service
// Tier 1: In-memory Map  (fastest, volatile)
// Tier 2: localStorage   (sync, ~5 MB cap)
// Tier 3: IndexedDB      (async, large capacity)
// ============================================================================

import type { CacheEntry, CacheTier } from '@/types/index';

// ---------------------------------------------------------------------------
// IndexedDB helpers
// ---------------------------------------------------------------------------

const IDB_NAME = 'atlas-intel-cache';
const IDB_STORE = 'entries';
const IDB_VERSION = 1;

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_NAME, IDB_VERSION);

    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(IDB_STORE)) {
        db.createObjectStore(IDB_STORE);
      }
    };

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function idbGet<T>(key: string): Promise<CacheEntry<T> | null> {
  return openDB().then(
    (db) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(IDB_STORE, 'readonly');
        const store = tx.objectStore(IDB_STORE);
        const req = store.get(key);
        req.onsuccess = () => resolve(req.result ?? null);
        req.onerror = () => reject(req.error);
      }),
  );
}

function idbSet<T>(key: string, entry: CacheEntry<T>): Promise<void> {
  return openDB().then(
    (db) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(IDB_STORE, 'readwrite');
        const store = tx.objectStore(IDB_STORE);
        const req = store.put(entry, key);
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      }),
  );
}

function idbDelete(key: string): Promise<void> {
  return openDB().then(
    (db) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(IDB_STORE, 'readwrite');
        const store = tx.objectStore(IDB_STORE);
        const req = store.delete(key);
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      }),
  );
}

function idbClear(): Promise<void> {
  return openDB().then(
    (db) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(IDB_STORE, 'readwrite');
        const store = tx.objectStore(IDB_STORE);
        const req = store.clear();
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      }),
  );
}

// ---------------------------------------------------------------------------
// localStorage helpers
// ---------------------------------------------------------------------------

const LS_PREFIX = 'atlas-cache:';

function lsKey(key: string): string {
  return `${LS_PREFIX}${key}`;
}

function lsGet<T>(key: string): CacheEntry<T> | null {
  try {
    const raw = localStorage.getItem(lsKey(key));
    if (!raw) return null;
    return JSON.parse(raw) as CacheEntry<T>;
  } catch {
    return null;
  }
}

function lsSet<T>(key: string, entry: CacheEntry<T>): void {
  try {
    localStorage.setItem(lsKey(key), JSON.stringify(entry));
  } catch (err: unknown) {
    // Quota exceeded — evict oldest atlas-cache entries and retry once
    if (err instanceof DOMException && err.name === 'QuotaExceededError') {
      evictOldestLocalStorage();
      try {
        localStorage.setItem(lsKey(key), JSON.stringify(entry));
      } catch {
        // Still full — silently drop; memory tier is still valid
        console.warn('[CacheService] localStorage quota exceeded, entry dropped:', key);
      }
    }
  }
}

function lsDelete(key: string): void {
  try {
    localStorage.removeItem(lsKey(key));
  } catch {
    // ignore
  }
}

function lsClear(): void {
  try {
    const toRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k?.startsWith(LS_PREFIX)) toRemove.push(k);
    }
    toRemove.forEach((k) => localStorage.removeItem(k));
  } catch {
    // ignore
  }
}

function lsCount(): number {
  let count = 0;
  try {
    for (let i = 0; i < localStorage.length; i++) {
      if (localStorage.key(i)?.startsWith(LS_PREFIX)) count++;
    }
  } catch {
    // ignore
  }
  return count;
}

/** Evict the oldest (by timestamp) atlas-cache entry from localStorage. */
function evictOldestLocalStorage(): void {
  let oldestKey: string | null = null;
  let oldestTs = Infinity;

  try {
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k?.startsWith(LS_PREFIX)) continue;
      try {
        const entry = JSON.parse(localStorage.getItem(k)!) as CacheEntry<unknown>;
        if (entry.timestamp < oldestTs) {
          oldestTs = entry.timestamp;
          oldestKey = k;
        }
      } catch {
        // corrupt entry — remove it
        localStorage.removeItem(k);
        return;
      }
    }
    if (oldestKey) localStorage.removeItem(oldestKey);
  } catch {
    // ignore
  }
}

// ---------------------------------------------------------------------------
// Expiry check
// ---------------------------------------------------------------------------

function isExpired(entry: CacheEntry<unknown>): boolean {
  return Date.now() > entry.timestamp + entry.ttl;
}

// ---------------------------------------------------------------------------
// CacheService
// ---------------------------------------------------------------------------

class CacheService {
  /** Tier 1 — in-memory store */
  private memory = new Map<string, CacheEntry<unknown>>();

  // -------------------------------------------------------------------------
  // get — check tiers in order: memory → localStorage → IndexedDB
  // -------------------------------------------------------------------------
  async get<T>(key: string): Promise<T | null> {
    // --- Tier 1: memory ---
    const memEntry = this.memory.get(key) as CacheEntry<T> | undefined;
    if (memEntry) {
      if (isExpired(memEntry)) {
        this.memory.delete(key);
      } else {
        return memEntry.data;
      }
    }

    // --- Tier 2: localStorage ---
    const lsEntry = lsGet<T>(key);
    if (lsEntry) {
      if (isExpired(lsEntry)) {
        lsDelete(key);
      } else {
        // Promote back to memory for faster subsequent reads
        this.memory.set(key, lsEntry as CacheEntry<unknown>);
        return lsEntry.data;
      }
    }

    // --- Tier 3: IndexedDB ---
    try {
      const idbEntry = await idbGet<T>(key);
      if (idbEntry) {
        if (isExpired(idbEntry)) {
          await idbDelete(key).catch(() => {});
        } else {
          // Promote back to memory
          this.memory.set(key, idbEntry as CacheEntry<unknown>);
          return idbEntry.data;
        }
      }
    } catch {
      // IndexedDB unavailable — skip
    }

    return null;
  }

  // -------------------------------------------------------------------------
  // set — always writes to memory, optionally persists to lower tiers
  // -------------------------------------------------------------------------
  async set<T>(
    key: string,
    data: T,
    ttl: number,
    tier: CacheTier = 'memory',
  ): Promise<void> {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
    };

    // Always set in memory (Tier 1)
    this.memory.set(key, entry as CacheEntry<unknown>);

    // Tier 2
    if (tier === 'localStorage' || tier === 'indexedDB') {
      lsSet(key, entry);
    }

    // Tier 3
    if (tier === 'indexedDB') {
      try {
        await idbSet(key, entry);
      } catch (err) {
        console.warn('[CacheService] IndexedDB write failed:', key, err);
      }
    }
  }

  // -------------------------------------------------------------------------
  // delete — remove from all tiers
  // -------------------------------------------------------------------------
  async delete(key: string): Promise<void> {
    this.memory.delete(key);
    lsDelete(key);
    try {
      await idbDelete(key);
    } catch {
      // IndexedDB unavailable — skip
    }
  }

  // -------------------------------------------------------------------------
  // clear — wipe all tiers
  // -------------------------------------------------------------------------
  async clear(): Promise<void> {
    this.memory.clear();
    lsClear();
    try {
      await idbClear();
    } catch {
      // IndexedDB unavailable — skip
    }
  }

  // -------------------------------------------------------------------------
  // has — key exists and is not expired (checks all tiers)
  // -------------------------------------------------------------------------
  async has(key: string): Promise<boolean> {
    return (await this.get(key)) !== null;
  }

  // -------------------------------------------------------------------------
  // stats — counts for inspectable tiers
  // -------------------------------------------------------------------------
  stats(): { memory: number; localStorage: number } {
    return {
      memory: this.memory.size,
      localStorage: lsCount(),
    };
  }
}

export const cache = new CacheService();
