#!/usr/bin/env python3
"""
Self-Improvement Engine for Atlas
The unified interface for the Gödel Agent pattern.

This integrates:
- Gödel Core (self-awareness, self-modification)
- Capability Builder (gap detection, tool building)
- Memory Evolution (A-Mem pattern, knowledge graph)

Usage:
    python3 self_improve.py reflect <task> <result_json>
    python3 self_improve.py gap <action> <error>
    python3 self_improve.py evolve <new_info>
    python3 self_improve.py meta
    python3 self_improve.py stats
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import the component modules
CLAWD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CLAWD_DIR / "scripts"))

from godel_core import GodelAgent
from capability_builder import CapabilityBuilder
from memory_evolution import MemoryEvolution

DB_PATH = CLAWD_DIR / "atlas-memory" / "atlas_memory.db"


class SelfImprovementEngine:
    """
    The unified self-improvement system.
    
    Combines:
    - GodelAgent: Self-inspection, modification, reflection
    - CapabilityBuilder: Gap detection and tool building
    - MemoryEvolution: Knowledge graph and memory evolution
    """
    
    def __init__(self):
        self.workspace = CLAWD_DIR
        self.godel = GodelAgent(self.workspace)
        self.builder = CapabilityBuilder(self.workspace)
        self.memory = MemoryEvolution(DB_PATH)
    
    # ==================== MAIN WORKFLOWS ====================
    
    def post_task_reflection(
        self,
        task_description: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        The main post-task improvement loop.
        Called after every significant task.
        
        Flow:
        1. Reflect on task (extract learnings)
        2. Propose improvements
        3. Apply high-confidence improvements
        4. Evolve related memories
        5. Detect any capability gaps
        """
        output = {
            'task': task_description,
            'reflection': None,
            'improvements_applied': [],
            'improvements_pending': [],
            'memory_evolutions': [],
            'gaps_detected': []
        }
        
        # 1. Reflect on the task
        reflection = self.godel.reflect_on_task(task_description, result)
        output['reflection'] = reflection
        
        # 2. Apply improvements
        for improvement in reflection.get('proposed_improvements', []):
            if improvement.get('confidence', 0) >= 0.7:
                applied = self.godel.apply_improvement(improvement)
                if applied:
                    output['improvements_applied'].append(improvement)
                else:
                    output['improvements_pending'].append(improvement)
            else:
                output['improvements_pending'].append(improvement)
        
        # 3. Evolve memories with learnings
        for learning in reflection.get('learnings', []):
            content = learning.get('content', '')
            if content:
                evolution = self.memory.evolve_memories(
                    content,
                    context=task_description
                )
                if evolution.get('updated'):
                    output['memory_evolutions'].extend(evolution['updated'])
        
        # 4. Detect capability gaps from errors
        if result.get('errors'):
            for error in result['errors']:
                gap = self.builder.detect_gap(
                    task_description,
                    error,
                    context="Post-task reflection"
                )
                output['gaps_detected'].append(gap)
        
        # 5. Log the reflection cycle
        self._log_reflection_cycle(output)
        
        return output
    
    def handle_capability_gap(
        self,
        failed_action: str,
        error: str,
        auto_build: bool = False
    ) -> Dict[str, Any]:
        """
        Handle a capability gap.
        
        Flow:
        1. Detect and classify the gap
        2. Generate research hints
        3. Optionally auto-build a scaffold
        4. Register for future reference
        """
        output = {
            'gap': None,
            'built': None,
            'test_result': None
        }
        
        # 1. Detect the gap
        gap = self.builder.detect_gap(failed_action, error)
        output['gap'] = gap
        
        # 2. Auto-build if requested
        if auto_build:
            build_result = self.builder.build_capability(gap)
            output['built'] = build_result
            
            # 3. Test the new capability
            if build_result.get('success'):
                test_result = self.builder.test_capability(build_result['path'])
                output['test_result'] = test_result
        
        # 4. Add to memory as a known gap
        self.memory.add_with_links(
            category='capability_gap',
            subject=f"Gap: {failed_action}",
            content=f"Error: {error}\nType: {gap['gap_type']}\nHints: {', '.join(gap['research_hints'][:3])}",
            source='capability_builder'
        )
        
        return output
    
    def evolve_knowledge(
        self,
        new_info: str,
        context: str = "",
        add_as_fact: bool = True
    ) -> Dict[str, Any]:
        """
        Evolve the knowledge base with new information.
        
        Flow:
        1. Optionally add as new fact with auto-linking
        2. Evolve related existing memories
        3. Report on changes
        """
        output = {
            'new_fact': None,
            'evolved_memories': [],
            'new_links': []
        }
        
        # 1. Add as fact if requested
        if add_as_fact:
            result = self.memory.add_with_links(
                category='knowledge',
                subject=new_info[:50] + '...' if len(new_info) > 50 else new_info,
                content=new_info,
                source='self_improvement'
            )
            output['new_fact'] = result.get('fact_id')
            output['new_links'] = result.get('links_created', [])
        
        # 2. Evolve related memories
        evolution = self.memory.evolve_memories(new_info, context)
        output['evolved_memories'] = evolution.get('updated', [])
        
        return output
    
    def run_meta_improvement(self) -> Dict[str, Any]:
        """
        Run the meta-improvement loop.
        Improves the improvement process itself.
        """
        output = {
            'godel_meta': None,
            'graph_stats': None,
            'recommendations': []
        }
        
        # 1. Run Gödel meta-improvement
        output['godel_meta'] = self.godel.meta_improve()
        
        # 2. Get memory graph stats
        output['graph_stats'] = self.memory.get_graph_stats()
        
        # 3. Prune old weak links
        prune_result = self.memory.prune_obsolete(days_old=60)
        output['pruned'] = prune_result
        
        # 4. Generate recommendations
        stats = output['graph_stats']
        
        if stats.get('total_links', 0) < stats.get('total_facts', 1) * 0.5:
            output['recommendations'].append({
                'type': 'low_connectivity',
                'message': 'Knowledge graph has low connectivity. Consider running evolve more often.'
            })
        
        if output['godel_meta'].get('metrics', {}).get('success_rate', 1) < 0.5:
            output['recommendations'].append({
                'type': 'low_success',
                'message': 'Improvement success rate is low. Consider raising confidence threshold.'
            })
        
        return output
    
    def get_full_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats on the self-improvement system."""
        return {
            'godel_stats': self.godel._get_improvement_stats(),
            'graph_stats': self.memory.get_graph_stats(),
            'open_gaps': len(self.builder.get_open_gaps()),
            'built_capabilities': len(self.builder.get_built_capabilities()),
            'workspace': str(self.workspace)
        }
    
    # ==================== HELPERS ====================
    
    def _log_reflection_cycle(self, output: Dict):
        """Log a reflection cycle to daily notes."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.workspace / "memory" / f"{today}.md"
        log_file.parent.mkdir(exist_ok=True)
        
        entry = f"""
## Self-Improvement Cycle - {datetime.utcnow().strftime("%H:%M")}

**Task:** {output['task'][:100]}...
**Learnings:** {len(output['reflection'].get('learnings', []))}
**Improvements Applied:** {len(output['improvements_applied'])}
**Improvements Pending:** {len(output['improvements_pending'])}
**Memories Evolved:** {len(output['memory_evolutions'])}
**Gaps Detected:** {len(output['gaps_detected'])}

"""
        
        if log_file.exists():
            content = log_file.read_text()
        else:
            content = f"# Daily Log - {today}\n"
        
        log_file.write_text(content + entry)


# ==================== BACKWARDS COMPATIBILITY ====================
# Keep old function signatures for existing code

def get_db():
    return sqlite3.connect(DB_PATH)

def log_improvement(category: str, trigger: str, before: str, after: str, confidence: float):
    """Log a self-improvement action to the database."""
    engine = SelfImprovementEngine()
    engine.godel._log_improvement(
        category=category,
        trigger=trigger,
        before_state=before,
        after_state=after,
        confidence=confidence
    )
    print(f"✅ Logged improvement: {category}")

def add_fact(category: str, subject: str, content: str, source: str = "self_improvement"):
    """Add a fact to the memory database."""
    engine = SelfImprovementEngine()
    result = engine.memory.add_with_links(category, subject, content, source)
    print(f"✅ Added fact #{result['fact_id']}: {subject}")
    return result['fact_id']

def detect_correction(user_message: str) -> bool:
    """Detect if a message is a correction."""
    correction_triggers = [
        "no,", "no ", "wrong", "actually", "instead", 
        "that's not", "don't do", "never do", "always do",
        "you should", "you shouldn't", "incorrect"
    ]
    lower = user_message.lower()
    return any(trigger in lower for trigger in correction_triggers)

def record_capability_gap(capability: str, context: str):
    """Record when we hit a capability gap to address later."""
    engine = SelfImprovementEngine()
    engine.handle_capability_gap(capability, context, auto_build=False)
    print(f"✅ Recorded capability gap: {capability}")

def get_improvement_stats() -> dict:
    """Get statistics on self-improvements made."""
    engine = SelfImprovementEngine()
    return engine.get_full_stats()


# ==================== CLI ====================

def main():
    if len(sys.argv) < 2:
        print("Self-Improvement Engine for Atlas")
        print("=" * 40)
        print("\nUsage: self_improve.py <command> [args]")
        print("\nCommands:")
        print("  reflect <task> <result_json>  - Post-task reflection loop")
        print("  gap <action> <error>          - Handle capability gap")
        print("  evolve <new_info> [context]   - Evolve knowledge")
        print("  meta                          - Run meta-improvement")
        print("  stats                         - Show full statistics")
        print("\nLegacy commands:")
        print("  log <cat> <trigger> <before> <after> <conf>")
        print("  add_fact <category> <subject> <content>")
        return
    
    engine = SelfImprovementEngine()
    cmd = sys.argv[1]
    
    if cmd == 'reflect' and len(sys.argv) >= 4:
        task = sys.argv[2]
        result = json.loads(sys.argv[3])
        output = engine.post_task_reflection(task, result)
        print(json.dumps(output, indent=2, default=str))
    
    elif cmd == 'gap' and len(sys.argv) >= 4:
        action = sys.argv[2]
        error = sys.argv[3]
        auto_build = '--build' in sys.argv
        output = engine.handle_capability_gap(action, error, auto_build)
        print(json.dumps(output, indent=2, default=str))
    
    elif cmd == 'evolve' and len(sys.argv) >= 3:
        new_info = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        output = engine.evolve_knowledge(new_info, context)
        print(json.dumps(output, indent=2, default=str))
    
    elif cmd == 'meta':
        output = engine.run_meta_improvement()
        print(json.dumps(output, indent=2, default=str))
    
    elif cmd == 'stats':
        stats = engine.get_full_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    # Legacy commands
    elif cmd == 'log' and len(sys.argv) >= 7:
        log_improvement(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], float(sys.argv[6]))
    
    elif cmd == 'add_fact' and len(sys.argv) >= 5:
        add_fact(sys.argv[2], sys.argv[3], sys.argv[4])
    
    else:
        print("Invalid command or arguments")
        print("Run without arguments for help")


if __name__ == "__main__":
    main()
