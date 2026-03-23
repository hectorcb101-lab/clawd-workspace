// ===== GLOBAL STATE =====
const state = {
    globe: null,
    data: {
        vessels: [],
        flights: [],
        thermal: [],
        gdelt: [],
        alerts: []
    },
    layers: {
        vessels: true,
        flights: true,
        thermal: true,
        gdelt: true,
        chokepoints: true
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
    washington: { lat: 38.9072, lng: -77.0369, alt: 1.5 }
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
    initClock();
    initGlobe();
    initEventListeners();
    initKeyboardShortcuts();
    loadAllData();
    startAutoRefresh();
});

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
        .globeImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/earth-dark.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe@2.27.2/example/img/night-sky.png')
        .pointOfView({ lat: 20, lng: 0, altitude: 2.5 })
        .showAtmosphere(true)
        .atmosphereColor('#00ffcc')
        .atmosphereAltitude(0.15)
        .onGlobeClick(handleGlobeClick);

    // Auto-rotate
    startAutoRotate();
    
    // Update coordinates on move
    state.globe.controls().addEventListener('change', updateCoordinates);
    
    // Responsive resize with debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            state.globe.width(container.clientWidth);
            state.globe.height(container.clientHeight);
        }, 250);
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
            loadAlerts()
        ]);
        updateGlobeData();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function loadVesselData() {
    try {
        const response = await fetch('data/vessel_status.json');
        const data = await response.json();
        state.data.vessels = data.vessels || [];
        
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
    
    // Pause auto-scroll on hover
    feed.addEventListener('mouseenter', () => {
        feed.style.overflowY = 'hidden';
    });
    feed.addEventListener('mouseleave', () => {
        feed.style.overflowY = 'auto';
    });
}

// ===== GLOBE DATA UPDATE =====
function updateGlobeData() {
    // Points for vessels (cyan dots)
    if (state.layers.vessels) {
        state.globe
            .pointsData(state.data.vessels)
            .pointLat('lat')
            .pointLng('lng')
            .pointColor(() => '#00ffcc')
            .pointAltitude(0.01)
            .pointRadius(0.15)
            .pointLabel(d => `🚢 ${d.name}<br/>Type: ${d.type}<br/>Speed: ${d.speed} kn`);
    } else {
        state.globe.pointsData([]);
    }
    
    // Arcs for flight paths (amber lines)
    if (state.layers.flights) {
        const arcs = state.data.flights.map(f => ({
            startLat: f.origin.lat,
            startLng: f.origin.lng,
            endLat: f.destination.lat,
            endLng: f.destination.lng,
            color: '#ffd700'
        }));
        
        state.globe
            .arcsData(arcs)
            .arcColor('color')
            .arcStroke(0.5)
            .arcDashLength(0.4)
            .arcDashGap(0.2)
            .arcDashAnimateTime(3000);
    } else {
        state.globe.arcsData([]);
    }
    
    // Rings for thermal hotspots (pulsing red)
    if (state.layers.thermal) {
        state.globe
            .ringsData(state.data.thermal)
            .ringLat('lat')
            .ringLng('lng')
            .ringColor(() => '#ff3333')
            .ringMaxRadius(2)
            .ringPropagationSpeed(2)
            .ringRepeatPeriod(1500);
    } else {
        state.globe.ringsData([]);
    }
    
    // HTML elements for GDELT events (sized markers)
    if (state.layers.gdelt) {
        state.globe
            .htmlElementsData(state.data.gdelt)
            .htmlLat('lat')
            .htmlLng('lng')
            .htmlAltitude(0.01)
            .htmlElement(d => {
                const el = document.createElement('div');
                const size = Math.max(4, d.significance * 8);
                el.style.width = `${size}px`;
                el.style.height = `${size}px`;
                el.style.borderRadius = '50%';
                el.style.background = 'rgba(255, 255, 255, 0.8)';
                el.style.border = '1px solid #00ffcc';
                el.style.boxShadow = '0 0 10px rgba(0, 255, 204, 0.6)';
                el.style.cursor = 'pointer';
                el.title = d.title;
                el.addEventListener('click', (e) => {
                    e.stopPropagation();
                    showInfoPopup('GDELT EVENT', `
                        <strong>${d.title}</strong><br/>
                        <em>Location: ${d.location}</em><br/><br/>
                        Significance: ${(d.significance * 10).toFixed(1)}/10<br/>
                        Tone: ${d.tone}<br/>
                        Time: ${d.timestamp}
                    `);
                });
                return el;
            });
    } else {
        state.globe.htmlElementsData([]);
    }
    
    // Polygons for chokepoint regions (dashed borders)
    if (state.layers.chokepoints) {
        const polygons = chokepoints.map(cp => {
            const points = [];
            const segments = 32;
            for (let i = 0; i <= segments; i++) {
                const angle = (i / segments) * 2 * Math.PI;
                points.push([
                    cp.lng + cp.radius * Math.cos(angle),
                    cp.lat + cp.radius * Math.sin(angle)
                ]);
            }
            return {
                name: cp.name,
                geometry: {
                    type: 'Polygon',
                    coordinates: [points]
                }
            };
        });
        
        state.globe
            .polygonsData(polygons)
            .polygonCapColor(() => 'rgba(255, 215, 0, 0.05)')
            .polygonSideColor(() => 'rgba(255, 215, 0, 0.1)')
            .polygonStrokeColor(() => '#ffd700')
            .polygonAltitude(0.01)
            .polygonLabel(d => `⚠️ ${d.name}`);
    } else {
        state.globe.polygonsData([]);
    }
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
    container.addEventListener('touchstart', stopAutoRotate);
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

// Update economic indicators (static for now)
document.getElementById('balticDry').textContent = '1,247';
document.getElementById('economicLast').textContent = '2h ago';
document.getElementById('nlpSignals').textContent = '42';
