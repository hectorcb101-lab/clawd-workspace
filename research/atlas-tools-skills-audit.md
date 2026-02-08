# Atlas Tools & Skills Audit
**Date:** 2026-02-08
**Auditor:** Atlas (sub-agent)

---

## Part 1: TOOLS.md Audit

### Overall Assessment
TOOLS.md is **bloated** — 350+ lines mixing account credentials, tool documentation, and system descriptions. Signal-to-noise ratio: ~40%. Half the file duplicates what's in SKILL.md files or could be.

### Section-by-Section

| Section | Status | Notes |
|---------|--------|-------|
| My Accounts | ✅ Current | Useful, keep |
| Obsidian Vault | ✅ Current | Useful, keep |
| Search & Research | ⚠️ Stale | References `mcporter call exa.*` but mcporter isn't in PATH. Exa works via skill. Duplicates exa-search SKILL.md |
| Email | ✅ Current | Good, practical |
| Image Generation | ⚠️ Unverified | `mcporter call nanobanana.*` — not tested this session. References mcporter which isn't in PATH |
| Voice Settings | ✅ Current | Keep |
| Atlas Self-Modification | ✅ Works | But duplicates what's in the skill/project. ~60 lines that could be 10 |
| Atlas Self-Awareness | ✅ Works | Same duplication issue. ~40 lines |
| Atlas Judgment Layer | ✅ Works | Same. ~50 lines |
| Atlas Memory System | ✅ Works | Same. ~50 lines |
| Notion | ✅ Current | Keep |
| Auto-Built: convert_markdown_to_pdf | ⚠️ Stub | Auto-generated, never implemented |

### Critical Issue: `~/clawd/bin/` NOT in PATH
All `atlas-*` CLIs require full path (`~/clawd/bin/atlas-mem`) or won't be found. TOOLS.md documents them as if they're in PATH. This is a recurring friction point.

### Undocumented in TOOLS.md
- `atlas-bus` — Event bus CLI (Feb 3). Not mentioned anywhere
- `atlas-eval` — Evaluation CLI. Not documented
- `atlas-finetune` — Fine-tuning CLI. Not documented  
- `atlas-llm` — LLM interaction CLI. Not documented
- `atlas-quality` — Quality assessment CLI. Not documented
- `atlas-train` — Training CLI. Not documented
- `email-tracker` — Email tracking. Not documented
- `gmail-watcher` — Gmail watcher. Not documented
- Most scripts in `~/clawd/scripts/` — undocumented

### Recommendation
**Restructure TOOLS.md** into:
1. **Accounts & Credentials** (keep as-is, ~20 lines)
2. **CLI Quick Reference** — one-liner per CLI with full path
3. **Environment Notes** (voice, obsidian path, etc.)

Move all detailed tool docs to respective SKILL.md files. TOOLS.md should be a cheat sheet, not a manual.

---

## Part 2: Skills Audit

### Custom Skills (`~/clawd/skills/`)

| Skill | Status | Assessment |
|-------|--------|------------|
| **Reddit** | 💤 DORMANT | Works (no auth needed for reading), but Atlas rarely uses it. Could be valuable for research |
| **agent-browser** | 🗑️ OBSOLETE | OpenClaw has native `browser` tool. This skill's CLI (`agent-browser`) is redundant. 250+ lines of docs for a superseded tool |
| **convert_markdown_to_pdf** | ⚠️ BROKEN | Auto-generated stub. Never implemented. No actual code. Delete or implement |
| **dr** (Deep Research) | ✅ ACTIVE | Core workflow, well-documented. Works via Exa |
| **ex** (Exhaustive Research) | 🌟 UNDERUSED | Powerful but rarely triggered. 10-15 min deep research with email delivery |
| **exa-search** | ✅ ACTIVE | Foundation for dr/ex. Well-documented |
| **google-docs-formatter** | 💤 DORMANT | Elaborate skill but rarely used. Index calculation is fragile |
| **google-lean** | ✅ ACTIVE | Core skill. Gmail, Calendar, Drive. Used daily |
| **google-workspace-auth** | ✅ ACTIVE | Reference doc for OAuth troubleshooting. Useful when needed |
| **obsidian** | ✅ ACTIVE | Used for vault management |
| **perry-coding-agents** | 💤 DORMANT | Requires Perry workspaces. Niche use case |
| **polymarket** | 🌟 UNDERUSED | Works, interesting for predictions/research. Rarely triggered |
| **project-builder** | ✅ ACTIVE | Massive skill (500+ lines). Core workflow guide. Could be trimmed |
| **remotion-video-toolkit** | 💤 DORMANT | Video generation. Cool but unused |
| **second-brain** | 💤 DORMANT | Overlaps with atlas-mem + obsidian |
| **self-improving-agent** | 🗑️ OBSOLETE | Superseded by atlas-self + atlas-mod |
| **team** | 💤 DORMANT | Agent team coordination |
| **yahoo-finance** | 🌟 UNDERUSED | Financial data. Useful for research tasks |

### Summary
- **4 Active** — dr, exa-search, google-lean, obsidian
- **3 Underused** — ex, polymarket, yahoo-finance
- **5 Dormant** — Reddit, google-docs-formatter, perry-coding-agents, remotion-video-toolkit, second-brain, team
- **2 Obsolete** — agent-browser, self-improving-agent
- **1 Broken** — convert_markdown_to_pdf

---

## Part 3: Capability Gaps

### Missing Capabilities
1. **No scheduled task runner** — Cron exists but no skill for managing recurring tasks
2. **No structured note-taking from conversations** — Atlas captures memory but can't create structured meeting notes or conversation summaries on demand
3. **No file format conversion** — PDF skill is broken. No DOCX, PPTX, etc.
4. **No notification aggregator** — Checks email manually. No unified "what needs attention" across all channels
5. **No code deployment skill** — project-builder documents coding but no deployment automation

### Quick Wins
- **Fix PATH** — Add `~/clawd/bin` to PATH in `.bashrc`. Eliminates constant friction
- **Delete broken/obsolete skills** — agent-browser, self-improving-agent, convert_markdown_to_pdf stub
- **Document the 6 undocumented CLIs** in TOOLS.md (atlas-bus, atlas-eval, atlas-finetune, atlas-llm, atlas-quality, atlas-train)

---

## Part 4: Tool Ecosystem Architecture

### Current Organization Issues
1. **TOOLS.md is doing too much** — credentials + tool docs + system descriptions. Should be split
2. **Duplication** — Atlas OS tools documented in both TOOLS.md AND project READMEs
3. **Stale references** — mcporter commands documented but PATH issues make them unreliable
4. **6 CLIs completely undocumented** — atlas-bus, atlas-eval, atlas-finetune, atlas-llm, atlas-quality, atlas-train

### `~/clawd/bin/` CLIs (13 total)

| CLI | Documented? | Works? |
|-----|-------------|--------|
| atlas-bus | ❌ No | Unknown |
| atlas-daemon | ✅ Yes | ✅ Yes (running, PID 813571) |
| atlas-eval | ❌ No | Unknown |
| atlas-finetune | ❌ No | Unknown |
| atlas-judge | ✅ Yes | ✅ Yes (12 principles) |
| atlas-llm | ❌ No | Unknown |
| atlas-mem | ✅ Yes | ✅ Yes (718 events) |
| atlas-mod | ✅ Yes | ✅ Yes (10 requests) |
| atlas-quality | ❌ No | Unknown |
| atlas-self | ✅ Yes | ✅ Yes (health: 46.3) |
| atlas-train | ❌ No | Unknown |
| email-tracker | ❌ No | Unknown |
| gmail-watcher | ❌ No | Unknown |

### `~/clawd/scripts/` (20+ files)
Mostly undocumented. Key ones:
- `atlas_email.py` — documented in TOOLS.md ✅
- `google` — documented in google-lean SKILL.md ✅
- `google_lean.py` — backing script for google-lean
- `check_emails.py`, `email_monitor.py`, `email_notify_daemon.py` — email infrastructure, undocumented
- `weather_briefing.py` — undocumented
- `voice_respond.py` — undocumented
- `godel_core.py` — undocumented build loop engine

### `~/clawd/projects/` (12 projects)
- atlas-infrastructure, atlas-memory-evolution, atlas-os, atlas-self-awareness, atlas-self-modification — Core Atlas OS
- atlas-voice-interface — dormant
- daily-intelligence-briefing — unclear status
- gmail-webhook — unclear status
- prediction-arb — unclear status
- research-protocol — unclear status
- rugby-sponsors, six-nations-fantasy-2026 — domain projects

### Recommended Restructure

**TOOLS.md → Lean cheat sheet (~80 lines):**
```
# Accounts (keep)
# CLI Quick Reference (one-liner per tool, full paths)
# Environment Notes (voice, paths, devices)
```

**Move detailed docs → SKILL.md files or project READMEs**

**Delete:**
- `skills/agent-browser/` (superseded by native browser)
- `skills/self-improving-agent/` (superseded by atlas-self + atlas-mod)
- `skills/convert_markdown_to_pdf/` (stub, never implemented)

**Document:**
- All 6 undocumented CLIs
- Key scripts (weather, voice, email infrastructure)

---

## Priority Actions

1. 🔴 **Fix PATH** — `echo 'export PATH="$HOME/clawd/bin:$PATH"' >> ~/.bashrc`
2. 🔴 **Delete 3 obsolete/broken skills** — agent-browser, self-improving-agent, convert_markdown_to_pdf
3. 🟡 **Slim TOOLS.md** — move detailed docs out, keep as cheat sheet
4. 🟡 **Document 6 undocumented CLIs** — atlas-bus, atlas-eval, atlas-finetune, atlas-llm, atlas-quality, atlas-train
5. 🟢 **Leverage underused skills** — polymarket, yahoo-finance, ex research
6. 🟢 **Audit projects/** — determine status of each project, archive dead ones
