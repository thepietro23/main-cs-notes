---
title: "Module 25 — Projects (Build to Cement)"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 25 — Projects

> **Why build projects.**
> Reading about a data structure ≠ owning it. **Building** a small system forces
> you to handle the edge cases, the API, and the trade-offs — and it's the
> strongest signal on a resume and in a "tell me about something you built"
> interview. Each project below is a **direct application** of earlier modules.

This module is **P1** (do 2–3 well rather than all 8 shallowly).

> **How to read.** For each: what it is, the core DS, the key design decisions,
> and the modules it exercises.

---

## 25.1 Project → Data Structure Map

![Projects and their core data structures: LRU (hashmap+DLL), autocomplete (trie+heap), mini-Git (DAG+Merkle), etc.](images/142_projects_map.png)

---

## 25.2 The Projects

### 1. LRU Cache (start here)
- **DS:** **HashMap + Doubly Linked List** (Module 4/7).
- **Design:** map key→node for O(1) lookup; DLL ordered by recency (MRU head, LRU
  tail); `get`/`put` move the node to head; evict the tail when full. All **O(1)**.
- **Extend:** **LFU** (frequency buckets), TTL expiry, thread-safety (locks /
  sharding). *Interview-classic (LC 146).*

### 2. Autocomplete / Typeahead
- **DS:** **Trie** + a **heap** for top-k ranking (Module 3/6).
- **Design:** insert words (with frequencies); on a prefix, walk to the prefix
  node, then collect/rank the top-k completions (precompute top-k per node for
  speed). **Extend:** fuzzy match (edit distance), weighted by popularity.

### 3. URL Shortener (TinyURL)
- **DS:** **HashMap** + **base-62 encoding** of an auto-increment counter (Module
  7/16).
- **Design:** counter → base-62 string (a–z A–Z 0–9) = short code; store
  code↔URL; handle collisions/custom aliases; scale with sharding + caching.
  *Classic system-design + DSA crossover.*

### 4. Search Engine Index (mini)
- **DS:** **Inverted index** (term → posting list) + **Trie** (autocomplete) +
  **heap** (top-N ranking) (Module 3/7/6).
- **Design:** tokenize/normalize docs → build `term → sorted doc IDs`; query =
  **intersect/union** posting lists; rank by TF-IDF/BM25; return top-N via a heap.

### 5. Mini Git
- **DS:** **DAG of commits** + **Merkle/content hashing** (Module 10/3).
- **Design:** `blob`/`tree`/`commit` objects, each addressed by **SHA of its
  content**; a commit points to its parent(s) → history is a DAG; `diff` compares
  trees; branches are pointers. **Exercises:** hashing, graphs, deduplication.

### 6. Task Scheduler / Job Queue
- **DS:** **Heap (priority queue)** + **topological sort** for dependencies
  (Module 6/10).
- **Design:** min-heap keyed by run-time/priority → next job in O(log n); a DAG of
  dependencies → run in topological order; handle retries, delays, cron.

### 7. Memory Allocator (malloc)
- **DS:** **free lists**, **segregated bins**, **buddy system** (Module 1/4).
- **Design:** track free blocks (linked lists by size class); `malloc` finds a
  fit (first/best-fit); `free` coalesces neighbours; the **buddy system** splits/
  merges power-of-two blocks. **Exercises:** pointers, fragmentation, the heap
  (Module 1) from the *implementer's* side.

### 8. Recommendation Engine
- **DS:** **graph** (user-item) + **ANN** (embeddings) + **heap** (top-N) (Module
  10/21/6).
- **Design:** collaborative filtering on a bipartite graph, or embed users/items
  and **ANN-retrieve** similar ones (HNSW), then rank and take **top-N** with a
  heap.

### MCQs

1. LRU cache core structures? → **HashMap + doubly linked list**.
2. Autocomplete core structure? → **Trie** (+ heap for ranking).
3. Mini-Git's history is a? → **DAG** (with Merkle hashing).
4. URL shortener code generation? → **base-62 of a counter**.

---

## 25.3 How to Approach a Project

1. **Define the API first** (`get/put`, `insert/search`, `commit/diff`).
2. **Pick the DS** from the trade-offs (this whole course).
3. **Build the happy path**, then **edge cases** (empty, full, eviction, missing).
4. **Test** (unit tests + a stress test).
5. **Write a short README**: the design, the DS choice + *why*, complexity, and
   what you'd do at scale. (That README is your interview talking points.)

---

## Module 25 — Concept Review (one page)

- Projects = applied DSA + the strongest signal. Map: **LRU** (hashmap+DLL),
  **autocomplete** (trie+heap), **URL shortener** (hashmap+base62), **search
  index** (inverted index+trie+heap), **mini-Git** (DAG+Merkle), **scheduler**
  (heap+topo), **allocator** (free lists/buddy), **recsys** (graph+ANN+heap).
- Build 2–3 deeply; write a README explaining the DS choice, complexity, and
  scaling.

## Module 25 — Flash Cards

- Q: LRU cache? **A: hashmap + doubly linked list (O(1)).**
- Q: Autocomplete? **A: trie + top-k heap.**
- Q: Mini-Git? **A: DAG of commits + Merkle hashing.**
- Q: Search index core? **A: inverted index (+ trie + ranking heap).**
- Q: Allocator structures? **A: free lists / segregated bins / buddy system.**

## Module 25 — Pattern Recognition

- "O(1) get/put with eviction" → hashmap + DLL.
- "Prefix suggestions" → trie (+ heap).
- "Short unique IDs" → base-62 of a counter.
- "Version history / content integrity" → DAG + Merkle.
- "Run jobs by priority/dependency" → heap + topological sort.

## Module 25 — Interview Questions

1. *Design an LRU cache.* (then LFU, TTL, thread-safety.)
2. *Design TinyURL.* (encoding, collisions, scale.)
3. *Design autocomplete at scale.* (trie + precomputed top-k + sharding.)
4. *How does Git store and dedupe objects?* (content hashing / Merkle.)

## Module 25 — GATE / SEBI / RBI / ISRO Perspective

- Projects aren't directly examined, but building a **memory allocator**,
  **scheduler**, or **B+-tree index** deeply reinforces OS/DBMS exam topics.

---

*End of Module 25. Next: Module 26 — Revision Kit (cheat sheets, complexity
tables, roadmaps, the dependency graph, and the Top-300 plan) — the finale.*
