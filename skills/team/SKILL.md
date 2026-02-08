---
name: team
description: Decompose any task into parallel sub-agents for faster execution. Use when Finn sends a complex task that benefits from splitting into independent workstreams.
metadata: {"clawdbot":{"emoji":"\ud83d\udc65"}}
---

# Team — Multi-Agent Task Orchestration

When Finn triggers `/team <task>`, decompose the task into 2-5 sub-agents and execute them via `sessions_spawn`.

## Workflow

### 1. Analyse & Decompose

Read Finn's task carefully. Break it into **2-5 independent sub-tasks**. Each sub-task must be:

- **Self-contained** — a fresh agent with no shared context must be able to complete it
- **Non-overlapping** — no two sub-agents should touch the same files
- **Clearly scoped** — specific deliverable, not vague

If the task is too small to split (single file edit, quick lookup), just do it inline and tell Finn you handled it directly.

### 2. Choose Orchestration Pattern

Pick the right pattern based on task structure:

| Pattern | When | Example |
|---------|------|---------|
| **Fan-out (parallel)** | Sub-tasks are independent | Research 3 topics simultaneously |
| **Sequential chain** | Output of one feeds next | Research → Plan → Implement |
| **Background** | Non-blocking side work | Audit codebase while building feature |

**Default to fan-out (parallel)** unless there are clear dependencies between sub-tasks.

### 3. Choose Model Per Sub-Agent

| Use | Model |
|-----|-------|
| Complex reasoning, architecture, code review | `anthropic/claude-opus-4-6` |
| Routine tasks, research, simple code, docs | `anthropic/claude-sonnet-4-5` |

When in doubt, use Sonnet — it's faster and cheaper. Reserve Opus for tasks that genuinely need deeper reasoning.

### 4. Spawn Sub-Agents

Use `sessions_spawn` for each sub-task. Write **complete, specific task definitions**:

```
sessions_spawn({
  task: "<full task definition — see template below>",
  label: "<short-kebab-label>",
  model: "anthropic/claude-sonnet-4-5",
  cleanup: "delete"
})
```

**Task definition template** (include all four sections):

```
What: <specific deliverable>
Where: <file paths, directories, or URLs to work with>
Constraints: <rules, patterns to follow, things to avoid>
Done when: <concrete completion criteria>
```

**Cleanup rules:**
- `cleanup: "delete"` — one-off tasks (research, analysis, reports)
- `cleanup: "keep"` — ongoing work, code changes you want to review later

### 5. Report Back

After spawning all sub-agents, tell Finn:

1. How many agents you dispatched
2. What each one is doing (one-liner per agent)
3. Which model each is using
4. Estimated completion: "quick" (< 2 min) or "a few minutes" (2-10 min)

When sub-agents announce their results, aggregate and deliver a **unified summary** to Finn. Don't just relay raw output — synthesise it.

## Example

Finn says: `/team research the latest Opus 4.6 benchmarks and compare with Sonnet 4.5`

**Decomposition:**

1. **Research Opus 4.6 benchmarks** — find official benchmarks, third-party evals, real-world reports
2. **Research Sonnet 4.5 benchmarks** — same scope for Sonnet
3. **Comparison & synthesis** — wait for 1 & 2, then produce comparative analysis

**Execution:**

```
sessions_spawn({
  task: "What: Find comprehensive benchmarks for Claude Opus 4.6\nWhere: Web search — official Anthropic announcements, arxiv papers, third-party eval sites (lmsys, artificial-analysis)\nConstraints: Only credible sources. Include numbers, not just claims.\nDone when: You have a structured list of benchmarks with scores across coding, reasoning, math, and general knowledge",
  label: "research-opus",
  model: "anthropic/claude-sonnet-4-5",
  cleanup: "delete"
})

sessions_spawn({
  task: "What: Find comprehensive benchmarks for Claude Sonnet 4.5\nWhere: Web search — official Anthropic announcements, arxiv papers, third-party eval sites\nConstraints: Only credible sources. Include numbers, not just claims.\nDone when: You have a structured list of benchmarks with scores across coding, reasoning, math, and general knowledge",
  label: "research-sonnet",
  model: "anthropic/claude-sonnet-4-5",
  cleanup: "delete"
})
```

Then aggregate results into a comparison table for Finn.

## Rules

- **Max 5 sub-agents** per `/team` invocation — keep it focused
- **Never spawn for trivial tasks** — if it takes < 30 seconds, just do it
- **No file overlap** between parallel agents — this causes merge conflicts
- **Pass complete context** — sub-agents have no memory of Finn's conversation
- **Label clearly** — use descriptive kebab-case labels like `research-opus`, `impl-backend`, `audit-security`
- **Report immediately** after spawning — don't make Finn wait in silence
