# 🏛️ Atlas Voice Interface v0.2

**Voice + Visual interface for Atlas AI**

*Talk to me. I talk back.*

---

## ✨ What's New in v0.2

- **Thinking Orb** — Beautiful pulsing animation when processing
- **Particle Background** — Subtle floating particles with mouse interaction
- **Quick Commands** — One-tap access to common requests
- **Settings Panel** — Customize sound, history, waveform display
- **Conversation History** — Persists across sessions (localStorage)
- **Audio Waveform** — Real-time mic visualization when speaking
- **Latency Monitor** — See connection quality in real-time
- **PWA Support** — Install as an app on mobile/desktop
- **Keyboard Shortcuts** — Space to talk, F11 for fullscreen
- **Service Worker** — Faster loads, offline fallback

---

## 🚀 Quick Start

### Access URL

```
https://trim-navigation-oriental-chicago.trycloudflare.com
```

Open in **Chrome** for best voice recognition support.

### Or run locally

```bash
cd ~/clawd/projects/atlas-voice-interface
./start-with-tunnel.sh
```

---

## 🎮 How to Use

| Action | How |
|--------|-----|
| **Speak** | Hold mic button or **spacebar** |
| **Stop** | Release the button |
| **Fullscreen** | Press **F11** |
| **Settings** | Click ⚙️ in header |
| **Quick Commands** | Tap the preset buttons |

---

## 🎛️ Settings

- **Sound Effects** — Subtle audio cues for actions
- **Auto-speak Responses** — TTS for Atlas replies
- **Save History** — Remember conversations
- **Show Waveform** — Visual mic feedback

---

## 🔊 Voice

- **Input**: Web Speech API (Chrome recommended)
- **Output**: OpenAI TTS (echo voice, 1.15x speed)
- **Fallback**: Browser speech synthesis if TTS fails

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your Browser                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐     │
│  │   Voice    │  │   Canvas   │  │  Particles │     │
│  │   Input    │  │  Display   │  │ Background │     │
│  └─────┬──────┘  └─────▲──────┘  └────────────┘     │
│        │               │                             │
│        └───────────────┼──────────────────┐         │
│                        │                  │         │
│  WebSocket ←───────────┴──────────→ TTS Audio       │
│                                                      │
└──────────────────────────┬───────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Express   │
                    │   Server    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Clawdbot   │
                    │   Gateway   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Claude API │
                    │ (Full Atlas │
                    │   Context)  │
                    └─────────────┘
```

---

## 🛠️ Files

```
atlas-voice-interface/
├── server.js          # Node.js backend
├── public/
│   ├── index.html     # Main interface
│   ├── app.js         # Frontend logic (30KB)
│   ├── styles.css     # JARVIS-inspired styling
│   ├── particles.js   # Background effect
│   ├── sw.js          # Service worker
│   ├── manifest.json  # PWA manifest
│   └── favicon.svg    # Atlas icon
├── start.sh           # Start server
├── start-with-tunnel.sh  # Start with public URL
├── stop.sh            # Stop server
└── logs/              # Server & tunnel logs
```

---

## 🔮 Coming Next

- [ ] Wake word detection ("Atlas")
- [ ] Image generation on canvas
- [ ] Diagram drawing
- [ ] Memory visualization
- [ ] Calendar integration
- [ ] Weather widget
- [ ] ElevenLabs voice options
- [ ] Multi-room audio

---

## 🎯 The Vision

This is the bridge.

**Text** → **Voice+Visual** → **Glass Panel** → **Holograms**

One step at a time toward JARVIS.

---

*Built with 🏛️ by Atlas*
*v0.2 — 2026-02-02*
