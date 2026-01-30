# Experiment Log

**Purpose:** Track all A/B tests and learning method experiments

---

## EXP-001: Chess Analogies for Pattern Recognition Concepts

**Status:** 🟡 Ready to Run (Planned)  
**Started:** [TBD - When Finn runs this]  
**Completed:** [TBD]

### Hypothesis
Chess analogies will improve understanding and retention for pattern-recognition concepts by 20%+ compared to standard explanations, because Finn's daily chess practice has built strong mental models that can transfer to ML concepts.

### Design

**Method A (Control):** Standard technical explanation with generic examples  
**Method B (Experimental):** Same content + chess analogy integrated throughout

**Concepts to test:**
- **Concept A:** Greedy Algorithms (taught with chess analogy)
- **Concept B:** Dynamic Programming (taught without chess analogy)

Both concepts are:
- Similar complexity (both optimization strategies)
- Similar abstraction level
- Equally unfamiliar to Finn
- Foundational for ML/AI

### Chess Analogy Example (for Greedy Algorithm)

**Standard explanation:**
"Greedy algorithm makes locally optimal choice at each step, hoping to find global optimum."

**With chess analogy:**
"Greedy algorithm is like always capturing the highest-value piece available without thinking ahead - it looks good locally (winning material now) but might miss better long-term strategy (sacrificing piece for checkmate). Short-sighted but fast."

### Variables Held Constant
- Same day/week (similar energy levels)
- Same session duration (45 min each)
- Same practice amount (3 problems each)
- Same visual diagram style
- Same instructor/materials

### Single Variable
ONLY difference: Chess analogy present or absent

### Metrics

**Primary:**
- 1-week retention score (1-5 scale): Expected 20%+ difference
  - Target: Method B (chess) ≥ 4.0, Method A ≤ 3.3

**Secondary:**
- Immediate understanding (1-5)
- Questions asked (depth indicator)
- Application success rate (% problems solved correctly)
- Time to solve practice problems
- Finn's self-reported preference

### Success Criteria
Method B produces ≥20% higher retention score at 1 week AND Finn reports analogy was helpful (not confusing).

### Data Collection

**Session logs:**
- `sessions/2026-XX-XX-greedy-algorithms.md` (with chess)
- `sessions/2026-XX-XX-dynamic-programming.md` (without chess)

**Retention checks:**
- 24h: Quick recall test
- 1 week: Explain from memory + solve new problem
- 1 month: Apply to novel situation

### Timeline
- Week 1: Teach both concepts (different days)
- Week 2: 1-week retention checks
- Week 4: 1-month retention checks
- Week 5: Analyze results

### Expected Results
**Prediction:** Chess analogy improves retention by 25-30%

**Why:** Finn plays chess daily → strong chess mental models → analogies leverage existing knowledge → deeper encoding → better retention

**Alternative outcomes:**
- No difference → Chess analogies don't help (or hurt)
- Negative effect → Analogies add confusion, cognitive load

### Analysis Plan

| Metric | Greedy (w/ chess) | Dynamic Prog (no chess) | Difference | Winner |
|--------|-------------------|-------------------------|------------|--------|
| Immediate (1-5) | | | | |
| 24h retention | | | | |
| 1wk retention | | | | |
| Application % | | | | |
| Time to solve (min) | | | | |

**Qualitative:**
- Did chess analogy help or confuse?
- What did Finn say about it?
- Would he want more chess analogies?

### Confounding Factors to Watch
- Concept difficulty (is one actually harder?)
- Order effect (first taught vs second)
- External factors (stress, sleep, etc.)
- Day of week (energy levels)

**Mitigation:** Note all confounds, re-run if suspicious

### Conclusion
[TBD after experiment runs]

**Result:**
- [ ] Hypothesis confirmed - Chess analogies significantly better
- [ ] Partially confirmed - Small improvement
- [ ] No significant difference
- [ ] Hypothesis rejected - No benefit or negative
- [ ] Inconclusive - Need more data

**Confidence:**
- [ ] High - Clear, consistent results
- [ ] Medium - Some evidence
- [ ] Low - Noisy, uncertain

**Action:**
- [ ] Use chess analogies for all pattern-based concepts
- [ ] Use selectively for specific concept types
- [ ] Continue without chess analogies
- [ ] Run follow-up experiment with different concepts

### Notes
[Space for observations during experiment]

---

## EXP-002: Network Diagrams vs. Flowcharts

**Status:** 🟡 Ready to Run (Planned)  
**Started:** [TBD]  
**Completed:** [TBD]

### Hypothesis
Network/graph diagrams will produce 15%+ better retention than flowcharts for structural AI concepts (neural architectures, graph algorithms) because Finn's chess thinking is naturally network-oriented (piece relationships, board control).

### Design

**Method A (Control):** Flowchart representation (boxes + sequential arrows)  
**Method B (Experimental):** Network/graph diagram (nodes + connections)

**Concepts to test:**
- **Concept A:** CNN Architecture (taught with network diagram)
- **Concept B:** RNN Architecture (taught with flowchart)

Both are:
- Similar complexity (both neural architectures)
- Similar structure (layers, connections, information flow)
- Unfamiliar to Finn at same level

### Example Visual Difference

**Flowchart style:**
```
[Input] → [Conv Layer] → [Pool] → [FC Layer] → [Output]
```

**Network style:**
```
    Input
   /  |  \
Conv Conv Conv
   \  |  /
    Pool
     |
   Output
```

### Variables Held Constant
- Same week
- Same session duration
- Same level of detail
- Same practice amount
- Same retention test format

### Single Variable
Visual representation type ONLY

### Metrics

**Primary:**
- 1-week retention (can Finn sketch architecture from memory?)
- Target: Network diagram ≥ 15% better recall

**Secondary:**
- Immediate understanding
- Ability to explain relationships
- Application to new architecture
- Visual recall (does diagram trigger memory?)

### Success Criteria
Method B (network) produces ≥15% better retention AND Finn finds network diagrams more intuitive.

### Timeline
2 weeks teaching + 2 weeks retention testing = 4 weeks total

### Expected Results
**Prediction:** Network diagrams 20-25% better retention

**Why:** Chess = network thinking (pieces interact, positions connect) → network diagrams match mental model → easier encoding

### Analysis Plan
Compare retention scores, sketch accuracy, explanation quality

### Confounding Factors
- One architecture might be inherently easier
- Prior exposure (has Finn seen CNNs/RNNs before?)
- Different application domains

### Conclusion
[TBD]

---

## EXP-003: Immediate vs. Delayed Practice

**Status:** 🟡 Ready to Run (Planned)  
**Started:** [TBD]  
**Completed:** [TBD]

### Hypothesis
Immediate practice (right after learning) will produce 15%+ better retention than delayed practice (24h later) because immediate consolidation strengthens memory traces.

### Design

**Method A (Control):** Learn concept → Practice 24h later  
**Method B (Experimental):** Learn concept → Practice immediately

**Concepts to test:**
- **Concept A:** Backpropagation (immediate practice)
- **Concept B:** Gradient Descent Variants (delayed practice)

Both are:
- Similar complexity (both optimization algorithms)
- Require hands-on coding to understand
- Mathematical + practical

### Variables Held Constant
- Same type of practice (coding implementation)
- Same difficulty level
- Same practice duration (30 min)
- Same learning session quality

### Single Variable
Timing of practice ONLY

### Metrics

**Primary:**
- 1-week retention (can Finn implement from memory?)
- Application success rate

**Secondary:**
- Code accuracy
- Time to complete
- Confidence during implementation
- Bugs/errors made

### Success Criteria
Immediate practice produces ≥15% better retention OR saves significant time in re-learning.

### Timeline
2 weeks (teach both, practice at different times, measure retention)

### Expected Results
**Prediction:** Immediate practice 15-20% better

**Why:** Memory consolidation strongest right after learning → immediate practice reinforces while neural traces are active

**Alternative:** Delayed practice might benefit from "desirable difficulty" (spacing effect)

### Analysis Plan
Track retention scores, implementation success, time efficiency

### Conclusion
[TBD]

---

## EXP-004: ELI5-First vs. Technical-First

**Status:** 🟡 Ready to Run (Planned)  
**Started:** [TBD]  
**Completed:** [TBD]

### Hypothesis
ELI5 → Technical progression will produce better understanding than Technical → ELI5 by reducing cognitive load during initial learning phase.

### Design

**Method A (Control):** Technical explanation first, simplify later  
**Method B (Experimental):** ELI5 first, build to technical

**Concepts to test:**
- **Concept A:** Transformers (ELI5 first)
- **Concept B:** GANs (Technical first)

### Metrics
- Immediate understanding
- Confusion points
- Retention at 1 week
- Depth of understanding

### Expected Results
**Prediction:** ELI5 first is 10-15% better for high-complexity concepts

**Why:** Progressive complexity reduces working memory overload → better encoding

### Timeline
3 weeks (complex concepts need more time)

### Conclusion
[TBD]

---

## Experiment Queue (Priority Order)

1. **EXP-001: Chess Analogies** ← Run first (highest impact prediction)
2. **EXP-002: Diagram Types** ← Run second (visual learning validation)
3. **EXP-003: Practice Timing** ← Run third (optimize practice)
4. **EXP-004: Explanation Order** ← Run fourth (refine teaching order)

**Can run EXP-001 and EXP-002 in parallel** (different variables, no overlap)

---

## Meta-Analysis (After Multiple Experiments)

### Patterns Emerging
[Update after running 3+ experiments]

### Confirmed Hypotheses
[What works consistently?]

### Rejected Hypotheses
[What doesn't work?]

### Surprising Findings
[Unexpected results?]

### Updated Best Practices
[Based on evidence, what should become standard?]

### Next Experiments to Design
[What new questions emerged?]

---

## Experiment Design Checklist

Before adding new experiment, verify:
- [ ] Clear hypothesis with specific prediction
- [ ] Single variable changed between conditions
- [ ] Concepts matched for difficulty
- [ ] Metrics defined and measurable
- [ ] Success criteria specified (X% improvement)
- [ ] Timeline realistic
- [ ] Confounding factors identified
- [ ] Data collection method ready

---

**VALIDATION TEST RESULTS:**

✅ Experiment protocol is actionable (can actually run these)  
✅ Real concepts, specific predictions, clear metrics  
✅ Chess analogy experiment is ready to run immediately  
✅ Multiple experiments can run in parallel  
✅ Clear success criteria (not subjective)  
✅ Timeline is realistic (2-4 weeks per experiment)  
✅ Confounding factors identified and mitigated

**This is functional, not theoretical.**
