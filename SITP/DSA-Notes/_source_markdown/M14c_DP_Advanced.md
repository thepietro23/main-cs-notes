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

![Re-rooting DP: pass 1 (post-order) computes each subtree's answer, pass 2 (pre-order) pushes the parent's contribution down, giving every node a whole-tree answer in O(n).](images/250_reroot_dp.png)

**Why two passes (intuition).** A single DFS gives each node the answer looking
*only into its own subtree* — it cannot see the part of the tree that sits *above*
it. Re-rooting fixes this: pass 2 hands each child the "everything above me" piece
that its parent already knows, so every node ends up with a **whole-tree** answer
without re-running DFS from all `n` roots (that naive way is O(n²)).

**Worked idea — Sum of Distances in Tree.** Let `answer[root]` be found in pass 1.
When we move the root from a node `u` to its child `v`, every node **inside v's
subtree gets 1 step closer** and every node **outside it gets 1 step farther**:

```text
 answer[v] = answer[u] - size[v] + (N - size[v])
             \_________/  \______/   \_________/
              parent's    v's subtree  the rest of the tree
              total       moved closer moved farther
```

That single O(1) update per edge, pushed down in a pre-order pass, gives **every**
node's answer in total **O(n)**.

> **Trigger:** "compute an answer *for every node as if it were the root*" → think
> re-rooting (down-pass + up-pass), not `n` separate DFS runs.

> **Memory hook:** "**ask the children, then decide**" — the postorder mantra from
> Module 8a, now carrying richer state.

### MCQs

1. Tree DP traversal order? → **post-order** (children first).
2. House Robber III state? → `(rob this node, skip this node)`.
3. Tree DP time? → **O(n)** (one DFS).
4. "Answer for every node as root" without O(n²)? → **re-rooting** (down + up pass).

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

**Worked trace — TSP for 4 cities `{0,1,2,3}`.** The mask counts up in binary; a bit
set means that city is visited. `dp[mask][i]` = cheapest path from 0 covering exactly
`mask`, ending at `i`. Distance matrix (symmetric):

```text
      to: 0   1   2   3
 from 0:  -  10  15  20
 from 1: 10   -  35  25
 from 2: 15  35   -  30
 from 3: 20  25  30   -

 mask=0001 (just 0):  dp[0001][0] = 0                       (start)
 mask=0011 (0,1):     dp[..][1] = dp[0001][0]+d(0,1) = 10
 mask=0101 (0,2):     dp[..][2] = 0 + d(0,2)         = 15
 mask=1001 (0,3):     dp[..][3] = 0 + d(0,3)         = 20
 mask=0111 (0,1,2):   dp[..][2] = dp[0011][1]+d(1,2) = 10+35 = 45
                      dp[..][1] = dp[0101][2]+d(2,1) = 15+35 = 50
 ... (fill all masks by ASCENDING order) ...
 full = 1111: close the tour -> min over last city i of dp[1111][i] + d(i,0)
 best closed tour cost here = 80  (route 0->1->3->2->0)
```

Key point: masks are processed **in increasing numeric order**, which guarantees
every submask is finished before the supermask that needs it.

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
4. Why iterate masks in ascending order? → so every **submask is filled before** its
   supermask (dependencies ready).

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

**Worked table — Matrix Chain, `p = [40, 20, 30, 10, 30]`** (4 matrices
A₁=40×20, A₂=20×30, A₃=30×10, A₄=10×30). Fill `dp[i][j]` by chain length; `dp[i][i]=0`:

```text
 Length-2 (single products):
   dp[1][2] = 40*20*30 = 24000
   dp[2][3] = 20*30*10 =  6000
   dp[3][4] = 30*10*30 =  9000

 Length-3 (try each split k):
   dp[1][3] = min( k=1: 0+6000 +40*20*10=8000  -> 14000,
                   k=2: 24000+0 +40*30*10=12000 -> 36000 ) = 14000  (k=1)
   dp[2][4] = min( k=2: 0+9000 +20*30*30=18000 -> 27000,
                   k=3: 6000+0 +20*10*30= 6000  -> 12000 ) = 12000  (k=3)

 Length-4 (the answer, dp[1][4]):
   k=1: dp[1][1]+dp[2][4] + 40*20*30 = 0+12000+24000 = 36000
   k=2: dp[1][2]+dp[3][4] + 40*30*30 = 24000+9000+36000 = 69000
   k=3: dp[1][3]+dp[4][4] + 40*10*30 = 14000+0+12000 = 26000  <- MIN
   dp[1][4] = 26000  (best split at k=3)
```

So the cheapest order is **`(A₁A₂A₃)·A₄`** at **26000** multiplications. The `s`
table would store `s[1][4]=3`, `s[1][3]=1` to reconstruct the full parenthesisation
`((A₁A₂)A₃)A₄`.

- **Other interval DP:** Min Cost to Cut a Stick (1547), Palindrome Partitioning
  II (132), Optimal BST.

> **Memory hook:** parenthesisation problems — "which split / which last
> operation?" over a range.

### MCQs

1. Interval DP fill order? → by **increasing interval length**.
2. Burst Balloons trick? → treat `k` as the **last** balloon burst.
3. Interval DP typical time? → **O(n³)**.
4. Matrix chain for `p=[40,20,30,10,30]` min cost? → **26000** (split `(A₁A₂A₃)A₄`).

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

**Worked mini-example — count integers in `[0, 21]` whose digits are all even.**
Write `N = 21` as digits `[2, 1]`. Walk position 0 (tens) then position 1 (units):

```text
 pos 0, tight, digits allowed 0..2, but must be even -> {0, 2}
   pick 0 (now NOT tight): pos 1 can be any even digit {0,2,4,6,8} -> 5 numbers
                           (these are 00,02,04,06,08 i.e. 0,2,4,6,8)
   pick 2 (STILL tight, since 2 == N[0]): pos 1 limited to 0..N[1]=1, even -> {0}
                           -> 1 number (that is 20)
 total = 5 + 1 = 6   -> {0, 2, 4, 6, 8, 20}
```

The moment we pick a digit *below* the tight limit, `tight` turns off and the rest
of the positions are unconstrained (0..9) — that is exactly what the skeleton's
`tight and d==limit` expresses.

### MCQs

1. Digit DP counts numbers up to N with a? → **digit property**.
2. The crucial state flag? → **tight** (still bounded by N's prefix).
3. `[L,R]` answer? → **count(R) − count(L−1)**.
4. When does `tight` turn off? → the moment you pick a digit **below** the limit.

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

**When to reach for each (recognition cheatsheet):**

- **Rolling array** — the transition reads only the last 1–2 rows/values. *Always*
  the first optimisation to try; safe and simple.
- **Monotonic deque** — the inner `min`/`max` is over a **sliding window** of
  previous states (e.g. `dp[i] = min(dp[j]) + cost` for `j` in `[i-k, i-1]`). The
  deque keeps window extremes in amortised O(1).
- **Divide & Conquer optimisation** — `dp[i][j] = min_k(dp[i-1][k] + C(k,j))` and
  the **optimal `k` is monotonic** in `j` (`opt(i,j) ≤ opt(i,j+1)`). Recurse on the
  split range → O(n log n) per layer.
- **Knuth optimisation** — interval DP `dp[i][j] = min_k(dp[i][k]+dp[k+1][j]) +
  w(i,j)` where `w` satisfies the **quadrangle inequality**; then optimal splits are
  monotonic and the k-loop collapses → **O(n²)** (Optimal BST is the classic case).
- **Convex Hull Trick** — the transition is a **minimum over lines** `mⱼ·x + bⱼ`
  evaluated at a query `x`; maintain the lower/upper hull of lines.

> **Golden rule:** first get a **correct** DP, *then* optimise. Knuth / D&C-opt /
> CHT are **ICPC-level** — recognise the transition shape (interval with QI; cost
> = line `mx+b`) rather than memorising the math.

### MCQs

1. First priority before optimising DP? → get a **correct** recurrence.
2. Transitions `min(m·x + b)` → use? → **Convex Hull Trick**.
3. Interval DP with quadrangle inequality → ? → **Knuth optimisation** (O(n²)).
4. `min` over a sliding window of previous states → ? → **monotonic deque** (O(n)).
5. Optimal split monotonic in `j` → ? → **divide & conquer optimisation**.

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
- Q: Answer for every node as root in O(n)? **A: re-rooting (down + up pass).**
- Q: Sliding-window min in a DP transition? **A: monotonic deque (O(n)).**

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
