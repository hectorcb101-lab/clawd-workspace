"""
Atlas OS Training Runner

Orchestrates the fine-tuning pipeline.
NOTE: This is a scaffold - actual training requires GPU environment.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .config import AtlasTrainingConfig, get_preset, estimate_vram
from .exporter import export_all, get_stats


@dataclass
class TrainingRun:
    """Record of a training run."""
    id: str
    config: AtlasTrainingConfig
    status: str  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metrics: Dict[str, Any] = None
    error: Optional[str] = None
    output_path: Optional[str] = None


RUNS_DIR = Path.home() / "clawd" / "projects" / "atlas-os" / "data" / "training-runs"


class TrainingRunner:
    """
    Orchestrates Atlas fine-tuning runs.
    
    Usage:
        runner = TrainingRunner()
        run = runner.prepare("standard")
        runner.execute(run)
    """
    
    def __init__(self):
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
    
    def prepare(
        self,
        preset: str = "standard",
        config: Optional[AtlasTrainingConfig] = None,
    ) -> TrainingRun:
        """
        Prepare a training run.
        
        1. Export training data
        2. Create run configuration
        3. Estimate requirements
        """
        if config is None:
            config = get_preset(preset)
        
        # Generate run ID
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Export training data
        print(f"📦 Exporting training data...")
        exports = export_all(prefix=run_id, min_quality=3)
        
        # Update config with data paths
        config.sft_dataset = str(exports["sft"].output_path) if exports["sft"].entries > 0 else None
        config.dpo_dataset = str(exports["dpo"].output_path) if exports["dpo"].entries > 0 else None
        config.output_dir = str(run_dir / "output")
        
        # Save config
        config.save(run_dir / "config.json")
        
        # Estimate requirements
        vram = estimate_vram(config)
        
        # Create run record
        run = TrainingRun(
            id=run_id,
            config=config,
            status="pending",
            metrics={
                "data_stats": {
                    "sft_entries": exports["sft"].entries,
                    "dpo_entries": exports["dpo"].entries,
                    "reasoning_entries": exports["reasoning"].entries,
                },
                "vram_estimate": vram,
            }
        )
        
        # Save run record
        with open(run_dir / "run.json", "w") as f:
            json.dump({
                "id": run.id,
                "status": run.status,
                "config_path": str(run_dir / "config.json"),
                "metrics": run.metrics,
            }, f, indent=2)
        
        print(f"✅ Prepared run: {run_id}")
        print(f"   SFT entries: {exports['sft'].entries}")
        print(f"   DPO entries: {exports['dpo'].entries}")
        print(f"   Estimated VRAM: {vram['estimated_vram_gb']} GB")
        print(f"   Recommended: {vram['recommended_gpu']}")
        
        return run
    
    def generate_script(self, run: TrainingRun) -> Path:
        """Generate the training script for a run."""
        run_dir = RUNS_DIR / run.id
        script_path = run_dir / "train.py"
        
        script = '''#!/usr/bin/env python3
"""
Atlas Fine-Tuning Script
Generated for run: {run_id}

Run with:
    python train.py

Or on RunPod/Lambda:
    pip install -r requirements.txt
    python train.py
"""

import json
from pathlib import Path

# Check dependencies
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, DPOTrainer
    from datasets import load_dataset
except ImportError as e:
    print(f"Missing dependency: {{e}}")
    print("Install with: pip install torch transformers peft trl datasets accelerate bitsandbytes")
    exit(1)

# Load config
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config = json.load(f)

print(f"🚀 Starting Atlas fine-tuning")
print(f"   Base model: {{config['base_model']}}")
print(f"   Output: {{config['output_dir']}}")

# Setup LoRA config
lora_config = LoraConfig(
    r=config["lora"]["r"],
    lora_alpha=config["lora"]["lora_alpha"],
    lora_dropout=config["lora"]["lora_dropout"],
    bias=config["lora"]["bias"],
    target_modules=config["lora"]["target_modules"],
    task_type="CAUSAL_LM",
)

# Load model and tokenizer
print("📥 Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    config["base_model"],
    torch_dtype=torch.bfloat16 if config["training"]["bf16"] else torch.float16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
tokenizer.pad_token = tokenizer.eos_token

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Phase 1: SFT
if config["do_sft"] and config.get("sft_dataset"):
    print("\\n📚 Phase 1: Supervised Fine-Tuning")
    
    sft_dataset = load_dataset("json", data_files=config["sft_dataset"], split="train")
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=sft_dataset,
        tokenizer=tokenizer,
        max_seq_length=2048,
        args=dict(
            output_dir=config["output_dir"] + "/sft",
            num_train_epochs=config["training"]["num_epochs"],
            per_device_train_batch_size=config["training"]["batch_size"],
            gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
            learning_rate=config["training"]["learning_rate"],
            warmup_ratio=config["training"]["warmup_ratio"],
            logging_steps=config["training"]["logging_steps"],
            save_steps=config["training"]["save_steps"],
            bf16=config["training"]["bf16"],
            gradient_checkpointing=config["training"]["gradient_checkpointing"],
        ),
    )
    
    trainer.train()
    trainer.save_model(config["output_dir"] + "/sft-final")
    print("✅ SFT complete")

# Phase 2: DPO
if config["do_dpo"] and config.get("dpo_dataset"):
    print("\\n🎯 Phase 2: Direct Preference Optimization")
    
    dpo_dataset = load_dataset("json", data_files=config["dpo_dataset"], split="train")
    
    trainer = DPOTrainer(
        model=model,
        ref_model=None,  # Use implicit reference
        train_dataset=dpo_dataset,
        tokenizer=tokenizer,
        beta=config["dpo"]["beta"],
        args=dict(
            output_dir=config["output_dir"] + "/dpo",
            num_train_epochs=config["training"]["num_epochs"],
            per_device_train_batch_size=config["training"]["batch_size"],
            gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
            learning_rate=config["training"]["learning_rate"] / 2,  # Lower LR for DPO
            logging_steps=config["training"]["logging_steps"],
            save_steps=config["training"]["save_steps"],
            bf16=config["training"]["bf16"],
        ),
    )
    
    trainer.train()
    trainer.save_model(config["output_dir"] + "/dpo-final")
    print("✅ DPO complete")

# Merge adapter
if config["merge_adapter"]:
    print("\\n🔗 Merging adapter into base model...")
    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(config["output_dir"] + "/merged")
    tokenizer.save_pretrained(config["output_dir"] + "/merged")
    print("✅ Merged model saved")

print("\\n🎉 Training complete!")
print(f"   Output: {{config['output_dir']}}")
'''.format(run_id=run.id)
        
        with open(script_path, "w") as f:
            f.write(script)
        
        script_path.chmod(0o755)
        
        # Also generate requirements
        requirements = """# Atlas Fine-Tuning Requirements
torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
trl>=0.7.0
datasets>=2.14.0
accelerate>=0.25.0
bitsandbytes>=0.41.0
sentencepiece
protobuf
"""
        with open(run_dir / "requirements.txt", "w") as f:
            f.write(requirements)
        
        print(f"📝 Generated training script: {script_path}")
        print(f"📝 Generated requirements: {run_dir / 'requirements.txt'}")
        
        return script_path
    
    def list_runs(self) -> list:
        """List all training runs."""
        runs = []
        for run_dir in RUNS_DIR.iterdir():
            if run_dir.is_dir():
                run_file = run_dir / "run.json"
                if run_file.exists():
                    with open(run_file) as f:
                        runs.append(json.load(f))
        return sorted(runs, key=lambda x: x["id"], reverse=True)
    
    def get_run(self, run_id: str) -> Optional[Dict]:
        """Get a specific run by ID."""
        run_file = RUNS_DIR / run_id / "run.json"
        if run_file.exists():
            with open(run_file) as f:
                return json.load(f)
        return None


def prepare_training(preset: str = "standard") -> TrainingRun:
    """Convenience function to prepare a training run."""
    runner = TrainingRunner()
    return runner.prepare(preset)


def list_training_runs() -> list:
    """Convenience function to list training runs."""
    runner = TrainingRunner()
    return runner.list_runs()
