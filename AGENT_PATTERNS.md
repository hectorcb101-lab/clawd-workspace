# Agent Patterns: Orchestration & Multi-Agent Systems

**Date Created:** 2026-01-25
**Purpose:** Document patterns for sub-agent spawning, orchestration, and multi-agent workflows in Clawdbot
**Status:** Living document - patterns to use for building real systems

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [When to Spawn vs When to Do Inline](#when-to-spawn-vs-inline)
3. [Sub-Agent Spawning Patterns](#sub-agent-spawning-patterns)
4. [Agent Orchestration Strategies](#orchestration-strategies)
5. [Memory & Context Management](#memory-and-context)
6. [Long-Running Workflows](#long-running-workflows)
7. [Error Recovery & Retry Logic](#error-recovery)
8. [Practical Recipes](#practical-recipes)

---

## Core Concepts

### What is a Sub-Agent?

A sub-agent is a **fresh Claude instance** spawned by the main agent to work on a specific part of a problem. Each sub-agent has:

- **Own context window** (clean slate, no pollution from main conversation)
- **Specific task** (focused, well-defined work)
- **Independent execution** (can run in background or parallel with others)
- **Result reporting** (announces back to main agent when done)

**Key tool:** `sessions_spawn`

```typescript
sessions_spawn({
  task: "Analyze codebase for security vulnerabilities",
  label: "security-audit",
  model: "anthropic/claude-opus-4-5",
  runTimeoutSeconds: 600,
  cleanup: "keep"  // or "delete"
})
```

### Session Management in Clawdbot

**Session types:**

```typescript
// Main direct chat
agent:main:main

// Group chats
agent:main:group:<groupId>

// Cron jobs
agent:main:cron:<cronId>

// Hooks (webhooks, gmail pubsub)
agent:main:hook:<hookId>

// Sub-agents (spawned)
agent:main:subagent:<uuid>
```

**Session persistence:**
- Sessions stored as JSONL: `~/.clawdbot/agents/<agentId>/sessions/<sessionKey>.jsonl`
- Transcripts survive restarts
- Can fetch history with `sessions_history`
- Can send messages between sessions with `sessions_send`

**Session tools:**

| Tool | Purpose |
|------|---------|
| `sessions_list` | List active/recent sessions |
| `sessions_history` | Fetch transcript for a session |
| `sessions_send` | Send message to another session |
| `sessions_spawn` | Spawn a sub-agent |

### Multi-Agent Routing

Clawdbot supports **multiple isolated agents** in one Gateway:

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/clawd-personal",
        "model": "anthropic/claude-sonnet-4-5"
      },
      {
        "id": "work",
        "workspace": "~/clawd-work",
        "model": "anthropic/claude-opus-4-5"
      }
    ]
  },
  "bindings": [
    { "agentId": "personal", "match": { "channel": "whatsapp" } },
    { "agentId": "work", "match": { "channel": "telegram" } }
  ]
}
```

**Each agent has:**
- Own workspace (separate AGENTS.md, SOUL.md, memory)
- Own session store
- Own auth profiles
- Own skills directory

**Use cases:**
- Different personalities for different contexts (work vs personal)
- Different model choices per agent
- Isolated environments (family vs work)
- Multi-user setups (one Gateway, multiple people)

---

## When to Spawn vs Inline

### Spawn a Sub-Agent When:

✅ **Context window management**
- Processing large files that would pollute main context
- Analyzing entire codebases (thousands of lines)
- Research tasks with lots of web content

✅ **Concurrent work**
- Multiple independent tasks can run in parallel
- I/O-bound operations (API calls, web scraping)
- Map-reduce patterns (process many items simultaneously)

✅ **Code-driven LLM invocation**
- Main workflow is deterministic code
- Need LLM for specific decisions within the flow
- Return control to code after LLM call

✅ **Security isolation**
- Sub-agent needs different tool permissions
- Untrusted code execution
- Separate credentials/auth contexts

✅ **Long-running background work**
- Research that doesn't block main work
- Analysis tasks where results aren't immediately needed
- Periodic monitoring or polling

### Do Inline When:

❌ **Simple, quick operations**
- Reading a single file
- Running a quick command
- Small code changes

❌ **Sequential dependencies**
- Next step depends on previous result
- Building on conversation context
- User might want to intervene

❌ **Interactive work**
- User is providing input step-by-step
- Exploring a problem together
- Debugging with user feedback

---

## Sub-Agent Spawning Patterns

### Pattern 1: Parallel Research (Fan-Out)

**Problem:** Need to research multiple independent topics simultaneously

**Solution:** Spawn multiple sub-agents in parallel, gather results when done

```typescript
// Main agent creates research plan
const topics = [
  "React best practices for drag-and-drop",
  "TypeScript patterns for state management",
  "Modern CSS animation techniques"
];

// Spawn sub-agents in parallel (fire-and-forget)
for (const topic of topics) {
  sessions_spawn({
    task: `Research: ${topic}. Find 3-5 authoritative sources, summarize key points, provide code examples.`,
    label: `research-${topic.replace(/\s+/g, '-')}`,
    cleanup: "keep"
  });
}

// Sub-agents run in background, announce results when done
// Main agent can continue other work
```

**Benefits:**
- 3 sub-agents finish in ~same time as 1 sequential
- Main context stays clean
- Results come back as separate announcements
- Easy to review each research area independently

**Limitations:**
- No guaranteed order of completion
- Need to aggregate results manually
- Overhead of spawning multiple agents

### Pattern 2: Sequential Pipeline (Chain)

**Problem:** Task has dependencies - Step B needs output from Step A

**Solution:** Spawn sub-agents sequentially, passing results forward

```typescript
// Step 1: Research phase
const researchResult = await sessions_send({
  sessionKey: "subagent-research",
  message: "Research best practices for email classification",
  timeoutSeconds: 300
});

// Step 2: Planning phase (uses research)
const planResult = await sessions_send({
  sessionKey: "subagent-planning",
  message: `Based on research: ${researchResult.reply}\n\nCreate implementation plan for email classifier`,
  timeoutSeconds: 180
});

// Step 3: Implementation (uses plan)
const implResult = await sessions_send({
  sessionKey: "subagent-implementation",
  message: `Implement this plan: ${planResult.reply}`,
  timeoutSeconds: 600
});
```

**When to use:**
1. Research → Planning → Implementation
2. Schema design → Migration → Testing
3. Data fetch → Transform → Load (ETL)
4. Analysis → Report → Delivery

### Pattern 3: Background Non-Blocking Work

**Problem:** Need to do research/analysis but don't want to block current work

**Solution:** Spawn background sub-agent, check results later

```typescript
// Spawn background analysis
sessions_spawn({
  task: "Analyze codebase for performance bottlenecks. Check all components for unnecessary re-renders, large bundle sizes, and slow API calls.",
  label: "performance-audit",
  thinking: "extended",
  cleanup: "delete"  // Auto-cleanup after announce
});

// Continue main work immediately
// User: "Let's add the new feature..."
// (Main agent works on feature while performance audit runs in background)

// Later, performance audit finishes and announces results
// Main agent can address findings in next iteration
```

**Use cases:**
- Performance profiling
- Security audits
- Documentation generation
- Test coverage analysis
- Dependency updates check

### Pattern 4: Map-Reduce (Swarm Migration)

**Problem:** Need to process many items (e.g., update 100+ files)

**Solution:** Spawn swarm of sub-agents, each handling a batch

```typescript
// Example: Update YAML front-matter in 100 markdown files
const files = glob("**/*.md");  // 100 files
const batchSize = 10;
const batches = chunk(files, batchSize);  // 10 batches of 10 files

// Spawn sub-agents for each batch (parallel processing)
for (const batch of batches) {
  sessions_spawn({
    task: `Update YAML front-matter in these files: ${batch.join(', ')}. 
           Add 'updatedAt' field with current date.
           Verify YAML is valid after update.`,
    label: `batch-${batches.indexOf(batch)}`,
    cleanup: "delete"
  });
}

// 10 sub-agents process 100 files in parallel
// Finish in 1/10th the time of sequential processing
```

**High-volume use case:**
- Framework migrations (React 17 → 18 across entire codebase)
- Lint rule rollouts (apply new ESLint rule to all files)
- API updates (change all API calls to new endpoint format)
- Dependency upgrades (update imports across project)

**Anthropic insight:** Users spending $1000+/month on Claude Code are typically running swarm migrations

### Pattern 5: Quality Control Agent ("Karen")

**Problem:** Sub-agents claim tasks are "done" but didn't actually work

**Solution:** Specialized QA sub-agent that aggressively verifies work

```typescript
// Main implementation agent
sessions_spawn({
  task: "Implement email classifier feature",
  label: "implement-classifier"
});

// Quality control agent (spawned after implementation)
sessions_spawn({
  task: `You are Karen, the quality-control-enforcer.
  
  Your job: Aggressively detect BS and verify work is ACTUALLY done.
  
  Check the email classifier implementation:
  1. Does the code actually run? (npm run dev)
  2. Are there tests? Do they pass? (npm test)
  3. Does it handle edge cases? (empty email, malformed input, etc.)
  4. Are there any console errors?
  5. Is the API documented?
  6. Can you break it? (Try to make it fail)
  
  Be ruthless. If something is half-done or broken, say so.
  Don't accept "looks good" - PROVE it works.`,
  label: "qa-karen",
  model: "anthropic/claude-opus-4-5"  // Use best model for QA
});
```

**Why this works:**
- Separate context = no bias from implementation
- Specialized prompt = focused on verification
- Runs actual tests, not just code review
- Catches issues before they reach production

### Pattern 6: Role-Based AI Dev Team

**Problem:** Complex project needs different specializations

**Solution:** Spawn sub-agents with specific roles

```typescript
// Tech Lead (orchestrator)
const techLeadPlan = await sessions_send({
  sessionKey: "subagent-tech-lead",
  message: "Break down this feature into backend, frontend, API tasks"
});

// Parallel implementation
sessions_spawn({
  task: `Backend: ${techLeadPlan.backend}`,
  label: "backend-dev",
  model: "anthropic/claude-opus-4-5"
});

sessions_spawn({
  task: `Frontend: ${techLeadPlan.frontend}`,
  label: "frontend-dev",
  model: "anthropic/claude-sonnet-4-5"
});

sessions_spawn({
  task: `API: ${techLeadPlan.api}`,
  label: "api-dev",
  model: "anthropic/claude-opus-4-5"
});

// Documentation agent (background, non-blocking)
sessions_spawn({
  task: "Generate API documentation from code",
  label: "docs-agent",
  cleanup: "delete"
});
```

**Roles:**
- **Tech Lead:** Planning, architecture, task breakdown
- **Backend Dev:** Server logic, database, API endpoints
- **Frontend Dev:** UI components, state management
- **API Architect:** Endpoint design, validation, docs
- **QA Engineer:** Testing, verification, edge cases
- **DevOps:** Deployment, CI/CD, monitoring

---

## Orchestration Strategies

### Strategy 1: Domain-Based Parallel Splitting

**When:** Feature spans independent domains with no file overlap

**Pattern:**
```typescript
// NO file overlap between domains = safe to parallelize
sessions_spawn({
  task: "Frontend: Build React components for task list",
  label: "frontend",
  // Will modify: src/components/*, src/pages/*
});

sessions_spawn({
  task: "Backend: Build Express API for tasks",
  label: "backend",
  // Will modify: server/routes/*, server/models/*
});

sessions_spawn({
  task: "Database: Design schema and migrations",
  label: "database",
  // Will modify: migrations/*, schema.sql
});
```

**Critical rule:** Parallel agents must touch **different files**. File overlap = merge conflicts.

**How to verify:**
- List files each agent will modify
- Ensure zero overlap
- If overlap, make sequential or split differently

### Strategy 2: Dependency-Based Sequential Chaining

**When:** Task output feeds into next task

**Pattern:**
```typescript
// Sequential chain: A → B → C

// Step A: Schema design
const schema = await runSubAgent("Design database schema for tasks");

// Step B: API design (depends on schema)
const api = await runSubAgent(`Design API endpoints based on schema: ${schema}`);

// Step C: Frontend (depends on API)
const frontend = await runSubAgent(`Build UI components that call API: ${api}`);
```

**Common chains:**
1. Schema → API → Frontend
2. Research → Planning → Implementation
3. Implementation → Testing → Documentation
4. Analysis → Report → Recommendations

### Strategy 3: Background + Foreground Hybrid

**When:** Main work can proceed while background work happens

**Pattern:**
```typescript
// Background: Long-running analysis (doesn't block)
sessions_spawn({
  task: "Analyze entire codebase for security issues",
  label: "security-audit",
  cleanup: "delete"
});

// Foreground: Continue with main feature work
// (Main agent works on feature implementation)

// Security audit finishes later, announces findings
// Main agent addresses them in next iteration
```

**Use cases:**
- Security audits while building features
- Performance profiling while coding
- Documentation generation while implementing
- Test coverage analysis while adding features

---

## Memory and Context

### Sub-Agent Context Inheritance

**What sub-agents get:**
- `AGENTS.md` (operating instructions)
- `TOOLS.md` (tool notes)
- **NOT** SOUL.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md

**Why:** Sub-agents are task-focused workers, not personality-driven assistants

**Context isolation:**
```
Main Agent Context (polluted):
- 50 messages of conversation
- Explored 20 files
- Discussed 5 different approaches
- 10,000+ tokens used

Sub-Agent Context (clean):
- Only the task description
- Fresh context window
- Focused execution
- Zero prior baggage
```

**Benefit:** Sub-agents don't get confused by main conversation history

### Passing Context to Sub-Agents

**Bad (vague):**
```typescript
sessions_spawn({
  task: "Fix the authentication bug"
});
// Sub-agent: "Which bug? Where? How do I reproduce it?"
```

**Good (specific):**
```typescript
sessions_spawn({
  task: `Fix OAuth redirect loop bug:
  
  Context:
  - File: src/lib/auth.ts
  - Issue: Successful login redirects to /login instead of /dashboard
  - Reproduction: Login with Google → redirects to /login → infinite loop
  - Expected: Login → redirect to /dashboard
  - Error logs: ${errorLogs}
  
  Fix:
  1. Review redirect logic in auth.ts
  2. Check REDIRECT_URI configuration
  3. Test with actual Google OAuth flow
  4. Verify no other redirect paths are affected`
});
```

**Essential context:**
- **What:** Specific problem or task
- **Where:** File paths, line numbers
- **How to reproduce:** Steps to trigger the issue
- **Expected behavior:** What should happen
- **Actual behavior:** What's happening instead
- **Constraints:** Any limitations or requirements

### Agent-to-Agent Communication

**Direct messaging:**
```typescript
// Agent A sends to Agent B
sessions_send({
  sessionKey: "agent:work:main",
  message: "Please review the PR I just created: PR #42",
  timeoutSeconds: 300
});

// Agent B receives, processes, replies
// Reply goes back to Agent A
```

**Ping-pong conversation:**
- Max turns: 5 (configurable via `session.agentToAgent.maxPingPongTurns`)
- Either agent can end with `REPLY_SKIP`
- Prevents infinite loops

**Announce mechanism:**
```typescript
// Sub-agent finishes, runs announce step
// If replies ANNOUNCE_SKIP → stays silent
// Otherwise → posts to requester's chat channel

// Example announce:
`Status: success
Result: Implemented email classifier with 95% accuracy
Notes: Added tests, documentation, and example usage

Runtime: 5m12s
Tokens: 10,234 in / 3,456 out / 13,690 total
Cost: $0.42
Session: agent:main:subagent:abc123
Transcript: ~/.clawdbot/agents/main/sessions/agent:main:subagent:abc123.jsonl`
```

### Memory Persistence Patterns

**Session transcripts:**
- Stored as JSONL
- Survive Gateway restarts
- Can be fetched with `sessions_history`
- Useful for debugging, auditing, learning

**Workspace files (persistent memory):**
```
clawd/
├── AGENTS.md              # Operating instructions
├── MEMORY.md              # Long-term curated memory
├── memory/
│   ├── 2026-01-25.md      # Daily log (today)
│   ├── 2026-01-24.md      # Daily log (yesterday)
│   └── heartbeat-state.json  # Heartbeat tracking
├── .learnings/
│   ├── LEARNINGS.md       # Corrections, improvements
│   ├── ERRORS.md          # Failed commands, bugs
│   └── FEATURE_REQUESTS.md  # Missing capabilities
└── PROJECT_STATUS.md      # Current project state
```

**Pattern: Learning loop**
1. Sub-agent encounters error
2. Logs to `.learnings/ERRORS.md`
3. Main agent reviews periodically
4. Promotes valuable learnings to `AGENTS.md`
5. Future sub-agents inherit the knowledge

---

## Long-Running Workflows

### Pattern: Cron Jobs (Scheduled Tasks)

**Use case:** Periodic background work (daily briefing, weekly cleanup, monitoring)

**Setup:**
```bash
# List cron jobs
clawdbot cron list

# Add daily briefing
clawdbot cron add \
  --name daily-briefing \
  --schedule "0 8 * * *" \
  --task "Generate daily briefing: weather, calendar, top tasks" \
  --deliver telegram
```

**Cron session:**
- Session key: `agent:main:cron:daily-briefing`
- Runs at scheduled time
- Delivers result to specified channel
- Independent from main conversation

### Pattern: Webhook Triggers

**Use case:** React to external events (new email, GitHub PR, Slack mention)

**Example: Gmail Pub/Sub**
```json
{
  "hooks": {
    "gmail": {
      "enabled": true,
      "model": "openai/gpt-5.2-mini",
      "wakeMode": "now",
      "deliver": true,
      "messageTemplate": "New email from {from}: {subject}\n\n{snippet}\n\nBody:\n{body}"
    }
  }
}
```

**Flow:**
```
Gmail → Pub/Sub → Webhook → Clawdbot Hook Session → Process → Deliver to Chat
```

**Hook session:**
- Session key: `agent:main:hook:gmail`
- Triggered by external event
- Processes data and delivers result
- Can spawn sub-agents for complex processing

### Pattern: Long-Running Task with Checkpointing

**Problem:** Task might take hours, Gateway might restart

**Solution:** Save progress to files, resume from checkpoint

```typescript
// Checkpoint pattern
const CHECKPOINT_FILE = '.checkpoints/migration-progress.json';

// Load checkpoint
const checkpoint = existsSync(CHECKPOINT_FILE)
  ? JSON.parse(readFileSync(CHECKPOINT_FILE))
  : { processedFiles: [], currentBatch: 0 };

// Process next batch
const files = glob("**/*.tsx");
const remaining = files.filter(f => !checkpoint.processedFiles.includes(f));

for (const batch of chunk(remaining, 10)) {
  // Process batch
  await processBatch(batch);
  
  // Save checkpoint
  checkpoint.processedFiles.push(...batch);
  checkpoint.currentBatch++;
  writeFileSync(CHECKPOINT_FILE, JSON.stringify(checkpoint));
}
```

**Benefits:**
- Restart-safe
- Can monitor progress
- Can pause/resume
- Can parallelize with multiple agents sharing checkpoint

---

## Error Recovery & Retry Logic

### Pattern: Timeout Handling

```typescript
sessions_spawn({
  task: "Long-running analysis",
  runTimeoutSeconds: 600  // 10 minutes
});

// If timeout, sub-agent is aborted
// Announce includes: Status: timeout
// Can inspect partial work via session transcript
```

### Pattern: Retry on Failure

```typescript
async function resilientSubAgent(task: string, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await sessions_spawn({
        task,
        runTimeoutSeconds: 300
      });
      
      if (result.status === "ok") {
        return result;
      }
      
      // If error, log and retry
      console.log(`Attempt ${attempt} failed: ${result.error}`);
      
      if (attempt < maxRetries) {
        // Exponential backoff
        await sleep(Math.pow(2, attempt) * 1000);
      }
      
    } catch (error) {
      console.log(`Attempt ${attempt} exception: ${error}`);
    }
  }
  
  throw new Error(`Failed after ${maxRetries} attempts`);
}
```

### Pattern: Fallback Model

```typescript
// Try with Opus first, fall back to Sonnet if timeout/error
sessions_spawn({
  task: "Complex analysis",
  model: "anthropic/claude-opus-4-5",
  runTimeoutSeconds: 300
});

// If fails, retry with cheaper model
sessions_spawn({
  task: "Complex analysis (simplified for faster model)",
  model: "anthropic/claude-sonnet-4-5",
  runTimeoutSeconds: 180
});
```

---

## Practical Recipes

### Recipe 1: Code Review Workflow

```typescript
// 1. Spawn analysis sub-agents in parallel
sessions_spawn({
  task: "Review code quality: check for complexity, duplicates, code smells",
  label: "review-quality"
});

sessions_spawn({
  task: "Review security: check for vulnerabilities, unsafe patterns",
  label: "review-security"
});

sessions_spawn({
  task: "Review performance: check for bottlenecks, inefficient algorithms",
  label: "review-performance"
});

sessions_spawn({
  task: "Review tests: check coverage, quality, edge cases",
  label: "review-tests"
});

// 2. Sub-agents run in parallel, announce findings
// 3. Main agent aggregates results
// 4. Generate summary report
```

### Recipe 2: Multi-Step Feature Implementation

```typescript
// Sequential workflow with verification

// Step 1: Research
const research = await runSubAgent("Research best practices for drag-and-drop in React");

// Step 2: Design
const design = await runSubAgent(`Design component architecture based on: ${research}`);

// Step 3: Implement
sessions_spawn({
  task: `Implement: ${design}`,
  label: "implementation",
  model: "anthropic/claude-opus-4-5"
});

// Step 4: Test (parallel with implementation finishing)
sessions_spawn({
  task: "Write tests for drag-and-drop components",
  label: "testing"
});

// Step 5: QA (after implementation + testing)
sessions_spawn({
  task: "Verify drag-and-drop works correctly. Test all interactions.",
  label: "qa-verification"
});

// Step 6: Document (background)
sessions_spawn({
  task: "Generate documentation for drag-and-drop feature",
  label: "documentation",
  cleanup: "delete"
});
```

### Recipe 3: Data Pipeline (ETL)

```typescript
// Extract → Transform → Load

// Extract (parallel from multiple sources)
sessions_spawn({ task: "Fetch data from API A", label: "extract-a" });
sessions_spawn({ task: "Fetch data from API B", label: "extract-b" });
sessions_spawn({ task: "Fetch data from Database C", label: "extract-c" });

// Wait for extracts, then transform (sequential)
const dataA = await waitForSubAgent("extract-a");
const dataB = await waitForSubAgent("extract-b");
const dataC = await waitForSubAgent("extract-c");

const transformed = await runSubAgent(`Transform and merge: ${dataA}, ${dataB}, ${dataC}`);

// Load (single sub-agent)
sessions_spawn({
  task: `Load transformed data to destination: ${transformed}`,
  label: "load"
});
```

### Recipe 4: Self-Improving System

```typescript
// Continuous improvement loop

// 1. Monitor for errors
sessions_spawn({
  task: "Monitor logs for errors and failures",
  label: "monitor-errors",
  cleanup: "keep"  // Long-running
});

// 2. Periodically review learnings
// (Cron job: daily at 2am)
clawdbot cron add \
  --name review-learnings \
  --schedule "0 2 * * *" \
  --task "Review .learnings/ files. Promote valuable learnings to AGENTS.md. Fix recurring issues."

// 3. Generate improvement PRs
// (Spawned when learnings accumulate)
sessions_spawn({
  task: "Read .learnings/LEARNINGS.md. Create PR to fix top 3 issues.",
  label: "auto-improvement"
});
```

---

## Configuration & Best Practices

### Sub-Agent Tool Policy

**Default:** Sub-agents get all tools except session tools

**Override:**
```json
{
  "tools": {
    "subagents": {
      "tools": {
        "deny": ["gateway", "cron", "browser"],
        "allow": ["read", "exec", "write"]
      }
    }
  }
}
```

**Why restrict tools:**
- Security: Prevent sub-agents from modifying system
- Simplicity: Focused task agents don't need all tools
- Safety: Avoid accidental destructive operations

### Concurrency Limits

**Configuration:**
```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxConcurrent": 8  // Default: 8
      }
    }
  }
}
```

**Considerations:**
- More concurrent = faster but more resource usage
- High concurrency can overwhelm APIs or databases
- Monitor token usage and costs
- Start conservative, scale up if needed

### Cost Management

**Use cheaper models for sub-agents:**
```typescript
// Main agent: Opus 4.5 (expensive, high quality)
// Sub-agents: Sonnet 4.5 or Haiku (cheaper, faster)

sessions_spawn({
  task: "Simple analysis task",
  model: "anthropic/claude-sonnet-4-5"  // Override to cheaper model
});
```

**Cleanup strategy:**
```typescript
// For background tasks that don't need history
sessions_spawn({
  task: "Generate daily report",
  cleanup: "delete"  // Auto-archive after announce
});

// For important work you want to review later
sessions_spawn({
  task: "Critical feature implementation",
  cleanup: "keep"  // Keep transcript for debugging
});
```

---

## Summary

### When to Use Sub-Agents

✅ **Context management:** Large files, codebases
✅ **Parallelization:** Independent tasks
✅ **Background work:** Non-blocking research
✅ **Isolation:** Security, permissions, testing
✅ **Specialization:** Role-based task delegation

### Orchestration Principles

1. **Parallel when possible** (independent domains, no file overlap)
2. **Sequential when necessary** (dependencies, shared state)
3. **Background for non-blocking** (research, analysis)
4. **Clear task definitions** (specific, with context)
5. **Proper error handling** (timeouts, retries, fallbacks)

### Key Takeaways

- Sub-agents are **fresh contexts** with **focused tasks**
- Use `sessions_spawn` for fire-and-forget, `sessions_send` for request-response
- **Plan orchestration:** Draw the workflow before spawning agents
- **Pass complete context:** Don't make sub-agents guess
- **Verify results:** Use QA agents to check work
- **Learn and improve:** Log learnings, promote to memory, iterate

---

**Next:** Build a real project using these patterns. Apply orchestration to solve an actual problem, not just demos.
