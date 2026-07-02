---
title: "Module 9 — ML Infrastructure & MLOps"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 9 — ML Infrastructure & MLOps

> **Why this module exists.**
> By now you can frame a problem, build features, train a model, and serve it.
> But a model that lives in a notebook on one laptop is not a *system*. The
> moment a second person, a second model version, or a second week of traffic
> shows up, you need **infrastructure**: a way to track what you ran, store which
> model is live, rebuild any result on demand, retrain automatically when the
> world drifts, and run all of it cheaply on shared hardware. That discipline —
> the plumbing that turns "a model" into "a reliable, repeatable ML product" — is
> called **MLOps** (Machine Learning + DevOps). This module is the plumbing.
> Skip it and you get the classic failure: a great offline model that nobody can
> reproduce, nobody can roll back, and nobody notices when it silently rots.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★      | ★★★★★       |

**What you must be able to do after this module:**
place any team on the **MLOps maturity ladder** (manual → automated → CI/CD/CT)
and say what the next rung costs; explain **experiment tracking** and why it
exists; describe a **model registry** and its stage lifecycle; define
**CI, CD, and CT** for ML and why CT is the ML-only piece; state the three things
you must pin for **reproducibility**; name the main **orchestrators** and what a
pipeline DAG is; explain why ML teams use **containers + Kubernetes**; reason
about **GPU cost and scheduling**; and compare the big **platform case studies**
(Uber Michelangelo, Netflix Metaflow, Meta FBLearner, Google TFX). Finally, you
must be able to draw the **end-to-end MLOps architecture** tying training →
registry → CI/CD → serving → monitoring into one loop.

> **How to read this module.** Same as always: **problem → simplest attempt →
> why it breaks → the fix.** MLOps is easiest to learn as a series of pains that
> each tool removes. We name the pain first, then the tool.

---

## 9.1 The MLOps Maturity Ladder

### Motivation (the problem that existed)

A data scientist trains a model in a notebook, downloads the weights, and emails
them to an engineer who copies them onto a server by hand. It works — once. Then
the data changes and nobody remembers which notebook cell produced the live
model, which data it used, or how to make a new one. This is **Level 0: manual**.
It is where almost every team starts, and it does not scale past one model and
one person.

MLOps is the answer to "how do we make this repeatable, safe, and fast?" The
journey is best understood as a **maturity ladder** — you climb one rung at a
time, and each rung removes a specific kind of manual toil.

![A three-step staircase: Level 0 Manual (notebooks and hand deploys), Level 1 Automated Training (reusable pipeline, auto retrain, registry), Level 2 CI/CD/CT (tests, auto deploy, continuous training, full monitoring).](images/m09_01_maturity_ladder.png)

### The three rungs (Google's model, simplified)

- **Level 0 — Manual.** Every step is done by hand: notebooks, manual data prep,
  manual deploy. No automated tests, no monitoring. Releases are rare and scary.
  Fine for a proof of concept; dangerous in production.
- **Level 1 — ML pipeline automation.** The *training* process is packaged as a
  reusable **pipeline** that anyone can run. Models land in a **registry**.
  Retraining can be triggered on a schedule or on new data. You can now produce a
  fresh model without a human babysitting a notebook.
- **Level 2 — CI/CD/CT automation.** The *pipeline itself* is tested and shipped
  automatically. Code commits trigger **CI** (tests) and **CD** (deploy), and
  new data triggers **CT** (continuous training). Monitoring closes the loop.
  This is a self-updating ML system.

### First-principles: why climb at all?

Each rung trades **engineering investment now** for **less toil and risk later**.
The question is never "are we mature enough?" but "does the pain of the current
rung justify building the next one?" A single low-stakes batch model may live
happily at Level 0 forever. A fraud model serving millions of requests needs
Level 2. Matching maturity to stakes is a senior judgment call, not a badge to
collect.

> **Senior signal:** naming the maturity level of a proposed design — and
> refusing to over-build a Level 2 platform for a one-off model — shows you
> understand cost, not just tooling.

---

## 9.2 Experiment Tracking

### Motivation

You train 40 versions of a model this week — different learning rates, different
features, different data windows. On Friday your boss asks "which run gave the
0.91 AUC, and can you reproduce it?" If your answer is "it's in one of these
notebooks somewhere", you have the problem that **experiment tracking** solves.

An experiment tracker is a service that **records every training run**: its
inputs, its outputs, and enough context to compare and reproduce it.

![Experiment tracking: a training run logs to a tracking server (MLflow / W&B), which records params, metrics, artifacts, and code plus data version.](images/m09_02_experiment_tracking.png)

### What gets logged (and why)

- **Parameters** — the knobs you chose (learning rate, tree depth, batch size).
  So you can tell *why* run A beat run B.
- **Metrics** — the results (accuracy, loss, AUC), often across training steps.
  So you can rank runs and plot learning curves.
- **Artifacts** — the actual outputs (the model file, plots, a confusion matrix).
  So the winning model is downloadable, not lost.
- **Code + data version** — the git commit and the dataset hash/version. So the
  run can be *reproduced*, not just admired.

### The tools

- **MLflow** — open source, self-hostable; the de-facto standard. Four parts:
  Tracking, Projects, Models, and a Model Registry (Section 9.3).
- **Weights & Biases (W&B)** — hosted, polished dashboards and live charts;
  popular for deep learning research and team collaboration.
- Cloud-native equivalents: Vertex AI Experiments, SageMaker Experiments,
  Comet, Neptune.

> **First-principles takeaway:** a tracker turns "I think this worked" into "run
> #4127, commit `a3f9`, dataset v12, AUC 0.91, here is the model file." That is
> the difference between a hobby and an engineering practice.

---

## 9.3 Model Registry & Versioning

### Motivation

Your tracker holds thousands of trained models. Which one is **live in
production** right now? Which one is being tested? If today's model misbehaves,
which exact version do you roll back to? A pile of files named
`model_final_v2_REALLY_final.pkl` cannot answer these questions. A **model
registry** can.

A model registry is a **central, versioned catalogue of models** with a
lifecycle stage attached to each version.

![Model registry: a trained model v3 is registered, then promoted through stages Staging (test) to Production (serving) to Archived (rollback), with a dashed rollback arrow from Archived back to Production.](images/m09_03_model_registry.png)

### The stage lifecycle

1. **Register** — a trained model becomes an immutable, numbered version
   (`fraud-model v3`).
2. **Staging** — the version is deployed to a test/shadow environment and
   validated against real-ish traffic.
3. **Production** — promoted to serve live requests. There is exactly one (or a
   controlled few) production version at a time.
4. **Archived** — retired versions are kept, not deleted, so you can **roll
   back** in seconds if a new version regresses.

### What a version pins (lineage)

A good registry entry links to: the training run (tracker), the code commit, the
dataset version, the metrics, and who approved the promotion. This **lineage**
answers audits ("why did the model deny this loan in March?") and enables
one-click rollback — the single most valuable safety feature in production ML.

> **Interview note:** whenever you say "we'll deploy the model", follow it with
> "…via the registry, so we can shadow, promote, and roll back". That one clause
> signals production maturity.

---

## 9.4 CI / CD / CT Pipelines for ML

### Motivation

Traditional software has **CI** (Continuous Integration: test and build on every
commit) and **CD** (Continuous Delivery/Deployment: ship automatically). ML
needs both — *plus a third loop that no ordinary software has*, because an ML
system decays when the data drifts (Module 1). That third loop is **CT:
Continuous Training**.

![CI/CD/CT for ML: a horizontal flow Code commit to CI (test+build) to CD (deploy) to Serve in prod; a red dashed CT loop where new data triggers retrain, feeding from serving back into CI.](images/m09_04_cicd_ct.png)

### The three loops

- **CI (Continuous Integration).** On every code commit, run tests and build
  artifacts. For ML this means *more than* unit tests: **data validation tests**
  (schema, ranges, nulls), **feature tests**, and even a small **model
  sanity/quality test** (does it beat a baseline on a fixed set?).
- **CD (Continuous Delivery).** Automatically package and deploy the pipeline
  and/or the model — into staging, then production, ideally with a canary or
  shadow rollout and an automatic rollback trigger.
- **CT (Continuous Training).** The ML-only loop. When **new data arrives** or
  **monitoring detects drift** or **a schedule fires**, automatically retrain,
  evaluate, and (if better) promote a new model version. This is what keeps the
  system from rotting.

### Why CT is the hard, ML-specific part

CD ships *code*. CT ships a *new model produced from new data* — which means the
"build" is non-deterministic, the "tests" are statistical (is the new model
actually better, and not just different?), and the trigger is often *data*, not a
human pressing merge. Getting CT right requires the registry (9.3), the tracker
(9.2), and reproducibility (9.5) all working together.

> **Common mistake:** treating CT as "just retrain nightly". Blind retraining can
> *ship a worse model* if the new data is bad. Always gate promotion on an
> evaluation that compares the candidate to the current production model.

---

## 9.5 Reproducibility — Pin Data + Code + Environment

### Motivation

Six months from now, a regulator (or your future self) asks: "re-create the exact
model that was live in January." You rerun the code and get a *different* model —
because the data has changed, a library upgraded, or a random seed differed.
Reproducibility is the property that **the same inputs always produce the same
model**. It is the foundation everything else rests on.

![Reproducibility Venn: three overlapping circles — CODE (git SHA), DATA (version/hash), ENV (container + seed) — must all be pinned to get the SAME MODEL.](images/m09_05_reproducibility.png)

### The three things you MUST pin

1. **Code** — the exact git commit SHA of training code, feature code, and
   config. Not "the main branch" — the *commit*.
2. **Data** — the exact dataset version or content hash. Tools: **DVC** (Data
   Version Control), **LakeFS**, Delta Lake time-travel, or a dated snapshot in
   the feature store.
3. **Environment** — the exact library versions and system, captured in a
   **container image** (Docker), plus **fixed random seeds** for any stochastic
   step.

Miss any one and results drift silently. Pin all three and any run becomes a
deterministic, auditable function of its inputs.

### Why this is uniquely hard in ML

In classic software, pinning code + environment is enough (same input → same
output). ML adds **data** as a first-class input *and* **randomness** (weight
init, shuffling, dropout). Both must be controlled. This is exactly the
"reproducibility" row from the Module 1 comparison table, now made concrete.

> **First-principles takeaway:** a model is a *function of code, data, and
> environment*. If you don't version all three, you don't have a function — you
> have a coincidence.

---

## 9.6 Orchestration — Turning Steps into Pipelines

### Motivation

Training is never one step. It is: ingest data → validate → build features →
train → evaluate → register. Running these by hand, in order, retrying the one
that failed at 3 a.m., is toil. An **orchestrator** runs this sequence for you,
as a **DAG** (Directed Acyclic Graph — steps with dependencies, no cycles).

![Orchestration DAG: Ingest data to Validate+features, which fans out to Train model and Evaluate, both feeding into Register model; caption lists Kubeflow, Metaflow, TFX, Vertex, SageMaker Pipelines.](images/m09_06_orchestration.png)

### What an orchestrator gives you

- **Ordering & dependencies** — step B runs only after step A succeeds.
- **Retries & error handling** — a flaky data pull retries instead of failing the
  whole run.
- **Caching / incremental runs** — if only the model step changed, reuse the
  cached feature step (huge time and cost saver).
- **Scheduling & triggering** — run nightly, or on new data (this powers CT).
- **Observability** — a visual DAG showing what ran, what failed, and how long
  each step took.

### The main tools (know the flavour of each)

- **Kubeflow Pipelines** — pipelines native to **Kubernetes**; heavy but powerful,
  cloud-agnostic.
- **Metaflow** (Netflix) — Python-first, designed to be **data-scientist
  friendly**; you write normal Python and it handles scaling and versioning.
- **TFX** (Google TensorFlow Extended) — opinionated, production-grade components
  for TensorFlow pipelines, with strong data validation.
- **Vertex AI Pipelines** (Google) and **SageMaker Pipelines** (AWS) — managed
  cloud orchestrators so you don't run the control plane yourself.
- General-purpose: **Airflow** and **Prefect** (used widely, though not
  ML-specific).

> **Interview note:** you rarely need to pick the "right" orchestrator. What
> impresses is knowing *why* a pipeline/DAG exists at all — repeatability,
> caching, and triggering CT — and naming one or two tools confidently.

---

## 9.7 Containerization & Kubernetes for ML

### Motivation

"It works on my machine" is the oldest bug in software, and ML makes it worse:
CUDA versions, Python versions, exotic libraries. A **container** (Docker) packs
the code *and* its entire environment into one image that runs identically
everywhere — your laptop, CI, and production. This is the "environment" pin from
9.5, made portable.

Once you have many containers (training jobs, serving replicas), you need
something to **schedule, scale, and heal** them across a fleet of machines. That
is **Kubernetes (K8s)**.

![Containers + Kubernetes: a container image (code+env+libs) runs on a Kubernetes cluster, which schedules a Train pod (GPU) and two Serving pods, with autoscale and self-healing.](images/m09_07_k8s.png)

### Why ML teams standardise on this

- **Containers** = reproducible, portable environments. Build once, run anywhere;
  no more dependency drift between training and serving.
- **Kubernetes** = automatic scheduling of pods onto machines, **autoscaling**
  (add serving replicas when traffic spikes), **self-healing** (restart crashed
  pods), and **GPU-aware scheduling** (place a training pod on a GPU node).
- Together they let one platform run **bursty training jobs** and **always-on
  serving** on the *same* shared cluster, packing hardware efficiently.

### The ML-specific wrinkles

- **GPUs are special resources** — K8s must know which nodes have them and pin
  pods accordingly (`nvidia.com/gpu: 1`).
- **Serving vs training have opposite shapes** — serving is latency-sensitive and
  steady; training is throughput-sensitive and bursty. They compete for the same
  GPUs, which leads directly to the cost problem below.

---

## 9.8 Cost Management & GPU Scheduling

### Motivation

GPUs are the most expensive line item in most ML budgets — a single high-end GPU
node can cost thousands of dollars a month, and a large idle cluster burns money
doing nothing. Because Kubernetes makes it *easy* to request GPUs, teams
routinely over-provision. Cost management is the discipline of getting the work
done on the fewest GPU-hours.

### The main levers (first-principles: reduce idle GPU-hours)

- **Right-size the hardware.** Don't train a small model on the biggest GPU. Match
  the accelerator to the job.
- **Spot / preemptible instances.** For fault-tolerant training (with
  checkpointing), use interruptible instances at 60–90% discount.
- **Autoscaling to zero.** Serving replicas and training clusters should scale
  **down** when idle, not sit warm overnight.
- **Bin-packing & sharing.** Pack many small jobs onto one GPU (MIG / time-slicing)
  instead of one job per giant GPU. A **scheduler/queue** (e.g. Kubeflow's,
  Volcano, or Slurm-style) fairly shares scarce GPUs across teams.
- **Checkpointing.** Save training state often so a preempted job resumes instead
  of restarting — this is what makes spot instances safe.
- **Batch offline work.** Move non-urgent training to off-peak, cheaper capacity.

> **Senior signal:** when asked "how would you cut ML cost?", strong candidates go
> straight to *idle GPU-hours*: spot instances + checkpointing, scale-to-zero
> serving, and GPU sharing — not "use a smaller model" alone.

---

## 9.9 Platform Case Studies

### Motivation

The big ML companies each built an internal **ML platform** that packages
everything in this module. They look different but solve the *same* job:
pipelines + feature store + registry + serving + monitoring, made self-serve for
hundreds of teams. Knowing them by name and by "flavour" is a common interview
flex.

![Platform comparison: Uber Michelangelo (end-to-end, feature store first), Netflix Metaflow (data-scientist friendly, Python DAGs), Meta FBLearner (reusable workflows at huge scale), Google TFX (production pipelines on TensorFlow).](images/m09_08_platforms.png)

### The four to know

| Platform | Company | Signature idea | Notable for |
|----------|---------|----------------|-------------|
| **Michelangelo** | Uber | **End-to-end** platform; popularised the **feature store** | One system for train + serve + monitor; batch + online features |
| **Metaflow** | Netflix | **Data-scientist-first**; write plain Python, it handles scale/versioning | Low friction; great local-to-cloud story |
| **FBLearner Flow** | Meta | **Reusable workflows** run by non-experts at massive scale | Thousands of engineers, millions of models trained |
| **TFX** | Google | **Production pipelines** with strong data validation, on TensorFlow | Opinionated components; open-sourced; powers Google-scale ML |

### The common architecture underneath

Despite different philosophies, every platform converges on the same building
blocks: a **feature store** (Module 5), an **experiment tracker + registry** (9.2,
9.3), an **orchestrator** (9.6), a **serving layer** (Module 8), and
**monitoring** (Module 10) — all on shared containerised infra (9.7). The lesson:
these components are not fashion; they are the *minimum viable MLOps*.

---

## 9.10 The End-to-End MLOps Architecture

### Putting it all together

Everything in this module snaps into one loop. This is the diagram to draw on the
whiteboard when an interviewer says "now show me how you'd operate this in
production."

![End-to-end MLOps architecture: Data + Feature store to Training pipeline to Model registry to CI/CD deploy to Serving API to Monitoring, with a red dashed retrain-feedback arrow from Monitoring back to Data.](images/m09_09_e2e_architecture.png)

### Walk the loop (say this out loud in an interview)

1. **Data + feature store** — versioned data and shared features feed training.
2. **Training pipeline** — an orchestrated DAG produces a candidate model
   (tracked, reproducible).
3. **Model registry** — the candidate is registered, evaluated, and staged.
4. **CI/CD deploy** — tests pass, the model is promoted and shipped (canary /
   shadow first).
5. **Serving API** — the model answers live requests within its latency budget.
6. **Monitoring** — watches latency, errors, data drift, and business metrics.
7. **Feedback → retrain** — when monitoring detects drift or new labels arrive,
   **CT** fires and the loop repeats.

This is the Module 1 lifecycle loop, now with real machinery bolted on. If your
design answer walks this loop and names the tool at each stage, you are answering
at a Staff level.

> **First-principles takeaway:** MLOps is just the ML lifecycle made
> **automatic, reproducible, and observable**. Every tool in this module removes a
> specific manual step from that loop.

---

## Module 9 — Interview Mapping (what companies probe)

| Company | How Module 9 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "How do you deploy and keep this model fresh?" | "Push the model file to a server" | Registry + CI/CD/CT + monitoring loop; canary + rollback |
| **Amazon / AWS** | Operational excellence; SageMaker Pipelines | Lists services | Ties pipeline, registry, and cost controls to the business SLA |
| **Uber / Netflix** | Platform thinking; feature store, Metaflow | One-off scripts | Self-serve pipeline + feature reuse across teams |
| **Startups / OpenAI** | "How do you reproduce a result / control GPU cost?" | "Rerun the notebook" | Pin code+data+env; spot + checkpointing + scale-to-zero |

**The single most common follow-up:** *"Your model is deployed — now how do you
operate it?"* Answer with the end-to-end loop (9.10): registry, CI/CD/CT,
monitoring, rollback. Candidates who stop at "it's deployed" lose the offer here.

---

## Module 9 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT / GATE / ISRO:** MLOps is **almost entirely interview- and
  job-relevant, not written-exam material**. At most, a general-awareness paper
  might ask what "CI/CD" or "containerisation/Docker" means in a DevOps sense.
- **GATE DA:** knows the ML *workflow* (Module 1) but does not test MLOps tooling
  (MLflow, Kubeflow, registries) at any depth.
- **Bottom line:** invest here for **interviews and real MLE/AI-engineer work**,
  where this module is worth ★★★★★, not for written exams.

> **Flag:** this is one of the most *interview-only* modules in the course. Its
> value is in system-design rounds and on the job, not on multiple-choice exams.

---

## Module 9 — Common Mistakes & Misconceptions

1. **"MLOps = deploying a model."** No — it is the *whole loop*: tracking,
   registry, CI/CD/CT, reproducibility, monitoring. Deployment is one arrow.
2. **"CI/CD is enough for ML."** No — ML adds **CT (continuous training)** because
   models decay. CD ships code; CT ships a model from new data. (Section 9.4.)
3. **"Retrain nightly and you're safe."** Blind retraining can ship a *worse*
   model. Always gate promotion on a comparison to the current production model.
4. **"Pinning code reproduces the model."** No — you must pin **data + code +
   environment** (and seeds). Data and randomness are ML-specific. (Section 9.5.)
5. **"Bigger cluster = faster ML."** Idle GPUs are the real cost. Spot instances,
   scale-to-zero, and GPU sharing beat brute over-provisioning. (Section 9.8.)
6. **"Pick the best orchestrator."** The tool matters less than knowing *why* a
   pipeline DAG exists: repeatability, caching, and triggering CT. (Section 9.6.)
7. **"The registry is just a folder of files."** It is a versioned catalogue with
   stages and lineage that enables one-click rollback and audits. (Section 9.3.)

---

## Module 9 — MCQs (with answers & explanations)

**Q1.** Which loop is unique to ML and not present in ordinary software CI/CD?
a) Continuous Integration  b) Continuous Delivery
c) Continuous Training (CT)  d) Continuous Logging

<details><summary>Answer</summary>**c.** CT (Continuous Training) automatically
retrains and promotes a new model when data drifts or new labels arrive. It
exists because ML models decay; ordinary software does not need it.</details>

**Q2.** To reproduce a past model exactly, you must pin:
a) only the code  b) code + environment
c) code + data + environment (and seeds)  d) just the random seed

<details><summary>Answer</summary>**c.** A model is a function of code, data, and
environment. Miss any one (or an unfixed random seed) and results drift
silently.</details>

**Q3.** What is the primary purpose of a model registry?
a) Store training logs
b) A versioned catalogue of models with stages (staging/production/archived) and
   lineage, enabling promotion and rollback
c) Serve predictions
d) Track GPU cost

<details><summary>Answer</summary>**b.** The registry is the source of truth for
"which version is live", supports one-click rollback, and records lineage for
audits.</details>

**Q4.** A team is on the MLOps maturity ladder Level 0 (manual). What best
describes the *next* rung (Level 1)?
a) Fully automated CI/CD/CT
b) Automated, reusable training pipeline with a model registry
c) On-device inference
d) Bigger GPUs

<details><summary>Answer</summary>**b.** Level 1 automates the *training* pipeline
and adds a registry. CI/CD/CT for the pipeline itself is Level 2.</details>

**Q5.** The cheapest lever to cut GPU cost for a fault-tolerant training job is:
a) Buy more on-demand GPUs
b) Use spot/preemptible instances with checkpointing
c) Never scale down
d) Run everything at peak hours

<details><summary>Answer</summary>**b.** Spot instances are 60–90% cheaper;
checkpointing makes preemption safe by resuming instead of restarting. Idle
GPU-hours are the real enemy.</details>

**Q6.** Which pairing correctly matches platform to signature idea?
a) TFX → data-scientist-first Python
b) Metaflow → TensorFlow-only production components
c) Michelangelo → end-to-end platform that popularised the feature store
d) FBLearner → single-user notebook tool

<details><summary>Answer</summary>**c.** Uber's Michelangelo is the end-to-end
platform famous for its feature store. Metaflow (Netflix) is Python-first; TFX
(Google) is TensorFlow production pipelines; FBLearner (Meta) runs reusable
workflows at massive scale.</details>

**Q7.** Why is a training pipeline modelled as a DAG rather than one script?
a) DAGs run faster on GPUs
b) So steps have explicit dependencies, can retry/cache independently, and can be
   triggered/scheduled (enabling CT)
c) DAGs are required by Docker
d) It reduces model size

<details><summary>Answer</summary>**b.** A DAG gives ordering, per-step retries,
caching of unchanged steps, and scheduling/triggering — the machinery that makes
retraining repeatable.</details>

---

## Module 9 — Design Exercises (easy → hard)

- **Easy.** For a team emailing model files by hand, name their maturity level and
  the *one* next thing to build. *(Level 0; add a tracker + registry toward
  Level 1.)*
- **Easy.** List the three things you must version to reproduce a model, and one
  tool for each. *(Code→git; data→DVC; environment→Docker.)*
- **Medium.** Draw the CI/CD/CT loops for a churn model. Say what each loop tests
  or triggers, and what gate stops a bad model from reaching production.
- **Medium.** Your nightly retrain occasionally ships a worse model. Design the
  promotion gate that prevents this without a human in the loop for every run.
- **Hard.** Design the GPU scheduling policy for a shared cluster used by 5 teams
  running both bursty training and always-on serving. Address fairness, spot
  usage, checkpointing, and scale-to-zero. What breaks at 10× the teams?
- **Hard.** Draw the full end-to-end MLOps architecture for a fraud system and
  mark, at each stage, the tool you'd use and the one failure it prevents.

---

## Module 9 — Concept Review (one page)

- **MLOps** = the ML lifecycle made **automatic, reproducible, observable**. It is
  the plumbing that turns "a model" into "a reliable ML product".
- **Maturity ladder:** Level 0 manual → Level 1 automated training pipeline +
  registry → Level 2 CI/CD/CT. Match the rung to the stakes; don't over-build.
- **Experiment tracking** (MLflow, W&B) logs params, metrics, artifacts, and
  code/data versions so runs can be compared and reproduced.
- **Model registry** = versioned catalogue with stages (staging → production →
  archived) + lineage → enables promotion and **one-click rollback**.
- **CI/CD/CT:** CI tests code + data; CD ships the model; **CT** retrains on new
  data/drift. CT is the ML-only loop.
- **Reproducibility** = pin **data + code + environment** (+ seeds). Miss one and
  results silently differ.
- **Orchestration** (Kubeflow, Metaflow, TFX, Vertex, SageMaker) runs the pipeline
  as a **DAG**: ordering, retries, caching, scheduling/triggering.
- **Containers + Kubernetes** give portable environments + autoscaling +
  self-healing + GPU scheduling on shared infra.
- **Cost** = kill **idle GPU-hours**: spot + checkpointing, scale-to-zero, GPU
  sharing.
- **Platforms:** Michelangelo (Uber, feature store), Metaflow (Netflix, Python),
  FBLearner (Meta, scale), TFX (Google, TF pipelines) — same job, different
  flavour.

---

## Module 9 — Flash Cards (Q → A)

1. MLOps in one line? → *The ML lifecycle made automatic, reproducible, and
   observable.*
2. The three maturity rungs? → *Manual → automated training pipeline → CI/CD/CT.*
3. What does an experiment tracker log? → *Params, metrics, artifacts, and
   code/data versions.*
4. What does a model registry enable? → *Versioning, stages, lineage, and
   one-click rollback.*
5. What is CT? → *Continuous Training — auto-retrain + promote when data drifts;
   the ML-only loop.*
6. Three things to pin for reproducibility? → *Data, code, environment (plus
   seeds).*
7. Why model a pipeline as a DAG? → *Ordering, retries, caching, and
   triggering/scheduling (enables CT).*
8. Cheapest GPU cost lever for training? → *Spot instances + checkpointing; kill
   idle GPU-hours.*
9. Uber's platform and its signature idea? → *Michelangelo; the feature store.*

---

## Module 9 — Pattern Recognition (how to spot it in an interview)

- Hear **"now operate it in production"** → draw the end-to-end loop: registry →
  CI/CD/CT → serving → monitoring → retrain.
- Hear **"keep the model fresh / it decays"** → say **CT (continuous training)**
  gated by an evaluation.
- Hear **"reproduce this result / audit"** → pin **data + code + environment**;
  registry lineage.
- Hear **"roll back a bad model"** → model **registry** stages + archived
  versions.
- Hear **"cut ML cost / GPUs are expensive"** → **idle GPU-hours**: spot +
  checkpointing, scale-to-zero, GPU sharing.
- Hear **"many teams, many models"** → an internal **platform** (Michelangelo /
  Metaflow style): self-serve pipelines + feature store + registry.
- Hear **"it works on my machine"** → **containers** for portable environments.

---

## Module 9 — Revision Notes / Mini Cheat Sheet

```
MLOps = ML lifecycle made AUTOMATIC + REPRODUCIBLE + OBSERVABLE

MATURITY LADDER:  L0 manual -> L1 automated training + registry -> L2 CI/CD/CT
                  (match rung to stakes; don't over-build)

TRACKING (MLflow/W&B): log params | metrics | artifacts | code+data version
REGISTRY:              versions + stages (staging->prod->archived) + lineage
                       -> promote + ONE-CLICK ROLLBACK

CI  = test code + DATA VALIDATION + model sanity
CD  = ship model (canary/shadow, auto-rollback)
CT  = retrain on new data/drift + gate on eval  <-- ML-ONLY LOOP

REPRODUCIBILITY: pin DATA (DVC) + CODE (git SHA) + ENV (Docker + seed)

ORCHESTRATION (DAG): Kubeflow | Metaflow | TFX | Vertex | SageMaker
                     ordering | retries | caching | triggering(=CT)

CONTAINERS + K8S: portable env | autoscale | self-heal | GPU scheduling
COST: kill IDLE GPU-HOURS -> spot + checkpoint | scale-to-zero | GPU sharing

PLATFORMS: Uber Michelangelo(feature store) | Netflix Metaflow(Python) |
           Meta FBLearner(scale) | Google TFX(TF pipelines)  -> same job

E2E LOOP: data/features -> train -> registry -> CI/CD -> serve -> monitor -^
```

---

> **Next module:** *Module 10 — Monitoring, Drift & Model Reliability.* MLOps
> built the loop; now we make the **monitoring** arrow real — detecting data and
> concept **drift**, watching live metrics, setting alerts and kill switches, and
> deciding *when* to fire the CT retrain we wired up here.
