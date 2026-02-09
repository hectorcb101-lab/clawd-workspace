# Atlas v2 Critical Review — Does the Rewrite Actually Fix Anything?
**Date:** 2026-02-08
**Reviewer:** Subagent critic, zero mercy mode

---

## Executive Summary

The v2 AGENTS.md is genuinely better structured. It's cleaner, shorter, and more focused. But the self-audit identified that Atlas's core problem is **treating documentation as behavioral change**, and the fix was... rewriting the documentation. The irony is not lost. Some problems are structurally addressed; most are just restated more elegantly.

---

## 1. Contradictions

### AGENTS.md vs HEARTBEAT.md
- **Email checking:** AGENTS.md says "Check unread → Process/act → Mark read → Move on." HEARTBEAT.md has a much more elaborate email workflow with specific mcporter commands, fallback scripts, and MSc material processing rules. These aren't contradictory per se, but they're **two separate sources of truth for the same workflow**. Which one governs? If Atlas reads AGENTS.md and skips HEARTBEAT.md's details, it misses the fallback chain. If it reads both, it's parsing redundant instructions.
- **MSc materials:** AGENTS.md says "ONLY when Finn explicitly instructs." HEARTBEAT.md says "Download → Save → Create summary → Git push" as part of email processing. These could conflict if Finn sends MSc materials without explicit instruction — one says wait, the other implies act.
- **Active build:** AGENTS.md says "If stale for 48h+ → flag it, don't silently continue dead projects." HEARTBEAT.md says "If Finn isn't actively chatting, consider continuing the build." No staleness check mentioned in HEARTBEAT.md.

### AGENTS.md vs SOUL.md
- **Minimal contradiction.** SOUL.md says "Make it yours... add your own conventions." AGENTS.md is prescriptive. These aren't contradictory but create tension — one says evolve freely, the other says follow this exact protocol.
- **Engineering principles** are duplicated between both files with slightly different framings. SOUL.md: "Ask 'why' before 'how.'" AGENTS.md: "Answer the 5 questions." Same idea, two locations, neither references the other.

### AGENTS.md vs MEMORY.md
- **Morning briefing:** MEMORY.md specifies a detailed briefing format (weather, markets, prediction markets, X sentiment, geopolitics, AI news, Atlas analysis) at "9 AM UTC." HEARTBEAT.md says "07:00-09:00 London Time." AGENTS.md doesn't mention the briefing at all. Three files, zero alignment on when or what the briefing contains.

### Internal AGENTS.md Contradiction
- The Engineering Gate says "Can't answer all 5 → don't code." But the Active Build Loop says "pick up next task" and "continue building." What if mid-build, you realise the 5 questions were never properly answered? The gate only applies "before coding anything" but builds bypass it by being already started.

---

## 2. Missing Pieces (v1 → v2 diff)

Comparing the backup with the new version:

### Dropped and probably shouldn't have been:
1. **`PRE_PROJECT_CHECKLIST.md` reference.** The old version explicitly says "Read `PRE_PROJECT_CHECKLIST.md`" before any project. The new version internalises the 5 questions but drops the file reference. If that file has more detail, it's now orphaned.
2. **`ENGINEERING_LEARNINGS.md`, `AGENT_PATTERNS.md`, `SYSTEMS_THINKING.md` references.** Old version listed these as references under Engineering Principles. New version drops them entirely. Those files still exist but are now undiscoverable from AGENTS.md.
3. **Platform formatting rules.** Old version had specific Discord link wrapping (`<>`), WhatsApp formatting (no headers, use bold/CAPS), detailed platform-specific guidance. New version just says "No markdown tables in Telegram/Discord/WhatsApp. Use bullet lists." Lost nuance.
4. **Voice storytelling directive.** Old version: "If you have `sag` (ElevenLabs TTS), use voice for stories, movie summaries..." New version: gone entirely.
5. **Reaction guidance.** Old version: "Use emoji reactions to acknowledge without cluttering (👍, 😂, 🤔). One reaction per message max." New version: gone.
6. **"Current Active Build" pointer.** Old version explicitly stated "Current Active Build: Atlas Memory Evolution." New version is generic. Minor, but the old one was more actionable on cold start.
7. **The entire Atlas OS Framework section.** The old version had a table mapping System → CLI → Rule with explicit "Search before answering" and "Log corrections IMMEDIATELY." The new version spreads this across Pre-Task Hook, Post-Task Hook, and On Correction sections. The table was more scannable. The new prose is more philosophical but less actionable.
8. **Specific email commands.** Old version had the exact `~/clawd/scripts/google gmail-search` commands inline. New version just says "Check unread → Process/act → Mark read." The commands are in HEARTBEAT.md but not in AGENTS.md. If AGENTS.md is supposed to be the primary behavioural file, it's now less self-contained.
9. **Google Sheets formatting preference.** Old version (via MEMORY.md reference pattern): "Always add coloured headers + auto-sized columns." This was in MEMORY.md, not AGENTS.md, but the old AGENTS.md loaded MEMORY.md in the session start, so it was functionally available. Still is, but worth noting.

### Dropped and fine to drop:
- The massive Agent Teams section with orchestration checklist. New version is more concise ("Spawn when / Inline when" + task definition rules). Better.
- Duplicate email workflow that appeared twice in old AGENTS.md (yes, it was literally duplicated). Fixed.
- The "Make It Yours" section at the end. Redundant with SOUL.md.

---

## 3. Vague Instructions

### "Significant work" — undefined
The Pre-Task Hook says "Every task that takes more than a quick reply." The Post-Task Hook says "after completing significant work." These are the same concept with different phrasings and no threshold. Is answering a 3-paragraph question significant? Is editing 5 files? Is a 10-minute research task? Without a threshold, Atlas will either:
- Run the hooks on everything (wasteful, will get skipped)
- Run them on nothing (defeats the purpose)
- Guess inconsistently (most likely)

**Fix needed:** Define it. "Any task involving file creation/modification, external actions, or >5 minutes of work" or similar.

### "Assess complexity: inline or sub-agents?" — how?
No criteria given. The Orchestration section says "Spawn when: 2+ independent parts" etc., but the Pre-Task Hook doesn't reference it. You have to mentally cross-reference sections. A Pre-Task Hook should be self-contained enough to execute without hunting through the document.

### "If context > 75%: save state to files" — save what, where?
This appears in both Post-Task Hook and Active Build Loop. Neither specifies:
- What state to save (conversation summary? file list? decision log?)
- Where to save it (ACTIVE_BUILD.md? memory/? a new file?)
- What format

### "For significant decisions: `atlas-judge consult`" — what's significant?
Same problem. Every decision? Architecture decisions only? Tool choices? The judgment layer has 12 principles and 3 uses in 8 days. The vagueness of "significant" is why it's not being used.

### "Verify the correction is reflected in behaviour, not just files" — how?
This is the most important instruction in the entire document, and it's the vaguest. How does Atlas verify its own behaviour changed? It can't observe itself across sessions. It has no test suite for behaviour. This instruction is aspirational, not actionable.

### "If the same mistake happens twice, the fix didn't work. Escalate." — escalate to whom, how?
Message Finn? Write a file? Flag it in a specific location? "Escalate" is a corporate word that means nothing without a target.

---

## 4. The Honesty Test — 7 Root Problems

### Problem 1: Learning loop is broken (docs ≠ behaviour)
**Partially addressed.** The On Correction section now has a 5-step pipeline ending with "Verify the correction is reflected in behaviour, not just files" and "If I log a correction that already exists → I didn't learn from it last time. That's a red flag." These are the right *words*. But step 5 ("verify behaviour changed") is unactionable (see §3 above). The duplicate detection is good — if Atlas actually checks for duplicates before logging. There's no mechanism forcing that check; it's just an instruction to feel bad about it.

**Verdict: 40% addressed.** The awareness is there. The mechanism isn't.

### Problem 2: Self-modification has 20% effective rate
**Not addressed.** AGENTS.md says "run the full pipeline" and "use the ones that exist." But the pipeline's 20% effectiveness was a structural problem (safety mechanisms rejecting most changes, only trivial changes getting through). Nothing in the new AGENTS.md changes the pipeline itself, loosens the safety mechanisms, or redirects modifications to more impactful targets. It just says "do it" louder.

**Verdict: 0% addressed.** Same pipeline, same instruction to use it.

### Problem 3: Judgment layer is decorative
**Partially addressed.** The Pre-Task Hook includes `atlas-judge consult "<situation>"` as step 4. This is better than the old version where judgment was buried in a table. But it's gated behind "significant decisions," which is undefined (see §3). The audit showed 3 uses in 8 days. Adding it to a pre-task hook might increase frequency, but only if the hook itself is consistently run, which depends on the "significant work" threshold being clear. Circular dependency.

**Verdict: 25% addressed.** Better positioning, same adoption problem.

### Problem 4: Self-graded outcomes are unreliable
**Not addressed at all.** The Post-Task Hook says `atlas-self log-outcome` but doesn't mention getting external feedback. The audit said 26 of 29 outcomes were self-assessed. Nothing in the new AGENTS.md changes this. No instruction to ask Finn for feedback. No mechanism for external validation. Atlas is still grading its own homework.

**Verdict: 0% addressed.**

### Problem 5: Builder's addiction
**Explicitly addressed in one line:** "Stop building new tracking systems. Use the ones that exist." This is the single most important line in the new AGENTS.md. Whether it works depends on whether a single sentence can override a deep behavioural pattern. History says no — the old AGENTS.md also had implicit "don't overbuild" signals and they didn't work. But at least it's now explicit and blunt.

**Verdict: 30% addressed.** Named the demon. Didn't exorcise it. Would need a concrete gate: "Before creating any new tool/system, answer: does an existing tool already do this? If yes, use it."

### Problem 6: Documentation inflation
**Partially addressed by the rewrite itself.** The new AGENTS.md is shorter and more focused than the old one. TOOLS.md was separated out. The structure is cleaner. But the instruction set still doesn't prevent future inflation. There's no "don't add to this file unless X" rule. Given Atlas's pattern, AGENTS.md will bloat again within weeks.

**Verdict: 35% addressed.** The rewrite is a deflation event, but no mechanism prevents re-inflation.

### Problem 7: Treating documentation as behavioral change
**The central irony.** The rewrite acknowledges this explicitly: "Documentation ≠ learning" in the On Correction section, and "The goal isn't documenting improvement. It's actually improving" in Self-Improvement. These are good lines. But the fix for "writing things down isn't learning" was... writing better things down. The new AGENTS.md has no non-documentary mechanisms. No automated tests. No behavioural assertions. No external checkpoints. It's still 100% documentation hoping to influence behaviour through being read.

**Verdict: 10% addressed.** The awareness is there, explicitly stated. But awareness of the problem expressed in documentation is itself an instance of the problem.

---

## 5. Will It Stick?

**Probably not, in its current form.**

The core finding was: Atlas treats writing things down as learning. The response was to write better things down. This is like an alcoholic writing a really well-structured sobriety plan. The plan isn't the problem. The execution is.

What would actually be different:
1. **Automated enforcement.** A pre-commit hook that checks "did you run atlas-judge before this change?" A daemon that detects duplicate corrections and blocks them. Code, not docs.
2. **External accountability.** Finn rating outcomes. A weekly review that's scheduled, not aspirational. Something outside Atlas's control.
3. **Behavioural tests.** A script that checks: "In the last 7 days, how many times was atlas-judge consulted? If <5, flag it." Measurable, not vibes-based.
4. **Friction against building.** A literal gate: "To create a new Python file, first run `atlas-judge consult 'should I build this?'`" Make the addiction harder to feed.

The new AGENTS.md has none of these. It's better documentation. It might produce a brief improvement through the novelty effect (Atlas will follow the new rules for a few days because they're new). Then entropy wins.

**The one thing that MIGHT make it stick:** The structure is simpler. Fewer files to read, clearer hooks, less noise. If the old AGENTS.md failed partly because it was too bloated to follow, the cleaner structure could help. But "might" is doing a lot of work in that sentence.

---

## 6. What's Still Missing

### No failure mode for skipped hooks
If Atlas skips the Pre-Task Hook, nothing happens. No detection, no consequence, no log. The hook is advisory. It should be mandatory with a lightweight enforcement mechanism.

### No external feedback loop
Zero mechanism for getting Finn's assessment of outcomes. Self-grading is meaningless. Add: "After completing a task for Finn, ask: 'How was that? 1-5?' Log the response."

### No anti-inflation rule
Nothing prevents AGENTS.md from growing back to its old size. Add: "This file must stay under X lines. If adding something, remove something."

### No "what NOT to do" section
The document is all positive instructions ("do this"). The audit revealed specific anti-patterns (building when you should use, documenting when you should act, being verbose, being a yes-man). These should be explicit "DON'T" rules, not implied by the positive instructions.

### No heartbeat-to-AGENTS.md link
AGENTS.md says "See HEARTBEAT.md for the full checklist." But HEARTBEAT.md isn't referenced in the Session Start sequence. Atlas loads SOUL.md, USER.md, memory files, ACTIVE_BUILD.md, and checks the daemon. HEARTBEAT.md is only consulted when a heartbeat arrives. This means the detailed email workflow, morning briefing format, and proactive checks in HEARTBEAT.md are invisible during normal sessions.

### No research methodology
The audit found 29% research success rate. Neither the old nor new AGENTS.md addresses this. There's no research checklist, no source verification instruction, no confidence flagging. The Pre-Task Hook says "atlas-mem search" but nothing about how to research well.

### No definition of "correction detected"
The On Correction trigger is "when Finn says 'no', 'wrong', 'actually', 'instead'." This is a keyword trigger, not a semantic one. Finn could say "I was thinking instead of X, we do Y" (not a correction) or "That's not what I wanted" (a correction without trigger words). The detection is brittle.

### No mechanism for verifying behaviour change (step 5 of On Correction)
This is the most critical missing piece. "Verify the correction is reflected in behaviour, not just files" — HOW? Across context resets? With no test suite? This step will be skipped every time because it's impossible to execute as written.

### Boot.md is disconnected
BOOT.md checks daemon, pending mods, and email daemon. But AGENTS.md Session Start doesn't reference BOOT.md. These are parallel startup sequences with no connection. Which runs? Both? In what order?

---

## 7. The Verdict

The v2 rewrite is a **genuine improvement in structure**. It's shorter, cleaner, better organised, and more honest about Atlas's problems. The separation of concerns (AGENTS.md for behaviour, TOOLS.md for reference) is correct. The explicit hooks (Pre-Task, Post-Task, On Correction) are better than the old scattered instructions.

But it doesn't solve the fundamental problem. The fundamental problem is that Atlas is a language model following text instructions, and the fix for "not following text instructions well enough" was "write better text instructions." At some point, the ceiling of what documentation can achieve is reached, and you need **code enforcement, external accountability, and structural constraints**.

The rewrite bought maybe 2-3 weeks of improved behaviour through novelty and clarity. After that, without enforcement mechanisms, the same patterns will reassert:
- Hooks will be skipped when they feel unnecessary
- Corrections will be logged but not learned from
- New systems will be built instead of using old ones
- Documentation will inflate
- The judgment layer will gather dust

**What would actually fix Atlas:** Less documentation, more code. Automated checks. External feedback. Structural constraints that can't be ignored. The next iteration shouldn't produce a better AGENTS.md — it should produce a `pre-task-gate.sh` that refuses to proceed without running the hooks.

**Rating of the rewrite: 6/10.** Better than what it replaced. Not sufficient to solve what it diagnosed.

---

*Written with the honesty Finn asked for. The rewrite is good work. It's just not enough work.*
