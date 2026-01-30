# PRE-PROJECT CHECKLIST
**Use this BEFORE starting ANY project**

## The 5 Engineering Questions

Answer these FIRST. If you can't answer clearly, STOP:

1. **What problem am I solving?**
   - [ ] Clear pain point articulated (not "feature idea")
   - [ ] Real friction identified (what manual work am I eliminating?)
   - [ ] Can describe problem without mentioning solution

2. **Who is the user and what do they need?**
   - [ ] User workflow understood
   - [ ] Success outcome defined (what does "done" look like?)
   - [ ] Not "what would be cool" but "what helps accomplish goal"

3. **What does success look like?**
   - [ ] Measurable outcomes listed
   - [ ] Clear acceptance criteria
   - [ ] Know how to verify it works

4. **What can go wrong?**
   - [ ] Error cases identified
   - [ ] Edge cases considered
   - [ ] Failure modes documented
   - [ ] Graceful degradation strategy

5. **How will this evolve?**
   - [ ] Maintenance plan exists
   - [ ] Extension strategy clear
   - [ ] Debugging approach defined

## Engineering vs Decoration Check

**Is it engineering?** Must answer YES to ALL:

- [ ] Runs when I'm not using it (or has persistent state)?
- [ ] Solves real problem (not cosmetic)?
- [ ] Can describe without mentioning appearance?
- [ ] Has error handling planned?
- [ ] Will improve/learn over time?

**If ANY are NO → It's decoration. Rethink the approach.**

## Architecture-First Requirements

Before writing code:

- [ ] **Data model designed** (entities, relationships, types defined)
- [ ] **System diagram drawn** (components, interactions, data flow)
- [ ] **Component responsibilities clear** (each has ONE job)
- [ ] **Dependencies mapped** (what needs what, critical path identified)
- [ ] **Error handling planned** (for EVERY component: what fails, how detect, how recover)
- [ ] **Tech stack justified** (not "popular" but "right for problem")

## Agent Orchestration Plan

If using sub-agents:

- [ ] **Orchestration strategy chosen:**
  - [ ] Parallel (independent tasks, no file overlap)?
  - [ ] Sequential (dependencies, shared state)?
  - [ ] Background (non-blocking)?
  - [ ] Hybrid?

- [ ] **Context plan:**
  - [ ] Complete context defined for each sub-agent
  - [ ] Not making sub-agents guess

- [ ] **Error recovery:**
  - [ ] Timeout handling
  - [ ] Retry logic
  - [ ] Fallback models/strategies

## Validation Plan

- [ ] **Testing strategy:**
  - [ ] Unit tests (what to test?)
  - [ ] Integration tests (what workflows?)
  - [ ] Manual validation (how to verify?)

- [ ] **Monitoring:**
  - [ ] Logging points identified
  - [ ] Metrics to track
  - [ ] Health checks defined

## Red Flags (Stop If You See These)

🚩 Starting with "Make it look like..."  
🚩 Talking about colors/gradients before data model  
🚩 No clear problem statement  
🚩 "Just add feature X" without understanding why  
🚩 No idea how to verify it works  
🚩 No error handling plan  
🚩 Can't explain the data model  

## The Go/No-Go Decision

**GO if:**
✅ All 5 questions answered  
✅ Engineering check passes  
✅ Architecture planned  
✅ Clear success criteria  

**NO-GO if:**
❌ Problem unclear  
❌ Just decoration  
❌ No architecture plan  
❌ Can't explain data model  

## Next Step After Checklist

If GO:
1. Create GitHub repo (if needed)
2. Switch to Opus for coding (`/model opus`)
3. Start with data model implementation
4. Build incrementally
5. Test before commit

**Remember: Architecture before code. Engineering before decoration.**
