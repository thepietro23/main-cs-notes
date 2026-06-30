---
title: "Module 14a — Dynamic Programming: Foundations, 1D, 2D"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14a — Dynamic Programming: Foundations, 1D & 2D

> **Why DP is the boss level.**
> Dynamic Programming is the single most feared (and most asked) interview topic.
> The idea is simple once it clicks: **a hard problem = the answer to smaller
> versions of itself, and we never solve the same small version twice.** Master
> the *thinking framework* — define a state, write a recurrence, choose top-down
> or bottom-up — and DP stops being scary. This part builds the foundations and
> the 1D/2D patterns; M14b covers sequences & knapsack; M14c covers advanced DP.

This module is **P0** — DP is the highest-leverage interview + GATE topic.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

### Designing any DP (the 5-step recipe)

![How to design a DP: state → recurrence → base cases + order → memoize/tabulate → optimise space.](images/108_fc_dp.png)

---

## 14a.1 Foundations — when & how

### The two requirements (same as greedy's, plus overlap)

1. **Optimal substructure:** the optimal answer is built from optimal answers to
   subproblems.
2. **Overlapping subproblems:** the same subproblems recur many times (so caching
   pays off).

If you have optimal substructure but **no** overlap → use **divide & conquer** or
**greedy** instead. DP's whole value is *reusing* repeated subproblems.

![DP = recursion + remembering answers; fib recomputes f3/f2 (orange) — cache them. Two styles: memoization (top-down) and tabulation (bottom-up).](images/104_dp_concept.png)

### Memoization (top-down) vs Tabulation (bottom-up)

| | Memoization (top-down) | Tabulation (bottom-up) |
|---|---|---|
| Style | recursion + a cache | iterative table fill |
| Solves | only subproblems you **need** | **all** subproblems in order |
| Risk | recursion stack overflow (deep) | must get the **fill order** right |
| Ease | mirrors the recurrence (easy) | no recursion overhead (fast) |

Both are **same time complexity**; pick whichever is clearer. Interviewers accept
either, but often like "I'll write it top-down first, then convert to bottom-up".

> **Practical warning:** when constraints reach **~10⁵+**, deep top-down recursion
> can **overflow the stack** — there the bottom-up conversion becomes *mandatory*,
> not just a style choice. (This is *why* the "convert to iterative" follow-up
> exists.)

### The 5-step DP recipe (say this out loud in interviews)

1. **State:** what does `dp[i]` / `dp[i][j]` *mean*? (the hardest, most important
   step.)
2. **Recurrence:** how does a state depend on smaller states (the transition)?
3. **Base cases** + the **iteration order** (so dependencies are ready).
4. **Memoize or tabulate.**
5. **Optimise space** (often only the last 1–2 rows/values are needed).

> **Memory hook:** *"Don't solve the same subproblem twice — write its answer on a
> sticky note."* DP = recursion + sticky notes.

### MCQs

1. Two requirements for DP? → **optimal substructure + overlapping subproblems**.
2. Optimal substructure but NO overlap → use? → **divide & conquer / greedy**.
3. Top-down vs bottom-up time? → **same**; differ in style/overhead.

---

## 14a.2 The Fibonacci ladder (memoization → tabulation → O(1))

```text
# BRUTE FORCE: plain recursion                Time O(φ^n), Space O(n) stack
fib(n): return n if n<2 else fib(n-1)+fib(n-2)

# BETTER: memoization (top-down)              Time O(n), Space O(n)
memo={}; fib(n): if n<2 return n; if n in memo return memo[n]
                 memo[n]=fib(n-1)+fib(n-2); return memo[n]

# GOOD: tabulation (bottom-up)                Time O(n), Space O(n)
dp[0]=0; dp[1]=1; for i in 2..n: dp[i]=dp[i-1]+dp[i-2]

# OPTIMAL: rolling variables                  Time O(n), Space O(1)
a,b=0,1; repeat n times: a,b = b, a+b; return a
```

This exact ladder (exponential → O(n) → O(1) space) is the template for almost
every 1D DP.

---

## 14a.3 1D DP Patterns

### Climbing Stairs / Fibonacci-shaped

`dp[i] = dp[i-1] + dp[i-2]` (ways to reach step i), with **base cases
`dp[0]=1, dp[1]=1`**. (Note the off-by-one vs Fibonacci, where `dp[0]=0` — Climbing
Stairs counts the empty way as 1.) House robber, decode ways, and tiling all share
this "depends on the last one or two states" shape.

### House Robber — `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`

![House robber 1D DP: dp[i] = max(skip = dp[i-1], rob = dp[i-2]+nums[i]); answer = dp[last].](images/105_dp_1d.png)

At each house: **skip it** (carry `dp[i-1]`) or **rob it** (`dp[i-2] + nums[i]`,
can't rob adjacent). `nums=[2,7,9,3,1]` → `dp=[2,7,11,11,12]` → **12**. O(n)/O(1).

- **House Robber II (LC 213):** houses in a **circle**. Since house 0 and house
  n−1 are now adjacent, any valid plan must **exclude at least one of them** →
  answer = `max( rob(nums[0..n-2]), rob(nums[1..n-1]) )` (run the line-DP twice).

### Coin Change — fewest coins for an amount

```text
# Coin Change (min coins)                     Time O(amount * #coins)
dp[0] = 0; dp[x] = infinity for x>0
for x in 1..amount:
    for coin in coins:
        if coin <= x: dp[x] = min(dp[x], dp[x-coin] + 1)
return dp[amount] (or -1 if still infinity)
```

> **Note:** this is the DP that fixes the greedy failure from Module 11 (coins
> {1,3,4} → 6). DP tries *all* coins per amount, so it's always optimal.

### Coin Change II — COUNT ways (the loop-order gotcha)

A *different* problem: count the **number of combinations** that make the amount
(unlimited coins).

```text
# Coin Change II (count combinations)         Time O(amount * #coins)
dp[0] = 1                                       # one way to make 0: take nothing
for coin in coins:              # <-- coins OUTER loop
    for x in coin..amount:      # <-- amount inner
        dp[x] += dp[x - coin]
return dp[amount]
```

> **Critical gotcha:** the **coin loop must be the OUTER loop** to count
> *combinations*. If you loop amount-outer/coin-inner you count **permutations**
> (e.g. 1+2 and 2+1 separately) — the classic wrong answer. Contrast: the
> *min-coins* version (above) works with either order because `min` doesn't
> double-count.

### Decode Ways & Word Break (1D over a string)

```text
# Decode Ways (LC 91): s of digits -> #ways to decode (A=1..Z=26)
dp[0] = 1
dp[i] += dp[i-1]   if s[i-1] != '0'                 # single digit 1..9
dp[i] += dp[i-2]   if "10" <= s[i-2..i-1] <= "26"   # valid two-digit
# zero-handling is the whole difficulty: '0' alone is invalid; '30' invalid; '10','20' ok

# Word Break (LC 139): dp[i] = can the prefix of length i be segmented?
dp[0] = true
dp[i] = OR over j<i of ( dp[j] AND s[j..i-1] in dictionary )
```

### Maximum Product Subarray (track two states)

Negatives flip sign, so track **both** the max and min product ending here:
`maxP = max(x, x*prevMax, x*prevMin)`, `minP = min(...)`. (Kadane's multiplicative
cousin — Module 2.)

### Longest Increasing Subsequence (LIS) — the #1 1D DP

The longest strictly-increasing (not necessarily contiguous) subsequence.

```text
# O(n^2)                                       answer = max(dp)
dp[i] = 1 + max(dp[j] for all j < i with nums[j] < nums[i], else 0)
```

There is also an **O(n log n)** method (a "tails" array + binary search). Full
treatment, variants (Number of LIS, Russian Doll), and the n log n code are in
**Module 14b §14b.1** — but every reader of 14a should know the O(n²) recurrence
above, since LIS is the most common 1D DP interview question.

### MCQs

1. House Robber recurrence? → `dp[i]=max(dp[i-1], dp[i-2]+nums[i])`.
2. Coin Change (min coins) complexity? → **O(amount × #coins)**.
3. Max Product Subarray tracks? → **both max and min** (negatives flip sign).

### Problems

- Climbing Stairs (70); House Robber I/II (198/213); Coin Change (322); Coin
  Change II (518 — count ways); Decode Ways (91); Word Break (139); Maximum
  Product Subarray (152); Min Cost Climbing Stairs (746).

---

## 14a.4 2D / Grid DP

### Unique Paths — `dp[i][j] = dp[i-1][j] + dp[i][j-1]`

![Unique Paths grid DP: each cell = ways to reach it = from above + from left; bottom-right = 10.](images/106_grid_dp.png)

Move only **right/down**; each cell's count = from above + from left. Closed form
= `C(m+n−2, n−1)`. **Min Path Sum (LC 64):** `dp[i][j] = grid[i][j] + min(up,
left)`. **Unique Paths II (LC 63):** obstacles set those cells to 0.

### Edit Distance (Levenshtein) — the 2D classic

![Edit Distance DP table for 'horse' → 'ros' = 3; equal chars copy the diagonal, else 1 + min(insert, delete, replace).](images/107_edit_distance.png)

```text
# Edit Distance                               Time O(m*n), Space O(m*n) -> O(min)
dp[i][j] = edits to turn first i chars of A into first j chars of B
base: dp[i][0]=i (delete all), dp[0][j]=j (insert all)
if A[i-1]==B[j-1]: dp[i][j] = dp[i-1][j-1]               # match, no cost
else: dp[i][j] = 1 + min(dp[i][j-1],    # insert
                         dp[i-1][j],    # delete
                         dp[i-1][j-1])  # replace
```

`"horse" → "ros"` = **3** edits: replace **h→r**, delete **r** (2nd char of
"horse"), delete **e** → leaves "ros". (Trace it through the table; bottom-right =
3.)

### Matrix Chain Multiplication (the #1 GATE interval DP)

Given matrices `A₁…Aₙ` with dimension array `p[0..n]` (so `Aᵢ` is `p[i-1] × p[i]`),
parenthesise to **minimise scalar multiplications**.

```text
# Matrix Chain Multiplication                 Time O(n^3), Space O(n^2)
m[i][i] = 0
m[i][j] = min over k in i..j-1 of:
          m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j]     # cost of the last multiply
# fill diagonal by diagonal (by chain length L = 2..n)
```

**Worked example.** Dimensions `p = [10, 20, 30]` (two matrices A₁=10×20,
A₂=20×30): only one way → `10·20·30 = 6000` multiplications. For three matrices
`p=[10,20,30,40]`: compare `(A₁A₂)A₃` and `A₁(A₂A₃)` and take the min — this is
exactly what `m[1][3]` computes. The `s[i][j]` table records the best split `k` to
**reconstruct the parenthesisation**. (More interval DP in M14c.)

### Other 2D / grid DP patterns (distinct recurrences)

- **Maximal Square (LC 221):** `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1],
  dp[i-1][j-1])` when `grid[i][j]==1` → largest all-1 square. *(min of three
  neighbours, not up+left.)*
- **Dungeon Game (LC 174):** solved **in reverse** (bottom-right → top-left):
  `dp[i][j] = max(1, min(dp[i+1][j], dp[i][j+1]) − grid[i][j])`. The reverse
  direction is the whole insight.
- **LCS / Distinct Subsequences / Interleaving String** — `dp[i][j]` over two
  strings (full LCS in M14b).

### Space optimisation (the standard follow-up)

Most 2D grid/string DPs only read the **previous row** (and current row), so you
can drop from `O(m·n)` to **`O(min(m, n))`** by keeping one or two rows. This is a
classic "can you do better on space?" interview ask.

### MCQs

1. Unique Paths recurrence & closed form? → `dp[i-1][j]+dp[i][j-1]`; `C(m+n−2,
   n−1)`.
2. Edit Distance equal-char transition? → copy the **diagonal** `dp[i-1][j-1]`.
3. 2D DP space optimisation? → keep only the **previous row** → O(min(m,n)).

### Problems

- Unique Paths I/II (62/63); Minimum Path Sum (64); Edit Distance (72); Longest
  Common Subsequence (1143); Maximal Square (221); Dungeon Game (174); Matrix
  Chain Multiplication (classic).

---

## Module 14a — Concept Review (one page)

- **DP** needs **optimal substructure + overlapping subproblems**; otherwise use
  D&C/greedy.
- **5 steps:** define state → recurrence → base+order → memoize/tabulate →
  optimise space.
- **Top-down (memo)** = recursion + cache; **bottom-up (tab)** = iterative table;
  same time.
- **Fibonacci ladder:** exponential → O(n) → **O(1) space** (rolling vars) — the
  1D template.
- **1D:** House Robber `max(skip, rob)`; Coin Change `min(dp[x-coin]+1)`; Max
  Product tracks max & min.
- **2D:** Unique Paths `up+left`; Edit Distance `diag` or `1+min(3)`; space →
  O(min(m,n)).

## Module 14a — Flash Cards

- Q: DP requirements? **A: optimal substructure + overlapping subproblems.**
- Q: Memo vs tab time? **A: same; style differs.**
- Q: Fibonacci optimal space? **A: O(1) (two rolling variables).**
- Q: House Robber recurrence? **A: max(dp[i-1], dp[i-2]+nums[i]).**
- Q: Coin Change time? **A: O(amount × #coins).**
- Q: Edit Distance match transition? **A: copy diagonal dp[i-1][j-1].**
- Q: 2D DP space cut? **A: keep last row → O(min(m,n)).**

## Module 14a — Pattern Recognition

- "Count ways / min cost over a 1D sequence, depends on last few" → **1D DP**.
- "Fewest/most to reach a target amount" → **coin-change style DP**.
- "Two strings → similarity/transform" → **2D DP** (edit distance / LCS).
- "Grid, move right/down, count/min" → **grid DP** (`up + left`).
- "Greedy gave a wrong answer" → **fall back to DP** (it tries all choices).

## Module 14a — Interview Questions (with follow-ups)

1. *Climbing stairs / house robber.* FU: *O(1) space; circular variant.*
2. *Coin change.* FU: *count ways vs fewest coins; why not greedy?*
3. *Edit distance.* FU: *recover the actual edit operations; O(min) space.*
4. *Unique paths.* FU: *with obstacles; closed-form combinatorics.*
5. *"Solve it top-down, then convert to bottom-up."* (common Google ask.)

## Module 14a — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** filling a DP table by hand (edit distance, matrix chain,
  coin change), stating the recurrence, **matrix chain multiplication** order &
  cost, identifying optimal substructure, and memo-vs-tab trade-offs. Frequently
  tested numerically.

---

*End of Module 14a. Next: Module 14b — Sequence DP (LIS, LCS) & Knapsack family —
with visuals.*
