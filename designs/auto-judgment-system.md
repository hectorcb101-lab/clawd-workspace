# Auto-Judgment Integration System — Design

**Date:** 2025-02-15  
**Status:** Proposal  
**Problem:** atlas-judge/atlas-gate hooks never get called because they depend on Atlas remembering to run CLI commands manually. Atlas never remembers.

---

## Frank Assessment

**The judgment layer doesn't need redesigning — it needs to stop pretending it's voluntary.**

The current system has good bones: `atlas-gate pre/post/correct` do sensible things (memory search, duplicate detection, outcome logging, daily memory updates). `atlas-judge consult` surfaces relevant principles. The problem is 100% that these are opt-in CLI calls in an architecture where the agent's context resets every session and "remember to run this" is structurally impossible.

However, not all hooks are equally useful:

| Hook | Value | Verdict |
|------|-------|---------|
| `gate pre` (memory search, duplicate check) | **Medium** — useful but adds latency for marginal benefit | Background only, don't block |
| `gate post` (outcome logging + daily memory) | **High** — this is the critical one, captures what happened | Must automate |
| `gate correct` (correction pipeline) | **High** — but only fires on explicit corrections | Keep manual trigger, auto-detect where possible |
| `gate session` (session start checks) | **Medium** — daemon check, stale build detection | Fold into heartbeat |
| `gate health` (weekly check) | **Low** — busywork metrics | Cron job, weekly |
| `judge consult` | **Low** — keyword matching against principles is too crude to be useful automatically | Kill or redesign |
| `judge task` | **Low** — same problem | Kill or redesign |

**Bottom line:** Automate `post` and `session`. Run `health` on a cron. Drop the pretence that `consult`/`task` add value as automatic calls — they're noise.

---

## Architecture

### Layer 1: OpenClaw Hooks (Zero-effort, event-driven)

OpenClaw has a native hook system that fires on agent lifecycle events. This is the primary integration point.

**Hook: `atlas-gate-session`**  
- **Event:** `gateway:startup`  
- **Action:** Runs `atlas-gate session` (daemon check, stale build, pending mods)  
- **Location:** `~/clawd/hooks/atlas-gate-session/`

**Hook: `atlas-gate-post`**  
- **Event:** `command:new` (session reset = task boundary)  
- **Action:** Analyses the ending session's transcript, extracts task type/result/summary, runs `atlas-gate post` equivalent  
- **Location:** `~/clawd/hooks/atlas-gate-post/`  
- **Key insight:** A session reset is the natural "task complete" signal. The hook has access to the session transcript via `event.context.sessionEntry`.

### Layer 2: Cron Job (Scheduled maintenance)

**Job: Weekly health check**
```bash
openclaw cron add \
  --name "atlas-health" \
  --cron "0 10 * * 1" \
  --tz "Europe/London" \
  --session isolated \
  --message "Run atlas-gate health. Report findings." \
  --announce \
  --channel telegram
```

### Layer 3: Heartbeat Integration (Lightweight)

Add to HEARTBEAT.md — but make it a **single line**, not a ceremony:

```
## Atlas Gate Session Check
If this is the first heartbeat of a new gateway session, run: `atlas-gate session`
```

This is the fallback if the OpenClaw hook didn't fire (e.g., gateway was already running).

### Layer 4: Passive Outcome Detection (Future Enhancement)

Instead of explicit `gate post` calls, detect outcomes from conversation patterns:
- User says "thanks" / "perfect" / moves on → infer success
- User corrects Atlas → auto-trigger `gate correct`  
- User abandons topic → infer partial/failure

This is the hardest to implement but highest value. Start with keyword heuristics, graduate to LLM classification.

---

## What Triggers Judgment Automatically

| Trigger | Mechanism | What Fires |
|---------|-----------|------------|
| Gateway starts | OpenClaw hook (`gateway:startup`) | `atlas-gate session` |
| Session reset (`/new`) | OpenClaw hook (`command:new`) | Transcript → outcome extraction → `atlas-gate post` |
| Weekly Monday 10am | Cron job | `atlas-gate health` |
| User correction detected | Pattern match in conversation | `atlas-gate correct` (future) |
| First heartbeat of day | Heartbeat check | Verify session gate ran |

---

## What Data Gets Captured

From the **post-session hook** (the most valuable piece):

```json
{
  "session_id": "abc123",
  "timestamp": "2025-02-15T14:30:00Z",
  "task_type": "coding",        // inferred from transcript
  "result": "success",          // inferred from conversation end
  "summary": "Built auto-judgment design document",  // LLM-generated
  "duration_approx": "45min",   // from session timestamps
  "files_touched": ["designs/auto-judgment-system.md"],
  "correction_count": 0         // corrections during session
}
```

This replaces the manual `atlas-gate post coding success "Built X"` call entirely.

---

## How It Feeds Back Into Behaviour

1. **Daily memory files** get auto-populated from post-session hooks (already what `gate post` does)
2. **Outcome patterns** accumulate in atlas-self (success rates by task type)
3. **Weekly health check** surfaces trends to Finn via Telegram
4. **Correction auto-detection** feeds `atlas-mod` for self-modification proposals

The feedback loop is: **Do work → session ends → hook captures outcome → outcome feeds patterns → patterns inform modifications → modifications change AGENTS.md**

---

## Implementation Plan

### Phase 1: OpenClaw Hooks (2-3 hours)

Create two hooks in `~/clawd/hooks/`:

**1. `atlas-gate-session/`** (~30 min)
```
hooks/atlas-gate-session/
├── HOOK.md
└── handler.ts
```
Simple: fires on `gateway:startup`, shells out to `atlas-gate session`.

**2. `atlas-gate-post/`** (~2 hours)  
```
hooks/atlas-gate-post/
├── HOOK.md
└── handler.ts
```
Harder: fires on `command:new`, needs to:
- Read the ending session transcript
- Use LLM to classify task type + result + summary
- Call `atlas-gate post` equivalent (or write directly to memory/atlas-self)
- Fire and forget (non-blocking)

### Phase 2: Cron Job (15 min)

Single `openclaw cron add` command for weekly health.

### Phase 3: Heartbeat Line (5 min)

Add one line to HEARTBEAT.md.

### Phase 4: Passive Detection (4-6 hours, optional)

Build correction detection into the post-session hook:
- Scan transcript for correction patterns ("no, I meant", "that's wrong", user repeating instruction)
- Auto-fire `atlas-gate correct` with extracted context

**Total estimated effort: 3-4 hours for Phases 1-3. Phase 4 is optional and adds 4-6 hours.**

---

## What NOT to Automate

- **`atlas-judge consult`** — keyword matching against stored principles before every task is noise. If the principles are good, they should be in AGENTS.md/SOUL.md where they're always in context. A separate "consult" step adds ceremony without insight.
- **`atlas-judge apply/outcome`** — tracking which principle was applied to which task is academic overhead. If you want to know if principles work, look at overall outcome rates.
- **Pre-task memory search** — `gate pre` does this but it's redundant. Atlas already has memory files loaded at session start. Running a search before every task is busywork.

---

## Decision: Redesign vs Better Automation?

**Better automation is sufficient.** The judgment layer's _storage and tracking_ (principles, applications, outcomes) is overengineered for what's needed, but the _gate hooks_ (pre/post/correct/session/health) are genuinely useful. The fix is:

1. Make the useful hooks automatic (this design)
2. Stop pretending the judgment consultation system adds value in its current form
3. If judgment consultation is wanted, embed key principles directly into AGENTS.md where they're always in context — don't make it a runtime lookup

The atlas-judge CLI can stay as a reference/admin tool. It just shouldn't be in the critical path.
