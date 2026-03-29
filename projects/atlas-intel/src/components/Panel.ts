// ============================================================================
// Atlas Intel — Base Panel Component
// ============================================================================

import { PanelConfig } from '@/types/index';
import { h, uid } from '@/utils/dom-utils';

export class Panel {
  readonly id: string;
  readonly config: PanelConfig;
  protected el: HTMLElement;
  protected header: HTMLElement;
  protected body: HTMLElement;
  protected footer: HTMLElement;
  protected badgeEl: HTMLElement | null = null;
  private _isOpen: boolean;
  private _isDragging = false;
  private _dragOffset = { x: 0, y: 0 };

  constructor(config: PanelConfig) {
    this.id = config.id;
    this.config = config;
    this._isOpen = config.defaultOpen;
    this.el = this.createElement();
    this.header = this.el.querySelector('.panel-header')!;
    this.body = this.el.querySelector('.panel-body')!;
    this.footer = this.el.querySelector('.panel-footer')!;
    this.badgeEl = this.el.querySelector('.panel-header .badge');
    this.setupDrag();

    if (!this._isOpen) this.el.classList.add('closed');

    // Apply initial position if provided
    if (config.position) {
      this.setPosition(config.position.x, config.position.y);
    }
  }

  // --------------------------------------------------------------------------
  // DOM Construction
  // --------------------------------------------------------------------------

  private createElement(): HTMLElement {
    const panelId = `panel-${this.id}-${uid()}`;

    // Badge element (hidden by default)
    const badge = h('span', { class: 'badge', style: 'display:none' });

    // Title section: icon + title text + badge
    const titleSection = h(
      'div',
      { class: 'title' },
      h('span', { class: 'icon' }, this.config.icon),
      h('span', null, this.config.title),
      badge,
    );

    // Control buttons: minimize and close
    const minimizeBtn = h(
      'button',
      {
        class: 'minimize-btn',
        title: 'Minimize',
        onClick: (e: Event) => {
          e.stopPropagation();
          this.close();
        },
      },
      '−',
    );

    const closeBtn = h(
      'button',
      {
        class: 'close-btn',
        title: 'Close',
        onClick: (e: Event) => {
          e.stopPropagation();
          this.close();
        },
      },
      '✕',
    );

    const controls = h('div', { class: 'controls' }, minimizeBtn, closeBtn);

    // Header: title section + controls
    const header = h('div', { class: 'panel-header' }, titleSection, controls);

    // Body
    const body = h('div', { class: 'panel-body' });

    // Footer
    const footer = h('div', { class: 'panel-footer' }, 'Awaiting data…');

    // Assemble panel
    const panel = h(
      'div',
      {
        class: 'panel',
        id: panelId,
        'data-panel-id': this.id,
      },
      header,
      body,
      footer,
    );

    return panel;
  }

  // --------------------------------------------------------------------------
  // Drag handling
  // --------------------------------------------------------------------------

  private setupDrag(): void {
    const header = this.el.querySelector('.panel-header')!;

    // --- Mouse events ---
    const onMouseDown = (e: Event) => {
      const me = e as MouseEvent;
      // Ignore clicks on buttons inside header controls
      if ((me.target as HTMLElement).closest('.controls')) return;

      this._isDragging = true;
      const rect = this.el.getBoundingClientRect();
      this._dragOffset.x = me.clientX - rect.left;
      this._dragOffset.y = me.clientY - rect.top;

      // Bring panel to front
      this.el.style.zIndex = String(100 + Date.now() % 1000);

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e: Event) => {
      if (!this._isDragging) return;
      const me = e as MouseEvent;
      me.preventDefault();

      const x = me.clientX - this._dragOffset.x;
      const y = me.clientY - this._dragOffset.y;
      this.setPosition(
        Math.max(0, Math.min(x, window.innerWidth - 50)),
        Math.max(0, Math.min(y, window.innerHeight - 50)),
      );
    };

    const onMouseUp = () => {
      this._isDragging = false;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    header.addEventListener('mousedown', onMouseDown);

    // --- Touch events for mobile ---
    const onTouchStart = (e: Event) => {
      const te = e as TouchEvent;
      if ((te.target as HTMLElement).closest('.controls')) return;
      if (te.touches.length !== 1) return;

      this._isDragging = true;
      const touch = te.touches[0];
      const rect = this.el.getBoundingClientRect();
      this._dragOffset.x = touch.clientX - rect.left;
      this._dragOffset.y = touch.clientY - rect.top;

      this.el.style.zIndex = String(100 + Date.now() % 1000);

      document.addEventListener('touchmove', onTouchMove, { passive: false });
      document.addEventListener('touchend', onTouchEnd);
    };

    const onTouchMove = (e: Event) => {
      if (!this._isDragging) return;
      const te = e as TouchEvent;
      te.preventDefault();
      const touch = te.touches[0];

      const x = touch.clientX - this._dragOffset.x;
      const y = touch.clientY - this._dragOffset.y;
      this.setPosition(
        Math.max(0, Math.min(x, window.innerWidth - 50)),
        Math.max(0, Math.min(y, window.innerHeight - 50)),
      );
    };

    const onTouchEnd = () => {
      this._isDragging = false;
      document.removeEventListener('touchmove', onTouchMove);
      document.removeEventListener('touchend', onTouchEnd);
    };

    header.addEventListener('touchstart', onTouchStart, { passive: true });
  }

  // --------------------------------------------------------------------------
  // Open / Close / Toggle
  // --------------------------------------------------------------------------

  open(): void {
    this._isOpen = true;
    this.el.classList.remove('closed');
    this.onOpen();
  }

  close(): void {
    this._isOpen = false;
    this.el.classList.add('closed');
    this.onClose();
  }

  toggle(): void {
    if (this._isOpen) { this.close(); } else { this.open(); }
  }

  get isOpen(): boolean {
    return this._isOpen;
  }

  get element(): HTMLElement {
    return this.el;
  }

  // --------------------------------------------------------------------------
  // Badge
  // --------------------------------------------------------------------------

  /** Set badge count. Hides badge when count is 0. */
  setBadge(count: number): void {
    if (!this.badgeEl) return;
    this.badgeEl.textContent = count > 0 ? String(count) : '';
    this.badgeEl.style.display = count > 0 ? 'inline-flex' : 'none';
  }

  // --------------------------------------------------------------------------
  // Position
  // --------------------------------------------------------------------------

  /** Set absolute position of the panel. */
  setPosition(x: number, y: number): void {
    this.el.style.left = `${x}px`;
    this.el.style.top = `${y}px`;
  }

  // --------------------------------------------------------------------------
  // Footer
  // --------------------------------------------------------------------------

  /** Set footer text (e.g. last updated timestamp). */
  setFooter(text: string): void {
    this.footer.textContent = text;
  }

  // --------------------------------------------------------------------------
  // Lifecycle hooks — override in subclass
  // --------------------------------------------------------------------------

  /** Override in subclass to render content into the body. */
  protected render(): void {}

  /** Called when panel opens. */
  protected onOpen(): void {}

  /** Called when panel closes. */
  protected onClose(): void {}

  /** Refresh data — override in subclass. */
  async refresh(): Promise<void> {}

  // --------------------------------------------------------------------------
  // Mount / Destroy
  // --------------------------------------------------------------------------

  /** Destroy the panel and remove it from the DOM. */
  destroy(): void {
    this.el.remove();
  }

  /** Mount the panel into a parent element. */
  mount(parent: HTMLElement): void {
    parent.appendChild(this.el);
  }
}
