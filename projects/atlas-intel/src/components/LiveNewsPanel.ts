// ============================================================================
// Atlas Intel — Live News Panel (YouTube iframe player)
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { LiveChannel } from '@/types/index';

// ---------------------------------------------------------------------------
// Channel definitions
// ---------------------------------------------------------------------------

const CHANNELS: LiveChannel[] = [
  { id: 'bloomberg',  name: 'Bloomberg TV', youtubeId: 'UCIALMKvObZNtJ68-rmLhXA', category: 'finance',  language: 'en' },
  { id: 'sky-news',   name: 'Sky News',     youtubeId: 'UCoMdktPbSTixAyNGwb-UYkQ', category: 'general',  language: 'en' },
  { id: 'euronews',   name: 'Euronews',     youtubeId: 'UCW2QaBMkkVszMr2sz6Jyp6w', category: 'general',  language: 'en' },
  { id: 'dw-news',    name: 'DW News',      youtubeId: 'UCknLrEdhRCp1aegoMqRaCZg', category: 'general',  language: 'en' },
  { id: 'cnbc',       name: 'CNBC',         youtubeId: 'UCvJJ_dzjViJCoLf5uKUTwoA', category: 'finance',  language: 'en' },
  { id: 'france24',   name: 'France 24',    youtubeId: 'UCQfwfsi5VDQ0dC-JB7JRz3Q', category: 'general',  language: 'en' },
  { id: 'aljazeera',  name: 'Al Jazeera',   youtubeId: 'UCNye-wNBqNL5ZzHSJj3l8Bg', category: 'general',  language: 'en' },
  { id: 'cnn',        name: 'CNN',          youtubeId: 'UCupvZG-5ko_eiXAupbDfxWw', category: 'general',  language: 'en' },
  { id: 'nbc-news',   name: 'NBC News',     youtubeId: 'UCeY0bbntWzzVIaj2z3QigXg', category: 'general',  language: 'en' },
];

// ---------------------------------------------------------------------------
// LiveNewsPanel
// ---------------------------------------------------------------------------

export class LiveNewsPanel extends Panel {
  private activeChannel: LiveChannel = CHANNELS[0];
  private isMuted = true;
  private playerContainer!: HTMLElement;
  private channelBar!: HTMLElement;
  private controlsBar!: HTMLElement;
  private iframeEl: HTMLIFrameElement | null = null;

  constructor() {
    super({
      id: 'live-news',
      title: 'LIVE NEWS',
      icon: '📡',
      description: 'Live broadcast news channels via YouTube',
      defaultOpen: false,
    });

    this.setBadge(CHANNELS.length);
    this.buildUI();
  }

  // ── UI scaffolding ──────────────────────────────────────────────────────

  private buildUI(): void {
    // Player container (holds iframe)
    this.playerContainer = h('div', { class: 'live-player' });

    // Controls bar (mute + live indicator)
    this.controlsBar = h('div', { class: 'live-controls' });
    this.renderControls();

    // Channel buttons
    this.channelBar = h('div', { class: 'live-channel-bar' });
    this.renderChannelButtons();

    replaceChildren(
      this.body,
      this.controlsBar,
      this.playerContainer,
      this.channelBar,
    );
  }

  // ── Controls (mute + live dot) ──────────────────────────────────────────

  private renderControls(): void {
    const liveDot = h('span', { class: 'live-dot' });
    const liveLabel = h('span', { class: 'live-label' }, 'LIVE');
    const liveIndicator = h('div', { class: 'live-indicator' }, liveDot, liveLabel);

    const muteBtn = h(
      'button',
      {
        class: 'mute-btn',
        title: this.isMuted ? 'Unmute' : 'Mute',
        onClick: () => this.toggleMute(),
      },
      this.isMuted ? '🔇' : '🔊',
    );

    const channelName = h(
      'span',
      { class: 'active-channel-name' },
      this.activeChannel.name,
    );

    replaceChildren(this.controlsBar, liveIndicator, channelName, muteBtn);
  }

  // ── Channel buttons ─────────────────────────────────────────────────────

  private renderChannelButtons(): void {
    const buttons = CHANNELS.map(ch => {
      const isActive = ch.id === this.activeChannel.id;
      return h(
        'button',
        {
          class: `channel-btn${isActive ? ' active' : ''}`,
          'data-channel': ch.id,
          title: ch.name,
          onClick: () => this.switchChannel(ch),
        },
        ch.name,
      );
    });

    replaceChildren(this.channelBar, ...buttons);
  }

  // ── Channel switching ───────────────────────────────────────────────────

  private switchChannel(channel: LiveChannel): void {
    if (channel.id === this.activeChannel.id) return;
    this.activeChannel = channel;
    this.renderChannelButtons();
    this.renderControls();
    this.loadPlayer();
    this.setFooter(`Now watching: ${channel.name}`);
  }

  // ── Player iframe ───────────────────────────────────────────────────────

  private loadPlayer(): void {
    // Build YouTube live embed URL
    const embedUrl = this.buildEmbedUrl(this.activeChannel.youtubeId);

    // Remove old iframe if present
    if (this.iframeEl) {
      this.iframeEl.remove();
      this.iframeEl = null;
    }

    const iframe = document.createElement('iframe');
    iframe.src = embedUrl;
    iframe.className = 'live-iframe';
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('allow', 'autoplay; encrypted-media');
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('loading', 'lazy');

    this.iframeEl = iframe;
    replaceChildren(this.playerContainer, iframe);
  }

  private buildEmbedUrl(youtubeChannelId: string): string {
    // Use the /live path which auto-resolves to the channel's current livestream
    const mute = this.isMuted ? 1 : 0;
    return (
      `https://www.youtube.com/embed/live_stream` +
      `?channel=${youtubeChannelId}` +
      `&autoplay=1` +
      `&mute=${mute}` +
      `&modestbranding=1` +
      `&rel=0` +
      `&controls=1`
    );
  }

  // ── Mute toggle ─────────────────────────────────────────────────────────

  private toggleMute(): void {
    this.isMuted = !this.isMuted;
    this.renderControls();
    // Reload iframe to apply mute state
    this.loadPlayer();
  }

  // ── Lifecycle ───────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.loadPlayer();
    this.setFooter(`Now watching: ${this.activeChannel.name}`);
  }

  protected onClose(): void {
    // Remove iframe to stop playback & save resources
    if (this.iframeEl) {
      this.iframeEl.remove();
      this.iframeEl = null;
    }
    replaceChildren(this.playerContainer);
  }

  async refresh(): Promise<void> {
    // Reload the current player
    if (this.isOpen) {
      this.loadPlayer();
    }
  }
}
