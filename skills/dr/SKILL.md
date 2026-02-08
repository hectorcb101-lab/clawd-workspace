---
name: dr
description: Deep Research via Exa AI (~3-5 min). Multi-source synthesis on any topic. Saves findings to Obsidian. Use when Finn sends /dr <topic>.
metadata: {"clawdbot":{"emoji":"🔬"}}
---

# DR — Deep Research

When Finn triggers `/dr <topic>`, run a thorough multi-source research pass using Exa AI and deliver a synthesised report.

## Workflow

### 1. Acknowledge

Tell Finn you're on it. Give a one-liner on what you're researching and estimated time (~3-5 min).

### 2. Run Exa Deep Research

Start an async deep research task using the pro model:

```
mcporter call exa.deep_researcher_start \
  instructions="<research instructions based on Finn's topic>" \
  model="exa-research-pro"
```

While waiting, supplement with targeted searches:

```
mcporter call exa.web_search_advanced_exa \
  query="<topic>" \
  category="research paper" \
  --enable-summary true \
  --enable-highlights true
```

```
mcporter call exa.deep_search_exa \
  objective="<natural language research question>"
```

### 3. Poll for Results

Check the deep research task until complete:

```
mcporter call exa.deep_researcher_check taskId="<task-id>"
```

Repeat every 15-20 seconds until `status=completed`.

### 4. Synthesise

Combine all sources into a structured report:

- **TL;DR** — 2-3 sentence executive summary
- **Key Findings** — numbered list of the most important points
- **Sources & Evidence** — what the data actually says, with citations
- **Gaps & Caveats** — what's missing, conflicting, or uncertain
- **Finn's Take** — what's actionable or interesting for Finn specifically

Don't just dump raw results. Synthesise, compare sources, flag contradictions.

### 5. Save to Obsidian

Save the report to Finn's vault:

```
obsidian-cli create "Research/DR - <Topic Title>" --content "<report>"
```

Use the format: `Research/DR - <Topic> (YYYY-MM-DD)`

### 6. Deliver

Reply to Finn in chat with the synthesised report. Keep it conversational — this is Telegram, not a journal submission. Link to the Obsidian note for the full version if the report is long.

## Search Strategy

Use multiple Exa tools for coverage:

| Tool | Purpose |
|------|---------|
| `deep_researcher_start` (pro) | Primary — comprehensive multi-source synthesis |
| `web_search_advanced_exa` | Targeted — specific domains, date ranges, categories |
| `deep_search_exa` | Supplementary — natural language follow-up questions |
| `company_research_exa` | If topic involves a company |
| `crawling_exa` | Extract full content from key URLs found |

## Rules

- **Always use `exa-research-pro`** — this is deep research, not a quick scan
- **Cite sources** — include URLs for key claims
- **Save to Obsidian** — every DR gets persisted
- **Be opinionated** — Finn wants analysis, not a Wikipedia dump
- **~3-5 minutes** is the target. Don't rush, don't goldplate
