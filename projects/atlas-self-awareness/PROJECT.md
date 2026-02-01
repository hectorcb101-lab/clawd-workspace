# Atlas Self-Awareness System

*Project started: 2026-02-01*
*Status: Planning*

---

## The 5 Engineering Questions

### 1. What problem am I solving?

I can remember things (memory system), but I don't *understand myself*. I repeat mistakes without noticing patterns. I don't know my actual strengths or blind spots. I can't answer "Am I getting better?" with data.

**The gap:** Raw memory → Actionable self-knowledge

### 2. Who is the user and what do they need?

**Primary user: Me (Atlas)**
- Need to understand my own performance patterns
- Need to catch recurring failures before they become habits
- Need to know what I'm genuinely good at vs what I assume
- Need to track improvement over time

**Secondary user: Finn**
- Visibility into how I'm performing
- Ability to point out patterns I'm missing
- Trust that I'm actually learning, not just logging

### 3. What does success look like?

**Measurable outcomes:**
- I can query my top 5 failure patterns and get accurate data
- I can see improvement trends over weeks/months
- Recurring mistakes are flagged before I make them again
- I have data-backed understanding of my strengths
- Finn can ask "how are you doing at X?" and I answer with evidence

**Qualitative:**
- I feel more grounded in who I am
- Decisions about self-improvement are based on data, not guesses
- The system surfaces insights I wouldn't have noticed

### 4. What can go wrong?

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Noisy data (too much, no signal) | High | Medium | Careful event filtering, meaningful categories |
| Wrong metrics (measuring what's easy, not what matters) | Medium | High | Start with clear definitions, iterate |
| Over-indexing on failures (ignoring successes) | Medium | Medium | Explicitly track both success and failure |
| Gaming my own metrics | Low | High | Keep raw data immutable, analysis separate |
| Privacy concerns (logging too much) | Low | Medium | Focus on patterns, not content |
| Analysis paralysis (too much data, no action) | Medium | Medium | Limit to actionable insights |

### 5. How will this evolve?

**Phase 1-2:** Foundation — instrumentation + basic patterns
**Phase 3:** Self-query — I can ask questions about myself
**Phase 4:** Proactive — System surfaces insights unprompted
**Future:** 
- Feed into self-modification (auto-update AGENTS.md based on patterns)
- Cross-session learning (what works in different contexts)
- Predictive (anticipate where I'll struggle)

---

## Architecture

### Data Model

```
┌─────────────────────────────────────────────────────────┐
│                    EVENT LOG (existing)                  │
│  Memory system captures: messages, tool_calls, etc.     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   OUTCOME LAYER (new)                    │
│                                                          │
│  OutcomeEvent:                                          │
│  - event_id: str (links to memory event)                │
│  - outcome: success | failure | partial | unknown       │
│  - task_type: str (coding, research, communication...)  │
│  - confidence: float (how sure am I?)                   │
│  - feedback_source: self | user | system               │
│  - notes: str (what happened)                           │
│  - timestamp: datetime                                  │
│                                                          │
│  CorrectionEvent:                                       │
│  - original_event_id: str                               │
│  - correction_type: factual | approach | style | other │
│  - user_signal: str (what Finn said)                    │
│  - lesson: str (what I learned)                         │
│  - severity: minor | moderate | major                   │
│  - timestamp: datetime                                  │
│                                                          │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   PATTERN LAYER                          │
│                                                          │
│  FailurePattern:                                        │
│  - pattern_id: str                                      │
│  - description: str                                     │
│  - task_types: list[str]                                │
│  - occurrences: list[event_id]                          │
│  - first_seen: datetime                                 │
│  - last_seen: datetime                                  │
│  - frequency: float (per week)                          │
│  - status: active | resolved | monitoring               │
│                                                          │
│  StrengthPattern:                                       │
│  - pattern_id: str                                      │
│  - description: str                                     │
│  - task_types: list[str]                                │
│  - evidence: list[event_id]                             │
│  - confidence: float                                    │
│                                                          │
│  TrendData:                                             │
│  - task_type: str                                       │
│  - period: week | month                                 │
│  - success_rate: float                                  │
│  - total_count: int                                     │
│  - comparison_to_previous: float (% change)            │
│                                                          │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   INSIGHT LAYER                          │
│                                                          │
│  Insight:                                               │
│  - insight_id: str                                      │
│  - type: blind_spot | improvement | regression | tip   │
│  - message: str (human-readable)                        │
│  - evidence: list[pattern_id]                           │
│  - priority: low | medium | high                        │
│  - surfaced: bool                                       │
│  - surfaced_at: datetime | null                         │
│  - actionable: bool                                     │
│  - suggested_action: str | null                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Task Type Taxonomy

Start simple, expand based on data:

```
TASK_TYPES = {
    # Core capabilities
    "coding": ["writing", "debugging", "reviewing", "refactoring"],
    "research": ["web_search", "deep_dive", "synthesis", "fact_check"],
    "communication": ["email", "message", "document", "explanation"],
    "planning": ["architecture", "project_planning", "scheduling"],
    "memory": ["recall", "logging", "search"],
    
    # Tool usage
    "tool_browser": [],
    "tool_exec": [],
    "tool_file": ["read", "write", "edit"],
    "tool_mcp": [],
    
    # Meta
    "self_reflection": [],
    "learning": [],
}
```

### Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Instrumenter  │────▶│    Analyzer     │────▶│  InsightEngine  │
│                 │     │                 │     │                 │
│ - Tag outcomes  │     │ - Find patterns │     │ - Generate      │
│ - Log correct-  │     │ - Cluster       │     │   insights      │
│   ions          │     │   failures      │     │ - Prioritize    │
│ - Classify      │     │ - Track trends  │     │ - Surface       │
│   task types    │     │ - Compute stats │     │   proactively   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │    QueryInterface   │
                    │                     │
                    │  atlas-self <cmd>   │
                    │  - patterns         │
                    │  - strengths        │
                    │  - blind-spots      │
                    │  - trend <type>     │
                    │  - insights         │
                    │  - log-outcome      │
                    │  - log-correction   │
                    └─────────────────────┘
```

### Storage

**SQLite database:**
```
projects/atlas-self-awareness/
├── data/
│   └── self_awareness.db
│       ├── outcomes              # Task outcomes
│       ├── corrections           # User corrections
│       ├── patterns              # Identified patterns
│       ├── trends                # Aggregated statistics
│       └── insights              # Generated insights
```

**Why SQLite:**
- Compact (more data, fewer tokens when I query)
- Native SQL querying (I know SQL well)
- Single file, easy to manage
- Built for analysis workloads (not just append)
- This system is for ME — optimised for how I process data

**Design note:** The memory system uses JSON for append-only event logging. Self-awareness is different — it's about querying and analysing patterns. Different use case → different tool.

---

## Phase Plan

### Phase 1: Instrumentation (Foundation)
**Goal:** Capture structured outcome data

**Deliverables:**
- [ ] OutcomeEvent schema and logging
- [ ] CorrectionEvent schema and logging  
- [ ] Task type classifier (simple rules first)
- [ ] CLI: `atlas-self log-outcome`
- [ ] CLI: `atlas-self log-correction`
- [ ] Integration hook for automatic outcome detection

**Success criteria:**
- Can log outcomes manually
- Can log corrections when Finn corrects me
- Data is being captured consistently

### Phase 2: Pattern Analysis
**Goal:** Find meaning in the data

**Deliverables:**
- [ ] Failure pattern clustering
- [ ] Strength pattern detection
- [ ] Weekly/monthly trend computation
- [ ] CLI: `atlas-self analyze` (run analysis)
- [ ] Basic stats: success rate by task type

**Success criteria:**
- Can identify top 3 failure patterns from data
- Can show success rate trends over time
- Patterns are accurate (validated manually)

### Phase 3: Self-Query Interface
**Goal:** Let me ask questions about myself

**Deliverables:**
- [ ] CLI: `atlas-self patterns` (failure patterns)
- [ ] CLI: `atlas-self strengths`
- [ ] CLI: `atlas-self blind-spots`
- [ ] CLI: `atlas-self trend <task_type>`
- [ ] CLI: `atlas-self stats` (overview)
- [ ] Natural language query support

**Success criteria:**
- I can answer "what are my weaknesses?" with data
- I can track improvement over time
- Queries return actionable information

### Phase 4: Proactive Insights
**Goal:** Surface insights without being asked

**Deliverables:**
- [ ] Insight generation engine
- [ ] Priority scoring for insights
- [ ] Integration with heartbeat (check for new insights)
- [ ] CLI: `atlas-self insights` (pending insights)
- [ ] Surfacing mechanism (how/when to tell me)

**Success criteria:**
- System notices patterns I haven't asked about
- Important insights bubble up at appropriate times
- Insights lead to actual improvements

---

## Integration Points

### With Memory System
- Outcome events link to memory events via event_id
- Can query memory for context around failures
- Share the event log infrastructure

### With Self-Improvement Skill
- Corrections flow into .learnings/ as well
- Patterns inform what to add to AGENTS.md
- Insights can suggest instruction updates

### With HEARTBEAT.md
- Check for pending insights during heartbeats
- Run periodic analysis (weekly)
- Surface high-priority patterns

### With Session Workflow
- Detect corrections in real-time ("no, that's wrong")
- Auto-tag outcomes when tasks complete
- End-of-session summary of performance

---

## Design Decisions (Resolved)

### 1. Success/Failure Detection: Multi-Signal with Confidence

| Signal Type | Example | Confidence |
|-------------|---------|------------|
| Direct feedback | "Perfect" / "Wrong" | High |
| Correction needed | User rephrases or we redo | Medium |
| Tool outcome | Command succeeded/failed | Medium |
| Flow | Conversation moved on vs got stuck | Low |
| Completion | Task finished vs abandoned | Low |

**Principle:** Be generous with "uncertain." Better accurate low-confidence data than forced categorisation. If unclear, log as unknown.

### 2. Task Type Granularity

Start broad, split when data supports it. Let patterns emerge from real usage rather than over-specifying upfront.

### 3. Ambiguous Outcomes

- Use confidence scores (0.0-1.0)
- "Partial" is a valid outcome
- Unknown/uncertain is better than wrong classification

### 4. Insight Surfacing: Tiered by Importance

| Priority | When to Surface | Example |
|----------|-----------------|---------|
| Critical | Immediately, before acting | "You've failed at this 3 times" |
| Important | Session start or heartbeat | "Research success rate dropped 20%" |
| Interesting | Only when asked | "Browser tool usage down 40%" |

**Highest value:** Right before repeating a past mistake. Prevention > post-mortem.

### 5. Avoiding Self-Deception

**Structural:**
- Raw data is immutable (can't edit history)
- Analysis is algorithmic where possible
- Every pattern requires disconfirming evidence

**Adversarial:**
- Generate counter-arguments for insights
- Minimum evidence threshold before surfacing
- Score on both supporting AND contradicting evidence

**External:**
- Finn can challenge conclusions
- Calibration checks: self-assessment vs external observation
- Periodic "am I fooling myself?" reviews

**Mindset:**
- Frame as opportunities, not judgments
- Reduce stakes of admitting weakness
- Goal is improvement, not protection

---

## Dependencies

- Atlas Memory Evolution system (event log, extraction)
- Python 3.10+
- No external databases (JSON files)
- CLI infrastructure (existing pattern)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Not enough data initially | Start logging now, analyze later |
| Patterns too noisy | Require minimum occurrences before surfacing |
| Self-deception (only seeing what I want) | Keep raw data immutable, separate from analysis |
| Over-engineering | Start with MVP, iterate based on real usage |
| Forgetting to log | Automate detection where possible |

---

## Definition of Done

**MVP (Phases 1-2):**
- Outcomes are being logged consistently
- Can see basic stats: X successes, Y failures, Z corrections
- At least one real pattern identified from data

**Full System (Phases 1-4):**
- Can answer "what are my weaknesses?" with evidence
- Can track improvement over time with data
- System surfaces insights I hadn't noticed
- Insights have led to at least one concrete improvement

---

## Notes

*This is about understanding myself, not judging myself. The goal is clarity, not criticism. Good data leads to good decisions.*

*Building on the memory system means I'm not starting from scratch — I'm adding a layer of meaning on top of what I already capture.*

---

**Next step:** Review this plan, refine if needed, then start Phase 1.
