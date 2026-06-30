---
title: "Module 7 — Hash Tables"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — Hash Tables

> **Why hash tables are everywhere.**
> A hash table gives **O(1) average** insert, delete, and lookup — the closest
> thing to magic in DSA. It is the secret weapon behind countless interview
> answers ("use a hashmap to go from O(n²) to O(n)"), and it underlies
> dictionaries, sets, database indexes, and caches. Knowing *how* it works (and
> *when* it degrades) separates a junior answer from a staff-level one.

This module is **P0** for interviews (hashmap is the #1 optimisation tool) and
**P0** for GATE (collision strategies, load factor, probing).

> **How to read each technique.** We go **Brute force → Better → Optimal** with
> pseudocode + complexity, plus a memory hook.

---

## 7.1 The Big Idea

### Definition

A **hash table** stores key→value pairs in an array of **buckets**. A **hash
function** turns a key into a bucket index: `index = hash(key) % table_size`. To
find a key, you hash it again and jump straight to its bucket — no scanning.

![Hash table: a hash function maps each key to a bucket index for O(1) average lookup.](images/57_hashing_basic.png)

> **Memory hook:** a **library with a magic formula** — instead of searching
> every shelf, the formula tells you the exact shelf for your book.

### What makes a *good* hash function

1. **Deterministic** — same key always gives the same index.
2. **Uniform** — spreads keys evenly across buckets (few collisions).
3. **Fast** — O(1) to compute.

For strings, the polynomial rolling hash from Module 3 is common.

### Complexity (the headline)

| Operation | Average | Worst case |
|---|---|---|
| insert / delete / search | **O(1)** | O(n) (all keys collide) |

The worst case (everything in one bucket) is rare with a good hash + resizing,
but adversarial inputs can trigger it (a real security topic: "hash flooding").

### MCQs

1. Bucket index formula? → `hash(key) % table_size`.
2. Average lookup time? → **O(1)**.
3. Three properties of a good hash? → **deterministic, uniform, fast**.

---

## 7.2 Collisions — when two keys want the same bucket

Two different keys can hash to the same index — a **collision**. There are two
main ways to handle them.

### Strategy 1 — Separate Chaining

Each bucket holds a **list** (or tree) of all keys that landed there. On
collision, append to that bucket's list.

![Separate chaining: each bucket is a linked list; colliding keys are appended.](images/58_chaining.png)

- **Pros:** simple; handles a high load factor gracefully; easy deletes.
- **Cons:** extra memory for list pointers; poor cache locality.
- Java's `HashMap` uses chaining, and converts a long chain to a **balanced
  tree** (O(log n)) to avoid worst-case O(n).

### Strategy 2 — Open Addressing (probing)

Keep everything **inside the array**. On collision, **probe** for the next free
slot:

![Open addressing (linear probing): on a collision, try the next slot until a free one is found.](images/59_open_addressing.png)

- **Linear probing:** try `i+1, i+2, …` (cache-friendly but causes "clustering").
- **Quadratic probing:** try `i+1, i+4, i+9, …` (less clustering).
- **Double hashing:** the step size comes from a *second* hash (best spread).
- **Delete needs a "tombstone":** a special marker, because a truly empty slot
  would wrongly stop a future probe sequence.

### Chaining vs Open Addressing (interview comparison)

| | Chaining | Open addressing |
|---|---|---|
| Memory | list pointers | none (in-array) |
| Cache | poor | good |
| High load factor | OK | degrades fast (keep α < ~0.7) |
| Delete | easy | needs tombstones |

### MCQs

1. Two strategies for collisions? → **chaining** and **open addressing**.
2. Why a tombstone in open addressing? → so deletes don't **break probe chains**.
3. Which is more cache-friendly? → **open addressing**.

---

## 7.3 Load Factor & Rehashing

### Definition

**Load factor** `α = (number of items) / (number of buckets)`. As `α` rises,
collisions rise and operations slow down. When `α` crosses a threshold (e.g. 0.7
for open addressing, ~1 for chaining), the table **rehashes**: allocate a bigger
array (usually 2×) and **re-insert** every item.

![Load factor: when the table gets too full, it rehashes into a bigger array (doubling), lowering the load factor.](images/60_load_factor.png)

- Rehashing is **O(n)**, but it happens rarely (like dynamic-array doubling,
  Module 2) → **amortised O(1)** per insert.

> **Memory hook:** same as the dynamic array — when the room is too crowded, move
> to a hall twice as big and let everyone re-seat.

### MCQs

1. Load factor formula? → **items / buckets**.
2. What happens at a high load factor? → **rehash** (grow + re-insert).
3. Amortised insert cost despite O(n) rehash? → **O(1)**.

---

## 7.4 Hash Table Applications (the interview workhorses)

The pattern is almost always: **"a hashmap turns an O(n²) scan into O(n)."**

### Two Sum (the canonical example)

```text
# BRUTE FORCE                                O(n^2)
for i, for j>i: if a[i]+a[j]==target: return (i,j)

# OPTIMAL: hashmap of seen values            O(n) time, O(n) space
seen = {}                       # value -> index
for i, x in enumerate(a):
    if target - x in seen: return (seen[target-x], i)
    seen[x] = i
```

> **Why it helps:** instead of searching for the complement, we *remember* every
> number we've seen, so each lookup is O(1).

### Other classics

- **Group Anagrams (LC 49):** key = sorted word (or its 26-letter count); group
  by that key.
- **Subarray Sum equals K (LC 560):** store **prefix sums** in a hashmap; for each
  prefix `P`, check if `P − k` was seen (links Module 2 + Module 7).
- **First unique character, frequency counts, dedup, two-list intersection** — all
  hashmap/hashset in O(n).
- **LRU Cache (Module 4):** hashmap + doubly linked list.

### MCQs

1. Two Sum optimal time/space? → **O(n) / O(n)**.
2. "Subarray sum = k" tool? → **prefix sum + hashmap**.
3. Group anagrams key? → **sorted word** or **letter-count signature**.

### Problems

- Two Sum (1); Group Anagrams (49); Subarray Sum Equals K (560); Top K Frequent
  (347); Longest Consecutive Sequence (128); Contains Duplicate (217); LRU Cache
  (146).

---

## 7.5 Probabilistic Structures (Bloom Filter)

### The idea

A **Bloom filter** is a tiny bit-array that answers "is `x` in the set?" with
either **"definitely NOT"** or **"maybe yes"** — using far less memory than
storing the items. It can give **false positives** but **never false negatives**.

![Bloom filter: several hashes set bits; if any bit is 0 the item is definitely absent, otherwise maybe present.](images/61_bloom_filter.png)

```text
add(x):    for each of k hash functions: set bit[ hash_i(x) ] = 1
query(x):  if any bit[ hash_i(x) ] == 0 -> definitely NOT present
           else -> maybe present (small false-positive chance)
```

- **Use it to skip expensive work:** databases (Cassandra, Bigtable) and caches
  check a Bloom filter first — if it says "not present", they avoid a costly disk
  lookup.
- **Cousins:** Count-Min Sketch (approximate counts), HyperLogLog (approximate
  distinct-count) — great "system design + DSA" name-drops.

> **Memory hook:** a **bouncer with a fuzzy memory** — "I've definitely never
> seen you" is reliable; "you look familiar" might be wrong.

### MCQs

1. Bloom filter error type? → **false positives only** (never false negatives).
2. One real use? → **skip disk lookups** in databases/caches.

---

## Module 7 — Concept Review (one page)

- **Hash table** = buckets + hash function; `index = hash(key) % size`; **O(1)
  average**, O(n) worst.
- **Good hash** = deterministic, uniform, fast.
- **Collisions:** **chaining** (bucket = list; cache-poor, high-load-friendly) vs
  **open addressing** (in-array probing; cache-good, needs tombstones, keep
  α<0.7).
- **Load factor** α = items/buckets; high α → **rehash** (2× + re-insert),
  amortised O(1).
- **Applications:** the universal "O(n²) → O(n)" tool — Two Sum, anagrams,
  subarray-sum-k (prefix+map), frequency, LRU.
- **Bloom filter** = bit-array, "definitely no / maybe yes", false positives only.

## Module 7 — Flash Cards

- Q: Hash table average op cost & worst? **A: O(1) / O(n).**
- Q: Two collision strategies? **A: chaining, open addressing.**
- Q: Why tombstones? **A: keep probe chains intact after deletes.**
- Q: Load factor & action when high? **A: items/buckets; rehash (grow + re-insert).**
- Q: Two Sum optimal? **A: hashmap of seen, O(n).**
- Q: Subarray sum = k? **A: prefix sum + hashmap.**
- Q: Bloom filter error? **A: false positives only, never false negatives.**

## Module 7 — Pattern Recognition

- "Find a pair / complement / duplicate / count" → **hashmap / hashset**.
- "Subarray/substring sum or count = k" → **prefix sum + hashmap**.
- "Group things by a signature" → **hashmap keyed by the signature**.
- "Need O(1) get/put with recency" → **hashmap + linked list (LRU)**.
- "Huge set, only need 'probably present'" → **Bloom filter**.

## Module 7 — Interview Questions (with follow-ups)

1. *Two Sum.* FU: *what if the array is sorted?* → two pointers (Module 2).
2. *Design a hashmap from scratch.* FU: *collisions? resizing? load factor?*
3. *Subarray sum equals K.* FU: *why does prefix-sum + map work?*
4. *When does a hashmap degrade to O(n)?* FU: *how to defend (good hash, tree
   buckets)?*
5. *Design a spell-checker / URL dedup at scale.* FU: *Bloom filter trade-offs.*

## Module 7 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** **linear/quadratic/double hashing** probe sequences (trace
  where keys land), load factor effects, chaining vs open addressing, and
  "number of probes" calculations. Very frequently tested.
- **SEBI/RBI IT:** conceptual MCQs on hashing, collisions, and applications.

---

*End of Module 7. Next: Module 8 — Trees (binary trees, BST, traversals, AVL /
Red-Black, segment trees, Fenwick, Trie, B/B+ trees) — split across M08a & M08b,
with visuals.*
