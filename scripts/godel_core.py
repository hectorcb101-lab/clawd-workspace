#!/usr/bin/env python3
"""
Gödel Agent Core for Atlas
Self-referential recursive self-improvement

Based on:
- Gödel Agent paper (arxiv.org/abs/2410.04444)
- AgentK pattern (github.com/mikekelly/agentk)
- CASCADE skill acquisition
"""

import sqlite3
import json
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import glob

CLAWD_DIR = Path(__file__).parent.parent
DB_PATH = CLAWD_DIR / "atlas-memory" / "atlas_memory.db"
ROLLBACK_DIR = CLAWD_DIR / ".rollback"

# Confidence thresholds
THRESHOLD_LOG_ONLY = 0.5
THRESHOLD_REVIEW = 0.7
THRESHOLD_AUTO_APPLY = 0.9

class GodelAgent:
    """
    The Gödel Agent - a self-referential system that can:
    1. Inspect its own code and state (self-awareness)
    2. Modify its own behavior (self-modification)
    3. Improve the improvement process (meta-improvement)
    """
    
    def __init__(self, workspace_path: Path = CLAWD_DIR):
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / "atlas-memory" / "atlas_memory.db"
        self.rollback_dir = self.workspace / ".rollback"
        self.rollback_dir.mkdir(exist_ok=True)
        
        # Files we're allowed to modify
        self.modifiable_patterns = [
            "AGENTS.md",
            "TOOLS.md", 
            "MEMORY.md",
            "HEARTBEAT.md",
            "scripts/*.py",
            "skills/*/SKILL.md",
            "skills/*/*.py",
            ".learnings/*.md"
        ]
        
        # Files requiring human review before modification
        self.review_required = [
            "SOUL.md",
            "scripts/godel_core.py",  # Self-modification of self-modification code
            "atlas-memory/*.py"
        ]
        
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Self-improvements tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS self_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                category TEXT NOT NULL,
                trigger TEXT NOT NULL,
                target_file TEXT,
                before_state TEXT,
                after_state TEXT,
                confidence REAL,
                verified INTEGER DEFAULT 0,
                rollback_path TEXT,
                reason TEXT
            )
        """)
        
        # Capability gaps
        cur.execute("""
            CREATE TABLE IF NOT EXISTS capability_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detected_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                description TEXT NOT NULL,
                failed_action TEXT,
                error_message TEXT,
                attempted_solutions TEXT,
                resolved INTEGER DEFAULT 0,
                resolution TEXT
            )
        """)
        
        # Memory links (A-Mem pattern)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_fact_id INTEGER NOT NULL,
                target_fact_id INTEGER NOT NULL,
                link_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY (source_fact_id) REFERENCES facts(id),
                FOREIGN KEY (target_fact_id) REFERENCES facts(id),
                UNIQUE(source_fact_id, target_fact_id, link_type)
            )
        """)
        
        # Meta-improvement tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meta_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                metric TEXT NOT NULL,
                old_value REAL,
                new_value REAL,
                reason TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== SELF-AWARENESS ====================
    
    def self_inspect(self) -> Dict[str, Any]:
        """
        Read own code and configuration.
        The first step in the Gödel loop.
        """
        state = {
            'timestamp': datetime.utcnow().isoformat(),
            'workspace': str(self.workspace),
            'files': {},
            'stats': {}
        }
        
        # Read core config files
        for filename in ['AGENTS.md', 'TOOLS.md', 'SOUL.md', 'MEMORY.md']:
            filepath = self.workspace / filename
            if filepath.exists():
                state['files'][filename] = {
                    'content': filepath.read_text()[:10000],  # First 10k chars
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                }
        
        # List scripts
        state['files']['scripts'] = [
            f.name for f in (self.workspace / 'scripts').glob('*.py')
        ]
        
        # List skills
        skills_dir = self.workspace / 'skills'
        if skills_dir.exists():
            state['files']['skills'] = [
                d.name for d in skills_dir.iterdir() if d.is_dir()
            ]
        
        # Get improvement stats
        state['stats'] = self._get_improvement_stats()
        
        return state
    
    def _get_improvement_stats(self) -> Dict[str, Any]:
        """Get statistics on self-improvements."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        stats = {}
        
        try:
            cur.execute("SELECT COUNT(*) FROM self_improvements")
            stats['total_improvements'] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM self_improvements WHERE verified = 1")
            stats['verified_improvements'] = cur.fetchone()[0]
            
            cur.execute("""
                SELECT category, COUNT(*) 
                FROM self_improvements 
                GROUP BY category
            """)
            stats['by_category'] = dict(cur.fetchall())
            
            cur.execute("SELECT COUNT(*) FROM capability_gaps WHERE resolved = 0")
            stats['open_gaps'] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM memory_links")
            stats['memory_links'] = cur.fetchone()[0]
            
        except sqlite3.OperationalError:
            pass
        
        conn.close()
        return stats
    
    # ==================== SELF-MODIFICATION ====================
    
    def _is_modifiable(self, filepath: str) -> bool:
        """Check if a file is in the modifiable list."""
        rel_path = str(Path(filepath).relative_to(self.workspace))
        
        for pattern in self.modifiable_patterns:
            if glob.fnmatch.fnmatch(rel_path, pattern):
                return True
        return False
    
    def _requires_review(self, filepath: str) -> bool:
        """Check if file modification requires human review."""
        rel_path = str(Path(filepath).relative_to(self.workspace))
        
        for pattern in self.review_required:
            if glob.fnmatch.fnmatch(rel_path, pattern):
                return True
        return False
    
    def _create_backup(self, filepath: Path) -> str:
        """Create a timestamped backup for rollback."""
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        safe_name = str(filepath.relative_to(self.workspace)).replace('/', '_')
        backup_name = f"{timestamp}_{safe_name}"
        backup_path = self.rollback_dir / backup_name
        
        if filepath.exists():
            shutil.copy2(filepath, backup_path)
        else:
            # Mark as "new file" backup
            backup_path.write_text("__NEW_FILE__")
        
        return str(backup_path)
    
    def _rollback(self, filepath: Path, backup_path: str):
        """Restore file from backup."""
        backup = Path(backup_path)
        if backup.read_text() == "__NEW_FILE__":
            # File was new, delete it
            filepath.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, filepath)
    
    def self_modify(
        self,
        target: str,
        new_content: str,
        reason: str,
        confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Modify a file with rollback capability.
        The core self-modification operation.
        """
        result = {
            'success': False,
            'target': target,
            'reason': reason,
            'confidence': confidence,
            'action': None,
            'message': None
        }
        
        filepath = self.workspace / target
        
        # Check if modifiable
        if not self._is_modifiable(target):
            result['message'] = f"File not in modifiable list: {target}"
            return result
        
        # Check confidence thresholds
        if confidence < THRESHOLD_LOG_ONLY:
            result['action'] = 'logged_only'
            result['message'] = f"Confidence too low ({confidence}), logged for review"
            self._log_for_review(target, new_content, reason, confidence)
            return result
        
        if self._requires_review(target) or confidence < THRESHOLD_REVIEW:
            result['action'] = 'pending_review'
            result['message'] = f"Logged for human review (confidence: {confidence})"
            self._log_for_review(target, new_content, reason, confidence)
            return result
        
        # Create backup
        backup_path = self._create_backup(filepath)
        old_content = filepath.read_text() if filepath.exists() else ""
        
        try:
            # Apply modification
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(new_content)
            
            # Verify (basic check - file exists and is readable)
            if not filepath.exists() or not filepath.read_text():
                raise ValueError("Verification failed: file empty or missing")
            
            # Log the improvement
            self._log_improvement(
                category='self_modification',
                trigger=reason,
                target_file=target,
                before_state=old_content[:5000],
                after_state=new_content[:5000],
                confidence=confidence,
                rollback_path=backup_path
            )
            
            result['success'] = True
            result['action'] = 'applied'
            result['message'] = f"Successfully modified {target}"
            result['rollback_path'] = backup_path
            
        except Exception as e:
            # Rollback on error
            self._rollback(filepath, backup_path)
            result['message'] = f"Error during modification, rolled back: {str(e)}"
            result['action'] = 'rolled_back'
        
        return result
    
    def _log_improvement(self, **kwargs):
        """Log an improvement to the database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO self_improvements 
            (category, trigger, target_file, before_state, after_state, 
             confidence, rollback_path, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            kwargs.get('category'),
            kwargs.get('trigger'),
            kwargs.get('target_file'),
            kwargs.get('before_state'),
            kwargs.get('after_state'),
            kwargs.get('confidence'),
            kwargs.get('rollback_path'),
            kwargs.get('trigger')
        ))
        
        conn.commit()
        conn.close()
    
    def _log_for_review(self, target: str, content: str, reason: str, confidence: float):
        """Log a proposed change for human review."""
        review_file = self.workspace / ".learnings" / "PENDING_IMPROVEMENTS.md"
        review_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        entry = f"""
## {timestamp} - Proposed: {target}

**Reason:** {reason}
**Confidence:** {confidence}
**Status:** Pending Review

<details>
<summary>Proposed Content</summary>

```
{content[:2000]}
```

</details>

---
"""
        
        if review_file.exists():
            current = review_file.read_text()
        else:
            current = "# Pending Improvements\n\nChanges requiring human review.\n"
        
        review_file.write_text(current + entry)
    
    # ==================== POST-TASK REFLECTION ====================
    
    def reflect_on_task(
        self,
        task_description: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze task execution and extract learnings.
        Called after every significant task.
        """
        reflection = {
            'timestamp': datetime.utcnow().isoformat(),
            'task': task_description,
            'success': result.get('success', False),
            'learnings': [],
            'proposed_improvements': []
        }
        
        # Extract success patterns
        if result.get('success'):
            learning = {
                'type': 'success_pattern',
                'content': f"Task '{task_description}' succeeded",
                'details': result.get('summary', ''),
                'confidence': 0.8
            }
            reflection['learnings'].append(learning)
            
            # If there was a notable approach, log it
            if result.get('approach'):
                reflection['proposed_improvements'].append({
                    'target': 'AGENTS.md',
                    'improvement': f"Add tip: For tasks like '{task_description}', use approach: {result['approach']}",
                    'confidence': 0.6
                })
        
        # Extract failure patterns
        if result.get('errors'):
            for error in result['errors']:
                learning = {
                    'type': 'failure_pattern',
                    'content': f"Error in '{task_description}': {error}",
                    'suggested_fix': self._suggest_fix(error),
                    'confidence': 0.7
                }
                reflection['learnings'].append(learning)
                
                # If we can suggest a fix, propose it
                fix = learning['suggested_fix']
                if fix:
                    reflection['proposed_improvements'].append({
                        'target': '.learnings/ERRORS.md',
                        'improvement': f"## Error Pattern\n\n**Error:** {error}\n**Fix:** {fix}",
                        'confidence': 0.7
                    })
        
        # Check for correction patterns
        if result.get('was_corrected'):
            learning = {
                'type': 'correction',
                'content': result.get('correction_message', ''),
                'confidence': 0.9
            }
            reflection['learnings'].append(learning)
            reflection['proposed_improvements'].append({
                'target': 'AGENTS.md',
                'improvement': f"Learned from correction: {result['correction_message']}",
                'confidence': 0.85
            })
        
        # Log the reflection
        self._save_reflection(reflection)
        
        return reflection
    
    def _suggest_fix(self, error: str) -> Optional[str]:
        """Suggest a fix based on common error patterns."""
        error_lower = error.lower()
        
        patterns = {
            'permission denied': 'Check file permissions or use sudo',
            'not found': 'Verify path exists before accessing',
            'connection refused': 'Check if service is running',
            'timeout': 'Increase timeout or add retry logic',
            'out of memory': 'Process in smaller chunks',
            'rate limit': 'Add exponential backoff',
        }
        
        for pattern, fix in patterns.items():
            if pattern in error_lower:
                return fix
        
        return None
    
    def _save_reflection(self, reflection: Dict):
        """Save reflection to daily log."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.workspace / "memory" / f"{today}.md"
        log_file.parent.mkdir(exist_ok=True)
        
        entry = f"""
### Task Reflection: {reflection['task'][:50]}...
- **Success:** {reflection['success']}
- **Learnings:** {len(reflection['learnings'])}
- **Proposed Improvements:** {len(reflection['proposed_improvements'])}
"""
        
        if log_file.exists():
            content = log_file.read_text()
        else:
            content = f"# Daily Log - {today}\n"
        
        log_file.write_text(content + entry)
    
    # ==================== META-IMPROVEMENT ====================
    
    def meta_improve(self) -> Dict[str, Any]:
        """
        Improve the improvement process itself.
        The recursive heart of the Gödel pattern.
        """
        result = {
            'adjustments': [],
            'metrics': {}
        }
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Analyze recent improvements
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified
            FROM self_improvements
            WHERE timestamp > datetime('now', '-7 days')
        """)
        row = cur.fetchone()
        total, verified = row[0] or 0, row[1] or 0
        
        result['metrics']['recent_total'] = total
        result['metrics']['recent_verified'] = verified
        
        if total > 0:
            success_rate = verified / total
            result['metrics']['success_rate'] = success_rate
            
            # Adjust confidence threshold based on success rate
            if success_rate < 0.5 and total > 5:
                # Too many failures - be more conservative
                self._adjust_threshold('THRESHOLD_AUTO_APPLY', 0.95, 'Low success rate')
                result['adjustments'].append({
                    'metric': 'auto_apply_threshold',
                    'action': 'increased to 0.95',
                    'reason': f'Success rate only {success_rate:.1%}'
                })
            elif success_rate > 0.9 and total > 10:
                # Very successful - can be less conservative
                self._adjust_threshold('THRESHOLD_AUTO_APPLY', 0.85, 'High success rate')
                result['adjustments'].append({
                    'metric': 'auto_apply_threshold',
                    'action': 'decreased to 0.85',
                    'reason': f'Excellent success rate {success_rate:.1%}'
                })
        
        conn.close()
        return result
    
    def _adjust_threshold(self, metric: str, new_value: float, reason: str):
        """Log a meta-improvement adjustment."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO meta_improvements (metric, old_value, new_value, reason)
            VALUES (?, ?, ?, ?)
        """, (metric, None, new_value, reason))
        
        conn.commit()
        conn.close()
    
    # ==================== APPLY IMPROVEMENT ====================
    
    def apply_improvement(self, improvement: Dict) -> bool:
        """
        Apply a proposed improvement.
        Returns True if applied, False if logged for review.
        """
        target = improvement.get('target')
        content = improvement.get('content') or improvement.get('improvement')
        confidence = improvement.get('confidence', 0.5)
        reason = improvement.get('reason', 'Post-task learning')
        
        if not target or not content:
            return False
        
        # For append-style improvements (like adding to AGENTS.md)
        filepath = self.workspace / target
        if filepath.exists() and improvement.get('append', True):
            existing = filepath.read_text()
            new_content = existing + "\n" + content
        else:
            new_content = content
        
        result = self.self_modify(target, new_content, reason, confidence)
        return result.get('success', False)


# ==================== CLI INTERFACE ====================

def main():
    import sys
    
    agent = GodelAgent()
    
    if len(sys.argv) < 2:
        print("Usage: godel_core.py <command> [args]")
        print("Commands:")
        print("  inspect          - Show current state")
        print("  stats            - Show improvement statistics")
        print("  reflect <task> <result_json> - Reflect on task")
        print("  meta             - Run meta-improvement")
        print("  modify <file> <content> <reason> [confidence]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'inspect':
        state = agent.self_inspect()
        print(json.dumps(state, indent=2))
    
    elif cmd == 'stats':
        stats = agent._get_improvement_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == 'reflect' and len(sys.argv) >= 4:
        task = sys.argv[2]
        result = json.loads(sys.argv[3])
        reflection = agent.reflect_on_task(task, result)
        print(json.dumps(reflection, indent=2))
    
    elif cmd == 'meta':
        result = agent.meta_improve()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'modify' and len(sys.argv) >= 5:
        target = sys.argv[2]
        content = sys.argv[3]
        reason = sys.argv[4]
        confidence = float(sys.argv[5]) if len(sys.argv) > 5 else 0.7
        result = agent.self_modify(target, content, reason, confidence)
        print(json.dumps(result, indent=2))
    
    else:
        print("Invalid command or arguments")


if __name__ == "__main__":
    main()
