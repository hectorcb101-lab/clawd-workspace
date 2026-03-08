# Machine Learning Theory & Formulas Cheatsheet
**ECS7020P Principles of Machine Learning**  
*Optimised for open-book exam — Quick reference*

---

## 📐 Maths Foundations

### Notation Basics

**Scalars**: Single numerical values (e.g., `a`, `b`, `c` or indexed `a₁, a₂, a₃`)

**Vectors**: 1D arrays of scalars (bold typeface **a**)
```python
import numpy as np
a = np.array([a1, a2, a3])  # Column vector by default
```

**Matrices**: 2D arrays (bold uppercase **A**)
```python
A = np.array([[a11, a12, a13],
              [a21, a22, a23]])  # 2×3 matrix
```

**Shape notation**: N×M means N rows, M columns

---

### Sum and Product Notation

**Sum (Σ)**  
**What this does**: Adds all values from i=1 to i=N

$$\sum_{i=1}^{N} a_i = a_1 + a_2 + \cdots + a_N$$

**Variables**:
- `N` = number of terms
- `aᵢ` = the i-th term
- `i` = index

```python
# Python implementation
a = np.array([a1, a2, a3, ..., aN])
result = np.sum(a)  # or a.sum()
```

---

**Product (Π)**  
**What this does**: Multiplies all values from i=1 to i=N

$$\prod_{i=1}^{N} a_i = a_1 \times a_2 \times \cdots \times a_N$$

```python
# Python implementation
a = np.array([a1, a2, a3, ..., aN])
result = np.prod(a)  # or a.prod()
```

---

**Linear Combination**  
**What this does**: Weighted sum of values

$$\sum_{i=1}^{N} b_i a_i = b_1 a_1 + b_2 a_2 + \cdots + b_N a_N$$

**Variables**:
- `aᵢ` = values to combine
- `bᵢ` = weights

```python
a = np.array([a1, a2, ..., aN])
b = np.array([b1, b2, ..., bN])
result = np.dot(b, a)  # or (b * a).sum()
```

---

### Matrix Operations

**Transpose (Aᵀ)**  
**What this does**: Flips rows ↔ columns

**Variables**:
- `A` = original N×M matrix
- `Aᵀ` = transposed M×N matrix

```python
A = np.array([[1, 4],
              [5, 6],
              [0, 3]])  # 3×2
AT = A.T               # 2×3
```

**Tip**: For vector `x` (N×1), `xᵀ` becomes (1×N) row vector

---

**Matrix Addition**  
**What this does**: Adds corresponding elements (element-wise)

$$C = A + B \quad \text{where} \quad c_{i,j} = a_{i,j} + b_{i,j}$$

**Constraint**: A and B must have **same shape**

```python
A = np.array([[1, 4], [5, 6]])
B = np.array([[2, 0], [-1, 2]])
C = A + B  # [[3, 4], [4, 8]]
```

---

**Scalar Multiplication**  
**What this does**: Multiplies every element by scalar b

$$C = b \times A \quad \text{where} \quad c_{i,j} = b \times a_{i,j}$$

```python
b = 3
A = np.array([[1, 2], [3, 4]])
C = b * A  # [[3, 6], [9, 12]]
```

---

**Matrix Multiplication (AB)**  
**What this does**: Linear transformation; each element is a dot product of row×column

$$c_{i,j} = \sum_k a_{i,k} b_{k,j}$$

**Variables**:
- `A` = N×P matrix
- `B` = P×M matrix
- `C = AB` = N×M matrix
- `cᵢⱼ` = dot product of i-th row of A and j-th column of B

**Constraint**: #columns in A must equal #rows in B

```python
A = np.array([[1, 2, 3],
              [4, 5, 6]])     # 2×3
B = np.array([[7, 8],
              [9, 10],
              [11, 12]])       # 3×2
C = np.dot(A, B)  # or A @ B  # 2×2
# C[0,0] = 1*7 + 2*9 + 3*11 = 58
```

**Common mistake**: AB ≠ BA (non-commutative)

---

**Matrix Inverse (A⁻¹)**  
**What this does**: Finds the matrix that "undoes" A

$$A^{-1} A = A A^{-1} = I$$

**Variables**:
- `A` = square matrix (N×N)
- `A⁻¹` = inverse matrix
- `I` = identity matrix (1s on diagonal, 0s elsewhere)

**Constraint**: Only square matrices with linearly independent columns have inverses

```python
A = np.array([[4, 7], [2, 6]])
A_inv = np.linalg.inv(A)
# Check: A @ A_inv ≈ I
I = np.eye(2)  # 2×2 identity
```

**Watch out for**: Singular matrices (determinant = 0) have no inverse

---

### Linear Functions (Lines, Planes, Hyperplanes)

**Straight Line (1 predictor)**  
**What this does**: Maps x to y using slope and intercept

$$y = w_0 + w_1 x$$

**Variables**:
- `w₀` = intercept (y-value when x=0)
- `w₁` = slope (gradient)
- `x` = independent variable
- `y` = dependent variable

```python
w0, w1 = 2, 0.5
x = np.linspace(0, 10, 100)
y = w0 + w1 * x
```

---

**Plane (2 predictors)**  
**What this does**: Maps two inputs (x₁, x₂) to one output y

$$y = w_0 + w_1 x_1 + w_2 x_2$$

```python
w0, w1, w2 = 1, 0.5, -0.3
x1, x2 = 2, 3
y = w0 + w1*x1 + w2*x2
```

---

**Hyperplane (P predictors) — Vector Notation**  
**What this does**: General linear mapping from P inputs to 1 output

$$y = \mathbf{w}^T \mathbf{x} = w_0 + w_1 x_1 + \cdots + w_P x_P$$

**Variables**:
- `w = [w₀, w₁, ..., wₚ]ᵀ` = weight vector (P+1 elements)
- `x = [1, x₁, ..., xₚ]ᵀ` = extended predictor vector (prepend 1 for intercept)
- `y` = predicted value

```python
w = np.array([w0, w1, w2, ..., wP])  # weights
x = np.array([1, x1, x2, ..., xP])   # extended predictors
y = np.dot(w, x)  # or w @ x
```

**Alternative form** (boundary): `xᵀw = 0` defines points on the hyperplane

---

### Probability Basics

**Random Variable**: Variable that takes values randomly (discrete or continuous)

**Event**: Set of possible values

**Probability P(x)**  
**What this does**: Quantifies likelihood of event x
- `P(x) = 1` → certain
- `P(x) = 0` → impossible
- `0 < P(x) < 1` → uncertain

---

**Joint Probability P(x, y)**  
**What this does**: Probability that both x AND y occur

```python
# Example: rolling two dice
# P(x=6, y=6) = 1/36
```

---

**Conditional Probability P(x|y)**  
**What this does**: Probability of x GIVEN that y has occurred

$$P(x|y) = \frac{P(x, y)}{P(y)}$$

---

**Bayes' Theorem**  
**What this does**: Reverses conditional probabilities (from P(y|x) to P(x|y))

$$P(x|y) = \frac{P(y|x) P(x)}{P(y)}$$

**Variables**:
- `P(x)` = prior probability of x
- `P(y|x)` = likelihood of y given x
- `P(x|y)` = posterior probability of x given y
- `P(y)` = marginal probability of y (normalisation)

```python
# Example: Disease diagnosis
# P(disease|positive_test) = P(positive|disease) * P(disease) / P(positive)
P_disease = 0.01  # prior
P_positive_given_disease = 0.95  # sensitivity
P_positive = 0.05  # marginal
P_disease_given_positive = (P_positive_given_disease * P_disease) / P_positive
```

---

**Gaussian (Normal) Distribution**  
**What this does**: Bell-curve probability density (most data near mean µ)

$$\mathcal{N}(x; \mu, \sigma) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

**Variables**:
- `x` = value
- `µ` = mean (centre)
- `σ` = standard deviation (spread)
- `σ²` = variance

```python
from scipy.stats import norm
mu, sigma = 0, 1
x = np.linspace(-3, 3, 100)
pdf = norm.pdf(x, mu, sigma)  # probability density

# Generate samples
samples = norm.rvs(mu, sigma, size=1000)
```

**Tip**: ~68% of data within µ±σ, ~95% within µ±2σ, ~99.7% within µ±3σ

---

## 📊 Week 1: Introduction to Machine Learning

### Key Concepts

**Machine Learning Definition**  
A set of tools + methodology for solving problems using data.

**Two stages**:
1. **Learning** (training): Build model from dataset
2. **Deployment**: Use model for predictions/insights

---

### ML Taxonomy

```
Machine Learning
├── Supervised
│   ├── Classification (discrete labels)
│   └── Regression (continuous labels)
└── Unsupervised
    ├── Structure Discovery (clustering, basis discovery)
    └── Density Estimation (probability models)
```

**Supervised**: Predict label y from predictors x using labelled dataset  
**Unsupervised**: Find structure in data without labels

---

### Dataset Notation

**Dataset**: Collection of N samples (items), each with K predictors + 1 label

**Notation**:
- `N` = number of samples
- `K` = number of predictors (features)
- `i` = sample index (1 ≤ i ≤ N)
- `xᵢ` = predictor(s) for sample i
- `yᵢ` = true label for sample i
- `(xᵢ, yᵢ)` = labelled sample i

**Design matrix X** (N×(K+1)):
```
X = [ 1  x₁,₁  x₁,₂  ...  x₁,K ]
    [ 1  x₂,₁  x₂,₂  ...  x₂,K ]
    [ ⋮   ⋮     ⋮    ⋱    ⋮   ]
    [ 1  xₙ,₁  xₙ,₂  ...  xₙ,K ]
```
First column is 1s (for intercept w₀)

**Label vector y** (N×1):
```
y = [y₁, y₂, ..., yₙ]ᵀ
```

```python
# Example: Age & Salary dataset
X = np.array([[1, 18, 175],   # [1, age, height]
              [1, 37, 180],
              [1, 66, 158],
              [1, 25, 168]])  # N=4, K=2
y = np.array([12000, 68000, 80000, 45000])  # salaries
```

**Watch out for**: First column of X is always 1 (for intercept term)

---

### Model Notation

**Model**: Function f(·) that maps predictors to predicted labels

**Variables**:
- `f(·)` = model function
- `ŷᵢ = f(xᵢ)` = predicted label for sample i
- `eᵢ = yᵢ - ŷᵢ` = prediction error for sample i

```python
# Linear model example
def f(x, w):
    return np.dot(w, x)  # w^T x

w = np.array([2, 0.5, -0.1])  # coefficients
xi = np.array([1, 30, 170])   # [1, age, height]
y_hat_i = f(xi, w)            # prediction
```

---

## 📈 Week 2: Regression

### Problem Formulation

**Goal**: Predict continuous label y from predictors x

**Model**: `ŷ = f(x)`  
**Error**: `e = y - ŷ` (embrace the error!)

---

### Quality Metrics

**Sum of Squared Errors (SSE)**  
**What this does**: Total squared error across all samples

$$E_{SSE} = \sum_{i=1}^{N} e_i^2 = \sum_{i=1}^{N} (y_i - \hat{y}_i)^2$$

**Variables**:
- `eᵢ` = error for sample i
- `N` = number of samples

```python
y = np.array([12000, 68000, 80000, 45000])
y_hat = np.array([15000, 65000, 75000, 50000])
errors = y - y_hat
SSE = np.sum(errors**2)
# or: SSE = np.sum((y - y_hat)**2)
```

---

**Mean Squared Error (MSE)**  
**What this does**: Average squared error (penalises large errors more than MAE)

$$E_{MSE} = \frac{1}{N} \sum_{i=1}^{N} e_i^2 = \frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2$$

```python
MSE = np.mean((y - y_hat)**2)
# or: MSE = SSE / len(y)
```

**Common use**: Training objective (minimise MSE)

---

**Root Mean Squared Error (RMSE)**  
**What this does**: Square root of MSE (same units as label, interpretable)

$$E_{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} e_i^2}$$

```python
RMSE = np.sqrt(MSE)
# or: RMSE = np.sqrt(np.mean((y - y_hat)**2))
```

**Tip**: RMSE measures sample standard deviation of prediction error

---

**Mean Absolute Error (MAE)**  
**What this does**: Average absolute error (less sensitive to outliers than MSE)

$$E_{MAE} = \frac{1}{N} \sum_{i=1}^{N} |e_i| = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$

```python
MAE = np.mean(np.abs(y - y_hat))
```

---

**R-squared (R²)**  
**What this does**: Proportion of variance explained by model (1 = perfect, 0 = useless)

$$R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}$$

**Variables**:
- `ȳ = (1/N) Σyᵢ` = mean of true labels
- Numerator = residual sum of squares (RSS)
- Denominator = total sum of squares (TSS)

```python
y_mean = np.mean(y)
RSS = np.sum((y - y_hat)**2)
TSS = np.sum((y - y_mean)**2)
R_squared = 1 - (RSS / TSS)

# Or use sklearn:
from sklearn.metrics import r2_score
R_squared = r2_score(y, y_hat)
```

**Watch out for**: R² can be negative for bad models!

---

### Simple Linear Regression

**Model**: Straight line with 2 parameters

$$f(x) = w_0 + w_1 x$$

**Variables**:
- `w₀` = intercept
- `w₁` = slope (gradient)

```python
# Manual implementation
w0, w1 = 1000, 500  # example coefficients
x = np.array([18, 37, 66, 25])  # ages
y_hat = w0 + w1 * x

# Using sklearn
from sklearn.linear_model import LinearRegression
X = x.reshape(-1, 1)  # must be 2D
model = LinearRegression()
model.fit(X, y)
w0, w1 = model.intercept_, model.coef_[0]
y_hat = model.predict(X)
```

---

### Polynomial Regression

**Model**: Polynomial of degree D

$$f(x) = w_0 + w_1 x + w_2 x^2 + \cdots + w_D x^D$$

**Variables**:
- `D` = degree (hyperparameter)
- `w₀, w₁, ..., wᴅ` = coefficients (D+1 parameters)

**Degrees of freedom**: D+1

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Degree D=3 (cubic)
D = 3
x = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
y = np.array([2, 4, 5, 4, 5])

poly = PolynomialFeatures(degree=D)
X_poly = poly.fit_transform(x)  # [1, x, x², x³]
model = LinearRegression()
model.fit(X_poly, y)
y_hat = model.predict(X_poly)

# Coefficients
w = np.concatenate([[model.intercept_], model.coef_[1:]])
# w = [w0, w1, w2, w3]
```

**Tip**: Treat xᵏ as separate predictors for least squares

---

### Multiple Linear Regression

**Model**: Linear combination of K predictors

$$\hat{y}_i = \mathbf{w}^T \mathbf{x}_i = w_0 + w_1 x_{i,1} + \cdots + w_K x_{i,K}$$

**Matrix form**:
$$\hat{\mathbf{y}} = \mathbf{X} \mathbf{w}$$

**Variables**:
- `w = [w₀, w₁, ..., wₖ]ᵀ` = coefficient vector ((K+1)×1)
- `xᵢ = [1, xᵢ,₁, ..., xᵢ,ₖ]ᵀ` = extended predictor vector for sample i
- `X` = design matrix (N×(K+1))
- `ŷ` = predicted label vector (N×1)

```python
# Example: age + height → salary
X = np.array([[1, 18, 175],  # [1, age, height]
              [1, 37, 180],
              [1, 66, 158],
              [1, 25, 168]])
y = np.array([12000, 68000, 80000, 45000])

# Manual: w = (X^T X)^(-1) X^T y (see below)
w = np.linalg.inv(X.T @ X) @ X.T @ y
y_hat = X @ w

# Using sklearn (no need to add 1s column)
from sklearn.linear_model import LinearRegression
X_no_intercept = X[:, 1:]  # drop first column
model = LinearRegression()
model.fit(X_no_intercept, y)
y_hat = model.predict(X_no_intercept)
```

---

### Least Squares Solution (Analytical)

**What this does**: Finds optimal weights that minimise MSE on training data

$$\mathbf{w}_{best} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

**Variables**:
- `X` = design matrix (N×(K+1))
- `y` = label vector (N×1)
- `w_best` = optimal weights ((K+1)×1)

**Constraint**: Columns of X must be linearly independent (for inverse to exist)

```python
X = np.array([[1, 18, 175],
              [1, 37, 180],
              [1, 66, 158],
              [1, 25, 168]])
y = np.array([12000, 68000, 80000, 45000])

# Compute w_best
XTX = X.T @ X
XTX_inv = np.linalg.inv(XTX)
XTy = X.T @ y
w_best = XTX_inv @ XTy

# Or in one line:
w_best = np.linalg.inv(X.T @ X) @ X.T @ y

# Predictions
y_hat = X @ w_best
```

**Watch out for**: Singular matrix error if columns of X are linearly dependent

---

### Flexibility, Underfitting, Overfitting

**Flexibility**: Model's ability to fit different shapes
- **Low flexibility** (rigid): Simple models (e.g., linear)
- **High flexibility**: Complex models (e.g., high-degree polynomial)

**Degrees of freedom**: Number of parameters (≈ flexibility)

---

**Underfitting**  
**What this means**: Model too simple to capture underlying pattern
- **High training error**
- **High deployment (test) error**
- Model is too rigid

**Example**: Linear model for non-linear data

```
Training MSE: 0.98 ← large
Test MSE: 1.02     ← large
```

**Fix**: Increase model complexity (higher degree, more features)

---

**Overfitting**  
**What this means**: Model memorises noise instead of pattern
- **Low training error**
- **High deployment (test) error**
- Model is too flexible for amount of data

**Example**: Degree-15 polynomial on 20 samples

```
Training MSE: 0.001 ← tiny
Test MSE: 5.23      ← huge!
```

**Fix**: 
- Reduce model complexity
- Get more training data
- Regularisation (not covered yet)

---

**Just Right**  
- **Low training error**
- **Low test error**
- Model captures pattern, ignores noise

```
Training MSE: 0.12
Test MSE: 0.15
```

**Common mistake**: Judging model only by training error (need test set!)

---

### Interpretability

**Trade-off**: Flexibility ↔ Interpretability

**High interpretability** (linear model):
> "For every extra year of age, salary increases by £500"

**Low interpretability** (degree-10 polynomial):
> "Salary follows a complex non-linear pattern..."

---

## 🔬 Week 3: Methodology I

### The Three Datasets

**Test Dataset**  
**Purpose**: Estimate deployment quality (true performance)
- **NEVER use for training**
- **Use only ONCE** on final model
- Provides estimate of true error (random quantity)

```python
from sklearn.model_selection import train_test_split

# Split: 80% train+val, 20% test
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

---

**Training Dataset**  
**Purpose**: Tune model parameters (fit model)
- Compute empirical error surface
- Run gradient descent or analytical solution

```python
# Further split temp into train and validation
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42  # 0.25 * 0.8 = 0.2
)
# Now: 60% train, 20% val, 20% test
```

---

**Validation Dataset**  
**Purpose**: Compare model families, select hyperparameters
- Evaluate different model architectures
- Choose degree D, k for kNN, etc.
- Can use same data for training final model after selection

**Common mistake**: Using test data for validation → inflated performance

---

### Sampling & IID Data

**IID = Independent and Identically Distributed**

**Requirements for representative dataset**:
1. Samples extracted **randomly**
2. Samples extracted **independently**
3. All samples from **same population** (identically distributed)
4. **Sufficiently large** sample size

**Watch out for**: Selection bias (e.g., 1936 Literary Digest Poll)

---

### Optimisation Concepts

**Error Surface E(w)**  
**What this is**: Maps each candidate model w to its error
- Also called: objective function, loss function, cost function

**Optimal model**: w* where E(w*) is minimum

**Gradient ∇E(w)**  
**What this is**: Vector pointing in direction of steepest increase of E
- At optimal model: ∇E(w*) = 0

---

### Gradient Descent

**What this does**: Iteratively updates model parameters to minimise error

**Update rule**:
$$\mathbf{w}_{new} = \mathbf{w}_{old} - \eta \nabla E(\mathbf{w}_{old})$$

**Variables**:
- `η` (eta) = learning rate (step size)
- `∇E(w)` = gradient of error at current w
- `w_old` = current parameters
- `w_new` = updated parameters

```python
def gradient_descent(X, y, lr=0.01, n_iterations=1000):
    N, K = X.shape
    w = np.zeros(K)  # initialise weights
    
    for iteration in range(n_iterations):
        # Predictions
        y_hat = X @ w
        
        # Gradient of MSE: ∇E = -(2/N) X^T (y - ŷ)
        gradient = -(2/N) * X.T @ (y - y_hat)
        
        # Update
        w = w - lr * gradient
    
    return w

# Usage
w_optimal = gradient_descent(X_train, y_train, lr=0.01, n_iterations=1000)
```

---

**Learning Rate η**

**Too small**: Slow convergence (many iterations needed)
```python
lr = 0.0001  # might need 100,000 iterations
```

**Too large**: Overshooting, oscillation, divergence
```python
lr = 10  # might never converge
```

**Just right**: Fast convergence to optimum
```python
lr = 0.01  # typical value, tune as needed
```

**Tip**: Try values like 0.001, 0.01, 0.1, 1.0 and monitor error curve

---

**Stopping Criteria**

1. **Fixed iterations**: Stop after N iterations
```python
for i in range(1000):
    ...
```

2. **Time limit**: Stop after T seconds
```python
import time
start = time.time()
while time.time() - start < 60:  # 60 seconds
    ...
```

3. **Error threshold**: Stop when E(w) < threshold
```python
while MSE > 0.01:
    ...
```

4. **Relative change**: Stop when error change is tiny
```python
while abs(MSE_new - MSE_old) > 1e-6:
    ...
```

---

**Local vs Global Optima**

**Convex error surface**: One global minimum (gradient descent works well)

**Non-convex error surface**: Multiple local minima
- Gradient descent can get stuck in local optimum
- **Solution**: Run multiple times from different random initialisations
- Pick model with lowest final error

```python
best_w = None
best_error = float('inf')

for trial in range(10):  # 10 random starts
    w_init = np.random.randn(K) * 0.01
    w = gradient_descent(X, y, w_init=w_init)
    error = compute_error(X, y, w)
    
    if error < best_error:
        best_error = error
        best_w = w
```

---

### Batch Gradient Descent

**What this does**: Estimate gradient using subset (batch) of training data

**Variables**:
- Batch size = number of samples used per iteration
- Epoch = one pass through entire training set

**Trade-off**:
- **Large batch** (full dataset): Accurate gradient, slow per iteration
- **Small batch**: Noisy gradient, fast per iteration, better generalisation

```python
def batch_gradient_descent(X, y, batch_size=32, lr=0.01, n_epochs=100):
    N, K = X.shape
    w = np.zeros(K)
    
    for epoch in range(n_epochs):
        # Shuffle data
        indices = np.random.permutation(N)
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        # Process in batches
        for i in range(0, N, batch_size):
            X_batch = X_shuffled[i:i+batch_size]
            y_batch = y_shuffled[i:i+batch_size]
            
            # Compute gradient on batch
            y_hat_batch = X_batch @ w
            gradient = -(2/batch_size) * X_batch.T @ (y_batch - y_hat_batch)
            
            # Update
            w = w - lr * gradient
    
    return w
```

**Tip**: Common batch sizes: 32, 64, 128, 256

---

### Validation Approaches

**Purpose**: Select best model family/hyperparameters before final training

---

**Validation Set Approach**  
**What this does**: Single split into train & validation

**Pros**: Simple, fast (one training round)  
**Cons**: High variance, wastes data (small training set)

```python
from sklearn.model_selection import train_test_split

# Try different polynomial degrees
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

best_degree = None
best_val_error = float('inf')

for D in range(1, 11):  # degrees 1-10
    model = fit_polynomial(X_train, y_train, degree=D)
    val_error = compute_MSE(X_val, y_val, model)
    
    if val_error < best_val_error:
        best_val_error = val_error
        best_degree = D

print(f"Best degree: {best_degree}")
```

---

**K-Fold Cross-Validation**  
**What this does**: Split data into K folds, train K times (each fold as validation once)

**Pros**: Lower variance, uses all data for both training & validation  
**Cons**: K times more computation

**Common values**: K=5 or K=10

```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)

for D in range(1, 11):  # try degrees 1-10
    fold_errors = []
    
    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = fit_polynomial(X_train, y_train, degree=D)
        val_error = compute_MSE(X_val, y_val, model)
        fold_errors.append(val_error)
    
    avg_error = np.mean(fold_errors)
    print(f"Degree {D}: CV error = {avg_error:.4f}")
```

---

**Leave-One-Out Cross-Validation (LOOCV)**  
**What this does**: K-fold with K=N (one sample as validation each time)

**Pros**: 
- Least bias (almost all data for training)
- Deterministic (no randomness in splits)

**Cons**: 
- Very expensive (N training rounds)
- High variance

```python
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()

for D in range(1, 11):
    errors = []
    
    for train_idx, val_idx in loo.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = fit_polynomial(X_train, y_train, degree=D)
        error = (y_val - model.predict(X_val))**2
        errors.append(error[0])
    
    loocv_error = np.mean(errors)
    print(f"Degree {D}: LOOCV error = {loocv_error:.4f}")
```

**Tip**: LOOCV = K-fold with K=N

---

### Complete ML Methodology

```python
# 1. Split: test set aside (NEVER touch until end)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 2. Validation: select hyperparameters using k-fold CV
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

best_degree = None
best_cv_score = -float('inf')

for D in range(1, 11):
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=D)),
        ('linear', LinearRegression())
    ])
    
    # 5-fold CV on X_temp (train+val)
    cv_scores = cross_val_score(model, X_temp, y_temp, 
                                 cv=5, scoring='neg_mean_squared_error')
    avg_cv_score = np.mean(cv_scores)
    
    if avg_cv_score > best_cv_score:
        best_cv_score = avg_cv_score
        best_degree = D

print(f"Selected degree: {best_degree}")

# 3. Train final model on ALL temp data (train+val)
final_model = Pipeline([
    ('poly', PolynomialFeatures(degree=best_degree)),
    ('linear', LinearRegression())
])
final_model.fit(X_temp, y_temp)

# 4. Test ONCE on held-out test set
test_mse = mean_squared_error(y_test, final_model.predict(X_test))
print(f"Final test MSE: {test_mse:.4f}")
```

**Critical rule**: Test set used exactly ONCE at the very end

---

## 🎯 Week 4: Classification I

### Problem Formulation

**Goal**: Predict discrete label (class) y from predictors x

**Classes**:
- **Binary**: 2 classes (e.g., spam/not spam, 0/1)
- **Multiclass**: >2 classes (e.g., digits 0-9, cat/dog/bird)

**Model**: `ŷ = f(x)` where ŷ ∈ {class labels}

---

### Decision Regions & Boundaries

**Decision region**: Area in predictor space mapped to same class

**Decision boundary**: Line/surface separating decision regions

**Linear boundary**: Defined by `wᵀx = 0`

```python
# 2D example: boundary is line w0 + w1*x1 + w2*x2 = 0
w = np.array([1, 0.5, -0.3])  # [w0, w1, w2]

# Point [x1, x2] = [2, 3]
x = np.array([1, 2, 3])  # extended [1, x1, x2]
decision_value = w @ x

if decision_value > 0:
    y_hat = "Class A"
elif decision_value < 0:
    y_hat = "Class B"
else:
    # On boundary
    y_hat = "Uncertain"
```

---

### Classification Quality Metrics

**Accuracy (Â)**  
**What this does**: Proportion of correct predictions

$$\hat{A} = \frac{\text{# correct predictions}}{N}$$

```python
y_true = np.array([0, 1, 1, 0, 1])
y_pred = np.array([0, 1, 0, 0, 1])

accuracy = np.mean(y_true == y_pred)  # 0.8 (4/5)

# Or use sklearn
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_true, y_pred)
```

---

**Error Rate (Ê)**  
**What this does**: Proportion of incorrect predictions

$$\hat{E} = \frac{\text{# incorrect predictions}}{N} = 1 - \hat{A}$$

```python
error_rate = 1 - accuracy  # 0.2
# Or:
error_rate = np.mean(y_true != y_pred)
```

---

**Confusion Matrix** (binary classification)

```
                Predicted
              Negative  Positive
Actual Neg       TN        FP      ← FP = False Positive
Actual Pos       FN        TP      ← FN = False Negative
                 ↑         ↑
                TN=True   TP=True
                Negative  Positive
```

```python
from sklearn.metrics import confusion_matrix

y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
y_pred = np.array([0, 1, 1, 0, 1, 0, 1, 0])

cm = confusion_matrix(y_true, y_pred)
# cm = [[3, 1],   ← Row 0: actual class 0 (TN=3, FP=1)
#       [1, 3]]   ← Row 1: actual class 1 (FN=1, TP=3)

TN, FP, FN, TP = cm.ravel()
print(f"TN={TN}, FP={FP}, FN={FN}, TP={TP}")
```

---

### Linear Classifiers

**Binary Linear Classifier**  
**What this does**: Separates classes using linear boundary

**Decision rule**:
$$\text{if } \mathbf{w}^T \mathbf{x} > 0 \rightarrow \text{Class } \circ$$
$$\text{if } \mathbf{w}^T \mathbf{x} < 0 \rightarrow \text{Class } \bullet$$

**Variables**:
- `w = [w₀, w₁, ..., wₖ]ᵀ` = boundary coefficients
- `x = [1, x₁, ..., xₖ]ᵀ` = extended predictors

```python
def linear_classifier_predict(X, w):
    """
    X: (N, K+1) design matrix (includes 1s column)
    w: (K+1,) weight vector
    Returns: (N,) array of predictions (0 or 1)
    """
    decision_values = X @ w
    predictions = (decision_values > 0).astype(int)
    return predictions

# Example
w = np.array([1, 0.5, -0.3])  # learned weights
X = np.array([[1, 2, 3],      # sample 1
              [1, 5, 1],       # sample 2
              [1, 1, 4]])      # sample 3
y_pred = linear_classifier_predict(X, w)
```

---

**Linearly Separable**  
Dataset is linearly separable if ∃ linear boundary with 100% accuracy (error = 0)

**Linearly Non-Separable**  
No linear boundary achieves 100% accuracy (error > 0)

**Tip**: Most real-world data is non-separable

---

### Logistic Regression

**Motivation**: Not all predictions are equal — samples far from boundary are more certain

**Distance from Boundary**:
$$d_i = \mathbf{w}^T \mathbf{x}_i$$

- Large positive d → confidently class ○
- Large negative d → confidently class ●
- d ≈ 0 → uncertain (near boundary)

---

**Logistic Function**  
**What this does**: Maps distance to probability (certainty) in [0, 1]

$$p(d) = \frac{1}{1 + e^{-d}} = \frac{e^d}{1 + e^d}$$

**Properties**:
- `p(0) = 0.5` (on boundary)
- `p(d) → 1` as `d → ∞`
- `p(d) → 0` as `d → -∞`

```python
def logistic(d):
    return 1 / (1 + np.exp(-d))

# Or use scipy
from scipy.special import expit
p = expit(d)  # same as logistic(d), numerically stable

# Example
d_values = np.array([-2, -1, 0, 1, 2])
p_values = logistic(d_values)
# p ≈ [0.12, 0.27, 0.5, 0.73, 0.88]
```

---

**Logistic Model for Classification**

For sample i with distance `dᵢ = wᵀxᵢ`:
$$p(\mathbf{x}_i) = \frac{1}{1 + e^{-\mathbf{w}^T \mathbf{x}_i}}$$

**Interpretation** (binary: ○ if wᵀx > 0, ● if wᵀx < 0):
- `p(xᵢ)` = certainty that sample i is class ○
- `1 - p(xᵢ)` = certainty that sample i is class ●

```python
def predict_proba_logistic(X, w):
    """
    X: (N, K+1) design matrix
    w: (K+1,) weights
    Returns: (N,) array of probabilities for class 1
    """
    d = X @ w
    probs = 1 / (1 + np.exp(-d))
    return probs

# Binary predictions (threshold at 0.5)
def predict_logistic(X, w):
    probs = predict_proba_logistic(X, w)
    return (probs > 0.5).astype(int)
```

---

**Likelihood Function L(w)**  
**What this does**: Measures total certainty of classifier on dataset

$$L(\mathbf{w}) = \prod_{y_i = \bullet} (1 - p(\mathbf{x}_i)) \times \prod_{y_i = \circ} p(\mathbf{x}_i)$$

**Variables**:
- Product over all samples
- For class ●: multiply (1 - p)
- For class ○: multiply p

**Goal**: Find w that maximises L(w)

---

**Log-Likelihood ℓ(w)**  
**What this does**: Log of likelihood (easier to optimise, same maximum)

$$\ell(\mathbf{w}) = \sum_{y_i = \bullet} \log(1 - p(\mathbf{x}_i)) + \sum_{y_i = \circ} \log p(\mathbf{x}_i)$$

```python
def log_likelihood(X, y, w):
    """
    X: (N, K+1) design matrix
    y: (N,) labels (0 or 1)
    w: (K+1,) weights
    Returns: log-likelihood value
    """
    p = predict_proba_logistic(X, w)
    
    # Avoid log(0) with clipping
    p = np.clip(p, 1e-15, 1 - 1e-15)
    
    # Log-likelihood
    ll = np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))
    return ll

# Find w_best by maximising log-likelihood (use gradient descent or sklearn)
```

---

**Training Logistic Regression**

```python
from sklearn.linear_model import LogisticRegression

# Prepare data (NO need to add 1s column with sklearn)
X_train = np.array([[18, 175], [37, 180], [66, 158], [25, 168]])
y_train = np.array([0, 1, 1, 0])

# Train
model = LogisticRegression()
model.fit(X_train, y_train)

# Coefficients
w0 = model.intercept_[0]  # bias
w = model.coef_[0]         # [w1, w2]
print(f"Boundary: {w0} + {w[0]}*x1 + {w[1]}*x2 = 0")

# Predictions
y_pred = model.predict(X_train)
y_proba = model.predict_proba(X_train)  # probabilities
```

---

### k-Nearest Neighbours (kNN)

**What this does**: Classify sample based on majority vote of k nearest neighbours

**Non-parametric**: No explicit boundary equation (but boundary exists implicitly)

**Algorithm**:
1. Given new sample x, compute distance to all training samples
2. Find k closest training samples (neighbours)
3. Count votes: how many neighbours in each class?
4. Assign class with most votes

**Variables**:
- `k` = number of neighbours (hyperparameter)
- Distance metric = usually Euclidean

---

**Euclidean Distance**

$$d(\mathbf{x}_i, \mathbf{x}_j) = \sqrt{\sum_{m=1}^{K} (x_{i,m} - x_{j,m})^2}$$

```python
def euclidean_distance(x1, x2):
    return np.sqrt(np.sum((x1 - x2)**2))

# Vectorised for all pairs
from scipy.spatial.distance import cdist

X_train = np.array([[1, 2], [3, 4], [5, 6]])
x_new = np.array([[2, 3]])

distances = cdist(x_new, X_train, metric='euclidean')
# distances[0] = [1.414, 2.236, 4.243]
```

---

**kNN Algorithm**

```python
from sklearn.neighbors import KNeighborsClassifier

# Training data
X_train = np.array([[1, 2], [2, 3], [3, 1], [6, 5], [7, 7], [8, 6]])
y_train = np.array([0, 0, 0, 1, 1, 1])

# Train kNN with k=3
k = 3
model = KNeighborsClassifier(n_neighbors=k)
model.fit(X_train, y_train)

# Predict new sample
x_new = np.array([[4, 4]])
y_pred = model.predict(x_new)

# Get distances and indices of neighbours
distances, indices = model.kneighbors(x_new)
print(f"Nearest {k} neighbours: indices {indices[0]}, distances {distances[0]}")
print(f"Their labels: {y_train[indices[0]]}")
```

---

**kNN Complexity Trade-off**

**Small k (e.g., k=1)**:
- Complex, wiggly boundaries
- Risk of overfitting (sensitive to noise)
- Low bias, high variance

**Large k (e.g., k=N)**:
- Smooth boundaries
- Risk of underfitting (too simple)
- High bias, low variance

**Optimal k**: Use validation to select

```python
from sklearn.model_selection import cross_val_score

best_k = None
best_score = 0

for k in range(1, 21, 2):  # try odd values 1, 3, 5, ..., 19
    model = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(model, X_train, y_train, cv=5)
    avg_score = np.mean(scores)
    
    print(f"k={k}: CV accuracy = {avg_score:.3f}")
    
    if avg_score > best_score:
        best_score = avg_score
        best_k = k

print(f"\nBest k: {best_k}")
```

**Tip**: Use odd k for binary classification (avoids ties)

---

### Parametric vs Non-Parametric

**Parametric** (e.g., linear classifier, logistic regression):
- Assume boundary shape (linear, quadratic, etc.)
- Learn parameters from data
- Fast prediction (just compute wᵀx)
- Limited flexibility

**Non-parametric** (e.g., kNN):
- No assumed boundary shape
- Store entire training set
- Slow prediction (compute distances to all training samples)
- High flexibility (can fit complex boundaries)

---

## 🔧 Common Mistakes & Tips

### General Tips

✅ **Always split data before doing anything else**
```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
```

✅ **Embrace the error**: `y = ŷ + e` (error is inevitable, noise exists)

✅ **Validation THEN testing**: Use validation to select model, test only once

✅ **Matrix shapes matter**:
- X: (N, K+1) with 1s column
- y: (N,) or (N, 1)
- w: (K+1,) or (K+1, 1)

✅ **Standardise features** for gradient descent & kNN:
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # use same scaler!
```

---

### Common Mistakes

❌ **Using test data for training or validation**
→ Inflated performance estimates

❌ **Forgetting to add intercept column**
```python
# ❌ Wrong:
X = data[:, :-1]

# ✅ Correct:
X = np.column_stack([np.ones(N), data[:, :-1]])
```

❌ **Comparing models only by training error**
→ Can't detect overfitting without test error

❌ **Confusing matrix dimensions**
```python
# ❌ This fails:
y_hat = w @ X  # Wrong order!

# ✅ Correct:
y_hat = X @ w
```

❌ **Not shuffling before k-fold CV**
→ Biased splits if data is ordered

❌ **Using accuracy for imbalanced datasets**
→ 95% accuracy meaningless if 95% of data is one class
→ Use precision, recall, F1-score instead (not covered in lectures yet)

❌ **Singular matrix in least squares**
→ Check for linearly dependent columns (e.g., duplicate features)

---

### Quick Debugging Checks

**Regression**:
```python
# Predictions should be continuous
print(f"y_pred range: [{y_pred.min():.2f}, {y_pred.max():.2f}]")
print(f"y_true range: [{y_true.min():.2f}, {y_true.max():.2f}]")

# MSE should decrease during training
print(f"Training MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")

# R² should be between -∞ and 1 (higher is better)
print(f"R²: {r2:.4f}")
```

**Classification**:
```python
# Predictions should be discrete
print(f"Unique predictions: {np.unique(y_pred)}")
print(f"Unique true labels: {np.unique(y_true)}")

# Accuracy between 0 and 1
print(f"Accuracy: {accuracy:.4f}")

# Class distribution
print(f"Predicted class counts: {np.bincount(y_pred)}")
print(f"True class counts: {np.bincount(y_true)}")
```

---

## 📚 Glossary of Key Terms

| Term | Definition |
|------|------------|
| **Sample** | Single data point (also: instance, example, item) |
| **Feature** | Input variable (also: predictor, attribute, independent variable) |
| **Label** | Output variable (also: target, response, dependent variable) |
| **N** | Number of samples |
| **K** | Number of features |
| **Training** | Fitting model parameters to training data |
| **Testing** | Evaluating model on held-out test data |
| **Validation** | Comparing models to select hyperparameters |
| **Overfitting** | Model memorises noise (low train error, high test error) |
| **Underfitting** | Model too simple (high train error, high test error) |
| **Hyperparameter** | Setting chosen before training (e.g., degree D, k in kNN) |
| **Parameter** | Value learned during training (e.g., weights w) |
| **IID** | Independent and Identically Distributed |
| **Empirical** | Computed on finite dataset (vs. true/population) |
| **Gradient** | Vector of partial derivatives (direction of steepest increase) |
| **Convex** | Function with single global minimum |

---

## 🎓 Exam Strategy

### Quick Lookup Structure

**Given problem, answer these first**:
1. **Supervised or unsupervised?** → Labels present?
2. **Classification or regression?** → Label discrete or continuous?
3. **Which model family?** → Linear, polynomial, kNN?
4. **Which metric?** → MSE/RMSE/R² (regression), Accuracy (classification)
5. **Data split?** → Train/validation/test
6. **Overfitting or underfitting?** → Compare train vs. test error

---

### Formula Lookup by Task

**Need to compute predictions?**
→ `ŷ = Xw` or `ŷ = f(x)`

**Need to compute error?**
→ MSE: `(1/N) Σ(y - ŷ)²`
→ Accuracy: `(# correct) / N`

**Need to find optimal weights analytically?**
→ `w = (XᵀX)⁻¹Xᵀy`

**Need to update weights iteratively?**
→ `w_new = w_old - η∇E(w_old)`

**Need to classify with linear boundary?**
→ If `wᵀx > 0`: class A, else class B

**Need probability from logistic?**
→ `p = 1/(1 + e^(-wᵀx))`

**Need to select hyperparameter?**
→ Use k-fold CV, pick lowest validation error

---

### Matrix Notation Cheatsheet

```
X:     (N × K+1)  design matrix (rows=samples, cols=features+1)
y:     (N × 1)    label vector
w:     (K+1 × 1)  weight vector
ŷ:     (N × 1)    predictions: ŷ = Xw
e:     (N × 1)    errors: e = y - ŷ

Least squares solution:
w = (XᵀX)⁻¹Xᵀy
    └─┬──┘ └┬┘
   (K+1×K+1) (K+1×N)
    inverse
```

---

## ✨ Final Checklist Before Exam

- [ ] Can explain every formula in plain English
- [ ] Can write NumPy code for each formula from memory
- [ ] Understand train/validation/test split purpose
- [ ] Know when to use which quality metric
- [ ] Can identify overfitting vs underfitting from error curves
- [ ] Understand matrix shapes and operations
- [ ] Can classify problem as supervised/unsupervised, regression/classification
- [ ] Know gradient descent update rule
- [ ] Understand least squares analytical solution
- [ ] Can implement kNN algorithm
- [ ] Understand logistic regression likelihood
- [ ] Know k-fold CV procedure

---

**Good luck! Remember**: Understand concepts > memorise formulas. This cheatsheet is for quick reference during exam when you know what you need but just need to confirm the exact notation or code syntax.

**British spelling used throughout**: optimise, generalisation, behaviour, analyse, centre, colour, organisation ✓
