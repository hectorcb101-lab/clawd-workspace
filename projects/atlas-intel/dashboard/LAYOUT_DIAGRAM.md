# Atlas Intel Dashboard - Responsive Layout Diagram

## Desktop Layout (> 1024px)

```
┌──────────────────────────────────────────────────────────────────────┐
│  TOP BAR                                                             │
│  ⬢ ATLAS INTEL  [UNCLASSIFIED // FOUO]  |  12:34:56 UTC  [ONLINE]  │
└──────────────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────┬────────────────┐
│          │                                          │                │
│  LEFT    │                                          │     RIGHT      │
│  PANEL   │             GLOBE                        │     PANEL      │
│  280px   │           (center)                       │     320px      │
│          │                                          │                │
│  Feed    │                                          │   Alerts       │
│  Cards   │                                          │   Feed         │
│          │                                          │                │
│  Layers  │                                          │                │
│          │                                          │                │
└──────────┴──────────────────────────────────────────┴────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│  BOTTOM BAR                                                          │
│  [LONDON] [NEW YORK] [DUBAI] ... | NORMAL [CRT] [NVG] [THERMAL]    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Tablet Layout (768px - 1024px)

```
┌──────────────────────────────────────────────────────────────────────┐
│  TOP BAR                                                             │
│  ⬢ ATLAS INTEL  [UNCLASSIFIED]  |  12:34:56 UTC  [ONLINE]          │
└──────────────────────────────────────────────────────────────────────┘
┌──────────┬────────────────────────────────────────────────────────┐
│          │                                                        │
│  LEFT    │                                                        │
│  PANEL   │               GLOBE                                   │
│  240px   │             (expanded)                                │
│          │                                                        │
│  Feed    │                                                        │
│  Cards   │                                                        │
│          │                                                        │
│  Layers  │                                                        │
│          │                                                        │
└──────────┴────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│  BOTTOM BAR (wrapped)                                                │
│  [LONDON] [NEW YORK] [DUBAI] [SINGAPORE] [TOKYO] [WASHINGTON DC]    │
│  VIEW MODE: [NORMAL] [CRT] [NVG] [THERMAL]                          │
└──────────────────────────────────────────────────────────────────────┘
```

**Note:** Right alerts panel hidden on tablet

---

## Mobile Layout (< 768px) - PORTRAIT

```
┌────────────────────────────────────┐
│  TOP BAR                           │
│  ⬢ ATLAS INTEL | 12:34:56 UTC     │
│  (classification hidden)           │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│                                    │
│                                    │
│            GLOBE                   │
│         (full width)               │
│           50vh                     │
│                                    │
│                                    │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  FEED CARDS (stacked)              │
│  ┌──────────────────────────────┐ │
│  │ 🚢 VESSEL TRACKER            │ │
│  │ Status: ONLINE               │ │
│  │ Tracked: 156                 │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ ✈️  FLIGHT MONITOR           │ │
│  │ Status: ONLINE               │ │
│  │ Tracked: 89                  │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 🔥 THERMAL/FIRMS             │ │
│  │ ...                          │ │
│  └──────────────────────────────┘ │
│  ...                               │
│                                    │
│  LAYERS                            │
│  ☑ Vessels                         │
│  ☑ Flights                         │
│  ☑ Thermal                         │
│  ...                               │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  ALERTS (scrollable)               │
│  ┌──────────────────────────────┐ │
│  │ [INFO] 12:34                 │ │
│  │ New vessel detected...       │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ [WARNING] 12:30              │ │
│  │ Thermal anomaly...           │ │
│  └──────────────────────────────┘ │
│  ...                               │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│  BOTTOM BAR (sticky)               │
│  ◀ [LDN] [NYC] [DXB] [SIN] ... ▶  │
│  (horizontal scroll)               │
│                                    │
│  VIEW MODE:                        │
│  [NORMAL] [CRT]                    │
│  [NVG] [THERMAL]                   │
│  (wrapped)                         │
└────────────────────────────────────┘
```

---

## Mobile Layout (< 768px) - LANDSCAPE

```
┌────────────────────────────────────────────────────────────────┐
│  TOP BAR  |  ⬢ ATLAS INTEL  |  12:34:56 UTC                   │
└────────────────────────────────────────────────────────────────┘
┌─────────────────────────────┬──────────────────────────────────┐
│                             │  FEED CARDS (scrollable)         │
│                             │  ┌────────────────────────────┐  │
│          GLOBE              │  │ 🚢 VESSEL TRACKER          │  │
│       (left side)           │  │ Status: ONLINE             │  │
│         ~50vh               │  └────────────────────────────┘  │
│                             │  ┌────────────────────────────┐  │
│                             │  │ ✈️  FLIGHT MONITOR         │  │
│                             │  └────────────────────────────┘  │
│                             │  ...                             │
│                             │                                  │
│                             │  ALERTS                          │
│                             │  ┌────────────────────────────┐  │
│                             │  │ [INFO] New vessel...       │  │
│                             │  └────────────────────────────┘  │
└─────────────────────────────┴──────────────────────────────────┘
┌────────────────────────────────────────────────────────────────┐
│  ◀ [LONDON] [NYC] [DUBAI] ... ▶  |  [NORMAL] [CRT] [NVG] ... │
└────────────────────────────────────────────────────────────────┘
```

---

## Very Small Mobile (< 400px)

```
┌────────────────────┐
│  ⬢ ATLAS INTEL     │
│  12:34:56 UTC      │
└────────────────────┘
┌────────────────────┐
│                    │
│      GLOBE         │
│      40vh          │
│                    │
└────────────────────┘
┌────────────────────┐
│  FEED CARDS        │
│  (compact)         │
│  ...               │
└────────────────────┘
┌────────────────────┐
│  ALERTS            │
│  (compact)         │
│  ...               │
└────────────────────┘
┌────────────────────┐
│  ◀ [LDN] [NYC] ▶   │
│  [NRM] [CRT]       │
│  [NVG] [THL]       │
└────────────────────┘
```

---

## Login Page Responsive

### Desktop (> 480px)
```
┌─────────────────────────────────────────┐
│                                         │
│         ┌─────────────────┐             │
│         │                 │             │
│         │  ⬢ ATLAS INTEL  │             │
│         │                 │             │
│         │ [Username]      │             │
│         │ [Password]      │             │
│         │                 │             │
│         │ [AUTHENTICATE]  │             │
│         │                 │             │
│         └─────────────────┘             │
│           420px max-width               │
│                                         │
└─────────────────────────────────────────┘
```

### Mobile (< 480px)
```
┌───────────────────────┐
│                       │
│ ┌───────────────────┐ │
│ │                   │ │
│ │ ⬢ ATLAS INTEL     │ │
│ │                   │ │
│ │ [Username]        │ │
│ │ [Password]        │ │
│ │                   │ │
│ │ [AUTHENTICATE]    │ │
│ │                   │ │
│ └───────────────────┘ │
│   95% width           │
│   Reduced padding     │
│                       │
└───────────────────────┘
```

---

## Touch Targets (Mobile)

All interactive elements meet WCAG 2.1 AA standards:

```
Minimum tap target: 44px × 44px

Examples:
┌────────────────┐
│   LONDON       │  44px height
└────────────────┘  (city button)

┌──┐
│  │  20×20px (checkbox, but 44px tap area)
└──┘

┌────┐
│  ✕ │  44×44px (popup close)
└────┘
```

---

## Scrolling Behavior

### Horizontal Scroll (City Buttons)
```
┌───────────────────────────────────────┐
│ ◀ [LDN] [NYC] [DXB] [SIN] [TYO] [WDC] ▶ │
│ ═════════════════════════════════════ │
│ ▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← scroll indicator
└───────────────────────────────────────┘
  Swipe left/right to scroll
  Gradient fade on right edge
```

### Vertical Scroll (Alerts)
```
┌────────────────┐
│ Alert 1        │ ↑
│ Alert 2        │ │
│ Alert 3        │ │ Swipe up/down
│ Alert 4        │ │
│ Alert 5        │ ↓
└────────────────┘
  Momentum scrolling
  -webkit-overflow-scrolling: touch
```

---

## Breakpoint Summary

| Breakpoint | Layout | Grid Columns | Globe Size |
|------------|--------|--------------|------------|
| > 1024px   | Desktop | `280px 1fr 320px` | Flexible |
| 768-1024px | Tablet  | `240px 1fr` | Expanded |
| 400-767px  | Mobile  | Single column | 50vh |
| < 400px    | Small   | Single column | 40vh |

---

## Media Query Structure

```css
/* Desktop (default) */
.main-container {
    grid-template-columns: 280px 1fr 320px;
}

/* Tablet (768-1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
    .main-container {
        grid-template-columns: 240px 1fr;
    }
    .right-panel { display: none; }
}

/* Mobile (< 768px) */
@media (max-width: 767px) {
    .main-container {
        display: flex;
        flex-direction: column;
    }
    .center-panel { height: 50vh; }
}

/* Very small (< 400px) */
@media (max-width: 399px) {
    .center-panel { height: 40vh; }
}
```

---

## Color & Typography Consistency

**All layouts maintain:**
- Colors: Cyan (#00ffcc), Amber (#ffd700), Red (#ff3333)
- Font: JetBrains Mono
- Effects: CRT scanlines, glows, pulse animations
- View modes: Normal, CRT, NVG, Thermal

No visual compromises for mobile.

---

**Legend:**
- `┌─┐ └─┘` = Container borders
- `│` = Vertical division
- `◀ ▶` = Scrollable area indicators
- `☑` = Checkbox
- `...` = Additional content
