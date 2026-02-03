/**
 * Atlas Voice Interface - Server v0.3
 * 
 * Routes voice/text through Clawdbot Gateway for full Atlas context.
 * 
 * v0.3 Changes:
 * - Added message queue per connection (prevents race conditions)
 * - Sequential processing of chat messages
 * - Better error handling and state management
 */

require('dotenv').config();
const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const OpenAI = require('openai');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Initialize OpenAI client for TTS
const openai = new OpenAI();

const PORT = process.env.PORT || 3000;

// Clawdbot Gateway configuration
const GATEWAY_URL = process.env.GATEWAY_URL || 'http://127.0.0.1:18789';
const GATEWAY_TOKEN = process.env.GATEWAY_TOKEN || '97a3b1b511a483c973057781c87737155c4f731ab5a801a7';

// Voice interface system prompt addition
const VOICE_CONTEXT = `
## Voice Interface Mode

You are speaking through a voice + visual interface. Adjust your responses:

- Keep responses conversational and concise (this is speech, not text)
- Use natural spoken language, avoid markdown formatting
- You can display things on the canvas using special tags:
  - [DISPLAY:text:content] — show text on canvas
  - [DISPLAY:code:language:content] — show code
  - [DISPLAY:list:item1|item2|item3] — show a list
  - [CLEAR] — clear the canvas
- Be warm, witty, present — JARVIS energy
- Finn can see you and hear you now. This is more personal than text chat.
`;

// Parse display commands from response
function parseDisplayCommands(text) {
    const displays = [];
    let cleanText = text;
    
    // Parse [DISPLAY:type:content] commands
    const displayRegex = /\[DISPLAY:(\w+):([^\]]+)\]/g;
    let match;
    
    while ((match = displayRegex.exec(text)) !== null) {
        const [fullMatch, type, content] = match;
        displays.push({ type, content });
        cleanText = cleanText.replace(fullMatch, '');
    }
    
    // Parse [CLEAR] command
    if (text.includes('[CLEAR]')) {
        displays.unshift({ type: 'clear', content: '' });
        cleanText = cleanText.replace(/\[CLEAR\]/g, '');
    }
    
    return {
        text: cleanText.trim(),
        displays
    };
}

// Call Clawdbot Gateway
async function callGateway(messages, sessionId) {
    const response = await fetch(`${GATEWAY_URL}/v1/chat/completions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${GATEWAY_TOKEN}`,
            'x-clawdbot-agent-id': 'main'
        },
        body: JSON.stringify({
            model: 'clawdbot:main',
            messages: [
                { role: 'system', content: VOICE_CONTEXT },
                ...messages
            ],
            user: `voice-interface-${sessionId}`
        })
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Gateway error: ${response.status} - ${error}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// Connection state management
class ConnectionState {
    constructor(id, ws) {
        this.id = id;
        this.ws = ws;
        this.history = [];
        this.queue = [];
        this.processing = false;
    }
    
    addToHistory(role, content) {
        this.history.push({ role, content });
        // Keep last 20 messages for context
        if (this.history.length > 20) {
            this.history.splice(0, this.history.length - 20);
        }
    }
    
    async processQueue() {
        if (this.processing || this.queue.length === 0) return;
        
        this.processing = true;
        
        while (this.queue.length > 0) {
            const message = this.queue.shift();
            
            // Check if connection is still open
            if (this.ws.readyState !== 1) { // WebSocket.OPEN = 1
                console.log(`[${this.id}] Connection closed, clearing queue`);
                this.queue = [];
                break;
            }
            
            try {
                await this.handleChatMessage(message);
            } catch (err) {
                console.error(`[${this.id}] Queue processing error:`, err);
            }
        }
        
        this.processing = false;
    }
    
    async handleChatMessage(text) {
        console.log(`[${this.id}] Processing: ${text}`);
        
        // Add to history
        this.addToHistory('user', text);
        
        // Notify client we're thinking
        this.send({ type: 'status', status: 'thinking' });
        
        try {
            const assistantMessage = await callGateway(this.history, this.id);
            this.addToHistory('assistant', assistantMessage);
            
            // Parse display commands
            const parsed = parseDisplayCommands(assistantMessage);
            
            console.log(`[${this.id}] Response: ${parsed.text.substring(0, 100)}...`);
            
            // Send response
            this.send({
                type: 'response',
                text: parsed.text,
                displays: parsed.displays
            });
        } catch (err) {
            console.error(`[${this.id}] Gateway error:`, err);
            this.send({
                type: 'response',
                text: "I'm having trouble connecting to my brain right now. Give me a moment.",
                displays: []
            });
        }
    }
    
    async handleTTS(text) {
        this.send({ type: 'status', status: 'speaking' });
        
        try {
            const audio = await openai.audio.speech.create({
                model: 'tts-1',
                voice: 'echo',
                input: text,
                speed: 1.15
            });
            
            const buffer = Buffer.from(await audio.arrayBuffer());
            const base64 = buffer.toString('base64');
            
            this.send({
                type: 'audio',
                audio: base64,
                format: 'mp3'
            });
        } catch (err) {
            console.error(`[${this.id}] TTS error:`, err);
            this.send({ 
                type: 'tts_fallback',
                text: text 
            });
        }
    }
    
    send(data) {
        if (this.ws.readyState === 1) { // WebSocket.OPEN
            this.ws.send(JSON.stringify(data));
        }
    }
    
    enqueueChat(text) {
        this.queue.push(text);
        // Notify client that message is queued if already processing
        if (this.processing) {
            this.send({ type: 'queued', position: this.queue.length });
        }
        this.processQueue();
    }
}

// Active connections
const connections = new Map();

// Handle WebSocket connections
wss.on('connection', (ws) => {
    const connectionId = Date.now().toString();
    const state = new ConnectionState(connectionId, ws);
    connections.set(connectionId, state);
    
    console.log(`[${connectionId}] Client connected`);
    
    ws.on('message', async (data) => {
        try {
            const message = JSON.parse(data);
            
            // Handle ping for latency measurement
            if (message.type === 'ping') {
                state.send({ type: 'pong' });
                return;
            }
            
            if (message.type === 'chat') {
                console.log(`[${connectionId}] User: ${message.text}`);
                state.enqueueChat(message.text);
            }
            
            if (message.type === 'tts') {
                await state.handleTTS(message.text);
            }
        } catch (err) {
            console.error('Message error:', err);
            state.send({ type: 'error', message: err.message });
        }
    });
    
    ws.on('close', (code, reason) => {
        console.log(`[${connectionId}] Client disconnected, code: ${code}, reason: ${reason?.toString() || 'none'}`);
        connections.delete(connectionId);
    });
    
    ws.on('error', (err) => {
        console.error(`[${connectionId}] WebSocket error:`, err.message);
    });
    
    // Send welcome
    state.send({
        type: 'welcome',
        message: 'Connected to Atlas'
    });
});

// Serve static files
app.use(express.static('public'));

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        name: 'Atlas Voice Interface',
        version: '0.3',
        gateway: GATEWAY_URL,
        connections: connections.size
    });
});

// Start server
server.listen(PORT, () => {
    console.log(`
🏛️  Atlas Voice Interface v0.3
   http://localhost:${PORT}
   
   Routing through Clawdbot Gateway: ${GATEWAY_URL}
   
   Changes in v0.3:
   - Message queue per connection
   - Sequential processing (no more race conditions)
   - Better state management
   
   Voice + Visual interface ready.
   Open in Chrome for best experience.
`);
});
