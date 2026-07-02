---
title: "Module 15 — NLP Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 15 — NLP Systems

> **Why this module exists.**
> A huge share of the world's data is *text*: emails, reviews, chat messages,
> support tickets, search queries, legal documents. Natural Language Processing
> (NLP) is how we turn that messy human language into something a machine can
> reason about. Almost every product you use runs NLP somewhere — spam filters,
> autocomplete, search, translation, sentiment dashboards. This module builds the
> **classic and BERT-era** NLP mental model from first principles: how text
> becomes numbers, how embeddings evolved, how the main tasks are framed, and how
> you *serve* an NLP model under a real latency budget.
>
> **Scope note.** Large Language Models (GPT-style, prompting, RAG, fine-tuning)
> get their own deep treatment in **Module 16**. Here we deliberately stay on the
> foundations — tokenization, embeddings, classic tasks, semantic search, and
> serving — because these ideas are what LLMs are *built on top of*, and they are
> what interviews and exams still test directly.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★      | ★★     | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
explain the full text pipeline (clean → tokenize → embed → model) and *why text
must become numbers*; compare word / subword-BPE / character tokenization and say
why subword won; tell the embeddings story (word2vec → GloVe → BERT → modern) and
crisply distinguish **static vs contextual** embeddings; frame the core tasks
(classification, sentiment, NER, QA, summarization, translation) as either
"predict a label/tag" or "generate a sequence"; design **semantic search** with
embeddings + cosine similarity; reason about **NLP serving latency** (tokenization
cost, sequence length, the n² attention wall); and sketch end-to-end designs for
spam/abuse detection, support-ticket routing, and autocomplete.

> **How to read this module.** As always we go **problem → simplest attempt →
> why it breaks → the fix**, in plain English, and we tie every idea to how it
> shows up in a real interview or exam.

---

## 15.1 The Text Pipeline — Why Text Must Become Numbers

### Motivation (the problem that existed)

A model — any model, from logistic regression to a transformer — does arithmetic
on numbers. It multiplies, adds, and compares floating-point values. But a user
hands you `"I love it"`. A computer cannot multiply the word *love*. So the very
first problem in every NLP system is: **how do we turn a string of characters
into an array of numbers without throwing away the meaning?**

That single question drives the whole pipeline. Every stage below exists to move
one step closer to "meaningful numbers", and every stage costs time and memory
that you will later have to defend in a serving-latency discussion.

### The pipeline, stage by stage

![The NLP pipeline: raw text is cleaned/normalized, split into tokens, mapped to embedding vectors, then fed to a model that produces the output.](images/m15_01_pipeline.png)

1. **Raw text.** The input as it arrives: `"I love it"`, possibly with emojis,
   HTML, mixed case, typos, and multiple languages.
2. **Clean / normalize.** Lowercase, strip HTML, fix encoding, maybe remove
   accents or expand contractions. *Be careful:* lowercasing "US" (the country)
   to "us" can destroy meaning — normalization is a design choice, not a reflex.
3. **Tokenize.** Split the text into small units (**tokens**) — words or pieces
   of words. `"I love it"` → `[i] [love] [it]`. Each token maps to an integer id
   from a fixed **vocabulary**.
4. **Embed.** Look up (or compute) a dense **vector** for each token id, e.g.
   `[0.2, -1.1, 0.7, ...]`. This is where meaning finally becomes numbers.
5. **Model + output.** Feed the vectors to a model that produces the answer —
   a label (`positive`), a tag per token, or generated text.

### First-principles: why not just use ASCII codes?

A naive idea: "the letter *a* is 97, so just feed character codes." This fails
because those numbers carry **no semantic relationship** — 97 and 98 (`a` and
`b`) are close numerically but unrelated in meaning, while "good" and "great" are
close in meaning but would be far apart as raw codes. The whole point of the
pipeline is to produce numbers where **distance ≈ difference in meaning**. That
is exactly what embeddings (Section 15.3) give us.

> **Senior signal:** every box in this pipeline is a latency and failure surface.
> Mentioning "and this is where training-serving skew sneaks in — the cleaning
> and tokenization must be *identical* offline and online" (see M05) marks you as
> someone who has shipped NLP, not just trained it.

---

## 15.2 Tokenization — Word, Subword (BPE), Character

### Motivation

Tokenization decides your **vocabulary** — the fixed list of tokens the model
knows. Get it wrong and you either have a giant, brittle vocabulary or hopelessly
long sequences. Three strategies compete.

![Three tokenization strategies: word-level (huge vocab, breaks on new words), subword/BPE (small vocab, handles rare and new words), and character-level (tiny vocab, very long sequences).](images/m15_02_tokenization.png)

### The three strategies

**1. Word-level.** One token per word: `playing` → `[playing]`.

- *Problem:* the vocabulary must contain *every* word form — `play`, `plays`,
  `played`, `playing` are four separate entries. Real languages have millions of
  word forms, so the vocabulary explodes. Worse, any word not seen in training is
  an **out-of-vocabulary (OOV)** token — the model literally has no vector for it,
  so it maps everything unknown to a single `<UNK>` and loses the meaning.

**2. Subword / Byte-Pair Encoding (BPE).** Split rare words into reusable pieces:
`playing` → `[play] [ing]`.

- BPE starts from characters and *greedily merges* the most frequent adjacent
  pairs until it reaches a target vocabulary size (say 30k–50k pieces). Common
  words stay whole (`the`, `play`); rare words break into known pieces
  (`tokenization` → `token` + `ization`). **WordPiece** (used by BERT) and
  **SentencePiece** are close cousins.
- *Why it won:* no OOV problem (any string can be built from pieces), a small
  fixed vocabulary, and reasonable sequence lengths. This is the **modern
  default**.

**3. Character-level.** One token per character: `playing` → `[p][l][a][y]...`.

- Tiny vocabulary (~100 symbols), literally never OOV — but sequences become
  very long (a 5-word sentence is ~30 tokens instead of 5), which makes the model
  slower and forces it to learn spelling from scratch.

### Why sequence length matters later

Hold onto one number: **tokens-per-input**. It appears again in Section 15.6
because model cost usually grows with sequence length (often ~n² for attention).
Character-level maximizes length; word-level minimizes it; subword sits in the
sweet spot. This is not an accident — it is the trade-off subword was designed to
win.

> **Exam pointer (GATE DA):** know that BPE is a *data-driven, frequency-based
> merging* algorithm and that it eliminates OOV by falling back to smaller pieces.

---

## 15.3 Embeddings — How Words Become Vectors

### Motivation

We can now turn text into token ids. But an id like `4173` is just a name — it
has no meaning. We want a **vector** where similar words sit close together, so
the model can generalize: if it learns something about "good", it should partly
transfer to "great". That vector is an **embedding**. The history of NLP is
largely the history of *better* embeddings.

![Embeddings evolution timeline: word2vec (2013, static) and GloVe (2014, static) give one fixed vector per word; BERT (2018) and modern encoders (2020+) give contextual vectors that depend on the whole sentence.](images/m15_03_embeddings_timeline.png)

### The story, left to right

- **word2vec (2013).** Learn a vector per word by predicting nearby words (the
  "you shall know a word by the company it keeps" idea). Famous result:
  `king − man + woman ≈ queen` — meaning shows up as *directions* in vector
  space. It is **static**: one vector per word, fixed forever.
- **GloVe (2014).** Same static idea, but learned from a global **co-occurrence
  matrix** (how often words appear together across the whole corpus) rather than
  local windows. Also one vector per word.
- **BERT (2018).** A transformer that reads the **whole sentence** and produces a
  vector for each word *in context*. This is **contextual**: the same word gets
  different vectors in different sentences. Trained by masking words and
  predicting them ("masked language modelling").
- **Modern (2020+).** Larger context encoders and sentence/embedding models
  (e.g. sentence-transformers, and the embedding endpoints of LLM providers).
  These power today's semantic search. Their generative cousins are Module 16.

### Static vs contextual — the single most-tested distinction

![The word "bank": a static model gives the SAME vector for "river bank" and "money bank"; a contextual model reads the sentence and produces different vectors (A vs B) for the two meanings.](images/m15_04_static_vs_contextual.png)

- **Static (word2vec, GloVe):** the word *bank* has **one** vector, no matter
  what. So "river bank" and "money bank" collapse to the same point — the model
  cannot tell the two meanings apart. Cheap (just a lookup table), fast, and often
  good enough for simple classification.
- **Contextual (BERT):** the model reads the surrounding words, so *bank* in
  "river bank" gets **vector A** and *bank* in "money bank" gets **vector B**.
  This resolves ambiguity (polysemy) but costs a full model forward pass, not a
  table lookup — which is exactly why contextual models are slower to serve.

> **Interview line that lands:** *"word2vec is a dictionary — one entry per word.
> BERT is a reader — it re-reads the sentence every time, so the same word can
> mean different things."* That one sentence shows you truly understand the leap.

---

## 15.4 Core NLP Tasks — How Each Is Framed

### Motivation

Interviewers rarely ask "what is NER" — they ask "how would you *frame* this as
an ML problem?" The skill is recognizing which of a few standard shapes a
business request maps to. There are two big families.

![Core NLP tasks: classification, sentiment, and NER map text to a label or per-token tag (understanding); QA, summarization, and translation produce a sequence of new text (generation).](images/m15_05_nlp_tasks.png)

### Family A — predict a label or tag ("understanding")

- **Text classification.** Whole input → one label from a fixed set.
  *Examples:* spam vs not-spam, topic = {sports, politics, tech}. Framed as
  supervised classification; metric is precision/recall/F1 (M07).
- **Sentiment analysis.** A special case of classification: text → {positive,
  negative, neutral}, or a 1–5 star score (then it is ordinal/regression).
- **Named Entity Recognition (NER).** Tag **each token**: label every word as
  Person / Organization / Location / Other. This is *sequence labelling* (one
  prediction per token, usually with a BIO tagging scheme). Powers "extract all
  company names from these filings".

### Family B — generate a sequence ("generation" / seq-to-seq)

- **Question Answering (QA).** Two flavours: *extractive* QA finds the answer as
  a **span** inside a given passage (predict start and end token — still an
  understanding task); *generative* QA writes a free-form answer (M16).
- **Summarization.** Long document → short summary. *Extractive* picks existing
  sentences; *abstractive* generates new text. A sequence-to-sequence task.
- **Machine translation.** Sequence in one language → sequence in another. The
  original poster-child for the encoder-decoder (seq-to-seq) architecture.

### First-principles: why the split matters for design

The family decides your **output layer, metric, and cost**. Family A ends in a
softmax over a small label set — cheap, easy to evaluate (F1/accuracy). Family B
generates tokens one at a time — expensive at serving time, and hard to evaluate
(you need metrics like BLEU/ROUGE, or human review). When an interviewer offers a
vague task, *first classify it into A or B*: it instantly tells you the model
shape, the metric, and the latency profile.

---

## 15.5 Search & Semantic Similarity

### Motivation

Keyword search matches *strings*: a query for "car" misses a document that only
says "automobile". Humans mean the same thing; the letters differ. **Semantic
search** fixes this by comparing *meaning* instead of *characters* — and meaning,
as we just learned, lives in embedding vectors.

![Semantic search: the query text goes through an encoder to a query vector; document vectors are precomputed; an ANN index finds the top-k nearest by cosine similarity and returns the best matches.](images/m15_06_semantic_search.png)

### The core idea: embed everything, compare by cosine

1. **Embed the documents once, offline.** Run every document through an encoder
   and store its vector. This is precomputed — you pay for it in batch, not at
   query time.
2. **Embed the query live.** When a query arrives, encode it to a vector.
3. **Compare by cosine similarity.** Two vectors that point in the same direction
   have cosine ≈ 1 (very similar); perpendicular ≈ 0 (unrelated). Cosine ignores
   length and cares only about *direction*, which is what we want for meaning.
4. **Return the top-k nearest.** The most similar document vectors are the best
   semantic matches.

### Why you need an ANN index (the scaling problem)

Comparing the query to *every* document (exact nearest neighbour) is O(N) per
query — fine for thousands of docs, hopeless for billions. So we use an
**Approximate Nearest Neighbour (ANN)** index (HNSW, IVF, ScaNN) that finds
*almost* the closest vectors in roughly logarithmic time, trading a tiny bit of
accuracy for a massive speed-up. This is the heart of a **vector database**.

> **Cross-links:** retrieval and ANN indexes are covered in depth in **Module 13**
> (retrieval / recommendation candidate generation), and this exact
> embed-and-retrieve pattern is the "R" in **RAG** in **Module 16**. Semantic
> search is the bridge between classic NLP and modern LLM systems.

---

## 15.6 Serving NLP Models & Latency

### Motivation

You can train a beautiful model and still fail the interview if you cannot serve
it inside a latency budget. NLP serving has costs that classic tabular models
don't — and the biggest one is hidden in a variable you already met: **sequence
length**.

![NLP serving latency breakdown: tokenization and embedding lookup are cheap; the model forward pass dominates and grows with sequence length. Fixes: cap length, cache, batch, distill/quantize.](images/m15_07_serving_latency.png)

### Where the milliseconds go

- **Tokenization cost.** Usually cheap, but *not free* — and it must run on the
  exact same code path as training to avoid **training-serving skew** (M05). At
  very high QPS, tokenization can become a measurable slice.
- **Embedding lookup.** For static embeddings, a fast table lookup. For
  contextual models it is fused into the forward pass.
- **Model forward pass — the dominant cost.** For transformer/BERT-style models,
  self-attention is roughly **O(n²)** in the number of tokens `n`. Double the
  sequence length and you roughly *quadruple* the compute. This is the single
  most important serving fact in this module.

### The levers you pull to hit a budget

- **Cap / truncate sequence length.** Most tickets, reviews, and queries are
  short; setting a max length (e.g. 128 or 256 tokens) bounds the worst case.
- **Cache.** Many queries repeat — cache embeddings for popular inputs, and cache
  document vectors permanently (they don't change).
- **Batch requests.** GPUs love parallelism; grouping requests raises throughput
  (at a small latency cost — a classic throughput-vs-latency trade).
- **Shrink the model.** **Distillation** (train a small model to mimic a big one,
  e.g. DistilBERT) and **quantization** (use 8-bit instead of 32-bit numbers)
  cut latency and memory. (Covered as serving optimizations in M08.)

> **Senior signal:** the crisp statement *"attention is O(n²), so my first lever
> is capping sequence length, then batching, then distillation"* connects the ML
> internals to a concrete serving plan. That linkage is exactly what staff-level
> interviews reward.

---

## 15.7 Case Studies (short 7-step sketches)

Below are three compact end-to-end sketches. Each follows the same rhythm:
frame → data → features/tokens → model → serve → guardrail → feedback.

### Case A — Spam / abuse detection

1. **Frame.** Binary text classification: message → {spam/abuse, ok}. (Family A.)
2. **Data.** Historical messages with labels from user reports + moderator
   decisions. Beware class imbalance (spam is rare).
3. **Tokens/features.** Subword tokens + light metadata (sender age, links,
   repetition).
4. **Model.** Start with a simple baseline (logistic regression on TF-IDF or
   averaged embeddings); upgrade to a fine-tuned BERT if it earns its cost.
5. **Serve.** Online, low latency (block before the message is shown). Short
   inputs → cheap.
6. **Guardrail.** Tune the threshold by **cost of being wrong** (M01): a false
   positive silences a real user, a false negative lets abuse through. Send
   borderline cases to human moderators.
7. **Feedback.** Adversaries adapt (spammers obfuscate), so this **drifts fast**
   — monitor and retrain frequently on fresh reports.

### Case B — Support ticket routing

![Support ticket routing as a 7-step loop: ticket text in → clean+tokenize → embed → classify team → confidence check → route or send to human → log+retrain, with a feedback arrow returning corrections to the model.](images/m15_08_case_study.png)

1. **Ticket text in.** A customer writes a free-form problem.
2. **Clean + tokenize.** Normalize and subword-tokenize.
3. **Embed.** Encode to a vector.
4. **Classify team.** Multi-class classification → {billing, tech, returns, ...}.
5. **Confidence check.** Look at the top class probability.
6. **Route or human.** High confidence → auto-route; low confidence → a human
   triages it (keep a human in the loop where the model is unsure).
7. **Log + retrain.** Human corrections become **fresh labels** — the dashed
   feedback arrow — which retrain the model and steadily shrink the "send to
   human" pile. This is the data flywheel (M01) in miniature.

### Case C — Autocomplete / next-word suggestion

1. **Frame.** Predict the next token(s) given the prefix typed so far — a
   generation task, but small and local.
2. **Data.** Anonymized past queries / typed text; heavy use of frequency.
3. **Tokens.** Subword or word-level over a **prefix**.
4. **Model.** Often a lightweight n-gram / small language model — because...
5. **Serve.** ...the latency budget is *brutal*: suggestions must appear within a
   few ms **per keystroke**. This is why autocomplete frequently runs **on-device**
   (M01) and stays small.
6. **Guardrail.** Filter offensive/unsafe completions; never suggest private data.
7. **Feedback.** Which suggestion the user accepts is a strong training signal —
   but beware the **feedback loop**: only suggesting popular completions makes
   them even more popular.

---

## Module 15 — Interview Mapping (what companies probe)

| Company | How Module 15 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | "Design a system to detect toxic comments / route messages" | Jumps to "fine-tune BERT" | Frames task family, starts with a cheap baseline, plans threshold by cost of error, monitors for drift |
| **Amazon** | "Classify / route millions of support tickets" | Talks model only | Ties to Customer Obsession, adds human-in-loop for low confidence, feedback loop for retraining |
| **OpenAI / Anthropic** | Tokenization, static vs contextual embeddings, why subword | Vague on tokenization | Explains BPE eliminates OOV, static vs contextual with the "bank" example, forward-links to LLMs (M16) |
| **Uber / Stripe** | "Semantic search over docs" or "fraud from text" | Keyword match / one big model | Embed + cosine + ANN index, caps sequence length, discusses p99 latency and O(n²) attention |

**Common opener:** *"How would you build an NLP system for X?"* Your first move:
(1) classify the task into label/tag vs generate; (2) name the pipeline
(clean → tokenize → embed → model); (3) propose a **simple baseline first**
(TF-IDF + logistic regression) before any transformer; (4) call out latency and
drift. That structure alone beats most candidates.

---

## Module 15 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** may ask *definitional* NLP items — what is tokenization,
  what is an embedding, what is sentiment analysis, bag-of-words vs word
  embeddings. Sections 15.1–15.3 cover these.
- **GATE CS / DA:** the DA paper can test tokenization (BPE), word embeddings
  (word2vec skip-gram/CBOW idea, GloVe co-occurrence), TF-IDF, and the
  static-vs-contextual distinction. Cosine similarity for text is fair game.
- **ISRO / DRDO:** occasional basic NLP definitions and TF-IDF / vector-space
  model questions.

> **Flag:** the *system design* parts (serving latency levers, ANN indexes,
> case-study architectures) are largely **interview-only**. The *concept* parts
> (tokenization, embeddings, tasks, cosine similarity) carry the **exam** value.

---

## Module 15 — Common Mistakes & Misconceptions

1. **"word2vec understands context."** No — word2vec/GloVe are **static**: one
   fixed vector per word. Context awareness starts with BERT. (Section 15.3.)
2. **"Word-level tokenization is fine."** It explodes the vocabulary and breaks on
   any unseen word (OOV). Subword/BPE is the modern default. (Section 15.2.)
3. **"Semantic search is just keyword matching."** Keyword matches characters;
   semantic search matches *meaning* via embeddings + cosine similarity.
4. **"Bigger transformer = better."** Often a TF-IDF + logistic-regression
   baseline is faster, cheaper, and good enough — and it tells you if ML even
   helps. Start simple.
5. **"Latency doesn't depend on the input."** Transformer cost grows ~O(n²) with
   sequence length; long inputs are expensive. Cap the length. (Section 15.6.)
6. **"Train the tokenizer one way, serve another."** That is training-serving
   skew — cleaning and tokenization must be *identical* on both paths. (M05.)
7. **"Sentiment is always positive/negative."** It can be neutral, multi-class, or
   a 1–5 score (ordinal) — frame it to match the business need.

---

## Module 15 — MCQs (with answers & explanations)

**Q1.** Which statement best distinguishes static from contextual embeddings?
a) Static embeddings are larger vectors
b) Contextual embeddings give the same word different vectors depending on the sentence
c) Static embeddings require a GPU
d) Contextual embeddings cannot be used for classification

<details><summary>Answer</summary>**b.** word2vec/GloVe (static) give one fixed
vector per word; BERT (contextual) re-reads the sentence, so "bank" in "river
bank" and "money bank" get different vectors.</details>

**Q2.** Why did subword/BPE tokenization largely replace word-level tokenization?
a) It is faster to type
b) It eliminates out-of-vocabulary words while keeping the vocabulary small
c) It removes the need for embeddings
d) It only works for English

<details><summary>Answer</summary>**b.** Any word can be built from known
sub-pieces, so there is no OOV problem, and the vocabulary stays small (~30–50k).</details>

**Q3.** In semantic search, why is cosine similarity used to compare vectors?
a) It measures the length of each vector
b) It measures direction (angle), so it captures meaning regardless of magnitude
c) It is the only metric a GPU supports
d) It requires no embeddings

<details><summary>Answer</summary>**b.** Cosine looks at the angle between
vectors; similar meaning → similar direction → cosine near 1, independent of
vector length.</details>

**Q4.** A transformer's self-attention cost grows roughly as:
a) O(1)  b) O(log n)  c) O(n) with sequence length  d) O(n²) with sequence length

<details><summary>Answer</summary>**d.** Attention compares every token with every
other token, so cost scales ~n². This is why capping sequence length is the first
serving lever.</details>

**Q5.** "Tag each token as Person / Organization / Location" is which task?
a) Text classification  b) Named Entity Recognition (NER)  c) Summarization  d) Translation

<details><summary>Answer</summary>**b.** NER is sequence labelling — one prediction
per token — not a single label for the whole text.</details>

**Q6.** Which is the strongest *first* move when asked to build a text classifier?
a) Fine-tune the largest transformer available
b) Build a simple baseline (e.g. TF-IDF + logistic regression) to establish a floor
c) Collect no data and start serving
d) Use character-level tokenization for speed

<details><summary>Answer</summary>**b.** A cheap baseline tells you whether ML
helps at all and gives a number to beat before you pay for a transformer.</details>

**Q7.** In the support-ticket routing design, what should happen on a *low
confidence* prediction?
a) Auto-route anyway  b) Drop the ticket  c) Send it to a human, whose correction
becomes new training data  d) Retrain immediately on that one ticket

<details><summary>Answer</summary>**c.** Keep a human in the loop where the model
is unsure; their corrections are fresh labels that feed the retraining flywheel.</details>

**Q8.** Autocomplete typically runs on-device with a small model mainly because:
a) Phones have more compute than servers
b) The per-keystroke latency budget is extremely tight and privacy matters
c) On-device models are always more accurate
d) It avoids the need for tokenization

<details><summary>Answer</summary>**b.** Suggestions must appear within a few ms
per keystroke, and keeping typed text on the device protects privacy — so the
model must be small and local.</details>

---

## Module 15 — Design Exercises (easy → hard)

- **Easy.** For each, name the task family (label/tag vs generate) and one metric:
  (1) detect spam; (2) extract all dates from contracts; (3) translate reviews;
  (4) score reviews 1–5 stars. *(1 classification/F1; 2 NER/F1; 3 translation/BLEU;
  4 ordinal/MAE.)*
- **Easy.** Given `"unbelievable"`, show how word / subword / character
  tokenization each split it, and say which produces OOV on an unseen word.
- **Medium.** Design semantic search over 50 million help-center articles. Specify:
  what you precompute, what runs per query, the similarity metric, and why you need
  an ANN index. State a p99 latency target.
- **Medium.** Your BERT-based ticket classifier meets accuracy but blows the
  latency budget at peak traffic. List three levers (with trade-offs) to bring
  p99 down without retraining from scratch.
- **Hard.** Design an abuse-detection system for a chat app. Cover baseline vs
  transformer, threshold by cost of error, human review, and how you detect and
  respond to adversarial drift over weeks.
- **Hard.** A team wants "smart autocomplete" in a legal editor. Decide on-device
  vs server, tokenization, model size, the per-keystroke latency budget, and one
  feedback-loop risk plus how you'd detect it.

---

## Module 15 — Concept Review (one page)

- **Pipeline:** raw text → clean/normalize → **tokenize** → **embed** → model →
  output. Text must become numbers where *distance ≈ difference in meaning*.
- **Tokenization:** word (huge vocab, OOV) · **subword/BPE** (small vocab, no OOV
  — the default) · character (tiny vocab, very long sequences).
- **Embeddings:** word2vec → GloVe (**static**, one vector per word) → BERT
  (**contextual**, vector depends on the sentence) → modern encoders. The "bank"
  example is the canonical static-vs-contextual illustration.
- **Tasks, two families:** predict a **label/tag** (classification, sentiment,
  NER, extractive QA) vs **generate a sequence** (summarization, translation,
  generative QA). The family fixes the output layer, metric, and cost.
- **Semantic search:** embed docs offline + query live, compare by **cosine**,
  retrieve top-k via an **ANN index** (vector DB). Links to M13 and M16 (RAG).
- **Serving:** attention is ~**O(n²)** in sequence length; levers are **cap
  length → cache → batch → distill/quantize**. Tokenization must match training
  (no skew).
- **Case studies:** spam (fast drift, threshold by cost), ticket routing
  (confidence → human → retrain), autocomplete (tiny model, on-device, per-key
  budget).

---

## Module 15 — Flash Cards (Q → A)

1. Why must text be tokenized + embedded? → *Models do math on numbers; embeddings
   put meaning into vector distance.*
2. Word vs subword vs char in one line? → *Word = big vocab + OOV; subword = small
   vocab, no OOV (default); char = tiny vocab, long sequences.*
3. What does BPE do? → *Frequency-based merging of characters into subword pieces;
   removes OOV.*
4. Static vs contextual embedding? → *Static = one fixed vector per word (word2vec);
   contextual = vector depends on the sentence (BERT).*
5. Embeddings timeline? → *word2vec → GloVe (static) → BERT (contextual) → modern
   encoders.*
6. Two task families? → *Predict a label/tag vs generate a sequence.*
7. How does semantic search compare texts? → *Embed both, take cosine similarity,
   retrieve top-k via an ANN index.*
8. Biggest NLP serving cost + first lever? → *Attention ~O(n²) in sequence length;
   cap the length first.*

---

## Module 15 — Pattern Recognition (how to spot it in an interview)

- Hear **"classify / detect / flag text"** → Family A; propose a simple baseline
  first, then BERT if it earns it; threshold by cost of error.
- Hear **"extract entities / tag each word"** → NER (sequence labelling), F1 metric.
- Hear **"summarize / translate / answer"** → Family B (seq-to-seq), expensive
  serving, BLEU/ROUGE or human eval; forward-link to M16 for LLMs.
- Hear **"find documents that mean the same thing"** → embeddings + cosine + ANN
  index (semantic search), link to M13/M16.
- Hear **"it must respond in a few ms"** → sequence-length cap, caching, batching,
  distillation; maybe on-device.
- Hear **"handles emojis / typos / new slang"** → subword tokenization, no OOV;
  and expect **drift** → monitor + retrain.

---

## Module 15 — Revision Notes / Mini Cheat Sheet

```
NLP PIPELINE:  raw text -> clean/normalize -> TOKENIZE -> EMBED -> model -> output
               (goal: numbers where distance ~ difference in meaning)

TOKENIZE:  word   (huge vocab, OOV)  | subword/BPE (small vocab, NO OOV = default)
           char   (tiny vocab, long sequences)      BPE = frequency-based merges

EMBEDDINGS:  word2vec -> GloVe  = STATIC  (one vector per word)
             BERT -> modern     = CONTEXTUAL (vector depends on sentence)
             "bank": static=SAME vector | contextual=A(river) vs B(money)

TASKS (2 families):
  label/tag  -> classification | sentiment | NER (per-token) | extractive QA
  generate   -> summarization | translation | generative QA   (seq-to-seq)

SEMANTIC SEARCH:  embed docs offline + query live -> COSINE similarity
                  -> top-k via ANN index (vector DB)    [links M13, M16 RAG]

SERVING:  attention ~ O(n^2) in seq length
          levers: CAP length -> cache -> batch -> distill/quantize
          tokenizer MUST match training (no train-serve skew)

CASES:  spam(fast drift, cost threshold) | tickets(low-conf -> human -> retrain)
        autocomplete(tiny model, on-device, per-keystroke budget)
LLMs -> Module 16.  This module = classic + BERT-era foundations.
```

---

> **Next module:** *Module 16 — Large Language Models & LLM Systems.* We build on
> everything here — tokenization, embeddings, and semantic search — and go deep on
> LLMs: prompting, in-context learning, fine-tuning vs RAG (retrieval-augmented
> generation), context windows, and how to design and serve LLM-powered systems at
> scale.
