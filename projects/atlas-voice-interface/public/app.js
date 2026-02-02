/**
 * Atlas Voice Interface - Frontend
 * 
 * Handles voice input, WebSocket communication, and display.
 */

class AtlasInterface {
    constructor() {
        // Elements
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
        
        // Initialize
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupSpeechRecognition();
        this.setupMicButton();
        this.updateAmbientDisplay();
        
        // Update time every second
        setInterval(() => this.updateAmbientDisplay(), 1000);
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
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.setStatus('disconnected', 'Disconnected');
            console.log('Disconnected from Atlas');
            
            // Reconnect after 3 seconds
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
    
    handleMessage(data) {
        switch (data.type) {
            case 'welcome':
                console.log(data.message);
                break;
                
            case 'status':
                if (data.status === 'thinking') {
                    this.setStatus('thinking', 'Thinking...');
                } else if (data.status === 'speaking') {
                    this.setStatus('speaking', 'Speaking...');
                }
                break;
                
            case 'response':
                this.handleResponse(data);
                break;
                
            case 'audio':
                this.playAudio(data.audio, data.format);
                break;
                
            case 'tts_fallback':
                // Use browser's built-in speech synthesis
                this.speakWithBrowserTTS(data.text);
                break;
                
            case 'error':
                console.error('Server error:', data.message);
                this.setStatus('connected', 'Connected');
                break;
        }
    }
    
    speakWithBrowserTTS(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-GB';
            utterance.rate = 1.1;
            utterance.pitch = 0.9;
            
            // Try to find a nice British voice
            const voices = speechSynthesis.getVoices();
            const britishVoice = voices.find(v => v.lang.includes('en-GB')) || voices[0];
            if (britishVoice) utterance.voice = britishVoice;
            
            utterance.onend = () => this.setStatus('connected', 'Connected');
            speechSynthesis.speak(utterance);
        }
    }
    
    handleResponse(data) {
        // Add to transcript
        this.addTranscript('atlas', data.text);
        
        // Handle display commands
        if (data.displays && data.displays.length > 0) {
            for (const display of data.displays) {
                this.handleDisplay(display);
            }
        }
        
        // Request TTS
        if (data.text) {
            this.requestTTS(data.text);
        }
        
        this.setStatus('connected', 'Connected');
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
        div.className = 'display-text';
        div.textContent = text;
        this.canvasContent.appendChild(div);
    }
    
    showCode(code, language = '') {
        this.hideAmbient();
        const pre = document.createElement('pre');
        pre.className = 'display-code';
        pre.textContent = code;
        if (language) {
            pre.dataset.language = language;
        }
        this.canvasContent.appendChild(pre);
    }
    
    showList(items) {
        this.hideAmbient();
        const ul = document.createElement('ul');
        ul.className = 'display-list';
        for (const item of items) {
            const li = document.createElement('li');
            li.textContent = item.trim();
            ul.appendChild(li);
        }
        this.canvasContent.appendChild(ul);
    }
    
    showImagePlaceholder(description) {
        this.hideAmbient();
        const div = document.createElement('div');
        div.className = 'display-text';
        div.style.fontStyle = 'italic';
        div.style.color = 'var(--text-muted)';
        div.textContent = `[Image: ${description}]`;
        this.canvasContent.appendChild(div);
    }
    
    hideAmbient() {
        if (this.ambientDisplay) {
            this.ambientDisplay.style.display = 'none';
        }
    }
    
    updateAmbientDisplay() {
        const now = new Date();
        const timeEl = document.getElementById('timeDisplay');
        const dateEl = document.getElementById('dateDisplay');
        const greetingEl = document.getElementById('greetingDisplay');
        
        if (timeEl) {
            timeEl.textContent = now.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
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
            else greeting = 'Good evening';
            greetingEl.textContent = `${greeting}, Finn`;
        }
    }
    
    // === Transcript ===
    
    addTranscript(speaker, text) {
        const entry = document.createElement('div');
        entry.className = `transcript-entry ${speaker}`;
        entry.textContent = text;
        this.transcript.appendChild(entry);
        this.transcript.scrollTop = this.transcript.scrollHeight;
        
        // Keep only last 10 entries
        while (this.transcript.children.length > 10) {
            this.transcript.removeChild(this.transcript.firstChild);
        }
    }
    
    // === Voice Recognition ===
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported');
            this.voiceHint.textContent = 'Voice not supported in this browser';
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
            this.voiceVisualizer.classList.add('active');
            this.voiceHint.textContent = 'Listening...';
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.micButton.classList.remove('listening');
            this.voiceVisualizer.classList.remove('active');
            this.voiceHint.textContent = 'Hold to speak';
            
            if (this.isConnected) {
                this.setStatus('connected', 'Connected');
            }
        };
        
        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            
            if (finalTranscript) {
                this.sendMessage(finalTranscript);
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.micButton.classList.remove('listening');
            this.voiceVisualizer.classList.remove('active');
            
            if (event.error === 'not-allowed') {
                this.voiceHint.textContent = 'Microphone access denied';
            } else {
                this.voiceHint.textContent = 'Hold to speak';
            }
        };
    }
    
    setupMicButton() {
        // Hold to speak
        this.micButton.addEventListener('mousedown', () => this.startListening());
        this.micButton.addEventListener('mouseup', () => this.stopListening());
        this.micButton.addEventListener('mouseleave', () => this.stopListening());
        
        // Touch support
        this.micButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startListening();
        });
        this.micButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopListening();
        });
        
        // Keyboard: hold space
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !e.repeat && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                this.startListening();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.stopListening();
            }
        });
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            try {
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
    }
    
    // === Communication ===
    
    sendMessage(text) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('Not connected');
            return;
        }
        
        this.addTranscript('user', text);
        
        this.ws.send(JSON.stringify({
            type: 'chat',
            text: text
        }));
    }
    
    requestTTS(text) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        this.ws.send(JSON.stringify({
            type: 'tts',
            text: text
        }));
    }
    
    playAudio(base64Audio, format) {
        const audioData = `data:audio/${format};base64,${base64Audio}`;
        this.audioPlayer.src = audioData;
        this.audioPlayer.play().catch(err => {
            console.error('Audio playback error:', err);
        });
        
        this.audioPlayer.onended = () => {
            this.setStatus('connected', 'Connected');
        };
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
});
