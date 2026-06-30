---
title: "Module 20 — Google / FAANG Interview Preparation"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 20 — Google / FAANG Interview Preparation

> **Why this module.**
> M1–M18 gave you the toolbox. This module is about **using it under interview
> conditions**: a repeatable problem-solving framework, instant pattern
> recognition, the curated problem sets that cover ~90% of questions (Blind 75 /
> Neetcode 150 / Grind 169), and what each company actually optimises for. The
> bar isn't "did you solve it" — it's "did you communicate, justify complexity,
> handle edge cases, and write clean code."

This module is **P0** for your stated goal (Google/Meta/Amazon/...).

> **How to read.** The framework, the pattern map, the curated lists, company
> specifics, and a study plan. (Track problems in the Excel **"Top 300"** tab.)

---

## 20.1 The Universal Interview Framework

![Interview framework: Clarify → Examples → Approach (brute force first) → Code → Test → Complexity.](images/134_interview_framework.png)

Follow this **every single time** (never jump straight to code):

1. **Clarify** — restate the problem; ask about input ranges, types, duplicates,
   empty/negative inputs, expected output. (Interviewers *plant* ambiguity.)
2. **Examples** — walk one small example by hand to confirm understanding.
3. **Approach** — state the **brute force** + its complexity first, *then*
   optimise. Think aloud; name the pattern.
4. **Code** — clean, readable, helper functions, good names. Keep narrating.
5. **Test** — dry-run your code; check edge cases (empty, size 1, overflow,
   duplicates, max bounds). Fix bugs calmly.
6. **Complexity** — state final **time and space**, and discuss trade-offs.

> **Scored signals** (what actually gets you hired): communication, brute-force-
> then-optimise, complexity analysis, edge-case discipline, clean code. A correct
> answer in silence often *fails*.

### MCQs

1. First step on any problem? → **clarify** (restate + ask constraints).
2. Before optimising, state? → the **brute force + its complexity**.
3. Biggest non-coding scored signal? → **communication / think-aloud**.

---

## 20.2 Pattern Recognition (classify in seconds)

![Pattern map: keyword in the problem → the technique and module (binary search, sliding window, heap, DP, graphs, hashmap, ...).](images/135_pattern_map.png)

| The problem says… | Reach for… |
|---|---|
| sorted array / "find target" / "min-max that works" | **Binary search** (M12) |
| contiguous subarray/substring + condition | **Sliding window / two pointers** (M2) |
| top-K / K-th largest / "closest K" | **Heap** (M6) |
| next greater/smaller, histogram, spans | **Monotonic stack** (M5) |
| all subsets / permutations / combinations | **Backtracking** (M13) |
| count ways / min cost / can-reach (overlapping) | **DP** (M14) |
| shortest path / connectivity / grid / islands | **BFS/DFS/Dijkstra/DSU** (M10) |
| "subarray sum = k" / pair / dedupe / frequency | **Hashmap** (M7) |
| intervals / meetings / merge / scheduling | **Sort + sweep / greedy** (M11) |
| prefix / range-sum queries | **Prefix sum / Fenwick** (M2 / M8b) |
| string matching / autocomplete | **KMP/Z / Trie** (M3) |

> **Drill this table** until classification is automatic — most interview problems
> are a known pattern in disguise.

### MCQs

1. "Longest substring with ≤ k distinct" → ? → **sliding window**.
2. "K-th largest in a stream" → ? → **heap**.
3. "Number of ways to make change" → ? → **DP**.

---

## 20.3 The Curated Problem Sets

Don't grind 2000 random problems — these cover the space:

- **Blind 75** — the classic minimum set, ~75 problems across all core patterns.
  *If you only do one list, do this.*
- **Neetcode 150** — Blind 75 + 75 more, grouped by pattern (arrays, two pointers,
  sliding window, stack, binary search, linked list, trees, tries, heap,
  backtracking, graphs, DP, greedy, intervals, math, bit). **Best structured
  path.**
- **Grind 75 / 169** — schedule-based (adjustable by hours/week).
- **LeetCode company tags** — once a company is targeted, do its tagged "last 6
  months" set.

> **Your Excel "Top 300 Problems" tab** seeds this pattern-wise; mark Solved /
> Revisit there. Aim for **breadth across patterns first**, then depth.

### Study sequence (recommended order)

Arrays & Hashing → Two Pointers → Sliding Window → Stack → Binary Search →
Linked List → Trees → Tries → Heap → Backtracking → Graphs → 1-D DP → 2-D DP →
Greedy → Intervals → Math & Bit. (Mirrors Neetcode's grouping and this course's
module order.)

### MCQs

1. The single best minimal list? → **Blind 75**.
2. Best *structured-by-pattern* path? → **Neetcode 150**.
3. Breadth or depth first? → **breadth across patterns**, then depth.

---

## 20.4 Company-Specific Focus

| Company | Coding focus | Other rounds / notes |
|---|---|---|
| **Google** | graphs, DP, trees, hard recursion; **optimal + clean + complexity** | "Googleyness", system design (L5+); ask clarifying Qs |
| **Meta** | arrays/strings, BFS/DFS; **fast pace (≈2 Qs/round)** | behavioral signals, system design; communicate while coding |
| **Amazon** | trees, graphs, DP, heaps; clean working code | **Leadership Principles (STAR)** heavily; bar-raiser |
| **Microsoft** | arrays, strings, trees, linked lists; practical | design + behavioral; clarity valued, friendlier pace |
| **Apple** | domain + DSA, depth in your area | team-specific; strong fundamentals |
| **Netflix** | senior **system design** + DSA | culture ("freedom & responsibility"); fewer, senior rounds |
| **Uber/Stripe** | practical coding, API design, concurrency | Stripe: integration-style coding; system design |
| **OpenAI/Anthropic** | strong DSA + ML/AI eng + practical coding | research/eng depth (see Module 21) |
| **NVIDIA** | DSA + systems/CUDA/perf | cache/memory awareness valued (Module 1) |
| **Databricks/Palantir** | DSA + distributed/data systems | design; sometimes take-home |

- **Amazon LP tip:** prepare ~10 STAR stories mapped to the Leadership Principles;
  every behavioral answer ties to one.
- **Google tip:** they want the *optimal* solution and a crisp complexity
  argument; partial/brute-only often isn't enough at the bar.

### MCQs

1. Amazon's signature non-coding round? → **Leadership Principles (STAR)**.
2. Meta interview pace? → **fast** (~2 problems/round).
3. Google emphasises? → **optimal solution + clean code + complexity**.

---

## 20.5 A Realistic Study Plan

- **Foundation (weeks 1–8):** learn patterns (this course M1–M14) + ~100 problems
  across patterns.
- **Volume (weeks 9–16):** Neetcode 150 / Blind 75; ~150–200 problems; redo missed
  ones.
- **Polish (weeks 17–24):** **mock interviews** (Pramp/peers), company-tagged
  problems, behavioral prep, system design (for senior).
- **Daily:** 2–4 problems, always **timed** (35–45 min), always **think-aloud**.
- **Weakness log:** track every problem you missed and *why* (pattern? bug? edge
  case?) and re-drill it.

> See the Excel **"6-Month Roadmap"** and **"Interview Roadmap"** tabs for the
> week-by-week and company-by-company plans.

### MCQs

1. Practice problems how? → **timed + think-aloud**.
2. What to track? → a **weakness log** (what you missed and why).
3. Senior rounds add? → **system design** + behavioral.

---

## Module 20 — Concept Review (one page)

- **Framework:** Clarify → Examples → Approach (brute force first) → Code → Test →
  Complexity. Communication + complexity + edge cases are scored.
- **Pattern map:** learn keyword → technique (binary search, sliding window, heap,
  monotonic stack, backtracking, DP, graphs, hashmap, intervals, prefix sum).
- **Lists:** Blind 75 (minimum), Neetcode 150 (structured), Grind (scheduled);
  breadth → depth; track in the Excel Top-300 tab.
- **Companies:** Google (optimal+clean), Meta (fast pace), Amazon (LP/STAR),
  Microsoft (practical), AI labs (DSA+ML).
- **Plan:** patterns → volume → mocks; daily timed think-aloud; keep a weakness
  log.

## Module 20 — Flash Cards

- Q: Steps before coding? **A: clarify, examples, approach (brute force first).**
- Q: Top scored signal? **A: communication / think-aloud.**
- Q: Best structured list? **A: Neetcode 150.**
- Q: Amazon's key round? **A: Leadership Principles (STAR).**
- Q: Practice style? **A: timed + think-aloud + weakness log.**

## Module 20 — Pattern Recognition

(See §20.2 table — the master keyword→technique map. This *is* the interview
skill: classify the problem, then apply the right module.)

## Module 20 — Interview Questions (meta-level)

1. *Walk me through how you'd approach an unfamiliar problem.* → the framework.
2. *Give the brute force, then optimise.* → always lead with brute + complexity.
3. *What's the time/space complexity, and the trade-off?* → state both, discuss.
4. *(Amazon)* *Tell me about a time you…* → STAR story mapped to an LP.

## Module 20 — GATE / SEBI / RBI / ISRO Perspective

- Different format (MCQ/written), but the **pattern-recognition** and
  **complexity** reflexes transfer directly. For exams, prioritise the
  module-by-module mastery (M1–M18) over interview-specific drills.

---

*End of Module 20. Next: Module 21 — AI Engineering DSA (vector search, ANN,
HNSW/FAISS, beam search, tokenization, RAG) — with visuals.*
