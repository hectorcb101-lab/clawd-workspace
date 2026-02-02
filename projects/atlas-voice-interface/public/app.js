/**
 * Atlas Voice Interface v0.2 - Enhanced
 * 
 * Features:
 * - Voice input/output
 * - Visual canvas with display commands
 * - Audio waveform visualization
 * - Thinking orb animation
 * - Quick commands
 * - Fullscreen mode
 * - Connection quality monitoring
 * - Persistent conversation history
 */

class AtlasInterface {
    constructor() {
        // Core elements
        this.statusDot = document.querySelector('.status-dot');
        this.statusText = document.querySelector('.status-text');
        this.canvasContent = document.getElementById('canvasContent');
        this.ambientDisplay = document.getElementById('ambientDisplay');
        this.transcript = document.getElementById('transcript');
        this.micButton = document.getElementById('micButton');
        this.voiceVisualizer = document.getElementById('voiceVisualizer');
        this.voiceHint = document.getElementById('voiceHint');
        this.audioPlayer = document.getElementById('audioPlayer');
        
        // State
        this.ws = null;
        this.recognition = null;
        this.isListening = false;
        this.isConnected = false;
        this.isSpeaking = false;
        this.isThinking = false;
        this.audioContext = null;
        this.analyser = null;
        this.mediaStream = null;
        this.lastPingTime = null;
        this.latency = 0;
        
        // Settings
        this.settings = this.loadSettings();
        
        // Initialize
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupSpeechRecognition();
        this.setupMicButton();
        this.setupKeyboardShortcuts();
        this.updateAmbientDisplay();
        this.loadConversationHistory();
        this.setupAudioVisualization();
        this.createQuickCommands();
        this.createSettingsPanel();
        
        // Update time every second
        setInterval(() => this.updateAmbientDisplay(), 1000);
        
        // Ping for latency every 10 seconds
        setInterval(() => this.measureLatency(), 10000);
        
        // Show welcome message
        setTimeout(() => this.showWelcome(), 500);
    }
    
    // === Settings ===
    
    loadSettings() {
        const defaults = {
            soundEffects: true,
            autoSpeak: true,
            saveHistory: true,
            showWaveform: true,
            darkMode: true
        };
        try {
            const saved = localStorage.getItem('atlas-settings');
            return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
        } catch {
            return defaults;
        }
    }
    
    saveSettings() {
        localStorage.setItem('atlas-settings', JSON.stringify(this.settings));
    }
    
    // === Welcome ===
    
    showWelcome() {
        const hour = new Date().getHours();
        let greeting = 'Hello';
        if (hour < 12) greeting = 'Good morning';
        else if (hour < 17) greeting = 'Good afternoon';
        else if (hour < 21) greeting = 'Good evening';
        else greeting = 'Good night';
        
        this.addSystemMessage(`${greeting}, Finn. I'm ready when you are.`);
    }
    
    addSystemMessage(text) {
        const entry = document.createElement('div');
        entry.className = 'transcript-entry system';
        entry.innerHTML = `<span class="system-icon">🏛️</span> ${text}`;
        this.transcript.appendChild(entry);
    }
    
    // === WebSocket ===
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.setStatus('connected', 'Connected');
            console.log('Connected to Atlas');
            this.measureLatency();
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.setStatus('disconnected', 'Reconnecting...');
            console.log('Disconnected from Atlas');
            setTimeout(() => this.setupWebSocket(), 3000);
        };
        
        this.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            this.setStatus('error', 'Connection error');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }
    
    measureLatency() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.lastPingTime = Date.now();
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }
    
    handleMessage(data) {
        // Handle pong for latency
        if (data.type === 'pong' && this.lastPingTime) {
            this.latency = Date.now() - this.lastPingTime;
            this.updateLatencyDisplay();
            return;
        }
        
        switch (data.type) {
            case 'welcome':
                console.log(data.message);
                break;
                
            case 'status':
                this.handleStatusUpdate(data.status);
                break;
                
            case 'response':
                this.handleResponse(data);
                break;
                
            case 'audio':
                this.playAudio(data.audio, data.format);
                break;
                
            case 'tts_fallback':
                this.speakWithBrowserTTS(data.text);
                break;
                
            case 'error':
                console.error('Server error:', data.message);
                this.setStatus('connected', 'Connected');
                this.hideThinkingOrb();
                break;
        }
    }
    
    handleStatusUpdate(status) {
        if (status === 'thinking') {
            this.isThinking = true;
            this.setStatus('thinking', 'Thinking...');
            this.showThinkingOrb();
        } else if (status === 'speaking') {
            this.isThinking = false;
            this.isSpeaking = true;
            this.setStatus('speaking', 'Speaking...');
            this.hideThinkingOrb();
        }
    }
    
    updateLatencyDisplay() {
        const el = document.getElementById('latencyDisplay');
        if (el) {
            el.textContent = `${this.latency}ms`;
            el.className = this.latency < 100 ? 'latency good' : 
                          this.latency < 300 ? 'latency ok' : 'latency slow';
        }
    }
    
    // === Thinking Orb ===
    
    showThinkingOrb() {
        let orb = document.getElementById('thinkingOrb');
        if (!orb) {
            orb = document.createElement('div');
            orb.id = 'thinkingOrb';
            orb.className = 'thinking-orb';
            orb.innerHTML = `
                <div class="orb-inner"></div>
                <div class="orb-ring"></div>
                <div class="orb-ring delay-1"></div>
                <div class="orb-ring delay-2"></div>
            `;
            this.canvasContent.appendChild(orb);
        }
        orb.classList.add('active');
        this.hideAmbient();
    }
    
    hideThinkingOrb() {
        const orb = document.getElementById('thinkingOrb');
        if (orb) {
            orb.classList.remove('active');
            setTimeout(() => orb.remove(), 500);
        }
    }
    
    handleResponse(data) {
        this.isThinking = false;
        this.hideThinkingOrb();
        
        // Add to transcript
        this.addTranscript('atlas', data.text);
        
        // Save to history
        if (this.settings.saveHistory) {
            this.saveToHistory('atlas', data.text);
        }
        
        // Handle display commands
        if (data.displays && data.displays.length > 0) {
            for (const display of data.displays) {
                this.handleDisplay(display);
            }
        }
        
        // Request TTS
        if (data.text && this.settings.autoSpeak) {
            this.requestTTS(data.text);
        }
        
        this.setStatus('connected', 'Connected');
        
        // Play subtle sound effect
        if (this.settings.soundEffects) {
            this.playSound('response');
        }
    }
    
    // === Audio Visualization ===
    
    setupAudioVisualization() {
        // Create waveform container
        const waveform = document.createElement('canvas');
        waveform.id = 'waveformCanvas';
        waveform.className = 'waveform-canvas';
        waveform.width = 200;
        waveform.height = 50;
        
        const visualizer = document.getElementById('voiceVisualizer');
        if (visualizer) {
            visualizer.innerHTML = '';
            visualizer.appendChild(waveform);
        }
    }
    
    startAudioVisualization(stream) {
        if (!this.settings.showWaveform) return;
        
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        
        this.drawWaveform();
    }
    
    drawWaveform() {
        if (!this.isListening || !this.analyser) return;
        
        const canvas = document.getElementById('waveformCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        this.analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = 'rgba(10, 10, 15, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height;
            
            // Gradient from accent to secondary
            const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
            gradient.addColorStop(0, '#60a5fa');
            gradient.addColorStop(1, '#3b82f6');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
        
        requestAnimationFrame(() => this.drawWaveform());
    }
    
    stopAudioVisualization() {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
            this.analyser = null;
        }
    }
    
    // === Quick Commands ===
    
    createQuickCommands() {
        const commands = [
            { icon: '📅', label: 'Schedule', text: "What's on my calendar today?" },
            { icon: '🌤️', label: 'Weather', text: "What's the weather like?" },
            { icon: '📧', label: 'Email', text: "Do I have any important emails?" },
            { icon: '📝', label: 'Tasks', text: "What should I focus on today?" }
        ];
        
        const container = document.createElement('div');
        container.className = 'quick-commands';
        container.id = 'quickCommands';
        
        commands.forEach(cmd => {
            const btn = document.createElement('button');
            btn.className = 'quick-command';
            btn.innerHTML = `<span class="cmd-icon">${cmd.icon}</span><span class="cmd-label">${cmd.label}</span>`;
            btn.onclick = () => this.sendMessage(cmd.text);
            container.appendChild(btn);
        });
        
        // Add after transcript
        const transcriptArea = document.getElementById('transcriptArea');
        if (transcriptArea) {
            transcriptArea.insertAdjacentElement('afterend', container);
        }
    }
    
    // === Settings Panel ===
    
    createSettingsPanel() {
        const panel = document.createElement('div');
        panel.id = 'settingsPanel';
        panel.className = 'settings-panel';
        panel.innerHTML = `
            <div class="settings-header">
                <span>Settings</span>
                <button class="settings-close" onclick="atlas.toggleSettings()">✕</button>
            </div>
            <div class="settings-content">
                <label class="setting-item">
                    <input type="checkbox" id="settingSound" ${this.settings.soundEffects ? 'checked' : ''}>
                    <span>Sound Effects</span>
                </label>
                <label class="setting-item">
                    <input type="checkbox" id="settingAutoSpeak" ${this.settings.autoSpeak ? 'checked' : ''}>
                    <span>Auto-speak Responses</span>
                </label>
                <label class="setting-item">
                    <input type="checkbox" id="settingHistory" ${this.settings.saveHistory ? 'checked' : ''}>
                    <span>Save Conversation History</span>
                </label>
                <label class="setting-item">
                    <input type="checkbox" id="settingWaveform" ${this.settings.showWaveform ? 'checked' : ''}>
                    <span>Show Audio Waveform</span>
                </label>
                <div class="settings-actions">
                    <button class="btn-secondary" onclick="atlas.clearHistory()">Clear History</button>
                    <button class="btn-primary" onclick="atlas.saveSettingsFromPanel()">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(panel);
        
        // Add settings button to header
        const header = document.querySelector('.header');
        if (header) {
            const settingsBtn = document.createElement('button');
            settingsBtn.className = 'settings-btn';
            settingsBtn.innerHTML = '⚙️';
            settingsBtn.onclick = () => this.toggleSettings();
            header.appendChild(settingsBtn);
        }
    }
    
    toggleSettings() {
        const panel = document.getElementById('settingsPanel');
        if (panel) {
            panel.classList.toggle('open');
        }
    }
    
    saveSettingsFromPanel() {
        this.settings.soundEffects = document.getElementById('settingSound').checked;
        this.settings.autoSpeak = document.getElementById('settingAutoSpeak').checked;
        this.settings.saveHistory = document.getElementById('settingHistory').checked;
        this.settings.showWaveform = document.getElementById('settingWaveform').checked;
        this.saveSettings();
        this.toggleSettings();
    }
    
    // === Sound Effects ===
    
    playSound(type) {
        // Create subtle sound effects using Web Audio API
        if (!this.settings.soundEffects) return;
        
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        
        switch (type) {
            case 'response':
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                gainNode.gain.value = 0.05;
                break;
            case 'send':
                oscillator.frequency.value = 600;
                oscillator.type = 'sine';
                gainNode.gain.value = 0.03;
                break;
            case 'listen':
                oscillator.frequency.value = 500;
                oscillator.type = 'sine';
                gainNode.gain.value = 0.04;
                break;
        }
        
        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
        oscillator.stop(ctx.currentTime + 0.2);
    }
    
    // === Conversation History ===
    
    loadConversationHistory() {
        if (!this.settings.saveHistory) return;
        
        try {
            const history = localStorage.getItem('atlas-history');
            if (history) {
                const entries = JSON.parse(history);
                // Only load last 5 entries
                const recent = entries.slice(-5);
                recent.forEach(entry => {
                    this.addTranscript(entry.speaker, entry.text, true);
                });
            }
        } catch (e) {
            console.error('Failed to load history:', e);
        }
    }
    
    saveToHistory(speaker, text) {
        try {
            const history = JSON.parse(localStorage.getItem('atlas-history') || '[]');
            history.push({ speaker, text, timestamp: Date.now() });
            // Keep only last 50 entries
            const trimmed = history.slice(-50);
            localStorage.setItem('atlas-history', JSON.stringify(trimmed));
        } catch (e) {
            console.error('Failed to save history:', e);
        }
    }
    
    clearHistory() {
        localStorage.removeItem('atlas-history');
        this.transcript.innerHTML = '';
        this.addSystemMessage('History cleared.');
        this.toggleSettings();
    }
    
    // === Display ===
    
    handleDisplay(display) {
        switch (display.type) {
            case 'clear':
                this.clearCanvas();
                break;
            case 'text':
                this.showText(display.content);
                break;
            case 'code':
                const [lang, ...codeParts] = display.content.split(':');
                this.showCode(codeParts.join(':'), lang);
                break;
            case 'list':
                const items = display.content.split('|');
                this.showList(items);
                break;
            case 'image':
                this.showImagePlaceholder(display.content);
                break;
        }
    }
    
    clearCanvas() {
        this.canvasContent.innerHTML = '';
        this.ambientDisplay = null;
    }
    
    showText(text) {
        this.hideAmbient();
        const div = document.createElement('div');
        div.className = 'display-text fade-in';
        div.textContent = text;
        this.canvasContent.appendChild(div);
    }
    
    showCode(code, language = '') {
        this.hideAmbient();
        const container = document.createElement('div');
        container.className = 'code-container fade-in';
        
        if (language) {
            const label = document.createElement('div');
            label.className = 'code-language';
            label.textContent = language;
            container.appendChild(label);
        }
        
        const pre = document.createElement('pre');
        pre.className = 'display-code';
        pre.textContent = code;
        container.appendChild(pre);
        
        this.canvasContent.appendChild(container);
    }
    
    showList(items) {
        this.hideAmbient();
        const ul = document.createElement('ul');
        ul.className = 'display-list fade-in';
        items.forEach((item, i) => {
            const li = document.createElement('li');
            li.textContent = item.trim();
            li.style.animationDelay = `${i * 0.1}s`;
            ul.appendChild(li);
        });
        this.canvasContent.appendChild(ul);
    }
    
    showImagePlaceholder(description) {
        this.hideAmbient();
        const div = document.createElement('div');
        div.className = 'image-placeholder fade-in';
        div.innerHTML = `
            <div class="image-icon">🖼️</div>
            <div class="image-desc">${description}</div>
        `;
        this.canvasContent.appendChild(div);
    }
    
    hideAmbient() {
        const ambient = document.getElementById('ambientDisplay');
        if (ambient) {
            ambient.style.display = 'none';
        }
    }
    
    showAmbient() {
        const ambient = document.getElementById('ambientDisplay');
        if (ambient) {
            ambient.style.display = 'flex';
        }
    }
    
    updateAmbientDisplay() {
        const now = new Date();
        const timeEl = document.getElementById('timeDisplay');
        const dateEl = document.getElementById('dateDisplay');
        const greetingEl = document.getElementById('greetingDisplay');
        
        if (timeEl) {
            const hours = now.getHours().toString().padStart(2, '0');
            const mins = now.getMinutes().toString().padStart(2, '0');
            timeEl.textContent = `${hours}:${mins}`;
        }
        
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('en-GB', {
                weekday: 'long',
                day: 'numeric',
                month: 'long'
            });
        }
        
        if (greetingEl) {
            const hour = now.getHours();
            let greeting = 'Hello';
            if (hour < 12) greeting = 'Good morning';
            else if (hour < 17) greeting = 'Good afternoon';
            else if (hour < 21) greeting = 'Good evening';
            else greeting = 'Good night';
            greetingEl.textContent = `${greeting}, Finn`;
        }
    }
    
    // === Transcript ===
    
    addTranscript(speaker, text, isHistory = false) {
        const entry = document.createElement('div');
        entry.className = `transcript-entry ${speaker}${isHistory ? ' from-history' : ' fade-in'}`;
        entry.textContent = text;
        this.transcript.appendChild(entry);
        this.transcript.scrollTop = this.transcript.scrollHeight;
        
        // Keep only last 15 entries in view
        while (this.transcript.children.length > 15) {
            this.transcript.removeChild(this.transcript.firstChild);
        }
        
        // Save to history
        if (!isHistory && this.settings.saveHistory) {
            this.saveToHistory(speaker, text);
        }
    }
    
    // === Speech Recognition ===
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported');
            this.voiceHint.textContent = 'Voice not supported';
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-GB';
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.setStatus('listening', 'Listening...');
            this.micButton.classList.add('listening');
            document.getElementById('voiceVisualizer').classList.add('active');
            this.voiceHint.textContent = 'Listening...';
            
            if (this.settings.soundEffects) {
                this.playSound('listen');
            }
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.micButton.classList.remove('listening');
            document.getElementById('voiceVisualizer').classList.remove('active');
            this.voiceHint.textContent = 'Hold to speak';
            this.stopAudioVisualization();
            
            if (this.isConnected) {
                this.setStatus('connected', 'Connected');
            }
        };
        
        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Show interim results
            if (interimTranscript) {
                this.voiceHint.textContent = interimTranscript;
            }
            
            if (finalTranscript) {
                this.sendMessage(finalTranscript);
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.micButton.classList.remove('listening');
            document.getElementById('voiceVisualizer').classList.remove('active');
            
            if (event.error === 'not-allowed') {
                this.voiceHint.textContent = 'Microphone access denied';
            } else {
                this.voiceHint.textContent = 'Try again';
                setTimeout(() => {
                    this.voiceHint.textContent = 'Hold to speak';
                }, 2000);
            }
        };
    }
    
    setupMicButton() {
        // Hold to speak
        this.micButton.addEventListener('mousedown', () => this.startListening());
        this.micButton.addEventListener('mouseup', () => this.stopListening());
        this.micButton.addEventListener('mouseleave', () => {
            if (this.isListening) this.stopListening();
        });
        
        // Touch support
        this.micButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startListening();
        });
        this.micButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopListening();
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Space: hold to speak
            if (e.code === 'Space' && !e.repeat && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                this.startListening();
            }
            
            // Escape: stop/cancel
            if (e.code === 'Escape') {
                if (this.isListening) this.stopListening();
                this.toggleSettings(false);
            }
            
            // F11: fullscreen
            if (e.code === 'F11') {
                e.preventDefault();
                this.toggleFullscreen();
            }
            
            // Ctrl+H: toggle history
            if (e.ctrlKey && e.code === 'KeyH') {
                e.preventDefault();
                this.showAmbient();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.stopListening();
            }
        });
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    async startListening() {
        if (this.recognition && !this.isListening) {
            try {
                // Get microphone stream for visualization
                this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.startAudioVisualization(this.mediaStream);
                this.recognition.start();
            } catch (e) {
                console.error('Could not start recognition:', e);
            }
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        this.stopAudioVisualization();
    }
    
    // === Communication ===
    
    sendMessage(text) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('Not connected');
            return;
        }
        
        this.addTranscript('user', text);
        
        if (this.settings.soundEffects) {
            this.playSound('send');
        }
        
        this.ws.send(JSON.stringify({
            type: 'chat',
            text: text
        }));
    }
    
    requestTTS(text) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
        
        this.ws.send(JSON.stringify({
            type: 'tts',
            text: text
        }));
    }
    
    playAudio(base64Audio, format) {
        this.isSpeaking = true;
        const audioData = `data:audio/${format};base64,${base64Audio}`;
        this.audioPlayer.src = audioData;
        this.audioPlayer.play().catch(err => {
            console.error('Audio playback error:', err);
            this.isSpeaking = false;
        });
        
        this.audioPlayer.onended = () => {
            this.isSpeaking = false;
            this.setStatus('connected', 'Connected');
        };
    }
    
    speakWithBrowserTTS(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-GB';
            utterance.rate = 1.1;
            utterance.pitch = 0.95;
            
            const voices = speechSynthesis.getVoices();
            const britishVoice = voices.find(v => v.lang.includes('en-GB') && v.name.includes('Male')) ||
                                 voices.find(v => v.lang.includes('en-GB')) ||
                                 voices[0];
            if (britishVoice) utterance.voice = britishVoice;
            
            utterance.onend = () => {
                this.isSpeaking = false;
                this.setStatus('connected', 'Connected');
            };
            
            this.isSpeaking = true;
            speechSynthesis.speak(utterance);
        }
    }
    
    // === Status ===
    
    setStatus(status, text) {
        this.statusDot.className = 'status-dot ' + status;
        this.statusText.textContent = text;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.atlas = new AtlasInterface();
    
    // Register service worker for offline support
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.error('SW registration failed:', err));
    }
});
