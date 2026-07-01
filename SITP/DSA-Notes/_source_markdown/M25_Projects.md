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
- **Probe:** *Why a doubly (not singly) linked list?* → O(1) removal of an
  arbitrary node needs its predecessor. *Why store the node in the map, not the
  value?* → so `get` can splice it to the head in O(1). *What breaks under
  concurrency?* → the map and list can desync; you need a lock or a striped/sharded
  design.

### 2. Autocomplete / Typeahead
- **DS:** **Trie** + a **heap** for top-k ranking (Module 3/6).
- **Design:** insert words (with frequencies); on a prefix, walk to the prefix
  node, then collect/rank the top-k completions (precompute top-k per node for
  speed). **Extend:** fuzzy match (edit distance), weighted by popularity.
- **Probe:** *Trie vs hashmap of words?* → the trie shares prefixes (space) and
  gives prefix walk in O(prefix length). *How to serve top-k fast?* → cache the
  top-k list at each node so a query is a single lookup, not a subtree scan.
  *Memory blow-up?* → compress with a radix/Patricia trie or a DAWG.

### 3. URL Shortener (TinyURL)
- **DS:** **HashMap** + **base-62 encoding** of an auto-increment counter (Module
  7/16).
- **Design:** counter → base-62 string (a–z A–Z 0–9) = short code; store
  code↔URL; handle collisions/custom aliases; scale with sharding + caching.
  *Classic system-design + DSA crossover.*
- **Probe:** *Why base-62, not a random string?* → a counter guarantees
  uniqueness with no collision check; base-62 keeps codes short. *How short can
  codes be?* → 62^7 ≈ 3.5 trillion, so 7 chars is plenty. *Hashing the URL
  instead?* → risks collisions; you'd need to probe/re-hash. *Distributed
  counter?* → hand out ID ranges per shard (or use a key-generation service).

### 4. Search Engine Index (mini)
- **DS:** **Inverted index** (term → posting list) + **Trie** (autocomplete) +
  **heap** (top-N ranking) (Module 3/7/6).
- **Design:** tokenize/normalize docs → build `term → sorted doc IDs`; query =
  **intersect/union** posting lists; rank by TF-IDF/BM25; return top-N via a heap.
- **Probe:** *Why keep posting lists sorted?* → intersection of two sorted lists
  is a linear merge (like the two-pointer step), and you can skip ahead. *Why a
  heap for top-N, not a full sort?* → you only need the N best of many scored docs,
  so a size-N heap is O(m log N) vs O(m log m). *Compression?* → delta-encode the
  doc IDs (gap encoding) to shrink the index.

### 5. Mini Git
- **DS:** **DAG of commits** + **Merkle/content hashing** (Module 10/3).
- **Design:** `blob`/`tree`/`commit` objects, each addressed by **SHA of its
  content**; a commit points to its parent(s) → history is a DAG; `diff` compares
  trees; branches are pointers. **Exercises:** hashing, graphs, deduplication.
- **Probe:** *Why content-address (hash the content)?* → identical content hashes
  to the same key, so storage is deduplicated for free, and the hash verifies
  integrity. *Why a DAG, not a tree?* → a merge commit has two parents. *How does
  `git` find the change set between two commits?* → diff their tree objects
  recursively, descending only where subtree hashes differ.

### 6. Task Scheduler / Job Queue
- **DS:** **Heap (priority queue)** + **topological sort** for dependencies
  (Module 6/10).
- **Design:** min-heap keyed by run-time/priority → next job in O(log n); a DAG of
  dependencies → run in topological order; handle retries, delays, cron.
- **Probe:** *Why a heap over a sorted list?* → jobs arrive continuously; a heap
  gives O(log n) insert and O(1) peek of the next due job. *How do you detect an
  impossible dependency set?* → a cycle in the DAG (topological sort fails / DFS
  finds a back edge). *Delayed jobs?* → key the heap by the future run-time and
  sleep until the top's time.

### 7. Memory Allocator (malloc)
- **DS:** **free lists**, **segregated bins**, **buddy system** (Module 1/4).
- **Design:** track free blocks (linked lists by size class); `malloc` finds a
  fit (first/best-fit); `free` coalesces neighbours; the **buddy system** splits/
  merges power-of-two blocks. **Exercises:** pointers, fragmentation, the heap
  (Module 1) from the *implementer's* side.
- **Probe:** *First-fit vs best-fit?* → first-fit is faster; best-fit wastes less
  but scans more and can leave tiny unusable slivers. *Why coalesce on free?* → to
  fight external fragmentation by re-merging adjacent free blocks. *Why the buddy
  system?* → splitting/merging power-of-two blocks makes finding a buddy O(1) by
  address arithmetic, at the cost of internal fragmentation.

### 8. Recommendation Engine
- **DS:** **graph** (user-item) + **ANN** (embeddings) + **heap** (top-N) (Module
  10/21/6).
- **Design:** collaborative filtering on a bipartite graph, or embed users/items
  and **ANN-retrieve** similar ones (HNSW), then rank and take **top-N** with a
  heap.
- **Probe:** *Why ANN instead of exact nearest neighbours?* → exact search over
  millions of vectors is too slow; ANN (HNSW/IVF) trades a little recall for huge
  speed. *Cold-start?* → new users/items have no interactions; fall back to
  popularity or content features. *Why a heap for top-N?* → same reason as the
  search index — you want the N best scores, not a full sort.

### 9. Rate Limiter (SEBI/GATE-relevant, OS + systems)
- **DS:** **queue / ring buffer** (sliding-window log) or two **counters**
  (token-bucket) (Module 4/5).
- **Design:** *token bucket* — refill tokens at a fixed rate up to a cap; each
  request spends one token, reject when empty. *Sliding-window log* — keep request
  timestamps in a queue, drop those older than the window, allow if the count is
  under the limit. All operations **O(1)** amortized.
- **Probe:** *Token bucket vs fixed window?* → fixed windows allow bursts at the
  boundary; token bucket smooths the rate. *Memory of the log approach?* → grows
  with requests in the window; the counter/bucket approach is O(1) space.
  *Exercises:* queues, amortized analysis — a favourite OS/networks exam topic.

### 10. Spell Checker / Dictionary (GATE strings + DP)
- **DS:** **hash set** (membership) + **BK-tree** or **Trie + edit-distance DP**
  for suggestions (Module 3/7/14).
- **Design:** store the dictionary in a hash set for O(1) "is this a word?"; for a
  misspelling, generate candidates within edit distance ≤ 2 and rank by frequency.
  A **BK-tree** prunes the search using the triangle inequality on edit distance.
- **Probe:** *Why edit distance?* → it models insert/delete/substitute typos as a
  classic DP (Module 14). *Why a BK-tree over brute force?* → it avoids scoring
  every dictionary word by pruning on the metric. *Exercises:* the edit-distance
  DP that GATE tests directly.

### MCQs

1. LRU cache core structures? → **HashMap + doubly linked list**.
2. Autocomplete core structure? → **Trie** (+ heap for ranking).
3. Mini-Git's history is a? → **DAG** (with Merkle hashing).
4. URL shortener code generation? → **base-62 of a counter**.
5. Rate limiter that smooths bursts uses? → **token bucket** (refill at a fixed
   rate).
6. Spell-checker suggestions rank candidates within a small **edit distance** —
   which paradigm computes edit distance? → **dynamic programming**.
7. Search-engine top-N ranking of many scored docs uses a? → **size-N heap**.
8. Detecting an impossible job-dependency set means finding a? → **cycle in the
   DAG** (topological sort fails).

---

## 25.2a Rubric — Score Your Own Project (before you show it)

Rate each project **0 / 1 / 2** (missing / partial / solid). Aim for **12+/16**
before you put it on a resume or bring it to an interview.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| **Correctness** | crashes / wrong output | happy path only | happy path + edge cases pass |
| **Right data structure** | unjustified choice | works but suboptimal | optimal + you can defend it |
| **Complexity stated** | unknown | rough guess | time **and** space, per operation |
| **Edge cases** | none handled | some | empty / full / duplicate / overflow |
| **Tests** | none | a few asserts | unit + one stress/randomized test |
| **API design** | ad-hoc | usable | clean, minimal, documented |
| **README / talking points** | none | what it does | design + DS *why* + scaling notes |
| **Scaling story** | none | "add a cache" | concrete: sharding / concurrency / limits |

> **Memory hook:** an interviewer scores the **same eight things** — grade
> yourself first, then close the gaps. A 2/2 README is your interview script.

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
- Two exam-flavoured extras: **rate limiter** (queue / token-bucket, amortized
  O(1) — OS/networks) and **spell checker** (hash set + edit-distance DP / BK-tree
  — GATE strings). Grade every project on the **§25.2a rubric** (aim 12+/16).

## Module 25 — Flash Cards

- Q: LRU cache? **A: hashmap + doubly linked list (O(1)).**
- Q: Autocomplete? **A: trie + top-k heap.**
- Q: Mini-Git? **A: DAG of commits + Merkle hashing.**
- Q: Search index core? **A: inverted index (+ trie + ranking heap).**
- Q: Allocator structures? **A: free lists / segregated bins / buddy system.**
- Q: Rate limiter that smooths bursts? **A: token bucket.**
- Q: Spell-checker suggestions rely on? **A: edit-distance DP (+ BK-tree pruning).**
- Q: Score your project before showing it? **A: the §25.2a rubric, target 12+/16.**

## Module 25 — Pattern Recognition

- "O(1) get/put with eviction" → hashmap + DLL.
- "Prefix suggestions" → trie (+ heap).
- "Short unique IDs" → base-62 of a counter.
- "Version history / content integrity" → DAG + Merkle.
- "Run jobs by priority/dependency" → heap + topological sort.
- "Cap requests per user per window" → token bucket / sliding-window queue.
- "Nearest word / typo correction" → edit-distance DP (+ BK-tree).

## Module 25 — Interview Questions

1. *Design an LRU cache.* (then LFU, TTL, thread-safety.)
2. *Design TinyURL.* (encoding, collisions, scale.)
3. *Design autocomplete at scale.* (trie + precomputed top-k + sharding.)
4. *How does Git store and dedupe objects?* (content hashing / Merkle.)

## Module 25 — GATE / SEBI / RBI / ISRO Perspective

- Projects aren't directly examined, but building a **memory allocator**,
  **scheduler**, or **B+-tree index** deeply reinforces OS/DBMS exam topics.
- The **rate limiter** cements queues + amortized analysis (OS/networks MCQs) and
  the **spell checker** cements the **edit-distance DP**, which GATE tests almost
  every year — so these two double as exam revision, not just resume material.

---

*End of Module 25. Next: Module 26 — Revision Kit (cheat sheets, complexity
tables, roadmaps, the dependency graph, and the Top-300 plan) — the finale.*
