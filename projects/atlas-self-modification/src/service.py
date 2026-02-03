"""
Core service for Atlas Self-Modification System.
Orchestrates proposals, validation, application, and rollback.
Integrated with Atlas OS Event Bus for training data capture.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pathlib import Path
import sys

from .models import (
    ModificationRequest, ModificationLog, ModificationRule, ModificationOutcome,
    Status, RiskLevel, Source, ModificationType, AppliedBy, TriggerType, OutcomeType,
    generate_modification_id
)
from .repository import ModificationRepository, LogRepository, RuleRepository, OutcomeRepository
from .risk import assess_risk, requires_approval, explain_risk
from .file_ops import safe_modify, read_file, is_protected, restore_from_content

# Add Atlas OS bus to path
sys.path.insert(0, str(Path.home() / "clawd" / "projects" / "atlas-os" / "src"))

def _emit_mod_to_bus(action: str, mod_id: str, file: str, reason: str, outcome: str = None):
    """Emit modification event to Atlas OS Event Bus (non-blocking, fail-safe)."""
    try:
        from bus import emit, AtlasEvent, EventType, EventSource, TrainingMeta, TrainingFormat
        event = AtlasEvent(
            type=EventType.MOD_APPLY if action == "apply" else EventType.MOD_ROLLBACK,
            source=EventSource.MODIFICATION,
            summary=f"{action.capitalize()}: {Path(file).name} - {reason[:50]}",
            data={
                "modification_id": mod_id,
                "target_file": file,
                "action": action,
                "reason": reason,
                "outcome": outcome
            },
            training=TrainingMeta(usable=False)  # Mod events aren't directly training data
        )
        emit(event)
    except Exception:
        pass  # Don't let bus errors break modification system


# Workspace root
WORKSPACE = Path.home() / "clawd"


class ModificationService:
    """Main service for self-modification operations."""
    
    def __init__(self):
        self.mods = ModificationRepository()
        self.logs = LogRepository()
        self.rules = RuleRepository()
        self.outcomes = OutcomeRepository()
    
    def propose(
        self,
        target_file: str,
        modification_type: ModificationType,
        content: str,
        reason: str,
        source: Source = Source.MANUAL,
        source_id: Optional[str] = None,
        target_section: Optional[str] = None,
        evidence: Optional[str] = None,
        confidence: float = 0.5,
    ) -> Tuple[ModificationRequest, str]:
        """
        Propose a new modification.
        
        Returns:
            (ModificationRequest, risk_explanation)
        """
        # Normalize file path
        if not target_file.startswith('/'):
            target_file = str(WORKSPACE / target_file)
        
        # Verify file exists
        if not Path(target_file).exists():
            raise FileNotFoundError(f"Target file does not exist: {target_file}")
        
        # Create request
        mod = ModificationRequest(
            target_file=target_file,
            modification_type=modification_type,
            content=content,
            reason=reason,
            source=source,
            source_id=source_id,
            target_section=target_section,
            evidence=evidence,
            confidence=confidence,
        )
        
        # Assess risk
        risk_level, risk_score = assess_risk(mod)
        mod.risk_level = risk_level
        mod.risk_score = risk_score
        
        # Determine if approval required
        mod.requires_approval = requires_approval(risk_level) or is_protected(target_file)
        
        # Set evaluation deadline (7 days after potential application)
        mod.evaluation_deadline = datetime.now() + timedelta(days=7)
        
        # Save
        self.mods.save(mod)
        
        # Generate explanation
        explanation = explain_risk(mod, risk_score)
        
        return mod, explanation
    
    def list_pending(self, limit: int = 50) -> List[ModificationRequest]:
        """List pending modifications."""
        return self.mods.list_pending(limit)
    
    def list_all(self, status: Optional[Status] = None, limit: int = 50) -> List[ModificationRequest]:
        """List all modifications."""
        return self.mods.list_by_status(status, limit)
    
    def get(self, modification_id: str) -> Optional[ModificationRequest]:
        """Get a modification by ID."""
        return self.mods.get(modification_id)
    
    def approve(self, modification_id: str) -> bool:
        """Approve a pending modification."""
        mod = self.mods.get(modification_id)
        if not mod:
            raise ValueError(f"Modification not found: {modification_id}")
        
        if mod.status != Status.PENDING:
            raise ValueError(f"Cannot approve modification in status: {mod.status.value}")
        
        return self.mods.update_status(modification_id, Status.APPROVED)
    
    def reject(self, modification_id: str, reason: str) -> bool:
        """Reject a pending modification."""
        mod = self.mods.get(modification_id)
        if not mod:
            raise ValueError(f"Modification not found: {modification_id}")
        
        if mod.status != Status.PENDING:
            raise ValueError(f"Cannot reject modification in status: {mod.status.value}")
        
        return self.mods.update_status(
            modification_id, 
            Status.REJECTED,
            rejected_reason=reason
        )
    
    def apply(self, modification_id: str, by: AppliedBy = AppliedBy.HUMAN) -> ModificationLog:
        """
        Apply a modification.
        
        Returns:
            ModificationLog with full diff
        """
        mod = self.mods.get(modification_id)
        if not mod:
            raise ValueError(f"Modification not found: {modification_id}")
        
        # Check status
        valid_statuses = [Status.PENDING, Status.APPROVED]
        if mod.status not in valid_statuses:
            raise ValueError(f"Cannot apply modification in status: {mod.status.value}")
        
        # Check approval requirements
        if mod.requires_approval and mod.status != Status.APPROVED:
            raise ValueError(
                f"This modification requires approval (risk: {mod.risk_level.value}). "
                f"Run: atlas-mod approve {modification_id}"
            )
        
        # Apply the modification
        before, after, diff, git_hash = safe_modify(
            file_path=mod.target_file,
            modification_type=mod.modification_type.value,
            content=mod.content,
            section=mod.target_section,
            modification_id=mod.id,
            reason=mod.reason,
        )
        
        # Create log
        log = ModificationLog(
            modification_id=mod.id,
            file_path=mod.target_file,
            before_content=before,
            after_content=after,
            diff=diff,
            git_commit_hash=git_hash,
        )
        self.logs.save(log)
        
        # Update status
        self.mods.update_status(
            modification_id,
            Status.APPLIED,
            applied_at=datetime.now(),
            applied_by=by
        )
        
        # Emit to Atlas OS Event Bus
        _emit_mod_to_bus("apply", mod.id, mod.target_file, mod.reason, "success")
        
        return log
    
    def rollback(self, modification_id: str, reason: str) -> bool:
        """
        Rollback an applied modification.
        """
        mod = self.mods.get(modification_id)
        if not mod:
            raise ValueError(f"Modification not found: {modification_id}")
        
        if mod.status != Status.APPLIED:
            raise ValueError(f"Cannot rollback modification in status: {mod.status.value}")
        
        # Get the log
        log = self.logs.get_by_modification(modification_id)
        if not log:
            raise ValueError(f"No log found for modification: {modification_id}")
        
        if log.reverted_at:
            raise ValueError(f"Modification already rolled back")
        
        # Restore original content
        restore_from_content(
            file_path=log.file_path,
            content=log.before_content,
            modification_id=modification_id,
            reason=reason
        )
        
        # Mark log as reverted
        self.logs.mark_reverted(modification_id, reason)
        
        # Update status
        self.mods.update_status(modification_id, Status.ROLLED_BACK)
        
        # Emit to Atlas OS Event Bus
        _emit_mod_to_bus("rollback", modification_id, log.file_path, reason, "success")
        
        return True
    
    def get_history(self, file_path: Optional[str] = None, days: int = 30, limit: int = 50) -> List[ModificationRequest]:
        """Get modification history."""
        if file_path:
            if not file_path.startswith('/'):
                file_path = str(WORKSPACE / file_path)
            return self.mods.list_by_file(file_path, limit)
        else:
            return self.mods.list_by_status(None, limit)
    
    def get_log(self, modification_id: str) -> Optional[ModificationLog]:
        """Get the log for a modification."""
        return self.logs.get_by_modification(modification_id)
    
    def show(self, modification_id: str) -> dict:
        """Get full details of a modification."""
        mod = self.mods.get(modification_id)
        if not mod:
            raise ValueError(f"Modification not found: {modification_id}")
        
        log = self.logs.get_by_modification(modification_id)
        outcomes = self.outcomes.list_for_modification(modification_id)
        
        return {
            'modification': mod,
            'log': log,
            'outcomes': outcomes,
            'risk_explanation': explain_risk(mod, mod.risk_score),
        }
    
    def expire_stale(self, days: int = 14) -> int:
        """Expire pending modifications older than N days."""
        return self.mods.expire_stale(days)
    
    def record_outcome(
        self,
        modification_id: str,
        outcome_type: OutcomeType,
        metric_name: str,
        before_value: Optional[float] = None,
        after_value: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> int:
        """Record an outcome for a modification."""
        outcome = ModificationOutcome(
            modification_id=modification_id,
            outcome_type=outcome_type,
            metric_name=metric_name,
            before_value=before_value,
            after_value=after_value,
            notes=notes,
        )
        return self.outcomes.save(outcome)
    
    def stats(self) -> dict:
        """Get service statistics."""
        from .database import get_stats
        return get_stats()


# Singleton instance
_service: Optional[ModificationService] = None


def get_service() -> ModificationService:
    """Get the singleton service instance."""
    global _service
    if _service is None:
        _service = ModificationService()
    return _service
