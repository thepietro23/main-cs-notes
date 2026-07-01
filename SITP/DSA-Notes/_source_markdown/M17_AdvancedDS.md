---
title: "Module 17 — Advanced Data Structures"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 17 — Advanced Data Structures

> **Why this module (and how to use it).**
> These are the "specialist tools" — rarely needed in a standard FAANG coding
> round, but they appear in **competitive programming**, hard/senior interviews,
> and a few GATE questions, and they show up in real systems (Redis, databases).
> Goal: **recognise what each one is for** and its headline complexity. Don't
> memorise full implementations — know *when* you'd reach for it.

This module is **P2**.

> **How to read each technique.** What it is, what it's for, complexity.

---

## 17.1 Skip List

A **skip list** is a stack of linked lists: the bottom holds all elements; each
higher level is an "express lane" skipping ~half the nodes. Search drops down a
level when it would overshoot.

![Skip list: express lanes on top let search skip many nodes, giving expected O(log n).](images/125_skip_list.png)

- **Expected O(log n)** search/insert/delete (randomised level per node) — a
  simpler, lock-friendlier alternative to balanced BSTs.
- **Real use:** **Redis sorted sets (ZSET)** = a **skip list** (ordered range/rank
  queries) **+ a hash table** (O(1) score-by-member); tiny sets use a compact
  *listpack* and upgrade past a size threshold. Also Java `ConcurrentSkipListMap`.

> **Memory hook:** highway exits — take the fastest lane, drop to a slower one only
> when you're about to pass your exit.

### 17.1a Why the levels give expected O(log n)

The trick is the **coin flip**. When you insert a node, you keep tossing a fair
coin: it goes up one level for every "heads", and stops at the first "tails". So
each node reaches level `L` with probability `1/2^L`.

- With probability **1/2** a node is on level 1 (the base only).
- With probability **1/4** it also reaches level 2.
- With probability **1/8** it also reaches level 3, and so on.

So on average **half** the nodes appear at level 1, a **quarter** at level 2, an
**eighth** at level 3… Each higher lane holds about half as many nodes as the one
below — exactly the "skip half" property a balanced structure needs, but achieved
by pure chance, with **no rotations and no rebalancing**.

```text
Expected count per level (n nodes, p = 1/2):
  level 1 : n            (all nodes)
  level 2 : n/2
  level 3 : n/4
  ...
  top     : ~1
Number of levels ≈ log2(n).  Total nodes ≈ n + n/2 + n/4 + ... ≈ 2n = O(n) space.
```

**Search cost intuition.** Search walks *right* on a level, then *drops down* when
the next node would overshoot the target. At each level you expect to step right
only **~1–2 times** before dropping (because each node has a ~1/2 chance of being
promoted, a right-move that does not overshoot is "rare"). There are about
`log2(n)` levels, so total work is **O(log n) expected**. The bound is
*probabilistic* (expected / with-high-probability), not a hard worst case — a very
unlucky run of coin flips could be worse, but that is astronomically unlikely.

> **Memory hook:** flip a coin per node; heads = promote. Halving lanes ⇒ log
> height ⇒ O(log n), for free, no balancing code.

### MCQs

1. Probability a skip-list node reaches level `L` (p = 1/2)? → **1/2^L**.
2. Expected number of levels for `n` nodes? → **≈ log₂ n**.
3. Is skip-list O(log n) a worst case? → **No — expected / with-high-probability.**

---

## 17.2 Treap / Cartesian Tree

A **treap** is a BST on **keys** that is *also* a max-heap on **random
priorities** assigned to each node. Random priorities keep it balanced in
**expected O(log n)** — with much simpler code than AVL/Red-Black (no rotation
cases to memorise; just rotate to fix the heap order).

![Treap: BST by key + heap by random priority → expected O(log n), self-balancing on average.](images/126_treap.png)

- **Cartesian tree:** the same idea where priorities come from the array values
  (used to build in O(n) and for range-minimum / LCA tricks).
- **Implicit treap:** keyed by *position* → supports `insert/erase/reverse a
  subarray` in O(log n) (a CP power-tool).

### 17.2a Treap worked example (two invariants at once)

A treap obeys **two** rules together:

- **BST rule on keys:** left subtree keys < node key < right subtree keys.
- **Heap rule on priorities:** every node's priority ≥ its children's priorities
  (a *max*-heap on the random priorities).

Say we insert these `(key, priority)` pairs in order. Priorities are random; here
we just pick numbers to trace the shape:

```text
Insert (key, prio):  (D,50)  (B,30)  (F,80)  (A,10)  (C,20)

Step 1: insert D50           D50
Step 2: insert B30       B30 is left of D (B<D). prio 30<50, heap ok.
              D50
             /
           B30
Step 3: insert F80       F is right of D (F>D). But prio 80 > 50 (heap broken!)
                          -> rotate F up above D.
              F80
             /
           D50
           /
         B30
Step 4: insert A10       A<B<D<F, goes far left; prio 10 smallest, no rotation.
              F80
             /
           D50
           /
         B30
         /
       A10
Step 5: insert C20       B<C<D, so C is right child of B. prio 20<30, heap ok.
              F80
             /
           D50
           /
         B30
        /   \
      A10   C20
```

Read the **keys** left-to-right (in-order): A, B, C, D, F — sorted (BST holds).
Read the **priorities** top-down: 80, 50, 30, … each parent ≥ child (heap holds).
Because the priorities are random, the tree's shape is the same as a **randomly
built BST**, whose expected height is **O(log n)** — that is where the balance
comes from. Deletion is the mirror: rotate the node *down* (always toward the
child with the larger priority) until it becomes a leaf, then cut it.

> **Memory hook:** keys sorted left-to-right, priorities big-at-top. Random
> priorities = a random BST = expected O(log n), with almost no code.

### MCQs

1. A treap combines which two structures? → **BST on keys + heap on priorities**.
2. Where does a treap's balance come from? → **random priorities ⇒ random-BST
   height ⇒ expected O(log n)**.
3. To delete a treap node you? → **rotate it down toward the larger-priority child
   until it is a leaf, then remove it**.

---

## 17.3 Suffix Array (+ LCP)

A **suffix array** is the sorted list of starting indices of **all suffixes** of a
string. With the companion **LCP array** (longest common prefix of adjacent
suffixes), it answers many string problems efficiently.

![Suffix array of 'banana' = [5,3,1,0,4,2]; with the LCP array it powers fast substring queries.](images/127_suffix_array.png)

- Build in **O(n log n)** (or O(n log² n) simply; O(n) with DC3/SA-IS).
- **Uses:** substring search, **longest repeated substring**, distinct-substring
  count, longest common substring of two strings.
- A **space-efficient alternative to a suffix tree** (same power, smaller
  constant, easier to code).

### 17.3a Suffix array vs suffix automaton (which linear string tool?)

Both index *all* substrings of a string, but they are shaped differently and shine
on different jobs:

| Aspect | Suffix array (+ LCP) | Suffix automaton (SAM) |
|---|---|---|
| What it is | sorted list of suffix start indices | smallest DFA accepting all substrings |
| Build | **O(n log n)** (O(n) via SA-IS) | **O(n)** online (add chars one by one) |
| Shape | flat array + LCP array | DAG, ≤ 2n−1 states |
| Best at | substring **search**, longest **repeated** substring, distinct-substring count via LCP, suffix ordering | distinct-substring count (sum of state lengths), **longest common substring** of 2+ strings, counting occurrences |
| Mental model | "sort every suffix, binary-search in it" | "a compressed graph of every substring" |

**Rule of thumb:** if you think in terms of *sorted suffixes / ranges / binary
search*, reach for the **suffix array**. If you think in terms of *walking
substrings as transitions / online addition of characters / matching against many
strings*, reach for the **suffix automaton**.

> **Memory hook:** suffix **array** = a sorted *phone book* of suffixes; suffix
> **automaton** = a *road map* where every path spells a substring.

### MCQs

1. Which builds in guaranteed linear time online? → **suffix automaton (SAM)**.
2. Longest common substring of two strings prefers? → **suffix automaton**.
3. Longest *repeated* substring of one string via LCP prefers? → **suffix array**.

---

## 17.4 Persistent Data Structures

A **persistent** structure keeps **every past version** after an update (you can
query old versions). The trick is **path copying**: an update copies only the
O(log n) nodes on the changed path and shares the rest.

- **Persistent segment tree** (the common one): O(log n) per update/query, O(log
  n) extra memory per update; powers "k-th smallest in a range", versioned
  arrays.
- **Functional/immutable** structures (used in functional languages) are
  persistent by design.

> **Memory hook:** like **git for a data structure** — each commit (update) shares
> most of the previous tree and only records what changed.

- **Real use:** copy-on-write B-trees (LMDB, CouchDB), filesystem snapshots
  (ZFS/Btrfs), immutable collections (Clojure/Scala) — all "persistence via
  structural sharing".

---

## 17.5 KD-Tree (spatial)

A **KD-tree** partitions k-dimensional space, **alternating the splitting axis**
by depth (x, then y, then z, …). It supports **nearest-neighbour** and **range**
queries.

![KD-tree: alternately split 2D space by x then y; supports nearest-neighbour and range search.](images/128_kd_tree.png)

- **~O(log n)** average per query in **low dimensions**; degrades in high
  dimensions ("curse of dimensionality") → for high-D similarity search use
  **Approximate Nearest Neighbour (ANN)**: **HNSW** graphs (the production default
  in Faiss/pgvector/Milvus/Pinecone), **IVF + product quantization** for scale,
  and the older **LSH** hashing family (Module 21).
- **Uses:** geometry, k-nearest-neighbour (ML), collision detection, maps.

---

## 17.6 Wavelet Tree & Aho-Corasick (brief)

- **Wavelet tree:** answers **rank/select** and "k-th smallest in a range"
  queries over a sequence of values in O(log σ) (σ = alphabet/value range).
  Powers compact text indexes.
- **Aho-Corasick:** a **Trie + failure links** (KMP generalised to many patterns)
  → find **all** occurrences of a set of patterns in O(text + matches). The
  multi-pattern matcher (virus scanners, keyword filters). (Links to Module 3.)
- **Suffix automaton (SAM):** an O(n) DAG of all substrings, built online; used
  for distinct-substring counting and longest common substring (another linear
  string structure alongside the suffix array).

## 17.6a Sqrt Decomposition (the √n range trick)

**Sqrt decomposition** is one of the most useful "medium-power" CP structures. The
idea is simple: split the array of `n` elements into blocks of size about `√n`,
and precompute a summary (e.g. the **sum**) for each block. Then a range query
touches at most **two partial blocks at the ends** (scanned element by element) and
some **whole blocks in the middle** (read from the precomputed summaries).

- Number of blocks ≈ √n, block size ≈ √n.
- A range `[l, r]` has **at most 2 partial blocks** (≤ 2·√n elements to scan) and
  **at most √n whole blocks** (each read in O(1)).
- So each query is **O(√n)**, and a point update is **O(1)** (fix one element and
  its block's summary).

![Sqrt decomposition: whole blocks read in O(1), only edge cells scanned, giving O(sqrt n) per range query.](images/290_sqrt_decomposition.png)

**Worked query** (from the figure): array `[1,3,2,5,4,1,6,2,7]`, block size 3, so
block sums are `[6, 10, 15]`. Compute `sum(2..7)` (0-indexed, inclusive):

```text
Range 2..7 breaks into:
  - index 2        (partial, left edge)   -> value 2
  - indices 3,4,5  (whole block 1)        -> use block sum 10   (no scan!)
  - indices 6,7    (partial, right edge)  -> 6 + 2 = 8
Total = 2 + 10 + 8 = 20
```

Pseudocode:

```text
BLOCK = floor(sqrt(n))
build:  for i in 0..n-1:  blockSum[i / BLOCK] += a[i]

query(l, r):                       # inclusive
    total = 0
    while l <= r and l % BLOCK != 0:      # left partial block
        total += a[l]; l++
    while l + BLOCK - 1 <= r:             # whole blocks
        total += blockSum[l / BLOCK]; l += BLOCK
    while l <= r:                         # right partial block
        total += a[l]; l++
    return total

update(i, val):                     # point update
    blockSum[i / BLOCK] += val - a[i]
    a[i] = val
```

**Why bother when a segment tree also does ranges?** Sqrt decomposition is the
**bridge between brute force and a segment tree**: it is far easier to code and
works even when the merge operation is *awkward* (e.g. "how many elements in this
range are > x", by keeping each block **sorted**). It is often "good enough" and
much less bug-prone under contest pressure.

> **Memory hook:** √n blocks. Ends scanned by hand, middle read from summaries —
> `2√n + √n = O(√n)` per query.

### MCQs

1. Sqrt decomposition query cost? → **O(√n)**.
2. How many *whole* precomputed blocks can a range span? → **at most √n**.
3. Why pick it over a segment tree? → **simpler to code; handles awkward merges**.

## 17.6b Mo's Algorithm (offline range queries in O((n+q)√n))

**Mo's algorithm** answers many range queries *offline* (all queries known up
front, no updates) by **reordering** them so the answer window slides cheaply.

- Maintain a current window `[curL, curR]` and its answer (e.g. count of distinct
  values, using a frequency array). Moving an endpoint by one is an **add/remove**
  of a single element — O(1) each.
- **The reorder trick:** sort queries by **(block of L, then R)**, using block
  size ≈ √n. This bounds total endpoint movement: `curR` moves O(n) within each of
  the √n L-blocks (O(n√n) total), and `curL` moves O(√n) per query (O(q√n) total).
- **Total: O((n + q)√n).** No fancy tree — just clever ordering.

```text
add(x):    freq[a[x]]++;  if freq[a[x]]==1: distinct++
remove(x): freq[a[x]]--;  if freq[a[x]]==0: distinct--

for each query (l,r) in Mo-sorted order:
    while curR < r: curR++; add(curR)
    while curL > l: curL--; add(curL)
    while curR > r: remove(curR); curR--
    while curL < l: remove(curL); curL++
    answer[query] = distinct
```

**When to reach for it:** many range queries, **no updates**, and a per-query
statistic that is **easy to update by ±1 element** but hard to merge (classic:
"number of distinct values in `[l, r]`"). If there *are* updates, a segment tree
or "Mo's with updates" variant is needed instead.

> **Memory hook:** Mo's = "sort the questions so the answer window barely moves."

### MCQs

1. Mo's algorithm total complexity? → **O((n+q)√n)**.
2. Key precondition for plain Mo's? → **offline queries, no updates**.
3. Queries are sorted by? → **(block of L, then R)**, block ≈ √n.

## 17.7 System-Design & Range-Query Structures (senior-interview essentials)

- **B+-tree vs LSM-tree (the two database index families):**
  - **B+-tree** (Module 8b): **read-optimised**, balanced, in-place updates →
    relational DB indexes (MySQL/Postgres).
  - **LSM-tree** (Log-Structured Merge): **write-optimised** — buffer writes in a
    memtable, flush to sorted **SSTables**, **compact** in the background →
    Cassandra, RocksDB, LevelDB. Trade-off: LSM has higher read/space
    amplification but far better write throughput.
- **Sqrt decomposition / Mo's algorithm:** split the array into ~√n blocks →
  **O(√n)** per range query/update; the bridge between brute force and a segment
  tree when a clean associative merge is hard. **Mo's algorithm** reorders
  *offline* queries for **O((n+q)√n)**.
- **Probabilistic (cross-ref Module 7):** approximate membership → **Bloom /
  Cuckoo filter** (SSTable Bloom filters skip disk reads); approximate distinct
  count → **HyperLogLog** (Redis `PFADD`/`PFCOUNT`).
- **Base structures:** segment tree / **Fenwick (BIT)** live in **Module 8b**; the
  *persistent* segment tree (§17.4) = that base + path copying.

### MCQs

1. Write-optimised DB index family? → **LSM-tree** (Cassandra/RocksDB).
2. Range queries without a clean merge / offline? → **sqrt decomposition / Mo's**.
3. Approximate membership / distinct-count? → **Bloom filter / HyperLogLog** (M07).

## 17.7a Decision table — which advanced structure do I reach for?

When a problem smells "advanced", match the *signal* in the statement to the tool.
Read this top-to-bottom; the first row that fits usually wins.

| The problem needs… | Reach for… | Typical cost |
|---|---|---|
| ordered set, simple + concurrent-friendly | **skip list** | expected **O(log n)** |
| balanced BST with tiny code / reverse-a-subarray | **treap / implicit treap** | expected **O(log n)** |
| many substring / repeated-substring queries, one fixed string | **suffix array + LCP** | build **O(n log n)** |
| online substring index / LCS of several strings | **suffix automaton** | build **O(n)** |
| query *old* versions / k-th in range with history | **persistent segment tree** | **O(log n)** per op |
| nearest-neighbour / range in 2-D–3-D | **KD-tree** (high-D → HNSW/LSH) | ~**O(log n)** low-D |
| rank/select, k-th smallest in a range | **wavelet tree** | **O(log σ)** |
| match many patterns at once | **Aho-Corasick** | **O(text + matches)** |
| range queries, awkward merge, easy to code | **sqrt decomposition** | **O(√n)** per query |
| many *offline* range queries, no updates, ±1-updatable stat | **Mo's algorithm** | **O((n+q)√n)** total |
| write-heavy on-disk index | **LSM-tree** | amortised, high write throughput |
| read-heavy on-disk index | **B+-tree** | **O(log n)** in-place |

> **Memory hook:** first ask "is a plain segment tree / Fenwick (M8b) enough?" —
> only when the *merge is awkward, versions are needed, or it's a string/spatial
> problem* do you climb up to these specialist tools.

### MCQs

1. Awkward merge + easy to code, one array, updates allowed? → **sqrt
   decomposition**.
2. Offline range distinct-count, no updates? → **Mo's algorithm**.
3. Need to query historical versions of an array? → **persistent segment tree**.

---

## Module 17 — Concept Review (one page)

- **Skip list:** layered lists, expected O(log n); Redis sorted sets.
- **Treap:** BST key + heap random priority → expected O(log n), simple;
  Cartesian/implicit treaps for arrays.
- **Suffix array + LCP:** sorted suffixes, O(n log n) build; substring / repeated-
  substring problems; lean suffix-tree alternative.
- **Persistent structures:** keep all versions via path copying (persistent
  segment tree); "git for data".
- **KD-tree:** alternate-axis spatial partition, ~O(log n) low-D NN/range; high-D
  → HNSW/LSH.
- **Wavelet tree** (rank/select, k-th in range); **Aho-Corasick** (multi-pattern
  matching = Trie + failure links).

## Module 17 — Flash Cards

- Q: Redis sorted sets use? **A: skip list.**
- Q: Treap = ? **A: BST by key + heap by random priority (expected O(log n)).**
- Q: Suffix array build time? **A: O(n log n) (O(n) with SA-IS).**
- Q: Persistent update memory/time? **A: O(log n) via path copying.**
- Q: KD-tree splits how? **A: alternate axis per depth; low-D NN search.**
- Q: Multi-pattern matching structure? **A: Aho-Corasick (Trie + failure links).**
- Q: Skip-list node reaches level L with probability? **A: 1/2^L.**
- Q: Sqrt decomposition query cost? **A: O(√n).**
- Q: Mo's algorithm total cost? **A: O((n+q)√n), offline, no updates.**
- Q: Guaranteed-linear online string index? **A: suffix automaton (SAM).**

## Module 17 — Pattern Recognition

- "Ordered set, simple + concurrent" → **skip list**.
- "Balanced BST without rotation pain / reverse a subarray" → **treap / implicit
  treap**.
- "Many substring/repeated-substring queries on a fixed string" → **suffix array +
  LCP**.
- "Query old versions / k-th in a range with updates" → **persistent segment
  tree**.
- "Nearest neighbour / range in 2D-3D" → **KD-tree** (high-D → ANN, Module 21).
- "Match many patterns at once" → **Aho-Corasick**.
- "Range query, awkward merge, easy to code, with updates" → **sqrt
  decomposition**.
- "Many offline range queries, no updates, count-distinct style" → **Mo's
  algorithm**.
- "Longest common substring of several strings / online char-by-char" → **suffix
  automaton**.

## Module 17 — Interview / CP Questions

1. *Design Redis ZADD/ZRANGE.* → skip list (or balanced BST) ordering.
2. *Longest repeated substring.* → suffix array + LCP.
3. *k-th smallest in a subarray with updates / historical queries.* → persistent
   segment tree / wavelet tree.
4. *k nearest points.* → KD-tree (low-D) / heap; high-D → ANN.

## Module 17 — GATE / SEBI / RBI / ISRO Perspective

- **GATE:** mostly conceptual — skip-list expected complexity, suffix
  structures, persistence idea. These are **less frequent**; prioritise
  M08 (trees), M10 (graphs), M14 (DP) for exams and treat M17 as "recognise the
  tool".

---

*End of Module 17. Next: Module 18 — Algorithm Design & Analysis (recurrences,
Master theorem, amortized analysis, randomized & approximation, P/NP) — with
visuals.*
