---
title: "Module 19 — The AI-Engineering Perspective (GPUs, CUDA & LLM Serving as OS Problems)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 19 — The AI-Engineering Perspective (GPUs, CUDA & LLM Serving as OS Problems)

> **Where this module sits.**
> Every idea in this course — **scheduling** (M6), **memory management &
> paging** (M9), **virtual memory** (M10), **DMA & I/O** (M2, M13),
> **synchronization** (M7), **IPC** (M4) — reappears, almost unchanged, when you
> build or run AI systems. A GPU is just **another device the OS schedules**; a
> **CUDA kernel** is a job dispatched to that device; **CUDA streams** are a
> pipeline that overlaps I/O with compute (double buffering); the **GPU memory
> hierarchy** is the same registers→cache→RAM story one level down; and modern
> **LLM serving** literally reinvents **paging** to manage attention memory
> (**PagedAttention**). This module is not a deep-learning tutorial — it is a map
> from **AI infrastructure back to the OS concepts you already know**, so an
> interviewer's "how does an LLM server manage GPU memory?" becomes an OS
> question you can answer from first principles.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★       | ★      | ★       | ★★★★      | ★★★★★   |

**Most-asked interview/backend concepts:** why GPUs (**throughput vs latency**
cores); the **CPU→GPU offload** lifecycle; **host vs device**, **kernel**,
**grid / block / thread / warp** (**warp = 32 threads, SIMT**); **CUDA streams**
for overlapping copy and compute; the **GPU memory hierarchy** (registers →
shared → L2 → global/HBM) and **memory coalescing**; **pinned (page-locked)
memory** and why it enables **DMA**; **multi-GPU NUMA / NVLink**; **LLM inference
as a memory-management problem** — **KV-cache** growth and **PagedAttention =
paging for attention**; **distributed training** (data / tensor / pipeline
parallelism, **all-reduce**) and why the bottleneck is usually **memory and
network**, not FLOPs.

---

## 19.1 Why a GPU at all? The CPU→GPU Offload Model

### Motivation (first principles)

A CPU core is a **latency-optimised** machine: a few very fast cores, deep
pipelines, large caches, branch prediction — built to finish **one thread of
control** as quickly as possible. A GPU is the opposite: a **throughput-optimised**
machine with **thousands of simple cores** that run the **same instruction on
many data elements** at once. Deep learning is mostly **matrix multiplication** —
millions of identical multiply-adds with no branching — which is exactly the
**data-parallel** work a GPU eats for breakfast.

The OS/hardware truth: the **GPU is a peripheral device** hanging off the **PCIe**
bus (or **NVLink**), with its **own memory** (HBM). The CPU (the **host**) cannot
run Python on the GPU; it must **offload** work to it, exactly the way it offloads
a disk write — set up the data, kick off the device, and collect the result.

![CPU offloads data-parallel work; DMA moves data over PCIe/NVLink, the GPU runs the kernel in parallel.](images/181_cpu_gpu_offload.png)

The **offload lifecycle** (memorise these four steps — they frame everything):

```text
1. COPY data   Host RAM -> GPU HBM        (cudaMemcpy, done by DMA)
2. LAUNCH      kernel<<<grid, block>>>()  (host queues work on the device)
3. COMPUTE     GPU runs 1000s of threads in parallel
4. COPY back   GPU HBM -> Host RAM        (cudaMemcpy, DMA again)
```

> **Memory hook:** the GPU is the **kitchen**, the CPU is the **head waiter**.
> The waiter (CPU) never cooks; it carries orders and ingredients **in**
> (H2D copy), shouts the order (**kernel launch**), lets the many cooks work in
> parallel, and carries plates **out** (D2H copy). A restaurant is fast not
> because the waiter is fast, but because the **kitchen parallelises**.

### The cost that dominates: data movement, not compute

Steps 1 and 4 are **I/O over PCIe** (~16–64 GB/s), while HBM inside the GPU runs
at **~1–3 TB/s** and compute is faster still. So the classic OS lesson returns:
**the slow link is the bottleneck.** Good AI code, like good OS code, works hard
to **keep data on the fast side** (in HBM) and **overlap** the slow copies with
compute (§19.4). "Never let the fast unit sit idle waiting on I/O" — the same
sentence that drove multiprogramming in **M1** drives GPU programming.

### MCQs

1. CPU vs GPU core design goal? → **latency** (few fast cores) vs **throughput**
   (many simple cores).
2. Where does GPU data physically live? → the GPU's own **HBM (device memory)**.
3. The usual bottleneck in a GPU program? → **data movement over PCIe** (H2D/D2H),
   not the compute.

---

## 19.2 GPU Scheduling — the Same Ideas, One Level Down

### The host-side queue and the device-side scheduler

When the host calls `kernel<<<...>>>()` it does **not** block; it **enqueues**
the launch onto the GPU and returns (asynchronous). This is a **producer–consumer
queue** (M7): the CPU produces work, the GPU consumes it. On the device, a
hardware **GigaThread / grid scheduler** hands **thread blocks** to the
**Streaming Multiprocessors (SMs)**, and within each SM a **warp scheduler**
picks which **warp** (group of 32 threads) issues next cycle.

### Latency hiding = the GPU's version of multiprogramming

A single SM keeps **many warps resident** at once. When one warp **stalls** on a
slow global-memory read (hundreds of cycles), the warp scheduler instantly
switches to **another ready warp** — with **zero context-switch cost**, because
each warp's registers are already allocated on-chip. This is *literally*
**multiprogramming from M1**: "when one job blocks on I/O, run another." The GPU
just does it in hardware, per-cycle, to hide **memory latency** instead of disk
latency.

| OS concept (this course) | GPU equivalent |
|---|---|
| Process/job scheduled onto a CPU | **thread block** scheduled onto an **SM** |
| Ready queue, dispatcher | **warp scheduler** picks a ready warp each cycle |
| Multiprogramming (run another on I/O wait) | **latency hiding** (switch warps on a memory stall) |
| Context switch (save/restore registers) | **free** — warp registers stay resident on the SM |
| Time quantum / preemption | warps interleave per-instruction (fine-grained) |
| Oversubscription (more procs than CPUs) | launch **far more threads than cores** on purpose |

> **Memory hook:** an SM is a **call-centre agent juggling many calls**. The
> moment one caller says "hold on, let me find it" (memory stall), the agent
> takes the next call. Idle time disappears because there is **always another
> ready warp**. That is why you deliberately launch **thousands** of threads —
> to give the scheduler plenty to switch to.

> **Occupancy** is the GPU word for "how many warps are resident vs the maximum."
> High occupancy → more warps to hide latency behind → the SM rarely stalls.
> It is bounded by **registers per thread** and **shared memory per block**
> (a fixed budget per SM) — the same "resources are finite, allocation is a
> tradeoff" theme as OS memory management.

### MCQs

1. What hides memory latency on a GPU? → keeping **many warps resident** and
   switching to a **ready warp** on a stall (latency hiding = multiprogramming).
2. Cost of a GPU "context switch" between warps? → effectively **zero** (registers
   stay on-chip).
3. What is **occupancy**? → resident warps ÷ maximum warps per SM (limited by
   register/shared-memory budget).

---

## 19.3 The CUDA Runtime — Host vs Device, Kernels, and the Thread Hierarchy

**CUDA** is NVIDIA's programming model for offloading to the GPU. Two facts
organise everything:

- **Host** code runs on the **CPU** (ordinary C/C++/Python); **device** code (a
  **kernel**, marked `__global__`) runs on the **GPU**.
- A kernel is launched over a **grid of thread blocks**, and each block holds many
  **threads**; the same kernel body runs in **every** thread, distinguished only
  by its index. This is **SIMT** — Single Instruction, Multiple Threads.

![Kernel = a GRID of BLOCKS; each block runs on one SM; 32 threads form a WARP executed in lockstep.](images/182_cuda_thread_hierarchy.png)

| Level | What it is | OS analogy |
|-------|-----------|------------|
| **Grid** | all threads of one kernel launch | a whole **job** |
| **Block** | group of threads that share **shared memory** + can `__syncthreads()` | a **process** with shared address space + a barrier |
| **Warp** | **32 threads** that execute **in lockstep** (SIMT) | a **gang** scheduled together |
| **Thread** | one lane; has its **own registers** | a **thread** with private stack/registers |

A minimal kernel (vector add) — note how each thread computes **one** element:

```c
__global__ void vadd(const float *a, const float *b, float *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;  // this thread's global index
    if (i < n) c[i] = a[i] + b[i];                  // one element per thread
}
// host launches a grid of ceil(n/256) blocks x 256 threads:
vadd<<<(n + 255) / 256, 256>>>(dA, dB, dC, n);
```

> **The warp is the real scheduling unit (favourite trap).** Threads are *written*
> individually, but the hardware issues instructions **per warp of 32**. Two
> consequences you must know:
> - **Warp divergence:** if threads in a warp take different branches of an
>   `if/else`, the warp executes **both** paths serially with lanes masked off —
>   halving throughput. Data-parallel code avoids per-thread branching.
> - **Block size should be a multiple of 32**, else the last warp runs with idle
>   lanes (wasted like internal fragmentation in M9).

> **Memory hook:** a warp is a **rowing eight** — all 32 oars must pull the *same*
> stroke at the *same* time. If half the crew rows a different stroke (divergent
> branch), the boat does both strokes one after the other and slows down.

### MCQs

1. `__global__` marks code that runs on? → the **device (GPU)**, launched from the
   host.
2. How many threads in a warp? → **32** (executed in lockstep, SIMT).
3. Why keep block size a multiple of 32? → so no warp runs with **idle lanes**.
4. What is warp divergence? → threads in a warp taking different branches, forcing
   **both paths to run serially**.

---

## 19.4 CUDA Streams — Overlapping Copy and Compute (an OS-scheduling story)

### The problem: the PCIe copy stalls the GPU

If you do the naive thing — copy **all** data H2D, then compute, then copy **all**
results D2H — the GPU sits **idle** during both copies, and the copy engine sits
idle during compute. It is the same waste as a CPU blocking on a full disk read
before doing any work.

### The fix: streams (independent queues that overlap)

A **CUDA stream** is an **ordered queue** of operations (copies + kernels) that
run **in order within the stream**, but **different streams can run
concurrently**. Modern GPUs have separate **copy engines** and **compute
engines**, so a copy in stream B can run **while** a kernel computes in stream A.
Split the work into chunks, put each chunk in its own stream, and the timeline
turns from serial into a **pipeline** — this is **double buffering / prefetching**
(the same trick as the DBMS buffer manager and OS read-ahead in M13).

![Splitting work into streams overlaps transfer with compute — the GPU analogue of OS double buffering/DMA overlap.](images/183_cuda_streams_overlap.png)

```c
for (int c = 0; c < CHUNKS; ++c) {
    cudaMemcpyAsync(dA+off, hA+off, sz, H2D, stream[c]); // copy chunk (engine 1)
    process<<<g, b, 0, stream[c]>>>(dA+off, dC+off);      // compute  (engine 2)
    cudaMemcpyAsync(hC+off, dC+off, sz, D2H, stream[c]); // copy back (engine 1)
}   // while stream[0] computes, stream[1] is already copying in -> overlap
```

> **Two rules exams/interviews test:**
> - The **default stream (stream 0)** is **synchronising** — it serialises with
>   others. Real overlap needs **explicit non-default streams**.
> - `cudaMemcpyAsync` only truly overlaps when the host buffer is **pinned
>   (page-locked)** memory (§19.6). With pageable memory the copy silently falls
>   back to synchronous.

> **Memory hook:** streams are an **assembly line**. Stage 1 (copy in), stage 2
> (compute), stage 3 (copy out) each work on a **different chunk at the same
> time**, so no station is ever idle — exactly like overlapping I/O with CPU in
> a pipelined OS.

### MCQs

1. What lets a copy and a kernel run at the same time? → putting them in
   **different (non-default) CUDA streams**.
2. The default stream (0) behaves how? → it **synchronises** with other streams.
3. Prerequisite for true async `cudaMemcpyAsync` overlap? → **pinned (page-locked)**
   host memory.

---

## 19.5 The GPU Memory Hierarchy — the Same Pyramid, One Level Down

A GPU has its own **memory hierarchy**, and it maps cleanly onto the CPU one from
**M2/M9**. Faster + smaller + closer at the top; slower + larger + shared at the
bottom.

| GPU memory | Scope | Speed | OS/CPU analogue |
|-----------|-------|-------|-----------------|
| **Registers** | per **thread** | fastest (~1 cyc) | CPU **registers** |
| **Shared memory / L1** | per **block** (on-chip) | very fast | a small **scratchpad cache** the programmer controls |
| **L2 cache** | whole GPU | fast | CPU **L2/L3** |
| **Global memory (HBM)** | whole GPU, off-chip | ~1–3 TB/s but ~hundreds of cycles latency | main **RAM** |
| **Host RAM (over PCIe)** | CPU side | slow link (~tens of GB/s) | a slow **disk/network** from the GPU's view |

**Shared memory** is the one to understand: it is a **small, fast, on-chip
scratchpad** that all threads in a **block** can read/write — a *software-managed
cache*. Tiling a matrix multiply through shared memory (load a tile once, reuse it
32 times) is the GPU version of "**exploit locality; avoid the slow level**,"
identical in spirit to the DBMS buffer pool.

### Memory coalescing — the GPU's "sequential vs random I/O"

Global-memory accesses are served in **transactions** of a fixed width (e.g. 128
bytes). If the **32 threads of a warp** read **32 consecutive** 4-byte floats
(4×32 = 128 B), the hardware **coalesces** them into **one** transaction. If they
read **scattered/strided** addresses, it may take **up to 32** transactions —
**32× the memory traffic** for the same data.

```text
COALESCED   (thread t reads a[t]):     one 128-byte transaction   -> full bandwidth
STRIDED     (thread t reads a[t*17]):  up to 32 transactions       -> ~1/32 bandwidth
```

> **Memory hook:** coalescing is **sequential vs random disk I/O (M12/DBMS M6)**
> all over again. One big contiguous read beats 32 scattered reads — on a disk
> *and* on HBM. Lay data out so **neighbouring threads touch neighbouring
> addresses**.

### MCQs

1. GPU shared memory is best described as? → a **programmer-managed on-chip
   scratchpad/cache**, shared per block.
2. What is memory coalescing? → combining a warp's **consecutive** accesses into
   **one** transaction (like sequential I/O).
3. Slowest link from the GPU's viewpoint? → **host RAM over PCIe**.

---

## 19.6 Pinned (Page-Locked) Memory & DMA — a Direct M9/M10 Payoff

### First principles: why ordinary RAM cannot be DMA'd safely

Recall **paging (M9/M10)**: your process sees **virtual** memory, and the OS may
**page out** or **relocate** a physical frame at any time. But a **DMA engine**
(M2) moves bytes using **physical addresses** with no knowledge of the page
tables. If the OS moved a page mid-transfer, DMA would scribble on the wrong
physical frame. So the GPU driver cannot DMA directly from ordinary **pageable**
memory.

### The fix: pin the pages

**Pinned (page-locked)** memory is host RAM the OS has **locked in place** — it
**cannot be paged out or moved** (like `mlock()` in Linux). Now its physical
address is stable, so the GPU's **DMA engine** can stream from it directly.

```text
PAGEABLE copy:  Host pageable RAM --(CPU copies)--> hidden PINNED staging buffer
                                  --(DMA)--> GPU HBM        (two hops, slower, sync)
PINNED   copy:  Host PINNED RAM   --(DMA)--------------> GPU HBM
                                  (one hop, faster, can be truly async)
```

- With **pageable** memory the driver must first copy your data into a hidden
  **pinned staging buffer**, *then* DMA — an extra copy, and it forces the
  transfer to be **synchronous**.
- With **pinned** memory (`cudaHostAlloc` / `cudaMallocHost`) the DMA goes
  **straight** from your buffer → **higher bandwidth** and **true async overlap**
  (§19.4).

> **The tradeoff (edge case):** pinned memory is **scarce** — it is unswappable
> physical RAM, so over-pinning starves the rest of the system and can hurt
> overall performance. Pin the **hot** transfer buffers (e.g. the data-loader's
> output), not everything.

> **Memory hook:** pinning is **nailing a page to the floor** so the DMA truck can
> load it without the OS shuffling it to another room mid-load. Great for the few
> boxes you ship constantly; terrible if you nail down the whole warehouse.

This is the clearest "AI infra **is** OS" moment: **pinned memory only makes sense
if you understand paging and DMA.** It ties **M2 (DMA)**, **M9 (paging)**, and
**M10 (page replacement/locking)** together.

### MCQs

1. Why can't DMA use ordinary pageable memory directly? → the OS may **page
   out/move** the frame; DMA uses **physical addresses**.
2. Two benefits of pinned memory? → **faster** (no staging copy) and enables
   **true async** transfers.
3. Downside of too much pinned memory? → it is **unswappable RAM**; over-pinning
   **starves the system**.

---

## 19.7 Multi-GPU: NUMA, NVLink, and IPC for Data Loading

### NUMA — the multi-GPU version of a topology you already know

In a multi-socket server, **NUMA (Non-Uniform Memory Access)** means a CPU core
reaches its **local** memory bank faster than a **remote** one. Multi-GPU boxes
have the *same* shape: each GPU sits under a particular **PCIe root / CPU socket**,
so a GPU talks fastest to the **CPU and NIC on its own socket**. Pinning a
data-loader process to the **right NUMA node** (near its GPU) can noticeably cut
transfer latency — the same **affinity/locality** idea as CPU-cache and
NUMA-aware scheduling.

Between GPUs, **NVLink** is a fast direct GPU-to-GPU interconnect (far faster than
routing through PCIe and host RAM), and **GPUDirect P2P / RDMA** lets one GPU read
another's memory — or a NIC DMA straight into GPU memory — **bypassing the CPU**.
This is DMA/zero-copy thinking applied across devices.

### IPC and shared memory for the data pipeline

Training is often **input-starved**: the GPU finishes a batch before the CPU has
decoded/augmented the next one. The fix is classic OS **IPC (M4)**:

- **Multiple worker processes** decode data in parallel (e.g. PyTorch
  `DataLoader(num_workers=k)` **forks** worker processes).
- They hand batches to the trainer through **shared memory** (`/dev/shm`, POSIX
  shared memory) to avoid re-serialising large tensors over pipes — a **zero-copy
  handoff** using the **shared-memory IPC** model from M4.
- Watch out for **fork + COW (M10)**: forked workers share pages copy-on-write, so
  touching large Python objects can silently blow up memory as pages get copied.

> **Memory hook:** the data loader is a **producer–consumer problem (M7)** with a
> **bounded buffer** — CPU workers *produce* batches, the GPU *consumes* them, and
> shared memory is the buffer. If producers are too slow, the GPU (consumer)
> starves and utilisation drops.

### MCQs

1. Multi-GPU affinity to the nearest CPU/NIC is an instance of? → **NUMA
   locality**.
2. What lets one GPU read another's memory without the CPU? → **NVLink /
   GPUDirect P2P (RDMA)**.
3. PyTorch DataLoader workers hand tensors to the trainer via? → **shared-memory
   IPC** (avoids re-copy); beware **fork COW**.

---

## 19.8 LLM Inference as an OS Problem — KV-Cache & PagedAttention

This is the section interviewers love, because it is **pure OS**.

### Why serving an LLM is a memory-management problem

A transformer generates text **one token at a time**. To avoid recomputing
attention over the whole prompt each step, it caches the **Keys and Values** of
every past token — the **KV-cache**. This cache **grows with every generated
token** and is **per-request**. On a busy server with many concurrent
conversations of *unknown final length*, the question "**who gets which GPU memory,
and how do we not waste it?**" is exactly an **OS memory-allocation** problem.

**Worked numerical — how big is a KV-cache?**

```text
KV bytes/token = 2 (K and V) x num_layers x hidden_size x bytes_per_element
Example (Llama-2-13B, fp16): 2 x 40 x 5120 x 2 bytes
                           = 819,200 bytes  ~= 0.78 MiB per token
For a 2,048-token context:  2048 x 0.78 MiB ~= 1.6 GiB  (ONE request!)
```

(With **grouped-query attention (GQA)** the KV heads are fewer, shrinking this —
but the point stands: KV memory is huge and per-request.) Multiply by dozens of
concurrent requests and GPU HBM fills instantly — memory, not compute, caps how
many users you can serve.

### The naive allocator wastes memory — just like early OS memory schemes

Early LLM servers reserved a **single contiguous block** per request, sized for
the **maximum** possible length. This repeats the mistakes of **contiguous memory
allocation (M9)**:

- **Internal fragmentation:** a request that ends early leaves its big reserved
  block mostly empty.
- **External fragmentation:** freed blocks of different sizes leave holes too small
  to reuse.
- **Over-reservation:** you must reserve for the worst case, so you fit **far fewer**
  concurrent requests than the hardware could hold.

### PagedAttention — literally paging, applied to attention

**vLLM's PagedAttention** solves this with the **exact** idea from **M9/M10
paging**: stop demanding contiguous memory. Split the KV-cache into **fixed-size
blocks** (e.g. **16 tokens** each), store them **anywhere** in HBM, and keep a
**block table** per request that maps **logical KV blocks → physical GPU blocks** —
a **page table for attention**.

![Both OS virtual memory and PagedAttention map logical -> physical in fixed-size blocks, so memory need not be contiguous.](images/184_pagedattention_paging.png)

| OS paging (M9/M10) | PagedAttention (vLLM) |
|---|---|
| Fixed-size **page/frame** | fixed-size **KV block** (e.g. 16 tokens) |
| **Page table**: virtual page → physical frame | **block table**: logical KV block → physical GPU block |
| Frames allocated **on demand** (demand paging) | KV blocks allocated **as tokens are generated** |
| No **external** fragmentation (fixed frames) | no external fragmentation (fixed blocks) |
| **Copy-on-write** shared pages after `fork` | **shared prefix** blocks COW'd across requests |

The payoffs are the same ones paging gave the OS: **near-zero external
fragmentation**, so memory utilisation jumps and you fit **many more concurrent
requests**; and **sharing** — two requests with the same system prompt can
**share** those KV blocks **copy-on-write** (identical to `fork` COW in M10),
until one diverges. vLLM reports this cuts KV waste from ~60–80% down to a few
percent, raising throughput several-fold.

> **The one-line interview answer:** *"How does a modern LLM server manage GPU
> memory?"* → **"It pages the KV-cache. PagedAttention chops attention memory into
> fixed-size blocks with a per-request block table — OS virtual memory applied to
> attention — killing fragmentation and enabling COW prefix sharing."**

> **Memory hook:** the KV-cache is a **process's growing heap**, and PagedAttention
> is the **MMU + page table** that lets it grow into **scattered frames** instead
> of demanding one huge contiguous chunk.

### MCQs

1. What grows per token during LLM generation? → the **KV-cache** (cached keys &
   values).
2. PagedAttention is analogous to which OS mechanism? → **paging** (virtual→physical
   via a block/page table).
3. How do two requests with the same prompt save memory? → **copy-on-write
   sharing** of KV blocks (like `fork` COW).
4. Which problem does contiguous KV allocation suffer? → **internal & external
   fragmentation** + over-reservation.

---

## 19.9 Distributed Training — When One GPU Isn't Enough

Big models don't fit (or train too slowly) on one GPU, so work is split across
many. There are **three axes of parallelism**; know what each splits and its
**OS/network cost**.

| Parallelism | What is split | Communication | OS analogy |
|-------------|---------------|---------------|------------|
| **Data** | the **batch** (each GPU has a full model copy, different data) | **all-reduce** gradients every step | replicas + a **barrier/reduce** sync (M7) |
| **Tensor (model)** | **individual layers/matrices** across GPUs | all-reduce **within** each layer (very chatty) | one job's address space **striped** across nodes |
| **Pipeline** | **groups of layers** into stages on different GPUs | activations passed **stage→stage** | an **assembly line**; suffers startup **"bubble"** |

### All-reduce and why the network is the bottleneck

In **data parallelism**, after each step every GPU must average its gradients with
all others — a collective **all-reduce** (NVIDIA's **NCCL** uses a **ring
all-reduce**). Each GPU ends up sending/receiving ~**2×(N−1)/N × (model size)**
bytes **every step**. For a multi-billion-parameter model that is **gigabytes of
traffic per step**, so the **interconnect** (NVLink within a node, InfiniBand/
RoCE across nodes) — not the math — usually caps scaling. This is the OS lesson
yet again: past a point, **communication/synchronisation overhead dominates**
(cf. Amdahl's law and lock contention in M7).

- **Pipeline bubble:** while the pipeline fills and drains, some stages are idle —
  the same **startup/pipeline-fill latency** you see in any pipelined system.
  Splitting the batch into **micro-batches** shrinks the bubble.
- **Stragglers & barriers:** an all-reduce is a **barrier** — the slowest GPU sets
  the pace, exactly like the slowest thread at a barrier in M7.

> **Memory hook:** distributed training is a **synchronisation problem, not a math
> problem**. FLOPs are cheap and parallel; the pain is **all-reduce traffic** and
> **barriers**, which are M7/networking, not linear algebra.

### MCQs

1. Data vs tensor vs pipeline parallelism split what? → the **batch** vs a **single
   layer** vs **groups of layers (stages)**.
2. What collective syncs gradients in data parallelism? → **all-reduce** (e.g.
   ring all-reduce via NCCL).
3. The usual scaling bottleneck at large N? → the **interconnect/network** +
   **barrier sync**, not compute.
4. What is the pipeline "bubble" and its fix? → idle stages during fill/drain;
   fixed by **micro-batching**.

---

## 19.10 Real-World & Backend Perspectives

- **Serving stacks (vLLM, TensorRT-LLM, TGI)** are, at heart, **OS schedulers +
  memory managers** for the GPU: they do **continuous batching** (add/remove
  requests from the running batch each step — like a ready queue), **PagedAttention**
  memory management, and **preemption/swapping** of KV blocks to host RAM when HBM
  is full (**swapping**, straight from M10).
- **GPU utilisation is the KPI**, and it is usually low because of the same OS
  villains: **data-loading I/O starvation**, **PCIe transfer stalls**, and
  **synchronisation barriers**. Fixing them is streams/pinning/overlap (§19.4–6).
- **MPS / MIG (multi-tenancy):** NVIDIA **MIG** partitions one physical GPU into
  isolated instances — **virtualization/partitioning** (M17) for GPUs; **MPS**
  lets multiple processes share a GPU context (time/space sharing).
- **Cost:** GPU HBM is the scarce, expensive resource; every trick in this module
  (paging the KV-cache, coalescing, overlap) is ultimately about **serving more
  users per GPU-dollar** — an ops/backend concern.

---

## 19.11 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking the GPU is "just faster." It is **throughput-oriented**;
  **latency-bound, branchy** code runs *worse* on a GPU than a CPU.
- **Mistake:** measuring kernel time but ignoring **H2D/D2H copies** — the copies
  often dominate; always overlap them (streams + pinned).
- **Mistake:** using the **default stream** and expecting overlap (it serialises).
- **Mistake:** using `cudaMemcpyAsync` from **pageable** memory (silently
  synchronous — no overlap).
- **Edge case:** over-pinning host memory → unswappable RAM starves the OS.
- **Edge case:** **warp divergence** from data-dependent branches quietly halves
  throughput.
- **Tradeoff:** bigger blocks/more threads improve **occupancy** but each thread
  gets **fewer registers** — spilling to slow local memory. It's the same
  finite-resource allocation tension as OS scheduling/memory.
- **Edge case (LLM):** small **KV block size** cuts fragmentation but adds
  block-table overhead — the classic **page-size tradeoff** from M9.

---

## 19.12 Exam, Interview & Coding Perspectives

- **Interview (the money questions):**
  - *"Walk me through what happens when you call a CUDA kernel."* → offload
    lifecycle (§19.1) + async launch + warp scheduling (§19.2).
  - *"How would you speed up a GPU pipeline that's only 30% utilised?"* → overlap
    copies with compute via **streams + pinned memory**; fix **data-loader
    starvation**; improve **coalescing/occupancy**.
  - *"How does an LLM server manage GPU memory?"* → **PagedAttention = paging the
    KV-cache** + COW prefix sharing + swapping to host (§19.8).
  - *"Why doesn't training scale linearly to 100 GPUs?"* → **all-reduce/network
    bottleneck** + **barrier/straggler** overhead (§19.9).
- **Backend/SRE:** you'll tune `num_workers`, pinned buffers, batch size, and
  `--gpu-memory-utilization`; every knob is an OS resource-allocation decision.
- **GATE/SEBI/RBI:** GPUs aren't core syllabus, but the *transferable* concepts —
  **DMA, paging, producer-consumer, barriers, NUMA** — are, and this module is how
  they show up in practice.

---

## 19.13 Concept Checks & MCQs (test yourself)

1. Two design philosophies: CPU vs GPU? → **latency** (few fast cores) vs
   **throughput** (many simple cores, SIMT).
2. The four offload steps? → **copy H2D → launch kernel → compute → copy D2H**.
3. Warp size? → **32 threads**, executed in **lockstep (SIMT)**.
4. Grid ⊃ block ⊃ ? → **warp (32) ⊃ thread**.
5. What hides GPU memory latency? → **many resident warps**; switch to a **ready
   warp** on stall (multiprogramming in hardware).
6. Cost of switching warps? → **~zero** (registers stay on-chip).
7. Shared memory is? → a **per-block, on-chip, programmer-managed scratchpad**.
8. Memory coalescing = ? → merging a warp's **consecutive** accesses into **one**
   transaction (sequential vs random I/O).
9. Why pinned memory for DMA? → pages **can't move/page-out**; stable physical
   address; faster + async.
10. Downside of over-pinning? → unswappable RAM **starves the system**.
11. Real overlap of copy+compute needs? → **non-default streams** + **pinned**
    memory.
12. Default stream (0) behaviour? → **synchronising**.
13. Multi-GPU nearest-socket affinity is? → **NUMA locality**.
14. GPU-to-GPU direct memory access? → **NVLink / GPUDirect P2P (RDMA)**.
15. DataLoader workers pass tensors via? → **shared-memory IPC** (beware fork COW).
16. What grows per generated token? → the **KV-cache**.
17. KV bytes/token formula? → `2 × layers × hidden × bytes`.
18. PagedAttention ≈ which OS mechanism? → **paging** (block table = page table).
19. How do same-prompt requests save memory? → **COW block sharing**.
20. Three parallelism axes? → **data / tensor / pipeline**.
21. Gradient sync collective? → **all-reduce** (ring, NCCL).
22. Large-scale training bottleneck? → **interconnect + barriers**, not FLOPs.
23. Pipeline "bubble" fix? → **micro-batching**.
24. Warp divergence effect? → both branches run **serially** (throughput halved).
25. GPU partitioning for multi-tenancy? → **MIG** (virtualization, cf. M17).

**True/False**
- A GPU speeds up any program. → **False** (only data-parallel, low-divergence work).
- `cudaMemcpyAsync` from pageable memory overlaps compute. → **False** (silently sync).
- A warp switch costs a full context save/restore. → **False** (registers stay resident).
- PagedAttention needs contiguous KV memory. → **False** (that's the whole point:
  non-contiguous blocks).
- All-reduce acts like a barrier. → **True** (slowest GPU sets the pace).

---

## 19.14 One-Page Revision Sheet

```
WHY GPU: CPU=latency(few fast cores) ; GPU=throughput(1000s cores, SIMT).
OFFLOAD LIFECYCLE: (1)copy H2D  (2)launch kernel<<<grid,block>>>  (3)compute  (4)copy D2H.
  bottleneck = PCIe data movement (~tens GB/s) vs HBM ~TB/s -> OVERLAP copies w/ compute.

GPU SCHEDULING = MULTIPROGRAMMING in HW: many warps resident; on memory stall switch to a
  READY warp (context switch ~FREE). occupancy = resident/max warps (limited by regs+shared mem).
  block -> SM ; warp scheduler picks ready warp/cycle.

CUDA HIERARCHY: GRID > BLOCK (shares SHARED MEM, __syncthreads) > WARP (32, lockstep) > THREAD (regs).
  WARP=32 (block size multiple of 32). WARP DIVERGENCE: if/else in a warp -> both paths serial.

STREAMS: ordered queue; different streams overlap (copy engine || compute engine) = double buffering.
  default stream(0) SYNCHRONISES. async copy needs PINNED memory.

GPU MEM PYRAMID: registers(thread) > shared/L1(block, scratchpad) > L2 > GLOBAL/HBM > host RAM(PCIe).
  COALESCING: warp reads 32 consecutive -> 1 transaction (like SEQUENTIAL I/O); strided -> up to 32x.

PINNED (page-locked) MEM: OS can't page-out/move it -> stable phys addr -> DMA direct (faster+async).
  pageable => extra staging copy + sync. over-pinning = unswappable RAM starves system. (ties M2/M9/M10)

MULTI-GPU: NUMA affinity (GPU near its CPU/NIC); NVLink/GPUDirect P2P/RDMA = GPU<->GPU direct.
  DataLoader = producer/consumer (M7); workers via SHARED MEMORY IPC (M4); beware fork COW (M10).

LLM INFERENCE = MEMORY MGMT: KV-CACHE grows/token, per-request.
  KV bytes/token = 2 x layers x hidden x bytes (Llama13B fp16 ~0.78MiB/tok; 2048 tok ~1.6GiB).
  naive contiguous alloc -> internal+external FRAGMENTATION (M9).
  PAGEDATTENTION = PAGING: fixed KV blocks(~16 tok) + BLOCK TABLE (logical->physical). COW prefix share.
  serving = continuous batching (ready queue) + swap KV to host when HBM full (SWAPPING, M10).

DISTRIBUTED TRAIN: DATA(split batch, all-reduce grads) / TENSOR(split a layer) / PIPELINE(stages, bubble).
  all-reduce (ring/NCCL) ~2(N-1)/N x model bytes/step => NETWORK + BARRIER is the bottleneck, not FLOPs.
```

### Flash cards

| Front | Back |
|-------|------|
| CPU vs GPU core goal? | Latency vs throughput (SIMT) |
| Offload 4 steps? | copy H2D → launch → compute → copy D2H |
| Warp size? | 32 threads, lockstep |
| Grid ⊃ ? ⊃ ? ⊃ ? | block ⊃ warp ⊃ thread |
| Hides GPU memory latency? | Switch to a ready warp (many resident) |
| Streams give you? | Overlap of copy & compute (needs pinned) |
| Coalescing? | Warp's consecutive reads → 1 transaction |
| Why pinned memory? | Stable phys addr → DMA direct, async |
| PagedAttention ≈ ? | Paging the KV-cache (block table) |
| Prefix sharing uses? | Copy-on-write KV blocks |
| Gradient sync? | All-reduce (ring, NCCL) |
| Training bottleneck at scale? | Interconnect + barriers |

### Spaced repetition
- **24-hour:** recite the offload lifecycle, the CUDA hierarchy (grid/block/warp/
  thread, warp=32), and "PagedAttention = paging the KV-cache."
- **7-day:** explain warp-based latency hiding as multiprogramming; why pinned
  memory enables DMA (tie to M9/M10); coalescing as sequential I/O; the KV-cache
  numerical.
- **30-day:** given a slow GPU pipeline or an LLM-serving memory problem, diagnose
  it using OS vocabulary (overlap, paging, NUMA, all-reduce/barrier) end-to-end.

---

## 19.15 Summary

AI infrastructure is **operating-systems knowledge wearing new clothes**. A GPU is
a **throughput device** the host **offloads** to (copy in → launch → compute →
copy out), and its hardware **warp scheduler** hides memory latency by switching to
**ready warps** — **multiprogramming (M1)** in silicon. The **CUDA** model exposes a
**grid → block → warp(32) → thread** hierarchy; **streams** overlap copy with
compute (**double buffering, M13**); the **memory pyramid** (registers → shared →
HBM) and **coalescing** replay the CPU cache and **sequential-vs-random I/O**
lessons; and **pinned memory** only makes sense once you know **paging + DMA
(M2/M9/M10)**. Scaling out brings **NUMA**, **NVLink/RDMA**, and **shared-memory
IPC** for the data pipeline. Most strikingly, **LLM serving is a memory-management
problem**: the **KV-cache** grows per token, and **PagedAttention** manages it by
**paging** — fixed blocks + a block table + **copy-on-write** sharing — the exact
mechanism from **M9/M10**. And **distributed training** is a **synchronisation**
problem: **all-reduce** traffic and **barriers**, not FLOPs, cap scaling.

There is no "next module" beyond the perspective set; if you continue, **Module 20 —
The Backend-Engineering Perspective** shows the *other* place these OS primitives
resurface: high-concurrency servers (event loops, `epoll`, `io_uring`, load
balancing) built directly on scheduling (M6) and I/O (M13).

> **You have mastered this module when** you can: narrate the CPU→GPU offload
> lifecycle; explain warp-based latency hiding as multiprogramming; draw the CUDA
> grid/block/warp/thread hierarchy and say why warp=32 matters; justify pinned
> memory from paging + DMA; compute a KV-cache size; and explain **PagedAttention
> as paging** (with COW prefix sharing) and distributed training's **all-reduce/
> barrier** bottleneck — all in OS terms, without notes.
