---
title: "Module 8b — Trees: Balanced & Range Trees"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8b — Trees: Balanced & Range Trees

> **Why this part matters.**
> M08a showed that a BST is fast *only when balanced* — sorted inserts turn it
> into a slow O(n) chain. This part shows the **self-balancing** trees (AVL,
> Red-Black) that guarantee O(log n) forever, and the **range-query** trees
> (Segment, Fenwick) and **disk-based** trees (B, B+) that power competitive
> programming and real databases.

This module is **P1–P2**: AVL/Red-Black and segment/Fenwick are GATE + CP
favourites; B/B+ trees are core for DBMS exams and system-design interviews.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

---

## 8b.1 AVL Trees (height-balanced BST)

### The idea

An **AVL tree** is a BST that keeps itself balanced after every insert/delete. For
each node it tracks a **balance factor**:

```
balance factor = height(left subtree) − height(right subtree)
```

It must stay in **{−1, 0, +1}**. If an insert/delete pushes it to ±2, a
**rotation** restores balance.

![AVL rotation: a left-heavy (LL) node is fixed by a single right rotation, restoring balance.](images/67_avl_rotation.png)

### The four rotation cases

| Case | Shape | Fix |
|---|---|---|
| **LL** | left-left heavy | single **right** rotation |
| **RR** | right-right heavy | single **left** rotation |
| **LR** | left-right heavy | left rotate child, then right rotate |
| **RL** | right-left heavy | right rotate child, then left rotate |

> **Memory hook:** the case name tells you the heavy path; "single" rotations fix
> straight lines (LL/RR), "double" rotations fix zig-zags (LR/RL).

### Complexity

| Operation | Time |
|---|---|
| search / insert / delete | **O(log n)** guaranteed |

AVL stays **strictly** balanced (height ≈ 1.44 log n), so lookups are very fast.
The cost: more rotations on insert/delete than a Red-Black tree.

### MCQs

1. AVL balance factor allowed values? → **−1, 0, +1**.
2. LL imbalance fix? → single **right** rotation.
3. AVL guaranteed height? → **O(log n)**.

---

## 8b.2 Red-Black Trees (the practical balancer)

### The idea

A **Red-Black tree** is a BST where each node is coloured **red or black**, and a
set of colour rules keeps it *roughly* balanced — height ≤ **2·log₂(n+1)**.

![Red-Black tree: colour rules (no two reds in a row, equal black-height on every path) keep it balanced.](images/68_redblack.png)

### The five rules

1. Every node is **red or black**.
2. The **root is black**.
3. All leaves (NULL) are **black**.
4. A **red node's children are black** (no two reds in a row).
5. **Every path** from a node down to a NULL leaf has the **same number of black
   nodes** (the "black height").

### AVL vs Red-Black (a great interview comparison)

| | AVL | Red-Black |
|---|---|---|
| Balance | strict (faster lookups) | looser (taller, but fine) |
| Insert/delete | more rotations | fewer rotations |
| Best for | lookup-heavy | insert/delete-heavy |
| Real use | databases (some) | **Linux scheduler (CFS), `std::map`, Java `TreeMap`** |

> **Memory hook:** Red-Black trades a little extra height for **fewer rotations**,
> which is why general-purpose libraries prefer it.

### MCQs

1. Can a red node have a red child? → **no**.
2. What is equal on every root-to-leaf path? → the **black height**.
3. Which real systems use Red-Black trees? → **Linux CFS, C++ `std::map`, Java
   `TreeMap`**.

---

## 8b.3 Segment Tree (range queries + updates)

### The problem it solves

Recall (Module 2): a **prefix sum** answers range-sum queries in O(1), but a
single element update forces an O(n) rebuild. A **segment tree** handles **both**
range queries *and* updates in **O(log n)**.

### The idea

Build a binary tree where each node stores an **aggregate** (sum / min / max /
gcd…) of a range. The root covers the whole array; each child covers half.

![Segment tree: each node stores the aggregate of a range; queries and updates touch O(log n) nodes.](images/69_segment_tree.png)

```text
build:   O(n)              # array of size ~4n
query(L,R):  O(log n)      # combine a few covering segments
update(i,v): O(log n)      # update the leaf, then fix ancestors
```

- **Lazy propagation** extends this to **range updates** (e.g. "add 5 to all of
  [L,R]") in O(log n) by deferring updates to children until needed.

### Prefix sum vs Segment tree vs Fenwick (when to use what)

| Need | Best tool |
|---|---|
| Range query, **no updates** | **Prefix sum** (O(1) query) |
| Range **sum** query + point/range updates | **Fenwick (BIT)** — compact |
| Range **min/max/gcd/...** + updates | **Segment tree** (more general) |

### MCQs

1. Segment tree query/update time? → **O(log n)**.
2. What enables range *updates* in O(log n)? → **lazy propagation**.
3. Prefix sum's weakness that a segment tree fixes? → **slow (O(n)) updates**.

### Problems

- Range Sum Query – Mutable (LC 307); Range Minimum Query; Count of Smaller
  Numbers After Self (LC 315); many CP range problems.

---

## 8b.4 Fenwick Tree / Binary Indexed Tree (BIT)

### The idea

A **Fenwick tree** is a compact array that supports **prefix-sum query** and
**point update**, both in **O(log n)**, using a neat **lowest-set-bit** trick.

![Fenwick tree: jump by the lowest set bit (i & −i) to cover a prefix in O(log n) steps.](images/70_fenwick.png)

```text
update(i, delta):  while i <= n: tree[i] += delta; i += i & (-i)
prefix_sum(i):     s = 0; while i > 0: s += tree[i]; i -= i & (-i); return s
range_sum(L,R) = prefix_sum(R) - prefix_sum(L-1)
```

- **`i & (-i)`** isolates the lowest set bit — the size of the range each index
  is responsible for.
- **Fenwick vs Segment tree:** Fenwick is smaller, faster, simpler to code, but
  mainly for **invertible** operations (sums/counts). Segment tree is more
  general (min/max) and supports lazy range updates.

> **Memory hook:** jump by **powers of two** — a prefix of length n is covered in
> ~log n binary "hops".

### MCQs

1. Fenwick update/query time? → **O(log n)**.
2. What does `i & (-i)` give? → the **lowest set bit**.
3. Fenwick vs segment tree trade-off? → smaller/simpler **but** mainly for
   sums (invertible ops).

### Problems

- Range Sum Query – Mutable (307); Count of Smaller Numbers After Self (315);
  Reverse Pairs (493).

---

## 8b.5 B-Trees and B+ Trees (disk / database trees)

### Why they exist

A binary tree node holds one key → for billions of records on **disk**, that is
billions of slow disk reads. A **B-tree** is an **m-way** balanced tree: each
node holds **many keys** and has **many children**, so the tree is **wide and
shallow** — fewer levels means fewer disk reads.

![B+ tree: a wide, shallow tree; all data lives in linked leaves while internal nodes hold only keys.](images/71_bplus_tree.png)

### B-tree vs B+ tree

| | B-tree | B+ tree |
|---|---|---|
| Data stored | in **all** nodes | only in **leaves** |
| Leaves | not linked | **linked list** (fast range scans) |
| Internal nodes | keys + data | **keys only** (so they hold more keys) |
| Used by | some file systems | **MySQL/Postgres indexes, NTFS** |

- **Why B+ for databases:** keys-only internal nodes pack more keys per node →
  even shallower tree; linked leaves make **range scans** (`WHERE age BETWEEN…`)
  fast.
- Operations are O(log n), but with a **large base** (branching factor m), so the
  height is tiny (often 3–4 levels for millions of rows).

> **Memory hook:** B+ tree = a **library catalogue**: the index cards (internal
> nodes) only point you toward the shelves; the actual books (data) sit on the
> linked shelves (leaves) you can walk along.

### MCQs

1. Why do databases use B+ trees over binary trees? → **wide & shallow → fewer
   disk reads**; linked leaves → fast range scans.
2. Where is the data in a B+ tree? → only in the **leaves**.
3. B-tree vs B+ tree key difference? → B+ keeps data **only in leaves** and
   **links** them.

### Problems / context

- Mostly **DBMS + system design**: index design, "why B+ tree not hash index"
  (range queries!), page size and branching factor.

---

## Module 8b — Concept Review (one page)

- **AVL:** strict balance (bf ∈ {−1,0,+1}); 4 rotation cases (LL/RR single,
  LR/RL double); O(log n), lookup-friendly.
- **Red-Black:** colour rules (no two reds; equal black-height) → height ≤
  2·log(n+1); fewer rotations → used by Linux CFS, `std::map`, Java `TreeMap`.
- **Segment tree:** range query **and** update in O(log n); lazy propagation for
  range updates; general (sum/min/max).
- **Fenwick/BIT:** compact prefix-sum + point update O(log n) via `i & (-i)`;
  best for sums.
- **B/B+ trees:** wide, shallow, disk-friendly; B+ keeps data in **linked
  leaves** → database indexes (MySQL/Postgres).
- **Tool choice:** no updates → prefix sum; sum + updates → Fenwick; min/max +
  updates → segment tree; on-disk ordered data → B+ tree.

## Module 8b — Flash Cards

- Q: AVL balance factor range? **A: {−1, 0, +1}.**
- Q: LR imbalance fix? **A: double rotation (left then right).**
- Q: Red node's children? **A: must be black (no two reds).**
- Q: Red-Black real uses? **A: Linux CFS, std::map, Java TreeMap.**
- Q: Segment tree query/update? **A: O(log n) (lazy → range updates).**
- Q: Fenwick lowest-set-bit op? **A: i & (-i).**
- Q: Where is B+ tree data? **A: only in linked leaves.**

## Module 8b — Pattern Recognition

- "Ordered set with guaranteed fast ops" → **balanced BST (AVL / Red-Black)**.
- "Range sum, no updates" → **prefix sum**; "+ point updates" → **Fenwick**.
- "Range min/max/gcd with updates" → **segment tree** (+ lazy for range updates).
- "Billions of records on disk / database index / range scan" → **B+ tree**.

## Module 8b — Interview Questions (with follow-ups)

1. *Why does a BST need balancing?* FU: *AVL vs Red-Black trade-offs.*
2. *Design a structure for range-sum with updates.* FU: *Fenwick vs segment
   tree.*
3. *Why do databases use B+ trees, not hash indexes?* FU: *range queries.*
4. *Implement a segment tree.* FU: *add lazy propagation for range updates.*

## Module 8b — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** AVL **rotations and balance factors** (trace insertions),
  Red-Black properties, **B/B+ tree order, number of keys/children, and
  insertions/splits** (very frequently asked in DBMS too), segment/Fenwick
  complexity.
- **SEBI/RBI IT + DBMS:** B/B+ tree indexing is a core topic — see the DBMS notes.

---

*End of Module 8b. Next: Module 9 — Heaps (binary heap deep-dive, heapsort,
Fibonacci/pairing heaps, applications) — with visuals.*
