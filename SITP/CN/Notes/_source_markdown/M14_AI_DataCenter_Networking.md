---
title: "Module 14 — AI & Data-Center Networking"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14 — AI & Data-Center Networking

> **Where this module sits.**
> Modern AI is a **networking** problem as much as a compute problem. Training a large
> model spreads work across **thousands of GPUs** that must exchange gradients **every
> step** — so the **network fabric** often decides how fast (and how big) you can train.
> This module covers the **data-center network** (spine-leaf), the fast transports
> (**RDMA/RoCE/InfiniBand**), **GPU interconnects** (NVLink), and **collective
> communication** (all-reduce). It ties the AI-infra story to everything you've learned.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend / AI |
|----------------|:-------:|:------:|:-------:|:---------:|:------------:|
| This module    | ★       | ★      | ★       | ★★★       | ★★★★★        |

**Most-asked concepts (interview / AI-infra):** **spine-leaf (Clos)** topology &
east-west traffic; **RDMA / RoCE / InfiniBand** (kernel-bypass, why); **GPU
interconnect (NVLink/NVSwitch)**; **collective ops (all-reduce)** for distributed
training; **network as the training bottleneck**; congestion control in DCs (ECN/PFC).

---

## 14.1 Why Data-Center Networking Is Different

- **East-west dominates:** traditional networks optimised **north-south** (user ↔
  server) traffic. AI/cloud DCs are dominated by **east-west** (server ↔ server) traffic
  — GPUs constantly exchanging data.
- **Ultra-low latency & high bandwidth** are required (microseconds, 100s of Gbps).
- **Lossless** matters: dropped packets stall collective operations, so DCs use
  congestion control that avoids loss (**ECN**, **PFC**).

> **Memory hook:** **the Internet is north-south (users↔servers); an AI data center is
> east-west (GPUs↔GPUs)** — that flips the whole network design.

### MCQs

1. Dominant traffic direction in an AI DC? → **east-west** (server↔server).
2. Two requirements DC networks emphasise? → **low latency + high bandwidth** (and
   lossless).
3. Why avoid packet loss in AI DCs? → drops **stall collective ops** (all GPUs wait).

---

## 14.2 Spine-Leaf (Clos) Topology

![Spine-leaf: every leaf switch connects to every spine, so any server-to-server path is the same two hops — uniform low latency and high bisection bandwidth.](images/36_spine_leaf.png)

- **Every leaf connects to every spine.** Any server-to-server path is **leaf → spine →
  leaf** — **at most 2 hops** (two servers under the *same* leaf are just 1 hop),
  giving **predictable latency** and **high bisection
  bandwidth**.
- Replaces the old **3-tier tree** (core/aggregation/access), which bottlenecked
  east-west traffic and had uneven path lengths.
- Scales by **adding spines** (more bandwidth) or **leaves** (more servers).

> **Memory hook:** **spine-leaf = "everyone is 2 hops from everyone"** — flat, uniform,
> and easy to scale, unlike the tall old tree.

### MCQs

1. Server-to-server hop count in spine-leaf? → **2** (leaf → spine → leaf).
2. What does spine-leaf maximise? → **bisection bandwidth** (uniform, non-blocking).
3. Add bandwidth by adding? → **spines** (servers by adding leaves).

---

## 14.3 Fast Transports — RDMA, RoCE, InfiniBand

Normal TCP/IP copies data through the **kernel** and CPU — too slow for GPU-scale
traffic. **RDMA (Remote Direct Memory Access)** lets one machine read/write another's
**memory directly**, **bypassing the kernel and CPU** (zero-copy, ultra-low latency).

- **InfiniBand:** a dedicated high-speed interconnect with native RDMA (common in HPC/AI
  supercomputers).
- **RoCE (RDMA over Converged Ethernet):** RDMA on standard Ethernet (needs lossless
  config — **PFC/ECN**).
- Benefit: **microsecond** latency and CPU offload, essential for collective ops.

> **Memory hook:** **RDMA = "write straight into the other machine's RAM, skip the OS
> kernel."** InfiniBand = dedicated fabric; RoCE = RDMA on Ethernet.

### MCQs

1. What does RDMA bypass? → the **kernel/CPU** (zero-copy, direct memory).
2. RDMA on standard Ethernet is called? → **RoCE**.
3. Dedicated RDMA fabric common in AI clusters? → **InfiniBand**.

---

## 14.4 GPU Interconnects (inside & across nodes)

- **Within a server:** **NVLink / NVSwitch** connect GPUs directly at up to **~TB/s**
  (NVSwitch aggregate), far
  faster than PCIe — so 8 GPUs act almost like one.
- **Across servers:** **InfiniBand / RoCE** NICs (often GPUDirect RDMA — NIC reads GPU
  memory directly, skipping the CPU).
- **Hierarchy of speeds:** GPU memory (HBM) > NVLink (intra-node) > InfiniBand/RoCE
  (inter-node) > general Ethernet. Training performance depends on keeping data in the
  **fastest tier** possible.

### MCQs

1. Intra-server GPU-to-GPU link? → **NVLink / NVSwitch**.
2. Inter-server GPU transport? → **InfiniBand / RoCE** (GPUDirect RDMA).
3. Fastest memory tier for a GPU? → its own **HBM**.

---

## 14.5 Collective Communication — All-Reduce

Data-parallel training replicates the model on every GPU; each computes gradients on its
data shard, then **all GPUs must average their gradients every step** — a **collective
operation** called **all-reduce**.

![Ring all-reduce: each GPU passes partial sums around a ring until every GPU holds the same averaged gradient; the interconnect bandwidth caps how fast this completes.](images/37_all_reduce.png)

- **Ring all-reduce** (used by **NCCL**): GPUs form a ring and pass partial sums around,
  so bandwidth use is optimal and independent of GPU count.
- Other collectives: **broadcast, all-gather, reduce-scatter**.
- **This is the bottleneck:** as models/clusters grow, **network bandwidth for
  all-reduce** — not raw GPU FLOPs — often limits training speed. Hence NVLink +
  InfiniBand + lossless fabrics.

**Parallelism strategies** (why the network is stressed): **data parallelism** (each
GPU a data shard, all-reduce gradients), **model/tensor parallelism** (split a layer
across GPUs), **pipeline parallelism** (split layers across GPUs). All require heavy
inter-GPU communication.

> **Memory hook:** **training = compute a gradient, then all-reduce it across every
> GPU, every step.** The faster the fabric, the faster (and bigger) you can train.

### MCQs

1. Op that averages gradients across GPUs? → **all-reduce**.
2. Library implementing ring all-reduce? → **NCCL**.
3. Common training bottleneck at scale? → **network bandwidth** (all-reduce), not FLOPs.

---

## 14.6 Serving & Inference Networking (brief)

- **LLM inference** is latency-sensitive: **KV-cache** memory and **fast token
  streaming** matter; requests are **load-balanced** across GPU servers (M12).
- **Model/tensor parallel serving** spreads a huge model across GPUs → inter-GPU
  communication on the critical path of every token.
- **Edge/CDN + 5G** (M11–M12) push inference closer to users for low latency.

### MCQs

1. What's load-balanced across GPU servers for inference? → **requests** (M12 LB).
2. Serving a model too big for one GPU needs? → **model/tensor parallelism** (inter-GPU
   comms).

---

## 14.7 Real-World & Interview Perspectives

- **AI-infra interviews** ask: "why InfiniBand/RDMA?", "what's all-reduce?", "why
  spine-leaf?", "what bottlenecks large-scale training?" — the answers are all here.
- **The network is a first-class citizen** of AI systems — cluster design (fabric,
  topology, lossless config) directly determines training throughput and cost.
- Ties to the **OS notes' AI module** (GPU scheduling, CUDA, NCCL) — networking is the
  inter-node half of that story.

---

## 14.8 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** assuming GPUs are the only bottleneck — at scale, **the network
  (all-reduce bandwidth)** often is.
- **Mistake:** using plain TCP for GPU traffic — too much CPU/kernel overhead; use
  **RDMA**.
- **Trap:** RoCE needs a **lossless** Ethernet (PFC/ECN) — drops devastate collectives.
- **Edge case:** north-south-optimised (3-tier) designs bottleneck AI's **east-west**
  traffic → spine-leaf.

---

## 14.9 Concept Checks & MCQs (test yourself)

1. Traffic direction dominating AI DCs? → **east-west**.
2. Server-to-server hops in spine-leaf? → **2**.
3. What does RDMA bypass? → **kernel/CPU** (direct memory).
4. RDMA on Ethernet? → **RoCE**; dedicated fabric? → **InfiniBand**.
5. Intra-node GPU link? → **NVLink/NVSwitch**.
6. Gradient-averaging collective? → **all-reduce** (NCCL, ring).
7. Common large-scale training bottleneck? → **network bandwidth**.
8. Three parallelism strategies? → **data, model/tensor, pipeline**.
9. Why lossless fabric for AI? → drops **stall collectives**.
10. Old topology that bottlenecks east-west? → **3-tier tree**.

---

## 14.10 One-Page Revision Sheet

```
AI/DC NETWORKING: traffic is EAST-WEST (GPU<->GPU), needs ultra-low latency + high bw + LOSSLESS.

SPINE-LEAF (Clos): every leaf <-> every spine => any server-server = 2 hops (leaf-spine-leaf).
  uniform latency, high BISECTION bandwidth. scale: +spines(bw) / +leaves(servers). replaces 3-tier tree.

FAST TRANSPORT: RDMA = read/write remote RAM directly, BYPASS kernel/CPU (zero-copy, microseconds).
  InfiniBand = dedicated RDMA fabric ; RoCE = RDMA over (lossless) Ethernet (needs PFC/ECN).

GPU INTERCONNECT: intra-node NVLink/NVSwitch (TB/s) > PCIe ; inter-node InfiniBand/RoCE + GPUDirect RDMA.
  speed tiers: HBM > NVLink > InfiniBand/RoCE > Ethernet.

COLLECTIVES: data-parallel training -> ALL-REDUCE gradients EVERY step (ring all-reduce, NCCL).
  parallelism: DATA(shard data, all-reduce) | MODEL/TENSOR(split a layer) | PIPELINE(split layers).
  BOTTLENECK at scale = network bandwidth (all-reduce), not GPU FLOPs.

INFERENCE: requests load-balanced across GPU servers; big models -> tensor-parallel (inter-GPU on token path).
```

### Flash cards

| Front | Back |
|-------|------|
| AI DC traffic direction | east-west (GPU↔GPU) |
| Spine-leaf hop count | 2 (leaf→spine→leaf) |
| RDMA bypasses | kernel/CPU (direct memory) |
| RDMA on Ethernet / dedicated | RoCE / InfiniBand |
| Intra-node GPU link | NVLink / NVSwitch |
| Gradient sync op | all-reduce (NCCL ring) |
| Scale-training bottleneck | network bandwidth |
| Parallelism types | data / model-tensor / pipeline |
| Why lossless fabric | drops stall collectives |
| Replaces 3-tier tree | spine-leaf (Clos) |

### Spaced repetition
- **24-hour:** east-west vs north-south; spine-leaf 2-hop; RDMA bypasses kernel.
- **7-day:** InfiniBand vs RoCE; NVLink; ring all-reduce + NCCL.
- **30-day:** explain why the network (not GPUs) bottlenecks large-scale training —
  without notes.

---

## 14.11 Summary

AI is a **networking** story: training spreads across **thousands of GPUs** that must
**all-reduce gradients every step**, so the **fabric** often bounds performance. AI data
centers are **east-west** dominated and use **spine-leaf (Clos)** topologies for uniform
**2-hop** paths and high bisection bandwidth. To move data fast they use **RDMA**
(kernel-bypass, zero-copy) over **InfiniBand** or **RoCE** (lossless Ethernet), with
**NVLink/NVSwitch** connecting GPUs inside a node. **Collective operations** — especially
**ring all-reduce (NCCL)** — synchronise gradients, and at scale the **network
bandwidth**, not GPU FLOPs, is the bottleneck. The same fabric serves latency-sensitive
**inference**.

Next, **Module 15 — Competitive Exams** consolidates the whole subject into a
topic × exam map, high-yield facts, and solved MCQs.

> **You have mastered this module when** you can: explain east-west vs north-south;
> describe spine-leaf and its 2-hop property; say what RDMA bypasses and contrast
> InfiniBand vs RoCE; explain all-reduce and the three parallelism strategies; and state
> why the network bottlenecks large-scale AI training — all without notes.
