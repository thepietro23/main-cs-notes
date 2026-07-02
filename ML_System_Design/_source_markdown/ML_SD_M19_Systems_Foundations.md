---
title: "Module 19 — Systems & Distributed Systems Foundations for ML"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 19 — Systems & Distributed Systems Foundations for ML

> **Why this module exists.**
> An ML system *is* a distributed system that happens to have a model inside it.
> The model is the easy part. Getting a prediction to a million users in under
> 100 ms, without falling over when one machine dies, without serving stale
> garbage from a cache, and without going bankrupt on infrastructure — that is
> the hard part, and it is pure classic systems engineering. Almost every serving
> answer you will give in an interview (Modules 8 and 11) rests on the ideas in
> this module: load balancing, caching, the right database, message queues, the
> CAP theorem, gRPC, reliability budgets, the latency ladder, and
> back-of-the-envelope sizing. Candidates who cannot do a capacity estimate, or
> who think a cache is "just make it faster," get exposed fast. We build every
> idea from first principles, in plain English, and tie each one to how it shows
> up in a real ML serving design.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★★★    | ★★★★   | ★★★★       | ★★★★★     | ★★★★★       |

> **Flag — HIGH exam value.** Unlike the framing and case-study modules, this one
> has *strong CS-fundamentals overlap*. Load balancing, caching, CAP, consistency,
> databases, and queues are staple **GATE CS/DA, SEBI IT, and RBI IT** topics and
> appear on almost every written exam. Learn this module for the exam *and* the
> interview — the return is double.

**What you must be able to do after this module:**
choose L4 vs L7 load balancing and a routing algorithm; pick a cache pattern and
eviction policy and explain cache-friendliness for ML; select SQL / NoSQL /
key-value / vector / time-series storage for a given ML workload; explain Kafka's
log, partitions, and consumer groups; state the CAP theorem correctly and pick a
consistency model; justify gRPC over REST for model serving; define SLA / SLO /
SLI and design retries, timeouts, and circuit breakers; recite the latency ladder
"numbers every engineer should know"; and do a back-of-the-envelope QPS, storage,
and bandwidth sizing on the spot.

> **How to read this module.** For every idea we go **problem → simplest attempt
> → why it breaks → the fix**, and we connect each systems concept to the ML
> serving decision it drives.

---

## 19.1 Load Balancing (L4 vs L7, and the algorithms)

### Motivation (the problem that existed)

You trained a great model and wrapped it in one server. It handles 500 requests
per second. Traffic grows to 50,000 QPS. One machine cannot do it, and if that
one machine dies, your whole product is down. The obvious fix is to run **many
identical copies** of the server. But now the client has a new question: *which
copy do I talk to?* You cannot hard-code one address (that defeats the point),
and you cannot make every client know about every server (they come and go).

The fix is a **load balancer (LB)**: a single front door that spreads incoming
requests across a fleet of backend servers, hides individual machines, and
routes around dead ones.

![Load balancer sitting between clients and a fleet of identical backend model servers, spreading incoming requests across healthy replicas and routing around a failed one via health checks.](images/m19_01_load_balancing.png)

### Definition

- A **load balancer** is a component that receives client requests and forwards
  each one to one of several backend servers, according to a **routing
  algorithm**, while continuously **health-checking** backends and removing dead
  ones from rotation.
- **Layer 4 (L4) load balancing** operates at the *transport* layer (TCP/UDP). It
  looks only at IP addresses and ports — not the request content. It is fast and
  cheap because it just forwards packets/connections.
- **Layer 7 (L7) load balancing** operates at the *application* layer (HTTP/gRPC).
  It can read the request — URL path, headers, cookies — and route based on
  content (e.g. send `/predict/v2` to the new model, `/predict/v1` to the old).
  It is smarter but does more work per request.

### Intuition & analogy

Think of a busy clinic. An **L4** receptionist just counts heads and sends you to
"the next free doctor" without asking why you came. An **L7** receptionist reads
your form ("skin problem") and sends you to the dermatologist. L7 is smarter and
enables things like A/B routing and canary releases; L4 is faster and simpler.

### Routing algorithms (first principles)

The LB must decide *which* backend gets the next request. Common policies:

| Algorithm | How it works | Best when |
|-----------|--------------|-----------|
| **Round robin** | Send to servers in turn: 1, 2, 3, 1, 2, 3… | Backends are identical and requests are similar cost |
| **Weighted round robin** | Bigger servers get proportionally more traffic | Mixed hardware (some GPUs, some CPUs) |
| **Least connections** | Send to the backend with the fewest in-flight requests | Request costs vary a lot (some inferences slow) |
| **Least response time** | Combine active connections + measured latency | Latency-sensitive serving |
| **Consistent hashing** | Hash a key (user id) → always the same server | You want cache/session affinity (see 19.2) |
| **Random (two-choices)** | Pick 2 at random, send to the less-loaded one | Cheap, near-optimal spread at scale |

> **ML angle.** For a **stateless** model server, least-connections or round
> robin is fine. If each server caches per-user embeddings or holds a shard of a
> huge index, use **consistent hashing** so the same user keeps hitting the
> server that already has their data warm — a huge latency win.

### Trade-offs and failure modes

- **Health checks are non-negotiable.** Without them the LB keeps sending traffic
  to a crashed server → users get errors. A good check hits a real `/healthz` that
  confirms the model is *loaded*, not just that the process is up.
- **The LB itself is a single point of failure.** In production you run the LB in
  a redundant pair (or use a managed/anycast LB) so it, too, survives a failure.
- **Sticky sessions vs even spread.** Affinity (always route a user to the same
  box) helps caches but can create hot spots if one user is very heavy.

---

## 19.2 Caching (Redis / Memcached, patterns, eviction)

### Motivation

Some work is expensive and *repeated*. Recomputing a user's recommendations, or
re-reading the same product row from the database a million times a second, is
wasteful. A **cache** stores the answer to expensive/repeated work in fast memory
so the next request gets it in microseconds instead of milliseconds.

![Cache-aside flow: application checks the cache first; on a hit it returns instantly, on a miss it reads the database, stores the result in the cache with a TTL, and returns it. Eviction policies LRU and LFU shown removing cold entries when memory fills.](images/m19_02_caching.png)

### Definition

A **cache** is a small, fast store (usually in RAM) that holds a copy of data
that is expensive to fetch or compute. **Redis** and **Memcached** are the two
industry-standard in-memory caches.

- **Memcached:** dead-simple key→value string cache, multi-threaded, great for
  pure "make reads fast."
- **Redis:** richer — data structures (lists, sets, sorted sets, hashes),
  persistence, pub/sub, atomic ops. The default choice when you need more than
  plain get/set (e.g. leaderboards, rate limiters, feature caches).

### Caching patterns (how the app and cache cooperate)

- **Cache-aside (lazy loading).** The app checks the cache first. **Hit** → return
  it. **Miss** → read the database, write the value into the cache (with a TTL),
  return it. Simplest and most common. Downside: the first request after a miss is
  slow, and the cache can hold stale data until it expires.
- **Write-through.** On every write, update the cache *and* the database together.
  Reads are always fresh; writes are a bit slower. Good when reads far outnumber
  writes.
- **Write-back (write-behind).** Write to the cache immediately, flush to the DB
  later in batches. Fastest writes, but you can lose data if the cache dies before
  flushing. Rare in ML serving.

### Eviction policies (what to throw out when memory is full)

Cache memory is finite. When it fills, something must go:

| Policy | Evicts | Good for |
|--------|--------|----------|
| **LRU** (Least Recently Used) | The item untouched for the longest | General purpose; recent = likely-reused |
| **LFU** (Least Frequently Used) | The item accessed fewest times | Stable "popular items" that must stay hot |
| **FIFO** | The oldest inserted item | Rarely ideal; simple |
| **TTL expiry** | Anything past its time-to-live | Data that goes stale on a clock (prices, features) |

**TTL (time-to-live)** is the seconds an entry is allowed to live before it is
considered stale and dropped. TTL is your main knob for *freshness vs load*: a
short TTL means fresher data but more cache misses (more DB/model load); a long
TTL means less load but staler answers.

### Cache-friendliness for ML

- **Cache the expensive, reusable, and slow-changing.** Precomputed batch
  recommendations, popular-item features, and embeddings are ideal cache
  contents. A per-request personalized score that is never repeated is *not*
  worth caching.
- **Feature caching** is standard: an online feature store keeps hot features in
  Redis so the serving path avoids a slow database read (Module 5).
- **Beware the cache stampede (thundering herd):** a hot key expires and thousands
  of requests all miss and hit the DB at once. Fixes: add small random jitter to
  TTLs, or use a lock so only one request refills the key.
- **Cache invalidation is famously hard.** When the model version changes, stale
  cached predictions become wrong. Version your cache keys (`preds:v7:user123`) so
  a new model naturally misses and refills.

> **Interview line.** "There are only two hard things in computer science: cache
> invalidation and naming things." Show you know *when* a cache helps (high
> read/compute cost + high reuse + tolerance for slight staleness) and *when it
> hurts* (write-heavy, must-be-fresh, low reuse).

---

## 19.3 Databases for ML (SQL, NoSQL, key-value, vector, time-series)

### Motivation

"Where does the data live?" is not one question — different ML data has wildly
different shapes and access patterns. Training data, online features, embeddings,
and metrics logs each want a *different* kind of store. Picking the wrong one
means slow queries, huge bills, or an index that cannot answer your question at
all.

![A row of database types — relational SQL, document/wide-column NoSQL, key-value, vector, and time-series — each labeled with the ML workload it serves best, from transactional metadata to nearest-neighbor embedding search and metrics.](images/m19_03_databases.png)

### The families (and when each wins)

- **Relational / SQL** (Postgres, MySQL). Data in tables with a fixed schema and
  relationships; strong consistency and joins; supports transactions (ACID). Best
  for structured, related data where correctness matters — user accounts, orders,
  labels, experiment metadata.
- **NoSQL document / wide-column** (MongoDB, Cassandra, DynamoDB). Flexible
  schema, scales horizontally to huge write volumes, weaker joins. Best for
  large-scale, semi-structured data and high write throughput — event logs, user
  profiles, clickstreams.
- **Key-value** (Redis, DynamoDB, RocksDB). Just `get(key)` / `put(key, value)`,
  extremely fast. Best for the **online feature store** and low-latency lookups on
  the serving path.
- **Vector database** (FAISS, Milvus, Pinecone, pgvector). Stores high-dimensional
  **embeddings** and answers *approximate nearest neighbour* (ANN) queries — "find
  the 50 items most similar to this vector." This is the backbone of semantic
  search, retrieval, and candidate generation for recommenders (Modules 12, 13).
- **Time-series** (Prometheus, InfluxDB, TimescaleDB). Optimized for
  timestamp-indexed metrics with fast range/rollup queries. Best for monitoring,
  drift metrics, and any "value over time" data (Module 10).

### Comparison table

| Type | Data shape | Query strength | Consistency | ML use |
|------|-----------|----------------|-------------|--------|
| **SQL** | Tables, fixed schema | Joins, transactions | Strong (ACID) | Labels, metadata, experiments |
| **NoSQL doc/column** | Flexible docs / wide rows | Key + range, scale-out writes | Tunable/eventual | Event logs, profiles, clickstream |
| **Key-value** | Opaque value by key | Point get/put (µs) | Usually eventual | Online feature store, session cache |
| **Vector** | Dense embeddings | ANN similarity search | Eventual (index) | Semantic search, retrieval, recs |
| **Time-series** | (time, value) points | Range, downsample, rollup | Eventual | Monitoring, drift, metrics |

### First-principles: how to choose

Ask three questions: **(1) What is the access pattern?** Point lookups → key-value;
similarity → vector; range over time → time-series; complex joins → SQL. **(2) How
big and how write-heavy?** Massive writes that must scale out → NoSQL. **(3) How
strict is consistency?** Money/labels → strong (SQL); logs/features → eventual is
fine. A real ML system uses **several** of these together, not one.

> **Common real design.** Postgres for metadata, Kafka + a data lake for raw
> events, Redis (key-value) as the online feature store, and a vector DB for
> candidate retrieval — all in one recommender. Naming this stack is a strong
> senior signal.

---

## 19.4 Message Queues & Streaming (Kafka, Flink, Spark Streaming)

### Motivation

Systems must talk to each other, but calling a service *directly and
synchronously* is fragile: if the downstream is slow or down, the caller blocks or
fails, and a traffic spike overwhelms everyone. We want to **decouple** producers
from consumers so each can work at its own pace and survive the other being down.
The answer is a **message queue / log** in the middle.

![Kafka's append-only commit log split into partitions, with producers appending events at the end, each consumer group tracking its own offset, and partitions distributed across brokers for parallelism and replay.](images/m19_04_kafka_log.png)

### Kafka — the distributed commit log

**Apache Kafka** is not a classic queue that deletes messages after reading. It is
a **durable, append-only log**: producers append events to the end; consumers read
forward at their own pace and can **replay** history.

- **Topic:** a named stream of events (e.g. `clicks`, `transactions`).
- **Partition:** a topic is split into partitions — ordered, append-only sequences.
  Partitions are the unit of **parallelism** and are spread across **brokers**
  (servers). Order is guaranteed *within* a partition, not across partitions.
- **Offset:** each message's position in a partition. A consumer stores its offset,
  so it knows where it left off and can rewind to reprocess.
- **Consumer group:** a set of consumers that share the work — each partition is
  read by exactly one consumer in the group, so adding consumers (up to the
  partition count) scales throughput. A second group reading the same topic gets
  its *own* independent copy of the stream.
- **Replication:** each partition is copied to several brokers, so a broker dying
  loses no data.

> **Why the log shape matters for ML.** Because Kafka *retains and replays*, you
> can (1) feed the same event stream to real-time features *and* to a training
> pipeline (avoiding training-serving skew, Module 5), and (2) reprocess history
> when you add a new feature. A delete-on-read queue cannot do this.

### Stream processors — computing on the flow

Kafka *moves* events; a **stream processor** *computes* on them continuously:

- **Apache Flink.** True event-at-a-time streaming with low latency, stateful
  windows, and event-time handling. Best for real-time features and fraud
  detection where every millisecond and correct time-windowing matter.
- **Spark Streaming (Structured Streaming).** Processes data in small
  **micro-batches**. Slightly higher latency but reuses the batch Spark ecosystem —
  great when you already run Spark for batch and want "good enough" near-real-time.

| | **Batch** | **Micro-batch (Spark)** | **Streaming (Flink)** |
|--|-----------|-------------------------|-----------------------|
| Latency | minutes–hours | seconds | milliseconds |
| Model | process a fixed dataset | small chunks on a clock | event-by-event |
| ML use | training, nightly features | near-real-time features | fraud, live personalization |

### Trade-offs

- **Decoupling + buffering** are the whole point: a spike is absorbed by the log
  instead of crushing the consumer; a down consumer catches up later.
- **Ordering only holds within a partition** — choose your partition key (e.g. by
  user id) so events that must stay ordered land in the same partition.
- **At-least-once vs exactly-once.** By default you may see a message twice on
  retry; design consumers to be **idempotent**, or use exactly-once semantics where
  supported.

---

## 19.5 CAP Theorem, Consistency, Replication & Sharding

### Motivation

Once your data lives on **many machines** (for scale and to survive failures), a
brutal truth appears: the network between them *will* fail sometimes, and when it
does you must choose between answering with possibly-stale data or refusing to
answer. This is the **CAP theorem**, and it silently shapes every distributed
store you pick.

![CAP theorem triangle showing Consistency, Availability, and Partition tolerance, with the rule that during a network partition a system can keep only two — illustrated as CP (refuse to serve stale) versus AP (serve possibly stale but stay up).](images/m19_05_cap_theorem.png)

### The CAP theorem (stated correctly)

A distributed data store can provide at most **two** of these three at once:

- **C — Consistency:** every read sees the most recent write (all nodes agree).
- **A — Availability:** every request gets a (non-error) response.
- **P — Partition tolerance:** the system keeps working even when the network
  between nodes is broken.

The subtlety most candidates miss: **network partitions happen whether you like it
or not**, so P is not really optional. The *real* choice is, **during a
partition**, do you sacrifice **C** or **A**?

- **CP system** (e.g. HBase, Zookeeper, a leader-based SQL): during a partition it
  **refuses** requests it cannot serve consistently → stays correct, drops
  availability. Choose when stale data is dangerous (bank balance).
- **AP system** (e.g. Cassandra, DynamoDB default): during a partition it **keeps
  answering** with possibly-stale data → stays up, drops consistency. Choose when
  being up matters more than perfect freshness (feature store, product catalog).

### Consistency models (the shades between)

- **Strong consistency:** a read always reflects the latest write. Simple to reason
  about, but slower and less available. Needed for money, inventory, and labels.
- **Eventual consistency:** if writes stop, all replicas *eventually* converge; a
  read may briefly return stale data. Cheaper, faster, more available — and
  perfectly fine for most ML serving (a feature that is 2 seconds stale rarely
  matters).

### Replication, partitioning & sharding

- **Replication** = keep multiple **copies** of the same data on different nodes.
  Buys durability (survive a node death) and read scaling (read from any replica).
  Introduces the consistency question above (which copy is authoritative?).
- **Partitioning / sharding** = **split** data across nodes so no single machine
  holds it all — each shard owns a slice (e.g. users A–M on shard 1, N–Z on shard
  2). Buys write scaling and lets datasets exceed one machine.
- **Real systems do both:** shard for size, replicate each shard for safety.
- **Watch for hot shards:** a bad shard key (e.g. sharding by country when one
  country is 80% of traffic) overloads one node. Choose a high-cardinality,
  evenly-distributed key.

> **ML angle.** A large embedding index or feature store is **sharded** (too big
> for one box) and each shard is **replicated** (for QPS and failure tolerance).
> Most ML serving data tolerates **eventual consistency**, which is exactly why
> ML platforms lean on fast **AP** stores.

---

## 19.6 Microservices & APIs (REST vs gRPC, service mesh)

### Motivation

You could build the whole ML product as one giant program (a **monolith**). It is
simple at first, but soon the feature pipeline, the model server, and the business
logic all scale, deploy, and fail together — a change to one forces redeploying
all. **Microservices** split the system into small, independently deployable
services that talk over the network. Now the model server can scale on GPUs while
the API layer scales on cheap CPUs.

But once services talk over the network, *how* they talk matters a lot for
latency and throughput — this is where REST vs gRPC comes in.

![Side-by-side of REST (HTTP/1.1, JSON text payloads, human-readable) versus gRPC (HTTP/2, binary Protobuf, multiplexed streaming) with gRPC highlighted as the lower-latency, higher-throughput choice for internal model-serving calls.](images/m19_06_rest_vs_grpc.png)

### REST vs gRPC

- **REST** (over HTTP/1.1, usually **JSON**). Text-based, human-readable, works in
  every browser and language, easy to debug with `curl`. But JSON is verbose to
  send and slow to parse, and HTTP/1.1 handles one request per connection at a time.
- **gRPC** (over HTTP/2, using **Protobuf** binary). Compact binary payloads, a
  typed schema (`.proto`) generating client/server code, multiplexed streams over
  one connection, and built-in streaming. Faster and lighter, but not
  browser-native and harder to eyeball.

| | **REST + JSON** | **gRPC + Protobuf** |
|--|-----------------|---------------------|
| Payload | Text (verbose) | Binary (compact) |
| Transport | HTTP/1.1 | HTTP/2 (multiplexed) |
| Schema/contract | Loose (OpenAPI optional) | Strong, generated from `.proto` |
| Streaming | Awkward | First-class (bi-directional) |
| Human-debuggable | Yes (`curl`) | No (binary) |
| Best for | Public/browser APIs | Internal service-to-service, ML serving |

### Why gRPC for ML serving

1. **Latency & throughput.** Model serving is chatty, internal, high-QPS traffic
   where every millisecond counts. Binary Protobuf + HTTP/2 multiplexing cut
   serialization cost and connection overhead vs JSON/HTTP1 — often a large win.
2. **Tensors are numeric.** ML payloads are big numeric arrays; encoding them as
   JSON text is wasteful, while Protobuf packs them compactly.
3. **Streaming.** gRPC streams suit token-by-token LLM output and continuous
   feature pushes.
4. **Typed contracts** catch shape mismatches (a classic serving bug) at compile
   time. This is why **TensorFlow Serving** and **NVIDIA Triton** expose gRPC.

> **Balanced answer.** Expose a **REST** endpoint at the public edge (browser- and
> partner-friendly), and use **gRPC** for internal service-to-service and
> model-serving hops. Best of both.

### Service mesh

As services multiply, every one needs retries, timeouts, TLS, load balancing, and
metrics. A **service mesh** (e.g. Istio, Linkerd) pushes this into a **sidecar
proxy** next to each service, so the network concerns are handled uniformly by
infrastructure instead of being re-coded in every service. It gives you
observability, traffic shifting (canary), and mTLS "for free" — very useful when
rolling out a new model version to 5% of traffic.

---

## 19.7 Reliability (SLA / SLO / SLI, redundancy, degradation, retries)

### Motivation

At scale, **failure is normal, not exceptional.** With thousands of machines,
something is always broken. Reliability engineering is about making the *system*
stay up and correct even though its *parts* fail. And you must measure it, because
"is it reliable?" is meaningless without a number.

![Reliability layers: SLI measurements feeding an SLO target and an SLA contract at the top, with redundancy, graceful degradation, and the retry/timeout/circuit-breaker request-protection pattern shown as the mechanisms underneath.](images/m19_07_reliability.png)

### SLI, SLO, SLA (measure, target, promise)

- **SLI — Service Level Indicator:** the *measured* number. E.g. "99.95% of
  requests succeeded in the last 30 days," or "p99 latency = 80 ms." It is a fact.
- **SLO — Service Level Objective:** the internal *target* for an SLI. E.g.
  "p99 latency < 100 ms" or "availability ≥ 99.9%." It is a goal you engineer to.
- **SLA — Service Level Agreement:** the *contractual promise* to customers, with
  penalties if broken. E.g. "99.9% uptime or you get a refund." The SLA is looser
  than the SLO on purpose, so you have a safety margin.

Memory hook: **SLI = Indicator (measured), SLO = Objective (target), SLA =
Agreement (promise with teeth).** The "nines": 99.9% ≈ 8.7 h downtime/year;
99.99% ≈ 52 min/year; 99.999% ≈ 5 min/year. Each extra nine costs a lot more.

> **ML-specific SLOs.** Serving has classic SLOs (latency, availability) **plus**
> ML-quality ones: prediction latency p99, model freshness ("features < 5 min
> old"), and even an accuracy/AUC floor monitored in production (Module 10).

### Mechanisms that buy reliability

- **Redundancy.** Run N+1 (or more) copies across different machines, racks, and
  **availability zones**, so one death does not take the service down. No single
  point of failure — including the LB and the database (use replicas).
- **Graceful degradation.** When a dependency fails, return a *worse but useful*
  answer instead of an error. If the personalized model times out, serve
  **popular items** (a cheap fallback). A degraded answer beats a blank page.

### Retries, timeouts & circuit breakers (protecting a request)

- **Timeout.** Never wait forever. Cap how long you wait for a downstream (e.g.
  50 ms); past that, fail fast or fall back. Without timeouts, one slow dependency
  freezes threads and cascades into a full outage.
- **Retry (with backoff + jitter).** A transient blip? Try again — but with
  **exponential backoff** and random **jitter** so you don't stampede the struggling
  service. Cap the number of retries.
- **Circuit breaker.** If a downstream keeps failing, **stop calling it** for a
  while (the breaker "opens"), immediately serving a fallback. This lets the sick
  service recover instead of being hammered, and it stops failures cascading. After
  a cooldown the breaker "half-opens" to test if it recovered.

> **Interview trap.** Naive retries make outages *worse*: a struggling service gets
> retried by everyone at once (a **retry storm**). Always pair retries with backoff,
> jitter, a retry cap, and a circuit breaker. Saying this unprompted is a senior
> signal.

---

## 19.8 The Latency Ladder (numbers every engineer should know)

### Motivation

Every design decision — cache or not, one datacenter or many, in-memory or on
disk — comes down to *how long things take*. If you carry rough numbers in your
head, you can reason about latency budgets on the spot. If you don't, you'll
propose designs that cannot possibly meet a 100 ms budget. These are Jeff Dean's
famous **"numbers every engineer should know."**

![A latency ladder rising by orders of magnitude — from nanosecond L1/L2 cache and RAM reads, to microsecond SSD reads, to millisecond disk seeks and same-region network round trips, up to hundred-plus-millisecond cross-continent round trips — each rung annotated with its approximate time.](images/m19_08_latency_ladder.png)

### The ladder (approximate, order-of-magnitude)

| Operation | Approx time | In "human" scale (×1e9) |
|-----------|-------------|-------------------------|
| L1 cache reference | ~1 ns | 1 second |
| Branch mispredict | ~3 ns | 3 s |
| L2 cache reference | ~4 ns | 4 s |
| Mutex lock/unlock | ~17 ns | 17 s |
| Main memory (RAM) reference | ~100 ns | ~1.5 min |
| Compress 1 KB | ~2 µs | ~33 min |
| Read 1 MB sequentially from RAM | ~10 µs | ~2.8 h |
| SSD random read | ~16 µs | ~4.4 h |
| Read 1 MB from SSD | ~200 µs | ~2.3 days |
| Round trip within same datacenter | ~500 µs | ~5.8 days |
| Read 1 MB from disk (HDD) | ~1–2 ms | ~11–23 days |
| Disk seek | ~2–10 ms | weeks |
| Round trip California ↔ Netherlands | ~150 ms | ~4.7 years |

### The lessons that actually matter

1. **RAM is ~100× faster than SSD, and SSD is ~100× faster than a disk seek, and
   the network is slower still.** This is *why* caches exist (19.2) and why the
   online feature store keeps hot features in RAM.
2. **Memory (ns) ≪ SSD (µs) ≪ disk seek (ms) ≪ cross-region (100+ ms).** Each
   step is roughly 1000× — spanning nanoseconds to hundreds of milliseconds.
3. **Cross-region round trips (~150 ms) can *alone* blow a 100 ms budget.** So keep
   the serving path within one region; replicate data close to users; never make a
   synchronous cross-continent call on the hot path.
4. **A same-datacenter round trip (~0.5 ms) is cheap; a chain of 30 of them is not.**
   Every microservice hop adds up — this is why you batch calls and prefer gRPC.

> **How to use it in an interview.** When asked "can this meet 50 ms p99?", add up
> the hops: LB → feature fetch (cache 0.5 ms or DB few ms) → model inference (say
> 20 ms) → response. If the sum blows the budget, that's your cue to cache,
> co-locate, or shrink the model.

---

## 19.9 Back-of-the-Envelope Capacity Estimation

### Motivation

Interviewers *always* ask "how many servers? how much storage? how much
bandwidth?" They don't want a precise number — they want to see you reason with
round numbers and sensible assumptions. This skill also protects you from
proposing a design that needs 10,000 machines when 10 will do (or vice versa).

![A worked back-of-the-envelope estimation panel: from daily active users and requests-per-user to average QPS and peak QPS, then storage per record times record count to total storage, and QPS times payload size to bandwidth — the reusable estimation pipeline.](images/m19_09_estimation.png)

### The reusable recipe

1. **State assumptions out loud** (DAU, requests/user/day, payload size, retention).
   Round aggressively.
2. **QPS.** `average QPS = total daily requests / 86,400 s`. Then `peak QPS ≈
   average × (2 to 10)` to cover bursty traffic.
3. **Storage.** `bytes/record × records/day × retention days`. Add replication
   factor (×3 is common).
4. **Bandwidth.** `QPS × payload size` for both in and out.
5. **Servers.** `peak QPS / per-server capacity`, then add headroom (×1.5–2) and
   replicas for redundancy.

Handy round numbers: **1 day ≈ 86,400 s ≈ 10^5 s**; **1 million QPS-seconds/day**
etc. Use powers of ten and don't sweat the last digit.

### Worked sizing #1 — an online recommendation service

**Assumptions:** 100 M DAU; each user triggers 20 recommendation requests/day;
each response is ~10 KB; we keep 90 days of prediction logs; replication ×3.

- **Requests/day** = 100 M × 20 = **2 × 10^9 req/day**.
- **Average QPS** = 2 × 10^9 / 86,400 ≈ **23,000 QPS**.
- **Peak QPS** ≈ 23k × 5 ≈ **115,000 QPS**. Design for ~120k.
- **Egress bandwidth (peak)** = 115k × 10 KB ≈ **1.15 GB/s** (~9.2 Gbps). You need
  multiple 10 GbE-class links / a CDN-like fanout.
- **Log storage** = 2 × 10^9 req/day × (say) 1 KB/log × 90 days × 3 replicas
  ≈ 2 × 10^9 × 10^3 × 90 × 3 ≈ **~540 TB**. Plan a data lake, not one disk.
- **Servers.** If one server does ~2,000 inferences/s, need 120k / 2k = **60
  servers**; add headroom + redundancy → ~**90–120 servers** across zones.

### Worked sizing #2 — storing user embeddings

**Assumptions:** 500 M users; each has a 256-dimensional `float32` embedding.

- **Bytes/embedding** = 256 × 4 = **1,024 bytes ≈ 1 KB**.
- **Total** = 500 M × 1 KB = **500 GB** for one copy.
- **With ×3 replication** ≈ **1.5 TB**. This won't fit one machine comfortably as a
  low-latency index → **shard** it across, say, 10 nodes (~150 GB each) and
  **replicate** each shard. Now the vector-DB / sharding discussion from 19.3 and
  19.5 is grounded in a real number.

### Reusable cheat sheet

```
SECONDS/DAY   ≈ 86,400  ≈ 1e5           WEEK ≈ 6e5 s     MONTH ≈ 2.5e6 s
AVG QPS       = requests_per_day / 86,400
PEAK QPS      = AVG QPS × (2 … 10)      (bursty)
STORAGE       = bytes/record × records × retention × replication(×3)
BANDWIDTH     = QPS × payload_bytes     (do ingress AND egress)
SERVERS       = PEAK_QPS / per_server_qps , then × headroom(1.5–2) + replicas
SIZES:  float32 = 4 B   |   char ≈ 1 B   |   1 KB row/log is a fine default
        1 K=1e3  1 M=1e6  1 B=1e9  1 T=1e12
EMBEDDING BYTES = dim × 4 (float32)     e.g. 256-d = 1 KB
```

> **Golden rule.** State assumptions, use powers of ten, compute average → peak →
> storage → bandwidth → servers, then sanity-check against the latency ladder
> (19.8). Being *organized* matters more than being *exact*.

---

## Module 19 — Interview Mapping (what companies probe)

| Company | How Module 19 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | "Serve this model at 100k QPS under 100 ms" | "Add servers" | Sizes QPS, adds LB + cache + gRPC, budgets the latency ladder, co-locates by region |
| **Amazon** | Reliability, cost, operational excellence | Ignores failure | Designs redundancy, timeouts, circuit breakers, graceful degradation, SLOs |
| **Uber / Stripe** | Streaming features, exactly-once, fraud latency | "Use Kafka" | Explains partitions, consumer groups, idempotency, Flink vs Spark trade-off |
| **OpenAI / Anthropic** | Low-latency LLM serving, streaming tokens | REST + JSON | gRPC streaming, batching, KV-cache, region locality |

**The recurring demand:** *connect the systems choice to the number.* "We use a
Redis feature cache (0.5 ms) instead of the DB (5 ms) so the p99 fits our 50 ms
budget at 100k QPS, which needs ~50 servers plus headroom across two zones." That
sentence — mechanism + latency + capacity — is the staff bar.

---

## Module 19 — Exam Mapping (SEBI / RBI / GATE / ISRO)

> **HIGH exam value.** This is the most exam-relevant module in the course.

- **GATE CS/DA:** CAP theorem, ACID vs BASE, consistency models, SQL vs NoSQL,
  indexing, and sharding are recurring topics. Caching (LRU/LFU) and hashing are
  classic OS/DBMS questions. Know the definitions cold.
- **SEBI IT / RBI IT:** database types, ACID, load balancing, high availability,
  and networking basics (latency, bandwidth) appear in the IT/CS sections. The
  "nines" of availability and RTO/RPO-style reliability concepts show up too.
- **ISRO / DRDO / UGC-NET:** distributed systems fundamentals, CAP, and DB models
  are standard.

Focus for exams: **CAP (pick 2), strong vs eventual consistency, SQL vs NoSQL,
LRU vs LFU, replication vs sharding, SLA/SLO/SLI definitions.**

---

## Module 19 — Common Mistakes & Misconceptions

1. **"CAP means pick any 2 freely."** No — partitions are unavoidable, so you
   really choose **C or A during a partition**. P is not optional in a distributed
   system.
2. **"A cache always helps."** Only for high read/compute cost + high reuse +
   tolerance for slight staleness. For write-heavy, must-be-fresh, low-reuse data
   it adds complexity and bugs.
3. **"Retries make things more reliable."** Naive retries cause **retry storms**
   that deepen outages. Always add backoff, jitter, a cap, and a circuit breaker.
4. **"gRPC is just faster REST."** It's binary + HTTP/2 + typed contracts +
   streaming. Use REST at the public edge, gRPC internally.
5. **"Kafka is a queue that deletes on read."** It's a durable, replayable **log** —
   that replay property is exactly why ML uses it.
6. **"L4 and L7 are the same."** L4 routes by IP/port (fast, blind); L7 reads the
   request (smart, enables canary/A-B routing).
7. **"Eventual consistency = broken."** It's a deliberate, correct trade for
   availability and speed, and it's fine for most ML features.
8. **"Just add servers."** Without sizing QPS, latency budget, and the bottleneck,
   this is hand-waving. Do the back-of-the-envelope.

---

## Module 19 — MCQs (with answers & explanations)

**Q1.** During a network partition, a **CP** system will:
a) keep answering with possibly-stale data
b) refuse/serve errors rather than return inconsistent data
c) never experience partitions
d) automatically switch to AP

<details><summary>Answer</summary>**b.** CP keeps *consistency* and *partition
tolerance*, sacrificing availability during the partition — it refuses rather than
serve stale/inconsistent data.</details>

**Q2.** Which cache eviction policy removes the entry that has not been *accessed*
for the longest time?
a) LFU  b) FIFO  c) LRU  d) TTL

<details><summary>Answer</summary>**c.** LRU (Least Recently Used) evicts the
least-recently-touched item. LFU evicts the least-*frequently* used.</details>

**Q3.** Why is **gRPC** often preferred over REST/JSON for internal model serving?
a) It is browser-native
b) Binary Protobuf + HTTP/2 multiplexing give lower latency/overhead, with typed
   contracts and streaming
c) It cannot be debugged, which is good
d) JSON cannot represent numbers

<details><summary>Answer</summary>**b.** Compact binary payloads, multiplexed
HTTP/2, generated typed contracts, and first-class streaming make gRPC faster and
safer for high-QPS numeric ML traffic.</details>

**Q4.** In Kafka, ordering is guaranteed:
a) across the whole topic  b) within a single partition  c) never  d) only with one
consumer

<details><summary>Answer</summary>**b.** Order holds *within a partition*. Choose a
partition key so events that must stay ordered land in the same partition.</details>

**Q5.** Approximately how long is a round trip between California and Europe?
a) ~0.5 ms  b) ~15 µs  c) ~150 ms  d) ~2 s

<details><summary>Answer</summary>**c.** ~150 ms — large enough to blow a 100 ms
budget by itself, which is why you keep the serving path within one region.</details>

**Q6.** Which correctly orders SLI, SLO, SLA?
a) Agreement, Objective, Indicator
b) Indicator (measured) → Objective (target) → Agreement (contract)
c) They are synonyms
d) SLA is stricter than the SLO

<details><summary>Answer</summary>**b.** SLI is the measured number, SLO is the
internal target, SLA is the customer contract (deliberately looser than the SLO for
safety margin).</details>

**Q7.** You must store 500 M users × a 256-dim float32 embedding (one copy). Roughly
how much?
a) ~5 GB  b) ~500 GB  c) ~50 TB  d) ~5 PB

<details><summary>Answer</summary>**b.** 256×4 B = 1 KB/embedding; ×500 M ≈ 500 GB
(×3 replication ≈ 1.5 TB), so you must shard + replicate.</details>

**Q8.** A hot cache key expires and thousands of requests all miss and hit the DB at
once. This is a:
a) circuit breaker  b) cache stampede / thundering herd  c) partition  d) retry
budget

<details><summary>Answer</summary>**b.** A cache stampede. Fix with TTL jitter or a
refill lock so only one request repopulates the key.</details>

---

## Module 19 — Design Exercises (easy → hard)

- **Easy.** For each, name the best storage: (1) user account + orders; (2)
  find-similar-images by embedding; (3) online features read at serving time; (4)
  p99 latency over the last hour. *(SQL; vector DB; key-value; time-series.)*
- **Easy.** Give one case where a cache *hurts* and explain why.
- **Medium.** Design the routing for a model-serving fleet where each server caches
  per-user state. Which LB algorithm and why? What breaks if one user is 50% of
  traffic?
- **Medium.** A downstream feature service starts timing out under load and your
  service falls over with it. Add timeouts, retries (with backoff+jitter), a
  circuit breaker, and a graceful-degradation fallback. Describe each.
- **Hard.** Size an online fraud-scoring service: 50 M transactions/day, must score
  within 50 ms, keep 1 year of scored logs (~2 KB each), ×3 replication. Compute
  avg/peak QPS, storage, bandwidth, and rough server count. Which parts must be
  strong-consistent vs eventual?
- **Hard.** You must serve a recommender at 200k peak QPS under 80 ms p99 across two
  continents. Lay out LB (L4/L7), cache, feature store, model servers, DB
  (SQL/NoSQL/vector), Kafka for events, and region strategy. Justify each with a
  latency-ladder number.

---

## Module 19 — Concept Review (one page)

- **Load balancing** spreads traffic over a fleet + routes around dead nodes.
  **L4** = fast, IP/port-blind; **L7** = smart, reads the request (enables
  canary/A-B). Algorithms: round robin, least-connections, consistent hashing.
- **Caching** stores expensive/repeated results in RAM (Redis/Memcached). Patterns:
  **cache-aside**, write-through, write-back. Eviction: **LRU / LFU / TTL**. Cache
  the expensive + reusable + slow-changing; beware stampedes and invalidation.
- **Databases:** **SQL** (structured, ACID, joins) · **NoSQL** (scale-out,
  flexible) · **key-value** (µs lookups, feature store) · **vector** (ANN over
  embeddings) · **time-series** (metrics/monitoring). Real ML uses several.
- **Kafka** = durable, replayable **log**; **partitions** = parallelism + ordering
  unit; **consumer groups** share work; **offsets** track position. **Flink** =
  event-at-a-time; **Spark Streaming** = micro-batch.
- **CAP:** during a partition, choose **C or A**. **Strong** vs **eventual**
  consistency. **Replication** = copies (durability/reads); **sharding** = split
  (scale/size). ML serving usually tolerates eventual (AP).
- **REST vs gRPC:** REST/JSON at the edge; **gRPC/Protobuf/HTTP2** internally for
  low-latency ML serving + streaming + typed contracts. **Service mesh** handles
  retries/TLS/observability in sidecars.
- **Reliability:** **SLI** (measured) → **SLO** (target) → **SLA** (contract).
  Redundancy, graceful degradation, timeouts, backoff+jitter retries, circuit
  breakers.
- **Latency ladder:** RAM ≪ SSD ≪ disk seek ≪ cross-region (~150 ms). Cache, keep
  in RAM, co-locate by region.
- **Estimation:** assumptions → avg QPS → peak QPS → storage → bandwidth → servers,
  in powers of ten.

---

## Module 19 — Flash Cards (Q → A)

1. L4 vs L7? → *L4 routes by IP/port (fast, blind); L7 reads the request (smart,
   enables canary/A-B).*
2. Cache-aside in one line? → *App checks cache; miss → read DB, fill cache w/ TTL,
   return.*
3. LRU vs LFU? → *LRU evicts least-recently-used; LFU evicts least-frequently-used.*
4. Which DB for embeddings similarity? → *Vector DB (ANN).*
5. Kafka ordering guarantee? → *Only within a partition.*
6. Consumer group rule? → *Each partition is read by exactly one consumer in the
   group.*
7. CAP real choice? → *During a partition, pick C or A (P is unavoidable).*
8. Replication vs sharding? → *Replication = copies (safety/reads); sharding =
   split (scale/size).*
9. Why gRPC for ML serving? → *Binary Protobuf + HTTP/2 + typed contracts +
   streaming = low latency at high QPS.*
10. SLI/SLO/SLA? → *Measured / target / contract.*
11. Circuit breaker? → *Stop calling a failing dependency for a while; serve
    fallback so it recovers.*
12. Cross-region round trip? → *~150 ms — can blow a 100 ms budget alone.*
13. Peak QPS rule of thumb? → *avg QPS × 2–10.*
14. float32 embedding of dim d bytes? → *d × 4 bytes.*

---

## Module 19 — Pattern Recognition (how to spot it in an interview)

- Hear **"serve at N QPS under X ms"** → do the sizing, then add LB + cache + gRPC +
  region locality; budget with the latency ladder.
- Hear **"must survive a machine/zone failure"** → redundancy (N+1), replicas, no
  single point of failure, graceful degradation.
- Hear **"find similar / retrieve candidates"** → vector DB + ANN.
- Hear **"react to events as they happen"** → Kafka + Flink; mind partitions and
  idempotency.
- Hear **"can we tolerate stale data?"** → CAP + eventual consistency; usually yes
  for ML features → pick an AP store.
- Hear **"a downstream is flaky/slow"** → timeouts + backoff/jitter retries +
  circuit breaker + fallback.
- Hear **"how many servers / how much storage?"** → back-of-the-envelope with
  powers of ten; state assumptions.
- Hear **"roll out the new model safely"** → L7/service-mesh canary to 5%, monitor
  SLOs, kill switch.

---

## Module 19 — Revision Notes / Mini Cheat Sheet

```
LOAD BALANCING:  L4 = IP/port (fast) | L7 = reads request (canary/A-B)
   algos: round-robin | least-conn | consistent-hash (affinity) | 2-choices
CACHE (Redis/Memcached):  cache-aside | write-through | write-back
   evict: LRU | LFU | TTL   | cache = expensive+reused+slow-changing
   watch: stampede (jitter/lock), invalidation (version the keys)
DATABASES:  SQL(ACID,joins) | NoSQL(scale-out) | KV(µs,feature-store)
            VECTOR(ANN embeddings) | TIME-SERIES(metrics)
KAFKA:  durable REPLAYABLE log | partition=parallelism+order | offset | group
        Flink=event-at-a-time | Spark=micro-batch
CAP:  partition unavoidable -> pick C or A | strong vs eventual
      replicate=copies(safety/reads) | shard=split(scale/size) | ML~AP/eventual
API:  REST/JSON @edge | gRPC/Protobuf/HTTP2 internal (fast, typed, streaming)
      service mesh = sidecar retries/TLS/observability/canary
RELIABILITY:  SLI(measured)->SLO(target)->SLA(contract)
   redundancy N+1 | graceful-degrade | TIMEOUT | RETRY(backoff+jitter+cap) | BREAKER
LATENCY LADDER:  L1~1ns | RAM~100ns | SSD~16µs | same-DC RT~0.5ms
                 disk seek~ms | cross-region RT~150ms   (RAM<<SSD<<disk<<net)
ESTIMATION:  day=86,400s(~1e5) | avgQPS=req/day/86400 | peakQPS=avg×(2..10)
   storage=bytes×records×retention×3 | bw=QPS×payload | servers=peakQPS/cap×headroom
   float32=4B | emb bytes=dim×4 | 1K=1e3 1M=1e6 1B=1e9
```

---

> **Next module:** *Module 20 — ML Serving & Inference Systems in Depth.* We take
> these foundations and build the real serving stack: model servers (TF-Serving,
> Triton, TorchServe), dynamic batching, GPU utilization, model/version routing,
> autoscaling, and the end-to-end latency budget of a production prediction — all
> on top of the load balancers, caches, gRPC, and reliability patterns you just
> learned.
