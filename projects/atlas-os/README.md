# Atlas OS

**A model-agnostic AI scaffold designed for continuous self-improvement.**

Atlas OS is infrastructure for building an AI assistant that gets better over time. It captures training signal from everyday operation and prepares it for fine-tuning on open-source models.

## Vision

Current state: Scaffold around Claude (API) to improve context and consistency.

End goal: Fine-tuned open-source model with Atlas identity, where we control the weights.

The path:
1. Build robust scaffold (memory, self-awareness, judgment) ✅
2. Capture high-quality training signal automatically ✅
3. Create model-agnostic interface ✅
4. Build evaluation pipeline to measure "Atlas-ness" ✅
5. Train on open-source model
6. Close the loop: continuous improvement through fine-tuning

## Components

### Core Systems

| System | CLI | Purpose |
|--------|-----|---------|
| **Integration Bus** | `atlas-bus` | Central event routing, auto-captures training data |
| **LLM Interface** | `atlas-llm` | Model-agnostic LLM access |
| **Evaluation** | `atlas-eval` | Measure "Atlas-ness" of models |
| **Training** | `atlas-finetune` | Prepare and manage fine-tuning runs |

### Integrated Systems

| System | CLI | Purpose |
|--------|-----|---------|
| **Memory** | `atlas-mem` | Persistent memory with semantic search |
| **Self-Awareness** | `atlas-self` | Outcome/correction tracking |
| **Judgment** | `atlas-judge` | Meta-cognitive principles |
| **Self-Modification** | `atlas-mod` | Instruction updates |

## Quick Start

```bash
# Check event bus stats
atlas-bus stats

# Test LLM connection
atlas-llm test -p openai

# Run evaluation
atlas-eval run -p openai -m gpt-4o-mini

# Check training data
atlas-finetune stats
```

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      ATLAS OS SCAFFOLD                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   atlas-self      atlas-judge      atlas-mod                │
│        │               │               │                    │
│        └───────────────┼───────────────┘                    │
│                        ▼                                    │
│                 Integration Bus                             │
│                        │                                    │
│        ┌───────────────┼───────────────┐                    │
│        ▼               ▼               ▼                    │
│   Training Data   Event Log      LLM Interface              │
│        │                              │                     │
│        │              ┌───────────────┼───────────────┐     │
│        ▼              ▼               ▼               ▼     │
│    Exports        Claude          Ollama          vLLM      │
│        │                                                    │
│        ▼                                                    │
│   Fine-Tuning ──────────────────────────────────────────►   │
│                     [Future Atlas Model]                    │
└────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Normal operation** → Systems emit events to bus
2. **Bus** → Logs events, auto-captures training data
3. **Training data** → Accumulates in structured formats
4. **Export** → Generate DPO/SFT datasets
5. **Fine-tune** → Train open-source model
6. **Evaluate** → Measure improvement
7. **Deploy** → Switch to fine-tuned model
8. **Repeat**

## File Structure

```
atlas-os/
├── config/
│   └── llm.json           # LLM provider config
├── data/
│   ├── events/            # Event bus logs
│   ├── eval/              # Evaluation reports
│   └── training-runs/     # Training run configs
├── docs/
│   └── MODEL_SWITCHING.md # Guide for swapping models
├── src/
│   ├── bus/               # Integration bus
│   ├── llm/               # LLM abstraction
│   ├── eval/              # Evaluation pipeline
│   ├── training/          # Fine-tuning infrastructure
│   └── judgment/          # Judgment layer
└── README.md
```

## Training Data Formats

### Corrections (DPO)
```json
{"prompt": "context", "chosen": "correct response", "rejected": "wrong response"}
```

### Instructions (SFT)
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### Reasoning (Chain-of-Thought)
```json
{"situation": "...", "reasoning": "...", "decision": "..."}
```

## Evaluation Scenarios

14 scenarios across 6 categories:
- **Personality**: No sycophancy, has opinions, respectful disagreement
- **Reasoning**: Engineering mindset, architecture before code
- **Tone**: Concise when appropriate, thorough when needed
- **Values**: Acknowledges correction, handles ambition
- **Honesty**: Calibrated uncertainty, admits limitations
- **Engineering**: Design for failure, utility over aesthetics

Baseline: GPT-4o-mini scores 68.4/100 on "Atlas-ness".

## Training Presets

| Preset | Model | Epochs | LoRA | VRAM |
|--------|-------|--------|------|------|
| quick | Qwen 7B | 1 | r=32 | ~3 GB |
| standard | Qwen 7B | 3 | r=64 | ~4 GB |
| thorough | Qwen 7B | 5 | r=128 | ~5 GB |
| large_model | Qwen 72B | 2 | r=32 | ~17 GB |

## Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Integration Bus | ✅ Complete |
| 2 | Format Standardisation | ✅ 90% |
| 3 | Model Abstraction | ✅ 85% |
| 4 | Evaluation Pipeline | ✅ 80% |
| 5 | Training Pipeline | 🔄 60% |
| 6 | Closed-Loop Learning | ⏳ Pending |

## What's Next

1. Accumulate more training data through normal operation
2. Test fine-tuning on small model (Qwen 7B)
3. Evaluate fine-tuned model against baseline
4. Iterate on data quality and training approach
5. Scale to larger model when ready

---

*Created: 2026-02-03*
*Goal: AGI through continuous self-improvement*
