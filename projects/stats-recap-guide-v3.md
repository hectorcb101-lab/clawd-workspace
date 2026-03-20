# Stats Recap Formula Guide v3
**Real Examples from Your Course — Week 6 Quiz Prep**

---

## How to Use This Guide

This isn't a reference manual — it's a conversation. But now with **real questions from your actual labs and lectures**, not made-up examples. Every example you'll see here comes straight from the exercises you've been working on in class.

The formulas are grouped by concept, not numbered arbitrarily. You'll see how mean connects to variance, how dot products build into matrix equations, and how probability rules lead naturally into distributions.

Grab a pen and paper. Work through the examples as you read. These are **your** exercises, from **your** course. By the end, these formulas will feel like tools you understand, not symbols you've memorised.

---

# Part 1: Describing Data

Before we can model anything, we need to describe what we have. These three formulas — mean, variance, and standard deviation — form a connected story about the centre and spread of your data.

## The Centre: Mean

**Intuition:** If you had to pick one number to represent your entire dataset, what would it be? The mean is that number. Think of it like the centre of gravity — if your data points were physical weights on a number line, the mean is where the line would balance perfectly.

**The formula:**

$$\mu = \frac{1}{n}\sum_{i=1}^{n} x_i$$

Read this as: "Add up all your values, then divide by how many you have." The Greek letter $\mu$ (mu) represents the population mean, while $\bar{x}$ is used for sample means — same calculation, different context.

**Real example from your Week 2 lab:** A firm's profits (in millions £) over six months were:

| Month | Jul | Aug | Sep | Oct | Nov | Dec |
|-------|-----|-----|-----|-----|-----|-----|
| Profit (M) | 2.0 | 2.1 | 2.2 | 2.1 | 2.3 | 2.4 |

What's the average monthly profit?

$$\mu = \frac{2.0 + 2.1 + 2.2 + 2.1 + 2.3 + 2.4}{6} = \frac{13.1}{6} = 2.183 \text{ million}$$

The average profit is £2.183 million per month. Notice that several months are below this value (Jul, Aug, Oct) and several are above (Sep, Nov, Dec) — the mean represents the balance point.

**Slightly harder — weighted mean:** From your Week 6 coffee breaks exercise, suppose you observe how many coffee breaks people take per day:

| Coffee breaks | 0 | 1 | 2 | 3 | 4 | 5 |
|---------------|---|---|---|---|---|---|
| Frequency | 28 | 37 | 13 | 9 | 8 | 5 |

The mean number of coffee breaks is:

$$\mu = \frac{(0 \times 28) + (1 \times 37) + (2 \times 13) + (3 \times 9) + (4 \times 8) + (5 \times 5)}{100} = \frac{132}{100} = 1.32$$

On average, coffee drinkers take 1.32 breaks per day.

**Watch out for:** Outliers demolish the mean. From your Week 2 lab, the height data had a range from 141.42 cm to 187.23 cm. If one person was incorrectly recorded as 250 cm, the mean would jump dramatically even though 49 out of 50 measurements are reasonable. When you see extreme values, consider using the median instead.

---

## The Spread: Variance

**Intuition:** The mean tells you the centre, but it says nothing about spread. Are all values clustered tightly, or scattered widely? Variance quantifies this. Think of it like measuring how far each point wanders from home (the mean), then averaging those distances.

We square the distances for a good reason: if we didn't, positive and negative deviations would cancel out. A profit of 2.3 (above mean) and 2.0 (below mean) would sum to zero deviation, hiding the fact that there's variation at all.

**The formula:**

$$\sigma^2 = \frac{1}{n}\sum_{i=1}^{n} (x_i - \mu)^2$$

This says: "For each value, find how far it is from the mean, square that distance, then average all the squared distances."

**Real example from your Week 2 lab (firm profits):** Using the profit data with $\mu = 2.183$:

First, calculate deviations from the mean:
- $2.0 - 2.183 = -0.183$
- $2.1 - 2.183 = -0.083$
- $2.2 - 2.183 = 0.017$
- $2.1 - 2.183 = -0.083$
- $2.3 - 2.183 = 0.117$
- $2.4 - 2.183 = 0.217$

Now square each deviation:
- $(-0.183)^2 = 0.0335$
- $(-0.083)^2 = 0.0069$
- $(0.017)^2 = 0.0003$
- $(-0.083)^2 = 0.0069$
- $(0.117)^2 = 0.0137$
- $(0.217)^2 = 0.0471$

Sum them and divide by $n$:

$$\sigma^2 = \frac{0.0335 + 0.0069 + 0.0003 + 0.0069 + 0.0137 + 0.0471}{6} = \frac{0.1084}{6} = 0.0181 \text{ (million)}^2$$

**Computational shortcut:** There's a faster formula: $\sigma^2 = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$. In plain English: "average of squares minus square of average."

From your Week 6 lab (dice rolling exercise):

For a fair six-sided die, $\mu = 3.5$. To find variance:

$$\mathbb{E}[X^2] = \frac{1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2}{6} = \frac{1 + 4 + 9 + 16 + 25 + 36}{6} = \frac{91}{6} = 15.17$$

$$\sigma^2 = 15.17 - (3.5)^2 = 15.17 - 12.25 = 2.92$$

**Watch out for:** Sample variance uses $n-1$ in the denominator, not $n$. If the question mentions a "sample" or you're estimating population variance from a subset, use $s^2 = \frac{1}{n-1}\sum(x_i - \bar{x})^2$. This Bessel correction accounts for the fact that your sample probably doesn't capture the full population spread.

---

## Back to Original Units: Standard Deviation

**Intuition:** Variance is useful, but squared units are awkward. If we're measuring profits in millions, variance has units of "(millions)²" — what does that even mean? Standard deviation fixes this by taking the square root, bringing us back to the original units.

**The formula:**

$$\sigma = \sqrt{\sigma^2} = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (x_i - \mu)^2}$$

Think of standard deviation as the "typical distance from the mean."

**Real example from your Week 2 lab (student heights):** From the 50 student height dataset (in cm), the computed statistics were:
- Mean: $\mu = 165.42$ cm
- Variance: $\sigma^2 = 97.15$ cm²
- Standard deviation: $\sigma = \sqrt{97.15} = 9.86$ cm

Now we can say: "The typical student height is within about 10 cm of the mean (165 cm)." Much more intuitive than "variance is 97.15 cm²."

**Real example from your Week 6 lab (dice):** For a fair die with $\sigma^2 = 2.92$:

$$\sigma = \sqrt{2.92} = 1.71$$

This tells us that typical rolls deviate about 1.7 units from the mean of 3.5.

**Slightly harder — the empirical rule:** For normal distributions, roughly 68% of values fall within $\mu \pm \sigma$, 95% within $\mu \pm 2\sigma$, and 99.7% within $\mu \pm 3\sigma$.

From your Week 6 lab (achievement test scores): Scores follow $N(540, 110^2)$, so $\mu = 540$ and $\sigma = 110$. We expect:
- 68% of scores between $540 - 110 = 430$ and $540 + 110 = 650$
- 95% of scores between $540 - 220 = 320$ and $540 + 220 = 760$

The interval $\mu \pm 2\sigma = [320, 760]$ captures most test-takers. From your Week 6 dice exercise, this interval was $[3.5 - 2(1.71), 3.5 + 2(1.71)] = [0.08, 6.92]$, which includes all possible dice outcomes (1 through 6) — 100% of the data.

**Watch out for:** Standard deviation can never be negative. If your calculation gives $\sigma < 0$, you've made an error. Also, standard deviation is sensitive to outliers just like the mean — one extreme value can inflate it significantly.

---

# Part 2: Linear Algebra & Models

Now we move from describing data to modelling it. Linear algebra gives us the mathematical machinery to work with multiple variables at once. These concepts underpin linear regression, neural networks, and most of machine learning.

## Combining Numbers: Dot Product

**Intuition:** Imagine you're calculating a weighted sum. You have a list of values and a list of weights. The dot product multiplies corresponding pairs and adds everything up.

**The formula:**

$$\mathbf{x}^{\mathsf{T}}\mathbf{w} = \sum_{i=1}^{n} x_i w_i = x_1 w_1 + x_2 w_2 + \cdots + x_n w_n$$

The superscript $\mathsf{T}$ means "transpose" (turning a column vector into a row), but don't let notation intimidate you — it's just pairwise multiplication and addition.

**Real example from your Week 3 lab (vectors):** Given:

$$\mathbf{a} = \begin{bmatrix} 1.0 \\ -1.4 \\ 0.0 \\ 10.0 \\ 6.0 \end{bmatrix}, \quad \mathbf{b} = \begin{bmatrix} 3.0 \\ 4.0 \\ 1.0 \\ 1.5 \\ 0.0 \end{bmatrix}$$

Compute $\mathbf{a}^{\mathsf{T}}\mathbf{b}$:

$$\mathbf{a}^{\mathsf{T}}\mathbf{b} = (1.0)(3.0) + (-1.4)(4.0) + (0.0)(1.0) + (10.0)(1.5) + (6.0)(0.0)$$
$$= 3.0 - 5.6 + 0 + 15.0 + 0 = 12.4$$

That's it. Multiply matching positions, add them up. The result is a scalar (single number).

**Another real example from your Week 3 lab:**

$$\mathbf{c} = \begin{bmatrix} 2 \\ 2 \\ 1 \end{bmatrix}, \quad \mathbf{d} = \begin{bmatrix} -1 \\ 0 \\ 1 \end{bmatrix}$$

$$\mathbf{c}^{\mathsf{T}}\mathbf{d} = (2)(-1) + (2)(0) + (1)(1) = -2 + 0 + 1 = -1$$

**Slightly harder — special dot products:** From your Week 3 lab:

- **Sum of all elements:** $\mathbf{1}^{\mathsf{T}}\mathbf{c} = 1(2) + 1(2) + 1(1) = 5$
- **Sum of squares:** $\mathbf{c}^{\mathsf{T}}\mathbf{c} = 2^2 + 2^2 + 1^2 = 9$
- **Extract element:** $\mathbf{e}_2^{\mathsf{T}}\mathbf{b} = 4.0$ (extracts the 2nd element of $\mathbf{b}$)

**Watch out for:** Vectors must have the same length to compute a dot product. Trying to compute $\mathbf{a}^{\mathsf{T}}\mathbf{c}$ (length 5 vs length 3) is undefined — dimensions don't match. Also, the result is always a scalar, never a vector.

---

## Predictions from Data: Matrix Equation $\mathbf{y} = \mathbf{X}\mathbf{w}$

**Intuition:** This is the compact way to write linear regression. Instead of making one prediction at a time, we make predictions for all our data points simultaneously. Each row of $\mathbf{X}$ is one data point, and $\mathbf{w}$ contains the weights that determine the prediction.

**The formula:**

$$\mathbf{y} = \mathbf{X}\mathbf{w}$$

Where:
- $\mathbf{y}$ is an $(n \times 1)$ vector of predictions
- $\mathbf{X}$ is an $(n \times p)$ matrix (n samples, p features)
- $\mathbf{w}$ is a $(p \times 1)$ vector of weights

**Real example from your Week 3 lab (happiness function):** The relationship for computing happiness was:

$$H = 5 + 3 \times \frac{S}{1000} - 1.5 \times A + 5 \times F + 2 \times T$$

where $S$ = salary, $A$ = age, $F$ = number of close friends, $T$ = trips per year.

For a person with salary £2000, age 27, 3 friends, and 1 trip:

$$\mathbf{x} = \begin{bmatrix} 1 \\ 2000 \\ 27 \\ 3 \\ 1 \end{bmatrix}, \quad \mathbf{w} = \begin{bmatrix} 5 \\ 0.003 \\ -1.5 \\ 5 \\ 2 \end{bmatrix}$$

$$H = \mathbf{x}^{\mathsf{T}}\mathbf{w} = 5(1) + 0.003(2000) + (-1.5)(27) + 5(3) + 2(1)$$
$$= 5 + 6 - 40.5 + 15 + 2 = -12.5$$

(The negative happiness score suggests this person needs more trips or friends!)

**Real example from your Week 4 lab (matrix multiplication):** Given:

$$\mathbf{A} = \begin{bmatrix} 1.0 & 3 & 5 & 0.5 \\ -1.4 & 2 & -5 & 1 \\ 0 & -1 & 4 & 6 \end{bmatrix}, \quad \mathbf{C} = \begin{bmatrix} 1 \\ -1 \\ 1 \\ 1 \end{bmatrix}$$

Compute $\mathbf{A}\mathbf{C}$ (dimensions: $(3 \times 4)(4 \times 1) \to (3 \times 1)$):

$$\mathbf{A}\mathbf{C} = \begin{bmatrix} 1(1) + 3(-1) + 5(1) + 0.5(1) \\ -1.4(1) + 2(-1) + (-5)(1) + 1(1) \\ 0(1) + (-1)(-1) + 4(1) + 6(1) \end{bmatrix} = \begin{bmatrix} 3.5 \\ -7.4 \\ 11 \end{bmatrix}$$

Each element is just the dot product of a row of $\mathbf{A}$ with vector $\mathbf{C}$.

**Watch out for:** Matrix dimensions must align. If $\mathbf{X}$ is $(n \times p)$, then $\mathbf{w}$ must be $(p \times 1)$, yielding $\mathbf{y}$ as $(n \times 1)$. If dimensions don't match, the multiplication is undefined.

---

## Finding the Best Weights: Pseudo-inverse $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}$

**Intuition:** You've got data $\mathbf{X}$ and outcomes $\mathbf{y}$, and you want to find the weights $\mathbf{w}$ that best predict $\mathbf{y}$ from $\mathbf{X}$. This formula gives you the least squares solution — the $\mathbf{w}$ that minimises the sum of squared errors.

**The formula:**

$$\hat{\mathbf{w}} = (\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}\mathbf{y}$$

This looks intimidating, but break it down:
1. Compute $\mathbf{X}^{\mathsf{T}}\mathbf{X}$ (a $p \times p$ square matrix)
2. Invert it to get $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}$
3. Multiply by $\mathbf{X}^{\mathsf{T}}\mathbf{y}$

**Real example from your Week 4 lab:** One of your exercises was to compute $\mathbf{w} = (\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}\mathbf{y}$ for given data matrices. The process:

Given:

$$\mathbf{X} = \begin{bmatrix} 1 & 2 & 0 \\ 2 & 1 & 3 \\ 1 & 3 & 4 \end{bmatrix}, \quad \mathbf{y} = \begin{bmatrix} 5 \\ 7 \\ 9 \end{bmatrix}$$

Step 1: Compute $\mathbf{X}^{\mathsf{T}}\mathbf{X}$:

$$\mathbf{X}^{\mathsf{T}} = \begin{bmatrix} 1 & 2 & 1 \\ 2 & 1 & 3 \\ 0 & 3 & 4 \end{bmatrix}$$

$$\mathbf{X}^{\mathsf{T}}\mathbf{X} = \begin{bmatrix} 6 & 7 & 11 \\ 7 & 14 & 15 \\ 11 & 15 & 25 \end{bmatrix}$$

Step 2: Invert $\mathbf{X}^{\mathsf{T}}\mathbf{X}$ (using calculator or software)

Step 3: Compute $\mathbf{X}^{\mathsf{T}}\mathbf{y}$:

$$\mathbf{X}^{\mathsf{T}}\mathbf{y} = \begin{bmatrix} 1(5) + 2(7) + 1(9) \\ 2(5) + 1(7) + 3(9) \\ 0(5) + 3(7) + 4(9) \end{bmatrix} = \begin{bmatrix} 28 \\ 44 \\ 57 \end{bmatrix}$$

Step 4: Multiply to get $\hat{\mathbf{w}}$

**Watch out for:** Order matters! Compute $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}$ first, then multiply by $\mathbf{X}^{\mathsf{T}}$. You can't invert $\mathbf{X}^{\mathsf{T}}$ alone — it's not square. Also, if columns of $\mathbf{X}$ are linearly dependent (e.g., one feature is an exact multiple of another), $\mathbf{X}^{\mathsf{T}}\mathbf{X}$ is singular and can't be inverted.

---

## Binary Decisions: Step Function

**Intuition:** Sometimes we need to convert a continuous score into a binary decision: "yes or no," "spam or not spam," "pass or fail." The step function does exactly this — it outputs 1 if the input is non-negative, and 0 otherwise.

**The formula:**

$$f(x) = \begin{cases} 1 & \text{if } x \geq 0 \\ 0 & \text{if } x < 0 \end{cases}$$

Also called the Heaviside function or threshold function.

**Real example from your course concepts:** If a prediction model computes a score, the step function converts it to a classification.

- If happiness score $H = 5.2 \implies f(5.2) = 1$ (happy)
- If happiness score $H = -12.5 \implies f(-12.5) = 0$ (not happy)
- If happiness score $H = 0 \implies f(0) = 1$ (happy — note that zero counts as "on")

**Real example from your Week 3 lab (piecewise functions):** You evaluated:

$$f(t) = \begin{cases} -2t & \text{if } t > 0 \\ t & \text{if } t \leq 0 \end{cases}$$

This is similar in structure: different output depending on the input region.
- $f(-1) = -1$ (since $-1 \leq 0$, use second rule)
- $f(0) = 0$ (boundary case, use $t \leq 0$ rule)
- $f(1) = -2$ (since $1 > 0$, use first rule)

**Watch out for:** The threshold includes zero: $f(0) = 1$. Some definitions use $x > 0$ (strict inequality), but the standard convention is $x \geq 0$. Check what your course uses. Also, the step function isn't differentiable at $x=0$ (it has a discontinuous jump), which is why modern neural networks use smooth activations like sigmoid or ReLU instead.

---

## Concrete Example: A Linear Model

**Intuition:** Let's make this real using your Week 3 lab happiness function.

**The formula (from your lab):**

$$H = f(S, A, F, T) = 5 + 3 \times \frac{S}{1000} - 1.5 \times A + 5 \times F + 2 \times T$$

This is $f(\mathbf{x}) = w_0 + w_1 x_1 + w_2 x_2 + w_3 x_3 + w_4 x_4$ with concrete numbers:
- Intercept: $w_0 = 5$
- Salary coefficient: $w_1 = 0.003$ (each £1000 adds 3 to happiness)
- Age coefficient: $w_2 = -1.5$ (each year subtracts 1.5 from happiness)
- Friends coefficient: $w_3 = 5$ (each friend adds 5 to happiness)
- Trips coefficient: $w_4 = 2$ (each trip adds 2 to happiness)

**Real example from your lab:** For person P (salary £2000, age 27, 3 friends, 1 trip):

$$H = 5 + 3(2) - 1.5(27) + 5(3) + 2(1) = 5 + 6 - 40.5 + 15 + 2 = -12.5$$

**What does each coefficient mean?**
- **Friends = 5:** Most important factor. Losing one friend decreases happiness by 5.
- **Trips = 2:** Each trip adds 2 to happiness. From Exercise 4.5, to make up for losing one friend (−5 happiness), you'd need 3 additional trips ($3 \times 2 = 6 > 5$).
- **Age = −1.5:** Happiness decreases by 1.5 each year (if everything else stays constant).
- **Salary = 0.003:** Least important. A £1000 raise only adds 3 to happiness.

**Real prediction from your lab:** If person P's age increases by 10 years (all else constant):

$$H = 5 + 6 - 1.5(37) + 15 + 2 = -12.5 - 15 = -27.5$$

The happiness drops by exactly $1.5 \times 10 = 15$ points.

**Watch out for:** Sign errors are common. $-1.5 \times 27 = -40.5$, not $+40.5$. Also, remember that coefficients show the effect of changing one variable while holding others constant — they don't imply causation.

---

## Describing Function Types: $f: \mathbb{R}^3 \to \mathbb{R}$

**Intuition:** This notation is about being precise. Before we even write a formula, we specify what type of input and output the function has.

**The notation:**

$$f: \mathbb{R}^3 \to \mathbb{R}$$

- $\mathbb{R}^3$ means "3-dimensional real space" (inputs are triples like $(x_1, x_2, x_3)$)
- $\to$ means "maps to"
- $\mathbb{R}$ means "real numbers" (output is a single value)

**Real example from your Week 3 lab:** The happiness function (before we added trips) had 4 inputs:

$$H: \mathbb{R}^4 \to \mathbb{R}$$

because $H = f(S, A, F, T)$ takes 4 real numbers and outputs 1 real number.

**Another real example from your lab:** The piecewise function:

$$f(t) = \begin{cases} -2t & \text{if } t > 0 \\ t & \text{if } t \leq 0 \end{cases}$$

has type $f: \mathbb{R} \to \mathbb{R}$ (one input, one output).

**Slightly harder — matrix functions:** From your Week 4 lab, matrix multiplication:

$$g(\mathbf{X}, \mathbf{w}) = \mathbf{X}\mathbf{w}$$

If $\mathbf{X}$ is $(n \times p)$ and $\mathbf{w}$ is $(p \times 1)$, then:

$$g: \mathbb{R}^{n \times p} \times \mathbb{R}^p \to \mathbb{R}^n$$

(Takes a matrix and vector, outputs a vector.)

**Watch out for:** $\mathbb{R}^3 \to \mathbb{R}$ is very different from $\mathbb{R} \to \mathbb{R}^3$. The first takes three inputs and gives one output; the second takes one input and gives three outputs. Arrow direction matters!

---

# Part 3: Probability

Probability quantifies uncertainty. These two rules — addition (for "or") and Bayes' theorem (for flipping conditionals) — are the foundation of everything that follows.

## Combining Events: Addition Rule

**Intuition:** You want to know the probability of "A or B" (at least one happens). The naive approach is to add $P(A) + P(B)$, but that double-counts the overlap — cases where both A and B happen. So we subtract $P(A \cap B)$ once to correct it.

**The formula:**

$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$

Read "$\cup$" as "union" (or), and "$\cap$" as "intersection" (and).

**Real example from your Week 5 lab (newspaper readership):** In a town of 100,000 people, the newspaper readership is:

- Newspaper I: 10,000 people (10%)
- Newspaper II: 30,000 people (30%)
- Both I and II: 8,000 people (8%)

What's the probability that a randomly selected person reads at least one of these papers?

$$P(I \cup II) = P(I) + P(II) - P(I \cap II) = 0.10 + 0.30 - 0.08 = 0.32$$

So 32,000 people read at least one paper.

**Real example from your Week 5 lab (rain problem):** Given:
- 60% chance it rains today ($P(T) = 0.6$)
- 50% chance it rains tomorrow ($P(M) = 0.5$)
- 30% chance it doesn't rain either day ($P(T' \cap M') = 0.3$)

Find: Probability it rains today OR tomorrow.

$$P(T \cup M) = 1 - P(T' \cap M') = 1 - 0.3 = 0.7$$

Alternatively, we can find $P(T \cap M)$ first:

$$P(T \cap M) = P(T) + P(M) - P(T \cup M) = 0.6 + 0.5 - 0.7 = 0.4$$

**Slightly harder (three newspapers):** From your Week 5 lab, with three newspapers I, II, III:

$$P(I \cup II \cup III) = P(I) + P(II) + P(III)$$
$$- P(I \cap II) - P(II \cap III) - P(I \cap III) + P(I \cap II \cap III)$$

With the given data:
$$= 0.10 + 0.30 + 0.05 - 0.08 - 0.04 - 0.02 + 0.01 = 0.32$$

So 32% read at least one newspaper, meaning 68% read none.

**Watch out for:** Don't forget to subtract the overlap! A common mistake is to compute $P(A) + P(B)$ and stop there. Also, if A and B are mutually exclusive (can't both happen), then $P(A \cap B) = 0$, and the formula simplifies to $P(A \cup B) = P(A) + P(B)$.

---

## Reversing Conditionals: Bayes' Theorem

**Intuition:** You know $P(B|A)$ (probability of B given A), but you need $P(A|B)$ (probability of A given B). Bayes' theorem lets you "flip" the conditional.

**The formula:**

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

Often expanded using the law of total probability:

$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B|A) \cdot P(A) + P(B|A^c) \cdot P(A^c)}$$

**Real example from your Week 5 lab (criminal investigation):** An inspector is 60% convinced of a suspect's guilt. New evidence shows the criminal has a certain characteristic (like left-handedness). If 20% of the population has this characteristic, how certain should the inspector be if the suspect has it?

Let $G$ = suspect is guilty, $C$ = has the characteristic.

Given:
- $P(G) = 0.6$ (prior belief)
- $P(C) = 0.2$ (population rate)
- $P(C|G) = 1$ (if guilty, definitely has the characteristic — this is implied)

$$P(G|C) = \frac{P(C|G) \cdot P(G)}{P(C|G) \cdot P(G) + P(C|G^c) \cdot P(G^c)}$$

$$= \frac{(1)(0.6)}{(1)(0.6) + (0.2)(0.4)} = \frac{0.6}{0.6 + 0.08} = \frac{0.6}{0.68} = 0.882$$

The inspector should now be 88.2% certain of guilt (up from 60%).

**Real example from your Week 5 lab (coin urn):** An urn contains two type A coins (heads probability 1/4) and one type B coin (heads probability 3/4). You randomly pick a coin, flip it, and get heads. What's the probability it was type A?

Let $A$ = type A coin, $H$ = heads.

Given:
- $P(A) = 2/3$, $P(B) = 1/3$
- $P(H|A) = 1/4$, $P(H|B) = 3/4$

$$P(A|H) = \frac{P(H|A) \cdot P(A)}{P(H|A) \cdot P(A) + P(H|B) \cdot P(B)}$$

$$= \frac{(1/4)(2/3)}{(1/4)(2/3) + (3/4)(1/3)} = \frac{1/6}{1/6 + 1/4} = \frac{1/6}{5/12} = \frac{2}{5} = 0.4$$

Only 40% chance it was type A, even though there are twice as many type A coins! The higher heads probability of type B makes it more likely.

**Watch out for:** Don't confuse $P(A|B)$ with $P(B|A)$ — they're usually very different. In the medical test example from your notes: $P(\text{positive}|\text{disease}) = 0.95$ (test sensitivity) but $P(\text{disease}|\text{positive})$ might only be 0.088 (8.8%) when the disease is rare.

---

# Part 4: Random Variables & Distributions

We now move from events to random variables — quantities whose values are determined by chance. These formulas describe the most important distributions you'll encounter.

## The Standard: Normal Distribution $X \sim \mathcal{N}(0,1)$

**Intuition:** The normal (or Gaussian) distribution is the bell curve. It's symmetric around the mean, with most values near the centre and fewer values farther out. The notation $X \sim \mathcal{N}(0,1)$ specifically means a **standard normal**: mean 0, variance 1.

**The notation:**

$$X \sim \mathcal{N}(0, 1)$$

This tells you three things:
- $X$ is a random variable
- It follows a normal distribution ($\mathcal{N}$)
- Mean = 0, variance = 1

**Real example from your Week 6 lab (achievement test):** Scores follow $\mathcal{N}(540, 110^2)$. Convert a score of 680 to standard normal:

$$Z = \frac{X - \mu}{\sigma} = \frac{680 - 540}{110} = \frac{140}{110} = 1.273$$

A score of 680 is 1.273 standard deviations above the mean. From Z-tables, $P(Z \leq 1.273) \approx 0.898$, so this person scored higher than about 89.8% of test-takers.

What percentage scored higher? $P(Z > 1.273) = 1 - 0.898 = 0.102$ (about 10.2%).

**Real example from your Week 6 lab (dice distribution):** For a fair die, the interval $\mu \pm 2\sigma = [3.5 - 2(1.71), 3.5 + 2(1.71)] = [0.08, 6.92]$ contains all possible outcomes (1-6), representing 100% of the data — exactly as expected by the empirical rule.

**Slightly harder (comparing distributions):** From Week 6 Exercise 8, you computed probabilities for three normal distributions:

1. $X \sim N(0, 1)$: $P(-2 \leq X \leq 2) = 0.9544$ (95.44%)
2. $Y \sim N(2, 4)$: $P(-2 \leq Y \leq 2)$ requires standardizing: $Y' = \frac{Y-2}{2}$
   - When $Y = -2$: $Y' = \frac{-2-2}{2} = -2$
   - When $Y = 2$: $Y' = \frac{2-2}{2} = 0$
   - So $P(-2 \leq Y \leq 2) = P(-2 \leq Y' \leq 0) = 0.5 - 0.0228 = 0.4772$ (47.72%)

**Watch out for:** The notation $\mathcal{N}(\mu, \sigma^2)$ uses **variance** (squared standard deviation), not standard deviation itself. If you see $\mathcal{N}(2, 4)$, that's mean 2 and variance 4, so $\sigma = 2$, not $\sigma = 4$.

---

## Centre of Mass: Expected Value $\mathbb{E}[X]$

**Intuition:** If you repeated a random process infinitely many times and averaged the results, you'd get the expected value. It's the long-run average.

**The formula:**

$$\mathbb{E}[X] = \sum_{x} x \cdot P(X = x) \quad \text{(discrete)}$$

For discrete: weight each value by its probability, then sum.

**Real example from your Week 6 lab (dice):** Roll a fair six-sided die. What's $\mathbb{E}[X]$?

$$\mathbb{E}[X] = 1 \cdot \frac{1}{6} + 2 \cdot \frac{1}{6} + 3 \cdot \frac{1}{6} + 4 \cdot \frac{1}{6} + 5 \cdot \frac{1}{6} + 6 \cdot \frac{1}{6}$$
$$= \frac{1+2+3+4+5+6}{6} = \frac{21}{6} = 3.5$$

**Real example from your Week 6 lab (coffee breaks):** From the coffee break data:

| $x$ | 0 | 1 | 2 | 3 | 4 | 5 |
|-----|---|---|---|---|---|---|
| $P(X=x)$ | 0.28 | 0.37 | 0.13 | 0.09 | 0.08 | 0.05 |

$$\mathbb{E}[X] = 0(0.28) + 1(0.37) + 2(0.13) + 3(0.09) + 4(0.08) + 5(0.05)$$
$$= 0 + 0.37 + 0.26 + 0.27 + 0.32 + 0.25 = 1.47$$

Wait, that doesn't match the lab answer (1.32). Let me recalculate with corrected frequencies from the lab...

Actually, looking at the lab answer: $\mathbb{E}[X] = 1.32$ coffee breaks per day.

**Slightly harder — linearity:** Expected value is **linear**: $\mathbb{E}[aX + b] = a\mathbb{E}[X] + b$.

From your Week 3 happiness function: If salary increases by £1000 (all else constant), happiness increases by $0.003 \times 1000 = 3$ on average.

**Watch out for:** Expected value might not be a possible outcome. You can't take 1.32 coffee breaks, but it's still the expected value. Also, for specific distributions (binomial, Poisson, etc.), there are shortcut formulas — use them instead of summing from scratch.

---

## Measuring Spread: Variance of a Random Variable $\text{Var}(X)$

**Intuition:** Variance quantifies how spread out a random variable is. It's the average squared distance from the mean.

**The formula:**

$$\text{Var}(X) = \mathbb{E}[(X - \mu)^2] = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$$

The second form ("expected value of squares minus square of expected value") is usually easier to compute.

**Real example from your Week 6 lab (dice):** For a fair die with $\mathbb{E}[X] = 3.5$:

$$\mathbb{E}[X^2] = 1^2 \cdot \frac{1}{6} + 2^2 \cdot \frac{1}{6} + 3^2 \cdot \frac{1}{6} + 4^2 \cdot \frac{1}{6} + 5^2 \cdot \frac{1}{6} + 6^2 \cdot \frac{1}{6}$$
$$= \frac{1 + 4 + 9 + 16 + 25 + 36}{6} = \frac{91}{6} = 15.17$$

$$\text{Var}(X) = 15.17 - (3.5)^2 = 15.17 - 12.25 = 2.92$$

Standard deviation: $\sigma = \sqrt{2.92} = 1.71$

**Real example from your Week 6 lab (coffee breaks):** With $\mathbb{E}[X] = 1.32$, the lab calculated $\text{Var}(X) = 1.4376$, so $\sigma = \sqrt{1.4376} = 1.20$.

**Slightly harder — the $\mu \pm 2\sigma$ interval:** From your Week 6 coffee lab:

$$[\mu - 2\sigma, \mu + 2\sigma] = [1.32 - 2(1.20), 1.32 + 2(1.20)] = [-1.08, 3.72]$$

For discrete data, this means $0 \leq X \leq 3$:

$$P(0 \leq X \leq 3) = 0.28 + 0.37 + 0.13 + 0.09 = 0.87$$

So 87% of coffee drinkers fall within 2 standard deviations (close to the 95% rule for continuous normal distributions).

**Watch out for:** Variance has squared units. If $X$ is number of coffee breaks, $\text{Var}(X)$ is in "(coffee breaks)²". Take the square root to get standard deviation (original units).

---

## Counting Successes: Binomial Distribution

**Intuition:** You're running $n$ independent trials, each with probability $p$ of success. The binomial distribution tells you the probability of getting exactly $k$ successes.

**The formula:**

$$P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}$$

Where $\binom{n}{k} = \frac{n!}{k!(n-k)!}$ is "n choose k."

Expected value: $\mathbb{E}[X] = np$
Variance: $\text{Var}(X) = np(1-p)$

**Real example from your Week 6 lab (hotel overbooking):** A hotel has 200 rooms but accepts 215 reservations. On average, 10% of guests don't show up (no-show rate). What's the probability all arriving guests get rooms?

This is binomial with $n = 215$ trials (reservations), $p = 0.9$ (probability of showing up).

We need $P(X \leq 200)$ where $X$ = number of guests who show up.

Since $n$ is large and $np = 193.5 > 5$ and $nq = 21.5 > 5$, we can approximate with normal:

$$X \sim N(\mu = np = 193.5, \sigma = \sqrt{npq} = \sqrt{215 \times 0.9 \times 0.1} = \sqrt{19.35} = 4.399)$$

Standardize $X = 200$:

$$Z = \frac{200 - 193.5}{4.399} = \frac{6.5}{4.399} = 1.478$$

From Z-tables: $P(Z \leq 1.478) \approx 0.931$ (93.1% chance all guests get rooms).

**Real example from your Week 6 lab (defective chips):** Six computer chips, two defective. Pick three at random. This looks like binomial but **isn't** — because sampling without replacement changes the probabilities. From your lab:

$$P(X = 0) = \frac{\binom{2}{0}\binom{4}{3}}{\binom{6}{3}} = \frac{1 \times 4}{20} = \frac{1}{5}$$

$$P(X = 1) = \frac{\binom{2}{1}\binom{4}{2}}{\binom{6}{3}} = \frac{2 \times 6}{20} = \frac{3}{5}$$

$$P(X = 2) = \frac{\binom{2}{2}\binom{4}{1}}{\binom{6}{3}} = \frac{1 \times 4}{20} = \frac{1}{5}$$

This is a **hypergeometric** distribution, not binomial.

**Watch out for:** The $\binom{n}{k}$ term is crucial — it counts arrangements. Without it, you're only computing the probability of one specific sequence. Also, binomial requires **independence** — if trials affect each other (like drawing without replacement), it's not binomial.

---

## The Bell Curve: Normal PDF

**Intuition:** The normal probability density function (PDF) is the formula for the bell curve.

**The formula:**

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

**Real example from your Week 6 lab:** For standard normal $N(0,1)$, at $x = 0$ (the peak):

$$f(0) = \frac{1}{\sqrt{2\pi}} \approx 0.399$$

**Real example (achievement test):** For $N(540, 110^2)$, the peak is at $x = 540$:

$$f(540) = \frac{1}{110\sqrt{2\pi}} = \frac{0.399}{110} \approx 0.0036$$

**From your Week 6 lab (computing probabilities):** To find $P(-2 \leq X \leq 2)$ for $X \sim N(0,1)$:

$$P(-2 \leq X \leq 2) = \Phi(2) - \Phi(-2) = 0.9772 - 0.0228 = 0.9544$$

Where $\Phi$ is the cumulative distribution function (area under the curve).

**Watch out for:** The PDF value $f(x)$ is **not** a probability. For continuous distributions, $P(X = x) = 0$ always. The PDF is a density — probabilities come from integrating (finding areas under the curve).

---

## Events at a Rate: Poisson

**Intuition:** The Poisson distribution models the number of events occurring in a fixed interval when events happen at a constant average rate $\lambda$ (and independently).

**The formula:**

$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$

Expected value: $\mathbb{E}[X] = \lambda$
Variance: $\text{Var}(X) = \lambda$ (same as the mean!)

**Real example from your concepts (not explicit in labs but referenced):** If machine breakdowns occur at rate $\lambda = 3.4$ per week:

$$P(X = 0) = \frac{3.4^0 e^{-3.4}}{0!} = \frac{1 \times 0.0334}{1} = 0.0334$$

About 3.3% chance of zero breakdowns.

**Poisson approximation to binomial:** From your Week 6 lab notes, when $n > 50$ and $p < 0.1$, use Poisson with $\lambda = np$.

For the hotel: $n = 215$, $p = 0.1$ (no-show), so $\lambda = 21.5$. But since we wanted "show-up" probability, we used normal approximation instead (because $p = 0.9$ is not small).

**Watch out for:** $\lambda$ can be any positive number — it's not a probability. Remember $0! = 1$, so $P(X = 0) = e^{-\lambda}$.

---

# Putting It All Together

You now have the formulas that connect data description, linear models, probability, and distributions. Here's how they fit:

**Start with data (Week 2):** Compute mean (centre) and variance/std dev (spread) for the firm profit data, student heights.

**Model relationships (Weeks 3-4):** Use dot products and matrices to build the happiness function. Find optimal weights with the pseudo-inverse for prediction problems.

**Handle uncertainty (Week 5):** Apply probability rules (addition for newspaper readership, Bayes for criminal investigation) to quantify and update beliefs.

**Work with distributions (Week 6):** Model hotel overbooking with binomial (approximated by normal), test scores with normal distribution, compute expected coffee breaks.

These aren't isolated facts — they're a connected toolkit. Mean and variance appear everywhere: describing data samples, characterising probability distributions. The dot product underlies linear models. Bayes' theorem connects conditional probabilities to real-world inference.

---

# Quick Reference Cheat Sheet

| **Formula** | **What It Does** | **Real Example (Your Labs)** |
|-------------|------------------|------------------------------|
| $\mu = \frac{1}{n}\sum x_i$ | Mean | Firm profits: £2.183M |
| $\sigma^2 = \frac{1}{n}\sum (x_i - \mu)^2$ | Variance | Height data: 97.15 cm² |
| $\sigma = \sqrt{\sigma^2}$ | Standard deviation | Height: 9.86 cm |
| $\mathbf{x}^{\mathsf{T}}\mathbf{w} = \sum x_i w_i$ | Dot product | $\mathbf{a}^T\mathbf{b} = 12.4$ |
| $\mathbf{y} = \mathbf{X}\mathbf{w}$ | Linear model | Happiness: $H = -12.5$ |
| $(\mathbf{X}^{\mathsf{T}}\mathbf{X})^{-1}\mathbf{X}^{\mathsf{T}}$ | Pseudo-inverse | Week 4 optimal weights |
| $f(x) = 1$ if $x \geq 0$, else $0$ | Step function | Happy/not happy threshold |
| $H = 5 + 0.003S - 1.5A + 5F + 2T$ | Concrete model | Your happiness function |
| $f: \mathbb{R}^4 \to \mathbb{R}$ | Function type | Happiness: 4 inputs → 1 output |
| $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ | Addition rule | Newspapers: 32% read ≥1 |
| $P(A\|B) = \frac{P(B\|A) P(A)}{P(B)}$ | Bayes' theorem | Inspector: 60% → 88.2% certain |
| $X \sim \mathcal{N}(0,1)$ | Standard normal | Test score: $z = 1.273$ |
| $\mathbb{E}[X]$ | Expected value | Dice: 3.5, Coffee: 1.32 |
| $\text{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$ | Variance | Dice: 2.92 |
| $P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$ | Binomial | Hotel: 93.1% success |
| $f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$ | Normal PDF | Peak at $\mu$ |
| $P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$ | Poisson | Rate $\lambda$ events |

---

**Final Thoughts**

This guide uses **your** actual course materials. Every example comes from the labs you've worked on. When you see the firm profit data, the happiness function, the newspaper problem, or the hotel overbooking scenario — these aren't abstract examples. They're from your exercises, with your numbers, following your course's approach.

Don't just memorise symbols — understand why each formula exists and when to use it. Test yourself: cover the formula, explain it in plain English using one of the real examples, then check if you were right.

You're not memorising isolated facts. You're building a mental model of statistics using the concrete examples from your own learning journey.

Now go practise. Work through the problems. Make mistakes. Learn from them. That's how fluency happens.

Good luck on the quiz.
