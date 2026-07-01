---
title: "Module 9 — Transactions & Concurrency Control"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 9 — Transactions & Concurrency Control

> **Where this module sits.**
> Modules 1–8 made data **fast to query**. This module makes it **correct when many
> users hit it at once and when crashes happen**. It is the **single most important
> and most heavily tested** DBMS topic for **SEBI Grade A IT, RBI, and GATE** — the
> source video devotes its entire **Chapter 1** to it. Master **ACID**,
> **serializability** (conflict & view), **2PL**, **deadlocks**, **timestamp
> ordering**, and **isolation levels**, and you own the highest-value section of the
> whole subject.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★★  | ★★★★★   | ★★★★      | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **ACID**; **conflict
serializability + precedence graph (cycle test)**; **view serializability**;
**2PL & its variants** (strict/rigorous/conservative); **deadlock**
(wait-die/wound-wait, wait-for graph); **timestamp ordering + Thomas write rule**;
**recoverable / cascadeless / strict** schedules; **isolation levels vs anomalies**
(dirty/unrepeatable/phantom); **MVCC / snapshot isolation**.

---

## 9.1 What Is a Transaction?

A **transaction** is a **logical unit of work** — a sequence of operations that the
DBMS treats as a **single, indivisible** action (e.g. "transfer ₹500 from A to B" =
*debit A* **and** *credit B*).

![Transaction states: active → partially committed → committed; or active → failed → aborted.](images/90_transaction_states.png)

**Transaction states:** **active** (executing) → **partially committed** (after the
last operation) → **committed** (changes permanent); or → **failed** → **aborted**
(rolled back, as if it never ran).

> **Two outcomes only:** a transaction either **commits** (all changes durable) or
> **aborts** (all changes undone). There is no "half done" visible to others — that
> is the promise the rest of this module enforces.

---

## 9.2 ACID Properties

![ACID: Atomicity (all-or-nothing), Consistency (valid→valid), Isolation (concurrent txns don't interfere), Durability (committed=permanent), with the bank-transfer example.](images/91_acid.png)

| Property | Meaning | Bank-transfer example | Enforced by |
|----------|---------|------------------------|-------------|
| **Atomicity** | all-or-nothing | debit **and** credit both happen, or **neither** | transaction manager (undo) |
| **Consistency** | valid state → valid state | total money unchanged; constraints hold | application + DBMS |
| **Isolation** | concurrent txns don't interfere | two transfers at once don't corrupt balances | **concurrency control** |
| **Durability** | committed = permanent | a crash after "success" can't undo it | **recovery / WAL** (Module 10) |

> **The big mental split:** **A** and **D** protect against **crashes** (Module
> 10 — recovery); **I** protects against **concurrency** (this module — the rest of
> it); **C** is the *goal* that A+I+D together preserve. Memory hook: **A**ll-or-
> nothing, **C**orrect, **I**solated, **D**urable.

---

## 9.3 Why Concurrency Control? The Anomalies

Running transactions **concurrently** boosts throughput, but **uncontrolled**
interleaving causes four classic problems.

![Concurrency problems: lost update, dirty read, unrepeatable read, phantom read.](images/92_concurrency_problems.png)

| Anomaly | What happens |
|---------|--------------|
| **Lost update** | T1 and T2 both read X, both write → one update is **overwritten/lost** |
| **Dirty read** | T2 reads X written by T1, then T1 **aborts** → T2 used invalid data |
| **Unrepeatable read** | T1 reads X twice; T2 modifies X in between → T1 sees **different** values |
| **Phantom read** | T1 re-runs a range query; T2 **inserts** a new matching row → a **phantom** appears |

> **The whole point of isolation:** prevent these. Which ones are *allowed* is set
> by the **isolation level** (§9.13). Lower levels permit some anomalies for more
> speed.

---

## 9.4 Schedules — Serial vs Concurrent

A **schedule** is the **order** in which operations of multiple transactions
execute.

![Serial schedule runs transactions one at a time (always correct, slow); concurrent schedule interleaves them (fast, but may be incorrect unless serializable).](images/93_schedules.png)

- **Serial schedule:** transactions run **one at a time**, no interleaving — always
  **correct**, but **no parallelism** (slow).
- **Concurrent (interleaved) schedule:** operations interleave — **fast**, but may
  be **incorrect**.

> **The central goal of concurrency control:** get the **speed** of concurrency
> with the **correctness** of serial execution. We accept a concurrent schedule if
> and only if it is **serializable** — i.e. **equivalent to *some* serial
> schedule**.

---

## 9.5 Conflict Serializability

![Two operations conflict if they are from different transactions, on the same data item, and at least one is a write; conflict matrix shows R-R is safe, R-W/W-R/W-W conflict.](images/94_conflict_serializability.png)

**Two operations conflict** if they (1) belong to **different** transactions, (2)
access the **same** data item, and (3) **at least one is a write**.

| | Read | Write |
|--|------|-------|
| **Read** | no conflict | **conflict** |
| **Write** | **conflict** | **conflict** |

A schedule is **conflict serializable** if we can **swap non-conflicting adjacent
operations** to transform it into a **serial** schedule.

> **R-R never conflicts** (two reads can be reordered freely). Any pair involving a
> **write** on the same item conflicts (their order changes the result).

---

## 9.6 Precedence Graph — Testing Conflict Serializability

![Precedence graph: a node per transaction, an edge Ti→Tj when an operation of Ti conflicts with and precedes one of Tj; acyclic ⇒ conflict serializable (topological sort gives the serial order), a cycle ⇒ not serializable.](images/95_precedence_graph.png)

**Build the precedence (serialization) graph:**

1. One **node per transaction**.
2. Add an edge **Ti → Tj** if an operation of **Ti conflicts with and comes
   *before*** an operation of **Tj** (on the same item).

> **THE RULE (memorize):** a schedule is **conflict serializable ⟺ its precedence
> graph has NO CYCLE.** If acyclic, a **topological sort** of the graph gives an
> equivalent **serial order**.

> **Worked example:** in schedule S, T1 writes A then T2 reads A (T1→T2); T2 writes
> B then T3 reads B (T2→T3); T3 writes C then T1 reads C (T3→T1). Edges
> T1→T2→T3→T1 form a **cycle** → **not** conflict serializable. Remove the last
> conflict and you'd get T1→T2→T3 (acyclic) → serializable, serial order **T1, T2,
> T3**.

### 9.6A Fully worked check (schedule → graph → verdict → serial order)

Let's do one end-to-end the way GATE asks it. Given the schedule (subscript = txn):

```text
S :  r1(A) ; r2(A) ; w1(A) ; r3(A) ; w4(B) ; r2(B) ; w3(C) ; w4(C)
```

**Step 1 — list every conflicting pair** (different txns, same item, at least one
write). Read-read pairs are skipped (they never conflict).

```text
Item A:  r2(A) .. w1(A)   -> T2 precedes T1's write   => edge T2 -> T1
         w1(A) .. r3(A)   -> T1's write precedes r3   => edge T1 -> T3
         r1(A) .. w1(A)   -> SAME txn (T1) -> ignore
Item B:  w4(B) .. r2(B)   -> T4's write precedes r2   => edge T4 -> T2
Item C:  w3(C) .. w4(C)   -> T3's write precedes w4   => edge T3 -> T4
```

**Step 2 — draw the precedence graph** with those edges:

```text
   T2 ──▶ T1 ──▶ T3 ──▶ T4 ──▶ T2   ??
```

**Step 3 — cycle test.** Follow the edges: `T2 → T1 → T3 → T4 → T2`. That returns to
**T2** — a **cycle**.

> **Verdict:** the graph has a cycle → schedule S is **NOT conflict serializable.**
> (It may still be *view* serializable, but that is NP-hard to test — see §9.7.) If
> you delete the last write `w4(C)`, the `T3→T4` edge disappears, the cycle breaks,
> and the graph `T2→T1→T3, T4→T2` becomes acyclic → **conflict serializable**, with
> the topological order **T4, T2, T1, T3**.

![Worked precedence graph for an acyclic schedule: T1 points to T2 and T3, both point to T4; no cycle so the topological sort T1,{T2,T3},T4 is an equivalent serial schedule.](images/190_worked_precedence_graph.png)

### 9.6B Counting conflict-equivalent serial schedules

A frequent GATE twist: *"How many distinct serial schedules is a given schedule
conflict-equivalent to?"* Answer = **the number of distinct topological sorts of the
acyclic precedence graph** (a cyclic graph has **zero**).

> **Worked count.** Suppose the graph is `T1→T2, T1→T3, T2→T4, T3→T4` (the acyclic
> graph pictured above). T1 must come first, T4 last, and T2/T3 are unordered
> relative to each other → the valid serial orders are **T1,T2,T3,T4** and
> **T1,T3,T2,T4** = **2** conflict-equivalent serial schedules.

> **Exam trap:** a conflict-serializable schedule can be equivalent to **more than
> one** serial order (whenever the graph leaves some transactions unordered). If the
> graph is a single chain (total order), the answer is exactly **1**.

---

## 9.7 View Serializability

A more **general** (looser) notion of correctness.

![View serializability: two schedules are view-equivalent if they agree on initial reads, read-from (updated read) relationships, and final writes; conflict-serializable ⇒ view-serializable but not vice versa, and testing view serializability is NP-hard.](images/96_view_serializability.png)

Schedule S is **view equivalent** to a serial schedule S′ if, for **every** data
item, all three hold:

1. **Initial read:** the txn that reads the *initial* value of X in S also does in
   S′.
2. **Updated read (read-from):** if Ti reads X *written by* Tj in S, the same holds
   in S′.
3. **Final write:** the txn doing the *last* write of X in S also does in S′.

S is **view serializable** if it is view-equivalent to **some** serial schedule.

> **The relationship (classic exam fact):** **every conflict-serializable schedule
> is view-serializable, but NOT vice-versa.** View serializability is **more
> general** — it accepts some schedules with **blind writes** (a write without a
> prior read) that conflict-serializability rejects. **But** testing view
> serializability is **NP-hard**, so real DBMSs enforce the stricter, cheap-to-test
> **conflict** serializability.

---

## 9.8 Recoverable, Cascadeless & Strict Schedules

Serializability ensures *concurrency* correctness; **recoverability** ensures we
can *undo* safely after an abort.

![Recoverable schedules nest: strict ⊆ cascadeless ⊆ recoverable; irrecoverable schedules let a committed transaction depend on one that later aborts.](images/97_recoverable_schedules.png)

| Schedule type | Condition |
|---------------|-----------|
| **Irrecoverable** | Tj reads from Ti, Tj **commits**, then Ti **aborts** → can't undo Tj. **BAD** |
| **Recoverable** | Tj commits only **after** the Ti it read from commits (minimum requirement) |
| **Cascadeless** | Tj reads X only **after** the writer Ti has **committed** → no cascading aborts |
| **Strict** | Tj neither reads nor writes X until the last writer Ti **commits/aborts** → trivial recovery |

> **Nesting (strictest → loosest):** **Strict ⊆ Cascadeless ⊆ Recoverable.**
> **Cascading rollback** = one abort forces aborting every transaction that read
> its uncommitted data — expensive; **cascadeless** schedules avoid it. **Strict**
> schedules (used by Strict 2PL) make recovery simplest.

---

## 9.9 Lock-Based Protocols & Two-Phase Locking (2PL)

The most common way to *enforce* serializability is **locking**.

![Lock compatibility matrix (S-S compatible, anything with X incompatible) and the two-phase locking growing/shrinking phases with the lock point at the peak.](images/98_2pl.png)

**Lock modes:** **Shared (S)** = read lock (many txns may hold it); **Exclusive
(X)** = write lock (only one, blocks all others).

| | S | X |
|--|---|---|
| **S** | ✅ compatible | ❌ |
| **X** | ❌ | ❌ |

**Two-Phase Locking (2PL):** every transaction has two phases —

- **Growing phase:** may **acquire** locks, **may not release** any.
- **Shrinking phase:** may **release** locks, **may not acquire** any.

Once a transaction **releases its first lock**, it can **never acquire another**.

> **THE GUARANTEE:** **2PL produces only conflict-serializable schedules.** The
> **lock point** (the moment a txn holds all its locks = end of growing phase)
> determines the equivalent serial order. **But basic 2PL does NOT prevent
> deadlock**, and can cause **cascading rollback**.

### Variants of 2PL

![2PL variants: basic, conservative (deadlock-free), strict (holds X locks to commit, cascadeless), rigorous (holds all locks to commit).](images/99_2pl_variants.png)

| Variant | Rule | Guarantees | Note |
|---------|------|------------|------|
| **Basic 2PL** | growing then shrinking | conflict serializable | deadlock + cascading possible |
| **Conservative (static)** | acquire **all** locks **before** starting | **deadlock-free** | must predict all locks |
| **Strict 2PL** | hold all **X** locks until commit/abort | cascadeless + recoverable | **most used** |
| **Rigorous 2PL** | hold **all** locks (S and X) until commit/abort | strict + simple serial order | least concurrency |

> **Exam favourites:** **Strict 2PL** is the practical default (no cascading
> rollback). **Conservative 2PL** is the **only deadlock-free** variant (it grabs
> everything upfront). **Rigorous** holds even read locks to the end.

### 9.9A Worked 2PL schedule — finding the lock point

Trace two transactions under **basic 2PL** and mark the **lock point** (the instant a
txn holds its *last* lock — the peak of its growing phase). `L-S`/`L-X` = acquire
shared/exclusive lock; `U` = unlock.

```text
 T1                         T2
 ------------------------   ------------------------
 L-X(A)
 read A ; write A
                            L-S(B)
                            read B
 L-X(B)  ── must WAIT (T2 holds S on B) ... granted after T2 unlocks
 write B
 U(A) ; U(B)   <-- shrinking begins; nothing new acquired after this
                            U(B)
```

**Where is each lock point?**

```text
T1 lock point  =  right after L-X(B) is granted   (T1 now holds A and B — its max set)
T2 lock point  =  right after L-S(B) is granted   (T2's only lock)
```

> **The serial order 2PL produces = the order of lock points.** T2 reaches its lock
> point before T1 does, so the schedule is conflict-equivalent to the serial order
> **T2, T1**. This is *why* 2PL guarantees conflict serializability: no txn can grab a
> new lock after releasing one, so lock points impose a consistent global order → the
> precedence graph is guaranteed **acyclic**.

**Same schedule under the three variants** (only *when locks are released* changes):

```text
BASIC 2PL    : T1 may U(A) as soon as it finishes A (before commit) -> a later abort
               of T1 could cascade to any txn that read A. Cascading possible.
STRICT 2PL   : T1 holds the X lock on A and B until it COMMITs/ABORTs, then releases.
               No one reads T1's uncommitted writes -> cascadeless.
RIGOROUS 2PL : T1 holds even its SHARED locks until commit -> simplest serial order,
               least concurrency.
```

### 9.9B Why 2PL is serializable yet can still deadlock

The very rule that makes 2PL correct is what lets it deadlock. In the trace above,
imagine T2 *also* needs `L-X(A)` while still holding `S(B)`:

```text
T1 holds X(A), wants X(B)  ──▶ waits for T2
T2 holds S(B), wants X(A)  ──▶ waits for T1
```

Neither can release (releasing would end its growing phase before it has all its
locks) → **wait-for cycle T1↔T2 = deadlock.** So 2PL trades one problem for another:
it **removes non-serializable schedules** but **introduces deadlock** (resolved by
detection + victim rollback, §9.10, or avoided entirely by **conservative** 2PL).

### Lock conversion (upgrade / downgrade)

A transaction can hold a weaker lock and **convert** it:

- **Upgrade** `S → X` (it read X, now wants to write) — allowed **only in the
  growing phase**.
- **Downgrade** `X → S` (done writing, will only read) — allowed **only in the
  shrinking phase**.

> **Why:** taking a shared lock first and **upgrading** only when needed gives more
> concurrency than grabbing an exclusive lock immediately. The phase restriction
> keeps 2PL's serializability guarantee intact.

### Multiple-granularity locking (IS / IX / SIX)

Locking every row individually is expensive when a transaction touches a whole
table. **Multiple-granularity locking** organizes data as a **hierarchy**
(database → file/table → page → record) and lets a txn lock at the **right level**.

To do this it adds **intention locks** on ancestors:

| Mode | Meaning |
|------|---------|
| **IS** (intention-shared) | intend to take **S** locks somewhere below |
| **IX** (intention-exclusive) | intend to take **S/X** locks below |
| **SIX** (shared + intention-exclusive) | **S** on this node **plus** intend **X** below |

> **The rule:** to lock a node in **S** you must hold **IS (or IX)** on **all its
> ancestors**; to lock it in **X** you must hold **IX (or SIX)** on all ancestors.
> Locks are acquired **root → leaf**, released **leaf → root**. This lets the DBMS
> lock a whole table with **one** lock instead of millions of row locks, while
> still allowing fine-grained row locking elsewhere.

---

## 9.10 Deadlocks

![Deadlock: a cycle in the wait-for graph; prevention via wait-die / wound-wait timestamp schemes; detection via wait-for graph or timeout; the four Coffman conditions.](images/100_deadlock.png)

A **deadlock** is a cycle of transactions each waiting for a lock the next holds —
none can proceed.

**Detection:** build a **wait-for graph** (node per txn, edge Ti→Tj if Ti waits for
a lock Tj holds); a **cycle = deadlock**. Resolve by rolling back a **victim**. Or
use **timeout** (abort a txn waiting too long).

**Prevention (timestamp-based; older TS = higher priority):**

- **Wait-Die (non-preemptive):** if an **older** txn requests a lock held by a
  **younger** one, it **waits**; if a **younger** requests an **older's** lock, it
  **dies** (rolls back, restarts with same TS).
- **Wound-Wait (preemptive):** if an **older** requests a **younger's** lock, it
  **wounds** (rolls back) the younger; if a **younger** requests an **older's**
  lock, it **waits**.

> **Memory hook:** in **both** schemes the **older transaction never dies** (it
> either waits or wins) — this guarantees **no starvation** (an old txn eventually
> gets priority). **Wait-die:** younger *dies*. **Wound-wait:** older *wounds*
> younger.

> **Four (Coffman) conditions** for deadlock — all must hold: **mutual exclusion,
> hold-and-wait, no preemption, circular wait.** Breaking any one prevents
> deadlock.

---

## 9.11 Timestamp-Ordering (TO) Protocol

A **lock-free** alternative: order transactions by a **timestamp** assigned at
start, and force conflicting operations to obey that order.

![Timestamp ordering: each item has read- and write-timestamps; reads/writes that violate timestamp order are rejected and the transaction rolls back; Thomas write rule ignores outdated writes.](images/101_timestamp_ordering.png)

Each transaction T gets a unique **TS(T)** at start (older = smaller). Each item X
keeps **R-timestamp(X)** (largest TS that read X) and **W-timestamp(X)** (largest TS
that wrote X).

- **Read X by T:** if `TS(T) < W-timestamp(X)` (a *newer* txn already wrote X) →
  **reject, roll back T**. Else read, and set `R-ts(X) = max(R-ts(X), TS(T))`.
- **Write X by T:** if `TS(T) < R-ts(X)` **or** `TS(T) < W-ts(X)` → **reject, roll
  back T**. Else write, set `W-ts(X) = TS(T)`.

> **Thomas Write Rule (optimization):** if on a *write* `TS(T) < W-ts(X)`, the
> write is **obsolete** (a newer write already exists) → **ignore it** instead of
> rolling back. Allows more concurrency.

> **Worked example (a rejected operation).** Let `TS(T1)=5`, `TS(T2)=10` (T1 older).
> Item X starts with `R-ts(X)=0`, `W-ts(X)=0`.
>
> ```text
>  op        rule check                           result
>  --------  -----------------------------------  -------------------------------
>  r2(X)     TS(2)=10 ≥ W-ts=0    OK              read; R-ts(X)=max(0,10)=10
>  w1(X)     TS(1)=5  < R-ts(X)=10  VIOLATION     REJECT -> roll back T1
> ```
>
> T1's write is rejected because a **younger** transaction (T2) has **already read**
> X — letting T1 write now would make T2's earlier read incorrect (T2 read a value
> that "should" have included T1's older write). T1 restarts with a **new, larger**
> timestamp. Note: had it been `w1(X)` with only `W-ts(X)=12 > 5` (no younger read),
> the **Thomas write rule** would simply **ignore** the write instead of rolling back.

> **Key property:** TO is **deadlock-free** (it never waits — it rejects/rolls
> back), but can cause **starvation** (a txn repeatedly restarted). Locking
> (2PL) waits and risks deadlock; timestamp ordering rolls back and risks
> starvation — the classic trade-off.

> **Handling starvation:** a transaction that keeps getting rolled back is
> eventually allowed to **keep its original (oldest) timestamp** on restart, so it
> gains the **highest priority** and finally succeeds — the same "the oldest never
> loses" idea used by wait-die / wound-wait.

### Optimistic (Validation-Based) Concurrency Control

When conflicts are **rare**, even checking timestamps on every operation is
wasteful. **Optimistic Concurrency Control (OCC)** assumes success and only checks
at the end, in **three phases**:

1. **Read phase:** the txn executes, reading freely and writing to a **private,
   local copy** (no changes visible to others yet).
2. **Validation phase:** at commit, the DBMS checks whether this txn's read/write
   set **conflicts** with transactions that committed concurrently (using
   start/validation/finish timestamps).
3. **Write phase:** if validation **passes**, apply the local changes to the
   database; otherwise **roll back** and restart.

> **Trade-off:** OCC is **deadlock-free** and has almost no locking overhead, so
> it's excellent under **low contention** (e.g. mostly-read workloads). Under
> **high** contention it wastes work on rollbacks and can **starve**. It's the
> conceptual cousin of MVCC/snapshot isolation (validate-at-commit).

---

## 9.12 MVCC — Multiversion Concurrency Control

![MVCC keeps multiple versions of each item so writes create new versions and reads see a consistent snapshot; readers never block writers and vice versa; snapshot isolation underlies PostgreSQL/Oracle.](images/102_mvcc.png)

**MVCC** keeps **multiple versions** of each data item. A **write creates a new
version** (it doesn't overwrite); a **read** returns the version appropriate to the
reader's snapshot.

> **The win:** **readers never block writers, and writers never block readers** — a
> huge concurrency gain. This is what **PostgreSQL, Oracle, and MySQL InnoDB**
> actually use.

**Snapshot isolation:** each transaction sees a **consistent snapshot** of the
database as of its start. Avoids dirty and unrepeatable reads with little locking.

> **Caveat:** plain snapshot isolation can still allow **write skew** (it is **not
> fully serializable**); **Serializable Snapshot Isolation (SSI)** closes that gap.
> Old versions are garbage-collected later (e.g. `VACUUM` in PostgreSQL).

### 9.12A Worked multiversion trace (read-ts / write-ts per version)

Multiversion timestamp ordering keeps, for **each version** X_k of item X, a
**W-timestamp** (the txn that created it) and a **R-timestamp** (largest txn that read
it). A read of X by T is routed to the **newest version whose W-ts ≤ TS(T)** — so a
read **never fails**; only writes can be rejected.

> Let `TS(T1)=5`, `TS(T2)=10`, `TS(T3)=8`. X begins as version `X0` with `W-ts=0`.
>
> ```text
>  op       routed to / action                                   versions of X
>  -------  --------------------------------------------------   -----------------------
>  w1(X)    T1 writes -> create X1 with W-ts=5                    X0(w0)  X1(w5)
>  r2(X)    newest version with W-ts ≤ 10 -> X1 ; set R-ts(X1)=10 X0      X1(w5,r10)
>  r3(X)    newest version with W-ts ≤ 8  -> X1 (reads T1's val)  X0      X1(w5,r10)
>  w2(X)    T2 writes -> create X2 with W-ts=10                   X0  X1  X2(w10)
> ```
>
> **The key win, made concrete:** `r3(X)` (an *older* reader, TS=8) still gets a
> valid, consistent version (`X1`) **even while** T2 is writing a new version `X2` —
> the reader and writer **never block each other**. A write is only rejected if some
> version already has a **read-timestamp greater** than the writer's TS (its read
> would have needed to see this write) — the multiversion analogue of the
> single-version rule in §9.11.

---

## 9.13 SQL Isolation Levels

The SQL standard exposes **four isolation levels** that trade correctness for
concurrency by choosing *which anomalies* are allowed.

![SQL isolation levels vs anomalies: Read Uncommitted allows all three; Read Committed blocks dirty reads; Repeatable Read also blocks unrepeatable reads; Serializable blocks all including phantoms.](images/103_isolation_levels.png)

| Isolation Level | Dirty Read | Unrepeatable Read | Phantom Read |
|-----------------|:----------:|:-----------------:|:------------:|
| **Read Uncommitted** | possible | possible | possible |
| **Read Committed** | ❌ no | possible | possible |
| **Repeatable Read** | ❌ no | ❌ no | possible |
| **Serializable** | ❌ no | ❌ no | ❌ no |

> **Higher isolation = fewer anomalies but less concurrency.** **Serializable** is
> the safest (no anomalies). Many databases default to **Read Committed** (e.g.
> PostgreSQL, Oracle). You pick per workload: analytics may tolerate Read
> Committed; money movement wants Serializable.

> **Why phantoms are special (predicate / next-key locking):** ordinary **row
> locks** only protect rows that **already exist**. A concurrent **INSERT** of a new
> row matching the query's predicate had **no row to lock**, so it slips through and
> appears as a **phantom** on re-query. Preventing phantoms therefore needs
> **predicate locks** (lock the *condition*, e.g. `salary > 50000`) or
> **index-range / next-key locks** (MySQL InnoDB locks the gaps between index keys),
> or simply **Serializable** isolation. This is why phantoms persist up to
> Repeatable Read and only vanish at Serializable.

---

## 9.14 Deciding Serializability — the Test Flow

![Flowchart: build the precedence graph; if it has a cycle it is not conflict serializable (possibly still view serializable); if acyclic it is conflict serializable and a topological sort gives the serial order.](images/104_fc_serializability.png)

1. **Build the precedence graph.**
2. **Cycle? →** not conflict serializable (might still be *view* serializable — but
   that's NP-hard to test).
3. **Acyclic? →** conflict serializable; **topological sort = serial order**.

> In practice, DBMSs **enforce** conflict serializability *proactively* (via 2PL /
> timestamp ordering / MVCC) rather than testing schedules after the fact.

---

## 9.15 Real-World & Backend Perspectives

- **`BEGIN; … COMMIT;` / `ROLLBACK`** delimit transactions; **`SET TRANSACTION
  ISOLATION LEVEL …`** picks the level.
- **PostgreSQL/Oracle/MySQL-InnoDB use MVCC** — so "readers don't block writers" is
  real; you mostly tune the **isolation level**.
- **Deadlocks happen in production:** the DB detects a cycle and **aborts a
  victim**; apps must **retry** the aborted transaction. Always order lock
  acquisition consistently to reduce deadlocks.
- **`SELECT … FOR UPDATE`** takes explicit row locks; long transactions hold locks
  longer → more contention.

---

## 9.16 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Saying **R-R conflicts** (it does **not**).
- Thinking **2PL prevents deadlock** (it does **not** — only *conservative* 2PL).
- Confusing **wait-die** and **wound-wait** (younger *dies* vs older *wounds*).
- Believing **view ⊆ conflict** — it's the **reverse** (conflict ⊆ view).
- Thinking serializable = serial (serializable means *equivalent to* some serial).
- Forgetting **timestamp ordering is deadlock-free but starvation-prone**.

**Edge cases**
- A schedule can be **view-serializable but not conflict-serializable** (blind
  writes).
- A schedule can be **serializable but not recoverable** (correct concurrency, unsafe
  on abort) — both properties are needed.
- **Phantoms** need range/predicate locks (or serializable isolation), not just
  row locks.

**Tradeoffs**

| Mechanism | Strength | Weakness |
|-----------|----------|----------|
| 2PL (locking) | simple, guarantees serializability | deadlocks, blocking |
| Timestamp ordering | deadlock-free | starvation, many rollbacks |
| MVCC | readers don't block writers | version storage, write skew (SI) |
| Higher isolation | fewer anomalies | less concurrency |

---

## 9.17 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** ACID; build a **precedence graph** and decide conflict
serializability; view vs conflict (conflict ⊆ view, view NP-hard); 2PL + variants;
**wait-die/wound-wait**; timestamp rules + Thomas write rule; recoverable/
cascadeless/strict; **isolation level vs anomaly** table.

**Interview:** "What are ACID properties?"; "How does the DB prevent two people
overdrawing the same account?" (locking/isolation); "What's a deadlock and how is
it resolved?"; "Explain MVCC / why readers don't block writers"; "difference
between Read Committed and Serializable".

**Coding/practical:**
- Open two `psql` sessions, set isolation levels, and reproduce a dirty/unrepeatable
  read; then raise the level and see it disappear.
- Force a deadlock with two sessions locking rows in opposite order; watch the DB
  abort a victim.

---

## 9.18 Concept Checks & MCQs

1. A transaction ends in one of two states: ___ or ___ → **committed / aborted**.
2. Which ACID property is about concurrency? → **Isolation**. About crashes? →
   **Atomicity & Durability**.
3. Do two reads on the same item conflict? → **No**.
4. Conflict serializable ⟺ precedence graph has ___ → **no cycle**.
5. Conflict ⊆ view or view ⊆ conflict? → **conflict ⊆ view** (conflict is stricter).
6. Why don't DBMSs test view serializability? → it's **NP-hard**.
7. Does basic 2PL prevent deadlock? → **No** (only conservative 2PL does).
8. Strict 2PL holds which locks till commit? → all **exclusive (X)** locks.
9. In wait-die, who rolls back: older or younger? → **younger** (dies).
10. In wound-wait, who rolls back: older or younger? → **younger** (older wounds it).
11. Timestamp ordering: deadlock-free but suffers ___ → **starvation**.
12. Thomas write rule: an outdated write is ___ → **ignored**.
13. Nesting of schedules (strictest first)? → **strict ⊆ cascadeless ⊆ recoverable**.
14. Which isolation level allows phantoms but not unrepeatable reads? →
    **Repeatable Read**.
15. MVCC's main benefit? → **readers don't block writers** (and vice-versa).
16. OCC's three phases? → **read, validation, write**.
17. Intention locks for multiple-granularity locking? → **IS, IX, SIX**.
18. Upgrade S→X is allowed only in which 2PL phase? → **growing**.
19. What prevents phantoms (besides Serializable)? → **predicate / index-range
    (next-key) locks**.

**True/False**
- Every serializable schedule is serial. → **False** (equivalent to *some* serial).
- 2PL guarantees conflict serializability. → **True**.
- Read Committed prevents unrepeatable reads. → **False**.
- A view-serializable schedule may not be conflict-serializable. → **True**.

**Numerical (do it):**
> Schedule: `r1(A); r2(A); w1(A); w2(A)`. Conflicts: r2(A)–w1(A) → **T2→T1**;
> w1(A)–w2(A) → **T1→T2**; r1(A)–w2(A) → **T1→T2**. Edges **T1→T2 and T2→T1** form a
> **cycle** → **NOT conflict serializable.** ✔

**More (new subsections):**
20. If a precedence graph is a single chain of 4 nodes, how many conflict-equivalent
    serial schedules? → **1** (a total order).
21. If the graph is `T1→T2, T1→T3, T2→T4, T3→T4`, how many? → **2**
    (T1,T2,T3,T4 and T1,T3,T2,T4).
22. In 2PL, the equivalent serial order is given by the order of ___ → **lock
    points**.
23. Under strict 2PL, until when are exclusive locks held? → **until commit/abort**.
24. TO: `w1(X)` with `TS(1)=5 < R-ts(X)=10` → ___ → **reject and roll back T1**.
25. In MVCC, a read is routed to → **the newest version with W-ts ≤ TS(reader)**.
26. Can a *read* ever be rejected in multiversion TO? → **No** (only writes can be).

**Numerical (do it) — full serializability check:**
> `S: r1(A); r2(A); w1(A); r3(A); w4(B); r2(B); w3(C); w4(C)`. Edges: **T2→T1**
> (r2(A)–w1(A)), **T1→T3** (w1(A)–r3(A)), **T4→T2** (w4(B)–r2(B)), **T3→T4**
> (w3(C)–w4(C)). Follow them: `T2→T1→T3→T4→T2` = **cycle** → **NOT conflict
> serializable.** ✔

---

## 9.19 One-Page Revision Sheet

```
TRANSACTION = logical unit of work. states: active -> partially committed -> committed | failed -> aborted.

ACID: Atomicity (all-or-nothing), Consistency (valid->valid), Isolation (concurrency), Durability (committed=permanent).
  A,D = crash safety (M10 recovery). I = concurrency (this module). C = the goal.

ANOMALIES (uncontrolled interleaving): LOST UPDATE, DIRTY READ, UNREPEATABLE READ, PHANTOM.

SCHEDULE serial (correct, slow) vs concurrent (fast, maybe wrong). GOAL = SERIALIZABLE (= equiv to SOME serial).

CONFLICT: diff txns + same item + at least one WRITE. (R-R no; R-W,W-R,W-W yes.)
CONFLICT SERIALIZABLE <=> precedence graph ACYCLIC. edge Ti->Tj if Ti's op conflicts & precedes Tj's. topo-sort=order.
VIEW SERIALIZABLE: initial read + read-from + final write match a serial schedule.
  conflict-serial SUBSET view-serial (NOT reverse). view test = NP-HARD -> DBMS uses conflict.

RECOVERABILITY: STRICT subset CASCADELESS subset RECOVERABLE. irrecoverable=committed txn read from later-aborted txn.

LOCKS: S (shared/read, many) , X (exclusive/write, one). compat: S-S yes, else no.
2PL: GROWING (acquire only) then SHRINKING (release only). once you release, no new lock. => conflict serializable.
  basic 2PL: deadlock+cascading possible. CONSERVATIVE = deadlock-FREE (locks upfront).
  STRICT = hold X till commit (cascadeless, most used). RIGOROUS = hold ALL locks till commit.
  LOCK CONVERSION: upgrade S->X (growing phase only); downgrade X->S (shrinking phase only).
  MULTIPLE GRANULARITY: lock hierarchy DB->table->page->row with INTENTION locks IS/IX/SIX
    (to S-lock a node hold IS/IX on ancestors; to X-lock hold IX/SIX). lock root->leaf, release leaf->root.

OPTIMISTIC (OCC): 3 phases READ (local copies) -> VALIDATION (conflict check) -> WRITE. deadlock-free, low-contention best.
TO STARVATION fix: restart the victim with its OLDEST timestamp so it eventually wins priority.

DEADLOCK: cycle in WAIT-FOR graph. detect->rollback victim; or timeout. prevention (older=priority):
  WAIT-DIE (non-preemptive): younger requesting older's lock DIES; older WAITS.
  WOUND-WAIT (preemptive): older requesting younger's lock WOUNDS younger; younger WAITS.
  (older never dies -> no starvation). Coffman: mutual excl, hold&wait, no preempt, circular wait.

TIMESTAMP ORDERING: TS at start. R-ts/W-ts per item. violate order -> reject+rollback. DEADLOCK-FREE, STARVATION-prone.
  THOMAS WRITE RULE: outdated write (TS<W-ts) -> IGNORE (not rollback).

MVCC: many versions; write=new version; read=snapshot. readers don't block writers. snapshot isolation (PG/Oracle).
  caveat: SI allows WRITE SKEW (not fully serializable) -> SSI fixes.

ISOLATION LEVELS (anomaly allowed?):
  READ UNCOMMITTED: dirty Y, unrepeatable Y, phantom Y
  READ COMMITTED:   dirty N, unrepeatable Y, phantom Y   (common default)
  REPEATABLE READ:  dirty N, unrepeatable N, phantom Y
  SERIALIZABLE:     dirty N, unrepeatable N, phantom N   (safest)
```

### Flash cards

| Front | Back |
|-------|------|
| ACID = ? | Atomicity, Consistency, Isolation, Durability |
| Which ACID for concurrency? | Isolation |
| Do two reads conflict? | No |
| Conflict serializable test? | Precedence graph has no cycle |
| Conflict vs view subset? | conflict ⊆ view |
| View serializability test cost? | NP-hard |
| Does 2PL prevent deadlock? | No (only conservative 2PL) |
| Most-used 2PL variant? | Strict 2PL |
| Wait-die: who rolls back? | Younger (dies) |
| Wound-wait: who rolls back? | Younger (older wounds it) |
| Timestamp ordering: deadlock? | Free, but starvation-prone |
| Thomas write rule? | Ignore an outdated write |
| Schedule nesting? | strict ⊆ cascadeless ⊆ recoverable |
| Repeatable Read allows? | Phantoms only |
| MVCC benefit? | Readers don't block writers |
| OCC phases? | Read, validation, write |
| Intention lock modes? | IS, IX, SIX |
| Prevent phantoms how? | Predicate / next-key locks (or Serializable) |

### Spaced repetition
- **24-hour:** build precedence graphs for 3 schedules; redo the isolation-levels table from memory.
- **7-day:** explain 2PL variants + wait-die/wound-wait; trace a timestamp-ordering schedule.
- **30-day:** given a schedule, decide conflict & view serializability, recoverability, and which 2PL/level would produce it.

---

## 9.20 Summary

Transactions make data **correct under concurrency and crashes**. A transaction is
an **all-or-nothing logical unit** with **ACID** guarantees (A/D = crash safety,
I = concurrency, C = the goal). Uncontrolled interleaving causes **lost updates,
dirty/unrepeatable reads, and phantoms**, so we only accept **serializable**
schedules. **Conflict serializability** is tested with a **precedence graph**
(acyclic ⟺ serializable; topo-sort = order); **view serializability** is more
general but **NP-hard**, so DBMSs enforce conflict serializability — via **2PL**
(growing/shrinking; strict/rigorous/conservative variants) which can **deadlock**
(handled by **wait-for graphs**, **wait-die/wound-wait**), via **timestamp
ordering** (deadlock-free, starvation-prone, **Thomas write rule**), or via
**MVCC/snapshot isolation** (readers don't block writers). **Recoverability**
(strict ⊆ cascadeless ⊆ recoverable) ensures safe aborts, and **SQL isolation
levels** trade anomalies for concurrency.

Next, **Module 10 — Recovery & Backup** completes the **A** and **D** of ACID: how
the DBMS uses **logs (WAL)**, **checkpoints**, and protocols like **ARIES** to
restore a consistent state after a crash.

> **You have mastered this module when** you can: state ACID and map each letter to
> what protects it; build a precedence graph and decide conflict (and view)
> serializability; explain 2PL and all its variants; contrast wait-die vs
> wound-wait; apply the timestamp-ordering rules with the Thomas write rule; and
> fill the isolation-level-vs-anomaly table — all without notes.
