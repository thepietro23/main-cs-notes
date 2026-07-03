---
title: "Module 24 — The Revision Kit (Your Final Sprint)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 24 — The Revision Kit (Your Final Sprint)

> **Where this module sits.**
> This is the **last module** and it owns none of its own theory — it **compresses
> the whole course.** Modules 1–20 taught the concepts; M21–M23 gave you PYQs,
> practice, and projects. Now, in the final days before an exam or an interview, you
> need one place that holds **every formula, every trap, every one-liner** and a
> plan to review it. That is this module: a **master formula sheet** (all OS
> numericals recomputed and verified), **cheat sheets** per topic, a **topic
> dependency graph**, **mind-maps**, a consolidated **flash-card** deck, a
> **spaced-repetition schedule**, the **common exam traps**, a **last-minute
> strategy**, and the **50 one-liners** that carry the most marks. Read nothing else
> the night before — read this.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★★  | ★★★★★   | ★★★★★     | ★★★★    |

**Most-asked PYQ concepts (all modules, in one place):** scheduling averages
(TAT/WT); **EAT with TLB** and **with page faults**; **page-fault counting**
(FIFO/LRU/Optimal + Belady's anomaly); **disk head movement** (FCFS/SSTF/SCAN/
C-SCAN); **Banker's algorithm** safe sequence; **RMS utilisation bound**
`n(2^(1/n)−1)`; **inode max file size**; **effective access time with cache**;
address translation (page number/offset bits); semaphores & the classic
synchronisation problems; deadlock's four conditions.

---

## 24.1 How to Revise (the method that actually works)

- **Recompute, don't reread.** OS marks come from *numericals.* Re-derive one Gantt
  chart, one EAT, one Banker's sequence **by hand** every day — passive reading fails.
- **Spaced repetition over cramming.** Use the 24h / 7d / 30d schedule in §24.7. Ten
  minutes daily beats one panicked night.
- **Traps first.** Half of all lost marks are the traps in §24.8 (½-rotation, Belady,
  RAID-0 has no redundancy). Learn the traps and you claw back easy marks.
- **Teach it.** Explain "what is a page fault" or "why SJF is optimal" out loud. If
  you stumble, that is your next revision target.
- **One page per topic.** §24.5 condenses each module to a page — if you can
  reproduce that page from memory, you know the module.

> **Memory hook:** **R-C-T** — **R**ecompute a numerical, **C**over the answer and
> recall the one-liner, **T**each it to an empty chair. Do R-C-T for one topic a day.

---

## 24.2 Master Formula Sheet — EVERY OS Numerical (verified)

This is the centrepiece. Every formula below was **re-derived and checked**; the
worked numbers are computed, not remembered.

### A. CPU Scheduling (M6)

```
Turnaround Time (TAT) = Completion Time − Arrival Time
Waiting Time    (WT)  = TAT − Burst Time   =  (Completion − Arrival) − Burst
Response Time         = First-CPU-start − Arrival Time
Average X             = (Σ X) / n
Throughput            = (jobs completed) / (total time)
CPU Utilisation       = busy time / total time
```

> **Worked (one example that drives the whole topic):** processes
> `P1(AT0,BT5) P2(AT1,BT3) P3(AT2,BT8) P4(AT3,BT6)`.
>
> | Algo | Order (Gantt) | Avg TAT | Avg WT |
> |------|---------------|:-------:|:------:|
> | **FCFS** | P1,P2,P3,P4 | 45/4 = **11.25** | 23/4 = **5.75** |
> | **SJF (np)** | P1,P2,P4,P3 | 43/4 = **10.75** | 21/4 = **5.25** |
> | **RR (q=3)** | P1,P2,P3,P4,P1,P3,P4,P3 | 56/4 = **14.0** | 34/4 = **8.5** |
>
> **SJF/SRTF gives the provably minimum average WT.** RR's average is worse but its
> **response time** is best. (Full traces are in M23 §23.3.)

- **RR quantum rule:** quantum too **large** → behaves like **FCFS**; too **small** →
  context-switch **overhead** dominates.
- **Convoy effect:** in FCFS a long job delays everyone behind it.

### B. Real-Time Scheduling — Rate-Monotonic bound (M6)

```
A set of n periodic tasks is schedulable under RMS if:
   U = Σ (Ci / Ti)  ≤  n · (2^(1/n) − 1)          (sufficient, not necessary)
   as n → ∞ the bound → ln 2 ≈ 0.6931
EDF bound (optimal):  U ≤ 1  (schedulable iff total utilisation ≤ 100%)
```

> **The bound values you should recognise (verified):**
>
> | n | `n(2^(1/n)−1)` |
> |---|:--------------:|
> | 1 | **1.000** |
> | 2 | **0.828** |
> | 3 | **0.780** |
> | 4 | **0.757** |
> | 5 | **0.743** |
> | ∞ | **0.693** (ln 2) |
>
> **Trap:** the RMS bound is **sufficient, not necessary** — a set above the bound
> *may still* be schedulable (test it exactly). EDF is optimal: schedulable iff
> `U ≤ 1`.

### C. Address Translation & Paging (M9, M10)

```
Logical address space = 2^m bytes ; Page size = 2^n bytes
  → offset bits = n ; page-number bits = m − n ; number of pages = 2^(m−n)
Physical address space = 2^p bytes → number of frames = 2^(p−n)
Page-table entries      = number of pages = 2^(m−n)
Internal fragmentation  ≈ half a page per process (average), on the last page
```

### D. Effective Access Time — TLB / paging (M10)

```
No TLB (single-level page table):  EAT = 2 × (memory access)   [1 for table, 1 for data]
With TLB (hit ratio h, TLB time t, memory m):
   EAT = h·(t + m) + (1 − h)·(t + 2m)
Multi-level (L levels) on a TLB miss:
   EAT = h·(t + m) + (1 − h)·(t + (L + 1)·m)
```

> **Worked (verified):** `h = 80%`, `TLB t = 20 ns`, `memory m = 100 ns`:
> `EAT = 0.8·(20+100) + 0.2·(20+200) = 0.8·120 + 0.2·220 = 96 + 44 =` **140 ns**.

### E. Effective Access Time — cache/memory two-level (M2)

```
EAT = H·Tc + (1 − H)·Tm          (miss served straight from memory)
EAT = H·Tc + (1 − H)·(Tc + Tm)   (miss also pays the cache probe first)
```

> **Worked (verified, simple form):** `H = 90%`, `Tc = 10 ns`, `Tm = 100 ns`:
> `EAT = 0.9·10 + 0.1·100 = 9 + 10 =` **19 ns**.

### F. Demand Paging — EAT with page faults (M10)

```
EAT = (1 − p)·(memory access) + p·(page-fault service time)
   p = page-fault rate ; a fault costs ~ms (disk) vs ~ns (memory)
```

> **Worked (verified):** memory `= 100 ns`, page-fault service `= 8 ms = 8,000,000
> ns`, `p = 0.001`:
> `EAT = 0.999·100 + 0.001·8,000,000 = 99.9 + 8000 =` **8099.9 ns ≈ 8.1 µs**.
> One fault in a thousand makes memory ~**80× slower** — why we fear thrashing.

### G. Page-Replacement — fault counting & Belady (M10)

```
Count faults for FIFO / LRU / Optimal on a reference string with F frames.
  Optimal (OPT): evict the page used FARTHEST in the future (lower bound; unbeatable).
  LRU: evict the least-recently USED (past). Stack algorithm → NO Belady anomaly.
  FIFO: evict the oldest loaded. CAN suffer Belady's anomaly.
```

> **Worked (verified)** — string `1 2 3 4 1 2 5 1 2 3 4 5`:
>
> | Policy | Frames | Faults |
> |--------|:------:|:------:|
> | **FIFO** | 3 | **9** |
> | **FIFO** | 4 | **10** ← *more frames, MORE faults = **Belady's anomaly*** |
> | **LRU** | 3 | **10** |
> | **Optimal** | 3 | **7** (the minimum) |
>
> **`OPT ≤ LRU` always; `Optimal` is the theoretical floor. FIFO can get worse with
> more frames** (this exact string proves it). LRU/OPT are **stack algorithms** —
> immune to Belady.

### H. Disk Scheduling — head movement (M12)

```
Total head movement = Σ | next position − current position |  (in cylinders)
  FCFS  : serve in arrival order.
  SSTF  : always the nearest request next (can starve far requests).
  SCAN  : sweep to one END, reverse, sweep back (elevator).
  C-SCAN: sweep to the end, JUMP to the start, sweep the same direction (uniform wait).
  LOOK / C-LOOK: like SCAN/C-SCAN but only go as far as the last request (no wasted end trip).
```

> **Worked (verified)** — head `= 53`, requests `98,183,37,122,14,124,65,67`,
> disk `0–199`, moving toward larger first:
>
> | Algorithm | Total head movement |
> |-----------|:-------------------:|
> | **FCFS** | **640** |
> | **SSTF** | **236** |
> | **SCAN** (to 199, then down) | **331** |
> | **C-SCAN** (to 199, wrap to 0, up) | **382** |
>
> **SSTF gives the least movement here but can starve; SCAN/C-SCAN are fairer.**
> LOOK/C-LOOK would be lower (no trip to the physical end 199).

### I. Deadlock — Banker's Algorithm (M8)

```
Need = Max − Allocation
Work = Available ; Finish[i] = false for all i
Repeat: find an i with Finish[i]=false AND Need[i] ≤ Work
        → Work = Work + Allocation[i] ; Finish[i] = true
If all Finish[i]=true → SAFE (the order found is a safe sequence); else UNSAFE.
```

> **Worked (verified)** — 5 processes, resources (A,B,C), Total `= (10,5,7)`:
>
> ```text
>        Alloc     Max      Need(=Max−Alloc)
> P0     0 1 0    7 5 3     7 4 3
> P1     2 0 0    3 2 2     1 2 2
> P2     3 0 2    9 0 2     6 0 0
> P3     2 1 1    2 2 2     0 1 1
> P4     0 0 2    4 3 3     4 3 1
> Available = Total − ΣAlloc = (10,5,7) − (7,2,5) = (3,3,2)
> ```
> Safe sequence: **P1 → P3 → P4 → P0 → P2** (each Need ≤ current Work; system is
> **SAFE**). **Trap:** *safe ≠ no deadlock possible ever* — it means a sequence
> exists that lets everyone finish from *this* state.

### J. File System — inode max file size (M11)

```
Let block size = B, pointer size = P → pointers per block  N = B / P
Direct blocks = d ; plus single, double, triple indirect:
Max file size = ( d + N + N² + N³ ) × B
```

> **Worked (verified):** `B = 4 KB`, `P = 4 B` → `N = 1024`, `d = 12`:
> `(12 + 1024 + 1,048,576 + 1,073,741,824) × 4096 = 4,402,345,721,856 B ≈` **4.00 TB**.
>
> **Second variant (GATE-style):** `B = 1 KB`, `P = 4 B` → `N = 256`, `d = 10`:
> `(10 + 256 + 65,536 + 16,777,216) × 1024 = 17,247,250,432 B ≈` **16.06 GB**.

### K. Disk & Storage (from M12 / storage)

```
Average rotational latency = ½ × (60 / RPM)   seconds     (HALF a rotation)
Transfer time              = data size / transfer rate
Disk access time           = seek + rotational latency + transfer (+ controller)
Blocking factor  bfr       = floor(Block size / Record size)
Number of blocks           = ceil(records / bfr)
```

> **Worked:** disk at `6000 RPM` → one rotation `= 60/6000 = 10 ms`; average
> rotational latency `= 5 ms`. With seek `4 ms` and transfer `1 ms`, total `≈` **10
> ms**.

### L. Synchronisation quick-formulas (M7)

```
Counting semaphore: wait(S){ S--; if(S<0) block } ; signal(S){ S++; if(S≤0) wakeup }
  |S| when negative = number of processes blocked on S.
Binary semaphore / mutex: value ∈ {0,1}.
Bounded buffer: semaphores  empty=N, full=0, mutex=1.
```

---

## 24.3 Topic Dependency Graph (what to learn before what)

![OS topic dependency graph: hardware and OS basics feed processes and threads, which feed scheduling, synchronization, and deadlocks; memory leads to virtual memory; storage leads to file systems and disk scheduling — all converging on Linux internals and systems projects.](images/219_topic_dependency_graph.png)

Read this **top to bottom**: an arrow means "understand the source before the
target." If a later topic feels shaky, the fix is almost always an **upstream** node.

```text
M1 Intro ─┬─> M2 Hardware ─┬─> M3 Architecture ──> M14 Linux internals
          │                └─> M9 Memory ──> M10 Virtual memory ─┐
          └─> M4 Processes ─┬─> M5 Threads ─┬─> M6 Scheduling     │
                            │               └─> M7 Sync ─> M8 Deadlocks
                            └─> M11 File systems <── M12 Disk mgmt ┘
   (everything feeds) ──────────────────────> M23 Projects ─> M24 Revision
```

> **The three natural clusters (revise as blocks):**
> 1. **Process world:** M4 → M5 → M6 → M7 → M8 (processes, threads, scheduling,
>    synchronisation, deadlocks).
> 2. **Memory world:** M2 → M9 → M10 (hierarchy, allocation, paging/virtual memory).
> 3. **Storage world:** M11 → M12 (file systems, inodes, disk scheduling).

---

## 24.4 Mind-Map Overviews (the whole course on one wall)

![OS mind-map: five branches — Process Management, Memory Management, Storage & I/O, Concurrency, and System/Kernel — each with its key sub-topics radiating out.](images/220_os_mindmap.png)

**Branch 1 — Process Management (M4–M6):** PCB · states (new/ready/running/waiting/
terminated) · context switch · `fork`/`exec`/`wait` · scheduling (FCFS/SJF/SRTF/RR/
priority) · TAT/WT · IPC (pipes, shared memory, message passing).

**Branch 2 — Concurrency (M7–M8):** race condition · critical section · mutex ·
semaphore · monitor · producer–consumer · readers–writers · dining philosophers ·
deadlock's **4 conditions** (mutual exclusion, hold-and-wait, no preemption, circular
wait) · Banker's algorithm · RAG.

**Branch 3 — Memory Management (M2, M9–M10):** hierarchy · contiguous vs paging vs
segmentation · MMU · logical vs physical address · TLB · page table (multi-level,
inverted) · page faults · replacement (FIFO/LRU/OPT/CLOCK) · Belady · thrashing ·
working set · demand paging · copy-on-write.

**Branch 4 — Storage & I/O (M11–M12):** file · directory · inode · allocation
(contiguous/linked/indexed) · free-space (bitmap/free-list) · disk geometry · disk
scheduling (FCFS/SSTF/SCAN/C-SCAN/LOOK) · RAID · I/O methods (polling/interrupt/DMA).

**Branch 5 — System / Kernel (M1–M3, M14):** OS roles · types · user vs kernel mode ·
system calls · kernel architectures (monolithic/microkernel/hybrid) · boot process ·
`/proc` · loadable modules · virtualization/hypervisors.

---

## 24.5 One Page Per Topic (condensed cheat sheets)

**Processes (M4).** PCB holds PID, state, PC, registers, memory maps, open files.
States: new→ready→running→(waiting)→ready→terminated. `fork`=clone (returns 0 to
child, child-PID to parent), `exec`=replace image, `wait`=reap. Zombie = dead but
un-`wait`ed; orphan → adopted by **init (PID 1)**. IPC: shared memory (fast, needs
sync), message passing (safe, slower), pipes, sockets.

**Threads (M5).** Share code/data/heap/files; **own** stack + registers + PC.
User-level (fast, N:1, one blocking call blocks all), kernel-level (true parallelism,
costlier). Models: many-to-one, one-to-one, many-to-many. Thread switch < process
switch (same address space → no TLB flush).

**CPU Scheduling (M6).** Non-preemptive: FCFS, SJF. Preemptive: SRTF, RR, priority.
**SJF/SRTF = min average WT.** RR fair/responsive, tune quantum. Priority → starvation
→ fix with **aging**. Metrics: TAT, WT, response, throughput. Convoy effect (FCFS).

**Synchronisation (M7).** Race condition needs a **critical section** with mutual
exclusion + progress + bounded waiting. Tools: mutex, **semaphore** (wait/signal),
monitor (language-level). Classics: producer–consumer (empty/full/mutex),
readers–writers, dining philosophers (break circular wait). Peterson's algorithm =
software mutex for 2 processes. Priority inversion → priority inheritance.

**Deadlocks (M8).** Four **necessary** conditions together: mutual exclusion,
hold-and-wait, no preemption, circular wait. Handle by prevent / avoid (**Banker's**)
/ detect+recover / ignore (ostrich). RAG: a cycle ⇒ deadlock **iff single instance**
per resource. Safe state ≠ deadlock; unsafe *may* deadlock.

**Memory (M9).** Contiguous (first/best/worst fit → external fragmentation) →
**paging** (fixed frames, no external frag, small internal) and **segmentation**
(logical, external frag). MMU maps logical→physical. Page table per process; TLB
caches translations.

**Virtual Memory (M10).** Demand paging: load pages on fault. EAT dominated by fault
cost. Replacement: FIFO (Belady), LRU, OPT (best), CLOCK/second-chance. **Thrashing**
= more time paging than working → fix with **working-set** model / page-fault-
frequency. Copy-on-write speeds `fork`.

**File Systems (M11).** File = named bytes + metadata (**inode**). Directory maps
name→inode. Allocation: contiguous (fast, fragments), linked (no random access),
**indexed/inode** (direct + single/double/triple indirect). Free space: bitmap or
free-list. Hard link = another name → same inode; soft link = a path.

**Disk Management (M12).** Access = seek + ½-rotation + transfer. Scheduling: FCFS,
SSTF (starves), SCAN/C-SCAN (elevator, fair), LOOK/C-LOOK (no end trip). SSD → no
seek. RAID 0/1/5/6/10 (M12/storage).

**Architecture (M3).** User vs kernel mode; the boundary is the **system call** (trap
→ kernel). Monolithic (fast, Linux) vs microkernel (safe, message-passing) vs hybrid.
Boot: firmware → bootloader → kernel → init/systemd.

---

## 24.6 Consolidated Flash Cards (meta-set across all modules)

| Front | Back |
|-------|------|
| Two roles of an OS? | Resource manager + extended (virtual) machine |
| App→OS doorway? | System call (trap into kernel mode) |
| PCB holds? | PID, state, PC, registers, memory maps, open files |
| `fork` returns? | 0 to child, child-PID to parent |
| Zombie vs orphan? | Dead-unreaped vs parent-died (→ init/PID 1) |
| Thread's private parts? | Stack, registers, PC (shares code/data/heap) |
| Min average waiting time algo? | SJF / SRTF |
| RR quantum too small → ? | Context-switch overhead |
| 4 deadlock conditions? | Mutual excl., hold-and-wait, no preempt, circular wait |
| Banker's Need = ? | Max − Allocation |
| Safe state means? | A sequence exists letting all finish |
| Paging cures which fragmentation? | External (adds small internal) |
| TLB is? | Cache of page-table entries |
| EAT with faults dominated by? | Page-fault service time (disk, ~ms) |
| Belady's anomaly in? | FIFO (LRU/OPT immune — stack algorithms) |
| Optimal replacement rule? | Evict page used farthest in future |
| Thrashing fix? | Working-set / page-fault-frequency |
| Inode does NOT store? | The file name (directory does) |
| Hard vs soft link? | Same inode vs a path string |
| Least disk movement (may starve)? | SSTF |
| Fair elevator disk scan? | SCAN / C-SCAN |
| Avg rotational latency? | ½ × (60/RPM) |
| User↔kernel switch trigger? | System call / interrupt / trap |
| Monolithic vs microkernel? | One kernel space vs minimal + message passing |
| RMS bound as n→∞? | ln 2 ≈ 0.693 |
| Semaphore |S| when negative? | Number of blocked processes |
| Copy-on-write speeds? | `fork` (share pages until a write) |
| Convoy effect in? | FCFS (long job blocks the queue) |

---

## 24.7 Spaced-Repetition Schedule

![Spaced-repetition timeline: review at 1 day, 3 days, 7 days, 16 days, and 30 days — each review resets a longer interval, moving facts into long-term memory before exam day.](images/221_spaced_repetition.png)

Map each module to a **first-learn day**, then review on the offsets below. Tick the
box each time you *recall from memory* (not reread).

| Interval | What you do | Time |
|----------|-------------|:----:|
| **Same day** | Read the module + its one-page sheet (§24.5) | 30 min |
| **+1 day** | Recompute ONE numerical from the module; recite its flash cards | 10 min |
| **+3 days** | Cover-and-recall the cheat sheet; redo a *harder* numerical | 15 min |
| **+7 days** | Teach the topic aloud; do 5 mixed MCQs | 15 min |
| **+16 days** | Full-topic recall from a blank page | 20 min |
| **+30 days** | Timed mixed set (all modules) | 45 min |

> **The 3-week countdown plan (before the exam):**
> - **Weeks −3 to −2:** one *cluster* per day (process world → memory world → storage
>   world), always with a hand-computed numerical.
> - **Week −1:** only §24.2 (formulas), §24.8 (traps), and §24.10 (one-liners); one
>   full mixed mock daily.
> - **Last 24 h:** read §24.2, §24.8, §24.12 only. Sleep. Do **not** learn anything
>   new.

---

## 24.8 Common Mistakes & Exam Traps (reclaim these marks)

- **Rotational latency = ½ rotation**, not a full one. (`½ × 60/RPM`.)
- **RAID 0 has NO fault tolerance** (despite the "0"); RAID 5 needs ≥3, RAID 6 ≥4.
- **Belady's anomaly is FIFO-only.** LRU and Optimal are stack algorithms — immune.
- **Optimal ≤ LRU always;** Optimal is a *theoretical* lower bound (needs the future).
- **SJF minimises average WT** but can **starve** long jobs (needs burst prediction).
- **RR:** huge quantum → FCFS; tiny quantum → overhead. State the quantum you assume.
- **Safe state ≠ deadlock-free forever** — it means a finishing sequence exists *now*.
- **A cycle in a RAG ⇒ deadlock only with single-instance resources**; multi-instance
  needs the detection algorithm.
- **Paging removes external fragmentation** but adds **internal** (last page); pure
  segmentation is the opposite.
- **EAT with page faults** — convert units! ms vs ns differ by **10⁶**; a tiny fault
  rate dominates the average.
- **TLB EAT** — on a miss you pay the page-table walk **plus** the data access
  (`t + 2m` for single-level).
- **Inode max size** — remember to add **single + double + triple** indirect, not just
  direct; and multiply by the block size at the end.
- **Deadlock's four conditions are necessary *together*** — breaking **any one**
  prevents deadlock.
- **Semaphore vs mutex:** a mutex has an **owner** (only the locker unlocks); a
  semaphore is a counter anyone can signal.
- **`wait()` reaps a child** — forgetting it leaves **zombies**; the child's parent
  must reap, or init adopts an **orphan**.
- **Preemptive vs non-preemptive** — SJF is non-preemptive, **SRTF** is its
  preemptive version; don't mix the averages.
- **Thrashing** is a *memory* problem (too little RAM for the working set), not a CPU
  or disk-speed problem.

---

## 24.9 Last-Minute Exam Strategy

**Before you start:**
- Skim the whole paper; **mark the numericals** — they are the highest, most certain
  marks. Do the ones you recognise (scheduling, EAT, disk, Banker's) **first**.
- Keep a **formula strip** in your head from §24.2: TAT/WT, EAT(TLB), EAT(fault),
  head-movement, Need=Max−Alloc, inode `(d+N+N²+N³)·B`, RMS `n(2^(1/n)−1)`.

**During numericals:**
- **Draw the Gantt chart / page-frame table / RAG** — never compute in your head.
- **Write units** at every step (ns vs ms); convert once, up front.
- For page-replacement, **draw the frames as columns** and mark hit/fault per column.
- For Banker's, **write the Need matrix first**, then sweep for a satisfiable process.
- **Recompute the average** — a single arithmetic slip loses the whole sub-question.

**For MCQs / one-liners:**
- Trust the **traps list** (§24.8): RAID-0, Belady=FIFO, ½ rotation, safe≠safe-forever.
- Eliminate absolutes ("always/never") unless you're sure.

**Time & nerves:**
- Budget ~1 min per mark; **flag and move on** if stuck — return later.
- The night before: **§24.2 + §24.8 + §24.10 only.** Then sleep — recall beats
  cramming.

---

## 24.10 The 50 Most Important One-Liners

1. OS = **resource manager + extended (virtual) machine**.
2. App reaches the OS via a **system call** (trap to kernel mode).
3. The always-resident core is the **kernel**.
4. **Multiprogramming** = many jobs in RAM, 1 CPU switches on I/O wait.
5. **Multitasking** = multiprogramming + rapid time slices (interactive).
6. **Multiprocessing** = many CPUs, true parallelism.
7. **Hard RTOS**: missed deadline = failure; **soft**: tolerable.
8. **Spooling** = disk as buffer for a slow device (printer queue).
9. **Type-1** hypervisor = bare-metal; **Type-2** = hosted.
10. **PCB** stores PID, state, PC, registers, memory maps, open files.
11. Process states: new → ready → running → waiting → terminated.
12. **`fork`** returns 0 to child, child-PID to parent.
13. **`exec`** replaces the image; **`wait`** reaps the child.
14. **Zombie** = dead, un-`wait`ed; **orphan** → adopted by init (PID 1).
15. **Context switch** saves/restores registers, PC, stack pointer.
16. Threads share code/data/heap/files but own **stack + registers + PC**.
17. Thread switch < process switch (**same address space**, no TLB flush).
18. Thread models: many-to-one, one-to-one, many-to-many.
19. **SJF/SRTF** = minimum average waiting time (optimal).
20. **RR** quantum: too big → FCFS, too small → overhead.
21. **Priority scheduling** → starvation → fixed by **aging**.
22. **Convoy effect** = a long job stalls the FCFS queue.
23. **TAT** = Completion − Arrival; **WT** = TAT − Burst.
24. Critical section needs mutual exclusion + progress + bounded waiting.
25. **Semaphore** = counter with `wait`/`signal`; **mutex** has an owner.
26. **Peterson's algorithm** = software mutex for two processes.
27. Bounded buffer uses semaphores **empty=N, full=0, mutex=1**.
28. **Priority inversion** fixed by **priority inheritance**.
29. Deadlock needs **4 conditions together**: mutual excl., hold-and-wait, no
    preempt, circular wait.
30. Break **any one** condition → no deadlock.
31. **Banker's**: `Need = Max − Allocation`; find a safe sequence.
32. **Safe state ≠ deadlock-free forever**; unsafe *may* deadlock.
33. RAG **cycle ⇒ deadlock iff single-instance** resources.
34. **Paging** removes external fragmentation, adds small internal.
35. **Segmentation** is logical/variable-size → external fragmentation.
36. **MMU** translates logical → physical addresses.
37. **TLB** caches page-table entries; a hit avoids the walk.
38. **EAT(TLB, single-level)** = `h(t+m) + (1−h)(t+2m)`.
39. **Demand paging** loads pages on fault; EAT dominated by fault cost (~ms).
40. **Belady's anomaly** = more frames, more faults — **FIFO only**.
41. **Optimal** evicts the page used farthest in the future (lower bound).
42. **LRU/Optimal** are stack algorithms — immune to Belady.
43. **Thrashing** = excessive paging; fix with working-set / PFF.
44. **Copy-on-write** makes `fork` cheap (share until a write).
45. **Inode** holds metadata + block pointers but **not the file name**.
46. Inode max size = `(direct + N + N² + N³) × block`, `N = block/pointer`.
47. **Hard link** = same inode; **soft link** = a path string.
48. Disk access = **seek + ½-rotation + transfer**.
49. **SSTF** = least head movement but can starve; **SCAN/C-SCAN** = fair elevator.
50. **RAID 0** = no redundancy; **RAID 5** ≥3 disks; **RMS bound** → ln 2 ≈ 0.693.

---

## 24.11 Concept Checks (mixed, all modules)

1. Average WT for the §24.2 FCFS example? → **5.75**.
2. Which policy minimises average WT? → **SJF/SRTF**.
3. `EAT` with `h=80%, TLB=20 ns, mem=100 ns`? → **140 ns**.
4. `EAT` with `p=0.001, mem=100 ns, fault=8 ms`? → **≈ 8100 ns**.
5. FIFO on `1 2 3 4 1 2 5 1 2 3 4 5`: faults at 3 vs 4 frames? → **9 vs 10** (Belady).
6. Least disk head movement here (§24.2 H)? → **SSTF (236)**.
7. Banker's safe sequence for the §24.2 I example? → **P1,P3,P4,P0,P2** (safe).
8. RMS bound for `n=3`? → **≈ 0.780**.
9. Inode max size, `B=4 KB, P=4 B, 12 direct`? → **≈ 4 TB**.
10. `EAT` cache with `H=90%, Tc=10, Tm=100`? → **19 ns**.
11. Which fragmentation does paging cure? → **external**.
12. Which replacement policies are immune to Belady? → **LRU and Optimal**.
13. Number of pages if logical space `2^32`, page `2^12`? → `2^20` = **1,048,576**.
14. Deadlock's four conditions? → mutual excl., hold-and-wait, no preempt, circular
    wait.
15. Average rotational latency at 6000 RPM? → **5 ms**.

---

## 24.12 One-Page Revision Sheet (the revision of the revision)

```
FORMULAS (verified):
  TAT=CT-AT ; WT=TAT-BT ; avg=Σ/n ; SJF=min avg WT ; RR: big q->FCFS, small q->overhead
  EAT(TLB,1lvl)= h(t+m)+(1-h)(t+2m)     e.g. .8(120)+.2(220)=140ns
  EAT(cache)  = H*Tc+(1-H)*Tm           e.g. .9*10+.1*100=19ns
  EAT(faults) = (1-p)*ma + p*service    e.g. .999*100+.001*8e6=8099.9ns
  RMS bound   = n(2^(1/n)-1) -> ln2=.693 ; EDF: U<=1
  DISK access = seek + (1/2)(60/RPM) + transfer ; head move = Σ|Δ|
  BANKER      = Need=Max-Alloc ; safe if a seq lets all finish (P1,P3,P4,P0,P2)
  INODE max   = (d + N + N^2 + N^3)*B , N=B/P  (4KB/4B,12 direct ~ 4TB)
  PAGING      = offset=n bits, pages=2^(m-n) ; paging kills EXTERNAL frag

TRAPS: rot latency=1/2 rotation | RAID0=no redundancy | Belady=FIFO only |
  OPT<=LRU | safe!=deadlock-free forever | cycle=>deadlock iff single-instance |
  SJF starves | thrashing=memory problem | convert ms<->ns (10^6)

DISK MOVEMENT (head53, 8 reqs): FCFS640 SSTF236 SCAN331 C-SCAN382 (SSTF least, may starve)
PAGE FAULTS (1,2,3,4,1,2,5,1,2,3,4,5): FIFO 3f=9 4f=10(Belady) | LRU=10 | OPT=7

CLUSTERS: [process: M4-M8] [memory: M2,M9,M10] [storage: M11,M12] [system: M1-M3,M14]
DEADLOCK 4: mutual-excl, hold-and-wait, no-preempt, circular-wait (break ANY one)
```

### Flash cards (the final ten)

| Front | Back |
|-------|------|
| WT formula? | (Completion − Arrival) − Burst |
| Min avg WT algo? | SJF / SRTF |
| Belady's anomaly? | FIFO only (more frames → more faults) |
| Optimal replacement? | Evict page used farthest in future |
| EAT(TLB) single-level? | h(t+m) + (1−h)(t+2m) |
| Banker's Need? | Max − Allocation |
| Inode max size? | (d + N + N² + N³) × block |
| Least head movement? | SSTF (but starves) |
| RMS bound as n→∞? | ln 2 ≈ 0.693 |
| 4 deadlock conditions? | mutual-excl, hold-wait, no-preempt, circular-wait |

### Spaced repetition
- **24-hour:** recompute one Gantt chart, one EAT, one page-fault count — from blank.
- **7-day:** do the disk-movement four-way and a Banker's safe sequence cold.
- **30-day:** a full timed mixed mock across all modules; then reread §24.8 traps.

---

## 24.13 Summary — and the close of the whole course

This module is your **compression of the entire OS course into a single sprint kit.**
The **master formula sheet** (§24.2) holds every numerical you can be asked —
scheduling averages, EAT with TLB and with page faults, page-fault counting with
Belady's anomaly, disk head movement, the Banker's safe sequence, the RMS bound
`n(2^(1/n)−1)`, and the inode max-file-size formula — each one **recomputed and
verified**, not remembered. Around it sit the tools to *retain* it: a **topic
dependency graph** and **mind-maps** to see the shape of the subject, **one-page
cheat sheets** per module, a **consolidated flash-card deck**, a **spaced-repetition
schedule**, the **exam traps** that quietly cost marks, a **last-minute strategy**,
and the **50 one-liners** that carry the most weight.

Step back and see what you have built across twenty-four modules. You started at
**"what is an OS?"** and can now explain how a computer **shares itself fairly, safely,
and fast** — how a **process** is born (`fork`/`exec`) and scheduled (FCFS→SJF→RR),
how threads and semaphores tame **concurrency** without deadlock, how **virtual
memory** gives every program its own vast address space over a tiny RAM, how **file
systems** and **disks** turn spinning platters into named files, and how the **kernel**
sits beneath it all. In M23 you even *built* small versions yourself. That is the
whole arc of the subject — from the first system call to a shell you wrote.

Revise with **recall, not rereading**; lead with the **numericals**; respect the
**traps**. Do that, and you walk into any SEBI / RBI / NABARD / GATE / C-DAC paper —
or any systems interview — knowing not just the answers, but *why* they are the
answers.

> **You have mastered this module — and the course — when** you can: reproduce the
> master formula sheet from memory and compute every OS numerical cold; draw the
> topic dependency graph and place any concept on it; recite the 50 one-liners and
> the exam traps without hesitation; and explain, end to end, how an operating system
> shares a computer fairly, safely, and fast. That is OS mastery. Go earn the marks.
