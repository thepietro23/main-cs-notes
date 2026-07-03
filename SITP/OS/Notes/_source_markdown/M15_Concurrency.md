---
title: "Module 15 — Concurrency"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 15 — Concurrency

> **Where this module sits.**
> Module 7 introduced synchronization — mutexes, semaphores, the critical-section
> problem — as the *tools* that keep concurrent code correct. This module goes one
> level **deeper and lower**, to the layer beneath the locks: **what the hardware
> actually does when multiple cores touch the same memory.** We separate
> **concurrency from parallelism**, expose why **race conditions** and **memory
> visibility** bugs happen even on "simple" code, and then meet the primitives locks
> are *built from* — **atomic operations** (CAS, fetch-and-add), **memory ordering /
> barriers**, and finally **lock-free and wait-free** programming (the Treiber
> stack, the ABA problem, false sharing). This is the hardest, highest-signal topic
> for senior backend / systems / AI-infra interviews, and the foundation for the
> concurrent data structures inside every database, kernel, and runtime.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★      | ★★     | ★★★     | ★★★★★     | ★★★★★   |

**Most-asked PYQ / interview concepts:** concurrency **vs** parallelism; what a
**race condition** really is + **memory visibility** (why a flag loop hangs without
`volatile`/atomics); **atomic read-modify-write** (**CAS**, **fetch-and-add**); the
**ABA problem**; **memory ordering** (reordering, **barriers/fences**, **acquire /
release**, **sequential consistency**); **lock-free vs wait-free** and when
lock-free beats locks (and its dangers); **false sharing**.

---

## 15.1 Concurrency vs Parallelism (deeper than M5)

These two words are used interchangeably in casual speech and are *wrong* to conflate
in an interview.

- **Concurrency** is a **structuring** property: a program is concurrent if it has
  **multiple independent tasks in progress** that *may* overlap in time. It is about
  **dealing with many things at once** — even on a **single core** (the OS
  time-slices them, §M6).
- **Parallelism** is an **execution** property: **multiple tasks literally running at
  the same instant**, which requires **multiple cores/CPUs** (§M1 multiprocessing).
  It is about **doing many things at once**.

> **Memory hook (Rob Pike's line):** **"Concurrency is dealing with many things at
> once; parallelism is doing many things at once."** Concurrency is a way to
> *structure* a program; parallelism is a way to *run* it. You can have concurrency
> with **zero** parallelism (one core, many tasks), and you *achieve* parallelism by
> running concurrent tasks on many cores.

![Concurrency vs parallelism: on one core, tasks A and B are interleaved over time (concurrent, not parallel); on two cores, A and B run simultaneously (parallel). Concurrency is a structure; parallelism is simultaneous execution needing multiple cores.](images/146_concurrency_vs_parallelism.png)

| | Concurrency | Parallelism |
|---|---|---|
| **What** | many tasks *in progress* | many tasks *executing at once* |
| **Needs** | 1+ core (interleaving is enough) | 2+ cores |
| **Goal** | responsiveness, structure | speedup / throughput |
| **Example** | a web server juggling 10k connections on 4 cores | multiply two matrices across 32 cores |

> **The trap:** adding cores gives **parallelism**, but only if your program is
> **concurrent** in a way that has independent work to run. And more concurrency on
> shared data means **more synchronization** — the subject of the rest of this
> module. (**Amdahl's law**, §M6: the serial fraction caps the speedup no matter how
> many cores you add.)

### MCQs

1. One core, many interleaved tasks — concurrency, parallelism, or both? →
   **concurrency** only.
2. What does parallelism require that concurrency doesn't? → **multiple cores/CPUs**.
3. "Dealing with many things at once" describes? → **concurrency** (doing = parallelism).

---

## 15.2 Race Conditions and Memory Visibility

### A race condition, precisely

A **race condition** exists when the **correctness of a program depends on the
relative timing/interleaving** of operations on **shared mutable state**. The classic
example is a non-atomic **increment**:

```text
Shared counter = 0. Two threads each do counter++ (which is really 3 steps):

  Thread A            Thread B
  read  counter (0)
                      read  counter (0)     <- both read 0
  add 1 -> 1
                      add 1 -> 1
  write counter (1)
                      write counter (1)     <- one increment LOST

Result = 1, but two increments happened. Correct answer was 2. This is a DATA RACE.
```

`counter++` is a **read-modify-write (RMW)**: three machine steps (load, add, store).
An interleaving between the load and the store loses updates. This is the same
critical-section problem from §M7 — but here we care about the **hardware-level**
reason it's non-atomic.

### Memory visibility — the subtler bug

Even without interleaving, a thread may **never see** another thread's write, because
of **caches** and **compiler optimizations**:

```text
bool done = false;    int data = 0;

Thread A (producer):        Thread B (consumer):
  data = 42;                  while (!done) { /* spin */ }
  done = true;               use(data);            // may see data == 0 !
```

Two things can break this:
1. **Compiler** may hoist `done` out of the loop (it "proves" `done` never changes in
   B's code) → B spins forever.
2. **CPU/cache**: A's writes may sit in A's **store buffer** / cache and reach B's
   core **out of order** or **late**, so B sees `done==true` but `data==0`.

> **Memory hook:** there are **two** concurrency demons, not one:
> **(1) atomicity** — updates stomping on each other (the counter);
> **(2) visibility & ordering** — one thread not seeing (or seeing reordered)
> another's writes (the flag). Locks fix **both**; atomics + memory ordering fix them
> at a finer grain. `volatile` in C/C++ fixes **neither** for threading (it is *not*
> a concurrency tool — a very common myth).

### MCQs

1. Why is `counter++` unsafe across threads? → it's a **read-modify-write** (3
   steps); interleaving loses updates (**data race**).
2. Name the two distinct concurrency problems. → **atomicity** and
   **visibility/ordering**.
3. Does C/C++ `volatile` make code thread-safe? → **No** (it's for memory-mapped I/O,
   not thread synchronization).

---

## 15.3 Atomic Operations — CAS and Fetch-and-Add

An **atomic operation** completes **indivisibly**: no other thread can observe it
half-done, and it can't be interleaved. The hardware provides a few **atomic
read-modify-write (RMW)** instructions that are the bedrock of *all* synchronization
— locks, semaphores, and lock-free structures are built on them.

### The workhorses

- **Test-and-set / Exchange (`XCHG`)** — atomically write a value and return the old
  one. Enough to build a **spinlock**.
- **Fetch-and-add (`XADD`)** — atomically `old = *p; *p += n; return old`. Perfect
  for **counters**, ticket locks, and sequence numbers — no lock needed:

```text
// Thread-safe counter with NO lock — one atomic instruction:
new_value = fetch_and_add(&counter, 1);   // atomic; no lost updates
```

- **Compare-and-swap (CAS)** — the **universal** primitive:

```text
CAS(addr, expected, new):        // all atomic, in hardware (x86: CMPXCHG)
    if *addr == expected:
        *addr = new
        return true              // success
    else:
        return false             // someone else changed it; retry
```

> **Memory hook:** **CAS = "change it *only if* nobody touched it since I looked."**
> It's the atomic version of "check the price tag, and buy only if it hasn't
> changed." Almost every lock-free algorithm is a **CAS in a retry loop**.

**The CAS retry loop** (how you do *any* atomic update, e.g. an atomic max):

```text
do {
    old = *addr;                 // read current value
    new = f(old);                // compute desired new value
} while (!CAS(addr, old, new));  // install it; retry if someone raced us
```

CAS is **universal** (Herlihy's result): with CAS you can build a wait-free version
of *any* concurrent object — test-and-set and fetch-and-add cannot. That's why every
language's atomics (`std::atomic`, `java.util.concurrent.atomic`, Go's `sync/atomic`)
expose CAS.

### MCQs

1. Which atomic primitive is **universal** (can build anything)? → **compare-and-swap
   (CAS)**.
2. Best atomic for a shared counter with no lock? → **fetch-and-add**.
3. What does CAS return/do on failure? → it **doesn't write**; returns false →
   **retry** with the new current value.
4. Locks and semaphores are ultimately built on? → **atomic RMW** instructions.

---

## 15.4 Memory Ordering and Memory Models

Even with atomics, there's a deeper problem: **the order you write instructions is
NOT the order they execute or become visible.** Compilers reorder for optimization;
CPUs reorder for pipelining and use per-core **store buffers** and caches. A **memory
model** is the contract stating **which reorderings are allowed** and how to stop
them.

### Reordering is real

On a weakly-ordered view, a core may make its stores visible to other cores **out of
program order**. The classic **Dekker/Store-Buffer** litmus test:

```text
Initially x = 0, y = 0.
Thread 1:  x = 1;  r1 = y;
Thread 2:  y = 1;  r2 = x;

Intuition says r1 and r2 can't BOTH be 0.
On real x86/ARM they CAN both be 0 — each store sits in a store buffer while the
load reads the other (still-zero) variable. This is store->load reordering.
```

### Barriers / fences

A **memory barrier (fence)** is an instruction that forbids reordering across it and
forces buffered writes to become visible. Types:

- **Full barrier** — no memory operation may move across it in either direction.
- **Acquire barrier** — later reads/writes can't move **before** it (used *after* a
  lock acquire / load).
- **Release barrier** — earlier reads/writes can't move **after** it (used *before* a
  lock release / store).

### Acquire–release — the practical model

Most real code uses **acquire/release** semantics, which give exactly the guarantee
you want cheaply:

- A **release** store **publishes**: everything the thread wrote *before* the release
  is visible to anyone who later does an **acquire** load of that same variable.
- An **acquire** load **subscribes**: after it sees the released value, it also sees
  all writes that happened before the release.

```text
Fixes the §15.2 flag bug:
  Thread A:  data = 42;
             store_release(&done, true);   // publishes data too
  Thread B:  if (load_acquire(&done))      // subscribes
                 use(data);                // now GUARANTEED to see 42
```

This is exactly what a **mutex** does: `unlock` is a **release**, `lock` is an
**acquire** — which is *why* everything you did inside the critical section is visible
to the next thread that takes the lock.

![Memory ordering: without a barrier, a producer's data write can be reordered after its flag write, so the consumer sees the flag set but stale data. A release store (producer) paired with an acquire load (consumer) forbids that reordering, so all writes before the release are visible after the acquire — this is the happens-before guarantee locks provide.](images/147_memory_ordering.png)

### Sequential consistency (SC) — the strongest, simplest model

**Sequential consistency** (Lamport): the program behaves **as if** all operations
from all threads ran in **some single global interleaving** that respects each
thread's program order. It's the intuitive "no weird reordering" model — easiest to
reason about but the **most expensive** (needs full barriers). `std::atomic`'s
**default** (`memory_order_seq_cst`) and Java `volatile` give SC for the atomic
variables. **Ordering strength ladder** (strong → weak):

```text
Sequential Consistency  (seq_cst)   strongest, simplest to reason, slowest
Acquire / Release       (acq/rel)   publish/subscribe pairs, cheaper, common
Relaxed                 (relaxed)    atomic value only, NO ordering  (counters/stats)
```

> **Memory hook:** **release = publish, acquire = subscribe.** A release store and a
> matching acquire load create a **happens-before** edge, so everything before the
> publish is seen after the subscribe. **seq_cst** = "one global order, no
> surprises" (safe default, slowest). **relaxed** = "atomic, but no ordering promises"
> (fine for a pure statistics counter, dangerous for flags).

### MCQs

1. Why can two threads' stores appear out of order? → CPU **store buffers** / caches
   + compiler/CPU **reordering**.
2. Instruction that forbids reordering & flushes writes? → a **memory barrier
   (fence)**.
3. Which pairing fixes the publish/see-stale-data bug? → **release** store +
   **acquire** load.
4. Strongest, most intuitive (and slowest) model? → **sequential consistency**.
5. A mutex `unlock`/`lock` act as which barriers? → **release** / **acquire**.

---

## 15.5 Lock-Free and Wait-Free Programming

Locks have real downsides: a thread holding a lock that gets **preempted** (§M6)
blocks *everyone* waiting; locks risk **deadlock**, **priority inversion**, and
**convoying**. **Non-blocking** algorithms avoid locks by using atomics (CAS) so that
**stopping one thread never blocks the whole system.**

### The hierarchy (progress guarantees)

| Property | Guarantee | Meaning |
|----------|-----------|---------|
| **Blocking (locks)** | none | a stalled lock-holder can stall everyone |
| **Lock-free** | **system-wide** progress | *some* thread always makes progress (individuals may retry forever) |
| **Wait-free** | **per-thread** progress | *every* thread finishes in a **bounded** number of steps (no starvation) |

> **Memory hook:** **lock-free = *someone* always makes progress; wait-free =
> *everyone* makes progress in bounded time.** Wait-free is strictly stronger (and
> much harder/rarer). Lock-free is the common practical target.

### The Treiber stack — the canonical lock-free structure

A **lock-free stack** (R. K. Treiber, 1986) is a singly-linked list where `push`/`pop`
just CAS the **head** pointer in a retry loop:

```text
push(v):
    n = new Node(v)
    do {
        old = head            // read current top
        n.next = old
    } while (!CAS(&head, old, n))   // install n as new head; retry on race

pop():
    do {
        old = head
        if old == null: return EMPTY
        next = old.next
    } while (!CAS(&head, old, next)) // move head past old; retry on race
    return old.value
```

No locks — concurrent pushers/poppers simply **retry** their CAS if another thread
won the race. Some thread always succeeds → **lock-free**.

![The Treiber lock-free stack: push allocates a node, points it at the current head, and CAS-swaps head to the new node; if another thread changed head first, the CAS fails and the operation retries. No locks — progress is guaranteed system-wide.](images/148_treiber_stack.png)

### The ABA problem — the classic trap

CAS checks **"is the value still what I read?"** — but a value can change **A → B →
A** between your read and your CAS. CAS sees "still A" and **wrongly succeeds**, even
though the world changed underneath it:

```text
1. Thread 1 reads head = A, plans CAS(&head, A, A.next).
2. Thread 1 is paused.
3. Thread 2 pops A, pops B, then pushes A back (reusing the freed node).
   head is A again, but A.next now points somewhere STALE/freed.
4. Thread 1 resumes: CAS(&head, A, A.next) SUCCEEDS (head is "still" A!) —
   and installs a dangling/old .next -> corruption.
```

> **Memory hook:** **ABA = "it looks unchanged, but it isn't."** CAS compares
> *values*, not *history*. Fixes:
> - **Tagged/versioned pointer** — pack a **counter** with the pointer; every change
>   bumps the counter, so A-with-tag-1 ≠ A-with-tag-3 (**double-width CAS**,
>   `CMPXCHG16B`). Most common fix.
> - **Hazard pointers** or **epoch-based reclamation** / GC — don't free/reuse a node
>   while another thread might still reference it (this is why ABA is easy to hit in
>   C/C++ manual memory and rarer under a garbage collector).

### False sharing — a silent performance killer

Even **independent** atomic variables are slow if they share a **cache line** (~**64
bytes**). CPUs keep caches coherent per **line**, so when core 1 writes variable `x`
and core 2 writes a *different* variable `y` on the **same line**, each write
**invalidates** the other core's copy — the line "ping-pongs" between cores. The
program is logically correct but crawls.

```text
struct Counters { long a; long b; };   // a and b on the SAME 64B cache line
  Core1 keeps updating a;  Core2 keeps updating b;
  -> every write invalidates the other core's cached line -> massive slowdown.

Fix: PAD/ALIGN each hot variable to its own cache line (e.g. alignas(64)),
     so a and b live on different lines and never invalidate each other.
```

> **Memory hook:** **false sharing = true contention on data you thought was
> separate.** No logical sharing, but the **cache line** is shared. Fix by **padding
> to 64 bytes** / cache-line alignment. A classic "why did adding a second thread
> make it *slower*?" interview answer.

### When lock-free beats locks — and its dangers

**Use lock-free when:**
- The critical section is **tiny** (a pointer/counter swap) — CAS is cheaper than
  taking a lock.
- You need **progress under preemption/failure** — a stalled thread mustn't block
  others (real-time, kernel, high-contention counters, ring buffers).
- **Interrupt/signal-context** code where blocking on a lock is forbidden.

**Dangers (why not everything is lock-free):**
- **Brutally hard to get right** — ABA, memory reclamation, and subtle **memory
  ordering** bugs; needs expert review and tools.
- **Not automatically faster** — under **high contention** the CAS **retry storm**
  can waste more CPU than a good lock; lock-free ≠ fast.
- **Livelock / starvation** — threads can retry forever (lock-free guarantees
  *system* progress, not *individual* progress).
- **Memory management** is the real monster in non-GC languages (when is it safe to
  free a node?).

> **Interview one-liner:** *"lock-free is about **progress guarantees**, not raw
> speed. Prefer a well-designed lock; reach for lock-free for tiny hot paths
> (counters, queues) or when a stalled thread must not block others — and budget for
> ABA and memory-ordering pain."*

### MCQs

1. Lock-free vs wait-free? → lock-free = **some** thread progresses; wait-free =
   **every** thread progresses in **bounded** steps.
2. Canonical lock-free structure using CAS on the head? → the **Treiber stack**.
3. What is the ABA problem? → a value goes **A→B→A**, so CAS wrongly succeeds
   (compares value, not history).
4. Two common ABA fixes? → **tagged/versioned pointers (double-width CAS)** and
   **hazard pointers / epoch reclamation / GC**.
5. Two threads updating different variables on the same 64B line → ? → **false
   sharing** (fix: pad/align to a cache line).
6. Is lock-free always faster than locks? → **No** — CAS retry storms under high
   contention can be slower.

---

## 15.6 Real-World & Backend Perspectives

- **Every high-performance system** uses these primitives: `java.util.concurrent`
  (`AtomicInteger`, `ConcurrentLinkedQueue` — a lock-free Michael-Scott queue), Go's
  `sync/atomic` and channels, C++ `std::atomic`, Rust's `Arc`/`Atomic*` (whose type
  system *forces* correct sharing).
- **Databases & kernels:** lock-free/wait-free queues and RCU (read-copy-update) in
  the Linux kernel let readers run with **zero locking**; the page-cache and
  scheduler use atomics heavily (§M14).
- **Metrics/counters:** high-throughput request counters use **fetch-and-add** (or
  **per-core sharded** counters to dodge **false sharing**) instead of a mutex.
- **Ring buffers:** lock-free single-producer/single-consumer ring buffers (LMAX
  Disruptor) power low-latency trading and logging — and they pad head/tail indices
  to separate cache lines to avoid false sharing.
- **AI infra (M19):** GPU host-side pipelines, lock-free work queues, and
  atomic reference counts on tensors all rely on exactly these ideas; a subtle
  memory-ordering bug shows up as a "sometimes-wrong" result under load.

---

## 15.7 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** using `volatile` for thread safety (C/C++). It gives **neither**
  atomicity nor ordering — use `std::atomic` / language atomics. (Java's `volatile`
  *does* give visibility/ordering — don't mix the two languages up.)
- **Mistake:** assuming "the code runs in the order I wrote it." Compilers and CPUs
  **reorder**; only barriers/atomics constrain it.
- **Mistake:** "lock-free = fast." It's a **progress** property; under contention it
  can be slower than a good lock.
- **Mistake:** ignoring **ABA** in manual-memory lock-free code — leads to rare,
  brutal corruption.
- **Edge case (false sharing):** adding a thread makes the program **slower** because
  two hot variables share a cache line — pad to 64 bytes.
- **Tradeoff:** stronger memory order (`seq_cst`) = easier reasoning but slower;
  `relaxed` = fast but only safe for order-independent uses (pure counters).
- **Edge case:** a **benign data race** is still **undefined behaviour** in C/C++ —
  "it worked in testing" is not correctness.

---

## 15.8 Exam, Interview & Coding Perspectives

- **GATE / C-DAC:** the race-condition/lost-update reasoning, atomicity of
  read-modify-write, and concurrency-vs-parallelism definitions; ties back to §M7
  (critical section, semaphores).
- **SEBI / RBI / NABARD:** mostly the concurrency-vs-parallelism distinction and
  race-condition concept as MCQs.
- **Interview (senior backend/systems — extremely high yield):**
  - "Concurrency vs parallelism?" → structure vs simultaneous execution.
  - "What's a race condition / how do you fix it?" → shared mutable state + timing;
    lock or atomic.
  - "What is CAS? Write a CAS loop." → the universal primitive + retry loop.
  - "Explain acquire/release / memory ordering." → publish/subscribe happens-before.
  - "What's the ABA problem?" → value A→B→A defeats CAS; fix with tags/hazard
    pointers.
  - "What is false sharing?" → different variables, same cache line, ping-pong.
  - "When would you go lock-free?" → tiny hot path / no-block-on-stall; mind the
    dangers.
- **Coding/practical:** implement a lock-free counter (fetch-and-add) and a Treiber
  stack (CAS loop); use ThreadSanitizer (`-fsanitize=thread`) to catch data races;
  `perf c2c` to detect false sharing.

---

## 15.9 Concept Checks & MCQs (test yourself)

1. Concurrency vs parallelism? → **dealing with** many tasks (structure, 1+ core) vs
   **doing** many at once (execution, 2+ cores).
2. Why is `x++` racy across threads? → it's a **read-modify-write**; interleaving
   loses updates.
3. The two concurrency demons? → **atomicity** and **visibility/ordering**.
4. Does C/C++ `volatile` synchronize threads? → **No**.
5. The **universal** atomic primitive? → **CAS**.
6. Best atomic for a lock-free counter? → **fetch-and-add**.
7. What does a CAS loop do on failure? → **retry** with the fresh current value.
8. What forbids memory reordering? → a **memory barrier / fence**.
9. Release + acquire create a ___ edge → **happens-before** (publish/subscribe).
10. Strongest memory model? → **sequential consistency** (slowest).
11. Weakest useful order (atomic, no ordering)? → **relaxed** (counters/stats only).
12. Lock-free vs wait-free? → **some** vs **every** thread makes bounded progress.
13. Canonical lock-free stack? → **Treiber stack** (CAS on head).
14. The ABA problem? → **A→B→A** fools CAS (value, not history).
15. Two ABA fixes? → **tagged pointers (DWCAS)** / **hazard pointers or GC**.
16. Two vars, same 64B line, two cores → ? → **false sharing** (pad to a cache line).
17. Is lock-free always faster? → **No** (retry storms under contention).
18. Mutex unlock/lock behave as which fences? → **release** / **acquire**.

**True/False**
- Concurrency requires multiple cores. → **False** (parallelism does).
- CAS can build any concurrent object. → **True** (universal).
- Lock-free means no thread ever starves. → **False** (that's **wait-free**).
- `volatile` (C/C++) prevents data races. → **False**.
- False sharing is a correctness bug. → **False** (a **performance** bug).
- `seq_cst` is the fastest memory order. → **False** (it's the slowest/strongest).

---

## 15.10 One-Page Revision Sheet

```
CONCURRENCY = dealing with many tasks (STRUCTURE; 1+ core, interleave).
PARALLELISM = doing many at once (EXECUTION; needs 2+ cores). Pike: deal vs do.

RACE CONDITION = correctness depends on timing of shared mutable state.
  x++ = READ-MODIFY-WRITE (3 steps) -> interleave loses updates.
  TWO demons: (1) ATOMICITY  (2) VISIBILITY/ORDERING. Locks fix both.
  C/C++ volatile fixes NEITHER (not a threading tool).

ATOMIC RMW (hardware; base of ALL sync):
  test-and-set/XCHG -> spinlock ; FETCH-AND-ADD -> counters (no lock);
  CAS(addr,expected,new) = write only if unchanged -> UNIVERSAL.
  CAS loop:  do{ old=*a; new=f(old);} while(!CAS(a,old,new));

MEMORY ORDERING (compiler+CPU REORDER; store buffers):
  BARRIER/FENCE forbids reordering + flushes.
  RELEASE store = PUBLISH ; ACQUIRE load = SUBSCRIBE -> happens-before.
    (mutex unlock=release, lock=acquire => CS writes visible to next locker)
  Ladder: seq_cst (strongest,intuitive,slow) > acquire/release > relaxed (no order).

NON-BLOCKING:
  blocking(locks): stalled holder blocks all.
  LOCK-FREE  = SOME thread progresses (may retry forever).
  WAIT-FREE  = EVERY thread progresses in BOUNDED steps (stronger, rare).
  TREIBER STACK = lock-free stack: CAS the head in a retry loop.
  ABA problem: value A->B->A fools CAS (compares value, not history).
    fix: TAGGED/versioned pointer (DWCAS) ; hazard pointers / epoch / GC.
  FALSE SHARING: different vars on same 64B CACHE LINE -> ping-pong -> slow.
    fix: pad/align to 64B. (perf bug, not correctness.)
  LOCK-FREE when: tiny hot path, must not block on stall. Dangers: hard, ABA,
    retry storms (NOT always faster), livelock/starvation.
```

### Flash cards

| Front | Back |
|-------|------|
| Concurrency vs parallelism? | deal-with-many (structure) vs do-many-at-once (execution) |
| Why is x++ racy? | read-modify-write; interleave loses updates |
| Two concurrency demons? | atomicity + visibility/ordering |
| Does volatile (C/C++) synchronize? | No |
| Universal atomic primitive? | CAS |
| Lock-free counter primitive? | fetch-and-add |
| CAS on failure? | doesn't write; retry |
| Publish/subscribe fences? | release / acquire (happens-before) |
| Strongest memory model? | sequential consistency (slowest) |
| Lock-free vs wait-free? | some vs every thread bounded progress |
| Canonical lock-free stack? | Treiber (CAS head) |
| ABA problem? | A→B→A fools CAS; tag/hazard-pointer fix |
| False sharing? | different vars, same 64B line → pad |
| Is lock-free always faster? | No (retry storms) |

### Spaced repetition
- **24-hour:** recite concurrency-vs-parallelism, the lost-update trace, and the CAS
  loop.
- **7-day:** explain acquire/release publish-subscribe, the Treiber stack, and the
  ABA problem with the A→B→A trace.
- **30-day:** given "adding a thread made it slower" (false sharing) or "flag loop
  hangs / sees stale data" (ordering), diagnose and fix from first principles.

---

## 15.11 Summary

Concurrency (**structure**: many tasks in progress, even on one core) is not
parallelism (**execution**: many tasks at once, needing many cores). Where they meet
**shared mutable state**, two demons appear: **atomicity** (the lost-update
**race condition** on a read-modify-write like `x++`) and **visibility/ordering**
(caches, store buffers, and compilers making one thread's writes late or reordered —
and `volatile` fixes neither in C/C++). The hardware answer is **atomic RMW**
instructions — **fetch-and-add** for counters and the **universal CAS**
("write only if unchanged"), used in a **retry loop**. Above that sits the **memory
model**: **barriers/fences** stop reordering, **release/acquire** give a cheap
**publish/subscribe happens-before** edge (exactly what a mutex's unlock/lock do),
and **sequential consistency** is the strongest, simplest, slowest guarantee. Built
on CAS, **lock-free** (some thread always progresses) and **wait-free** (every
thread progresses in bounded time) algorithms — the **Treiber stack** being the
canonical example — avoid the perils of locks, but bring their own: the **ABA
problem** (fixed with tagged pointers or hazard pointers), **false sharing** (fixed
by padding to a 64-byte cache line), and the sober truth that **lock-free is a
progress guarantee, not a speed guarantee**.

Next, **Module 16 — Security** builds on all of this: how the OS enforces
**privilege, isolation, and access control** — the protections that keep concurrent,
multi-tenant systems safe.

> **You have mastered this module when** you can: cleanly separate concurrency from
> parallelism; explain a race condition *and* a memory-visibility bug and fix each;
> write a CAS loop and say why CAS is universal; explain acquire/release and
> sequential consistency; and describe the Treiber stack, the ABA problem, false
> sharing, and when (and when *not*) to go lock-free — all without notes.
