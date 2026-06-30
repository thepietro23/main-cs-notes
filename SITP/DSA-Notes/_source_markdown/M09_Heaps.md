---
title: "Module 9 — Heaps (deep dive)"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 9 — Heaps (deep dive)

> **Why a second heap module?**
> Module 6 introduced the **binary heap** and its everyday uses (priority queue,
> top-K, merge-K, streaming median). This module goes **deeper**: the **O(n)
> build-heap proof** (a GATE classic), **heapsort**, **d-ary heaps**, and the
> **advanced heaps** (binomial, Fibonacci, pairing) that make algorithms like
> Dijkstra theoretically faster. Treat M6 as "how to use", M9 as "how it works
> and its frontiers".

This module is **P1** (heapsort, build-heap proof — GATE) and **P2** (advanced
heaps — theory + CP).

> **Recap (Module 6):** a **binary heap** is a complete tree stored in an array;
> `parent=(i−1)/2`, `children=2i+1, 2i+2`; push/pop O(log n), peek O(1).

---

## 9.1 Build-Heap in O(n) (the proof everyone gets wrong)

### The claim

Turning an unsorted array into a heap by **sifting down** from the last internal
node up to the root is **O(n)** — *not* O(n log n).

![Build-heap is O(n): most nodes are leaves (zero work); only the few top nodes sift far.](images/73_build_heap.png)

### Why (the intuition + the math)

If you instead **insert** n items one by one, each insert is O(log n) → O(n log n).
But **bottom-up build** is cheaper because **work depends on a node's height, and
most nodes are near the bottom** (cheap):

- ~n/2 nodes are leaves → **0** work each.
- ~n/4 nodes sift down at most **1** level.
- ~n/8 nodes sift down at most **2** levels, and so on.

Total work `= n·(1/2·0 + 1/4·1 + 1/8·2 + …) = n · Σ (k / 2^(k+1))`. That sum
converges to a **constant (≈1)**, so the total is **O(n)**. ∎

> **Memory hook:** the expensive nodes (near the root) are **few**; the cheap
> nodes (leaves) are **many**. The cheap ones dominate the count, so the average
> is constant.

### MCQs

1. Build-heap time bottom-up? → **O(n)**.
2. Insert-one-by-one heap build? → **O(n log n)**.
3. Why is bottom-up cheaper? → most nodes are **leaves** (≈0 work).

---

## 9.2 Heapsort

### The idea

Sort by using a heap: **build a max-heap**, then repeatedly **swap the root
(largest) with the last element**, shrink the heap by one, and **sift down** the
new root. After n steps the array is sorted — **in place**.

![Heapsort: build a max-heap, then repeatedly move the max to the end and sift down.](images/72_heapsort.png)

```text
# Heapsort                                   Time O(n log n), Space O(1)
build_max_heap(a)                  # O(n)
for end = n-1 downto 1:
    swap(a[0], a[end])             # largest goes to its final spot
    sift_down(a, 0, end)           # restore heap on a[0..end-1]
```

### Heapsort vs other sorts (interview comparison)

| | Heapsort | Quicksort | Merge sort |
|---|---|---|---|
| Worst case | **O(n log n)** | O(n²) | O(n log n) |
| Space | **O(1)** in place | O(log n) | O(n) |
| Stable? | No | No | Yes |
| Cache | poor (jumps) | great | good |

- **Use heapsort when** you need guaranteed O(n log n) **and** O(1) space.
  Quicksort is usually faster in practice (cache), so it's the common default.

### MCQs

1. Heapsort time & space? → **O(n log n) / O(1)**.
2. Is heapsort stable? → **no**.
3. Heapsort's edge over quicksort? → **O(n log n) worst case** + O(1) space.

---

## 9.3 d-ary Heaps (a practical tweak)

A **d-ary heap** gives each node **d children** instead of 2. This makes the tree
**shallower** (height `log_d n`), so **decrease-key / insert** are faster, but
**extract-min** compares among d children (more work). A **4-ary heap** is often
fastest in practice for Dijkstra due to better cache behaviour.

> **Memory hook:** more children = shorter tree = faster pushes, slightly slower
> pops. Tune `d` to your workload.

### MCQs

1. Height of a d-ary heap? → **log_d n**.
2. Trade-off of larger d? → faster insert/decrease-key, slower extract-min.

---

## 9.4 Advanced Heaps (binomial, Fibonacci, pairing)

These exist to make **merge (union)** and **decrease-key** cheap — operations a
binary heap does in O(log n) or O(n).

![Heap variants and their amortised costs: Fibonacci heaps give O(1) insert, merge, and decrease-key.](images/74_advanced_heaps.png)

| Operation | Binary | Binomial | **Fibonacci** |
|---|---|---|---|
| insert | O(log n) | O(log n) | **O(1)** |
| find-min | O(1) | O(log n) | **O(1)** |
| extract-min | O(log n) | O(log n) | O(log n) amort. |
| **decrease-key** | O(log n) | O(log n) | **O(1) amort.** |
| **merge** | O(n) | O(log n) | **O(1)** |

### Why this matters: Dijkstra

Dijkstra's shortest-path (Module 10) does many **decrease-key** operations. With a
**binary heap** it is `O((V+E) log V)`; with a **Fibonacci heap** the O(1)
amortised decrease-key gives the theoretical best **`O(E + V log V)`**.

> **Reality check (say this in interviews):** Fibonacci heaps have **large hidden
> constants** and are complex, so in practice a **binary heap** (or 4-ary heap)
> usually wins. Fibonacci heaps are mostly a **theoretical** result.

- **Pairing heap:** much simpler than Fibonacci, great real-world performance,
  decrease-key O(log n) amortised (conjectured better). A common practical choice.
- **Binomial heap:** a forest of binomial trees; mergeable in O(log n).

### MCQs

1. Which heap gives O(1) amortised decrease-key? → **Fibonacci**.
2. Dijkstra with a Fibonacci heap? → **O(E + V log V)**.
3. Why aren't Fibonacci heaps used much in practice? → **large constants /
   complexity**.

---

## Module 9 — Concept Review (one page)

- **Build-heap = O(n)** (not O(n log n)): most nodes are leaves; Σ k/2^k
  converges to a constant.
- **Heapsort:** build max-heap, repeatedly swap root→end + sift down; **O(n log
  n), O(1) space**, not stable, poor cache.
- **d-ary heap:** d children → height log_d n; faster insert, slower extract-min;
  4-ary often best for Dijkstra.
- **Advanced heaps:** binomial (mergeable O(log n)), **Fibonacci** (O(1) insert/
  merge/decrease-key amortised → Dijkstra O(E+V log V) in theory), pairing
  (simple + fast in practice).
- **In practice:** binary or 4-ary heaps win; Fibonacci is mostly theory.

## Module 9 — Flash Cards

- Q: Build-heap time & why? **A: O(n); leaves dominate, Σ k/2^k = const.**
- Q: Heapsort time/space/stable? **A: O(n log n) / O(1) / not stable.**
- Q: d-ary heap height? **A: log_d n.**
- Q: O(1) amortised decrease-key heap? **A: Fibonacci.**
- Q: Dijkstra with Fibonacci heap? **A: O(E + V log V).**
- Q: Why Fibonacci heaps rare in practice? **A: huge constants.**

## Module 9 — Pattern Recognition

- "Sort with guaranteed O(n log n) + O(1) space" → **heapsort**.
- "Lots of decrease-key (Dijkstra/Prim)" → heap choice matters (binary/4-ary in
  practice, Fibonacci in theory).
- "Merge many heaps cheaply" → **binomial / Fibonacci / pairing**.

## Module 9 — Interview Questions (with follow-ups)

1. *Prove build-heap is O(n).* FU: *why is insert-based build O(n log n)?*
2. *Implement heapsort.* FU: *max-heap vs min-heap; stability?*
3. *Which heap for Dijkstra and why?* FU: *Fibonacci theory vs practice.*

## Module 9 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** **build-heap O(n)** result, heapsort complexity & number
  of comparisons, heap array indexing, min/max-heap tracing. Very frequently
  tested.
- **Advanced heaps** appear in algorithm-analysis questions (amortised costs).

---

*End of Module 9. Next: Module 10 — Graphs (representation, BFS/DFS, topological
sort, union-find, shortest paths, MST, advanced) — split across M10a/b/c, with
visuals.*
