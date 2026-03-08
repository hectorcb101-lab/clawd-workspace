---
name: atlas-gate-session
description: "Auto-run atlas-gate session checks on gateway startup"
metadata:
  {
    "openclaw":
      {
        "emoji": "🏛️",
        "events": ["gateway:startup"],
        "requires": { "bins": ["atlas-gate"] },
      },
  }
---

# Atlas Gate Session Hook

Automatically runs `atlas-gate session` when the gateway starts, replacing the manual session checklist.

## What It Does

On `gateway:startup`:
1. Runs `atlas-gate session` (checks daemon health, stale builds, pending mods)
2. Logs the result
3. Pushes a summary message if issues are found

No manual intervention needed. Fires every time OpenClaw restarts.
