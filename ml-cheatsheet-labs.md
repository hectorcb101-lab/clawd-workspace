# ML Lab Code Patterns Cheatsheet
**MSc Machine Learning Labs - Queen Mary University of London**  
*Copy-paste ready code templates for open-book exams*

---

## Table of Contents
1. [Data Loading & Preprocessing](#data-loading--preprocessing)
2. [Linear Regression](#linear-regression)
3. [Polynomial Regression](#polynomial-regression)
4. [Logistic Regression](#logistic-regression)
5. [K-Nearest Neighbours (KNN)](#k-nearest-neighbours-knn)
6. [Decision Trees](#decision-trees)
7. [Model Evaluation Metrics](#model-evaluation-metrics)
8. [Cross-Validation](#cross-validation)
9. [Feature Scaling & Regularisation](#feature-scaling--regularisation)
10. [Plotting Patterns](#plotting-patterns)
11. [Exam Patterns & Quick Reference](#exam-patterns--quick-reference)

---

## Data Loading & Preprocessing

### Load CSV Data
```python
import pandas as pd
import numpy as np

# Load from CSV
df = pd.read_csv('data.csv')

# Display basic info
print(df.head())
print(df.describe())
print(df.info())
```

### Create NumPy Arrays from Lists
```python
import numpy as np

# From lists
x = np.array([2, 3, 1, 1, 0, 5, 4, 6, 5, 3])
y = np.array([1, 2, 2, 1, 1, 3, 3, 7, 6, 5])

# Reshape for sklearn (n_samples, n_features)
X = x.reshape(-1, 1)  # Column vector
```

### Create Design Matrix (Manual Method)
```python
import numpy as np

# For simple linear regression: y = w0 + w1*x
# Design matrix X includes intercept column
x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
n = len(x)

# Add intercept column
X = np.column_stack([np.ones(n), x])
# X is now [[1, 1],
#           [1, 2],
#           [1, 3], ...]
```

### Train-Test Split
```python
from sklearn.model_selection import train_test_split
import numpy as np

# Standard 70-30 split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Stratified split (for classification - preserves class proportions)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
```

### Handle Missing Values
```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

# Drop rows with missing values
df_clean = df.dropna()

# Fill with mean
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Fill with median or constant
imputer = SimpleImputer(strategy='median')  # or strategy='constant', fill_value=0
```

### Log Transformations
```python
import numpy as np
import pandas as pd

# Apply log10 transformation (useful for data spanning multiple orders of magnitude)
df['log_body_mass'] = np.log10(df['body_mass'])
df['log_heart_rate'] = np.log10(df['heart_rate'])

# Natural log
df['ln_x'] = np.log(df['x'])

# Exponential transformation (reverse of log)
df['exp_x'] = np.exp(df['ln_x'])
```

**Exam Pattern:** Given a dataset with wide value ranges (e.g., body mass from 10g to 10^7g), apply log transformations before fitting linear models to reveal linear relationships.

---

## Linear Regression

### sklearn Linear Regression (Standard Method)
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Create and fit model
model = LinearRegression()
model.fit(X_train, y_train)

# Get coefficients
print(f"Intercept (w0): {model.intercept_}")
print(f"Coefficients (w1, w2, ...): {model.coef_}")

# Make predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Evaluate
train_mse = mean_squared_error(y_train, y_pred_train)
test_mse = mean_squared_error(y_test, y_pred_test)
train_mae = mean_absolute_error(y_train, y_pred_train)
test_mae = mean_absolute_error(y_test, y_pred_test)

print(f"Train MSE: {train_mse:.4f}")
print(f"Test MSE: {test_mse:.4f}")
print(f"Train MAE: {train_mae:.4f}")
print(f"Test MAE: {test_mae:.4f}")

# R² score
print(f"Train R²: {model.score(X_train, y_train):.4f}")
print(f"Test R²: {model.score(X_test, y_test):.4f}")
```

### Normal Equations Method (Manual Implementation)
```python
import numpy as np

# Create design matrix X and label vector y
x = np.array([2, 3, 1, 1, 0, 5, 4, 6, 5, 3])
y = np.array([1, 2, 2, 1, 1, 3, 3, 7, 6, 5])
n = len(x)

# Design matrix with intercept
X = np.column_stack([np.ones(n), x])

# Solve normal equations: w = (X^T X)^(-1) X^T y
XTX = X.T @ X
XTX_inv = np.linalg.inv(XTX)
XTy = X.T @ y
w = XTX_inv @ XTy

print(f"w0 (intercept): {w[0]:.4f}")
print(f"w1 (slope): {w[1]:.4f}")

# Make predictions
y_pred = X @ w

# Calculate MSE manually
errors = y - y_pred
mse = np.mean(errors**2)
mae = np.mean(np.abs(errors))

print(f"MSE: {mse:.4f}")
print(f"MAE: {mae:.4f}")
```

### Multiple Linear Regression
```python
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

# Multiple features
# X should be shape (n_samples, n_features)
X = df[['feature1', 'feature2', 'feature3']].values
y = df['target'].values

# Or create from arrays
X = np.column_stack([x1, x2, x3])

model = LinearRegression()
model.fit(X, y)

print(f"Intercept: {model.intercept_}")
print(f"Coefficients: {model.coef_}")
# Coefficients correspond to each feature in order
```

### Compare Multiple Models
```python
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Define candidate models as functions
def f1(x): return 2*x + 1
def f2(x): return x
def f3(x): return 2*x - 1
def f4(x): return x - 0.5
def f5(x): return x + 0.5

models = [f1, f2, f3, f4, f5]
names = ['f1: 2x+1', 'f2: x', 'f3: 2x-1', 'f4: x-0.5', 'f5: x+0.5']

# Given data
x = np.array([2, 3, 1, 1, 0, 5, 4, 6, 5, 3])
y = np.array([1, 2, 2, 1, 1, 3, 3, 7, 6, 5])

# Evaluate each model
results = []
for model, name in zip(models, names):
    y_pred = model(x)
    mse = mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    results.append({'Model': name, 'MSE': mse, 'MAE': mae})

# Display results
import pandas as pd
df_results = pd.DataFrame(results)
print(df_results)
print(f"\nBest MSE: {df_results.loc[df_results['MSE'].idxmin(), 'Model']}")
print(f"Best MAE: {df_results.loc[df_results['MAE'].idxmin(), 'Model']}")
```

**Exam Pattern:** Given multiple candidate models and a dataset, compute MSE/MAE for each and select the best. Remember: MSE penalises large errors more than MAE.

---

## Polynomial Regression

### Polynomial Regression with sklearn
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import numpy as np

# Data
x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
y = np.array([2.2, 3.5, 3.9, 2.9, 5, 6.2, 3, 4.8])
X = x.reshape(-1, 1)

# Create polynomial pipeline (degree 2)
model_poly2 = Pipeline([
    ('poly', PolynomialFeatures(degree=2)),
    ('linear', LinearRegression())
])

model_poly2.fit(X, y)
y_pred = model_poly2.predict(X)
mse = mean_squared_error(y, y_pred)
print(f"Degree 2 MSE: {mse:.4f}")

# Get coefficients
coefficients = model_poly2.named_steps['linear'].coef_
intercept = model_poly2.named_steps['linear'].intercept_
print(f"Polynomial: {intercept:.4f} + {coefficients[1]:.4f}*x + {coefficients[2]:.4f}*x²")
```

### Compare Multiple Polynomial Degrees
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import numpy as np

x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
y = np.array([2.2, 3.5, 3.9, 2.9, 5, 6.2, 3, 4.8])
X = x.reshape(-1, 1)

degrees = [1, 2, 3, 4, 6]
results = []

for degree in degrees:
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    model.fit(X, y)
    y_pred = model.predict(X)
    train_mse = mean_squared_error(y, y_pred)
    results.append({'Degree': degree, 'Train MSE': train_mse})

import pandas as pd
df_results = pd.DataFrame(results)
print(df_results)
```

### Manual Polynomial Design Matrix
```python
import numpy as np

# For quadratic: y = w0 + w1*x + w2*x²
x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
n = len(x)

# Create design matrix manually
X_linear = np.column_stack([np.ones(n), x])
X_quadratic = np.column_stack([np.ones(n), x, x**2])
X_cubic = np.column_stack([np.ones(n), x, x**2, x**3])

# Solve using normal equations
y = np.array([2.2, 3.5, 3.9, 2.9, 5, 6.2, 3, 4.8])

w_quad = np.linalg.inv(X_quadratic.T @ X_quadratic) @ X_quadratic.T @ y
print(f"Quadratic coefficients: {w_quad}")
# [w0, w1, w2]

y_pred = X_quadratic @ w_quad
mse = np.mean((y - y_pred)**2)
print(f"MSE: {mse:.4f}")
```

### Polynomial Regression with Train/Test Split
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Try different degrees
for degree in [1, 2, 3, 4]:
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    
    model.fit(X_train, y_train)
    
    train_mse = mean_squared_error(y_train, model.predict(X_train))
    test_mse = mean_squared_error(y_test, model.predict(X_test))
    
    print(f"Degree {degree}: Train MSE={train_mse:.4f}, Test MSE={test_mse:.4f}")
```

**Exam Pattern:** When asked about overfitting, show that training MSE decreases with polynomial degree, but test MSE may increase (U-shaped curve). Degree ≥ number of samples → perfect fit on training (MSE=0) but terrible generalisation.

---

## Logistic Regression

### Binary Classification
```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np

# Load data (X: features, y: binary labels 0/1)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Create and fit model
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Probabilities
y_prob_test = model.predict_proba(X_test)
# Returns array of shape (n_samples, 2): [prob_class_0, prob_class_1]

# Evaluate
train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")
print(f"\nCoefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred_test)
print(f"\nConfusion Matrix:\n{cm}")

# Detailed report
print(f"\nClassification Report:\n{classification_report(y_test, y_pred_test)}")
```

### Multi-class Classification
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
import numpy as np

# y has multiple classes (0, 1, 2, ...)
model = LogisticRegression(multi_class='ovr', max_iter=1000, random_state=42)
# 'ovr' = one-vs-rest, 'multinomial' = softmax

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
```

### Logistic Regression with Regularisation
```python
from sklearn.linear_model import LogisticRegression
import numpy as np

# C is inverse of regularisation strength (smaller C = stronger regularisation)
model_l2 = LogisticRegression(penalty='l2', C=1.0, max_iter=1000, random_state=42)
model_l1 = LogisticRegression(penalty='l1', C=1.0, solver='liblinear', max_iter=1000, random_state=42)

model_l2.fit(X_train, y_train)
print(f"L2 Test Accuracy: {model_l2.score(X_test, y_test):.4f}")

model_l1.fit(X_train, y_train)
print(f"L1 Test Accuracy: {model_l1.score(X_test, y_test):.4f}")
```

**Exam Pattern:** For classification problems, use logistic regression (not linear regression). Always report accuracy, confusion matrix, and consider class imbalance (use stratified split).

---

## K-Nearest Neighbours (KNN)

### KNN Classification
```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import numpy as np

# IMPORTANT: Scale features for KNN (distance-based algorithm)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create and fit KNN model
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
```

### KNN Regression
```python
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create and fit model
model = KNeighborsRegressor(n_neighbors=5)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)

# Evaluate
train_mse = mean_squared_error(y_train, y_pred_train)
test_mse = mean_squared_error(y_test, y_pred_test)
print(f"Train MSE: {train_mse:.4f}")
print(f"Test MSE: {test_mse:.4f}")
print(f"Test R²: {r2_score(y_test, y_pred_test):.4f}")
```

### Find Optimal k
```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt

# Scale data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Try different k values
k_values = range(1, 21)
train_scores = []
test_scores = []

for k in k_values:
    model = KNeighborsClassifier(n_neighbors=k)
    
    # Train score
    model.fit(X_train_scaled, y_train)
    train_scores.append(model.score(X_train_scaled, y_train))
    
    # Cross-validation score (better than single test set)
    cv_scores = cross_val_score(model, X_scaled, y, cv=5)
    test_scores.append(cv_scores.mean())

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(k_values, train_scores, label='Train Accuracy', marker='o')
plt.plot(k_values, test_scores, label='CV Accuracy', marker='s')
plt.xlabel('k (Number of Neighbours)')
plt.ylabel('Accuracy')
plt.title('KNN: Choosing Optimal k')
plt.legend()
plt.grid(True)
plt.show()

best_k = k_values[np.argmax(test_scores)]
print(f"Optimal k: {best_k}")
```

**Exam Pattern:** KNN requires feature scaling. Small k → overfitting (high variance), large k → underfitting (high bias). Use cross-validation to find optimal k.

---

## Decision Trees

### Decision Tree Classification
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import numpy as np

# Create and fit model
model = DecisionTreeClassifier(
    max_depth=5,           # Limit depth to prevent overfitting
    min_samples_split=2,   # Minimum samples to split a node
    min_samples_leaf=1,    # Minimum samples in a leaf
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Evaluate
train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

# Feature importance
print(f"Feature Importances: {model.feature_importances_}")
```

### Decision Tree Regression
```python
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

model = DecisionTreeRegressor(max_depth=5, random_state=42)
model.fit(X_train, y_train)

y_pred_test = model.predict(X_test)
print(f"Test MSE: {mean_squared_error(y_test, y_pred_test):.4f}")
print(f"Test R²: {r2_score(y_test, y_pred_test):.4f}")
```

### Tune Tree Depth
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import matplotlib.pyplot as plt

depths = range(1, 21)
train_scores = []
test_scores = []

for depth in depths:
    model = DecisionTreeClassifier(max_depth=depth, random_state=42)
    model.fit(X_train, y_train)
    
    train_scores.append(model.score(X_train, y_train))
    test_scores.append(model.score(X_test, y_test))

# Plot
plt.figure(figsize=(10, 6))
plt.plot(depths, train_scores, label='Train Accuracy', marker='o')
plt.plot(depths, test_scores, label='Test Accuracy', marker='s')
plt.xlabel('Tree Depth')
plt.ylabel('Accuracy')
plt.title('Decision Tree: Effect of Max Depth')
plt.legend()
plt.grid(True)
plt.show()

best_depth = depths[np.argmax(test_scores)]
print(f"Optimal depth: {best_depth}")
```

### Visualise Decision Tree
```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# Plot tree
plt.figure(figsize=(20, 10))
plot_tree(model, 
          feature_names=['feature1', 'feature2'],
          class_names=['Class 0', 'Class 1'],
          filled=True,
          rounded=True,
          fontsize=10)
plt.title('Decision Tree Visualisation')
plt.show()
```

**Exam Pattern:** Decision trees don't require feature scaling. Prone to overfitting without constraints (max_depth, min_samples_split). Use feature_importances_ to identify key features.

---

## Model Evaluation Metrics

### Regression Metrics
```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Predictions vs actual
y_pred = model.predict(X_test)

# Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print(f"MSE: {mse:.4f}")

# Root Mean Squared Error
rmse = np.sqrt(mse)
print(f"RMSE: {rmse:.4f}")

# Mean Absolute Error
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae:.4f}")

# R² Score (coefficient of determination)
r2 = r2_score(y_test, y_pred)
print(f"R²: {r2:.4f}")

# Manual calculation of MSE and MAE
errors = y_test - y_pred
mse_manual = np.mean(errors**2)
mae_manual = np.mean(np.abs(errors))
print(f"MSE (manual): {mse_manual:.4f}")
print(f"MAE (manual): {mae_manual:.4f}")
```

### Classification Metrics
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import numpy as np

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # Probability of positive class

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Precision, Recall, F1 (binary classification)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:\n{cm}")
# [[TN, FP],
#  [FN, TP]]

# Extract components
tn, fp, fn, tp = cm.ravel()
print(f"True Negatives: {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives: {tp}")

# Manual calculation of metrics
accuracy_manual = (tp + tn) / (tp + tn + fp + fn)
precision_manual = tp / (tp + fp) if (tp + fp) > 0 else 0
recall_manual = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_manual = 2 * (precision_manual * recall_manual) / (precision_manual + recall_manual) if (precision_manual + recall_manual) > 0 else 0

print(f"\nManual calculations:")
print(f"Accuracy: {accuracy_manual:.4f}")
print(f"Precision: {precision_manual:.4f}")
print(f"Recall: {recall_manual:.4f}")
print(f"F1: {f1_manual:.4f}")

# ROC-AUC Score
roc_auc = roc_auc_score(y_test, y_prob)
print(f"\nROC-AUC: {roc_auc:.4f}")

# Full classification report
print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
```

### Multi-class Classification Metrics
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np

# For multi-class: use average parameter
precision_macro = precision_score(y_test, y_pred, average='macro')
recall_macro = recall_score(y_test, y_pred, average='macro')
f1_macro = f1_score(y_test, y_pred, average='macro')

precision_weighted = precision_score(y_test, y_pred, average='weighted')
recall_weighted = recall_score(y_test, y_pred, average='weighted')
f1_weighted = f1_score(y_test, y_pred, average='weighted')

print(f"Macro Precision: {precision_macro:.4f}")
print(f"Macro Recall: {recall_macro:.4f}")
print(f"Macro F1: {f1_macro:.4f}")
print(f"\nWeighted Precision: {precision_weighted:.4f}")
print(f"Weighted Recall: {recall_weighted:.4f}")
print(f"Weighted F1: {f1_weighted:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:\n{cm}")
```

**Exam Pattern:** 
- **Regression:** Use MSE (penalises large errors) or MAE (robust to outliers). R² shows proportion of variance explained.
- **Classification:** Accuracy for balanced datasets. For imbalanced: use precision (minimise false positives), recall (minimise false negatives), or F1 (balance both).

---

## Cross-Validation

### k-Fold Cross-Validation
```python
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.linear_model import LinearRegression
import numpy as np

model = LinearRegression()

# Simple cross-validation (returns scores only)
cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
# Note: scoring returns negative MSE, so negate it
cv_mse = -cv_scores
print(f"CV MSE scores: {cv_mse}")
print(f"Mean CV MSE: {cv_mse.mean():.4f}")
print(f"Std CV MSE: {cv_mse.std():.4f}")

# For classification (accuracy)
from sklearn.linear_model import LogisticRegression
model_clf = LogisticRegression(max_iter=1000)
cv_scores_acc = cross_val_score(model_clf, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {cv_scores_acc.mean():.4f} ± {cv_scores_acc.std():.4f}")
```

### Cross-Validation with Multiple Metrics
```python
from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
import numpy as np

model = LogisticRegression(max_iter=1000)

# Multiple scoring metrics
scoring = ['accuracy', 'precision', 'recall', 'f1']
cv_results = cross_validate(model, X, y, cv=5, scoring=scoring, return_train_score=True)

# Display results
for metric in scoring:
    test_scores = cv_results[f'test_{metric}']
    train_scores = cv_results[f'train_{metric}']
    print(f"{metric.capitalize()}:")
    print(f"  Train: {train_scores.mean():.4f} ± {train_scores.std():.4f}")
    print(f"  Test:  {test_scores.mean():.4f} ± {test_scores.std():.4f}")
```

### Stratified k-Fold (Classification)
```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
import numpy as np

# Stratified k-fold preserves class proportions in each fold
model = LogisticRegression(max_iter=1000)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
print(f"Stratified CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
```

### Leave-One-Out Cross-Validation (LOOCV)
```python
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.linear_model import LinearRegression
import numpy as np

model = LinearRegression()
loo = LeaveOneOut()

cv_scores = cross_val_score(model, X, y, cv=loo, scoring='neg_mean_squared_error')
cv_mse = -cv_scores
print(f"LOOCV MSE: {cv_mse.mean():.4f}")
```

### Compare Models with Cross-Validation
```python
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
import numpy as np

# Define models to compare
models = {
    'Linear Regression': LinearRegression(),
    'Ridge (alpha=1)': Ridge(alpha=1.0),
    'Lasso (alpha=1)': Lasso(alpha=1.0),
    'Decision Tree': DecisionTreeRegressor(max_depth=5, random_state=42),
    'KNN (k=5)': KNeighborsRegressor(n_neighbors=5)
}

# Cross-validate each model
results = []
for name, model in models.items():
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    cv_mse = -cv_scores
    results.append({
        'Model': name,
        'Mean CV MSE': cv_mse.mean(),
        'Std CV MSE': cv_mse.std()
    })

# Display results
import pandas as pd
df_results = pd.DataFrame(results).sort_values('Mean CV MSE')
print(df_results)
```

**Exam Pattern:** Use cross-validation to estimate deployment performance when you don't have a separate test set. k=5 or k=10 is standard. For classification with imbalanced classes, use StratifiedKFold.

---

## Feature Scaling & Regularisation

### Feature Scaling
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import numpy as np

# StandardScaler: (x - mean) / std (z-score normalisation)
scaler_standard = StandardScaler()
X_train_scaled = scaler_standard.fit_transform(X_train)
X_test_scaled = scaler_standard.transform(X_test)  # Use training stats

print(f"Mean: {scaler_standard.mean_}")
print(f"Std: {scaler_standard.scale_}")

# MinMaxScaler: scales to [0, 1] range
scaler_minmax = MinMaxScaler()
X_train_minmax = scaler_minmax.fit_transform(X_train)
X_test_minmax = scaler_minmax.transform(X_test)

# RobustScaler: uses median and IQR (robust to outliers)
scaler_robust = RobustScaler()
X_train_robust = scaler_robust.fit_transform(X_train)
X_test_robust = scaler_robust.transform(X_test)
```

### Pipeline with Scaling
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Fit and predict
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")
```

### Ridge Regression (L2 Regularisation)
```python
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
import numpy as np

# alpha controls regularisation strength (higher = more regularisation)
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)

y_pred_test = model.predict(X_test)
test_mse = mean_squared_error(y_test, y_pred_test)

print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
print(f"Test MSE: {test_mse:.4f}")
```

### Lasso Regression (L1 Regularisation)
```python
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
import numpy as np

# L1 regularisation → sparse coefficients (feature selection)
model = Lasso(alpha=0.1, max_iter=10000)
model.fit(X_train, y_train)

y_pred_test = model.predict(X_test)
test_mse = mean_squared_error(y_test, y_pred_test)

print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
print(f"Test MSE: {test_mse:.4f}")
print(f"Number of zero coefficients: {np.sum(model.coef_ == 0)}")
```

### Tune Regularisation Parameter
```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
import numpy as np
import matplotlib.pyplot as plt

# Try different alpha values
alphas = np.logspace(-3, 3, 50)  # 0.001 to 1000
train_scores = []
cv_scores = []

for alpha in alphas:
    model = Ridge(alpha=alpha)
    
    # Train score
    model.fit(X_train, y_train)
    train_scores.append(model.score(X_train, y_train))
    
    # Cross-validation score
    cv_score = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    cv_scores.append(cv_score.mean())

# Plot
plt.figure(figsize=(10, 6))
plt.semilogx(alphas, train_scores, label='Train R²', marker='o')
plt.semilogx(alphas, cv_scores, label='CV R²', marker='s')
plt.xlabel('Alpha (Regularisation Strength)')
plt.ylabel('R² Score')
plt.title('Ridge Regression: Tuning Alpha')
plt.legend()
plt.grid(True)
plt.show()

best_alpha = alphas[np.argmax(cv_scores)]
print(f"Best alpha: {best_alpha:.4f}")
```

### Elastic Net (L1 + L2)
```python
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
import numpy as np

# Combines L1 and L2 regularisation
# l1_ratio: 0=Ridge, 1=Lasso, 0.5=equal mix
model = ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Test MSE: {mean_squared_error(y_test, y_pred):.4f}")
```

**Exam Pattern:** 
- Scale features for distance-based algorithms (KNN, SVM) and regularised models
- Ridge: shrinks coefficients, good for correlated features
- Lasso: sets some coefficients to zero, performs feature selection
- Higher alpha → simpler model → less overfitting

---

## Plotting Patterns

### Scatter Plot with Regression Line
```python
import matplotlib.pyplot as plt
import numpy as np

# Data
x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
y = np.array([2.2, 3.5, 3.9, 2.9, 5, 6.2, 3, 4.8])

# Fit model
from sklearn.linear_model import LinearRegression
X = x.reshape(-1, 1)
model = LinearRegression()
model.fit(X, y)

# Generate smooth line for plotting
x_line = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
y_line = model.predict(x_line)

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='blue', label='Data', s=100, alpha=0.6)
plt.plot(x_line, y_line, color='red', linewidth=2, label=f'y = {model.intercept_:.2f} + {model.coef_[0]:.2f}x')
plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.title('Linear Regression', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Multiple Models on Same Plot
```python
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

x = np.array([1, 2, 3, 5, 7, 8, 2.5, 8])
y = np.array([2.2, 3.5, 3.9, 2.9, 5, 6.2, 3, 4.8])
X = x.reshape(-1, 1)

# Fit different models
models = {}
for degree in [1, 2, 3]:
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    model.fit(X, y)
    models[f'Degree {degree}'] = model

# Plot
x_line = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)

plt.figure(figsize=(12, 6))
plt.scatter(x, y, color='black', label='Data', s=100, zorder=5)

colours = ['red', 'green', 'blue']
for (name, model), colour in zip(models.items(), colours):
    y_line = model.predict(x_line)
    plt.plot(x_line, y_line, color=colour, linewidth=2, label=name)

plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.title('Polynomial Regression Comparison', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Confusion Matrix Heatmap
```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np

# Get confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Class 0', 'Class 1'],
            yticklabels=['Class 0', 'Class 1'],
            cbar_kws={'label': 'Count'})
plt.ylabel('Actual', fontsize=12)
plt.xlabel('Predicted', fontsize=12)
plt.title('Confusion Matrix', fontsize=14)
plt.show()

# Alternative without seaborn
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(cm, cmap='Blues')

# Add text annotations
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        text = ax.text(j, i, cm[i, j], ha='center', va='center', color='black', fontsize=16)

ax.set_xticks(range(cm.shape[1]))
ax.set_yticks(range(cm.shape[0]))
ax.set_xticklabels(['Class 0', 'Class 1'])
ax.set_yticklabels(['Class 0', 'Class 1'])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.colorbar(im)
plt.show()
```

### ROC Curve
```python
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np

# Get predicted probabilities
y_prob = model.predict_proba(X_test)[:, 1]

# Calculate ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = roc_auc_score(y_test, y_prob)

# Plot
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14)
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.show()
```

### Learning Curves
```python
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.linear_model import LogisticRegression
import numpy as np

model = LogisticRegression(max_iter=1000)

# Generate learning curve data
train_sizes, train_scores, val_scores = learning_curve(
    model, X, y, cv=5, n_jobs=-1,
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='accuracy'
)

# Calculate mean and std
train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
val_mean = np.mean(val_scores, axis=1)
val_std = np.std(val_scores, axis=1)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, 'o-', color='r', label='Training score')
plt.plot(train_sizes, val_mean, 'o-', color='g', label='Cross-validation score')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='r')
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='g')
plt.xlabel('Training Set Size', fontsize=12)
plt.ylabel('Accuracy', fontsize=12)
plt.title('Learning Curves', fontsize=14)
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.show()
```

### Decision Boundary (2D Classification)
```python
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression

# Assumes X has 2 features
model = LogisticRegression()
model.fit(X_train, y_train)

# Create mesh grid
h = 0.02  # Step size
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# Predict on mesh
Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

# Plot
plt.figure(figsize=(10, 6))
plt.contourf(xx, yy, Z, alpha=0.4, cmap='RdYlBu')
plt.scatter(X[:, 0], X[:, 1], c=y, s=100, edgecolors='k', cmap='RdYlBu')
plt.xlabel('Feature 1', fontsize=12)
plt.ylabel('Feature 2', fontsize=12)
plt.title('Decision Boundary', fontsize=14)
plt.colorbar(label='Class')
plt.show()
```

### Residual Plot
```python
import matplotlib.pyplot as plt
import numpy as np

# Get predictions and residuals
y_pred = model.predict(X_test)
residuals = y_test - y_pred

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(y_pred, residuals, alpha=0.6)
plt.axhline(y=0, color='r', linestyle='--', linewidth=2)
plt.xlabel('Predicted Values', fontsize=12)
plt.ylabel('Residuals', fontsize=12)
plt.title('Residual Plot', fontsize=14)
plt.grid(True, alpha=0.3)
plt.show()
```

### MSE vs Parameter (Grid Search Visualisation)
```python
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

# Try different alpha values
alphas = np.logspace(-3, 3, 50)
train_mse = []
test_mse = []

for alpha in alphas:
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    
    train_mse.append(mean_squared_error(y_train, model.predict(X_train)))
    test_mse.append(mean_squared_error(y_test, model.predict(X_test)))

# Plot
plt.figure(figsize=(10, 6))
plt.semilogx(alphas, train_mse, label='Train MSE', marker='o')
plt.semilogx(alphas, test_mse, label='Test MSE', marker='s')
plt.xlabel('Alpha (Regularisation Strength)', fontsize=12)
plt.ylabel('MSE', fontsize=12)
plt.title('Ridge Regression: MSE vs Alpha', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Find best alpha
best_alpha = alphas[np.argmin(test_mse)]
print(f"Best alpha: {best_alpha:.4f}")
```

---

## Exam Patterns & Quick Reference

### Pattern 1: Basic Regression Problem
**Given:** Dataset with predictors X and labels y  
**Task:** Fit a linear model and evaluate

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Fit model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
print(f"Train R²: {model.score(X_train, y_train):.4f}")
print(f"Test R²: {model.score(X_test, y_test):.4f}")
print(f"Test MSE: {mean_squared_error(y_test, model.predict(X_test)):.4f}")
```

### Pattern 2: Polynomial Regression with Overfitting Analysis
**Given:** Dataset, asked to compare polynomial degrees  
**Task:** Show training MSE decreases, test MSE U-shaped

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import numpy as np

degrees = [1, 2, 3, 4, 5]
results = []

for degree in degrees:
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    model.fit(X_train, y_train)
    
    train_mse = mean_squared_error(y_train, model.predict(X_train))
    test_mse = mean_squared_error(y_test, model.predict(X_test))
    
    results.append({'Degree': degree, 'Train MSE': train_mse, 'Test MSE': test_mse})
    print(f"Degree {degree}: Train MSE={train_mse:.4f}, Test MSE={test_mse:.4f}")

# Best model: lowest test MSE (NOT train MSE)
import pandas as pd
df = pd.DataFrame(results)
best_degree = df.loc[df['Test MSE'].idxmin(), 'Degree']
print(f"\nBest degree: {best_degree}")
```

### Pattern 3: Classification with Evaluation
**Given:** Binary classification dataset  
**Task:** Train logistic regression, report metrics

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np

# Split (stratified for classification)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Train
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
```

### Pattern 4: Model Selection with Cross-Validation
**Given:** Multiple candidate models  
**Task:** Use CV to select best model

```python
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
import numpy as np

models = {
    'Linear': LinearRegression(),
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=0.1),
    'Tree': DecisionTreeRegressor(max_depth=5)
}

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    mse_scores = -scores
    print(f"{name}: CV MSE = {mse_scores.mean():.4f} ± {mse_scores.std():.4f}")
```

### Pattern 5: KNN with Feature Scaling
**Given:** KNN classification task  
**Task:** Remember to scale features!

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Pipeline ensures scaling is done correctly
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier(n_neighbors=5))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

pipeline.fit(X_train, y_train)
print(f"Accuracy: {pipeline.score(X_test, y_test):.4f}")
```

### Pattern 6: Train/Validation/Test Split
**Given:** Need to tune hyperparameters AND estimate deployment performance  
**Task:** Use 3-way split or cross-validation + final test

```python
from sklearn.model_selection import train_test_split
import numpy as np

# Option 1: 3-way split (60% train, 20% val, 20% test)
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)
# 0.25 x 0.8 = 0.2 of original data

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

# Option 2: Cross-validation on train, then final test
# Use cross_val_score for model selection, then .score(X_test, y_test) for final eval
```

### Pattern 7: Log Transformation for Exponential Relationships
**Given:** Data spanning multiple orders of magnitude  
**Task:** Apply log transform, fit linear model

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Original data: exponential relationship
df = pd.read_csv('animals.csv')  # columns: body_mass, heart_rate

# Transform both variables
df['log_bm'] = np.log10(df['body_mass'])
df['log_hr'] = np.log10(df['heart_rate'])

# Fit linear model to transformed data
X = df[['log_bm']].values
y = df['log_hr'].values

model = LinearRegression()
model.fit(X, y)

print(f"log(HR) = {model.intercept_:.4f} + {model.coef_[0]:.4f} * log(BM)")

# This corresponds to: HR = 10^intercept * BM^coef (power law)
```

### Pattern 8: Regularisation to Prevent Overfitting
**Given:** High-dimensional data or polynomial features  
**Task:** Use Ridge/Lasso regularisation

```python
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

# High-degree polynomial with regularisation
pipeline = Pipeline([
    ('poly', PolynomialFeatures(degree=10)),
    ('ridge', Ridge(alpha=1.0))
])

# Tune alpha via cross-validation
alphas = np.logspace(-3, 3, 20)
best_alpha = None
best_score = -np.inf

for alpha in alphas:
    pipeline.set_params(ridge__alpha=alpha)
    scores = cross_val_score(pipeline, X, y, cv=5, scoring='r2')
    mean_score = scores.mean()
    if mean_score > best_score:
        best_score = mean_score
        best_alpha = alpha

print(f"Best alpha: {best_alpha:.4f}, Best CV R²: {best_score:.4f}")
```

### Common Mistakes to Avoid

1. **Using training MSE to select models** → Use validation/test MSE or cross-validation
2. **Not scaling features for KNN/SVM** → Distance-based methods need scaling
3. **Data leakage**: fitting scaler on entire dataset before split → Fit on training only
4. **Overfitting**: high degree polynomials without regularisation → Use cross-validation to detect
5. **Classification with linear regression** → Use logistic regression for classification
6. **Ignoring class imbalance** → Use stratified splits, consider precision/recall not just accuracy
7. **Testing on training data** → Always use separate test set or cross-validation

### Quick sklearn Cheatsheet

| Task | Algorithm | Import |
|------|-----------|--------|
| Linear regression | LinearRegression | `from sklearn.linear_model import LinearRegression` |
| Polynomial regression | PolynomialFeatures + LinearRegression | `from sklearn.preprocessing import PolynomialFeatures` |
| Logistic regression | LogisticRegression | `from sklearn.linear_model import LogisticRegression` |
| Ridge (L2) | Ridge | `from sklearn.linear_model import Ridge` |
| Lasso (L1) | Lasso | `from sklearn.linear_model import Lasso` |
| KNN classifier | KNeighborsClassifier | `from sklearn.neighbors import KNeighborsClassifier` |
| KNN regressor | KNeighborsRegressor | `from sklearn.neighbors import KNeighborsRegressor` |
| Decision tree classifier | DecisionTreeClassifier | `from sklearn.tree import DecisionTreeClassifier` |
| Decision tree regressor | DecisionTreeRegressor | `from sklearn.tree import DecisionTreeRegressor` |
| Train/test split | train_test_split | `from sklearn.model_selection import train_test_split` |
| Cross-validation | cross_val_score | `from sklearn.model_selection import cross_val_score` |
| Feature scaling | StandardScaler | `from sklearn.preprocessing import StandardScaler` |
| Pipeline | Pipeline | `from sklearn.pipeline import Pipeline` |

### Scoring Metrics Reference

| Metric | Regression | Classification | sklearn function |
|--------|-----------|----------------|------------------|
| MSE | ✓ | | `mean_squared_error` |
| MAE | ✓ | | `mean_absolute_error` |
| R² | ✓ | | `r2_score` or `.score()` |
| Accuracy | | ✓ | `accuracy_score` or `.score()` |
| Precision | | ✓ | `precision_score` |
| Recall | | ✓ | `recall_score` |
| F1 | | ✓ | `f1_score` |
| ROC-AUC | | ✓ | `roc_auc_score` |
| Confusion Matrix | | ✓ | `confusion_matrix` |

### Formula Reference

**MSE (Mean Squared Error):**
```
MSE = (1/n) * Σ(yi - ŷi)²
```

**MAE (Mean Absolute Error):**
```
MAE = (1/n) * Σ|yi - ŷi|
```

**R² Score:**
```
R² = 1 - (Σ(yi - ŷi)²) / (Σ(yi - ȳ)²)
```

**Normal Equations (Linear Regression):**
```
w = (XᵀX)⁻¹Xᵀy
```

**Accuracy:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Precision:**
```
Precision = TP / (TP + FP)
```

**Recall:**
```
Recall = TP / (TP + FN)
```

**F1 Score:**
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

---

## Essential Imports Template

```python
# Data manipulation
import numpy as np
import pandas as pd

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns

# Train/test split and cross-validation
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate

# Preprocessing
from sklearn.preprocessing import StandardScaler, MinMaxScaler, PolynomialFeatures

# Models - Regression
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet

# Models - Classification
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

# Metrics - Regression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Metrics - Classification
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve
)

# Pipeline
from sklearn.pipeline import Pipeline

# Set random seed for reproducibility
np.random.seed(42)
```

---

**End of ML Lab Code Patterns Cheatsheet**

*Remember: Every code snippet is complete and runnable. Copy-paste and modify as needed for your specific problem.*
