# Errors Log

Tracks command failures, unexpected errors, and troubleshooting notes.

---

## [ERR-20260125-001] clawdhub_search_timeout

**Logged**: 2026-01-25T14:49:14Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
ClawdHub CLI search command times out when trying to browse available skills

### Error
```
- Searching
✖ Non-error was thrown: "Timeout". You should only throw errors.
Error: Non-error was thrown: "Timeout". You should only throw errors.
```

### Context
- Command attempted: `clawdhub search "agent" --limit 20`
- Missing dependency was installed first: `undici`
- `clawdhub list` works fine (shows installed skills)
- Only `search` operation times out

### Suggested Fix
1. Increase timeout in clawdhub CLI config
2. Use alternative: browse https://clawdhub.com directly in browser
3. Search X/Twitter for skill recommendations instead

### Metadata
- Reproducible: yes
- Related Files: N/A (external CLI tool)
- Workaround: Manual browsing + `clawdhub install <name>` works

---

## [ERR-20260126-002] google_drive_upload_failure

**Logged**: 2026-01-26T09:39:00Z
**Priority**: medium
**Status**: pending
**Area**: integration

### Summary
Google Drive file upload via workspace-mcp failed for tar.gz archive

### Error
Created file on Google Drive but contents showed as "Unknown" - file didn't upload properly. Archive was corrupted or API issue.

### Context
- Attempted to upload meta_learning_complete_package.tar.gz (52 KB)
- Used mcporter google-workspace.create_drive_file with fileUrl parameter
- File was created (ID: 1s79QVNrQTcrR__rpA-5cWqhPMWOk6gPK) but contents broken
- Screenshot showed "1 item" but type "Unknown" with no size/date

### Suggested Fix
Alternative methods:
1. Use SCP for direct server download
2. Send individual files via email
3. Use different file hosting service
4. Investigate workspace-mcp fileUrl handling for binary files

### Metadata
- Reproducible: likely (fileUrl method may not support tar.gz properly)
- Related Files: workspace-mcp integration
- Workaround: Server download or individual file emails

---

## [ERR-20260126-003] mcp_batch_connection_failure

**Logged**: 2026-01-26T09:55:00Z
**Priority**: high
**Status**: pending
**Area**: integration

### Summary
Google Workspace MCP connection fails in batch operations via bash subprocess

### Error
```
[mcporter] Unknown MCP server 'google-workspace'.
Error: Unknown MCP server 'google-workspace'.
```

### Context
- Single mcporter call works: ✅ Created first doc successfully
- Batch calls in bash fail: ❌ Connection drops after first call
- `mcporter list` shows google-workspace is online (32 tools)
- `mcporter call` from bash subprocess gets "Unknown MCP server" error
- Rapid succession calls fail even with sleep delays

### Root Cause
MCP connection is session/context specific and doesn't persist across bash subprocesses when called via exec tool.

### Suggested Fix
1. Create Node.js script that maintains MCP connection
2. Use Clawdbot's native function calling (not bash exec)
3. Add connection pooling/retry logic
4. Rate limit: One call per 5-10 seconds
5. Or: Use Google API directly (not via MCP)

### Workaround
Manual one-at-a-time creation with proper connection handling

### Metadata
- Reproducible: yes (consistently fails in batch)
- Related Files: google-docs-formatter skill
- Impact: Blocks batch document creation
- Workaround exists: Manual/slow creation

---

### Related Learning
See LRN-20260126-002 - This error directly relates to learning about Finn's preference for Google Docs over markdown files.

---

---

## ERR-20260126-003: Morning Briefing Wrong Day of Week

**Date:** 2026-01-26
**Severity:** Low (cosmetic but embarrassing)
**Category:** Date handling

**What happened:**
Morning intelligence briefing sent at 09:00 UTC stated "Sunday" when the actual day was Monday (January 26, 2026).

**Root cause:**
Likely calculated or assumed the day of week incorrectly instead of using proper date functions.

**Fix:**
Always use programmatic date calculation:
```python
from datetime import datetime
day_name = datetime.now().strftime('%A')  # Returns "Monday", "Tuesday", etc.
```

Or in shell:
```bash
date +%A  # Returns day name
```

**Prevention:**
Never hardcode or mentally calculate day of week. Always use `date` command or datetime library.

**Status:** Logged, will fix in future briefings
