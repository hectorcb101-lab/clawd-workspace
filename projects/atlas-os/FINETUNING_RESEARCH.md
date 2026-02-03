# Fine-Tuning Research & Planning

*Preparing for the eventual transition to a trainable open-source model.*

## Overview

When we're ready to move Atlas to an open-source model, we'll need to:
1. Select the right base model
2. Choose a fine-tuning approach
3. Train on our captured data
4. Evaluate the results
5. Iterate

---

## Base Model Candidates

### Top Tier (as of early 2026)

| Model | Parameters | Strengths | Considerations |
|-------|-----------|-----------|----------------|
| **Llama 3.1** | 8B, 70B, 405B | Meta's flagship, strong reasoning, good instruction following | 405B needs serious hardware |
| **Mistral Large** | 123B | Excellent multilingual, strong coding | Commercial license needed for some uses |
| **Qwen 2.5** | 7B-72B | Strong coding, good reasoning | From Alibaba, very capable |
| **DeepSeek V3** | 671B (MoE) | Massive scale, competitive with GPT-4 | MoE architecture, complex |
| **Gemma 2** | 9B, 27B | Google's open model, efficient | Smaller but punchy |

### Recommended Starting Point

**Qwen 2.5 72B** or **Llama 3.1 70B** — large enough to be capable, small enough to fine-tune on prosumer hardware with quantisation.

For initial experiments: **Qwen 2.5 7B** or **Llama 3.1 8B** — fast iteration, cheap to train.

---

## Fine-Tuning Approaches

### 1. Full Fine-Tuning

**What:** Update all model weights.

**Pros:**
- Maximum learning capacity
- Can significantly shift model behaviour

**Cons:**
- Requires massive VRAM (70B model = ~140GB+ for training)
- Expensive
- Risk of catastrophic forgetting

**When to use:** Final training run when you have resources and validated data.

---

### 2. LoRA (Low-Rank Adaptation)

**What:** Train small adapter matrices that modify layer outputs.

**Pros:**
- 10-100x less VRAM than full fine-tuning
- Fast to train
- Can merge adapters into base model
- Multiple adapters for different behaviours

**Cons:**
- Less learning capacity than full fine-tuning
- May not capture very complex behaviour shifts

**When to use:** Default approach for most fine-tuning. Start here.

**Typical settings:**
```python
lora_config = LoraConfig(
    r=64,              # Rank (higher = more capacity, more VRAM)
    lora_alpha=128,    # Scaling factor
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

---

### 3. QLoRA (Quantised LoRA)

**What:** LoRA but with the base model quantised to 4-bit.

**Pros:**
- Train 70B models on a single 48GB GPU
- Almost as good as full LoRA
- Very accessible

**Cons:**
- Slightly lower quality than full-precision LoRA
- Quantisation adds complexity

**When to use:** When hardware-constrained. Great for iteration.

**VRAM requirements:**
- 7B model: ~6GB
- 13B model: ~10GB
- 70B model: ~40GB

---

### 4. DPO (Direct Preference Optimisation)

**What:** Train directly on preference pairs (chosen vs rejected).

**Pros:**
- No need for a separate reward model
- More stable than RLHF
- Works well with LoRA

**Cons:**
- Needs high-quality preference data
- Can overfit to preferences

**When to use:** When we have enough correction data (100+ high-quality pairs minimum).

---

### 5. ORPO (Odds Ratio Preference Optimisation)

**What:** Newer alternative to DPO, combines SFT and preference learning.

**Pros:**
- Single training stage
- Often outperforms DPO
- Less prone to reward hacking

**When to use:** Worth trying as alternative to DPO.

---

## Training Pipeline

### Phase 1: SFT (Supervised Fine-Tuning)

First, fine-tune on high-quality instruction-response pairs:

```bash
# Using unsloth (fast LoRA training)
python train_sft.py \
  --model_name "Qwen/Qwen2.5-7B-Instruct" \
  --dataset_path ~/clawd/training-data/exports/sft_dataset.json \
  --output_dir ./atlas-sft \
  --lora_r 64 \
  --epochs 3
```

### Phase 2: DPO (Preference Alignment)

Then, align with preferences from corrections:

```bash
python train_dpo.py \
  --model_name ./atlas-sft \
  --dataset_path ~/clawd/training-data/exports/dpo_dataset.json \
  --output_dir ./atlas-dpo \
  --beta 0.1
```

### Phase 3: Merge & Evaluate

Merge LoRA weights into base model:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
model = PeftModel.from_pretrained(base, "./atlas-dpo")
merged = model.merge_and_unload()
merged.save_pretrained("./atlas-final")
```

---

## Compute Options

### Cloud GPU Rental

| Provider | GPU | $/hour | Good for |
|----------|-----|--------|----------|
| **RunPod** | A100 80GB | ~$2-3 | Production training |
| **Lambda Labs** | A100 80GB | ~$1.50 | Great value |
| **Vast.ai** | Various | $0.30-2 | Budget option |
| **Together.ai** | Cluster | Variable | Large-scale |

### Local Hardware

| GPU | VRAM | Can train |
|-----|------|-----------|
| RTX 4090 | 24GB | 7B full, 70B QLoRA |
| RTX 3090 | 24GB | 7B full, 70B QLoRA |
| A6000 | 48GB | 13B full, 70B LoRA |
| A100 | 80GB | 70B full |

**Recommendation:** Start with RunPod or Lambda for experiments. Consider local hardware if training frequently.

---

## Data Requirements

### Minimum Viable Dataset

| Data Type | Minimum | Ideal |
|-----------|---------|-------|
| SFT pairs | 500 | 5,000+ |
| Corrections (DPO) | 100 | 1,000+ |
| Evaluation scenarios | 50 | 200+ |

### Quality > Quantity

- 500 excellent examples beats 5000 mediocre ones
- Each example should clearly demonstrate desired behaviour
- Diverse coverage of scenarios/tasks

---

## Evaluation Plan

### Automated Metrics
- Perplexity on held-out data
- BLEU/ROUGE on expected responses
- Pass rate on evaluation scenarios

### Human Evaluation
- Does it "feel" like Atlas?
- Tone and personality match
- Reasoning quality
- Honest uncertainty calibration

### A/B Testing
- Run both models on same prompts
- Blind evaluation: which response is better?
- Track over time

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Data collection | Ongoing | Need ~3-6 months of quality data |
| First experiment | 1 week | 500+ SFT pairs, 100+ corrections |
| Iteration | 2-4 weeks | Eval results, feedback |
| Production model | 1-2 weeks | Sufficient data, validated approach |

---

## Tools & Libraries

### Training
- **Unsloth** — Fast LoRA training, highly optimised
- **Axolotl** — Config-driven training, very flexible
- **TRL** — HuggingFace's RLHF library
- **LLaMA-Factory** — Easy fine-tuning framework

### Serving
- **vLLM** — Fast inference, PagedAttention
- **llama.cpp** — CPU inference, quantisation
- **Ollama** — Easy local deployment

### Evaluation
- **lm-evaluation-harness** — Standard benchmarks
- **AlpacaEval** — Instruction-following evaluation

---

## Next Steps

1. [ ] Continue collecting training data (ongoing)
2. [ ] Set up RunPod/Lambda account
3. [ ] Run first experiment with small model (Qwen 7B)
4. [ ] Build evaluation pipeline
5. [ ] Iterate on data quality based on results

---

*Last updated: 2026-02-02*
