"""
Export judgment layer to human-readable JUDGMENT.md
"""
from pathlib import Path
from datetime import datetime
from .storage import JudgmentStorage
from .models import PrincipleCategory


JUDGMENT_MD_PATH = Path.home() / "clawd" / "JUDGMENT.md"


def export_to_markdown(storage: JudgmentStorage, output_path: Path = JUDGMENT_MD_PATH) -> str:
    """
    Export all active principles to a human-readable markdown file.
    """
    principles = storage.list_principles(active_only=True)
    stats = storage.get_stats()
    
    lines = [
        "# JUDGMENT.md — Atlas Judgment Layer",
        "",
        f"*Auto-generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "These principles guide my decision-making. Rules say 'when X, do Y.'",
        "Principles say 'how to decide what to do.'",
        "",
        "---",
        "",
        f"**Active Principles:** {stats['principles']['active']}",
        f"**Applications Logged:** {stats['applications']}",
        "",
        "---",
        "",
    ]
    
    # Group by category
    by_category = {}
    for p in principles:
        cat = p.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)
    
    category_titles = {
        PrincipleCategory.DECISION: "🎯 Decision Principles",
        PrincipleCategory.METACOGNITIVE: "🧠 Meta-Cognitive Principles", 
        PrincipleCategory.PRIORITY: "📊 Priority Principles",
        PrincipleCategory.ESCALATION: "⚡ Escalation Principles",
    }
    
    category_descriptions = {
        PrincipleCategory.DECISION: "How to choose actions.",
        PrincipleCategory.METACOGNITIVE: "How to think about thinking.",
        PrincipleCategory.PRIORITY: "What matters most when.",
        PrincipleCategory.ESCALATION: "When to act vs. ask.",
    }
    
    for cat in PrincipleCategory:
        if cat not in by_category:
            continue
            
        lines.append(f"## {category_titles.get(cat, cat.value)}")
        lines.append("")
        lines.append(f"*{category_descriptions.get(cat, '')}*")
        lines.append("")
        
        for p in by_category[cat]:
            # Effectiveness indicator
            eff = p.effectiveness
            if eff is not None:
                eff_str = f" · {eff*100:.0f}% effective ({p.applications_count} uses)"
            elif p.applications_count > 0:
                eff_str = f" · {p.applications_count} uses (evaluating)"
            else:
                eff_str = ""
            
            lines.append(f"### {p.id}: {_truncate(p.content, 60)}")
            lines.append("")
            lines.append(f"> {p.content}")
            lines.append("")
            lines.append(f"**Why:** {p.rationale}")
            lines.append("")
            
            if p.examples:
                lines.append("**Examples:**")
                for ex in p.examples[:3]:  # Limit to 3
                    lines.append(f"- {ex}")
                lines.append("")
            
            if p.counter_examples:
                lines.append("**When NOT to apply:**")
                for ex in p.counter_examples[:2]:  # Limit to 2
                    lines.append(f"- {ex}")
                lines.append("")
            
            lines.append(f"*Confidence: {p.confidence*100:.0f}% · Priority: {p.priority}/10{eff_str}*")
            lines.append("")
            lines.append("---")
            lines.append("")
    
    content = "\n".join(lines)
    
    output_path.write_text(content)
    return str(output_path)


def _truncate(s: str, length: int) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= length:
        return s
    return s[:length-3] + "..."


if __name__ == "__main__":
    storage = JudgmentStorage()
    path = export_to_markdown(storage)
    print(f"Exported to {path}")
