---
title: "Module 21 — Hands-On Projects"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 21 — Hands-On Projects

> **Why this module exists.**
> You have read twenty modules of theory. But an interviewer — and a real job —
> asks a harder question: *can you actually build the thing?* This module turns
> theory into seven end-to-end projects you can build, run, and talk about.
> Each project is a small but complete ML system: it has an architecture, a tech
> stack, real code structure, an evaluation plan, and deployment notes. These are
> the exact systems that show up as case studies in Modules 12–16 — here we get
> our hands dirty. Building even three of these deeply will do more for your
> interviews than re-reading any chapter. **Talk is cheap; a running system is
> proof.**

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
sketch the architecture of each of the seven systems from memory; name the tech
stack and justify each choice; write the *skeleton* of the core code (candidate
generation, an embedding index, a RAG loop, a streaming feature job, a feature
store read, an A/B test, a batched LLM server); describe how you would *evaluate*
each system offline and online; and explain how you would *deploy* it and what
breaks at scale. In short: turn every design answer into something you could ship.

> **How to read this module.** Each project follows the same shape:
> **problem → architecture (a diagram) → tech stack → code skeleton → evaluation
> → deployment → what breaks at scale.** The code is deliberately a *skeleton* —
> the key structure and glue, not a full app — so you learn the shape without
> drowning in boilerplate. Cross-links point back to the module where the theory
> lives.

---

## Project 1 — Movie / Product Recommender (Candidate Generation + Ranking)

### The problem

Given a user, pick the ~10 items (movies, products) most likely to be clicked or
watched, out of a catalogue of *millions*. You cannot score millions of items per
request under a 100 ms budget, so real recommenders use **two stages**: a cheap
**candidate generation** step that narrows millions → a few hundred, then an
expensive **ranking** step that carefully orders those few hundred. *(Full theory
in **Module 12**.)*

### Architecture

![Two-stage recommender architecture: a two-tower retrieval model generates a few hundred candidates from millions of items via an ANN index, then a ranking model scores and orders them into a final top-10 list served to the user.](images/m21_01_recommender.png)

### Tech stack

- **Retrieval:** a two-tower model (user tower + item tower) in PyTorch or
  TensorFlow; item vectors indexed in **FAISS** (or ScaNN) for fast
  approximate-nearest-neighbour (ANN) lookup.
- **Ranking:** gradient-boosted trees (LightGBM/XGBoost) or a small DNN.
- **Features:** a feature store (Project 5) for user + item features.
- **Serving:** FastAPI/gRPC service; item index refreshed in batch nightly.

### Code skeleton

```python
import torch, torch.nn as nn
import faiss, numpy as np

# --- 1. Two-tower retrieval model ---
class TwoTower(nn.Module):
    def __init__(self, n_users, n_items, dim=64):
        super().__init__()
        self.user_emb = nn.Embedding(n_users, dim)
        self.item_emb = nn.Embedding(n_items, dim)

    def user_vec(self, u): return self.user_emb(u)
    def item_vec(self, i): return self.item_emb(i)

    def forward(self, u, i):
        # dot product = predicted affinity
        return (self.user_vec(u) * self.item_vec(i)).sum(-1)

# Train with in-batch negatives (sampled softmax) — Module 12.

# --- 2. Build ANN index over ALL item vectors (offline / nightly) ---
item_vectors = model.item_emb.weight.detach().numpy().astype("float32")
index = faiss.IndexFlatIP(item_vectors.shape[1])   # inner-product = cosine-ish
index.add(item_vectors)

# --- 3. Serve: retrieve candidates, then rank ---
def recommend(user_id, k_cand=300, k_final=10):
    uvec = model.user_vec(torch.tensor([user_id])).detach().numpy()
    _, cand_ids = index.search(uvec.astype("float32"), k_cand)   # millions -> 300
    cand_ids = cand_ids[0]

    feats = build_features(user_id, cand_ids)      # from feature store
    scores = ranker.predict(feats)                 # LightGBM ranking model
    top = cand_ids[np.argsort(-scores)[:k_final]]
    return top.tolist()
```

### Evaluation plan

- **Offline (retrieval):** Recall@K — did the true clicked item land in the top-K
  candidates? **Offline (ranking):** NDCG@10, MAP, AUC.
- **Online (the truth):** A/B test on click-through rate (CTR), watch time, or
  revenue per session (see Project 6 and **Module 7**). Guard against the
  offline–online gap.

### Deployment notes

- Rebuild the FAISS index nightly in batch; hot-swap it behind the serving API.
- Cache per-user candidates for a short TTL to cut latency.
- **What breaks at scale:** index memory grows with the catalogue → shard the ANN
  index or use IVF/PQ compression; popularity feedback loops (Module 12) push the
  same items → add exploration and diversity re-ranking.

---

## Project 2 — Semantic Search Engine with a Vector DB

### The problem

Keyword search fails when the user's words don't match the document's words
("car" vs "automobile"). **Semantic search** embeds both the query and the
documents into the same vector space, so *meaning* — not exact words — drives
the match. The core loop is **embed → index → query by nearest neighbour**.
*(Ranking theory in **Module 13**; embeddings in **Module 16**.)*

### Architecture

![Semantic search architecture: documents are embedded by an encoder model and stored in a vector index (FAISS/HNSW); at query time the query is embedded and the nearest-neighbour vectors are retrieved and returned as ranked results.](images/m21_02_semantic_search.png)

### Tech stack

- **Embeddings:** a sentence-transformer (e.g. `all-MiniLM`) or a hosted
  embedding API.
- **Index:** **FAISS** or **HNSW** (via `hnswlib`) for in-process ANN; or a
  managed vector DB (Qdrant, Weaviate, pgvector) for persistence + filters.
- **Serving:** FastAPI; optional cross-encoder re-ranker for the top results.

### Code skeleton

```python
from sentence_transformers import SentenceTransformer
import hnswlib, numpy as np

encoder = SentenceTransformer("all-MiniLM-L6-v2")

# --- 1. Offline: embed and index the corpus ---
docs = load_documents()                       # list[str]
emb = encoder.encode(docs, normalize_embeddings=True)  # (N, dim)

index = hnswlib.Index(space="cosine", dim=emb.shape[1])
index.init_index(max_elements=len(docs), ef_construction=200, M=16)
index.add_items(emb, np.arange(len(docs)))
index.set_ef(64)                              # higher ef = better recall, slower

# --- 2. Online: embed query, retrieve nearest neighbours ---
def search(query, k=10):
    qv = encoder.encode([query], normalize_embeddings=True)
    ids, dists = index.knn_query(qv, k=k)
    return [(docs[i], 1 - d) for i, d in zip(ids[0], dists[0])]

# --- 3. Optional: cross-encoder re-rank top-k for precision (Module 13) ---
```

### Evaluation plan

- **Retrieval quality:** Recall@K and MRR on a labelled query→relevant-doc set.
- **Ranking quality:** NDCG@10 after the (optional) cross-encoder re-rank.
- **Latency:** p99 of embed + ANN query; tune `ef`/`M` for the recall–latency
  trade-off.

### Deployment notes

- Keep the *same* embedding model in indexing and querying — a version mismatch
  is a silent skew bug.
- Re-embed and rebuild when you change the model; version the index.
- **What breaks at scale:** billions of vectors won't fit RAM → use a managed
  vector DB with disk-backed indexes and PQ compression; add metadata filters so
  ANN + filters happen together.

---

## Project 3 — RAG Chatbot over a Document Corpus (with Evals)

### The problem

A raw LLM hallucinates and knows nothing about *your* private documents.
**Retrieval-Augmented Generation (RAG)** fixes both: chunk your documents, embed
and index them, retrieve the chunks relevant to a question, and stuff them into
the prompt so the LLM answers *from your data* with citations. The hard,
senior-level part is **evaluating** it. *(Full theory in **Module 16**.)*

### Architecture

![RAG chatbot architecture: documents are chunked, embedded and stored in a vector store; a user question is embedded, relevant chunks are retrieved, combined with the question into a prompt, and an LLM generates a grounded answer with citations; an eval harness scores faithfulness and relevance.](images/m21_03_rag_chatbot.png)

### Tech stack

- **Chunk + embed:** a text splitter + sentence-transformer / embedding API.
- **Vector store:** FAISS / pgvector / Qdrant (from Project 2).
- **Generation:** an LLM via API (Claude, or an open model served in Project 7).
- **Evals:** a small labelled QA set + an LLM-as-judge for faithfulness.

### Code skeleton

```python
def chunk(text, size=800, overlap=100):
    # split into overlapping windows so context isn't cut mid-idea
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+size]); i += size - overlap
    return out

# --- Index (offline) ---
chunks = [c for d in docs for c in chunk(d)]
store = build_vector_store(chunks, encoder)     # reuse Project 2's index

# --- Answer (online) ---
def answer(question, k=4):
    ctx = store.search(question, k=k)            # top-k relevant chunks
    prompt = (
        "Answer ONLY from the context. Cite chunk ids. "
        "If the answer isn't present, say you don't know.\n\n"
        f"Context:\n{format_chunks(ctx)}\n\nQuestion: {question}"
    )
    resp = llm.generate(prompt)
    return resp, [c.id for c in ctx]

# --- Eval harness (the senior part) ---
def evaluate(qa_set):
    faith, relev = [], []
    for q, gold in qa_set:
        pred, cited = answer(q)
        faith.append(judge_faithful(pred, cited))   # LLM-judge: grounded?
        relev.append(judge_relevant(pred, gold))    # matches gold answer?
    return {"faithfulness": mean(faith), "answer_relevancy": mean(relev)}
```

### Evaluation plan

- **Retrieval:** context Recall@K and precision — are the right chunks retrieved?
- **Generation:** *faithfulness* (is every claim grounded in retrieved context?),
  *answer relevancy*, and citation correctness — scored by an LLM-judge plus a
  human-checked gold set.
- **Guardrails:** track "I don't know" rate; a good RAG abstains rather than
  hallucinates.

### Deployment notes

- Cache embeddings and frequent Q→A pairs; stream tokens to the user for
  perceived speed.
- Re-index when documents change; keep chunk→source mapping for citations.
- **What breaks at scale:** retrieval quality dominates — bad chunks → bad
  answers regardless of the LLM; add re-ranking, hybrid (keyword + vector)
  search, and monitor faithfulness drift over time (**Module 10**).

---

## Project 4 — Real-Time Fraud Detection Pipeline (Streaming Features)

### The problem

Fraud must be caught in the *milliseconds* a payment is happening, not in
tonight's batch job. That means computing features over a live event stream —
"how many transactions from this card in the last 60 seconds?" — and scoring
them instantly. This is a **streaming** system. *(Data engineering in **Module
4**; monitoring & drift in **Module 10**.)*

### Architecture

![Real-time fraud pipeline: transaction events flow through Kafka into a Flink streaming job that computes windowed aggregate features written to an online store; a scoring service reads features, runs the fraud model, and returns allow/block/review decisions with alerting and feedback to retraining.](images/m21_04_fraud_pipeline.png)

### Tech stack

- **Ingest:** **Kafka** (transaction event stream).
- **Streaming features:** **Flink** (or Spark Structured Streaming / Kafka
  Streams) for windowed aggregations.
- **Online store:** Redis / DynamoDB for low-latency feature reads.
- **Model:** gradient-boosted trees or a small NN; served behind a scoring API.

### Code skeleton

```python
# --- Streaming feature job (PyFlink, conceptual) ---
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.common.time import Time

env = StreamExecutionEnvironment.get_execution_environment()
txns = env.add_source(kafka_consumer("transactions"))

# feature: count + sum of txns per card over a sliding 60s window
features = (
    txns.key_by(lambda t: t.card_id)
        .window(SlidingEventTimeWindows.of(Time.seconds(60), Time.seconds(10)))
        .aggregate(CountAndSum())          # -> (card_id, cnt_60s, amt_60s)
)
features.add_sink(redis_sink("online_features"))   # write to online store

# --- Scoring service (online, per transaction) ---
def score(txn):
    f = redis.hgetall(f"feat:{txn.card_id}")        # fresh streaming features
    x = assemble(txn, f)                            # + static card/user features
    p = fraud_model.predict_proba(x)[1]
    if   p > 0.95: return "BLOCK"
    elif p > 0.70: return "REVIEW"                  # human-in-the-loop
    else:          return "ALLOW"
```

### Evaluation plan

- **Offline:** precision/recall and **PR-AUC** (fraud is highly imbalanced —
  accuracy is useless). Tune the threshold on the *cost* of a false positive
  (blocking a real customer) vs a false negative (letting fraud through).
- **Online:** shadow mode first; track fraud caught, false-block rate, and dollar
  loss; alert on drift in feature distributions.

### Deployment notes

- Keep the **same** feature definitions in the Flink job and any training job to
  avoid training-serving skew (**Module 5**).
- Roll out with shadow mode + a kill switch.
- **What breaks at scale:** stream backpressure and late events → use event-time
  windows + watermarks; hot keys (one huge merchant) skew partitions → salt keys;
  fraudsters adapt fast → frequent retraining and drift alarms (**Module 10**).

---

## Project 5 — Feature Store Mini-Implementation (Offline + Online)

### The problem

The single most common ML production bug is **training-serving skew**: a feature
is computed one way in the training pipeline and a different way in the live
service. A **feature store** solves this by defining each feature *once* and
serving it to both — from an **offline store** (big historical table, for
training) and an **online store** (fast key-value store, for serving) — with
correct **point-in-time** joins so no future data leaks. *(Full theory in
**Module 5**.)*

### Architecture

![Feature store architecture: raw data feeds feature pipelines that materialize features into both an offline store (historical, for point-in-time training joins) and an online store (low-latency key-value, for serving); a shared feature definition guarantees training and serving use identical logic.](images/m21_05_feature_store.png)

### Tech stack

- **Offline store:** Parquet / a data warehouse (BigQuery, Snowflake) — big,
  historical, cheap.
- **Online store:** Redis / DynamoDB — small, fresh, millisecond reads.
- **Definitions:** a single Python/YAML spec (or the open-source **Feast**).

### Code skeleton

```python
import pandas as pd

# --- 1. One feature definition, used by BOTH stores ---
FEATURES = ["user_avg_order", "user_orders_7d"]

# --- 2. Offline: POINT-IN-TIME join (no leakage!) ---
def get_training_frame(labels: pd.DataFrame, feats: pd.DataFrame):
    # for each labelled event, attach the feature value AS OF that timestamp
    labels = labels.sort_values("event_ts")
    feats  = feats.sort_values("feature_ts")
    return pd.merge_asof(
        labels, feats,
        left_on="event_ts", right_on="feature_ts",   # <= as-of, never future
        by="user_id", direction="backward",
    )

# --- 3. Materialize latest values to the ONLINE store ---
def materialize(feats: pd.DataFrame, redis):
    latest = feats.sort_values("feature_ts").groupby("user_id").tail(1)
    for _, r in latest.iterrows():
        redis.hset(f"user:{r.user_id}", mapping={f: r[f] for f in FEATURES})

# --- 4. Online read at serving time ---
def get_online_features(user_id, redis):
    return redis.hgetall(f"user:{user_id}")   # same features as training
```

### Evaluation plan

- **Correctness:** assert offline-computed and online-served values match for the
  same entity + timestamp (skew check).
- **Leakage test:** confirm the point-in-time join never pulls a feature stamped
  *after* the label event.
- **Freshness / latency:** online read p99; staleness of materialized values.

### Deployment notes

- Schedule materialization jobs; monitor feature freshness and null rates.
- Version feature definitions; deprecate features safely.
- **What breaks at scale:** online store cost/size for millions of entities → TTL
  and tiering; backfilling history for a new feature is expensive → design
  features to be reusable across models.

---

## Project 6 — A/B Testing & Monitoring Dashboard

### The problem

Offline metrics lie. The only way to know a model actually helps is to run it on
real users and compare against the old one — an **A/B test** — and to *keep
watching* it in production for drift and degradation. This project builds the
experiment logic and a monitoring dashboard. *(Metrics in **Module 7**;
monitoring in **Module 10**.)*

### Architecture

![A/B testing and monitoring dashboard: incoming traffic is split by a deterministic hash into control and treatment variants, each served by a different model; outcomes are logged, aggregated into metrics with confidence intervals, and displayed on a dashboard tracking business KPIs, model performance, and drift.](images/m21_06_ab_dashboard.png)

### Tech stack

- **Assignment:** deterministic hashing (user_id → bucket) for stable, sticky
  splits.
- **Logging:** an event pipeline (Kafka → warehouse).
- **Stats:** two-proportion z-test / t-test with confidence intervals; sequential
  tests to avoid peeking.
- **Dashboard:** Streamlit / Grafana / Metabase over the metrics table.

### Code skeleton

```python
import hashlib
from math import sqrt
from scipy import stats

# --- 1. Deterministic, sticky assignment ---
def variant(user_id, salt="rec_v2", split=0.5):
    h = int(hashlib.md5(f"{salt}:{user_id}".encode()).hexdigest(), 16)
    return "treatment" if (h % 1000) / 1000 < split else "control"

# --- 2. Serve the right model, log the outcome ---
def handle(user_id, request):
    v = variant(user_id)
    model = treatment_model if v == "treatment" else control_model
    pred = model.predict(request)
    log_event(user_id, v, pred)      # outcome (click/convert) logged async
    return pred

# --- 3. Analyze: is treatment better, and is it significant? ---
def ab_result(conv_c, n_c, conv_t, n_t):
    p_c, p_t = conv_c / n_c, conv_t / n_t
    p = (conv_c + conv_t) / (n_c + n_t)
    se = sqrt(p * (1 - p) * (1/n_c + 1/n_t))
    z = (p_t - p_c) / se
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"lift": p_t - p_c, "z": z, "p_value": pval,
            "significant": pval < 0.05}
```

### Evaluation plan

- **Primary metric:** the business KPI (CTR, conversion, revenue/session) with a
  confidence interval — not offline accuracy.
- **Guardrail metrics:** latency, error rate, revenue must not regress.
- **Validity:** check sample-ratio mismatch (did the 50/50 split actually
  happen?), run for full business cycles, avoid peeking (use sequential tests).

### Deployment notes

- Make assignment sticky so a user always sees the same variant.
- Add monitors for drift (feature and prediction distributions) and auto-alerts.
- **What breaks at scale:** network effects break independence (marketplaces) →
  use cluster/geo randomization; many simultaneous experiments interact → an
  experimentation platform with mutual-exclusion groups.

---

## Project 7 — LLM-Serving Setup with Batching & Caching

### The problem

LLMs are huge and slow, and GPUs are expensive. Serving them naively — one
request at a time — wastes almost all the GPU. Two techniques make LLM serving
affordable: **continuous batching** (pack many requests through the GPU together)
and **caching** (KV-cache within a generation; a response/prompt cache across
requests). *(Serving theory in **Module 8**; LLM internals in **Module 16**.)*

### Architecture

![LLM serving architecture: incoming requests hit a cache layer (exact and semantic); misses enter a dynamic batching queue that groups requests for the GPU-backed model server with KV-cache and continuous batching; generated tokens stream back and populate the cache.](images/m21_07_llm_serving.png)

### Tech stack

- **Engine:** vLLM or TGI (they implement continuous batching + paged KV-cache).
- **Cache:** Redis for exact-match prompt/response cache; a vector index for
  *semantic* cache (near-duplicate prompts).
- **Serving:** an async API gateway (FastAPI) with a batching queue; token
  streaming (SSE) to the client.

### Code skeleton

```python
import asyncio, hashlib

# --- 1. Cache layer (exact + optional semantic) ---
def cache_key(prompt): return hashlib.sha256(prompt.encode()).hexdigest()

async def generate(prompt):
    key = cache_key(prompt)
    if (hit := await redis.get(key)):
        return hit                       # exact-match cache hit -> ~0 GPU cost
    out = await batched_infer(prompt)    # miss -> go to the GPU (batched)
    await redis.set(key, out, ex=3600)
    return out

# --- 2. Dynamic batching queue: group requests within a small time window ---
class BatchQueue:
    def __init__(self, max_batch=32, wait_ms=10):
        self.q, self.max_batch, self.wait = [], max_batch, wait_ms / 1000

    async def submit(self, prompt):
        fut = asyncio.get_event_loop().create_future()
        self.q.append((prompt, fut))
        return await fut

    async def run(self):                 # background loop
        while True:
            await asyncio.sleep(self.wait)
            if not self.q: continue
            batch = self.q[:self.max_batch]; self.q = self.q[self.max_batch:]
            prompts = [p for p, _ in batch]
            outputs = llm.generate(prompts)          # ONE batched GPU call
            for (_, fut), out in zip(batch, outputs):
                fut.set_result(out)
```

### Evaluation plan

- **Throughput:** tokens/second and requests/second at a fixed GPU count.
- **Latency:** time-to-first-token (TTFT) and inter-token latency; watch the
  batching-induced tail (p99).
- **Cost & quality:** \$ per 1k tokens; cache hit rate; and an output-quality
  check so batching/quantization didn't degrade responses.

### Deployment notes

- Autoscale GPU replicas on queue depth; put a token-bucket rate limiter in front.
- Use quantization (INT8/FP8) and paged KV-cache to fit bigger models / batches.
- **What breaks at scale:** the latency–throughput trade-off — bigger batches
  raise throughput but hurt TTFT → cap batch size and wait window; long contexts
  blow up KV-cache memory → paged attention and context limits; cold model loads
  are slow → keep replicas warm.

---

## Module 21 — Interview Mapping (what companies probe)

| Company | How this module shows up | Junior answer | Staff answer |
|---------|--------------------------|---------------|--------------|
| **Google / Meta** | "Design YouTube/newsfeed recommendations" | One model scoring everything | Two-stage retrieval + ranking, ANN index, hybrid batch/online (Project 1) |
| **OpenAI / Anthropic** | "Build a chatbot over our docs; how do you eval it?" | "Just prompt the LLM" | RAG with retrieval + faithfulness evals and abstention (Project 3) |
| **Stripe / Uber** | "Detect fraud in real time" | Nightly batch model | Kafka+Flink streaming features, online store, shadow rollout (Project 4) |
| **Any infra role** | "Serve an LLM cheaply at scale" | One request per GPU call | Continuous batching + KV-cache + prompt/semantic cache (Project 7) |
| **All** | "How do you know it works in production?" | Offline accuracy | A/B test on the business KPI + drift monitoring (Project 6) |

**The pattern interviewers reward:** you can move from a whiteboard box to a
*runnable* design — naming the index, the store, the queue, the eval metric — and
you connect each choice to latency, cost, and the business metric.

---

## Module 21 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT / GATE / ISRO:** hands-on system-building is **essentially
  interview- and job-only**; written exams do not ask you to design a RAG eval
  harness or a batching queue. The *underlying concepts* (ANN search, streaming
  windows, point-in-time joins, A/B statistical tests) can appear as short
  definitional or numerical questions — study those in Modules 4, 5, 7, 12, 16.
- **Takeaway:** treat this module as portfolio and interview preparation, not exam
  cramming. Building two or three of these projects is the highest-leverage thing
  you can do for an AI/MLE role.

---

## Module 21 — Common Mistakes & Misconceptions

1. **Scoring millions of items per request.** No — use two stages: cheap
   candidate generation, then expensive ranking (Project 1).
2. **Different embedding models for indexing vs querying.** A silent skew bug in
   semantic search and RAG — always use the *same* model (Projects 2, 3).
3. **"RAG works, ship it" with no evals.** Faithfulness and retrieval quality must
   be measured; a RAG that hallucinates confidently is worse than one that
   abstains (Project 3).
4. **Fraud on nightly batch.** Fraud needs streaming features and instant scoring;
   batch is far too stale (Project 4).
5. **Point-in-time leakage.** Joining the *latest* feature value into training
   instead of the value *as of* the event time leaks the future (Project 5).
6. **Peeking at A/B tests.** Stopping the moment it looks significant inflates
   false positives; use fixed horizons or sequential tests (Project 6).
7. **One-request-per-GPU LLM serving.** Wastes ~90% of the GPU; use continuous
   batching and caching (Project 7).

---

## Module 21 — MCQs (with answers & explanations)

**Q1.** Why do large recommenders use two stages (candidate generation + ranking)?
a) To use two teams
b) Because you cannot score millions of items per request under a latency budget
c) Ranking models are cheap
d) ANN indexes are inaccurate

<details><summary>Answer</summary>**b.** A cheap retrieval step narrows millions →
hundreds, then an expensive ranker orders just those. (Project 1 / Module 12.)</details>

**Q2.** In semantic search, what is the most common silent bug?
a) Using HNSW instead of FAISS
b) Different embedding models for indexing and querying
c) Normalizing vectors
d) Using cosine similarity

<details><summary>Answer</summary>**b.** Index and query embeddings must come from
the same model version, or the vector space doesn't match. (Project 2.)</details>

**Q3.** What does the "R" in RAG add over a plain LLM?
a) Faster GPUs
b) Retrieved, grounded context from your own documents, reducing hallucination
c) A bigger model
d) Reinforcement learning

<details><summary>Answer</summary>**b.** Retrieval injects relevant private context
into the prompt so answers are grounded and citable. (Project 3 / Module 16.)</details>

**Q4.** Why can't a nightly batch job power fraud detection?
a) Batch is too expensive
b) The prediction must happen in milliseconds as the transaction occurs
c) Kafka is required by law
d) Batch jobs can't use models

<details><summary>Answer</summary>**b.** Fraud is a streaming problem — features
and scoring must be near real-time. (Project 4 / Module 10.)</details>

**Q5.** A point-in-time join in a feature store prevents:
a) Slow reads  b) Data leakage from future feature values  c) Duplicate rows
d) Cache misses

<details><summary>Answer</summary>**b.** It attaches each feature's value *as of*
the event time, never a value stamped after the label. (Project 5 / Module 5.)</details>

**Q6.** Which metric should decide whether a new recommender ships?
a) Offline NDCG only
b) The online business KPI (e.g. CTR/revenue) from an A/B test
c) Model file size
d) Training accuracy

<details><summary>Answer</summary>**b.** Offline metrics can disagree with reality;
the A/B test on the business metric is the truth. (Project 6 / Module 7.)</details>

**Q7.** Continuous batching in LLM serving primarily improves:
a) Model accuracy
b) GPU utilization / throughput
c) Prompt quality
d) Disk usage

<details><summary>Answer</summary>**b.** Packing many requests through the GPU
together raises tokens/second dramatically. (Project 7 / Module 8.)</details>

**Q8.** For a highly imbalanced fraud dataset, the best offline metric is:
a) Accuracy  b) PR-AUC / precision-recall  c) Training loss  d) R²

<details><summary>Answer</summary>**b.** With rare positives, accuracy is
misleading; precision/recall and PR-AUC reflect real performance. (Project 4.)</details>

---

## Module 21 — Design Exercises (easy → hard)

- **Easy.** For the recommender (Project 1), pick Recall@K vs NDCG for each stage
  and justify which stage each metric evaluates.
- **Easy.** For semantic search, describe one experiment to tune the HNSW `ef`
  parameter for a recall–latency target.
- **Medium.** Extend the RAG chatbot with a *re-ranker* and *hybrid* (keyword +
  vector) retrieval. Where do they slot into the code skeleton, and what metric
  should improve?
- **Medium.** Design the sliding-window features for fraud on the *merchant* key
  as well as the card key. What hot-key problem appears and how do you fix it?
- **Hard.** Add a new feature to the feature store that needs six months of
  history. Describe the backfill, the point-in-time correctness check, and the
  materialization schedule.
- **Hard.** Your LLM service must hit TTFT < 300 ms *and* maximize throughput.
  Explain the batch-size / wait-window trade-off and how caching changes the math.

---

## Module 21 — Concept Review (one page)

- **Recommender (P1):** two stages — cheap **candidate generation** (two-tower +
  ANN) narrows millions→hundreds; expensive **ranking** orders them. Eval:
  Recall@K then NDCG; ship on an A/B test.
- **Semantic search (P2):** **embed → index (FAISS/HNSW) → query by nearest
  neighbour**. Same embedding model everywhere. Eval: Recall@K, MRR, latency.
- **RAG chatbot (P3):** **chunk → embed → retrieve → generate with citations**;
  the senior skill is **evals** (faithfulness, retrieval recall, abstention).
- **Fraud (P4):** **Kafka → Flink windowed features → online store → instant
  scoring**; PR-AUC and cost-based thresholds; shadow rollout + drift alarms.
- **Feature store (P5):** define once, serve to **offline** (point-in-time joins,
  no leakage) and **online** (ms reads); kills training-serving skew.
- **A/B + monitoring (P6):** sticky hashed assignment, log outcomes, test the
  **business KPI** with confidence intervals; guardrails + drift monitors.
- **LLM serving (P7):** **continuous batching + KV-cache + prompt/semantic
  cache**; watch throughput vs TTFT; quantize to fit bigger batches.

---

## Module 21 — Flash Cards (Q → A)

1. Why two-stage recommenders? → *Can't score millions/request; retrieve cheaply,
   then rank carefully.*
2. Semantic search core loop? → *Embed → index → nearest-neighbour query.*
3. Biggest RAG mistake? → *Shipping without faithfulness/retrieval evals.*
4. Why streaming for fraud? → *Must score in milliseconds on fresh windowed
   features.*
5. What does a point-in-time join prevent? → *Future-value data leakage.*
6. What decides if a model ships? → *The online business KPI from an A/B test.*
7. Two techniques that make LLM serving cheap? → *Continuous batching + caching
   (with KV-cache).*
8. Right offline metric for imbalanced fraud? → *PR-AUC / precision-recall, not
   accuracy.*

---

## Module 21 — Pattern Recognition (how to spot it in an interview)

- Hear **"recommend from a huge catalogue"** → two-stage retrieval + ranking with
  an ANN index (P1).
- Hear **"search by meaning / find similar"** → embeddings + vector index (P2).
- Hear **"answer from our documents / reduce hallucination"** → RAG *and* an eval
  plan (P3).
- Hear **"real-time / within milliseconds / as it happens"** → Kafka + streaming
  features + online store (P4).
- Hear **"features differ in training vs serving"** → feature store + point-in-time
  joins (P5).
- Hear **"how do you know it works / does it move the metric?"** → A/B test on the
  business KPI + monitoring (P6).
- Hear **"serve an LLM cheaply / at scale"** → continuous batching + caching (P7).

---

## Module 21 — Revision Notes / Mini Cheat Sheet

```
P1 RECOMMENDER   two-tower + FAISS (candidates) -> LightGBM (rank)   | Recall@K, NDCG | A/B
P2 SEMANTIC SRCH embed -> HNSW/FAISS -> kNN query | same model both sides | Recall@K, MRR
P3 RAG CHATBOT   chunk->embed->retrieve->generate+cite | EVAL faithfulness+recall+abstain
P4 FRAUD         Kafka -> Flink windowed feats -> online store -> score(ms) | PR-AUC | shadow
P5 FEATURE STORE define once -> offline (point-in-time, no leak) + online (ms reads)
P6 A/B + MONITOR hashed sticky split -> log -> z-test/CI on BUSINESS KPI + drift monitors
P7 LLM SERVING   continuous batching + KV-cache + prompt/semantic cache | throughput vs TTFT

GOLDEN RULES
  two stages when catalogue is huge (retrieve cheap, rank dear)
  same embedding model for index + query (skew kills search & RAG)
  RAG without evals is not done; measure faithfulness + retrieval recall
  fraud = streaming, not batch; imbalanced => PR-AUC + cost-based threshold
  point-in-time joins or you leak the future
  ship on the ONLINE business metric (A/B), never offline accuracy alone
  batch + cache the GPU or you burn 90% of it
```

---

> **Next module:** *Module 22 — Capstone: Putting It All Together.* We take these
> seven building blocks and assemble a single end-to-end design under realistic
> constraints — the way a full Staff-level interview or a real product launch
> actually demands.
