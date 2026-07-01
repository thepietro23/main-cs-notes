---
title: "Module 7 — Indexing & Hashing"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — Indexing & Hashing

> **Where this module sits.**
> Module 6 told us the painful truth: disk is ~100,000× slower than RAM, and the
> cost of a query is "how many **blocks** did we read?" An **index** is the data
> structure that turns an O(n) full scan into an O(log n) — or O(1) — lookup. This
> is the **single most important performance topic** in databases, and one of the
> **highest-scoring** areas in GATE (B+ tree order/height numericals appear almost
> every year). Get B+ trees right and you understand how every real database makes
> queries fast.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **B+ tree order / fan-out /
height** numericals; **B-tree vs B+ tree** differences; **dense vs sparse**;
**primary vs clustering vs secondary** index; **B+ tree insertion (leaf split,
copy-up)**; **extendible hashing** (global/local depth, directory doubling);
**static hashing** & overflow; **bitmap** index; number of block accesses for a
search.

---

## 7.1 What Is an Index? (first principles)

### Motivation

To find "the customer with id 5000" in a 10-million-row table with **no** index,
the DBMS must scan every block — potentially **hundreds of thousands** of disk
reads. An **index** is a small, sorted auxiliary structure of `(search-key,
pointer)` entries that lets us locate the record with a handful of reads — exactly
like the **index at the back of a book**.

![An index: a small sorted file of (search-key, pointer-to-record) entries pointing into a large, possibly unsorted data file.](images/67_index_concept.png)

- **Search key:** the attribute(s) the index is built on.
- **Index entry:** `(search-key value, pointer)` — the pointer locates the record
  or its block.
- The index is **small and sorted**, so we binary-search it, then make **one**
  jump to the data.

> **The fundamental trade-off:** an index **speeds up reads** but **costs extra
> space** and **slows down writes** (every INSERT/UPDATE/DELETE must also update the
> index). So you index the columns you *search/join/sort on*, not every column.

---

## 7.2 Ordered Indexes — Primary, Clustering, Secondary; Dense vs Sparse

![Index types: primary (data sorted on key, sparse), clustering (sorted on non-key), secondary (data not sorted on this key, must be dense); plus dense vs sparse.](images/68_index_types.png)

| Type | Data file is… | Density | How many per table |
|------|---------------|---------|--------------------|
| **Primary index** | **sorted** on this (usually key) field | usually **sparse** | **one** |
| **Clustering index** | **sorted** on a **non-key** (duplicate) field | sparse | one |
| **Secondary index** | **not** sorted on this field | must be **dense** | **many** |

> **Primary vs clustering:** both require the data file to be **physically sorted**
> on the indexed field. *Primary* is on a key (unique ordering field); *clustering*
> is on a non-key (records with the same value cluster together). A file can have
> **only one** physical sort order → **only one** primary/clustering index.

### Dense vs Sparse

- **Dense index:** an entry for **every** record (or every distinct search-key
  value). Faster lookups, **bigger** index.
- **Sparse index:** an entry for **every block** (one per block). Find the largest
  key ≤ target, then **scan within that block**. Smaller index, but **requires the
  data file to be sorted**.

> **Key rule (exam):** a **secondary** index **must be dense** — because the data
> file isn't sorted on that field, you can't "scan forward to find" a missing key,
> so every value needs its own entry. A **primary** index can be **sparse** (data
> is sorted, so one entry per block suffices).

> **Industry terminology — clustered vs non-clustered (SEBI/RBI MCQ):**
> - **Clustered index** = the **table is physically stored in the index's order**
>   (the data *is* the index leaf). This is the **primary/clustering** index —
>   **one per table** (a file has only one physical order). (In MySQL InnoDB the
>   primary key *is* the clustered index.)
> - **Non-clustered index** = a **separate structure** holding `(key → row
>   pointer)`, leaving the table in its own order. This is a **secondary** index —
>   **many per table**.
> So: *clustered ≈ primary/clustering (one); non-clustered ≈ secondary (many).*

### 7.2A Numerical — index size: dense vs sparse, primary vs secondary

The classic GATE/SEBI question: *how many blocks does the index itself occupy?* The
answer depends on **dense vs sparse** and on the **number of index entries**.

> **Given:** a file of `N = 100,000` records, each data block holds **10 records**
> (so `b_r = 10,000` data blocks), and each index entry `(key, pointer)` = **16 B**
> in a block of **1024 B** → an index block holds `⌊1024/16⌋ = 64` entries.

```text
SPARSE primary index  → one entry PER DATA BLOCK.
   entries = b_r = 10,000
   index blocks = ⌈10,000 / 64⌉ = ⌈156.25⌉ = 157 blocks.
   Search (single level, binary): ⌈log2 157⌉ + 1 = 8 + 1 = 9 block accesses.

DENSE index (e.g. a SECONDARY index) → one entry PER RECORD.
   entries = N = 100,000
   index blocks = ⌈100,000 / 64⌉ = ⌈1562.5⌉ = 1563 blocks.
   Search (binary on the dense index): ⌈log2 1563⌉ + 1 = 11 + 1 = 12 accesses.
```

> **The takeaways:** (1) a **sparse** index is ~`10×` smaller here (157 vs 1563
> blocks) because it stores one entry per *block*, not per *record* — but it needs
> the file **sorted**. (2) A **secondary** index has **no choice** but to be dense
> (`100,000` entries) because the data isn't sorted on its key. (3) The number of
> distinct values matters: if the dense index keeps one entry per **distinct
> value** and there are only `2,000` distinct values, that is `⌈2000/64⌉ = 32`
> blocks instead of `1563`.

---

## 7.3 Multilevel Indexes → the idea behind trees

A single-level index can itself become too large to search quickly. Solution:
**build an index on the index**, repeating until the top level fits in one block.

![Multilevel index: an outer index points to inner index blocks, which point to data blocks — repeated until the top fits in one block.](images/69_multilevel_index.png)

> **ISAM (Indexed Sequential Access Method)** is the classic **static** multilevel
> ordered index — the historical predecessor to B+ trees. It's built once over a
> sorted file; the index levels are **fixed**. Its weakness: **inserts** go to
> **overflow chains** (the static index can't grow/rebalance), so after many inserts
> the overflow chains get long and performance **degrades** — exactly the problem
> dynamic trees solve.

> **This is precisely the idea behind B-trees and B+ trees** — a multilevel,
> **self-balancing** index that automatically keeps itself shallow as data grows
> and shrinks (unlike static ISAM). Next we build them.

---

## 7.4 B-Trees

A **B-tree** of order *p* is a balanced multilevel index where:

- each node holds up to **p − 1 keys** and **p child-pointers**,
- every node (except the root) is at least **half full** (≥ ⌈p/2⌉ children),
- **keys appear at every level**, and **each key carries a pointer to its data
  record**.

![B-tree node: pointers and keys, with a data pointer attached to every key at every level; a search can stop early at an internal node.](images/70_btree_node.png)

> **The B-tree property:** because keys (with their data pointers) live at *all*
> levels, a search can **stop early** if it finds the key in an internal node. But
> this also means internal nodes carry data pointers, which **lowers the fan-out**
> (fewer keys per node), making the tree taller — the downside B+ trees fix.

---

## 7.5 B+ Trees — the index every database actually uses

A **B+ tree** modifies the B-tree with one decisive change: **data pointers live
ONLY in the leaves**, and **all leaves are linked** in a sorted list.

![B+ tree: internal nodes are routers (keys only), all keys appear in the sorted leaves which hold the data pointers and are connected as a linked list; separator = smallest key of the right subtree.](images/71_bplus_structure.png)

- **Internal nodes are pure routers** — their keys only *guide* the search; they
  hold **no** data pointers.
- **All keys appear in the leaves** (sorted). A separator key in an internal node
  equals the **smallest key of its right subtree**, so it *also* appears in a leaf
  (the internal copy is just a router).
- **Leaves are a linked list** → **range queries** are trivial: find the start
  leaf, then walk the links.

> **Why B+ trees win (and why "database index" ≈ B+ tree):** because internal
> nodes carry **no data pointers**, they pack **more keys per node** → **higher
> fan-out** → a **shorter tree** → **fewer disk reads**. Plus, linked leaves make
> range scans cheap. Almost every RDBMS index (MySQL, PostgreSQL, Oracle) is a B+
> tree.

### B-tree vs B+ tree (a guaranteed comparison)

![B-tree vs B+ tree comparison: data location, key repetition, linked leaves, range queries, fan-out/height, search cost.](images/72_btree_vs_bplus.png)

| Aspect | B-Tree | B+ Tree |
|--------|--------|---------|
| Data pointers | at **all** nodes | **only in leaves** |
| Keys | each key appears **once** | internal keys **repeat** in leaves |
| Leaves linked? | no | **yes** (linked list) |
| Range queries | awkward (traversal) | **excellent** (walk leaf links) |
| Fan-out / height | lower fan-out, taller | **higher fan-out, shorter** |
| Search cost | may stop early | **always reaches a leaf** (uniform) |

---

## 7.6 B+ Tree: Order, Fan-out & Height (the GATE numerical)

![B+ tree order, fan-out and height: deriving order p from block size, and how high fan-out gives tiny height for millions of keys.](images/73_bplus_order_height.png)

**Finding the order *p*** (internal node) from the block size:

```
p × (block-pointer size) + (p − 1) × (key size) ≤ Block size
```

> **Worked example:** Block = 4096 B, key = 4 B, block-pointer = 8 B.
> `8p + 4(p − 1) ≤ 4096` → `12p − 4 ≤ 4096` → `12p ≤ 4100` → `p ≤ 341.67` → **p =
> 341** (take the floor).

**Height & search cost:** with fan-out *p* and *N* search-key values,
`height ≈ ⌈log_p(N)⌉`, and a search reads **(height + 1)** blocks (root → leaf).

> **The "wow" fact:** fan-out 341 → `341³ ≈ 39.6 million` keys in a tree of
> **height 3** → a key among ~40 million is found in just **~4 disk reads**. *That*
> is why B+ trees dominate. (Internal nodes are usually cached in RAM, so real
> lookups are even faster.)

**Leaf node order *p_leaf*:** a leaf holds `(search-key, record-pointer)` pairs plus
one **next-leaf pointer**: `p_leaf × (key + record-pointer) + (block-pointer) ≤
Block size`.

> **Balance guarantee:** every internal node (except root) has **≥ ⌈p/2⌉**
> children, so the tree can never become a skewed chain — height stays `O(log N)`.

### 7.6A Full numerical — order, leaf order, height & records held

A complete GATE-style problem that chains **internal order → leaf order → number
of levels → records addressable**. Watch the two *different* order formulas.

> **Given:** block = **4096 B**, search-key = **4 B**, block-pointer (to another
> index node) = **8 B**, record-pointer (to a data record) = **8 B**.

```text
(1) INTERNAL order p  (p pointers + (p−1) keys):
      8p + 4(p−1) ≤ 4096  →  12p ≤ 4100  →  p ≤ 341.6  →  p = 341
      → an internal node fans out to up to 341 children.

(2) LEAF order p_leaf  ((key + record-ptr) pairs + one next-leaf pointer):
      p_leaf·(4 + 8) + 8 ≤ 4096  →  12·p_leaf ≤ 4088  →  p_leaf ≤ 340.6
      → p_leaf = 340   (a leaf holds up to 340 data entries).

(3) MAX records addressable at each height (best/most-full case):
      height 1 (root is a leaf) : 340 records
      height 2 : 341 leaves × 340        ≈ 115,940 records
      height 3 : 341² leaves × 340       ≈ 39.5 million records
      height 4 : 341³ × 340              ≈ 13.5 billion records

(4) SEARCH COST for a key among, say, 40 million records:
      height = 3, so a root→leaf path = 3 index-block reads + 1 data-record read
      = 4 disk accesses  (and internal levels are usually cached → ~1 real read).
```

> **Two traps in one problem:** (a) internal order uses the **block-pointer** (8 B),
> leaf order uses the **record-pointer** and an extra **next-leaf pointer** — they
> give *different* orders (341 vs 340). (b) "Height" conventions differ: some texts
> count **levels** (root = level 1), some count **edges** (root→leaf = height 2).
> State your convention; the **number of block reads = number of levels**.

---

## 7.7 B+ Tree Insertion (leaf split & copy-up)

![B+ tree insertion: inserting 25 into a full leaf [10,20,30] overflows; the leaf splits into [10,20] and [25,30], and 25 (smallest of the right half) is copied up to the parent.](images/74_bplus_insertion.png)

**Algorithm:** find the correct leaf; insert in sorted order. If the leaf
**overflows** (more than the max keys), **split** it into two and **copy up** the
smallest key of the **right** half to the parent. If the parent overflows too,
split it (internal split **moves up** the middle key) — recursively up to the root.

> **The crucial leaf-vs-internal distinction (exam favourite):**
> - **Leaf split → COPY UP**: the separator key is **copied** to the parent and
>   **also stays** in the leaf (all keys must remain in the leaves).
> - **Internal split → MOVE UP (push up)**: the middle key **moves** to the parent
>   and is **removed** from the node (internal keys are only routers).

> **Worked (from the diagram):** insert 25 into a B+ tree leaf `[10,20,30]` (max 3
> keys). It overflows to `[10,20,25,30]` → split into `[10,20]` and `[25,30]`,
> **copy up 25**. The root `[40]` becomes `[25,40]`, now with three leaves
> `[10,20] [25,30] [40,50]` — and you can verify the routing: `<25 → [10,20]`,
> `25≤k<40 → [25,30]`, `≥40 → [40,50]`. ✔

> **Deletion (brief):** remove the key from its leaf; if the node **underflows**
> (drops below its **minimum occupancy** — roughly **half full**, the exact
> threshold depends on the textbook's leaf-capacity convention), **borrow** a key
> from a sibling, or **merge** with a sibling and adjust the parent (which may
> cascade up). Symmetric to insertion. *(For numericals, always use the
> minimum-fill convention your exam/textbook states.)*

### 7.7A Worked Insertion with an INTERNAL-node split (cascading up)

The 7.7 example split only a leaf. The next case is the one exams love: an insert
that **cascades** — a leaf split forces the parent to split too, growing a **new
root** (the *only* way a B+ tree gets taller).

![Inserting 16 splits a leaf (copy-up 16), which overflows the root and forces an internal split that MOVES 16 up into a brand-new root, increasing tree height by one.](images/175_bplus_internal_split.png)

**Setup:** order `p = 3` → each node holds **max 2 keys** (and min 1). Start with
root `[13 | 24]` and leaves `[5,9] [13,20] [24,30]`.

```text
Insert 16:
  1. Route 16: 13 ≤ 16 < 24  → goes to leaf [13,20].
  2. Leaf becomes [13,16,20] → 3 keys > max 2 → OVERFLOW → split.
       left leaf = [13],  right leaf = [16,20]
       COPY UP the smallest key of the right half = 16  → to parent.
  3. Parent (root) [13,24] must absorb 16 → [13,16,24] → 3 keys > max 2 → OVERFLOW.
       This is an INTERNAL node → split by MOVING UP the middle key (16):
         left internal = [13],  right internal = [24],  push 16 into a NEW root.
  4. New root = [16]. Height increased by 1.
```

**Final tree** (verify the routing is still correct):

```text
                 [16]
             /          \
          [13]          [24]
         /    \        /     \
     [5,9]  [13]   [16,20]  [24,30]
```

> **The two behaviours side by side (the classic MCQ trap):**
> - **Leaf split → COPY-UP:** the separator (16) is **copied** up **and kept** in the
>   right leaf `[16,20]` (every key must still be reachable in a leaf).
> - **Internal split → MOVE-UP:** the middle key (16) **moves** up and is **removed**
>   from the internal level (internal keys are pure routers, never data).
> - **A B+ tree grows ONLY at the root** (via an internal split that creates a new
>   root) — that is why all leaves stay at the **same depth** (perfectly balanced).

### 7.7B Worked Deletion with borrow & merge (underflow)

Deletion is the mirror image: remove the key, and if a node drops below its
**minimum occupancy** it must **borrow** from a sibling (redistribute) or **merge**.

**Setup:** order `p = 3` (min 1 key per non-root node). Leaves
`[5,7] [13,20] [24,30]` under root `[13 | 24]`.

```text
Case A — BORROW (sibling has a spare key):
  Delete 20  → leaf [13,20] becomes [13]  (still 1 key = min → OK, no underflow).
  Delete 13  → leaf becomes []  → UNDERFLOW (below min 1).
    Left sibling [5,7] has 2 keys (a spare) → BORROW its largest key 7.
      leaf becomes [7]; and UPDATE the parent separator (7's old position) → 7.
    Result: root [7 | 24], leaves [5] [7] [24,30].  Borrow = redistribute + fix separator.

Case B — MERGE (no sibling can spare a key):
  Now delete 5 → leaf [5] becomes [] → UNDERFLOW.
    Right sibling [7] has only 1 key (min) → cannot lend → MERGE the two leaves.
      merged leaf = [7]; DROP the separator (7) from the parent.
    Parent loses a key/pointer → may itself underflow → the merge can CASCADE up
    (a merge at the root that empties it shrinks the tree's height by 1).
```

> **Borrow vs merge — the rule:** on underflow, **borrow** if an adjacent sibling
> has **more than the minimum** keys (cheap, local); otherwise **merge** with a
> sibling and pull the separator down, which may **propagate** upward. A **merge is
> the only way a B+ tree shrinks in height** — the exact dual of a root split.

---

## 7.8 Hashing — O(1) Lookups by Key

Indexes give O(log n); **hashing** aims for **O(1)** average lookups for
**equality** searches. A **hash function** maps a key to a **bucket** (a block).

### Static hashing

![Static hashing: h(key)=key mod 4 maps each key to one of 4 fixed buckets; collisions go to an overflow chain.](images/75_static_hashing.png)

`bucket = h(key)`, e.g. `h(key) = key mod (#buckets)`. Multiple keys hashing to the
same bucket are stored together; when a bucket fills, extras go to an **overflow
chain**.

> **Collision-resolution methods (exam contrast):**
> - **Chaining (closed addressing):** overflowing records go to **linked overflow
>   buckets** — the bucket "chains" extra blocks. *(This is what DB static hashing
>   typically uses.)*
> - **Open addressing:** on collision, **probe** for another free slot —
>   **linear probing** (next slot), **quadratic probing**, or **double hashing**.
>   No overflow chain, but clustering can hurt.

> **The fatal flaw of static hashing:** the **number of buckets is fixed**. As data
> grows, overflow chains get long and lookups degrade toward **O(n)**. As data
> shrinks, buckets sit empty. Fixing this requires **dynamic hashing**.

### Extendible hashing (dynamic)

![Extendible hashing: a directory addressed by the first d bits (global depth) of the hash points to buckets with their own local depth; overflow either splits a bucket or doubles the directory.](images/76_extendible_hashing.png)

Extendible hashing grows gracefully using a **directory**:

- **Global depth (d):** how many leading bits of `h(key)` the **directory** uses
  (directory size = `2^d`).
- **Local depth:** how many bits a **particular bucket** agrees on.
- **On overflow:**
  - if `local depth < global depth` → just **split that bucket** (local depth++),
  - if `local depth == global depth` → **double the directory** (global depth++),
    then split.

> **The big win:** only **one bucket** splits at a time — **no full rehash** of all
> data (unlike rebuilding a static hash table). The directory doubles occasionally,
> but buckets are shared.

> **Linear hashing** is another dynamic scheme that grows buckets **one at a time
> in a fixed order** *without* a directory (using a split pointer). Know it exists;
> extendible hashing is the one GATE tests in detail.

#### Extendible hashing — worked trace (directory doubling)

![A full bucket whose local depth equals the global depth forces the directory to double; only that one bucket splits while the others are simply shared by two directory entries.](images/176_extendible_doubling.png)

**Setup:** bucket capacity = **2** records; hash on the **low-order bits** of the
key (so key `k` is placed by the last `d` bits of `k`, where `d` = global depth).
Start at **global depth d = 1**, directory `{0, 1}`:

```text
State:  d = 1
  dir[0] → bucket A (local depth 1) : {4, 12}      (…0 in the last bit)
  dir[1] → bucket B (local depth 1) : {5, 13}      (…1 in the last bit)   ← FULL

Insert 7  (7 = …0111, last bit = 1) → must go to bucket B.
  B is FULL and local_depth(B) == global_depth (1 == 1)
  → DOUBLE the directory: d becomes 2, entries {00, 01, 10, 11}.
  → SPLIT bucket B using the last 2 bits:
       B0 (local 2) holds keys ending 01 : {5, 13}   (5=…01, 13=…01)
       B1 (local 2) holds keys ending 11 : {7}       (7=…11)
  → bucket A was NOT touched: its local depth stays 1, so BOTH dir[00] and dir[10]
    still point to the same A (no rehash of A's records).

State:  d = 2
  dir[00] → A  (local 1)         dir[10] → A  (local 1, shared)
  dir[01] → B0 (local 2): {5,13}
  dir[11] → B1 (local 2): {7}
```

> **The exam rhythm:** compare **local depth** vs **global depth** on every
> overflow. `local < global` → split the bucket only (local++). `local == global`
> → **double the directory** (global++) **then** split. **Directory size = 2^d**;
> a bucket with local depth `ℓ` is pointed to by `2^(d−ℓ)` directory entries (that
> is why A, with `ℓ=1` under `d=2`, is shared by `2` entries).

### Hashing vs B+ tree

> **Decision:** **hash** = O(1) for **exact-match** (`WHERE id = 5`) but **useless
> for ranges** (it scatters neighbouring keys). **B+ tree** = O(log n) but handles
> **both** equality *and* ranges/sorting. That's why B+ tree is the default index.

---

## 7.9 Bitmap Index

![Bitmap index: one bit-vector per distinct column value; a query reads the matching bitmap (and ANDs/ORs bitmaps for multi-condition queries).](images/77_bitmap_index.png)

A **bitmap index** stores, **per distinct value**, a **bit-vector** with one bit
per row (1 = this row has that value). Query `gender = 'F'` just reads the `F`
bitmap; multi-condition queries (`F AND active`) are fast bitwise `AND`/`OR`.

- **Best for low-cardinality columns** (gender, status, yes/no) used in analytics.
- **Bad for high-cardinality** (too many bitmaps) and **frequent updates** (bit
  maintenance is costly).

---

## 7.10 Choosing an Index

![Flowchart: range queries → B+ tree; exact-match only → hash (or bitmap if low cardinality); default → B+ tree.](images/78_fc_index_choice.png)

- **Range queries / sorting / general purpose →** **B+ tree** (the default).
- **Pure equality lookups →** **hash** index (O(1)).
- **Low-cardinality analytics columns →** **bitmap**.
- **Don't over-index:** each index speeds reads but slows every write and uses
  space.

---

## 7.11 Real-World & Backend Perspectives

- **`CREATE INDEX idx ON emp(dno);`** builds a B+ tree by default in PostgreSQL/
  MySQL. `EXPLAIN` shows whether the optimizer chose an **index scan** vs a **seq
  scan**.
- **Composite / covering indexes:** `INDEX(a, b)` helps `WHERE a=? AND b=?` and
  `WHERE a=?`, but **not** `WHERE b=?` (leftmost-prefix rule). A **covering index**
  includes all columns a query needs, so the table isn't touched at all.
- **Clustered index in practice:** in MySQL InnoDB the **primary key IS the
  clustered index** — the table is physically stored as that B+ tree.
- **Write amplification:** every index multiplies write cost; high-write tables
  keep indexes lean.

---

## 7.12 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Saying a **secondary** index can be **sparse** (it must be **dense**).
- Confusing **leaf split (copy-up)** with **internal split (move-up)**.
- Using **hashing** and expecting fast **range** queries (it can't).
- Forgetting B-tree stores data pointers at **all** levels (lower fan-out), B+ tree
  **only in leaves**.
- In the order formula, forgetting it's **p pointers but p−1 keys**.
- Thinking more indexes are always better (they slow writes).

**Edge cases**
- A table can have **only one** primary/clustering index (one physical sort order)
  but **many** secondary indexes.
- B+ tree with all internal nodes cached → a lookup is effectively **one** disk
  read (the leaf).
- Extendible hashing directory can **double** even when only one bucket was full.

**Tradeoffs**

| Index choice | Gain | Cost |
|--------------|------|------|
| B+ tree | range + equality, shallow | update cost, space |
| Hash | O(1) equality | no ranges, resize pain (static) |
| Bitmap | fast multi-condition on low-cardinality | bad for high-cardinality / updates |
| More indexes | faster reads | slower writes, more space |

---

## 7.13 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** compute B+ tree **order** from block size; **height** /
block accesses; dense vs sparse; primary vs clustering vs secondary; B-tree vs B+
tree; leaf split copy-up; extendible hashing global/local depth & directory
doubling; static hashing overflow; bitmap use-case.

**Interview:** "Why are database indexes B+ trees, not hash tables or binary search
trees?" (disk-friendly high fan-out + ranges); "What's a covering index?"; "When
does an index hurt?" (write-heavy tables); "leftmost-prefix rule".

**Coding/practical:**
- `CREATE INDEX` then `EXPLAIN ANALYZE` a query to see index scan vs seq scan.
- Build a composite index and test which `WHERE` clauses use it (leftmost prefix).

---

## 7.14 Concept Checks & MCQs

1. An index trades ___ for faster reads → **space + write cost**.
2. A secondary index must be ___ → **dense**.
3. Which can be sparse: primary or secondary? → **primary**.
4. In a B-tree, data pointers are at ___ → **every node**. In a B+ tree? → **only
   leaves**.
5. Which has higher fan-out (shorter tree)? → **B+ tree**.
6. B+ tree order: `8p + 4(p−1) ≤ 4096` → p = ? → **341**.
7. Leaf split in a B+ tree does ___ up; internal split does ___ up → **copy** /
   **move**.
8. Hashing is bad for which query type? → **range queries**.
9. In extendible hashing, the directory doubles when ___ → **a bucket's local depth
   equals the global depth and it overflows**.
10. Bitmap index is best for ___ columns → **low-cardinality**.
11. Max keys in a B-tree/B+ tree node of order p? → **p − 1**.
12. Leaves of a B+ tree are connected as a ___ → **linked list** (for ranges).
13. Clustered index ≈ ___ (one per table); non-clustered ≈ ___ (many) → **primary/
    clustering** / **secondary**.
14. Static multilevel index whose inserts degrade via overflow chains? → **ISAM**.
15. Two collision-resolution families? → **chaining (closed addressing)** and **open
    addressing (probing)**.

**True/False**
- A B+ tree stores data pointers in internal nodes. → **False**.
- A table can have many clustering indexes. → **False** (one sort order).
- Static hashing handles growth gracefully. → **False** (fixed buckets).
- B+ tree internal keys also appear in leaves. → **True**.

**Numerical (do it):**
> Block = 1024 B, key = 6 B, pointer = 10 B. Find the B+ tree order p (internal).
> `10p + 6(p−1) ≤ 1024` → `16p − 6 ≤ 1024` → `16p ≤ 1030` → `p ≤ 64.4` → **p =
> 64**. With fan-out 64, height 3 holds `64³ ≈ 262,000` keys.

**More MCQs (7.6A–7.8A additions):**

16. Leaf split does ___ up; internal split does ___ up → **copy** / **move**.
17. The only way a B+ tree increases in height is by ___ → **an internal (root)
    split creating a new root**.
18. The only way a B+ tree decreases in height is by ___ → **a merge that empties
    the root**.
19. On deletion underflow, you first try to ___; if impossible you ___ → **borrow
    from a sibling** / **merge**.
20. Extendible hashing doubles the directory when a full bucket has ___ → **local
    depth = global depth**.
21. Directory size for global depth d? → **2^d**. A bucket of local depth ℓ is
    pointed to by ___ directory entries → **2^(d−ℓ)**.
22. Which two order formulas differ in a B+ tree — internal vs leaf? → internal
    uses **block-pointer**; leaf uses **record-pointer + a next-leaf pointer**.
23. Sparse primary index on 10,000 data blocks, 64 entries/index block → index
    blocks = ? → **⌈10000/64⌉ = 157**.
24. A dense index on 100,000 records at 64 entries/block → index blocks = ? →
    **⌈100000/64⌉ = 1563**.

**Numerical 2 (do it — extendible hashing):**
> Capacity 2, hash on **last** bits, d=2, dir {00,01,10,11}. Bucket for `…11` holds
> `{3, 7}` (both …11) with local depth 2 and is full. Insert `11` (=…1011, last two
> bits 11). It maps to the full bucket whose **local depth (2) = global depth (2)**
> → **double** the directory to d=3, then split that bucket by the last 3 bits:
> `3=…011`, `7=…111`, `11=…011` → `{3, 11}` (…011) and `{7}` (…111). ✔

**Numerical 3 (do it — internal vs leaf order):**
> Block 512 B, key 4 B, block-ptr 6 B, record-ptr 6 B.
> Internal: `6p + 4(p−1) ≤ 512 → 10p ≤ 516 → p = 51`.
> Leaf: `p_leaf·(4+6) + 6 ≤ 512 → 10·p_leaf ≤ 506 → p_leaf = 50`.

---

## 7.15 One-Page Revision Sheet

```
INDEX = (search-key, pointer) sorted aux structure. Trades SPACE + WRITE cost for fast reads.

ORDERED INDEXES:
  PRIMARY  : data sorted on key field; can be SPARSE; ONE per table.
  CLUSTERING: data sorted on NON-key; sparse; one per table.
  SECONDARY: data NOT sorted on field; MUST be DENSE; MANY per table.
  DENSE = entry per record. SPARSE = entry per block (data must be sorted).
  CLUSTERED index = table physically in index order (primary/clustering, ONE).
  NON-CLUSTERED = separate structure -> row pointers (secondary, MANY).

MULTILEVEL INDEX = index on index -> idea behind B/B+ trees.
ISAM = static multilevel ordered index; inserts -> overflow chains -> degrades (B+ tree fixes).

B-TREE: order p -> p pointers, p-1 keys; data ptrs at ALL nodes; keys appear ONCE; search may stop early.
B+ TREE: data ptrs ONLY in leaves; ALL keys in leaves (sorted); leaves LINKED LIST (range-good);
  internal = routers (separator = smallest key of right subtree). HIGHER fan-out -> shorter tree.
  -> the default RDBMS index.

ORDER from block: p*ptr + (p-1)*key <= Block.  e.g. 8p+4(p-1)<=4096 -> p=341.
HEIGHT ~ ceil(log_p N); search reads height+1 blocks. fan-out 341, h=3 -> ~40M keys in 4 reads.
MIN children (non-root) = ceil(p/2) -> balanced.

B+ INSERT: leaf overflow -> SPLIT + COPY UP smallest key of right half. internal overflow -> MOVE UP middle.
B+ DELETE: underflow (< ceil(p/2)-1) -> borrow from sibling or MERGE.

HASHING (equality O(1), NO ranges):
  STATIC: bucket=h(key)=key mod B; fixed buckets -> overflow chains as data grows (degrades).
  COLLISIONS: chaining (closed addressing, overflow buckets) vs open addressing (linear/quadratic probe).
  EXTENDIBLE: directory by first d bits (global depth); bucket local depth.
    overflow: local<global -> split bucket; local=global -> DOUBLE directory then split. No full rehash.
  LINEAR: grows one bucket at a time via split pointer, no directory.

BITMAP: one bit-vector per distinct value; AND/OR for multi-condition. LOW-cardinality only.

CHOOSE: ranges/sort/general -> B+ tree; pure equality -> hash; low-cardinality analytics -> bitmap.
```

### Flash cards

| Front | Back |
|-------|------|
| Secondary index density? | Must be dense |
| Primary index can be? | Sparse |
| Data pointers in B+ tree? | Only in leaves |
| Higher fan-out: B-tree or B+? | B+ tree |
| B+ order formula? | p·ptr + (p−1)·key ≤ block |
| Leaf split vs internal split? | Copy-up vs move-up |
| Hashing weakness? | Range queries |
| Extendible: directory doubles when? | local depth = global depth & overflow |
| Bitmap best for? | Low-cardinality columns |
| Leaves linked → good for? | Range queries |
| Max keys per order-p node? | p − 1 |

### Spaced repetition
- **24-hour:** compute B+ tree order & height for 2 block-size problems; redo MCQs.
- **7-day:** draw a B+ tree insertion with a leaf split (copy-up); explain B-tree vs B+.
- **30-day:** trace an extendible-hashing insert sequence that doubles the directory; pick the right index for 5 workloads.

---

## 7.16 Summary

Indexing is how databases beat the disk. An **index** is a small sorted
`(search-key, pointer)` structure that trades **space + write cost** for **fast
reads**. We classified **ordered indexes** — **primary** (sorted key, can be
sparse), **clustering** (sorted non-key), and **secondary** (unsorted field, must
be **dense**) — and the **dense vs sparse** distinction. Multilevel indexing led to
**B-trees** (data pointers at all levels) and the dominant **B+ tree** (data only
in **linked leaves**, internal nodes as **routers**, high **fan-out** → shallow
tree → few disk reads, great for **ranges**). We did the **order/height
numericals** (`p·ptr + (p−1)·key ≤ block`; fan-out 341 → ~40M keys in height 3) and
**insertion** (leaf split **copy-up** vs internal split **move-up**). Then
**hashing** for O(1) equality — **static** (fixed buckets, overflow) and the
dynamic **extendible** hashing (global/local depth, directory doubling, no full
rehash) — and **bitmap** indexes for low-cardinality analytics.

Next, **Module 8 — Query Processing & Optimization** uses these access methods and
the Module 6 cost model to decide *how* to actually run a query (which index, which
join algorithm), turning the relational algebra of Module 3 into an efficient
execution plan.

> **You have mastered this module when** you can: compute a B+ tree's order and
> height from block/key/pointer sizes; explain dense vs sparse and primary vs
> secondary; contrast B-tree and B+ tree and say why B+ wins; perform a B+ tree
> insertion with a leaf split (copy-up); and trace extendible hashing through a
> directory doubling — all without notes.
