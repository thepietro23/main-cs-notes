---
title: "Module 2 — The Physical Layer & Transmission Media"
subtitle: "Computer Networks Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — The Physical Layer & Transmission Media

> **Where this module sits.**
> Module 1 gave us the layered map. Now we start at the very bottom — **Layer 1, the
> Physical layer** — whose only job is to move **raw bits as signals** across a
> medium. Everything above depends on this: if the physical link is slow or noisy,
> no clever protocol above can fix it. This module explains **signals**, the two
> famous limits (**Nyquist & Shannon**) that cap how fast any link can go, the
> **media** (copper, fibre, air), the **performance metrics** (bandwidth, latency,
> bandwidth-delay product) you'll use for the rest of the course, and
> **multiplexing**. The Nyquist/Shannon **numericals are a GATE/C-DAC staple.**

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★        | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **Nyquist** (noiseless) and
**Shannon** (noisy) channel-capacity numericals; **bit rate vs baud rate**;
**bandwidth**; transmission impairments (**attenuation, distortion, noise**);
**guided vs unguided media** (and "which is fastest / immune to EMI" → fibre);
**bandwidth-delay product**; **multiplexing** (FDM/TDM/WDM); propagation vs
transmission delay.

---

## 2.1 Data, Signals, Analog vs Digital

**Data** is information; a **signal** is the electrical/optical/radio representation
that actually travels. Both data and signals can be **analog** (continuous) or
**digital** (discrete levels).

![Analog signals are continuous waves; digital signals are discrete 0/1 levels — what computers send.](images/03_analog_vs_digital.png)

- **Analog signal:** a smooth wave with infinitely many values (e.g. a sine wave;
  voice on an old phone line).
- **Digital signal:** discrete levels — for binary, two levels for **0** and **1**.

A periodic signal has three properties: **amplitude** (height/strength),
**frequency** (cycles per second, **Hz**), and **phase** (shift). Frequency is the
inverse of period: `f = 1/T`.

> **Memory hook:** analog = a **dimmer knob** (any brightness); digital = a **light
> switch** (only on/off). Computers speak switches.

### MCQs

1. Frequency unit? → **hertz (Hz)** = cycles/second.
2. `f = ?` in terms of period T? → **1/T**.
3. Which signal type do computers natively use? → **digital**.

---

## 2.2 Bandwidth, Bit Rate & Baud Rate (don't mix these up)

- **Bandwidth (analog sense):** the **range of frequencies** a channel passes,
  measured in **Hz** (e.g. a channel from 1000–4000 Hz has bandwidth 3000 Hz).
- **Bandwidth (digital/networking sense):** loosely, the **maximum bit rate** a link
  can carry, in **bits per second (bps)**.
- **Bit rate:** number of **bits** sent per second (bps).
- **Baud rate (signal rate):** number of **signal units (symbols)** sent per second.

The link between them: `bit rate = baud rate × log₂(L)`, where **L = number of signal
levels** (bits carried per symbol = log₂ L).

> **Memory hook:** **baud = symbols/sec, bit rate = bits/sec.** If each symbol
> carries 2 bits (4 levels), the bit rate is **twice** the baud rate. Baud ≤ bit rate.

**Worked example:** a signal with **baud = 1000** symbols/s using **L = 8** levels →
`bit rate = 1000 × log₂8 = 1000 × 3 = 3000 bps`.

### MCQs

1. Baud rate measures? → **symbols (signal units) per second**.
2. `bit rate = baud × ?` → **log₂(L)** (L = levels).
3. 2000 baud with 4 levels → bit rate? → `2000 × log₂4 = 2000 × 2 =` **4000 bps**.

---

## 2.3 Channel Capacity — Nyquist & Shannon (the GATE numericals)

Two formulas cap how fast a channel can go. **Learn both and when to use which.**

### Nyquist — noiseless channel (theoretical max, you choose the levels)

```
C = 2 × B × log₂(L)      bits/second
   B = bandwidth (Hz),  L = number of signal levels
```

Use Nyquist when the question is **noiseless** and gives you the **number of levels**.

**Worked example:** B = 3000 Hz, L = 2 (binary) → `C = 2 × 3000 × log₂2 = 6000 × 1 =`
**6000 bps**. With L = 4 → `2 × 3000 × 2 =` **12000 bps**.

### Shannon — noisy channel (real-world max, set by noise)

```
C = B × log₂(1 + S/N)    bits/second
   S/N = signal-to-noise power ratio (a plain ratio, NOT decibels)
```

If **S/N is given in decibels (dB)**, convert first: `S/N = 10^(dB/10)`.
A famous shortcut: `log₂(1 + S/N) ≈ SNR_dB / 3` for large SNR.

**Worked example:** B = 3000 Hz, SNR = 30 dB → `S/N = 10^(30/10) = 10³ = 1000` →
`C = 3000 × log₂(1001) ≈ 3000 × 9.97 ≈` **29,900 bps** (≈ 30 kbps — the classic
dial-up modem limit).

### Which one? (the exam trick)

- **Noiseless + levels given** → **Nyquist**.
- **Noisy + SNR given** → **Shannon**.
- **Both given** → compute **both** and take the **smaller** (Shannon caps the true
  rate; Nyquist then tells you how many levels you may use).

> **Memory hook:** **Nyquist = "how many levels can I squeeze in?"** (you control it).
> **Shannon = "how much noise will let through?"** (nature controls it). The real
> limit is the **lower** of the two.

### MCQs

1. Nyquist capacity formula? → **C = 2B·log₂L**.
2. Shannon capacity formula? → **C = B·log₂(1 + S/N)**.
3. SNR = 30 dB as a ratio? → **1000** (`10^(30/10)`).
4. If Nyquist gives 12 kbps and Shannon gives 8 kbps, the usable capacity is? →
   **8 kbps** (the smaller).

---

## 2.4 Transmission Impairments (why signals degrade)

Signals weaken and distort as they travel. Three impairments:

| Impairment | What happens | Fix |
|---|---|---|
| **Attenuation** | signal **loses strength** with distance | **amplifiers** (analog) / **repeaters** (digital) |
| **Distortion** | signal **shape changes** (components travel at different speeds) | equalisation |
| **Noise** | unwanted signals added (thermal, crosstalk, impulse) | shielding; higher SNR |

Signal strength/loss is measured in **decibels**: `dB = 10·log₁₀(P₂/P₁)`. A **loss**
is negative dB; a **gain** is positive.

> **Memory hook:** **A-D-N: Attenuation (weaker), Distortion (mis-shapen), Noise
> (corrupted).** Repeaters fight attenuation; SNR fights noise.

### MCQs

1. Loss of strength over distance? → **attenuation**.
2. Digital device that regenerates a weakened signal? → **repeater**.
3. Crosstalk is a form of? → **noise**.

---

## 2.5 Transmission Media — Guided vs Unguided

![Guided media carry the signal inside a cable (twisted pair, coax, fibre); unguided media send it through air (radio, microwave, infrared).](images/04_transmission_media.png)

### Guided (wired)

| Medium | Notes |
|---|---|
| **Twisted pair** (UTP/STP) | cheapest; phone & most LAN cabling (Cat5e/6); twisting reduces crosstalk; limited distance |
| **Coaxial cable** | more bandwidth & noise-immunity than twisted pair; cable TV, older LANs |
| **Fibre optic** | carries **light**; **highest bandwidth**, **immune to EMI**, very low attenuation, most secure; backbone & long-haul. Single-mode (long) vs multi-mode (short) |

### Unguided (wireless)

| Medium | Notes |
|---|---|
| **Radio waves** | omnidirectional; Wi-Fi, AM/FM, cellular |
| **Microwave** | **line-of-sight**; towers & satellites; high bandwidth |
| **Infrared** | short-range, can't pass walls; remotes, old IrDA |

> **Memory hook:** **Fibre wins on speed, distance, and security** (it's light — no
> electromagnetic interference and hard to tap). **Twisted pair wins on cost.**

### MCQs

1. Fastest, EMI-immune guided medium? → **fibre optic**.
2. Cheapest guided medium? → **twisted pair**.
3. Which wireless medium needs line-of-sight? → **microwave**.
4. Fibre carries data as? → **light**.

---

## 2.6 Network Performance — the Metrics You'll Use All Course

- **Bandwidth** — max data rate of the link (bps).
- **Throughput** — actual measured rate (always ≤ bandwidth).
- **Latency (delay)** — total time for one bit/message to arrive, made of four parts:

```
Total delay = Transmission + Propagation + Queuing + Processing
  Transmission delay = message size / bandwidth      (time to PUSH bits onto link)
  Propagation delay  = distance / propagation speed   (time for a bit to TRAVEL)
```

- **Jitter** — variation in delay (bad for voice/video).
- **Bandwidth-Delay Product (BDP)** = **bandwidth × RTT** = the number of bits "in
  flight" the link can hold — it sets how big TCP's window must be (Module 8).

**Worked example (transmission vs propagation):** send a **1000-bit** message over a
**1 Mbps** link that is **2000 km** long (propagation speed 2×10⁸ m/s):
- Transmission delay = `1000 / 10⁶ = 1 ms`.
- Propagation delay = `2×10⁶ m / 2×10⁸ = 10 ms`.
- Total ≈ **11 ms** — here propagation dominates (long link, small message).

> **Memory hook:** **transmission delay = how long to *load the truck*;
> propagation delay = how long the *truck drives* to the destination.**

### MCQs

1. Time to put all bits on the wire? → **transmission delay** = size/bandwidth.
2. Time for a bit to travel the distance? → **propagation delay** = distance/speed.
3. Bandwidth-delay product = ? → **bandwidth × RTT** (bits in flight).
4. Variation in delay is called? → **jitter**.

---

## 2.7 Multiplexing — Sharing One Link

**Multiplexing** lets several signals share one physical link (a *multiplexer*
combines them, a *demultiplexer* splits them at the far end).

![FDM gives each signal its own frequency band (all send at once); TDM gives each signal a time slot (they take turns).](images/05_multiplexing.png)

| Technique | Shares by | Example |
|---|---|---|
| **FDM** (Frequency-Division) | different **frequency** bands, all at once | radio/TV, cable |
| **TDM** (Time-Division) | different **time** slots, taking turns | digital telephony (T1/E1) |
| **WDM** (Wavelength-Division) | different **light wavelengths** (FDM for fibre) | fibre backbones |
| **CDM/CDMA** (Code-Division) | different **codes**, all at once | some cellular |

TDM comes in two flavours: **synchronous** (fixed slots, even if a source is idle →
wasted slots) and **statistical** (slots given on demand → efficient).

> **Memory hook:** **FDM = different radio stations (pitch); TDM = taking turns
> (time); WDM = different colours of light; CDMA = everyone talks at once in a
> different language (code).**

### MCQs

1. FDM shares by? → **frequency**. TDM by? → **time**.
2. WDM is basically FDM applied to? → **fibre (light wavelengths)**.
3. TDM type that wastes idle slots? → **synchronous** TDM.

---

## 2.8 Switching (how data crosses a network of links)

To connect many devices we don't wire every pair; we route through **switches**.

- **Circuit switching:** reserve a **dedicated path** for the whole call (telephone
  network). Pros: guaranteed bandwidth. Cons: wastes capacity when idle; setup delay.
- **Packet switching:** data is split into **packets**, each routed independently;
  links are shared on demand (the **Internet**). Two sub-types:
  - **Datagram** (connectionless — IP): each packet routed independently, may arrive
    out of order.
  - **Virtual circuit** (connection-oriented — e.g. MPLS/ATM): a path is set up first,
    all packets follow it.
- **Message switching:** whole message stored-and-forwarded hop by hop (old telegraph;
  high delay).

> **Memory hook:** **circuit = a reserved private lane (phone); packet = everyone
> shares the road, cars routed independently (Internet).**

### MCQs

1. The Internet uses which switching? → **packet switching** (datagram).
2. Guaranteed dedicated bandwidth but wasteful when idle? → **circuit switching**.
3. IP is datagram or virtual-circuit? → **datagram** (connectionless).

---

## 2.9 Real-World & Backend Perspectives

- **BDP is why "fat long-distance links" need big TCP windows** — a 1 Gbps link across
  the world (RTT 200 ms) holds `10⁹ × 0.2 = 200 Mbit ≈ 25 MB` in flight; if TCP's
  window is smaller, you can't fill the pipe (Module 8; "long fat networks").
- **Latency ≠ bandwidth:** a backend truth — adding bandwidth won't fix a
  latency-bound app; propagation delay (speed of light) is a hard floor. This is why
  **CDNs** put content physically closer to users (Module 12).
- **Fibre everywhere:** data-center and backbone links are fibre for bandwidth and
  distance; "dark fibre" and WDM carry terabits per strand.

---

## 2.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** treating **bit rate and baud rate as equal** — they're equal only when
  each symbol carries 1 bit (2 levels).
- **Mistake:** plugging **dB directly** into Shannon — convert `S/N = 10^(dB/10)` first.
- **Trap:** forgetting the **×2** in Nyquist (`C = 2B·log₂L`, not `B·log₂L`).
- **Edge case:** more signal **levels** raise capacity (Nyquist) but are **harder to
  tell apart under noise** — Shannon is the real ceiling.

---

## 2.11 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD:** conceptual — media comparison ("which is fastest/immune to
  EMI"), analog vs digital, multiplexing types, switching types.
- **GATE / C-DAC:** the **numericals** — Nyquist, Shannon (with dB conversion), bit vs
  baud, transmission vs propagation delay, BDP. Practice until automatic.
- **Interview:** "difference between latency and bandwidth?" and "why does a CDN
  help?" — answer with propagation delay + BDP.

---

## 2.12 Concept Checks & MCQs (test yourself)

1. Nyquist for B = 4 kHz, L = 4? → `2 × 4000 × 2 =` **16,000 bps**.
2. Shannon for B = 1 kHz, S/N = 63? → `1000 × log₂64 =` **6000 bps**.
3. Bit rate if baud = 4000, 16 levels? → `4000 × log₂16 =` **16,000 bps**.
4. Which impairment do repeaters fight? → **attenuation**.
5. Guided medium immune to EMI? → **fibre optic**.
6. FDM vs TDM share by? → **frequency vs time**.
7. Internet switching type? → **packet (datagram)**.
8. Transmission delay formula? → **message size / bandwidth**.
9. BDP formula and meaning? → **bandwidth × RTT** = bits in flight.
10. 40 dB SNR as a ratio? → **10,000** (`10⁴`).

---

## 2.13 One-Page Revision Sheet

```
PHYSICAL LAYER (L1): move raw BITS as signals. PDU = bits.
SIGNAL: analog(continuous wave) vs digital(discrete 0/1). f = 1/T (Hz). amp/freq/phase.

RATES: bandwidth(Hz analog | bps digital) ; bit rate(bits/s) ; baud(symbols/s).
  bit rate = baud x log2(L).   baud <= bit rate (equal only if L=2).

CAPACITY:
  NYQUIST (noiseless):  C = 2 * B * log2(L)      <- you pick L
  SHANNON (noisy):      C = B * log2(1 + S/N)    <- S/N is a RATIO
     dB -> ratio: S/N = 10^(dB/10).  approx log2(1+SNR) ~ dB/3.
  BOTH given -> take the SMALLER. (Nyquist=levels, Shannon=noise ceiling.)

IMPAIRMENTS (A-D-N): Attenuation(weaker->repeater/amplifier) | Distortion(mis-shape) | Noise(SNR/shield).
  dB = 10 log10(P2/P1).

MEDIA:  GUIDED: twisted pair(cheap) < coax < FIBRE(fastest, EMI-immune, secure, light).
        UNGUIDED: radio(omni,Wi-Fi) | microwave(line-of-sight, sat) | infrared(short,no walls).

PERFORMANCE: bandwidth>=throughput. Delay = Transmission(size/BW) + Propagation(dist/speed)
  + Queuing + Processing.  Jitter = delay variation.  BDP = BW x RTT = bits in flight.
  Transmission = "load the truck"; Propagation = "truck drives there."

MULTIPLEXING: FDM(frequency) | TDM(time; sync wastes idle vs statistical) | WDM(light=FDM on fibre) | CDMA(codes).
SWITCHING: circuit(dedicated path, phone) | PACKET(shared; datagram=IP / virtual-circuit) | message(store-fwd).
```

### Flash cards

| Front | Back |
|-------|------|
| Nyquist capacity | C = 2B·log₂L |
| Shannon capacity | C = B·log₂(1 + S/N) |
| dB → SNR ratio | 10^(dB/10) |
| bit rate vs baud | bit = baud × log₂L |
| Fastest / EMI-immune medium | fibre optic |
| Cheapest guided medium | twisted pair |
| Transmission delay | size / bandwidth |
| Propagation delay | distance / speed |
| Bandwidth-delay product | bandwidth × RTT |
| Internet switching | packet (datagram) |

### Spaced repetition
- **24-hour:** redo one Nyquist and one Shannon numerical (with a dB→ratio step).
- **7-day:** media comparison table; transmission vs propagation delay; multiplexing.
- **30-day:** given B, L, and SNR, compute usable capacity and explain which limit binds.

---

## 2.14 Summary

The **Physical layer** turns bits into **signals** and pushes them across a medium.
Signals are **analog** (continuous) or **digital** (discrete). We distinguish
**bandwidth**, **bit rate**, and **baud rate** (`bit rate = baud × log₂L`), and cap
throughput with two formulas: **Nyquist** (`C = 2B·log₂L`, noiseless) and **Shannon**
(`C = B·log₂(1+S/N)`, noisy) — with the real limit being the **smaller**. Signals
suffer **attenuation, distortion, and noise**. **Media** split into **guided**
(twisted pair → coax → **fibre**, the fastest and EMI-immune) and **unguided** (radio,
microwave, infrared). We measure links by **bandwidth, throughput, and delay**
(transmission + propagation + queuing + processing), and reason about pipes with the
**bandwidth-delay product**. Finally, **multiplexing** (FDM/TDM/WDM/CDMA) shares a
link, and **switching** (circuit vs **packet**) moves data across a network.

Next, **Module 3 — The Data Link Layer** climbs to Layer 2: how bits are grouped into
**frames**, how errors are **detected and corrected** (parity, checksum, CRC, Hamming
code), and how flow is controlled (stop-and-wait, sliding window) — with more
high-value numericals.

> **You have mastered this module when** you can: pick and apply Nyquist vs Shannon
> (converting dB), separate bit rate from baud, rank the media by speed/cost/EMI,
> split total delay into its four parts and compute transmission vs propagation
> delay, define the bandwidth-delay product, and contrast FDM/TDM and
> circuit/packet switching — all without notes.
