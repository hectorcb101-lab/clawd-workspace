# Experiment Protocol: Testing Learning Methods

**Purpose:** Systematically test different teaching approaches to discover what works best for Finn.

---

## Experiment Philosophy

**Core principle:** Evidence over assumptions.

We think we know what works (visual, interactive, problem-based). But do we really? Run experiments to find out.

**The scientific approach:**
1. Form hypothesis
2. Design controlled test
3. Collect data
4. Analyze results
5. Update beliefs
6. Iterate

---

## Types of Experiments

### A/B Tests (Most Common)

**Structure:** Teach two similar concepts using different methods, compare outcomes.

**Example:**
- Concept A: Teach with network diagram
- Concept B: Teach with flowchart  
- Measure: Which has better retention at 1 week?

**Strength:** Direct comparison, controlled variables  
**Weakness:** Need similar concepts to test fairly

---

### Longitudinal Tests

**Structure:** Track single concept/method over extended time period.

**Example:**
- Track retention of all concepts taught with chess analogies
- Compare to baseline retention rate
- Measure: Do chess analogies improve long-term retention?

**Strength:** Real-world validity, multiple data points  
**Weakness:** Takes time, many confounding variables

---

### Progressive Refinement

**Structure:** Start with method A, iterate based on results.

**Example:**
- Week 1: ELI5 → technical explanation
- Week 2: Adjust based on what worked
- Week 3: Further refinement
- Measure: Does retention improve over iterations?

**Strength:** Continuous improvement  
**Weakness:** No baseline comparison

---

## Running an A/B Experiment

### 1. Hypothesis Formation

**Template:**
"[Method A] will produce better [outcome metric] than [Method B] for [concept type] because [theoretical reason]."

**Example:**
"Visual network diagrams will produce better 1-week retention than textual explanations for structural AI concepts because Finn is a visual learner and dual coding theory predicts better encoding."

**Key elements:**
- Specific methods to compare
- Clear outcome metric
- Concept type (not all concepts are equal)
- Theoretical justification

---

### 2. Concept Pair Selection

**Requirements:**
- Similar complexity
- Similar abstraction level  
- Similar prior knowledge
- Taught close in time (same week ideally)
- Both relevant to current learning

**Example pairs:**
- CNNs vs. RNNs (both neural architectures)
- Gradient descent vs. Adam optimizer (both optimization)
- Supervised vs. Unsupervised learning (both paradigms)

**Avoid:**
- Vastly different complexity (unfair comparison)
- One familiar, one novel (confounding variable)
- Different domains (too many variables)

---

### 3. Method Specification

**Control method (baseline):**
[Current standard approach]

**Experimental method (new approach):**
[What you're testing]

**Variables to keep constant:**
- Session duration
- Time of day
- Finn's energy level
- Prior context
- Follow-up practice amount

**Single variable change:**
[ONLY change one thing between conditions]

---

### 4. Metrics Definition

**Primary metric:**
[Main outcome you care about]

**Examples:**
- Retention score at 1 week (1-5 scale)
- Application success rate (% problems solved)
- Time to mastery (sessions needed)
- Confidence rating (1-5 scale)

**Secondary metrics:**
[Additional data points]

**Examples:**
- Immediate understanding (1-5)
- Questions asked during learning
- Time to complete practice
- Self-reported preference

**Success criteria:**
[What result would confirm hypothesis?]

"Method A produces ≥10% higher retention score than Method B"

---

### 5. Data Collection

**During learning session:**

Track in `concept-capture.md`:
- Immediate understanding (1-5)
- Questions asked
- Confusion points
- Time spent
- Finn's engagement

**Retention checks:**

Use `retention-check.md`:
- 24 hours: Quick recall
- 1 week: Explain from memory
- 1 month: Apply to new problem

**Application tests:**

New problems using each concept:
- Success rate
- Time to solve
- Hint usage

---

### 6. Analysis

**Quantitative comparison:**

| Metric | Method A | Method B | Difference |
|--------|----------|----------|------------|
| Immediate understanding | 4.2 | 3.8 | +0.4 (A better) |
| 24h retention | 4.5 | 4.0 | +0.5 (A better) |
| 1 week retention | 4.0 | 3.2 | +0.8 (A better) |
| Application success | 85% | 70% | +15% (A better) |

**Qualitative observations:**
- What did Finn say about each method?
- Which felt more natural?
- Which generated better questions?

**Confounding factors:**
- Was Finn more tired for one session?
- Was one concept actually harder?
- Did external factors interfere?

---

### 7. Conclusion

**Result:**
- [ ] Hypothesis confirmed - Method A clearly better
- [ ] Hypothesis partially confirmed - Method A slightly better
- [ ] No significant difference
- [ ] Hypothesis rejected - Method B actually better
- [ ] Inconclusive - need more data

**Confidence level:**
- [ ] High - clear, consistent results
- [ ] Medium - some evidence but not overwhelming
- [ ] Low - noisy data, uncertain

**Action:**
- [ ] Adopt Method A as standard
- [ ] Use Method A for specific concept types only
- [ ] Continue using current method
- [ ] Run follow-up experiment
- [ ] Try different approach entirely

---

### 8. Update Learning Profile

**Add to `finn-profile.md`:**
- What worked
- What didn't
- When to use each method
- Updated best practices

**Share insights:**
- Update templates with learnings
- Refine future experiments based on results

---

## Active Experiments Template

### Experiment ID: EXP-001

**Date started:** YYYY-MM-DD  
**Status:** [ ] Planning [ ] Running [ ] Analyzing [ ] Complete

**Hypothesis:**

**Method A (Control):**

**Method B (Experimental):**

**Concepts tested:**
- Concept A: __________
- Concept B: __________

**Primary metric:**

**Results:**
- Method A: __________
- Method B: __________
- Winner: __________

**Conclusion:**

**Actions taken:**

---

## Priority Experiments (Run These First)

### Experiment 1: Diagram Types

**Hypothesis:** Network diagrams > flowcharts for structural concepts

**Methods:**
- A: Network diagram (nodes + edges)
- B: Flowchart (boxes + arrows)

**Concepts:** CNNs vs. RNNs (both neural architectures)

**Measure:** 1-week retention, application success

**Timeline:** 2 weeks

**Rationale:** Finn plays chess (network thinking), might prefer network representations

---

### Experiment 2: Chess Analogies

**Hypothesis:** Chess metaphors improve understanding for tactical concepts

**Methods:**
- A: Chess analogy included
- B: No chess reference

**Concepts:** Greedy algorithms vs. Dynamic programming (both optimization strategies)

**Measure:** Understanding depth, retention, transfer to new problems

**Timeline:** 1 month

**Rationale:** Daily chess practice → strong chess mental models → might transfer well

---

### Experiment 3: Practice Timing

**Hypothesis:** Immediate practice > 24h delayed practice

**Methods:**
- A: Practice right after learning
- B: Practice 24 hours later

**Concepts:** Backpropagation vs. Gradient descent variants

**Measure:** Retention at 1 week, application confidence

**Timeline:** 2 weeks

**Rationale:** Immediate consolidation might strengthen memory

---

### Experiment 4: Explanation Order

**Hypothesis:** ELI5 → technical > technical → ELI5

**Methods:**
- A: Simple first, build to complex
- B: Technical first, simplify later

**Concepts:** Transformers vs. GANs (both complex architectures)

**Measure:** Immediate understanding, retention at 1 week

**Timeline:** 2 weeks

**Rationale:** Progressive complexity might reduce cognitive load

---

### Experiment 5: Problem-First vs. Theory-First

**Hypothesis:** Problem → concept > concept → problem

**Methods:**
- A: Present problem, struggle, then teach
- B: Teach concept, then apply to problem

**Concepts:** Overfitting solutions vs. Regularization techniques

**Measure:** Understanding depth, ability to identify in wild

**Timeline:** 3 weeks

**Rationale:** Finn is problem-solving oriented, might learn better through challenge

---

## Experiment Log File

**Track all experiments in:** `memory/learning-patterns/experiments/experiment-log.md`

**Format:**
```markdown
## EXP-001: Diagram Types
**Status:** Complete
**Hypothesis:** Network diagrams > flowcharts
**Result:** ✅ Confirmed - network diagrams showed 25% better retention
**Action:** Use network diagrams as default for structural concepts
**Notes:** Finn said "networks make more sense to me, like chess positions"

## EXP-002: Chess Analogies  
**Status:** Running
**Hypothesis:** Chess metaphors improve understanding
**Result:** [TBD]
**Action:** [TBD]
**Notes:** [In progress]
```

---

## Experiment Design Checklist

Before running any experiment:

- [ ] Clear hypothesis stated
- [ ] Single variable changed between conditions
- [ ] Concepts similar in complexity
- [ ] Metrics defined and measurable
- [ ] Success criteria specified
- [ ] Timeline realistic
- [ ] Data collection method ready
- [ ] Confounding factors identified
- [ ] Control and experimental methods documented

---

## Common Pitfalls to Avoid

### ❌ Too many variables

**Wrong:** Test visual + chess analogy + immediate practice vs. text + no analogy + delayed practice

**Right:** Test visual vs. text, keeping everything else constant

---

### ❌ Biased concept selection

**Wrong:** Test new method on easy concept, control on hard concept

**Right:** Match concept difficulty carefully

---

### ❌ No baseline

**Wrong:** "Let's try this new method!" [no comparison]

**Right:** Always compare to current standard

---

### ❌ Stopping too early

**Wrong:** "Method A worked once, let's use it forever!"

**Right:** Test multiple times, look for patterns

---

### ❌ Ignoring confounding factors

**Wrong:** Finn was exhausted for Method B session → Method A wins

**Right:** Note confounds, retest if suspicious

---

## Long-Term Experiment Strategy

### Phase 1: Test high-impact variables (Months 1-2)
- Diagram types
- Chess analogies
- Practice timing

### Phase 2: Optimize winners (Months 3-4)
- Fine-tune successful methods
- Test combinations
- Establish best practices

### Phase 3: Edge cases (Months 5-6)
- Special concept types
- Advanced techniques
- Personalization refinement

### Phase 4: Maintenance (Ongoing)
- Validate assumptions periodically
- Test new ideas as they arise
- Keep system adaptive

---

## Meta-Learning: Learning About Learning

**The ultimate goal:** Not just find what works, but understand WHY it works.

**Build theory:**
- What patterns emerge across experiments?
- Can we predict what will work for new concepts?
- How does Finn's learning evolve over time?

**Refine continuously:**
- Update profile based on evidence
- Adapt methods as Finn develops expertise
- Build toward Finn's meta-cognitive awareness

---

**Remember: This is science. Collect data. Test hypotheses. Update beliefs. Optimize continuously.**

**The meta-learning system that doesn't experiment is just a static template. This one evolves.**
