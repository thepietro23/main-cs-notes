---
title: "Module 4 — The MAC Sublayer & LANs (Access, Ethernet, ARP, Switching)"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — The MAC Sublayer & LANs (Access, Ethernet, ARP, Switching)

> **Where this module sits.**
> Module 3 made a single link reliable. But a LAN is a **shared medium** — many hosts,
> one cable/air. If two send at once, their signals **collide** and both are lost. The
> **MAC (Media Access Control) sublayer** answers the question **"who gets to talk,
> and when?"** This module covers the access protocols (**ALOHA, CSMA/CD, CSMA/CA**),
> the LAN that won (**Ethernet**), how a host finds another's MAC (**ARP**), and how
> **switches, collision/broadcast domains, and VLANs** structure real networks. ALOHA
> efficiency and the CSMA/CD **minimum-frame-size** numerical are exam favourites.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **pure vs slotted ALOHA**
efficiency (**18.4% / 36.8%**); **CSMA** variants (1-persistent / non-persistent /
p-persistent); **CSMA/CD vs CSMA/CA** (wired vs Wi-Fi); **minimum Ethernet frame size**
and why (`≥ 2·Tp·B`); **MAC address** (48-bit); **ARP** (broadcast request / unicast
reply); **hub vs switch vs router** and **collision vs broadcast domains**; **VLAN**.

---

## 4.1 The Multiple-Access Problem

On a shared medium, simultaneous transmissions **collide**. MAC protocols coordinate
access. They fall into three families:

![Multiple-access protocols split into random access (contend and recover), controlled access (take turns), and channelization (split the channel).](images/09_multiple_access.png)

1. **Random access** — hosts transmit whenever they have data, and **recover from
   collisions** (ALOHA, CSMA, CSMA/CD, CSMA/CA).
2. **Controlled access** — hosts **coordinate turns** (reservation, polling, token
   passing) — no collisions, but overhead.
3. **Channelization** — statically **split the channel** (FDMA/TDMA/CDMA — from M2).

> **Memory hook:** **Random = "just talk, apologise on collision"; Controlled = "raise
> your hand / pass the mic"; Channelization = "everyone gets a fixed lane."**

### MCQs

1. Three MAC families? → **random, controlled, channelization**.
2. Token passing is which family? → **controlled access**.
3. Ethernet (classic) is which family? → **random access (CSMA/CD)**.

---

## 4.2 ALOHA (the ancestor) — Pure & Slotted

**Pure ALOHA:** transmit whenever you have data; if a collision occurs (no ACK), wait
a random time and resend. Very simple, but collisions are frequent.

- **Vulnerable period = 2 × frame time** (a frame collides with any frame starting in
  the frame-time before *or* during it).
- **Maximum efficiency = 1/(2e) ≈ 18.4%** at load G = 0.5.

**Slotted ALOHA:** time is divided into **slots** equal to one frame time; hosts may
only start at a slot boundary. This halves the vulnerable period.

- **Vulnerable period = 1 × frame time.**
- **Maximum efficiency = 1/e ≈ 36.8%** at G = 1.

> **Memory hook:** **slotting doubles ALOHA's efficiency** (18.4% → 36.8%) by making
> everyone start on the beat. `S = G·e^(−2G)` (pure), `S = G·e^(−G)` (slotted).

### MCQs

1. Pure vs slotted ALOHA max efficiency? → **18.4% (1/2e)** vs **36.8% (1/e)**.
2. Pure ALOHA vulnerable period? → **2 × frame time**.
3. Slotted ALOHA improves efficiency by? → aligning sends to **time slots**.

---

## 4.3 CSMA — Listen Before You Talk

**Carrier Sense Multiple Access:** sense the channel first; transmit only if idle.
This cuts collisions but can't eliminate them (**propagation delay** means two hosts
can both sense "idle" and then collide). Variants differ in *what you do when the
channel is busy*:

| Variant | If channel busy | Behaviour |
|---|---|---|
| **1-persistent** | keep sensing; send **immediately** when idle | greedy; high collision if many wait |
| **Non-persistent** | wait a **random** time, then sense again | fewer collisions, more delay |
| **p-persistent** | (slotted) when idle, send with prob **p**, else defer | tunable middle ground |

### MCQs

1. Why does CSMA still get collisions? → **propagation delay** (two see idle, both send).
2. Which CSMA sends immediately when the channel frees? → **1-persistent**.
3. Which waits a random time when busy? → **non-persistent**.

---

## 4.4 CSMA/CD (classic Ethernet) & CSMA/CA (Wi-Fi)

**CSMA/CD (Collision Detection):** while transmitting, keep listening; if a collision
is detected, **stop, send a JAM signal**, and back off a random time
(**binary exponential backoff**: after the k-th collision, wait a random number of
slots in `[0, 2^k − 1]`, up to k = 10).

![CSMA/CD: sense the channel, transmit, and if a collision is detected send a jam and back off before retrying.](images/10_csma_cd.png)

**The minimum-frame-size rule (key numerical):** to *detect* a collision, a sender
must still be transmitting when the collision signal returns — so the frame must take
at least **2 × Tp** (round-trip propagation) to send:

```
Frame transmission time  Tt ≥ 2 · Tp
Minimum frame size  L_min = 2 · Tp · B      (B = bandwidth)
```

For classic 10 Mbps Ethernet this gives the famous **64-byte** minimum frame.

**CSMA/CA (Collision Avoidance):** used by **Wi-Fi (802.11)**, because a wireless node
**can't detect collisions** while transmitting (its own signal drowns others, and the
**hidden-terminal** problem). Instead it *avoids* them: sense idle, wait a random
backoff, use **ACKs** to confirm receipt, and optionally **RTS/CTS** handshake to
reserve the medium.

> **Memory hook:** **CD = "Collision Detection" (wired, stop when you hear a crash);
> CA = "Collision Avoidance" (wireless, tiptoe with backoff + ACK because you can't
> hear the crash).**

### MCQs

1. Min frame size formula? → **L_min = 2·Tp·B**.
2. Classic Ethernet min frame? → **64 bytes**.
3. Why Wi-Fi uses CA not CD? → a station **can't detect collisions** while sending
   (hidden terminal).
4. Backoff after k-th collision picks a slot in? → **[0, 2^k − 1]** (binary
   exponential backoff).

---

## 4.5 Ethernet & the MAC Address

**Ethernet (IEEE 802.3)** is the dominant wired LAN. Its frame:

![Ethernet frame: preamble + SFD, destination and source MAC, type/length, 46–1500-byte payload, and a CRC-32 FCS trailer.](images/11_ethernet_frame.png)

- **MAC address:** **48 bits (6 bytes)**, written as `AA:BB:CC:DD:EE:FF`. First 3
  bytes = **OUI** (vendor); globally unique per NIC. Broadcast = `FF:FF:FF:FF:FF:FF`.
- **Payload:** **46–1500 bytes** (1500 = the standard **MTU**). Min frame **64 bytes**
  (padding if needed); **FCS** = CRC-32 (from M3).
- **Evolution:** 10 Mbps → Fast (100M) → Gigabit → 10/40/100 GbE; modern Ethernet is
  **switched full-duplex** (no collisions at all — CSMA/CD is legacy for shared media).

> **Memory hook:** **MAC = 48-bit hardware address burned into the NIC** (physical),
> vs **IP = logical address** (M5). MAC is local; IP is end-to-end.

### MCQs

1. MAC address length? → **48 bits (6 bytes)**.
2. Ethernet MTU (max payload)? → **1500 bytes**.
3. Broadcast MAC address? → **FF:FF:FF:FF:FF:FF**.
4. First 3 bytes of a MAC identify the? → **vendor (OUI)**.

---

## 4.6 ARP — Mapping IP to MAC

To send a frame on the LAN you need the destination's **MAC**, but apps use **IP**.
**ARP (Address Resolution Protocol)** bridges L3 → L2.

![ARP broadcasts "who has this IP?" to the whole LAN; only the owner replies with its MAC, and the sender caches the mapping.](images/12_arp.png)

- **ARP request:** broadcast — *"Who has 10.0.0.5? Tell 10.0.0.1."*
- **ARP reply:** unicast from the owner — *"10.0.0.5 is at AA:BB:CC:DD:EE:FF."*
- The sender **caches** it in the **ARP table** (with a timeout).
- Cousins: **RARP** (MAC→IP, obsolete), **DHCP** (get your own IP — M9),
  **ARP spoofing** is a classic LAN attack (M10).

> **Memory hook:** **ARP asks the whole room "who owns this IP?"; only the owner
> answers with its MAC.** IP is known, MAC is discovered.

### MCQs

1. ARP maps? → **IP → MAC** (L3 to L2).
2. ARP request is sent how? → **broadcast**; the reply is **unicast**.
3. Where is the resolved mapping stored? → the **ARP cache/table**.

---

## 4.7 LAN Devices — Collision vs Broadcast Domains

| Device | Layer | Collision domains | Broadcast domains |
|---|---|---|---|
| **Hub** | 1 | **1** (all ports share) | 1 |
| **Switch/bridge** | 2 | **1 per port** (each port isolated) | 1 (floods broadcasts) |
| **Router** | 3 | 1 per port | **1 per port** (blocks broadcasts) |

- A **switch** learns which MAC is on which port (**MAC learning**) and forwards a
  frame only to the right port (unicast) — unlike a hub which repeats to all. It
  **breaks up collision domains** but still forwards broadcasts to the whole LAN.
- A **router** separates **broadcast domains** (each interface = a different network).
- **Spanning Tree Protocol (STP)** prevents switching **loops** (which would cause
  broadcast storms) by disabling redundant links.

> **Memory hook:** **Hub = 1 collision domain (dumb); Switch = collision domain per
> port (smart by MAC); Router = broadcast domain per port (smart by IP).**

### MCQs

1. How many collision domains does an 8-port switch have? → **8** (one per port).
2. Which device separates broadcast domains? → **router**.
3. What prevents switching loops? → **Spanning Tree Protocol (STP)**.

---

## 4.8 VLANs (Virtual LANs)

A **VLAN** logically splits one physical switch into **multiple broadcast domains** —
hosts in different VLANs can't talk directly (need a router / L3 switch), even on the
same switch. Benefits: **segmentation, security, and less broadcast traffic**. VLAN
tags use the **802.1Q** header (a 4-byte tag inserted in the Ethernet frame with a
12-bit VLAN ID → up to 4094 VLANs).

> **Memory hook:** **VLAN = software walls inside one switch** — same hardware, many
> separate LANs; crossing walls needs a router.

### MCQs

1. A VLAN creates multiple? → **broadcast domains** on one switch.
2. VLAN tagging standard? → **802.1Q**.
3. To route between VLANs you need? → a **router / L3 switch**.

---

## 4.9 Real-World & Backend Perspectives

- **Modern data-center LANs are fully switched and full-duplex** — collisions are
  gone; CSMA/CD survives only as exam history and legacy shared media. Throughput and
  microbursts (buffer overflow at switches) are the real concerns.
- **ARP + MAC learning** are why "it works on the LAN": `arp -a` shows the cache;
  stale ARP or **ARP spoofing** causes classic connectivity/security incidents.
- **VLANs + 802.1Q** are how cloud VPCs and office networks isolate tenants/teams on
  shared switching hardware.

---

## 4.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** swapping ALOHA numbers — **pure 18.4%, slotted 36.8%** (slotted is
  higher).
- **Mistake:** thinking a switch breaks **broadcast** domains — it breaks **collision**
  domains; only a **router** breaks broadcast domains.
- **Trap:** forgetting the **min-frame-size** reason — it exists so a sender is still
  transmitting when a collision returns (`Tt ≥ 2Tp`).
- **Edge case:** on a full-duplex switched link there are **no collisions**, so CSMA/CD
  is disabled.

---

## 4.11 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** ALOHA/CSMA definitions, CD vs CA, MAC-address facts,
  hub/switch/router domain table, what a VLAN is.
- **GATE / C-DAC:** **ALOHA efficiency**, **min-frame-size**, backoff, collision-domain
  counting — numericals and precise definitions.
- **Interview:** "what happens (at L2) when two hosts talk to each other on a LAN?" →
  ARP to resolve MAC, switch forwards by MAC; "hub vs switch?" → collision domains.

---

## 4.12 Concept Checks & MCQs (test yourself)

1. Pure vs slotted ALOHA efficiency? → **18.4% vs 36.8%**.
2. Three CSMA persistence methods? → **1-persistent, non-persistent, p-persistent**.
3. CD vs CA — wired or wireless? → **CD wired (Ethernet)**, **CA wireless (Wi-Fi)**.
4. Min-frame-size formula & classic value? → **2·Tp·B**; **64 bytes**.
5. MAC address size and broadcast value? → **48 bits**; **FF:FF:FF:FF:FF:FF**.
6. ARP resolves what, and how is the request sent? → **IP→MAC**, **broadcast**.
7. Collision domains of an N-port switch? → **N**.
8. Which device breaks broadcast domains? → **router**.
9. VLAN tagging standard? → **802.1Q**.
10. What stops switching loops? → **STP**.

---

## 4.13 One-Page Revision Sheet

```
MAC SUBLAYER: who talks on a SHARED medium. Families:
  RANDOM (ALOHA, CSMA, CSMA/CD, CSMA/CA) | CONTROLLED (polling, token) | CHANNELIZATION (FDMA/TDMA/CDMA).

ALOHA:  pure  S=G e^-2G, max 1/2e = 18.4% (vuln = 2 frame times)
        slot  S=G e^-G,  max 1/e  = 36.8% (vuln = 1 frame time)

CSMA (listen before talk; collisions remain due to PROPAGATION DELAY):
  1-persistent(send immediately when idle) | non-persistent(random wait) | p-persistent(prob p).

CSMA/CD (Ethernet, WIRED): sense->send->detect collision->JAM->binary exp backoff [0,2^k-1].
  MIN FRAME: Tt >= 2Tp  => Lmin = 2*Tp*B  => 64 bytes (10M Ethernet).
CSMA/CA (Wi-Fi, WIRELESS): can't detect collisions -> avoid: backoff + ACK + optional RTS/CTS.

ETHERNET 802.3: Preamble|SFD|DstMAC(6)|SrcMAC(6)|Type/Len(2)|Payload 46-1500|FCS(CRC32).
  MAC = 48-bit (OUI vendor + NIC). Broadcast=FF:FF:FF:FF:FF:FF. MTU=1500. Modern=switched full-duplex(no collisions).

ARP: IP->MAC. REQUEST=broadcast "who has IP?"; REPLY=unicast MAC. cached in ARP table.

DOMAINS:  Hub(L1)=1 collision domain | Switch(L2)=1 collision/port, floods broadcast |
          Router(L3)=1 broadcast domain/port. Switch learns MAC->port. STP stops loops.
VLAN: split 1 switch into many BROADCAST domains (802.1Q, 12-bit ID <=4094). inter-VLAN needs router.
```

### Flash cards

| Front | Back |
|-------|------|
| Pure / slotted ALOHA efficiency | 18.4% / 36.8% |
| Min Ethernet frame + rule | 64 bytes; Tt ≥ 2Tp |
| CD vs CA | wired detection vs wireless avoidance |
| Binary exponential backoff range | [0, 2^k − 1] |
| MAC address size | 48 bits (6 bytes) |
| Ethernet MTU | 1500 bytes |
| ARP maps / request type | IP→MAC / broadcast |
| Switch breaks which domain | collision (per port) |
| Router breaks which domain | broadcast |
| VLAN standard | 802.1Q |

### Spaced repetition
- **24-hour:** recite ALOHA efficiencies + the min-frame-size derivation.
- **7-day:** CSMA variants; CD vs CA; hub/switch/router domain table.
- **30-day:** given B and Tp, find L_min; count collision/broadcast domains in a mixed
  topology — without notes.

---

## 4.14 Summary

The **MAC sublayer** decides **who transmits on a shared medium**. **Random-access**
protocols evolved from **ALOHA** (pure **18.4%**, slotted **36.8%**) to **CSMA**
(listen first; 1-/non-/p-persistent) to **CSMA/CD** (Ethernet — detect collisions,
jam, binary exponential backoff, and a **64-byte minimum frame** so `Tt ≥ 2Tp`) and
**CSMA/CA** (Wi-Fi — *avoid* collisions since it can't detect them). **Ethernet** frames
carry **48-bit MAC** addresses and a CRC FCS; **ARP** resolves **IP → MAC** by
broadcast request / unicast reply. In LANs, **hubs** share one collision domain,
**switches** give a collision domain per port and learn MACs, **routers** separate
**broadcast** domains, **STP** prevents loops, and **VLANs (802.1Q)** carve one switch
into many broadcast domains.

Next, **Module 5 — The Network Layer & IP Addressing** moves to Layer 3: **IPv4/IPv6
addresses, subnetting, CIDR**, and how packets are addressed for the whole journey —
with the subnetting numericals that dominate exams.

> **You have mastered this module when** you can: name the three MAC families and place
> each protocol; state pure/slotted ALOHA efficiency; derive the minimum frame size and
> explain CD vs CA; read an Ethernet frame and a MAC address; walk through ARP; and
> count collision vs broadcast domains for hubs/switches/routers and VLANs — all
> without notes.
