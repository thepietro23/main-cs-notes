---
title: "Module 8 — Congestion Control & Quality of Service"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8 — Congestion Control & Quality of Service

> **Where this module sits.**
> Module 7 showed **flow control** — not overwhelming the *receiver* (`rwnd`). But the
> *network itself* can be the bottleneck: too many senders → routers' queues overflow →
> packets dropped → **congestion collapse**. **Congestion control** (the `cwnd` half of
> TCP) keeps the whole network stable, and **QoS** mechanisms give important traffic
> priority. The **TCP congestion "sawtooth"** (slow start + AIMD) and **leaky/token
> bucket** are classic, high-frequency exam topics.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★★   | ★★★★      | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **flow vs congestion
control**; **slow start / congestion avoidance (AIMD)**; **cwnd / ssthresh**; **fast
retransmit & fast recovery** (3 dup ACKs); **timeout vs 3-dup-ACK** reactions; TCP
**Tahoe vs Reno**; **leaky bucket vs token bucket**; congestion collapse; AQM/RED, ECN.

---

## 8.1 Flow Control vs Congestion Control (don't confuse them)

| | Flow control (M7) | Congestion control (this module) |
|---|---|---|
| Protects | the **receiver** | the **network** (routers/links) |
| Window | **rwnd** (advertised by receiver) | **cwnd** (computed by sender) |
| Signal | receiver's buffer space | packet **loss** / delay |
| Sender limit | in-flight ≤ **min(rwnd, cwnd)** | (same) |

**Congestion** happens when the offered load exceeds capacity: router queues fill,
delay rises, and drops occur. Uncontrolled, this spirals into **congestion collapse**
(everyone retransmits, making it worse).

> **Memory hook:** **flow control = "don't flood the listener"; congestion control =
> "don't flood the road."** TCP obeys the stricter of the two windows.

### MCQs

1. cwnd protects? → the **network**. rwnd protects? → the **receiver**.
2. Sender's in-flight limit? → **min(rwnd, cwnd)**.
3. Everyone retransmitting into an overloaded net = ? → **congestion collapse**.

---

## 8.2 TCP Congestion Control — Slow Start & AIMD (the sawtooth)

TCP has no direct view of the network, so it **treats packet loss as a congestion
signal** and adjusts **cwnd** in phases:

![TCP congestion window: slow start grows exponentially to ssthresh, then AIMD grows linearly; a 3-dup-ACK loss halves cwnd (fast recovery) while a timeout resets it to 1.](images/23_tcp_congestion.png)

1. **Slow start:** begin `cwnd = 1 MSS`; **double each RTT** (exponential) until
   `cwnd ≥ ssthresh` (slow-start threshold).
2. **Congestion avoidance (AIMD):** past ssthresh, grow **linearly** — **+1 MSS per
   RTT** (Additive Increase).
3. **On loss:**
   - **3 duplicate ACKs** (mild loss) → **fast retransmit** the missing segment, and
     **halve** cwnd (Multiplicative Decrease) → **fast recovery** (TCP Reno).
   - **Timeout** (severe loss) → set `ssthresh = cwnd/2`, **cwnd = 1**, restart **slow
     start**.

This **AIMD** (Additive Increase, Multiplicative Decrease) produces the characteristic
**sawtooth** and is what makes TCP **fair** and stable across many flows.

> **Memory hook:** **"start slow (but double), then crawl up by 1; on trouble, cut in
> half; on disaster, start over."** Additive up, multiplicative down.

### Tahoe vs Reno (a common exam distinction)

- **TCP Tahoe:** *any* loss (timeout **or** 3 dup ACKs) → cwnd = 1, slow start.
- **TCP Reno:** 3 dup ACKs → **fast recovery** (halve, don't reset); only a **timeout**
  resets to 1. (Reno is the "sawtooth" above; most later variants build on it.)

### MCQs

1. Slow start growth pattern? → **exponential** (double per RTT).
2. Congestion avoidance growth? → **linear** (+1 MSS/RTT) = **AIMD**.
3. Reaction to 3 dup ACKs (Reno)? → **fast retransmit + halve cwnd** (fast recovery).
4. Reaction to a **timeout**? → **cwnd = 1**, slow start (ssthresh = cwnd/2).
5. Tahoe vs Reno on 3 dup ACKs? → Tahoe **resets to 1**; Reno **halves** (fast
   recovery).

---

## 8.3 Congestion Detection at Routers (AQM, ECN)

Routers can help *before* buffers overflow:

- **Tail drop:** the default — drop arriving packets once the queue is full (can cause
  synchronized global backoff).
- **RED (Random Early Detection):** an **AQM** (Active Queue Management) that **drops/
  marks packets randomly as the queue grows**, signalling congestion early and avoiding
  synchronization.
- **ECN (Explicit Congestion Notification):** routers **mark** a bit instead of dropping;
  the receiver echoes it so the sender slows down **without a loss** — congestion
  signalling without dropping packets.

### MCQs

1. Dropping packets only when the queue is full is? → **tail drop**.
2. AQM that drops early & randomly? → **RED**.
3. Signalling congestion by marking (not dropping)? → **ECN**.

---

## 8.4 Quality of Service (QoS) & Traffic Shaping

**QoS** gives certain traffic (voice, video) better treatment (bandwidth, low delay/
jitter, low loss). Core tools:

**Traffic shaping** regulates the *rate* a source sends:

![Leaky bucket emits at a constant rate and drops overflow; token bucket permits bursts up to the bucket size while enforcing an average rate.](images/24_traffic_shaping.png)

- **Leaky bucket:** output is a **constant rate** regardless of bursty input; overflow
  is dropped. Smooths traffic but is inflexible (no bursts).
- **Token bucket:** tokens accumulate at rate **r** (up to bucket size **b**); a packet
  needs a token to be sent. **Allows bursts** (up to `b`) while limiting the **average**
  rate to `r`. More flexible than leaky bucket. Max burst ≈ `b`; long-term rate ≈ `r`.

**Scheduling** at routers: **FIFO**, **priority queuing**, **Weighted Fair Queuing
(WFQ)** to divide bandwidth fairly among flows/classes.

**QoS models:** **IntServ** (per-flow reservations via RSVP — doesn't scale) vs
**DiffServ** (mark packets into classes via the DSCP field — scalable, widely used).

> **Memory hook:** **leaky bucket = strict metronome (constant out); token bucket =
> saved-up allowance (burst then refill).**

### MCQs

1. Constant-output shaper? → **leaky bucket**.
2. Shaper allowing bursts up to bucket size? → **token bucket** (avg rate r).
3. Scalable QoS model marking classes? → **DiffServ (DSCP)**.
4. Fair per-flow scheduling? → **WFQ**.

---

## 8.5 Real-World & Backend Perspectives

- **Modern TCP variants** — **CUBIC** (Linux default, better for high-bandwidth links)
  and **BBR** (Google; models bandwidth + RTT instead of reacting to loss) — evolve the
  AIMD idea; interviews love "why BBR?".
- **Bufferbloat:** oversized router buffers hide loss and inflate latency; **AQM
  (CoDel/RED)** and ECN fight it — a real backend/latency issue.
- **QoS in practice:** VoIP/video conferencing rely on DiffServ marking + WFQ; cloud
  load balancers and rate limiters use **token buckets** (the same algorithm as API
  rate limiting).

---

## 8.6 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** confusing **flow** (rwnd, receiver) and **congestion** (cwnd, network)
  control — both cap the sender, but for different reasons.
- **Mistake:** thinking slow start is "slow" — it's **exponential** (fast); it just
  *starts* small.
- **Trap:** **timeout ⇒ cwnd = 1** (slow start); **3 dup ACKs ⇒ halve** (fast recovery,
  Reno). Different severities, different reactions.
- **Edge case:** loss-based TCP misreads **wireless loss** (not congestion) as
  congestion, needlessly slowing down — a reason for BBR.

---

## 8.7 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** flow vs congestion control, slow start/AIMD idea, leaky vs
  token bucket, what QoS means.
- **GATE / C-DAC:** trace **cwnd** over RTTs (slow start → AIMD → loss), compute cwnd
  after events, Tahoe vs Reno, token-bucket burst/rate math.
- **Interview:** "how does TCP handle congestion?" → slow start + AIMD + fast
  recovery; "leaky vs token bucket?"; "why BBR/CUBIC?".

---

## 8.8 Concept Checks & MCQs (test yourself)

1. Flow vs congestion window? → **rwnd (receiver)** vs **cwnd (network)**.
2. Slow start vs congestion avoidance growth? → **exponential** vs **linear (AIMD)**.
3. cwnd after a **timeout**? → **1 MSS**, slow start (ssthresh = cwnd/2).
4. cwnd after **3 dup ACKs** (Reno)? → **halved** (fast recovery).
5. AIMD stands for? → **Additive Increase, Multiplicative Decrease**.
6. Tahoe vs Reno? → Tahoe resets to 1 on any loss; Reno halves on 3-dup-ACK.
7. Constant-rate shaper vs burst-allowing shaper? → **leaky** vs **token** bucket.
8. Router marking instead of dropping? → **ECN**.
9. Scalable QoS via packet classes? → **DiffServ**.
10. Congestion collapse means? → throughput crashes as everyone retransmits.

---

## 8.9 One-Page Revision Sheet

```
FLOW CONTROL (M7) = don't overrun RECEIVER (rwnd). CONGESTION CONTROL = don't overrun NETWORK (cwnd).
  sender in-flight <= min(rwnd, cwnd). congestion collapse = overload -> drops -> retransmit spiral.

TCP CONGESTION (cwnd), loss = congestion signal:
  1) SLOW START: cwnd=1, DOUBLE per RTT (exponential) until cwnd >= ssthresh.
  2) CONGESTION AVOIDANCE (AIMD): +1 MSS per RTT (linear).
  3) LOSS:
     - 3 DUP ACKs -> fast retransmit + cwnd/=2 -> FAST RECOVERY (Reno).
     - TIMEOUT -> ssthresh=cwnd/2, cwnd=1, slow start.
  AIMD (additive up, multiplicative down) -> sawtooth, fairness.
  TAHOE: any loss -> cwnd=1. RENO: 3dupACK -> halve; timeout -> 1. (CUBIC/BBR = modern.)

ROUTER AQM: tail drop (queue full) | RED (drop early/random) | ECN (MARK not drop).

QoS: goals = bandwidth, low delay/jitter/loss.
  SHAPING: leaky bucket(constant out, drop overflow) | token bucket(rate r, burst up to b).
  SCHED: FIFO | priority | WFQ.  MODELS: IntServ(RSVP per-flow, not scalable) | DiffServ(DSCP classes, scalable).
```

### Flash cards

| Front | Back |
|-------|------|
| Flow vs congestion window | rwnd (receiver) vs cwnd (network) |
| Slow start growth | exponential (double/RTT) |
| Congestion avoidance | +1 MSS/RTT (AIMD) |
| After timeout | cwnd = 1, slow start |
| After 3 dup ACKs (Reno) | halve cwnd (fast recovery) |
| AIMD | Additive Increase, Multiplicative Decrease |
| Leaky vs token bucket | constant out vs burst up to b |
| ECN | mark (not drop) to signal congestion |
| RED | random early drop (AQM) |
| Scalable QoS model | DiffServ (DSCP) |

### Spaced repetition
- **24-hour:** draw the cwnd sawtooth labelling slow start, AIMD, 3-dup-ACK halving,
  timeout reset.
- **7-day:** flow vs congestion; Tahoe vs Reno; leaky vs token bucket.
- **30-day:** trace cwnd across a sequence of RTTs and loss events; explain token-bucket
  burst vs average rate — without notes.

---

## 8.10 Summary

**Congestion control** protects the **network** (via **cwnd**), complementing flow
control's protection of the **receiver** (**rwnd**) — the sender obeys **min(rwnd,
cwnd)**. TCP treats **loss as congestion** and adjusts cwnd in phases: **slow start**
(exponential to **ssthresh**), **congestion avoidance** (**AIMD**, +1/RTT), and on loss
either **fast recovery** (halve, on 3 dup ACKs — Reno) or **slow start** (cwnd = 1, on
timeout) — the **sawtooth**. Routers assist with **AQM (RED)** and **ECN** (mark, not
drop). **QoS** prioritises important traffic via **traffic shaping** (**leaky bucket** =
constant rate, **token bucket** = bursts up to `b` at average rate `r`), **scheduling**
(WFQ), and models (**DiffServ** scales, IntServ doesn't).

Next, **Module 9 — The Application Layer** reaches Layer 7: **DNS, HTTP/HTTPS, email
(SMTP/IMAP/POP3), FTP, and DHCP** — the protocols you use every day.

> **You have mastered this module when** you can: separate flow from congestion control;
> draw and narrate the cwnd sawtooth (slow start, AIMD, fast recovery, timeout);
> distinguish Tahoe vs Reno; contrast leaky vs token bucket; and explain RED/ECN and
> DiffServ — all without notes.
