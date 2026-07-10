---
title: "Module 9 — The Application Layer (DNS, HTTP, Email, DHCP)"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 9 — The Application Layer (DNS, HTTP, Email, DHCP)

> **Where this module sits.**
> We've climbed the whole stack — physical (M2), link (M3–M4), network (M5–M6),
> transport (M7–M8). Now we reach the top: **Layer 7, the Application layer**, where the
> protocols you actually use live — **DNS** (names → IPs), **HTTP/HTTPS** (the web),
> **email** (SMTP/IMAP/POP3), **FTP**, and **DHCP** (auto-configuration). These map
> directly to everyday tools and are heavily tested (which protocol, which port, which
> transport, request/response behaviour).

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★   | ★★★★    | ★★★★      | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **DNS** (hierarchy, recursive
vs iterative, record types, port 53/UDP); **HTTP** methods & status codes, stateless +
cookies, HTTP/1.1 vs 2 vs 3; **HTTPS**; **email** (SMTP send vs IMAP/POP3 retrieve);
**FTP** (control/data, port 20/21); **DHCP** (DORA, ports 67/68); client-server vs P2P;
protocol → port → transport mapping.

---

## 9.1 Application Architectures & the Layer's Job

The Application layer provides **network services directly to user programs** (it does
**not** include the apps themselves — the browser is the app; **HTTP** is the layer's
protocol). Two architectures:

- **Client-server:** clients request, a always-on **server** responds (web, email, DNS).
- **Peer-to-peer (P2P):** peers act as both client and server (BitTorrent, blockchain);
  scales with users, no central server.

Most protocols run over **TCP** (reliability) or **UDP** (speed) — knowing which is a
classic exam point.

### MCQs

1. Is the web browser the "application layer"? → no — the **protocol (HTTP)** is; the
   browser is the app.
2. BitTorrent uses which architecture? → **P2P**.
3. Always-on host that answers requests? → **server**.

---

## 9.2 DNS — the Internet's Phone Book

**DNS (Domain Name System)** translates human names (`example.com`) into **IP
addresses**. It's a **distributed, hierarchical** database, queried over **UDP port 53**
(TCP 53 for large responses / zone transfers).

![DNS resolves a name by walking the hierarchy: the recursive resolver queries root → TLD → authoritative servers, then caches the answer.](images/25_dns_resolution.png)

**The hierarchy:** **root (.)** → **TLD (.com, .org, .in)** → **authoritative** server
for the domain. Resolution:

- Your PC (stub) asks its **recursive resolver** (ISP/8.8.8.8) — a **recursive** query.
- The resolver walks root → TLD → authoritative with **iterative** queries, then returns
  the IP and **caches** it (**TTL**-bounded).

**Common record types:** **A** (name→IPv4), **AAAA** (→IPv6), **CNAME** (alias), **MX**
(mail server), **NS** (nameserver), **PTR** (reverse: IP→name), **TXT** (SPF/verify).

> **Memory hook:** **PC→resolver = recursive ("you do all the work"); resolver→servers
> = iterative ("go ask them"); everything is cached.** DNS = phone book of the Internet.

### MCQs

1. DNS port & transport? → **53**, mostly **UDP**.
2. Recursive vs iterative? → PC→resolver = **recursive**; resolver→servers = **iterative**.
3. Record for a mail server / IPv4 / alias? → **MX / A / CNAME**.
4. What bounds how long a record is cached? → its **TTL**.

---

## 9.3 HTTP & HTTPS — the Web

**HTTP (HyperText Transfer Protocol)** is a **stateless, text-based request/response**
protocol over **TCP port 80** (**HTTPS** = HTTP over **TLS**, port **443**).

![HTTP request/response: the client sends a method + URL + headers; the server returns a status code + headers + body. Stateless, so cookies/tokens add state.](images/26_http.png)

- **Methods:** **GET** (read), **POST** (create/submit), **PUT** (replace), **PATCH**
  (partial update), **DELETE**, **HEAD** (headers only).
- **Status codes:** **1xx** info, **2xx** success (200 OK), **3xx** redirect (301/302),
  **4xx** client error (**400** bad request, **401** unauthorized, **403** forbidden,
  **404** not found), **5xx** server error (**500**, **502/503**).
- **Stateless** → state added via **cookies**, **sessions**, or **tokens (JWT)**.
- **Versions:** **HTTP/1.1** (persistent connections, one request at a time per
  connection → head-of-line blocking); **HTTP/2** (**multiplexing** many streams on one
  TCP connection, header compression); **HTTP/3** (over **QUIC/UDP**, removes TCP
  head-of-line blocking).

> **Memory hook:** **request (method + URL + headers) → response (status + headers +
> body).** 2xx good, 4xx *your* fault, 5xx *server's* fault.

### MCQs

1. HTTP/HTTPS ports? → **80 / 443**.
2. 404 vs 500? → **client error (not found)** vs **server error**.
3. What makes HTTP stateful? → **cookies / sessions / tokens** (HTTP itself is
   stateless).
4. HTTP/2's key improvement? → **multiplexing** (many streams per connection).

---

## 9.4 Email — SMTP, IMAP, POP3

Email uses **different protocols to send vs retrieve**:

| Protocol | Job | Port |
|---|---|---|
| **SMTP** | **send** / relay mail (client→server, server→server) | 25 (587 submit) |
| **POP3** | **download** mail to one device (then usually deletes from server) | 110 |
| **IMAP** | **sync** mail across devices (stays on server, folders) | 143 |

> **Memory hook:** **SMTP pushes (sends); POP3/IMAP pull (retrieve).** POP3 =
> download-and-go (one device); IMAP = stay-in-sync (many devices). MIME lets email
> carry attachments/non-text.

### MCQs

1. Protocol to **send** email? → **SMTP** (port 25).
2. POP3 vs IMAP? → POP3 **downloads (single device)**; IMAP **syncs (multi-device)**.
3. What lets email carry attachments? → **MIME**.

---

## 9.5 FTP & Other Protocols

- **FTP (File Transfer Protocol):** two connections — **control (port 21)** for commands
  and **data (port 20)** for the file. **Not encrypted** (use **SFTP**/FTPS). Active vs
  passive mode differ in who opens the data connection.
- **Telnet** (remote login, insecure) → replaced by **SSH (port 22, encrypted)**.
- **SNMP** (network management), **NTP** (time sync), **LDAP** (directory).

### MCQs

1. FTP control vs data ports? → **21 (control) / 20 (data)**.
2. Secure replacement for Telnet? → **SSH (22)**.
3. FTP uses how many connections? → **two** (control + data).

---

## 9.6 DHCP — Automatic IP Configuration

**DHCP (Dynamic Host Configuration Protocol)** auto-assigns a host its **IP address,
subnet mask, default gateway, and DNS servers** — no manual setup. It uses the **DORA**
exchange over **UDP ports 67 (server) / 68 (client)**:

![DHCP DORA: the client broadcasts DISCOVER, a server sends OFFER, the client sends REQUEST, and the server confirms with ACK — leasing an IP plus gateway/DNS/mask.](images/27_dhcp_dora.png)

1. **Discover** — client broadcasts "any DHCP server?"
2. **Offer** — server offers an IP + lease.
3. **Request** — client requests that offer (broadcast, so other servers withdraw).
4. **Acknowledge** — server confirms; the **lease** begins (and is renewed later).

> **Memory hook:** **DORA — Discover, Offer, Request, Acknowledge.** It's broadcast-based
> (the client has no IP yet) and gives you *everything* to get online.

### MCQs

1. DHCP four steps? → **DORA** (Discover, Offer, Request, Acknowledge).
2. DHCP ports? → **67 (server) / 68 (client)**, UDP.
3. Besides an IP, DHCP provides? → **subnet mask, gateway, DNS** (and lease time).

---

## 9.7 Protocol → Port → Transport (memorise this table)

| Protocol | Port | Transport | Purpose |
|---|---|---|---|
| HTTP / HTTPS | 80 / 443 | TCP | web |
| DNS | 53 | **UDP** (TCP for big) | name resolution |
| SMTP | 25 | TCP | send email |
| POP3 / IMAP | 110 / 143 | TCP | retrieve email |
| FTP | 20 / 21 | TCP | file transfer |
| SSH / Telnet | 22 / 23 | TCP | remote login |
| DHCP | 67 / 68 | **UDP** | auto IP config |
| SNMP | 161 | UDP | management |

### MCQs

1. Which of these use UDP? → **DNS, DHCP, SNMP** (rest TCP).
2. HTTPS vs SSH ports? → **443 / 22**.

---

## 9.8 Real-World & Backend Perspectives

- **DNS is the first step of almost every request** — and a top outage cause ("it's
  always DNS"). Backend adds CDNs, GeoDNS, and health-checked records.
- **HTTP is the backend lingua franca** — REST APIs, status codes, headers, caching,
  cookies/JWT for auth; HTTP/2 & HTTP/3 (QUIC) cut latency.
- **DHCP + DNS + NAT (M5)** are what silently get every device online.
- **These app protocols ride the transport you learned in M7** — HTTP/SMTP/FTP on TCP;
  DNS/DHCP on UDP.

---

## 9.9 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking DNS is TCP — it's **UDP 53** normally (TCP only for large/zone
  transfers).
- **Mistake:** SMTP retrieves mail — no, **SMTP sends**; **IMAP/POP3 retrieve**.
- **Trap:** 4xx = **client** error, 5xx = **server** error (don't swap).
- **Edge case:** HTTP is **stateless** by design; all "logged-in" state is bolted on via
  cookies/tokens — a frequent interview clarification.

---

## 9.10 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** protocol→port→transport table, DNS/DHCP basics, SMTP vs
  IMAP/POP3, HTTP status codes.
- **GATE / C-DAC:** DNS recursive/iterative + caching, HTTP persistent/non-persistent
  connection RTT counting, FTP two-connection model, DORA.
- **Interview:** "what happens when you type a URL?" (DNS → TCP → TLS → HTTP — ties the
  whole course), "GET vs POST", "how does DNS work?", "stateless HTTP + sessions".

---

## 9.11 Concept Checks & MCQs (test yourself)

1. DNS transport/port? → **UDP 53**.
2. Recursive vs iterative query? → PC→resolver **recursive**; resolver→servers
   **iterative**.
3. HTTP methods for read/create? → **GET / POST**.
4. 401 vs 403 vs 404? → **unauthorized / forbidden / not found**.
5. Send vs retrieve email protocols? → **SMTP** vs **IMAP/POP3**.
6. FTP ports? → **21 control, 20 data**.
7. DHCP steps & ports? → **DORA**, **67/68 UDP**.
8. HTTP/3 runs over? → **QUIC (UDP)**.
9. Record types A/MX/CNAME? → **IPv4 / mail / alias**.
10. Which use UDP: HTTP, DNS, SMTP, DHCP? → **DNS, DHCP**.

---

## 9.12 One-Page Revision Sheet

```
APPLICATION LAYER (L7): services to apps (protocol != the app). client-server vs P2P. PDU=data/message.

DNS (UDP 53): name->IP, distributed hierarchy root(.) -> TLD(.com) -> authoritative.
  PC->resolver = RECURSIVE; resolver->servers = ITERATIVE. CACHED (TTL).
  records: A(IPv4) AAAA(IPv6) CNAME(alias) MX(mail) NS(nameserver) PTR(reverse) TXT.

HTTP (TCP 80) / HTTPS (TLS 443): stateless request/response.
  methods: GET POST PUT PATCH DELETE HEAD. status: 2xx ok/3xx redirect/4xx client(404)/5xx server(500).
  state via cookies/sessions/JWT. HTTP1.1 persistent; HTTP2 multiplex; HTTP3 over QUIC/UDP.

EMAIL: SMTP(25) SEND/relay ; POP3(110) download-one-device ; IMAP(143) sync-multi-device. MIME=attachments.
FTP: control 21 + data 20 (two connections, unencrypted -> SFTP/FTPS). SSH(22) replaces Telnet(23).
DHCP (UDP 67/68): DORA = Discover(broadcast) -> Offer -> Request -> Acknowledge. gives IP+mask+gateway+DNS+lease.

PORT/TRANSPORT: HTTP80/HTTPS443/DNS53(UDP)/SMTP25/POP110/IMAP143/FTP20-21/SSH22/DHCP67-68(UDP)/SNMP161(UDP).
UDP ones: DNS, DHCP, SNMP.  everything else TCP.
```

### Flash cards

| Front | Back |
|-------|------|
| DNS port / transport | 53 / UDP |
| Recursive vs iterative | PC→resolver vs resolver→servers |
| MX / A / CNAME record | mail / IPv4 / alias |
| HTTP vs HTTPS port | 80 / 443 |
| 4xx vs 5xx | client error vs server error |
| Send vs retrieve email | SMTP vs IMAP/POP3 |
| FTP ports | 21 control, 20 data |
| DHCP steps & ports | DORA; 67/68 UDP |
| HTTP/3 transport | QUIC (UDP) |
| App protocols on UDP | DNS, DHCP, SNMP |

### Spaced repetition
- **24-hour:** recite the protocol→port→transport table + DORA + HTTP status classes.
- **7-day:** DNS recursive/iterative + record types; SMTP vs IMAP/POP3; HTTP versions.
- **30-day:** narrate "type a URL → page loads" touching DNS, TCP, TLS, HTTP — without
  notes.

---

## 9.13 Summary

The **Application layer** gives programs their network protocols. **DNS** (UDP 53)
resolves names via a **hierarchy** (root → TLD → authoritative) using **recursive**
(PC→resolver) and **iterative** (resolver→servers) queries with **caching**. **HTTP**
(TCP 80) / **HTTPS** (TLS 443) is a **stateless** request/response protocol with
**methods** (GET/POST/…), **status codes** (2xx/3xx/4xx/5xx), and cookies/tokens for
state — evolving through **HTTP/1.1 → 2 (multiplexing) → 3 (QUIC/UDP)**. **Email** splits
into **SMTP** (send) and **IMAP/POP3** (retrieve); **FTP** uses **two connections**
(21/20); **DHCP** auto-configures hosts via **DORA** (UDP 67/68). The **protocol → port
→ transport** table ties it together — with **DNS, DHCP, SNMP on UDP** and the rest on
TCP.

Next, **Module 10 — Network Security & Cryptography** covers how we protect all this:
symmetric/asymmetric encryption, **TLS/HTTPS**, firewalls, VPNs, and common attacks.

> **You have mastered this module when** you can: explain DNS resolution (recursive vs
> iterative + caching) and its records; list HTTP methods/status codes and the version
> differences; separate SMTP from IMAP/POP3; describe DORA; and fill the protocol → port
> → transport table — all without notes.
