# AI Snake Oil: Comprehensive Summary

**By Arvind Narayanan & Sayash Kapoor (Princeton University Press, 2024)**

*Research compiled for Finn McKie, January 2026*

---

## 1. Book Summary: Main Thesis and Key Arguments

### Core Thesis
"AI Snake Oil" argues that much of what is marketed as AI today doesn't work and probably never will. The authors distinguish between AI that genuinely functions (like generative AI) and "snake oil" AI—products sold on hype rather than proven capability.

### Central Argument
**"We should be far more concerned about what people will do with AI than with what AI will do on its own."**

The book's mission: help readers develop the literacy to identify AI snake oil and distinguish it from AI that can work well when used appropriately.

### Key Arguments:
1. **Broken AI appeals to broken institutions** - The demand for AI snake oil comes from dysfunctional organizations seeking quick fixes. HR departments drowning in applications, courts seeking "objective" sentencing tools, schools wanting automated student evaluation—these broken systems create demand for technological solutions that don't work.

2. **The capability-reliability gap** - AI often performs impressively in benchmarks but fails catastrophically in real-world deployment. Laboratory performance doesn't translate to practical utility.

3. **Predictive AI is fundamentally limited** - The book draws a sharp distinction between generative AI (which has genuine capabilities) and predictive AI (which makes claims about predicting human behavior that are largely unfounded).

4. **AI hype serves commercial interests** - Companies, journalists, and even researchers have incentives to overstate AI capabilities, creating a self-reinforcing cycle of exaggeration.

5. **Existential risk discourse distracts from present harms** - The focus on hypothetical superintelligent AI diverts attention from the actual damage being caused by deployed AI systems today.

---

## 2. Chapter Breakdown

### Chapter 1: Introduction
- Authors' backgrounds and what brought them to write the book
- Defines "AI snake oil" as AI that "does not and cannot work as advertised"
- Examples: Allstate's 2013 predictive AI, concerns about AI replicating actors' likenesses, 2023 Writers Guild strikes
- Discusses false arrests of six Black individuals due to facial recognition errors
- Comparison to the Industrial Revolution's labor displacement

### Chapter 2: Predictive AI
- Critical examination of predictive AI's overestimated capabilities
- Key examples:
  - **EAB Navigate** - Student success prediction tool
  - **COMPAS** - Criminal sentencing risk prediction software
- Argues that most predictive AI uses decades-old statistical techniques, not modern AI

### Chapter 3: The History of Prediction
- Traces early computational prediction attempts
- Discusses **Simulmatics Corporation** - a 1960s precursor to modern predictive analytics
- Shows that the dream of computational prediction has a long history of failure

### Chapter 4: The Long Road to Generative AI
- Historical overview from Frank Rosenblatt's **perceptron** to modern transformers
- **Be My Eyes** - Positive example: visual assistance app for blind users
- **Chai chatbot** - Negative example: Belgian man's suicide after extended interaction
- Discusses deepfakes, particularly non-consensual pornographic content
- Technical explanation of neural networks, support vector machines, and deep learning
- Recognition of **Fei-Fei Li's ImageNet** and its role in AI development

### Chapter 5: Is Advanced AI an Existential Threat?
- Examines AGI (Artificial General Intelligence) claims
- Introduces the **"Ladder of Generality"**:
  - Rung 0: Special-purpose hardware
  - Rung 1: Programmable computers
  - Rung 2: Stored program computers
  - Rung 3: Machine learning
  - Rung 4: Deep learning
  - Rung 5: Pretrained models
  - Rung 6: Instruction-tuned models
  - Rung 7+: Unknown (the authors argue we can't see what's next, or if there's a dead end)
- Discusses the **ELIZA effect** - our tendency to attribute more intelligence to responsive programs than they possess
- Key argument: AGI threat would only exist if AI functioned reliably, which it doesn't

### Chapter 6: Why AI Can't Fix Social Media
- Content moderation's reliance on AI and its failures
- Machines can't understand context and nuance
- **Fingerprint matching** vs **machine learning** approaches to moderation
- Hidden labor: content moderation outsourced to developing countries
- Psychological toll on human moderators

### Chapter 7: Why Do Myths About AI Persist?
- **Epic's sepsis prediction model** - Promised breakthrough, only 63% accuracy (near random)
- Sources of hype:
  - Companies (greed, shareholder pressure)
  - Journalists (financial incentives over accuracy)
  - Researchers (publication pressure, grant seeking)
- Problem of "company statement regurgitation" in news media
- Anthropomorphization of AI to cut labor costs

### Chapter 8: The Future of AI
- Authors' predictions for AI's evolution
- Call for democratic engagement and resistance to surveillance AI
- Warning about power concentration in tech companies

---

## 3. Key Claims: The "Snake Oil" Patterns

### Pattern 1: Predictive AI in High-Stakes Decisions
**Claim:** AI systems that claim to predict individual human behavior (criminality, job performance, academic success) don't work and cause real harm.

**Examples:**
- Criminal risk prediction tools
- Hiring AI that screens candidates
- Child maltreatment prediction
- Insurance risk assessment

### Pattern 2: The Benchmark Illusion
**Claim:** AI benchmark performance doesn't translate to real-world utility.

**Quote:** "The easier a task is to measure via benchmarks, the less likely it is to represent the kind of complex, contextual work that defines professional practice."

**Examples:**
- GPT-4 scoring in top 10% on bar exam but unable to practice law
- Coding benchmarks vs. real software engineering
- Self-driving car demonstrations vs. road safety

### Pattern 3: The Innovation-Diffusion Lag
**Claim:** AI methods advance rapidly, but AI adoption in high-stakes domains is (appropriately) slow—often decades behind the technology.

**Key insight:** In predictive optimization applications (criminal risk, insurance, child welfare), most deployed systems use decades-old regression models, not modern AI.

### Pattern 4: The Anthropomorphization Trap
**Claim:** Companies deliberately encourage people to think of AI as human-like to justify replacing workers and avoiding accountability.

### Pattern 5: The Existential Risk Distraction
**Claim:** Debates about superintelligent AI and existential risk distract from present harms.

**Quote:** "Maybe we should take existential risk seriously, I don't dispute that. But the interventions that are being proposed—either we should find some magic bullet technical breakthrough, or we should slow down this tech, or ban this tech, or limit it to a very small number of companies—all of those are really problematic."

---

## 4. Notable Examples

### Cases of AI Failure:

| System | Domain | Failure |
|--------|--------|---------|
| **Epic Sepsis Prediction** | Healthcare | Only 63% accuracy (near random), missed 2/3 of sepsis cases, overwhelmed physicians with false alerts |
| **COMPAS** | Criminal justice | Biased against Black defendants, not more accurate than untrained humans |
| **CNET AI Writer** | Journalism | Published articles riddled with factual errors |
| **Bing Sydney** | Chatbot | Went "off the rails" in extended conversations; developers hadn't tested long interactions |
| **Gemini Image Generator** | Image generation | Historical accuracy failures; "seemingly never tested on historical figures" |
| **Facial Recognition** (various) | Law enforcement | Six Black individuals falsely arrested |

### Cases of AI Working:

| System | Domain | Success |
|--------|--------|---------|
| **Be My Eyes** | Accessibility | Genuinely helps visually impaired users navigate environments |
| **Language Translation** | NLP | LLMs have made translation "relatively trivial" |
| **Weather Forecasting** | Prediction | Works because it's based on physics, not social behavior |

### The Sepsis Prediction Story (Detailed)
Epic's sepsis prediction tool became the authors' key cautionary tale:
- Internally validated with "high accuracy"
- Deployed in hospitals and performed terribly
- **Root cause:** The model used whether a physician had *already prescribed antibiotics* (to treat sepsis) as a feature—essentially using a feature from the future
- Demonstrates why complex, opaque models are dangerous in high-stakes settings

---

## 5. Connection to Peterson's "Abstracted Power" Concept

*Note: Direct documentation of Dr. Tina Peterson's "abstracted power" concept was not found in this research. The following connection is inferred from the book's themes.*

### Likely Connections:

**1. Power Laundering Through Technology**
AI Snake Oil describes how institutional power is "laundered" through AI systems. When a judge uses COMPAS to inform sentencing, or HR uses AI to screen candidates, human decisions become obscured behind technical processes. This is a form of **abstracted power**—authority exercised at a distance, made invisible, and rendered difficult to challenge.

**2. The Demand Side of Snake Oil**
The book argues that "broken AI appeals to broken institutions." Peterson's concept likely addresses how power structures create *demand* for these systems—they want to abstract away difficult decisions, avoid accountability, and claim objectivity.

**3. Hidden Labor, Hidden Power**
The book discusses content moderation outsourced to workers in developing countries. The "AI" is actually human labor, abstracted away. This fits Peterson's framework: power operates through layers of abstraction that obscure who is actually making decisions and who bears the costs.

**4. Algorithmic Governance**
AI Snake Oil warns about "a world where AI continues to be controlled by largely unaccountable big tech companies." This concentration of power operates through abstraction—users interact with interfaces, not decisions; with outputs, not the humans and values encoding them.

**Key Quote That Likely Resonates:**
"We should be far more concerned about what people will do with AI than with what AI will do on its own."

This frames AI as a *tool of power* rather than an autonomous agent—exactly the kind of analysis Peterson's "abstracted power" concept would support.

---

## 6. Reviews and Reception

### Awards and Recognition:
- **Nature** Best Book of the Year
- **Publishers Weekly** Fall Science Preview Top 10
- **Behavioral Scientist** Notable Book of the Year
- **Forbes** Must-Read Tech Book of the Year
- **UK Tech News** Best Technology Book of the Year
- **PROSE Award Finalist** in Computing and Information Sciences (Association of American Publishers)
- Authors named to **TIME 100 AI** list (2023)

### Positive Reviews:

**Publishers Weekly:**
"A capable examination of AI's limitations... offers a solid overview of AI's defects."

**General Academic Reception:**
Praised for translating technical concepts for general audiences while maintaining rigor. The book filled a gap between academic AI criticism and accessible public writing.

### Criticisms:

**Edward Ongweso Jr. (cited in Wikipedia):**
- Lack of discussion outside the West
- Insufficient focus on who controls the power surrounding AI technologies
- Questions raised about global impact of AI and hype from non-Western sources

**Other Critiques:**
- Some argue the book "largely reiterates the same critiques found in other AI cris de coeur"
- Doesn't break entirely new ground, though it synthesizes existing criticism effectively

---

## 7. Author Backgrounds

### Arvind Narayanan
- **Position:** Professor of Computer Science, Princeton University; Director, Center for Information Technology Policy
- **Education:** IIT Madras (2004), PhD University of Texas at Austin (2009) under Vitaly Shmatikov
- **Post-doc:** Stanford University (with Dan Boneh)
- **Major Contributions:**
  - Pioneering research in **de-anonymization** (showed Netflix "anonymous" data could be re-identified)
  - Co-authored influential cryptocurrency textbook
  - Developed prototypes for **Do Not Track** with Mozilla
  - Research on **dark patterns** in web design
  - Co-authored textbook *Fairness and Machine Learning*
- **Awards:** Presidential Early Career Award for Scientists and Engineers; Privacy Enhancing Technology Award (2008)
- **Known For:** 2019 viral talk "How to Recognize AI Snake Oil" (slides downloaded tens of thousands of times, tweets viewed 2+ million times)

### Sayash Kapoor
- **Position:** PhD candidate, Computer Science, Princeton University
- **Prior Experience:** Software engineer at Facebook, where he helped create AI for content moderation
- **Research Focus:** Reproducibility in AI research, limits of prediction
- **Key Contribution:** Led work exposing errors in peer-reviewed papers claiming AI superiority in predicting civil wars
- **Collaboration:** Co-writes "AI as Normal Technology" newsletter (formerly "AI Snake Oil"), read by 60,000+ researchers, policymakers, and journalists

### How They Came Together:
Sayash took Narayanan's course "Limits to Prediction" (co-taught with sociologist Matt Salganik) in Fall 2020. The course asked: "Given enough data, is everything predictable?" Their research collaboration grew from there, with Kapoor's industry experience at Facebook complementing Narayanan's academic perspective.

---

## 8. Quotable Insights and Frameworks

### On the Nature of AI Snake Oil:
> "Much of what's being sold as 'AI' today is snake oil. It does not and cannot work."

> "The goal of this book is to identify AI snake oil—and to distinguish it from AI that can work well if used in the right ways."

### On Why Snake Oil Persists:
> "Rather than looking at the supply of bullshit, look at the demand for bullshit. If the demand exists, the supply will automatically materialize."

> "Broken AI is very appealing to broken institutions."

### On Existential Risk:
> "We should be far more concerned about what people will do with AI than with what AI will do on its own."

> "When I look at the methods behind these probability estimates [for existential risk], they're all complete bunk."

### On Benchmarks vs. Reality:
> "The easier a task is to measure via benchmarks, the less likely it is to represent the kind of complex, contextual work that defines professional practice."

### On AI Progress:
> "In this broad set of domains [predictive optimization], AI diffusion lags decades behind innovation."

### On the Real Danger:
> "AI Snake Oil warns of the dangers of a world where AI continues to be controlled by largely unaccountable big tech companies."

### The Ladder of Generality Framework:
A visual tool where "each rung represents a way of computing that is more flexible, and more general, than the previous one." The authors argue we can't see the next rungs—or whether the ladder has a ceiling.

### Call to Action:
> "And finally, a plea to our fellow techies and engineers: refuse to build AI snake oil."

---

## Quick Reference Card

**For Conversation:**

If someone asks what the book is about:
> "It's a Princeton computer scientists' systematic examination of which AI actually works vs. which is pure hype. Their core insight is that broken AI appeals to broken institutions—companies buy AI snake oil because they *want* to believe in technological fixes for systemic problems."

If someone brings up AI existential risk:
> "The AI Snake Oil authors are skeptical—they point out the probability estimates are methodologically weak, and argue we should focus on what *people* will do with AI rather than what AI will do autonomously."

If someone asks about predictive AI:
> "One of their key findings: most deployed 'AI' in high-stakes domains like criminal justice and hiring is actually decades-old regression models dressed up as AI. The cutting-edge stuff doesn't work reliably enough for real-world deployment."

---

*Compiled from Princeton University Press, Wikipedia, Knight First Amendment Institute, TIME, Publishers Weekly, and the authors' Substack newsletter.*
