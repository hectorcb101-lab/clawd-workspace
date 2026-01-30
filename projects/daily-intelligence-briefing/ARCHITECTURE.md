# Daily Intelligence Briefing System

**Status:** Design Complete, Ready for Implementation
**Created:** 2026-01-25 20:39 UTC
**Type:** Real Engineering Project (not UI decoration)

---

## Problem Statement

**Friction:** Every morning I manually check:
- Email (important messages, action items)
- Calendar (today's schedule, prep needed)
- News (relevant topics I care about)
- Weather (affects plans)
- Tasks (what's blocked, what's due)

This takes 20-30 minutes and I miss things.

**Desired outcome:** Wake up to a comprehensive briefing that:
- Surfaces what matters
- Identifies action items
- Highlights risks/blockers
- Gets smarter over time

---

## Solution Overview

An automated system that:
1. **Gathers** information from multiple sources (email, calendar, news, weather, tasks)
2. **Analyzes** for relevance and urgency
3. **Synthesizes** into a personalized briefing
4. **Delivers** at the right time via preferred channel
5. **Learns** from feedback to improve over time

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Daily Briefing System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Cron      │  │  Gatherers  │  │     State Store         │ │
│  │  Trigger    │─▶│  (parallel) │─▶│  (persistent JSON)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                          │                      │               │
│                          ▼                      ▼               │
│                   ┌─────────────┐        ┌─────────────┐       │
│                   │  Analyzer   │◀──────▶│   Memory    │       │
│                   │ (relevance) │        │  (prefs)    │       │
│                   └─────────────┘        └─────────────┘       │
│                          │                                      │
│                          ▼                                      │
│                   ┌─────────────┐                               │
│                   │ Synthesizer │                               │
│                   │ (briefing)  │                               │
│                   └─────────────┘                               │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Deliverer  │─▶│  Channel    │  │    Feedback Loop        │ │
│  │             │  │  (WhatsApp) │◀─│  (corrections/prefs)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Cron triggers at 7:00 AM local time
2. Spawn parallel sub-agents for gathering:
   - Email gatherer → email_summary.json
   - Calendar gatherer → calendar_summary.json
   - News gatherer → news_summary.json
   - Weather gatherer → weather_summary.json
   - Tasks gatherer → tasks_summary.json
3. Wait for all gatherers (max 5 min timeout)
4. Analyzer reads summaries + user preferences
5. Synthesizer creates personalized briefing
6. Deliverer sends to WhatsApp/Telegram
7. Track delivery, await feedback
8. Update preferences based on feedback
```

---

## Component Specifications

### 1. Cron Trigger

**Implementation:**
```bash
clawdbot cron add \
  --name "morning-briefing" \
  --cron "0 7 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --model opus \
  --message "Execute daily briefing workflow. Read projects/daily-intelligence-briefing/WORKFLOW.md" \
  --deliver \
  --channel telegram
```

### 2. Gatherers (Sub-Agents)

Each gatherer is a spawned sub-agent with specific focus:

**Email Gatherer:**
```javascript
sessions_spawn({
  task: `Analyze emails from last 24 hours:
    1. Identify urgent/action-required emails
    2. Summarize key threads
    3. Flag anything from VIP senders
    4. Output to projects/daily-intelligence-briefing/state/email_summary.json
    
    Format: { urgent: [], actionRequired: [], threads: [], vip: [] }`,
  label: "email-gatherer",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 180
})
```

**Calendar Gatherer:**
```javascript
sessions_spawn({
  task: `Analyze calendar for today and tomorrow:
    1. List all events with times
    2. Identify prep needed
    3. Flag conflicts or tight transitions
    4. Note travel time requirements
    5. Output to projects/daily-intelligence-briefing/state/calendar_summary.json
    
    Format: { today: [], tomorrow: [], prepNeeded: [], conflicts: [] }`,
  label: "calendar-gatherer",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 120
})
```

**News Gatherer:**
```javascript
sessions_spawn({
  task: `Gather relevant news:
    1. Read user's topic preferences from ../preferences.json
    2. Search for relevant articles (max 5 per topic)
    3. Summarize key developments
    4. Output to projects/daily-intelligence-briefing/state/news_summary.json
    
    Topics: ${JSON.stringify(preferences.newsTopics)}
    Format: { topics: { [topic]: [{ headline, summary, source }] } }`,
  label: "news-gatherer",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 180
})
```

**Weather Gatherer:**
```javascript
sessions_spawn({
  task: `Get weather information:
    1. Current conditions
    2. Today's forecast
    3. Tomorrow's forecast
    4. Any alerts or unusual conditions
    5. Output to projects/daily-intelligence-briefing/state/weather_summary.json
    
    Location: ${preferences.location}
    Format: { current: {}, today: {}, tomorrow: {}, alerts: [] }`,
  label: "weather-gatherer",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 60
})
```

**Tasks Gatherer:**
```javascript
sessions_spawn({
  task: `Review task status:
    1. Due today
    2. Overdue
    3. Blocked (and why)
    4. Recently completed (for context)
    5. Output to projects/daily-intelligence-briefing/state/tasks_summary.json
    
    Format: { dueToday: [], overdue: [], blocked: [], completed: [] }`,
  label: "tasks-gatherer",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 120
})
```

### 3. Analyzer

Reads all summaries and user preferences to identify:
- What's most important
- What needs action
- What's risky/blocked
- What can be skipped

**Relevance scoring:**
```javascript
function scoreRelevance(item, preferences) {
  let score = 0
  
  // Urgency
  if (item.urgent) score += 50
  if (item.deadline === 'today') score += 30
  
  // Sender importance
  if (preferences.vipSenders.includes(item.from)) score += 40
  
  // Topic relevance
  if (preferences.priorityTopics.includes(item.topic)) score += 20
  
  // Historical engagement
  score += preferences.engagementHistory[item.type] || 0
  
  return score
}
```

### 4. Synthesizer

Creates the final briefing:

```markdown
# Good Morning, Finn 🌅

## Weather
**Today:** 72°F, partly cloudy. Perfect for outdoor lunch.
**Tomorrow:** Rain expected after 3pm. Plan accordingly.

## Today's Schedule
- **9:00 AM** - Team standup (15 min)
- **10:30 AM** - Client call with Acme Corp
  ⚠️ Prep: Review Q4 numbers (attached summary)
- **2:00 PM** - Deep work block
- **5:00 PM** - Gym (don't skip!)

## Action Required
1. **Reply to Sarah's email** - Contract question, she's waiting
2. **Approve PR #142** - John pinged twice
3. **Review budget doc** - Due EOD

## Blocked Tasks
- **API integration** - Waiting on credentials from DevOps (3 days)
  → Consider escalating?

## News Highlights
**AI/Tech:**
- Anthropic releases new model capabilities
- OpenAI announces enterprise features

## Quick Stats
- Unread emails: 23 (3 urgent)
- Tasks due today: 4
- Meetings: 3 (2.5 hours total)

---
*Reply with feedback or "skip [section]" to customize*
```

### 5. Deliverer

Sends briefing via configured channel:

```javascript
// Delivery configuration
const deliveryConfig = {
  channel: preferences.deliveryChannel || 'telegram',
  time: preferences.deliveryTime || '07:00',
  format: preferences.briefingFormat || 'full',
  includeAttachments: preferences.includeAttachments || false
}

// Send with retry
async function deliverBriefing(briefing, config) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      await message({
        action: 'send',
        channel: config.channel,
        message: briefing
      })
      
      logDelivery({ success: true, timestamp: Date.now() })
      return
    } catch (error) {
      logError(error)
      await sleep(Math.pow(2, attempt) * 1000)
    }
  }
  
  // Fallback
  await notifyFallback("Briefing delivery failed")
}
```

### 6. Feedback Loop

Learn from user interactions:

**Explicit feedback:**
```
User: "Skip weather section"
→ Update preferences.skipSections = [..., 'weather']

User: "Add [topic] to news"
→ Update preferences.newsTopics = [..., topic]

User: "Mark [sender] as VIP"
→ Update preferences.vipSenders = [..., sender]
```

**Implicit feedback:**
```javascript
// Track which sections user engages with
function trackEngagement(section, action) {
  const stats = loadStats()
  
  stats.sections[section] = stats.sections[section] || { views: 0, actions: 0 }
  stats.sections[section].views++
  if (action) stats.sections[section].actions++
  
  saveStats(stats)
}

// Adjust section ordering based on engagement
function optimizeSectionOrder(stats) {
  return Object.entries(stats.sections)
    .sort((a, b) => b[1].actions - a[1].actions)
    .map(([section]) => section)
}
```

---

## State Management

### File Structure

```
projects/daily-intelligence-briefing/
├── ARCHITECTURE.md          # This file
├── WORKFLOW.md              # Execution instructions
├── state/
│   ├── email_summary.json   # Latest email summary
│   ├── calendar_summary.json
│   ├── news_summary.json
│   ├── weather_summary.json
│   ├── tasks_summary.json
│   └── last_briefing.json   # Last generated briefing
├── preferences.json         # User preferences
├── stats/
│   ├── delivery_log.json    # Delivery history
│   ├── engagement.json      # Section engagement
│   └── feedback.json        # User corrections
└── .learnings/
    ├── LEARNINGS.md         # What we've learned
    └── ERRORS.md            # Error log
```

### Preferences Schema

```json
{
  "deliveryChannel": "telegram",
  "deliveryTime": "07:00",
  "timezone": "America/New_York",
  "briefingFormat": "full",
  "skipSections": [],
  "sectionOrder": ["weather", "calendar", "action", "blocked", "news"],
  "newsTopics": ["AI", "tech", "startups"],
  "vipSenders": ["boss@company.com", "spouse@email.com"],
  "location": "New York, NY",
  "includeAttachments": false
}
```

### Stats Schema

```json
{
  "deliveries": {
    "total": 45,
    "successful": 44,
    "failed": 1,
    "lastDelivery": "2026-01-25T12:00:00Z"
  },
  "sections": {
    "calendar": { "views": 45, "actions": 38 },
    "action": { "views": 45, "actions": 42 },
    "news": { "views": 45, "actions": 12 }
  },
  "feedback": {
    "positive": 8,
    "negative": 2,
    "adjustments": 5
  }
}
```

---

## Error Handling

### Gatherer Failures

```javascript
async function gatherWithFallback(gatherer, timeout) {
  try {
    return await withTimeout(gatherer.run(), timeout)
  } catch (error) {
    logError({
      component: gatherer.name,
      error: error.message,
      timestamp: Date.now()
    })
    
    // Return cached data if available
    const cached = loadCached(gatherer.name)
    if (cached && isRecent(cached, 24 * 60 * 60 * 1000)) {
      return { ...cached, stale: true }
    }
    
    // Return empty with error flag
    return { error: true, message: error.message }
  }
}
```

### Delivery Failures

```javascript
// Primary: Telegram
// Fallback: WhatsApp
// Last resort: Email
const deliveryChain = ['telegram', 'whatsapp', 'email']

async function deliverWithFallback(briefing) {
  for (const channel of deliveryChain) {
    try {
      await deliver(briefing, channel)
      return { success: true, channel }
    } catch (error) {
      logError({ channel, error })
    }
  }
  
  // All failed - log for manual review
  await logCritical("All delivery methods failed")
  return { success: false }
}
```

### Partial Success Handling

```javascript
function synthesizeBriefing(summaries) {
  const briefing = []
  
  for (const [section, summary] of Object.entries(summaries)) {
    if (summary.error) {
      briefing.push(`## ${section}\n⚠️ Unavailable - ${summary.message}`)
    } else if (summary.stale) {
      briefing.push(`## ${section} (cached)\n${formatSection(summary)}`)
    } else {
      briefing.push(`## ${section}\n${formatSection(summary)}`)
    }
  }
  
  return briefing.join('\n\n')
}
```

---

## Self-Improvement Mechanisms

### 1. Section Relevance Learning

Track which sections lead to actions:
```javascript
// If user always skips weather, auto-minimize it
// If user always acts on calendar items, prioritize them
```

### 2. News Topic Refinement

Track which news items get engagement:
```javascript
// If AI articles get clicks, weight AI higher
// If politics gets skipped, reduce politics
```

### 3. Timing Optimization

Track when briefing is read:
```javascript
// If briefing sent at 7am is read at 8am consistently
// Suggest moving to 7:45am
```

### 4. Format Evolution

A/B test briefing formats:
```javascript
// Try bullet points vs prose
// Try emoji vs no emoji
// Track engagement and adapt
```

---

## Implementation Roadmap

### Phase 1: Minimum Viable System (Week 1)
- [ ] Set up cron trigger
- [ ] Implement calendar gatherer
- [ ] Implement email gatherer (subject lines only)
- [ ] Basic synthesizer
- [ ] Telegram delivery
- [ ] Manual testing

### Phase 2: Full Gathering (Week 2)
- [ ] Add weather gatherer
- [ ] Add news gatherer
- [ ] Add tasks gatherer
- [ ] Implement preferences file
- [ ] Add section customization

### Phase 3: Reliability (Week 3)
- [ ] Add error handling for each gatherer
- [ ] Implement delivery fallback chain
- [ ] Add caching for stale data
- [ ] Set up logging and monitoring
- [ ] Add partial success handling

### Phase 4: Learning (Week 4)
- [ ] Implement engagement tracking
- [ ] Add feedback processing
- [ ] Create preference adjustment logic
- [ ] Build section ordering optimization
- [ ] Add self-improvement reports

### Phase 5: Polish (Week 5)
- [ ] Optimize briefing format
- [ ] Add weekend vs weekday variants
- [ ] Implement holiday awareness
- [ ] Add vacation mode
- [ ] Documentation and handoff

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Delivery success rate | >99% | - |
| Briefing read rate | >90% | - |
| Action items actioned | >70% | - |
| User satisfaction | >4/5 | - |
| False urgency rate | <5% | - |
| Time saved (self-reported) | >15 min/day | - |

---

## Why This Is Engineering, Not Decoration

| Engineering Aspect | Implementation |
|--------------------|----------------|
| **Solves real problem** | Saves 20-30 min daily manual checking |
| **Persistent state** | Preferences, stats, cache in JSON files |
| **Runs autonomously** | Cron trigger at 7am, no human needed |
| **Handles failures** | Fallback chain, cached data, partial success |
| **Self-improving** | Engagement tracking, preference learning |
| **Composable** | Each gatherer is independent, synthesizer combines |
| **Observable** | Delivery logs, error logs, stats tracking |
| **Testable** | Each component has clear inputs/outputs |

**No mention of gradients, glassmorphism, or pretty colors. Just utility.**
