// ============================================================================
// Atlas Intel — 3D Globe Component (globe.gl + Three.js)
// ============================================================================

import Globe from 'globe.gl';
import type { GlobeInstance } from 'globe.gl';
import * as THREE from 'three';
import type { MapMarker, Coordinates, RenderQuality } from '@/types/index';
import { debounce } from '@/utils/dom-utils';

// ---------------------------------------------------------------------------
// GlobeMap — wraps globe.gl with markers, atmosphere, rotation, quality
// ---------------------------------------------------------------------------

export class GlobeMap {
  private container: HTMLElement;
  private globe: GlobeInstance | null = null;
  private markers: MapMarker[] = [];
  private autoRotateTimer: ReturnType<typeof setTimeout> | null = null;
  private isInteracting = false;
  private quality: RenderQuality = 'auto';
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private pendingMarkers: MapMarker[] | null = null;
  private visibilityHandler: (() => void) | null = null;
  private resizeHandler: (() => void) | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  /** Initialize the globe and attach it to the container */
  async init(quality?: RenderQuality): Promise<void> {
    if (quality) this.quality = quality;

    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    // globe.gl uses Kapsule — typed as `new Globe(el, config)` but the
    // fluent API lets us chain configuration before/after mounting.
    const instance = new Globe(this.container, { animateIn: true });

    this.globe = instance
      .globeImageUrl('/textures/earth-topo.jpg')
      .bumpImageUrl('/textures/earth-water.png')
      .backgroundImageUrl('/textures/night-sky.png')
      .width(width)
      .height(height)
      .showAtmosphere(true)
      .atmosphereColor('#4466cc')
      .atmosphereAltitude(0.25)
      // HTML marker layer
      .htmlElementsData([])
      .htmlElement((d: object) => this.createMarkerElement(d as MapMarker))
      .htmlLat((d: object) => (d as MapMarker).lat)
      .htmlLng((d: object) => (d as MapMarker).lng)
      .htmlAltitude(0.01);

    // Post-mount setup
    this.setupAtmosphere();
    this.setupAutoRotation();
    this.setupInteractionHandlers();
    this.setupResizeHandler();
    this.setupVisibilityHandler();
    this.applyQuality();
  }

  // -------------------------------------------------------------------------
  // Atmosphere — Fresnel limb-glow shader
  // -------------------------------------------------------------------------

  private setupAtmosphere(): void {
    if (!this.globe) return;

    const scene = this.globe.scene();

    // Custom Fresnel atmosphere mesh for limb glow
    const atmosphereGeometry = new THREE.SphereGeometry(101, 64, 64);
    const atmosphereMaterial = new THREE.ShaderMaterial({
      vertexShader: `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 vNormal;
        void main() {
          float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
          // #4466cc → rgb(0.267, 0.4, 0.8)
          gl_FragColor = vec4(0.267, 0.4, 0.8, 1.0) * intensity;
        }
      `,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
    });

    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);
  }

  // -------------------------------------------------------------------------
  // Auto-rotation
  // -------------------------------------------------------------------------

  private setupAutoRotation(): void {
    if (!this.globe) return;

    const controls = this.globe.controls();
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.3;
  }

  // -------------------------------------------------------------------------
  // Interaction — pause rotation while user interacts, resume after 60s
  // -------------------------------------------------------------------------

  private setupInteractionHandlers(): void {
    if (!this.globe) return;

    const controls = this.globe.controls();

    controls.addEventListener('start', () => {
      this.isInteracting = true;
      controls.autoRotate = false;

      if (this.autoRotateTimer) {
        clearTimeout(this.autoRotateTimer);
        this.autoRotateTimer = null;
      }
    });

    controls.addEventListener('end', () => {
      this.isInteracting = false;

      // Resume auto-rotation after 60 s of inactivity
      this.autoRotateTimer = setTimeout(() => {
        if (!this.isInteracting) {
          controls.autoRotate = true;
        }
        this.autoRotateTimer = null;
      }, 60_000);
    });
  }

  // -------------------------------------------------------------------------
  // Resize
  // -------------------------------------------------------------------------

  private setupResizeHandler(): void {
    this.resizeHandler = debounce(() => {
      if (!this.globe) return;
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      if (w > 0 && h > 0) {
        this.globe.width(w);
        this.globe.height(h);
      }
    }, 200);

    window.addEventListener('resize', this.resizeHandler);
  }

  // -------------------------------------------------------------------------
  // Visibility — pause rendering when tab is hidden
  // -------------------------------------------------------------------------

  private setupVisibilityHandler(): void {
    this.visibilityHandler = () => {
      if (!this.globe) return;

      if (document.hidden) {
        this.globe.pauseAnimation();
      } else {
        this.globe.resumeAnimation();
      }
    };

    document.addEventListener('visibilitychange', this.visibilityHandler);
  }

  // -------------------------------------------------------------------------
  // Quality
  // -------------------------------------------------------------------------

  private applyQuality(): void {
    if (!this.globe) return;

    const renderer = this.globe.renderer();
    const dpr = window.devicePixelRatio || 1;

    switch (this.quality) {
      case 'eco':
        renderer.setPixelRatio(Math.min(dpr, 1));
        break;
      case 'sharp':
        renderer.setPixelRatio(Math.min(dpr, 2));
        break;
      case '4k':
        renderer.setPixelRatio(dpr);
        break;
      default: // 'auto'
        renderer.setPixelRatio(Math.min(dpr, 1.5));
        break;
    }
  }

  // -------------------------------------------------------------------------
  // Markers
  // -------------------------------------------------------------------------

  /** Build the DOM element for a single marker */
  private createMarkerElement(marker: MapMarker): HTMLElement {
    const el = document.createElement('div');
    el.className = `globe-marker ${marker.kind}`;
    el.dataset.id = marker.id;
    el.title = marker.label || marker.kind;

    el.addEventListener('click', () => {
      window.dispatchEvent(
        new CustomEvent('atlas:marker-click', { detail: marker }),
      );
    });

    return el;
  }

  /**
   * Set markers with debounced flush.
   *
   * Callers may invoke this rapidly (e.g. on every WebSocket message);
   * the actual DOM/Three.js update is coalesced into ≤ 1 update per 100 ms.
   */
  setMarkers(markers: MapMarker[]): void {
    this.pendingMarkers = markers;

    if (!this.flushTimer) {
      this.flushTimer = setTimeout(() => {
        this.flushMarkers();
        this.flushTimer = null;
      }, 100);
    }
  }

  private flushMarkers(): void {
    if (!this.globe || !this.pendingMarkers) return;

    this.markers = this.pendingMarkers;
    this.globe.htmlElementsData(this.markers as object[]);
    this.pendingMarkers = null;
  }

  // -------------------------------------------------------------------------
  // Camera / Navigation
  // -------------------------------------------------------------------------

  /** Fly the camera to coordinates over `duration` ms (default 1 500) */
  flyTo(coords: Coordinates, duration?: number): void {
    if (!this.globe) return;

    this.globe.pointOfView(
      { lat: coords.lat, lng: coords.lng, altitude: coords.alt ?? 2.0 },
      duration ?? 1500,
    );
  }

  /** Get the current camera point-of-view as Coordinates */
  getPointOfView(): Coordinates {
    if (!this.globe) return { lat: 0, lng: 0, alt: 2 };

    const pov = this.globe.pointOfView();
    return { lat: pov.lat, lng: pov.lng, alt: pov.altitude };
  }

  // -------------------------------------------------------------------------
  // Public controls
  // -------------------------------------------------------------------------

  /** Update the rendering quality preset */
  setQuality(quality: RenderQuality): void {
    this.quality = quality;
    this.applyQuality();
  }

  /** Pause auto-rotation */
  pauseRotation(): void {
    if (!this.globe) return;
    this.globe.controls().autoRotate = false;
  }

  /** Resume auto-rotation */
  resumeRotation(): void {
    if (!this.globe) return;
    this.globe.controls().autoRotate = true;
  }

  /** Access the underlying GlobeInstance (escape hatch for advanced usage) */
  getGlobeInstance(): GlobeInstance | null {
    return this.globe;
  }

  // -------------------------------------------------------------------------
  // Cleanup
  // -------------------------------------------------------------------------

  /** Tear down everything: timers, listeners, Three.js resources */
  destroy(): void {
    // Clear pending timers
    if (this.autoRotateTimer) {
      clearTimeout(this.autoRotateTimer);
      this.autoRotateTimer = null;
    }

    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }

    // Remove global listeners
    if (this.visibilityHandler) {
      document.removeEventListener('visibilitychange', this.visibilityHandler);
      this.visibilityHandler = null;
    }

    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
      this.resizeHandler = null;
    }

    // Destroy globe.gl internals (disposes Three.js objects)
    if (this.globe) {
      this.globe._destructor();
      this.globe = null;
    }

    // Clear container DOM
    this.container.innerHTML = '';
  }
}
