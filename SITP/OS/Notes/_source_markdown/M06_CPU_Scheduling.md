---
title: "Module 6 — CPU Scheduling"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — CPU Scheduling

> **Where this module sits.**
> Modules 1–5 built the machinery — the OS, the hardware, **processes and threads**,
> and how they are created. Now comes the question that decides how *fast* and how
> *fair* a system feels: **when several processes are ready, which one gets the CPU
> next, and for how long?** That decision is **CPU scheduling**. This is the single
> most **numerically loaded** module of the whole course — GATE, SEBI IT, RBI IT and
> C-DAC ask you to draw a **Gantt chart** and compute **average waiting and
> turnaround times** almost every year. We build every algorithm from first
> principles, work a full example for each, and finish with **real-time scheduling**
> (EDF, Rate-Monotonic) — the part that separates a good score from a great one.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **Gantt chart + average
waiting / turnaround** for FCFS, SJF, SRTF, Priority, Round Robin; **turnaround =
completion − arrival** and **waiting = turnaround − burst**; **convoy effect**;
**SJF is optimal** for average waiting time; **SRTF is preemptive SJF**; **Round
Robin time-quantum** effect (too small → context-switch overhead, too large → FCFS);
**starvation & aging** in priority scheduling; **preemptive vs non-preemptive**;
**MLFQ rules**; **Rate-Monotonic utilisation bound** `U ≤ n(2^(1/n) − 1)` and **EDF**.

---

## 6.1 The Scheduling Problem — First Principles

### The CPU–I/O burst cycle

A process does not use the CPU continuously. Its life is a **repeating cycle**: a
burst of computation (**CPU burst**), then a wait for input/output (**I/O burst**),
then compute again, and so on until it exits.

![Short CPU bursts dominate; favouring I/O-bound jobs keeps the devices busy while the CPU runs someone else.](images/53_cpu_io_burst_cycle.png)

Real workloads have **many short CPU bursts and a few long ones** (an
exponential-ish distribution). This one fact drives the whole module: if we could
run the **shortest** bursts first, most processes finish quickly and the average
wait plummets — which is exactly what **SJF** does (§6.5).

- **CPU-bound process:** long CPU bursts, few I/O waits (e.g. matrix multiply).
- **I/O-bound process:** short CPU bursts, frequent I/O waits (e.g. a text editor).

> **Memory hook:** the scheduler is a **traffic cop at a single-lane bridge** (the
> CPU). Many cars (processes) wait; the cop decides the order and how long each may
> cross. Every algorithm below is just a different rule the cop uses.

### The CPU scheduler and the dispatcher

- **CPU (short-term) scheduler** — *chooses* which ready process runs next. It runs
  extremely often (milliseconds), so it must be **fast**.
- **Dispatcher** — the module that actually *hands the CPU over*: it performs the
  **context switch**, switches to **user mode**, and jumps to the right instruction
  in the chosen program.
- **Dispatch latency** — the time the dispatcher takes to stop one process and start
  the next. This is **pure overhead** — no useful work happens during it.

![Dispatch latency is the unavoidable overhead of every context switch — keep it small and switch only when it pays off.](images/54_dispatch_latency.png)

> **Exam line:** the **scheduler decides**, the **dispatcher does**. Dispatch latency
> is the cost of the dispatcher's work (context switch + mode switch + jump).

### When does scheduling happen? (the four points)

The short-term scheduler is invoked when a process:

1. switches from **running → waiting** (e.g. issues I/O, `wait()`),
2. switches from **running → ready** (a timer interrupt / preemption),
3. switches from **waiting → ready** (I/O completes),
4. **terminates**.

> **Preemptive vs non-preemptive — the pivotal definition:**
> - If scheduling happens **only** at points **1 and 4** (a process keeps the CPU
>   until it blocks or exits), the scheme is **non-preemptive (cooperative)**.
> - If it can *also* happen at points **2 and 3** (the OS can *forcibly* take the CPU
>   away from a running process), the scheme is **preemptive**.

Preemption gives responsiveness but needs care: if the OS grabs the CPU while a
process is mid-update to shared kernel data, you get **race conditions** (Module 7).

### MCQs

1. What component performs the context switch? → the **dispatcher**.
2. Dispatch latency is? → the **overhead** to stop one process and start another.
3. Non-preemptive scheduling switches only when a process ___ → **blocks or exits**.

---

## 6.2 Scheduling Criteria & Metrics (memorise the formulas)

We judge a scheduling algorithm by five metrics. The first two we want **high**, the
last three we want **low**.

| Metric | Meaning | Want |
|--------|---------|------|
| **CPU utilisation** | fraction of time the CPU is busy | **high** |
| **Throughput** | processes completed per unit time | **high** |
| **Turnaround time** | total time from arrival to completion | **low** |
| **Waiting time** | time spent waiting in the ready queue | **low** |
| **Response time** | arrival → **first** time it gets the CPU | **low** |

**The three formulas you will use in every numerical:**

```text
Turnaround time (TAT) = Completion time − Arrival time
Waiting time   (WT)   = Turnaround time − CPU Burst time
                      = (Completion − Arrival) − Burst
Response time  (RT)   = First-CPU time − Arrival time
```

> **Memory hook:** **TAT is the whole journey** (door to door); **WT is TAT minus the
> time actually spent working**; **RT is only how long until you're first served.**
> For a non-preemptive run of a single burst, `RT = WT`. When a process is preempted
> and resumes later, `RT` (first touch) can be **much smaller** than `WT` (total idle).

**Why response time ≠ waiting time.** In Round Robin a process may get the CPU
quickly (low response time — good for interactivity) yet be preempted repeatedly and
therefore accumulate a large total **waiting** time. Interactive systems optimise
**response time**; batch systems optimise **turnaround/waiting**.

> **Little's Law (backend bonus):** in steady state, `N = λ × W` — average number of
> jobs in the system = arrival rate × average time in system. It links throughput
> (λ) to turnaround (W) and is the queueing-theory backbone of capacity planning.

### MCQs

1. Turnaround time formula? → **completion − arrival**.
2. Waiting time formula? → **turnaround − burst** (= completion − arrival − burst).
3. Response time measures time until? → the **first** CPU allocation.
4. Metric interactive systems care about most? → **response time**.

---

## 6.3 How to Solve Any Scheduling Numerical (the recipe)

Every worked example below follows the same five steps. Learn the recipe once.

```text
1. Draw the GANTT CHART: lay out who runs in each time interval (respect arrivals).
2. Read off COMPLETION time for each process (when its last slice ends).
3. TAT  = Completion − Arrival        (per process)
4. WT   = TAT − Burst                 (per process)
5. AVERAGE the WT and TAT columns (sum ÷ number of processes).
```

> **Tie-break conventions (state them, exams expect these):** when two processes are
> equal on the primary key, break ties by (a) **earlier arrival**, then (b) **lower
> process id**. For Round Robin, a **newly arriving** process is placed in the ready
> queue **before** a process that was just preempted at the same instant (a common
> convention — always state the rule you use).

---

## 6.4 FCFS — First-Come, First-Served

**Rule:** run processes in **order of arrival**. Non-preemptive. Implemented with a
simple **FIFO queue**. Fair in the "first in line" sense, but blind to burst length.

> *Given:* all arrive at t = 0 in the order P1, P2, P3.

| Process | Arrival | Burst |
|:-------:|:-------:|:-----:|
| P1 | 0 | 24 |
| P2 | 0 | 3 |
| P3 | 0 | 3 |

**Gantt chart:**

```text
|      P1       |  P2  |  P3  |
0              24     27     30
```

| Process | Completion | TAT = C−A | WT = TAT−B |
|:-------:|:----------:|:---------:|:----------:|
| P1 | 24 | 24 | 0  |
| P2 | 27 | 27 | 24 |
| P3 | 30 | 30 | 27 |

```text
Average WT  = (0 + 24 + 27) / 3 = 51/3 = 17.0
Average TAT = (24 + 27 + 30) / 3 = 81/3 = 27.0
```

### The convoy effect (why FCFS hurts)

Now reverse the order — **P2, P3, P1** (short jobs first):

```text
|P2|P3|         P1         |
0  3  6                   30
WT: P2=0, P3=3, P1=6  →  Average WT = (0+3+6)/3 = 3.0
```

Same jobs, **average wait fell from 17 to 3** — just by ordering. Under FCFS, one
long CPU-bound job at the front makes all the short jobs behind it wait; the short
jobs "convoy" behind the elephant. This is the **convoy effect**, and it is the
motivation for SJF.

> **Memory hook:** FCFS = **supermarket queue behind the trolley piled high** — you
> only have two items but you still wait. Fair by arrival, terrible for average wait.

### MCQs

1. FCFS is preemptive or non-preemptive? → **non-preemptive**.
2. The problem when a long job arrives first? → **convoy effect**.
3. Data structure behind FCFS? → **FIFO queue**.

---

## 6.5 SJF — Shortest Job First (non-preemptive)

**Rule:** when the CPU is free, pick the ready process with the **shortest next CPU
burst**. Non-preemptive: once chosen, a process runs to the end of its burst.

> **SJF is provably optimal:** it gives the **minimum possible average waiting time**
> for a given set of processes. Moving a shorter job ahead of a longer one always
> reduces total waiting. (Optimal, but only if you *know* the burst lengths.)

> *Given:*

| Process | Arrival | Burst |
|:-------:|:-------:|:-----:|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

**Reasoning:** at t=0 only P1 is present → run P1 to completion (t=7). At t=7 the
ready set is {P2(4), P3(1), P4(4)} → shortest is **P3**. Then {P2(4), P4(4)} tie →
earlier arrival **P2**, then **P4**.

**Gantt chart:**

```text
|      P1       |P3|  P2  |  P4  |
0              7  8      12     16
```

| Process | Arrival | Burst | Completion | TAT | WT |
|:-------:|:-------:|:-----:|:----------:|:---:|:--:|
| P1 | 0 | 7 | 7  | 7  | 0 |
| P2 | 2 | 4 | 12 | 10 | 6 |
| P3 | 4 | 1 | 8  | 4  | 3 |
| P4 | 5 | 4 | 16 | 11 | 7 |

```text
Average WT  = (0 + 6 + 3 + 7) / 4 = 16/4 = 4.0
Average TAT = (7 + 10 + 4 + 11) / 4 = 32/4 = 8.0
```

### The catch: predicting the next burst

You can't know a process's next burst in advance. SJF **estimates** it from history
using an **exponential moving average** (exponential averaging):

```text
τ(n+1) = α · t(n) + (1 − α) · τ(n)
   τ = predicted next burst,  t = actual last burst,  0 ≤ α ≤ 1
   α = 0 → history only (ignore recent);  α = 1 → last burst only.
```

> **Memory hook:** SJF is the **express checkout** ("10 items or fewer") — serve the
> quick ones first and the average wait for *everybody* drops. The snag: you must
> **guess** how full each basket is (burst prediction).

### MCQs

1. SJF is optimal for? → **minimum average waiting time**.
2. The practical obstacle to SJF? → you must **predict the next CPU burst**.
3. Formula to predict the next burst? → **exponential averaging**.

---

## 6.6 SRTF — Shortest Remaining Time First (preemptive SJF)

**Rule:** the preemptive version of SJF. At **every arrival**, compare the new
process's burst against the **remaining time** of the running one; if the newcomer is
shorter, **preempt**. Also called **SRTN**.

We reuse the **exact same table** as SJF so you can see preemption pay off.

> *Given:* P1(arr0, b7), P2(arr2, b4), P3(arr4, b1), P4(arr5, b4).

**Step-by-step:**

```text
t=0 : only P1 → run P1.                       (P1 rem: 7)
t=2 : P2 arrives (4). P1 rem = 5. 4 < 5 → PREEMPT, run P2.
t=4 : P3 arrives (1). P2 rem = 2. 1 < 2 → PREEMPT, run P3.
t=5 : P3 finishes. P4 arrives (4). Ready {P1:5, P2:2, P4:4} → run P2 (2).
t=7 : P2 finishes. Ready {P1:5, P4:4} → run P4 (4).
t=11: P4 finishes. Run P1 (rem 5).
t=16: P1 finishes.
```

**Gantt chart:**

![SRTF re-checks the shortest remaining time at every arrival, so short jobs slip ahead of long ones — giving the minimum average waiting time.](images/55_gantt_srtf.png)

```text
|P1|P2|P3|P2|    P4    |     P1     |
0  2  4  5  7          11           16
```

| Process | Arrival | Burst | Completion | TAT | WT |
|:-------:|:-------:|:-----:|:----------:|:---:|:--:|
| P1 | 0 | 7 | 16 | 16 | 9 |
| P2 | 2 | 4 | 7  | 5  | 1 |
| P3 | 4 | 1 | 5  | 1  | 0 |
| P4 | 5 | 4 | 11 | 6  | 2 |

```text
Average WT  = (9 + 1 + 0 + 2) / 4 = 12/4 = 3.0
Average TAT = (16 + 5 + 1 + 6) / 4 = 28/4 = 7.0
```

> **The payoff (same processes):** SJF gave avg WT **4.0**; SRTF gives **3.0**.
> Preemption lets a freshly-arrived short job jump the queue immediately instead of
> waiting for the current burst to end. SRTF gives the **theoretical minimum average
> waiting time** of any algorithm — at the cost of more context switches and possible
> **starvation** of long jobs.

### MCQs

1. SRTF is the preemptive version of? → **SJF**.
2. When is preemption checked in SRTF? → at **every new arrival** (compare remaining
   times).
3. Which gives the lowest possible average waiting time? → **SRTF**.

---

## 6.7 Priority Scheduling

**Rule:** each process has a **priority number**; the CPU goes to the highest
priority. **Convention (and the usual exam convention): a *lower* number = *higher*
priority.** Can be **non-preemptive** (finish current burst) or **preemptive** (a
higher-priority arrival preempts).

> **SJF is a special case of priority scheduling** where priority = (predicted) next
> CPU burst.

### Non-preemptive priority — worked example

> *Given:* all arrive at t=0. Lower number = higher priority.

| Process | Burst | Priority |
|:-------:|:-----:|:--------:|
| P1 | 10 | 3 |
| P2 | 1  | 1 |
| P3 | 2  | 4 |
| P4 | 1  | 5 |
| P5 | 5  | 2 |

Order by priority (1→5): **P2, P5, P1, P3, P4.**

```text
|P2|  P5  |      P1      |P3|P4|
0  1      6             16 18 19
```

| Process | Burst | Completion | TAT | WT |
|:-------:|:-----:|:----------:|:---:|:--:|
| P2 | 1  | 1  | 1  | 0  |
| P5 | 5  | 6  | 6  | 1  |
| P1 | 10 | 16 | 16 | 6  |
| P3 | 2  | 18 | 18 | 16 |
| P4 | 1  | 19 | 19 | 18 |

```text
Average WT  = (0 + 1 + 6 + 16 + 18) / 5 = 41/5 = 8.2
Average TAT = (1 + 6 + 16 + 18 + 19) / 5 = 60/5 = 12.0
```

### Preemptive priority — worked example

> *Given:* lower number = higher priority.

| Process | Arrival | Burst | Priority |
|:-------:|:-------:|:-----:|:--------:|
| P1 | 0 | 4 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 1 | 3 |

```text
t=0: P1 runs (only one).
t=1: P2 arrives, priority 1 > P1's 2 → PREEMPT, run P2.
t=2: P3 arrives, priority 3 (lower) → keep P2.
t=4: P2 done. Ready {P1 rem3 (pri2), P3 (pri3)} → run P1.
t=7: P1 done. Run P3.
t=8: P3 done.

|P1|  P2  |  P1  |P3|
0  1      4      7  8
```

| Process | Arrival | Burst | Completion | TAT | WT |
|:-------:|:-------:|:-----:|:----------:|:---:|:--:|
| P1 | 0 | 4 | 7 | 7 | 3 |
| P2 | 1 | 3 | 4 | 3 | 0 |
| P3 | 2 | 1 | 8 | 6 | 5 |

```text
Average WT  = (3 + 0 + 5) / 3 = 8/3 ≈ 2.67
Average TAT = (7 + 3 + 6) / 3 = 16/3 ≈ 5.33
```

### Starvation and aging

**Problem — starvation (indefinite blocking):** a steady stream of high-priority
processes can mean a **low-priority process never runs**. (Legend: an IBM 7094 shut
down in 1973 was found to still have a low-priority job submitted in 1967.)

**Solution — aging:** gradually **raise the priority** of a process the longer it
waits. Eventually even the lowest-priority job's priority climbs high enough to run.

> **Memory hook:** **starvation = the polite guest who never gets served**; **aging =
> the maître d' who bumps up anyone who's been waiting too long.**

### MCQs

1. In the usual convention, lower number means? → **higher priority**.
2. The danger of priority scheduling? → **starvation** of low-priority processes.
3. The cure for starvation? → **aging** (raise priority with waiting time).
4. SJF is a special case of priority scheduling with priority = ? → **next CPU
   burst**.

---

## 6.8 Round Robin (RR) — the time-sharing workhorse

**Rule:** FCFS **with preemption** and a fixed **time quantum** (time slice) `q`.
Each process runs for at most `q`; if it isn't finished, it is preempted and sent to
the **back** of the ready queue. Preemptive, **starvation-free**, and the basis of
interactive time-sharing.

> *Given:* q = 4; all arrive at t = 0 in order P1, P2, P3.

| Process | Arrival | Burst |
|:-------:|:-------:|:-----:|
| P1 | 0 | 24 |
| P2 | 0 | 3  |
| P3 | 0 | 3  |

**Gantt chart** (P1 keeps getting re-queued because 24 > q):

```text
|  P1 |P2|P3|  P1 |  P1 |  P1 |  P1 |  P1 |
0     4  7 10    14    18    22    26    30
```

| Process | Burst | Completion | TAT | WT |
|:-------:|:-----:|:----------:|:---:|:--:|
| P1 | 24 | 30 | 30 | 6 |
| P2 | 3  | 7  | 7  | 4 |
| P3 | 3  | 10 | 10 | 7 |

```text
Average WT  = (6 + 4 + 7) / 3 = 17/3 ≈ 5.67
Average TAT = (30 + 7 + 10) / 3 = 47/3 ≈ 15.67
```

> **Key property:** with `n` processes and quantum `q`, **no process waits more than
> `(n−1) × q`** time units for its next turn. That bounded wait is why RR feels
> responsive.

### The effect of the time quantum (the classic trap)

The quantum size trades **responsiveness** against **overhead**:

| Quantum | Behaviour | Problem |
|---------|-----------|---------|
| **too large** (`q ≥ largest burst`) | RR **degenerates into FCFS** | loses responsiveness, convoy effect returns |
| **too small** (`q → 0`) | many tiny slices | **context-switch overhead dominates** (dispatch latency eaten every `q`) |
| **"just right"** | `q` a bit larger than a typical burst | most jobs finish in one slice; low overhead |

**Overhead, quantified.** Suppose a context switch costs `s` time units. Each quantum
of useful work `q` costs an extra `s`, so **CPU efficiency = q / (q + s)**.

```text
If s = 1 and q = 4  → efficiency = 4/5   = 80%  (20% wasted on switching)
If s = 1 and q = 1  → efficiency = 1/2   = 50%  (HALF the CPU lost to overhead!)
If s = 1 and q = 100→ efficiency = 100/101 ≈ 99% (but response time suffers → FCFS-like)
```

> **Rule of thumb (Silberschatz):** a quantum of **10–100 ms** with a context switch
> of ~**10 µs** keeps switching overhead under ~1%, and ~**80% of CPU bursts** should
> be shorter than the quantum. Typical Linux desktop slices are in this range.

> **Memory hook:** RR quantum is a **speed-dating timer**. Too long and it's just one
> long date (FCFS); too short and everyone spends all night swapping seats (context
> switches) instead of talking.

### MCQs

1. RR with a very large quantum behaves like? → **FCFS**.
2. RR with a very small quantum suffers from? → **context-switch overhead**.
3. Max wait for the next turn with n processes, quantum q? → **(n−1)·q**.
4. Is RR starvation-free? → **yes** (every process gets a turn).

---

## 6.9 Multilevel Queue (MLQ) Scheduling

When processes fall into **distinct, fixed classes**, use **several separate ready
queues**, each with its **own scheduling algorithm**, and a rule to pick *between*
queues.

```text
┌──────────────────────────────┐  highest priority
│  System processes    (RR)     │
├──────────────────────────────┤
│  Interactive processes (RR)   │
├──────────────────────────────┤
│  Batch processes    (FCFS)    │  lowest priority
└──────────────────────────────┘
```

- Each queue has a fixed priority; typically a queue is served only if all
  higher-priority queues are **empty** (fixed-priority preemptive), **or** each queue
  gets a **time slice** of the CPU (e.g. 80% to foreground RR, 20% to background
  FCFS).
- **A process is permanently assigned to one queue** — it cannot move. This rigidity
  is the weakness (a batch job stuck low can **starve**), and it's what MLFQ fixes.

### MCQ

1. Key limitation of a plain multilevel queue? → processes **can't move** between
   queues (inflexible, can starve low queues).

---

## 6.10 Multilevel Feedback Queue (MLFQ)

The most **practical, general-purpose** scheduler (the ancestor of Windows/macOS
schedulers). Like MLQ, but a process can **move between queues** based on its
observed behaviour — so it **learns** whether a job is interactive or CPU-bound
*without being told*.

**The MLFQ rules:**

```text
Rule 1: If Priority(A) > Priority(B), A runs.
Rule 2: If Priority(A) = Priority(B), A and B run in ROUND ROBIN.
Rule 3: A new job enters at the TOP (highest) priority queue.
Rule 4: If a job uses its ENTIRE time slice, it DROPS one queue (CPU-bound → lower).
        If it gives up the CPU early (I/O), it STAYS (interactive → high priority).
Rule 5: PRIORITY BOOST — periodically move ALL jobs to the top queue.
        (prevents starvation + adapts if a CPU-bound job turns interactive)
```

- **Top queues get a small quantum** (fast response for interactive jobs), **lower
  queues a larger quantum** (efficient for long CPU-bound jobs).
- **Why it works:** interactive jobs (short bursts, frequent I/O) naturally stay high
  and stay responsive; CPU-bound jobs sink to the bottom where they run in long,
  efficient slices without hurting interactivity. It **approximates SJF** without
  ever knowing burst lengths, and Rule 5 prevents **starvation** and **gaming** (a
  job doing a tiny I/O just before its slice ends to stay high).

> **Memory hook:** MLFQ is a **video-game ranking system** — you start at the top,
> get demoted if you hog the CPU (play too long), and a periodic **season reset**
> (boost) gives everyone another shot.

### MCQ

1. Difference between MLQ and MLFQ? → in **MLFQ processes can move between queues**
   (feedback); MLQ assignment is fixed.
2. What prevents starvation in MLFQ? → periodic **priority boost**.

---

## 6.11 Lottery (Proportional-Share) Scheduling

A **randomised, proportional-share** scheme. Each process holds some **tickets**; the
scheduler holds a **lottery** each slice and the process with the winning ticket
runs. **Expected CPU share = your tickets ÷ total tickets.**

```text
P1 holds 75 tickets, P2 holds 25 tickets  (total 100)
→ over time P1 gets ≈ 75% of the CPU, P2 ≈ 25%.
```

- **Probabilistically fair and starvation-free** — any process with ≥1 ticket will
  *eventually* win. Shares are **proportional and easy to adjust** (give a job more
  tickets to speed it up). **Ticket transfer** lets a client lend tickets to a server
  working on its behalf (fights priority inversion, Module 7).
- **Caveat:** fairness is only guaranteed **over the long run**; short runs can be
  unlucky. **Stride scheduling** is a deterministic variant that removes the
  randomness.

### MCQ

1. In lottery scheduling, a process's CPU share is proportional to its ___ →
   **tickets**.

---

## 6.12 Real-Time Scheduling — EDF and Rate-Monotonic

Real-time systems (Module 1's RTOS) must meet **deadlines**, not just minimise
averages. We model each task by its **period `p`** (how often it recurs), **execution
time `c`** (worst-case CPU burst), and a deadline (usually `= p`). The **CPU
utilisation** of a task is `c/p`, and the whole task set's utilisation is
`U = Σ (c_i / p_i)`.

### Rate-Monotonic Scheduling (RMS)

**Rule:** **static** priorities assigned by rate — a **shorter period = higher
priority** (runs more often). Preemptive. RMS is the **optimal static-priority**
algorithm.

**Schedulability test (sufficient, not necessary):** a set of `n` periodic tasks is
**guaranteed** schedulable by RMS if

```text
U = Σ (c_i / p_i)  ≤  n · (2^(1/n) − 1)
```

The bound shrinks as `n` grows:

```text
n = 1 : 1.000       n = 3 : 0.780
n = 2 : 0.828       n → ∞ : ln 2 ≈ 0.693
```

> **Reading the test:** if `U ≤ bound`, RMS **definitely** works. If `U > bound` (but
> `≤ 1`), RMS *might* still work — the test is only **sufficient**; you must draw the
> schedule to be sure.

**Worked schedulability check (a set that PASSES):**

```text
T1: c=1, p=4   → U1 = 0.250
T2: c=2, p=6   → U2 = 0.333
T3: c=1, p=8   → U3 = 0.125
U = 0.250 + 0.333 + 0.125 = 0.708
Bound (n=3) = 0.780.   0.708 ≤ 0.780  →  SCHEDULABLE by RMS. ✓
```

**Worked case where RMS FAILS but EDF succeeds (the classic Silberschatz example):**

```text
T1: p=50, c=25 → U1 = 0.50
T2: p=80, c=35 → U2 = 0.4375
U = 0.9375  >  bound(n=2)=0.828  → RMS not guaranteed.

Trace RMS (T1 has shorter period → higher priority):
  0–25   T1 (1st)         50–75  T1 (2nd, PREEMPTS T2)
  25–50  T2 runs 25 (rem 10)     75–85  T2 resumes → finishes at 85
  T2's deadline was 80  →  MISSED by 5.  RMS fails.
```

### Earliest-Deadline-First (EDF)

**Rule:** **dynamic** priorities — whichever ready task has the **nearest absolute
deadline** runs next. Preemptive. EDF is the **optimal dynamic-priority** algorithm.

**Schedulability test (necessary AND sufficient):**

```text
A set of periodic tasks is EDF-schedulable  ⇔  U = Σ (c_i / p_i)  ≤  1
```

For the failing RMS set above, `U = 0.9375 ≤ 1`, so **EDF schedules it**:

```text
  0–25  T1 (deadline 50)          At t=50, T2 (deadline 80) is nearer than
  25–50 T2 (deadline 80)          T1's new deadline (100) → T2 keeps running:
  50–60 T2 finishes at 60  ✓ (deadline 80)
  60–85 T1 (2nd) finishes at 85 ✓ (deadline 100)
```

EDF meets both deadlines exactly because it lets the tighter-deadline job go first —
something static RMS priorities cannot do.

| | RMS | EDF |
|---|---|---|
| Priority | **static** (by period) | **dynamic** (by deadline) |
| Utilisation bound | `n(2^(1/n)−1)` (≈0.693 worst) | **1.0** (up to full CPU) |
| Test type | sufficient | necessary + sufficient |
| Overhead | low (fixed priorities) | higher (recompute nearest deadline) |
| On overload | high-rate tasks still meet deadlines | can cascade (domino) misses |

> **Memory hook:** **RMS = seniority** (whoever recurs most often outranks you,
> forever); **EDF = whoever's exam is soonest studies now.** EDF squeezes the CPU to
> 100%; RMS is simpler but caps out near 69% in the worst case.

### MCQs

1. RMS assigns priority by? → **rate** (shorter period = higher priority).
2. EDF assigns priority by? → **earliest (nearest) deadline**.
3. RMS utilisation bound for n tasks? → `n(2^(1/n) − 1)` (→ **ln 2 ≈ 0.693**).
4. EDF is schedulable iff? → `U ≤ 1`.
5. Which can achieve 100% CPU utilisation? → **EDF**.

---

## 6.13 Putting It Together — Comparison & How to Pick

| Algorithm | Preemptive? | Starvation? | Optimises | Overhead | Notes |
|-----------|:-----------:|:-----------:|-----------|:--------:|-------|
| **FCFS** | No | No | — (simple, fair by arrival) | very low | **convoy effect** |
| **SJF** | No | **Yes** (long jobs) | **min avg waiting** | low | needs burst prediction |
| **SRTF** | Yes | **Yes** (long jobs) | **min avg waiting (theoretical)** | medium | preemptive SJF |
| **Priority** | either | **Yes** | meeting importance | low–med | fix with **aging** |
| **Round Robin** | Yes | **No** | response time (fairness) | med–high | tune quantum `q` |
| **MLQ** | usually | **Yes** (low queues) | class separation | med | fixed queues |
| **MLFQ** | Yes | No (with **boost**) | balances all (adaptive) | med–high | approximates SJF |
| **Lottery** | Yes | No | **proportional share** | low | probabilistic fairness |
| **RMS** | Yes | possible (overload) | real-time deadlines (static) | low | bound ≈0.693 |
| **EDF** | Yes | possible (overload) | real-time deadlines (dynamic) | higher | `U ≤ 1` |

![Match the scheduler to what matters: deadlines → EDF/RMS; interactivity → RR/MLFQ; minimum average wait → SJF/SRTF.](images/56_fc_pick_scheduler.png)

**How to pick (decision):**

- **Deadlines are hard** (control, sensors) → **EDF** or **RMS**.
- **Interactive / fairness / general-purpose OS** → **Round Robin** or **MLFQ**.
- **Batch, bursts known, minimise average wait** → **SJF / SRTF**.
- **Simple, batch, order doesn't matter** → **FCFS**.
- **Jobs differ in importance** → **Priority** (add **aging** to avoid starvation).
- **Guaranteed proportional shares** (VMs, containers, cgroups) → **Lottery / stride
  / CFS-style weights**.

---

## 6.14 Real-World & Backend Perspectives

- **Linux CFS (Completely Fair Scheduler).** The default Linux scheduler is not any
  single textbook algorithm — it approximates an **ideal fair share** by tracking
  each task's **virtual runtime (vruntime)** in a **red-black tree** and always
  running the task with the smallest vruntime. **`nice` values** act as weights
  (proportional share, like lottery tickets). (Newer kernels use **EEVDF**, a
  deadline-aware refinement.)
- **Priority inversion (interview favourite).** A high-priority task blocks on a lock
  held by a low-priority task that a medium-priority task keeps preempting — the high
  task is stuck. Real fix: **priority inheritance** (the low task temporarily
  inherits the high priority). This bug famously hit the **Mars Pathfinder** rover
  (1997). Detailed in Module 7.
- **Containers & the cloud.** Kubernetes CPU **requests/limits** and Linux **cgroups
  CPU shares** are proportional-share scheduling (§6.11) at the fleet level — you're
  handing out "tickets" to pods.
- **Thread pools & tail latency.** Backend request schedulers face the same
  SJF-vs-fairness tension: run short requests first for low average latency, but
  bound the wait of long requests to protect **p99 tail latency** — exactly the
  FCFS-vs-SJF-vs-RR trade-off.

---

## 6.15 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**

- Forgetting to **respect arrival times** — a process can't be scheduled before it
  arrives (idle CPU gaps are allowed on the Gantt chart).
- Using `WT = Completion − Burst` — **wrong**; it is `Completion − Arrival − Burst`
  (subtract arrival too).
- Assuming **lower priority number = lower priority** — the standard convention is the
  **opposite** (lower number = *higher* priority). Always state the convention.
- Treating **response time = waiting time** — they differ under preemption.
- Forgetting the RMS bound test is only **sufficient**: `U > bound` does **not** prove
  it's unschedulable — you must draw the timeline.
- In SRTF, forgetting to re-evaluate at **each arrival** (that's the whole point).

**Edge cases**

- **All arrive together** → SJF is just "sort by burst"; FCFS depends on the given
  order.
- **Ties** → break by arrival, then process id (state your rule).
- **Idle CPU** → if no process has arrived yet, the CPU sits idle; the Gantt chart
  shows a gap, and later turnaround still counts from arrival.
- **RR quantum ≥ every burst** → identical to FCFS (verify by tracing).

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Preemption | responsiveness, lower waiting | context-switch overhead, race conditions |
| Small RR quantum | fast response | overhead dominates (efficiency `q/(q+s)`) |
| SJF/SRTF | minimum average wait | starves long jobs; needs prediction |
| Static priority (RMS) | simple, predictable | wastes CPU (≤69% guarantee) |
| Dynamic priority (EDF) | up to 100% CPU | complex; can cascade on overload |

---

## 6.16 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** the bread-and-butter is "given this process table,
draw the Gantt chart and compute average waiting/turnaround time" for FCFS, SJF,
SRTF, Priority, and RR — **practise until it's mechanical.** Also expect one-liners on
convoy effect, SJF optimality, starvation/aging, RR quantum extremes, MLFQ, and the
RMS bound.

**Interview:** "Why is SJF optimal but impractical?" (min avg wait, but you can't
know bursts); "What happens if the RR quantum is too small / too large?"; "How does
Linux schedule?" (CFS / vruntime / fair share); "What is priority inversion and how
do you fix it?" (priority inheritance).

**Coding/practical:**
- `nice` / `renice` set a process's CFS weight; `chrt` sets real-time policies
  (`SCHED_FIFO`, `SCHED_RR`, `SCHED_DEADLINE` = EDF-like) on Linux.
- `sched_setscheduler(2)` / `sched_setaffinity(2)` are the syscalls; `top`/`htop`
  show priorities (`PR`/`NI`).

---

## 6.17 Concept Checks & MCQs (test yourself)

1. Turnaround time formula? → **completion − arrival**.
2. Waiting time formula? → **turnaround − burst** (= completion − arrival − burst).
3. Which algorithm gives the minimum average waiting time (non-preemptive)? → **SJF**.
4. …and preemptively (theoretical minimum)? → **SRTF**.
5. FCFS's classic weakness? → **convoy effect**.
6. Preemptive version of SJF is called? → **SRTF / SRTN**.
7. Component that performs the context switch? → **dispatcher**.
8. Overhead to start the next process? → **dispatch latency**.
9. Cure for starvation in priority scheduling? → **aging**.
10. RR with a huge quantum behaves like? → **FCFS**.
11. RR with a tiny quantum is dominated by? → **context-switch overhead**.
12. Max wait between turns in RR (n procs, quantum q)? → **(n−1)·q**.
13. In MLFQ, what happens to a job that uses its whole slice? → it **drops** a queue.
14. What prevents starvation in MLFQ? → periodic **priority boost**.
15. Lottery scheduling gives CPU proportional to? → **tickets**.
16. RMS priority rule? → **shorter period = higher priority** (static).
17. RMS utilisation bound? → `n(2^(1/n) − 1)` (→ **ln 2 ≈ 0.693**).
18. EDF is schedulable iff? → `U ≤ 1`.
19. Which reaches 100% CPU utilisation for real-time sets? → **EDF**.
20. SJF is a special case of ___ scheduling → **priority** (priority = next burst).
21. Metric interactive systems optimise? → **response time**.
22. Convention for priority numbers? → **lower number = higher priority**.
23. Non-preemptive scheduling reschedules only when a process ___ → **blocks/exits**.
24. Linux default scheduler? → **CFS** (fair share via vruntime).
25. High-priority task stuck behind a lock held by a low one? → **priority inversion**
    (fix: **priority inheritance**).

**True/False**
- SJF is optimal for average waiting time. → **True**.
- RR can cause starvation. → **False** (it's starvation-free).
- FCFS is preemptive. → **False**.
- A larger RR quantum improves response time. → **False** (it worsens it → FCFS).
- EDF uses static priorities. → **False** (dynamic; RMS is static).
- RMS can always schedule any set with U ≤ 1. → **False** (only up to its bound is
  *guaranteed*).
- Response time equals waiting time under preemption. → **False**.

**Numerical (do it yourself):**

> *Given* P1(arr0,b5), P2(arr1,b3), P3(arr2,b1), P4(arr4,b2). Compute the average
> waiting time under **FCFS** and under **SRTF**.
>
> **FCFS** (served in arrival order P1, P2, P3, P4):
> `Gantt: |P1|P2|P3|P4|  boundaries 0,5,8,9,11`
> Completion = 5, 8, 9, 11 → TAT = 5, 7, 7, 7 → WT = 0, 4, 6, 5.
> **Average WT = (0+4+6+5)/4 = 15/4 = 3.75.**
>
> **SRTF** (re-check remaining time at every arrival):
> `t0 run P1; t1 P2(3) < P1(rem4) → run P2; t2 P3(1) < P2(rem2) → run P3;`
> `t3 P3 done, P2(rem2) < P1(rem4) → run P2; t5 P2 done, run P4(2); t7 run P1(rem4).`
> `Gantt: |P1|P2|P3| P2 | P4 |   P1   |  boundaries 0,1,2,3,5,7,11`
> Completion: P3=3, P2=5, P4=7, P1=11 → TAT = 11, 4, 1, 3 → WT = 6, 1, 0, 1.
> **Average WT = (6+1+0+1)/4 = 8/4 = 2.0** — SRTF beats FCFS (2.0 < 3.75), as
> expected.

---

## 6.18 One-Page Revision Sheet

```
FORMULAS (memorise):
  Turnaround (TAT) = Completion − Arrival
  Waiting    (WT)  = TAT − Burst = Completion − Arrival − Burst
  Response   (RT)  = First-CPU-time − Arrival
  RECIPE: Gantt → Completion → TAT=C−A → WT=TAT−B → average.

SCHEDULER decides WHO; DISPATCHER does the switch; DISPATCH LATENCY = that overhead.
PREEMPTIVE (can grab CPU: ready↔run) vs NON-PREEMPTIVE (only on block/exit).

FCFS   FIFO, non-preempt, fair-by-arrival, CONVOY EFFECT (long job first = all wait).
SJF    non-preempt, pick shortest next burst → MIN AVG WAIT (optimal); needs prediction
       (exp avg: τ' = α·t + (1−α)·τ). starves long jobs.
SRTF   preemptive SJF; re-check at EVERY arrival → theoretical MIN avg wait.
PRIORITY  lower number = higher prio; preempt/non-preempt; STARVATION → fix with AGING.
          SJF = priority where priority = next burst.
ROUND ROBIN  FCFS + quantum q; preempt to back of queue; STARVATION-FREE.
   wait ≤ (n−1)·q.  q too big → FCFS;  q too small → context-switch overhead.
   efficiency = q/(q+s).  rule: q=10–100ms, ~80% bursts < q.
MLQ   several fixed queues (system/interactive/batch), each own algo; NO movement.
MLFQ  queues WITH feedback: new→top; use whole slice→drop; I/O early→stay;
      periodic BOOST (anti-starvation). approximates SJF w/o knowing bursts.
LOTTERY  tickets → CPU share = tickets/total; probabilistic, starvation-free.

REAL-TIME (task: period p, exec c, U=Σc/p):
  RMS  static, shorter period = higher prio; guaranteed if U ≤ n(2^(1/n)−1)
       (n=2:0.828, n=3:0.780, ∞:ln2≈0.693). SUFFICIENT test only.
  EDF  dynamic, nearest deadline first; schedulable IFF U ≤ 1 (reaches 100%).
  Classic: p1=50,c=25 & p2=80,c=35 (U=0.9375): RMS MISSES, EDF MEETS.

WORKED AVERAGES (remember the numbers):
  FCFS  P1=24,P2=3,P3=3 all@0 → avgWT 17 (reorder short-first → 3: convoy).
  SJF   (0,7)(2,4)(4,1)(5,4) → avgWT 4.0, avgTAT 8.0.
  SRTF  same table          → avgWT 3.0, avgTAT 7.0.
  RR q=4 (24,3,3)           → avgWT 5.67, avgTAT 15.67.
```

### Flash cards

| Front | Back |
|-------|------|
| Turnaround time? | Completion − Arrival |
| Waiting time? | Turnaround − Burst |
| Optimal for avg waiting? | SJF (preemptively: SRTF) |
| FCFS weakness? | Convoy effect |
| Preemptive SJF? | SRTF |
| Cure for starvation? | Aging |
| RR huge quantum → | FCFS |
| RR tiny quantum → | Context-switch overhead |
| RR max wait for turn? | (n−1)·q |
| MLFQ: uses whole slice → | Drops a queue |
| MLFQ anti-starvation? | Periodic priority boost |
| Lottery share ∝ | Tickets |
| RMS priority by? | Shortest period (static) |
| RMS bound? | n(2^(1/n)−1) → ln2≈0.693 |
| EDF schedulable iff? | U ≤ 1 |
| Linux default scheduler? | CFS (vruntime fair share) |

### Spaced repetition
- **24-hour:** redo the FCFS, SJF, SRTF and RR(q=4) numericals from a blank page —
  Gantt + average WT/TAT — until fully mechanical.
- **7-day:** explain convoy effect, SJF optimality + prediction, RR quantum
  trade-off, starvation/aging, and MLFQ's five rules from memory.
- **30-day:** state and apply the RMS bound and the EDF test; reproduce the
  RMS-fails/EDF-succeeds example; fill the comparison table (preemptive? starvation?
  optimises? overhead) from scratch.

---

## 6.19 Summary

CPU scheduling answers the central performance question of an OS: **when many
processes are ready, who runs next, and for how long?** Every process alternates
**CPU and I/O bursts**; the **short-term scheduler** picks a ready process and the
**dispatcher** switches to it, paying **dispatch latency**. We measure success with
**CPU utilisation, throughput, turnaround (= completion − arrival), waiting (=
turnaround − burst), and response time**, and we compute them via one recipe: **Gantt
chart → completion → TAT → WT → average.**

We worked every classic algorithm end-to-end: **FCFS** (simple but the **convoy
effect**), **SJF** (**optimal average waiting**, but needs burst prediction),
**SRTF** (preemptive SJF, the theoretical minimum), **Priority** (importance-driven,
cured of **starvation** by **aging**), **Round Robin** (interactive, starvation-free,
with the crucial **quantum** trade-off — too small wastes CPU on switching, too large
becomes FCFS), and the practical hierarchies **MLQ** and **MLFQ** plus
proportional-share **Lottery**. Finally, **real-time scheduling** gave us **RMS**
(static, shorter-period-first, bound `U ≤ n(2^(1/n)−1)`) and **EDF** (dynamic,
nearest-deadline-first, schedulable up to `U ≤ 1`), and the classic set where **RMS
misses a deadline but EDF meets it**.

Next, **Module 7 — Process Synchronization** tackles what happens when those
scheduled, preempted processes touch **shared data** at the same time: race
conditions, critical sections, locks, semaphores, and the deadlocks that scheduling
choices can create.

> **You have mastered this module when** you can: from a raw process table draw the
> Gantt chart and compute average waiting/turnaround for FCFS, SJF, SRTF, Priority,
> and RR without hesitation; explain convoy effect, SJF optimality, starvation/aging,
> and the RR quantum trade-off in one sentence each; recite the MLFQ rules; and apply
> both the RMS utilisation bound and the EDF `U ≤ 1` test — all without notes.
