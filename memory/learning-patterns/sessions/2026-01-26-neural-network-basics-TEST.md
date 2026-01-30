# TEST SESSION: Neural Network Basics

**Date:** 2026-01-26  
**Topic:** Basic Neural Network Architecture  
**Context:** MSc AI prep - foundational concept  
**Duration:** 45 minutes  
**Session type:** [X] Mixed approach - visual + interactive

---

## Concept Details

### What was taught?
A neural network is a computational model inspired by biological neurons that learns to map inputs to outputs through weighted connections and activation functions. It consists of layers of nodes (neurons) that process information through forward propagation and learn through backpropagation.

### Why does it matter?
Neural networks are the foundation of modern deep learning. Understanding basic architecture is essential for MSc AI coursework and Finn's work on ML systems like MD-Pilot.

### What problem does it solve?
Learns complex non-linear mappings from data without explicit programming - can recognize patterns in images, text, time series, etc.

---

## Teaching Method Used

### Primary modality:
- [X] Visual (diagram/infographic)
- [X] Interactive (hands-on/coding)
- [ ] Problem-solving (puzzle/challenge)
- [ ] Verbal explanation
- [ ] Reading/textbook
- [X] Mixed approach

### Visual elements used:
- [X] Diagram (type: Network graph)
- [ ] Infographic
- [ ] Flowchart
- [X] Network/graph
- [ ] Matrix/table
- [X] Analogy/metaphor
- [X] Code example
- [ ] None

### Specific visual:
Network diagram showing input layer → hidden layer → output layer with weighted connections. Each neuron visualized as a circle, connections as arrows with weights.

### Analogies used:
- [X] Chess-related: "Like evaluating a chess position - each piece (input) has different importance (weight), combined to give overall position evaluation (output)"
- [ ] Engineering/architecture
- [ ] Physical systems
- [ ] Programming concepts
- [ ] Other

### Practice/application:
- [X] Immediate coding exercise
- [ ] Problem to solve
- [ ] Build small project
- [ ] Debug challenge
- [ ] Thought experiment
- [ ] None

**Practice description:**
Built simple 2-layer neural network in Python/NumPy to classify XOR pattern. Started with random weights, implemented forward pass, observed outputs change as weights adjusted manually.

---

## Immediate Understanding Assessment

### Finn's understanding (1-5):
**Rating: [4]** - Confident understanding, can apply with guidance

### Evidence of understanding:
- [X] Explained concept in own words
- [X] Generated novel examples
- [X] Asked deeper "why/how" questions
- [X] Connected to prior knowledge
- [X] Identified limitations or edge cases
- [X] Successfully applied to practice problem
- [ ] Could teach it back clearly

### Evidence of confusion:
- [ ] Needed re-explanation
- [X] Asked clarifying questions (list below)
- [ ] Struggled with practice problem
- [ ] Verbatim repetition without understanding
- [ ] "I get it" without elaboration
- [ ] Couldn't generate own examples

### Questions Finn asked:
1. "Why do we need non-linear activation functions? Why not just stack linear layers?"
2. "How does the network 'know' which weights to adjust during learning?"
3. "Is this like how I evaluate chess positions - combining multiple factors with different weights?"

### Confusion points:
Initial confusion about why activation functions matter. Cleared up with visual showing how linear stacking still produces linear function.

---

## Connection to Prior Knowledge

### Related concepts Finn already knows:
- Linear regression (from property development background)
- Function composition (programming)
- Weighted scoring (chess position evaluation)

### How this builds on previous learning:
Extends linear models to non-linear through activation functions. Uses familiar programming concepts (functions, loops, matrix operations).

### New mental model created or updated:
"Neural networks as universal function approximators" - can learn any mapping given enough neurons and data.

---

## Retention Plan

### Scheduled reviews:
- [X] 24 hours: Quick recall test
- [X] 1 week: Explain from memory
- [X] 1 month: Apply to new problem

### What to test in retention check:
- [X] Core concept explanation (what is a neural network?)
- [X] Key components (layers, weights, activations)
- [X] Practical application (implement simple network)
- [X] Connection to related concepts (vs linear models)

### Predicted retention difficulty (1-5):
**Prediction: [2]** - Should remember well due to visual + hands-on + chess analogy

---

## Optimization Notes

### What worked well:
- Chess position evaluation analogy resonated strongly
- Network diagram made structure immediately clear
- Hands-on coding cemented understanding
- Incremental complexity (simple first, add depth)

### What didn't work:
- Initial verbal explanation was too abstract
- Should have started with diagram immediately
- Could have used more interactive visualization (watch weights update)

### Try next time:
- Lead with visual diagram first
- Use interactive visualization tool for weight updates
- More chess analogies for other ML concepts

### Method effectiveness hypothesis:
Visual + chess analogy + immediate coding is highly effective for Finn. Combination of all three learning modalities created strong understanding.

---

## Quick Reference

**One-line summary:**  
Layers of weighted connections that transform inputs to outputs through non-linear activations, learning by adjusting weights.

**Key visual/analogy:**  
Network graph with neurons as nodes, weights as edges. "Like chess evaluation - weight different factors to reach decision."

**When to use it:**  
Pattern recognition, classification, regression when relationship is non-linear and complex.

---

## Metadata

**Concept complexity:** [X] Medium  
**Finn's prior familiarity:** [X] Heard of it  
**Practical utility:** [X] High  
**Mathematical intensity:** [X] Medium  
**Abstraction level:** [X] Mixed

---

**VALIDATION TEST RESULTS:**

✅ Template is usable and captures relevant data  
✅ Provides actionable information for retention checks  
✅ Chess analogy section worked perfectly for this concept  
✅ Clear trail for measuring method effectiveness  
⚠️ Could add field for "session energy level" (confounding factor)  
⚠️ Need to link to actual visual files when created
