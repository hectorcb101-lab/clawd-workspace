// ============================================================================
// Atlas Intel — Main App Controller
// Builds the app shell (top bar, map container, bottom bar, scanlines),
// manages panels, settings, clock, URL state, and keyboard shortcuts.
// ============================================================================

import { h } from '@/utils/dom-utils';
import { dataBridge } from '@/services/data-bridge';
import { Panel } from '@/components/Panel';
import type { AppSettings, BreakingAlert, MapEngine, URLState } from '@/types/index';

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_SETTINGS: AppSettings = {
  mapEngine: '3d',
  renderQuality: 'auto',
  tileProvider: 'openfreemap',
  mapTheme: 'dark',
  aiProvider: 'ollama',
  ollamaEndpoint: 'http://localhost:11434',
  language: 'en',
  enableML: false,
  enableHeadlineMemory: false,
  enableScanlines: true,
};

const VERSION = '2.0.0';

// ============================================================================
// App
// ============================================================================

export class App {
  private root: HTMLElement;
  private panels = new Map<string, Panel>();
  private settings: AppSettings;
  private clockTimer: ReturnType<typeof setInterval> | null = null;
  private mapEngine: MapEngine = '3d';

  // DOM references
  private topBar!: HTMLElement;
  private mainContainer!: HTMLElement;
  private mapContainer!: HTMLElement;
  private bottomBar!: HTMLElement;
  private clockEl!: HTMLElement;
  private scanlines!: HTMLElement;
  private defconEl!: HTMLElement;
  private signalCountEl!: HTMLElement;
  private dataSourceCountEl!: HTMLElement;
  private commandPalette!: HTMLElement;
  private commandInput!: HTMLInputElement;
  private commandResults!: HTMLElement;
  private statusDots!: { data: HTMLElement; map: HTMLElement; ai: HTMLElement };
  private breakingBannerEl: HTMLElement | null = null;
  private breakingBannerTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(root: HTMLElement) {
    this.root = root;
    this.settings = this.loadSettings();
    this.mapEngine = this.settings.mapEngine;
    this.buildLayout();
    this.startClock();
    this.parseURLState();
    this.setupKeyboardShortcuts();
    this.listenForDataStatus();
  }

  // --------------------------------------------------------------------------
  // Settings persistence
  // --------------------------------------------------------------------------

  private loadSettings(): AppSettings {
    try {
      const saved = localStorage.getItem('atlas-settings');
      if (saved) return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
    } catch { /* ignore corrupt data */ }
    return { ...DEFAULT_SETTINGS };
  }

  saveSettings(): void {
    localStorage.setItem('atlas-settings', JSON.stringify(this.settings));
  }

  // --------------------------------------------------------------------------
  // Layout construction
  // --------------------------------------------------------------------------

  private buildLayout(): void {
    // ── Scanlines overlay ──────────────────────────────────────────────
    this.scanlines = h('div', { class: 'scanlines' });
    if (!this.settings.enableScanlines) {
      this.scanlines.style.display = 'none';
    }

    // ── Top bar ────────────────────────────────────────────────────────

    // Left: title + classification badge
    const titleSection = h(
      'div',
      { class: 'title-section' },
      h('h1', null, 'ATLAS INTEL'),
      h('span', { class: 'classification' }, 'OSINT // UNCLASSIFIED'),
    );

    // Center: DEFCON indicator + signal badge
    this.defconEl = h(
      'div',
      { class: 'defcon-indicator defcon-5' },
      h('span', null, '⬟'),
      h('span', null, 'DEFCON 5'),
    );

    this.signalCountEl = h('span', { class: 'count' }, '0');
    const signalBadge = h(
      'div',
      {
        class: 'signal-badge',
        onClick: () => {
          const signalsPanel = this.panels.get('signals');
          if (signalsPanel) signalsPanel.toggle();
        },
      },
      h('span', null, '⚡ SIGNALS'),
      this.signalCountEl,
    );

    const centerSection = h(
      'div',
      { class: 'center-section' },
      this.defconEl,
      signalBadge,
    );

    // Right: UTC clock + system status dots
    this.clockEl = h('span', { class: 'utc-clock' }, '--:--:--Z');

    const dataDot = h('span', { class: 'status-dot' });
    const mapDot = h('span', { class: 'status-dot' });
    const aiDot = h('span', { class: 'status-dot' });
    this.statusDots = { data: dataDot, map: mapDot, ai: aiDot };

    const systemStatus = h(
      'div',
      { class: 'system-status' },
      h('div', { class: 'status-indicator' }, dataDot, h('span', null, 'DATA')),
      h('div', { class: 'status-indicator' }, mapDot, h('span', null, 'MAP')),
      h('div', { class: 'status-indicator' }, aiDot, h('span', null, 'AI')),
    );

    const statusSection = h(
      'div',
      { class: 'status-section' },
      this.clockEl,
      systemStatus,
    );

    this.topBar = h(
      'div',
      { class: 'top-bar' },
      titleSection,
      centerSection,
      statusSection,
    );

    // ── Main container + map ──────────────────────────────────────────
    this.mapContainer = h('div', { class: 'map-container' });

    this.mainContainer = h(
      'div',
      { class: 'main-container' },
      this.mapContainer,
    );

    // ── Bottom bar ────────────────────────────────────────────────────
    this.dataSourceCountEl = h('span', null, '0');
    const bottomLeft = h(
      'div',
      { class: 'bottom-bar-left' },
      h('span', null, '◉ DATA SOURCES: '),
      this.dataSourceCountEl,
      h('span', null, ` / ${dataBridge.sources.length}`),
    );

    const bottomRight = h(
      'div',
      { class: 'bottom-bar-right' },
      h('span', null, `ATLAS INTEL v${VERSION}`),
      h('span', { style: 'margin: 0 8px; opacity: 0.3' }, '|'),
      h('span', null, 'ENGINE: '),
      h('span', { style: 'color: var(--accent)' }, this.mapEngine.toUpperCase()),
    );

    this.bottomBar = h(
      'div',
      { class: 'bottom-bar' },
      bottomLeft,
      bottomRight,
    );

    // ── Command palette (Cmd+K) ──────────────────────────────────────
    this.commandInput = document.createElement('input');
    this.commandInput.type = 'text';
    this.commandInput.placeholder = 'Search panels, layers, countries…';
    this.commandInput.addEventListener('input', () => this.onCommandInput());
    this.commandInput.addEventListener('keydown', (e) => this.onCommandKeydown(e));

    this.commandResults = h('div', { class: 'results' });

    const paletteBox = h(
      'div',
      { class: 'palette-box' },
      this.commandInput,
      this.commandResults,
    );

    this.commandPalette = h(
      'div',
      {
        class: 'command-palette',
        onClick: (e: Event) => {
          // Close when clicking backdrop (not the box itself)
          if (e.target === this.commandPalette) this.closeCommandPalette();
        },
      },
      paletteBox,
    );

    // ── Assemble into root ───────────────────────────────────────────
    this.root.appendChild(this.scanlines);
    this.root.appendChild(this.topBar);
    this.root.appendChild(this.mainContainer);
    this.root.appendChild(this.bottomBar);
    this.root.appendChild(this.commandPalette);
  }

  // --------------------------------------------------------------------------
  // Clock
  // --------------------------------------------------------------------------

  private startClock(): void {
    const updateClock = () => {
      const now = new Date();
      this.clockEl.textContent = now.toISOString().slice(11, 19) + 'Z';
    };
    updateClock();
    this.clockTimer = setInterval(updateClock, 1000);
  }

  // --------------------------------------------------------------------------
  // URL state
  // --------------------------------------------------------------------------

  private parseURLState(): void {
    const params = new URLSearchParams(window.location.search);

    const state: Partial<URLState> = {};

    const lat = params.get('lat');
    const lng = params.get('lng');
    const zoom = params.get('zoom');
    const layers = params.get('layers');
    const timeRange = params.get('timeRange');
    const engine = params.get('engine');
    const panel = params.get('panel');
    const country = params.get('country');

    if (lat) state.lat = parseFloat(lat);
    if (lng) state.lng = parseFloat(lng);
    if (zoom) state.zoom = parseFloat(zoom);
    if (layers) state.layers = layers.split(',');
    if (timeRange) state.timeRange = timeRange as URLState['timeRange'];
    if (engine && (engine === '2d' || engine === '3d')) {
      state.engine = engine;
      this.mapEngine = engine;
    }
    if (panel) state.panel = panel;
    if (country) state.country = country;

    // If a specific panel was requested, open it once registered
    if (state.panel) {
      // Defer: panels may not be registered yet
      requestAnimationFrame(() => {
        const p = this.panels.get(state.panel!);
        if (p && !p.isOpen) p.open();
      });
    }

    // Emit parsed state for map and panels to consume
    if (Object.keys(state).length > 0) {
      window.dispatchEvent(new CustomEvent('atlas:url-state', { detail: state }));
    }
  }

  updateURL(state: Partial<URLState>): void {
    const params = new URLSearchParams(window.location.search);

    if (state.lat !== undefined) params.set('lat', state.lat.toFixed(4));
    if (state.lng !== undefined) params.set('lng', state.lng.toFixed(4));
    if (state.zoom !== undefined) params.set('zoom', state.zoom.toFixed(1));
    if (state.layers !== undefined) {
      if (state.layers.length > 0) {
        params.set('layers', state.layers.join(','));
      } else {
        params.delete('layers');
      }
    }
    if (state.timeRange !== undefined) params.set('timeRange', state.timeRange);
    if (state.engine !== undefined) params.set('engine', state.engine);
    if (state.panel !== undefined) {
      if (state.panel) { params.set('panel', state.panel); } else { params.delete('panel'); }
    }
    if (state.country !== undefined) {
      if (state.country) { params.set('country', state.country); } else { params.delete('country'); }
    }

    const qs = params.toString();
    const url = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    window.history.pushState(null, '', url);
  }

  // --------------------------------------------------------------------------
  // Keyboard shortcuts
  // --------------------------------------------------------------------------

  private setupKeyboardShortcuts(): void {
    document.addEventListener('keydown', (e) => {
      // Cmd+K / Ctrl+K — toggle command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.toggleCommandPalette();
        return;
      }

      // Escape — close command palette, then close topmost open panel
      if (e.key === 'Escape') {
        if (this.commandPalette.classList.contains('open')) {
          this.closeCommandPalette();
          return;
        }
        // Close the last-opened visible panel
        const openPanels = this.getAllPanels().filter((p) => p.isOpen);
        if (openPanels.length > 0) {
          openPanels[openPanels.length - 1].close();
        }
        return;
      }
    });
  }

  // --------------------------------------------------------------------------
  // Command palette
  // --------------------------------------------------------------------------

  private toggleCommandPalette(): void {
    if (this.commandPalette.classList.contains('open')) {
      this.closeCommandPalette();
    } else {
      this.openCommandPalette();
    }
  }

  private openCommandPalette(): void {
    this.commandPalette.classList.add('open');
    this.commandInput.value = '';
    this.commandResults.innerHTML = '';
    this.populateCommandDefaults();
    // Focus after transition
    requestAnimationFrame(() => this.commandInput.focus());
  }

  private closeCommandPalette(): void {
    this.commandPalette.classList.remove('open');
    this.commandInput.blur();
  }

  private populateCommandDefaults(): void {
    this.commandResults.innerHTML = '';
    for (const panel of this.panels.values()) {
      const item = h(
        'div',
        {
          class: 'result-item',
          onClick: () => {
            panel.toggle();
            this.closeCommandPalette();
          },
        },
        h('span', null, `${panel.config.icon} ${panel.config.title}`),
      );
      this.commandResults.appendChild(item);
    }
  }

  private onCommandInput(): void {
    const query = this.commandInput.value.toLowerCase().trim();
    this.commandResults.innerHTML = '';

    if (!query) {
      this.populateCommandDefaults();
      return;
    }

    // Filter panels by query
    for (const panel of this.panels.values()) {
      const text = `${panel.config.title} ${panel.config.description}`.toLowerCase();
      if (text.includes(query)) {
        const item = h(
          'div',
          {
            class: 'result-item',
            onClick: () => {
              panel.toggle();
              this.closeCommandPalette();
            },
          },
          h('span', null, `${panel.config.icon} ${panel.config.title}`),
        );
        this.commandResults.appendChild(item);
      }
    }

    // If no results, show empty state
    if (this.commandResults.children.length === 0) {
      this.commandResults.appendChild(
        h('div', { class: 'result-item', style: 'color: var(--text-dim); pointer-events: none' }, 'No results'),
      );
    }
  }

  private onCommandKeydown(e: KeyboardEvent): void {
    const items = this.commandResults.querySelectorAll('.result-item:not([style*="pointer-events"])');
    const selected = this.commandResults.querySelector('.result-item.selected');
    let idx = -1;
    items.forEach((item, i) => {
      if (item === selected) idx = i;
    });

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (selected) selected.classList.remove('selected');
      const next = idx + 1 < items.length ? idx + 1 : 0;
      items[next]?.classList.add('selected');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (selected) selected.classList.remove('selected');
      const prev = idx - 1 >= 0 ? idx - 1 : items.length - 1;
      items[prev]?.classList.add('selected');
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selected) {
        (selected as HTMLElement).click();
      } else if (items.length > 0) {
        (items[0] as HTMLElement).click();
      }
    }
  }

  // --------------------------------------------------------------------------
  // Data status watcher
  // --------------------------------------------------------------------------

  private listenForDataStatus(): void {
    // Periodically update the data source count and status dots
    setInterval(() => {
      const statuses = dataBridge.getStatus();
      const liveCount = statuses.filter((s) => s.status === 'live').length;
      this.dataSourceCountEl.textContent = String(liveCount);

      // Data dot: green if any are live, amber if only cached, red if all unavailable
      if (liveCount > 0) {
        this.statusDots.data.className = 'status-dot online';
      } else if (statuses.some((s) => s.status === 'cached')) {
        this.statusDots.data.className = 'status-dot warning';
      } else {
        this.statusDots.data.className = 'status-dot error';
      }
    }, 5_000);
  }

  // --------------------------------------------------------------------------
  // DEFCON
  // --------------------------------------------------------------------------

  /** Update the DEFCON indicator (1-5). */
  setDefcon(level: number): void {
    const clamped = Math.max(1, Math.min(5, Math.round(level)));
    this.defconEl.className = `defcon-indicator defcon-${clamped}`;
    this.defconEl.innerHTML = '';
    this.defconEl.appendChild(h('span', null, '⬟'));
    this.defconEl.appendChild(h('span', null, `DEFCON ${clamped}`));
  }

  /** Update the signal count badge. */
  setSignalCount(count: number): void {
    this.signalCountEl.textContent = String(count);
  }

  /** Set a status dot state. */
  setStatusDot(system: 'data' | 'map' | 'ai', state: 'online' | 'warning' | 'error'): void {
    this.statusDots[system].className = `status-dot ${state}`;
  }

  // --------------------------------------------------------------------------
  // Panel management
  // --------------------------------------------------------------------------

  /** Register a panel with the app. */
  registerPanel(panel: Panel): void {
    this.panels.set(panel.id, panel);
    panel.mount(document.body);
  }

  /** Get a panel by id. */
  getPanel(id: string): Panel | undefined {
    return this.panels.get(id);
  }

  /** Get all registered panels. */
  getAllPanels(): Panel[] {
    return Array.from(this.panels.values());
  }

  // --------------------------------------------------------------------------
  // Accessors
  // --------------------------------------------------------------------------

  /** Get the map container element. */
  getMapContainer(): HTMLElement {
    return this.mapContainer;
  }

  /** Get current settings (copy). */
  getSettings(): AppSettings {
    return { ...this.settings };
  }

  /** Update settings and broadcast change. */
  updateSettings(partial: Partial<AppSettings>): void {
    Object.assign(this.settings, partial);
    this.saveSettings();

    // Toggle scanlines
    if (partial.enableScanlines !== undefined) {
      this.scanlines.style.display = partial.enableScanlines ? '' : 'none';
    }

    // Update engine display if changed
    if (partial.mapEngine) {
      this.mapEngine = partial.mapEngine;
    }

    window.dispatchEvent(new CustomEvent('atlas:settings-changed', { detail: this.settings }));
  }

  /** Get current map engine. */
  getMapEngine(): MapEngine {
    return this.mapEngine;
  }

  // --------------------------------------------------------------------------
  // Breaking news banner
  // --------------------------------------------------------------------------

  /** Show a breaking news banner at the top of the viewport. Auto-hides after 10s. */
  showBreakingBanner(alert: BreakingAlert): void {
    // Create the banner element on first use
    if (!this.breakingBannerEl) {
      this.breakingBannerEl = h(
        'div',
        { class: 'breaking-banner' },
        h('span', { class: 'tag' }, 'BREAKING'),
        h('span', { class: 'text' }, ''),
      );
      this.root.appendChild(this.breakingBannerEl);
    }

    // Update content
    const tagEl = this.breakingBannerEl.querySelector('.tag') as HTMLElement;
    const textEl = this.breakingBannerEl.querySelector('.text') as HTMLElement;
    if (tagEl) tagEl.textContent = 'BREAKING';
    if (textEl) textEl.textContent = alert.title;

    // Show with animation
    this.breakingBannerEl.classList.add('visible');

    // Clear any existing auto-hide timer
    if (this.breakingBannerTimer) {
      clearTimeout(this.breakingBannerTimer);
    }

    // Auto-hide after 10 seconds
    this.breakingBannerTimer = setTimeout(() => {
      this.breakingBannerEl?.classList.remove('visible');
      this.breakingBannerTimer = null;
    }, 10_000);
  }

  // --------------------------------------------------------------------------
  // DEFCON mount point
  // --------------------------------------------------------------------------

  /** Get the DEFCON indicator element in the top bar for external component mounting. */
  getDefconMount(): HTMLElement {
    return this.defconEl;
  }

  // --------------------------------------------------------------------------
  // Lifecycle
  // --------------------------------------------------------------------------

  /** Start data bridge and refresh all open panels. */
  async start(): Promise<void> {
    dataBridge.startAll();

    // Mark map dot as online once we've started
    this.statusDots.map.className = 'status-dot online';

    // Refresh all open panels
    for (const panel of this.panels.values()) {
      if (panel.isOpen) panel.refresh();
    }
  }

  /** Stop all polling and timers. */
  stop(): void {
    dataBridge.stopAll();
    if (this.clockTimer) {
      clearInterval(this.clockTimer);
      this.clockTimer = null;
    }
  }

  /** Destroy app — stop everything, tear down DOM. */
  destroy(): void {
    this.stop();
    for (const panel of this.panels.values()) {
      panel.destroy();
    }
    this.panels.clear();
    this.root.innerHTML = '';
  }
}
