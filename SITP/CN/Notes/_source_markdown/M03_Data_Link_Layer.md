---
title: "Module 3 — The Data Link Layer (Framing, Error & Flow Control)"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — The Data Link Layer (Framing, Error & Flow Control)

> **Where this module sits.**
> The Physical layer (M2) moves raw bits but makes **no promises** — bits can flip,
> and a fast sender can drown a slow receiver. **Layer 2, the Data Link layer (DLL)**,
> turns that unreliable bit-pipe into a **reliable link between two directly-connected
> nodes**. It groups bits into **frames**, **detects and corrects errors**, and
> **controls the flow** so nobody is overwhelmed. This is one of the **most
> numerical-heavy modules** in the syllabus — CRC, Hamming code, and sliding-window
> **efficiency** calculations appear in almost every GATE/C-DAC paper.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★★   | ★★        | ★★      |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **CRC** computation
(polynomial division); **Hamming code** (number of parity bits, error position);
**framing** (bit stuffing / byte stuffing); **stop-and-wait vs sliding window
efficiency** (`U = 1/(1+2a)`); **Go-Back-N vs Selective Repeat** (window sizes
`2^m−1` vs `2^(m−1)`); **piggybacking**; parity vs checksum vs CRC (detection power).

---

## 3.1 What the Data Link Layer Does (first principles)

The DLL provides **node-to-node** delivery over **one link**. Its jobs:

1. **Framing** — group bits into **frames** with clear start/end.
2. **Physical addressing** — put source/destination **MAC** addresses on the frame
   (details in M4).
3. **Error control** — detect (and sometimes correct) bit errors.
4. **Flow control** — stop a fast sender from overwhelming a slow receiver.
5. **Access control** — decide who may transmit when the medium is shared (M4).

The DLL has two sublayers: **LLC** (Logical Link Control — flow/error control) and
**MAC** (Media Access Control — addressing + who-talks-when, covered in M4).

> **Memory hook:** the DLL is a **careful courier for one leg of the journey** — it
> boxes the goods (framing), labels them (MAC), checks nothing broke (error control),
> and doesn't hand over faster than the receiver can take (flow control).

### MCQs

1. The DLL delivers between? → **two directly-connected nodes** (node-to-node).
2. Two DLL sublayers? → **LLC** and **MAC**.
3. Which layer adds the MAC address? → **Data Link (2)**.

---

## 3.2 Framing — Where Does a Frame Start and End?

The receiver sees a stream of bits; framing marks boundaries. Methods:

- **Character/byte count:** first field says how many bytes follow. Fragile — if the
  count is corrupted, all following frames desync.
- **Byte (character) stuffing:** mark frame with a **FLAG byte**; if the flag appears
  in data, insert an **escape (ESC)** byte before it (and escape the ESC too).
- **Bit stuffing:** frame delimited by the flag `01111110`. In the data, after **five
  consecutive 1s the sender inserts a 0**; the receiver removes it. This guarantees
  the flag never appears inside data.

**Bit-stuffing worked example:** data `0111111 0111110` →
after every five 1s insert a 0 → `011111**0**1 0111110` (sender stuffs a 0 after the
first five 1s). The receiver strips the stuffed 0 to recover the original.

> **Memory hook:** **bit stuffing = "after five 1s, sneak in a 0"** so the real flag
> `01111110` is never faked by the data.

### MCQs

1. Flag pattern in bit stuffing? → `01111110`.
2. Bit-stuffing rule? → after **five consecutive 1s**, insert a **0**.
3. Byte stuffing uses which special byte before a data-flag? → **ESC**.

---

## 3.3 Error Detection — Parity, Checksum, CRC

Noise flips bits. **Detection** adds redundant bits so the receiver can tell
something changed (it can't necessarily fix it).

### Parity

- **Simple (1-D) parity:** add one bit so the total number of 1s is even (even parity).
  Detects **any odd number** of bit errors; **misses even-numbered** errors.
- **2-D parity:** parity per row *and* per column — detects and can locate many errors.

### Checksum

Sum the data words (with end-around carry), send the **complement**; receiver re-adds
everything and expects all-1s. Used by IP/TCP/UDP headers. Weaker than CRC.

### CRC (Cyclic Redundancy Check) — the workhorse

Treats the bit string as a polynomial and divides by a **generator polynomial**
(using XOR / modulo-2 arithmetic). The **remainder (CRC)** is appended. The receiver
divides the whole thing by the same generator — a **non-zero remainder means error.**

```text
CRC worked example
  Data      : 1101011011           Generator G : 10011  (degree 4 -> append 4 zeros)
  Dividend  : 1101011011 0000      (data << 4)

  Modulo-2 (XOR) long division by 10011:
    1101011011 0000  ÷ 10011
    ... performing XOR division ...
    Remainder (CRC) = 1110

  Transmit  : 1101011011 1110      (data + CRC)
  Receiver  : divides received frame by 10011 ->
              remainder 0000 = OK ;  non-zero = ERROR detected.
```

- A CRC with an **r-bit** remainder needs a generator of **degree r** (r+1 bits) and
  appends **r zero bits** to the data before dividing.
- CRC catches all single-bit errors, all odd errors (if G has a factor `x+1`), all
  burst errors **shorter than r**, and most longer ones — far stronger than checksum.

> **Memory hook:** **CRC = binary long division with XOR; remainder 0 at the receiver
> = clean.** Degree of generator = number of CRC bits = zeros you append.

### MCQs

1. Simple parity misses which errors? → an **even number** of bit flips.
2. CRC uses which arithmetic? → **modulo-2 (XOR)** polynomial division.
3. Generator of degree r → how many CRC bits / appended zeros? → **r**.
4. Receiver's remainder is 0 → ? → **no error detected**.

---

## 3.4 Error Correction — Hamming Code

Detection just says "something broke." **Hamming code** can **correct a single-bit
error** by adding parity bits at power-of-two positions.

![Hamming code places parity bits at positions 1,2,4,8...; each parity checks a fixed set of positions, so the failed checks spell out the error's position in binary.](images/08_hamming_code.png)

- **Number of parity bits r** for **m** data bits: choose the smallest r with
  `2^r ≥ m + r + 1`.
- **Placement:** parity bits go at positions **1, 2, 4, 8, …** (powers of 2); data
  fills the rest.
- **Each parity** covers positions whose binary index includes its bit: P1 checks
  1,3,5,7…; P2 checks 2,3,6,7…; P4 checks 4,5,6,7,12….
- **At the receiver:** recompute each parity; the **binary number formed by the failing
  checks is the position of the wrong bit** — flip it to correct.

**Worked example:** for **m = 4** data bits, `2^r ≥ 4 + r + 1` → r = 3 (since
`2³ = 8 ≥ 8`). So **Hamming(7,4)**: 7 total bits, 4 data + 3 parity, corrects any
single-bit error.

> **Memory hook:** parity bits sit at **powers of two**; the **syndrome** (which
> checks fail, read as binary) **points straight at the broken bit**.

### Detection vs correction (a classic distinction)

- To **detect** up to `d` errors, you need Hamming distance `d + 1`.
- To **correct** up to `d` errors, you need Hamming distance `2d + 1`.

### MCQs

1. Parity bits for 4 data bits? → **3** (Hamming(7,4)).
2. Parity-bit positions? → **powers of 2** (1,2,4,8…).
3. Hamming distance to correct `d` errors? → **2d + 1**.
4. The failing-checks binary number gives? → the **error position**.

---

## 3.5 Flow Control & ARQ — Stop-and-Wait

**Flow control** matches sender speed to receiver capacity. **ARQ (Automatic Repeat
reQuest)** adds reliability: lost/corrupt frames are **retransmitted** using ACKs and
timeouts.

![Stop-and-Wait: the sender transmits one frame and then waits for its ACK before sending the next, leaving the link idle for a full round trip.](images/06_stop_and_wait.png)

**Stop-and-Wait ARQ:** send one frame, wait for its ACK, then send the next. Simple,
but the link is **idle** during the round trip → poor efficiency on long/fast links.

**Efficiency** (the key formula). Let `a = Tp / Tt` where **Tt** = transmission time
(frame/bandwidth) and **Tp** = propagation time:

```
Stop-and-Wait efficiency  U = Tt / (Tt + 2·Tp) = 1 / (1 + 2a)
Throughput = U × Bandwidth
```

**Worked example:** bandwidth 1 Mbps, frame 1000 bits, Tp = 10 ms →
`Tt = 1000/10⁶ = 1 ms`, `a = 10/1 = 10` → `U = 1/(1 + 20) = 1/21 ≈ 4.76%`. The long
link is almost idle — motivating sliding windows.

### MCQs

1. Stop-and-Wait efficiency? → **1/(1 + 2a)**, `a = Tp/Tt`.
2. Why is Stop-and-Wait poor on long links? → link **idle** for the whole round trip.
3. `a` is defined as? → **Tp / Tt** (propagation / transmission).

---

## 3.6 Sliding Window — Go-Back-N & Selective Repeat

To keep the pipe full, allow **N unacknowledged frames in flight** (a window).

![Go-Back-N discards out-of-order frames and resends everything from the lost frame; Selective Repeat buffers out-of-order frames and resends only the lost one.](images/07_gbn_vs_sr.png)

### Go-Back-N (GBN)

- Sender may send up to **N** frames without ACK; receiver accepts **only in order**
  and **discards** anything out of order.
- On a loss/timeout, the sender **goes back and resends the lost frame and all after
  it**. Simple receiver (no buffering), but wasteful on lossy links.
- **Sender window ≤ 2^m − 1** (m = sequence-number bits). Receiver window = 1.

### Selective Repeat (SR)

- Receiver **buffers** out-of-order frames and ACKs them individually; sender
  **resends only the specific lost frame**. Efficient but needs buffering + more
  bookkeeping.
- **Sender & receiver window ≤ 2^(m−1)** (must be ≤ half the sequence space to avoid
  ambiguity).

### Efficiency (sliding window)

```
U = N / (1 + 2a)      capped at 1  (when N ≥ 1 + 2a, the pipe is full, U = 100%)
  N = window size,  a = Tp/Tt
Optimal window to fill the pipe:  N = 1 + 2a
```

**Worked example:** with `a = 10` (from §3.5), Stop-and-Wait (N=1) gave 4.76%. To fill
the pipe we need `N = 1 + 2×10 = 21` frames in flight → **U = 100%**. This is why
sliding windows exist.

> **Memory hook:** **GBN = "go back and redo from the mistake"** (simple, wasteful).
> **SR = "just redo the one that broke"** (efficient, needs buffers). Window sizes:
> **GBN 2^m−1, SR 2^(m−1)**.

### MCQs

1. GBN max sender window? → **2^m − 1**. SR window? → **2^(m−1)**.
2. Sliding-window efficiency? → **N/(1 + 2a)** (max 1).
3. Which protocol buffers out-of-order frames? → **Selective Repeat**.
4. Window size N to fully utilise the link? → **N = 1 + 2a**.

---

## 3.7 Piggybacking & Other Essentials

- **Piggybacking:** on a two-way link, attach the ACK for received data **onto an
  outgoing data frame** instead of sending a separate ACK — saves bandwidth (small
  delay while waiting for a data frame to ride on).
- **NAK (negative ACK):** explicitly requests a resend (used by Selective Repeat).
- **Cumulative ACK:** one ACK confirms all frames up to a number (GBN, TCP).

### MCQs

1. Combining an ACK with an outgoing data frame? → **piggybacking**.
2. "ACK N" confirming everything up to N is a? → **cumulative ACK**.

---

## 3.8 Real-World & Backend Perspectives

- **Ethernet frames** (M4) are the DLL in practice: preamble, MAC addresses,
  type/length, payload, and a **CRC-32** trailer (FCS) — exactly the framing + error
  detection here.
- **The sliding window you learn here is the same idea TCP uses** at Layer 4 (M8) — a
  window of unacknowledged data sized to the **bandwidth-delay product** (M2). DLL =
  one link; TCP = end-to-end, but the mechanism rhymes.
- **Wi-Fi** uses link-layer ARQ (retransmit lost frames) because radio is lossy —
  which is why Wi-Fi latency is jittery.

---

## 3.9 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** confusing **detection** (parity/checksum/CRC — "something's wrong") with
  **correction** (Hamming — "fix it"). CRC does **not** correct.
- **Mistake:** SR window = `2^m − 1`. It's **`2^(m−1)`** (half) — over-sizing causes
  sequence-number ambiguity.
- **Trap:** forgetting to **append r zeros** to the data before CRC division.
- **Edge case:** parity misses even-count errors; that's why real links use **CRC**.

---

## 3.10 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** conceptual — framing methods, parity vs CRC vs Hamming,
  what piggybacking is, GBN vs SR difference.
- **GATE / C-DAC:** the **numericals** dominate — CRC remainder, Hamming parity-bit
  count & error position, stop-and-wait / sliding-window **efficiency**, window-size
  formulas. Drill these.
- **Interview:** "how does a sliding window improve throughput?" → the efficiency
  formula and bandwidth-delay-product intuition.

---

## 3.11 Concept Checks & MCQs (test yourself)

1. Bit-stuffing rule and flag? → insert **0 after five 1s**; flag `01111110`.
2. Generator degree 4 → CRC bits and appended zeros? → **4**.
3. Parity bits for 8 data bits? → smallest r with `2^r ≥ 8 + r + 1` → **r = 4**.
4. Stop-and-Wait efficiency with a = 3? → `1/(1 + 6) =` **1/7 ≈ 14.3%**.
5. GBN vs SR sender window (m bits)? → **2^m − 1** vs **2^(m−1)**.
6. Sliding-window efficiency, N = 5, a = 2? → `5/(1 + 4) =` **1 (100%)**.
7. Which corrects a single-bit error? → **Hamming code**.
8. Which is stronger detection: parity or CRC? → **CRC**.
9. Combining ACK with a data frame? → **piggybacking**.
10. Receiver discards out-of-order frames in? → **Go-Back-N**.

---

## 3.12 One-Page Revision Sheet

```
DLL (L2): node-to-node over ONE link. PDU=FRAME. Sublayers: LLC(flow/error)+MAC(address/access).
JOBS: framing, MAC addressing, error control, flow control, access control.

FRAMING: char-count(fragile) | byte stuffing(FLAG + ESC) | bit stuffing(after five 1s insert 0; flag 01111110).

ERROR DETECTION:
  parity: even-parity; catches ODD errors, misses EVEN. 2-D locates errors.
  checksum: sum + complement; used by IP/TCP/UDP; weak.
  CRC: modulo-2 (XOR) poly division by generator G(degree r). append r zeros.
       remainder=CRC; receiver remainder 0 => OK. catches bursts < r. STRONGEST.

ERROR CORRECTION (Hamming): parity at positions 1,2,4,8...(powers of 2).
  parity bits r: smallest r with 2^r >= m+r+1.  m=4 -> r=3 => Hamming(7,4).
  syndrome (failed checks in binary) = ERROR POSITION -> flip it.
  detect d errors: distance d+1 ; correct d: distance 2d+1.

FLOW/ARQ:  a = Tp/Tt.
  Stop-and-Wait U = 1/(1+2a).
  Sliding window U = N/(1+2a) capped 1. Full pipe when N = 1+2a.
  GBN: receiver in-order only, DISCARDS oob, resend-all-after-loss. Wsend <= 2^m - 1.
  SR : receiver BUFFERS oob, resend-only-lost. Wsend=Wrecv <= 2^(m-1).
  PIGGYBACKING = ACK rides on outgoing data. Cumulative ACK (GBN/TCP). NAK (SR).
```

### Flash cards

| Front | Back |
|-------|------|
| Bit-stuffing rule | after five 1s, insert a 0 (flag 01111110) |
| CRC arithmetic | modulo-2 XOR polynomial division |
| CRC bits for gen degree r | r (append r zeros) |
| Hamming parity count | smallest r: 2^r ≥ m+r+1 |
| Hamming parity positions | powers of 2 (1,2,4,8) |
| Correct d errors needs distance | 2d + 1 |
| Stop-and-Wait efficiency | 1/(1+2a), a = Tp/Tt |
| Sliding-window efficiency | N/(1+2a), max 1 |
| GBN vs SR window | 2^m−1 vs 2^(m−1) |
| Piggybacking | ACK carried on a data frame |

### Spaced repetition
- **24-hour:** compute one CRC remainder and one Hamming parity-bit count from scratch.
- **7-day:** stop-and-wait & sliding-window efficiency numericals; GBN vs SR windows.
- **30-day:** given bandwidth/frame/Tp, find `a`, the efficiency, and the window size
  to reach 100% — without notes.

---

## 3.13 Summary

The **Data Link layer** turns the raw bit-pipe into a **reliable link between two
nodes**. It performs **framing** (bit/byte stuffing), **error detection** (parity <
checksum < **CRC**, the strongest, via modulo-2 division), and **error correction**
(**Hamming code**, parity bits at powers of two, syndrome = error position). It
controls flow and reliability with **ARQ**: **Stop-and-Wait** (efficiency
`1/(1+2a)`, poor on long links) and **sliding-window** protocols — **Go-Back-N**
(resend everything after a loss, window `2^m−1`) and **Selective Repeat** (resend only
the lost frame, window `2^(m−1)`), with efficiency `N/(1+2a)`. Extras like
**piggybacking** and cumulative ACKs save bandwidth. These mechanisms reappear
end-to-end in **TCP** (M8).

Next, **Module 4 — The MAC Sublayer & LANs** answers "who gets to talk on a shared
medium?" — ALOHA, CSMA/CD (Ethernet), CSMA/CA (Wi-Fi), plus switching, ARP, and
VLANs.

> **You have mastered this module when** you can: stuff/unstuff bits, compute a CRC
> remainder and verify it, size and place Hamming parity bits and locate an error from
> the syndrome, derive stop-and-wait and sliding-window efficiency from `a`, and state
> the GBN vs SR window formulas and behaviours — all without notes.
