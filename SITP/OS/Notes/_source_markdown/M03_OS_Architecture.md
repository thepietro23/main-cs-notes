---
title: "Module 3 — Operating System Architecture"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — Operating System Architecture

> **Where this module sits.**
> Module 1 said *what* an OS is; Module 2 laid out the *hardware* it manages. Now
> we look at the **shape of the OS itself**: how its code is organised (**kernel
> architectures** — monolithic, microkernel, hybrid, modular, exokernel; the
> **layered** model), the hardware-enforced wall between **user space and kernel
> space** (**dual mode**), the **system call** — the one door programs use to ask
> the kernel for anything — and the **boot process** that brings the whole thing to
> life from power-on. This is the scaffolding for everything after: processes (M4)
> run in user space, make **system calls** into the kernel; drivers (M12) are
> kernel or user modules depending on the architecture; Linux internals (M14) are a
> deep dive into the *monolithic-modular* design introduced here.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★     | ★★★★      | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **monolithic vs
microkernel** (pros/cons, examples) — near-guaranteed; **hybrid** kernels
(Windows/macOS); **layered** design (THE system); **kernel vs user mode** and the
**mode bit / dual mode**; **mode switch vs context switch**; **system calls**
(mechanism = trap, examples like `fork/exec/open/read`, categories, **syscall vs
library call**, **API**); the **boot process** (**BIOS vs UEFI**, **POST**,
**bootloader/GRUB**, kernel loading, **init/systemd**).

---

## 3.1 Kernel vs User Space, and Dual-Mode Operation (start here)

The **kernel** is the always-resident core of the OS that has **full control of the
hardware**. To stop a buggy or malicious program from crashing the machine, the CPU
provides **two modes**, selected by a **mode bit** in the status register (M2's
PSW):

- **User mode (bit = 1):** normal programs run here. **Privileged instructions**
  (halt the CPU, set the timer, do raw I/O, change page tables, switch mode) are
  **forbidden** — attempting one traps to the kernel.
- **Kernel mode (bit = 0):** the kernel runs here with **full privileges** — all
  instructions and all memory allowed.

![Two rings: user-space processes run with limited privilege; a system call traps across the boundary into kernel space, which alone touches hardware, then returns.](images/17_user_kernel_mode.png)

Correspondingly, memory is split into **user space** (where processes live) and
**kernel space** (the kernel's protected memory). A user process **cannot read or
write kernel space** directly — it must ask via a **system call**.

> **Memory hook:** **user mode = the public lobby; kernel mode = the vault.** The
> only way from lobby to vault is the **system-call teller window** — you hand over
> a request, staff (kernel) go inside and do it for you.

> **Mode switch vs context switch (classic confusion):**
> - **Mode switch** = the *same* process crosses **user → kernel** (and back) on a
>   system call/interrupt. **Cheap** — no scheduler, no change of process.
> - **Context switch** = the CPU is handed from **one process to another** (save
>   all of A's registers, load B's). **More expensive**; involves the scheduler
>   (M6). A mode switch does **not** imply a context switch.

### MCQs

1. What selects user vs kernel mode? → the **mode bit** in the PSW.
2. Can a user program run privileged instructions? → **no** (it traps).
3. Mode switch vs context switch? → **user↔kernel in same process** vs **swap to a
   different process**.
4. Which is cheaper? → a **mode switch**.

---

## 3.2 System Calls — The Only Door Into the Kernel

A **system call** is a program's request for a service the OS alone can perform
(create a process, open a file, send on a socket). It is the **controlled entry
point** across the user→kernel boundary from §3.1.

### 3.2.1 The mechanism (how a system call actually works)

![A system call: the library wrapper sets a call number and args, executes a trap; the CPU switches to kernel mode, the dispatcher runs the handler via the syscall table, then returns to user mode.](images/18_syscall_flow.png)

```text
1. User program calls a library wrapper, e.g. read(fd, buf, n)   (in libc).
2. Wrapper puts the SYSCALL NUMBER in a register + arguments in registers.
3. Executes a TRAP instruction (syscall / int 0x80 / svc) --> SOFTWARE INTERRUPT.
4. CPU switches USER -> KERNEL mode, jumps to the fixed syscall entry point.
5. Kernel's DISPATCHER indexes the SYSCALL TABLE by the number -> runs the handler.
6. Handler does the work (checks args/permissions, touches hardware).
7. Return value placed in a register; CPU switches KERNEL -> USER; wrapper returns.
```

The **trap** is the key: a system call is a **software interrupt** (M2 §2.4) — the
program deliberately traps into the kernel. Arguments too big for registers are
passed in a **block/table** whose address is passed, or on the stack.

> **Memory hook:** a system call is **ordering at a restaurant**: you (user) don't
> walk into the kitchen (kernel). You hand a numbered order (**syscall number +
> args**) through the pass (**trap**); the kitchen cooks it and hands the plate
> back (**return value**).

### 3.2.2 Categories of system calls (with examples)

| Category | What it does | Examples (POSIX/Linux) |
|----------|--------------|------------------------|
| **Process control** | create/end/wait/load programs | `fork`, `exec`, `wait`, `exit`, `kill` |
| **File management** | create/open/read/write/close | `open`, `read`, `write`, `close`, `lseek` |
| **Device management** | request/release/use devices | `ioctl`, `read`, `write`, `mmap` |
| **Information maintenance** | get/set system data | `getpid`, `time`, `gettimeofday`, `alarm` |
| **Communication** | messaging, shared memory, sockets | `pipe`, `shmget`, `socket`, `send`, `recv` |
| **Protection** | permissions, access control | `chmod`, `umask`, `chown` |

A tiny but complete example (creating a new process and running a program):

```c
pid_t pid = fork();          /* process control: duplicate the process   */
if (pid == 0) {              /* child                                     */
    execlp("ls", "ls", NULL);/* process control: replace image with ls   */
} else {                     /* parent                                    */
    wait(NULL);              /* process control: wait for child to finish */
}
```

### 3.2.3 System call vs library call vs API (a favourite distinction)

- **System call:** a **direct request to the kernel** via a trap (`read`, `write`,
  `fork`). Involves a **mode switch** — relatively expensive.
- **Library (function) call:** ordinary code in **user space** (`strlen`, `printf`,
  `malloc`). No kernel involvement *by itself* — though it **may** make system calls
  underneath (`printf` eventually calls `write`; `malloc` may call `brk`/`mmap`).
- **API (Application Programming Interface):** the **specification** of functions a
  programmer uses (e.g. **POSIX**, the **Win32 API**). Programmers code to the API;
  the library implements it, invoking system calls as needed. **You rarely invoke
  the raw trap yourself** — you call the API, the library wraps the syscall.

> **The exam line:** **`printf` is a library call; `write` is the system call it
> uses.** An **API is the interface (contract); a system call is the actual kernel
> entry**. Programs are portable across the same API even if the underlying
> syscalls differ.

### MCQs

1. A system call reaches the kernel via a? → **trap (software interrupt)**.
2. `printf` vs `write`? → **library call** vs **system call**.
3. `fork`, `exec`, `wait` belong to which category? → **process control**.
4. What indexes the correct handler? → the **syscall number** into the **syscall
   table**.
5. POSIX / Win32 are examples of? → an **API** (interface, not the syscall itself).

---

## 3.3 Kernel Architectures — How the OS Is Structured

Where should OS services (scheduler, memory manager, file system, drivers, network
stack) live — **all inside the kernel**, or **outside as user processes**? That one
question defines the kernel architectures. It is the highest-yield conceptual topic
in this module.

![Monolithic keeps all services in one kernel address space; microkernel keeps only essentials in the kernel and runs services as user processes talking via IPC; hybrid puts performance-critical services back in the kernel.](images/19_kernel_architectures.png)

### 3.3.1 Monolithic kernel

**All** OS services (scheduling, memory, file systems, drivers, networking) run
**together in one program in kernel space**, sharing one address space and calling
each other as fast function calls.

- **Pros:** **fast** (no messaging between services — direct calls); simple, mature.
- **Cons:** **large** and hard to maintain; a bug/driver crash **can take down the
  whole kernel**; less modular (though see *modular*, below).
- **Examples:** **Linux**, classic **UNIX**, BSD, MS-DOS.

### 3.3.2 Microkernel

Keep the kernel **minimal** — only the bare essentials: **IPC, basic scheduling,
and low-level address-space/memory management.** Everything else (file system,
drivers, network stack) runs as **separate user-space server processes** that
communicate by **message passing (IPC)**.

- **Pros:** **reliable & secure** — a crashed driver/service is just a user process
  the kernel can **restart**, not a kernel panic; **modular**; easier to verify;
  good for real-time.
- **Cons:** **slower** — every service request is **IPC + mode switches** instead of
  a function call (message-passing overhead).
- **Examples:** **Minix**, **QNX** (real-time), **L4**, **Mach** (research/base).

### 3.3.3 Hybrid kernel

A **pragmatic middle ground**: a microkernel-style structure, but performance-
critical services (drivers, file systems, graphics) are pulled **back into kernel
space** to avoid IPC cost. This is what most desktop OSes actually ship.

- **Pros:** balances the speed of monolithic with some modularity of microkernel.
- **Cons:** blurred boundaries; still large; "hybrid" is partly a marketing term.
- **Examples:** **Windows NT** family (Windows 10/11), **macOS** (**XNU** = Mach
  microkernel core + BSD monolithic parts + I/O Kit).

### 3.3.4 Modular kernel (loadable modules)

A monolithic kernel that can **load and unload code at runtime** as **modules**
(e.g. a driver or file system loaded on demand). Combines monolithic speed with
some flexibility — you don't recompile the kernel to add a driver.

- **Example:** **Linux** is best described as **monolithic + modular** — it loads
  **loadable kernel modules (LKMs)** with `insmod`/`modprobe`.

### 3.3.5 Exokernel (and unikernels — awareness level)

An **exokernel** does as **little abstraction as possible**: it only **securely
multiplexes the raw hardware**, and lets applications (linked with **library OSes**)
implement their own abstractions for maximum performance/customisation.

- **Pro:** apps get near-hardware performance and can tailor policies. **Con:** far
  more work pushed to applications; research/niche. (A modern cousin: **unikernels**
  — a single app + minimal library OS compiled into one image.)

### 3.3.6 Comparison table (memorise this)

| Feature | Monolithic | Microkernel | Hybrid |
|---------|-----------|-------------|--------|
| Services in kernel | **all** | **minimal** (rest in user space) | most **critical** ones |
| Communication | function calls (fast) | **IPC / messages** (slower) | mix |
| Speed | **fast** | slower (IPC overhead) | fast-ish |
| Reliability / isolation | driver crash → **kernel down** | crash = restartable **user process** | in between |
| Size / complexity in kernel | large | **small** | large |
| Extensibility | modules | services as processes | modules + services |
| Examples | **Linux**, UNIX, BSD | **Minix, QNX, L4, Mach** | **Windows NT, macOS (XNU)** |

> **The #1 exam trade-off (say it out loud):** **monolithic = fast but fragile**
> (everything in one address space, a driver bug can crash the kernel);
> **microkernel = robust but slower** (services are isolated user processes, but
> every request costs **IPC**). **Hybrid** trades a little isolation back for speed.

> **Memory hook:** **monolithic = open-plan office** (everyone in one room, fast
> shouting, one fire spreads everywhere). **microkernel = separate locked rooms**
> (safe, but you must send memos = IPC). **hybrid = mostly rooms, but the busy
> teams share one room** for speed.

### MCQs

1. Where do drivers run in a **microkernel**? → in **user space** (as server
   processes).
2. Why is a monolithic kernel **fast**? → services call each other **directly** (no
   IPC).
3. Why is a microkernel **more reliable**? → a crashed service is a **restartable
   user process**, not a kernel panic.
4. Classify Linux, QNX, Windows NT. → **monolithic (modular)**, **microkernel**,
   **hybrid**.
5. macOS's kernel is called? → **XNU** (Mach + BSD, hybrid).
6. Which architecture does the *least* abstraction? → **exokernel**.

---

## 3.4 The Layered Architecture

Instead of by *where code runs*, an OS can be organised by **layers**: each layer
**uses only the layer directly below it** and offers services to the one above.
Layer 0 is the hardware; the top layer is the user interface.

```text
   Layer N   : user interface / applications
     ...
   Layer 2   : device drivers / I/O
   Layer 1   : CPU scheduling / memory management
   Layer 0   : HARDWARE
```

- **Pros:** **modular**, easy to **debug and verify** one layer at a time (if lower
  layers are correct, you only test the new layer); clean abstraction.
- **Cons:** **hard to define the layers** cleanly (which layer owns what?);
  **performance overhead** — a request may pass through many layers.
- **Classic example:** **THE** operating system (Dijkstra, 1968) — the textbook
  layered design.

> **Memory hook:** layered OS = a **wedding cake** — each tier rests only on the
> one below; clean, but a message from top to hardware traverses every tier.

### MCQs

1. In a layered OS, a layer may call? → **only the layer directly below it**.
2. Main drawback of strict layering? → **performance overhead** + hard to define
   layers.
3. The classic layered OS example? → **THE** (Dijkstra).

---

## 3.5 The Boot Process — From Power-On to Login

When you press power, there is **no OS in RAM yet** — so how does the OS load
itself? By a chain of ever-larger loaders, each starting the next
("**bootstrapping**", pulling yourself up by your bootstraps).

![Boot sequence: firmware (BIOS/UEFI) runs POST, hands off to the bootloader (GRUB), which loads the kernel; the kernel initialises hardware and starts init/systemd (PID 1), which brings up user space.](images/20_boot_process.png)

```text
POWER ON
  1. FIRMWARE (BIOS or UEFI) runs from ROM/flash.
  2. POST (Power-On Self-Test): check RAM, CPU, keyboard, disks.
  3. Firmware finds the boot device and loads the BOOTLOADER.
        BIOS : reads the 512-byte MBR (first sector)  -> stage-1 loader.
        UEFI : reads a .efi bootloader from the EFI System Partition (GPT).
  4. BOOTLOADER (e.g. GRUB) shows the menu, loads the KERNEL (+ initrd) into RAM.
  5. KERNEL initialises: sets up memory, drivers, mounts the root filesystem.
  6. Kernel starts the first user process: INIT / systemd  (PID 1).
  7. init/systemd starts services (daemons), reaches a target/runlevel, spawns login.
  READY: login prompt / desktop.
```

### 3.5.1 BIOS vs UEFI (high-yield comparison)

| | **BIOS** (legacy) | **UEFI** (modern) |
|---|---|---|
| Age / mode | old, **16-bit** real mode | modern, **32/64-bit** |
| Boot data | **MBR** (Master Boot Record, 512 B) | **GPT** + **EFI System Partition** (`.efi`) |
| Disk size limit | **≤ 2 TB** (MBR) | **> 2 TB** (GPT) |
| Partitions | up to 4 primary | many |
| Speed / features | slower | **faster boot**, **Secure Boot**, GUI, network boot |

> **Memory hook:** **BIOS = MBR (old, 2 TB cap, 16-bit); UEFI = GPT + EFI partition
> (modern, >2 TB, Secure Boot).**

### 3.5.2 Key players

- **POST** — the firmware's hardware self-check before anything loads.
- **Bootloader (GRUB / GRUB2, Windows Boot Manager):** loads and hands control to
  the kernel; on Linux it also loads the **initrd/initramfs** (a tiny temporary root
  FS with drivers needed to mount the real root).
- **Kernel loading:** the kernel decompresses, sets up memory management and core
  drivers, then mounts the root filesystem.
- **`init` / `systemd` (PID 1):** the **first user-space process**, ancestor of all
  others. Traditional **SysV init** used **runlevels** and shell scripts;
  **systemd** (today's default on most Linux) uses **units** and **targets**, starts
  services **in parallel** (faster boot), and manages daemons.

> **Exam nuggets:** **PID 1 = init/systemd**, the ancestor of every process. The
> **MBR is 512 bytes** and holds the stage-1 bootloader; **GPT** replaces it under
> UEFI. **initrd/initramfs** exists so the kernel has the drivers to mount the real
> root filesystem.

### MCQs

1. What runs first at power-on? → the **firmware (BIOS/UEFI)** from ROM/flash.
2. POST checks? → **basic hardware** (RAM, CPU, devices).
3. BIOS boot record vs UEFI? → **MBR (512 B)** vs **GPT + EFI System Partition**.
4. GRUB is a? → **bootloader**.
5. First user-space process / PID 1? → **init / systemd**.
6. Why does Linux use an **initrd/initramfs**? → to carry **drivers needed to mount
   the real root** filesystem.

---

## 3.6 Real-World & Backend Perspectives

- **Linux is monolithic-modular, and that's why it's fast:** drivers and file
  systems are **loadable modules** (`lsmod`, `modprobe`), so you extend the kernel
  without a reboot-recompile, keeping the speed of in-kernel function calls.
- **The syscall boundary is where performance and security meet:** minimising
  syscalls (batching, `io_uring`, `readv`/`writev`) cuts mode-switch overhead;
  **seccomp** restricts which syscalls a process may make (container hardening).
- **Containers vs microkernels:** containers share the **host's monolithic Linux
  kernel** (isolation via namespaces/cgroups), which is why they're lightweight —
  contrast with a microkernel's process-level isolation or a VM's full guest kernel.
- **systemd runs your servers:** production services are **systemd units**
  (`systemctl start/status`, journald logs); understanding PID 1 and targets is
  everyday backend/DevOps work.
- **eBPF** lets you safely run sandboxed programs *inside* the Linux kernel — a
  modern way to extend a monolithic kernel without new modules.

---

## 3.7 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** "microkernel is faster because it's smaller." **No** — smaller kernel,
  but **slower** due to **IPC** between services. It wins on **reliability**, not
  speed.
- **Mistake:** calling Linux a microkernel. Linux is **monolithic (modular)**;
  **Minix/QNX** are microkernels.
- **Mistake:** confusing **mode switch** (user↔kernel, cheap) with **context
  switch** (process→process, costly).
- **Mistake:** `printf` is a system call. **No** — it's a **library call** that
  *uses* the `write` system call.
- **Mistake:** BIOS uses GPT / UEFI uses MBR — it's the **reverse** (BIOS→MBR,
  UEFI→GPT).
- **Edge case:** a hybrid kernel is not a clean category — Windows/macOS mix designs
  for pragmatism.
- **Tradeoff:** in-kernel drivers (speed, but a bug crashes the kernel) vs
  user-space drivers (isolation, but IPC overhead) — the monolithic/microkernel
  divide in miniature.

---

## 3.8 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** monolithic vs microkernel (pros/cons/examples),
  kernel vs user mode, system-call basics, BIOS vs UEFI, PID 1 = init/systemd.
- **GATE:** the mode bit / privileged instructions; syscall mechanism (trap);
  layered vs monolithic; the microkernel IPC trade-off.
- **Interview:** "What happens when you call `read()`?" (library wrapper → trap →
  kernel mode → syscall table → handler → return); "Monolithic vs microkernel — why
  is Linux monolithic?"; "What happens from power button to login?" (the boot
  chain).
- **Coding/practical:** `strace ./prog` shows the exact system calls a program
  makes; `lsmod`/`modprobe` list/load kernel modules; `systemctl` and `dmesg`
  inspect boot/services; `uname -a` shows the kernel.

---

## 3.9 Concept Checks & MCQs (test yourself)

1. Two CPU modes and the bit that selects them? → **user/kernel**, the **mode bit**.
2. Can user mode run privileged instructions? → **no** (traps to kernel).
3. Mode switch vs context switch? → **user↔kernel (same process)** vs **process→
   process**.
4. A system call enters the kernel via? → a **trap (software interrupt)**.
5. `fork/exec/wait` category? → **process control**.
6. `printf` vs `write`? → **library call** vs **system call**.
7. API means? → the **interface/specification** (POSIX, Win32), not the syscall.
8. Monolithic pros/cons? → **fast**, but a bug can **crash the whole kernel**.
9. Microkernel pros/cons? → **reliable/isolated**, but **slower (IPC)**.
10. Classify Linux / QNX / Windows NT / macOS. → **monolithic-modular /
    microkernel / hybrid / hybrid (XNU)**.
11. Exokernel's philosophy? → **minimal abstraction**, securely multiplex raw
    hardware.
12. Layered OS rule and example? → each layer uses **only the one below**; **THE**.
13. What runs first at power-on? → **firmware (BIOS/UEFI)**; then **POST**.
14. BIOS vs UEFI boot data? → **MBR** vs **GPT + EFI System Partition**.
15. Bootloader example? → **GRUB**.
16. PID 1? → **init / systemd**.
17. Why an initrd/initramfs? → drivers to **mount the real root** filesystem.
18. Where do containers get isolation? → the **host's monolithic kernel**
    (namespaces/cgroups), not a separate kernel.

**True/False**
- A microkernel is faster than a monolithic kernel. → **False** (more reliable, but
  slower due to IPC).
- Linux is a microkernel. → **False** (monolithic + modular).
- A system call requires a mode switch. → **True**.
- `printf` is a system call. → **False** (library call using `write`).
- UEFI uses the MBR. → **False** (UEFI uses GPT).
- init/systemd is PID 1. → **True**.

---

## 3.10 One-Page Revision Sheet

```
DUAL MODE: MODE BIT (in PSW) -> USER(limited, no privileged instr) vs KERNEL(full power).
  memory split: USER SPACE (processes) | KERNEL SPACE (protected). cross only via SYSCALL.
  MODE SWITCH = user<->kernel, SAME process (cheap) ; CONTEXT SWITCH = process->process (costly).

SYSTEM CALL = program's request to kernel. MECHANISM:
  libc wrapper -> put syscall NUMBER + args in registers -> TRAP (software interrupt)
  -> kernel mode -> DISPATCHER indexes SYSCALL TABLE -> handler -> return value -> user mode.
  CATEGORIES: process control(fork,exec,wait,exit) | file(open,read,write,close) |
    device(ioctl,mmap) | info(getpid,time) | comms(pipe,socket,shmget) | protection(chmod).
  SYSCALL vs LIBRARY vs API: syscall=kernel trap ; library=user code(printf,malloc, may call
    syscalls); API=the interface/spec (POSIX, Win32).  "printf=library, write=syscall".

KERNEL ARCHITECTURES:
  MONOLITHIC : ALL services in kernel, direct calls -> FAST but a bug crashes kernel.
               Linux, UNIX, BSD.  (Linux also MODULAR: loadable kernel modules.)
  MICROKERNEL: only IPC+sched+basic mem in kernel ; drivers/FS/net = USER processes via IPC
               -> RELIABLE/isolated but SLOWER (IPC). Minix, QNX, L4, Mach.
  HYBRID     : microkernel-ish + critical services back in kernel for speed. Windows NT,
               macOS (XNU = Mach + BSD).
  EXOKERNEL  : minimal abstraction, securely multiplex raw hardware (+ library OS). niche.
  TRADE-OFF: monolithic FAST/fragile ; microkernel ROBUST/slower(IPC) ; hybrid = balance.

LAYERED: each layer uses only the one below (0=hardware, top=UI). easy to verify, but
  overhead + hard to partition. Example: THE (Dijkstra).

BOOT: POWER -> FIRMWARE(BIOS/UEFI from ROM) -> POST(hw self-test) -> BOOTLOADER
  (BIOS: MBR 512B ; UEFI: .efi on EFI partition, GPT) -> GRUB loads KERNEL(+initrd)
  -> kernel init (mem, drivers, mount root) -> INIT/systemd = PID 1 -> services -> login.
  BIOS: MBR, 16-bit, <=2TB. UEFI: GPT, >2TB, Secure Boot, faster.  initrd=drivers to mount root.
```

### Flash cards

| Front | Back |
|-------|------|
| What selects user/kernel mode? | The mode bit (in the PSW) |
| Mode switch vs context switch? | User↔kernel (same proc) vs proc→proc |
| System call mechanism? | Trap (software interrupt) into kernel |
| `printf` vs `write`? | Library call vs system call |
| What is an API? | The interface/spec (POSIX, Win32) |
| `fork/exec/wait`? | Process-control system calls |
| Monolithic: pro/con? | Fast / a bug crashes the kernel |
| Microkernel: pro/con? | Reliable / slower (IPC) |
| Linux kernel type? | Monolithic + modular |
| Minix, QNX? | Microkernel |
| Windows NT, macOS? | Hybrid (macOS = XNU) |
| Exokernel idea? | Minimal abstraction, multiplex hardware |
| Layered example? | THE (Dijkstra) |
| First code at power-on? | Firmware (BIOS/UEFI), then POST |
| BIOS vs UEFI boot data? | MBR vs GPT + EFI partition |
| Bootloader example? | GRUB |
| PID 1? | init / systemd |

### Spaced repetition
- **24-hour:** recite monolithic vs microkernel vs hybrid (pros/cons/examples) and
  the syscall mechanism.
- **7-day:** trace `read()` end-to-end (wrapper → trap → table → handler → return);
  BIOS vs UEFI; syscall categories.
- **30-day:** draw the boot chain from power-on to login; explain dual mode, mode vs
  context switch, and the layered model without notes.

---

## 3.11 Summary

An OS enforces a hardware wall between **user space** (limited) and **kernel space**
(full power), chosen by the **mode bit** — and a program crosses it only through a
**system call**, a **trap (software interrupt)** that switches to kernel mode, runs
a handler via the **syscall table**, and returns. We separated the **system call**
(kernel trap), the **library call** (`printf`, user code that *uses* syscalls), and
the **API** (the interface/spec like POSIX). The OS's own code can be shaped as a
**monolithic** kernel (all services in one address space — **fast but fragile**,
e.g. **Linux**), a **microkernel** (essentials only; services as isolated user
processes over **IPC** — **robust but slower**, e.g. **Minix/QNX**), a **hybrid**
(the pragmatic mix — **Windows NT, macOS/XNU**), **modular** (Linux's loadable
modules), or an **exokernel** (minimal abstraction). The **layered** model (e.g.
**THE**) stacks services, each using only the layer below. Finally, the **boot
process** bootstraps the machine: **firmware (BIOS/UEFI)** → **POST** →
**bootloader (GRUB)** loading the **kernel** → **init/systemd (PID 1)** bringing up
user space.

Next, **Module 4 — Processes** builds directly on the syscalls (`fork`, `exec`,
`wait`) and user/kernel boundary introduced here, defining the process, its states,
and the PCB the kernel uses to manage it.

> **You have mastered this module when** you can: explain dual mode and the mode bit,
> and distinguish mode switch from context switch; trace a system call end-to-end and
> tell syscall / library call / API apart with examples; compare monolithic,
> microkernel, hybrid, modular, and exokernel designs (pros/cons/examples) and
> classify Linux/QNX/Windows/macOS; describe the layered model; and walk the full
> boot process (BIOS vs UEFI, POST, GRUB, kernel, init/systemd) — all without notes.
