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

### 19.2a Fast I/O templates (paste-ready)

Keep these at the top of every solution. They routinely turn a TLE into an AC on
input-heavy problems.

**C++** — the standard header:

```text
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);   // unhook C++ streams from C stdio
    cin.tie(NULL);                      // don't flush cout before every cin
    // ... read with cin, print with cout, use '\n' NOT endl (endl flushes) ...
    return 0;
}
```

**Java** — never use `Scanner` on big input:

```text
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
StringBuilder sb = new StringBuilder();          // batch output
int n = Integer.parseInt(br.readLine().trim());
StringTokenizer st = new StringTokenizer(br.readLine());
// ... build answer in sb ...
System.out.print(sb);                            // one big write at the end
```

**Python** — read in one shot, avoid `input()` in loops:

```text
import sys
input = sys.stdin.readline          # faster line reads
data = sys.stdin.buffer.read().split()   # or: read EVERYTHING at once
# ... process the token list `data` ...
sys.stdout.write("\n".join(map(str, answers)) + "\n")   # one big write
```

- **Why it matters:** `endl` flushes the buffer every call; `Scanner` parses with
  regex; `input()` in a tight loop re-acquires locks. On 10⁶ lines these dominate
  the runtime.
- On Codeforces, if Python is too slow even with fast I/O, **switch to PyPy**.

> **Memory hook:** *read in bulk, print in bulk, never flush in a loop.*

### MCQs

1. In C++, why prefer `'\n'` over `endl`? → **`endl` flushes every time**.
2. Java fast input class? → **`BufferedReader`** (not `Scanner`).
3. Fast Python input? → **`sys.stdin.readline` / read all at once**.

### 19.2b STL / standard-library must-knows

Most CP problems are "known algorithm + the right container". Know these cold:

| Need | C++ STL | Cost |
|---|---|---|
| dynamic array | `vector` | push_back amortised O(1) |
| sorted unique set / ordered map | `set` / `map` | **O(log n)** per op |
| hash set / map (unordered) | `unordered_set` / `unordered_map` | avg **O(1)** |
| priority queue (heap) | `priority_queue` | push/pop **O(log n)** |
| double-ended queue | `deque` | push/pop both ends O(1) |
| sort / stable_sort | `sort(v.begin(), v.end())` | **O(n log n)** |
| binary search on sorted | `lower_bound` / `upper_bound` | **O(log n)** |
| next permutation | `next_permutation` | O(n) per step |
| gcd / built-in popcount | `__gcd`, `__builtin_popcount` | O(log), O(1) |

- **`lower_bound` vs `upper_bound`:** `lower_bound(x)` = first element **≥ x**;
  `upper_bound(x)` = first element **> x**. Their difference counts occurrences of
  `x` in a sorted array.
- **Watch out:** `unordered_map` can be hacked to O(n) per op on Codeforces (anti-
  hash tests) — use a custom hash or fall back to `map` if you get a surprise TLE.
- Java equivalents: `ArrayList`, `TreeSet`/`TreeMap`, `HashMap`, `PriorityQueue`,
  `ArrayDeque`, `Collections.sort`, `Arrays.binarySearch`.

### MCQs

1. `lower_bound(x)` returns? → **first element ≥ x**.
2. `upper_bound(x) − lower_bound(x)` gives? → **count of x** in a sorted range.
3. Sudden `unordered_map` TLE on Codeforces? → **anti-hash test; use custom
   hash / `map`**.

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

### 19.3a How to debug inside a contest (fast)

The verdict tells you *what kind* of bug it is — read it first:

| Verdict | Likely cause | First thing to check |
|---|---|---|
| **WA** (wrong answer) | logic / edge case | re-read statement; test n=0/1, all-equal, max |
| **TLE** (time limit) | wrong complexity or slow I/O | recheck §19.1 target; fast I/O; `endl` |
| **RE** (runtime error) | out-of-bounds / div-by-zero / stack | array sizes, `n+1`, deep recursion |
| **MLE** (memory) | too-big arrays / recursion | reduce dimensions; iterative |

A tight debugging loop:

1. **Re-read the statement** — most WAs are a misread constraint or output format
   (spaces, newlines, "print YES/NO" case), not a code bug.
2. **Test the given samples locally** — if a sample fails, the bug is easy to find.
3. **Stress test** when a WA has no obvious cause: write a tiny **brute force**,
   generate random small inputs, and diff the two outputs until they disagree —
   that first mismatch is a minimal failing case.

```text
# stress-test loop (shell)
while true; do
    ./gen > in.txt              # random small input
    ./brute < in.txt > b.txt    # obviously-correct slow solution
    ./fast  < in.txt > f.txt    # your suspect solution
    diff b.txt f.txt || { echo "MISMATCH:"; cat in.txt; break; }
done
```

4. **Add asserts / print intermediate state** on the failing case, not blindly.
5. **Binary-search the bug:** comment out halves of the logic to localise it.

> **Memory hook:** the verdict names the *category*; samples + a stress test
> against a brute force find the *exact* input that breaks you.

### MCQs

1. WA with no obvious cause? → **stress test vs a brute force** to find a minimal
   case.
2. RE most often means? → **out-of-bounds / bad array size / deep recursion**.
3. First response to any wrong verdict? → **re-read the statement / output
   format**.

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

### 19.4a Pre-submit checklist (run this every time)

Before you hit submit, sweep this list — it catches the bugs above *before* the
penalty:

```text
OVERFLOW
  [ ] any product/sum > 2e9 ?  -> long long (C++) / long (Java)
  [ ] a*b in a mod problem ?   -> cast to long long BEFORE multiplying
  [ ] mid = (l+r)/2 overflow ? -> mid = l + (r-l)/2

OFF-BY-ONE / INDEXING
  [ ] 0-indexed vs 1-indexed consistent everywhere?
  [ ] loop bounds:  < n  vs  <= n ?  arrays sized n or n+1 ?
  [ ] binary search:  is the search space [l, r] or [l, r) ?  which end moves?
  [ ] substring/prefix ranges inclusive or exclusive?

EDGE CASES
  [ ] n = 0 ?  n = 1 ?  empty input/line ?
  [ ] all elements equal / all zero / all negative ?
  [ ] max bound (e.g. n = 1e5, a_i = 1e9) — does it still fit / finish in time?
  [ ] single query / single element range ?

STATE (multi-testcase)
  [ ] cleared every global array / map / counter between test cases?
  [ ] reset `answer`, visited[], and any accumulator?

OUTPUT FORMAT
  [ ] exact spacing / newlines ?  "YES"/"Yes" case as the statement says ?
  [ ] printed all t answers (not just the last) ?
```

- **The classic overflow trap:** `int a, b;  long long p = a * b;` still overflows
  — the multiply happens in `int` *first*. Fix: `(long long)a * b`.
- **The classic binary-search off-by-one:** decide up front whether your interval
  is `[l, r]` (both inclusive) or `[l, r)` and keep the update (`l = mid+1` vs
  `r = mid`) consistent with that choice (Module 12).

> **Memory hook:** *overflow, off-by-one, edges, reset, format* — five checks, ten
> seconds, saves a penalty.

### MCQs

1. `int a,b; long long p = a*b;` bug? → **multiply is done in `int` first
   (overflow)**; cast first.
2. Overflow-safe midpoint? → **`mid = l + (r-l)/2`**.
3. Cheapest way to avoid a WA on the last subtask? → **run the pre-submit
   checklist (edges + reset + format)**.

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

**Upsolving done right** (the highest-ROI habit in CP):

1. Right after the contest, **retry the first problem you couldn't solve** on your
   own — no editorial yet. A fresh, no-clock attempt teaches the most.
2. Only after you are truly stuck, read the editorial **up to the key idea**, then
   close it and finish the implementation yourself.
3. **Implement and get it accepted** — reading the solution is not learning; typing
   it and passing tests is.
4. Write one line in your notes: *what signal should have told me the technique?*
   (This feeds your Pattern Recognition instincts.)
5. Revisit the problem **a week later** from scratch to confirm it stuck.

> **Memory hook:** the problems you *failed* are your syllabus. Solve them without
> the editorial, then log the missed signal.

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
- Q: `int a,b; long long p=a*b;` fix? **A: cast `(long long)a*b` before multiply.**
- Q: Overflow-safe midpoint? **A: `l + (r-l)/2`.**
- Q: `lower_bound(x)` returns? **A: first element ≥ x.**
- Q: WA with no clue? **A: stress test vs a brute force.**
- Q: Fast Java input? **A: BufferedReader + StringBuilder (not Scanner).**

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
