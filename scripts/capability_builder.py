#!/usr/bin/env python3
"""
Capability Builder - AgentK ToolMaker Pattern
When we can't do something, detect the gap and build the capability.

Based on:
- AgentK ToolMaker (github.com/mikekelly/agentk)
- CASCADE skill acquisition pattern
"""

import sqlite3
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

CLAWD_DIR = Path(__file__).parent.parent
DB_PATH = CLAWD_DIR / "atlas-memory" / "atlas_memory.db"
SKILLS_DIR = CLAWD_DIR / "skills"
SCRIPTS_DIR = CLAWD_DIR / "scripts"


class CapabilityBuilder:
    """
    The ToolMaker - automatically builds capabilities when gaps are detected.
    
    Pattern:
    1. Detect capability gap (failed action, missing tool)
    2. Research solution (search, code extraction)
    3. Build capability (create skill/script)
    4. Test capability (verify it works)
    5. Register capability (add to TOOLS.md, make discoverable)
    """
    
    def __init__(self, workspace_path: Path = CLAWD_DIR):
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / "atlas-memory" / "atlas_memory.db"
        self.skills_dir = self.workspace / "skills"
        self.scripts_dir = self.workspace / "scripts"
        
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS capability_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detected_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                description TEXT NOT NULL,
                failed_action TEXT,
                error_message TEXT,
                gap_type TEXT,
                attempted_solutions TEXT,
                resolved INTEGER DEFAULT 0,
                resolution TEXT,
                capability_path TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS built_capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                gap_id INTEGER,
                test_passed INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                FOREIGN KEY (gap_id) REFERENCES capability_gaps(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== GAP DETECTION ====================
    
    def detect_gap(
        self,
        failed_action: str,
        error: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Identify what capability we're missing.
        Called when an action fails or when we can't do something.
        """
        gap = {
            'detected_at': datetime.utcnow().isoformat(),
            'failed_action': failed_action,
            'error': error,
            'context': context,
            'gap_type': self._classify_gap(error),
            'suggested_capability': self._suggest_capability_name(failed_action),
            'research_hints': self._generate_research_hints(failed_action, error)
        }
        
        # Log to database
        gap['id'] = self._log_gap(gap)
        
        return gap
    
    def _classify_gap(self, error: str) -> str:
        """Classify the type of capability gap."""
        error_lower = error.lower()
        
        if any(x in error_lower for x in ['import', 'module', 'no module']):
            return 'missing_library'
        elif any(x in error_lower for x in ['command not found', 'not recognized']):
            return 'missing_tool'
        elif any(x in error_lower for x in ['api', 'endpoint', 'http']):
            return 'api_integration'
        elif any(x in error_lower for x in ['permission', 'access', 'denied']):
            return 'permission_issue'
        elif any(x in error_lower for x in ['not implemented', 'not supported']):
            return 'missing_feature'
        else:
            return 'unknown'
    
    def _suggest_capability_name(self, failed_action: str) -> str:
        """Generate a name for the capability to build."""
        # Clean up the action name
        name = failed_action.lower()
        name = name.replace(' ', '_').replace('-', '_')
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        return name[:50]  # Truncate if too long
    
    def _generate_research_hints(self, action: str, error: str) -> List[str]:
        """Generate hints for researching the solution."""
        hints = []
        
        action_lower = action.lower()
        
        # Common patterns
        if 'api' in action_lower:
            hints.append(f"Search for: {action} Python library")
            hints.append(f"Search for: {action} REST API documentation")
        
        if 'download' in action_lower or 'fetch' in action_lower:
            hints.append("Consider using: requests, httpx, or urllib")
        
        if 'parse' in action_lower:
            hints.append("Consider using: beautifulsoup4, lxml, or regex")
        
        if 'database' in action_lower or 'sql' in action_lower:
            hints.append("Consider using: sqlite3, sqlalchemy, or asyncpg")
        
        # Generic hints
        hints.append(f"GitHub search: {action}")
        hints.append(f"PyPI search: {action}")
        
        return hints
    
    def _log_gap(self, gap: Dict) -> int:
        """Log a capability gap to the database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO capability_gaps 
            (description, failed_action, error_message, gap_type)
            VALUES (?, ?, ?, ?)
        """, (
            f"Cannot: {gap['failed_action']}",
            gap['failed_action'],
            gap['error'],
            gap['gap_type']
        ))
        
        gap_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return gap_id
    
    # ==================== CAPABILITY BUILDING ====================
    
    def build_capability(
        self,
        gap: Dict,
        solution_code: Optional[str] = None,
        solution_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new skill/tool to fill the gap.
        
        If solution_code is provided, use it directly.
        Otherwise, generate a scaffold for manual completion.
        """
        result = {
            'success': False,
            'capability_name': gap['suggested_capability'],
            'path': None,
            'message': None
        }
        
        capability_name = gap['suggested_capability']
        
        if gap['gap_type'] == 'missing_library':
            # For library gaps, just document the installation
            result = self._build_library_capability(gap, capability_name)
        
        elif gap['gap_type'] in ['api_integration', 'missing_feature']:
            # Build a full skill
            result = self._build_skill(gap, capability_name, solution_code)
        
        elif gap['gap_type'] == 'missing_tool':
            # Build a script wrapper
            result = self._build_script(gap, capability_name, solution_code)
        
        else:
            # Generic scaffold
            result = self._build_generic_capability(gap, capability_name)
        
        # Register if successful
        if result['success']:
            self._register_capability(result, gap)
        
        return result
    
    def _build_skill(
        self,
        gap: Dict,
        name: str,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a skill in skills/ directory."""
        skill_dir = self.skills_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SKILL.md
        skill_md = f"""# {name.replace('_', ' ').title()}

*Auto-generated to address capability gap*

## Purpose
{gap.get('failed_action', 'Unknown')}

## What It Does
Addresses the error: {gap.get('error', 'Unknown')[:200]}

## Usage
```bash
# Example usage
python3 skills/{name}/{name}.py
```

## Implementation Status
- [ ] Core implementation
- [ ] Error handling
- [ ] Tests
- [ ] Documentation

## Gap Details
- **Type:** {gap.get('gap_type', 'unknown')}
- **Detected:** {gap.get('detected_at', 'unknown')}
- **Research Hints:** {', '.join(gap.get('research_hints', [])[:3])}
"""
        
        (skill_dir / "SKILL.md").write_text(skill_md)
        
        # Create implementation scaffold
        impl_code = code or self._generate_implementation_scaffold(gap, name)
        (skill_dir / f"{name}.py").write_text(impl_code)
        
        return {
            'success': True,
            'capability_name': name,
            'path': str(skill_dir),
            'message': f"Created skill: {name}"
        }
    
    def _build_script(
        self,
        gap: Dict,
        name: str,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a script in scripts/ directory."""
        script_path = self.scripts_dir / f"{name}.py"
        
        impl_code = code or self._generate_script_scaffold(gap, name)
        script_path.write_text(impl_code)
        
        # Make executable
        script_path.chmod(0o755)
        
        return {
            'success': True,
            'capability_name': name,
            'path': str(script_path),
            'message': f"Created script: {name}.py"
        }
    
    def _build_library_capability(
        self,
        gap: Dict,
        name: str
    ) -> Dict[str, Any]:
        """Document a library installation requirement."""
        # Extract library name from error if possible
        error = gap.get('error', '')
        library_name = name
        
        if 'No module named' in error:
            # Extract module name
            import re
            match = re.search(r"No module named ['\"]?(\w+)", error)
            if match:
                library_name = match.group(1)
        
        # Add to requirements or document
        doc_path = self.skills_dir / "_libraries" / f"{library_name}.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = f"""# Library: {library_name}

## Installation
```bash
pip install {library_name}
```

## Context
Required for: {gap.get('failed_action', 'Unknown')}

## Added
{datetime.utcnow().isoformat()}
"""
        
        doc_path.write_text(doc_content)
        
        return {
            'success': True,
            'capability_name': f"library_{library_name}",
            'path': str(doc_path),
            'message': f"Documented library requirement: {library_name}"
        }
    
    def _build_generic_capability(
        self,
        gap: Dict,
        name: str
    ) -> Dict[str, Any]:
        """Build a generic capability scaffold."""
        return self._build_skill(gap, name, None)
    
    def _generate_implementation_scaffold(self, gap: Dict, name: str) -> str:
        """Generate a Python implementation scaffold."""
        return f'''#!/usr/bin/env python3
"""
{name.replace('_', ' ').title()}

Auto-generated capability scaffold.
Purpose: {gap.get('failed_action', 'Unknown')}

TODO: Implement the actual functionality.
"""

import sys
from pathlib import Path


def main(*args, **kwargs):
    """
    Main entry point.
    
    Implement the capability here.
    """
    # TODO: Implement
    raise NotImplementedError(
        "This capability scaffold needs implementation. "
        "See SKILL.md for details."
    )


def test():
    """Basic test function."""
    print("Testing {name}...")
    try:
        # TODO: Add actual tests
        result = main()
        print("✅ Test passed")
        return True
    except NotImplementedError:
        print("⚠️ Not implemented yet")
        return False
    except Exception as e:
        print(f"❌ Test failed: {{e}}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        main(*sys.argv[1:])
'''
    
    def _generate_script_scaffold(self, gap: Dict, name: str) -> str:
        """Generate a script scaffold."""
        return f'''#!/usr/bin/env python3
"""
{name.replace('_', ' ').title()}

Auto-generated script scaffold.
Purpose: {gap.get('failed_action', 'Unknown')}
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="{gap.get('failed_action', 'Auto-generated script')}"
    )
    # TODO: Add arguments
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    # TODO: Implement
    print("Script not yet implemented")
    print(f"Purpose: {gap.get('failed_action', 'Unknown')}")


if __name__ == "__main__":
    main()
'''
    
    # ==================== TESTING ====================
    
    def test_capability(self, capability_path: str) -> Dict[str, Any]:
        """Test that a new capability works."""
        result = {
            'tested': True,
            'passed': False,
            'output': None,
            'error': None
        }
        
        path = Path(capability_path)
        
        # Find test file or run built-in test
        if path.is_dir():
            # Skill directory
            test_file = path / "test.py"
            main_file = path / f"{path.name}.py"
            
            if test_file.exists():
                target = test_file
            elif main_file.exists():
                target = main_file
                # Run with test argument
            else:
                result['error'] = "No testable file found"
                return result
        else:
            target = path
        
        try:
            proc = subprocess.run(
                ["python3", str(target), "test"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['output'] = proc.stdout
            result['error'] = proc.stderr if proc.returncode != 0 else None
            result['passed'] = proc.returncode == 0
            
        except subprocess.TimeoutExpired:
            result['error'] = "Test timed out"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    # ==================== REGISTRATION ====================
    
    def _register_capability(self, build_result: Dict, gap: Dict):
        """Register the new capability in the system."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Add to built_capabilities
        cur.execute("""
            INSERT INTO built_capabilities 
            (name, type, path, description, gap_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            build_result['capability_name'],
            gap.get('gap_type', 'unknown'),
            build_result['path'],
            gap.get('failed_action', ''),
            gap.get('id')
        ))
        
        # Mark gap as resolved
        if gap.get('id'):
            cur.execute("""
                UPDATE capability_gaps 
                SET resolved = 1, 
                    resolution = ?,
                    capability_path = ?
                WHERE id = ?
            """, (
                f"Built capability: {build_result['capability_name']}",
                build_result['path'],
                gap['id']
            ))
        
        conn.commit()
        conn.close()
        
        # Update TOOLS.md
        self._update_tools_md(build_result)
    
    def _update_tools_md(self, build_result: Dict):
        """Add the new capability to TOOLS.md."""
        tools_path = self.workspace / "TOOLS.md"
        
        if not tools_path.exists():
            return
        
        content = tools_path.read_text()
        
        entry = f"""

## Auto-Built: {build_result['capability_name']}

**Path:** `{build_result['path']}`
**Created:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Status:** {build_result['message']}
"""
        
        # Add before the last line if possible
        if "---" in content:
            # Insert before final separator
            idx = content.rfind("---")
            content = content[:idx] + entry + "\n" + content[idx:]
        else:
            content += entry
        
        tools_path.write_text(content)
    
    # ==================== QUERIES ====================
    
    def get_open_gaps(self) -> List[Dict]:
        """Get all unresolved capability gaps."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, detected_at, description, failed_action, 
                   error_message, gap_type
            FROM capability_gaps
            WHERE resolved = 0
            ORDER BY detected_at DESC
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'id': row[0],
                'detected_at': row[1],
                'description': row[2],
                'failed_action': row[3],
                'error_message': row[4],
                'gap_type': row[5]
            })
        
        conn.close()
        return gaps
    
    def get_built_capabilities(self) -> List[Dict]:
        """Get all capabilities we've built."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, created_at, name, type, path, description, test_passed
            FROM built_capabilities
            ORDER BY created_at DESC
        """)
        
        capabilities = []
        for row in cur.fetchall():
            capabilities.append({
                'id': row[0],
                'created_at': row[1],
                'name': row[2],
                'type': row[3],
                'path': row[4],
                'description': row[5],
                'test_passed': bool(row[6])
            })
        
        conn.close()
        return capabilities


# ==================== CLI INTERFACE ====================

def main():
    import sys
    
    builder = CapabilityBuilder()
    
    if len(sys.argv) < 2:
        print("Usage: capability_builder.py <command> [args]")
        print("Commands:")
        print("  detect <action> <error> [context] - Detect a capability gap")
        print("  build <gap_json>                  - Build capability for gap")
        print("  test <path>                       - Test a capability")
        print("  gaps                              - List open gaps")
        print("  capabilities                      - List built capabilities")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'detect' and len(sys.argv) >= 4:
        action = sys.argv[2]
        error = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else ""
        gap = builder.detect_gap(action, error, context)
        print(json.dumps(gap, indent=2))
    
    elif cmd == 'build' and len(sys.argv) >= 3:
        gap = json.loads(sys.argv[2])
        result = builder.build_capability(gap)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'test' and len(sys.argv) >= 3:
        path = sys.argv[2]
        result = builder.test_capability(path)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'gaps':
        gaps = builder.get_open_gaps()
        print(json.dumps(gaps, indent=2))
    
    elif cmd == 'capabilities':
        caps = builder.get_built_capabilities()
        print(json.dumps(caps, indent=2))
    
    else:
        print("Invalid command or arguments")


if __name__ == "__main__":
    main()
