---
title: "Module 8 — Query Processing & Optimization"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8 — Query Processing & Optimization

> **Where this module sits.**
> Module 3 gave us relational algebra (*what*), Module 4 gave us SQL, Modules 6–7
> gave us the cost model (block I/O) and access methods (indexes). Now we answer:
> *how does the DBMS actually run a query, and how does it choose the fastest way?*
> The same SQL can run **1000× faster or slower** depending on the **plan** the
> optimizer picks. This module is the bridge from "a query" to "an efficient
> execution" — and the **join-algorithm cost** numericals are a GATE staple.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **join algorithm costs**
(nested-loop / block / indexed / sort-merge / hash); **measures of query cost**
(block transfers + seeks); **selection algorithm costs**; **external merge sort**
passes; **materialization vs pipelining**; **heuristic optimization** (push
selection down) & **equivalence rules**; **cost-based optimization & join order**.

---

## 8.1 The Query Processing Pipeline

A query travels through four stages before producing results.

![Query processing pipeline: SQL → parser/translator (to relational algebra) → optimizer (pick cheapest plan using statistics) → evaluation engine → result, with the catalog and statistics feeding the optimizer.](images/79_query_pipeline.png)

1. **Parser & translator** — checks syntax/semantics (does the table exist? is the
   user allowed?) and converts the SQL into a **relational-algebra** expression.
2. **Optimizer** — generates many equivalent **plans** and picks the **cheapest**
   using the **catalog** (schema, indexes) and **statistics** (table sizes, value
   distributions).
3. **Evaluation engine** — executes the chosen plan (access methods + join
   algorithms).
4. **Result** — rows returned.

> **First-principles point:** a *query* (SQL) says **what** you want; a **query
> plan** (a.k.a. *evaluation plan*) is a specific **annotated algebra tree** saying
> exactly **how** — which index to use, which join algorithm, in what order. The
> optimizer's job is to choose the best plan among many that all give the **same
> answer**.

---

## 8.2 Measuring Query Cost

We measure cost in **disk I/O**, because (Module 6) disk dominates. The standard
cost model counts:

```
Cost = (#block transfers × transfer-cost) + (#seeks × seek-cost)
```

![Query cost is measured in disk I/O (block transfers + seeks); selection algorithms (linear scan, binary search, primary/secondary index) with their block-transfer costs.](images/80_cost_selection.png)

**Notation** (memorize — used in every formula): `b_r` = number of **blocks** of
relation r; `n_r` = number of **tuples** of r; `M` = number of memory **buffer
blocks** available.

> We usually report cost as **number of block transfers** (sometimes also seeks).
> CPU cost is ignored because it's tiny next to disk I/O.

---

## 8.3 Selection Algorithms (σ)

How the engine finds the rows matching a `WHERE`:

| Algorithm | When usable | Cost (block transfers) |
|-----------|-------------|------------------------|
| **Linear scan** | always (no index needed) | **b_r** (read every block) |
| **Binary search** | file **sorted** on the attribute | **⌈log₂(b_r)⌉** + matching blocks |
| **Primary B+-tree index** | equality on the indexed (sort) key | **height + 1** |
| **Secondary index** | equality on a non-sort attribute | **height + (number of matching records)** |

> **Comparison / range selections (`A ≥ v`, `A BETWEEN …`):** with a **primary
> index or sorted file**, locate the first matching block (≈ height) and **scan
> forward** from there (≈ height + matching blocks). With a **secondary** index a
> range scan does **one random I/O per matching record**, so for a wide range a
> **linear scan is usually cheaper**.

> **Why a full scan can beat an index (selectivity):** **selectivity** = fraction
> of rows matching. A **secondary** index costs ~one **random** I/O *per matching
> record*. If many records match, that's more expensive than **one sequential**
> full scan. So the optimizer uses an index only when **few** rows match (low
> selectivity), and prefers a scan when **many** match.

---

## 8.4 Sorting — External Merge Sort

Sorting underlies `ORDER BY`, `GROUP BY`, and sort-merge join. When data is bigger
than RAM, we use **external merge sort**.

![External merge sort: Phase 1 creates sorted runs (load M blocks, sort, write); Phase 2 merges (M−1) runs at a time over multiple passes into the final sorted file.](images/81_external_merge_sort.png)

- **Phase 1 (run creation):** read **M** blocks at a time, sort them in RAM, write
  out a **sorted run**. Produces `⌈b_r / M⌉` runs.
- **Phase 2 (merging):** merge **(M−1)** runs at a time (one output buffer),
  repeating in **passes** until one sorted file remains.

```
Number of initial runs    = ⌈ b_r / M ⌉
Number of merge passes    = ⌈ log_(M−1) ( b_r / M ) ⌉
Total block transfers     = b_r × ( 2 × (#merge passes) + 1 )
```

> The `+1` is the initial read during run creation; each merge pass reads **and**
> writes all `b_r` blocks (hence the `2×`). **More memory M → fewer passes →
> cheaper.** A common GATE numerical asks for the number of passes/transfers.
> *(Convention note: this counts block transfers only; some GATE variants also add
> the **seek** cost or count the final write separately — use your exam's
> convention.)*

---

## 8.5 Join Algorithms — the Heart of Query Processing

Joins are the most expensive and most optimized operation. Learn each algorithm's
**cost** and **when to use it**. (Convention: **r** = outer, **s** = inner.)

### Nested-loop joins

![Nested-loop joins: simple (per-tuple) scans all of s for each tuple of r; block nested-loop scans s once per block of r; best case is when the inner relation fits in memory.](images/82_nested_loop_join.png)

- **Simple (tuple) nested-loop:** for **each tuple** of r, scan **all** of s.
  Cost = **n_r × b_s + b_r** — expensive (note `n_r`, the *tuple* count).
- **Block nested-loop:** for **each block** of r, scan all of s. Worst-case
  Cost = **b_r × b_s + b_r** — far better than per-tuple.
- **Best case** (smaller relation fits in M buffers): **b_r + b_s** (read each
  once). With M buffers generally: `⌈b_r/(M−2)⌉ × b_s + b_r`.

> **Rule:** make the **smaller** relation the **outer** loop (fewer passes over the
> inner). Nested-loop is the **only** algorithm that handles **any** (theta) join
> condition (`<, >, ≠`), so it's the fallback when no index/sort exists.

### Indexed nested-loop & sort-merge join

![Indexed nested-loop uses an index on s to fetch matches per tuple of r; sort-merge sorts both relations then merges with two pointers.](images/83_indexed_merge_join.png)

- **Indexed nested-loop join** (s has an index on the join attribute): for each
  tuple of r, **use the index** on s to fetch matches (no full scan of s).
  Cost = **b_r + n_r × c** where `c` = cost of one index lookup. Best when **r is
  small** and **s is indexed** on the join key.
- **Sort-merge join** (equi-join): **sort** both relations on the join attribute,
  then **merge** with two pointers. Cost = **b_r + b_s** if already sorted (else add
  the sort cost). Excellent for **large equi-joins** and when the output must be
  sorted anyway.

### Hash join

![Hash join: build a hash table on the smaller relation by the join key, then probe it with the larger; only matching buckets are compared. Equi-join only.](images/84_hash_join.png)

- **Hash join** (equi-join **only**): **build** a hash table on the **smaller**
  relation (hash on the join key), then **probe** it with the larger relation; only
  tuples in the **same bucket** are compared.
  - In-memory (build fits in RAM): Cost = **b_r + b_s**.
  - **Grace / partitioned** hash join (doesn't fit): partition both to disk, then
    join partitions. Cost ≈ **3 × (b_r + b_s)** (partition reads+writes both, then
    reads both again).

### Cost comparison (the summary table)

![Join algorithm cost summary: simple/block nested-loop, indexed, sort-merge, hash — with cost formulas, join types, and best-use.](images/85_join_cost_comparison.png)

| Algorithm | Cost | Join type | Best when |
|-----------|------|-----------|-----------|
| Simple nested-loop | n_r × b_s + b_r | any (theta) | tiny relations |
| Block nested-loop | b_r × b_s + b_r | any (theta) | no index/sort, small inner |
| Indexed nested-loop | b_r + n_r × c | equi **or comparison** (ordered index) | r small + s indexed |
| Sort-merge | b_r + b_s (+ sort) | equi | large equi-joins / pre-sorted |
| Hash join | ~3(b_r + b_s) | **equi only** | large equi-joins, order not needed |

> **The two big exam facts:** (1) **nested-loop is the only one that does non-equi
> joins** (`>`, `<`, `≠`); (2) **hash and sort-merge** are equi-only but **fastest
> at scale**. Always make the **smaller** relation the **outer/build** side.

### Other operations (projection, duplicate elimination, set operations)

**Projection with `DISTINCT`, duplicate elimination, and set operations
(∪, ∩, −)** are all evaluated by **sorting or hashing** — the same machinery as
sort-merge / hash join. Cost ≈ the underlying sort or hash (e.g. `b_r(2·passes+1)`
for sort-based duplicate elimination). The set operations process **both** inputs
much like an equi-join (∪ keeps all, ∩ keeps common, − keeps left-only). *(Plain
projection without `DISTINCT` is free — it pipelines with no extra I/O.)*

---

## 8.6 Evaluating Expressions: Materialization vs Pipelining

A query is a **tree** of operations. How do results flow between them?

![Materialization writes each operation's result to a temp file that the next reads; pipelining passes tuples directly in memory; blocking operators (sort, aggregation) force materialization.](images/86_materialization_pipelining.png)

- **Materialization:** evaluate one operation **fully**, write its result to a
  **temp file** on disk, then the next operation reads it. Simple, but pays extra
  disk I/O for the temporary results.
- **Pipelining:** pass each output tuple **directly** to the next operation in
  memory (no temp file). **Faster** (no temp writes) and produces first rows
  sooner.

> **Blocking operators** (sort, aggregation/`GROUP BY`, the **build** phase of hash
> join) must consume **all** input before producing any output — they **force
> materialization** at that step. Non-blocking operators (`select`, `project`)
> **pipeline** freely. The engine pipelines wherever the operators allow.

---

## 8.7 Query Optimization — Heuristic (Rule-Based)

The optimizer transforms the algebra tree into an equivalent but **cheaper** one
using **relational-algebra equivalence rules** (introduced in Module 3 §3.4).

**The core equivalence rules (these *license* each transformation — GATE asks them
directly):**

- **Selection cascade:** `σ_{θ1 ∧ θ2}(R) = σ_{θ1}(σ_{θ2}(R))`.
- **Selection commutativity:** `σ_{θ1}(σ_{θ2}(R)) = σ_{θ2}(σ_{θ1}(R))`.
- **σ distributes over join:** `σ_θ(R ⋈ S) = (σ_θ(R)) ⋈ S` when θ uses only R's
  attributes (this is what lets us "push selection down").
- **Projection cascade:** `π_{L1}(π_{L2}(R)) = π_{L1}(R)` when `L1 ⊆ L2`.
- **σ–π commutativity:** selection and projection can be reordered when the
  selection only uses retained attributes.
- **Join commutativity & associativity:** `R ⋈ S = S ⋈ R`;
  `(R ⋈ S) ⋈ T = R ⋈ (S ⋈ T)` — this is what enables **join-order** choices.

These rules **preserve the result** (the relations are equal) but change the
**cost**; the heuristics below apply them in a beneficial direction.

![Heuristic optimization: pushing the selection below the join so we filter CUSTOMER first, then join the smaller result, instead of joining whole tables then filtering.](images/87_heuristic_optimization.png)

**Heuristic rules (apply in roughly this order):**

1. **Push SELECTION (σ) down** — filter **as early as possible** (the single most
   important rule — shrinks inputs before expensive joins).
2. **Push PROJECTION (π) down** — drop unneeded columns early (smaller tuples).
3. **Do the most restrictive selections first.**
4. **Convert a σ over a Cartesian product into a JOIN** (`σ_θ(r × s) = r ⋈_θ s`).
5. **Choose a good join order** (small intermediate results first).

> **Worked idea (from the diagram):** "names of customers in Mumbai who placed
> orders." *Naive:* join the **whole** CUSTOMER and ORDER tables, then filter
> `city='Mumbai'`. *Optimized:* filter CUSTOMER to Mumbai **first**, then join the
> much smaller set. Same answer, dramatically less work.

> **Why it's called "heuristic":** these rules *usually* help, applied without
> computing exact costs — fast to apply, "good enough" plans.

---

## 8.8 Query Optimization — Cost-Based

Heuristics aren't always optimal. **Cost-based optimization** **enumerates** many
plans, **estimates** each one's cost from statistics, and picks the **cheapest**.

![Cost-based optimization: enumerate plans, estimate cost using statistics (tuple/block counts, distinct values, selectivity), and pick the cheapest; join order is the biggest lever.](images/88_cost_based_optimization.png)

- **Join order is the biggest lever:** for `A ⋈ B ⋈ C`, the order `(A ⋈ B) ⋈ C`
  vs `A ⋈ (B ⋈ C)` can differ by **orders of magnitude** (because intermediate
  result sizes differ). With *n* relations there are many orderings.
- **Cost estimation needs statistics:** number of tuples/blocks, **number of
  distinct values** per attribute, and **selectivity** → estimated **result size**
  of each operation. These live in the catalog and are refreshed by `ANALYZE`.
- Classic **System-R / Selinger** optimizers use **dynamic programming** over join
  orders (plus pruning) to avoid checking every plan.

> **Real-world failure mode:** stale statistics → wrong size estimates → the
> optimizer picks a **bad plan** (e.g. nested-loop on a huge table). The fix in
> production is literally **run `ANALYZE`** to refresh statistics.

### Size estimation formulas (GATE numericals)

To cost a plan, the optimizer must **estimate the output size** of each operation.
`V(A, r)` = number of **distinct values** of attribute A in r.

| Operation | Estimated number of result tuples |
|-----------|------------------------------------|
| **Equality selection** `σ_{A = a}(r)` | **n_r / V(A, r)** |
| **Range selection** `σ_{A ≤ v}(r)` | `n_r × (v − min) / (max − min)` (or `n_r/2` if unknown) |
| **Equi-join** `r ⋈ s` on common attr A | **(n_r × n_s) / max( V(A,r), V(A,s) )** |
| **Conjunction** `σ_{θ1 ∧ θ2}` | multiply the individual selectivities |
| **Cartesian product** `r × s` | `n_r × n_s` |

> **Worked example:** `STUDENT` has `n_r = 10,000` rows and `V(dept, STUDENT) = 50`
> distinct departments. Estimated rows for `σ_{dept = 'CSE'}(STUDENT) = 10000/50 =`
> **200**. For an equi-join of r (n_r = 1000) and s (n_s = 2000) on A with
> `V(A,r) = 100`, `V(A,s) = 500`: estimated `= (1000 × 2000)/max(100,500) =
> 2,000,000/500 =` **4,000** rows.

> **Why it matters:** these estimates drive the **cost** comparison and **join
> order**. Wrong `V(A,r)` (stale stats) → wrong estimate → wrong plan.

---

## 8.9 Choosing a Join Algorithm

![Flowchart: non-equi join → nested-loop; equi with index + small side → indexed nested-loop; sorted/needs-sort → sort-merge; otherwise → hash join.](images/89_fc_join_selection.png)

- **Non-equi (`>`, `<`, `≠`) →** nested-loop (the only option).
- **Equi (or comparison, if the index is an ordered B+-tree) + index on join attr +
  one side small →** indexed nested-loop.
- **Input already sorted / output needs sorting →** sort-merge.
- **Large equi-join, order doesn't matter →** hash join (often the fastest).

---

## 8.10 Real-World & Backend Perspectives

- **`EXPLAIN` / `EXPLAIN ANALYZE`** prints the chosen plan — the algebra tree with
  the access methods and join algorithms the optimizer selected, plus estimated and
  actual costs. Reading it is the #1 SQL performance skill.
- **"Seq Scan vs Index Scan vs Bitmap Heap Scan"** in a Postgres plan = the §8.3
  selection algorithms. **"Hash Join / Merge Join / Nested Loop"** = §8.5.
- **`ANALYZE` / auto-vacuum** keep statistics fresh so estimates are accurate.
- **Why a query suddenly got slow:** often stale stats or a plan flip after data
  growth — diagnosed by comparing `EXPLAIN` plans.

---

## 8.11 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Mixing up **simple** nested-loop cost (`n_r × b_s`, uses *tuples*) with **block**
  nested-loop (`b_r × b_s`, uses *blocks*).
- Using **hash/sort-merge** for a **non-equi** join (they only do equality).
- Making the **larger** relation the outer/build side (do the opposite).
- Thinking an index always beats a scan (high selectivity → scan wins).
- Forgetting blocking operators (sort, aggregation) force **materialization**.
- Ignoring **statistics** — bad stats → bad plans.

**Edge cases**
- If both relations are already sorted on the join key, **sort-merge = b_r + b_s**
  (no sort cost) — often the cheapest.
- Hash join degrades if the build side doesn't fit and partitions overflow
  (recursive partitioning).
- Optimizer can choose a **worse** plan than a human if statistics are stale.

**Tradeoffs**

| Choice | Gain | Cost |
|--------|------|------|
| Pipelining | less temp I/O, faster first row | not possible across blocking ops |
| Heuristic optimization | fast to compute | may miss the optimal plan |
| Cost-based optimization | finds near-optimal plans | needs good statistics; more planning time |
| Index scan | great for low selectivity | random I/O hurts for high selectivity |

---

## 8.12 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** join algorithm costs (nested-loop tuple vs block,
indexed, sort-merge, hash); selection costs; external merge sort passes/transfers;
materialization vs pipelining; heuristic rules (push σ down); cost-based & join
order; which join handles non-equi.

**Interview:** "How would you speed up a slow query?" (read `EXPLAIN`, add/adjust
index, fix join order, update stats); "nested-loop vs hash join?"; "why might the
optimizer pick a full scan over an index?" (selectivity); "what is pipelining?".

**Coding/practical:**
- Run `EXPLAIN ANALYZE` on a join; see which join algorithm and access method were
  chosen; add an index and re-check.
- Force a bad plan (disable index) to feel the cost difference.

---

## 8.13 Concept Checks & MCQs

1. Cost is measured mainly in ___ → **disk I/O (block transfers + seeks)**.
2. Simple nested-loop cost? → **n_r × b_s + b_r**.
3. Block nested-loop cost (worst)? → **b_r × b_s + b_r**.
4. Which join algorithms do **equi-only**? → **sort-merge and hash**.
5. Which join handles non-equi conditions? → **nested-loop**.
6. Sort-merge cost if both already sorted? → **b_r + b_s**.
7. Grace hash join cost? → **~3(b_r + b_s)**.
8. Should the smaller or larger relation be the outer/build side? → **smaller**.
9. Operation that forces materialization? → a **blocking** op (sort, aggregation).
10. Single most important heuristic rule? → **push selection (σ) down**.
11. Cost-based optimization's biggest lever? → **join order**.
12. Stale statistics cause ___ → **bad cost estimates → bad plans** (fix: ANALYZE).
13. Estimated rows of `σ_{A=a}(r)`? → **n_r / V(A, r)**.
14. Estimated rows of equi-join `r ⋈ s` on A? → **(n_r × n_s) / max(V(A,r), V(A,s))**.
15. `σ_{θ1∧θ2}(R) = σ_{θ1}(σ_{θ2}(R))` is the ___ rule → **selection cascade**.
16. How are `DISTINCT` / set operations evaluated? → by **sorting or hashing**.

**True/False**
- Hash join works for `r.a > s.b`. → **False** (equi-only).
- Pipelining avoids writing temp results to disk. → **True**.
- Block nested-loop is cheaper than simple (tuple) nested-loop. → **True**.
- The optimizer always finds the truly optimal plan. → **False** (depends on stats/search).

**Numerical (do it):**
> r: b_r = 100 blocks, n_r = 1000 tuples. s: b_s = 500 blocks. Memory tiny.
> - Block nested-loop (r outer): `b_r × b_s + b_r = 100×500 + 100 = 50,100` transfers.
> - Block nested-loop (s outer): `b_s × b_r + b_s = 500×100 + 500 = 50,500`.
> → Making the **smaller (r)** the outer is cheaper. ✔ Simple nested-loop (r outer)
>   would be `n_r × b_s + b_r = 1000×500 + 100 = 500,100` — **10× worse**.

---

## 8.14 One-Page Revision Sheet

```
PIPELINE: SQL -> parse/translate (to RA) -> OPTIMIZER (pick cheapest plan via stats) -> EVAL engine -> result.
COST = disk I/O = (#block transfers) + (#seeks). b_r=blocks, n_r=tuples, M=memory blocks.

SELECTION: linear scan = b_r ; binary search (sorted) = ceil(log2 b_r)+matches ;
  primary index = height+1 ; secondary index = height + #matches. (index wins only at LOW selectivity)

EXTERNAL MERGE SORT: runs=ceil(b_r/M); passes=ceil(log_(M-1)(b_r/M));
  transfers = b_r*(2*passes + 1). more M -> fewer passes.

JOINS (r outer/build, s inner/probe):
  simple nested-loop  = n_r*b_s + b_r        (ANY join; uses TUPLES)
  block nested-loop   = b_r*b_s + b_r         (ANY join; uses BLOCKS) best: b_r+b_s if inner fits
  indexed nested-loop = b_r + n_r*c           (equi; s indexed; r small)
  sort-merge          = b_r+b_s (+sort)       (EQUI; pre-sorted/needs sort)
  hash join           = ~3(b_r+b_s) grace     (EQUI ONLY; big joins)
  -> smaller relation = OUTER/BUILD. nested-loop = ONLY non-equi method.

MATERIALIZATION (temp file to disk) vs PIPELINING (tuple-by-tuple in RAM, faster).
  blocking ops (SORT, AGGREGATION, hash-build) force materialization.

OPTIMIZATION:
  HEURISTIC (rule-based): push SELECTION down (#1), push PROJECTION down, most-restrictive first,
    sigma-over-cartesian -> JOIN, good join order.
  COST-BASED: enumerate plans, estimate cost via STATISTICS (tuples, distinct values, selectivity),
    pick cheapest. JOIN ORDER = biggest lever. System-R/Selinger DP. stale stats -> bad plan (ANALYZE).
  EQUIVALENCE RULES: selection cascade/commutativity; sigma distributes over join (push down);
    projection cascade; sigma-pi commute; join commutative+associative (-> join order).
  SIZE ESTIMATION: sigma_{A=a}(r) = n_r/V(A,r); equi-join = n_r*n_s/max(V(A,r),V(A,s)); cross = n_r*n_s.
  DISTINCT / set ops (union/intersect/minus) -> evaluated by SORTING or HASHING (cost ~= underlying sort/hash).
```

### Flash cards

| Front | Back |
|-------|------|
| Cost metric? | Disk I/O (block transfers + seeks) |
| Simple vs block nested-loop cost? | n_r·b_s+b_r vs b_r·b_s+b_r |
| Only join for non-equi? | Nested-loop |
| Equi-only fast joins? | Sort-merge, hash |
| Sort-merge if pre-sorted? | b_r + b_s |
| Grace hash join cost? | ~3(b_r + b_s) |
| Outer/build side should be? | The smaller relation |
| #1 heuristic rule? | Push selection down |
| Biggest cost-based lever? | Join order |
| Blocking ops force? | Materialization |
| Index loses to scan when? | High selectivity (many matches) |

### Spaced repetition
- **24-hour:** compute join costs for 3 (b_r, b_s, n_r) cases; redo MCQs.
- **7-day:** draw the heuristic push-down transformation; list all 5 join costs.
- **30-day:** given statistics, choose the join algorithm + order and justify with cost.

---

## 8.15 Summary

Query processing turns SQL into an efficient execution. The **pipeline** is
**parse → translate to algebra → optimize → evaluate**, with **cost measured in
disk I/O** (`b_r` blocks, `n_r` tuples, `M` buffers). We costed **selection**
algorithms (scan vs index, governed by **selectivity**), **external merge sort**
(`runs = ⌈b_r/M⌉`, `transfers = b_r(2·passes+1)`), and the five **join
algorithms** — simple/block **nested-loop** (`n_r·b_s` vs `b_r·b_s`, the only ones
for **non-equi**), **indexed** nested-loop (`b_r + n_r·c`), **sort-merge**
(`b_r+b_s` if sorted), and **hash** (`~3(b_r+b_s)`, equi-only) — always putting the
**smaller** relation outer/build. We saw **pipelining vs materialization** (blocking
operators force the latter), then the two optimizer styles: **heuristic** (push
selection/projection **down**) and **cost-based** (enumerate plans, estimate via
**statistics**, with **join order** the biggest lever).

Next, **Module 9 — Transactions & Concurrency** shifts from *speed* to
*correctness*: how the DBMS keeps data consistent when many of these queries run at
once and crashes happen.

> **You have mastered this module when** you can: state and apply every join
> algorithm's cost; explain when an index beats a scan (selectivity); compute
> external-merge-sort passes; contrast materialization and pipelining; and walk
> through heuristic vs cost-based optimization (push σ down; join order via
> statistics) — all without notes.
