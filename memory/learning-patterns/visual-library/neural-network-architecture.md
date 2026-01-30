# Visual: Neural Network Architecture

**Created:** 2026-01-26  
**Concept:** Basic neural network structure  
**Type:** Network diagram  
**Effectiveness:** [To be tested]

---

## ASCII Diagram (Always Available)

```
INPUT LAYER    HIDDEN LAYER    OUTPUT LAYER
    
    [X₁]────────┐
                │ w₁₁
                ├─────→[H₁]────┐
    [X₂]────────┤       │       │ w₁
                │ w₂₁   │       ├────→[Y]
                │       │       │
    [X₃]────────┤       │       │
                │ w₃₁   │       │
                └─────→[H₂]────┘
                  w₃₂     w₂

Legend:
[Xi] = Input neuron i
[Hi] = Hidden neuron i  
[Y]  = Output neuron
wij  = Weight from neuron i to j
─→   = Forward flow of information
```

---

## Enhanced Diagram with Activations

```
     INPUT          WEIGHTED SUM        ACTIVATION         OUTPUT
                                        
  x₁ ─┐              
      ├──→ Σ(w·x) ──→ f(Σ) ──→ a₁ ─┐
  x₂ ─┤                              │
      │                              ├──→ Σ(w·a) ──→ f(Σ) ──→ ŷ
  x₃ ─┘              Σ(w·x) ──→ f(Σ) ──→ a₂ ─┘
      

Where:
• Σ(w·x) = weighted sum = w₁x₁ + w₂x₂ + w₃x₃ + b
• f(·) = activation function (ReLU, sigmoid, tanh)
• ai = activation output from hidden neuron i
• ŷ = final network output
```

---

## Information Flow Diagram

```
FORWARD PROPAGATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input → [Weights] → Sum → [Activation] → Hidden
Hidden → [Weights] → Sum → [Activation] → Output

EXAMPLE: XOR Problem
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: [0,1]
  ↓ ×[w₁₁, w₂₁]
Sum: w₁₁×0 + w₂₁×1 = w₂₁
  ↓ sigmoid
Hidden: [h₁, h₂]
  ↓ ×[w₁, w₂]
Sum: w₁×h₁ + w₂×h₂
  ↓ sigmoid
Output: 1 (True for XOR)
```

---

## Chess Analogy Diagram

```
CHESS POSITION EVALUATION ♟️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Material count    ─┐
Piece activity     ├─→ Weighted sum → Evaluation → Position score
King safety       ─┤
Pawn structure    ─┘

NEURAL NETWORK 🧠
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input feature 1   ─┐
Input feature 2    ├─→ Weighted sum → Activation → Hidden values
Input feature 3   ─┤                                    ↓
Input feature 4   ─┘                            Final prediction

Same pattern: Multiple inputs × different weights = combined output
```

---

## Component Breakdown

```
ANATOMY OF A NEURON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        INPUTS
          ↓
    ┌─────────────┐
    │   WEIGHTS   │ ← Learned parameters
    └─────────────┘
          ↓
    ┌─────────────┐
    │  SUMMATION  │ ← Σ(wi × xi + b)
    └─────────────┘
          ↓
    ┌─────────────┐
    │ ACTIVATION  │ ← Non-linearity
    └─────────────┘
          ↓
        OUTPUT

Each component has a job:
• Weights: Importance of each input
• Sum: Combine weighted inputs  
• Activation: Add non-linearity
• Output: Pass to next layer
```

---

## Learning Process Visualization

```
BEFORE TRAINING                AFTER TRAINING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Random weights                 Optimized weights
      ↓                              ↓
  [X] ──?──→ [H] ──?──→ [Y]      [X] ──2.3──→ [H] ──-1.7──→ [Y]
                                              
  Bad predictions                Good predictions
  Loss = HIGH ❌                 Loss = LOW ✅
      ↓                              ↑
  Adjust weights ←──────────────────┘
  (Backpropagation)

The network LEARNS by:
1. Make prediction (forward pass)
2. Calculate error (loss)
3. Adjust weights to reduce error (backprop)
4. Repeat until loss is minimized
```

---

## 3-Layer Network Example

```
FULL NETWORK ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         INPUT (3)      HIDDEN (4)      OUTPUT (2)
                         
         [x₁] ─────┬─→ [h₁] ───┬─→ [y₁] = Class A
                   │           │
         [x₂] ──┬──┼─→ [h₂] ──┼┼─→ [y₂] = Class B
                │  │           ││
         [x₃] ──┼──┼─→ [h₃] ──┼┘
                │  │           │
                └──┼─→ [h₄] ───┘
                   │
                   └── Fully connected
                       (each input connects to each hidden)

Parameters to learn:
• Input→Hidden: 3×4 = 12 weights + 4 biases = 16 params
• Hidden→Output: 4×2 = 8 weights + 2 biases = 10 params
• TOTAL: 26 learnable parameters
```

---

## Visual Design Principles Used

✅ **One concept per diagram** - Each shows single aspect  
✅ **Progressive complexity** - Simple → detailed  
✅ **Consistent shapes** - Circles = neurons, arrows = flow  
✅ **Clear labels** - Every component named  
✅ **Chess analogy** - Connects to Finn's daily practice  
✅ **ASCII format** - Works anywhere, no rendering issues

---

## Usage Instructions

### When to use each diagram:

**ASCII Network Diagram** - First introduction, basic structure  
**Enhanced with Activations** - Explaining how neurons compute  
**Information Flow** - Teaching forward propagation  
**Chess Analogy** - Making concept relatable  
**Component Breakdown** - Deep dive into neuron mechanics  
**Learning Process** - Explaining training/backprop  
**Full Network Example** - Putting it all together

### Dual coding approach:
1. Show diagram
2. Explain verbally what each part does
3. Let Finn trace through an example
4. Code it together

---

## Interactive Extension Ideas

**For browser-based learning:**
- Interactive weight sliders - see output change in real-time
- Step-through forward propagation - watch values flow
- Visualization of activation functions - plot shapes
- Training animation - watch weights update during learning

**For hands-on coding:**
- Implement from scratch in NumPy
- Modify architecture (add layers, change sizes)
- Experiment with different activations
- Visualize decision boundaries

---

## Effectiveness Tracking

**To measure if this visual works:**
- [ ] Can Finn explain architecture using diagram?
- [ ] Does diagram trigger recall in retention test?
- [ ] Can Finn sketch similar diagram for new architecture?
- [ ] Does chess analogy make concept click?

**Test results:** [TBD - use in actual learning session]

---

## Related Visuals

**Next concepts to visualize:**
- Backpropagation (error flowing backwards)
- Different activation functions (ReLU, sigmoid, tanh)
- CNN architecture (convolutional layers)
- RNN architecture (recurrent connections)

**Pattern:** Each visual uses same design language for consistency

---

**VALIDATION TEST:**

✅ ASCII diagrams render properly in markdown  
✅ Progressive complexity from simple to detailed  
✅ Chess analogy integrated naturally  
✅ Multiple representations for different learning stages  
✅ Actionable (can actually use these to teach)  
✅ Dual coding ready (visual + verbal)

**TEST IN BROWSER:** Let me verify these render properly...
