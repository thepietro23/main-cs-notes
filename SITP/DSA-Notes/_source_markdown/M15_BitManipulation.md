---
title: "Module 15 — Bit Manipulation"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 15 — Bit Manipulation

> **Why bits matter.**
> Under the hood everything is bits (Module 1). Working *directly* with bits gives
> O(1) tricks that replace loops: test/flip a flag, count set bits, find the odd
> one out, enumerate subsets, and pack a whole set into one integer (the basis of
> bitmask DP, Module 14c). Interviewers love bit tricks because they reveal whether
> you understand the machine; GATE tests them numerically.

This module is **P0–P1**: XOR tricks and the 4 basic operations are must-know;
Gray code and advanced packing are P1/CP.

> **How to read each technique.** The operation, the one-liner, the use, plus a
> memory hook.

---

## 15.1 Bitwise Operators

![Bitwise AND/OR/XOR/NOT and shifts, each acting bit-by-bit; XOR is 1 when bits differ.](images/117_bit_ops.png)

| Op | Symbol | Result bit is 1 when… |
|---|---|---|
| AND | `&` | **both** bits are 1 |
| OR | `\|` | **either** bit is 1 |
| XOR | `^` | the bits **differ** |
| NOT | `~` | flips every bit (and the sign, two's complement) |
| Left shift | `<< k` | slide left = **× 2ᵏ** |
| Right shift | `>> k` | slide right = **÷ 2ᵏ** (floor) |

- `1 << k` builds a **mask** with only bit `k` set — the workhorse of everything
  below.
- **Caution:** shifting by ≥ the type width, and right-shifting negatives
  (arithmetic vs logical), is implementation-defined — a common bug/GATE trap.

> **Memory hook:** AND = "both", OR = "either", XOR = "different", shift = "slide".

### MCQs

1. `x << 3` equals? → `x × 8`.
2. XOR bit is 1 when? → the two bits **differ**.
3. `1 << k` gives? → a mask with **only bit k set**.

### Two's complement & right shift (GATE numerics)

For an n-bit two's-complement number with bits `b_{n-1}…b_0`:

```
value = -b_{n-1}·2^(n-1) + Σ_{i=0..n-2} b_i·2^i ,   range = [ -2^(n-1) , 2^(n-1)-1 ]
to negate: invert all bits, then add 1
```

**Worked examples (8-bit):**

- `11010110₂` = `-128 + 64 + 16 + 4 + 2` = **−42**.
- Represent **−45**: `45 = 00101101` → invert `11010010` → +1 → **`11010011`**.
- Asymmetry: the most-negative value `-2^(n-1)` (e.g. −128) has **no** positive
  counterpart.

**Right shift `>>` on negatives is two kinds:**

- **Arithmetic** (Java `>>`, C on signed): copies the **sign bit** → for negatives
  it floors toward −∞ (e.g. `-8 >> 1 = -4`, `-1 >> 1 = -1`).
- **Logical** (Java `>>>`, unsigned types): fills with **0** → treats the value as
  unsigned. Mixing them up is a classic bug/GATE trap.

### MCQs (two's complement)

1. Value of `11010110₂` (8-bit)? → **−42**.
2. n-bit signed range? → `[-2^(n-1), 2^(n-1)-1]`.
3. `-8 >> 1` (arithmetic)? → **−4**.

---

## 15.2 The 4 Essential Operations (on bit `i`)

![The four bit operations: check (x>>i)&1, set x|(1<<i), clear x&~(1<<i), toggle x^(1<<i).](images/118_bit_manip.png)

```text
CHECK  bit i:   (x >> i) & 1        # -> 0 or 1
SET    bit i:   x | (1 << i)        # force to 1
CLEAR  bit i:   x & ~(1 << i)       # force to 0
TOGGLE bit i:   x ^ (1 << i)        # flip
```

These four turn an integer into a compact **set of up to 32/64 flags** (a "bitset"
/ bitmask) — used for visited-states, permissions, feature flags, and bitmask DP.

### MCQs

1. Set bit i? → `x | (1<<i)`. Clear bit i? → `x & ~(1<<i)`.
2. Toggle bit i? → `x ^ (1<<i)`.
3. Check bit i? → `(x>>i) & 1`.

---

## 15.3 XOR Tricks (the most loved)

XOR's three properties make it magic: `a ^ a = 0`, `a ^ 0 = a`, and it is
**commutative & associative** (order doesn't matter).

![XOR trick: XOR all numbers; pairs cancel (a^a=0), leaving the single unique number.](images/119_xor_tricks.png)

- **Single Number (LC 136):** every element appears twice except one → **XOR them
  all**; pairs cancel, the lone one survives. O(n)/O(1).
- **Missing Number (LC 268):** XOR all indices `0..n` with all values → the
  missing one remains.
- **Swap without a temp:** `a^=b; b^=a; a^=b;`.
- **Single Number II (LC 137)** — others appear 3×: either count set bits per
  position **mod 3**, or the O(1) two-mask automaton
  `ones = (ones ^ x) & ~twos;  twos = (twos ^ x) & ~ones`.
- **Single Number III (LC 260)** — two singles `a, b`: `xorAll = XOR of all`;
  isolate a differing bit `diff = xorAll & (-xorAll)`; split numbers into two
  buckets by `(e & diff)` and XOR each bucket → recovers `a` and `b`.
- **a ^ b** has a 1 in every position where `a` and `b` differ (→ Hamming
  distance = popcount(a^b)).

### Add without `+`, and Maximum XOR

```text
# Sum of Two Integers (LC 371) — no + or -
while b != 0:
    carry = (a & b) << 1     # bits where both are 1 -> carry left
    a = a ^ b                # sum without carry
    b = carry
return a        # (in Python, mask with & 0xFFFFFFFF and fix the sign for 32-bit)
```

- **XOR = sum without carry**, **(a & b) << 1 = the carry** — loop until no carry.
- **Maximum XOR of two numbers (LC 421):** go MSB→LSB, greedily try to set each
  answer bit, checking a **set of seen prefixes** (or a **binary trie of bits**)
  for a value that XORs to the desired prefix. O(32·n).

> **Memory hook:** XOR is a **light switch** — flip it twice and you're back to the
> start; that's why duplicates cancel.

### MCQs

1. Find the unique among pairs? → **XOR everything**.
2. Hamming distance of a,b? → `popcount(a ^ b)`.
3. Why do pairs cancel? → `a ^ a = 0`.

---

## 15.4 Counting & Isolating Bits

![Bit tricks: lowest set bit x&(-x), remove lowest x&(x-1), power-of-two test, popcount, and Gray code.](images/120_bit_tricks.png)

| Trick | One-liner | Use |
|---|---|---|
| **Lowest set bit** | `x & (-x)` | isolate the rightmost 1 (Fenwick tree!) |
| **Remove lowest set bit** | `x & (x - 1)` | Brian Kernighan's bit count |
| **Is power of two?** | `x > 0 && (x & (x-1)) == 0` | exactly one bit set |
| **Count set bits (popcount)** | builtin `__builtin_popcount` / `Integer.bitCount` / `int.bit_count()` | population count |

```text
# Brian Kernighan's set-bit count            Time O(number of set bits)
count = 0
while x: x &= (x - 1); count++      # each step removes the lowest set bit
```

- `x & (x-1)` clears the lowest set bit; `x & (-x)` *isolates* it. (`-x` is `~x+1`
  in two's complement, Module 1.)
- **Counting Bits (LC 338):** `dp[i] = dp[i >> 1] + (i & 1)` — a neat DP using
  bits.
- **Power of four:** power of two **and** the set bit is at an even index →
  `x>0 && (x&(x-1))==0 && (x & 0x55555555) != 0`.
- **Reverse Bits (LC 190):** process bits LSB→MSB, pushing into the result
  MSB→LSB (or swap symmetric halves).
- **Bitwise AND of range [m,n] (LC 201):** right-shift both ends until equal
  (counting shifts), then left-shift back — the result is the common prefix.

### MCQs

1. Isolate the lowest set bit? → `x & (-x)`.
2. Power-of-two check? → `x>0 && (x & (x-1))==0`.
3. Kernighan's count complexity? → **O(#set bits)** (not O(32)).

---

## 15.5 Subsets & Gray Code

### Enumerate all subsets via bitmask

For `n` items, each integer `mask` in `0 .. 2ⁿ−1` is one subset: bit `j` set ⇒
include item `j`. (This is the iterative version of Module 13 subsets, and the
core of bitmask DP, Module 14c.)

```text
for mask in 0 .. (1<<n) - 1:
    subset = [ a[j] for j in 0..n-1 if (mask >> j) & 1 ]
# iterate submasks of a mask: for (s=mask; s; s=(s-1)&mask)   -> O(3^n) total
```

### Gray Code

A **Gray code** orders the numbers `0..2ⁿ−1` so that **consecutive codes differ in
exactly one bit**. The formula is beautiful:

```
gray(i) = i ^ (i >> 1)
```

`0,1,2,3,4,5,6,7` → `000,001,011,010,110,111,101,100` (each step flips one bit).

- **Uses:** rotary/position encoders (one-bit change avoids misreads),
  Karnaugh maps, minimising switching errors.

### MCQs

1. #subsets of n items via masks? → **2ⁿ** (mask 0..2ⁿ−1).
2. Gray code formula? → `i ^ (i >> 1)`.
3. Gray-code neighbours differ by? → **exactly one bit**.

### Problems

- Single Number I/II/III (136/137/260); Number of 1 Bits (191); Counting Bits
  (338); Missing Number (268); Sum of Two Integers (371 — add without `+`);
  Bitwise AND of Range (201); Subsets (78 — bitmask); Gray Code (89); Maximum XOR
  of Two Numbers (421 — trie of bits).

---

## Module 15 — Concept Review (one page)

- **Operators:** `&` both, `|` either, `^` differ, `~` flip, `<<`/`>>` ×/÷ 2ᵏ;
  `1<<k` = mask.
- **4 ops on bit i:** check `(x>>i)&1`, set `x|(1<<i)`, clear `x&~(1<<i)`, toggle
  `x^(1<<i)`.
- **XOR:** `a^a=0`, `a^0=a` → single number, missing number, swap, Hamming
  distance.
- **Isolate/clear lowest bit:** `x&(-x)` / `x&(x-1)`; power-of-two `x&(x-1)==0`;
  Kernighan count O(#set bits).
- **Subsets** via masks `0..2ⁿ−1`; **Gray code** `i ^ (i>>1)` (one-bit change).

## Module 15 — Flash Cards

- Q: Set / clear / toggle / check bit i? **A: `|(1<<i)` / `&~(1<<i)` / `^(1<<i)` /
  `(x>>i)&1`.**
- Q: Find the unique among pairs? **A: XOR all.**
- Q: Lowest set bit / remove it? **A: `x&(-x)` / `x&(x-1)`.**
- Q: Power of two test? **A: `x>0 && (x&(x-1))==0`.**
- Q: Gray code formula? **A: `i ^ (i>>1)`.**
- Q: Hamming distance? **A: popcount(a^b).**

## Module 15 — Pattern Recognition

- "Appears twice except one / missing / duplicate" → **XOR**.
- "Count / test / flip a flag, pack flags" → **bit operations / bitmask**.
- "All subsets / state = subset (small n)" → **bitmask enumeration / DP**.
- "Power of two, lowest set bit, range index" → **bit identities** (`x&(x-1)`,
  `x&(-x)`).
- "Consecutive differ by one bit" → **Gray code**.

## Module 15 — Interview Questions (with follow-ups)

1. *Single Number.* FU: *appears 3× (II), or two singles (III)?*
2. *Number of 1 bits.* FU: *Kernighan O(#set bits) vs loop over 32.*
3. *Counting Bits 0..n.* FU: *the `dp[i]=dp[i>>1]+(i&1)` trick.*
4. *Sum of two integers without `+`.* FU: *XOR = sum-without-carry, AND<<1 =
   carry.*
5. *Power of two / four.* FU: *bit-pattern tests.*

## Module 15 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** two's-complement arithmetic, shift = ×/÷ 2ᵏ, evaluating
  bitwise expressions, counting set bits, and number-system conversions (Module 1
  links). Bit tricks appear in C-programming and digital-logic crossover
  questions.

---

*End of Module 15. Next: Module 16 — Mathematics (GCD, modular arithmetic, sieve,
prime factorisation, combinatorics, fast exponentiation) — with visuals.*
