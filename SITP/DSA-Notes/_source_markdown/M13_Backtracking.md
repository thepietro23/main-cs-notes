---
title: "Module 13 — Backtracking"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 13 — Backtracking

> **Why backtracking.**
> Some problems ask for **all** solutions, or a valid arrangement, where you must
> **try a choice, explore its consequences, and undo it if it fails**. That is
> backtracking: a smart **DFS over a "state-space tree"** that **prunes** dead
> branches early. One "choose → explore → un-choose" skeleton solves subsets,
> permutations, N-Queens, Sudoku, word search, graph coloring, and more.

This module is **P0** for interviews (one template, many problems) and appears in
GATE as state-space / branch-and-bound questions.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

---

## 13.1 The Backtracking Framework

### The idea

Build a solution incrementally. At each step **choose** an option, **recurse** to
extend the partial solution, then **un-choose** (undo) to try the next. If a
partial solution can't possibly lead to a valid answer, **prune** that branch.

![Backtracking is a DFS over a state-space tree; pruned branches (X) can't lead to a solution.](images/100_backtracking_tree.png)

### The universal template

![The backtracking template: if complete record it; else for each valid choice, choose → recurse → undo.](images/103_fc_backtracking.png)

```text
# Backtracking skeleton
backtrack(state):
    if state is a complete solution:
        record a COPY of it; return        # COPY! path is mutated on the way back
    for each choice in options(state):
        if choice is valid (PRUNE here):
            make the choice              # choose
            backtrack(new state)         # explore
            undo the choice              # un-choose (backtrack)
```

> **Live-coding bug #1:** "record it" means **append a *copy/snapshot*** of the
> path. Recording the path *by reference* yields all-empty or all-identical
> results because it keeps getting mutated.

> **Memory hook:** exploring a **maze with breadcrumbs** — walk a path; if it's a
> dead end, walk back (pick up the breadcrumb) and try another. Picking up the
> breadcrumb is the *undo*.

### Worked dry-run — Subsets of [1, 2]

Watch `path` grow and shrink (● = record a snapshot):

| Depth | Action | path |
|---|---|---|
| 0 | start, record ● | `[]` |
| 1 | add 1, record ● | `[1]` |
| 2 | add 2, record ● | `[1,2]` |
| 2 | undo 2 | `[1]` |
| 1 | undo 1 | `[]` |
| 1 | add 2, record ● | `[2]` |
| 1 | undo 2 | `[]` |

Snapshots recorded: `[] , [1] , [1,2] , [2]` → the 4 = 2² subsets. The **undo** is
what lets the same `path` object visit every branch.

### Time vs space (a GATE distinction)

- **Time** = number of nodes in the state-space tree → **exponential** (2ⁿ
  subsets, n! permutations). Pruning shrinks this hugely in practice.
- **Auxiliary space** = **recursion depth** = number of decision stages = **O(n)**
  (n for subsets/permutations/N-Queens; #cells for Sudoku) — *not* exponential.
- **Node counts (exam):** the binary subset tree has `2^(n+1) − 1` total nodes
  (2ⁿ leaves); the permutation tree has `Σ_{k=0..n} n!/(n−k)!` nodes. "O(2ⁿ)" /
  "O(n!)" are **leaf** counts.

### How to reason about backtracking time — branching^depth

The skeleton makes the cost formula concrete. At every node you loop over the
choices (the **branching factor `b`**) and the tree is as deep as the number of
decisions (the **depth `d`**). So the tree has roughly **`b^d` nodes**, and total
time is `O(b^d × work per node)`.

```text
technique          branching b        depth d      => leaves
---------------------------------------------------------------
subsets            2 (in/out)         n            2^n
permutations       n, n-1, ... , 1    n            n!
combinations C(n,k) up to n           k            C(n,k)
N-Queens           N (columns)        N            <= N^N, but pruned to ~ small
m-coloring         m (colors)         V            m^V
```

Pruning does **not** change this worst-case bound, but it slashes the *practical*
node count: a branch cut at depth `j` removes an entire `b^(d−j)` subtree. That is
why N-Queens, whose naive bound is `N^N`, is solvable for `N=8` in microseconds —
the diagonal/column checks prune almost everything early.

> **Memory hook:** backtracking time = **(choices per step) ^ (number of steps)**;
> pruning removes whole subtrees but not the worst-case exponent.

### Backtracking vs Branch-and-Bound vs DP

| | Backtracking | Branch & Bound | DP |
|---|---|---|---|
| Purpose | enumerate / feasibility | **optimisation** (min/max) | optimisation with overlap |
| Prunes by | constraint violation | **optimistic bound vs best-so-far** | reuses subproblems (memo/table) |
| Typical cost | exponential | exponential (less w/ bounds) | polynomial |

### MCQs

1. The three backtracking actions? → **choose, explore, un-choose**.
2. Backtracking recursion depth (subsets/perms)? → **O(n)** (not exponential).
3. Subset tree total nodes? → **2^(n+1) − 1** (2ⁿ leaves).
4. Backtracking worst-case time in one phrase? → **branching^depth** (b^d nodes ×
   work/node).
5. Does pruning change the worst-case exponent? → **no** (it only cuts practical
   node count, removing whole `b^(d−j)` subtrees).

---

## 13.2 Subsets, Permutations, Combinations

### The single most important decision: what to pass to recursion

| Pass to recursion | Effect | Use for |
|---|---|---|
| **`i + 1`** | each element used once, **order doesn't matter** | subsets, combinations |
| **`i`** | element **reusable** | combination sum (with reuse) |
| **`used[]`, loop from 0** | revisit earlier indices, **order matters** | permutations |

> **The hinge of the whole topic:** a **`start` index** prevents reorderings
> (combinations/subsets); a **`used[]` array** (or in-place swap) allows revisiting
> earlier elements but forbids reusing the same index (permutations). Confusing
> them gives O(n!) when you wanted O(2ⁿ), or duplicate combinations.

### Subsets vs combinations vs permutations — a 2-question decision

Two yes/no questions pick the right structure every time:

```text
Q1: does ORDER matter? (is [1,2] different from [2,1]?)
      YES  -> PERMUTATION  (used[] array, loop from 0)
      NO   -> go to Q2

Q2: is the SIZE fixed to exactly k?
      YES  -> COMBINATION  (start index, record only when size == k)
      NO   -> SUBSET       (start index, record at EVERY node, all sizes)
```

- **Subsets** = all combinations of *every* size (`C(n,0)+…+C(n,n) = 2ⁿ`).
- **Combinations** = subsets of one fixed size `k` (`C(n,k)`).
- **Permutations** = arrangements where order counts (`n!`, or `n!/(n−k)!` for
  length `k`).

> **Memory hook:** **order? → permutation. Fixed size? → combination. Neither? →
> subset.**

![Subsets of [1,2]: at each element choose include/exclude; permutations pick an unused element each step.](images/101_subsets_perms.png)

### Subsets — O(2ⁿ) (n=4 → 16 subsets)

```text
backtrack(start, path):
    record a copy of path                    # every node is a subset
    for i in start..n-1:
        path.add(a[i]); backtrack(i+1, path); path.removeLast()
```

### Subsets II / Combination Sum II — dedup (the error-prone line)

```text
# Sort first, then skip equal SIBLINGS at the same tree level
sort(a)
backtrack(start, path):
    record a copy of path
    for i in start..n-1:
        if i > start and a[i] == a[i-1]: continue   # <-- i > start, NOT i > 0
        path.add(a[i]); backtrack(i+1, path); path.removeLast()
```

> **Critical:** the guard is **`i > start`** (skip duplicates that are *siblings*
> at this level), **not** `i > 0` (which would wrongly drop valid duplicates that
> legitimately appear deeper in the tree).

### Permutations — O(n!) (n=4 → 24); and the *different* dedup

```text
# Permutations
backtrack(path, used):
    if path.size == n: record a copy; return
    for i in 0..n-1:
        if used[i]: continue
        # Permutations II dedup (DIFFERENT condition!):
        if i > 0 and a[i] == a[i-1] and not used[i-1]: continue
        used[i]=true; path.add(a[i]); backtrack(path,used); path.removeLast(); used[i]=false
```

> **Permutations dedup ≠ subsets dedup.** Here it is `i>0 and a[i]==a[i-1] and
> not used[i-1]` — the `not used[i-1]` part is unique to permutations. Sort first.

### Combinations (n choose k) — with pruning

```text
backtrack(start, path):
    if path.size == k: record a copy; return
    for i in start..n-1:
        if k - path.size > n - i: break          # not enough left -> prune
        path.add(a[i]); backtrack(i+1, path); path.removeLast()
# C(5,2) = 10
```

### Iterative subsets via bitmask (no recursion)

For `n` elements, every integer `mask` in `0 .. 2ⁿ−1` encodes one subset: bit `j`
set ⇒ include `a[j]`.

```text
for mask in 0 .. (1<<n)-1:
    subset = [ a[j] for j in 0..n-1 if mask has bit j set ]
```

(Links to Module 15 Bit Manipulation.)

### MCQs

1. #subsets / #permutations of n=4? → **16 / 24**.
2. Subsets dedup guard? → **`i > start`** (not `i > 0`).
3. Permutations II dedup guard? → `i>0 and a[i]==a[i-1] and **not used[i-1]**`.
4. Combination Sum (reuse) recurses with? → **i** (not i+1).

### Problems

- Subsets (78); Subsets II (90); Permutations (46); Permutations II (47);
  Combinations (77); Combination Sum I/II (39/40); Letter Combinations of a Phone
  Number (17 — map each digit to letters, recurse by advancing the digit index).

---

## 13.3 Grid & Board Backtracking

### N-Queens — place N queens, none attacking

![N-Queens 4×4: place queens row by row, checking column and both diagonals; backtrack when stuck.](images/102_nqueens.png)

```text
# N-Queens                                   Time O(N!), far less with pruning
place(row):
    if row == N: record board; return
    for col in 0..N-1:
        if col, (row-col), (row+col) are all free:    # O(1) checks via 3 sets
            place queen; place(row+1); remove queen
```

- **O(1) safety check** with three hash sets: used **columns**, **diagonals
  (`row−col`)**, **anti-diagonals (`row+col`)**.

**Worked pruning trace — 4×4 (find the first solution).** Place one queen per row;
`✓` = try, `✗` = attacked (pruned before recursing):

```text
row 0: try col 0  -> place Q at (0,0)
  row 1: col 0 ✗(same column)  col 1 ✗(diagonal 0,0-1,1)  col 2 ✓ -> place (1,2)
    row 2: col 0 ✗(col)  col 1 ✗(anti-diag 1+2=3 = 2+1)  col 2 ✗(col)  col 3 ✗(diag) 
           -> NO valid column, DEAD END, backtrack
    remove (1,2); try col 3 ✓ -> place (1,3)
    row 2: col 0 ✗  col 1 ✓ -> place (2,1)
      row 3: col 0 ✗  col 1 ✗  col 2 ✗  col 3 ✗ -> DEAD END, backtrack
      remove (2,1); no more cols in row 2 -> backtrack
    remove (1,3); no more cols in row 1 -> backtrack
  remove (0,0)
row 0: try col 1 -> place (0,1)
  row 1: col 3 ✓ -> (1,3)
    row 2: col 0 ✓ -> (2,0)
      row 3: col 2 ✓ -> (3,2)   ALL 4 ROWS FILLED -> SOLUTION [1,3,0,2]
```

The whole `col 0` start subtree is abandoned after only a handful of node visits —
that is pruning doing the heavy lifting. The two solutions for `N=4` are
`[1,3,0,2]` and its mirror `[2,0,3,1]`.

**Solution counts (a GATE/ISRO favourite — memorise):**

| N | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| distinct solutions | 1 | **0** | **0** | **2** | 10 | 4 | 40 | **92** |

(N=2 and N=3 are **unsolvable**; the 4×4 board has exactly **2** solutions; the
classic 8×8 has **92**.)

### Sudoku Solver

Fill the first empty cell with a digit 1–9 that doesn't violate its row, column,
or 3×3 box; recurse; if stuck, undo and try the next digit. Use the **minimum-
remaining-values** heuristic (fill the most-constrained cell first) to speed it
up.

### Word Search (LC 79)

DFS from each cell matching the word char by char. **Order matters:** check
**bounds + char match FIRST**, then mark (overwrite the cell with a sentinel like
`#`), recurse to the 4 neighbours, then **restore the original character** (not a
generic unmark). **Word Search II (LC 212)** uses a **Trie** (Module 3) to search
many words at once.

### MCQs

1. N-Queens solutions for N=4 and N=8? → **2 and 92** (N=2,3 → 0).
2. N-Queens O(1) check uses? → **column + (row−col) + (row+col)** sets.
3. Word Search undo restores? → the **original character** (not a generic mark).

### Problems

- N-Queens (51/52); Sudoku Solver (37); Word Search (79); Word Search II (212);
  Rat in a Maze, Knight's Tour (classic).

---

## 13.4 Graph Backtracking (coloring, Hamiltonian)

### m-Coloring

Assign one of `m` colors to each vertex so no two **adjacent** vertices share a
color (the basis of map coloring, register allocation, exam scheduling).

```text
# m-coloring                                 Time O(m^V)
color(v):
    if v == V: record coloring; return true
    for c in 1..m:
        if no neighbour of v already has color c:
            assign c; if color(v+1): ...; unassign c    # backtrack
```

> N-Queens is a special coloring/constraint problem; m-coloring generalises the
> "no conflict" idea.

### Hamiltonian Path / Cycle

Build a path that visits **every vertex exactly once** (a **cycle** also returns
to the start). Extend the path to an unvisited adjacent vertex; **prune** when no
such vertex exists; for a cycle, require an edge back to the start.

```text
# Hamiltonian path/cycle                     Time O(N!)
extend(path):
    if path has all V vertices: (cycle? need edge back to start) record; return
    for next adjacent unvisited vertex w:
        add w; extend(path); remove w        # backtrack
```

(Hamiltonian cycle is **NP-complete** — Module 18 — hence the exponential search.)

### MCQs

1. m-coloring complexity? → **O(m^V)**.
2. Hamiltonian cycle is in which complexity class? → **NP-complete**.
3. N-Queens is a special case of? → **graph coloring / constraint satisfaction**.

---

## 13.5 String & Partition Backtracking

- **Generate Parentheses (LC 22):** place `(` if opens < n, `)` if closes < opens
  → only builds valid strings. Count = the **Catalan number** `Cₙ = C(2n,n)/(n+1)`
  → n=1:1, n=2:2, **n=3:5, n=4:14**.
- **Palindrome Partitioning (LC 131):** try each prefix; if palindrome, recurse on
  the rest (pre-compute palindrome DP to speed checks).
- **Restore IP Addresses (LC 93):** split into 4 valid octets (0–255, no leading
  zeros).
- **Word Break II (LC 140):** try each dictionary-word prefix; recurse on the
  rest; **memoise** to avoid recomputation.

### MCQs

1. Generate Parentheses for n=3 / n=4? → **5 / 14** (Catalan).
2. Palindrome partitioning recurses on? → the **remaining suffix**.

---

## 13.6 Branch & Bound (optimisation, GATE-heavy)

Backtracking finds *feasible / all* solutions; **Branch & Bound (B&B)** finds the
*optimal* one by pruning any branch whose **optimistic bound** can't beat the
**best found so far**.

### 0/1 Knapsack upper bound (for maximisation)

At a node, compute an **optimistic upper bound** by **fractionally** filling the
remaining capacity with the best value/weight items (the LP relaxation). If that
bound ≤ the best complete solution found, **prune** the node. *(Items 60/10,
100/20, 120/30, W=50: the fractional bound at the root = 60+100+ (2/3)·120 = 240;
any branch that can't reach the current best is cut.)*

### TSP lower bound (for minimisation)

Reduce the cost matrix (subtract each row's minimum, then each column's minimum);
the **sum of reductions is a lower bound** on any tour. Branch on including/
excluding edges; prune branches whose lower bound exceeds the best tour so far.

### Search orders

- **FIFO-BB** (queue → BFS-like), **LIFO-BB** (stack → DFS-like), **LC-BB**
  (least-cost: expand the most promising node first, via a priority queue). LC is
  usually the most efficient.

### MCQs

1. B&B prunes using? → an **optimistic bound vs the best-so-far**.
2. 0/1 knapsack B&B bound comes from? → the **fractional (LP) relaxation**.
3. TSP B&B lower bound from? → **cost-matrix row/column reduction**.

---

## 13.7 Pruning & Optimisation Techniques

- **Constraint checking early** (don't extend an invalid state) — the core idea.
- **Choice ordering** — try the most-constrained option first (**minimum
  remaining values**, e.g. the Sudoku cell with fewest candidates).
- **Symmetry breaking** — e.g. fix the first queen to the first half of row 0.
- **Memoisation** when subproblems repeat (Word Break) — backtracking → DP.
- **Bounding** — branch & bound for optimisation.

### Forward checking & constraint propagation (the smarter pruning)

Plain backtracking checks a choice only *when it is about to be made*. **Forward
checking** looks one step **ahead**: after assigning a variable, it removes the
now-illegal values from the **domains of the not-yet-assigned** variables. If any
future variable's domain becomes **empty**, you backtrack **immediately** —
before ever descending into that doomed subtree.

- **Sudoku example:** after writing a `5` in a cell, delete `5` from the candidate
  lists of every cell in the same row, column, and box. If some empty cell is left
  with **zero** candidates, this branch is already dead — undo now.
- **Constraint propagation** is forward checking taken further: keep cascading the
  eliminations. If a cell is reduced to a **single** candidate, fill it and
  propagate again (the "naked single" rule). This can solve easy Sudokus with
  almost no search.
- **MRV pairs naturally with it:** forward checking shrinks domains; MRV (§13.7,
  "choice ordering") then dives into the variable with the **smallest remaining
  domain** — the one most likely to fail fast.

> **Memory hook:** backtracking says "try it, then check"; **forward checking says
> "check the future first, and quit the moment a neighbour runs out of options."**

### MCQs

1. Forward checking prunes by? → detecting a **future variable with an empty
   domain** after an assignment.
2. Reducing a cell to one candidate and filling it is? → **constraint propagation
   (naked single)**.
3. Best partner heuristic for forward checking? → **MRV** (fewest remaining
   values).

---

## Module 13 — Concept Review (one page)

- **Backtracking** = DFS over a state-space tree with **choose → explore →
  un-choose** + **pruning**; record a **copy** of the path. Time exponential,
  **space O(depth)=O(n)**.
- **Recursion passing:** `i+1` (subsets/combos), `i` (reuse), `used[]`
  (permutations). Dedup: subsets `i>start`; **permutations** `i>0 && a[i]==a[i-1]
  && !used[i-1]`.
- **Counts:** subsets 2ⁿ, perms n!, C(n,k); N-Queens(4)=2, (8)=92; Generate
  Parentheses = Catalan (n=3→5, n=4→14).
- **Board/graph:** N-Queens (3 sets), Sudoku (MRV), Word Search (sentinel +
  restore; +Trie), **m-coloring O(m^V)**, **Hamiltonian O(N!) (NP-complete)**.
- **Branch & Bound** = optimisation via bounds (knapsack LP bound, TSP matrix
  reduction; FIFO/LIFO/LC search).

## Module 13 — Flash Cards

- Q: Backtracking space? **A: O(depth)=O(n) (nodes visited is exponential).**
- Q: Subsets vs permutations recursion? **A: start index `i+1` vs `used[]` from 0.**
- Q: Subsets dedup vs perms dedup? **A: `i>start` vs `i>0 && !used[i-1]`.**
- Q: N-Queens(4)/(8) solutions? **A: 2 / 92 (N=2,3 → 0).**
- Q: Generate Parentheses n=3/4? **A: 5 / 14 (Catalan).**
- Q: B&B vs backtracking? **A: B&B optimises via bounds; backtracking enumerates.**
- Q: Backtracking time formula? **A: branching^depth (b^d) × work per node.**
- Q: Forward checking? **A: after an assignment, prune future domains; backtrack if
  any becomes empty.**
- Q: 4-Queens solutions (as column arrays)? **A: [1,3,0,2] and [2,0,3,1].**

## Module 13 — Pattern Recognition

- "Generate ALL subsets/permutations/combinations" → **backtracking template**.
- "Place items with constraints (queens, colors, assignments)" → **constraint
  backtracking + validity sets** / **m-coloring**.
- "Fill a grid/board legally" → **cell-by-cell backtracking** (Sudoku, word
  search).
- "Visit every node/vertex once" → **Hamiltonian path/cycle**.
- "Partition a string into valid pieces" → **prefix-try backtracking**.
- "Find the BEST among exponentially many (optimise)" → **branch & bound**.
- "Choices repeat as subproblems" → add **memoisation** (→ DP, Module 14).
- "Order matters? fixed size?" → **permutation / combination / subset** (the 2-Q
  decision).
- "Constraint puzzle that's slow" → add **forward checking + MRV** (prune future
  domains early).

## Module 13 — Interview Questions (with follow-ups)

1. *Subsets / permutations.* FU: *handle duplicates — show both (different!)
   guards.*
2. *Combination Sum.* FU: *with/without reuse; avoid duplicate sets.*
3. *N-Queens.* FU: *count solutions (N=8→92); O(1) diagonal checks.*
4. *Word Search.* FU: *many words at once → Trie (Word Search II).*
5. *Generate Parentheses.* FU: *why always valid? count = Catalan.*
6. *Graph m-coloring.* FU: *relation to N-Queens; complexity O(m^V).*

## Module 13 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** **N-Queens solution counts**, state-space tree **node
  counts** (2^(n+1)−1; permutation-tree nodes) and recursion depth, **branch &
  bound** for 0/1 knapsack (LP upper bound) and TSP (matrix-reduction lower
  bound), FIFO/LIFO/LC-BB, m-coloring, Hamiltonian cycle (NP-complete), and
  "which technique" (backtracking vs B&B vs DP) MCQs. **CSP topics** —
  **forward checking**, **constraint propagation**, and the **MRV** heuristic —
  are AI/DAA staples worth a line each.

---

*End of Module 13. Next: Module 14 — Dynamic Programming (the big one) — split
across M14a (foundations, 1D, 2D), M14b (sequences, knapsack), M14c (advanced:
tree/bitmask/digit/interval + optimisations) — with visuals.*
