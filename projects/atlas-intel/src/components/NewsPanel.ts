// ============================================================================
// Atlas Intel — News Feed Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, timeAgo, replaceChildren } from '@/utils/dom-utils';
import { rssAggregator } from '@/services/rss-feeds';
import type { NewsItem, SourceTier } from '@/types/index';

// ---------------------------------------------------------------------------
// Filter definitions
// ---------------------------------------------------------------------------

interface FilterDef {
  label: string;
  key: string;               // 'all' or a ThreatCategory value
}

const FILTERS: FilterDef[] = [
  { label: 'All',            key: 'all' },
  { label: 'Military',       key: 'military' },
  { label: 'Conflict',       key: 'conflict' },
  { label: 'Cyber',          key: 'cyber' },
  { label: 'Nuclear',        key: 'nuclear' },
  { label: 'Terrorism',      key: 'terrorism' },
  { label: 'Unrest',         key: 'unrest' },
  { label: 'Economic',       key: 'economic' },
  { label: 'Health',         key: 'health' },
  { label: 'Energy',         key: 'energy' },
  { label: 'Aviation',       key: 'aviation' },
  { label: 'Maritime',       key: 'maritime' },
  { label: 'Infrastructure', key: 'infrastructure' },
  { label: 'Space',          key: 'space' },
];

// ---------------------------------------------------------------------------
// Tier labels & CSS classes
// ---------------------------------------------------------------------------

const TIER_LABELS: Record<SourceTier, string> = {
  1: 'T1',
  2: 'T2',
  3: 'T3',
  4: 'T4',
};

const TIER_CLASSES: Record<SourceTier, string> = {
  1: 'tier-1',
  2: 'tier-2',
  3: 'tier-3',
  4: 'tier-4',
};

// ---------------------------------------------------------------------------
// NewsPanel
// ---------------------------------------------------------------------------

export class NewsPanel extends Panel {
  private activeFilter = 'all';
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private filterBar!: HTMLElement;
  private listEl!: HTMLElement;

  constructor() {
    super({
      id: 'news',
      title: 'NEWS FEED',
      icon: '📰',
      description: 'Aggregated intelligence from RSS feeds worldwide',
      defaultOpen: false,
    });

    this.buildUI();
    this.render();
  }

  // ── UI scaffolding ──────────────────────────────────────────────────────

  private buildUI(): void {
    // Filter bar
    this.filterBar = h('div', { class: 'news-filter-bar' });
    this.buildFilterButtons();

    // Scrollable list
    this.listEl = h('div', { class: 'news-list' });

    replaceChildren(this.body, this.filterBar, this.listEl);
  }

  private buildFilterButtons(): void {
    const buttons = FILTERS.map(f => {
      const isActive = f.key === this.activeFilter;
      return h(
        'button',
        {
          class: `filter-btn${isActive ? ' active' : ''}`,
          'data-filter': f.key,
          onClick: () => this.setFilter(f.key),
        },
        f.label,
      );
    });
    replaceChildren(this.filterBar, ...buttons);
  }

  // ── Filter logic ────────────────────────────────────────────────────────

  private setFilter(key: string): void {
    this.activeFilter = key;
    this.buildFilterButtons();
    this.render();
  }

  private getFilteredItems(): NewsItem[] {
    const all = rssAggregator.getItems();
    if (this.activeFilter === 'all') return all;
    return all.filter(
      item => item.threatCategory === this.activeFilter,
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    const items = this.getFilteredItems();
    this.setBadge(items.length);

    if (items.length === 0) {
      replaceChildren(
        this.listEl,
        h('div', { class: 'news-empty' }, 'No items. Awaiting feed data…'),
      );
      this.setFooter('No data');
      return;
    }

    const elements = items.slice(0, 200).map(item => this.renderItem(item));
    replaceChildren(this.listEl, ...elements);

    const newest = items[0];
    this.setFooter(`${items.length} items · Updated ${timeAgo(newest.timestamp)}`);
  }

  private renderItem(item: NewsItem): HTMLElement {
    // --- Headline (linked) ---
    const headline = h(
      'a',
      {
        class: 'headline',
        href: item.url,
        target: '_blank',
        rel: 'noopener noreferrer',
      },
      item.title,
    );

    // --- Source tier indicator ---
    const tierBadge = h(
      'span',
      { class: `tier-badge ${TIER_CLASSES[item.sourceTier]}` },
      TIER_LABELS[item.sourceTier],
    );

    // --- Propaganda risk icon ---
    const propagandaIcon = item.propagandaRisk
      ? h('span', { class: 'propaganda-risk', title: 'Propaganda risk — state-affiliated source' }, ' ⚠')
      : null;

    // --- Source label ---
    const sourceName = h('span', { class: 'source-name' }, item.source);

    // --- Time ---
    const time = h('span', { class: 'time' }, timeAgo(item.timestamp));

    // --- Country (if available) ---
    const country = item.country
      ? h('span', { class: 'country' }, item.country)
      : null;

    // --- Meta line ---
    const metaChildren: (Node | string)[] = [
      tierBadge,
      sourceName,
    ];
    if (propagandaIcon) metaChildren.push(propagandaIcon);
    metaChildren.push(h('span', { class: 'meta-sep' }, '·'));
    metaChildren.push(time);
    if (country) {
      metaChildren.push(h('span', { class: 'meta-sep' }, '·'));
      metaChildren.push(country);
    }

    const meta = h('div', { class: 'meta' }, ...metaChildren);

    // --- Threat badge (if classified) ---
    const threatBadge = item.threatCategory
      ? h(
          'span',
          {
            class: `threat-badge threat-${item.threatCategory}`,
            title: `Classified: ${item.threatCategory}`,
          },
          item.threatCategory.toUpperCase(),
        )
      : null;

    // --- Assemble news item ---
    const children: (Node | string)[] = [headline, meta];
    if (threatBadge) children.push(threatBadge);

    return h('div', { class: 'news-item' }, ...children);
  }

  // ── Auto-refresh ────────────────────────────────────────────────────────

  protected onOpen(): void {
    // Kick off initial fetch then auto-refresh every 60 s
    this.doRefresh();
    this.refreshTimer = setInterval(() => this.doRefresh(), 60_000);
  }

  protected onClose(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  async refresh(): Promise<void> {
    await this.doRefresh();
  }

  private async doRefresh(): Promise<void> {
    try {
      this.setFooter('Fetching feeds…');
      await rssAggregator.fetchAll();
      this.render();
    } catch {
      this.setFooter('Feed fetch failed');
    }
  }
}
