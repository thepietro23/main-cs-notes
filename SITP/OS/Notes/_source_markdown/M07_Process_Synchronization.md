---
title: "Module 7 — Process Synchronization"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — Process Synchronization

> **Where this module sits.**
> Modules on processes and threads (M4–M5) let many things run "at once".
> Scheduling (M6) decides *who* runs *when*. But the moment two of those
> concurrent flows touch the **same data**, we hit the deepest, most exam-heavy
> problem in operating systems: **how do we let them cooperate without corrupting
> shared state?** This module builds the answer from the ground up — the
> **critical-section problem**, **race conditions**, software (**Peterson's**) and
> hardware (**test-and-set / compare-and-swap**) locks, **semaphores** and
> **monitors**, and the four *classic problems* (Producer–Consumer,
> Readers–Writers, Dining Philosophers, Sleeping Barber) that every one of these
> exams recycles. It sets up **Deadlocks (M8)**, which is what synchronization
> looks like when it goes *wrong*.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★★      | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** the **critical-section
problem** and its **three requirements** (mutual exclusion, progress, bounded
waiting); **race conditions** on a shared counter; **Peterson's algorithm**
(flag + turn, why it works); **test-and-set** and **compare-and-swap** atomicity;
**semaphore** `wait`/`signal` (P/V) and **counting vs binary**; **busy-wait
(spinlock) vs block**; **monitors** and **condition variables**; and the four
classic problems — especially **Producer–Consumer (empty/full/mutex)** and
**Dining Philosophers** deadlock + fix.

---

## 7.1 The Critical-Section Problem (first principles)

### Why we even have a problem

Concurrency is an illusion built on **interleaving**. On one CPU the scheduler can
pause a thread *between any two machine instructions* and run another; on many CPUs
threads run *truly* at the same time. Either way, when two flows read-modify-write
the **same shared variable**, their steps can interleave in an order the
programmer never imagined — and the data ends up wrong.

A **critical section** is the piece of code that touches shared data (a shared
counter, a linked list, a bank balance). The problem: **make sure that when one
process is in its critical section, no other process is in *its* critical section
for the same data.**

Every process's code is split into four regions:

```text
do {
    [ entry section ]        // ask permission to enter
        critical section     // touch shared data  <-- must be exclusive
    [ exit section ]         // signal "I'm done"
        remainder section    // everything else (no shared data)
} while (true);
```

> **Memory hook:** a critical section is a **single-occupancy toilet**. The
> **entry section** is knocking + locking the door; the **exit section** is
> unlocking; **remainder** is your normal life outside. The whole subject is just
> "how do we build a reliable lock on that door?"

### The three requirements a correct solution MUST satisfy

Any solution to the critical-section problem must meet **all three** (a guaranteed
exam line — memorise the names):

1. **Mutual Exclusion.** If process Pi is executing in its critical section, then
   **no other process** can be in its critical section at the same time.
2. **Progress.** If no process is in its critical section and some processes *want*
   to enter, then **only those not in their remainder** participate in deciding who
   goes next, and the decision **cannot be postponed indefinitely**. (No process
   outside the critical section may block another from entering.)
3. **Bounded Waiting.** There is a **limit** on how many times other processes may
   enter their critical sections *after* a process has requested entry and *before*
   that request is granted. (No **starvation** — everyone eventually gets in.)

> **Memory hook — "ME-P-BW" (Me, Please, Be-Waiting):** **M**utual exclusion,
> **P**rogress, **B**ounded **W**aiting. Mutual exclusion = *safety* (nothing bad
> happens); progress + bounded waiting = *liveness* (something good eventually
> happens).

### MCQs

1. The three requirements of a CS solution? → **mutual exclusion, progress,
   bounded waiting**.
2. Which requirement prevents starvation? → **bounded waiting**.
3. A process stuck in its remainder section must not block others — which
   requirement is that? → **progress**.

---

## 7.2 Race Conditions — the bug, worked step by step

A **race condition** is when the **final result depends on the timing/order** in
which processes are scheduled. The program is "correct" in every single run of a
thread alone, yet **wrong** when they interleave.

### The classic shared-counter example

Two threads each run `counter++` on a shared variable `counter` that starts at
**5**. In a high-level language `counter++` looks atomic, but the CPU actually does
**three** steps:

```text
counter++  compiles to:   R1 = counter      (load)
                          R1 = R1 + 1        (increment register)
                          counter = R1       (store)
```

Each thread has its **own** register `R1`. If the scheduler interleaves them
*badly*, one update is **lost**:

```text
Thread A                 Thread B                counter
--------                 --------                -------
R1a = counter (=5)                                  5
R1a = R1a + 1 (=6)                                  5
                         R1b = counter (=5)         5   <- B read the STALE 5
                         R1b = R1b + 1 (=6)         5
counter = R1a (=6)                                  6   <- A stores 6
                         counter = R1b (=6)         6   <- B stores 6 (LOST UPDATE)
```

Both threads incremented, so the answer *should* be **7**, but we got **6**. One
increment vanished. Run it a million times and you'll occasionally see 6 and
occasionally 7 — **the same program, different answers**. That non-determinism is
the signature of a race.

> **Memory hook:** the villain is the **read-modify-write** gap. Between "read 5"
> and "write 6", the value can go stale under you. A lock makes that gap
> **indivisible (atomic)**.

> **Why it matters in the real world:** this exact pattern corrupts bank balances,
> inventory counts, reference counters (`use_count`), and web request metrics. It
> is the #1 reason multithreaded code is hard.

### MCQs

1. `counter` starts 5, two threads do `counter++`; possible wrong result? →
   **6** (a lost update; correct is 7).
2. A race condition means the result depends on? → the **timing/order of
   scheduling**.
3. Why isn't `counter++` safe? → it is a **non-atomic read-modify-write**.

---

## 7.3 Peterson's Algorithm (a pure-software solution)

Before hardware help, can **two processes** coordinate using only ordinary shared
variables? Yes — **Peterson's algorithm** (1981) is the elegant classic. It uses
two shared variables:

- `flag[2]` — `flag[i] = true` means "**process i wants to enter**".
- `turn` — whose **turn** it is to yield (a tie-breaker).

```c
// shared, initialised
boolean flag[2] = {false, false};
int     turn;

// code for process Pi   (the other is Pj, where j = 1 - i)
do {
    flag[i] = true;                 // 1. announce: I want in
    turn    = j;                    // 2. politely give the turn away
    while (flag[j] && turn == j)    // 3. wait ONLY if j also wants in AND it's j's turn
        ;                           //    (busy-wait / spin)

        /* ---- critical section ---- */

    flag[i] = false;                // 4. exit: I no longer want in

        /* ---- remainder section ---- */
} while (true);
```

### Why it works (satisfies all three requirements)

- **Mutual exclusion.** For *both* to be inside, both need `flag[]=true`. But
  `turn` holds a **single** value — it can be `i` **or** `j`, not both. Whoever set
  `turn` **last** loses the race and spins. So at most one enters. ✔
- **Progress.** If Pj is not interested (`flag[j]=false`), Pi enters immediately —
  a remainder-section process never blocks anyone. ✔
- **Bounded waiting.** After Pi sets `turn = j` and waits, when Pj exits it will
  (if it re-tries) set `turn = i`, letting Pi in. So Pi waits **at most one** turn.
  No starvation. ✔

> **Memory hook:** "**I raise my hand (`flag`), then say *after you* (`turn`).**"
> The polite one who spoke last waits — and because there's only one `turn`, only
> one can proceed.

> **Real-world caveat (why we don't use it today):** Peterson's assumes memory
> reads/writes happen **in program order**. Modern CPUs and compilers **reorder**
> memory operations, so on real hardware it needs **memory barriers/fences** to be
> correct. It also **only works for 2 processes** and **busy-waits**. It's a
> teaching gem, not production code — real systems use atomic hardware
> instructions (§7.4).

### MCQs

1. Two shared variables in Peterson's? → **`flag[]`** and **`turn`**.
2. What guarantees only one enters? → `turn` holds **one value**; last writer
   waits.
3. Peterson's works for how many processes? → **two**.
4. Why can Peterson's fail on real CPUs? → **memory reordering** (needs fences).

---

## 7.4 Hardware Support — Atomic Instructions

Software locks are fiddly. Modern CPUs give us **atomic** read-modify-write
instructions the hardware guarantees run as **one indivisible step** (no
interleaving, even across cores). Locks are built on these.

### Test-and-Set (TAS)

Atomically returns the old value **and** sets the location to `true`:

```c
// executed ATOMICALLY by hardware
boolean test_and_set(boolean *target) {
    boolean old = *target;
    *target = true;
    return old;
}

// a simple spinlock:
boolean lock = false;
do {
    while (test_and_set(&lock))    // spin while lock was already true
        ;                          // (the entry section)
        /* ---- critical section ---- */
    lock = false;                  // exit section: release
        /* ---- remainder ---- */
} while (true);
```

The first thread finds `lock=false`, TAS returns `false` (so it enters) and sets
`lock=true`. Everyone else's TAS returns `true` and they spin. Because TAS is
atomic, **two threads can't both read `false`**.

### Compare-and-Swap (CAS)

More powerful (and what real hardware exposes as `CMPXCHG` / `LOCK XADD`, or C11
`atomic_compare_exchange`). Atomically: "if the value is what I *expected*, replace
it; either way tell me the old value."

```c
// executed ATOMICALLY
int compare_and_swap(int *value, int expected, int new_val) {
    int old = *value;
    if (*value == expected)
        *value = new_val;
    return old;
}

// spinlock with CAS:  0 = free, 1 = held
int lock = 0;
while (compare_and_swap(&lock, 0, 1) != 0)   // enter only if it was 0
    ;
    /* ---- critical section ---- */
lock = 0;                                     // release
```

> **Memory hook:** **TAS = "grab it and tell me if it was free."**
> **CAS = "swap it *only if* nobody changed it behind my back."** CAS is the
> foundation of **lock-free** data structures because it detects interference.

- **Atomicity** here means: the read, the compare, and the write happen as **one**
  bus/cache-coherency transaction — no other core can sneak in between. This is
  enforced by the CPU (e.g. the x86 `LOCK` prefix / cache-line locking).
- Plain TAS spinlocks can **violate bounded waiting** (an unlucky thread might spin
  forever). Textbooks give a bounded-waiting variant using a `waiting[]` array +
  TAS that hands the lock to the next waiter in turn.

### MCQs

1. What does test-and-set return? → the **old** value (then sets it true).
2. CAS updates only if? → the current value equals the **expected** value.
3. Why are these instructions special? → they are **atomic** (indivisible, even
   across cores).
4. Which is the basis of lock-free structures? → **compare-and-swap (CAS)**.

---

## 7.5 Mutex, Spinlocks: Busy-Wait vs Block

A **mutex** (mutual-exclusion lock) is the simplest lock: `acquire()` before the
critical section, `release()` after. Only the thread that acquired it may release
it (**ownership**). The key design question is **what a thread does when the lock
is already held**:

| | **Spinlock (busy-wait)** | **Blocking mutex (sleep)** |
|---|---|---|
| While waiting | **loops** on the CPU checking the lock | **sleeps**; OS puts it on a wait queue |
| Wastes CPU? | **yes**, burns cycles spinning | **no**, CPU runs others |
| Context-switch cost | **none** | **two** switches (block + wake) |
| Best when | critical section is **very short** & multi-core | critical section is **long** or single-core |

- A **spinlock** is worth it only when the expected wait is **shorter than a
  context switch** (a few hundred ns) and there is **another CPU** actually running
  the lock-holder — spinning on a single CPU while the holder is descheduled is
  pure waste (and can deadlock).
- A **blocking mutex** trades two context switches for freeing the CPU — right when
  the critical section is long.

> **Memory hook:** **spin = wait *at* the door tapping your foot** (fast to notice
> it opens, but you do nothing else); **block = go home and get a phone call when
> it's free** (frees you up, but the call has overhead). Short wait → spin; long
> wait → block.

- **Busy-waiting** is also called **spinning**. Its one virtue is **no context
  switch**; its vice is **wasted CPU**. Semaphores (next) can be built either way.
- Real kernels use **hybrid** locks (e.g. Linux **adaptive mutex** / futex): spin
  briefly *if* the holder is running on another CPU, else sleep.

### MCQs

1. Spinlock vs blocking mutex core difference? → **busy-wait on CPU** vs **sleep +
   requeue**.
2. When is a spinlock appropriate? → **very short** critical section on a
   **multi-core** system.
3. Cost of a blocking mutex when contended? → **two context switches**.

---

## 7.6 Semaphores (the workhorse)

A **semaphore** is an integer `S` accessed **only** through two **atomic**
operations, invented by **Dijkstra**:

- **`wait(S)`** — a.k.a. **`P`** (Dutch *proberen*, "to test") or **down**.
- **`signal(S)`** — a.k.a. **`V`** (*verhogen*, "to increment") or **up**.

```text
wait(S) {                 signal(S) {
    S = S - 1;                S = S + 1;
    if (S < 0)                if (S <= 0)
        block(this proc);        wakeup(one waiting proc);
}                         }
```

The whole `wait`/`signal` body is **atomic** (protected by the OS with interrupts
disabled or a spinlock). With the block/wakeup form, a **negative `S` means "how
many processes are waiting"** (`|S|` = queue length).

> **Memory hook:** semaphore = a **box of permits**. `wait` = **take a permit**
> (if none left, sleep until one appears); `signal` = **return a permit** (and wake
> someone waiting). The count *is* the number of free permits.

### Counting vs Binary semaphores

- **Counting semaphore:** `S` can be any non-negative count — use it to guard
  **N identical resources** (e.g. 5 database connections → `S = 5`). Each `wait`
  takes one; when `S = 0`, further `wait`s block.
- **Binary semaphore:** `S ∈ {0, 1}` — behaves like a **lock** (mutex). Initialise
  to **1**: first `wait` makes it 0 (locked); `signal` makes it 1 (unlocked).

> **Semaphore vs mutex — the interview nuance:** a **mutex has ownership** (only
> the locker unlocks it); a **binary semaphore does not** — *any* thread may
> `signal`. That makes a binary semaphore a **signalling** tool (thread A tells
> thread B "go"), while a mutex is strictly a **locking** tool.

### Using a semaphore to solve the critical-section problem

```text
semaphore mutex = 1;          // shared, initial value 1

do {
    wait(mutex);              // entry section
        /* ---- critical section ---- */
    signal(mutex);           // exit section
        /* ---- remainder ---- */
} while (true);
```

This gives **mutual exclusion** trivially: the first `wait` drops `mutex` to 0, so
the next thread blocks until the holder `signal`s.

### Two dangers with semaphores (exam favourites)

Semaphores are powerful but **error-prone** because *you* place every `wait`/
`signal` by hand:

- **Deadlock.** Two processes each hold one semaphore and wait for the other:

  ```text
  P0: wait(S); wait(Q); ...        P1: wait(Q); wait(S); ...
  ```
  If P0 gets `S` and P1 gets `Q`, each waits forever (see M8).
- **Priority inversion.** A high-priority task waits on a semaphore held by a
  low-priority task that a medium task keeps preempting. Fixed by **priority
  inheritance** (the famous Mars Pathfinder bug).
- Also: forgetting a `signal` (permanent block) or an extra `signal` (breaks mutual
  exclusion). These bugs motivate **monitors** (§7.7).

### MCQs

1. `wait`/`signal` are also called? → **P/V** (down/up).
2. A binary semaphore initialised to 1 acts as a? → **mutex/lock**.
3. Counting semaphore for 5 resources starts at? → **5**.
4. `S = -3` (block form) means? → **3 processes are waiting**.
5. Semaphore vs mutex? → semaphore has **no ownership**; mutex does.

---

## 7.7 Monitors and Condition Variables

Hand-placed `wait`/`signal` calls are like manual memory management — one slip and
you deadlock or corrupt data. A **monitor** is a **higher-level** construct
(supported by the language/runtime, e.g. Java `synchronized`, C# `lock`, POSIX
condition variables) that makes synchronization **automatic and structured**.

- A **monitor** bundles shared data + the procedures that use it, and guarantees
  that **only one process is active inside the monitor at a time** — mutual
  exclusion is **built in**; you don't write `wait(mutex)` yourself.
- To let a process **wait for a condition** (e.g. "buffer not full"), monitors add
  **condition variables** with two operations:
  - **`x.wait()`** — the caller **suspends** and, crucially, **releases the
    monitor lock** so others can enter.
  - **`x.signal()`** — **resumes one** process waiting on `x` (if none is waiting,
    it does **nothing** — unlike a semaphore's `signal`, which is remembered).

> **Memory hook:** a semaphore's `signal` is a **coin dropped in a jar** (counted,
> remembered even if nobody's there). A condition variable's `signal` is a **knock
> on a sleeping person's door** — if nobody's asleep, the knock is **wasted**.
> Hence CV waits must be inside a **`while` loop** re-checking the condition.

### Why monitors are "higher-level" than semaphores

| | Semaphore | Monitor |
|---|---|---|
| Mutual exclusion | you must code it | **automatic** (compiler/runtime) |
| `signal` with no waiter | **increments** (remembered) | **lost** (no effect) |
| Error-prone? | very (misplaced wait/signal) | much safer (structured) |
| Where | any language, OS primitive | language/runtime feature |

### Signal semantics (Hoare vs Mesa)

When `x.signal()` wakes a waiter, **who runs next**?

- **Hoare (signal-and-wait):** the signaller **yields immediately** to the woken
  process; the condition it signalled is still true. Cleaner theory, harder to
  implement.
- **Mesa (signal-and-continue):** the signaller **keeps running**; the woken
  process runs *later*, by which time the condition **may no longer hold**. This is
  what Java and pthreads use — **so you must re-check with `while`, not `if`.**

```text
// Mesa-style: ALWAYS re-check in a while loop
while (!condition)
    x.wait();
```

### MCQs

1. What is built into a monitor automatically? → **mutual exclusion**.
2. `x.signal()` with no waiter does? → **nothing** (lost).
3. Why re-check a condition in a `while`, not `if`? → **Mesa** signal-and-continue
   (condition may change before you run).
4. `x.wait()` on a condition variable also does what to the lock? → **releases**
   it while sleeping.

---

## 7.8 Classic Problem #1 — Producer–Consumer (Bounded Buffer)

A **producer** makes items and puts them in a shared buffer of **n** slots; a
**consumer** removes them. We must: never overflow a full buffer, never read from
an empty one, and never corrupt the buffer with simultaneous access.

![Producer–Consumer with a bounded buffer guarded by three semaphores: empty counts free slots, full counts filled slots, and mutex protects the buffer.](images/73_producer_consumer.png)

**Three semaphores** do the job:

- `mutex = 1` — binary lock for exclusive buffer access.
- `empty = n` — counts **free** slots (producer waits on it).
- `full  = 0` — counts **filled** slots (consumer waits on it).

```text
semaphore mutex = 1, empty = n, full = 0;

Producer:                          Consumer:
do {                               do {
    // produce an item                 wait(full);      // wait for an item
    wait(empty);   // a free slot?     wait(mutex);     // lock buffer
    wait(mutex);   // lock buffer      // remove item from buffer
    // add item to buffer              signal(mutex);   // unlock
    signal(mutex); // unlock           signal(empty);   // one more free slot
    signal(full);  // one more item    // consume the item
} while (true);                    } while (true);
```

> **The two rules you must never break (classic exam mistake):**
> 1. **Order of `wait`s matters:** take the **counting** semaphore (`empty`/`full`)
>    **before** `mutex`. If you do `wait(mutex)` then `wait(empty)` and the buffer
>    is full, the producer **holds `mutex` while blocked** — the consumer can never
>    get `mutex` to make room → **deadlock**.
> 2. **`signal`s** on `mutex` and the counter can be in either order, but `mutex`
>    must be released.

> **Memory hook:** producer **`wait(empty)` → `wait(mutex)` … `signal(mutex)` →
> `signal(full)`**; consumer is the **mirror image** (`full`↔`empty`).

### MCQs

1. Three semaphores in bounded buffer? → **mutex(1), empty(n), full(0)**.
2. Producer waits on? → **empty**. Consumer waits on? → **full**.
3. Why take `empty`/`full` before `mutex`? → else you **hold `mutex` while
   blocked** → deadlock.

---

## 7.9 Classic Problem #2 — Readers–Writers

Many processes want a shared object. **Readers** only read (safe together);
**writers** modify (need exclusive access). Rule: **any number of readers OR one
writer**, never both. The **reader-preference** solution:

```text
semaphore mutex = 1;    // protects read_count
semaphore wrt   = 1;    // writer lock (also blocks readers vs writer)
int       read_count = 0;

Writer:
    wait(wrt);          // exclusive access
        // ... write ...
    signal(wrt);

Reader:
    wait(mutex);
        read_count++;
        if (read_count == 1)   // FIRST reader
            wait(wrt);         //   locks out writers
    signal(mutex);
        // ... read ...          (many readers here at once)
    wait(mutex);
        read_count--;
        if (read_count == 0)   // LAST reader
            signal(wrt);       //   lets a writer in
    signal(mutex);
```

- The **first** reader grabs `wrt` (blocking writers); the **last** reader releases
  it. In between, readers pour in freely — that's *why* they share.
- `mutex` protects only the tiny `read_count` update, not the reading itself.

> **This is reader-preference → writers can STARVE.** As long as readers keep
> arriving, `read_count` never hits 0, so a waiting writer waits forever. Fixes:
> **writer-preference**, or a **fair (FIFO) queue** (e.g. add a `turnstile`
> semaphore all newcomers must pass, so a waiting writer blocks new readers).

> **Memory hook:** **first reader turns the lights on (locks out writers); last
> reader turns them off.** More readers = free; a writer needs the whole room dark.

### MCQs

1. Readers–writers rule? → **many readers OR one writer**, not both.
2. Who acquires `wrt` among readers? → the **first** reader; released by the
   **last**.
3. Downside of reader-preference? → **writer starvation**.

---

## 7.10 Classic Problem #3 — Dining Philosophers

Five philosophers sit around a table; between each pair is **one fork**. A
philosopher needs **both** the fork on the left **and** the one on the right to
eat, then puts both down and thinks. Model: each fork is a binary semaphore.

![Five philosophers around a table sharing five forks; if every philosopher picks up the left fork first, all hold one and wait for the right — a circular wait deadlock.](images/74_dining_philosophers.png)

**The naive (broken) solution:**

```text
semaphore fork[5] = {1,1,1,1,1};

Philosopher i:
do {
    wait(fork[i]);            // pick up LEFT fork
    wait(fork[(i+1) % 5]);    // pick up RIGHT fork
        // ... eat ...
    signal(fork[i]);          // put down LEFT
    signal(fork[(i+1) % 5]);  // put down RIGHT
        // ... think ...
} while (true);
```

> **Why it deadlocks:** if **all five** pick up their **left** fork at the same
> instant, every fork is held and **each waits forever** for the right fork —
> that's a **circular wait** (all four Coffman conditions hold; see M8).

**Fixes (any one works — know at least two):**

1. **Allow at most 4 at the table.** Add a counting semaphore `room = 4`;
   `wait(room)` before grabbing forks, `signal(room)` after. With ≤4 competing for
   5 forks, at least one can always eat → no circular wait.
2. **Asymmetric ordering.** Odd philosophers pick **left then right**; even pick
   **right then left**. This breaks the symmetry that causes circular wait.
3. **Pick up both forks atomically.** Guard the two `wait`s with an extra `mutex`
   so a philosopher grabs **both or neither** — never holds one while waiting.
4. **Resource ordering.** Always grab the **lower-numbered** fork first (a general
   deadlock-prevention rule — negates *circular wait*, M8).

> **Memory hook:** deadlock here = **"everyone grabbed left, nobody can grab
> right."** Break it by **removing one diner (room=4)**, **flipping one person's
> grab order**, or **grabbing both forks at once**.

### MCQs

1. What causes the dining-philosophers deadlock? → all hold **left**, wait for
   **right** (**circular wait**).
2. A simple fix using a counter? → allow only **n−1 (4)** at the table.
3. Asymmetric fix? → **odd/even** pick forks in **opposite order**.

---

## 7.11 Classic Problem #4 — Sleeping Barber

A barbershop has **one barber**, one barber chair, and **N** waiting chairs. If no
customers, the barber **sleeps**. A customer wakes the barber if he's asleep; if
all waiting chairs are full, the customer **leaves**. Model the coordination:

```text
semaphore customers = 0;   // # of waiting customers (barber waits on this)
semaphore barber    = 0;   // barber is ready (customer waits on this)
semaphore mutex     = 1;   // protects 'waiting'
int       waiting   = 0;   // customers currently waiting
const int CHAIRS    = N;

Barber:                              Customer:
do {                                 wait(mutex);
    wait(customers); // sleep if 0   if (waiting < CHAIRS) {
    wait(mutex);                         waiting++;
    waiting--;                           signal(customers); // wake barber
    signal(barber);  // I'm ready        signal(mutex);
    signal(mutex);                       wait(barber);      // wait my turn
    // ... cut hair ...                  // ... get haircut ...
} while (true);                      } else {
                                         signal(mutex);     // shop full: leave
                                     }
```

- `customers` lets the **barber sleep** when the count is 0 and be **woken** by an
  arriving customer.
- `barber` makes the **customer wait** until the barber signals "ready".
- `mutex` protects the shared `waiting` count. A customer who finds
  `waiting == CHAIRS` **balks** (leaves) instead of blocking.

> **Memory hook:** it's Producer–Consumer with a **bounded waiting room**: the
> **barber is the consumer** (sleeps when no items), **customers are producers**
> who **give up** if the buffer (chairs) is full.

### MCQs

1. What does the barber `wait(customers)` do when count is 0? → **sleeps**.
2. What happens when all chairs are full? → the customer **leaves (balks)**.
3. Sleeping Barber is a variant of which problem? → **Producer–Consumer** (bounded
   buffer).

---

## 7.12 Real-World & Backend Perspectives

- **Every database** you touch is a giant synchronization engine: row/table
  **locks**, **latches** (spinlock-like short locks on buffer pages), and MVCC are
  M7 ideas at scale. The Producer–Consumer pattern *is* a **connection pool** or a
  **message queue** (Kafka, RabbitMQ, Go channels).
- **Language primitives** are direct descendants: Java `synchronized`/`ReentrantLock`/
  `Semaphore`, Go's `sync.Mutex` + **channels** (CSP-style monitors), Python's
  `threading.Lock`/`Semaphore` (though the **GIL** serialises CPU-bound threads),
  C++ `std::mutex`/`std::atomic` (CAS).
- **Atomics power lock-free code:** counters, ring buffers, and concurrent queues in
  high-performance servers use **CAS** to avoid the two-context-switch cost of
  blocking locks.
- **Linux futex** is the hybrid mutex from §7.5 — spin briefly in user space, then
  make a system call to sleep only under contention (fast uncontended path).
- **Priority inversion** famously froze **NASA's Mars Pathfinder** (1997) — fixed
  in flight by enabling **priority inheritance** on a mutex.

---

## 7.13 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Assuming `counter++` / `x = x + 1` is **atomic** — it is **not** (§7.2).
- In Producer–Consumer, taking **`mutex` before** `empty`/`full` → **deadlock**.
- Using **`if`** instead of **`while`** to re-check a condition variable (Mesa
  semantics) → spurious-wakeup bug.
- Confusing **binary semaphore** with **mutex** — a semaphore has **no ownership**.
- Forgetting a `signal` (permanent block) or double-`signal` (breaks mutual
  exclusion).
- Spinning on a single-core CPU while the lock-holder is descheduled → wasted CPU /
  livelock.

**Edge cases**
- A `signal` on a **condition variable** with no waiter is **lost**; on a
  **semaphore** it is **remembered** (increments the count).
- **Reader-preference** starves writers; **writer-preference** starves readers —
  fairness needs a queue.
- **Priority inversion** can defeat correct locking on real-time systems.

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Spinlock | no context switch (fast if short) | wastes CPU while waiting |
| Blocking mutex | frees CPU | two context switches |
| Semaphore | flexible, low-level | error-prone (manual wait/signal) |
| Monitor | safe, structured | needs language/runtime support |
| Lock-free (CAS) | no blocking, scalable | hard to write correctly (ABA problem) |

---

## 7.14 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** state the **three CS requirements**; trace a
**race condition** on a counter; write/explain **Peterson's** and why it works;
**test-and-set vs compare-and-swap**; **counting vs binary** semaphore; the
**Producer–Consumer** semaphore code (and the mutex-order deadlock); dining
philosophers deadlock + fix; **semaphore vs monitor**.

**Interview:** "What's a race condition — show one." "Difference between a mutex
and a semaphore?" (ownership). "When would you spin vs block?" "What's a deadlock
and how do you avoid it?" (segue to M8). "Why re-check condition variables in a
loop?" (Mesa).

**Coding/practical:**
- Reproduce a race: two threads `++` a shared counter 1,000,000 times → the total
  is < 2,000,000; fix with a mutex/atomic.
- Build a bounded blocking queue (Producer–Consumer) with a mutex + two condition
  variables — the canonical interview implementation.

---

## 7.15 Concept Checks & MCQs (test yourself)

1. Three requirements of a CS solution? → **mutual exclusion, progress, bounded
   waiting**.
2. Which prevents starvation? → **bounded waiting**.
3. `counter=5`, two threads `counter++` — wrong result? → **6** (lost update).
4. Two variables in Peterson's? → **`flag[]`, `turn`**; works for **2** processes.
5. What breaks the tie in Peterson's? → the single-valued **`turn`**.
6. Test-and-set returns? → the **old** value (then sets true).
7. CAS swaps only if value == ? → **expected**.
8. What makes TAS/CAS special? → **atomicity** (indivisible across cores).
9. Binary semaphore = ? → a **lock/mutex** (values 0/1).
10. Counting semaphore for N resources starts at? → **N**.
11. `wait`/`signal` other names? → **P/V** (down/up).
12. Producer waits on ___, consumer on ___? → **empty / full**.
13. Producer–Consumer: take `mutex` first? → **no** — deadlock; take `empty`/`full`
    first.
14. Readers–writers: who locks `wrt`? → the **first** reader (last one releases).
15. Reader-preference starves? → **writers**.
16. Dining philosophers deadlock cause? → all grab **left**, wait for **right**
    (circular wait).
17. One dining-philosophers fix? → allow **4** at the table (or asymmetric grab).
18. Sleeping Barber is a variant of? → **Producer–Consumer**.
19. Monitor gives you ___ automatically? → **mutual exclusion**.
20. Condition-variable `signal` with no waiter? → **lost** (does nothing).
21. Why `while` not `if` on a CV? → **Mesa** (signal-and-continue).
22. Semaphore vs mutex? → semaphore has **no ownership**.
23. Spinlock good when? → **short** CS, **multi-core**.
24. Famous priority-inversion incident? → **Mars Pathfinder** (fixed by priority
    inheritance).

**True/False**
- `x = x + 1` is atomic. → **False**.
- Peterson's works for 3 processes. → **False** (2 only).
- A binary semaphore has ownership. → **False** (a mutex does).
- A condition-variable signal is remembered if no one waits. → **False**
  (semaphore's is; CV's is lost).
- Reader-preference can starve writers. → **True**.
- Taking the counting semaphore before mutex avoids a deadlock in Producer–Consumer.
  → **True**.

---

## 7.16 One-Page Revision Sheet

```
CRITICAL-SECTION PROBLEM: entry | CRITICAL | exit | remainder.
  3 REQUIREMENTS (ME-P-BW): MUTUAL EXCLUSION (safety) + PROGRESS + BOUNDED WAITING (liveness).

RACE CONDITION: result depends on interleaving. counter++ = LOAD/INC/STORE (not atomic).
  5 + two ++ can give 6 (LOST UPDATE) instead of 7. Fix = make the RMW atomic (lock).

PETERSON (2 procs, software): flag[i]=true; turn=j; while(flag[j] && turn==j);  CS; flag[i]=false.
  works: turn holds ONE value -> last writer waits. Needs memory fences on real CPUs. 2 procs only.

HARDWARE ATOMICS:
  test_and_set(&x): return old, set true.   spinlock: while(TAS(&lock)); CS; lock=false.
  compare_and_swap(&x,exp,new): set to new IFF x==exp; return old.  basis of LOCK-FREE.

LOCKS: SPINLOCK = busy-wait (no ctx switch; good for SHORT CS, multi-core).
       BLOCKING MUTEX = sleep+requeue (2 ctx switches; good for LONG CS). Mutex has OWNERSHIP.

SEMAPHORE (Dijkstra): integer + atomic wait(P/down) & signal(V/up).
  wait: S--; if S<0 block.   signal: S++; if S<=0 wakeup one.   (S<0 => |S| waiting)
  COUNTING (N resources, init N) vs BINARY (0/1 = lock). Semaphore = NO ownership (signalling).
  CS: mutex=1; wait(mutex); CS; signal(mutex).  Dangers: DEADLOCK, priority inversion.

MONITOR (high-level): mutual exclusion AUTOMATIC. condition vars: x.wait() (sleep+release lock),
  x.signal() (wake one; LOST if none waiting). Re-check with WHILE (Mesa signal-and-continue).

CLASSIC PROBLEMS:
  PRODUCER-CONSUMER: mutex=1, empty=n, full=0.
    Prod: wait(empty),wait(mutex),put,signal(mutex),signal(full).  Cons: mirror (full<->empty).
    RULE: counting sem BEFORE mutex (else hold mutex while blocked -> deadlock).
  READERS-WRITERS (reader-pref): first reader wait(wrt), last reader signal(wrt). STARVES writers.
  DINING PHILOSOPHERS: all grab left -> circular wait DEADLOCK. Fix: room=4 / asymmetric / both-at-once.
  SLEEPING BARBER: customers, barber, mutex + waiting count. = Producer-Consumer w/ bounded room.
```

### Flash cards

| Front | Back |
|-------|------|
| 3 CS requirements? | Mutual exclusion, progress, bounded waiting |
| Race on counter 5, two ++? | Can give 6 (lost update) |
| Peterson's variables? | flag[] and turn (2 processes) |
| test-and-set returns? | Old value, then sets true |
| CAS swaps only if? | value == expected |
| Binary semaphore = ? | Lock (0/1); no ownership |
| Counting sem for N resources? | Init to N |
| Producer waits on / Consumer waits on? | empty / full |
| Take mutex before empty/full? | No — deadlock |
| First reader does? | wait(wrt); last does signal(wrt) |
| Reader-preference starves? | Writers |
| Dining philosophers deadlock? | All grab left, wait right (circular wait) |
| CV signal, no waiter? | Lost (semaphore's is remembered) |
| Monitor gives you? | Automatic mutual exclusion |
| Spinlock good when? | Short CS on multi-core |

### Spaced repetition
- **24-hour:** trace the counter race; write the Producer–Consumer semaphore code
  from memory; state the 3 CS requirements.
- **7-day:** write Peterson's and explain why it works; TAS vs CAS; semaphore vs
  monitor vs mutex; dining-philosophers fix.
- **30-day:** given a scenario (connection pool, print queue, barbershop), pick the
  right primitive and write the wait/signal placement without notes.

---

## 7.17 Summary

Process synchronization is about one hard goal: let concurrent flows **share data
without corrupting it**. The trouble is the **race condition** — a non-atomic
**read-modify-write** (like `counter++`) whose result depends on interleaving,
which we watched turn "5 + two increments" into **6** instead of 7. The fix is a
correct solution to the **critical-section problem**, which must guarantee **mutual
exclusion, progress, and bounded waiting**. We built locks from the bottom up:
**Peterson's** pure-software algorithm (flag + turn, two processes), then the
**atomic hardware** instructions **test-and-set** and **compare-and-swap** that
real locks use. We compared **spinlocks (busy-wait)** with **blocking mutexes**,
then met the workhorse **semaphore** (`wait`/`signal` = P/V, counting vs binary)
and the safer, higher-level **monitor** with **condition variables** (whose
`signal` is *lost* if nobody waits — hence `while`, not `if`). Finally we fully
worked the four classics: **Producer–Consumer** (empty/full/mutex, and why the
`wait` order matters), **Readers–Writers** (first/last reader, writer starvation),
**Dining Philosophers** (circular-wait deadlock + fixes), and **Sleeping Barber**.

That last deadlock in Dining Philosophers is the perfect bridge: synchronization
done wrong *creates* deadlock. **Module 8 — Deadlocks** studies exactly that — the
four conditions that cause it, how to detect and avoid it (Banker's algorithm), and
how to recover.

> **You have mastered this module when** you can: state the three CS requirements;
> trace a counter race and explain the lost update; write Peterson's and justify
> all three properties; contrast test-and-set with compare-and-swap; explain
> spinlock vs blocking mutex and semaphore vs monitor vs mutex; and write the
> semaphore solutions to Producer–Consumer, Readers–Writers, Dining Philosophers,
> and Sleeping Barber — including *why* the Producer–Consumer `wait` order prevents
> deadlock — all without notes.
