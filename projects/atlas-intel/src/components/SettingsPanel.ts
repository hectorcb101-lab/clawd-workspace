// ============================================================================
// Atlas Intel — Settings Panel
// ============================================================================

import { Panel } from '@/components/Panel';
import { h, replaceChildren } from '@/utils/dom-utils';
import type { AppSettings, AIProvider, MapEngine, RenderQuality, TileProvider, MapTheme } from '@/types/index';

// ---------------------------------------------------------------------------
// Option definitions
// ---------------------------------------------------------------------------

interface RadioOption<T extends string> {
  label: string;
  value: T;
}

interface SelectOption<T extends string> {
  label: string;
  value: T;
}

const MAP_ENGINE_OPTIONS: RadioOption<MapEngine>[] = [
  { label: '3D Globe', value: '3d' },
  { label: '2D Flat Map', value: '2d' },
];

const RENDER_QUALITY_OPTIONS: SelectOption<RenderQuality>[] = [
  { label: 'Auto', value: 'auto' },
  { label: 'Eco', value: 'eco' },
  { label: 'Sharp', value: 'sharp' },
  { label: '4K', value: '4k' },
];

const TILE_PROVIDER_OPTIONS: SelectOption<TileProvider>[] = [
  { label: 'OpenFreeMap', value: 'openfreemap' },
  { label: 'CARTO', value: 'carto' },
];

const MAP_THEME_OPTIONS: RadioOption<MapTheme>[] = [
  { label: 'Dark', value: 'dark' },
  { label: 'Light', value: 'light' },
];

const AI_PROVIDER_OPTIONS: SelectOption<AIProvider>[] = [
  { label: 'Ollama (local)', value: 'ollama' },
  { label: 'Groq', value: 'groq' },
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'Browser T5', value: 'browser-t5' },
];

const LANGUAGE_OPTIONS: SelectOption<string>[] = [
  { label: 'English', value: 'en' },
  { label: 'French', value: 'fr' },
  { label: 'German', value: 'de' },
  { label: 'Spanish', value: 'es' },
  { label: 'Arabic', value: 'ar' },
  { label: 'Chinese', value: 'zh' },
  { label: 'Russian', value: 'ru' },
  { label: 'Japanese', value: 'ja' },
];

// ---------------------------------------------------------------------------
// Inline styles for terminal-dark themed form controls
// ---------------------------------------------------------------------------

const STYLES = {
  section: [
    'margin-bottom: 14px',
    'padding-bottom: 10px',
    'border-bottom: 1px solid rgba(255,255,255,0.06)',
  ].join(';'),

  sectionLast: 'margin-bottom: 0; padding-bottom: 0; border-bottom: none',

  label: [
    'display: block',
    'font-size: 10px',
    'letter-spacing: 1.2px',
    'text-transform: uppercase',
    'color: var(--accent, #00e5ff)',
    'margin-bottom: 6px',
    'font-family: var(--font-mono, monospace)',
  ].join(';'),

  select: [
    'width: 100%',
    'padding: 5px 8px',
    'background: rgba(0,0,0,0.5)',
    'color: var(--text, #e0e0e0)',
    'border: 1px solid rgba(255,255,255,0.12)',
    'border-radius: 3px',
    'font-size: 11px',
    'font-family: var(--font-mono, monospace)',
    'outline: none',
    'cursor: pointer',
    'appearance: auto',
  ].join(';'),

  input: [
    'width: 100%',
    'padding: 5px 8px',
    'background: rgba(0,0,0,0.5)',
    'color: var(--text, #e0e0e0)',
    'border: 1px solid rgba(255,255,255,0.12)',
    'border-radius: 3px',
    'font-size: 11px',
    'font-family: var(--font-mono, monospace)',
    'outline: none',
    'box-sizing: border-box',
  ].join(';'),

  radioGroup: [
    'display: flex',
    'gap: 12px',
  ].join(';'),

  radioLabel: [
    'display: flex',
    'align-items: center',
    'gap: 5px',
    'font-size: 11px',
    'color: var(--text, #e0e0e0)',
    'cursor: pointer',
    'font-family: var(--font-mono, monospace)',
  ].join(';'),

  checkboxRow: [
    'display: flex',
    'align-items: center',
    'gap: 8px',
    'margin-bottom: 8px',
  ].join(';'),

  checkboxLabel: [
    'font-size: 11px',
    'color: var(--text, #e0e0e0)',
    'cursor: pointer',
    'font-family: var(--font-mono, monospace)',
    'user-select: none',
  ].join(';'),

  scrollBody: [
    'overflow-y: auto',
    'max-height: 420px',
    'padding: 10px',
  ].join(';'),
} as const;

// ---------------------------------------------------------------------------
// SettingsPanel
// ---------------------------------------------------------------------------

export class SettingsPanel extends Panel {
  private app: { getSettings(): AppSettings; updateSettings(p: Partial<AppSettings>): void } | null = null;

  constructor() {
    super({
      id: 'settings',
      title: 'SETTINGS',
      icon: '⚙',
      description: 'Application settings and configuration',
      defaultOpen: false,
    });
  }

  // ── App reference resolution ───────────────────────────────────────────────

  private getApp(): { getSettings(): AppSettings; updateSettings(p: Partial<AppSettings>): void } | null {
    if (this.app) return this.app;
    const win = window as unknown as Record<string, unknown>;
    const atlas = win['__atlas'] as Record<string, unknown> | undefined;
    if (atlas?.app) {
      const ref = atlas.app as { getSettings(): AppSettings; updateSettings(p: Partial<AppSettings>): void };
      this.app = ref;
      return ref;
    }
    return null;
  }

  private settings(): AppSettings {
    const app = this.getApp();
    if (app) return app.getSettings();
    // Fallback: read from localStorage directly
    try {
      const saved = localStorage.getItem('atlas-settings');
      if (saved) return JSON.parse(saved) as AppSettings;
    } catch { /* ignore */ }
    return {
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
  }

  private update(partial: Partial<AppSettings>): void {
    const app = this.getApp();
    if (app) {
      app.updateSettings(partial);
    } else {
      // Fallback: write to localStorage + dispatch event
      const current = this.settings();
      Object.assign(current, partial);
      localStorage.setItem('atlas-settings', JSON.stringify(current));
      window.dispatchEvent(new CustomEvent('atlas:settings-changed', { detail: current }));
    }
  }

  /** Allow external code to inject the app reference directly. */
  setApp(app: { getSettings(): AppSettings; updateSettings(p: Partial<AppSettings>): void }): void {
    this.app = app;
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  protected onOpen(): void {
    this.render();
  }

  protected override render(): void {
    const s = this.settings();
    const sections: HTMLElement[] = [];

    // 1. Map Engine — radios
    sections.push(this.buildRadioSection('MAP ENGINE', 'mapEngine', MAP_ENGINE_OPTIONS, s.mapEngine));

    // 2. Render Quality — select
    sections.push(this.buildSelectSection('RENDER QUALITY', 'renderQuality', RENDER_QUALITY_OPTIONS, s.renderQuality));

    // 3. Tile Provider — select
    sections.push(this.buildSelectSection('TILE PROVIDER', 'tileProvider', TILE_PROVIDER_OPTIONS, s.tileProvider));

    // 4. Map Theme — radios
    sections.push(this.buildRadioSection('MAP THEME', 'mapTheme', MAP_THEME_OPTIONS, s.mapTheme));

    // 5. AI Provider — select
    sections.push(this.buildSelectSection('AI PROVIDER', 'aiProvider', AI_PROVIDER_OPTIONS, s.aiProvider));

    // 6. Ollama Endpoint — text input
    sections.push(this.buildTextSection('OLLAMA ENDPOINT', 'ollamaEndpoint', s.ollamaEndpoint, 'http://localhost:11434'));

    // 7. Language — select
    sections.push(this.buildSelectSection('LANGUAGE', 'language', LANGUAGE_OPTIONS, s.language));

    // 8-10. Checkboxes
    sections.push(this.buildCheckboxGroup([
      { key: 'enableML', label: 'Enable ML', checked: s.enableML },
      { key: 'enableHeadlineMemory', label: 'Enable Headline Memory', checked: s.enableHeadlineMemory },
      { key: 'enableScanlines', label: 'Enable Scanlines', checked: s.enableScanlines },
    ]));

    // Remove bottom border from last section
    const last = sections[sections.length - 1];
    last.style.cssText += ';' + STYLES.sectionLast;

    const wrapper = h('div', { style: STYLES.scrollBody }, ...sections);
    replaceChildren(this.body, wrapper);
    this.setFooter('Settings auto-saved');
  }

  // ── Section builders ───────────────────────────────────────────────────────

  private buildRadioSection<T extends string>(
    title: string,
    key: keyof AppSettings,
    options: RadioOption<T>[],
    current: string,
  ): HTMLElement {
    const groupName = `settings-${key}`;

    const radios = options.map((opt) => {
      const radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = groupName;
      radio.value = opt.value;
      radio.checked = opt.value === current;
      radio.style.cssText = 'accent-color: var(--accent, #00e5ff); cursor: pointer';

      radio.addEventListener('change', () => {
        if (radio.checked) {
          this.update({ [key]: opt.value } as Partial<AppSettings>);
        }
      });

      const label = h('label', { style: STYLES.radioLabel }, radio, opt.label);
      return label;
    });

    const group = h('div', { style: STYLES.radioGroup }, ...radios);

    return h(
      'div',
      { style: STYLES.section },
      h('div', { style: STYLES.label }, title),
      group,
    );
  }

  private buildSelectSection<T extends string>(
    title: string,
    key: keyof AppSettings,
    options: SelectOption<T>[],
    current: string,
  ): HTMLElement {
    const select = document.createElement('select');
    select.style.cssText = STYLES.select;

    for (const opt of options) {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;
      option.selected = opt.value === current;
      select.appendChild(option);
    }

    select.addEventListener('change', () => {
      this.update({ [key]: select.value } as Partial<AppSettings>);
    });

    // Focus style
    select.addEventListener('focus', () => {
      select.style.borderColor = 'var(--accent, #00e5ff)';
    });
    select.addEventListener('blur', () => {
      select.style.borderColor = 'rgba(255,255,255,0.12)';
    });

    return h(
      'div',
      { style: STYLES.section },
      h('div', { style: STYLES.label }, title),
      select,
    );
  }

  private buildTextSection(
    title: string,
    key: keyof AppSettings,
    current: string,
    placeholder: string,
  ): HTMLElement {
    const input = document.createElement('input');
    input.type = 'text';
    input.value = current;
    input.placeholder = placeholder;
    input.style.cssText = STYLES.input;

    // Debounce updates on input
    let timer: ReturnType<typeof setTimeout> | null = null;
    input.addEventListener('input', () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        this.update({ [key]: input.value } as Partial<AppSettings>);
      }, 400);
    });

    // Also update on blur immediately
    input.addEventListener('blur', () => {
      if (timer) clearTimeout(timer);
      this.update({ [key]: input.value } as Partial<AppSettings>);
    });

    // Focus style
    input.addEventListener('focus', () => {
      input.style.borderColor = 'var(--accent, #00e5ff)';
    });
    input.addEventListener('blur', () => {
      input.style.borderColor = 'rgba(255,255,255,0.12)';
    });

    return h(
      'div',
      { style: STYLES.section },
      h('div', { style: STYLES.label }, title),
      input,
    );
  }

  private buildCheckboxGroup(
    items: { key: keyof AppSettings; label: string; checked: boolean }[],
  ): HTMLElement {
    const rows = items.map(({ key, label, checked }) => {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = checked;
      checkbox.style.cssText = 'accent-color: var(--accent, #00e5ff); cursor: pointer';

      checkbox.addEventListener('change', () => {
        this.update({ [key]: checkbox.checked } as Partial<AppSettings>);
      });

      const labelEl = h(
        'label',
        { style: STYLES.checkboxRow },
        checkbox,
        h('span', { style: STYLES.checkboxLabel }, label),
      );
      return labelEl;
    });

    return h(
      'div',
      { style: STYLES.section },
      h('div', { style: STYLES.label }, 'OPTIONS'),
      ...rows,
    );
  }
}
