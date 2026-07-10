---
title: "Module 13 — The Backend & Distributed-Systems Networking Perspective"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 13 — The Backend & Distributed-Systems Networking Perspective

> **Where this module sits.**
> Everything in Modules 1–12 was "networking theory." This module shows **how it all
> assembles into a real backend system** — the request path, service-to-service
> communication, and the distributed-systems realities (latency, partial failure,
> consistency) that networking forces on us. It's the bridge from CN to **System
> Design**, and it's where interviewers spend most of their time.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★      | ★★     | ★★      | ★★★★★     | ★★★★★   |

**Most-asked concepts:** the request path (DNS → CDN → LB → gateway → services);
**REST vs gRPC/RPC**; **synchronous vs async (message queues)**; **the fallacies of
distributed computing**; **latency numbers**; **idempotency, retries, timeouts,
circuit breakers**; **caching**; **CAP** (from DBMS) applied to networked services.

---

## 13.1 The Anatomy of a Request

![A modern request flows client → CDN → load balancer → API gateway → microservices → DB/cache; every arrow is a network hop secured and balanced along the way.](images/35_backend_path.png)

A typical request path:

1. **DNS** resolves the domain (M9) → IP (often a CDN/LB anycast address).
2. **CDN** (M12) serves static assets from the edge; dynamic requests continue.
3. **Load balancer** (M12) spreads traffic across servers (L4/L7), terminates **TLS**
   (M10).
4. **API gateway** authenticates, rate-limits, and **routes** to the right service.
5. **Microservices** talk to each other (REST/gRPC over TCP) and to **DB/caches**.

Every arrow is a **network hop** — subject to latency, loss, and failure. Good backends
are designed around that fact.

### MCQs

1. First step of almost every request? → **DNS** resolution.
2. Where is TLS usually terminated? → the **load balancer / gateway**.
3. What authenticates & rate-limits at the edge of your services? → the **API gateway**.

---

## 13.2 Service-to-Service Communication

- **REST (HTTP/JSON):** simple, human-readable, ubiquitous; stateless; good for public
  APIs.
- **gRPC (HTTP/2 + Protocol Buffers):** binary, fast, strongly-typed, streaming; great
  for **internal microservice** calls.
- **RPC** in general: make a remote call look like a local function (but it **isn't** —
  it can fail, time out, and be slow).
- **Message queues (async):** Kafka, RabbitMQ, SQS **decouple** producer and consumer —
  the producer doesn't wait; work is buffered and processed later. Enables resilience and
  spikes-handling.

**Synchronous** (request-response, caller waits) vs **asynchronous** (fire-and-forget /
event-driven) is a core design axis.

> **Memory hook:** **REST = readable & universal; gRPC = fast & typed (internal);
> queues = decouple & absorb spikes.** Sync waits; async doesn't.

### MCQs

1. Binary, typed, HTTP/2-based internal RPC? → **gRPC**.
2. What decouples producer from consumer? → a **message queue** (async).
3. REST typically uses which format/protocol? → **JSON over HTTP**.

---

## 13.3 The Fallacies of Distributed Computing (must-know)

Networked systems fail when designers assume the network is perfect. The classic
**8 fallacies** (assume the opposite of each):

1. The network is **reliable**. 2. **Latency** is zero. 3. **Bandwidth** is infinite.
4. The network is **secure**. 5. **Topology** doesn't change. 6. There is **one admin**.
7. **Transport cost** is zero. 8. The network is **homogeneous**.

Reality: packets drop, latency is real and variable, links change, and security is not
free. **Design for partial failure.**

> **Memory hook:** **"the network is NOT reliable, fast, infinite, secure, or free."**
> Every distributed bug traces back to assuming one of these.

### MCQs

1. First fallacy of distributed computing? → "the network is **reliable**."
2. What should you design for? → **partial failure** (assume things fail).

---

## 13.4 Reliability Patterns (how backends survive the network)

- **Timeouts:** never wait forever for a remote call.
- **Retries with backoff + jitter:** retry transient failures, but back off to avoid
  overload (thundering herd).
- **Idempotency:** make a retried operation safe to repeat (idempotency keys) — because
  the network may deliver a request twice.
- **Circuit breaker:** stop calling a failing service to let it recover (fail fast).
- **Bulkheads / rate limiting / load shedding:** contain failures and shed excess load
  (token bucket, M8).
- **Health checks + graceful degradation:** remove sick instances; serve a reduced
  experience rather than none.

> **Memory hook:** **timeout → retry (with backoff+jitter) → but be idempotent → and
> trip a circuit breaker if it keeps failing.**

### MCQs

1. Safe-to-repeat operation property? → **idempotency**.
2. Pattern that stops calling a failing service? → **circuit breaker**.
3. Why add **jitter** to retries? → avoid a synchronized **thundering herd**.

---

## 13.5 Latency Numbers & Caching

Rough **latency ladder** (order-of-magnitude, "numbers every engineer should know"):

```text
L1 cache           ~1 ns   (L2 ~5 ns)
main memory (RAM)  ~100 ns
SSD read           ~100 us (microseconds)
network same DC    ~0.5 ms
disk (HDD) seek    ~10 ms
network cross-continent  ~100+ ms  (speed of light!)
```

Because **remote > local by orders of magnitude**, backends **cache aggressively**:
browser cache → CDN → in-memory cache (Redis/Memcached) → DB. Cache strategies:
**cache-aside**, **write-through**, **write-back**; watch for **invalidation** and
**stampedes**.

> **Memory hook:** **RAM ~100 ns, same-DC network ~0.5 ms, cross-continent ~100 ms.**
> The network is the slow part → cache and keep data close (CDN, M12).

### MCQs

1. Same-datacenter round trip is roughly? → **~0.5 ms** (vs ~100 ns RAM).
2. Cross-continent latency floor is set by? → the **speed of light**.
3. Common in-memory cache? → **Redis / Memcached**.

---

## 13.6 Distributed Data & CAP (networking meets consistency)

The network's unreliability forces trade-offs on distributed data (from DBMS, applied
here):

- **CAP theorem:** during a **network partition (P)**, you must choose **Consistency**
  or **Availability** — you can't have both. **CP** (refuse stale reads) vs **AP** (stay
  up, maybe stale).
- **Consistency models:** strong vs **eventual** consistency (many web systems choose AP
  + eventual for availability).
- **Consensus** (Raft/Paxos) keeps replicas agreeing **despite** message loss/reordering
  — expensive network coordination.

> **Memory hook:** **a partition is a network failure — CAP says pick C or A when it
> happens.** Money → CP; feeds/likes → AP + eventual.

### MCQs

1. During a partition, CAP forces a choice between? → **Consistency** and
   **Availability**.
2. "Stay up, maybe stale" is? → **AP** (availability + eventual consistency).
3. Algorithm to agree despite unreliable messages? → **consensus (Raft/Paxos)**.

---

## 13.7 Real-World & Backend / Interview Perspectives

- This module **is** the systems-design interview: "design a URL shortener / news feed /
  chat" all reduce to **DNS + CDN + LB + gateway + services + cache + queue + DB**, wired
  over an **unreliable network** with **timeouts/retries/idempotency**.
- Know the **latency ladder** and **CAP** cold; be able to justify **sync vs async** and
  **REST vs gRPC**.
- Observability (metrics/tracing/logs) and **p99 latency** are how you run it.

---

## 13.8 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** treating a remote call like a local one (RPC hides the network, but not
  its failures) — **always** set timeouts.
- **Mistake:** retrying **non-idempotent** operations → duplicates (double charge). Add
  idempotency keys.
- **Trap:** you can't have C **and** A during a partition (CAP) — pick per use case.
- **Edge case:** aggressive retries **without backoff** cause a **retry storm** that
  worsens an outage.

---

## 13.9 Concept Checks & MCQs (test yourself)

1. Typical request path? → **DNS → CDN → LB → gateway → services → DB/cache**.
2. gRPC is built on? → **HTTP/2 + Protocol Buffers**.
3. Async decoupling tool? → **message queue** (Kafka/RabbitMQ/SQS).
4. Name three fallacies of distributed computing. → network reliable / latency zero /
   bandwidth infinite (any).
5. Retry safety property? → **idempotency**.
6. Pattern to fail fast on a broken dependency? → **circuit breaker**.
7. RAM vs same-DC network latency? → **~100 ns vs ~0.5 ms**.
8. CAP choice during a partition? → **C or A**.
9. Cache patterns? → **cache-aside, write-through, write-back**.
10. Why jitter in retries? → prevent **thundering herd**.

---

## 13.10 One-Page Revision Sheet

```
REQUEST PATH: DNS -> CDN(edge, static) -> LOAD BALANCER(L4/L7, TLS term) -> API GATEWAY(auth/rate-limit/route)
  -> MICROSERVICES (REST/gRPC over TCP) -> DB / CACHE. every arrow = a network hop.

COMMS: REST(HTTP/JSON, readable, public) | gRPC(HTTP2+protobuf, fast/typed, internal) | RPC(looks local, isn't).
  SYNC(caller waits) vs ASYNC(message queue: Kafka/RabbitMQ/SQS -> decouple, absorb spikes).

8 FALLACIES (assume the OPPOSITE): reliable, zero latency, infinite bw, secure, fixed topology,
  one admin, zero transport cost, homogeneous. => DESIGN FOR PARTIAL FAILURE.

RELIABILITY PATTERNS: timeout -> retry(backoff+JITTER) -> IDEMPOTENCY(safe repeat) -> CIRCUIT BREAKER(fail fast)
  -> bulkhead / rate-limit(token bucket) / load-shed / health checks / graceful degradation.

LATENCY LADDER: RAM ~100ns | SSD ~100us | same-DC net ~0.5ms | HDD seek ~10ms | cross-continent ~100ms(light).
  CACHE: browser -> CDN -> Redis/Memcached -> DB. strategies: cache-aside / write-through / write-back.

CAP: partition(P=network failure) -> choose C (consistent, refuse stale) or A (available, eventual). consensus=Raft/Paxos.
```

### Flash cards

| Front | Back |
|-------|------|
| Request path | DNS → CDN → LB → gateway → services → DB/cache |
| REST vs gRPC | HTTP/JSON readable vs HTTP2/protobuf fast typed |
| Async decoupling | message queue (Kafka/RabbitMQ) |
| 1st fallacy | network is reliable (it isn't) |
| Safe-to-repeat op | idempotency |
| Fail-fast pattern | circuit breaker |
| Same-DC vs cross-continent | ~0.5 ms vs ~100 ms |
| CAP under partition | pick C or A |
| Consensus algorithms | Raft / Paxos |
| Retry jitter reason | avoid thundering herd |

### Spaced repetition
- **24-hour:** draw the request path; list the reliability patterns (timeout→…→circuit
  breaker).
- **7-day:** 8 fallacies; latency ladder; CAP CP vs AP.
- **30-day:** design a scalable service end-to-end citing each networking piece — without
  notes.

---

## 13.11 Summary

A real backend is the **whole CN course assembled**: a request flows **DNS → CDN → load
balancer → API gateway → microservices → DB/cache**, every hop crossing an **unreliable
network**. Services talk via **REST** (readable) or **gRPC** (fast/typed), or decouple
via **async message queues**. Because the **fallacies of distributed computing** are
real, backends design for **partial failure** with **timeouts, retries (backoff +
jitter), idempotency, and circuit breakers**, and fight latency with **caching** (the
latency ladder: RAM ~100 ns vs cross-continent ~100 ms). Finally, the network's
partitions force **CAP** trade-offs (**C or A**) and **consensus** for agreement.

Next, **Module 14 — AI & Data-Center Networking** zooms into the network that trains and
serves modern AI: spine-leaf fabrics, RDMA, GPU interconnects, and all-reduce.

> **You have mastered this module when** you can: trace a request through the backend
> path; choose REST vs gRPC vs a queue; recite the fallacies and the reliability patterns
> that answer them; quote the latency ladder; and apply CAP to a networked service — all
> without notes.
