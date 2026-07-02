---
title: "Module 12 — Recommendation Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 12 — Recommendation Systems

> **Why this module matters so much.**
> If ML system design interviews had a "most-asked" list, recommendation would
> sit at the very top. Every large consumer company — YouTube, Netflix, TikTok,
> Instagram, Amazon, Spotify — is, at its core, a giant recommender. The question
> *"design the YouTube homepage / TikTok For-You feed / Amazon 'customers also
> bought'"* is a rite of passage. It is beloved by interviewers because it
> touches **everything** in this course at once: framing a fuzzy business goal,
> picking a metric, building features, choosing a model, and — above all —
> designing a **serving architecture that works at the scale of billions of
> items and requests**. This module builds the whole thing from first principles,
> in plain English, so you can walk into that interview and drive the
> conversation instead of being dragged through it.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★★         | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
state the recsys problem and the business metric it serves; explain
collaborative filtering (user-user and item-item) and *why* item-item scales
better; derive **matrix factorization** with its objective and know ALS vs SGD;
contrast content-based, collaborative, and hybrid approaches; draw and defend the
**two-stage candidate-generation → ranking** architecture (the single most
important picture in the module); explain **two-tower** retrieval with ANN
lookup; name what **Wide & Deep, DeepFM, DLRM, DCN** each add; describe
**sequential** models (GRU4Rec, SASRec); handle **cold start** for users and
items; reason about **exploration vs exploitation** (bandits); and run a full
7-step design of "recommend videos" end to end.

> **How to read this module.** As always: **problem → simplest attempt → why it
> breaks → the fix.** Recommendation is the perfect subject for this because each
> classic idea (CF → matrix factorization → two-tower → two-stage) is literally
> the fix for the previous one's scaling wall.

---

## 12.1 The Recommendation Problem & Business Framing

### Motivation (the problem that exists)

A user opens an app. There are **millions** of things they *could* be shown —
videos, products, songs, posts. The screen fits maybe ten. Which ten? Showing
the wrong ten wastes the single most valuable thing the company has: the user's
attention. Showing the right ten keeps them watching, buying, and coming back.
That is the recommendation problem: **given one user and a huge catalog, produce
a short, ordered list the user is most likely to engage with.**

![A recommender turns one user plus millions of items into a short personalized ranked list, with the goal of increasing engagement.](images/m12_01_recsys_problem.png)

As the figure above shows, the recommender sits between two very lopsided
inputs — a single user's history and context on one side, a catalog of millions
of items on the other — and squeezes them into a top-N list. Everything hard
about recsys comes from that asymmetry of scale.

### Definition

- A **recommendation system** predicts, for a given user and context, how much
  the user will like (click, watch, buy, save) each candidate item, and returns
  the highest-scoring items as a ranked list.
- The **feedback** we learn from is usually **implicit** (clicks, watch time,
  purchases) rather than **explicit** (1–5 star ratings). Implicit feedback is
  abundant but noisy — a click is not the same as "liked it".

### Business framing (why it is worth billions)

Recsys is never optimised for its own sake; it exists to move a **business
metric**:

| Company | The list they recommend | The business metric it drives |
|---------|-------------------------|-------------------------------|
| YouTube | Home feed, "Up next" | Watch time / sessions |
| Netflix | Rows of titles | Retention (fewer cancellations) |
| Amazon | "Customers also bought" | Revenue per visit |
| TikTok | For-You feed | Time spent, session length |
| Spotify | Discover Weekly | Engagement, subscription retention |

> **Senior signal:** open a recsys interview by naming the *business* objective
> and the *proxy* you will actually optimise (e.g. "long-term retention, proxied
> by expected watch time per session"). Juniors jump straight to "matrix
> factorization"; seniors first pin down *what good means*.

### First-principles: why not just show the most popular items?

The simplest baseline is **"show everyone the globally most popular items."** It
is not personalised at all, but it is a real, strong baseline you should always
mention. It breaks because tastes differ wildly, popular-only creates a rich-get-
richer **feedback loop** (Module 1), and it ignores the long tail where most of
the catalog's value hides. Personalisation is the fix — and the rest of this
module is how to personalise at scale.

---

## 12.2 Collaborative Filtering (User-User & Item-Item)

### Motivation

How do you personalise *without* knowing anything about what the items actually
*are*? The insight of **collaborative filtering (CF)** is beautiful: you do not
need to understand the items or the users — you only need the **matrix of who
interacted with what.** "People who behaved like you, liked this" is enough.

![Collaborative filtering has two flavours: user-user finds similar users and recommends what they liked; item-item finds items similar to ones you liked. Both use only the interaction matrix.](images/m12_02_collaborative_filtering.png)

### The two flavours (see the figure above)

- **User-user CF.** Find users whose past behaviour is similar to mine (e.g. by
  cosine similarity of their rating rows), then recommend items *they* liked that
  I have not seen. Intuitive, but users are many and their tastes shift fast, so
  similarities must be recomputed constantly.
- **Item-item CF.** Find items that tend to be liked by the same people as the
  items I already liked, and recommend those. Amazon's famous "customers who
  bought X also bought Y" is item-item CF.

### First-principles: why item-item usually wins at scale

Item-item CF is the workhorse of classic recsys for two reasons the figure
hints at:

1. **Stability.** Item-item similarities change slowly (the relationship between
   two movies is stable), while a user's taste vector shifts daily. So you can
   **precompute** an item-item similarity table offline and reuse it.
2. **Scale.** There are usually far fewer *distinct behaviours per item* to
   compare than users, and the item catalog is more stable, making the
   neighbourhood computation cheaper and cacheable.

### How similarity is computed

Represent each item as its **column** in the user-item matrix (who interacted
with it). Similarity between items $i$ and $j$ is typically **cosine
similarity**:

$$ \text{sim}(i, j) = \frac{\mathbf{r}_i \cdot \mathbf{r}_j}{\lVert \mathbf{r}_i \rVert \, \lVert \mathbf{r}_j \rVert} $$

To score item $j$ for user $u$, take a similarity-weighted sum of that user's
ratings on items similar to $j$.

### Where plain CF breaks

- **Sparsity.** The matrix is >99% empty; most user-item pairs have no signal.
- **Cold start.** A brand-new user or item has no row/column at all (Section
  12.9).
- **No content.** CF cannot use the fact that two movies share a director — it
  only sees co-interaction. The fix for sparsity and scale is **matrix
  factorization**, next.

---

## 12.3 Matrix Factorization (with the Math)

### Motivation

Neighbourhood CF stores a giant, sparse similarity table and struggles with
sparsity. **Matrix factorization (MF)** — made famous by the Netflix Prize —
replaces that with something far more compact and powerful: it **learns a small
dense vector for every user and every item** such that their dot product
reconstructs the ratings. This is the birth of **embeddings** in recsys.

![Matrix factorization approximates the sparse rating matrix R as the product of a small user-vector matrix U and item-vector matrix V-transpose; a predicted rating is the dot product of a user and item vector.](images/m12_03_matrix_factorization.png)

### The setup (see the figure above)

We have a rating matrix $R$ of shape (users × items), mostly empty. We
approximate it as a product of two thin matrices:

$$ R \approx U V^{\top} $$

where $U$ has one **latent vector** $\mathbf{u}_i \in \mathbb{R}^k$ per user, and
$V$ has one latent vector $\mathbf{v}_j \in \mathbb{R}^k$ per item. Here $k$ (the
number of latent factors) is small, e.g. 32–256. The predicted rating is just a
**dot product**:

$$ \hat{r}_{ui} = \mathbf{u}_i \cdot \mathbf{v}_j = \sum_{f=1}^{k} u_{if}\, v_{jf} $$

Intuitively, each of the $k$ dimensions is a hidden "taste axis" (how much
comedy, how much action…) learned automatically. If a user's vector and an
item's vector point the same way, the dot product is large → strong
recommendation.

### The objective (what we minimise)

We fit the vectors so predictions match the *observed* ratings, plus an L2
**regularisation** term to prevent overfitting:

$$ \min_{U,V} \sum_{(u,i)\,\in\,\text{observed}} \left( r_{ui} - \mathbf{u}_i \cdot \mathbf{v}_j \right)^2 \; + \; \lambda \left( \lVert \mathbf{u}_i \rVert^2 + \lVert \mathbf{v}_j \rVert^2 \right) $$

Notice we sum **only over observed entries** — we do not try to fit the empty
cells. In practice we also add **bias terms** (a global average, a per-user bias,
a per-item bias) because some users rate high and some items are universally
loved: $\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{u}_i \cdot \mathbf{v}_j$.

### How we optimise it: ALS vs SGD

Two standard algorithms fit these vectors:

- **ALS (Alternating Least Squares).** Fix all item vectors, and the objective
  becomes a plain **least-squares** problem in the user vectors that has a closed-
  form solution — solve for all users. Then fix the users and solve for the
  items. Alternate until convergence. ALS is easily **parallelised** (each
  user/item solves independently) and is the classic choice for **implicit
  feedback** at scale (Spark MLlib uses it).
- **SGD (Stochastic Gradient Descent).** Loop over observed ratings; for each,
  nudge $\mathbf{u}_i$ and $\mathbf{v}_j$ down the gradient of the squared error.
  Simpler, more flexible (easy to add biases, custom losses), and the default
  when the model is part of a larger deep network.

### Implicit feedback twist

With clicks/watches (not star ratings) there are no explicit negatives — a
non-click might mean "disliked" *or* "never saw it". The standard fixes:
treat interactions as **confidence-weighted positives** (implicit-ALS, Hu et al.
2008) or train with a **ranking loss** like BPR (Bayesian Personalized Ranking)
that just says "observed items should rank above unobserved ones."

> **Key takeaway.** MF's dot-product-of-embeddings idea is the seed of everything
> modern: the two-tower retrieval model (Section 12.6) is literally "matrix
> factorization where the vectors are produced by neural networks instead of
> looked up."

---

## 12.4 Content-Based Filtering & Hybrid Systems

### Motivation

CF and MF share a blind spot: they know *nothing about the items themselves*.
A brand-new movie with zero views is invisible to them. **Content-based
filtering** fixes this by recommending items whose **features** resemble those
the user already liked.

![Content-based filtering uses item features and matches them to a user's past likes; collaborative filtering uses the interaction matrix; a hybrid combines both.](images/m12_04_content_vs_hybrid.png)

### Content-based filtering

Describe each item by features: genre, tags, text embeddings of the description,
audio features (for music), the creator, etc. Build a **user profile** as an
aggregate of the features of items they liked. Then recommend items whose feature
vector is close to that profile. Because it depends only on item content, it
**works for brand-new items** (no interactions needed) — this is its superpower.

**Weaknesses:** it stays inside the user's existing bubble (over-specialisation,
poor **serendipity**), and it needs good item features to work at all.

### Hybrid systems (what real products actually use)

As the figure shows, the two families are complementary: content-based handles
cold items and explainability; collaborative captures crowd wisdom and
serendipity. **Hybrids** combine them. Common recipes:

- **Weighted / switching:** blend or choose between the two scores depending on
  how much interaction data exists (use content when cold, CF when warm).
- **Feature fusion:** feed *both* interaction embeddings *and* content features
  into one model — this is exactly what modern deep recommenders (Section 12.7)
  and two-tower models (Section 12.6) do. The towers take content features **and**
  learned ID embeddings.

> **Interview line:** "Nearly every production recommender is a hybrid — the two-
> tower retrieval model already fuses content features with ID embeddings, which
> is why it degrades gracefully on cold items."

---

## 12.5 The Two-Stage Architecture (the Centrepiece)

### Motivation — the scaling wall

Here is the crux of real-world recsys. Suppose you have the world's best ranking
model — a deep network that, given a (user, item) pair, predicts engagement very
accurately. The naive plan is: **score every item for the user, sort, take the
top ten.** With a catalog of tens of millions of items and a latency budget of
tens of milliseconds, this is **completely impossible** — you cannot run a heavy
neural network millions of times per request. This wall is what forces the
industry-standard design.

![The two-stage recommender: a catalog of millions goes through Stage 1 candidate generation which is fast and cheap and returns hundreds, then Stage 2 ranking which is a heavy accurate DNN and returns tens, then the top-N goes to the user.](images/m12_05_two_stage.png)

### The fix: a funnel with two stages

As the centrepiece figure shows, we split the work into two stages with very
different jobs:

- **Stage 1 — Candidate Generation (Retrieval).** Cheaply and quickly reduce
  **millions → hundreds**. Optimise for **recall** (don't miss good items), not
  precision. Techniques: **two-tower ANN lookup** (Section 12.6), item-item
  co-visitation, popularity, freshly-uploaded, "from creators you follow", etc.
  Often **several candidate sources** are unioned together. Each source is a
  cheap approximation; the ranker sorts out the details.
- **Stage 2 — Ranking.** Take those few hundred candidates and score each one
  **precisely** with a heavy model using **rich features** (full user history,
  item features, context, cross features). Optimise for **precision at the top**.
  Because it only runs on hundreds of items, we can afford a big DNN.

Some systems add a third **re-ranking** stage for business rules: diversity,
freshness, fairness, "don't show three videos from the same channel in a row",
and de-duplication.

### First-principles: why the split works

The numbers on the arrows tell the story: **millions → ~hundreds → ~tens.**

- The expensive-per-item model (ranking) only ever sees **hundreds** of items, so
  its cost is bounded regardless of catalog size.
- The cheap-per-item step (retrieval) can scan the whole catalog because its
  per-item cost is tiny (a nearest-neighbour lookup, or a table read).
- The two stages optimise **different metrics** on purpose: retrieval maximises
  recall (cast a wide net); ranking maximises precision (put the best on top).

> **This is the single most important diagram to reproduce in an interview.**
> When asked to "design YouTube recommendations," draw the funnel first and label
> the item counts. It instantly signals you understand production recsys, not
> just textbook MF.

---

## 12.6 Two-Tower / Dual-Encoder Retrieval

### Motivation

Stage-1 retrieval needs to find "items relevant to this user" among millions, in
milliseconds. The **two-tower model** (also called dual-encoder) makes this a
**nearest-neighbour search** in an embedding space — the modern, learned way to
do candidate generation.

![The two-tower model: a user tower encodes user and context features into a user vector, an item tower encodes item features into an item vector, and their dot product is the similarity score. Item vectors are precomputed into an ANN index.](images/m12_06_two_tower.png)

### The architecture (see the figure above)

There are two separate neural networks ("towers"):

- The **user tower** takes user + context features (history, location, time,
  device) and outputs a **user embedding**.
- The **item tower** takes item features (ID, category, content) and outputs an
  **item embedding**.
- The **score** is the dot product (or cosine) of the two embeddings — exactly
  like matrix factorization, but the vectors are *computed by neural nets* rather
  than looked up, so they generalise to new items and use rich features.

Training uses **in-batch negatives**: for a batch of positive (user, item) pairs,
every *other* item in the batch serves as a negative, and a softmax/contrastive
loss pushes each user close to its true item and away from the rest.

### Why the towers are kept separate (the key trick)

Because the item embedding depends **only** on item features and the user
embedding **only** on user features, we can:

1. **Precompute all item embeddings offline** and load them into an **ANN index**
   (Approximate Nearest Neighbour — e.g. FAISS, ScaNN, HNSW).
2. At request time, run the **user tower once** to get the user vector, then ask
   the ANN index for the **k nearest item vectors** in sub-millisecond time.

This is what makes retrieval over millions of items feasible. Contrast this with
a model that mixes user and item features early (a "cross" model): it would have
to be re-run for every candidate, which is fine for *ranking* (hundreds of items)
but impossible for *retrieval* (millions). The separation is the whole point.

> **Interview tie-in:** two-tower for retrieval + a cross-feature DNN for ranking
> is the canonical modern recsys stack. Say those two sentences and you have
> covered 80% of the architecture question.

---

## 12.7 Deep Recommenders: Wide & Deep, DeepFM, DLRM, DCN

### Motivation

The **ranking** stage wants the most accurate possible score for a few hundred
candidates, so it can be a big model. The central challenge is **feature
interactions**: "this user + this time-of-day + this genre" together predict a
click far better than any feature alone. The following families are all different
answers to "how do we model feature interactions on top of embeddings?"

![Deep recommender ranking models: Wide and Deep combines memorization and generalization; DeepFM adds a factorization machine for feature pairs; DCN adds explicit crosses via a cross network; DLRM uses embeddings plus dot interactions plus an MLP. All turn sparse IDs into embeddings then learn interactions.](images/m12_07_deep_recommenders.png)

### What each one adds (see the figure above)

- **Wide & Deep (Google, 2016).** Two parts trained jointly: a **wide** linear
  model over crossed features that **memorises** specific combinations ("users who
  installed app A also install app B"), and a **deep** network over embeddings
  that **generalises** to unseen combinations. The insight: you want both
  memorisation *and* generalisation.
- **DeepFM (2017).** Replaces the hand-engineered wide crosses with a
  **Factorization Machine** component that automatically models **all pairwise
  feature interactions** via embedding dot products, sharing embeddings with the
  deep part. No manual feature crossing needed.
- **DCN — Deep & Cross Network (2017, v2 2020).** Adds a **cross network** that
  explicitly and efficiently computes **higher-order feature crosses** layer by
  layer, alongside a deep network. More expressive crosses than FM's pairwise.
- **DLRM — Deep Learning Recommendation Model (Meta, 2019).** The industrial
  workhorse: turn categorical IDs into **embeddings**, model interactions via
  **explicit pairwise dot products** between embeddings, then feed through an
  **MLP**. Designed for enormous embedding tables sharded across many machines.

The common thread, stated at the bottom of the figure: **all of them turn sparse
categorical IDs into dense embeddings, then learn how features interact** — they
just differ in the mechanism (manual crosses, FM, cross-network, dot
interactions).

> **What to say:** "For ranking I'd start with a DLRM/DCN-style model — embeddings
> for the sparse IDs, an interaction layer, and an MLP head — trained on
> click/watch logs with a ranking or logistic loss." That is a precise, credible
> answer.

---

## 12.8 Sequential / Session-Based Recommendation

### Motivation

Everything so far ignores **order and recency**. But what you watched *just now*
matters enormously — after three cooking videos, the next recommendation should
probably be cooking, not last month's favourite genre. **Sequential models**
treat a user's recent actions as an ordered sequence and predict the **next
item**.

![Sequential recommendation: a sequence of recent items feeds a model (GRU4Rec, SASRec, or BERT4Rec) that predicts the next item; it uses the order of recent actions and helps with cold users.](images/m12_08_sequential.png)

### The models (see the figure above)

- **GRU4Rec (2016).** An **RNN** (GRU) that reads the session item-by-item and
  predicts the next click. First big "session-based" model; great when you have no
  long-term profile (a logged-out user, a fresh session).
- **SASRec (2018).** A **self-attention / transformer** over the item sequence.
  Attention lets the model decide **which past items matter most** for the next
  action — usually stronger and more parallelisable than RNNs.
- **BERT4Rec (2019).** Like SASRec but trained with a **masked-item** objective
  (predict a hidden item using items on both sides), borrowing BERT's bidirectional
  trick.

### Why it helps cold and returning users

Sequential models shine for **session/cold users** because they need only the
current session, not a long history. They also capture **short-term intent**
(the user is shopping for a laptop *right now*) that a static profile misses.
This is a big part of why the **TikTok For-You feed** feels so responsive — it
reacts to your last few swipes almost immediately.

---

## 12.9 Cold Start (User & Item)

### Motivation

Collaborative methods need history. But every system constantly gets **new users**
(no interactions) and **new items** (no one has seen them). The **cold-start
problem** is how you make good recommendations with zero collaborative signal — a
guaranteed interview follow-up.

![Cold start strategies: for a new user, ask onboarding preferences, use profile and context features, or show popular items; for a new item, use content features, similar-item embeddings, or explore by showing it to some users.](images/m12_09_cold_start.png)

### Strategies (see the figure above)

**New user (no history):**

- **Onboarding preferences** — ask a few "pick genres you like" questions.
- **Context / profile features** — country, device, language, signup source; a
  content-based or context model works with zero clicks.
- **Popularity fallback** — show trending items until enough signal accumulates.
- **Sequential model** — start personalising from the very first session click.

**New item (no interactions):**

- **Content features** — the item tower embeds it from its metadata/text/thumbnail,
  so a two-tower model can retrieve it immediately.
- **Similar-item embedding** — place it near similar known items in latent space.
- **Exploration** — deliberately show it to a slice of users to gather signal (see
  bandits, next).

> **Senior signal:** note that pure MF/CF *cannot* handle cold items at all
> (no column exists), which is a core reason production systems use **feature-based
> two-tower / content-hybrid** models rather than plain MF. Connecting the cold-
> start requirement to the architecture choice is the mark of a strong answer.

---

## 12.10 Exploration vs Exploitation (Bandits)

### Motivation

Recsys has a nasty **feedback loop** (Module 1): you only ever collect data on
items you **choose to show**. If you always show the current best guesses
(**exploit**), you never learn whether the items you *didn't* show are actually
better — and new/niche items never get a chance. You must sometimes **explore**.

![Exploration vs exploitation: exploit shows known winners for safe engagement, explore tries uncertain items to learn their value; bandits (epsilon-greedy, UCB, Thompson sampling) balance both.](images/m12_10_bandit.png)

### The trade-off (see the figure above)

- **Exploit** = show items you are confident about → safe short-term engagement.
- **Explore** = show uncertain items → learn their true value, surface fresh and
  long-tail content, and avoid a stale **filter bubble**.

Too much exploit → the system ossifies and the catalog's tail dies. Too much
explore → you annoy users with irrelevant items. The right answer is a
principled **balance**.

### Bandit algorithms

- **ε-greedy** — exploit the best item with probability $1-\varepsilon$, pick a
  random item with probability $\varepsilon$. Simple, effective.
- **UCB (Upper Confidence Bound)** — pick the item with the highest *optimistic*
  score (mean + uncertainty bonus); naturally tries under-explored items.
- **Thompson sampling** — keep a probability distribution over each item's value,
  sample from it, and show the sampled winner; explores in proportion to
  uncertainty.
- **Contextual bandits** — the reward depends on the user's context (features), so
  the model learns *per-context* which arm to pull. This is how many news/feed
  systems handle fresh content.

> **Interview tie-in:** connect this back to the feedback-loop danger from Module
> 1 — exploration is how you *break* a harmful popularity loop and keep the
> flywheel healthy.

---

## 12.11 Real Systems (How the Giants Do It)

Grounding the theory in real designs is a strong interview move. Know these at a
one-paragraph level.

- **YouTube (two-stage deep recommender, 2016 paper).** The canonical two-stage
  design: a **candidate-generation** DNN retrieves a few hundred videos from
  millions (treated as extreme multiclass, then approximate nearest neighbour),
  then a **ranking** DNN scores them with rich features, optimising **expected
  watch time** (not just clicks — clickbait gets clicks but low watch time).
- **Netflix.** Famous for the Netflix Prize (MF), but production is a hybrid of
  many models producing **personalised rows**; they optimise **retention** and
  even personalise **artwork/thumbnails**. Ranking is row-by-row and page-level.
- **TikTok "Monolith".** A recommendation system built for **real-time**,
  **collisionless** embedding tables with **online training** — the model updates
  from fresh interactions almost immediately, which is why the For-You feed adapts
  to your swipes so fast. Heavy use of sequential signals.
- **Instagram / Meta.** Multi-stage ranking (retrieval → first-pass light ranker →
  heavy ranker → re-ranking for diversity/integrity), **multi-task** models
  predicting several engagement events (like, comment, save, time) and combining
  them into one value score. DLRM-style ranking at massive scale.
- **Spotify.** Hybrid: collaborative filtering on listening logs + **content**
  (audio analysis, NLP on playlists/reviews) — Discover Weekly blends CF with
  content and sequence. Content signals are crucial for cold tracks.

> **Pattern:** every one of these is a **multi-stage funnel** (retrieval →
> ranking → re-ranking), uses **embeddings**, is increasingly **multi-task** and
> **real-time**, and optimises a **long-term** engagement/retention metric via
> short-term proxies. That sentence is your executive summary of modern recsys.

---

## 12.12 Worked Mini-Design — "Recommend Videos" (7-Step Framework)

Let us run the **7-step framework from Module 2** (Clarify → Frame → Metrics →
Data & Features → Model → Serve → Monitor) end to end on a YouTube-style "what to
watch next" system. This is the payoff of the whole module.

**Step 1 — Clarify requirements.**
*Functional:* show a personalised home feed of ~20 videos and an "Up next"
list. *Non-functional:* catalog ~ hundreds of millions of videos; ~billions of
users; **p99 latency < ~100 ms** end to end; huge QPS; fresh (react within a
session); must handle cold users and freshly-uploaded videos. Clarify the
**business goal:** long-term user satisfaction and retention.

**Step 2 — Frame as an ML problem.**
It is a **ranking** problem: score candidate videos by expected engagement and
return the top-N. Frame the target as **expected watch time** (weighted), not raw
clicks, to avoid clickbait. Multi-task heads (P(click), P(watch>30s), P(like))
combined into one score is the modern framing.

**Step 3 — Define metrics.**
*Offline:* ranking metrics — **NDCG**, recall@k for retrieval, AUC/logloss for the
ranker. *Online (the real test):* **watch time per session**, session count,
day-7 retention, measured with an **A/B test**. Guardrails: diversity, and
integrity metrics. Note the **offline-online gap** (Module 7): improve offline
NDCG only ships if the online metric moves.

**Step 4 — Data & features.**
*Data:* interaction logs (impressions, clicks, watch time, likes, skips) — mostly
**implicit** feedback; log both positives and shown-but-not-clicked negatives.
*Features:* user (watch history embeddings, demographics, context: time, device),
item (video ID embedding, channel, topic, age, thumbnail/text embeddings), and
**cross** features. Beware **training-serving skew** and **leakage** (Modules 5,
7) — compute features the same way offline and online.

**Step 5 — Model & training.**
Adopt the **two-stage** design:
- *Retrieval:* a **two-tower** model → precompute item embeddings into an **ANN
  index**; add extra candidate sources (subscriptions, trending, sequential
  next-item) and union them. Handles cold items via content features.
- *Ranking:* a **DLRM/DCN-style deep model** with multi-task heads over the few
  hundred candidates, trained on logged engagement with a ranking/logistic loss.
- *Re-ranking:* apply diversity, freshness, and dedup rules.
Add a **bandit/exploration** slice for fresh content and cold items.

**Step 6 — Serving & scaling.**
Item embeddings and popularity are **precomputed in batch**; the ANN index and
feature store are read at request time; the ranker runs **online** on hundreds of
candidates behind a gRPC service under the latency budget. **Cache** user
embeddings and popular candidates. This is a **hybrid batch + online** design
(Module 1) — heavy lifting precomputed, final decision fresh.

**Step 7 — Monitor & iterate.**
Watch for **drift** (Module 10), the health of the **feedback loop** (is the
system collapsing into a popularity bubble?), online metrics, and cold-start
coverage. Retrain the ranker frequently (even continuously, TikTok-style),
refresh item embeddings, and A/B test every change. This closes the loop.

> **Why this answer scores well:** it names the business metric first, uses a
> proxy (watch time) instead of clicks, draws the two-stage funnel, picks a
> concrete model per stage, connects each choice to a non-functional requirement,
> and plans the feedback loop. That is a Staff-level answer.

---

## Module 12 — Interview Mapping (what companies probe)

| Company | How Module 12 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **YouTube / Google** | "Design video recommendations" | One big ranking model over all videos | Two-stage funnel, watch-time objective, two-tower retrieval + deep ranker |
| **Meta (IG/FB)** | "Design the feed / reels ranking" | Single-task CTR model | Multi-stage, multi-task ranking, value model combining events, integrity/diversity re-rank |
| **Amazon** | "Customers who bought X…" | "Use collaborative filtering" | Item-item CF for stability + embeddings, connects to revenue and cold items |
| **TikTok / ByteDance** | "Why is For-You so fast?" | "Good model" | Real-time online training, sequential signals, exploration for fresh content |
| **Netflix / Spotify** | "Design recommendations / Discover Weekly" | MF only | Hybrid CF+content, retention metric, cold-start via content, personalised rows |

**The single most common opening question:** *"Design the recommendation system
for X."* Your first 90 seconds should: (1) name the **business metric** and a
sensible **proxy**, (2) sketch the **two-stage funnel** with item counts, (3) say
**two-tower retrieval + deep ranker**. That structure alone puts you ahead of most
candidates.

---

## Module 12 — Exam Mapping (SEBI / RBI / GATE / ISRO)

> **Flag: this is an interview-heavy, exam-light module.** Recommendation *system
> design* is essentially **interview-only** and rarely appears on written
> government/academic exams.

- **SEBI IT / RBI IT:** at most a definitional mention of "recommendation system"
  or collaborative filtering; the architecture material here is not tested.
- **GATE CS / DA:** the DA paper may touch **collaborative filtering** and the
  idea of **matrix factorization / latent factors** at a conceptual level, and
  cosine similarity. Two-stage serving and deep recommenders are not exam
  material.
- **ISRO / DRDO:** occasional one-line ML definitions only.

The **exam-transferable** ideas are the general ones — cosine similarity, the
notion of embeddings/latent factors, and the exploration-exploitation trade-off
(which overlaps reinforcement-learning basics).

---

## Module 12 — Common Mistakes & Misconceptions

1. **"Just score every item and sort."** Impossible at scale — you must use the
   **two-stage funnel**. This is the number-one thing juniors miss. (Section 12.5.)
2. **"Optimise clicks."** Clicks reward clickbait. Optimise a **quality proxy**
   like watch time / long-term engagement. (Sections 12.1, 12.12.)
3. **"Matrix factorization is state of the art."** MF is the *foundation*; modern
   systems use **two-tower retrieval + deep ranking** and feature-based models.
4. **"CF handles new items."** Pure CF/MF **cannot** — no column exists. Cold items
   need **content features** or exploration. (Sections 12.4, 12.9.)
5. **"One model does everything."** Retrieval and ranking optimise **different
   metrics** (recall vs precision) and use **different architectures** (separated
   towers vs early feature crosses). (Sections 12.5, 12.6.)
6. **"Always exploit the best predictions."** Ignoring **exploration** creates a
   filter bubble and starves the long tail (a harmful feedback loop). (Section
   12.10.)
7. **"Offline NDCG going up means we ship."** Only the **online A/B** business
   metric decides — mind the offline-online gap. (Section 12.12.)

---

## Module 12 — MCQs (with answers & explanations)

**Q1.** Why do large recommenders use a two-stage (candidate generation →
ranking) architecture?
a) To use two different programming languages
b) Because running a heavy ranking model over millions of items per request is
   too slow and costly
c) Because collaborative filtering needs it
d) To store more data

<details><summary>Answer</summary>**b.** Retrieval cheaply cuts millions to
hundreds (optimising recall); the expensive ranker then runs only on those
hundreds (optimising precision), keeping cost bounded regardless of catalog
size.</details>

**Q2.** In matrix factorization, the predicted rating for user $u$ and item $i$
is:
a) the cosine of their raw rating rows
b) the dot product of their learned latent vectors
c) the global average rating
d) the number of items they share

<details><summary>Answer</summary>**b.** $\hat{r}_{ui} = \mathbf{u}_i \cdot
\mathbf{v}_j$ — the dot product of the user's and item's $k$-dimensional latent
vectors (optionally plus bias terms).</details>

**Q3.** Why can the two-tower model retrieve from millions of items in
milliseconds?
a) It scores every item with a big DNN
b) Item embeddings are precomputed into an ANN index, so serving is a fast
   nearest-neighbour lookup after embedding the user once
c) It uses SQL joins
d) It caches the final answer for all users

<details><summary>Answer</summary>**b.** Because the towers are separate, item
vectors depend only on item features and can be precomputed into an approximate-
nearest-neighbour index; only the user tower runs per request.</details>

**Q4.** Which method can recommend a brand-new item with zero interactions?
a) User-user collaborative filtering
b) Plain matrix factorization
c) Content-based / feature-based (e.g. an item tower using metadata)
d) Item-item co-visitation counts

<details><summary>Answer</summary>**c.** Only content/feature-based methods work
with no interaction history; CF and MF have no row/column for the new item (the
cold-start problem).</details>

**Q5.** What does the "exploration" side of the exploration-exploitation
trade-off buy you?
a) Lower latency
b) Learning the value of items you are unsure about and avoiding a filter bubble
c) Smaller models
d) Guaranteed higher short-term clicks

<details><summary>Answer</summary>**b.** Exploration gathers data on uncertain /
fresh items so the system can improve and surface long-tail content; it may cost
short-term engagement but prevents a harmful popularity loop.</details>

**Q6.** Between user-user and item-item CF, why is item-item usually preferred at
scale?
a) Items have more features
b) Item-item similarities are more stable over time and can be precomputed and
   cached
c) Users are more numerous than items always
d) It needs no data

<details><summary>Answer</summary>**b.** Item relationships change slowly, so the
item-item similarity table can be computed offline and reused, unlike fast-
shifting user tastes.</details>

**Q7.** In the YouTube-style design, why optimise **watch time** rather than
**clicks**?
a) Clicks are hard to log
b) Clicks reward clickbait; watch time better reflects genuine satisfaction
c) Watch time is easier to predict
d) There is no difference

<details><summary>Answer</summary>**b.** A click-only objective rewards
misleading thumbnails/titles that get clicks but low satisfaction; expected
watch time is a better proxy for the real goal.</details>

**Q8.** What do Wide & Deep, DeepFM, DCN, and DLRM all have in common?
a) They are retrieval models
b) They turn sparse categorical IDs into embeddings and then model feature
   interactions
c) They avoid neural networks
d) They require star ratings

<details><summary>Answer</summary>**b.** All are ranking-stage deep models that
embed sparse IDs and learn feature interactions; they differ only in the
interaction mechanism (manual crosses, FM, cross-network, dot interactions).</details>

---

## Module 12 — Design Exercises (easy → hard)

- **Easy.** For a small bookstore with 5,000 books and 50,000 users, would you
  build a two-stage funnel or score all items directly? Justify with the numbers.
  *(Direct scoring is fine — only 5k items; the funnel is for millions.)*
- **Easy.** Given a user-item rating matrix, write the objective that matrix
  factorization minimises, and name two ways to optimise it. *(Regularised
  squared error over observed entries; ALS or SGD.)*
- **Medium.** Design candidate generation for a music app: list three distinct
  candidate sources and why each exists (e.g. two-tower personalised, recently-
  played sequence, trending/popularity for cold users).
- **Medium.** Your recommender keeps pushing the same few viral videos and new
  creators get no views. Diagnose the feedback loop and propose an exploration
  strategy to fix it (ε-greedy vs Thompson sampling trade-offs).
- **Hard.** Design the full "For-You" feed for a short-video app that must react
  within a session. Cover: real-time features, sequential model, two-stage
  serving, freshness/exploration, and how you'd A/B test it.
- **Hard.** You must add a brand-new product category (cold items) to an
  e-commerce recommender that currently uses matrix factorization. Explain why MF
  fails and redesign the retrieval stage to handle cold items gracefully.

---

## Module 12 — Concept Review (one page)

- **The problem:** one user + millions of items → a short ranked list, to move a
  **business metric** (watch time, revenue, retention) via a **proxy** target.
- **Collaborative filtering:** learn from the interaction matrix only.
  **User-user** ("people like you") vs **item-item** ("items like this");
  item-item is more **stable & scalable** (precomputable).
- **Matrix factorization:** $R \approx UV^{\top}$; predict $\hat{r}_{ui} =
  \mathbf{u}_i\cdot\mathbf{v}_j$; minimise regularised squared error over observed
  entries via **ALS** (parallel, closed-form alternation) or **SGD**. Seed of
  **embeddings**.
- **Content-based** uses item features (handles cold items, but narrow);
  **hybrid** combines content + collaborative — what real systems use.
- **Two-stage funnel (centrepiece):** **candidate generation** (millions →
  hundreds, optimise recall) → **ranking** (hundreds → tens, heavy DNN, optimise
  precision) → optional **re-ranking** (diversity/rules).
- **Two-tower retrieval:** separate user & item towers, dot-product score; item
  vectors precomputed → **ANN lookup**; enables retrieval over millions.
- **Deep rankers:** Wide & Deep (memorise + generalise), DeepFM (auto pairwise),
  DCN (explicit crosses), DLRM (embeddings + dot interactions + MLP) — all model
  **feature interactions**.
- **Sequential:** GRU4Rec (RNN), SASRec/BERT4Rec (transformers) predict the
  **next item** from recent actions — great for cold/session users.
- **Cold start:** users → onboarding/context/popularity; items → content
  features/similar-item/exploration. Pure CF/MF can't do cold items.
- **Exploration vs exploitation:** bandits (ε-greedy, UCB, Thompson) break the
  feedback loop and surface the long tail.
- **Real systems** are all **multi-stage, embedding-based, increasingly multi-task
  & real-time**, optimising long-term engagement.

---

## Module 12 — Flash Cards (Q → A)

1. Recsys problem in one line? → *One user + millions of items → short ranked
   list that moves a business metric.*
2. User-user vs item-item CF? → *Similar users' likes vs similar items; item-item
   is more stable and precomputable.*
3. MF prediction formula? → *$\hat{r}_{ui} = \mathbf{u}_i \cdot \mathbf{v}_j$ (dot
   product of latent vectors).*
4. ALS vs SGD? → *ALS: alternate closed-form least squares (parallel); SGD:
   gradient step per observed rating.*
5. Why two stages? → *A heavy model can't score millions per request; retrieve
   cheaply (recall) then rank precisely (precision).*
6. Why keep two towers separate? → *Item vectors precompute into an ANN index →
   fast nearest-neighbour retrieval.*
7. What do Wide&Deep / DeepFM / DCN / DLRM share? → *Embed sparse IDs, then model
   feature interactions.*
8. Cold item fix? → *Content/feature-based (item tower) + exploration; pure CF
   can't.*
9. Why explore? → *Break the feedback loop, learn uncertain items, surface the
   long tail.*
10. Why watch time over clicks? → *Clicks reward clickbait; watch time proxies
    real satisfaction.*

---

## Module 12 — Pattern Recognition (how to spot it in an interview)

- Hear **"design recommendations for X"** → business metric + proxy → **two-stage
  funnel** → two-tower retrieval + deep ranker.
- Hear **"millions of items, tight latency"** → say **candidate generation +
  ANN**, not "score everything".
- Hear **"brand-new items / creators"** → **cold start**: content features +
  exploration.
- Hear **"our recs keep showing the same popular stuff"** → **feedback loop**;
  add **exploration / bandits** and diversity re-ranking.
- Hear **"react within the session / real-time"** → **sequential model** +
  online training + hybrid serving.
- Hear **"which model for ranking?"** → **DLRM/DCN-style** deep model with
  embeddings and feature interactions, multi-task heads.
- Hear **"how do you measure success?"** → offline NDCG/recall but **online A/B on
  the business metric** decides.

---

## Module 12 — Revision Notes / Mini Cheat Sheet

```
RECSYS  =  one user + millions of items  ->  short ranked list  ->  business metric
          optimise a PROXY (watch time), not clicks (clickbait) or raw popularity

COLLABORATIVE FILTERING:  use interaction matrix only
   user-user ("people like you")  |  item-item ("items like this" - stable, cacheable)

MATRIX FACTORIZATION:  R ~= U V^T ;  r_ui = u_i . v_j  (dot of k-dim latent vectors)
   min  sum_obs (r_ui - u_i.v_j)^2 + lambda(||u||^2+||v||^2)   via ALS (parallel) or SGD
   -> births EMBEDDINGS ; implicit feedback -> confidence weights / BPR ranking loss

CONTENT-BASED: item features (handles COLD items) | HYBRID = content + collaborative

TWO-STAGE FUNNEL (centrepiece):
   catalog(millions) -> CANDIDATE GEN (recall, cheap) -> ~hundreds
                     -> RANKING (precision, heavy DNN) -> ~tens
                     -> RE-RANK (diversity/rules) -> top-N

TWO-TOWER RETRIEVAL: user tower + item tower -> dot product
   item vectors PRECOMPUTED -> ANN index (FAISS/ScaNN/HNSW) ; embed user once/request

DEEP RANKERS (all embed IDs + model feature interactions):
   Wide&Deep (memorise+generalise) | DeepFM (auto pairwise) | DCN (explicit crosses)
   | DLRM (embeddings + dot interactions + MLP)

SEQUENTIAL: GRU4Rec (RNN) | SASRec/BERT4Rec (transformer) -> predict NEXT item
COLD START: user->onboarding/context/popular ; item->content/similar/explore
EXPLORE vs EXPLOIT: epsilon-greedy | UCB | Thompson  -> break feedback loop, long tail

REAL SYSTEMS: YouTube (2-stage, watch-time) | Netflix (hybrid rows, retention)
   TikTok Monolith (real-time online train) | Meta (multi-stage multi-task) | Spotify (CF+content)
```

---

> **Next module:** *Module 13 — Search & Ranking Systems.* Recommendation and
> search are close cousins — both retrieve then rank — but search adds an explicit
> **query** and **relevance**. We will reuse the two-stage funnel and two-tower
> retrieval here, and add learning-to-rank, query understanding, and relevance
> metrics.
