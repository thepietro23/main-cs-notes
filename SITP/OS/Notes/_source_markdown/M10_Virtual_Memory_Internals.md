---
title: "Module 10 — Virtual Memory Internals"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10 — Virtual Memory Internals

> **Where this module sits.**
> Module 9 made many processes share RAM through **paging** — but every page of
> a running process still had to be **physically present** in memory. Virtual
> memory removes that final constraint: a process can run **even if only part of
> it is in RAM**, so programs can be **larger than physical memory** and far more
> of them can run at once. The magic hook is the **valid bit** from §9.10 — touch
> a page that isn't resident and the hardware raises a **page fault**, which the
> OS quietly services by fetching the page from disk. That single mechanism gives
> us **demand paging**, and it forces the two biggest questions of this module:
> *which page do we evict when RAM is full* (**page-replacement algorithms**) and
> *what happens when there isn't enough RAM to go around* (**thrashing**). This is
> a **GATE goldmine** — **page-fault counting** on a reference string (FIFO,
> Optimal, LRU) and **Belady's anomaly** appear almost every year.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **page fault** &
step-by-step handling; **demand paging** (pure demand paging); **page-replacement
algorithms** with page-fault counts — **FIFO**, **Optimal (OPT)**, **LRU**,
**clock/second-chance**; **Belady's anomaly**; **frame allocation** (equal vs
proportional); **thrashing** + **working-set model** + **page-fault frequency**;
**copy-on-write** (`fork`); **memory-mapped files**; **shared memory**; **memory
protection bits**.

---

## 10.1 What Is Virtual Memory?

**Virtual memory** is a technique that lets a process execute while **only some of
its pages are in physical memory**; the rest sit on disk (in a **swap area** /
page file) and are brought in **on demand**. The process is given a **large,
contiguous virtual address space** that is *bigger than* physical RAM; the OS +
MMU maintain the illusion.

**Why it is transformative:**

- **Programs can exceed RAM** — a 4 GB program runs on a 1 GB machine.
- **Higher multiprogramming** — each process occupies less RAM, so **more
  processes fit**, keeping the CPU busier.
- **Faster start-up & less I/O** — load only what's actually used (a huge binary
  starts instantly; unused features never load).
- Enables **shared pages**, **copy-on-write**, and **memory-mapped files**
  (§10.9–10.11).

> **Memory hook:** virtual memory is a **library with a small reading desk**. You
> don't carry the whole library (disk) to your desk (RAM) — you fetch a book (page)
> **only when you open it**, and return one to the shelf when the desk is full.

### MCQs

1. Virtual memory lets a program be? → **larger than physical RAM**.
2. Where do non-resident pages live? → on **disk** (swap / page file).
3. One key benefit besides "big programs"? → **higher degree of
   multiprogramming**.

---

## 10.2 Demand Paging and the Page Fault

### Demand paging

In **demand paging**, a page is loaded into RAM **only when it is referenced** —
never in advance. Each PTE has a **valid/invalid bit** (§9.10):

- **valid** → the page is in RAM at the recorded frame.
- **invalid** → the page is **not in memory** (it's on disk, or illegal). Touching
  it raises a **page fault**.

**Pure demand paging** takes this to the extreme: **start a process with *zero*
pages in memory**. The very first instruction faults, its page is brought in, and
the process pages everything in **purely on demand** — nothing is pre-loaded.

### The page fault — full step-by-step handling (know this cold)

A **page fault** is a trap raised by the MMU when a program references a page
whose PTE is **invalid**. The OS handles it as follows:

![Page-fault handling: the MMU traps on an invalid PTE; the OS checks the reference is legal, finds a free frame (or evicts a victim), schedules the disk read of the page, updates the page table to valid, and restarts the faulting instruction.](images/97_page_fault_handling.png)

```text
1. MMU checks PTE -> valid bit = invalid  -> TRAP to the OS (page fault).
2. OS checks an internal table: is the reference LEGAL?
      illegal (outside address space) -> terminate process (segfault).
      legal but not resident          -> continue below.
3. Find a FREE FRAME (from the free-frame list).
      none free -> run PAGE REPLACEMENT: pick a VICTIM frame;
                   if victim is DIRTY, write it back to disk first.
4. Schedule a DISK READ to load the desired page into the frame.
      (process is BLOCKED; CPU may run another process meanwhile)
5. Disk read completes -> interrupt. Update the PAGE TABLE:
      set frame number, set valid bit = valid.
6. RESTART the instruction that faulted -> now the access succeeds.
```

> **Key subtlety — instruction restart.** A page fault can occur **in the middle
> of an instruction** (e.g. a block-move touching two pages). The hardware must
> **restart the whole instruction** cleanly after the page is in — otherwise state
> would be corrupted. This is why page-fault handling needs careful hardware
> support.

> **Effective access time with page faults (a numerical you may see).**
> Let `p` = page-fault rate, `ma` = memory-access time, `pf` = page-fault service
> time. Then
> `EAT = (1 − p) × ma + p × pf`.
> **Worked:** `ma = 200 ns`, `pf = 8 ms = 8,000,000 ns`, `p = 0.001` (1 in 1000).
> `EAT = 0.999 × 200 + 0.001 × 8,000,000 ≈ 200 + 8000 =` **~8200 ns** — a **~40×**
> slowdown from just **0.1%** faults! This is why keeping the fault rate tiny (via
> good replacement + enough frames) is everything.

### MCQs

1. When is a page loaded in demand paging? → only when **referenced** (on the
   fault).
2. What raises a page fault? → referencing a page whose PTE is **invalid**.
3. Pure demand paging starts a process with how many pages? → **zero**.
4. After servicing a fault, what does the CPU do? → **restart the faulting
   instruction**.

---

## 10.3 Page Replacement — The Setup

When a page fault occurs and **no frame is free**, the OS must **evict** a
resident page to make room — this is **page replacement**. We want the algorithm
that yields the **fewest page faults** on a program's **reference string** (the
sequence of page numbers it accesses).

**The universal procedure for tracing (and counting faults):**

```text
- Keep the set of pages currently in the frames.
- For each reference:
    if the page is already in a frame  -> HIT (no fault).
    else                               -> FAULT:
        if a free frame exists         -> load it there.
        else                           -> pick a VICTIM by the algorithm's rule,
                                          evict it, load the new page.
- Page faults = number of misses. (The first N distinct pages are always faults =
  "cold-start" / compulsory misses.)
```

We now trace **FIFO, Optimal, and LRU** on **one** standard reference string with
**3 frames**, so you can compare fault counts directly:

> **Reference string (Silberschatz standard):**
> `7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1`, with **3 frames**, all initially
> empty.

---

## 10.4 FIFO and Belady's Anomaly

### FIFO (First-In, First-Out)

**Rule:** evict the page that has been in memory **longest** (the oldest arrival)
— a simple queue, regardless of how heavily it's used.

```text
ref: 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1
     F  F  F  F  H  F  F  F  F  F  F  H  H  F  F  H  H  F  F  F      (F=fault,H=hit)

     7  7  7  2  .  2  2  4  4  4  0  .  .  0  2  .  .  7  7  1   <- frame contents
        0  0  0  .  3  3  3  2  2  2  .  .  3  3  .  .  1  1  7   (queue; oldest evicted)
           1  1  .  1  0  0  0  3  3  .  .  1  1  .  .  2  2  0
Page faults = 15
```

FIFO is trivial but **ignores usage** — it can evict a heavily used page just
because it arrived first, so it performs poorly.

### Belady's anomaly (a must-know exam trap)

Intuition says **more frames → fewer faults**. For **FIFO this can be FALSE**:
adding a frame can *increase* faults. This is **Belady's anomaly**.

> **Classic worked example.** Reference string
> `1 2 3 4 1 2 5 1 2 3 4 5`, using **FIFO**.

**With 3 frames:**

```text
ref: 1 2 3 4 1 2 5 1 2 3 4 5
     F F F F F F F H H F F H
Page faults = 9
```

**With 4 frames:**

```text
ref: 1 2 3 4 1 2 5 1 2 3 4 5
     F F F F H H F F F F F F
Page faults = 10
```

> **The anomaly:** going from **3 → 4** frames made faults go **9 → 10** — *more*
> memory, *more* faults! **Only FIFO** (and some others) suffer this.
> **Stack algorithms — LRU and OPT — are immune** (their set of pages with *n*
> frames is always a superset of the set with fewer frames, so faults can never
> increase).

### MCQs

1. FIFO evicts which page? → the **oldest** (first-in).
2. FIFO faults on the standard string, 3 frames? → **15**.
3. Belady's anomaly means? → **more frames → more faults** (possible under FIFO).
4. Which algorithms are immune to it? → **LRU and Optimal** (stack algorithms).

---

## 10.5 Optimal (OPT / MIN) — The Theoretical Best

**Rule:** evict the page that **will not be used for the longest time in the
future**. This gives the **provably lowest** possible number of faults — but it
needs **future knowledge**, so it's **unimplementable**. It exists as the
**benchmark** you measure real algorithms against.

```text
ref: 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1
     F  F  F  F  H  F  H  F  H  H  F  H  H  F  H  H  H  F  H  H
Page faults = 9      <- the minimum achievable on this string with 3 frames
```

> **How to pick the victim by hand:** at a fault, look **forward** in the string
> for each resident page; the one whose next use is **farthest away** (or never
> used again) is the victim. Example at ref `2` (step 4), resident `{7,0,1}`: 7's
> next use is far (position 18), 0's is soon (position 5), 1's is later (position
> 14) → evict **7** (farthest future use).

### MCQs

1. OPT evicts the page? → **used farthest in the future**.
2. Why isn't OPT implementable? → needs **future knowledge**.
3. OPT faults on the standard string, 3 frames? → **9** (the minimum).

---

## 10.6 LRU and Its Approximations

### LRU (Least Recently Used)

**Rule:** evict the page **unused for the longest time** — use the **past** as a
proxy for the future (locality: recently used → likely used again). LRU is the
best *practical* algorithm and is **immune to Belady's anomaly**.

```text
ref: 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1
     F  F  F  F  H  F  H  F  F  F  F  H  H  F  H  F  H  F  H  H
Page faults = 12     <- between OPT (9) and FIFO (15)
```

**Fault comparison on the standard string (3 frames):**

| Algorithm | Page faults | Note |
|-----------|:-----------:|------|
| **Optimal (OPT)** | **9** | theoretical best (needs the future) |
| **LRU** | **12** | best practical; immune to Belady |
| **FIFO** | **15** | simplest; suffers Belady's anomaly |

> **Ordering to remember:** `OPT ≤ LRU ≤ FIFO` (Optimal is always best; LRU
> usually beats FIFO because it respects usage).

### Why exact LRU is expensive

Exact LRU must know the **recency order** on every access. Implementations:

- **Counters/timestamps** — stamp each PTE with a clock on every reference; evict
  the smallest. Needs a memory **write on every access** + a search → costly.
- **Stack** — move the referenced page to the top of a doubly-linked stack;
  bottom = LRU. Costly pointer updates per reference.

Because both are too slow in hardware, real systems use **approximations** built
on the **reference (accessed) bit** (§9.10).

### Clock / Second-Chance (the practical LRU approximation)

Each frame has a **reference bit** the hardware sets to 1 on use. Frames sit in a
**circular list** with a "clock hand." On a fault, the hand advances:

- reference bit **1** → give a **second chance**: clear it to **0**, move on.
- reference bit **0** → this is the **victim**; evict it, load the new page (bit 1).

```text
ring of frames, each [page:refbit], hand -> advances until it finds refbit 0

fault: hand at [A:1] -> clear to [A:0], advance
                [B:1] -> clear to [B:0], advance
                [C:0] -> VICTIM: evict C, load new page as [X:1]
```

So a page gets a "second chance" if it's been used since the hand last passed —
approximating LRU with just **O(1)** work and a single bit, **no timestamps**.

- **Enhanced second-chance** uses **(reference, dirty)** as an ordered pair,
  preferring to evict **(0,0)** — not recently used *and* clean (no write-back)
  — before **(0,1)**, **(1,0)**, **(1,1)**. Saves disk writes.

> **Memory hook:** clock = a **security guard** walking a circle of doors. A door
> flagged "recently opened" (bit 1) gets its flag wiped and a **second chance**;
> the first door found already **un-flagged** (bit 0) is the one evicted.

### MCQs

1. LRU evicts the page? → **least recently used** (longest unused).
2. LRU faults on the standard string, 3 frames? → **12**.
3. What bit does clock/second-chance use? → the **reference (accessed)** bit.
4. Clock gives a page a second chance when its reference bit is? → **1** (clears
   it and moves on).
5. Is LRU subject to Belady's anomaly? → **No** (stack algorithm).

---

## 10.7 Frame Allocation — How Many Frames per Process?

With many processes, how do we split the free frames among them? Two schemes:

- **Equal allocation** — split frames **equally**: `m` frames, `n` processes →
  `m/n` each. Simple, but unfair to big processes and wasteful for tiny ones.
- **Proportional allocation** — give frames **in proportion to process size**:
  process `i` of size `s_i` gets `a_i = (s_i / Σs) × m` frames. Bigger processes
  get more.

> **Worked example.** `m = 62` frames, two processes: `s1 = 10` KB, `s2 = 127` KB.
> Proportional: `a1 = (10/137)×62 ≈ 4.5 → 4`, `a2 = (127/137)×62 ≈ 57.5 → 57`.
> (Compare equal: 31 each — the tiny process would waste most of its 31.)

**Global vs local replacement** (a separate, tested axis):

- **Local replacement** — a process may only evict **its own** frames; its fault
  rate depends only on its own behavior (predictable, but can't borrow from idle
  processes).
- **Global replacement** — a process may evict **any** process's frame; better
  throughput, but a process's fault rate now depends on **others** (unpredictable,
  and a key ingredient of **thrashing**). Most systems use **global**.

### MCQs

1. Equal vs proportional allocation? → same count each vs **by process size**.
2. Proportional frames for a 10 KB process of {10,127} KB with 62 frames? → **~4**.
3. Global replacement lets a process evict? → **any** process's frame.

---

## 10.8 Thrashing, the Working-Set Model, and PFF

### Thrashing (the failure mode)

If a process has **too few frames** to hold its **active working set**, it faults
constantly — every fetched page immediately evicts another page it's about to need
again. The process spends **more time paging than computing**. When many
processes do this at once (under **global** replacement, they steal each other's
frames), CPU utilization **collapses** — this is **thrashing**.

![Thrashing curve: CPU utilization rises with the degree of multiprogramming until the working sets no longer fit in RAM, after which utilization collapses as processes spend all their time paging.](images/98_thrashing_curve.png)

> **The classic trap.** As you add processes, CPU utilization rises... then past a
> point it **plunges**: the scheduler, seeing idle CPU, adds *even more* processes
> (a vicious cycle), making it worse. **The fix is to *reduce* the degree of
> multiprogramming** (suspend/swap out some processes), not add more.

### Working-set model (the principle behind the fix)

The **working set** `W(t, Δ)` is the set of **distinct pages a process
referenced in the last `Δ` references** (its working-set window). By the
**locality principle**, this is roughly the set it will need **next**.

- Let `WSS_i` = working-set size of process `i`. Total demand `D = Σ WSS_i`.
- If `D > m` (total frames) → **thrashing**. The OS should keep `D ≤ m` by
  **suspending** processes until demand fits.
- **Give each process enough frames to hold its working set** → it faults rarely.

> **Worked idea.** `Δ = 10` references, window = `2 6 1 5 7 7 7 5 1 6` → distinct
> pages `{1,2,5,6,7}` → **WSS = 5** frames needed right now. If we grant ≥5 frames,
> this process runs smoothly; fewer, and it thrashes.

### Page-Fault Frequency (PFF) — the practical control loop

Directly measuring the working set is expensive. **PFF** controls frames using the
**observed fault rate** with an upper and lower bound:

```text
if fault rate > UPPER bound  -> process needs more locality -> GIVE it a frame.
if fault rate < LOWER bound  -> it has spare frames         -> TAKE a frame away.
if no frames to give and rate too high -> SUSPEND a process (reduce multiprogramming).
```

> **Memory hook:** the **working-set model** *predicts* how many frames a process
> needs; **PFF** *reacts* to how many it's actually short of. Both aim at the same
> target — keep each process's hot pages resident so the fault rate stays low.

### MCQs

1. Thrashing is? → spending more time **paging than computing** (fault storm).
2. Fix for thrashing? → **reduce the degree of multiprogramming** (suspend/swap
   out).
3. Working set `W(t,Δ)` = ? → distinct pages used in the **last Δ references**.
4. Thrashing condition? → `Σ WSS > m` (demand exceeds frames).
5. PFF raises a process's frames when its fault rate is? → **above the upper
   bound**.

---

## 10.9 Copy-on-Write (COW) — the trick behind `fork`

When a process calls **`fork()`**, the child is a copy of the parent's entire
address space — but copying every page immediately would be enormously wasteful,
especially since the child often calls **`exec()`** right away and throws it all
away. **Copy-on-write** avoids the copy:

- Parent and child **share the same physical frames**, all marked **read-only**.
- Reads by either just read the shared pages — **no copying**.
- The **first write** to a shared page triggers a **protection fault**; the OS
  then **copies just that one page**, makes the writer's copy writable, and lets
  the write proceed.

![Copy-on-write after fork: parent and child share read-only frames; only when one writes a page does the OS duplicate that single page, so unmodified pages are never copied.](images/99_cow_fork.png)

```text
fork():   child page table = copy of parent's, ALL entries read-only, frames SHARED.
read:     either process reads shared frame        -> fine, nothing copied.
write P:  protection fault -> OS copies frame of P -> writer gets private writable copy;
          other process keeps the original. Only touched pages are ever duplicated.
```

> **Why it matters:** `fork()` is **fast and cheap** even for a huge process,
> because almost nothing is copied. Only pages that are actually **modified** get
> their own frame. This is one of the most important optimizations in Unix.

### MCQs

1. What does COW share after `fork`? → the parent's frames, marked **read-only**.
2. When is a page actually copied? → on the **first write** to it (protection
   fault).
3. Why does COW make `fork` cheap? → **no eager copy**; copy only modified pages.

---

## 10.10 Memory-Mapped Files

**Memory mapping** (`mmap`) maps a **file directly into a process's address
space**, so the file's bytes appear as ordinary memory. Instead of `read()`/
`write()` syscalls, the program just **dereferences pointers**; the OS pages the
file in **on demand** (a page fault reads the corresponding file block) and
**writes dirty pages back** to the file.

- **Pro:** no explicit read/write syscalls; the buffer-cache/page-cache does the
  I/O lazily; **large files** processed without loading them fully; a mapped file
  can be **shared** between processes (shared mapping) for fast IPC.
- Executables and shared libraries are loaded via memory mapping — which is *why*
  demand paging can start a program before fully reading its binary.

> **Memory hook:** `mmap` turns **"file I/O"** into **"array indexing"** — you
> read/write the file by touching memory, and the page-fault mechanism moves the
> bytes for you.

### MCQs

1. What does `mmap` do? → maps a **file into the address space** (access as
   memory).
2. How is a mapped file's data brought in? → **on demand via page faults**.

---

## 10.11 Shared Memory and Memory Protection

### Shared memory (fastest IPC)

Two processes can map the **same physical frames** into both address spaces
(POSIX `shm_open`+`mmap`, or System V `shmget`/`shmat`). Once set up, they
communicate by **reading/writing the same memory** — **no kernel copy per
message**, so it is the **fastest IPC** (but needs synchronization — semaphores/
mutexes — to avoid races, tying back to the concurrency modules).

### Memory protection bits (recap, in the VM context)

The PTE control bits (§9.10) are what make virtual memory safe and powerful:

| Bit | Role in virtual memory |
|-----|------------------------|
| **valid/invalid** | **triggers the page fault** that drives demand paging |
| **read/write/execute** | enforces read-only sharing, **NX** data, COW (read-only until write) |
| **dirty** | decides whether a victim must be **written back** on eviction |
| **reference** | powers **clock/second-chance** replacement |

> COW, memory-mapped files, and shared memory are all the **same core idea** —
> multiple page-table entries pointing at (or faulting into) physical frames,
> governed by these protection bits.

### MCQs

1. Fastest IPC mechanism? → **shared memory** (no per-message copy).
2. Which bit makes read-only sharing and COW possible? → the **write/protection**
   bit.

---

## 10.12 Real-World & Backend Perspectives

- **Swap & the OOM killer:** Linux swaps cold pages to disk; when memory is truly
  exhausted it invokes the **OOM killer**. Heavy swapping *is* thrashing — you see
  it as a machine that goes unresponsive with the disk light solid.
- **`fork()` + COW** underlies process creation everywhere (shells, web servers
  like the classic Apache prefork, `Gunicorn` workers). Copy-on-write is why
  spawning a big Python/JVM process is cheap — until it writes and pages diverge.
- **Redis persistence** relies on COW: `BGSAVE` forks and dumps the snapshot while
  the parent keeps serving; only pages modified during the save get duplicated.
- **`mmap` in databases:** some engines (older MongoDB MMAPv1, LMDB, SQLite) map
  data files and let the OS page cache do the caching — the buffer-pool discussion
  from storage, delegated to the kernel.
- **Containers** set memory **cgroups**; exceeding the limit triggers reclaim/OOM
  — production tuning is largely about keeping each service's **working set**
  within its cgroup so it doesn't thrash.

---

## 10.13 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**

- **Miscounting page faults:** forgetting the first *N* distinct references are
  **always** faults (compulsory), or mis-tracking recency (LRU) / arrival (FIFO).
- Assuming **more frames always help** — false for **FIFO** (Belady's anomaly).
- Claiming **LRU or OPT** suffer Belady's anomaly — they **don't** (stack
  algorithms).
- Confusing **OPT's rule** (farthest **future** use) with LRU's (farthest **past**
  use).
- Thinking the fix for thrashing is **more processes** — it's **fewer** (reduce
  multiprogramming).
- Believing `fork()` copies all memory — it uses **copy-on-write**.

**Edge cases**

- **Belady's anomaly** only for FIFO-like (non-stack) algorithms.
- **Pure demand paging**: even the first instruction faults (nothing preloaded).
- A **dirty** victim costs an **extra disk write** on eviction — enhanced
  second-chance prefers clean victims to avoid it.
- COW's benefit vanishes if the child **writes everything** (then you pay for the
  copies anyway).

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Demand paging | run big programs; fast start; more processes | page-fault latency (~ms) |
| More frames per process | fewer faults | fewer processes fit |
| Global replacement | better throughput | fault rate depends on others (thrash risk) |
| LRU vs FIFO | far fewer faults; no Belady | needs reference tracking (use clock) |
| COW | cheap `fork` | first-write fault; copies if heavily written |

---

## 10.14 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** page-fault counting on a reference string for FIFO /
OPT / LRU; **Belady's anomaly** (the `1 2 3 4 1 2 5 1 2 3 4 5` example); EAT with
page-fault rate; working-set size; thrashing condition `ΣWSS > m`; clock/second-
chance mechanics; frame allocation (equal vs proportional); COW.

**Interview:** "What happens on a page fault, step by step?"; "FIFO vs LRU vs
Optimal?"; "What is thrashing and how do you fix it?"; "How does `fork()` avoid
copying memory?" (COW); "What is `mmap` and when would you use it?"

**Coding/practical:**

- `/proc/<pid>/status` (VmRSS), `vmstat` columns `si`/`so` (swap in/out — nonzero
  under thrashing), `sar -B` for page-fault stats, `time -v` shows "Major
  (requiring I/O) page faults."
- `getrusage()` reports `ru_majflt` (faults that hit disk) vs `ru_minflt` (served
  from memory, e.g. COW).

---

## 10.15 Concept Checks & MCQs

1. Virtual memory lets a program be? → **larger than physical RAM**.
2. Demand paging loads a page? → only when **referenced** (on the fault).
3. What raises a page fault? → an **invalid** PTE on reference.
4. Last step of page-fault handling? → **restart the faulting instruction**.
5. FIFO evicts? → the **oldest** page.
6. FIFO faults, standard string, 3 frames? → **15**.
7. OPT evicts? → page used **farthest in the future**; **9** faults on the string.
8. LRU evicts? → **least recently used**; **12** faults on the string.
9. Fault ordering OPT/LRU/FIFO? → `9 ≤ 12 ≤ 15` (OPT best).
10. Belady's anomaly? → **more frames → more faults** (FIFO).
11. Algorithms immune to Belady? → **LRU, OPT** (stack algorithms).
12. Clock uses which bit? → **reference (accessed)**.
13. Second chance is given when reference bit = ? → **1** (clear it, move on).
14. Equal vs proportional allocation? → same each vs **by size**.
15. Global replacement can evict? → **any** process's frame.
16. Thrashing = ? → more time **paging than computing**.
17. Fix for thrashing? → **reduce** the degree of multiprogramming.
18. Working set = ? → distinct pages in the **last Δ references**.
19. Thrashing condition? → **ΣWSS > m**.
20. PFF adds frames when fault rate is? → **above the upper bound**.
21. What makes `fork()` cheap? → **copy-on-write**.
22. When does COW copy a page? → on the **first write** (protection fault).
23. `mmap` maps a? → **file into the address space**.
24. Fastest IPC? → **shared memory**.

**True/False**

- Optimal page replacement is implementable in practice. → **False** (needs the
  future).
- LRU can suffer Belady's anomaly. → **False**.
- FIFO can suffer Belady's anomaly. → **True**.
- Pure demand paging preloads the first page. → **False** (starts with zero).
- `fork()` immediately copies all of the parent's memory. → **False** (COW).
- The reference bit powers the clock algorithm. → **True**.

**Numerical (do it):**

> Reference string `1 2 3 4 1 2 5 1 2 3 4 5`. FIFO faults with **3** frames vs
> **4** frames? → **9** vs **10** (Belady's anomaly).

> `ma = 100 ns`, page-fault service `pf = 10 ms`, fault rate `p = 0.0005`.
> `EAT = (1−p)·ma + p·pf = 0.9995×100 + 0.0005×10,000,000 ≈ 100 + 5000 =` **~5100
> ns** (a ~51× slowdown from a 0.05% fault rate).

---

## 10.16 One-Page Revision Sheet

```
VIRTUAL MEMORY: run a process with only SOME pages in RAM; rest on disk (swap).
  -> programs bigger than RAM; more processes fit; faster start. Hook = VALID bit.

DEMAND PAGING: load a page only when referenced. PURE demand paging = start with 0 pages.
PAGE FAULT (invalid PTE -> trap): 1 check legal? 2 find free frame (else REPLACE victim;
  if DIRTY write back) 3 disk read page in (process blocked) 4 set frame+valid 5 RESTART instr.
  EAT = (1-p)*ma + p*(fault service).  e.g. ma200ns,pf8ms,p0.001 -> ~8200ns (40x slowdown).

PAGE REPLACEMENT (fewest faults). Standard string 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1, 3 frames:
  FIFO  = evict OLDEST arrival.               faults = 15
  OPT   = evict page used FARTHEST in future. faults = 9  (min; needs future -> not real)
  LRU   = evict LEAST RECENTLY USED.          faults = 12 (best practical)
  order: OPT <= LRU <= FIFO.

BELADY'S ANOMALY: more frames -> MORE faults (FIFO only!). string 1 2 3 4 1 2 5 1 2 3 4 5:
  3 frames = 9 faults, 4 frames = 10 faults.  LRU & OPT immune (STACK algorithms).

LRU APPROX = CLOCK / SECOND-CHANCE: ring + REFERENCE bit. bit1 -> clear, second chance;
  bit0 -> evict. O(1), no timestamps. Enhanced = (ref,dirty), prefer (0,0) clean victim.

FRAME ALLOCATION: EQUAL (m/n each) vs PROPORTIONAL (by size s_i/Ss * m).
  LOCAL replace (own frames only) vs GLOBAL (any frame; better throughput; thrash risk).

THRASHING: too few frames -> constant faults -> CPU util COLLAPSES. FIX = REDUCE multiprogramming.
  WORKING SET W(t,D) = distinct pages in last D refs (~ what it needs next). thrash if SUM WSS > m.
  PFF: fault rate > upper -> give frame; < lower -> take frame; else suspend a process.

COW (fork!): child shares parent frames READ-ONLY; first WRITE -> copy just that page.
  -> fork cheap, copy only modified pages. (Redis BGSAVE, web server workers.)
MMAP: map FILE into address space; access as memory; paged in on demand, dirty pages written back.
SHARED MEMORY = map same frames in 2 processes = FASTEST IPC (needs sync).
PROTECTION BITS: valid(fault) | R/W/X(NX, COW) | dirty(writeback) | reference(clock).
```

### Flash cards

| Front | Back |
|-------|------|
| Virtual memory enables? | Programs larger than RAM; more multiprogramming |
| Page loaded when? (demand paging) | Only when referenced (on fault) |
| Pure demand paging starts with? | Zero pages in memory |
| Last step of fault handling? | Restart the faulting instruction |
| FIFO / OPT / LRU faults (std string, 3 frames)? | 15 / 9 / 12 |
| Belady's anomaly? | More frames → more faults (FIFO) |
| Immune to Belady? | LRU and Optimal (stack algorithms) |
| OPT rule? | Evict page used farthest in the future |
| Clock uses which bit? | Reference (accessed) bit |
| Thrashing fix? | Reduce degree of multiprogramming |
| Working set? | Distinct pages in last Δ references |
| Thrashing condition? | Σ working-set sizes > frames |
| What makes fork cheap? | Copy-on-write |
| COW copies a page when? | On first write (protection fault) |
| Fastest IPC? | Shared memory |

### Spaced repetition
- **24-hour:** trace FIFO, OPT, LRU on the standard string and get 15 / 9 / 12;
  redo the Belady 3→4 frame example (9→10).
- **7-day:** recite the page-fault handling steps; explain clock/second-chance;
  state the thrashing condition and its fix.
- **30-day:** explain COW, `mmap`, and shared memory as one idea (page-table
  entries + protection bits), and compute an EAT-with-faults numerical — no notes.

---

## 10.17 Summary

Virtual memory lets a process run with only part of it in RAM, so **programs can
exceed physical memory** and more of them can run at once. The mechanism is
**demand paging**: an **invalid PTE** raises a **page fault**, and the OS finds a
frame (evicting a victim if needed), reads the page from disk, marks it valid, and
**restarts the instruction** — a rare fault is fine, but even a **0.1%** fault
rate causes a ~40× slowdown, so we minimize faults with good **page replacement**.
On the standard reference string with 3 frames, **FIFO = 15**, **LRU = 12**, and
**Optimal = 9** faults (`OPT ≤ LRU ≤ FIFO`); **FIFO alone suffers Belady's
anomaly** (`1 2 3 4 1 2 5 1 2 3 4 5`: 3 frames → 9, 4 frames → 10 faults), while
**LRU and OPT are immune**. Because exact LRU is expensive, real systems
approximate it with **clock/second-chance** using the **reference bit**. We
allocate frames **equally or proportionally**, chose **global vs local**
replacement, and saw that too few frames cause **thrashing** — fixed by
**reducing multiprogramming**, guided by the **working-set model** (`ΣWSS > m` ⇒
thrash) and **page-fault frequency** control. Finally, **copy-on-write** makes
`fork()` cheap, **memory-mapped files** turn file I/O into pointer access, and
**shared memory** is the fastest IPC — all the same idea of page-table entries and
**protection bits** pointing at physical frames.

This completes the memory-management pair (M9–M10). Next comes the **file system**
and **I/O** layers, where the same themes — caching, on-demand loading, and hiding
slow disks — reappear one level up.

> **You have mastered this module when** you can: list the page-fault handling
> steps from memory; trace FIFO, OPT, and LRU to the correct fault counts and
> demonstrate Belady's anomaly; explain clock/second-chance with the reference
> bit; state the thrashing condition and its fix via the working-set/PFF models;
> and explain copy-on-write, memory-mapped files, and shared memory — all without
> notes.
