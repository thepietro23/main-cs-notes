---
title: "Module 11 — Scaling ML Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — Scaling ML Systems

> **Why this module matters.**
> Almost every real ML system starts small and then, if it is any good, gets
> *big*. A demo that serves 10 requests a second on your laptop is a completely
> different animal from a system serving 100,000 requests a second across a
> fleet of machines, training on 1000s of GPUs, and looking up embeddings from a
> table too large to fit on one box. Scaling is where the *systems* half of "ML
> system design" earns its name. This is the module where interviewers stop
> asking about models and start asking "what breaks at 100× traffic, and what do
> you change?" We answer that from first principles: what a bottleneck *is*, why
> you scale data, training, and serving **separately**, and why you can never
> get low cost, low latency, and high throughput all at once.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★★         | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
explain why data, training, and serving scale on *independent* axes; define
sharding, replication, and partitioning and say when to use each; explain the
all-reduce communication bottleneck that caps distributed training and size it
roughly; size a large embedding table with the `N × d × 4 bytes` rule and give
two ways to shrink it (sharding, the hashing trick); contrast horizontal vs
vertical scaling and describe autoscaling inference on QPS/latency; draw the
cost / latency / throughput trade-off triangle and explain why you can only
pick two; and walk through a concrete "1k QPS → 100k QPS" scaling story.

> **How to read this module.** As always we go **problem → simplest attempt →
> why it breaks → the fix**. Scaling is nothing but a chain of bottlenecks: you
> find the one thing that is saturated, fix *that*, and move to the next. The
> whole art is knowing which knob to turn.

---

## 11.1 The Three Independent Axes of Scaling

### Motivation (the problem that existed)

A beginner hears "scale the ML system" and reaches for one lever — usually "add
more servers". But an ML system is really *three* systems glued together, and
each one saturates for a different reason:

- The **data** side can run out of storage or read bandwidth.
- The **training** side can run out of compute or, more often, network
  bandwidth between GPUs.
- The **serving** side can run out of QPS capacity or blow its latency budget.

Adding serving replicas does nothing for a training job that is bottlenecked on
gradient communication, and buying more GPUs does nothing for a feature store
that is too big for one disk. You must diagnose *which* axis is saturated.

### Definition

**Scaling** means increasing a system's capacity to handle more work (more data,
more compute, more requests) while keeping its quality and latency acceptable.
The key insight of this module: **data, training, and serving scale
independently**, on separate axes, with separate bottlenecks and separate fixes.

![An ML system splits into three scaling axes — data, training, and serving — each with its own bottleneck and its own fix.](images/m11_01_three_axes.png)

### Intuition & analogy

Think of a restaurant. The **pantry** (data) can be too small to hold the
ingredients. The **kitchen** (training) can be too slow to cook the day's prep.
The **dining room / waiters** (serving) can be too few to seat the dinner rush.
A bigger pantry does not seat more diners; more waiters do not cook faster. You
size each part for *its own* load. An ML system is the same: you scale the axis
that is actually the bottleneck, not whichever one is easiest to think about.

### First-principles: find the bottleneck first

Every scaling problem reduces to one question: **what resource is saturated?**

1. Measure. Look at utilization — is the disk full, the GPU network pinned, the
   serving CPU at 100%, the latency p99 blown?
2. Identify the single tightest constraint (there is almost always exactly one).
3. Relax *that* constraint (shard the data, add GPUs, add replicas, cache).
4. Re-measure. The bottleneck usually *moves* to the next resource. Repeat.

> **Senior signal:** a strong candidate never says "just add more machines". They
> say "let me find the bottleneck first — is this data-bound, compute-bound, or
> request-bound?" and then scale the matching axis.

---

## 11.2 Scaling Data: Sharding, Replication, Partitioning

### Motivation

Your training data, feature store, and embedding tables can grow past what one
machine can hold or serve. A single node has a fixed disk, fixed RAM, and fixed
read bandwidth. Once you exceed any of these, you must **spread the data across
many machines** — but there are two very different reasons to do so, and mixing
them up is a classic mistake.

![Sharding splits data across nodes for capacity; replication copies the same data for read throughput and availability.](images/m11_02_shard_replicate.png)

### The three words (and what they actually mean)

- **Partitioning** = the general idea of *dividing* data into chunks. Sharding is
  one kind of horizontal partitioning.
- **Sharding** = split the data itself **across** nodes so each node holds a
  *different slice* (e.g. users A–M on node 1, N–Z on node 2). Motive:
  **capacity** — the whole dataset is too big for one node. Each shard is
  smaller and independently servable.
- **Replication** = keep **full copies** of the same data on several nodes.
  Motive: **read throughput and availability** — many replicas can answer reads
  in parallel, and if one dies the others still serve.

You usually use **both together**: shard for size, then replicate each shard for
reads and safety. This is exactly how large feature stores and embedding
services are laid out.

### How you pick a shard key

The shard key decides which node a row lives on. Good keys spread load *evenly*.

- **Hash partitioning** — `node = hash(key) mod N`. Spreads uniformly; great for
  point lookups (get features for user X). The downside: range scans ("all users
  created in June") hit every shard.
- **Range partitioning** — contiguous key ranges per node. Good for range scans,
  but risks **hot shards** if recent keys are the busiest (everyone reads
  "today").

> **The classic failure: a hot shard.** If one celebrity user, or one popular
> item, lives on a single shard and gets 90% of the traffic, that shard melts
> while the others idle. Fixes: hash the key, add a replica just for the hot key,
> or cache the hot key separately. Interviewers love to poke at hot keys.

### Edge cases

- **Rebalancing.** Adding a shard means moving data. Naive `mod N` reshuffles
  *everything* when `N` changes; **consistent hashing** moves only a small
  fraction — know the term.
- **Cross-shard joins are expensive.** If a query needs data from many shards,
  you pay a scatter-gather cost. Design keys so common queries hit one shard.

---

## 11.3 Distributed Training at Scale (and the Communication Bottleneck)

### Motivation

Large models train on datasets and parameter counts too big for one GPU. The
obvious fix is "use 1000 GPUs" — but here is the trap that surprises everyone:
**past a certain point, adding GPUs stops helping, because the GPUs spend more
time *talking to each other* than computing.** Training at scale is a
*communication* problem, not just a compute problem. (This builds directly on
the distributed-training material in **Module 6** — revisit it if the parallelism
types are hazy.)

![In data-parallel training each GPU computes gradients on its own shard, then all-reduce sums and shares them so every GPU stays in sync.](images/m11_03_distributed_training.png)

### The two ways to split a training job

- **Data parallelism** (most common). Every GPU holds a *full copy* of the model
  but processes a *different slice* of the batch. After each step they must
  **average their gradients** so all copies stay identical. That averaging step
  is called **all-reduce**, and it is where the network cost lives.
- **Model parallelism** (for models too big for one GPU). The *model itself* is
  split across GPUs — different layers or different tensor shards on different
  devices. Now activations must flow between GPUs on every forward/backward pass.

### First-principles: why all-reduce is the bottleneck

In data parallelism, every training step does:

```
1. each GPU computes a gradient on its mini-batch      (compute)
2. ALL-REDUCE: sum gradients across all GPUs, share back (communication)
3. each GPU applies the same averaged gradient          (compute)
```

Step 2 must move data proportional to the *model size* across the network, on
**every** step. If the model has billions of parameters, that is gigabytes moved
per step. Compute scales with more GPUs, but the communication does **not** get
free — it is limited by **network bandwidth** (how many GB/s between nodes) and
**latency**. So:

- Add GPUs → each does less compute per step (good).
- But the all-reduce still has to move ~the whole gradient every step (fixed
  cost that does not shrink, and can even grow with more participants).

Eventually communication dominates and adding GPUs yields almost nothing. This
is why fast interconnects (NVLink, InfiniBand) and tricks like **gradient
compression**, **overlapping communication with computation**, and **larger
batches** (fewer, bigger sync steps) matter so much at scale.

> **Interview one-liner:** "Distributed training is usually bandwidth-bound, not
> FLOP-bound. The all-reduce of gradients on every step is the wall." Saying this
> marks you as someone who has actually scaled training.

### Edge cases & failure modes

- **Stragglers.** All-reduce waits for the *slowest* GPU. One slow node stalls
  1000 fast ones. Fixes: health checks, backup workers.
- **Batch size too large.** Huge global batches reduce sync frequency but can
  hurt model quality (needs learning-rate warmup / scaling rules).
- **Fault tolerance.** At 1000s of GPUs, hardware *will* fail mid-run.
  Checkpoint often so you can restart without losing days of work.

---

## 11.4 Large-Scale Embedding Tables

### Motivation

Recommenders, ads, and search represent every user, item, video, or word as a
learned vector called an **embedding**. The problem: there can be *hundreds of
millions* of items, each needing its own vector. Store one row per item and the
table alone can be **tens or hundreds of gigabytes** — far more than a single
GPU's memory, and often the single biggest object in the whole system.

![Size an embedding table with N x d x 4 bytes; shrink it by sharding across parameter servers or by hashing ids into a fixed-size table.](images/m11_04_embeddings.png)

### The sizing rule (memorise this)

An embedding table is `N` rows (one per item) × `d` numbers per row (the
dimension) × the bytes per number. In `float32`, each number is **4 bytes**:

```
table size = N × d × 4 bytes
```

**Worked example.** 100 million items, embedding dimension 128:

```
100,000,000 × 128 × 4 bytes
  = 100e6 × 512 bytes
  = 51.2e9 bytes
  ≈ 51 GB
```

That single table does **not** fit on one GPU (typically 16–80 GB, shared with
the rest of the model). Two standard fixes:

### Fix A — Sharded embeddings (parameter servers)

Split the table by row across several machines (**parameter servers**). Row 0–33M
on PS 1, 33M–66M on PS 2, and so on. A training or serving worker that needs the
vector for item *X* looks up `X`'s shard and fetches just that row. This is
sharding (Section 11.2) applied to a model parameter. It removes the capacity
ceiling but adds a network hop per lookup.

### Fix B — The hashing trick (for huge / open vocabularies)

Sometimes the vocabulary is effectively unbounded (every URL, every search
query, new user IDs every second). You cannot pre-allocate a row for each. The
**hashing trick** fixes memory by *forcing* everything into a fixed-size table:

```
row_index = hash(id) mod M      # M is a fixed, chosen table size
```

You pick `M` (say 10 million rows) up front, so memory is capped no matter how
many distinct IDs appear. The cost: **collisions** — two different IDs can map
to the same row and share a vector. In practice a small collision rate barely
hurts quality, and it is a great trade for bounded memory. (Using several
independent hash functions — the "hashing trick" with multiple hashes — reduces
collision damage.)

> **When to use which:** shard when you *can* enumerate items and just need more
> capacity; hash when the vocabulary is huge, open-ended, or long-tailed and you
> want a hard memory cap.

---

## 11.5 Scaling Serving: Horizontal vs Vertical, and Autoscaling

### Motivation

Serving is the axis interviewers push hardest, because it is user-facing: it has
a **latency budget** (p99 < X ms) *and* a **throughput target** (QPS) *and* a
**cost budget**, all at once. The first question is *how* you add capacity.

![Vertical scaling makes one box bigger and hits a ceiling; horizontal scaling adds many boxes behind a load balancer.](images/m11_05_horiz_vs_vert.png)

### Vertical vs horizontal scaling

- **Vertical scaling (scale up)** = make one machine bigger (more CPU, RAM, a
  beefier GPU). *Simple* — no code changes, no distribution. But it hits a
  **hard ceiling** (there is a biggest machine you can buy), it is expensive at
  the top end, and it is a single point of failure.
- **Horizontal scaling (scale out)** = add *many* machines behind a **load
  balancer**. Scales almost without limit and survives node failures. The
  requirement: your service must be **stateless** (any replica can handle any
  request) so requests can be spread freely. This is the preferred pattern for
  ML inference.

> **Rule of thumb:** scale *up* first because it is easy; scale *out* when you
> hit the ceiling, need high availability, or need to grow past one box. Real
> systems do both: reasonably large boxes, many of them.

### Autoscaling inference

Traffic is rarely flat — it has daily peaks, spikes, and quiet nights. Paying for
peak capacity 24/7 wastes money; paying for average capacity drops requests at
peak. **Autoscaling** adds and removes replicas automatically based on a live
signal.

![An autoscaler watches QPS and p99 latency, adds replicas when load is high, and removes them when load is low to save cost.](images/m11_06_autoscaling.png)

- **What to scale on.** The usual signals are **QPS per replica** (e.g. keep each
  pod under 200 QPS) and **latency** (e.g. add replicas if p99 climbs toward the
  budget). CPU/GPU utilization is a common proxy.
- **Scale out** when the signal crosses a high threshold; **scale in** when it
  drops, to save cost.
- **The cold-start trap.** New replicas take time to boot, load the model into
  memory (a big model can take tens of seconds), and warm caches. If you only
  react *after* traffic spikes, latency blows up during the boot window. Fixes:
  keep a **warm minimum pool**, pre-load models, and scale on a *leading*
  signal (queue length) rather than a lagging one.

### Edge cases

- **Flapping.** Scaling in and out repeatedly wastes work; add cooldowns and
  hysteresis.
- **Downstream limits.** Scaling serving replicas is useless if they all hammer
  one feature store or database that then becomes the bottleneck (back to
  Section 11.2 — shard/replicate it too).

---

## 11.6 The Cost / Latency / Throughput Trade-off (and a Worked Example)

### Motivation

New engineers want to "make it fast, cheap, *and* high-capacity". You cannot.
These three goals pull against each other, and every serving decision is really
a choice about *which one you sacrifice*.

![The trade-off triangle: low latency, low cost, and high throughput — you can optimize for two, but not all three at once.](images/m11_07_tradeoff_triangle.png)

### The trade-off triangle (pick two)

- **Latency** = how long one request takes (p50, p99).
- **Throughput** = how many requests per second the system handles.
- **Cost** = dollars of hardware to do it.

Why you cannot max all three:

- **Batching** requests together uses the GPU efficiently → **high throughput,
  low cost per request**, but each request now *waits* for the batch to fill →
  **higher latency**.
- **Serving one request at a time** on a dedicated fast replica → **low
  latency**, but the GPU sits idle between requests → **low throughput, high
  cost**.
- **Adding replicas** cuts queueing latency and lifts throughput → but **costs
  more**.

So you pick the two that matter for the product and *give* on the third. A search
box picks low latency + high throughput and pays for it. A nightly batch job
picks low cost + high throughput and does not care about latency.

### Worked scaling example: 1k QPS → 100k QPS (100×)

A favourite interview prompt: *"Your system does 1,000 QPS on one server. Traffic
grows 100× to 100,000 QPS. What changes?"* The senior answer is: **almost none of
it is about the model — it is systems work.**

![Scaling from 1k to 100k QPS is a systems problem: replicate stateless servers, cache hot predictions, batch on GPUs, shard the store, and autoscale.](images/m11_08_scaling_example.png)

Walk through it in order:

1. **Replicate stateless servers behind a load balancer** (Section 11.5). If one
   box does 1k QPS, you need roughly 100 of them — plus headroom for peaks and
   failures, so budget ~130–150. This is the main lever.
2. **Cache hot predictions.** Many requests repeat (same popular item, same
   query). A cache serving even 40% of traffic removes 40% of the compute — the
   cheapest 100× trick there is.
3. **Batch requests and use the GPU efficiently.** Group incoming requests into
   small batches to raise throughput per replica (accepting a little latency, per
   the triangle).
4. **Shard the feature store / embedding table** (Sections 11.2, 11.4). At 100k
   QPS the *data lookups* become the bottleneck, not the model. Shard and
   replicate the store so it keeps up.
5. **Autoscale on QPS + p99** (Section 11.5) so you run ~100 replicas at peak and
   far fewer at 3 a.m., instead of paying for peak all day.
6. **Watch the triangle.** More replicas fix latency but cost more; bigger batches
   cut cost but add latency. State your budget and choose deliberately.

> **What does NOT change:** the model architecture, usually. Scaling 100× is
> about replication, caching, batching, sharding, and autoscaling — not a bigger
> network. Candidates who answer "train a bigger model" have misread the
> question.

### Back-of-envelope check

Always sanity-check capacity:

```
replicas needed ≈ target QPS ÷ QPS per replica
100,000 QPS ÷ ~1,000 QPS per replica ≈ 100 replicas (before cache + headroom)
```

A cache hit rate of 40% means only ~60,000 QPS reach the model → ~60 replicas.
This kind of quick arithmetic, out loud, is exactly what interviewers want.

---

## Module 11 — Interview Mapping (what companies probe)

| Company | How Module 11 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | "Scale this recommender to 100k QPS" | "Add servers" | Replicate + cache + shard embeddings + autoscale; names the bottleneck each step |
| **Amazon** | Cost vs latency trade-offs at scale | Ignores cost | Uses the triangle; batches for cost, keeps a latency SLO, sizes replicas |
| **OpenAI / Anthropic** | Distributed training of large models | "Use more GPUs" | Explains the all-reduce bandwidth wall, overlap, checkpointing, stragglers |
| **Uber / Stripe** | Hot shards, feature-store scaling | One shard key | Flags hot keys, uses consistent hashing, replicates hot shards |

**The single most common opening question:** *"It works at small scale — what
breaks at 100×?"* Answer with the three-axes framing (data / training / serving),
find the bottleneck, and fix it with replication, caching, sharding, and
autoscaling — while naming the cost/latency/throughput trade-off out loud.

---

## Module 11 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask *general* distributed-systems terms — sharding vs
  replication, horizontal vs vertical scaling, load balancing. Sections 11.2 and
  11.5 cover the definitions likely to appear. ML-specific scaling is
  essentially **interview-only**.
- **GATE CS / DA:** partitioning, hashing, and consistent hashing show up in DBMS
  and distributed-systems topics; the `N × d × 4 bytes` sizing arithmetic is fair
  game as a numeric question. Deep training-communication tradeoffs are not
  tested.
- **ISRO / DRDO:** occasional basic parallel/distributed computing definitions
  only.

> **Flag:** the distributed-training and autoscaling internals here are
> **interview / role** material, not written-exam material. The reusable exam
> value is the vocabulary (shard, replica, partition, horizontal/vertical) and
> the sizing arithmetic.

---

## Module 11 — Common Mistakes & Misconceptions

1. **"Scaling = add more servers."** Only for the *serving* axis, and only if the
   bottleneck is there. Training and data scale differently. (Section 11.1.)
2. **"Sharding and replication are the same."** No — sharding splits data for
   *capacity*; replication copies it for *read throughput and availability*.
   (Section 11.2.)
3. **"More GPUs always trains faster."** No — the all-reduce communication cost
   caps it; past a point you are bandwidth-bound. (Section 11.3.)
4. **"Just fit the embedding table in memory."** A 100M × 128 table is ~51 GB;
   you must shard it or use the hashing trick. (Section 11.4.)
5. **"Autoscaling is instant."** Cold starts (model load, warmup) mean new
   replicas lag; keep a warm minimum pool. (Section 11.5.)
6. **"We can be fast, cheap, and high-throughput."** Pick two — batching trades
   latency for throughput/cost. (Section 11.6.)
7. **"To handle 100× traffic, train a bigger model."** Scaling traffic is a
   systems problem (replicate, cache, shard), not a modelling one. (Section 11.6.)

---

## Module 11 — MCQs (with answers & explanations)

**Q1.** What is the main difference between sharding and replication?
a) They are the same thing
b) Sharding splits data across nodes for capacity; replication copies it for
   read throughput and availability
c) Replication splits data; sharding copies it
d) Sharding only applies to GPUs

<details><summary>Answer</summary>**b.** Sharding gives each node a *different*
slice (motive: capacity). Replication puts *full copies* on many nodes (motive:
more reads + high availability). Big systems do both.</details>

**Q2.** In large-scale data-parallel training, why does adding more GPUs
eventually stop speeding things up?
a) GPUs get slower with age
b) The all-reduce of gradients every step is bandwidth-bound and does not shrink
c) The dataset runs out
d) Python is single-threaded

<details><summary>Answer</summary>**b.** Every step must sync (all-reduce)
gradients across all GPUs over the network. That communication cost is limited by
bandwidth and does not fall as you add GPUs, so it eventually dominates.</details>

**Q3.** An embedding table has 100 million items and dimension 128, stored as
float32. Roughly how big is it?
a) ~51 MB  b) ~5 GB  c) ~51 GB  d) ~512 GB

<details><summary>Answer</summary>**c.** 100e6 × 128 × 4 bytes = 51.2e9 bytes ≈
**51 GB**. Use the rule `N × d × 4 bytes`.</details>

**Q4.** The "hashing trick" for embeddings mainly buys you:
a) Zero collisions
b) A fixed, capped memory footprint regardless of vocabulary size (at the cost of
   some collisions)
c) Faster training only
d) Better accuracy always

<details><summary>Answer</summary>**b.** `row = hash(id) mod M` forces every id
into a table of fixed size `M`, so memory is bounded even for huge/open
vocabularies. The price is occasional collisions, usually harmless.</details>

**Q5.** You must serve 100k QPS but one server handles 1k QPS. What is the
*primary* change?
a) Train a bigger model
b) Replicate stateless servers behind a load balancer (~100+), add caching and
   sharding
c) Switch programming languages
d) Increase the learning rate

<details><summary>Answer</summary>**b.** 100× traffic is a systems problem:
horizontal replication behind a load balancer, plus caching hot predictions and
sharding the feature store. The model usually stays the same.</details>

**Q6.** Batching requests on a GPU server mainly does what to the trade-off
triangle?
a) Improves all three of latency, throughput, cost
b) Raises throughput and lowers cost per request, but *increases* latency
c) Lowers throughput
d) Has no effect

<details><summary>Answer</summary>**b.** Batching uses the GPU efficiently (more
throughput, less cost per request) but each request waits for the batch to fill,
so latency rises. You cannot win on all three at once.</details>

**Q7.** A single celebrity account causes one shard to receive most of the
traffic while others idle. This is called:
a) A cache miss  b) A hot shard / hot key  c) Overfitting  d) A cold start

<details><summary>Answer</summary>**b.** A **hot shard**. Fixes: hash the key,
replicate the hot shard, or cache the hot key separately.</details>

---

## Module 11 — Design Exercises (easy → hard)

- **Easy.** For each, say sharding or replication (or both): (1) the dataset is
  too big for one disk; (2) reads are overwhelming one node but data fits;
  (3) you need the store to survive a node failure. *(1 shard, 2 replicate,
  3 replicate.)*
- **Easy.** Size an embedding table: 500M items, dimension 64, float32. Does it
  fit on an 80 GB GPU? *(500e6 × 64 × 4 = 128 GB → no; shard or hash.)*
- **Medium.** A distributed training run uses 512 GPUs but is only ~1.5× faster
  than 256 GPUs. Explain why and list three fixes.
- **Medium.** Design autoscaling for an inference service with a strict p99 <
  80 ms SLO and spiky traffic. What signal do you scale on, and how do you handle
  cold starts?
- **Hard.** Your recommender serves 5k QPS today and must reach 250k QPS for a
  product launch. Walk through every axis (data, training, serving) and state the
  bottleneck you expect at each 10× step.
- **Hard.** You must serve a recommender with a 40 ms p99 budget *and* keep cost
  low. Use the trade-off triangle to justify your batching and replica choices,
  and say explicitly which corner you sacrifice.

---

## Module 11 — Concept Review (one page)

- **Three axes:** data, training, and serving scale **independently**, each with
  its own bottleneck. Always find the saturated resource *first*.
- **Sharding** splits data across nodes for **capacity**; **replication** copies
  it for **read throughput + availability**; **partitioning** is the umbrella
  term. Watch for **hot shards**; prefer **consistent hashing** for rebalancing.
- **Distributed training** is usually **bandwidth-bound**: the per-step
  **all-reduce** of gradients caps how far you can scale GPUs. Overlap comms,
  compress gradients, checkpoint, handle stragglers. (Cross-link **Module 6**.)
- **Embedding tables:** size = **N × d × 4 bytes** (float32). 100M × 128 ≈ 51 GB.
  Shrink by **sharding** across parameter servers or the **hashing trick**
  (`hash(id) mod M`, collisions OK) for huge/open vocabularies.
- **Serving:** **vertical** (scale up, simple, capped) vs **horizontal** (scale
  out, needs statelessness + load balancer, preferred). **Autoscale** on QPS /
  p99; beware **cold starts** → keep a warm minimum pool.
- **Trade-off triangle:** low latency, low cost, high throughput — **pick two**.
  Batching trades latency for throughput/cost.
- **100× traffic** is a *systems* problem: replicate, cache, batch, shard,
  autoscale — **not** a bigger model.

---

## Module 11 — Flash Cards (Q → A)

1. Three independent scaling axes? → *Data, training, serving.*
2. Sharding vs replication? → *Shard = split for capacity; replicate = copy for
   reads + availability.*
3. Why do extra GPUs stop helping training? → *All-reduce is bandwidth-bound and
   runs every step.*
4. Embedding table sizing rule? → *N × d × 4 bytes (float32).*
5. 100M items × 128 dims ≈ ? → *~51 GB.*
6. What does the hashing trick buy? → *Fixed capped memory for huge vocab, at the
   cost of collisions.*
7. Horizontal scaling requires what? → *Stateless servers + a load balancer.*
8. Autoscaling's main gotcha? → *Cold starts; keep a warm minimum pool.*
9. Trade-off triangle corners? → *Latency, throughput, cost — pick two.*
10. Primary fix for 100× QPS? → *Replicate stateless servers + cache + shard, not
    a bigger model.*

---

## Module 11 — Pattern Recognition (how to spot it in an interview)

- Hear **"what breaks at 100× scale?"** → three axes → find bottleneck →
  replicate, cache, shard, autoscale.
- Hear **"data too big for one machine"** → *sharding / partitioning* (+ replicate
  each shard).
- Hear **"reads are overwhelming the store"** → *replication* + caching.
- Hear **"training on 1000s of GPUs is not getting faster"** → *all-reduce
  bandwidth bottleneck*, stragglers, overlap comms.
- Hear **"huge / open vocabulary of IDs"** → *hashing trick* for a fixed table.
- Hear **"tight latency budget AND low cost"** → *trade-off triangle*; batch
  carefully, size replicas, name the sacrificed corner.
- Hear **"traffic is spiky"** → *autoscaling* on QPS/p99 + warm pool for cold
  starts.

---

## Module 11 — Revision Notes / Mini Cheat Sheet

```
THREE AXES:  DATA  |  TRAINING  |  SERVING   (scale each independently)
STEP 0 ALWAYS: find the saturated resource FIRST, then fix that one.

DATA SCALING
  SHARD      = split data across nodes      -> for CAPACITY (too big)
  REPLICATE  = full copies on many nodes     -> for READS + AVAILABILITY
  PARTITION  = umbrella term; hash vs range; beware HOT SHARDS
             -> consistent hashing for cheap rebalancing

TRAINING SCALING (see M06)
  data-parallel: each GPU full model, diff batch slice -> ALL-REDUCE gradients
  ALL-REDUCE cost ~ model size, EVERY step -> BANDWIDTH-BOUND
  => more GPUs eventually stops helping; overlap comms, compress, checkpoint

EMBEDDING TABLES
  size = N x d x 4 bytes (float32)      100M x 128 x 4B ~= 51 GB
  fix A: SHARD across parameter servers (capacity)
  fix B: HASHING TRICK  row = hash(id) mod M  (capped memory, collisions OK)

SERVING SCALING
  VERTICAL (scale up)   : simple, capped, single point of failure
  HORIZONTAL (scale out): stateless + load balancer; preferred
  AUTOSCALE on QPS / p99; beware COLD STARTS -> warm minimum pool

TRADE-OFF TRIANGLE:  LOW LATENCY | HIGH THROUGHPUT | LOW COST  -> pick 2
  batching  = +throughput -cost  BUT +latency

1k -> 100k QPS (100x):  replicate(~100+) + cache hot + batch + shard store
                        + autoscale   ---  NOT a bigger model
  replicas ~= target QPS / QPS-per-replica (minus cache hits, plus headroom)
```

---

> **Next module:** *Module 12 — Feedback Loops, Continual Learning & the Data
> Flywheel.* Now that the system scales, we return to the loop from Module 1:
> how a live system's own predictions reshape its future data, how to retrain
> continuously without breaking things, and how to keep a virtuous flywheel from
> turning into a harmful bias-amplifying loop.
