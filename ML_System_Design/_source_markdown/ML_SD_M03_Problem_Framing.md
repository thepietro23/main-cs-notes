---
title: "Module 3 — Problem Framing & Requirements"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — Problem Framing & Requirements

> **Why this module is the make-or-break step.**
> More ML projects die from *bad framing* than from bad models. A brilliant model
> that predicts the *wrong thing* is worthless; a mediocre model pointed at the
> *right* objective can transform a business. This module teaches the first, most
> important 30 minutes of any design: turning a fuzzy business wish
> ("make users happier", "reduce fraud") into a concrete, measurable ML problem —
> the right *task*, the right *label*, the right *objective* — and then sizing the
> system with back-of-the-envelope math before you write a single line of model
> code. Getting this right is the clearest Staff-level signal in an interview.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★         | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
take any vague business goal and translate it into a success metric, an ML
objective, and a concrete label; pick the correct ML *task* (classification /
regression / ranking / generation / retrieval / RL / anomaly detection) from the
*shape of the output*; recognise and avoid the three label traps (proxy labels,
label leakage, delayed labels); explain when a proxy metric silently fights the
true goal; and do **back-of-the-envelope capacity math** — DAU → QPS → peak QPS
and storage sizing — with real numbers, out loud, in an interview.

> **How to read this module.** As in Module 1, every idea follows **problem →
> simplest attempt → why it breaks → the fix**, in plain English, with a worked
> example and the interview angle attached.

---

## 3.1 Translating a Business Goal into an ML Objective

### Motivation (the problem that existed)

A product manager walks up and says: *"We want people to spend more time on the
app."* That sentence is **not** something a model can optimise. It has no label,
no unit, no data type. The single most common beginner mistake is to grab this
wish and immediately train a model on... what, exactly? Before any modelling,
you must **translate** the business goal down a ladder until you reach something
a model can actually predict.

### Definition

- **Business goal** — what the company ultimately wants (money, growth,
  retention, safety). Expressed in dollars and users, never in AUC.
- **Success metric** — a *measurable* number that stands in for the goal
  (watch-time per session, 30-day retention, fraud-loss in dollars).
- **ML objective** — the thing the model predicts, i.e. the **label** and the
  prediction it produces ("probability this video is watched to completion").
- **ML task** — the mathematical shape of that prediction (regression,
  classification, ranking, …).

![Translation ladder from business goal to success metric to ML objective (the label) to ML task, with a video-streaming example underneath each stage.](images/m03_01_business_to_ml.png)

### Intuition & analogy

Think of a doctor. The patient's goal is *"feel healthy"* — untreatable
directly. The doctor translates it into measurable proxies (blood pressure,
cholesterol, weight), then into an *intervention* (a specific drug dose) they can
actually control and measure. ML framing is the same descent: **goal → metric →
label → task.** You never operate on the goal; you operate on the label.

### First-principles derivation

A model is a function `f(features) → prediction`. To train it you need
`(features, label)` pairs. So the framing question is really:
*"What is the single quantity `y` such that (a) I can measure it from data, (b)
predicting it well moves the success metric, and (c) the success metric moves the
business goal?"* Every arrow in that chain is a place framing can go wrong.

### Worked examples (goal → metric → label → task)

| Business goal | Success metric | ML objective (label) | Task |
|---------------|----------------|----------------------|------|
| Increase engagement (video) | Watch-time / session | Predicted watch-time of a video for a user | Regression / ranking |
| Reduce fraud loss | $ fraud prevented | P(transaction is fraud) | Classification |
| Grow marketplace GMV | Completed purchases | P(user buys item) → rank | Ranking |
| Cut support cost | Tickets auto-resolved | Best help-article for a query | Retrieval |
| Faster deliveries | On-time rate | Predicted delivery ETA (minutes) | Regression |

> **Senior signal:** Say the whole chain out loud. "The business goal is
> retention; the success metric is 30-day return rate; but I can't train on that
> directly, so my ML objective is *predicted watch-time*, framed as a ranking
> task — and I'll validate the link with an A/B test." That sentence alone marks
> a strong candidate.

---

## 3.2 Choosing the ML Task

### Motivation

Once you have a label, you must pick the **task type** — and this decides your
model family, your loss function, and your evaluation metric. Beginners memorise
"it's classification" reflexively. The reliable trick is to look at the **shape
of the output** the system must produce.

![Decision fan: start from what the system OUTPUTS — a class label, a number, an ordering, a matching item, new content, or a rare event/action — and each maps to a task.](images/m03_02_task_decision.png)

### The tasks and when each fits

| Output shape | Task | When it fits | Example |
|--------------|------|--------------|---------|
| A category / class | **Classification** | Finite set of labels | Spam / not-spam, disease type |
| A continuous number | **Regression** | Real-valued target | ETA in minutes, house price |
| An *ordering* of items | **Ranking** | "Which items, in what order?" | Search results, news feed |
| A best match from a huge set | **Retrieval** | Millions of candidates, need top-k fast | Find similar products, RAG |
| Brand-new content | **Generation** | Output is text / image / audio | Chat reply, summarisation |
| Sequential decisions under reward | **Reinforcement learning** | Actions change future state | Ad bidding, robotics, game play |
| "Is this weird?" | **Anomaly detection** | Rare positives, few/no labels | Fraud, intrusion, machine faults |

### First-principles: why the output shape decides everything

The output shape fixes the **loss function**, which fixes the **model** and the
**metric**:

- A *class* → cross-entropy loss → metrics like precision/recall/AUC.
- A *number* → squared/absolute error → RMSE/MAE.
- An *ordering* → pairwise/listwise ranking loss → NDCG/MAP.
- *New content* → likelihood / token loss → perplexity + human eval.

So if you can name the output shape, the rest of the pipeline falls out almost
mechanically. This is why "start from the output" is such a powerful habit.

### Edge cases & re-framings (a Staff move)

The same business problem can often be framed as *different* tasks — and the
re-framing is where senior candidates shine:

- **Recommendation** can be classification (P(click) per item) *or* ranking
  (order all items) *or* retrieval (fetch top-k from millions). Real systems use
  retrieval **then** ranking (a two-stage funnel, Module 15).
- **Fraud** can be classification (labelled fraud) *or* anomaly detection (when
  labels are scarce).
- **"What should we show next?"** can be supervised ranking *or* an RL problem if
  today's choice changes tomorrow's data.

> **Interview tip:** When asked "how would you model X?", state the default task,
> then say "but if labels are scarce I'd frame it as anomaly detection" or "at
> this catalogue size I'd add a retrieval stage." Showing you can *re-frame* is
> the point.

---

## 3.3 When NOT to Use ML (reinforced)

### Motivation

Module 1 introduced this; framing is where it bites hardest. Having *just*
translated a goal into an ML objective, the disciplined next question is:
*"Do we actually need a model for this?"* Reaching for ML by default is a junior
reflex; questioning it is a senior one.

![Four red-flag conditions — a simple rule already works, too little or no labeled data, zero error tolerance with no human backup, cannot measure success — all pointing to: don't use ML, use rules or a heuristic.](images/m03_03_when_not_ml.png)

### The four red flags (any one → prefer rules)

1. **A simple rule already works.** "Block transactions over $10,000 from a new
   device" may catch 80% of the fraud with zero training. Ship the rule; revisit
   ML only for the remaining hard cases.
2. **Too little or no labeled data.** ML needs examples of the pattern. With a
   few dozen rows, a heuristic or a human beats any model.
3. **Zero error tolerance and no human backup.** If a single mistake is
   catastrophic and nobody reviews the output, a probabilistic model is the wrong
   tool.
4. **You cannot measure success.** No metric, no labels, no feedback → you can
   neither train nor tell if you improved. Fix measurement *first*.

### First-principles

ML buys you the ability to handle patterns too complex or numerous to hand-code.
That power costs you **data pipelines, training infra, monitoring, drift, and
non-determinism** (all of Modules 4–12). If a rule gets you 90% of the value at
1% of that cost, the rule wins. ML must *earn* its complexity.

> **Common mistake:** proposing a deep model for a problem a `WHERE amount >
> threshold` clause solves. Always offer the simplest baseline first; add ML only
> where the baseline demonstrably fails.

---

## 3.4 Defining the Label

### Motivation

The label `y` *is* the ground truth your model chases. If the label is subtly
wrong, the model faithfully learns the wrong thing — and no amount of tuning
fixes it. Label definition is where most real-world ML projects quietly fail.

![Three label failure modes as columns: proxy labels (stand-in for a hard-to-measure target), label leakage (a feature secretly contains the answer, giving fake offline accuracy), and delayed labels (the true label arrives weeks later).](images/m03_04_label_pitfalls.png)

### Trap 1 — Proxy labels

Often the true target is **hard or impossible to measure**, so you substitute a
*proxy* that is easy to log:

- True target: "did the user find this video satisfying?" → proxy: "did they
  watch > 80%?"
- True target: "is this a good hire?" → proxy: "did they stay 2 years?"

Proxies are usually necessary, but they are *approximations*. A watch-time proxy
rewards long, slow videos; a click proxy rewards clickbait. **Always name the gap
between the proxy and the true target**, and monitor it.

### Trap 2 — Label leakage (the silent killer)

Label leakage happens when a feature secretly contains information about the
label that **would not be available at prediction time**. The model looks
brilliant offline (99% accuracy!) and collapses in production.

![A time axis: at t = now we make the prediction using only data from t or earlier (OK feature, green); a leaky feature uses data from after now (t + 7 days, when the label is known). Fraud example: 'account_was_closed' is set only after fraud is confirmed.](images/m03_05_label_leakage.png)

**Concrete failure:** you build a fraud classifier and include the feature
`account_was_closed`. Offline AUC is 0.999 — amazing! But an account is only
*closed* **after** the fraud team confirms fraud. At real prediction time (when
the transaction happens) that field is always empty. You leaked the label. The
rule of thumb: **every feature must be computable using only data available at or
before the prediction timestamp.** (This is the temporal cutoff idea; see also
training-serving skew, Module 5.)

### Trap 3 — Delayed labels

Sometimes the true label simply **arrives late**:

- **Loan default:** you approve a loan today; whether it defaults is known in
  *months or years*.
- **Churn:** "did this user leave?" is only answerable after the churn window
  passes.
- **Ad conversion:** a purchase may happen days after the click.

Delayed labels create two problems: (1) you cannot train on recent data (its
labels aren't ready), and (2) your monitoring lags reality. Fixes include using
**shorter-horizon proxy labels** (early-payment behaviour predicts default),
**attribution windows**, and clearly documenting the label delay in the design.

> **Interview gold:** When you define a label, always ask three questions aloud —
> *"Is this a proxy, and for what? Could any feature leak it? When does the true
> label actually arrive?"* Nailing these three separates Staff answers from
> junior ones.

---

## 3.5 Objective Function Design & Business Alignment

### Motivation

Even with a clean label, you choose an **objective (loss) function** that the
model minimises. The danger: the thing you optimise (the proxy objective) can
**diverge from** the thing you actually care about (the true business goal). The
model is a ruthless optimiser — it will exploit any gap you leave.

![A chain showing optimizing CLICKS (a proxy) leads the model to serve CLICKBAIT, which drives clicks up but trust down, with a red dashed arrow showing this hurts the TRUE goal of long-term satisfaction.](images/m03_06_proxy_misalignment.png)

### The classic misalignment story

You optimise **click-through rate**. The model learns that the fastest way to get
clicks is **clickbait** and outrage. CTR goes *up* — your proxy objective is
winning! — but users lose trust, satisfaction drops, and long-term retention (the
*true* goal) falls. This is *proxy misalignment*, and it has burned every major
feed and recommender platform.

### First-principles: choosing the objective

1. **Name the true goal** (long-term satisfaction / retention / GMV).
2. **Pick a proxy objective you can train on** (click, watch-time, purchase).
3. **Measure the gap** between them, and design the objective to close it:
   - Combine signals (e.g. `0.3·click + 0.7·watch-time`) so no single hack wins.
   - Add **guardrail metrics** that must not regress (report rate, dwell, unsubscribe).
   - Penalise known bad behaviour (down-weight clickbait, add a diversity term).
4. **Validate with an A/B test on the true metric**, never the proxy alone.

### Worked example — objective vs guardrails

Designing a news feed:

- **Proxy objective:** predicted engagement (a blend of click + dwell + share).
- **Guardrail metrics (must not drop):** 7-day retention, "see less like this"
  rate, source diversity.
- **Why:** optimising engagement alone drifts to outrage; guardrails catch the
  drift before it ships.

> **Senior signal:** Explicitly separating the **optimisation objective** from the
> **guardrail metrics**, and tying both back to the true goal, is exactly what
> distinguishes a Staff-level framing answer.

### Trade-offs

| Choice | Pro | Con |
|--------|-----|-----|
| Single simple proxy (CTR) | Easy to train, clear signal | Easily gamed; misaligns with goal |
| Blended objective | Harder to game, closer to goal | More weights to tune, less interpretable |
| Guardrails only | Safety without over-constraining | Doesn't by itself improve the goal |

---

## 3.6 Capacity Estimation (Back-of-the-Envelope Math)

### Motivation

Before designing serving, you must know the **scale**: how many predictions per
second, how much storage, how big the model. Interviewers *expect* you to do this
math out loud with round numbers. It decides batch vs online, fleet size, caching,
and whether the model fits in RAM. This is a defining **Staff-level** skill.

### Worked example 1 — DAU → QPS → Peak QPS

![Four-box pipeline: 100M DAU, times 10 requests per user per day equals 1B requests/day, divided by 86,400 seconds equals about 11.6k QPS average, times a 3x peak factor equals about 35k QPS peak.](images/m03_07_qps_sizing.png)

Suppose a feed product has **100 M daily active users (DAU)**, and each user
triggers about **10 prediction requests/day** (scrolls, refreshes).

```
Requests/day = 100,000,000 users x 10 req/user = 1,000,000,000 = 1B req/day
Seconds/day  = 24 x 3600 = 86,400
Average QPS  = 1,000,000,000 / 86,400 ≈ 11,574  ≈ 11.6k QPS
Peak QPS     = average x peak_factor (2-4x) ≈ 11.6k x 3 ≈ 35k QPS
```

**Interpretation.** Traffic is not flat — evenings spike. Always size the fleet
for **peak**, not average. If one server handles ~1,000 QPS, you need
`35,000 / 1,000 = 35` servers just for the model, before redundancy (add ~30% for
headroom and failover → ~45 servers). If latency budget is 50 ms and each request
does one model call, that is easily met; if it fans out to 100 candidate scores,
recompute per-item throughput.

### Worked example 2 — Embedding table storage

![Four-box pipeline: 10M items, times 128 dims, times 4 bytes (float32) equals 5.12 GB; plus a second line, 50M users x 64 dims x 4 bytes = 12.8 GB.](images/m03_08_storage_sizing.png)

A recommender learns an **embedding vector** per item and per user. Storage is
just `rows x dimension x bytes-per-number`:

```
Item table:  10,000,000 items x 128 dims x 4 bytes (float32)
           = 10e6 x 128 x 4 = 5,120,000,000 bytes ≈ 5.12 GB

User table:  50,000,000 users x 64 dims x 4 bytes
           = 50e6 x 64 x 4 = 12,800,000,000 bytes ≈ 12.8 GB

Total embeddings ≈ 18 GB
```

**Interpretation.** 18 GB will *not* fit comfortably in a single serving process
alongside the rest of the model. Options: shard across a **parameter server**,
keep hot embeddings in RAM and cold ones on SSD, or **reduce precision** to
`float16`/`int8` (halving or quartering the size — 5.12 GB → 2.56 GB → 1.28 GB).
Cutting dimension from 128 to 64 also halves item storage. These are the levers a
Staff engineer reaches for.

### A reusable back-of-the-envelope kit

| Quantity | Formula | Handy numbers |
|----------|---------|---------------|
| Average QPS | requests/day ÷ 86,400 | 1B/day ≈ 11.6k QPS |
| Peak QPS | avg × peak factor | peak factor 2–4× |
| Servers needed | peak QPS ÷ per-server QPS | + ~30% headroom |
| Embedding storage | rows × dim × bytes | float32 = 4 B, fp16 = 2 B |
| Daily log volume | events/day × bytes/event | 1B × 1 KB = 1 TB/day |
| Model size (dense) | #params × bytes | 1B params × 2 B (fp16) = 2 GB |

> **Senior signal:** Round aggressively (86,400 → "~10⁵"), state assumptions
> ("assume 10 req/user/day, 3× peak"), and always convert the number into a
> **decision** ("so ~45 servers, and the table needs a param server"). Numbers
> without a decision are just trivia.

---

## Module 3 — Interview Mapping (what companies probe)

| Company | How Module 3 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "Design ranking for the feed" | Jumps to a model | Translates goal → metric → label; separates objective from guardrails; sizes QPS |
| **Amazon** | Ties to Customer Obsession & Dive Deep | Optimises a raw proxy | Names proxy-vs-true-goal gap; adds guardrail metrics |
| **Uber / Stripe / DoorDash** | ETA / fraud framing + scale | Picks a task, forgets scale | Chooses task from output shape, does QPS + storage math, flags delayed labels |
| **OpenAI / Anthropic** | When is ML the right tool; framing generation vs retrieval | Reaches for a big model | Questions if ML is needed; frames retrieval + generation two-stage |

**The single most common opening move:** before modelling, spend 3–5 minutes on
framing — restate the business goal, pick the success metric, define the label
(and its traps), name the task, and size the system. That structure alone
outperforms most candidates.

---

## Module 3 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask *definitional* items — supervised task types,
  what a label is, classification vs regression. Sections 3.2 and 3.4 cover this.
  Objective-design and capacity math are essentially **interview-only**.
- **GATE CS / DA:** knows classification vs regression, loss functions matched to
  task, and basic evaluation metric pairing. Section 3.2's task→loss→metric chain
  is directly relevant.
- **ISRO / DRDO:** occasional basic ML task-type definitions only.

> **Flag:** Capacity estimation and objective-alignment are high-value for
> **interviews and MLE roles**, low-value for written exams. Task types and label
> definitions carry the most *exam* value.

---

## Module 3 — Common Mistakes & Misconceptions

1. **Optimising the business goal directly.** You can't train on "engagement";
   translate it down to a label (Section 3.1).
2. **Picking the task by habit.** Let the *output shape* choose the task, and
   consider re-framing (Section 3.2).
3. **Including a leaky feature.** A feature computed using post-label information
   gives fake offline accuracy and fails live (Section 3.4).
4. **Forgetting the label delay.** Loan default / churn labels arrive late;
   design for it or use a shorter-horizon proxy (Section 3.4).
5. **Trusting a single proxy metric.** CTR-only optimisation breeds clickbait;
   add guardrails and validate on the true goal (Section 3.5).
6. **Skipping capacity math.** Not sizing QPS/storage means you can't justify
   batch vs online or fleet size (Section 3.6).
7. **Sizing for average, not peak.** Traffic spikes; provision for peak QPS.

---

## Module 3 — MCQs (with answers & explanations)

**Q1.** A PM says "increase watch-time". Which is the correct *ML objective*?
a) Watch-time itself
b) Predicted watch-time (or watch probability) of a video for a user
c) Daily active users
d) Server latency

<details><summary>Answer</summary>**b.** You can't train on the aggregate goal;
you predict a per-item label (predicted watch-time / completion probability) that,
when optimised, moves the success metric.</details>

**Q2.** You need to return the 20 most relevant products from a catalogue of 50
million. The most appropriate task is:
a) Regression  b) Binary classification  c) Retrieval (then ranking)  d) RL

<details><summary>Answer</summary>**c.** With millions of candidates you first
*retrieve* top-k cheaply, then *rank* them — the two-stage funnel. Scoring all 50M
per request with a classifier is infeasible.</details>

**Q3.** An offline fraud model scores AUC 0.999, but performs terribly in
production. The most likely cause is:
a) Too little regularisation  b) Label leakage  c) A slow database  d) Overfitting the learning rate

<details><summary>Answer</summary>**b.** A near-perfect offline score that
collapses live is the signature of leakage — a feature carried information only
available *after* the label (e.g. `account_was_closed`).</details>

**Q4.** "Did the user find the content satisfying?" is measured by "watched >
80%". The "watched > 80%" signal is a:
a) Guardrail metric  b) Proxy label  c) Leaky feature  d) Delayed label

<details><summary>Answer</summary>**b.** The true target (satisfaction) is hard to
measure, so completion is used as a *proxy label*. Name the gap and monitor it.</details>

**Q5.** A product has 200M DAU and 5 requests/user/day. Approximately what is the
*average* QPS?
a) ~1.2k  b) ~11.6k  c) ~35k  d) ~1M

<details><summary>Answer</summary>**b.** 200M × 5 = 1B req/day; 1B ÷ 86,400 ≈
11,574 ≈ 11.6k QPS average. (Peak would be ~35k at 3×.)</details>

**Q6.** You store embeddings for 20M items at 256 dims in float32. Approximate
table size?
a) ~0.5 GB  b) ~5 GB  c) ~20 GB  d) ~80 GB

<details><summary>Answer</summary>**c.** 20e6 × 256 × 4 bytes = 20.48e9 bytes ≈
20.5 GB. Consider fp16 or smaller dims if it must fit in RAM.</details>

**Q7.** Optimising click-through rate makes CTR rise but 7-day retention fall.
This is an example of:
a) Data drift  b) Proxy-objective misalignment  c) Label leakage  d) Cold start

<details><summary>Answer</summary>**b.** The proxy (clicks) diverges from the true
goal (retention). Fix with a blended objective plus guardrail metrics.</details>

**Q8.** Which situation most argues *against* using ML?
a) Millions of labelled examples exist
b) A single rule (`amount > 10000`) already catches most cases
c) The pattern is complex and changing
d) Some error is tolerable and there is a human reviewer

<details><summary>Answer</summary>**b.** If a simple, stable rule already solves it,
ML adds cost and risk without payoff. Ship the rule first.</details>

---

## Module 3 — Design Exercises (easy → hard)

- **Easy.** For each, name the ML task from the output shape: (1) predict tomorrow's
  temperature; (2) tag an email as spam/not; (3) order 100 search results;
  (4) generate a product description. *(Regression; classification; ranking;
  generation.)*
- **Easy.** For "reduce customer churn", write the full ladder: business goal →
  success metric → ML objective (label) → task. Note when the label arrives.
- **Medium.** You are building a loan-default model. Identify (a) one proxy label
  you could use for the *delayed* true label, and (b) two features that would leak
  the label. Explain why each leaks.
- **Medium.** A team optimises "time-on-app" and engagement rises but complaints
  spike. Redesign the objective: name one blended objective and two guardrail
  metrics.
- **Hard.** Size a search backend: 300M DAU, 8 queries/user/day, 4× peak factor,
  one server ≈ 2,000 QPS. Compute average QPS, peak QPS, and server count with
  30% headroom. State one decision the numbers drive.
- **Hard.** Design the label, objective, guardrails, and a QPS + embedding-storage
  estimate for a short-video recommender (say 500M items, 128-dim embeddings).
  Where would you put a retrieval stage and why?

---

## Module 3 — Concept Review (one page)

- **Framing ladder:** business goal → success metric → **ML objective (label)** →
  **ML task**. You optimise the label, never the goal directly.
- **Pick the task from the OUTPUT shape:** class → classification; number →
  regression; ordering → ranking; match from many → retrieval; new content →
  generation; sequential decisions → RL; rare/odd → anomaly detection. Be ready to
  **re-frame**.
- **When NOT to use ML:** simple rule works / no data / zero error tolerance & no
  human / cannot measure success.
- **Three label traps:** **proxy** (stand-in for a hard target), **leakage**
  (feature uses post-label info → fake offline win), **delayed** (true label
  arrives late).
- **Objective alignment:** the proxy objective can fight the true goal (CTR →
  clickbait). Use a **blended objective + guardrail metrics**, validate on the
  true metric via A/B.
- **Capacity math:** avg QPS = req/day ÷ 86,400; peak = avg × (2–4×); embeddings =
  rows × dim × bytes. Always size for **peak** and convert numbers into a
  **decision**.

---

## Module 3 — Flash Cards (Q → A)

1. Framing ladder in one line? → *goal → success metric → label → task.*
2. How do you pick the ML task? → *From the shape of the output.*
3. Retrieval vs ranking? → *Retrieval fetches top-k from millions; ranking orders
   the shortlist.*
4. What is a proxy label? → *An easy-to-log stand-in for a hard-to-measure true
   target.*
5. Signature of label leakage? → *Great offline metric, terrible in production.*
6. Leakage rule of thumb? → *Every feature must use only data available at/before
   the prediction time.*
7. Delayed-label example + fix? → *Loan default; use a shorter-horizon proxy.*
8. Proxy misalignment example? → *Optimise CTR → clickbait → trust/retention drop.*
9. Fix for proxy misalignment? → *Blended objective + guardrail metrics + A/B on
   the true goal.*
10. Average QPS formula? → *requests per day ÷ 86,400.*
11. Embedding table size? → *rows × dimension × bytes-per-number.*
12. Size the fleet for average or peak? → *Peak (avg × 2–4×), plus headroom.*

---

## Module 3 — Pattern Recognition (how to spot it in an interview)

- Hear **"increase engagement / revenue / retention"** → run the framing ladder;
  don't optimise the goal directly.
- Hear **"how would you model this?"** → name the task from the output shape, then
  offer a re-framing.
- Hear **"millions of items, return the best few"** → say *retrieval then ranking*.
- Hear **"the offline metric is amazing"** → suspect *label leakage*; check the
  temporal cutoff.
- Hear **"the label is not known for weeks"** → say *delayed labels*; propose a
  proxy horizon.
- Hear **"CTR went up but users are unhappy"** → say *proxy misalignment*; add
  guardrails.
- Hear **"how many servers / how much storage?"** → do QPS and rows×dim×bytes
  math out loud, size for peak.

---

## Module 3 — Revision Notes / Mini Cheat Sheet

```
FRAMING LADDER:  business goal -> success metric -> ML OBJECTIVE (label) -> ML TASK
                 (optimise the LABEL, never the goal directly)

PICK TASK BY OUTPUT SHAPE:
  class -> classification | number -> regression | ordering -> ranking
  match-from-many -> retrieval | new content -> generation
  sequential decisions -> RL | rare/odd -> anomaly detection
  (recsys = RETRIEVAL then RANKING; re-frame when labels are scarce)

WHEN NOT TO USE ML:  simple rule works | no data | zero error tolerance & no human
                     | cannot measure success

LABEL TRAPS:  PROXY (stand-in) | LEAKAGE (uses post-label info) | DELAYED (late label)
  leakage rule: every feature uses ONLY data available at/before prediction time

OBJECTIVE ALIGNMENT:  proxy objective can fight the true goal (CTR -> clickbait)
                      fix = blended objective + GUARDRAIL metrics + A/B on true goal

CAPACITY MATH:
  avg QPS   = requests/day / 86,400            (1B/day ~ 11.6k QPS)
  peak QPS  = avg x 2..4                        (size the fleet for PEAK)
  servers   = peak QPS / per-server QPS  (+30% headroom)
  embeddings= rows x dim x bytes    (fp32=4B, fp16=2B, int8=1B)
  ALWAYS turn the number into a DECISION.
```

---

> **Next module:** *Module 4 — Data: Collection, Labelling & Versioning.* Now that
> we have framed the problem and defined the label, we go get the data — how to
> collect it, label it (manually, weakly, or programmatically), split it without
> leakage, and version it so training is reproducible. Data is where most of the
> real ML work lives.
