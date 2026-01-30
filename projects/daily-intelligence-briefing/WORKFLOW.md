# Daily Briefing Workflow

**Execution Instructions for Cron Job**

---

## Trigger Conditions

This workflow runs:
- Daily at 7:00 AM (configured timezone)
- Can be manually triggered with `/briefing now`
- Can be scheduled for later with `/briefing at 9am`

---

## Execution Steps

### Step 1: Load Configuration

```
1. Read preferences.json for user settings
2. Read state/last_briefing.json for previous run info
3. Verify all required integrations are accessible
```

### Step 2: Spawn Gatherers

Spawn these sub-agents **in parallel**:

1. **Email Gatherer** (label: `email-gatherer`)
   - Check inbox for last 24 hours
   - Identify urgent/action-required
   - Output: `state/email_summary.json`

2. **Calendar Gatherer** (label: `calendar-gatherer`)
   - Get today + tomorrow events
   - Identify prep requirements
   - Output: `state/calendar_summary.json`

3. **News Gatherer** (label: `news-gatherer`)
   - Search topics from preferences
   - Summarize top stories
   - Output: `state/news_summary.json`

4. **Weather Gatherer** (label: `weather-gatherer`)
   - Get local weather
   - Check for alerts
   - Output: `state/weather_summary.json`

5. **Tasks Gatherer** (label: `tasks-gatherer`)
   - Check task system
   - Identify blockers
   - Output: `state/tasks_summary.json`

**Timeout:** 5 minutes total for all gatherers

### Step 3: Wait and Collect

```
1. Poll for sub-agent completion (check announce messages)
2. After timeout, proceed with available data
3. Log any missing/failed gatherers to .learnings/ERRORS.md
```

### Step 4: Analyze and Synthesize

```
1. Read all available *_summary.json files
2. Apply relevance scoring from preferences
3. Order sections by user preference
4. Generate briefing markdown
5. Save to state/last_briefing.json
```

### Step 5: Deliver

```
1. Send briefing to configured channel
2. Log delivery to stats/delivery_log.json
3. Update stats/engagement.json
```

### Step 6: Handle Feedback

Listen for responses like:
- "Skip [section]" → Update preferences.skipSections
- "Add [topic]" → Update preferences.newsTopics
- "VIP [sender]" → Update preferences.vipSenders
- "Great briefing" → Log positive feedback
- "This was wrong" → Log to learnings

---

## Failure Handling

### If a gatherer fails:
1. Log error to .learnings/ERRORS.md
2. Check for cached data (< 24 hours old)
3. If cached exists, use with "stale" warning
4. If no cache, include "[Section] unavailable" note

### If delivery fails:
1. Try fallback channel (telegram → whatsapp → email)
2. If all fail, log critical error
3. Manual review on next heartbeat

### If synthesis fails:
1. Send simple "Briefing generation failed" message
2. Include what data was gathered
3. Log for debugging

---

## Quick Commands

**Force immediate briefing:**
```
/briefing now
```

**Schedule briefing:**
```
/briefing at 9am
```

**Skip today's briefing:**
```
/briefing skip
```

**Customize:**
```
/briefing skip weather
/briefing add topic: crypto
/briefing vip: boss@company.com
```

---

## State Files

| File | Purpose | Format |
|------|---------|--------|
| `preferences.json` | User settings | JSON |
| `state/*_summary.json` | Gatherer outputs | JSON |
| `state/last_briefing.json` | Previous briefing | JSON |
| `stats/delivery_log.json` | Delivery history | JSON array |
| `stats/engagement.json` | Section usage | JSON |
| `.learnings/ERRORS.md` | Error log | Markdown |
