"""
Risk assessment engine for Atlas Self-Modification System.

Calculates risk level based on multiple factors:
- Target file sensitivity
- Modification type
- Content size
- Confidence level
- Evidence strength
"""

from .models import ModificationRequest, ModificationType, RiskLevel


# File sensitivity scores (higher = more sensitive)
FILE_SENSITIVITY = {
    'AGENTS.md': 30,
    'SOUL.md': 35,
    'USER.md': 25,
    'IDENTITY.md': 25,
    'TOOLS.md': 15,
    'HEARTBEAT.md': 5,
    'MEMORY.md': 20,
}

# Path pattern sensitivity
PATH_SENSITIVITY = {
    'skills/': 20,
    'memory/': 5,
    '.learnings/': 10,
    'projects/': 15,
}

# Modification type risk
TYPE_RISK = {
    ModificationType.APPEND: 5,
    ModificationType.EDIT: 15,
    ModificationType.DELETE: 25,
    ModificationType.RESTRUCTURE: 35,
}

# Risk level thresholds
THRESHOLDS = {
    'low': 20,
    'medium': 40,
    'high': 60,
}


def get_file_sensitivity(file_path: str) -> int:
    """Get sensitivity score for a file path."""
    # Check exact match first
    filename = file_path.split('/')[-1]
    if filename in FILE_SENSITIVITY:
        return FILE_SENSITIVITY[filename]
    
    # Check path patterns
    for pattern, score in PATH_SENSITIVITY.items():
        if pattern in file_path:
            return score
    
    # Default sensitivity
    return 10


def assess_risk(modification: ModificationRequest) -> tuple[RiskLevel, int]:
    """
    Calculate risk level based on multiple factors.
    
    Returns:
        (RiskLevel, risk_score)
    """
    risk_score = 0
    
    # Factor 1: Target file sensitivity (0-35 points)
    risk_score += get_file_sensitivity(modification.target_file)
    
    # Factor 2: Modification type (5-35 points)
    risk_score += TYPE_RISK.get(modification.modification_type, 20)
    
    # Factor 3: Content size - bigger changes = higher risk (0-15 points)
    content_lines = len(modification.content.split('\n'))
    if content_lines > 20:
        risk_score += 15
    elif content_lines > 10:
        risk_score += 10
    elif content_lines > 5:
        risk_score += 5
    
    # Factor 4: Confidence - lower confidence = higher risk (0-20 points)
    risk_score += int((1 - modification.confidence) * 20)
    
    # Factor 5: Evidence strength (0-15 points)
    if not modification.evidence:
        risk_score += 15
    elif len(modification.evidence) < 50:
        risk_score += 5
    
    # Factor 6: Section targeting - no section = higher risk (0-10 points)
    if modification.modification_type != ModificationType.APPEND:
        if not modification.target_section:
            risk_score += 10
    
    # Map to risk level
    if risk_score >= THRESHOLDS['high']:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= THRESHOLDS['medium']:
        risk_level = RiskLevel.HIGH
    elif risk_score >= THRESHOLDS['low']:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    return risk_level, risk_score


def requires_approval(risk_level: RiskLevel) -> bool:
    """Determine if a risk level requires human approval."""
    return risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


def explain_risk(modification: ModificationRequest, risk_score: int) -> str:
    """Generate a human-readable risk explanation."""
    factors = []
    
    # File sensitivity
    file_sens = get_file_sensitivity(modification.target_file)
    if file_sens >= 30:
        factors.append(f"🔴 High-sensitivity file ({modification.target_file})")
    elif file_sens >= 20:
        factors.append(f"🟡 Medium-sensitivity file ({modification.target_file})")
    else:
        factors.append(f"🟢 Low-sensitivity file ({modification.target_file})")
    
    # Modification type
    type_risk = TYPE_RISK.get(modification.modification_type, 20)
    if type_risk >= 25:
        factors.append(f"🔴 High-risk operation: {modification.modification_type.value}")
    elif type_risk >= 15:
        factors.append(f"🟡 Medium-risk operation: {modification.modification_type.value}")
    else:
        factors.append(f"🟢 Low-risk operation: {modification.modification_type.value}")
    
    # Content size
    content_lines = len(modification.content.split('\n'))
    if content_lines > 20:
        factors.append(f"🔴 Large change ({content_lines} lines)")
    elif content_lines > 10:
        factors.append(f"🟡 Medium change ({content_lines} lines)")
    else:
        factors.append(f"🟢 Small change ({content_lines} lines)")
    
    # Confidence
    if modification.confidence < 0.5:
        factors.append(f"🔴 Low confidence ({modification.confidence:.0%})")
    elif modification.confidence < 0.8:
        factors.append(f"🟡 Medium confidence ({modification.confidence:.0%})")
    else:
        factors.append(f"🟢 High confidence ({modification.confidence:.0%})")
    
    # Evidence
    if not modification.evidence:
        factors.append("🔴 No evidence provided")
    elif len(modification.evidence) < 50:
        factors.append("🟡 Weak evidence")
    else:
        factors.append("🟢 Evidence provided")
    
    return "\n".join(factors)
