---
title: "Module 21 — Competitive Exams (OS for SEBI / RBI / NABARD / GATE / C-DAC)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 21 — Competitive Exams

> **Where this module sits.**
> Modules 1–20 taught the *subject*. This capstone teaches how the subject is
> **tested** — and the same OS content is examined very differently across
> **SEBI Grade A (IT) / RBI Grade B (IT) / NABARD / GATE CS / C-DAC (CCAT)**.
> **GATE and C-DAC want you to *compute*** (Gantt charts, page-fault counts, EAT,
> disk head movement, Banker's algorithm); **SEBI / RBI / NABARD want you to
> *know*** (crisp conceptual MCQs, definitions, one-liners). This module maps every
> OS topic to every exam, gives per-exam strategy, the **formulas to memorise
> cold**, a **memorise-cold concept list**, and **~50 solved MCQs with worked
> answers** grouped by topic. Treat it as the single sheet you revise the night
> before the paper.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★★  | ★★★★★   | ★★        | ★★      |

**Most-asked PYQ concepts (SEBI / RBI / NABARD / GATE / C-DAC):** CPU scheduling
(**Gantt + avg WT/TAT**, SJF optimality, RR quantum); **page replacement** fault
counts (FIFO/LRU/Optimal, **Belady's anomaly**); **EAT with TLB** and demand-paging
EAT; **deadlock** four conditions + **Banker's safe sequence**; **synchronization**
(semaphore wait/signal, critical-section requirements, classic problems);
**disk-scheduling** head movement (FCFS/SSTF/SCAN/C-SCAN); **inode max file size**;
paging vs segmentation; process states; thread models.

---

## 21.1 The Exam Landscape — "Compute It" vs "Know It"

Before choosing *what* to study, understand *how* each exam asks. Two families:

![The five exams split into two camps: GATE and C-DAC test numerical computation (Gantt/paging/disk/Banker's); SEBI, RBI and NABARD test conceptual recall (definitions, one-liners, MCQs).](images/199_exam_positioning.png)

- **Compute-it exams (GATE, C-DAC/CCAT):** give a *concrete instance* and ask you to
  **trace or calculate** a number — average waiting time, number of page faults,
  effective access time, total head movement, a safe sequence. Practice *doing* the
  arithmetic fast and correctly; reading is not enough.
- **Know-it exams (SEBI IT, RBI IT, NABARD):** objective MCQs across the whole IT
  syllabus (OS + DBMS + Networks + Cyber + emerging tech). OS questions are
  **conceptual** — definitions, "which is true", one-line facts. **Breadth +
  accuracy** beat deep numerical drill here.

> **Memory hook:** *GATE/C-DAC = "compute it"; SEBI/RBI/NABARD = "know it".* Same
> syllabus, opposite question style — so split your prep accordingly.

### Topic × Exam Relevance Matrix (all OS modules M1–M20)

Read down a column to plan a specific exam; read across a row to see where a topic
pays off. (★ = light, ★★★★★ = heavily and repeatedly tested.)

| # | Topic / Module | SEBI IT | RBI IT | NABARD | GATE CS | C-DAC |
|---|----------------|:---:|:---:|:---:|:---:|:---:|
| M1  | Introduction to OS (types, spooling, hypervisor) | ★★★ | ★★★ | ★★★ | ★★ | ★★★ |
| M2  | Computer Hardware Foundations (interrupts, hierarchy) | ★★ | ★★ | ★★ | ★★ | ★★★ |
| M3  | OS Architecture (kernel: monolithic/micro, dual mode) | ★★★ | ★★★ | ★★ | ★★★ | ★★★ |
| M4  | Processes (PCB, states, context switch, IPC, fork) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ |
| M5  | Threads (user/kernel, models, thread vs process) | ★★★ | ★★★ | ★★ | ★★★ | ★★★★ |
| M6  | **CPU Scheduling** (FCFS/SJF/SRTF/RR/priority) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★★ |
| M7  | **Process Synchronization** (semaphores, CS, classics) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ |
| M8  | **Deadlocks** (4 conditions, RAG, Banker's) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ |
| M9  | **Memory Management** (paging, segmentation, fragmentation) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★★ |
| M10 | **Virtual Memory** (demand paging, replacement, TLB, EAT) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★★ |
| M11 | File Systems (inode, allocation, directory, FAT) | ★★★ | ★★★ | ★★ | ★★★★ | ★★★★ |
| M12 | **Disk Management** (disk scheduling, RAID) | ★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ |
| M13 | I/O Systems (polling, interrupt, DMA) | ★★ | ★★ | ★★ | ★★★ | ★★★ |
| M14 | Linux Internals (commands, /proc, scheduler) | ★★★ | ★★★ | ★★ | ★★ | ★★★★ |
| M15 | Concurrency (atomics, memory ordering, lock-free) | ★★ | ★★ | ★★ | ★★★ | ★★★★ |
| M16 | Security (rings, DAC/MAC/RBAC, capabilities, sandboxing) | ★★★ | ★★★ | ★★ | ★★★ | ★★★ |
| M17 | Virtualization (VMs, hypervisors, containers) | ★★★ | ★★★ | ★★ | ★★ | ★★★ |
| M18 | Cloud OS (pooled resources, scheduling at scale) | ★★★ | ★★ | ★★ | ★ | ★★ |
| M19 | AI-Engineering Perspective (GPU scheduling, memory) | ★★ | ★★ | ★ | ★ | ★★ |
| M20 | Backend Engineering (servers, epoll, load balancing) | ★★ | ★★ | ★ | ★★★ | ★★★★★ |

> **How to use it.** For **GATE/C-DAC**, live in the ★★★★★ numerical rows —
> **M6, M7, M8, M9, M10, M12** decide your marks. For **SEBI/RBI/NABARD**, sweep the
> ★★★ conceptual rows broadly (M1, M3, M4, M5, M11, M14, M15, M17) and *understand*
> the numerical topics well enough to answer a conceptual MCQ about them.

---

## 21.2 Per-Exam Strategy

### GATE CS (numerical, trace-and-compute)

- **Format:** MCQ + MSQ + NAT (numerical answer type). OS is a **standalone,
  reliably examined** subject — historically **~5–8 marks** every year, sometimes
  more.
- **Highest-yield (do these until automatic):**
  - **CPU scheduling:** draw the **Gantt chart**, then compute **average waiting
    time / turnaround time**; SJF/SRTF optimality; RR with a given quantum;
    priority + starvation.
  - **Page replacement:** count **page faults** for FIFO / LRU / Optimal on a given
    reference string; **Belady's anomaly** (FIFO only).
  - **Virtual memory:** **EAT with TLB**, demand-paging EAT with a fault rate,
    **multi-level page table** address splitting.
  - **Memory:** paging address translation, internal vs external fragmentation,
    **best/first/worst-fit** placement.
  - **Deadlock:** the four conditions, **Banker's algorithm safe sequence**,
    resource-allocation-graph cycle detection.
  - **Synchronization:** semaphore trace, counting-semaphore value, the
    critical-section requirements, classic-problem correctness.
  - **Disk scheduling:** total **head movement** for FCFS/SSTF/SCAN/C-SCAN/LOOK.
  - **File systems:** **inode max file size** from block/pointer sizes; number of
    disk accesses for indexed/linked allocation.
- **Style:** they give the numbers; you **compute**. Time yourself — a Gantt +
  averages should take < 3 minutes.

### SEBI Grade A (IT) / RBI Grade B (IT) — *your target*

- **Format:** objective MCQs spread across the whole IT syllabus. OS is
  **conceptual** — you will see a handful of one-fact questions, not a full Banker's
  table.
- **Highest-yield:** OS definitions & goals; **process states** and transitions;
  **thread vs process**; scheduling algorithm *properties* (which minimises WT,
  which starves, which is preemptive); **deadlock four conditions**; **semaphore vs
  mutex**; **paging vs segmentation**; **internal vs external fragmentation**;
  **virtual memory / thrashing**; **RAID levels**; **inode / file allocation**;
  basic **Linux commands** and the **fork/exec** idea.
- **Strategy:** **breadth + speed + accuracy.** Learn the one-liners and the traps
  (multiprogramming vs multitasking vs multiprocessing; internal vs external
  fragmentation; preemptive vs non-preemptive). Don't over-invest in long
  numericals — but know *enough* of each to answer a conceptual variant.

### NABARD (Development Assistant / Grade A IT)

- **Format:** general IT/CS awareness with some OS MCQs; lighter and more
  definitional than SEBI/RBI.
- **Highest-yield:** the same conceptual core as SEBI/RBI but shallower —
  definitions, types of OS, basic scheduling names, deadlock conditions, memory
  terms. **Recall over calculation.**

### C-DAC (CCAT — for PG-DAC admission)

- **Format:** aptitude + CS fundamentals; the CS section is **GATE-like but more
  direct**. C programming, DSA, and OS fundamentals matter.
- **Highest-yield:** scheduling numericals, paging/page-fault counts, deadlock
  conditions + Banker's, semaphores, disk scheduling, file allocation — plus quick,
  direct fact MCQs. Expect the **compute** style with a tighter time budget.

> **Memory hook (triage a question in 2 seconds):** *"Trace / compute a number"* →
> GATE/C-DAC skill. *"Which of the following is true about X"* →
> SEBI/RBI/NABARD skill. Prepare both muscles; lead with the one your exam favours.

---

## 21.3 The Formulas to Memorise Cold

These generate the majority of numerical marks. Learn the formula **and** one worked
number for each.

![The six GATE/C-DAC numerical families: scheduling (Gantt→WT/TAT), paging (EAT with TLB), demand paging (fault-rate EAT), disk (head movement), real-time (RMS bound), file system (inode max size).](images/200_gate_numerical_map.png)

### (1) Turnaround & Waiting time (scheduling)

```text
Turnaround Time (TAT) = Completion Time − Arrival Time
Waiting Time    (WT)  = Turnaround Time − Burst (CPU) Time
Response Time         = First-CPU Time  − Arrival Time
Average = (sum over all processes) / (number of processes)
```

> **Worked (FCFS, all arrive at t=0, order P1,P2,P3, bursts 24,3,3):**
> Gantt `P1[0–24] P2[24–27] P3[27–30]`.
> WT = 0, 24, 27 → **avg WT = 51/3 = 17**. TAT = 24, 27, 30 → **avg TAT = 27**.
> Reorder shortest-first (SJF: P2,P3,P1) and **avg WT drops to 3** — SJF is
> *provably optimal* for average waiting time.

### (2) Effective Access Time with a TLB (paging)

```text
EAT = h × (TLB_time + mem_time) + (1 − h) × (TLB_time + 2 × mem_time)
      h = TLB hit ratio ; mem_time = one memory access ; 2× because a miss needs
      one access for the page table + one for the actual data.
(If TLB search time is ignored:  EAT = h × mem + (1 − h) × 2·mem.)
```

> **Worked:** h = 0.8, TLB = 20 ns, memory = 100 ns.
> EAT = 0.8×(20+100) + 0.2×(20+200) = 96 + 44 = **140 ns**.
> (Ignoring TLB time: 0.8×100 + 0.2×200 = **120 ns**.)

### (3) Demand-paging EAT (with a page-fault rate)

```text
EAT = (1 − p) × memory_access + p × page_fault_service_time
      p = page-fault probability ; a fault costs a disk I/O (~ms), so it dominates.
```

> **Worked:** memory = 200 ns, p = 0.001, fault service = 8 ms = 8,000,000 ns.
> EAT = 0.999×200 + 0.001×8,000,000 = 199.8 + 8000 = **8199.8 ns ≈ 8.2 µs** — a
> single fault-in-a-thousand makes memory **~40× slower**. Lesson: keep `p` tiny.

### (4) Rate-Monotonic (RMS) schedulability bound (real-time)

```text
A set of n periodic tasks is RMS-schedulable if  Σ (Ci / Ti) ≤ n·(2^(1/n) − 1)
   Ci = worst-case compute time, Ti = period.  Bound → ln 2 ≈ 0.693 as n → ∞.
   n=1 → 1.000 ; n=2 → 0.828 ; n=3 → 0.780 ; n=4 → 0.757.
```

> **Note:** the bound is **sufficient, not necessary** — a task set above it *may*
> still be schedulable (test exactly). **EDF** (Earliest Deadline First) has a
> higher bound of **1.0** (100% utilisation).

### (5) Disk head movement (disk scheduling)

```text
Total head movement = Σ |current_position − next_position|  over the service order.
  FCFS   : service in request order.
  SSTF   : always the nearest pending request (can starve far ones).
  SCAN   : go one direction to the disk END, reverse (elevator).
  C-SCAN : go to the end, JUMP back to the start, continue one way (fairer waits).
  LOOK / C-LOOK : like SCAN/C-SCAN but reverse at the LAST request, not the edge.
```

> **Worked (requests 82,170,43,140,24,16,190; head at 50; disk 0–199):**
> **FCFS** = 32+88+127+97+116+8+174 = **642**.
> **SSTF** = **208** (nearest-first: 50→43→24→16→82→140→170→190).
> **SCAN toward 199** = (199−50)+(199−16) = 149+183 = **332**.
> **C-SCAN** = (199−50)+(199−0)+(43−0) = 149+199+43 = **391** (counting the jump).

### (6) Inode maximum file size (file systems)

```text
pointers_per_block  = block_size / pointer_size
max_file = ( #direct + PPB + PPB² + PPB³ ) × block_size
           (12 direct + 1 single-indirect + 1 double + 1 triple, UNIX-style)
```

> **Worked:** block = 1 KB, pointer = 4 B → PPB = 256.
> direct 12·1KB = 12 KB; single 256·1KB = 256 KB; double 256²·1KB = 64 MB;
> triple 256³·1KB = **16 GB**. Total ≈ **16.06 GB** (the triple-indirect dominates).
> (Block 4 KB, pointer 4 B → PPB = 1024 → max ≈ **4 TB**.)

---

## 21.4 Frequently-Asked Concepts — Memorise Cold

These one-liners appear again and again across all five exams. Recite until reflex.

- **Two roles of an OS:** resource manager + extended (virtual) machine. Doorway =
  **system call**. Always-resident core = **kernel**.
- **Trap trio:** multiprogramming (many jobs in RAM, 1 CPU switches on I/O) vs
  multitasking (adds rapid time-slices) vs multiprocessing (many CPUs, true
  parallel).
- **Process states:** new → ready → running → waiting(blocked) → terminated. Only
  **one** process runs per CPU at a time. The **PCB** stores a process's context.
- **Context switch** saves/restores the PCB — pure overhead, no useful work.
- **Thread vs process:** threads of one process **share** code/data/heap/files but
  have **own** stack + registers + PC. Threads are cheaper to create/switch.
- **Scheduling one-liners:** FCFS = non-preemptive, convoy effect; **SJF = optimal
  avg WT** (non-preemptive); **SRTF** = preemptive SJF; **RR** = preemptive, fair,
  quantum-driven; priority can **starve** (fix = **aging**).
- **Deadlock 4 (Coffman) conditions (ALL must hold):** mutual exclusion,
  hold-and-wait, no preemption, circular wait. Break any one → prevention.
- **RAG:** a cycle is **necessary** for deadlock; with single-instance resources a
  cycle is also **sufficient**. Banker's = deadlock **avoidance**.
- **Semaphore:** `wait/P/down` decrements (may block); `signal/V/up` increments.
  **Binary semaphore ≈ mutex**; counting semaphore counts instances.
- **Critical-section requirements:** mutual exclusion, **progress**, **bounded
  waiting**. Peterson's solution is software; TSL/`test-and-set` is hardware.
- **Fragmentation:** **internal** = wasted space *inside* a fixed block (paging);
  **external** = free space scattered in unusable gaps (segmentation/variable
  partitions), fixed by **compaction**.
- **Paging vs segmentation:** paging = **fixed** frames, no external frag, invisible
  to user; segmentation = **variable** logical units (code/stack/data), external
  frag, user-visible.
- **Page fault** = referenced page not in RAM → trap → load from disk. **Thrashing**
  = so many faults the CPU spends all its time paging (fix = **working-set** /
  reduce multiprogramming).
- **TLB** = cache of recent page-table entries; a hit avoids the extra page-table
  memory access.
- **Belady's anomaly:** more frames → more faults; happens with **FIFO only**
  (LRU/Optimal are stack algorithms, immune).
- **Disk scheduling:** SSTF can **starve**; **SCAN/C-SCAN** = elevator; C-SCAN gives
  more **uniform** wait times.
- **File allocation:** contiguous (fast, external frag), linked (no random access),
  **indexed/inode** (random access via an index block).
- **RAID:** 0 = striping (no redundancy), 1 = mirroring (50%), 5 = distributed
  parity (min 3), 6 = double parity (min 4), 10 = mirror+stripe.
- **Fork:** `fork()` returns **0 to the child, child-PID to the parent**, −1 on
  failure. A **zombie** = finished child not yet reaped (`wait`); an **orphan** =
  parent died first (re-parented to `init`/PID 1).

---

## 21.5 Solved MCQs by Topic (~50, with answers + one-line explanations)

Every numerical below is recomputed. Cover the answer, attempt, then check.

### A. CPU Scheduling (M6)

1. Non-preemptive scheduling that **minimises average waiting time**? → **SJF**
   (Shortest Job First) — provably optimal for average WT.
2. FCFS, bursts 24, 3, 3 (order P1,P2,P3, all at t=0): average WT? →
   `(0+24+27)/3 =` **17**. (Long job first = **convoy effect**.)
3. Same three jobs under SJF (P2,P3,P1): average WT? → `(0+3+6)/3 =` **3**.
4. Round Robin, quantum 4, bursts P1=24,P2=3,P3=3 (arrive 0, queue P1,P2,P3):
   average WT? → **17/3 ≈ 5.67** (completions P2=7, P3=10, P1=30).
5. SRTF, P1(0,8) P2(1,4) P3(2,9) P4(3,5): average waiting time? → **6.5**
   (completions P1=17, P2=5, P3=26, P4=10 → avg TAT = 13, avg WT = 6.5).
6. Which algorithm suffers the **convoy effect**? → **FCFS** (a long job delays
   short ones behind it).
7. Preemptive version of SJF is called? → **SRTF** (Shortest Remaining Time First).
8. RR with a **very large** time quantum degenerates into? → **FCFS**. With a very
   small quantum? → high **context-switch overhead**.
9. Priority scheduling's classic problem and its fix? → **starvation**, fixed by
   **aging** (gradually raise a waiting job's priority).
10. Which scheduling metric does interactive/time-sharing care about most? →
    **response time**, not turnaround.

### B. Memory Management & Paging (M9, M10)

11. Wasted space *inside* an allocated fixed block is? → **internal
    fragmentation** (typical of paging).
12. Free memory scattered in small unusable gaps is? → **external fragmentation**
    (fixed by **compaction**).
13. Paging eliminates which fragmentation? → **external** (but introduces a little
    **internal** in the last page).
14. Logical address 32-bit, page size 4 KB → bits for page **offset**? →
    `log2(4096) =` **12 bits** (so 20 bits for the page number).
15. EAT with TLB hit ratio 0.8, TLB 20 ns, memory 100 ns? →
    `0.8(120)+0.2(220) =` **140 ns**.
16. Demand paging: memory 200 ns, fault rate 0.001, fault service 8 ms? →
    `0.999(200)+0.001(8,000,000) =` **8199.8 ns ≈ 8.2 µs**.
17. Reference string 1,2,3,4,1,2,5,1,2,3,4,5 with **3 frames, FIFO** → faults? →
    **9**. With **4 frames, FIFO** → **10** — this *increase* is **Belady's
    anomaly**.
18. Which replacement policies are **immune** to Belady's anomaly? → **LRU and
    Optimal** (stack algorithms); **FIFO** is not.
19. The optimal (theoretically best) replacement rule? → evict the page **used
    farthest in the future** (Bélády's OPT — not implementable, used as a
    benchmark).
20. Thrashing is? → excessive paging where the CPU does little useful work; fix
    with the **working-set model** / reduce degree of multiprogramming.
21. A TLB is a cache of? → recent **page-table entries** (page → frame mappings).
22. Multi-level page tables exist to? → avoid keeping one **huge** contiguous page
    table in memory (page the page table itself).
23. Page size doubling tends to → **less** page-table overhead but **more**
    internal fragmentation.

### C. Deadlocks (M8)

24. The four (Coffman) conditions for deadlock? → **mutual exclusion,
    hold-and-wait, no preemption, circular wait** (all four together).
25. Deadlock **prevention** works by? → ensuring at least **one** of the four
    conditions can never hold.
26. Banker's algorithm is a deadlock- ___ technique? → **avoidance** (grants a
    request only if the resulting state is **safe**).
27. Banker's: Available (3,3,2); Needs P0(7,4,3) P1(1,2,2) P2(6,0,0) P3(0,1,1)
    P4(4,3,1); Allocs P0(0,1,0) P1(2,0,0) P2(3,0,2) P3(2,1,1) P4(0,0,2). A safe
    sequence? → **⟨P1, P3, P4, P0, P2⟩** (P1 fits first, freeing resources for the
    rest).
28. In a resource-allocation graph, a **cycle** means deadlock when? → resources
    are **single-instance** (then a cycle is necessary *and* sufficient).
29. A "safe state" guarantees? → there **exists** an order in which all processes
    can finish; a safe state is never a deadlock.
30. Recovery from deadlock by? → **process termination** or **resource
    preemption** (roll back a victim).

### D. Process Synchronization (M7)

31. Requirements a valid critical-section solution must meet? → **mutual
    exclusion, progress, bounded waiting**.
32. `wait()` (a.k.a. **P / down**) on a semaphore does? → **decrement**; if the
    value goes negative the process **blocks**.
33. A binary semaphore is essentially a? → **mutex** (lock) — values 0/1.
34. A counting semaphore initialised to `N` controls? → up to **N** concurrent
    accesses to a resource pool.
35. Peterson's algorithm solves mutual exclusion for? → **two processes**, in
    **software** (needs `flag[]` + `turn`).
36. Hardware primitive giving atomic read-modify-write? → **test-and-set (TSL)** /
    **compare-and-swap**.
37. A **race condition** is? → outcome depends on the **non-deterministic order**
    of concurrent accesses to shared data.
38. In producer–consumer, which semaphores are used? → a **mutex** + counting
    semaphores **empty** and **full**.
39. Dining philosophers can deadlock because of? → **circular wait** on forks; fix
    with resource ordering / at-most-N-1 seated / an arbitrator.
40. Difference between a semaphore and a mutex? → a **mutex** has **ownership**
    (only the locker unlocks); a semaphore is a signalling counter with no owner.

### E. File Systems (M11)

41. UNIX inode with 12 direct pointers, 1 KB blocks, 4 B pointers → **max file
    size**? → ≈ **16 GB** (PPB = 256; triple-indirect 256³·1 KB dominates).
42. Same but 4 KB blocks, 4 B pointers → max size ≈? → **4 TB** (PPB = 1024).
43. File allocation with **no external fragmentation** but **no random access**? →
    **linked allocation**.
44. Allocation giving fast **random access** via an index block? → **indexed
    (inode) allocation**.
45. Contiguous allocation's drawbacks? → **external fragmentation** and hard
    **file growth**.
46. FAT stands for and stores? → **File Allocation Table** — a table of block
    links (a linked list kept in one table for faster random access).
47. What does an inode store? → file **metadata** (size, owner, permissions,
    timestamps, block pointers) — **not** the file name (that's in the directory).

### F. Disk Management (M12)

48. Requests 82,170,43,140,24,16,190; head 50 — **FCFS** total head movement? →
    **642**.
49. Same set — **SSTF** total head movement? → **208** (nearest-first order
    50→43→24→16→82→140→170→190).
50. Same set — **SCAN toward 199** total head movement? → **332**
    (`(199−50)+(199−16)`).
51. Which algorithm can **starve** distant requests? → **SSTF** (always favours the
    nearest).
52. Which gives the most **uniform** waiting time? → **C-SCAN** (services one
    direction then jumps back, treating the disk as circular).
53. Average **rotational latency** = ? → **½ of one full rotation** = `½ × 60/RPM`.

---

## 21.6 Exam, Interview & Coding Perspectives

- **GATE/C-DAC:** the numerical families in §21.3 are the marks. Drill each until a
  Gantt+averages, a page-fault count, an EAT, or a head-movement total takes under
  three minutes with zero arithmetic slips.
- **SEBI/RBI/NABARD:** the §21.4 one-liners and the traps in §21.5's *conceptual*
  MCQs are your bread and butter — accuracy and speed across breadth.
- **Interview crossover:** the *reasons behind* the formulas (why SJF is optimal,
  why FIFO thrashes, why SSTF starves) are exactly what interviewers probe — see
  **Module 22**.

---

## 21.7 One-Page Revision Sheet

```
TWO EXAM CAMPS:  GATE/C-DAC = COMPUTE (Gantt, faults, EAT, head-move, Banker's)
                 SEBI/RBI/NABARD = KNOW  (definitions, one-liners, "which is true")

SCHEDULING:  TAT = Completion − Arrival ;  WT = TAT − Burst ;  Response = firstCPU − Arrival
  SJF = optimal avg WT (non-preemptive) ; SRTF = preemptive SJF ; RR = fair, quantum
  FCFS = convoy effect ; priority -> STARVATION (fix = AGING)

PAGING EAT (with TLB) = h(TLB+mem) + (1−h)(TLB+2·mem)     [h=0.8,20,100 -> 140ns]
DEMAND PAGING EAT     = (1−p)·mem + p·faultservice        [200ns,p=.001,8ms -> ~8.2µs]
PAGE FAULTS: FIFO/LRU/OPTIMAL ; BELADY (more frames->more faults) = FIFO only

DEADLOCK 4 (all): mutual exclusion, hold&wait, no preemption, circular wait
  Banker's = AVOIDANCE (grant only if resulting state SAFE). RAG cycle = deadlock if single-instance.
  Safe seq example: ⟨P1,P3,P4,P0,P2⟩

SYNC: wait/P/down (dec, may block) ; signal/V/up (inc). binary sem ≈ mutex.
  CS needs: MUTUAL EXCLUSION + PROGRESS + BOUNDED WAITING. Peterson(sw,2proc), TSL(hw).

FRAGMENTATION: internal(inside fixed block=paging) vs external(scattered gaps=segmentation, fix=compaction)
PAGING(fixed frames, no ext frag) vs SEGMENTATION(variable, user-visible, ext frag)

DISK head-move = Σ|cur−next|.  FCFS / SSTF(starves) / SCAN,C-SCAN(elevator; C-SCAN uniform waits)
  reqs 82,170,43,140,24,16,190 head50: FCFS=642, SSTF=208, SCAN(->199)=332
Avg rotational latency = 1/2 × 60/RPM.

INODE max = (12 + PPB + PPB² + PPB³) × block ; PPB = block/pointer
  1KB block,4B ptr -> 16GB ;  4KB block,4B ptr -> 4TB.

RMS bound: Σ Ci/Ti ≤ n(2^(1/n)−1) -> ln2≈0.693 ; EDF bound = 1.0.
```

### Flash cards

| Front | Back |
|-------|------|
| SJF is optimal for? | Average waiting time (non-preemptive) |
| Belady's anomaly happens with? | FIFO only |
| EAT with TLB formula? | h(TLB+mem)+(1−h)(TLB+2·mem) |
| Deadlock four conditions? | Mutual excl., hold&wait, no preempt, circular wait |
| Banker's algorithm is? | Deadlock avoidance (safe state) |
| CS requirements? | Mutual exclusion, progress, bounded waiting |
| Internal vs external frag? | Inside a fixed block vs scattered gaps |
| SSTF drawback? | Starvation of far requests |
| Inode max size? | (12+PPB+PPB²+PPB³)×block |
| Semaphore wait/signal? | Decrement (may block) / increment |

### Spaced repetition
- **24-hour:** redo one Gantt (FCFS+SJF), one page-fault count (FIFO 3f vs 4f), one
  EAT, one disk head-movement — all from scratch.
- **7-day:** recite the §21.4 concept list; state each scheduling algorithm's
  one-line property and the four deadlock conditions.
- **30-day:** given any numerical prompt, pick the right formula family from §21.3
  and compute the answer without notes.

---

## 21.8 Summary

The five exams split cleanly into **compute-it (GATE, C-DAC)** and **know-it
(SEBI, RBI, NABARD)**. We built the **topic × exam matrix** across all twenty OS
modules, gave **per-exam strategy**, and drilled the **six formula families** that
generate the numerical marks — **TAT/WT** (with SJF optimal), **EAT with TLB** and
**demand-paging EAT**, **page-fault counts + Belady's anomaly**, **Banker's safe
sequence**, **disk head movement**, and **inode max file size** — every worked
number recomputed. We compiled the **memorise-cold** concept list and **~50 solved
MCQs** grouped by scheduling, memory/paging, deadlock, synchronization, file
systems, and disk. Practise the compute muscle for GATE/C-DAC and the recall muscle
for SEBI/RBI/NABARD, and you can walk into any of these papers and pick up the OS
marks fast.

Next, **Module 22 — Interview Preparation** turns the same material outward:
how FAANG and backend/AI-infra interviews probe *why* these mechanisms work, plus
scenario and production-debugging questions. After that, **Module 23 — Hands-On
Projects** and **Module 24 — The Revision Kit** close the course.

> **You have mastered this module when** you can: state which of the five exams
> wants computation vs recall; reproduce all six formula families with one worked
> number each; compute a Gantt's average WT, a FIFO/LRU fault count, an EAT, a
> Banker's safe sequence, and a disk head-movement total from scratch; and rattle
> off the §21.4 concept one-liners without notes.
