---
title: "Module 12 — Modern Networking: SDN, CDN & Cloud"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 12 — Modern Networking: SDN, CDN & Cloud

> **Where this module sits.**
> Modules 1–11 covered the classic protocol stack. But the Internet you use today is
> shaped by a few **modern** ideas layered on top: **SDN** (software-defined
> networking), **CDNs** and **load balancing** (how services scale to billions),
> **cloud/virtual networks**, and new transport like **QUIC/HTTP-3**. These tie the
> theory to how real systems are built — high value for interviews and backend roles,
> and increasingly appearing in exams.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★      | ★★     | ★★      | ★★★★      | ★★★★★   |

**Most-asked concepts:** **SDN** (control vs data plane, controller, OpenFlow); **CDN**
(edge caching, why latency); **load balancing** (L4 vs L7, algorithms); **NAT/VPC/cloud
networking**; **QUIC / HTTP-3**; **network virtualization** (overlays, VXLAN); **anycast**.

---

## 12.1 Software-Defined Networking (SDN)

Traditionally every router/switch runs **both** the control logic (deciding routes) and
the forwarding (moving packets). **SDN separates them:**

![SDN separates the control plane (a central programmable controller) from the data plane (dumb, fast switches), programmed via a southbound API like OpenFlow.](images/33_sdn.png)

- **Control plane → a central SDN controller** (the "brain"): programmable, holds the
  global view and policy.
- **Data plane → dumb, fast switches**: they just forward, following tables the
  controller installs (via a **southbound API** like **OpenFlow**).
- **Northbound API:** apps/orchestrators tell the controller what they want.

**Benefits:** central control, **programmability/automation**, faster changes, vendor
independence. **NFV (Network Function Virtualization)** is the cousin: run firewalls/
load-balancers as **software** on commodity servers instead of dedicated boxes.

> **Memory hook:** **SDN = "smart central brain + dumb fast switches."** Decouple the
> *decision* (control plane) from the *forwarding* (data plane).

### MCQs

1. SDN separates which two planes? → **control** and **data**.
2. Protocol the controller uses to program switches? → **OpenFlow** (southbound).
3. Running network functions as software = ? → **NFV**.

---

## 12.2 CDN & Anycast — Beating Latency

Latency has a hard floor (**speed of light**), so you can't make a far server fast — you
**move the content closer**. A **CDN (Content Delivery Network)** caches static content
at **edge servers (PoPs)** around the world.

![A CDN caches copies at edge PoPs worldwide; each user is served from the nearest edge, cutting latency and offloading the origin.](images/34_cdn.png)

- Users are routed to the **nearest edge** via **anycast** or **GeoDNS**.
- Benefits: **lower latency**, **less origin load**, **DDoS absorption**, higher
  availability. Examples: Cloudflare, Akamai, CloudFront.

> **Memory hook:** **you can't beat the speed of light — so cache the content next
> door.** CDN = the Internet's local warehouses.

### MCQs

1. A CDN reduces latency by? → serving from an **edge near the user**.
2. How are users sent to the nearest edge? → **anycast / GeoDNS**.
3. A CDN also helps against? → **DDoS** and **origin load**.

---

## 12.3 Load Balancing

A **load balancer (LB)** spreads incoming requests across many backend servers for
scale and availability.

- **L4 (transport) LB:** routes by **IP + port** (fast, protocol-agnostic; e.g. AWS NLB,
  LVS). Doesn't see the HTTP content.
- **L7 (application) LB:** routes by **HTTP content** (URL path, host, cookies) — enables
  smart routing, TLS termination, caching (e.g. Nginx, HAProxy, AWS ALB).
- **Algorithms:** round-robin, least-connections, weighted, IP-hash (sticky sessions).
- **Health checks** remove dead servers; this is how services stay up.

> **Memory hook:** **L4 = route by IP:port (fast, blind); L7 = route by URL/headers
> (smart, HTTP-aware).**

### MCQs

1. L4 vs L7 load balancer routes by? → **IP:port** vs **HTTP content (URL/headers)**.
2. Which LB can do TLS termination & path routing? → **L7**.
3. What removes a failed backend from rotation? → **health checks**.

---

## 12.4 Cloud & Virtual Networking

Cloud networking recreates all the classic concepts **in software**:

- **VPC (Virtual Private Cloud):** your own isolated network in the cloud — a **CIDR
  block** (M5) split into **subnets** (public/private) per availability zone.
- **Overlays / tunnelling:** **VXLAN**, GRE, and SDN build **virtual networks** on top
  of the physical one (multi-tenant isolation).
- **Security groups / NACLs** = cloud firewalls (M10). **NAT gateways**, **elastic IPs**,
  **private links**, and **DNS-based service discovery** wire it together.

> **Memory hook:** **the cloud is your networking course, virtualized** — VPC = your
> network, subnets = M5, security groups = firewalls, overlays = SDN tunnels.

### MCQs

1. Your isolated cloud network defined by a CIDR block? → a **VPC**.
2. Cloud firewall at the instance level? → **security group**.
3. Tech that builds virtual L2 networks over L3? → **VXLAN** (overlay).

---

## 12.5 Modern Transport — QUIC & HTTP/3

**QUIC** is a transport built on **UDP** (in user space) that powers **HTTP/3**:

- **Faster setup:** combines transport + TLS handshake → **0-/1-RTT** connections.
- **No head-of-line blocking:** independent **streams** (TCP would stall all streams on
  one lost packet).
- **Connection migration:** survives an IP change (Wi-Fi → cellular) via a connection ID.

This is why big providers moved to HTTP/3 — lower latency, better on lossy/mobile links.

### MCQs

1. QUIC runs over? → **UDP** (user space).
2. HTTP version over QUIC? → **HTTP/3**.
3. QUIC's advantage over TCP for many streams? → **no head-of-line blocking**.

---

## 12.6 Real-World & Backend Perspectives

- **This is the day-to-day of backend/SRE:** DNS → CDN → L7 load balancer → API gateway
  → services (M13). SDN/overlays run inside every cloud; QUIC/HTTP-3 is default for
  Google/Meta/Cloudflare.
- **Anycast + CDN + BGP** (M6) is how content gets to you fast and survives outages.
- **Observability** (latency, p99, retries) is how you actually operate all this.

---

## 12.7 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking a CDN speeds up **dynamic/personalised** content — it mainly
  caches **static** assets (though edge compute is changing this).
- **Mistake:** L4 can inspect URLs — no, only **L7** sees HTTP content.
- **Trap:** SDN centralizes the **control plane**, not the forwarding — switches still
  forward at line rate.
- **Edge case:** QUIC over UDP can be **blocked/throttled** by some middleboxes → clients
  fall back to TCP/HTTP-2.

---

## 12.8 Exam, Interview & Coding Perspectives

- **Exams:** SDN control/data plane + OpenFlow, CDN purpose, L4 vs L7, QUIC/HTTP-3
  basics.
- **Interview (backend-heavy):** "how would you scale a web service?" (CDN + LB +
  caching + horizontal scaling), "L4 vs L7 LB?", "why HTTP/3?", "what's a VPC?".

---

## 12.9 Concept Checks & MCQs (test yourself)

1. SDN planes separated? → **control** vs **data**.
2. Southbound protocol? → **OpenFlow**.
3. CDN reduces latency how? → **edge caching near users**.
4. L4 vs L7 LB? → **IP:port** vs **HTTP content**.
5. Cloud isolated network? → **VPC** (a CIDR block).
6. QUIC transport & HTTP version? → **UDP**, **HTTP/3**.
7. QUIC benefit over TCP? → **no head-of-line blocking** + faster handshake.
8. NFV means? → network functions **as software**.
9. Route users to nearest edge via? → **anycast / GeoDNS**.
10. Overlay tech for virtual networks? → **VXLAN**.

---

## 12.10 One-Page Revision Sheet

```
SDN: separate CONTROL plane (central programmable CONTROLLER = brain) from DATA plane (dumb fast switches).
  southbound=OpenFlow (controller -> switches); northbound=apps -> controller. NFV = net functions as software.

CDN: cache STATIC content at EDGE PoPs near users (anycast/GeoDNS route to nearest). cuts latency + origin load + DDoS.
  (latency floor = speed of light -> move content closer.)

LOAD BALANCER: L4 = route by IP:port (fast, blind) | L7 = route by URL/headers (smart, TLS term, path routing).
  algos: round-robin, least-conn, weighted, IP-hash(sticky). health checks remove dead servers.

CLOUD NET: VPC = your CIDR network -> subnets (public/private). security groups/NACL = firewalls. VXLAN/GRE overlays. NAT gw.

QUIC/HTTP-3: transport over UDP (user space). 0/1-RTT handshake (transport+TLS), independent STREAMS (no HoL blocking),
  connection migration (Wi-Fi<->cellular). = HTTP/3.
```

### Flash cards

| Front | Back |
|-------|------|
| SDN planes | control (controller) vs data (switches) |
| SDN southbound API | OpenFlow |
| CDN benefit | edge caching → low latency |
| Route to nearest edge | anycast / GeoDNS |
| L4 vs L7 LB | IP:port vs HTTP content |
| VPC | cloud CIDR network |
| QUIC transport | UDP (user space) |
| HTTP/3 over | QUIC |
| QUIC vs TCP win | no head-of-line blocking |
| VXLAN | network overlay |

### Spaced repetition
- **24-hour:** SDN control/data split; L4 vs L7; QUIC over UDP.
- **7-day:** CDN + anycast; VPC/security groups; HTTP/3 benefits.
- **30-day:** design "scale a web app" using CDN + LB + cache + VPC — without notes.

---

## 12.11 Summary

Modern networking layers powerful ideas on the classic stack. **SDN** splits the
**control plane** (a central programmable **controller**, via **OpenFlow**) from the
**data plane** (dumb fast switches), enabling automation; **NFV** virtualizes network
functions. **CDNs** cache static content at **edge PoPs**, routing users to the nearest
via **anycast/GeoDNS** to beat the speed-of-light latency floor. **Load balancers**
(**L4** by IP:port, **L7** by HTTP content) scale services with health checks. **Cloud
networking** re-implements the course in software (**VPC**, subnets, security groups,
**VXLAN** overlays). And **QUIC/HTTP-3** (over **UDP**) delivers faster handshakes,
stream independence, and connection migration.

Next, **Module 13 — The Backend/Distributed-Systems Perspective** shows exactly how all
these networking pieces assemble into a real, scalable system.

> **You have mastered this module when** you can: explain SDN's control/data split and
> OpenFlow; say why CDNs cut latency and how users reach the nearest edge; contrast L4 vs
> L7 load balancing; describe a VPC; and list QUIC/HTTP-3's advantages — all without
> notes.
