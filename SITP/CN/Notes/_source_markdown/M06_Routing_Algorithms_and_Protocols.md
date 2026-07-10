---
title: "Module 6 — Routing Algorithms & Protocols"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — Routing Algorithms & Protocols

> **Where this module sits.**
> Module 5 gave each host an **IP address**. But how does a packet actually find its
> way across dozens of routers from source to destination? That is **routing** — the
> Network layer's second big job. This module covers the two core algorithm families
> (**distance-vector** with Bellman-Ford, and **link-state** with Dijkstra), the real
> protocols that run the Internet (**RIP, OSPF, BGP**), and the ideas that make routing
> scale (**autonomous systems, hierarchy, longest-prefix match**). Dijkstra/Bellman-Ford
> tracing and DV-vs-LS comparisons are frequent exam questions.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★★   | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **distance-vector vs
link-state**; **Bellman-Ford** vs **Dijkstra** (and tracing shortest paths);
**RIP** (hop count, max 15, count-to-infinity, split horizon); **OSPF** (link-state,
areas, cost); **BGP** (path-vector, inter-AS); **IGP vs EGP**; **longest-prefix
match**; hierarchical routing / autonomous systems.

---

## 6.1 Routing vs Forwarding (get this distinction right)

- **Routing** — the **control plane**: routers exchange information and **build the
  routing table** (which path to use for each destination). Runs in the background.
- **Forwarding** — the **data plane**: for each arriving packet, **look up the table
  and send it out the right interface**. Happens per-packet, at line speed.

> **Memory hook:** **routing = drawing the map (slow, occasional); forwarding =
> following the map for each car (fast, constant).**

A **routing table** maps a **destination prefix → next hop / outgoing interface**.
When several entries match, the router uses **longest-prefix match** (the most specific
prefix wins); a **default route** `0.0.0.0/0` catches everything else.

### MCQs

1. Building the routing table is? → **routing** (control plane).
2. Sending each packet using the table is? → **forwarding** (data plane).
3. Two entries match a destination — which wins? → the **longest prefix** (most
   specific).

---

## 6.2 Static vs Dynamic Routing

- **Static routing:** admin manually configures routes. Simple, secure, no overhead —
  but doesn't adapt to failures; fine for tiny/stub networks.
- **Dynamic routing:** routers **learn and adapt** automatically via a routing protocol
  (RIP/OSPF/BGP). Scales and self-heals, at the cost of protocol overhead.

Routing protocols pick paths by a **metric**: hop count (RIP), link cost/bandwidth
(OSPF), or policy + AS-path length (BGP).

### MCQs

1. Which routing adapts to link failures automatically? → **dynamic**.
2. RIP's metric? → **hop count**. OSPF's? → **cost (bandwidth-based)**.

---

## 6.3 Distance-Vector Routing (Bellman-Ford, RIP)

Each router keeps a **vector of distances** to every destination and **tells its
neighbours** its whole table. It updates using **Bellman-Ford**:

```
D_x(dest) = min over neighbours n of [ cost(x,n) + D_n(dest) ]
  "my distance = cheapest (link to a neighbour + that neighbour's distance)"
```

Routers exchange tables periodically; distances converge to the shortest paths.

- **RIP (Routing Information Protocol):** classic DV; metric = **hop count**, **max =
  15** (16 = unreachable → limits network size); updates every 30 s.
- **Problem — count-to-infinity:** when a link fails, bad news spreads slowly and
  routers can bounce increasing distances back and forth.
- **Fixes:** **split horizon** (don't advertise a route back to the neighbour you
  learned it from), **poison reverse** (advertise it back with distance ∞), **hold-down
  timers**.

> **Memory hook:** DV = **"routing by rumour"** — you only hear distances *from
> neighbours*, so bad news travels slowly (count-to-infinity).

### MCQs

1. DV algorithm? → **Bellman-Ford**.
2. RIP metric and max hops? → **hop count**, **15** (16 = unreachable).
3. Count-to-infinity fix that won't re-advertise a route to its source? → **split
   horizon**.

---

## 6.4 Link-State Routing (Dijkstra, OSPF)

Each router **learns the entire topology** (a map), then computes shortest paths
itself with **Dijkstra**.

![Every router floods its links to all others, builds the full map, and runs Dijkstra to find shortest paths (here A=0, B=2, C=3, D=5, E=8).](images/17_dijkstra_routing.png)

How it works:

1. **Discover neighbours** and measure link costs.
2. **Flood** a **Link-State Advertisement (LSA)** to *every* router (so all share the
   same map / link-state database).
3. Each router runs **Dijkstra (SPF)** to build its **shortest-path tree** and fill its
   routing table.

- **OSPF (Open Shortest Path First):** the dominant IGP; link-state; metric = **cost**
  (inversely proportional to bandwidth); groups routers into **areas** (hierarchy) with
  a backbone **area 0**; fast convergence, no routing loops.

> **Memory hook:** LS = **"everyone gets the same map, then each finds its own shortest
> path."** Floods *link states*, not distances.

### Distance-Vector vs Link-State (the guaranteed comparison)

![Distance vector tells neighbours about all destinations (Bellman-Ford, slow convergence); link state floods its links to everyone (Dijkstra, fast convergence).](images/18_dv_vs_ls.png)

| | Distance-Vector (RIP) | Link-State (OSPF) |
|---|---|---|
| Knows | distances via neighbours | the **whole topology** |
| Tells | its table to **neighbours** | its links to **everyone** (flood) |
| Algorithm | **Bellman-Ford** | **Dijkstra** |
| Convergence | slow (count-to-infinity) | **fast**, loop-free |
| Resources | low CPU/memory | more CPU/memory + flooding |

> **Memory hook:** **DV = "tell your neighbours about the whole world"; LS = "tell the
> whole world about your neighbours."**

### MCQs

1. LS algorithm and a real protocol? → **Dijkstra**, **OSPF**.
2. What does a router flood in link-state? → its **LSA (link states)**.
3. OSPF's metric? → **cost** (∝ 1/bandwidth). Backbone area? → **area 0**.
4. Which converges faster, DV or LS? → **link-state**.

---

## 6.5 Path-Vector Routing & BGP (the Internet's glue)

The Internet is a network of **Autonomous Systems (AS)** — networks under one
administration (an ISP, a company). Routing has two levels:

![Inside an AS an interior protocol (OSPF/RIP) runs; between ASes, BGP — a path-vector protocol — exchanges reachability and enforces policy.](images/19_as_bgp.png)

- **IGP (Interior Gateway Protocol)** — routing **inside** one AS: **OSPF, RIP,
  EIGRP**.
- **EGP (Exterior Gateway Protocol)** — routing **between** ASes: **BGP** (the only one
  in use).

**BGP (Border Gateway Protocol)** is a **path-vector** protocol: it advertises the full
**AS-path** to each destination (so loops are detected by seeing your own AS in the
path), and chooses routes by **policy** (business relationships), not just shortest
distance. BGP is what makes the global Internet route.

> **Memory hook:** **inside an AS = IGP (OSPF/RIP); between ASes = BGP.** BGP carries
> the **AS-path** and is **policy-driven**, not shortest-hop.

### MCQs

1. Routing between autonomous systems uses? → **BGP** (path-vector, EGP).
2. How does BGP detect loops? → sees its **own AS in the AS-path**.
3. OSPF and RIP are which category? → **IGP** (interior).

---

## 6.6 Other Routing Ideas (quick but tested)

- **Flooding:** send an incoming packet out **every** link except the one it came on;
  guaranteed delivery but wasteful — controlled by TTL/sequence numbers (used by LS to
  distribute LSAs).
- **Hierarchical routing:** group routers into regions/areas so tables stay small
  (OSPF areas; the Internet's AS structure) — essential for scale.
- **Broadcast/Multicast routing:** deliver to all / a group (spanning trees, reverse-
  path forwarding; protocols like IGMP/PIM).
- **Anycast:** route to the **nearest** of several identical servers (how DNS root
  servers and CDNs work).

### MCQs

1. Sending a packet out every link but the source is? → **flooding**.
2. What keeps routing tables small as the Internet grows? → **hierarchy** (areas/ASes).
3. Routing to the nearest of many identical servers? → **anycast**.

---

## 6.7 Real-World & Backend Perspectives

- **BGP runs the Internet** — and BGP misconfigurations cause real global outages
  (route leaks/hijacks that redirect traffic). Backend/SRE on-call knows BGP.
- **OSPF/link-state inside data centers** (and modern designs like BGP-in-the-DC) keep
  large fabrics converging fast.
- **Anycast + longest-prefix match** is how CDNs and DNS send you to the nearest edge —
  the routing concepts here directly power low-latency delivery (M12).

---

## 6.8 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** swapping algorithms — **DV = Bellman-Ford, LS = Dijkstra** (not the
  reverse).
- **Mistake:** thinking RIP scales — **max 15 hops** deliberately limits it to small
  networks.
- **Trap:** BGP is **not** shortest-path; it is **policy/AS-path** based.
- **Edge case:** DV's **count-to-infinity** needs split horizon / poison reverse; LS
  avoids it but pays with flooding + CPU.

---

## 6.9 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** DV vs LS, which protocol is which (RIP/OSPF/BGP), IGP vs EGP,
  RIP hop limit, what BGP does.
- **GATE / C-DAC:** trace **Dijkstra/Bellman-Ford** on a given graph; count-to-infinity;
  longest-prefix match; metric definitions.
- **Interview:** "how does the Internet route between networks?" → AS + BGP; "OSPF vs
  RIP?" → link-state/Dijkstra/fast vs distance-vector/hop-count/slow.

---

## 6.10 Concept Checks & MCQs (test yourself)

1. Routing vs forwarding? → **build table (control)** vs **use table per packet (data)**.
2. DV and LS algorithms? → **Bellman-Ford** and **Dijkstra**.
3. RIP metric & hop limit? → **hop count**, **15**.
4. OSPF type & metric? → **link-state**, **cost (∝1/bandwidth)**.
5. Inter-AS protocol & type? → **BGP**, **path-vector**.
6. Two count-to-infinity fixes? → **split horizon**, **poison reverse**.
7. Multiple matching routes — selection rule? → **longest-prefix match**.
8. What does LS flood? → **LSAs (link states)**.
9. IGP examples? → **OSPF, RIP (, EIGRP)**.
10. Which converges faster? → **link-state (OSPF)**.

---

## 6.11 One-Page Revision Sheet

```
ROUTING (control plane) = build table.  FORWARDING (data plane) = use table per packet.
  table: dest prefix -> next hop. LONGEST-PREFIX MATCH wins. default = 0.0.0.0/0.
STATIC (manual) vs DYNAMIC (protocol; adapts). metric: hop(RIP)/cost(OSPF)/policy(BGP).

DISTANCE VECTOR (RIP): Bellman-Ford  Dx(d)=min_n[cost(x,n)+Dn(d)].
  tell NEIGHBOURS your table. "routing by rumour" -> slow, COUNT-TO-INFINITY.
  fixes: split horizon, poison reverse, hold-down. RIP hop metric, MAX 15 (16=unreachable), 30s.

LINK STATE (OSPF): learn WHOLE map -> flood LSAs -> Dijkstra (SPF) -> shortest-path tree.
  fast convergence, loop-free, more CPU/mem. cost ~ 1/bandwidth. areas + backbone AREA 0.

DV vs LS: "tell neighbours about the world" vs "tell the world about your neighbours".

PATH VECTOR (BGP): between AUTONOMOUS SYSTEMS. carries AS-PATH (loop detect = own AS in path),
  POLICY-based (not shortest). IGP=inside AS (OSPF/RIP/EIGRP) | EGP=between AS (BGP).

OTHER: flooding(all links but source) | hierarchy(areas/AS -> scale) | anycast(nearest server).
```

### Flash cards

| Front | Back |
|-------|------|
| DV algorithm / protocol | Bellman-Ford / RIP |
| LS algorithm / protocol | Dijkstra / OSPF |
| RIP metric & max hops | hop count; 15 |
| OSPF metric & backbone | cost (∝1/BW); area 0 |
| Inter-AS protocol & type | BGP; path-vector |
| Count-to-infinity fixes | split horizon, poison reverse |
| Multiple route match rule | longest-prefix match |
| IGP vs EGP | inside AS vs between ASes |
| Routing vs forwarding | build table vs use table |
| BGP route selection basis | policy + AS-path (not shortest) |

### Spaced repetition
- **24-hour:** trace Dijkstra and Bellman-Ford on a small weighted graph.
- **7-day:** DV vs LS table; RIP limits & count-to-infinity fixes; IGP vs EGP.
- **30-day:** explain end-to-end how a packet is routed across two ASes (IGP + BGP) —
  without notes.

---

## 6.12 Summary

**Routing** (control plane) builds the table; **forwarding** (data plane) uses it per
packet, choosing the **longest-prefix match**. Routes are **static** or **dynamic**.
**Distance-vector** protocols (**RIP**) run **Bellman-Ford**, telling neighbours their
distance vectors — simple but slow, with **count-to-infinity** (fixed by split horizon /
poison reverse) and a **15-hop** limit. **Link-state** protocols (**OSPF**) flood
**LSAs** so every router has the full map, then run **Dijkstra** for fast, loop-free
paths, organised into **areas**. Between **autonomous systems**, **BGP** (a
**path-vector**, **policy-driven** protocol carrying the **AS-path**) routes the global
Internet — an **IGP** runs inside an AS, **BGP** (EGP) between them. Hierarchy,
flooding, and anycast round out how routing **scales**.

Next, **Module 7 — The Transport Layer (TCP & UDP)** climbs to Layer 4: ports and
sockets, UDP vs TCP, the **three-way handshake**, connection teardown, and reliable
delivery.

> **You have mastered this module when** you can: separate routing from forwarding and
> apply longest-prefix match; trace Dijkstra and Bellman-Ford; contrast DV vs LS and
> name their algorithms/protocols; state RIP's limits and count-to-infinity fixes; and
> explain IGP vs EGP and BGP's path-vector, policy-based role — all without notes.
