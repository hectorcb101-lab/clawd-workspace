# Deprecation Plan: Old Memory System → Atlas Memory Evolution

**Date:** 2026-02-01
**Status:** Ready to Execute

---

## Overview

Migrate fully from the old SQLite-based memory system to the new Atlas Memory Evolution system.

### Old System (TO REMOVE)
```
~/clawd/atlas-memory/
├── atlas_memory.db      # 4.5MB SQLite database (492 facts migrated)
├── query.py             # Old query script
├── generate_embeddings.py
├── memory_manager.py
├── integration.py
├── migrate_markdown.py
├── schema.sql
└── venv/                # Old virtual environment
```

### New System (ACTIVE)
```
~/clawd/projects/atlas-memory-evolution/
├── src/
│   ├── atlas_memory.py      # Unified interface
│   ├── memory_daemon.py     # Real-time capture
│   ├── knowledge_graph.py   # Phase 3
│   ├── semantic_search.py   # Phase 4
│   └── ...
├── data/
│   ├── events/              # Event log (615 events)
│   ├── knowledge/           # Extracted facts (585)
│   └── graph/               # Knowledge graph (569 facts)
└── tests/
```

---

## Migration Steps

### Step 1: Update HEARTBEAT.md
Replace old DB health check with new daemon check.

**Remove:**
```bash
python3 -c "import sqlite3; c=sqlite3.connect('/home/ubuntu/clawd/atlas-memory/atlas_memory.db')..."
```

**Replace with:**
```bash
atlas-daemon status
atlas-mem stats
```

### Step 2: Update TOOLS.md
Already partially done. Remove remaining old system references.

### Step 3: Update AGENTS.md
Already done (Phase 5). Verify no old references remain.

### Step 4: Archive Old System
```bash
# Create archive
tar -czvf ~/clawd/archives/atlas-memory-old-$(date +%Y%m%d).tar.gz ~/clawd/atlas-memory/

# Remove old directory
rm -rf ~/clawd/atlas-memory/
```

### Step 5: Update Scripts
- Remove ~/clawd/scripts/atlas (old wrapper)
- Keep ~/clawd/scripts/atlas-mem (new CLI)
- Keep ~/clawd/scripts/atlas-daemon (daemon CLI)

### Step 6: Clean Up References in Other Files
Files to update:
- AGI_IMPLEMENTATION_PLAN.md
- AGI_UPGRADES.md
- Any other files with atlas_memory.db references

---

## Files to Update

| File | Action | Status |
|------|--------|--------|
| HEARTBEAT.md | Replace DB check with daemon check | TODO |
| TOOLS.md | Remove old system section | TODO |
| AGENTS.md | Already updated | ✅ DONE |
| AGI_IMPLEMENTATION_PLAN.md | Update or archive | TODO |
| AGI_UPGRADES.md | Update or archive | TODO |

---

## Verification After Migration

1. `atlas-daemon status` — Daemon running
2. `atlas-mem stats` — Shows 580+ facts
3. `atlas-mem search "test"` — Returns results
4. Old directory removed
5. No broken references in workspace

---

## Rollback Plan

If something goes wrong:
1. Archive is kept at `~/clawd/archives/atlas-memory-old-*.tar.gz`
2. Can restore with: `tar -xzvf ~/clawd/archives/atlas-memory-old-*.tar.gz -C /`
3. Old data was already migrated to new system, so no data loss

---

## Timeline

1. **Now:** Create this plan ✅
2. **Now:** Update HEARTBEAT.md
3. **Now:** Update TOOLS.md (remove old fallback section)
4. **Now:** Archive old system
5. **Now:** Clean up other files
6. **Verify:** Run tests to confirm everything works

---

*Ready for Finn's approval to execute.*
