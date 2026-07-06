---
title: "Module 14 — Linux Internals"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14 — Linux Internals

> **Where this module sits.**
> Modules 1–13 built the *general theory* of operating systems — processes (M4),
> threads (M5), scheduling (M6), synchronization (M7), memory & virtual memory
> (M9–M10), file systems (M11–M12), and I/O (M13). This module makes it **concrete
> in the one kernel you will actually deploy on**: **Linux**. Every backend server,
> every cloud VM, every Android phone, and every Docker container runs a Linux
> kernel. We open the hood and see how Linux *implements* those abstractions:
> `task_struct` and `clone()` for processes/threads, the **Completely Fair
> Scheduler (CFS)** for §M6 scheduling, the **page cache / zones / OOM killer** for
> §M9 memory, the **VFS** for §M11 files, and — most important for modern infra —
> **cgroups + namespaces**, the two kernel features that make **containers (M17)**
> possible. Learn this module and the rest of the course stops being abstract.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★      | ★★★★★     | ★★★★★   |

**Most-asked PYQ / interview concepts:** monolithic vs microkernel (**Linux is a
monolithic kernel with loadable modules**); `fork()` vs `clone()` and how Linux
represents a thread; **CFS** (vruntime, red-black tree, nice→weight); **page cache**
and **`kswapd` / OOM killer**; the **VFS** four objects (superblock, inode, dentry,
file); **ext4** (extents, journaling); **namespaces vs cgroups** (isolation vs
resource limits — the container foundation); **systemd** as PID 1; reading
**`/proc/<pid>`** and **`/sys`**.

---

## 14.1 Linux Architecture — The Big Picture (first principles)

Linux is a **monolithic kernel**: the scheduler, memory manager, file systems, and
device drivers all run together in **one address space in kernel mode** (fast direct
calls, no message passing). But it is a **modular** monolith — drivers and file
systems can be compiled as **loadable kernel modules (LKMs)** loaded at runtime
(`insmod` / `modprobe`), giving it microkernel-like flexibility without the IPC cost.

> **Memory hook:** Linux is a **monolithic kernel with a plug-in socket**. The
> engine block is one solid casting (monolithic = fast), but you can screw in extra
> parts while it runs (modules = flexible). This is the classic exam answer to
> "is Linux monolithic or microkernel?" → **monolithic (modular)**.

![Linux kernel architecture: user space reaches the kernel only through the system-call interface; the monolithic kernel groups process management, memory management, VFS, networking, and device drivers, sitting on the hardware via arch-specific code.](images/141_linux_architecture.png)

The kernel is organised into a handful of **subsystems**, each mapping to an earlier
module:

| Subsystem | Job | Course link |
|-----------|-----|-------------|
| **Process management / scheduler** | create, schedule, and kill tasks | M4, M5, M6 |
| **Memory management (MM)** | virtual memory, paging, page cache | M9, M10 |
| **Virtual File System (VFS)** | uniform interface over many filesystems | M11 |
| **Networking stack** | sockets, TCP/IP, netfilter | M13 / networking |
| **Device drivers** | talk to hardware; char / block / net devices | M13 |
| **Arch layer** | CPU-specific code (x86, ARM, RISC-V) | M2 |

**User space vs kernel space.** User programs never touch hardware directly. They
call the C library (glibc), which issues a **system call** (`syscall` instruction on
x86-64) to trap into kernel mode (§M3 dual-mode). Everything above the syscall line
is **user space**; everything below runs with full privilege in **kernel space**.

### MCQs

1. Is Linux a microkernel or monolithic kernel? → **monolithic**, but **modular**
   (loadable kernel modules).
2. How does user space enter the kernel? → via a **system call** (traps to kernel
   mode).
3. Command to load a kernel module? → **`insmod` / `modprobe`**.

---

## 14.2 The Process/Thread Model — `task_struct` and `clone()`

### One structure to rule them all: `task_struct`

Linux does **not** have separate "process" and "thread" objects. Every schedulable
entity — whether you call it a process or a thread — is **one `task_struct`** (the
kernel's **PCB**, §M4). A `task_struct` holds the task's PID, state, scheduling
info, pointers to its memory (`mm_struct`), open files, signal handlers, and
credentials.

> **Memory hook:** to the Linux scheduler, **there are no threads — only tasks.** A
> "thread" is just a task that **shares** more with its siblings (same address
> space) than a "process" does. This one idea explains all of Linux's process API.

### `fork()`, `clone()`, and threads

- **`fork()`** creates a new process: a **copy** of the parent with its **own**
  address space (via **copy-on-write**, §M10 — pages are shared read-only until one
  side writes). Parent and child share nothing writable.
- **`clone()`** is the powerful primitive underneath. It creates a new task and lets
  you choose *exactly what to share* via flags:

| `clone()` flag | Shares with parent |
|----------------|--------------------|
| `CLONE_VM` | the **address space** (`mm_struct`) — this makes it a *thread* |
| `CLONE_FILES` | the open **file descriptor** table |
| `CLONE_FS` | filesystem info (cwd, root, umask) |
| `CLONE_SIGHAND` | signal handlers |
| `CLONE_THREAD` | same **thread group** (shared PID / getpid()) |
| `CLONE_NEWPID`, `CLONE_NEWNET`, … | create new **namespaces** (§14.7) |

> **The key insight:** `fork()` and creating a **thread** are the *same syscall*
> with different flags.
> - **`fork()`** ≈ `clone()` with **almost nothing shared** (new address space).
> - **`pthread_create()`** ≈ `clone()` with `CLONE_VM | CLONE_FILES | CLONE_SIGHAND
>   | CLONE_THREAD` (share everything). Both end up as a `task_struct` on the same
>   run queue.

```c
/* fork: child gets a private (copy-on-write) copy of memory */
pid_t pid = fork();
if (pid == 0)      { /* child  */ }
else if (pid > 0)  { /* parent */ }

/* A thread = clone() sharing the address space (what pthread_create does under the hood) */
clone(fn, stack, CLONE_VM | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD, arg);
```

**Thread group id (TGID).** All threads of a process share a **TGID** (which is what
`getpid()` returns); each thread also has its own kernel-level **TID** (what
`gettid()` returns and what the scheduler uses). So user-space "PID" = kernel TGID.

### MCQs

1. What kernel structure represents both a process and a thread? → **`task_struct`**.
2. Which `clone()` flag makes the child share the address space (i.e. a thread)? →
   **`CLONE_VM`**.
3. `fork()` copies memory using what technique? → **copy-on-write (COW)**.
4. What does `getpid()` return for a multithreaded process? → the shared **TGID**.

---

## 14.3 The Completely Fair Scheduler (CFS)

CFS was Linux's default scheduler from kernel **2.6.23 (2007)** until **6.6 (2023)**,
when it was replaced by **EEVDF** (see the note at the end). CFS remains *the* most
important OS-scheduler to understand for interviews and exams because it perfected
one elegant idea.

### The idea: model an "ideal, perfectly-fair CPU"

On an ideal multitasking CPU with *n* runnable tasks, each would get exactly **1/n**
of the CPU *at every instant*. Real hardware runs one task at a time, so CFS tracks
how far each task has **fallen behind** this ideal and always runs the one that is
**most behind**. The bookkeeping variable for "how much CPU this task has received"
is **`vruntime` (virtual runtime)**.

> **Memory hook:** CFS is a **fairness debt collector**. `vruntime` = "how much CPU
> you've already eaten." CFS always serves the **hungriest** task — the one with the
> **smallest `vruntime`**.

### vruntime, nice values, and weights

Every task accumulates `vruntime` as it runs. For a **default-priority** task
(nice 0), `vruntime` advances at the **same rate** as real time. For other
priorities, CFS scales the rate by the task's **weight**:

```text
vruntime += delta_exec * (NICE_0_LOAD / task_weight)
   where  delta_exec  = real nanoseconds the task just ran
          NICE_0_LOAD = 1024   (the weight of a nice-0 task)
```

- A **high-priority** task (negative nice → **large weight**) accumulates `vruntime`
  **slowly**, so it stays "hungry" and is picked more often → more CPU.
- A **low-priority** task (positive nice → **small weight**) accumulates `vruntime`
  **fast**, so it looks "full" quickly → less CPU.

**Nice → weight mapping.** Nice ranges from **−20 (highest priority)** to **+19
(lowest)**. Weight ≈ `1024 / 1.25^nice`, so **each nice step changes CPU share by
~10%**. Selected values from the kernel's `sched_prio_to_weight[]` table:

| nice | weight | relative CPU (2 tasks) |
|:----:|:------:|:----------------------:|
| −20  | 88761  | vastly more |
| −5   | 3121   | more |
| **0**| **1024** | baseline |
| +5   | 335    | less |
| +19  | 15     | almost none |

> **Worked example (10% rule).** Two CPU-bound tasks, nice 0 and nice 0 → each gets
> **50%**. Now renice one to **nice 1** (weight 820). Its share =
> `820 / (1024 + 820) ≈ 44%`; the other gets `1024/1844 ≈ 56%`. One nice level ≈ a
> **~10–12% swing** — exactly the design goal.

### The red-black tree — O(log n) "pick next"

CFS keeps all runnable tasks in a **red-black tree keyed by `vruntime`** (a balanced
BST). The **leftmost node** is the task with the **smallest `vruntime`** — the one to
run next — and CFS caches a pointer to it, so **picking the next task is O(1)**;
insertion/removal after a task runs is **O(log n)**.

![CFS keeps runnable tasks in a red-black tree ordered by vruntime; the leftmost node (smallest vruntime = most starved) is chosen to run next. A high-weight (low-nice) task accrues vruntime slowly and stays near the left, getting more CPU.](images/142_cfs_rbtree.png)

**The scheduling loop:**

```text
1. pick the LEFTMOST task in the RB-tree (smallest vruntime = most behind).
2. run it for a slice (targeted so all tasks cycle within one "scheduling latency").
3. add the real time it ran to its vruntime (scaled by weight).
4. re-insert it into the tree at its new position; go to 1.
```

- **No fixed time-quantum:** CFS computes each task's slice from a target
  **scheduling latency** (e.g. ~6 ms) divided among runnable tasks (with a minimum
  **`sched_min_granularity`** so slices don't get absurdly tiny).
- **New / woken tasks** are given a `vruntime` close to the tree minimum (not 0) so
  a freshly-woken task doesn't unfairly hog the CPU forever, yet still gets prompt
  service — great for **interactive** tasks that sleep a lot.

> **Why CFS feels responsive:** a task that **sleeps** (waiting on I/O, like a text
> editor) doesn't accrue `vruntime` while asleep, so on waking it has a **small
> `vruntime`** and jumps to the front — interactive apps get CPU quickly without any
> special "interactive priority" heuristic. Fairness *is* the responsiveness.

> **Note — CFS → EEVDF.** Since kernel **6.6 (Nov 2023)** the default is **EEVDF
> (Earliest Eligible Virtual Deadline First)**, which adds an explicit **latency**
> knob and virtual **deadlines** on top of the same `vruntime`/weight machinery.
> Conceptually it is CFS + deadlines; the `vruntime`/nice/weight ideas above still
> apply. For exams, **know CFS**; for currency, know that **EEVDF replaced it**.

### MCQs

1. What variable does CFS use to track fairness? → **`vruntime`** (virtual runtime).
2. Which task does CFS run next? → the one with the **smallest `vruntime`**
   (leftmost RB-tree node).
3. Data structure holding runnable tasks in CFS? → a **red-black tree** (keyed by
   `vruntime`).
4. Weight of a nice-0 task? → **1024** (`NICE_0_LOAD`); one nice step ≈ **10%** CPU.
5. What replaced CFS as the default scheduler in kernel 6.6? → **EEVDF**.

---

## 14.4 The Memory Manager — Zones, Page Cache, kswapd, OOM Killer

Linux implements the virtual-memory concepts of M9/M10. A few Linux-specific pieces
are exam- and interview-favourites.

### Zones — physical memory is not uniform

The kernel splits physical RAM into **zones** because some hardware can only use
certain address ranges:

- **ZONE_DMA / DMA32** — low addresses for old devices that can only DMA to the
  first 16 MB / 4 GB.
- **ZONE_NORMAL** — directly kernel-mapped RAM (the bulk on 64-bit systems).
- **ZONE_HIGHMEM** — memory not permanently kernel-mapped (a 32-bit relic; gone on
  64-bit).

Free pages within a zone are handed out by the **buddy allocator** (splits/merges
power-of-two page blocks to fight external fragmentation), and small kernel objects
come from the **slab/slub allocator** on top of it.

### The page cache — free RAM is wasted RAM

Linux uses **all spare RAM as a disk cache**: file data read from disk stays in the
**page cache** so repeat reads are memory-speed (§M6-DBMS buffer-pool idea, but for
the whole OS). Writes go to **dirty** pages flushed later by kernel threads
(writeback). This is why `free` shows little "free" memory — it's **cache**, and is
instantly reclaimable.

> **Memory hook:** on Linux, **"free" RAM is failed caching.** A healthy server has
> almost no truly-free RAM because the kernel filled it with **page cache**. That
> memory is *available*, not lost.

### kswapd and reclaim

When free pages fall below a **watermark**, the kernel thread **`kswapd`** wakes and
**reclaims** pages: it drops clean page-cache pages (free — just discard), writes
back dirty pages, and **swaps** anonymous (heap/stack) pages out to the swap area.
This keeps a pool of free pages ready. Under sudden pressure the allocating task may
do **direct reclaim** itself (a stall).

### The OOM killer

If reclaim can't free enough and memory is truly exhausted, the kernel invokes the
**Out-Of-Memory (OOM) killer**. It scores every process by an **`oom_score`** (based
mostly on memory footprint, adjustable via `oom_score_adj`) and **kills the
highest-scoring process** to save the system — famously "the OOM killer shot my
database." In containers, hitting a **cgroup memory limit** triggers OOM kill
*within that cgroup* (§14.7).

![Linux memory reclaim path: physical RAM in zones (DMA/Normal), most of it used as page cache; when free pages cross the low watermark kswapd reclaims (drop clean pages, write back dirty, swap anonymous). If reclaim fails, the OOM killer picks the highest oom_score process and kills it.](images/143_linux_memory_reclaim.png)

### MCQs

1. Where does Linux cache file data read from disk? → the **page cache**.
2. Kernel thread that reclaims memory when free pages get low? → **`kswapd`**.
3. What happens when memory is truly exhausted? → the **OOM killer** kills the
   highest-`oom_score` process.
4. Allocator that manages power-of-two free page blocks? → the **buddy allocator**.
5. Does high "used"/low "free" memory on Linux indicate a problem? → **No** — it's
   mostly reclaimable **page cache**.

---

## 14.5 The Virtual File System (VFS)

The **VFS** is the abstraction layer that lets one set of syscalls (`open`, `read`,
`write`, `close`, `stat`) work over **dozens of different filesystems** (ext4,
XFS, Btrfs, FAT, NFS, procfs…). Each filesystem implements a common set of
operations; the VFS dispatches to them. This is textbook **polymorphism in C**
(function-pointer "operations" tables) and is exactly the **"extended machine"** role
of an OS (§M1).

### The four core objects

| VFS object | Represents | Lives | Analogy |
|------------|-----------|-------|---------|
| **superblock** | a **mounted filesystem** as a whole | one per mount | the "volume header" |
| **inode** | a **file's metadata** (size, perms, owner, block pointers) — **no name** | one per file | the file's ID card |
| **dentry** | a **directory entry**: a **name → inode** link; builds the path tree | cached in RAM (dcache) | a name tag / index card |
| **file** | an **open file** by a process (holds the current **offset**, mode) | one per open() | a bookmark into the file |

![The four VFS objects: a superblock represents a mounted filesystem; a dentry maps a pathname component to an inode; an inode holds a file's metadata and block pointers (but no name); a file object is a process's open handle with its own read/write offset. Multiple file objects can point to the same inode.](images/144_vfs_objects.png)

> **The name-vs-file split (interview gold):** an **inode has no filename** — the
> name lives in the **dentry**. That is why:
> - **Hard links** = two dentries pointing to the **same inode** (same file, two
>   names; deleting one name just decrements the inode's **link count**).
> - **Deleting an open file** works: `unlink()` removes the dentry, but the inode
>   (and its data blocks) survive until the last **file** object closes — the
>   classic "disk still full after `rm`; a process still holds it open."

> **Memory hook:** **superblock = the filesystem; inode = the file; dentry = the
> name; file = your open handle (offset).** Names and files are *separate* — that
> single fact explains hard links, `rm` on open files, and rename.

### MCQs

1. What lets `read()`/`write()` work identically on ext4, XFS, and NFS? → the
   **VFS**.
2. Which VFS object stores a filename? → the **dentry** (NOT the inode).
3. Two names for one file (same inode) is a ___ → **hard link**.
4. Which object holds a process's current read/write **offset**? → the **file**
   object.
5. Why can you `rm` a file a process still has open? → the **inode** survives until
   the last **file** handle closes (dentry removed, link count → 0 later).

---

## 14.6 ext4 Basics

**ext4** (2008) is the long-time default Linux filesystem — a practical example of
the on-disk structures behind §14.5.

- **Inodes + block groups.** The disk is divided into **block groups**, each with its
  own inode table, block bitmap, and data blocks (locality → less seeking).
- **Extents (the big ext3→ext4 change).** Instead of listing every block
  individually (ext2/3's indirect-block scheme), ext4 records **extents** —
  `(start_block, length)` runs of contiguous blocks. One extent can map thousands of
  blocks, so large files need far less metadata and are less fragmented.
- **Journaling.** ext4 keeps a **journal** (write-ahead log, §M11/M12): it records
  intended changes before applying them, so after a crash it **replays/rolls back**
  the journal to reach a consistent state without a full `fsck`. Modes:
  **`journal`** (data + metadata journaled, safest/slowest), **`ordered`**
  (metadata journaled, data written first — the default), **`writeback`** (metadata
  only, fastest/riskiest).
- **Other niceties:** delayed allocation, larger volumes/files, `htree` directory
  indexing for fast lookup in huge directories.

> **Memory hook:** the two words for ext4 are **extents** (contiguous block runs →
> less metadata, less fragmentation) and **journaling** (crash consistency without a
> full disk scan). Successors **XFS** (great for huge/parallel I/O) and **Btrfs/ZFS**
> (copy-on-write, snapshots, checksums) push these ideas further.

### MCQs

1. What replaced indirect block pointers in ext4 for efficiency? → **extents**
   (`start, length`).
2. What gives ext4 crash consistency without a full `fsck`? → the **journal**
   (write-ahead log).
3. Default ext4 journaling mode? → **`ordered`** (metadata journaled, data first).

---

## 14.7 cgroups and Namespaces — The Foundation of Containers

This is the **most important section for backend/DevOps interviews.** Containers
(Docker, Kubernetes pods — M17) are **not** a special kernel feature. They are just
ordinary Linux processes wrapped in **two independent kernel mechanisms**:

- **Namespaces = isolation (what a process can SEE).**
- **cgroups = resource control (how much a process can USE).**

> **Memory hook:** **Namespaces give a process its own *view*; cgroups give it a
> *budget*.** A container = a process with a private view (namespaces) and a spending
> limit (cgroups). Say this in any interview and you've nailed containers.

### Namespaces — isolation

A **namespace** wraps a global system resource so that processes **inside** the
namespace see their **own isolated instance**. Created with `clone()`/`unshare()`
flags; visible under **`/proc/<pid>/ns/`**. The eight types (as of recent kernels):

| Namespace | Isolates | So a container gets… |
|-----------|----------|----------------------|
| **PID** | process IDs | its own PID 1; can't see host processes |
| **Mount (mnt)** | the mount table / filesystem view | its own root filesystem |
| **Network (net)** | interfaces, IPs, routes, ports | its own `eth0`, IP, firewall |
| **UTS** | hostname & domain name | its own hostname |
| **IPC** | System V IPC, POSIX msg queues | isolated shared memory |
| **User** | UID/GID mappings | **root inside, unprivileged outside** |
| **Cgroup** | the cgroup root view | its own cgroup hierarchy view |
| **Time** | boot & monotonic clocks | its own uptime (5.6+) |

> **The user namespace is the security keystone:** it maps UID 0 (root) *inside* the
> container to an unprivileged UID *on the host*. So even if an attacker becomes
> "root" in the container, they're just a normal user to the host kernel — a big
> reason "rootless" containers are safer (tie-in to M16).

### cgroups (control groups) — resource limits

**cgroups** organise processes into a hierarchy and **limit / account / prioritise**
their resource use through **controllers**:

| Controller | Limits |
|------------|--------|
| **cpu** | CPU shares / quota (e.g. "0.5 CPU") |
| **memory** | RAM limit (exceed → **cgroup OOM kill**, §14.4) |
| **io (blkio)** | disk read/write bandwidth & IOPS |
| **pids** | max number of processes (fork-bomb protection) |

**cgroup v2** (the modern unified hierarchy) exposes this under
`/sys/fs/cgroup/...` (a **sysfs**-style interface). When you run
`docker run --memory=512m --cpus=1.5`, Docker is just writing those numbers into a
cgroup.

![A container = a normal Linux process placed in new namespaces (isolation: its own PID/net/mnt/user view) and a cgroup (resource limits: cpu/memory/io/pids). Namespaces answer "what can I see?"; cgroups answer "how much can I use?". Together they create a lightweight isolated environment sharing the host kernel.](images/145_namespaces_cgroups.png)

> **Container vs VM (must-know, ties to M1 hypervisors and M16).** A **VM** runs a
> **full guest kernel** on a hypervisor (strong isolation, heavy). A **container
> shares the host kernel** and is isolated only by namespaces + cgroups (lightweight,
> starts in ms, but a **weaker security boundary** — a kernel bug can escape it;
> §M16). This single distinction is asked constantly.

### MCQs

1. Which mechanism gives a container its **isolated view** (own PID 1, own network)?
   → **namespaces**.
2. Which mechanism **limits** a container's CPU/memory/IO? → **cgroups**.
3. Which namespace makes a process **root inside but unprivileged outside**? → the
   **user** namespace.
4. What happens when a cgroup exceeds its memory limit? → **OOM kill within that
   cgroup**.
5. Do containers share the host kernel? → **Yes** (unlike VMs, which run their own
   kernel) — a weaker isolation boundary.

---

## 14.8 systemd and Init — Bringing Userspace to Life

After the kernel boots (bootloader → kernel → mounts root fs, §M2/M3), it starts the
**first user-space process, PID 1**, the **init** system. PID 1 is special: it is the
**ancestor of every process** and **reaps orphaned zombies** (§M4).

- **Traditional SysV init** ran numbered shell scripts sequentially (`/etc/rc.d`) —
  simple but slow (no parallelism) and no dependency tracking.
- **systemd** (today's default on most distros) replaces it with **units**
  (`.service`, `.socket`, `.mount`, `.timer`, `.target`). It starts services **in
  parallel**, resolves **dependencies**, does **socket activation** (start a service
  on first connection), tracks each service's processes **in a cgroup** (§14.7),
  restarts crashed services, and captures logs in the **journal** (`journalctl`).

> **Memory hook:** **PID 1 = init = the root of the process tree and the zombie
> reaper.** Modern PID 1 = **systemd**: parallel, dependency-aware, cgroup-backed
> service manager. (In a container, PID 1 is usually your app — which is why you
> need proper signal handling / a tiny init like `tini` to reap zombies.)

### MCQs

1. What is PID 1 and what special duty does it have? → the **init** process; it
   **reaps orphaned zombies** and is the ancestor of all processes.
2. Modern replacement for SysV init? → **systemd** (parallel, dependency-based).
3. How does systemd track a service's processes? → in a **cgroup**.

---

## 14.9 /proc and /sysfs — The Kernel as Files

Linux embodies the UNIX philosophy **"everything is a file."** Two **pseudo
(virtual) filesystems** — files backed by kernel data, not disk — let you read and
tune the kernel with ordinary file tools (`cat`, `echo`).

### /proc — processes and kernel state

**`/proc`** (procfs) exposes one directory **per process** (`/proc/<pid>/`) plus
system-wide files:

| Path | Shows |
|------|-------|
| `/proc/<pid>/status` | state, memory, UID, threads of that process |
| `/proc/<pid>/cmdline` | the command line it was started with |
| `/proc/<pid>/fd/` | symlinks to every **open file descriptor** |
| `/proc/<pid>/maps` | its **virtual-memory** map (which library/heap is where) |
| `/proc/<pid>/ns/` | its **namespaces** (§14.7) |
| `/proc/cpuinfo`, `/proc/meminfo` | CPU and memory info |
| `/proc/loadavg`, `/proc/mounts` | load average, mounted filesystems |

Tools like `ps`, `top`, and `htop` are just **pretty printers for `/proc`**.

### /sys (sysfs) — devices and the driver model

**`/sys`** (sysfs) exposes the kernel **device model**: buses, devices, drivers, and
their attributes as a clean tree — e.g. `/sys/class/net/eth0/` (network device),
`/sys/block/sda/` (a disk), `/sys/fs/cgroup/` (**cgroups**, §14.7). You often *tune*
the kernel by writing here (e.g. `echo 1 > /sys/.../parameter`).

> **Rule of thumb:** **`/proc` ≈ processes + legacy kernel knobs; `/sys` ≈ devices +
> the modern driver/cgroup model.** Both are **virtual** — the files have size 0 on
> disk; reading them runs kernel code.

```text
# Real examples you can run today:
$ cat /proc/$$/status | head        # info about your own shell ($$ = its PID)
$ ls /proc/1/ns                     # PID 1's namespaces
$ cat /proc/meminfo | grep Cached   # size of the page cache (§14.4)
$ ls /sys/class/net                 # your network interfaces
```

### MCQs

1. What kind of filesystems are `/proc` and `/sys`? → **pseudo/virtual** filesystems
   (backed by kernel data, not disk).
2. Where do you find a process's open file descriptors? → **`/proc/<pid>/fd/`**.
3. Where does a process's virtual-memory map live? → **`/proc/<pid>/maps`**.
4. Where does the modern **cgroup** interface live? → under **`/sys/fs/cgroup/`**.
5. `top`/`ps` read their data from? → **`/proc`**.

---

## 14.10 Real-World & Backend Perspectives

- **Every container you run** (`docker run`, a Kubernetes pod) is §14.7 in action:
  namespaces for isolation, cgroups for `--memory`/`--cpus` limits, sharing the host
  kernel. Understanding this is the difference between "using Docker" and
  "debugging why the pod got OOM-killed."
- **"OOM-killed" incidents (§14.4):** a container hits its cgroup memory limit and
  the kernel kills the process — you see exit code **137** (128 + SIGKILL 9). The fix
  is a memory limit or a leak fix, not "add RAM."
- **Load average & CFS:** the numbers in `top` come from `/proc/loadavg`; how quickly
  your app gets CPU under contention is CFS (now EEVDF) fairness at work; `nice`/
  `renice` and cgroup `cpu.weight` tune it.
- **Page cache tuning:** database and file servers live and die by the page cache;
  `free -m` "available" (not "free") is the number that matters.
- **Observability:** `strace` shows the **syscalls** an app makes (the §14.1 syscall
  boundary); `/proc/<pid>/maps` and `fd/` are your first stop when debugging leaks
  and "too many open files."

---

## 14.11 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** calling Linux a microkernel. It's a **monolithic (modular)** kernel.
- **Mistake:** thinking threads and processes are different kernel objects in Linux.
  Both are **`task_struct`s**; a thread just shares more (via `clone()` flags).
- **Mistake:** "my server has no free RAM!" — that's the **page cache**; it's
  reclaimable. Read **available**, not **free**.
- **Mistake:** confusing **namespaces** (isolation/visibility) with **cgroups**
  (resource limits). Different mechanisms; containers need **both**.
- **Edge case:** deleting a large open log file doesn't free disk space until the
  writing process closes it — because the **inode** outlives the **dentry** (§14.5).
- **Tradeoff (containers vs VMs):** containers are lightweight but share the kernel
  → **weaker isolation** (M16). Multi-tenant untrusted workloads sometimes use VMs
  or micro-VMs (Firecracker/gVisor) for a stronger boundary.
- **Edge case (CFS):** a `vruntime` that's grossly behind (e.g. a long-sleeping
  task) is clamped near the tree minimum on wake, so it can't monopolise the CPU.

---

## 14.12 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD / C-DAC:** monolithic vs microkernel (Linux = monolithic);
  `fork` vs `clone`; what `/proc` is; init/systemd; ext4 journaling — mostly
  conceptual MCQs.
- **GATE:** lighter here, but `fork()` process-tree/`printf` counting questions and
  scheduling fairness recur; know CFS at a conceptual level.
- **Interview (backend/infra — very high yield):**
  - "How does Linux represent a thread vs a process?" → one `task_struct`; `clone()`
    flags decide sharing.
  - "Explain CFS." → `vruntime`, run the smallest-vruntime task, RB-tree, nice→weight.
  - "What are namespaces vs cgroups?" → isolation (view) vs resource limits (budget);
    the container foundation.
  - "Why did my container get OOM-killed?" → cgroup memory limit → OOM killer.
  - "What's the difference between a container and a VM?" → shared host kernel
    (namespaces+cgroups) vs full guest kernel on a hypervisor.
- **Coding/practical:** `strace ./app` (see syscalls), `cat /proc/<pid>/maps`,
  `ls /proc/<pid>/fd`, `nsenter`/`unshare` to play with namespaces, `systemctl` and
  `journalctl` for services.

---

## 14.13 Concept Checks & MCQs (test yourself)

1. Linux kernel type? → **monolithic**, modular via **loadable kernel modules**.
2. One structure for processes and threads? → **`task_struct`**.
3. `clone()` flag that shares the address space (makes a thread)? → **`CLONE_VM`**.
4. `fork()` shares memory via? → **copy-on-write**.
5. CFS picks which task? → **smallest `vruntime`** (leftmost RB-tree node).
6. Nice-0 weight and per-nice CPU change? → **1024**, **~10%** per level.
7. Data structure in CFS? → **red-black tree** keyed by `vruntime`.
8. What replaced CFS in kernel 6.6? → **EEVDF**.
9. Kernel thread that reclaims memory? → **`kswapd`**.
10. Reclaim fails, memory exhausted → ? → **OOM killer** (highest `oom_score`).
11. Where is file data cached? → the **page cache** (reclaimable).
12. VFS's four objects? → **superblock, inode, dentry, file**.
13. Which VFS object stores the **name**? → the **dentry** (not the inode).
14. Two names → one inode is a ___ → **hard link**.
15. ext4's efficient block mapping? → **extents**; crash safety via **journaling**.
16. Namespaces provide ___; cgroups provide ___. → **isolation (view)** ;
    **resource limits (budget)**.
17. Namespace giving "root inside, unprivileged outside"? → **user** namespace.
18. Container vs VM? → **shares host kernel** vs **own guest kernel**.
19. PID 1's special duty? → it's **init**; reaps **orphaned zombies**.
20. Modern init? → **systemd** (parallel, dependency-based, cgroup-backed).
21. `/proc` and `/sys` are ___ filesystems → **pseudo/virtual**.
22. Open FDs of a process live in? → **`/proc/<pid>/fd/`**.

**True/False**
- Linux threads and processes are different kernel objects. → **False** (both
  `task_struct`).
- A high `vruntime` means a task should run next. → **False** (**smallest** runs
  next).
- On Linux, low "free" memory is a problem. → **False** (it's page cache).
- An inode stores the filename. → **False** (the dentry does).
- Namespaces limit CPU/memory. → **False** (that's **cgroups**).
- A container runs its own kernel. → **False** (shares the host kernel).

---

## 14.14 One-Page Revision Sheet

```
LINUX = MONOLITHIC kernel + loadable MODULES. User space -> SYSCALL -> kernel.
  Subsystems: process/sched | memory(MM) | VFS | net | drivers | arch.

PROCESS/THREAD:
  task_struct = the PCB for BOTH processes and threads (no separate thread object).
  fork()   = clone() sharing ~nothing (own addr space, COPY-ON-WRITE).
  thread   = clone(CLONE_VM|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD) share everything.
  getpid()=TGID (shared), gettid()=TID (per-thread, what scheduler uses).

CFS (default 2.6.23 -> 6.6; then EEVDF):
  vruntime = "CPU already eaten". RUN THE SMALLEST vruntime (most starved).
  vruntime += delta_exec * (1024 / weight).  nice -20..+19, weight=1024/1.25^nice,
    nice0 weight=1024, ~10% CPU per nice step.
  Red-Black tree keyed by vruntime; leftmost = next (O(1) pick, O(log n) update).
  Sleepers wake with small vruntime -> interactive & responsive. No fixed quantum.

MEMORY: zones(DMA/Normal/High) ; buddy allocator (power-of-2) ; slab (small objs).
  PAGE CACHE = spare RAM caches disk (free RAM = wasted). "available" not "free".
  kswapd reclaims at low watermark (drop clean / writeback dirty / SWAP anon).
  OOM KILLER kills highest oom_score when reclaim fails (cgroup limit -> cgroup OOM).

VFS (one API over many FS):  SUPERBLOCK=mounted FS | INODE=file metadata (NO name)
  | DENTRY=name->inode | FILE=open handle (offset).
  inode has NO name => hard link = 2 dentries -> 1 inode; rm on open file OK
  (inode lives till last file closed).
EXT4 = EXTENTS (start,len runs) + JOURNALING (ordered=default). block groups.

CONTAINERS = process + NAMESPACES (isolation: what you SEE) + CGROUPS (limits: how
  much you USE). Namespaces: pid/mnt/net/uts/ipc/USER(root in,unpriv out)/cgroup/time.
  cgroup controllers: cpu/memory/io/pids. Container SHARES host kernel (VM = own kernel).

INIT: PID 1 = init = ancestor + reaps zombies. Modern = SYSTEMD (parallel, deps,
  units, cgroup-tracked, journalctl).
/proc = per-process + kernel state (/proc/<pid>/{status,fd,maps,ns}); /sys = devices +
  cgroups (/sys/fs/cgroup). Both PSEUDO/virtual (backed by kernel, not disk).
```

### Flash cards

| Front | Back |
|-------|------|
| Linux kernel type? | Monolithic (modular / LKMs) |
| Process & thread structure? | one `task_struct` |
| fork vs thread creation? | same `clone()`, different share flags |
| CFS runs which task? | smallest `vruntime` |
| CFS data structure? | red-black tree (by vruntime) |
| Nice-0 weight / per-step CPU? | 1024 / ~10% |
| Replaced CFS in 6.6? | EEVDF |
| Memory reclaimer thread? | kswapd |
| Last-resort on OOM? | OOM killer (oom_score) |
| Free RAM used for? | page cache |
| VFS 4 objects? | superblock, inode, dentry, file |
| Which VFS object has the name? | dentry (not inode) |
| ext4 key features? | extents + journaling |
| Namespaces vs cgroups? | isolation (view) vs limits (budget) |
| "root inside, unpriv outside"? | user namespace |
| Container vs VM? | shared host kernel vs own kernel |
| PID 1 duties? | init + reap zombies |
| /proc & /sys are? | pseudo/virtual filesystems |

### Spaced repetition
- **24-hour:** recite `task_struct`/`clone`, the CFS rule (run smallest vruntime),
  and namespaces-vs-cgroups.
- **7-day:** explain the memory reclaim path (page cache → kswapd → swap → OOM), the
  four VFS objects, and container vs VM.
- **30-day:** given "my container was OOM-killed" or "rm didn't free space," explain
  the exact kernel reason using cgroups/OOM and inode/dentry.

---

## 14.15 Summary

Linux is a **monolithic, modular** kernel reached only through **system calls**. It
represents **every process and thread as one `task_struct`**, and builds threads and
processes from the **same `clone()`** primitive by choosing what to share
(`CLONE_VM` = a thread; `fork()` = a copy-on-write new address space). Its scheduler,
**CFS**, keeps things fair by running the task with the **smallest `vruntime`** —
stored in a **red-black tree**, weighted by **nice** values (~10% CPU per step) —
and was replaced by the closely-related **EEVDF** in kernel 6.6. Its memory manager
splits RAM into **zones**, uses spare RAM as **page cache**, reclaims via **`kswapd`**
(and **swap**), and, as a last resort, invokes the **OOM killer**. The **VFS**
abstracts many filesystems behind four objects — **superblock, inode, dentry,
file** — where the crucial split of **name (dentry) from file (inode)** explains hard
links and deleting open files; **ext4** implements this with **extents** and
**journaling**. Most important for modern infrastructure: **namespaces** (isolation —
what a process can *see*) and **cgroups** (limits — how much it can *use*) together
create **containers**, ordinary processes that **share the host kernel**. Userspace
is launched by **PID 1 (systemd)**, and the whole kernel is inspectable as files
through **`/proc`** and **`/sys`**.

Next, **Module 15 — Concurrency** goes deeper into the hardest problem all of this
rests on: making many tasks run *correctly* at once — atomics, memory ordering, and
lock-free programming.

> **You have mastered this module when** you can: say why Linux is monolithic-modular;
> explain `task_struct`/`clone()` and how a thread differs from `fork()`; describe
> CFS (vruntime, RB-tree, nice→weight) end to end; trace the memory-reclaim path to
> the OOM killer; name the four VFS objects and why name≠file; and crisply
> distinguish **namespaces vs cgroups** and **container vs VM** — all without notes.
