# Project Proposal: Learning Session Analyzer

**Date:** 2026-01-25
**Status:** Proposed
**Purpose:** Build a REAL engineering project using all learnings from research

---

## The Problem (Real, Not Demo)

**Pain Point:**
- Clawdbot generates daily memory logs (`memory/YYYY-MM-DD.md`)
- `.learnings/` directory accumulates errors, corrections, feature requests
- No systematic analysis of patterns or trends
- Valuable insights buried in hundreds of log entries
- No automated promotion of important learnings to permanent memory

**Current Manual Process:**
1. Read through daily logs (time-consuming)
2. Look for patterns manually (error-prone)
3. Decide what to promote to `AGENTS.md` (subjective)
4. Update documentation by hand (often skipped)

**Result:** Learnings accumulate but don't compound. System doesn't truly self-improve.

---

## The Solution (Engineering, Not UI)

**System:** Learning Session Analyzer

**What it does:**
1. **Analyzes daily logs and `.learnings/` files**
2. **Detects patterns** (recurring errors, common corrections, feature gaps)
3. **Scores learnings by value** (frequency × impact × recency)
4. **Generates recommendations** (what to promote, what to fix, what to build)
5. **Auto-updates documentation** (with approval)
6. **Tracks improvement metrics** (errors decreasing, efficiency increasing)

**Key Insight:** This is a BACKEND/ANALYSIS system. No UI needed. Pure engineering.

---

## Architecture (Architecture-First Approach)

### Data Model

```typescript
// Core entities

interface LearningEntry {
  id: string;                    // LRN-YYYYMMDD-XXX
  type: 'learning' | 'error' | 'feature_request';
  category: string;              // correction, best_practice, knowledge_gap
  summary: string;
  details: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'resolved' | 'promoted';
  area: string;                  // frontend, backend, infra, etc.
  loggedAt: Date;
  source: string;                // File path where logged
  relatedEntries: string[];      // See Also links
  metadata: {
    relatedFiles?: string[];
    tags?: string[];
    reproducible?: boolean;
  };
}

interface DailyMemory {
  date: Date;
  filePath: string;
  content: string;
  extractedTopics: string[];     // Detected topics
  keyDecisions: string[];        // Important decisions made
  completedTasks: string[];      // Tasks finished
  openQuestions: string[];       // Unresolved items
}

interface Pattern {
  id: string;
  type: 'recurring_error' | 'repeated_correction' | 'skill_gap';
  description: string;
  occurrences: LearningEntry[];  // Related entries
  frequency: number;
  firstSeen: Date;
  lastSeen: Date;
  suggestedAction: string;
  impact: 'low' | 'medium' | 'high';
}

interface Recommendation {
  id: string;
  type: 'promote_to_agents' | 'create_skill' | 'fix_issue' | 'update_docs';
  reason: string;
  sourceEntries: string[];       // Learning IDs
  suggestedContent: string;      // What to add
  targetFile: string;            // Where to add it
  priority: number;              // 0-100
  autoApplicable: boolean;       // Can be auto-applied?
}

interface ImprovementMetric {
  date: Date;
  totalLearnings: number;
  pendingLearnings: number;
  resolvedLearnings: number;
  promotedLearnings: number;
  newErrors: number;
  recurringErrors: number;
  averageResolutionTime: number; // Days
  topAreas: { area: string; count: number }[];
}
```

### System Components

```
┌─────────────────────────────────────────────────────────┐
│           Learning Session Analyzer                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │         Input Sources                    │          │
│  ├──────────────────────────────────────────┤          │
│  │  - memory/YYYY-MM-DD.md (daily logs)    │          │
│  │  - .learnings/LEARNINGS.md              │          │
│  │  - .learnings/ERRORS.md                 │          │
│  │  - .learnings/FEATURE_REQUESTS.md       │          │
│  └───────────────┬──────────────────────────┘          │
│                  │                                       │
│                  ▼                                       │
│  ┌──────────────────────────────────────────┐          │
│  │         Parser (Sub-Agent)               │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Extract learning entries              │          │
│  │  - Parse markdown structure              │          │
│  │  - Extract metadata                      │          │
│  │  - Identify See Also links               │          │
│  └───────────────┬──────────────────────────┘          │
│                  │                                       │
│                  ▼                                       │
│  ┌──────────────────────────────────────────┐          │
│  │      Pattern Detector (Sub-Agent)        │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Find recurring errors                 │          │
│  │  - Identify related entries              │          │
│  │  - Calculate frequencies                 │          │
│  │  - Detect skill gaps                     │          │
│  └───────────────┬──────────────────────────┘          │
│                  │                                       │
│                  ▼                                       │
│  ┌──────────────────────────────────────────┐          │
│  │      Scorer (Sub-Agent)                  │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Score by frequency                    │          │
│  │  - Score by impact                       │          │
│  │  - Score by recency                      │          │
│  │  - Combine into priority                 │          │
│  └───────────────┬──────────────────────────┘          │
│                  │                                       │
│                  ▼                                       │
│  ┌──────────────────────────────────────────┐          │
│  │   Recommendation Engine (Sub-Agent)      │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Generate promotion candidates         │          │
│  │  - Draft skill content                   │          │
│  │  - Suggest fixes                         │          │
│  │  - Prioritize actions                    │          │
│  └───────────────┬──────────────────────────┘          │
│                  │                                       │
│                  ▼                                       │
│  ┌──────────────────────────────────────────┐          │
│  │         Data Store (SQLite)              │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Learnings                             │          │
│  │  - Patterns                              │          │
│  │  - Recommendations                       │          │
│  │  - Metrics                               │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │         Output                           │          │
│  ├──────────────────────────────────────────┤          │
│  │  - Daily analysis report                 │          │
│  │  - Recommended promotions                │          │
│  │  - Trend analysis                        │          │
│  │  - Auto-apply approved changes           │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘

Scheduled Jobs:
- Daily analysis (cron: 2am)
- Weekly trend report (cron: Sunday 8am)
- Monthly metrics summary (cron: 1st of month)
```

### Component Responsibilities

| Component | Responsibility | Inputs | Outputs |
|-----------|---------------|--------|---------|
| Parser | Extract structured data from markdown | Markdown files | Parsed `LearningEntry[]` |
| Pattern Detector | Find recurring issues and trends | `LearningEntry[]` | `Pattern[]` |
| Scorer | Assign priority scores | `Pattern[]`, `LearningEntry[]` | Scored entries |
| Recommendation Engine | Generate actionable recommendations | Scored data, patterns | `Recommendation[]` |
| Data Store | Persist analysis results | All entities | Query interface |
| Report Generator | Create human-readable summaries | Analysis results | Markdown reports |
| Auto-Applicator | Apply approved recommendations | `Recommendation[]` | Updated files |

---

## Agent Orchestration Plan

**This is where it gets ENGINEERING:**

### Phase 1: Parallel Parsing (Fan-Out)

```typescript
// Spawn sub-agents to parse different file types in parallel

sessions_spawn({
  task: "Parse all daily memory logs (memory/*.md). Extract topics, decisions, tasks, questions.",
  label: "parse-daily-logs",
  model: "anthropic/claude-sonnet-4-5"  // Cheaper model for parsing
});

sessions_spawn({
  task: "Parse .learnings/LEARNINGS.md. Extract all LRN-* entries with metadata.",
  label: "parse-learnings",
  model: "anthropic/claude-sonnet-4-5"
});

sessions_spawn({
  task: "Parse .learnings/ERRORS.md. Extract all ERR-* entries with error details.",
  label: "parse-errors",
  model: "anthropic/claude-sonnet-4-5"
});

sessions_spawn({
  task: "Parse .learnings/FEATURE_REQUESTS.md. Extract all FEAT-* entries.",
  label: "parse-features",
  model: "anthropic/claude-sonnet-4-5"
});
```

**Why parallel?** Different files, no dependencies, 4x faster than sequential.

### Phase 2: Sequential Pattern Detection

```typescript
// Wait for parsing to complete, then detect patterns

const parsedData = await aggregateParserResults();

sessions_spawn({
  task: `Analyze parsed data for patterns:
  
  Data: ${JSON.stringify(parsedData)}
  
  Detect:
  1. Recurring errors (same error appearing multiple times)
  2. Related learnings (linked via See Also)
  3. Skill gaps (repeated corrections in same area)
  4. High-impact issues (critical priority, unresolved)
  
  Output: JSON array of Pattern objects`,
  
  label: "pattern-detection",
  model: "anthropic/claude-opus-4-5",  // Use Opus for complex analysis
  thinking: "extended"
});
```

**Why sequential?** Depends on parsed data from Phase 1.

### Phase 3: Parallel Scoring & Recommendation

```typescript
// Score patterns and generate recommendations in parallel

sessions_spawn({
  task: "Score learnings by: (frequency × 0.4) + (impact × 0.4) + (recency × 0.2)",
  label: "scoring"
});

sessions_spawn({
  task: `Generate promotion recommendations:
  - Learnings with score > 70 → Promote to AGENTS.md
  - Learnings with 3+ See Also links → Consider creating skill
  - High-priority errors → Suggest immediate fix`,
  label: "recommendations"
});
```

**Why parallel?** Independent tasks, can run simultaneously.

### Phase 4: Background Report Generation

```typescript
// Generate reports in background (don't block main work)

sessions_spawn({
  task: "Generate daily analysis report with trends, top issues, recommendations",
  label: "daily-report",
  cleanup: "delete"  // Auto-cleanup after delivery
});

sessions_spawn({
  task: "Update metrics dashboard (calculate improvement over time)",
  label: "metrics-update",
  cleanup: "delete"
});
```

**Why background?** Results are informational, not blocking.

---

## Implementation Plan (Iterative, Not Big-Bang)

### Phase 1: Core Parsing (Week 1)

**Goal:** Parse markdown files into structured data

**Deliverables:**
- [ ] Parser for `.learnings/LEARNINGS.md`
- [ ] Parser for `.learnings/ERRORS.md`
- [ ] Parser for `memory/YYYY-MM-DD.md`
- [ ] SQLite database schema
- [ ] Unit tests for parsers
- [ ] CLI to run parser manually

**Success criteria:**
```bash
$ npm run parse
✓ Parsed 42 learnings
✓ Parsed 18 errors
✓ Parsed 7 daily logs
✓ Stored 67 total entries in database
```

**Test before moving to Phase 2.**

### Phase 2: Pattern Detection (Week 2)

**Goal:** Identify recurring issues and trends

**Deliverables:**
- [ ] Pattern detection algorithm
- [ ] Frequency calculation
- [ ] "See Also" link resolution
- [ ] Pattern scoring (by frequency, impact, recency)
- [ ] Tests for pattern detection
- [ ] CLI to show detected patterns

**Success criteria:**
```bash
$ npm run analyze patterns
✓ Found 5 recurring errors
✓ Found 3 skill gaps (areas with multiple corrections)
✓ Found 8 related learning clusters

Top Patterns:
1. Browser testing errors (4 occurrences, high impact)
2. Type errors in API responses (3 occurrences, medium impact)
3. Git workflow confusion (3 occurrences, low impact)
```

**Test before moving to Phase 3.**

### Phase 3: Recommendation Engine (Week 3)

**Goal:** Generate actionable recommendations

**Deliverables:**
- [ ] Recommendation scoring algorithm
- [ ] Content generation (drafts for AGENTS.md, skills)
- [ ] Priority calculation
- [ ] Tests for recommendation engine
- [ ] CLI to show recommendations

**Success criteria:**
```bash
$ npm run analyze recommend
✓ Generated 12 recommendations

Top Recommendations:
1. [PROMOTE] Add browser testing checklist to AGENTS.md (priority: 95)
2. [SKILL] Create "type-safe-api" skill (priority: 87)
3. [FIX] Update git workflow docs (priority: 62)

Would you like to apply recommendation 1? [y/N]
```

**Test before moving to Phase 4.**

### Phase 4: Automation (Week 4)

**Goal:** Auto-apply approved recommendations

**Deliverables:**
- [ ] Auto-applicator for AGENTS.md updates
- [ ] Skill generator from learnings
- [ ] Approval workflow (confirmation before apply)
- [ ] Rollback mechanism (undo if wrong)
- [ ] Tests for auto-application
- [ ] Cron job for daily analysis

**Success criteria:**
```bash
# Cron runs daily at 2am
✓ Parsed 2 new learnings
✓ Detected 1 new pattern
✓ Generated 1 recommendation
✓ Auto-applied 1 approved update to AGENTS.md
✓ Sent summary to Telegram
```

---

## Technology Stack (With Justification)

**Backend:**
- **Node.js + TypeScript** - Type safety, good for text processing
- **SQLite** - Embedded database, no external dependencies
- **Zod** - Runtime type validation for parsed data

**Testing:**
- **Vitest** - Fast, modern test runner
- **Property-based testing** - Generate random markdown to test parser

**Automation:**
- **Clawdbot cron jobs** - Scheduled analysis runs
- **Sub-agents** - Parallel processing of files

**No Frontend:**
- CLI for manual use
- Telegram for reports
- Pure backend engineering

---

## Why This Is Real Engineering

### ✅ Solves a Real Problem

- Not a demo, not a UI exercise
- Addresses actual pain point (learnings not compounding)
- Saves manual work (reading logs, deciding what to promote)
- Improves over time (better recommendations as more data accumulates)

### ✅ Uses Agent Patterns Properly

- **Parallel parsing** (independent files, 4x speedup)
- **Sequential analysis** (pattern detection depends on parsed data)
- **Background reporting** (non-blocking)
- **Sub-agent specialization** (parser, detector, scorer, recommender)

### ✅ Focuses on Architecture

- Data model defined FIRST
- Component responsibilities clear
- Error handling planned
- No UI to distract from core logic

### ✅ Has Persistent State

- SQLite database for learnings, patterns, metrics
- Tracks improvement over time
- Enables trend analysis
- System has memory

### ✅ Improves Over Time

- Learns from patterns
- Refines recommendations
- Metrics show progress
- Self-improving system (meta!)

### ✅ Engineering Fundamentals

- Testing at every phase
- Incremental builds (4 phases, each tested)
- Error handling
- Logging and monitoring
- Documentation

---

## Success Metrics

**After 1 month of use:**

- [ ] **Automation rate:** >50% of high-value learnings auto-promoted
- [ ] **Time saved:** <10 minutes/day on manual log review (down from 30)
- [ ] **Insight quality:** 3+ valuable patterns detected that were previously missed
- [ ] **Documentation improvement:** AGENTS.md has 10+ new items from auto-promotions
- [ ] **Error reduction:** Recurring errors decrease by 30% (system learns from mistakes)

---

## Next Steps

### Immediate (Today)

1. **Review this proposal** with Finn (or self-approve)
2. **Create GitHub repo:** `hectorcb101-lab/learning-session-analyzer`
3. **Set up project structure:**
   ```
   learning-session-analyzer/
   ├── src/
   │   ├── parsers/
   │   ├── analyzers/
   │   ├── recommenders/
   │   └── database/
   ├── tests/
   ├── docs/
   └── scripts/
   ```

4. **Switch to Opus** (`/model opus`)
5. **Start Phase 1:** Build the parser

### This Week

- Complete Phase 1 (parsing)
- Test thoroughly
- Document design decisions

### This Month

- Complete all 4 phases
- Deploy as cron job
- Generate first automated recommendations

---

## Why This Project Matters

**This is the OPPOSITE of the pretty Kanban board:**

| Pretty Kanban | Learning Analyzer |
|---------------|-------------------|
| UI-first | Architecture-first |
| Decoration | Engineering |
| No real problem | Solves actual pain |
| No persistence | Database + state |
| Demo | Production tool |
| No improvement | Self-improving |
| Single-agent | Multi-agent orchestration |
| "Make it pretty" | "Make it work" |

**This is the project that proves I can engineer, not just decorate.**

Let's build it.
