---
title: "Module 5 — The Network Layer & IP Addressing"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — The Network Layer & IP Addressing

> **Where this module sits.**
> The Data Link layer (M3–M4) moves a frame across **one link**. But the Internet is
> millions of links. **Layer 3, the Network layer**, provides **end-to-end delivery
> across many networks** using **logical (IP) addresses** and **routing**. This module
> is about the *addressing* half: **IPv4, classes, subnetting, CIDR, special
> addresses, NAT, the IP header (and fragmentation), ICMP, and IPv6**. Routing
> *algorithms* come next (M6). **Subnetting is the single most exam-tested CN skill** —
> we drill it with worked numericals.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★★   | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **subnetting** (network/
broadcast/first/last host, #subnets, #hosts = 2^h − 2); **subnet mask ↔ prefix (CIDR)**;
**classes A/B/C** and default masks; **CIDR aggregation/supernetting**; **private
addresses & NAT**; **IPv4 header fields** (TTL, protocol, fragmentation offset);
**fragmentation** numericals (MTU, offset in units of 8); **ICMP** (ping/traceroute);
**IPv6** (128-bit, notation, why).

---

## 5.1 What the Network Layer Does

- **Logical addressing** — every host gets an **IP address** (works across links,
  unlike the local-only MAC).
- **Routing** — choose a path across networks (M6); **forwarding** — move a packet to
  the next hop using the routing table.
- **Fragmentation & reassembly** — split a packet if it exceeds a link's **MTU**.
- **Best-effort, connectionless** — IP does **not** guarantee delivery, order, or
  no-duplication (that's TCP's job, M7). IP just tries its best.

> **Memory hook:** **IP is the postal address of the Internet** — it gets a packet
> from any host to any host, hop by hop, but makes no delivery promises (that's the
> courier's "we'll try"). MAC = which house on this street; IP = which house on Earth.

### MCQs

1. IP delivery guarantee? → **best-effort** (no guarantee; connectionless).
2. MAC vs IP scope? → **MAC = local link**, **IP = end-to-end**.
3. Splitting a big packet for a small-MTU link is? → **fragmentation**.

---

## 5.2 IPv4 Addresses & Classes

An **IPv4 address is 32 bits**, written as four **octets** in dotted decimal
(`192.168.1.10`), each 0–255. An address has a **network part** and a **host part**.

![IPv4 is 32 bits in four octets; classes A/B/C set how many leading bits are network vs host, with characteristic first-octet ranges.](images/13_ipv4_classes.png)

| Class | Leading bits | 1st octet range | Default mask | Hosts/network |
|---|---|---|---|---|
| **A** | 0 | 1–126 | /8 (255.0.0.0) | ~16 million |
| **B** | 10 | 128–191 | /16 (255.255.0.0) | ~65,000 |
| **C** | 110 | 192–223 | /24 (255.255.255.0) | 254 |
| **D** | 1110 | 224–239 | — | **multicast** |
| **E** | 1111 | 240–255 | — | experimental |

(127.x.x.x is reserved for **loopback** — `127.0.0.1` = localhost.)

> **Memory hook:** first octet tells the class — **A ≤ 126, B ≤ 191, C ≤ 223, D ≤ 239,
> E ≤ 255.** Classful wastes addresses, so the real world uses **CIDR** (§5.4).

### MCQs

1. IPv4 address length? → **32 bits**.
2. First octet 150 → which class? → **B** (128–191).
3. 224–239 is reserved for? → **multicast (Class D)**.
4. Loopback address? → **127.0.0.1**.

---

## 5.3 Subnetting — the Core Exam Skill

**Subnetting** borrows bits from the **host** part to create smaller **subnets**. The
**subnet mask** (or **/prefix**) marks how many bits are network+subnet (1s) vs host
(0s).

![Splitting 192.168.1.0/24 into four /26 subnets: borrow 2 host bits (2² = 4 subnets), leaving 6 host bits (2⁶−2 = 62 hosts each).](images/14_subnetting.png)

**The formulas (memorise):**

```
prefix /p  ->  host bits h = 32 - p
number of subnets  = 2^(bits borrowed)
addresses per subnet = 2^h
usable hosts per subnet = 2^h - 2   (minus network & broadcast addresses)
block size (per octet) = 256 - (mask octet value)
```

**Worked example 1 — analyse an address.** Given `192.168.1.100/26`:
- Mask /26 = `255.255.255.192`; host bits `h = 32 − 26 = 6`; block size `256 − 192 = 64`.
- Subnets step by 64: `.0, .64, .128, .192`. `.100` falls in the **.64** block.
- **Network = 192.168.1.64**, **Broadcast = 192.168.1.127**, **first host .65, last
  host .126**, **usable = 2⁶ − 2 = 62**.

**Worked example 2 — split a network.** "Divide `192.168.1.0/24` into 4 subnets":
- Need 4 = 2² subnets → **borrow 2 bits** → new prefix **/26**.
- Subnets: `.0/26, .64/26, .128/26, .192/26`; each has **62 usable hosts**.

**Worked example 3 — size for hosts.** "A subnet must fit 500 hosts":
- Need `2^h − 2 ≥ 500` → `h = 9` (2⁹−2 = 510). Prefix `= 32 − 9 = /23`.

> **Memory hook:** **hosts halve, subnets double** each time you borrow a bit. Always
> subtract **2** for host count (network + broadcast are not assignable).

### VLSM (Variable-Length Subnet Masking)

Real networks use **different-size subnets** from one block (a /30 for a 2-host link, a
/25 for a big LAN). Assign **largest subnets first**. This avoids the waste of fixed
subnetting.

### MCQs

1. Usable hosts in a /26? → **62** (2⁶−2).
2. To make 8 subnets, borrow how many bits? → **3** (2³).
3. /29 gives how many usable hosts? → `2³ − 2 =` **6** (good for tiny subnets; note a
   pure point-to-point link uses **/30** or **/31**).
4. Network address of 10.1.1.200/26? → **10.1.1.192**.

---

## 5.4 CIDR & Supernetting (classless addressing)

**CIDR (Classless Inter-Domain Routing)** drops fixed classes and uses an explicit
**/prefix** of any length (e.g. `10.0.0.0/12`). Benefits:

- **Flexible allocation** — give an org exactly what it needs, not a whole class.
- **Route aggregation (supernetting)** — combine many small routes into **one**,
  shrinking routing tables.

**Aggregation worked example:** `200.1.0.0/24, 200.1.1.0/24, 200.1.2.0/24,
200.1.3.0/24` share the first **22 bits** → aggregate to **`200.1.0.0/22`** (one route
instead of four).

> **Memory hook:** **subnetting splits (more, smaller); supernetting merges (fewer,
> bigger).** CIDR = "prefix length is whatever you say," not tied to A/B/C.

### MCQs

1. CIDR notation for a 255.255.255.0 mask? → **/24**.
2. Four consecutive /24s aggregate to? → a **/22**.
3. CIDR's routing-table benefit? → **aggregation** (fewer routes).

---

## 5.5 Special & Private Addresses; NAT

- **Private ranges (RFC 1918)** — not routable on the Internet: `10.0.0.0/8`,
  `172.16.0.0/12`, `192.168.0.0/16`.
- **Loopback** `127.0.0.0/8` (localhost). **APIPA** `169.254.0.0/16` (self-assigned
  when DHCP fails). **Network address** (all host bits 0) and **broadcast** (all host
  bits 1) are reserved.

**NAT (Network Address Translation)** lets many private hosts share one public IP,
tracked by **port (PAT)**. It **conserves scarce IPv4** addresses and hides the
internal network.

![NAT maps many private IPs to one public IP using port numbers, conserving IPv4 addresses and masking the internal network.](images/16_nat.png)

> **Memory hook:** **private IPs are "internal extensions"; NAT is the receptionist**
> that maps them to one public number using port "extension" numbers.

### MCQs

1. Three private ranges? → **10/8, 172.16/12, 192.168/16**.
2. APIPA range (DHCP failed)? → **169.254.0.0/16**.
3. NAT tracks internal hosts by? → **port number (PAT)**.

---

## 5.6 The IPv4 Header & Fragmentation

![The 20-byte IPv4 header: version/IHL/ToS, total length, the fragmentation trio (identification/flags/offset), TTL, protocol, checksum, and source/destination IPs.](images/15_ipv4_header.png)

Key fields:

- **Version (4)**, **IHL** (header length), **Total Length** (header+data, max 65,535).
- **TTL (Time To Live):** decremented each hop; at **0** the packet is dropped (stops
  loops). `traceroute` exploits this.
- **Protocol:** what's inside — **6 = TCP, 17 = UDP, 1 = ICMP**.
- **Fragmentation trio:** **Identification** (same for all fragments of a packet),
  **Flags** (DF = don't fragment, MF = more fragments), **Fragment Offset** (position
  of this fragment, **in units of 8 bytes**).

**Fragmentation worked example:** a **4000-byte** packet (20-byte header → 3980 data)
must cross a link with **MTU = 1500**. Each fragment's data must be a multiple of 8:
max data per fragment = 1480 (1500 − 20; 1480 is divisible by 8).
- Frag 1: data 0–1479, **offset = 0**, MF = 1.
- Frag 2: data 1480–2959, **offset = 1480/8 = 185**, MF = 1.
- Frag 3: data 2960–3979 (1020 bytes), **offset = 2960/8 = 370**, MF = 0 (last).

> **Memory hook:** **offset is counted in 8-byte units** (so non-last fragments carry
> a multiple of 8 bytes). TTL = "hops left"; DF = "don't fragment me."

### MCQs

1. Field that prevents infinite loops? → **TTL**.
2. Protocol number for TCP / UDP / ICMP? → **6 / 17 / 1**.
3. Fragment offset is measured in units of? → **8 bytes**.
4. Flag meaning "more fragments follow"? → **MF = 1**.

---

## 5.7 ICMP — the Network Layer's Messenger

**ICMP (Internet Control Message Protocol)** carries error/diagnostic messages for IP
(it rides *inside* IP packets, protocol 1). Examples: **destination unreachable, time
exceeded (TTL=0), echo request/reply**.

- **`ping`** = ICMP echo request/reply → is the host reachable + round-trip time.
- **`traceroute`/`tracert`** = send packets with increasing **TTL** (1, 2, 3…); each
  router that drops one at TTL=0 replies "time exceeded," revealing the path hop by hop.

### MCQs

1. `ping` uses? → **ICMP echo request/reply**.
2. `traceroute` works by manipulating? → the **TTL** field.
3. ICMP sits at which layer? → **Network (3)** (rides in IP).

---

## 5.8 IPv6 — Why & What

IPv4's **~4.3 billion** addresses ran out. **IPv6 uses 128-bit** addresses
(~3.4×10³⁸ — effectively unlimited), written as 8 groups of 4 hex digits
(`2001:0db8:0000:0000:0000:ff00:0042:8329`), shortened with `::` (one run of zeros) and
dropped leading zeros → `2001:db8::ff00:42:8329`.

Improvements over IPv4:

- **Vast address space** → **no NAT needed**; end-to-end addressing restored.
- **Simpler, fixed 40-byte header** (extension headers for options); **no header
  checksum**; **no router fragmentation** (only the source fragments).
- Built-in **IPsec**, better multicast, **SLAAC** (stateless auto-config).
- **Transition:** dual-stack (run both), tunnelling (6in4), translation (NAT64).

> **Memory hook:** **IPv4 = 32 bits (dotted decimal, ran out); IPv6 = 128 bits (hex,
> `::` shorthand, no NAT, no router fragmentation).**

### MCQs

1. IPv6 address length? → **128 bits**.
2. What does `::` mean in IPv6? → one run of **all-zero groups** (used once).
3. IPv6 removed which IPv4 header features? → **checksum** and **router
   fragmentation**.

---

## 5.9 Real-World & Backend Perspectives

- **Subnetting is daily backend/cloud work:** an AWS VPC is a CIDR block (e.g.
  `10.0.0.0/16`) you carve into subnets (public/private) per AZ — exactly §5.3.
- **NAT & private IPs** are why your laptop's `192.168.x.x` reaches the Internet; **NAT
  traversal** (STUN/TURN) is a real problem for peer-to-peer/WebRTC.
- **TTL** shows up as the "hop limit" in `traceroute`, and as a cause of "why can't I
  reach X" (routing loops drop packets at TTL 0).
- **IPv6 now carries a large share of traffic** for big providers (Google reports
  ~40%+ and rising); backend
  services must be dual-stack.

---

## 5.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** forgetting **−2** for usable hosts (network + broadcast are reserved).
  (Exception: modern /31 point-to-point links use both addresses — RFC 3021.)
- **Mistake:** fragment offset in **bytes** — it's in **8-byte units**.
- **Trap:** class D/E aren't for hosts (multicast/experimental).
- **Edge case:** NAT breaks true end-to-end addressing (a reason IPv6 exists), and
  complicates protocols that embed IPs (FTP, SIP).

---

## 5.11 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** classes & ranges, private addresses, IPv4 vs IPv6, what NAT/
  ICMP do, subnet-mask ↔ prefix.
- **GATE / C-DAC:** **subnetting** (network/broadcast/host counts, VLSM), **CIDR
  aggregation**, **fragmentation** (offsets), header fields — pure numericals; be fast.
- **Interview:** "how does subnetting work / what's a /24?"; "what is NAT and why?";
  "IPv4 vs IPv6?" — all core.

---

## 5.12 Concept Checks & MCQs (test yourself)

1. Usable hosts in /28? → `2⁴ − 2 =` **14**.
2. Network of 172.16.20.10/20? → **172.16.16.0** (block size 16 in 3rd octet).
3. Aggregate 172.16.0.0/24 … 172.16.7.0/24 → ? → **172.16.0.0/21** (8 = 2³).
4. Protocol numbers TCP/UDP/ICMP? → **6/17/1**.
5. A 5000-byte packet, MTU 1500 → data per fragment (mult. of 8)? → **1480**.
6. Fragment offset for the 2nd fragment above? → **185** (1480/8).
7. Private class-C range? → **192.168.0.0/16**.
8. IPv6 length & IPv4 length? → **128** vs **32** bits.
9. `traceroute` manipulates? → **TTL**.
10. Prefix to fit 1000 hosts? → **/22** (2¹⁰−2 = 1022).

---

## 5.13 One-Page Revision Sheet

```
NETWORK LAYER (L3): logical addressing + routing/forwarding + fragmentation. IP = best-effort, connectionless. PDU=PACKET.

IPv4 = 32 bits, 4 octets. CLASS by 1st octet: A 1-126(/8) | B 128-191(/16) | C 192-223(/24)
  | D 224-239 multicast | E 240-255. 127=loopback.

SUBNETTING:  h = 32 - prefix.  subnets = 2^borrowed.  addrs/subnet = 2^h.  USABLE = 2^h - 2.
  block size = 256 - mask_octet.  /26=255.255.255.192 (64 block, 62 hosts).
  network=host bits all 0; broadcast=all 1; first=net+1; last=bcast-1.
  size for N hosts: smallest h with 2^h - 2 >= N.   VLSM: assign biggest subnets first.

CIDR: any prefix length. SUPERNET/aggregate: 4 x /24 (same top 22 bits) -> /22.

PRIVATE (RFC1918): 10/8, 172.16/12, 192.168/16.  APIPA 169.254/16.  NAT: many private<->1 public via PORT (PAT).

IPv4 HEADER (20B): Ver|IHL|ToS|TotalLen | ID|Flags(DF,MF)|FragOffset | TTL|Protocol|Checksum | SrcIP|DstIP.
  TTL=hops left(0=drop). Protocol 6=TCP 17=UDP 1=ICMP. OFFSET in 8-byte units. non-last frag data = multiple of 8.

ICMP (proto 1): errors/diagnostics. ping=echo req/reply. traceroute=increasing TTL.

IPv6 = 128 bits, 8 hex groups, :: = one zero-run. no NAT, fixed 40B header, NO checksum, NO router-fragmentation,
  IPsec, SLAAC. transition: dual-stack / tunnel / NAT64.
```

### Flash cards

| Front | Back |
|-------|------|
| Usable hosts formula | 2^h − 2 (h = 32 − prefix) |
| /26 mask & hosts | 255.255.255.192; 62 |
| Class ranges A/B/C | 1–126 / 128–191 / 192–223 |
| Private ranges | 10/8, 172.16/12, 192.168/16 |
| Supernet 4×/24 | one /22 |
| Protocol nums TCP/UDP/ICMP | 6 / 17 / 1 |
| Fragment offset unit | 8 bytes |
| TTL purpose | hop limit; stops loops |
| IPv6 length | 128 bits |
| `::` in IPv6 | one run of zero groups |

### Spaced repetition
- **24-hour:** given an IP/prefix, find network, broadcast, host range, and usable
  count (three examples).
- **7-day:** split a block into N subnets (VLSM); aggregate routes; fragmentation offsets.
- **30-day:** design a VPC-style addressing plan (public/private subnets) from one CIDR
  block — without notes.

---

## 5.14 Summary

The **Network layer** provides **best-effort, end-to-end** delivery across many
networks using **32-bit IPv4** addresses (classes **A/B/C**, plus D multicast / E
experimental). **Subnetting** borrows host bits to make subnets — with the core
formulas **host bits = 32 − prefix**, **subnets = 2^borrowed**, and **usable hosts =
2^h − 2** — and **VLSM** lets subnets vary in size. **CIDR** replaces classes with
arbitrary prefixes and enables **route aggregation (supernetting)**. **Private
addresses + NAT** conserve scarce IPv4. The **IPv4 header** carries **TTL, Protocol,
and the fragmentation trio** (offset in **8-byte units**), while **ICMP** powers
**ping/traceroute**. Finally, **IPv6** (**128-bit**, hex with `::`) fixes address
exhaustion, drops NAT and router fragmentation, and simplifies the header.

Next, **Module 6 — Routing Algorithms & Protocols** answers *how* routers choose paths:
distance-vector vs link-state, Dijkstra & Bellman-Ford, and the real protocols
(**RIP, OSPF, BGP**).

> **You have mastered this module when** you can: classify an address and find its
> network/broadcast/host range/usable count from any prefix; split a block into subnets
> (fixed and VLSM) and aggregate routes; explain private addressing and NAT; read the
> IPv4 header and compute fragment offsets; and contrast IPv4 with IPv6 — all without
> notes.
