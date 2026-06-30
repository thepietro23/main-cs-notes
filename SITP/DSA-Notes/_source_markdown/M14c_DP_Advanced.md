---
title: "Module 14c — Dynamic Programming: Advanced"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14c — Advanced DP (Tree, Bitmask, Digit, Interval, Optimisations)

> **Why this part.**
> Once you can define a state and a transition (M14a/b), the "advanced" DP topics
> are mostly about **what the state is**: a *subtree* (tree DP), a *subset of bits*
> (bitmask DP), a *position in a number* (digit DP), or a *range* (interval DP).
> The final piece — **DP optimisations** — speeds up a correct-but-slow recurrence.
> These are **P2** (hard interviews + ICPC + GATE algorithm-design), so focus on
> recognising the state shape and the headline complexity.

> **How to read each technique.** The state, the recurrence, the complexity, and
> when to reach for it.

---

## 14c.1 Tree DP (state = a subtree)

### The idea

Run a **post-order DFS**: each node computes its answer from its **children's**
answers. The state is usually `(node, small extra flag)`.

![Tree DP: each node returns answers for its subtree; House Robber III returns (rob-this, skip-this).](images/113_tree_dp.png)

```text
# House Robber III (LC 337) — can't rob a node and its child
solve(node) returns (withNode, skipNode):
    if node is null: return (0, 0)
    L = solve(node.left); R = solve(node.right)
    withNode = node.val + L.skip + R.skip
    skipNode = max(L.with, L.skip) + max(R.with, R.skip)
    return (withNode, skipNode)
answer = max(solve(root))
```

- One DFS pass → **O(n)**. Returning the **pair** `(with, skip)` is the trick:
  the naive single-value `rob(node)` re-queries grandchildren (overlapping
  subproblems → needs a memo map); the pair eliminates that entirely → pure O(n),
  no memo.
- **Other tree DP:** Diameter / Max Path Sum (Module 8a), Binary Tree Cameras
  (968), Distribute Coins (979), counting subtrees.

### Re-rooting (two-pass) — an answer for EVERY node as root, in O(n)

```text
# Re-rooting DP (e.g. Sum of Distances in Tree, LC 834)      O(n) total
pass 1 (post-order): down[v] = answer within v's subtree (+ subtree sizes)
pass 2 (pre-order from root): up[v] derived from the parent's total minus v's
        own contribution -> answer[v] = down[v] combined with up[v]
```

Pass 1 gathers subtree info bottom-up; pass 2 pushes the parent's contribution
down to "re-root" at each child. Examples: Sum of Distances in Tree (834),
tree-centroid / min-height framing (310).

> **Memory hook:** "**ask the children, then decide**" — the postorder mantra from
> Module 8a, now carrying richer state.

### MCQs

1. Tree DP traversal order? → **post-order** (children first).
2. House Robber III state? → `(rob this node, skip this node)`.
3. Tree DP time? → **O(n)** (one DFS).

---

## 14c.2 Bitmask DP (state = a subset)

### The idea

When `n` is **small (≤ ~20)** and the state is "**which subset** is done", encode
the subset as the bits of an integer `mask`.

![Bitmask DP: a subset is the bits of an integer; dp[mask][i] = best having visited 'mask', now at i.](images/114_bitmask_dp.png)

```text
# Travelling Salesman (Held-Karp)             Time O(2^n * n^2), Space O(2^n * n)
dp[mask][i] = min cost to start at 0, visit exactly the set 'mask', end at city i
base: dp[1][0] = 0 (only city 0 visited), everything else = infinity
iterate masks in ASCENDING order (so every submask is filled before its supermask):
    dp[mask | (1<<j)][j] = min(..., dp[mask][i] + dist[i][j])   # i in mask, j not
closed tour: answer = min over i of dp[full][i] + dist[i][0]   # open path: drop the +dist[i][0]
# (keep a parent[] to reconstruct the actual tour)
```

- **TSP** drops from O(n!) brute force to **O(2ⁿ·n²)** — feasible to n ≈ 18–20.

### Partition into k equal subsets (LC 698) — the single-dimension mask trick

```text
# precheck: target = sum/k must be integer AND max(nums) <= target
dp[mask] = remaining capacity in the CURRENT bucket after placing items in 'mask'
dp[0] = target
for each mask, for each j not in mask with nums[j] <= dp[mask]:
    dp[mask | (1<<j)] = (dp[mask] - nums[j]) % target    # hitting 0 rolls to a fresh bucket
answer: dp[full] == 0      # Time O(2^n * n)
```

- **Submask enumeration idiom** (for "assign each element to one of several
  precomputed valid groups", LC 1986/2305): `for (sub = mask; sub; sub = (sub-1) &
  mask)` iterates all submasks of `mask` in **O(3ⁿ)** total.
- **Other bitmask DP:** assignment (workers↔jobs), counting Hamiltonian paths,
  Shortest Superstring (943).

> **Trigger:** small `n` + "subset of things already chosen/used" → think bitmask.

### MCQs

1. Bitmask DP applies when n is? → **small (≤ ~20)**.
2. TSP via bitmask DP time? → **O(2ⁿ·n²)**.
3. `mask | (1<<j)` does? → adds element **j** to the set.

---

## 14c.3 Interval DP (state = a range [i, j])

### The idea

`dp[i][j]` = the best answer for the sub-range `i..j`. Fill by **increasing
interval length**. The key trick: pick the **last** thing to handle in `(i, j)` so
the two sides become **independent**.

![Interval DP: dp[i][j] over a range; choose the LAST item to handle so both sides are independent.](images/115_interval_dp.png)

```text
# Burst Balloons (LC 312)                     Time O(n^3)
# PAD nums with a virtual 1 at each end; (i,j) is an OPEN interval (boundaries survive)
dp[i][j] = max coins from bursting all balloons strictly inside (i, j)
dp[i][i+1] = 0                                # nothing between adjacent boundaries
dp[i][j] = max over k in (i,j) of:
           dp[i][k] + dp[k][j] + nums[i]*nums[k]*nums[j]   # k = LAST burst inside
```

- **Pick the last move, not the first** — that keeps the two sides independent.
  The **virtual 1s** at both ends make `nums[i]`/`nums[j]` valid boundaries after
  everything inside is burst.

### Two interval-DP cost shapes (don't confuse them)

| Cost added at the split | Example |
|---|---|
| **multiply boundary/last** `nums[i]·nums[k]·nums[j]` | Burst Balloons |
| **add the range sum** `prefixSum(i, j)` at each merge | Merge Stones (1000), Stone Game |
| **`p[i-1]·p[k]·p[j]`** (matrix dims) | Matrix Chain Mult. (M14a) |

**Matrix Chain recurrence (GATE-critical, restated here):** `dp[i][j] = min over k
of dp[i][k] + dp[k+1][j] + p[i-1]·p[k]·p[j]`, base `dp[i][i]=0`, fill by increasing
chain length → **O(n³)** time, **O(n²)** space (worked numeric example in M14a).

- **Other interval DP:** Min Cost to Cut a Stick (1547), Palindrome Partitioning
  II (132), Optimal BST.

> **Memory hook:** parenthesisation problems — "which split / which last
> operation?" over a range.

### MCQs

1. Interval DP fill order? → by **increasing interval length**.
2. Burst Balloons trick? → treat `k` as the **last** balloon burst.
3. Interval DP typical time? → **O(n³)**.

---

## 14c.4 Digit DP (state = position in a number)

### The idea

Count numbers in `[0, N]` (or `[L, R]`) with some digit property (e.g. "no two
equal adjacent digits", "digit sum = s"). Build the number digit by digit; the
state tracks **(position, tight, extra)** where **tight** = "are we still on the
prefix of N?".

```text
# Digit DP skeleton                           Time O(digits * states * 10)
count(pos, tight, extra):
    if pos == len(N): return 1 if extra is valid else 0
    limit = N[pos] if tight else 9
    total = 0
    for d in 0..limit:
        total += count(pos+1, tight and d==limit, update(extra, d))
    return total
# answer for [L,R] = count(R) - count(L-1)
```

- **`tight`** is the heart: while tight, you can't exceed N's digit at this
  position. Memoise on `(pos, tight, extra)`.
- **Examples:** count numbers with digit-sum k, numbers without consecutive 1s,
  "Numbers At Most N Given Digit Set" (902), Count Numbers with Unique Digits.

### MCQs

1. Digit DP counts numbers up to N with a? → **digit property**.
2. The crucial state flag? → **tight** (still bounded by N's prefix).
3. `[L,R]` answer? → **count(R) − count(L−1)**.

---

## 14c.5 DP Optimisations (speed up a correct DP)

![DP optimisations: rolling space, bitmask, Knuth/D&C-opt, convex hull trick, monotonic deque — and the from→to speedups.](images/116_dp_optimizations.png)

| Technique | Idea | Speedup |
|---|---|---|
| **Rolling array** | keep only last 1–2 rows | O(n·m) → O(m) space |
| **Monotonic deque** | sliding-window min/max in the transition | O(n·k) → O(n) |
| **Knuth optimisation** | for interval DP with the quadrangle inequality | O(n³) → O(n²) |
| **Divide & Conquer opt** | when the optimal split is monotonic | O(n²) → O(n log n) |
| **Convex Hull Trick (CHT)** | transitions of the form `min(m·x + b)` (lines) | O(n²) → O(n log n)/O(n) |

> **Golden rule:** first get a **correct** DP, *then* optimise. Knuth / D&C-opt /
> CHT are **ICPC-level** — recognise the transition shape (interval with QI; cost
> = line `mx+b`) rather than memorising the math.

### MCQs

1. First priority before optimising DP? → get a **correct** recurrence.
2. Transitions `min(m·x + b)` → use? → **Convex Hull Trick**.
3. Interval DP with quadrangle inequality → ? → **Knuth optimisation** (O(n²)).

---

## Module 14c — Concept Review (one page)

- **Tree DP:** post-order DFS, state `(node, flag)`; O(n); House Robber III, max
  path sum, re-rooting.
- **Bitmask DP:** subset = integer bits; small n (≤20); **TSP O(2ⁿ·n²)**,
  assignment, partition-to-k.
- **Interval DP:** `dp[i][j]` by increasing length; pick the **last** move; Burst
  Balloons / Matrix Chain O(n³).
- **Digit DP:** state `(pos, tight, extra)`; count numbers ≤ N with a digit
  property; `[L,R] = f(R)−f(L−1)`.
- **Optimisations:** rolling space, monotonic deque, Knuth/D&C-opt, CHT — get
  correct first, then speed up.

## Module 14c — Flash Cards

- Q: Tree DP order & time? **A: post-order DFS, O(n).**
- Q: When bitmask DP? **A: small n (≤20), state = subset.**
- Q: TSP DP complexity? **A: O(2ⁿ·n²) (Held-Karp).**
- Q: Interval DP key trick? **A: choose the LAST operation in the range.**
- Q: Digit DP key flag? **A: tight (bounded by N's prefix).**
- Q: Transition min(mx+b) optimisation? **A: Convex Hull Trick.**

## Module 14c — Pattern Recognition

- "Answer over a tree / subtree, choices per node" → **tree DP**.
- "Small n, 'which subset is used/visited'" → **bitmask DP** (TSP/assignment).
- "Best over a range / parenthesisation / merge cost" → **interval DP**.
- "Count numbers with a digit property up to N" → **digit DP**.
- "Correct DP too slow (O(n²)/O(n³))" → **CHT / Knuth / D&C-opt / deque**.

## Module 14c — Interview Questions (with follow-ups)

1. *House Robber III.* FU: *why return a pair; why post-order.*
2. *TSP for n≤15.* FU: *bitmask DP; why O(2ⁿ·n²) beats n!.*
3. *Burst Balloons.* FU: *why "last burst" makes sides independent.*
4. *Count numbers ≤ N with no consecutive equal digits.* FU: *digit DP `tight`.*

## Module 14c — GATE / SEBI / RBI / ISRO Perspective

- **GATE:** TSP via DP complexity **O(2ⁿ·n²)**, interval DP (matrix chain — also
  M14a), tree DP concepts. **Bitmask/digit DP** and CHT/Knuth are more ICPC than
  GATE; prioritise M14a/M14b for exams and treat M14c as "recognise the state
  shape".

---

*End of Module 14 (DP complete: a + b + c). Next: Module 15 — Bit Manipulation
(XOR tricks, bitmasking, subsets, Gray code) — with visuals.*
