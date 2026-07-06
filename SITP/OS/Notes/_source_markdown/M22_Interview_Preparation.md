---
title: "Module 22 — Interview Preparation (OS for FAANG / Backend / AI-Infra)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 22 — Interview Preparation

> **Where this module sits.**
> Exams (Module 21) test whether you can *compute*. Interviews test whether you
> *understand* — **why** SJF is optimal, **why** a mutex differs from a semaphore,
> **what actually happens** when you type `ls` or call `fork()`, and **how you'd
> debug** a slow or leaking production server. This capstone collects the OS
> questions FAANG, backend, and AI-infrastructure interviews actually ask —
> **~70 Q&A with concise model answers** grouped by area, the **classic
> scenario/debugging** questions, **production war-stories**, per-company flavour,
> and the **tools you should name-drop** (`top`, `vmstat`, `iostat`, `strace`,
> `perf`). Learn to *explain*, not just recite.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★      | ★★     | ★       | ★★★★★     | ★★★★★   |

**Most-asked interview concepts:** process vs thread; how `fork()`/`exec()` work and
what happens on `ls`; **race conditions, mutex vs semaphore, deadlock** (and how to
avoid one); **virtual memory, paging, page faults, TLB**; context switch cost;
user vs kernel mode & system calls; **zombie/orphan** processes; "the app is slow —
diagnose it"; memory leaks; and the Linux tools to find all of the above.

---

## 22.1 What OS Topics Interviews Actually Ask

OS shows up in interviews three ways: **direct concept questions** (screening and
systems roles), **"what happens when…" walkthroughs** (senior/systems), and
**debugging/production scenarios** (backend, SRE, infra). Coverage clusters here:

![The OS interview map: a core of processes/threads, synchronization/deadlock, memory/virtual-memory, scheduling, and file/IO systems — surrounded by Linux fluency, systems-design flavour, and production debugging scenarios.](images/201_os_interview_map.png)

| Area | Why interviewers ask | Roles that lean on it |
|------|----------------------|-----------------------|
| **Processes & threads** | concurrency is everywhere in backends | all SWE, backend |
| **Synchronization & deadlock** | multithreaded correctness bugs are costly | backend, systems |
| **Memory & virtual memory** | leaks/OOM/performance in production | backend, infra, AI |
| **Scheduling** | latency, tail latency, fairness | systems, SRE |
| **File systems & I/O** | storage, throughput, durability | infra, data, storage |
| **Linux fluency** | every server is Linux | all backend/infra/SRE |
| **Systems-design flavour** | design a thread pool / cache / rate limiter | senior SWE |
| **Debugging scenarios** | "app is slow / leaking" — real ops | SRE, backend, infra |

> **The bar isn't recall — it's reasoning.** "Define a mutex" is a warm-up; the real
> question is "why would a spinlock beat a mutex here?" Always answer with the
> **mechanism + the trade-off**.

---

## 22.2 Processes & Threads

1. **Process vs thread?** A **process** is a program in execution with its **own**
   address space (code, data, heap), file table, and PID. A **thread** is a unit of
   execution *inside* a process; threads **share** the address space, heap, and open
   files but each has its **own stack, registers, and program counter**. Threads are
   cheaper to create and switch (no address-space swap).

2. **Why use threads over processes?** Lower creation/switch cost, easy **data
   sharing** (same address space), better responsiveness. The cost: **shared state
   → synchronization bugs** (races, deadlocks). Processes give **isolation** (a
   crash in one doesn't corrupt another) at the price of costlier IPC.

3. **What is in a PCB (Process Control Block)?** PID, process **state**, **program
   counter**, CPU **registers**, scheduling info (priority), memory-management info
   (page tables/base-limit), open-file table, accounting. It *is* a process's saved
   context.

4. **What is a context switch and why is it expensive?** Saving one process/thread's
   CPU state to its PCB and loading another's. It's pure overhead: no useful work,
   plus indirect cost from **cache and TLB flushes** (a cold cache after the switch).

5. **Process states?** new → **ready** → **running** → **waiting/blocked** →
   **terminated**. Running→ready is a **preemption/timeout**; running→waiting is an
   **I/O or event wait**; waiting→ready is **I/O completion**.

6. **Explain `fork()`.** It creates a **child** process that is a near-copy of the
   parent. It returns **0 in the child**, the **child's PID in the parent**, and
   **−1 on failure**. Parent and child then run concurrently from the point of the
   call. Modern kernels use **copy-on-write** so pages are shared until one writes.

7. **What does `exec()` do?** It **replaces** the current process image with a new
   program — same PID, new code/data. The classic pattern is **`fork()` then
   `exec()`**: fork to make a new process, exec to run a different program in it
   (this is how a shell launches commands).

8. **What is a zombie process?** A child that has **terminated** but whose exit
   status hasn't been **reaped** by the parent (`wait()`/`waitpid()`). It holds only
   a PCB entry. Too many zombies **exhaust the PID table**. Fix: the parent must
   `wait()`; or handle `SIGCHLD`.

9. **What is an orphan process?** A process whose **parent died first**. It's
   **re-parented to `init`/PID 1** (or a subreaper), which reaps it when it exits.
   Orphans are harmless; zombies pile up.

10. **How do processes communicate (IPC)?** **Pipes / named pipes (FIFOs)**,
    **message queues**, **shared memory** (fastest, needs synchronization),
    **sockets** (also across machines), **signals** (async notifications). Shared
    memory is fastest because there's no kernel copy per message.

11. **User thread vs kernel thread?** **User-level** threads are managed by a
    library, invisible to the kernel — fast to switch, but one blocking syscall
    blocks *all* of them and they can't use multiple cores. **Kernel-level** threads
    are scheduled by the OS — true parallelism and independent blocking, at higher
    switch cost. Real systems map user→kernel (1:1, M:N).

12. **What's a daemon?** A long-running **background** process (often re-parented to
    init) providing a service (e.g. `sshd`, `cron`). No controlling terminal.

---

## 22.3 Synchronization & Deadlock

13. **What is a race condition?** When the result depends on the **timing/order** of
    concurrent accesses to **shared** data (e.g. two threads doing `count++`, which
    is read-modify-write, and losing an update). Fix: make the critical section
    **atomic** with a lock/atomic instruction.

14. **What is a critical section, and what must a solution guarantee?** The code that
    touches shared data. A correct solution needs **mutual exclusion** (one at a
    time), **progress** (no unnecessary blocking of a willing entrant), and
    **bounded waiting** (no starvation).

15. **Mutex vs semaphore?** A **mutex** is a lock with **ownership** — only the
    thread that locked it may unlock it; used for mutual exclusion. A **semaphore**
    is a **signalling counter** (no owner) — `wait`/`signal` — used to count
    resources or coordinate order (e.g. producer/consumer). Binary semaphore ≈
    mutex, but the ownership semantics differ.

16. **Binary vs counting semaphore?** Binary = value 0/1 (lock-like); counting =
    value up to *N*, allowing **N** concurrent holders of a resource pool.

17. **What is a spinlock and when is it better than a mutex?** A lock that **busy-
    waits** (spins) instead of sleeping. Better when the critical section is **very
    short** and you're on a **multiprocessor** — spinning wastes fewer cycles than a
    sleep/wake context switch. Bad on a uniprocessor or for long sections (it just
    burns CPU).

18. **What causes deadlock (the four conditions)?** **Mutual exclusion,
    hold-and-wait, no preemption, circular wait** — all four simultaneously. Remove
    any one to *prevent* deadlock.

19. **How do you avoid/prevent deadlock in code?** Impose a **global lock ordering**
    (always acquire locks in the same order — breaks circular wait), use
    **`try-lock` with back-off**, acquire **all locks at once** (breaks
    hold-and-wait), keep critical sections short, or use lock-free structures. At the
    OS level, **Banker's algorithm** is avoidance.

20. **Deadlock vs livelock vs starvation?** **Deadlock** = everyone blocked forever.
    **Livelock** = threads keep changing state in response to each other but make
    **no progress** (two people stepping aside in a corridor). **Starvation** = a
    thread waits indefinitely while others proceed (fixed by **aging**/fairness).

21. **What's a condition variable?** A synchronization primitive to **wait for a
    predicate** to become true, always used **with a mutex**: `wait()` atomically
    releases the mutex and sleeps; a `signal()`/`broadcast()` wakes waiters. Always
    re-check the predicate in a **`while` loop** (spurious wakeups).

22. **Explain the producer–consumer problem.** Producers add to a bounded buffer,
    consumers remove. Use a **mutex** for buffer access plus two counting semaphores:
    **`empty`** (free slots) and **`full`** (filled slots). Producer:
    `wait(empty); lock; add; unlock; signal(full)`. Consumer mirrors it.

23. **Readers–writers problem?** Many readers may read concurrently, but a writer
    needs **exclusive** access. Trade-off: a reader-preference solution can **starve
    writers**; a writer-preference or fair variant fixes it.

24. **Dining philosophers — why does it deadlock and how to fix?** Each grabs the
    left fork then waits on the right → **circular wait**. Fixes: **resource
    ordering** (number forks, always pick lower first), allow **at most N−1** at the
    table, or use an **arbitrator**/waiter.

25. **What's a memory barrier / why does `volatile` not make code thread-safe?**
    Compilers/CPUs reorder memory operations; a **memory barrier** enforces ordering.
    `volatile` (in C/C++) only prevents *compiler caching* of a value — it does **not**
    provide atomicity or ordering guarantees, so it's not a substitute for a lock or
    atomic.

26. **What is priority inversion?** A high-priority task waits on a lock held by a
    low-priority task that itself is preempted by a medium one — the high task is
    effectively blocked by the medium. Fix: **priority inheritance** (the low task
    temporarily inherits the high priority). (Famous in the Mars Pathfinder bug.)

---

## 22.4 Memory & Virtual Memory

27. **What is virtual memory?** An abstraction giving each process its **own large,
    contiguous** address space, decoupled from physical RAM. Pages live in RAM or on
    **disk (swap)**; the MMU translates virtual→physical. Benefits: **isolation**,
    running programs **larger than RAM**, and efficient sharing (COW).

28. **Explain paging and address translation.** The virtual address splits into a
    **page number** + **offset**. The page number indexes the **page table** to get
    a **frame number**; frame + offset = physical address. A **TLB** caches recent
    translations to skip the page-table lookup.

29. **What is a page fault and what happens on one?** A reference to a page **not in
    RAM**. The MMU traps to the kernel, which finds the page on disk, picks a **free
    frame** (or **evicts** one via the replacement policy, writing it back if
    **dirty**), reads the page in, updates the page table, and **restarts** the
    instruction.

30. **What is a TLB and why does it matter?** Translation Lookaside Buffer — a small
    cache of page-table entries. A **hit** avoids the extra memory access for the
    page table, so it's critical to performance; a context switch may **flush** it
    (hence the cost).

31. **Paging vs segmentation?** Paging = **fixed-size** pages/frames, no external
    fragmentation, invisible to the programmer. Segmentation = **variable-size**
    logical units (code, stack, heap) that match program structure but cause
    **external fragmentation**. Real systems often combine (paged segments).

32. **Internal vs external fragmentation?** **Internal** = unused space **inside** an
    allocated block (last page half-empty). **External** = enough total free memory
    but it's **scattered** in unusable gaps (fixed by **compaction**). Paging causes
    internal; variable partitions/segmentation cause external.

33. **What is thrashing?** When processes have too few frames, the page-fault rate
    explodes and the CPU spends nearly all its time **paging**, not computing.
    Detect via low CPU + high paging; fix by **reducing multiprogramming** or using
    the **working-set model** to give each process enough frames.

34. **What is copy-on-write (COW)?** After `fork()`, parent and child **share** pages
    marked read-only; on the **first write**, the kernel copies just that page. Makes
    `fork()` cheap and avoids copying memory that's never modified.

35. **Demand paging vs pre-paging?** Demand paging loads a page **only when
    referenced** (lazy) — minimal I/O but a fault on first touch. Pre-paging loads
    pages it expects to need **ahead of time** — fewer faults if the guess is right,
    wasted I/O if wrong.

36. **How does `malloc` get memory from the OS?** Via **`brk`/`sbrk`** (grow the
    heap) or **`mmap`** (map anonymous pages) system calls. `malloc` manages a
    user-space **free list** and only calls the kernel when it needs more; freed
    memory is often **not returned** to the OS immediately (hence RSS staying high).

37. **Stack vs heap?** **Stack**: automatic, LIFO, per-thread, fast, fixed-ish size,
    holds locals/return addresses. **Heap**: dynamic (`malloc`/`new`), shared across
    threads, manually or GC-managed, flexible size, slower, prone to fragmentation
    and leaks.

38. **What's the difference between `mmap` and `read`/`write` for file I/O?** `mmap`
    maps a file into the address space so you access it like memory (page faults pull
    data in) — great for random access and sharing. `read`/`write` copy through a
    kernel buffer per call — simpler, better for streaming/sequential.

39. **Which page-replacement policy is best, and why not FIFO?** **LRU** approximates
    the optimal well (temporal locality) but needs bookkeeping; real kernels use
    **clock/second-chance**. **FIFO** can suffer **Belady's anomaly** (more frames →
    more faults) and evicts hot pages, so it's avoided.

40. **What is an OOM (out-of-memory) situation on Linux?** When memory + swap is
    exhausted, the kernel's **OOM killer** picks a victim (by an `oom_score`) and
    kills it. Overcommit (`mmap` more than RAM) makes this possible. Backend fix:
    set limits (cgroups), fix leaks, add swap/RAM.

---

## 22.5 CPU Scheduling

41. **Preemptive vs non-preemptive scheduling?** **Preemptive** can take the CPU from
    a running process (on a timer or a higher-priority arrival) — better
    responsiveness, needs careful synchronization. **Non-preemptive** runs a process
    until it blocks or finishes — simpler, but a long job hurts everyone (convoy).

42. **Why is SJF optimal, and what's its catch?** Shortest Job First minimises
    **average waiting time** (short jobs don't queue behind long ones). Catch: you
    can't know burst lengths in advance (estimate via **exponential averaging**), and
    it can **starve** long jobs.

43. **How does Round Robin pick its time quantum?** Too **large** → behaves like
    FCFS (poor responsiveness); too **small** → excessive **context-switch
    overhead**. Rule of thumb: quantum somewhat larger than a typical interaction so
    ~80% of bursts finish within one quantum.

44. **What is a multilevel feedback queue?** Multiple ready queues with different
    priorities/quanta; a process that uses too much CPU is **demoted** (CPU-bound),
    while I/O-bound/interactive jobs stay high. Approximates SJF **without** knowing
    burst lengths — close to how real schedulers behave.

45. **How does the Linux scheduler work (high level)?** The **CFS (Completely Fair
    Scheduler)** tracks each task's **virtual runtime** and always runs the task with
    the smallest vruntime, kept in a **red-black tree** — approximating "give every
    task a fair share of CPU". Real-time classes (`SCHED_FIFO`/`RR`) sit above CFS.

46. **What metric matters for interactive apps vs batch?** Interactive →
    **response time / tail latency**; batch → **throughput / turnaround**. You tune
    the scheduler and quantum to the workload's goal.

47. **What causes high tail latency (p99) even at low average load?** Head-of-line
    blocking, GC/allocation pauses, **context-switch and lock contention**, a slow
    I/O behind a shared queue, or scheduler starvation of a low-priority thread.
    Diagnose per-request, not by averages.

---

## 22.6 File Systems & Disk / I/O

48. **What is an inode?** A file's **metadata** structure: size, owner, permissions,
    timestamps, link count, and **block pointers** (direct + single/double/triple
    indirect). It does **not** hold the filename — that's a directory entry mapping a
    name → inode number.

49. **What happens to disk blocks when you delete a file?** The directory entry is
    removed and the inode's **link count** drops; when it reaches 0 **and** no
    process has it open, the inode and its data blocks are freed. Data isn't
    physically erased (hence recovery/forensics is possible).

50. **Hard link vs soft (symbolic) link?** A **hard link** is another directory entry
    pointing to the **same inode** (same file, shared link count; can't cross
    filesystems or link directories). A **soft link** is a small file containing a
    **path** to the target — can cross filesystems, breaks if the target moves.

51. **File allocation methods?** **Contiguous** (fast sequential, external frag,
    hard growth), **linked** (no external frag, no random access), **indexed/inode**
    (index block enables random access — used by UNIX). FAT keeps the links in one
    table for faster random access.

52. **What is journaling and why does it matter?** A journaling filesystem (ext4,
    NTFS) writes intended changes to a **log (journal)** first, then applies them, so
    after a crash it **replays/rolls back** the journal instead of a full `fsck`.
    Gives **crash consistency**.

53. **Buffer cache / page cache — what is it?** The kernel caches disk blocks in
    **RAM**; reads hit the cache, writes are buffered and flushed later (**write-back**).
    This is why a second `read` of a file is instant and why `free` shows RAM "used"
    by cache (reclaimable).

54. **Disk scheduling algorithms and their point?** FCFS (fair, lots of seeking),
    **SSTF** (nearest-first, can starve), **SCAN/C-SCAN** (elevator; C-SCAN gives
    uniform waits), LOOK/C-LOOK. Goal: minimise **seek** (head movement). On **SSDs**
    seek ≈ 0, so these matter far less.

55. **Polling vs interrupts vs DMA?** **Polling** = CPU repeatedly checks the device
    (wastes CPU). **Interrupts** = device signals the CPU when ready (efficient).
    **DMA** = a controller moves bulk data device↔memory **without the CPU**, which
    is interrupted only once at completion (best for large transfers).

56. **What is `fsync` and why do databases call it?** `fsync(fd)` forces buffered
    (write-back) data for a file to **actually reach disk**. Databases call it at
    commit for **durability** (the D in ACID) — otherwise a crash loses "written"
    data still sitting in the page cache.

---

## 22.7 Linux Fluency

57. **User mode vs kernel mode?** Two CPU privilege levels. **User mode** can't touch
    hardware directly; **kernel mode** can. Crossing from user to kernel happens via
    a **system call / trap / interrupt**. This dual-mode is the basis of
    **protection**.

58. **What is a system call? Give examples.** The API by which a user program
    requests a kernel service: `read`, `write`, `open`, `close`, `fork`, `exec`,
    `wait`, `mmap`, `brk`, `socket`. It traps into kernel mode, runs the service,
    returns to user mode.

59. **What does the shell do when you run a command?** Parses the line, **`fork()`s**
    a child, the child **`exec()`s** the program, the shell **`wait()`s** (unless
    backgrounded with `&`). Redirection/pipes are set up by manipulating file
    descriptors before `exec`.

60. **Explain the permission bits `rwxr-xr--`.** Three triples: **owner** (rwx),
    **group** (r-x), **others** (r--). r=4, w=2, x=1 → this is **754**. `x` on a
    **directory** means "may enter/traverse".

61. **What is `/proc`?** A **virtual filesystem** exposing kernel and per-process
    state as files: `/proc/<pid>/status`, `/proc/meminfo`, `/proc/cpuinfo`,
    `/proc/<pid>/fd`. Tools like `ps`/`top` read it.

62. **What is a signal? Name a few.** An asynchronous notification to a process:
    `SIGKILL` (9, uncatchable kill), `SIGTERM` (15, polite terminate), `SIGSEGV`
    (invalid memory), `SIGCHLD` (child changed state), `SIGINT` (Ctrl-C),
    `SIGSTOP`/`SIGCONT`. Processes can install **handlers** (except KILL/STOP).

63. **`SIGKILL` vs `SIGTERM`?** `SIGTERM` asks a process to shut down cleanly (it can
    catch it and clean up); `SIGKILL` is forcible and **can't be caught or ignored**.
    Always try TERM first.

64. **What is a file descriptor?** A small integer index into the process's open-file
    table. **0/1/2** are stdin/stdout/stderr. Redirection and pipes work by
    duplicating/replacing these fds (`dup2`).

65. **What are environment variables and how do children get them?** Key–value
    strings in a process's environment (e.g. `PATH`, `HOME`). A child **inherits** a
    copy across `fork`/`exec` — that's how config flows down a process tree.

66. **What does `nice`/priority do?** Adjusts a process's scheduling priority
    (`nice` −20 highest … +19 lowest). Backend use: deprioritise batch jobs so they
    don't hurt latency-sensitive services.

67. **What is a cgroup and a namespace (the basis of containers)?** **Namespaces**
    isolate what a process can *see* (PIDs, network, mounts, users); **cgroups**
    limit what it can *use* (CPU, memory, I/O). Together they make **containers**
    (Docker) — isolated processes sharing the host kernel, lighter than VMs.

68. **How is a container different from a VM?** A **VM** runs a full guest OS on a
    hypervisor (strong isolation, heavier). A **container** shares the **host
    kernel** via namespaces+cgroups (lightweight, fast start, weaker isolation).

---

## 22.8 Systems-Design-Flavoured OS Questions

69. **Design a thread pool.** A fixed set of worker threads pull tasks from a
    **thread-safe queue** (mutex + condition variable, or a lock-free queue). Bounds
    concurrency (avoids thread-explosion and context-switch thrash), reuses threads
    (amortises creation cost). Discuss queue backpressure, sizing (~#cores for
    CPU-bound, higher for I/O-bound), and graceful shutdown.

70. **Design a producer/consumer pipeline for high throughput.** Bounded buffer +
    `empty`/`full` semaphores; batch items to amortise locking; use multiple
    consumers; consider **lock-free ring buffers** and **backpressure** when
    consumers fall behind. Tie back to §22.3.

71. **How would you build an in-memory cache with eviction?** A hash map for O(1)
    lookup + an eviction policy (**LRU** via a doubly linked list, or **clock**);
    make it thread-safe with sharded locks; consider TTLs and memory bounds. This is
    literally the OS page-cache design.

72. **Design a rate limiter.** Token-bucket / leaky-bucket with an atomically
    updated counter; per-key state in a concurrent map; discuss clock, refill, and
    contention. OS angle: atomic ops vs locks under high concurrency.

73. **How do you scale a server to many concurrent connections (C10K)?** Don't use a
    thread per connection at large scale — use **non-blocking I/O + an event loop**
    (`epoll`/`kqueue`) or an async runtime, plus a bounded worker pool. The OS
    concept is **I/O multiplexing** and avoiding per-connection thread overhead.

74. **CPU-bound vs I/O-bound — how does it change your design?** CPU-bound → threads
    ≈ #cores, minimise context switches, pin/affinity. I/O-bound → many more
    outstanding requests than cores, async/event-driven so threads don't block idle
    on I/O.

75. **How would you make a shared counter fast under high concurrency?** Avoid a
    single hot lock: use an **atomic** (`fetch_add`) or **per-thread/sharded
    counters** summed on read (reduces cache-line contention / false sharing).

---

## 22.9 Classic Scenario & Debugging Questions

These "walk me through it" questions test real understanding. Narrate the mechanism.

### "What happens when you type `ls` and press Enter?"

1. The **shell** reads the line and parses it (`ls` + args).
2. Shell **`fork()`s** a child process (copy-on-write of its address space).
3. In the child, the shell **`exec()`s** `/bin/ls` — the process image is replaced
   by the `ls` program (a syscall resolves the path via `PATH`).
4. `ls` runs in **user mode**; to read the directory it makes **system calls**
   (`openat`, `getdents`, `stat`) that trap into the **kernel**, which reads
   directory entries/inodes (often from the **page cache**).
5. `ls` writes output to **fd 1 (stdout)** via `write` → the terminal.
6. `ls` exits; the kernel sends **`SIGCHLD`**; the shell, blocked in **`wait()`**,
   reaps the child (no zombie) and prints the next prompt.

### "What happens when a process calls `fork()`?"

- The kernel creates a **new PCB** and PID, and gives the child a **copy** of the
  parent's address space — but via **copy-on-write** (pages shared read-only, copied
  on first write). Open file descriptors are **shared** (same offset). `fork` returns
  **twice**: **0** in the child, the **child PID** in the parent. Both continue from
  the return point; scheduling order between them is **non-deterministic**.

### "The app is slow — how do you diagnose it?"

Work down the stack, cheapest checks first.

![Slow-app diagnosis ladder: start with top/uptime (is it CPU, memory, or I/O?), then drill with vmstat/iostat, then strace/perf on the process, then application logs and profilers.](images/202_slow_app_diagnosis.png)

1. **Is it CPU, memory, I/O, or network?** Start with **`top`/`htop`** and
   **`uptime`** (load average). High CPU% → compute or busy-wait; high **`wa`**
   (iowait) → disk/network bound; swap active → memory pressure.
2. **Memory:** **`free -m`**, `/proc/meminfo`. Swapping (`si/so` in **`vmstat`**
   non-zero) or the **OOM killer** in `dmesg` → memory problem.
3. **Disk/I/O:** **`iostat -x`** — high `%util`/`await` means the disk is the
   bottleneck.
4. **Which process/syscall?** **`strace -p <pid>`** to see if it's stuck in a syscall
   (e.g. blocking on a lock, `futex`, or `read`); **`perf top`/`perf record`** for
   where CPU time actually goes.
5. **Concurrency:** many threads in `D` (uninterruptible sleep) → I/O wait; lock
   contention shows as high `sys` time / lots of `futex` in `strace`.
6. **Application layer:** logs, slow queries (DB), GC pauses, thread-pool
   exhaustion, and profilers. Form a hypothesis, change **one** thing, measure.

> **Say the method, not just tools:** "I isolate the resource (CPU/mem/I/O/net) with
> `top`/`vmstat`/`iostat`, drill into the process with `strace`/`perf`, then confirm
> at the app layer — changing one variable at a time."

### "Design a scenario out of deadlock."

Given two threads that each lock A then B (or B then A) → circular wait. **Fix:**
enforce a **global lock ordering** (everyone locks A before B), or use
**`try_lock` with timeout + back-off**, or acquire both locks **atomically** (single
combined lock / lock hierarchy). Explain which Coffman condition each fix removes.

---

## 22.10 Production Scenarios (backend / SRE / infra)

- **"Server load spiked — what do you do?"** Check **load average** vs #cores
  (`uptime`), then split CPU vs I/O vs memory (`top`, `vmstat`, `iostat`). Identify
  the hot process/endpoint; check for **thread-pool exhaustion**, a **retry storm**,
  a hot lock, or a slow downstream. Mitigate (scale out, shed load / rate-limit,
  roll back a bad deploy), then root-cause.
- **"Memory keeps growing (leak)."** Watch **RSS** over time (`ps`, `top`,
  `/proc/<pid>/status`). Distinguish a real **leak** (unfreed allocations) from
  **cache growth** or heap that `malloc` didn't return to the OS. Tools: **`valgrind
  --leak-check`**, **ASan/heaptrack**, language heap profilers; check for unbounded
  caches/collections. If unaddressed → **OOM killer**.
- **"Zombie processes are piling up."** The parent isn't **reaping** children. Fix:
  call `wait()`/`waitpid()`, or handle **`SIGCHLD`** (or set `SA_NOCLDWAIT`). Confirm
  with `ps -el` (state **`Z`**, `<defunct>`). Zombies consume **PID slots**, not
  memory — but can exhaust the PID table.
- **"CPU is 100% but throughput is low."** Suspect a **busy-wait/spinlock**,
  **lock contention** (high `sys`), a **GC** loop, or **context-switch thrash**
  (too many threads). Check `vmstat` context-switch (`cs`) and interrupt (`in`)
  rates and `perf top`.
- **"Disk is full / slow."** `df -h` (space), `du -sh` (culprit dirs), `iostat -x`
  (utilisation/await). Watch for a runaway log file, unrotated logs, or a filesystem
  at ~100% causing write stalls.
- **"Too many open files."** `EMFILE`/`ENFILE` errors → fd leak or a low `ulimit -n`.
  Check `/proc/<pid>/fd` count; fix the leak or raise the limit.

---

## 22.11 Company Flavour

| Company | OS emphasis in interviews |
|---------|---------------------------|
| **Google** | Deep systems: virtual memory, page cache, concurrency correctness, "what happens when…"; expect precise, first-principles answers and follow-ups. |
| **Meta** | Fast-paced concurrency and Linux performance; threading, locks, and practical debugging of a running service. |
| **Amazon** | Practical scaling + operations: scheduling, resource limits (cgroups), production debugging, plus **Leadership Principles** (STAR) around an incident you handled. |
| **Microsoft** | Fundamentals done cleanly: processes/threads, synchronization, memory, deadlock; friendly pace, clarity valued. |
| **Apple** | Depth in your domain; low-level memory, real-time/latency, kernel/driver awareness for systems teams. |
| **NVIDIA** | Memory hierarchy, cache/TLB awareness, GPU/CPU scheduling, performance and parallelism (CUDA-adjacent); "know where the bytes are." |
| **OpenAI / AI-infra** | Systems for ML: **GPU scheduling & memory**, data-loading/I/O pipelines, NUMA, huge-memory processes, distributed training bottlenecks — OS reasoning applied to accelerators. |

> **Adapt the register:** at Google/Apple go **deep on the mechanism**; at
> Amazon/SRE lead with **operational reasoning** (metrics → hypothesis → fix); at
> NVIDIA/AI-infra tie every answer back to **where memory lives and how it's
> scheduled**.

---

## 22.12 Tools to Name-Drop (and what each is for)

Knowing the tool *and its one job* signals real experience.

| Tool | One-line purpose |
|------|------------------|
| **`top` / `htop`** | live per-process CPU/memory; first look at "what's hot" |
| **`uptime`** | load average (1/5/15 min) vs #cores |
| **`vmstat`** | memory/swap (`si/so`), context switches (`cs`), CPU breakdown over time |
| **`iostat -x`** | per-device disk utilisation, `await`, throughput — is I/O the bottleneck? |
| **`free -m`** | memory used vs cached vs available |
| **`ps` / `pstree`** | process list/tree, states (spot `Z` zombies, `D` I/O wait) |
| **`strace`** | trace a process's **system calls** — see where it blocks |
| **`ltrace`** | trace library calls |
| **`lsof`** | list open files/sockets/fds (leaks, "who holds this file/port") |
| **`perf`** | CPU profiler / hardware counters — where cycles actually go |
| **`dmesg`** | kernel ring buffer — OOM kills, hardware/driver errors |
| **`netstat` / `ss`** | sockets and connection states |
| **`gdb`** | attach/debug a process; inspect stacks of a hung app |
| **`valgrind`** | memory-leak / invalid-access detection |
| **`nice` / `taskset`** | adjust priority / CPU affinity |

> **Interview line:** *"I'd triage with `top`/`vmstat`/`iostat` to isolate the
> resource, `strace`/`perf` to find where the process spends time, and `lsof`/`dmesg`
> to catch fd leaks or OOM kills."*

---

## 22.13 One-Page Revision Sheet

```
INTERVIEWS TEST WHY + DEBUGGING, not recall. Answer = MECHANISM + TRADE-OFF.

PROCESS vs THREAD: process=own address space; thread=shares code/data/heap, own stack/regs/PC.
FORK: returns 0 to child, child-PID to parent, −1 fail. COW pages. EXEC replaces image (same PID).
ZOMBIE = dead child not reaped (wait) ; ORPHAN = parent died -> reparented to init(1).
CONTEXT SWITCH = save/restore PCB (+cache/TLB flush) = pure overhead.

SYNC: race=timing-dependent shared access. CS needs mutual excl + progress + bounded wait.
  MUTEX (ownership) vs SEMAPHORE (counter, no owner). SPINLOCK = busy-wait, short CS on multicore.
  DEADLOCK 4: mutual excl, hold&wait, no preempt, circular wait -> break one (global LOCK ORDER).
  livelock=busy no progress ; starvation=waits forever (fix=aging). Priority inversion->inheritance.

MEMORY/VM: virtual addr = page# + offset -> page table -> frame ; TLB caches it.
  PAGE FAULT: trap->find on disk->evict(dirty? write back)->load->restart instr.
  paging(fixed,internal frag) vs segmentation(variable,external frag,compaction).
  THRASHING=all time paging (working-set fix). COW after fork. malloc via brk/mmap.
  OOM killer when RAM+swap exhausted. FIFO can Belady; use LRU/clock.

SCHEDULING: preemptive vs not. SJF optimal avg WT (can't know bursts->estimate; starves).
  RR quantum: big->FCFS, small->overhead. MLFQ approximates SJF. Linux=CFS (vruntime, RB-tree).

FS/IO: inode=metadata+block ptrs (NOT name). hard link=same inode; soft=path.
  journaling=crash consistency. page cache=RAM disk cache. fsync=durability.
  polling<interrupts<DMA. SSD -> seek~0.

LINUX: user vs kernel mode via syscall/trap. shell = fork+exec+wait. /proc virtual FS.
  SIGKILL(9 uncatchable) vs SIGTERM(15 clean). fd 0/1/2. cgroups(limit)+namespaces(isolate)=containers.

DIAGNOSE SLOW APP: top/uptime (CPU/mem/IO?) -> vmstat/iostat -> strace/perf on pid -> app logs.
TOOLS: top vmstat iostat free ps strace lsof perf dmesg valgrind.
```

### Flash cards

| Front | Back |
|-------|------|
| Process vs thread? | Own address space vs shared (own stack/regs/PC) |
| `fork()` return values? | 0 child, child-PID parent, −1 fail |
| Zombie vs orphan? | Dead-unreaped vs parent-died (reparented to init) |
| Mutex vs semaphore? | Ownership lock vs counter/signal |
| Four deadlock conditions? | Mut-excl, hold&wait, no preempt, circular wait |
| Break a deadlock in code? | Global lock ordering / try-lock + back-off |
| What happens on a page fault? | Trap→load from disk (evict if needed)→restart |
| Thrashing fix? | Working-set / reduce multiprogramming |
| Shell runs a command via? | fork → exec → wait |
| Diagnose a slow app? | top→vmstat/iostat→strace/perf→app logs |
| SIGKILL vs SIGTERM? | Forcible/uncatchable vs polite/catchable |
| Container vs VM? | Shares host kernel (ns+cgroups) vs full guest OS |

### Spaced repetition
- **24-hour:** narrate "what happens when you run `ls`" and the "app is slow"
  diagnosis ladder out loud.
- **7-day:** answer the process/thread, mutex-vs-semaphore, virtual-memory, and
  deadlock-fix questions in 60 seconds each.
- **30-day:** do a mock: pick 10 random questions across §22.2–22.9 and answer with
  **mechanism + trade-off**; then the three production scenarios in §22.10.

---

## 22.14 Summary

Interviews reward **understanding and debugging**, not recall. We mapped the OS
areas interviewers probe and worked **~70 Q&A** across **processes/threads,
synchronization & deadlock, memory & virtual memory, scheduling, file systems &
I/O, Linux fluency**, and **systems-design-flavoured** questions — always answering
with the **mechanism plus the trade-off**. We walked the classic "what happens when
you type `ls`", "what `fork()` does", "diagnose a slow app", and "design out a
deadlock" scenarios; the production war-stories (**load spikes, memory leaks,
zombie pileups, fd exhaustion, OOM**); the per-company emphasis (Google/Apple deep
mechanism, Amazon/SRE operational reasoning, NVIDIA/AI-infra memory-and-scheduling);
and the **tools to name-drop** (`top`, `vmstat`, `iostat`, `strace`, `perf`, `lsof`,
`dmesg`). Pair this with Module 21's exam drills and the whole OS course now serves
both the written papers and the interview room.

Next, **Module 23 — Hands-On Projects** turns this theory into working code, and
**Module 24 — The Revision Kit** closes the course with a final integrated view and
revision plan.

> **You have mastered this module when** you can: explain process vs thread, mutex
> vs semaphore, virtual memory, and the four deadlock conditions with their
> trade-offs; narrate "what happens when you run `ls`" and "what `fork()` does" end
> to end; walk the "app is slow" diagnosis ladder naming the right tool at each step;
> and reason through the load-spike, memory-leak, and zombie-pileup production
> scenarios — all without notes.
