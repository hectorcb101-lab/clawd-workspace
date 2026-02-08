---
name: ex
description: Exhaustive Research via Exa AI (~10-15 min). Maximum-depth multi-source research with email delivery, Obsidian save, and source tracking. Use when Finn sends /ex <topic>.
metadata: {"clawdbot":{"emoji":"🔎"}}
---

# EX — Exhaustive Research

When Finn triggers `/ex <topic>`, run the most thorough research possible using Exa AI. This is the full treatment — multiple research passes, cross-referencing, email delivery, Obsidian save, and source tracking.

## Workflow

### 1. Acknowledge

Tell Finn you're launching exhaustive research. Set expectations: ~10-15 minutes, results delivered via email + Obsidian + chat summary.

### 2. Decompose the Topic

Break the research question into 3-5 sub-questions that together give complete coverage. Example:

Topic: "State of quantum computing in 2026"
- Sub-Q1: Latest hardware milestones (qubit counts, error rates, coherence)
- Sub-Q2: Software/algorithm breakthroughs
- Sub-Q3: Commercial applications and revenue
- Sub-Q4: Key players and funding landscape
- Sub-Q5: Timeline predictions from credible sources

### 3. Run Parallel Research Passes

For each sub-question, run Exa deep research:

```
mcporter call exa.deep_researcher_start \
  instructions="<sub-question with specific guidance>" \
  model="exa-research-pro"
```

Simultaneously run targeted advanced searches for each sub-question:

```
mcporter call exa.web_search_advanced_exa \
  query="<sub-question>" \
  category="research paper" \
  --enable-summary true \
  --enable-highlights true \
  --start-published-date "<recent date cutoff>"
```

Also search for:
- **Academic sources**: category `research paper`, domains `arxiv.org`, `openreview.net`, `scholar.google.com`
- **News/analysis**: category `news`, recent dates
- **Industry reports**: category `pdf`, `financial report`
- **Expert opinions**: category `personal site`, `tweet`

### 4. Poll All Tasks

Check each deep research task until all complete:

```
mcporter call exa.deep_researcher_check taskId="<task-id>"
```

### 5. Deep Crawl Key Sources

For the most important URLs found, extract full content:

```
mcporter call exa.crawling_exa url="<key-url>" maxCharacters:10000
```

Do this for 3-5 of the highest-value sources to get full context beyond snippets.

### 6. Cross-Reference & Synthesise

Build a comprehensive report with rigorous structure:

- **Executive Summary** — 3-5 sentences, the big picture
- **Key Findings by Sub-Topic** — each sub-question gets its own section with:
  - Core findings with evidence
  - Consensus vs contrarian views
  - Data points and numbers where available
- **Cross-Cutting Themes** — patterns that emerge across sub-topics
- **Source Quality Assessment** — which sources are strongest, any conflicts
- **Gaps & Open Questions** — what couldn't be answered, where more research is needed
- **Actionable Insights** — what this means for Finn specifically
- **Full Source List** — every URL used, categorised by type

### 7. Save to Obsidian

Save the full report:

```
obsidian-cli create "Research/EX - <Topic Title> (YYYY-MM-DD)" --content "<full report>"
```

### 8. Email to Finn

Send the formatted report via email using the Atlas email template:

```bash
python3 ~/clawd/scripts/atlas_email.py \
  --to wfmckie@gmail.com \
  --subject "EX Research: <Topic>" \
  --template ~/clawd/templates/atlas-email-final.html \
  --body "<formatted report>"
```

The email should be the full, well-formatted report — this is the primary deliverable.

### 9. Chat Summary

Reply to Finn on Telegram with a concise summary:
- 5-8 bullet points of the most important findings
- Note that full report is in email + Obsidian
- Flag anything surprising or time-sensitive

## Search Strategy

Maximise coverage across source types:

| Pass | Tool | Focus |
|------|------|-------|
| Primary | `deep_researcher_start` (pro) x3-5 | One per sub-question |
| Academic | `web_search_advanced_exa` | category=research paper, arxiv/openreview |
| News | `web_search_advanced_exa` | category=news, recent dates |
| Industry | `web_search_advanced_exa` | category=pdf/financial report |
| Social | `web_search_advanced_exa` | category=tweet/personal site |
| Deep crawl | `crawling_exa` | Full content from top 3-5 URLs |
| Follow-up | `deep_search_exa` | Fill gaps found during synthesis |

## Rules

- **Always use `exa-research-pro`** for all deep researcher tasks
- **Multiple passes** — minimum 3 deep research tasks, one per sub-question
- **Cross-reference** — don't trust any single source, compare across multiple
- **Email is mandatory** — EX always delivers via email with Atlas branding
- **Obsidian is mandatory** — EX always saves to vault
- **Cite everything** — full URLs for every claim
- **Be exhaustive but opinionated** — cover everything, then tell Finn what matters
- **~10-15 minutes** — take the time needed for thorough coverage
- **Track sources** — maintain a running source list throughout research
