---
title: "Module 4 — Data Engineering for ML"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — Data Engineering for ML

> **Why this module matters.**
> In Module 1 we learned a hard truth: an ML system is **90% data and systems
> work, 10% modelling**. This module is that 90%. Before a model can learn
> anything, someone has to *find* the data, *move* it, *clean* it, *label* it,
> *check* it, *balance* it, *version* it, and *protect* it. Get this layer wrong
> and even the best model quietly fails — trained on stale, leaked, imbalanced,
> or privacy-violating data. Get it right and everything downstream becomes
> easier. This module has strong overlap with classic **database warehousing /
> ETL** (so it carries real *exam* value for SEBI/RBI/GATE), and it is the single
> richest source of "what could go wrong" follow-ups in an interview. We build
> it, as always, from first principles and plain English.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★★     | ★★★    | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
choose **batch vs streaming** ingestion and name the right tool (Kafka / Kinesis
/ Pub-Sub); sketch a **pipeline DAG** and name an orchestrator (Airflow /
Kubeflow) and a processing engine (Spark / Flink / Beam); pick **lake vs
warehouse vs lakehouse** and justify it; describe four ways to **get labels**
(human, weak supervision, active learning, programmatic); set up **data
validation** (Great Expectations / TFDV); explain *why class imbalance hurts* and
list three fixes; **version and trace** data (DVC / lakeFS / Delta time-travel);
and handle **PII / GDPR** correctly.

> **How to read this module.** For every idea we go **problem → simplest attempt
> → why it breaks → the fix**, and we tie each concept to both the *interview*
> and the *exam*.

---

## 4.1 Data Sources & Ingestion: Batch vs Streaming

### Motivation (the problem that existed)

A model is useless without data, and that data lives *somewhere else* — in
transactional databases, log files, third-party APIs, sensors, click streams.
**Ingestion** is the act of moving data from those sources into a place where you
can process and learn from it. The first and most important choice is *how often*
and *in what size* you move it.

### Definition

- **Batch ingestion** moves data in large chunks on a **schedule** (every hour,
  every night). High latency, simple, cheap, and easy to reason about.
- **Streaming ingestion** moves data **event by event**, continuously, the moment
  it is produced. Low latency (fresh), but more complex and more expensive to run
  correctly.

![Top: batch ingestion loads big chunks on a schedule into a warehouse or lake. Bottom: streaming ingestion pushes each event through a message bus like Kafka to live consumers.](images/m04_01_batch_vs_stream.png)

### Intuition & analogy

Think about doing laundry. **Batch** is waiting until you have a full load and
running the machine once — efficient per item, but your favourite shirt might sit
dirty for three days. **Streaming** is washing each item the instant it gets
dirty — always fresh, but you run the machine constantly and it costs far more
water and effort. Neither is "better"; it depends on how fresh you need clean
clothes and how much you can spend.

### First-principles: which do I pick?

Ask exactly the questions from Module 1:

1. **How fresh must the data be?** If yesterday's data is fine (a nightly
   recommendation email) → **batch**. If you must react within seconds (fraud,
   live personalization) → **streaming**.
2. **What is the cost budget?** Streaming systems run 24/7 and need careful
   engineering (ordering, exactly-once, backpressure) → more expensive.
3. **How complex can the team handle?** Batch is a cron job. Streaming is a
   distributed always-on service.

### The streaming tools (know the three)

| Tool | Who | One-liner |
|------|-----|-----------|
| **Apache Kafka** | Open-source / Confluent | The de-facto durable, partitioned event log. Runs anywhere. |
| **Amazon Kinesis** | AWS | Managed Kafka-like streaming on AWS. |
| **Google Pub/Sub** | GCP | Managed, serverless publish/subscribe messaging. |

All three are **message buses**: producers *publish* events to a topic; many
consumers *subscribe* and read at their own pace. The bus decouples producers
from consumers and buffers spikes.

### Trade-offs & failure modes

- **Batch that is too stale:** a fraud model run once a day misses attacks that
  happen in minutes.
- **Streaming that loses order or duplicates:** without care you get
  double-counted transactions. Look for *exactly-once* / *at-least-once*
  guarantees.
- **Common pattern — do both (Lambda architecture):** a fast streaming path for
  fresh-but-approximate results plus a slow batch path for accurate corrections.

---

## 4.2 Data Pipelines & Orchestration

### Motivation

Ingestion is step one of many. Real data flows through a *chain* of steps:
extract → clean → validate → build features → aggregate → load/train. Each step
depends on the previous one, steps can fail, and they must run in the right order
every day. Doing this by hand does not scale. We need an **orchestrator**.

### Definition

- A **data pipeline** is a sequence of processing steps that transform raw data
  into something useful (features, a training set).
- An **orchestrator** schedules those steps, runs them in **dependency order**,
  **retries** failures, and **alerts** you when something breaks. Pipelines are
  usually modelled as a **DAG** (Directed Acyclic Graph): nodes are tasks, edges
  are "must run before".

![A pipeline drawn as a DAG: Extract feeds Clean/Validate, which fans out to Build Features and Aggregate, which both feed Load/Train; an orchestrator like Airflow or Kubeflow schedules, retries, and monitors the whole graph.](images/m04_02_orchestration_dag.png)

### Intuition & analogy

A pipeline DAG is a **recipe with prerequisites**: you cannot frost the cake
before you bake it, and you cannot bake before you mix. The orchestrator is the
head chef who reads the recipe, starts each step when its inputs are ready,
re-does a burnt step, and shouts if the oven breaks.

### Batch vs stream *processing* (not just ingestion)

The same batch/stream split from 4.1 applies to *processing*:

| | Batch processing | Stream processing |
|---|---|---|
| **Data unit** | Big bounded dataset | Unbounded, one event at a time |
| **Latency** | Minutes–hours | Milliseconds–seconds |
| **Engines** | Spark, Beam | Flink, Beam |
| **Example** | Nightly feature recompute | Live sessionization, fraud scoring |

### The tools (know what each is *for*)

- **Airflow** — the standard *batch* orchestrator; you write DAGs in Python, it
  schedules and monitors them.
- **Kubeflow (Pipelines)** — orchestration built for *ML on Kubernetes* (training,
  tuning, serving steps).
- **Apache Spark** — distributed *batch* engine for large-scale transforms and
  ML.
- **Apache Flink** — a true *streaming* engine (low-latency, stateful event
  processing).
- **Apache Beam** — one API to write a pipeline that can run on *either* a batch
  or a stream backend ("write once, run batch or stream").

### Trade-offs

Orchestration adds operational weight — you now run and monitor a scheduler. But
without it, a broken step at 3 a.m. means a silently stale model by morning. For
anything beyond a toy, orchestration is mandatory.

---

## 4.3 Where Data Lives: Lake vs Warehouse vs Lakehouse

### Motivation

Once data is ingested you must *store* it. There are three storage philosophies,
and choosing wrong makes everything slow or expensive. This section overlaps
directly with DBMS **data warehousing** — the concepts are the same, just with an
ML flavour.

### Definition

- **Data lake** — cheap storage of **raw** data in **any** format (S3, HDFS).
  **Schema-on-read**: you impose structure only when you query. Great for
  keeping everything; messy to query.
- **Data warehouse** — **structured**, cleaned data optimized for fast SQL
  analytics (BigQuery, Snowflake, Redshift). **Schema-on-write**: data must fit a
  schema before it lands. Clean and fast; less flexible, can be pricier per byte.
- **Lakehouse** — a newer hybrid: cheap lake storage **plus** warehouse features
  (ACID transactions, schema enforcement) on top, via a table format like **Delta
  Lake**, Apache Iceberg, or Hudi. "Best of both."

![Three columns: Data Lake stores raw any-format data cheaply with schema-on-read; Warehouse stores structured schema-on-write data for fast SQL; Lakehouse combines cheap lake storage with ACID and schema for reliable tables.](images/m04_03_storage_tiers.png)

### Comparison table

| Property | Lake (S3) | Warehouse (BigQuery/Snowflake) | Lakehouse (Delta) |
|----------|-----------|--------------------------------|-------------------|
| **Data type** | Any (raw, images, logs) | Structured/tabular | Any + tables |
| **Schema** | On read | On write | Enforced, evolvable |
| **Cost/byte** | Lowest | Higher | Low (lake storage) |
| **Query speed** | Slow (raw) | Fast SQL | Fast SQL |
| **ACID / reliability** | No | Yes | Yes |
| **Best for** | Dump everything, ML raw data | BI, dashboards, SQL analytics | Unified ML + analytics |

### First-principles: when each wins

- Choose a **lake** when you want to keep *all* raw data cheaply and figure out
  its use later (classic for ML: images, click logs).
- Choose a **warehouse** when analysts need fast, reliable SQL over clean tables.
- Choose a **lakehouse** when you want one system so you do not maintain a lake
  *and* a warehouse and constantly copy between them.

> **Exam bridge (DBMS):** schema-on-write vs schema-on-read, ETL vs ELT, and
> star/snowflake schemas from the warehousing module apply directly here. ELT
> ("load raw first, transform later") is the lake philosophy; ETL ("transform
> before load") is the classic warehouse philosophy.

---

## 4.4 Data Labeling

### Motivation

Supervised learning needs **labels** ("this transaction is fraud", "this image is
a cat"). Labels are often the *most expensive and slowest* part of an ML project.
Hand-labelling a million examples is impractical, so we need cheaper strategies.

### Definition & the four approaches

![Four labeling approaches: human labeling (accurate but slow and costly), weak supervision via Snorkel (combine noisy rules), active learning (label only the hard cases), and programmatic/heuristic label functions; plus semi-supervised learning with few labels and many unlabeled examples.](images/m04_04_labeling.png)

1. **Human labeling** — people label examples (in-house experts, or crowdsourcing
   like Mechanical Turk). **Highest quality, slowest, most expensive.** The gold
   standard, but does not scale to millions cheaply.
2. **Programmatic / heuristic labeling** — write simple **label functions** (code
   rules) that guess labels, e.g. "if the email contains the word *invoice*, tag
   it *finance*." Cheap and instant, but noisy.
3. **Weak supervision (Snorkel)** — combine *many* noisy label functions and let a
   model **learn how much to trust each one**, producing better labels than any
   single rule. This is the key idea behind **Snorkel**. Scales labelling to
   millions with no manual annotation.
4. **Active learning** — the model itself picks the **most informative** examples
   (the ones it is most unsure about) and asks a human to label *only those*. You
   get most of the accuracy for a fraction of the labelling cost.

A close cousin is **semi-supervised learning**: use a *few* labelled examples plus
*many* unlabelled ones to train.

### Worked example

You must label 1,000,000 customer support tickets by topic.

- **All human:** at ~$0.10/ticket, that is ~$100k and weeks of work.
- **Programmatic:** write 20 keyword rules → label all 1M in seconds, but ~15%
  wrong.
- **Weak supervision:** feed those 20 noisy rules to Snorkel → it de-noises and
  reconciles them → far fewer errors, still near-zero human cost.
- **Active learning:** have humans label only the 5,000 tickets the model is most
  unsure about → best accuracy-per-dollar.

### Trade-offs

The universal trade is **cost vs quality vs speed**. Humans are gold but slow and
expensive; programmatic/weak labels scale cheaply but are noisier. Real systems
**mix**: bootstrap with weak/programmatic labels, then use active learning to
spend precious human hours only where they matter.

---

## 4.5 Data Quality, Validation & Schema Enforcement

### Motivation

Recall the Module 1 warning: *a silent schema change upstream can corrupt your
model with no error message.* Data does not throw exceptions — a column that
turns from "age in years" to "age in months" trains a broken model, and you only
find out from bad predictions weeks later. The fix is to **validate data
automatically** before it is allowed into training or serving.

### Definition

- **Data validation** = automated checks that incoming data matches expectations.
- A **schema** here is a contract: which columns exist, their types, allowed
  ranges, and how much null/missing is tolerable.
- **Schema enforcement** rejects or flags data that violates the contract.

![Incoming data passes through a validation step (Great Expectations or TFDV); if it passes, it proceeds to training; if it fails, the pipeline alerts and stops. Checks include schema, types, ranges, nulls, distribution drift, and uniqueness.](images/m04_05_validation.png)

### Intuition & analogy

Validation is a **bouncer at the door**. Every batch of data must show its ID
(schema), be in the right shape (types/ranges), and not be obviously fake
(distribution looks like yesterday's). Bad data gets turned away *before* it
poisons the model, and someone gets paged.

### What to check (first-principles checklist)

- **Schema:** expected columns present, correct types.
- **Ranges / domains:** age in [0, 120]; country in a known set.
- **Missingness:** null rate below a threshold.
- **Uniqueness / keys:** no duplicate primary keys.
- **Distribution:** does today's data *look like* the training data? (early
  drift detection — deep dive in Module 10).

### The tools

- **Great Expectations** — a Python library where you declare "expectations"
  (assertions) about data and get a validation report. General-purpose.
- **TFDV (TensorFlow Data Validation)** — infers a schema from your data, detects
  anomalies, and flags **training–serving skew** and drift. ML-native.

### Trade-offs

Too-strict validation blocks pipelines on harmless changes (false alarms);
too-loose validation lets bad data through. Start with schema + ranges + null
checks, and tighten as you learn what actually breaks.

---

## 4.6 Sampling, Class Imbalance & Negative Sampling

### Motivation

In many important problems the classes are wildly **imbalanced**: fraud is maybe
0.1% of transactions, disease maybe 1% of patients. Naively training on this data
produces a model that looks great and is useless.

### Why imbalance hurts (the math/intuition)

Suppose 99% of transactions are legitimate. A lazy model that predicts "not
fraud" for *everything* scores **99% accuracy** — while catching **zero** fraud.
Accuracy is dominated by the majority class, so it *lies*. The model also has
little incentive to learn the rare pattern because the loss is already tiny.

![Class imbalance: a majority class fills 99% and the minority just 1%, so a model can score 99% accuracy by always predicting the majority; fixes are resampling, class weights in the loss, and negative sampling for retrieval.](images/m04_06_imbalance.png)

### The fixes

1. **Resampling.**
   - *Oversample* the minority (duplicate or synthesize minority examples — e.g.
     **SMOTE** creates synthetic minority points).
   - *Undersample* the majority (drop some majority examples).
   - Goal: give the model a more balanced view so the rare class matters.
2. **Class weights.** Instead of changing the data, change the **loss**: make each
   minority mistake count more. E.g. weight the positive class by
   `(#negatives / #positives)` so the model "pays" more for missing fraud.
3. **Better metrics.** Stop trusting accuracy. Use **precision, recall, F1, and
   PR-AUC** (Module 7), which focus on the rare positive class.
4. **Negative sampling (for retrieval / recommendation).** When there are billions
   of possible negatives (every item a user did *not* click), you cannot use them
   all. You **sample a small set of negatives** per positive to train on. This
   makes training tractable and is the standard trick for two-tower retrieval and
   word2vec-style models.

### Worked intuition for class weights

If positives are 1% of data, set the positive weight ≈ 99. Now a single missed
fraud contributes as much to the loss as 99 correctly-handled legit transactions,
forcing the model to actually learn the rare pattern.

### Trade-offs

- Oversampling can cause **overfitting** to the duplicated minority points.
- Undersampling **throws away** real data (information loss).
- Aggressive class weights can make the model **over-predict** the rare class
  (too many false positives). Always tie the choice back to the *cost of being
  wrong* (Module 1's 2×2).

---

## 4.7 Data Versioning & Lineage

### Motivation

Six months from now someone asks: *"Why did the model make this decision?"* or a
regulator demands you reproduce a past model exactly. If you only version *code*
but not *data*, you cannot. Models are a function of **code + data + config**, so
all three must be versioned together.

### Definition

- **Data versioning** = tracking snapshots of a dataset over time, like Git for
  data, so any past version can be retrieved.
- **Lineage** = the recorded *history* of where data came from and every
  transformation it went through (source → cleaned → features → model). Answers
  "what produced this number?"

![Data versioning: dataset v1 → v2 → v3, each commit tracked; tools like DVC, lakeFS, and Delta time-travel pin data, code, and model together so any past model can be reproduced.](images/m04_07_versioning.png)

### The tools

- **DVC (Data Version Control)** — Git-like versioning for datasets and models;
  stores large files in remote storage and small pointers in Git.
- **lakeFS** — Git-like branches, commits, and merges over a whole data lake.
- **Delta Lake time-travel** — query a table *as of* a past version or timestamp
  (`VERSION AS OF 42`), built into the lakehouse.

### Why it matters (first-principles)

- **Reproducibility:** re-train the exact same model → pin the exact data version
  + code + random seed.
- **Debugging:** a metric dropped after a retrain → diff the data version.
- **Rollback:** a bad dataset shipped → revert to the previous version instantly.
- **Audit / compliance:** prove *which* data trained a decision (critical for
  regulated finance — SEBI/RBI).

### Trade-offs

Versioning large datasets costs storage and discipline. But the cost of *not*
being able to reproduce or audit a production model is far higher, especially
under regulation.

---

## 4.8 Privacy-Aware Data Handling (PII, GDPR)

### Motivation

Data about people is regulated. Mishandling it risks fines, lawsuits, and lost
trust. For finance and government exams (SEBI, RBI) this is *directly testable*,
and in interviews "how do you handle PII?" is a common senior probe.

### Definition

- **PII (Personally Identifiable Information)** — data that identifies a person:
  name, email, phone, PAN/Aadhaar, address, precise location.
- **GDPR** (EU) / **DPDP Act** (India) / sector rules (SEBI, RBI) — laws that
  govern how personal data may be collected, stored, used, and deleted.

![Raw data containing PII (name, PAN) is protected by masking, hashing, or anonymization before it becomes safe to train on or share; core principles are minimize, consent, purpose-limit, right-to-be-forgotten, access control, and audit; this has SEBI/RBI/GDPR/DPDP exam value.](images/m04_08_privacy.png)

### Core principles (first-principles)

- **Data minimization:** collect only what you need.
- **Consent & purpose limitation:** use data only for the purpose the user agreed
  to.
- **Right to be forgotten:** users can demand deletion — your pipelines must be
  able to find and remove their data.
- **Access control & audit:** restrict who can see PII and log every access.

### The techniques

| Technique | What it does | Note |
|-----------|--------------|------|
| **Masking / redaction** | Hide fields (`4111-****-****-1234`) | Simple, reversible if key kept |
| **Hashing / tokenization** | Replace an identifier with an irreversible token | One-way; good for joins without exposing raw ID |
| **Anonymization** | Remove/aggregate so individuals cannot be re-identified | Strong but can reduce data utility |
| **Pseudonymization** | Replace identifiers with pseudonyms, key stored separately | GDPR-recognized middle ground |
| **Differential privacy** | Add calibrated noise so no single person's data is detectable | Strong formal guarantee (Module 18) |

### First-principles rule of thumb

**Never train on raw PII.** Anonymize or pseudonymize as *early* as possible in
the pipeline, keep raw PII in a locked, access-controlled, audited store, and
make deletion a first-class operation.

> **Exam value:** SEBI and RBI IT papers test data-protection and IT-governance
> concepts; GDPR/DPDP definitions and the difference between anonymization and
> pseudonymization are fair game.

### Trade-offs

More privacy protection usually means **less data utility** (anonymized data
trains slightly worse models). The design job is to protect people while keeping
enough signal to be useful — and when in doubt, protect the person.

---

## Module 4 — Interview Mapping (what companies probe)

| Company | How Module 4 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "How do you get and validate training data at scale?" | "We collect logs" | Names ingestion mode, validation gate, labeling strategy, versioning |
| **Amazon / Uber / Stripe** | Batch vs streaming for fraud/ETA | Picks one | Weighs freshness vs cost, proposes Lambda hybrid |
| **OpenAI / Anthropic** | Labeling & data quality for LLMs | "Hire labelers" | Weak supervision + active learning + dedup + PII scrubbing |
| **Any fintech** | "How do you handle customer PII?" | Ignores it | Minimize, anonymize early, access control, right-to-be-forgotten |

**Common opening:** *"Where does your data come from and how do you know it's
good?"* Strong answer: name the **sources**, the **ingestion mode**, a
**validation gate**, a **labeling** plan, and **versioning** — in one breath.

---

## Module 4 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT:** strong overlap with **data warehousing, ETL/ELT**, and
  **data-protection / IT-governance**. Know lake vs warehouse, schema-on-read vs
  schema-on-write, PII handling, and GDPR/DPDP basics (Sections 4.3, 4.8).
- **GATE CS / DA:** warehousing concepts, ETL, sampling, and class imbalance
  handling appear in the DA paper. Know oversampling/undersampling and why
  accuracy misleads under imbalance (Section 4.6).
- **ISRO / DRDO:** occasional DBMS/warehousing definitions.

> **Flag:** this module has the *most exam value* in the whole course because it
> overlaps with the well-established DBMS warehousing/ETL syllabus.

---

## Module 4 — Common Mistakes & Misconceptions

1. **"Streaming is always better because it's fresh."** No — it is more complex
   and costly; batch is fine when yesterday's data suffices.
2. **"A data lake and a warehouse are the same thing."** No — raw + schema-on-read
   vs structured + schema-on-write. Lakehouse merges them.
3. **"Accuracy tells me my imbalanced model is good."** No — 99% accuracy can mean
   zero fraud caught. Use precision/recall/PR-AUC.
4. **"Labels just come from humans."** No — weak supervision, programmatic labels,
   and active learning scale far cheaper.
5. **"If the code is versioned, I can reproduce the model."** No — you must also
   version the **data** and config.
6. **"We'll deal with PII later."** No — anonymize *early*; retrofitting privacy is
   painful and risky.
7. **"Data validation is optional."** No — a silent schema change is the #1 cause
   of production ML bugs (Module 1).

---

## Module 4 — MCQs (with answers & explanations)

**Q1.** You must flag fraud within seconds of a transaction. Which ingestion fits?
a) Nightly batch  b) Streaming (Kafka/Kinesis)  c) One-time export  d) Manual CSV

<details><summary>Answer</summary>**b.** Fraud needs event-by-event, low-latency
streaming ingestion. A nightly batch is far too stale.</details>

**Q2.** A data **lake** differs from a **warehouse** primarily because:
a) The lake is faster for SQL
b) The lake stores raw data with schema-on-read; the warehouse stores structured
   data with schema-on-write
c) The warehouse cannot store structured data
d) They are identical

<details><summary>Answer</summary>**b.** Lake = cheap raw, schema-on-read;
warehouse = clean structured, schema-on-write. A lakehouse combines both.</details>

**Q3.** A fraud model reports 99% accuracy but catches no fraud. The cause is:
a) Overfitting  b) Class imbalance (accuracy is dominated by the majority class)
c) A cache miss  d) Data leakage

<details><summary>Answer</summary>**b.** With 99% negatives, always predicting
"not fraud" scores 99% accuracy while catching zero fraud. Use precision/recall/
PR-AUC and rebalancing/class weights.</details>

**Q4.** **Weak supervision** (e.g. Snorkel) mainly lets you:
a) Skip having any data
b) Combine many noisy labeling rules into better labels without manual annotation
c) Deploy models faster
d) Encrypt PII

<details><summary>Answer</summary>**b.** Snorkel de-noises and reconciles multiple
noisy label functions to produce training labels at scale.</details>

**Q5.** **Active learning** reduces labeling cost by:
a) Labeling every example twice
b) Having the model pick the most *uncertain* examples for humans to label
c) Removing all labels
d) Using a bigger model

<details><summary>Answer</summary>**b.** You spend scarce human labeling effort
only on the most informative (uncertain) examples.</details>

**Q6.** Delta Lake **time-travel** is useful because it lets you:
a) Predict the future
b) Query a table as it existed at a past version/timestamp, aiding reproducibility
   and rollback
c) Speed up training
d) Anonymize PII automatically

<details><summary>Answer</summary>**b.** Time-travel gives you data versioning
inside the lakehouse — query `VERSION AS OF n` to reproduce or roll back.</details>

**Q7.** The safest way to handle PII before training is to:
a) Train on raw PII, delete later
b) Anonymize/pseudonymize early, restrict access, and support deletion requests
c) Email it to the team
d) Store it in plain text with no logging

<details><summary>Answer</summary>**b.** Minimize, anonymize early, access-control,
audit, and honour the right to be forgotten (GDPR/DPDP/SEBI/RBI).</details>

**Q8.** Which tool is a *streaming* processing engine (not just batch)?
a) Airflow  b) Spark (core)  c) Flink  d) BigQuery

<details><summary>Answer</summary>**c.** Flink is a true low-latency stateful
stream processor. Airflow orchestrates; Spark core is batch; BigQuery is a
warehouse. (Beam can target either.)</details>

---

## Module 4 — Design Exercises (easy → hard)

- **Easy.** For each, say batch or streaming and why: (1) nightly sales report;
  (2) live credit-card fraud alerts; (3) monthly churn model retrain; (4) live
  "trending now" feed. *(1,3 batch; 2,4 streaming.)*
- **Easy.** Given a table `users(name, email, age, country)`, list five data
  validation checks you would run before training.
- **Medium.** You have 2M unlabeled support tickets and a $5k labeling budget.
  Design a labeling plan mixing programmatic, weak supervision, and active
  learning. What fraction goes to humans?
- **Medium.** A model was 91% recall at launch and is 78% after four months, code
  unchanged. Which Module 4 mechanisms (validation, versioning, drift checks) help
  you diagnose it, and how?
- **Hard.** Design the full data platform for a ride-hailing ETA model: sources,
  ingestion mode(s), storage tier, orchestration, validation, and versioning.
  State one failure mode per layer.
- **Hard.** A fraud dataset is 0.2% positive. Design the sampling / weighting /
  metric strategy end-to-end, and explain how the *cost of a false negative vs
  false positive* changes your choices.

---

## Module 4 — Concept Review (one page)

- **Ingestion:** *batch* = scheduled big chunks (cheap, stale); *streaming* =
  event-by-event (fresh, complex). Tools: Kafka, Kinesis, Pub/Sub.
- **Pipelines:** modelled as a **DAG**; **orchestrators** (Airflow, Kubeflow)
  schedule/retry/alert. Engines: Spark/Beam (batch), Flink/Beam (stream).
- **Storage:** *lake* (raw, schema-on-read, S3) · *warehouse* (structured,
  schema-on-write, BigQuery/Snowflake) · *lakehouse* (both, Delta Lake).
- **Labeling:** human (gold, costly) · programmatic (cheap, noisy) · weak
  supervision/Snorkel (combine noisy rules) · active learning (label the hard
  cases).
- **Validation:** a gate before training (Great Expectations, TFDV) — schema,
  ranges, nulls, distribution.
- **Imbalance:** accuracy lies; fix with resampling, class weights, negative
  sampling; measure with PR-AUC/F1.
- **Versioning & lineage:** DVC, lakeFS, Delta time-travel → reproducibility,
  rollback, audit.
- **Privacy:** minimize, anonymize early, access-control, audit,
  right-to-be-forgotten (PII, GDPR/DPDP, SEBI/RBI).

---

## Module 4 — Flash Cards (Q → A)

1. Batch vs streaming in one line? → *Batch = scheduled chunks (cheap, stale);
   streaming = per-event (fresh, complex).*
2. Name three message buses? → *Kafka, Kinesis, Pub/Sub.*
3. What is an orchestrator? → *Runs pipeline DAG tasks in order, retries, alerts
   (Airflow/Kubeflow).*
4. Lake vs warehouse? → *Raw + schema-on-read vs structured + schema-on-write.*
5. What is a lakehouse? → *Cheap lake storage + ACID/schema (Delta Lake).*
6. What does Snorkel do? → *Combines many noisy label functions into better labels
   (weak supervision).*
7. Why does accuracy lie under imbalance? → *Predicting the majority scores high
   while catching none of the rare class.*
8. Three imbalance fixes? → *Resampling, class weights, negative sampling.*
9. Three data-versioning tools? → *DVC, lakeFS, Delta time-travel.*
10. Rule for PII? → *Never train on raw PII; anonymize early, control access,
    support deletion.*

---

## Module 4 — Pattern Recognition (how to spot it in an interview)

- Hear **"react within seconds / real-time events"** → streaming, Kafka/Flink.
- Hear **"nightly / hourly / report"** → batch, Airflow + Spark.
- Hear **"store everything cheaply, decide later"** → data lake / lakehouse.
- Hear **"we can't afford to label everything"** → weak supervision + active
  learning.
- Hear **"the data upstream keeps changing"** → validation gate (GE/TFDV).
- Hear **"only 0.1% are positive"** → class imbalance: resample/weights/PR-AUC.
- Hear **"reproduce / audit / roll back the model"** → data versioning + lineage.
- Hear **"customer / personal data"** → PII, anonymize, GDPR/DPDP, access control.

---

## Module 4 — Revision Notes / Mini Cheat Sheet

```
INGESTION:  BATCH (scheduled, cheap, stale)  |  STREAMING (per-event, fresh, complex)
            buses: Kafka | Kinesis | Pub/Sub          hybrid = Lambda architecture

PIPELINES:  DAG of tasks; orchestrate = Airflow / Kubeflow (schedule+retry+alert)
            batch engines: Spark, Beam    stream engines: Flink, Beam

STORAGE:    LAKE (raw, schema-on-read, S3) | WAREHOUSE (structured, schema-on-write,
            BigQuery/Snowflake) | LAKEHOUSE (both + ACID, Delta Lake)

LABELS:     human (gold, slow) | programmatic (cheap, noisy) |
            weak-supervision/Snorkel (combine noisy rules) | active-learning (hard cases)

VALIDATE:   gate BEFORE training — Great Expectations / TFDV
            check: schema | types | ranges | nulls | uniqueness | distribution/drift

IMBALANCE:  accuracy LIES -> resample (over/under, SMOTE) | class-weights |
            negative-sampling (retrieval) ; measure with PR-AUC / F1

VERSION:    data+code+config together -> DVC | lakeFS | Delta time-travel
            = reproduce | rollback | audit | debug

PRIVACY:    PII (name/PAN/email); minimize | anonymize EARLY | pseudonymize |
            access-control + audit | right-to-be-forgotten   (GDPR / DPDP / SEBI / RBI)
```

---

> **Next module:** *Module 5 — Feature Engineering & Feature Stores.* Now that the
> data is ingested, clean, labelled, validated, balanced, versioned, and private,
> we turn it into the numerical **features** a model actually consumes — and we
> meet the **feature store** that keeps training and serving in perfect agreement
> (killing training–serving skew).
