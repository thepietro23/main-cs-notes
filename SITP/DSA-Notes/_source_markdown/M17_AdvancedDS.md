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
