---
title: "Module 5 — Threads"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — Threads

> **Where this module sits.**
> Module 4 gave us the **process** — powerful but **heavy**: creating one, switching
> to one, and making two of them talk (IPC) all cost real time. Yet a single program
> often needs to do **many things at once** — a browser rendering a page *while*
> downloading images *while* running JavaScript. The answer is the **thread**: a
> lightweight unit of execution **inside** a process that **shares its memory** with
> its siblings. Threads make concurrency cheap, but sharing memory is exactly what
> makes **synchronization (M7)** necessary, and how threads are mapped to the CPU
> shapes **scheduling (M6)**. This module covers **thread vs process**, **user vs
> kernel threads**, the **multithreading models**, **pthreads**, **thread pools**,
> and the **concurrency-vs-parallelism** distinction every interviewer asks about.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★★★★     | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **thread vs process** and
**what threads share vs keep private**; **user-level vs kernel-level threads**
(pros/cons, the blocking-call problem); the **multithreading models** (many-to-one,
one-to-one, many-to-many); **benefits of threads** (responsiveness, resource
sharing, economy, scalability); **TCB vs PCB**; **pthreads** create/join;
**thread pools**; **concurrency vs parallelism**.

---

## 5.1 What Is a Thread? (first principles)

A **thread** is a **single sequential flow of execution within a process** — it has
its own **program counter, registers, and stack**, but **shares the process's code,
data (globals), heap, and open files** with the other threads of that process.

- A traditional **("heavyweight") process has one thread**.
- A **multithreaded process** has several threads, all running the same program's
  code but at **different points**, sharing the same memory.

> **Memory hook:** a **process is an office; threads are the workers in it.** They
> share the **same room, filing cabinets, and whiteboard** (code, globals, heap,
> files) but each has **their own desk and notepad** (stack, registers, PC). Workers
> get more done in parallel — but if two scribble on the whiteboard at once, you get
> chaos (**race conditions** → M7).

### MCQs

1. What is a thread? → a **flow of execution within a process** (own PC/registers/
   stack, shared memory).
2. How many threads does a classic process have? → **one**.
3. Threads of one process share which memory? → **code, data (globals), heap, files**.

---

## 5.2 Thread vs Process — What's Shared, What's Private

The single most-tested table in this module: **what threads share** (because they
live inside one address space) versus **what each thread owns privately**.

![Thread vs process memory: a process holds one code/data/heap/files region shared by all its threads; each thread keeps a private stack, registers, and program counter.](images/38_thread_vs_process.png)

| Resource | Shared across threads? | Why |
|---|:---:|---|
| **Code / text** | **Shared** | all threads run the same program |
| **Global / static data** | **Shared** | one copy of globals (source of races!) |
| **Heap** (`malloc`) | **Shared** | one heap per process |
| **Open files / sockets** | **Shared** | shared file-descriptor table |
| **Program counter (PC)** | **Private** | each thread is at a different instruction |
| **CPU registers** | **Private** | each thread has its own working state |
| **Stack** | **Private** | each has its own call frames / locals |
| **Thread ID** | **Private** | each thread is individually identifiable |

> **The core trade-off in one line:** **processes are isolated** (safe, but talking
> needs IPC and switching is expensive); **threads share memory** (fast, easy to
> share data — but you *must* synchronize, or globals corrupt).

### Cost comparison

| | Process | Thread |
|---|---|---|
| **Creation** | expensive (new address space, PCB) | cheap (shares address space) |
| **Context switch** | expensive (change page tables, flush TLB) | cheap (same address space) |
| **Communication** | via **IPC** (pipes, shm) | via **shared memory directly** |
| **Isolation / safety** | strong (one crash ≠ others) | weak (a bad thread can crash all) |

### MCQs

1. What do threads keep **private**? → **stack, registers, PC** (and thread ID).
2. What do threads **share**? → **code, globals, heap, open files**.
3. Why is a thread switch cheaper than a process switch? → **same address space**
   (no page-table change / TLB flush).
4. Why do threads need synchronization but separate processes need it less? →
   threads **share global memory** (races).

---

## 5.3 Benefits of Threads (the "why")

Textbooks (Silberschatz) list **four** classic benefits — memorize them:

1. **Responsiveness** — one thread can keep the **UI responsive** while another does
   slow work (a download, a computation). The app doesn't "freeze."
2. **Resource sharing** — threads **share memory and files by default**, so they
   exchange data **without** the setup cost of IPC (unlike separate processes).
3. **Economy** — creating and context-switching threads is **far cheaper** than
   processes (no new address space). "Threads are lightweight."
4. **Scalability (parallelism)** — on a **multicore** CPU, different threads run on
   **different cores at the same time**, so a multithreaded program actually gets
   faster with more cores (a single-threaded one cannot).

> **Memory hook:** **"R-R-E-S"** — **R**esponsiveness, **R**esource sharing,
> **E**conomy, **S**calability.

### MCQs

1. Four benefits of threads? → **responsiveness, resource sharing, economy,
   scalability**.
2. Which benefit needs multiple cores? → **scalability / parallelism**.
3. Why "economy"? → cheaper **creation and context switch** than processes.

---

## 5.4 Concurrency vs Parallelism (the interview classic)

These two words are **not** synonyms, and mixing them up is a classic interview
stumble.

- **Concurrency** = **dealing with** many tasks by **interleaving** them so they all
  make progress. Possible on a **single core** (the CPU rapidly switches between
  threads). It's about **structure** — tasks *in progress* at the same time.
- **Parallelism** = **doing** many tasks **literally at the same instant**, which
  **requires multiple cores/CPUs**. It's about **execution** — tasks *running* at
  the same time.

```text
CONCURRENCY (1 core, interleaved):   PARALLELISM (2 cores, simultaneous):
  core: A B A B A B A B                core0: A A A A
        (switching quickly)            core1: B B B B
  "in progress together"              "running together"
```

> **Rob Pike's line:** *"Concurrency is about **dealing with** lots of things at
> once; parallelism is about **doing** lots of things at once."* Concurrency is a
> **design**; parallelism is a **runtime capability**. You can have concurrency
> without parallelism (one core, time-sliced), and parallelism is achieved by
> **running concurrent tasks on multiple cores**.

### MCQs

1. Concurrency vs parallelism? → **interleaving (progress together, 1 core ok)** vs
   **simultaneous execution (needs multiple cores)**.
2. Can you have concurrency on a single core? → **yes** (time-slicing).
3. What does true parallelism require? → **multiple cores/CPUs**.

---

## 5.5 User-Level vs Kernel-Level Threads

Threads can be managed in **two places**: entirely in a **user-space library**
(kernel unaware), or **by the kernel itself**. This distinction drives everything
about the multithreading models.

### User-level threads (ULT)

Managed by a **thread library in user space**; the **kernel sees only one process**
and knows nothing about the threads.

- **Pros:** **very fast** create/switch/schedule (no kernel/mode switch — it's just
  a function call in the library); **portable** (works even if the OS has no thread
  support).
- **Cons:** if **one thread makes a blocking system call, the *whole process*
  blocks** (the kernel blocks the one entity it sees). Cannot use **multiple cores**
  in parallel (the kernel schedules the single process on one core).

### Kernel-level threads (KLT)

Managed **directly by the OS kernel**; the kernel schedules **each thread** and
knows about all of them.

- **Pros:** if one thread blocks, **others keep running**; threads can run on
  **different cores in parallel** (true multicore use).
- **Cons:** **more overhead** — creating/switching a thread requires a **system call
  (mode switch)** into the kernel, so it's heavier than a ULT operation.

| | User-level (ULT) | Kernel-level (KLT) |
|---|---|---|
| **Managed by** | user-space library | the OS kernel |
| **Kernel aware?** | no (sees 1 process) | yes (schedules each thread) |
| **Switch speed** | very fast (no mode switch) | slower (system call) |
| **One thread blocks →** | **whole process blocks** | **only that thread blocks** |
| **True parallelism (multicore)?** | **no** | **yes** |

> **Memory hook:** **ULT = fast but blind** (kernel can't help it — one blocking
> call sinks the ship). **KLT = smart but heavier** (kernel manages each thread, so
> it can keep others running and spread them across cores). Modern OSes (Linux,
> Windows) use **kernel threads** so a blocking call and multicore both work.

### MCQs

1. In ULTs, what happens when one thread makes a blocking syscall? → the **whole
   process blocks**.
2. Which thread type can run truly in parallel on multiple cores? → **kernel-level**.
3. Which is faster to switch, and why? → **user-level** (no kernel mode switch).
4. Which does Linux/Windows use? → **kernel-level** threads.

---

## 5.6 Multithreading Models

Because there are **user** threads and **kernel** threads, we must decide **how many
user threads map onto how many kernel threads**. Three models — **a very common
GATE/interview figure.**

![Multithreading models: many-to-one maps many user threads to one kernel thread; one-to-one maps each user thread to its own kernel thread; many-to-many multiplexes M user threads onto N kernel threads.](images/39_threading_models.png)

### Many-to-One

Many **user** threads → **one** kernel thread.

- Thread management is in user space (fast), but **one blocking call blocks all**,
  and **no multicore parallelism** (only one kernel thread runs at a time).
- **Example:** old "green threads" (early Java, GNU Portable Threads).

### One-to-One

Each **user** thread → **its own** kernel thread.

- **True parallelism** and one thread blocking **doesn't** block others.
- **Cost:** each user thread needs a kernel thread, so creating many is expensive;
  OSes cap the number.
- **Example:** **Linux** (via `clone`/NPTL) and **Windows** — the **dominant model
  today**.

### Many-to-Many

**M** user threads multiplexed onto **N** kernel threads (N ≤ M).

- Best of both: create **many** user threads, while the kernel runs several in
  **parallel**; if one blocks, another can be scheduled.
- More complex to implement. A variant is the **two-level model** (many-to-many plus
  the option to bind a user thread to a kernel thread).
- **Example:** Solaris (older), Windows fibers, Go's goroutine scheduler is a
  spiritual M:N design.

| Model | Parallel? | One blocks → all block? | Note |
|---|:---:|:---:|---|
| **Many-to-one** | no | **yes** | simple, obsolete (green threads) |
| **One-to-one** | **yes** | no | **Linux/Windows**, may limit count |
| **Many-to-many** | **yes** | no | flexible, complex (M user → N kernel) |

> **Memory hook:** count the arrows — **many→one** (all in one boat, no parallelism),
> **one→one** (everyone gets a car, but cars are pricey), **many→many** (a
> **carpool** — many riders, a few shared cars, flexible).

### MCQs

1. Model used by Linux and Windows? → **one-to-one**.
2. Which model has no multicore parallelism? → **many-to-one**.
3. In many-to-one, one blocking call causes? → **all threads block**.
4. Which model multiplexes M user threads onto N kernel threads? → **many-to-many**.

---

## 5.7 TCB vs PCB

Just as each process has a **PCB (Module 4)**, each thread has a **Thread Control
Block (TCB)** — the kernel's record of one thread's state.

| | **PCB** (per process) | **TCB** (per thread) |
|---|---|---|
| **Holds** | PID, **memory (page tables)**, open files, accounting, **+ shared state** | thread ID, **PC, registers, stack pointer**, thread state, priority |
| **Owns memory?** | **yes** — the whole address space | **no** — shares the process's memory |
| **How many** | one per process | one per **thread** (a process has ≥1) |

> **Key idea:** the TCB stores **only what is private to a thread** (PC, registers,
> stack). Everything shared — the address space, page tables, open files — stays in
> the **PCB**. That's *why* a thread switch is cheap: you swap a small TCB, not the
> whole memory map.

### MCQs

1. Per-thread kernel structure? → **TCB** (Thread Control Block).
2. Does a TCB own the address space? → **no** (the PCB does; threads share it).
3. What does the TCB store? → **thread ID, PC, registers, stack pointer, state**.

---

## 5.8 Thread Lifecycle

A thread moves through states much like a process:

```text
   NEW ──start──▶ RUNNABLE ──scheduled──▶ RUNNING ──finish──▶ TERMINATED
                    ▲   ▲                    │  │
                    │   └───unblock──────────┘  │
                    │    (I/O/lock ready)        ▼
                    └──────────────────────── BLOCKED / WAITING
                          (wait on I/O, lock, join, sleep)
```

- **New** — created but not yet started.
- **Runnable / Ready** — eligible to run, waiting for a CPU.
- **Running** — executing on a core.
- **Blocked / Waiting** — waiting on I/O, a **lock/mutex**, `join`, or `sleep`.
- **Terminated** — finished (or cancelled); its result may be collected via `join`.

(These map cleanly onto the **process states** of Module 4 — threads are scheduled
by the same machinery.)

### MCQs

1. A thread waiting for a mutex is in which state? → **blocked / waiting**.
2. A thread eligible to run but not on a CPU yet? → **runnable / ready**.

---

## 5.9 POSIX Threads (pthreads)

**Pthreads** is the **POSIX standard API** for threads on UNIX/Linux (it is a
*specification*; Linux implements it as **one-to-one** kernel threads via NPTL).
The two calls you must know are **create** and **join**.

```c
#include <stdio.h>
#include <pthread.h>

void *worker(void *arg) {              // the function each thread runs
    long id = (long)arg;
    printf("Hello from thread %ld\n", id);
    return (void *)(id * id);          // return a value to whoever joins us
}

int main(void) {
    pthread_t t[3];
    for (long i = 0; i < 3; i++)
        pthread_create(&t[i], NULL, worker, (void *)i);   // spawn 3 threads

    for (int i = 0; i < 3; i++) {
        void *ret;
        pthread_join(t[i], &ret);      // wait for each thread, collect its result
        printf("thread %d returned %ld\n", i, (long)ret);
    }
    return 0;                          // (compile with:  gcc file.c -pthread)
}
```

- **`pthread_create(&tid, attr, start_routine, arg)`** — creates a new thread that
  runs `start_routine(arg)`; the thread ID is written to `tid`. `attr` = `NULL` for
  defaults.
- **`pthread_join(tid, &retval)`** — **blocks** until thread `tid` finishes and
  collects its return value (the thread analogue of `wait()` for processes). Joining
  also **frees** the thread's resources — the equivalent of "reaping."
- Others: **`pthread_exit()`** (terminate the calling thread),
  **`pthread_detach()`** (auto-reclaim on exit, no join needed),
  **`pthread_mutex_*`** (locks — Module 7).

> **Memory hook:** `create` = `fork` for threads; `join` = `wait` for threads. But
> unlike `fork` (which copies memory), a new thread **shares** the process's memory —
> the whole point.

### MCQs

1. Pthread call to create a thread? → **`pthread_create`**.
2. Pthread analogue of `wait()`? → **`pthread_join`**.
3. Flag to compile a pthreads program with gcc? → **`-pthread`**.
4. How to avoid needing `join` for cleanup? → **`pthread_detach`**.

---

## 5.10 Thread Pools

Creating a **new thread per task** is cheap-ish but not free, and **unbounded**
thread creation can exhaust memory and thrash the scheduler. A **thread pool**
solves this: create a **fixed set of worker threads up front**, and feed them tasks
from a **queue**; when a worker finishes a task it grabs the next one.

```text
   incoming tasks ─▶ [ task queue ]
                         │  │  │
                    ┌────┘  │  └────┐
                 worker1  worker2  worker3   ← fixed pool, reused for every task
```

**Why a thread pool:**

1. **Faster** — no create/destroy cost per task; threads are **reused**.
2. **Bounded resource use** — a hard cap on live threads prevents **overload** (a
   server under a request flood won't spawn a million threads and die).
3. **Decouples** task submission from execution (a clean producer/consumer design).

> **Memory hook:** a thread pool is a **taxi rank** — a fixed fleet of drivers
> (threads) waiting; a rider (task) takes the next free taxi and returns it after
> the trip. No hiring/firing a driver per ride.

> **Backend reality:** every web/app server uses a pool — Java's
> `ExecutorService`/`ThreadPoolExecutor`, Tomcat's request threads, nginx/Postgres
> worker pools. **Pool size ≈ number of cores** for CPU-bound work; **larger** for
> I/O-bound work (threads spend time blocked, so more can overlap).

### MCQs

1. Why use a thread pool? → **reuse threads** (no per-task create cost) and **bound**
   the thread count.
2. Good pool size for CPU-bound work? → roughly the **number of cores**.
3. What structure feeds a pool? → a **task queue** (producer/consumer).

---

## 5.11 Thread Scheduling (brief)

- The OS scheduler (Module 6) schedules **kernel threads** — on a one-to-one system,
  that means it schedules each of your threads directly onto cores.
- **Contention scope:** **PCS (process-contention scope)** — user threads compete
  *within* a process for a kernel thread (many-to-many/many-to-one); **SCS
  (system-contention scope)** — kernel threads compete *system-wide* for a CPU
  (one-to-one, as on Linux/Windows).
- Threads have **priorities**; higher-priority runnable threads are dispatched first
  (details and algorithms are Module 6).

### MCQs

1. What does the OS actually schedule on Linux? → **kernel threads** (one-to-one).
2. PCS vs SCS? → contention **within a process** vs **system-wide** for a CPU.

---

## 5.12 Synchronization — a Teaser to Module 7

The very thing that makes threads powerful — **shared memory** — is also their
danger. If two threads update the **same global** without coordination, the result
depends on **timing**: a **race condition**.

```text
Two threads each run:  counter = counter + 1   (counter starts at 0)
  Thread A: read 0 ......................... write 1
  Thread B: ......... read 0 ... write 1
  Result: counter = 1   (a lost update — should be 2!)
```

The fix is **synchronization**: make the update **atomic** with a **mutex/lock** or
**semaphore**, so only one thread touches the shared data at a time (the **critical
section**).

> **Memory hook:** shared memory is a **shared whiteboard**; without a "one writer at
> a time" rule (a **lock**), two threads scribble over each other and you **lose
> updates**. This is the entire subject of **Module 7 (Process Synchronization)** —
> critical sections, mutexes, semaphores, and deadlock.

### MCQs

1. Two threads updating a shared variable unsafely cause a? → **race condition**.
2. The region of code touching shared data? → the **critical section**.
3. Basic tool to protect it? → a **mutex / lock** (or semaphore).

---

## 5.13 Real-World & Backend Perspectives

- **Servers are thread stories.** Tomcat/Jetty serve each request on a **pooled**
  thread; a slow downstream call blocking a pool thread is why **thread-pool
  exhaustion** is a top production incident.
- **The GIL caveat.** CPython's **Global Interpreter Lock** means Python threads
  give **concurrency but not CPU parallelism** — use **processes** (or async) for
  CPU-bound work. A perfect illustration of §5.4.
- **Async vs threads.** Node.js/nginx use a **single-threaded event loop** for I/O
  concurrency (avoiding per-request thread cost and locks) — a different point on
  the same concurrency spectrum.
- **Goroutines / green threads return.** Go multiplexes millions of **goroutines**
  onto a few OS threads (an M:N design), reviving user-level threading with a smart
  runtime scheduler.

---

## 5.14 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** "concurrency = parallelism." **No** — concurrency is interleaving
  (single core ok); parallelism needs **multiple cores**.
- **Mistake:** thinking threads are always faster. Shared state needs **locks**, and
  locking can serialize threads (and cause **deadlock**, M7). For CPU-bound Python,
  threads don't help (GIL).
- **Mistake:** forgetting to **`join`/`detach`** threads → resource leaks (the thread
  analogue of a zombie).
- **Edge case (isolation):** one thread's **segfault crashes the whole process**
  (shared address space) — unlike separate processes. Safety vs speed trade-off.
- **Edge case (ULT):** in a pure user-level (many-to-one) system, a single blocking
  syscall freezes **every** thread — the reason one-to-one won.
- **Tradeoff:** **threads** (fast, shared memory, need sync, weak isolation) vs
  **processes** (isolated, safe, expensive, IPC to talk).

---

## 5.15 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** thread-vs-process (shared vs private), benefits (RRES),
  user-vs-kernel threads, and the three models are common MCQs.
- **GATE:** the **multithreading-models** figure, ULT-vs-KLT properties (the blocking
  and parallelism points), and PCS-vs-SCS appear regularly.
- **Interview (backend/systems):** "Thread vs process?" (address-space sharing),
  "Concurrency vs parallelism?", "Why a thread pool?", "What's a race condition and
  how do you prevent it?" (mutex → M7), "Why doesn't Python thread well for CPU
  work?" (GIL).
- **Coding:** write a `pthread_create`/`pthread_join` snippet; reason about a race on
  a shared counter and fix it with a mutex.

---

## 5.16 Concept Checks & MCQs (test yourself)

1. Thread vs process in one line? → thread = **flow of execution sharing a process's
   memory**; process = **isolated address space**.
2. What do threads share / keep private? → share **code/globals/heap/files**; private
   **stack/registers/PC**.
3. Four benefits of threads? → **responsiveness, resource sharing, economy,
   scalability** (RRES).
4. Concurrency vs parallelism? → **interleaving (1 core ok)** vs **simultaneous
   (needs multiple cores)**.
5. ULT: one blocking call → ? → **whole process blocks**.
6. Which thread type gives true multicore parallelism? → **kernel-level**.
7. Model used by Linux/Windows? → **one-to-one**.
8. Model with no parallelism? → **many-to-one**.
9. Per-thread control block? → **TCB** (shares PCB's memory).
10. Pthread create / join calls? → **`pthread_create`** / **`pthread_join`**.
11. Why use a thread pool? → **reuse** threads, **bound** the count.
12. Why is a thread switch cheaper than a process switch? → **same address space**.
13. Two threads clobbering a shared variable → ? → **race condition** (fix: mutex).
14. Does a TCB own memory? → **no** (the PCB does).
15. Good thread-pool size for CPU-bound work? → **≈ number of cores**.

**True/False**
- Threads of a process share the heap. → **True**.
- Each thread has its own stack. → **True**.
- Concurrency requires multiple cores. → **False** (parallelism does).
- In many-to-one, threads run in parallel on many cores. → **False**.
- A crashing thread can take down the whole process. → **True** (shared address
  space).
- `pthread_join` is the thread analogue of `wait()`. → **True**.

---

## 5.17 One-Page Revision Sheet

```
THREAD = flow of execution INSIDE a process. own PC/REGISTERS/STACK ; SHARES code/data(globals)/
  heap/open-files with sibling threads. classic process = 1 thread.

SHARED vs PRIVATE:  shared = CODE, GLOBALS/STATIC, HEAP, FILES.  private = STACK, REGISTERS, PC, TID.
  => threads cheap to create/switch (same address space) BUT need SYNCHRONIZATION (shared globals).

BENEFITS (RRES): Responsiveness, Resource sharing, Economy(cheap), Scalability(multicore parallel).

CONCURRENCY vs PARALLELISM:
  concurrency = DEALING WITH many (interleave; 1 core OK) ; parallelism = DOING many (needs >1 core).
  concurrency = design ; parallelism = runtime. concurrency-without-parallelism = time-slice on 1 core.

USER-LEVEL (ULT): lib in user space, kernel sees 1 process. FAST switch, portable.
  BUT 1 blocking syscall blocks ALL ; NO multicore parallelism.
KERNEL-LEVEL (KLT): kernel schedules each thread. others run if one blocks ; TRUE parallelism.
  BUT heavier (syscall/mode switch to create/switch). Linux/Windows use KLT.

MODELS:
  many-to-one  many ULT -> 1 KLT     : no parallel, one blocks->all (green threads)
  one-to-one   each ULT -> own KLT    : parallel, one blocks!=all ; LINUX/WINDOWS ; may cap count
  many-to-many M ULT -> N KLT (N<=M)  : flexible, parallel (Solaris old; Go-like)

TCB vs PCB: PCB=per process (owns address space, page tables, files). TCB=per thread (PC, regs,
  stack ptr, state) — does NOT own memory. thread switch = swap small TCB => cheap.

LIFECYCLE: new -> runnable -> running -> (blocked on I/O/lock/join) -> ... -> terminated.

PTHREADS (POSIX; Linux = one-to-one/NPTL):
  pthread_create(&tid, attr, fn, arg)   // = fork for threads (but SHARES memory)
  pthread_join(tid, &ret)               // = wait for threads (blocks, collects result, reaps)
  pthread_exit / pthread_detach / pthread_mutex_*   // compile: gcc x.c -pthread

THREAD POOL: fixed worker set + task queue. reuse (no per-task create), BOUND count (no overload).
  size ~= #cores for CPU-bound ; larger for I/O-bound.

SYNC TEASER (M7): shared global + no lock => RACE CONDITION (lost update). protect CRITICAL SECTION
  with MUTEX/semaphore. deadlock etc = Module 7.

CAVEATS: Python GIL => threads = concurrency not CPU parallelism (use processes). one thread crash
  kills whole process (shared address space).
```

### Flash cards

| Front | Back |
|-------|------|
| Thread shares what? | Code, globals, heap, files |
| Thread keeps private? | Stack, registers, PC (+ TID) |
| Four thread benefits? | Responsiveness, resource sharing, economy, scalability |
| Concurrency vs parallelism? | Interleave (1 core ok) vs simultaneous (needs cores) |
| ULT: one thread blocks → ? | Whole process blocks |
| Model of Linux/Windows? | One-to-one |
| Model with no parallelism? | Many-to-one |
| Per-thread control block? | TCB (shares PCB's memory) |
| Create / join a pthread? | pthread_create / pthread_join |
| Why a thread pool? | Reuse threads + bound the count |
| Unsafe shared update? | Race condition (fix: mutex) |
| Why thread switch is cheap? | Same address space (no TLB flush) |

### Spaced repetition
- **24-hour:** recite shared-vs-private and the three models; state concurrency vs
  parallelism in one sentence each.
- **7-day:** explain ULT-vs-KLT with the blocking and multicore points; write a
  `pthread_create`/`join` snippet from memory.
- **30-day:** draw the thread-vs-process memory picture and the multithreading
  models; explain a race condition and its fix (bridge to M7).

---

## 5.18 Summary

A **thread** is a lightweight flow of execution **inside** a process: it keeps its
own **PC, registers, and stack** but **shares the process's code, globals, heap, and
files** with sibling threads. That sharing gives the four benefits — **responsiveness,
resource sharing, economy, and scalability (RRES)** — and makes creation and context
switching **far cheaper** than for processes (swap a small **TCB**, not the whole
address space held in the **PCB**). We separated **concurrency** (interleaving,
possible on one core) from **parallelism** (simultaneous, needs multiple cores), and
**user-level threads** (fast but a blocking call freezes all, no multicore) from
**kernel-level threads** (heavier but truly parallel — what Linux/Windows use). The
**multithreading models** map user to kernel threads — **many-to-one** (no
parallelism), **one-to-one** (the modern default), and **many-to-many** (flexible
M:N). We wrote **pthreads** (`create`/`join`), saw why **thread pools** reuse and
bound threads, and previewed the price of shared memory: **race conditions**, fixed
by synchronization.

Next, **Module 6 — CPU Scheduling** decides *which* ready thread runs next and for
how long (FCFS, SJF, Round Robin, priority — with Gantt charts and waiting-time
numericals), and **Module 7 — Process Synchronization** tackles the race conditions
this module warned about (critical sections, mutexes, semaphores, deadlock).

> **You have mastered this module when** you can: list exactly what threads share vs
> keep private and why that makes them cheap; state the four benefits (RRES);
> distinguish concurrency from parallelism and ULT from KLT (blocking + multicore);
> draw the three multithreading models; write a `pthread_create`/`pthread_join`
> snippet; explain why thread pools exist; and describe a race condition and its fix
> — all without notes.
