"""
Atlas OS Training Configuration

Configuration and presets for fine-tuning runs.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path
import json


@dataclass
class LoRAConfig:
    """LoRA adapter configuration."""
    r: int = 64                          # Rank
    lora_alpha: int = 128                # Scaling factor
    lora_dropout: float = 0.05           # Dropout
    bias: str = "none"                   # Bias training
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])


@dataclass
class TrainingConfig:
    """Training hyperparameters."""
    # Basic
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    
    # Scheduling
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    
    # Optimization
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    
    # Memory
    gradient_checkpointing: bool = True
    fp16: bool = False
    bf16: bool = True  # Better for newer GPUs
    
    # Logging
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100


@dataclass
class DPOConfig:
    """DPO-specific configuration."""
    beta: float = 0.1                    # KL penalty coefficient
    loss_type: str = "sigmoid"           # sigmoid, hinge, ipo
    max_length: int = 2048
    max_prompt_length: int = 1024


@dataclass
class AtlasTrainingConfig:
    """Complete configuration for Atlas fine-tuning."""
    # Model
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    output_dir: str = "./atlas-finetuned"
    
    # Data
    sft_dataset: Optional[str] = None
    dpo_dataset: Optional[str] = None
    eval_split: float = 0.1
    
    # Components
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dpo: DPOConfig = field(default_factory=DPOConfig)
    
    # Pipeline
    do_sft: bool = True
    do_dpo: bool = True
    merge_adapter: bool = True
    quantize_output: bool = False  # GGUF quantization
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def save(self, path: Path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'AtlasTrainingConfig':
        with open(path) as f:
            data = json.load(f)
        
        # Reconstruct nested configs
        data['lora'] = LoRAConfig(**data.get('lora', {}))
        data['training'] = TrainingConfig(**data.get('training', {}))
        data['dpo'] = DPOConfig(**data.get('dpo', {}))
        
        return cls(**data)


# Presets for different scenarios

PRESETS = {
    "quick": AtlasTrainingConfig(
        base_model="Qwen/Qwen2.5-7B-Instruct",
        training=TrainingConfig(
            num_epochs=1,
            batch_size=2,
            gradient_accumulation_steps=2,
        ),
        lora=LoRAConfig(r=32),
    ),
    
    "standard": AtlasTrainingConfig(
        base_model="Qwen/Qwen2.5-7B-Instruct",
        training=TrainingConfig(
            num_epochs=3,
            batch_size=4,
            gradient_accumulation_steps=4,
        ),
    ),
    
    "thorough": AtlasTrainingConfig(
        base_model="Qwen/Qwen2.5-7B-Instruct",
        training=TrainingConfig(
            num_epochs=5,
            batch_size=4,
            gradient_accumulation_steps=8,
            learning_rate=1e-5,
        ),
        lora=LoRAConfig(r=128, lora_alpha=256),
    ),
    
    "large_model": AtlasTrainingConfig(
        base_model="Qwen/Qwen2.5-72B-Instruct",
        training=TrainingConfig(
            num_epochs=2,
            batch_size=1,
            gradient_accumulation_steps=16,
            gradient_checkpointing=True,
        ),
        lora=LoRAConfig(r=32),  # Lower rank for memory
    ),
}


def get_preset(name: str) -> AtlasTrainingConfig:
    """Get a training preset by name."""
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
    return PRESETS[name]


def estimate_vram(config: AtlasTrainingConfig) -> Dict[str, float]:
    """Estimate VRAM requirements for a training config."""
    # Rough estimates based on model size
    model_sizes = {
        "7B": 14,   # GB for base model
        "13B": 26,
        "70B": 140,
        "72B": 144,
    }
    
    # Extract model size from name
    base_vram = 14  # Default 7B
    for size, vram in model_sizes.items():
        if size in config.base_model:
            base_vram = vram
            break
    
    # LoRA reduces requirements significantly
    lora_factor = 0.1 + (config.lora.r / 128) * 0.1
    
    # Quantization reduces further
    if "bnb" in str(config.training) or "4bit" in str(config.base_model):
        quant_factor = 0.25
    else:
        quant_factor = 1.0
    
    # Gradient checkpointing
    gc_factor = 0.6 if config.training.gradient_checkpointing else 1.0
    
    training_vram = base_vram * lora_factor * quant_factor * gc_factor
    
    # Add overhead for optimizer states, gradients
    training_vram *= 1.5
    
    # Batch size impact
    training_vram += config.training.batch_size * 0.5
    
    return {
        "estimated_vram_gb": round(training_vram, 1),
        "recommended_gpu": (
            "RTX 4090 (24GB)" if training_vram <= 20 else
            "A6000 (48GB)" if training_vram <= 40 else
            "A100 (80GB)" if training_vram <= 70 else
            "Multi-GPU required"
        )
    }
