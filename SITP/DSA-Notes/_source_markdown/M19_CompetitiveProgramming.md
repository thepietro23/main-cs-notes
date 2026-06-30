---
title: "Module 19 — Competitive Programming"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 19 — Competitive Programming

> **Why CP, even for interviews.**
> Competitive programming (Codeforces, AtCoder, ICPC, LeetCode contests) sharpens
> the exact muscles FAANG interviews test: pattern recognition, fast bug-free
> coding, complexity reasoning under time pressure, and edge-case discipline. This
> module is **strategy, not new algorithms** — it shows how to *use* everything
> from M1–M18 to solve unseen problems fast.

This module is **P2** (P0 for ICPC/Codeforces goals).

> **How to read.** Strategy, the constraint→complexity reflex, language/IO setup,
> contest workflow, and per-platform patterns.

---

## 19.1 The #1 Reflex: Constraints → Complexity

Before writing any code, read `n` and **work backwards** to the intended
complexity (assume ~10⁸ simple operations/second, 1–2 s limit):

![Constraint-to-complexity cheat sheet: n≤20 → O(2ⁿ), n≤500 → O(n³), n≤10⁵ → O(n log n), etc.](images/132_constraints_complexity.png)

| Input size `n` | Target | Typical technique |
|---|---|---|
| ≤ 10–12 | O(n!) | permutations / brute backtracking |
| ≤ 20–25 | O(2ⁿ), O(2ⁿ·n) | bitmask DP / subset enumeration |
| ≤ 100 | O(n³) | Floyd-Warshall / interval DP |
| ≤ 1000–5000 | O(n²) | 2D DP / all pairs |
| ≤ 10⁵–10⁶ | O(n log n) | sort, heap, segment tree, binary search |
| ≤ 10⁷–10⁸ | O(n) | two pointers, prefix sum, greedy |
| up to 10¹⁸ | O(log n)/O(1) | math, fast exponentiation, formula |

> **This table is the single highest-value CP skill** — it usually tells you the
> intended algorithm *before* you start. (`10¹⁸` doesn't fit in 32 bits → use
> 64-bit `long long`.)

### MCQs

1. `n ≤ 20` suggests? → **O(2ⁿ)** (bitmask DP / subsets).
2. `n ≤ 10⁶` suggests? → **O(n log n)** or O(n).
3. Answer up to `10¹⁸` needs what type? → **64-bit (long long)**.

---

## 19.2 Setup: Language, Fast I/O, Templates

- **Language:** **C++** dominates CP (speed + STL); Python is fine for easier
  problems but risks TLE on tight limits (use fast I/O, PyPy on Codeforces).
- **Fast I/O** (the most common avoidable TLE):
  - C++: `ios_base::sync_with_stdio(false); cin.tie(NULL);` and prefer `'\n'` over
    `endl`.
  - Java: `BufferedReader`/`StreamTokenizer` + `StringBuilder`, not `Scanner`.
  - Python: `sys.stdin.readline` / read all input at once; `sys.stdout.write`.
- **Template/library:** keep a personal file with fast I/O, GCD, modpow, sieve,
  DSU, segment tree, Dijkstra, etc. (everything from M1–M18) ready to paste.
- **64-bit overflow:** the #1 silent bug — use `long long` (C++) / `long` (Java)
  whenever products or sums can exceed ~2×10⁹.

### MCQs

1. Most common avoidable TLE cause? → slow I/O (`endl`/`Scanner`).
2. Default CP language & why? → **C++** (speed + STL).
3. When to switch to `long long`? → products/sums beyond ~2×10⁹.

---

## 19.3 Contest Workflow & Time Management

![Contest strategy: scan all problems, solve easiest first, derive complexity from constraints, test edge cases, move on if stuck.](images/133_cp_strategy.png)

1. **Scan ALL problems first** — sort by difficulty (Codeforces shows #solves; the
   most-solved is usually easiest). Don't anchor on problem A.
2. **Solve the easiest first** — bank quick points; build momentum.
3. **Constraints → complexity** — pick the algorithm before coding.
4. **Code + test edge cases** — n = 0/1, empty, max bounds, overflow, all-equal,
   negatives.
5. **Stuck 15–20 min? Move on** — come back later; avoid tunnel vision.
6. **Test locally before submitting** — wrong submissions cost **penalty time**;
   a quick local test beats a WA penalty.

> **Memory hook:** a contest rewards **most problems solved**, not the hardest one
> attempted. Greedily grab the cheap points.

### MCQs

1. Which problem to attempt first? → the **easiest** (most #solves).
2. Stuck for ~20 min? → **move on**, return later.
3. Why test locally first? → avoid **wrong-submission penalties**.

---

## 19.4 Common Pitfalls (lose-the-problem bugs)

- **Integer overflow** (use 64-bit; mod after every op — Module 16).
- **Off-by-one** in loops/binary search (Module 12 template).
- **Uninitialised / not reset** state between test cases (multi-testcase
  problems — clear arrays!).
- **Wrong complexity** for the constraints (TLE) — re-check §19.1.
- **Edge cases:** empty input, single element, all-same, max/min values, n=0.
- **Recursion depth / stack overflow** on deep DFS (Module 1) — increase stack or
  go iterative.
- **Floating point** equality / precision — prefer integers or an epsilon.
- **Reading input wrong** (counts, 0- vs 1-indexed).

### MCQs

1. Multi-testcase silent bug? → **not resetting** global state between cases.
2. Deep DFS risk? → **stack overflow** (go iterative / raise limit).
3. Equality on floats? → avoid; use **epsilon** or integers.

---

## 19.5 Platform Patterns

- **Codeforces (Div 2):** A/B are observation/greedy/math; C/D need a clean
  algorithm (DP, graphs, number theory); E/F are hard. **Rating** ≈ difficulty;
  practice slightly above your level. Strong on **constructive** and **greedy +
  proof** problems.
- **AtCoder (ABC):** clean, math-leaning, well-tested; great for fundamentals;
  difficulty ramps smoothly A→F.
- **ICPC (team, 5 hours, 1 computer):** **breadth + teamwork** — one reads/finds
  problems, others code; share a printed **team reference document (notebook)**;
  prioritise by #solves on the scoreboard.
- **LeetCode contests:** closest to interviews; 4 problems in ~1.5 h; speed +
  accuracy.

### Practice approach

- **Upsolve:** after a contest, solve the problems you *couldn't* — that's where
  the learning is.
- Practice **by topic** (ladders) and **by rating**; track patterns you keep
  missing.
- Maintain your **template library** and a list of "tricks I forgot".

### MCQs

1. Best way to improve after a contest? → **upsolve** the unsolved problems.
2. ICPC format? → **team of 3, 1 computer, ~5 hours**; use a team notebook.
3. Codeforces A/B problems are usually? → greedy/math/observation.

---

## Module 19 — Concept Review (one page)

- **Constraints → complexity** is the master reflex (n≤20→2ⁿ, n≤500→n³,
  n≤10⁵→n log n, n≤10⁷→n, huge→log/formula).
- **Setup:** C++ + STL, **fast I/O** (sync_with_stdio / BufferedReader /
  sys.stdin), template library, **64-bit** for overflow.
- **Workflow:** scan all → easiest first → derive complexity → test edge cases →
  move on if stuck → test locally before submit.
- **Pitfalls:** overflow, off-by-one, unreset state, wrong complexity, edge cases,
  recursion depth, float precision.
- **Platforms:** Codeforces (greedy/constructive + rating), AtCoder (clean math),
  ICPC (team/breadth), LeetCode (interview-like). **Upsolve** to improve.

## Module 19 — Flash Cards

- Q: n ≤ 20 → ? **A: O(2ⁿ) bitmask/subsets.**
- Q: n ≤ 10⁵ → ? **A: O(n log n).**
- Q: #1 avoidable TLE? **A: slow I/O.**
- Q: Which problem first in a contest? **A: easiest (most #solves).**
- Q: Multi-testcase bug? **A: forgot to reset state.**
- Q: Best post-contest practice? **A: upsolve.**

## Module 19 — Pattern Recognition (map constraints to M1–M18)

- "n tiny (≤20)" → bitmask DP (M14c) / backtracking (M13).
- "n ≤ few hundred" → O(n²)/O(n³) DP (M14) / Floyd (M10b).
- "n ≤ 10⁵, many queries" → sort + binary search (M12) / segment tree (M8b) /
  prefix sum (M2).
- "huge n / huge answer" → math, fast exponentiation, mod (M16).
- "shortest path / connectivity" → BFS/Dijkstra/DSU (M10).

## Module 19 — Interview crossover

CP habits that win interviews: derive complexity from constraints out loud,
enumerate edge cases first, test before claiming done, and recognise the pattern
fast. (The **interview** craft itself is Module 20.)

## Module 19 — GATE / SEBI / RBI / ISRO Perspective

- Not directly examined, but the **complexity-from-constraints** reflex and clean
  implementation help in any timed coding/aptitude round.

---

*End of Module 19. Next: Module 20 — Google / FAANG Interview Preparation
(Blind 75, Neetcode 150, company patterns, the interview framework) — with
visuals.*
