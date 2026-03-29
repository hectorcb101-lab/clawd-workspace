// ============================================================================
// Atlas Intel — Live Webcams Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { Webcam } from '@/types/index';

// ---------------------------------------------------------------------------
// localStorage key for pinned webcams
// ---------------------------------------------------------------------------

const PINNED_KEY = 'atlas-intel-pinned-webcams';

// ---------------------------------------------------------------------------
// Mock strategic-location webcams
// ---------------------------------------------------------------------------

function getWebcams(): Webcam[] {
  return [
    {
      id: 'cam-01',
      name: 'Strait of Hormuz',
      location: 'Oman / Iran',
      lat: 26.57,
      lng: 56.25,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Hormuz',
      streamUrl: 'https://example.com/stream/hormuz',
    },
    {
      id: 'cam-02',
      name: 'Suez Canal — Port Said',
      location: 'Egypt',
      lat: 31.26,
      lng: 32.30,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Suez',
      streamUrl: 'https://example.com/stream/suez',
    },
    {
      id: 'cam-03',
      name: 'Bosphorus Strait',
      location: 'Istanbul, Turkey',
      lat: 41.12,
      lng: 29.07,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Bosphorus',
      streamUrl: 'https://example.com/stream/bosphorus',
    },
    {
      id: 'cam-04',
      name: 'Panama Canal — Miraflores',
      location: 'Panama',
      lat: 9.01,
      lng: -79.59,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Panama',
      streamUrl: 'https://example.com/stream/panama',
    },
    {
      id: 'cam-05',
      name: 'Taiwan Strait',
      location: 'Taiwan',
      lat: 24.50,
      lng: 119.50,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Taiwan+Strait',
      streamUrl: 'https://example.com/stream/taiwan-strait',
    },
    {
      id: 'cam-06',
      name: 'Kaliningrad Port',
      location: 'Russia',
      lat: 54.71,
      lng: 20.51,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Kaliningrad',
      streamUrl: 'https://example.com/stream/kaliningrad',
    },
    {
      id: 'cam-07',
      name: 'Sevastopol Harbor',
      location: 'Crimea',
      lat: 44.62,
      lng: 33.53,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Sevastopol',
      streamUrl: 'https://example.com/stream/sevastopol',
    },
    {
      id: 'cam-08',
      name: 'DMZ — Panmunjom',
      location: 'South Korea',
      lat: 37.96,
      lng: 126.68,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=DMZ',
      streamUrl: 'https://example.com/stream/dmz',
    },
    {
      id: 'cam-09',
      name: 'Strait of Malacca',
      location: 'Singapore / Malaysia',
      lat: 1.27,
      lng: 103.75,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Malacca',
      streamUrl: 'https://example.com/stream/malacca',
    },
    {
      id: 'cam-10',
      name: 'Gibraltar Strait',
      location: 'Spain / Morocco',
      lat: 35.97,
      lng: -5.50,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Gibraltar',
      streamUrl: 'https://example.com/stream/gibraltar',
    },
    {
      id: 'cam-11',
      name: 'Djibouti — Camp Lemonnier',
      location: 'Djibouti',
      lat: 11.55,
      lng: 43.15,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Djibouti',
      streamUrl: 'https://example.com/stream/djibouti',
    },
    {
      id: 'cam-12',
      name: 'Bab el-Mandeb Strait',
      location: 'Yemen / Djibouti',
      lat: 12.58,
      lng: 43.33,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Bab+el-Mandeb',
      streamUrl: 'https://example.com/stream/bab-el-mandeb',
    },
    {
      id: 'cam-13',
      name: 'Ramstein Air Base',
      location: 'Germany',
      lat: 49.44,
      lng: 7.60,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Ramstein',
      streamUrl: 'https://example.com/stream/ramstein',
    },
    {
      id: 'cam-14',
      name: 'Yokosuka Naval Base',
      location: 'Japan',
      lat: 35.28,
      lng: 139.67,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Yokosuka',
      streamUrl: 'https://example.com/stream/yokosuka',
    },
    {
      id: 'cam-15',
      name: 'Diego Garcia',
      location: 'Indian Ocean (UK/US)',
      lat: -7.32,
      lng: 72.42,
      thumbUrl: 'https://placehold.co/320x180/1a1a2e/00e676?text=Diego+Garcia',
      streamUrl: 'https://example.com/stream/diego-garcia',
    },
  ];
}

// ---------------------------------------------------------------------------
// LiveWebcamsPanel
// ---------------------------------------------------------------------------

export class LiveWebcamsPanel extends Panel {
  private gridEl!: HTMLElement;
  private filterBarEl!: HTMLElement;
  private expandedOverlay: HTMLElement | null = null;
  private webcams: Webcam[] = [];
  private pinnedIds: Set<string>;
  private showPinnedOnly = false;

  constructor() {
    super({
      id: 'webcams',
      title: 'LIVE WEBCAMS',
      icon: '📷',
      description: 'Strategic location webcams with pin/unpin favourites',
      defaultOpen: false,
    });

    this.pinnedIds = this.loadPinned();
    this.buildUI();
    this.render();
  }

  // ── Pinned state persistence ────────────────────────────────────────────

  private loadPinned(): Set<string> {
    try {
      const raw = localStorage.getItem(PINNED_KEY);
      if (raw) return new Set(JSON.parse(raw) as string[]);
    } catch { /* ignore */ }
    return new Set();
  }

  private savePinned(): void {
    try {
      localStorage.setItem(PINNED_KEY, JSON.stringify([...this.pinnedIds]));
    } catch { /* ignore */ }
  }

  private togglePin(id: string): void {
    if (this.pinnedIds.has(id)) {
      this.pinnedIds.delete(id);
    } else {
      this.pinnedIds.add(id);
    }
    this.savePinned();
    this.render();
  }

  // ── UI scaffolding ──────────────────────────────────────────────────────

  private buildUI(): void {
    this.filterBarEl = h('div', { class: 'webcam-filter-bar' });
    this.gridEl = h('div', { class: 'webcam-grid' });
    replaceChildren(this.body, this.filterBarEl, this.gridEl);
    this.renderFilterBar();
  }

  private renderFilterBar(): void {
    const allBtn = h(
      'button',
      {
        class: `filter-btn${!this.showPinnedOnly ? ' active' : ''}`,
        onClick: () => {
          this.showPinnedOnly = false;
          this.renderFilterBar();
          this.render();
        },
      },
      `All (${this.webcams.length})`,
    );

    const pinnedBtn = h(
      'button',
      {
        class: `filter-btn${this.showPinnedOnly ? ' active' : ''}`,
        onClick: () => {
          this.showPinnedOnly = true;
          this.renderFilterBar();
          this.render();
        },
      },
      `📌 Pinned (${this.pinnedIds.size})`,
    );

    replaceChildren(this.filterBarEl, allBtn, pinnedBtn);
  }

  // ── Render ──────────────────────────────────────────────────────────────

  protected render(): void {
    this.renderFilterBar();

    if (this.webcams.length === 0) {
      replaceChildren(
        this.gridEl,
        h('div', { class: 'webcam-empty' }, 'Awaiting webcam data…'),
      );
      this.setFooter('No data');
      return;
    }

    let visible = this.webcams;
    if (this.showPinnedOnly) {
      visible = this.webcams.filter(w => this.pinnedIds.has(w.id));
    }

    // Sort: pinned first, then alphabetical by name
    visible = [...visible].sort((a, b) => {
      const aPinned = this.pinnedIds.has(a.id) ? 0 : 1;
      const bPinned = this.pinnedIds.has(b.id) ? 0 : 1;
      if (aPinned !== bPinned) return aPinned - bPinned;
      return a.name.localeCompare(b.name);
    });

    if (visible.length === 0) {
      replaceChildren(
        this.gridEl,
        h('div', { class: 'webcam-empty' }, 'No pinned webcams. Pin some to see them here.'),
      );
      this.setFooter('No pinned webcams');
      return;
    }

    const thumbs = visible.map(w => this.renderThumb(w));
    replaceChildren(this.gridEl, ...thumbs);

    this.setBadge(visible.length);
    this.setFooter(`${visible.length} webcams · ${this.pinnedIds.size} pinned`);
  }

  private renderThumb(webcam: Webcam): HTMLElement {
    const isPinned = this.pinnedIds.has(webcam.id);

    // Thumbnail image
    const img = h('img', {
      class: 'webcam-img',
      src: webcam.thumbUrl,
      alt: webcam.name,
      loading: 'lazy',
    }) as HTMLImageElement;

    // Pin button (top-right corner of thumbnail)
    const pinBtn = h(
      'button',
      {
        class: `webcam-pin${isPinned ? ' pinned' : ''}`,
        title: isPinned ? 'Unpin' : 'Pin',
        onClick: (e: Event) => {
          e.stopPropagation();
          this.togglePin(webcam.id);
        },
      },
      isPinned ? '📌' : '📍',
    );

    // Location label overlay
    const label = h(
      'div',
      { class: 'webcam-label' },
      h('div', { class: 'webcam-name' }, webcam.name),
      h('div', { class: 'webcam-location' }, webcam.location),
    );

    // Webcam thumbnail card — click to expand
    const thumb = h(
      'div',
      {
        class: `webcam-thumb${isPinned ? ' is-pinned' : ''}`,
        onClick: () => this.expandWebcam(webcam),
      },
      img,
      pinBtn,
      label,
    );

    return thumb;
  }

  // ── Expanded view ───────────────────────────────────────────────────────

  private expandWebcam(webcam: Webcam): void {
    // Remove existing overlay if any
    this.closeExpanded();

    const img = h('img', {
      class: 'webcam-expanded-img',
      src: webcam.thumbUrl,
      alt: webcam.name,
    });

    const title = h('div', { class: 'webcam-expanded-title' }, webcam.name);
    const loc = h('div', { class: 'webcam-expanded-location' }, webcam.location);
    const coords = h(
      'div',
      { class: 'webcam-expanded-coords' },
      `${webcam.lat.toFixed(2)}°, ${webcam.lng.toFixed(2)}°`,
    );

    const streamLink = h(
      'a',
      {
        class: 'webcam-stream-link',
        href: webcam.streamUrl,
        target: '_blank',
        rel: 'noopener noreferrer',
      },
      '▶ Open Stream',
    );

    const closeBtn = h(
      'button',
      {
        class: 'webcam-expanded-close',
        onClick: () => this.closeExpanded(),
      },
      '✕',
    );

    const content = h(
      'div',
      { class: 'webcam-expanded-content' },
      closeBtn,
      img,
      title,
      loc,
      coords,
      streamLink,
    );

    this.expandedOverlay = h(
      'div',
      {
        class: 'webcam-expanded-overlay',
        onClick: (e: Event) => {
          if (e.target === this.expandedOverlay) this.closeExpanded();
        },
      },
      content,
    );

    this.body.appendChild(this.expandedOverlay);
  }

  private closeExpanded(): void {
    if (this.expandedOverlay) {
      this.expandedOverlay.remove();
      this.expandedOverlay = null;
    }
  }

  // ── Lifecycle ───────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.doRefresh();
  }

  protected onClose(): void {
    this.closeExpanded();
  }

  async refresh(): Promise<void> {
    await this.doRefresh();
  }

  private async doRefresh(): Promise<void> {
    try {
      this.setFooter('Loading webcams…');
      // In production, fetch from webcam APIs / Windy / etc.
      this.webcams = getWebcams();
      // Restore pinned state onto webcam objects
      this.webcams.forEach(w => {
        w.pinned = this.pinnedIds.has(w.id);
      });
      this.render();
    } catch {
      this.setFooter('Webcam data load failed');
    }
  }
}
