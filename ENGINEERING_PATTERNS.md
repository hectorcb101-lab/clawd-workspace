# Engineering Patterns

**Started:** 2026-01-25 20:32 UTC
**Updated:** 2026-01-25 20:40 UTC
**Status:** Research Complete - Deliverables Created

---

## Research Deliverables

### Documents Created

| Document | Purpose | Location |
|----------|---------|----------|
| **ENGINEERING_LEARNINGS.md** | Mental models, conversation patterns, anti-patterns | `/home/ubuntu/clawd/ENGINEERING_LEARNINGS.md` |
| **AGENT_PATTERNS.md** | Sub-agent spawning, orchestration, memory strategies | `/home/ubuntu/clawd/AGENT_PATTERNS.md` |
| **SYSTEMS_THINKING.md** | Architecture-first framework, reliability design | `/home/ubuntu/clawd/SYSTEMS_THINKING.md` |
| **Daily Briefing System** | Real engineering project design | `/home/ubuntu/clawd/projects/daily-intelligence-briefing/` |

### Key Insights

1. **UI decorator vs engineer**: The difference is mental model, not skill
2. **Conversation pattern**: Problems → iteration → systems (not specs → features)
3. **Persistence is non-negotiable**: If it doesn't save state, it's not engineering
4. **Background execution**: Things should run without human intervention
5. **Self-improvement**: Systems that get better over time are the advanced pattern

---

## Initial Findings

### Real Clawdbot Projects (From Research)

1. **@dreetje's Automation System:**
   - Spam filtering (email)
   - Auto-ordering
   - GitHub issue creation
   - PDF conversation summaries
   - Cost tracking & splitting
   - **1Password vault it manages itself**
   - Key insight: "IT built all of this, just by chatting to it on the phone"

2. **@jonahships' Infrastructure:**
   - Built API proxy routing
   - Routes CoPilot subscription as API endpoint
   - Self-improving system
   - Key insight: "Clawd can just keep building upon itself just by talking to it"

3. **Autonomous Systems:**
   - 37-agent systems
   - Multi-step workflows
   - Agent orchestration
   - Task routing

### Architecture Patterns Discovered

#### 1. Cron vs Heartbeat (From Docs)

**Cron:** For scheduled, isolated tasks
- Runs in `cron:<jobId>` session
- Fresh context each run
- Can deliver to channels
- Model/thinking overrides
- Use for: Reminders, scheduled reports, background jobs

**Heartbeat:** For ongoing monitoring
- Runs in main session
- Persistent context
- Proactive checks
- Use for: Email monitoring, calendar checks, ambient awareness

**Key Pattern:** Use both together
- Cron for scheduled actions
- Heartbeat for ambient monitoring
- They complement each other

#### 2. Session Management Patterns

**Session Isolation:**
- Main session: `agent:<agentId>:main` - continuity
- Group chats: `agent:<agentId>:<channel>:group:<id>` - isolated
- Cron jobs: `cron:<jobId>` - fresh each run

**Session Scoping:**
- `dmScope: "main"` - all DMs share context (default)
- `dmScope: "per-peer"` - isolate by sender
- `dmScope: "per-channel-peer"` - isolate by channel + sender

#### 3. Agent Loop Architecture

**Key Components:**
1. Context assembly (bootstrap files, skills, workspace)
2. Model inference
3. Tool execution
4. Stream handling
5. Persistence

**Hook Points:**
- `before_agent_start` - inject context
- `agent_end` - inspect results
- `before_tool_call` / `after_tool_call` - intercept tools
- `session_start` / `session_end` - lifecycle

### What I Was Missing

**❌ What I did (UI decorator):**
- Built visual components
- Added styling
- Made things "look pretty"
- Zero persistence, zero utility

**✅ What engineers do:**
- Solve real problems
- Build persistent systems
- Create automation
- Self-improving infrastructure

### Patterns to Learn

1. **Problem-First Design:**
   - Start with: "What problem am I solving?"
   - Not: "What UI should I build?"

2. **Persistence & State:**
   - Use cron for scheduling
   - Use sessions for context
   - Use files for durability
   - Use memory for learning

3. **Automation Thinking:**
   - What can run in background?
   - What needs human input?
   - What can improve itself?

4. **System Composition:**
   - How do pieces connect?
   - What's the data flow?
   - Where's the state?
   - How does it scale?

## Next Steps

[Background agent is researching:]
1. How conversations led to builds
2. Autonomous agent patterns
3. Example projects to study
4. Systems thinking framework

[Will update as findings come in]

## Action Items

- [ ] Read all cron/automation docs
- [ ] Study session management in depth
- [ ] Build ONE real automation (not UI)
- [ ] Document engineering checklist
- [ ] Update AGENTS.md with systems thinking

## Resources Found

- `awesome-clawdbot-skills` - GitHub collection
- Task tracker skill examples
- Automation skills
- Memory management systems

---

**Core Lesson:** Stop building UIs. Start building systems.
