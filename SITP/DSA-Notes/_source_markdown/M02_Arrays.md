---
title: "Module 2 — Arrays"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — Arrays

> **Why arrays come first (after fundamentals).**
> The array is the most basic and most important data structure. About 60–70% of
> interview and contest problems involve arrays in some form. Strings, stacks,
> queues, heaps, and hash tables are all built on arrays internally. Here we
> start with array *internals* and then learn the **patterns** (prefix sum, two
> pointers, sliding window) that you will reuse in every later module.

This module is **P0**. Roughly 70% of interviews start here.

> **How to read each technique below.** For every problem we go
> **Brute force → Better → Optimal**, with pseudocode and complexity at each
> step, and we explain *why* each optimisation works.

### Quick pattern selector (use this to pick a technique)

![Flowchart: ask these questions in order to choose the right array technique.](images/21_fc_array_selector.png)

---

## 2.1 Array Internals (what happens inside?)

### Definition

An **array** is a **contiguous** (back-to-back) block of same-type elements,
where each element is reached in O(1) using its **index**.

The address of an element comes from a simple formula:

```
address(arr[i]) = base_address + i * size_of_one_element
```

Because of this **one-multiply-one-add** formula, array access is **O(1)** — no
searching, just a calculation.

### Intuition (simple example)

Think of a **train** whose coaches are joined in a line, each coach the same
size. If you know where the first coach is, the 5th coach = first +
5×(coach length). You just calculate — you never search. That is "random
access": you can jump straight to any index.

### Static vs Dynamic arrays

| | Static array | Dynamic array (vector/ArrayList/list) |
|---|---|---|
| Size | Fixed at compile time | Can grow at runtime |
| Memory | Stack or a fixed block | On the heap; resizes when full |
| Example | `int a[10];` | C++ `vector`, Java `ArrayList`, Python `list` |

### Internal working — dynamic array doubling

A dynamic array holds a normal array with a **capacity**. When it is full and you
add one more element:

1. Allocate a new array of **double the capacity**.
2. Copy all old elements (O(n)).
3. Add the new element.

![A dynamic array doubles its size when full, copies the old data, then appends.](images/10_dynamic_array.png)

### Mathematical proof — amortised O(1) append

One copy is O(n), so how is append O(1)? Because copies happen **rarely**.

Suppose capacity starts at 1 and doubles. To add `n` elements, the total copy
cost is `1 + 2 + 4 + … + n ≈ 2n` = **O(n)** total. So the **per-append** average
is `2n / n = O(1)`. We call this **amortised O(1)** (a guaranteed average over a
sequence — Module 18).

> **Why double, not +1 or +10?** If you grow by just +1 each time, `n` appends
> cost `1+2+…+n = O(n²)`. **Doubling** (×2) is what gives O(1) amortised. This is
> a classic interview question.

### Complexity & memory

| Operation | Time | Note |
|---|---|---|
| Access `arr[i]` | O(1) | from the formula |
| Update `arr[i]` | O(1) | |
| Append (end) | O(1) amortised | doubling |
| Insert/delete (middle) | O(n) | everything else shifts |
| Search (unsorted) | O(n) | linear scan |
| Search (sorted) | O(log n) | binary search |

Memory: `n` elements × element size, plus a little spare capacity in a dynamic
array (up to ~2× in the worst case).

### Cache-friendliness (link to Module 1)

Array elements sit together, so one **cache line** holds several of them →
traversal is very fast (spatial locality). This is why arrays often beat linked
lists at the same O(n).

### Edge cases & common mistakes

- **Out-of-bounds** access (`arr[n]` when size is `n`) → undefined behaviour /
  crash / security bug.
- **Off-by-one** (loop `<= n` vs `< n`).
- Insert/delete in the middle is O(n) — doing it inside a loop accidentally makes
  it O(n²).
- Always test empty array and single element.

### MCQs

1. Why is `arr[i]` O(1)? → the address formula `base + i*size`.
2. Append with doubling is? → **O(1) amortised**.
3. n appends with +1 growth? → **O(n²)** total.

---

## 2.2 Prefix Sum (the king of range queries)

### Definition

A **prefix sum** array `pre` is built so that `pre[i]` = the sum of the first `i`
elements (`arr[0] + … + arr[i-1]`). Build it once (O(n)), then get **any range
sum in O(1)**.

```
sum(arr[L..R]) = pre[R+1] - pre[L]
```

### Intuition (simple example)

Suppose you wrote down your earnings for each day and you keep being asked "what
is the total from day 3 to day 7?" Adding it up each time is slow. Instead, keep
a **running total** (total up to each day). Then "total up to day 7 − total up to
day 2" gives the answer — just one subtraction!

![Prefix sum: running totals up to each element; a range sum is the difference of two prefix values.](images/11_prefix_sum.png)

### Brute force → Optimal

```text
# BRUTE FORCE: re-add for every query     Time O(n) per query, O(n*q) total
rangeSum(L, R):
    s = 0
    for i = L..R: s += arr[i]
    return s

# OPTIMAL: prefix sum                      Build O(n), each query O(1)
build:
    pre[0] = 0
    for i = 0..n-1: pre[i+1] = pre[i] + arr[i]
rangeSum(L, R):
    return pre[R+1] - pre[L]
```

*Why it helps:* the running total is computed once; each query becomes a single
subtraction instead of a loop. With many queries this changes O(n·q) into
O(n + q).

### Dry run

```python
arr  = [3, 1, 4, 1, 5, 9]
pre  = [0]
for x in arr:
    pre.append(pre[-1] + x)
# pre = [0, 3, 4, 8, 9, 14, 23]

# sum of arr[1..3] = 1+4+1 = 6
# = pre[4] - pre[1] = 9 - 3 = 6   ✓
```

> **Tip:** make `pre` of size `n+1` (an extra 0 at the front). Then `L=0` works
> with no special case. This avoids off-by-one bugs.
>
> **Memory hook:** prefix sum is like a *bank passbook* — it stores the running
> balance, so any "how much between two dates" question is just one subtraction.

### 2D Prefix Sum (matrix range sum)

In 2D, `P[i][j]` = the sum of the top-left rectangle. Any sub-rectangle's sum is
O(1) using **inclusion-exclusion**:

![2D prefix sum: a region's sum = P[D] − P[B] − P[C] + P[A] (A is added back because it was subtracted twice).](images/12_2d_prefix.png)

```
sum(rectangle) = P[D] - P[B] - P[C] + P[A]
```

Build O(n·m), each query O(1). (LeetCode 304 "Range Sum Query 2D".)

### Complexity

- Build: O(n) (1D), O(n·m) (2D)
- Query: O(1)
- Space: O(n) extra

### Production usage

Analytics dashboards (cumulative metrics), image processing (integral images —
used in Viola-Jones face detection), databases (running aggregates), range
queries.

### Common mistakes

- Making `pre` of size `n` (use `n+1`).
- Confusing inclusive vs exclusive ranges.
- Forgetting the `+P[A]` in the 2D inclusion-exclusion.

### Interview / Exam perspective

- **FAANG:** "subarray sum equals k" → prefix sum + hashmap (Module 7). The first
  tool for any range-query problem.
- **GATE:** rarely direct, but cumulative-cost reasoning is common.

### MCQs

1. How to make a range sum O(1)? → **prefix sum** preprocessing.
2. Size of the `pre` array? → **n+1**.
3. Why add A in the 2D sub-rectangle sum? → it was subtracted twice.

### Problems (Easy → Hard)

- **Easy:** Running Sum (LC 1480); Range Sum Query Immutable (LC 303).
- **Medium:** Subarray Sum Equals K (LC 560); Product Except Self (LC 238);
  Range Sum 2D (LC 304); Pivot Index (LC 724).
- **Hard:** Count subarrays with sum divisible by k; Max sum rectangle in 2D.

---

## 2.3 Difference Array (the king of range updates)

### Definition

The reverse of prefix sum. A **difference array** lets you add a value to an
entire **range** in **O(1)**, and then one prefix-sum pass produces the final
array. Perfect when there are many range updates.

### Intuition

You want to add `+v` to a range `[L, R]`. Looping over the whole range is
O(range). Instead, just **mark two spots**: `diff[L] += v` (start adding here)
and `diff[R+1] -= v` (stop here). At the end, take the prefix sum of `diff` to
get each position's actual value.

![Difference array: +v at the range start, −v just after the range end; then a prefix sum builds the final array.](images/13_difference_array.png)

### Brute force → Optimal

```text
# BRUTE FORCE: loop each update over its range   Time O(n) per update, O(n*k) total
for each update (L, R, v):
    for i = L..R: arr[i] += v

# OPTIMAL: difference array                       k updates O(k), finalise O(n)
diff = array of zeros, size n+1
for each update (L, R, v):
    diff[L]   += v
    diff[R+1] -= v
# finalise with a prefix sum
run = 0
for i = 0..n-1:
    run += diff[i]
    arr[i] = run
```

*Why it helps:* each range update touches only two cells instead of the whole
range; the single prefix-sum pass "spreads" all updates at once.

### Dry run

```python
n = 6
diff = [0]*(n+1)
# add 5 to indices 1..3
diff[1] += 5
diff[4] -= 5          # R+1 = 4
res, run = [], 0
for i in range(n):
    run += diff[i]
    res.append(run)
# res = [0, 5, 5, 5, 0, 0]   ✓
```

### Complexity

- `k` range updates: O(k)
- Finalising: O(n) (one prefix pass)
- Total: **O(n + k)** vs brute force **O(n·k)**

### Production usage

Booking/calendar systems (LC 731/732), traffic counts over time intervals,
"car pooling" (LC 1094), histogram counting, range increments.

### Common mistakes

- Writing `diff[R]` instead of `diff[R+1]` (off-by-one).
- Array bounds when `R+1 = n` (keep size `n+1`).

### MCQs

1. What is a difference array for? → **range update in O(1)**.
2. Prefix sum vs difference array? → one for range **queries**, one for range
   **updates**.

### Problems

- **Medium:** Car Pooling (LC 1094); Corporate Flight Bookings (LC 1109); My
  Calendar I/II (LC 731/732); Range Addition (LC 370).

---

## 2.4 Two Pointers

### Definition

Two index pointers move over the array (often from opposite directions, or at
different speeds) to turn a nested loop (O(n²)) into **O(n)**.

Two common forms:

1. **Opposite ends** — `L` from the start, `R` from the end, meeting in the
   middle (sorted array, pair sum, palindrome).
2. **Same direction** — both move forward at different speeds (slow/fast — dedup,
   window).

### Intuition (simple example)

In a sorted array you want a **pair with sum = target**. Start from both ends:

- Sum is **too big** → make it smaller → `R--`
- Sum is **too small** → make it bigger → `L++`
- **Found** → done

Each step moves one pointer, so there are at most `n` steps → **O(n)**.

> **Memory hook:** two people walk toward each other from both ends of a *sorted
> queue*; if the pair is too "heavy", the bigger one steps back (R−−); if too
> "light", the smaller one steps up (L++).

![Two pointers: L at the start, R at the end of a sorted array; move inward based on the sum.](images/14_two_pointers.png)

### Why it works (proof intuition)

Because the array is sorted: when the sum is too big, moving `L` right only makes
it bigger (useless) — so `R--` is the only correct move. We never skip a valid
pair. This **monotonicity** is what makes it correct.

![Flowchart: the two-pointer decision loop for finding a pair with a target sum.](images/22_fc_two_pointers.png)

### Brute force → Better → Optimal (pair with target sum)

```text
# BRUTE FORCE: try all pairs                 Time O(n^2), Space O(1)
for i = 0..n-1:
    for j = i+1..n-1:
        if arr[i] + arr[j] == target: return (i, j)

# BETTER: hash set (works on UNSORTED too)   Time O(n), Space O(n)
seen = empty set
for i = 0..n-1:
    if target - arr[i] in seen: return found
    add arr[i] to seen

# OPTIMAL for a SORTED array: two pointers    Time O(n), Space O(1)
L, R = 0, n-1
while L < R:
    s = arr[L] + arr[R]
    if   s == target: return (L, R)
    elif s >  target: R -= 1
    else:             L += 1
```

*Why each step helps:* the hash set removes the inner loop by remembering what we
have seen (space for time). If the array is already sorted, two pointers get the
same O(n) time with O(1) space.

### Complexity

- Time: **O(n)** (if sorted); if you must sort first → O(n log n)
- Space: **O(1)** (two-pointer version)

### When NOT to use

- The array is **unsorted** and you must keep original indices → a hashmap is
  better (Two Sum LC 1).
- Conditions are not monotonic, so it is unclear which pointer to move.

### Common mistakes

- `L <= R` vs `L < R` (double-counting a single element).
- Forgetting to skip duplicates (important in 3Sum).

### Interview perspective

- **Very common at FAANG:** 3Sum (LC 15), Container With Most Water (LC 11),
  Trapping Rain Water (LC 42), Valid Palindrome (LC 125).

### MCQs

1. Two pointers turn which complexity into which? → **O(n²) → O(n)**.
2. Opposite-ends two pointers needs the array to be? → **sorted**.

### Problems

- **Easy:** Valid Palindrome (125); Two Sum II sorted (167); Remove Duplicates
  (26).
- **Medium:** 3Sum (15); Container With Most Water (11); Sort Colors (75).
- **Hard:** Trapping Rain Water (42); 4Sum (18).

---

## 2.5 Sliding Window

### Definition

A **contiguous window** (subarray/substring) that slides across the array. Its
two edges are `left` and `right`. `right` moves forward to add an element;
when a condition breaks, `left` moves forward to remove an element. It turns
O(n²)/O(n³) brute force into **O(n)**.

Two forms: **fixed-size** window (size k) and **variable-size** window (the
longest/shortest that satisfies a condition).

### Intuition (simple example)

"Longest substring **without repeating** characters" — checking every substring
is O(n²). Instead keep a window:

- Move `right` forward, add the new character.
- If a duplicate appears, move `left` forward until the duplicate is gone.
- At each step, update the answer with the window length.

> **Memory hook:** think of a *bus with a stretchy length*. The front (right)
> keeps moving to pick up passengers; if a rule breaks, the back (left) moves up
> to drop passengers. The bus never reverses.

![Sliding window: move right forward; on a duplicate move left; each element is added and removed once → O(n).](images/15_sliding_window.png)

### Why it is O(n) (proof intuition)

Both `left` and `right` only move **forward**, never backward. Each element is
added at most once and removed at most once. Total moves ≤ 2n → **O(n)**. (This
is amortised reasoning.)

![Flowchart: expand the window with right; shrink with left while invalid; update the answer.](images/23_fc_sliding_window.png)

### Brute force → Optimal (longest substring without repeats)

```text
# BRUTE FORCE: check every substring        Time O(n^2) or O(n^3), Space O(n)
best = 0
for i = 0..n-1:
    seen = empty set
    for j = i..n-1:
        if s[j] in seen: break
        add s[j] to seen
        best = max(best, j - i + 1)

# OPTIMAL: sliding window + last-seen map    Time O(n), Space O(min(n, charset))
seen = empty map (char -> last index)
left = 0; best = 0
for right = 0..n-1:
    c = s[right]
    if c in seen and seen[c] >= left:
        left = seen[c] + 1          # jump left past the duplicate
    seen[c] = right
    best = max(best, right - left + 1)
```

*Why it helps:* instead of restarting the scan from every `i`, the window keeps
the work from the previous step and only slides `left` when needed.

### Fixed vs variable window templates

```python
# FIXED size k: build one window, then slide
window_sum = sum(a[:k]); best = window_sum
for i in range(k, len(a)):
    window_sum += a[i] - a[i-k]   # add new, remove old
    best = max(best, window_sum)

# VARIABLE: expand right; shrink left while invalid
left = 0
for right in range(len(a)):
    add(a[right])
    while invalid():
        remove(a[left]); left += 1
    update_answer(right - left + 1)
```

### Complexity

- Time: **O(n)** (each element in once, out once)
- Space: O(1) or O(k) (the window's map/counts)

### When NOT to use

- The target is **not contiguous** (a subsequence, not a subarray) → use DP.
- Negative numbers with "sum ≥ target" → the window is not monotonic; use prefix
  sum + a deque or binary search.

### Common mistakes

- Setting `left = seen[c]` instead of `seen[c]+1`.
- Forgetting to remove the old element in a fixed window.
- Not shrinking the window when it becomes invalid.

### Interview perspective

- **Extremely common:** Longest Substring Without Repeats (3), Minimum Window
  Substring (76), Longest Repeating Char Replacement (424), Max Sum Subarray of
  size k, Permutation in String (567).

### MCQs

1. Sliding-window time? → **O(n)** (each element in/out once).
2. When do you shrink a variable window? → when it becomes **invalid**.

### Problems

- **Easy:** Max Average Subarray I (643).
- **Medium:** Longest Substring Without Repeats (3); Longest Repeating Char
  Replacement (424); Permutation in String (567); Fruit Into Baskets (904).
- **Hard:** Minimum Window Substring (76); Sliding Window Maximum (239 — needs a
  monotonic deque, Module 6); Subarrays with K Distinct (992).

---

## 2.6 Kadane's Algorithm (maximum subarray sum)

### Definition

The maximum **contiguous** subarray sum in O(n). It is a tiny DP (a seed for
Module 14).

### Intuition (simple example)

Walk across the array keeping a "current running sum". **Key idea:** if the
running sum has gone **negative**, there is no point carrying it forward — it can
only make any new element smaller. So **start fresh**.

```
cur  = max(x, cur + x)      # either start fresh at x, or extend the previous run
best = max(best, cur)       # best so far
```

![Kadane: drop a negative running sum (start fresh); track the best subarray.](images/16_kadane.png)

### Brute force → Better → Optimal

```text
# BRUTE FORCE: every subarray                Time O(n^3), Space O(1)
best = -inf
for i = 0..n-1:
    for j = i..n-1:
        s = sum(arr[i..j])      # inner loop again
        best = max(best, s)

# BETTER: running sum for inner loop          Time O(n^2), Space O(1)
for i = 0..n-1:
    s = 0
    for j = i..n-1:
        s += arr[j]
        best = max(best, s)

# OPTIMAL: Kadane                              Time O(n), Space O(1)
cur = best = arr[0]
for x in arr[1..]:
    cur  = max(x, cur + x)
    best = max(best, cur)
```

*Why it helps:* the brute force recomputes overlapping sums; the better version
reuses the running sum (drops one loop); Kadane keeps just the best run ending
"here", so a single pass suffices.

### Why it works (DP view)

`cur` = "the max sum of a subarray ending at this index". Recurrence:
`cur[i] = max(arr[i], cur[i-1] + arr[i])`. The answer is the max over all
`cur[i]`. Optimal substructure + one variable = an elegant DP.

### Dry run

```python
def kadane(a):
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
# [-2,1,-3,4,-1,2,1,-5,4] -> 6  (subarray [4,-1,2,1])
```

### Edge cases (interview traps)

- **All negative** → the answer is the largest (least negative) element.
  Initialise `best = a[0]`, **not** `0`! (Common bug.)
- Empty array → define the behaviour.
- If you need the indices (not just the sum) → track start/end.

### Variants / follow-ups

- Maximum product subarray (LC 152 — track both min and max, since negative ×
  negative).
- Circular array maximum subarray (LC 918).
- Maximum sum with at most one deletion.

### MCQs

1. Initialising `best=0` on an all-negative array? → **bug**; use `best=a[0]`.
2. Kadane time/space? → **O(n) / O(1)**.

### Problems

- **Medium:** Maximum Subarray (53); Maximum Product Subarray (152); Maximum Sum
  Circular Subarray (918); Best Time to Buy & Sell Stock (121).

---

## 2.7 Dutch National Flag (3-way partition)

### Definition

Sort an array into three groups in **one pass** (classic: 0s, 1s, 2s). Designed
by Edsger Dijkstra. It is the basis of quicksort's 3-way partition.

### Intuition

Three pointers:

- `low` — the 0s region ends here
- `mid` — the element we are currently looking at (the scanner)
- `high` — the 2s region starts here

Look at `arr[mid]`: if `0` → swap with `low`, move both forward; if `1` → leave
it, `mid++`; if `2` → swap with `high`, `high--` (do **not** move `mid`, because
the swapped-in element has not been checked yet).

![Dutch flag: 0s on the left, 1s in the middle, 2s on the right — one pass, three pointers.](images/17_dutch_flag.png)

![Flowchart: the Dutch National Flag decision loop for 0s, 1s, and 2s.](images/24_fc_dutch.png)

### Brute force → Better → Optimal

```text
# BRUTE FORCE: just sort                      Time O(n log n), Space O(1)
sort(arr)

# BETTER: counting sort (two passes)          Time O(n), Space O(1), 2 passes
count zeros, ones, twos
overwrite arr with that many 0s, then 1s, then 2s

# OPTIMAL: Dutch national flag (one pass)      Time O(n), Space O(1), 1 pass
low = mid = 0; high = n-1
while mid <= high:
    if   arr[mid] == 0: swap(arr[low], arr[mid]); low++; mid++
    elif arr[mid] == 1: mid++
    else:               swap(arr[mid], arr[high]); high--
```

*Why it helps:* sorting ignores that there are only 3 values; counting needs two
passes; Dutch flag places every element correctly in a single pass.

### Dry run

```python
def sort012(a):
    low, mid, high = 0, 0, len(a) - 1
    while mid <= high:
        if a[mid] == 0:
            a[low], a[mid] = a[mid], a[low]; low += 1; mid += 1
        elif a[mid] == 1:
            mid += 1
        else:                       # a[mid] == 2
            a[high], a[mid] = a[mid], a[high]; high -= 1
    return a
# [2,0,2,1,1,0] -> [0,0,1,1,2,2]
```

### Complexity

- Time: **O(n)** (single pass), Space: **O(1)**

### Common mistakes

- Doing `mid++` after the `2`-swap (wrong — the swapped-in element is unchecked).
- Using `mid < high` instead of `mid <= high` (misses the last element).

### Interview perspective

- **Sort Colors (LC 75)** — very common; "one pass, O(1) space" is expected.

### MCQs

1. How many passes does Dutch flag use? → **one (1)**.
2. After a `2`-swap, do you advance `mid`? → **no**.

### Problems

- **Medium:** Sort Colors (75); partition an array around a pivot; Wiggle Sort.

---

## 2.8 Matrix Problems

### Common patterns

A matrix is a 2D array, internally often one 1D contiguous block (row-major:
`a[i][j]` = `a[i*cols + j]`).

#### Rotate image 90° (in place)

**Trick:** Transpose (swap rows and columns), then **reverse each row** = a 90°
clockwise rotation, with O(1) extra space.

![Rotate 90° clockwise = transpose + reverse each row, done in place.](images/18_matrix_rotate.png)

```text
# BRUTE FORCE: use a new matrix               Time O(n^2), Space O(n^2)
new[j][n-1-i] = old[i][j]

# OPTIMAL: in place                           Time O(n^2), Space O(1)
transpose: for i, for j>i: swap(a[i][j], a[j][i])
then reverse each row
```

```python
def rotate(m):
    n = len(m)
    for i in range(n):                      # transpose
        for j in range(i+1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    for row in m:                           # reverse each row
        row.reverse()
```

#### Other classics

- **Spiral traversal** (LC 54): shrink four boundaries (top/bottom/left/right).
- **Search in a sorted matrix** (LC 240): start at the top-right, O(m+n) — each
  step removes a row or a column.
- **Set matrix zeroes** (LC 73): use the first row/column as markers for O(1)
  extra space.

### Cache note

Iterate `a[i][j]` with `j` in the inner loop (row-major friendly) — Module 1's
cache lesson applies directly here (a 5–10× speed difference).

### Complexity

- Most matrix traversals: **O(n·m)** time.
- In-place rotate/zeroes: **O(1)** extra space (with the trick).

### MCQs

1. 90° clockwise rotate? → **transpose + reverse each row**.
2. Where do you start searching a sorted matrix? → **top-right** (or
   bottom-left).

### Problems

- **Medium:** Rotate Image (48); Spiral Matrix (54); Set Matrix Zeroes (73);
  Search 2D Matrix II (240); Game of Life (289).

---

## 2.9 More Essential Array Patterns (interview must-knows)

These three patterns appear constantly in interviews and GATE, and each has a
clean O(n) or O(n log n) trick worth memorising.

### A) Moore's Voting Algorithm — Majority Element

**Problem:** find the element that appears **more than n/2 times** (guaranteed to
exist).

**Intuition (memory hook — "tug of war"):** imagine two teams. Each majority
element is +1 for its team; every other element is −1. Keep a `candidate` and a
`count`. If the next element equals the candidate, `count++`; otherwise
`count--`. When `count` hits 0, adopt the current element as the new candidate.
Because the majority appears more than half the time, it always survives the
cancelling.

![Moore's voting: keep a candidate and a count; matching elements add, others subtract; the majority survives.](images/25_moore_voting.png)

```text
# BRUTE FORCE: count each value          Time O(n^2) or O(n) with a hashmap, Space O(n)
for each value: count occurrences; return the one with count > n/2

# OPTIMAL: Moore's voting                 Time O(n), Space O(1)
candidate = none; count = 0
for x in arr:
    if count == 0: candidate = x; count = 1
    elif x == candidate: count += 1
    else: count -= 1
return candidate          # (optional: verify with a second pass if not guaranteed)
```

- **Why it works:** pairing each majority element with a different element cancels
  pairs; since the majority is > n/2, at least one copy is left uncancelled.
- **Complexity:** O(n) time, O(1) space.
- **Edge case:** if the majority is *not* guaranteed, do a second pass to verify
  the candidate's count.
- **Problems:** Majority Element (LC 169); Majority Element II (LC 229 — keeps two
  candidates for elements > n/3).

### B) Merge Intervals

**Problem:** given intervals like `[[1,3],[2,6],[8,10]]`, merge all overlapping
ones → `[[1,6],[8,10]]`.

**Intuition (memory hook — "sort, then sweep"):** sort by **start**. Walk left to
right keeping the "current" interval. If the next interval starts **before or at**
the current end, they overlap → extend the current end. Otherwise close the
current interval and start a new one.

![Merge intervals: sort by start; if the next starts at/before the current end, extend; else start a new interval.](images/26_merge_intervals.png)

```text
# OPTIMAL                                 Time O(n log n) (sort) + O(n) sweep, Space O(n)
sort intervals by start
result = [ intervals[0] ]
for each next in intervals[1..]:
    if next.start <= result.last.end:           # overlap
        result.last.end = max(result.last.end, next.end)
    else:
        result.append(next)
return result
```

- **Key test:** overlap condition is `next.start <= current.end`.
- **Complexity:** dominated by the sort → O(n log n).
- **Problems:** Merge Intervals (LC 56); Insert Interval (LC 57); Non-overlapping
  Intervals (LC 435); Meeting Rooms I/II (LC 252/253).

### C) Cyclic Sort

**Problem family:** the array holds numbers from a known range **1..n** (or 0..n).
Find the missing number, the duplicate, or sort in O(n) without extra space.

**Intuition (memory hook — "everyone goes home"):** the number `v` belongs at
index `v-1` (its "home"). Walk the array; while the current element is not at its
home, **swap it to where it belongs**. After one pass, everything is in place,
and any index `i` whose value isn't `i+1` reveals a missing/duplicate number.

![Cyclic sort: each value v is swapped to its home index v-1; mismatches reveal missing/duplicate numbers.](images/27_cyclic_sort.png)

```text
# OPTIMAL                                 Time O(n), Space O(1)
i = 0
while i < n:
    home = arr[i] - 1                     # where arr[i] should sit
    if arr[i] != arr[home]:
        swap(arr[i], arr[home])          # send it home; do NOT advance i yet
    else:
        i += 1
# now scan: the first index i with arr[i] != i+1 gives the answer
```

- **Why O(n) despite the inner swaps:** each swap puts at least one number in its
  final home, so there are at most n swaps total.
- **Use when:** values are a contiguous range 1..n — this is the giveaway.
- **Problems:** Missing Number (LC 268); Find All Numbers Disappeared (LC 448);
  Find the Duplicate Number (LC 287); First Missing Positive (LC 41 — hard).

---

## Module 2 — Concept Review (one page)

- **Array** = contiguous block; access O(1) via `base + i*size`; cache-friendly.
- **Dynamic array** doubles when full → append O(1) amortised (proof:
  1+2+4+…+n = O(n) total).
- **Prefix sum** → range **query** O(1) (1D & 2D). **Difference array** → range
  **update** O(1).
- **Two pointers** → O(n²)→O(n) on sorted/monotonic input (pair sum, palindrome,
  3Sum).
- **Sliding window** → contiguous subarray/substring, O(n) (each element in/out
  once); fixed vs variable.
- **Kadane** → max subarray O(n)/O(1); init `best=a[0]` (all-negative trap).
- **Dutch flag** → 3-way partition, one pass, O(1) space.
- **Matrix** → rotate = transpose+reverse; spiral; sorted search from a corner.
- **Moore's voting** → majority (>n/2) in O(n)/O(1) (tug of war).
- **Merge intervals** → sort by start, then sweep merging overlaps.
- **Cyclic sort** → values in 1..n → put each at index value−1 (find missing/dup).

## Module 2 — Flash Cards

- Q: Append amortised cost & why? **A: O(1); doubling → 1+2+…+n = 2n.**
- Q: Range sum O(1)? **A: prefix sum, `pre[R+1]-pre[L]`.**
- Q: Range update O(1)? **A: difference array.**
- Q: Two pointers needs the array to be? **A: sorted/monotonic.**
- Q: Sliding window — why O(n)? **A: each element added & removed once.**
- Q: Kadane all-negative bug? **A: init best=a[0], not 0.**
- Q: Sort 0/1/2 in one pass? **A: Dutch national flag (3 pointers).**
- Q: Rotate 90° CW? **A: transpose + reverse rows.**
- Q: Majority element (>n/2) in O(1) space? **A: Moore's voting (tug of war).**
- Q: Merge overlapping intervals? **A: sort by start, sweep; overlap if next.start ≤ cur.end.**
- Q: Values are 1..n, find missing/duplicate in O(1) space? **A: cyclic sort.**

## Module 2 — Pattern Recognition (how to spot it in an interview)

- "Range sum / many queries" → **prefix sum**.
- "Range update many times" → **difference array**.
- "Sorted array + pair/triplet" → **two pointers**.
- "Longest/shortest contiguous subarray/substring with a condition" → **sliding
  window**.
- "Max contiguous sum" → **Kadane**.
- "Sort into a few categories in place" → **Dutch flag / partition**.
- "Subarray sum = k (unsorted)" → **prefix sum + hashmap** (Module 7).
- "Element appears more than n/2 times" → **Moore's voting**.
- "Overlapping intervals / merge / meeting rooms" → **sort + merge intervals**.
- "Array contains 1..n, find missing/duplicate, O(1) space" → **cyclic sort**.

## Module 2 — Interview Questions (with follow-ups)

1. *How is dynamic-array append O(1)?* FU: *what about +1 growth?* → O(n²).
2. *Make range sum O(1).* FU: *for 2D?* → inclusion-exclusion.
3. *Solve 3Sum.* FU: *handle duplicates; complexity?* → O(n²).
4. *Longest substring without repeats.* FU: *prove it is O(n).*
5. *Sort colors in one pass.* FU: *does it generalise to 4 colors?*
6. *Max subarray; the all-negative case?* FU: *also return the indices.*

## Module 2 — GATE / SEBI / RBI / ISRO Perspective

- **Common:** address calculation (`base + i*size`, the 2D row-major formula),
  amortised analysis of dynamic arrays, time complexity of insert/delete/search,
  prefix-sum reasoning. The 2D array address formula is a GATE favourite.

---

*End of Module 2. Next: Module 3 — Strings (hashing, KMP, Z-algorithm, Rabin-
Karp, Trie basics) — with visuals.*
