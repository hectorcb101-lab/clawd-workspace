# Atlas Intel Dashboard - Globe Centering Fix

## Changes Made

### 1. app.js - Globe Initialization
**Problem**: Globe was initialized without explicit dimensions, defaulting to window width
**Fix**: Added `.width()` and `.height()` calls with container dimensions

```javascript
// Get container dimensions
const width = container.clientWidth;
const height = container.clientHeight;

state.globe = Globe()
    (container)
    .width(width)      // ← NEW: Set explicit width
    .height(height)    // ← NEW: Set explicit height
    // ... rest of config
```

### 2. styles.css - Centre Panel Layout
**Problem**: Globe canvas may not be properly centred within the flex container
**Fix**: Added flexbox centering and canvas-specific styling

```css
.center-panel {
    position: relative;
    background: var(--bg-primary);
    overflow: hidden;
    display: flex;              /* ← NEW: Enable flexbox */
    justify-content: center;    /* ← NEW: Centre horizontally */
    align-items: center;        /* ← NEW: Centre vertically */
}

#globeContainer {
    width: 100%;
    height: 100%;
    position: relative;         /* ← NEW: Positioning context */
}

#globeContainer canvas {        /* ← NEW: Canvas-specific styling */
    display: block;
    margin: 0 auto;
}
```

## How It Works

1. **Grid Layout**: The main container uses CSS Grid with 3 columns:
   - Left sidebar: 280px fixed
   - Centre panel: 1fr (flexible, takes remaining space)
   - Right sidebar: 320px fixed

2. **Globe Sizing**: The globe now explicitly uses the centre panel's dimensions rather than window dimensions

3. **Responsive**: The existing resize handler continues to update globe dimensions on window resize

## Testing

All existing features preserved:
✓ 3D globe with textures
✓ Vessel markers (cyan dots)
✓ Flight arcs (amber lines)
✓ Thermal hotspots (red rings)
✓ GDELT events (white markers)
✓ Chokepoint regions (amber polygons)
✓ Layer toggles (bottom left)
✓ City quick-jump buttons
✓ View mode toggles (CRT/NVG/Thermal)
✓ Auto-rotation
✓ Click handlers and popups
✓ Keyboard shortcuts
✓ Coordinate display
✓ Military aesthetic maintained

## Result

The globe is now **centred in the viewport** between the left sidebar and right alerts panel, rendering at the correct size for the available space.
