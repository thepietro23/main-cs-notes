---
title: "Module 24 — Interview Question Bank"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 24 — Interview Question Bank

> **How to use this.**
> This is your consolidated **practice index** — the highest-value questions
> grouped by pattern (drawn from every module), plus the **follow-up framework**
> interviewers use to push you, and **debugging drills**. Track Solved / Revisit
> in the Excel **"Top 300"** tab. Quality of *reps* (timed, think-aloud, then
> review) beats raw count.

This module is **P0** for interview prep. (Curated lists: Blind 75 / Neetcode 150,
Module 20.)

---

## 24.1 Questions by Pattern (the core ~200)

### Arrays & Hashing
Two Sum (1) · Best Time to Buy/Sell Stock (121) · Contains Duplicate (217) ·
Product Except Self (238) · Maximum Subarray/Kadane (53) · Group Anagrams (49) ·
Top K Frequent (347) · Longest Consecutive Sequence (128) · Subarray Sum = K
(560) · Majority Element (169) · Merge Intervals (56) · Insert Interval (57) ·
Cyclic-sort family: Missing Number (268), Find Duplicate (287), First Missing
Positive (41).

### Two Pointers & Sliding Window
Valid Palindrome (125) · Two Sum II (167) · 3Sum (15) · Container With Most Water
(11) · Trapping Rain Water (42) · Sort Colors (75) · Longest Substring Without
Repeats (3) · Longest Repeating Char Replacement (424) · Min Window Substring
(76) · Permutation in String (567) · Fruit Into Baskets (904).

### Stack
Valid Parentheses (20) · Min Stack (155) · Daily Temperatures (739) · Next Greater
Element (496/503) · Largest Rectangle in Histogram (84) · Evaluate RPN (150) ·
Decode String (394) · Car Fleet (853) · Trapping Rain Water (42).

### Binary Search
Binary Search (704) · Search Rotated (33) · Find Min Rotated (153) · First/Last
Position (34) · Search 2D Matrix (74) · Koko Eating Bananas (875) · Ship Capacity
(1011) · Split Array Largest Sum (410) · Median of Two Sorted Arrays (4) · Find
Peak (162).

### Linked List
Reverse List (206) · Merge Two Sorted (21) · Linked List Cycle (141/142) · Reorder
List (143) · Remove Nth From End (19) · Copy List w/ Random Pointer (138) · Add
Two Numbers (2) · Merge K Sorted (23) · LRU Cache (146) · LFU Cache (460).

### Trees
Invert (226) · Max Depth (104) · Diameter (543) · Balanced (110) · Same Tree (100)
· Subtree (572) · Level Order (102) · Right Side View (199) · Validate BST (98) ·
Kth Smallest BST (230) · LCA (235/236) · Construct from Pre+In (105) ·
Serialize/Deserialize (297) · Binary Tree Max Path Sum (124).

### Tries & Strings
Implement Trie (208) · Add & Search Word (211) · Word Search II (212) · Longest
Palindromic Substring (5) · Palindromic Substrings (647) · Encode/Decode Strings
(271) · KMP/Z (find pattern) · Longest Common Prefix (14).

### Heap / Priority Queue
Kth Largest (215) · Top K Frequent (347) · K Closest Points (973) · Task Scheduler
(621) · Find Median from Stream (295) · Merge K Lists (23) · Reorganize String
(767).

### Backtracking
Subsets (78/90) · Permutations (46/47) · Combination Sum (39/40) · Word Search
(79) · Palindrome Partitioning (131) · N-Queens (51/52) · Sudoku Solver (37) ·
Generate Parentheses (22) · Letter Combinations (17).

### Graphs
Number of Islands (200) · Clone Graph (133) · Course Schedule (207/210) · Pacific
Atlantic (417) · Rotting Oranges (994) · Word Ladder (127) · Number of Connected
Components (323) · Redundant Connection (684) · Network Delay (743) · Cheapest
Flights K Stops (787) · Alien Dictionary (269) · Min Cost Connect Points (1584) ·
Critical Connections/bridges (1192).

### Dynamic Programming
Climbing Stairs (70) · House Robber (198/213) · Coin Change (322/518) · LIS (300)
· Word Break (139) · LCS (1143) · Unique Paths (62/63) · Min Path Sum (64) · Edit
Distance (72) · Partition Equal Subset (416) · Target Sum (494) · Longest
Palindromic Subseq (516) · Max Product Subarray (152) · Decode Ways (91) · Burst
Balloons (312) · Best Time Buy/Sell w/ Cooldown (309).

### Greedy / Intervals / Math / Bit
Jump Game I/II (55/45) · Gas Station (134) · Candy (135) · Partition Labels (763)
· Non-overlapping Intervals (435) · Meeting Rooms II (253) · Min Arrows (452) ·
Single Number (136/137/260) · Number of 1 Bits (191) · Counting Bits (338) · Sum
of Two Integers (371) · Pow(x,n) (50) · Count Primes (204) · Happy Number (202) ·
Rotate Image (48) · Spiral Matrix (54).

> **That's ~200 high-signal problems.** Doing these well (and their follow-ups)
> covers the overwhelming majority of FAANG questions. Expand toward 300+ via
> Neetcode 150 + company tags.

---

## 24.2 The Follow-Up Ladder (how interviewers push)

For *any* problem, expect this escalation — prepare for it:

1. **"Can you do better?"** → brute force → optimal (better time/space).
2. **"What's the complexity?"** → state time **and** space, justify.
3. **"What about edge cases?"** → empty, size 1, duplicates, overflow, negatives,
   max bounds.
4. **"Optimise space."** → 2D→1D DP, O(1) two-pointer, in-place.
5. **"What if the input is huge / streaming / distributed?"** → external sort,
   heap-of-k, sharding, approximate (Bloom/HLL).
6. **"What if it's sorted / already partly solved / updates come live?"** → binary
   search / segment tree / incremental.
7. **"Write tests / find the bug."** → debugging round.

> **Memory hook:** every answer should pre-empt "can you do better, and what does
> it cost?"

---

## 24.3 Debugging Exercises (a real interview round)

Common planted bugs to train your eye:

- **Off-by-one:** loop `<= n` vs `< n`; binary search `lo<hi` vs `lo<=hi`;
  `mid` vs `mid±1`.
- **Integer overflow:** `(lo+hi)/2`; `n*n` in 32-bit; missing `long`.
- **Uninitialised / wrong init:** Kadane `best=0` on all-negative (should be
  `a[0]`); DP base cases.
- **Mutation while iterating:** modifying a list/map during a loop.
- **Reference vs copy:** recording `path` by reference in backtracking (must
  snapshot).
- **Null/empty:** unchecked `head.next`, empty array, root null.
- **Recursion:** missing/never-reached base case → stack overflow.
- **Hash/equality:** using mutable keys; floating-point `==`.
- **Loop direction:** 0/1-knapsack 1D must go right-to-left.

**Drill:** take a working solution, *intentionally* introduce one of these, and
practice spotting it fast — that's exactly the debugging round.

---

## 24.3a Dry-Run Output Questions (SEBI Phase-2 style — with answers)

SEBI Phase-2 (and GATE) love **"what does this print?"** questions. You are given
a small snippet and must **hand-trace** it. The trick: keep a tiny table of
variables per iteration — do NOT trace in your head. Below are worked examples;
cover the answer, trace on paper, then check.

**Q1 — off-by-one loop.** What does this print?

```text
int s = 0;
for (int i = 1; i <= 5; i++) s += i;
print(s);
```

*Trace:* i=1→s=1, i=2→s=3, i=3→s=6, i=4→s=10, i=5→s=15. Loop is `<=5`, so i=5
runs. **Answer: 15.** (If it were `< 5`, the answer would be 10 — this is the
classic off-by-one trap.)

**Q2 — pass-by-reference vs value.** What does this print?

```text
void f(int[] a) { a[0] = 99; }      // arrays passed by reference
int[] x = {1, 2, 3};
f(x);
print(x[0]);
```

*Trace:* the array reference is shared, so `f` mutates the caller's array.
**Answer: 99.** (A plain `int` passed by value would stay unchanged — know the
difference for your language.)

**Q3 — recursion return value.** What does `g(4)` return?

```text
int g(int n) {
    if (n <= 1) return 1;
    return n * g(n - 1);
}
```

*Trace:* g(4)=4·g(3)=4·3·g(2)=4·3·2·g(1)=4·3·2·1. **Answer: 24** (this is 4!).
Base case `n<=1` returns 1, so g(1)=1 stops the recursion.

**Q4 — post-increment in an expression.** What does this print?

```text
int i = 0;
int a = i++;      // post: use old value, then increment
int b = ++i;      // pre: increment first, then use
print(a, b, i);
```

*Trace:* `a = i++` → a takes the **old** i (0), then i becomes 1. `b = ++i` → i
becomes 2 first, then b takes 2. **Answer: a=0, b=2, i=2.**

**Q5 — integer division and modulo.** What does this print?

```text
for (int n = 13; n > 0; n = n / 2)
    print(n % 2);
```

*Trace:* n=13→1, n=6→0, n=3→1, n=1→1, then n=0 stops. Prints `1 0 1 1` — this is
13 in binary read **least-significant-bit first**. **Answer: 1 0 1 1.**
(13 = 1101₂; the loop emits bits LSB→MSB.)

**Q6 — reference aliasing bug (spot the output).** What does this print?

```text
list outer = [];
list row = [0, 0];
for (int i = 0; i < 3; i++) {
    row[0] = i;
    outer.append(row);       // BUG: appends the SAME row reference 3 times
}
print(outer);
```

*Trace:* every `append` stores the **same** list object, and the final loop sets
`row[0] = 2`. So all three entries point to that one mutated list.
**Answer: `[[2,0], [2,0], [2,0]]`** — not `[[0,0],[1,0],[2,0]]`. The fix is to
append a **copy** (`row.clone()`), the same snapshot pitfall as backtracking.

> **Memory hook:** for dry-run questions, *write a variable table row per
> iteration.* Speed comes from neatness, not from tracing in your head.

---

## 24.4 GATE/SEBI-style Conceptual MCQ Bank (samples)

(Each module's "MCQs" section is your per-topic bank — ~150+ across M1–M23. A few
cross-cutting samples:)

1. Worst case of quicksort, and the input that triggers it? → O(n²); sorted input
   w/ first/last pivot.
2. Build-heap from n elements? → **O(n)**.
3. Which shortest-path algorithm handles negative edges? → **Bellman-Ford**.
4. Inorder traversal of a BST yields? → **sorted order**.
5. Hash table average vs worst lookup? → **O(1) / O(n)**.
6. Master Theorem: `2T(n/2)+n`? → **Θ(n log n)**.
7. NP-complete means? → in NP **and** every NP problem reduces to it.
8. B+ tree vs hash index — which supports range queries? → **B+ tree**.
9. Amortized cost of dynamic-array append? → **O(1)**.
10. Minimum spanning tree algorithms? → **Kruskal, Prim**.

**More samples (with a one-line *why*):**

11. Time to build a heap by repeated `heapify` bottom-up? → **O(n)**. *Why:* the
    cost sums to `Σ n/2^h · h`, a convergent series ≈ 2n — most nodes are near the
    leaves and sift down very little.
12. Time to sort using a heap (heapsort)? → **O(n log n)**. *Why:* build-heap is
    O(n), but the n extract-max operations each cost O(log n).
13. Best-case comparisons for binary search on n elements? → **1** (target is at
    `mid`); worst case **⌊log₂ n⌋ + 1**.
14. Stable sorts among merge / quick / heap? → **only merge sort** (of the three).
    *Why:* quicksort and heapsort can reorder equal keys.
15. DFS on a graph is typically implemented with a? → **stack** (or recursion);
    BFS uses a **queue**.
16. Which traversal of a BST gives keys in sorted order? → **inorder**; a
    **reverse** inorder (right→root→left) gives descending order.
17. A complete binary tree with n nodes has height? → **⌊log₂ n⌋** (**O(log n)**).
18. Preferred collision resolution when the load factor stays low and cache
    locality matters? → **open addressing** (linear/quadratic probing).
19. Recurrence `T(n) = 2T(n/2) + O(1)` solves to? → **O(n)** (Master Theorem
    case 1: leaves dominate). Contrast with `2T(n/2)+O(n)` → **O(n log n)**.
20. Topological sort is possible **iff** the graph is a? → **DAG** (no cycle).

---

## 24.4a How to Attempt MCQs Under Time Pressure

SEBI/GATE objective sections give you roughly **a minute or less per question**.
Speed comes from a routine, not from rushing. Use this order:

1. **Two-pass sweep.** Pass 1: answer every question you *know* in under ~30s and
   flag the rest. Pass 2: return to the flagged ones with the time you saved. Never
   let one hard MCQ eat five easy ones' worth of time.
2. **Read the stem for the trap word.** Circle `NOT`, `EXCEPT`, `always`, `never`,
   `worst-case`, `average-case`. Most wrong answers are right for a *different*
   qualifier (e.g. quicksort is O(n log n) *average* but O(n²) *worst*).
3. **Eliminate, don't just pick.** Cross out the obviously-wrong options first; two
   of four are usually easy to reject, doubling your odds if you must guess.
4. **Sanity-check complexity claims with a tiny n.** Plug n=2 or n=4 into the
   formula/recurrence; a wrong option often breaks immediately.
5. **Trust the standard result.** Build-heap O(n), hash worst-case O(n), inorder =
   sorted, Bellman-Ford for negatives — these recur every year. Memorise the
   §24.4 bank and the Module 26 cheat sheet cold.
6. **Guess if there's no negative marking; skip only if there is.** Know your
   exam's marking scheme *before* the day and set your risk accordingly.
7. **Watch the clock in thirds.** At 1/3 time you should be ~1/3 done; if not,
   speed up on recognition questions and stop over-verifying.

> **Memory hook:** *Easy first, flag the rest, watch for the trap word.*

---

## Module 24 — How to Practice (one page)

- **Breadth first:** one pass over all patterns (§24.1) — recognise, don't
  memorise.
- **Timed reps:** 35–45 min/problem, **think aloud**, then read the editorial and
  **redo**.
- **Follow-up drill:** for each solved problem, answer the §24.2 ladder.
- **Weakness log:** record every miss + *why*; re-drill weekly.
- **Mock interviews:** Pramp / peers — practise the *communication*, not just the
  code.
- Track everything in the **Excel Top-300 tab**; aim for ~60–70% green before
  interviews.

## Module 24 — Flash Cards

- Q: How many high-signal problems cover most interviews? **A: ~200 (then 300+).**
- Q: Universal follow-up? **A: "can you do better, and what does it cost?"**
- Q: Practice format? **A: timed + think-aloud + redo + weakness log.**
- Q: Where to track? **A: Excel Top-300 tab.**
- Q: Best way to trace a dry-run question? **A: a variable table, one row per
  iteration — never in your head.**
- Q: MCQ time strategy? **A: easy first, flag the rest, watch for the trap word
  (NOT/EXCEPT/worst-case).**
- Q: `for (n=13; n>0; n/=2) print(n%2)` prints? **A: 1 0 1 1 (bits of 13, LSB
  first).**

---

*End of Module 24. Next: Module 25 — Projects (build LRU cache, autocomplete, URL
shortener, mini-Git, scheduler, memory allocator, recommendation engine) — with
visuals.*
