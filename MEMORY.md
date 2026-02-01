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
- **Weather:** London forecast for the day
- **Markets:** SPY, QQQ, BTC, ETH, Big Tech (NVDA, MSFT, GOOGL, META, AAPL, TSLA)
- **Prediction Markets:** Polymarket trending + key categories (Fed, geopolitics, tech/crypto)
- **X/Twitter Sentiment:** What people are saying about markets (needs bird auth setup)
- **Geopolitical News:** Ukraine, major world events, Trump foreign policy
- **AI News:** OpenAI, Anthropic, DeepMind, industry moves, funding
- **Atlas Analysis:** My opinions/takes on each section

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

### Google Workspace OAuth
- Tokens expire periodically (~weekly?)
- Auth for hectorcb101@gmail.com only
- wfmckie@gmail.com not set up (Finn's actual email)
- When it fails: refer to `skills/google-workspace-auth/SKILL.md`
- **Flagged again:** 2026-02-01

### ClawdHub Search
- `clawdhub search` times out consistently
- Workaround: Browse clawdhub.com directly
- `clawdhub install <name>` still works

### MCP Batch Operations
- Connection drops after first call in bash subprocess
- Workaround: One call at a time, or use Node.js script to maintain connection

---

*Update this file with significant events, lessons, and context worth keeping long-term.*
