---
title: "Module 17 — Flagship Case Studies"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 17 — Flagship Case Studies

> **Why this module is the capstone.**
> Everything you have learned so far — the lifecycle (M1), the 7-step framework
> (M2), framing (M3), data and features (M4–M5), training and evaluation
> (M6–M7), serving and scale (M8, M11), MLOps and monitoring (M9–M10), and the
> deep-dive systems (recommendation M12, search M13, and the rest) — was
> preparation for *this*. In a real interview you are not asked "explain BM25";
> you are asked **"design YouTube recommendations"** or **"design fraud
> detection for a payments company."** This module is a **worked-answer bank**:
> seven flagship systems designed end-to-end with the *same* 7-step skeleton,
> plus six more sketched quickly. Study these until the *shape* of a great
> answer becomes automatic. The goal is not to memorise these designs — it is to
> internalise the **pattern** so you can improvise a strong answer to a system
> you have never seen. Everything is in plain English, with concrete numbers and
> honest trade-offs.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★★     | ★★★★★       |

> **Flag — this is an interview-centric module.** Case-study design is *almost
> entirely* interview and on-the-job material. Written exams (SEBI / RBI / GATE /
> ISRO) do not ask you to design YouTube. If you are studying only for a written
> exam, skim this; if you are preparing for FAANG / AI-engineer / staff
> interviews, this is the single most practically valuable module in the course.

**What you must be able to do after this module:**
run the 7-step framework cold on *any* of these seven flagship prompts and
produce a complete, numbered answer in ~40 minutes; state the business metric,
the ML proxy, and the offline + online metrics for each; draw the serving
architecture with a latency budget per stage and a rough capacity estimate;
name the one or two *gotchas* that make each system hard (feedback loops,
delayed labels, position bias, class imbalance, leakage, hallucination); and
recognise, from the wording of a new prompt, which known pattern it is closest
to so you can reuse the right skeleton.

> **How to read this module.** Each flagship study follows the **exact same
> seven headings** so you can compare them side by side: *Clarify → Frame →
> Metrics → Data & Features → Model → Serving & Scale → Monitoring.* Read the
> first two in full, then try to *predict* the next five before reading them —
> that active recall is what builds interview fluency. We deliberately cross-link
> to M12 (recommendation), M13 (search) and M16 (LLMs/RAG & vector DBs) rather
> than repeating their theory; this module is about *assembling* what you know.

---

## 17.1 The Reusable Answer Template (Master Funnel)

### The one skeleton behind every answer

Almost every large ML product, when you squint, is the **same funnel**: a huge
pool of candidates is narrowed, in stages, into a tiny final output, under a
tight latency budget, with a feedback loop that feeds tomorrow's training data.
If you can draw this master funnel and hang the 7 steps off it, you can answer
questions about systems you have never designed.

![The master ML system funnel: raw events and a large candidate pool flow through retrieval, then ranking, then re-ranking and business rules, into a small final result shown to the user; user feedback is logged and loops back to training. The seven framework steps (clarify, frame, metrics, data/features, model, serving, monitoring) are labelled around the funnel.](images/m17_01_master_funnel.png)

The seven steps, as a checklist you say out loud at the start of every answer:

1. **Clarify** — goal, users, scale (QPS, catalogue size, users), constraints
   (latency, cost, privacy), and *scope for today*.
2. **Frame** — one concrete ML task (classification / ranking / regression /
   retrieval / generation), or a rule if ML is overkill.
3. **Metrics** — business + ML, offline + online, plus a guardrail.
4. **Data & features** — sources, labels, freshness; avoid leakage and
   training-serving skew.
5. **Model** — simple baseline first, then justify each jump in complexity.
6. **Serving & scale** — batch / online / streaming from the NFRs; the funnel
   stages; caches, ANN indexes, replicas; a capacity estimate.
7. **Monitoring** — drift, the business metric, alerting, retraining cadence,
   and the failure path (shadow, canary, kill switch, fallback).

> **Senior signal:** announce this plan in your first 30 seconds ("I'll clarify,
> frame, define metrics, then design data, model, serving and monitoring"), then
> *drive* through it, checking in at each transition. Structure alone puts you
> ahead of most candidates.

Two structural ideas recur so often they deserve names you can reuse verbatim:

- **The two-stage funnel** (retrieval → ranking): cheaply narrow millions to
  hundreds, then spend an expensive model only on those hundreds. Reused in
  recommendation (M12), search (M13), ads, feed, and RAG.
- **The hybrid batch+online split**: precompute the heavy, slow-changing parts
  offline (embeddings, candidate pools, aggregate features); compute only the
  small, fresh, per-request part online. This is how you hit millisecond
  latency at millions of QPS without a giant per-request model.

Keep these two in your pocket. Most of the seven studies below are just these
two ideas dressed in different business clothes.

---

## 17.2 Case Study 1 — YouTube Video Recommendation

> *Prompt: "Design the video recommendation system for YouTube's home feed."*
> This is the archetypal recommender. Full theory is in **M12**; here we
> *assemble* it end to end.

![YouTube recommendation architecture: user request enters a candidate generation stage (two-tower retrieval with ANN over billions of videos plus recent/subscribed/trending sources) producing a few hundred candidates, then a heavy deep ranking model scores them using user, video, and context features, then a re-ranking layer applies diversity and freshness and business rules, returning about 20 videos; watch and click events are logged back to training.](images/m17_02_youtube_reco.png)

### 1. Clarify
Goal: increase **long-term user satisfaction**, proxied by watch time and return
visits (not raw clicks — clickbait hurts retention). Users: ~2B monthly,
personalised home feed on phone/TV/web. Scale: **billions of videos**, hundreds
of thousands of requests per second at peak, catalogue growing by ~500 hours of
video *per minute*. Constraints: feed must load in a few hundred ms; must handle
brand-new videos and brand-new users (cold start). Scope for today: the home-feed
ranking pipeline, not the search box.

### 2. Frame
A **two-stage ranking / recommendation** problem. Stage A (retrieval): from
billions of videos, pick a few hundred *plausible* candidates per user. Stage B
(ranking): score those few hundred by expected satisfaction and return the top
~20. Frame the ranking target as a **multi-objective** score — predicted watch
time *and* probability of a positive engagement (like, share, not-dislike) —
because optimising clicks alone breeds clickbait.

### 3. Metrics
- **Business (online):** total watch time, daily/weekly active users, 28-day
  retention. Decided by A/B test.
- **ML (online):** live CTR, average watch time per impression, satisfaction
  survey score. Guardrails: **diversity**, **freshness** (don't only show old
  viral hits), and no increase in "reported/not-interested" rate.
- **ML (offline):** ranking metrics on logged data — **NDCG / MAP** and
  held-out watch-time regression error; retrieval **recall@k** (did the
  candidate set contain the videos the user actually watched?).

### 4. Data & Features
Logged **implicit feedback**: impressions, clicks, watch time, likes, skips,
"not interested". Features: *user* (watch history embeddings, subscribed
channels, demographics, device), *video* (topic embeddings, age, channel,
historical CTR/watch-time), *context* (time of day, device, session position).
Beware **feedback loops** (the feed only logs engagement on what it chose to
show) and **position bias** (top slots get clicked more regardless of quality) —
log the position and correct for it. Avoid leakage: never use "what the user
watched *after* this impression" as a feature.

### 5. Model
- **Baseline:** most-popular + subscribed-channel uploads. Always mention it.
- **Retrieval:** a **two-tower** model — a user tower and a video tower produce
  embeddings in the same space; nearest videos are fetched with an **ANN index**
  (M12/M13). Video embeddings are precomputed in batch; the user embedding is
  computed fresh per request.
- **Ranking:** a **deep neural network** (the DLRM/Wide-&-Deep family, M12) that
  takes hundreds of features and outputs multiple heads (watch-time, click,
  like). Combine heads into one score with tuned weights.

### 6. Serving & Scale
Classic **hybrid two-stage funnel**. Video-tower embeddings and candidate pools
are refreshed in **batch** (hourly/daily) and stored in an ANN index; retrieval
and ranking run **online** per request. Capacity sketch: at ~500k QPS, retrieval
must return in ~10–20 ms (ANN over a sharded index), ranking scores ~500
candidates with a compact model in ~30–50 ms; total feed budget a few hundred
ms. Cache per-user results for a short TTL to absorb refreshes and repeated
scrolls. Thousands of serving replicas behind load balancers; GPUs/accelerators
for the ranking model.

### 7. Monitoring
Watch the business metric (watch time, retention) and guardrails (diversity,
report rate) live. Monitor **drift** in feature distributions and in the
video mix (new formats, trends). Retrain ranking frequently (daily) and
retrieval regularly; refresh embeddings continuously so new videos are
reachable (mitigates item cold start). Failure path: if the ranker is down,
fall back to popularity + subscriptions; canary every new model on a small
traffic slice before full rollout.

> **The one gotcha to say out loud:** *feedback loops + position bias.* Naming
> these, and proposing logged-position debiasing and exploration, is the
> senior signal on any recommender.

---

## 17.3 Case Study 2 — Facebook / Instagram Feed Ranking

> *Prompt: "Design the ranking system for the Facebook/Instagram home feed."*
> Similar funnel to YouTube, but the candidates are **posts from your own
> network**, engagement is **multi-action**, and *integrity* (down-ranking bad
> content) is first-class.

![Facebook/Instagram feed ranking architecture: candidate posts are gathered from friends, followed accounts, groups, and recommended sources (inventory), a multi-task ranking model predicts probabilities of several actions (like, comment, share, hide, dwell) for each post, these are combined via a weighted value model into a single score, then integrity demotions and diversity rules re-rank the list before the final feed is shown; all interactions are logged back.](images/m17_03_feed_ranking.png)

### 1. Clarify
Goal: **meaningful engagement** and time well spent, not just raw time. Users:
billions, feed refreshed many times a day. Scale: each feed load considers
**thousands of eligible posts** (friends, follows, groups, recommended), at
huge QPS. Constraints: low-latency feed build (a few hundred ms), strong
**integrity** requirements (suppress misinformation, borderline, clickbait).
Scope: the ranking of an already-fetched candidate set.

### 2. Frame
**Multi-task ranking.** For each candidate post predict the probability of
several actions — like, comment, share, dwell/long-view, and *negative* actions
(hide, report). Combine them into a single **value score** with business-chosen
weights (a comment or share is worth more than a passive scroll; a hide is
strongly negative). This "predict many actions, then weight them" pattern is the
heart of modern feed ranking.

### 3. Metrics
- **Business (online):** meaningful interactions, sessions, retention;
  down-weighting integrity-violating content. A/B tested.
- **ML (offline):** per-action AUC / calibration for each head; ranking NDCG on
  logged sessions.
- **Guardrails:** integrity (prevalence of harmful content shown), diversity
  (not all from one author), and negative-feedback rate (hides/reports).

### 4. Data & Features
Logged engagement per (user, post) with **action types**. Features: *author↔viewer*
affinity (past interactions), *post* (type, media, age, topic embedding, early
engagement velocity), *viewer* (interests, session context), and *integrity
signals* (classifier scores for misinformation/borderline). Beware **position
bias** and **presentation bias**; log positions. Cold start for new posts:
rely on content features and author priors until engagement accrues.

### 5. Model
Baseline: reverse-chronological (an honest, real baseline — mention it). Then a
**multi-task deep network** with a shared bottom and one head per action, so the
heads share representation but predict distinct behaviours. A separate integrity
model produces demotion signals applied after scoring.

### 6. Serving & Scale
Candidates are gathered online from the social graph (fan-out) plus recommended
inventory; the multi-task model scores a few hundred–thousand candidates within
the latency budget; a re-ranking layer applies integrity demotions and diversity
(avoid many posts from one author, mix content types). Precompute expensive
embeddings and affinity features offline; compute the freshest signals (early
engagement velocity) in **streaming**. Cache candidate sets briefly.

### 7. Monitoring
Track engagement, negative feedback, and integrity prevalence live. Watch for
**drift** and for the model over-optimising a single action (e.g. chasing
comments creates outrage bait — a guardrail must catch it). Retrain frequently;
canary and shadow new value-model weightings, since re-weighting the heads can
swing the whole feed. Fallback: chronological or affinity-only ranking if the
model fails.

> **Gotcha to say out loud:** optimising one engagement signal (clicks, or
> comments) can *degrade* long-term satisfaction and integrity. The senior move
> is **multi-objective ranking with a guardrail on negative/harmful outcomes.**

---

## 17.4 Case Study 3 — Ad Click-Through-Rate (CTR) Prediction

> *Prompt: "Design the CTR prediction system for a large ad network."* This is a
> **calibrated-probability** problem: the number matters, not just the ranking,
> because it feeds an auction.

![Ad CTR prediction and auction architecture: a page/query request retrieves eligible ads, a fast CTR model predicts a well-calibrated click probability (pCTR) for each ad using user, ad, advertiser, and context features (heavy on embeddings for high-cardinality IDs), the auction ranks ads by bid times pCTR (expected value), the winning ads are shown, and click/no-click labels flow back with a delay to retrain the model.](images/m17_04_ctr_prediction.png)

### 1. Clarify
Goal: maximise long-term **ad revenue** while keeping ads relevant (bad ads hurt
the platform). The ranking rule is an auction: **expected value ≈ bid × pCTR**
(and quality). So we need a *calibrated* probability, not just an order. Scale:
enormous — millions of QPS, billions of (user, ad) pairs, very high-cardinality
categorical features (user IDs, ad IDs). Constraints: single-digit-millisecond
scoring; the auction must complete in the ad slot's tight budget. Scope: the
pCTR model that feeds the auction.

### 2. Frame
**Binary classification with calibrated probability output.** Predict P(click |
user, ad, context). Calibration is essential: if the model says 2%, clicks
should happen ~2% of the time, because that number is multiplied by the bid to
decide who wins and what they pay.

### 3. Metrics
- **Business (online):** revenue, revenue per mille (RPM), advertiser ROI,
  long-term user retention (guardrail against too many/bad ads).
- **ML (offline):** **AUC / PR-AUC** for ranking quality, and **log-loss /
  calibration (reliability curve, ECE)** for probability quality — calibration
  is as important as AUC here.
- **ML (online):** live CTR vs predicted, revenue lift in A/B.

### 4. Data & Features
Impression logs with click/no-click labels. **Delayed & biased labels** are the
central data problem: a "no click" now might become a conversion later, and you
only observe clicks on ads you *chose* to show (selection bias). Features:
*user* (history, interests), *ad* (creative, advertiser, category embeddings),
*context* (page, query, device, time), and **crossed features** (user×ad
category). High-cardinality IDs are handled with **embeddings** and hashing.

### 5. Model
Baseline: **logistic regression** with hashed cross features — historically the
industry workhorse and still a great baseline; mention it. Then the
**Wide & Deep / DeepFM / DCN / DLRM** family (M12): a wide memorised part for
seen cross-features plus a deep generalising part with embeddings. Keep the model
**small and fast** because latency and QPS dominate.

### 6. Serving & Scale
Fully **online**, per request, in a few milliseconds. Precompute and cache
embedding tables (they are huge — often sharded across a distributed parameter
store); the per-request compute is a small forward pass. Capacity: at millions of
QPS you need thousands of replicas, aggressive caching of embeddings, and an
auction service colocated with the model to avoid extra network hops.

### 7. Monitoring
Watch **calibration drift** obsessively (retrain often — hourly/daily — because
ad inventory and user behaviour shift fast), plus revenue and CTR. Monitor
feature freshness and the embedding store. Handle the **delayed-label** problem
with delayed-feedback modelling and short retrain windows. Fallback: a simpler
calibrated model or historical-CTR lookup if the main model degrades.

> **Gotcha to say out loud:** **calibration and delayed/biased labels.** Ranking
> AUC is not enough — the probability itself is consumed by the auction, so a
> mis-calibrated model directly loses money.

---

## 17.5 Case Study 4 — Fraud / Anomaly Detection

> *Prompt: "Design a fraud detection system for a payments company."* The
> defining features: **extreme class imbalance**, an **adversary** who adapts,
> and a very **asymmetric cost** of errors.

![Fraud detection architecture: an incoming transaction is enriched with real-time streaming features (velocity counts, aggregates over recent windows) and historical user/merchant features, scored by a gradient-boosted-tree/ensemble model that outputs a fraud probability, then a decision layer applies thresholds and business rules to approve, decline, or send to step-up verification or a human review queue; confirmed-fraud and chargeback labels return with a long delay to retrain.](images/m17_05_fraud_detection.png)

### 1. Clarify
Goal: **minimise fraud losses** without annoying legitimate customers (false
declines are extremely costly — lost sales and churn). Latency: score in
**tens of milliseconds**, inline with the transaction. Scale: tens of thousands
of transactions per second. Cost of errors is asymmetric and business-specific:
a missed fraud (false negative) costs the chargeback amount; a false positive
blocks a good customer. Scope: real-time transaction scoring + the decision
layer.

### 2. Frame
**Binary classification** (fraud vs legit) with a **heavily imbalanced** positive
class (often <0.1%), *or* **anomaly detection** where labelled fraud is scarce.
Usually a hybrid: supervised model on known fraud patterns + unsupervised
anomaly signals + hard rules for known-bad. The output feeds a **decision
policy** (approve / decline / step-up challenge / human review), not a raw
label.

### 3. Metrics
- **Business (online):** fraud loss ($), false-decline rate, chargeback rate,
  investigation cost.
- **ML (offline):** **PR-AUC / recall at a fixed low false-positive rate** —
  *never* accuracy (99.9% accuracy is trivial when 99.9% is legit). Precision at
  the operating threshold.
- **Guardrail:** customer-friction rate (how many good users get challenged).

### 4. Data & Features
Transaction stream + labels from chargebacks/investigations — which arrive
**weeks late**, so recent data is only partially labelled. Features are heavily
**streaming aggregates**: velocity ("# transactions from this card/device/IP in
the last 1m/1h/24h"), amount vs the user's norm, device/geo mismatch, merchant
risk. These require a real-time feature pipeline (M5). Beware leakage from
post-transaction fields.

### 5. Model
Baseline: hand-written **rules** (block if amount > X and new device) — genuinely
strong here and always deployed alongside ML. Then **gradient-boosted trees**
(XGBoost/LightGBM) — the industry default for tabular fraud — often ensembled
with an anomaly detector (isolation forest / autoencoder) for novel attacks.
Handle imbalance with class weights / focal loss / careful thresholding, not
naive oversampling that leaks.

### 6. Serving & Scale
**Online + streaming.** A stream processor (Kafka/Flink) maintains velocity
features in real time; the model scores inline in tens of ms; a decision engine
applies the threshold and routes to approve / decline / step-up / review queue.
Capacity: tens of thousands of TPS, each needing fresh aggregates — the feature
store's freshness is the bottleneck, not the model.

### 7. Monitoring
Because there is an **adversary**, drift is fast and deliberate — attackers
probe and adapt. Monitor score distributions, precision/recall on the trickle of
confirmed labels, and challenge/decline rates. Retrain often and keep a fast path
to add rules for new attack patterns. Failure path: fail *closed* (safer to
challenge than to let fraud through) for high-risk, fail *open* for low-risk to
avoid blocking everyone if the model dies.

> **Gotcha to say out loud:** **imbalance + delayed labels + adversarial drift.**
> Say "accuracy is useless here; I optimise recall at a fixed low false-positive
> rate and expect to retrain constantly against an adversary." That is the
> senior signal.

---

## 17.6 Case Study 5 — Uber / DoorDash ETA Prediction

> *Prompt: "Design the ETA (estimated time of arrival) prediction system."* A
> **regression** problem where the number is shown to users and drives dispatch —
> so bias and tail errors matter more than average error.

![ETA prediction architecture: a request (origin, destination, time) is combined with a routing engine's base travel time, real-time features (current traffic, weather, driver supply/demand, restaurant prep-time signals) and historical segment speeds, fed to a gradient-boosted / neural regression model that predicts total ETA (and its components); the prediction is shown to the user and used for dispatch, and actual delivery times flow back as labels for retraining.](images/m17_06_eta_prediction.png)

### 1. Clarify
Goal: an **accurate, well-calibrated ETA** that users trust and that dispatch can
plan on. Two sub-problems often: travel-time and (for food) prep-time. Cost of
error is asymmetric — being *late* is worse than being early (broken promise), so
the loss may be tilted. Latency: fast (tens of ms), called constantly during a
trip. Scale: high QPS, global, per-city patterns. Scope: the point-ETA model.

### 2. Frame
**Regression**: predict total minutes to arrival. Often decompose into
components (to-restaurant + prep + to-customer) and sum, or predict end-to-end.
Consider predicting a **distribution / quantiles** (e.g. p50 and p90) rather than
a single number, so the app can show a reliable range and dispatch can plan for
the tail.

### 3. Metrics
- **Business (online):** on-time rate, user satisfaction/cancellations, dispatch
  efficiency.
- **ML (offline):** **MAE / RMSE**, and crucially **quantile loss / calibration**
  and the **late-error rate** (fraction where actual ≫ predicted). Average error
  hides the painful tail.
- **Guardrail:** systematic bias per city/time (don't be chronically optimistic).

### 4. Data & Features
Historical trips with actual durations (clean, abundant labels — a nice change
from fraud). Features: route distance and the **routing engine's base time**,
*real-time traffic*, time of day / day of week, weather, **driver supply/demand**,
restaurant historical prep time and current load, historical **segment speeds**.
Real-time traffic and supply are streaming features. Watch leakage: don't use
anything only known after the trip completes.

### 5. Model
Baseline: the **routing engine's physics-based estimate** (distance ÷ typical
speed) — a strong, always-available baseline; the ML model *corrects* it. Then
**gradient-boosted trees** (great for tabular spatio-temporal data) or a neural
model; often **quantile regression** or a custom asymmetric loss that penalises
lateness more than earliness.

### 6. Serving & Scale
**Online**, low latency, backed by a real-time feature store for traffic and
supply. Precompute slow features (historical segment speeds, restaurant prep
baselines) in batch; join fresh traffic/supply online. The routing engine and the
ML correction are colocated to meet the budget. Capacity: high QPS with heavy
reuse — cache ETAs for identical/near routes for a short TTL.

### 7. Monitoring
Track MAE, late-rate, and bias **per city/segment/time** (a model can be great
globally and terrible at airport pickups at 5pm). Watch for **drift** from road
changes, events, and demand shocks. Retrain regularly and per-region. Fallback:
the routing-engine estimate if the ML correction fails — graceful and always
sane.

> **Gotcha to say out loud:** **asymmetric error and the tail.** "I'd use
> quantile/asymmetric loss and monitor late-rate and per-segment bias, because a
> chronically optimistic ETA erodes trust even if MAE looks fine."

---

## 17.7 Case Study 6 — Web Search Ranking

> *Prompt: "Design web search ranking."* The classic **multi-stage retrieval →
> ranking** funnel. Full IR theory (inverted index, BM25, learning-to-rank,
> NDCG) is in **M13**; here we assemble the whole engine.

![Web search ranking funnel: a user query is processed (tokenised, spell-corrected, expanded, embedded), then two retrieval paths run in parallel over billions of documents — a lexical inverted-index (BM25) path and a dense embedding + ANN path — producing a candidate set of a few thousand; a lightweight pre-ranker cuts to a few hundred; a heavy learning-to-rank / cross-encoder model produces the final order; a re-ranking layer applies freshness, diversity and policy before showing ten results; clicks and dwell feed back.](images/m17_07_web_search.png)

### 1. Clarify
Goal: return the **most relevant** results fast; success is the user finding what
they need (proxied by clicks with long dwell, low query reformulation). Scale:
**billions of documents**, huge QPS, sub-second (ideally <300 ms) end to end.
Constraints: freshness (news queries need minutes-old pages), spam/quality
control. Scope: the ranking pipeline given a crawled+indexed corpus.

### 2. Frame
**Multi-stage ranking / learning-to-rank.** Retrieve candidates cheaply
(lexical + semantic), then rank with a learned model. Relevance labels come from
human raters and/or click models. This is the canonical **retrieval → pre-rank →
rank → re-rank** funnel.

### 3. Metrics
- **Business (online):** successful sessions, click-with-long-dwell, low
  reformulation/abandonment rate.
- **ML (offline):** **NDCG@k** (the search metric — compute it by hand in the
  interview, M13), MAP, MRR on human-judged query-doc pairs.
- **Online:** interleaving / A/B on click and dwell; guardrail on latency and on
  showing spam/low-quality.

### 4. Data & Features
Query logs + clicks + human relevance judgments. Features: **lexical** (BM25,
term match, field matches in title/URL/anchor), **semantic** (query-doc embedding
similarity), **document quality** (PageRank-style authority, freshness, spam
score), and **user/context** (locale, personalisation, device). Handle **click
bias** (position, presentation) with a click model; don't treat a top-position
click as ground-truth relevance.

### 5. Model
Baseline: **BM25** over an inverted index — a genuinely strong, must-mention
baseline. Retrieval adds a **dense dual-encoder + ANN** path for semantic matches
BM25 misses (M13/M16). Ranking uses **learning-to-rank** — LambdaMART
(gradient-boosted trees optimising NDCG) or a neural ranker; the final re-rank
stage may use a heavy **cross-encoder** on the top few dozen for maximum
precision.

### 6. Serving & Scale
The **funnel with a latency budget per stage**: retrieval (BM25 + ANN, sharded
across the index) ~tens of ms returning a few thousand; a cheap pre-ranker cuts
to a few hundred (~10 ms); the main ranker scores those (~30–50 ms); a
cross-encoder re-ranks the top ~50 (~20 ms). Index is built **offline/batch** and
served from memory/SSD across many shards; queries only read. Cache results for
popular queries.

### 7. Monitoring
Track NDCG on fresh judgments, click/dwell/reformulation live, and **freshness
lag** (are new pages retrievable?). Monitor for **query drift** (new entities,
trending topics) and index health. Retrain the ranker regularly; rebuild/refresh
indexes continuously. Fallback: if the neural ranker fails, serve BM25 +
document-quality ordering — degraded but always sane.

> **Gotcha to say out loud:** **combine lexical and semantic retrieval, and
> debias clicks.** Pure keyword misses meaning; pure embeddings miss exact/rare
> terms and are costly — a strong answer uses **both** and treats clicks as
> biased signal, not truth.

---

## 17.8 Case Study 7 — Enterprise RAG Assistant

> *Prompt: "Design a question-answering assistant over a company's internal
> documents."* The modern **retrieval-augmented generation** system. LLM,
> embedding, vector-DB and evaluation theory is in **M16**; here we assemble a
> production RAG pipeline and its failure modes.

![Enterprise RAG architecture: offline ingestion chunks and embeds internal documents into a vector database with access-control metadata; at query time the user question is embedded and used for hybrid retrieval (vector ANN plus keyword) filtered by the user's permissions, top chunks are re-ranked, then a prompt (question plus retrieved context plus citations) is sent to an LLM which generates a grounded answer with source links; feedback (thumbs up/down, cited-source clicks) is logged for evaluation and improvement.](images/m17_08_enterprise_rag.png)

### 1. Clarify
Goal: let employees get **accurate, grounded, cited** answers from internal docs
(wikis, tickets, PDFs) instead of searching manually. Hard constraints:
**permissions** (a user must never see content they can't access), **freshness**
(docs change), **groundedness** (no hallucinations; every claim cited), and cost/
latency of LLM calls. Scale: thousands–millions of documents, moderate QPS.
Scope: the RAG pipeline, not training the base LLM.

### 2. Frame
**Retrieval + generation**, not a single model. Retrieval is a search problem
(reuse M13/M16): find the few most relevant, *permitted* chunks. Generation is an
**LLM grounded on those chunks**, instructed to answer only from context and cite
sources, and to say "I don't know" when the context is insufficient.

### 3. Metrics
- **Business (online):** answer usefulness (thumbs up/down), deflection of
  support tickets, time saved.
- **Offline (retrieval):** recall@k / precision@k of the retrieved chunks against
  question→relevant-doc pairs.
- **Offline (generation):** **faithfulness / groundedness** (does the answer stick
  to the sources?), answer correctness, and citation accuracy — often scored by
  an **LLM-as-judge** plus a human-labelled eval set (M16). Guardrail:
  hallucination rate and permission leaks (must be ~zero).

### 4. Data & Features
The corpus of internal documents, **chunked** (with overlap) and **embedded**;
each chunk carries **access-control metadata**, source, and timestamp. The
"features" are the embeddings plus keyword index plus permission tags. Ingestion
must re-embed changed docs (freshness). Beware **chunking** choices — too big
dilutes retrieval, too small loses context.

### 5. Model
- **Retrieval:** **hybrid** — dense embeddings + ANN over a **vector DB** *plus*
  keyword/BM25, filtered by the user's permissions, then a **cross-encoder
  re-ranker** on the top chunks (M16).
- **Generation:** a strong instruction-following **LLM** with a prompt that
  includes the question, the retrieved chunks, and an instruction to answer only
  from them and cite. Start with a hosted model + good prompting as the baseline
  before considering fine-tuning.

### 6. Serving & Scale
**Offline:** ingest → chunk → embed → upsert into the vector DB (batch/streaming
on doc changes). **Online:** embed query → permission-filtered hybrid retrieval
(ANN, ~tens of ms) → re-rank → assemble prompt → LLM generate (the dominant
latency, often 1–5 s). Cache embeddings and frequent Q&A. Capacity is usually
bound by **LLM cost/latency**, so retrieve tightly (few high-quality chunks) to
keep the prompt short.

### 7. Monitoring
Track thumbs up/down, groundedness, citation clicks, and — critically —
**permission-leak** incidents and **hallucination rate**. Watch retrieval recall
and freshness lag. Run a **regression eval set** on every prompt/model change
(prompts are code — version them, M16). Failure path: if retrieval returns
nothing relevant, the assistant must say "I couldn't find this" rather than
inventing an answer; guardrail models filter unsafe output.

> **Gotcha to say out loud:** **grounding, permissions, and hallucination.** The
> senior answer treats RAG as *"search + a generation head with strict
> grounding and access control"*, evaluates **faithfulness** (not just fluency),
> and never lets the LLM answer beyond the retrieved, permitted context.

---

## 17.9 Six More Systems, Briefly (Key Framing + Gotchas)

The seven flagships above cover the main *shapes*. These six show how the same
skeletons stretch to other prompts. For each: the framing in one breath, and the
one gotcha that trips candidates. Cross-links tell you which flagship/module to
borrow the full design from.

![A grid introducing six more case studies — Airbnb search / similar listings, spam and harmful-content detection, e-commerce "customers also bought", People-You-May-Know, autocomplete / typeahead, and multimodal recommendation & search — each shown as a small card with its core ML framing.](images/m17_09_brief_patterns.png)

### Airbnb search / similar listings
**Framing:** learning-to-rank over listings for a query (location + dates +
filters), *plus* a "similar listings" retrieval using **listing embeddings**.
It is the search funnel (17.7 / M13) with a **two-sided marketplace** twist:
optimise for **bookings**, and balance guest relevance with host/geographic
diversity and availability. **Gotcha:** strong **location + availability
constraints** (a listing must be free for those dates), and **seasonality**;
embeddings must capture "listings booked in the same session are similar."

### Spam / harmful-content detection
**Framing:** binary (or multi-label) **classification** of content as
spam/toxic/harmful, feeding a moderation decision (allow / demote / remove /
human review). Same skeleton as fraud (17.5): imbalance, adversary, asymmetric
cost. **Gotcha:** **adversarial drift** (attackers obfuscate — "f.r.e.e",
leetspeak, image text) and **precision/recall trade-off tied to harm severity**;
combine ML with rules and human review, and never optimise accuracy.

### E-commerce "customers also bought"
**Framing:** **item-item recommendation** (M12) — given the current item/cart,
recommend complementary items. Baseline is **co-occurrence / market-basket**
("bought together"); upgrade to item embeddings. **Gotcha:** distinguish
**complements from substitutes** (don't recommend another phone right after a
phone purchase — recommend a case), and beware **popularity bias** drowning the
long tail.

### LinkedIn / Meta "People You May Know"
**Framing:** **link prediction** on a social graph — rank candidate people by
probability of a real connection. Candidates come from **friends-of-friends** and
graph features (common connections, shared org/school, embeddings). It is the
two-stage funnel over a **graph**. **Gotcha:** **feedback loops and fairness**
(recommending only the already-popular densifies the rich), plus the classic
"met once, now haunted by suggestions" **privacy** sensitivity — be careful which
signals you use.

### Autocomplete / typeahead
**Framing:** predict the **most likely completions** of a prefix, ranked by
popularity + personalisation + recency; served from a **trie / prefix index**
with a language-model score. Extreme **latency** constraint: must respond in a
few ms *per keystroke*. **Gotcha:** it is a **latency and freshness** problem
more than a modelling one — precompute top completions per prefix, cache
aggressively, and add safety filters so it never suggests harmful/offensive
queries.

### Multimodal recommendation / search
**Framing:** retrieval and ranking where items and/or queries span **text +
image (+ audio/video)** — e.g. search Pinterest by image, or recommend products
from a photo. Uses **shared multimodal embeddings** (CLIP-style) so text and
images live in one space, then the usual ANN retrieval + ranking funnel (M12/M13/
M16). **Gotcha:** **aligning modalities** (a good joint embedding is the whole
game) and **cold start** for new items using content embeddings when there is no
interaction history yet.

---

## 17.10 The Case-Study Pattern Cheat Sheet

Every prompt above collapses into a handful of **patterns**. If you can map a new
question to one of these in the first minute, you already know the skeleton of
your answer.

![Case-study pattern cheat sheet: a table mapping problem type to canonical pattern — recommendation/feed to two-stage retrieval+ranking funnel; search/RAG to multi-stage retrieval then rank then (generate); CTR/ads to calibrated classification feeding an auction; fraud/spam to imbalanced classification plus rules with an adversary; ETA to regression with asymmetric/quantile loss; each row lists the key metric and the signature gotcha.](images/m17_10_pattern_cheatsheet.png)

| Prompt smells like… | Pattern to reuse | Key metric | Signature gotcha |
|---------------------|------------------|-----------|------------------|
| "recommend / feed / for-you" | two-stage **retrieval → ranking** funnel (M12) | NDCG / watch-time; retention | feedback loops, position bias, multi-objective |
| "search / find / rank docs" | multi-stage **retrieval → rank → re-rank** (M13) | NDCG / MRR | click bias; lexical **and** semantic |
| "answer from our docs" | **RAG** = retrieval + grounded generation (M16) | faithfulness, recall@k | hallucination, permissions, chunking |
| "predict click / ad" | **calibrated classification** → auction | log-loss / calibration, AUC | calibration, delayed/biased labels |
| "detect fraud / spam / abuse" | **imbalanced classification + rules**, adversary | recall @ fixed FPR, PR-AUC | imbalance, adversarial drift, asym. cost |
| "how long / how much" (ETA, price) | **regression** (quantile/asymmetric) | MAE + late-rate/quantile loss | the tail, systematic bias |
| "people/items you may know/like" | **link prediction / item-item** over a graph | ranking + connection rate | feedback loop, fairness, privacy |
| "typeahead / suggest" | **prefix index + LM score**, precompute | latency, acceptance | ms-latency, freshness, safety |

**The universal moves that apply to *all* of them:**

1. Always propose a **simple baseline** first (popularity, BM25, rules,
   co-occurrence, routing-engine estimate) — it is a senior signal and a real
   fallback.
2. Split **batch (precompute embeddings, pools, aggregates)** from **online
   (fresh per-request scoring)** — the hybrid pattern hits low latency at scale.
3. Name **business + ML + offline + online** metrics *and a guardrail*.
4. Say the **gotcha** for the pattern (loops, bias, imbalance, calibration,
   hallucination, tail error) — this is what separates senior from junior.
5. Design the **failure path**: shadow, canary, kill switch, and a safe
   fallback. Every model *will* break.

---

## Module 17 — Interview Mapping (what companies probe)

| Company | Favourite case-study prompts | Junior answer | Staff answer |
|---------|------------------------------|---------------|--------------|
| **Google** | Web search ranking, YouTube reco, ads CTR | Jumps to a model | Multi-stage funnel, NDCG, lexical+semantic, latency budget per stage |
| **Meta** | Feed ranking, PYMK, harmful-content, ads | Single-objective | Multi-task ranking + integrity guardrail; feedback loops |
| **Amazon** | "Customers also bought", product search | Generic reco | Complements vs substitutes; ties to revenue and Customer Obsession |
| **Uber / DoorDash / Lyft** | ETA, dispatch, fraud | RMSE only | Asymmetric/quantile loss, per-segment bias, streaming features |
| **Stripe / banks** | Payment fraud / risk | "accuracy" | Recall @ fixed FPR, imbalance, adversary, fail-open vs closed |
| **OpenAI / Anthropic / startups** | Enterprise RAG, LLM assistants | "just prompt an LLM" | Retrieval + grounding + faithfulness eval + permissions |

**The single most common opening:** *"Design an ML system for X."* Map X to a
pattern (17.10), announce the 7 steps, and drive. That structure plus one named
gotcha is most of the score.

---

## Module 17 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **Interview-only, in practice.** Written exams do not ask you to design
  YouTube or a fraud system end to end.
- **GATE CS/DA:** the *underlying* concepts can appear standalone — task types
  (classification / regression / ranking), evaluation metrics (precision/recall,
  AUC, RMSE, NDCG), and class imbalance. Learn those from M7; the *assembly* here
  is interview material.
- **SEBI / RBI / ISRO:** at most definitional ML items. The value of this module
  is overwhelmingly for **interviews and the job**.

> **Bottom line:** treat this module as interview/on-the-job training. Its
> exam-relevant residue (metrics, task types, imbalance) is already covered in
> the exam-heavy modules.

---

## Module 17 — Common Mistakes & Misconceptions

1. **Jumping to the model** without clarifying scope/scale or naming the business
   metric. Announce the 7 steps first. (17.1)
2. **One metric ("accuracy").** Fatal for fraud/ads/search. Use the pattern's
   right metric — recall@FPR, calibration, NDCG, faithfulness — plus a guardrail.
3. **Ignoring the gotcha.** Not mentioning feedback loops (reco), calibration
   (ads), imbalance (fraud), the tail (ETA), or hallucination (RAG) reads as
   junior.
4. **Skipping the baseline.** Popularity / BM25 / rules / routing-estimate are
   real, strong, and your fallback — always propose one.
5. **No batch/online split.** Trying to run one giant model per request at
   millions of QPS. Precompute the heavy parts; keep the online part small.
6. **Treating clicks as truth.** Clicks are biased (position, presentation,
   selection). Debias them.
7. **Forgetting the failure path.** No shadow/canary/kill-switch/fallback. Every
   model breaks; design for it.
8. **RAG = "just an LLM".** Ignoring retrieval quality, permissions, and
   faithfulness evaluation.

---

## Module 17 — MCQs (with answers & explanations)

**Q1.** Why is the **two-stage** (retrieval → ranking) architecture used in
recommendation and search?
a) It is easier to code
b) Retrieval cheaply narrows millions to hundreds so the expensive ranker runs on
   few candidates
c) It removes the need for metrics
d) It avoids using embeddings

<details><summary>Answer</summary>**b.** You cannot run a heavy model on billions
of items per request. Cheap retrieval (ANN / BM25) narrows the pool, then the
expensive ranker scores only the survivors. (17.1, 17.2, 17.7)</details>

**Q2.** In ad **CTR prediction**, why does *calibration* matter as much as AUC?
a) It doesn't
b) Because the predicted probability is multiplied by the bid in the auction, so a
   mis-calibrated pCTR directly mis-prices ads
c) Because calibration improves latency
d) Because AUC is unmeasurable

<details><summary>Answer</summary>**b.** Expected value ≈ bid × pCTR. If the
probability is wrong in absolute terms, the auction pays the wrong amount even if
the ranking (AUC) is fine. (17.4)</details>

**Q3.** For **fraud detection** with 0.1% fraud, which metric is appropriate?
a) Accuracy
b) Recall at a fixed low false-positive rate (and PR-AUC)
c) RMSE
d) BLEU

<details><summary>Answer</summary>**b.** With extreme imbalance, 99.9% accuracy is
trivial and useless. You care about catching fraud without too many false
declines — recall at a fixed FPR, PR-AUC. (17.5)</details>

**Q4.** Why prefer **quantile / asymmetric loss** for ETA prediction?
a) It's faster to train
b) Being late is more costly than being early, and the app needs a reliable range,
   so the tail and asymmetry matter more than mean error
c) It removes the need for features
d) It guarantees zero error

<details><summary>Answer</summary>**b.** A chronically optimistic ETA breaks trust
even at low MAE; asymmetric/quantile loss penalises lateness and lets you show
p50/p90. (17.6)</details>

**Q5.** In an **enterprise RAG** assistant, which is the most important
correctness concern beyond fluency?
a) Font rendering
b) Groundedness/faithfulness, correct citations, and never leaking documents the
   user lacks permission to see
c) Model size
d) GPU brand

<details><summary>Answer</summary>**b.** RAG must answer only from retrieved,
permitted context and cite it; hallucination and permission leaks are the
defining risks. (17.8)</details>

**Q6.** A recommender keeps pushing the same popular items, which get more
engagement, which promotes them further. This is:
a) a cache miss
b) a feedback loop (popularity/bias amplification)
c) overfitting
d) label leakage

<details><summary>Answer</summary>**b.** The system's own choices shape the next
training data, amplifying popularity. Mitigate with exploration and
position-debiasing. (17.2)</details>

**Q7.** Web search retrieval works best when it combines:
a) only BM25
b) only dense embeddings
c) lexical (BM25) **and** semantic (dense + ANN) retrieval
d) neither

<details><summary>Answer</summary>**c.** Lexical catches exact/rare terms;
semantic catches meaning/synonyms. Hybrid retrieval covers both, then a ranker
merges them. (17.7)</details>

**Q8.** For "customers also bought", the key modelling subtlety is:
a) using RMSE
b) distinguishing complements from substitutes (recommend a case, not another
   phone) and avoiding popularity bias
c) training an LLM
d) using a trie

<details><summary>Answer</summary>**b.** Co-occurrence alone can recommend
substitutes; the value is in complements, and the long tail must survive
popularity bias. (17.9)</details>

---

## Module 17 — Design Exercises (easy → hard)

- **Easy.** For each prompt, name the pattern (from 17.10) and its signature
  gotcha: (1) TikTok For-You feed; (2) credit-card fraud; (3) "answer from our HR
  docs"; (4) food-delivery ETA; (5) app-store search.
- **Easy.** Give the *baseline* you would propose for each of the seven flagship
  systems.
- **Medium.** Design **Spotify Discover Weekly** end to end using the 7 steps.
  Which flagship does it most resemble, and what is different (weekly batch, audio
  features, exploration)?
- **Medium.** For **YouTube reco**, sketch a latency budget across retrieval,
  ranking, and re-ranking that fits a few-hundred-ms feed at 500k QPS, and say
  what you precompute vs compute online.
- **Hard.** Design **payment fraud** and justify a *fail-open vs fail-closed*
  policy for two transaction risk tiers. State your metric and threshold logic.
- **Hard.** Design an **enterprise RAG** assistant with strict document
  permissions. Where exactly do you enforce access control, and how do you
  evaluate faithfulness and detect permission leaks before launch?
- **Hard.** You are given a brand-new prompt: *"design a system to recommend
  which push notification to send each user, and when."* Map it to known
  patterns, name the business metric, the gotcha (annoyance/opt-outs as a
  guardrail), and sketch the funnel.

---

## Module 17 — Concept Review (one page)

- Almost every large ML product is the **same funnel**: candidates → retrieval →
  ranking → re-rank/rules → small output, with a **feedback loop** to training.
- Run the **7 steps** on every prompt: Clarify → Frame → Metrics → Data →
  Model → Serve → Monitor. Announce them and drive.
- **Two-stage retrieval → ranking** (M12/M13) and the **hybrid batch+online
  split** are the two skeletons behind most systems.
- **Metrics per pattern:** reco/feed → NDCG + watch-time/retention; search →
  NDCG/MRR; ads → calibration + AUC; fraud/spam → recall@FPR + PR-AUC; ETA →
  MAE + late-rate/quantile; RAG → faithfulness + recall@k. Always add a
  **guardrail**.
- **The gotchas define seniority:** feedback loops & position bias (reco),
  multi-objective + integrity (feed), calibration + delayed labels (ads),
  imbalance + adversary + asymmetric cost (fraud), the tail + bias (ETA),
  lexical+semantic + click bias (search), hallucination + permissions +
  grounding (RAG).
- Always propose a **baseline**, split **batch vs online**, and design the
  **failure path** (shadow, canary, kill switch, fallback).
- **Map a new prompt to a known pattern** in the first minute — that is the whole
  skill this module builds.

---

## Module 17 — Flash Cards (Q → A)

1. Skeleton behind reco and search? → *Two-stage retrieval → ranking funnel.*
2. Metric for fraud with 0.1% positives? → *Recall at a fixed low FPR / PR-AUC,
   never accuracy.*
3. Why calibration in ad CTR? → *pCTR × bid drives the auction, so absolute
   probability must be right.*
4. ETA loss of choice and why? → *Quantile/asymmetric — lateness costs more than
   earliness; watch the tail.*
5. RAG's three defining risks? → *Hallucination, permission leaks, stale/poor
   retrieval; evaluate faithfulness.*
6. Reco's signature gotcha? → *Feedback loops + position bias → use exploration &
   debiasing.*
7. Best web-search retrieval? → *Hybrid lexical (BM25) + semantic (dense+ANN).*
8. "Customers also bought" subtlety? → *Complements vs substitutes; beat
   popularity bias.*
9. Universal senior moves? → *Baseline first; batch/online split; right metric +
   guardrail; name the gotcha; design the failure path.*
10. First thing to do on a new prompt? → *Map it to a known pattern, then run the
    7 steps.*

---

## Module 17 — Pattern Recognition (how to spot it in an interview)

- Hear **"recommend / feed / for-you / up-next"** → two-stage funnel; NDCG +
  engagement; say *feedback loops & position bias*.
- Hear **"search / rank documents / product search"** → retrieval→rank→re-rank;
  NDCG/MRR; *lexical + semantic, debias clicks*.
- Hear **"answer questions from our documents"** → RAG; *retrieval + grounded
  generation, faithfulness, permissions*.
- Hear **"predict clicks / serve ads"** → calibrated classification + auction;
  *calibration + delayed labels*.
- Hear **"detect fraud / spam / abuse"** → imbalanced classification + rules;
  *recall@FPR, adversary, fail-open vs closed*.
- Hear **"how long / estimate time or cost"** → regression; *asymmetric/quantile
  loss, the tail, per-segment bias*.
- Hear **"people/items you may know or like"** → link prediction / item-item over
  a graph; *feedback loop, fairness, privacy*.
- Hear **"suggest as they type"** → prefix index + LM; *millisecond latency,
  freshness, safety filters*.
- Any prompt → **baseline first, batch/online split, guardrail metric, failure
  path.**

---

## Module 17 — Revision Notes / Mini Cheat Sheet

```
MASTER FUNNEL:  events + huge candidate pool
                -> RETRIEVAL (cheap, ANN/BM25)  -> hundreds
                -> RANKING (heavy model)        -> tens
                -> RE-RANK + business rules      -> small final output
                -> log feedback -> retrain  (LOOP)

RUN 7 STEPS EVERY TIME:  Clarify Frame Metrics Data Model Serve Monitor

PATTERN  ->  METRIC  ->  GOTCHA
  reco/feed   NDCG + watch/retention    feedback loops, position bias, multi-obj
  search      NDCG / MRR                 lexical+semantic, click bias
  RAG         faithfulness, recall@k     hallucination, permissions, chunking
  ads CTR     calibration + AUC          calibration, delayed/biased labels
  fraud/spam  recall@fixed-FPR, PR-AUC   imbalance, adversary, asym cost, fail o/c
  ETA/price   MAE + late-rate/quantile   the TAIL, systematic bias
  PYMK/item   ranking + connect rate     feedback loop, fairness, privacy
  typeahead   latency, acceptance        ms-latency, freshness, safety

UNIVERSAL MOVES
  1 baseline first (popularity/BM25/rules/routing-est/co-occurrence)
  2 split BATCH (precompute embeds/pools/aggregates) vs ONLINE (fresh per-req)
  3 metrics = business + ML + offline + online + GUARDRAIL
  4 SAY THE GOTCHA for the pattern (this = seniority)
  5 failure path = shadow -> canary -> kill switch -> safe fallback

MAP THE PROMPT TO A PATTERN IN THE FIRST MINUTE.  Then drive the 7 steps.
```

---

> **Next module:** *Module 18 — Responsible AI: Fairness, Bias, Privacy &
> Safety.* Every case study above quietly raised an ethical edge — feedback loops
> that amplify bias, fraud models that wrongly decline real customers, RAG
> systems that could leak private documents, feeds that could push harmful
> content. Module 18 turns those scattered "guardrails" into a first-class
> discipline: how to measure fairness, protect privacy, and build safety and
> accountability into an ML system by design, not as an afterthought.
