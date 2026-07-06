---
title: "Module 4 — Processes"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — Processes

> **Where this module sits.**
> Module 1 said an OS is a **resource manager**. But *what* is it managing? The
> answer is the **process** — a program in execution, the unit the OS schedules,
> protects, and accounts for. This is the beating heart of the whole subject:
> **CPU scheduling (M6)** decides which process runs next; **synchronization (M7)**
> keeps cooperating processes from corrupting shared data; **memory management
> (M9)** gives each process its own address space; and **IPC (M7)** lets processes
> talk. Get the process model right here and every later module clicks. This module
> covers the **PCB**, the **process state diagram**, **context switching**, and the
> UNIX creation syscalls **fork / exec / wait** that every backend engineer must
> know cold.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★    | ★★★★      | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **program vs process**;
**PCB** contents; the **process state diagram** (esp. ready↔running↔waiting and the
**suspended** states); **context switch** (what is saved, why it is pure overhead);
**fork()** return value (parent vs child) and the classic **"how many processes for
N forks = 2ⁿ"** counting question; **exec()** vs **fork()**; **wait()/waitpid()**;
**zombie vs orphan** and how each is handled; **daemon** processes; **IPC**
(shared memory vs message passing, pipes).

---

## 4.1 Program vs Process (first principles)

A **program** is a **passive** entity — a file of instructions sitting on disk
(`/bin/ls`, `a.out`). A **process** is an **active** entity — that program **loaded
into memory and executing**, with its own CPU state, memory, and OS bookkeeping.

> **Memory hook:** a **program is the recipe**; a **process is the cooking** — the
> chef, the hot pans, the half-chopped onions. One recipe (program) can drive **many
> simultaneous cookings** (processes): run `python` in three terminals → **one
> program, three processes**, each with its own memory and progress.

### The four segments of a process in memory

When a program becomes a process, the OS lays out its address space into four parts:

```text
   high address
   ┌───────────────┐
   │     STACK     │  ← function calls, local vars, return addrs (grows DOWN)
   │      ↓        │
   │      ...      │  ← free gap
   │      ↑        │
   │     HEAP      │  ← dynamic memory: malloc/new (grows UP)
   ├───────────────┤
   │  DATA (BSS +  │  ← global & static variables
   │   initialised)│
   ├───────────────┤
   │  TEXT (CODE)  │  ← the machine instructions (read-only, shareable)
   low address
   └───────────────┘
```

- **Text/Code** — the instructions (read-only, so many processes running the same
  program can **share one copy**).
- **Data** — global and static variables (initialised data + **BSS** for
  zero-initialised).
- **Heap** — dynamically allocated memory (`malloc`, `new`), **grows up**.
- **Stack** — local variables, parameters, return addresses, **grows down**.

> **Why stack and heap grow toward each other:** they start at opposite ends of the
> free region so each can expand into the shared gap. If they collide you get a
> **stack overflow** / out-of-memory.

### MCQs

1. Program vs process? → **passive file on disk** vs **active program in execution**.
2. One program can have how many processes? → **many** (each independent).
3. Which segment is read-only and shareable? → **text/code**.
4. `malloc`/`new` memory comes from the? → **heap**.

---

## 4.2 The Process Control Block (PCB)

The **PCB** (also called the **process descriptor**, or `task_struct` in Linux) is
the OS's **data structure for one process** — everything the kernel must remember to
pause, resume, schedule, and account for it. **There is one PCB per process**, kept
in a kernel table.

![The Process Control Block stores identity, CPU state, scheduling, memory, and I/O information for one process; the OS keeps one per process.](images/33_pcb_fields.png)

| Field group | What it stores |
|---|---|
| **Process state** | new / ready / running / waiting / terminated |
| **Process ID (PID)** | unique number identifying the process; **parent PID (PPID)** |
| **Program counter (PC)** | address of the **next instruction** to execute |
| **CPU registers** | all register values (saved on a context switch) |
| **CPU-scheduling info** | priority, scheduling queue pointers, time-quantum info |
| **Memory-management info** | base/limit registers, **page tables** / segment tables |
| **Accounting info** | CPU time used, time limits, process number |
| **I/O status info** | list of open files, allocated I/O devices, pending I/O |

> **Memory hook:** the PCB is the process's **passport + medical chart**. When the
> CPU is taken away, the OS writes the process's entire "vital signs" (PC, registers,
> state) into the PCB; to resume it, the OS reads them back. **No PCB = the OS
> cannot manage the process.**

> **The PC and registers are the crucial pair.** They are exactly what makes it
> possible to **stop a process mid-instruction-stream and resume later as if nothing
> happened** — the whole illusion of multitasking rests on saving/restoring them.

### MCQs

1. Per-process OS data structure? → **PCB** (Process Control Block).
2. What in the PCB points to the next instruction? → the **program counter**.
3. Linux name for the PCB? → **`task_struct`**.
4. Where are page-table pointers kept? → in the PCB's **memory-management info**.

---

## 4.3 The Process State Diagram

A process is not always running — it moves through a small set of **states** as it
competes for the CPU and waits on I/O. **This diagram is one of the most-asked
figures in the entire syllabus.**

![Process state diagram: new→ready→running, running↔ready via scheduler and interrupt, running→waiting on I/O and back to ready, running→terminated; plus suspended (swapped-out) ready and waiting states.](images/34_process_states.png)

### The five core states

| State | Meaning |
|---|---|
| **New** | process is being **created** (PCB allocated, not yet ready) |
| **Ready** | in memory, **waiting only for the CPU** (sitting in the ready queue) |
| **Running** | instructions are **executing on the CPU** |
| **Waiting / Blocked** | waiting for an **event** (I/O completion, a signal, a lock) |
| **Terminated / Exit** | finished executing; PCB about to be released |

### The transitions (learn every arrow)

```text
  new ──admit──▶ ready ──dispatch(scheduler)──▶ running ──exit──▶ terminated
                   ▲                              │  │
                   │  ◀──interrupt/timeout────────┘  │  (time quantum expires)
                   │                                 ▼
                   └───I/O or event complete──── waiting ◀── I/O or event wait
```

- **admit:** new → ready (long-term scheduler admits it).
- **dispatch:** ready → running (short-term scheduler / dispatcher picks it).
- **interrupt / timeout:** running → ready (its **time quantum** expired, or a
  higher-priority process preempted it — it is *still runnable*).
- **I/O or event wait:** running → waiting (it requested I/O or a resource).
- **I/O or event completion:** waiting → **ready** (note: it goes back to **ready**,
  **not** straight to running — it must be re-scheduled).
- **exit:** running → terminated.

> **The #1 trap:** after I/O completes, a process goes **waiting → ready**, *not*
> **waiting → running**. It must wait its turn for the CPU again. Only the
> **dispatcher** moves a process into **running**, and **only one process per CPU
> core** can be running at a time.

### Suspended states (swapping)

When memory is scarce, the OS can **swap** a process out to disk, freeing RAM. This
adds two states:

- **Ready-suspended:** was ready, now swapped out to disk (runnable once swapped in).
- **Waiting/Blocked-suspended:** was blocked *and* swapped out.

> **Memory hook:** *suspended = "on the bench, sent to the locker room (disk)."*
> Swapping is the bridge to **virtual memory (M10)**.

### MCQs

1. A process waiting only for the CPU is in which state? → **ready**.
2. After I/O completes, a process moves to? → **ready** (not running).
3. Which state means "waiting for an event/I/O"? → **waiting / blocked**.
4. What moves a process from ready to running? → the **dispatcher** (short-term
   scheduler).
5. Swapping a process to disk puts it in a ___ state → **suspended**.

---

## 4.4 Context Switching

A **context switch** is the act of **saving the state of the running process into
its PCB and loading the state of the next process from its PCB**, so the CPU can
switch from one process to another.

![Context switch: process P0 running, an interrupt saves P0's state into PCB0, the OS loads PCB1, P1 runs; the CPU is idle (pure overhead) during both save and restore.](images/35_context_switch.png)

### What exactly is saved and restored?

The **CPU context** — everything in the PCB that defines "where the process was":

- the **program counter** (next instruction),
- all **CPU registers** (general-purpose, stack pointer, status/flags),
- **memory-management state** (e.g. page-table base register — switching this may
  flush the **TLB**, adding cost).

### When does a context switch happen?

- **Timer interrupt** — the running process's time quantum expired.
- **I/O request / wait** — the process blocks.
- **Higher-priority process** becomes ready (preemption).
- **System call / interrupt** handling, and process exit.

> **Why a context switch is PURE OVERHEAD:** during the switch the CPU does **no
> useful user work** — it is only shuffling bookkeeping. Every microsecond spent
> switching is a microsecond stolen from real computation. Typical cost is **~1–10
> microseconds**, but the *hidden* cost is bigger: the new process starts with a
> **cold cache and cold TLB**, so it runs slower until they warm up.

> **Design consequence (ties to M6):** this is why the **time quantum** in Round
> Robin must not be too small — if the quantum ≈ the switch cost, the CPU spends half
> its time switching instead of working. It is also **the** reason threads (M5) are
> attractive: switching between **threads of the same process** is cheaper because
> the address space (and often the TLB) does **not** change.

### MCQs

1. What is saved on a context switch? → the **PC + registers + memory-management
   state** (into the PCB).
2. Why is a context switch overhead? → the CPU does **no useful work** during it.
3. Name two events that trigger a switch. → **timer interrupt** and **I/O wait**
   (also preemption, exit).
4. Why is a thread switch cheaper than a process switch? → same **address space**
   (no page-table/TLB change).

---

## 4.5 The Process Tree & Process Creation

Every process (except the very first) is **created by another process**, forming a
**tree**. In UNIX/Linux the root is **`init`/`systemd` (PID 1)**, started by the
kernel at boot; it is the ancestor of every other process.

![A process creation tree: init (PID 1) is the root; it spawns login/shell, which forks user programs; each child records its parent (PPID), forming a hierarchy.](images/36_process_tree.png)

```text
                 init / systemd  (PID 1)
                 /       |        \
             login    sshd      cron
               |        |
             bash     bash
            /    \       \
          ls    python   gcc      ← each child has a parent PID (PPID)
```

- The creator is the **parent**; the created process is the **child**.
- Inspect the live tree with **`pstree`** or `ps -ef` (the **PPID** column).
- **Resource sharing models:** parent and child may share all, some, or no
  resources. **Execution:** the parent may run **concurrently** with the child, or
  **wait** for it to finish.

### MCQs

1. Root of the UNIX process tree? → **init / systemd (PID 1)**.
2. The process that creates another is the? → **parent**.
3. Command to view the process tree? → **`pstree`**.

---

## 4.6 fork() — Creating a Process

**`fork()`** is the UNIX system call that creates a **new process by duplicating the
calling process**. The child is an almost-exact **copy** of the parent: same code,
same data (a separate copy), same open files, same PC — it resumes **right after the
`fork()`**.

### The single most important fact: the return value

`fork()` is called **once** but **returns twice** — once in each process:

| Where | `fork()` returns | Meaning |
|---|---|---|
| **In the parent** | the **child's PID** (a positive number > 0) | so the parent knows its child |
| **In the child** | **0** | "you are the child" |
| **On failure** | **−1** (in the parent; no child made) | e.g. process-table full |

> **Memory hook:** *"Parent gets the child's number; the child gets zero."* This is
> the branch every fork program uses to make parent and child do different things.

### A worked C example

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid = fork();          // called ONCE, returns TWICE

    if (pid < 0) {               // fork failed
        perror("fork");
        return 1;
    } else if (pid == 0) {       // ---- CHILD (fork returned 0) ----
        printf("Child : my PID=%d, my parent=%d\n", getpid(), getppid());
    } else {                     // ---- PARENT (fork returned child PID) ----
        printf("Parent: my PID=%d, my child=%d\n", getpid(), pid);
        wait(NULL);              // reap the child (see 4.8) to avoid a zombie
    }
    return 0;
}
```

> **Copy-on-write (COW) — how fork is fast (interview gold):** naively, copying the
> parent's entire memory would be slow. Modern kernels instead let parent and child
> **share the same physical pages, marked read-only**; a page is **copied only when
> one of them writes to it**. So `fork()` is cheap until memory actually diverges.

### The classic counting question: "how many processes for N forks?"

Each `fork()` **doubles** the number of processes (every existing process spawns one
child). So after **N** successive `fork()` calls executed by **all** resulting
processes:

```text
Total processes = 2^N        (including the original)
Children created = 2^N − 1
```

> **Worked example — 3 forks in a row:**
> ```c
> fork();   // 1 → 2 processes
> fork();   // 2 → 4 processes
> fork();   // 4 → 8 processes
> ```
> **Total = 2³ = 8 processes** (7 new children + 1 original). Trace it: after the
> 1st fork there are 2; **both** run the 2nd fork → 4; **all four** run the 3rd
> fork → **8**. The number of **`printf`s** after the last fork would be 8.

> **Variant trap:** if the code is `fork() && fork()` or `fork() || fork()`,
> **short-circuit evaluation** means not every process reaches the second fork —
> count carefully. And `for(i=0;i<n;i++) fork();` is the same as *n* sequential
> forks → **2ⁿ** processes.

### MCQs

1. What does `fork()` return in the child? → **0**.
2. In the parent? → the **child's PID** (>0); **−1** on failure.
3. Total processes after 4 forks in a row? → **2⁴ = 16**.
4. How does modern `fork()` avoid copying all memory? → **copy-on-write**.

---

## 4.7 exec() — Replacing the Program

`fork()` makes a **copy** of the *same* program. To run a **different** program you
use the **`exec()`** family, which **replaces the current process's memory image**
(text, data, heap, stack) with a **new program** — but keeps the **same PID**.

> **The fork–exec idiom (the core of how shells launch commands):**
> ```text
> pid = fork();               // 1. duplicate ourselves
> if (pid == 0)               // 2. in the CHILD:
>     execvp("ls", args);     //    become a totally new program (ls)
> else                        // 3. in the PARENT (the shell):
>     waitpid(pid, ...);      //    wait for the command to finish
> ```
> This is exactly what your shell does for every command you type: **fork** a child,
> **exec** the program into it, **wait** for it.

- **`exec()` succeeds → it never returns** (the old program is gone). Any code after
  a successful `exec` does **not** run.
- **`exec()` returns only on failure** (e.g. file not found), returning **−1**.
- The family differs by how you pass arguments/environment/path:

| Call | Args | PATH search | Environment |
|---|---|:---:|---|
| `execl` / `execlp` / `execle` | **l**ist (`arg0, arg1, …, NULL`) | `p` = yes | `e` = custom |
| `execv` / `execvp` / `execve` | **v**ector (`char *argv[]`) | `p` = yes | `e` = custom |

> **`execve()` is the real system call**; all the others are C-library wrappers
> around it. Mnemonic: **l** = list of args, **v** = vector (array) of args,
> **p** = search **PATH**, **e** = pass an **environment** array.

### MCQs

1. What does a successful `exec()` return? → **nothing — it never returns**.
2. Does `exec()` change the PID? → **no** (same process, new program).
3. `fork` vs `exec`? → **fork copies** the current program; **exec replaces** it
   with a new one.
4. The underlying system call for the exec family? → **`execve()`**.

---

## 4.8 wait() / waitpid() — Reaping Children

When a child finishes, it becomes a **zombie** (see 4.9) until the parent collects
its **exit status**. The parent does this with **`wait()`** (any child) or
**`waitpid()`** (a specific child), an act called **reaping**.

```c
int status;
pid_t child = wait(&status);           // block until ANY child exits
// or wait for a specific child:
waitpid(pid, &status, 0);              // 0 = block; WNOHANG = don't block

if (WIFEXITED(status))                 // did it exit normally?
    printf("child exited with %d\n", WEXITSTATUS(status));  // its exit code
```

- **`wait(&status)`** blocks the parent until **any one** child terminates, returns
  that child's PID, and writes its exit info into `status`.
- **`waitpid(pid, &status, options)`** waits for a **specific** child; with the
  **`WNOHANG`** option it returns immediately (non-blocking poll) if no child has
  exited yet.
- Macros **`WIFEXITED`** / **`WEXITSTATUS`** decode the status word.

> **Why reaping matters:** `wait()` is what lets the OS **free the child's PCB**.
> Skip it and the finished child lingers as a **zombie**, leaking a PCB slot.

### MCQs

1. What does `wait()` do? → **blocks** the parent until a child exits and **reaps**
   it (frees its PCB).
2. Non-blocking wait option? → **`WNOHANG`** with `waitpid`.
3. How to get a child's exit code? → **`WEXITSTATUS(status)`** (after `WIFEXITED`).

---

## 4.9 Zombie vs Orphan Processes

Two special situations arise from the parent–child relationship. **Exams love the
"which is which" contrast.**

| | **Zombie** (defunct) | **Orphan** |
|---|---|---|
| **What happened** | child **finished**, but parent **hasn't `wait()`ed** yet | **parent died** while the child is still running |
| **Who is alive** | child is **dead**; parent alive but negligent | child is **alive**; parent is dead |
| **Problem** | its **PCB entry stays** (holds a PID/status) | it has **no parent** to reap it |
| **How it's handled** | parent calls **`wait()`** → PCB freed | it is **reparented to `init` (PID 1)**, which reaps it |

> **Memory hook:**
> - **Zombie = dead child, un-reaped** ("dead but still in the process table,
>   waiting to be buried by `wait()`").
> - **Orphan = live child, dead parent** ("adopted by `init`").

> **Why a zombie is (a little) dangerous:** a zombie uses almost no memory (just a
> PCB slot holding the exit status), but a program that **forks in a loop and never
> `wait()`s** will fill the process table and eventually **`fork()` fails (−1)** —
> a real production bug. The fix: always reap children (call `wait`/`waitpid`, or
> handle `SIGCHLD`).

> **How orphans are auto-cleaned:** when a parent dies, the kernel **re-parents its
> children to PID 1 (`init`/`systemd`)**. `init` continuously calls `wait()`, so
> orphaned children never become permanent zombies.

### MCQs

1. Child finished but not reaped? → **zombie**.
2. Parent died, child still running? → **orphan**.
3. An orphan is adopted by? → **`init` / `systemd` (PID 1)**.
4. How is a zombie removed? → the parent calls **`wait()`** (reaps it).
5. What happens if you never reap children in a loop? → the **process table fills**,
   `fork()` starts failing.

---

## 4.10 Daemons — Background Service Processes

A **daemon** is a long-running **background process** that provides a service and is
**not attached to a controlling terminal** — it starts at boot and runs quietly.
By convention their names often **end in `d`**: `sshd` (SSH server), `httpd`
(web server), `crond` (scheduler), `systemd`.

- Typically **parented by `init`/`systemd` (PID 1)** and run without user
  interaction.
- Classic creation ("daemonizing"): `fork()`, let the parent exit (so the child is
  orphaned and adopted by init), **`setsid()`** to start a new session and detach
  from the terminal, then redirect stdin/stdout/stderr.

> **Memory hook:** a **daemon is a "waiter on standby"** — always in the background,
> no terminal of its own, ready to serve requests (a connection, a timer, a print
> job). Every backend server you run (nginx, postgres, redis) runs as a daemon.

### MCQs

1. A background service process with no terminal? → **daemon**.
2. Daemons are usually the child of? → **init / systemd**.
3. Naming convention for daemons? → often **ends in `d`** (`sshd`, `httpd`).

---

## 4.11 Inter-Process Communication (IPC) — a Bridge to M7

Processes are **isolated** (each has its own address space), which is great for
safety but means cooperating processes need an explicit way to **exchange data**.
There are two fundamental models.

![IPC models: shared memory (both processes map a common region and read/write it directly — fast, needs synchronization) vs message passing (processes send/receive via the kernel — slower, but clean isolation).](images/37_ipc_models.png)

### Model 1 — Shared Memory

The OS lets two processes **map the same region of physical memory** into both
their address spaces; they then communicate by **reading and writing that region
directly**.

- **Pro:** **fastest** — after setup, no kernel involvement per access (memory-speed).
- **Con:** the processes must **synchronize** themselves (semaphores/mutexes, M7) to
  avoid **race conditions** on the shared region.

### Model 2 — Message Passing

Processes communicate by **sending and receiving messages through the kernel**
(`send`/`receive`), never touching each other's memory.

- **Pro:** clean **isolation**, easier to reason about, works **across machines**
  (networking).
- **Con:** **slower** — every message is copied via the kernel (two copies:
  user→kernel→user).

| | Shared memory | Message passing |
|---|---|---|
| **Speed** | fast (direct access) | slower (kernel-mediated copies) |
| **Synchronization** | **you** must do it (mutex/semaphore) | handled by send/receive |
| **Scope** | same machine | same machine **or over a network** |
| **Ease** | harder (races) | easier / safer |

### Common IPC mechanisms (know the list)

- **Pipes** — a one-way byte stream. **Anonymous pipe** (`|` in the shell) connects
  **related** processes (parent↔child); **named pipe (FIFO)** connects **unrelated**
  processes via a filesystem name.
- **Message queues** — kernel-maintained list of discrete messages.
- **Shared memory** — the model above (POSIX `shm_open`/`mmap`, System V `shmget`).
- **Sockets** — endpoints for communication, including **across the network** (the
  basis of all networked services).
- **Signals** — a lightweight async notification (e.g. `SIGCHLD`, `SIGKILL`).

> **Memory hook:** *shell pipe* `ls | grep txt` is IPC in the wild — the kernel
> creates a **pipe**, `ls`'s stdout becomes the pipe's write end and `grep`'s stdin
> its read end. **Two processes, one byte stream.** Full synchronization and
> the producer–consumer problem come in **Module 7**.

### MCQs

1. Two IPC models? → **shared memory** and **message passing**.
2. Which is faster, and what's its catch? → **shared memory**; it needs **explicit
   synchronization**.
3. `ls | grep` uses which mechanism? → an **(anonymous) pipe**.
4. IPC that works across a network? → **sockets** (message passing).
5. Named pipe vs anonymous pipe? → **FIFO connects unrelated** processes; anonymous
   connects **related** (parent/child) ones.

---

## 4.12 Real-World & Backend Perspectives

- **Every server is a fork/exec story.** Classic servers (Apache prefork,
  PostgreSQL) **fork a worker process per connection**; the OS's process model *is*
  your concurrency model. Understanding COW fork explains why forking is cheap.
- **Zombies are a real outage cause.** A supervisor that spawns workers but forgets
  to reap them (`SIGCHLD`/`wait`) slowly exhausts the PID table until nothing can
  start. `docker` PID-1 "zombie reaping" (`--init` / tini) exists exactly for this.
- **Containers are processes.** A Docker container is (mostly) a process tree in
  isolated **namespaces**; PID 1 inside it must reap orphans or you leak zombies.
- **Context-switch cost is why async exists.** Node.js/nginx use an **event loop**
  (few threads, no per-request process) precisely to avoid thousands of expensive
  context switches under high concurrency.

---

## 4.13 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking `fork()` returns the *same* value in both processes. It
  returns **0 to the child, child-PID to the parent**.
- **Mistake:** believing code after a successful `exec()` runs. It **never does**
  (the old image is gone).
- **Mistake:** "waiting → running" after I/O. It is **waiting → ready**.
- **Mistake:** counting forks. `n` sequential forks = **2ⁿ** processes, not 2n or
  n+1 — and watch **short-circuit** `&&`/`||`.
- **Edge case:** a **zombie can't be killed** with `kill` — it's already dead; you
  must make its **parent reap it** (or kill the parent so `init` adopts and reaps).
- **Tradeoff:** processes (isolation, safety, expensive to switch) vs **threads**
  (shared memory, cheap to switch, but need synchronization) — the whole reason
  **Module 5** exists.

---

## 4.14 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** program-vs-process, PCB contents, the state diagram,
  zombie-vs-orphan one-liners, and daemon definitions are frequent MCQs.
- **GATE:** the **fork-counting** numerical (2ⁿ, with `&&`/`||` traps) and the
  **process-state transitions** are perennial. Know that I/O completion → **ready**.
- **Interview (backend/systems):** "What happens when you type `ls` and press
  Enter?" → **fork + exec + wait**. "Zombie vs orphan?" "How does `fork` avoid
  copying all memory?" → **copy-on-write**. "Why are context switches expensive?"
- **Coding:** be able to write the fork/exec/wait skeleton and predict the output
  (and process count) of a small fork program.

---

## 4.15 Concept Checks & MCQs (test yourself)

1. Program vs process? → **passive file** vs **program in execution**.
2. Per-process kernel structure? → **PCB** (`task_struct` in Linux).
3. Three things saved on a context switch? → **PC, registers, memory-mgmt state**.
4. After I/O completes, the process becomes? → **ready**.
5. `fork()` return value in child / parent? → **0** / **child PID** (−1 on fail).
6. Processes after 5 sequential forks? → **2⁵ = 32**.
7. Does `exec` change the PID? → **no**.
8. What does `wait()` return? → the **terminated child's PID** (and its status).
9. Dead child not reaped? → **zombie**; parent-less live child? → **orphan**.
10. Orphan is adopted by? → **init/systemd (PID 1)**.
11. Background service process, no terminal? → **daemon**.
12. Two IPC models? → **shared memory** (fast, needs sync) / **message passing**.
13. `ls | grep` mechanism? → **pipe**.
14. Real system call behind the exec family? → **`execve`**.
15. Why is a context switch pure overhead? → **no useful user work** happens during
    it (plus cold cache/TLB afterwards).

**True/False**
- `fork()` is called once and returns twice. → **True**.
- Code after a successful `exec()` runs. → **False**.
- A zombie can be removed with `kill`. → **False** (parent must `wait`).
- I/O completion moves a process straight to running. → **False** (→ ready).
- Threads of one process share the address space. → **True** (preview of M5).

---

## 4.16 One-Page Revision Sheet

```
PROGRAM = passive file on disk. PROCESS = program in execution (active).
  Memory: TEXT(code,RO,shared) | DATA(globals+BSS) | HEAP(malloc, grows UP) | STACK(grows DOWN).

PCB (task_struct): STATE, PID/PPID, PROGRAM COUNTER, REGISTERS, sched info(priority,queues),
  memory info(base/limit, PAGE TABLES), accounting(CPU time), I/O(open files). One per process.

STATES: new -admit-> READY -dispatch-> RUNNING -exit-> terminated
  RUNNING -timeout/preempt-> READY ;  RUNNING -I/O wait-> WAITING ;  WAITING -I/O done-> READY(!)
  SUSPENDED (swapped to disk): ready-suspended / blocked-suspended.
  TRAP: I/O done => READY (not running). Only dispatcher -> running.

CONTEXT SWITCH: save PC+registers+mem-state to old PCB, load new PCB. PURE OVERHEAD (no user work;
  cold cache/TLB after). Triggers: timer, I/O wait, preemption, exit. ~1-10us. Thread switch cheaper.

PROCESS TREE: root = init/systemd (PID 1). parent forks child (records PPID). pstree / ps -ef.

fork(): once-called, TWICE-returned. child gets 0 ; parent gets CHILD PID ; -1 on fail.
  Copy-On-Write (share pages RO, copy on write) => fast. N sequential forks => 2^N processes.
  (watch && / || short-circuit; for-loop n times = 2^n).
exec(): REPLACES image with new program, SAME PID. success => NEVER returns; -1 on fail.
  family: l=list v=vector args, p=PATH search, e=env. real syscall = execve.
  SHELL = fork + exec + wait.
wait(&st)/waitpid(pid,&st,opt): parent blocks, REAPS child (frees PCB). WNOHANG=nonblock.
  WIFEXITED/WEXITSTATUS decode status.

ZOMBIE = dead child, NOT reaped (PCB lingers) -> parent wait() fixes. loop w/o wait => table full.
ORPHAN = live child, dead parent -> reparented to init(1), which reaps it.
DAEMON = background service, no terminal, child of init, name ends in 'd' (sshd/httpd/crond).

IPC: SHARED MEMORY (fast, direct, YOU synchronize) vs MESSAGE PASSING (kernel copies, isolated,
  works over network). Mechanisms: PIPE(| anon=related, FIFO=unrelated), msg queue, shm, SOCKET, signal.
```

### Flash cards

| Front | Back |
|-------|------|
| Program vs process? | Passive file vs program in execution |
| Per-process OS structure? | PCB (task_struct) |
| fork() in child / parent? | 0 / child PID (−1 on fail) |
| Processes after N forks? | 2ⁿ |
| exec() on success returns? | Never returns (same PID, new program) |
| What does wait() do? | Blocks parent, reaps child (frees PCB) |
| Dead child, not reaped? | Zombie |
| Live child, dead parent? | Orphan (adopted by init) |
| After I/O completes → state? | Ready (not running) |
| Two IPC models? | Shared memory / message passing |
| Why context switch = overhead? | No useful work + cold cache/TLB |
| How fork avoids full copy? | Copy-on-write |

### Spaced repetition
- **24-hour:** recite the state diagram arrows and the fork() return-value rule;
  redo one 2ⁿ fork-count question.
- **7-day:** explain fork/exec/wait as "what a shell does"; zombie vs orphan;
  why a context switch is pure overhead.
- **30-day:** from scratch, draw the process state diagram (with suspended) and the
  memory layout; write a fork/exec/wait skeleton and predict its output.

---

## 4.17 Summary

A **process is a program in execution** — the active, schedulable unit the OS
manages via one **PCB** per process (state, PID, **program counter**, registers,
memory and I/O info). Each process moves through the **state diagram** — **new →
ready → running**, back to **ready** on timeout, to **waiting** on I/O and back to
**ready** when it completes, and finally **terminated** — with **suspended** states
when swapped to disk. Switching the CPU between processes is a **context switch**:
save/restore the PC and registers via the PCB, and it is **pure overhead**. UNIX
builds processes in a **tree** with **`fork()`** (copy the parent — **0 to child,
child-PID to parent**, **2ⁿ** for n forks, cheap via **copy-on-write**),
**`exec()`** (replace the image with a new program, same PID, never returns on
success), and **`wait()`** (reap the child, freeing its PCB). We distinguished
**zombie** (dead child, un-reaped) from **orphan** (live child, dead parent →
adopted by init), met **daemons**, and previewed **IPC** (shared memory vs message
passing, pipes).

Next, **Module 5 — Threads** takes the process apart: multiple threads share one
process's address space to get concurrency **without** the cost of full processes —
which is exactly why the context switch and IPC problems of this module get cheaper,
and why synchronization (M7) becomes essential.

> **You have mastered this module when** you can: draw the process state diagram
> (including suspended) and label every transition; list the PCB fields and what a
> context switch saves; explain `fork`/`exec`/`wait` and predict a fork program's
> output and process count (2ⁿ); contrast zombie vs orphan and say how each is
> handled; and describe shared memory vs message-passing IPC — all without notes.
