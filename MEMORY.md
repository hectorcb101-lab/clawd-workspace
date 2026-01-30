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

### Daily Intelligence Briefing (9 AM UTC)
- **Weather:** London forecast for the day
- **Markets:** SPY, QQQ, BTC, ETH, Big Tech (NVDA, MSFT, GOOGL, META, AAPL, TSLA)
- **Prediction Markets:** Polymarket trending + key categories (Fed, geopolitics, tech/crypto)
- **X/Twitter Sentiment:** What people are saying about markets (needs bird auth setup)
- **Geopolitical News:** Ukraine, major world events, Trump foreign policy
- **AI News:** OpenAI, Anthropic, DeepMind, industry moves, funding
- **Atlas Analysis:** My opinions/takes on each section

---

*Update this file with significant events, lessons, and context worth keeping long-term.*
