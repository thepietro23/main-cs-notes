---
title: "Module 12 — Divide & Conquer"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 12 — Divide & Conquer

> **Why divide & conquer.**
> The idea: **split** a problem into smaller independent pieces, **solve** each
> (usually by recursion), and **combine** the results. This single template gives
> the fastest general sorts (merge/quick sort), O(log n) search (binary search),
> O(n) selection (quickselect), fast multiplication (Karatsuba/FFT), and more.
> Mastering binary search and its "search the answer" cousin alone unlocks a huge
> slice of FAANG questions.

This module is **P0**: binary search is one of the most-asked interview tools;
merge/quick sort + recurrences are GATE staples.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

### Quick selector

![Flowchart: binary search, binary-search-on-answer, quickselect, or a general sort.](images/99_fc_divide_conquer.png)

---

## 12.1 The D&C Template, Recurrences & Master Theorem

### The three steps

1. **Divide** the problem into smaller subproblems.
2. **Conquer** each subproblem (recurse; the base case solves directly).
3. **Combine** the sub-answers into the final answer.

The running time is a **recurrence** `T(n) = a·T(n/b) + f(n)` (`a` subproblems of
size `n/b`, plus `f(n)` to divide+combine).

### Master Theorem (self-contained recap)

Compare `f(n)` with `n^(log_b a)`. The **bigger one wins**:

| Case | Condition | Result |
|---|---|---|
| 1 | `f(n)` smaller: `f = O(n^(log_b a − ε))` | `T(n) = Θ(n^(log_b a))` |
| 2 | `f(n)` equal: `f = Θ(n^(log_b a))` | `T(n) = Θ(n^(log_b a) · log n)` |
| 3 | `f(n)` bigger: `f = Ω(n^(log_b a + ε))` (+ regularity) | `T(n) = Θ(f(n))` |

**Worked examples (GATE practice):**

- `T(n)=2T(n/2)+n`: `n^(log₂2)=n¹=f(n)` → **Case 2** → **Θ(n log n)** (merge sort).
- `T(n)=4T(n/2)+n`: `n^(log₂4)=n²` dominates `n` → **Case 1** → **Θ(n²)**.
- `T(n)=2T(n/2)+n²`: `f=n²` dominates `n` → **Case 3** → **Θ(n²)**.
- `T(n)=T(n/2)+1`: `n^(log₂1)=n⁰=1=f` → **Case 2** → **Θ(log n)** (binary search).
- **GATE trap:** `T(n)=2T(n/2)+n log n` — `f` is **between** cases → Master
  Theorem (basic form) **does not apply**; the extended Case 2 gives **Θ(n
  log² n)**.

**When Master Theorem doesn't apply:** uneven splits (e.g. median-of-medians
`T(n)=T(n/5)+T(7n/10)+O(n)`) or **subtract-and-conquer** (`T(n)=aT(n−b)+f(n)`)
need the **recursion-tree** or **substitution (guess & verify)** methods (Module
1 §1.5).

> **When does D&C beat iteration?** When splitting saves more work than the
> combine step costs, or the problem is naturally recursive (sorting, trees). For
> simple linear scans, iteration wins (no recursion overhead).

### MCQs

1. `T(n)=2T(n/2)+n²`? → **Θ(n²)** (Case 3).
2. `T(n)=2T(n/2)+n log n`? → **Θ(n log² n)** (extended; basic MT fails).
3. Which recurrences need recursion-tree/substitution? → **uneven splits /
   subtract-and-conquer**.

---

## 12.2 Merge Sort (and counting inversions)

### The idea

Split in half, **recursively sort** each half, then **merge** the sorted halves
(compare fronts, take the smaller).

![Merge sort: divide in half down to single elements, then merge sorted halves back up.](images/95_merge_sort.png)

```text
# Merge sort                                 Time O(n log n) always, Space O(n)
sort(a):
    if len(a) <= 1: return a
    mid = len/2; L = sort(a[:mid]); R = sort(a[mid:])
    return merge(L, R)        # walk both, append smaller front each time
```

- **O(n log n) in ALL cases**; **stable**; **O(n) extra space**. Best for **linked
  lists** and **external sorting** (data too big for RAM).
- **Comparison count:** merging runs of size `m, n` takes between `min(m,n)` and
  `m+n−1` comparisons (e.g. merging `[1,3,5]` & `[2,4,6]` = 5 comparisons). Total
  is Θ(n log n).

### Counting inversions in O(n log n) (GATE + FAANG)

An **inversion** is a pair `(i<j)` with `a[i] > a[j]` (a measure of
"unsortedness"). Brute force counts them in O(n²); merge sort does it in **O(n log
n)** with one extra line.

**Key insight:** during the merge, when you take an element from the **right**
half (because it's smaller), it forms an inversion with **every element still
remaining in the left** half — so add `(remaining left count)`.

```text
# Count inversions (augmented merge)         O(n log n)
during merge of L and R:
    if L[i] <= R[j]: take L[i]; i++
    else: take R[j]; j++; inversions += (len(L) - i)   # R[j] < all remaining L
```

**Worked example.** `[2,4,1,3,5]` → inversions are `(2,1),(4,1),(4,3)` = **3**.
Max inversions = `n(n−1)/2` (reverse-sorted); min = 0 (sorted). (Ties to LC 315
Count of Smaller Numbers After Self, LC 493 Reverse Pairs.)

### MCQs

1. Merge sort time/space/stable? → **O(n log n) / O(n) / stable**.
2. Count inversions efficiently? → **merge sort, O(n log n)**.
3. Max inversions in an array of n? → **n(n−1)/2** (reverse-sorted).

### Problems

- Sort an Array (912); Sort List (148); Count of Smaller Numbers After Self (315);
  Reverse Pairs (493); Count Inversions (classic).

---

## 12.3 Quicksort, Quickselect & Selection

### Quicksort

Pick a **pivot**, **partition** (smaller left, larger right; pivot to its final
spot), recurse on each side.

![Quicksort: choose a pivot, partition around it, then recurse on the two sides.](images/96_quicksort.png)

```text
# Quicksort                                  Avg O(n log n), Worst O(n^2)
quicksort(a, lo, hi):
    if lo >= hi: return
    p = partition(a, lo, hi)
    # recurse into the SMALLER side first to bound stack depth to O(log n)
    quicksort(a, lo, p-1); quicksort(a, p+1, hi)
```

- **In place**; **not stable**. Stack depth is **O(log n) expected**, but **O(n)
  worst-case** unless you always recurse into the smaller partition first.
- **Worst case O(n²)** on already-sorted input with a first/last pivot → fix with
  a **random pivot** or median-of-three → expected O(n log n).
- Usually the **fastest in practice** (cache locality); libraries use **introsort**
  (quicksort + insertion sort for small parts + heapsort fallback).

**Comparison counts (GATE):**

- **Worst case** = sorted input with first/last pivot → partitions of size
  `(n−1, 0)` → comparisons `(n−1)+(n−2)+…+1 = n(n−1)/2 = C(n,2)`. (n=5 sorted →
  4+3+2+1 = **10**.)
- **Best/average** = balanced splits → `T(n)=2T(n/2)+(n−1)` → **Θ(n log n)**;
  average ≈ **1.386·n·log₂n**.

### Lomuto vs Hoare partition (know the difference)

| | Lomuto | Hoare |
|---|---|---|
| Pointers | one forward; pivot = last | two, from both ends |
| Swaps | more | ~3× fewer |
| Pivot final position | **yes** (returns pivot index) | **no** (returns a split) |
| Recursion split | `lo..p−1`, `p+1..hi` | **`lo..p`, `p+1..hi`** |

> **Bug warning:** the recursion bounds **differ**. Lomuto returns the pivot's
> final index (recurse around it); Hoare returns a split where the pivot is *not*
> placed (recurse including `p`). Mixing them breaks the sort. For many duplicate
> keys, use **3-way (Dutch National Flag) partition** (Module 2, LC 75).

### Quickselect — k-th smallest in O(n) average

Same partition, but recurse into **only the side** containing the k-th element.

```text
# Quickselect                                Avg O(n), Worst O(n^2)
after partition at index p:
    if k == p: return a[p]
    elif k < p: recurse left
    else: recurse right
```

### Quickselect vs heap (the interview follow-up)

| | Quickselect | Size-k heap |
|---|---|---|
| Time | **O(n)** avg, O(n²) worst | **O(n log k)** |
| Space / data | in-place, **mutates** input, needs all data | O(k), works on **streams** |
| Use when | one-shot, in-memory k-th element | small k, streaming, or don't mutate |

### Median-of-medians (BFPRT) — guaranteed O(n) selection

Pick the pivot smartly to guarantee O(n) worst case: split into **groups of 5**,
take each group's median, **recursively select the median of those medians** as
the pivot. That pivot discards ≥ 3n/10 elements → `T(n) ≤ T(n/5) + T(7n/10) +
O(n)` = **O(n)** (since 1/5 + 7/10 < 1). Mostly **theoretical** (big constant);
randomised quickselect is preferred in practice.

### MCQs

1. Quicksort worst-case comparisons? → **n(n−1)/2** (sorted input, bad pivot).
2. Quickselect vs heap for streaming k-th? → **heap** (O(n log k)).
3. Guaranteed O(n) selection? → **median-of-medians (BFPRT)**.
4. Hoare vs Lomuto recursion split? → Hoare `lo..p, p+1..hi`; Lomuto `lo..p−1,
   p+1..hi`.

---

## 12.4 Binary Search — ONE template to rule them all

### The core

On a **sorted** array (or any **monotonic** condition), halve the range each step.

![Binary search: lo/mid/hi narrow the range by half each step; O(log n).](images/97_binary_search.png)

> **The #1 binary-search bug** is the loop boundary (`<` vs `<=`) and the update
> (`mid` vs `mid±1`). **Fix: learn ONE canonical template** (the half-open
> `lower_bound` below) and derive every variant from it.

### The canonical template — `lower_bound` (half-open)

```text
# first index i with a[i] >= target          Time O(log n)
lo, hi = 0, n             # hi = n (half-open; the answer can be n = "not found")
while lo < hi:
    mid = lo + (hi - lo) // 2
    if a[mid] < target: lo = mid + 1      # mid too small -> discard left incl mid
    else:               hi = mid          # mid is a candidate -> keep, shrink right
return lo                 # in [0, n]; invariant: a[lo-1] < target <= a[lo]
```

Derive everything from this `lo < hi` / `hi = mid` style:

- **upper_bound** (first `i` with `a[i] > target`): change `<` to `<=`.
- **first occurrence** = `lower_bound`; **last occurrence** = `upper_bound − 1`.
- **count of target** = `upper_bound − lower_bound`.

The **exact-match** template (`lo <= hi`, `return mid`) is fine for "does it
exist?", but for *boundaries/duplicates*, always use the half-open one above so
you never fight off-by-one again.

### Comparison count (GATE)

Worst-case comparisons = `⌊log₂ n⌋ + 1` (= `⌈log₂(n+1)⌉`). Examples: `n=100` →
`⌊6.64⌋+1 = 7`; `n=1000` → `9+1 = 10`; a million → ~20.

### The variants you MUST know

- **Search in a rotated sorted array (LC 33):** one half is always sorted; decide
  which half holds the target. **With duplicates (LC 81):** when `a[lo]==a[mid]
  ==a[hi]` you can't tell which half is sorted → advance `lo++ / hi--` (worst case
  **O(n)**).
- **Find Minimum in rotated array (LC 153);** duplicate variant **LC 154**.
- **Find Peak Element (LC 162):** works on an **unsorted** array! Compare `a[mid]`
  vs `a[mid+1]`; a peak must exist on the **uphill** side → binary search it in
  O(log n).

> **Memory hook:** the "guess 1–100, higher/lower" game — each guess halves the
> possibilities.

### MCQs

1. Binary search worst-case comparisons for n=1000? → **10**.
2. `lower_bound` vs `upper_bound`? → `<` vs `<=` in the same template.
3. Rotated array with duplicates worst case? → **O(n)** (ambiguous halves).
4. Why does Find Peak work unsorted? → a peak always lies on the **uphill** half.

### Problems

- Binary Search (704); Search Insert Position (35); First/Last Position (34);
  Rotated Array (33) + duplicates (81); Find Minimum Rotated (153) + dup (154);
  Find Peak (162); Single Element in Sorted Array (540 — index parity); Find K
  Closest Elements (658); Search a 2D Matrix (74); Time-Based Key-Value Store
  (981 — upper_bound).

---

## 12.5 Binary Search on the Answer (the FAANG power-move)

### The idea

When you can't binary-search an array directly, binary-search the **answer
itself** — *if* "**can we achieve value X?**" is **monotonic** (F…F, T…T). Find
the boundary.

![Binary search on the answer: a monotonic FFFF...TTTT predicate — binary-search the first TRUE.](images/98_bsearch_answer.png)

```text
# MINIMISE: smallest X that is feasible      O(log(range) * cost(feasible))
lo, hi = min_answer, max_answer
while lo < hi:
    mid = lo + (hi - lo) // 2
    if feasible(mid): hi = mid          # works -> try smaller
    else:             lo = mid + 1      # too small -> go bigger
return lo

# MAXIMISE: largest X that is feasible       (mirror — note the CEILING mid!)
while lo < hi:
    mid = lo + (hi - lo + 1) // 2        # +1 ceiling, else infinite loop
    if feasible(mid): lo = mid           # works -> try bigger
    else:             hi = mid - 1
return lo
```

> **Notorious bug:** in the **maximise** mirror, you MUST use the **ceiling**
> `mid = lo + (hi−lo+1)/2`; the plain floor causes an infinite loop when
> `hi = lo+1`.

- **Recognise it:** "minimise the maximum…", "maximise the minimum…", "smallest
  capacity/speed/size such that …".
- **Classics:** Koko Eating Bananas (875), Capacity to Ship in D Days (1011),
  Split Array Largest Sum (410), Min Days to Make Bouquets (1482), Kth Smallest in
  a Sorted Matrix (378), Aggressive Cows / Magnetic Force (1552 — *maximise the
  minimum*).

### MCQs

1. Precondition for BS-on-answer? → the feasibility test is **monotonic**.
2. Maximise-variant midpoint? → **ceiling** `lo+(hi−lo+1)/2` (avoids infinite
   loop).
3. Koko/ship search over? → the **answer space** (speed/capacity), not an array.

---

## 12.6 More Classic D&C Algorithms

### Fast (binary) exponentiation — O(log n)

Compute `aⁿ` by squaring: `aⁿ = (a^(n/2))²` (× a once more if n is odd).
`T(n)=T(n/2)+O(1)` = **O(log n)**.

```text
# Fast power (iterative, bit-scanning)        O(log n)
result = 1; base = a
while n > 0:
    if n & 1: result *= base       # for modular: result = result*base % m
    base *= base                   # base = base*base % m
    n >>= 1
return result
```

- **Modular exponentiation** `aⁿ mod m` (crypto, hashing, SEBI-IT) uses the same
  loop with `% m`.
- **Matrix exponentiation:** raise a transition matrix to the n-th power in O(log
  n) — e.g. Fibonacci via `[[1,1],[1,0]]ⁿ`. (LC 50 Pow(x,n); LC 372.)

### Closest Pair of Points (2D)

Sort by x; split; recursively find the closest pair in each half; then check a
thin **strip** around the dividing line — each point compares against **at most
~7** following points (a constant, by a packing argument). **O(n log n)** vs
brute-force O(n²).

### Maximum Subarray (D&C view)

The max subarray lies in the **left** half, the **right** half, or **crosses the
middle**. The crossing case: scan **left from mid** for the best suffix sum, scan
**right from mid+1** for the best prefix sum, add them. `answer = max(left, right,
across)` → `T(n)=2T(n/2)+O(n)` = **O(n log n)**. (Kadane does it in O(n) — Module
2 — but this is the instructive D&C version.)

### Ternary Search (unimodal functions)

When a function **strictly increases then decreases** (unimodal), binary search
doesn't apply but **ternary search** does: probe at the two trisection points
`m1=lo+(hi−lo)/3`, `m2=hi−(hi−lo)/3`; discard the third that can't hold the
extremum. **O(log n)** probes. (Continuous analogue: golden-section search.)

### Karatsuba / Strassen / FFT (fast multiplication)

- **Karatsuba:** multiply n-digit numbers with **3** half-size multiplications
  instead of 4 → `T(n)=3T(n/2)+O(n)` = **O(n^1.585)**.
- **Strassen:** 7 instead of 8 recursive matrix multiplications → **O(n^2.807)**.
- **FFT:** evaluate a polynomial at the n complex roots of unity by splitting into
  even/odd-indexed terms (`P(x)=Pₑ(x²)+x·Pₒ(x²)`), recursing, combining →
  `T(n)=2T(n/2)+O(n)` = **O(n log n)**. Used for fast polynomial/bignum
  multiplication and convolution. *(ICPC/advanced; optional for SEBI.)*

### MCQs

1. Fast exponentiation time? → **O(log n)**.
2. Closest pair strip checks how many neighbours per point? → a **constant (~7)**.
3. Karatsuba / Strassen / FFT complexities? → **O(n^1.585) / O(n^2.807) / O(n log
   n)**.
4. Search a unimodal function's max? → **ternary search**.

---

## Module 12 — Concept Review (one page)

- **D&C** = divide + conquer + combine; analyse with the **Master Theorem** (3
  cases by comparing `f(n)` vs `n^(log_b a)`); uneven/subtract recurrences need
  tree/substitution.
- **Merge sort:** O(n log n) always, **stable**, O(n) space; counts **inversions**
  in O(n log n).
- **Quicksort:** O(n log n) avg, **O(n²) worst** = `n(n−1)/2` comparisons (random
  pivot fixes it); Lomuto vs Hoare differ in the recursion split.
- **Quickselect:** k-th smallest O(n) avg; **vs heap** (O(n log k), streaming);
  **median-of-medians** = guaranteed O(n).
- **Binary search:** learn ONE half-open `lower_bound` template; `upper_bound` =
  `<=`; worst comparisons `⌊log₂n⌋+1`; know rotated (+dup), find-peak (unsorted).
- **BS on the answer:** monotonic feasibility; **maximise** needs a **ceiling
  mid**.
- **Classics:** fast/modular/matrix exponentiation O(log n); closest pair O(n log
  n); ternary search (unimodal); Karatsuba/Strassen/FFT.

## Module 12 — Flash Cards

- Q: `T(n)=2T(n/2)+n log n`? **A: Θ(n log² n) (basic MT fails).**
- Q: Merge sort & inversions? **A: O(n log n); add remaining-left on right-take.**
- Q: Quicksort worst comparisons? **A: n(n−1)/2 (sorted + bad pivot).**
- Q: k-th smallest, streaming? **A: size-k heap O(n log k); else quickselect.**
- Q: Guaranteed O(n) select? **A: median-of-medians (BFPRT).**
- Q: lower vs upper bound? **A: `<` vs `<=` in the same half-open template.**
- Q: Maximise BS-on-answer pitfall? **A: use ceiling mid (else infinite loop).**
- Q: Fast exponentiation? **A: square-and-multiply, O(log n).**

## Module 12 — Pattern Recognition

- "Sorted array, find/insert/boundary/count" → **binary search (lower/upper
  bound)**.
- "Minimise max / maximise min / smallest X that works" → **BS on the answer**.
- "k-th smallest/largest / median, no full sort" → **quickselect** (streaming →
  heap).
- "Stable sort / linked list / external data / count inversions" → **merge sort**.
- "aⁿ or aⁿ mod m fast / fast Fibonacci" → **binary / matrix exponentiation**.
- "Max of a unimodal function" → **ternary search**.
- "Fast big-number / matrix / polynomial multiply" → **Karatsuba / Strassen /
  FFT**.

## Module 12 — Interview Questions (with follow-ups)

1. *Search in a rotated sorted array.* FU: *with duplicates (LC 81) — why O(n)?*
2. *Kth largest element.* FU: *quickselect vs heap; streaming data?*
3. *Koko eating bananas / ship capacity.* FU: *why monotonic; minimise vs
   maximise template.*
4. *Median of two sorted arrays.* FU: *partition the smaller array; O(log
   min(m,n)).*
5. *Why can quicksort be O(n²)? Prevent it?* FU: *worst-case comparison count.*
6. *Count inversions.* FU: *how does merge accumulate the count?*

## Module 12 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** **Master Theorem** on new recurrences (incl. the `n log n`
  trap & subtract-and-conquer), **quicksort best/worst/average comparison counts**
  (`n(n−1)/2`, `1.39 n log n`) and which input triggers each, **merge sort**
  comparisons/space/stability, **binary search comparison count** `⌊log₂n⌋+1`,
  and **counting inversions** (max `n(n−1)/2`). Modular exponentiation appears in
  SEBI-IT/crypto contexts. Extremely frequently tested.

---

## Median of Two Sorted Arrays (LC 4 — the partition sketch)

A top FAANG hard problem worth its own note. Binary-search the **cut** in the
**smaller** array `A` so that the left side of both arrays together holds exactly
`(m+n+1)/2` elements. Maintain `maxLeftA ≤ minRightB` **and** `maxLeftB ≤
minRightA`; when both hold you've found the split. The median is `max(maxLeftA,
maxLeftB)` (odd total) or the average of the two middle values (even total).
Complexity: **O(log min(m, n))** (binary-search the smaller array only).

---

*End of Module 12. Next: Module 13 — Backtracking (subsets, permutations,
combinations, N-Queens, Sudoku, word search) — with visuals.*
