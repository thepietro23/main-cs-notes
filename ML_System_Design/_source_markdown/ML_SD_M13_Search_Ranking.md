---
title: "Module 13 — Search & Ranking Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 13 — Search & Ranking Systems

> **Why this module matters.**
> Search and ranking are the beating heart of almost every large ML product:
> web search, e-commerce product search, app stores, feeds, ads, and even the
> "retrieval" step of a RAG system all boil down to the same question — *given a
> query and millions of candidates, which few should we show, and in what
> order?* Ranking is where classic information retrieval (IR) meets modern deep
> learning, and where the systems constraints (latency, scale, freshness) bite
> hardest. Interviewers love it because a strong answer forces you to connect
> **an IR baseline**, **a learning-to-rank model**, **embeddings + ANN**, and a
> **multi-stage serving funnel** — all under a tight latency budget. We build the
> whole picture from first principles, starting with a 1960s data structure and
> ending with a full product-search design.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
explain an inverted index and why it makes search fast; write the TF-IDF and
BM25 scoring formulas and say *why* BM25 beats plain TF-IDF; distinguish
pointwise, pairwise (RankNet), and listwise (LambdaRank / LambdaMART)
learning-to-rank and say what each optimizes; explain dense / semantic retrieval
with a dual-encoder plus approximate nearest neighbour (ANN) search, and how it
relates to two-tower models (M12) and vector DBs (M16); draw the multi-stage
funnel (retrieval → pre-rank → rank → re-rank) with a latency budget per stage;
compute NDCG by hand; and run a full 7-step design for web / product search
ranking.

> **How to read this module.** For every idea we go **problem → simplest attempt
> → why it breaks → the fix**. We explain the *why* before the *how* and tie
> each concept to how it shows up in a real Google / Amazon / Meta interview.

---

## 13.1 Information Retrieval Foundations

### Motivation (the problem that existed)

You have a billion documents (web pages, product listings). A user types "red
running shoes". You must return the most relevant few **in tens of
milliseconds**. The naive approach — scan every document, check if it contains
the words — is hopeless: a billion string scans per query. We need a data
structure that turns "which documents contain this word?" into an instant
lookup. That structure is the **inverted index**, and it is the foundation of
every search engine ever built.

### The inverted index

A normal ("forward") index maps *document → words in it*. An **inverted index**
flips this: it maps *word → list of documents that contain it*. That list is
called a **posting list**. To answer "red running shoes", you fetch the posting
lists for `red`, `running`, `shoes` and **intersect** them — a few list merges
instead of a billion scans.

![Left: three documents. Right: the inverted index maps each term to the list of documents that contain it. A query looks up terms and intersects their posting lists in milliseconds.](images/m13_01_inverted_index.png)

As the diagram shows, `cat -> D1, D2` means the word "cat" appears in documents
1 and 2. Posting lists are usually sorted by document id and heavily compressed,
and they often store extra data (term positions, term counts) so we can rank
and support phrase queries. The index is built **offline** (batch) and served
from memory or SSD; queries only *read* it. This is why keyword search is cheap
and scalable — the expensive work happened at index build time.

### TF-IDF — the first scoring idea

Finding documents that contain the words is not enough; we must **rank** them.
The oldest good idea is **TF-IDF** (Term Frequency × Inverse Document
Frequency). The intuition, from first principles:

- **Term Frequency (TF):** a document that uses the query word many times is
  probably more about it. TF rewards repetition.
- **Inverse Document Frequency (IDF):** a word that appears in *almost every*
  document (like "the") carries little information; a rare word (like "chondroma")
  is highly discriminative. IDF *down-weights* common words and *up-weights*
  rare ones.

For a term $t$ in document $d$ within a collection of $N$ documents:

$$\text{TF-IDF}(t,d) = \text{tf}(t,d) \times \log\frac{N}{\text{df}(t)}$$

where $\text{tf}(t,d)$ is the count of $t$ in $d$, and $\text{df}(t)$ is the
number of documents containing $t$. A document's score for a query is the sum of
TF-IDF over the query terms. Simple, fast, and for decades it was the default.

### BM25 — why it beats TF-IDF

TF-IDF has two real flaws:

1. **TF grows linearly forever.** A document that repeats "shoes" 100 times
   scores 100× — but a page is not 100× more relevant just because it spams a
   word. Relevance should **saturate**.
2. **No length normalization.** A very long document naturally contains more
   term occurrences, so it unfairly out-scores a short, on-point document.

**BM25** (Best Match 25, the Okapi weighting scheme) fixes both. Its score for a
document $d$ and query $Q$ is:

$$\text{BM25}(d,Q)=\sum_{t\in Q}\text{IDF}(t)\cdot\frac{\text{tf}(t,d)\,(k_1+1)}{\text{tf}(t,d)+k_1\left(1-b+b\,\frac{|d|}{\text{avgdl}}\right)}$$

The two tuning knobs are the whole point:

- **$k_1$** (typically 1.2–2.0) controls **saturation**: as term frequency
  rises, the extra reward shrinks. Ten mentions is barely more than five.
- **$b$** (typically 0.75) controls **length normalization**: it penalizes
  documents longer than the average length `avgdl`, so a short focused document
  competes fairly with a long one.

![TF-IDF grows linearly with term frequency and has no length normalization, so it over-rewards repetition and long documents. BM25 saturates term frequency (via k1) and normalizes by document length (via b), so it ranks better.](images/m13_02_tfidf_vs_bm25.png)

As the figure summarizes: **BM25 = TF-IDF + saturation + length normalization.**
It is still the strongest *keyword* baseline today, ships in Elasticsearch /
Lucene by default, and is the number you must beat before adding any ML.

> **Senior signal:** In a search design, *always* name BM25 as your retrieval
> baseline. Reaching straight for embeddings without a keyword baseline is a
> junior move — BM25 is cheap, interpretable, and surprisingly hard to beat on
> exact-match ("head") queries.

---

## 13.2 Learning to Rank (LTR)

### Motivation

BM25 uses one text signal. Real ranking wants to combine **hundreds** of
signals — text match, click history, price, freshness, seller rating, user
personalization. Hand-tuning weights for all of these is hopeless (recall the
whack-a-mole problem from Module 1). **Learning to Rank** trains a model to
combine features into a relevance score, using logged relevance judgments or
clicks as labels. There are three families, differing in *what unit they look at
and what they optimize.*

![Three learning-to-rank families. Pointwise scores each document alone as a regression problem. Pairwise learns the correct order of document pairs (RankNet). Listwise optimizes the whole ranked list at once (LambdaMART), aligned with NDCG. Left to right is weaker to stronger for ranking.](images/m13_03_ltr_families.png)

### Pointwise

Treat each (query, document) pair independently and predict an absolute
relevance score or label (e.g. regression to a 0–4 grade, or binary
click/no-click). Then sort documents by predicted score. **What it optimizes:** a
per-document loss (squared error, log-loss). It is the simplest and most like
ordinary supervised learning, and it works when you have graded labels. Its
weakness: it does not care about *relative order* — getting document A's absolute
score slightly wrong may still flip it above B, which is what actually hurts.

### Pairwise (RankNet)

Look at **pairs** of documents for the same query and learn which one should
rank higher. **RankNet** (Burges et al., Microsoft) feeds both documents through
the same neural net to get scores $s_i, s_j$, converts the score difference into
a probability that $i$ beats $j$ via a sigmoid, and minimizes cross-entropy
against the true preference. **What it optimizes:** the number of correctly
ordered pairs (closely related to minimizing *inversions*). This matches ranking
much better than pointwise because ranking *is* about relative order. Its
weakness: it treats every pair equally, but a mistake at position 1 matters far
more than a mistake at position 50.

### Listwise (LambdaRank, LambdaMART)

Look at the **entire list** for a query and optimize a list-level ranking metric
directly. The problem: metrics like NDCG are **flat or discontinuous** (swapping
two docs changes NDCG in steps), so you cannot take a gradient of them.
**LambdaRank**'s clever trick is to skip the loss and define the **gradient**
directly: it takes the RankNet pairwise gradient and *scales* it by the change
in NDCG (`|ΔNDCG|`) you would get by swapping that pair. So pairs whose swap
would move NDCG a lot get a big push; pairs near the bottom get almost none.
**LambdaMART** = LambdaRank gradients plus **gradient-boosted decision trees
(MART)**, and it is the workhorse that has won many ranking competitions.

**What each optimizes, in one line:**

| Family | Unit | Optimizes | Example |
|--------|------|-----------|---------|
| Pointwise | one doc | absolute relevance score | regression / classification |
| Pairwise | doc pair | correct order of pairs | RankNet |
| Listwise | whole list | a list metric (NDCG) | LambdaRank, LambdaMART |

### How NDCG ties in

The reason listwise methods win is that the business cares about **top-of-list
quality**, and **NDCG** (Normalized Discounted Cumulative Gain) is the metric
that captures it: it rewards putting highly relevant documents near the top and
discounts relevance by position. LambdaMART bakes `ΔNDCG` straight into its
gradient, so it is *directly* chasing the metric you report. We compute NDCG by
hand in Section 13.6.

> **Senior signal:** Say "I'd start with LambdaMART / gradient-boosted trees for
> tabular ranking features, because they train fast, handle mixed feature types,
> and directly optimize NDCG." Only reach for a deep ranker when you have huge
> data and rich text/embedding features.

---

## 13.3 Embedding-Based (Semantic / Neural) Retrieval

### Motivation — the vocabulary-mismatch problem

Keyword search fails when the words differ but the *meaning* matches. A user
searches "how to fix a flat tyre"; the best document says "repairing a punctured
wheel" and shares almost no words. BM25 scores it near zero. We need retrieval
based on **meaning**, not exact tokens. That is **dense / semantic retrieval**:
represent both query and documents as vectors (embeddings) in a shared space
where *closeness = semantic similarity*.

### Dual-encoder (two-tower) retrieval

The standard architecture is a **dual-encoder**, also called **two-tower**
(covered as a modeling pattern in Module 12): one neural encoder turns the query
into a vector, another encoder turns each document into a vector, and relevance
is the dot product (or cosine similarity) of the two vectors. Crucially, the
**document vectors are precomputed offline and indexed**; at query time you only
encode the query and search the index.

![Dense retrieval with a dual-encoder. A query encoder maps the query to a vector; a doc encoder maps every document to a vector, precomputed and indexed. An ANN index finds the nearest doc vectors to the query vector and returns the top-K. Cross-links to two-tower (M12) and vector DBs (M16).](images/m13_04_dense_retrieval.png)

Because the towers are separate, all the heavy document encoding happens in
batch, and the online cost is: one query encode + one nearest-neighbour search.
This is exactly the two-tower recommendation retrieval pattern from Module 12,
reused for search.

### Approximate Nearest Neighbour (ANN)

Finding the closest document vectors to the query vector by brute force means
computing a billion dot products per query — far too slow. **Approximate Nearest
Neighbour (ANN)** search trades a tiny bit of accuracy for a massive speed-up,
returning *almost* the true nearest neighbours in sub-millisecond time. Common
methods:

- **HNSW** (Hierarchical Navigable Small World): a layered graph you greedily
  walk toward the query; excellent recall/latency, memory-heavy.
- **IVF** (Inverted File): cluster vectors, search only the nearest few clusters.
- **PQ** (Product Quantization): compress vectors so more fit in RAM.

These indexes live inside **vector databases** (FAISS, ScaNN, Milvus, Pinecone),
the subject of **Module 16**. The key trade-off is **recall vs latency vs
memory** — you tune how many clusters/graph-neighbours to visit.

### Dense vs sparse — use both

Dense retrieval catches meaning but can miss exact matches (part numbers, rare
names, "iPhone 15 Pro Max 256GB"). Keyword/BM25 nails exact matches but misses
synonyms. The strong production answer is **hybrid retrieval**: run BM25 *and*
dense retrieval, then merge the candidate lists (e.g. reciprocal rank fusion)
before ranking. This is also the modern RAG retrieval recipe.

> **Senior signal:** Propose hybrid (BM25 + dense) retrieval and explain *why*:
> dense for semantic "torso/tail" queries, sparse for exact-match "head"
> queries. Then note the cross-links — two-tower (M12) for the encoders, vector
> DB / ANN (M16) for the index.

---

## 13.4 Multi-Stage Ranking (the Funnel)

### Motivation

You cannot run your expensive, feature-rich ranking model on a billion
documents — that would blow the latency budget by orders of magnitude. But you
also cannot run a cheap model on everything and still be accurate. The universal
solution is a **funnel**: several stages, each keeping fewer candidates but
spending more compute per candidate. Cheap-and-broad first, expensive-and-precise
last.

![The multi-stage ranking funnel. Retrieval narrows millions to about 1000 using cheap methods (BM25 / ANN). Pre-rank narrows to about 100 with a light model. Rank narrows to about 10 with a heavy model and many features. Re-rank applies business rules, diversity, and freshness to set the final order. Each stage keeps fewer items but spends more compute per item, so the total stays inside the latency budget.](images/m13_05_multistage_funnel.png)

### The four stages and their latency budget

1. **Retrieval (candidate generation).** Input: millions. Output: ~1000. Use the
   *cheapest* recall methods — BM25 over the inverted index, plus ANN over dense
   vectors (often several sources unioned). Optimizes **recall** (don't lose good
   docs). Budget: a few ms.
2. **Pre-rank (first-pass ranking).** Input: ~1000. Output: ~100. A **light**
   model (e.g. a small GBDT or the two-tower dot product) with a handful of cheap
   features prunes the list. Budget: a few ms.
3. **Rank (full ranking).** Input: ~100. Output: ~10. The **heavy** model —
   LambdaMART with hundreds of features, or a deep cross-attention ranker — does
   the precise scoring. This is where most model quality lives. Budget: the bulk
   of the tens of ms.
4. **Re-rank (post-processing).** Input: top ~10. Reorder for **business rules,
   diversity, freshness, de-duplication, and policy** (e.g. don't show 10 results
   from the same seller). Budget: ~1 ms.

**Why the funnel works:** total cost ≈ (millions × tiny) + (1000 × small) +
(100 × large) + (10 × huge). Because each stage shrinks the count roughly 10×,
you can afford a 100× more expensive model at each step and still meet, say, a
100 ms end-to-end p99 budget. This is the single most important structural idea
in ranking systems, and it mirrors the "hybrid batch + online" pattern from
Module 1.

> **Interview move:** When asked "how do you serve ranking at scale?", draw this
> funnel first. Then attach a model and a latency figure to each stage. It
> instantly signals you understand the systems constraint, not just the model.

---

## 13.5 Query Understanding, Personalization & Freshness

### Motivation

A ranking model that sees only the raw query text is leaving huge signal on the
table. The same three words mean different things to different users at
different times. Great search fuses three extra signal sources before and during
ranking.

![Beyond the raw query, three signal sources feed the ranking model. Query understanding does spell correction, intent detection, and synonym expansion. Personalization adds user history and location. Freshness adds recency and trending. Good search fuses query meaning, who is asking, and how fresh results must be.](images/m13_06_signals.png)

### Query understanding

Before retrieval, clean and enrich the query:

- **Spell correction:** "runing shoes" → "running shoes".
- **Tokenization / normalization:** lowercasing, stemming, handling accents.
- **Intent classification:** is "apple" a fruit, a company, or a location? Is
  the query navigational (go to a site), informational, or transactional (buy)?
- **Query expansion / synonyms:** add "sneakers" when the user typed "trainers".
- **Entity recognition:** detect "iphone 15" as a product entity.

Better query understanding improves retrieval recall *and* gives the ranker
cleaner features.

### Personalization

Two users typing the same query may want different results. Signals: past
searches and clicks, purchase history, location (a "coffee" search wants nearby
shops), language, device. Personalization is usually injected as **user features**
(and user embeddings) into the ranking model — never by over-fitting so hard
that a user gets trapped in a filter bubble. Beware the **feedback loop** from
Module 1: personalization trained on clicks reinforces what it already shows.

### Freshness

For news, social, and trending products, **recency is relevance**. A perfect
match from three years ago may be useless. Freshness enters as features
(document age, recent click velocity, "trending" scores) and as re-ranking rules
that boost new content. There is a tension: freshness vs authority/quality —
tuned per vertical (news leans fresh; reference leans authoritative).

---

## 13.6 Evaluation — NDCG and Online Metrics

### Offline: why not just accuracy?

Ranking quality is about **order**, not classification. The dominant offline
metric is **NDCG@k**. Build it up from three ideas:

1. **Gain:** each result has a relevance grade (e.g. 0=irrelevant … 3=perfect).
   The **gain** is the relevance (or $2^{rel}-1$ for the exponential variant).
2. **Discounted Cumulative Gain (DCG):** rewards putting relevant items high by
   dividing each gain by a positional discount:
   $$\text{DCG@}k=\sum_{i=1}^{k}\frac{\text{gain}_i}{\log_2(i+1)}$$
3. **Normalize:** divide DCG by the **ideal DCG (IDCG)** — the DCG of the best
   possible ordering — so the metric lands in $[0,1]$ and is comparable across
   queries: $\text{NDCG@}k = \text{DCG@}k / \text{IDCG@}k$.

### Worked example

Suppose our ranking returns four documents with relevance grades
$[3, 2, 3, 0]$ (using linear gain = relevance):

![NDCG worked example. For a ranking with relevance grades 3, 2, 3, 0, each gain is divided by log2(1+rank): 3.00, 1.26, 1.50, 0.00, summing to DCG = 5.76. NDCG is DCG divided by the ideal DCG, landing in [0, 1].](images/m13_07_ndcg.png)

As the figure computes:

- Rank 1: $3 / \log_2(2) = 3/1.00 = 3.00$
- Rank 2: $2 / \log_2(3) = 2/1.58 = 1.26$
- Rank 3: $3 / \log_2(4) = 3/2.00 = 1.50$
- Rank 4: $0 / \log_2(5) = 0/2.32 = 0.00$
- **DCG = 5.76.**

The **ideal** ordering sorts by relevance: $[3, 3, 2, 0]$, giving
$3.00 + 3/1.58 + 2/2.00 + 0 = 3.00 + 1.89 + 1.00 = 5.89$ = **IDCG**. So
$\text{NDCG} = 5.76 / 5.89 = 0.98$ — very good; the only flaw is the second-best
doc sits at rank 3 instead of 2.

Other offline metrics you should name: **MAP** (Mean Average Precision, for
binary relevance), **MRR** (Mean Reciprocal Rank, for "first correct answer" —
great for question answering), and **Precision@k / Recall@k**.

### Online metrics — the real judge

Offline NDCG uses *labels or logged clicks*, which are biased (position bias:
users click top results just because they are on top). The true test is an
**online A/B test** (Module 7 / 10) measuring business outcomes:

- **Click-through rate (CTR)** and **click position**.
- **Conversion / purchase rate** (product search), **watch time** (video).
- **Query reformulation / abandonment rate** (low = users found it).
- **Session success and long-term revenue / retention.**

Beware the **offline–online gap**: a model can lift NDCG offline yet lose the A/B
test (e.g. because offline labels came from the *old* ranker). Always confirm
online.

---

## 13.7 Worked Mini-Design — Web / Product Search Ranking (7-step framework)

We now run the Module 2 seven-step framework end to end on **"design product
search ranking for an e-commerce site."**

![End-to-end product search ranking design. A user query plus context goes to retrieval (BM25 + ANN), then to a rank stage (LambdaMART or neural), then to a re-rank stage for freshness and diversity, producing the results page. Logs of clicks and purchases feed a retrain loop back to the model. Offline evaluation uses NDCG; online uses A/B tests of click-through and conversion.](images/m13_08_design_pipeline.png)

**Step 1 — Clarify requirements & framing.** Business goal: increase purchases /
revenue, not just clicks. Scale: 100M products, 10k QPS peak, p99 latency budget
~150 ms. Freshness: new products and price changes should surface within minutes.
Both text and structured signals (price, rating, stock) matter.

**Step 2 — Frame as ML problem.** Ranking task: given (query, user, candidate
products), predict a relevance/purchase score to order the results. Labels: from
logged clicks and purchases (with position-bias correction), plus periodic human
relevance judgments.

**Step 3 — Data.** Query logs, click/add-to-cart/purchase events, product
catalog (title, description, category, price, ratings, stock), and user history.
Watch for leakage (don't use post-click signals as features) and feedback loops.

**Step 4 — Features & retrieval.** Build an **inverted index** (BM25) and a
**dense two-tower** index (ANN) over product embeddings — **hybrid retrieval**.
Query understanding (spell-fix, synonyms, entity detection) runs first. Features
for ranking: BM25 score, dense similarity, price, rating, popularity, freshness,
personalization (user–category affinity), query–product category match.

**Step 5 — Model & multi-stage serving.** Use the **funnel**: retrieval (BM25 +
ANN) → pre-rank (light GBDT / two-tower dot product) → **rank (LambdaMART**,
directly optimizing NDCG, or a neural ranker if data is huge) → **re-rank** for
diversity (limit results per seller), freshness boosts, and business rules
(sponsored placements, out-of-stock demotion).

**Step 6 — Evaluation.** Offline: **NDCG@10** and MAP on held-out judged
queries. Online: **A/B test** conversion rate, revenue per search, and query
abandonment — the offline metric only gates which models reach the A/B test.

**Step 7 — Deploy, monitor, iterate.** Serve behind a low-latency service
(cross-link M8/M11); precompute product embeddings in **batch**, re-rank
**online**. Monitor CTR/conversion, latency tails, and **drift** (M10) as the
catalog and trends change. Logs feed the **retrain loop** — closing the flywheel
from Module 1.

---

## Module 13 — Interview Mapping (what companies probe)

| Company | How Module 13 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google** | "Design web search ranking" | Jumps to a neural ranker | BM25 baseline → LTR → hybrid dense → multi-stage funnel with latency budget |
| **Amazon** | "Design product search" (Customer Obsession) | Optimizes CTR only | Optimizes purchase/revenue, handles exact-match part numbers, diversity by seller |
| **Meta / LinkedIn** | Feed / people / job search ranking | Ignores personalization | Adds user features, freshness, and guards against feedback loops |
| **OpenAI / Anthropic** | Retrieval for RAG | Uses only dense retrieval | Hybrid BM25 + dense, reranker, cites ANN recall/latency trade-off |

**The single most common opening:** *"How would you design search ranking for
X?"* Your first 90 seconds: (1) clarify the business metric and latency budget,
(2) name BM25 as the retrieval baseline, (3) draw the multi-stage funnel. That
structure alone separates you from most candidates.

---

## Module 13 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **GATE CS / DA:** information retrieval basics appear — inverted index,
  TF-IDF, precision/recall, and sometimes cosine similarity. Know the TF-IDF
  formula and how an inverted index answers a query. (Sections 13.1, 13.6.)
- **SEBI IT / RBI IT:** occasional definitional IR questions (what is an
  inverted index, TF-IDF). Learning-to-rank and system-design depth are
  **interview-only**.
- **ISRO / DRDO:** rare; at most basic IR definitions.

> **Flag:** the *scoring formulas* (TF-IDF, BM25, NDCG/DCG) and the *inverted
> index* carry the most exam value; the funnel, LTR families, and dense
> retrieval are primarily interview / role material.

---

## Module 13 — Common Mistakes & Misconceptions

1. **"Just use embeddings for everything."** Dense retrieval misses exact matches
   (part numbers, rare names). Hybrid BM25 + dense is stronger. (Section 13.3.)
2. **"Skip the BM25 baseline."** BM25 is cheap, interpretable, and hard to beat
   on head queries — always the baseline. (Section 13.1.)
3. **"Run the big model on all candidates."** Impossible under latency; you need
   the multi-stage funnel. (Section 13.4.)
4. **"Optimize accuracy / CTR."** Ranking is about *order* (NDCG) and the
   *business* metric (conversion, revenue), not classification accuracy or raw
   clicks. (Sections 13.2, 13.6.)
5. **"Offline NDCG win = ship it."** The offline–online gap is real; confirm with
   an A/B test. Clicks are position-biased. (Section 13.6.)
6. **"Pointwise is enough."** Pairwise/listwise (RankNet, LambdaMART) match the
   ranking objective far better because they model relative order. (Section 13.2.)
7. **"Personalization is free."** It can create filter bubbles and feedback loops
   that amplify what the model already shows. (Section 13.5.)

---

## Module 13 — MCQs (with answers & explanations)

**Q1.** An inverted index maps:
a) documents → the words they contain
b) words → the list of documents that contain them
c) queries → users
d) documents → their length

<details><summary>Answer</summary>**b.** A term maps to its posting list of
documents. This turns "which docs contain this word?" into an instant lookup,
which is why keyword search is fast.</details>

**Q2.** Why does BM25 usually beat plain TF-IDF?
a) It uses a neural network
b) It saturates term frequency and normalizes by document length
c) It ignores rare words
d) It needs no index

<details><summary>Answer</summary>**b.** BM25 adds a saturation term (via $k_1$)
so repetition has diminishing returns, and length normalization (via $b$) so
long documents don't unfairly win. TF-IDF grows linearly and ignores length.</details>

**Q3.** Which learning-to-rank method directly ties its gradient to the change in
NDCG from swapping two documents?
a) Pointwise regression  b) RankNet  c) LambdaRank / LambdaMART  d) BM25

<details><summary>Answer</summary>**c.** LambdaRank scales the pairwise gradient
by `|ΔNDCG|`; LambdaMART combines those gradients with boosted trees, so it
chases NDCG directly.</details>

**Q4.** In a dual-encoder (two-tower) retrieval system, at query time you:
a) re-encode all documents
b) encode only the query and search an ANN index of precomputed doc vectors
c) run BM25 only
d) train the model

<details><summary>Answer</summary>**b.** Document vectors are precomputed and
indexed offline; online you encode the query once and do an approximate
nearest-neighbour search. This is the two-tower pattern from Module 12.</details>

**Q5.** In the multi-stage funnel, which stage spends the *most compute per
candidate*?
a) Retrieval  b) Pre-rank  c) Rank  d) All equal

<details><summary>Answer</summary>**c.** Rank sees the fewest candidates (~100 →
~10) so it can afford the heaviest model with the most features. Retrieval is
cheap-and-broad.</details>

**Q6.** A ranking returns relevance grades [3, 2, 3, 0]. Using linear gain and
$\log_2(1+\text{rank})$ discount, the DCG is:
a) 8.0  b) 5.76  c) 5.89  d) 3.00

<details><summary>Answer</summary>**b.** $3/1.00 + 2/1.58 + 3/2.00 + 0 = 3.00 +
1.26 + 1.50 + 0 = 5.76$. (Dividing by IDCG = 5.89 gives NDCG ≈ 0.98.)</details>

**Q7.** Approximate Nearest Neighbour (ANN) search trades a small amount of
______ for a large gain in ______.
a) latency; accuracy  b) accuracy (recall); speed  c) memory; correctness
d) cost; documents

<details><summary>Answer</summary>**b.** ANN returns *almost* the true nearest
neighbours much faster than brute force. You tune recall vs latency vs memory
(HNSW, IVF, PQ) — the domain of vector DBs in Module 16.</details>

**Q8.** Which is the strongest reason to use hybrid (BM25 + dense) retrieval?
a) It is cheaper than either alone
b) Dense catches semantic matches while BM25 catches exact matches
c) It removes the need for ranking
d) It avoids building an index

<details><summary>Answer</summary>**b.** They are complementary: dense for
synonyms/meaning (torso/tail queries), sparse/BM25 for exact tokens (head
queries like part numbers). Merge the lists before ranking.</details>

---

## Module 13 — Design Exercises (easy → hard)

- **Easy.** Given three short documents, build the inverted index by hand, then
  list which documents a query of two words would retrieve (intersection).
- **Easy.** For the ranking [2, 3, 0, 1], compute DCG@4 with linear gain, then
  the IDCG and NDCG.
- **Medium.** You have 100M products and a 120 ms p99 budget. Sketch the
  multi-stage funnel: name the method and candidate count at each stage, and
  give a rough latency for each.
- **Medium.** A query "cheap flights to blr" returns poor results. Which query
  understanding steps (spell, synonym, entity, intent) would you add, and what
  new ranking features do they enable?
- **Hard.** Design retrieval for a RAG chatbot over 10M internal documents.
  Choose sparse, dense, or hybrid; pick an ANN index; state the recall vs
  latency trade-off and how you'd add a reranker.
- **Hard.** Your new ranker lifts offline NDCG@10 by 4% but *loses* the online
  A/B test on conversion. Give three plausible causes and how you'd diagnose
  each (hint: position bias, offline label source, freshness, diversity).

---

## Module 13 — Concept Review (one page)

- **Inverted index** = term → posting list of docs; makes keyword search fast.
  Built offline, read at query time.
- **TF-IDF** = term frequency × inverse document frequency; rewards rare,
  repeated terms. **BM25** adds **saturation ($k_1$)** and **length
  normalization ($b$)**, so it ranks better and is the keyword baseline.
- **Learning to Rank:** **pointwise** (score each doc), **pairwise / RankNet**
  (order pairs), **listwise / LambdaRank & LambdaMART** (optimize the list;
  gradient scaled by `ΔNDCG`). Listwise best matches the ranking objective.
- **Dense retrieval** = dual-encoder / two-tower embeds query and docs into one
  space; **ANN** finds nearest doc vectors fast (recall vs latency vs memory).
  Cross-links: two-tower **M12**, vector DBs **M16**. Use **hybrid** BM25 + dense.
- **Multi-stage funnel:** retrieval (millions→1k, cheap) → pre-rank (1k→100,
  light) → rank (100→10, heavy) → re-rank (diversity/freshness/rules). Each stage
  fewer items, more compute each → fits the latency budget.
- **Query understanding, personalization, freshness** are the signal sources
  beyond raw text.
- **Evaluation:** offline **NDCG@k** (DCG / IDCG), MAP, MRR; **online A/B** on
  CTR / conversion / revenue. Mind the **offline–online gap** and position bias.

---

## Module 13 — Flash Cards (Q → A)

1. What does an inverted index map? → *Term → posting list of documents.*
2. BM25's two knobs? → *$k_1$ = term-frequency saturation; $b$ = document-length
   normalization.*
3. Why BM25 > TF-IDF? → *Saturation + length normalization stop over-rewarding
   repetition and long docs.*
4. Three LTR families? → *Pointwise, pairwise (RankNet), listwise (LambdaMART).*
5. What does LambdaMART optimize? → *NDCG — gradient scaled by `ΔNDCG`, with
   boosted trees.*
6. Dual-encoder online cost? → *Encode the query once + ANN search of precomputed
   doc vectors.*
7. ANN trades what for what? → *A little recall for a lot of speed.*
8. The four funnel stages? → *Retrieval → pre-rank → rank → re-rank.*
9. NDCG range and idea? → *[0,1]; DCG (position-discounted gain) ÷ ideal DCG.*
10. Why confirm online after offline NDCG? → *Offline–online gap; clicks are
    position-biased.*

---

## Module 13 — Pattern Recognition (how to spot it in an interview)

- Hear **"design search / ranking for X"** → clarify metric + latency → BM25
  baseline → multi-stage funnel.
- Hear **"results miss synonyms / meaning"** → propose dense retrieval
  (dual-encoder) + hybrid with BM25.
- Hear **"we can't run the big model on everything"** → draw the funnel; cheap
  retrieval first, heavy rank last.
- Hear **"which ranking model?"** → LambdaMART for tabular features (optimizes
  NDCG); deep ranker only with huge data.
- Hear **"how do you measure it?"** → NDCG@k offline, A/B on conversion online;
  warn about position bias.
- Hear **"serve at scale / low latency"** → precompute doc embeddings in batch,
  ANN retrieval, re-rank online (hybrid).
- Hear **"results feel stale / same items"** → freshness features + diversity in
  re-rank; watch feedback loops.

---

## Module 13 — Revision Notes / Mini Cheat Sheet

```
SEARCH = RETRIEVE candidates  ->  RANK them  ->  RE-RANK for rules/diversity

IR BASELINE:
  inverted index:  term -> posting list of docs   (fast lookup, built offline)
  TF-IDF = tf * log(N/df)                 (linear TF, no length norm)
  BM25  = TF-IDF + saturation(k1) + length-norm(b)   <- beats TF-IDF, the baseline

LEARNING TO RANK:
  pointwise  -> score each doc alone        (regression)
  pairwise   -> order of doc PAIRS          (RankNet)
  listwise   -> whole LIST, optimize NDCG   (LambdaRank / LambdaMART)  <- strongest

DENSE / SEMANTIC:
  dual-encoder (two-tower, M12): query vec . doc vec
  doc vectors precomputed + indexed;  ANN search (HNSW/IVF/PQ, M16)
  ANN = trade recall for speed;  HYBRID = BM25 + dense  (exact + meaning)

FUNNEL (latency budget!):  millions -> 1000 -> 100 -> 10
  retrieval(cheap) -> pre-rank(light) -> rank(heavy) -> re-rank(rules)

SIGNALS: query-understanding (spell/intent/synonym) | personalization | freshness

EVAL:  offline NDCG@k = DCG/IDCG , MAP, MRR ; online A/B: CTR / conversion
       beware offline-online gap + click position bias
```

---

> **Next module:** *Module 14 — Recommendation Systems at Scale.* We build on the
> retrieval + ranking funnel from this module and specialize it for
> recommendations: candidate generation, collaborative filtering, matrix
> factorization, deep recommenders, and the cold-start problem — the other half
> of the "retrieve-then-rank" world.
