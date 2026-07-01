---
title: "Module 10 — Recovery & Backup"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10 — Recovery & Backup

> **Where this module sits.**
> Module 9 handled the **I** of ACID (isolation under concurrency). This module
> delivers the **A** and **D** — **atomicity** and **durability** *across
> crashes*. When the power dies mid-transfer, how does the database guarantee that
> committed money moves are **never lost** and half-finished ones **never persist**?
> The answer is the **log** + **Write-Ahead Logging** + a recovery algorithm
> (**ARIES**). It's a focused, highly **examinable** topic (undo/redo logic and the
> deferred-vs-immediate classification are reliable GATE/SEBI questions).

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★    | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **Write-Ahead Logging (WAL)**;
**deferred (NO-UNDO/REDO) vs immediate (UNDO/REDO)** update; **undo/redo lists**
after a crash; **checkpoints**; **STEAL/NO-FORCE** buffer policies; **ARIES**
(analysis/redo/undo, LSN); **shadow paging**; **log record format**; **backup
types** (full / incremental / differential).

---

## 10.1 Why Recovery? Failures & Storage

![Failure types (transaction, system crash, media) and storage types (volatile, non-volatile, stable); recovery uses a log on stable storage to undo uncommitted and redo committed work.](images/105_failures_storage.png)

**Types of failure:**

| Failure | Cause | Effect |
|---------|-------|--------|
| **Transaction failure** | logical error, abort, deadlock victim | one txn must be rolled back |
| **System crash** | power loss, OS crash | **RAM lost**, disk intact |
| **Media failure** | disk head crash, corruption | **disk lost** → need a backup |

**Storage types:** **volatile** (RAM — lost on power off), **non-volatile** (disk/SSD
— survives power off), **stable** (replicated so it "never" fails — an idealization
we approximate with redundancy).

> **First principle:** a crash can leave the database **half-done**, violating
> **atomicity** and **durability**. The recovery manager keeps a **log** on
> **stable** storage and, after a crash:
> - **UNDO** the effects of transactions that did **not** commit, and
> - **REDO** the effects of transactions that **did** commit (so committed work
>   survives).

---

## 10.2 The Log & Write-Ahead Logging (WAL)

The **log** is an append-only sequence of records, on **stable** storage,
describing every change.

![Log records of the form ⟨Ti, X, old, new⟩ plus start/commit; the Write-Ahead Logging rule writes the log before the data page and before reporting commit.](images/106_log_wal.png)

**Log record types:**

- `⟨Ti, START⟩` — transaction begins.
- `⟨Ti, X, old_value, new_value⟩` — Ti changed item X (old for **undo**, new for
  **redo**).
- `⟨Ti, COMMIT⟩` — transaction committed.
- `⟨Ti, ABORT⟩` — transaction aborted.

> **WRITE-AHEAD LOGGING (WAL) — the golden rule of recovery:**
> 1. The **log record** of a change must reach **stable storage BEFORE** the
>    changed **data page** is written to disk. *(So the old value is always
>    recoverable to UNDO an uncommitted change.)*
> 2. **All** log records of a transaction (including `⟨COMMIT⟩`) must be on stable
>    storage **before** the commit is reported to the user. *(So committed work can
>    always be REDONE → durability.)*

> **Why "write-ahead":** the log always runs *ahead* of the data. If the data page
> hit disk first and we crashed before logging, we'd have a change on disk with no
> way to undo it. WAL makes that impossible.

> **The log buffer (what "on stable storage" really means):** for performance, log
> records first accumulate in an **in-memory log buffer**; a record only counts as
> "on stable storage" once that buffer is **force-written (flushed/`fsync`)** to
> disk. So WAL rule 1 means *force the log up to a page's update record before
> writing that data page*, and WAL rule 2 is **"force-log-at-commit"** — flush the
> buffer through the `⟨COMMIT⟩` record before reporting success. This is exactly why
> **commit latency is dominated by the log `fsync`**.

---

## 10.3 Deferred vs Immediate Update

The recovery requirements depend on **when** modified pages are allowed to reach
disk.

![Deferred update (NO-UNDO/REDO) writes to disk only after commit; immediate update (UNDO/REDO) may write before commit; recovery actions differ accordingly.](images/107_deferred_immediate.png)

| | **Deferred update** | **Immediate update** |
|--|--------------------|----------------------|
| Disk writes happen | **only after** commit | **may happen before** commit |
| Log stores | **new** values only | **old + new** values |
| Committed txns | **REDO** | **REDO** |
| Uncommitted txns | **do nothing** (DB untouched) | **UNDO** (changes may be on disk) |
| Nickname | **NO-UNDO / REDO** | **UNDO / REDO** |

> **The intuition:** in **deferred** update, an uncommitted txn never touched the
> disk, so there is **nothing to undo**. In **immediate** update, its dirty pages
> *might* be on disk, so we **must undo**. Both **redo** committed txns (their
> changes might not have been flushed yet).

### 10.3A Worked side-by-side — same log, two update strategies

Take one log and one crash, and see how the recovery action differs:

```text
LOG:  ⟨T1,start⟩  ⟨T1,A,100,150⟩  ⟨T1,COMMIT⟩  ⟨T2,start⟩  ⟨T2,B,50,80⟩  --CRASH--
```

```text
                     DEFERRED (NO-UNDO/REDO)          IMMEDIATE (UNDO/REDO)
 T1 (committed)      REDO: set A = 150                REDO: set A = 150
 T2 (uncommitted)   *nothing* -- T2's write never    UNDO: set B back to 50
                     reached disk (deferred)          (its dirty page MAY be on disk)
```

> **Read the difference off the strategy.** Deferred update writes to the database
> **only after commit**, so T2's `B=80` was never applied to disk → **nothing to
> undo**. Immediate update **may** have flushed T2's dirty page before the crash → we
> **must undo** it back to the old value `50`. Both strategies **REDO** the committed
> T1, because with **NO-FORCE** even a committed txn's page may not have been flushed
> yet. Note deferred update only needs to log the **new** value; immediate update must
> log **both old and new** (old is needed for the undo).

### Buffer policies that decide this (STEAL / FORCE — a GATE favourite)

| Policy | Meaning | Implication |
|--------|---------|-------------|
| **STEAL** | buffer may write an **uncommitted** txn's dirty page to disk | **UNDO needed** |
| **NO-STEAL** | uncommitted dirty pages are **never** written early | **no UNDO** |
| **FORCE** | **all** dirty pages flushed to disk **at commit** | **no REDO** |
| **NO-FORCE** | dirty pages **not** forced at commit | **REDO needed** |

> **The practical choice:** real databases use **STEAL + NO-FORCE** → they need
> **both UNDO and REDO** (the most general case), because it gives the best buffer
> performance (flush whenever convenient, don't force at commit). **NO-STEAL +
> FORCE** needs neither undo nor redo but cripples buffer management.

---

## 10.4 Recovery: Which Transactions to UNDO vs REDO

![Crash timeline: transactions committed before the checkpoint need nothing; those committed after the checkpoint are redone; those active (uncommitted) at the crash are undone.](images/108_undo_redo.png)

After a crash, scan the log and classify each transaction:

- **Committed (has `⟨COMMIT⟩`) after the last checkpoint → REDO** (changes might
  not be flushed).
- **Active at crash (`⟨START⟩` but no `⟨COMMIT⟩`) → UNDO** (changes might be on
  disk).
- **Committed before the last checkpoint → nothing** (already safely on disk).

> **Order matters (immediate update):** UNDO is done **backward** (latest change
> first), REDO **forward** (oldest first). Many algorithms **redo first** (repeat
> history), **then undo** — this is what ARIES does.

---

## 10.5 Checkpoints

![A checkpoint flushes the log and all dirty pages to disk and writes a checkpoint record, so recovery only needs to scan back to the last checkpoint.](images/109_checkpoint.png)

Without checkpoints, recovery would scan the **entire** log from the beginning. A
**checkpoint** periodically:

1. flushes all **log records** to disk,
2. flushes all **modified (dirty) buffer pages** to disk,
3. writes a `⟨CHECKPOINT⟩` record to the log.

> **The payoff:** everything before the checkpoint is **safely on disk**, so
> recovery only scans the log **back to the last checkpoint** — bounding redo work
> and recovery time. *(A naïve checkpoint briefly pauses transactions; real systems
> use **fuzzy checkpoints** that don't stop the world.)*

### 10.5A Fuzzy (non-quiescent) checkpoints — how real systems avoid stopping the world

A **sharp/consistent checkpoint** must **quiesce** the system: block new
transactions and flush *every* dirty page before writing `⟨CKPT⟩`. On a busy database
that pause is unacceptable. A **fuzzy checkpoint** lets transactions keep running:

```text
1. write  ⟨BEGIN-CHECKPOINT⟩  to the log  (and record the active-txn list + DPT).
2. keep processing transactions normally; flush dirty pages LAZILY in the background.
3. once the pages that were dirty *at step 1* are safely on disk,
   write  ⟨END-CHECKPOINT⟩  -> the checkpoint is now valid.
```

> **Why it works:** the checkpoint record only *records* what was dirty; it does **not**
> require an instant global flush. Recovery therefore cannot assume everything before
> `⟨CKPT⟩` is on disk — so it starts REDO from the **earliest recLSN** in the recorded
> Dirty Page Table (this is exactly the **RedoLSN** ARIES computes, §10.6), not simply
> from the checkpoint record. **Trade-off:** fuzzy checkpoints add near-zero runtime
> pause but make recovery slightly more involved (it must consult the DPT). This is
> what PostgreSQL, Oracle, and ARIES-style engines actually do.

---

## 10.6 ARIES — the Industry-Standard Algorithm

![ARIES three phases — Analysis (rebuild dirty-page and transaction tables), Redo (repeat history), Undo (roll back losers with CLRs) — driven by LSNs.](images/110_aries.png)

Every log record gets a unique, increasing **LSN (Log Sequence Number)**; each data
page records the **pageLSN** of the last log record applied to it (so recovery
knows exactly what is/isn't applied). Recovery runs in **three phases**:

1. **Analysis:** scan **forward** from the last checkpoint to rebuild the **Dirty
   Page Table (DPT)** and **Transaction Table**, find where REDO must start, and
   identify the **loser** transactions (active, uncommitted at crash).
2. **Redo (repeat history):** re-apply **all** logged changes from the redo start
   point forward — **even those of losers** — to reconstruct the *exact* pre-crash
   state.
3. **Undo:** roll back the **losers**, writing **CLRs (Compensation Log Records)**
   so that the undo work is itself logged and **never redone** if we crash again
   during recovery.

> **The two tables, in detail (GATE probes these):** the **Dirty Page Table**
> stores a **recLSN** per dirty page (the LSN that *first* dirtied it); the
> **smallest recLSN** across all dirty pages is the **RedoLSN** — *where the Redo
> phase begins*. The **Transaction Table** stores a **lastLSN** per active txn, and
> every log record carries a **prevLSN** back-pointer; chaining these prevLSNs is how
> the **Undo** phase walks each loser's changes **backward**.

> **The three big ARIES ideas (exam):** (1) **WAL**, (2) **repeat history** during
> redo (redo everything, then selectively undo), (3) **log undos with CLRs** so
> recovery is **idempotent** (restart-safe). Most commercial databases follow ARIES
> in spirit.

### 10.6A ARIES worked walkthrough (LSN → DPT → Txn Table → three phases)

Recover from this log. `pageP` / `pageQ` are the data pages touched; `prevLSN` chains
each txn's records; `recLSN` is the LSN that *first* dirtied a page after the last
flush.

```text
 LSN   record                         page   prevLSN
 ----  -----------------------------  -----  -------
 10    ⟨T1, start⟩                     -      -
 20    ⟨T1, P, old, new⟩               P      10       <- first dirties P (recLSN=20)
 30    ⟨CHECKPOINT⟩  (fuzzy)           -      -
 40    ⟨T2, start⟩                     -      -
 50    ⟨T2, Q, old, new⟩               Q      40       <- first dirties Q (recLSN=50)
 60    ⟨T2, COMMIT⟩                    -      50
 70    ⟨T3, start⟩                     -      -
 80    ⟨T3, P, old, new⟩               P      70
 --CRASH--
```

**Phase 1 — Analysis** (scan forward from the checkpoint). Rebuild the two tables:

```text
 Dirty Page Table (DPT)          Transaction Table (TT)
 page  recLSN                     txn  status       lastLSN
 ----  ------                     ---  -----------  -------
 P     20                         T2   committed    60
 Q     50                         T3   ACTIVE       80   <- loser
                                  (T1 finished before ckpt; not a loser)
 RedoLSN = min(recLSN) = 20   -> Redo starts here.   Losers = {T3}
```

**Phase 2 — Redo (repeat history)** from **LSN 20** forward. Re-apply every logged
change whose `LSN > pageLSN` of its page — **including loser T3's LSN 80** — to rebuild
the exact pre-crash disk image. (Records already reflected on a page, i.e.
`pageLSN ≥ LSN`, are skipped.)

**Phase 3 — Undo the losers.** Walk **T3's** `prevLSN` chain backward: undo **LSN 80**
(restore P's old value), writing a **CLR** for it, then follow prevLSN 70 to T3's
start → done. If the system crashes *again* mid-undo, the CLR ensures LSN 80 is
**never undone twice** (idempotent).

![ARIES worked pass over a log with a checkpoint: Analysis builds the DPT and Txn table and finds RedoLSN and the loser set; Redo replays from RedoLSN including losers; Undo rolls back losers with CLRs.](images/191_aries_worked.png)

> **The exam-critical takeaways of this trace:** (1) **RedoLSN = smallest recLSN in
> the DPT** (here 20), *not* the checkpoint LSN — because with a fuzzy checkpoint a
> page dirtied before `⟨CKPT⟩` may still not be on disk. (2) Redo **repeats history**,
> replaying even the loser T3. (3) Undo is driven by the **prevLSN** back-pointer
> chain and logs **CLRs** for restart-safety.

---

## 10.7 Shadow Paging (a log-free alternative)

![Shadow paging keeps a current and a shadow page table; writes go to new page copies, commit atomically swaps the pointer, and a crash reverts to the shadow.](images/111_shadow_paging.png)

**Shadow paging** keeps **two page tables**: a **current** one (in use) and a
**shadow** one (saved). A write **copies the page to a new location** and points the
current table at it, leaving the shadow pointing at the **old** page.

- **Commit** = atomically make the current table the new shadow (one pointer write).
- **Crash before commit** = revert to the shadow table → old state.

> **Pros:** **no log, no undo, no redo** — recovery is trivial. **Cons:**
> expensive **page-table copying**, **data fragmentation**, hard to garbage-collect
> old pages, and poor concurrency support → **rarely used** in practice (WAL/ARIES
> won).

---

## 10.8 Backup & Media Recovery

A crash loses RAM; a **media (disk) failure** loses the data itself. Recovery from
that needs **backups** plus the log.

![Backup types: full (entire DB), incremental (changes since last backup), differential (changes since last full backup), with their backup/restore trade-offs.](images/112_backup_types.png)

| Type | Copies | Backup vs restore | Size |
|------|--------|-------------------|------|
| **Full** | the **entire** database | slow backup, fast restore | large |
| **Incremental** | changes since the **last backup** (of any type) | fast backup, **slow restore** (need the chain) | small |
| **Differential** | changes since the last **full** backup | medium / medium | grows over time |

**Media-recovery procedure:** restore the last **full** backup → apply
**incrementals/differential** → **roll forward** using the log (redo committed
transactions after the backup).

> **Don't confuse them (classic MCQ):** **Incremental** = "since the last *any*
> backup"; **Differential** = "since the last *full* backup." Differential restore
> needs only **full + latest differential**; incremental restore needs the **whole
> chain**.

---

## 10.9 The Recovery Decision Flow

![Flowchart: media failure → restore from backup + roll forward; system crash → log-based recovery (ARIES analysis → redo → undo) → consistent DB.](images/113_fc_recovery.png)

- **Media (disk) failure →** restore from **backup** + roll forward via log.
- **System crash (RAM lost) →** **log-based recovery** (ARIES: Analysis → Redo →
  Undo).
- **Transaction failure (single abort) →** **undo** just that transaction using its
  log records.

---

## 10.10 Real-World & Backend Perspectives

- **PostgreSQL WAL** (the `pg_wal` directory) is exactly this log; `fsync` enforces
  WAL ordering; **`CHECKPOINT`** is a real command.
- **Point-in-Time Recovery (PITR):** base backup + archived WAL lets you restore to
  **any moment** (e.g. "just before the bad `DELETE`").
- **Replication** ships the WAL to standby servers — the same log that powers
  recovery powers high availability.
- **`COMMIT` latency** is dominated by the WAL `fsync` (rule 2 of WAL) — group
  commit batches these.

---

## 10.11 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Swapping **deferred (NO-UNDO/REDO)** and **immediate (UNDO/REDO)**.
- Violating WAL order (writing data before its log) — breaks recoverability.
- Confusing **incremental** vs **differential** backup.
- Thinking a checkpoint means "no recovery needed" (it only **bounds** the work).
- Forgetting that ARIES **redoes losers too** (repeat history) before undoing them.
- Believing shadow paging is widely used (it isn't — WAL won).

**Edge cases**
- Crash **during recovery**: ARIES is **idempotent** (LSNs + CLRs) → just restart
  recovery.
- A transaction that committed but whose data pages weren't flushed → **REDO** saves
  it (durability).
- `⟨COMMIT⟩` written but the crash happened right after → still durable (WAL rule 2
  guarantees the log is stable).

**Tradeoffs**

| Choice | Gain | Cost |
|--------|------|------|
| STEAL + NO-FORCE | best buffer performance | needs both undo + redo |
| Frequent checkpoints | faster recovery | runtime overhead |
| Shadow paging | no log/undo/redo | copying, fragmentation, poor concurrency |
| Incremental backup | small, fast backup | slow chained restore |

---

## 10.12 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** WAL rules; deferred vs immediate (and their nicknames);
undo/redo lists from a log + checkpoint; STEAL/FORCE matrix; ARIES three phases &
LSN/CLR; shadow paging pros/cons; backup types and restore procedure.

**Interview:** "How does a DB guarantee durability?" (WAL + fsync at commit); "What
happens on recovery after a crash?" (redo committed, undo uncommitted); "What is a
checkpoint?"; "incremental vs differential backup".

**Coding/practical:**
- Inspect PostgreSQL `pg_wal`; run `CHECKPOINT`; do a base backup + PITR to a chosen
  time.
- Simulate: kill the server mid-transaction, restart, and observe the uncommitted
  change is gone (undo) and committed ones survive (redo).

---

## 10.13 Concept Checks & MCQs

1. ACID properties guaranteed by recovery? → **Atomicity & Durability**.
2. WAL rule 1: write the ___ before the ___ → **log record / data page**.
3. Deferred update needs undo? → **No** (NO-UNDO/REDO).
4. Immediate update needs ___ and ___ → **undo and redo**.
5. On crash, committed transactions are ___ → **redone**.
6. On crash, uncommitted (active) transactions are ___ → **undone**.
7. STEAL policy implies we need ___ → **UNDO**.
8. NO-FORCE policy implies we need ___ → **REDO**.
9. Real DBs use which buffer policy pair? → **STEAL + NO-FORCE**.
10. A checkpoint lets recovery scan back only to ___ → **the last checkpoint**.
11. ARIES three phases (in order)? → **Analysis, Redo, Undo**.
12. ARIES "repeat history" means redo even ___ transactions → **uncommitted (loser)**.
13. CLRs make recovery ___ → **idempotent / restart-safe**.
14. Differential backup copies changes since the last ___ → **full backup**.
15. Recovery technique with two page tables and no log? → **shadow paging**.
16. Log records are buffered in RAM and become durable only when ___ → **force-written
    / flushed (fsync) to stable storage**.
17. In ARIES, the smallest recLSN in the Dirty Page Table gives the ___ → **RedoLSN
    (where Redo starts)**.

**True/False**
- WAL allows writing a data page before its log record. → **False**.
- Deferred update requires undo. → **False**.
- Differential restore needs the full backup plus the latest differential only. →
  **True**.
- ARIES undoes losers before redoing committed transactions. → **False** (redo
  first, then undo).

**Worked (do it):**
> Log: `⟨T1,COMMIT⟩`, `⟨CHECKPOINT⟩`, `⟨T2,start⟩`, `⟨T2,A,10,20⟩`, `⟨T2,COMMIT⟩`,
> `⟨T3,start⟩`, `⟨T3,B,5,9⟩`, then **CRASH**.
> → T1 committed **before** the checkpoint → **nothing**. **REDO T2** (committed
> after the checkpoint). **UNDO T3** (active at crash → set B back to 5). ✔

**More (new subsections):**
18. A fuzzy checkpoint writes which two records around normal processing? →
    **⟨BEGIN-CHECKPOINT⟩ and ⟨END-CHECKPOINT⟩**.
19. Deferred update logs which value(s)? → **new only**. Immediate update? →
    **old and new**.
20. Same crash: an uncommitted write under **deferred** update needs → **nothing**;
    under **immediate** update needs → **UNDO**.
21. In ARIES, Redo starts at the ___ , not the checkpoint LSN → **RedoLSN (min
    recLSN in the DPT)**.
22. The Undo phase follows which back-pointer to walk a loser's changes? →
    **prevLSN**.
23. During Redo, a log record is skipped when → **pageLSN ≥ LSN** (already applied).

**Worked (do it) — ARIES tables:**
> Log (LSNs): `10 ⟨T1,start⟩; 20 ⟨T1,P,..⟩; 30 ⟨CKPT⟩; 40 ⟨T2,start⟩; 50 ⟨T2,Q,..⟩;
> 60 ⟨T2,COMMIT⟩; 70 ⟨T3,start⟩; 80 ⟨T3,P,..⟩;` CRASH.
> → DPT: `P(recLSN 20), Q(recLSN 50)` → **RedoLSN = 20**. Losers = **{T3}** (active).
> Redo replays 20..80 (incl. T3); Undo rolls back **T3** via prevLSN, logging CLRs. ✔

---

## 10.14 One-Page Revision Sheet

```
WHY: crashes break A (atomicity) + D (durability). recovery = UNDO uncommitted + REDO committed, via LOG.
FAILURES: transaction (abort) | system crash (RAM lost, disk ok) | media (disk lost -> need backup).
STORAGE: volatile (RAM) | non-volatile (disk) | stable (replicated, 'never' fails).

LOG record = <Ti,X,old,new> (+ start/commit/abort). buffered in RAM (log buffer), force-written/fsync to STABLE storage.
WAL (write-ahead logging):
  1) log record on stable storage BEFORE its data page hits disk (-> can UNDO).
  2) all log records (incl COMMIT) stable BEFORE commit reported (force-log-at-commit -> durability, fsync-bound latency).

UPDATE STRATEGY:
  DEFERRED  = NO-UNDO/REDO : write to DB only after commit. uncommitted -> nothing; committed -> REDO.
  IMMEDIATE = UNDO/REDO    : may write before commit. uncommitted -> UNDO; committed -> REDO.
BUFFER POLICY:
  STEAL -> need UNDO ; NO-STEAL -> no undo. FORCE -> no REDO ; NO-FORCE -> need REDO.
  real DBs = STEAL + NO-FORCE (need BOTH undo & redo; best performance).

RECOVERY: REDO committed-after-checkpoint ; UNDO active-at-crash ; before-ckpt-commit = nothing.
CHECKPOINT: flush log + dirty pages + write <CKPT>. recovery scans back only to last checkpoint.

ARIES (LSN per log rec; pageLSN per page; prevLSN back-pointer per record):
  1) ANALYSIS: rebuild Dirty Page Table (recLSN/page; min recLSN = RedoLSN start) + Transaction Table (lastLSN/txn); find losers.
  2) REDO: from RedoLSN, repeat history (redo ALL changes incl losers) -> exact pre-crash state.
  3) UNDO: roll back losers backward via prevLSN chain, write CLRs (idempotent, restart-safe).

SHADOW PAGING: current + shadow page tables; write=new page; commit=swap pointer; crash=revert. no log/undo/redo.
  BUT copying + fragmentation + poor concurrency -> rarely used.

BACKUP: FULL (whole DB) | INCREMENTAL (since last ANY backup; slow chained restore) |
  DIFFERENTIAL (since last FULL; restore = full + latest diff). media recovery = restore + roll forward via log.
```

### Flash cards

| Front | Back |
|-------|------|
| Recovery guarantees which ACID? | Atomicity & Durability |
| WAL rule 1? | Log record before data page on disk |
| WAL rule 2? | All log (incl commit) stable before commit reported |
| Deferred update = ? | NO-UNDO / REDO |
| Immediate update = ? | UNDO / REDO |
| STEAL needs? | UNDO |
| NO-FORCE needs? | REDO |
| Real-DB buffer policy? | STEAL + NO-FORCE |
| Committed txns on crash? | REDO |
| Active txns on crash? | UNDO |
| ARIES phases? | Analysis, Redo, Undo |
| ARIES redo scope? | Repeat history (incl losers) |
| CLR purpose? | Idempotent, restart-safe undo |
| Two-page-table recovery? | Shadow paging |
| Differential backup base? | Last full backup |
| RedoLSN comes from? | Smallest recLSN in Dirty Page Table |
| When is a log record durable? | After force-write (fsync) to stable storage |

### Spaced repetition
- **24-hour:** from a sample log + checkpoint, list the undo and redo sets; redo MCQs.
- **7-day:** explain WAL's two rules and the STEAL/FORCE matrix from memory.
- **30-day:** walk through ARIES's three phases on a log; compare shadow paging vs WAL; pick a backup strategy.

---

## 10.15 Summary

Recovery delivers ACID's **atomicity** and **durability** across crashes. The
**log** on **stable** storage records every change as `⟨Ti, X, old, new⟩`, and
**Write-Ahead Logging** enforces two rules — **log before data**, and **all log
(incl. commit) stable before reporting commit** — so we can always **UNDO**
uncommitted and **REDO** committed work. Update strategy splits into **deferred**
(NO-UNDO/REDO) and **immediate** (UNDO/REDO), determined by the **STEAL/NO-FORCE**
buffer policies (real DBs use STEAL+NO-FORCE → need both). **Checkpoints** bound
recovery to the log since the last checkpoint. **ARIES** — **Analysis → Redo
(repeat history) → Undo (with CLRs)**, driven by **LSNs** — is the industry
standard and **idempotent**. **Shadow paging** avoids logs but lost on performance.
Finally, **backups** (full / incremental / differential) plus log roll-forward
recover from **media** failure.

That completes the **internals** half of the syllabus. **Module 11 — Distributed,
NoSQL & Modern Databases** zooms out to data **across many machines**: the **CAP
theorem**, replication & partitioning (sharding), the **NoSQL** families, and how
the ACID guarantees of Modules 9–10 relax into **BASE** at scale.

> **You have mastered this module when** you can: state the two WAL rules; classify
> deferred vs immediate and map STEAL/FORCE to undo/redo; produce the undo and redo
> sets from a log with a checkpoint; walk ARIES's three phases and explain CLRs;
> and distinguish full/incremental/differential backups — all without notes.
