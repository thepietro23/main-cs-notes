---
title: "Module 23 — Competitive Exams Mapping (GATE / SEBI / RBI / ISRO / C-DAC)"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 23 — Competitive Exams Mapping

> **Why this module.**
> The same DSA content is tested very differently across exams. This module maps
> **every topic to every exam** and tells you what to **prioritise**, so you don't
> waste time studying ICPC-only topics for SEBI, or skipping P/NP for GATE.

This module is **P0 for exam-takers** (you're targeting SEBI/RBI IT + GATE).

> **How to read.** The weightage table, then per-exam strategy.

---

## 23.1 Topic × Exam Relevance

![Topic × exam heatmap: GATE/ISRO/C-DAC are algorithm-heavy (mostly High); SEBI/RBI lean conceptual + DBMS/OS overlap.](images/141_exam_weightage.png)

| Topic | GATE | SEBI/RBI IT | ISRO | C-DAC |
|---|---|---|---|---|
| Asymptotics / recurrences / Master thm | **High** | Medium | High | High |
| Arrays / sorting / searching | **High** | High | High | High |
| Linked list / stack / queue | **High** | High | High | High |
| Trees (BST/AVL/B/B+) | **High** | Medium | High | High |
| Hashing (collisions, probing) | **High** | Medium | High | High |
| Graphs (BFS/DFS/MST/shortest path) | **Very High** | Medium | High | High |
| Greedy / Divide & Conquer / DP | **High** | Medium | High | High |
| Heaps / priority queue | Medium | Low | Medium | Medium |
| Complexity classes (P/NP) | **High** | Low | Medium | Medium |
| Bit manipulation / number theory | Medium | Medium | Medium | High |
| B/B+ tree & hashing (DBMS overlap) | **High** | **High** | High | High |
| Recursion / backtracking | High | Medium | High | High |
| Strings (pattern matching, tries) | Medium | Medium | Medium | High |
| Amortised analysis (dyn. array, DSU) | **High** | Low | Medium | Medium |
| Disjoint-set / union-find | Medium | Low | Medium | Medium |
| OOP concepts (SEBI IT Paper-2) | Low | **High** | Medium | High |
| DBMS: normalisation / transactions / SQL | Medium | **High** | High | High |
| OS: scheduling / paging / concurrency | Medium | **High** | High | High |

> **Memory hook:** *GATE/ISRO/C-DAC = "compute it"; SEBI/RBI = "know it".* Same
> topics, different question style.

---

## 23.2 Per-Exam Strategy

### GATE CS (algorithm-heavy, numerical)

- **Format:** MCQ + NAT (numerical answer). Algorithms + Programming & DS are a
  **major chunk** (~13–15 marks combined with related areas).
- **Highest-yield:** recurrences & **Master Theorem**, **graph algorithms**
  (BFS/DFS/MST/Dijkstra/Bellman-Ford traversal & complexity), **DP** (table-fill:
  LCS, matrix chain, knapsack), **greedy** (Huffman numericals), **hashing**
  (probing sequences), **B/B+ trees** (order, splits), **P/NP** definitions &
  reductions, **quicksort/mergesort** comparison counts, heap (build O(n)).
- **Style:** they give you a concrete instance and ask you to **trace/compute**
  (table values, #comparisons, #nodes). Practice *doing*, not just reading.

### SEBI Grade A / RBI Grade B (IT stream) — *your target*

- **Format:** objective MCQs across IT (DSA + DBMS + OS + Networks + Cyber +
  emerging tech). DSA is **conceptual**, not heavy table-filling.
- **Highest-yield DSA:** complexity (Big-O of common algorithms), stack/queue/LL,
  tree traversals & BST, **hashing**, sorting basics, **B/B+ trees** (big DBMS
  overlap), graph basics. Plus **DBMS indexing** (ties to Module 8b / the DBMS
  notes).
- **Strategy:** breadth + accuracy on definitions and complexities; don't over-
  invest in ICPC-only topics (suffix automaton, HLD, flows).

#### SEBI IT Phase-2 (Paper 2) — programming weightage

For the **IT stream Phase-2 technical paper**, the CS-fundamentals portion is
widely reported (coaching syllabus breakdowns) to weight the four programming
areas roughly like this:

| Area | Approx. weightage |
|---|---|
| **Data Structures** (incl. JSON handling) | **~40%** |
| **Algorithms** | **~30%** |
| **Object-Oriented Programming (OOP)** | **~20%** |
| **String manipulation** | **~10%** |

- **Takeaway:** **Data Structures + Algorithms ≈ 70%** — they decide selection.
  OOP (~20%) and String handling (~10%) still matter but are secondary.
- **Note:** these are **relative weightages** from prep material, not per-topic
  official marks; the SEBI notification states subjects, not a public number
  split. Treat the split as a **study-priority guide**, not a guarantee.
- **JSON** shows up under Data Structures because IT roles handle config/API data;
  be comfortable parsing/serialising nested JSON (objects = maps, arrays = lists).

### ISRO / DRDO / C-DAC

- **ISRO CS:** GATE-like, slightly more direct; same DSA core + OS/DBMS/networks.
- **C-DAC (CCAT):** aptitude + CS fundamentals; **C programming + DSA + number
  theory/bit** matter.

### MCQs

1. Highest-yield GATE algorithm area? → **graph algorithms** (+ DP, recurrences).
2. SEBI/RBI DSA style? → **conceptual MCQ** (+ DBMS indexing overlap).
3. Which DSA topic spans *all* exams strongly? → **trees + hashing (esp. B/B+
   trees)**.

---

## 23.3 Frequently-Asked Concepts (memorise cold)

- Time complexities of **all** sorts (bubble/insertion/selection/merge/quick/heap/
  counting) — best/avg/worst + stable?
- **Master Theorem** application; recurrence → Θ.
- BST/AVL/**B/B+ tree** operations & heights; **number of nodes/keys**.
- **Hashing:** load factor, linear/quadratic/double probing, chaining.
- **Graph:** BFS/DFS order, MST (Kruskal/Prim), Dijkstra/Bellman-Ford/Floyd
  complexity & applicability (negative edges!).
- **DP:** LCS, matrix chain, 0/1 knapsack table-fill; greedy **Huffman** total
  bits.
- **Heap:** build-heap **O(n)**, heapsort O(n log n), array indices.
- **P/NP/NP-complete/NP-hard** definitions; SAT; reductions; undecidability.

### MCQs

1. Build-heap complexity (favourite trap)? → **O(n)**, not O(n log n).
2. Dijkstra with negative edges? → **fails** (use Bellman-Ford).
3. Which sorts are stable? → merge, insertion, counting (not quick/heap/selection).

---

## 23.4 Most-Repeated MCQ Facts (per exam)

These are the facts that show up **again and again**. Memorise them cold.

### GATE — the classic traps

- **Master Theorem:** `T(n)=aT(n/b)+f(n)`; compare `f(n)` with `n^(log_b a)`.
- **Build-heap = O(n)**; heapsort = **O(n log n)**; heapsort is **not stable**.
- **Quicksort worst case = O(n²)** (already-sorted with bad pivot); avg **O(n log n)**.
- **Dijkstra fails on negative edges** → Bellman-Ford (**O(VE)**); all-pairs =
  Floyd-Warshall (**O(V³)**).
- **DFS/BFS = O(V+E)**; BFS gives shortest path in **unweighted** graphs.
- **MST:** Kruskal (sort edges + union-find), Prim (**O(E log V)** with heap).
- **Hashing:** load factor α = n/m; linear probing suffers **clustering**.
- **B-tree of order m:** each node has **⌈m/2⌉ to m** children; height **O(log n)**.
- **P/NP:** NP-complete = in NP **and** NP-hard; SAT was the **first** (Cook-Levin).
- **A complete binary tree** of n nodes has height **⌊log₂ n⌋**.

### SEBI / RBI IT — conceptual one-liners

- **Big-O of common ops:** array access **O(1)**, search **O(n)**; BST search
  **O(log n)** avg / **O(n)** worst (skewed).
- **Stack = LIFO**, **Queue = FIFO**; stack does DFS, queue does BFS.
- **B/B+ tree indexes** power RDBMS; **B+ tree leaves are linked** for range scans.
- **Hash index** = O(1) equality, **no range queries**.
- **Normalisation:** 1NF (atomic) → 2NF (no partial dep) → 3NF (no transitive dep)
  → BCNF.
- **ACID** = Atomicity, Consistency, Isolation, Durability.
- **OOP four pillars:** encapsulation, abstraction, inheritance, polymorphism.
- **Overloading = compile-time**, **overriding = run-time** polymorphism.
- **Deadlock 4 conditions:** mutual exclusion, hold-and-wait, no preemption,
  circular wait.

### ISRO / C-DAC — direct fundamentals

- **Array indices in a heap:** children of `i` are `2i+1`, `2i+2` (0-based).
- **Postfix / prefix evaluation** uses a **stack**.
- **Number of nodes** at level `L` of a binary tree ≤ **2^L**.
- **Infix → postfix** conversion (Shunting-yard) uses a stack + precedence.
- **Circular queue** avoids the "false full" problem of a linear array queue.
- **Recursion uses the call stack**; tail recursion can be loop-optimised.
- **Two's complement:** negate = invert bits + 1; range `-2^(n-1)..2^(n-1)-1`.

---

## Module 23 — Concept Review (one page)

- **GATE/ISRO/C-DAC** = algorithm-heavy, **trace/compute** style → master
  recurrences, graphs, DP table-fill, hashing, B/B+ trees, P/NP, sort
  comparisons, build-heap O(n).
- **SEBI/RBI IT** (your target) = conceptual MCQ across IT; DSA complexities +
  trees + hashing + **DBMS indexing** overlap; breadth + accuracy.
- Use the **Excel "Exam Mapping"** tab to track exam-specific focus.

## Module 23 — Flash Cards

- Q: GATE highest-yield? **A: graphs, DP, recurrences, hashing, B+ trees, P/NP.**
- Q: SEBI/RBI DSA style? **A: conceptual MCQ + DBMS indexing.**
- Q: build-heap? **A: O(n).**
- Q: Dijkstra + negative edges? **A: fails → Bellman-Ford.**
- Q: stable sorts? **A: merge, insertion, counting.**
- Q: SEBI IT Paper-2 weightage? **A: DS ~40, Algo ~30, OOP ~20, String ~10 (%).**
- Q: B-tree order m children range? **A: ⌈m/2⌉ to m.**
- Q: Overloading vs overriding? **A: compile-time vs run-time.**
- Q: First NP-complete problem? **A: SAT (Cook-Levin).**
- Q: Normalisation order? **A: 1NF → 2NF → 3NF → BCNF.**

## Module 23 — Pattern Recognition (exam triage)

- "Trace this algorithm / fill this table" → GATE/ISRO numerical.
- "Which is true about X complexity" → SEBI/RBI conceptual MCQ.
- "B/B+ tree order / splits / index" → all exams + DBMS.
- "OOP pillars / overloading vs overriding" → SEBI IT Paper-2 (OOP ~20%).
- "Normalisation / ACID / SQL" → SEBI/RBI + all exams' DBMS section.
- "Evaluate postfix / infix→postfix" → ISRO/C-DAC stack question.

## Module 23 — GATE / SEBI / RBI / ISRO Perspective

This module *is* the exam perspective. Pair it with the per-module "GATE/SEBI…"
sections throughout M1–M18, and the **Excel Exam-Mapping + 6-Month Roadmap** tabs.

---

*End of Module 23. Next: Module 24 — Interview Question Bank (1000+ questions by
topic, follow-ups, debugging) — with visuals.*
