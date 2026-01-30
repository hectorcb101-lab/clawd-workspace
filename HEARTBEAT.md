# HEARTBEAT.md

## Context Monitoring (Every Heartbeat)
Check session context usage via `session_status`.
- **75%+:** Warn Finn proactively
- **90%+:** Critical alert, suggest model switch or new session
- Log to `memory/usage-tracking.md`

## Periodic Checks

### Anthropic OAuth Ban Monitor
Check X for reports of Anthropic banning accounts for using OAuth with Clawdbot/third-party tools.
If bans are confirmed, alert Finn immediately.
Search: `clawdbot banned anthropic oauth`

### Google Workspace Health Check (Weekly)
Test that Google Workspace credentials are still valid by calling a simple read operation.
If auth fails, alert Finn and refer to `skills/google-workspace-auth/SKILL.md` to re-authenticate.
```bash
mcporter call google-workspace.list_calendars user_google_email="hectorcb101@gmail.com"
```
