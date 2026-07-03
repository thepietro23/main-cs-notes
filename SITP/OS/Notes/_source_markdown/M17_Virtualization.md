---
title: "Module 17 — Virtualization & Containers"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 17 — Virtualization & Containers

> **Where this module sits.**
> Module 1 introduced the **hypervisor** in one line; Modules 4–5 taught
> **processes and threads**; Module 9–10 taught **virtual memory**; and Module 14
> (Linux internals) taught **namespaces and cgroups**. This module ties them
> together into the two technologies that run the entire modern cloud: **virtual
> machines** (one physical box pretends to be many computers) and **containers**
> (one OS kernel pretends to be many isolated OSes). Virtualization *is* an
> operating-system idea taken one level up — instead of an OS sharing a CPU among
> **processes**, a hypervisor shares the **hardware** among whole **guest OSes**.
> Everything in **Module 18 — Cloud Operating Systems** is built on what you learn
> here.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★    | ★★      | ★★★★★     | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** definition & benefits of
**virtualization**; **Type-1 vs Type-2 hypervisor** (bare-metal vs hosted, with
examples); **full vs para-virtualization**; **hardware-assisted virtualization
(Intel VT-x / AMD-V)** and **trap-and-emulate**; **VM vs container** (the single
most common modern MCQ — "which shares the host kernel?"); **Docker image vs
container**, **image layers / union file system**, **Dockerfile**; **cgroups vs
namespaces** (limits vs isolation); **Kubernetes** pod / node / control plane and
why orchestration is needed.

---

## 17.1 What Is Virtualization — and Why? (first principles)

### The problem

A physical server is bought for its **peak** load but sits **idle** most of the
time — a classic data-centre server runs at **10–15% average CPU utilisation**.
Running one application per physical box therefore **wastes ~85% of the hardware**,
plus its power, cooling, and rack space. We also want to run **many different OSes**
(Windows, Linux, old and new) on one machine, keep them **isolated** so one crash
or hack can't touch the others, and **move a whole running system** from one box to
another. A raw OS cannot do this — it assumes it *owns* the machine.

### The idea

**Virtualization** is the creation of a **software illusion of hardware** (or of an
OS) so that **several isolated systems share one physical machine**, each believing
it has the machine to itself. The software that creates this illusion for whole
operating systems is the **hypervisor** (also called a **Virtual Machine Monitor,
VMM**).

> **Memory hook:** an OS shares **one CPU among many processes**; a **hypervisor**
> shares **one physical machine among many whole OSes**. Same trick — *time-share a
> resource and give each user the illusion of owning it* — just one floor higher.

### Why it matters (benefits)

- **Consolidation / higher utilisation** — pack many under-used servers onto one
  box (the original business case; drives cloud economics).
- **Isolation** — each VM is a sealed sandbox; a crash, virus, or reboot in one VM
  does not affect the others.
- **Hardware independence & portability** — a VM is just files; you can **snapshot**,
  **clone**, and **live-migrate** it to another physical host with no downtime.
- **Flexibility** — run any OS on any hardware; spin up/tear down machines in
  seconds (the foundation of "rent a server by the minute").
- **Efficiency & cost** — fewer physical machines → less power, cooling, and space.

### MCQs

1. Software that lets one machine run many guest OSes? → **hypervisor / VMM**.
2. One-line benefit that started it all? → **server consolidation** (higher
   utilisation).
3. Moving a running VM to another host with no downtime is called? → **live
   migration**.

---

## 17.2 The Virtual Machine and the Hypervisor

A **virtual machine (VM)** is a software computer: it has a **virtual CPU, virtual
RAM, virtual disk, and virtual network card**, all backed by slices of the real
hardware. Inside it runs a complete, unmodified **guest OS** and its apps, which
believe they are on a real machine.

The **hypervisor** is the thin layer that:

1. **partitions** the real CPU, memory, and devices among the VMs,
2. **schedules** virtual CPUs onto real CPUs (just as an OS schedules threads),
3. **isolates** each VM, and
4. **traps** any operation a guest tries that would affect real hardware and
   **emulates** it safely.

> **The three rules a VMM must satisfy (Popek & Goldberg, 1974 — a classic exam
> line):**
> - **Equivalence / fidelity** — a program runs in the VM *the same* as on real
>   hardware.
> - **Resource control / safety** — the VMM has *complete* control of the real
>   resources; a guest can never bypass it.
> - **Efficiency** — *most* guest instructions run **directly on the real CPU** with
>   no VMM intervention (otherwise it would be an emulator, not a virtualizer).

> **Emulation vs virtualization (don't confuse them):** an **emulator** (e.g. QEMU
> running ARM code on an x86 laptop) *interprets/translates every instruction* — slow
> but can fake *different* hardware. **Virtualization** runs the guest on the **same**
> CPU architecture, executing most instructions **natively** — fast.

### MCQs

1. The three Popek–Goldberg requirements? → **equivalence, resource control,
   efficiency**.
2. VM vs emulator key difference? → a VM runs guest code **natively on the same
   CPU**; an emulator **translates every instruction**.

---

## 17.3 Type-1 vs Type-2 Hypervisors

Hypervisors come in two shapes depending on **where they sit**.

![Type-1 runs directly on hardware (servers, cloud, faster); Type-2 runs as an app on top of a host OS (desktops, testing).](images/164_hypervisor_types.png)

- **Type-1 (bare-metal / native):** the hypervisor runs **directly on the
  hardware**; guest OSes run on top of it. There is **no host OS** underneath.
  Fastest and most secure — the standard for **servers and cloud data centres**.
  **Examples:** VMware **ESXi**, Microsoft **Hyper-V**, **Xen**, **KVM** (KVM turns
  the Linux kernel *itself* into a Type-1 hypervisor).
- **Type-2 (hosted):** the hypervisor runs as an **ordinary application inside a
  host OS** (Windows/macOS/Linux). Easy to install on a laptop; slower because guest
  operations pass through the **extra host-OS layer**. Great for **desktops, dev,
  and testing**. **Examples:** Oracle **VirtualBox**, **VMware Workstation/Player**,
  **QEMU** (hosted mode), Parallels.

| | Type-1 (bare-metal) | Type-2 (hosted) |
|---|---|---|
| Runs on | **hardware directly** | **inside a host OS** (as an app) |
| Host OS below it | **none** | **yes** (Windows/macOS/Linux) |
| Speed | **faster** (one fewer layer) | slower (extra layer) |
| Isolation/security | stronger | weaker |
| Typical use | **servers, cloud** | **laptops, testing** |
| Examples | ESXi, Hyper-V, Xen, KVM | VirtualBox, VMware Workstation |

> **Memory hook:** **Type-1 = "type won" = on the metal, wins on speed** (cloud).
> **Type-2 = "two layers" = hypervisor on top of a host OS** (your laptop).

> **KVM edge case (interview favourite):** KVM is a Linux **kernel module**. Because
> the hypervisor *is* the kernel running on bare metal, KVM is classed as **Type-1**,
> even though Linux can also run normal apps. This blurring is why the strict "1 vs
> 2" line is a bit academic — but exams still want **bare-metal vs hosted**.

### MCQs

1. Type-1 vs Type-2? → runs on **hardware directly** vs **inside a host OS**.
2. Give three Type-1 examples. → **ESXi, Hyper-V, Xen, KVM** (any three).
3. VirtualBox is Type-? → **Type-2 (hosted)**.
4. Which is faster and why? → **Type-1** — no extra host-OS layer to cross.

---

## 17.4 How Virtualization Actually Works (the deep part)

To satisfy **equivalence + control + efficiency**, the VMM must let safe guest
instructions run natively but **intercept** the dangerous ones (those that touch
real hardware or change privilege). There are four techniques; exams love comparing
them.

### 17.4.1 Trap-and-emulate (the classic mechanism)

The guest OS *thinks* it runs in **kernel mode**, but the VMM actually runs it in
**user mode** (this is **deprivileging**). When the guest executes a **privileged
instruction** (e.g. disable interrupts, load the page-table register), the CPU
**traps** into the VMM, which **emulates** the instruction's effect on the *virtual*
hardware and returns. Ordinary (unprivileged) instructions run **directly on the
CPU** at full speed.

```text
guest user app     ── runs natively ──────────────►  real CPU
guest OS kernel    ── privileged instruction ──► TRAP ──► VMM emulates ──► return
```

> **Popek–Goldberg theorem (why x86 was "not virtualizable"):** trap-and-emulate
> works *only if* every **sensitive** instruction (one that touches real resources)
> is also a **privileged** instruction (one that traps in user mode). Old **x86 had
> ~17 sensitive-but-not-privileged instructions** (e.g. `POPF`) that **silently
> failed instead of trapping** — so pure trap-and-emulate was impossible. Two
> software fixes (17.4.2–17.4.3) and one hardware fix (17.4.4) were invented.

### 17.4.2 Full virtualization via binary translation (VMware's original trick)

The guest OS runs **completely unmodified**. The VMM **scans the guest kernel code
just before it runs** and **rewrites** the troublesome sensitive instructions
on-the-fly into safe sequences that call the VMM (**dynamic binary translation**).
User-mode code still runs natively. Pioneered by **VMware** in the late 1990s.

- **Pro:** any OS runs as-is (great compatibility). **Con:** translation overhead.

### 17.4.3 Para-virtualization (Xen's trick)

The guest OS is **modified**: the sensitive instructions are replaced with explicit
**hypercalls** (like a system call, but into the hypervisor). The guest *knows* it
is virtualized and cooperates.

- **Pro:** low overhead (no trapping/translation guesswork). **Con:** you must
  **change the guest OS** — impossible for closed-source OSes without vendor help.
  Popularised by **Xen**.

> **One-line contrast:** **full virtualization = guest is fooled (unmodified);
> para-virtualization = guest cooperates (modified with hypercalls).**

### 17.4.4 Hardware-assisted virtualization (Intel VT-x / AMD-V) — today's default

Around 2005–2006, Intel (**VT-x**) and AMD (**AMD-V**) added CPU support that makes
trap-and-emulate work **without** binary translation or guest modification. They add
a new **root mode (for the VMM)** and **non-root mode (for the guest)**, each with
its own rings 0–3, plus a hardware **VMCS** (VM Control Structure) that defines
exactly which guest events cause a **VM exit** into the VMM. Sensitive instructions
now trap cleanly in hardware.

- **Second-generation extended/nested page tables** — **EPT** (Intel) / **RVI/NPT**
  (AMD) — let the CPU translate **guest-virtual → guest-physical → host-physical**
  addresses in hardware, removing the huge cost of the VMM maintaining "shadow page
  tables." (This ties directly to **M9/M10 paging** — it is *two levels* of the same
  translation you already learned.)
- **Result:** modern hypervisors (KVM, ESXi, Hyper-V, Xen HVM) use hardware
  assistance; guests run unmodified and nearly at native speed.

| Technique | Guest modified? | How sensitive instrs handled | Example |
|-----------|:---------------:|------------------------------|---------|
| **Trap-and-emulate** | no | trap on privileged instr (needs "clean" ISA) | classic mainframes |
| **Binary translation (full virt)** | **no** | VMM **rewrites** guest kernel code | early VMware |
| **Para-virtualization** | **yes** | guest calls **hypercalls** | Xen (PV) |
| **Hardware-assisted (VT-x/AMD-V)** | no | **CPU** traps via root/non-root + VMCS | KVM, ESXi, Hyper-V |

### MCQs

1. Trap-and-emulate: what runs the guest kernel in? → **user mode** (deprivileged);
   privileged instrs **trap** to the VMM.
2. Why was classic x86 "not virtualizable"? → some **sensitive instructions were
   not privileged** (didn't trap).
3. Full vs para-virtualization? → guest **unmodified** vs **modified (hypercalls)**.
4. Intel's and AMD's hardware support are called? → **VT-x** and **AMD-V**.
5. Hardware nested paging for VMs is called? → **EPT** (Intel) / **NPT/RVI** (AMD).

---

## 17.5 Containers vs Virtual Machines (the modern must-know)

A **container** takes virtualization one level higher. Instead of virtualizing the
**hardware** and running a **whole guest OS** per instance, a container virtualizes
the **operating system**: all containers **share the single host kernel** but each
gets its own **isolated view** of processes, files, network, and users.

![VMs give each instance a full guest OS on a hypervisor; containers share the host kernel through the container engine, so they are much lighter and start in milliseconds.](images/163_vm_vs_container.png)

| | Virtual Machine | Container |
|---|---|---|
| Virtualizes | **hardware** | the **OS (kernel)** |
| Guest OS | **one full OS per VM** | **none** — shares the host kernel |
| Isolated by | **hypervisor** | **namespaces + cgroups** (kernel features) |
| Size | **GBs** | **MBs** |
| Start time | **seconds** (full boot) | **milliseconds** |
| Density (per host) | tens | **hundreds–thousands** |
| Isolation strength | **strong** (hardware boundary) | weaker (shared kernel) |

> **Memory hook:** **A VM ships the whole house (its own OS); a container ships just
> the furniture (app + libs) and rents the shared foundation (the host kernel).**
> That is why a container is MBs and boots in milliseconds, while a VM is GBs and
> boots in seconds.

> **The single most common modern MCQ:** *"Which one shares the host OS kernel?"* →
> the **container** (a VM has its **own** kernel).

### MCQs

1. What does a container share that a VM does not? → the **host OS kernel**.
2. Why do containers start faster than VMs? → **no OS to boot** (share the running
   kernel).
3. Which gives stronger isolation? → the **VM** (hardware-level boundary).

---

## 17.6 How Containers Work — Namespaces + cgroups (tie to M14)

A container is **not a special object** in Linux — there is no "container" system
call. A container is simply a **normal process** wrapped in two kernel features you
met in Module 14, plus a layered filesystem (17.7):

- **Namespaces → isolation (what a process can *see*).** A namespace gives a process
  its **own private view** of one kind of global resource, so it cannot see or touch
  others'. Linux has these namespaces:

  | Namespace | Isolates |
  |-----------|----------|
  | **PID** | process IDs — the container sees its app as **PID 1**, not the host's PIDs |
  | **NET** | network interfaces, IPs, ports, routing tables |
  | **MNT** | mount points / the filesystem tree |
  | **UTS** | hostname and domain name |
  | **IPC** | System-V IPC, shared memory, message queues |
  | **USER** | user & group IDs (map container root → unprivileged host user) |
  | **cgroup** | the cgroup root a process sees |
  | **TIME** | system clocks (boot/monotonic offsets) |

- **cgroups (control groups) → limits (how *much* a process can *use*).** A cgroup
  **meters and caps** a group of processes' resources: **CPU** shares/quota,
  **memory** limit, **block-I/O** bandwidth, **PIDs** count, and devices. Without
  cgroups, one container could starve the host (a "noisy neighbour").

> **Memory hook — the two halves of a container:** **namespaces = walls (what you
> can SEE); cgroups = a budget (what you can USE).** Isolation + limits =
> container. (Add the layered filesystem of 17.7 for the image.)

> **Why this matters (interview):** because containers are *just processes* sharing
> the host kernel, they are **lighter but less isolated** than VMs. A **kernel
> vulnerability** exploited from inside a container can potentially escape to the
> host — a VM's hardware boundary does not have this exposure. This one fact drives
> most container-security design (user namespaces, seccomp, gVisor, Kata/microVMs).

### MCQs

1. Namespaces provide ___; cgroups provide ___. → **isolation (visibility)** ;
   **resource limits**.
2. Which namespace makes the app appear as PID 1? → the **PID namespace**.
3. Which kernel feature stops a "noisy-neighbour" container hogging CPU/RAM? →
   **cgroups**.
4. Does a container have its own kernel? → **no** — it shares the host kernel.

---

## 17.7 Docker — Images, Layers, Containers, Dockerfile

**Docker** is the tool that made containers mainstream by giving them a simple
**package-build-run** workflow. Learn its four core nouns.

### The four core concepts

- **Image** — a **read-only template**: a snapshot of a filesystem (app + libraries
  + runtime) plus metadata (which command to run). Images are **built once** and
  **shared** via a **registry** (e.g. **Docker Hub**, ECR, GCR).
- **Container** — a **running instance of an image**: the image's read-only layers
  **plus one thin writable layer** on top. You can run many containers from one
  image.
- **Dockerfile** — a text recipe of steps to build an image.
- **Registry** — the store you `push`/`pull` images from (Docker Hub is the public
  default).

### Layers and the union filesystem

![A Docker image is a stack of read-only layers (built from Dockerfile steps, shared and cached via a union filesystem); the running container adds one writable copy-on-write layer.](images/165_docker_layers.png)

Each instruction in a Dockerfile that changes the filesystem creates **one new
read-only layer**. A **union (overlay) filesystem** (Docker's default driver is
**overlay2**; older ones were **AUFS**, **devicemapper**) stacks these layers into a
single view. Two big wins:

- **Sharing & caching** — layers are **content-addressed** and **reused**: if ten
  images all start `FROM ubuntu:22.04`, that base layer is stored and downloaded
  **once**. Rebuilds reuse **cached** layers for unchanged steps → fast builds.
- **Copy-on-write (CoW)** — the running container gets **one thin writable layer**.
  Reading a file comes from the shared read-only layers; **writing** first **copies
  the file up** into the writable layer. So starting a container copies **almost
  nothing** — hence millisecond startup and tiny per-container disk cost.

> **Memory hook:** **an image is like a stack of transparent sheets** (layers); you
> see the combined picture. Running a container just lays **one blank sheet on top**
> to scribble on — the sheets below stay clean and shared.

### A minimal Dockerfile (know these instructions)

```text
FROM python:3.12-slim         # base image (a layer) — start small
WORKDIR /app                  # set working directory inside the image
COPY requirements.txt .       # copy build context → a layer
RUN pip install -r requirements.txt   # run a command → a layer (deps cached)
COPY . .                      # copy the app source → a layer
EXPOSE 8000                   # document the port the app listens on
CMD ["python", "app.py"]      # default process to run when the container starts
```

> **Layer-order best practice (asked in interviews):** put the **rarely-changing**
> steps (install dependencies) **before** the **often-changing** steps (copy source
> code). Since a changed layer **invalidates every layer after it**, copying
> `requirements.txt` and running `pip install` *before* `COPY . .` means editing your
> code doesn't force a full dependency re-install — the cache is reused.

> **`RUN` vs `CMD` vs `ENTRYPOINT`:** `RUN` executes **at build time** (creating a
> layer); `CMD`/`ENTRYPOINT` define **what runs when the container starts**.

### MCQs

1. Image vs container? → image is a **read-only template**; a container is a
   **running instance** (image + writable layer).
2. What lets ten images share one Ubuntu base? → **layers + union filesystem**
   (content-addressed, cached).
3. Docker's default storage driver / union FS? → **overlay2** (OverlayFS).
4. Why does writing a file in a container not touch the image? → **copy-on-write**
   into the container's writable layer.
5. Where are images shared from? → a **registry** (e.g. **Docker Hub**).
6. Which Dockerfile instruction sets the default process? → **`CMD`** (or
   `ENTRYPOINT`).

---

## 17.8 Kubernetes Basics — Orchestrating Containers at Scale

Docker runs containers on **one machine**. But production runs **thousands** of
containers across **many machines**, and things constantly break: a container
crashes, a node dies, traffic spikes. Doing this by hand is impossible. A
**container orchestrator** automates it. **Kubernetes (K8s)** is the industry
standard.

### What orchestration gives you (why it exists)

- **Scheduling / bin-packing** — decide *which node* runs each container (§18.6).
- **Self-healing** — restart crashed containers; reschedule pods off a dead node.
- **Scaling** — add/remove replicas automatically as load changes (§18.7).
- **Rolling updates & rollback** — deploy a new version gradually, revert on failure.
- **Service discovery & load balancing** — give a stable name/IP to a set of
  replicas and spread traffic across them.

### The architecture

![Kubernetes has a control plane (API server, scheduler, etcd, controllers) that manages worker nodes; each node runs pods, and a pod is one or more containers sharing network and storage.](images/166_kubernetes_arch.png)

**Objects (smallest → largest):**

- **Container** → **Pod** → **Node** → **Cluster**.
- **Pod** — the **smallest deployable unit**: **one or more containers** that share
  the **same network (IP/port space) and storage volumes** and are always scheduled
  **together**. (Usually one main container per pod.)
- **Node** — a worker machine (VM or physical) that runs pods.
- **Cluster** — the control plane plus all worker nodes.

**Control plane (the "brain"):**

| Component | Job |
|-----------|-----|
| **kube-apiserver** | the **front door** — all commands and state changes go through it |
| **etcd** | the **cluster's database** — stores the entire desired + current state (key-value) |
| **kube-scheduler** | decides **which node** each new pod runs on (§18.6 bin-packing) |
| **controller-manager** | runs control loops that drive **actual state → desired state** (restart, replace) |

**Node components (the "hands"):**

| Component | Job |
|-----------|-----|
| **kubelet** | agent on each node; starts/stops pods and reports health to the API server |
| **kube-proxy** | programs the node's networking so pods/services are reachable |
| **container runtime** | actually runs the containers (containerd, CRI-O) |

> **Memory hook — desired-state / control loop:** you tell Kubernetes **"I want 3
> replicas"** (the *desired state*). Controllers **constantly compare** desired vs
> actual and act to close the gap: if one pod dies, actual=2 < desired=3, so a new
> pod is created. You declare the **what**; Kubernetes figures out the **how** and
> keeps it true — this **declarative, self-healing** loop is the whole idea.

> **Deployment vs Pod (interview):** you rarely create pods directly. A
> **Deployment** manages a **ReplicaSet**, which keeps N identical pods running and
> handles rolling updates. A **Service** gives that changing set of pods a **stable
> virtual IP / DNS name** so clients don't chase individual pod IPs.

### MCQs

1. Smallest deployable unit in Kubernetes? → the **Pod** (1+ containers sharing
   net/storage).
2. Where is the whole cluster state stored? → **etcd**.
3. Which component chooses the node for a new pod? → the **kube-scheduler**.
4. The per-node agent that runs pods? → **kubelet**.
5. What keeps N replicas alive and self-heals? → a **controller / ReplicaSet**
   (declarative control loop).
6. Why orchestrate at all? → **scheduling, self-healing, scaling, rolling updates,
   service discovery** across many nodes.

---

## 17.9 VM vs Container Trade-offs (decide with reasons)

Neither is "better" — they trade **isolation** for **speed and density**. Real
systems often **combine** them (containers *inside* VMs in the cloud).

| Dimension | Virtual Machine | Container | Winner |
|-----------|-----------------|-----------|:------:|
| **Isolation** | hardware boundary via hypervisor | shared kernel (namespaces/cgroups) | **VM** |
| **Security** | strong (kernel escape ≠ host) | weaker (kernel exploit can escape) | **VM** |
| **Start-up speed** | seconds (boots an OS) | **milliseconds** (no boot) | **Container** |
| **Size / image** | GBs (full OS) | **MBs** (app + libs) | **Container** |
| **Density per host** | tens | **hundreds–thousands** | **Container** |
| **Overhead** | full guest OS per VM | ~none beyond the app | **Container** |
| **OS flexibility** | **any** guest OS (Windows on Linux host) | must match **host kernel** (Linux) | **VM** |
| **Portability of a running instance** | live-migrate whole VM | rebuild/restart from image | **VM** |

> **How to choose:**
> - Need to run a **different OS**, run **untrusted/multi-tenant** workloads, or want
>   the **strongest isolation** → **VM**.
> - Need **fast start, high density, easy CI/CD packaging, microservices** →
>   **containers**.
> - Want **both** (strong isolation *and* container speed) → **microVMs** (AWS
>   **Firecracker**, **Kata Containers**, **gVisor**) — a tiny fast-booting VM per
>   container. This is exactly what serverless platforms use (§18.5).

### MCQs

1. Container beats VM on? → **speed, size, density, overhead**.
2. VM beats container on? → **isolation, security, OS flexibility, live migration**.
3. Best of both worlds? → **microVMs** (Firecracker / Kata / gVisor).

---

## 17.10 Real-World & Backend Perspectives

- **This is how every backend ships today.** You build a **Docker image** in CI,
  push it to a **registry**, and **Kubernetes** (or ECS/Cloud Run) runs it as pods
  across a fleet — the direct application of §§17.7–17.8.
- **"Works on my machine" solved.** A container bundles the exact runtime, libraries,
  and OS files, so the code that passes tests locally is **byte-for-byte** what runs
  in production.
- **Microservices** = many small services, each a container, scaled independently —
  orchestration (K8s) is what makes that manageable.
- **The cloud stacks both:** your EC2 instance is a **VM on a Type-1 hypervisor**
  (§18.4), and *inside* it you run **containers**. Serverless (AWS Lambda, §18.5)
  runs your function in a **Firecracker microVM** — a container-speed VM.
- **AI infra (M19):** GPU training/inference jobs are shipped as containers with the
  CUDA runtime baked in, and scheduled onto GPU nodes by Kubernetes.

---

## 17.11 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** "a container is a lightweight VM." **No** — a container has **no guest
  OS**; it is a **process** sharing the host kernel. This is the #1 misconception.
- **Mistake:** swapping **namespaces** and **cgroups**. **Namespaces = isolation
  (what you see); cgroups = limits (what you can use).**
- **Mistake:** calling Docker Hub a "hypervisor." Docker Hub is a **registry** (image
  store); Docker Engine runs containers; there is **no hypervisor** in plain
  containers.
- **Edge case:** you **cannot** run a Windows container on a Linux kernel (or vice
  versa) — containers must **match the host kernel**. Windows "Linux containers" run
  inside a hidden Linux **VM**.
- **Edge case (security):** because containers share the kernel, a **kernel exploit**
  can escape the container; VMs don't share a kernel, so the blast radius is smaller.
  Hence microVMs (Firecracker/Kata) for untrusted multi-tenant code.
- **Tradeoff:** more isolation (VM) ⇒ more overhead & slower start; more density
  (container) ⇒ weaker isolation. Pick per workload.
- **Mistake (Dockerfile):** putting `COPY . .` **before** installing dependencies —
  it busts the layer cache on every code change (see §17.7).

---

## 17.12 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** expect 1–2 MCQs — hypervisor **Type-1 vs Type-2** with
  examples; **VM vs container** ("which shares the kernel?"); **Docker image vs
  container**; benefits of virtualization.
- **GATE:** virtualization is light but the **Popek–Goldberg** idea, **trap-and-
  emulate**, and **full vs para-virtualization** can appear; the paging tie-in
  (nested/EPT) connects to M9/M10.
- **Interview (very high yield for backend/AI-infra):**
  - "Difference between a VM and a container?" → **hardware vs OS virtualization;
    guest OS vs shared kernel; GB/seconds vs MB/milliseconds; strong vs lighter
    isolation.**
  - "How does Docker make images small/fast?" → **layers + union FS + copy-on-write
    + caching.**
  - "What are cgroups and namespaces?" → **limits** and **isolation**.
  - "What does Kubernetes do that Docker doesn't?" → **orchestration across many
    nodes: scheduling, self-healing, scaling, rolling updates, service discovery.**
- **Coding/practical:**
  - `docker build -t app .` → `docker run -p 8000:8000 app` → `docker ps`.
  - `docker history <image>` shows the **layers**; `docker image ls` shows sizes.
  - `kubectl get pods/nodes`, `kubectl apply -f deploy.yaml`, `kubectl scale
    --replicas=5`.
  - Inspect isolation: `lsns` lists **namespaces**; files under
    `/sys/fs/cgroup/...` show **cgroup** limits.

---

## 17.13 Concept Checks & MCQs (test yourself)

1. Define virtualization in one line. → a **software illusion of hardware/OS** so
   many isolated systems share **one physical machine**.
2. Hypervisor's other name? → **Virtual Machine Monitor (VMM)**.
3. Type-1 vs Type-2? → **bare-metal (on hardware)** vs **hosted (in a host OS)**.
4. Give a Type-1 and a Type-2 example. → **ESXi/KVM/Xen/Hyper-V** ; **VirtualBox**.
5. Popek–Goldberg's three requirements? → **equivalence, resource control,
   efficiency**.
6. Trap-and-emulate runs the guest kernel in which mode? → **user mode**
   (deprivileged).
7. Full vs para-virtualization? → **unmodified guest** vs **modified guest with
   hypercalls**.
8. Intel/AMD hardware virtualization? → **VT-x / AMD-V** (+ **EPT/NPT** nested
   paging).
9. What does a container share with the host? → the **kernel**.
10. Namespaces vs cgroups? → **isolation (visibility)** vs **resource limits**.
11. Name three Linux namespaces. → **PID, NET, MNT** (also UTS/IPC/USER/cgroup/TIME).
12. Docker image vs container? → **read-only template** vs **running instance +
    writable layer**.
13. What is a Docker layer, and why cache it? → a filesystem diff per Dockerfile
    step; **shared/cached** to speed builds and downloads (union FS).
14. Container writable layer uses which technique? → **copy-on-write**.
15. Kubernetes smallest deployable unit? → **Pod**.
16. Where is cluster state stored? → **etcd**. Which picks the node? → **scheduler**.
17. Per-node agent? → **kubelet**.
18. Why containers start in ms but VMs in seconds? → containers **don't boot an OS**.
19. Which has stronger isolation, VM or container, and why? → **VM** — a **hardware
    boundary**, not a shared kernel.
20. Best-of-both technology for untrusted code? → **microVMs** (Firecracker / Kata).

**True/False**
- A container has its own OS kernel. → **False** (shares the host kernel).
- Type-2 hypervisors are faster than Type-1. → **False**.
- cgroups isolate what a process can see. → **False** (that's **namespaces**;
  cgroups **limit** usage).
- A Docker image is read-only. → **True**.
- You can run a Windows container directly on a Linux kernel. → **False**.
- Changing an early Dockerfile layer invalidates the later layers' cache. → **True**.

---

## 17.14 One-Page Revision Sheet

```
VIRTUALIZATION = software illusion of hardware/OS -> many isolated systems on 1 box.
  Benefits: CONSOLIDATION(util up), ISOLATION, PORTABILITY(snapshot/clone/LIVE-MIGRATE), cost.
  OS shares CPU among PROCESSES; HYPERVISOR shares HARDWARE among whole GUEST OSes.
  VM = virtual CPU/RAM/disk/NIC + a full unmodified GUEST OS.

POPEK-GOLDBERG (VMM rules): EQUIVALENCE + RESOURCE CONTROL + EFFICIENCY (most instrs native).
  Emulator = translate EVERY instr (slow, diff HW). Virtualizer = run natively (same HW).

HYPERVISOR:
  TYPE-1 BARE-METAL on hardware, NO host OS, faster, cloud   -> ESXi/Hyper-V/Xen/KVM
  TYPE-2 HOSTED as an app in a host OS, slower, laptops      -> VirtualBox/VMware WS

HOW IT WORKS:
  TRAP-AND-EMULATE: guest kernel in USER mode; privileged instr TRAPS -> VMM emulates.
    (needs sensitive ⊆ privileged; old x86 broke this -> ~17 bad instrs)
  FULL VIRT (binary translation): guest UNMODIFIED, VMM rewrites bad instrs (early VMware)
  PARA-VIRT: guest MODIFIED -> HYPERCALLS (Xen). low overhead, needs source.
  HARDWARE-ASSISTED: Intel VT-x / AMD-V root/non-root + VMCS; EPT/NPT nested paging (today).

CONTAINER vs VM:
  VM virtualizes HARDWARE (guest OS each, GBs, seconds, strong isolation).
  CONTAINER virtualizes the OS -> SHARES HOST KERNEL (MBs, ms, high density, weaker isolation).
  Container = NAMESPACES(isolation: what you SEE) + CGROUPS(limits: what you USE) + union FS.
    namespaces: PID/NET/MNT/UTS/IPC/USER/cgroup/TIME.

DOCKER: IMAGE(read-only template, layered) -> CONTAINER(image + 1 writable CoW layer).
  Each Dockerfile step = 1 LAYER; union FS (overlay2) -> layers SHARED + CACHED.
  Registry = Docker Hub (push/pull). Order deps BEFORE code (cache!). CMD = default process.

KUBERNETES (orchestrate many nodes): Container < POD < NODE < CLUSTER.
  Pod = 1+ containers sharing net/storage = smallest deployable unit.
  CONTROL PLANE: apiserver(front door) | etcd(state) | scheduler(pick node) | controllers(loops).
  NODE: kubelet(runs pods) | kube-proxy(net) | runtime(containerd).
  Declarative desired-state + self-healing. Why: schedule/heal/scale/rolling-update/discover.

MICROVM (Firecracker/Kata/gVisor) = VM isolation at container speed (serverless).
```

### Flash cards

| Front | Back |
|-------|------|
| Hypervisor other name? | Virtual Machine Monitor (VMM) |
| Type-1 vs Type-2? | Bare-metal (on hardware) vs hosted (in a host OS) |
| Type-1 examples? | ESXi, Hyper-V, Xen, KVM |
| Full vs para-virtualization? | Unmodified guest vs modified guest (hypercalls) |
| Intel/AMD HW virtualization? | VT-x / AMD-V (+ EPT/NPT) |
| Container shares what? | The host OS kernel |
| Namespaces vs cgroups? | Isolation (what you see) vs limits (what you use) |
| Image vs container? | Read-only template vs running instance (+writable layer) |
| Why images are small/fast? | Layers + union FS + copy-on-write + caching |
| Smallest K8s unit? | Pod (1+ containers) |
| Where is cluster state? | etcd |
| Picks a node for a pod? | kube-scheduler |
| VM vs container isolation? | VM stronger (hardware boundary) |

### Spaced repetition
- **24-hour:** recite Type-1 vs Type-2 (+examples) and the VM-vs-container table
  (kernel, size, speed, isolation).
- **7-day:** explain namespaces vs cgroups; Docker image/layer/container/CoW; the
  four virtualization techniques (trap-and-emulate, binary translation, para-virt,
  VT-x/AMD-V).
- **30-day:** draw the Kubernetes control-plane/node diagram from memory and explain
  desired-state self-healing; choose VM vs container vs microVM for a given workload.

---

## 17.15 Summary

**Virtualization** creates a **software illusion of hardware** so one physical
machine safely runs **many isolated guest OSes**, driven by a **hypervisor (VMM)**.
Hypervisors are **Type-1 (bare-metal**, on the hardware, fast, cloud: ESXi/Xen/KVM/
Hyper-V**)** or **Type-2 (hosted**, an app on a host OS: VirtualBox**)**. Under the
hood, a VMM obeys **Popek–Goldberg** (equivalence, control, efficiency) using
**trap-and-emulate**, **binary translation (full virtualization)**,
**para-virtualization (hypercalls)**, or today's **hardware-assisted VT-x/AMD-V**
with **EPT/NPT** nested paging. **Containers** push virtualization up a level: they
**share the host kernel**, isolated by **namespaces** (what you *see*) and limited by
**cgroups** (what you *use*), so they are **MB-sized and start in milliseconds** but
give **weaker isolation** than a VM. **Docker** packages apps as **layered,
copy-on-write images** shared via a **registry**, and **Kubernetes** orchestrates
those containers across many nodes with a **control plane** (apiserver, etcd,
scheduler, controllers) and **declarative self-healing**.

Next, **Module 18 — Cloud Operating Systems** scales all of this to the data centre:
IaaS/PaaS/SaaS, EC2/Azure/GCP VMs, serverless/FaaS, and the schedulers and
autoscalers that turn a fleet of machines into **"an operating system for the whole
data centre."**

> **You have mastered this module when** you can: define virtualization and its
> benefits; separate Type-1 vs Type-2 with examples; explain trap-and-emulate and
> full/para/hardware-assisted virtualization; state precisely how a container differs
> from a VM (shared kernel = namespaces + cgroups); explain Docker images, layers,
> copy-on-write, and a Dockerfile; and sketch the Kubernetes architecture and why
> orchestration exists — all without notes.
