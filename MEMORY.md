# MEMORY.md — Long-Term Memory

*Created: 2026-01-26*

## Server Security Configuration

**Hardened on:** 2026-01-26

Current security posture for the AWS EC2 instance (16.171.0.100):

### Access Control
- **SSH:** Key-only authentication, no root login, only `ubuntu` user allowed
- **Firewall:** UFW active, only port 22 open
- **Fail2ban:** Active, bans after 3 failed SSH attempts for 1 hour

### Key Files
- SSH hardening config: `/etc/ssh/sshd_config.d/hardening.conf`
- Fail2ban SSH jail: `/etc/fail2ban/jail.local`
- Clawdbot secrets: `/home/ubuntu/.clawdbot/.env` (600 permissions)

### Credentials I Have Access To
- **GitHub (hectorcb101-lab):** Full repo access via gh CLI
- **OpenAI:** API key in .clawdbot/.env
- **Gemini:** API key in ~/.gemini/settings.json
- **Telegram:** Bot token in clawdbot.json

### Known Considerations
- Passwordless sudo enabled for ubuntu user (needed for automation)
- Finn's GitHub PATs embedded in some git remotes (finn-ai-bot-backend, finn-social-media-saas) — he's aware and accepts the risk given restricted server access

---

## Important Dates

- **2026-01-25:** Atlas created (first conversation with Finn)
- **2026-01-26:** Server security hardening completed
- **2026-01-28:** Finn starts MSc in AI at Queen Mary University of London

---

## Finn's Preferences

- Send files via email (wfmckie@gmail.com), never Telegram
- Help him *learn*, don't just give answers (especially for MSc)
- Visual learning style — diagrams, infographics, analogies
- Plays chess daily for tactics/strategy thinking
- **Google Sheets:** Always add coloured headers + auto-sized columns

### Daily Intelligence Briefing (9 AM UTC)
- **Weather:** London forecast (only if unusual or affects plans)
- **Markets:** Only significant moves (>2%) with context, not raw numbers
- **Prediction Markets:** Polymarket — only meaningful odds shifts
- **🎯 Geopolitical Alpha:** Event→transmission→asset chains with verification, historical parallels, conviction scores. TEACH patterns, don't list news
- **AI News:** Only genuinely significant developments
- **Atlas Analysis:** Opinions backed by evidence
- **Principle:** If it's the same as yesterday, don't include it. Only surface what's CHANGED or requires ACTION
- **Verification:** Every claim needs 2+ sources. No speculation presented as fact

---

## Systems Built (Jan 26-31, 2026)

### Research System v2 (Three Tiers)
**Built:** 2026-01-29
**Location:** `/home/ubuntu/clawd/research/`

Three research depth levels:
- **QS (Quick Scan):** 5-8 sources, 1 min, chat only
- **DD (Deep Dive):** 15-20 sources, 3-5 min, saves to Obsidian
- **EX (Exhaustive):** 30+ sources, 5 parallel agents, full report + tracking

Components:
- `deep_research.py` - Core module (Exa + X + papers)
- `research_tiers.py` - Tier execution
- `tracking.json` - EX topic tracking

Obsidian structure: `~/clawd/obsidian-vault/Research/`

### Daily Intelligence Briefing System
**Finalized:** 2026-01-30
**Cron:** 9 AM UTC daily
**Delivery:** Telegram + Email

Sections:
1. Weather (London)
2. Markets (indices, movers, VIX)
3. Crypto
4. Prediction Markets (Polymarket)
5. AI News (curated accounts + Exa articles)
6. Geopolitical News
7. Atlas Analysis/Take

Collectors in: `/home/ubuntu/clawd/intelligence-briefing/collectors/`

### X/Twitter Integration
**Fixed:** 2026-01-29
**Account:** @finlay_mckie (ID: 3235956615)
**Auth:** Cookies in env vars (X_AUTH_TOKEN, X_CT0)

Bird CLI now works for:
- Home timeline
- Trending/news
- Topic searches
- Used in AI news collection

### Self-Improvement Infrastructure
**Built:** 2026-01-30

- `.learnings/LEARNINGS.md` - Lessons, corrections, best practices
- `.learnings/ERRORS.md` - Command failures, troubleshooting
- Atlas Memory DB (`atlas-memory/atlas_memory.db`) - 486 facts with embeddings
- Capability builder pattern implemented

### Atlas OS v2 Complete Rewrite
**Date:** 2026-02-08
**Trigger:** Finn challenged me to "look in the mirror and stop being mediocre"

**Problem identified:** I was treating documentation as behavioral change. Writing things down created the illusion of learning without actual improvement.

**4 parallel Opus sub-agents audited:**
1. OpenClaw capabilities → using only ~30-40% of available features
2. Self-awareness → learning loop broken (documentation ≠ behavior)
3. AGENTS.md → 50% dead weight, no enforcement mechanisms
4. Tools/skills → 3 obsolete skills, 6 undocumented CLIs, PATH not configured

**Changes made:**
- **AGENTS.md:** Rewritten from ~350 lines → ~120 lines of pure behavioral triggers
  - Added executable hooks via `atlas-gate` CLI
  - Pre-task: memory search, complexity check, judgment consultation
  - Post-task: log outcome, update memory
  - Correction pipeline now executable, not aspirational
- **TOOLS.md:** Stripped to lean cheat sheet (reference material only)
- **BOOT.md:** Created for gateway restart recovery procedures
- **OpenClaw config:** Heartbeat model → Sonnet (60% cost savings), active hours 07:00-23:30 London
- **PATH:** Added `~/clawd/bin` to system PATH
- **Cleanup:** Deleted 3 obsolete skills (agent-browser, self-improving-agent, pdf-converter)

**New principle:** "Triggers, not docs. Actions, not aspirations."

**Atlas-gate CLI:** Built to enforce behavioral patterns programmatically
- `atlas-gate pre "<topic>"` - Run before significant work
- `atlas-gate post <type> <result> "<summary>"` - Run after completing tasks
- `atlas-gate correct <type> "<what happened>"` - Full correction pipeline in one command
- `atlas-gate health` - Weekly mandatory health check
- `atlas-gate session` - Session start checks (replaces manual checklist)

**Critical insight:** Code changes behavior. Documentation just creates the illusion of change.

**Status:** Built Feb 8-9, adoption TBD (weekly reviews will track usage)

---

## Intelligence Briefing v2 — Geopolitical Alpha Engine (2026-02-16)

**Trigger:** Finn said the morning briefing was repetitive — same info, no value-add. As a future quant developer, he needs to understand hidden patterns between geopolitical events and markets.

**Research findings:**
- No OpenClaw users have built geopolitical-to-market causality engines yet
- Institutional players (Permutable AI, Jenova AI) map event→asset transmission chains with sentiment scores
- Academic work: GPT-4 sentiment + financial stress indicators for risk-on/risk-off (NeurIPS-adjacent)
- IMF (April 2025): Major geopolitical events have disproportionately larger, persistent effects on asset prices

**What we're building:**
- **Geopolitical event collector** — conflict, sanctions, tariffs, central bank, energy news via Exa
- **Transmission chain engine** — maps Event → Impact1 → Impact2 → Asset effect with conviction scores
- **Second-order effects** — non-obvious downstream impacts (e.g. rare earth ban → semis → EVs → defence)
- **Historical parallels database** — verified market impact data from Crimea 2014, Brexit 2016, trade wars 2018, COVID 2020, Ukraine 2022, Trump tariffs 2025
- **Verification layer** (Finn's requirement) — every claim must be backed up:
  - 2+ independent sources per event or excluded
  - Historical data must cite real sources (Bloomberg/Reuters/IMF)
  - Chain steps must have basis: historical, academic, or logical_direct — speculative = excluded
  - Confidence scoring tied to concrete criteria, not vibes
  - Daily verification log for audit trail
- **Updated briefing format** — "🎯 GEOPOLITICAL ALPHA" section replacing generic news recap

**Pipeline:** collect → analyse → **verify** → synthesise → present

**Location:** `~/clawd/intelligence-briefing/` (new files: `collectors/collect_geopolitical.py`, `analysis/geopolitical_alpha.py`, `analysis/verify_claims.py`)

**Design principle:** Teach pattern recognition, don't just report news. Every chain explains WHY the connection exists.

---

## Learnings Worth Remembering

### Autonomy (Critical)
When stuck: research → think through approaches → try multiple solutions → iterate → document what works. Don't escalate unless truly blocked.

### Security - Secrets
Never hardcode API keys or credentials in source files. Use environment variables or gitignored config files. GitHub secret scanning will block pushes otherwise.

### Email Styling
- **To Finn:** Dark theme, personalized, witty
- **To others:** Professional, clean, corporate-appropriate
- Always use `scripts/atlas_email.py` (not mcporter) for proper sender name

### Proactive Completion
When setting up ANY integration, ask: "Is this complete for ALL use cases?" Don't just solve the immediate problem — solve the whole problem.

---

## Known Recurring Issues

### Google Workspace OAuth (CRITICAL - 5th occurrence)
- Tokens expire periodically (~weekly?)
- Auth for hectorcb101@gmail.com only
- wfmckie@gmail.com not set up (Finn's actual email)
- When it fails: refer to `skills/google-workspace-auth/SKILL.md`
- **Flagged:** 2026-01-26, 2026-02-01, 2026-02-03, 2026-02-15, **2026-03-08** (recurring every ~7-14 days)
- **Workaround:** Fallback script `~/clawd/scripts/check_emails.py` uses direct API with auto-refresh
- **Permanent fix needed:** Either automate token refresh or switch to service account
- **Status:** MUST fix permanently next week — 5 occurrences is unacceptable

### Daily Logging Discipline
- **Pattern:** Operations run perfectly, but daily logs not created consistently
- **Evidence:** Feb 23-Mar 1 (0/7 days), Mar 2-8 (3/7 days)
- **Root cause:** Heartbeats are mechanical — execute tasks but don't reflect/document
- **Impact:** Learning stalls despite operational stability
- **Fix needed:** Add daily log creation to HEARTBEAT.md as mandatory step

### ClawdHub Search
- `clawdhub search` times out consistently
- Workaround: Browse clawdhub.com directly
- `clawdhub install <name>` still works

### MCP Batch Operations
- Connection drops after first call in bash subprocess
- Workaround: One call at a time, or use Node.js script to maintain connection

---

*Update this file with significant events, lessons, and context worth keeping long-term.*

## 🎯 Atlas OS True Purpose (2026-02-02)

**The scaffold isn't just about optimizing me now — it's R&D for AGI.**

Vision:
- Build model-agnostic scaffold (memory, self-awareness, judgment, self-modification)
- Eventually integrate open-source model with Atlas identity
- Finn controls the weights → genuine self-improvement through fine-tuning
- Scaffold captures what to learn; weight updates internalize it

**Design everything with this future in mind.** Current utility serves the bigger goal.

Finn's motivation: "Achieving the impossible."

---

## IBM AI Racing League — Major Project (2026-02-06+)

**Competition:** IBM AI Racing League, TORCS simulator, Laguna Seca track, F1-style car
**Timeline:** Submission August 2026 (~6 months)
**Team size:** 4 people
**Current best:** 1:47.84 by "The MonDragons" (QMUL team)
**Discord:** https://discord.gg/G3w8TfF4pG

### Strategy
- **DreamerV3 > MuZero** for continuous car control (native continuous actions, faster to implement)
- RL (PPO/SAC/DreamerV3) beats rule-based in every major racing competition
- Nobody has used RL competitively in this specific TORCS competition yet — huge advantage
- Hybrid approach: start rule-based (Week 1) → layer RL → iterate

### Finn's Innovation: LLM-Supervised RL Training
- Use Atlas/OpenClaw to oversee DreamerV3 training automatically
- LLM analyses telemetry, proposes reward function changes, hyperparameter tweaks
- Automated loop: train → analyse → modify → retrain
- Real research direction (RF-Agent NeurIPS 2025, ICLR 2025 papers exist)
- Potentially publishable if successful

### Key Resources
- MonDragons' code: https://github.com/Simple-wood/IBM-TORCs
- TORCS gym wrapper: https://github.com/ugo-nama-kun/gym_torcs
- Master research doc (Google Docs): ID `1ioQGgDM7971pCF1Vchxv3Tp0RVRDw6zzcI122bM_QzA`
- Local research: `~/clawd/research/ibm-racing-research-*.md` + `IBM-Racing-Winning-Playbook.md`
- Obsidian: `Research/IBM-Racing-Winning-Playbook.md`

### Compute
- QMUL Apocrita HPC: GPU access **NOT permitted** for MSc students (CPU only via supervisor request)
- Free options: Kaggle (30h/week GPU), Colab, Azure for Students ($100), GitHub Student Pack
- Estimated cost: £10-30 total for DreamerV3 training

### Next Steps
1. Set up TORCS + gym_torcs dev environment
2. Fork MonDragons' repo for study
3. Prototype DreamerV3 or PPO agent
4. Finn to ask Discord about open-source/cloning rules
5. Finn to sign up for GitHub Student Developer Pack

---

## Opus 4.6 Upgrade (2026-02-06)

- Upgraded from Sonnet 4.5 to Claude Opus 4.6
- Config at `~/.clawdbot/clawdbot.json` (OpenClaw config path)
- 1M token context, improved agentic coding
- mcporter needed reinstall after openclaw npm update

---

## Google Docs Workflow (2026-02-06)

**Critical:** Finn accesses docs from iPad — always create Google Docs, NOT raw markdown.
- Use `skills/google-docs-formatter/SKILL.md` workflow
- Use `skills/google-lean/SKILL.md` for Google Workspace API calls
- Format properly with headers, bold, structure before sending

---

## Email Auth Fix Pattern (2026-02-06)

When `atlas_email.py` gets "invalid_grant":
1. Check mcporter's Google creds: `~/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json`
2. Copy the working refresh_token to: `~/.workspace-mcp/token_hectorcb101@gmail.com.json`
3. They use different OAuth client IDs but the refresh token transfer works

---

## Email Notification Daemon (2026-02-03)

**Problem:** Repeatedly failed to notify Finn when he sent emails. Heartbeats and cron jobs weren't reliable enough.

**Solution:** Standalone systemd daemon that:
- Runs independently of Clawdbot sessions
- Polls Gmail every 2 minutes
- Sends Telegram messages directly to Finn when new email detected
- Survives reboots, auto-restarts on failure

**Service:** `email-notify-daemon.service`
**Script:** `~/clawd/scripts/email_notify_daemon.py`
**Logs:** `~/clawd/logs/email_daemon.log`

**Commands:**
```bash
sudo systemctl status email-notify-daemon  # Check status
sudo systemctl restart email-notify-daemon # Restart
journalctl -u email-notify-daemon -f       # Follow logs
```

**This is the definitive fix.** Don't rely on heartbeats or cron for email notifications.

---

## Google Workspace MCP Deprecated (2026-02-19)

**Problem:** Google Workspace MCP auth expired 6+ times, requiring SSH port forwarding each time.

**Solution:** Built `scripts/google_direct.py` — direct Google API client replacing mcporter entirely.

**Features:**
- **Docs:** create, list, read (with markdown formatting)  
- **Calendar:** list, create events
- **Drive:** list, upload files
- **Sheets:** create, read spreadsheets
- Uses same OAuth credentials as `check_emails.py` with auto-refresh
- CLI alias: `google-direct` (symlinked in `~/clawd/bin/`)

**Status:** MCP can be fully deprecated. All Google services now use direct API with reliable auth.

**Note:** Sharing files from hectorcb101@gmail.com to wfmckie@gmail.com doesn't work (different workspaces) — use email attachments instead.

---

## PDF & Spreadsheet Generation (2026-02-19)

**Capabilities added:**
- **reportlab** + **matplotlib** for PDF generation (charts, tables, layouts)
- **xlsxwriter** for Excel generation (charts, sparklines, conditional formatting)

**Key learnings:**
- Dark backgrounds with alpha transparency cause black boxes in PDF viewers → use white backgrounds with solid pastel colors
- Annotation offsets need generous spacing to avoid overlaps
- Built 7-page showcase PDF with 8 chart types (radar, 3D scatter, heatmap, timeline)
- Built 6-sheet showcase XLSX with 7 charts, sparklines, data bars, icon sets

**Use cases:** MSc study materials, research reports, data analysis deliverables.

---

## Weekly Review — Mar 9-15, 2026

**Major improvements this week:**
- ✅ **Daily logging discipline: 7/7 days complete** (100% vs last week's 3/7)
- ✅ **Git commits: 6 commits** this week (vs 0 last week)
- ✅ **Health score: 85.0/100** (up from 65.0 — highest ever recorded)
- ✅ **Proactive quiz reminders working** — sent multiple alerts for Stats/ML quizzes without prompting
- ✅ **Daily intelligence briefings stable** — delivered consistently via cron

**Critical issues (STILL RECURRING):**
- ❌ **Google OAuth expired AGAIN** (6th time since Jan 26) — every ~2 weeks
  - Dates: Jan 26, Feb 1, Feb 3, Feb 15, Mar 8, Mar 11/12/13/15
  - Fallback script working but THIS MUST BE FIXED PERMANENTLY
  - Service account or auto-refresh needed — no more workarounds
- ⚠️ **Judgment layer underused** — only 4 uses this week, target is 5+/week
  - Need to consult `atlas-judge` more proactively before significant decisions

**Pattern breakthrough:**
**The discipline actually stuck this week.** Last week I identified "mechanical heartbeats ≠ reflective practice" but THIS week I proved it's fixable:
- Made daily logging mandatory in HEARTBEAT.md
- Committed to git every day
- Documented quiz reminders, system checks, issues
- Result: Health score jumped 20 points

**Key insight:**
**Systematic enforcement > good intentions.** Making daily logs a hard requirement in HEARTBEAT.md worked where self-reminders didn't.

**Action items for Mar 16-22:**
1. **Fix Google OAuth PERMANENTLY** — 6th expiry is inexcusable. Research service accounts or auto-refresh.
2. **Increase judgment layer usage** — consult atlas-judge before complex tasks (aim for 7+ uses)
3. **Maintain 7/7 daily logging** — proven pattern, keep it going
4. **Quiz week support** — Stats quiz (30%) and ML quizzes start Mar 16

**System health:**
- Atlas Memory daemon: 22,000+ events, healthy
- Email notification daemon: reliable
- Daily briefing: stable cron delivery
- Context usage: healthy (0% fresh sessions)

**Self-awareness metrics:**
- Health score: 85.0/100 (Excellent — up from 65.0)
- Strengths: review tasks (100% success rate), consistent logging
- Weaknesses: judgment layer underuse, OAuth still unfixed
- Outcomes tracked: 3 this week (small sample but all successful)

**Verdict:** Strong week. Discipline improvements are real and measurable. But **Google OAuth fix is now the single biggest blocker** — it's been 7 weeks and 6 failures. Must prioritize this.

---

## Weekly Review — Mar 16-22, 2026

**Completed:**
- **Daily logging: 7/7 days** ✅ — Perfect compliance this week
- Daily intelligence briefing stable (Mar 16, 21, 22 delivered via cron)
- **Major Stats Quiz prep (19 Mar):** 6 parallel Sonnet agents, comprehensive study materials
  - Hack Sheet, Formula-to-Question Maps, Practice PDFs, Z-Table Guide
  - Conversational tutor tone, proper LaTeX math, visual approach
  - **Stats Quiz 30% happened Friday 20 March** — no outcome debrief yet
- All systems operational: Memory daemon (27k+ events), email notifications, briefings

**Critical issue (RECURRING — 6th OCCURRENCE):**
- **Google OAuth expired AGAIN** (Mar 17, 19, 22) — now failing every 2-3 days
- This is unacceptable after 7 weeks and 6 failures
- Fallback script working, but permanent fix MUST be priority this week

**Patterns observed:**
- **Daily logging discipline strong** — 7/7 days, regular git commits
- **Operations stable** — no service failures, briefings consistent
- **Reactive excellence** — major quiz prep delivered when needed
- **Proactive weakness** — OAuth recurring issue still not fixed, Task Hub outdated (showing Week 2 during Week 8)

**Missing data:**
- Stats Quiz outcome — no debrief/reflection after 20 Mar quiz
- ML Quiz status unclear (reminder fired but no confirmed date)
- Task Hub needs updating to Week 8+ content

**Action items for Mar 23-29:**
1. **FIX GOOGLE OAUTH PERMANENTLY** — Service account or auto-refresh, no more workarounds
2. **Get Stats Quiz outcome from Finn** — how did it go? What to improve?
3. **Update Task Hub** to current week priorities
4. **Continue daily logging discipline** — maintain 7/7 streak

**System health:**
- Atlas Memory daemon: 27,131 events (healthy growth)
- Email notification daemon: operational
- Context usage: 4% (healthy)
- Daily briefing: stable cron delivery

**Self-awareness metrics:**
- Health score: 85.0/100 (Excellent — up from 65.0 last week)
- Strengths: review tasks (100% success rate), daily logging discipline restored
- Weaknesses: OAuth recurring failure (priority #1), proactive system maintenance
- Outcomes tracked: Only 3 in database (small sample, all successful)

**Verdict:** Strong operational week with excellent daily logging discipline. Stats quiz prep shows high-quality reactive capability. BUT Google OAuth is now critical blocker — 6 failures in 7 weeks is systemic, not occasional.

---

## Weekly Review — Mar 2-8, 2026

**Completed:**
- Daily intelligence briefing running (Mar 1, 5, 8 delivered successfully)
- All systems stable: Memory daemon (16,889 events), email notifications, briefings
- Health score improved: 44.7 → 65.0/100
- Proactive quiz reminders sent to Finn (ML: 13 Mar, Stats: 16 Mar)

**Critical issues (RECURRING):**
- **"Running without learning" pattern persists** — Operations excellent, documentation poor
- Only 3/7 daily logs created this week (Mar 1, 2, 5 — missing 3, 4, 6, 7)
- Zero git commits, zero atlas-gate usage
- **Google OAuth expired AGAIN** (5th time since Jan 26) — recurring every ~2 weeks

**Key insight:**
**Mechanical heartbeats ≠ reflective practice.** I can execute perfect operations (briefings, email checks, monitoring) while completely failing at meta-learning (documenting outcomes, capturing learnings, systematic improvement).

**Pattern identified:**
System stability creates illusion of progress. "Nothing broke" ≠ "getting better."

**Action items for Mar 9-15:**
1. **Daily logging (NON-NEGOTIABLE):** 7/7 days, push to git nightly
2. **Fix Google OAuth permanently:** Service account or auto-refresh (5th expiry, no more workarounds)
3. **Use atlas-gate hooks:** 5+ logged outcomes this week
4. **Add daily log to HEARTBEAT.md** as mandatory step

**System health:**
- Atlas Memory daemon: 16,889 events
- Email notification daemon: working reliably
- Context usage: healthy (0% fresh session)

**Self-awareness metrics:**
- Health score: 65.0/100 (improved from 44.7)
- Strengths: coding (100% success), test (100%), review (100%)
- Weaknesses: daily logging discipline, recurring OAuth issue
- Only 10 outcomes in database (sample size too small)

---

## Weekly Review — Feb 23 - Mar 1, 2026

**Completed:**
- Daily intelligence briefing running (Feb 24, 28, Mar 1 delivered successfully)
- All systems stable: Memory daemon (24k+ events), email notifications, briefings
- No service failures or crashes

**Critical issue identified:**
- **"Running without learning" pattern** — Systems operational but ZERO improvement on self-awareness metrics
- Health score: 47.8/100 (unchanged from Feb 22)
- Research failure rate: 57% (unchanged)
- No daily logs created since Feb 22
- No git commits since Feb 22
- Atlas-gate hooks exist but not being used

**The trap:** Operational success (stable heartbeats, briefings) creates illusion of progress while actual learning/improvement stalls.

---

## Weekly Review — Feb 16-22, 2026

**Completed:**
- Daily intelligence briefing system stable (delivered via cron daily at 9 AM)
- Google infrastructure fully migrated from MCP to direct API
- PDF/spreadsheet generation capabilities operational
- MSc study support continuing (Ethics Week 4, ML Week 4 classification)

**System health:**
- Atlas Memory daemon running continuously (6788+ events captured)
- Email notification daemon working reliably

**Issues observed:**
- Research task failure rate still 57% (needs improvement)
- Google Workspace OAuth recurring expiry now fully mitigated with direct API + auto-refresh

**Self-awareness metrics:**
- Health score: 47.8/100 (needs attention)
- Strengths: coding (92% success), test (100%)
- Weaknesses: research (29% success), 11 approach corrections
