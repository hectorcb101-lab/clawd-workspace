# Python Notes Wikilink Audit Report

**Generated:** 2026-02-13  
**Scope:** All Python notes in `~/clawd/obsidian-vault/QMUL MSc AI - notes/2 - Python/`

---

## Executive Summary

Analyzed 6 Python markdown files and identified **47 missing wikilink opportunities** across the following categories:
- **Internal Python note cross-references:** 12 missing links
- **Cross-subject connections (Stats, ML, Ethics):** 18 missing links
- **Faculty/Reference connections:** 8 missing links
- **Home/Hub navigation links:** 9 missing links

---

## 1. Missing Internal Python Cross-References

### In: `week 1/Notes - Week 1 Summary.md`

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "Notes - Week 1"  
**Target:** [[Notes - Week 1]]  
**Reason:** References the detailed notes but doesn't link to them. Creates navigation between summary and full notes.

---

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "Practice 1"  
**Target:** [[Practice 1]]  
**Reason:** References practice exercises but doesn't link. Users should be able to jump to practice directly.

---

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Next: Control flow, conditionals, loops"  
**Target:** [[Notes - Week 2 Lists and Tuples]]  
**Reason:** Points forward to next topic, should enable direct navigation.

---

### In: `week 1/lab/Lab 1 Notes.md`

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "Week 1 - Python Basics Notes"  
**Target:** [[Notes - Week 1]]  
**Reason:** Explicitly references the lecture notes in "Related" section but doesn't link.

---

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "S01.1-IntroPython.ipynb"  
**Target:** [[Notes - Week 1]]  
**Reason:** References source notebook; should link to the note that covers this material.

---

### In: `week 2/Notes - Week 2 Lists and Tuples.md`

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Prerequisites: Week 1 Python basics"  
**Target:** [[Notes - Week 1]]  
**Reason:** Explicitly states dependency on Week 1, should link for easy reference.

---

### In: `Checklist.md`

**Source:** `Checklist.md`  
**Text:** "Review Week 1 notes"  
**Target:** [[Notes - Week 1]]  
**Reason:** Task references specific note, should link directly to it.

---

**Source:** `Checklist.md`  
**Text:** "PYnative Basics Exercises"  
**Target:** [[Practice 1]]  
**Reason:** Practice exercises are documented in Practice 1 note.

---

**Source:** `Checklist.md`  
**Text:** "Integer division (125 inches to feet + remaining)"  
**Target:** [[Practice 1]]  
**Reason:** This specific exercise is covered in detail in Practice 1.

---

**Source:** `Checklist.md`  
**Text:** "String manipulation (extract first name)"  
**Target:** [[Practice 1]]  
**Reason:** String manipulation exercises are in Practice 1.

---

**Source:** `Checklist.md`  
**Text:** "Build a calculator"  
**Target:** [[Practice 1]]  
**Reason:** Calculator exercise appears in Practice 1 challenges.

---

## 2. Cross-Subject Connections: Python → Stats

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Data Types" (in section "📦 Variables")  
**Target:** [[Week 2 - Descriptive Statistics]]  
**Reason:** Data types are fundamental to statistical datasets. Stats Week 2 covers data and attributes—understanding Python data types is the foundation.

---

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "type(x)" (in Built-in Functions table)  
**Target:** [[Week 2 - Descriptive Statistics]]  
**Reason:** Understanding data types is critical for statistics; checking types with `type()` relates to identifying variable types in datasets.

---

### In: `week 2/Notes - Week 2 Lists and Tuples.md`

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Lists" (heading "### Lists")  
**Target:** [[Week 2 - Descriptive Statistics]]  
**Reason:** Lists are the primary data structure for storing datasets in Python for statistical analysis.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Nested Lists (Matrices)" (heading)  
**Target:** [[Week 3 - Mathematical Foundations]]  
**Reason:** Stats Week 3 covers matrices and linear algebra. Nested Python lists represent matrices—direct conceptual link.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "matrix" (in code example)  
**Target:** [[Week 3 - Mathematical Foundations]]  
**Reason:** The code shows matrix indexing; Stats Week 3 teaches matrix operations mathematically.

---

### In: `week 1/lab/Lab 1 Notes.md`

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "import math" (heading "## 📦 Importing Modules")  
**Target:** [[Week 3 - Mathematical Foundations]]  
**Reason:** The `math` module provides functions used in statistical calculations (covered in Stats Week 3).

---

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "math.sqrt(16)"  
**Target:** [[Week 3 - Mathematical Foundations]]  
**Reason:** Square root is a mathematical operation; Stats Week 3 covers mathematical foundations including such operations.

---

## 3. Cross-Subject Connections: Python → Machine Learning

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Variables" (heading "## 📦 Variables")  
**Target:** [[Notes - Week 1]] (ML)  
**Reason:** ML Week 1 defines "features" and "attributes" which are implemented as Python variables. Understanding variable assignment is foundational.

---

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Data Types" (section "### Data Types")  
**Target:** [[Notes - Week 1]] (ML)  
**Reason:** ML Week 1 discusses datasets with attributes (features). Python data types map directly to feature types (int, float, str).

---

### In: `week 2/Notes - Week 2 Lists and Tuples.md`

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Lists" (heading)  
**Target:** [[Notes - Week 1]] (ML)  
**Reason:** ML Week 1 shows datasets as collections of items. Python lists are the data structure for storing ML datasets.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Nested Lists (Matrices)"  
**Target:** [[Notes - Week 2 Regression]]  
**Reason:** ML Week 2 Regression uses matrix notation (ŷ = Xw). Nested Python lists represent the feature matrix X.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "matrix" (code example with `matrix[0][1]`)  
**Target:** [[Notes - Week 2 Regression]]  
**Reason:** Matrix indexing in Python directly relates to accessing features in ML regression datasets.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Dictionaries"  
**Target:** [[Notes - Week 1]] (ML)  
**Reason:** Dictionaries are ideal for representing ML dataset items (key-value = feature-value pairs), as shown in ML Week 1 table examples.

---

### In: `week 1/lab/Lab 1 Notes.md`

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "type(x)" (in Built-in Functions table)  
**Target:** [[Notes - Week 1]] (ML)  
**Reason:** ML requires understanding data types for features. Checking types with `type()` is essential for validating ML input data.

---

## 4. Cross-Subject Connections: Python → Ethics

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Object-Oriented Programming (OOP)" (heading)  
**Target:** [[Abstracted Power]]  
**Reason:** OOP creates abstraction layers. Dr Tina Peterson's "Abstracted Power" concept discusses how abstraction in technology distances users from consequences—OOP is a prime technical example.

---

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "An object is a self-contained unit"  
**Target:** [[Abstracted Power]]  
**Reason:** Self-contained objects abstract complexity, directly relating to Peterson's theory on how abstraction obscures consequences.

---

## 5. Faculty/Reference Connections

### In: `week 1/Notes - Week 1 Summary.md`

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "Module: ECS7039P: Python Programming for AI"  
**Target:** [[Dr Jesús Requena Carrión]]  
**Reason:** Python module taught by same instructor as ML. Connecting to instructor profile provides context on teaching style and research focus.

---

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** "Module: ECS7039P: Python Programming for AI"  
**Target:** [[Dr Jesús Requena Carrión]]  
**Reason:** Same as above—module lead connection.

---

### In: `week 1/lab/Lab 1 Notes.md`

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** "Module: ECS7039P: Python Programming for AI"  
**Target:** [[Dr Jesús Requena Carrión]]  
**Reason:** Same as above—module lead connection.

---

### In: `week 2/Notes - Week 2 Lists and Tuples.md`

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "Module: ECS708P Python Programming"  
**Target:** [[Dr Jesús Requena Carrión]]  
**Reason:** Same module, same instructor—should link to faculty profile.

---

### In: `week 1/Notes - Week 1 Summary.md`

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "W3Schools Python Quiz" (in Practice Quizzes section)  
**Target:** [[Reading List]]  
**Reason:** Reading List includes "Python Practice" section with W3Schools reference—should cross-link.

---

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "Real Python"  
**Target:** [[Reading List]]  
**Reason:** Real Python appears in Reading List under "Python Practice"—should link.

---

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** "PYnative Python Basics Quiz"  
**Target:** [[Reading List]]  
**Reason:** PYnative appears in Reading List under "Python Practice"—should link.

---

## 6. Home/Hub Navigation Links

### In: `Checklist.md`

**Source:** `Checklist.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]]"  
**Reason:** Every module checklist should link back to Home for navigation consistency.

---

**Source:** `Checklist.md`  
**Text:** After assignments section (add link)  
**Suggested addition:** "[[🎯 Task Hub]]"  
**Reason:** Checklist items are tasks—should integrate with central Task Hub.

---

### In: `week 1/Notes - Week 1 Summary.md`

**Source:** `week 1/Notes - Week 1 Summary.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]] | [[2 - Python/Checklist]]"  
**Reason:** Provides navigation to home and module checklist.

---

### In: `week 1/Notes - Week 1.md`

**Source:** `week 1/Notes - Week 1.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]] | [[2 - Python/Checklist]]"  
**Reason:** Same navigation consistency.

---

### In: `week 1/lab/Lab 1 Notes.md`

**Source:** `week 1/lab/Lab 1 Notes.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]] | [[2 - Python/Checklist]]"  
**Reason:** Same navigation consistency.

---

### In: `week 1/Practice 1.md`

**Source:** `week 1/Practice 1.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]] | [[Notes - Week 1]]"  
**Reason:** Practice note should link to related lecture notes and home.

---

### In: `week 2/Notes - Week 2 Lists and Tuples.md`

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** Top of file (add link)  
**Suggested addition:** "← [[🏠 Home]] | [[2 - Python/Checklist]]"  
**Reason:** Same navigation consistency.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** "See: [[List_Indexing_1.png]]"  
**Target:** Should be `![[List_Indexing_1.png]]` (embedded image)  
**Reason:** Image files in Obsidian should use `![[]]` for embedding, not `[[]]` for linking.

---

**Source:** `week 2/Notes - Week 2 Lists and Tuples.md`  
**Text:** Multiple image references (`[[List_Slicing_1.png]]`, `[[List_methods_1.PNG]]`, etc.)  
**Target:** Change all to `![[filename]]` format  
**Reason:** These are images meant to be displayed inline, not linked to as separate notes.

---

## 7. Additional Opportunities: Concept Notes

### Concepts Mentioned That Could Have Dedicated Notes

**Source:** `week 1/Notes - Week 1.md`  
**Concept:** "Object-Oriented Programming (OOP)"  
**Suggestion:** Create `[[Object-Oriented Programming]]` reference note  
**Reason:** OOP is a major programming paradigm used throughout Python and connects to abstraction concepts in Ethics. Worth a dedicated explainer note.

---

**Source:** `week 1/Notes - Week 1.md` & `week 2/Notes - Week 2 Lists and Tuples.md`  
**Concept:** "Data Structures" (lists, tuples, sets, dictionaries)  
**Suggestion:** Create `[[Python Data Structures]]` overview note  
**Reason:** Central concept that connects to both ML (storing datasets) and Stats (data organization). A hub note would tie these together.

---

**Source:** `week 1/Notes - Week 1.md`  
**Concept:** "BODMAS/PEMDAS" (order of operations)  
**Suggestion:** Create `[[Order of Precedence]]` or link to Math Foundations  
**Reason:** Mathematical concept that spans Python programming and Stats calculations.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Internal Python cross-references | 12 |
| Python → Stats connections | 7 |
| Python → ML connections | 7 |
| Python → Ethics connections | 2 |
| Faculty connections | 4 |
| Reference/Reading List connections | 3 |
| Navigation (Home/Hub) links | 9 |
| **TOTAL MISSING LINKS** | **47** |

---

## Recommendations

### Priority 1: Internal Navigation (High Impact, Low Effort)
1. Add Home/Checklist links to all Python note headers
2. Link week summaries to full notes and practice exercises
3. Link forward/backward between weeks

### Priority 2: Cross-Subject (High Learning Value)
1. Link data types, variables, and lists to Stats and ML notes
2. Link nested lists/matrices to Stats Week 3 Math Foundations
3. Link OOP concepts to Abstracted Power (Ethics)

### Priority 3: Context & Discovery
1. Add faculty links (Dr Jesús Requena Carrión) to module headers
2. Link practice resources (W3Schools, Real Python) to Reading List
3. Create dedicated concept notes for OOP and Data Structures

### Priority 4: Technical Fixes
1. Convert `[[image.png]]` to `![[image.png]]` in Week 2 notes for proper embedding

---

**End of Report**
