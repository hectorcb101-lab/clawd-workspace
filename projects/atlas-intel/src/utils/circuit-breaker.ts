// ============================================================================
// Atlas Intel — Circuit Breaker for Fetch
// ============================================================================

export interface CircuitBreakerOptions {
  /** Number of consecutive failures before opening the circuit. Default: 5 */
  maxFailures?: number;
  /** Time in ms before an open circuit transitions to half-open. Default: 60000 */
  resetTimeout?: number;
  /** Per-request timeout in ms. Default: 10000 */
  timeout?: number;
  /** Number of retry attempts on failure (while circuit is closed). Default: 2 */
  retries?: number;
}

export type CircuitState = 'closed' | 'open' | 'half-open';

const DEFAULT_MAX_FAILURES = 5;
const DEFAULT_RESET_TIMEOUT = 60_000;
const DEFAULT_TIMEOUT = 10_000;
const DEFAULT_RETRIES = 2;

/**
 * Circuit Breaker wrapping the Fetch API.
 *
 * States:
 *  - **closed** — requests flow normally; failures are counted.
 *  - **open** — all requests are immediately rejected; after `resetTimeout`
 *    the circuit transitions to half-open.
 *  - **half-open** — a single probe request is allowed through. On success
 *    the circuit closes; on failure it re-opens.
 */
export class CircuitBreaker {
  private _state: CircuitState = 'closed';
  private failures = 0;
  private lastFailureTime = 0;

  private readonly maxFailures: number;
  private readonly resetTimeout: number;
  private readonly timeout: number;
  private readonly retries: number;

  constructor(options?: CircuitBreakerOptions) {
    this.maxFailures = options?.maxFailures ?? DEFAULT_MAX_FAILURES;
    this.resetTimeout = options?.resetTimeout ?? DEFAULT_RESET_TIMEOUT;
    this.timeout = options?.timeout ?? DEFAULT_TIMEOUT;
    this.retries = options?.retries ?? DEFAULT_RETRIES;
  }

  /** Current circuit state. */
  get state(): CircuitState {
    if (this._state === 'open') {
      // Check if enough time has passed to transition to half-open
      if (Date.now() - this.lastFailureTime >= this.resetTimeout) {
        this._state = 'half-open';
      }
    }
    return this._state;
  }

  /** Manually reset the circuit to closed. */
  reset(): void {
    this._state = 'closed';
    this.failures = 0;
    this.lastFailureTime = 0;
  }

  /**
   * Perform a fetch request through the circuit breaker.
   *
   * @throws {Error} When circuit is open or the request fails after retries.
   */
  async fetch(url: string, init?: RequestInit): Promise<Response> {
    const currentState = this.state;

    // If open, reject immediately
    if (currentState === 'open') {
      throw new Error(
        `Circuit breaker OPEN — request to ${url} rejected. ` +
        `Retry after ${Math.ceil((this.resetTimeout - (Date.now() - this.lastFailureTime)) / 1000)}s.`,
      );
    }

    // In half-open state, allow exactly one probe (no retries)
    if (currentState === 'half-open') {
      return this.attemptFetch(url, init);
    }

    // Closed — attempt with retries
    let lastError: Error | null = null;
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const response = await this.attemptFetch(url, init);
        return response;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        // Don't retry if circuit just opened
        if (this._state === 'open') break;
      }
    }

    throw lastError ?? new Error(`Fetch failed for ${url}`);
  }

  // ---------------------------------------------------------------------------
  // Internals
  // ---------------------------------------------------------------------------

  private async attemptFetch(
    url: string,
    init?: RequestInit,
  ): Promise<Response> {
    try {
      const response = await fetchWithTimeout(url, this.timeout, init);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`);
      }

      // Success — reset failure tracking
      this.onSuccess();
      return response;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this._state = 'closed';
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();

    if (this.failures >= this.maxFailures || this._state === 'half-open') {
      this._state = 'open';
    }
  }
}

// =============================================================================
// Standalone helpers
// =============================================================================

/**
 * Fetch with a timeout. Rejects with an AbortError if the request takes
 * longer than `timeout` milliseconds.
 *
 * @param url     Request URL
 * @param timeout Timeout in ms (default: 10 000)
 * @param init    Optional RequestInit (merged with abort signal)
 */
export async function fetchWithTimeout(
  url: string,
  timeout: number = DEFAULT_TIMEOUT,
  init?: RequestInit,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Convenience wrapper: fetch JSON through an optional CircuitBreaker,
 * returning `null` on any error instead of throwing.
 *
 * @example
 *   const data = await safeFetchJSON<MyType>('https://api.example.com/data');
 *   if (data) { ... }
 */
export async function safeFetchJSON<T>(
  url: string,
  breaker?: CircuitBreaker,
): Promise<T | null> {
  try {
    const response = breaker
      ? await breaker.fetch(url)
      : await fetchWithTimeout(url);

    if (!response.ok) return null;

    const data = (await response.json()) as T;
    return data;
  } catch {
    return null;
  }
}
