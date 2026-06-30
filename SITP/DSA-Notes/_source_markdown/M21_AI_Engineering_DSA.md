---
title: "Module 21 — AI Engineering DSA"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 21 — AI Engineering DSA

> **Why this module.**
> Modern AI systems (LLMs, RAG, recommendation, search) are built on classic data
> structures and algorithms applied at scale. If you're targeting **AI / ML
> engineering** (OpenAI, Anthropic, NVIDIA, or any company shipping LLM features),
> you need the DSA *behind* embeddings, vector search, and decoding. This is the
> bridge from M1–M18 to AI infrastructure.

This module is **P1 for AI roles**, P2 otherwise.

> **How to read.** The data structure / algorithm, what it powers, and the
> trade-offs.

---

## 21.1 Embeddings & Vector Search

Text, images, and audio are turned into **embeddings** — fixed-length vectors
(e.g. 768 or 1536 dimensions) where **semantic similarity = geometric
closeness**.

![Vector search: embed inputs into vectors; find nearest neighbours by cosine/dot/Euclidean; ANN makes it scale.](images/136_vector_search.png)

- **Similarity metrics:** **cosine** (angle, the most common for text), **dot
  product**, **Euclidean (L2)**.
- **Exact k-NN** is **O(n·d)** per query (n vectors, d dims) — fine for thousands,
  hopeless for billions.
- **The fix: Approximate Nearest Neighbour (ANN)** — trade a tiny bit of recall
  for sublinear search.

### MCQs

1. Most common text-similarity metric? → **cosine similarity**.
2. Exact k-NN cost per query? → **O(n·d)** (too slow at scale).
3. What does an embedding capture? → **semantic similarity as geometric
   distance**.

---

## 21.2 ANN Algorithms (the heart of vector DBs)

| Method | Idea | Trade-off |
|---|---|---|
| **HNSW** | layered "small-world" graph; greedy search dropping levels | best recall/speed; **production default**; more memory |
| **IVF** (inverted file) | cluster vectors (k-means); search only the nearest clusters | fast; tune #clusters probed (`nprobe`) |
| **PQ** (product quantization) | compress vectors into codes | huge memory savings; some accuracy loss |
| **LSH** | hash so near vectors collide | older; simpler; lower recall |

### HNSW in detail

![HNSW: a layered navigable small-world graph; start at the sparse top layer, greedily hop toward the query, drop down, repeat (~O(log n)).](images/137_hnsw.png)

A **hierarchy of graphs**: the top layer is sparse (long-range links), lower
layers denser. Search **starts at the top, greedily hops toward the query, drops
a level, repeats** → about **O(log n)** hops. It's essentially a **skip list for
high-dimensional space** (Module 17).

- **Libraries:** **FAISS** (Meta), ScaNN (Google); **vector DBs:** Pinecone,
  Milvus, Weaviate, Qdrant, **pgvector**.
- **KD-trees (Module 17) fail in high dimensions** (curse of dimensionality) → ANN
  graphs/quantization win.

### MCQs

1. Production-default ANN method? → **HNSW**.
2. HNSW is analogous to which 1-D structure? → a **skip list**.
3. PQ trades what for what? → **memory** for a little **accuracy**.

---

## 21.3 RAG (Retrieval-Augmented Generation)

The dominant pattern for grounding LLMs in your data:

```text
1. Offline: chunk documents -> embed each chunk -> store vectors in an ANN index
2. Query time:
   embed the user query  ->  ANN search (top-k similar chunks)
   ->  put those chunks in the prompt as context  ->  LLM generates an answer
```

- **The DSA:** chunking (sliding window over text), embedding store (vector DB +
  HNSW), top-k retrieval (heap / ANN), often **re-ranking** the candidates.
- **Why it works:** keeps the LLM's context **grounded + up-to-date** without
  retraining; reduces hallucination.

### MCQs

1. RAG retrieval uses which search? → **ANN (vector search)**.
2. What does RAG avoid vs fine-tuning? → **retraining** the model.
3. Top-k selection structure? → **heap / ANN index**.

---

## 21.4 Tokenization & LLM Decoding Data Structures

### Tokenization (BPE)

LLMs read **tokens**, not characters. **Byte-Pair Encoding (BPE)** builds the
vocabulary by **repeatedly merging the most frequent adjacent pair** of
tokens — using **hashmaps** (pair frequencies) and often **tries** for the merge
table. (Conceptually like Huffman's "merge frequent things", Module 11.)

### Beam Search (decoding)

![Beam search keeps the top-k highest-probability partial sequences at each step, pruning the rest.](images/138_beam_search.png)

At each step, an LLM has a probability over the next token. **Beam search** keeps
the **top-k partial sequences** (beam width k), expands each, and again keeps the
best k → better than greedy (k=1) but costs k×.

- **Alternatives:** **top-k sampling**, **nucleus / top-p sampling** (sample from
  the smallest set of tokens whose probability ≥ p) — used for *creative* output;
  beam search for *deterministic* tasks (translation).
- **KV-cache:** during generation, cache each layer's key/value tensors so each
  new token is **O(1)** in attention over the past instead of recomputing — a
  classic **memoization** (Module 14) applied to transformers.

### MCQs

1. BPE merges what each step? → the **most frequent adjacent pair** (hashmap).
2. Beam width k=1 is just? → **greedy decoding**.
3. KV-cache is an instance of? → **memoization**.

---

## 21.5 Other AI-Infra DSA (brief)

- **Recommendation:** candidate generation via ANN + ranking; **graphs** for
  collaborative filtering; **heaps** for top-N.
- **Feature stores / dedup:** **Bloom filters / HyperLogLog** (Module 7) for "seen
  before?" and cardinality at scale.
- **Streaming / counts:** **Count-Min Sketch** for approximate frequencies.
- **GPU/perf (NVIDIA):** memory coalescing & cache locality (Module 1) decide
  kernel speed; data layout (SoA vs AoS) matters.

---

## Module 21 — Concept Review (one page)

- **Embeddings:** semantic similarity = vector closeness (cosine/dot/L2); exact
  k-NN O(n·d) too slow.
- **ANN:** HNSW (graph, production default ≈ high-D skip list), IVF (clusters), PQ
  (compression), LSH (older); FAISS / vector DBs.
- **RAG:** chunk → embed → ANN retrieve top-k → LLM context; grounds the model
  without retraining.
- **Tokenization:** BPE merges frequent pairs (hashmap/trie). **Decoding:** beam
  search keeps top-k sequences; top-k/top-p sampling for creativity; **KV-cache** =
  memoization.
- **Infra:** ANN + heaps (recsys), Bloom/HLL/CMS (scale), cache locality (GPU).

## Module 21 — Flash Cards

- Q: Why ANN over exact k-NN? **A: exact is O(n·d); ANN is sublinear.**
- Q: Production ANN method? **A: HNSW (≈ high-D skip list).**
- Q: RAG pipeline? **A: embed query → ANN top-k → LLM context.**
- Q: BPE merges? **A: most frequent adjacent token pair.**
- Q: KV-cache = ? **A: memoization in transformer attention.**
- Q: Beam width 1 = ? **A: greedy decoding.**

## Module 21 — Pattern Recognition

- "Find similar items at scale" → **embeddings + ANN (HNSW)**.
- "Ground an LLM in my docs" → **RAG (vector retrieval)**.
- "Pick best next tokens / sequences" → **beam search / sampling**.
- "Seen-before / approximate counts at scale" → **Bloom / HLL / Count-Min**.
- "Top-N recommendations" → **ANN + heap**.

## Module 21 — Interview Questions (AI-eng)

1. *Design semantic search over 1B documents.* → embeddings + HNSW/IVF-PQ + sharding.
2. *Build a RAG pipeline.* → chunk/embed/index/retrieve/re-rank/generate.
3. *Why does KD-tree fail for embeddings?* → curse of dimensionality → ANN.
4. *Greedy vs beam vs sampling decoding — trade-offs?*

## Module 21 — GATE / SEBI / RBI / ISRO Perspective

- Not in classic syllabi, but **vector search / ANN / RAG** are increasingly
  relevant to applied-AI and data-engineering roles (and modern IT exams' GK
  sections). The underlying DSA (graphs, heaps, hashing, memoization) is all from
  M1–M18.

---

*End of Module 21. Next: Module 22 — System Design Connections (why Redis uses
skip lists, DBs use B+ trees, Linux uses RB-trees, Git uses DAGs) — with visuals.*
