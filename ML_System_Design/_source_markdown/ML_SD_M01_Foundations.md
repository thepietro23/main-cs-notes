---
title: "Module 1 — Foundations of ML Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Foundations of ML Systems

> **Why this module comes first.**
> Before you can design a recommender, tune a feature store, or reason about
> model serving, you must understand *what an ML system actually is*, *why it is
> fundamentally different from ordinary software*, and *how the whole thing fits
> together end to end*. Almost every later topic in this course is an answer to
> a problem first raised here. Candidates who skip these foundations later
> confuse "a model" with "an ML system", forget the feedback loop, and get
> surprised when their accurate model quietly rots in production. We will not let
> that happen. We start from the world *before* ML and build the mental model
> brick by brick, in plain English.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★         | ★★★★      | ★★★★★       |

**What you must be able to do after this module:**
explain Software 1.0 vs 2.0 in one sentence; list the seven stages of the ML
lifecycle and why it is a *loop*; name the four ways ML systems differ from
normal software (data dependencies, feedback loops, non-determinism, decay);
classify a system as batch / online / streaming / on-device / federated and
justify the choice; and decide *when NOT to use ML* — which is itself a senior
signal in interviews.

> **How to read this module.** For every idea we go **problem → simplest
> attempt → why it breaks → the fix**. We explain the *why* before the *how*,
> and we tie every concept to how it shows up in a real Google / Meta / Amazon
> interview.

---

## 1.1 What Is an ML System? (Software 1.0 vs Software 2.0)

### Motivation (the problem that existed)

Imagine you must build a spam filter for email in 2005. The obvious approach is
to sit down and **write rules by hand**:

```
if email contains "FREE MONEY"      -> spam
if email contains "viagra"          -> spam
if sender not in contacts AND
   subject in ALL CAPS              -> spam
...
```

This is **ordinary programming**: a human thinks hard, writes explicit `if/else`
logic, and the computer follows those instructions exactly. It works — until it
doesn't. Spammers write "F.R.E.E M0NEY", or "ⓕⓡⓔⓔ", or switch languages, and
your rule list explodes into thousands of brittle lines that still miss new
tricks. You are playing an endless game of whack-a-mole.

The **insight of Machine Learning** is to flip the problem around. Instead of
writing the rules yourself, you show the computer **thousands of examples**
("this email is spam", "this one is not") and let it **learn the rules on its
own**. The learned rules live inside a *model* (a set of numbers, called
parameters). When a new email arrives, the model outputs a probability that it
is spam.

### Definition

- **Software 1.0** = traditional software. A human writes explicit rules (code).
  Input + Rules → Output. The behaviour is fixed until a human edits the code.
- **Software 2.0** (a term popularised by Andrej Karpathy) = machine learning.
  A human provides Input + desired Output (examples), and a training algorithm
  *produces the rules* (the model). The behaviour changes when you feed it new
  data.
- An **ML system** is the *entire production setup* that turns raw data into
  useful predictions for real users — not just the model. It includes data
  pipelines, feature computation, training, serving, monitoring, and the
  feedback loop. **A model is one part of an ML system, the way an engine is one
  part of a car.**

![Top: Software 1.0 — humans write the rules. Bottom: Software 2.0 — we give data plus answers and the machine learns the rules (the model).](images/m01_01_sw1_vs_sw2.png)

### Intuition & analogy

Think of teaching a child to recognise a dog.

- **Software 1.0 way:** you write a checklist — "four legs, fur, tail, barks".
  But a cat also has four legs and fur; a dog with three legs still is a dog.
  The checklist never quite works.
- **Software 2.0 way:** you point at hundreds of animals and say "dog", "not a
  dog". The child *generalises* and soon recognises breeds it has never seen.
  You never wrote down what a dog "is" — the child learned it from examples.

That is the core trade you make with ML: **you give up writing exact rules, and
in return you get a system that handles messy, fuzzy patterns you could never
enumerate by hand.** The price is that the system is now *statistical* — it is
usually right, not always right.

### First-principles derivation (why ML exists at all)

Ask: *when is learning-from-data better than writing rules?* Three conditions
must all hold:

1. **A pattern exists.** There must be a real relationship between the inputs
   (email text) and the output (spam or not). If the output is pure randomness
   (like a fair coin flip), no amount of data helps.
2. **You cannot write the rules by hand** — either because they are too complex
   (recognising faces), too numerous (spam tricks), or they keep changing.
3. **You have data** that captures the pattern (labelled examples, or at least
   lots of raw examples).

If all three hold, ML wins. If any fails, plain code is simpler, cheaper, and
more reliable. Memorise this — interviewers love the candidate who says "we may
not need ML here."

### When NOT to use ML (anti-pattern)

Use this quick decision flowchart before reaching for a model:

![Decision flowchart: if a simple rule solves it, use rules; only use ML when patterns exist, data exists, and some error is acceptable.](images/m01_06_fc_use_ml.png)

- The rule is simple and stable ("block emails from this exact address").
- You have almost no data.
- You cannot tolerate *any* mistake and there is no human safety net (e.g. a
  system that must be 100% correct with legal consequences).
- You cannot measure success (no metric, no labels, no feedback).

> **Senior signal:** In an interview, before jumping to a model, a Staff-level
> candidate first asks "should this even be ML?" A junior candidate immediately
> reaches for a neural network.

---

## 1.2 Why ML System Design Is Fundamentally Different

### Motivation

If you already know classic system design (load balancers, databases, caches,
queues), you might think ML system design is "just system design with a model
box in the middle". That intuition is *dangerously incomplete*. ML systems
inherit **every** classic concern **and add four brand-new ones** that break
things in ways ordinary software never does.

![Classic systems have deterministic logic and fixed behaviour. ML systems add probabilistic outputs, "good-enough" metrics, decay over time, and richer testing.](images/m01_07_ml_vs_classic.png)

### The four things that make ML systems hard

**1. Data dependencies (data is now part of your code).**
In Software 1.0, your logic lives entirely in code you can read and review. In
ML, the behaviour is decided by *data* — and data is messy, changes without
warning, and is often owned by another team. A schema change upstream ("age is
now in months, not years") can silently corrupt your model with no error
message. There is a saying: **"Changing anything changes everything"** (the
*CACE* principle). Data dependencies are harder to track than code
dependencies, and they are the number-one source of production ML bugs.

**2. Feedback loops (the system changes the world it learns from).**
An ML system's own predictions influence future data. A recommender that only
shows popular items collects clicks *only* on popular items, "proving" they are
popular, so it shows them even more. The model shapes the very data it will next
be trained on. This can be a virtuous *flywheel* — or a vicious loop that
amplifies bias. Ordinary software does not have this problem.

**3. Non-determinism ("good enough", not "correct").**
A sorting function is either correct or buggy. A model is *never* perfectly
correct — it is 94% accurate, or has an AUC of 0.89. There is no single right
answer; there are trade-offs (precision vs recall, latency vs accuracy). You
ship something that is *good enough for the business metric*, and reasonable
engineers can disagree about what "good enough" means.

**4. Decay (the model rots even if you touch nothing).**
Deploy a working web server and leave it alone: it keeps working. Deploy a
working model and leave it alone: it *gets worse over time*, because the world
drifts away from the data it was trained on. User tastes change, fraudsters
adapt, new products launch, a pandemic hits. This silent rot is called **drift**
(covered in depth in Module 10) and it means an ML system is never "done".

### The "hidden technical debt" picture

A famous Google paper (Sculley et al., *"Hidden Technical Debt in Machine
Learning Systems"*, NeurIPS 2015) makes the key point with one picture: the
actual ML model code is a **tiny box** surrounded by a huge amount of
infrastructure — data collection, feature extraction, verification, serving,
monitoring, configuration.

![The ML model code is the small orange box; the real work is the large surrounding infrastructure — data, features, serving, monitoring, configuration.](images/m01_03_hidden_debt.png)

> **First-principles takeaway:** "Doing ML" in production is 90% systems and data
> work, 10% modelling. This is exactly why *ML system design* is its own
> interview and its own discipline. If your answer is all about model
> architecture, you are answering the wrong question.

### Classic traps that only exist in ML (preview)

You will meet these repeatedly; know the names now:

| Trap | One-line meaning | Fixed in module |
|------|------------------|-----------------|
| **Training-serving skew** | Features computed differently in training vs live serving | M05 |
| **Data leakage** | Info from the future/label sneaks into features → great offline, terrible live | M04, M07 |
| **Drift** | The world moves away from the training data → accuracy decays | M10 |
| **Feedback loops** | Model's predictions bias the next training data | M10, M12 |
| **Offline–online gap** | Offline metric improves but the live business metric does not | M07 |

---

## 1.3 The End-to-End ML Lifecycle

### Motivation

Beginners picture ML as "train a model, done". In reality, production ML is a
**repeating loop** of seven stages. Understanding this loop is the backbone of
the whole course — every module you study later slots into one of these stages.

![The seven-stage ML lifecycle drawn as a loop; monitoring feeds fresh data back to the start so the model can be retrained as the world drifts.](images/m01_02_ml_lifecycle.png)

### The seven stages (what happens and why)

1. **Business problem → ML problem.** Start from a business goal ("increase
   watch time") and translate it into a concrete ML task ("predict which video a
   user will watch next"). Getting this wrong dooms everything downstream.
   *(Module 3.)*
2. **Data.** Collect, clean, label, and version the data. In practice this is
   where most of the time and pain live. *(Module 4.)*
3. **Features.** Turn raw data into numerical signals the model can use
   (features), and store them so training and serving agree. *(Module 5.)*
4. **Train the model.** Pick a model, choose a loss function, and fit it to the
   data, possibly across many machines. *(Module 6.)*
5. **Evaluate.** Measure quality *offline* (on held-out data) with the right
   metric, and check for leakage and bias. *(Module 7.)*
6. **Deploy & serve.** Put the model behind an API (or on-device), meeting a
   latency and cost budget. *(Modules 8, 11.)*
7. **Monitor & iterate.** Watch for drift, errors, and degraded metrics; collect
   fresh data; retrain. This closes the loop back to stage 2. *(Module 10.)*

### Why it is a loop, not a line

The dashed feedback arrow is the whole point. Because ML systems **decay**
(Section 1.2), monitoring is not optional garnish — it is what keeps the system
alive. Fresh production data flows back, the model is retrained, and a new
version is deployed. A design answer that stops at "deploy the model" is
missing half the system.

> **Recurring mental model — the ML flywheel:** better product → more users →
> more data → better model → better product. We will reuse this picture in every
> recommender and search design.

![The data flywheel: a better product attracts more users, who generate more data, which trains a better model, which improves the product.](images/m01_05_flywheel.png)

### Worked mini-example (Netflix-style, concrete)

- **Business problem:** keep subscribers watching so they don't cancel.
- **ML problem:** rank the catalogue per user by "probability this title is
  watched to completion".
- **Data:** every play/pause/skip event, plus title metadata.
- **Features:** user's recent genres, time of day, title popularity, etc.
- **Train:** a ranking model on last 90 days of events.
- **Evaluate:** offline NDCG (a ranking metric, Module 7); then an online A/B
  test on real users.
- **Deploy:** precompute recommendations nightly (batch) + re-rank live.
- **Monitor:** watch click-through and watch-time; when they dip, retrain.

Every one of those steps is a later module. Module 1's job is to make you *see
the whole loop at once.*

---

## 1.4 Types of ML Systems

### Motivation

"Where and when does the prediction actually happen?" is one of the first
questions in any design. The answer drives your latency budget, cost, freshness,
and even privacy story. There is no single best choice — it is a **trade-off**.

![Four types of ML systems by where inference runs: batch (offline), online (real-time), streaming, and on-device/federated, with example use cases.](images/m01_04_types.png)

### The main types (by *how predictions are produced*)

| Type | How it works | Latency | Freshness | Best for | Example |
|------|--------------|---------|-----------|----------|---------|
| **Batch (offline)** | Predict for *all* entities on a schedule (e.g. nightly), store results in a DB, look them up later | None at request time (just a DB read) | Stale between runs | Predictions that don't need to be instant | Nightly "recommended for you" email |
| **Online (real-time)** | Compute a prediction *per request*, live, within a tight latency budget (ms) | Low (p99 budget) | Fresh (uses latest input) | User-facing decisions | Search ranking, ad CTR |
| **Streaming** | React to events as they arrive (Kafka/Flink), updating features/predictions continuously | Near real-time | Very fresh | Reacting to just-happened events | Fraud alerts, live personalization |
| **On-device (edge)** | Model runs on the phone/IoT device itself | Very low, offline-capable | Depends on model update cadence | Privacy, no network, low latency | Keyboard autocomplete, face unlock |
| **Federated** | Model trains *across* many devices without raw data leaving them | — | — | Privacy-sensitive training | Mobile keyboards learning across users |

### First-principles: how to choose

Ask three questions:

1. **How fresh must the prediction be?** If yesterday's answer is fine → batch is
   cheapest. If it must reflect what the user did *this second* → online or
   streaming.
2. **What is the latency budget?** A user waiting for search results tolerates
   ~100–300 ms; an email recommendation can be computed overnight.
3. **Where must the data live?** If it cannot leave the device (privacy, law) →
   on-device / federated.

> **Common real-world pattern — hybrid:** big systems mix modes. YouTube
> *precomputes* candidate videos in batch, then *re-ranks* them online per
> request. This gives cheap heavy lifting plus fresh final decisions. When an
> interviewer pushes on latency and cost, proposing a hybrid batch+online design
> is a strong senior move.

### Edge cases & failure modes

- **Batch that's too stale:** a fraud model run once a day misses attacks that
  happen in minutes. → wrong mode for the problem.
- **Online that's too slow:** a great model that takes 800 ms blows the latency
  budget and hurts the business metric more than a simpler fast model helps. →
  latency is a feature.
- **On-device that's too big:** a 2 GB model won't fit a phone; you must shrink
  it (quantization/distillation, Module 8).

---

## 1.5 ML System Design vs Classic System Design

### What overlaps (you still need all of this)

Everything from classic system design still applies to ML systems:
load balancing, caching, databases, message queues, replication, horizontal
scaling, APIs (REST/gRPC), SLAs/SLOs, and back-of-the-envelope capacity
estimation. These are covered in **Module 19** because you cannot design an ML
serving layer without them. An ML system *is* a distributed system that happens
to have models in it.

### What is new (the ML-specific layer)

On top of classic concerns, ML system design adds:

| Dimension | Classic system | ML system |
|-----------|----------------|-----------|
| **Logic source** | Code written by humans | Model learned from data |
| **Correctness** | Right or wrong | "Good enough" on a metric; probabilistic |
| **Testing** | Unit/integration tests | + data validation, offline metrics, A/B tests, monitoring |
| **Change over time** | Stable until code changes | Decays on its own (drift) |
| **Key artifacts** | Code, config | Code, config, **data, features, model versions** |
| **Debugging** | Read logs/stack traces | Inspect data distributions, features, and predictions |
| **Reproducibility** | Same input → same output | Must pin data + code + seeds to reproduce |

### The interview implication

An ML system design interview expects you to cover **both** layers:

- the **ML layer** (framing, data, features, model, metrics), and
- the **systems layer** (serving, scaling, latency, cost, reliability).

Candidates who only talk about model architecture, or only talk about
microservices, both fail. The bar is *connecting* the two: "we use a two-tower
model (ML choice) served with an approximate-nearest-neighbour index behind a
gRPC service with a 50 ms p99 budget (systems choice), because the business
needs fresh, personalized results at scale (business goal)."

---

## 1.6 Stakeholders, Requirements & the Cost of Being Wrong

### Who cares about an ML system (stakeholders)

An ML system is never built in a vacuum. Typical stakeholders:

- **Product / business:** wants a business metric to move (revenue, engagement,
  retention). Speaks in dollars and users, not AUC.
- **Users:** want a fast, useful, fair, private experience.
- **ML / data engineers:** build and maintain the pipelines and models.
- **SRE / platform:** care about latency, uptime, and cost.
- **Legal / privacy / risk:** care about compliance, bias, and safety.

Good design starts by asking *whom this serves and what "good" means to them* —
which is exactly the "clarify requirements" step of the framework in Module 2.

### Functional vs non-functional requirements

- **Functional:** *what* the system must do — "recommend 10 videos", "flag
  fraudulent transactions", "answer questions from our docs".
- **Non-functional:** the *qualities* it must have — latency (p99 < 100 ms),
  throughput (50k QPS), availability (99.9%), cost budget, freshness, privacy,
  fairness. In ML interviews, **the non-functional requirements usually drive the
  hardest design decisions** (they decide batch vs online, model size, caching,
  etc.).

### The cost of being wrong (this picks your metric)

Not all mistakes cost the same, and *where* a mistake lands decides how you
design. Reason about it as a 2×2:

![A 2x2 of mistake cost vs volume: low-stakes ship fast; high-stakes rare needs human review; high-stakes high-volume (fraud) demands caution.](images/m01_08_cost_of_wrong.png)

- **Low stakes (movie recommendation):** a bad rec is mildly annoying → optimise
  for engagement, ship fast, iterate.
- **High stakes, rare (loan approval):** a wrong decision has legal and human
  cost → keep a human in the loop, demand explainability (Module 18).
- **High volume, low stakes (autocomplete):** each error is tiny but there are
  billions → add cheap guardrails.
- **High stakes and high volume (payment fraud):** the scariest quadrant → tune
  precision/recall carefully, roll out slowly with shadow mode and kill
  switches (Module 10).

> **Senior signal:** asking "what does a false positive cost vs a false
> negative?" *before* choosing a metric is one of the clearest markers of a
> strong candidate. It shows you connect ML choices to business consequences.

---

## Module 1 — Interview Mapping (what companies probe)

| Company | How Module 1 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "Walk me through how you'd approach this ML problem" | Jumps to a model | Names the lifecycle, clarifies the business metric first, flags data + feedback loop |
| **Amazon** | Ties to Leadership Principles (Customer Obsession, Dive Deep) | Talks tech only | Starts from the customer/business impact and cost of errors |
| **OpenAI / Anthropic** | Framing + when NOT to use ML / when a simpler baseline wins | Over-engineers | Proposes a simple baseline first, justifies added complexity |
| **Uber / Stripe** | Batch vs streaming, cost of wrong (fraud/ETA) | Picks one mode | Weighs freshness vs latency vs cost, proposes a hybrid |

**The single most common opening question:** *"How would you design an ML system
for X?"* Your first 60 seconds should: (1) clarify the goal and constraints,
(2) decide whether ML is even the right tool, (3) sketch the lifecycle loop. That
structure alone separates you from most candidates. (Full framework in Module 2.)

---

## Module 1 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask *definitional* ML questions — supervised vs
  unsupervised, what an ML model is, ML vs traditional programming. Section 1.1
  covers this. ML *system design* itself is essentially **interview-only** and
  rarely appears on written exams.
- **GATE CS / DA:** the DA (Data Science & AI) paper covers ML foundations and
  the ML workflow; know the lifecycle stages and the supervised/unsupervised
  split. Deep system-design tradeoffs are not tested.
- **ISRO / DRDO:** occasional basic ML/AI definitions only.

> **Flag:** Modules that are *interview-only* (like the design framework and
> case studies) are clearly marked throughout the course. Foundations (this
> module), data, features, evaluation metrics, and systems foundations carry the
> most *exam* value.

---

## Module 1 — Common Mistakes & Misconceptions

1. **"An ML system = a model."** No. The model is a small part; data, features,
   serving, and monitoring are the bulk. (Section 1.2.)
2. **"Once deployed, it keeps working."** No — models decay due to drift. ML
   systems need continuous monitoring and retraining. (Sections 1.2, 1.3.)
3. **"More data / a bigger model is always the answer."** Often a simpler model
   with better features or a cleaner metric wins. Complexity has a cost.
4. **"ML is always the right tool."** Frequently a rule or heuristic is simpler,
   cheaper, and more reliable. Knowing when *not* to use ML is a senior signal.
5. **"Offline accuracy is what matters."** The *business/online* metric is what
   matters; offline and online often disagree (the offline–online gap, Module 7).
6. **"The lifecycle is a straight line."** It is a loop; monitoring feeds back
   into data and retraining.

---

## Module 1 — MCQs (with answers & explanations)

**Q1.** Which best describes the difference between Software 1.0 and Software 2.0?
a) 2.0 is written in a newer language
b) In 2.0, rules are *learned from data* rather than hand-written
c) 2.0 does not need data
d) 1.0 cannot run on servers

<details><summary>Answer</summary>**b.** In Software 2.0 (ML), a training
algorithm produces the rules (the model) from data + examples, instead of a
human writing explicit `if/else` logic.</details>

**Q2.** A model that was accurate at launch slowly gets worse over months even
though its code never changed. This is called:
a) a compile error  b) drift/decay  c) a cache miss  d) overfitting

<details><summary>Answer</summary>**b.** The world moves away from the training
data (concept/data drift), so accuracy decays. This is unique to ML systems and
is why monitoring + retraining exist (Module 10).</details>

**Q3.** Which is a *feedback loop* problem?
a) A load balancer routes to a dead server
b) A recommender only shows popular items, so it only collects data on popular
   items, reinforcing their popularity
c) A database index is missing
d) The API returns 500 errors

<details><summary>Answer</summary>**b.** The system's own predictions shape the
future training data. This is specific to ML systems and can amplify bias.</details>

**Q4.** You must flag fraudulent card transactions within milliseconds of them
happening. Which system type fits best?
a) Batch (nightly)  b) On-device only  c) Online / streaming  d) Federated

<details><summary>Answer</summary>**c.** Fraud must be caught as events happen,
so you need low-latency online/streaming inference. A nightly batch job is far
too stale.</details>

**Q5.** Which statement is a *senior* signal in an ML design interview?
a) "Let's use the biggest transformer available."
b) "There may be a simple rule that solves this without ML — let's check first."
c) "Accuracy is the only metric that matters."
d) "We'll deploy and we're done."

<details><summary>Answer</summary>**b.** Questioning whether ML is even needed
(and starting from a simple baseline) shows judgment about complexity and cost.</details>

**Q6.** In the "hidden technical debt" view of ML systems, the ML model code is:
a) the majority of the system
b) a small fraction surrounded by data + infra + monitoring
c) unnecessary
d) the same size as the serving layer

<details><summary>Answer</summary>**b.** Per Sculley et al. (2015), the model
code is a tiny box; most of the work is data collection, features, serving,
configuration, and monitoring.</details>

---

## Module 1 — Design Exercises (easy → hard)

- **Easy.** For each, say ML or plain rules, and why: (1) block emails from a
  specific address; (2) detect toxic comments; (3) compute a shopping cart
  total; (4) recommend songs. *(Rules for 1 and 3; ML for 2 and 4.)*
- **Medium.** Draw the seven-stage lifecycle for a food-delivery ETA predictor.
  For each stage, name one concrete thing that happens.
- **Medium.** A team's model was 92% accurate at launch and is 84% after six
  months, with no code changes. List three possible causes and how monitoring
  would catch each.
- **Hard.** You must recommend products on an e-commerce homepage. Decide
  batch vs online vs hybrid. State your latency budget, freshness need, and cost
  reasoning. What breaks if traffic grows 100×?
- **Hard.** Design the *feedback loop* for a job-recommendation site and identify
  one way it could become a harmful loop (bias amplification) and how you'd
  detect it.

---

## Module 1 — Concept Review (one page)

- **Software 1.0** = humans write rules; **2.0** = rules learned from data (the
  model). An **ML system** ⊃ the model (adds data, features, serving,
  monitoring, feedback).
- ML systems differ from normal software in four ways: **data dependencies,
  feedback loops, non-determinism ("good enough"), and decay (drift).**
- The **lifecycle** is a *loop* of 7 stages: problem → data → features → train →
  evaluate → deploy → monitor → (back to data).
- **Types:** batch (scheduled, cheap, stale) · online (per-request, low-latency,
  fresh) · streaming (event-driven) · on-device/federated (private, edge). Big
  systems go **hybrid**.
- ML design = **classic system design + an ML layer**. You must cover both, and
  *connect* ML choices to systems choices to the business metric.
- **Cost of being wrong** (false-positive vs false-negative cost) decides your
  metric, whether you keep a human in the loop, and how cautiously you roll out.
- **When NOT to use ML** (no pattern / no data / no tolerance for error / no
  metric) — saying this is a senior signal.

---

## Module 1 — Flash Cards (Q → A)

1. Software 2.0 in one line? → *Rules learned from data, not hand-written.*
2. Four ways ML systems differ? → *Data dependencies, feedback loops,
   non-determinism, decay.*
3. Why is the lifecycle a loop? → *Models decay; monitoring feeds fresh data back
   for retraining.*
4. Batch vs online in one line? → *Batch = predict everything on a schedule,
   cheap but stale; online = per-request, fresh, latency-bound.*
5. CACE principle? → *Changing Anything Changes Everything (data dependencies).*
6. Cheapest mode when yesterday's answer is fine? → *Batch.*
7. When NOT to use ML? → *No pattern, no data, no error tolerance, or no
   measurable success.*
8. What decides precision-vs-recall trade-off? → *The relative cost of a
   false positive vs a false negative.*

---

## Module 1 — Pattern Recognition (how to spot it in an interview)

- Hear **"How would you design an ML system for X?"** → open with clarify → is-ML-needed → lifecycle loop.
- Hear **"must be real-time / within X ms"** → think online/streaming and latency budget.
- Hear **"the model got worse over time"** → say *drift*, propose monitoring + retraining.
- Hear **"our recommendations keep pushing the same items"** → say *feedback loop / bias amplification.*
- Hear **"do we even need ML?"** → weigh pattern + data + error tolerance; propose a simple baseline first.
- Hear **"what could go wrong at 100× scale?"** → talk cost, latency tails, stale batch, and infra, not model math.

---

## Module 1 — Revision Notes / Mini Cheat Sheet

```
ML SYSTEM  =  MODEL + DATA + FEATURES + SERVING + MONITORING + FEEDBACK LOOP
SW 1.0: input + RULES        -> output      (humans write rules)
SW 2.0: input + OUTPUT(data) -> RULES/model (machine learns rules)

WHY ML IS HARD (4):  data-dependencies | feedback-loops | non-determinism | decay
USE ML ONLY IF:      a pattern exists + can't hand-write rules + you have data
                     + you can tolerate some error + you can measure success

LIFECYCLE (loop):    problem -> data -> features -> train -> eval -> deploy -> monitor -^

TYPES:  batch (sched, cheap, stale) | online (per-req, fresh, ms-budget)
        streaming (events) | on-device/federated (private, edge)   -> often HYBRID

DESIGN = classic-system-design (LB, cache, DB, queue, gRPC, SLO)  +  ML layer
COST OF WRONG:  FP-cost vs FN-cost  -> picks metric, human-in-loop, rollout caution
SENIOR SIGNALS: clarify first | question if ML is needed | start simple | connect
                ML choice <-> systems choice <-> business metric | plan the feedback loop
```

---

> **Next module:** *Module 2 — The ML System Design Interview Framework.* We turn
> the lifecycle loop into a repeatable **7-step framework** you can run on any
> design question in an interview, and we learn exactly how a junior, senior, and
> Staff answer differ at each step.
