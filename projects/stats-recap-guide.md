# Week 6 Stats Recap Quiz — Complete Answer Guide
## Step-by-Step Solutions for All 18 Formula Slides

**Purpose:** This guide provides everything you need to confidently answer "Do you know what this formula means?" for every formula in the Week 6 recap quiz.

**Study Strategy:**
1. Read each section thoroughly
2. Cover the worked example and try it yourself
3. Review the common pitfalls
4. Test yourself: can you explain the formula in plain English without looking?

---

## Formula 1: Mean (μ = (1/n) Σxᵢ)

### Name
**Arithmetic Mean** (Average)

### Plain English Explanation
The mean is the "center of gravity" of your data. It tells you what value you'd get if you distributed all your data equally across every observation.

**When to use it:**
- When you want a single number that represents the "typical" value
- When your data doesn't have extreme outliers that would skew it
- As the foundation for calculating variance and standard deviation

### Worked Numerical Example

**Question:** Five students scored the following marks on a test: 65, 72, 68, 81, 74. What is the mean score?

**Step-by-step solution:**

```
Given data: {65, 72, 68, 81, 74}
n = 5 (number of values)

μ = (1/n) Σxᵢ
  = (1/5) × (65 + 72 + 68 + 81 + 74)
  = (1/5) × 360
  = 72

Answer: The mean score is 72 marks.
```

**Interpretation:** The average student scored 72 on this test. Notice that not every student scored exactly 72 — the mean represents the balance point of all scores.

### Common Exam Pitfalls

❌ **TRAP 1:** Forgetting to divide by n
- Wrong: 65 + 72 + 68 + 81 + 74 = 360 ✗
- Right: 360 ÷ 5 = 72 ✓

❌ **TRAP 2:** Using mean with extreme outliers
- Data: {10, 12, 11, 13, 95}
- Mean = 28.2 (misleading! Most values are around 10-13)
- Better to use median (12) when outliers present

❌ **TRAP 3:** Confusing μ (population mean) with x̄ (sample mean)
- They use the same formula, but notation matters in exams
- μ when talking about the entire population
- x̄ when talking about a sample from the population

---

## Formula 2: Variance (σ² = (1/n) Σ(xᵢ − μ)²)

### Name
**Population Variance**

### Plain English Explanation
Variance measures how "spread out" your data is from the mean. It's the average of squared distances from the mean. We square the distances so positive and negative deviations don't cancel out.

**When to use it:**
- When you need to quantify how much variability exists in your data
- Before calculating standard deviation (σ = √variance)
- In statistical tests and machine learning algorithms
- When comparing the spread of different datasets

### Worked Numerical Example

**Question:** Calculate the variance of the test scores: {65, 72, 68, 81, 74}

**Step-by-step solution:**

```
Step 1: Calculate the mean (from Formula 1)
μ = 72

Step 2: Calculate each deviation from the mean
x₁ − μ = 65 − 72 = −7
x₂ − μ = 72 − 72 =  0
x₃ − μ = 68 − 72 = −4
x₄ − μ = 81 − 72 =  9
x₅ − μ = 74 − 72 =  2

Step 3: Square each deviation
(x₁ − μ)² = (−7)² = 49
(x₂ − μ)² = (0)²  = 0
(x₃ − μ)² = (−4)² = 16
(x₄ − μ)² = (9)²  = 81
(x₅ − μ)² = (2)²  = 4

Step 4: Sum the squared deviations
Σ(xᵢ − μ)² = 49 + 0 + 16 + 81 + 4 = 150

Step 5: Divide by n
σ² = (1/5) × 150 = 30

Answer: The variance is 30 (squared marks).
```

### Common Exam Pitfalls

❌ **TRAP 1:** Using n−1 instead of n for population variance
- **Population variance:** divide by n (σ²)
- **Sample variance:** divide by n−1 (s²)
- If the question says "sample variance," use n−1!

❌ **TRAP 2:** Forgetting to square the deviations
- Wrong: σ² = (1/n) Σ(xᵢ − μ) — this gives zero!
- Right: σ² = (1/n) Σ(xᵢ − μ)²

❌ **TRAP 3:** Taking the square root too early
- Variance is σ², not σ
- If they ask for variance, stop here — don't take the square root

❌ **TRAP 4:** Rounding the mean before calculating deviations
- Use the exact mean value (72, not 72.0 rounded)
- Rounding errors compound when squaring

---

## Formula 3: Standard Deviation (σ = √[(1/n) Σ(xᵢ − μ)²])

### Name
**Population Standard Deviation**

### Plain English Explanation
Standard deviation is the square root of variance. It measures spread in the **same units** as your original data, making it easier to interpret than variance.

**When to use it:**
- When you want to describe spread in the original units (marks, not squared marks)
- To understand how far "typical" values are from the mean
- With normal distributions (68-95-99.7 rule: 68% of data within 1σ of μ)
- When comparing variability across different datasets

### Worked Numerical Example

**Question:** Calculate the standard deviation of the test scores: {65, 72, 68, 81, 74}

**Step-by-step solution:**

```
Step 1: Calculate the variance (from Formula 2)
σ² = 30

Step 2: Take the square root
σ = √σ²
  = √30
  = 5.477 marks (rounded to 3 decimal places)

Answer: The standard deviation is approximately 5.48 marks.
```

**Interpretation:** On average, student scores deviate from the mean (72) by about 5.5 marks. Most scores fall within the range 72 ± 5.5, or roughly 66.5 to 77.5.

### Common Exam Pitfalls

❌ **TRAP 1:** Confusing variance and standard deviation
- Variance = σ² = 30 (units: marks²)
- Standard deviation = σ = 5.48 (units: marks)
- Read the question carefully to see which they want!

❌ **TRAP 2:** Forgetting to take the square root
- If they ask for standard deviation, you MUST take √

❌ **TRAP 3:** Units confusion
- Variance: squared units (marks², cm², etc.)
- Standard deviation: original units (marks, cm, etc.)

❌ **TRAP 4:** Negative standard deviation
- σ is ALWAYS ≥ 0 (it's a distance measure)
- If you get negative, you made a calculation error

---

## Formula 4: Dot Product (x⊤w)

### Name
**Dot Product** (Scalar Product, Inner Product)

### Plain English Explanation
The dot product takes two vectors and produces a single number (scalar). You multiply corresponding elements and add them all up. It's fundamental in machine learning, especially in linear models.

**When to use it:**
- Linear regression predictions: ŷ = w⊤x
- Neural network forward pass
- Calculating similarity between vectors (larger dot product = more aligned)
- Computing weighted sums

### Worked Numerical Example

**Question:** Calculate the dot product of x = [2, −1, 3, 0] and w = [0.5, 1, −2, 4]

**Step-by-step solution:**

```
Given:
x = [2, −1, 3, 0]
w = [0.5, 1, −2, 4]

x⊤w = x₁w₁ + x₂w₂ + x₃w₃ + x₄w₄

Step-by-step multiplication:
Element 1: 2 × 0.5  =  1.0
Element 2: (−1) × 1 = −1.0
Element 3: 3 × (−2) = −6.0
Element 4: 0 × 4    =  0.0

Sum all products:
x⊤w = 1.0 + (−1.0) + (−6.0) + 0.0
    = 1.0 − 1.0 − 6.0
    = −6.0

Answer: x⊤w = −6
```

**Real-world interpretation:** If w represents weights in a linear model and x represents features, the prediction would be −6.

### Common Exam Pitfalls

❌ **TRAP 1:** Dimensions must match
- Can't compute dot product if vectors have different lengths
- [1,2,3]⊤[4,5] → ERROR (3 ≠ 2)

❌ **TRAP 2:** Result is a scalar, not a vector
- Wrong: x⊤w = [1, −1, −6, 0]
- Right: x⊤w = −6 (single number!)

❌ **TRAP 3:** Sign errors with negative numbers
- (−1) × 1 = −1 (not +1)
- 3 × (−2) = −6 (not +6)
- Double-check your signs!

❌ **TRAP 4:** Forgetting that dot product is commutative
- x⊤w = w⊤x (order doesn't matter)
- But notation matters: x⊤w means "x transpose times w"

---

## Formula 5: Matrix Equation (y = Xw)

### Name
**Linear Model Matrix Equation**

### Plain English Explanation
This is how we write linear regression (and many ML models) in compact matrix form. X is your data matrix (rows = samples, columns = features), w is your weight vector, and y is your predictions.

**When to use it:**
- Linear regression: predicting house prices, sales, etc.
- Neural networks (layers are matrix multiplications)
- Any model that's a linear combination of inputs
- Efficiently computing predictions for many samples at once

### Worked Numerical Example

**Question:** We have 3 houses with features [size, bedrooms] and weights w = [100, 5000] (price per sqm and price per bedroom). Predict prices using y = Xw.

**Step-by-step solution:**

```
Given:
Houses (rows = houses, columns = features):
        Size  Bedrooms
House 1:  80     2
House 2: 120     3
House 3:  60     1

X = ⎡ 80   2 ⎤
    ⎢120   3 ⎥
    ⎣ 60   1 ⎦   (3×2 matrix)

w = ⎡100  ⎤
    ⎣5000 ⎦   (2×1 vector)

Compute y = Xw:

House 1: y₁ = 80×100 + 2×5000 = 8000 + 10000 = 18,000
House 2: y₂ = 120×100 + 3×5000 = 12000 + 15000 = 27,000
House 3: y₃ = 60×100 + 1×5000 = 6000 + 5000 = 11,000

y = ⎡18000⎤
    ⎢27000⎥
    ⎣11000⎦

Answer: Predicted prices are £18k, £27k, and £11k respectively.
```

**Interpretation:** Each row of X is a house. The matrix multiplication efficiently computes predictions for all houses simultaneously.

### Common Exam Pitfalls

❌ **TRAP 1:** Dimension mismatch
- (m×n) matrix × (n×1) vector → (m×1) result
- If X is (3×2) and w is (2×1), result is (3×1) ✓
- If dimensions don't line up, can't multiply!

❌ **TRAP 2:** Wrong multiplication order
- y = Xw ✓ (data matrix first, weights second)
- y = wX ✗ (dimensions won't work)

❌ **TRAP 3:** Confusing rows and columns
- Rows of X = individual samples (houses, people, etc.)
- Columns of X = features (size, age, etc.)
- w = weights (one per feature)

❌ **TRAP 4:** Forgetting this is just multiple dot products
- Each element yᵢ = (row i of X) · w
- It's just Formula 4 repeated for each row!

---

## Formula 6: Pseudo-inverse ((X⊤X)⁻¹X⊤)

### Name
**Moore-Penrose Pseudo-inverse** (Least Squares Solution)

### Plain English Explanation
This formula gives you the "best fit" weights for linear regression. It minimizes the sum of squared errors between predictions and actual values. It's called "pseudo-inverse" because most data matrices X aren't square, so we can't directly invert them.

**When to use it:**
- Finding the optimal weights ŵ in linear regression: ŵ = (X⊤X)⁻¹X⊤y
- Solving overdetermined systems (more equations than unknowns)
- Machine learning model training (least squares method)

### Worked Numerical Example

**Question:** Find the least squares solution for predicting y from x using data: (x,y) = {(1,2), (2,3), (3,5)}

**Step-by-step solution:**

```
Set up the problem y = Xw where X includes intercept column:

X = ⎡1  1⎤     y = ⎡2⎤
    ⎢1  2⎥         ⎢3⎥
    ⎣1  3⎦         ⎣5⎦

Step 1: Calculate X⊤
X⊤ = ⎡1  1  1⎤
     ⎣1  2  3⎦

Step 2: Calculate X⊤X
X⊤X = ⎡1  1  1⎤ ⎡1  1⎤   ⎡3   6⎤
      ⎣1  2  3⎦ ⎢1  2⎥ = ⎣6  14⎦
                 ⎣1  3⎦

Step 3: Calculate (X⊤X)⁻¹
Determinant: det = 3×14 − 6×6 = 42 − 36 = 6

(X⊤X)⁻¹ = (1/6) ⎡ 14  −6⎤ = ⎡ 7/3  −1⎤
                ⎣ −6   3⎦   ⎣−1   1/2⎦

Step 4: Calculate X⊤y
X⊤y = ⎡1  1  1⎤ ⎡2⎤   ⎡10⎤
      ⎣1  2  3⎦ ⎢3⎥ = ⎣23⎦
                 ⎣5⎦

Step 5: Calculate ŵ = (X⊤X)⁻¹X⊤y
ŵ = ⎡ 7/3  −1⎤ ⎡10⎤   ⎡70/3 − 23  ⎤   ⎡1/3⎤
    ⎣−1   1/2⎦ ⎣23⎦ = ⎣−10 + 23/2⎦ = ⎣3/2⎦

Answer: ŵ = [1/3, 3/2]⊤, so y = 1/3 + (3/2)x
         (intercept = 0.33, slope = 1.5)
```

### Common Exam Pitfalls

❌ **TRAP 1:** Order of operations matters
- Must compute (X⊤X)⁻¹ FIRST, then multiply by X⊤
- Can't compute X⊤X⁻¹ (X⊤ isn't square, can't invert it alone!)

❌ **TRAP 2:** Forgetting to transpose X first
- Wrong: (XX⊤)⁻¹X⊤
- Right: (X⊤X)⁻¹X⊤

❌ **TRAP 3:** Matrix dimensions
- If X is (n×p), then X⊤X is (p×p) — small and square
- XX⊤ would be (n×n) — potentially huge!

❌ **TRAP 4:** Singular matrices
- If (X⊤X) is singular (determinant = 0), can't invert
- Happens when columns of X are linearly dependent
- Exam usually gives you invertible matrices

---

## Formula 7: Step Function (f(x) = 1 if x≥0, 0 otherwise)

### Name
**Heaviside Step Function** (Threshold Function, Unit Step)

### Plain English Explanation
This function outputs 1 if the input is positive or zero, and 0 if the input is negative. It's a simple binary classifier: above threshold → activate (1), below threshold → don't activate (0).

**When to use it:**
- Binary classification (yes/no decisions)
- Perceptron algorithm (early neural network)
- Converting continuous values to binary outputs
- Decision boundaries in machine learning

### Worked Numerical Example

**Question:** Apply the step function f(x) = 1 if x≥0, 0 otherwise to the following values: [−2, 0, 1.5, −0.1, 3]

**Step-by-step solution:**

```
f(x) = 1 if x ≥ 0
       0 if x < 0

Evaluate each input:

x = −2:   −2 < 0   →   f(−2) = 0
x = 0:     0 ≥ 0   →   f(0) = 1     (note: threshold INCLUDES zero)
x = 1.5:   1.5 ≥ 0 →   f(1.5) = 1
x = −0.1:  −0.1 < 0 →  f(−0.1) = 0
x = 3:     3 ≥ 0   →   f(3) = 1

Answer: f([−2, 0, 1.5, −0.1, 3]) = [0, 1, 1, 0, 1]
```

**Real-world example:** Email spam classifier
- Calculate score: score = w⊤x = 0.3 (positive)
- Apply step: f(0.3) = 1 → "This is spam"
- If score was −0.5, f(−0.5) = 0 → "Not spam"

### Common Exam Pitfalls

❌ **TRAP 1:** The threshold value x=0
- f(0) = 1 (NOT 0!)
- The condition is x ≥ 0, which INCLUDES zero
- Sometimes written as "x > 0" (different function!)

❌ **TRAP 2:** Not a smooth function
- Step function has a discontinuous jump at x=0
- Can't take the derivative at x=0 (not differentiable there)
- This is why modern neural networks use smooth activations (sigmoid, ReLU)

❌ **TRAP 3:** Output is always 0 or 1
- Never outputs 0.5, 2, or any other value
- Strictly binary output

❌ **TRAP 4:** Threshold can be shifted
- f(x) = 1 if x≥θ, 0 otherwise (threshold at θ, not 0)
- f(x−5) shifts the threshold to x=5

---

## Formula 8: Linear Function (f(Age, Height) = 1 + 2×Age − 3×Height)

### Name
**Multi-variate Linear Function** (Linear Predictor)

### Plain English Explanation
This is a concrete example of a linear function with two input features (Age and Height) and three parameters (intercept=1, weight for Age=2, weight for Height=−3). It's the core of linear regression and many ML models.

**When to use it:**
- Predicting outcomes from multiple features
- Understanding how different variables contribute to a result
- Linear regression, logistic regression, SVMs
- Any additive model where effects combine linearly

### Worked Numerical Example

**Question:** Predict the outcome for a person who is 30 years old and 180 cm tall using f(Age, Height) = 1 + 2×Age − 3×Height

**Step-by-step solution:**

```
Given:
Age = 30 years
Height = 180 cm
f(Age, Height) = 1 + 2×Age − 3×Height

Step 1: Substitute the values
f(30, 180) = 1 + 2×(30) − 3×(180)

Step 2: Multiply the coefficients
= 1 + 60 − 540

Step 3: Add/subtract from left to right
= 61 − 540
= −479

Answer: f(30, 180) = −479
```

**Interpretation:** 
- The intercept (1) is the baseline
- Each year of age ADDS 2 to the output
- Each cm of height SUBTRACTS 3 from the output
- Negative coefficient for Height means taller → lower output

**Alternative calculation (vector form):**
```
w = [1, 2, −3]⊤ (weights: intercept, age, height)
x = [1, 30, 180]⊤ (include 1 for intercept)
f = w⊤x = 1×1 + 2×30 + (−3)×180 = −479
```

### Common Exam Pitfalls

❌ **TRAP 1:** Sign errors with negative coefficients
- Coefficient is −3, not +3
- −3 × 180 = −540 (makes the total MORE negative)

❌ **TRAP 2:** Order of operations
- Multiply BEFORE adding/subtracting
- 2×30 = 60 first, THEN add to 1

❌ **TRAP 3:** Units matter
- Age must be in years, Height in cm (or whatever units the model was trained on)
- Using Age=30 months instead of 30 years gives wrong answer

❌ **TRAP 4:** Interpreting coefficients
- Positive coefficient → feature increases output
- Negative coefficient → feature decreases output
- Magnitude shows importance (−3 has larger effect than +2)

---

## Formula 9: Function Mapping (f: ℝ³ → ℝ)

### Name
**Function Type Notation** (Domain and Codomain)

### Plain English Explanation
This notation describes what kind of inputs and outputs a function has. f: ℝ³ → ℝ means "f takes a 3-dimensional real vector as input and produces a single real number as output."

**When to use it:**
- Specifying machine learning model architectures
- Understanding dimensionality of inputs and outputs
- Mathematical proofs and formal definitions
- Checking if functions can be composed (output of one = input of next)

### Worked Numerical Example

**Question:** Identify the domain and codomain of these functions:
a) f(x,y,z) = x² + 2y − z (input: 3 numbers, output: 1 number)
b) g(x,y) = [x+y, x−y, xy] (input: 2 numbers, output: 3 numbers)

**Step-by-step solution:**

```
Function a: f(x,y,z) = x² + 2y − z

Input: (x, y, z) — 3 real numbers — lives in ℝ³
Output: one real number — lives in ℝ

Notation: f: ℝ³ → ℝ

Example evaluation:
f(1, 2, 3) = 1² + 2(2) − 3 = 1 + 4 − 3 = 2

---

Function b: g(x,y) = [x+y, x−y, xy]

Input: (x, y) — 2 real numbers — lives in ℝ²
Output: 3 real numbers — lives in ℝ³

Notation: g: ℝ² → ℝ³

Example evaluation:
g(3, 2) = [3+2, 3−2, 3×2] = [5, 1, 6]
```

**Understanding the notation:**
- **ℝⁿ** = n-dimensional real space (all possible n-tuples of real numbers)
- **ℝ³** = 3D space: (x, y, z)
- **ℝ** = 1D space: just a single number
- **→** = "maps to" (input type → output type)

### Common Exam Pitfalls

❌ **TRAP 1:** Confusing dimension of input vs output
- f: ℝ³ → ℝ — input is 3D, output is 1D
- NOT the other way around!

❌ **TRAP 2:** Counting dimensions wrong
- f(x, y, z, w) requires ℝ⁴ (4 inputs)
- Output [a, b] is ℝ² (2 outputs)

❌ **TRAP 3:** ℝ vs ℝⁿ notation
- ℝ = single real number (scalar)
- ℝ¹ = same thing (1-dimensional)
- ℝⁿ for n>1 = vector/tuple

❌ **TRAP 4:** Composing functions requires matching types
- If f: ℝ³ → ℝ² and g: ℝ² → ℝ
- Can compute g(f(x)) because output of f matches input of g ✓
- Can't compute f(g(x)) because output of g (1D) doesn't match input of f (3D) ✗

---

## Formula 10: Addition Rule (P(A∪B) = P(A) + P(B) − P(A∩B))

### Name
**Addition Rule of Probability** (Inclusion-Exclusion Principle)

### Plain English Explanation
The probability of "A or B" equals the probability of A plus the probability of B, minus the overlap (A and B both happening). We subtract the overlap because we counted it twice when we added P(A) and P(B).

**When to use it:**
- Finding probability of at least one event occurring
- Working with Venn diagrams
- When events can overlap (not mutually exclusive)
- Combining probabilities in complex scenarios

### Worked Numerical Example

**Question:** A deck of 52 cards has 26 red cards and 4 aces (2 red aces). If you draw one card, what's the probability it's red OR an ace?

**Step-by-step solution:**

```
Define events:
A = card is red
B = card is an ace

Step 1: Calculate P(A)
P(A) = 26/52 = 1/2 = 0.5

Step 2: Calculate P(B)
P(B) = 4/52 = 1/13 ≈ 0.077

Step 3: Calculate P(A∩B) — cards that are BOTH red AND ace
Red aces = 2 (ace of hearts, ace of diamonds)
P(A∩B) = 2/52 = 1/26 ≈ 0.038

Step 4: Apply the addition rule
P(A∪B) = P(A) + P(B) − P(A∩B)
       = 26/52 + 4/52 − 2/52
       = (26 + 4 − 2)/52
       = 28/52
       = 7/13
       ≈ 0.538

Answer: P(red or ace) = 7/13 ≈ 53.8%
```

**Why we subtract P(A∩B):**
```
When we add P(A) + P(B):
- P(A) counts all 26 red cards (including 2 red aces)
- P(B) counts all 4 aces (including 2 red aces)
- Red aces were counted TWICE!
- Subtract P(A∩B) once to correct the double-counting
```

**Special case — Mutually Exclusive Events:**
If A and B can't both happen (mutually exclusive), then P(A∩B) = 0
→ P(A∪B) = P(A) + P(B) (simplified formula)

Example: P(roll a 2 or roll a 5 on die) = 1/6 + 1/6 = 2/6 = 1/3

### Common Exam Pitfalls

❌ **TRAP 1:** Forgetting to subtract the overlap
- Wrong: P(A∪B) = P(A) + P(B) = 26/52 + 4/52 = 30/52 ✗
- Right: P(A∪B) = 26/52 + 4/52 − 2/52 = 28/52 ✓
- The 2 red aces were counted twice!

❌ **TRAP 2:** Using addition rule when events are mutually exclusive
- If events can't both happen, P(A∩B) = 0
- Formula still works, but simplifies to P(A∪B) = P(A) + P(B)

❌ **TRAP 3:** Confusing ∪ (OR) with ∩ (AND)
- P(A∪B) = "A or B or both" — use addition rule
- P(A∩B) = "A and B both" — different formula (often multiply if independent)

❌ **TRAP 4:** P(A∪B) > 1 is impossible!
- If your answer > 1, you forgot to subtract the overlap
- Probabilities must be between 0 and 1

---

## Formula 11: Bayes' Theorem (P(A|B) = P(B|A)P(A)/P(B))

### Name
**Bayes' Theorem** (Bayes' Rule)

### Plain English Explanation
Bayes' theorem lets you "flip" conditional probabilities. If you know P(B|A) and want to find P(A|B), Bayes gives you the formula. It's crucial for updating beliefs based on new evidence.

**When to use it:**
- Medical testing: P(disease|positive test)
- Spam filtering: P(spam|word appears)
- Machine learning: Bayesian inference
- Any time you need to reverse a conditional probability

### Worked Numerical Example

**Question:** A disease affects 1% of the population. A test for the disease is 95% accurate (correctly identifies 95% of sick people) and has a 10% false positive rate (incorrectly says 10% of healthy people are sick). If you test positive, what's the probability you actually have the disease?

**Step-by-step solution:**

```
Define events:
D = has disease
T = tests positive

Given information:
P(D) = 0.01 (1% have disease)
P(D') = 0.99 (99% don't have disease)
P(T|D) = 0.95 (test catches 95% of sick people)
P(T|D') = 0.10 (test wrongly flags 10% of healthy people)

Want to find: P(D|T) = ?

Step 1: Write Bayes' theorem
P(D|T) = P(T|D) × P(D) / P(T)

Step 2: Calculate P(T) using law of total probability
P(T) = P(T|D)P(D) + P(T|D')P(D')
     = (0.95)(0.01) + (0.10)(0.99)
     = 0.0095 + 0.099
     = 0.1085

Step 3: Apply Bayes' theorem
P(D|T) = P(T|D) × P(D) / P(T)
       = (0.95)(0.01) / 0.1085
       = 0.0095 / 0.1085
       = 0.0876
       ≈ 8.76%

Answer: Even with a positive test, there's only an 8.76% chance you have the disease!
```

**Why this makes sense:**
- Disease is rare (1%)
- Test has 10% false positive rate
- For every 1 truly sick person who tests positive, there are ~11 healthy people who falsely test positive
- Most positive tests are false alarms!

### Common Exam Pitfalls

❌ **TRAP 1:** Confusing P(A|B) with P(B|A)
- P(T|D) = 0.95 (probability of positive test GIVEN disease)
- P(D|T) = 0.0876 (probability of disease GIVEN positive test)
- These are DIFFERENT! Don't mix them up.

❌ **TRAP 2:** Forgetting to calculate P(B)
- Need P(T) in denominator
- Use total probability: P(T) = P(T|D)P(D) + P(T|D')P(D')

❌ **TRAP 3:** Ignoring base rates
- If disease is rare (small P(D)), even a good test gives low P(D|T)
- This is the "false positive paradox"

❌ **TRAP 4:** Sign/arithmetic errors
- Carefully substitute values
- Check: final probability must be between 0 and 1

---

## Formula 12: Standard Normal Distribution (X ~ N(0,1))

### Name
**Standard Normal Distribution** (Z-distribution)

### Plain English Explanation
X ~ N(0,1) means "X follows a normal (bell curve) distribution with mean 0 and variance 1." It's the standardized version of any normal distribution — the reference distribution for Z-scores.

**When to use it:**
- Converting any normal distribution to standard form (Z-scores)
- Looking up probabilities in Z-tables
- Comparing values from different normal distributions
- Statistical hypothesis testing

### Worked Numerical Example

**Question:** IQ scores are normally distributed with mean 100 and standard deviation 15. Convert an IQ of 130 to a Z-score and interpret it.

**Step-by-step solution:**

```
Original distribution: X ~ N(100, 15²)
Mean μ = 100
Standard deviation σ = 15

Observed value: x = 130

Step 1: Calculate Z-score (standardization formula)
Z = (x − μ) / σ
  = (130 − 100) / 15
  = 30 / 15
  = 2

Answer: Z = 2

Interpretation: An IQ of 130 is 2 standard deviations above the mean.

Step 2: Find probability using 68-95-99.7 rule
For standard normal:
- 68% of data within ±1σ of mean
- 95% within ±2σ
- 99.7% within ±3σ

Z = 2 means top ~2.5% (since 95% is within ±2σ, the remaining 5% is split between tails)

More precisely (from Z-table):
P(Z ≤ 2) ≈ 0.9772
So this person scores higher than 97.72% of the population.
```

**Properties of Standard Normal N(0,1):**
```
Mean: E(X) = 0
Variance: Var(X) = 1
Standard deviation: σ = 1
Symmetric around 0
Total area under curve = 1
```

### Common Exam Pitfalls

❌ **TRAP 1:** Confusing N(0,1) with N(μ,σ²)
- N(0,1) specifically means mean=0, variance=1
- N(5,4) means mean=5, variance=4 (NOT standard normal)

❌ **TRAP 2:** Variance vs standard deviation
- N(0,1) has variance=1, so standard deviation=√1=1 ✓
- N(0,4) has variance=4, so standard deviation=√4=2 (NOT 4!)

❌ **TRAP 3:** Z-score formula
- Z = (x−μ)/σ (NOT (x−μ)/σ²)
- Divide by standard deviation, not variance

❌ **TRAP 4:** Interpreting Z-scores
- Z = 2 means "2 standard deviations above mean" (positive = above)
- Z = −1.5 means "1.5 standard deviations below mean" (negative = below)

---

## Formula 13: Expected Value (E(X))

### Name
**Expected Value** (Expectation, Mean of a Random Variable)

### Plain English Explanation
E(X) is the long-run average value of a random variable if you repeated the experiment infinitely many times. It's the "center" of the probability distribution — where you expect the variable to be on average.

**When to use it:**
- Calculating average outcomes in probabilistic scenarios
- Decision making under uncertainty
- Comparing different random variables or strategies
- Foundation for variance, covariance, and other statistics

### Worked Numerical Example

**Question:** You roll a fair six-sided die. What's the expected value of the roll?

**Step-by-step solution:**

```
Random variable: X = outcome of die roll
Possible values: {1, 2, 3, 4, 5, 6}
Probability of each: P(X=k) = 1/6 for all k

Formula for discrete random variable:
E(X) = Σ x · P(X=x)
     = sum of (value × probability)

Step-by-step calculation:
E(X) = 1·P(X=1) + 2·P(X=2) + 3·P(X=3) + 4·P(X=4) + 5·P(X=5) + 6·P(X=6)

     = 1·(1/6) + 2·(1/6) + 3·(1/6) + 4·(1/6) + 5·(1/6) + 6·(1/6)
     
     = (1/6)·(1 + 2 + 3 + 4 + 5 + 6)
     
     = (1/6)·21
     
     = 3.5

Answer: E(X) = 3.5
```

**Interpretation:** On average, you'll roll 3.5. Of course, you can never actually roll 3.5 on a single roll — this is the average over many rolls.

**Verification:** If you rolled a die 600 times, you'd expect about:
- 100 ones → total 100
- 100 twos → total 200
- 100 threes → total 300
- 100 fours → total 400
- 100 fives → total 500
- 100 sixes → total 600
- Grand total: 2100
- Average: 2100/600 = 3.5 ✓

### Common Exam Pitfalls

❌ **TRAP 1:** E(X) might not be a possible value
- E(die roll) = 3.5, but you can't roll 3.5
- Expected value is a long-run average, not a prediction for next outcome

❌ **TRAP 2:** Forgetting to multiply by probabilities
- Wrong: E(X) = sum of all values = 1+2+3+4+5+6 = 21
- Right: E(X) = sum of (value × probability) = 3.5

❌ **TRAP 3:** E(X) for different distributions
- **Binomial X~B(n,p):** E(X) = np
- **Poisson X~Po(λ):** E(X) = λ
- **Geometric X~Geo(p):** E(X) = 1/p
- Don't recalculate from scratch if you recognize the distribution!

❌ **TRAP 4:** Linearity of expectation
- E(aX + b) = aE(X) + b (useful shortcut!)
- E(X + Y) = E(X) + E(Y) (even if X,Y not independent!)

---

## Formula 14: Variance of Random Variable (Var(X))

### Name
**Variance of a Random Variable**

### Plain English Explanation
Var(X) measures how spread out a random variable is around its expected value. Large variance = outcomes widely scattered. Small variance = outcomes tightly clustered around the mean.

**When to use it:**
- Quantifying uncertainty or risk
- Comparing variability of different random processes
- Calculating standard deviation (σ = √Var(X))
- Statistical inference and hypothesis testing

### Worked Numerical Example

**Question:** You flip a coin 3 times and count heads. Let X = number of heads. Calculate Var(X).

**Step-by-step solution:**

```
X ~ Binomial(n=3, p=0.5)

Possible values of X: {0, 1, 2, 3}

Step 1: Calculate probabilities
P(X=0) = C(3,0)(0.5)³(0.5)⁰ = 1 × 0.125 × 1 = 0.125
P(X=1) = C(3,1)(0.5)¹(0.5)² = 3 × 0.5 × 0.25 = 0.375
P(X=2) = C(3,2)(0.5)²(0.5)¹ = 3 × 0.25 × 0.5 = 0.375
P(X=3) = C(3,3)(0.5)³(0.5)⁰ = 1 × 0.125 × 1 = 0.125

Step 2: Calculate E(X)
E(X) = 0×0.125 + 1×0.375 + 2×0.375 + 3×0.125
     = 0 + 0.375 + 0.75 + 0.375
     = 1.5

Or use shortcut: E(X) = np = 3×0.5 = 1.5 ✓

Step 3: Calculate E(X²)
E(X²) = 0²×0.125 + 1²×0.375 + 2²×0.375 + 3²×0.125
      = 0 + 0.375 + 1.5 + 1.125
      = 3

Step 4: Use computational formula
Var(X) = E(X²) − [E(X)]²
       = 3 − (1.5)²
       = 3 − 2.25
       = 0.75

Or use shortcut: Var(X) = npq = 3×0.5×0.5 = 0.75 ✓

Answer: Var(X) = 0.75
Standard deviation: σ = √0.75 ≈ 0.866
```

### Common Exam Pitfalls

❌ **TRAP 1:** Confusing E(X²) with [E(X)]²
- E(X²) = expected value of X-squared = 3
- [E(X)]² = square of expected value = 2.25
- These are DIFFERENT! Var(X) = E(X²) − [E(X)]²

❌ **TRAP 2:** Using the wrong formula for known distributions
- Don't calculate from scratch if you know the distribution!
- Binomial: Var(X) = npq
- Poisson: Var(X) = λ
- Geometric: Var(X) = q/p²

❌ **TRAP 3:** Variance has squared units
- If X is in meters, Var(X) is in meters²
- Take square root to get standard deviation in original units

❌ **TRAP 4:** Var(aX + b) ≠ aVar(X) + b
- Adding constant doesn't change spread: Var(X+b) = Var(X)
- Scaling does: Var(aX) = a²Var(X) (coefficient gets squared!)

---

## Formula 15: Binomial Distribution (P(X=k) = n!/(k!(n-k)!) × pᵏ(1-p)ⁿ⁻ᵏ)

### Name
**Binomial Probability Mass Function**

### Plain English Explanation
Use binomial when you have a fixed number of independent trials (n), each with the same probability of success (p), and you're counting how many successes you get. The formula tells you the probability of getting exactly k successes.

**When to use it:**
- Fixed number of trials (n)
- Each trial is independent
- Only two outcomes per trial (success/failure)
- Probability of success (p) stays constant
- Counting successes

### Worked Numerical Example

**Question:** You take a 10-question multiple choice test where each question has 4 options. You guess randomly on all questions. What's the probability you get exactly 3 correct?

**Step-by-step solution:**

```
Define the problem:
n = 10 (number of trials/questions)
p = 1/4 = 0.25 (probability of guessing correctly)
q = 1 − p = 3/4 = 0.75 (probability of guessing incorrectly)
k = 3 (we want exactly 3 correct)

Formula:
P(X=k) = C(n,k) × pᵏ × qⁿ⁻ᵏ

Step 1: Calculate C(10,3)
C(10,3) = 10! / (3! × 7!)
        = (10 × 9 × 8) / (3 × 2 × 1)
        = 720 / 6
        = 120

Step 2: Calculate pᵏ
p³ = (0.25)³ = 0.015625

Step 3: Calculate qⁿ⁻ᵏ
q⁷ = (0.75)⁷ ≈ 0.1335

Step 4: Multiply all parts
P(X=3) = 120 × 0.015625 × 0.1335
       = 120 × 0.002086
       ≈ 0.2503

Answer: P(exactly 3 correct) ≈ 0.25 or 25%
```

**Additional calculations:**
```
Expected number of correct answers:
E(X) = np = 10 × 0.25 = 2.5

Variance:
Var(X) = npq = 10 × 0.25 × 0.75 = 1.875

Standard deviation:
σ = √1.875 ≈ 1.37
```

### Common Exam Pitfalls

❌ **TRAP 1:** Forgetting the combination term C(n,k)
- Wrong: P(X=3) = p³q⁷ only
- Right: P(X=3) = C(10,3) × p³ × q⁷
- The C(n,k) counts how many different ways to get k successes

❌ **TRAP 2:** Using n-k in wrong place
- p^k × q^(n-k) ✓ (correct)
- p^(n-k) × q^k ✗ (backwards!)

❌ **TRAP 3:** Probabilities don't sum to p
- If p=0.25, P(X=0) is NOT 0.25
- You must calculate using the full formula

❌ **TRAP 4:** "At least k" vs "exactly k"
- Exactly k: use formula once
- At least k: P(X≥k) = P(X=k) + P(X=k+1) + ... + P(X=n)
- At most k: P(X≤k) = P(X=0) + P(X=1) + ... + P(X=k)

---

## Formula 16: Normal/Gaussian PDF (f(x) = (1/(σ√(2π))) × e^(-(x-μ)²/(2σ²)))

### Name
**Normal Distribution Probability Density Function** (Gaussian PDF)

### Plain English Explanation
This is the formula for the bell curve. It describes continuous data that clusters symmetrically around a mean (μ) with spread determined by standard deviation (σ). The shape is always the same (bell-shaped), just shifted and stretched.

**When to use it:**
- Continuous measurements (heights, weights, test scores)
- Errors and noise in measurements
- Central Limit Theorem: sums of random variables → normal
- Many natural phenomena approximately normal

### Worked Numerical Example

**Question:** Heights of adult men follow N(175, 7²) cm. What is the PDF value at exactly x=175 cm? What does this represent?

**Step-by-step solution:**

```
Given:
μ = 175 cm (mean)
σ = 7 cm (standard deviation)
x = 175 cm (the value we're evaluating)

Formula:
f(x) = (1/(σ√(2π))) × e^(-(x-μ)²/(2σ²))

Step 1: Substitute into formula
f(175) = (1/(7√(2π))) × e^(-(175-175)²/(2×7²))

Step 2: Simplify the exponent
(175-175)² = 0² = 0
-(0)/(2×49) = 0
e⁰ = 1

Step 3: Calculate the coefficient
σ√(2π) = 7 × √(2π)
       = 7 × √6.2832
       = 7 × 2.5066
       = 17.546

Step 4: Final calculation
f(175) = 1/17.546 × 1
       ≈ 0.057

Answer: f(175) ≈ 0.057
```

**Important interpretation:**
- This is NOT a probability! (Probabilities for continuous distributions are areas, not point values)
- It's a density — the height of the curve at x=175
- To get probability: P(a < X < b) = ∫[a to b] f(x)dx (area under curve)
- P(X = exactly 175) = 0 for any continuous distribution

**Key properties:**
```
- Peak occurs at x = μ (mean)
- f(μ) is maximum value = 1/(σ√(2π))
- Symmetric around μ
- Inflection points at μ±σ
- Total area under curve = 1
```

### Common Exam Pitfalls

❌ **TRAP 1:** PDF value is NOT a probability
- f(175) = 0.057 does NOT mean P(X=175) = 0.057
- For continuous: P(X = any exact value) = 0 always!
- Probabilities are areas: P(174 < X < 176) = integral

❌ **TRAP 2:** σ² vs σ in the formula
- Formula uses σ² in the exponent: (x-μ)²/(2σ²)
- If given variance (σ²=49), then σ=7
- Don't mix them up!

❌ **TRAP 3:** The formula is rarely asked directly
- Exams usually give you Z-tables or ask for standardization
- You rarely need to compute e^(...) by hand
- Focus on understanding what it represents

❌ **TRAP 4:** 68-95-99.7 rule (more useful!)
- 68% of data within μ±σ
- 95% within μ±2σ
- 99.7% within μ±3σ
- Use this instead of the PDF formula when possible

---

## Formula 17: Moment Generating Function / Multivariate Gaussian Integral

### Name
**Advanced Probability Expression** (Moment Generating Function or Multivariate Gaussian)

### Plain English Explanation
This represents more advanced concepts typically involving either:
1. **Moment Generating Function (MGF):** A tool for finding expected values, variances, and other moments of distributions
2. **Multivariate Gaussian:** Extension of normal distribution to multiple dimensions (used in ML, robotics, computer vision)

Since the recap slide doesn't show the exact formula, I'll cover both concepts.

### Concept A: Moment Generating Function

**What it is:** M_X(t) = E(e^(tX)) — the expected value of e^(tX)

**When to use it:**
- Deriving moments (mean, variance, etc.) by taking derivatives
- Proving distribution properties
- Showing sums of independent random variables

**Example:**

```
For X ~ N(μ, σ²), the MGF is:
M_X(t) = e^(μt + (σ²t²)/2)

Properties:
- M_X(0) = 1 always
- M_X'(0) = E(X) (first derivative at t=0 gives mean)
- M_X''(0) = E(X²) (second derivative gives second moment)
```

### Concept B: Multivariate Gaussian

**What it is:** Extension of normal distribution to vectors

For vector **x** in ℝⁿ with mean vector **μ** and covariance matrix **Σ**:

```
f(x) = (1/√((2π)ⁿ|Σ|)) × exp(-½(x-μ)ᵀΣ⁻¹(x-μ))

Where:
- |Σ| = determinant of covariance matrix
- Σ⁻¹ = inverse of covariance matrix
- (x-μ)ᵀΣ⁻¹(x-μ) = quadratic form (generalizes (x-μ)²/σ² to vectors)
```

**When to use it:**
- Machine learning with multiple features
- Kalman filters (robotics, GPS)
- Multivariate data analysis
- Covariance and correlation between variables

### Worked Example: Bivariate Normal

**Question:** Two variables X and Y follow a bivariate normal distribution. What does this mean?

```
X and Y are jointly normal with:
- Means: E(X) = μ_X, E(Y) = μ_Y
- Variances: Var(X) = σ_X², Var(Y) = σ_Y²
- Covariance: Cov(X,Y) = σ_XY (measures linear relationship)
- Correlation: ρ = σ_XY / (σ_X σ_Y) (standardized covariance)

Mean vector: μ = [μ_X]
                 [μ_Y]

Covariance matrix: Σ = [σ_X²    σ_XY  ]
                        [σ_XY    σ_Y²  ]

Properties:
- Marginal distributions X and Y are each univariate normal
- Conditional distributions X|Y and Y|X are normal
- Contour plots show ellipses (circles if independent)
```

### Common Exam Pitfalls

❌ **TRAP 1:** MGFs require calculus
- Finding derivatives and expected values
- Usually provided or asked conceptually, not computed

❌ **TRAP 2:** Multivariate ≠ multiple univariate
- Multivariate Gaussian models relationships (covariance)
- Multiple independent normals have diagonal covariance matrix

❌ **TRAP 3:** Covariance matrix must be positive definite
- All eigenvalues must be positive
- Ensures valid probability distribution

❌ **TRAP 4:** Dimensionality explodes quickly
- 2D: need mean vector (2 values) + covariance matrix (3 unique values)
- 10D: need 10 means + 55 unique covariances
- Curse of dimensionality in ML

**For the exam:**
- Focus on understanding what these concepts represent
- You likely won't hand-calculate multivariate integrals
- Know when to use multivariate models (multiple correlated variables)
- Understand that MGFs are tools for theoretical work, not everyday calculations

---

## Formula 18: End Slide

**This is just the closing slide of the recap quiz — no formula to learn!**

---

## Quick Reference Summary

| Formula | Key Insight | Memory Hook |
|---------|-------------|-------------|
| 1. Mean | Add all, divide by count | "Fair share distribution" |
| 2. Variance | Average squared distance from mean | "S.O.S. — Sum Of Squares" |
| 3. Std Dev | Square root of variance | "Same units as data" |
| 4. Dot Product | Multiply matching, add all | w₁x₁ + w₂x₂ + ... |
| 5. Matrix y=Xw | Predictions from data × weights | Each row = one prediction |
| 6. Pseudo-inverse | Best fit weights | (XᵀX)⁻¹Xᵀy solves least squares |
| 7. Step Function | Binary threshold | 1 if x≥0, else 0 |
| 8. Linear f(x,y) | Weighted sum of inputs | Intercept + coefficients |
| 9. f: ℝ³→ℝ | Input dimensions → output dimensions | 3 inputs, 1 output |
| 10. P(A∪B) | Add then subtract overlap | Don't double-count! |
| 11. Bayes | Flip conditional probability | P(B\|A) → P(A\|B) |
| 12. N(0,1) | Standard normal | Mean 0, variance 1 |
| 13. E(X) | Long-run average | Sum of value × probability |
| 14. Var(X) | Spread around mean | E(X²) − [E(X)]² |
| 15. Binomial | Fixed trials, count successes | C(n,k)pᵏqⁿ⁻ᵏ |
| 16. Normal PDF | Bell curve formula | Rarely calculate by hand |
| 17. Advanced | MGF or multivariate Gaussian | Theoretical tools |

---

## Final Exam Strategy

**Before the exam:**
1. ✅ Write out all formulas from memory (no looking!)
2. ✅ Do practice problems for each formula type
3. ✅ Review "Common Pitfalls" sections — these are exam trap hotspots
4. ✅ Sleep well — memory consolidation happens during sleep

**During the exam:**
1. **First 60 seconds:** Brain dump key formulas onto scratch paper
2. **Read twice:** Understand what they're asking before calculating
3. **Show work:** Partial credit comes from correct method
4. **Sanity check:** Does your answer make sense? (Probability between 0 and 1? Variance ≥ 0?)
5. **Stuck? Skip it:** Come back later with fresh eyes

**Key principles:**
- Negative probability → WRONG, recalculate
- Probability > 1 → WRONG, check if you forgot to subtract overlap
- Huge variance from small dataset → Check if you used n vs n-1 correctly
- Answer doesn't match units → Review what the question asked for

---

## Good luck! 🚀

You have all the tools. Now go show that quiz what you know!
