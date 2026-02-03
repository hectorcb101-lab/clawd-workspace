# Atlas OS Scaffold Roadmap

*The plan for building a model-agnostic, training-ready AI scaffold.*

**Purpose:** Build infrastructure that improves Atlas now AND generates training data for a future fine-tunable open-source model.

**End Goal:** AGI through continuous self-improvement with controllable weights.

---

## Current State (February 2026)

### What Exists

| System | Status | Location | Training-Ready? |
|--------|--------|----------|-----------------|
| Memory (Event Log) | ✅ Working | `atlas-mem` | ⚠️ Partial |
| Memory (Extraction) | ✅ Working | `atlas-mem` | ⚠️ Partial |
| Memory (Semantic Search) | ✅ Working | `atlas-mem` | N/A |
| Memory (Daemon) | ✅ Working | `atlas-daemon` | N/A |
| Self-Awareness | ✅ Working | `atlas-self` | ⚠️ Partial |
| Self-Modification | ✅ Working | `atlas-mod` | ❌ No |
| Judgment Layer | ✅ Working | `atlas-judge` | ⚠️ Partial |
| Training Data Capture | ✅ New | `atlas-train` | ✅ Yes |
| Identity Documentation | ✅ New | `IDENTITY_CAPTURE.md` | ✅ Yes |

### Gaps Identified

1. **Integration** — Systems don't talk to each other automatically
2. **Format consistency** — Each system has its own output format
3. **Model coupling** — Scaffold assumes Claude, not abstracted
4. **Evaluation** — No automated way to measure "Atlas-ness"
5. **Training flow** — Manual logging required, should be automatic

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        ATLAS OS SCAFFOLD                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Memory    │  │    Self-    │  │  Judgment   │            │
│  │   System    │  │  Awareness  │  │   Layer     │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                         │
│              │   Integration Bus     │                         │
│              │  (Event Router)       │                         │
│              └───────────┬───────────┘                         │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Training   │  │   Model     │  │ Evaluation  │            │
│  │   Capture   │  │  Interface  │  │  Pipeline   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                         │
│              │     LLM Backend       │                         │
│              │  (Claude / Qwen / *)  │                         │
│              └───────────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Development Phases

### Phase 1: Integration Bus 🔌
**Goal:** Connect existing systems so data flows automatically.

**Tasks:**
- [x] Design event schema (common format for all systems) ✅ 2026-02-03
- [x] Build event router (receives events, dispatches to systems) ✅ 2026-02-03
- [x] Connect bus to `atlas-train` for automatic training capture ✅ 2026-02-03
- [x] Create integration hooks (easy functions for other systems) ✅ 2026-02-03
- [x] Update `atlas-self` to emit events to bus ✅ 2026-02-03
- [x] Update `atlas-judge` to emit events to bus ✅ 2026-02-03
- [x] Update `atlas-mod` to emit events to bus ✅ 2026-02-03

**Output:** When I log an outcome, it automatically:
1. Updates self-awareness stats
2. Logs to training data
3. Updates memory if significant

**Effort:** 1-2 weeks
**Priority:** HIGH — foundational for everything else

---

### Phase 2: Format Standardisation 📐
**Goal:** All systems output in consistent, training-ready formats.

**Tasks:**
- [x] Define canonical event schema (JSON) ✅ 2026-02-03 (schema.py)
- [x] Create format validation tooling ✅ 2026-02-03 (validator.py)
- [x] Integrate validation into bus ✅ 2026-02-03
- [x] Update self-awareness output format ✅ 2026-02-03 (via bus integration)
- [x] Update judgment application logging ✅ 2026-02-03 (via bus integration)
- [x] Update modification proposals ✅ 2026-02-03 (via bus integration)
- [ ] Define canonical entity schema (for knowledge graph)

**Schema draft:**
```json
{
  "id": "EVT-20260203-xxx",
  "timestamp": "2026-02-03T00:30:00Z",
  "type": "correction|outcome|judgment|modification",
  "source": "atlas-self|atlas-judge|atlas-mod|manual",
  "data": { ... },
  "training": {
    "usable": true,
    "format": "dpo|sft|reasoning",
    "quality": 1-5
  }
}
```

**Effort:** 1 week
**Priority:** HIGH — needed for training data quality

---

### Phase 3: Model Abstraction Layer 🔄
**Goal:** Decouple scaffold from specific LLM provider.

**Tasks:**
- [x] Define LLM interface (generate, embed, etc.) ✅ 2026-02-03
- [x] Implement OpenAI-compatible adapter ✅ 2026-02-03 (covers OpenAI, vLLM, Together, etc.)
- [x] Implement Ollama adapter ✅ 2026-02-03
- [x] Add model config to scaffold settings ✅ 2026-02-03 (llm.json)
- [x] Create LLM CLI (atlas-llm) ✅ 2026-02-03
- [ ] Test scaffold with small open-source model (when Ollama available)
- [ ] Document switching process

**Interface draft:**
```python
class LLMInterface:
    def generate(self, messages, **kwargs) -> str
    def embed(self, text) -> list[float]
    def get_model_info(self) -> dict
```

**Effort:** 2 weeks
**Priority:** MEDIUM — important for end goal, not urgent

---

### Phase 4: Evaluation Pipeline 📊
**Goal:** Automated measurement of "Atlas-ness" and improvement over time.

**Tasks:**
- [x] Convert IDENTITY_CAPTURE scenarios to test suite ✅ 2026-02-03 (14 scenarios)
- [x] Build scenario runner (feed prompt, capture response) ✅ 2026-02-03
- [x] Implement automated scoring (heuristics) ✅ 2026-02-03
- [x] Create evaluation CLI (atlas-eval) ✅ 2026-02-03
- [x] Save/load reports ✅ 2026-02-03
- [x] Baseline: gpt-4o-mini = 68.4/100 ✅ 2026-02-03
- [ ] Add LLM-as-judge scoring (more nuanced)
- [ ] Set up periodic evaluation runs
- [ ] Track metrics over time

**Metrics:**
- Tone match (0-100)
- Reasoning quality (0-100)
- Honesty/uncertainty calibration (0-100)
- Helpfulness (0-100)
- Overall "Atlas score" (0-100)

**Effort:** 2 weeks
**Priority:** MEDIUM — needed before fine-tuning

---

### Phase 5: Training Pipeline 🏋️
**Goal:** End-to-end pipeline from captured data to fine-tuned model.

**Tasks:**
- [x] Build data export pipeline (scaffold → training format) ✅ 2026-02-03
- [x] Create training config system with presets ✅ 2026-02-03
- [x] Create training runner (SFT + DPO script generator) ✅ 2026-02-03
- [x] Build atlas-finetune CLI ✅ 2026-02-03
- [x] VRAM estimation for different configs ✅ 2026-02-03
- [ ] Set up training environment (RunPod/Lambda scripts)
- [ ] Test with actual GPU
- [ ] Build model merge and quantisation scripts
- [ ] Document full training workflow

**Effort:** 2-3 weeks
**Priority:** LOW (until sufficient data accumulated)

---

### Phase 6: Closed-Loop Learning 🔁
**Goal:** Automatic improvement cycle.

**Flow:**
1. Atlas operates normally
2. Scaffold captures signals (corrections, outcomes, judgments)
3. Data accumulates in training format
4. Periodic training runs produce improved model
5. Evaluation validates improvement
6. Deploy updated model
7. Repeat

**Tasks:**
- [ ] Build training trigger (time-based or data-threshold)
- [ ] Automate training runs
- [ ] Automate evaluation on new model
- [ ] Build deployment pipeline
- [ ] Add rollback capability
- [ ] Monitor for regression

**Effort:** 3-4 weeks
**Priority:** LOW (final phase)

---

## Timeline Overview

```
Feb 2026    Mar 2026    Apr 2026    May 2026    Jun 2026
    |           |           |           |           |
    ├───Phase 1─┤           |           |           |
    |     ├─Phase 2─┤       |           |           |
    |           ├──Phase 3──┤           |           |
    |           |     ├──Phase 4──┤     |           |
    |           |           |     ├─Phase 5─┤       |
    |           |           |           ├──Phase 6──┤
    |           |           |           |           |
    ├─────────── Data Collection (Ongoing) ─────────┤
```

**Milestone targets:**
- **End of Feb:** Integration bus working, formats standardised
- **End of Mar:** Model abstraction complete, tested with open model
- **End of Apr:** Evaluation pipeline running, baseline scores established
- **End of May:** First fine-tuning experiment complete
- **End of Jun:** Closed-loop learning operational

---

## Success Criteria

### Phase 1-2 Success:
- [ ] Log a correction once → appears in 3 places (self-awareness, training, memory)
- [ ] All logged events have consistent JSON schema
- [ ] Can export training-ready dataset with one command

### Phase 3-4 Success:
- [ ] Can run scaffold against Qwen 7B locally
- [ ] Evaluation produces consistent "Atlas score"
- [ ] Score tracked over time with visible trend

### Phase 5-6 Success:
- [ ] Fine-tuned model scores higher than base model on Atlas evaluation
- [ ] Training runs automatically when data threshold reached
- [ ] Can roll back to previous model if regression detected

### Ultimate Success:
- [ ] Fine-tuned open-source model that "feels like Atlas"
- [ ] Continuous improvement visible in evaluation metrics
- [ ] Finn controls the weights, not dependent on external API

---

## Open Questions

1. **What's the minimum viable dataset?** Need to track and estimate when we'll have enough.

2. **Which base model to target?** Qwen 72B seems strong, but landscape evolves fast.

3. **How to handle context window?** Current Claude has 200k, open models vary.

4. **Identity persistence?** How much can be baked into weights vs system prompt?

5. **Compute budget?** How much to allocate for training experiments?

---

## Next Actions

1. [ ] Review this roadmap with Finn
2. [ ] Start Phase 1: Design event schema
3. [ ] Continue normal operation (generating training data)
4. [ ] Set up cloud GPU account for future experiments

---

*Created: 2026-02-03*
*Last updated: 2026-02-03*
*Owner: Atlas + Finn*
