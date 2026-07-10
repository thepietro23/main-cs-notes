---
title: "Module 1 — Introduction to Networks & the Layered Models"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Introduction to Networks & the Layered Models

> **Where this module sits.**
> This is the map for the whole subject. Before we study cables (M2), Ethernet
> (M4), IP (M5), routing (M6), TCP (M7), or DNS/HTTP (M9), we need one mental
> framework that tells us **where each of those topics lives and how they fit
> together**. That framework is the **layered model** (OSI and TCP/IP). Almost
> every later module is really "a deep dive into one layer," so getting this map
> right makes everything afterwards click — and layering itself is one of the most
> reliably asked exam topics.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★    | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** the **7 OSI layers in
order** (and their one-line jobs); **OSI vs TCP/IP** differences; **which layer does
what** (encryption? routing? MAC address? end-to-end delivery?); **PDU names** at
each layer (segment/packet/frame/bits); **encapsulation**; **which device works at
which layer** (hub/switch/router); protocol-to-layer matching (HTTP=App, IP=Network,
Ethernet=Data Link).

---

## 1.1 What Is a Computer Network? (first principles)

### Definition

A **computer network** is a set of **autonomous computing devices** connected by
communication links so they can **share data and resources**. "Autonomous" matters:
the machines are independent — none is the master of the others (that rules out, say,
a CPU and its dumb terminal).

Why network at all? Four classic goals:

1. **Resource sharing** — files, printers, compute, databases.
2. **Communication** — email, chat, video calls.
3. **Reliability** — replicate data so one failure isn't fatal.
4. **Scalability / cost** — many cheap machines beat one giant one.

> **Memory hook:** a network is a **postal system for data** — it takes a message
> from a sender, moves it hop by hop, and delivers it to the right receiver, even
> across the whole planet.

### Network types by scale (a favourite MCQ)

| Type | Scope | Example |
|---|---|---|
| **PAN** | ~1 m (personal) | Bluetooth earbuds |
| **LAN** | a building/campus | office Ethernet/Wi-Fi |
| **MAN** | a city | cable-TV / metro network |
| **WAN** | country/global | the **Internet** |

### MCQs

1. "Autonomous" in the network definition rules out? → a **master–slave** setup
   (e.g. CPU + dumb terminal).
2. A city-wide network is a? → **MAN**.
3. The Internet is a? → **WAN** (a network of networks).

---

## 1.2 Why Layering? (the single biggest idea in networking)

Networking is hugely complex: signals, addressing, routing, reliability,
encryption, applications. Doing it all in one giant program would be unmaintainable.
So we **divide the work into layers**, each with **one job** and a **clean interface**
to the layer above and below.

Benefits of layering (exam-ready list):

- **Modularity** — change one layer (e.g. Wi-Fi → Ethernet) without touching others.
- **Abstraction** — an app says "send these bytes"; it needn't know about cables.
- **Interoperability** — vendors that follow the same layer interface work together.
- **Easier troubleshooting** — isolate a fault to one layer.

> **Memory hook:** layering is like **sending a gift by courier** — you wrap the
> gift (App), put it in a box (Transport), write the address (Network), the courier
> loads the truck (Data Link), and the road carries it (Physical). Each person only
> does their own step.

### MCQs

1. Main benefit of layering? → **modularity** (change one layer independently).
2. Which principle lets an app ignore whether it's on Wi-Fi or Ethernet? →
   **abstraction**.

---

## 1.3 The OSI Model — 7 Layers (know these cold)

The **OSI (Open Systems Interconnection)** model, from ISO, is the **7-layer
reference model**. It's a *teaching/standard* model — real networks use TCP/IP — but
exams love OSI because it separates every job cleanly.

![The OSI 7-layer reference model beside the practical 4-layer TCP/IP model; OSI's top three layers all map to TCP/IP's Application layer.](images/01_osi_tcpip_layers.png)

**Top-to-bottom (Layer 7 → 1)** with the *one job* of each:

| # | Layer | One-line job | Example / protocol | PDU |
|---|---|---|---|---|
| 7 | **Application** | interface to the user's app | HTTP, DNS, SMTP, FTP | data |
| 6 | **Presentation** | translation, **encryption**, compression | TLS/SSL, JPEG, ASCII | data |
| 5 | **Session** | set up / manage / tear down sessions | NetBIOS, RPC | data |
| 4 | **Transport** | **end-to-end** delivery, ports, reliability | **TCP, UDP** | **segment** |
| 3 | **Network** | logical addressing + **routing** across networks | **IP**, routers | **packet** |
| 2 | **Data Link** | node-to-node delivery on one link, **MAC** | Ethernet, switches | **frame** |
| 1 | **Physical** | raw **bits** as signals on the medium | cables, hubs, NIC | bits |

> **Mnemonic (top→bottom):** **"All People Seem To Need Data Processing"**
> (Application, Presentation, Session, Transport, Network, Data Link, Physical).
> Bottom→top: **"Please Do Not Throw Sausage Pizza Away."**

### The exam traps — which layer does X?

- **Encryption / compression** → **Presentation (6)**.
- **Ports & end-to-end reliability (TCP)** → **Transport (4)**.
- **Routing & IP addressing** → **Network (3)**.
- **MAC address & error detection on a link** → **Data Link (2)**.
- **Bits / voltage / connectors** → **Physical (1)**.

### MCQs

1. Encryption is handled by which OSI layer? → **Presentation (Layer 6)**.
2. Routing happens at which layer? → **Network (Layer 3)**.
3. The PDU at the Transport layer is a? → **segment**.
4. MAC addresses live at which layer? → **Data Link (Layer 2)**.

---

## 1.4 The TCP/IP Model — What the Internet Actually Uses

The **TCP/IP model** is the practical model the Internet runs on. It **collapses
OSI's 7 into 4** (some books say 5, splitting Link into Data Link + Physical):

| TCP/IP layer | = OSI layers | Key protocols |
|---|---|---|
| **Application** | 7 + 6 + 5 | HTTP, DNS, SMTP, FTP, TLS |
| **Transport** | 4 | TCP, UDP |
| **Internet** | 3 | IP, ICMP, routers |
| **Link (Network Access)** | 2 + 1 | Ethernet, Wi-Fi, ARP |

### OSI vs TCP/IP (a guaranteed exam comparison)

| | OSI | TCP/IP |
|---|---|---|
| Layers | **7** | **4** (or 5) |
| Role | reference/teaching model | practical, in-use model |
| Developed | ISO | DARPA / IETF |
| Layer coupling | strict, well-defined | protocols came first, model after |
| Transport delivery | both CO and CL service | TCP (CO) + UDP (CL) |

> **Memory hook:** **OSI teaches, TCP/IP runs.** OSI's top three (Application,
> Presentation, Session) all fold into TCP/IP's single **Application** layer.

### MCQs

1. TCP/IP has how many layers? → **4** (or 5 if Link is split).
2. OSI's Presentation + Session + Application map to which TCP/IP layer? →
   **Application**.
3. Which model is "reference only"? → **OSI**.

---

## 1.5 Encapsulation — How Data Travels Down the Stack

When you send data, it moves **down** the sender's stack; each layer wraps it with
its own **header** (and Data Link adds a trailer too). At the receiver it moves
**up**, each layer stripping its header (**decapsulation**).

![Going down the stack, each layer wraps the data in its own header; the names change: data → segment → packet → frame → bits.](images/02_encapsulation.png)

The **PDU (Protocol Data Unit) names** are a classic one-mark question:

```text
Application data
   + TCP/UDP header      -> SEGMENT (Transport, L4)
   + IP header           -> PACKET / datagram (Network, L3)
   + Frame header+trailer-> FRAME (Data Link, L2)
   -> converted to       -> BITS (Physical, L1)
```

> **Memory hook (PDU ladder):** **"Some People Fear Birthdays"** — **S**egment,
> **P**acket, **F**rame, **B**its (top of transport → wire).

### MCQs

1. Data + TCP header = ? → **segment**.
2. Adding the IP header creates a? → **packet (datagram)**.
3. Decapsulation happens at the? → **receiver** (stripping headers going up).

---

## 1.6 Networking Devices by Layer (which box works where)

| Device | Layer | What it does |
|---|---|---|
| **Hub / repeater** | 1 Physical | dumb signal copier; one collision domain (obsolete) |
| **Switch / bridge** | 2 Data Link | forwards frames by **MAC address**; separates collision domains |
| **Router** | 3 Network | forwards packets between networks by **IP**; separates broadcast domains |
| **NIC** | 1–2 | the network card; has the **MAC address** |
| **Gateway / L7 proxy** | up to 7 | translates between protocols / apps (e.g. API gateway) |

> **Memory hook:** **Hub = broadcast to all; Switch = smart by MAC; Router = smart
> by IP (crosses networks).** As you go up a layer, the device gets "smarter."

### MCQs

1. A switch forwards using which address? → **MAC** (Layer 2).
2. Which device connects two different networks? → **router** (Layer 3).
3. A hub operates at which layer? → **Physical (Layer 1)**.

---

## 1.7 A Day in the Life of a Web Request (tying it together)

You type `https://example.com` and press Enter. Watch the layers work:

```text
1. Application : browser builds an HTTP GET request.
   (DNS first resolves example.com -> an IP address — Module 9.)
2. Presentation: TLS encrypts the request (HTTPS).
3. Transport  : TCP splits it into SEGMENTS, adds source/dest PORTS (443),
                and sets up a connection (3-way handshake — Module 7).
4. Network    : IP wraps each segment in a PACKET with source/dest IP;
                routers forward it hop by hop (Module 6).
5. Data Link  : each hop wraps the packet in a FRAME with MAC addresses;
                ARP finds the next hop's MAC (Module 4).
6. Physical   : bits go out as electrical/optical/radio signals.
```

At the server, the same stack runs **in reverse** (decapsulation) until the web
server reads your HTTP GET. This one example previews the entire course.

---

## 1.8 Connection-Oriented vs Connectionless, and Service Models

- **Connection-oriented (CO):** set up a path/handshake first, then send (reliable,
  ordered) — like a **phone call**. Example: **TCP**.
- **Connectionless (CL):** just send each packet independently — like **postcards**.
  Example: **UDP**, and IP itself.

Two more terms exams mix up:

- **Unicast** (one→one), **broadcast** (one→all), **multicast** (one→group),
  **anycast** (one→nearest of a group).
- **Simplex** (one direction), **half-duplex** (both, one at a time — walkie-talkie),
  **full-duplex** (both at once — phone).

### MCQs

1. TCP is connection-**oriented** or connection-**less**? → **oriented**.
2. Walkie-talkie communication is? → **half-duplex**.
3. One-to-nearest-member delivery is? → **anycast**.

---

## 1.9 Real-World & Backend Perspectives

- **Every API call** you make is this stack in action: your HTTP request (L7) rides
  TCP (L4) over IP (L3) over Ethernet/Wi-Fi (L2). Debugging "why is my service
  slow/unreachable" is literally **asking which layer failed**.
- **Tools by layer:** `ping`/`traceroute` (L3), `telnet`/`nc` to a port (L4),
  `curl` (L7), `ifconfig`/`ip` (L2/3), **Wireshark** (see every layer's header live).
- **Cloud/backend:** a load balancer is "L4 (TCP) vs L7 (HTTP)"; a CDN and API
  gateway live at L7; a VPC/router at L3. The OSI vocabulary is how infra is described.

---

## 1.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking TCP/IP has "no session/presentation layer functions." It
  does — they're just **inside the Application layer** (e.g. TLS does presentation's
  encryption).
- **Mistake:** confusing **Data Link (MAC, one link)** with **Network (IP,
  end-to-end)**. MAC = local hop; IP = the whole journey.
- **Trap:** a **switch is L2, a router is L3** — mixing these is the #1 device error.
- **Edge case:** layering costs a little overhead (headers, copies), but the
  modularity is worth it — the Internet scaled precisely *because* of clean layers.

---

## 1.11 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** expect direct one-markers — layer order, which-layer-does-X,
  PDU names, OSI vs TCP/IP, device-to-layer. High-frequency, easy marks — memorise.
- **GATE / C-DAC:** same plus subtle traps (which layer adds which header;
  connection-oriented vs -less; the exact protocol→layer mapping).
- **Interview:** "What happens when you type a URL and press Enter?" — answer with the
  §1.7 layer walkthrough; it's the most-asked networking interview question.

---

## 1.12 Concept Checks & MCQs (test yourself)

1. List the 7 OSI layers top to bottom. → **A, P, S, T, N, DL, Ph**.
2. Which two OSI layers does the TCP/IP **Link** layer cover? → **Data Link +
   Physical**.
3. Encryption is at which layer? → **Presentation (6)**.
4. PDU at Network layer? → **packet (datagram)**.
5. Router vs switch — layers? → **router = L3 (IP)**, **switch = L2 (MAC)**.
6. TCP vs UDP — connection type? → **TCP oriented**, **UDP connectionless**.
7. Adding headers going down the stack is called? → **encapsulation**.
8. The Internet is which network type by scale? → **WAN**.
9. Which layer provides **end-to-end** delivery and ports? → **Transport (4)**.
10. Full-duplex example? → a **phone call** (both talk at once).

---

## 1.13 One-Page Revision Sheet

```
NETWORK = autonomous devices sharing data/resources. Goals: sharing, comms, reliability, scale.
SCALE: PAN(1m) < LAN(building) < MAN(city) < WAN(global=Internet).

WHY LAYERS: modularity, abstraction, interoperability, easy debugging.

OSI 7 (top->bottom)  "All People Seem To Need Data Processing"
  7 Application   user apps        HTTP,DNS,SMTP,FTP
  6 Presentation  ENCRYPT/compress/translate  TLS,JPEG
  5 Session       sessions         RPC,NetBIOS
  4 Transport     END-TO-END, PORTS, reliability   TCP/UDP     PDU=SEGMENT
  3 Network       ROUTING + IP addressing          IP,router   PDU=PACKET
  2 Data Link     node-to-node, MAC, error-detect  Ethernet,switch  PDU=FRAME
  1 Physical      raw BITS/signals                 cables,hub,NIC   PDU=bits

TCP/IP 4: Application(=OSI 5-7) | Transport(4) | Internet(3) | Link(2+1).
  OSI=teaching(7, ISO); TCP/IP=runs the Internet(4, DARPA/IETF).

PDU ladder (down): DATA -> SEGMENT(+TCP) -> PACKET(+IP) -> FRAME(+MAC hdr/trailer) -> BITS.
  "Some People Fear Birthdays" = Segment, Packet, Frame, Bits.
  Encapsulation=wrap headers down; decapsulation=strip headers up.

DEVICES: Hub=L1(broadcast) | Switch/Bridge=L2(MAC, collision domains) |
  Router=L3(IP, broadcast domains) | NIC=L1-2(has MAC) | Gateway/proxy=up to L7.

CO vs CL: TCP=connection-oriented(phone); UDP/IP=connectionless(postcard).
CAST: unicast(1-1), broadcast(1-all), multicast(1-group), anycast(1-nearest).
DUPLEX: simplex | half(walkie-talkie) | full(phone).
```

### Flash cards

| Front | Back |
|-------|------|
| OSI layer count / mnemonic | 7 — "All People Seem To Need Data Processing" |
| Encryption layer | Presentation (6) |
| Routing layer | Network (3) |
| MAC-address layer | Data Link (2) |
| Ports & end-to-end layer | Transport (4) |
| PDU: Transport / Network / Data Link | segment / packet / frame |
| Switch vs router layer | L2 (MAC) vs L3 (IP) |
| TCP/IP layer count | 4 (or 5) |
| OSI 5–7 map to TCP/IP | Application |
| Add headers going down = | encapsulation |

### Spaced repetition
- **24-hour:** recite the 7 OSI layers + one job each + PDU names, from memory.
- **7-day:** OSI vs TCP/IP table; which-layer-does-X traps; device-to-layer.
- **30-day:** narrate "URL to page load" through all layers without notes.

---

## 1.14 Summary

A **computer network** connects autonomous devices to share data and resources,
ranging in scale from **PAN → LAN → MAN → WAN (the Internet)**. Because networking is
so complex, we split it into **layers**, each with one job — giving modularity,
abstraction, and interoperability. The **OSI model** defines **7 layers**
(Application, Presentation, Session, Transport, Network, Data Link, Physical), while
the **TCP/IP model** collapses these into the **4 layers** the Internet actually
runs. Data moves **down** the sender's stack via **encapsulation** — becoming a
**segment → packet → frame → bits** — and **up** the receiver's stack via
decapsulation. Different **devices** operate at different layers (**hub = L1, switch
= L2, router = L3**), and services are **connection-oriented (TCP)** or
**connectionless (UDP)**.

Next, **Module 2 — The Physical Layer & Transmission Media** goes to Layer 1: how
bits actually become signals on copper, fibre, and radio, and the limits (bandwidth,
Nyquist, Shannon) that cap how fast we can send.

> **You have mastered this module when** you can: recite the 7 OSI layers top-to-
> bottom with each layer's job and PDU; map OSI to TCP/IP; explain encapsulation and
> name the PDU at each layer; say which device works at which layer; and walk a web
> request through all seven layers — all without notes.
