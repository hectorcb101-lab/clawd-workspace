# Diagram Templates & Patterns

**Reusable visual structures for common concept types**

---

## Visual Vocabulary (Use Consistently)

### Shapes & Meanings
- **Circle** ⭕ = Entity, object, node, data point
- **Rectangle** ▭ = Process, operation, function, transformation
- **Diamond** ◇ = Decision, condition, gate, choice point
- **Rounded rectangle** = Module, component, subsystem
- **Cloud** = Abstract concept, external system
- **Cylinder** = Data storage, database
- **Arrow** → = Flow, causation, direction, transformation
- **Dashed line** --- = Optional, weak connection, abstraction layer
- **Double arrow** ⇄ = Bidirectional, feedback loop

### Colors (Semantic Coding)
- **Blue** = Input, data, information
- **Green** = Process, active computation
- **Red** = Output, result, error
- **Yellow** = Decision, condition
- **Gray** = Passive, storage, constant

---

## Template 1: Network / Graph Structure

**Use for:** Neural networks, graph algorithms, relationships, connections

```
    A ——— B
    |  ×  |
    | / \ |
    C ——— D
```

**Components:**
- Nodes (circles) = entities
- Edges (lines) = relationships
- Direction (arrows) = flow/causation
- Weight (line thickness) = strength

**Examples:**
- Neural network layers
- Knowledge graphs
- Social networks
- State machines

**Chess analogy:** Board position with piece relationships

---

## Template 2: Hierarchical Tree

**Use for:** Taxonomies, inheritance, decision trees, decomposition

```
        Root
       / | \
      /  |  \
     A   B   C
    / \ / \
   D  E F  G
```

**Components:**
- Root = highest level concept
- Branches = subcategories, types
- Leaves = specific instances
- Depth = level of abstraction

**Examples:**
- Class hierarchies
- Decision trees
- Concept taxonomies
- File systems

**Chess analogy:** Game tree (opening variations)

---

## Template 3: Sequential Flow / Pipeline

**Use for:** Algorithms, processes, transformations, workflows

```
Input → [Process 1] → [Process 2] → [Process 3] → Output
         ↓ feedback     ↓ side effect
      [Validate]    [Log/Monitor]
```

**Components:**
- Steps (rectangles) = operations
- Arrows = sequence, data flow
- Branches = conditionals
- Loops = iteration

**Examples:**
- Data pipelines
- Training loops
- Algorithm steps
- System workflows

**Chess analogy:** Move sequence in combination

---

## Template 4: Layered Architecture

**Use for:** System architecture, abstraction layers, stacks

```
┌─────────────────────┐
│   Application       │  ← High-level
├─────────────────────┤
│   API / Interface   │
├─────────────────────┤
│   Business Logic    │
├─────────────────────┤
│   Data Layer        │  ← Low-level
└─────────────────────┘
```

**Components:**
- Horizontal layers = abstraction levels
- Vertical = components at same level
- Interfaces = boundaries between layers

**Examples:**
- Software architecture
- Neural network layers
- Protocol stacks
- Abstraction levels

**Chess analogy:** Strategic layers (tactics → strategy → plan)

---

## Template 5: Comparison Matrix

**Use for:** Trade-offs, feature comparison, decision-making

```
         │ Method A │ Method B │ Method C
─────────┼──────────┼──────────┼─────────
Speed    │    ✅    │    ❌    │    ⚠️
Accuracy │    ❌    │    ✅    │    ✅
Memory   │   Low    │   High   │  Medium
```

**Components:**
- Rows = criteria
- Columns = options
- Cells = evaluation
- Symbols = quick assessment

**Examples:**
- Algorithm comparison
- Model selection
- Trade-off analysis
- Feature matrices

**Chess analogy:** Position evaluation (space, material, king safety)

---

## Template 6: State Transition Diagram

**Use for:** States, transitions, FSMs, workflows

```
     start
       ↓
   [State A] ──event1──> [State B]
       ↑                     ↓
       └────event2───────────┘
```

**Components:**
- States (circles/rectangles) = conditions
- Transitions (arrows) = events/triggers
- Labels = conditions for transition

**Examples:**
- Finite state machines
- Process states
- Game states
- Lifecycle diagrams

**Chess analogy:** Game phases (opening → middlegame → endgame)

---

## Template 7: Input-Process-Output (IPO)

**Use for:** Functions, transformations, black-box models

```
┌─────────┐     ┌─────────────┐     ┌────────┐
│  Input  │ ──> │   Process   │ ──> │ Output │
└─────────┘     │ [mechanism] │     └────────┘
                └─────────────┘
```

**Components:**
- Input = what goes in
- Process = transformation
- Output = result
- Optional: internal mechanism

**Examples:**
- Functions
- ML models (data → model → predictions)
- Algorithms
- Systems

**Chess analogy:** Position → thinking → move

---

## Template 8: Feedback Loop

**Use for:** Optimization, training, iterative processes

```
   Input ──> Process ──> Output
     ↑          ↓         ↓
     │      Evaluate   Measure
     │          ↓         ↓
     └────── Adjust ←────┘
```

**Components:**
- Forward path = main process
- Measurement = evaluation
- Feedback = adjustment signal
- Loop = iteration

**Examples:**
- Training loops
- Optimization algorithms
- Control systems
- Iterative refinement

**Chess analogy:** Think → move → evaluate → adjust

---

## Template 9: Venn / Set Relationships

**Use for:** Overlaps, intersections, category relationships

```
     A          B
   ┌───┐      ┌───┐
   │   │      │   │
   │  ┌┴──────┴┐  │
   └──│ A ∩ B  │──┘
      └────────┘
```

**Components:**
- Circles = sets, categories
- Overlap = shared elements
- Outside = unique elements

**Examples:**
- Concept relationships
- Set operations
- Category overlaps
- Skill intersections

**Chess analogy:** Tactical motifs overlapping (fork + pin)

---

## Template 10: Timeline / Sequence

**Use for:** Chronology, events, training progress

```
t₀ ────t₁────t₂────t₃────t₄────>
  │     │     │     │     │
Event  Milestone  Decision  Result
```

**Components:**
- Horizontal axis = time
- Points = events, milestones
- Segments = periods
- Markers = significant moments

**Examples:**
- Training progress
- Algorithm convergence
- Historical development
- Project timeline

**Chess analogy:** Game timeline (opening moves → middlegame → endgame)

---

## Choosing the Right Template

### Ask:
1. **What's the core relationship?**
   - Connection → Network
   - Hierarchy → Tree
   - Sequence → Flow
   - Comparison → Matrix

2. **What's the concept structure?**
   - Parts + whole → Layered architecture
   - States + transitions → State diagram
   - Input + output → IPO
   - Loop → Feedback diagram

3. **What's Finn trying to understand?**
   - Structure → Network / Tree
   - Process → Flow / Pipeline
   - Decision → Matrix / Tree
   - Change → State / Timeline

---

## Combining Templates

**Complex concepts often need multiple views:**

**Example: Neural Network Training**
- Architecture = Layered architecture
- Forward pass = Flow diagram
- Training loop = Feedback loop
- Comparison of architectures = Matrix

**Use multiple simple diagrams > one complex diagram**

---

## Common Mistakes to Avoid

❌ **Too much detail** - cluttered, overwhelming  
✅ **Focus on one concept per diagram**

❌ **Inconsistent notation** - confusing across diagrams  
✅ **Use same shapes for same meanings**

❌ **No labels** - reader has to guess  
✅ **Label everything clearly**

❌ **Decorative elements** - waste cognitive load  
✅ **Every element serves understanding**

❌ **Text-heavy** - defeats purpose of visual  
✅ **Minimal text, maximum structure**

---

## Progressive Detail Pattern

**For complex concepts, show 3 versions:**

### Version 1: Simplest Overview
- Bare minimum structure
- Core relationships only
- One-glance understanding

### Version 2: Standard Detail
- Key components shown
- Main relationships
- Common use case

### Version 3: Complete Picture
- Full detail
- Edge cases
- Advanced understanding

**Start with V1, add complexity only after Finn grasps basics.**

---

## Quick Selection Guide

| Concept Type | Best Template |
|--------------|---------------|
| Neural architecture | Layered + Network |
| Algorithm | Flow + IPO |
| Optimization | Feedback loop |
| Model comparison | Matrix |
| System design | Layered architecture |
| Process workflow | State transition |
| Taxonomy | Tree |
| Relationships | Network |
| Decision logic | Tree + Diamond nodes |
| Time series | Timeline |

---

## Chess-Specific Visual Patterns

### Tactical Pattern Diagrams
```
Before:  [Position A]
         ↓ tactic
After:   [Position B] → advantage
```

### Strategic Map
```
Weakness ──attack──> Target
    ↑                  ↓
    └───── defend ─────┘
```

### Pattern Recognition
```
Pattern X seen in:
├─ Variation A
├─ Variation B
└─ Variation C
```

**Use chess visual thinking for AI concepts when analogies fit.**

---

## Action Items

1. **Before creating any diagram:** Pick the template that fits the concept structure
2. **Use consistent vocabulary:** Same shapes = same meanings across all diagrams
3. **Start simple:** V1 overview before V2 detail
4. **Test understanding:** Can Finn explain the concept using just the diagram?

**Good diagram = Finn can explain concept without words.**

**Great diagram = Finn can teach concept to others using diagram.**
