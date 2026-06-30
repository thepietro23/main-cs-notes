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

---

*End of Module 24. Next: Module 25 — Projects (build LRU cache, autocomplete, URL
shortener, mini-Git, scheduler, memory allocator, recommendation engine) — with
visuals.*
