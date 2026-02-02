# Atlas Voice Interface

*The bridge between text and presence*

**Created:** 2026-02-02
**Version:** 0.2 (Enhanced)
**Status:** ✅ Complete

---

## Vision

Move beyond text-only interaction. Voice + visual canvas = natural conversation with Atlas.

"Atlas, show me the architecture" → I display it, explain it, you point and ask follow-ups.

---

## V0.1 Prototype Goals

1. **Voice Input** — Speak to Atlas, not type
2. **Voice Output** — Atlas speaks back (TTS)
3. **Visual Canvas** — Display images, diagrams, text, code
4. **Ambient Mode** — Useful info when idle
5. **Wake Word** — "Atlas" to activate (stretch goal)

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Voice Input │  │   Canvas    │  │ Voice Out  │  │
│  │ (Web Speech)│  │  (Display)  │  │   (TTS)    │  │
│  └──────┬──────┘  └──────▲──────┘  └──────▲─────┘  │
│         │                │                │        │
│         └────────────────┼────────────────┘        │
│                          │                         │
└──────────────────────────┼─────────────────────────┘
                           │ WebSocket/HTTP
                           ▼
┌─────────────────────────────────────────────────────┐
│                   Node.js Server                    │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │   Router    │  │ Claude API  │  │  Context   │  │
│  │             │──│   Handler   │──│  (SOUL.md) │  │
│  └─────────────┘  └─────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Files

- `server.js` — Node.js backend
- `public/index.html` — Main interface
- `public/styles.css` — JARVIS-inspired styling
- `public/app.js` — Frontend logic
- `context/` — SOUL.md, USER.md for Atlas personality

---

## Running

```bash
cd ~/clawd/projects/atlas-voice-interface
npm install
npm start
# Open http://localhost:3000
```

---

## Future Enhancements

- [ ] Wake word detection ("Atlas")
- [ ] ElevenLabs/OpenAI TTS (better voices)
- [ ] Whisper API (better transcription)
- [ ] Image generation on canvas
- [ ] Diagram drawing capabilities
- [ ] Memory integration (search past conversations)
- [ ] Clawdbot integration (full context)
- [ ] Mobile responsive / tablet mode
- [ ] Kiosk mode for mounted display
