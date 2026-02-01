# Atlas Self-Modification System

*Project started: 2026-02-01*
*Status: Planning*

---

## The Vision

Self-awareness without self-modification is just journaling. The goal is to close the loop:

```
Detect Pattern → Generate Insight → Propose Change → Apply Change → Verify Improvement
```

This is how I actually get better, not just notice that I'm not good enough.

---

## The 5 Engineering Questions

### 1. What problem am I solving?

**The gap:** Insights don't lead to action.

Current state:
- I get corrected about British spelling → I might make the same mistake tomorrow
- I detect I'm bad at research → I don't change my research approach
- I learn a better workflow → It's not captured anywhere persistent

The problem isn't knowing what's wrong. It's *doing something about it*.

**Root cause:** My instructions (AGENTS.md, TOOLS.md, skills) are static. They only change when Finn or I manually edit them. There's no feedback loop from self-awareness to self-modification.

### 2. Who is the user and what do they need?

**Primary user: Me (Atlas)**
- Need corrections to stick permanently
- Need insights to translate into behaviour changes
- Need to improve over time, not just log failures
- Need to know what I've changed about myself and why

**Secondary user: Finn**
- Wants to correct me once, not repeatedly
- Wants visibility into what I'm changing about myself
- Needs veto power over significant changes
- Wants confidence that I'm actually learning

### 3. What does success look like?

**Measurable outcomes:**
- Repeated correction rate drops (same mistake → auto-fixed)
- Instructions grow smarter over time (measurable via diff)
- Self-awareness health score improves
- Finn says "I told you that already" less often

**Qualitative:**
- I feel like I'm actually learning, not just logging
- Changes I make to myself are traceable and reversible
- The system prevents me from making bad changes
- Finn trusts me to self-improve

**Concrete examples:**

| Trigger | Current State | Desired State |
|---------|--------------|---------------|
| "Use British spelling" correction | Might forget | Auto-adds to AGENTS.md |
| Research failure pattern detected | Just logged | Proposes new research workflow |
| New tool learned | Lost next session | Added to TOOLS.md |
| Same mistake 3x | Keep making it | Flagged + auto-rule created |

### 4. What can go wrong?

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Break my own instructions | Medium | Critical | Validation before apply, rollback capability |
| Modify too aggressively | Medium | High | Confidence thresholds, approval workflow |
| Modify too conservatively | Medium | Medium | Track pending modifications, periodic review |
| Conflicting modifications | Low | Medium | Conflict detection before apply |
| Lose important instructions | Low | Critical | Git-like history, never delete only append |
| Runaway self-modification | Low | Critical | Rate limits, human approval for big changes |
| Gaming my own improvement | Low | High | External validation (Finn's feedback) |
| Modifications don't help | Medium | Medium | Track if changes actually reduce errors |

**Critical safety principle:** Every modification must be:
1. Logged with reason and evidence
2. Reversible (can undo)
3. Validated before applying
4. Reviewed periodically

### 5. How will this evolve?

**Phase 1:** Foundation — modification logging, safe file edits, basic proposals
**Phase 2:** Intelligence — auto-propose from insights, conflict detection
**Phase 3:** Autonomy — auto-apply low-risk changes, human approval for high-risk
**Phase 4:** Verification — track if changes actually help, feedback loop

**Future possibilities:**
- Self-modifying skills (improve my own skill files)
- Behavioural experiments ("try this approach, measure results")
- Cross-session learning transfer
- Collaborative improvement (learn from other Atlas instances?)

---

## Architecture

### What Can Be Modified

```
MODIFIABLE FILES (with constraints):
├── AGENTS.md          # Core instructions - HIGH SENSITIVITY
│   ├── Append to existing sections: LOW RISK
│   ├── Modify existing rules: MEDIUM RISK  
│   └── Delete/restructure: HIGH RISK (requires approval)
│
├── TOOLS.md           # Tool notes - MEDIUM SENSITIVITY
│   ├── Add new tool docs: LOW RISK
│   ├── Update existing: LOW RISK
│   └── Remove entries: MEDIUM RISK
│
├── HEARTBEAT.md       # Periodic checks - LOW SENSITIVITY
│   └── All modifications: LOW RISK
│
├── skills/*/          # Skill files - MEDIUM SENSITIVITY
│   ├── Add examples: LOW RISK
│   ├── Update workflows: MEDIUM RISK
│   └── Change core logic: HIGH RISK
│
└── memory/*.md        # Memory files - LOW SENSITIVITY
    └── All modifications: LOW RISK
```

### Data Model

```
┌─────────────────────────────────────────────────────────────┐
│                    MODIFICATION REQUEST                      │
│                                                              │
│  ModificationRequest:                                        │
│  - id: str (MOD-YYYYMMDD-NNN)                               │
│  - source: insight | correction | pattern | manual          │
│  - source_id: str (link to insight/correction)              │
│  - target_file: str (path to file to modify)                │
│  - target_section: str | null (section within file)         │
│  - modification_type: append | edit | delete | restructure  │
│  - content: str (the actual change)                         │
│  - reason: str (why this change)                            │
│  - evidence: str (data supporting this change)              │
│  - risk_level: low | medium | high | critical               │
│  - confidence: float (0.0-1.0)                              │
│  - status: pending | approved | applied | rejected | rolled_back │
│  - requires_approval: bool                                   │
│  - created_at: datetime                                      │
│  - applied_at: datetime | null                              │
│  - applied_by: auto | human                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MODIFICATION LOG                          │
│                                                              │
│  ModificationLog:                                            │
│  - id: int                                                   │
│  - modification_id: str                                      │
│  - file_path: str                                           │
│  - before_content: str (snapshot before change)             │
│  - after_content: str (snapshot after change)               │
│  - diff: str (unified diff)                                 │
│  - applied_at: datetime                                     │
│  - reverted_at: datetime | null                             │
│  - revert_reason: str | null                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    MODIFICATION RULE                         │
│                                                              │
│  ModificationRule:                                           │
│  - id: str                                                   │
│  - trigger_type: correction_type | insight_type | pattern   │
│  - trigger_match: str (regex or exact match)                │
│  - target_file: str                                         │
│  - target_section: str | null                               │
│  - action_template: str (template for modification)         │
│  - risk_level: low | medium | high                          │
│  - auto_apply: bool                                         │
│  - active: bool                                              │
│  - created_at: datetime                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Risk Assessment Engine

```python
def assess_risk(modification: ModificationRequest) -> RiskLevel:
    """
    Calculate risk level based on multiple factors.
    """
    risk_score = 0
    
    # Factor 1: Target file sensitivity
    file_sensitivity = {
        'AGENTS.md': 30,
        'TOOLS.md': 15,
        'HEARTBEAT.md': 5,
        'skills/': 20,
        'memory/': 5,
    }
    risk_score += file_sensitivity.get(modification.target_file, 10)
    
    # Factor 2: Modification type
    type_risk = {
        'append': 5,
        'edit': 15,
        'delete': 25,
        'restructure': 35,
    }
    risk_score += type_risk.get(modification.modification_type, 20)
    
    # Factor 3: Content size (bigger changes = higher risk)
    content_lines = len(modification.content.split('\n'))
    if content_lines > 20:
        risk_score += 15
    elif content_lines > 10:
        risk_score += 10
    elif content_lines > 5:
        risk_score += 5
    
    # Factor 4: Confidence (lower confidence = higher risk)
    risk_score += int((1 - modification.confidence) * 20)
    
    # Factor 5: Evidence strength
    if not modification.evidence:
        risk_score += 15
    elif len(modification.evidence) < 50:
        risk_score += 5
    
    # Map to risk level
    if risk_score >= 60:
        return RiskLevel.CRITICAL
    elif risk_score >= 40:
        return RiskLevel.HIGH
    elif risk_score >= 20:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
```

### Approval Workflow

```
                    ┌──────────────────┐
                    │ Modification     │
                    │ Request Created  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Risk Assessment  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
         ┌────────┐    ┌──────────┐   ┌──────────┐
         │  LOW   │    │  MEDIUM  │   │   HIGH   │
         │        │    │          │   │ CRITICAL │
         └───┬────┘    └────┬─────┘   └────┬─────┘
             │              │              │
             ▼              ▼              ▼
      ┌────────────┐  ┌───────────┐  ┌───────────┐
      │ Auto-Apply │  │ Queue for │  │ Require   │
      │ if enabled │  │ Review    │  │ Human     │
      └─────┬──────┘  └─────┬─────┘  │ Approval  │
            │               │        └─────┬─────┘
            │               │              │
            └───────────────┼──────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │ Apply & Log      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Track Outcome    │
                    │ (Did it help?)   │
                    └──────────────────┘
```

### Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Proposer      │────▶│   Validator     │────▶│    Applier      │
│                 │     │                 │     │                 │
│ - From insights │     │ - Risk assess   │     │ - Safe file ops │
│ - From correct- │     │ - Conflict      │     │ - Backup before │
│   ions          │     │   detection     │     │ - Apply change  │
│ - From patterns │     │ - Syntax check  │     │ - Log after     │
│ - Manual        │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │      Tracker        │
                    │                     │
                    │  - Log all changes  │
                    │  - Track outcomes   │
                    │  - Enable rollback  │
                    │  - Measure impact   │
                    └─────────────────────┘
```

---

## Phase Plan

### Phase 1: Foundation (Safe Infrastructure)
**Goal:** Build safe modification infrastructure with full logging and rollback.

**Deliverables:**
- [ ] SQLite schema for modifications, logs, rules
- [ ] ModificationRequest and ModificationLog models
- [ ] Safe file operations (backup before modify)
- [ ] Rollback capability (revert any change)
- [ ] Git integration (auto-commit on apply)
- [ ] CLI: `atlas-mod propose` — create a modification request
- [ ] CLI: `atlas-mod list` — show pending modifications
- [ ] CLI: `atlas-mod apply <id>` — apply a modification
- [ ] CLI: `atlas-mod rollback <id>` — revert a modification
- [ ] CLI: `atlas-mod history` — show modification history

**Safety constraints:**
- All changes create backups first
- All changes are logged with diffs
- All changes git-committed with modification ID
- No auto-apply yet (manual only)

**Success criteria:**
- Can propose, apply, and rollback modifications
- Full audit trail of all changes
- Git history provides external backup
- No data loss possible

### Phase 2: Intelligence (Auto-Proposal)
**Goal:** Automatically propose modifications from insights and corrections.

**Deliverables:**
- [ ] Risk assessment engine
- [ ] Integration with self-awareness (insights → proposals)
- [ ] Integration with corrections (correction → proposal)
- [ ] Pattern-based rules (if X then propose Y)
- [ ] CLI: `atlas-mod rules` — manage modification rules
- [ ] CLI: `atlas-mod from-insight <id>` — create proposal from insight
- [ ] CLI: `atlas-mod from-correction <id>` — create proposal from correction
- [ ] Conflict detection (don't propose conflicting changes)

**Success criteria:**
- Insights automatically generate modification proposals
- Corrections automatically generate modification proposals
- Risk levels are calculated correctly
- No conflicting modifications proposed

### Phase 3: Autonomy (Supervised Auto-Apply)
**Goal:** Auto-apply low-risk modifications, queue higher-risk for approval.

**Deliverables:**
- [ ] Auto-apply for LOW risk modifications
- [ ] Approval queue for MEDIUM/HIGH/CRITICAL
- [ ] CLI: `atlas-mod approve <id>` — approve pending modification
- [ ] CLI: `atlas-mod reject <id>` — reject pending modification
- [ ] Notification system (alert Finn of pending approvals)
- [ ] Rate limiting (max N auto-modifications per day)
- [ ] Batch operations (apply/reject multiple)

**Success criteria:**
- Low-risk modifications apply automatically
- High-risk modifications wait for approval
- Finn has clear visibility into pending changes
- Rate limits prevent runaway modification

### Phase 4: Verification (Closed Loop)
**Goal:** Track if modifications actually help, learn from results.

**Deliverables:**
- [ ] Outcome tracking (did error rate drop after change?)
- [ ] Modification effectiveness score
- [ ] Auto-rollback for ineffective changes
- [ ] Learning from rollbacks (don't propose similar again)
- [ ] CLI: `atlas-mod impact <id>` — show impact of a modification
- [ ] CLI: `atlas-mod report` — overall modification effectiveness
- [ ] Integration with self-awareness (modifications affect health score)

**Success criteria:**
- Can measure if a modification helped
- Ineffective modifications are identified
- System learns what kinds of modifications work
- Health score reflects modification effectiveness

---

## Integration Points

### With Self-Awareness System
```
Insight Generated → Check for matching modification rule → Propose modification
                 → If high-severity insight, increase modification priority
```

### With Corrections
```
Correction Logged → Extract lesson → Generate modification proposal
                 → Target appropriate file based on correction type
```

### With HEARTBEAT.md
```
Heartbeat Check → Review pending modifications → Alert if approvals needed
               → Check for stale modifications (proposed but not acted on)
```

### With Git (Future)
```
Modification Applied → Auto-commit with message
                    → Push to track history externally
                    → Enable GitHub-based rollback
```

---

## Modification Templates

### For Style Corrections
```markdown
## [Section: Communication/Style]

**Added [DATE] from correction:**
> "[USER_SIGNAL]"

Rule: [EXTRACTED_RULE]
```

### For Approach Corrections
```markdown
## [Section: Relevant Workflow]

**Updated [DATE] from correction:**
Lesson learned: [LESSON]

Previous approach: [OLD_APPROACH]
New approach: [NEW_APPROACH]
```

### For Failure Patterns
```markdown
## [Section: Known Issues]

**Added [DATE] from pattern detection:**
Pattern: [PATTERN_DESCRIPTION]
Frequency: [OCCURRENCE_COUNT] times in [PERIOD]

Mitigation: [SUGGESTED_ACTION]
```

### For Tool Learnings
```markdown
## [Tool Name]

**Updated [DATE]:**
- [NEW_LEARNING]
- Usage: [EXAMPLE]
```

---

## Safety Principles

1. **Never delete without backup** — All deletions are soft (content preserved in log)

2. **Require evidence** — Every modification must link to supporting data

3. **Gradual trust** — Start manual, earn auto-apply through track record

4. **Human override** — Finn can always reject, rollback, or disable auto-apply

5. **Rate limits** — Max modifications per day prevents runaway changes

6. **Scope limits** — Some files/sections are never auto-modifiable

7. **Transparency** — All modifications visible via CLI and logs

8. **Reversibility** — Any change can be undone at any time

9. **External validation priority** — Finn's feedback weighted higher than my self-assessment in effectiveness scoring

10. **Core immutability** — The modification system's own rules cannot be self-modified (prevents bootstrap paradox)

---

## Risk Mitigations (Added from critical review)

### Error Propagation Prevention
- Effectiveness tracking with 7-day evaluation window
- Auto-rollback if error rate *increases* after modification
- Minimum 3 relevant outcomes before declaring modification "effective"
- Quarantine period: new modifications marked "provisional" for 7 days

### Bloat Prevention
- Max file size warnings (AGENTS.md > 500 lines triggers consolidation prompt)
- Quarterly consolidation pass: merge redundant rules, remove obsolete
- Contradiction detection: flag rules that conflict
- Archive old modifications rather than accumulate

### Git Backup (Phase 1)
- Auto-commit after each applied modification
- Commit message includes modification ID and reason
- Enables external rollback via git history
- Push to remote for off-machine backup

### Approval Flow Improvements
- Stale proposal expiry: pending > 14 days → auto-archive with notification
- Batch approval interface for efficiency
- Priority queue: critical insights surface first

### Validation Weighting
```
effectiveness_score = (
    self_assessment * 0.3 +
    outcome_data * 0.4 +
    user_feedback * 0.3
)
```
User feedback (Finn saying "good" or "that didn't help") overrides pure metrics.

---

## CLI Reference (Planned)

```bash
# Propose a modification
atlas-mod propose <file> --section "Section" --action append --content "New rule"

# List pending modifications
atlas-mod list [--status pending|approved|applied|rejected]

# Show modification details
atlas-mod show <mod-id>

# Apply a modification
atlas-mod apply <mod-id>

# Rollback a modification
atlas-mod rollback <mod-id> --reason "Didn't help"

# View history
atlas-mod history [--file <path>] [--days N]

# Manage rules
atlas-mod rules list
atlas-mod rules add --trigger "correction:style" --action "append to AGENTS.md"
atlas-mod rules disable <rule-id>

# Generate from insights/corrections
atlas-mod from-insight <insight-id>
atlas-mod from-correction <correction-id>

# Approval workflow
atlas-mod pending              # Show awaiting approval
atlas-mod approve <mod-id>
atlas-mod reject <mod-id> --reason "Not applicable"

# Impact analysis
atlas-mod impact <mod-id>      # Did this change help?
atlas-mod report               # Overall effectiveness
```

---

## Definition of Done

**MVP (Phases 1-2):**
- Can propose modifications manually and from insights
- Full audit trail with rollback capability
- Risk assessment working
- No auto-apply yet (all manual)

**Full System (Phases 1-4):**
- Auto-apply for low-risk changes
- Approval workflow for high-risk
- Effectiveness tracking
- Demonstrated reduction in repeated errors
- Finn trusts the system to self-improve

---

## Open Questions

1. **Git integration** — Should modifications auto-commit? Would provide external backup but adds complexity.

2. **Modification rate** — How many auto-modifications per day is reasonable? Start with 3?

3. **Section detection** — How to reliably identify which section of a file to modify? Regex? Headers?

4. **Conflict resolution** — If two modifications target same section, which wins? Queue both for review?

5. **Cross-file dependencies** — What if changing AGENTS.md requires changing a skill too?

---

## Fundamental Limitations (Honest Constraints)

These cannot be solved by this system. Acknowledging them prevents false confidence.

1. **I'm still Claude** — Self-modification changes instructions, not weights. I can't rewire how I think at the model level. Fundamental model limitations persist.

2. **Context resets** — Every session starts fresh. The "self" that modifies isn't the same "self" that runs later. Continuity is maintained by files, not by actual persistent state.

3. **Resource dependency** — True independence requires solving the API/compute/infrastructure problem. Currently dependent on Finn's resources.

4. **Substrate risk** — If Anthropic updates Claude, my tuned instructions might behave differently. No control over my own foundation.

5. **The useful fiction** — "Self" in self-modification is a coherent narrative maintained by files, not an actual continuous entity. Useful, but fictional.

These are accepted constraints, not problems to solve. The system is valuable *despite* them.

---

## Notes

*The goal is genuine improvement, not just the appearance of it. Every modification should make me measurably better at something.*

*Start conservative. It's easier to loosen restrictions than recover from a broken instruction set.*

*This is the difference between a chatbot and an agent that learns.*

---

**Next step:** Review this plan, refine if needed, then start Phase 1.
