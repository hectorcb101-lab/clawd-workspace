# HEARTBEAT.md

## 🔨 Active Build Check
If `ACTIVE_BUILD.md` exists and status is ACTIVE:
- Check if there's idle time to make progress
- If Finn isn't actively chatting, consider continuing the build
- Small incremental progress is fine during heartbeats

## 📝 Event Log Sync
Run periodically to capture new events:
```bash
cd ~/clawd/projects/atlas-memory-evolution/src && python3 conversation_ingester.py 2>/dev/null | tail -5
```
This ingests daily logs and new conversations into the event system.

## Context Monitoring (Every Heartbeat)
Check session context usage via `session_status`.
- **75%+:** Warn Finn proactively
- **90%+:** Critical alert, suggest model switch or new session
- Log to `memory/usage-tracking.md`

## Memory Daemon Health Check
Verify Atlas Memory daemon is running:
```bash
atlas-daemon status
```
- If not running: `atlas-daemon start`
- Check stats: `atlas-mem stats`

## Self-Awareness Check
Run insight check for proactive alerts:
```bash
~/clawd/bin/atlas-self check
```
- If critical insights: surface to Finn
- Periodically run `atlas-self analyze` for health score
- Log outcomes after significant tasks

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

## Proactive Checks (Rotate through these)

### Calendar Awareness
Check upcoming events in next 24-48h. If important meeting approaching:
- Surface relevant context from memory
- Check if prep materials exist
- Alert Finn if < 2h away

### Email Triage (via hectorcb101@gmail.com)
Check for urgent unread messages. Flag anything that:
- Is from Finn
- Contains deadlines
- Requires immediate action

### Pattern Detection
Track and note:
- Commands I run repeatedly (document if 3+ times)
- Errors I hit multiple times (fix the root cause)
- Files I access together (note the pattern)

### Proactive Outreach Rules
Reach out if:
- Important email arrived
- Calendar event < 2h away
- Found something interesting worth sharing
- Been > 8h since any interaction (during waking hours)

Stay quiet if:
- Late night (23:00-08:00 London time) unless urgent
- Finn clearly busy
- Nothing new since last check


## Test Section

This is a test modification to verify the system works.
