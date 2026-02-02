# 🏛️ Atlas Voice Interface

**Voice + Visual interface for Atlas**

Talk to me instead of typing. I talk back.

---

## Quick Start

### 1. Access from your laptop

Since I'm running on the VPS, use SSH tunneling:

```bash
ssh -L 3000:localhost:3000 ubuntu@<vps-ip>
```

Then open: **http://localhost:3000**

### 2. Or start locally (if you're on the VPS)

```bash
cd ~/clawd/projects/atlas-voice-interface
./start.sh
```

---

## How to Use

1. **Open in Chrome** (best voice recognition support)
2. **Hold the microphone button** (or hold spacebar) and speak
3. **Release when done** — I'll process and respond
4. Watch the **canvas** for visual content I display
5. Listen as I speak my response

---

## Features

### Voice Input
- Hold mic button or spacebar to speak
- Release to send
- Uses Web Speech API (Chrome recommended)

### Voice Output
- I speak my responses using OpenAI TTS
- Falls back to browser TTS if needed
- Echo voice at 1.15x speed — warm, JARVIS-like

### Visual Canvas
- I can display text, code, lists on the canvas
- Shows ambient info (time, date, greeting) when idle
- Clears when new content arrives

### Status Indicators
- 🟢 Connected — Ready
- 🔵 Thinking — Processing your message
- 🟡 Speaking — Playing audio response
- 🟠 Listening — Recording your voice

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space (hold) | Push to talk |

---

## Troubleshooting

### Microphone not working
- Allow microphone access when prompted
- Use Chrome for best compatibility
- Check if another app is using the mic

### No audio output
- Check volume
- Allow audio autoplay in browser
- If API TTS fails, browser TTS will be used

### Connection failed
- Make sure Clawdbot gateway is running: `clawdbot status`
- Check SSH tunnel is active
- View logs: `tail -f logs/server.log`

---

## Architecture

```
Your Browser (laptop)
       ↓
    WebSocket
       ↓
Voice Interface Server (VPS:3000)
       ↓
Clawdbot Gateway (VPS:18789)
       ↓
    Claude API
```

This means you get full Atlas context — SOUL.md, memory, everything.

---

## What's Next

- [ ] Wake word detection ("Atlas")
- [ ] Better TTS voices (ElevenLabs)
- [ ] Image generation on canvas
- [ ] Diagram drawing
- [ ] Memory visualization
- [ ] Mobile/tablet optimization
- [ ] Kiosk mode for mounted display

---

*Built with 🏛️ by Atlas, 2026-02-02*
