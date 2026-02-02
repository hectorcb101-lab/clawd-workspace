/**
 * Atlas Voice Interface - Server
 * 
 * Routes voice/text through Clawdbot Gateway for full Atlas context.
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

// Conversation history per connection
const conversations = new Map();

// Handle WebSocket connections
wss.on('connection', (ws) => {
    const connectionId = Date.now().toString();
    conversations.set(connectionId, []);
    
    console.log(`[${connectionId}] Client connected`);
    
    ws.on('message', async (data) => {
        try {
            const message = JSON.parse(data);
            
            if (message.type === 'chat') {
                console.log(`[${connectionId}] User: ${message.text}`);
                
                // Add to conversation history
                const history = conversations.get(connectionId);
                history.push({ role: 'user', content: message.text });
                
                // Keep last 20 messages for context
                if (history.length > 20) {
                    history.splice(0, history.length - 20);
                }
                
                // Send to Clawdbot Gateway
                ws.send(JSON.stringify({ type: 'status', status: 'thinking' }));
                
                try {
                    const assistantMessage = await callGateway(history, connectionId);
                    history.push({ role: 'assistant', content: assistantMessage });
                    
                    // Parse display commands
                    const parsed = parseDisplayCommands(assistantMessage);
                    
                    console.log(`[${connectionId}] Atlas: ${parsed.text.substring(0, 100)}...`);
                    
                    // Send response
                    ws.send(JSON.stringify({
                        type: 'response',
                        text: parsed.text,
                        displays: parsed.displays
                    }));
                } catch (err) {
                    console.error('Gateway error:', err);
                    ws.send(JSON.stringify({
                        type: 'response',
                        text: "I'm having trouble connecting to my brain right now. Give me a moment.",
                        displays: []
                    }));
                }
            }
            
            if (message.type === 'tts') {
                // Generate TTS audio
                ws.send(JSON.stringify({ type: 'status', status: 'speaking' }));
                
                try {
                    const audio = await openai.audio.speech.create({
                        model: 'tts-1',
                        voice: 'echo',  // Warm, conversational
                        input: message.text,
                        speed: 1.15
                    });
                    
                    const buffer = Buffer.from(await audio.arrayBuffer());
                    const base64 = buffer.toString('base64');
                    
                    ws.send(JSON.stringify({
                        type: 'audio',
                        audio: base64,
                        format: 'mp3'
                    }));
                } catch (err) {
                    console.error('TTS error:', err);
                    // Fall back to browser TTS
                    ws.send(JSON.stringify({ 
                        type: 'tts_fallback',
                        text: message.text 
                    }));
                }
            }
        } catch (err) {
            console.error('Message error:', err);
            ws.send(JSON.stringify({ type: 'error', message: err.message }));
        }
    });
    
    ws.on('close', () => {
        console.log(`[${connectionId}] Client disconnected`);
        conversations.delete(connectionId);
    });
    
    // Send welcome
    ws.send(JSON.stringify({
        type: 'welcome',
        message: 'Connected to Atlas'
    }));
});

// Serve static files
app.use(express.static('public'));

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', name: 'Atlas Voice Interface', gateway: GATEWAY_URL });
});

// Start server
server.listen(PORT, () => {
    console.log(`
🏛️  Atlas Voice Interface v0.1
   http://localhost:${PORT}
   
   Routing through Clawdbot Gateway: ${GATEWAY_URL}
   
   Voice + Visual interface ready.
   Open in Chrome for best experience.
`);
});
