---
title: "Module 1 — Introduction to Operating Systems"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Introduction to Operating Systems

> **Where this module sits.**
> This is the front door to the whole subject. Before we can talk about processes,
> memory, or file systems, we need one clear picture: **what an operating system
> actually is, why it exists, and the different shapes it takes** (from the batch
> systems of the 1950s to today's cloud hypervisors). Everything later in the
> course — scheduling (M6), synchronization (M7), memory (M9), Linux internals
> (M14) — is just a *detailed answer* to the question this module raises: **how
> does one piece of software share a computer fairly, safely, and fast?**

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★      | ★★        | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** definition & goals of an
OS; the OS as **resource manager** vs **extended (virtual) machine**;
**multiprogramming vs multitasking vs multiprocessing** (the classic confusion);
**time-sharing** and the idea of a time quantum; **real-time OS** (hard vs soft)
and **which scheduling** they use; **types of OS** one-liners; **spooling** and
**buffering**; **hypervisor type-1 vs type-2** (bare-metal vs hosted).

---

## 1.1 What Is an Operating System? (first principles)

### Definition

An **operating system (OS)** is the master program that sits between your
**hardware** and your **applications**. It has two jobs, and every OS topic is one
of these two in disguise:

1. **Resource manager** — it shares the CPU, memory, disk, and devices among many
   competing programs, fairly and efficiently.
2. **Extended machine (abstraction layer)** — it hides ugly hardware details behind
   clean, easy interfaces (you write `open("file.txt")`, not "move disk arm to
   cylinder 4021, sector 12").

![The OS is the layer between raw hardware and user programs; apps reach it only through system calls.](images/01_os_position.png)

> **Memory hook:** an OS is a **hotel manager**. Guests (programs) never go into the
> boiler room (hardware); they call the front desk (**system calls**), and the
> manager allocates rooms (memory), staff time (CPU), and services (I/O) so nobody
> fights and everybody thinks they have the place to themselves.

### The two classic viewpoints (a favourite exam line)

- **Top-down (user view):** the OS is a **convenience** layer — it makes the machine
  easy and pleasant to use.
- **Bottom-up (system view):** the OS is a **resource allocator and control
  program** — it decides who gets what, and prevents programs from harming each
  other.

### MCQs

1. Two core roles of an OS? → **resource manager** and **extended/virtual machine**.
2. How does an application ask the OS for a service? → via a **system call**.
3. The OS component always resident in memory is called the? → **kernel**.

---

## 1.2 Why Operating Systems Exist — The Problem They Solve

Imagine a computer with **no OS**. Every program would have to:

- talk to the disk controller and mouse directly (thousands of lines of
  device-specific code in *every* app),
- make sure it doesn't overwrite another program's memory,
- decide by itself when to give the CPU to someone else.

This is impossible to scale. The OS exists to solve four hard problems at once:

| Problem | Without an OS | The OS's answer |
|---|---|---|
| **Hardware is complex** | every app re-writes device code | **abstraction** (files, sockets, drivers) |
| **Resources are shared** | programs fight for CPU/RAM | **scheduling + allocation** |
| **Programs can misbehave** | one crash takes down all | **protection & isolation** (user/kernel mode) |
| **The CPU is fast, I/O is slow** | CPU idles waiting on disk | **multiprogramming** (run another job meanwhile) |

> **Memory hook:** the single idea driving OS history is **"never let the fast CPU
> sit idle."** Every type of OS below is another trick to keep the CPU busy.

### MCQs

1. Why do we need protection between programs? → so one **crash/bug** can't corrupt
   others (**isolation**).
2. The mismatch that motivates multiprogramming? → **CPU fast, I/O slow**.

---

## 1.3 A Short History (how we got here)

![Each generation of OS was invented to stop the fast CPU from waiting on slow I/O.](images/02_os_evolution.png)

- **1940s — no OS.** Programs entered by switches/plugboards. The programmer *was*
  the operator.
- **1950s — batch systems.** Jobs on punched cards were collected into a **batch**
  and run one after another by a resident **monitor**. Still one job at a time; the
  CPU idled during I/O.
- **1960s — multiprogramming.** Keep **several jobs in memory**; when one waits for
  I/O, the CPU switches to another. CPU utilisation jumps.
- **1960s–70s — time-sharing (multitasking).** Give each user a tiny **time slice**
  so many users at terminals feel like they each have the machine (CTSS, MULTICS,
  then **UNIX**, 1969).
- **1980s — personal computers.** MS-DOS, early Windows, Mac OS — one user, GUIs.
- **1990s–2000s — networked & multiprocessor.** Windows NT, **Linux** (1991), SMP.
- **2010s–now — mobile & cloud.** Android/iOS on phones; **virtual machines,
  containers, and hypervisors** run thousands of isolated OSes in data centres.

### MCQs

1. First OS to popularise time-sharing lineage → **MULTICS → UNIX**.
2. Year Linux was released? → **1991** (by Linus Torvalds).

---

## 1.4 Goals of an Operating System

An OS is designed to balance several goals — some for the user, some for the system:

- **Convenience / usability** — easy to use (GUI, simple APIs).
- **Efficiency** — high **throughput** and **resource utilisation** (keep CPU, RAM,
  disk busy with useful work).
- **Fairness** — no program is starved of resources.
- **Reliability & robustness** — survive faulty programs; recover from errors.
- **Protection & security** — isolate programs and users; enforce permissions.
- **Scalability** — work from a smartwatch to a 128-core server.

These goals often **conflict** (e.g. maximum throughput vs. fair response time),
and the "right" OS is the one that strikes the balance its workload needs — a theme
you'll see again in **CPU scheduling (M6)**.

### MCQs

1. "Amount of useful work done per unit time" is called? → **throughput**.
2. Name a pair of goals that conflict. → **throughput vs. fairness/response time**.

---

## 1.5 Types of Operating Systems

This is the highest-yield section for objective exams. Learn each type by its
**one-line purpose** and a **real example**.

### 1.5.1 Batch OS
Jobs with similar needs are grouped and run **without user interaction**; a resident
monitor loads the next job automatically.
- **Pro:** high throughput for bulk work. **Con:** no interactivity; hard to debug;
  CPU still idles on I/O (unless multiprogrammed).
- **Example:** old mainframe payroll runs. **Key terms:** *spooling*, *job control*.

### 1.5.2 Multiprogramming OS
Keeps **multiple jobs in memory**; when the running job blocks on I/O, the CPU is
handed to another ready job. **Goal: maximise CPU utilisation.**

### 1.5.3 Multitasking / Time-Sharing OS
An extension of multiprogramming where the CPU switches so **rapidly** (each job a
small **time quantum**) that **multiple users/programs appear simultaneous**.
- **Goal: minimise response time.** **Example:** UNIX/Linux, Windows.

### 1.5.4 Multiprocessing OS
Uses **two or more CPUs/cores** for **true parallel** execution.
- **SMP (symmetric):** all CPUs are peers sharing one OS + memory (today's norm).
- **AMP (asymmetric):** a master CPU controls the others.

> **The #1 exam trap — say it out loud:**
> **Multiprogramming** = many jobs in memory, **one CPU** switches on I/O wait.
> **Multitasking** = multiprogramming + **rapid time slices** for interactivity.
> **Multiprocessing** = **many CPUs** running truly in parallel.

### 1.5.5 Real-Time OS (RTOS)
Correctness depends on **meeting deadlines**, not just the answer.
- **Hard RTOS:** missing a deadline = system failure (airbag, pacemaker, flight
  control). **Soft RTOS:** deadlines are important but occasional misses are
  tolerable (video streaming, VoIP).
- Uses **priority-based / EDF / rate-monotonic** scheduling (see M6). **Examples:**
  VxWorks, FreeRTOS, QNX.

### 1.5.6 Distributed OS
Manages a **network of independent computers** so they appear as **one system**;
resources and computation are shared across nodes.
- **Pro:** resource sharing, speed, reliability. **Con:** complexity, network
  dependence. **Example:** cluster/grid systems (concepts carry into **M18 cloud**).

### 1.5.7 Embedded OS
A small, dedicated OS inside an appliance with tight memory/power limits (router,
microwave, car ECU). Often *is* an RTOS. **Examples:** FreeRTOS, embedded Linux.

### 1.5.8 Mobile OS
Optimised for touch, battery, connectivity, and app sandboxing. **Examples:**
**Android** (Linux-based), **iOS** (Darwin/BSD-based).

### 1.5.9 Cloud / Network OS
Manages pooled data-centre resources and virtual machines; users rent compute on
demand. Built on **virtualization** (M17) and studied further in **M18**.

### MCQs

1. Goal of multiprogramming vs time-sharing? → **CPU utilisation** vs **response
   time**.
2. Hard vs soft real-time difference? → a **missed deadline = failure** (hard) vs
   **tolerable** (soft).
3. Android's kernel is based on? → **Linux**.
4. True parallel execution needs? → **multiprocessing (multiple CPUs/cores)**.

---

## 1.6 Spooling and Buffering (small terms, big in MCQs)

- **Buffering:** overlap I/O with computation using a memory **buffer** — while the
  CPU processes block *n*, the device reads block *n+1*.
- **Spooling** (*Simultaneous Peripheral Operation On-Line*): use the **disk** as a
  giant buffer for a slow device. The classic case is the **printer queue** — many
  jobs spool to disk and print one by one, so the CPU never waits for the printer.

> **Memory hook:** **buffer = small waiting room (RAM); spool = big waiting hall on
> disk** (printer queue is the textbook example).

### MCQs

1. Printer queue is an example of? → **spooling**.
2. Buffering overlaps? → **I/O with CPU computation**.

---

## 1.7 Bare-Metal vs Hosted, and Hypervisors (a modern must-know)

A **hypervisor** (Virtual Machine Monitor) lets one physical machine run **many
guest OSes** at once, each believing it owns the hardware.

- **Type-1 (bare-metal):** the hypervisor runs **directly on hardware**; guest OSes
  run on top. Fast, secure, used in data centres. **Examples:** VMware ESXi,
  Microsoft Hyper-V, Xen, KVM.
- **Type-2 (hosted):** the hypervisor runs **as an app inside a host OS**. Easy for
  desktops/testing, a bit slower. **Examples:** VirtualBox, VMware Workstation.

| | Type-1 (bare-metal) | Type-2 (hosted) |
|---|---|---|
| Runs on | hardware directly | on top of a host OS |
| Speed | faster | slower (extra layer) |
| Use | servers, cloud | desktops, testing |

This is the foundation for **virtualization (M17)** and **cloud OS (M18)**;
containers (Docker) are a lighter-weight cousin covered there.

### MCQs

1. Type-1 vs Type-2 hypervisor? → runs on **hardware directly** vs **inside a host
   OS**.
2. Give a Type-1 example. → **ESXi / Hyper-V / Xen / KVM**.

---

## 1.8 Real-World & Backend Perspectives

- **Every backend server** you deploy runs on Linux; understanding the OS's job
  (processes, scheduling, memory, I/O) is what separates "it works on my machine"
  from "it scales to a million users."
- **Cloud (AWS/GCP/Azure)** is hypervisors + schedulers at planetary scale — a VM is
  literally a guest OS on a Type-1 hypervisor; a container shares the host kernel.
- **AI infra** (M19) is an OS story too: GPUs are devices the OS/driver schedules,
  and LLM serving is bottlenecked by memory and I/O management.

---

## 1.9 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** conflating **multiprogramming / multitasking / multiprocessing** —
  see §1.5's out-loud rule.
- **Mistake:** thinking an RTOS is "fast." An RTOS is **predictable** (deterministic
  deadlines), not necessarily high-throughput.
- **Edge case:** more programs in memory ≠ always faster — beyond a point you get
  **thrashing** (M9) as memory pressure dominates.
- **Tradeoff:** convenience vs control — a GUI OS is friendly; a server runs
  headless for efficiency and security.

---

## 1.10 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** expect 1–2 conceptual MCQs — definition/goals, type
  one-liners, spooling, hypervisor types, the multiprogramming/multitasking trap.
- **GATE:** M1 itself is light, but the *vocabulary* (throughput, response time,
  time quantum, SMP) recurs in the numerical modules (M6, M9).
- **Interview:** "What does an operating system actually do?" — answer with the
  **two roles** (resource manager + abstraction) and one example each.

---

## 1.11 Concept Checks & MCQs (test yourself)

1. Define an OS in one sentence. → software that **manages hardware resources** and
   provides an **abstraction** for programs.
2. Difference between multiprogramming and multitasking? → time-sharing adds
   **rapid time slices** for interactivity.
3. What is a time quantum? → the small **fixed CPU slice** each job gets in
   time-sharing/Round Robin.
4. Hard vs soft real-time? → **deadline miss = failure** vs **tolerable**.
5. Spooling vs buffering? → **disk** as buffer for a slow device (printer) vs **RAM**
   overlap of I/O and CPU.
6. Type-1 vs Type-2 hypervisor? → **bare-metal** vs **hosted**.
7. SMP means? → **symmetric multiprocessing**: peer CPUs share one OS + memory.
8. The always-resident core of the OS? → the **kernel**.

---

## 1.12 One-Page Revision Sheet

```
OS = (1) RESOURCE MANAGER (share CPU/RAM/disk/IO) + (2) EXTENDED MACHINE (hide hardware).
  App -> SYSTEM CALL -> kernel -> hardware. Kernel = always-resident core.
  Driving idea of all OS history: never let the fast CPU sit idle.

VIEWS: user=convenience ; system=resource allocator/control program.

HISTORY: no-OS -> BATCH(1 job, monitor) -> MULTIPROGRAMMING(many in RAM, switch on IO)
  -> TIME-SHARING(slices, interactive; UNIX 1969) -> PC(GUI) -> networked/SMP(Linux 1991)
  -> mobile/cloud(VMs, containers).

TYPES:
  Batch          group jobs, no interaction (spooling)
  Multiprogramming  many jobs in RAM, 1 CPU switches on IO  -> maximise CPU util
  Multitasking/Time-sharing  rapid quanta, interactive      -> minimise response time
  Multiprocessing   many CPUs, TRUE parallel (SMP=peers / AMP=master-slave)
  Real-time (RTOS)  meet DEADLINES; hard(fail) vs soft(tolerable); EDF/RMS; VxWorks/FreeRTOS
  Distributed    many nodes look like one system
  Embedded       tiny, dedicated (router/car); often RTOS
  Mobile         Android(Linux)/iOS(BSD); touch+battery+sandbox
  Cloud/Network  pooled DC resources, VMs on demand

TRAP: multiprogramming(many jobs,1 CPU) vs multitasking(+slices) vs multiprocessing(many CPUs).

SPOOLING = disk as buffer for slow device (PRINTER queue). BUFFERING = RAM overlap IO & CPU.

HYPERVISOR: Type-1 BARE-METAL on hardware (ESXi/Hyper-V/Xen/KVM, fast, cloud)
            Type-2 HOSTED inside host OS (VirtualBox/VMware WS, easy, slower).
```

### Flash cards

| Front | Back |
|-------|------|
| Two roles of an OS? | Resource manager + extended (virtual) machine |
| Doorway from app to OS? | System call |
| Multiprogramming goal? | Maximise CPU utilisation |
| Time-sharing goal? | Minimise response time |
| Many CPUs, true parallel? | Multiprocessing (SMP/AMP) |
| Hard vs soft RTOS? | Deadline miss = failure vs tolerable |
| Printer queue mechanism? | Spooling |
| Type-1 hypervisor? | Bare-metal (runs on hardware) |
| Android kernel? | Linux |
| Always-resident OS core? | Kernel |

### Spaced repetition
- **24-hour:** recite the type one-liners and the multiprogramming/multitasking/
  multiprocessing trap.
- **7-day:** explain the two OS roles with examples; hard vs soft RTOS; spooling vs
  buffering.
- **30-day:** given a device/scenario (phone, airbag, data centre, mainframe batch),
  name the OS type and justify it.

---

## 1.13 Summary

An operating system is the **master resource manager and hardware abstraction**
layer: apps ask for services through **system calls**, and the **kernel** shares the
CPU, memory, disk, and devices safely and efficiently. Its whole history is one
long campaign to **keep the fast CPU from idling** — from **batch** to
**multiprogramming** (many jobs in RAM), to **time-sharing** (rapid slices for
interactivity), to **multiprocessing** (many CPUs in parallel), and on to today's
**mobile and cloud** systems built on **hypervisors**. We separated the confusing
trio (multiprogramming vs multitasking vs multiprocessing), met **real-time,
distributed, embedded, and mobile** OSes, and learned the small-but-tested terms
**spooling** and **buffering** plus **Type-1 vs Type-2** hypervisors.

Next, **Module 2 — Computer Hardware Foundations** goes one layer down to the CPU,
registers, interrupts, and memory hierarchy the OS is built to manage — the
hardware vocabulary that makes every later module click.

> **You have mastered this module when** you can: state the two roles of an OS with
> examples; walk the history as a series of "keep the CPU busy" steps; instantly
> separate multiprogramming / multitasking / multiprocessing; classify any device
> into an OS type; and explain spooling, buffering, and Type-1 vs Type-2
> hypervisors — all without notes.
