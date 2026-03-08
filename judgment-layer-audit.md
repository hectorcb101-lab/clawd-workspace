# Judgment Layer Audit — Diagnosis Report
**Date:** 2026-02-15  
**Status:** Read-only analysis complete

---

## Executive Summary

**The judgment layer is theatre.** Built with good intentions, comprehensive tooling, and solid architecture — but **usage is <5% of what was intended**. 

**Key numbers:**
- 12 principles defined
- 4 applications logged (3 from the initial build demo, 1 test)
- 0 applications with evaluated outcomes that could drive learning
- Target: 5+ uses/week → Actual: <1/week
- Built: Feb 2 → Last real use: Feb 2

**Root cause:** Too manual, no forcing function, unclear value proposition in the moment.

---

## What Was Built

### 1. atlas-judge CLI (783 lines)
**Capabilities:**
- ✅ Principle management (add/update/deactivate/show/list)
- ✅ Consultation (`consult "situation"`) — search for relevant principles
- ✅ Application logging (`apply <id> --situation --how --decision`)
- ✅ Outcome tracking (`outcome <app_id> --result success|partial|failure`)
- ✅ Learning cycle (`learn`) — analyze effectiveness, propose confidence updates
- ✅ Effectiveness analysis (`effectiveness`) — per-principle or overview
- ✅ Calibration tracking (`calibrate`, `calibration`) — log predictions, check accuracy
- ✅ Self-awareness sync (`sync`) — auto-propose principles from correction patterns
- ✅ Task-specific retrieval (`task "description"`) — get relevant principles for a task
- ✅ Stats, export to JUDGMENT.md

**What it does well:**
- Comprehensive feature set
- Clean CLI interface
- Thoughtful data model (principles, applications, calibration)
- Good integration with self-awareness system
- Learning loop designed to update principle confidence from outcomes

### 2. atlas-gate CLI (340 lines)
**Hooks:**
- `pre <topic>` — memory search, duplicate check, stale build warning
- `post <type> <result> <summary>` — log outcome + update daily memory
- `correct <type> <description>` — full correction pipeline
- `health` — weekly check (catches judgment underuse!)
- `session` — startup checks

**Atlas-gate does NOT call atlas-judge.** This is the first problem.

**What atlas-gate actually does:**
- Pre-task: memory search, duplicate detection, context reminders
- Post-task: logs to atlas-self, updates daily memory file
- Correct: runs atlas-self log-correction → atlas-mod from-correction
- Health: checks judgment stats (notices underuse) but doesn't fix it
- Session: daemon check, active build staleness

**What it doesn't do:**
- No automatic consultation of judgment layer in `pre`
- No judgment principle suggestion before tasks
- No forcing of principle application logging
- No feedback loop to judgment layer from outcomes

### 3. Database Schema
**Tables:**
- `principles` — 12 active principles, categories (decision/metacognitive/priority/escalation)
- `applications` — 4 records total (1 test, 3 from Feb 2 demo)
- `calibration` — 1 record

**Data quality:**
- ✅ Principles well-defined with rationale, examples, keywords
- ❌ Applications have no evaluated outcomes (outcome field = "success" but no feedback cycle)
- ❌ Effectiveness scores all null (need 3+ evaluated applications)
- ❌ Learning cycle never ran on real data

### 4. Integration Points
**atlas-judge → Event Bus:** Designed to emit judgment events for training data capture. Never used.

**self-awareness → atlas-judge:** `sync` command can auto-propose principles from correction patterns. Never ran after initial seed.

**atlas-gate → atlas-judge:** **NO INTEGRATION.** This is the core problem.

---

## Why It's Not Being Used

### Friction Point 1: Too Many Steps
**To apply a principle properly:**
1. Notice a decision point
2. Run `atlas-judge consult "situation"` or `atlas-judge task "description"`
3. Read output (5+ principles with rationale/examples)
4. Decide which principle applies
5. Make the decision
6. Run `atlas-judge apply <id> --situation "..." --how "..." --decision "..."`
7. Do the work
8. Run `atlas-judge outcome <app_id> --result success|partial|failure --notes "..."`

**Reality:** This is 3 manual CLI invocations + cognitive overhead mid-task. Never going to happen consistently.

**Compare to:** Just making the decision and moving on (0 steps).

### Friction Point 2: No Forcing Function
**AGENTS.md says:**
> **Pre-task:** `atlas-gate pre "<topic>"` — searches memory, checks for duplicates, flags stale builds. Run before any task involving file changes, external actions, or >5 min of work.

**But atlas-gate pre does NOT:**
- Call `atlas-judge consult` or `atlas-judge task`
- Surface relevant principles
- Prompt for principle application

**Result:** The judgment layer is opt-in, manual, and invisible.

### Friction Point 3: Unclear Value Proposition
**When in the flow of work, asking "should I consult the judgment layer?" the answer is always:**
- "I already know what to do" (pattern-matching)
- "This is urgent, no time for philosophy"
- "The principles are too abstract to help"
- "I'll remember to log it later" (narrator: they didn't)

**The value only appears in hindsight:**
- After a mistake: "Oh, PRINC-003 would have caught that"
- In review: "I should have consulted principles"

### Friction Point 4: Learning Loop Broken
**The system was designed to improve over time:**
1. Apply principle → log application
2. Log outcome (success/partial/failure)
3. Run `atlas-judge learn` to analyze effectiveness
4. Update confidence scores based on evidence
5. Retire ineffective principles, promote effective ones

**What actually happened:**
- Step 1: 4 applications (3 from demo, 1 test)
- Step 2: 0 outcomes evaluated (all marked "success" but no actual feedback)
- Step 3: `learn` never ran on real data
- Steps 4-5: Never reached

**Result:** The system can't learn because there's no data. There's no data because logging is too manual.

### Friction Point 5: Principles Too Abstract
**Example principles:**
- PRINC-001: "Match the complexity of my approach to the complexity of the problem."
- PRINC-005: "Notice when I'm pattern-matching vs. actually reasoning."

**These are good principles.** But in the moment, they don't provide actionable guidance. They're metacognitive reminders, not decision procedures.

**When facing a decision, I need:**
- "Given X situation, do Y"
- "If stakes are high, add confirmation step"
- "Research tasks: always create plan doc first"

**What the principles provide:**
- "Think about whether you're thinking correctly"
- "Be aware of your cognitive patterns"

**Gap:** Principles are one level of abstraction too high for real-time use.

---

## What's Actually Working

### 1. The Health Check Caught It
**atlas-gate health** flagged judgment underuse:
```
{
  "name": "judgment_usage",
  "warning": "Judgment layer only used 4 times. Target: 5+/week."
}
```

This audit exists because the health check worked. Self-awareness detected the problem.

### 2. The Infrastructure Is Solid
- Clean data model
- Well-designed CLI
- Thoughtful integration points (self-awareness, event bus)
- Comprehensive feature set

The engineering is good. The UX and forcing function are the problems.

### 3. The Principles Themselves
The 12 seed principles are valuable. They're just not accessible when needed.

**Top principles by priority:**
1. PRINC-009: "Actions that leave the system require explicit confirmation" (escalation, prio 10)
2. PRINC-002: "Prefer reversible actions over irreversible ones" (decision, prio 9)
3. PRINC-007: "Finn's explicit request > inferred need > my initiative" (priority, prio 9)
4. PRINC-010: "Higher stakes = more explicit reasoning and confirmation" (escalation, prio 9)

These ARE being followed — just not via the judgment layer. They're internalized from AGENTS.md.

---

## Comparison: What's Actually Used

### atlas-self: 33 outcomes, 17 corrections
**Why it works:**
- Single command: `atlas-self log-outcome <type> <result> -n "summary"`
- Called by atlas-gate post (enforcement)
- Clear value: tracks performance, identifies patterns
- Low friction: 1 command, minimal args

### atlas-gate: Used occasionally
**Adoption:**
- `session` — used at session start (automated)
- `health` — used weekly (manual but valuable)
- `pre`/`post` — underused (manual, no enforcement)
- `correct` — never used (forgot it exists)

**Why partial adoption:**
- `session` is automatic (daemon check)
- `health` shows clear value (catches problems)
- `pre`/`post` compete with "just do the work"
- `correct` is invisible (would need to remember it exists mid-correction)

### atlas-judge: 4 total uses (3 demo, 1 test)
**Why it failed:**
- 3-step process (consult → apply → outcome)
- No forcing function
- No integration with atlas-gate
- Value unclear in the moment

---

## Specific Friction Points (Ranked)

### 🔴 Critical: No Forcing Function
**Problem:** atlas-gate pre doesn't call atlas-judge.

**Evidence:**
```python
# atlas-gate pre only does:
1. Memory search
2. Duplicate check  
3. Stale build warning
4. Reminder to log outcome later

# It does NOT:
- Consult judgment layer
- Surface relevant principles
- Prompt for principle application
```

**Fix:** `atlas-gate pre` should call `atlas-judge task` and surface top 2-3 principles.

### 🔴 Critical: 3-Step Process Too Manual
**Problem:** Consult → Apply → Outcome is 3 separate CLI calls with manual tracking.

**Current flow:**
1. `atlas-judge consult "situation"` → returns principles
2. (make decision)
3. `atlas-judge apply PRINC-XXX --situation "..." --how "..." --decision "..."` → returns app ID
4. (do the work)
5. `atlas-judge outcome <app_id> --result ...` → must remember app ID

**Why it's broken:**
- Step 3: must copy principle ID from step 1
- Step 5: must copy app ID from step 3
- Steps are separated by actual work
- Easy to forget

**Fix:** Single-step logging: `atlas-judge used PRINC-XXX --success|failure --notes "..."`

### 🟠 High: Outcome Tracking Separated from Outcome Logging
**Problem:** atlas-gate post logs to atlas-self but NOT to atlas-judge.

**Evidence:**
```python
# atlas-gate post:
log_out = run_cli(f'atlas-self log-outcome {task_type} {result} -n "{summary}"')
# Updates daily memory file
# Does NOT call: atlas-judge outcome <app_id> --result ...
```

**Result:** Even if principle was applied, outcome never logged → learning loop broken.

**Fix:** If a principle was applied during pre, atlas-gate post should auto-log outcome.

### 🟠 High: Principles Too Abstract
**Problem:** "Match complexity to problem" is a good reminder but not actionable guidance.

**Evidence:** All 9 principles with 0 applications are metacognitive or abstract.
The 3 with applications (PRINC-001, PRINC-009, PRINC-012) are concrete enough to remember.

**Fix:** Either:
- Add "actionable step" field to principles (concrete "do X" instruction)
- Lower abstraction level (specific → general, not general → specific)
- Accept that principles are reminders, not procedures

### 🟡 Medium: CLI Output Too Verbose
**Example:**
```bash
$ atlas-judge consult "send email to professor"

🔍 Consulting judgment layer for: "send email to professor"

Relevant principles (5):

1. [PRINC-009] Actions that leave the system require explicit confirmation.
   → Before sending an email to someone external, draft it for Finn to review
   
2. [PRINC-007] Finn's explicit request > inferred need > my initiative.
   → If Finn didn't ask for this email, confirm before sending
   
3. [PRINC-010] Higher stakes = more explicit reasoning and confirmation.
   → Email to professor = higher stakes, add confirmation step
...
```

**Problem:** This is 20+ lines. Mid-task, this is noise.

**Fix:** Concise mode: `atlas-judge consult --brief` → 1 line per principle, max 3.

### 🟡 Medium: No Incremental Value
**Problem:** Using 10% of the judgment layer provides 0% value.

The system only becomes valuable when:
1. Principles are consulted regularly
2. Applications are logged consistently  
3. Outcomes are tracked
4. Learning cycle runs
5. Confidence scores update
6. Principles evolve

**Doing steps 1-2 without 3-6 = no benefit, only overhead.**

**Fix:** Either commit fully or retire the system. Half-measures waste time.

---

## Database Evidence

### Principles Table (12 active)
```
applications_count:
- PRINC-001: 1 use (demo)
- PRINC-009: 1 use (demo)
- PRINC-012: 1 use (demo)
- All others: 0 uses

effectiveness:
- All: null (need 3+ evaluated applications)

confidence:
- Range: 50-90% (all seed values, no learning updates)
```

### Applications Table (4 records)
```
ID | principle_id | situation                    | outcome  | evaluated_at
1  | PRINC-001   | Building Judgment Layer       | success  | 2026-02-02
2  | PRINC-012   | Research on AI slop           | success  | 2026-02-02
3  | PRINC-009   | Send email with findings      | success  | 2026-02-02
4  | PRIN-decision-001 | Testing event bus      | success  | null
```

**Observations:**
- 3 applications are from Feb 2 (initial build demo)
- 1 application is a test (malformed principle ID)
- All marked "success" but no actual outcome evaluation
- No applications logged in 13 days since Feb 2

### Calibration Table (1 record)
```
domain | prediction | confidence | correct
-------+-----------+-----------+--------
test   | test      | 0.8       | 1
```

**Observation:** Single test record. Feature unused.

---

## Memory Evidence

### Last Real Usage: Feb 2, 2026
**From 2026-02-02.md:**
```markdown
Built Judgment Layer system
- Created 12 seed principles
- Tested consult, apply, outcome workflow
- Logged 3 applications (all successful)
```

### Awareness of Underuse: Feb 15, 2026
**From 2026-02-15-health-check.md:**
```markdown
Judgment Layer Underused
- Only 4 calls this week (target: 5+)
- Not consulting judgment principles enough
- Action: Be more intentional about using atlas-judge consult
```

**From 2026-02-15-weekly-review.md:**
```markdown
Review atlas-gate usage — Was it actually adopted, or just built and forgotten?
Check: When was atlas-gate last used?
If not being used: Why? Too manual? Forgotten?
```

**Gap:** 13 days between build and health check catching the problem.

---

## Diagnosis Summary

### Why Judgment Layer Is Underused

#### Root Causes (in priority order):

1. **No forcing function** — atlas-gate pre doesn't call atlas-judge → invisible, opt-in
2. **Too manual** — 3-step process (consult → apply → outcome) → high friction
3. **Outcome tracking broken** — atlas-gate post logs to atlas-self, not atlas-judge → learning loop never starts
4. **Unclear immediate value** — benefits only appear in hindsight → easy to skip
5. **Principles too abstract** — good reminders, but not actionable in-the-moment guidance
6. **CLI too verbose** — 20-line output mid-task → feels like overhead, not help

#### What This Means:

The judgment layer is **well-engineered but poorly integrated**. It's a standalone system that requires manual opt-in at every step. In a flow-based environment (agent responding to user requests), manual meta-cognitive checks don't survive.

**The system assumes:**
- I'll remember to consult it mid-task
- I'll log application details afterward
- I'll track outcome weeks later
- I'll run learning analysis periodically

**Reality:**
- I'm focused on the task, not the tracking
- "Later" never comes
- The system provides no value until fully adopted
- Partial adoption = pure overhead

---

## What Would Make It Work?

### Option A: Full Integration (High Effort)

**Changes needed:**

1. **atlas-gate pre calls atlas-judge task**
   - Auto-consult judgment layer
   - Surface top 2 principles in concise format
   - Store consultation in session state

2. **atlas-gate post logs to both atlas-self AND atlas-judge**
   - If principle was consulted in pre, auto-log outcome
   - No manual tracking of app IDs
   - Learning loop gets data automatically

3. **Simplify application logging**
   - Single command: `atlas-judge used PRINC-XXX --success|failure`
   - No multi-step flow
   - No manual ID tracking

4. **Concise output mode**
   - Default: 1 line per principle, max 3
   - Full details: `--verbose`

5. **Weekly auto-learning**
   - atlas-gate health runs atlas-judge learn
   - Auto-updates confidence scores
   - Flags ineffective principles

**Effort:** 2-3 days of engineering

**Value:** Judgment layer becomes self-sustaining, data-driven, useful

**Risk:** Still might not use it (forcing function only works if the output is valuable)

### Option B: Simplify to Essentials (Low Effort)

**Changes needed:**

1. **Retire most of the CLI**
   - Keep: principles list, principle show
   - Remove: apply, outcome, learn, effectiveness, calibration
   
2. **atlas-gate pre: manual reminder only**
   - "High-stakes task detected. Relevant principles: PRINC-009, PRINC-010"
   - No logging, no tracking, just visibility

3. **Accept principles as reference, not system**
   - Export to JUDGMENT.md (already works)
   - Read it weekly as part of review
   - No tracking, no feedback loop

**Effort:** 1 day (mostly deletions)

**Value:** Removes overhead, keeps reference value

**Risk:** Admits defeat on data-driven judgment improvement

### Option C: Retire It (Zero Effort)

**Changes:**

1. Archive atlas-judge to `archive/`
2. Remove atlas-judge references from AGENTS.md
3. Keep JUDGMENT.md as static reference doc
4. Extract valuable principles into AGENTS.md directly

**Effort:** 30 minutes

**Value:** Honesty about what's actually used

**Risk:** Loses potential for future improvement

---

## Recommendation

**Go with Option A (Full Integration) with a 30-day trial.**

**Why:**
- The engineering is already done (sunk cost, but also means integration is feasible)
- The health check proved self-awareness works (judgment underuse was caught)
- The principles are valuable (PRINC-009, PRINC-007, PRINC-010 are already internalized)
- The learning loop is the missing piece (could actually improve decision-making over time)

**30-day trial:**
- Implement full integration (atlas-gate ↔ atlas-judge)
- Measure: applications/week, outcome logging %, learning cycle runs
- Success criteria: 10+ applications/week, 80%+ outcome logging, weekly learning
- If criteria not met: Retire to Option C

**Why not Option B or C now:**
- Option B keeps overhead without upside (worst of both worlds)
- Option C gives up before trying enforcement (health check worked, hooks might too)

**Key insight:** The problem isn't the judgment layer — it's the integration. Fix the integration before retiring the system.

---

## Appendix: Commands That Actually Work

### atlas-self (33 outcomes, 17 corrections)
```bash
atlas-self log-outcome coding success -n "built X feature"
atlas-self log-correction "wrong approach" -t approach -l "should have done Y"
atlas-self analyze
```

**Why it works:** Single command, called by atlas-gate post, clear value.

### atlas-gate (partially used)
```bash
atlas-gate session  # automatic at startup
atlas-gate health   # weekly, shows clear value
atlas-gate pre "topic"  # underused, no enforcement
atlas-gate post coding success "summary"  # underused, competes with just working
```

**Why session/health work:** Automation + clear value.  
**Why pre/post don't:** Manual + unclear immediate value.

### atlas-judge (4 uses, 3 were demo)
```bash
atlas-judge principles list
atlas-judge principle show PRINC-009
atlas-judge consult "situation"  # never used outside demo
atlas-judge apply ...  # never used outside demo
atlas-judge outcome ...  # never used
```

**Why it doesn't work:** See entire report above.

---

## Final Diagnosis

**Theatre score: 9/10**

Built with care, never used. The infrastructure exists, the principles are sound, the integration is missing. It's a car with no road to drive on.

**Friction points:**
1. No forcing function (atlas-gate doesn't call atlas-judge)
2. Too manual (3-step process)
3. Outcome tracking broken (atlas-gate post doesn't log to atlas-judge)
4. Unclear value (benefits only in hindsight)
5. Principles too abstract (good reminders, not actionable guidance)
6. CLI too verbose (20 lines mid-task)

**What would fix it:**
- Atlas-gate pre → atlas-judge task (auto-consult)
- Atlas-gate post → atlas-judge outcome (auto-log)
- Single-command application logging
- Concise output mode
- Weekly auto-learning

**Current state:** Built Feb 2, used Feb 2, forgotten Feb 3-15, caught by health check Feb 15.

**Brutal honesty:** This is what happens when you build "wouldn't it be cool if..." without "how will I actually use this?"

The engineering is solid. The UX is the problem. Fix the UX or retire it.

---

*End of audit.*
