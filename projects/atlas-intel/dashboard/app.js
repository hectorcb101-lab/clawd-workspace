// ===== GLOBAL STATE =====
const state = {
    globe: null,
    data: {
        vessels: [],
        flights: [],
        thermal: [],
        gdelt: [],
        alerts: [],
        satellites: [],
        military: [],
        markets: null,
        radiation: [],
        earthquakes: [],
        gpsJamming: [],
        webcams: [],
        news: [],
        newsHeadlines: [],
        newsAll: [],
        cables: [],
        wildfires: [],
        cyber: [],
        unrest: [],
        infrastructure: [],
        militaryBases: [],
        pipelines: [],
        tradeRoutes: [],
        nuclearSites: []
    },
    layers: {
        vessels: true,
        flights: true,
        aircraft: true,
        thermal: true,
        gdelt: true,
        chokepoints: true,
        satellites: true,
        military: true,
        markets: true,
        radiation: true,
        earthquakes: true,
        gps: true,
        webcams: true,
        cables: true,
        wildfires: true,
        cyber: true,
        unrest: true,
        infrastructure: true,
        bases: true,
        pipelines: true,
        traderoutes: true,
        nuclear: true
    },
    autoRotate: true,
    refreshInterval: null
};

// ===== CITY COORDINATES =====
const cities = {
    london: { lat: 51.5074, lng: -0.1278, alt: 1.5 },
    newyork: { lat: 40.7128, lng: -74.0060, alt: 1.5 },
    dubai: { lat: 25.2048, lng: 55.2708, alt: 1.5 },
    singapore: { lat: 1.3521, lng: 103.8198, alt: 1.5 },
    tokyo: { lat: 35.6762, lng: 139.6503, alt: 1.5 },
    washington: { lat: 38.9072, lng: -77.0369, alt: 1.5 },
    ukraine: { lat: 48.3794, lng: 31.1656, alt: 1.2 },
    taiwan: { lat: 23.6978, lng: 120.9605, alt: 1.2 },
    hormuz: { lat: 26.5, lng: 56.5, alt: 1.0 },
    southchinasea: { lat: 12.0, lng: 114.0, alt: 1.5 }
};

// ===== CHOKEPOINT REGIONS =====
const chokepoints = [
    { name: 'Strait of Hormuz', lat: 26.5, lng: 56.5, radius: 1.5 },
    { name: 'Suez Canal', lat: 30.5, lng: 32.5, radius: 2 },
    { name: 'Strait of Malacca', lat: 2.5, lng: 100.0, radius: 2 },
    { name: 'Panama Canal', lat: 9.0, lng: -79.5, radius: 1 },
    { name: 'Bab-el-Mandeb', lat: 13.5, lng: 43.5, radius: 1.5 },
    { name: 'Danish Straits', lat: 56.0, lng: 12.0, radius: 2 },
    { name: 'Turkish Straits', lat: 41.0, lng: 29.0, radius: 1.5 }
];

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initViewportHeight();
    initClock();
    initGlobe();
    initEventListeners();
    initKeyboardShortcuts();
    loadAllData();
    startAutoRefresh();
});

// ===== VIEWPORT HEIGHT (for mobile browsers) =====
function initViewportHeight() {
    const setVH = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    };
    
    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100);
    });
}

// ===== UTC CLOCK =====
function initClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    const seconds = String(now.getUTCSeconds()).padStart(2, '0');
    document.getElementById('utcClock').textContent = `${hours}:${minutes}:${seconds} UTC`;
}

// ===== GLOBE INITIALIZATION =====
function initGlobe() {
    const container = document.getElementById('globeContainer');
    
    // Get container dimensions
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    state.globe = Globe()
        (container)
        .width(width)
        .height(height)
        .globeImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/earth-night.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/night-sky.png')
        .pointOfView({ lat: 20, lng: 40, altitude: 2.2 })
        .showAtmosphere(true)
        .atmosphereColor('#004433')
        .atmosphereAltitude(0.12)
        .onGlobeClick(handleGlobeClick);

    // Auto-rotate
    startAutoRotate();
    
    // Update coordinates on move
    state.globe.controls().addEventListener('change', updateCoordinates);
    
    // Responsive resize with debounce
    let resizeTimeout;
    const handleResize = () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const newWidth = container.clientWidth;
            const newHeight = container.clientHeight;
            if (newWidth > 0 && newHeight > 0) {
                state.globe.width(newWidth);
                state.globe.height(newHeight);
            }
        }, 250);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Handle orientation change on mobile
    window.addEventListener('orientationchange', () => {
        setTimeout(handleResize, 100);
    });
}

function startAutoRotate() {
    if (state.autoRotate) {
        state.globe.controls().autoRotate = true;
        state.globe.controls().autoRotateSpeed = 0.3;
    }
}

function stopAutoRotate() {
    state.autoRotate = false;
    state.globe.controls().autoRotate = false;
}

function updateCoordinates() {
    const pov = state.globe.pointOfView();
    document.getElementById('coordinates').textContent = 
        `LAT: ${pov.lat.toFixed(2)}° / LON: ${pov.lng.toFixed(2)}°`;
}

// ===== DATA LOADING =====
async function loadAllData() {
    try {
        await Promise.all([
            loadVesselData(),
            loadFlightData(),
            loadThermalData(),
            loadGDELTData(),
            loadAlerts(),
            loadConvergenceSignals(),
            loadAircraftData(),
            loadSatelliteData(),
            loadMilitaryData(),
            loadRadiationData(),
            loadEarthquakeData(),
            loadGPSJammingData(),
            loadWebcamData(),
            loadCableData(),
            loadWildfireData(),
            loadCyberData(),
            loadUnrestData(),
            loadInfrastructureData(),
            loadMilitaryBasesData(),
            loadPipelineData(),
            loadTradeRouteData(),
            loadNuclearSitesData(),
            loadNewsData()
        ]);
        updateGlobeData();
        updateNewsTicker();
        populateNewsPanel();
        populateCctvPanel();
        populateMarketTicker();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function loadVesselData() {
    try {
        const response = await fetch('data/vessel_live.json');
        const data = await response.json();
        state.data.vessels = (data.vessels || []).filter(v => v.lat && v.lon);
        
        document.getElementById('vesselStatus').className = 'status-dot online';
        document.getElementById('vesselStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('vesselCount').textContent = data.tracked || state.data.vessels.length;
        document.getElementById('vesselLast').textContent = data.lastEvent || 'N/A';
    } catch (error) {
        document.getElementById('vesselStatus').className = 'status-dot error';
        document.getElementById('vesselStatusText').textContent = 'OFFLINE';
    }
}

async function loadFlightData() {
    try {
        const response = await fetch('data/flight_status.json');
        const data = await response.json();
        state.data.flights = data.flights || [];
        
        document.getElementById('flightStatus').className = 'status-dot online';
        document.getElementById('flightStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('flightCount').textContent = data.tracked || state.data.flights.length;
        document.getElementById('flightAnomalies').textContent = data.anomalies || 0;
    } catch (error) {
        document.getElementById('flightStatus').className = 'status-dot error';
        document.getElementById('flightStatusText').textContent = 'OFFLINE';
    }
}

async function loadThermalData() {
    try {
        const response = await fetch('data/thermal_status.json');
        const data = await response.json();
        state.data.thermal = data.hotspots || [];
        
        document.getElementById('thermalStatus').className = 'status-dot online';
        document.getElementById('thermalStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('thermalCount').textContent = data.count || state.data.thermal.length;
        document.getElementById('thermalLast').textContent = data.lastScan || 'N/A';
    } catch (error) {
        document.getElementById('thermalStatus').className = 'status-dot error';
        document.getElementById('thermalStatusText').textContent = 'OFFLINE';
    }
}

async function loadGDELTData() {
    try {
        const response = await fetch('data/gdelt_status.json');
        const data = await response.json();
        state.data.gdelt = data.events || [];
        
        document.getElementById('gdeltStatus').className = 'status-dot online';
        document.getElementById('gdeltStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('gdeltRate').textContent = data.eventsPerHour || 0;
        document.getElementById('gdeltSignificant').textContent = data.significant || 0;
    } catch (error) {
        document.getElementById('gdeltStatus').className = 'status-dot error';
        document.getElementById('gdeltStatusText').textContent = 'OFFLINE';
    }
}

async function loadAlerts() {
    try {
        const response = await fetch('data/alerts.json');
        const data = await response.json();
        state.data.alerts = data.alerts || [];
        displayAlerts();
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// ===== AIRCRAFT LIVE DATA =====
async function loadAircraftData() {
    try {
        const response = await fetch('data/flight_live.json');
        const data = await response.json();
        const commercial = (data.aircraft || []).filter(a => a.lat && a.lon);
        const military = (data.military_aircraft || []).filter(a => a.lat && a.lon);
        state.data.aircraft = [...commercial, ...military].slice(0, 2000);

        document.getElementById('aircraftStatus').className = 'status-dot online';
        document.getElementById('aircraftStatusText').textContent = 'ONLINE';
        document.getElementById('aircraftCount').textContent = commercial.length;
        document.getElementById('aircraftMilitary').textContent = military.length;
        document.getElementById('aircraftLast').textContent = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC';
    } catch (error) {
        document.getElementById('aircraftStatus').className = 'status-dot error';
        document.getElementById('aircraftStatusText').textContent = 'OFFLINE';
        state.data.aircraft = [];
    }
}

// ===== SATELLITE LIVE DATA =====
async function loadSatelliteData() {
    try {
        const response = await fetch('data/satellite_live.json');
        const data = await response.json();
        const civSats = (data.satellites || []).filter(s => s.lat && s.lon);
        const milSats = (data.military_sats || []).filter(s => s.lat && s.lon);
        state.data.satellites = [...civSats, ...milSats].slice(0, 500);

        document.getElementById('satelliteStatus').className = 'status-dot online';
        document.getElementById('satelliteStatusText').textContent = 'ONLINE';
        document.getElementById('satelliteCount').textContent = civSats.length + milSats.length;
        document.getElementById('satelliteMilitary').textContent = milSats.length;
        document.getElementById('satelliteLast').textContent = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC';
    } catch (error) {
        document.getElementById('satelliteStatus').className = 'status-dot error';
        document.getElementById('satelliteStatusText').textContent = 'OFFLINE';
        state.data.satellites = [];
    }
}

// ===== MILITARY LIVE DATA =====
async function loadMilitaryData() {
    try {
        const response = await fetch('data/military_live.json');
        const data = await response.json();
        state.data.military = data;

        const hotspots = data.hotspots || [];
        const vessels = data.military_vessels || [];
        const events = data.recent_events || [];
        const navalGroups = data.naval_groups || [];
        const totalAssets = vessels.length + navalGroups.reduce((s, g) => s + (g.vessels || []).length, 0);

        // Determine max threat level
        const levels = ['normal', 'elevated', 'high', 'critical'];
        let maxThreat = 'normal';
        hotspots.forEach(h => {
            const idx = levels.indexOf(h.threat_level);
            if (idx > levels.indexOf(maxThreat)) maxThreat = h.threat_level;
        });

        document.getElementById('militaryStatus').className = 'status-dot online';
        document.getElementById('militaryStatusText').textContent = 'ONLINE';
        document.getElementById('militaryAssets').textContent = totalAssets;
        document.getElementById('militaryHotspots').textContent = hotspots.length;
        const threatEl = document.getElementById('militaryThreat');
        threatEl.textContent = maxThreat.toUpperCase();
        threatEl.className = 'threat-level ' + maxThreat;
        document.getElementById('militaryLast').textContent = new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC';

        // Display military events in right panel
        displayMilitaryEvents(events);
    } catch (error) {
        document.getElementById('militaryStatus').className = 'status-dot error';
        document.getElementById('militaryStatusText').textContent = 'OFFLINE';
        state.data.military = {};
    }
}

function displayMilitaryEvents(events) {
    const feed = document.getElementById('militaryEventsFeed');
    if (!feed) return;
    feed.innerHTML = '';
    if (!events || events.length === 0) {
        feed.innerHTML = '<div style="color:#555;font-size:0.7rem;padding:8px;">No recent military events</div>';
        return;
    }
    events.forEach(evt => {
        const el = document.createElement('div');
        const sev = evt.severity || 'notable';
        el.className = `military-event-item severity-${sev}`;
        el.innerHTML = `
            <div class="mil-event-header">
                <span class="mil-event-type">${(evt.type || 'event').replace(/_/g, ' ').toUpperCase()}</span>
                <span class="mil-event-time">${evt.time || ''}</span>
            </div>
            <div class="mil-event-desc">${evt.description || ''}</div>
        `;
        feed.appendChild(el);
    });
}

// ===== WORLDMONITOR DATA LOADERS =====

async function loadRadiationData() {
    try {
        const r = await fetch('api/data/radiation_live.json');
        const data = await r.json();
        state.data.radiation = (data.stations || []).filter(s => s.lat && (s.lon || s.lng));
        document.getElementById('radiationStatus').className = 'status-dot online';
        document.getElementById('radiationStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('radiationCount').textContent = data.count || state.data.radiation.length;
        document.getElementById('radiationAnomalies').textContent = data.anomalies || 0;
    } catch (e) {
        document.getElementById('radiationStatus').className = 'status-dot error';
        document.getElementById('radiationStatusText').textContent = 'OFFLINE';
    }
}

async function loadEarthquakeData() {
    try {
        const r = await fetch('api/data/earthquake_live.json');
        const data = await r.json();
        state.data.earthquakes = (data.earthquakes || []).filter(q => q.lat && (q.lon || q.lng));
        document.getElementById('seismicStatus').className = 'status-dot online';
        document.getElementById('seismicStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('seismicCount').textContent = data.count || state.data.earthquakes.length;
        document.getElementById('seismicMaxMag').textContent = data.max_magnitude || (state.data.earthquakes.length ? Math.max(...state.data.earthquakes.map(q => q.magnitude || 0)).toFixed(1) : '--');
    } catch (e) {
        document.getElementById('seismicStatus').className = 'status-dot error';
        document.getElementById('seismicStatusText').textContent = 'OFFLINE';
    }
}

async function loadGPSJammingData() {
    try {
        const r = await fetch('api/data/gps_jamming_live.json');
        const data = await r.json();
        state.data.gpsJamming = (data.zones || []).filter(z => z.lat && (z.lon || z.lng));
        document.getElementById('gpsStatus').className = 'status-dot online';
        document.getElementById('gpsStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('gpsZones').textContent = data.count || state.data.gpsJamming.length;
        document.getElementById('gpsHighIntensity').textContent = data.high_intensity || state.data.gpsJamming.filter(z => z.intensity === 'high').length;
    } catch (e) {
        document.getElementById('gpsStatus').className = 'status-dot error';
        document.getElementById('gpsStatusText').textContent = 'OFFLINE';
    }
}

async function loadWebcamData() {
    try {
        const r = await fetch('api/data/webcam_live.json');
        const data = await r.json();
        state.data.webcams = (data.webcams || []).filter(c => c.lat && c.lng);
        document.getElementById('webcamStatus').className = 'status-dot online';
        document.getElementById('webcamStatusText').textContent = 'ONLINE';
        document.getElementById('webcamCount').textContent = state.data.webcams.length;
        document.getElementById('webcamLive').textContent = state.data.webcams.filter(w => w.status === 'active').length;
    } catch (e) {
        document.getElementById('webcamStatus').className = 'status-dot error';
        document.getElementById('webcamStatusText').textContent = 'OFFLINE';
    }
}

async function loadCableData() {
    try {
        const r = await fetch('api/data/cable_health_live.json');
        const data = await r.json();
        state.data.cables = data.cables || [];
        document.getElementById('cableStatus').className = 'status-dot online';
        document.getElementById('cableStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('cableMonitored').textContent = data.monitored || state.data.cables.length;
        const alertCount = Array.isArray(data.alerts) ? data.alerts.length : (data.alerts || state.data.cables.filter(c => c.status !== 'ok').length);
        document.getElementById('cableAlerts').textContent = alertCount;
    } catch (e) {
        document.getElementById('cableStatus').className = 'status-dot error';
        document.getElementById('cableStatusText').textContent = 'OFFLINE';
    }
}

async function loadWildfireData() {
    try {
        const r = await fetch('api/data/wildfire_live.json');
        const data = await r.json();
        state.data.wildfires = (data.fires || []).filter(f => f.lat && (f.lon || f.lng));
        document.getElementById('wildfireStatus').className = 'status-dot online';
        document.getElementById('wildfireStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('wildfireCount').textContent = data.count || state.data.wildfires.length;
        document.getElementById('wildfireClusters').textContent = data.clusters || 0;
    } catch (e) {
        document.getElementById('wildfireStatus').className = 'status-dot error';
        document.getElementById('wildfireStatusText').textContent = 'OFFLINE';
    }
}

async function loadCyberData() {
    try {
        const r = await fetch('api/data/cyber_threats_live.json');
        const data = await r.json();
        state.data.cyber = data.threats || [];
        document.getElementById('cyberStatus').className = 'status-dot online';
        document.getElementById('cyberStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('cyberActive').textContent = data.active || state.data.cyber.length;
        document.getElementById('cyberCritical').textContent = data.critical || state.data.cyber.filter(t => t.severity === 'critical').length;
    } catch (e) {
        document.getElementById('cyberStatus').className = 'status-dot error';
        document.getElementById('cyberStatusText').textContent = 'OFFLINE';
    }
}

async function loadUnrestData() {
    try {
        const r = await fetch('api/data/unrest_live.json');
        const data = await r.json();
        state.data.unrest = (data.events || []).filter(u => u.lat && (u.lon || u.lng));
        document.getElementById('unrestStatus').className = 'status-dot online';
        document.getElementById('unrestStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('unrestTotal').textContent = data.total || state.data.unrest.length;
        document.getElementById('unrestHotspots').textContent = data.hotspots || 0;
    } catch (e) {
        document.getElementById('unrestStatus').className = 'status-dot error';
        document.getElementById('unrestStatusText').textContent = 'OFFLINE';
    }
}

async function loadInfrastructureData() {
    try {
        const r = await fetch('api/data/infrastructure_live.json');
        const data = await r.json();
        state.data.infrastructure = (data.sites || []).filter(s => s.lat && (s.lon || s.lng));
        document.getElementById('infraStatus').className = 'status-dot online';
        document.getElementById('infraStatusText').textContent = data.status || 'ONLINE';
        document.getElementById('infraMonitored').textContent = data.monitored || state.data.infrastructure.length;
        document.getElementById('infraDisruptions').textContent = data.disruptions || state.data.infrastructure.filter(s => s.status === 'disrupted').length;
    } catch (e) {
        document.getElementById('infraStatus').className = 'status-dot error';
        document.getElementById('infraStatusText').textContent = 'OFFLINE';
    }
}

async function loadMilitaryBasesData() {
    try {
        const r = await fetch('api/data/military_bases.json');
        const data = await r.json();
        state.data.militaryBases = (data.bases || []).filter(b => b.lat && (b.lon || b.lng));
    } catch (e) { state.data.militaryBases = []; }
}

async function loadPipelineData() {
    try {
        const r = await fetch('api/data/pipelines.json');
        const data = await r.json();
        state.data.pipelines = data.pipelines || [];
    } catch (e) { state.data.pipelines = []; }
}

async function loadTradeRouteData() {
    try {
        const r = await fetch('api/data/trade_routes.json');
        const data = await r.json();
        state.data.tradeRoutes = data.routes || [];
    } catch (e) { state.data.tradeRoutes = []; }
}

async function loadNuclearSitesData() {
    try {
        const r = await fetch('api/data/nuclear_sites.json');
        const data = await r.json();
        state.data.nuclearSites = (data.sites || []).filter(s => s.lat && (s.lon || s.lng));
    } catch (e) { state.data.nuclearSites = []; }
}

async function loadNewsData() {
    try {
        const r = await fetch('data/news_live.json');
        const data = await r.json();
        state.data.news = (data.geolocated_articles || []).filter(a => a.lat && (a.lon || a.lng));
        state.data.newsHeadlines = data.headlines || [];
        state.data.newsAll = [...state.data.news, ...state.data.newsHeadlines];
    } catch (e) {
        state.data.news = [];
        state.data.newsHeadlines = [];
        state.data.newsAll = [];
    }
}

function updateNewsTicker() {
    const articles = state.data.newsAll || [];
    if (!articles.length) return;
    
    // Create or update ticker
    let ticker = document.getElementById('newsTicker');
    if (!ticker) {
        ticker = document.createElement('div');
        ticker.id = 'newsTicker';
        ticker.style.cssText = 'position:fixed;bottom:30px;left:200px;right:200px;height:28px;overflow:hidden;background:rgba(10,10,15,0.9);border:1px solid #00ffcc33;font-family:JetBrains Mono,monospace;font-size:0.7rem;z-index:100;display:flex;align-items:center;';
        const label = document.createElement('span');
        label.style.cssText = 'background:#ff3333;color:#0a0a0f;padding:2px 8px;font-weight:bold;white-space:nowrap;font-size:0.65rem;';
        label.textContent = '⚡ LIVE';
        ticker.appendChild(label);
        const scroll = document.createElement('div');
        scroll.id = 'newsTickerScroll';
        scroll.style.cssText = 'flex:1;overflow:hidden;white-space:nowrap;';
        const inner = document.createElement('span');
        inner.id = 'newsTickerInner';
        inner.style.cssText = 'display:inline-block;animation:tickerScroll 120s linear infinite;color:#ccc;';
        scroll.appendChild(inner);
        ticker.appendChild(scroll);
        document.body.appendChild(ticker);
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = '@keyframes tickerScroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }';
        document.head.appendChild(style);
    }
    
    const inner = document.getElementById('newsTickerInner');
    if (inner) {
        const severityColors = { critical: '#ff3333', high: '#ff6600', medium: '#ffd700', low: '#888' };
        inner.innerHTML = articles.slice(0, 50).map(a => {
            const color = severityColors[a.severity] || '#888';
            const dot = a.severity === 'critical' ? '🔴' : a.severity === 'high' ? '🟠' : '•';
            return `<span style="margin:0 30px;">${dot} <span style="color:${color}">[${a.source}]</span> ${a.title}</span>`;
        }).join('');
    }
}

// ===== NEWS PANEL POPULATION =====
function populateNewsPanel() {
    const feed = document.getElementById('newsFeed');
    if (!feed) return;
    const articles = state.data.newsAll || [];
    if (!articles.length) { feed.innerHTML = '<div style="color:#555;padding:12px;text-align:center">No news data loaded</div>'; return; }
    
    const severityColors = { critical: '#ff3333', high: '#ff6600', medium: '#ffd700', low: '#666' };
    const sourceColors = { 'BBC World': '#bb1919', 'BBC Business': '#bb1919', 'Al Jazeera': '#fa9800', 'NPR World': '#689ad8', 'France24': '#0055a4', 'GDELT': '#00ffcc' };
    
    feed.innerHTML = articles.slice(0, 60).map(a => {
        const sevColor = severityColors[a.severity] || '#666';
        const srcColor = sourceColors[a.source] || '#555';
        const dot = a.severity === 'critical' ? 'pulse' : '';
        return `<div class="news-item" onclick="${a.url ? `window.open('${a.url}','_blank')` : ''}" style="cursor:${a.url ? 'pointer' : 'default'}">
            <span class="severity-dot ${dot}" style="background:${sevColor}"></span>
            <span class="news-source-badge" style="background:${srcColor}">${a.source?.split(' ')[0] || 'NEWS'}</span>
            <span class="news-title">${a.title || ''}</span>
            ${a.category ? `<span class="category-badge" style="opacity:0.5;font-size:0.55rem">${a.category}</span>` : ''}
        </div>`;
    }).join('');
}

// News filter
window.filterNews = function(category) {
    // Update active button
    document.querySelectorAll('.news-filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    const feed = document.getElementById('newsFeed');
    if (!feed) return;
    const articles = state.data.newsAll || [];
    const filtered = category === 'all' ? articles : articles.filter(a => a.category === category);
    
    const severityColors = { critical: '#ff3333', high: '#ff6600', medium: '#ffd700', low: '#666' };
    const sourceColors = { 'BBC World': '#bb1919', 'BBC Business': '#bb1919', 'Al Jazeera': '#fa9800', 'NPR World': '#689ad8', 'France24': '#0055a4' };
    
    feed.innerHTML = filtered.slice(0, 60).map(a => {
        const sevColor = severityColors[a.severity] || '#666';
        const srcColor = sourceColors[a.source] || '#555';
        return `<div class="news-item" onclick="${a.url ? `window.open('${a.url}','_blank')` : ''}" style="cursor:pointer">
            <span class="severity-dot" style="background:${sevColor}"></span>
            <span class="news-source-badge" style="background:${srcColor}">${a.source?.split(' ')[0] || 'NEWS'}</span>
            <span class="news-title">${a.title || ''}</span>
        </div>`;
    }).join('');
    
    if (!filtered.length) feed.innerHTML = '<div style="color:#555;padding:12px;text-align:center">No articles in this category</div>';
};

// ===== CCTV PANEL POPULATION =====
function populateCctvPanel() {
    const grid = document.getElementById('cctvGrid');
    const list = document.getElementById('cctvList');
    if (!grid || !list) return;
    
    const webcams = state.data.webcams || [];
    if (!webcams.length) return;
    
    // Top 4 by view count for the grid
    const top4 = webcams.filter(w => w.status === 'active' && w.player?.day).slice(0, 4);
    
    // Update grid slots
    const slots = grid.querySelectorAll('.cctv-slot');
    top4.forEach((cam, i) => {
        if (slots[i]) {
            const header = slots[i].querySelector('.cctv-slot-header span') || slots[i].querySelector('.cctv-slot-header');
            if (header) header.textContent = `${cam.title} — ${cam.city || cam.country || ''}`;
            const iframe = slots[i].querySelector('iframe');
            if (iframe && cam.player?.day) {
                iframe.src = cam.player.day;
                iframe.style.display = 'block';
            }
            const placeholder = slots[i].querySelector('.cctv-placeholder');
            if (placeholder) placeholder.style.display = 'none';
        }
    });
    
    // Populate camera list
    const catColors = { traffic: '#ffd700', maritime: '#00aaff', aviation: '#44ffaa', military: '#ff3366', border: '#ffaa00', urban: '#00ddff', landscape: '#66ff66', weather: '#aaccff' };
    list.innerHTML = webcams.slice(0, 50).map(cam => {
        const catColor = catColors[cam.category] || '#888';
        return `<div class="cctv-list-item" data-id="${cam.id}">
            <span style="color:#00ddff;margin-right:6px">📹</span>
            <span class="cctv-cam-name">${cam.title}</span>
            <span style="color:#555;font-size:0.65rem;margin:0 4px">${cam.city || ''}${cam.city && cam.country ? ', ' : ''}${cam.country || ''}</span>
            <span class="category-badge" style="background:${catColor}22;color:${catColor};border:1px solid ${catColor}44">${cam.category || 'cam'}</span>
            <button class="cctv-pin-btn" onclick="pinWebcam(${cam.id})">PIN</button>
        </div>`;
    }).join('');
}

// Pin webcam to grid
window.pinWebcam = async function(webcamId) {
    const cam = (state.data.webcams || []).find(w => w.id === webcamId);
    if (!cam) return;
    
    // Refresh image URLs
    try {
        const r = await fetch(`/api/webcam/${webcamId}/refresh`);
        if (r.ok) {
            const fresh = await r.json();
            if (fresh.player) cam.player = fresh.player;
        }
    } catch(e) {}
    
    // Find first empty or replace last grid slot
    const grid = document.getElementById('cctvGrid');
    const slots = grid.querySelectorAll('.cctv-slot');
    let targetSlot = null;
    for (const slot of slots) {
        const iframe = slot.querySelector('iframe');
        if (!iframe || !iframe.src || iframe.src === 'about:blank') { targetSlot = slot; break; }
    }
    if (!targetSlot) targetSlot = slots[slots.length - 1]; // Replace last
    
    if (targetSlot) {
        const header = targetSlot.querySelector('.cctv-slot-header span') || targetSlot.querySelector('.cctv-slot-header');
        if (header) header.textContent = `${cam.title} — ${cam.city || ''}`;
        const iframe = targetSlot.querySelector('iframe');
        if (iframe && cam.player?.day) {
            iframe.src = cam.player.day;
            iframe.style.display = 'block';
        }
        const placeholder = targetSlot.querySelector('.cctv-placeholder');
        if (placeholder) placeholder.style.display = 'none';
    }
};

// ===== MARKET TICKER =====
async function populateMarketTicker() {
    try {
        const r = await fetch('data/market_status.json');
        const data = await r.json();
        const m = data.markets || {};
        
        const setTicker = (id, changeId, val, changePct) => {
            const el = document.getElementById(id);
            const chEl = document.getElementById(changeId);
            if (el && val != null) el.textContent = typeof val === 'number' ? val.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 1}) : val;
            if (chEl && changePct != null) {
                const sign = changePct >= 0 ? '+' : '';
                chEl.textContent = `${sign}${changePct.toFixed(2)}%`;
                chEl.style.color = changePct >= 0 ? '#00ff66' : '#ff3333';
            }
        };
        
        if (m.VIX) setTicker('tickerVix', 'tickerVixChange', m.VIX.value, m.VIX.change_pct);
        if (m.OIL) setTicker('tickerOil', 'tickerOilChange', m.OIL.value, m.OIL.change_pct);
        if (m.GOLD) setTicker('tickerGold', 'tickerGoldChange', m.GOLD.value, m.GOLD.change_pct);
        if (m.DXY) setTicker('tickerDxy', 'tickerDxyChange', m.DXY.value, m.DXY.change_pct);
        if (m.BTC) setTicker('tickerBtc', 'tickerBtcChange', m.BTC.value, m.BTC.change_pct);
        
        // Also update sidebar market card
        const vixEl = document.getElementById('marketVix');
        if (vixEl && m.VIX) vixEl.textContent = m.VIX.value;
    } catch(e) { console.warn('Market ticker load failed:', e); }
}

// ===== ALERT DISPLAY =====
function displayAlerts() {
    const feed = document.getElementById('alertFeed');
    feed.innerHTML = '';
    
    state.data.alerts.forEach(alert => {
        const alertEl = document.createElement('div');
        alertEl.className = `alert-item ${alert.severity}`;
        alertEl.innerHTML = `
            <div class="alert-header">
                <span class="alert-severity ${alert.severity}">${alert.severity.toUpperCase()}</span>
                <span class="alert-time">${alert.time}</span>
            </div>
            <div class="alert-message">${alert.message}</div>
        `;
        feed.appendChild(alertEl);
    });
    
    // Pause auto-scroll on hover (desktop only)
    if (window.matchMedia('(hover: hover)').matches) {
        feed.addEventListener('mouseenter', () => {
            feed.style.overflowY = 'hidden';
        });
        feed.addEventListener('mouseleave', () => {
            feed.style.overflowY = 'auto';
        });
    }
    
    // Smooth scrolling on mobile
    feed.style.webkitOverflowScrolling = 'touch';
}

// ===== GLOBE DATA UPDATE =====
function updateGlobeData() {
    // Build combined objects data (vessels + satellites)
    const combinedObjects = [];
    
    // Vessels — 3D arrow markers colour-coded by type
    if (state.layers.vessels) {
        const sorted = [...state.data.vessels].sort((a, b) => {
            const typeScore = t => t === 'tanker' ? 3 : t === 'cargo' ? 2 : 1;
            const sa = typeScore(a.type) * 10 + (a.speed || 0);
            const sb = typeScore(b.type) * 10 + (b.speed || 0);
            return sb - sa;
        });
        const visible = sorted.slice(0, 4000);
        visible.forEach(v => combinedObjects.push({ ...v, _kind: 'vessel' }));
    }
    
    // Aircraft — arrow markers with heading
    if (state.layers.aircraft) {
        state.data.aircraft.forEach(a => combinedObjects.push({ ...a, _kind: 'aircraft' }));
    }
    
    // Satellites — diamond markers at varying altitudes
    if (state.layers.satellites) {
        state.data.satellites.forEach(s => combinedObjects.push({ ...s, _kind: 'satellite' }));
    }
    
    // Military vessels — distinct magenta markers
    if (state.layers.military && state.data.military.military_vessels) {
        state.data.military.military_vessels.forEach(m => combinedObjects.push({ ...m, _kind: 'military_vessel' }));
    }
    
    // Market impact lines as custom objects
    if (state.layers.markets && state.data.markets && state.data.markets.correlations) {
        state.data.markets.correlations.forEach(c => combinedObjects.push({ ...c, _kind: 'market' }));
    }
    
    // Radiation stations
    if (state.layers.radiation) {
        state.data.radiation.slice(0, 500).forEach(s => combinedObjects.push({ ...s, _kind: 'radiation' }));
    }
    
    // Earthquakes
    if (state.layers.earthquakes) {
        state.data.earthquakes.slice(0, 200).forEach(q => combinedObjects.push({ ...q, _kind: 'earthquake' }));
    }
    
    // GPS Jamming zones
    if (state.layers.gps) {
        state.data.gpsJamming.slice(0, 100).forEach(z => combinedObjects.push({ ...z, _kind: 'gps_jamming' }));
    }
    
    // Webcams
    if (state.layers.webcams) {
        state.data.webcams.slice(0, 500).forEach(c => combinedObjects.push({ ...c, _kind: 'webcam' }));
    }
    
    // News events (geolocated)
    if (state.data.news) {
        state.data.news.slice(0, 100).forEach(n => combinedObjects.push({ ...n, _kind: 'news' }));
    }
    
    // Wildfires
    if (state.layers.wildfires) {
        state.data.wildfires.slice(0, 500).forEach(f => combinedObjects.push({ ...f, _kind: 'wildfire' }));
    }
    
    // Unrest events
    if (state.layers.unrest) {
        state.data.unrest.slice(0, 200).forEach(u => combinedObjects.push({ ...u, _kind: 'unrest' }));
    }
    
    // Infrastructure
    if (state.layers.infrastructure) {
        state.data.infrastructure.slice(0, 200).forEach(i => combinedObjects.push({ ...i, _kind: 'infrastructure' }));
    }
    
    // Military bases
    if (state.layers.bases) {
        state.data.militaryBases.slice(0, 300).forEach(b => combinedObjects.push({ ...b, _kind: 'base' }));
    }
    
    // Nuclear sites
    if (state.layers.nuclear) {
        state.data.nuclearSites.slice(0, 200).forEach(n => combinedObjects.push({ ...n, _kind: 'nuclear' }));
    }
    
    state.globe
        .objectsData(combinedObjects)
        .objectLat(d => d.lat)
        .objectLng(d => d.lng || d.lon)
        .objectAltitude(d => {
            if (d._kind === 'aircraft') return 0.01 + (d.alt || 0) / 5000000;
            if (d._kind === 'satellite') return 0.04 + (d.alt_km || 400) / 20000;
            if (d._kind === 'military_vessel') return 0.006;
            if (d._kind === 'market') return 0.01;
            if (d._kind === 'gps_jamming') return 0.002;
            if (d._kind === 'base') return 0.004;
            return 0.005;
        })
        .objectThreeObject(d => {
            if (d._kind === 'vessel') return createVesselObject(d);
            if (d._kind === 'aircraft') return createAircraftObject(d);
            if (d._kind === 'satellite') return createSatelliteObject(d);
            if (d._kind === 'military_vessel') return createMilitaryVesselObject(d);
            if (d._kind === 'market') return createMarketObject(d);
            if (d._kind === 'radiation') return createRadiationObject(d);
            if (d._kind === 'earthquake') return createEarthquakeObject(d);
            if (d._kind === 'gps_jamming') return createGPSJammingObject(d);
            if (d._kind === 'webcam') return createWebcamObject(d);
            if (d._kind === 'wildfire') return createWildfireObject(d);
            if (d._kind === 'unrest') return createUnrestObject(d);
            if (d._kind === 'infrastructure') return createInfraObject(d);
            if (d._kind === 'base') return createBaseObject(d);
            if (d._kind === 'nuclear') return createNuclearObject(d);
            if (d._kind === 'news') return createNewsObject(d);
            return new THREE.Mesh(new THREE.SphereGeometry(0.1), new THREE.MeshBasicMaterial({ color: 0xffffff }));
        })
        .onObjectClick(d => {
            if (d._kind === 'vessel') return handleVesselClick(d);
            if (d._kind === 'aircraft') return handleAircraftClick(d);
            if (d._kind === 'satellite') return handleSatelliteClick(d);
            if (d._kind === 'military_vessel') return handleMilitaryVesselClick(d);
            if (d._kind === 'market') return handleMarketClick(d);
            if (d._kind === 'radiation') return handleRadiationClick(d);
            if (d._kind === 'earthquake') return handleEarthquakeClick(d);
            if (d._kind === 'gps_jamming') return handleGPSJammingClick(d);
            if (d._kind === 'webcam') return handleWebcamClick(d);
            if (d._kind === 'wildfire') return handleWildfireClick(d);
            if (d._kind === 'unrest') return handleUnrestClick(d);
            if (d._kind === 'infrastructure') return handleInfraClick(d);
            if (d._kind === 'base') return handleBaseClick(d);
            if (d._kind === 'nuclear') return handleNuclearClick(d);
            if (d._kind === 'news') return handleNewsClick(d);
        });
    
    // Arcs: flights + satellite orbit trails + market correlation lines
    const allArcs = [];
    
    if (state.layers.flights) {
        state.data.flights.forEach(f => {
            allArcs.push({
                startLat: f.origin.lat,
                startLng: f.origin.lng,
                endLat: f.destination.lat,
                endLng: f.destination.lng,
                color: '#ffd700',
                stroke: 0.5,
                dashLen: 0.4,
                dashGap: 0.2,
                dashTime: 3000
            });
        });
    }
    
    // Satellite orbit trails
    if (state.layers.satellites) {
        state.data.satellites.forEach(s => {
            if (s.orbit_trail) {
                allArcs.push({
                    startLat: s.orbit_trail.startLat || s.lat,
                    startLng: s.orbit_trail.startLng || (s.lng || s.lon) - 15,
                    endLat: s.orbit_trail.endLat || s.lat,
                    endLng: s.orbit_trail.endLng || (s.lng || s.lon) + 15,
                    color: s.type === 'military' ? 'rgba(255,51,68,0.4)' :
                           s.type === 'reconnaissance' ? 'rgba(255,170,0,0.4)' :
                           'rgba(255,255,255,0.3)',
                    stroke: 0.3,
                    dashLen: 0.6,
                    dashGap: 0.3,
                    dashTime: 5000
                });
            }
        });
    }
    
    // Cyber threat arcs (source → target)
    if (state.layers.cyber) {
        state.data.cyber.forEach(t => {
            if (t.source_lat && t.source_lng && t.target_lat && t.target_lng) {
                const typeColor = t.type === 'ransomware' ? 'rgba(255,51,51,0.7)' :
                                  t.type === 'ddos' ? 'rgba(255,215,0,0.7)' :
                                  t.type === 'espionage' ? 'rgba(0,221,255,0.7)' :
                                  'rgba(255,140,0,0.6)';
                allArcs.push({
                    startLat: t.source_lat, startLng: t.source_lng,
                    endLat: t.target_lat, endLng: t.target_lng,
                    color: typeColor, stroke: 0.6,
                    dashLen: 0.3, dashGap: 0.15, dashTime: 1500
                });
            }
        });
    }
    
    // Market correlation lines (geo event → market hub)
    if (state.layers.markets && state.data.markets && state.data.markets.correlations) {
        state.data.markets.correlations.forEach(c => {
            if (c.event_lat && c.event_lng && c.market_lat && c.market_lng) {
                const color = (c.impact || 0) >= 0 ? 'rgba(0,255,100,0.5)' : 'rgba(255,51,68,0.5)';
                allArcs.push({
                    startLat: c.event_lat,
                    startLng: c.event_lng,
                    endLat: c.market_lat,
                    endLng: c.market_lng,
                    color: color,
                    stroke: 0.4,
                    dashLen: 0.3,
                    dashGap: 0.15,
                    dashTime: 2000
                });
            }
        });
    }
    
    state.globe
        .arcsData(allArcs)
        .arcColor('color')
        .arcStroke(d => d.stroke || 0.5)
        .arcDashLength(d => d.dashLen || 0.4)
        .arcDashGap(d => d.dashGap || 0.2)
        .arcDashAnimateTime(d => d.dashTime || 3000);
    
    // Rings: thermal + military pulsing + chokepoints
    const allRings = [];
    
    if (state.layers.thermal) {
        state.data.thermal.forEach(h => {
            allRings.push({
                lat: h.lat,
                lng: h.lng || h.lon,
                color: () => '#ff3333',
                maxR: 2,
                speed: 2,
                repeat: 1500
            });
        });
    }
    
    // Military hotspot pulsing threat rings
    if (state.layers.military && state.data.military.hotspots) {
        const threatSpeed = { normal: 1, elevated: 2, high: 3, critical: 4 };
        state.data.military.hotspots.forEach(h => {
            const spd = threatSpeed[h.threat_level] || 2;
            allRings.push({
                lat: h.lat,
                lng: h.lng || h.lon,
                color: h.threat_level === 'critical' ? () => '#ff0000' :
                       h.threat_level === 'high' ? () => '#ff6600' :
                       h.threat_level === 'elevated' ? () => '#ffaa00' :
                       () => '#ff3344',
                maxR: (h.radius_km || 200) / 80,
                speed: spd,
                repeat: 1200 - spd * 200,
                _hotspot: h
            });
        });
    }
    
    // Earthquake pulsing rings
    if (state.layers.earthquakes) {
        state.data.earthquakes.forEach(q => {
            const mag = q.magnitude || 0;
            if (mag >= 3) {
                allRings.push({
                    lat: q.lat, lng: q.lng || q.lon,
                    color: mag >= 7 ? () => '#ff0000' : mag >= 5 ? () => '#ff8c00' : () => '#ffd700',
                    maxR: mag >= 7 ? 6 : mag >= 5 ? 3 : 1.5,
                    speed: mag >= 7 ? 4 : mag >= 5 ? 2.5 : 1.5,
                    repeat: mag >= 7 ? 600 : mag >= 5 ? 1000 : 2000
                });
            }
        });
    }
    
    // Radiation spike rings
    if (state.layers.radiation) {
        state.data.radiation.forEach(s => {
            if (s.severity === 'spike' || s.severity === 'elevated') {
                allRings.push({
                    lat: s.lat, lng: s.lng || s.lon,
                    color: s.severity === 'spike' ? () => '#ff3333' : () => '#ffd700',
                    maxR: s.severity === 'spike' ? 3 : 1.5,
                    speed: s.severity === 'spike' ? 3 : 1.5,
                    repeat: s.severity === 'spike' ? 800 : 1500
                });
            }
        });
    }
    
    if (state.layers.chokepoints) {
        chokepoints.forEach(cp => {
            allRings.push({
                lat: cp.lat,
                lng: cp.lng,
                color: cp.name.includes('Hormuz') ? () => '#ff0000' : () => 'rgba(0,255,204,0.3)',
                maxR: cp.name.includes('Hormuz') ? 4 : 2,
                speed: cp.name.includes('Hormuz') ? 3 : 1,
                repeat: cp.name.includes('Hormuz') ? 800 : 2000
            });
        });
    }
    
    state.globe
        .ringsData(allRings)
        .ringLat('lat')
        .ringLng('lng')
        .ringColor('color')
        .ringMaxRadius(d => d.maxR || 2)
        .ringPropagationSpeed(d => d.speed || 2)
        .ringRepeatPeriod(d => d.repeat || 1500);
    
    // Chokepoint labels
    if (state.layers.chokepoints) {
        state.globe
            .labelsData(chokepoints)
            .labelLat('lat')
            .labelLng('lng')
            .labelText('name')
            .labelSize(0.6)
            .labelDotRadius(0.3)
            .labelDotOrientation(() => 'bottom')
            .labelColor(() => 'rgba(255, 215, 0, 0.85)')
            .labelResolution(2)
            .labelAltitude(0.015);
    } else {
        state.globe.labelsData([]);
    }
    
    // Paths: cables, pipelines, trade routes
    const allPaths = [];
    
    if (state.layers.cables) {
        state.data.cables.forEach(c => {
            if (c.coords && c.coords.length >= 2) {
                const color = c.status === 'fault' ? ['#ff3333', '#ff3333'] :
                              c.status === 'degraded' ? ['#ffd700', '#ffd700'] :
                              ['#0088ff', '#0088ff'];
                allPaths.push({
                    coords: c.coords, color: color,
                    stroke: c.status === 'fault' ? 1.5 : 1,
                    dashLen: 0.5, dashGap: 0.25, dashTime: 5000,
                    _kind: 'cable', _data: c
                });
            }
        });
    }
    
    if (state.layers.pipelines) {
        state.data.pipelines.forEach(p => {
            if (p.coords && p.coords.length >= 2) {
                const color = p.type === 'oil' ? ['#ff4444', '#ff4444'] :
                              p.type === 'gas' ? ['#4488ff', '#4488ff'] :
                              ['#00ddff', '#00ddff']; // LNG
                allPaths.push({
                    coords: p.coords, color: color,
                    stroke: 0.8, dashLen: 0.4, dashGap: 0.2, dashTime: 6000,
                    _kind: 'pipeline', _data: p
                });
            }
        });
    }
    
    if (state.layers.traderoutes) {
        state.data.tradeRoutes.forEach(tr => {
            if (tr.coords && tr.coords.length >= 2) {
                allPaths.push({
                    coords: tr.coords, color: ['rgba(0,255,204,0.4)', 'rgba(0,255,204,0.4)'],
                    stroke: 0.5, dashLen: 0.6, dashGap: 0.3, dashTime: 8000,
                    _kind: 'traderoute', _data: tr
                });
            }
        });
    }
    
    state.globe
        .pathsData(allPaths)
        .pathPoints('coords')
        .pathPointLat(p => p[0])
        .pathPointLng(p => p[1])
        .pathColor('color')
        .pathStroke(d => d.stroke || 1)
        .pathDashLength(d => d.dashLen || 0.5)
        .pathDashGap(d => d.dashGap || 0.25)
        .pathDashAnimateTime(d => d.dashTime || 5000);
}

// ===== THREE.JS OBJECT FACTORIES =====

function createVesselObject(d) {
    // ⚓ VESSEL — boat/ship shape: elongated hull with wake
    const spd = d.speed || 0;
    const vtype = d.type || 'other';
    let color;
    if (vtype === 'tanker') color = 0xff4444;
    else if (vtype === 'cargo') color = 0x44aaff;
    else if (vtype === 'passenger') color = 0xffff44;
    else if (vtype === 'military') color = 0xff00ff;
    else if (vtype === 'fishing') color = 0x44ff44;
    else if (spd < 0.5) color = 0xff8800;
    else color = 0x00ffcc;

    const size = spd > 5 ? 0.35 : (spd > 0.5 ? 0.25 : 0.18);
    const group = new THREE.Group();
    // Hull shape — elongated diamond
    const hullGeo = new THREE.ConeGeometry(size * 0.25, size * 0.8, 3);
    hullGeo.rotateX(Math.PI / 2);
    const hullMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85 });
    group.add(new THREE.Mesh(hullGeo, hullMat));
    // Wake indicator for moving vessels
    if (spd > 2) {
        const wakeGeo = new THREE.PlaneGeometry(size * 0.15, size * 0.6);
        const wakeMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
        const wake = new THREE.Mesh(wakeGeo, wakeMat);
        wake.position.z = -size * 0.5;
        group.add(wake);
    }
    return group;
}

function createSatelliteObject(d) {
    const cat = d.category || 'civilian';
    const name = (d.name || '').toLowerCase();
    let color;
    if (cat === 'military') color = 0xff3344;
    else if (cat === 'science') color = 0x00ff66;
    else if (cat === 'navigation') color = 0xffd700;
    else if (cat === 'comms') color = 0x00ddff;
    else if (name.includes('starlink')) color = 0x8888ff;
    else color = 0xccccff;

    const isISS = name.includes('iss') || name === 'iss (zarya)';
    const isTiangong = name.includes('tiangong') || name.includes('css');
    const isNotable = isISS || isTiangong || cat === 'military';
    const size = isISS || isTiangong ? 0.7 : (cat === 'military' ? 0.5 : (name.includes('starlink') ? 0.18 : 0.35));

    const group = new THREE.Group();
    // Diamond shape — larger and brighter
    const topGeo = new THREE.ConeGeometry(size * 0.5, size * 0.6, 4);
    const botGeo = new THREE.ConeGeometry(size * 0.5, size * 0.6, 4);
    botGeo.rotateX(Math.PI);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: isNotable ? 1.0 : 0.9 });

    const top = new THREE.Mesh(topGeo, mat);
    top.position.y = size * 0.2;
    const bot = new THREE.Mesh(botGeo, mat);
    bot.position.y = -size * 0.2;
    group.add(top, bot);

    // Pulsing glow ring — bigger for visibility
    const glowGeo = new THREE.RingGeometry(size * 0.6, size * 0.85, isNotable ? 16 : 6);
    const glowMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: isNotable ? 0.5 : 0.35, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(glowGeo, glowMat));

    // Outer beacon ring for notable sats (ISS, Tiangong, military)
    if (isNotable) {
        const beaconGeo = new THREE.RingGeometry(size * 1.0, size * 1.3, 16);
        const beaconMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
        group.add(new THREE.Mesh(beaconGeo, beaconMat));
    }

    if (isISS) {
        // Extra outer ring for ISS visibility
        const outerGeo = new THREE.RingGeometry(size * 0.8, size * 1.0, 16);
        const outerMat = new THREE.MeshBasicMaterial({ color: 0x00ff66, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
        group.add(new THREE.Mesh(outerGeo, outerMat));
    }

    return group;
}

function createMilitaryObject(d) {
    const intensity = d.intensity || 1;
    const size = 0.3 + intensity * 0.25;
    
    const group = new THREE.Group();
    
    // Core pulsing sphere
    const coreGeo = new THREE.SphereGeometry(size * 0.3, 8, 8);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0xff3344, transparent: true, opacity: 0.8 });
    group.add(new THREE.Mesh(coreGeo, coreMat));
    
    // Outer glow ring
    const ringGeo = new THREE.RingGeometry(size * 0.5, size * 0.7, 16);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xff3344, transparent: true, opacity: 0.3, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(ringGeo, ringMat));
    
    // Second larger glow for high intensity
    if (intensity >= 3) {
        const outerGeo = new THREE.RingGeometry(size * 0.8, size * 1.0, 16);
        const outerMat = new THREE.MeshBasicMaterial({ color: 0xff0000, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
        group.add(new THREE.Mesh(outerGeo, outerMat));
    }
    
    return group;
}

function createMarketObject(d) {
    const impact = d.impact || 0;
    const color = impact >= 0 ? 0x00ff66 : 0xff3344;
    const size = 0.2;
    const geo = new THREE.BoxGeometry(size, size * 1.5, size);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7 });
    return new THREE.Mesh(geo, mat);
}

function createAircraftObject(d) {
    const cat = d.category || 'commercial';
    let color;
    if (cat === 'military') color = 0xff00ff;
    else if (cat === 'cargo') color = 0x4488ff;
    else if (cat === 'helicopter') color = 0xffff00;
    else color = 0x00ddff; // commercial = cyan

    const size = cat === 'military' ? 0.35 : 0.25;
    // Arrow/triangle shape pointing in heading direction
    const geo = new THREE.ConeGeometry(size * 0.35, size, 3);
    geo.rotateX(Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const mesh = new THREE.Mesh(geo, mat);

    // Rotate to match heading
    const heading = (d.heading || 0) * (Math.PI / 180);
    mesh.rotation.z = -heading;

    // Glow for military aircraft
    if (cat === 'military') {
        const glowGeo = new THREE.RingGeometry(size * 0.4, size * 0.6, 6);
        const glowMat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.25, side: THREE.DoubleSide });
        mesh.add(new THREE.Mesh(glowGeo, glowMat));
    }

    return mesh;
}

function createMilitaryVesselObject(d) {
    const size = 0.45;
    const group = new THREE.Group();

    // Core cone marker
    const geo = new THREE.ConeGeometry(size * 0.4, size, 4);
    geo.rotateX(Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.9 });
    group.add(new THREE.Mesh(geo, mat));

    // Magenta glow ring
    const ringGeo = new THREE.RingGeometry(size * 0.5, size * 0.7, 8);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.35, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(ringGeo, ringMat));

    // Outer glow
    const outerGeo = new THREE.RingGeometry(size * 0.8, size * 1.0, 8);
    const outerMat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(outerGeo, outerMat));

    return group;
}

// ===== DISTINCTIVE ICON FACTORIES — each type has a unique shape =====

function createRadiationObject(d) {
    // ☢️ RADIATION — trefoil: 3 fan blades + center dot (iconic nuclear symbol)
    const sev = d.severity || d.status || 'normal';
    const color = sev === 'spike' ? 0xff3333 : sev === 'elevated' ? 0xffd700 : 0x00ff66;
    const size = sev === 'spike' ? 0.4 : 0.28;
    const group = new THREE.Group();
    // Center circle
    const coreGeo = new THREE.SphereGeometry(size * 0.2, 8, 8);
    const coreMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95 });
    group.add(new THREE.Mesh(coreGeo, coreMat));
    // Three fan blades (trefoil)
    for (let i = 0; i < 3; i++) {
        const bladeGeo = new THREE.CircleGeometry(size * 0.45, 8, 0, Math.PI * 0.5);
        const bladeMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.5, side: THREE.DoubleSide });
        const blade = new THREE.Mesh(bladeGeo, bladeMat);
        blade.rotation.z = (i * Math.PI * 2) / 3;
        blade.position.x = Math.cos((i * Math.PI * 2) / 3) * size * 0.15;
        blade.position.y = Math.sin((i * Math.PI * 2) / 3) * size * 0.15;
        group.add(blade);
    }
    return group;
}

function createEarthquakeObject(d) {
    // 🌍 EARTHQUAKE — concentric shockwave rings (seismic waves)
    const mag = d.magnitude || 0;
    const color = mag >= 7 ? 0xff0000 : mag >= 5 ? 0xff6600 : mag >= 3 ? 0xffd700 : 0x88ccaa;
    const size = mag >= 7 ? 0.6 : mag >= 5 ? 0.45 : mag >= 3 ? 0.3 : 0.2;
    const group = new THREE.Group();
    // Epicenter dot
    const dotGeo = new THREE.SphereGeometry(size * 0.15, 8, 8);
    const dotMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95 });
    group.add(new THREE.Mesh(dotGeo, dotMat));
    // Shockwave rings — 2 or 3 based on magnitude
    const rings = mag >= 5 ? 3 : 2;
    for (let i = 1; i <= rings; i++) {
        const r = size * 0.25 * i;
        const ringGeo = new THREE.RingGeometry(r - 0.02, r + 0.02, 24);
        const ringMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.6 / i, side: THREE.DoubleSide });
        group.add(new THREE.Mesh(ringGeo, ringMat));
    }
    return group;
}

function createGPSJammingObject(d) {
    // 📡 GPS JAMMING — hexagonal interference zone with signal disruption lines
    const intensity = d.intensity || 'low';
    const color = intensity === 'high' ? 0xff3333 : intensity === 'medium' ? 0xffd700 : 0xff8800;
    const size = intensity === 'high' ? 0.6 : 0.45;
    const group = new THREE.Group();
    // Hex zone
    const hexGeo = new THREE.CylinderGeometry(size, size, 0.03, 6);
    const hexMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.25, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(hexGeo, hexMat));
    // Hex border
    const borderGeo = new THREE.RingGeometry(size * 0.9, size, 6);
    const borderMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(borderGeo, borderMat));
    // Center jammer icon — crossed signal bars
    for (let i = 0; i < 3; i++) {
        const barGeo = new THREE.PlaneGeometry(size * 0.08, size * 0.6);
        const barMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
        const bar = new THREE.Mesh(barGeo, barMat);
        bar.rotation.z = (i * Math.PI) / 3;
        group.add(bar);
    }
    return group;
}

function createWebcamObject(d) {
    // 📹 WEBCAM — camera icon: rectangle body + circular lens + status LED
    const group = new THREE.Group();
    const size = 0.25;
    const catColor = d.category === 'maritime' ? 0x00aaff : d.category === 'aviation' ? 0x44ffaa :
                     d.category === 'military' ? 0xff3366 : d.category === 'border' ? 0xffaa00 : 0x00ddff;
    // Camera body
    const bodyGeo = new THREE.BoxGeometry(size, size * 0.65, size * 0.4);
    const bodyMat = new THREE.MeshBasicMaterial({ color: catColor, transparent: true, opacity: 0.85 });
    group.add(new THREE.Mesh(bodyGeo, bodyMat));
    // Lens circle
    const lensGeo = new THREE.RingGeometry(size * 0.12, size * 0.22, 16);
    const lensMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
    const lens = new THREE.Mesh(lensGeo, lensMat);
    lens.position.z = size * 0.21;
    group.add(lens);
    // Status LED dot
    const ledGeo = new THREE.SphereGeometry(0.03, 6, 6);
    const ledMat = new THREE.MeshBasicMaterial({ color: d.status === 'active' ? 0x00ff00 : 0xff0000 });
    const led = new THREE.Mesh(ledGeo, ledMat);
    led.position.set(size * 0.35, size * 0.25, size * 0.21);
    group.add(led);
    // Glow ring for visibility
    const glowGeo = new THREE.RingGeometry(size * 0.55, size * 0.7, 16);
    const glowMat = new THREE.MeshBasicMaterial({ color: catColor, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(glowGeo, glowMat));
    return group;
}

function createWildfireObject(d) {
    // 🔥 WILDFIRE — flame shape: tall cone + flickering glow
    const frp = d.frp || d.radiative_power || 10;
    const size = Math.min(0.2 + frp / 150, 0.7);
    const color = frp > 100 ? 0xff2200 : frp > 50 ? 0xff6600 : 0xff9900;
    const group = new THREE.Group();
    // Flame body — tall narrow cone
    const flameGeo = new THREE.ConeGeometry(size * 0.25, size * 0.8, 5);
    const flameMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const flame = new THREE.Mesh(flameGeo, flameMat);
    flame.position.y = size * 0.3;
    group.add(flame);
    // Inner bright core
    const coreGeo = new THREE.ConeGeometry(size * 0.12, size * 0.5, 5);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0xffcc00, transparent: true, opacity: 0.7 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.position.y = size * 0.2;
    group.add(core);
    // Heat glow on ground
    const heatGeo = new THREE.RingGeometry(size * 0.3, size * 0.5, 12);
    const heatMat = new THREE.MeshBasicMaterial({ color: 0xff4400, transparent: true, opacity: 0.25, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(heatGeo, heatMat));
    return group;
}

function createUnrestObject(d) {
    // ✊ UNREST — raised fist / starburst: spiky circle indicating disruption
    const count = d.event_count || d.count || 1;
    const size = Math.min(0.2 + count / 15, 0.55);
    const group = new THREE.Group();
    // Center mass
    const coreGeo = new THREE.SphereGeometry(size * 0.2, 6, 6);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0xff6600, transparent: true, opacity: 0.9 });
    group.add(new THREE.Mesh(coreGeo, coreMat));
    // Spiky rays (starburst)
    const spikes = 8;
    for (let i = 0; i < spikes; i++) {
        const spikeGeo = new THREE.PlaneGeometry(size * 0.06, size * 0.45);
        const spikeMat = new THREE.MeshBasicMaterial({ color: 0xff6600, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
        const spike = new THREE.Mesh(spikeGeo, spikeMat);
        spike.rotation.z = (i * Math.PI * 2) / spikes;
        spike.position.x = Math.cos((i * Math.PI * 2) / spikes) * size * 0.15;
        spike.position.y = Math.sin((i * Math.PI * 2) / spikes) * size * 0.15;
        group.add(spike);
    }
    return group;
}

function createInfraObject(d) {
    // 🏗️ INFRASTRUCTURE — tower shape: tall narrow rectangle + signal arcs
    const status = d.status || 'operational';
    const color = status === 'disrupted' ? 0xff3333 : status === 'degraded' ? 0xffd700 : 0x00ff66;
    const group = new THREE.Group();
    // Tower
    const towerGeo = new THREE.BoxGeometry(0.08, 0.5, 0.08);
    const towerMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85 });
    const tower = new THREE.Mesh(towerGeo, towerMat);
    tower.position.y = 0.25;
    group.add(tower);
    // Signal arcs
    for (let i = 1; i <= 2; i++) {
        const arcGeo = new THREE.RingGeometry(0.08 * i, 0.08 * i + 0.02, 16, 1, 0, Math.PI);
        const arcMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.4 / i, side: THREE.DoubleSide });
        const arc = new THREE.Mesh(arcGeo, arcMat);
        arc.position.y = 0.45;
        group.add(arc);
    }
    return group;
}

function createBaseObject(d) {
    // 🏛️ MILITARY BASE — pentagon (5-sided) with star center
    const size = 0.35;
    const group = new THREE.Group();
    // Pentagon base
    const pentGeo = new THREE.CylinderGeometry(size, size, 0.06, 5);
    const pentMat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.5 });
    group.add(new THREE.Mesh(pentGeo, pentMat));
    // Pentagon border ring
    const ringGeo = new THREE.RingGeometry(size * 0.85, size, 5);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xff00ff, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(ringGeo, ringMat));
    // Center star point
    const starGeo = new THREE.ConeGeometry(size * 0.15, size * 0.3, 5);
    const starMat = new THREE.MeshBasicMaterial({ color: 0xff44ff, transparent: true, opacity: 0.9 });
    const star = new THREE.Mesh(starGeo, starMat);
    star.position.y = 0.15;
    group.add(star);
    return group;
}

function createNuclearObject(d) {
    // ☢️ NUCLEAR — warning triangle with inner radiation symbol
    const size = 0.35;
    const group = new THREE.Group();
    // Warning triangle
    const triGeo = new THREE.ConeGeometry(size * 0.5, size * 0.6, 3);
    const triMat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.7 });
    const tri = new THREE.Mesh(triGeo, triMat);
    tri.position.y = size * 0.2;
    group.add(tri);
    // Hazard rings
    const r1Geo = new THREE.RingGeometry(size * 0.55, size * 0.65, 16);
    const r1Mat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.35, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(r1Geo, r1Mat));
    const r2Geo = new THREE.RingGeometry(size * 0.75, size * 0.85, 16);
    const r2Mat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.15, side: THREE.DoubleSide });
    group.add(new THREE.Mesh(r2Geo, r2Mat));
    return group;
}

function createNewsObject(d) {
    // 📰 NEWS — pulsing broadcast tower: vertical bar + radiating waves
    const sevColors = { critical: 0xff3333, high: 0xff6600, medium: 0xffd700, low: 0x888888 };
    const color = sevColors[d.severity] || 0xffd700;
    const size = d.severity === 'critical' ? 0.4 : d.severity === 'high' ? 0.32 : 0.22;
    const group = new THREE.Group();
    // Broadcast tower
    const towerGeo = new THREE.BoxGeometry(0.04, size * 0.7, 0.04);
    const towerMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const tower = new THREE.Mesh(towerGeo, towerMat);
    tower.position.y = size * 0.3;
    group.add(tower);
    // Signal waves (2 arcs on each side)
    for (let side = -1; side <= 1; side += 2) {
        for (let i = 1; i <= 2; i++) {
            const waveGeo = new THREE.RingGeometry(0.06 * i, 0.06 * i + 0.015, 12, 1, side > 0 ? 0 : Math.PI, Math.PI * 0.6);
            const waveMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.5 / i, side: THREE.DoubleSide });
            const wave = new THREE.Mesh(waveGeo, waveMat);
            wave.position.y = size * 0.55;
            group.add(wave);
        }
    }
    // Ground marker
    const dotGeo = new THREE.SphereGeometry(size * 0.12, 8, 8);
    const dotMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.7 });
    group.add(new THREE.Mesh(dotGeo, dotMat));
    return group;
}

function handleNewsClick(d) {
    const sevColors = { critical: '#ff3333', high: '#ff6600', medium: '#ffd700', low: '#888' };
    const color = sevColors[d.severity] || '#ffd700';
    showInfoPopup('📰 BREAKING NEWS', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.05rem;color:${color}">${d.title}</strong><br/>
        <span style="color:#888;font-size:0.75rem">${d.source} · ${d.category?.toUpperCase() || 'NEWS'} · ${d.severity?.toUpperCase() || ''}</span><br/><br/>
        ${d.description ? `<p style="color:#aaa;font-size:0.8rem">${d.description}</p>` : ''}
        ${d.published ? `<strong>TIME:</strong> ${d.published}<br/>` : ''}
        <strong>POSITION:</strong> ${d.lat?.toFixed(2)}°, ${(d.lon || d.lng)?.toFixed(2)}°<br/>
        ${d.url ? `<a href="${d.url}" target="_blank" style="color:#00ffcc;text-decoration:none">Read Full Article →</a>` : ''}
        </div>
    `);
}

// ===== NEW CLICK HANDLERS =====

function handleRadiationClick(d) {
    const sev = (d.severity || 'normal').toUpperCase();
    const col = d.severity === 'spike' ? '#ff3333' : d.severity === 'elevated' ? '#ffd700' : '#00ff66';
    showInfoPopup('☢️ RADIATION MONITOR', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.name || d.station || 'STATION'}</strong><br/><br/>
        <strong>SEVERITY:</strong> <span style="color:${col}">${sev}</span><br/>
        <strong>READING:</strong> ${d.value || d.reading || 'N/A'} ${d.unit || 'µSv/h'}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.country ? `<strong>COUNTRY:</strong> ${d.country}<br/>` : ''}
        ${d.last_updated ? `<strong>UPDATED:</strong> ${d.last_updated}<br/>` : ''}
        </div>
    `);
}

function handleEarthquakeClick(d) {
    const mag = d.magnitude || 0;
    const col = mag >= 7 ? '#ff0000' : mag >= 5 ? '#ff8c00' : '#ffd700';
    showInfoPopup('🌍 SEISMIC EVENT', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">M${mag.toFixed(1)} EARTHQUAKE</strong><br/><br/>
        <strong>LOCATION:</strong> ${d.place || d.location || 'Unknown'}<br/>
        <strong>DEPTH:</strong> ${d.depth ? d.depth + ' km' : 'N/A'}<br/>
        <strong>MAGNITUDE:</strong> <span style="color:${col}">${mag.toFixed(1)}</span><br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.time ? `<strong>TIME:</strong> ${d.time}<br/>` : ''}
        ${d.tsunami ? `<strong>⚠️ TSUNAMI WARNING</strong><br/>` : ''}
        </div>
    `);
}

function handleGPSJammingClick(d) {
    const col = d.intensity === 'high' ? '#ff3333' : '#ffd700';
    showInfoPopup('📡 GPS/EW INTERFERENCE', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.name || 'JAMMING ZONE'}</strong><br/><br/>
        <strong>INTENSITY:</strong> <span style="color:${col}">${(d.intensity || 'unknown').toUpperCase()}</span><br/>
        <strong>RADIUS:</strong> ${d.radius_km ? d.radius_km + ' km' : 'N/A'}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.source ? `<strong>SOURCE:</strong> ${d.source}<br/>` : ''}
        ${d.affected ? `<strong>AFFECTED:</strong> ${d.affected}<br/>` : ''}
        </div>
    `);
}

async function handleWebcamClick(d) {
    // Try to refresh image URLs (tokens expire after 10 min)
    let images = d.images || {};
    let player = d.player || {};
    try {
        const r = await fetch(`/api/webcam/${d.id}/refresh`);
        if (r.ok) {
            const fresh = await r.json();
            images = fresh.images || images;
            player = fresh.player || player;
        }
    } catch(e) { /* use cached */ }

    const preview = (images.current || images).preview || images.daylight_preview || '';
    const thumb = preview ? `<img class="webcam-thumb" src="${preview}" style="width:100%;max-width:380px;border:1px solid #00ddff33;margin:8px 0;border-radius:2px" alt="webcam preview"/>` : '';
    const playerUrl = (player.day || player.live || '');
    const playerEmbed = playerUrl ? `<iframe src="${playerUrl}" style="width:100%;height:220px;border:1px solid #00ddff33;margin:8px 0;border-radius:2px" allowfullscreen></iframe>` : '';
    const catColor = d.category === 'maritime' ? '#00aaff' : d.category === 'aviation' ? '#44ffaa' :
                     d.category === 'military' ? '#ff3366' : d.category === 'border' ? '#ffaa00' : '#00ddff';

    showInfoPopup('📹 WEBCAM', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${catColor}">${d.title || 'CAMERA'}</strong><br/>
        <span style="color:#888">${d.city || ''}${d.city && d.country ? ', ' : ''}${d.country || ''}</span><br/>
        <span style="color:#555;font-size:0.75rem">Region: ${d.strategic_region || 'N/A'} · Category: ${d.category || 'general'}</span><br/>
        ${thumb}
        ${playerEmbed}
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${d.lng.toFixed(4)}°<br/>
        <strong>STATUS:</strong> <span style="color:${d.status === 'active' ? '#00ff66' : '#ff3333'}">${(d.status || 'unknown').toUpperCase()}</span><br/>
        <strong>VIEWS:</strong> ${(d.view_count || 0).toLocaleString()}<br/>
        ${d.last_updated ? `<strong>LAST IMAGE:</strong> ${new Date(d.last_updated).toLocaleString()}<br/>` : ''}
        <div style="margin-top:8px;font-size:0.7rem;color:#555">⚡ Powered by Windy Webcams API · Images refresh every 5-15 min</div>
        </div>
    `);
}

function handleWildfireClick(d) {
    const frp = d.frp || d.radiative_power || 0;
    showInfoPopup('🔥 WILDFIRE', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ff6600">${d.name || 'ACTIVE FIRE'}</strong><br/><br/>
        <strong>FRP:</strong> ${frp} MW<br/>
        <strong>CONFIDENCE:</strong> ${d.confidence || 'N/A'}%<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.satellite ? `<strong>SATELLITE:</strong> ${d.satellite}<br/>` : ''}
        ${d.detected ? `<strong>DETECTED:</strong> ${d.detected}<br/>` : ''}
        </div>
    `);
}

function handleUnrestClick(d) {
    showInfoPopup('✊ CIVIL UNREST', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ff6600">${d.title || d.event_type || 'UNREST EVENT'}</strong><br/><br/>
        <strong>LOCATION:</strong> ${d.location || d.city || 'Unknown'}<br/>
        ${d.country ? `<strong>COUNTRY:</strong> ${d.country}<br/>` : ''}
        <strong>EVENTS:</strong> ${d.event_count || d.count || 1}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.description ? `<strong>DETAILS:</strong> ${d.description}<br/>` : ''}
        ${d.date ? `<strong>DATE:</strong> ${d.date}<br/>` : ''}
        </div>
    `);
}

function handleInfraClick(d) {
    const status = d.status || 'operational';
    const col = status === 'disrupted' ? '#ff3333' : status === 'degraded' ? '#ffd700' : '#00ff66';
    showInfoPopup('⚡ INFRASTRUCTURE', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.name || 'FACILITY'}</strong><br/><br/>
        <strong>TYPE:</strong> ${(d.type || 'unknown').toUpperCase()}<br/>
        <strong>STATUS:</strong> <span style="color:${col}">${status.toUpperCase()}</span><br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.description ? `<strong>DETAILS:</strong> ${d.description}<br/>` : ''}
        </div>
    `);
}

function handleBaseClick(d) {
    showInfoPopup('🏛️ MILITARY BASE', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ff00ff">${d.name || 'BASE'}</strong><br/><br/>
        ${d.country ? `<strong>COUNTRY:</strong> ${d.country}<br/>` : ''}
        ${d.branch ? `<strong>BRANCH:</strong> ${d.branch}<br/>` : ''}
        ${d.type ? `<strong>TYPE:</strong> ${d.type.toUpperCase()}<br/>` : ''}
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.description ? `<strong>NOTE:</strong> ${d.description}<br/>` : ''}
        </div>
    `);
}

function handleNuclearClick(d) {
    showInfoPopup('☢️ NUCLEAR SITE', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ffff00">${d.name || 'NUCLEAR FACILITY'}</strong><br/><br/>
        ${d.type ? `<strong>TYPE:</strong> ${d.type.toUpperCase()}<br/>` : ''}
        ${d.country ? `<strong>COUNTRY:</strong> ${d.country}<br/>` : ''}
        ${d.capacity ? `<strong>CAPACITY:</strong> ${d.capacity}<br/>` : ''}
        ${d.status ? `<strong>STATUS:</strong> ${d.status}<br/>` : ''}
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        </div>
    `);
}

// ===== CLICK HANDLERS =====

function handleVesselClick(d) {
    const spd = d.speed != null ? `${d.speed} kn` : 'N/A';
    const vtype = (d.type || 'unknown').toUpperCase();
    const zone = d.chokepoint ? d.chokepoint.replace(/_/g, ' ') : 'Open Ocean';
    const status = (d.speed || 0) < 0.5 ? '⚓ AT ANCHOR / STATIONARY' : 
                   (d.speed || 0) < 5 ? '🐌 SLOW STEAMING' : '🚢 UNDERWAY';
    const cargoMap = {
        tanker: 'Oil / LNG / LPG / Chemicals',
        cargo: 'General Cargo / Containers / Bulk',
        passenger: 'Passengers / Cruise / Ferry',
        fishing: 'Fish / Seafood',
        tug: 'Towing / Port Operations',
        military: 'Military / Naval',
        hsc: 'High Speed Craft',
    };
    const cargo = cargoMap[d.type] || 'Unclassified';
    
    showInfoPopup('VESSEL INTEL', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#00ffcc">${d.name || 'UNKNOWN'}</strong><br/>
        <span style="color:#888">MMSI: ${d.mmsi || 'N/A'}</span><br/><br/>
        <strong>TYPE:</strong> ${vtype}<br/>
        <strong>CARGO:</strong> ${cargo}<br/>
        <strong>STATUS:</strong> ${status}<br/>
        <strong>SPEED:</strong> ${spd}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        <strong>ZONE:</strong> ${zone}<br/>
        </div>
    `);
}

function handleSatelliteClick(d) {
    const cat = (d.category || 'civilian').toUpperCase();
    const colorMap = { military: '#ff3344', science: '#00ff66', navigation: '#ffd700', comms: '#00ddff' };
    const col = colorMap[d.category] || '#ffffff';

    showInfoPopup('🛰️ SATELLITE INTEL', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.name || 'UNKNOWN SAT'}</strong><br/>
        ${d.norad_id ? `<span style="color:#888">NORAD ID: ${d.norad_id}</span><br/>` : ''}<br/>
        <strong>CATEGORY:</strong> ${cat}<br/>
        <strong>ORBIT:</strong> ${d.orbit_type || 'Unknown'}<br/>
        <strong>ALTITUDE:</strong> ${d.alt_km ? d.alt_km.toLocaleString() + ' km' : 'N/A'}<br/>
        <strong>GROUND TRACK:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        ${d.description ? `<strong>NOTE:</strong> ${d.description}<br/>` : ''}
        </div>
    `);
}

function handleMilitaryClick(d) {
    const intensity = d.intensity || 1;
    const bars = '█'.repeat(Math.min(intensity, 5)) + '░'.repeat(Math.max(5 - intensity, 0));
    
    showInfoPopup('⚔️ MILITARY ACTIVITY', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ff3344">${d.event_type || 'ACTIVITY DETECTED'}</strong><br/><br/>
        <strong>REGION:</strong> ${d.region || 'Unknown'}<br/>
        <strong>INTENSITY:</strong> <span style="color:#ff3344">${bars}</span> (${intensity}/5)<br/>
        <strong>DETAILS:</strong> ${d.details || 'No further details'}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        <strong>FIRST DETECTED:</strong> ${d.first_detected || 'N/A'}<br/>
        ${d.sources ? `<strong>SOURCES:</strong> ${d.sources}<br/>` : ''}
        </div>
    `);
}

function handleAircraftClick(d) {
    const cat = (d.category || 'commercial').toUpperCase();
    const colorMap = { military: '#ff00ff', cargo: '#4488ff', helicopter: '#ffff00' };
    const col = colorMap[d.category] || '#00ddff';

    showInfoPopup('✈️ AIRCRAFT INTEL', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.callsign || 'UNKNOWN'}</strong><br/>
        ${d.aircraft_type ? `<span style="color:#888">${d.aircraft_type}</span><br/>` : ''}<br/>
        <strong>CATEGORY:</strong> ${cat}<br/>
        <strong>ALTITUDE:</strong> ${d.alt ? d.alt.toLocaleString() + ' ft' : 'N/A'}<br/>
        <strong>SPEED:</strong> ${d.speed ? d.speed + ' kts' : 'N/A'}<br/>
        <strong>HEADING:</strong> ${d.heading != null ? d.heading + '°' : 'N/A'}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        </div>
    `);
}

function handleMilitaryVesselClick(d) {
    showInfoPopup('⚔️ MILITARY VESSEL', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:#ff00ff">${d.name || 'UNKNOWN'}</strong><br/><br/>
        <strong>TYPE:</strong> ${(d.type || 'unknown').replace(/_/g, ' ').toUpperCase()}<br/>
        <strong>FLAG:</strong> ${d.flag || 'N/A'}<br/>
        <strong>POSITION:</strong> ${d.lat.toFixed(4)}°, ${(d.lon || d.lng).toFixed(4)}°<br/>
        </div>
    `);
}

function handleMarketClick(d) {
    const impact = d.impact || 0;
    const col = impact >= 0 ? '#00ff66' : '#ff3344';
    const sign = impact >= 0 ? '+' : '';
    
    showInfoPopup('📈 MARKET IMPACT', `
        <div style="font-family:monospace;font-size:0.85rem;line-height:1.6">
        <strong style="font-size:1.1rem;color:${col}">${d.event_name || 'GEO EVENT'}</strong><br/><br/>
        <strong>EVENT:</strong> ${d.event_description || 'N/A'}<br/>
        <strong>LOCATION:</strong> ${d.event_lat ? d.event_lat.toFixed(2) + '°' : '--'}, ${d.event_lng ? d.event_lng.toFixed(2) + '°' : '--'}<br/>
        <strong>MARKET:</strong> ${d.market || 'N/A'}<br/>
        <strong>IMPACT:</strong> <span style="color:${col}">${sign}${impact.toFixed(2)}%</span><br/>
        <strong>CHAIN:</strong> ${d.chain || 'Direct'}<br/>
        <strong>CONFIDENCE:</strong> ${d.confidence ? Math.round(d.confidence * 100) + '%' : 'N/A'}<br/>
        </div>
    `);
}

// ===== EVENT LISTENERS =====
function initEventListeners() {
    // City navigation
    document.querySelectorAll('.city-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const city = cities[btn.dataset.city];
            if (city) {
                stopAutoRotate();
                state.globe.pointOfView(city, 1000);
                setTimeout(() => {
                    state.autoRotate = true;
                    startAutoRotate();
                }, 3000);
            }
        });
    });
    
    // View mode toggles
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.body.className = '';
            const mode = btn.dataset.mode;
            if (mode !== 'normal') {
                document.body.classList.add(`mode-${mode}`);
            }
        });
    });
    
    // Layer toggles
    document.querySelectorAll('[id^="layer-"]').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const layer = e.target.id.replace('layer-', '');
            state.layers[layer] = e.target.checked;
            updateGlobeData();
        });
    });
    
    // Popup close
    document.getElementById('popupClose').addEventListener('click', closeInfoPopup);
    document.getElementById('infoPopup').addEventListener('click', (e) => {
        if (e.target.id === 'infoPopup') closeInfoPopup();
    });
    
    // Stop auto-rotate on user interaction
    const container = document.getElementById('globeContainer');
    container.addEventListener('mousedown', stopAutoRotate);
    container.addEventListener('touchstart', stopAutoRotate, { passive: true });
    
    // Prevent accidental zoom on double-tap (mobile)
    let lastTouchEnd = 0;
    container.addEventListener('touchend', (e) => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

// ===== KEYBOARD SHORTCUTS =====
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        switch(e.key.toLowerCase()) {
            case 'f':
                toggleFullscreen();
                break;
            case 'r':
                resetGlobeView();
                break;
            case '1':
                toggleLayer('vessels');
                break;
            case '2':
                toggleLayer('flights');
                break;
            case '3':
                toggleLayer('thermal');
                break;
            case '4':
                toggleLayer('gdelt');
                break;
            case '5':
                toggleLayer('chokepoints');
                break;
            case '6':
                toggleLayer('aircraft');
                break;
            case '7':
                toggleLayer('satellites');
                break;
            case '8':
                toggleLayer('military');
                break;
            case '9':
                toggleLayer('radiation');
                break;
            case '0':
                toggleLayer('earthquakes');
                break;
        }
    });
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function resetGlobeView() {
    state.globe.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 1000);
    state.autoRotate = true;
    startAutoRotate();
}

function toggleLayer(layer) {
    const checkbox = document.getElementById(`layer-${layer}`);
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        state.layers[layer] = checkbox.checked;
        updateGlobeData();
    }
}

// ===== INFO POPUP =====
function showInfoPopup(title, content) {
    document.getElementById('popupTitle').textContent = title;
    document.getElementById('popupContent').innerHTML = content;
    document.getElementById('infoPopup').classList.add('active');
}

function closeInfoPopup() {
    document.getElementById('infoPopup').classList.remove('active');
}

function handleGlobeClick(coords) {
    if (coords) {
        showInfoPopup('LOCATION', `
            <strong>Coordinates</strong><br/>
            Latitude: ${coords.lat.toFixed(4)}°<br/>
            Longitude: ${coords.lng.toFixed(4)}°<br/><br/>
            <em>Click markers for detailed information</em>
        `);
    }
}

// ===== AUTO-REFRESH =====
function startAutoRefresh() {
    state.refreshInterval = setInterval(() => {
        loadAllData();
    }, 30000); // 30 seconds
}

// ===== CONVERGENCE SIGNALS =====
async function loadConvergenceSignals() {
    try {
        const response = await fetch('data/convergence.json');
        const data = await response.json();
        displayConvergenceSignals(data.signals || []);
    } catch (error) {
        console.error('Error loading convergence signals:', error);
    }
}

function displayConvergenceSignals(signals) {
    const feed = document.getElementById('convergenceFeed');
    if (!feed) return;
    feed.innerHTML = '';

    if (signals.length === 0) {
        feed.innerHTML = '<div style="color:#555;font-size:0.7rem;padding:8px;">No convergence signals detected</div>';
        return;
    }

    signals.forEach(sig => {
        const card = document.createElement('div');
        const sev = sig.severity || 'low';
        card.className = `convergence-card severity-${sev}`;

        const confPct = Math.round((sig.confidence || 0) * 100);
        const assets = (sig.affected_assets || []).map(a =>
            `<span class="asset-tag">${a.replace(/_/g, ' ')}</span>`
        ).join('');

        card.innerHTML = `
            <div class="convergence-header">
                <span class="convergence-icon">${sig.icon || '⚠️'}</span>
                <span class="convergence-type ${sev}">${sig.signal_type || 'SIGNAL'}</span>
                <span class="convergence-confidence">${confPct}%</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill ${sev}" style="width:${confPct}%"></div>
            </div>
            <div class="convergence-narrative">${sig.narrative || ''}</div>
            <div class="convergence-assets">${assets}</div>
            <div class="convergence-region">📍 ${sig.region || 'Unknown'}</div>
        `;
        feed.appendChild(card);
    });
}

// Update economic indicators (static for now)
document.getElementById('balticDry').textContent = '1,247';
document.getElementById('economicLast').textContent = '2h ago';
document.getElementById('nlpSignals').textContent = '42';
