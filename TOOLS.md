# TOOLS.md — Quick Reference

This is a cheat sheet, not a manual. For detailed tool docs, read the relevant SKILL.md.

---

## Accounts

| Service | Account | Notes |
|---------|---------|-------|
| Google | hectorcb101@gmail.com | Atlas's account. OAuth tokens at `~/.google_workspace_mcp/credentials/` |
| GitHub | hectorcb101-lab | Full repo access via `gh` CLI |
| GitHub (Finn) | fmckie | PAT in `~/.clawdbot/.env` |
| Telegram | Bot | Token in config |
| X/Twitter | @finlay_mckie (ID: 3235956615) | Cookies in env vars (X_AUTH_TOKEN, X_CT0) |

**Finn:** wfmckie@gmail.com · Telegram ID 6047368408

---

## Atlas OS CLIs

All in `~/clawd/bin/` (in PATH).

| CLI | Purpose | Key Commands |
|-----|---------|-------------|
| `atlas-daemon` | Memory capture daemon | `status`, `start`, `stop`, `logs` |
| `atlas-mem` | Memory search & storage | `search "topic"`, `remember "fact"`, `stats`, `sync` |
| `atlas-self` | Self-awareness & patterns | `log-outcome`, `log-correction`, `analyze`, `strengths`, `weaknesses`, `blind-spots` |
| `atlas-mod` | Self-modification | `propose`, `list`, `pending`, `apply`, `rollback`, `from-correction`, `stats` |
| `atlas-judge` | Judgment & principles | `consult "situation"`, `apply`, `outcome`, `learn`, `effectiveness`, `stats` |
| `atlas-bus` | Event bus | `correction`, `outcome`, `judgment`, `instruction`, `stats`, `tail` |
| `atlas-eval` | Evaluation | `run`, `scenarios`, `single`, `history`, `compare` |
| `atlas-quality` | Quality assessment | `score`, `judge`, `ingest`, `stats` |
| `atlas-train` | Training data | `correction`, `instruction`, `outcome`, `stats`, `export` |
| `atlas-llm` | LLM interface | `config`, `list`, `test`, `generate`, `embed`, `models` |
| `atlas-finetune` | Fine-tuning pipeline | `stats`, `export`, `prepare`, `list`, `presets` |

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/atlas_email.py` | Send email as "Atlas" with branded template |
| `scripts/google` | Google Workspace CLI (gmail-search, gmail-read, gmail-labels, calendar) |
| `scripts/check_emails.py` | Direct Gmail API check (fallback if mcporter fails) |
| `scripts/email_notify_daemon.py` | Standalone email notification daemon (systemd) |

---

## Email

**Always use:** `python3 ~/clawd/scripts/atlas_email.py`
```bash
python3 ~/clawd/scripts/atlas_email.py \
  --to "wfmckie@gmail.com" \
  --subject "Subject" \
  --body "$(cat email.html)"
```
- Template (Finn): `templates/atlas-email-final.html` — `{{ATLAS_LOGO}}` auto-embeds
- Template (External): `templates/atlas-email-external.html` — professional, "PA to Finn McKie"
- **Never** use mcporter for sending email (no display name support)

**When auth breaks** (invalid_grant): Copy refresh token from `~/.google_workspace_mcp/credentials/hectorcb101@gmail.com.json` to `~/.workspace-mcp/token_hectorcb101@gmail.com.json`

---

## Search & Research

- **Primary:** Exa Search via `mcporter call exa.web_search_exa` (or exa-search skill)
- **Code/APIs:** `mcporter call exa.get_code_context_exa`
- **Company intel:** `mcporter call exa.company_research_exa`
- **Fallback:** `web_fetch` for URLs, `browser` for JS-heavy sites
- **Deep research:** See `skills/dr/` (deep dive) and `skills/ex/` (exhaustive)

---

## Image Generation

**Primary:** Nanobanana (Gemini Imagen) via mcporter
- `mcporter call nanobanana.generate_image` — general images
- `mcporter call nanobanana.generate_icon` — avatars, app icons
- `mcporter call nanobanana.generate_diagram` — flowcharts, architecture
- Output: `~/clawd/config/nanobanana-output/`

---

## Voice

- Voice: `en-GB-RyanNeural` (echo, warm male)
- Speed: 1.25x
- Model: tts-1

---

## Obsidian Vault

**Location:** `~/clawd/obsidian-vault/`
**Always push after edits:**
```bash
cd ~/clawd/obsidian-vault && git add -A && git commit -m "msg" && git push
```

---

## Notion

- Workspace: Finn's personal
- API key: `~/.config/notion/api_key`
- MSc AI 2026: `2fb6833e-c12d-80bf-9339-ff27ec4be644`
- Assignments DB: `2fb6833e-c12d-8167-8910-df1c19219133`

---

## Google Workspace Auth

When mcporter Google calls fail with auth errors:
1. See `skills/google-workspace-auth/SKILL.md`
2. Requires SSH port forwarding for OAuth flow
3. Alert Finn if it needs re-auth

---

## Email Notification Daemon

Standalone systemd service — polls Gmail, sends Telegram alerts.
```bash
sudo systemctl status email-notify-daemon
sudo systemctl restart email-notify-daemon
journalctl -u email-notify-daemon -f
```

---

## Key Paths

| What | Where |
|------|-------|
| Workspace | `~/clawd/` |
| Skills (npm) | `~/.npm-global/lib/node_modules/clawdbot/skills/` |
| Skills (custom) | `~/clawd/skills/` |
| OpenClaw docs | `~/.npm-global/lib/node_modules/openclaw/docs/` |
| OpenClaw config | `~/.clawdbot/clawdbot.json` |
| Memory | `~/clawd/memory/` |
| Research | `~/clawd/research/` |
| Projects | `~/clawd/projects/` |
| Templates | `~/clawd/templates/` |
| Learnings | `~/clawd/.learnings/` |
