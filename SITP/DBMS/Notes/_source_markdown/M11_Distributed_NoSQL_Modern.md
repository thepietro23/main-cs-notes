---
title: "Module 11 — Distributed, NoSQL & Modern Databases"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — Distributed, NoSQL & Modern Databases

> **Where this module sits.**
> Modules 1–10 covered the **single-machine relational** database in depth. This
> finale **zooms out** to data spread **across many machines**: why we distribute,
> the unavoidable **CAP** trade-off, how **ACID relaxes into BASE** at scale, the
> four **NoSQL** families, **sharding**, and **distributed transactions (2PC)**. For
> **SEBI/RBI IT** it's conceptual (CAP, ACID-vs-BASE, SQL-vs-NoSQL are favourite
> MCQs); for **backend engineering** it's everything — modern systems are
> distributed by default.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★     | ★★★★      | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **CAP theorem** (pick 2; CP vs
AP); **ACID vs BASE**; **SQL vs NoSQL** differences; **NoSQL families**
(key-value / document / column / graph); **fragmentation** (horizontal/vertical) &
**replication**; **sharding / partitioning** (range/hash/consistent hashing);
**two-phase commit (2PC)**; **consistency models** (strong vs eventual).

---

## 11.1 Why Distributed Databases?

![A single node has finite CPU/RAM/disk and is a single point of failure; a distributed database spreads data across many nodes for horizontal scale, fault tolerance, and lower latency, using partitioning and replication.](images/114_why_distributed.png)

A single machine has **finite** CPU, RAM, and disk (**vertical scaling** caps out),
is a **single point of failure**, and serves distant users with high latency. A
**distributed database** spreads data across **many nodes** (and data centres).

- **+ Horizontal scale** (add machines), **fault tolerance** (no single point of
  failure), **low latency** (data near users).
- Two core tools: **partitioning** (split data across nodes → scale) and
  **replication** (copy data → availability).

> **The catch:** the moment data lives on multiple machines connected by an
> **unreliable network**, you hit a fundamental trade-off that the **CAP theorem**
> formalizes. Everything in this module flows from that tension.

---

## 11.2 Fragmentation & Replication

![Fragmentation splits a table horizontally (by rows = sharding) or vertically (by columns); replication copies data fully or partially, trading read availability against write cost.](images/115_fragmentation_replication.png)

**Fragmentation (splitting a table):**

- **Horizontal:** split by **rows** (e.g. North-region customers → node A, South →
  node B). This is **sharding**.
- **Vertical:** split by **columns** (e.g. profile columns → node A, billing
  columns → node B); rejoin by primary key.

**Replication (copying data):**

- **Full:** every node holds a complete copy — great read availability, but writes
  must update all copies.
- **Partial:** only some fragments are copied to some nodes.

> **The replication trade-off:** more copies → better **read availability** and
> fault tolerance, but every **write** must propagate to all copies. **Synchronous**
> replication is consistent but slow; **asynchronous** is fast but copies can **lag**
> (stale reads). A common pattern is **leader–follower** (primary–replica): writes
> go to the **leader**, reads can be served by **followers**.

> **Transparency goals:** users shouldn't need to know **where** data physically
> lives — **location**, **fragmentation**, and **replication** transparency.

---

## 11.3 The CAP Theorem

![CAP theorem triangle: Consistency, Availability, Partition tolerance — during a network partition you can keep only two, so the real choice is CP vs AP (CA only exists without partitions).](images/116_cap_theorem.png)

In a distributed system you can guarantee at most **two** of:

- **Consistency (C):** every read sees the **latest** write (or an error).
- **Availability (A):** every request gets a **non-error** response (not
  necessarily the latest data).
- **Partition tolerance (P):** the system keeps working despite **dropped/delayed**
  messages between nodes.

> **The real-world reading (crucial):** network **partitions are unavoidable** in a
> distributed system, so **P is mandatory**. That means during a partition you must
> **choose between C and A**:
> - **CP** (consistency over availability): refuse/block requests it can't answer
>   consistently. *e.g. HBase, MongoDB (default), traditional distributed RDBMS.*
> - **AP** (availability over consistency): always respond, possibly with **stale**
>   data. *e.g. Cassandra, DynamoDB, CouchDB.*
> - **CA** exists only **without** partitions — i.e. a **single-node** system.

> **Caveat (so you don't over-apply it):** CAP is about behaviour **only during a
> partition**. When the network is healthy, a system can offer **both** C and A —
> which is what **PACELC** captures next.

---

## 11.4 ACID vs BASE (and PACELC)

![ACID (strong consistency, correctness-first, CP-leaning) versus BASE (basically available, soft state, eventual consistency, availability-first, AP-leaning); PACELC extends CAP to the no-partition case.](images/117_acid_vs_base.png)

| | **ACID** (relational) | **BASE** (many NoSQL) |
|--|----------------------|------------------------|
| Stands for | Atomicity, Consistency, Isolation, Durability | **B**asically **A**vailable, **S**oft state, **E**ventual consistency |
| Consistency | **strong**, immediate | **eventual** (copies converge later) |
| Priority | **correctness** | **availability + scale** |
| Best for | banking, orders (stale = unacceptable) | feeds, carts (brief staleness OK) |
| CAP leaning | CP | AP |

> **BASE is the philosophical opposite of ACID:** it deliberately accepts
> **temporary inconsistency** so the system stays **available** and **scalable** — a
> direct consequence of choosing **A** over **C** under CAP. "Eventual consistency"
> means: if writes stop, all replicas **eventually** converge to the same value.

> **PACELC (the CAP extension, exam bonus):** *if* there is a **P**artition, choose
> **A** or **C**; **E**lse (normal operation), choose **L**atency or **C**onsistency.
> It captures that even *without* partitions there's a **latency vs consistency**
> trade-off (waiting to sync all replicas costs latency).

---

## 11.5 Consistency Models

![Consistency models from strong (linearizable — every read sees the latest write) through sequential and causal to eventual (replicas converge eventually), trading correctness for availability/latency.](images/118_consistency_models.png)

| Model | Guarantee | Trade-off |
|-------|-----------|-----------|
| **Strong (linearizable)** | every read sees the **latest** write, immediately | correctness; lower availability, **higher** latency |
| **Sequential** | all nodes see ops in **one global order** consistent with each process's **program order**, but **not necessarily real-time** order | drops the real-time **recency** guarantee that linearizability adds |
| **Causal** | causally-related ops seen in order; concurrent ones may differ | middle ground |
| **Eventual** | if writes stop, all copies **converge** | highest availability; may read **stale** |

> **The spectrum:** **stronger** = easier to reason about but costs availability and
> latency; **weaker** = more available/scalable but the application must **tolerate
> stale reads**. Many NoSQL stores make this **tunable per query** (e.g. Cassandra's
> `ONE` / `QUORUM` / `ALL` read/write levels).

> **Session (client-centric) guarantees** soften "eventual" for a single user:
> **read-your-writes** (you always see your own writes), **monotonic reads** (you
> never go *backwards* in time), **monotonic writes** (your writes apply in order),
> and **consistent prefix** (you see writes in a causally sensible order). These
> explain UX like "I posted a comment and *I* can see it, even if others don't yet."

> **The quorum rule (R + W > N) — how tunable consistency actually works:** with
> **N** replicas, a write waits for **W** acknowledgements and a read queries **R**
> replicas. If **R + W > N**, the read set is guaranteed to **overlap** the latest
> write set → the read sees the **most recent value** (**strong** consistency on the
> replica set); if **W > N/2**, two concurrent writes can't both succeed. *Example:*
> `N=3, W=2, R=2` → `R+W = 4 > 3` → strongly consistent **yet tolerates one node
> down**. Lowering R/W (e.g. `ONE`) trades consistency for **lower latency / higher
> availability**. This formula *is* Cassandra/Dynamo's `ONE/QUORUM/ALL`.

---

## 11.6 The NoSQL Families

**NoSQL** = "**Not Only SQL**": schema-flexible, horizontally-scalable stores for
data and scale that don't fit rigid relational tables. Four families:

![The four NoSQL families: key-value (Redis/DynamoDB), document (MongoDB/CouchDB), column-family (Cassandra/HBase), and graph (Neo4j/Neptune), each with typical use-cases.](images/119_nosql_families.png)

| Family | Model | Examples | Best for |
|--------|-------|----------|----------|
| **Key-value** | `{key → value}`, a giant hash map | Redis, DynamoDB | cache, sessions, leaderboards |
| **Document** | JSON-like documents, flexible schema | MongoDB, CouchDB | content, catalogs, profiles |
| **Column-family (wide-column)** | rows with dynamic column families | Cassandra, HBase | time-series, logs, IoT at scale |
| **Graph** | nodes + edges; relationships first-class | Neo4j, Neptune | social, fraud, recommendations |

> **How to choose:** by **data shape and access pattern**, not hype. Lots of
> simple lookups → **key-value**. Nested, varied records → **document**. Enormous
> write throughput / time-series → **column-family**. Richly connected data with
> relationship traversals → **graph**.

---

## 11.7 Partitioning / Sharding Strategies

![Sharding strategies: range partitioning (by key ranges, good for scans but risks hotspots), hash partitioning (even spread but scatters range queries and rehashes on resize), and consistent hashing (a ring that minimizes data movement when nodes change).](images/120_sharding.png)

How do we decide which node stores a given key?

- **Range partitioning:** split by key **ranges** (A–H → node 1, …). **+** efficient
  range scans; **−** **hotspots** if keys are skewed.
- **Hash partitioning:** `node = hash(key) mod N`. **+** even spread (no hotspots);
  **−** range queries scatter, and **adding a node** forces remapping ~**everything**
  (full rehash).
- **Consistent hashing:** place nodes **and** keys on a **ring**; a key belongs to
  the **next node clockwise**. Adding/removing a node only remaps keys in **one
  arc** → **minimal data movement**. Used by **Cassandra** (and Amazon's original
  **Dynamo** design); **virtual nodes** smooth out load.

> **Why consistent hashing matters:** plain hash partitioning re-shuffles almost the
> whole dataset when the cluster grows. Consistent hashing moves only `~1/N` of the
> keys — the property that makes elastic scaling practical.

---

## 11.8 Distributed Transactions — Two-Phase Commit (2PC)

When one transaction spans **multiple nodes**, how do we keep it **atomic** (all
commit or all abort)? The **two-phase commit** protocol.

![Two-phase commit sequence: Phase 1 (voting) — coordinator sends PREPARE, participants reply with a vote; Phase 2 (decision) — coordinator broadcasts global commit/abort, participants acknowledge.](images/121_two_phase_commit.png)

- **Phase 1 — Voting:** the **coordinator** sends **PREPARE** to all participants;
  each writes to its log and replies **VOTE-COMMIT** (ready) or **VOTE-ABORT**.
- **Phase 2 — Decision:** if **all** voted commit, the coordinator broadcasts
  **GLOBAL COMMIT**; if **any** voted abort (or timed out), **GLOBAL ABORT**.
  Participants apply the decision and **acknowledge**.

> **Direction matters (exam):** **votes flow up** (participants → coordinator); the
> **decision flows down** (coordinator → participants). The decision rule —
> **all-yes ⇒ commit, otherwise abort** — guarantees **atomicity** across nodes.

> **The weakness — 2PC blocks:** if the **coordinator crashes after PREPARE**,
> participants are stuck **holding locks**, waiting for a decision that may never
> come. **Three-Phase Commit (3PC)** inserts a **pre-commit** phase to reduce
> blocking, at the cost of extra messages. Modern systems often use consensus
> protocols (**Paxos/Raft**) for fault-tolerant agreement.

---

## 11.9 SQL vs NoSQL & Modern (NewSQL)

![SQL vs NoSQL comparison across schema, scaling, consistency, queries, best-fit, and examples; modern systems are often polyglot, and NewSQL aims for SQL plus horizontal scale plus ACID.](images/122_sql_vs_nosql.png)

| Aspect | SQL (relational) | NoSQL |
|--------|------------------|-------|
| Schema | **fixed** (upfront) | **flexible** / schema-less |
| Scaling | **vertical** (bigger machine) | **horizontal** (more machines) |
| Consistency | **strong** (ACID) | often **eventual** (BASE) |
| Queries / joins | rich SQL, joins | limited; **denormalize** instead |
| Best for | structured data, transactions | huge scale, varied/unstructured data |
| Examples | PostgreSQL, MySQL, Oracle | MongoDB, Cassandra, Redis, Neo4j |

> **Not "better/worse" — different tools.** Real systems are often **polyglot**: a
> relational DB for orders, **Redis** for caching, a document store for the catalog.
> **NewSQL** (e.g. **Google Spanner, CockroachDB**) aims to give **SQL + horizontal
> scale + ACID** together — closing the historical gap.

### Choosing a database

![Flowchart: need ACID + relations → SQL; key→value lookups → key-value; relationships central → graph; massive writes/time-series → column-family; otherwise → document. Reality is polyglot; NewSQL combines SQL, scale, and ACID.](images/123_fc_database_choice.png)

- **ACID + structured relations →** relational (SQL).
- **Simple key → value lookups →** key-value.
- **Relationships are the point →** graph.
- **Massive write throughput / time-series →** column-family.
- **Nested, flexible records →** document.

---

## 11.10 Real-World & Backend Perspectives

- **Sharding in practice:** MongoDB shard keys, Cassandra's partition key + ring,
  Vitess for MySQL. A **bad shard key** (low cardinality / monotonic) creates
  **hotspots**.
- **Eventual consistency you've used:** a social post that takes a moment to appear
  for all friends; a shopping cart that briefly differs across devices.
- **Read replicas** scale reads; **leader election** (Raft) handles failover.
- **Distributed transactions are expensive** — microservices often avoid 2PC using
  the **Saga** pattern (a sequence of local transactions + compensating actions).
- **CAP in product decisions:** payment systems lean **CP** (never double-spend);
  shopping/social lean **AP** (stay up, reconcile later).

---

## 11.11 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Saying you "give up P" — in a distributed system **P is mandatory**; the choice is
  **C vs A**.
- Reading CAP as "always pick 2 of 3" — the trade-off only bites **during a
  partition** (see PACELC).
- Thinking **NoSQL = no transactions/no schema ever** (many now offer both).
- Confusing **horizontal** (rows / sharding) with **vertical** (columns)
  fragmentation.
- Forgetting **2PC blocks** if the coordinator fails.
- Believing eventual consistency means "inconsistent forever" (it **converges**).

**Edge cases**
- A network partition with an **AP** store → two sides accept conflicting writes →
  need **conflict resolution** (last-write-wins, vector clocks, CRDTs).
- **Hash** sharding makes range queries hit **every** node.
- Cross-shard joins/transactions are slow → design to keep related data
  **co-located**.

**Tradeoffs**

| Choice | Gain | Cost |
|--------|------|------|
| Replication | availability, read scale | write cost, consistency lag |
| AP (eventual) | always available | stale reads, conflict handling |
| CP (strong) | correctness | may reject requests in a partition |
| Sharding | horizontal scale | cross-shard ops expensive |
| 2PC | cross-node atomicity | blocking, latency |

---

## 11.12 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** CAP (pick 2, CP vs AP, P mandatory); ACID vs BASE;
SQL vs NoSQL; the four NoSQL families + examples; horizontal vs vertical
fragmentation; replication trade-offs; sharding (range/hash/consistent hashing);
2PC phases & blocking.

**Interview:** "Explain CAP and where you'd land for a payment system"; "SQL vs
NoSQL — when each?"; "What is eventual consistency?"; "How does consistent hashing
help scaling?"; "Why is 2PC problematic, and what alternatives exist (Saga, Raft)?".

**Coding/practical:**
- Set up a MongoDB replica set or sharded cluster; observe failover and read
  preferences.
- Use Redis as a cache in front of a SQL DB (polyglot); measure latency improvement.
- Reason about a shard key choice and show a hotspot vs an even distribution.

---

## 11.13 Concept Checks & MCQs

1. CAP stands for? → **Consistency, Availability, Partition tolerance**.
2. In a distributed system, which CAP property is effectively mandatory? →
   **Partition tolerance**.
3. During a partition, the real choice is between ___ and ___ → **consistency and
   availability**.
4. Cassandra/DynamoDB lean toward ___ → **AP**. MongoDB(default)/HBase → **CP**.
5. BASE stands for? → **Basically Available, Soft state, Eventual consistency**.
6. ACID leans toward which CAP pair? → **CP**.
7. Horizontal fragmentation splits by ___; vertical by ___ → **rows / columns**.
8. Sharding = which fragmentation? → **horizontal**.
9. Which sharding minimizes data movement when adding a node? → **consistent
   hashing**.
10. Hash partitioning's weakness? → **range queries scatter; rehash on resize**.
11. The four NoSQL families? → **key-value, document, column-family, graph**.
12. 2PC phases? → **voting (prepare) and decision (commit/abort)**.
13. 2PC's main weakness? → **blocking if the coordinator crashes**.
14. NewSQL aims to combine ___ → **SQL + horizontal scale + ACID**.
15. Eventual consistency means copies ___ → **converge eventually**.
16. Quorum rule for a read to see the latest write? → **R + W > N**.
17. With N=3, which (W,R) is strongly consistent yet tolerates one node down? →
    **W=2, R=2** (R+W=4>3).
18. "You always see your own writes" is which guarantee? → **read-your-writes**.

**True/False**
- In CAP you can have all three at once in a distributed system. → **False**.
- BASE provides strong, immediate consistency. → **False** (eventual).
- A graph database is best for key-value caching. → **False** (use key-value).
- Consistent hashing remaps the whole dataset when a node is added. → **False**
  (only ~1/N).

**Scenario (do it):**
> "Design storage for an e-commerce site." → **orders/payments**: relational
> (**ACID/CP**); **product catalog**: document (MongoDB); **session/cart cache**:
> key-value (Redis); **recommendations**: graph (Neo4j). This is **polyglot
> persistence**. ✔

---

## 11.14 One-Page Revision Sheet

```
WHY DISTRIBUTE: scale beyond one node, fault tolerance, low latency. tools = PARTITIONING + REPLICATION.

FRAGMENTATION: horizontal = by ROWS (=sharding); vertical = by COLUMNS (rejoin on PK).
REPLICATION: full/partial; sync (consistent, slow) vs async (fast, stale). leader-follower: write leader, read followers.

CAP THEOREM: pick 2 of {Consistency, Availability, Partition-tolerance}. P is MANDATORY (network fails) ->
  during a partition choose C or A:  CP (HBase, Mongo default)  vs  AP (Cassandra, DynamoDB). CA = single node only.
PACELC: if Partition -> A or C ; Else -> Latency or Consistency.

ACID (RDBMS, CP, strong) <-> BASE (NoSQL, AP): Basically Available, Soft state, Eventual consistency.
  eventual consistency = if writes stop, replicas CONVERGE.

CONSISTENCY MODELS (strong->weak): STRONG/linearizable > SEQUENTIAL > CAUSAL > EVENTUAL. (often tunable per query)

NoSQL FAMILIES:
  KEY-VALUE (Redis, DynamoDB)        : hash map; cache/sessions.
  DOCUMENT (MongoDB, CouchDB)        : JSON docs; catalogs/profiles.
  COLUMN-FAMILY (Cassandra, HBase)   : wide rows; time-series/logs at scale.
  GRAPH (Neo4j, Neptune)             : nodes+edges; social/fraud/recommend.

SHARDING: RANGE (scan-friendly, hotspots) | HASH (even, but scatter + rehash) |
  CONSISTENT HASHING (ring; add/remove node moves only ~1/N keys; Cassandra + Amazon Dynamo design; virtual nodes).
QUORUM: N replicas, read R + write W. R+W>N -> read sees latest write (strong); W>N/2 -> no conflicting writes.
  e.g. N=3,W=2,R=2 (R+W=4>3) = strong + tolerate 1 node down. lower R/W (ONE) = faster/more available, weaker.
SESSION guarantees: read-your-writes, monotonic reads, monotonic writes, consistent prefix.

2PC (distributed atomicity): PHASE1 voting (coordinator PREPARE-> ; participants VOTE up) ;
  PHASE2 decision (ALL yes -> GLOBAL COMMIT down ; any no/timeout -> ABORT). votes UP, decision DOWN.
  WEAKNESS = BLOCKING if coordinator crashes. 3PC adds pre-commit. alt: Saga, Paxos/Raft.

SQL vs NoSQL: fixed vs flexible schema; vertical vs horizontal scale; strong vs eventual; joins vs denormalize.
  POLYGLOT persistence = use several. NewSQL (Spanner, CockroachDB) = SQL + scale + ACID.
```

### Flash cards

| Front | Back |
|-------|------|
| CAP = ? | Consistency, Availability, Partition tolerance |
| Mandatory CAP property (distributed)? | Partition tolerance |
| Partition → choose between? | Consistency vs Availability |
| AP examples? | Cassandra, DynamoDB |
| CP examples? | HBase, MongoDB (default) |
| BASE = ? | Basically Available, Soft state, Eventual consistency |
| ACID CAP leaning? | CP |
| Horizontal fragmentation? | By rows (sharding) |
| Vertical fragmentation? | By columns |
| Minimal-movement sharding? | Consistent hashing |
| Four NoSQL families? | Key-value, document, column-family, graph |
| 2PC phases? | Voting (prepare), decision (commit/abort) |
| 2PC weakness? | Blocking on coordinator failure |
| NewSQL goal? | SQL + scale + ACID |
| Eventual consistency? | Replicas converge eventually |
| Quorum strong-read rule? | R + W > N |
| Read-your-writes is a? | Session (client-centric) guarantee |

### Spaced repetition
- **24-hour:** draw the CAP triangle and place 5 databases as CP/AP; redo MCQs.
- **7-day:** explain ACID vs BASE and the four NoSQL families with examples; sketch 2PC.
- **30-day:** design polyglot storage for a given app and justify each choice; compare sharding strategies.

---

## 11.15 Summary — and the Whole Syllabus

Distributed databases trade single-machine simplicity for **scale, availability, and
low latency**, using **partitioning** (horizontal/vertical fragmentation =
sharding) and **replication**. The **CAP theorem** says that, because partitions are
unavoidable, you must choose **consistency (CP)** or **availability (AP)** when the
network splits — and **ACID** (strong, CP-leaning) gives way to **BASE** (eventually
consistent, AP-leaning) at scale, with **PACELC** adding the latency-vs-consistency
trade in normal operation. We surveyed **consistency models** (strong → eventual),
the four **NoSQL families** (key-value, document, column-family, graph),
**sharding** strategies (range / hash / **consistent hashing**), and **two-phase
commit** for cross-node atomicity (and its blocking weakness). Finally, **SQL vs
NoSQL** is a tooling choice, real systems are **polyglot**, and **NewSQL** unites
SQL, scale, and ACID.

> **The DBMS journey, end to end:** we began with the **relational model** and
> **SQL** (M1–M4), made schemas sound via **normalization** (M5), made access fast
> with **storage, indexing, and query optimization** (M6–M8), made data **correct
> under concurrency and crashes** with **transactions and recovery** (M9–M10), and
> finally **scaled out** to distributed and NoSQL systems (M11). Together these are
> the complete mental model of how a modern database **stores, finds, protects, and
> scales** data — exactly what SEBI/RBI IT, GATE, and backend interviews test.

> **You have mastered this module when** you can: state CAP and justify a CP/AP
> choice for a given app; contrast ACID and BASE; name the four NoSQL families with
> use-cases; explain horizontal vs vertical fragmentation and the three sharding
> strategies; and walk through 2PC including its blocking failure — all without
> notes.
