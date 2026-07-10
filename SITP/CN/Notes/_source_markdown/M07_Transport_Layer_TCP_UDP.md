---
title: "Module 7 — The Transport Layer (TCP & UDP)"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — The Transport Layer (TCP & UDP)

> **Where this module sits.**
> The Network layer (M5–M6) delivers a packet **host-to-host** — but a host runs many
> programs at once. **Layer 4, the Transport layer**, delivers **process-to-process**
> using **ports**, and adds the reliability IP lacks. This is where **TCP** (reliable,
> ordered, connection-oriented) and **UDP** (fast, connectionless) live. The **3-way
> handshake**, TCP vs UDP, ports/sockets, and sequence/ack numbers are among the most
> asked topics in the whole subject and in interviews.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★★★     | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **TCP vs UDP**; the **3-way
handshake** (SYN/SYN-ACK/ACK) and **4-way teardown** (FIN); **ports & sockets**
(well-known ports); **TCP header** (seq/ack, flags, window); **reliability**
(seq numbers, retransmission, RTO); **flow control** (receiver window); **multiplexing/
demultiplexing**; connection-oriented vs connectionless.

---

## 7.1 What the Transport Layer Does

- **Process-to-process delivery** via **port numbers** (the Network layer only reaches
  the host; ports reach the right *program*).
- **Multiplexing / demultiplexing** — combine data from many apps at the sender; deliver
  to the right app at the receiver, using **(IP, port)** = a **socket**.
- **Reliability** (TCP only): detect loss, retransmit, deliver **in order**, no
  duplicates.
- **Flow control** (TCP): don't overrun the *receiver*.
- **Congestion control** (TCP): don't overrun the *network* (Module 8).

![Many apps on one host share one IP; the port number demultiplexes each segment to the correct process (socket = IP : port).](images/22_ports_mux.png)

**Ports:** 16-bit (0–65535). **Well-known (0–1023):** HTTP **80**, HTTPS **443**, DNS
**53**, SSH **22**, SMTP **25**, FTP **20/21**, DHCP **67/68**. Registered
(1024–49151); dynamic/ephemeral (49152–65535, used by clients).

> **Memory hook:** **IP gets you to the building; the port is the apartment number.**
> A socket = IP + port = one endpoint of a conversation.

### MCQs

1. Transport delivers to a? → **process** (via port), not just a host.
2. A socket is? → **(IP address, port number)**.
3. Well-known port for HTTPS / DNS / SSH? → **443 / 53 / 22**.
4. Port number field size? → **16 bits** (0–65535).

---

## 7.2 UDP — Fast & Connectionless

**UDP (User Datagram Protocol)** is a thin wrapper over IP: **no connection, no
reliability, no ordering, no congestion control** — just ports + a checksum. Header is
only **8 bytes** (source port, dest port, length, checksum).

- **Pros:** low overhead, low latency, supports **broadcast/multicast**, no
  handshake/teardown.
- **Cons:** may lose/reorder/duplicate; the app must handle it if it cares.
- **Used by:** **DNS**, **DHCP**, **VoIP/video**, online games, streaming — where
  **speed matters more than perfect delivery**; and **QUIC/HTTP-3** (reliability built
  on top of UDP in user space).

> **Memory hook:** **UDP = a postcard** — cheap, fast, might get lost, no confirmation.
> Great when a late packet is worse than a lost one (live voice).

### MCQs

1. UDP header size? → **8 bytes**.
2. Does UDP guarantee delivery/order? → **no**.
3. Two protocols that use UDP? → **DNS, DHCP** (also VoIP, QUIC).

---

## 7.3 TCP — Reliable & Connection-Oriented

**TCP (Transmission Control Protocol)** provides a **reliable, ordered, byte-stream**
between two endpoints: connection setup/teardown, sequence/ack numbers,
retransmission, flow control, and congestion control (M8).

![The 20-byte TCP header: ports, sequence and acknowledgement numbers, header length, flags, window size, checksum, and urgent pointer.](images/21_tcp_header.png)

Key header fields:

- **Source/Destination Port** — the sockets.
- **Sequence Number** — byte offset of this segment's first byte (enables ordering).
- **Acknowledgement Number** — next byte expected (cumulative ACK).
- **Flags** — **SYN** (open), **ACK**, **FIN** (close), **RST** (reset/abort), **PSH**,
  **URG**.
- **Window Size** — receiver's free buffer (**flow control**).
- **Checksum** — error detection.

> **Memory hook:** **TCP = a phone call** — dial (handshake), talk reliably in order,
> hang up (teardown). UDP = shouting a postcard into the void.

### MCQs

1. TCP delivers a? → **reliable, ordered byte stream**.
2. Which field enables reordering? → **sequence number**.
3. Flag to abruptly abort a connection? → **RST**.
4. Which field carries flow-control info? → **window size**.

---

## 7.4 Connection Setup & Teardown (the handshake)

![TCP opens with a 3-way handshake (SYN, SYN-ACK, ACK) that syncs sequence numbers, then closes with a 4-way exchange of FIN/ACK in each direction.](images/20_tcp_handshake.png)

**3-way handshake (open):**

1. Client → **SYN** (seq = x): "let's talk; my start seq is x."
2. Server → **SYN-ACK** (seq = y, ack = x+1): "ok; my start seq is y, I got yours."
3. Client → **ACK** (ack = y+1): "got yours." → **connection established**.

Why **three**? Both sides must **agree on initial sequence numbers** and confirm each
other is reachable — two messages can't confirm both directions.

**4-way teardown (close):** each side sends its own **FIN** and gets an **ACK** (the
connection is full-duplex, so each direction closes independently). The active closer
enters **TIME_WAIT** (~2×MSL) to absorb stray delayed segments before fully closing.

- **SYN flood** = a DoS attack: send many SYNs, never complete the handshake, exhausting
  the server's half-open table (defended by **SYN cookies**).

### MCQs

1. The 3 handshake messages? → **SYN, SYN-ACK, ACK**.
2. Why 3 (not 2)? → to **sync sequence numbers** and confirm **both** directions.
3. Messages to close? → **4** (FIN + ACK each way).
4. State the active closer waits in? → **TIME_WAIT** (~2·MSL).

---

## 7.5 Reliability & Flow Control

**Reliability:** every byte has a **sequence number**; the receiver sends **cumulative
ACKs** ("next byte I expect"). Lost segments are **retransmitted** on **timeout (RTO)**
or **3 duplicate ACKs** (fast retransmit — M8). The **RTO** is set from a smoothed
**RTT estimate** (`RTT` + variance, Jacobson's algorithm).

**Flow control (receiver-driven):** the receiver advertises a **window (rwnd)** = free
buffer space; the sender may have at most `rwnd` unacknowledged bytes in flight — a
**sliding window** (the same idea as M3, now end-to-end). If the receiver's window hits
0, the sender pauses and probes with **window-update / zero-window probes**.

> **Memory hook:** **flow control = the receiver saying "slow down, my inbox is
> filling"** (rwnd). Congestion control (M8) = **the network** saying slow down.

### MCQs

1. TCP ACKs are? → **cumulative** ("next byte expected").
2. Two triggers for retransmission? → **timeout (RTO)** and **3 duplicate ACKs**.
3. Flow control uses which field? → **receiver window (rwnd)**.
4. RTO is derived from? → the **estimated RTT** (+ variance).

---

## 7.6 TCP vs UDP (the comparison you must know cold)

| | **TCP** | **UDP** |
|---|---|---|
| Connection | connection-oriented (handshake) | connectionless |
| Reliability | reliable (ACK + retransmit) | best-effort |
| Ordering | in-order (seq numbers) | no ordering |
| Flow / congestion control | yes | no |
| Header size | 20 bytes (min) | 8 bytes |
| Speed / overhead | slower, more overhead | fast, minimal |
| Broadcast/multicast | no | yes |
| Use cases | web, email, file transfer, SSH | DNS, DHCP, VoIP, video, games, QUIC |

> **Memory hook:** **TCP = reliable phone call; UDP = fast postcard.** Choose TCP when
> every byte must arrive correctly; UDP when speed beats perfection.

### MCQs

1. Header sizes TCP/UDP? → **20 / 8 bytes**.
2. Which supports multicast? → **UDP**.
3. Video call — TCP or UDP? → **UDP** (late data is useless).
4. File download — TCP or UDP? → **TCP** (must be exact).

---

## 7.7 Real-World & Backend Perspectives

- **Sockets are the backend API:** `socket → bind → listen → accept` (server) and
  `connect` (client) are exactly this layer (M20 in the OS notes). Ports are what your
  service "listens on."
- **TIME_WAIT** piling up is a real ops issue on busy servers/load-balancers (tune reuse,
  keep-alive).
- **QUIC / HTTP-3** move reliability + ordering into **user space over UDP** to cut
  handshake latency and avoid head-of-line blocking — a modern, heavily-tested trend.
- **SYN floods** and **RST injection** are classic network attacks tied to this layer
  (M10).

---

## 7.8 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** "UDP has no header fields for reliability, so it's useless" — it's ideal
  when **latency** matters (voice) or the app adds its own reliability (QUIC).
- **Mistake:** thinking close is 3-way — **open = 3**, **close = 4** (each direction
  FIN/ACK).
- **Trap:** flow control (rwnd, receiver) vs congestion control (cwnd, network) — **two
  different windows**; TCP sends `min(rwnd, cwnd)`.
- **Edge case:** TIME_WAIT exists so a delayed duplicate from an old connection can't be
  mistaken for the new one.

---

## 7.9 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** TCP vs UDP, handshake, ports, which protocol uses which
  transport (DNS=UDP, HTTP=TCP).
- **GATE / C-DAC:** handshake sequence-number arithmetic, header fields, flow-control
  window, connection states, efficiency (ties to M3 sliding window).
- **Interview:** "TCP vs UDP and when to use each?", "explain the 3-way handshake",
  "what is a socket?" — near-guaranteed questions.

---

## 7.10 Concept Checks & MCQs (test yourself)

1. Socket = ? → **(IP, port)**.
2. 3-way handshake messages? → **SYN, SYN-ACK, ACK**.
3. Why 3, not 2? → sync **sequence numbers** + confirm **both directions**.
4. TCP vs UDP header size? → **20 / 8 bytes**.
5. Which is connectionless? → **UDP**.
6. Two retransmission triggers? → **RTO timeout**, **3 dup ACKs**.
7. Flow-control window vs congestion window? → **rwnd (receiver)** vs **cwnd
   (network)**; send `min(rwnd,cwnd)`.
8. Ports for HTTP/HTTPS/DNS/SSH? → **80/443/53/22**.
9. Teardown message count? → **4** (FIN/ACK each way).
10. Protocol for VoIP? → **UDP**.

---

## 7.11 One-Page Revision Sheet

```
TRANSPORT (L4): PROCESS-to-process via PORTS. socket = (IP,port). mux/demux. PDU=SEGMENT.
PORTS: 16-bit. well-known 0-1023: HTTP80 HTTPS443 DNS53 SSH22 SMTP25 FTP20/21 DHCP67/68.

UDP (8B header): connectionless, unreliable, unordered, NO flow/congestion ctrl, supports multicast.
  fast/low-overhead. used: DNS, DHCP, VoIP, video, games, QUIC. "postcard".

TCP (20B header): connection-oriented, RELIABLE, ordered byte-stream, flow+congestion control. "phone call".
  header: srcPort|dstPort|SEQ|ACK|HLen|flags(SYN ACK FIN RST PSH URG)|WINDOW|checksum|urgptr.
  SEQ=byte offset; ACK=next byte expected (CUMULATIVE).

HANDSHAKE (open, 3-way): SYN(x) -> SYN-ACK(y,ack x+1) -> ACK(ack y+1). syncs seq nums + both directions.
TEARDOWN (close, 4-way): FIN/ACK each direction. active closer -> TIME_WAIT (~2*MSL).
  SYN flood = DoS (half-open); defend with SYN cookies.

RELIABILITY: seq + cumulative ACK; retransmit on RTO (from RTT estimate) or 3 DUP ACKs (fast retransmit).
FLOW CONTROL: receiver window rwnd (don't overrun RECEIVER). sender in-flight <= min(rwnd, cwnd).
  (congestion control cwnd = don't overrun NETWORK -> Module 8.)

TCP vs UDP: reliable/ordered/heavy vs fast/unordered/light. TCP=web/email/file/SSH; UDP=DNS/VoIP/stream.
```

### Flash cards

| Front | Back |
|-------|------|
| Socket | (IP, port) |
| 3-way handshake | SYN, SYN-ACK, ACK |
| Why 3-way | sync seq numbers + both directions |
| Teardown messages | 4 (FIN/ACK each way) |
| TCP / UDP header size | 20 / 8 bytes |
| Cumulative ACK meaning | next byte expected |
| Retransmit triggers | RTO timeout; 3 dup ACKs |
| Flow vs congestion window | rwnd (receiver) vs cwnd (network) |
| Ports 80/443/53/22 | HTTP/HTTPS/DNS/SSH |
| Active closer state | TIME_WAIT (~2·MSL) |

### Spaced repetition
- **24-hour:** draw the 3-way handshake with seq/ack numbers and the 4-way teardown.
- **7-day:** TCP vs UDP table; ports; flow vs congestion window.
- **30-day:** explain end-to-end how a browser opens a TCP connection and why UDP suits
  VoIP — without notes.

---

## 7.12 Summary

The **Transport layer** provides **process-to-process** delivery via **ports**
(**socket = IP + port**) and **multiplexing/demultiplexing**. **UDP** is a thin,
**connectionless, unreliable** wrapper (8-byte header) — fast and multicast-capable,
ideal for **DNS, DHCP, VoIP, and QUIC**. **TCP** is **connection-oriented and
reliable** (20-byte header): it opens with a **3-way handshake** (SYN/SYN-ACK/ACK) that
**syncs sequence numbers**, closes with a **4-way** FIN exchange (with **TIME_WAIT**),
and guarantees an **ordered byte stream** via sequence/cumulative-ACK numbers,
retransmission (**RTO** or **3 dup ACKs**), and **flow control** (receiver window
`rwnd`). The sender is limited by **min(rwnd, cwnd)** — the second window,
**congestion**, is next.

Next, **Module 8 — Congestion Control & QoS** covers **cwnd**: slow start, AIMD, fast
retransmit/recovery (the TCP "sawtooth"), and traffic shaping (leaky/token bucket).

> **You have mastered this module when** you can: define ports/sockets and list
> well-known ports; contrast TCP vs UDP and pick the right one; draw and explain the
> 3-way handshake (with seq numbers) and 4-way teardown; describe TCP reliability and
> flow control; and distinguish rwnd from cwnd — all without notes.
