---
title: "Module 23 — Hands-On OS Projects (Build to Understand)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 23 — Hands-On OS Projects (Build to Understand)

> **Where this module sits.**
> Modules 1–20 taught you the *theory* — processes, scheduling, memory, file
> systems, Linux internals. This is the **capstone lab**: you now **build small
> versions of the OS yourself**. Nothing cements "what is a context switch" like
> writing one with `ucontext`; nothing explains fragmentation like watching your own
> `malloc` leak it. Each project is a **one-weekend build** that turns a chapter of
> theory into ~200 lines of C you can put on GitHub and defend in an interview. This
> module is the bridge between *knowing* OS and *being able to say you have written
> one.* The revision kit that follows (M24) then compresses everything for the exam.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★      | ★★     | ★★      | ★★★★★     | ★★★★★   |

**What this module gives you:** these projects are **low weight for written exams**
but **the single highest-leverage thing for interviews and real backend/AI-infra
work.** A candidate who has *built* a shell, an allocator, and a thread library
answers "how does `fork` work", "explain a page fault", and "what is a context
switch" from **muscle memory**, not memorisation. Every project below explicitly
links back to the module whose theory it makes real.

---

## 23.1 How to Use This Module (the build method)

Each project follows the same template so you can pick one up in a weekend:

1. **What you build** — the one-line goal and scope.
2. **OS concepts it teaches** — the exact modules (M1–M20) it makes concrete.
3. **Key data structures** — the 2–3 structs at the heart of it.
4. **Step-by-step build plan** — incremental stages, each runnable.
5. **Milestones** — "you are done with stage N when …" checkpoints.
6. **What interviewers probe** — the questions this project prepares you to nail.

> **The golden rule of these projects:** *always keep it running.* Build the
> smallest thing that compiles and prints something, then add one feature at a time.
> A shell that only runs `ls` today beats a "complete" shell that never compiled.

### Your environment (do this once)

You need **Linux** (real, a VM, or **WSL2** on Windows) because these projects use
POSIX system calls (`fork`, `exec`, `mmap`, `/proc`, `ucontext`, kernel modules)
that do not exist on native Windows.

```text
sudo apt update && sudo apt install build-essential gdb make    # gcc, make, gdb
gcc --version                                                    # confirm toolchain
uname -r                                                         # your kernel version
```

- **`gcc -Wall -Wextra -g`** always — warnings on, debug symbols on.
- **`gdb`** and **`valgrind`** (`sudo apt install valgrind`) are your microscopes —
  `valgrind` catches the memory bugs the allocator project will teach you to make.
- **`strace ./yourprog`** shows *every system call* your program makes — the single
  best learning tool in this module. Run it on your shell to watch `fork`/`execve`.

> **Memory hook:** **theory tells you what the OS does; `strace` shows you it doing
> it.** Keep a terminal open with `strace` while you build — it turns abstract
> syscalls into a live log.

---

## 23.2 Difficulty / Impact Table & Suggested Build Order

![Suggested build order: start with the CPU scheduler (pure logic), climb through shell and allocator to the thread library and kernel module; difficulty and depth of OS insight rise together.](images/216_build_order.png)

| # | Project | Core module(s) | Difficulty | Interview impact | Weekend est. |
|---|---------|----------------|:----------:|:----------------:|:------------:|
| 1 | **Mini CPU Scheduler** (FCFS/SJF/RR) | M6 | ★☆☆☆☆ | ★★★☆☆ | 1 |
| 2 | **Mini Shell** (fork/exec/pipe/redir) | M4, M3 | ★★★☆☆ | ★★★★★ | 1–2 |
| 3 | **Mini Memory Allocator** (malloc/free) | M9 | ★★★☆☆ | ★★★★★ | 1–2 |
| 4 | **Mini File System** (inodes/blocks) | M11, M12 | ★★★★☆ | ★★★★☆ | 2–3 |
| 5 | **Mini Process Manager** (ps via /proc) | M4, M14 | ★★☆☆☆ | ★★★☆☆ | 1 |
| 6 | **OS Monitoring Tool** (top-like) | M4, M6, M9, M14 | ★★☆☆☆ | ★★★☆☆ | 1 |
| 7 | **User-level Thread Library** (ucontext) | M5, M6 | ★★★★☆ | ★★★★★ | 2 |
| 8 | **Linux Kernel Module** (hello + /proc) | M3, M14 | ★★★★★ | ★★★★☆ | 1–2 |

**Suggested order (why this sequence):**

1. **Scheduler first** — pure algorithm, no tricky syscalls; it *proves the M6
   theory* and gives an early win.
2. **Shell** next — your first real dance with `fork`/`exec`/`wait`/`pipe`; the most
   discussed project in interviews.
3. **Allocator** — now you understand memory from userspace; teaches `sbrk`/`mmap`
   and fragmentation.
4. **Process manager → monitoring tool** — read the kernel's own bookkeeping via
   `/proc`; light and rewarding after the allocator.
5. **Thread library** — the hardest *userspace* project: you implement context
   switching yourself, which finally *demystifies* M5/M6.
6. **File system** — a big data-structure project (inodes, bitmaps, blocks).
7. **Kernel module last** — you now write code that runs in **kernel mode**; needs
   everything above to appreciate.

> **Memory hook:** **logic → processes → memory → observation → threads → storage →
> kernel.** You climb from "pure C" to "code inside the kernel," one privilege level
> at a time.

---

## 23.3 Project 1 — Mini CPU Scheduler (FCFS / SJF / Round Robin)

### What you build
A command-line simulator: read a list of processes (arrival time, burst time),
run a chosen algorithm, print the **Gantt chart** and the **average waiting time
(WT)** and **turnaround time (TAT)**. No real processes — pure simulation of M6.

### OS concepts it teaches (→ M6)
- **Scheduling algorithms:** FCFS, SJF (non-preemptive), SRTF (preemptive SJF),
  **Round Robin** with a time quantum.
- **The four metrics:** turnaround, waiting, response time, throughput.
- **Preemption vs non-preemption** and the **ready queue** as a live data structure.
- Why **RR trades average WT for responsiveness**, and **SJF is provably optimal**
  for average WT.

### Key data structures
```c
typedef struct {
    int pid, arrival, burst;      /* input */
    int remaining;                /* for RR / SRTF */
    int completion, tat, wt;      /* computed output */
    int started;                  /* first-run flag for response time */
} Proc;

Proc procs[MAX];                  /* the process table            */
int  ready_q[MAX], head, tail;    /* circular ready queue for RR  */
```

### Step-by-step build plan
1. **Parse input** — read `n` and each `(arrival, burst)` into `procs[]`.
2. **FCFS** — sort by arrival; sweep a `time` cursor, set `completion`, derive
   `tat = completion − arrival`, `wt = tat − burst`.
3. **SJF (non-preemptive)** — at each decision point pick the shortest-burst process
   *among those that have arrived*.
4. **Round Robin** — maintain a circular queue; run each head for
   `min(quantum, remaining)`; re-enqueue arrivals *then* the preempted job.
5. **Print a Gantt chart** and averages; add a `--algo` flag to select.

### Worked check (use this to validate your code — recompute by hand)
> Input: `P1(AT0,BT5) P2(AT1,BT3) P3(AT2,BT8) P4(AT3,BT6)`.

**FCFS** (run in arrival order):
```text
| P1  | P2  |   P3   |  P4  |
0     5     8        16     22
CT : P1=5  P2=8  P3=16 P4=22
TAT: 5, 7, 14, 19  -> avg = 45/4 = 11.25
WT : 0, 4,  6, 13  -> avg = 23/4 =  5.75
```

**SJF non-preemptive** (at t=5 pick shortest arrived = P2; then P4 over P3):
```text
| P1  | P2  |  P4  |   P3   |
0     5     8      14       22
CT : P1=5 P2=8 P4=14 P3=22
TAT: 5, 7, 20, 11  -> avg = 43/4 = 10.75
WT : 0, 4, 12,  5  -> avg = 21/4 =  5.25   (lowest avg WT — SJF is optimal)
```

**Round Robin, quantum = 3** (add arrivals before the preempted job):
```text
|P1|P2|P3|P4|P1|P3|P4|P3|
0  3  6  9 12 14 17 20 22
CT : P1=14 P2=6 P3=22 P4=20
TAT: 14, 5, 20, 17 -> avg = 56/4 = 14.0
WT :  9, 2, 12, 11 -> avg = 34/4 =  8.5   (worse avg, but everyone runs early)
```

> **The lesson your own numbers prove:** SJF wins on **average WT** (5.25), FCFS is
> simple (5.75), RR is **worst on average** (8.5) yet **best on responsiveness** —
> exactly the M6 tradeoff, now demonstrated by code you wrote.

### Milestones
- **M1:** FCFS prints a correct Gantt chart and averages matching the hand check.
- **M2:** SJF selects by shortest arrived burst; averages match.
- **M3:** RR with a `--quantum` flag; re-enqueue order correct.
- **M4 (stretch):** add **SRTF** and **priority** scheduling; plot avg WT vs quantum.

### What interviewers probe
- "Which algorithm minimises average waiting time?" → **SJF/SRTF** (optimal).
- "What is the danger of SJF?" → **starvation** of long jobs; needs burst prediction.
- "How does the quantum affect RR?" → too large → **FCFS**; too small → **overhead**
  from constant context switches.
- "Difference between waiting and response time?" → WT = total time in ready queue;
  response = time to **first** run.

---

## 23.4 Project 2 — Mini Shell (fork / exec / wait, pipes, redirection)

### What you build
A working Unix shell: a prompt loop that reads a command line, and **runs external
programs** with argument passing, **I/O redirection** (`>`, `<`), **pipes**
(`ls | grep c | wc -l`), background jobs (`&`), and a few **built-ins** (`cd`,
`exit`). This is *the* classic OS project.

### OS concepts it teaches (→ M4, M3)
- **`fork()`** — creating a child process (M4); the parent/child return-value trick.
- **`execvp()`** — replacing the process image with a new program.
- **`wait()/waitpid()`** — reaping children, reading exit status, avoiding **zombies**.
- **`pipe()` + `dup2()`** — inter-process communication and **file-descriptor
  redirection** (M4 IPC, M11 file descriptors).
- **Process groups & signals** — `Ctrl-C` handling (M4, M7 preview).

![How `ls | wc -l` runs in your shell: the shell creates a pipe, forks two children, and each uses dup2() to wire its stdout/stdin to the pipe before exec.](images/217_mini_shell_pipeline.png)

### The core pattern (the 12 lines every shell is built on)
```c
pid_t pid = fork();               /* 1. duplicate the process           */
if (pid == 0) {                   /* --- CHILD ---                      */
    /* optional: redirect fds here with dup2() before exec */
    execvp(argv[0], argv);        /* 2. become the new program          */
    perror("execvp"); _exit(127); /*    only runs if exec FAILED        */
} else {                          /* --- PARENT (the shell) ---         */
    int status;
    waitpid(pid, &status, 0);     /* 3. wait for the child, reap zombie */
}
```

> **Memory hook:** **`fork` = clone, `exec` = become, `wait` = reap.** The child is a
> copy that *turns into* the new program; the parent *waits* for it and collects its
> corpse (exit status) so it does not become a **zombie**.

### Pipes and redirection (the `dup2` insight)
A pipe is a pair of fds: `fd[0]` (read end), `fd[1]` (write end). To run `A | B`:
```c
int fd[2]; pipe(fd);
if (fork()==0){ dup2(fd[1],STDOUT_FILENO); close(fd[0]);close(fd[1]); exec A; }
if (fork()==0){ dup2(fd[0],STDIN_FILENO ); close(fd[0]);close(fd[1]); exec B; }
close(fd[0]); close(fd[1]);        /* PARENT must close BOTH ends       */
```
`dup2(oldfd, newfd)` makes `newfd` refer to the same file as `oldfd` — so writing to
`stdout` actually writes to the pipe. **Redirection `> file`** is the same trick with
an `open()`ed file instead of a pipe end.

> **The #1 pipe bug (interviewers love this):** if the parent (or a child) **forgets
> to close unused pipe ends**, the reader never sees **EOF** and hangs forever,
> because a pipe returns EOF only when *all* write ends are closed. Close every fd
> you do not need.

### Key data structures
```c
typedef struct { char *argv[MAXARGS]; char *infile, *outfile; int bg; } Cmd;
Cmd stages[MAXSTAGES];   /* one per pipeline segment */
```

### Step-by-step build plan
1. **REPL** — print a prompt, `fgets` a line, tokenise on spaces.
2. **Single command** — `fork` + `execvp` + `waitpid`; run `ls`, `pwd`, `echo`.
3. **Built-ins** — handle `cd` (must be built-in: it changes the *shell's* cwd via
   `chdir`, so it cannot run in a child) and `exit`.
4. **Redirection** — parse `>`/`<`, `open()` the file, `dup2` onto std fds in child.
5. **Pipes** — split on `|`, create pipes, wire stages with `dup2`, close all ends.
6. **Background `&`** — do not `waitpid`; reap later with `waitpid(-1, …, WNOHANG)`.
7. **Signals (stretch)** — trap `SIGINT` so `Ctrl-C` kills the child, not the shell.

### Milestones
- **M1:** runs external commands and built-in `cd`/`exit`.
- **M2:** `>` and `<` redirection work.
- **M3:** a two-stage pipe (`ls | wc -l`) works; then an N-stage pipeline.
- **M4:** background jobs with `&` and zombie reaping; `Ctrl-C` handled.

### What interviewers probe
- "Why must `cd` be a built-in?" → it must change the **shell's own** working
  directory; a child's `chdir` dies with the child.
- "What is a zombie? An orphan?" → zombie = dead child **not yet `wait`ed**; orphan =
  child whose parent died (re-parented to **init/PID 1**).
- "Why close both pipe ends?" → otherwise the reader never gets **EOF** (deadlock).
- "What does `exec` do to the PID / open files?" → **PID unchanged**; open fds
  survive across `exec` unless marked **close-on-exec**.

---

## 23.5 Project 3 — Mini Memory Allocator (malloc / free, free-list, fragmentation)

### What you build
Your own `my_malloc()` and `my_free()` — a heap allocator that requests memory from
the OS (`sbrk` or `mmap`), carves it into blocks, tracks free blocks in a
**free list**, and **coalesces** neighbours on free. You will *see* fragmentation.

### OS concepts it teaches (→ M9)
- **The heap** and how userspace grows it (`sbrk`/`brk`, `mmap`).
- **Dynamic allocation policies:** **first-fit, best-fit, worst-fit** (M9).
- **Internal vs external fragmentation** — you will produce both.
- **Coalescing** and **splitting** blocks; block **metadata (headers)**.
- Why real allocators use **size classes / bins** (glibc, jemalloc, tcmalloc).

![A free-list allocator: each block has a header (size, free flag); free() flips the flag and coalesces with free neighbours. Scattered small free blocks are external fragmentation.](images/218_free_list_allocator.png)

### Key data structures (the block header trick)
```c
typedef struct block {
    size_t size;              /* payload size */
    int    free;              /* 1 = free, 0 = in use */
    struct block *next;       /* next block in the list */
} Block;                      /* header sits JUST BEFORE the returned pointer */

#define HDR sizeof(Block)
Block *free_list = NULL;      /* head of the free list */
```
The pointer you return to the user is `(void*)(header + 1)`; on `free(p)` you recover
the header with `((Block*)p) - 1`. This "hidden header before the pointer" is exactly
how real `malloc` finds a block's size when you only hand it a raw pointer.

### Step-by-step build plan
1. **Grow the heap** — `void *p = sbrk(size + HDR);` (or `mmap`) to get raw bytes.
2. **First-fit malloc** — walk `free_list` for a free block ≥ requested size; if none,
   grow the heap and append.
3. **Split** — if the found block is much bigger, split it so the remainder stays
   free (reduces internal fragmentation).
4. **free()** — flip `free = 1`; do **not** return to OS yet.
5. **Coalesce** — on free, merge with the adjacent free block(s) to fight external
   fragmentation.
6. **Best-fit / worst-fit** — add a policy flag and *measure* fragmentation for each.

> **Memory hook:** **internal** fragmentation = wasted space **inside** a block you
> rounded up; **external** fragmentation = enough free memory total, but **scattered**
> in pieces too small for the request. Best-fit minimises leftover but *creates lots
> of tiny slivers* (bad external frag); first-fit is faster and often better in
> practice.

### Milestones
- **M1:** `my_malloc`/`my_free` work for a few allocations; no crash.
- **M2:** blocks split and coalesce; a fragmentation counter drops after coalescing.
- **M3:** `valgrind` and a stress test (random malloc/free) run clean.
- **M4 (stretch):** add **size-class bins** and compare speed/fragmentation to glibc.

### What interviewers probe
- "First-fit vs best-fit?" → best-fit least immediate waste but **worst external
  fragmentation** (tiny slivers); first-fit faster.
- "Internal vs external fragmentation?" → inside a block vs scattered between blocks;
  **paging cures external, causes a little internal** (last page).
- "How does `free` know the size?" → the **header stored just before the pointer**.
- "Why not return every freed block to the OS?" → `sbrk`/`mmap` syscalls are
  expensive; allocators **cache** freed memory for reuse.

---

## 23.6 Project 4 — Mini File System (inodes, blocks, directories)

### What you build
A file system **inside a single file** (a "disk image"): you format a fixed-size file
into a superblock, an **inode table**, a **block bitmap**, and data blocks, then
implement `create`, `write`, `read`, `ls`, and `delete` on it. This makes M11/M12
completely concrete.

### OS concepts it teaches (→ M11, M12)
- **Inodes** — metadata (size, permissions, block pointers) separate from the name.
- **Direct + indirect block pointers** and the **max-file-size** calculation (M11).
- **Free-space management** with a **bitmap** (M11).
- **Directories** as tables mapping **name → inode number** (M11).
- **Blocks** as the unit of allocation; **internal fragmentation** of the last block.

### Key data structures
```c
typedef struct {                 /* on-disk superblock */
    int total_blocks, inode_count, block_size, data_start;
} Superblock;

typedef struct {                 /* one inode */
    int    used, size;
    int    direct[12];           /* direct block numbers */
    int    single_indirect;      /* block full of block numbers */
} Inode;

typedef struct { char name[28]; int inode_no; } DirEntry;   /* name -> inode */
unsigned char block_bitmap[NBLOCKS/8];                       /* 1 bit per block */
```

### Step-by-step build plan
1. **mkfs (format)** — create the image file, write the superblock, zero the bitmap
   and inode table.
2. **Allocate blocks** — scan the bitmap for a free bit, set it, return the block no.
3. **create(name)** — grab a free inode, add a `DirEntry` to the root directory.
4. **write(name, data)** — allocate data blocks, fill `direct[]`, spill into
   `single_indirect` when you exceed 12 blocks.
5. **read / ls / delete** — walk pointers to read; free bits + inode on delete.

### Worked check — max file size (recompute by hand, then in code)
> Block = **4 KB**, pointer = **4 B** → **1024 pointers per block**; 12 direct + 1
> single + 1 double + 1 triple indirect:
```text
capacity (in blocks) = 12 + 1024 + 1024^2 + 1024^3
                     = 12 + 1024 + 1,048,576 + 1,073,741,824 = 1,074,791,436 blocks
max file size        = 1,074,791,436 x 4096 B = 4,402,345,721,856 B  ~= 4.00 TB
```
> Your `single_indirect`-only version caps at `(12 + 1024) x 4 KB = 4,144 KB ≈ 4.05
> MB` — a great milestone to verify before adding double/triple indirection.

### Milestones
- **M1:** `mkfs` writes a valid superblock; you can re-open the image.
- **M2:** create + write + read a small file using only `direct[]`.
- **M3:** files bigger than 12 blocks work via `single_indirect`.
- **M4 (stretch):** subdirectories, and a `fsck` that verifies the bitmap.

### What interviewers probe
- "What is an inode; what does it *not* store?" → all metadata + block pointers, but
  **not the file name** (that lives in the directory).
- "How do hard links work?" → multiple directory entries → **same inode**
  (link count); file dies when count hits 0 (M11).
- "Compute the max file size" → the direct+indirect sum above — a GATE staple.
- "Why blocks, not bytes?" → amortise disk seeks; the cost is last-block **internal
  fragmentation**.

---

## 23.7 Project 5 — Mini Process Manager (a `ps`-like tool via /proc)

### What you build
A program that lists running processes with PID, state, name, memory, and CPU — by
**reading the `/proc` filesystem**, exactly as real `ps`/`top` do. No special
syscalls; `/proc` *is* the kernel's interface for this.

### OS concepts it teaches (→ M4, M14)
- **`/proc` as a virtual filesystem** — the kernel exposes process state as files
  (M14).
- **The PCB made visible** — `/proc/<pid>/stat` and `/status` are the kernel's
  **process control block** fields you learned in M4.
- **Process states** — you read `R/S/D/Z/T` (running, sleeping, uninterruptible,
  zombie, stopped) straight from the kernel (M4).
- **The process tree** — `PPID` links children to parents (M4).

### Key data structures
```c
typedef struct {
    int  pid, ppid;
    char state;              /* R,S,D,Z,T */
    char comm[64];           /* command name */
    long rss_pages;          /* resident memory in pages */
    unsigned long utime, stime;  /* CPU jiffies in user/kernel mode */
} PInfo;
```

### Step-by-step build plan
1. **Enumerate** — `opendir("/proc")`; every entry whose name is all-digits is a PID.
2. **Parse `/proc/<pid>/stat`** — one line of space-separated fields: pid, comm,
   state, ppid, …, utime, stime, …, rss.
3. **Human-readable** — map state letters to words; convert RSS pages → MB (page size
   from `sysconf(_SC_PAGESIZE)`).
4. **Sort & print** a table (by memory or CPU).
5. **Tree view (stretch)** — build the PPID→children map and indent a tree.

> **Memory hook:** **everything is a file** — even a running process. `cat
> /proc/self/status` shows *this* program's own PCB. Your tool is just a formatter
> over files the kernel already writes.

### Milestones
- **M1:** list every PID and its command name.
- **M2:** add state, PPID, and memory (RSS in MB).
- **M3:** sort by memory; add a `--tree` view.

### What interviewers probe
- "What is `/proc`?" → a **virtual (pseudo) filesystem** — files backed by kernel
  data, **not disk** (M14).
- "Where does `ps` get its data?" → from **`/proc/<pid>/stat` and `/status`**.
- "What are the process states?" → R/S/D/Z/T (see M4); what's a **D (uninterruptible
  sleep)** and why can't you kill it easily.

---

## 23.8 Project 6 — OS Monitoring Tool (a `top`-like dashboard)

### What you build
An interactive, refreshing terminal dashboard: overall **CPU %**, **memory usage**,
**load average**, and the **top-N processes** — updating every second, like `top`.
Builds directly on Project 5.

### OS concepts it teaches (→ M4, M6, M9, M14)
- **CPU utilisation** computed as a **delta** of `/proc/stat` jiffies between samples
  (M6).
- **Memory accounting** — total/free/cached from `/proc/meminfo` (M9).
- **Load average** — the run-queue length over 1/5/15 min from `/proc/loadavg` (M6).
- **Sampling** — why you must diff two snapshots to get a *rate* (a real profiling
  idea).

### The CPU-% insight (the one subtlety)
`/proc/stat` gives **cumulative** jiffies since boot. Instantaneous CPU% needs **two
reads**:
```text
CPU% = 100 * (1 - (idle2 - idle1) / (total2 - total1))
       where total = user+nice+system+idle+iowait+irq+softirq
```
> **Memory hook:** the kernel gives you a **odometer** (cumulative), not a
> **speedometer** (rate). To get speed, subtract two odometer readings over a known
> interval. That is *the* pattern behind every monitoring tool.

### Key data structures
```c
typedef struct { unsigned long user,nice,sys,idle,iowait,irq,softirq; } CpuTimes;
CpuTimes prev, cur;      /* two samples, one second apart */
```

### Step-by-step build plan
1. **CPU%** — read `/proc/stat`, sleep 1s, read again, apply the delta formula.
2. **Memory bar** — parse `/proc/meminfo` (`MemTotal`, `MemAvailable`).
3. **Process rows** — reuse Project 5; compute per-process CPU% from utime/stime
   deltas.
4. **Refresh loop** — clear screen (ANSI escape), redraw each second; add sort keys.

### Milestones
- **M1:** live overall CPU% and memory bar refreshing each second.
- **M2:** top-N processes by CPU, updating.
- **M3:** keyboard sort toggles (CPU/mem) and a quit key.

### What interviewers probe
- "Why does CPU% need two samples?" → `/proc/stat` is **cumulative**; you diff for a
  rate.
- "What is load average of 4 on a 4-core box?" → **fully utilised**, no queueing;
  `>4` means processes are **waiting** (M6 run queue).
- "iowait vs idle?" → CPU idle **because it is waiting on I/O** vs simply idle.

---

## 23.9 Project 7 — User-Level Thread Library (context switch via `ucontext`)

### What you build
A cooperative (green) threading library: `thread_create`, `thread_yield`, and a
simple **round-robin scheduler**, all in **userspace**, by saving and restoring CPU
context with `ucontext`. You implement a **context switch by hand** — the single
best way to *finally understand* M5 and M6.

### OS concepts it teaches (→ M5, M6)
- **What a context switch actually is** — save registers + stack pointer of one
  thread, restore another's (M5, M6). You *write* it.
- **Thread Control Block (TCB)** — the userspace cousin of the PCB (M5).
- **User-level vs kernel-level threads** — you build **N:1** (many user threads on
  one kernel thread) and feel its limitation (M5).
- **Cooperative vs preemptive** scheduling (M6); the run queue.

### Key data structures
```c
#include <ucontext.h>
typedef struct tcb {
    ucontext_t ctx;         /* saved registers + stack pointer */
    char      *stack;       /* this thread's own stack         */
    int        id, done;
    struct tcb *next;       /* ready-queue link                */
} TCB;
TCB *current, *ready_head;  /* the scheduler's state           */
```

### The heart of it (the two calls that *are* a context switch)
```c
getcontext(&t->ctx);              /* snapshot current context      */
t->ctx.uc_stack.ss_sp   = t->stack;
t->ctx.uc_stack.ss_size = STACKSZ;
t->ctx.uc_link          = &main_ctx;   /* where to go when done    */
makecontext(&t->ctx, fn, 0);      /* set entry function            */
/* ... later, to switch from A to B: */
swapcontext(&A->ctx, &B->ctx);    /* SAVE A, RESTORE B  == a context switch */
```
> **Memory hook:** **`swapcontext` IS a context switch.** It saves every register and
> the stack pointer of the running thread and loads another's — precisely what the
> kernel does on a timer interrupt, except here *you* trigger it in `thread_yield`.

### Step-by-step build plan
1. **One thread** — `makecontext` a function, `swapcontext` into it, return.
2. **Two threads that yield** — a ready queue; `thread_yield` = pick next +
   `swapcontext`.
3. **N threads, round-robin** — schedule until all `done`; clean up stacks.
4. **Preemptive (stretch)** — a `SIGALRM` timer that calls `thread_yield` — now you
   have built a **preemptive** scheduler and can explain the timer interrupt for real.

### Milestones
- **M1:** control transfers into a created thread and back.
- **M2:** two threads alternate via cooperative `yield`.
- **M3:** N threads run to completion under a round-robin scheduler.
- **M4:** timer-based preemption works (the "aha" moment for M6).

### What interviewers probe
- "What is saved during a context switch?" → **registers, program counter, stack
  pointer** (and, for processes, memory maps) — you literally saved them.
- "User-level vs kernel-level threads?" → your **N:1** library: fast switches, **but
  one blocking syscall blocks all** threads, and no multicore parallelism (M5).
- "Cooperative vs preemptive?" → yield-based vs **timer-interrupt** based; you built
  both.
- "Why is a thread switch cheaper than a process switch?" → **same address space**,
  no TLB/page-table swap (M5, M10).

---

## 23.10 Project 8 — A Simple Linux Kernel Module (hello + a /proc entry)

### What you build
A **loadable kernel module (LKM)**: code that runs in **kernel mode**. Start with a
"hello world" that logs on load/unload, then add a **`/proc/myinfo` entry** that
returns text when read. You cross from userspace into the kernel — the ultimate OS
project.

### OS concepts it teaches (→ M3, M14)
- **Kernel mode vs user mode** — your code now runs with **full privilege** (M3).
- **Monolithic kernel + loadable modules** — how Linux extends itself at runtime
  (M3, M14).
- **The `/proc` interface from the other side** — you *provide* a `/proc` file
  (Project 5 read one; now you write one) (M14).
- **No libc, no `main`** — kernel code uses `printk`, module init/exit, and must
  never crash (a bug = **kernel panic**).

### The skeleton
```c
#include <linux/module.h>
#include <linux/init.h>
static int __init my_init(void){ printk(KERN_INFO "hello from kernel\n"); return 0; }
static void __exit my_exit(void){ printk(KERN_INFO "bye from kernel\n"); }
module_init(my_init);
module_exit(my_exit);
MODULE_LICENSE("GPL");
```
Build with a `Makefile` using the **kernel build system** (`obj-m += mymod.o`),
`make`, then `sudo insmod mymod.ko`, `dmesg | tail`, `sudo rmmod mymod`.

> **Memory hook:** a kernel module is **surgery on a running OS.** There is no safety
> net: a null-pointer deref in userspace is a segfault; **in the kernel it can panic
> the machine.** Test in a VM you do not mind rebooting.

### Key APIs
```text
printk(KERN_INFO ...)          kernel's printf (writes to the ring buffer / dmesg)
module_init / module_exit      register load/unload hooks
proc_create("myinfo",...)      create a /proc entry backed by your read handler
```

### Step-by-step build plan
1. **Toolchain** — install `linux-headers-$(uname -r)`; write the `Makefile`.
2. **Hello module** — `insmod`, check `dmesg`, `rmmod`. Confirm both messages appear.
3. **`/proc/myinfo`** — `proc_create` with a `read` handler that copies a string to
   userspace (`copy_to_user` / `seq_file`).
4. **Parameterise (stretch)** — a module parameter (`module_param`) you set at load.

### Milestones
- **M1:** module loads/unloads; messages in `dmesg`.
- **M2:** `cat /proc/myinfo` prints your text.
- **M3:** module accepts a load-time parameter and reports it.

### What interviewers probe
- "User mode vs kernel mode?" → privilege level; syscalls are the **gate** between
  them (M3).
- "Why is Linux 'monolithic with modules'?" → one big kernel address space, but
  drivers/features load at runtime as **modules** (M3, M14).
- "What happens if kernel code dereferences NULL?" → **oops / panic** — no process
  isolation to catch it.
- "Difference between `printk` and `printf`?" → `printk` runs in-kernel, has **log
  levels**, writes to the kernel ring buffer (`dmesg`), and cannot use libc.

---

## 23.11 Real-World & Backend Perspectives

- **The shell project** is the closest thing to how **every process launcher works** —
  container runtimes (Docker, `runc`), CI systems, and `systemd` all `fork`/`exec`/
  `wait` and wire up fds exactly as you did.
- **The allocator project** is why senior backend engineers understand
  **`jemalloc`/`tcmalloc`**, memory fragmentation in long-running services, and why a
  Go/Java heap profile looks the way it does.
- **The thread library** is the mental model behind **goroutines, async/await, and
  fibers** — cooperative userspace scheduling over a few kernel threads (the **M:N**
  model). AI-infra (M19) serving stacks live and die by this.
- **The monitoring tool** is a baby `top`/`htop`/`node_exporter`; the `/proc` deltas
  you compute are exactly what **Prometheus node exporters** scrape in production.
- **The kernel module** is the entry point to **device drivers and eBPF** — the
  skills behind observability tools like `bpftrace` and high-performance networking.

---

## 23.12 Tradeoffs, Common Mistakes, Edge Cases

- **Shell:** forgetting to **close pipe fds** (hangs), running `cd` in a child (no
  effect), not reaping background children (**zombie** buildup).
- **Allocator:** returning a pointer **without room for the header**; forgetting to
  **coalesce** (external fragmentation explodes); alignment bugs (return
  8/16-byte-aligned pointers).
- **Thread library:** too-small thread **stacks** (silent corruption); forgetting
  `uc_link` (falling off the end of a thread); assuming it gives **multicore**
  parallelism (it does not — it is N:1).
- **File system:** off-by-one in the **bitmap**; forgetting the **last block is
  partially wasted** (internal fragmentation); not persisting the superblock.
- **Kernel module:** testing on your **main machine** (test in a VM!); using libc or
  floating point in the kernel; memory leaks that persist until reboot.
- **Monitoring:** reporting **cumulative** jiffies as if instantaneous (must diff two
  samples).

---

## 23.13 Exam, Interview & Coding Perspectives

- **Interviews (the big payoff):** put 2–3 of these on your résumé with a one-line
  "what it taught me." Expect deep-dives on **`fork`/`exec`/`wait`**, **context
  switching**, **fragmentation**, and **`/proc`** — all of which you can now answer
  from having *built* them.
- **GATE/written:** these projects reinforce the **numericals** (scheduling averages,
  max file size) you must compute in the exam; the code is a checker for your hand
  calculations.
- **Coding rounds:** the shell and allocator are common **systems coding-round**
  prompts ("implement a mini-shell / a memory pool"); you will have done it already.

---

## 23.14 Concept Checks & MCQs

1. Which project best explains a **context switch**? → the **thread library**
   (`swapcontext`).
2. Why must `cd` be a shell **built-in**? → it must change the **shell's own** cwd.
3. First-fit vs best-fit — which risks the **most external fragmentation**? →
   **best-fit** (tiny slivers).
4. Where does a `ps`-tool get its data? → the **`/proc`** filesystem.
5. To get instantaneous CPU% from `/proc/stat` you must? → **diff two samples**.
6. What does `dup2(fd, STDOUT_FILENO)` achieve in a pipe? → redirects **stdout** to
   the pipe's write end.
7. A child that has exited but not been `wait`ed is a? → **zombie**.
8. In an inode with 12 direct + single/double/triple indirect (4 KB block, 4 B
   pointer), max size ≈? → **~4 TB**.
9. `swapcontext(&A,&B)` does what? → **saves A's context, restores B's** (a context
   switch).
10. Why can a kernel-module NULL deref be catastrophic? → it runs in **kernel mode** —
    no process isolation → **panic**.
11. Which scheduling algorithm gives the **lowest average WT**? → **SJF/SRTF**.
12. Why close **both** pipe ends in the parent? → so the reader receives **EOF**.

---

## 23.15 One-Page Revision Sheet

```
PROJECT -> WHAT IT TEACHES (module) -> KEY SYSCALLS/STRUCTS
  1 CPU SCHEDULER (M6)  FCFS/SJF/RR; TAT=CT-AT, WT=TAT-BT; SJF min avg WT; RR=quantum
  2 SHELL (M4)          fork=clone, exec=become, wait=reap; pipe()+dup2(); close all fds!
                        cd=builtin; zombie=unreaped; orphan->init(PID1)
  3 ALLOCATOR (M9)      sbrk/mmap; free-list; header BEFORE pointer; split+coalesce
                        first/best/worst fit; internal(inside) vs external(scattered) frag
  4 PS TOOL (M4,M14)    /proc/<pid>/stat & status = PCB made visible; states R/S/D/Z/T
  5 TOP TOOL (M6,M9)    /proc/stat cumulative -> DIFF two samples for CPU%; loadavg
  6 THREAD LIB (M5,M6)  ucontext: makecontext + swapcontext = CONTEXT SWITCH by hand
                        TCB; N:1 (one blocking call blocks all; no multicore)
  7 FILE SYSTEM (M11)   superblock+inode table+block bitmap+data; direct+indirect ptrs
                        maxsize=(12 + N + N^2 + N^3)*B ; name lives in DIRECTORY not inode
  8 KERNEL MODULE (M3)  insmod/rmmod; printk->dmesg; module_init/exit; proc_create; TEST IN VM

BUILD ORDER: scheduler -> shell -> allocator -> ps -> top -> threads -> filesystem -> kmod
GOLDEN RULE: always keep it compiling; add ONE feature at a time. strace to watch syscalls.
```

### Flash cards

| Front | Back |
|-------|------|
| `fork` / `exec` / `wait` in one word each? | clone / become / reap |
| Pipe reader hangs — likely cause? | an unclosed write end (no EOF) |
| `swapcontext(&A,&B)` does? | saves A, restores B = a context switch |
| Best-fit's downside? | worst external fragmentation (slivers) |
| Where `malloc` stores a block's size? | header just before the pointer |
| Source of `ps`/`top` data? | /proc/<pid>/stat & /proc/stat |
| Instantaneous CPU% needs? | diff of two /proc/stat samples |
| Max inode file size formula? | (direct + N + N² + N³) × block |
| Kernel module logging call? | printk (→ dmesg) |
| Why `cd` is built-in? | changes the shell's own cwd |

### Spaced repetition
- **24-hour:** re-derive the FCFS/SJF/RR averages by hand; recite fork/exec/wait.
- **7-day:** explain a context switch using your `swapcontext` code; internal vs
  external fragmentation from your allocator.
- **30-day:** whiteboard the `ls | wc -l` pipe wiring (pipe + fork×2 + dup2 + close);
  compute a max inode file size cold.

---

## 23.16 Summary

Theory becomes yours only when you **build it**. Eight weekend-sized projects turn
Modules 1–20 into working C: a **CPU scheduler** proves the M6 averages; a **shell**
makes `fork`/`exec`/`wait`, **pipes**, and **redirection** second nature; a **memory
allocator** shows fragmentation and free-lists from M9; a **`ps`/`top` pair** reads
the kernel's own bookkeeping through **`/proc`**; a **user-level thread library**
lets you *write a context switch* with `ucontext` (the deepest insight in the
course); a **mini file system** realises inodes, bitmaps, and the max-file-size
formula from M11; and a **kernel module** carries you across the line into **kernel
mode**. Build in the order scheduler → shell → allocator → observers → threads →
file system → kernel module, always keeping the code compiling and adding one feature
at a time.

These are the projects that make an interviewer lean in — and the reason you will
answer "how does the OS actually do it?" with *"let me show you the one I wrote."*

Next, **Module 24 — The Revision Kit** compresses the entire course into formula
sheets, cheat sheets, flash cards, and an exam-day strategy for your final sprint.

> **You have mastered this module when** you can: pick the right project for a concept
> you want to prove; wire `ls | wc -l` with pipe/fork/dup2/close on a whiteboard;
> explain a context switch from your own `swapcontext` code; reason about
> first/best-fit fragmentation from your allocator; and describe how `ps`, `top`, and
> a kernel module talk to `/proc` — all from projects you have actually built.
