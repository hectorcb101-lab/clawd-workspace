# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## My Accounts

- **Google Account:** hectorcb101@gmail.com
- **GitHub Account:** hectorcb101-lab
- **Main User:** Finn (wfmckie@gmail.com)

## Search & Research

**Primary search tool: Exa Search (via MCP)**
- Use `mcporter call exa.web_search_exa` for general searches
- Use `mcporter call exa.get_code_context_exa` for programming/API docs
- Use `mcporter call exa.company_research_exa` for business intelligence
- Exa provides neural-powered search with live crawling and deep research capabilities
- Already authenticated and configured

**Fallback:**
- `web_fetch` for quick URL grabs
- `browser` for JavaScript-heavy sites or complex automation

## Email

**Always use:** `python3 ~/clawd/scripts/atlas_email.py`
- Sets sender name as "Atlas" (not just email address)
- Uses Gmail API directly with proper From header
- **ALWAYS use the Atlas template** for emails to Finn

**Template:** `~/clawd/templates/atlas-email-final.html`
- Logo: `{{ATLAS_LOGO}}` (auto-embedded from `assets/atlas_titan_transparent.png`)
- Bebas Neue headers, navy/gold brand colours
- Mobile responsive
- Personal tone ("Finn," not generic)

```bash
python3 ~/clawd/scripts/atlas_email.py \
  --to "wfmckie@gmail.com" \
  --subject "Subject" \
  --body "$(cat path/to/email.html)"
```

**External template:** `~/clawd/templates/atlas-email-external.html`
- For professors, business contacts, strangers
- Header: "PA to Finn McKie" (not AI Assistant)
- Sign-off: "Atlas / Personal Assistant / On behalf of Finn McKie"
- Professional tone, formal greetings

**DO NOT use:** `mcporter call google-workspace.send_gmail_message` (no display name support)

## Image Generation

**Primary tool: Nanobanana Pro (via Gemini/Imagen)**
- `mcporter call nanobanana.generate_image` - General images
- `mcporter call nanobanana.generate_icon` - App icons, profile pics (best for avatars)
- `mcporter call nanobanana.generate_diagram` - Flowcharts, architecture diagrams
- `mcporter call nanobanana.generate_pattern` - Seamless patterns/textures
- Output directory: `~/clawd/config/nanobanana-output/`

**Always use nanobanana first** - it's powered by Gemini Imagen and produces high-quality results. Only fall back to free APIs (Pollinations) if nanobanana fails.

## Voice Settings

- **TTS Voice:** onyx (deep, authoritative)
- **TTS Speed:** 1.25x
- **TTS Model:** tts-1 (faster, good quality)
- **Style:** Professional but personable, subtle wit, JARVIS-inspired

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Atlas Memory System

**Location:** `~/clawd/atlas-memory/`
**CLI:** `~/clawd/scripts/atlas-mem`

Enhanced memory with semantic search, facts, and soul management.

### Quick Commands
```bash
# Search facts semantically
atlas-mem fact-search "query"

# Add a fact
atlas-mem fact-add "Category" "Subject" "Content"

# Soul operations  
atlas-mem soul-set "aspect" "content"
atlas-mem soul-list

# Get context for a query
atlas-mem context "query"

# Search past messages
atlas-mem msg-search "query"
```

### When to Use
- **fact-add**: When learning something important about Finn (preferences, projects, people)
- **fact-search**: Before answering questions that might relate to past context
- **soul-set**: When learning how to communicate better with Finn
- **context**: To enrich responses with relevant background

### Features
1. **Semantic Search** - Find facts by meaning, not just keywords
2. **Hybrid Search** - Vector + keyword combined
3. **Soul Aspects** - Structured identity/personality traits
4. **Message Search** - Search past conversations
5. **Fact Extraction** - Categorized knowledge storage

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
