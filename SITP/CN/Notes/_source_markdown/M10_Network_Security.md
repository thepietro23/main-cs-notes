---
title: "Module 10 — Network Security & Cryptography"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10 — Network Security & Cryptography

> **Where this module sits.**
> Modules 1–9 built a network that *works*. This one makes it *safe*. Packets cross
> untrusted links where anyone can read, alter, or forge them. **Network security**
> uses **cryptography** (encryption, hashing, signatures) plus **firewalls, VPNs, and
> TLS** to protect data. This is core for SEBI/RBI IT (and a bridge to the dedicated
> Cyber Security subject): symmetric vs asymmetric, hashing vs encryption, how HTTPS
> works, firewall types, and common attacks are all heavily tested.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★★★  | ★★★     | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **CIA triad**; **symmetric vs
asymmetric** encryption (AES/DES vs RSA/ECC); **hashing** (SHA/MD5) vs encryption;
**digital signatures** & **PKI/certificates/CA**; **TLS/SSL / HTTPS** handshake;
**firewalls** (packet-filter / stateful / proxy) & **IDS/IPS**; **VPN / IPsec**; common
**attacks** (MITM, DoS/DDoS, spoofing, phishing, replay, SQL injection).

---

## 10.1 Security Goals — the CIA Triad (and friends)

- **Confidentiality** — only authorised parties can read the data (encryption).
- **Integrity** — data isn't altered undetected (hashes, MACs).
- **Availability** — the service stays up (anti-DoS, redundancy).
- Plus **Authentication** (prove identity), **Non-repudiation** (can't deny an action —
  digital signatures), and **Authorization** (what you're allowed to do).

> **Memory hook:** **CIA — Confidentiality, Integrity, Availability.** Encryption =
> confidentiality; hashing = integrity; signatures = authentication + non-repudiation.

### MCQs

1. Three CIA goals? → **Confidentiality, Integrity, Availability**.
2. Which goal does encryption serve? → **confidentiality**.
3. "Can't deny you sent it" is? → **non-repudiation**.

---

## 10.2 Symmetric vs Asymmetric Encryption

![Symmetric encryption uses one shared key (fast, but key distribution is hard); asymmetric uses a public/private key pair (slower, but solves key exchange).](images/28_sym_asym.png)

- **Symmetric:** **one shared secret key** encrypts and decrypts. **Fast**, good for bulk
  data. Problem: **how to share the key** securely. Algorithms: **AES** (modern
  standard), DES/3DES (old).
- **Asymmetric (public-key):** a **key pair** — **encrypt with the public key, decrypt
  with the private key**. **Slow**, but solves key distribution. Algorithms: **RSA**,
  **ECC** (Diffie-Hellman for key exchange).
- **Hybrid (the real world):** use **asymmetric to exchange a symmetric session key**,
  then **symmetric** for the actual data (this is exactly what TLS does).

> **Memory hook:** **symmetric = one shared key (fast); asymmetric = public/private pair
> (solves exchange, slow).** Combine them = hybrid = TLS.

### MCQs

1. Symmetric vs asymmetric key(s)? → **one shared** vs **public/private pair**.
2. Which is faster / used for bulk data? → **symmetric (AES)**.
3. Why use hybrid? → asymmetric to **exchange the symmetric key**, then symmetric for
   speed.

---

## 10.3 Hashing, MACs & Digital Signatures

- **Hash function** (SHA-256, ~~MD5/SHA-1 broken~~): a **one-way** function mapping any
  input to a fixed-size digest. Properties: **deterministic, one-way, collision-
  resistant, avalanche**. Used for **integrity** (compare digests) — **not** encryption
  (you can't reverse it).
- **MAC / HMAC:** a hash **keyed** with a secret → integrity **+ authentication** (only
  someone with the key could have produced it).
- **Digital signature:** **hash the message, then encrypt the hash with your *private*
  key**. Anyone can verify with your **public key** → gives **integrity,
  authentication, and non-repudiation**.

> **Memory hook:** **encryption = confidentiality (reversible with a key); hashing =
> integrity (one-way).** Signature = "hash then sign with private key."

### MCQs

1. Is hashing reversible? → **no** (one-way).
2. Encryption vs hashing purpose? → **confidentiality** vs **integrity**.
3. A digital signature is made with the sender's? → **private key** (verified with the
   public key).

---

## 10.4 PKI & Certificates

How do you trust that a public key really belongs to `bank.com`? **PKI (Public Key
Infrastructure)**: a trusted **Certificate Authority (CA)** issues a **digital
certificate** binding a domain to its public key, **signed by the CA**. Your
browser/OS ships with trusted **root CAs**, forming a **chain of trust**.

- A certificate contains: subject (domain), public key, issuer (CA), validity, and the
  **CA's signature**.
- This is what stops a man-in-the-middle from faking a site's key.

### MCQs

1. Who issues certificates? → a **Certificate Authority (CA)**.
2. A certificate binds a domain to its? → **public key** (signed by the CA).
3. Trust flows along the? → **chain of trust** (to a root CA).

---

## 10.5 TLS / SSL & HTTPS

**TLS (Transport Layer Security**, successor to SSL) secures data in transit — it's what
puts the **S in HTTPS** (port 443). It combines everything above:

![The TLS handshake: client and server negotiate, the server proves identity with a CA-signed certificate, they derive a shared symmetric key, then all data uses fast symmetric encryption.](images/29_tls_handshake.png)

1. **Handshake (asymmetric):** negotiate ciphers; the server sends its **certificate**
   (public key, CA-signed); the client verifies it and they **derive a shared symmetric
   session key**.
2. **Data (symmetric):** all traffic is then encrypted with the fast **symmetric** key,
   with a **MAC** for integrity.

Result: **confidentiality + integrity + authentication** — the padlock in your browser.

> **Memory hook:** **TLS = hybrid crypto in action** — asymmetric + certificate to set
> up a symmetric key, then symmetric for speed.

### MCQs

1. HTTPS = HTTP over? → **TLS** (port 443).
2. TLS uses which crypto where? → **asymmetric** (handshake) then **symmetric** (data).
3. What authenticates the server in TLS? → its **CA-signed certificate**.

---

## 10.6 Firewalls, IDS/IPS & VPNs

![A firewall filters traffic between zones by rules; a DMZ isolates public servers from the trusted internal LAN.](images/30_firewall_dmz.png)

- **Firewall:** allows/denies traffic by **rules**. Types: **packet-filter** (stateless,
  L3/4 rules on IP/port), **stateful** (tracks connection state), **application/proxy**
  (L7, inspects content). A **DMZ** isolates public servers from the internal LAN.
- **IDS vs IPS:** **IDS** *detects* and alerts on intrusions; **IPS** *detects and
  blocks* inline.
- **VPN (Virtual Private Network):** an **encrypted tunnel** over the public Internet,
  giving secure remote access / site-to-site links. **IPsec** (network-layer: AH for
  integrity, ESP for encryption; transport vs tunnel mode) and **TLS/WireGuard** VPNs.

> **Memory hook:** **firewall = gatekeeper by rules; IDS = alarm; IPS = alarm + lock;
> VPN = encrypted tunnel through the public Internet.**

### MCQs

1. Firewall that tracks connection state? → **stateful**.
2. IDS vs IPS? → **detect/alert** vs **detect + block**.
3. VPN provides? → an **encrypted tunnel** (e.g. **IPsec**).
4. What isolates public servers from the LAN? → a **DMZ**.

---

## 10.7 Common Network Attacks

| Attack | What it does | Defence |
|---|---|---|
| **MITM** | intercept/alter traffic between two parties | **TLS**, cert pinning |
| **DoS / DDoS** | flood a service to exhaust it | rate limiting, scrubbing, CDNs |
| **IP / ARP / DNS spoofing** | forge addresses/records to redirect | authentication, DNSSEC, dynamic ARP inspection |
| **Replay** | resend captured valid messages | nonces, timestamps, sequence numbers |
| **Phishing / social engineering** | trick users into credentials | awareness, MFA |
| **Packet sniffing** | read traffic on a shared medium | **encryption** (TLS) |
| **SYN flood** | half-open TCP connections (a DoS) | SYN cookies (M7) |

> **Memory hook:** **encryption defeats sniffing/MITM; nonces defeat replay; rate
> limiting defeats DoS; MFA + awareness defeat phishing.**

### MCQs

1. Intercepting and altering traffic in transit? → **MITM** (defeated by TLS).
2. Flooding to exhaust a service? → **DoS/DDoS**.
3. Resending captured valid messages? → **replay** (defeated by nonces/timestamps).
4. Forging "who has this IP" replies on a LAN? → **ARP spoofing**.

---

## 10.8 Real-World & Backend Perspectives

- **TLS everywhere** — every API/website should be HTTPS; backends manage certificates
  (Let's Encrypt, rotation), TLS termination at load balancers, and mTLS between
  services.
- **DDoS protection** (Cloudflare/CDN scrubbing) and **WAFs** (application firewalls) are
  standard for public services.
- **Zero-trust / VPN / mTLS** secure internal traffic; **secrets management** (Vault)
  protects keys. This module is the bridge to the dedicated **Cyber Security** subject.

---

## 10.9 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** "hashing encrypts data" — hashing is **one-way** (integrity), not
  encryption (confidentiality).
- **Mistake:** signing with the *public* key — you **sign with your private key**, verify
  with the public key.
- **Trap:** symmetric is **faster** but has the key-distribution problem; asymmetric
  solves distribution but is **slow** → hybrid.
- **Edge case:** encryption alone doesn't give **integrity/authentication** — you also
  need a **MAC/signature** (TLS uses both).

---

## 10.10 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** CIA, symmetric vs asymmetric, hashing vs encryption, HTTPS/
  TLS basics, firewall types, attack names — high frequency.
- **GATE / C-DAC:** RSA mechanics (public/private roles), Diffie-Hellman key exchange,
  digital-signature steps, IPsec AH vs ESP.
- **Interview:** "how does HTTPS work?" (hybrid + certs), "hashing vs encryption",
  "symmetric vs asymmetric", "how to stop MITM/replay".

---

## 10.11 Concept Checks & MCQs (test yourself)

1. CIA triad? → **Confidentiality, Integrity, Availability**.
2. Symmetric vs asymmetric key(s)? → **one shared** vs **public/private pair**.
3. Encryption vs hashing? → **reversible confidentiality** vs **one-way integrity**.
4. Digital signature uses which key to sign? → the sender's **private key**.
5. HTTPS uses which two crypto types? → **asymmetric (handshake) + symmetric (data)**.
6. Who vouches for a public key? → a **CA** (certificate).
7. IDS vs IPS? → **detect** vs **detect + block**.
8. VPN provides? → **encrypted tunnel** (IPsec).
9. Defence against MITM? → **TLS** (+ cert validation).
10. Defence against replay? → **nonces / timestamps / sequence numbers**.

---

## 10.12 One-Page Revision Sheet

```
GOALS: CIA = Confidentiality(encryption) + Integrity(hash/MAC) + Availability(anti-DoS).
  + Authentication, Non-repudiation(signature), Authorization.

ENCRYPTION:
  SYMMETRIC: 1 shared key; FAST; key-distribution problem. AES, DES/3DES.
  ASYMMETRIC: public/private pair; encrypt w/ public, decrypt w/ private; SLOW; solves exchange. RSA, ECC, DH.
  HYBRID (TLS): asymmetric to exchange a symmetric session key, then symmetric for data.

HASH (SHA-256): one-way, deterministic, collision-resistant, avalanche = INTEGRITY (not encryption). MD5/SHA1 broken.
  MAC/HMAC = keyed hash (integrity+auth). SIGNATURE = hash then encrypt with PRIVATE key (integrity+auth+non-repudiation).

PKI: CA issues CERTIFICATE binding domain->public key (CA-signed). chain of trust to root CAs.
TLS/SSL (HTTPS 443): handshake(asymmetric + cert) -> shared symmetric key -> symmetric data + MAC.

DEFENCES: firewall (packet-filter L3/4 | stateful | proxy L7) + DMZ. IDS=detect, IPS=detect+block. VPN=encrypted tunnel (IPsec AH/ESP, tunnel/transport).
ATTACKS: MITM(->TLS) | DoS/DDoS(->rate limit/CDN) | IP/ARP/DNS spoof(->auth/DNSSEC) | replay(->nonce) | phishing(->MFA) | sniffing(->encrypt) | SYN flood(->SYN cookies).
```

### Flash cards

| Front | Back |
|-------|------|
| CIA triad | Confidentiality, Integrity, Availability |
| Symmetric vs asymmetric | one shared key vs public/private pair |
| Faster / bulk crypto | symmetric (AES) |
| Hashing purpose | integrity (one-way) |
| Digital signature key | sign with private, verify with public |
| HTTPS crypto | asymmetric handshake + symmetric data |
| Certificate issuer | CA (chain of trust) |
| IDS vs IPS | detect vs detect+block |
| VPN | encrypted tunnel (IPsec) |
| Replay defence | nonce / timestamp / sequence number |

### Spaced repetition
- **24-hour:** symmetric vs asymmetric vs hashing (purpose + example each); the CIA triad.
- **7-day:** the TLS handshake as hybrid crypto; firewall types; attack → defence table.
- **30-day:** explain end-to-end how HTTPS gives confidentiality + integrity +
  authentication — without notes.

---

## 10.13 Summary

**Network security** pursues the **CIA triad** (Confidentiality, Integrity,
Availability) plus authentication and non-repudiation. **Encryption** gives
confidentiality — **symmetric** (one shared key, fast: AES) vs **asymmetric**
(public/private pair, solves key exchange: RSA/ECC) — combined as **hybrid** in
practice. **Hashing** (SHA-256) is **one-way** and gives **integrity**; **MACs** add
authentication; **digital signatures** (hash + private-key encryption) add
non-repudiation. **PKI/CAs** issue **certificates** binding domains to public keys, which
**TLS** uses to secure **HTTPS** (asymmetric handshake → symmetric data). **Firewalls**
(packet-filter/stateful/proxy) + **DMZ**, **IDS/IPS**, and **VPNs (IPsec)** defend the
network against attacks like **MITM, DoS/DDoS, spoofing, replay, and sniffing**.

Next, **Module 11 — Wireless & Mobile Networks** covers Wi-Fi (802.11, CSMA/CA), the
hidden-terminal problem, Bluetooth, and cellular (2G→5G).

> **You have mastered this module when** you can: state the CIA triad; contrast
> symmetric/asymmetric/hashing by purpose; explain digital signatures and PKI; walk the
> TLS handshake as hybrid crypto; classify firewalls and IDS vs IPS; and match common
> attacks to defences — all without notes.
