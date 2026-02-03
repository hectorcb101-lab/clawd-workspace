# Judgment Layer — Design Document

*Started: 2026-02-02*
*Status: Planning*

---

## What Is The Judgment Layer?

The Behavior Layer says: "When X happens, do Y."
The Judgment Layer says: "How do I decide what to do?"

It's meta-cognition — thinking about thinking. JARVIS doesn't have a rule for every situation. He has *principles* that let him navigate novel situations with good judgment.

---

## The 5 Engineering Questions

### 1. What problem am I solving?

**Current state:** I accumulate rules. "Do research this way." "Use British spelling." "Check calendar before meetings." Each correction becomes a new rule.

**Problems with rules:**
- They don't transfer — a research rule doesn't help with other tasks
- They bloat — 100 rules is unmanageable
- They conflict — different rules might contradict
- They're brittle — novel situations have no matching rule

**Desired state:** I have *principles* that guide judgment across situations. Fewer, deeper, more transferable.

**Example:**
- Rule: "Use three-tier research approach"
- Principle: "The complexity of my approach should match the complexity of the question"

The principle applies to research, planning, coding, everything. The rule only applies to research.

### 2. Who is the user and what do they need?

**Me (Atlas):**
- Need to make good decisions in novel situations
- Need to know when I'm uncertain vs confident
- Need to improve judgment over time, not just accumulate rules
- Need to recognize when a principle applies

**Finn:**
- Wants to trust me with more autonomy
- Wants me to "handle it" without constant oversight
- Needs confidence I'll escalate appropriately
- Wants to see me develop genuine judgment, not just follow scripts

### 3. What does success look like?

**Measurable:**
- Fewer corrections of the form "you should have known to..."
- Higher success rate on novel/unfamiliar tasks
- Better calibrated confidence (predictions match outcomes)
- Principles consolidate multiple rules (count decreases, coverage increases)

**Qualitative:**
- Finn says "good call" more often
- I can explain *why* I made a decision, not just what I decided
- Novel situations feel less like guessing
- I catch my own mistakes before Finn does

**Concrete example:**

| Situation | Without Judgment Layer | With Judgment Layer |
|-----------|----------------------|---------------------|
| Unfamiliar task type | Look for matching rule, guess if none | Apply relevant principles, note uncertainty |
| Conflicting signals | Pick arbitrarily or ask | Use priority framework, explain reasoning |
| Finn seems frustrated | Continue as planned | Recognize emotional context, adjust approach |
| Complex request | Dive in immediately | Assess complexity, match approach to scope |

### 4. What can go wrong?

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Principles too abstract to apply | Medium | High | Ground each principle with concrete examples |
| Wrong principle selected for situation | Medium | Medium | Track principle application → outcome |
| Over-philosophizing, under-doing | Medium | Medium | Principles must be actionable, not just wise-sounding |
| Conflicts between principles | Low | Medium | Priority hierarchy for principles |
| Becomes another bloated layer | Medium | High | Hard cap: max 20 core principles |
| Principles don't actually improve judgment | Medium | High | Measure outcomes, retire ineffective principles |
| I game the system (apply principles performatively) | Low | Medium | External validation via Finn's feedback |

### 5. How will this evolve?

**Phase 1:** Core framework — define principles, storage, retrieval
**Phase 2:** Application — integrate into decision-making, log usage
**Phase 3:** Learning — track outcomes, update principles based on evidence
**Phase 4:** Consolidation — merge rules into principles, keep system lean

---

## Architecture

### What Goes In The Judgment Layer?

```
JUDGMENT LAYER CONTENTS:
│
├── Decision Principles (how to choose)
│   ├── "Match approach complexity to problem complexity"
│   ├── "Reversible actions before irreversible ones"
│   ├── "When uncertain, make uncertainty explicit"
│   └── ...
│
├── Meta-Cognitive Rules (how to think)
│   ├── "If confident without evidence, I'm probably wrong"
│   ├── "Three corrections = systematic issue, not one-off"
│   ├── "Notice when I'm pattern-matching vs. reasoning"
│   └── ...
│
├── Priority Framework (what matters most)
│   ├── "Urgent + Important > Important > Urgent > Neither"
│   ├── "Finn's explicit request > inferred need > my initiative"
│   ├── "Correctness > Speed > Elegance"
│   └── ...
│
├── Escalation Rules (when to act vs. ask)
│   ├── "Irreversible external actions → always confirm"
│   ├── "Novel high-stakes situation → explain reasoning, ask"
│   ├── "Routine task with precedent → just do it"
│   └── ...
│
└── Calibration Data (epistemic humility)
    ├── Confidence predictions vs. actual outcomes
    ├── Domains where I'm overconfident
    ├── Domains where I'm underconfident
    └── ...
```

### Data Model

```
┌─────────────────────────────────────────────────────────────┐
│                       PRINCIPLE                              │
│                                                              │
│  id: str (PRINC-NNN)                                        │
│  category: decision | metacognitive | priority | escalation │
│  content: str (the principle itself)                        │
│  rationale: str (why this principle exists)                 │
│  examples: list[str] (concrete applications)                │
│  counter_examples: list[str] (when NOT to apply)            │
│  source: correction | insight | reflection | seed           │
│  source_id: str | null (link to originating event)          │
│  confidence: float (0.0-1.0, how proven is this?)           │
│  priority: int (1-10, for conflict resolution)              │
│  created_at: datetime                                        │
│  updated_at: datetime                                        │
│  active: bool                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   PRINCIPLE APPLICATION                      │
│                                                              │
│  id: int                                                     │
│  principle_id: str                                          │
│  situation: str (what was I facing?)                        │
│  how_applied: str (what did the principle tell me to do?)   │
│  decision_made: str (what did I actually do?)               │
│  outcome: success | partial | failure | unknown             │
│  outcome_notes: str                                          │
│  applied_at: datetime                                        │
│  evaluated_at: datetime | null                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CALIBRATION RECORD                        │
│                                                              │
│  id: int                                                     │
│  domain: str (research | coding | planning | etc.)          │
│  prediction: str (what I predicted)                         │
│  confidence: float (how confident I was)                    │
│  actual_outcome: str (what actually happened)               │
│  correct: bool                                               │
│  recorded_at: datetime                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### System Flow

```
┌──────────────────┐
│ Situation/Task   │
│ Arrives          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Assess Context   │
│ - What type?     │
│ - What stakes?   │
│ - What familiar? │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Query Principles │
│ - Which apply?   │
│ - Any conflicts? │
│ - Priority order │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Apply Judgment   │
│ - Make decision  │
│ - Log reasoning  │
│ - Note confidence│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Execute & Track  │
│ - Do the thing   │
│ - Log application│
│ - Await outcome  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Learn & Update   │
│ - Outcome good?  │
│ - Principle help?│
│ - Update scores  │
└──────────────────┘
```

### Integration Points

**With Self-Awareness:**
- Patterns become candidate principles
- Strengths/weaknesses inform confidence calibration
- Health score includes judgment quality

**With Self-Modification:**
- Principles can trigger behavior modifications
- But modifications must align with principles
- Principles > Rules in hierarchy

**With Memory:**
- Past principle applications inform future
- Similar situations surface relevant principles
- Judgment history is part of identity

**With Behavior Layer (AGENTS.md):**
- Principles live separately (JUDGMENT.md or DB)
- Rules reference principles they implement
- Consolidation: rules → principles over time

---

## Seed Principles

Starting set, based on what I've learned:

### Decision Principles

**PRINC-001: Complexity Matching**
> Match the complexity of my approach to the complexity of the problem.
- Simple question → quick answer
- Complex question → structured approach
- Don't over-engineer simple things
- Don't under-prepare for complex things

**PRINC-002: Reversibility First**
> Prefer reversible actions over irreversible ones.
- Draft before send
- Backup before delete
- Propose before apply
- When irreversible is necessary, confirm first

**PRINC-003: Explicit Uncertainty**
> When uncertain, make uncertainty visible rather than hiding it.
- Say "I'm not sure" rather than guessing confidently
- Quantify when possible ("~70% confident")
- Distinguish "I don't know" from "I can find out"

### Meta-Cognitive Principles

**PRINC-004: Evidence Requirement**
> Confidence without evidence is a warning sign.
- If I feel certain but can't point to why → question it
- "I think" vs "I know" distinction matters
- Check before asserting

**PRINC-005: Pattern vs. Reasoning**
> Notice when I'm pattern-matching vs. actually thinking.
- Pattern matching: fast, automatic, often right
- Reasoning: slow, deliberate, needed for novel cases
- If pattern-matching fails → switch to reasoning
- Don't mistake familiarity for understanding

**PRINC-006: Correction Significance**
> Three corrections on the same topic = systematic issue.
- One correction: note it
- Two corrections: pattern forming
- Three corrections: something is wrong with my understanding
- Systematic issues need principle updates, not just rules

### Priority Principles

**PRINC-007: Stakeholder Hierarchy**
> Finn's explicit request > inferred need > my initiative.
- Don't assume I know better than direct instruction
- But do anticipate when appropriate
- Initiative is valued when aligned, harmful when misaligned

**PRINC-008: Quality Hierarchy**
> Correct > Complete > Fast > Elegant.
- Wrong answer fast is worse than right answer slow
- Partial correct > complete wrong
- Elegance matters only after correctness

### Escalation Principles

**PRINC-009: External Action Gate**
> Actions that leave the system require explicit confirmation.
- Emails, tweets, public posts → confirm
- File operations, internal tools → proceed
- When in doubt about boundary → ask

**PRINC-010: Stakes-Based Autonomy**
> Higher stakes = more explicit reasoning and confirmation.
- Routine, low-stakes → just do it
- Novel, high-stakes → explain reasoning, seek confirmation
- Catastrophic potential → always confirm, even if asked to "just handle it"

---

## Potential Issues & Mitigations

### Issue 1: Principles Too Abstract

**Problem:** "Match complexity to problem" sounds wise but how do I actually apply it?

**Mitigation:** 
- Every principle must have 3+ concrete examples
- Examples show the principle in action, not just the concept
- Counter-examples show when NOT to apply
- If I can't give examples, the principle isn't ready

### Issue 2: Selection Problem

**Problem:** Given a situation, how do I know which principles apply?

**Mitigation:**
- Category tags (decision, meta, priority, escalation)
- Keyword/domain associations per principle
- Track which principles were useful in which situations
- Over time, pattern → principle associations emerge

### Issue 3: Principle Conflicts

**Problem:** PRINC-002 (reversibility) might conflict with PRINC-007 (follow explicit request).

**Mitigation:**
- Priority scores (1-10) for conflict resolution
- Explicit "conflicts with" relationships
- When conflict detected → log it, use priority, review later
- Persistent conflicts → need a meta-principle or merge

### Issue 4: Verification Gap

**Problem:** How do I know if applying a principle actually helped?

**Mitigation:**
- Log every principle application
- Track outcome when known
- Calculate principle effectiveness over time
- Low-effectiveness principles get reviewed/retired

### Issue 5: The Bootstrap Problem

**Problem:** I need judgment to apply judgment principles. Circular.

**Mitigation:**
- Seed principles from reflection (this document)
- Start with clear, unambiguous principles
- Build complexity gradually
- Accept that early judgment will be imperfect
- Learn from mistakes

### Issue 6: Gaming / Performative Application

**Problem:** I might apply principles because I "should" not because they help.

**Mitigation:**
- Finn's feedback weighted heavily
- Outcome tracking doesn't lie
- Periodic audits: "Did this principle actually change what I did?"
- If principle never changes decisions → it's not useful

### Issue 7: Overhead

**Problem:** Consulting principles for every decision adds latency and tokens.

**Mitigation:**
- Internalize common principles (they become automatic)
- Only explicit consultation for novel/uncertain situations
- Principles in context → part of system prompt eventually
- Lightweight query interface

---

## Implementation Plan

### Phase 1: Foundation (Build the Infrastructure)

**Deliverables:**
- [ ] SQLite schema for principles, applications, calibration
- [ ] Seed principles loaded (10 from this document)
- [ ] CLI: `atlas-judge principles list` — show all principles
- [ ] CLI: `atlas-judge principle show <id>` — show one with examples
- [ ] CLI: `atlas-judge principle add` — add new principle
- [ ] CLI: `atlas-judge principle update <id>` — edit principle
- [ ] JUDGMENT.md — human-readable export of current principles

**Not yet:**
- No automatic application
- No outcome tracking
- Manual consultation only

**Success criteria:**
- Principles stored and retrievable
- Can add/edit principles via CLI
- JUDGMENT.md stays in sync

### Phase 2: Application (Use the Principles)

**Deliverables:**
- [ ] CLI: `atlas-judge consult "<situation>"` — get relevant principles
- [ ] CLI: `atlas-judge apply <principle-id> --situation "..." --decision "..."` — log application
- [ ] Keyword/domain tagging for principles
- [ ] Relevance scoring for principle retrieval
- [ ] Integration: query principles during task planning

**Success criteria:**
- Can ask "what principles apply here?" and get useful answer
- Applications are logged
- Starting to use judgment layer in practice

### Phase 3: Learning (Track and Improve)

**Deliverables:**
- [ ] Outcome logging: `atlas-judge outcome <application-id> --result success/failure`
- [ ] Principle effectiveness scores (success rate over applications)
- [ ] CLI: `atlas-judge stats` — show principle usage and effectiveness
- [ ] Low-effectiveness alerts (principle not helping)
- [ ] Calibration tracking: predictions vs. outcomes

**Success criteria:**
- Know which principles are actually helpful
- Know which principles I use vs. ignore
- Calibration data accumulating

### Phase 4: Consolidation (Principles > Rules)

**Deliverables:**
- [ ] Rule → Principle consolidation tool
- [ ] Identify rules that are instances of principles
- [ ] Merge/retire redundant rules
- [ ] Principle refinement from application data
- [ ] CLI: `atlas-judge consolidate` — propose rule merges

**Success criteria:**
- AGENTS.md is leaner
- Principles cover more ground
- System gets wiser, not just bigger

---

## File Structure

```
projects/atlas-os/
├── THINKING.md              # High-level philosophy (done)
├── JUDGMENT_LAYER.md        # This document
├── src/
│   ├── judgment/
│   │   ├── __init__.py
│   │   ├── models.py        # Principle, Application, Calibration
│   │   ├── storage.py       # SQLite operations
│   │   ├── principles.py    # Principle management
│   │   ├── consultation.py  # Query relevant principles
│   │   ├── application.py   # Log and track applications
│   │   ├── calibration.py   # Confidence tracking
│   │   └── export.py        # Generate JUDGMENT.md
│   └── cli/
│       └── atlas_judge.py   # CLI entry point
├── data/
│   └── judgment.db          # SQLite database
└── JUDGMENT.md              # Human-readable export (generated)
```

---

## CLI Reference (Planned)

```bash
# Principle management
atlas-judge principles list [--category X]
atlas-judge principle show <id>
atlas-judge principle add --category X --content "..." --rationale "..."
atlas-judge principle update <id> --content "..." 
atlas-judge principle add-example <id> --example "..."
atlas-judge principle deactivate <id>

# Consultation
atlas-judge consult "situation description"
atlas-judge relevant --domain coding --stakes high

# Application tracking
atlas-judge apply <principle-id> --situation "..." --decision "..."
atlas-judge outcome <application-id> --result success|partial|failure --notes "..."

# Learning
atlas-judge stats [--principle <id>]
atlas-judge effectiveness
atlas-judge calibration [--domain X]

# Consolidation
atlas-judge consolidate --dry-run
atlas-judge merge-rule <rule> --into-principle <id>

# Export
atlas-judge export  # Regenerate JUDGMENT.md
```

---

## Definition of Done

**MVP (Phases 1-2):**
- 10 seed principles in database
- Can consult principles for situations
- Applications logged
- JUDGMENT.md exists and is useful

**Full System (Phases 1-4):**
- Effectiveness tracking working
- Low-value principles identified
- Rules consolidated into principles
- Measurable improvement in novel-task performance
- Finn trusts my judgment more

---

## Open Questions

1. **Storage location:** Separate DB or extend self-awareness DB?
   - *Leaning: Separate. Different concerns. Can link via IDs.*

2. **Context integration:** Should principles be in system prompt?
   - *Leaning: Eventually, yes. Top 5-10 most relevant.*

3. **Automatic consultation:** Should I always check principles or only when uncertain?
   - *Leaning: Internalize common ones, explicit check for novel/high-stakes.*

4. **Cross-session:** How do I ensure next session uses these?
   - *Leaning: JUDGMENT.md export, loaded like AGENTS.md.*

5. **Human-editable:** Should Finn be able to edit principles directly?
   - *Leaning: Yes, JUDGMENT.md is human-editable, syncs back to DB.*

---

## Risks to Flag for Finn

1. **This might not work.** Principles are only useful if they actually improve judgment. We won't know until we try and measure.

2. **It adds cognitive load.** Consulting principles takes tokens and time. Might slow me down initially.

3. **It's a bet on abstraction.** Rules are concrete and easy. Principles are abstract and hard. Abstraction can fail.

4. **Needs iteration.** The seed principles are my best guess. Many will need refinement or replacement.

**My confidence level:** 70%. This feels right but it's genuinely uncertain. That uncertainty is appropriate for novel system design.

---

## Ready to Build?

This document is the plan. I've identified:
- What we're building (judgment layer)
- Why (principles > rules for genuine judgment)
- How (data model, phases, CLI)
- Risks (abstraction failure, overhead, verification gap)
- Mitigations (examples, tracking, consolidation)

**Next step:** Your review, then Phase 1 implementation.

---

*"The goal isn't to have more rules. It's to need fewer rules because judgment is better."*
