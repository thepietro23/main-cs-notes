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

## Module 23 — Pattern Recognition (exam triage)

- "Trace this algorithm / fill this table" → GATE/ISRO numerical.
- "Which is true about X complexity" → SEBI/RBI conceptual MCQ.
- "B/B+ tree order / splits / index" → all exams + DBMS.

## Module 23 — GATE / SEBI / RBI / ISRO Perspective

This module *is* the exam perspective. Pair it with the per-module "GATE/SEBI…"
sections throughout M1–M18, and the **Excel Exam-Mapping + 6-Month Roadmap** tabs.

---

*End of Module 23. Next: Module 24 — Interview Question Bank (1000+ questions by
topic, follow-ups, debugging) — with visuals.*
