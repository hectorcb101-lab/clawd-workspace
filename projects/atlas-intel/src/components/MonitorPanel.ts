// ============================================================================
// Atlas Intel — Keyword Monitor Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import type { NewsItem } from '@/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const STORAGE_KEY = 'atlas:monitor-keywords';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MonitorKeyword {
  id: string;
  keyword: string;
  matchCount: number;
  lastMatch: number | null;
  createdAt: number;
}

interface MatchedItem {
  keyword: string;
  item: NewsItem;
}

// ---------------------------------------------------------------------------
// MonitorPanel
// ---------------------------------------------------------------------------

export class MonitorPanel extends Panel {
  private keywords: MonitorKeyword[] = [];
  private matchedItems: MatchedItem[] = [];
  private inputEl!: HTMLInputElement;
  private addBtn!: HTMLButtonElement;
  private keywordListEl!: HTMLElement;
  private matchListEl!: HTMLElement;
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor() {
    super({
      id: 'monitor',
      title: 'KEYWORD MONITOR',
      icon: '🔍',
      description: 'Monitor custom keywords across all intelligence feeds',
      defaultOpen: false,
    });

    this.loadKeywords();
    this.buildUI();
    this.listenForNews();
  }

  // ── UI scaffolding ────────────────────────────────────────────────────────

  private buildUI(): void {
    // Input row
    this.inputEl = h('input', {
      class: 'monitor-input',
      type: 'text',
      placeholder: 'Add keyword to monitor…',
    }) as unknown as HTMLInputElement;

    // Handle enter key
    this.inputEl.addEventListener('keydown', (e: Event) => {
      if ((e as KeyboardEvent).key === 'Enter') this.addKeyword();
    });

    this.addBtn = h(
      'button',
      {
        class: 'monitor-add-btn',
        onClick: () => this.addKeyword(),
      },
      '+ ADD',
    ) as unknown as HTMLButtonElement;

    const inputRow = h(
      'div',
      { class: 'monitor-input-row' },
      this.inputEl,
      this.addBtn,
    );

    // Active keyword list
    const keywordHeader = h('div', { class: 'monitor-section-header' }, 'ACTIVE MONITORS');
    this.keywordListEl = h('div', { class: 'monitor-keyword-list' });

    // Match list
    const matchHeader = h('div', { class: 'monitor-section-header' }, 'MATCHES');
    this.matchListEl = h('div', { class: 'monitor-match-list' });

    replaceChildren(
      this.body,
      inputRow,
      keywordHeader,
      this.keywordListEl,
      matchHeader,
      this.matchListEl,
    );

    this.renderKeywords();
    this.renderMatches();
  }

  // ── Keyword management ────────────────────────────────────────────────────

  private addKeyword(): void {
    const raw = this.inputEl.value.trim().toLowerCase();
    if (!raw || raw.length < 2) return;

    // Prevent duplicates
    if (this.keywords.find(k => k.keyword === raw)) {
      this.inputEl.value = '';
      return;
    }

    const kw: MonitorKeyword = {
      id: `kw-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      keyword: raw,
      matchCount: 0,
      lastMatch: null,
      createdAt: Date.now(),
    };

    this.keywords.push(kw);
    this.saveKeywords();
    this.inputEl.value = '';
    this.renderKeywords();
    this.updateBadge();
  }

  private removeKeyword(id: string): void {
    this.keywords = this.keywords.filter(k => k.id !== id);
    this.matchedItems = this.matchedItems.filter(
      m => this.keywords.some(k => k.keyword === m.keyword),
    );
    this.saveKeywords();
    this.renderKeywords();
    this.renderMatches();
    this.updateBadge();
  }

  // ── News listener ─────────────────────────────────────────────────────────

  private listenForNews(): void {
    document.addEventListener('wm:headlines', ((e: CustomEvent) => {
      const items: NewsItem[] = e.detail?.items ?? [];
      this.processNewsItems(items);
    }) as EventListener);
  }

  private processNewsItems(items: NewsItem[]): void {
    if (this.keywords.length === 0) return;

    let newMatches = 0;

    for (const item of items) {
      const titleLower = item.title.toLowerCase();
      const summaryLower = (item.summary ?? '').toLowerCase();
      const text = `${titleLower} ${summaryLower}`;

      for (const kw of this.keywords) {
        if (text.includes(kw.keyword)) {
          // Deduplicate — don't re-match same item for same keyword
          const alreadyMatched = this.matchedItems.some(
            m => m.keyword === kw.keyword && m.item.id === item.id,
          );
          if (alreadyMatched) continue;

          kw.matchCount++;
          kw.lastMatch = Date.now();
          newMatches++;

          this.matchedItems.push({ keyword: kw.keyword, item });
        }
      }
    }

    if (newMatches > 0) {
      // Keep matched items manageable
      if (this.matchedItems.length > 100) {
        this.matchedItems = this.matchedItems.slice(-100);
      }

      this.saveKeywords();
      this.renderKeywords();
      this.renderMatches();
      this.updateBadge();
    }
  }

  // ── Render keywords ───────────────────────────────────────────────────────

  private renderKeywords(): void {
    if (this.keywords.length === 0) {
      replaceChildren(
        this.keywordListEl,
        h('div', { class: 'monitor-empty' }, 'No keywords configured. Add one above.'),
      );
      return;
    }

    const rows = this.keywords.map(kw => {
      const badge = h(
        'span',
        { class: `monitor-count${kw.matchCount > 0 ? ' has-matches' : ''}` },
        String(kw.matchCount),
      );

      const lastMatchText = kw.lastMatch ? timeAgo(kw.lastMatch) : 'no matches';
      const meta = h('span', { class: 'monitor-kw-meta' }, lastMatchText);

      const deleteBtn = h(
        'button',
        {
          class: 'monitor-delete-btn',
          title: 'Remove keyword',
          onClick: () => this.removeKeyword(kw.id),
        },
        '✕',
      );

      const keywordText = h('span', { class: 'monitor-kw-text' }, kw.keyword);

      return h(
        'div',
        { class: 'monitor-keyword-row' },
        keywordText,
        badge,
        meta,
        deleteBtn,
      );
    });

    replaceChildren(this.keywordListEl, ...rows);
  }

  // ── Render matches ────────────────────────────────────────────────────────

  private renderMatches(): void {
    if (this.matchedItems.length === 0) {
      replaceChildren(
        this.matchListEl,
        h('div', { class: 'monitor-empty' }, 'Waiting for matching headlines…'),
      );
      return;
    }

    // Show most recent matches first, limit to 50
    const recent = [...this.matchedItems].reverse().slice(0, 50);

    const rows = recent.map(m => {
      const kwBadge = h('span', { class: 'monitor-match-kw' }, m.keyword);

      const headline = h(
        'a',
        {
          class: 'monitor-match-headline',
          href: m.item.url,
          target: '_blank',
          rel: 'noopener noreferrer',
        },
        m.item.title,
      );

      const time = h('span', { class: 'monitor-match-time' }, timeAgo(m.item.timestamp));

      return h(
        'div',
        { class: 'monitor-match-row' },
        kwBadge,
        headline,
        time,
      );
    });

    replaceChildren(this.matchListEl, ...rows);
  }

  // ── Badge ─────────────────────────────────────────────────────────────────

  private updateBadge(): void {
    const total = this.keywords.reduce((sum, kw) => sum + kw.matchCount, 0);
    this.setBadge(total);
    this.setFooter(
      `${this.keywords.length} keywords · ${total} total matches`,
    );
  }

  // ── Persistence ───────────────────────────────────────────────────────────

  private loadKeywords(): void {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        this.keywords = JSON.parse(raw);
      }
    } catch {
      this.keywords = [];
    }
  }

  private saveKeywords(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.keywords));
    } catch {
      // localStorage full — ignore
    }
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.renderKeywords();
    this.renderMatches();
    this.updateBadge();
  }

  protected onClose(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  protected render(): void {
    this.renderKeywords();
    this.renderMatches();
    this.updateBadge();
  }

  async refresh(): Promise<void> {
    this.render();
  }
}
