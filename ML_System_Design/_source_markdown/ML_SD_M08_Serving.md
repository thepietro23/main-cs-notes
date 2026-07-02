---
title: "Module 8 — Model Serving & Inference"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8 — Model Serving & Inference

> **Why this module matters.**
> You have framed the problem (M2), built the data and features (M4, M5),
> trained a model (M6), and proved it is good offline (M7). None of that
> reaches a user until the model is *served* — wrapped behind an interface,
> given hardware, and made to answer within a strict time and cost budget.
> Serving is where ML meets real backend engineering: latency, throughput,
> queues, caches, GPUs, rollouts. It is also where most candidates get thin,
> because it is the least glamorous and most systems-heavy part of the loop.
> A model that is 2% more accurate but blows the p99 latency budget will lose
> to a simpler model that answers on time — *latency is a feature*. This module
> makes you fluent in the vocabulary and trade-offs that a Staff-level backend
> or ML engineer is expected to reason about on the spot.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
explain batch vs online vs streaming inference and pick one for a given
problem; name the four serving patterns (embedded, model-as-a-service,
microservice, sidecar) and their trade-offs; explain the *tail-latency*
problem and why p99 (not p50) drives design once you fan out; sketch a
latency budget that adds up to a target; list the main model servers (TF
Serving, TorchServe, Triton, BentoML, KServe, Ray Serve) and when each fits;
describe quantization, pruning, distillation, ONNX, and TensorRT with rough
size/latency/accuracy numbers; choose CPU vs GPU vs TPU vs edge; explain
request batching as a throughput-vs-latency knob; and design a safe rollout
using shadow, canary, and A/B routing.

> **How to read this module.** As always we go **problem → simplest attempt →
> why it breaks → the fix**, and we tie every idea to how it shows up in a real
> Google / Meta / Amazon / Stripe interview and in a real backend on-call
> shift.

---

## 8.1 Batch vs Online vs Streaming Inference

### Motivation (the problem that existed)

Once the model is trained, the very first design fork is: *when and how does a
prediction get produced?* This one choice cascades into your latency budget,
your cost, your freshness, and the entire shape of your serving stack. We first
met these modes in **Module 1** (types of ML systems); here we look at them
purely through the *serving* lens.

![Three ways to serve predictions: batch (offline, seconds-hours OK), online (real-time, ms budget), streaming (event-driven, sub-second).](images/m08_01_batch_online_streaming.png)

### The three modes

- **Batch (offline) inference.** You run the model over *all* the entities you
  care about on a schedule (say nightly), and write the results to a table or
  key-value store. At request time you just *look up* the precomputed answer —
  there is no model call in the hot path at all. Cheapest per prediction,
  trivially scalable, but the answer is as stale as your last run.
- **Online (real-time) inference.** You compute a prediction *per request*,
  live, inside a tight millisecond budget. This is what powers search ranking,
  ad click-through, and feed ranking. Fresh, but you now own a low-latency,
  high-availability service.
- **Streaming inference.** You react to events as they arrive on a bus (Kafka,
  Kinesis, Pulsar) and process them with a stream engine (Flink, Spark
  Streaming). Predictions update continuously as new events land — ideal for
  fraud alerts and live personalization where "the last few seconds" matter.

### First-principles: how to choose

Ask the same three questions from Module 1:

1. **How fresh must the answer be?** If yesterday's answer is fine → batch.
   If it must reflect what the user did *this request* → online. If it must
   react to a just-arrived *event* stream → streaming.
2. **What is the latency budget?** Batch has effectively none (a background
   job). Online is typically 10–200 ms end-to-end. Streaming is sub-second per
   event but is usually not blocking a user.
3. **What does it cost at scale?** Batch amortizes one big efficient run;
   online pays per request and must be provisioned for peak QPS.

> **Common real-world pattern — hybrid.** Big systems mix modes: YouTube
> *precomputes* candidate videos in batch, then *re-ranks* them online per
> request. Proposing a batch-heavy-lifting + online-final-decision hybrid when
> the interviewer pushes on latency and cost is a strong senior move.

---

## 8.2 Serving Patterns: Embedded, Service, Microservice, Sidecar

### Motivation

Given you need *online* inference, the next question is *where the model
physically lives* relative to the application calling it. This is an
architecture choice with real consequences for latency, scaling, and blast
radius.

![Four serving patterns: embedded (app plus model in one process), model-as-a-service (app calls a model server), microservice (independently scaled model service), sidecar (model co-located in the same pod or host).](images/m08_02_serving_patterns.png)

### The four patterns

- **Embedded.** The model is loaded *inside* the application process (e.g. a
  Python or Java library call). No network hop, so it is the **lowest latency**
  and simplest to reason about. But the model and app are coupled: they scale
  together, deploy together, and share memory. A 4 GB model now bloats every
  app replica. Great for small models and on-device.
- **Model-as-a-service.** The model runs in its own server process (often a
  dedicated model server like TF Serving or Triton) and the app calls it over
  the network (REST/gRPC). You pay a network hop but gain independence: update
  the model without redeploying the app.
- **Microservice.** A stronger version of the above — the model is a
  first-class service with its own repo, deploy cadence, autoscaling, and
  on-call. Best when many apps share one model, or when the model needs
  different hardware (GPUs) than the app.
- **Sidecar.** The model runs in a *separate container co-located with the app*
  (same pod / same host). You get process isolation *and* a near-local network
  hop (loopback), avoiding cross-host latency. Common in service-mesh setups.

### Trade-off summary

| Pattern | Latency | Coupling | Scale model separately? | Best for |
|---------|---------|----------|:-----------------------:|----------|
| Embedded | Lowest (no hop) | Tight | No | Small models, on-device |
| Model-as-a-service | +1 network hop | Loose | Yes | Shared model, GPU model |
| Microservice | +1 hop, own infra | Loosest | Yes (independently) | Many callers, own on-call |
| Sidecar | Near-local hop | Medium | Partly | Service mesh, isolation |

> **Senior signal:** knowing that "embedded is fastest but couples deploy and
> scaling" and that "a GPU model almost always wants to be its own service so
> you don't buy a GPU per app replica" shows you connect the ML choice to the
> infra bill.

---

## 8.3 Latency Budgets and the Tail-Latency Problem

### Motivation

Users and business metrics do not care about your *average* latency; they feel
the *slow* requests. And the moment your request depends on several downstream
calls, the slow ones start to dominate. This is the single most important
systems idea in serving, and it trips up almost every junior candidate.

### Percentiles: p50, p95, p99

- **p50 (median):** half of requests are faster than this. Comfortable but
  misleading — it hides the pain.
- **p95 / p99 (the tail):** 95% / 99% of requests are faster than this. The
  1-in-100 slow request is what users complain about and what breaks your SLA.
- You set SLOs on the tail, e.g. **"p99 < 100 ms"**, *not* on the mean, because
  the mean can look fine while 1% of users have a terrible experience.

### Why the tail explodes under fan-out

Here is the key derivation. Suppose one service call is "fast" (under budget)
99% of the time. If your request **fans out** to *N* independent services and
must wait for **all** of them (the slowest wins), then:

> P(the whole request is fast) = 0.99^N

- N = 1 → 99% fast.
- N = 10 → 0.99^10 ≈ 90% fast (so ~10% are slow!).
- N = 100 → 0.99^100 ≈ 37% fast, meaning **~63% of requests hit at least one
  tail call.** Your "p99-fast" components produce a *median-slow* system.

![Tail latency under fan-out: a request calls five services and the slowest one determines the total; with many fan-out calls the probability that all are fast collapses, so the tail dominates.](images/m08_03_tail_latency.png)

**This is why the tail matters:** at fan-out scale, your typical user
experiences your p99, not your p50. Techniques to fight it:

- **Hedged / backup requests:** if a call is slow past p95, fire a second copy
  and take whichever returns first (Google's classic trick).
- **Request timeouts + fallbacks:** cap each call and serve a cached/default
  answer rather than waiting forever.
- **Reduce fan-out:** batch downstream calls, cache aggressively, or
  precompute.

### A worked latency budget (must-have interview skill)

Give yourself a target of **p99 < 100 ms end-to-end** and *account for every
millisecond*:

![A worked 100 ms latency budget broken into network in/auth (10 ms), feature fetch (25 ms), preprocess (10 ms), model inference (35 ms), post-process and rank (12 ms), and network out (8 ms).](images/m08_08_latency_budget.png)

| Stage | Budget | Note |
|-------|-------:|------|
| Network in + auth | 10 ms | TLS, gateway, load balancer |
| Feature fetch (feature store) | 25 ms | often the biggest surprise |
| Preprocess | 10 ms | tokenize / normalize |
| **Model inference** | 35 ms | the actual forward pass |
| Post-process + rank | 12 ms | sort candidates, business rules |
| Network out | 8 ms | serialize + return |
| **Total** | **100 ms** | must fit the **p99**, not p50 |

> **The lesson candidates miss:** the model forward pass is often *not* the
> bottleneck — feature fetching and network frequently cost more. Optimizing
> the model from 35 ms to 25 ms is pointless if feature lookup is 25 ms and
> flaky. Always budget the *whole* path.

---

## 8.4 Model Servers (TF Serving, TorchServe, Triton, BentoML, KServe, Ray Serve)

### Motivation

You *could* hand-write a Flask app that loads a model and returns predictions.
It will work in a demo and fall over in production: no batching, no GPU
scheduling, no versioning, no metrics, no warm-up. **Model servers** are
purpose-built to solve exactly these production concerns so you don't
reinvent them.

### What a model server gives you

Regardless of vendor, a good model server provides: model **versioning** and
hot-swapping, **dynamic request batching** (8.7), **multi-model** hosting,
GPU scheduling, health checks and warm-up, standard REST/gRPC endpoints, and
metrics/tracing hooks.

### Comparison

| Server | Origin / ecosystem | Best at | Notes |
|--------|--------------------|---------|-------|
| **TensorFlow Serving** | Google / TF | Serving TF SavedModels | Mature, fast, TF-centric |
| **TorchServe** | Meta / PyTorch | Serving PyTorch models | Handlers in Python, PyTorch-native |
| **Triton Inference Server** | NVIDIA | Multi-framework on GPU | TF/PyTorch/ONNX/TensorRT; best GPU batching; multi-model |
| **BentoML** | OSS framework | Packaging + serving any Python model | "Bento" bundle, easy to build APIs, framework-agnostic |
| **KServe** | Kubernetes (KFServing) | Serverless serving on K8s | Autoscaling (incl. scale-to-zero), canary built in |
| **Ray Serve** | Anyscale / Ray | Python-native, composing models | Great for pipelines and LLMs; scales with Ray |

**Rules of thumb:**

- All-TensorFlow shop, CPU/GPU → **TF Serving**.
- All-PyTorch → **TorchServe**.
- Mixed frameworks and you want top GPU throughput / multi-model on one box →
  **Triton**.
- Want to package arbitrary Python logic into a clean API fast → **BentoML**.
- You live on Kubernetes and want autoscaling + canaries declaratively →
  **KServe** (often *on top of* Triton/TorchServe).
- You are composing several models / heavy Python glue (RAG, LLM pipelines) →
  **Ray Serve**.

> **Interview line:** "I'd serve the model with Triton for dynamic batching on
> GPU, wrap it in KServe for autoscaling and canary rollout on our K8s
> cluster." That one sentence signals you know the layers stack.

---

## 8.5 Model Optimization: Quantization, Pruning, Distillation, ONNX, TensorRT

### Motivation

Your trained model may be too big or too slow for the latency budget and
hardware you have. Optimization shrinks and speeds it up in exchange for a
(usually small) accuracy cost. This is how a model that needs a big GPU becomes
one that runs on a CPU or a phone.

![Model optimization: a big FP32 model is shrunk via quantization (FP32 to INT8), pruning (drop weights), and distillation (big teacher to small student), then compiled with ONNX/TensorRT into a small fast model.](images/m08_04_optimization.png)

### The techniques

- **Quantization.** Store and compute weights in lower precision — FP32 → FP16
  or INT8. Roughly **4× smaller** (FP32→INT8) and **2–4× faster**, typically
  with **~1% accuracy drop**. The single highest-return optimization for most
  models. *Post-training* quantization is easy; *quantization-aware training*
  recovers more accuracy.
- **Pruning.** Remove weights (or whole channels) that contribute little,
  producing a sparser model. Can cut size meaningfully; speedups need hardware
  that exploits sparsity. Accuracy holds if you prune gradually and fine-tune.
- **Distillation.** Train a small "student" model to mimic a big "teacher"
  model's outputs. You get a much smaller model that keeps most of the quality
  (e.g. DistilBERT ≈ 40% smaller, ~60% faster, ~97% of BERT's quality). Trades
  size for a little accuracy.
- **ONNX (Open Neural Network Exchange).** A common model *format*. Export from
  PyTorch/TF to ONNX so you can run anywhere with ONNX Runtime, decoupling
  training framework from serving runtime.
- **TensorRT.** NVIDIA's compiler/runtime that **fuses layers, picks fast
  kernels, and applies precision calibration** for a specific GPU — often
  another **2–5× speedup** on top of quantization.

### The trade-off table (rough, memorize the shape)

| Technique | Size | Latency | Accuracy | Effort |
|-----------|:----:|:-------:|:--------:|:------:|
| FP16 quantization | ~2× smaller | ~1.5–2× faster | ~0% loss | Low |
| INT8 quantization | ~4× smaller | ~2–4× faster | ~1% loss | Low–Med |
| Pruning | smaller | needs HW support | small loss | Medium |
| Distillation | much smaller | faster | few % loss | High (retrain) |
| ONNX export | same | portable / a bit faster | ~0% | Low |
| TensorRT compile | same | 2–5× faster (GPU) | ~0–1% | Medium |

> **Senior signal:** stacking them — "distill to a small student, quantize to
> INT8, compile with TensorRT" — is how teams fit a big model into a tight
> CPU/GPU budget. Always name the *accuracy check* you'd run after each step.

---

## 8.6 Hardware: CPU vs GPU vs TPU vs Accelerators

### Motivation

The same model can be cheap or ruinously expensive depending on the hardware,
and the right choice depends on model size, batch size, and QPS — not on hype.

![Hardware comparison: CPU (cheap, flexible, low parallelism), GPU (massively parallel, great for deep nets and batching, costly), TPU (Google ASIC for tensor ops at scale), Edge NPU (on-device, low power).](images/m08_06_hardware.png)

### When each is right

- **CPU.** Cheap, everywhere, flexible. Great for small models (linear models,
  small trees, tiny nets), low QPS, or latency-simple workloads where a GPU's
  batching advantage never kicks in. Often the *default* — don't buy a GPU you
  don't need.
- **GPU.** Thousands of cores → massive parallelism. Wins for deep neural nets,
  large matrix multiplies, and when you can **batch** requests to keep it busy.
  Costly and wasted if it sits idle at low QPS.
- **TPU.** Google's custom ASIC built for tensor ops; excels at very large
  training and high-scale serving inside Google Cloud. Less flexible than GPUs,
  best when your workload matches its sweet spot.
- **Custom accelerators / Edge NPUs.** AWS Inferentia, Apple Neural Engine,
  Qualcomm NPUs, etc. — chips tuned for inference, often on-device for low
  power and privacy (phone keyboard, face unlock). Pair with a quantized model
  from 8.5.

> **Cost intuition:** a GPU only pays off if you can keep it *fed*. At 5 QPS a
> GPU is mostly idle and a CPU fleet is cheaper; at 5000 QPS with batching, a
> GPU is far cheaper per prediction. The break-even is a throughput question.

---

## 8.7 Caching, Precomputation & Request Batching

### Motivation

The fastest inference is the one you never run. Before optimizing the model,
ask whether you can **avoid** or **amortize** the work.

### Caching and precomputation

- **Cache predictions.** If the same input recurs (popular query, popular
  item), cache the model output keyed by input. A cache hit skips the model
  entirely. Watch staleness — invalidate when the model or inputs change.
- **Cache / precompute features.** Feature fetching is often the latency
  hog (8.3). Precompute expensive features offline into the feature store so
  serving just reads them (cross-link **Module 5**).
- **Precompute predictions (batch).** The extreme case is 8.1's batch mode:
  compute everything ahead of time and serve by lookup.

### Request batching (the throughput vs latency knob)

GPUs are most efficient when they process a *batch* of inputs at once, not one
at a time. **Dynamic batching** holds incoming requests for a tiny window
(e.g. 5 ms) or until a max batch size, then runs them together.

![Request batching: incoming requests wait briefly in a batch queue, then the GPU runs one big batch efficiently; bigger batches raise throughput but also raise per-request latency.](images/m08_05_request_batching.png)

- **Bigger batch → higher throughput** (better hardware utilization, more
  predictions/second).
- **Bigger batch → higher per-request latency** (each request waits for the
  batch to fill).
- You tune two knobs: **max batch size** and **max wait time**. Under high
  load, batches fill instantly (great throughput, tiny added wait); under low
  load, you wait up to the timeout (so keep the timeout small).

> **Interview trap:** "just increase the batch size" is *not* free — it trades
> the latency you were trying to protect. State the max-wait cap explicitly.

---

## 8.8 Multi-Model Serving, A/B Routing, Shadow & Canary Deployments

### Motivation

Deploying a new model straight to 100% of traffic is how you cause an incident.
Real teams roll out *gradually* and *measure*, and often serve *many* models at
once (per-region, per-segment, or several versions).

### Multi-model serving

One server (e.g. Triton, Ray Serve) can host many models or many versions and
route between them. This lets you share expensive hardware, run per-segment
models, and keep the previous version warm for instant rollback.

### The safe-rollout ladder

![Safe rollouts: live traffic hits a router that sends most requests to Model A (old), a small canary share to Model B (new), and a shadow copy to Model C whose results are dropped.](images/m08_07_rollouts.png)

- **Shadow (dark launch).** Send a *copy* of live traffic to the new model but
  **throw its answers away** — users still see the old model. You compare the
  new model's predictions and latency against production *with zero user
  risk*. Best first step for a risky change.
- **Canary.** Route a **small percentage** (e.g. 1–10%) of *real* traffic to
  the new model and watch business + system metrics. If healthy, ramp up; if
  not, roll back — only a few users were affected.
- **A/B test.** Split traffic between versions and measure the *business
  metric* (not just offline accuracy) with statistical rigor to decide the
  winner (cross-link **Module 7** on online evaluation).
- **Blue-green.** Keep two full environments; flip all traffic at once and flip
  back instantly if it breaks. Fast rollback, higher cost.

> **Senior signal:** "shadow first to check parity, canary at 5% with automated
> rollback on a metric regression, then A/B to prove the business lift" is the
> answer that says you have shipped models to production, not just trained them.

---

## Module 8 — Interview Mapping (what companies probe)

| Company | How Module 8 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "Design low-latency serving for ranking" | "Put the model behind an API" | Budgets p99, fights tail with batching + hedged requests, hybrid batch+online |
| **Amazon** | Cost of serving at scale (Inferentia) | Ignores cost | Ties hardware choice to QPS/batch break-even and the customer latency SLA |
| **NVIDIA / infra** | Triton, TensorRT, GPU batching | "Use a GPU" | Explains dynamic batching, INT8/TensorRT, keeping the GPU fed |
| **Stripe / Uber** | Fraud/ETA serving, safe rollout | "Deploy the new model" | Shadow → canary → A/B with automated rollback and kill switch |

**The single most common opening:** *"How would you serve this model with p99 <
X ms?"* Your first 60 seconds should: (1) pick batch/online/streaming, (2) write
a latency budget that sums to X, (3) name the tail-latency risk and one
mitigation. That structure alone separates you.

---

## Module 8 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** serving/inference is essentially **interview- and
  job-only**; written exams rarely test it. At most, a definitional
  "batch vs real-time processing" question, which Section 8.1 covers.
- **GATE CS / DA:** may touch on latency percentiles and basic throughput vs
  latency trade-offs as general systems concepts; the ML-specific serving stack
  is not tested.
- **ISRO / DRDO:** occasional generic questions on inference vs training.

> **Flag:** this module carries very high **interview and on-the-job** value and
> low written-exam value. Invest here for FAANG / AI-engineer roles, skim for
> written exams.

---

## Module 8 — Common Mistakes & Misconceptions

1. **"Optimize the model first."** Often feature fetch and network dominate the
   budget (8.3). Profile the *whole* path before touching the model.
2. **"Average latency looks fine."** Users feel the **tail (p99)**, and fan-out
   makes the tail the common case. Design to the tail. (8.3.)
3. **"Bigger batch is free throughput."** It raises per-request latency; cap the
   max wait time. (8.7.)
4. **"Just put it behind Flask."** No batching, versioning, or GPU scheduling —
   use a real model server. (8.4.)
5. **"Quantization destroys accuracy."** INT8 is usually ~1% loss for ~4×
   smaller / 2–4× faster. Measure, don't assume. (8.5.)
6. **"Buy a GPU for everything."** A GPU idle at low QPS is more expensive than
   a CPU fleet; the break-even is a throughput question. (8.6.)
7. **"Deploy the new model to 100%."** Use shadow → canary → A/B with rollback.
   (8.8.)

---

## Module 8 — MCQs (with answers & explanations)

**Q1.** A request fans out to 100 downstream calls, each "fast" 99% of the time,
and must wait for all. Roughly what fraction of requests are fully fast?
a) 99%  b) 90%  c) 63%  d) 37%

<details><summary>Answer</summary>**d.** 0.99^100 ≈ 0.37, so only ~37% are fully
fast and ~63% hit at least one tail call. This is why p99 of components becomes
the *typical* experience under fan-out.</details>

**Q2.** You need the lowest possible inference latency with no network hop and
the model is small. Which serving pattern?
a) Microservice  b) Embedded  c) Sidecar  d) Model-as-a-service

<details><summary>Answer</summary>**b.** Embedded runs the model in the app
process — no network hop, lowest latency — at the cost of coupling deploy and
scaling. Fine for small models.</details>

**Q3.** Which optimization typically gives ~4× size reduction and 2–4× speedup
for about 1% accuracy loss?
a) Pruning  b) INT8 quantization  c) ONNX export  d) Distillation

<details><summary>Answer</summary>**b.** INT8 quantization is the highest-return
optimization for most models. ONNX export mainly aids portability; distillation
needs retraining.</details>

**Q4.** Increasing the dynamic batch size on a GPU server will most directly:
a) lower per-request latency  b) raise throughput but raise per-request latency
c) reduce accuracy  d) remove the need for caching

<details><summary>Answer</summary>**b.** Batching improves hardware utilization
(throughput) but each request waits for the batch to fill, raising latency.
Tune with a max-wait cap.</details>

**Q5.** You want to test a new model against production traffic with **zero user
risk** before exposing any users. Which technique?
a) Canary  b) A/B test  c) Shadow deployment  d) Blue-green flip

<details><summary>Answer</summary>**c.** Shadow (dark launch) sends a copy of
live traffic to the new model and discards its outputs, so you compare parity
and latency without affecting users.</details>

**Q6.** Which model server is the strongest choice for **multi-framework,
high-throughput GPU serving with dynamic batching** on one box?
a) TF Serving  b) TorchServe  c) Triton  d) Flask

<details><summary>Answer</summary>**c.** NVIDIA Triton serves TF/PyTorch/ONNX/
TensorRT models, does excellent dynamic batching, and hosts multiple models on
one GPU box.</details>

**Q7.** In a 100 ms p99 budget, feature fetch is 25 ms, inference 35 ms,
network 18 ms, pre/post 22 ms. Shaving inference from 35 → 25 ms while feature
fetch is flaky at 25 ms is:
a) the top priority  b) often the wrong optimization to start with
c) impossible  d) guaranteed to hit the SLA

<details><summary>Answer</summary>**b.** The model isn't the only cost; a flaky
25 ms feature fetch may dominate the tail. Budget and profile the whole path
first.</details>

---

## Module 8 — Design Exercises (easy → hard)

- **Easy.** For each, pick batch / online / streaming and justify: (1) nightly
  "recommended for you" email; (2) search ranking; (3) card-fraud alerting;
  (4) monthly churn scores. *(Batch, online, streaming, batch.)*
- **Medium.** Write a latency budget that sums to a **p99 < 80 ms** target for
  an online ranking service. Name each stage and its ms.
- **Medium.** You serve a PyTorch model at 3000 QPS on GPUs but utilization is
  low and latency is high. Which two knobs do you reach for, and what's the
  trade-off? *(Dynamic batching + right-size instances; batch raises latency.)*
- **Hard.** A model is 1.2 GB and misses the latency budget on CPU. Propose a
  concrete optimization plan (which techniques, in what order) and the accuracy
  checks after each step.
- **Hard.** Design the rollout of a new ranking model that could hurt revenue.
  Sequence shadow, canary, and A/B; specify the metric and the automated
  rollback trigger. What is your kill switch?

---

## Module 8 — Concept Review (one page)

- **Modes:** **batch** (precompute, lookup, stale, cheap) · **online**
  (per-request, fresh, ms budget) · **streaming** (event-driven). Big systems go
  **hybrid** (precompute candidates + online re-rank).
- **Patterns:** **embedded** (no hop, coupled) · **model-as-a-service** · 
  **microservice** (own infra/scaling) · **sidecar** (co-located, isolated).
- **Latency:** design to the **tail (p99)**, not p50; under fan-out to N,
  P(all fast) = p^N, so the tail becomes typical. Fight it with hedged
  requests, timeouts + fallbacks, and less fan-out. **Budget the whole path.**
- **Servers:** TF Serving (TF), TorchServe (PyTorch), **Triton** (multi-fw GPU),
  BentoML (packaging), **KServe** (K8s autoscale + canary), Ray Serve (Python
  pipelines).
- **Optimize:** **quantization** (INT8 ≈ 4× smaller, 2–4× faster, ~1% loss),
  **pruning**, **distillation** (small student), **ONNX** (portable),
  **TensorRT** (GPU compile, 2–5×). Stack them; check accuracy each step.
- **Hardware:** CPU (small/low-QPS default) · GPU (batchable deep nets) · TPU
  (Google-scale) · edge NPU (on-device). GPU pays off only when kept fed.
- **Batching:** throughput ↑ but per-request latency ↑; cap max batch + max
  wait. **Cache** predictions/features and **precompute** where possible.
- **Rollouts:** **shadow** (no user risk) → **canary** (small %) → **A/B**
  (measure business metric) with automated rollback; blue-green for instant flip.

---

## Module 8 — Flash Cards (Q → A)

1. Batch vs online in one line? → *Batch = precompute all + lookup (stale,
   cheap); online = per-request, fresh, ms budget.*
2. Why does p99, not p50, drive design? → *Users feel the tail; under fan-out
   P(all fast)=p^N so the tail becomes typical.*
3. Lowest-latency serving pattern? → *Embedded (no network hop), but couples
   deploy + scaling.*
4. INT8 quantization rough numbers? → *~4× smaller, 2–4× faster, ~1% accuracy
   loss.*
5. Distillation in one line? → *Train a small student to mimic a big teacher;
   much smaller, keeps most quality.*
6. Best server for multi-framework GPU batching? → *NVIDIA Triton.*
7. Batching trade-off? → *Higher throughput but higher per-request latency; cap
   max wait.*
8. Safe-rollout order? → *Shadow → canary → A/B, with automated rollback.*

---

## Module 8 — Pattern Recognition (how to spot it in an interview)

- Hear **"p99 < X ms"** → write a latency budget and name the tail risk.
- Hear **"fans out to many services"** → say *tail latency*, propose hedged
  requests / timeouts / less fan-out.
- Hear **"the GPU is underutilized"** → say *dynamic batching*, keep it fed.
- Hear **"model is too big / too slow"** → quantize → distill → TensorRT, check
  accuracy each step.
- Hear **"roll out a risky new model"** → shadow → canary → A/B with rollback.
- Hear **"cheapest way to serve at low QPS"** → CPU + caching/precompute, not a
  GPU.
- Hear **"same query keeps repeating"** → cache predictions; precompute
  features.

---

## Module 8 — Revision Notes / Mini Cheat Sheet

```
SERVE MODES:  batch (precompute+lookup, stale, cheap) | online (per-req, fresh, ms)
              streaming (events, sub-sec)              -> big systems go HYBRID

PATTERNS:  embedded (no hop, coupled) | model-as-a-service | microservice (own infra)
           sidecar (co-located, isolated)

LATENCY:   design to p99 (tail), NOT p50
           fan-out N: P(all fast)=p^N  -> tail becomes typical (0.99^100 ~= 37%)
           fight: hedged requests | timeouts+fallback | less fan-out | BUDGET whole path
           budget e.g. 100ms = net10 + feat25 + pre10 + INFER35 + post12 + net8

SERVERS:   TFServing(TF) | TorchServe(PyTorch) | TRITON(multi-fw GPU batch)
           BentoML(package) | KServe(K8s autoscale+canary) | RayServe(py pipelines)

OPTIMIZE:  quantize INT8 ~4x smaller,2-4x faster,~1% loss | prune | distill(student)
           ONNX(portable) | TensorRT(GPU 2-5x)   -> stack + check accuracy each step

HARDWARE:  CPU(small/low-QPS default) | GPU(batchable deep nets) | TPU(scale) | NPU(edge)
           GPU pays off ONLY if kept fed (throughput break-even)

CACHE/BATCH: cache preds+features, precompute | dynamic batch: throughput^ latency^
             tune max-batch-size + max-wait (e.g. 5ms)

ROLLOUT:   SHADOW (no user risk) -> CANARY (small %) -> A/B (business metric) + rollback
```

---

> **Next module:** *Module 9 — Scaling & Distributed Training.* Serving answers
> "how do we run the model fast for users"; next we go upstream to "how do we
> *train* models too big or datasets too large for one machine" — data vs model
> parallelism, parameter servers vs all-reduce, and the systems that make it
> practical.
