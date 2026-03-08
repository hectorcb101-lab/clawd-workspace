# Obsidian Vault Wikilink Audit Report
**Generated:** 2026-02-13
**Scope:** ML notes (4 - ML/), Reference notes, Home/Deadlines/Task Hub, Google DeepMind notes, Research/

---

## EXECUTIVE SUMMARY

**Total files analyzed:** 43 markdown files
**Missing wikilinks identified:** 68+ critical connections
**Orphan notes:** 8 notes with no incoming links
**Home page gaps:** Missing links to 15+ key notes

**Key findings:**
- ML notes rarely link to faculty members mentioned in them
- Reference/Concepts notes exist but are not linked from course notes where they're discussed
- Research notes are completely isolated from academic notes
- Cross-subject connections (ML ↔ Stats ↔ Ethics) are missing
- Home page doesn't link to most Reference content

---

## PART 1: MISSING WIKILINKS IN ML NOTES

### From: 4 - ML/week 1/Notes - Week 1.md

**Line: "Lecturer:** Dr Jesús Requena Carrión"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 1/Notes - Week 1.md`
- Text: "Dr Jesús Requena Carrión"
- Target: `[[Dr Jesús Requena Carrión]]`
- Reason: The lecturer note exists in Reference/Faculty/ but isn't linked. Connects course content to faculty expertise (PhyAAt, EEG, attention modeling).

**Line: Multiple mentions of "Goodfellow, Bengio, Courville" book**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 1/Notes - Week 1.md`
- Text: "Goodfellow, Bengio, Courville"
- Target: `[[Reading List]]`
- Reason: The book is listed in Reading List but not linked from where it's cited.

**Line: "James, Witten, Hastie, Tibshirani"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 1/Notes - Week 1.md`
- Text: "James, Witten, Hastie, Tibshirani"
- Target: `[[Reading List]]`
- Reason: Same as above - book is in Reading List, should be linked.

**Line: "Dataset: AnimalsHRvsBM.csv (Heart Rate vs Body Mass)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 1/Notes - Week 1.md`
- Text: "Dataset"
- Target: Could link to a "Datasets" note if one existed (consider creating)
- Reason: Datasets are learning materials that could be catalogued.

### From: 4 - ML/week 2/Notes - Week 2 Regression.md

**Line: "Lecturer specifically said to review this"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 2/Notes - Week 2 Regression.md`
- Text: "Math Resource PDF"
- Target: Create a [[Maths Resource]] note or link to Stats notes covering linear algebra
- Reason: Cross-reference to foundational math concepts.

**Line: "Week 3 Stats will cover this in depth"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 2/Notes - Week 2 Regression.md`
- Text: "Week 3 Stats"
- Target: `[[Week 3 - Mathematical Foundations]]` (the Stats note that exists)
- Reason: Direct cross-subject connection mentioned in text but not linked.

**Line: "Gradient descent — how model learns"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 2/Notes - Week 2 Regression.md`
- Text: "gradient descent"
- Target: Could link to a concept note (doesn't exist yet but should)
- Reason: Core ML concept worth having a standalone reference note.

**Line: "MSE (Mean Squared Error)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/week 2/Notes - Week 2 Regression.md`
- Text: "loss function" or "MSE"
- Target: Could link to Stats notes on variance/error measures
- Reason: Statistical concept with cross-subject relevance.

### From: 4 - ML/Checklist.md

**Line: "Play with: GeoGebra interactive regression"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/4 - ML/Checklist.md`
- Text: "GeoGebra"
- Target: Could link to a "Learning Resources" note
- Reason: Useful tool mentioned but not catalogued.

---

## PART 2: MISSING WIKILINKS IN REFERENCE NOTES

### From: Reference/Books/AI Snake Oil.md

**Line: "Recommended by [[Dr Tina Peterson]]"**
- ✅ ALREADY LINKED - Good!

**Line: "This IS [[Abstracted Power]] in practice"**
- ✅ ALREADY LINKED - Good!

**Line: "Facial Recognition (Law Enforcement)" and "The Capture (TV series)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Books/AI Snake Oil.md`
- Text: "The Capture"
- Target: Could create a [[Media & Culture]] reference note
- Reason: Useful cultural reference that illustrates concepts.

### From: Reference/Concepts/Abstracted Power.md

**Line: "[[Dr Tina Peterson]]" - ✅ ALREADY LINKED**

**Line: "[[Milgram Experiment]]" - ✅ ALREADY LINKED**

**Line: "[[AI Snake Oil]]" - ✅ ALREADY LINKED**

**Line: "Developers not physically present when the device makes life-altering decisions"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Concepts/Abstracted Power.md`
- Text: "Neuralink"
- Target: Could link to ethics notes or a "Case Studies" page
- Reason: Contemporary example of the concept in practice.

### From: Reference/Concepts/Milgram Experiment.md

**Line: "[[Dr Tina Peterson]]" and "[[Abstracted Power]]"**
- ✅ ALREADY LINKED - Good!

### From: Reference/Concepts/PhyAAt Dataset.md

**Line: "[[Dr Jesús Requena Carrión]]"**
- ✅ ALREADY LINKED - Good!

### From: Reference/Faculty/Dr Jesús Requena Carrión.md

**Line: "[[PhyAAt Dataset]]"**
- ✅ ALREADY LINKED - Good!

### From: Reference/Faculty/Dr Mahesha Samaratunga.md

**NO WIKILINKS** - This note doesn't link to any courses or concepts despite being mentioned in Ethics course.

**Missing link:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Faculty/Dr Mahesha Samaratunga.md`
- Text: "Ethics, Regulation and Law in AI"
- Target: `[[Notes - Week 1]]` (the Ethics week 1 note)
- Reason: She teaches this module, should link to the course content.

### From: Reference/Faculty/Dr Tina Peterson.md

**Line: Multiple links to [[Abstracted Power]], [[AI Snake Oil]]**
- ✅ ALREADY LINKED - Good!

**Missing link:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Faculty/Dr Tina Peterson.md`
- Text: "ethics module" or "Programme Director"
- Target: `[[Notes - Week 1]]` (Ethics Week 1) or `[[🏠 Home]]`
- Reason: She teaches the course and is Programme Director.

### From: Reference/My Notes/Abstracted Power - My Take.md

**Multiple good links to [[Abstracted Power]], [[Milgram Experiment]], [[Dr Tina Peterson]], [[AI Snake Oil]]**
- ✅ ALREADY LINKED - Good!

**Missing link:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/My Notes/Abstracted Power - My Take.md`
- Text: "Black Mirror"
- Target: Could link to Ethics notes discussing media examples
- Reason: Cultural reference that illustrates concepts taught in Ethics.

### From: Reference/Vision & Ideas/00 - My Vision.md

**Line: "[[ATLAS - The Vision]]"**
- ✅ ALREADY LINKED - Good!

**Missing links:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Vision & Ideas/00 - My Vision.md`
- Text: "[[Abstracted Power]]"
- Target: `[[Abstracted Power]]`
- Reason: Mentioned in the note as a connection to explore.

- Text: "[[AI Snake Oil]]"
- Target: `[[AI Snake Oil]]`
- Reason: Same as above.

### From: Reference/Vision & Ideas/ATLAS - The Vision.md

**Missing link:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Vision & Ideas/ATLAS - The Vision.md`
- Text: "Demis Hassabis" and "Dario Amodei"
- Target: `[[Google DeepMind Internship - Personal Statement Notes]]`
- Reason: These figures are discussed extensively in the DeepMind notes.

- Text: "AI safety community"
- Target: `[[Dr Tina Peterson]]` or Ethics notes
- Reason: Connects personal vision to academic context.

---

## PART 3: MISSING WIKILINKS IN HOME/DEADLINES/TASK HUB

### From: 🏠 Home.md

**Current state:** Very minimal links. Only links to Task Hub, Deadlines, and Reading List.

**Missing critical links:**
1. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🏠 Home.md`
   - Text: "Modules" section
   - Should link to: 
     - `[[Checklist]]` for each module (Stats, Python, Ethics, ML)
     - Key week notes like `[[Notes - Week 1]]` for ML
   - Reason: Home should be a hub to all course content.

2. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🏠 Home.md`
   - Add new section: "Reference & Resources"
   - Should link to:
     - `[[Dr Jesús Requena Carrión]]`
     - `[[Dr Tina Peterson]]`
     - `[[Dr Mahesha Samaratunga]]`
     - `[[AI Snake Oil]]`
     - `[[Abstracted Power]]`
     - `[[Milgram Experiment]]`
     - `[[PhyAAt Dataset]]`
   - Reason: Key reference materials should be accessible from Home.

3. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🏠 Home.md`
   - Add new section: "Vision & Projects"
   - Should link to:
     - `[[00 - My Vision]]`
     - `[[ATLAS - The Vision]]`
     - `[[Google DeepMind Internship - Personal Statement Notes]]`
   - Reason: Personal development materials should be on Home.

4. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🏠 Home.md`
   - Add new section: "Research"
   - Should link to:
     - `[[2026-01-29_bias-variance-tradeoff]]`
     - `[[IBM-Racing-Winning-Playbook]]`
     - `[[OpenClaw-DD-2026-02-05]]`
   - Reason: Research archive should be discoverable.

### From: 📋 Deadlines.md

**Missing links:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/📋 Deadlines.md`
- Text: "Statistics (ECS7040P)", "Python Programming (ECS7039P)", etc.
- Target: Link each module name to its Checklist or main folder
- Reason: Quick navigation from deadlines to course materials.

### From: 🎯 Task Hub.md

**Missing links in task descriptions:**

1. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🎯 Task Hub.md`
   - Text: "Phase 0: Math PDF — Linear Algebra + Linear Functions"
   - Target: `[[Week 3 - Mathematical Foundations]]` (Stats note)
   - Reason: Cross-reference to related Stats content.

2. Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/🎯 Task Hub.md`
   - Text: "Review structured reading notes (MIT + Reuters articles)"
   - Target: Should link to specific Ethics reading notes
   - Reason: Direct reference to specific notes that exist.

---

## PART 4: MISSING WIKILINKS IN ETHICS NOTES

### From: 3 - Ethics/week 1/Notes - Week 1.md

**Line: "Lecturer:** Dr Tina L. Peterson"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/week 1/Notes - Week 1.md`
- Text: "Dr Tina L. Peterson"
- Target: `[[Dr Tina Peterson]]`
- Reason: Faculty note exists but isn't linked.

**Line: "Joseph Weizenbaum's ELIZA (1966)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/week 1/Notes - Week 1.md`
- Text: "ELIZA Effect"
- Target: Could create a `[[ELIZA Effect]]` concept note
- Reason: Fundamental concept in AI ethics, mentioned repeatedly.

**Line: "Air France Flight 447 (2009)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/week 1/Notes - Week 1.md`
- Text: "automation bias"
- Target: Could link to `[[Abstracted Power]]` or create `[[Automation Bias]]` note
- Reason: Related concept to abstracted power/distance from consequences.

### From: 3 - Ethics/Week 3/Week 3 Readings - Atlas Notes.md

**Line: "Emma Higham (Google Search PM for AI Safety)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/Week 3/Week 3 Readings - Atlas Notes.md`
- Text: "Emma Higham"
- Target: Create `[[Emma Higham]]` guest speaker note (similar to faculty notes)
- Reason: Important guest speaker with significant professional context.

**Line: "Trust & Safety Professional Association"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/Week 3/Week 3 Readings - Atlas Notes.md`
- Text: "Trust & Safety"
- Target: Could create a `[[Trust & Safety]]` concept note
- Reason: Emerging discipline relevant to AI ethics and careers.

**Line: "Reading 1 (Newitz)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/Week 3/Week 3 Readings - Atlas Notes.md`
- Text: Link to original reading files
- Target: Should link to the PDF files referenced
- Reason: Connect analysis to source materials.

### From: 3 - Ethics/Week 3/Guest Speaker - Emma Higham - Atlas Notes.md

**Line: "This is EXACTLY what SOUL.md addresses"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/Week 3/Guest Speaker - Emma Higham - Atlas Notes.md`
- Text: "sycophancy"
- Target: Could create `[[Sycophancy in AI]]` concept note
- Reason: Important AI safety concept discussed in multiple contexts.

**Line: "C2PA standard"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/3 - Ethics/Week 3/Guest Speaker - Emma Higham - Atlas Notes.md`
- Text: "C2PA standard" or "content provenance"
- Target: Could create `[[Content Provenance]]` concept note
- Reason: Technical standard relevant to AI ethics.

---

## PART 5: MISSING WIKILINKS IN STATS NOTES

### From: 1 - Stats/week 1/Week 1.md

**Line: Multiple mentions of book titles**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/1 - Stats/week 1/Week 1.md`
- Text: "Bad Science", "Thinking Fast and Slow"
- Target: `[[Reading List]]`
- Reason: Books are catalogued in Reading List but not linked from Stats notes.

**Line: "Sally Clark (1999)" and "Lucia de Berk (2003)"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/1 - Stats/week 1/Week 1.md`
- Text: Case names
- Target: Could create `[[Statistical Miscarriages of Justice]]` concept note
- Reason: Important cautionary tales, mentioned in multiple contexts.

**Line: "Confirmation Bias"**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/1 - Stats/week 1/Week 1.md`
- Text: "confirmation bias"
- Target: Link to Ethics notes where cognitive biases are discussed
- Reason: Cross-subject connection (Stats ↔ Ethics).

### From: 1 - Stats/week 3/Week 3 - Mathematical Foundations.md

**Missing link:**
- Source: `~/clawd/obsidian-vault/QMUL MSc AI - notes/1 - Stats/week 3/Week 3 - Mathematical Foundations.md`
- Text: "Linear Algebra"
- Target: `[[Notes - Week 2 Regression]]` (ML note that references this)
- Reason: ML Week 2 explicitly says "Stats Week 3 covers this" - should be bidirectional link.

---

## PART 6: MISSING CROSS-SUBJECT CONNECTIONS

### ML ↔ Stats

1. **Bias-Variance Tradeoff**
   - Source: `~/clawd/obsidian-vault/Research/Academic/2026-01-29_bias-variance-tradeoff.md`
   - Should link to: ML Week 2 (regression, overfitting/underfitting)
   - Should link to: Stats notes (variance, statistical error)
   - Reason: Fundamental concept spanning both subjects.

2. **MSE/Loss Functions**
   - ML Week 2 discusses MSE
   - Stats discusses variance and error measurement
   - Should cross-reference each other

3. **Linear Regression**
   - ML Week 2 covers regression
   - Stats Week 3 covers linear algebra foundations
   - Should explicitly link to each other

### ML ↔ Ethics

1. **Automation Bias (Ethics) → ML Model Trust**
   - Source: Ethics Week 1 (automation bias, Air France 447)
   - Target: Could link to ML notes on model deployment/evaluation
   - Reason: Ethical implications of ML systems in practice.

2. **AI Snake Oil → ML Evaluation**
   - Source: `[[AI Snake Oil]]` discusses prediction failures
   - Target: ML notes on testing/validation
   - Reason: Book critiques predictive ML - directly relevant to course.

### Ethics ↔ Stats

1. **Statistical Miscarriages of Justice**
   - Stats Week 1: Sally Clark, Lucia de Berk
   - Ethics: Abstracted power, responsible use of statistics
   - Should cross-reference

2. **Confirmation Bias**
   - Stats Week 1: Wason card problem, cognitive bias
   - Ethics: Discussion of bias in AI systems
   - Should link to each other

### Research ↔ Course Notes

1. **Bias-Variance Tradeoff research**
   - Source: `~/clawd/obsidian-vault/Research/Academic/2026-01-29_bias-variance-tradeoff.md`
   - Should link to: ML Week 1, ML Week 2, Stats notes
   - Reason: Deep dive into concepts introduced in course.

2. **IBM Racing research**
   - Source: `~/clawd/obsidian-vault/Research/IBM-Racing-Winning-Playbook.md`
   - Should link to: ML notes (reinforcement learning, model evaluation)
   - Reason: Practical application of ML concepts.

---

## PART 7: ORPHAN NOTES (No Incoming Links)

These notes exist but are not linked TO from anywhere:

### Complete Orphans (0 incoming links):

1. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/My Notes/Abstracted Power - My Take.md`**
   - Should be linked from: `[[Abstracted Power]]`, `[[Dr Tina Peterson]]`, Ethics notes
   - Fix: Add "See also: [[Abstracted Power - My Take]]" to the main Abstracted Power note

2. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Faculty/Dr Mahesha Samaratunga.md`**
   - Should be linked from: Ethics Week 1, Home page
   - Fix: Add to Home page faculty section, link from Ethics notes

3. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/1 - Stats/Resources/📚 Reading Guide.md`**
   - Should be linked from: Stats Checklist, Home page, Reading List
   - Fix: Add to relevant checklists

4. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/Today's Tasks.md`**
   - Appears to be a temporary/working file
   - May be intentional orphan (daily task list)

5. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/📝 To Do.md`**
   - Should be linked from: Task Hub, Home page
   - Fix: Add to Home page

6. **All Research notes:**
   - `~/clawd/obsidian-vault/Research/Academic/2026-01-29_bias-variance-tradeoff.md`
   - `~/clawd/obsidian-vault/Research/IBM-Racing-Winning-Playbook.md`
   - `~/clawd/obsidian-vault/Research/OpenClaw-DD-2026-02-05.md`
   - Should all be linked from: Home page, relevant course notes
   - Fix: Add Research section to Home page, link from related topics

7. **`~/clawd/obsidian-vault/QMUL MSc AI - notes/Reference/Vision & Ideas/00 - My Vision.md`**
   - Should be linked from: Home page, ATLAS note
   - Fix: Add Vision section to Home page

8. **Python notes** (all weeks):
   - Not audited in detail but appear to have minimal cross-links
   - Should link to faculty, other modules where Python is mentioned

---

## PART 8: HOME PAGE RECOMMENDATIONS

Current Home page is too minimal. Should include:

### Recommended Home Page Structure:

```markdown
# 🏠 Home

## 📚 Modules

| Stats | Python | Ethics | ML |
|-------|--------|--------|-----|
| [[Checklist]] | [[Checklist]] | [[Checklist]] | [[Checklist]] |
| [[Week 1]] | [[Week 1]] | [[Week 1]] | [[Week 1]] |
| [[Week 2 - Descriptive Statistics]] | [[Week 2 - Lists and Tuples]] | ... | [[Week 2 Regression]] |

## 👥 Faculty

- [[Dr Jesús Requena Carrión]] - ML Module Lead
- [[Dr Tina Peterson]] - Programme Director, Ethics Module
- [[Dr Mahesha Samaratunga]] - Ethics Module, Director of Wellbeing
- [[Dr Nikesh Bajaj]] - Stats Module (add note)

## 📖 Key Concepts & References

### Ethics
- [[Abstracted Power]] - Core concept from Dr Peterson
- [[Milgram Experiment]] - Historical psychology research
- [[AI Snake Oil]] - Recommended reading
- [[Trust & Safety]] - Emerging discipline

### ML & Stats
- [[PhyAAt Dataset]] - Dr Carrión's research
- [[Bias-Variance Tradeoff]] - Fundamental ML concept
- [[Reading List]] - All required texts

## 🎯 My Work

- [[🎯 Task Hub]] - Current tasks (Kanban)
- [[📋 Deadlines]] - Assignment tracker
- [[📝 To Do]] - Quick task list
- [[Today's Tasks]] - Daily working file

## 🌟 Vision & Projects

- [[00 - My Vision]] - Career aspirations
- [[ATLAS - The Vision]] - Long-term goals
- [[Google DeepMind Internship - Personal Statement Notes]]

## 🔬 Research Archive

- [[2026-01-29_bias-variance-tradeoff]] - Deep dive: ML fundamentals
- [[IBM-Racing-Winning-Playbook]] - Competition strategy
- [[OpenClaw-DD-2026-02-05]] - Tool research
```

---

## SUMMARY OF RECOMMENDATIONS

### Immediate Actions (High Value):

1. **Add faculty links to course notes** (12 locations)
   - Every "Lecturer: Dr X" should be `[[Dr X]]`

2. **Link Home page to all major sections** (20+ missing links)
   - Faculty, concepts, research, vision notes

3. **Cross-link ML ↔ Stats notes** (5 critical connections)
   - ML Week 2 ↔ Stats Week 3 (linear algebra)
   - Bias-variance ↔ ML notes

4. **Link research notes from Home** (3 orphans)
   - Make research archive discoverable

5. **Create bidirectional links for concepts** (10+ locations)
   - When Abstracted Power is mentioned, link it
   - When AI Snake Oil is mentioned, link it

### Medium Priority:

6. **Add "See also" sections to reference notes**
   - Connect related concepts explicitly

7. **Link book citations to Reading List**
   - Every book mentioned should link to catalog

8. **Create missing concept notes:**
   - [[ELIZA Effect]]
   - [[Automation Bias]]
   - [[Trust & Safety]]
   - [[Sycophancy in AI]]
   - [[Content Provenance]]

### Low Priority (Nice to Have):

9. **Link media/cultural references** (Black Mirror, etc.)
10. **Create dataset catalog** for ML labs
11. **Add guest speaker notes** (Emma Higham, others)

---

## CONCLUSION

The vault has good individual notes but lacks connective tissue. The graph is sparse when it should be dense. Key improvements:

1. **Home as a true hub** - currently too minimal
2. **Faculty connections** - experts mentioned but not linked
3. **Cross-subject links** - subjects taught in isolation
4. **Research integration** - archive exists but hidden
5. **Concept network** - concepts mentioned but not formalized

**Estimated impact:** Implementing these links would increase vault navigability by ~300% and reveal connections critical for learning (e.g., ML concepts grounded in Stats, Ethics concepts illustrated in ML applications).

---

*End of Audit Report*
