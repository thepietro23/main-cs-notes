---
title: "Module 22 — System Design Connections"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 22 — System Design Connections

> **Why this module.**
> Interviewers love the question *"why does this real system use that data
> structure?"* — it proves you understand the **trade-offs**, not just the API.
> This module connects every structure from M1–M18 to the production system that
> relies on it. It's the bridge between "DSA" and "system design".

This module is **P1** (great for senior interviews and the "why" round).

> **How to read.** System → data structure → the trade-off that made it the
> choice.

---

## 22.1 The Big Picture

![Data structures powering real systems: Redis/skip list, DB/B+ tree, Cassandra/LSM, Linux/RB-tree, schedulers/heap, search/trie, Git/DAG.](images/139_ds_in_systems.png)

Every system-design decision is a **data-structure trade-off**: read-optimised vs
write-optimised, memory vs speed, exact vs approximate, ordered vs unordered.

---

## 22.2 The Classic "Why" Stories

### Why Redis sorted sets use a **skip list**

ZSET needs **ordered range/rank queries** (`ZRANGE`, leaderboards) *and* **O(1)
score lookup by member**. A **skip list** gives O(log n) ordered ops with simple,
concurrency-friendly code; a **hash table** alongside gives O(1) member→score.
(Module 17.) A balanced BST would also work but is harder to implement
lock-free; skip lists are simpler.

### Why databases use **B+ trees** for indexes

Data lives on **disk**; the cost that matters is **disk reads (page fetches)**. A
**B+ tree** is wide and shallow (hundreds of keys per node) → a billion rows is
~3–4 levels deep → ~3–4 disk reads. Leaves are **linked** → fast **range scans**
(`WHERE age BETWEEN…`), which a hash index can't do. (Module 8b.)

### Why write-heavy stores (Cassandra, RocksDB) use **LSM trees**

Random disk writes are slow. An **LSM tree** buffers writes in memory (memtable),
flushes them as **sorted SSTables**, and **compacts** in the background → turns
random writes into sequential ones (**write-optimised**). **Bloom filters** on
SSTables skip disk reads for absent keys. (Modules 8b/17/7.)

### Why Linux uses **red-black trees**

The **CFS scheduler** keeps runnable tasks in a red-black tree keyed by "virtual
runtime" → always pick the leftmost (least-run) task in O(log n); insert/remove
in O(log n). Also used for **virtual memory areas** and **epoll**. RB-trees
balance with **fewer rotations** than AVL → better for insert/delete-heavy kernel
use. (Module 8b.)

### Why schedulers/timers use **heaps**

"What fires next?" = **extract-min** → a **min-heap (priority queue)** gives O(log
n) insert and O(1) peek of the next event. Used in OS timers, event simulators,
Dijkstra, and job schedulers. (Module 6.)

### Why search engines use **tries + inverted indexes**

**Autocomplete** = prefix queries → **trie** (Module 3). **Full-text search** =
map each term → list of documents (**inverted index**) → intersect/union posting
lists for queries. Ranking adds heaps (top-N) and more.

### Why Git uses a **DAG + Merkle tree**

![Git: a DAG of commits (each points to its parent(s)); each commit ID is a Merkle hash of its content.](images/140_git_dag.png)

Commit history is a **Directed Acyclic Graph** — each commit points to its
**parent(s)** (a merge has two). Each object's ID is a **SHA hash of its content**
(a **Merkle tree** of trees/blobs) → **tamper-evident**, automatic **dedup**
(identical content = same hash), and fast diff/sync. (Modules 10 + 3-hashing.)

### Why distributed caches use **consistent hashing**

Plain `hash(key) % N` remaps *almost everything* when `N` changes (a node
joins/leaves). **Consistent hashing** places nodes and keys on a ring → adding a
node remaps only **~1/N** of keys. Used in DynamoDB, Cassandra, CDNs, memcached
clusters. (Module 7.)

### MCQs

1. Why B+ trees for DB indexes (not hash)? → **shallow (few disk reads) + linked
   leaves for range scans**.
2. Why LSM trees for write-heavy stores? → **turn random writes into sequential**
   (write-optimised) + Bloom filters.
3. Why consistent hashing? → adding/removing a node remaps only **~1/N** of keys.

---

## 22.3 Quick Reference: DS → System

| Data structure | Powers |
|---|---|
| **Array / dynamic array** | almost everything; columnar stores |
| **Hash table** | caches, DB hash indexes, dedup, sets |
| **Skip list** | Redis ZSET, concurrent maps |
| **B+ tree** | relational DB indexes, filesystems |
| **LSM tree** | Cassandra, RocksDB, LevelDB, time-series DBs |
| **Red-Black tree** | Linux CFS, C++ `std::map`, Java `TreeMap` |
| **Heap / priority queue** | schedulers, timers, Dijkstra, top-N |
| **Trie / inverted index** | autocomplete, search engines |
| **Graph (DAG)** | Git, build systems, task dependencies, package managers |
| **Bloom filter / HLL** | "seen before?", cardinality (Cassandra, Redis) |
| **Consistent hashing** | sharding, distributed caches/DBs |
| **HNSW / ANN** | vector DBs, semantic search (Module 21) |

### MCQs

1. C++ `std::map` / Java `TreeMap` use? → **red-black trees**.
2. Build-system / package-manager dependency ordering? → **DAG + topological
   sort**.
3. "Is this key probably present, cheaply?" → **Bloom filter**.

---

## Module 22 — Concept Review (one page)

- Every system choice = a **DS trade-off** (read/write, memory/speed,
  exact/approximate).
- **Redis ZSET** = skip list + hash; **DB index** = B+ tree (shallow + range
  scans); **write-heavy** = LSM + Bloom; **Linux CFS** = red-black tree;
  **schedulers** = heap; **search** = trie + inverted index; **Git** = DAG +
  Merkle; **sharding** = consistent hashing; **vector search** = HNSW.

## Module 22 — Flash Cards

- Q: Redis sorted set? **A: skip list + hash table.**
- Q: DB index structure & why? **A: B+ tree — shallow + linked-leaf range scans.**
- Q: Write-optimised store? **A: LSM tree (+ Bloom filters).**
- Q: Linux scheduler tree? **A: red-black tree (CFS).**
- Q: Git's structure? **A: DAG of commits + Merkle hashes.**
- Q: Minimal remap on scaling? **A: consistent hashing.**

## Module 22 — Pattern Recognition (system-design "why")

- "Ordered + ranked + fast lookup" → **skip list / balanced BST + hash**.
- "On-disk index, range queries" → **B+ tree**; "write-heavy" → **LSM**.
- "What happens next / top-N" → **heap**.
- "Prefix / search" → **trie / inverted index**.
- "History / dependencies / content integrity" → **DAG / Merkle**.
- "Scale out without reshuffling everything" → **consistent hashing**.

## Module 22 — Interview Questions

1. *Why does MySQL use a B+ tree, not a hash index?* → range scans + few disk
   reads.
2. *Design a leaderboard.* → Redis ZSET (skip list) / balanced BST + hash.
3. *Why does Cassandra write faster than a B-tree DB?* → LSM (sequential writes).
4. *How does Git detect identical files instantly?* → content hashing (Merkle).
5. *Why consistent hashing for a distributed cache?* → minimal remap on
   add/remove.

## Module 22 — GATE / SEBI / RBI / ISRO Perspective

- **DBMS overlap (high-yield):** B/B+ tree indexing, hashing, and these structure
  choices appear in DBMS and OS sections (CFS scheduler, paging). Ties directly to
  the DBMS notes.

---

*End of Module 22. Next: Module 23 — Competitive Exams mapping (GATE / SEBI / RBI
/ ISRO / DRDO / C-DAC topic weightage) — with visuals.*
