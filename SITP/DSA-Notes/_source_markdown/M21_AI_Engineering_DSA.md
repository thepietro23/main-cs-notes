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

#### Cosine vs dot product vs Euclidean — which and when

These three metrics feel similar but answer different questions. Learn the one-line
difference for each.

- **Cosine similarity** = the **angle** between two vectors (ignores length).
  Formula: `cos(a,b) = (a·b) / (|a|·|b|)`. Range **-1 to 1** (1 = same
  direction). Best for **text**, because a long document and a short one about the
  same topic should still match — length shouldn't matter.
- **Dot product** = `a·b = Σ aᵢbᵢ`. It mixes **angle AND length** together. If all
  vectors are **normalised** to length 1, then **dot product = cosine** (same
  ranking, less compute) — which is why many systems normalise once and then use
  the cheaper dot product.
- **Euclidean (L2) distance** = straight-line distance `√(Σ (aᵢ-bᵢ)²)`. Smaller =
  closer. Used when **absolute magnitude matters** (e.g. some image embeddings).

```text
Same direction, different length:
   a = (2, 0)      b = (6, 0)
   cosine(a,b)    = 1.0     (angle 0 -> identical topic)
   dot(a,b)       = 12      (big, because b is long)
   euclidean(a,b) = 4       (they are "far" by L2)
=> cosine says "same"; L2 says "far". Pick the metric that
   matches what you mean by "similar".
```

> **Memory hook:** *cosine = direction, L2 = distance, dot = both.* Normalise your
> vectors and cosine and dot give the same order.

- **Key fact:** on **unit-normalised** vectors, ranking by cosine, by dot product,
  and by (negative) squared-L2 all give the **same nearest neighbours** — because
  `|a-b|² = 2 - 2(a·b)` when `|a|=|b|=1`. Many vector DBs exploit this.

### MCQs

1. Most common text-similarity metric? → **cosine similarity**.
2. Exact k-NN cost per query? → **O(n·d)** (too slow at scale).
3. What does an embedding capture? → **semantic similarity as geometric
   distance**.
4. Cosine vs dot product on **normalised** vectors? → **same ranking** (cosine =
   dot when length = 1).
5. Which metric **ignores** vector length? → **cosine**.
6. Cosine range? → **-1 to 1** (1 = identical direction).

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

#### HNSW vs IVF vs LSH — side by side

The three families make different bets. HNSW builds a **graph**, IVF **partitions**
space, LSH **hashes**. Pick by your memory budget and update pattern.

| Property | **HNSW** (graph) | **IVF** (clusters) | **LSH** (hashing) |
|---|---|---|---|
| Core idea | navigable small-world graph | k-means buckets, probe nearest | hash so near points collide |
| Underlying DS | **layered graph** (≈ skip list) | inverted lists + centroids | hash tables |
| Query time | **~O(log n)** hops | O(nprobe · list size) | O(#tables) lookups |
| Recall | **highest** | high (tune `nprobe`) | lower |
| Memory | **high** (stores links) | moderate | low–moderate |
| Build time | slow (insert each node) | fast (one k-means) | fast |
| Updates/inserts | supported, incremental | needs periodic re-cluster | easy |
| Best when | recall + latency matter most | huge sets, memory-tight | very high dims, simple |

- **The key knobs:** HNSW → `M` (links per node) and `efSearch` (candidates kept);
  IVF → `nlist` (#clusters) and `nprobe` (#clusters searched). Higher = better
  recall, slower.
- **IVF + PQ is the classic billion-scale combo** (FAISS `IVF…,PQ…`): partition
  with IVF, then compress each vector with PQ to fit in RAM.

#### Product Quantization (PQ) — compress vectors to fit in RAM

A raw 768-dim `float32` vector is **~3 KB**; a billion of them is ~3 TB — too big
for memory. **PQ** shrinks each vector to a few **bytes**.

```text
PQ in one picture (split a vector into m sub-vectors):
  [   768-dim vector   ]  ->  split into m=8 chunks of 96 dims
   chunk1 chunk2 ... chunk8
     |      |          |
   k-means k-means   k-means      (each chunk has its own codebook of
     v      v          v           e.g. 256 "centroids" = 1 byte each)
    id=42  id=7  ...  id=200      -> store 8 bytes instead of 3072 bytes
=> ~384x smaller. Distance is approximated from precomputed
   centroid-distance tables (fast lookups, no full float math).
```

- **How it works:** cut the vector into **m sub-vectors**; run k-means (usually 256
  centroids → **1 byte**) on each sub-space; store only the **centroid IDs**. That's
  **m bytes per vector**.
- **Trade-off:** ~**8–64× memory savings** for a small recall drop; distances are
  **approximate**. Add a **re-rank** step on exact vectors for the final top-k.
- **Scalar quantization** is the simpler cousin: store each dim as `int8` instead of
  `float32` (4× smaller, tiny accuracy loss) — often the default first step.

#### Why vector DB internals are just graphs and trees (DSA tie)

Vector search is not new DSA — it's **M1–M18 applied in high dimensions**:

- **HNSW = a graph** (Module 10) with **skip-list layering** (Module 17): greedy
  best-first traversal, exactly like graph search toward a goal.
- **IVF = clustering + inverted lists** (the same **inverted index** search engines
  use, Module 3/22).
- **PQ = a lookup table / codebook** (hashing to centroid IDs, Module 7).
- **KD-tree / ball-tree** (space-partitioning **trees**, Module 17) work in **low**
  dimensions but collapse in high-D — which is *why* graphs (HNSW) took over.

### MCQs

1. Production-default ANN method? → **HNSW**.
2. HNSW is analogous to which 1-D structure? → a **skip list**.
3. PQ trades what for what? → **memory** for a little **accuracy**.
4. HNSW's underlying data structure? → a **layered graph**.
5. IVF's two main knobs? → **nlist** (#clusters) and **nprobe** (#probed).
6. PQ stores what per vector instead of floats? → **centroid IDs (bytes)**.
7. Billion-scale FAISS combo? → **IVF + PQ**.
8. Why do KD-trees fail for embeddings? → **curse of dimensionality**.

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

#### Chunking strategies (the part that decides RAG quality)

Chunks that are **too big** dilute the match; **too small** lose context. Chunking
is a **sliding-window** problem over text — the classic two-pointer pattern.

| Strategy | How | When to use |
|---|---|---|
| **Fixed-size** | every N tokens (e.g. 512) | simplest baseline |
| **Fixed + overlap** | N tokens, slide by N−k (overlap k) | keep context across boundaries |
| **Sentence / paragraph** | split on `.`/`\n\n` boundaries | keeps ideas whole |
| **Recursive** | try paragraph → sentence → word until it fits | good general default |
| **Semantic** | split where embedding similarity drops | best quality, more compute |

```text
Fixed window with overlap (window=100, overlap=20):
  [----- chunk 1 (0..100) -----]
                    [----- chunk 2 (80..180) -----]
                                       [--- chunk 3 (160..260) ---]
=> the 20-token overlap means a sentence split across a boundary
   still appears whole in one chunk (no lost context).
```

- **Overlap** (typically 10–20%) is the single easiest quality win — it stops a fact
  from being cut in half at a chunk edge.
- **Pitfall:** chunk by **tokens**, not characters, so a chunk never exceeds the
  embedding model's limit. Store the source doc + offsets as metadata for
  citations.
- **Re-ranking:** ANN gives ~top-50 fast (recall); a slower **cross-encoder**
  re-ranks them to the final top-5 (precision). Two-stage retrieval = fast + accurate.

### MCQs

1. RAG retrieval uses which search? → **ANN (vector search)**.
2. What does RAG avoid vs fine-tuning? → **retraining** the model.
3. Top-k selection structure? → **heap / ANN index**.
4. Cheapest chunking quality win? → **overlap** between chunks.
5. Chunking is which array pattern? → a **sliding window** over tokens.
6. Two-stage retrieval? → **ANN recall → cross-encoder re-rank**.

---

## 21.4 Tokenization & LLM Decoding Data Structures

### Tokenization (BPE)

LLMs read **tokens**, not characters. **Byte-Pair Encoding (BPE)** builds the
vocabulary by **repeatedly merging the most frequent adjacent pair** of
tokens — using **hashmaps** (pair frequencies) and often **tries** for the merge
table. (Conceptually like Huffman's "merge frequent things", Module 11.)

**Training BPE — a tiny dry run.** Start with characters, then merge the most
frequent adjacent pair, over and over:

```text
Corpus (as chars):  l o w   l o w   l o w e r   n e w e s t
Step 1: most frequent pair = ("l","o")  -> merge into "lo"
        lo w   lo w   lo w e r   n e w e s t
Step 2: most frequent pair = ("lo","w") -> merge into "low"
        low   low   low e r   n e w e s t
Step 3: most frequent pair = ("e","s")  -> merge into "es"
        low   low   low e r   n e w es t
... continue until you reach the target vocabulary size.
Each merge is one new token; the ordered list of merges is the "merge table".
```

- **Data structures:** a **hashmap** counts pair frequencies each round; the ordered
  **merge rules** are applied greedily at encode time. Fast BPE encoders store the
  vocabulary in a **trie** (Module 3) so the longest matching token is found by a
  single prefix walk.
- **Why subwords:** rare words split into known pieces (`unhappiness` →
  `un` + `happ` + `iness`), so the model never hits a true "unknown word", and the
  vocab stays small (~50k) instead of one entry per word.
- **Encoding cost:** greedy longest-match over a trie is about **O(length of text)**.
- **Variants:** **WordPiece** (BERT) and **Unigram / SentencePiece** (T5, Llama)
  are the same idea with different merge/scoring rules.

### Beam Search (decoding)

![Beam search keeps the top-k highest-probability partial sequences at each step, pruning the rest.](images/138_beam_search.png)

At each step, an LLM has a probability over the next token. **Beam search** keeps
the **top-k partial sequences** (beam width k), expands each, and again keeps the
best k → better than greedy (k=1) but costs k×.

**Greedy vs beam — a tiny dry run (beam width k=2).** Greedy grabs the single best
token each step and can get stuck; beam keeps k partial sequences and can recover.

```text
Greedy (k=1): pick argmax each step
  step1: "The"(0.6)   step2: "cat"(0.5)   -> locked in early, no undo

Beam (k=2): keep the 2 best *sequences* by total log-prob
  step1 keep:  "The"(0.6)      "A"(0.4)
  step2 expand both, score full sequences, keep best 2:
        "The cat"(0.30)  "A dog"(0.24)  "The dog"(0.18) ...
        -> keep "The cat"(0.30) and "A dog"(0.24)
  A high-prob step-2 token after a weaker step-1 word can still win overall.
=> beam explores k paths; greedy commits to one. Beam cost ~ k x greedy.
```

- **Data structure for beam search:** at each step you expand k beams × V vocab
  candidates and keep the **top-k** by score — a textbook **heap / top-k selection**
  (Module 6). Scores are summed in **log-space** to avoid tiny-float underflow.
- **Alternatives:** **top-k sampling**, **nucleus / top-p sampling** (sample from
  the smallest set of tokens whose probability ≥ p) — used for *creative* output;
  beam search for *deterministic* tasks (translation).
- **Pitfall:** beam search favours **short, safe, repetitive** outputs (higher
  total probability) → great for translation, dull for open-ended chat, where
  sampling wins.
- **KV-cache:** during generation, cache each layer's key/value tensors so each
  new token is **O(1)** in attention over the past instead of recomputing — a
  classic **memoization** (Module 14) applied to transformers.

**KV-cache — the data structure that makes generation fast.** During generation,
cache each layer's **key/value tensors** so each new token is **O(1)** in attention
over the past instead of recomputing — a classic **memoization** (Module 14)
applied to transformers.

```text
Without cache: to emit token t, recompute K,V for all t tokens -> O(t) work
               total over n tokens = O(1+2+...+n) = O(n^2)  (wasteful)
With cache:    append the new token's K,V to a growing per-layer buffer
               each step reuses all past K,V -> O(t) attention, O(1) recompute
=> the cache is a per-layer, per-head *append-only array* of (K,V) rows,
   one row per past token. Memory grows linearly with sequence length.
```

- **Shape/cost:** cache size ≈ `2 × layers × heads × seq_len × head_dim` — this is
  the memory that limits how long a context you can serve.
- **Serving optimisations:** **PagedAttention** (vLLM) stores the KV-cache in fixed
  **pages** (like OS virtual memory, Module 1) to avoid fragmentation; **MQA/GQA**
  share K/V across heads to shrink the cache.

### MCQs

1. BPE merges what each step? → the **most frequent adjacent pair** (hashmap).
2. Beam width k=1 is just? → **greedy decoding**.
3. KV-cache is an instance of? → **memoization**.
4. Beam search's top-k step uses which DS? → a **heap** (top-k selection).
5. KV-cache without caching costs? → **O(n²)** over a full generation.
6. The KV-cache is stored as? → a per-layer **append-only array** of K/V rows.
7. Why sum log-probs in beam search? → avoid **float underflow** on tiny products.
8. Beam search's typical failure mode? → **short/repetitive** outputs.

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
- Q: Cosine vs dot on unit vectors? **A: identical ranking.**
- Q: PQ stores? **A: centroid IDs (bytes), not floats.**
- Q: Billion-scale FAISS index? **A: IVF + PQ.**
- Q: Cheapest RAG quality win? **A: chunk overlap.**
- Q: KV-cache without caching costs? **A: O(n²) per generation.**
- Q: Fast BPE encoder uses which DS? **A: a trie (longest-match).**

## Module 21 — Pattern Recognition

- "Find similar items at scale" → **embeddings + ANN (HNSW)**.
- "Ground an LLM in my docs" → **RAG (vector retrieval)**.
- "Pick best next tokens / sequences" → **beam search / sampling**.
- "Seen-before / approximate counts at scale" → **Bloom / HLL / Count-Min**.
- "Top-N recommendations" → **ANN + heap**.
- "Vectors don't fit in RAM" → **quantization (PQ / int8)**.
- "Split a long document for RAG" → **overlapping / recursive chunking**.
- "Speed up token generation" → **KV-cache (memoization)**.

## Module 21 — Interview Questions (AI-eng)

1. *Design semantic search over 1B documents.* → embeddings + HNSW/IVF-PQ + sharding.
2. *Build a RAG pipeline.* → chunk/embed/index/retrieve/re-rank/generate.
3. *Why does KD-tree fail for embeddings?* → curse of dimensionality → ANN.
4. *Greedy vs beam vs sampling decoding — trade-offs?*
5. *HNSW vs IVF vs PQ — when do you pick each?* → recall/latency vs memory/scale.
6. *How would you fit 1B embeddings in RAM?* → IVF + PQ / scalar quantization.
7. *How do you chunk documents for RAG?* → recursive/overlapping, token-based, cite offsets.
8. *Why is a KV-cache needed?* → avoids O(n²) recompute during generation.

## Module 21 — GATE / SEBI / RBI / ISRO Perspective

- Not in classic syllabi, but **vector search / ANN / RAG** are increasingly
  relevant to applied-AI and data-engineering roles (and modern IT exams' GK
  sections). The underlying DSA (graphs, heaps, hashing, memoization) is all from
  M1–M18.

---

*End of Module 21. Next: Module 22 — System Design Connections (why Redis uses
skip lists, DBs use B+ trees, Linux uses RB-trees, Git uses DAGs) — with visuals.*
