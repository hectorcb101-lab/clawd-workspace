# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## My Accounts

- **Google Account:** hectorcb101@gmail.com
- **GitHub Account:** hectorcb101-lab
- **GitHub (Finn's repos):** fmckie — PAT stored in ~/.clawdbot/.env
- **Main User:** Finn (wfmckie@gmail.com)

## Obsidian Vault

**Location:** `~/clawd/obsidian-vault/`
**Repo:** git@github.com:fmckie/Obsidian-Vault.git

**⚠️ ALWAYS push after edits** — Finn won't see changes otherwise.
```bash
cd ~/clawd/obsidian-vault && git add -A && git commit -m "message" && git push
```

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
- **ALWAYS use the Atlas template for ALL emails to Finn** (not just morning briefings — consistency matters)

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

- **TTS Voice:** echo (warm, conversational, male)
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

## Atlas Self-Modification System (NEW)

**Location:** `~/clawd/projects/atlas-self-modification/`
**CLI:** `~/clawd/bin/atlas-mod`

### What it does
Closes the loop from insight to action. When I detect a pattern or get corrected, this system proposes modifications to my own instructions.

All changes are:
- Backed up before applying
- Logged with full diffs
- Git committed
- Reversible via rollback

### Key Commands
```bash
# Manual modifications
atlas-mod propose <file> -c "content" -r "reason"  # Propose modification
atlas-mod list [--status pending]                   # List modifications
atlas-mod pending                                   # Show pending (shortcut)
atlas-mod show <id>                                # Show details
atlas-mod approve <id>                             # Approve high-risk change
atlas-mod apply <id>                               # Apply modification
atlas-mod rollback <id> -r "reason"                # Undo modification
atlas-mod history [--file <path>]                  # Show history
atlas-mod stats                                    # Statistics

# From self-awareness (Phase 2)
atlas-mod from-correction <id>                     # Propose from correction
atlas-mod from-insight <id>                        # Propose from insight
atlas-mod process --dry-run                        # Show pending items
atlas-mod process                                  # Process all
atlas-mod rules list                               # List active rules
atlas-mod rules add --name X --trigger-type Y ...  # Add rule
```

### Risk Levels
- **LOW** (🟢) — Auto-apply ready (HEARTBEAT.md, memory/)
- **MEDIUM** (🟡) — Review recommended (TOOLS.md, skills/)
- **HIGH** (🟠) — Requires approval (AGENTS.md sections)
- **CRITICAL** (🔴) — Always requires approval (SOUL.md, USER.md, AGENTS.md edits)

### Safety
- Protected files (SOUL.md, USER.md) always require approval
- Large changes (>15 lines) flag for review
- Low confidence (<50%) increases risk score
- Every change creates backup + git commit

---

## Atlas Self-Awareness System (NEW)

**Location:** `~/clawd/projects/atlas-self-awareness/`
**CLI:** `~/clawd/bin/atlas-self`

### What it does
Memory stores what happened; self-awareness tells me what it means.
- Logs task outcomes and corrections
- Detects patterns (failures, strengths)
- Computes health score (0-100)
- Identifies blind spots
- Generates proactive insights

### Key Commands
```bash
atlas-self log-outcome <type> <outcome> -n "notes"  # Log task result
atlas-self log-correction "signal" -t type -l "lesson"  # Log correction
atlas-self analyze                    # Full analysis + health score
atlas-self strengths                  # What am I good at?
atlas-self weaknesses                 # What do I struggle with?
atlas-self blind-spots               # What am I missing?
atlas-self check                      # Heartbeat integration
atlas-self ask "question"            # Natural language query
```

### When to Log
- After completing significant tasks → `log-outcome`
- When Finn corrects me → `log-correction`
- During heartbeats → `check`

---

## Atlas Judgment Layer (NEW)

**Location:** `~/clawd/projects/atlas-os/`
**CLI:** `~/clawd/bin/atlas-judge`
**Export:** `~/clawd/JUDGMENT.md`

### What it does
The Judgment Layer provides meta-cognitive principles for decision-making.
- Rules say "when X, do Y"
- Principles say "how to decide what to do"
- Tracks principle applications and effectiveness
- Enables calibrated confidence over time

### Key Commands
```bash
# Core
atlas-judge principles list              # List all principles
atlas-judge principle show <id>          # Show principle details
atlas-judge consult "situation"          # Get relevant principles
atlas-judge task "desc" --type X --stakes high  # Get principles for task

# Application tracking
atlas-judge apply <id> -s "situation" --how "..." -d "decision"  # Log application
atlas-judge outcome <app_id> -r success|partial|failure          # Log outcome

# Learning (Phase 3)
atlas-judge learn [--auto-update]        # Run learning cycle
atlas-judge effectiveness [principle_id] # Show effectiveness scores
atlas-judge review                       # Show principles needing review

# Calibration
atlas-judge calibrate -d domain -p "prediction" -c 0.7 -o "outcome" [--correct]
atlas-judge calibration                  # Analyze calibration

# Maintenance
atlas-judge sync                         # Sync with self-awareness
atlas-judge stats                        # Statistics
atlas-judge export                       # Regenerate JUDGMENT.md
```

### Seed Principles (10 core)
- **Decision:** Complexity matching, reversibility, explicit uncertainty
- **Meta-cognitive:** Evidence requirement, pattern vs reasoning, correction significance
- **Priority:** Stakeholder hierarchy, quality hierarchy
- **Escalation:** External action gate, stakes-based autonomy

### When to Use
- Before making significant decisions → `atlas-judge consult`
- After applying a principle → `atlas-judge apply`
- When outcome is known → `atlas-judge outcome`

---

## Atlas Memory System (PRIMARY)

**Location:** `~/clawd/projects/atlas-memory-evolution/`
**CLIs:** `atlas-mem` (memory) + `atlas-daemon` (real-time capture)

### The System (Phase 5 Complete - 2026-02-01)
Event log → extraction → knowledge graph → semantic search.
**Real-time capture enabled** — daemon watches files automatically.

### Memory Daemon (Real-Time Capture)
```bash
atlas-daemon status   # Check if running
atlas-daemon start    # Start daemon
atlas-daemon stop     # Stop daemon
atlas-daemon logs     # View daemon logs
```
- Auto-starts on boot via systemd
- Watches ~/clawd/memory/ for changes
- Runs extraction when threshold reached (10 events)
- **No manual logging needed** — just work, it captures everything

### Memory CLI
```bash
atlas-mem search "topic"       # Search memory (semantic + keyword)
atlas-mem remember "fact"      # Manually log something
atlas-mem sync                 # Force sync + extraction
atlas-mem stats                # Check stats
atlas-mem summary              # Knowledge summary
atlas-mem index                # Rebuild semantic index
```

### Current Stats
- **597+ events** captured
- **575+ facts** extracted
- **13 entities** recognized
- Storage: ~250 KB
- Semantic search with embeddings

### Architecture
```
File Change → Daemon → Event Log → Extraction → Knowledge Graph → Semantic Index
                                      ↓
                              Facts, Entities, Relationships
```

### When to Query
- **ALWAYS** before answering questions about past work, decisions, preferences
- When Finn asks "do you remember..." or "what about that time..."
- When context from previous sessions would help

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.



## Auto-Built: convert_markdown_to_pdf

**Path:** `/home/ubuntu/clawd/skills/convert_markdown_to_pdf`
**Created:** 2026-01-30
**Status:** Created skill: convert_markdown_to_pdf

---

Add whatever helps you do your job. This is your cheat sheet.


## Notion

**Status:** ✅ Connected  
**Workspace:** Finn's personal workspace  
**API Key:** ~/.config/notion/api_key

**Main Pages:**
- MSc AI 2026: `2fb6833e-c12d-80bf-9339-ff27ec4be644`
- 1st Semester Assignments DB: `2fb6833e-c12d-8167-8910-df1c19219133`

