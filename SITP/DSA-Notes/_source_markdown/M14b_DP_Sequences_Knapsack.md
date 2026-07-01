---
title: "Module 14b — Dynamic Programming: Sequences & Knapsack"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14b — DP: Sequence DP & the Knapsack Family

> **Why this part.**
> Two of the most-asked DP families live here: **sequence DP** (LIS, LCS — the
> backbone of diff tools, DNA alignment, autocomplete) and the **knapsack family**
> (0/1, unbounded, subset-sum, partition — the backbone of resource-allocation
> problems). Recognise which family a problem belongs to and the recurrence almost
> writes itself.

This module is **P0**. LIS/LCS and 0/1 knapsack are interview + GATE staples.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

---

## 14b.1 Longest Increasing Subsequence (LIS)

### Problem & two solutions

The longest subsequence (not necessarily contiguous) whose values strictly
increase.

![LIS of [10,9,2,5,3,7,101,18] = 4; dp[i] = 1 + max(dp[j] for j<i, nums[j]<nums[i]); O(n log n) via tails.](images/109_lis.png)

```text
# O(n^2) DP
dp[i] = 1 + max(dp[j] for all j < i with nums[j] < nums[i], else 0)
answer = max(dp)

# O(n log n): maintain 'tails' (smallest possible tail of an LIS of each length)
for x in nums:
    pos = lower_bound(tails, x)     # first tail >= x
    if pos == len(tails): tails.append(x)   # x extends the longest LIS
    else: tails[pos] = x                     # x improves an existing length
answer = len(tails)
```

- `[10,9,2,5,3,7,101,18]` → LIS length **4** (e.g. `2,3,7,18` or `2,5,7,101`).
- **Important:** `tails` is **not** an actual LIS, only its length is correct.

**Reconstructing the actual subsequence** (a guaranteed follow-up): keep a
`parent[]` array. In the O(n²) version, set `parent[i] = the j that maximised
dp[i]`; track the index with the largest `dp`, then walk `parent` backwards and
reverse. (In the O(n log n) version, store `idx[pos]=i` when you place `x` at
`pos`, and `parent[i]=idx[pos-1]`.)

- **Number of LIS (LC 673):** keep a second array `count[i]`: when `dp[j]+1 ==
  dp[i]` **add** `count[j]`; when `dp[j]+1 > dp[i]` **reset** `count[i]=count[j]`.
- **Other variants:** Longest Non-Decreasing (use `upper_bound`), Russian Doll
  Envelopes (2D LIS), Longest Bitonic.

> **Memory hook:** *patience sorting* — deal each card onto the leftmost pile
> whose top is ≥ it; the number of piles = LIS length.

**Worked trace — O(n log n) tails, `nums=[10,9,2,5,3,7,101,18]`.** `tails[k]` = the
smallest possible tail value of an increasing subsequence of length `k+1`. For each
`x` we `lower_bound` (first tail ≥ x) and either append (new longest) or overwrite:

```text
 x=10 : tails empty -> append          tails=[10]
 x=9  : 9 replaces 10 (first >=9)       tails=[9]
 x=2  : 2 replaces 9                    tails=[2]
 x=5  : 5 > all -> append               tails=[2,5]
 x=3  : 3 replaces 5 (first >=3)        tails=[2,3]
 x=7  : 7 > all -> append               tails=[2,3,7]
 x=101: 101 > all -> append             tails=[2,3,7,101]
 x=18 : 18 replaces 101 (first >=18)    tails=[2,3,7,18]
 answer = len(tails) = 4
```

> **Warning (restate):** the final `tails=[2,3,7,18]` *happens* to be a real LIS
> here, but in general it is **not** — only its **length** is guaranteed. Overwrites
> can leave stale prefixes; use a `parent[]` array (above) to recover a true LIS.

### MCQs

1. LIS O(n²) recurrence? → `dp[i] = 1 + max(dp[j] : j<i, nums[j]<nums[i])`.
2. LIS in O(n log n) uses? → a **tails** array + **binary search**.
3. Is the tails array a valid LIS? → **No** (only its length is correct).

### Problems

- Longest Increasing Subsequence (300); Number of LIS (673); Russian Doll
  Envelopes (354); Longest Bitonic; Maximum Length of Pair Chain (646).

---

## 14b.2 Longest Common Subsequence (LCS) & friends

### LCS — the 2D string-DP archetype

![LCS of 'ACE' & 'ABCDE' = 3; equal chars add 1 to the diagonal, else take max of left/up.](images/110_lcs.png)

```text
# LCS                                         Time O(m*n), Space O(m*n) -> O(min)
if A[i-1] == B[j-1]: dp[i][j] = dp[i-1][j-1] + 1      # match -> extend diagonal
else:                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

`'ACE'` & `'ABCDE'` → **3** (`ACE`). LCS underlies `diff`, `git`, DNA alignment,
and plagiarism detection.

**Worked table** (`A`="ACE" rows, `B`="ABCDE" cols; first row/col = 0):

```
        ""  A  B  C  D  E
   ""    0  0  0  0  0  0
   A     0  1  1  1  1  1
   C     0  1  1  2  2  2
   E     0  1  1  2  2  3   <- answer = dp[3][5] = 3
```

**Printing the LCS** (backtrack from `dp[m][n]`): if `A[i-1]==B[j-1]`, prepend the
char and go **diagonal** (i--, j--); else move toward the **larger** of
`dp[i-1][j]` / `dp[i][j-1]`. **Space note:** two rolling rows give the **length in
O(min(m,n))** space — but then you **can't backtrack** the string; to recover the
LCS in O(min) space use **Hirschberg's algorithm** (divide & conquer).

**Worked backtrack — recover "ACE" from the table above** (start at `dp[3][5]=3`):

```text
 (i=3,j=5): A[2]='E', B[4]='E'  MATCH  -> emit 'E', go diagonal to (2,4)
 (i=2,j=4): A[1]='C', B[3]='D'  no     -> dp[1][4]=1 vs dp[2][3]=2, go left to (2,3)
 (i=2,j=3): A[1]='C', B[2]='C'  MATCH  -> emit 'C', go diagonal to (1,2)
 (i=1,j=2): A[0]='A', B[1]='B'  no     -> dp[0][2]=0 vs dp[1][1]=1, go left to (1,1)
 (i=1,j=1): A[0]='A', B[0]='A'  MATCH  -> emit 'A', go diagonal to (0,0) STOP
 emitted (reversed) = A, C, E  ->  "ACE"
```

Because we prepend on each match (or read the emissions in reverse), the recovered
subsequence is **"ACE"**, exactly length 3.

### The LCS family (same table, different transition)

- **Longest Common Substring** (contiguous): reset to 0 on mismatch; track the max
  cell.
- **Edit Distance** (Module 14a): the "min operations" cousin.
- **Longest Palindromic Subsequence (LC 516):** `LCS(s, reverse(s))`!
- **Shortest Common Supersequence, Distinct Subsequences, Interleaving String,
  Min Insertions/Deletions to make equal** — all `dp[i][j]` over two sequences.

> **Memory hook:** LCS = "how much of two sequences lines up *in order*"; matches
> step the **diagonal**, mismatches take the **better neighbour**.

### MCQs

1. LCS match vs mismatch transition? → `diag+1` vs `max(left, up)`.
2. Longest Palindromic Subsequence = ? → **LCS(s, reverse(s))**.
3. Longest common *substring* differs how? → **reset to 0** on mismatch.

### Problems

- Longest Common Subsequence (1143); Longest Palindromic Subsequence (516);
  Shortest Common Supersequence (1092); Distinct Subsequences (115); Interleaving
  String (97); Delete Operation for Two Strings (583).

---

## 14b.3 The Knapsack Family

This family = "pick items under a capacity/target constraint." Learn the **0/1**
base, then the variations are small tweaks.

### 0/1 Knapsack — each item used at most once

![0/1 Knapsack: dp[i][w] = max(skip item, take item); val=[60,100,120], wt=[10,20,30], W=50 → 220.](images/111_knapsack.png)

```text
# 0/1 Knapsack                                Time O(n*W), Space O(n*W) -> O(W)
dp[i][w] = max( dp[i-1][w],                       # skip item i
                dp[i-1][w - wt[i]] + val[i] )      # take item i (if it fits)

# 1D space-optimised: iterate w RIGHT-TO-LEFT so each item is used once
for each item (wt, val):
    for w in W down to wt:
        dp[w] = max(dp[w], dp[w-wt] + val)
```

- `val=[60,100,120], wt=[10,20,30], W=50` → **220** (items 2+3). Greedy-by-ratio
  gives only 160 → that's why this needs DP (Module 11 contrast).

**Worked table** (compressed: `wt=[1,2,3], val=[60,100,120], W=5` — same 220):

```
 item\w   0   1    2    3    4    5
   -      0   0    0    0    0    0
   1      0  60   60   60   60   60
   2      0  60  100  160  160  160
   3      0  60  100  160  180  220   <- dp[3][5] = 220
```

**Item recovery** (backtrack): `dp[3][5]=220 ≠ dp[2][5]=160` → item 3 taken; go to
`dp[2][5-3]=dp[2][2]=100 ≠ dp[1][2]=60` → item 2 taken; reach `dp[1][0]` → stop.
Chosen = **{2, 3}**.
- **Pseudo-polynomial:** O(n·W) looks polynomial, but `W` is a *value* whose input
  size is `log W` bits → not truly polynomial (a GATE/complexity subtlety).
- **Why right-to-left in 1D?** So `dp[w-wt]` still refers to the *previous* item's
  row (item used once). **Left-to-right** reads `dp[w-wt]` *after* it was already
  updated for this same item in this pass, so the item **stacks on itself** →
  unlimited copies → that's exactly unbounded knapsack.

### Unbounded Knapsack — unlimited copies (iterate left-to-right)

```text
for each item:
    for w in wt to W:        # LEFT-TO-RIGHT -> item can be reused
        dp[w] = max(dp[w], dp[w-wt] + val)
```

- **Coin Change** (Module 14a) is unbounded knapsack (each coin reusable).
  **Count ways (Coin Change II, LC 518):** loop **coins outside, amount inside**
  to count *combinations* (not permutations) — a classic loop-order gotcha.

### Bounded knapsack — at most `cᵢ` copies of item `i`

The middle ground: each item has a **fixed count limit** `cᵢ` (not once, not
infinite). The clean way is **binary splitting**: break `cᵢ` copies into powers of
two (1, 2, 4, …, remainder), each treated as one *new* 0/1 item. Then run ordinary
0/1 knapsack. This represents any count 0..cᵢ with only **O(log cᵢ)** items.

```text
# Bounded knapsack via binary splitting        Time O(W * sum(log c_i))
for each item (wt, val, count c):
    k = 1
    while c > 0:
        take = min(k, c)                     # a "bundle" of `take` copies
        add a 0/1 item of weight take*wt, value take*val
        c -= take;  k *= 2                   # 1,2,4,... then the remainder
run standard 0/1 knapsack (right-to-left) over the generated bundles
```

**Decision table — which knapsack am I in?**

| Copies per item | Name | 1D loop direction | Classic problems |
|---|---|---|---|
| **exactly once** | 0/1 knapsack | `w` **right→left** | subset-sum, partition, target sum |
| **unlimited** | unbounded | `w` **left→right** | coin change, rod cutting, perfect squares |
| **at most cᵢ** | bounded | binary-split → 0/1 | "≤ k of each item" resource problems |

> **Memory hook:** *once → right-to-left; forever → left-to-right; a fixed few →
> split into powers of two, then treat as 0/1.*

### Subset Sum / Equal Partition / Target Sum

![Subset Sum: dp[s] = dp[s] OR dp[s-num]; equal partition = subset-sum to total/2.](images/112_subset_sum.png)

- **Subset Sum:** boolean DP, base **`dp[0]=true`**, iterate **right-to-left** (as
  in 0/1, so each number is used once): `dp[s] = dp[s] or dp[s-num]`.
- **Equal Partition (LC 416):** subset-sum to `total/2` (only if total is even).
- **Target Sum (LC 494):** assign `+`/`−` to reach `target`. Let `P` = sum of the
  `+` set, `N` = sum of the `−` set: `P − N = target` and `P + N = sum` ⇒
  **`P = (sum + target) / 2`**. So count subsets summing to `(sum+target)/2`
  (reject if `sum+target` is odd or negative). *This algebra is the whole point.*
- **Last Stone Weight II, Ones and Zeroes** — knapsack variants.

**Worked table — Subset Sum, `nums=[3,34,4,12,5,2]`, target = 9.** `dp[s]` = "can we
hit sum `s`?" Start `dp[0]=T`; for each number sweep `s` **right→left** so a number
is used at most once. Showing sums 0..9 after each number:

```text
 after num   s: 0  1  2  3  4  5  6  7  8  9
   (init)       T  .  .  .  .  .  .  .  .  .
   +3           T  .  .  T  .  .  .  .  .  .
   +34          T  .  .  T  .  .  .  .  .  .   (34>9, no change)
   +4           T  .  .  T  T  .  .  T  .  .   (dp[7]=dp[3])
   +12          (no change, 12>9)
   +5           T  .  .  T  T  T  .  T  T  T   (dp[9]=dp[4], dp[8]=dp[3], dp[5]=dp[0])
   +2           T  .  T  T  T  T  T  T  T  T   (dp[9]=dp[7] etc.)
 dp[9] = T  ->  YES, e.g. subset {4,5} or {3,4,2} sums to 9
```

> **Memory hook:** subset-sum = a 0/1 knapsack where **value = weight** and you ask
> "can I fill *exactly* this much?"

### MCQs

1. 0/1 knapsack recurrence? → `max(dp[i-1][w], dp[i-1][w-wt]+val)`.
2. 1D knapsack iterate direction (0/1 vs unbounded)? → **right-to-left vs
   left-to-right**.
3. Equal partition reduces to? → **subset-sum to total/2**.
4. Why is O(n·W) "pseudo-polynomial"? → `W` is a **value** (input size log W).
5. Bounded knapsack (≤ cᵢ copies) trick? → **binary splitting** into powers of two,
   then run 0/1 → **O(W·Σ log cᵢ)**.

### Problems

- 0/1: Partition Equal Subset Sum (416); Target Sum (494); Last Stone Weight II
  (1049); Ones and Zeroes (474). Unbounded: Coin Change (322); Coin Change II
  (518); Combination Sum IV (377); Perfect Squares (279).

---

## Module 14b — Concept Review (one page)

- **LIS:** O(n²) `dp[i]=1+max(dp[j]:nums[j]<nums[i])`; **O(n log n)** via tails +
  binary search (length only).
- **LCS:** 2D string DP; match → `diag+1`, else `max(left,up)`; family includes
  edit distance, LPS = LCS(s, reverse(s)), supersequence.
- **0/1 Knapsack:** `max(skip, take)`; 1D iterate **right-to-left**; **pseudo-
  polynomial** O(n·W).
- **Unbounded knapsack** (reuse) iterate **left-to-right**; coin change is
  unbounded; count-ways needs **coins-outer** loop order.
- **Subset-sum / partition / target-sum** = knapsack with value=weight; partition
  → sum to total/2.

## Module 14b — Flash Cards

- Q: LIS in O(n log n)? **A: tails array + binary search (length only).**
- Q: LCS transitions? **A: diag+1 (match) / max(left,up) (mismatch).**
- Q: Longest palindromic subsequence trick? **A: LCS(s, reverse(s)).**
- Q: 0/1 vs unbounded 1D loop? **A: right-to-left vs left-to-right.**
- Q: Coin Change II loop order? **A: coins outside, amount inside (combinations).**
- Q: Equal partition? **A: subset-sum to total/2 (total even).**
- Q: Why knapsack pseudo-polynomial? **A: W is a value, size log W bits.**
- Q: Bounded knapsack (≤ cᵢ copies)? **A: binary-split into powers of two → 0/1.**
- Q: Is the LIS tails array a real LIS? **A: no — only its length is guaranteed.**

## Module 14b — Pattern Recognition

- "Longest increasing/chain subsequence" → **LIS** (n log n with tails).
- "Compare/align two sequences/strings" → **LCS-family 2D DP**.
- "Pick items under a capacity, each once" → **0/1 knapsack**.
- "Unlimited copies / make an amount" → **unbounded knapsack / coin change**.
- "Can a subset reach/split to a sum?" → **subset-sum / partition**.

## Module 14b — Interview Questions (with follow-ups)

1. *LIS.* FU: *O(n log n)? reconstruct the actual subsequence?*
2. *LCS.* FU: *print the LCS; O(min) space; longest palindromic subsequence.*
3. *0/1 knapsack.* FU: *1D space; why right-to-left? pseudo-polynomial meaning.*
4. *Coin change (min) vs coin change II (count).* FU: *why loop order differs.*
5. *Partition equal subset sum.* FU: *reduce to subset-sum; complexity.*

## Module 14b — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** filling LCS / 0/1-knapsack tables by hand, LIS length,
  knapsack as **pseudo-polynomial**, subset-sum/partition, and the **loop-order**
  distinction for count vs min. Frequently tested numerically.

---

*End of Module 14b. Next: Module 14c — Advanced DP (tree DP, bitmask DP, digit DP,
interval DP, DP optimisations) — with visuals.*
