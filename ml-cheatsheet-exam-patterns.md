# ML Exam Patterns & Notation Reference
**Open-Book Exam Quick Reference | Principles of Machine Learning**

---

## 📋 Practice Paper Analysis

### Exam Structure
- **Duration:** 2 hours
- **Format:** Open-book (textbooks, notes, online materials permitted)
- **Requirements:** Answer **FOUR** questions out of four
- **Citations:** Must cite all sources used (normal plagiarism rules apply)
- **Word Limits:** Strict adherence required - exceeding limits means no marks
- **Solo Work:** Must complete independently without consulting others

### Marks Distribution

| Question | Topic | Marks | Sub-parts |
|----------|-------|-------|-----------|
| Q1 | **Regression** | 25 | a) MMSE solution (15) + b) Model complexity (10) |
| Q2 | **Classification** | 25 | a) Linear classifiers (10) + b) Bayes/LDA (15) |
| Q3 | **Model Optimisation** | 25 | a) K-means & local minima (15) + b) Validation (10) |
| Q4 | **Neural Networks** | 25 | a) Architecture concepts (15) + b) Parameter counting (10) |

**Total:** 100 marks (4 questions × 25 marks each)

### Question Depth & Expectations

#### Q1 - Regression (25 marks)
- **Computational:** Calculate MMSE coefficients using matrix operations
- **Conceptual:** Understand bias-variance trade-off, overfitting
- **Personalised data:** Uses student ID digits for unique dataset
- **Show working:** Must show matrix multiplications, intermediate steps

#### Q2 - Classification (25 marks)
- **Visual analysis:** Interpret scatter plots, draw decision boundaries
- **Calculations:** Confusion matrices, sensitivity, specificity
- **Probabilistic reasoning:** Bayes classifier, prior/posterior calculations
- **Graph interpretation:** Read coordinates from figures

#### Q3 - Model Optimisation (25 marks)
- **Conceptual understanding:** Explain local vs global minima
- **Strategy design:** Propose practical solutions (e.g., random restarts)
- **Critical evaluation:** Assess validation approaches, identify flaws
- **Written explanation:** Clear, concise prose required

#### Q4 - Neural Networks (25 marks)
- **Architectural knowledge:** Compare layer types, design principles
- **Parameter counting:** Calculate trainable parameters systematically
- **Dimension tracking:** Follow feature map sizes through layers
- **Design rationale:** Explain architectural choices

---

## 🎯 Question Type Templates

### Template 1: MMSE Linear Regression

**Question Pattern:**
> Given a dataset with N samples, obtain the MMSE coefficients of a linear model y = w₀ + w₁x using w = (X<sup>T</sup>X)<sup>-1</sup> X<sup>T</sup>y

**Step-by-Step Template:**

1. **Calculate personalised y values** (if using student ID)
   ```
   Example: If D1=5, then y = 1 + 0.1×5 = 1.5
   ```

2. **Construct the design matrix X**
   ```
   For y = w₀ + w₁x:
   X = [1  x₁]
       [1  x₂]
       [⋮   ⋮]
       [1  xₙ]
   ```

3. **Construct the label vector y**
   ```
   y = [y₁]
       [y₂]
       [⋮ ]
       [yₙ]
   ```

4. **Use given intermediate result or calculate X<sup>T</sup>X**
   ```
   X^T X = [    N        Σxᵢ    ]
           [  Σxᵢ      Σxᵢ²    ]
   ```

5. **Calculate X<sup>T</sup>y**
   ```
   X^T y = [  Σyᵢ   ]
           [ Σxᵢyᵢ  ]
   ```

6. **Apply the formula**
   ```
   w = (X^T X)^(-1) X^T y = [w₀]
                             [w₁]
   ```

7. **State the final model**
   ```
   y = w₀ + w₁x = [value] + [value]x
   ```

**Worked Example (Practice Paper Solution):**
```
Dataset (D1=D2=D3=D4=0):
x: 2, 4, 1, 3
y: 1, 5, 2, 2

Design matrix:        Label vector:
X = [1  2]           y = [1]
    [1  4]               [5]
    [1  1]               [2]
    [1  3]               [2]

Given: (X^T X)^(-1) = [1.5  -0.5]
                      [-0.5  0.2]

Calculate X^T y:
X^T y = [1 1 1 1] [1]   = [10]
        [2 4 1 3] [5]     [30]
                  [2]
                  [2]

Apply formula:
w = [1.5  -0.5] [10]  = [0]
    [-0.5  0.2] [30]    [1]

Final model: y = 0 + 1x = x
```

---

### Template 2: Calculate Training MSE

**Question Pattern:**
> Calculate the training Mean Square Error (MSE) of the solution

**Step-by-Step Template:**

1. **For each sample, calculate prediction**
   ```
   ŷᵢ = f(xᵢ) = w₀ + w₁xᵢ
   ```

2. **Calculate error for each sample**
   ```
   eᵢ = yᵢ - ŷᵢ
   ```

3. **Square each error**
   ```
   eᵢ² = (yᵢ - ŷᵢ)²
   ```

4. **Sum and average**
   ```
   MSE = (1/N) Σ eᵢ²
   ```

**Worked Example:**
```
Model: y = x
Dataset: x=[2,4,1,3], y=[1,5,2,2]

Sample  x   y   ŷ=x   e=y-ŷ   e²
1       2   1   2     -1      1
2       4   5   4      1      1
3       1   2   1      1      1
4       3   2   3     -1      1

MSE = (1+1+1+1)/4 = 4/4 = 1
```

---

### Template 3: Linear Classifier Decision Boundary

**Question Pattern:**
> Given linear classifier w<sup>T</sup>x = 0 where w = [w₀, w₁, w₂]<sup>T</sup> and x = [1, xₐ, xᵦ]<sup>T</sup>, obtain decision regions

**Step-by-Step Template:**

1. **Write out the classifier equation**
   ```
   w^T x = w₀ + w₁xₐ + w₂xᵦ = 0
   ```

2. **Substitute given coefficients**
   ```
   Example: w₂=0, w₁=1, w₀=0.25×D
   → 0.25D + 1×xₐ + 0×xᵦ = 0
   ```

3. **Solve for decision boundary**
   ```
   xₐ = -0.25D  (vertical line if w₂=0)
   or
   xᵦ = -(w₀ + w₁xₐ)/w₂  (general case)
   ```

4. **Identify decision regions**
   ```
   w^T x > 0  →  Positive class (○)
   w^T x ≤ 0  →  Negative class (×)
   ```

5. **Express in plain English**
   ```
   "Points with xₐ > -0.25D are classified as ○"
   "Points with xₐ ≤ -0.25D are classified as ×"
   ```

**Worked Example (D=8):**
```
Classifier: 0.25×8 + xₐ = 0
Boundary: xₐ = -2

Decision regions:
- xₐ > -2  →  ○ (positive class)
- xₐ ≤ -2  →  × (negative class)

This is a vertical line at xₐ = -2
```

---

### Template 4: Confusion Matrix & Performance Metrics

**Question Pattern:**
> Obtain the classifier's confusion matrix and identify sensitivity and specificity

**Step-by-Step Template:**

1. **For each data point, determine:**
   - Actual class (from figure/data)
   - Predicted class (using decision boundary)

2. **Count outcomes:**
   - True Positives (TP): Actual ○, Predicted ○
   - False Positives (FP): Actual ×, Predicted ○
   - True Negatives (TN): Actual ×, Predicted ×
   - False Negatives (FN): Actual ○, Predicted ×

3. **Construct confusion matrix:**
   ```
                  Predicted
              ○           ×
   Actual ○   TP          FN
          ×   FP          TN
   ```

4. **Calculate metrics:**
   ```
   Sensitivity = TP/(TP+FN)    [True Positive Rate]
   Specificity = TN/(TN+FP)    [True Negative Rate]
   Accuracy = (TP+TN)/(TP+TN+FP+FN)
   ```

**Worked Example (Practice Paper):**
```
Decision boundary: xₐ = -2
From Figure 1, classify each point:

Actual ○ points at xₐ > -2: 5 points → TP = 5
Actual ○ points at xₐ ≤ -2: 1 point  → FN = 1
Actual × points at xₐ > -2: 2 points → FP = 2
Actual × points at xₐ ≤ -2: 7 points → TN = 7

Confusion Matrix:
              Predicted
          ○       ×
Actual ○  5       1
       ×  2       7

Sensitivity = 5/(5+1) = 5/6 ≈ 0.833
Specificity = 7/(7+2) = 7/9 ≈ 0.778
```

---

### Template 5: Bayes Classifier with Single Feature

**Question Pattern:**
> Build a Bayes classifier using predictor feature xₐ. Obtain priors, means, and classify a specific sample.

**Step-by-Step Template:**

1. **Calculate class priors**
   ```
   P(○) = (number of ○ samples) / (total samples)
   P(×) = (number of × samples) / (total samples)
   ```

2. **Calculate class-conditional means**
   ```
   μ_○ = (1/N_○) Σ(xₐ for all ○ samples)
   μ_× = (1/N_×) Σ(xₐ for all × samples)
   ```

3. **For Bayes classifier, compare:**
   ```
   P(xₐ|○) × P(○)  vs  P(xₐ|×) × P(×)
   ```

4. **If equal variances, decision boundary is at:**
   ```
   Midpoint weighted by priors
   ```

5. **Classify new sample:**
   - If sample is closer to mean of class with higher prior → that class
   - If equidistant and equal variances → class with higher prior

**Worked Example (Practice Paper):**
```
From Figure 1:
- ○ samples: 6 points
- × samples: 9 points
- Total: 15 points

Priors:
P(○) = 6/15 = 2/5 = 0.4
P(×) = 9/15 = 3/5 = 0.6

Means (reading from figure):
μ_○ = -3
μ_× = 2

Classify xₐ = -0.5:
- Midpoint between means: (-3 + 2)/2 = -0.5
- Sample is exactly halfway

With equal variances:
P(xₐ|○) = P(xₐ|×)  (same distance from means)

Therefore:
P(xₐ|○)×P(○) = P(xₐ|○) × 0.4
P(xₐ|×)×P(×) = P(xₐ|×) × 0.6

Since P(×) > P(○), classify as ×
```

---

### Template 6: Explain Local vs Global Minima

**Question Pattern:**
> Use the notion of error function to explain local minimum and global minimum

**Step-by-Step Template:**

1. **Define error function**
   ```
   "The error function E(θ) maps each candidate model 
   (parameterised by θ) to an error value"
   ```

2. **Explain global minimum**
   ```
   "A global minimum is the model θ* with the lowest error 
   amongst ALL candidate models:
   E(θ*) ≤ E(θ) for all θ"
   ```

3. **Explain local minimum**
   ```
   "A local minimum is a model θ_local with the lowest error 
   within a vicinity/neighbourhood:
   E(θ_local) ≤ E(θ) for all θ near θ_local
   (but may have E(θ_local) > E(θ*) elsewhere)"
   ```

4. **Visual metaphor (optional)**
   ```
   "Think of a hilly landscape: global minimum is the 
   lowest valley in the entire region; local minima are 
   lower than immediate surroundings but not globally lowest"
   ```

---

### Template 7: Parameter Counting in CNNs

**Question Pattern:**
> A convolutional layer has M feature maps of size H×W, using K×K filters. How many parameters?

**Step-by-Step Template:**

1. **Identify components:**
   - Number of output feature maps: M
   - Filter/kernel dimensions: K × K × D
     - D = number of input feature maps (depth)
   - Bias terms: 1 per filter

2. **Calculate parameters per filter:**
   ```
   Parameters per filter = (K × K × D) + 1
                         = kernel weights + bias
   ```

3. **Total parameters:**
   ```
   Total = M × [(K × K × D) + 1]
         = M × (K² × D + 1)
   ```

4. **Common mistake to avoid:**
   - DON'T multiply by output size H×W
   - Filters are SHARED across all spatial positions
   - That's what makes CNNs parameter-efficient!

**Worked Example (Practice Paper Q4):**
```
First layer:
- Input: 100×100 grayscale image (1 channel)
- Output: 2 feature maps of 100×100
- Filter size: 3×3

Parameters per filter = (3 × 3 × 1) + 1 = 9 + 1 = 10
Total parameters = 2 × 10 = 20

Second layer (max pooling):
- No trainable parameters!
- Input: 2 feature maps of 100×100
- Output: 2 feature maps of 50×50 (2×2 pooling)

Third layer:
- Input: 2 feature maps of 50×50
- Output: 8 feature maps of size ?
- Filter dimensions: 3 × 3 × D
- D = number of input feature maps = 2

Parameters per filter = (3 × 3 × 2) + 1 = 18 + 1 = 19
Total parameters = 8 × 19 = 152
```

---

## 📐 Mathematical Notation Quick Reference

### Summation Notation

| Notation | Plain English | Python Code |
|----------|---------------|-------------|
| `Σᵢ xᵢ` | Sum of all x values | `sum(x)` or `np.sum(x)` |
| `Σᵢ₌₁ⁿ xᵢ` | Sum x from i=1 to n | `sum(x[0:n])` |
| `Σᵢ xᵢ²` | Sum of squared x values | `sum(x**2)` or `np.sum(x**2)` |
| `Σᵢ xᵢyᵢ` | Sum of element-wise products | `sum(x*y)` or `np.dot(x,y)` |
| `(1/N) Σᵢ xᵢ` | Mean/average of x | `np.mean(x)` |
| `Σᵢ (xᵢ - μ)²` | Sum of squared deviations | `np.sum((x - mu)**2)` |

### Matrix Operations

| Notation | Plain English | Python Code |
|----------|---------------|-------------|
| `X^T` | Transpose of matrix X | `X.T` |
| `X^(-1)` | Inverse of matrix X | `np.linalg.inv(X)` |
| `X^T X` | X transpose times X | `X.T @ X` or `np.dot(X.T, X)` |
| `(X^T X)^(-1)` | Inverse of X transpose times X | `np.linalg.inv(X.T @ X)` |
| `w^T x` | Dot product of vectors | `np.dot(w, x)` or `w @ x` |
| `\\|x\\|` | Norm/length of vector | `np.linalg.norm(x)` |
| `\\|x\\|²` | Squared norm | `np.dot(x, x)` |

### Partial Derivatives

| Notation | Plain English | Python Context |
|----------|---------------|----------------|
| `∂E/∂w` | Partial derivative of E with respect to w | Rate of change of error as w changes |
| `∇E` | Gradient of E (vector of all partial derivatives) | Direction of steepest increase |
| `∂²E/∂w²` | Second partial derivative | Curvature of error surface |

**Gradient descent update rule:**
```
Mathematical: w_new = w_old - α(∂E/∂w)
Plain English: "Move w in opposite direction of gradient, step size α"
Python: w = w - alpha * gradient
```

### Argmin / Argmax

| Notation | Plain English | Python Code |
|----------|---------------|-------------|
| `argmin_w E(w)` | Value of w that minimises E | `w[np.argmin(E)]` |
| `argmax_w f(w)` | Value of w that maximises f | `w[np.argmax(f)]` |
| `w* = argmin E(w)` | Optimal w that gives minimum error | `w_optimal = w[np.argmin(E)]` |

**Example:**
```
Mathematical: ŷ = argmax_c P(c|x)
Plain English: "Predicted class is the one with highest probability"
Python: y_pred = classes[np.argmax(probabilities)]
```

### Probability Notation

| Notation | Plain English | Python Context |
|----------|---------------|----------------|
| `P(A)` | Probability of event A | Prior probability |
| `P(A\\|B)` | Probability of A given B | Conditional/posterior probability |
| `P(A,B)` | Joint probability of A and B | Probability both occur |
| `P(A\\|B) = P(B\\|A)P(A)/P(B)` | Bayes' theorem | Update belief with evidence |
| `E[X]` | Expected value of X | Mean/average value |
| `Var[X]` | Variance of X | Spread/dispersion |
| `N(μ, σ²)` | Normal/Gaussian distribution | Mean μ, variance σ² |

**Bayes Classifier:**
```
Mathematical: ĉ = argmax_c P(c|x) = argmax_c P(x|c)P(c)
Plain English: "Predict class with highest posterior probability"
Python:
posteriors = [P_x_given_c[c] * P_c[c] for c in classes]
c_pred = classes[np.argmax(posteriors)]
```

### Mean Square Error (MSE)

| Notation | Plain English | Python Code |
|----------|---------------|-------------|
| `MSE = (1/N) Σᵢ (yᵢ - ŷᵢ)²` | Average squared error | `np.mean((y - y_pred)**2)` |
| `MSE = (1/N) \\|y - ŷ\\|²` | Vector notation for MSE | `np.linalg.norm(y - y_pred)**2 / len(y)` |
| `MMSE = min_w MSE(w)` | Minimum Mean Square Error | Optimal value of MSE |

### Design Matrix for Polynomials

**Linear model: y = w₀ + w₁x**
```
X = [1  x₁]     w = [w₀]     y = [y₁]
    [1  x₂]         [w₁]         [y₂]
    [⋮   ⋮]                      [⋮ ]
    [1  xₙ]                      [yₙ]
```

**Quadratic model: y = w₀ + w₁x + w₂x²**
```
X = [1  x₁  x₁²]     w = [w₀]
    [1  x₂  x₂²]         [w₁]
    [⋮   ⋮   ⋮ ]         [w₂]
    [1  xₙ  xₙ²]
```

**General polynomial order d:**
```
X = [1  x₁  x₁²  ...  x₁ᵈ]
    [1  x₂  x₂²  ...  x₂ᵈ]
    [⋮   ⋮   ⋮   ...   ⋮ ]
    [1  xₙ  xₙ²  ...  xₙᵈ]
```

---

## 🌳 Decision Flowcharts

### Flowchart 1: What Model Should I Use?

```
START: What type of problem?
│
├─> REGRESSION (predict continuous value)
│   │
│   ├─> Linear relationship expected?
│   │   │
│   │   ├─> YES → LINEAR REGRESSION
│   │   │         • Model: y = w₀ + w₁x₁ + ... + wₚxₚ
│   │   │         • Use when: scatter plot shows straight line
│   │   │         • Solution: w = (X^T X)^(-1) X^T y
│   │   │
│   │   └─> NO → POLYNOMIAL REGRESSION
│   │             • Model: y = w₀ + w₁x + w₂x² + ... + wₐxᵈ
│   │             • Use when: curved relationship
│   │             • Caution: high d → overfitting
│   │
│   └─> Non-linear relationship?
│       │
│       ├─> Exponential pattern → EXPONENTIAL REGRESSION
│       │                         • Transform: log(y) vs x or log(y) vs log(x)
│       │
│       └─> Complex pattern → NEURAL NETWORK
│                            • Use when: many features, complex interactions
│
└─> CLASSIFICATION (predict discrete class)
    │
    ├─> Linear decision boundary?
    │   │
    │   ├─> YES → LINEAR CLASSIFIER
    │   │         • Model: w^T x = 0
    │   │         • Use when: classes separable by line/plane
    │   │
    │   └─> NO → NON-LINEAR CLASSIFIER
    │             • Polynomial features
    │             • Neural networks
    │
    ├─> Have probability distributions?
    │   │
    │   └─> YES → BAYES CLASSIFIER / LDA
    │             • Use when: know P(x|class) and P(class)
    │             • Optimal when assumptions met
    │
    ├─> Image data?
    │   │
    │   └─> YES → CONVOLUTIONAL NEURAL NETWORK (CNN)
    │             • Use for: images, spatial data
    │             • Exploits: spatial structure
    │
    ├─> Time series data?
    │   │
    │   └─> YES → RECURRENT NEURAL NETWORK (RNN)
    │             or CONVOLUTIONAL for sequences
    │
    └─> Clustering (unsupervised)?
        │
        └─> YES → K-MEANS
                  • Use when: want to find K groups
                  • Tip: try multiple random starts
```

### Flowchart 2: Model Selection & Validation Strategy

```
START: How much data do I have?
│
├─> VERY LIMITED (<100 samples)
│   │
│   └─> Use CROSS-VALIDATION
│       • K-fold (k=5 or k=10)
│       • Leave-one-out (extreme case)
│       • Maximises use of limited data
│
├─> MODERATE (100-10,000 samples)
│   │
│   └─> Use VALIDATION SET
│       • 70-30 or 80-20 split
│       • Train on 70-80%, validate on 20-30%
│       • Balance: enough data to train + reliable validation
│
└─> LARGE (>10,000 samples)
    │
    └─> Use HOLD-OUT TEST SET
        • 98-2 or 99-1 split
        • Small % sufficient for reliable test estimate
        • Use most data for training
        • Can add separate validation set for model selection

KEY DECISION POINTS:

Is my data sequential/temporal?
├─> YES → DON'T randomise splits!
│          • Use first K points for train
│          • Later points for validation
│          • Avoids "future information leakage"
│
└─> NO → RANDOMISE train/validation split
          • Ensures representative samples
          • Avoids sampling artifacts

Am I selecting between model FAMILIES?
├─> YES → Need VALIDATION set
│          1. Train each family on train set
│          2. Evaluate on validation set
│          3. Select best family
│          4. Retrain on ALL data
│          5. Report final test error
│
└─> NO → Just tuning ONE model
          • Can use full dataset
          • Or use cross-validation for robustness
```

### Flowchart 3: Debugging Poor Performance

```
My model performs poorly. Why?

Check TRAINING ERROR:
│
├─> Training error HIGH (underfitting)
│   │
│   ├─> Solution 1: INCREASE MODEL COMPLEXITY
│   │   • Add polynomial features
│   │   • Add more layers/neurons
│   │   • Use more flexible model family
│   │
│   ├─> Solution 2: ADD MORE FEATURES
│   │   • Feature engineering
│   │   • Polynomial/interaction terms
│   │
│   └─> Solution 3: REDUCE REGULARISATION
│       • Decrease λ in ridge/lasso
│       • Reduce dropout rate
│
└─> Training error LOW, test error HIGH (overfitting)
    │
    ├─> Solution 1: GET MORE TRAINING DATA
    │   • Best solution if possible
    │   • More data → better generalisation
    │
    ├─> Solution 2: REDUCE MODEL COMPLEXITY
    │   • Lower polynomial degree
    │   • Fewer layers/neurons
    │   • Simpler model family
    │
    ├─> Solution 3: ADD REGULARISATION
    │   • Ridge (L2): penalise large weights
    │   • Lasso (L1): feature selection
    │   • Dropout in neural networks
    │
    ├─> Solution 4: GET MORE TRAINING DATA
    │   • Data augmentation (images)
    │   • Synthetic data generation
    │
    └─> Solution 5: CROSS-VALIDATION
        • Ensure test error estimate is reliable
        • k-fold for more robust evaluation

Special case: Training error is ZERO
│
├─> Number of parameters ≥ Number of samples?
│   │
│   └─> YES → PERFECT MEMORISATION
│           • Polynomial degree = N samples → MSE=0
│           • Will NOT generalise
│           • REDUCE complexity
│
└─> Convergence to local minimum?
    │
    └─> YES (k-means, neural nets)
            • Try MULTIPLE RANDOM STARTS
            • Select best result
            • Consider different initialisation strategies
```

---

## 💡 Exam Tips

### Time Management (2 hours for 4 questions)

| Task | Time | Strategy |
|------|------|----------|
| **Read all questions** | 5 min | Identify easiest questions first |
| **Question 1** | 25 min | ~1 min per mark + buffer |
| **Question 2** | 25 min | ~1 min per mark + buffer |
| **Question 3** | 25 min | ~1 min per mark + buffer |
| **Question 4** | 25 min | ~1 min per mark + buffer |
| **Review** | 20 min | Check calculations, add clarifications |

**Strategy:**
- Do EASIEST question first (build confidence, bank marks)
- Flag any personalised data (student ID) immediately
- Leave hardest question for last
- If stuck, move on - come back later

### Showing Working for Full Marks

#### 1. Matrix Calculations
```
❌ BAD: "w = [0, 1]"

✓ GOOD:
"Calculate X^T y:
X^T y = [1 1 1 1] [1]   = [1+5+2+2]   = [10]
        [2 4 1 3] [5]     [2+20+2+6]    [30]
                  [2]
                  [2]

Apply w = (X^T X)^(-1) X^T y:
w = [1.5  -0.5] [10]  = [1.5×10 - 0.5×30]  = [0]
    [-0.5  0.2] [30]    [-0.5×10 + 0.2×30]   [1]"
```

#### 2. Classification Problems
```
❌ BAD: "Sensitivity = 5/6"

✓ GOOD:
"Count true positives:
Points at xₐ > -2 with ○ label: (0,1), (1,2), ... → 5 points
Points at xₐ ≤ -2 with ○ label: (-3,0) → 1 point

TP = 5, FN = 1

Sensitivity = TP / (TP + FN) = 5 / (5 + 1) = 5/6 ≈ 0.833"
```

#### 3. Conceptual Questions
```
❌ BAD: "K-means converges to local minimum because it's iterative"

✓ GOOD:
"The k-means algorithm defines an iterative process where each step
reduces the error function. Starting from an initial clustering,
the algorithm updates cluster assignments and centroids to minimise
within-cluster variance. Since the algorithm only explores solutions
near the starting point, it converges to a local minimum in that
region, not necessarily the global minimum across all possible
clusterings. Different starting points lead to different local minima."
```

### Common Pitfalls

#### ❌ Pitfall 1: Forgetting the Bias Term
```
WRONG:  Parameters in 3×3 filter = 3×3 = 9
CORRECT: Parameters in 3×3 filter = 3×3 + 1 = 10 (kernel + bias)
```

#### ❌ Pitfall 2: Multiplying by Output Size
```
WRONG:  CNN layer with 2 filters, output 100×100
        → Parameters = 2 × 10 × 100 × 100
        
CORRECT: Parameters = 2 × 10 = 20
        (filters are SHARED across spatial positions)
```

#### ❌ Pitfall 3: Using Training Error for Model Selection
```
WRONG:  "Model A has training MSE=0.1, Model B has 0.2,
        therefore A is better"

CORRECT: "Training error cannot assess generalisation.
         Must use validation/test set to compare models.
         Training error only shows how well model fits
         training data, not deployment performance."
```

#### ❌ Pitfall 4: Confusing Dimensions
```
WRONG:  After 2×2 max pooling on 100×100 image → 50×100

CORRECT: After 2×2 max pooling on 100×100 image → 50×50
        (pooling reduces BOTH dimensions)
```

#### ❌ Pitfall 5: Incorrect Confusion Matrix Layout
```
WRONG:                Actual
              ○           ×
Predicted ○   TP          FP    ← SWAPPED
          ×   FN          TN

CORRECT:              Predicted
                  ○           ×
   Actual     ○   TP          FN
              ×   FP          TN
```

#### ❌ Pitfall 6: Not Reading the Figure Carefully
```
"Always check:
- Which axis is which variable
- What are the marker shapes (○ vs ×)
- Scale of axes
- Exact coordinates of points"

If question says "dataset shown in Figure 1":
→ You MUST count and use those specific points
→ Don't assume symmetric or idealised data
```

#### ❌ Pitfall 7: Polynomial Degree Confusion
```
WRONG:  4 samples → can fit polynomial of degree 4

CORRECT: 4 samples → can fit polynomial of degree 3
        (need N samples for degree N-1 polynomial)
        
Or: N samples → degree N polynomial has N+1 parameters
    If parameters > samples → underdetermined system
```

### Quick Checks Before Submitting

- [ ] Substituted student ID digits correctly?
- [ ] All matrix dimensions compatible?
- [ ] Shown intermediate steps for calculations?
- [ ] Stated final answer clearly?
- [ ] Explained reasoning for conceptual questions?
- [ ] Checked answer makes intuitive sense?
- [ ] Units/dimensions correct?
- [ ] Confusion matrix labels correct?
- [ ] Word limits adhered to?
- [ ] Citations included (if used external sources)?

---

## 📚 Worked Examples from Solutions

### Example 1: Complete MMSE Regression (Q1)

**Given Dataset (D1=D2=D3=D4=0):**
| x | y |
|---|---|
| 2 | 1 |
| 4 | 5 |
| 1 | 2 |
| 3 | 2 |

**Model:** y = w₀ + w₁x

**Given:** (X<sup>T</sup>X)<sup>-1</sup> = [[1.5, -0.5], [-0.5, 0.2]]

**Solution:**

Step 1: Design matrix and label vector
```
X = [1  2]       y = [1]
    [1  4]           [5]
    [1  1]           [2]
    [1  3]           [2]
```

Step 2: Calculate X<sup>T</sup>y
```
X^T = [1  1  1  1]
      [2  4  1  3]

X^T y = [1  1  1  1] [1]   = [10]
        [2  4  1  3] [5]     [30]
                     [2]
                     [2]

Calculation:
First row:  1×1 + 1×5 + 1×2 + 1×2 = 10
Second row: 2×1 + 4×5 + 1×2 + 3×2 = 30
```

Step 3: Apply MMSE formula
```
w = (X^T X)^(-1) X^T y

w = [1.5  -0.5] [10]
    [-0.5  0.2] [30]

w₀ = 1.5×10 + (-0.5)×30 = 15 - 15 = 0
w₁ = (-0.5)×10 + 0.2×30 = -5 + 6 = 1

w = [0]
    [1]
```

**Final model:** y = 0 + 1×x = x

Step 4: Calculate training MSE
```
Sample  x   y   ŷ=x   e=y-ŷ   e²
1       2   1   2     -1      1
2       4   5   4      1      1
3       1   2   1      1      1
4       3   2   3     -1      1

MSE = (1/4) × (1+1+1+1) = 1
```

**Answer:** w₀=0, w₁=1, model is y=x, training MSE=1

---

### Example 2: Cubic Model Analysis (Q1b)

**Question:** Consider cubic model y = w₀ + w₁x + w₂x² + w₃x³ for the same 4-sample dataset.

**(i) What would you expect training MSE to be?**

**Answer:**
"The training MSE would be zero. A cubic polynomial has 4 parameters (w₀, w₁, w₂, w₃) and we have 4 samples. We can always find a polynomial of degree 3 that passes exactly through 4 points, resulting in perfect predictions (ŷᵢ = yᵢ) and therefore MSE = 0."

**(ii) True model is y = x + n where n ~ N(0, σ²). Identify main error sources during deployment.**

**Answer:**
The main sources of error are:

1. **Irreducible error (variance of n):** The random noise component σ² cannot be eliminated by any model.

2. **Model bias:** The difference between the true pattern (linear: y = x) and the predicted pattern (cubic). The cubic model will fit spurious curves not present in the true relationship.

3. **Model variance (due to sampling):** The cubic model's parameters are highly sensitive to the specific training samples. Different samples would produce very different cubic curves, leading to high variability in predictions.

**Key insight:** The cubic model will overfit, capturing noise as signal. Despite zero training error, deployment error will be higher than a simple linear model.

---

### Example 3: Linear Classifier with Confusion Matrix (Q2)

**Given:**
- Linear classifier: w<sup>T</sup>x = 0
- w = [w₀, w₁, w₂]<sup>T</sup> = [0.25D, 1, 0]<sup>T</sup> (D=8)
- x = [1, xₐ, xᵦ]<sup>T</sup>
- Classification: w<sup>T</sup>x > 0 → ○, otherwise ×

**Solution:**

**(i) Decision boundary:**
```
w^T x = w₀×1 + w₁×xₐ + w₂×xᵦ
      = 0.25×8 + 1×xₐ + 0×xᵦ
      = 2 + xₐ
      = 0

Decision boundary: xₐ = -2 (vertical line)

Decision regions:
- xₐ > -2  → w^T x > 0 → ○ (positive class)
- xₐ ≤ -2  → w^T x ≤ 0 → × (negative class)
```

**(ii) Confusion matrix from Figure 1:**
```
Reading from figure, count points in each region:

Actual ○ with xₐ > -2:  5 points → TP = 5
Actual ○ with xₐ ≤ -2:  1 point  → FN = 1
Actual × with xₐ > -2:  2 points → FP = 2  
Actual × with xₐ ≤ -2:  7 points → TN = 7

Confusion Matrix:
                Predicted
            ○       ×
Actual  ○   5       1       Total ○: 6
        ×   2       7       Total ×: 9

Sensitivity = TP/(TP+FN) = 5/(5+1) = 5/6 ≈ 0.833
Specificity = TN/(TN+FP) = 7/(7+2) = 7/9 ≈ 0.778
```

---

### Example 4: Bayes Classifier (Q2b)

**From Figure 1, build Bayes classifier using feature xₐ:**

**(i) Priors and means:**
```
Count samples:
- Total samples: 15
- ○ samples: 6
- × samples: 9

Priors:
P(○) = 6/15 = 2/5 = 0.4
P(×) = 9/15 = 3/5 = 0.6

Read xₐ coordinates for each class from figure:
○ samples: approximately at xₐ = -5, -4, -3, -3, -2, -1
Mean: μ_○ = (-5-4-3-3-2-1)/6 = -18/6 = -3

× samples: approximately at xₐ = 0, 1, 2, 2, 3, 3, 4, 5, 6
Mean: μ_× = (0+1+2+2+3+3+4+5+6)/9 = 26/9 ≈ 2.89 ≈ 2
```

**(ii) Bayes classifier description:**
```
"The Bayes classifier computes the posterior probability of each
class given the observed xₐ value:

Posterior(○|xₐ) ∝ P(xₐ|○) × P(○)
Posterior(×|xₐ) ∝ P(xₐ|×) × P(×)

where P(xₐ|○) and P(xₐ|×) are the class-conditional likelihoods.

The classifier assigns the label corresponding to the class with
the highest posterior probability."
```

**(iii) Classify xₐ = -0.5 with equal standard deviations:**
```
Distance from ○ mean: |-0.5 - (-3)| = 2.5
Distance from × mean: |-0.5 - 2| = 2.5

Sample is equidistant from both class means.

With equal standard deviations:
P(xₐ=-0.5|○) = P(xₐ=-0.5|×)  (same Gaussian shape, same distance)

Therefore:
Posterior(○) ∝ P(xₐ|○) × 0.4
Posterior(×) ∝ P(xₐ|×) × 0.6

Since likelihoods are equal and P(×) > P(○):
Posterior(×) > Posterior(○)

Classification: × (negative class)

Intuition: When equally uncertain from likelihood,
go with higher prior probability."
```

---

### Example 5: K-means Local Minima (Q3)

**(i) Explain local vs global minimum:**

**Answer:**
"The error function E(θ) associates an error value to each candidate model parameterised by θ. 

A **global minimum** is the model θ* that achieves the lowest error amongst ALL candidate models: E(θ*) ≤ E(θ) for all possible θ.

A **local minimum** is a model θ_local that achieves the lowest error within a neighbourhood or vicinity: E(θ_local) ≤ E(θ) for all θ near θ_local, but there may exist other θ elsewhere with E(θ) < E(θ_local).

In visualisation terms, imagine an error surface as a hilly landscape. The global minimum is the deepest valley in the entire terrain, whilst local minima are lower than their immediate surroundings but not the globally lowest point."

**(ii) Explain k-means convergence to local minimum:**

**Answer:**
"The k-means algorithm defines an iterative process that:
1. Assigns each point to its nearest cluster centre
2. Updates cluster centres to the mean of assigned points
3. Repeats until convergence

Each iteration reduces (or maintains) the within-cluster sum of squares error. Since the algorithm only explores solutions accessible from the initial clustering through these local updates, it converges to a local minimum near the starting configuration.

Different random initialisations lead to different local minima. The algorithm has no mechanism to escape a local minimum to search for the global minimum elsewhere in the solution space."

**(iii) Strategy to improve k-means solution:**

**Answer:**
"**Multiple random restarts strategy:**

1. Run k-means algorithm M times (e.g., M=10 or M=50)
2. Each run uses a different random initialisation of cluster centres
3. Let each run converge to its local minimum
4. Calculate the error (within-cluster sum of squares) for each solution
5. Select the solution with the lowest error across all runs

**Rationale:** Since k-means converges to the best local solution near the starting point, exploring multiple diverse starting points increases the probability of finding the global minimum (or a very good local minimum). The computational cost increases linearly with M, but the improvement in solution quality often justifies this cost.

**Advanced variant:** Use k-means++ initialisation (smart seeding) instead of purely random starts to bias towards better starting configurations."

---

### Example 6: Validation Set Approach (Q3b)

**(i) Model selection with validation errors E₁=10, E₂=12:**

**Answer:**
"Model f₁ shows better performance (E₁=10 < E₂=12) on the validation set. In principle, f₁ would be the preferred choice as it demonstrates better deployment performance.

However, this difference could be due to random chance in the specific validation samples used. Before making a final decision, we should:

1. **Assess statistical significance:** Is the difference meaningful or within noise margins?
2. **Consider practical factors:** Model complexity, computational cost, interpretability
3. **If possible, use cross-validation:** Get more robust performance estimates
4. **Check if difference matters:** Is |E₁-E₂|=2 practically significant for the application?

If the difference is statistically and practically significant, select f₁. Otherwise, may consider other factors (simpler model, faster inference, etc.)."

**(ii) Evaluate on training errors instead?**

**Answer:**
"**This suggestion should be rejected entirely.**

Training errors CANNOT be used to assess deployment performance or compare models. Key reasons:

1. **No generalisation assessment:** Training error only measures how well a model fits the specific training samples, not its ability to generalise to new data.

2. **Bias towards overfitting:** More complex models will always achieve lower training error (potentially zero) by memorising training data, even if they perform poorly on new data.

3. **Invalid comparison:** If f₁ is more flexible than f₂, it will have lower training error regardless of true deployment performance. This would lead to selecting overfit models.

4. **Violates ML principles:** The entire purpose of validation/testing is to simulate deployment on unseen data.

**Correct approach with limited data:**
- Use cross-validation (k-fold) to maximise data usage
- Still maintain train/validation separation
- Never conflate training and validation sets"

---

### Example 7: CNN Parameter Counting (Q4b)

**Scenario:**
- Grayscale images: 100×100 pixels
- Layer 1: Convolutional, 2 feature maps of 100×100, filters 3×3
- Layer 2: Max pooling 2×2
- Layer 3: Convolutional, 8 feature maps, filters 3×3×D

**Solutions:**

**(i) Parameters in Layer 1:**
```
Input: 100×100×1 (grayscale = 1 channel)
Output: 100×100×2 (2 feature maps)
Filter size: 3×3

Each filter has:
- Kernel parameters: 3 × 3 × 1 = 9 (width × height × input depth)
- Bias: 1
- Total per filter: 9 + 1 = 10

Number of filters: 2 (one per output feature map)

Total parameters in Layer 1: 2 × 10 = 20

Key insight: Parameters do NOT depend on output size (100×100).
The same 10-parameter filter is applied to all spatial positions (weight sharing).
```

**(ii) Layer 2 (max pooling):**
```
Input: 100×100×2
Pooling: 2×2 max pooling

Output dimensions:
- Width: 100/2 = 50
- Height: 100/2 = 50  
- Depth: 2 (unchanged - pooling doesn't change number of feature maps)

Number of feature maps: 2
Dimensions: 50×50

Trainable parameters: 0 (pooling has no learnable parameters)
```

**(iii) Value of D in Layer 3:**
```
Input: 50×50×2 (output from Layer 2)
Output: 8 feature maps
Filter dimensions: 3×3×D

D represents the DEPTH of the filter, which must match the number
of input feature maps (channels).

Input depth = 2 feature maps
Therefore: D = 2

Each 3×3×2 filter produces one output feature map.
To get 8 output feature maps, we need 8 filters.

Parameters in Layer 3:
- Per filter: (3 × 3 × 2) + 1 = 18 + 1 = 19
- Total: 8 × 19 = 152 parameters
```

**Summary table:**
| Layer | Type | Input | Output | Parameters |
|-------|------|-------|--------|------------|
| 1 | Conv 3×3 | 100×100×1 | 100×100×2 | 20 |
| 2 | MaxPool 2×2 | 100×100×2 | 50×50×2 | 0 |
| 3 | Conv 3×3×2 | 50×50×2 | 48×48×8 | 152 |

---

### Example 8: Train/Validation Split Strategy (Week 3)

**Scenario:** 1000 samples with 70-30 split works well. Dataset increases to 10,000 samples. What split?

**Answer:**
"If 30% of 1,000 samples (300 samples) provides a sufficiently reliable estimate of deployment performance, then we only need 300 samples for validation with the larger dataset.

**Recommended split:** 97-3 (9,700 for training, 300 for validation)

**Reasoning:**
1. **Validation set size:** 300 samples is adequate for reliable performance estimation (already proven with 1,000-sample dataset)
2. **Training set maximisation:** Use remaining 9,700 samples for training
3. **Benefit:** Significantly improved model quality from 9,700 vs 7,000 training samples
4. **Cost:** None - validation reliability unchanged

**Key principle:** Validation set size should be determined by estimation reliability needs, not by fixed percentage. Once adequate validation size is established, allocate remaining data to training.

**Formula:**
If V_min = minimum validation samples needed for reliable estimation,
and N = total samples, then:
- Validation: V_min
- Training: N - V_min
- Split ratio: (N-V_min)/N for training

Example: 10,000 samples, V_min=300
→ Training: 9,700 (97%)
→ Validation: 300 (3%)"

---

## 🔥 Last-Minute Checklist

### Formulas to Memorise

✓ **MMSE solution:** w = (X<sup>T</sup>X)<sup>-1</sup> X<sup>T</sup>y

✓ **MSE:** MSE = (1/N) Σ(yᵢ - ŷᵢ)²

✓ **MAE:** MAE = (1/N) Σ|yᵢ - ŷᵢ|

✓ **Sensitivity:** TP/(TP+FN) — True Positive Rate

✓ **Specificity:** TN/(TN+FP) — True Negative Rate

✓ **Accuracy:** (TP+TN)/(TP+TN+FP+FN)

✓ **Bayes' theorem:** P(A|B) = P(B|A)P(A) / P(B)

✓ **CNN parameters:** M filters × [(K×K×D) + 1]
   - M = number of output feature maps
   - K = kernel size
   - D = number of input feature maps

### Key Concepts in One Sentence

| Concept | One-Liner |
|---------|-----------|
| **Overfitting** | Model memorises training data, performs poorly on new data |
| **Underfitting** | Model too simple to capture true pattern |
| **Bias-Variance** | Trade-off: simple models high bias, complex models high variance |
| **Cross-validation** | Use multiple train/validation splits to get robust performance estimate |
| **Regularisation** | Penalise model complexity to prevent overfitting |
| **Local minimum** | Best solution in a neighbourhood, not globally |
| **MMSE** | Weights that minimise mean squared error on training data |
| **Bayes classifier** | Optimal classifier when probability distributions are known |
| **Confusion matrix** | Table showing TP, FP, TN, FN for classification |
| **Weight sharing (CNN)** | Same filter applied to all positions → fewer parameters |
| **Feature map** | Output of applying a filter across an image |
| **Max pooling** | Downsampling by taking maximum in each region |

### Common Question Patterns

1. **"Obtain MMSE solution"** → Use w = (X<sup>T</sup>X)<sup>-1</sup>X<sup>T</sup>y, show working
2. **"Calculate training MSE"** → Compute predictions, errors, average squared errors
3. **"Explain local minimum"** → Define using error function, contrast with global
4. **"Design a strategy to improve..."** → Propose solution with clear rationale
5. **"How many parameters..."** → Count systematically, include biases
6. **"What would you expect..."** → Use theory (e.g., degree=N-1 gives MSE≈0)
7. **"Identify decision regions"** → Solve w<sup>T</sup>x=0 for boundary, state regions
8. **"Confusion matrix"** → Count TP/FP/TN/FN carefully from data/figure

### British English Spellings

- Favour (not favor)
- Behaviour (not behavior)
- Minimise (not minimize)
- Optimise (not optimize)
- Generalise (not generalize)
- Analyse (not analyze)
- Colour (not color)
- Centre (not center)
- Neighbouring (not neighboring)

---

## 📖 Summary

This reference provides:
- ✅ Practice paper structure and marks distribution
- ✅ Template answers for each major question type
- ✅ Mathematical notation with plain English + Python equivalents
- ✅ Decision flowcharts for model selection and debugging
- ✅ Exam tips: time management, showing working, common pitfalls
- ✅ Worked examples from all solution files
- ✅ Last-minute checklist and key formulas

**How to use during exam:**
1. **Identify question type** using templates section
2. **Follow template structure** to ensure complete answer
3. **Reference notation guide** for mathematical expressions
4. **Check worked examples** for similar problems
5. **Verify against common pitfalls** before moving on
6. **Use decision flowcharts** for conceptual questions

**Remember:**
- Show ALL working for computational questions
- Explain reasoning clearly for conceptual questions
- Check student ID substitutions
- State final answers explicitly
- British English spelling throughout
- Cite any external sources used

**Good luck! 🎓**
