// ============================================================================
// Atlas Intel — HTML / Text / URL Sanitization Utilities
// ============================================================================

import DOMPurify from 'dompurify';

/** Sanitize HTML string, allowing safe tags */
export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br',
      'ul', 'ol', 'li', 'span', 'div',
      'h1', 'h2', 'h3', 'h4',
      'code', 'pre', 'blockquote',
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class', 'id', 'title'],
    ALLOW_DATA_ATTR: false,
  });
}

/** Sanitize to plain text only (strip all HTML) */
export function sanitizeText(dirty: string): string {
  return DOMPurify.sanitize(dirty, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}

/** Sanitize URL — only allow http / https protocols */
export function sanitizeURL(url: string): string {
  try {
    const parsed = new URL(url);
    if (!['http:', 'https:'].includes(parsed.protocol)) return '';
    return parsed.href;
  } catch {
    return '';
  }
}
