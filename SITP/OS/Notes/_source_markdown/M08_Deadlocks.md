---
title: "Module 8 — Deadlocks"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8 — Deadlocks

> **Where this module sits.**
> Module 7 gave us locks and semaphores to *coordinate* concurrent processes.
> This module studies what happens when that coordination **jams permanently**: a
> set of processes each holds a resource and waits for one another in a circle, so
> **none can ever proceed**. We build the whole theory — the **four Coffman
> conditions** that must *all* hold for deadlock, the **Resource-Allocation Graph**
> that lets you *see* it, and the four grand strategies (**prevention, avoidance,
> detection, recovery**) — anchored by the single most-asked numerical in the
> subject, the **Banker's Algorithm**. GATE and the banking IT exams love this
> module; it is a direct continuation of the Dining Philosophers deadlock from M7.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** definition of deadlock;
the **four Coffman conditions** (mutual exclusion, hold-and-wait, no preemption,
circular wait); **Resource-Allocation Graph** — cycle rules for **single vs
multiple** instances; the four **strategies** (prevention/avoidance/detection/
recovery); **Banker's Algorithm** (safe state, safe sequence, request check — a
guaranteed numerical); **wait-for graph** detection; **starvation vs deadlock**;
the **ostrich algorithm**.

---

## 8.1 What Is a Deadlock? (first principles)

A **deadlock** is a situation where a set of processes are each **blocked
forever**, because each holds a resource the next one needs and waits for a
resource the previous one holds — a **circular wait** with no escape.

> **Everyday analogy — the one-lane bridge / gridlock:** four cars enter a
> four-way intersection at once; each has advanced just enough to block the car to
> its right and is itself blocked by the car to its left. Nobody can move, and
> nobody will move without an outside intervention. That is a deadlock.

> **Memory hook:** deadlock = **"I'm waiting for you, you're waiting for me,
> forever."** No amount of *waiting* fixes it — that's what separates it from a
> temporary delay. Something external (kill, preempt, rollback) must break it.

A **resource** here is anything a process must hold exclusively for a while: a
lock/semaphore, a printer, a tape drive, a database record, memory, a file. A
resource type may have **one** instance (a specific printer) or **several
identical** instances (say, 3 equivalent tape drives).

**Deadlock vs a livelock vs starvation** (don't confuse them):

- **Deadlock:** processes are **blocked** (not running) and **stuck permanently**.
- **Livelock:** processes are **running** and keep changing state in response to
  each other but make **no progress** (two people stepping side-to-side in a
  corridor). CPU is busy; work isn't done.
- **Starvation:** a process waits **indefinitely** because others are
  *continuously* favoured (e.g. low priority under SJF) — but it *could* run if the
  favouritism stopped.

### MCQs

1. Deadlock in one line? → processes each **hold** a resource and **wait** for one
   held by another, forever (**circular wait**).
2. Deadlock vs livelock? → deadlock processes are **blocked**; livelock processes
   are **running but not progressing**.
3. What breaks a deadlock? → an **external** action (kill/preempt/rollback), never
   more waiting.

---

## 8.2 The Four Coffman Conditions (necessary conditions)

A deadlock can occur **only if all four** of these hold **simultaneously**. Break
**any one** and deadlock is impossible — this is the entire basis of prevention
(§8.5). Memorise them (Coffman, 1971):

1. **Mutual Exclusion.** At least one resource is held in a **non-shareable** mode
   — only one process can use it at a time. (Read-only/shareable resources never
   cause deadlock.)
2. **Hold and Wait.** A process is **holding at least one** resource while
   **waiting to acquire** additional resources held by others.
3. **No Preemption.** A resource **cannot be forcibly taken** from a process; it is
   released **only voluntarily**, after the process finishes with it.
4. **Circular Wait.** There exists a **cycle** of processes
   `P0 → P1 → P2 → … → Pn → P0` where each `Pi` waits for a resource held by
   `P(i+1)` (and `Pn` waits for one held by `P0`).

> **Memory hook — "MHNC" → "Must Have No Cycle" / mnemonic *"My Hungry Nephew
> Cries"*:** **M**utual exclusion, **H**old-and-wait, **N**o preemption, **C**ircular
> wait. All four are **necessary**; together they are **sufficient** when resources
> have single instances.

> **Key subtlety (exam trap):** circular wait implies hold-and-wait, so the four are
> **not independent**. But treat them separately, because **each gives a different
> way to prevent** deadlock.

### MCQs

1. How many Coffman conditions and must how many hold? → **four**, and **all four**
   simultaneously.
2. Name them. → **mutual exclusion, hold-and-wait, no preemption, circular wait**.
3. Which condition is a *cycle* of waiting? → **circular wait**.
4. A read-only shared resource violates which condition (so is deadlock-safe)? →
   **mutual exclusion**.

---

## 8.3 Resource-Allocation Graph (RAG)

The **RAG** is a directed graph that lets you *see* who holds and who wants what:

- **Vertices:** processes drawn as **circles** `P`; resource **types** drawn as
  **boxes** `R`, with one **dot** per instance inside.
- **Request edge** `Pi → Rj`: process `Pi` has **requested** (is waiting for) a
  unit of `Rj`.
- **Assignment edge** `Rj → Pi`: a unit of `Rj` has been **allocated** to `Pi`
  (drawn from a dot to the process).

![A resource-allocation graph with two single-instance resources: P1 holds R1 and requests R2, while P2 holds R2 and requests R1, forming a cycle that means deadlock.](images/75_rag_deadlock.png)

### The cycle rules (the high-yield part)

- **Single instance per resource type:** a **cycle** in the RAG is **necessary AND
  sufficient** → **cycle ⇔ deadlock**. (In the figure, `P1 → R2 → P2 → R1 → P1` is
  a cycle, so both are deadlocked.)
- **Multiple instances per resource type:** a **cycle is necessary but NOT
  sufficient**. A cycle *may or may not* mean deadlock — you must analyse further
  (e.g. with the detection algorithm of §8.7). **No cycle ⇒ no deadlock**, always.

> **Memory hook:** **"cycle = deadlock" only when every resource is a single
> instance.** With multiple instances, a cycle is a *warning sign*, not a verdict —
> another instance might free up and let the cycle drain.

> **Why multi-instance cycles can be safe:** if a resource type has 2 units and the
> cycle passes through it, a *third* process outside the cycle may release a unit,
> satisfying one waiter and breaking the cycle. So you must check whether **any**
> process can finish.

### MCQs

1. Circle vs box in a RAG? → **circle = process**, **box = resource type**.
2. `Rj → Pi` edge means? → a unit of `Rj` is **allocated** to `Pi` (assignment).
3. Cycle in a **single-instance** RAG means? → **deadlock** (necessary &
   sufficient).
4. Cycle in a **multi-instance** RAG means? → **maybe** deadlock (necessary, not
   sufficient).
5. **No** cycle means? → **no deadlock** (always).

---

## 8.4 The Four Strategies — a map

There are exactly four ways to deal with deadlock. Know the one-liners and the
trade-off (from strictest to most relaxed):

| Strategy | Idea | When resources are given | Cost |
|----------|------|--------------------------|------|
| **Prevention** | make one Coffman condition **impossible** by design | structurally restricted | low concurrency / wasted resources |
| **Avoidance** | grant a request **only if** the system stays in a **safe state** | dynamically, after a safety check | needs **max claims** known in advance (Banker's) |
| **Detection + recovery** | **allow** deadlock, find it, then fix it | freely | periodic detection + recovery pain |
| **Ignore (ostrich)** | pretend it never happens | freely | rare deadlock → reboot |

> **Memory hook:** **Prevention** = *"design it out."* **Avoidance** = *"look
> before you leap"* (Banker's). **Detection/recovery** = *"let it happen, then clean
> up."* **Ostrich** = *"head in the sand."*

The next sections take each in turn.

### MCQs

1. Which strategy needs **maximum demand known ahead**? → **avoidance** (Banker's).
2. Which strategy **lets** deadlock happen then fixes it? → **detection + recovery**.
3. What is the "do nothing" approach called? → the **ostrich algorithm**.

---

## 8.5 Strategy 1 — Deadlock **Prevention**

Prevention **negates one of the four Coffman conditions** so deadlock is
structurally impossible. Attack each:

| Condition to break | How to prevent | Downside |
|--------------------|----------------|----------|
| **Mutual exclusion** | make resources **shareable** (e.g. read-only files, or **spool** a printer) | many resources are *intrinsically* non-shareable |
| **Hold and wait** | require a process to request **all resources at once** (before starting), or **release all** before requesting more | **low utilisation** (resources held but idle); possible **starvation** |
| **No preemption** | if a process holding resources requests more and can't get them, **preempt** (take back) what it holds | only works for state you can **save/restore** (CPU, memory — not a printer mid-print) |
| **Circular wait** | impose a **total ordering** on resource types; each process requests **in increasing order** only | must **number** all resources; can be restrictive |

- **Breaking circular wait** with a global lock ordering is the **most practical**
  prevention technique in real software (always acquire locks in the same order →
  no cycle can form). This is the same idea as the "grab lower-numbered fork first"
  fix for Dining Philosophers (M7).

> **Memory hook:** prevention = **"remove one leg of the four-legged table and it
> can't stand."** The cheapest leg to remove in code is **circular wait** (order
> your locks).

### MCQs

1. Prevent circular wait by? → a **total ordering** of resources (request in
   increasing order).
2. "Request all resources up front" attacks which condition? → **hold-and-wait**.
3. Which condition is hardest to remove for physical devices? → **mutual
   exclusion** / **no preemption**.

---

## 8.6 Strategy 2 — Deadlock **Avoidance** & the Banker's Algorithm

Prevention is blunt (it wastes resources). **Avoidance** is smarter: allow the four
conditions, but before granting **each** resource request, check that doing so
leaves the system in a **safe state**. If not, the process **waits** even though the
resource is free.

### Safe state, unsafe state, deadlock

- A **safe state** is one where a **safe sequence** exists: an ordering
  `⟨P1, P2, …, Pn⟩` such that each `Pi`'s remaining needs can be met by the
  currently available resources **plus** what all processes *before* it release. If
  such a sequence exists, everyone can finish → **no deadlock possible**.
- An **unsafe state** *may* lead to deadlock (not guaranteed, but the system can no
  longer *guarantee* safety). **Deadlock ⊆ unsafe ⊆ all states.**

![Nested regions: the deadlock set sits inside the unsafe set, which sits inside all states; the Banker's algorithm keeps the system inside the outer safe region.](images/77_safe_unsafe_deadlock.png)

> **Memory hook:** **safe = "I can prove everyone finishes."** Unsafe isn't
> necessarily deadlocked, but the OS refuses to risk it — the Banker's algorithm
> **never lets you step out of the safe region.**

### The Banker's Algorithm (Dijkstra)

Like a banker who only lends cash if he can still satisfy *all* customers' credit
lines, the OS grants a request only if a **safe sequence** still exists afterwards.
Data structures for **n processes** and **m resource types**:

```text
Available[m]        : units of each resource currently free
Max[n][m]           : max demand each process may ever request
Allocation[n][m]    : units currently held by each process
Need[n][m]          : still required = Max - Allocation
```

**The Safety Algorithm** (is the current state safe?):

```text
1. Work = Available ;  Finish[i] = false for all i
2. Find an i with  Finish[i] == false  AND  Need[i] <= Work   (component-wise)
   - if none exists, go to 4
3. Work = Work + Allocation[i] ;  Finish[i] = true ;  go to 2
4. If Finish[i] == true for ALL i  -> SAFE (the order you picked = safe sequence)
   else                            -> UNSAFE
```

### Worked example — is the state safe? (do this by hand)

**5 processes** (P0–P4), **3 resource types** A, B, C with totals **A=10, B=5,
C=7**.

```text
        Allocation      Max          Need = Max - Allocation
        A  B  C       A  B  C            A  B  C
P0      0  1  0       7  5  3            7  4  3
P1      2  0  0       3  2  2            1  2  2
P2      3  0  2       9  0  2            6  0  0
P3      2  1  1       2  2  2            0  1  1
P4      0  0  2       4  3  3            4  3  1
```

**Available** = Total − Σ Allocation = (10,5,7) − (7,2,5) = **(3, 3, 2)**.

Now run the safety algorithm with `Work = (3,3,2)`:

```text
step  Work        try            Need<=Work?   Work += Allocation      Finish
----  ---------   ------------   -----------   ---------------------   -------------
init  (3,3,2)
 1    (3,3,2)     P1 (1,2,2)     yes           +(2,0,0) = (5,3,2)      P1
 2    (5,3,2)     P3 (0,1,1)     yes           +(2,1,1) = (7,4,3)      P3
 3    (7,4,3)     P4 (4,3,1)     yes           +(0,0,2) = (7,4,5)      P4
 4    (7,4,5)     P0 (7,4,3)     yes           +(0,1,0) = (7,5,5)      P0
 5    (7,5,5)     P2 (6,0,0)     yes           +(3,0,2) = (10,5,7)     P2
```

All five finished → **the state is SAFE**, with safe sequence
**⟨P1, P3, P4, P0, P2⟩**. (Other valid sequences exist, e.g. ⟨P1, P3, P0, P2, P4⟩ —
any order the algorithm can complete counts.)

### The Resource-Request Algorithm — should we grant a request?

Now suppose **P1 requests (1, 0, 2)**. Steps:

```text
1. Is Request <= Need[P1]?       (1,0,2) <= (1,2,2)  -> YES  (else error: over max)
2. Is Request <= Available?      (1,0,2) <= (3,3,2)  -> YES  (else P1 must wait)
3. PRETEND to grant it:
     Available   = (3,3,2) - (1,0,2) = (2,3,0)
     Alloc[P1]   = (2,0,0) + (1,0,2) = (3,0,2)
     Need[P1]    = (1,2,2) - (1,0,2) = (0,2,0)
4. Run the SAFETY algorithm on this new state. Safe -> GRANT ; unsafe -> DENY & roll back.
```

Run safety with `Work = (2,3,0)`:

```text
P1 Need (0,2,0) <= (2,3,0)? yes -> Work = (2,3,0)+(3,0,2) = (5,3,2)
P3 Need (0,1,1) <= (5,3,2)? yes -> Work = (5,3,2)+(2,1,1) = (7,4,3)
P4 Need (4,3,1) <= (7,4,3)? yes -> Work = (7,4,3)+(0,0,2) = (7,4,5)
P0 Need (7,4,3) <= (7,4,5)? yes -> Work = (7,4,5)+(0,1,0) = (7,5,5)
P2 Need (6,0,0) <= (7,5,5)? yes -> Work = (7,5,5)+(3,0,2) = (10,5,7)
```

All finish → the new state is **safe** → **the request is GRANTED**. Safe sequence
after granting: **⟨P1, P3, P4, P0, P2⟩**.

> **Exam contrast:** if instead **P4 requested (3,3,0)**, then `Available` would drop
> to `(0,0,2)` and **no process's Need** fits in `(0,0,2)` (P3 needs `(0,1,1)` — the
> B is 0), so the safety check **fails** → that request is **denied** even though the
> resources are physically free. That's avoidance in action.

> **Memory hook — "the Banker only lends if he can still pay everyone":** compute
> **Need = Max − Allocation**, start `Work = Available`, and repeatedly "fund"
> whichever process fits and **collect back** its Allocation. If you can fund
> everyone, it's **safe**.

### MCQs

1. `Need` = ? → **Max − Allocation**.
2. Available in the example? → **(3,3,2)**.
3. A safe sequence for the base example? → **⟨P1,P3,P4,P0,P2⟩** (among others).
4. First test in the request algorithm? → `Request ≤ Need` (else it exceeds max).
5. If the pretend-grant state is unsafe? → **deny** and roll back (process waits).

---

## 8.7 Strategy 3 — Deadlock **Detection**

If we neither prevent nor avoid, we must **detect** deadlock after it happens and
then recover. Detection differs by instance count:

### Single instance per type — the Wait-For Graph (WFG)

Collapse the RAG by removing resource nodes: draw an edge `Pi → Pj` iff `Pi` is
waiting for a resource currently held by `Pj`. A **cycle in the WFG ⇔ deadlock**.
Detect by periodically searching for a cycle.

![A wait-for graph where P1 waits for P2, P2 for P3, P3 for P4, and P4 for P1 — a cycle, so all four are deadlocked.](images/76_wait_for_graph.png)

### Multiple instances — the detection algorithm

Almost identical to the Banker's safety algorithm, but it uses the **current
`Request`** matrix (what each process is *actually* asking for now) instead of
`Need` (the *maximum* it might ask):

```text
1. Work = Available
   Finish[i] = (Allocation[i] == 0) ? true : false     // idle procs are "done"
2. Find i with Finish[i]==false AND Request[i] <= Work
   - if none, go to 4
3. Work = Work + Allocation[i] ; Finish[i] = true ; go to 2
4. Any Finish[i] == false  ->  those processes are DEADLOCKED
```

> **Banker vs detection — the one-line difference (favourite exam point):**
> avoidance uses **`Need` (max future claim)** *before* granting to stay safe;
> detection uses **`Request` (current ask)** *after the fact* to find who's stuck.

**When to run detection?** Every request (expensive, catches it instantly), or
periodically / when CPU utilisation drops (cheaper). More frequent = faster
recovery but more overhead.

### MCQs

1. WFG cycle means (single instance)? → **deadlock**.
2. Detection algorithm uses which matrix (vs Banker's `Need`)? → **`Request`
   (current)**.
3. How is the WFG built from a RAG? → remove resources; `Pi→Pj` if `Pi` waits for a
   resource **held by** `Pj`.

---

## 8.8 Strategy 4 — Deadlock **Recovery**

Once detected, break the deadlock. Two families:

**(a) Process termination**

- **Abort all** deadlocked processes — simple, drastic, loses all their work.
- **Abort one at a time** until the cycle breaks — re-run detection after each kill.
  Choose the **victim** to minimise cost: lowest priority, least work done so far,
  fewest resources held, most restartable.

**(b) Resource preemption**

- **Preempt** resources from some process and give them to others. Three issues:
  1. **Victim selection** — minimise cost (as above).
  2. **Rollback** — the preempted process must be rolled back to a **safe
     checkpoint** and restarted (you can't just yank a half-written resource).
  3. **Starvation** — the same process may repeatedly be the victim; include the
     **number of rollbacks** in the cost so it eventually makes progress.

> **Memory hook:** recover by **killing (abort a victim)** or **stealing
> (preempt + rollback)** — either way you pick the **cheapest victim** and guard
> against making it the victim **every** time (starvation).

### MCQs

1. Two recovery approaches? → **kill processes** or **preempt resources**.
2. What must accompany preemption? → **rollback** to a safe checkpoint.
3. A risk of repeatedly picking the same victim? → **starvation** (count rollbacks
   in the cost).

---

## 8.9 The Ostrich Algorithm & Starvation vs Deadlock

- **Ostrich algorithm** — *stick your head in the sand and pretend deadlocks don't
  happen.* Used by **most general-purpose OSes (UNIX, Linux, Windows)** for kernel
  resources, because deadlock is **rare**, and prevention/avoidance cost too much
  performance for everyday use. If one occurs, the user **reboots / kills** the
  process. It's an **engineering trade-off**, not laziness: cheap-common-case beats
  expensive-always-safe.

- **Starvation vs deadlock (must not confuse):**

| | **Deadlock** | **Starvation** |
|---|---|---|
| State | processes **blocked** forever | a process **waits** indefinitely |
| Cause | **circular wait** (mutual blocking) | continuous **favouritism** (e.g. priority, SJF) |
| Others progressing? | **no** (all in the cycle are stuck) | **yes** — others keep running ahead of it |
| Could it ever run? | **never** (without intervention) | **yes**, if the bias stopped |

> **Memory hook:** **deadlock = a knot** (nobody moves); **starvation = the end of
> a never-shrinking queue** (others keep cutting ahead, but the line *is* moving).
> Every deadlock is a permanent block; not every permanent wait is a deadlock.

### MCQs

1. OS that "ignores" deadlock uses the? → **ostrich algorithm**.
2. Why do Linux/Windows ignore many deadlocks? → they're **rare**; prevention costs
   more than the occasional reboot.
3. In deadlock, are other processes progressing? → **no**; in starvation? → **yes**.

---

## 8.10 Real-World & Backend Perspectives

- **Databases** are where you meet deadlock daily: two transactions each lock a row
  the other needs. DBMSs run **deadlock detection** (a wait-for graph) and
  **abort + roll back the cheapest victim** transaction (you then retry) — that is
  literally §8.7 + §8.8. PostgreSQL, MySQL/InnoDB, and SQL Server all do this.
- **Lock ordering** is the standard *prevention* discipline in application code:
  always acquire locks in a **fixed global order** (negates circular wait). Tools
  like Java's thread-dump / `jstack` and Go's race detector help find violations.
- **`SELECT ... FOR UPDATE`** and long transactions are classic deadlock breeders;
  keeping transactions short and touching rows in a consistent order avoids them.
- **Banker's Algorithm is rarely used in practice** — it needs every process's
  *maximum* claim in advance, which real systems don't know. It's a beautiful exam
  tool and the intellectual root of avoidance, but detection+recovery (DBs) and
  prevention-by-lock-ordering (apps) dominate real systems.
- **Distributed systems** face distributed deadlock (locks across machines);
  detection is harder, so timeouts + retries are common.

---

## 8.11 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Saying a **cycle always means deadlock** — true **only** for **single-instance**
  resources; with multiple instances a cycle is *necessary but not sufficient*.
- Confusing **unsafe** with **deadlocked** — unsafe *may* lead to deadlock; it is
  **not** deadlock yet.
- Forgetting **`Need = Max − Allocation`**, or comparing `Request > Need`.
- In detection, using `Need` instead of the **current `Request`** matrix.
- Mixing up **starvation** (others progress) with **deadlock** (nobody progresses).
- Thinking **avoidance** can run without knowing **maximum claims** — it can't.

**Edge cases**
- A resource that is **shareable/read-only** can't cause deadlock (breaks mutual
  exclusion).
- A safe state can still contain a **cycle** if resources have multiple instances —
  as long as a safe sequence exists.
- Preemption-based recovery needs **checkpointing**; not all resources can be rolled
  back (a printer mid-page cannot).

**Tradeoffs**

| Strategy | Pro | Con |
|----------|-----|-----|
| Prevention | deadlock impossible by design | low utilisation / restrictive |
| Avoidance (Banker's) | no deadlock, better utilisation than prevention | needs max claims; overhead per request |
| Detection + recovery | full concurrency | recovery is costly (kills/rollbacks) |
| Ostrich | zero overhead | rare deadlock → hang/reboot |

---

## 8.12 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** the **four conditions** (name + how to break each);
**RAG cycle rules** for single vs multiple instances; a **full Banker's** numerical
(compute Need, Available, find a safe sequence, test a request); **WFG detection**;
**starvation vs deadlock**; the **ostrich** one-liner. Banker's is *the* set-piece
numerical — practise until it's mechanical.

**Interview:** "What is a deadlock and what are the conditions for it?"; "How would
you prevent deadlock in your service?" (**lock ordering**); "How do databases handle
deadlock?" (detect + roll back victim); "Difference between deadlock and
starvation?".

**Coding/practical:**
- Reproduce a deadlock: two threads take mutex A then B vs B then A. Fix by
  **consistent lock ordering**.
- In PostgreSQL, trigger a deadlock with two interleaved `UPDATE`s in transactions;
  observe `deadlock detected` and the automatic victim rollback.

---

## 8.13 Concept Checks & MCQs (test yourself)

1. Define deadlock. → processes each **hold** a resource and **wait** in a circle,
   forever.
2. The four Coffman conditions? → **mutual exclusion, hold-and-wait, no preemption,
   circular wait**.
3. How many must hold for deadlock? → **all four**.
4. RAG: circle vs box? → **process** vs **resource type**.
5. Cycle in single-instance RAG? → **deadlock** (necessary & sufficient).
6. Cycle in multi-instance RAG? → **maybe** (necessary, not sufficient).
7. No cycle in a RAG? → **no deadlock**.
8. The four strategies? → **prevention, avoidance, detection, recovery** (+ ostrich).
9. Which breaks circular wait? → **total ordering** of resource requests.
10. "Request all up front" breaks? → **hold-and-wait**.
11. Making resources shareable breaks? → **mutual exclusion**.
12. Avoidance needs to know? → each process's **maximum** claim.
13. `Need` = ? → **Max − Allocation**.
14. Safe state definition? → a **safe sequence** exists (all can finish).
15. Deadlock ⊆ ___ ⊆ all states? → **unsafe**.
16. Banker's: first check on a request? → `Request ≤ Need`.
17. Detection uses which matrix vs Banker's Need? → current **`Request`**.
18. Single-instance detection tool? → **wait-for graph** (cycle = deadlock).
19. Two recovery methods? → **kill processes** / **preempt + rollback**.
20. Risk of preemption recovery? → **starvation** (same victim repeatedly).
21. OS "ignore deadlock" approach? → **ostrich algorithm**.
22. Deadlock vs starvation — others progressing? → deadlock **no**, starvation
    **yes**.

**True/False**
- A cycle always means deadlock. → **False** (only for single instances).
- An unsafe state is always deadlocked. → **False** (may lead to deadlock).
- Banker's algorithm can run without maximum claims. → **False**.
- The detection algorithm uses `Need`. → **False** (uses current `Request`).
- Read-only shared resources can cause deadlock. → **False** (no mutual exclusion).
- Linux uses Banker's algorithm for kernel resources. → **False** (ostrich).

**Numerical (do it):** Totals A=10,B=5,C=7; the matrices of §8.6. (a) Available? →
**(3,3,2)**. (b) A safe sequence? → **⟨P1,P3,P4,P0,P2⟩**. (c) Grant P1's request
(1,0,2)? → **yes** (resulting state is safe).

---

## 8.14 One-Page Revision Sheet

```
DEADLOCK = processes each HOLD a resource + WAIT for another in a CIRCLE, forever.
  vs LIVELOCK (running, no progress) vs STARVATION (waits while others progress).

FOUR COFFMAN CONDITIONS (all must hold)  -> "My Hungry Nephew Cries":
  1 MUTUAL EXCLUSION  (non-shareable)
  2 HOLD AND WAIT     (hold some, wait for more)
  3 NO PREEMPTION     (can't force-take)
  4 CIRCULAR WAIT     (P0->P1->...->P0 cycle)
  Break ANY ONE -> no deadlock.

RAG: circle=process, box=resource(dots=instances). request Pi->Rj ; assign Rj->Pi.
  SINGLE instance: cycle <=> DEADLOCK.   MULTI instance: cycle = necessary, NOT sufficient.
  NO cycle => NO deadlock (always).

STRATEGIES:
  PREVENTION  negate a condition: shareable(ME) / request-all-up-front(H&W) /
              preempt(no-preempt) / TOTAL ORDER of locks(circular wait <- most practical).
  AVOIDANCE   grant only if SAFE STATE remains. Needs MAX claims. BANKER'S ALGORITHM.
  DETECTION   allow it; WFG cycle (single) or detection algo w/ current REQUEST (multi).
  RECOVERY    kill victim (cheapest) or preempt+ROLLBACK (watch starvation).
  OSTRICH     ignore it (Linux/Windows) - rare, cheap.

BANKER'S:  Need = Max - Allocation ;  Available = Total - sum(Allocation).
  SAFETY: Work=Available; repeatedly pick i with Need[i]<=Work, Work += Allocation[i], mark done.
          all done -> SAFE (order = safe sequence).
  REQUEST(P,req): (1) req<=Need? (2) req<=Available? (3) pretend-grant, (4) safety-check -> grant/deny.
  Example totals(10,5,7): Available=(3,3,2); safe seq <P1,P3,P4,P0,P2>; P1 req(1,0,2) -> GRANT.

SAFE (safe sequence exists) => no deadlock.  DEADLOCK ⊆ UNSAFE ⊆ ALL states.
DETECTION uses current REQUEST ; AVOIDANCE uses max NEED. (the classic distinction)
```

### Flash cards

| Front | Back |
|-------|------|
| Four Coffman conditions? | Mutual excl., hold-and-wait, no preemption, circular wait |
| Break which is most practical in code? | Circular wait (lock ordering) |
| Single-instance cycle means? | Deadlock (necessary & sufficient) |
| Multi-instance cycle means? | Maybe (necessary, not sufficient) |
| Need = ? | Max − Allocation |
| Safe state? | A safe sequence exists (all can finish) |
| Banker's needs to know? | Each process's maximum claim |
| Avoidance vs detection matrix? | Need (max) vs Request (current) |
| Recovery options? | Kill victim / preempt + rollback |
| Ignore-deadlock approach? | Ostrich algorithm |
| Deadlock vs starvation? | Blocked forever vs waits while others progress |

### Spaced repetition
- **24-hour:** recite the four conditions + how to break each; redo the Banker's
  safe-sequence computation for §8.6.
- **7-day:** draw a RAG and a WFG; state single vs multi-instance cycle rules; run
  the request-grant check for a new request.
- **30-day:** given matrices, compute Available/Need, find a safe sequence, and
  decide a request — plus explain prevention vs avoidance vs detection without
  notes.

---

## 8.15 Summary

A **deadlock** is a permanent circular wait: a set of processes each holding a
resource and blocked on one another so **none can ever proceed**. It can happen
**only when all four Coffman conditions hold** — **mutual exclusion, hold-and-wait,
no preemption, and circular wait** — which is exactly why breaking **any one**
prevents it. The **Resource-Allocation Graph** lets us see the danger: a **cycle
means deadlock** for **single-instance** resources, but is only a **warning** when
resources have multiple instances (no cycle ever means no deadlock). We surveyed
the four strategies — **prevention** (design a condition away; lock ordering kills
circular wait), **avoidance** (grant only if a **safe state** remains, via the
fully worked **Banker's Algorithm**: `Need = Max − Allocation`, find a safe
sequence, test each request), **detection** (a **wait-for graph** or a
Request-based algorithm) and **recovery** (kill a victim or preempt + rollback) —
plus the pragmatic **ostrich algorithm** that real OSes actually use. Finally we
separated **deadlock** (everyone blocked forever) from **starvation** (one waits
while others progress).

Together, Modules 7 and 8 complete the concurrency story: M7 showed how to
**coordinate** processes with locks, semaphores, and monitors; M8 showed how that
coordination can **jam** — and how to prevent, avoid, detect, and recover from it.
Next, **Module 9 — Memory Management** turns from *sharing time* to *sharing space*.

> **You have mastered this module when** you can: state the four conditions and how
> to break each; apply the single- vs multi-instance RAG cycle rules; run the
> **Banker's Algorithm** end to end (Need, Available, safe sequence, request check)
> without hesitation; explain WFG detection and the Need-vs-Request distinction;
> describe recovery by termination and preemption; and cleanly separate deadlock,
> livelock, and starvation — all without notes.
