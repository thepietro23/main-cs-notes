---
title: "Module 2 — The ML System Design Interview Framework"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — The ML System Design Interview Framework

> **Why this module exists.**
> In Module 1 you learned *what* an ML system is and *why* it is different from
> ordinary software. But when an interviewer says "design an ML system for X",
> you have 45 minutes and a blank whiteboard, and knowledge alone is not enough —
> you need a **repeatable process** that keeps you calm, complete, and in
> control. Most candidates fail not because they lack ML knowledge, but because
> they ramble: they jump to a model, forget metrics, never mention serving, and
> run out of time. This module gives you a single **7-step framework** you can
> run on *any* design question, plus the soft skills — driving the conversation,
> managing time, and signalling seniority — that separate a hire from a no-hire.
> Everything here is plain English, built **problem → naive attempt → why it
> breaks → the fix**.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★★     | ★★★★★       |

> **Flag — this is an interview-centric module.** The 7-step framework, time
> management, and seniority signals are **almost entirely interview material**.
> Written exams (SEBI / RBI / GATE / ISRO) do *not* test "how you drive a design
> conversation". If you are studying only for a written exam, skim this module;
> if you are preparing for FAANG / AI-engineer / staff interviews, this is one of
> the most valuable modules in the whole course.

**What you must be able to do after this module:**
recite the 7-step framework and its mnemonic from memory; run it end-to-end on a
cold prompt in 45 minutes; separate functional from non-functional requirements
and show how the non-functional ones drive design; name business + ML and
offline + online metrics for any problem; handle "I don't know" and scope creep
without losing composure; and describe how a junior, senior, and staff candidate
answer the *same* question differently.

> **How to read this module.** For every idea we go **problem → simplest attempt
> → why it breaks → the fix**, and we tie each step to what a strong interview
> answer sounds like out loud.

---

## 2.1 The Universal 7-Step Framework

### Motivation (the problem that existed)

You are given a wide-open prompt: *"Design YouTube recommendations."* The naive
approach is to start talking about whatever comes to mind first — usually the
model ("I'd use a neural network..."). Within two minutes you are deep in
architecture details, you have never asked who the user is, you have not defined
success, and the interviewer is quietly marking you down for being unstructured.

The fix is to have a **fixed skeleton** in your head that works for *every*
question, so you never have to invent structure under pressure. You spend your
mental energy on the *content* of each step, not on remembering what comes next.

### Definition — the seven steps

1. **Clarify requirements & scope** — ask questions; pin down the goal, users,
   scale, and constraints *before* designing anything.
2. **Frame as an ML problem (or decide NOT to use ML)** — translate the business
   goal into one concrete ML task, or argue that a rule is better.
3. **Define metrics** — pick business + ML metrics, and offline + online metrics.
4. **Data & feature design** — what data exists, how it's labelled, what features
   you compute, and how you avoid leakage and training-serving skew.
5. **Model selection & training** — start with a baseline, justify complexity,
   pick a loss, plan training at scale.
6. **Serving, scaling & infrastructure** — batch vs online, latency budget,
   caching, and how it scales to the required QPS.
7. **Monitoring, iteration & failure handling** — detect drift, watch metrics,
   plan retraining, and design what happens when things break.

![The seven framework steps drawn as a serpentine flow with a dashed feedback arrow from monitoring back to clarifying requirements.](images/m02_01_seven_steps.png)

### Intuition & a memorable mnemonic

Think of the framework as a **recipe card** you pull out every time. You do not
re-invent cooking each night; you follow steps and vary the ingredients.

A mnemonic that sticks: **"Clever Frameworks Make Data Models Serve Metrics"** —
or just the initials **C-F-M-D-M-S-M**: **C**larify, **F**rame, **M**etrics,
**D**ata, **M**odel, **S**erve, **M**onitor. Say it three times; it fits on a
sticky note and will not desert you when you are nervous.

### First-principles: why exactly these seven, in this order

Each step answers a question that *must* be settled before the next makes sense:

- You cannot **frame** a problem until you know what "good" means → so **clarify
  first**.
- You cannot pick **data/features** until you know the **metric** you're
  optimising.
- You cannot choose a **model** until you know the data and the target.
- You cannot design **serving** until you know model size and latency needs.
- You cannot **monitor** until something is deployed — and monitoring feeds
  fresh data *back to step 1*, which is why the diagram loops.

The order is not arbitrary: it is a dependency chain. Skipping a step forces you
to guess, and a guess early on poisons everything downstream.

### Worked mini-example (spam detection, one line per step)

- **Clarify:** "Filter spam in a webmail inbox, ~1B emails/day, false-positive
  hurts more than false-negative."
- **Frame:** binary classification, spam vs not-spam.
- **Metrics:** business = user complaints / missed-important-mail; ML = precision
  at fixed recall (offline), user "mark as spam" rate (online).
- **Data:** past emails + user "spam/not-spam" labels.
- **Model:** start with logistic regression baseline → gradient-boosted trees.
- **Serve:** online scoring at delivery time, p99 < 50 ms.
- **Monitor:** watch precision, catch new spam campaigns (drift), retrain weekly.

That is a *complete* answer in seven sentences. The rest of the interview is you
going deeper on whichever step the interviewer pushes on.

---

## 2.2 Step 1 — Clarify Requirements & Scope

### Motivation

The single biggest reason candidates fail is **designing the wrong thing**. The
prompt "design a news feed" could mean a chronological feed (no ML!) or a
ranked, personalized feed at billion-user scale. If you assume, you might build
something impressive that does not answer the question.

### Naive attempt → why it breaks → fix

- **Naive:** start designing immediately to look decisive.
- **Why it breaks:** you bake in assumptions the interviewer never made; you
  optimise the wrong metric; you look junior.
- **Fix:** spend the first ~5 minutes asking targeted questions, then **state
  your assumptions out loud** and get a nod before proceeding.

### The clarifying-question checklist

Ask about five things (memorise these buckets):

1. **Goal / business objective** — what should improve? (engagement, revenue,
   safety). *"What does success look like for the business?"*
2. **Users & use case** — who uses it, on what device, how often?
3. **Scale** — how many users / requests per second / items in the catalogue?
4. **Constraints** — latency budget, cost, privacy, regulation, team size.
5. **Scope for today** — *"Should I focus on the ranking model, or the whole
   pipeline?"* This one sentence prevents you from spreading too thin.

> **Senior signal:** finishing clarification with *"So to confirm: we're
> building X, optimising for Y, at Z scale, with these constraints — is that
> right?"* This one-sentence recap shows structure and buys you a checkpoint.

We separate the *what* from the *how well* using functional vs non-functional
requirements — the subject of Section 2.4.

---

## 2.3 Step 2 — Frame as an ML Problem (or Decide NOT To)

### Motivation

A business goal ("keep users watching") is not an ML task. You must translate it
into a *specific* learning problem with a clear input and output — or recognise
that ML is overkill.

### The decision, then the mapping

First, honour the Module 1 rule: **is a simple rule good enough?** If yes, say so
— proposing a rule-based baseline is a senior move, not a weakness. If not, map
the goal to exactly **one** ML task type.

![Decision flow: business goal, then ask if a simple rule solves it (yes leads to a rule/heuristic), otherwise pick one ML task type among classification, ranking, regression, or generation.](images/m02_02_frame_or_not.png)

### The common task types (know these cold)

| Business goal | ML framing | Task type |
|---------------|------------|-----------|
| "Is this email spam?" | predict a label | **Binary classification** |
| "Which video next?" | order items by relevance | **Ranking / recommendation** |
| "How long till delivery?" | predict a number | **Regression** |
| "Write a reply / summary" | produce text | **Generation (LLM)** |
| "Group similar users" | find structure, no labels | **Clustering (unsupervised)** |

### First-principles: what makes a *good* framing

A good framing is one where (a) you can get **labels** (or a signal) for the
target, (b) the target is a **proxy the business actually cares about**, and
(c) the prediction can be **acted on**. Framing "watch time" as
"predict-probability-of-completing-a-video" is good because clicks/completions
are logged, they correlate with watch time, and you can rank by the score.

### Anti-pattern to avoid

Framing the problem as the *business metric itself* ("predict revenue") when the
model can only influence it indirectly. Predict the **immediate, learnable
signal** (click, completion) and let the ranking of those scores move the
business metric — which you then verify with an online test.

---

## 2.4 Functional vs Non-Functional Requirements

### Motivation

Two systems can have the *same* function — "recommend 10 items" — but wildly
different designs, because one needs answers in 20 ms at 100k QPS and the other
can run overnight. The *qualities* decide the architecture, not the function.

### Definitions

- **Functional requirement** = *what* the system does. "Return 10 ranked videos",
  "flag fraudulent transactions", "answer a question from our docs".
- **Non-functional requirement (NFR)** = *how well* it must do it: latency,
  throughput, scale, availability, cost, freshness, privacy, fairness.

![Two columns: functional requirements list what the system does; non-functional requirements list latency, throughput, and scale/cost/availability.](images/m02_04_func_vs_nonfunc.png)

### Why NFRs matter more in ML interviews

The functional part is often given in the prompt ("design recommendations").
The *interesting* design decisions — batch vs online, model size, caching,
sharding — all come from the NFRs. A candidate who nails down "p99 < 100 ms at
50k QPS on a $X budget" has *derived the design constraints* rather than guessing.

### The four NFRs you must always quantify

| NFR | Question to ask | Why it drives design |
|-----|-----------------|----------------------|
| **Latency** | "What p99 can the user tolerate?" | Decides online vs batch, model size |
| **Throughput** | "Requests per second at peak?" | Decides replicas, sharding, precompute |
| **Scale** | "How many users / items?" | Decides storage, ANN indexes, cost |
| **Cost** | "What's the compute budget?" | Decides model complexity, caching |

> **Rule of thumb:** always put a *number* on each NFR, even a rough one. "About
> 100 ms" beats "fast". Numbers let you do back-of-the-envelope sizing and show
> engineering maturity.

---

## 2.5 How Non-Functional Requirements Drive Design

### Motivation

Beginners treat NFRs as a checklist to recite. Seniors use each NFR as a
*lever*: state the number, then let it force a specific architectural choice.
This is where the interview stops being a quiz and becomes engineering.

### The requirement → implication map

![Three requirement boxes on the left map by arrows to design-implication boxes on the right: tight latency to small model plus cache plus ANN index; huge throughput to batch precompute plus horizontal scaling; low cost budget to a simpler model or distillation.](images/m02_05_nfr_drives_design.png)

Read each row aloud in an interview as *"Because the requirement is X, I will
do Y."* That causal sentence is exactly the seniority signal graders listen for.

### Worked reasoning chain

Suppose the interviewer says **p99 < 30 ms at 80k QPS**:

1. 30 ms is too tight to run a giant model per request → **precompute candidates
   in batch**, then **re-rank a small set online** (the hybrid pattern from
   Module 1).
2. 80k QPS × per-request work → you need **many replicas** behind a load
   balancer, plus a **cache** for hot users.
3. Fetching nearest items from millions of candidates in real time → use an
   **approximate-nearest-neighbour (ANN) index**, not a brute-force scan.

Notice you designed the *whole serving stack* purely by taking the NFRs
seriously. That is the point: **NFRs are the design.**

### Trade-off table

| If you tighten... | You usually pay with... | Typical fix |
|-------------------|-------------------------|-------------|
| Latency | Model accuracy (smaller model) | Distillation, caching, hybrid serving |
| Cost | Freshness or accuracy | Batch precompute, fewer features |
| Throughput | Infra complexity | Horizontal scaling, sharding |
| Freshness | Cost / latency | Streaming features, online inference |

---

## 2.6 Step 3 — Define Metrics (Business + ML, Offline + Online)

### Motivation

If you cannot measure success, you cannot design toward it — and you certainly
cannot know when to ship. Yet candidates routinely name a single metric
("accuracy") and move on. Real systems need a *small basket* of metrics along
two axes.

### The two axes → four kinds of metric

- **Business vs ML.** Business metrics (revenue, retention, CTR) are what
  leadership cares about. ML metrics (AUC, F1, NDCG) are what you can optimise
  directly. They are linked but *not* the same.
- **Offline vs online.** Offline metrics are computed on held-out data before
  launch. Online metrics come from live users, usually via an A/B test.

![A 2x2 of metrics: axes are offline vs online and ML vs business, giving business+offline (proxy), business+online (revenue/CTR/retention via A/B), ML+offline (AUC/F1/NDCG on holdout), and ML+online (live accuracy, latency, coverage).](images/m02_03_metrics_2x2.png)

### First-principles: why you need all four

- **ML + offline** lets you iterate fast without shipping (cheap, repeatable).
- **Business + online** is the *only* thing that proves value — but it is slow
  and expensive to run.
- The gap between them (the **offline–online gap**, Module 7) is why you need
  *both*: a model that wins offline can lose online.

### Worked example (recommendations)

| Axis | Metric | Used for |
|------|--------|----------|
| ML + offline | NDCG@10 on last week's logs | day-to-day iteration |
| ML + online | live click-through rate | validating the model live |
| Business + online | watch time, 30-day retention | the ship/no-ship decision |
| Guardrail | latency p99, diversity | make sure we didn't break UX |

> **Senior signal:** naming a **guardrail metric** ("we must not hurt latency or
> diversity while chasing CTR") shows you think about side-effects, not just the
> target.

---

## 2.7 Steps 4–7 — Data, Model, Serving, Monitoring (in brief)

These four steps each get a full module later; here is the framework-level view
so your answer is *complete* even before you go deep.

- **Step 4 — Data & features.** What data exists, how it's labelled, freshness,
  and volume. Design features and store them so **training and serving agree**
  (avoid training-serving skew) and no future info leaks in (avoid leakage).
  *(Modules 4–5.)*
- **Step 5 — Model & training.** *Always propose a simple baseline first*
  (logistic regression, popularity, a heuristic), then justify each jump in
  complexity by a metric gain. Pick a loss aligned to the metric; plan
  distributed training if data is large. *(Module 6.)*
- **Step 6 — Serving, scaling & infra.** Choose batch / online / streaming from
  the NFRs; place caches and ANN indexes; size replicas for the QPS; state the
  latency budget. *(Modules 8, 11, 19.)*
- **Step 7 — Monitoring, iteration & failure handling.** Watch drift and the
  business metric; alert on degradation; plan retraining cadence; and design the
  **failure path**: shadow mode, canary rollout, kill switch, and a safe
  fallback (e.g. show popular items if the model is down). *(Module 10.)*

> **Completeness beats depth-in-one-spot.** A candidate who names all seven
> steps and goes moderately deep beats one who spends 40 minutes only on model
> architecture and never mentions serving or monitoring.

---

## 2.8 Driving the Interview & Managing 45 Minutes

### Motivation

You could know every step and still fail by spending 30 minutes on step 1 and
never reaching serving. The interview is a **time-boxed performance**; managing
the clock is itself a graded skill.

### A time budget you can actually use

![A five-phase horizontal timeline: clarify and scope (~5 min), frame plus metrics (~8 min), data and features (~10 min), model and serving (~12 min), scale/monitor and wrap-up (~10 min), with a note to announce the plan up front and reserve the last 5 minutes.](images/m02_06_time_budget.png)

The exact minutes flex, but the *shape* holds: cheap up-front scoping, the bulk
in the middle on data/model/serving, and a protected block at the end for
trade-offs, failure modes, and "what I'd do next".

### How to drive (not be driven)

- **Announce your plan first:** *"I'll clarify, frame it, define metrics, then
  design data, model, serving, and monitoring — pushing me to go deeper anywhere
  is welcome."* This tells the interviewer you have structure and invites them to
  steer.
- **Narrate your reasoning.** Say *why* you choose each thing; graders score your
  thought process, not just the final diagram.
- **Check in at transitions:** *"That's the model — want me to go deeper here or
  move to serving?"* This keeps you aligned and paced.
- **Use the whiteboard as a map.** Draw the 7 steps (or the architecture) early
  so both of you can see progress.

### Handling "I don't know"

Never freeze or bluff. The strong move is: **state what you do know, reason from
first principles, and say how you'd find out.** Example: *"I haven't used that
exact index, but the requirement is fast nearest-neighbour lookup over millions
of vectors, so I'd reach for an ANN structure like HNSW and benchmark recall vs
latency."* You just turned a gap into a display of reasoning.

### Handling scope creep

Interviews sprawl — you can end up designing five subsystems at once. When that
happens: *"There are several directions here; the highest-impact one for our
metric is X, so I'll focus there and mention the others briefly."* **Explicitly
choosing scope** is a seniority signal; trying to do everything shallowly is not.

> **Common mistake:** treating interviewer interruptions as attacks. They are
> usually *hints* about where they want depth. Follow the pull.

---

## 2.9 Junior vs Senior vs Staff Answer Patterns

### Motivation

The *same* question is asked of a new grad and a staff engineer; the difference
is entirely in *how* they answer. Knowing the target behaviour lets you aim for
the next level up.

![Three columns comparing junior, senior, and staff answers: junior jumps to a model, lists tools, ignores trade-offs; senior follows the framework, names metrics, weighs trade-offs; staff clarifies and questions whether ML is needed, ties to business, and plans failure and iteration.](images/m02_07_seniority.png)

### The comparison in words

| Dimension | Junior | Senior | Staff |
|-----------|--------|--------|-------|
| **Opening** | Jumps to a model | Clarifies, then frames | Questions if ML is even needed |
| **Structure** | Ad-hoc, wanders | Follows the framework | Framework + adapts to the twist |
| **Metrics** | "Accuracy" | Business + ML, offline + online | Adds guardrails + cost of errors |
| **Trade-offs** | Ignores them | Weighs the obvious ones | Owns them, quantifies, decides |
| **Systems** | Talks model only | Covers serving & scale | Ties ML ↔ systems ↔ business |
| **Failure** | Not mentioned | Mentions monitoring | Designs rollback, canary, fallback |
| **Scope** | Tries to do all | Picks a focus when asked | Proactively scopes and prioritises |

### First-principles: what "seniority" actually is

Seniority in this interview is **not** deeper math. It is **breadth plus
ownership of trade-offs**: connecting the business goal, the ML choice, and the
systems constraint into one coherent story, and being willing to say *"here's the
trade-off, and here's the call I'd make, because..."*. A staff candidate makes
*decisions*; a junior lists *options*.

> **Aim one level up.** If you're targeting senior, don't just follow the
> framework — start weighing trade-offs out loud and tie every choice to the
> business metric.

---

## Module 2 — Interview Mapping (what companies probe)

| Company | How Module 2 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "Design system for X" — they grade *structure* | Wanders, model-first | Runs the 7 steps, checks in, scopes |
| **Amazon** | Ties to Leadership Principles; "dive deep" on one step | Stays shallow everywhere | Goes deep where pushed, ties to customer |
| **OpenAI / Anthropic** | Framing + baselines + when NOT to use ML | Over-engineers | Proposes simple baseline, justifies complexity |
| **Uber / Stripe** | NFR-driven design (latency, fraud cost) | Ignores latency/QPS | Derives design from quantified NFRs |

**The single most common opening question:** *"How would you design an ML system
for X?"* Your first 60 seconds should announce the framework and start clarifying.
That structure alone puts you ahead of most candidates.

---

## Module 2 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **This is an interview-only module.** Written exams do **not** test how you
  drive a design conversation, budget 45 minutes, or signal seniority.
- **SEBI IT / RBI IT / ISRO:** may ask *definitional* items at most — the
  difference between functional and non-functional requirements (Section 2.4) is
  a standard software-engineering exam topic, so know that one crisply.
- **GATE CS/DA:** the ML task-type taxonomy (classification / regression /
  ranking / clustering) from Section 2.3 overlaps with the syllabus; the
  framework and time-management content does not appear.

> **Bottom line:** if you are studying purely for a written exam, the only
> exam-relevant slice here is *functional vs non-functional requirements* and the
> *task-type taxonomy*. Everything else is high-value **interview** material.

---

## Module 2 — Common Mistakes & Misconceptions

1. **Jumping straight to the model.** Skipping clarify + frame is the #1
   failure. Always start with questions. (Sections 2.2–2.3.)
2. **Naming one metric ("accuracy").** You need business + ML and offline +
   online, plus a guardrail. (Section 2.6.)
3. **Ignoring non-functional requirements.** Latency/throughput/scale/cost are
   what actually drive the design. (Sections 2.4–2.5.)
4. **No time management.** Spending 30 minutes on one step and never reaching
   serving or monitoring. (Section 2.8.)
5. **Bluffing on "I don't know".** Reason from first principles and say how you'd
   find out instead. (Section 2.8.)
6. **Trying to design everything.** Scope explicitly; depth-where-it-matters beats
   shallow-everywhere. (Section 2.8.)
7. **Forgetting the failure path.** No monitoring, rollback, or fallback. A model
   *will* break; design for it. (Section 2.7.)

---

## Module 2 — MCQs (with answers & explanations)

**Q1.** What should be the *first* thing you do when given "design an ML system
for X"?
a) Pick a neural network
b) Clarify requirements, scope, and success metric
c) Draw the database schema
d) Estimate GPU cost

<details><summary>Answer</summary>**b.** Clarifying the goal, users, scale, and
constraints prevents you from designing the wrong thing. Everything downstream
depends on it.</details>

**Q2.** Which is a *non-functional* requirement?
a) "Return 10 recommended videos"
b) "Flag fraudulent transactions"
c) "p99 latency under 100 ms at 50k QPS"
d) "Answer questions from our docs"

<details><summary>Answer</summary>**c.** Latency/throughput are *qualities* (how
well), i.e. non-functional. The others describe *what* the system does
(functional).</details>

**Q3.** A model wins on offline NDCG but the live A/B test shows no lift in watch
time. This illustrates:
a) a compile error  b) the offline–online gap  c) overfitting the test set
d) a cache miss

<details><summary>Answer</summary>**b.** Offline and online metrics can disagree;
the online business metric is what decides whether you ship. This is why you
define metrics on both axes.</details>

**Q4.** In the framework, why must "define metrics" come *before* "choose a
model"?
a) It doesn't matter  b) Because the metric decides the loss and what "better"
means  c) Models are optional  d) To save time

<details><summary>Answer</summary>**b.** You cannot choose a model or loss
function, or tell whether one model beats another, without first knowing the
metric you're optimising.</details>

**Q5.** The interviewer asks about a technique you've never used. Best response?
a) Pretend you know it in detail
b) Say "no idea" and stop
c) State what you know, reason from first principles, and say how you'd find out
d) Change the subject

<details><summary>Answer</summary>**c.** Turning a gap into visible reasoning
scores well; bluffing and freezing both score poorly.</details>

**Q6.** Which best characterises a *staff-level* answer versus a junior one?
a) Uses a bigger model
b) Knows more math
c) Owns trade-offs and connects ML ↔ systems ↔ business
d) Talks faster

<details><summary>Answer</summary>**c.** Seniority here is breadth plus owning
trade-offs and decisions, not deeper math or a fancier model.</details>

**Q7.** A requirement of "p99 < 30 ms at 80k QPS" most directly pushes you
toward:
a) Training a bigger model per request
b) Hybrid serving: batch-precompute candidates + small online re-rank + cache
c) Removing all caching  d) Ignoring latency

<details><summary>Answer</summary>**b.** Tight latency at high QPS forces
precompute + a small online model + caching/ANN — the NFRs derive the
architecture.</details>

**Q8.** What is a *guardrail metric*?
a) The single metric you optimise
b) A metric you must not harm while chasing the target (e.g. latency, diversity)
c) A database constraint  d) A type of loss function

<details><summary>Answer</summary>**b.** Guardrails protect against harmful
side-effects of optimising the target metric; naming them is a senior
signal.</details>

---

## Module 2 — Design Exercises (easy → hard)

- **Easy.** Classify each as functional or non-functional: (1) "recommend 5
  songs"; (2) "99.9% availability"; (3) "detect toxic comments"; (4) "cost under
  $10k/month". *(Functional: 1, 3. Non-functional: 2, 4.)*
- **Easy.** For "predict food-delivery ETA", write the 7-step framework as one
  sentence per step.
- **Medium.** Given "design search ranking, p99 < 100 ms, 100k QPS", list three
  design choices that follow *directly* from the NFRs and explain the causal
  link for each.
- **Medium.** For a fraud-detection system, name one metric in each quadrant of
  the metrics 2×2 (business/ML × offline/online) plus one guardrail.
- **Hard.** You're 30 minutes into a 45-minute interview and have only covered
  clarify + frame + model. Describe how you'd re-budget the remaining 15 minutes
  and what you would deliberately cut.
- **Hard.** Take the prompt "design comment ranking for a social app" and write
  the *same* answer at three levels — junior, senior, staff — highlighting what
  changes at each level.

---

## Module 2 — Concept Review (one page)

- The **7-step framework** (mnemonic **C-F-M-D-M-S-M**): Clarify → Frame →
  Metrics → Data → Model → Serve → Monitor, looping back via monitoring.
- **Clarify first** — goal, users, scale, constraints, and *scope for today* —
  then recap assumptions before designing.
- **Frame** the goal as *one* ML task (classification / ranking / regression /
  generation / clustering), or argue for a **rule** if ML isn't warranted.
- **Metrics** live on two axes: **business vs ML** and **offline vs online**;
  add a **guardrail**. Offline guides iteration, online decides shipping.
- **Functional** = what it does; **non-functional** (latency, throughput, scale,
  cost) = how well — and NFRs *drive the architecture*. Put a number on each.
- **Data → Model → Serve → Monitor:** agree train/serve features, start with a
  baseline, pick serving mode from NFRs, and design the failure path.
- **Drive the interview:** announce your plan, narrate reasoning, check in at
  transitions, budget the 45 minutes, scope explicitly.
- **Seniority** = breadth + owning trade-offs (business ↔ ML ↔ systems), not more
  math. Handle "I don't know" by reasoning aloud.

---

## Module 2 — Flash Cards (Q → A)

1. The 7 steps in order? → *Clarify, Frame, Metrics, Data, Model, Serve,
   Monitor.*
2. Mnemonic? → *C-F-M-D-M-S-M.*
3. First thing to do in any design prompt? → *Clarify requirements, scope, and
   success metric.*
4. Functional vs non-functional? → *What it does vs how well (latency,
   throughput, scale, cost).*
5. Two axes of metrics? → *Business vs ML; offline vs online.*
6. What decides ship / no-ship? → *The online business metric (A/B test).*
7. Why define metrics before choosing a model? → *The metric decides the loss and
   what "better" means.*
8. How to handle "I don't know"? → *State what you know, reason from first
   principles, say how you'd find out.*
9. Seniority in one line? → *Breadth + owning trade-offs (business ↔ ML ↔
   systems), not more math.*
10. What is a guardrail metric? → *One you must not harm while chasing the
    target (e.g. latency, diversity).*

---

## Module 2 — Pattern Recognition (how to spot it in an interview)

- Hear **"Design an ML system for X"** → announce the 7-step framework, start
  clarifying.
- Hear **"How would you measure success?"** → give business + ML, offline +
  online, plus a guardrail.
- Hear **"It must handle N QPS at M ms"** → derive serving design from the NFRs
  (precompute, cache, ANN, replicas).
- Hear **"What if you don't know Z?"** → reason from first principles, say how
  you'd find out.
- Hear **"We could also do A, B, C..."** (scope creep) → pick the highest-impact
  one, mention the rest briefly.
- Hear **"What could go wrong in production?"** → drift, monitoring, rollback,
  canary, and a safe fallback.
- Running low on time → protect the last 5 minutes for trade-offs and next steps.

---

## Module 2 — Revision Notes / Mini Cheat Sheet

```
7-STEP FRAMEWORK  (mnemonic: C-F-M-D-M-S-M)
  1 CLARIFY   goal / users / scale / constraints / SCOPE-for-today  -> recap!
  2 FRAME     rule? else pick ONE task: classify | rank | regress | generate
  3 METRICS   axes = (business vs ML) x (offline vs online) + a GUARDRAIL
  4 DATA      labels, freshness, features; avoid leakage + train/serve skew
  5 MODEL     start SIMPLE baseline -> justify each jump; loss = metric
  6 SERVE     batch/online/streaming from NFRs; cache + ANN + replicas
  7 MONITOR   drift, business metric, retrain; rollback + canary + FALLBACK
              -> monitoring feeds fresh data back to step 1 (LOOP)

REQUIREMENTS
  FUNCTIONAL     = what it does           NON-FUNCTIONAL = how well
  NFRs (number each!): latency | throughput | scale | cost
  NFRs DRIVE DESIGN:  say "because req X, I will do Y"

METRICS
  offline (holdout) guides iteration | online (A/B) decides SHIP
  offline win != online win  (the offline-online gap)

INTERVIEW CRAFT (45 min)
  announce plan -> clarify(5) frame+metrics(8) data(10) model+serve(12) wrap(10)
  narrate WHY | check in at transitions | scope explicitly
  "I don't know" -> reason from first principles + how to find out

SENIORITY = breadth + OWN the trade-offs (business <-> ML <-> systems)
  junior lists options | staff makes decisions + plans failure
```

---

> **Next module:** *Module 3 — Framing: From Business Problem to ML Problem.* We
> zoom into Step 2 of the framework and learn, in depth, how to translate a fuzzy
> business goal into a precise ML task — choosing the target, the label, and the
> proxy signal — and how a poor framing quietly dooms every later stage.
