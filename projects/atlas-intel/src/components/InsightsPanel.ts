// ============================================================================
// Atlas Intel — Insights Panel (World Brief)
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren, timeAgo } from '@/utils/dom-utils';
import { aiSummarizer } from '@/services/ai-summarizer';
import type { AIBrief, AIProvider, NewsItem } from '@/types/index';

// ---------------------------------------------------------------------------
// InsightsPanel
// ---------------------------------------------------------------------------

export class InsightsPanel extends Panel {
  private briefContainer: HTMLElement | null = null;
  private focalContainer: HTMLElement | null = null;
  private providerBadge: HTMLElement | null = null;
  private generateBtn: HTMLElement | null = null;
  private refreshBtn: HTMLElement | null = null;
  private loadingIndicator: HTMLElement | null = null;
  private currentBrief: AIBrief | null = null;
  private isLoading = false;

  /** Externally supplied headlines (set by the app before calling refresh) */
  private headlines: NewsItem[] = [];

  constructor() {
    super({
      id: 'insights',
      title: 'WORLD BRIEF',
      icon: '🌐',
      description: 'AI-generated global intelligence brief',
      defaultOpen: false,
    });
    this.render();
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Set the headline source data for brief generation */
  setHeadlines(items: NewsItem[]): void {
    this.headlines = items;
  }

  /** Trigger a fresh brief generation */
  override async refresh(): Promise<void> {
    if (this.isLoading) return;
    await this.generateBrief();
  }

  // -------------------------------------------------------------------------
  // DOM Rendering
  // -------------------------------------------------------------------------

  protected override render(): void {
    // Loading indicator
    this.loadingIndicator = h('div', { class: 'insights-loading', style: 'display:none' },
      h('span', { class: 'spinner' }, '⟳'),
      h('span', null, ' Generating brief…'),
    );

    // Provider badge
    this.providerBadge = h('span', { class: 'provider-badge', style: 'display:none' });

    // Generate button
    this.generateBtn = h('button', {
      class: 'btn btn-primary insights-generate',
      onClick: () => { void this.generateBrief(); },
    }, '⚡ Generate Brief');

    // Refresh button
    this.refreshBtn = h('button', {
      class: 'btn btn-ghost insights-refresh',
      title: 'Regenerate brief',
      style: 'display:none',
      onClick: () => { void this.generateBrief(); },
    }, '↻ Refresh');

    // Toolbar
    const toolbar = h('div', { class: 'insights-toolbar' },
      this.generateBtn,
      this.refreshBtn,
      this.providerBadge,
    );

    // Brief content area
    this.briefContainer = h('div', { class: 'ai-brief' },
      h('p', { class: 'placeholder' }, 'Press "Generate Brief" to create an AI-powered summary of current global developments.'),
    );

    // Focal points area
    this.focalContainer = h('div', { class: 'insights-focal', style: 'display:none' });

    replaceChildren(
      this.body,
      this.loadingIndicator,
      toolbar,
      this.briefContainer,
      this.focalContainer,
    );
  }

  // -------------------------------------------------------------------------
  // Brief Generation
  // -------------------------------------------------------------------------

  private async generateBrief(): Promise<void> {
    if (this.isLoading) return;

    if (this.headlines.length === 0) {
      this.showError('No headlines available. Ensure news feeds are loaded.');
      return;
    }

    this.setLoading(true);

    try {
      const brief = await aiSummarizer.generateWorldBrief(this.headlines);
      this.currentBrief = brief;
      this.renderBrief(brief);
      this.renderFocalPoints(this.headlines);
      this.showProvider(brief.provider);
      this.setFooter(`Updated ${timeAgo(brief.timestamp)}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      this.showError(`Brief generation failed: ${msg}`);
    } finally {
      this.setLoading(false);
    }
  }

  // -------------------------------------------------------------------------
  // Render brief text with citation anchors
  // -------------------------------------------------------------------------

  private renderBrief(brief: AIBrief): void {
    if (!this.briefContainer) return;

    // Convert [N] references into clickable citation anchors
    const paragraphs = brief.text.split(/\n{2,}/);
    const elements: HTMLElement[] = [];

    for (const para of paragraphs) {
      if (!para.trim()) continue;
      const p = h('p', null);
      // Split on citation markers while preserving them
      const parts = para.split(/(\[\d+\])/g);
      for (const part of parts) {
        const citationMatch = part.match(/^\[(\d+)\]$/);
        if (citationMatch) {
          const idx = parseInt(citationMatch[1], 10);
          const anchor = h('a', {
            class: 'citation',
            'data-cite': String(idx),
            title: this.getCitationTitle(idx),
            onClick: () => this.onCitationClick(idx),
          }, `[${idx}]`);
          p.appendChild(anchor);
        } else {
          p.appendChild(document.createTextNode(part));
        }
      }
      elements.push(p);
    }

    replaceChildren(this.briefContainer, ...elements);
  }

  /** Get tooltip text for a citation index */
  private getCitationTitle(index: number): string {
    const item = this.headlines[index - 1];
    if (!item) return `Source [${index}]`;
    return `${item.title} — ${item.source}`;
  }

  /** Handle citation click — could scroll to or open the source */
  private onCitationClick(index: number): void {
    const item = this.headlines[index - 1];
    if (item?.url) {
      window.open(item.url, '_blank', 'noopener');
    }
  }

  // -------------------------------------------------------------------------
  // Focal point detection
  // -------------------------------------------------------------------------

  private renderFocalPoints(headlines: NewsItem[]): void {
    if (!this.focalContainer) return;

    const countryMentions = new Map<string, number>();
    const entityMentions = new Map<string, number>();

    for (const item of headlines) {
      // Count country mentions
      if (item.country) {
        countryMentions.set(item.country, (countryMentions.get(item.country) || 0) + 1);
      }
      if (item.countries) {
        for (const c of item.countries) {
          countryMentions.set(c, (countryMentions.get(c) || 0) + 1);
        }
      }

      // Extract simple entity mentions from titles (capitalized multi-word sequences)
      const entityMatches = item.title.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+/g);
      if (entityMatches) {
        for (const entity of entityMatches) {
          entityMentions.set(entity, (entityMentions.get(entity) || 0) + 1);
        }
      }
    }

    // Sort by frequency, take top entries
    const topCountries = [...countryMentions.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    const topEntities = [...entityMentions.entries()]
      .filter(([, count]) => count >= 2)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    if (topCountries.length === 0 && topEntities.length === 0) {
      this.focalContainer.style.display = 'none';
      return;
    }

    const tags: HTMLElement[] = [];

    if (topCountries.length > 0) {
      tags.push(h('span', { class: 'focal-label' }, 'Focal countries:'));
      for (const [name, count] of topCountries) {
        tags.push(h('span', { class: 'focal-tag country' }, `${name} (${count})`));
      }
    }

    if (topEntities.length > 0) {
      tags.push(h('span', { class: 'focal-label' }, 'Key entities:'));
      for (const [name, count] of topEntities) {
        tags.push(h('span', { class: 'focal-tag entity' }, `${name} (${count})`));
      }
    }

    replaceChildren(this.focalContainer, ...tags);
    this.focalContainer.style.display = '';
  }

  // -------------------------------------------------------------------------
  // Provider indicator
  // -------------------------------------------------------------------------

  private showProvider(provider: AIProvider): void {
    if (!this.providerBadge) return;

    const labels: Record<AIProvider, string> = {
      ollama: '🦙 Ollama',
      groq: '⚡ Groq',
      openrouter: '🌐 OpenRouter',
      'browser-t5': '🧠 Browser T5',
    };

    this.providerBadge.textContent = labels[provider] || provider;
    this.providerBadge.style.display = 'inline-flex';
  }

  // -------------------------------------------------------------------------
  // UI state helpers
  // -------------------------------------------------------------------------

  private setLoading(loading: boolean): void {
    this.isLoading = loading;

    if (this.loadingIndicator) {
      this.loadingIndicator.style.display = loading ? 'flex' : 'none';
    }
    if (this.generateBtn) {
      (this.generateBtn as HTMLButtonElement).disabled = loading;
      this.generateBtn.style.display = this.currentBrief ? 'none' : '';
    }
    if (this.refreshBtn) {
      (this.refreshBtn as HTMLButtonElement).disabled = loading;
      this.refreshBtn.style.display = this.currentBrief ? '' : 'none';
    }
  }

  private showError(message: string): void {
    if (!this.briefContainer) return;
    replaceChildren(
      this.briefContainer,
      h('p', { class: 'error' }, `⚠ ${message}`),
    );
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  protected override onOpen(): void {
    // Auto-generate if we have headlines but no brief yet
    if (this.headlines.length > 0 && !this.currentBrief) {
      void this.generateBrief();
    }
  }
}
