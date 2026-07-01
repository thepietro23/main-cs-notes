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

### Worked probe trace — linear probing (a GATE favourite)

Table size **10**, `hash(k) = k % 10`, **linear probing** `(h + i) % 10`. Insert
**23, 43, 13, 27** in order.

```text
index:  0    1    2    3      4    5    6    7      8    9
insert 23 -> 23%10 = 3           -> slot 3 free  -> place at 3
insert 43 -> 43%10 = 3 (taken)   -> try 4        -> place at 4
insert 13 -> 13%10 = 3 (taken)   -> 4 taken, try 5 -> place at 5
insert 27 -> 27%10 = 7           -> slot 7 free  -> place at 7

final:  .    .    .    23    43   13    .    27    .    .
                       (0)  (+1) (+2)       (0 probes)

probes: 23->1, 43->2, 13->3, 27->1   (a "probe" = each slot examined)
```

This clustering — 43 and 13 piling up right after 23 — is exactly the **primary
clustering** weakness of linear probing. **Quadratic probing** `(h + i²) % 10`
would place 13 at `(3+4)%10 = 7`… but 7 is later needed by 27, showing why probe
order matters in exam questions. **Double hashing** uses a second hash for the
step so keys with the same home slot spread differently.

### Chaining vs Open Addressing (interview comparison)

| | Chaining | Open addressing |
|---|---|---|
| Memory | list pointers | none (in-array) |
| Cache | poor | good |
| High load factor | OK | degrades fast (keep α < ~0.7) |
| Delete | easy | needs tombstones |

### Perfect vs universal hashing (brief)

Two theory ideas GATE and interviews sometimes name-drop:

- **Universal hashing:** pick the hash function **at random** from a carefully
  designed *family* of functions. Then for any two distinct keys, the *expected*
  collision probability is ≤ 1/m (m = table size). This defends against
  adversarial inputs — an attacker cannot know your function in advance
  (mitigates "hash flooding"). It guarantees good behaviour **on average over the
  random choice**, not for every fixed function.
- **Perfect hashing:** for a **static, known** key set, build a hash function
  with **zero collisions** → true **O(1) worst-case** lookup. The standard
  construction is **two levels** (FKS): a top table, and for each bucket a small
  second table sized to that bucket's collisions, giving O(n) total space. Used
  for fixed dictionaries (keywords, CD-ROM indexes).

> **One-liner:** universal = *random* function, good on average, beats attackers;
> perfect = *no collisions* for a *fixed* key set, O(1) worst case.

### String hashing & collisions (a quick note)

The polynomial rolling hash (Module 3) `h = (h·B + c) mod M` can collide when two
different strings map to the same value — an **anagram-like** clash or a
deliberately crafted one. Defences:

- Use a **large prime modulus** `M` and a random base `B` (harder to attack).
- **Double hashing** for strings: keep **two** independent hashes; a collision
  now needs both to clash at once (astronomically unlikely). Common in
  competitive programming (Rabin–Karp, string sets).

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

## 7.3a Ordered vs Unordered Map, and When a Hashmap Is Wrong

### Ordered map vs unordered map (a common interview/GATE contrast)

| | Unordered (hash) map | Ordered (tree) map |
|---|---|---|
| Backing structure | hash table | balanced BST (Module 8) |
| insert / erase / find | **O(1) average** | **O(log n)** always |
| Worst case | O(n) (bad collisions) | **O(log n)** guaranteed |
| Keys in sorted order? | **no** | **yes** (in-order walk) |
| Range / "next key ≥ x" query | not supported | **O(log n)** |
| C++ name | `unordered_map` | `map` |
| Java name | `HashMap` | `TreeMap` |

> **Interview line:** "Use the hash map for raw speed; use the ordered/tree map
> when you also need **sorted iteration**, **range queries**, or a **guaranteed**
> worst case." A hash map has *no order at all*.

### When a hashmap is the WRONG choice

- **You need sorted order or range queries** ("all keys between 10 and 50",
  "smallest key ≥ x") → use a **balanced BST / ordered map** (Module 8).
- **You need the min/max repeatedly** and updates → use a **heap** (Module 6),
  not a hashmap (a hashmap has no cheap min).
- **Prefix / autocomplete lookups on strings** → use a **Trie** (Module 8), which
  a hashmap of full strings cannot do.
- **Hard real-time / worst-case guarantees** (avionics, some DB internals) → hash
  worst case is O(n); a balanced tree's O(log n) is guaranteed.
- **Tiny key sets or dense small integer keys** → a plain **array** indexed
  directly is faster and simpler (no hashing overhead).
- **Adversarial untrusted keys** → a naive hashmap risks **hash flooding**; use
  universal/randomised hashing or a tree map.

### MCQs

1. Ordered map find cost vs unordered? → **O(log n)** vs **O(1) average**.
2. Need "all keys in a range"? → use an **ordered (tree) map**, not a hashmap.
3. Need prefix/autocomplete on strings? → use a **Trie**, not a hashmap.

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

## 7.6 Consistent Hashing (a system-design tie-in)

### The problem with plain `hash(key) % N`

To spread keys over **N servers**, the obvious rule is `server = hash(key) % N`.
It works — until `N` changes. Add or remove **one** server and `N` changes, so
`% N` remaps **almost every key** → a massive, cache-busting data reshuffle. In a
distributed cache or database that is catastrophic.

### The idea — a hash ring

**Consistent hashing** hashes both **keys** and **servers** onto the same circle
(0 … 2³²−1). A key belongs to the **first server found clockwise** from the key's
position. Now adding/removing a server only moves the keys **between it and its
neighbour** — on average just **1/N of the keys**, not all of them.

![Consistent hashing ring: keys and servers hash onto a circle; each key goes to the next server clockwise, so adding a node moves only a small slice of keys.](images/171_consistent_hashing.png)

- **Virtual nodes:** place each physical server at **many** points on the ring
  (e.g. 100 virtual copies) so load spreads **evenly** and removing a server
  redistributes its keys across *many* others, not one unlucky neighbour.
- **Where it is used:** Amazon **DynamoDB**, **Cassandra**, **memcached**
  clients, and load balancers — anywhere nodes join/leave and you want minimal
  data movement.

> **Memory hook:** a **clock face** of servers — a key walks clockwise to the
> next server. Remove one clock number and only *its* slice of time reassigns.

### MCQs

1. Problem with `hash % N` when N changes? → **almost all keys remap** (huge
   reshuffle).
2. Consistent hashing moves how many keys when a node is added? → about **1/N**.
3. What are virtual nodes for? → **even load spread** across the ring.

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
- Q: Ordered vs unordered map find? **A: O(log n) vs O(1) average.**
- Q: Need range queries / sorted keys? **A: tree/ordered map, not a hashmap.**
- Q: Perfect vs universal hashing? **A: perfect = no collisions (static set); universal = random function, good on average.**
- Q: Why not plain hash % N across servers? **A: N changes remap nearly all keys; use consistent hashing.**
- Q: Consistent hashing keys moved on add? **A: ~1/N.**

## Module 7 — Pattern Recognition

- "Find a pair / complement / duplicate / count" → **hashmap / hashset**.
- "Subarray/substring sum or count = k" → **prefix sum + hashmap**.
- "Group things by a signature" → **hashmap keyed by the signature**.
- "Need O(1) get/put with recency" → **hashmap + linked list (LRU)**.
- "Huge set, only need 'probably present'" → **Bloom filter**.
- "Need sorted keys / range / next-greater key" → **ordered (tree) map, not hash**.
- "Distribute keys over servers that join/leave" → **consistent hashing (ring)**.
- "Prefix / autocomplete on strings" → **Trie, not a hashmap of strings**.

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
- **Also asked:** hash-table vs balanced-BST trade-offs (O(1) avg vs O(log n)
  guaranteed), and the "leave-one-slot" style capacity/probing details.
- **SEBI/RBI IT:** conceptual MCQs on hashing, collisions, and applications.
- **SEBI/RBI (system design angle):** rounds may touch **consistent hashing** and
  **Bloom filters**.

---

*End of Module 7. Next: Module 8 — Trees (binary trees, BST, traversals, AVL /
Red-Black, segment trees, Fenwick, Trie, B/B+ trees) — split across M08a & M08b,
with visuals.*
