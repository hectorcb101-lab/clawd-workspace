# Stats Recap Formula Guide
**Prof. Bajaj's Week 6 Quiz Prep — 17 Essential Formulas**

---

## How to Use This Guide

This isn't a reference manual — it's a conversation. Think of it like sitting down with a tutor who's going to walk you through every formula you need for the quiz. We'll build intuition first, show you the proper notation, work through examples together, and point out where students typically stumble.

The formulas are grouped by concept, not numbered arbitrarily. You'll see how mean connects to variance, how dot products build into matrix equations, and how probability rules lead naturally into distributions.

Grab a pen and paper. Work through the examples as you read. By the end, these formulas will feel like tools you understand, not symbols you've memorised.

---

# Part 1: Describing Data

Before we can model anything, we need to describe what we have. These three formulas — mean, variance, and standard deviation — form a connected story about the centre and spread of your data.

## The Centre: Mean

**Intuition:** If you had to pick one number to represent your entire dataset, what would it be? The mean is that number. Think of it like the centre of gravity — if your data points were physical weights on a number line, the mean is where the line would balance perfectly.

**The formula:**

$$\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$$

Read this as: "Add up all your values, then divide by how many you have." The Greek letter $\mu$ (mu) represents the population mean, while $\bar{x}$ is used for sample means — same calculation, different context.

**Simple example:** Five students scored 65, 72, 68, 81, and 74 on a test. What's the average?

$$\mu = \frac{65 + 72 + 68 + 81 + 74}{5} = \frac{360}{5} = 72$$

The average score is 72. Notice that not a single student actually scored exactly 72 — the mean represents the balance point, not a value that must appear in the data.

**Slightly harder:** What if we have a frequency table? Suppose 10 people scored 60, 15 scored 70, and 5 scored 80:

$$\mu = \frac{(10 \times 60) + (15 \times 70) + (5 \times 80)}{10 + 15 + 5} = \frac{600 + 1050 + 400}{30} = \frac{2050}{30} = 68.33$$

Same concept — we're just being clever about not writing out "60, 60, 60..." ten times.

**Watch out for:** Outliers demolish the mean. If five students score around 70 and one scores 5 (perhaps they were ill), the mean drops to 59 — suddenly it doesn't represent anyone. When you see extreme values, consider using the median instead.

---

## The Spread: Variance

**Intuition:** The mean tells you the centre, but it says nothing about spread. Are all values clustered tightly around 72, or scattered wildly between 10 and 95? Variance quantifies this. Think of it like measuring how far each point wanders from home (the mean), then averaging those distances.

We square the distances for a good reason: if we didn't, positive and negative deviations would cancel out. A student scoring 5 points above the mean and another scoring 5 points below would sum to zero, hiding the fact that there's variation at all.

**The formula:**

$$\sigma^2 = \frac{1}{n}\sum_{i=1}^{n} (x_i - \mu)^2$$

This says: "For each value, find how far it is from the mean, square that distance, then average all the squared distances."

**Simple example:** Using the same five test scores (65, 72, 68, 81, 74) with $\mu = 72$:

First, calculate deviations from the mean:
- $65 - 72 = -7$
- $72 - 72 = 0$
- $68 - 72 = -4$
- $81 - 72 = 9$
- $74 - 72 = 2$

Now square each deviation:
- $(-7)^2 = 49$
- $(0)^2 = 0$
- $(-4)^2 = 16$
- $(9)^2 = 81$
- $(2)^2 = 4$

Sum them and divide by $n$:

$$\sigma^2 = \frac{49 + 0 + 16 + 81 + 4}{5} = \frac{150}{5} = 30$$

The variance is 30 marks². Yes, squared marks — variance has squared units, which is why we often prefer standard deviation.

**Slightly harder:** There's a computational shortcut: $\sigma^2 = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$. In plain English: "average of squares minus square of average." This is faster when you're working with expected values.

**Watch out for:** Sample variance uses $n-1$ in the denominator, not $n$. If the question mentions a "sample" or you're estimating population variance from a subset, use $s^2 = \frac{1}{n-1}\sum(x_i - \bar{x})^2$. This Bessel correction accounts for the fact that your sample probably doesn't capture the full population spread.

---

## Back to Original Units: Standard Deviation

**Intuition:** Variance is useful, but squared units are awkward. If we're measuring test scores, variance has units of "marks squared" — what does that even mean? Standard deviation fixes this by taking the square root, bringing us back to the original units.

**The formula:**

$$\sigma = \sqrt{\sigma^2} = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (x_i - \mu)^2}$$

Think of standard deviation as the "typical distance from the mean." If $\sigma = 5$ marks, most scores will be within 5 marks of the mean.

**Simple example:** From our variance calculation above, $\sigma^2 = 30$:

$$\sigma = \sqrt{30} \approx 5.48 \text{ marks}$$

Now we can say: "The typical student scores within about 5.5 marks of the mean (72)." Much more intuitive than "variance is 30 marks²."

**Slightly harder:** For normal distributions, there's a beautiful rule: roughly 68% of values fall within $\mu \pm \sigma$, 95% within $\mu \pm 2\sigma$, and 99.7% within $\mu \pm 3\sigma$. With $\mu = 72$ and $\sigma = 5.48$, we'd expect most scores between $72 - 5.48 = 66.5$ and $72 + 5.48 = 77.5$.

**Watch out for:** Standard deviation can never be negative. If your calculation gives $\sigma < 0$, you've made an error. Also, standard deviation is sensitive to outliers just like the mean — one extreme value can inflate it significantly.

---

# Part 2: Linear Algebra & Models

Now we move from describing data to modelling it. Linear algebra gives us the mathematical machinery to work with multiple variables at once. These concepts underpin linear regression, neural networks, and most of machine learning.

## Combining Numbers: Dot Product

**Intuition:** Imagine you're calculating a weighted average. You have a list of values (student scores) and a list of weights (how important each assignment is). The dot product multiplies corresponding pairs and adds everything up — it's a weighted sum.

Think of it like this: if $\mathbf{x}$ represents features of a house (size, bedrooms, age) and $\mathbf{w}$ represents how much you value each feature, then $\mathbf{x}^{\mathsf{T}}\mathbf{w}$ tells you the house's total "value score."

**The formula:**

$$\mathbf{x}^{\mathsf{T}}\mathbf{w} = \sum_{i=1}^{n} x_i w_i = x_1 w_1 + x_2 w_2 + \cdots + x_n w_n$$

The superscript $\mathsf{T}$ means "transpose" (turning a column vector into a row), but don't let notation intimidate you — it's just pairwise multiplication and addition.

**Simple example:** Calculate $\mathbf{x}^{\mathsf{T}}\mathbf{w}$ where $\mathbf{x} = [2, -1, 3]$ and $\mathbf{w} = [0.5, 1, -2]$:

$$\mathbf{x}^{\mathsf{T}}\mathbf{w} = (2)(0.5) + (-1)(1) + (3)(-2) = 1 - 1 - 6 = -6$$

That's it. Multiply matching positions, add them up. The result is a single number (a scalar).

**Slightly harder:** What's the length of a vector? It's the dot product with itself: $\|\mathbf{x}\| = \sqrt{\mathbf{x}^{\mathsf{T}}\mathbf{x}}$. For $\mathbf{x} = [3, 4]$:

$$\mathbf{x}^{\mathsf{T}}\mathbf{x} = 3^2 + 4^2 = 9 + 16 = 25 \implies \|\mathbf{x}\| = \sqrt{25} = 5$$

(Pythagorean theorem in disguise!)

**Watch out for:** Vectors must have the same length to compute a dot product. Trying to compute $[1,2,3]^{\mathsf{T}}[4,5]$ is undefined — dimensions don't match. Also, the result is always a scalar, never a vector.

---

## Predictions from Data: Matrix Equation $\mathbf{y} = \mathbf{X}\mathbf{w}$

**Intuition:** This is the compact way to write linear regression. Instead of making one prediction at a time, we make predictions for all our data points simultaneously. Each row of $\mathbf{X}$ is one data point (one house, one person, one observation), and $\mathbf{w}$ contains the weights that determine the prediction.

Think of $\mathbf{X}$ as a spreadsheet: rows are samples, columns are features. Multiply by $\mathbf{w}$ and out pops a column of predictions — one for each row.

**The formula:**

$$\mathbf{y} = \mathbf{X}\mathbf{w}$$

Where:
- $\mathbf{y}$ is an $(n \times 1)$ vector of predictions
- $\mathbf{X}$ is an $(n \times p)$ matrix (n samples, p features)
- $\mathbf{w}$ is a $(p \times 1)$ vector of weights

**Simple example:** Predict house prices using size (sqm) and bedrooms. Weights are $w_1 = 100$ (£ per sqm) and $w_2 = 5000$ (£ per bedroom):

$$\mathbf{X} = \begin{bmatrix} 80 & 2 \\ 120 & 3 \\ 60 & 1 \end{bmatrix}, \quad \mathbf{w} = \begin{bmatrix} 100 \\ 5000 \end{bmatrix}$$

$$\mathbf{y} = \mathbf{X}\mathbf{w} = \begin{bmatrix} (80)(100) + (2)(5000) \\ (120)(100) + (3)(5000) \\ (60)(100) + (1)(5000) \end{bmatrix} = \begin{bmatrix} 18000 \\ 27000 \\ 11000 \end{bmatrix}$$

Predicted prices: £18k, £27k, £11k.

**Slightly harder:** What if we want an intercept term? Add a column of ones to $\mathbf{X}$:

$$\mathbf{X} = \begin{bmatrix} 1 & 80 & 2 \\ 1 & 120 & 3 \\ 1 & 60 & 1 \end{bmatrix}, \quad \mathbf{w} = \begin{bmatrix} 2000 \\ 100 \\ 5000 \end{bmatrix}$$

Now $\mathbf{y} = \mathbf{X}\mathbf{w}$ includes a baseline price of £2000 before considering size and bedrooms.

**Watch out for:** Matrix dimensions must align. If $\mathbf{X}$ is $(n \times p)$, then $\mathbf{w}$ must be $(p \times 1)$, yielding $\mathbf{y}$ as $(n \times 1)$. If dimensions don't match, the multiplication is undefined. Also, each element of $\mathbf{y}$ is just the dot product of a row of $\mathbf{X}$ with $\mathbf{w}$ — it's formula 4 repeated $n$ times!

---

## Finding the Best Weights: Pseudo-inverse $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}$

**Intuition:** You've got data $\mathbf{X}$ and outcomes $\mathbf{y}$, and you want to find the weights $\mathbf{w}$ that best predict $\mathbf{y}$ from $\mathbf{X}$. This formula gives you the least squares solution — the $\mathbf{w}$ that minimises the sum of squared errors.

Think of it like fitting a line to scattered points. There's no perfect line through every point, so we find the one that gets as close as possible to all of them.

**The formula:**

$$\hat{\mathbf{w}} = (\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}\mathbf{y}$$

This looks intimidating, but break it down:
1. Compute $\mathbf{X}^{\mathsf{T}}\mathbf{X}$ (a $p \times p$ square matrix)
2. Invert it to get $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}$
3. Multiply by $\mathbf{X}^{\mathsf{T}}\mathbf{y}$

**Simple example:** Fit $y = w_0 + w_1 x$ to points $(1,2)$, $(2,3)$, $(3,5)$:

$$\mathbf{X} = \begin{bmatrix} 1 & 1 \\ 1 & 2 \\ 1 & 3 \end{bmatrix}, \quad \mathbf{y} = \begin{bmatrix} 2 \\ 3 \\ 5 \end{bmatrix}$$

$$\mathbf{X}^{\mathsf{T}}\mathbf{X} = \begin{bmatrix} 3 & 6 \\ 6 & 14 \end{bmatrix}, \quad (\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1} = \frac{1}{6}\begin{bmatrix} 14 & -6 \\ -6 & 3 \end{bmatrix}$$

$$\mathbf{X}^{\mathsf{T}}\mathbf{y} = \begin{bmatrix} 10 \\ 23 \end{bmatrix}, \quad \hat{\mathbf{w}} = \frac{1}{6}\begin{bmatrix} 14 & -6 \\ -6 & 3 \end{bmatrix}\begin{bmatrix} 10 \\ 23 \end{bmatrix} = \begin{bmatrix} 1/3 \\ 3/2 \end{bmatrix}$$

Best fit: $y = \frac{1}{3} + \frac{3}{2}x$ (intercept ≈ 0.33, slope = 1.5).

**Slightly harder:** Why does this work? It comes from solving $\mathbf{X}^{\mathsf{T}}\mathbf{X}\mathbf{w} = \mathbf{X}^{\mathsf{T}}\mathbf{y}$ (the "normal equations"). Multiplying both sides by $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}$ isolates $\mathbf{w}$.

**Watch out for:** Order matters! Compute $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}$ first, then multiply by $\mathbf{X}^{\mathsf{T}}$. You can't invert $\mathbf{X}^{\mathsf{T}}$ alone — it's not square. Also, if columns of $\mathbf{X}$ are linearly dependent (e.g., one feature is an exact multiple of another), $\mathbf{X}^{\mathsf{T}}\mathbf{X}$ is singular and can't be inverted.

---

## Binary Decisions: Step Function

**Intuition:** Sometimes we need to convert a continuous score into a binary decision: "yes or no," "spam or not spam," "pass or fail." The step function does exactly this — it outputs 1 if the input is non-negative, and 0 otherwise.

Think of it like a light switch: once you cross the threshold, it flips on. Before that, it's off.

**The formula:**

$$f(x) = \begin{cases} 1 & \text{if } x \geq 0 \\ 0 & \text{if } x < 0 \end{cases}$$

Also called the Heaviside function or threshold function.

**Simple example:** A spam filter computes a score for an email. If the score is positive, mark it as spam; otherwise, it's legitimate.

- Email A: score = $0.7 \implies f(0.7) = 1$ (spam)
- Email B: score = $-0.3 \implies f(-0.3) = 0$ (not spam)
- Email C: score = $0 \implies f(0) = 1$ (spam — note that zero counts as "on")

**Slightly harder:** The step function is often used after computing $\mathbf{w}^{\mathsf{T}}\mathbf{x}$. For instance, in the perceptron algorithm:

$$\text{prediction} = f(\mathbf{w}^{\mathsf{T}}\mathbf{x}) = \begin{cases} 1 & \text{if } \mathbf{w}^{\mathsf{T}}\mathbf{x} \geq 0 \\ 0 & \text{otherwise} \end{cases}$$

**Watch out for:** The threshold includes zero: $f(0) = 1$. Some definitions use $x > 0$ (strict inequality), but the standard convention is $x \geq 0$. Check what your course uses. Also, the step function isn't differentiable at $x=0$ (it has a discontinuous jump), which is why modern neural networks use smooth activations like sigmoid or ReLU instead.

---

## Concrete Example: A Linear Model with Two Features

**Intuition:** Let's make this real. Suppose we're predicting someone's fitness level based on age and height. We've fit a model and found specific weights. This formula shows how to plug in someone's data and get a prediction.

**The formula:**

$$f(\text{Age}, \text{Height}) = 1 + 2 \times \text{Age} - 3 \times \text{Height}$$

This is just $f(\mathbf{x}) = w_0 + w_1 x_1 + w_2 x_2$ with concrete numbers:
- Intercept: $w_0 = 1$
- Age coefficient: $w_1 = 2$ (each year adds 2 to the score)
- Height coefficient: $w_2 = -3$ (each cm subtracts 3 from the score)

**Simple example:** Predict fitness for a 30-year-old who is 180 cm tall:

$$f(30, 180) = 1 + 2(30) - 3(180) = 1 + 60 - 540 = -479$$

The prediction is $-479$. (Whether this number is meaningful depends on how the model was trained — often we'd apply a threshold or scaling.)

**Slightly harder:** What does each coefficient mean?
- **Age = 2:** Holding height constant, each additional year increases the score by 2. Older → higher score.
- **Height = -3:** Holding age constant, each additional cm decreases the score by 3. Taller → lower score.
- **Intercept = 1:** The baseline score when age and height are both zero (usually not meaningful, but mathematically necessary).

**Watch out for:** Sign errors are common. $-3 \times 180 = -540$, not $+540$. Also, remember that coefficients show the effect of changing one variable while holding others constant — they don't imply causation.

---

## Describing Function Types: $f: \mathbb{R}^3 \to \mathbb{R}$

**Intuition:** This notation is about being precise. Before we even write a formula, we specify what type of input and output the function has. $f: \mathbb{R}^3 \to \mathbb{R}$ says: "Function $f$ takes a 3-dimensional real vector as input and produces a single real number as output."

Think of it like specifying a function signature in programming: you're declaring the types before writing the implementation.

**The notation:**

$$f: \mathbb{R}^3 \to \mathbb{R}$$

- $\mathbb{R}^3$ means "3-dimensional real space" (inputs are triples like $(x_1, x_2, x_3)$)
- $\to$ means "maps to"
- $\mathbb{R}$ means "real numbers" (output is a single value)

**Simple example:** Consider $f(x, y, z) = x^2 + 2y - z$. What's its type?

Input: three numbers $(x, y, z)$ — lives in $\mathbb{R}^3$
Output: one number — lives in $\mathbb{R}$

So $f: \mathbb{R}^3 \to \mathbb{R}$.

Evaluate: $f(1, 2, 3) = 1^2 + 2(2) - 3 = 1 + 4 - 3 = 2$.

**Slightly harder:** Dimensions matter for function composition. If $f: \mathbb{R}^3 \to \mathbb{R}^2$ and $g: \mathbb{R}^2 \to \mathbb{R}$, then we can compute $g(f(\mathbf{x}))$ because the output dimension of $f$ matches the input dimension of $g$. But we can't compute $f(g(\mathbf{x}))$ — $g$ outputs a single number, while $f$ expects three.

**Watch out for:** $\mathbb{R}^3 \to \mathbb{R}$ is very different from $\mathbb{R} \to \mathbb{R}^3$. The first takes three inputs and gives one output; the second takes one input and gives three outputs. Arrow direction matters!

---

# Part 3: Probability

Probability quantifies uncertainty. These two rules — addition (for "or") and Bayes' theorem (for flipping conditionals) — are the foundation of everything that follows.

## Combining Events: Addition Rule

**Intuition:** You want to know the probability of "A or B" (at least one happens). The naive approach is to add $P(A) + P(B)$, but that double-counts the overlap — cases where both A and B happen. So we subtract $P(A \cap B)$ once to correct it.

Think of Venn diagrams: the union $A \cup B$ is the total shaded area, which equals the area of A plus the area of B, minus the overlapping area (because we counted it twice).

**The formula:**

$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$

Read "$\cup$" as "union" (or), and "$\cap$" as "intersection" (and).

**Simple example:** You draw one card from a standard deck. What's the probability it's red or an ace?

- $P(\text{red}) = 26/52 = 1/2$
- $P(\text{ace}) = 4/52 = 1/13$
- $P(\text{red and ace}) = 2/52 = 1/26$ (two red aces: hearts and diamonds)

$$P(\text{red or ace}) = \frac{26}{52} + \frac{4}{52} - \frac{2}{52} = \frac{28}{52} = \frac{7}{13}$$

**Slightly harder:** If A and B are mutually exclusive (can't both happen), then $P(A \cap B) = 0$, and the formula simplifies to $P(A \cup B) = P(A) + P(B)$. For example, rolling a 2 or a 5 on a die:

$$P(\{2\} \cup \{5\}) = \frac{1}{6} + \frac{1}{6} = \frac{2}{6} = \frac{1}{3}$$

**Watch out for:** Don't forget to subtract the overlap! A common mistake is to compute $P(A) + P(B)$ and stop there, which gives a probability greater than 1 when A and B overlap significantly. Also, $P(A \cup B) \neq P(A) \times P(B)$ — that's for intersection of independent events, not union.

---

## Reversing Conditionals: Bayes' Theorem

**Intuition:** You know $P(B|A)$ (probability of B given A), but you need $P(A|B)$ (probability of A given B). Bayes' theorem lets you "flip" the conditional. This is crucial in medical testing, spam filtering, and machine learning.

Think of a diagnostic test: you know $P(\text{positive}|\text{disease})$ (test sensitivity), but what you really care about is $P(\text{disease}|\text{positive})$ — if you test positive, what's the chance you actually have the disease? Bayes' theorem connects the two.

**The formula:**

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

Often expanded using the law of total probability:

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B|A) \cdot P(A) + P(B|A^c) \cdot P(A^c)}$$

**Simple example:** A disease affects 1% of the population. A test correctly identifies 95% of sick people (sensitivity) but incorrectly flags 10% of healthy people (false positive rate). You test positive. What's the probability you have the disease?

Let $D$ = disease, $T$ = positive test.
- $P(D) = 0.01$, $P(D^c) = 0.99$
- $P(T|D) = 0.95$, $P(T|D^c) = 0.10$

$$P(D|T) = \frac{(0.95)(0.01)}{(0.95)(0.01) + (0.10)(0.99)} = \frac{0.0095}{0.0095 + 0.099} = \frac{0.0095}{0.1085} \approx 0.088$$

Only 8.8%! Even with a "95% accurate" test, most positive results are false alarms when the disease is rare.

**Slightly harder:** Bayes' theorem is the engine behind Bayesian updating. Start with a prior belief $P(A)$, observe evidence $B$, and update to a posterior $P(A|B)$. For instance, spam filters learn $P(\text{spam}|\text{word})$ from training data and use Bayes to classify new emails.

**Watch out for:** Don't confuse $P(A|B)$ with $P(B|A)$ — they're usually very different. Also, when computing $P(B)$, you need to account for all ways $B$ can happen (both when $A$ is true and when it's false). Forgetting $P(B|A^c) \cdot P(A^c)$ is a common error.

---

# Part 4: Random Variables & Distributions

We now move from events to random variables — quantities whose values are determined by chance. These formulas describe the most important distributions you'll encounter.

## The Standard: Normal Distribution $X \sim \mathcal{N}(0,1)$

**Intuition:** The normal (or Gaussian) distribution is the bell curve. It's symmetric around the mean, with most values near the centre and fewer values farther out. The notation $X \sim \mathcal{N}(0,1)$ specifically means a **standard normal**: mean 0, variance 1.

This is the reference distribution. Any normal distribution $\mathcal{N}(\mu, \sigma^2)$ can be converted to standard normal using $Z = \frac{X - \mu}{\sigma}$.

**The notation:**

$$X \sim \mathcal{N}(0, 1)$$

This tells you three things:
- $X$ is a random variable
- It follows a normal distribution ($\mathcal{N}$)
- Mean = 0, variance = 1

**Simple example:** IQ scores follow $\mathcal{N}(100, 15^2)$. Convert an IQ of 130 to a standard normal:

$$Z = \frac{X - \mu}{\sigma} = \frac{130 - 100}{15} = \frac{30}{15} = 2$$

An IQ of 130 is 2 standard deviations above the mean. Since $Z \sim \mathcal{N}(0,1)$, we can look up $P(Z \leq 2) \approx 0.977$ in a Z-table — this person scores higher than 97.7% of the population.

**Slightly harder:** The 68-95-99.7 rule: for any normal distribution, approximately 68% of values fall within $\mu \pm \sigma$, 95% within $\mu \pm 2\sigma$, and 99.7% within $\mu \pm 3\sigma$. For IQ:
- 68% score between $100 - 15 = 85$ and $100 + 15 = 115$
- 95% score between 70 and 130

**Watch out for:** The notation $\mathcal{N}(\mu, \sigma^2)$ uses **variance** (squared standard deviation), not standard deviation itself. If you see $\mathcal{N}(0, 4)$, that's mean 0 and variance 4, so $\sigma = 2$. Also, for continuous distributions, $P(X = k)$ for any exact value $k$ is always zero — only intervals have non-zero probability.

---

## Centre of Mass: Expected Value $\mathbb{E}[X]$

**Intuition:** If you repeated a random process infinitely many times and averaged the results, you'd get the expected value. It's the long-run average, the "centre of mass" of the probability distribution.

Think of rolling a die: you can't roll 3.5 on a single roll, but if you roll thousands of times, the average converges to 3.5. That's $\mathbb{E}[X]$.

**The formula:**

$$\mathbb{E}[X] = \sum_{x} x \cdot P(X = x) \quad \text{(discrete)}$$
$$\mathbb{E}[X] = \int_{-\infty}^{\infty} x \cdot f(x) \, dx \quad \text{(continuous)}$$

For discrete: weight each value by its probability, then sum. For continuous: integrate $x$ times the probability density.

**Simple example:** Roll a fair six-sided die. What's $\mathbb{E}[X]$?

Each outcome has probability $1/6$:

$$\mathbb{E}[X] = 1 \cdot \frac{1}{6} + 2 \cdot \frac{1}{6} + 3 \cdot \frac{1}{6} + 4 \cdot \frac{1}{6} + 5 \cdot \frac{1}{6} + 6 \cdot \frac{1}{6} = \frac{1+2+3+4+5+6}{6} = \frac{21}{6} = 3.5$$

**Slightly harder:** Expected value is **linear**: $\mathbb{E}[aX + b] = a\mathbb{E}[X] + b$. Also, for independent $X$ and $Y$, $\mathbb{E}[X + Y] = \mathbb{E}[X] + \mathbb{E}[Y]$ (even if they're not independent!). This makes calculations much easier.

**Watch out for:** Expected value might not be a possible outcome. You can't roll 3.5, but it's still the expected value. Also, for specific distributions (binomial, Poisson, etc.), there are shortcut formulas — use them instead of summing from scratch.

---

## Measuring Spread: Variance of a Random Variable $\text{Var}(X)$

**Intuition:** Variance quantifies how spread out a random variable is. It's the average squared distance from the mean. Think of it as: "How surprised would you be by a typical outcome?"

**The formula:**

$$\text{Var}(X) = \mathbb{E}[(X - \mu)^2] = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$$

The second form ("expected value of squares minus square of expected value") is usually easier to compute.

**Simple example:** Flip a fair coin: $X = 1$ (heads) with probability 0.5, $X = 0$ (tails) with probability 0.5.

$$\mathbb{E}[X] = 1 \cdot 0.5 + 0 \cdot 0.5 = 0.5$$
$$\mathbb{E}[X^2] = 1^2 \cdot 0.5 + 0^2 \cdot 0.5 = 0.5$$
$$\text{Var}(X) = 0.5 - (0.5)^2 = 0.5 - 0.25 = 0.25$$

**Slightly harder:** Variance is **not linear**: $\text{Var}(aX + b) = a^2 \text{Var}(X)$ (the coefficient gets squared, and adding a constant doesn't change spread). For independent $X$ and $Y$, $\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y)$.

**Watch out for:** Variance has squared units. If $X$ is in metres, $\text{Var}(X)$ is in metres². Take the square root to get standard deviation (original units). Also, $\mathbb{E}[X^2]$ and $(\mathbb{E}[X])^2$ are different — don't confuse them.

---

## Counting Successes: Binomial Distribution

**Intuition:** You're flipping a coin $n$ times (or running $n$ independent trials), each with probability $p$ of success. The binomial distribution tells you the probability of getting exactly $k$ successes.

Think of multiple choice exams: 10 questions, 4 choices each, you guess randomly. What's the chance you get exactly 3 right? Binomial answers this.

**The formula:**

$$P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}$$

Where $\binom{n}{k} = \frac{n!}{k!(n-k)!}$ is "n choose k" — the number of ways to arrange $k$ successes among $n$ trials.

Expected value: $\mathbb{E}[X] = np$
Variance: $\text{Var}(X) = np(1-p)$

**Simple example:** Roll a die 5 times. What's the probability of rolling exactly two sixes?

$n = 5$, $p = 1/6$, $k = 2$:

$$\binom{5}{2} = \frac{5!}{2! \cdot 3!} = \frac{120}{2 \cdot 6} = 10$$

$$P(X = 2) = 10 \cdot \left(\frac{1}{6}\right)^2 \cdot \left(\frac{5}{6}\right)^3 = 10 \cdot \frac{1}{36} \cdot \frac{125}{216} = 10 \cdot \frac{125}{7776} \approx 0.161$$

About 16% chance.

**Slightly harder:** For "at least $k$ successes," sum probabilities: $P(X \geq k) = \sum_{i=k}^{n} P(X = i)$. For "at most $k$": $P(X \leq k) = \sum_{i=0}^{k} P(X = i)$.

**Watch out for:** The $\binom{n}{k}$ term is crucial — it counts arrangements. Without it, you're only computing the probability of one specific sequence (like "success, success, fail, fail, fail"), not all sequences with $k$ successes. Also, be careful with $p$ vs. $(1-p)$: successes get $p^k$, failures get $(1-p)^{n-k}$.

---

## The Bell Curve: Normal PDF

**Intuition:** The normal probability density function (PDF) is the formula for the bell curve. It describes continuous data that clusters symmetrically around a mean $\mu$ with spread controlled by $\sigma$.

**The formula:**

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

This looks terrifying, but the key parts are:
- $\frac{1}{\sigma\sqrt{2\pi}}$: normalising constant (makes total area = 1)
- $e^{-\frac{(x-\mu)^2}{2\sigma^2}}$: the exponential that creates the bell shape

**Simple example:** What's the PDF value at $x = \mu$ (the peak)?

At $x = \mu$, the exponent becomes $-\frac{(\mu - \mu)^2}{2\sigma^2} = 0$, so $e^0 = 1$:

$$f(\mu) = \frac{1}{\sigma\sqrt{2\pi}}$$

For $\mathcal{N}(0, 1)$, this is $\frac{1}{\sqrt{2\pi}} \approx 0.399$.

**Slightly harder:** To find $P(a < X < b)$, you integrate the PDF:

$$P(a < X < b) = \int_a^b f(x) \, dx$$

In practice, we use Z-tables or software rather than computing this by hand.

**Watch out for:** The PDF value $f(x)$ is **not** a probability. For continuous distributions, point probabilities are zero: $P(X = x) = 0$. The PDF is a density — probabilities come from integrating (finding areas). Also, the formula uses $\sigma^2$ in the exponent, so if given variance directly, use it; if given $\sigma$, square it.

---

## Events at a Rate: Poisson (mentioned briefly)

**Intuition:** The Poisson distribution models the number of events occurring in a fixed interval when events happen at a constant average rate $\lambda$ (and independently of each other). Think: phone calls per hour, typos per page, machine breakdowns per week.

**The formula:**

$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$

Expected value: $\mathbb{E}[X] = \lambda$
Variance: $\text{Var}(X) = \lambda$ (same as the mean!)

**Simple example:** A call centre receives an average of 4 calls per hour. What's the probability of exactly 2 calls in the next hour?

$\lambda = 4$, $k = 2$:

$$P(X = 2) = \frac{4^2 e^{-4}}{2!} = \frac{16 \cdot 0.0183}{2} = \frac{0.293}{2} \approx 0.146$$

About 14.6% chance.

**Slightly harder:** Poisson approximates binomial when $n$ is large and $p$ is small. If $n = 100$ and $p = 0.02$, computing binomial probabilities is tedious. Instead, use Poisson with $\lambda = np = 2$.

**Watch out for:** $\lambda$ can be any positive number — it's not a probability. If $\lambda = 50$ events per day, that's fine. Also, remember $0! = 1$, so $P(X = 0) = e^{-\lambda}$.

---

# Putting It All Together

You now have 17 formulas that connect data description, linear models, probability, and distributions. Here's how they fit:

**Start with data:** Compute mean (centre) and variance/std dev (spread).

**Model relationships:** Use dot products and matrices to build linear models. Find optimal weights with the pseudo-inverse.

**Handle uncertainty:** Apply probability rules (addition, Bayes) to quantify and update beliefs.

**Work with distributions:** Model counts with binomial, rates with Poisson, measurements with normal. Use expected value and variance to summarise.

These aren't isolated facts — they're a connected toolkit. Mean and variance appear everywhere: describing data samples, characterising probability distributions, measuring model error. The dot product underlies linear models, which generalise to neural networks. Bayes' theorem connects conditional probabilities to machine learning inference.

---

# Quick Reference Cheat Sheet

| **Formula** | **What It Does** | **Key Insight** |
|-------------|------------------|-----------------|
| $\mu = \frac{1}{n}\sum x_i$ | Mean | Balance point of data |
| $\sigma^2 = \frac{1}{n}\sum (x_i - \mu)^2$ | Variance | Average squared distance from mean |
| $\sigma = \sqrt{\sigma^2}$ | Standard deviation | Variance in original units |
| $\mathbf{x}^{\mathsf{T}}\mathbf{w} = \sum x_i w_i$ | Dot product | Weighted sum → scalar |
| $\mathbf{y} = \mathbf{X}\mathbf{w}$ | Linear model | Predictions for all samples |
| $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}$ | Pseudo-inverse | Best-fit weights (least squares) |
| $f(x) = 1$ if $x \geq 0$, else $0$ | Step function | Binary threshold |
| $f(\text{Age}, \text{Height}) = 1 + 2 \cdot \text{Age} - 3 \cdot \text{Height}$ | Concrete linear model | Shows coefficient interpretation |
| $f: \mathbb{R}^3 \to \mathbb{R}$ | Function type | 3 inputs → 1 output |
| $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ | Addition rule | Add, then subtract overlap |
| $P(A|B) = \frac{P(B|A) P(A)}{P(B)}$ | Bayes' theorem | Flip conditional probabilities |
| $X \sim \mathcal{N}(0,1)$ | Standard normal | Mean 0, variance 1 |
| $\mathbb{E}[X]$ | Expected value | Long-run average |
| $\text{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$ | Variance | Spread (squared units) |
| $P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$ | Binomial | Count successes in $n$ trials |
| $f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$ | Normal PDF | Bell curve formula |
| $P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$ | Poisson | Events at rate $\lambda$ |

---

**Final Thoughts**

This guide is meant to be read, worked through, and revisited. Don't just memorise symbols — understand why each formula exists and when to use it. Test yourself: cover the formula, explain it in plain English, then check if you were right.

You're not memorising 17 isolated facts. You're building a mental model of statistics — a framework for describing data, quantifying uncertainty, and making predictions. These formulas are the language. Once you're fluent, they'll feel natural.

Now go practise. Work through problems. Make mistakes. Learn from them. That's how fluency happens.

Good luck.
