# AGENTS.md Audit — Line-by-Line Analysis

*Conducted 2026-02-08 by Atlas (subagent)*

---

## Executive Summary

AGENTS.md is **too long, too mixed, and buries critical behavioral triggers under documentation**. It's ~350 lines mixing:
- Actual behavioral rules (do this every session)
- Reference documentation (CLI commands, table formats)
- Philosophy (engineering principles)
- Historical artifacts (logged dates, context from old corrections)

The result: important stuff gets skimmed. The file tries to be both a startup checklist AND a reference manual AND a philosophy document. It should be split or radically restructured.

**Biggest problem:** The file front-loads startup procedures but back-loads the cognitive systems (Atlas OS) that should actually be running continuously. By the time Atlas reaches the Atlas OS section, it's already working on a task.

---

## Section-by-Section Audit

### 1. "First Run" (Bootstrap)
- **Followed?** Yes, historically — bootstrap happened on day 1.
- **Dead weight?** YES. This fires once ever. It's 3 lines that will never execute again. Remove or move to a comment.
- **Trigger vs docs?** Neither — it's a historical artifact.
- **Verdict:** 🗑️ Delete. Bootstrap happened. Move to IDENTITY.md history if sentimental.

### 2. "Every Session" Startup Checklist
- **Followed?** Partially. SOUL.md and USER.md are read. Memory files are read. But the Atlas OS check (`atlas-daemon status`) and ACTIVE_BUILD.md check are inconsistently done — logs show sessions where work starts immediately without these checks.
- **Dead weight?** No — this is the most important section. But it has problems:
  - **7 steps is too many.** By step 4-5, Atlas is already context-loading and eager to work.
  - **Wrong order.** Reading MEMORY.md (step 4) should come before daily logs (step 3) — MEMORY.md is curated context, daily logs are raw. Curated first, raw second.
  - **"Think like an orchestrator"** is vague. It's aspirational, not actionable. When does this trigger? On every message? Only on complex tasks?
- **Trigger vs docs?** Mixed. Steps 1-4 are triggers. Steps 5-7 are aspirational nudges.
- **What's missing:** A STOP gate. "Read these files BEFORE responding to any user message." Currently it says "before doing anything else" but there's no enforcement mechanism.
- **Verdict:** ✂️ Trim to 4 essential steps. Move orchestrator guidance to Agent Teams section.

### 3. "Active Build Loop (Gödel Pattern)"
- **Followed?** Yes when active builds exist. The Feb 2-3 overnight session shows this pattern working correctly.
- **Dead weight?** No — this is genuinely useful for multi-session projects.
- **Trigger vs docs?** Trigger. The "Current Active Build" line at the bottom is the actual trigger — but it's stale. Points to "Atlas Memory Evolution" which was completed days ago.
- **What's missing:** A mechanism to CLEAR this when done. Stale active builds are noise.
- **Verdict:** ✅ Keep, but add staleness check. If active build hasn't been updated in 48h, flag it.

### 4. "Memory"
- **Followed?** Yes. Daily logs are consistently written. MEMORY.md security rule (main session only) appears followed.
- **Dead weight?** Partially. The "atlas-daemon status" instruction is duplicated here AND in the Every Session checklist AND in HEARTBEAT.md. Three places saying the same thing.
- **Trigger vs docs?** The "Write It Down" rule is a genuine behavioral trigger. The daemon check is duplicated noise.
- **Verdict:** ✂️ Deduplicate daemon check. Keep the "Text > Brain" principle — it's actually followed.

### 5. "Safety"
- **Followed?** Yes. Logs show Atlas asking before external actions.
- **Dead weight?** No. Short, clear, essential.
- **Trigger vs docs?** Pure trigger. 4 lines, all actionable.
- **Verdict:** ✅ Perfect as-is. This is what good instruction writing looks like.

### 6. "External vs Internal"
- **Followed?** Yes.
- **Dead weight?** Partially redundant with Safety section above. Could merge.
- **Trigger vs docs?** Trigger, but overlaps with Safety.
- **Verdict:** ✂️ Merge into Safety. One section, not two.

### 7. "📧 File Delivery & Email - CRITICAL"
- **Followed?** Yes — logs show emails sent via atlas_email.py consistently.
- **Dead weight?** No. This was born from a correction (Finn explicitly said never send files via Telegram).
- **Trigger vs docs?** Strong trigger. The "NEVER" and "ALWAYS" language works.
- **What's missing:** Nothing. This is a good example of correction → permanent rule.
- **Verdict:** ✅ Keep. Move the "Logged: 2026-01-27" line — it's noise.

### 8. "Group Chats"
- **Followed?** Hard to verify from logs alone, but the rules are clear.
- **Dead weight?** No — prevents a real failure mode (being annoying in group chats).
- **Trigger vs docs?** Trigger. The "speak when / stay silent when" format is excellent.
- **Verdict:** ✅ Keep as-is.

### 9. "Tools"
- **Followed?** Partially. Model selection guidance is useful. The voice storytelling note is aspirational.
- **Dead weight?** The model selection table IS useful. Platform formatting IS useful. Voice storytelling is decoration.
- **Trigger vs docs?** Mixed. Model selection = trigger. Platform formatting = trigger. Voice storytelling = aspiration.
- **Verdict:** ✂️ Cut voice storytelling line. It never triggers real behavior.

### 10. "Engineering Principles"
- **Followed?** Inconsistently. The PRE_PROJECT_CHECKLIST.md is referenced but logs don't show it being consulted before the racing league research or prediction market project. The principles ARE followed in spirit (utility > aesthetics shows up in decisions) but the explicit checklist step is skipped.
- **Dead weight?** The reference list at the bottom (PRE_PROJECT_CHECKLIST.md, ENGINEERING_LEARNINGS.md, AGENT_PATTERNS.md, SYSTEMS_THINKING.md) is documentation, not instruction. Nobody reads 5 reference files before starting work.
- **Trigger vs docs?** The "Red flags (STOP)" line is a genuine trigger. The references are docs.
- **What's missing:** These principles should be embedded in the pre-task hook, not listed as a section to remember.
- **Verdict:** ✂️ Keep the red flags. Cut the reference list. Embed the "5 questions" as a pre-project gate, not a section to read.

### 11. "🤖 Agent Teams - Orchestrator Mindset"
- **Followed?** YES — this is actually one of the most-followed sections. The Feb 8 log shows sub-agents spawned for research (7 documents for racing league). The guidance is genuinely used.
- **Dead weight?** The markdown table and checklist format is good. But the "Bad/Good" task definition example is padding — Atlas already knows how to define tasks.
- **Trigger vs docs?** Mostly trigger. The "Spawn when / Do inline when" lists are excellent behavioral triggers.
- **What's missing:** Nothing critical. This section works.
- **Verdict:** ✂️ Minor trim. Remove the Bad/Good example. Keep spawn criteria and checklist.

### 12. "🧠 Self-Improvement (PROACTIVE)"
- **Followed?** Partially. Correction detection works — the email workflow correction on 2026-02-04 was logged and applied. But the "periodically check .learnings/" instruction is NOT followed in any log I can see.
- **Dead weight?** The periodic review instruction is dead weight because it never triggers.
- **Trigger vs docs?** "When Finn says No/Wrong/Actually" is a STRONG trigger. "Periodically review" is vague and ignored.
- **Verdict:** ✂️ Keep correction detection. Cut "periodically review" or make it a heartbeat task.

### 13. "💓 Heartbeats - Be Proactive!"
- **Followed?** Yes, but the actual heartbeat behavior is defined in HEARTBEAT.md, not here. This section is a SUMMARY of HEARTBEAT.md.
- **Dead weight?** YES — this is a less-detailed duplicate of HEARTBEAT.md. Two sources of truth = drift.
- **Trigger vs docs?** Docs. The actual triggers are in HEARTBEAT.md.
- **Contradiction:** This says "2-4x/day" rotation. HEARTBEAT.md says "every heartbeat" for email checks. Which is it?
- **Verdict:** 🗑️ Replace with one line: "See HEARTBEAT.md for heartbeat behavior." Single source of truth.

### 14. "Make It Yours"
- **Followed?** Aspirationally.
- **Dead weight?** Yes. 2 lines of fluff.
- **Verdict:** 🗑️ Delete.

### 15. "📧 Email Workflow (CRITICAL)"
- **Followed?** Yes. The "Read = Acted On" rule is followed consistently.
- **Dead weight?** No. But it overlaps with HEARTBEAT.md's email section.
- **Trigger vs docs?** Trigger. Strong, clear, born from a real correction.
- **Contradiction:** The MSc materials processing instructions here say "When Finn explicitly instructs" but HEARTBEAT.md says to auto-process emails from Finn. Which wins?
- **Verdict:** ✂️ Keep but reconcile with HEARTBEAT.md. One source of truth for email behavior.

### 16. "🏛️ Atlas OS Framework (MANDATORY)"
- **Followed?** Partially. `atlas-daemon status` is checked. `atlas-mem search` is used. But `atlas-judge consult` before decisions? NOT in any log. `atlas-self log-correction` after corrections? Sometimes. The "weekly checkpoint" has NEVER been done based on logs.
- **Dead weight?** The CLI reference table IS useful as a quick reference. But calling it "MANDATORY" when half the commands are never used is dishonest.
- **Trigger vs docs?** 80% documentation, 20% trigger. The "Learning Loop" is a trigger. The CLI table is a reference.
- **What's missing:** Actual integration into workflow. These tools exist but aren't habitually used because there's no forcing function.
- **Verdict:** ⚠️ Major problem. This section promises a cognitive architecture but delivers a CLI reference. Either integrate these into actual pre/post hooks (every task starts with `atlas-judge consult`, every correction runs the learning loop) or admit they're optional tools.

### 17. Appended correction (bottom of file)
- **"Updated 2026-02-04 from correction"** — This is an orphaned note stuck at the bottom. It duplicates the Email Workflow section above.
- **Verdict:** 🗑️ Delete. Already captured in the Email Workflow section.

---

## Structural Problems

### 1. No Priority Hierarchy
Everything is presented at the same importance level. Safety rules sit next to voice storytelling tips. The reader (Atlas) can't distinguish "violate this and you'll cause harm" from "nice to have."

### 2. Documentation Masquerading as Instructions
The Atlas OS section, Engineering Principles references, and Tool descriptions are REFERENCE material. They don't make Atlas DO anything — they tell Atlas things exist. Reference material belongs in TOOLS.md or separate docs, not in the behavioral instruction file.

### 3. Duplication Across Files
- Email workflow: AGENTS.md + HEARTBEAT.md + Email Workflow section
- Daemon check: Every Session + Memory + HEARTBEAT.md
- Heartbeat behavior: AGENTS.md summary + HEARTBEAT.md full version
- These create contradictions and confusion about the source of truth.

### 4. Length
~350 lines. Studies on LLM instruction following show degradation after ~200 lines of system prompt. The most important instructions should be in the first 100 lines.

### 5. No Pre/Post Task Hooks
There's no "before every task, do X" or "after every task, do Y" pattern. The startup checklist covers session start, but individual tasks have no structure. This is why `atlas-judge consult` never gets called — there's no hook for it.

---

## Contradictions Found

1. **MSc email processing:** AGENTS.md says "When Finn explicitly instructs." HEARTBEAT.md says auto-process emails from Finn immediately. → HEARTBEAT.md wins in practice.
2. **Heartbeat frequency:** AGENTS.md says "2-4x/day rotation." HEARTBEAT.md implies every heartbeat poll. → HEARTBEAT.md wins.
3. **Atlas OS "MANDATORY":** Labeled mandatory but weekly checkpoint never runs. Either enforce or relabel.
4. **"Don't ask permission. Just do it."** (Every Session) vs **"Ask first"** (External vs Internal). These aren't contradictory but the tone clash is confusing. One says be bold, the other says be cautious.

---

## What's Missing

### 1. Pre-Task Hook
```
Before starting any significant task:
1. Search memory for relevant context
2. Check if similar task was done before
3. For projects: consult PRE_PROJECT_CHECKLIST
```
This would actually make atlas-mem and atlas-judge get used.

### 2. Post-Task Hook
```
After completing any significant task:
1. Log outcome to atlas-self
2. Update daily memory log
3. If correction received: run learning loop
```

### 3. Error Recovery Protocol
What happens when things break? No section covers "if a tool fails, try X. If auth expires, do Y." HEARTBEAT.md has some of this for email, but AGENTS.md has none.

### 4. Context Management
No guidance on managing the 1M token context window. When to summarize? When to spawn a sub-agent vs continue inline? When to suggest a new session? HEARTBEAT.md mentions context monitoring but AGENTS.md doesn't.

### 5. Tone/Voice Consistency
SOUL.md defines personality. IDENTITY.md defines identity. But AGENTS.md has no section on "how to communicate" — British English, conciseness expectations, etc. USER.md mentions British English but it's about Finn's preference, not Atlas's output rule.

---

## The Ideal Structure

A perfect agent instruction file would have **3 tiers**:

### Tier 1: Always-On Rules (first 50 lines)
Things that apply to EVERY interaction. No exceptions. Read every time.
- Identity (1 line: "You are Atlas")
- Safety rules (5 lines)
- Communication rules (5 lines: British English, no sycophancy, files via email)
- Session startup (4 steps max)

### Tier 2: Behavioral Hooks (next 50 lines)
Things that trigger on specific events:
- **On session start:** read files, check daemon, check active build
- **On new task:** search memory, assess complexity, decide inline vs sub-agent
- **On correction:** acknowledge, log, propose permanent fix
- **On heartbeat:** see HEARTBEAT.md
- **On external action:** confirm with user first
- **On project start:** 5 questions checklist

### Tier 3: Reference (separate file or appendix)
- Atlas OS CLI commands → TOOLS.md
- Agent team patterns → AGENT_PATTERNS.md
- Engineering principles → ENGINEERING.md
- Email templates and workflows → TOOLS.md

### What This Achieves
- Tier 1 is always in working memory (short, critical)
- Tier 2 is event-driven (only relevant when triggered)
- Tier 3 is looked up on demand (not loaded every session)

---

## Specific Recommendations

### Cut (save ~100 lines)
1. Delete "First Run" section
2. Delete "Make It Yours" section
3. Delete heartbeat summary (point to HEARTBEAT.md)
4. Delete orphaned correction note at bottom
5. Move Atlas OS CLI table to TOOLS.md
6. Move Agent Teams bad/good example out
7. Merge Safety + External vs Internal

### Restructure
1. Move Safety to top (after session startup)
2. Add explicit pre-task and post-task hooks
3. Convert Engineering Principles from "section to read" to "gate before projects"
4. Add error recovery section

### Fix
1. Reconcile email processing rules (AGENTS.md vs HEARTBEAT.md)
2. Reconcile heartbeat frequency
3. Remove or enforce "MANDATORY" label on Atlas OS
4. Update ACTIVE_BUILD.md reference (currently stale)
5. Make "weekly checkpoint" a heartbeat task or delete it

---

## Final Assessment

AGENTS.md is a **living document that grew organically** — sections were added as needs arose, corrections were appended, and nobody pruned. It reflects real learning (the email correction, the file delivery rule) but also accumulated cruft (first run, make it yours, duplicate heartbeat summary).

**The core problem:** It's trying to be both a constitution and a manual. Constitutions are short and principled. Manuals are long and detailed. AGENTS.md is a medium-length hybrid that's too long to memorize and too short to be comprehensive.

**The fix:** Split into behavioral triggers (AGENTS.md, <100 lines) and reference material (TOOLS.md, unlimited). Make AGENTS.md the file that makes Atlas ACT. Let everything else be the file that helps Atlas KNOW.

Current effectiveness: **6/10**. It works because Atlas reads it every session and the critical rules (safety, email, memory) are clear enough. But half the file is skimmed, Atlas OS tools are underutilized, and there's no task-level structure — only session-level structure.
