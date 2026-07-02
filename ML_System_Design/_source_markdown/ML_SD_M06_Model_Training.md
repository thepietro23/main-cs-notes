---
title: "Module 6 — Model Development & Training at Scale"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — Model Development & Training at Scale

> **Why this module matters.**
> By now you can frame a problem (Module 3), gather data (Module 4), and build
> features (Module 5). This is the module where you finally *pick a model, choose
> what it should minimise, and train it* — possibly across hundreds of GPUs.
> This is the part beginners think ML is *all* about; in reality it is one stage
> of the loop, but it is the stage with the most math. We handle that math from
> **first principles and in plain English**: every loss function is derived,
> every optimizer explained by what it is actually doing, and every distributed-
> training trick motivated by a concrete pain ("the model won't fit on one GPU").
> The golden rule that runs through the whole module: **start simple, add
> complexity only when a simpler thing provably fails.**

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★★★★      | ★★★★      | ★★★★★       |

**What you must be able to do after this module:**
pick a model family from the data type and justify it; explain why a *baseline*
comes first; define bias and variance and connect them to under/overfitting;
write and *derive* MSE, cross-entropy, hinge, pairwise-ranking, and contrastive
losses and say what each optimizes; explain SGD vs Adam and the role of the
learning rate; contrast data / model / tensor / pipeline parallelism and know
when to reach for ZeRO/FSDP and mixed precision; and choose between grid /
random / Bayesian / Hyperband tuning and between training-from-scratch and
transfer learning.

> **How to read this module.** As always: **problem → simplest attempt → why it
> breaks → the fix.** The math is here to *serve* the intuition, never to
> replace it. If a formula ever feels opaque, re-read the plain-English line
> right beside it.

---

## 6.1 Choosing a Model: Linear → Trees/GBDT → Deep Nets → Transformers

### Motivation (the problem that existed)

You have clean features and a target. Now: *which model?* Beginners reach
straight for a deep neural network because it sounds powerful. But a deep net on
500 rows of tabular data will overfit horribly, train slowly, and lose to a
30-line gradient-boosted-trees model. The right choice is driven by the **shape
of your data** and the **amount** of it — not by what is fashionable.

### Definition

- **Linear / logistic models** — the output is a weighted sum of features
  (plus a squashing function for classification). Few parameters, fast,
  interpretable.
- **Trees / GBDT** (Gradient Boosted Decision Trees: XGBoost, LightGBM) — build
  many small decision trees, each correcting the previous one's errors. King of
  **tabular** data.
- **Deep neural networks (DNNs)** — stacked layers of learned non-linear
  transforms; excel at **perception** (images, audio) and **sequences**.
- **Transformers** — attention-based deep nets that dominate **language** and,
  increasingly, any domain with huge data and long-range structure.

![Decision flow for choosing a model: split by data type, then climb from linear to GBDT for tabular, and from deep nets to transformers for perception/language.](images/m06_01_model_choice.png)

### Intuition & analogy

Think of tools in a workshop. A screwdriver (linear model) is fast and you
understand exactly what it did. A power drill (GBDT) handles almost any tabular
"screw" and is the reliable default. A CNC machine (deep net / transformer) is
incredibly powerful but needs lots of setup, lots of raw material (data), and
lots of electricity (compute). You do not use the CNC machine to hang a picture.

### First-principles: why GBDT wins on tabular data

Tabular columns are often **heterogeneous** (age, country, price) with no
spatial or sequential structure to exploit. Decision trees split on one feature
at a time using thresholds — exactly the piecewise, rule-like structure tabular
data has. They handle mixed scales and missing values naturally and need little
tuning. Deep nets, by contrast, shine when there is **structure to share**:
nearby pixels in an image, or nearby words in a sentence. No such structure ⇒ no
advantage for depth, and the DNN just overfits.

### Quick decision table

| Data / situation                    | First choice        | Why                                   |
|-------------------------------------|---------------------|---------------------------------------|
| Tabular, < ~100k rows               | GBDT (XGBoost)      | Best accuracy/effort on tabular       |
| Tabular, need interpretability      | Linear / logistic   | Coefficients are readable             |
| Images, audio, video                | CNN / deep net      | Exploits spatial structure            |
| Sequences, time series              | RNN / Transformer   | Exploits order / long-range deps      |
| Text, huge corpora                  | Transformer         | Attention + scale                     |
| Very little data                    | Linear / GBDT + regularization | Deep nets overfit small data |

> **Senior signal:** "For this tabular churn problem I'd start with logistic
> regression as a baseline, then XGBoost — a deep net is unlikely to pay for
> itself here." That one sentence signals judgment.

---

## 6.2 Baselines and Why They Matter

### Motivation

You train a model and get 82% accuracy. Is that good? You *cannot know* without
a reference point. If 80% of emails are "not spam", a model that always predicts
"not spam" gets 80% — your 82% is nearly worthless. A **baseline** is the cheap
reference every real model must beat.

### The baselines to always compute

![Baselines ladder: random/majority-class, a simple rule, and a linear model all feed into the question — does the fancy model beat every one of them?](images/m06_02_baselines.png)

1. **Random / majority-class** — predict the most common label, or predict at
   the base rate. Sets the floor.
2. **Simple heuristic / rule** — a hand rule a domain expert would write ("flag
   transactions over $10k from a new device").
3. **Simple model** — logistic regression or a shallow tree.

### First-principles: why bother

A baseline answers three questions at once: *(a)* is there signal in the data at
all? *(b)* how much lift does complexity buy? *(c)* is my evaluation pipeline
even wired up correctly? If your fancy model *loses* to the majority-class
baseline, you have a bug, a leak, or no signal — and you just saved weeks. A
baseline also gives the business a concrete cost/benefit: "the deep model is 3%
better but 20× more expensive to serve — worth it?"

> **Common mistake:** reporting a single accuracy number with no baseline. In an
> interview, always say what you are comparing against.

---

## 6.3 Bias, Variance, Regularization, and Over/Underfitting

### Motivation

The central tension of ML: a model must be **complex enough** to capture the
real pattern, but **simple enough** not to memorise noise. Get it wrong in
either direction and the model fails on new data — which is the only data that
matters.

### Definition (bias and variance, in plain English)

- **Bias** = error from the model being too simple to represent the truth (it
  makes systematic mistakes). High bias → **underfitting**.
- **Variance** = error from the model being too sensitive to the particular
  training set (it memorises noise). High variance → **overfitting**.

![Three regimes side by side: underfit (high bias, high train and test error), just right (low bias and low variance), and overfit (low train but high test error), under a model-complexity axis.](images/m06_03_bias_variance.png)

### First-principles derivation (the decomposition)

For a squared-error regression, the expected test error at a point decomposes
exactly into three pieces:

$$\mathbb{E}\big[(y-\hat f(x))^2\big] = \underbrace{(\text{bias})^2}_{\text{too simple}} + \underbrace{\text{variance}}_{\text{too sensitive}} + \underbrace{\sigma^2}_{\text{irreducible noise}}$$

In words: total error = *how wrong on average* + *how much you wobble across
datasets* + *noise you can never remove*. Making the model more complex lowers
bias but raises variance. The **sweet spot** minimises their sum — that is what
you are hunting for. The irreducible term $\sigma^2$ is a wall: no model beats it.

### The fix: regularization (penalise complexity)

The cleanest way to slide toward the sweet spot is to add a penalty for large
weights to the loss, so the optimizer prefers simpler solutions.

![L2 (Ridge) adds lambda times sum of squared weights and shrinks weights smoothly; L1 (Lasso) adds lambda times sum of absolute weights and drives some weights exactly to zero for feature selection.](images/m06_04_regularization.png)

- **L2 (Ridge):** add $\lambda \sum_i w_i^2$. Shrinks all weights smoothly toward
  zero; none become exactly zero. Good when many features each contribute a
  little.
- **L1 (Lasso):** add $\lambda \sum_i |w_i|$. Its corner-shaped penalty pushes
  some weights **exactly to zero**, so it doubles as automatic feature
  selection. Good when you suspect only a few features matter.
- **$\lambda$ (the strength knob):** bigger $\lambda$ = stronger penalty =
  simpler model = **more bias, less variance**. It is itself a hyperparameter
  (Section 6.7).
- Other regularizers: **dropout** (randomly zero neurons during training),
  **early stopping** (stop before the model memorises), **data augmentation**,
  **weight decay** (the optimizer form of L2).

### Worked example

Fitting a wiggly degree-15 polynomial to 20 noisy points: it passes through
every point (train error ≈ 0) but swings wildly between them (huge test error) —
classic overfitting / high variance. A straight line misses the curve entirely
(high train *and* test error) — underfitting / high bias. A degree-3 curve with
mild L2 nails the trend without chasing noise.

> **Interview line:** "Train error low but validation error high ⇒ overfitting ⇒
> add regularization, get more data, or reduce capacity. Both errors high ⇒
> underfitting ⇒ add capacity or better features."

---

## 6.4 Loss Functions — with Math and Derivations

### Motivation

Training = choosing weights that **minimise a loss**. The loss *is* your
definition of "good". Pick the wrong loss and even a perfectly optimised model
solves the wrong problem. Below, each loss is derived from what it is really
trying to do.

![Map of loss functions: MSE for regression, cross-entropy for classification, ranking loss for ordering, contrastive loss for embeddings, and hinge loss for max-margin classification, each labelled with the goal it optimises.](images/m06_05_loss_functions.png)

### MSE (Mean Squared Error) — for regression

$$L_{\text{MSE}} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat y_i)^2$$

Penalises the **square** of the error, so big misses hurt disproportionately. It
is the right loss when errors are roughly Gaussian and large errors are
genuinely worse. Downside: sensitive to outliers (one huge error dominates). Use
**MAE** (absolute error) or **Huber** loss when outliers are a concern.

### Cross-entropy — for classification (derived from MLE)

Where does cross-entropy come from? From **Maximum Likelihood Estimation**. For
binary labels, the model outputs $\hat y = P(y=1\mid x)$. The probability of
seeing the actual label under the model is $\hat y^{\,y}(1-\hat y)^{1-y}$. We want
weights that make the observed data **most likely**, i.e. maximise the product of
these over all examples. Maximising a product is awkward, so take the log
(turns product into sum) and flip the sign (maximise → minimise):

$$L_{\text{CE}} = -\frac{1}{n}\sum_{i=1}^{n}\Big[y_i\log \hat y_i + (1-y_i)\log(1-\hat y_i)\Big]$$

In words: **be confident and right → tiny loss; be confident and wrong →
enormous loss** (the $\log$ blows up as $\hat y \to 0$ while $y=1$). For multi-class
it generalises to $-\sum_c y_c \log \hat y_c$ over classes. This is why
classification uses cross-entropy, not MSE: MSE on probabilities gives weak,
flat gradients when the model is confidently wrong, so learning stalls.

### Hinge loss — the max-margin (SVM) idea

$$L_{\text{hinge}} = \max(0,\; 1 - y\cdot s), \qquad y\in\{-1,+1\}$$

where $s$ is the raw score. If a point is on the correct side *and* past a
margin of 1, loss is exactly 0 — the model stops caring about already-safe
points and focuses on the boundary. This produces the **maximum-margin**
separator that SVMs are famous for.

### Ranking losses — pairwise / order matters, not the exact value

For search and recommendations you care about **order**, not absolute scores.
A **pairwise** loss takes a relevant item $i^+$ and a less-relevant item $i^-$
and pushes their scores apart:

$$L_{\text{pair}} = \max\big(0,\; m - (s_{i^+} - s_{i^-})\big)$$

It is happy once the good item outscores the bad one by margin $m$. (BPR, RankNet
are smooth variants using a logistic on the score difference.) This directly
optimizes ranking metrics like NDCG far better than a pointwise MSE would.

### Contrastive loss — for learning embeddings

Used in metric learning and self-supervised learning (e.g. two-tower models,
SimCLR). Given pairs labelled *similar* ($y=1$) or *dissimilar* ($y=0$) with
embedding distance $d$:

$$L_{\text{contrastive}} = y\,d^2 + (1-y)\,\max(0,\; m-d)^2$$

Similar pairs are **pulled together** ($d\to 0$); dissimilar pairs are **pushed
apart** until at least margin $m$. This shapes an embedding space where distance
means semantic similarity. (Triplet loss extends this to anchor/positive/negative
triples.)

### Which loss when?

| Task                       | Loss                     | Optimizes                      |
|----------------------------|--------------------------|--------------------------------|
| Predict a number           | MSE / MAE / Huber        | Closeness of value             |
| Classify (probabilities)   | Cross-entropy            | Calibrated correct probability |
| Max-margin classify        | Hinge                    | Wide separating margin         |
| Rank a list                | Pairwise / listwise      | Correct ordering               |
| Learn embeddings           | Contrastive / triplet    | Meaningful distances           |

---

## 6.5 Optimization: SGD, Adam, and the Learning Rate

### Motivation

Given a loss, how do we actually find the weights that minimise it? We cannot
try all weight combinations (there are billions). We **walk downhill** on the
loss surface using gradients.

### Gradient descent from first principles

The gradient $\nabla L$ points in the direction of *steepest increase* of the
loss. So to *decrease* the loss we step in the opposite direction:

$$w \leftarrow w - \eta\,\nabla L(w)$$

$\eta$ (eta) is the **learning rate** — the step size. Repeat until the loss
stops improving. That is the whole idea; everything else is a refinement.

![Loss-surface picture: three boxes feed arrows toward the minimum — a tiny learning rate crawls, a right-sized one descends steadily, and a too-large one overshoots and can diverge.](images/m06_06_optimization.png)

### The learning rate is the most important knob

- **Too small:** training crawls; may take forever or get stuck.
- **Too large:** steps overshoot the valley, bounce around, or **diverge** (loss
  goes to infinity / NaN).
- **Just right:** steady, fast descent.

In practice you use a **schedule**: warm up, then decay (cosine or step decay).

### SGD vs Adam (intuition)

- **SGD (Stochastic Gradient Descent):** compute the gradient on a small
  **mini-batch** instead of the whole dataset. Cheaper per step and the noise
  actually helps escape shallow traps. Add **momentum** to keep rolling in a
  consistent direction and smooth out the noise.
- **Adam:** adapts the step size **per weight** using running averages of the
  gradient (momentum) and its squared magnitude (scale). Weights with big, noisy
  gradients get smaller steps; quiet weights get bigger steps. It "just works"
  with little tuning, which is why it is the default for deep nets. SGD +
  momentum sometimes generalises slightly better for vision, so it is still used.

> **Rule of thumb:** start with Adam and a learning rate around $10^{-3}$; if the
> loss explodes, lower it; if it barely moves, raise it. Tune the LR *before*
> anything else.

---

## 6.6 Distributed Training at Scale

### Motivation

Two walls force you off a single GPU: **(1)** the dataset is so large that one
GPU would take weeks, or **(2)** the *model itself* is too big to fit in one
GPU's memory. Two walls, two different families of solution.

### Data parallelism vs model parallelism

![Data parallelism keeps a full model copy on each GPU and feeds each a different data shard, then all-reduces gradients; model parallelism splits one big model's layers across GPUs.](images/m06_07_parallelism.png)

- **Data parallelism** — every GPU holds a **full copy** of the model; each
  processes a **different shard** of the batch, computes gradients, and then all
  GPUs **average their gradients** so the copies stay in sync. Use when the model
  *fits* on one GPU but the data is huge. This is the common case.
- **Model parallelism** — the model is **too big to fit**, so you split it across
  GPUs. Two flavours:
  - **Tensor parallelism:** split *within* a layer (e.g. shard a giant matrix
    multiply across GPUs).
  - **Pipeline parallelism:** put *different layers* on different GPUs and stream
    micro-batches through like an assembly line.

### How gradients get synced: parameter server vs all-reduce

- **Parameter server:** worker GPUs send gradients to central server(s) that
  hold the weights, update, and send weights back. Simple, but the server
  becomes a bandwidth bottleneck.
- **All-reduce (ring all-reduce):** GPUs exchange gradients **directly** with
  each other in a ring so bandwidth is used evenly and there is no central
  bottleneck. This is the modern default for synchronous data-parallel training.

### Memory-saving techniques (fitting bigger models)

- **ZeRO / FSDP** (Fully Sharded Data Parallel): even in data parallelism, every
  GPU redundantly stores the full weights, gradients, and optimizer states. ZeRO
  **shards** these across GPUs so each holds only a slice, gathering pieces only
  when needed. This lets you train models far larger than one GPU's memory while
  keeping data-parallel simplicity.
- **Mixed precision:** store and compute in 16-bit (FP16/BF16) instead of 32-bit.
  Roughly halves memory and speeds up math on modern GPUs; a small FP32 "master
  copy" and loss scaling keep it numerically stable. Almost free win — use it by
  default.
- **Gradient checkpointing:** recompute activations during the backward pass
  instead of storing them all — trades compute for memory.

### The scaling decision (in order)

1. One GPU + **mixed precision** — cheapest, try first.
2. **Data parallel + all-reduce** — data too big, model still fits.
3. **ZeRO / FSDP** — model states too big; shard them.
4. **Tensor + pipeline parallel** — model genuinely too large for one device.

> **Senior signal:** climb this ladder **only as far as forced to**. Every rung
> adds communication cost, complexity, and failure modes. "Do we actually need
> model parallelism, or does FSDP + mixed precision fit?" is the mature question.

---

## 6.7 Hyperparameter Tuning

### Motivation

Learning rate, tree depth, number of layers, $\lambda$ — these are
**hyperparameters** you set *before* training (the model does not learn them).
The search space is huge and each trial costs a full training run, so you need a
strategy smarter than guessing.

![Four hyperparameter search strategies: grid tries every combination, random samples combinations, Bayesian is model-guided and sample-efficient, and Hyperband cheaply early-stops bad trials.](images/m06_08_hpo.png)

### The four strategies

| Method       | Idea                                             | Best when                          |
|--------------|--------------------------------------------------|------------------------------------|
| **Grid**     | Try every combination on a fixed grid            | Very few hyperparameters           |
| **Random**   | Sample combinations at random                    | Many dims (usually beats grid)     |
| **Bayesian** | Build a model of "params → score", sample where it looks promising | Expensive trials, want efficiency |
| **Hyperband**| Start many trials cheaply, kill the losers early, give survivors more budget | Trials that can be stopped early |

### First-principles: why random beats grid

Usually only **one or two** hyperparameters really matter. A grid wastes most of
its trials varying the *unimportant* ones at fixed values of the important ones.
Random search, in the same budget, tries many *distinct* values of the important
hyperparameter — so it explores the axis that matters far better. This is a
classic, counter-intuitive result (Bergstra & Bengio, 2012).

**Bayesian optimization** goes further: it *learns* from finished trials to
propose the next promising point, so it needs fewer total runs. **Hyperband**
attacks a different axis — it saves compute by early-stopping obviously-bad
trials rather than running them to completion. (BOHB combines both.)

---

## 6.8 Transfer Learning, Fine-Tuning, and Pretraining

### Motivation

Training a big model from scratch needs enormous data and compute you often do
not have. But someone already trained a model on a massive generic dataset. Why
throw away everything it learned? **Reuse it.**

![Transfer learning: pretrain a base model on huge generic data with self-supervision, then freeze its early layers and fine-tune the rest on your small task-specific dataset.](images/m06_09_transfer_learning.png)

### The three terms

- **Pretraining:** train a large model once on a huge, generic corpus — often
  **self-supervised** (predict the next word, or fill in masked pixels), so no
  human labels are needed. It learns broadly useful features.
- **Transfer learning:** take that pretrained model and reuse its learned
  features for a *different, related* task.
- **Fine-tuning:** continue training the pretrained model on your (usually small)
  task-specific labelled data, so it adapts.

### First-principles: why it works

Early layers learn **general** features (edges, textures; grammar, syntax) that
transfer across tasks. Only the later layers are task-specific. So you can
**freeze** the early layers (keep their weights) and only train the top — needing
far less data and compute — because you are not re-learning "what an edge is".

### Practical patterns

- **Feature extraction:** freeze the whole backbone, train only a new head. Least
  data, fastest, best when your data is tiny and similar to the pretraining data.
- **Full fine-tuning:** unfreeze everything and train with a small learning rate.
  Best when you have moderate data and the domain differs.
- **Parameter-efficient fine-tuning (LoRA, adapters):** train a tiny number of
  extra weights while freezing the giant base — the modern default for adapting
  large models cheaply.

> **Interview line:** "With only 5k labelled images I would not train a CNN from
> scratch — I'd fine-tune a pretrained backbone, freezing early layers." That is
> the expected answer.

---

## Module 6 — Interview Mapping (what companies probe)

| Company | How Module 6 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "How would you train this at scale?" | "Use more GPUs" | Distinguishes data vs model parallel, mentions all-reduce, FSDP, mixed precision, and *why* |
| **Amazon** | Model choice for a tabular problem | Jumps to deep learning | Baseline → GBDT, justifies against a DNN on cost |
| **OpenAI / Anthropic** | Loss design, pretraining/fine-tuning | Vague on the loss | Derives cross-entropy from MLE, explains LoRA / fine-tuning trade-offs |
| **Uber / Stripe** | Regularization, overfitting on fraud model | "Add more data" | Diagnoses bias vs variance from train/val gap, picks the right fix |

**Most common trap:** proposing a deep net for tabular data, or reporting a
metric with no baseline. Naming the baseline first and matching model family to
data type instantly reads as senior.

---

## Module 6 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **GATE CS / DA:** **HIGH relevance.** The DA (Data Science & AI) paper tests
  the ML-algorithm core covered here directly — **bias-variance trade-off,
  L1/L2 regularization, gradient descent and learning rate, cross-entropy and
  MSE, over/underfitting, and hyperparameter concepts** are all fair game as
  numerical or conceptual questions. Know the loss formulas and the
  bias-variance decomposition cold.
- **SEBI IT / RBI IT:** definitional only — what is overfitting, what is gradient
  descent, supervised loss basics.
- **ISRO / DRDO:** occasional basic definitions (loss function, learning rate).

> **Flag:** the *distributed-training* and *transfer-learning* systems content is
> largely **interview/role-only**; the *algorithmic* content (6.3–6.5, 6.7) is
> the exam-heavy part, especially for GATE-DA.

---

## Module 6 — Common Mistakes & Misconceptions

1. **"Deep learning is always best."** For tabular data, GBDT usually wins with
   far less effort. (6.1)
2. **"82% accuracy is good."** Meaningless without a baseline; a majority-class
   guess may already hit 80%. (6.2)
3. **"Overfitting means the model is bad."** It means it is *too complex for the
   data* — regularize, get more data, or reduce capacity. (6.3)
4. **"Use MSE for classification."** No — cross-entropy gives proper gradients;
   MSE on probabilities stalls learning. (6.4)
5. **"Data parallelism helps when the model won't fit."** No — that is what
   *model* parallelism / ZeRO is for; data parallelism assumes the model fits. (6.6)
6. **"Grid search is the thorough, correct way."** Random search usually finds
   better configs per unit compute in high dimensions. (6.7)
7. **"Always train from scratch."** With little data, fine-tune a pretrained
   model instead. (6.8)

---

## Module 6 — MCQs (with answers & explanations)

**Q1.** You have 20k rows of tabular customer data. Best first real model?
a) A 12-layer transformer  b) XGBoost (GBDT)  c) A large CNN  d) k-means

<details><summary>Answer</summary>**b.** GBDT dominates tabular data of this size;
deep nets rarely pay off and tend to overfit. Start with a linear baseline, then
XGBoost.</details>

**Q2.** Cross-entropy loss is derived from:
a) minimising squared error  b) maximum likelihood estimation
c) the triangle inequality  d) the bias-variance decomposition

<details><summary>Answer</summary>**b.** Maximising the likelihood of the observed
labels, then taking the negative log, yields exactly the cross-entropy loss.</details>

**Q3.** Train error is low, validation error is high. This indicates:
a) underfitting  b) overfitting (high variance)  c) high bias  d) a learning
rate that is too small

<details><summary>Answer</summary>**b.** The model memorised the training set. Fix
with regularization, more data, or less capacity.</details>

**Q4.** Which regularizer tends to drive some weights *exactly* to zero
(feature selection)?
a) L2 / Ridge  b) L1 / Lasso  c) dropout  d) momentum

<details><summary>Answer</summary>**b.** L1's corner-shaped penalty produces exact
zeros; L2 shrinks smoothly but leaves weights non-zero.</details>

**Q5.** The learning rate is too large. Most likely symptom?
a) training is extremely slow  b) loss diverges / oscillates  c) perfect
convergence  d) the model underfits by definition

<details><summary>Answer</summary>**b.** Oversized steps overshoot the minimum and
can send the loss to infinity/NaN.</details>

**Q6.** Your model is too big to fit in a single GPU's memory. Best approach?
a) Data parallelism only  b) Model/tensor/pipeline parallelism or ZeRO/FSDP
c) A smaller learning rate  d) Grid search

<details><summary>Answer</summary>**b.** Splitting or sharding the model across GPUs
is what fits an oversized model; plain data parallelism assumes it already
fits.</details>

**Q7.** Why does random search often beat grid search?
a) It uses more compute  b) Only a few hyperparameters matter, and random search
explores their values better per unit budget  c) It is deterministic  d) It never
overfits

<details><summary>Answer</summary>**b.** Grid wastes trials on unimportant dims;
random samples more distinct values of the important ones (Bergstra & Bengio,
2012).</details>

**Q8.** You have 5k labelled images. Best strategy?
a) Train a large CNN from scratch  b) Fine-tune a pretrained backbone, freezing
early layers  c) Use logistic regression on raw pixels  d) Collect 10M images
first

<details><summary>Answer</summary>**b.** Transfer learning reuses general features;
fine-tuning adapts with little data and compute.</details>

---

## Module 6 — Design Exercises (easy → hard)

- **Easy.** For each, name the model family and one baseline: (1) predict house
  price from 8 columns; (2) classify cat vs dog photos; (3) rank search results.
  *(GBDT+linear; CNN/transfer+majority; ranking model+popularity.)*
- **Easy.** Write the MSE and binary cross-entropy formulas from memory and say
  which is for regression vs classification.
- **Medium.** A model gets 99% train accuracy, 71% validation accuracy. Diagnose
  the problem and list three concrete fixes in priority order.
- **Medium.** You must train a 3B-parameter language model but each GPU holds
  only 1B parameters' worth of state. Describe the exact combination of
  techniques you'd use and why.
- **Hard.** Design the loss function for a two-tower recommender that must both
  (a) rank relevant items above irrelevant ones and (b) learn a useful embedding
  space. Justify your choice.
- **Hard.** You have a fixed 100-GPU-hour tuning budget and 6 hyperparameters,
  one of which dominates. Design a tuning plan (method + budget split) and
  explain why it beats grid search.

---

## Module 6 — Concept Review (one page)

- **Model choice** follows the data: linear/GBDT for **tabular**, deep nets for
  **perception**, transformers for **language/scale**. Start simple; climb only
  if a simpler model provably fails.
- **Baselines** (majority / rule / linear) are mandatory — a metric with no
  baseline is meaningless.
- **Bias** = too simple (underfit); **variance** = too sensitive (overfit).
  Test error $=$ bias$^2$ + variance + noise. **Regularization** (L1 exact-zeros
  / feature selection; L2 smooth shrink; dropout; early stopping) trades a little
  bias for less variance.
- **Losses:** MSE (regression), **cross-entropy from MLE** (classification),
  hinge (max-margin), pairwise (ranking), contrastive (embeddings). The loss *is*
  your definition of good.
- **Optimization:** step downhill by $-\eta\nabla L$. **Learning rate** is the
  key knob (too big diverges, too small crawls). **SGD+momentum** vs **Adam**
  (adaptive, per-weight — the default).
- **Distributed:** **data parallel** (model fits, data huge; all-reduce) vs
  **model parallel** (model too big; tensor/pipeline). **ZeRO/FSDP** shards
  states; **mixed precision** halves memory. Climb the ladder only as needed.
- **Tuning:** grid < random < Bayesian; **Hyperband** early-stops losers.
- **Transfer learning:** pretrain once on generic data, freeze early layers,
  fine-tune the rest on little data (LoRA/adapters for cheap adaptation).

---

## Module 6 — Flash Cards (Q → A)

1. Default model for tabular data? → *GBDT (XGBoost).*
2. Why compute a baseline? → *A metric is meaningless without a reference; it
   also catches bugs and leaks.*
3. Bias vs variance in one line? → *Bias = too simple (underfit); variance = too
   sensitive (overfit).*
4. L1 vs L2? → *L1 drives weights to exactly 0 (feature selection); L2 shrinks
   smoothly.*
5. Where does cross-entropy come from? → *Negative log-likelihood (MLE) of the
   labels.*
6. Learning rate too large? → *Loss overshoots / diverges.*
7. Adam in one line? → *Adaptive per-weight step size with momentum; the default.*
8. Data vs model parallelism? → *Data: full model per GPU, split the data. Model:
   split the model across GPUs (it doesn't fit).*
9. What does ZeRO/FSDP do? → *Shards weights/gradients/optimizer states across
   GPUs to fit bigger models.*
10. Random vs grid search? → *Random usually wins — only a few hyperparameters
    matter and it explores them better.*
11. Transfer learning in one line? → *Reuse a pretrained model's general features;
    fine-tune on little data.*

---

## Module 6 — Pattern Recognition (how to spot it in an interview)

- Hear **"tabular data"** → say *baseline → GBDT*, question the need for a DNN.
- Hear **"great on train, bad on test"** → say *overfitting / high variance →
  regularize, more data, less capacity.*
- Hear **"predict a probability"** → say *cross-entropy*, not MSE.
- Hear **"rank / order results"** → say *pairwise / listwise ranking loss.*
- Hear **"learn an embedding / similarity"** → say *contrastive / triplet loss.*
- Hear **"training won't fit / is too slow"** → distinguish *data vs model
  parallel*, mention *all-reduce, FSDP, mixed precision.*
- Hear **"little labelled data"** → say *transfer learning / fine-tuning.*
- Hear **"tune the model"** → say *random or Bayesian, Hyperband to early-stop*,
  and *tune the learning rate first.*

---

## Module 6 — Revision Notes / Mini Cheat Sheet

```
MODEL CHOICE:  linear -> GBDT (TABULAR default) -> deep nets (perception)
               -> transformers (language/scale).  START SIMPLE.
BASELINE FIRST: majority-class / rule / linear. Metric without baseline = useless.

BIAS-VARIANCE:  test_err = bias^2 + variance + noise
  underfit = high bias (simple)   overfit = high variance (memorises noise)
REGULARIZE:  L1 |w| -> exact zeros (feature select) | L2 w^2 -> smooth shrink
             dropout | early-stop | weight-decay | augmentation. bigger lambda=simpler

LOSSES:
  MSE       (y - yhat)^2                 regression
  Cross-ent -[y log yhat + (1-y)log(1-yhat)]   classification (= MLE!)
  Hinge     max(0, 1 - y*s)              max-margin (SVM)
  Pairwise  max(0, m - (s+ - s-))        ranking
  Contrastive y*d^2 + (1-y)*max(0,m-d)^2 embeddings

OPTIMIZE:  w <- w - eta * grad(L)
  LR too big=diverge | too small=crawl.  SGD+momentum vs ADAM(adaptive, default)

DISTRIBUTED:
  data-parallel  = full model/GPU, split DATA, all-reduce grads (model FITS)
  model-parallel = split MODEL across GPUs (tensor within layer / pipeline layers)
  ZeRO/FSDP = shard weights+grads+optim states | mixed-precision = FP16, half mem
  ladder: 1GPU+FP16 -> data-parallel -> ZeRO/FSDP -> tensor+pipeline (only as needed)

TUNING:  grid < random < Bayesian ; Hyperband early-stops losers ; tune LR first
TRANSFER: pretrain(generic, self-sup) -> freeze early layers -> fine-tune (LoRA)
```

---

> **Next module:** *Module 7 — Model Evaluation: Offline Metrics, Leakage & A/B
> Testing.* We've trained a model — but *is it actually good?* We'll pick the
> right offline metric (precision/recall, AUC, NDCG), hunt down data leakage,
> understand the offline–online gap, and design the A/B test that decides whether
> it ships.
