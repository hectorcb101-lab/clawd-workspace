# Atlas OpenClaw Capabilities Audit

**Date:** 2026-02-08
**Auditor:** Sub-agent (openclaw-audit)
**Scope:** All OpenClaw docs + config vs. Atlas actual usage

---

## Executive Summary

Atlas is using maybe **30-40%** of what OpenClaw offers. The biggest gaps are in automation (cron isolation, webhooks, model overrides), session management (DM scoping, identity links, send policy), and platform features (OpenProse, Lobster, hooks, memory search, canvas). Several of these are genuine game-changers that could make Atlas significantly more autonomous and intelligent.

---

## 🔥 GAME-CHANGERS (Atlas doesn't use these and SHOULD)

### 1. Isolated Cron Jobs with Model Overrides
**What:** Cron jobs can run in isolated sessions with different models and thinking levels. Atlas could run expensive deep-analysis tasks on Opus with `--thinking high` weekly, and cheap monitoring tasks on Sonnet.

**Current state:** Atlas runs all cron jobs as main-session system events (`sessionTarget: "main"`, `wakeMode: "next-heartbeat"`). This means every cron task pollutes the main session context and uses the same model.

**Impact:** Could run a cheap Sonnet model for the daily briefing data collection, saving significant cost. Deep weekly reviews could use `--thinking high` without affecting daily work. Each isolated job gets a fresh context — no context pollution.

**Action:** Convert the Daily Intelligence Briefing to an isolated cron job with `--model sonnet` and `--announce --channel telegram --to 6047368408`. Convert Weekly Self-Review to isolated with `--model opus --thinking high`.

### 2. Webhook Ingress (`/hooks/wake` and `/hooks/agent`)
**What:** External systems can trigger Atlas via HTTP webhooks. The gateway exposes `/hooks/wake` (system event) and `/hooks/agent` (isolated agent run). Custom hook mappings can transform payloads.

**Current state:** ❌ Not configured. `hooks.enabled` is not set in config (only `hooks.internal` is set). Atlas has no webhook endpoints.

**Impact:** This is how Atlas could become event-driven rather than poll-driven. GitHub webhooks on repo pushes, external monitoring alerts, calendar change notifications — all could wake Atlas instantly instead of waiting for the next heartbeat.

**Action:** Enable `hooks.enabled: true` with a token. Wire up GitHub webhooks for repo activity. Consider wiring the atlas-daemon to trigger webhooks on significant memory events.

### 3. Gmail Pub/Sub Integration
**What:** Real-time email notifications via Google Pub/Sub → OpenClaw webhook. Emails trigger agent runs instantly instead of waiting for heartbeat polling.

**Current state:** ❌ Not used. Atlas checks email during heartbeats (polling). `hooks.presets: ["gmail"]` is not configured.

**Impact:** Instead of discovering emails 30min late during heartbeats, Atlas would process urgent emails within seconds. The gmail hook can use a cheap model (`hooks.gmail.model`) to triage, and only escalate important ones.

**Action:** Run `openclaw webhooks gmail setup --account hectorcb101@gmail.com`. Configure `hooks.gmail.model` to use a cheap model for triage.

### 4. OpenProse (Multi-Agent Workflows)
**What:** A markdown-first workflow format for orchestrating parallel sub-agent sessions with explicit control flow. `.prose` files define multi-agent pipelines.

**Current state:** ❌ Not enabled. Plugin exists but not active.

**Impact:** Atlas's morning briefing could be a `.prose` file: one agent researches markets, another checks calendar, another scans news — all in parallel, then a synthesizer merges results. Repeatable, auditable, version-controlled workflows.

**Action:** `openclaw plugins enable open-prose`. Write `.prose` files for the daily briefing pipeline, weekly review, and research tasks.

### 5. Lobster (Deterministic Workflow Runtime)
**What:** Typed workflow pipelines with approval gates and resume tokens. Chains tool calls deterministically instead of relying on LLM orchestration each time.

**Current state:** ❌ Not installed or enabled.

**Impact:** Email triage, project builds, memory consolidation — these could be deterministic pipelines instead of hoping the LLM follows the right steps each time. Approval gates make side effects explicit. Resume tokens survive context resets.

**Action:** Install Lobster CLI. Add `tools.alsoAllow: ["lobster"]` to config. Build pipelines for recurring workflows.

### 6. OpenClaw Native Memory Search (Vector)
**What:** OpenClaw has built-in vector memory search over `MEMORY.md` and `memory/*.md` with semantic embeddings. Auto-indexes on file changes.

**Current state:** ⚠️ Atlas built its own memory system (`atlas-mem`) with its own embeddings. OpenClaw's native `memory-core` plugin is likely running but Atlas never uses `openclaw memory search` or the built-in memory tools.

**Impact:** Atlas is maintaining a parallel memory infrastructure when OpenClaw already provides one. The native system auto-indexes, auto-watches files, and integrates directly with the agent's context. Could replace or supplement atlas-mem.

**Action:** Check `openclaw memory status --deep`. Compare quality with atlas-mem search. Consider using OpenClaw's native memory as the primary system and atlas-mem as a specialized layer.

### 7. Pre-Compaction Memory Flush
**What:** Before auto-compaction, OpenClaw triggers a silent agent turn that reminds the model to write durable notes to disk. Configurable via `compaction.memoryFlush`.

**Current state:** ⚠️ Likely running with defaults but Atlas hasn't tuned it. The prompts could be customized to write to Atlas's specific memory format.

**Impact:** Atlas could customize the flush prompt to write to `memory/YYYY-MM-DD.md` in its specific format, ensuring nothing is lost during compaction. Currently it's probably using the generic default.

**Action:** Configure `agents.defaults.compaction.memoryFlush.prompt` to match Atlas's memory format.

---

## ❌ UNUSED — Atlas doesn't use these at all

### 8. Heartbeat Active Hours
**What:** `heartbeat.activeHours` restricts heartbeats to specific time windows.

**Current state:** Not configured. Heartbeats run 24/7 (Atlas's AGENTS.md says "Stay quiet when: Late night 23:00-08:00" but this is an instruction to the LLM, not enforced).

**Action:** Add `activeHours: { start: "08:00", end: "23:00", timezone: "Europe/London" }` to heartbeat config.

### 9. Heartbeat Model Override
**What:** `heartbeat.model` can use a cheaper model for heartbeat runs.

**Current state:** Heartbeats use the primary model (Opus 4.6). Most heartbeats just return HEARTBEAT_OK.

**Impact:** Significant cost savings. Heartbeats that return HEARTBEAT_OK don't need Opus.

**Action:** Set `heartbeat.model: "anthropic/claude-sonnet-4-5"` — escalate to Opus only when something needs real attention.

### 10. Session Reset Configuration
**What:** `session.reset` supports daily reset, idle reset, per-type overrides (`resetByType`), and per-channel overrides (`resetByChannel`).

**Current state:** Using defaults (4 AM daily reset). No idle reset configured.

**Action:** Consider `resetByType.group: { mode: "idle", idleMinutes: 120 }` for group chats.

### 11. Session Identity Links
**What:** `session.identityLinks` maps provider-prefixed peer IDs to canonical identities so the same person shares a DM session across channels.

**Current state:** ❌ Not configured. Finn contacts Atlas via Telegram and webchat — these may have separate sessions.

**Action:** Add `session.identityLinks: { finn: ["telegram:6047368408", "webchat:..."] }`.

### 12. Send Policy
**What:** Block delivery for specific session types without listing individual IDs.

**Current state:** ❌ Not configured.

**Action:** Consider denying sends from cron sessions to prevent accidental spam: `{ action: "deny", match: { keyPrefix: "cron:" } }`.

### 13. Canvas Tool
**What:** Present HTML/web content to the user, render UI components, evaluate JavaScript, take snapshots.

**Current state:** ❌ Never used by Atlas.

**Impact:** Could present dashboards, briefing reports, interactive visualizations.

### 14. Custom Hooks (Event-Driven Automation)
**What:** Write TypeScript handlers that run on agent lifecycle events (`command:new`, `command:reset`, `gateway:startup`, `agent:bootstrap`).

**Current state:** Only bundled hooks enabled (`session-memory`, `command-logger`, `boot-md`). No custom hooks.

**Impact:** Could write hooks that trigger atlas-daemon actions on session events, auto-log corrections on `/new`, or inject dynamic context on `agent:bootstrap`.

**Action:** Create workspace hooks in `~/clawd/hooks/` for Atlas-specific automation.

### 15. BOOT.md (Gateway Startup Hook)
**What:** `boot-md` hook runs `BOOT.md` instructions when the gateway starts.

**Current state:** `boot-md` is enabled in config but no `BOOT.md` file exists in the workspace.

**Impact:** Could auto-run startup checks (daemon status, memory sync, pending tasks) every time the gateway restarts.

**Action:** Create `~/clawd/BOOT.md` with startup checklist.

### 16. LLM Task Plugin
**What:** JSON-only LLM step for workflows — structured output with schema validation, no tools exposed.

**Current state:** ❌ Not enabled.

**Impact:** Useful for classification, extraction, and structured analysis steps in Lobster pipelines.

### 17. Model Failover / Fallback Chain
**What:** `agents.defaults.model.fallbacks` defines a fallback chain when the primary model fails.

**Current state:** ❌ No fallbacks configured. If Opus goes down, Atlas goes down.

**Action:** Add `model.fallbacks: ["anthropic/claude-sonnet-4-5"]` as minimum safety net.

### 18. Diagnostics Flags
**What:** Targeted debug logging per subsystem without raising global log levels.

**Current state:** ❌ Not configured.

### 19. Agent-to-Agent Messaging
**What:** `tools.agentToAgent` enables cross-agent messaging in multi-agent setups.

**Current state:** ❌ Single agent setup — not applicable now but relevant if Atlas ever spawns specialist agents.

### 20. Broadcast Groups
**What:** Multiple agents process and respond to the same message simultaneously.

**Current state:** ❌ Not used (single agent).

### 21. `/context` and `/status` Inspection
**What:** `/context list`, `/context detail`, `/status` show exactly what's in the context window, what's being truncated, tool schema sizes, etc.

**Current state:** ❌ Atlas never self-inspects its own context usage.

**Impact:** Atlas's TOOLS.md is likely being truncated (it's huge). Knowing the exact overhead would help optimize.

---

## ⚠️ UNDERUSED — Atlas knows about these but doesn't use them well

### 22. Cron Jobs
**What:** Full-featured scheduler with one-shot, recurring, isolated sessions, model overrides, delivery routing.

**Current state:** Atlas has 5 cron jobs, all running as main-session system events. None use isolation, model overrides, or delivery routing.

**Missed features:** Isolated sessions, model/thinking overrides, announce delivery to specific channels, `--delete-after-run` for one-shots.

### 23. Sub-Agents
**What:** Background agent runs with isolated sessions, model overrides, auto-archive, concurrency control.

**Current state:** Atlas uses sub-agents but doesn't configure `subagents.model` to use cheaper models for routine tasks. `maxConcurrent` is set to 8 (good).

**Missed features:** `agents.defaults.subagents.model` could default sub-agents to Sonnet. `archiveAfterMinutes` cleanup. `runTimeoutSeconds` for safety.

### 24. Heartbeat Configuration
**What:** Heartbeat interval, target, prompt, active hours, reasoning delivery, ack threshold.

**Current state:** Using defaults (30min interval). No active hours, no model override, no custom prompt configured in OpenClaw config (Atlas relies on HEARTBEAT.md instructions instead).

### 25. TTS
**What:** Edge TTS with configurable voice, pitch, rate.

**Current state:** Configured (`en-GB-RyanNeural`, +25% rate) but rarely used proactively.

### 26. Hooks System
**What:** Event-driven automation for agent lifecycle events.

**Current state:** `session-memory`, `command-logger`, `boot-md` are enabled but Atlas doesn't leverage the hook system for custom automation.

### 27. Session Pruning
**What:** Auto-trims old tool results from in-memory context (doesn't rewrite JSONL).

**Current state:** Running with defaults. Atlas hasn't tuned pruning behavior.

### 28. Compaction
**What:** Auto-summarizes older conversation when context window fills up.

**Current state:** Running with defaults. Atlas hasn't tuned `reserveTokensFloor` or memory flush prompts.

---

## ✅ USED — Atlas already leverages these

### 29. Telegram Channel ✅
Configured and active as primary communication channel.

### 30. Workspace Files (AGENTS.md, SOUL.md, USER.md, TOOLS.md) ✅
Well-maintained and injected into every session.

### 31. Sub-Agent Spawning ✅
Atlas uses `sessions_spawn` for parallel tasks.

### 32. Cron Basic Scheduling ✅
5 active cron jobs for recurring tasks.

### 33. HEARTBEAT.md ✅
Active heartbeat checklist.

### 34. Web Search / Web Fetch ✅
Used for research tasks.

### 35. Browser Automation ✅
Available and used when needed.

### 36. File Operations (read/write/edit/exec) ✅
Core workflow.

### 37. TTS Configuration ✅
Edge TTS configured with custom voice.

### 38. Model Aliases ✅
Sonnet and Opus aliases configured.

---

## Priority Action Items (Top 5)

1. **🔥 Convert cron jobs to isolated sessions with model overrides** — Immediate cost savings and context hygiene. The daily briefing doesn't need Opus or main-session pollution.

2. **🔥 Enable webhooks + Gmail Pub/Sub** — Transform Atlas from poll-driven to event-driven. Real-time email processing instead of 30-minute delays.

3. **🔥 Set heartbeat model to Sonnet + configure active hours** — Most heartbeats return HEARTBEAT_OK. Using Opus for these is burning money.

4. **🔥 Configure model fallbacks** — Single point of failure if Opus goes down. Add Sonnet as fallback.

5. **🔥 Create BOOT.md** — Free startup automation. Gateway restart → auto-check daemon, memory, pending tasks.

---

## Cost Impact Estimate

| Change | Estimated Savings |
|--------|------------------|
| Heartbeat on Sonnet | ~60-70% of heartbeat costs |
| Daily briefing on Sonnet (isolated) | ~60% of briefing costs |
| Sub-agent default model to Sonnet | ~40-50% of sub-agent costs |
| Gmail Pub/Sub (fewer polling heartbeats) | Reduced heartbeat frequency possible |

---

## Config Changes Needed

```json5
// Add to ~/.clawdbot/clawdbot.json (or ~/.openclaw/openclaw.json)
{
  agents: {
    defaults: {
      heartbeat: {
        model: "anthropic/claude-sonnet-4-5",
        activeHours: { start: "08:00", end: "23:00", timezone: "Europe/London" },
      },
      model: {
        fallbacks: ["anthropic/claude-sonnet-4-5"],
      },
      subagents: {
        model: "anthropic/claude-sonnet-4-5",
      },
      compaction: {
        memoryFlush: {
          enabled: true,
          prompt: "Write any important context to memory/YYYY-MM-DD.md before compaction. Reply NO_REPLY if nothing to store.",
        },
      },
    },
  },
  hooks: {
    enabled: true,
    token: "<generate-a-token>",
    path: "/hooks",
    // presets: ["gmail"],  // when Gmail Pub/Sub is set up
  },
  session: {
    identityLinks: {
      finn: ["telegram:6047368408"],
    },
  },
}
```

---

*This audit was generated by reading all English-language docs in `/home/ubuntu/.npm-global/lib/node_modules/openclaw/docs/` and comparing against Atlas's current config and operational patterns.*
