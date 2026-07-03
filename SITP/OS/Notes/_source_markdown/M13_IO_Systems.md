---
title: "Module 13 — I/O Systems"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 13 — I/O Systems

> **Where this module sits.**
> Module 12 zoomed in on one device — the disk. This module zooms **out** to the OS's
> relationship with **every** device: keyboards, mice, network cards, GPUs, printers,
> disks, and USB sticks. The core question is simple and old: **the CPU runs in
> nanoseconds, but devices answer in milliseconds — how does the OS bridge that gap
> without wasting the CPU?** The three classic answers — **programmed I/O (polling),
> interrupt-driven I/O, and DMA** — plus **buffering, caching, and spooling**, plus
> the **kernel I/O subsystem** that ties them together, are the heart of this module.
> This is where hardware (M2's interrupts and DMA), scheduling (M6), and the file
> system (M11–M12) all meet, and it is the direct on-ramp to how a **backend server
> handles ten thousand connections** with `epoll`/`io_uring` (previewed for M20).

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★★★      | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **programmed I/O vs
interrupt-driven I/O vs DMA** (definitions, CPU cost, when each); **memory-mapped vs
port-mapped (isolated) I/O**; **DMA cycle stealing** and **one interrupt per block**;
the **interrupt-driven I/O cycle**; **block vs character devices**; **role of the
device driver**; **buffering vs caching vs spooling**; **single vs double buffering**;
**blocking vs non-blocking vs asynchronous I/O**.

---

## 13.1 I/O Hardware — Controllers, Ports, and the Bus

### First principles
A device rarely plugs straight into the CPU. Between them sits a **device controller**
(a small special-purpose processor), and they all share a **bus** — a set of parallel
wires (address, data, control) that everything hangs off.

![I/O hardware: the CPU and memory reach every device through its controller on a shared system bus; each controller exposes data, status, and control registers.](images/122_io_hardware.png)

- **Device** — the physical thing (disk, keyboard, NIC).
- **Device controller** — the electronics that operate the device and talk to the bus
  (a disk controller, USB host controller, NIC). It contains a few **registers** and
  often a small **local buffer**.
- **Port** — a connection point / a controller register the CPU can read or write.
- **Bus** — shared wires connecting CPU, memory, and controllers. A **daisy chain** of
  buses is common: fast PCIe near the CPU, slower USB/SATA further out.

**The four controller registers (learn these names):**

| Register | Direction | Purpose |
|----------|-----------|---------|
| **Data-in** | controller → CPU | byte(s) read from the device |
| **Data-out** | CPU → controller | byte(s) to send to the device |
| **Status** | controller → CPU | is it busy / ready / error / has data? |
| **Control** | CPU → controller | issue a command (read, write, seek) |

> **Memory hook:** the CPU never touches the device directly — it **pokes the
> controller's registers**. "Set control = READ, then keep checking status until the
> data-in register is ready." Everything in this module is a smarter way of doing
> that last "keep checking".

### MCQs
1. The small processor that operates a device and talks to the bus? → **device
   controller**.
2. The four controller registers? → **data-in, data-out, status, control**.
3. A connection point / register the CPU addresses? → a **port**.

---

## 13.2 How the CPU Addresses Devices — Memory-Mapped vs Port-Mapped I/O

The CPU reads/writes controller registers using one of **two addressing schemes**.

### Memory-mapped I/O
Device registers are given **addresses in the ordinary memory address space**. To talk
to a device the CPU uses **normal load/store instructions** (`MOV`) — the same ones it
uses for RAM. A range of physical addresses is simply routed to a device instead of to
memory.

- **Pro:** no special instructions; any memory-manipulating code (and C pointers) can
  drive the device; large register spaces (framebuffers) are easy.
- **Con:** consumes part of the physical address space; caching must be **disabled**
  for those addresses (a stale cached status register would be a disaster).

### Port-mapped (isolated) I/O
Devices live in a **separate I/O address space**, reached only by **special
instructions** — on x86 the `IN` and `OUT` instructions with an 8/16-bit **port
number**.

- **Pro:** keeps the memory address space fully for RAM; clearly separates I/O.
- **Con:** needs dedicated instructions and an extra control line; small address space.

| | **Memory-mapped I/O** | **Port-mapped (isolated) I/O** |
|---|---|---|
| Address space | shared with **memory** | **separate** I/O space |
| Instructions | ordinary `MOV` (load/store) | special `IN` / `OUT` |
| Caching | must be **disabled** for those addrs | N/A (separate space) |
| Typical use | ARM, RISC-V, modern PCIe, GPUs | legacy x86 peripherals |

> **Memory hook:** **memory-mapped = the device pretends to be RAM** (same addresses,
> same `MOV`). **Port-mapped = the device lives on a different street** with its own
> `IN`/`OUT` doors. Modern architectures lean almost entirely on memory-mapped I/O.

### MCQs
1. Scheme where device registers share the memory address space? → **memory-mapped
   I/O**.
2. x86 instructions for port-mapped I/O? → **IN / OUT**.
3. Why must memory-mapped device regions be **uncached**? → the CPU must see **live**
   status, not a stale cached copy.

---

## 13.3 Device Drivers — Block vs Character Devices

### The role of a driver
A **device driver** is the piece of kernel code that knows the **exact quirks of one
controller** and hides them behind a **uniform interface** the rest of the kernel
calls. It is the single "translator" so the kernel can say `read this block` and not
care whether the disk is SATA, NVMe, or a USB stick.

The kernel defines a small standard set of operations (in Unix: `open`, `close`,
`read`, `write`, `ioctl`, ...); each driver **fills in** those functions for its
hardware. This is **device independence** in action (§13.10): the same `read()` call
reaches the right driver through a **function-pointer table**.

> **Memory hook:** the driver is a **power adapter**. Your laptop (kernel) has one plug
> shape; every country's socket (device) is different; the adapter (driver) makes them
> fit. Swap the adapter, not the laptop.

### Block vs character devices (a favourite MCQ)
Unix classifies devices into two families:

| | **Block device** | **Character device** |
|---|---|---|
| Unit of transfer | fixed-size **blocks** (e.g. 4 KB) | a **stream of bytes** |
| Access | **random** (any block by number) | usually **sequential** |
| Buffering/cache | goes through the **buffer/page cache** | often unbuffered / line-buffered |
| Examples | **disk, SSD, USB drive** | **keyboard, mouse, serial port, terminal** |
| `ls -l` tag | `b` | `c` |

- A **network card** fits neither neatly and gets its **own interface** (the socket
  API), not a simple file-like read/write of blocks or bytes.
- A **pseudo-device** like `/dev/null` or `/dev/random` is a character device with no
  physical hardware behind it.

### MCQs
1. Kernel code that hides one controller's quirks behind a uniform interface? →
   **device driver**.
2. Disk vs keyboard device class? → **block** vs **character**.
3. Which device type transfers a **stream of bytes**? → **character**.
4. `/dev/null` is a ___ device → **character**.

---

## 13.4 The Three I/O Techniques — Programmed I/O vs Interrupt-Driven vs DMA

This is the centrepiece of the module. There are exactly **three** ways to move data
between a device and memory, and they differ entirely in **how much CPU they waste**.

![The three I/O techniques compared: programmed I/O busy-waits (CPU 100%), interrupt-driven I/O frees the CPU but interrupts once per byte/word, and DMA offloads the whole block with just one interrupt at the end.](images/123_io_techniques.png)

### 1. Programmed I/O (polling / busy-waiting)
The CPU issues the command, then **spins in a loop reading the status register** until
the device is ready, then **moves each byte itself**. The CPU is **100% busy doing
nothing useful** for the whole transfer.

```text
loop:  read STATUS register
       if not READY: goto loop        # busy-wait (polling)
       read DATA-IN register -> memory
       repeat for every byte
```

- **When:** tiny, fast, or embedded transfers where an interrupt would cost more than
  the wait; or very simple systems with no interrupt hardware.
- **CPU cost:** **worst** — the CPU wastes cycles polling.

### 2. Interrupt-driven I/O
The CPU issues the command and **goes off to do other work**. When the device becomes
ready, the controller raises an **interrupt**; the CPU stops, runs an **interrupt
service routine (ISR)** that moves the data, then resumes what it was doing.

- **When:** moderate-rate devices (keyboard, mouse, serial line) where the CPU has
  better things to do while waiting.
- **CPU cost:** far better than polling **for waiting**, but there is still **one
  interrupt per byte/word**, and each interrupt has real overhead (save state, run ISR,
  restore). For a fast disk moving millions of bytes, that overhead becomes huge — that
  is the problem DMA solves.

### 3. DMA (Direct Memory Access)
A dedicated **DMA controller** moves an **entire block** between the device and memory
**without the CPU touching each byte**. The CPU just programs the DMA controller
(source, destination, count) and is free until the **whole block** is done, when it
gets **one interrupt** (detailed in §13.6).

- **When:** **bulk transfers** — disk, network, GPU, sound.
- **CPU cost:** **best** — one setup + one interrupt per block, regardless of block
  size.

### The comparison table (memorise)

| | **Programmed I/O (polling)** | **Interrupt-driven** | **DMA** |
|---|---|---|---|
| Who moves each byte | **CPU** | **CPU** (in the ISR) | **DMA controller** |
| CPU while waiting | **busy-wait (100%)** | free to do other work | free to do other work |
| Interrupts | none | **1 per byte/word** | **1 per block** |
| Overhead per byte | polling cycles | interrupt handling | almost none |
| Best for | tiny/embedded transfers | moderate-rate devices | **bulk transfers (disk/NIC)** |
| CPU cost ranking | **highest** | medium | **lowest** |

> **Memory hook:** three ways to boil water. **Polling** = stare at the kettle the
> whole time. **Interrupts** = do chores, come when it whistles — but a kettle that
> whistles **every drop** is annoying. **DMA** = hire an assistant who fills the whole
> pot and taps you **once** when it's done.

### MCQs
1. Which technique makes the CPU **busy-wait**? → **programmed I/O (polling)**.
2. Which has **one interrupt per byte/word**? → **interrupt-driven I/O**.
3. Which moves a **whole block** with **one interrupt**? → **DMA**.
4. Lowest CPU cost for bulk transfers? → **DMA**.

---

## 13.5 The Interrupt-Driven I/O Cycle

An **interrupt** is a hardware signal that makes the CPU pause its current program and
jump to a handler. It is what turns "the CPU had to keep asking" into "the device tells
the CPU when it's ready." (The mechanism was introduced in **M2**; here we apply it to
I/O — see the interrupt-cycle diagram there.)

![The interrupt-driven I/O cycle: the device controller raises an interrupt when ready; the CPU saves state, the ISR moves the data via the driver, then state is restored and the program resumes.](images/14_interrupt_cycle.png)

**The cycle, step by step:**

```text
1. CPU issues an I/O command to the controller (via a driver), then continues
   running OTHER work.
2. Device finishes / is ready -> controller asserts the INTERRUPT-REQUEST line.
3. CPU finishes the current instruction, then checks the interrupt line.
4. CPU SAVES its state (program counter, registers) and looks up the
   INTERRUPT VECTOR to find the correct handler (ISR).
5. ISR (part of the device driver) runs: read/write the data register, clear
   the interrupt, maybe wake the waiting process.
6. CPU RESTORES the saved state and RESUMES the interrupted program.
```

**Key refinements:**
- **Interrupt vector:** a table mapping each interrupt number to its handler address,
  so dispatch is O(1) — the CPU doesn't ask "who interrupted?".
- **Maskable vs non-maskable:** the CPU can temporarily **mask** (defer) ordinary
  interrupts during a critical section; a **non-maskable interrupt (NMI)** (e.g. power
  failure) cannot be ignored.
- **Priority levels:** a higher-priority interrupt can pre-empt a lower one.
- **Top half / bottom half (Linux):** the ISR does the bare minimum urgently (**top
  half**), and defers slower work to a **softirq/tasklet/workqueue** (**bottom half**)
  so interrupts stay disabled for as short a time as possible.

> **Memory hook:** interrupt = a **doorbell**. You don't stand at the door waiting
> (polling); you cook dinner and the bell (interrupt) makes you drop everything,
> answer (ISR), then go back to exactly where you were (restored state).

### MCQs
1. Table mapping interrupt number → handler address? → **interrupt vector**.
2. Interrupt that cannot be masked (e.g. power fail)? → **NMI**.
3. Linux name for the deferred, slower half of interrupt work? → **bottom half**
   (softirq/tasklet/workqueue).

---

## 13.6 DMA in Depth — Cycle Stealing and One Interrupt per Block

**DMA (Direct Memory Access)** exists to kill the "one interrupt per byte" tax of
interrupt-driven I/O for **bulk** transfers. A separate **DMA controller** does the
byte-by-byte moving; the CPU only sets it up and hears about it **once** at the end.

![DMA: the CPU programs the DMA controller with source, destination, and count; the controller transfers the whole block directly to memory over the bus and raises a single interrupt when the block is complete.](images/16_dma_transfer.png)

**The DMA transfer cycle:**

```text
1. CPU programs the DMA controller: source addr, destination addr, byte COUNT,
   direction. Then the CPU goes back to other work.
2. DMA controller requests the BUS and moves data device <-> memory directly,
   decrementing the count after each word. (CPU is NOT involved per word.)
3. When count = 0 (whole BLOCK done), the DMA controller raises ONE interrupt.
4. CPU's ISR handles completion (wake the waiting process). Done.
```

### Cycle stealing vs burst mode
The DMA controller and the CPU **share the same memory bus**, so they must take turns:

- **Cycle stealing:** the DMA controller "steals" **one bus cycle at a time** between
  CPU accesses, transferring a word then releasing the bus. The CPU is only **slightly**
  slowed; this is the common mode.
- **Burst mode:** the DMA controller grabs the bus and transfers the **whole block at
  once**, blocking the CPU from memory during the burst — faster transfer, but the CPU
  stalls.

> **Cycle stealing, precisely:** DMA and CPU contend for the memory bus. In cycle
> stealing the DMA takes the bus for **one word**, hands it back, and repeats — so the
> CPU loses only the occasional cycle rather than being frozen for the whole block.

### The big win — tie back to M2
The decisive advantage is the **interrupt count**. To read a 4 KB block:

```text
Interrupt-driven I/O : ~4096 interrupts (one per byte)  -> huge ISR overhead
DMA                  : 1 interrupt (per BLOCK)          -> CPU barely touched
```

That is why **every disk, NIC, GPU, and sound card** uses DMA. **Cache coherence** is
the catch: because DMA writes to memory **behind the CPU's back**, the OS/hardware must
ensure caches don't hold stale copies of the DMA'd region (snooping or explicit cache
flush/invalidate).

### MCQs
1. DMA raises how many interrupts per block? → **one**.
2. DMA mode that takes one bus cycle at a time? → **cycle stealing**.
3. The main correctness worry when DMA writes memory directly? → **cache coherence**
   (stale cached copies).
4. Why is DMA far cheaper than interrupt-driven I/O for a disk? → **one interrupt per
   block** instead of one per byte.

---

## 13.7 Buffering, Caching, and Spooling

These three services (introduced in **M1**) all sit between a fast producer and a slow
consumer, but they solve **different** problems. Exams love to separate them.

### Buffering — smooth out speed and size mismatches
A **buffer** is a memory area holding data **in transit** between device and
application. It exists for three reasons:
1. **Speed mismatch** — device and CPU run at different rates (a fast disk feeding a
   slow modem, or vice-versa).
2. **Transfer-size mismatch** — reassemble small packets into a full block, or split a
   big write into device-sized chunks.
3. **Copy semantics** — copy the app's data into a kernel buffer at `write()` time so
   later changes by the app don't corrupt the in-flight write.

**Single vs double buffering:**

![Buffering: with a single buffer the CPU must wait while the one buffer refills; with double buffering the device fills buffer A while the CPU drains buffer B, then they swap, so I/O overlaps computation.](images/124_double_buffering.png)

- **Single buffer:** one region. While the CPU processes it, the device **cannot** fill
  it → the two **cannot overlap**; someone always waits.
- **Double buffering:** two buffers. The device **fills A** while the CPU **drains B**,
  then they **swap**. Now I/O and computation **overlap** — the classic way to keep
  both busy. (Generalises to **circular buffering** with N buffers for bursty streams.)

### Caching — keep a copy of what's likely reused
A **cache** holds a **copy** of frequently-used data in faster storage to avoid re-doing
slow work (the disk **page cache** in RAM; the CPU cache over RAM).

> **Buffer vs cache — the exam distinction:** a **buffer** holds the **only** copy of
> data **in transit** (it must be moved on). A **cache** holds a **duplicate** of data
> that also lives elsewhere, kept **for reuse**. Same RAM region can serve both roles,
> but the intent differs: *move it once* vs *keep it for next time*.

### Spooling — a disk queue for a non-shareable device
**Spooling** (*Simultaneous Peripheral Operation On-Line*) uses the **disk as a huge
buffer** for a device that **can't interleave** requests — the textbook case is the
**printer**. Jobs are written to a **disk spool queue** and printed one at a time, so
many processes "print" instantly (to disk) and never wait for the physical printer.

> **Memory hook (from M1):** **buffer = small waiting room (RAM), in transit; cache =
> a saved copy kept for reuse; spool = a big waiting hall on disk for a device that
> serves one job at a time (printer).**

### MCQs
1. Overlap I/O with computation using two regions? → **double buffering**.
2. Holds the **only** copy, **in transit**? → **buffer**. Holds a **reusable
   duplicate**? → **cache**.
3. Disk queue for a printer? → **spooling**.
4. Single buffering's flaw? → device and CPU **can't overlap** (someone waits).

---

## 13.8 The Kernel I/O Subsystem and I/O Scheduling

Above the drivers, the kernel provides a **device-independent I/O subsystem** — a set
of services every device gets "for free":

- **I/O scheduling** — reorder the pending request queue for efficiency/fairness (the
  disk-scheduling algorithms of **M12** live here; NVMe often uses `none`).
- **Buffering, caching, spooling** — as in §13.7.
- **Naming & protection** — map names like `/dev/sda`, `C:` to devices and enforce
  permissions.
- **Error handling** — retry transient failures; report permanent ones (`EIO`).
- **I/O protection** — I/O instructions are **privileged**; user programs must go
  through **system calls**, so no process can drive hardware directly (M2's user/kernel
  mode).
- **Data structures** — the **open-file table**, per-device request queues, and a
  **function-pointer table** per driver.

**The life of one `read()`** (ties the whole module together):

```text
read(fd, buf, n)  --syscall trap--> kernel I/O subsystem
  -> check cache: HIT? copy out, return.  MISS? continue
  -> pick device via open-file table -> enqueue request (I/O scheduling)
  -> driver programs the controller / sets up DMA
  -> process BLOCKS (goes to sleep), CPU runs someone else
  -> device done -> INTERRUPT -> ISR -> DMA copied data to a kernel buffer
  -> copy buffer -> user's buf, mark process READY
  -> scheduler eventually resumes it; read() returns n
```

### MCQs
1. Where do the disk-scheduling algorithms live? → the **kernel I/O subsystem** (I/O
   scheduling).
2. Why can't a user program run `IN`/`OUT` directly? → I/O instructions are
   **privileged** (needs a system call).
3. Kernel structure tracking each process's open files? → the **open-file table**.

---

## 13.9 Blocking vs Non-Blocking vs Asynchronous I/O

From the **application's** point of view, an I/O call behaves in one of three ways.
This is the single most important section for **backend interviews**.

### Blocking I/O (synchronous)
The calling thread **sleeps** until the I/O completes; then the call returns with the
data. Simple to reason about, but **one slow read stalls the whole thread**.

```text
n = read(fd, buf, 4096);   // thread SLEEPS here until data arrives, then continues
```

### Non-blocking I/O
The call **returns immediately**. If data isn't ready it returns **"would block"**
(`EWOULDBLOCK`/`EAGAIN`) instead of sleeping; the app must **try again later** (usually
by **polling** many descriptors with `select`/`poll`/`epoll`). The **data copy still
happens synchronously** once the call succeeds.

```text
set O_NONBLOCK;
n = read(fd, buf, 4096);   // returns NOW: either some bytes, or EAGAIN (try later)
```

### Asynchronous I/O (async)
The call **returns immediately** and the transfer proceeds in the **background**; the
app is **notified on completion** (via a callback, signal, or a completion queue). The
app never waits and never re-polls for readiness — it is told when the whole operation
is **done**.

```text
aio_read(...);             // returns NOW; kernel does the whole transfer
... do other work ...
// later: completion notification -> data is already in buf
```

**The distinction that trips people up:**

| | Returns immediately? | App waits for data? | Notified of what? |
|---|:---:|:---:|---|
| **Blocking** | no | **yes (sleeps)** | — (returns with data) |
| **Non-blocking** | **yes** | no (retries later) | **readiness** ("try now") |
| **Asynchronous** | **yes** | no | **completion** ("it's done") |

> **Memory hook:** ordering a pizza. **Blocking** = stand at the counter until it's
> baked. **Non-blocking** = keep walking back to ask "ready yet?" (readiness polling).
> **Asynchronous** = give your number and they **call you when it's done** (completion).

> **The classic exam line:** *non-blocking* tells you about **readiness** ("you can try
> now"); *asynchronous* tells you about **completion** ("it's finished"). They are
> **not** the same thing.

### MCQs
1. Call that sleeps until data arrives? → **blocking**.
2. Call that returns `EAGAIN` when not ready? → **non-blocking**.
3. Non-blocking signals ___ ; async signals ___ → **readiness** ; **completion**.
4. Which model does the OS complete the transfer in the background? → **asynchronous**.

---

## 13.10 Device Independence — the Layered I/O Stack

Everything above works because I/O is built in **layers**, each hiding the one below.
This is why one `read()` works on a file, a pipe, a socket, and a USB stick.

![The layered I/O stack: a user process calls read()/write(); the device-independent kernel I/O subsystem handles naming, buffering, caching, scheduling, and errors; device drivers translate to hardware; interrupt handlers and the controllers sit at the bottom.](images/125_io_layers.png)

| Layer | Responsibility | Device-specific? |
|-------|----------------|:----------------:|
| **User process** | issues `read()`/`write()` | no |
| **Device-independent kernel I/O** | naming, buffering, caching, scheduling, errors, protection | **no** |
| **Device drivers** | translate uniform ops → this controller's registers | **yes** |
| **Interrupt handlers** | catch completion, wake the driver | mostly |
| **Hardware** | controllers + devices | yes |

The magic is the **uniform driver interface** (a table of `open/read/write/ioctl`
function pointers): to add a new device you **write one driver** that fills that table —
**nothing above it changes**. In Unix this is taken further with **"everything is a
file"**: disks, terminals, and even the kernel's own knobs appear as file paths
(`/dev/*`, `/proc/*`, `/sys/*`) driven by the same `read`/`write` calls.

### MCQs
1. Which single layer is device-**specific**? → the **device driver**.
2. What keeps upper layers unchanged when you add a device? → the **uniform driver
   interface** (function-pointer table).
3. Unix philosophy that unifies devices and files? → **"everything is a file"**.

---

## 13.11 Real-World & Backend Perspectives — the Bridge to Async I/O (M20 teaser)

The blocking/non-blocking/async distinction of §13.9 **is** the story of scalable
servers.

- **The C10k problem:** a server that uses **one blocking thread per connection**
  collapses at ~10,000 connections — too many threads, too much context-switching. The
  fix is **event-driven I/O**: **one thread watches thousands of sockets** and only
  acts on the ready ones.
- **`select`/`poll` → `epoll`:** `select`/`poll` re-scan **all** descriptors every call
  (O(n)); Linux **`epoll`** registers interest once and returns only the **ready** ones
  (O(ready)). This **readiness** model powers **nginx, Node.js, Redis, Netty**.
- **`io_uring` (modern Linux):** a true **asynchronous, completion-based** interface —
  the app posts requests to a **submission queue (SQ)** and reaps results from a
  **completion queue (CQ)** in **shared memory**, often with **zero syscalls** in the
  hot path. It generalises async to disk I/O too (which `epoll` never did well).
  Windows' **IOCP** and BSD **kqueue** are the equivalents.
- **DMA + zero-copy:** `sendfile()`/`splice()` let the NIC DMA data **straight from the
  page cache**, skipping user-space copies — the §13.6 DMA idea taken to the network
  fast path.

> **The through-line:** polling → interrupts → DMA (hardware level) is mirrored by
> blocking → readiness (`epoll`) → completion (`io_uring`) (software level). Same idea:
> **stop the fast side from waiting on the slow side.** This is developed fully in
> **M20 (backend & systems programming)**.

### MCQs
1. Linux O(ready) readiness interface behind nginx/Node? → **epoll**.
2. Linux completion-based async interface with SQ/CQ rings? → **io_uring**.
3. Windows equivalent of epoll/io_uring? → **IOCP**.

---

## 13.12 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes**
- Confusing **non-blocking** with **asynchronous** — readiness vs completion (§13.9).
- Saying interrupt-driven I/O has **no** overhead — it still costs **one interrupt per
  byte/word**; that's exactly why DMA exists.
- Thinking **DMA has no CPU cost at all** — it costs a **setup** and **one completion
  interrupt** per block, plus **bus contention** (cycle stealing) and a **cache
  coherence** concern.
- Mixing up **buffer** (only copy, in transit) and **cache** (reusable duplicate).
- Forgetting memory-mapped device regions must be **uncached**.
- Calling a printer queue "buffering" — it's **spooling** (disk-backed, non-shareable
  device).

**Edge cases**
- **Very small/fast transfers:** **polling** can beat interrupts (interrupt setup >
  the wait) — Linux NAPI even **switches NICs from interrupts to polling** under high
  load to avoid an interrupt storm ("livelock").
- **Interrupt livelock:** at extreme packet rates the CPU spends all its time in ISRs
  and makes no progress — mitigated by **interrupt coalescing** / NAPI polling.
- **Slow devices with DMA** gain little (setup cost dominates); DMA shines for **bulk**.

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Polling | no interrupt setup; simple | **CPU busy-wait** (wasted) |
| Interrupts | CPU free while waiting | overhead **per byte/word** |
| DMA | CPU free; **1 interrupt/block** | setup + bus contention + coherence |
| Double buffering | overlaps I/O & compute | 2× buffer memory |
| Blocking I/O | simple code | one thread per slow op (C10k) |
| Async I/O (io_uring) | massive concurrency | complex, callback/queue code |

---

## 13.13 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** the §13.4 comparison table (polling vs interrupt vs
DMA — who moves data, interrupt count, CPU cost); **memory-mapped vs port-mapped**;
**DMA cycle stealing** and **one interrupt per block**; **block vs character** devices;
**buffer vs cache vs spool**; **single vs double buffering**; interrupt vector / NMI.

**Interview:**
- "**Blocking vs non-blocking vs async**" — readiness vs completion; then "**how does a
  server handle 10k connections?**" → event loop + **epoll** (readiness), **io_uring**
  (completion).
- "**Why does DMA help?**" → CPU offloaded, **one interrupt per block** not per byte.
- "**What's a device driver / block vs character device?**"

**Coding/practical:**
- `ls -l /dev` → `b` (block) vs `c` (character) devices in the first column.
- `cat /proc/interrupts` → per-device interrupt counts across CPUs.
- `strace -e trace=read,write,epoll_wait ./server` → watch the real I/O syscalls.
- `lsblk`, `lspci`, `lsusb` → the controller/bus topology of §13.1.
- Set `O_NONBLOCK` with `fcntl()`; use `epoll_create1`/`epoll_ctl`/`epoll_wait` for the
  readiness loop.

---

## 13.14 Concept Checks & MCQs

1. Small processor operating a device and talking to the bus? → **device controller**.
2. Four controller registers? → **data-in, data-out, status, control**.
3. Memory-mapped vs port-mapped I/O? → **shared** memory addresses + `MOV` vs
   **separate** I/O space + `IN`/`OUT`.
4. Why must memory-mapped device regions be **uncached**? → CPU must see **live**
   status.
5. Kernel code hiding one controller's quirks? → **device driver**.
6. Block vs character device examples? → **disk/SSD** vs **keyboard/serial**.
7. Which I/O technique **busy-waits**? → **programmed I/O (polling)**.
8. Interrupts per byte in interrupt-driven I/O? → **one per byte/word**.
9. Interrupts per block in DMA? → **one**.
10. Lowest CPU cost for bulk transfers? → **DMA**.
11. DMA mode taking one bus cycle at a time? → **cycle stealing**.
12. Correctness worry when DMA writes memory directly? → **cache coherence**.
13. Table mapping interrupt number → handler? → **interrupt vector**.
14. Interrupt that can't be masked? → **NMI**.
15. Overlap I/O with compute using two regions? → **double buffering**.
16. Buffer vs cache? → **only copy, in transit** vs **reusable duplicate**.
17. Disk queue for a printer? → **spooling**.
18. Non-blocking signals ___ ; async signals ___ → **readiness** ; **completion**.
19. Call returning `EAGAIN` when not ready? → **non-blocking** read.
20. Which single I/O layer is device-specific? → the **device driver**.
21. Linux O(ready) readiness interface? → **epoll**. Completion-based ring interface? →
    **io_uring**.
22. Unix philosophy unifying devices and files? → **"everything is a file"**.

**True/False**
- Interrupt-driven I/O has no per-transfer overhead. → **False** (one interrupt per
  byte/word).
- DMA needs the CPU to move each byte. → **False** (the DMA controller does).
- Non-blocking I/O and asynchronous I/O are the same. → **False** (readiness vs
  completion).
- A printer queue is an example of caching. → **False** (**spooling**).
- Memory-mapped device registers can be safely cached. → **False** (must be uncached).

**Scenario (answer it):**
> A NIC receives 1,000,000 small packets/sec. Under pure interrupt-driven I/O the CPU
> hits **interrupt livelock**. Two fixes? → **DMA** (move packets to memory with far
> fewer interrupts) + **NAPI/interrupt coalescing** (switch to **polling** under load
> and batch completions). This is polling→interrupts→DMA and epoll→io_uring in one
> real problem.

---

## 13.15 One-Page Revision Sheet

```
I/O HARDWARE: CPU/memory <--BUS--> DEVICE CONTROLLERS <--> devices.
  Controller regs: DATA-IN, DATA-OUT, STATUS, CONTROL.  PORT = a controller register.

ADDRESSING:
  MEMORY-MAPPED  device regs share MEMORY addresses; use MOV; must be UNCACHED (ARM/PCIe).
  PORT-MAPPED    separate I/O space; special IN/OUT instrs (legacy x86).

DRIVER = kernel code hiding one controller behind a uniform interface (fn-ptr table).
  BLOCK device  = fixed blocks, random, buffered  (disk/SSD/USB)   -> 'b'
  CHAR  device  = byte stream, sequential         (kbd/mouse/serial)-> 'c'

THREE I/O TECHNIQUES  (CPU cost: POLLING > INTERRUPT > DMA):
  PROGRAMMED I/O (poll) CPU busy-waits on STATUS, moves each byte    -> CPU 100%
  INTERRUPT-DRIVEN      CPU works; device INTERRUPTS when ready       -> 1 int / BYTE
  DMA                   DMA controller moves whole block; CPU set-up  -> 1 int / BLOCK
  DMA: cycle stealing (1 bus cycle at a time) vs burst; watch CACHE COHERENCE.

INTERRUPT CYCLE: device raises IRQ -> CPU finishes instr -> SAVE state -> vector->ISR
  -> ISR moves data/clears int -> RESTORE state -> resume.  NMI = unmaskable.
  Linux: TOP half (fast, in ISR) + BOTTOM half (softirq/tasklet/workqueue, deferred).

BUFFER  = only copy, IN TRANSIT (speed/size mismatch, copy semantics).
  single buffer = no overlap; DOUBLE buffer = device fills A while CPU drains B, swap.
CACHE   = reusable DUPLICATE of data that lives elsewhere (page cache).
SPOOL   = disk queue for a NON-shareable device (PRINTER).

KERNEL I/O SUBSYSTEM (device-independent): I/O scheduling(=disk sched M12), buffering,
  caching, spooling, naming, protection(I/O instrs PRIVILEGED), error handling.

APP I/O MODELS:
  BLOCKING     sleeps until data (simple; 1 thread/conn -> C10k)
  NON-BLOCKING returns now / EAGAIN; poll readiness (select/poll/EPOLL)  -> READINESS
  ASYNC        returns now; kernel does it; notify on done (io_uring/IOCP)-> COMPLETION

LAYERS: user read()/write() -> device-INDEPENDENT kernel I/O -> DRIVERS(device-specific)
  -> interrupt handlers -> hardware.  "Everything is a file" (/dev,/proc,/sys).

BACKEND BRIDGE (M20): C10k -> epoll(readiness,O(ready)) -> io_uring(completion,SQ/CQ).
  sendfile/splice = zero-copy via DMA. HW polling/interrupt/DMA == SW block/epoll/uring.
```

### Flash cards

| Front | Back |
|-------|------|
| Four controller registers? | data-in, data-out, status, control |
| Memory-mapped vs port-mapped? | Shared mem addrs + MOV vs separate space + IN/OUT |
| Which technique busy-waits? | Programmed I/O (polling) |
| Interrupts per byte / per block? | Interrupt-driven (per byte) / DMA (per block) |
| DMA one-cycle-at-a-time mode? | Cycle stealing |
| DMA correctness worry? | Cache coherence |
| Block vs character device? | Disk (blocks, random) vs keyboard (byte stream) |
| Buffer vs cache? | Only copy, in transit vs reusable duplicate |
| Printer queue mechanism? | Spooling |
| Single vs double buffering? | No overlap vs fill A while drain B |
| Non-blocking signals…? async signals…? | Readiness vs completion |
| epoll vs io_uring? | Readiness (O(ready)) vs completion (SQ/CQ) |
| Which I/O layer is device-specific? | The device driver |

### Spaced repetition
- **24-hour:** reproduce the polling/interrupt/DMA comparison table (who moves data,
  interrupt count, CPU cost) and the blocking/non-blocking/async table from memory.
- **7-day:** explain DMA cycle stealing + "one interrupt per block"; buffer vs cache vs
  spool; memory-mapped vs port-mapped; block vs character devices.
- **30-day:** given "a server must handle 100k connections," walk from blocking →
  epoll (readiness) → io_uring (completion), and connect it to hardware
  polling/interrupts/DMA.

---

## 13.16 Summary

The I/O system is the OS's answer to the **nanosecond CPU vs millisecond device**
mismatch. The CPU never touches hardware directly: it drives **controller registers**
(data-in/out, status, control) over a shared **bus**, addressed by **memory-mapped**
(shared addresses, `MOV`, uncached) or **port-mapped** (`IN`/`OUT`) I/O, through a
**device driver** that hides each controller behind a uniform interface (with **block**
vs **character** device classes). The three ways to move data rank by CPU cost:
**programmed I/O (polling)** busy-waits the CPU; **interrupt-driven I/O** frees the CPU
but costs **one interrupt per byte/word**; and **DMA** offloads the whole block for
**one interrupt per block** (via **cycle stealing**, with a **cache-coherence** catch).
Around this, the kernel provides **buffering** (single vs **double** to overlap I/O and
compute), **caching** (reusable copies), and **spooling** (disk queue for the printer),
plus **I/O scheduling**, naming, protection, and error handling. From the app's side,
I/O is **blocking**, **non-blocking** (signals **readiness**), or **asynchronous**
(signals **completion**) — the exact distinction that scales a backend from one thread
per connection to **epoll** and **io_uring**.

Next, **Module 14 — Linux Internals** grounds all of this in one real kernel: how Linux
actually implements processes, scheduling, memory, the VFS, and this very I/O stack
(drivers, `/dev`, softirqs, epoll, io_uring) in production code.

> **You have mastered this module when** you can: draw the CPU–controller–bus picture
> and name the four registers; contrast memory-mapped vs port-mapped I/O; reproduce the
> polling vs interrupt vs DMA table with CPU costs and interrupt counts; explain DMA
> cycle stealing and "one interrupt per block"; separate buffering, caching, and
> spooling (and single vs double buffering); and distinguish blocking, non-blocking
> (readiness), and asynchronous (completion) I/O — connecting them to epoll/io_uring —
> all without notes.
