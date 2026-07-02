---
title: "Module 5 — Feature Engineering & Feature Stores"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — Feature Engineering & Feature Stores

> **Why this module matters so much.**
> A model is only as good as the numbers you feed it. You can pick the fanciest
> architecture in the world, but if the *features* are noisy, leak the future, or
> are computed one way in training and a different way in production, the whole
> system quietly fails. In fact, most real-world accuracy gains at mature
> companies come not from a new model but from **better features**. This module
> teaches you how to turn raw, messy data into clean signals a model can learn
> from — and, just as important, how to *keep those signals consistent* between
> training and serving. That last problem, **training-serving skew**, is the
> single most common way production ML breaks. We first met the phrase in
> Module 1 (the trap table); here we finally take it apart and fix it with a
> **feature store**.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
name the six feature types and give an example of each; encode a categorical
variable four different ways (one-hot, hashing, target/mean, bucketization) and
say *when* each is right; explain *why* scaling matters for linear/NN models but
not for trees; explain what an embedding is and *why* dense beats sparse; build
a feature cross and say what interaction it captures; **diagnose and fix
training-serving skew**; and explain what a feature store gives you —
online/offline stores, **point-in-time correctness**, freshness, and backfills —
well enough to draw it on a whiteboard.

> **How to read this module.** As always: **problem → simplest attempt → why it
> breaks → the fix**. Features are where theory meets grimy reality, so we lean
> hard on concrete worked examples.

---

## 5.1 The Six Types of Features

### Motivation (the problem that existed)

Raw data almost never arrives as clean numbers. It arrives as a user's country,
a product review in English, a JPEG, a timestamp, a click log. But a model —
whether linear regression or a deep network — can only do arithmetic. It
multiplies numbers by weights and adds them up. So the very first job of feature
engineering is a translation problem: **turn every raw signal into a number (or
a vector of numbers) without throwing away the information that matters.**

### Definition

A **feature** is a measurable input signal derived from raw data and presented
to the model as a number or vector. Features fall into six common families:

![Six kinds of features: numerical, categorical, text, image, temporal, and cross features. Every raw signal must become a number before a model can use it.](images/m05_01_feature_types.png)

- **Numerical** — already a number: age, price, temperature. May still need
  scaling or bucketization.
- **Categorical** — a label from a fixed set: country, colour, device type.
  Needs *encoding* (Section 5.2).
- **Text** — free words: reviews, search queries, titles. Turned into numbers by
  bag-of-words, TF-IDF, or embeddings.
- **Image / audio** — pixels or waveforms, usually turned into a vector by a
  pretrained network (Module 6).
- **Temporal** — anything time-related: hour of day, day of week,
  time-since-last-purchase. Cyclic features (hour) often need special treatment.
- **Cross / interaction** — a *new* feature built by combining two others
  (Section 5.5), e.g. `city × hour`.

### Intuition & analogy

Think of a model as a chef who can only taste one thing: *saltiness on a scale
of 0–10*. To cook with anything — tomatoes, basil, lemon — you must first
translate each ingredient into that one scale the chef understands. Feature
engineering is that translation. Do it well and even a simple chef makes a great
dish; do it badly and no amount of talent saves the meal.

### First-principles: why "just feed the raw data" fails

You could imagine handing raw JSON straight to the model. Two problems: (1) the
model literally cannot multiply the string `"India"` by a weight, and (2) even
where a number exists, its *shape* may mislead — a raw user-id like `51204` is a
number, but adding "1" to it is meaningless. So we must deliberately choose a
representation that (a) is numeric and (b) reflects the real relationships in the
data. That deliberate choice is the whole discipline.

---

## 5.2 Encoding Categorical Features

### Motivation

Categoricals are everywhere and they are the trickiest to get right. `country`
might have 200 values; `product_id` might have 50 million. How you turn those
labels into numbers hugely affects both accuracy and memory. There are four
workhorse techniques.

### Technique 1 — One-hot encoding

Give each possible value its own column; set the column for the present value to
1 and all others to 0. `colour ∈ {red, green, blue}` becomes:

```
red   -> [1, 0, 0]
green -> [0, 1, 0]
blue  -> [0, 0, 1]
```

- **Math:** a value from a set of size *V* becomes a *V*-dimensional vector with
  a single 1. No false ordering is implied (unlike naively mapping red=1,
  green=2, blue=3, which wrongly tells the model green is "between" red and
  blue).
- **When to use:** small, stable vocabularies (say *V* ≤ a few hundred).
- **Breaks when:** *V* is huge (millions of ids) — the vector is enormous and
  mostly zeros, wasting memory and slowing training.

### Technique 2 — The hashing trick

Instead of a column per value, push every value through a hash function and take
the result modulo a fixed number of buckets *K*:

```
bucket(x) = hash(x) mod K          # K is fixed, e.g. 2^20
```

![One-hot encoding gives one slot per known value (exact but explodes for millions of values); the hashing trick squashes any value into K fixed buckets (fixed memory, no vocabulary, rare collisions).](images/m05_02_onehot_hashing.png)

- **Math:** any value — even one never seen before — maps into `[0, K)`. Vector
  size is fixed at *K*, independent of how many distinct values exist.
- **When to use:** very high-cardinality or *open* vocabularies (user ids, URLs,
  n-grams) where you cannot pre-list every value, and where a fixed memory
  budget matters.
- **Cost:** **collisions** — two different values may land in the same bucket and
  become indistinguishable. Bigger *K* means fewer collisions. In practice
  collisions are rare enough that the memory savings win.

### Technique 3 — Target (mean) encoding

Replace each category with a statistic of the *target* for that category —
usually the mean label:

```
encode(category c) = average target y over all rows where category = c
```

Example: for `city`, replace "Mumbai" with the historical fraud rate of Mumbai
transactions (say 0.03). Now one strong number carries predictive signal.

- **When to use:** high-cardinality categoricals with real signal, especially for
  tree models where one-hot would create thousands of sparse columns.
- **Danger — leakage:** if you compute the mean using the *same rows* you train
  on, the row's own label leaks into its feature. **Fix:** compute the encoding
  on a *separate fold* (out-of-fold / K-fold target encoding) or add smoothing
  toward the global mean for rare categories. This is a classic interview trap.

### Technique 4 — Bucketization (binning)

Turn a *numerical* feature into a *categorical* one by cutting it into ranges:

```
age -> {0-17, 18-25, 26-40, 41-65, 65+}
```

- **Why:** relationships are often non-linear. Income's effect on default risk is
  not a straight line; bucketing lets a linear model assign a separate weight per
  band. Buckets also tame outliers.
- **When to use:** non-linear effects, or to enable feature crosses (Section 5.5)
  on continuous variables. Choose bucket edges by quantiles (equal counts) or by
  domain knowledge.

### Trade-off summary

| Technique | Vector size | Handles unseen values? | Main risk | Best for |
|-----------|-------------|:----------------------:|-----------|----------|
| One-hot | *V* (grows) | No | Explodes when *V* large | Small stable vocab |
| Hashing | *K* (fixed) | Yes | Collisions | Huge / open vocab |
| Target/mean | 1 | Yes (via smoothing) | **Leakage** | High-card. with signal |
| Bucketization | #buckets | Yes | Info loss at edges | Non-linear numerics |

---

## 5.3 Normalization & Standardization

### Motivation

Suppose two features: `age` (0–100) and `income` (0–1,000,000). To a distance- or
gradient-based model, income *looks* a thousand times more important purely
because its numbers are bigger — even if age matters more. Scaling removes that
accident of units.

### Definition

- **Normalization (min-max):** rescale to a fixed range, usually [0, 1].
  `x' = (x − min) / (max − min)`.
- **Standardization (z-score):** center to mean 0, scale to standard deviation 1.
  `x' = (x − μ) / σ`.

### First-principles: why it matters for some models and not others

![Scale-sensitive models (linear/logistic regression, SVM/KNN using distances, neural networks using gradient descent) must have features scaled; scale-invariant models (decision trees, random forest, gradient-boosted trees) split on order, so scale is irrelevant.](images/m05_03_normalization.png)

- **Distance-based models (KNN, SVM, K-means):** they compute distances like
  `(a − b)²`. A feature with a huge range dominates the distance, drowning out
  others. Scaling puts every feature on equal footing.
- **Gradient-descent models (linear/logistic regression, neural nets):** with
  wildly different scales the loss surface becomes a long thin valley; gradients
  zig-zag and training is slow or unstable. Scaled inputs give a rounder bowl and
  faster, more stable convergence.
- **Tree-based models (decision trees, random forests, gradient-boosted trees):**
  a tree splits on *"is x > threshold?"*. That decision depends only on the
  **order** of values, not their magnitude. Scaling every value the same way does
  not change the order, so it does not change the tree at all. **This is why you
  do not need to scale features for XGBoost/LightGBM** — a favourite interview
  fact.

> **Watch the fit-on-train rule:** compute μ, σ (or min/max) on the **training
> set only**, then apply those same numbers to validation, test, and serving. If
> you fit the scaler on the whole dataset you leak test-set statistics into
> training — a subtle form of leakage (Module 7).

---

## 5.4 Embeddings — Dense Beats Sparse

### Motivation

One-hot encoding a `movie_id` with 1,000,000 possible values gives a
million-dimensional vector that is all zeros except one. It is huge, wasteful,
and — worse — it says every movie is equally unrelated to every other movie. The
one-hot vectors for "Toy Story" and "Toy Story 2" are just as far apart as "Toy
Story" and a horror film. There is **no notion of similarity**.

### Definition

An **embedding** maps each discrete value (an id, a word, a category) to a short,
**dense** vector of real numbers that is **learned** during training:

```
movie_id 51,204  ->  [0.31, -0.82, 0.10, 0.57]   (e.g. 4 to 256 dims)
```

![An embedding maps a movie id to a short learned dense vector instead of a giant sparse one-hot; similar items end up with nearby vectors, so the model generalises.](images/m05_04_embeddings.png)

### Intuition & why they generalise

During training the model nudges these vectors so that **items used in similar
ways end up near each other**. "Toy Story" and "Toy Story 2" drift close
together because the same users watch both. Now the model can *transfer* what it
learned about one to the other — it **generalises** across ids instead of
treating each as an isolated island. Dense vectors also cost far less memory: 256
floats instead of a million-slot one-hot.

### Three flavours you should name

- **Learned (task-specific) embeddings** — trained from scratch as part of your
  model. Best when you have lots of data for *your* task.
- **Pretrained embeddings** — reuse vectors trained elsewhere on a huge corpus
  (word embeddings like word2vec/GloVe, or text/image encoders). Great when your
  own labelled data is small; you inherit knowledge for free.
- **Entity embeddings** — the same idea applied to *any* high-cardinality
  categorical (user id, store id, zip code) in tabular models. Often beat one-hot
  on structured data.

### Worked example

A recommender embeds each user and each item into the same 64-dim space. To
score how much user *u* likes item *i*, take the **dot product** of their
vectors. Big dot product = predicted match. Because the space is shared and
dense, a brand-new item that is similar to popular items lands near them and gets
sensible recommendations immediately. (This "two-tower" pattern returns in the
recommender module.)

---

## 5.5 Feature Crosses & Interaction Features

### Motivation

A linear model treats each feature independently: it learns "Saturdays are
slightly busy" and "8 pm is slightly busy" but *cannot* learn that
**Saturday-at-8pm specifically** is a dinner rush. The effect of one feature
*depends on* another — an **interaction** — and a plain linear model is blind to
it.

### Definition

A **feature cross** is a new feature formed by combining two (or more) features
so their *combination* becomes its own signal:

![A feature cross combines day_of_week = Saturday and hour = 8pm into a single new feature 'Sat & 8pm', letting a simple model learn the interaction it could not see from each feature alone.](images/m05_05_feature_cross.png)

```
cross(day_of_week, hour_bucket)  ->  a new categorical like "Sat_20"
```

- **Intuition:** you are hand-building the interaction the linear model cannot
  discover on its own. After crossing, the model can put a dedicated weight on
  "Sat_20" that is unrelated to the weights on Saturday-in-general or 8pm-in-general.
- **When to use:** simpler models (linear, logistic) that lack interaction power.
  Cross bucketized numericals (e.g. `lat_bucket × lon_bucket` to capture
  neighbourhood effects in a pricing model).
- **Cost:** crosses explode cardinality (200 cities × 24 hours = 4,800 values), so
  they usually feed into the **hashing trick** or an **embedding** to stay
  compact. Deep networks and trees can learn many interactions on their own, so
  manual crosses matter most for wide/linear models.

---

## 5.6 Online vs Offline Features & Training-Serving Skew (Centrepiece)

### Motivation — the same feature, computed twice

Here is the problem that ruins more production ML systems than any modelling
mistake. Features are computed in **two different places**:

- **Offline (training):** a data engineer writes a big batch query (SQL/Spark)
  over months of historical logs to build the training table.
- **Online (serving):** a backend engineer writes application code (Python/Java)
  that must compute *the same feature* live, in milliseconds, for one user.

These are two codebases, two teams, two languages. Nothing forces them to agree.
And when they silently disagree, you get **training-serving skew**.

### Definition

**Training-serving skew** is any difference between how a feature is computed (or
what data it sees) during **training** versus during **serving**. The model was
trained on one distribution of inputs but sees a *different* distribution live,
so its accuracy in production is far worse than the glowing offline numbers
promised.

![Training-serving skew: the offline batch pipeline computes avg_spend as a mean over 90 days, while the online app code computes it over 30 days. The same feature name, two different formulas, equals skew, and the model sees inputs it never trained on.](images/m05_06_training_serving_skew.png)

### First-principles: the three ways skew arises

1. **Different code / logic.** Training averages spend over 90 days; serving over
   30. Same name, different number. The model's learned weight for `avg_spend` is
   now applied to a value that means something else.
2. **Different data freshness / availability.** A feature available in the
   historical warehouse (e.g. "total lifetime clicks") may not be computable in
   time at serving, so serving substitutes a stale or default value.
3. **Time-travel bugs (leakage).** Training accidentally uses information that
   would not yet exist at serving time — covered fully in Section 5.7.

### Worked example (concrete)

A fraud model trains beautifully — offline AUC 0.95. In production it barely
beats a coin flip on new fraud. Investigation: the training pipeline computed
`num_txns_last_hour` correctly from historical logs, but the serving code had a
bug that always returned 0 because the counter hadn't warmed up. Every live
request fed the model a feature value (0) it had rarely seen in training. **The
model wasn't wrong; the feature was skewed.**

### The fixes (in order of strength)

1. **Share one implementation.** Compute the feature with the *same code* for
   both paths — the core promise of a feature store (Section 5.7).
2. **Log features at serving time** and train on those *logged* features rather
   than recomputing from raw logs. If you train on exactly what you served, they
   cannot skew.
3. **Monitor feature distributions** in training vs serving and alert on drift
   (Module 10).

> **Cross-link:** Module 1 listed training-serving skew as the first entry in the
> "traps that only exist in ML" table and pointed here. This is the payoff.

---

## 5.7 Feature Stores (Feast, Tecton, Michelangelo Palette)

### Motivation

Once you accept that skew comes from *computing the same feature in two places*,
the fix is obvious: **compute it once, store it, and serve the same value to both
training and serving.** That is exactly what a **feature store** is.

### Definition & the two-store design

A **feature store** is a system where feature definitions are written **once** and
materialised into two synchronised stores:

![A feature store has one feature definition written once, materialised into an offline store (a warehouse with big history, read by training) and an online store (a fast key-value store with the latest values, read by serving). Feast, Tecton, and Michelangelo follow this pattern so training and serving agree.](images/m05_07_feature_store.png)

- **Offline store** — a data warehouse / lake holding the full history of feature
  values. **Training** reads from here to build large tables spanning months.
- **Online store** — a low-latency key-value store (Redis, DynamoDB, Cassandra)
  holding the *latest* value per entity. **Serving** reads from here with a
  single fast lookup (sub-millisecond).

Because both are generated from **one definition**, the value used to train and
the value used to serve are guaranteed consistent — skew from mismatched logic
disappears. Real systems: **Feast** (open source), **Tecton** (managed),
**Uber's Michelangelo Palette** (the system that popularised the idea).

### Point-in-time correctness (the subtle, must-know part)

When you build a training set you join features onto labelled events. The
**deadly mistake** is joining the *current* feature value onto a *past* event —
which leaks the future.

![Point-in-time correctness on a timeline: a label event happens at prediction time T. A feature may use only data BEFORE T (green, OK); pulling data from AFTER T (red) is leakage. A naive join pulls future rows and produces fake accuracy.](images/m05_08_point_in_time.png)

**Worked example of a naive join that leaks.** You are predicting churn. For a
customer who churned on **1 March**, you build features by joining their
`account_balance`. A naive `JOIN` grabs *today's* balance (say, April) — which is
0 because they already left! The model "learns" that balance-0 means churn, but
that fact was **unknown on 1 March**. Offline accuracy looks amazing; live it is
useless, because at real prediction time you never have the future balance.

**The correct rule — point-in-time (as-of) join:** for each labelled event at
time *T*, attach the feature value **as it was at time *T***, using only data
timestamped `≤ T`. A feature store's offline join enforces exactly this "as-of"
semantics for you, which is one of the biggest reasons to use one rather than
hand-writing joins.

### Freshness & backfills

- **Feature freshness** — how up-to-date the online value is. `avg_spend_30d`
  might be recomputed hourly; `num_txns_last_minute` must be near-real-time
  (updated by a streaming pipeline). Freshness is a design knob traded against
  cost: fresher = more compute.
- **Backfill** — when you add a *new* feature, you must compute its historical
  values for all past events so you can retrain on it. A good feature store
  backfills using the same point-in-time logic, so the historical values match
  what *would* have been served. Hand-rolled backfills are a classic source of
  leakage.

### Trade-offs

| Without a feature store | With a feature store |
|-------------------------|----------------------|
| Feature logic duplicated per model | Defined once, reused everywhere |
| High risk of training-serving skew | Consistent by construction |
| Point-in-time joins hand-written (buggy) | As-of joins handled for you |
| No feature sharing/discovery across teams | Central catalog, reuse |
| Infra overhead is zero | Extra system to run and pay for |

> **Senior signal:** proposing a feature store *and* explicitly calling out
> point-in-time correctness when asked "how do you avoid leakage / skew?" marks a
> Staff-level answer. Juniors describe features; seniors describe how features stay
> *consistent and honest over time*.

---

## Module 5 — Interview Mapping (what companies probe)

| Company | How Module 5 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "How do you engineer features for this ranker?" | Lists a few features | Names types, uses embeddings + crosses, plans a feature store for consistency |
| **Uber / Stripe** | Fraud/ETA features; "how avoid skew?" | Ignores skew | Cites training-serving skew, logs served features, point-in-time joins |
| **Amazon** | Tabular features at scale, cost | One-hot everything | Hashing/entity embeddings for high cardinality, justifies memory trade-off |
| **OpenAI / Anthropic** | Text/embedding features, leakage | Uses raw stats | Fits scalers on train only, out-of-fold target encoding, guards leakage |

**Most common opening move:** when asked to design features, first *classify the
signals* (numerical/categorical/text/temporal), then say how each is encoded, and
proactively raise **consistency between training and serving**. That last point
is what separates you.

---

## Module 5 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask definitional items — what is normalization vs
  standardization, one-hot encoding, why scale features. Sections 5.2–5.3 cover
  these.
- **GATE CS / DA:** the DA paper does test **feature scaling**, **encoding**, the
  effect of scaling on KNN/SVM/gradient descent vs trees, and basic
  dimensionality ideas. Section 5.3 is the highest-yield exam content here.
- **ISRO / DRDO:** occasional definitions of normalization and encoding.

> **Flag:** feature *stores* and training-serving skew are essentially
> **interview / job-only** topics — rarely on written exams, but central to the
> AI/MLE role.

---

## Module 5 — Common Mistakes & Misconceptions

1. **"Encode every categorical with one-hot."** For millions of values one-hot
   explodes; use hashing or embeddings. (Section 5.2, 5.4.)
2. **"Always scale features."** Not for tree models — splits depend on order, not
   magnitude. (Section 5.3.)
3. **"Fit the scaler on all the data."** That leaks test statistics; fit on train
   only. (Section 5.3.)
4. **"Target encoding is free signal."** Done naively it leaks the label; use
   out-of-fold encoding with smoothing. (Section 5.2.)
5. **"Offline AUC is great, so we're done."** If features are skewed, live
   performance collapses. Check training-serving consistency. (Section 5.6.)
6. **"A simple JOIN builds the training set."** Naive joins pull future values and
   leak; you need point-in-time (as-of) joins. (Section 5.7.)
7. **"Embeddings are only for text."** Entity embeddings help *any* high-cardinality
   categorical in tabular data. (Section 5.4.)

---

## Module 5 — MCQs (with answers & explanations)

**Q1.** You must encode `user_id` with ~50 million possible values under a fixed
memory budget. Best choice?
a) One-hot  b) Hashing trick or embedding  c) Standardization  d) Bucketization

<details><summary>Answer</summary>**b.** One-hot would be 50M columns. Hashing
gives fixed size *K*; an embedding gives a small dense learned vector. Both handle
huge/open cardinality.</details>

**Q2.** For which model does feature scaling make essentially **no** difference?
a) K-Nearest Neighbours  b) Logistic regression  c) Gradient-boosted trees
d) Neural network

<details><summary>Answer</summary>**c.** Trees split on the *order* of values, so
monotonic scaling doesn't change any split. KNN (distances), logistic regression
and NNs (gradient descent) all care about scale.</details>

**Q3.** A model has offline AUC 0.95 but performs at chance in production. The
features are computed by different code in training and serving. This is:
a) Overfitting  b) Training-serving skew  c) Underfitting  d) A cache miss

<details><summary>Answer</summary>**b.** The live inputs differ from what the
model trained on. Fix by sharing one implementation (feature store) or training on
logged served features.</details>

**Q4.** Building a churn training set, you join each churned customer's *current*
account balance onto their churn event from months ago. What have you done?
a) Correct point-in-time join  b) Data leakage from the future  c) Normalization
d) A feature cross

<details><summary>Answer</summary>**b.** The current balance was unknown at
prediction time; using it leaks the future. You need an as-of join using only data
timestamped at or before the event.</details>

**Q5.** Why do dense embeddings generalise better than one-hot vectors?
a) They use more memory  b) Similar items get nearby vectors, so learning
transfers  c) They avoid all collisions  d) They require no training

<details><summary>Answer</summary>**b.** Embeddings place similar items close in a
shared space, letting the model share what it learns across related ids. One-hot
treats every id as equally unrelated.</details>

**Q6.** A linear model can't learn that "Saturday at 8pm" is special even though it
knows about Saturdays and 8pm separately. The fix is:
a) Standardization  b) A feature cross of day × hour  c) One-hot on hour only
d) Dropping the hour feature

<details><summary>Answer</summary>**b.** A cross combines the two into one feature
so the model can weight the specific interaction. Often hashed/embedded to control
cardinality.</details>

**Q7.** In a feature store, which store does the *online serving* path read from?
a) The offline warehouse  b) The low-latency key-value online store  c) The
training notebook  d) Cold blob storage

<details><summary>Answer</summary>**b.** Serving needs sub-millisecond lookups, so
it reads the online store (Redis/DynamoDB). Training reads the offline store with
full history.</details>

**Q8.** Which is the safest way to compute target/mean encoding?
a) Mean over all rows including the current one  b) Out-of-fold mean with
smoothing  c) Mean over the test set  d) One-hot instead

<details><summary>Answer</summary>**b.** Out-of-fold encoding keeps the row's own
label out of its feature, and smoothing stabilises rare categories — avoiding
leakage.</details>

---

## Module 5 — Design Exercises (easy → hard)

- **Easy.** For each, name the feature type and one encoding/transform: (1)
  `country`; (2) `price_in_usd`; (3) `signup_timestamp`; (4) `review_text`.
- **Easy.** You feed `age` (0–100) and `salary` (0–1M) to a KNN classifier and
  results are poor. What one preprocessing step likely fixes it, and why?
- **Medium.** You have a `product_id` with 20 million values feeding an XGBoost
  model. Compare one-hot, hashing, and target encoding for this case; pick one and
  justify memory and leakage.
- **Medium.** Design features for a food-delivery ETA model. Include at least one
  temporal feature and one feature cross, and say what interaction the cross
  captures.
- **Hard.** A fraud model scores AUC 0.96 offline but 0.55 live. Walk through how
  you would diagnose whether the cause is skew, leakage, or drift, and what
  instrument you'd add for each.
- **Hard.** Design a feature store for a recommender used by three teams. Cover the
  online/offline split, point-in-time joins for training, freshness targets per
  feature, and how you'd backfill a newly added feature without leaking.

---

## Module 5 — Concept Review (one page)

- **Feature types:** numerical · categorical · text · image/audio · temporal ·
  cross. Everything must become a number.
- **Encoding:** one-hot (small vocab) · hashing (huge/open, fixed size,
  collisions) · target/mean (1 number, watch leakage → out-of-fold) ·
  bucketization (non-linear numerics).
- **Scaling** (normalize/standardize) matters for **distance & gradient** models
  (KNN, SVM, linear, NN), **not for trees**. Fit the scaler on **train only**.
- **Embeddings:** short **dense learned** vectors; similar items sit close →
  **generalise**; far cheaper than sparse one-hot. Learned / pretrained / entity.
- **Feature crosses:** hand-built interactions for models that can't learn them;
  hash or embed to control cardinality.
- **Training-serving skew:** same feature computed differently offline vs online →
  live accuracy collapses. Fix: one implementation, log served features, monitor.
- **Feature store:** define once → **offline store** (history, training) +
  **online store** (latest, serving). Enforces **point-in-time correctness** (no
  future leakage), manages **freshness** and **backfills**. Feast / Tecton /
  Michelangelo.

---

## Module 5 — Flash Cards (Q → A)

1. Four categorical encodings? → *one-hot, hashing, target/mean, bucketization.*
2. Why not one-hot a 10M-value id? → *Vector explodes; use hashing or embedding.*
3. Cost of the hashing trick? → *Collisions (two values share a bucket).*
4. Which models ignore feature scale? → *Tree-based (split on order).*
5. Fit the scaler on…? → *Training data only, then apply to val/test/serving.*
6. Why dense embeddings generalise? → *Similar items get nearby vectors; learning
   transfers.*
7. What is a feature cross for? → *Let a simple model learn an interaction.*
8. Training-serving skew in one line? → *Feature computed differently in training
   vs serving → live accuracy drops.*
9. Point-in-time correctness? → *Use only data known at/before prediction time T;
   no future leakage.*
10. Two stores in a feature store? → *Offline (history/training) + online
    (latest/serving).*

---

## Module 5 — Pattern Recognition (how to spot it in an interview)

- Hear **"high-cardinality categorical"** → say *hashing trick* or *entity
  embedding*, not one-hot.
- Hear **"we use KNN/SVM/linear/NN"** → mention *feature scaling*; if **trees**,
  say scaling is unnecessary.
- Hear **"great offline, bad in production"** → say *training-serving skew* and/or
  *leakage*; propose logging served features + a feature store.
- Hear **"how do you build the training set / avoid leakage?"** → say
  *point-in-time (as-of) joins*, fit stats on train only.
- Hear **"the effect of X depends on Y"** → propose a *feature cross* (hashed or
  embedded).
- Hear **"multiple teams reuse features / keep them fresh"** → propose a *feature
  store* with online+offline stores, freshness targets, and backfills.

---

## Module 5 — Revision Notes / Mini Cheat Sheet

```
FEATURE TYPES:  numerical | categorical | text | image | temporal | cross
                (everything must become a NUMBER)

ENCODE CATEGORICALS:
  one-hot      -> small stable vocab; size = V; no false order
  hashing      -> hash(x) mod K; fixed size; huge/open vocab; risk = collisions
  target/mean  -> replace cat with mean(y|cat); 1 number; LEAK -> out-of-fold+smooth
  bucketize    -> cut numeric into ranges; captures non-linearity

SCALING (normalize 0-1 / standardize z):
  MATTERS for:  KNN, SVM, k-means (distance) | linear, logistic, NN (gradient)
  IGNORED by:   decision tree, RF, GBDT (split on ORDER)
  RULE: fit scaler on TRAIN only (else leakage)

EMBEDDINGS: id -> short DENSE learned vector; similar items close -> generalise
            flavours: learned | pretrained | entity   (dense << sparse one-hot)

FEATURE CROSS: combine A x B into one feature -> interaction a linear model can't
               learn alone; hash/embed to tame cardinality

TRAINING-SERVING SKEW = same feature, different code offline vs online
  -> great offline, bad live.  FIX: one impl | log served features | monitor

FEATURE STORE:  define ONCE ->  OFFLINE store (history -> training)
                                ONLINE store  (latest  -> serving, ms lookup)
  POINT-IN-TIME: use only data known at/<= T  (as-of join) -> no future leak
  also: freshness knob | backfills (recompute history for new feature)
  tools: Feast | Tecton | Uber Michelangelo Palette
```

---

> **Next module:** *Module 6 — Model Training at Scale.* Now that we have clean,
> consistent features, we pick a model and *fit* it — choosing loss functions,
> handling data too big for one machine, and training across many GPUs/workers
> without the whole thing falling over.
