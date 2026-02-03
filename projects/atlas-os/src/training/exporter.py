"""
Atlas OS Training Data Exporter

Export captured training data to formats suitable for fine-tuning.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Data directories
TRAINING_DATA_DIR = Path.home() / "clawd" / "training-data"
EXPORTS_DIR = TRAINING_DATA_DIR / "exports"


@dataclass
class ExportStats:
    """Statistics from an export."""
    format: str
    entries: int
    output_path: Path
    timestamp: str
    filters_applied: Dict[str, Any]


def load_jsonl(path: Path) -> List[Dict]:
    """Load entries from a JSONL file."""
    if not path.exists():
        return []
    
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def collect_corrections(
    min_quality: int = 1,
    since: Optional[str] = None,
) -> List[Dict]:
    """Collect correction entries for DPO training."""
    corrections_dir = TRAINING_DATA_DIR / "corrections"
    entries = []
    
    if not corrections_dir.exists():
        return entries
    
    for month_dir in corrections_dir.iterdir():
        if not month_dir.is_dir():
            continue
        
        jsonl_file = month_dir / "corrections.jsonl"
        if jsonl_file.exists():
            for entry in load_jsonl(jsonl_file):
                # Filter by quality
                quality = entry.get("meta", {}).get("quality", 3)
                if quality < min_quality:
                    continue
                
                # Filter by date
                if since:
                    entry_date = entry.get("timestamp", "")[:10]
                    if entry_date < since:
                        continue
                
                entries.append(entry)
    
    return entries


def collect_instructions(
    min_quality: int = 1,
    tags: Optional[List[str]] = None,
    since: Optional[str] = None,
) -> List[Dict]:
    """Collect instruction-response pairs for SFT training."""
    instructions_dir = TRAINING_DATA_DIR / "instructions"
    entries = []
    
    if not instructions_dir.exists():
        return entries
    
    for month_dir in instructions_dir.iterdir():
        if not month_dir.is_dir():
            continue
        
        jsonl_file = month_dir / "sft_pairs.jsonl"
        if jsonl_file.exists():
            for entry in load_jsonl(jsonl_file):
                # Filter by quality
                quality = entry.get("meta", {}).get("quality", 3)
                if quality < min_quality:
                    continue
                
                # Filter by tags
                if tags:
                    entry_tags = entry.get("meta", {}).get("tags", [])
                    if not any(t in entry_tags for t in tags):
                        continue
                
                # Filter by date
                if since:
                    entry_date = entry.get("timestamp", "")[:10]
                    if entry_date < since:
                        continue
                
                entries.append(entry)
    
    return entries


def collect_reasoning(
    min_quality: int = 1,
    since: Optional[str] = None,
) -> List[Dict]:
    """Collect reasoning traces for chain-of-thought training."""
    judgments_dir = TRAINING_DATA_DIR / "judgments"
    entries = []
    
    if not judgments_dir.exists():
        return entries
    
    for month_dir in judgments_dir.iterdir():
        if not month_dir.is_dir():
            continue
        
        jsonl_file = month_dir / "reasoning.jsonl"
        if jsonl_file.exists():
            for entry in load_jsonl(jsonl_file):
                quality = entry.get("meta", {}).get("quality", 3)
                if quality < min_quality:
                    continue
                
                if since:
                    entry_date = entry.get("timestamp", "")[:10]
                    if entry_date < since:
                        continue
                
                entries.append(entry)
    
    return entries


def export_dpo(
    output_name: Optional[str] = None,
    min_quality: int = 1,
    since: Optional[str] = None,
) -> ExportStats:
    """
    Export corrections as DPO dataset.
    
    Format:
    {"prompt": "...", "chosen": "...", "rejected": "..."}
    """
    corrections = collect_corrections(min_quality, since)
    
    # Convert to DPO format
    dpo_entries = []
    for c in corrections:
        dpo_entries.append({
            "prompt": c.get("prompt", ""),
            "chosen": c.get("chosen", ""),
            "rejected": c.get("rejected", ""),
        })
    
    # Write output
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = output_name or f"dpo_dataset_{timestamp}"
    output_path = EXPORTS_DIR / f"{output_name}.json"
    
    with open(output_path, "w") as f:
        json.dump(dpo_entries, f, indent=2)
    
    return ExportStats(
        format="dpo",
        entries=len(dpo_entries),
        output_path=output_path,
        timestamp=timestamp,
        filters_applied={"min_quality": min_quality, "since": since}
    )


def export_sft(
    output_name: Optional[str] = None,
    min_quality: int = 1,
    tags: Optional[List[str]] = None,
    since: Optional[str] = None,
    include_system: bool = True,
) -> ExportStats:
    """
    Export instructions as SFT dataset.
    
    Format (ShareGPT/OpenAI style):
    {"messages": [{"role": "...", "content": "..."}]}
    """
    instructions = collect_instructions(min_quality, tags, since)
    
    # Convert to SFT format
    sft_entries = []
    for inst in instructions:
        messages = inst.get("messages", [])
        if messages:
            sft_entries.append({"messages": messages})
    
    # Write output
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = output_name or f"sft_dataset_{timestamp}"
    output_path = EXPORTS_DIR / f"{output_name}.json"
    
    with open(output_path, "w") as f:
        json.dump(sft_entries, f, indent=2)
    
    return ExportStats(
        format="sft",
        entries=len(sft_entries),
        output_path=output_path,
        timestamp=timestamp,
        filters_applied={"min_quality": min_quality, "tags": tags, "since": since}
    )


def export_reasoning(
    output_name: Optional[str] = None,
    min_quality: int = 1,
    since: Optional[str] = None,
) -> ExportStats:
    """
    Export reasoning traces for chain-of-thought training.
    
    Format:
    {"situation": "...", "reasoning": "...", "decision": "..."}
    """
    reasoning = collect_reasoning(min_quality, since)
    
    # Write output
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = output_name or f"reasoning_dataset_{timestamp}"
    output_path = EXPORTS_DIR / f"{output_name}.json"
    
    with open(output_path, "w") as f:
        json.dump(reasoning, f, indent=2)
    
    return ExportStats(
        format="reasoning",
        entries=len(reasoning),
        output_path=output_path,
        timestamp=timestamp,
        filters_applied={"min_quality": min_quality, "since": since}
    )


def export_all(
    prefix: Optional[str] = None,
    min_quality: int = 1,
    since: Optional[str] = None,
) -> Dict[str, ExportStats]:
    """Export all training data types."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = prefix or f"atlas_{timestamp}"
    
    return {
        "dpo": export_dpo(f"{prefix}_dpo", min_quality, since),
        "sft": export_sft(f"{prefix}_sft", min_quality, since=since),
        "reasoning": export_reasoning(f"{prefix}_reasoning", min_quality, since),
    }


def get_stats() -> Dict[str, Any]:
    """Get statistics about available training data."""
    corrections = collect_corrections(min_quality=0)
    instructions = collect_instructions(min_quality=0)
    reasoning = collect_reasoning(min_quality=0)
    
    return {
        "corrections": len(corrections),
        "instructions": len(instructions),
        "reasoning": len(reasoning),
        "total": len(corrections) + len(instructions) + len(reasoning),
        "exports_dir": str(EXPORTS_DIR),
    }


if __name__ == "__main__":
    print("Training Data Stats:")
    print(json.dumps(get_stats(), indent=2))
