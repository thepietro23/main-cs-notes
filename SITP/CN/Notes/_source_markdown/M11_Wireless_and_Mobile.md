---
title: "Module 11 — Wireless & Mobile Networks"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — Wireless & Mobile Networks

> **Where this module sits.**
> Most of this course assumed wired links. But today the "last hop" is usually
> **wireless** — Wi-Fi and cellular. Wireless changes the rules: the medium is
> **shared and unreliable**, nodes **move**, and you **can't detect collisions** the
> way wired Ethernet does. This module covers **Wi-Fi (802.11, CSMA/CA)**, the
> **hidden-terminal** problem and **RTS/CTS**, **Bluetooth**, and **cellular (2G→5G)**,
> plus **wireless security (WPA2/WPA3)**.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★     | ★★        | ★★      |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **CSMA/CA vs CSMA/CD** (why
wireless can't detect collisions); **hidden & exposed terminal** + **RTS/CTS**; **Wi-Fi
802.11** standards & bands; **Bluetooth (PAN, piconet)**; **cellular generations
(2G–5G)** and cell/handoff concepts; **WEP vs WPA2/WPA3**; FDMA/TDMA/CDMA (from M2).

---

## 11.1 Why Wireless Is Different

- **Shared, broadcast medium** (air) — interference, fading, multipath.
- **Can't reliably detect collisions** while transmitting (your own signal swamps the
  weak incoming one) → wired **CSMA/CD won't work**; wireless uses **CSMA/CA**.
- **Mobility** — nodes move between access points/cells (handoff).
- **Security** — anyone in range can listen → encryption is mandatory (WPA2/WPA3).
- **Higher error rates & variable bandwidth** than wired.

> **Memory hook:** wireless = **"everyone shouting in a room you can't fully hear."**
> You avoid collisions (CA) instead of detecting them (CD), and you must encrypt because
> everyone can eavesdrop.

### MCQs

1. Why can't wireless use CSMA/CD? → it **can't detect collisions** while sending.
2. Wireless access method instead? → **CSMA/CA** (collision avoidance).
3. Moving between APs/cells is called? → **handoff/handover**.

---

## 11.2 Wi-Fi (IEEE 802.11)

**Architecture:**

- **Infrastructure mode:** devices connect through an **Access Point (AP)** (the usual
  home/office Wi-Fi). A **BSS** = one AP + its clients; an **ESS** = multiple APs on one
  network.
- **Ad-hoc mode:** devices talk directly, peer-to-peer, no AP.

**Access:** **CSMA/CA** — sense idle, wait a random **backoff**, transmit, and expect an
**ACK** (no ACK = assume collision/loss, retry). Optionally reserve the medium with
**RTS/CTS**.

**Standards (know the trend):** 802.11 **b/g** (2.4 GHz) → **n** (2.4/5 GHz, MIMO) →
**ac** (5 GHz, faster) → **Wi-Fi 6/6E (ax)** (efficient in dense areas) → Wi-Fi 7.

![Wi-Fi standards and cellular generations: Wi-Fi is local & unlicensed (via an AP); cellular is wide-area & licensed, adding speed and lowering latency each generation.](images/32_wireless_generations.png)

### MCQs

1. Wi-Fi via an AP is which mode? → **infrastructure**.
2. Wi-Fi access method? → **CSMA/CA** (with ACKs).
3. Which 802.11 introduced MIMO? → **802.11n**.

---

## 11.3 Hidden & Exposed Terminals; RTS/CTS

![Two stations that can each reach the AP but not each other are hidden terminals: they transmit together and collide at the AP; RTS/CTS reserves the medium to prevent this.](images/31_wifi_hidden.png)

- **Hidden-terminal problem:** A and C can both reach the AP but **can't hear each
  other**, so they transmit at once and **collide at the AP**. Carrier sensing fails
  because they don't sense each other.
- **Exposed-terminal problem:** a node needlessly **defers** because it hears another
  transmission that wouldn't actually interfere with its intended receiver.
- **RTS/CTS handshake:** the sender sends a small **RTS (Request To Send)**; the AP
  replies **CTS (Clear To Send)**, which *all* nearby nodes hear and then stay quiet →
  reserves the medium and solves hidden terminals (at the cost of overhead).

> **Memory hook:** **hidden = can't hear each other → collide at the AP; RTS/CTS = "ask
> permission out loud"** so everyone in range backs off.

### MCQs

1. Hidden terminals collide **where**? → at the **AP** (they can't hear each other).
2. What solves the hidden-terminal problem? → **RTS/CTS**.
3. Exposed terminal causes? → **unnecessary deferral** (lost throughput).

---

## 11.4 Bluetooth & Other Short-Range Wireless

- **Bluetooth:** a **PAN** technology (~10 m). Devices form a **piconet** (one master +
  up to 7 active slaves); uses **frequency hopping** in 2.4 GHz. BLE (Low Energy) for
  IoT/wearables.
- **Zigbee:** low-power, low-rate mesh for IoT/home automation.
- **NFC:** very short range (cm), contactless payments/tap.
- **RFID:** tags read by a reader (inventory, access cards).

### MCQs

1. Bluetooth network of 1 master + up to 7 slaves? → a **piconet**.
2. Bluetooth range/class? → **PAN** (~10 m).
3. Very-short-range tap-to-pay tech? → **NFC**.

---

## 11.5 Cellular Networks (2G → 5G)

The area is divided into **cells**, each served by a **base station**; frequencies are
**reused** in non-adjacent cells. As you move, calls **hand off** between cells.

| Gen | Key feature |
|---|---|
| **1G** | analog voice |
| **2G** | **digital** voice + SMS (GSM) |
| **3G** | mobile **data** (UMTS) |
| **4G LTE** | **all-IP** broadband, high speed |
| **5G** | very **low latency**, massive IoT, mmWave, high density |

Multiple access across generations uses **FDMA/TDMA/CDMA/OFDMA** (from M2).

> **Memory hook:** **2G digital voice, 3G data, 4G broadband/all-IP, 5G low-latency +
> IoT.** Cellular = licensed, wide-area; Wi-Fi = unlicensed, local.

### MCQs

1. First **digital** cellular generation? → **2G**.
2. 4G's architecture is? → **all-IP** (LTE).
3. 5G's headline benefit? → very **low latency** (+ IoT density).

---

## 11.6 Wireless Security

- **WEP** — original Wi-Fi security; **broken** (weak RC4/IV), do not use.
- **WPA / WPA2** — WPA2 (AES-CCMP) is the long-time standard.
- **WPA3** — current; stronger handshake (SAE), forward secrecy.
- Because the medium is open, **encryption + strong auth are mandatory**; also beware
  **rogue APs / evil twins** and **deauth attacks**.

### MCQs

1. Which Wi-Fi security is broken? → **WEP**.
2. Modern Wi-Fi security standards? → **WPA2 / WPA3**.
3. A fake AP impersonating a real one? → **evil twin / rogue AP**.

---

## 11.7 Real-World & Backend Perspectives

- **Wi-Fi/cellular are the last hop** for most users — app performance must tolerate
  **jitter, loss, and handoffs** (why TCP tuning, QUIC/HTTP-3, and retries matter).
- **5G + edge computing** push compute closer to users for low latency (ties to CDNs,
  M12).
- **IoT** (BLE/Zigbee + cellular NB-IoT) is a huge growth area; constrained devices need
  lightweight protocols (CoAP/MQTT).

---

## 11.8 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** saying Wi-Fi uses CSMA/CD — it uses **CSMA/CA** (can't detect
  collisions).
- **Mistake:** confusing **hidden** (can't hear each other → collide) vs **exposed**
  (hear each other → over-defer) terminals.
- **Trap:** WEP is **insecure** — the "secure" answers are **WPA2/WPA3**.
- **Edge case:** RTS/CTS helps hidden terminals but adds overhead — usually only used
  for larger frames.

---

## 11.9 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** CSMA/CA, Wi-Fi vs cellular, Bluetooth piconet, cellular
  generations, WEP/WPA.
- **GATE / C-DAC:** hidden/exposed terminal + RTS/CTS, 802.11 access details, FDMA/TDMA/
  CDMA.
- **Interview:** "why does Wi-Fi use CA not CD?", "what's the hidden-terminal problem?",
  "how does mobile handoff work?".

---

## 11.10 Concept Checks & MCQs (test yourself)

1. Wireless access method & why? → **CSMA/CA** (can't detect collisions).
2. Wi-Fi infrastructure vs ad-hoc? → via **AP** vs **peer-to-peer**.
3. Hidden vs exposed terminal? → **collide at AP** vs **over-defer**.
4. What solves hidden terminals? → **RTS/CTS**.
5. Bluetooth 1-master/≤7-slave network? → **piconet**.
6. 2G vs 4G? → **digital voice+SMS** vs **all-IP broadband**.
7. Broken Wi-Fi security? → **WEP**.
8. 802.11n added? → **MIMO** (2.4/5 GHz).
9. 5G headline? → **low latency + IoT density**.
10. Wi-Fi vs cellular spectrum? → **unlicensed/local** vs **licensed/wide-area**.

---

## 11.11 One-Page Revision Sheet

```
WIRELESS: shared broadcast air; can't detect collisions -> CSMA/CA (avoid) + ACKs, not CSMA/CD.
  challenges: interference/fading, mobility(handoff), security(everyone hears), higher error.

WiFi 802.11: infrastructure(AP; BSS=1 AP, ESS=many) vs ad-hoc(peer).
  access CSMA/CA + backoff + ACK. standards: b/g(2.4) -> n(MIMO,2.4/5) -> ac(5) -> WiFi6(ax) -> WiFi7.
  HIDDEN terminal: A,C reach AP but not each other -> collide AT AP. fix = RTS/CTS (reserve medium).
  EXPOSED terminal: over-defer unnecessarily.

SHORT-RANGE: Bluetooth=PAN ~10m, PICONET(1 master + <=7 slaves), freq hopping; BLE=IoT. Zigbee=low-power mesh. NFC=cm. RFID=tags.

CELLULAR: cells + base stations, frequency reuse, handoff.
  1G analog | 2G digital voice+SMS(GSM) | 3G data(UMTS) | 4G all-IP broadband(LTE) | 5G low-latency+IoT+mmWave.
  access: FDMA/TDMA/CDMA/OFDMA.  Wi-Fi=unlicensed/local ; cellular=licensed/wide-area.

SECURITY: WEP=BROKEN. WPA2(AES) standard. WPA3(SAE, forward secrecy). beware rogue AP/evil twin, deauth.
```

### Flash cards

| Front | Back |
|-------|------|
| Wireless access method | CSMA/CA (+ ACKs) |
| Why not CSMA/CD | can't detect collisions while sending |
| Hidden terminal | can't hear each other → collide at AP |
| Fix for hidden terminal | RTS/CTS |
| Bluetooth network | piconet (1 master + ≤7 slaves) |
| 802.11n feature | MIMO |
| 2G / 4G / 5G | digital voice / all-IP / low-latency+IoT |
| Broken Wi-Fi security | WEP |
| Modern Wi-Fi security | WPA2 / WPA3 |
| Wi-Fi vs cellular | unlicensed local vs licensed wide-area |

### Spaced repetition
- **24-hour:** CSMA/CA vs CSMA/CD; hidden vs exposed terminal + RTS/CTS.
- **7-day:** 802.11 standards; cellular generations; WEP/WPA2/WPA3.
- **30-day:** explain why wireless needs CA + ACKs and how RTS/CTS fixes hidden
  terminals — without notes.

---

## 11.12 Summary

**Wireless** networking works on a **shared, unreliable, broadcast** medium where nodes
**move** and **collisions can't be detected** — so Wi-Fi uses **CSMA/CA** (avoid, with
**ACKs** and **backoff**) rather than CSMA/CD. **802.11** runs in **infrastructure**
(via an **AP**) or **ad-hoc** mode, evolving b/g → n (**MIMO**) → ac → Wi-Fi 6/7. The
**hidden-terminal** problem (nodes that can't hear each other collide at the AP) is
solved by **RTS/CTS**. **Bluetooth** forms **piconets** (PAN); **cellular** divides
space into **cells** with **handoff**, advancing **2G (digital) → 3G (data) → 4G
(all-IP) → 5G (low latency + IoT)**. Security moved from broken **WEP** to **WPA2/WPA3**.

Next, **Module 12 — Modern & SDN / Cloud Networking** covers software-defined
networking, CDNs, load balancing, and QUIC/HTTP-3 — how today's Internet actually
scales.

> **You have mastered this module when** you can: explain why wireless uses CSMA/CA not
> CSMA/CD; describe hidden vs exposed terminals and RTS/CTS; outline 802.11 modes &
> standards; define a piconet; sequence the cellular generations; and rank WEP/WPA2/WPA3
> — all without notes.
