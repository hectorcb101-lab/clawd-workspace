// ============================================================================
// Atlas Intel — DOM Utility Functions
// ============================================================================

/**
 * Hyperscript helper: create an HTMLElement declaratively.
 *
 * @example
 *   h('div', { class: 'foo', 'data-id': '1' }, 'Hello', h('span', null, 'World'))
 */
export function h(
  tag: string,
  attrs?: Record<string, string | boolean | EventListener> | null,
  ...children: (string | Node | null | undefined)[]
): HTMLElement {
  const el = document.createElement(tag);

  if (attrs) {
    for (const [key, value] of Object.entries(attrs)) {
      if (value === false || value == null) continue;

      if (typeof value === 'function') {
        // Event listener: onClick → click, onMouseEnter → mouseenter
        const event = key.startsWith('on')
          ? key.slice(2).toLowerCase()
          : key;
        el.addEventListener(event, value as EventListener);
      } else if (value === true) {
        el.setAttribute(key, '');
      } else {
        el.setAttribute(key, value);
      }
    }
  }

  for (const child of children) {
    if (child == null) continue;
    if (typeof child === 'string') {
      el.appendChild(document.createTextNode(child));
    } else {
      el.appendChild(child);
    }
  }

  return el;
}

/**
 * Replace all children of a parent element.
 * Uses native `replaceChildren` when available, falls back to manual clear.
 */
export function replaceChildren(
  parent: HTMLElement,
  ...children: (Node | string)[]
): void {
  if (typeof parent.replaceChildren === 'function') {
    parent.replaceChildren(...children);
  } else {
    // Fallback for older environments
    while (parent.firstChild) {
      parent.removeChild(parent.firstChild);
    }
    for (const child of children) {
      if (typeof child === 'string') {
        parent.appendChild(document.createTextNode(child));
      } else {
        parent.appendChild(child);
      }
    }
  }
}

/**
 * Create a DocumentFragment from a raw HTML string.
 *
 * ⚠️  DANGEROUS — sanitize input before use to prevent XSS.
 */
export function rawHtml(html: string): DocumentFragment {
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  return template.content;
}

/**
 * Format a Unix-millisecond timestamp to a human-readable relative string.
 *
 * @example
 *   timeAgo(Date.now() - 300_000) // "5m ago"
 *   timeAgo(Date.now() - 7200_000) // "2h ago"
 */
export function timeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = Math.max(0, now - timestamp);
  const seconds = Math.floor(diff / 1_000);

  if (seconds < 10) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;

  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks}w ago`;

  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;

  const years = Math.floor(days / 365);
  return `${years}y ago`;
}

/**
 * Format a Date to a UTC string: "2024-03-15 14:30 UTC"
 */
export function formatUTC(date: Date): string {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, '0');
  const d = String(date.getUTCDate()).padStart(2, '0');
  const h = String(date.getUTCHours()).padStart(2, '0');
  const min = String(date.getUTCMinutes()).padStart(2, '0');
  return `${y}-${m}-${d} ${h}:${min} UTC`;
}

/**
 * Debounce: delay invocation until `ms` milliseconds of inactivity.
 * The returned function has the same signature as the original.
 */
export function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  ms: number,
): T {
  let timer: ReturnType<typeof setTimeout> | null = null;

  const debounced = (...args: unknown[]) => {
    if (timer !== null) clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null;
      fn(...args);
    }, ms);
  };

  return debounced as unknown as T;
}

/**
 * Throttle: invoke at most once every `ms` milliseconds.
 * Uses a leading-edge call with trailing guarantee.
 */
export function throttle<T extends (...args: unknown[]) => void>(
  fn: T,
  ms: number,
): T {
  let lastCall = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;

  const throttled = (...args: unknown[]) => {
    const now = Date.now();
    const remaining = ms - (now - lastCall);

    if (remaining <= 0) {
      // Enough time has passed — invoke immediately
      if (timer !== null) {
        clearTimeout(timer);
        timer = null;
      }
      lastCall = now;
      fn(...args);
    } else if (timer === null) {
      // Schedule a trailing call
      timer = setTimeout(() => {
        lastCall = Date.now();
        timer = null;
        fn(...args);
      }, remaining);
    }
  };

  return throttled as unknown as T;
}

/**
 * Generate a short unique ID suitable for DOM element IDs.
 * Combines a timestamp component with random entropy (collision-resistant).
 *
 * @example
 *   uid() // "x7f3k9a2m"
 */
export function uid(): string {
  const ts = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 7);
  return `${ts}-${rand}`;
}
