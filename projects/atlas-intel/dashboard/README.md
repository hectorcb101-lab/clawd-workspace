# ATLAS INTEL Dashboard

## Tactical Intelligence Dashboard

A military-grade intelligence visualization interface inspired by SIGINT operations centres.

### Features

- **3D Interactive Globe** - Real-time visualization of global intelligence data
- **Multi-Source Data Feeds** - Vessels, flights, thermal imagery, GDELT events, economic indicators
- **Live Alert System** - Convergence detection and real-time notifications
- **Military Aesthetic** - CRT scanlines, cyan/amber/red color scheme, tactical UI
- **View Modes** - Normal, CRT, Night Vision (NVG), Thermal imaging
- **Strategic Chokepoints** - Automatic highlighting of critical maritime passages
- **Keyboard Shortcuts** - Full keyboard control for rapid navigation

### Quick Start

#### Option 1: Direct File Open
```bash
# Simply open in browser
open index.html
# or
firefox index.html
```

#### Option 2: Local Server (Recommended)
```bash
cd /home/ubuntu/clawd/projects/atlas-intel/dashboard
python3 -m http.server 8080
# Then visit: http://localhost:8080
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F` | Toggle fullscreen |
| `R` | Reset globe view |
| `1` | Toggle vessel layer |
| `2` | Toggle flight layer |
| `3` | Toggle thermal layer |
| `4` | Toggle GDELT layer |
| `5` | Toggle chokepoints layer |

### UI Controls

**Top Bar:**
- Live UTC clock
- System status indicators
- Classification badge

**Left Panel:**
- Data feed status cards
- Layer visibility toggles
- Real-time statistics

**Centre:**
- Interactive 3D globe
- Click any marker for details
- Auto-rotates when idle
- Mouse drag to navigate

**Right Panel:**
- Live alert feed
- Severity-coded messages
- Auto-scroll (pauses on hover)

**Bottom Bar:**
- Quick-jump city buttons
- View mode toggles (Normal/CRT/NVG/Thermal)

### Data Files

Dashboard loads from JSON files in `data/`:

- `vessel_status.json` - Maritime vessel tracking
- `flight_status.json` - Aviation monitoring
- `thermal_status.json` - Thermal/FIRMS hotspots
- `gdelt_status.json` - Global events database
- `alerts.json` - Live alert feed

Auto-refreshes every 30 seconds.

### Color Scheme

- **Cyan (#00ffcc)** - Primary accent, online status, vessel markers
- **Amber (#ffd700)** - Warnings, flight paths, chokepoints
- **Red (#ff3333)** - Critical alerts, thermal hotspots
- **Dark Background (#0a0a0f)** - Military-grade dark theme

### Technologies

- **Globe.gl** - 3D globe visualization
- **Three.js** - WebGL rendering
- **Vanilla JS** - No build step required
- **CSS3** - CRT effects, scanlines, glows
- **JetBrains Mono** - Tactical monospace font

### Architecture

Single-page application with:
- No dependencies beyond CDN libraries
- Works offline (once libraries cached)
- Fully responsive design
- Smooth 60fps animations
- Optimized for desktop displays

### Customization

Edit data files in `data/` directory to update:
- Vessel positions and details
- Flight paths and metadata
- Thermal signatures
- GDELT events
- Alert messages

Python daemons can write directly to these JSON files for live updates.

### Future Enhancements

- WebSocket live data streaming
- Historical playback mode
- Export alert reports
- Multi-user collaboration
- Classified data overlay mode
- Satellite imagery integration

---

**ATLAS INTEL** - Tactical Intelligence at your fingertips.
