"""
Atlas OS Training Pipeline

Fine-tuning infrastructure for Atlas models.
"""

from .exporter import (
    export_dpo,
    export_sft,
    export_reasoning,
    export_all,
    get_stats as get_training_stats,
    collect_corrections,
    collect_instructions,
    collect_reasoning,
)

from .config import (
    AtlasTrainingConfig,
    LoRAConfig,
    TrainingConfig,
    DPOConfig,
    get_preset,
    estimate_vram,
    PRESETS,
)

from .runner import (
    TrainingRunner,
    TrainingRun,
    prepare_training,
    list_training_runs,
)

__all__ = [
    # Exporter
    "export_dpo",
    "export_sft",
    "export_reasoning",
    "export_all",
    "get_training_stats",
    "collect_corrections",
    "collect_instructions",
    "collect_reasoning",
    # Config
    "AtlasTrainingConfig",
    "LoRAConfig",
    "TrainingConfig",
    "DPOConfig",
    "get_preset",
    "estimate_vram",
    "PRESETS",
    # Runner
    "TrainingRunner",
    "TrainingRun",
    "prepare_training",
    "list_training_runs",
]
