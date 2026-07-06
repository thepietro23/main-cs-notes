---
title: "Module 2 — Computer Hardware Foundations"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — Computer Hardware Foundations

> **Where this module sits.**
> Module 1 said the OS is a **resource manager** — but you cannot manage what you
> do not understand. This module is the **hardware the OS manages**: the **CPU**
> (its registers, ALU, control unit, and fetch–decode–execute heartbeat), the
> **interrupt** mechanism that lets slow devices grab the CPU's attention, the
> **memory hierarchy** (registers → cache → RAM → disk), and the helpers —
> **timers, MMU, DMA, PCIe, NUMA, multi-core**. Almost every later chapter is the
> OS *reacting to* something here: scheduling is triggered by a **timer
> interrupt** (M6), context switches save **registers** (M4), virtual memory is
> the **MMU** doing address translation (M9), and device drivers ride **interrupts
> and DMA** (M13). Get this vocabulary solid and every later module clicks.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★     | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** the **fetch–decode–execute**
cycle; **register** roles (**PC, IR, MAR, MBR, ACC, SP**); **interrupts** — types,
the **interrupt cycle**, **vectored vs polled**, and **trap vs interrupt** (very
high yield); the **memory hierarchy** with speeds/sizes; **RAM vs ROM** (volatile
vs non-volatile); **cache** — levels, **locality** (temporal/spatial), hit/miss,
mapping; **MMU** (logical → physical); **DMA** (why it frees the CPU, **cycle
stealing**); **PCIe**, **NUMA**, and **multi-core**.

---

## 2.1 The CPU — Architecture From First Principles

Everything a computer does is the **CPU (Central Processing Unit)** repeatedly
doing one tiny thing: **fetch an instruction, understand it, do it.** To do that,
the CPU has three parts and a set of small, blazing-fast memories called
**registers**.

![Inside the CPU: the control unit orchestrates the ALU and registers; the CPU talks to memory over the address bus (MAR) and data bus (MBR).](images/13_cpu_architecture.png)

- **ALU (Arithmetic Logic Unit)** — the calculator. It does arithmetic (`+ − × ÷`)
  and logic (`AND, OR, NOT, compare, shift`). It sets **flags** (zero, carry, sign,
  overflow) that the control unit uses to make decisions (branches).
- **Control Unit (CU)** — the conductor. It reads each instruction, then sends the
  right control signals to the ALU, registers, and memory so the instruction
  happens in the right order. It is the CU that drives the fetch–decode–execute
  cycle.
- **Registers** — a handful of tiny storage cells *inside* the CPU (each a few
  bytes), the **fastest memory that exists** (~1 CPU cycle, sub-nanosecond).

> **Memory hook:** the CPU is a **tiny kitchen**. The **CU is the chef** reading
> the recipe, the **ALU is the stove** doing the cooking, and **registers are the
> countertop** — the only surface small enough and close enough to work on right
> now. Everything else (RAM, disk) is the pantry down the hall.

### MCQs

1. Which unit performs arithmetic and comparisons? → the **ALU**.
2. Which unit issues control signals and sequences an instruction? → the **control
   unit**.
3. The fastest storage in a computer? → **CPU registers**.

---

## 2.2 Registers — The CPU's Working Memory

Registers are worth memorising **by role**, because context switching (M4) is
literally "save all the registers of process A, load all of process B", and
because register names are classic one-mark questions.

| Register | Full name | Job |
|----------|-----------|-----|
| **PC** | Program Counter | holds the **address of the *next* instruction** to fetch |
| **IR** | Instruction Register | holds the **instruction currently being executed** |
| **MAR** | Memory Address Register | holds the **address** to read/write in memory |
| **MBR / MDR** | Memory Buffer (Data) Register | holds the **data** going to/from memory |
| **ACC** | Accumulator | holds an ALU **operand / result** (in simple CPUs) |
| **SP** | Stack Pointer | points to the **top of the stack** (calls, locals) |
| **General-purpose** | e.g. `R0–R31`, `RAX/RBX…` | hold operands, addresses, temporaries |
| **PSW / FLAGS** | Program Status Word | condition flags + mode bit + interrupt state |

> **The PC vs IR trap (say it out loud):** the **PC points to the *next*
> instruction; the IR holds the *current* one.** The very first thing "fetch" does
> is copy the instruction PC points at into the IR, then **increment the PC**.

> **MAR vs MBR:** think of posting a letter. The **MAR is the address on the
> envelope** (*where* in memory); the **MBR is the letter inside** (*what* data).
> The MAR is wired to the **address bus**, the MBR to the **data bus**.

> **Memory hook:** **"PC next, IR now; MAR where, MBR what; SP top, ACC math."**

### MCQs

1. Which register holds the address of the *next* instruction? → **PC**.
2. Which holds the instruction being executed? → **IR**.
3. Data being transferred to/from memory sits in? → **MBR/MDR**.
4. Top of the stack is tracked by? → **SP** (stack pointer).

---

## 2.3 The Fetch–Decode–Execute Cycle (the machine's heartbeat)

This single loop, repeated billions of times a second, *is* computation. It is a
guaranteed exam favourite — learn it as a fixed micro-sequence.

```text
LOOP forever (the instruction / machine cycle):
  1. FETCH
       MAR <- PC              ; put next-instruction address on the address bus
       MBR <- Memory[MAR]     ; read that instruction from memory
       IR  <- MBR             ; move it into the instruction register
       PC  <- PC + 1          ; advance to the following instruction
  2. DECODE
       Control Unit interprets the opcode in IR (what to do, which operands)
  3. EXECUTE
       ALU / memory / I/O carry out the operation; results go to a register
  4. (INTERRUPT CHECK)
       if an interrupt is pending -> service it before the next fetch
```

- **Fetch** — bring the next instruction from memory into the IR (using PC → MAR →
  MBR → IR), and bump the PC.
- **Decode** — the CU works out the **opcode** and where the **operands** are.
- **Execute** — the ALU (or a memory/I-O step) actually performs the operation.
- **Interrupt check** — after each instruction the CPU checks for a pending
  interrupt (see §2.4); this is the hook the OS uses to regain control.

> **Memory hook:** **"Fetch → Decode → Execute → (check interrupts) → repeat."**
> The interrupt check at the loop's end is *why* an OS is possible at all: without
> it, a running program would never give the CPU back.

### Worked micro-trace (one instruction: `ADD R1, R2`)

```text
State before: PC = 100, R1 = 5, R2 = 3
FETCH:   MAR<-100 ; MBR<-Mem[100]="ADD R1,R2" ; IR<-MBR ; PC<-101
DECODE:  opcode=ADD, operands = R1 and R2
EXECUTE: ALU computes 5 + 3 = 8 ; R1 <- 8   (zero flag=0)
State after:  PC = 101, R1 = 8
```

### MCQs

1. Correct order of the machine cycle? → **fetch → decode → execute**.
2. During fetch the PC is copied into which register? → **MAR** (then incremented).
3. When does the CPU check for interrupts? → **at the end of each instruction
   cycle**.

---

## 2.4 Interrupts — How Hardware Grabs the CPU (high-yield)

The CPU is fast; devices are slow. Rather than the CPU **polling** ("keyboard, any
key? disk, done yet?") and wasting cycles, a device raises an **interrupt** — an
electrical signal that says *"stop what you're doing, I need attention."* This is
the single most important hardware idea for an OS: **every timer tick, keypress,
disk completion, and system call reaches the kernel as an interrupt/trap.**

### 2.4.1 Types of interrupts

| Category | Source | Synchronous? | Example |
|----------|--------|:------------:|---------|
| **Hardware interrupt** | external device (I/O, timer) | **async** | disk finished, key pressed, timer tick |
| **Software interrupt / trap** | a running instruction | **sync** | `int 0x80` / `syscall` — a **system call** |
| **Exception / fault** | error in current instruction | **sync** | divide-by-zero, page fault, invalid opcode |

> **Trap vs interrupt — the classic exam line.**
> An **interrupt** is **asynchronous** and **external** (hardware, unrelated to the
> current instruction — e.g. the disk finishing). A **trap** (a.k.a. software
> interrupt or exception) is **synchronous** and **internal** — deliberately or
> accidentally *caused by the currently executing instruction* (a system call, a
> divide-by-zero, a page fault). **Same handling machinery, different trigger.**

> **Memory hook:** **interrupt = "someone knocked at the door" (external, async);
> trap = "I tripped over my own feet" (internal, sync).**

### 2.4.2 The interrupt cycle (what the CPU/OS actually does)

![The interrupt cycle: finish the current instruction, save state, look up the ISR via the interrupt vector table, run the handler, restore state, resume.](images/14_interrupt_cycle.png)

```text
1. Device raises an interrupt request (IRQ) on the interrupt line.
2. CPU FINISHES the current instruction (never mid-instruction).
3. CPU SAVES context: PC + PSW (and enough registers) pushed to the stack.
4. CPU switches to KERNEL MODE and disables further interrupts (or masks lower ones).
5. It reads the interrupt NUMBER, indexes the INTERRUPT VECTOR TABLE, and
   jumps to that Interrupt Service Routine (ISR / handler).
6. ISR services the device (e.g. copies the disk block, acknowledges the device).
7. RESTORE the saved context (PC, PSW, registers).
8. Return-from-interrupt (IRET): re-enable interrupts, resume the interrupted program.
```

The interrupted program never knows it was paused — the OS restored its exact
state. **This save/restore is the seed of the context switch (M4).**

### 2.4.3 Vectored vs polled interrupts

- **Vectored interrupts:** the device supplies (directly or via the controller) an
  **interrupt number**; the CPU uses it to index the **interrupt vector table** and
  jump **straight to the right ISR**. **Fast** — no searching.
- **Polled (non-vectored) interrupts:** a **single, common** handler runs and then
  **asks each device in turn** "was it you?" **Simpler hardware, slower** (linear
  search); order of polling sets priority.

> **Memory hook:** **vectored = the caller says which extension to ring (direct
> dial); polled = the operator rings every desk asking "did you call?"**

> **Interrupt-driven I/O vs polling/busy-wait:** *polling I/O* (the CPU loops
> reading a status bit) wastes CPU; *interrupt-driven I/O* lets the CPU work on
> something else and be notified on completion. Don't confuse **polled
> *interrupts*** (§2.4.3, how the ISR is located) with **polling *I/O*** (how the
> CPU learns a device is ready) — different questions.

### MCQs

1. Trap vs interrupt? → trap = **synchronous/internal** (caused by the instruction);
   interrupt = **asynchronous/external** (hardware).
2. A **system call** reaches the kernel as a? → **software interrupt / trap**.
3. Vectored vs polled interrupt? → **index a vector table (direct)** vs **one handler
   that polls each device**.
4. Divide-by-zero is a? → **trap / exception** (synchronous).
5. When is a running instruction interrupted? → **after it finishes**, at the
   interrupt check.

---

## 2.5 The System Timer / Clock

A **programmable timer** (e.g. the PIT/APIC timer) is a device that raises a
**timer interrupt** at a fixed interval (a "tick", or in modern **tickless**
kernels, on demand). It is small but foundational:

- **Preemptive scheduling (M6):** each timer tick lets the OS check whether the
  current process has used its **time quantum** and, if so, **preempt** it. Without
  a timer interrupt, a CPU-bound program could run forever — no time-sharing.
- **Timekeeping:** counting ticks maintains the system clock, timeouts, and `sleep`.
- **Watchdogs:** detect a hung system and reset it.

> **Memory hook:** the timer interrupt is the OS's **heartbeat / alarm clock** — it
> is *how the kernel guarantees it periodically gets the CPU back* to make
> scheduling decisions.

### MCQs

1. Which hardware makes **preemptive** scheduling possible? → the **timer/clock**.
2. A CPU-bound loop is still preempted because of? → the **timer interrupt**.

---

## 2.6 The Memory Hierarchy — Speed vs Size vs Cost

There is no single memory that is fast, big, and cheap — so computers **layer**
them. Each level is faster and smaller than the one below, and the hardware/OS
tries to keep the **data you need soon** near the top.

![The memory hierarchy pyramid: registers → cache → RAM (volatile) → SSD → disk → tape (non-volatile); faster, smaller, costlier at the top.](images/15_memory_hierarchy.png)

| Level | Typical speed | Typical size | Volatile? | Managed by |
|-------|--------------|--------------|-----------|-----------|
| **Registers** | ~0.3–1 ns (1 cycle) | < 1 KB | yes | compiler / CPU |
| **L1 cache** | ~1 ns | 32–64 KB | yes | hardware |
| **L2 cache** | ~3–10 ns | 256 KB–1 MB | yes | hardware |
| **L3 cache** | ~10–20 ns | 2–64 MB | yes | hardware |
| **Main memory (RAM)** | ~50–100 ns | GBs | **yes (volatile)** | OS (virtual memory) |
| **SSD (flash)** | ~50–100 µs | 100s GB–TBs | no | OS / device |
| **Magnetic disk (HDD)** | ~5–10 ms | TBs | no | OS / device |
| **Tape / archive** | seconds | PBs | no | admin |

> **The numbers that matter:** **RAM (~100 ns) vs disk (~10 ms) ≈ 100,000×.** This
> single gap is why caching, virtual memory, and buffer pools exist — the whole
> game is *avoid touching the slow levels.*

> **Two great divides (memorise):**
> - **Volatile (registers/cache/RAM — lose data on power off)** vs **non-volatile
>   (SSD/HDD/tape — persist).**
> - **Primary storage** = directly CPU-addressable (registers, cache, RAM) vs
>   **secondary** = disks/SSD (I/O, not byte-addressable by the CPU) vs **tertiary**
>   = tape/optical archives.

### MCQs

1. Fastest → slowest of registers/RAM/cache/disk? → **registers > cache > RAM >
   disk**.
2. Order-of-magnitude RAM-to-disk speed gap? → **~100,000×**.
3. Which levels are **volatile**? → **registers, cache, RAM**.
4. Primary vs secondary storage divide? → **CPU-addressable (RAM)** vs **I/O
   (disk)**.

---

## 2.7 RAM vs ROM (and memory types)

- **RAM (Random Access Memory)** — **volatile** read/write working memory; loses
  contents on power off. Two flavours:
  - **SRAM (static)** — fast, expensive, no refresh → used for **cache**.
  - **DRAM (dynamic)** — denser, cheaper, needs periodic **refresh** → used for
    **main memory** (DDR4/DDR5).
- **ROM (Read-Only Memory)** — **non-volatile**; keeps contents without power. Holds
  **firmware** — the boot code (**BIOS/UEFI**, §2.13) that runs first at power-on.
  Variants: **PROM** (write once), **EPROM** (UV-erasable), **EEPROM / flash**
  (electrically erasable; SSDs and UEFI firmware are flash).

> **Memory hook:** **RAM = a whiteboard** (fast, rewritable, wiped when the lights
> go off). **ROM = a printed manual** (permanent, hard to change, always there at
> startup).

| | RAM | ROM |
|---|---|---|
| Volatile? | **yes** (lost on power off) | **no** (persists) |
| Read/write? | read **and** write | mostly **read** (firmware) |
| Speed | fast | slower |
| Use | running programs & data | boot firmware (BIOS/UEFI) |

### MCQs

1. Which memory is volatile — RAM or ROM? → **RAM**.
2. Cache is built from which RAM type? → **SRAM**. Main memory? → **DRAM**.
3. DRAM needs periodic ___ → **refresh**.
4. Boot firmware lives in? → **ROM / flash (BIOS/UEFI)**.

---

## 2.8 Cache & the Principle of Locality (brief)

**Cache** is small, fast SRAM that sits between the CPU and RAM and keeps **recently
and soon-to-be-used** data close. It works only because real programs obey the
**principle of locality**:

- **Temporal locality:** data used **now** is likely used **again soon** (a loop
  variable, a hot function).
- **Spatial locality:** if you touch address `X`, you'll likely touch **nearby**
  addresses (array elements, next instruction) — so caches fetch a whole **cache
  line** (e.g. 64 B), not one byte.

**Hit vs miss:** a **cache hit** = the data was in cache (fast). A **cache miss** =
not there → fetch from the next level down (slow) and cache it. **Hit ratio** =
`hits / (hits + misses)`; **average access time = hit_time + miss_rate ×
miss_penalty**.

**Cache mapping (how a memory block maps to a cache slot) — one line each:**

| Mapping | Rule | Trade-off |
|---------|------|-----------|
| **Direct-mapped** | each block → **exactly one** slot | simple/fast, more conflicts |
| **Fully associative** | a block → **any** slot | fewest misses, costly search |
| **Set-associative** (e.g. 4-way) | block → one **set**, any slot in it | the practical middle ground |

> **Memory hook:** **temporal = "same thing again soon"; spatial = "the neighbour
> next."** Caches bet on both — that's why they work.

### MCQs

1. Loop reusing a variable exploits which locality? → **temporal**.
2. Fetching a whole cache line exploits which? → **spatial**.
3. Average access time formula? → **hit time + miss rate × miss penalty**.
4. Mapping with exactly one slot per block? → **direct-mapped**.

---

## 2.9 The MMU — Memory Management Unit

The **MMU** is hardware (on the CPU) that translates the **logical/virtual address**
a program uses into the **physical address** in RAM, on **every** memory access. It
is what makes **virtual memory, paging, and protection** (M9–M10) possible.

- Programs run in their own **virtual address space** (each thinks it owns all of
  memory); the MMU maps virtual pages → physical frames via **page tables**.
- A small cache called the **TLB (Translation Lookaside Buffer)** stores recent
  translations so the MMU rarely walks the full page table (M9 covers this in
  depth).
- The MMU also **enforces protection**: an access outside a process's mapping (or
  writing a read-only page) triggers a **page fault / segmentation fault** trap.

> **Memory hook:** the MMU is a **real-time translator + bouncer**: it converts
> every "virtual" address to a real one *and* blocks addresses a process isn't
> allowed to touch.

### MCQs

1. What does the MMU translate? → **virtual/logical → physical** addresses.
2. Small cache of recent translations? → the **TLB**.
3. Illegal memory access triggers a? → **page/segmentation fault (trap)**.

---

## 2.10 DMA — Direct Memory Access (why it frees the CPU)

Moving a 4 KB disk block into RAM one word at a time would make the **CPU** copy
every word through a register — thousands of instructions of pure babysitting.
**DMA** hands that job to a dedicated **DMA controller**, so the CPU only sets up
the transfer and is interrupted **once**, at the end.

![Without DMA the CPU copies every word (programmed I/O); with DMA the controller moves data device↔memory directly and interrupts the CPU only once, at completion.](images/16_dma_transfer.png)

```text
Programmed I/O (no DMA):        DMA:
  device -> CPU register ->       CPU tells DMA: "move N bytes, dev<->addr"
  -> memory, word by word;        DMA moves data device <-> memory directly,
  CPU busy the whole time.        CPU does other work; ONE interrupt at the end.
```

**How DMA works:**

1. CPU programs the DMA controller: **source, destination, byte count, direction.**
2. DMA controller performs the transfer **directly between the device and RAM**
   over the bus, without CPU involvement per word.
3. On completion, the controller raises **one interrupt**; the CPU wraps up.

- **Cycle stealing:** the DMA controller "steals" occasional **bus cycles** from the
  CPU to move a word at a time, interleaving with CPU work — minimal disruption.
- **Burst mode:** DMA takes the bus and transfers a whole block at once — faster,
  but the CPU is blocked from the bus during the burst.

> **Why DMA matters (the exam point):** DMA **frees the CPU from data-copying**, so
> the CPU does useful work during large I/O. It is essential for high-throughput
> devices (disk, SSD, network, GPU). **The CPU is interrupted once per transfer,
> not once per word.**

### MCQs

1. What is the main benefit of DMA? → **frees the CPU from copying data during
   I/O**.
2. DMA "cycle stealing" steals what? → occasional **bus cycles** from the CPU.
3. With DMA, how many interrupts per block transfer? → **one** (at completion).
4. Who is programmed with source/dest/count? → the **DMA controller**.

---

## 2.11 Buses, Storage & I/O Devices, PCIe

### Buses

The CPU, memory, and devices are wired together by **buses**:

- **Address bus** — carries *which* location (driven by the MAR); its width sets the
  addressable memory (e.g. 32 lines → 4 GB).
- **Data bus** — carries the actual bits (via the MBR).
- **Control bus** — carries signals like read/write, interrupt, clock.

### Storage & I/O device classes

- **Block devices** (disk, SSD) — addressed in fixed-size **blocks**; support random
  access; read/written a block at a time.
- **Character devices** (keyboard, serial, mouse) — a **stream of bytes**, no seek.
- **Network devices** — send/receive packets (a special stream).

Each device has a **controller** (its own small processor + registers/buffers); the
OS talks to it through a **device driver** (M13). Registers are accessed via
**memory-mapped I/O** (device registers appear as memory addresses) or **port-mapped
I/O** (special `in`/`out` instructions).

### PCIe (Peripheral Component Interconnect Express)

**PCIe** is the modern high-speed bus connecting GPUs, NVMe SSDs, and network cards
to the CPU. Key facts:

- **Serial**, **point-to-point** links (not a shared parallel bus) made of
  **lanes**; a slot is **x1, x4, x8, or x16** (more lanes = more bandwidth).
- Each generation roughly **doubles** per-lane bandwidth (PCIe 3.0 → 4.0 → 5.0 …).
- NVMe SSDs and GPUs live on PCIe precisely because it is fast and uses **DMA** to
  move data straight to RAM.

> **Memory hook:** **PCIe = private multi-lane highways** (point-to-point lanes)
> replacing the old shared single-lane road (legacy PCI).

### MCQs

1. Block vs character device? → **fixed-size random-access blocks (disk)** vs **byte
   stream (keyboard)**.
2. Device registers mapped into the address space is called? → **memory-mapped
   I/O**.
3. `x16` on a PCIe slot refers to? → the number of **lanes**.
4. What sets the maximum addressable memory? → the **address bus width**.

---

## 2.12 Multi-Core & NUMA

### Multi-core

A modern CPU **chip** contains several **cores**, each a full CPU (its own ALU,
registers, L1/L2 cache) usually sharing an **L3 cache** and memory. This gives
**true parallelism** (M1's *multiprocessing*): the OS schedules **one thread per
core** at a time. **Hyper-threading / SMT** lets one core present as two **logical**
CPUs to hide stalls. Software must be written to **parallelise** to benefit —
**Amdahl's Law** caps speedup by the serial fraction.

### NUMA (Non-Uniform Memory Access)

In big multi-socket servers, each CPU (socket) has its **own local RAM**. A core
reaches its **local** memory fast, but a **remote** socket's memory (over an
interconnect) is **slower** — hence "**non-uniform**" access. Contrast with **UMA
(SMP)**, where every CPU sees the **same** memory latency.

- The OS is **NUMA-aware**: it tries to run a thread on the node whose **local**
  memory holds its data (**memory affinity**), because remote access can be ~1.5–2×
  slower.

> **Memory hook:** **UMA = one shared fridge for the whole office** (everyone same
> distance). **NUMA = each team has its own fridge** — grabbing from your own is
> fast; from another team's, slower.

### MCQs

1. UMA vs NUMA? → **uniform** memory latency for all CPUs vs **local-fast,
   remote-slow**.
2. Why is an OS "NUMA-aware"? → to keep a thread near its **local** memory
   (affinity).
3. One core acting as two logical CPUs is? → **SMT / hyper-threading**.
4. What caps parallel speedup? → the **serial fraction (Amdahl's Law)**.

---

## 2.13 The Bus's-Eye View: Putting It Together

A quick end-to-end picture of a **disk read**, which uses almost everything above:

```text
1. Program calls read()  -> TRAP (software interrupt) into the kernel (M3).
2. Kernel driver programs the disk controller + DMA (source LBA, dest RAM addr, count).
3. CPU goes off to run ANOTHER process (I/O is slow) -- multiprogramming (M1).
4. Disk finds the data; DMA moves the block DIRECTLY into RAM (cycle stealing).
5. Disk controller raises a HARDWARE INTERRUPT: "transfer complete."
6. CPU finishes its instruction, saves context, runs the ISR via the vector table.
7. ISR marks the waiting process READY; scheduler may resume it. Data is in RAM.
```

Trap, DMA, interrupt, vector table, memory hierarchy, scheduling — one operation,
the whole module.

---

## 2.14 Real-World & Backend Perspectives

- **Every performance problem is a memory-hierarchy problem.** A cache-friendly
  data layout (contiguous arrays, spatial locality) can beat a "smarter" algorithm
  that thrashes cache. Backend hot paths live or die by L1/L2 hit rates.
- **DMA is why servers scale I/O:** NVMe, 100 GbE NICs, and GPUs all DMA data
  straight to RAM; the CPU orchestrates rather than copies. "Zero-copy" networking
  (`sendfile`, `io_uring`) is about avoiding needless CPU copies on top of that.
- **NUMA tuning is real money in production:** pinning threads and memory to the
  same NUMA node (`numactl`, `taskset`) can cut latency noticeably on big
  databases and JVMs.
- **The timer interrupt is your scheduler's pulse:** understanding it explains why a
  runaway loop still yields (preemption) and why "tickless" kernels save power on
  idle servers.

---

## 2.15 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** swapping **PC and IR** — PC = *next* address, IR = *current*
  instruction.
- **Mistake:** confusing **MAR (address)** with **MBR (data)**.
- **Mistake:** calling a **system call** a hardware interrupt — it's a **trap
  (software interrupt / synchronous)**.
- **Mistake:** thinking DMA gives one interrupt **per word** — it's **one per
  transfer**.
- **Mistake:** "cache miss rate low ⇒ fast" while ignoring **miss penalty** — a rare
  miss to disk still dominates.
- **Edge case:** on **SSD**, "seek time" ≈ 0, so the classic random-vs-sequential
  gap shrinks (but sequential still wins).
- **Tradeoff:** SRAM (fast, costly, cache) vs DRAM (dense, cheap, main memory);
  direct-mapped (simple, more conflicts) vs associative (fewer misses, costlier).
- **Tradeoff:** DMA **burst mode** (fast, hogs the bus) vs **cycle stealing** (gentle
  on the CPU, slower per transfer).

---

## 2.16 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** register roles, fetch-decode-execute order, trap vs
  interrupt, RAM vs ROM, memory-hierarchy ordering, DMA benefit — all classic
  one-markers.
- **GATE:** average memory access time (cache), locality types, vectored vs polled,
  DMA cycle stealing; the vocabulary underpins M6/M9 numericals.
- **Interview:** "What happens on a system call?" (trap → kernel mode → handler);
  "Why is DMA better than programmed I/O?"; "Explain the memory hierarchy and why
  caches work" (locality).
- **Coding/practical:** `perf stat` shows cache-miss rates and IPC; `lscpu` shows
  cores/threads/caches/NUMA nodes; `numactl --hardware` shows NUMA topology.

---

## 2.17 Concept Checks & MCQs (test yourself)

1. Three parts of a CPU? → **ALU, control unit, registers**.
2. PC vs IR? → **address of next instruction** vs **current instruction**.
3. MAR vs MBR? → **address** (where) vs **data** (what).
4. Order of the machine cycle? → **fetch → decode → execute**.
5. Trap vs interrupt? → **synchronous/internal** vs **asynchronous/external**.
6. A system call is which kind? → a **trap (software interrupt)**.
7. Vectored vs polled interrupt? → **vector-table index** vs **poll each device**.
8. Which hardware enables preemptive scheduling? → the **timer**.
9. Memory hierarchy fastest → slowest? → **registers > cache > RAM > SSD > HDD >
   tape**.
10. RAM–disk speed gap? → **~100,000×**.
11. RAM vs ROM volatility? → RAM **volatile**, ROM **non-volatile**.
12. SRAM vs DRAM use? → **cache** vs **main memory** (DRAM needs refresh).
13. Two kinds of locality? → **temporal** and **spatial**.
14. Average access time? → **hit time + miss rate × miss penalty**.
15. What does the MMU do? → translate **virtual → physical**, enforce protection.
16. TLB is a cache of? → recent **address translations**.
17. Main benefit of DMA? → **frees the CPU from copying I/O data**.
18. DMA interrupts per transfer? → **one** (at completion).
19. Cycle stealing steals? → **bus cycles**.
20. PCIe is ___ and ___ (topology)? → **serial**, **point-to-point** (lanes).
21. UMA vs NUMA? → **uniform** vs **local-fast/remote-slow** memory.
22. What caps multi-core speedup? → the **serial fraction (Amdahl's Law)**.

**True/False**
- The PC holds the instruction currently executing. → **False** (that's the IR).
- A divide-by-zero is an asynchronous interrupt. → **False** (synchronous trap).
- ROM loses its contents on power off. → **False** (non-volatile).
- DMA raises one interrupt per word. → **False** (one per transfer).
- Cache exploits temporal and spatial locality. → **True**.
- In NUMA, all CPUs see equal memory latency. → **False** (that's UMA).

---

## 2.18 One-Page Revision Sheet

```
CPU = ALU (math/logic + flags) + CONTROL UNIT (sequences signals) + REGISTERS (fastest).
REGISTERS: PC=next-instr addr | IR=current instr | MAR=addr(where) | MBR/MDR=data(what)
  ACC=ALU operand/result | SP=top of stack | GPRs=temporaries | PSW/FLAGS=status+mode.
  "PC next, IR now; MAR where, MBR what; SP top, ACC math."

MACHINE CYCLE: FETCH (MAR<-PC; MBR<-Mem; IR<-MBR; PC++) -> DECODE (CU reads opcode)
  -> EXECUTE (ALU) -> CHECK INTERRUPTS -> repeat.  (interrupt check = OS regains CPU)

INTERRUPTS: hardware(async, external: timer/IO) | trap/software(sync: syscall) |
  exception(sync: div0, page fault).  TRAP=internal/sync ; INTERRUPT=external/async.
  CYCLE: finish instr -> save PC+PSW -> kernel mode -> vector table -> ISR -> restore -> IRET.
  VECTORED = index vector table (fast) ; POLLED = one handler asks each device (slow).

TIMER = raises periodic interrupt -> enables PREEMPTIVE scheduling + timekeeping.

MEMORY HIERARCHY (fast/small/costly -> slow/big/cheap):
  registers(~1ns) > L1 > L2 > L3 cache > RAM(~100ns, VOLATILE) > SSD(~100us) > HDD(~10ms) > tape.
  RAM vs disk ~100,000x.  VOLATILE=reg/cache/RAM ; PRIMARY=CPU-addressable vs SECONDARY=disk.

RAM(volatile, r/w): SRAM=cache(fast), DRAM=main mem(needs refresh).
ROM(non-volatile): firmware/BIOS/UEFI ; PROM/EPROM/EEPROM(flash).

CACHE: locality TEMPORAL(same soon) + SPATIAL(neighbour) -> fetch a line.
  hit/miss ; hit ratio=hits/(hits+miss) ; AMAT = hit_time + miss_rate*miss_penalty.
  mapping: direct(1 slot) | fully-assoc(any) | set-assoc(one set) .

MMU: virtual->physical each access + protection ; TLB caches translations ; bad access=fault.

DMA: controller moves data device<->RAM directly ; CPU freed ; ONE interrupt/transfer.
  cycle stealing = grab occasional bus cycles ; burst = take bus for whole block.

BUSES: address(where/MAR) + data(what/MBR) + control(read/write/irq).
  PCIe = serial, point-to-point LANES (x1/x4/x8/x16), doubles/gen ; GPUs/NVMe DMA to RAM.
MULTI-CORE: many full cores (true parallel), share L3 ; SMT=1 core->2 logical ; Amdahl caps.
NUMA: each socket has local RAM (local fast, remote slow) vs UMA(equal) ; OS uses affinity.
```

### Flash cards

| Front | Back |
|-------|------|
| PC vs IR? | Next-instruction address vs current instruction |
| MAR vs MBR? | Address (where) vs data (what) |
| Machine cycle order? | Fetch → decode → execute |
| Trap vs interrupt? | Synchronous/internal vs asynchronous/external |
| System call is which type? | Trap (software interrupt) |
| Vectored vs polled? | Vector-table index vs poll each device |
| Hardware for preemption? | Timer interrupt |
| RAM–disk speed gap? | ~100,000× |
| RAM vs ROM? | Volatile r/w vs non-volatile firmware |
| SRAM vs DRAM? | Cache vs main memory (refresh) |
| Temporal vs spatial locality? | Same data again vs nearby addresses |
| AMAT formula? | hit time + miss rate × miss penalty |
| MMU does? | Virtual→physical + protection |
| Benefit of DMA? | Frees CPU from I/O copying |
| DMA interrupts/transfer? | One (at completion) |
| Cycle stealing steals? | Bus cycles |
| PCIe topology? | Serial, point-to-point lanes |
| UMA vs NUMA? | Equal latency vs local-fast/remote-slow |

### Spaced repetition
- **24-hour:** recite the register roles and the fetch-decode-execute micro-steps;
  trap vs interrupt.
- **7-day:** draw the memory hierarchy with speeds; explain DMA and cycle stealing;
  vectored vs polled.
- **30-day:** trace a full `read()` (trap → DMA → interrupt → resume); explain
  locality, the MMU, and NUMA affinity without notes.

---

## 2.19 Summary

Underneath every OS is a **CPU** that forever repeats **fetch → decode → execute**,
using tiny **registers** (**PC** for the next instruction, **IR** for the current,
**MAR/MBR** for memory address/data, **SP**, **ACC**, and general-purpose) driven by
the **control unit** with the **ALU** doing the math. The OS gets to run at all
because of **interrupts**: **hardware** ones (async, external — timer, I/O),
**traps** (sync, internal — a **system call** or fault), located via the **vector
table** (**vectored** = direct, **polled** = search). The **timer interrupt** is the
scheduler's heartbeat. Because no memory is fast, big, and cheap, we layer a
**memory hierarchy** — **registers → cache → RAM (volatile) → SSD → disk → tape** —
where RAM is ~**100,000×** faster than disk, and **caches** win by exploiting
**temporal and spatial locality**. We separated **RAM vs ROM**, met the **MMU**
(virtual→physical + protection), and saw **DMA** free the CPU from I/O copying
(**one** interrupt per transfer, **cycle stealing** the bus). Finally, **PCIe**
(serial lanes), **multi-core** (true parallelism), and **NUMA** (local-fast,
remote-slow) round out the modern machine.

Next, **Module 3 — Operating System Architecture** puts the OS *itself* on top of
this hardware: kernel designs (monolithic vs microkernel vs hybrid), user vs kernel
mode, system calls, and the boot process that brings the kernel to life.

> **You have mastered this module when** you can: name each register's role and
> trace the fetch-decode-execute cycle; explain trap vs interrupt and the interrupt
> cycle (vectored vs polled); draw the memory hierarchy with speeds and the
> volatile/non-volatile and primary/secondary divides; contrast RAM vs ROM and
> SRAM vs DRAM; explain locality, the MMU, and why DMA frees the CPU (cycle
> stealing, one interrupt/transfer); and describe PCIe, multi-core, and NUMA — all
> without notes.
