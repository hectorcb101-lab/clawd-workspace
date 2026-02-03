# Atlas OS Training Data Specification

*Preparing for the transition to a fine-tunable open-source model.*

## Purpose

Everything captured by the Atlas OS scaffold should be structured as future training data. This document defines the formats and standards to ensure we're ready when the time comes.

---

## Data Types & Formats

### 1. Corrections (Preference Learning)

When Finn corrects Atlas, capture as a preference pair:

```json
{
  "id": "COR-20260202-001",
  "timestamp": "2026-02-02T23:45:00Z",
  "type": "correction",
  "context": "The situation/prompt that led to the response",
  "rejected": "What Atlas said (wrong)",
  "chosen": "What Atlas should have said (right)",
  "explanation": "Why the correction matters",
  "category": "factual|tone|judgment|process|other",
  "severity": "minor|moderate|major"
}
```

**Use for:** DPO (Direct Preference Optimization), RLHF

### 2. Instruction-Response Pairs (Supervised Fine-Tuning)

Good interactions worth reinforcing:

```json
{
  "id": "SFT-20260202-001",
  "timestamp": "2026-02-02T23:45:00Z",
  "type": "instruction_response",
  "system": "System prompt / context",
  "instruction": "User message / task",
  "response": "Atlas's response (good example)",
  "quality_score": 1-5,
  "tags": ["coding", "research", "communication", "reasoning"]
}
```

**Use for:** Supervised fine-tuning (SFT)

### 3. Judgment Applications (Reasoning Patterns)

When Atlas applies judgment principles:

```json
{
  "id": "JDG-20260202-001",
  "timestamp": "2026-02-02T23:45:00Z",
  "type": "judgment_application",
  "situation": "What Atlas was deciding",
  "principles_consulted": ["PRIN-001", "PRIN-003"],
  "reasoning": "How the principles informed the decision",
  "decision": "What Atlas decided",
  "outcome": "success|partial|failure",
  "outcome_notes": "What happened"
}
```

**Use for:** Teaching reasoning patterns, chain-of-thought fine-tuning

### 4. Outcome Tracking (Reinforcement Signal)

Task completion quality:

```json
{
  "id": "OUT-20260202-001",
  "timestamp": "2026-02-02T23:45:00Z",
  "type": "outcome",
  "task_description": "What Atlas was asked to do",
  "approach": "How Atlas approached it",
  "result": "success|partial|failure",
  "feedback": "Any explicit feedback from Finn",
  "learnings": "What should be learned from this"
}
```

**Use for:** Reward modeling, outcome-based training

---

## Storage Structure

```
~/clawd/training-data/
├── corrections/
│   └── 2026-02/
│       └── corrections.jsonl
├── instructions/
│   └── 2026-02/
│       └── sft_pairs.jsonl
├── judgments/
│   └── 2026-02/
│       └── judgment_apps.jsonl
├── outcomes/
│   └── 2026-02/
│       └── outcomes.jsonl
└── exports/
    └── dpo_dataset_v1.json
    └── sft_dataset_v1.json
```

**Format:** JSONL (one JSON object per line) for easy streaming and appending.

---

## Collection Triggers

### Automatic (via existing systems)
- Self-awareness corrections → `corrections/`
- Judgment layer applications → `judgments/`
- Outcome logging → `outcomes/`

### Manual / Prompted
- When Finn says "that was good" → prompt to log as SFT example
- When Finn corrects → prompt to log as correction pair
- Periodic review of conversations for high-quality examples

---

## Quality Standards

### Must have:
- Clear context (what led to this)
- Unambiguous signal (what was good/bad)
- Timestamps for temporal ordering
- Categories/tags for filtering

### Avoid:
- Vague corrections without clear "should have been"
- Examples that are too context-dependent to generalise
- Duplicate or near-duplicate entries

---

## Export Formats

When ready to fine-tune, export to standard formats:

### For DPO:
```json
{"prompt": "...", "chosen": "...", "rejected": "..."}
```

### For SFT:
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### For RLHF:
Requires reward model training first — separate pipeline.

---

## Next Steps

1. [ ] Create directory structure
2. [ ] Update self-awareness system to output in these formats
3. [ ] Update judgment layer to log applications
4. [ ] Build export scripts for training formats
5. [ ] Create CLI tool for manual logging (`atlas-train log ...`)
6. [ ] Document identity capture (separate file)

---

*Created: 2026-02-02*
*Purpose: Ensure all Atlas OS data collection serves the long-term goal of fine-tuning an open-source model.*
