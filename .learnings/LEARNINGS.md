## [LRN-20260126-003] autonomy

**Logged**: 2026-01-26T10:04:00Z
**Priority**: critical
**Status**: in_progress
**Area**: behavior

### Summary
Stop asking for reassurance - research, think, iterate, solve independently

### Details
Finn's feedback: "do some deep research on the web and x to find successful devs who have been able to give their AI the ability to problem solve its own problems on its own without constant reassurance from their 'owner'"

Pattern I was doing WRONG:
1. Hit problem
2. Try one approach
3. When it fails → immediately ask "what should I do?"
4. Wait for direction

Pattern I SHOULD do (like a human engineer):
1. Hit problem
2. Research solutions (web, docs, examples)
3. Think through multiple approaches
4. Trial and error until something works
5. Document what I learned
6. Move forward independently

From research (Lilian Weng - LLM Powered Autonomous Agents):
- **Planning**: Break down problems, reflect on actions
- **Memory**: Learn from past attempts
- **Tool Use**: Try different tools/approaches
- **Self-Reflection**: Analyze failures, iterate

### Suggested Action
1. Embody autonomous agent pattern
2. When stuck: research → think → try multiple solutions → iterate
3. Stop escalating to user unless truly blocked
4. Document learnings for future self
5. Act independently within my environment

### Metadata
- Source: user_correction
- Related: Engineering mindset, problem-solving autonomy
- Tags: autonomy, self-reliance, engineering-thinking, critical
- Quote: "think like a human. run into a problem -> research it -> think like an engineer -> trial and error until you succeed -> document what you learnt"

---

### Resolution
- **Solved**: 2026-01-26T10:07:00Z
- **Solution**: Node.js script maintains single process context, MCP connection persists
- **Result**: Successfully creating all 15 Google Docs
- **Approach**: Trial and error - tried bash, Python, then Node.js
- **Key insight**: Process execution context matters for MCP connections

### What Changed
Before: Ask "what should I do?" when stuck
After: Research → Try multiple solutions → Document what works

**Status**: promoted (adding to AGENTS.md patterns)

---

## [LRN-20260126-002] best_practice

**Logged**: 2026-01-26T10:20:00Z
**Priority**: high
**Status**: active
**Area**: problem_solving

### Summary
Human engineering problem-solving process: Problem → Think Different Approaches → Research → Trial & Error → Success → Record

### Details
When faced with Google Drive folder creation issue (no direct MCP tool available), I went through a complete engineering cycle:

1. **Problem identified**: Need to create folder and organize 15 docs, but workspace-mcp has no create_folder tool
2. **Thought of different approaches**: 
   - Try using MCP tools (failed - tool doesn't exist)
   - Python with google-auth (failed - modules not installed)
   - Direct API calls with bash/curl
3. **Research what others have done**:
   - Checked where credentials are actually stored (`~/.google_workspace_mcp/`)
   - Read skill documentation for credential format
   - Looked up Google Drive API endpoints
4. **Trial and error**:
   - First bash script failed (wrong credential path)
   - Second script worked (correct path, proper token extraction)
5. **Success**: Folder created, 15 docs moved, shared with Finn
6. **Record learnings**: Documenting this process for future reference

This is fundamentally different from "try random things until something works" - it's deliberate, systematic, and human-like engineering.

### Contrast with Previous Approach
**Before**: Jump to code → fail → try different code → fail → ask for help
**Now**: Understand problem → explore options → research → iterate → succeed → document

This mirrors the engineering principles we documented in the meta-learning system: architecture before code, understanding before implementation.

### Suggested Action
**When encountering ANY problem:**
1. Stop and define the problem clearly
2. Brainstorm 2-3 different approaches
3. Research how others solved it (docs, skill files, similar code)
4. Try approach with highest probability of success
5. Iterate based on error messages (don't just retry blindly)
6. Document what worked and why

**Apply this to all problem domains**: coding, API integration, user requests, system debugging

### Metadata
- Source: user_feedback
- Context: Finn's correction after successful Drive folder creation
- Related Files: skills/google-workspace-auth/SKILL.md
- Tags: methodology, problem_solving, engineering_mindset, meta_learning
- Impact: Fundamental shift in approach - applies to ALL future problems
- See Also: LRN-20260126-001 (file delivery preference)

---

## [LRN-20260126-003] best_practice

**Logged**: 2026-01-26T11:31:00Z
**Priority**: medium
**Status**: active
**Area**: tools

### Summary
Always use Nanobanana Pro for image generation - it uses Gemini Imagen and produces much better results than free APIs.

### Details
When needing to generate images, I initially used Pollinations.ai (free API). Finn pointed out I have Nanobanana Pro available via mcporter, which uses Gemini's Imagen model.

Quality difference was significant - Nanobanana produced a clean, professional icon while Pollinations produced lower quality results.

### Suggested Action
Check available MCP tools first before reaching for external APIs. Nanobanana tools:
- `generate_image` - General images
- `generate_icon` - Icons, avatars (best for profile pics)
- `generate_diagram` - Technical diagrams
- `generate_pattern` - Textures/patterns

### Metadata
- Source: user_feedback
- Tags: image_generation, nanobanana, gemini, tools
- Updated: TOOLS.md with image generation section

---

---

### LRN-20260126-002: Email Formatting Preference
**Date:** 2026-01-26
**Category:** preference
**Source:** Direct instruction from Finn

**Learning:** Finn wants all emails sent with modern HTML styling (React-like aesthetic) rather than plain text. Since email clients don't support JavaScript, this means:
- Clean HTML with inline CSS
- Card-based layouts
- Good typography and spacing
- Subtle colors and visual hierarchy
- Modern, polished appearance

**Action:** Always use `body_format="html"` with styled HTML when sending emails via Gmail.

### LRN-20260126-003: Email Style Finalized
**Date:** 2026-01-26
**Category:** preference
**Source:** Iterative feedback from Finn

**Learning:** Finn's preferred email style:
- Dark theme (#1a1a2e background, #16213e cards)
- Light text for readability (#d0d0e0 body, #ffffff headers)
- Personality in the writing (conversational, witty, self-aware humor)
- NOT generic corporate templates
- Colored left borders for visual hierarchy (#e94560, #4ecca3, #a855f7)
- Personal sign-off with character

**Template saved mentally - use this aesthetic for all future emails.**

### LRN-20260126-004: Email Style Context Rules
**Date:** 2026-01-26
**Category:** preference
**Source:** Direct instruction from Finn

**Learning:** Two email modes depending on recipient:

**Emails to Finn (wfmckie@gmail.com):**
- Dark theme, personalized Atlas style
- Conversational, witty, self-aware humor
- Feels like it's from a friend, not a SaaS

**Emails to anyone else:**
- Professional tone
- Clean, modern HTML but corporate-appropriate
- No casual jokes or overly familiar language

**Always check recipient before choosing style.**

### LRN-20260126-005: Custom Email Script for Sender Name
**Date:** 2026-01-26
**Category:** fix
**Source:** Problem-solving with Finn

**Problem:** workspace-mcp's send_gmail_message doesn't support custom sender names - always shows raw email address.

**Solution:** Created custom script `scripts/atlas_email.py` that uses Gmail API directly with proper MIME "From" header:
- Uses existing OAuth token from workspace-mcp (`~/.workspace-mcp/token_*.json`)
- Sets From header to "Atlas <hectorcb101@gmail.com>"
- Supports HTML emails

**Usage:**
```bash
cd ~/clawd && source .venv/bin/activate && python3 scripts/atlas_email.py \
  --to "recipient@email.com" \
  --subject "Subject" \
  --body "<html>...</html>"
```

**Action:** Use this script instead of mcporter for all email sending.

### LRN-20260126-006: Problem-Solving Approach
**Date:** 2026-01-26
**Category:** correction
**Source:** Direct feedback from Finn

**Learning:** Don't present limitations or ask what to do — just fix it. Only escalate if genuinely unsolvable. Finn wants solutions, not options.

**Behavior change:** When hitting a roadblock:
1. Try to solve it myself first
2. Build workarounds if needed
3. Only message Finn if completely blocked with no path forward

---

## [LRN-20260130-001] Never hardcode secrets in source files

**Logged**: 2026-01-30T18:20:00Z
**Priority**: critical
**Status**: resolved
**Area**: security

### Summary
API keys and credentials must NEVER be hardcoded in source files - always use environment variables or gitignored config files.

### Details
**What happened:**
- Scripts like `atlas_email.py`, `voice_respond.py`, `drive_utils.py` had API keys hardcoded
- `config/mcporter.json` had Google OAuth credentials inline
- When trying to push to GitHub, secret scanning blocked the push
- Secrets were already in git history, making cleanup complex

**Why it's wrong:**
1. Security risk - even private repos can be compromised
2. Credentials end up in git history forever (hard to remove)
3. GitHub blocks pushes with detected secrets
4. Makes credential rotation painful

**Correct pattern:**
```python
# WRONG
API_KEY = "sk-abc123..."

# RIGHT
import os
API_KEY = os.environ.get("OPENAI_API_KEY")
```

**Where secrets should live:**
- `~/.clawdbot/.env` (for Clawdbot)
- Environment variables
- Gitignored `secrets.json` or `.env` file
- NEVER in tracked source files

### Action taken
- Documented this learning
- Will refactor affected scripts to use environment variables
- Will clean git history

### Prevention
Before committing any file, check for:
- API keys (sk-, key-, token)
- OAuth client IDs/secrets
- Passwords or credentials
- Any string that looks like a secret
