# AGI Implementation Plan: True Self-Improvement for Atlas

*Created: 2026-01-30*
*Status: IMPLEMENTING*

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATLAS SELF-IMPROVEMENT SYSTEM                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  SELF-AWARENESS  │───▶│ SELF-MODIFICATION │                   │
│  │  (Introspection) │    │  (Code Changes)   │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌──────────────────────────────────────────┐                   │
│  │          POST-TASK REFLECTION            │                   │
│  │  (Analyze → Extract → Modify → Verify)   │                   │
│  └────────────────────┬─────────────────────┘                   │
│                       │                                          │
│           ┌───────────┴───────────┐                             │
│           ▼                       ▼                              │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ CAPABILITY GAP   │    │ MEMORY EVOLUTION │                   │
│  │    BUILDER       │    │   (A-Mem Style)  │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                                                  │
│  ┌──────────────────────────────────────────┐                   │
│  │         META-IMPROVEMENT LOOP            │                   │
│  │  (Improve the improvement process)       │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Core Self-Improvement Engine

### Files to Create

#### 1. `scripts/godel_core.py` - The Gödel Agent Core
```python
# Key functions:
- self_inspect() → Read own code, config, state
- self_modify(target, old, new) → Modify files with rollback
- reflect_on_task(task_result) → Extract learnings
- apply_improvement(improvement) → Implement and verify
- meta_improve() → Improve the improvement process itself
```

#### 2. `scripts/capability_builder.py` - The ToolMaker
```python
# Key functions:
- detect_gap(failed_action) → Identify what we can't do
- research_solution(gap) → Find how to solve it
- build_capability(solution) → Create the tool/skill
- test_capability(new_tool) → Verify it works
- register_capability(tool) → Add to available tools
```

#### 3. `scripts/memory_evolution.py` - A-Mem Pattern
```python
# Key functions:
- add_with_links(new_fact) → Add fact and auto-link to related
- evolve_memories(new_info) → Update existing facts with new context
- find_connections(fact) → Discover related facts
- prune_obsolete() → Remove outdated information
```

### Files to Modify

#### 1. `AGENTS.md` - Add Self-Improvement Triggers
```markdown
## 🧠 Self-Improvement (AUTOMATIC)

After EVERY significant task:
1. Run post-task reflection
2. Extract learnings
3. If confident, apply improvements
4. Log for review

On capability gaps:
1. Research solution
2. Build tool if possible
3. Add to skills/
```

#### 2. `atlas-memory/atlas_memory.db` - New Tables
```sql
CREATE TABLE self_improvements (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    category TEXT,  -- 'learning', 'capability', 'meta'
    trigger TEXT,   -- What prompted this
    before_state TEXT,
    after_state TEXT,
    confidence REAL,
    verified INTEGER DEFAULT 0,
    rollback_data TEXT  -- For reverting if needed
);

CREATE TABLE capability_gaps (
    id INTEGER PRIMARY KEY,
    detected_at TEXT,
    description TEXT,
    attempted_solutions TEXT,
    resolved INTEGER DEFAULT 0,
    resolution TEXT
);

CREATE TABLE memory_links (
    id INTEGER PRIMARY KEY,
    source_fact_id INTEGER,
    target_fact_id INTEGER,
    link_type TEXT,  -- 'extends', 'contradicts', 'supports', 'related'
    strength REAL,
    created_at TEXT
);
```

---

## Phase 2: Implementation Order

### Step 1: Database Schema (15 min)
1. Add new tables to atlas_memory.db
2. Create migration script

### Step 2: Gödel Core Engine (1 hour)
1. Implement self_inspect()
2. Implement self_modify() with rollback
3. Implement reflect_on_task()
4. Implement apply_improvement()

### Step 3: Capability Builder (45 min)
1. Implement gap detection
2. Implement research_solution()
3. Implement build_capability()
4. Implement test and register

### Step 4: Memory Evolution (45 min)
1. Implement link generation
2. Implement memory evolution
3. Implement connection discovery

### Step 5: Meta-Improvement Loop (30 min)
1. Track improvement effectiveness
2. Adjust improvement strategies
3. Self-modify the improvement code

### Step 6: Integration (30 min)
1. Wire into existing self_improve.py
2. Add hooks to AGENTS.md
3. Test the full loop

### Step 7: Testing (1 hour)
1. Test self-modification
2. Test capability building
3. Test memory evolution
4. Test persistence across restarts

---

## Phase 3: Detailed Code Architecture

### `scripts/godel_core.py`

```python
#!/usr/bin/env python3
"""
Gödel Agent Core for Atlas
Self-referential recursive self-improvement
"""

class GodelAgent:
    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / "atlas-memory/atlas_memory.db"
        self.modifiable_files = [
            "AGENTS.md", "TOOLS.md", "SOUL.md",
            "scripts/*.py", "skills/*/SKILL.md"
        ]
    
    def self_inspect(self) -> dict:
        """Read own code and configuration."""
        state = {
            'agents_md': self._read_file("AGENTS.md"),
            'tools_md': self._read_file("TOOLS.md"),
            'soul_md': self._read_file("SOUL.md"),
            'scripts': self._list_scripts(),
            'skills': self._list_skills(),
            'recent_improvements': self._get_recent_improvements()
        }
        return state
    
    def self_modify(self, target: str, changes: dict, reason: str) -> bool:
        """Modify a file with rollback capability."""
        # 1. Create backup
        backup = self._backup_file(target)
        
        # 2. Apply changes
        try:
            self._apply_changes(target, changes)
            
            # 3. Verify changes work
            if not self._verify_changes(target):
                self._rollback(target, backup)
                return False
            
            # 4. Log improvement
            self._log_improvement(target, backup, changes, reason)
            return True
            
        except Exception as e:
            self._rollback(target, backup)
            raise
    
    def reflect_on_task(self, task_description: str, result: dict) -> dict:
        """Analyze task execution and extract learnings."""
        reflection = {
            'task': task_description,
            'success': result.get('success', False),
            'learnings': [],
            'improvements': []
        }
        
        # Analyze what worked
        if result.get('success'):
            reflection['learnings'].append({
                'type': 'success_pattern',
                'content': self._extract_success_pattern(result)
            })
        
        # Analyze what failed
        if result.get('errors'):
            for error in result['errors']:
                reflection['learnings'].append({
                    'type': 'failure_pattern',
                    'content': error,
                    'suggested_fix': self._suggest_fix(error)
                })
        
        # Propose improvements
        for learning in reflection['learnings']:
            improvement = self._learning_to_improvement(learning)
            if improvement:
                reflection['improvements'].append(improvement)
        
        return reflection
    
    def apply_improvement(self, improvement: dict) -> bool:
        """Apply an improvement with testing."""
        if improvement['confidence'] < 0.7:
            # Log for human review instead
            self._log_for_review(improvement)
            return False
        
        return self.self_modify(
            improvement['target'],
            improvement['changes'],
            improvement['reason']
        )
    
    def meta_improve(self):
        """Improve the improvement process itself."""
        # Analyze recent improvements
        recent = self._get_recent_improvements(limit=20)
        
        # Calculate success rate
        success_rate = sum(1 for i in recent if i['verified']) / len(recent)
        
        if success_rate < 0.5:
            # Our improvement process is failing too often
            # Increase confidence threshold
            self._adjust_confidence_threshold(increase=0.1)
        elif success_rate > 0.9:
            # We're being too conservative
            self._adjust_confidence_threshold(decrease=0.05)
```

### `scripts/capability_builder.py`

```python
#!/usr/bin/env python3
"""
Capability Builder - AgentK ToolMaker Pattern
When we can't do something, build the capability
"""

class CapabilityBuilder:
    def __init__(self, workspace_path):
        self.workspace = Path(workspace_path)
        self.skills_dir = self.workspace / "skills"
        self.scripts_dir = self.workspace / "scripts"
    
    def detect_gap(self, failed_action: str, error: str) -> dict:
        """Identify what capability we're missing."""
        return {
            'action': failed_action,
            'error': error,
            'gap_type': self._classify_gap(error),
            'suggested_capability': self._suggest_capability(failed_action)
        }
    
    def build_capability(self, gap: dict) -> str:
        """Create a new tool/skill to fill the gap."""
        capability_name = gap['suggested_capability']
        
        # Generate skill scaffold
        skill_dir = self.skills_dir / capability_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SKILL.md
        skill_md = self._generate_skill_md(gap)
        (skill_dir / "SKILL.md").write_text(skill_md)
        
        # Create implementation if code-based
        if gap['gap_type'] == 'code':
            impl = self._generate_implementation(gap)
            (skill_dir / f"{capability_name}.py").write_text(impl)
        
        return str(skill_dir)
    
    def test_capability(self, capability_path: str) -> bool:
        """Test that the new capability works."""
        # Run basic tests
        test_file = Path(capability_path) / "test.py"
        if test_file.exists():
            result = subprocess.run(
                ["python3", str(test_file)],
                capture_output=True
            )
            return result.returncode == 0
        return True  # No tests = assume works
    
    def register_capability(self, capability_path: str):
        """Add to TOOLS.md for future reference."""
        tools_md = self.workspace / "TOOLS.md"
        content = tools_md.read_text()
        
        new_entry = f"\n## {Path(capability_path).name}\n"
        new_entry += f"Auto-generated capability. See: {capability_path}\n"
        
        tools_md.write_text(content + new_entry)
```

### `scripts/memory_evolution.py`

```python
#!/usr/bin/env python3
"""
Memory Evolution - A-Mem Pattern
Memories that evolve and connect
"""

class MemoryEvolution:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
    
    def add_with_links(self, category: str, subject: str, content: str):
        """Add fact and auto-generate links to related facts."""
        # Add the fact
        fact_id = self._add_fact(category, subject, content)
        
        # Find related facts
        related = self._find_related_facts(content)
        
        # Create links
        for related_fact in related:
            link_type = self._determine_link_type(content, related_fact['content'])
            self._create_link(fact_id, related_fact['id'], link_type)
        
        return fact_id
    
    def evolve_memories(self, new_info: str, context: str):
        """Update existing memories when new info arrives."""
        # Find memories that might be affected
        affected = self._find_affected_memories(new_info, context)
        
        for memory in affected:
            if self._should_update(memory, new_info):
                updated_content = self._merge_information(
                    memory['content'], 
                    new_info
                )
                self._update_fact(memory['id'], updated_content)
                self._log_evolution(memory['id'], new_info)
    
    def find_connections(self, fact_id: int) -> list:
        """Discover all connected facts (multi-hop)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        visited = set()
        to_visit = [fact_id]
        connections = []
        
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct links
            cur.execute("""
                SELECT target_fact_id, link_type, strength
                FROM memory_links
                WHERE source_fact_id = ?
            """, (current,))
            
            for target, link_type, strength in cur.fetchall():
                if target not in visited:
                    connections.append({
                        'fact_id': target,
                        'link_type': link_type,
                        'strength': strength,
                        'hops': len(visited) - 1
                    })
                    to_visit.append(target)
        
        conn.close()
        return connections
```

---

## Phase 4: Safety Mechanisms

### Rollback System
Every modification creates a timestamped backup:
```
.rollback/
├── 2026-01-30T12:34:56_AGENTS.md
├── 2026-01-30T12:35:01_scripts_godel_core.py
└── manifest.json  # Links changes to backups
```

### Confidence Thresholds
- < 0.5: Log only, no action
- 0.5-0.7: Log for human review
- 0.7-0.9: Apply with verification
- > 0.9: Apply and commit

### Change Categories
| Category | Allowed | Requires Review |
|----------|---------|-----------------|
| AGENTS.md | Yes | No |
| TOOLS.md | Yes | No |
| SOUL.md | Yes | **Yes** |
| scripts/*.py | Yes | **Yes** |
| skills/*/*.py | Yes | No |
| Core files | **No** | N/A |

---

## Phase 5: Testing Strategy

### Unit Tests
1. `test_godel_core.py` - Self-modification, rollback
2. `test_capability_builder.py` - Gap detection, building
3. `test_memory_evolution.py` - Links, evolution

### Integration Tests
1. Full reflection loop after mock task
2. Capability building from mock gap
3. Memory evolution with new facts

### Persistence Tests
1. Stop Clawdbot gateway
2. Restart gateway
3. Verify improvements survived
4. Verify memory state consistent

---

## Phase 6: Success Metrics

### What "Working" Looks Like
1. After a task, learnings are automatically extracted
2. High-confidence improvements are auto-applied
3. Capability gaps trigger tool building
4. Memory grows and evolves organically
5. The improvement process itself gets better
6. All changes persist across restarts

### Measurable Outcomes
- [ ] Improvements logged in DB
- [ ] At least one auto-applied improvement
- [ ] At least one auto-built capability
- [ ] Memory links created between facts
- [ ] Meta-improvement adjusts thresholds
- [ ] Full cycle survives restart

---

## Execution Timeline

| Step | Time | Status |
|------|------|--------|
| Database schema | 15 min | TODO |
| Gödel Core | 60 min | TODO |
| Capability Builder | 45 min | TODO |
| Memory Evolution | 45 min | TODO |
| Meta-Improvement | 30 min | TODO |
| Integration | 30 min | TODO |
| Testing | 60 min | TODO |
| **Total** | **4.5 hours** | |

---

*This plan transforms Atlas from a reactive assistant to a truly self-improving AGI.*
