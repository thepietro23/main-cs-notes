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

### The four rotations, before → after

![The four AVL rotation cases (LL, RR, LR, RL) shown before and after — the balanced middle value always ends up on top.](images/190_avl_four_rotations.png)

Notice the pattern: in **every** case the fix promotes the **middle of the three
values** to the top, with the smaller value on its left and the larger on its
right. That is why the result is always balanced.

#### Worked trace: inserting 1, 2, 3 (an RR case)

```text
insert 1:   1              bf(1)=0, fine
insert 2:   1              bf(1) = 0 - 1 = -1, still fine
             \
              2
insert 3:   1   bf(1) = -2  -> RIGHT-RIGHT heavy -> single LEFT rotation
             \
              2
               \
                3
after LEFT rotation about 1:
                2          balanced: bf(2)=0
               / \
              1   3
```

#### Worked trace: inserting 3, 1, 2 (an LR case, the tricky one)

```text
insert 3:   3
insert 1:   3      (left child)
           /
          1
insert 2:   3     bf(3) = +2, and the heavy path goes LEFT then RIGHT -> LR
           /
          1
           \
            2
Step 1 - LEFT-rotate the left child (1):    3
                                           /
                                          2
                                         /
                                        1
Step 2 - RIGHT-rotate the root (3):       2
                                         / \
                                        1   3   -> balanced (bf=0 everywhere)
```

- **Why two rotations for LR/RL:** a single rotation on a zig-zag just turns it
  into the *other* zig-zag — it does not shorten the tree. The first rotation
  straightens the zig-zag into a straight line; the second then fixes it like an
  LL/RR case.

### AVL insert: the fix-up procedure

```text
insert like an ordinary BST, then walk back up to the root:
  at each ancestor, update its height
  compute balance factor bf = height(left) - height(right)
  if bf == +2:  (left heavy)
      if the new key went into the LEFT-LEFT  -> single right rotation
      else (LEFT-RIGHT)                       -> left-rotate child, then right
  if bf == -2:  (right heavy)
      if RIGHT-RIGHT -> single left rotation
      else (RIGHT-LEFT) -> right-rotate child, then left
```

- On **insert**, exactly **one** rotation (single or double) restores the whole
  tree. On **delete**, you may need up to **O(log n)** rotations climbing up.

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
4. LR case fix? → **double** rotation (left-rotate child, then right-rotate).
5. Rotations to fix one AVL **insert**? → at most **one** (single or double).
6. Value that ends up on top after any rotation? → the **middle** of the three.

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

### Why these rules force O(log n) height

Two rules do the heavy lifting together:

- Rule 5 says every root-to-leaf path has the **same black count** — so all paths
  are "black-equal".
- Rule 4 says **no two reds in a row** — so on any path, reds are at most half the
  nodes; a path can be at most **twice** as long as an all-black path.

Let `b` = black height. The shortest possible path is all black (length `b`); the
longest alternates red/black (length ≤ `2b`). So the longest path is at most
**twice** the shortest → the tree is "balanced enough". Working the counting out
gives height **≤ 2·log₂(n+1)**, hence **O(log n)** search/insert/delete.

> **Memory hook:** "same black on every path" + "no red-red" ⇒ longest path ≤
> **2×** shortest ⇒ height stays logarithmic.

- **Repair cost:** inserts/deletes are fixed with **recolouring** (cheap) plus at
  most **O(1) rotations** for insert (up to O(log n) recolourings while climbing).
  That is the practical win over AVL: fewer structural rotations.

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
4. Why is a Red-Black tree's height O(log n)? → longest path ≤ **2×** shortest
   (no red-red + equal black-height) → height ≤ **2·log₂(n+1)**.
5. Red-Black insert repair cost? → recolour + at most **O(1)** rotations.

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

#### Worked example: build, query, update (sum tree)

Array `A = [2, 1, 5, 3]` (indices 0..3). Each node stores the **sum** of its
range `[lo,hi]`:

```text
                 [0..3]=11
                /         \
         [0..1]=3         [2..3]=8
         /     \          /      \
   [0..0]=2 [1..1]=1  [2..2]=5 [3..3]=3
```

**Query sum of [1..3]** (expected 1+5+3 = 9):

```text
start at root [0..3]: partial overlap -> recurse both children
  [0..1]: partial -> recurse
     [0..0]: no overlap with [1..3] -> return 0
     [1..1]: fully inside [1..3]    -> return 1
  [2..3]: fully inside [1..3]       -> return 8      (no need to go deeper)
total = 0 + 1 + 8 = 9   (touched only O(log n) nodes)
```

**Point update: A[2] += 4** (5 becomes 9):

```text
update leaf [2..2]: 5 -> 9
fix ancestors on the way up:
  [2..3]: 8 -> 12
  [0..3]: 11 -> 15
Only the path from that leaf to the root changes -> O(log n).
```

#### Lazy propagation — the intuition

For a **range** update like "add 5 to all of [L,R]", updating every leaf would be
O(n). Instead, when a node's range is **fully inside** [L,R], we update that one
node's aggregate and park a **"lazy" tag** ("+5 still owed to my children") on it
— we do **not** descend. Later, if a query or update needs to go *below* that
node, we first **push down** the parked tag to its two children (applying it and
moving the tag one level down), then continue. This keeps range updates at
**O(log n)**.

> **Memory hook:** lazy = **"I'll tell my children later."** Park the update high
> up; only push it down when someone actually visits below.

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
4. Segment tree array size (safe)? → about **4n**.
5. When does lazy "push down" happen? → only when a query/update must go
   **below** a tagged node.
6. Nodes touched by one query? → **O(log n)**.

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

#### Worked bit-trick trace (1-indexed)

`i & (-i)` peels off the lowest set bit. Two's-complement makes `-i` flip all
bits and add 1, so ANDing keeps exactly the lowest 1-bit:

```text
i = 6  = 110b     -i = ...010b (two's comp)   i & -i = 010b = 2
i = 12 = 1100b                                 i & -i = 100b = 4
i = 8  = 1000b                                 i & -i = 1000b = 8
i = 7  = 111b                                  i & -i = 001b = 1
```

**prefix_sum(6)** — keep subtracting the lowest set bit until 0:

```text
i=6 (110): s += tree[6];  6 - (6&-6=2) = 4
i=4 (100): s += tree[4];  4 - (4&-4=4) = 0
stop. sum = tree[6] + tree[4]        (covers indices 1..6 in 2 hops)
```

**update(5, +3)** — keep adding the lowest set bit until you pass n (say n=8):

```text
i=5 (101): tree[5] += 3;  5 + (5&-5=1) = 6
i=6 (110): tree[6] += 3;  6 + (6&-6=2) = 8
i=8 (1000):tree[8] += 3;  8 + (8&-8=8) = 16 > 8 -> stop
Three nodes updated -> O(log n).
```

- **query subtracts** the lowest bit (walk *down* the responsibility ranges);
  **update adds** it (walk *up* to every range that includes index i). They move
  in opposite directions — a common exam point.

### MCQs

1. Fenwick update/query time? → **O(log n)**.
2. What does `i & (-i)` give? → the **lowest set bit**.
3. Fenwick vs segment tree trade-off? → smaller/simpler **but** mainly for
   sums (invertible ops).
4. In `prefix_sum` and `update`, which direction is the lowest-bit step? → query
   **subtracts** (goes down), update **adds** (goes up).
5. Why 1-indexed? → so `i & (-i)` is well-defined (index 0 would loop forever).
6. `i & (-i)` for i = 12? → **4**.

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

### B-tree order and node fullness (a GATE staple)

A B-tree of **order m** obeys simple capacity rules:

```text
each node has at most  m children  and  m-1 keys
each node (except root) has at least  ceil(m/2)  children
                                 i.e. ceil(m/2) - 1  keys
keys inside a node are kept SORTED; children sit between/around them
```

- **Insertion split:** insert into the correct leaf; if it **overflows** (m
  keys), split it in two and push the **middle key up** to the parent. That push
  can cascade upward and, at the root, **increase the height by one** — the only
  way a B-tree grows taller.
- **Deletion:** if a node **underflows** (< ceil(m/2)-1 keys) it **borrows** a
  key from a sibling, or **merges** with a sibling (the mirror of a split).

#### Tiny insertion-split example (order 3: max 2 keys/node)

```text
insert 1,2:   [1,2]                    (leaf now full)
insert 3:     [1,2,3] overflows -> split, push middle (2) up
                 [2]
                /   \
             [1]     [3]
```

### Why leaf-linking matters (B+ range scans)

In a **B+ tree** every key also appears in a **leaf**, and the leaves form a
**doubly linked list** in sorted order. So a range query like
`WHERE age BETWEEN 20 AND 40` does **one** search down to the first leaf, then
just **walks the linked leaves** sequentially — no repeated root-to-leaf trips.
A plain B-tree, with data scattered in internal nodes, would need messy in-order
traversal instead. This is the core reason databases pick **B+ over B** and over
**hash indexes** (hash indexes give O(1) equality but cannot do ranges at all).

> **Memory hook:** B+ tree = a **library catalogue**: the index cards (internal
> nodes) only point you toward the shelves; the actual books (data) sit on the
> linked shelves (leaves) you can walk along.

### MCQs

1. Why do databases use B+ trees over binary trees? → **wide & shallow → fewer
   disk reads**; linked leaves → fast range scans.
2. Where is the data in a B+ tree? → only in the **leaves**.
3. B-tree vs B+ tree key difference? → B+ keeps data **only in leaves** and
   **links** them.
4. Max keys in a B-tree node of order m? → **m − 1** (and up to **m** children).
5. How does a B-tree grow taller? → a **root split** pushes a middle key up.
6. Why B+ over a hash index for `BETWEEN`? → hash gives **no range order**; B+
   linked leaves scan ranges fast.

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
- Q: Why is a Red-Black tree O(log n)? **A: longest path ≤ 2× shortest (no
  red-red + equal black-height).**
- Q: Value on top after any AVL rotation? **A: the middle of the three.**
- Q: Rotations to fix one AVL insert? **A: at most one (single or double).**
- Q: What is lazy propagation? **A: park a range update high, push down only
  when someone visits below.**
- Q: Segment tree array size? **A: about 4n.**
- Q: Fenwick — query vs update bit direction? **A: query subtracts, update adds
  the lowest set bit.**
- Q: Max keys in an order-m B-tree node? **A: m − 1.**
- Q: How does a B-tree grow taller? **A: a root split pushes a key up.**

## Module 8b — Pattern Recognition

- "Ordered set with guaranteed fast ops" → **balanced BST (AVL / Red-Black)**.
- "Range sum, no updates" → **prefix sum**; "+ point updates" → **Fenwick**.
- "Range min/max/gcd with updates" → **segment tree** (+ lazy for range updates).
- "Billions of records on disk / database index / range scan" → **B+ tree**.
- "Add a value to a whole range, many times" → **segment tree + lazy
  propagation**.
- "Lookup-heavy, few updates, want the shortest tree" → **AVL** (strict balance).
- "Insert/delete-heavy general-purpose ordered map" → **Red-Black** (fewer
  rotations).
- "Prefix sums with point updates, minimal code" → **Fenwick / BIT**.

## Module 8b — Interview Questions (with follow-ups)

1. *Why does a BST need balancing?* FU: *AVL vs Red-Black trade-offs.*
2. *Design a structure for range-sum with updates.* FU: *Fenwick vs segment
   tree.*
3. *Why do databases use B+ trees, not hash indexes?* FU: *range queries.*
4. *Implement a segment tree.* FU: *add lazy propagation for range updates.*
5. *Trace an AVL insert that triggers an LR rotation.* FU: *why two rotations,
   not one?*
6. *Explain why a Red-Black tree stays O(log n).* FU: *black-height and the
   no-red-red rule.*
7. *Walk through a B-tree insertion that splits the root.* FU: *how does the tree
   grow taller?*

## Module 8b — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** AVL **rotations and balance factors** (trace insertions),
  Red-Black properties, **B/B+ tree order, number of keys/children, and
  insertions/splits** (very frequently asked in DBMS too), segment/Fenwick
  complexity.
- **SEBI/RBI IT + DBMS:** B/B+ tree indexing is a core topic — see the DBMS notes.

---

*End of Module 8b. Next: Module 9 — Heaps (binary heap deep-dive, heapsort,
Fibonacci/pairing heaps, applications) — with visuals.*
