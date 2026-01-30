# Research System - Configuration

## Depth Tiers

### Quick Scan (QS)
**Trigger:** "QS on X" or "quick scan X"
**Use case:** Daily checks, staying current, quick answers

| Setting | Value |
|---------|-------|
| Sources | 5-8 |
| Types | News (Exa), X hot takes |
| Academic | No |
| Time | ~60 seconds |

**Output:**
- 3-5 bullet summary
- Top 3 links
- One-liner verdict
- Tables where helpful

**Follow-up:** None (one-shot)
**Save:** No (chat only)

---

### Deep Dive (DD)
**Trigger:** "DD on X" or "deep dive X"
**Use case:** Learning, MSc prep, genuine understanding

| Setting | Value |
|---------|-------|
| Sources | 15-20 |
| Types | News, blogs, academic papers, tutorials, X experts |
| Academic | Yes |
| Time | ~3-5 minutes |

**Output:**
- Executive summary (5-7 bullets)
- Sections: Key Findings → Best Resources → Learning Path → Expert Takes
- Comparison tables where relevant
- Source quality ratings

**Follow-up:** Interactive ("Want me to expand on any section?")
**Save:** 
- Markdown to `/research/briefs/`
- Auto-sync to Obsidian: `~/obsidian-vault/Research/[Category]/`

**Obsidian Categories:**
- `AI-ML/` - AI, machine learning, models
- `Quantum/` - Quantum computing, QML
- `Space/` - Space exploration, astrophysics
- `Finance/` - Quant trading, markets, fintech
- `Tech/` - General technology, tools, frameworks
- `Academic/` - MSc related, papers, coursework
- `Other/` - Uncategorised

---

### Exhaustive (EX)
**Trigger:** "EX on X" or "exhaustive X"
**Use case:** Mastery goals, major decisions, comprehensive understanding

| Setting | Value |
|---------|-------|
| Sources | 30+ (parallel agents) |
| Types | All sources across 5 parallel agents |
| Academic | Yes (dedicated agent) |
| Time | ~10-15 minutes |

**Parallel Agents:**
1. News & recent developments
2. Academic papers & research
3. Tutorials, courses, learning resources
4. X/social sentiment & expert opinions
5. Tools, frameworks, practical implementations

**Output:**
- Executive summary (1 page)
- Deep sections from each agent
- Comparison tables
- Complete source list with priority ranking:
  - 🔴 Read first (essential)
  - 🟡 Read later (valuable)
  - 🟢 Reference (keep for later)
- Key questions to explore

**Follow-up:** Ongoing weekly tracking
- Monitor topic weekly
- Alert on significant developments
- Monthly digest option
- "Stop tracking X" to end

**Save:**
- Full report to Obsidian: `~/obsidian-vault/Research/[Category]/`
- Email to wfmckie@gmail.com (HTML formatted)
- Google Sheet if data is tabular (Atlas decides, or on instruction)

---

## Obsidian Integration

**Vault location:** `~/obsidian-vault/` (configure if different)
**Research folder:** `Research/`

**File naming:** `YYYY-MM-DD_[topic-slug].md`
**Frontmatter:**
```yaml
---
type: research
tier: [QS|DD|EX]
topic: [topic name]
category: [category]
date: YYYY-MM-DD
status: [complete|tracking]
tags: [auto-generated]
---
```

---

## Tracking System (EX only)

**Active tracking stored in:** `/research/tracking.json`

```json
{
  "topics": [
    {
      "name": "quantum ML",
      "category": "Quantum",
      "started": "2026-01-29",
      "frequency": "weekly",
      "lastCheck": "2026-01-29",
      "alerts": true
    }
  ]
}
```

**Weekly check:** During heartbeat, check tracked topics for new developments.
**Alert threshold:** Significant news = notify Finn.

---

## Quick Reference

| Command | Tier | Sources | Save | Follow-up |
|---------|------|---------|------|-----------|
| QS on X | Quick Scan | 5-8 | No | None |
| DD on X | Deep Dive | 15-20 | Obsidian | Interactive |
| EX on X | Exhaustive | 30+ | Obsidian + Email + GS? | Weekly tracking |
