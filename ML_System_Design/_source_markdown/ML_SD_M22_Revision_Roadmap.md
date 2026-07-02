---
title: "Module 22 — Revision, Cheat Sheets & Roadmap"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 22 — Revision, Cheat Sheets & Roadmap

> **Why this module exists.**
> You have now walked through twenty-one modules — from *what an ML system is*
> all the way to *serving an LLM at scale*. That is a lot of ideas to hold in
> your head the night before an interview or exam. This module is the
> **single place you re-read to remember all of it fast**. It does not teach
> new theory. Instead it *compresses* the whole course into cards, tables, and
> decision trees you can scan in an hour. Think of it as the folded map you keep
> in your pocket: every road you already learned to drive, drawn on one sheet.
> Use it to revise, to self-test, and to warm up right before you walk into the
> room.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★★     | ★★★    | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
recite the **7-step framework** in one breath; recall the **3–5 must-remember
points** for every module M01–M21; pick the **right metric** for any task from
memory; run the four core **decision trees** (batch vs online, RAG vs fine-tune,
GBDT vs DNN, when-to-use-ML) without thinking; answer 30+ rapid **flash cards**;
see the **whole course as one mind map**; and follow a **study plan** (12 weeks
deep, or 2 weeks crash) that gets you interview-ready.

> **How to use this module.** First skim the 60-second card and the per-module
> table to jog your memory. Then drill the flash cards until they are automatic.
> Then quiz yourself on the decision trees. Finally, pick the roadmap that
> matches how much time you have. Revisit this page many times — spaced
> repetition beats one long cram.

---

## 22.1 ML System Design in 60 Seconds (the framework card)

### The one card that runs any interview

Every design prompt — "design YouTube recommendations", "design fraud
detection", "design a RAG chatbot" — is answered with the **same 7-step spine**.
If you remember nothing else, remember this card and speak it out loud in your
first minute.

![The 7-step ML system design framework card: Clarify, Frame, Metrics, Data, Model, Serve, Monitor — arranged as a loop where monitoring feeds back to the start.](images/m22_01_framework_card.png)

**The 7 steps (mnemonic C-F-M-D-M-S-M):**

1. **Clarify** — goal, users, scale (QPS, data size), constraints, and *scope
   for today*. Recap assumptions before you design. *(M02, M03)*
2. **Frame** — turn the business goal into **one** ML task (classification /
   regression / ranking / retrieval / generation), or argue for a plain **rule**
   if ML is not warranted. *(M03)*
3. **Metrics** — pick on two axes: **business vs ML** and **offline vs online**;
   always add a **guardrail** metric. Offline guides iteration; online (A/B)
   decides shipping. *(M07)*
4. **Data** — sources, labels, splits (**temporal**, no leakage), imbalance,
   privacy. *(M04)*
5. **Model** — start with a **baseline**; climb complexity only if it provably
   fails; agree train/serve features. *(M05, M06)*
6. **Serve** — batch vs online vs hybrid from the **non-functional
   requirements**; design the **latency budget** and the **failure path**.
   *(M08, M11, M19)*
7. **Monitor** — six signals (data, drift, performance, business, system,
   feedback loop); rollback + kill switch; retrain. This **loops** back to Data.
   *(M09, M10)*

> **Senior signal:** announce the plan, narrate your reasoning, budget the 45
> minutes out loud, and *connect* every ML choice to a systems choice to the
> business metric. Seniority = **breadth + owning trade-offs**, not more math.

---

## 22.2 Per-Module Cheat Sheet (M01–M21)

The 3–5 things you **must** be able to say for each module. If you can recite
this table, you can survive the interview.

| # | Module | Must-remember points |
|---|--------|----------------------|
| **M01** | Foundations | SW1.0 = write rules; SW2.0 = learn rules from data. ML system ⊃ model (+ data, features, serving, monitoring, feedback). 4 hard things: **data deps, feedback loops, non-determinism, decay**. Lifecycle is a **loop**. |
| **M02** | Framework | **C-F-M-D-M-S-M**. Clarify first, scope explicitly. Metrics on 2 axes + guardrail. NFRs drive the architecture. Drive the interview; own trade-offs. |
| **M03** | Problem Framing | Ladder: **goal → metric → label → task**. Pick task from **output shape**. Label traps: **proxy, leakage, delayed**. Capacity math: avg QPS = req/day ÷ 86,400; size for **peak** (2–4×). |
| **M04** | Data Engineering | Batch (cheap, stale) vs streaming (fresh, complex). Pipelines = **DAG** + orchestrator (Airflow). Lake vs warehouse vs lakehouse. Validate before training. Accuracy lies under **imbalance**. Version data (DVC). |
| **M05** | Features & Stores | Everything → a number. Encodings: one-hot / hashing / target / bucketize. Scale for distance & gradient models, **not trees**. **Embeddings** generalise. **Training-serving skew** kills live accuracy. Feature store = offline + online + **point-in-time**. |
| **M06** | Model Training | **GBDT** for tabular, DNN for perception, transformers for language. **Baseline first**. Bias vs variance; regularize (L1/L2/dropout/early-stop). Loss = definition of good. Adam default. Data vs model parallel; LoRA for cheap fine-tune. |
| **M07** | Evaluation | Confusion matrix → precision/recall/F1. **Accuracy lies on imbalance**; use **PR-AUC** when positives rare. **NDCG** for ranking. **Temporal split**; leakage = great offline, bad live. **Offline picks what to test; online (A/B) picks what to launch.** |
| **M08** | Serving | Batch / online / streaming / **hybrid**. Patterns: embedded / service / microservice / sidecar. Design to the **p99 tail**. Optimize: **quantize / prune / distill / ONNX / TensorRT**. Rollout: **shadow → canary → A/B** with rollback. |
| **M09** | MLOps | MLOps = lifecycle made **automatic, reproducible, observable**. Maturity L0→L1→L2 (CI/CD/**CT**). Track experiments; **model registry** = one-click rollback. Reproducibility = pin data+code+env+seed. Kill idle GPU cost. |
| **M10** | Monitoring & Drift | Monitor 6 signals; **labels lag**. **PSI** thresholds <0.1 / 0.1–0.25 / ≥0.25. **Data drift** P(X) vs **concept drift** P(Y\|X). Retrain: scheduled / triggered / continual. **Rollback first**, then triage. |
| **M11** | Scaling | Data / training / serving scale **independently** — find the saturated resource first. Shard (capacity) vs replicate (reads). Training is **bandwidth-bound** (all-reduce). Embedding table = N×d×4 B. **Vertical vs horizontal**; autoscale. 100× = a **systems** problem, not a bigger model. |
| **M12** | Recommendation | One user + millions of items → short list via a **proxy**. CF (user/item), **matrix factorization** (R≈UVᵀ). **Two-stage funnel**: candidate gen (recall) → ranking (precision). **Two-tower + ANN**. Deep rankers model interactions. **Cold start** + explore/exploit (bandits). |
| **M13** | Search & Ranking | **Inverted index**; **BM25** keyword baseline. **Learning to Rank**: pointwise / pairwise / **listwise (LambdaMART)**. **Dense retrieval** (two-tower + ANN); use **hybrid** BM25 + dense. Multi-stage funnel. Eval **NDCG@k** + online A/B; mind position bias. |
| **M14** | Computer Vision | 3 tasks: classify / detect / segment. Pipeline: preprocess → model (**CNN vs ViT**) → postprocess (NMS). Share one preprocess fn (skew). **Visual search** = embed + ANN. Augment (train-only). Levers: image size, batch, FP16/INT8. |
| **M15** | NLP | Pipeline: clean → **tokenize (subword/BPE)** → embed → model. **Static (word2vec) vs contextual (BERT)** embeddings. Label vs generate families. **Semantic search** = embed + cosine + ANN. Attention ~**O(n²)**: cap length → cache → batch → distill. |
| **M16** | LLM System Design | Token ≈ 4 chars; pay per token; context window bounds it. **Decision order: prompt → RAG → fine-tune → pre-train.** RAG changes *knowledge*, fine-tune changes *behaviour*. RAG: chunk→embed→index→retrieve→**re-rank**→generate. **Hybrid + RRF**. ANN: recall↔latency↔memory. **TTFT/TPOT**; KV-cache, continuous batching. **Prompt injection** = untrusted data. |
| **M17** | Case Studies | Nearly every product is the **same funnel** + feedback loop. Run the **7 steps**. Metrics per pattern (reco→NDCG+watch-time; fraud→recall@FPR+PR-AUC; RAG→faithfulness+recall). **Map a new prompt to a known pattern in minute 1.** |
| **M18** | Responsible AI | Bias enters via data, labels, feedback (proxies survive deleting attributes). Fairness: parity / equal-opportunity / equalized-odds — **can't have all; pick by harm**. Mitigate pre/in/post. **DP** (epsilon), **federated + secure aggregation**, **SHAP/LIME**. Governance: model cards, EU AI Act, GDPR. |
| **M19** | Systems Foundations | **Load balancing** (L4 fast vs L7 smart). **Caching** (aside/through/back; LRU/LFU/TTL). DBs: SQL / NoSQL / KV / **vector** / time-series. **Kafka** log + partitions. **CAP**: pick C or A on partition. **REST edge, gRPC internal**. SLI→SLO→SLA. Latency ladder RAM≪SSD≪disk≪cross-region. |
| **M20** | Interview Mastery | **8 patterns** cover most prompts. **45-min timeline**: clarify(0–5)→frame(5–10)→data/features/model(10–25)→serve/scale/monitor(25–38)→trade-offs(38–45). Company styles shift emphasis. **Recover, don't freeze.** Red flags: jumps to model, forgets serving+monitoring. |
| **M21** | Projects | 7 buildable systems: recommender (two-tower+ANN), semantic search (FAISS), RAG chatbot (+evals), fraud (Kafka→Flink→online store), feature store (point-in-time), A/B+monitoring, LLM serving (continuous batching+KV-cache). |

---

## 22.3 Metric Selection (task → metric)

The fastest way to lose points is to say "accuracy" for everything. Match the
**task shape** and the **cost of errors** to the metric.

![Metric-selection flowchart: from the task type (classification, ranking, regression, generation, retrieval) branch to the correct offline metric, with a note that A/B on the business metric decides launch.](images/m22_02_metric_selector.png)

**Quick lookup:**

| Task | Primary offline metric | When / note |
|------|------------------------|-------------|
| Balanced classification | Accuracy, F1 | Only when classes are roughly balanced |
| Imbalanced / rare-positive | **PR-AUC**, Recall@fixed-FPR | Fraud, spam, disease — accuracy lies |
| Probability quality | Log-loss, calibration (reliability) | Ads/CTR, risk scores |
| Regression | MAE (robust), RMSE (punishes big) | RMSE flags outliers; MAPE breaks near 0 |
| Ranking / search / reco | **NDCG@k**, MAP, MRR | Graded + discounted; MRR for first-hit |
| Retrieval (candidate gen) | **Recall@k** | Don't lose the good items early |
| Generation (NLP) | BLEU (precision), ROUGE (recall), perplexity | + LLM-as-judge (cheap, biased) |
| RAG | Faithfulness, context recall/precision | Low recall = retrieval bug; low faithfulness = generation bug |
| CV detection / segmentation | mAP, IoU | Boxes / pixel masks |
| **Launch decision (any task)** | **Online A/B on the business metric + guardrail** | Offline only *nominates*; online *decides* |

> **Senior signal:** before naming a metric, ask *"what does a false positive
> cost vs a false negative?"* That single question picks precision-vs-recall and
> shows you connect ML to business consequences.

---

## 22.4 The Four Core Decision Trees

These four choices come up in almost every design. Memorize the *branch
conditions*, not just the answers.

### 22.4.1 Batch vs Online (where does inference run?)

![Decision tree for batch vs online serving: if predictions can be precomputed and staleness is acceptable, use batch; if the request needs a fresh per-user answer within a tight latency budget, use online; large systems combine both as a hybrid.](images/m22_03_batch_vs_online.png)

- **Batch** if yesterday's answer is fine and you can precompute for all entities
  (nightly email recs). Cheap, simple, stale.
- **Online** if the answer must reflect *this request* within a ms budget (search,
  ads, fraud). Fresh, latency-bound.
- **Hybrid** (the senior move): precompute heavy **candidates** in batch, then
  **re-rank online** per request. YouTube/Netflix-style.

### 22.4.2 Prompt vs RAG vs Fine-tune (how to adapt an LLM)

![Decision tree for LLM adaptation: try prompting first; if the model lacks knowledge or needs fresh/private facts use RAG; if it needs a new behaviour, format, or style use fine-tuning; pre-train only at extreme scale.](images/m22_04_rag_vs_finetune.png)

- **Prompt** first — cheapest, no training. Few-shot examples + good instructions.
- **RAG** when the model **lacks knowledge** or needs **fresh / private / cited**
  facts. *RAG changes what the model **knows**.*
- **Fine-tune** (LoRA/QLoRA) when you need a **behaviour, format, or style**, not
  facts. *Fine-tuning changes how the model **behaves**.*
- **Pre-train** only at extreme scale / brand-new domain — almost never in an
  interview answer.
- Rule: **prompt → RAG → fine-tune → pre-train**, stop as soon as it works.

### 22.4.3 GBDT vs Deep Neural Net (which model?)

![Decision tree for model choice: for tabular data with modest size prefer gradient-boosted trees; for perception (images, audio) or language, or when you have huge data and need embeddings, prefer deep neural nets.](images/m22_05_gbdt_vs_dnn.png)

- **GBDT (XGBoost/LightGBM)** for **tabular** data, modest size, need speed,
  interpretability, and a strong baseline. Ignores feature scale. Usually wins on
  tabular.
- **Deep nets** for **perception** (images, audio, video) and **language**, when
  you need **embeddings**, have lots of data, or want end-to-end representation
  learning.
- Always **start with the simpler one** (linear/GBDT baseline) and climb only if
  it provably fails.

### 22.4.4 When to Use ML at All

![Decision tree for whether to use ML: only use ML if a real pattern exists, you cannot easily hand-write rules, you have data, you can tolerate some error, and you can measure success; otherwise use plain rules.](images/m22_06_when_ml.png)

Use ML **only if all** hold:

1. A **pattern exists** (input predicts output; not pure randomness).
2. You **cannot hand-write the rules** (too complex / numerous / changing).
3. You **have data** that captures the pattern.
4. You can **tolerate some error** (or have a human safety net).
5. You can **measure success** (a metric, labels, feedback).

If any fails → **use a plain rule**. Saying "we may not need ML here" is a
strong senior signal.

---

## 22.5 Course-Wide Flash Cards (drill until automatic)

Cover the right side; say the answer aloud; check.

**Foundations & framework**

1. Software 2.0 in one line? → *Rules learned from data, not hand-written.*
2. Four things that make ML hard? → *Data dependencies, feedback loops,
   non-determinism, decay.*
3. The 7 framework steps? → *Clarify, Frame, Metrics, Data, Model, Serve,
   Monitor (C-F-M-D-M-S-M).*
4. First thing in any prompt? → *Clarify goal, scale, constraints, scope.*
5. Seniority in one line? → *Breadth + owning trade-offs, not more math.*

**Framing & data**

6. Framing ladder? → *goal → metric → label → task.*
7. How to pick the ML task? → *From the shape of the output.*
8. Signature of label leakage? → *Great offline, terrible live.*
9. Average QPS formula? → *requests per day ÷ 86,400; size for peak (2–4×).*
10. Why does accuracy lie under imbalance? → *Predicting the majority scores high
    while catching none of the rare class.*
11. Retrieval vs ranking? → *Retrieval fetches top-k from millions; ranking
    orders the shortlist.*

**Features & models**

12. Which models ignore feature scale? → *Tree-based (they split on order).*
13. Training-serving skew in one line? → *A feature computed differently in
    training vs serving → live accuracy drops.*
14. Point-in-time correctness? → *Use only data known at/before prediction time.*
15. Default model for tabular data? → *GBDT (XGBoost/LightGBM).*
16. Bias vs variance? → *Bias = too simple (underfit); variance = too sensitive
    (overfit).*
17. L1 vs L2 regularization? → *L1 zeros weights (selection); L2 shrinks smoothly.*
18. Where does cross-entropy come from? → *Negative log-likelihood (MLE).*
19. Data vs model parallelism? → *Data: full model per GPU, split data; model:
    split the model when it won't fit.*

**Evaluation & metrics**

20. When PR-AUC over ROC-AUC? → *When positives are rare (imbalanced).*
21. Why NDCG over Precision@K? → *Graded relevance + log discount for lower ranks.*
22. Why a temporal split? → *Production predicts the future from the past; random
    split leaks the future.*
23. Offline vs online metrics? → *Offline decides what to test; online (A/B)
    decides what to launch.*
24. What is a guardrail metric? → *One you must not harm while chasing the target
    (latency, revenue, diversity).*

**Serving, scaling & MLOps**

25. Why design to p99, not p50? → *Under fan-out to N, P(all fast)=pᴺ, so the tail
    becomes the typical experience.*
26. Four serving optimizations? → *Quantization, pruning, distillation, compile
    (ONNX/TensorRT).*
27. Safe rollout order? → *Shadow → canary → A/B, with one-click rollback + kill
    switch.*
28. What is CT in CI/CD/CT? → *Continuous Training — retrain on new data/drift.*
29. Is 100× traffic a model problem? → *No — a systems problem: replicate, cache,
    batch, shard, autoscale.*
30. Embedding table size formula? → *N × d × 4 bytes (float32).*

**Monitoring, reco, search, LLM, responsible AI**

31. PSI drift thresholds? → *<0.1 stable, 0.1–0.25 moderate, ≥0.25 major.*
32. Data drift vs concept drift? → *P(X) moves vs P(Y\|X) changes.*
33. The two-stage funnel? → *Candidate generation (recall) → ranking (precision).*
34. Two-tower retrieval? → *Separate user & item towers, dot-product, item vectors
    precomputed → ANN lookup.*
35. Keyword search baseline? → *BM25 over an inverted index.*
36. RAG vs fine-tune? → *RAG changes knowledge; fine-tune changes behaviour.*
37. LLM latency metrics? → *TTFT (time to first token) + TPOT (time per output
    token).*
38. Biggest LLM security risk? → *Prompt injection — treat all external/retrieved
    text as untrusted data.*
39. Can you satisfy all fairness metrics at once? → *No — choose by the harm.*
40. What does differential privacy's epsilon control? → *The privacy budget (small
    = more private, noisier, less accurate).*

---

## 22.6 The Course as One Mind Map

Two halves. The **core pipeline** is the machinery every ML system shares; the
**applied & advanced** half is where you specialize.

### Part 1 — Core pipeline (M01–M11)

![Course mind map part 1: the core ML pipeline branching from foundations and framework into problem framing, data engineering, features, training, evaluation, serving, MLOps, monitoring, and scaling.](images/m22_07_mindmap_core.png)

Read it as the lifecycle loop: **Foundations & Framework** feed **Framing →
Data → Features → Training → Evaluation → Serving → MLOps → Monitoring**, with
**Scaling** wrapping the serving/training edges. Every arrow is a module.

### Part 2 — Applied & advanced (M12–M21)

![Course mind map part 2: the applied and advanced branches — recommendation, search and ranking, computer vision, NLP, LLM system design, case studies, responsible AI, systems foundations, interview mastery, and hands-on projects.](images/m22_08_mindmap_applied.png)

These reuse the core: **Recommendation, Search, CV, NLP, LLMs** are all the same
funnel + embeddings + serving story, specialized. **Responsible AI** and
**Systems Foundations** are cross-cutting; **Case Studies, Interview Mastery,
and Projects** are where you *practice putting it all together*.

---

## 22.7 Study Roadmaps

### 12-week deep plan (build real mastery)

Roughly 8–10 focused hours/week. Each week = read the module(s), redraw the key
diagram from memory, do the design exercises, and drill that module's flash cards.

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | M01 Foundations + M02 Framework | Recite the 7 steps from memory |
| 2 | M03 Framing + M04 Data | Frame 3 business problems into ML tasks + sketch a data pipeline |
| 3 | M05 Features + Feature Stores | Explain training-serving skew + point-in-time joins |
| 4 | M06 Training | Bias/variance, losses, distributed training; pick models for 5 datasets |
| 5 | M07 Evaluation | Metric-selection drill; build one offline eval + A/B test plan |
| 6 | M08 Serving + M19 Systems Foundations | Design a serving path with a p99 budget |
| 7 | M09 MLOps + M10 Monitoring/Drift | Draw the retraining loop + 6 monitored signals |
| 8 | M11 Scaling | Capacity math for 100× traffic; sharding vs replication |
| 9 | M12 Recommendation + M13 Search/Ranking | Design the two-stage funnel end-to-end |
| 10 | M14 CV + M15 NLP + M16 LLM/RAG | Build a RAG design with evals + ANN choice |
| 11 | M18 Responsible AI + M17 Case Studies | Add fairness/privacy to two designs |
| 12 | M20 Interview Mastery + M21 Projects + **this M22** | Full mock interviews; ship one project |

### 2-week interview crash plan (already know the basics)

Roughly 3–4 hours/day. Goal: automate the *shape* of a great answer, not learn
theory from scratch.

| Day | Focus |
|-----|-------|
| 1 | M22 §22.1–22.2: framework card + per-module cheat sheet. Recite the 7 steps. |
| 2 | M02 + M03: clarify → frame; run 3 prompts to "one ML task + metric". |
| 3 | M07 + M22 §22.3: metric selection until automatic. |
| 4 | M08 + M11 + M19: serving, latency (p99), scaling, systems foundations. |
| 5 | M10 + M09: monitoring, drift, rollback, retraining loop. |
| 6 | M12 + M13: the two-stage funnel + two-tower + ANN. |
| 7 | **Mock #1: recommendation/feed.** Self-review against red flags (M20). |
| 8 | M16: LLM/RAG design; decision tree prompt→RAG→fine-tune. |
| 9 | Fraud/anomaly + ETA patterns (M17): imbalance, cost, tails. |
| 10 | **Mock #2: RAG chatbot.** Time-box to 45 min. |
| 11 | M18: fairness, privacy, safety — bolt onto any design. |
| 12 | M20: company styles + the 45-minute timeline; drill all M22 flash cards. |
| 13 | **Mock #3: fraud or ETA.** Focus on trade-offs + failure path. |
| 14 | Rest + light re-skim of this module. Walk in calm. |

> **Rule for both plans:** always end a session by **drawing the design from
> memory** and **saying the *why* out loud**. Passive re-reading feels productive
> but does not transfer to the whiteboard.

---

## Module 22 — Interview Mapping (what companies probe)

| Company | What they emphasize | Revise from |
|---------|---------------------|-------------|
| **Google / Meta** | Depth + scale; end-to-end funnel, capacity math | M11, M12, M13, §22.4.1 |
| **Amazon** | Customer obsession + Leadership Principles; cost of errors | M01 §cost-of-wrong, M03 |
| **Netflix** | Metrics + A/B rigor; long-term engagement | M07, M12 |
| **Apple** | Privacy + on-device / federated | M18, M08 (edge) |
| **OpenAI / Anthropic** | LLM/RAG + safety + evals; when a simpler baseline wins | M16, M18, §22.4.2 |
| **NVIDIA** | Infra, GPUs, inference cost, batching | M08, M11 |
| **Uber / Airbnb / Stripe** | Real-time, fraud, ETA, cost | M17, M04 (streaming) |

> **The universal opener:** *"How would you design an ML system for X?"* Your
> first 60 seconds = clarify → is-ML-needed → name the pattern → sketch the
> 7-step loop. This module is your warm-up so that spine is automatic.

---

## Module 22 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** revise *definitional* items — ML vs traditional
  programming, supervised/unsupervised, metrics (precision/recall/F1), data
  concepts. The per-module table (§22.2) and metric table (§22.3) are your
  fastest exam refreshers.
- **GATE CS / DA:** the DA paper tests the **workflow**, metrics, bias/variance,
  and basic model choice — all compressed in §22.2 and the flash cards. Deep
  system-design trade-offs are **interview-only** and not on written exams.
- **ISRO / DRDO:** basic ML/AI definitions only.

> **Flag:** the decision-tree and serving/scaling content (§22.4, M08, M11, M19)
> is interview-focused. For written exams, prioritize definitions, metrics, and
> the workflow.

---

## Module 22 — Common Mistakes & Misconceptions

1. **Cramming theory instead of drilling recall.** Re-reading M06 for the fifth
   time helps less than *saying* the answer to a flash card. Test yourself.
2. **Memorizing answers, not branch conditions.** In the decision trees, learn
   *when* each branch fires — that is what an interviewer probes.
3. **Skipping the boring middle (data, features, serving, monitoring).** Weak
   candidates over-invest in the model and starve the rest. The per-module table
   is weighted to fix this.
4. **One metric for everything.** "Accuracy" is wrong on imbalanced, ranking,
   generation, and retrieval tasks. Use §22.3.
5. **Treating M22 as new material.** It is a *compression* of the course. If a
   line here is fuzzy, jump back to the source module, then return.
6. **No spaced repetition.** One long cram fades fast. Revisit this page several
   times across days.

---

## Module 22 — MCQs (with answers & explanations)

**Q1.** What is the correct order of the 7-step framework?
a) Clarify, Metrics, Frame, Model, Data, Serve, Monitor
b) Clarify, Frame, Metrics, Data, Model, Serve, Monitor
c) Frame, Clarify, Data, Metrics, Model, Monitor, Serve
d) Data, Model, Serve, Clarify, Frame, Metrics, Monitor

<details><summary>Answer</summary>**b.** C-F-M-D-M-S-M: Clarify → Frame →
Metrics → Data → Model → Serve → Monitor, looping back via monitoring.</details>

**Q2.** You must catch a rare fraud class (0.1% positives). Which offline metric?
a) Accuracy  b) ROC-AUC only  c) PR-AUC / recall at a fixed FPR  d) BLEU

<details><summary>Answer</summary>**c.** With rare positives, accuracy and even
ROC-AUC can look great while catching nothing. PR-AUC and recall@FPR reflect the
real objective.</details>

**Q3.** An LLM gives outdated answers about your company's private docs. Cheapest
correct fix?
a) Pre-train from scratch  b) Fine-tune on style  c) RAG over the docs  d) Bigger
context window alone

<details><summary>Answer</summary>**c.** The model lacks *knowledge*, so retrieve
it: RAG changes what the model knows. Fine-tuning changes behaviour, not facts.</details>

**Q4.** You have clean tabular data and need a strong, fast, interpretable
baseline. Best first model?
a) A 100-layer CNN  b) GBDT (XGBoost)  c) A large transformer  d) k-means

<details><summary>Answer</summary>**b.** GBDT is the default winner on tabular
data — fast, strong, ignores feature scale, and interpretable.</details>

**Q5.** A model's PSI on a key feature jumps to 0.30. This means:
a) The model improved  b) Major distribution drift → investigate/retrain  c) A
cache miss  d) Nothing, PSI is noise

<details><summary>Answer</summary>**b.** PSI ≥ 0.25 signals major drift. The input
distribution has shifted; check data quality and consider retraining.</details>

**Q6.** Which is a genuine *senior* signal?
a) "Use the biggest model available."  b) "Accuracy is all that matters."
c) "Let me clarify scope and check whether we even need ML, then name the
pattern."  d) "We deploy and we're done."

<details><summary>Answer</summary>**c.** Clarifying scope, questioning if ML is
needed, and mapping to a known pattern show judgment and breadth.</details>

**Q7.** Under request fan-out to N services, why design to the p99 tail?
a) p50 is unmeasurable  b) P(all N fast) = pᴺ, so the slow tail becomes the
typical user experience  c) Tails don't matter  d) It lowers cost

<details><summary>Answer</summary>**b.** With fan-out, the probability that *every*
sub-request is fast shrinks as pᴺ, so a rare per-service tail becomes common
end-to-end. Budget the whole path.</details>

**Q8.** Which best separates "data drift" from "concept drift"?
a) They are the same  b) Data drift = P(X) moves; concept drift = P(Y\|X) changes
c) Data drift needs new labels; concept drift never does  d) Concept drift only
affects images

<details><summary>Answer</summary>**b.** Data drift = inputs shift but the rule
holds (retrain on new data). Concept drift = the input→output relationship itself
changes (needs fresh labels).</details>

---

## Module 22 — Design Exercises (easy → hard)

- **Easy.** Without looking, recite the 7 steps and give a one-line meaning for
  each.
- **Easy.** For 5 tasks (fraud, movie ranking, house-price, translation, RAG QA),
  name the correct primary metric from memory.
- **Medium.** Pick batch vs online vs hybrid for: nightly email recs, live search,
  card-fraud scoring, a weekly churn report. Justify each in one sentence.
- **Medium.** You are given a new prompt: "design a system to detect fake product
  reviews." Map it to a known pattern (M17), then run all 7 steps in 5 minutes.
- **Hard.** A recommender's engagement is up but diversity is collapsing. Diagnose
  (which module?), and design the fix (explore/exploit + monitoring).
- **Hard.** Take any one design you built during the course and add the
  **Responsible-AI layer** (bias source, fairness metric by harm, privacy,
  governance) and the **failure path** (shadow/canary/rollback/kill switch).

---

## Module 22 — Concept Review (one page)

- **One card runs everything:** the **7 steps (C-F-M-D-M-S-M)** — Clarify, Frame,
  Metrics, Data, Model, Serve, Monitor — looping via monitoring.
- **Per-module table (§22.2)** holds the 3–5 must-remember points for M01–M21;
  it is your single densest revision asset.
- **Metric by task, not by habit:** imbalance → PR-AUC; ranking → NDCG;
  regression → MAE/RMSE; generation → BLEU/ROUGE; RAG → faithfulness+recall;
  **launch is decided by online A/B on the business metric + guardrail.**
- **Four decision trees:** batch vs online (freshness/latency → hybrid),
  prompt→RAG→fine-tune (knowledge vs behaviour), GBDT vs DNN (tabular vs
  perception/language), when-to-use-ML (pattern+data+error-tolerance+metric).
- **The whole course is one funnel + one loop:** candidates → retrieval →
  ranking → re-rank, with monitoring feeding retraining. Applied modules
  specialize the same machinery.
- **Study by recall, spaced:** redraw diagrams from memory, drill flash cards,
  and say the *why* out loud. Pick the 12-week or 2-week plan by your timeline.

---

## Module 22 — Flash Cards (fastest 10)

1. The 7 steps? → *Clarify, Frame, Metrics, Data, Model, Serve, Monitor.*
2. Metric for imbalance? → *PR-AUC / recall@fixed-FPR.*
3. Metric for ranking? → *NDCG@k.*
4. What decides launch? → *Online A/B on the business metric.*
5. Batch vs online in one line? → *Precompute+stale+cheap vs per-request+fresh+ms
   budget; big systems go hybrid.*
6. RAG vs fine-tune? → *RAG = knowledge; fine-tune = behaviour.*
7. Default tabular model? → *GBDT.*
8. When NOT to use ML? → *No pattern / no data / no error tolerance / no metric.*
9. PSI major-drift threshold? → *≥ 0.25.*
10. Seniority in one line? → *Breadth + owning trade-offs, not more math.*

---

## Module 22 — Pattern Recognition (how to spot it in an interview)

- Hear **"design an ML system for X"** → open with the **7 steps**; clarify first.
- Hear **"rare event / fraud / disease"** → say **imbalance → PR-AUC**, cost-based
  threshold.
- Hear **"real-time / within X ms"** → **online/streaming**, p99 budget, hybrid.
- Hear **"the model got worse"** → **drift**, PSI, monitoring + retraining.
- Hear **"answer from our documents"** → **RAG** (chunk→embed→retrieve→re-rank→
  generate) + faithfulness evals.
- Hear **"recommend / rank / search"** → **two-stage funnel** + two-tower + ANN +
  NDCG.
- Hear **"100× traffic"** → **systems** answer (replicate, cache, batch, shard,
  autoscale), not a bigger model.
- Hear **"is this fair / private?"** → fairness metric **by harm**, DP/federated,
  governance (model cards, EU AI Act).

---

## Module 22 — Revision Notes / Mini Cheat Sheet

```
FRAMEWORK (C-F-M-D-M-S-M): Clarify -> Frame -> Metrics -> Data -> Model -> Serve -> Monitor -^

METRIC BY TASK:  imbalance->PR-AUC | ranking->NDCG | regression->MAE/RMSE
                 generation->BLEU/ROUGE | RAG->faithfulness+recall
                 LAUNCH = online A/B on business metric + guardrail

DECISION TREES:
  batch vs online:   precompute+stale+cheap  vs  per-request+fresh+ms  -> HYBRID
  LLM adapt:         prompt -> RAG(knowledge) -> fine-tune(behaviour) -> pre-train
  model:             tabular->GBDT | perception/language->DNN ; baseline first
  use ML only if:    pattern + can't-rule + data + error-ok + measurable

CORE SKELETON:  candidates -> retrieval -> ranking -> re-rank  + feedback loop
SCALE 100x:     replicate | cache | batch | shard | autoscale  (systems, not model)
SERVE:          design to p99 tail ; shadow->canary->A/B ; rollback + kill switch
DRIFT (PSI):    <0.1 stable | 0.1-0.25 moderate | >=0.25 major
                data drift P(X) (retrain) vs concept drift P(Y|X) (new labels)

STUDY:  drill flash cards | redraw from memory | say the WHY | space it out
        12-week deep plan  OR  2-week crash plan (§22.7)
SENIOR: breadth + own trade-offs ; connect ML <-> systems <-> business ; design for failure
```

---

> **Next module:** *Module 23 — Capstone & Final Assessment.* You have the map;
> now you drive the whole route unaided. Module 23 puts you through a full-length,
> timed capstone design plus a final self-assessment, so you can prove — to
> yourself and to an interviewer — that the 7-step spine and every pattern in this
> revision are truly automatic.
