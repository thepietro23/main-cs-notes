---
title: "Module 10 — Monitoring, Drift & Reliability"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10 — Monitoring, Drift & Reliability

> **Why this module matters.**
> Module 1 warned you that an ML system is never "done": it *decays* on its own,
> even when nobody touches the code. This module is where we finally deal with
> that decay head-on. Shipping a model is not the finish line — it is the moment
> the clock starts ticking. The world drifts away from your training data,
> fraudsters adapt, a product launch changes user behaviour overnight, and an
> upstream team quietly renames a column. Without monitoring you will not even
> *know* your model has quietly become worthless until the business metric falls
> off a cliff and someone escalates. This module teaches you what to watch, how
> to measure drift *with actual math*, how to retrain safely, and how to survive
> a production incident. This is the difference between "I trained a model" and
> "I run an ML system."

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★         | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
list the six things a mature ML system monitors and *why each one lags or leads*;
compute a **Population Stability Index (PSI)** by hand and read its thresholds;
explain **KL divergence** and the **Kolmogorov–Smirnov (KS)** test in plain
English; cleanly separate **data drift** from **concept drift**; pick between
**scheduled, triggered, and continual** retraining and defend the trade-off;
describe how a **feedback loop** can turn degenerate and how to break it; and lay
out a **safe rollout** (shadow → canary → rollback → kill switch) plus an
**incident runbook** you could actually follow at 3 a.m.

> **How to read this module.** As always: **problem → simplest attempt → why it
> breaks → the fix.** We connect every idea to how an interviewer probes it and
> to the earlier modules it builds on (especially the feedback loops and cost-of-
> being-wrong ideas from Module 1).

---

## 10.1 What to Monitor (the six signals)

### Motivation (the problem that existed)

You deployed a model on Monday. It was 92% accurate in the offline test. By
Friday, complaints are rolling in. What broke? You have *no idea*, because you
are not watching anything. The core problem: an ML system can fail **silently**.
A classic web service that breaks throws 500 errors and pages someone. A model
that breaks keeps returning perfectly well-formed predictions — they are just
*wrong now*. There is no stack trace for "the world changed."

So the first job is to decide **what to watch**. There are six signal families,
and they differ in one crucial way: **how quickly they tell you something is
wrong.** System health is instant; true model quality can lag for days or weeks
because you have to wait for the real labels ("did this flagged transaction turn
out to be fraud?").

![The monitoring stack drawn as five layers from system health at the bottom to the business metric at the top; lower layers are easy to detect and far from money, upper layers are hard to detect and close to money.](images/m10_01_monitoring_stack.png)

### The six things you monitor (and why)

1. **Data quality.** Before anything clever, check the *plumbing*: are features
   arriving at all? What fraction is null? Did a column's type change? Are values
   inside their expected range? Most "model" incidents are actually a broken data
   pipeline. This is the cheapest, highest-value monitor.
2. **Feature drift (input drift).** The distribution of an input feature moves
   away from what the model trained on (e.g. average user age shifts, a new
   country dominates traffic). Measured with PSI / KL / KS (Section 10.2).
3. **Prediction drift (output drift).** The distribution of the model's *outputs*
   changes — e.g. it suddenly predicts "fraud" on 8% of transactions instead of
   the usual 1%. You can watch this **immediately**, without waiting for labels,
   which makes it a valuable early warning.
4. **Model performance.** The real quality metric — accuracy, AUC, precision/
   recall, calibration (Module 7). This is what you ultimately care about, but it
   **lags** because it needs ground-truth labels that arrive late (or never).
5. **Business / product metric.** Revenue, engagement, click-through, cancellations.
   Closest to money, but the noisiest and slowest signal, and affected by many
   things other than your model.
6. **System health.** Classic ops: latency (p50/p99), error rate, throughput/QPS,
   and **saturation** (CPU, memory, GPU utilisation). Instant to detect and often
   the first sign that something changed.

> **Senior signal:** a strong candidate says *"I watch prediction drift and data
> quality first, because model performance lags until labels come back."*
> Recognising the **label-latency problem** — that you often cannot measure true
> accuracy in real time — is a Staff-level insight.

### First-principles: leading vs lagging indicators

Think of it like a doctor. System health and data quality are your **vital
signs** — checked continuously, instant to read. Model performance is a **blood
test** — the truth, but it takes time to come back. The business metric is your
**general health over the year** — what matters most, but the slowest and
noisiest to interpret. A good monitoring stack uses fast *leading* indicators
(drift, health) to raise the alarm *before* the slow *lagging* indicators
(accuracy, revenue) confirm the damage.

---

## 10.2 Detecting Drift with Math (PSI, KL, KS)

### Motivation

"The distribution changed" is a vibe, not a metric. To *alert* automatically you
need a **number** that says how far the live data has moved from the training
data, plus a **threshold** that decides when to act. Here we make it concrete.

![Data drift shown as two bell curves: the training (reference) distribution in blue on the left and the live traffic distribution in red-dashed shifted to the right, with an arrow marking the mean moving right.](images/m10_02_data_drift_curves.png)

The setup is always the same: you have a **reference** distribution (from
training) and a **current** distribution (from live traffic), and you want one
scalar measuring the gap.

### Population Stability Index (PSI) — the industry workhorse

PSI is the most common drift metric in industry (it comes from credit scoring).
You bin the feature into *k* buckets, and compare the **fraction** of data in
each bucket, expected (training) vs actual (live):

```
PSI = Σ  (actual_i − expected_i) · ln( actual_i / expected_i )
      i=1..k
```

Both the difference and the log ratio grow as a bucket's share changes, so PSI is
zero when the two distributions are identical and grows as they diverge.

**Worked example.** Split a feature into 5 equal buckets. At training each held
20% of the data. In live traffic the shares have shifted lower on the left and
higher on the right:

![A PSI worked example: five bins B1..B5, each with an expected (blue) bar at 20% and an actual (orange) bar at 10, 15, 20, 25, 30 percent; the summary line shows PSI is approximately 0.14, a moderate shift.](images/m10_03_psi_bins.png)

| Bin | Expected | Actual | (A−E) | ln(A/E) | contribution |
|-----|:--------:|:------:|:-----:|:-------:|:------------:|
| B1  | 0.20 | 0.10 | −0.10 | −0.693 | 0.0693 |
| B2  | 0.20 | 0.15 | −0.05 | −0.288 | 0.0144 |
| B3  | 0.20 | 0.20 |  0.00 |  0.000 | 0.0000 |
| B4  | 0.20 | 0.25 | +0.05 | +0.223 | 0.0112 |
| B5  | 0.20 | 0.30 | +0.10 | +0.405 | 0.0405 |
|     |      |      |       | **PSI** | **≈ 0.135** |

**Reading the number (memorise these thresholds):**

- **PSI < 0.10** → no significant shift; the population is stable.
- **0.10 ≤ PSI < 0.25** → moderate shift; investigate, keep watching.
- **PSI ≥ 0.25** → major shift; the model is likely degraded, retrain / act now.

Our 0.135 lands in the **moderate** band — a yellow light, not yet a fire.

### KL divergence — the information-theory cousin

**Kullback–Leibler (KL) divergence** measures how many extra bits you waste when
you use distribution *Q* (current) to describe data that actually came from *P*
(reference):

```
KL(P || Q) = Σ  P(i) · ln( P(i) / Q(i) )
             i
```

Plain English: **"how surprised is a model trained on P when it sees Q?"** Two
things to remember for interviews: (1) KL is **not symmetric** — `KL(P||Q) ≠
KL(Q||P)` — which is why PSI (which adds both directions of the difference) is
often preferred for a stable, symmetric-ish drift score; (2) KL **blows up** if
some bucket has zero probability in *Q* but not in *P*, so you must smooth
(add a tiny epsilon to every bin). PSI is essentially a symmetrised, binned
relative of KL, which is why it is the practical favourite.

### Kolmogorov–Smirnov (KS) test — no binning needed

The **KS test** compares two *continuous* distributions without choosing bins. It
looks at the **cumulative** distribution functions (CDFs) of the reference and
current samples and takes the **largest vertical gap** between them:

```
KS statistic  D = max | CDF_reference(x) − CDF_current(x) |
```

A big **D** means the two samples are far apart. The KS test also gives a
**p-value** (probability the gap is just noise); a small p-value says the drift is
statistically real. Use KS for numeric features where you do not want to argue
about bin edges; use PSI for a stable, business-friendly score with well-known
thresholds; use KL when you are reasoning in information-theory terms.

> **Interview quick-pick:** *categorical or business dashboard* → PSI; *continuous
> feature, want a significance test* → KS; *comparing probability distributions /
> model outputs* → KL (with smoothing). Saying which and **why** beats naming just
> one.

---

## 10.3 Data Drift vs Concept Drift (do not confuse these)

### Motivation

Both are "drift", both hurt accuracy, but they have **different causes and
different fixes**, and interviewers love to see if you can tell them apart. The
cleanest way to separate them is with the two probabilities `P(X)` (the inputs)
and `P(Y|X)` (how inputs map to the label).

![Data drift vs concept drift compared side by side: data drift means the inputs P(X) change while the input-to-label link P(Y|X) stays the same (example: new user region); concept drift means the meaning P(Y|X) itself changes so the same input now maps to a new label (example: fraud tactics change).](images/m10_04_data_vs_concept.png)

### Data drift (covariate shift): the inputs move, the rule holds

- **What changes:** `P(X)` — the distribution of the features. `P(Y|X)` — the
  true relationship between input and label — **stays the same**.
- **Example:** your fraud model was trained mostly on Indian traffic; you launch
  in Brazil. The *inputs* look different (currencies, device types), but "what
  makes a transaction fraudulent" hasn't changed. The model may still be roughly
  right, but it is now operating in regions of input space it saw little of.
- **Typical fix:** retrain / fine-tune on data that includes the new region;
  sometimes reweighting is enough because the underlying rule is intact.

### Concept drift: the rule itself changes

- **What changes:** `P(Y|X)` — the *meaning*. The **same input now maps to a
  different label.**
- **Example:** fraudsters invent a new attack. A transaction pattern that used to
  be perfectly safe is now fraud. The inputs may look statistically identical to
  before, yet your learned rule is simply **wrong** now.
- **Types:** *sudden* (a policy change overnight), *gradual* (tastes slowly
  shift), *seasonal/recurring* (holiday shopping), and *incremental*.
- **Typical fix:** you **must** get fresh labels and retrain — reweighting old
  data cannot help, because the correct answer itself has changed.

> **Why this distinction is load-bearing:** data drift is detectable *without*
> labels (just watch the input distributions). Concept drift often needs
> **labels** to detect, because the inputs can look unchanged while the correct
> answer flips — which is exactly why concept drift is the more dangerous and
> harder-to-catch of the two.

---

## 10.4 Retraining Strategies

### Motivation

Once monitoring tells you the model is drifting, *when and how often* do you
refit it? Retraining is not free — it costs compute, engineering time, and every
new model is a **risk** (it could be worse). There are three main strategies, and
the answer in a real design is usually a blend.

![Retraining strategies compared as three columns: scheduled (fixed cadence, simple but may retrain too often or too late), triggered (retrain on detected drift or performance drop, efficient but needs good monitors), and continual/online (update as each batch arrives, freshest but risk of instability and bad-data harm).](images/m10_05_retraining.png)

### The three strategies

1. **Scheduled (calendar-based).** Retrain on a fixed cadence — nightly, weekly,
   monthly. *Pros:* dead simple, predictable, easy to reason about. *Cons:* you
   may retrain when nothing changed (wasted compute) **or** too slowly to catch a
   sudden drift. Good default for stable domains.
2. **Triggered (event-based).** Retrain **only when a monitor fires** — PSI crosses
   0.25, accuracy drops below a floor, or prediction drift spikes. *Pros:* efficient,
   reacts to real change. *Cons:* only as good as your monitors and thresholds; a
   bad threshold means you retrain too late or thrash retraining on noise.
3. **Continual / online learning.** Update the model **incrementally** as each new
   batch (or even each event) arrives, so it is always fresh. *Pros:* maximal
   freshness, great for fast-moving domains (ads, fraud). *Cons:* the scariest to
   operate — a burst of bad or poisoned data can corrupt the model immediately,
   it is hard to reproduce/debug, and it can be unstable (catastrophic forgetting).

### The trade-offs (how to choose in an interview)

| Strategy | Freshness | Cost | Risk / stability | Best when |
|----------|-----------|------|------------------|-----------|
| Scheduled | Low–medium | Predictable | Low, easy to reason about | Domain drifts slowly |
| Triggered | Medium–high | Efficient (only when needed) | Depends on monitor quality | Drift is bursty / rare |
| Continual | Highest | Ongoing infra | Highest (bad data, instability) | Fast-moving, high-volume |

> **Golden rule for all three:** *never auto-promote a freshly retrained model.*
> Always validate it offline against a hold-out **and** roll it out safely
> (Section 10.6). A model that is "fresher" but *worse* is a downgrade. Automated
> retraining without automated *validation* is how teams silently ship regressions.

---

## 10.5 Feedback Loops and Their Dangers

### Motivation

Module 1 introduced feedback loops as one of the four things that make ML systems
uniquely hard: **the model's own predictions shape the data it will next learn
from.** Monitoring is where this bites, because a degenerate loop looks *great* on
your dashboards (engagement is up!) while quietly destroying the system's real
value. This is the most subtle failure mode in all of ML systems.

![A degenerate feedback loop drawn as four stages in a cycle: the model shows popular items, users click only what is shown to them, the logs then say popular equals good, and retraining favours popular items even more, closing the loop back to the start.](images/m10_06_feedback_loop.png)

### Degenerate loops (the vicious cycle)

A **degenerate feedback loop** is a self-reinforcing cycle where the model's
output biases its own future training data. The classic recommender example:

1. The model recommends **popular** items (it's least uncertain about them).
2. Users can only click **what they are shown**, so they click popular items.
3. The logs now "prove" popular items get the most clicks.
4. Retraining on those logs makes the model favour popular items **even more**.

The result: a rich-get-richer collapse in diversity. Niche items never get shown,
so they never get clicks, so they look "bad", so they never get shown. The model
is not learning what users *like* — it is learning what it *already showed them*.

### Bias amplification (cross-link to Module 1)

The same mechanism **amplifies bias and unfairness**. If a hiring or lending model
slightly under-shows opportunities to a group, that group generates less positive
signal, the next model under-shows them *more*, and the disparity compounds each
retraining cycle. This is precisely the "harmful loop" warned about in Module 1's
flywheel discussion — the flywheel can spin the wrong way. **Small initial biases
become large systematic ones through repeated feedback.**

### How to detect and break the loop

- **Exploration:** deliberately show some items the model is *unsure* about
  (epsilon-greedy / bandits) so you collect unbiased signal on the long tail.
- **Position / presentation debiasing:** log *where* an item was shown and correct
  for the fact that top-of-page items get clicked regardless of quality.
- **Randomised hold-outs:** keep a small slice of traffic served randomly (or by
  an old model) as an **unbiased mirror** to compare against — if the main system
  diverges from the hold-out, a loop is forming.
- **Monitor diversity / coverage**, not just engagement: a rising engagement
  number with a *falling* number of distinct items served is the tell-tale
  signature of a degenerate loop.

> **Senior signal:** naming the degenerate feedback loop *and* proposing an
> exploration or hold-out mechanism to break it is one of the strongest things you
> can say in a recommender or ranking design.

---

## 10.6 Safe Rollout: Shadow, Canary, Rollback, Kill Switch

### Motivation

Every new model — even a retrain of the current one — is a **bet** that it is
better. If you flip 100% of traffic to it and you are wrong, you have just harmed
every user and possibly the business. Reliable ML systems **never** do a hard
cutover. They roll out along a ladder that limits the blast radius at each step.

![A safe rollout ladder: shadow (new model runs but serves 0% of traffic, compared offline), then canary (serve to a small percentage, watch metrics), then ramp up (grow to 100% if metrics stay healthy), then full (new model is default); a red dashed arrow drops to a kill switch / rollback box that reverts to the last good model instantly on any red metric.](images/m10_07_rollout_safety.png)

### The rollout ladder

1. **Shadow mode (dark launch).** The new model runs on **real production
   traffic** but its predictions are **not served** to users — they are only
   logged and compared against the current model. This catches crashes, latency
   blowups, and wildly different outputs **with zero user risk**. Best first step
   for any risky model.
2. **Canary.** Serve the new model to a **small slice** of real traffic (say 1–5%),
   ideally with an A/B split, and watch the metrics closely. If the canary looks
   healthy, proceed; if not, you have only affected a tiny fraction of users.
3. **Ramp up.** Gradually increase the share (5% → 25% → 50% → 100%) as long as
   metrics stay healthy at each step. Each increase is another checkpoint.
4. **Full.** The new model becomes the default. Keep the **previous model warm**
   so you can revert instantly.

### Rollback and kill switches (the safety net)

- **Rollback:** revert to the last known-good model version. This is why you
  **version every model** and keep the previous one deployable — rollback must be
  *one click / one command*, not a re-deploy from scratch.
- **Kill switch:** a pre-wired way to **instantly disable** the model and fall
  back to a safe default (a simple heuristic, the old model, or "show nothing").
  For a high-stakes system (fraud, medical) a kill switch is mandatory, and it
  should be triggerable **automatically** by a monitor crossing a red line.

> **Cross-link:** this is the concrete answer to Module 1's "cost of being wrong"
> quadrant — the higher the stakes and volume (payment fraud), the more of this
> ladder you *must* use: shadow first, tiny canary, automatic kill switch.

---

## 10.7 Incident Response & Debugging ML in Production

### Motivation

Despite everything above, one day a monitor will page you: the model is broken in
production and users are affected. Panicking and "just retraining" is the wrong
move. There is a disciplined order of operations, borrowed from SRE and adapted
for ML.

![A production ML incident runbook drawn as five stacked stages: detect (an alert fires on a metric, drift, or errors), stabilise (rollback or kill switch first), triage (is it data, feature, model, or infra?), root cause (check drift, skew, upstream schema), and fix plus postmortem (patch, add a monitor, write it up).](images/m10_08_incident_runbook.png)

### The runbook (in order)

1. **Detect.** An alert fires — a metric dropped, PSI crossed a threshold, error
   rate spiked. Good alerts point at *which* signal moved.
2. **Stabilise first (stop the bleeding).** Before you diagnose anything,
   **roll back or hit the kill switch** to protect users. Diagnosis can take
   hours; users cannot wait. This is the single most important habit.
3. **Triage — which layer?** Localise the problem: **data** (a feed is null / a
   schema changed), **features** (training-serving skew, Module 5), **model**
   (a bad deploy, a drift-driven regression), or **infra** (a slow dependency, an
   OOM). Narrowing the layer is 80% of the fix.
4. **Root cause.** Now dig in: compare live feature distributions to training
   (drift?), check for **training-serving skew** (are features computed the same
   way live as in training?), look for an **upstream schema change**, inspect a
   sample of the worst predictions.
5. **Fix + postmortem.** Deploy the fix, then write a blameless postmortem — and,
   crucially, **add a monitor or test that would have caught it earlier.** Every
   incident should make the system harder to break the same way twice.

### The most common ML production bugs (know these cold)

- **Upstream data change** (a column renamed, units changed, a feed went stale) —
  the #1 cause, and often *no error* is thrown.
- **Training-serving skew** — features computed differently in the training
  pipeline vs the serving path (Module 5). Offline looked great; live is broken.
- **Silent drift** — no bug at all; the world simply moved (Sections 10.2–10.3).
- **Feedback-loop degeneration** — dashboards look fine but diversity/fairness is
  collapsing (Section 10.5).
- **A bad model got promoted** — retrained model was worse but auto-shipped
  because there was no validation gate (Section 10.4).

> **Senior signal:** *"Stabilise before you diagnose."* Junior engineers dive
> straight into root-causing while users keep getting hurt. Staff engineers roll
> back first, *then* investigate calmly.

---

## Module 10 — Interview Mapping (what companies probe)

| Company | How Module 10 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | "How do you know your model is still good in prod?" | "Check accuracy" | Names leading vs lagging signals, watches prediction drift + data quality first (labels lag) |
| **Amazon** | "How do you roll out a new model safely?" (Dive Deep) | "Deploy it" | Shadow → canary → ramp → kill switch; keeps previous model warm for one-click rollback |
| **Stripe / Uber** | Fraud/ETA drift; retraining cadence | "Retrain weekly" | Distinguishes data vs concept drift, triggered retraining on PSI, validation gate before promote |
| **Netflix / TikTok** | Recommender feedback loops | "More engagement is good" | Flags degenerate loop + bias amplification; adds exploration and randomised hold-out |
| **OpenAI / Anthropic** | Monitoring generative systems | Talks accuracy only | Discusses drift in inputs, guardrails, canary + kill switch for risky launches |

**The single most common opening question:** *"Your model was fine at launch and
is worse now — walk me through what you'd do."* A strong answer: (1) check
monitors to localise the layer, (2) roll back / kill-switch to stabilise, (3)
diagnose drift vs skew vs upstream data, (4) retrain **with a validation gate**,
(5) roll out safely. That five-beat structure signals real production experience.

---

## Module 10 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask *definitional* questions — what is model drift,
  why do ML models need monitoring, what is retraining. Sections 10.1 and 10.3
  cover the level expected. The full rollout/incident machinery is
  **interview-only** and rarely on written exams.
- **GATE CS / DA:** the DA paper can touch **concept drift** and the idea that
  model performance degrades over time; know data vs concept drift and that KL
  divergence measures the gap between two distributions. PSI/KS specifics are not
  usually tested but the *concept* of a distribution-distance metric can appear.
- **ISRO / DRDO:** occasional basic "why monitor ML models" definitions only.

> **Flag:** the *math* of drift (PSI/KL/KS) is far more of an **interview + job**
> skill than an exam topic. For written exams, focus on the definitions and the
> data-vs-concept-drift distinction.

---

## Module 10 — Common Mistakes & Misconceptions

1. **"Monitor accuracy and you're done."** Accuracy **lags** (labels arrive late
   or never). You must also watch *leading* signals — data quality, feature drift,
   and prediction drift — to get early warning. (Section 10.1.)
2. **"Data drift and concept drift are the same."** No. Data drift = inputs `P(X)`
   move, rule holds. Concept drift = the rule `P(Y|X)` itself changes. Different
   causes, different fixes. (Section 10.3.)
3. **"Higher engagement always means the model is better."** A degenerate feedback
   loop can raise engagement while collapsing diversity and amplifying bias.
   Watch coverage, not just engagement. (Section 10.5.)
4. **"Retrain more often = always better."** Fresher can be *worse*; every retrain
   is a risk. Always validate before promoting, and consider triggered vs
   scheduled. (Section 10.4.)
5. **"Just flip 100% traffic to the new model."** Never hard-cutover. Use shadow →
   canary → ramp, with rollback and a kill switch. (Section 10.6.)
6. **"During an incident, find the root cause first."** No — **stabilise first**
   (roll back), diagnose second. Users can't wait for your investigation.
   (Section 10.7.)
7. **"PSI and KL are symmetric measures."** KL is **not** symmetric and blows up on
   zero bins; PSI is the symmetrised, binned, business-friendly cousin. (Section 10.2.)

---

## Module 10 — MCQs (with answers & explanations)

**Q1.** Which signal gives you the *earliest* warning that something changed,
without waiting for ground-truth labels?
a) Model accuracy  b) Business revenue  c) Prediction / feature drift  d) F1 score

<details><summary>Answer</summary>**c.** Drift in inputs/outputs can be watched in
real time; accuracy, F1, and revenue all lag because they need labels or slow
business signal. This is the leading-vs-lagging insight from Section 10.1.</details>

**Q2.** A feature's PSI comes out at **0.31**. What does the standard threshold
guidance say?
a) Stable, ignore  b) Moderate, watch  c) Major shift, investigate/retrain now  d) PSI can't exceed 1

<details><summary>Answer</summary>**c.** PSI ≥ 0.25 indicates a major population
shift; the model is likely degraded and you should act. (<0.1 stable, 0.1–0.25
moderate.)</details>

**Q3.** Fraudsters invent a brand-new attack. Transactions that were safe last
month are now fraud, though the inputs look statistically similar. This is:
a) Data drift  b) Concept drift  c) Training-serving skew  d) A cache miss

<details><summary>Answer</summary>**b.** The mapping `P(Y|X)` changed — the same
input now maps to a different label. That is concept drift, and it needs fresh
labels + retraining. (Section 10.3.)</details>

**Q4.** What is the point of running a new model in **shadow mode**?
a) To serve it to all users faster
b) To run it on real traffic but serve 0%, comparing outputs at zero user risk
c) To reduce training cost
d) To delete the old model

<details><summary>Answer</summary>**b.** Shadow mode logs and compares the new
model on live traffic without exposing users, catching crashes/latency/wild
outputs safely before any canary. (Section 10.6.)</details>

**Q5.** A recommender's engagement is rising, but the number of distinct items
shown keeps falling and niche creators are vanishing. This is most likely:
a) A latency problem  b) A degenerate feedback loop  c) Data leakage  d) Underfitting

<details><summary>Answer</summary>**b.** The model reinforces what it already
showed, collapsing diversity and amplifying bias — a degenerate loop. Fix with
exploration and randomised hold-outs. (Section 10.5.)</details>

**Q6.** During a production incident where the model is clearly harming users,
what should you do **first**?
a) Start root-causing the data pipeline
b) Retrain the model
c) Roll back / hit the kill switch to stabilise
d) Write the postmortem

<details><summary>Answer</summary>**c.** Stabilise before you diagnose — protect
users first, investigate second. (Section 10.7.)</details>

**Q7.** Which statement about KL divergence is correct?
a) It is symmetric: KL(P‖Q) = KL(Q‖P)
b) It is always between 0 and 1
c) It is not symmetric and can blow up when a bin has zero probability
d) It requires ground-truth labels

<details><summary>Answer</summary>**c.** KL is asymmetric and undefined/infinite
for zero-probability bins (needs smoothing). This is why PSI, its symmetrised
binned cousin, is often preferred for drift dashboards. (Section 10.2.)</details>

---

## Module 10 — Design Exercises (easy → hard)

- **Easy.** For a batch churn model that scores users nightly, list the six
  monitoring signals and say which one you'd expect to detect a broken upstream
  feed *first*. *(Data quality — before any drift or accuracy signal.)*
- **Easy.** Given expected bin shares `[0.25, 0.25, 0.25, 0.25]` and actual
  `[0.25, 0.25, 0.25, 0.25]`, compute PSI and interpret it. *(PSI = 0 → perfectly
  stable.)*
- **Medium.** A model's inputs look unchanged (PSI ≈ 0.02 on every feature) yet
  accuracy has dropped 8 points. Data drift or concept drift? Justify, and say
  what you need to confirm it. *(Concept drift — need fresh labels.)*
- **Medium.** Design the retraining strategy for a payment-fraud model. Pick
  scheduled/triggered/continual, define your trigger thresholds, and describe the
  validation gate before promotion.
- **Hard.** A ranking model's engagement is up 3% but creator diversity is down
  20% over two months. Diagnose the loop, propose two mechanisms to break it, and
  a monitor to detect it earlier next time.
- **Hard.** Write the rollout plan for a new medical-triage model: shadow, canary
  %, ramp schedule, the exact metrics that trip the kill switch, and who gets
  paged. State why a hard cutover would be negligent here.

---

## Module 10 — Concept Review (one page)

- **Monitor six signals:** data quality · feature drift · prediction drift · model
  performance · business metric · system health. **Leading** (drift, health) warn
  early; **lagging** (accuracy, revenue) confirm late because **labels lag**.
- **Drift math:** **PSI** = Σ(actual−expected)·ln(actual/expected); thresholds
  **<0.1 stable / 0.1–0.25 moderate / ≥0.25 major**. **KL** = Σ P·ln(P/Q),
  asymmetric, blows up on zero bins. **KS** = max gap between CDFs, no binning.
- **Data drift** = inputs `P(X)` move, rule `P(Y|X)` holds (fix: retrain on new
  data). **Concept drift** = `P(Y|X)` itself changes (needs fresh labels).
- **Retraining:** scheduled (simple) · triggered (efficient, needs good monitors)
  · continual (freshest, riskiest). **Always validate before promoting.**
- **Feedback loops** can go **degenerate** — the model biases its own future data,
  collapsing diversity and amplifying bias. Break with **exploration + hold-outs**;
  watch coverage, not just engagement.
- **Safe rollout:** shadow → canary → ramp → full, with **rollback** (one click)
  and a **kill switch** (auto-tripped on red metrics).
- **Incident order:** detect → **stabilise (rollback) first** → triage the layer →
  root cause → fix + postmortem (add a monitor).

---

## Module 10 — Flash Cards (Q → A)

1. Why watch prediction drift before accuracy? → *Accuracy lags (labels arrive
   late); drift is a real-time leading indicator.*
2. PSI thresholds? → *<0.1 stable · 0.1–0.25 moderate · ≥0.25 major shift.*
3. PSI formula? → *Σ (actual − expected) · ln(actual / expected) over bins.*
4. Is KL divergence symmetric? → *No — KL(P‖Q) ≠ KL(Q‖P), and it blows up on zero
   bins.*
5. What does the KS test measure? → *The largest gap between two CDFs (no binning).*
6. Data drift vs concept drift? → *Data: inputs P(X) move, rule holds. Concept:
   the rule P(Y|X) itself changes.*
7. Three retraining strategies? → *Scheduled, triggered, continual/online.*
8. First step in a production ML incident? → *Stabilise (rollback / kill switch)
   before diagnosing.*
9. What is shadow mode? → *New model runs on real traffic but serves 0%; compared
   offline at zero user risk.*
10. Tell-tale sign of a degenerate feedback loop? → *Engagement up while diversity/
    coverage falls.*

---

## Module 10 — Pattern Recognition (how to spot it in an interview)

- Hear **"the model got worse over time / how do you know it's still good?"** → talk
  monitoring, leading vs lagging signals, drift detection.
- Hear **"the distribution changed"** → reach for **PSI / KL / KS** and thresholds.
- Hear **"inputs look the same but accuracy dropped"** → say **concept drift**, need
  fresh labels.
- Hear **"how often do you retrain?"** → scheduled vs triggered vs continual, and a
  **validation gate** before promotion.
- Hear **"engagement is up but..."** or **"recommendations keep narrowing"** → say
  **degenerate feedback loop / bias amplification**, propose exploration + hold-outs.
- Hear **"how do you deploy a new model safely?"** → shadow → canary → ramp →
  rollback → **kill switch**.
- Hear **"the model is broken in prod right now"** → **stabilise first**, then triage
  data/feature/model/infra.

---

## Module 10 — Revision Notes / Mini Cheat Sheet

```
WHAT TO MONITOR (6): data-quality | feature-drift | prediction-drift
                     | model-perf | business-metric | system-health
LEADING (fast): drift, health     LAGGING (slow, needs labels): accuracy, revenue

DRIFT MATH
  PSI = Σ (act - exp) * ln(act/exp)   ->  <0.1 stable | 0.1-0.25 moderate | >=0.25 MAJOR
  KL(P||Q) = Σ P * ln(P/Q)            ->  asymmetric; smooth zero bins
  KS = max | CDF_ref - CDF_now |      ->  no binning; gives p-value

DATA drift    : P(X) moves,  P(Y|X) holds   -> retrain on new data
CONCEPT drift : P(Y|X) CHANGES              -> need fresh labels, must retrain

RETRAIN: scheduled(simple) | triggered(efficient) | continual(freshest, riskiest)
         -> ALWAYS validate before promote (never auto-ship a worse model)

FEEDBACK LOOP: model biases its own future data -> diversity collapse + bias amp
         FIX: exploration + randomised hold-outs; watch COVERAGE not just engagement

SAFE ROLLOUT: shadow(0%) -> canary(1-5%) -> ramp -> full  + rollback + KILL SWITCH
INCIDENT:     detect -> STABILISE(rollback) FIRST -> triage layer -> root cause -> fix+monitor
TOP PROD BUGS: upstream data change | train-serving skew | silent drift | bad promote
```

---

> **Next module:** *Module 11 — Model Serving & Deployment.* We go from *watching*
> a live model to *serving* it well — REST vs gRPC, batching, caching, autoscaling,
> GPU vs CPU, and meeting a hard p99 latency budget at scale — the systems half of
> the ML/systems pairing we keep returning to.
