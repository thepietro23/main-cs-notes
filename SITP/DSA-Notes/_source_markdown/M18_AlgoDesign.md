---
title: "Module 18 — Algorithm Design & Analysis"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 18 — Algorithm Design & Analysis

> **Why this module.**
> So far we learned *algorithms*; this module is about **reasoning rigorously
> about them**: solving recurrences, proving amortized bounds, using randomness,
> settling for approximate answers when exact is too hard, and the **P vs NP**
> landscape that tells you *which problems are hopeless to solve exactly*. This is
> the **theory backbone** of GATE and senior-interview "why" questions.

This module is **P1** (P0 for GATE). Recurrences, amortized analysis, and P/NP are
heavily tested in exams.

> **How to read each technique.** The idea, the method, plus a memory hook.

---

## 18.1 Solving Recurrences

![Three ways to solve a recurrence: Master Theorem, recursion tree, substitution.](images/131_recurrence_methods.png)

Three tools (full Master Theorem in Module 1 §1.5 & Module 12 §12.1):

1. **Master Theorem** — for `T(n) = a·T(n/b) + f(n)`: compare `f(n)` with
   `n^(log_b a)` (3 cases). Fast, but only this exact shape.
2. **Recursion tree** — draw the tree, sum **work per level × number of levels**.
   Intuitive, works for any shape (e.g. uneven splits).
3. **Substitution** — guess the bound, prove by induction. The fallback when the
   others don't apply.

**Per-case intuition** (compare leaf work `n^(log_b a)` with `f(n)`):

- **Leaf-dominated** (Case 1): the recursion's leaves do the most work → `Θ(n^(log_b
  a))`.
- **Balanced** (Case 2): every level costs the same → multiply by `log n`.
- **Root-dominated** (Case 3): the top-level `f(n)` dominates → `Θ(f(n))` (needs
  the **regularity condition** `a·f(n/b) ≤ c·f(n)`).
- **Gap cases** the basic theorem can't solve (e.g. `T(n)=2T(n/2)+n/log n`, where
  `f(n)` sits within a polylog factor of the threshold) → use recursion-tree /
  **Akra–Bazzi**.

- **Example:** `T(n) = 2T(n/2) + n` → all three give **Θ(n log n)**.
- **Subtract-and-conquer** `T(n) = a·T(n−b) + f(n)` (e.g. naive recursion) needs
  the tree/substitution method, **not** the Master Theorem. `T(n)=T(n−1)+O(1)` →
  O(n); `T(n)=2T(n−1)+O(1)` → O(2ⁿ).
- **Akra–Bazzi** generalises the Master Theorem to unequal splits.

### MCQs

1. `T(n)=2T(n/2)+n`? → **Θ(n log n)**.
2. `T(n)=2T(n−1)+1`? → **Θ(2ⁿ)** (subtract-and-conquer, not Master).
3. Method when Master doesn't apply? → **recursion tree / substitution**.

---

## 18.2 Amortized Analysis

**Amortized** cost = the average cost **per operation over a worst-case
sequence** (a *guarantee*, unlike average-case which is probabilistic).

![Amortized analysis: most appends cost O(1), rare doublings cost O(n); total 2n → O(1) amortized.](images/129_amortized.png)

Three methods to prove it:

| Method | Idea |
|---|---|
| **Aggregate** | total cost of n ops ÷ n |
| **Accounting** | overcharge cheap ops, store "credit" to pay for expensive ones |
| **Potential (Φ)** | define a potential function; amortized = actual + ΔΦ |

- **Classic example:** **dynamic-array append** — usually O(1), but doubling costs
  O(n); total for n appends = `1+2+4+…+n ≈ 2n` → **O(1) amortized** (Module 2).
- Other examples: **Fenwick/splay** operations, the **Union-Find** with path
  compression (O(α(n)) amortized), incrementing a binary counter.

> **Memory hook:** amortized = "pay a little extra each cheap step into a piggy
> bank, so the occasional expensive step is already paid for."

> **Senior caveat:** amortized O(1) bounds a **sequence**, not a **single**
> operation — one append can still cost O(n). For **latency-sensitive / real-time**
> systems (p99 spikes during a rehash!), use **de-amortized / incremental-resize**
> variants that spread the rebuild work over many operations.

### MCQs

1. Amortized vs average-case? → amortized is a **guarantee over a sequence**;
   average-case is **probabilistic**.
2. Three methods? → **aggregate, accounting, potential**.
3. Dynamic array append amortized? → **O(1)** (total 2n).

---

## 18.3 Randomized Algorithms

Use randomness to get simplicity or good *expected* performance.

- **Las Vegas** algorithms: always **correct**, running time is random (e.g.
  **randomized quicksort** — expected O(n log n), avoids the sorted-input worst
  case by picking a random pivot).
- **Monte Carlo** algorithms: fixed running time, **possibly wrong** with small
  probability (e.g. **Miller–Rabin** primality test, **Rabin-Karp** hashing).
- **Reservoir sampling**, **Fisher–Yates shuffle**, **rand7→rand10** (Module 16).
- **Why it really helps (the key insight):** the expectation is taken over the
  algorithm's **coin flips**, not over the input. A *deterministic* algorithm has a
  fixed worst-case input an adversary can always feed it; with randomization the
  "bad" inputs depend on hidden coins, so **no single input is reliably bad**.
- **Error amplification:** a one-sided Monte Carlo algorithm with error ≤ `p` run
  `k` independent times has error ≤ `pᵏ` → that's why "maybe wrong" is fine in
  practice. *Miller–Rabin:* each round errs with prob ≤ ¼, so `k` rounds ≤ `4⁻ᵏ`.
- **When to randomize:** simpler code, breaking symmetry / adversarial inputs, or
  when an expected/high-probability bound suffices and worst-case is unaffordable.

### MCQs

1. Las Vegas vs Monte Carlo? → always-correct/random-time vs fixed-time/maybe-wrong.
2. Random pivot in quicksort gives? → **expected O(n log n)** (defeats worst case).
3. Miller–Rabin is which type? → **Monte Carlo** (tiny error probability).

---

## 18.4 Approximation Algorithms

When a problem is **NP-hard** (no known efficient exact algorithm), settle for a
provably-close answer. An algorithm is a **ρ-approximation** if its answer is
always within a factor ρ of optimal.

- **Vertex Cover — 2-approximation:** repeatedly pick **both endpoints** of any
  uncovered edge → at most 2× the optimal cover. Simple and provable.
- **TSP (metric) — 2-approximation** via MST (1.5× with Christofides).
- **Set Cover — ln n approximation** (greedy: always take the set covering the most
  uncovered elements).

> **Memory hook:** "can't solve it exactly fast → guarantee 'no worse than ρ×
> optimal'."

### The "it's NP-hard — now what?" pivot menu

1. **Exact but exponential** (fine for small n): DP over subsets (**Held-Karp**
   TSP O(2ⁿ·n²)), **meet-in-the-middle** (Subset Sum O(2^(n/2))),
   **branch & bound** (Module 13).
2. **Pseudo-polynomial DP** when numeric inputs are small (Knapsack O(nW) —
   §18.5).
3. **Approximation with a guarantee** — ρ-approx, and the stronger tiers **PTAS**
   (any 1+ε) / **FPTAS** (also polynomial in 1/ε).
4. **Heuristics with NO guarantee** — greedy, local search, simulated annealing,
   ILP solvers (fast in practice, no proven bound — *different* from
   approximation).
5. **Fixed-parameter tractable (FPT)** — fast when a parameter `k` is small (e.g.
   `f(k)·nᶜ`).

### MCQs

1. ρ-approximation means? → answer within factor **ρ** of optimal.
2. Vertex cover greedy (both endpoints) ratio? → **2**.
3. Greedy set cover ratio? → **ln n**.

---

## 18.5 P, NP, NP-complete, NP-hard

![Complexity classes: P ⊆ NP, NP-complete = hardest in NP, NP-hard ⊇ NP-complete (assuming P ≠ NP).](images/130_complexity_classes.png)

- **P** — solvable in **polynomial time** (sorting, shortest path, matching).
- **NP** — a proposed solution can be **verified** in polynomial time (you may not
  be able to *find* it fast). P ⊆ NP.
- **NP-complete** — the **hardest problems in NP**: in NP **and** every NP problem
  reduces to them. If *any* NP-complete problem has a poly-time algorithm, then
  **P = NP**. Examples: **SAT** (Cook–Levin), 3-SAT, Clique, Vertex Cover,
  Hamiltonian Cycle, Subset Sum, Graph Coloring, TSP (decision).
- **NP-hard** — at least as hard as NP-complete, but **need not be in NP** (e.g.
  the optimisation/halting versions). 

**Reductions** are the tool: to show problem `X` is NP-hard, **reduce a known
NP-complete problem to X** in polynomial time ("if I could solve X fast, I could
solve SAT fast").

> **Memory hook:** **P** = easy to *solve*; **NP** = easy to *check*;
> **NP-complete** = the hardest "checkable" problems; **NP-hard** = at least that
> hard (maybe not even checkable).

### Pseudo-polynomial & weak vs strong NP-completeness

"Knapsack/Subset Sum are NP-complete, but DP solves them in O(nW)?" — the
resolution: **O(nW) is polynomial in the numeric *value* W, but exponential in its
*bit-length* (log W)** → **pseudo-polynomial**, not truly polynomial.

- **Weakly NP-complete** (Subset Sum, 0/1 Knapsack): admit a pseudo-poly DP and an
  **FPTAS**.
- **Strongly NP-complete** (3-SAT, TSP): **no** pseudo-poly algorithm unless P=NP.

### Beyond NP — undecidable (GATE)

Some problems have **no algorithm at all**: the **Halting Problem** (does program
P halt on input x?) is **undecidable** (Turing). Undecidable ≫ NP-hard:
NP-hard means "no *fast* algorithm (likely)"; undecidable means "no algorithm,
ever." **co-NP** = problems whose *no*-answers are easily verified (e.g.
"is this formula UNSAT?").

### MCQs

1. P vs NP in one line? → solvable-in-poly vs verifiable-in-poly.
2. First proven NP-complete problem? → **SAT** (Cook–Levin theorem).
3. To prove X is NP-hard? → **reduce** a known NP-complete problem to X.
4. NP-complete = ? → in NP **and** NP-hard.

---

## 18.6 Online vs Offline Algorithms (the competitive ratio)

- **Offline:** the whole input is known up front (everything so far in this
  course).
- **Online:** input arrives **one piece at a time** and each decision is
  **irrevocable** (you can't see the future) — caching/eviction, ski-rental, load
  balancing.

Quality metric = the **competitive ratio** `c`: `online_cost ≤ c · OPT_offline +
constant` for *every* input. (Parallel to the approximation ratio, but the
limitation is **missing future info**, not computational hardness.)

- **Ski-rental** ("rent for \$1/day or buy for \$B?"): renting until day B then
  buying is **2-competitive** (e/(e−1) ≈ 1.58 randomized).
- **Paging / cache eviction:** any deterministic policy is **k-competitive** (k =
  cache size); **LRU** achieves it; the offline optimum **OPT** evicts the page
  used farthest in the future (Bélády) — but that needs the future.
- **List update:** **move-to-front** is 2-competitive.

> **Interview link:** "your cache is LRU — how good is that vs a clairvoyant
> optimum?" → competitive ratio; LRU is k-competitive, OPT = Bélády.

### MCQs

1. Online vs offline? → decide **irrevocably as input arrives** vs **whole input
   known**.
2. Quality metric for online algorithms? → the **competitive ratio**.
3. Optimal *offline* page replacement? → **Bélády** (evict farthest-future use).

## Module 18 — Concept Review (one page)

- **Recurrences:** Master Theorem (a·T(n/b)+f(n), 3 cases) | recursion tree
  (work/level × levels) | substitution (guess+induct); subtract-and-conquer →
  not Master.
- **Amortized:** guaranteed average over a sequence; aggregate / accounting /
  potential; dynamic array O(1), Union-Find O(α(n)).
- **Randomized:** Las Vegas (correct, random time) vs Monte Carlo (fixed time,
  maybe wrong); random pivot, Miller–Rabin, reservoir.
- **Approximation:** ρ-approx for NP-hard; vertex cover 2×, set cover ln n, metric
  TSP 1.5× (Christofides).
- **P/NP:** P solve, NP verify, NP-complete = hardest in NP (SAT), NP-hard ≥ that;
  prove hardness by **reduction**.

## Module 18 — Flash Cards

- Q: 3 recurrence methods? **A: Master, recursion tree, substitution.**
- Q: Amortized vs average? **A: sequence-guarantee vs probabilistic.**
- Q: Union-Find amortized? **A: O(α(n)).**
- Q: Las Vegas vs Monte Carlo? **A: always-correct/random-time vs fixed/maybe-wrong.**
- Q: Vertex cover approx ratio? **A: 2.**
- Q: First NP-complete problem? **A: SAT (Cook–Levin).**
- Q: Prove NP-hardness? **A: reduce a known NP-complete problem to it.**

## Module 18 — Pattern Recognition

- "Solve T(n) = …" → Master / tree / substitution.
- "Average cost over many ops" → **amortized** (aggregate/accounting/potential).
- "Defeat worst-case input" → **randomization** (random pivot).
- "NP-hard, need *some* answer fast" → **approximation / heuristic**.
- "Is this problem even tractable?" → place it in **P / NP / NP-complete**.

## Module 18 — Interview Questions (with follow-ups)

1. *Why is randomized quicksort O(n log n) expected?* FU: *what input breaks
   deterministic quicksort?*
2. *Prove dynamic-array append is amortized O(1).* FU: *3 methods.*
3. *Is problem X solvable in poly time?* FU: *reduce from a known NP-complete
   problem.*
4. *Give a 2-approximation for vertex cover.* FU: *prove the ratio.*

## Module 18 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites (very high yield):** solving recurrences (Master theorem +
  tricky cases), amortized analysis, **P/NP/NP-complete/NP-hard** definitions and
  reductions, identifying which problems are NP-complete, approximation ratios.
  These appear almost every year.

---

*End of Module 18. Next: Module 19 — Competitive Programming (contest strategy,
fast I/O, templates, Codeforces/AtCoder/ICPC patterns) — with visuals.*
