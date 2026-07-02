---
title: "Module 7 — Model Evaluation"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — Model Evaluation

> **Why this module is the heart of ML.**
> Training a model is easy; *knowing whether it is any good* is the hard,
> senior part. Evaluation is where ML meets reality. Pick the wrong metric and
> you will happily ship a model that looks great on a slide and quietly loses
> the company money. Almost every famous ML failure — a fraud model that misses
> fraud, a recommender that recommends the same five items, a "99% accurate"
> cancer test that is useless — is really an *evaluation* failure: someone
> optimised the wrong number. This module teaches you to choose the right metric
> for the task, compute it by hand, read the curves, check calibration, split
> the data honestly, and finally prove your model works on *real users* with an
> A/B test. We build every metric from first principles and work a numeric
> example for each family.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★★     | ★★★    | ★★★★★      | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
draw a confusion matrix and derive accuracy, precision, recall, and F1 from it;
say *when precision matters more than recall* and why; read ROC and PR curves and
know which to use on imbalanced data; compute MAE / MSE / RMSE / MAPE / R² for a
regression; compute NDCG, MAP, MRR, and Precision@K for a ranking (a favourite
interview drill); name the right metric for NLP/LLM and CV tasks; explain why an
*accurate* model can be *mis-calibrated* and how to fix it; split data by **time**
to avoid leakage; and design an A/B test with a real notion of statistical
significance and guardrails.

> **How to read this module.** For every metric we go **what problem it solves →
> the formula → a worked number → when it lies to you.** Metrics are only useful
> when you know what they *hide*.

---

## 7.1 Why Evaluation Is the Whole Game

### Motivation (the problem that existed)

Suppose you build a model to detect a rare disease that affects 1 in 1000
people. You proudly report **99.9% accuracy**. Sounds amazing — until you notice
that a model which *always says "healthy"* also scores 99.9%, because 999 of
every 1000 people are healthy. Your model may have learned *nothing*. Accuracy
lied to you because the classes are **imbalanced**.

This is the central lesson of evaluation: **a metric is a lossy summary of
behaviour, and the wrong summary hides exactly the failure you care about.**
Choosing the metric is a design decision as important as choosing the model.

### Definition

- **Offline evaluation** = measuring quality on *held-out historical data*
  before deployment (accuracy, AUC, RMSE, NDCG…). Cheap, fast, repeatable, but a
  *proxy* for what you really want.
- **Online evaluation** = measuring the real business effect on *live users*
  (clicks, revenue, retention) via an A/B test. Expensive and slow, but it is
  the truth.

### Intuition & analogy

Offline metrics are like a *practice exam*: you can take them a hundred times,
they are cheap, and a high score is encouraging — but the practice exam is not
the real exam. Online metrics are the *real exam with real stakes*. Good students
use practice tests to decide what to study, then confirm on the real thing. Good
ML teams use offline metrics to decide **what to ship into an A/B test**, then let
the A/B test decide **what to launch**.

### First-principles: every metric answers one question

A metric exists to answer a specific question about a specific *kind of mistake*.
Before you pick one, finish this sentence: *"The mistake that costs us most is
\_\_\_\_."* If a false alarm costs most → precision. If a miss costs most →
recall. If being over-confident costs most → calibration/log-loss. If putting the
right item lower in the list costs most → a ranking metric. **The cost of being
wrong (Module 1) chooses your metric.**

---

## 7.2 Classification Metrics

### The confusion matrix — the source of everything

Every classification metric is just a ratio of four counts. Fix a **positive
class** (the thing you are trying to detect, e.g. "spam"), pick a decision
**threshold**, and count:

![The 2x2 confusion matrix: rows are the true label, columns are the prediction; TP and TN are correct, FP (false alarm) and FN (miss) are the two error types.](images/m07_01_confusion_matrix.png)

- **TP** (true positive): predicted positive, really positive — caught it.
- **FP** (false positive): predicted positive, really negative — false alarm.
- **FN** (false negative): predicted negative, really positive — a miss.
- **TN** (true negative): predicted negative, really negative — correct pass.

### The formulas (memorise these)

$$\text{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}\qquad
\text{Precision}=\frac{TP}{TP+FP}\qquad
\text{Recall}=\frac{TP}{TP+FN}$$

$$F_1=\frac{2\cdot P\cdot R}{P+R}\quad(\text{harmonic mean of precision and recall})$$

- **Precision** answers: *"of everything I flagged, how much was right?"*
- **Recall** (a.k.a. sensitivity, TPR) answers: *"of all real positives, how many
  did I catch?"*
- **F1** balances the two; use it when you need one number and classes are
  imbalanced. The *harmonic* mean punishes a low value harder than the plain
  average, so F1 is only high when *both* precision and recall are high.

### Worked example (do this by hand)

A spam filter is run on **1000 emails**: 100 are truly spam, 900 are ham. The
model produces:

| | Predicted spam | Predicted ham |
|---|:---:|:---:|
| **Actually spam** | TP = 80 | FN = 20 |
| **Actually ham**  | FP = 30 | TN = 870 |

- Accuracy $=(80+870)/1000 = \mathbf{0.95}$
- Precision $=80/(80+30)=80/110=\mathbf{0.727}$
- Recall $=80/(80+20)=80/100=\mathbf{0.80}$
- $F_1 = 2(0.727)(0.80)/(0.727+0.80)=\mathbf{0.762}$

Notice accuracy (0.95) looks great, but precision (0.73) reveals that ~1 in 4
emails we sent to the spam folder was actually a real email — which users hate.
**Accuracy hid the error that matters.**

### Log-loss (a.k.a. cross-entropy) — grading the *probabilities*

Accuracy/precision only look at the final yes/no. **Log-loss** grades the model's
*confidence*: it rewards being right *and confident*, and punishes being wrong
*and confident* very harshly.

$$\text{LogLoss}=-\frac{1}{N}\sum_{i}\big[y_i\log p_i+(1-y_i)\log(1-p_i)\big]$$

If the true label is 1 and you predict $p=0.9$, loss $=-\log 0.9=0.105$ (small).
If you predict $p=0.01$ for a true-1, loss $=-\log 0.01=4.6$ (huge). Lower is
better; a perfect confident model scores 0. Log-loss is the natural metric when
you care about the *probability itself* (see calibration, 7.8), not just the
label.

### ROC-AUC and PR-AUC — threshold-free scores

A single threshold gives one confusion matrix. If you sweep the threshold from
strict to lenient, you trace a *curve*. Two curves matter:

![Left: ROC curve plots TPR against FPR; the diagonal is a random model, higher-left is better. Right: PR curve plots precision against recall; the dashed line is class prevalence.](images/m07_03_roc_pr_curves.png)

- **ROC curve**: True Positive Rate (recall) vs False Positive Rate
  $(FP/(FP+TN))$. **ROC-AUC** = area under it = the probability that a random
  positive is scored higher than a random negative. 0.5 = random, 1.0 = perfect.
- **PR curve**: Precision vs Recall. **PR-AUC** (a.k.a. average precision)
  summarises it.

> **Key senior point:** on **imbalanced** data (rare positives — fraud, disease,
> click), use **PR-AUC, not ROC-AUC**. ROC-AUC can look flatteringly high because
> the huge number of true negatives keeps FPR tiny, hiding a terrible precision.
> PR-AUC's baseline is the positive prevalence, so it exposes the problem.

---

## 7.3 Precision vs Recall — Which Error Hurts More?

### The trade-off

Precision and recall pull against each other. Lower the threshold (flag more
things) → recall goes up, precision goes down. Raise it (flag fewer, only the
sure ones) → precision up, recall down. There is no free lunch; you pick the
operating point that matches the **cost of each error type.**

![Precision matters when a false alarm is costly (spam filter); recall matters when a miss is costly (cancer screening); F1 balances the two.](images/m07_02_precision_recall.png)

### First-principles rule

- **Optimise precision** when a **false positive is expensive**: junking a real
  email, blocking a legitimate transaction, a false fraud accusation.
- **Optimise recall** when a **false negative is expensive**: missing a cancer, a
  security threat, a critical safety fault. You would rather have a few false
  alarms than miss the real thing.
- Use **F1** (or Fβ, which weights recall β times as much as precision) when you
  need a single balanced number.

> **Interview line:** "Before I pick a metric I need to know the cost of a false
> positive vs a false negative — that decides precision vs recall." Saying this
> is a clear senior signal (ties back to Module 1's cost-of-being-wrong 2×2).

---

## 7.4 Regression Metrics

### Motivation

When the target is a number (price, ETA, demand) instead of a class, "correct"
no longer makes sense — every prediction has an **error** (residual)
$e_i = y_i-\hat y_i$. Regression metrics are different ways to summarise the size
of those residuals.

![A fitted line through scattered points; the red sticks are residuals (y minus prediction). MAE averages their size, MSE/RMSE square them, R-squared is the fraction of variance explained.](images/m07_05_regression_metrics.png)

### The formulas

$$\text{MAE}=\frac{1}{N}\sum|e_i|\qquad
\text{MSE}=\frac{1}{N}\sum e_i^2\qquad
\text{RMSE}=\sqrt{\text{MSE}}$$

$$\text{MAPE}=\frac{100\%}{N}\sum\left|\frac{e_i}{y_i}\right|\qquad
R^2=1-\frac{\sum e_i^2}{\sum (y_i-\bar y)^2}=1-\frac{SSE}{SST}$$

- **MAE** — mean absolute error. Same units as the target, easy to explain,
  **robust to outliers** (each error counts linearly).
- **MSE / RMSE** — square the errors, so **big errors are punished much more**.
  RMSE is in the target's units (interpretable); MSE is the thing you usually
  minimise mathematically.
- **MAPE** — percentage error, unit-free, good for comparing across scales — but
  **explodes when $y_i\approx 0$** and is asymmetric. Use with care.
- **R²** — fraction of the target's variance the model explains. 1 = perfect,
  0 = no better than predicting the mean, negative = worse than the mean.

### Worked example

Actuals $y=[3,5,2,8]$, predictions $\hat y=[2.5,5,4,7]$, so errors
$e=[0.5,0,-2,1]$.

- MAE $=(0.5+0+2+1)/4=3.5/4=\mathbf{0.875}$
- MSE $=(0.25+0+4+1)/4=5.25/4=\mathbf{1.3125}$
- RMSE $=\sqrt{1.3125}=\mathbf{1.146}$
- MAPE $=\tfrac{1}{4}(0.167+0+1.0+0.125)=0.323=\mathbf{32.3\%}$
- $R^2$: $\bar y=4.5$, $SST=(1.5^2+0.5^2+2.5^2+3.5^2)=21$, $SSE=5.25$, so
  $R^2=1-5.25/21=\mathbf{0.75}$.

RMSE (1.15) > MAE (0.875): the gap is the fingerprint of the one big error (−2).
When RMSE ≫ MAE, you have outliers.

---

## 7.5 Ranking & Recommender Metrics

### Motivation

Search and recommender systems do not output one label — they output an **ordered
list**. Getting the right items *near the top* matters far more than getting them
anywhere in the list. So we need **rank-aware** metrics that reward putting good
items high.

### The metric family (with @K = "look only at the top K")

- **Precision@K** = (relevant items in top K) / K. *"How clean is my top K?"*
- **Recall@K** = (relevant items in top K) / (all relevant items).
- **Hit Rate@K** = 1 if at least one relevant item is in the top K, else 0
  (averaged over users). *"Did we get anything useful up top?"*
- **MRR** (Mean Reciprocal Rank) = average of $1/(\text{rank of first relevant
  item})$. Great when there is essentially *one* right answer (e.g. "I'm feeling
  lucky", QA).
- **MAP** (Mean Average Precision) = mean over queries of *Average Precision* =
  average of Precision@k taken at each rank where a relevant item appears.
- **NDCG** (Normalised Discounted Cumulative Gain) = the gold standard, because it
  supports **graded** relevance (not just yes/no) and **discounts** lower ranks.

### NDCG — the worked example interviewers love

![Five ranked results with graded relevance; each gain is discounted by log2(1+rank); DCG divided by the ideal ordering IDCG gives NDCG in 0 to 1.](images/m07_06_ndcg.png)

Suppose the top 5 results have graded relevances (0–3): rank1=3, rank2=2,
rank3=3, rank4=0, rank5=1. Use the standard gain
$g_i=(2^{rel_i}-1)/\log_2(1+i)$:

$$DCG=\underbrace{\tfrac{7}{\log_2 2}}_{7.00}+\underbrace{\tfrac{3}{\log_2 3}}_{1.89}
+\underbrace{\tfrac{7}{\log_2 4}}_{3.50}+\underbrace{\tfrac{0}{\log_2 5}}_{0}
+\underbrace{\tfrac{1}{\log_2 6}}_{0.39}=12.78$$

The **ideal** order sorts relevances descending $[3,3,2,1,0]$:

$$IDCG=7.00+4.42+1.50+0.43+0=13.35\quad\Rightarrow\quad
NDCG=\frac{12.78}{13.35}=\mathbf{0.96}$$

For the same ranking, the binary metrics (treat rel > 0 as relevant; 4 relevant
items total): Precision@3 $=3/3=1.0$, Recall@3 $=3/4=0.75$, MRR $=1/1=1.0$,
Average Precision $=(1+1+1+0.8)/4=\mathbf{0.95}$, Hit Rate@3 $=1$.

> **Why NDCG wins:** it is the only one here that (a) uses *graded* relevance and
> (b) cares *how high* each good item sits. That is exactly what a search ranker
> optimises.

---

## 7.6 NLP / LLM Metrics

Text output has no single "correct" string, so we compare against references or
score fluency.

- **Exact Match (EM)** — 1 if the output string equals the reference exactly
  (after normalisation). Used for short factual answers (QA). Brutal but clear.
- **BLEU** (translation/generation) — **precision** of overlapping n-grams
  between output and reference(s), with a brevity penalty so you can't cheat by
  being too short. Higher = closer to the reference wording.
- **ROUGE** (summarisation) — **recall** of overlapping n-grams / longest common
  subsequence (ROUGE-N, ROUGE-L). *"How much of the reference did I cover?"*
- **Perplexity** — for language models, $\exp(\text{average log-loss per
  token})$. It measures how "surprised" the model is by real text; **lower is
  better.** It is an intrinsic metric (no references needed) but does not directly
  measure usefulness.
- **LLM-as-judge** — use a strong LLM to score or compare outputs against a
  rubric (helpfulness, correctness, harmlessness) or to pick the better of two
  (pairwise). Scales far cheaper than human raters, but beware biases (length
  bias, position bias, self-preference); calibrate against human labels.

> **Trade-off:** BLEU/ROUGE are cheap and reproducible but reward surface word
> overlap, not meaning — a perfect paraphrase can score low. Human eval and
> LLM-as-judge capture quality better but cost more and are harder to reproduce.

---

## 7.7 Computer-Vision Metrics

- **IoU** (Intersection over Union) — for detection/segmentation, the overlap
  between predicted and true regions:
  $\text{IoU}=\dfrac{\text{area of overlap}}{\text{area of union}}$. A prediction
  usually counts as correct if IoU ≥ 0.5.
- **mAP** (mean Average Precision) — the standard object-detection score: compute
  Average Precision (area under the precision–recall curve) at one or more IoU
  thresholds, then average over classes (and, in COCO, over IoU thresholds
  0.5–0.95). It rewards both **finding** objects (recall) and **not
  hallucinating** them (precision).

---

## 7.8 Calibration — Being Right About How Right You Are

### Motivation

Two models can have the *same accuracy* yet very different **probability
quality**. If your model says "0.7" for a batch of cases, do **70%** of them
actually turn out positive? If yes, it is **calibrated**; if not, the numbers are
misleading — dangerous when a downstream decision (loan pricing, medical triage,
expected-value bidding) *multiplies by the probability.*

![A reliability diagram: predicted probability on the x-axis, observed frequency on the y-axis; the green diagonal is perfect calibration, the red curve sags below it, showing an over-confident model.](images/m07_04_calibration.png)

### Reliability diagram (how to read it)

Bucket predictions (e.g. all cases predicted 0.6–0.7), then plot **mean predicted
probability (x)** vs **actual fraction positive (y)**. Perfect calibration lies on
the diagonal. A curve **below** the diagonal = **over-confident** (says 0.8 but
only 0.6 happen); **above** = under-confident. The **Expected Calibration Error
(ECE)** is the average gap across buckets.

### Fixes (post-hoc, on a validation set)

- **Platt scaling** — fit a small logistic regression $\sigma(a\cdot s + b)$ that
  maps the raw score $s$ to a calibrated probability. Simple, parametric, assumes
  a sigmoid shape; great with little data.
- **Isotonic regression** — fit a non-parametric, monotonic step function. More
  flexible (any monotonic shape) but needs more data and can overfit.

> **First-principles takeaway:** accuracy asks "is the label right?"; calibration
> asks "is the *probability* right?" Modern deep nets are often accurate but
> over-confident — always check calibration when the probability feeds a decision.

---

## 7.9 Splits, Cross-Validation, and Data Leakage

### The basic split

Divide data into **train** (fit the model), **validation** (tune hy-parameters /
choose the threshold), and **test** (a *one-time* honest estimate you never tune
on). If you tune on the test set, it stops being honest and you fool yourself.

### Cross-validation

With little data, a single split is noisy. **k-fold cross-validation** splits the
data into k parts, trains on k−1 and validates on the held-out part, rotating k
times, and averages. This uses all data for both roles and gives a variance
estimate — but it assumes rows are **exchangeable (i.i.d.)**, which breaks for
time series.

### Temporal splits — the production-correct way

![Temporal split: train on the past, validate, then test on the future along a time axis. A random split on time-series data lets future rows leak into training, giving a falsely high offline score.](images/m07_07_splits.png)

In production you always predict the **future** from the **past**. So your test
must imitate that: **train on older data, test on newer data.** A random shuffle
lets tomorrow's rows sit in the training set, which is **leakage** — the model
peeks at the future, scores brilliantly offline, and collapses live.

### Data leakage — the silent killer

**Leakage** = information that would not be available at prediction time sneaks
into the features (or the split). Classic examples:

- A feature computed *using the label* (e.g. "total refunds" when predicting
  fraud, if refunds happen after the fraud is known).
- Random-splitting time-series so future leaks into train.
- Normalising/imputing using statistics computed over the *whole* dataset
  (including test) before splitting.
- Duplicate rows appearing in both train and test.

Symptom: **offline metrics are suspiciously high but online performance is poor.**
(Cross-links to Module 1's training-serving skew and the offline–online gap.)

---

## 7.10 Online Evaluation — Proving It on Real Users

### Why offline is not enough

Offline metrics are computed on *past logged data*, which was collected under the
*old* model. A new model changes what users see, which changes their behaviour —
something no static dataset can capture. The only honest test is to run it live.

### A/B testing

![A/B test flow: split live traffic 50/50 into control (old model) and treatment (new model), compare guardrail and target metrics, then check whether the lift is statistically significant.](images/m07_08_ab_test.png)

Randomly assign users to **control** (A, current system) and **treatment** (B, new
system), keep everything else equal, run for a set period, and compare the
**target metric** (e.g. conversion). Randomisation is what lets you claim
*causation*, not just correlation.

### Statistical significance (don't ship noise)

Any two groups differ a little by luck. A **hypothesis test** asks: *if the two
systems were truly identical, how likely is a difference this big?* That
probability is the **p-value**; by convention $p<0.05$ is "statistically
significant." You must decide the **sample size in advance** — a bigger effect
needs fewer users, a smaller effect needs many more. Key pitfalls:

- **Peeking / early stopping** — checking daily and stopping the moment $p<0.05$
  massively inflates false positives. Fix the horizon (or use sequential tests).
- **Multiple comparisons** — test 20 metrics and one will look "significant" by
  chance; correct for it.

### Effects that fool A/B tests

- **Novelty effect** — users click a new feature just because it is new; the lift
  fades. Run long enough to see steady state.
- **Network effects** — one user's treatment leaks to control users (social
  feeds, marketplaces, ride pricing), breaking independence. Use cluster/geo
  randomisation.
- **Guardrail metrics** — metrics you must **not** harm even while chasing the
  target (latency, crash rate, revenue, complaints). A treatment that lifts clicks
  but doubles latency should **not** ship. Always watch guardrails.

### Cheaper / smarter online methods

- **Interleaving** — for ranking, blend results from A and B into one list per
  user and see which system's items get clicked. Far more sensitive than A/B, so
  it needs less traffic — but only compares rankers.
- **Multi-armed bandits** — instead of a fixed 50/50 split, *shift traffic toward
  the winning arm as evidence accumulates.* This reduces the cost of showing the
  worse variant ("regret") — good for many short-lived options (headlines,
  creatives), less so when you need a clean, static causal read.

---

## 7.11 The Offline–Online Gap (and How to Bridge It)

### The core problem

Your offline metric improves, you celebrate, you launch — and the business metric
does not move (or drops). This **offline–online gap** is one of the most cited ML
system-design topics.

![Offline metrics like AUC and NDCG often disagree with online metrics like clicks and revenue; bridge the gap by choosing an offline metric that tracks the goal, replaying on real traffic, and always confirming with an A/B test.](images/m07_09_offline_online_gap.png)

### Why the gap exists

- **Wrong proxy:** the offline metric (e.g. AUC) doesn't track the business goal
  (e.g. revenue).
- **Leakage / stale data:** offline scores are inflated (7.9).
- **Feedback loops:** logged data reflects the old model's choices, not user
  intent (Module 1).
- **Novelty / position effects** the offline set can't see.

### How to bridge it

1. **Pick an offline metric that correlates with the online goal** — validate the
   correlation historically before trusting it.
2. **Replay / shadow** the new model on real recent traffic to catch skew and
   engineering bugs before exposing users.
3. **Always confirm with an A/B test.** Offline decides *what to ship into the
   test*; online decides *what to launch.* Never let an offline win alone justify
   a launch.

---

## Module 7 — Interview Mapping (what companies probe)

| Company | How Module 7 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "What metric would you optimise for search / feed?" | "Accuracy" | Chooses NDCG/CTR, names guardrails, plans an A/B test |
| **Amazon** | Cost of false positive vs negative (Dive Deep) | Reports accuracy | Ties precision/recall to customer & dollar cost |
| **Stripe / Uber** | Fraud/ETA on imbalanced data | Uses ROC-AUC | Uses PR-AUC + recall at fixed precision, watches calibration |
| **OpenAI / Anthropic** | How to evaluate an LLM | "BLEU" | Mixes EM/ROUGE + human & LLM-as-judge, flags judge bias |
| **Netflix / Spotify** | Offline metric moved, online didn't | Confused | Explains the offline–online gap and how to bridge it |

**The most common trap question:** *"Your model is 99% accurate — ship it?"* The
right move is to ask about **class balance** and the **cost of each error**, then
propose precision/recall/PR-AUC instead of accuracy.

---

## Module 7 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **GATE CS / DA:** **very high value.** Confusion-matrix arithmetic
  (precision/recall/F1), ROC-AUC intuition, MSE/RMSE/R², and bias–variance are
  frequently tested and are *directly computable* — practice the numeric drills.
- **SEBI IT / RBI IT:** definitional and formula-based questions on
  precision/recall/accuracy and overfitting/regularisation appear; expect a
  confusion-matrix computation. Online A/B design is interview-only.
- **ISRO / DRDO:** occasional formula recall for accuracy/precision/recall.

> **Flag:** the *metric formulas and confusion-matrix computations* in 7.2–7.5
> carry the highest **exam** value in this whole course. The A/B testing and
> offline–online material (7.10–7.11) is mostly **interview** value.

---

## Module 7 — Common Mistakes & Misconceptions

1. **"High accuracy = good model."** Not on imbalanced data — a constant
   predictor can score 99%. Use precision/recall/PR-AUC. (7.1, 7.2.)
2. **"ROC-AUC is always the right classification metric."** For rare positives,
   PR-AUC is far more honest. (7.2.)
3. **"An accurate model has trustworthy probabilities."** No — accuracy ≠
   calibration. Check a reliability diagram. (7.8.)
4. **"Just shuffle and split randomly."** For time-series that causes leakage;
   split by **time.** (7.9.)
5. **"The offline metric went up, so we're done."** Confirm with an online A/B
   test; the two often disagree. (7.11.)
6. **"Stop the A/B test the moment p < 0.05."** Peeking inflates false positives;
   fix the sample size / horizon first. (7.10.)
7. **"F1 is the average of precision and recall."** It's the *harmonic* mean,
   which is dominated by the smaller of the two. (7.2.)

---

## Module 7 — MCQs (with answers & explanations)

**Q1.** A disease affects 1 in 1000 people. A model always predicts "healthy."
Its accuracy is:
a) ~50%  b) ~99.9%  c) 0%  d) undefined

<details><summary>Answer</summary>**b.** 999/1000 are healthy, so always-"healthy"
is 99.9% accurate yet useless — the classic imbalanced-data trap. Use
recall/PR-AUC instead.</details>

**Q2.** You must **not miss** a fraudulent transaction, even at the cost of some
false alarms. You should optimise:
a) precision  b) recall  c) specificity  d) accuracy

<details><summary>Answer</summary>**b.** A miss (false negative) is the expensive
error, so maximise recall (catch as many real frauds as possible).</details>

**Q3.** On a highly imbalanced dataset, which curve gives the more honest picture?
a) ROC  b) Precision–Recall  c) calibration  d) learning curve

<details><summary>Answer</summary>**b.** PR-AUC's baseline is the positive
prevalence, so it exposes poor precision that ROC-AUC hides behind the huge count
of true negatives.</details>

**Q4.** For actuals $[3,5,2,8]$ and predictions $[2.5,5,4,7]$, the RMSE is:
a) 0.875  b) 1.146  c) 1.3125  d) 0.75

<details><summary>Answer</summary>**b.** MSE $=5.25/4=1.3125$; RMSE
$=\sqrt{1.3125}=1.146$. (0.875 is the MAE, 0.75 is $R^2$.)</details>

**Q5.** NDCG is preferred over Precision@K for ranking because it:
a) is easier to compute
b) uses graded relevance and discounts lower ranks
c) needs no ground truth
d) ignores position

<details><summary>Answer</summary>**b.** NDCG rewards graded relevance and puts
more weight on higher ranks via a log discount, then normalises by the ideal
order.</details>

**Q6.** A model is 90% accurate, but when it says "0.9" only 60% of those cases
are positive. The problem is:
a) high variance  b) poor calibration  c) data leakage  d) low recall

<details><summary>Answer</summary>**b.** The labels are often right but the
*probabilities* are over-confident — a calibration problem. Fix with Platt
scaling or isotonic regression.</details>

**Q7.** You shuffle a year of daily sales randomly into train/test and get a great
$R^2$, but the live model is poor. Most likely cause:
a) underfitting  b) temporal data leakage  c) too few features  d) high bias

<details><summary>Answer</summary>**b.** Random shuffling let future rows leak into
training. Split by time (train on past, test on future).</details>

**Q8.** In an A/B test, checking results every hour and stopping as soon as
$p<0.05$ leads to:
a) faster valid results  b) inflated false-positive rate  c) higher recall  d) no effect

<details><summary>Answer</summary>**b.** Repeated peeking massively inflates the
false-positive (Type I error) rate. Fix the sample size/horizon in advance or use
sequential-testing methods.</details>

---

## Module 7 — Design Exercises (easy → hard)

- **Easy.** Given a confusion matrix (TP=40, FP=10, FN=20, TN=930), compute
  accuracy, precision, recall, and F1. Say which error type dominates.
- **Easy.** For a rare-event fraud model, state which single curve you'd report and
  why (PR vs ROC).
- **Medium.** You are ranking search results with graded relevance. Compute NDCG@5
  for the order [rel = 2, 3, 1, 0, 2] and state the ideal ordering.
- **Medium.** A credit model is 88% accurate but badly over-confident. Describe how
  you'd diagnose (reliability diagram, ECE) and fix (Platt vs isotonic) it, and why
  calibration matters for loan pricing.
- **Hard.** Design the full evaluation plan for a video recommender: pick offline
  metrics, a temporal split to avoid leakage, guardrail metrics, and an A/B test
  with a sample-size and significance plan. Explain the offline–online gap you
  expect and how you'll bridge it.
- **Hard.** Your marketplace A/B test shows a clear treatment lift, but you suspect
  network effects (sellers shared across arms). Redesign the experiment
  (cluster/geo randomisation) and justify it.

---

## Module 7 — Concept Review (one page)

- **Confusion matrix** (TP/FP/FN/TN) is the source of accuracy, precision, recall,
  F1. **Accuracy lies on imbalanced data.**
- **Precision** = clean flags (false-alarm cost); **Recall** = catch everything
  (miss cost); **F1** = harmonic balance. Cost of errors picks which.
- **ROC-AUC** vs **PR-AUC**: use **PR** when positives are rare. **Log-loss**
  grades probabilities.
- **Regression:** MAE (robust), MSE/RMSE (punish big errors, same units),
  MAPE (percent, breaks near 0), R² (variance explained).
- **Ranking:** Precision@K, Recall@K, MRR (first hit), MAP, and **NDCG** (graded +
  discounted, the gold standard). Hit Rate = got anything up top.
- **NLP/LLM:** EM, BLEU (precision of n-grams), ROUGE (recall), perplexity (lower =
  better), LLM-as-judge (cheap but biased). **CV:** IoU, mAP.
- **Calibration:** accuracy ≠ correct probabilities; read reliability diagram; fix
  with Platt / isotonic.
- **Splits:** train/val/test, k-fold, but **temporal split** for production;
  **leakage** = future/label info sneaks in → great offline, terrible live.
- **Online:** A/B test with randomisation, pre-set sample size, p < 0.05, watch
  **guardrails**; beware novelty & network effects; interleaving & bandits are
  cheaper. **Offline decides what to test; online decides what to launch.**

---

## Module 7 — Flash Cards (Q → A)

1. Precision vs recall in one line? → *Precision = of what I flagged how much was
   right; recall = of all real positives how many I caught.*
2. F1 is the ___ mean? → *Harmonic mean of precision and recall.*
3. When PR-AUC over ROC-AUC? → *When positives are rare (imbalanced data).*
4. RMSE vs MAE? → *RMSE squares errors so it punishes big ones and flags outliers;
   MAE is robust.*
5. What does R² = 0 mean? → *No better than predicting the mean.*
6. Why NDCG over Precision@K? → *Graded relevance + log discount for lower ranks.*
7. Accurate but wrong probabilities = ? → *Mis-calibration; fix with Platt /
   isotonic.*
8. Why temporal split? → *Production predicts the future from the past; random
   split leaks the future (leakage).*
9. What is a guardrail metric? → *A metric you must not harm (latency, revenue)
   while chasing the target.*
10. Offline vs online decision rule? → *Offline picks what to A/B test; online A/B
    picks what to launch.*

---

## Module 7 — Pattern Recognition (how to spot it in an interview)

- Hear **"the model is 99% accurate"** → ask about **class balance** and **cost of
  errors**; propose precision/recall/PR-AUC.
- Hear **"we must not miss any"** → **recall**; **"we must not false-alarm"** →
  **precision.**
- Hear **"rare event / fraud / disease"** → **PR-AUC, recall at fixed precision**,
  check calibration.
- Hear **"predict next month / future"** → **temporal split**, watch for
  **leakage.**
- Hear **"the probability feeds a decision (pricing/bidding)"** → talk
  **calibration.**
- Hear **"offline improved but the metric didn't move"** → **offline–online gap**,
  confirm with an **A/B test.**
- Hear **"how do you know it actually helped users"** → **A/B test**, significance,
  sample size, **guardrails.**

---

## Module 7 — Revision Notes / Mini Cheat Sheet

```
CONFUSION MATRIX -> everything
  Accuracy=(TP+TN)/all   Precision=TP/(TP+FP)   Recall=TP/(TP+FN)
  F1 = 2PR/(P+R) (harmonic)          Log-loss = grade the PROBABILITY
  ROC-AUC (balanced)  |  PR-AUC (RARE positives)  <- pick PR when imbalanced
PRECISION when FALSE ALARM costs ; RECALL when a MISS costs

REGRESSION:  MAE (robust) | MSE/RMSE (punish big, same units) | MAPE (% , dies near 0)
             R^2 = 1 - SSE/SST  (1 perfect, 0 = mean, <0 worse)

RANKING:  P@K , R@K , HitRate , MRR (first hit) , MAP , NDCG=DCG/IDCG (graded+discount)
NLP/LLM:  EM | BLEU (n-gram precision) | ROUGE (recall) | perplexity(low=good) | LLM-judge
CV:       IoU (overlap/union) | mAP (AP over classes & IoU)

CALIBRATION: accuracy != right probability ; reliability diagram + ECE ;
             fix = Platt (logistic) or Isotonic (monotonic steps)

SPLITS:  train / val / test(once) ; k-fold ; **TEMPORAL** for production
LEAKAGE: future/label info in features -> great offline, terrible live

ONLINE:  A/B (randomise, fix sample size, p<0.05, GUARDRAILS)
         traps: peeking, novelty, network effects ; interleaving & bandits = cheaper
BRIDGE OFFLINE->ONLINE:  correlated offline metric -> shadow/replay -> A/B test
  Offline decides what to TEST ; Online decides what to LAUNCH
```

---

> **Next module:** *Module 8 — Model Serving & Deployment.* Now that you can prove
> a model is good, we put it into production behind an API: batch vs online
> serving, latency/throughput budgets, model compression (quantization,
> distillation), shadow deployments, canaries, and rollbacks — the systems layer
> that carries your well-evaluated model to real users.
