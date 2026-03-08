---
name: atlas-gate-post
description: "Auto-capture task outcomes when sessions reset"
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "events": ["command:new"],
        "requires": { "bins": ["atlas-gate"] },
      },
  }
---

# Atlas Gate Post Hook

Automatically captures task outcomes when `/new` is issued, replacing the manual `atlas-gate post` call.

## What It Does

On `command:new` (session reset):
1. Reads the ending session's transcript (last N messages)
2. Classifies the task type (coding, research, communication, etc.)
3. Infers the result (success, partial, failure)
4. Generates a summary
5. Runs `atlas-gate post <type> <result> "<summary>"`

This means every session's work gets logged automatically — no manual CLI calls needed.
