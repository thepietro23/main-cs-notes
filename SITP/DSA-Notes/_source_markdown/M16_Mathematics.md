---
title: "Module 16 — Mathematics for DSA"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 16 — Mathematics for DSA

> **Why a math module.**
> A surprising number of problems are really *number-theory* problems in disguise:
> GCD/LCM, primes, modular arithmetic (to keep huge answers small), and counting
> (combinatorics). These are everywhere in competitive programming, common in
> interviews (Pow, primes, GCD), and a **major GATE topic**. The good news: a
> handful of formulas and algorithms cover almost all of it.

This module is **P1** (P0 for CP/GATE). Modular arithmetic + sieve + nCr show up
constantly.

> **How to read each technique.** The idea, the algorithm, the complexity, plus a
> memory hook.

---

## 16.1 GCD, LCM & the Euclidean Algorithm

![Euclidean algorithm: gcd(a,b)=gcd(b, a mod b); gcd(48,18)=6 in a few steps.](images/121_gcd_euclid.png)

```text
# Euclid's GCD                                Time O(log(min(a,b)))
gcd(a, b): return a if b == 0 else gcd(b, a % b)
lcm(a, b) = a / gcd(a,b) * b        # divide first to avoid overflow
```

- `gcd(48,18) → gcd(18,12) → gcd(12,6) → gcd(6,0) = 6`.
- **Iterative form** (no recursion): `while b: a, b = b, a % b; return a`. GCD of
  an array folds left-to-right. "No division/modulo" variant = **binary GCD
  (Stein's)**.
- **Extended Euclid** finds `x, y` with `a·x + b·y = gcd(a,b)`:

```text
extgcd(a, b):
    if b == 0: return (a, 1, 0)          # gcd, x, y
    (g, x1, y1) = extgcd(b, a % b)
    return (g, y1, x1 - (a / b) * y1)
# modular inverse of b mod m: extgcd(b, m) -> if g==1, inverse = ((x % m) + m) % m
```

> **Memory hook:** keep replacing the bigger number by `(bigger mod smaller)`
> until one becomes 0; the other is the GCD.

### Why Euclid is O(log): the Fibonacci worst case (GATE)

Each step replaces `(a,b)` with `(b, a mod b)`. The **slowest** possible
shrinkage is when consecutive **Fibonacci numbers** are the inputs — then each
step peels off exactly one Fibonacci number and the remainder is the previous one.

```text
gcd(13,8):   13 mod 8 = 5   -> gcd(8,5)
gcd(8,5):     8 mod 5 = 3   -> gcd(5,3)
gcd(5,3):     5 mod 3 = 2   -> gcd(3,2)
gcd(3,2):     3 mod 2 = 1   -> gcd(2,1)
gcd(2,1):     2 mod 1 = 0   -> gcd(1,0) = 1     # 5 steps for F(7),F(6)
```

- Because Fibonacci numbers grow like `φⁿ` (`φ ≈ 1.618`), reaching `Fₖ` takes
  about `k ≈ log_φ(n)` steps → **O(log n)** in the worst case. **Lamé's theorem**
  states this formally: the number of steps is ≤ `~4.785·log₁₀(min(a,b)) + 1`.

> **Memory hook:** *adjacent Fibonacci numbers are Euclid's kryptonite* — they
> force the maximum number of steps for their size.

### MCQs

1. `gcd(a,b)` recurrence? → `gcd(b, a mod b)`, base `b=0`.
2. Euclid complexity? → **O(log min(a,b))**.
3. LCM in terms of GCD? → `a·b / gcd(a,b)`.

---

## 16.2 Modular Arithmetic (keep numbers small)

Answers in CP/crypto can be astronomically large, so we work **mod m** (often
`m = 10⁹+7`, a prime). Apply mod after **every** operation.

![Modular arithmetic rules: add/mul distribute over mod; subtraction add m; division needs the modular inverse.](images/122_modular.png)

```text
(a + b) mod m = ((a mod m) + (b mod m)) mod m
(a * b) mod m = ((a mod m) * (b mod m)) mod m
(a - b) mod m = ((a mod m) - (b mod m) + m) mod m     # +m keeps it non-negative
```

### Modular inverse (division under a modulus)

You **can't** just divide. To compute `a / b mod m`, multiply by the **modular
inverse** `b⁻¹`:

- If `m` is **prime** (Fermat's little theorem): `b⁻¹ = b^(m−2) mod m` — compute
  with **fast exponentiation** (Module 12).
- General `m`: use the **extended Euclidean** algorithm (needs `gcd(b,m)=1`).

**Worked — inverse of 3 mod 11 (both methods).**

*Fermat (m prime):* `3⁻¹ = 3^(11−2) = 3⁹ mod 11`.

```text
3^1=3, 3^2=9, 3^4=(9^2)=81=4, 3^8=(4^2)=16=5   (all mod 11)
3^9 = 3^8 · 3^1 = 5·3 = 15 = 4 (mod 11)
check: 3·4 = 12 = 1 (mod 11)   ✓   so 3⁻¹ = 4
```

*Extended Euclid (works for any coprime m):* solve `3x + 11y = 1`.

```text
extgcd(3,11): 11 = 3·3 + 2  ;  3 = 1·2 + 1  ;  2 = 2·1 + 0   -> gcd = 1
back-substitute: 1 = 3 - 1·2 = 3 - (11 - 3·3) = 4·3 - 1·11
so x = 4  ->  3⁻¹ ≡ 4 (mod 11)   ✓   (same answer)
```

- **When to use which:** Fermat is one line but needs `m` **prime**; extended
  Euclid needs only `gcd(b,m)=1` (any modulus). For many inverses `1..n` mod a
  prime, use the linear recurrence `inv[i] = −(m/i)·inv[m mod i] mod m` in **O(n)**.

### Fast exponentiation & Pow(x, n) (LC 50 — a top FAANG problem)

`aⁿ` (or `aⁿ mod m`) in **O(log n)** by square-and-multiply:

```text
# Pow(x, n) — real-valued (LC 50)
long nn = n
if n < 0: x = 1 / x; nn = -nn        # CAREFUL: negating INT_MIN overflows -> use long
result = 1
while nn > 0:
    if nn & 1: result *= x
    x *= x; nn >>= 1
return result          # for modular pow: take % m after each * (Module 12 §12.6)
```

- **Gotchas:** negative `n` (invert and flip sign; `INT_MIN` negation overflow →
  widen to long); real-valued Pow vs **modular** pow `aⁿ mod m`.
- This powers **modular inverse** and **RSA-style crypto** (SEBI-IT relevant).

**Dry-run — `3^13 mod 100` (square-and-multiply).** `13 = 1101₂`, so read the
exponent bit-by-bit from the LSB:

```text
bit  nn  (nn&1)  action                  x (running square)   result
 -    13    -    init                     x=3                  result=1
 0    13    1    result *= x -> 1·3=3     x=3·3=9              result=3
 1     6    0    (skip)                   x=9·9=81             result=3
 2     3    1    result *= x -> 3·81=243  x=81·81=6561=61      result=243 mod100=43
 3     1    1    result *= x -> 43·61     x=61·61 (unused)     result=2623 mod100=23
      0                                                        -> answer = 23
```

- Check: `3^13 = 1594323`, and `1594323 mod 100 = 23`. ✓
- Only **⌈log₂n⌉+1 = 4** multiplications instead of 13 — that is the O(log n) win.
  Every multiply takes `% m` immediately so numbers never blow up.

### Key theorems (GATE — state them precisely)

- **Fermat's little theorem:** if `p` is prime and `gcd(a,p)=1`, then
  `a^(p−1) ≡ 1 (mod p)` ⇒ inverse `a^(p−2) mod p`.
- **Euler's theorem:** if `gcd(a,n)=1`, then `a^φ(n) ≡ 1 (mod n)`.
- **Chinese Remainder Theorem (CRT):** for **pairwise-coprime** moduli
  `m₁…m_k`, the system `x ≡ aᵢ (mod mᵢ)` has a unique solution mod `M = Πmᵢ`:
  `x = Σ aᵢ·Mᵢ·yᵢ (mod M)` where `Mᵢ = M/mᵢ`, `yᵢ = Mᵢ⁻¹ mod mᵢ`.
  *Example:* `x≡2(3), x≡3(5), x≡2(7)` → **x = 23** (mod 105).

### MCQs

1. Why work mod 10⁹+7? → keep numbers in range / **avoid overflow** (it's prime).
2. Modular inverse of b (m prime)? → `b^(m−2) mod m` (Fermat).
3. Subtraction mod m safe form? → `((a−b) mod m + m) mod m`.

---

## 16.3 Primes — Sieve & Factorisation

### Sieve of Eratosthenes — all primes up to n

![Sieve of Eratosthenes: cross out multiples of each prime; what remains are primes (10 primes ≤ 30).](images/123_sieve.png)

```text
# Sieve of Eratosthenes                       Time O(n log log n), Space O(n)
isPrime[2..n] = true
for p from 2 while p*p <= n:
    if isPrime[p]:
        for multiple in p*p, p*p+p, ... <= n: isPrime[multiple] = false
```

- Start crossing from `p*p` (smaller multiples were already crossed by smaller
  primes). Primes ≤ 30: `2,3,5,7,11,13,17,19,23,29`.
- **Count Primes (LC 204):** count `isPrime` entries for indices in **`[2, n)`**
  (strictly **< n** — a common off-by-one). Memory follow-ups: **odd-only** or
  **bitset** sieve halves space; the **linear (Euler) sieve** runs in O(n).
- **Smallest Prime Factor (SPF) sieve:** store each number's smallest prime
  factor → factorise any `x ≤ n` in **O(log x)**.
- **Segmented sieve:** find primes in a range `[L, R]` when `R` is huge but `R−L`
  is small.

**Sieve complexity, briefly.** For each prime `p` we cross `n/p` multiples, so the
total is `n·Σ(1/p)` over primes `p ≤ n`. That prime-reciprocal sum grows like
`ln ln n`, giving **O(n log log n)** — almost linear. Space is O(n) bits.

**Segmented sieve — how it works (worked idea).** To list primes in `[L,R]` with
`R` up to `10¹²` but `R−L ≤ 10⁶`:

```text
1. ordinary sieve up to sqrt(R)          # these "base" primes cross out the rest
2. make a boolean array of size (R−L+1), all true, indexed by (value − L)
3. for each base prime p:
     start = first multiple of p that is >= L (and >= p*p)
     cross out start, start+p, start+2p, ... within [L,R]
4. remaining true positions are the primes in [L,R]
```

- Only **√R** base primes are needed, and memory is `O(R−L)`, not `O(R)` — that is
  the whole trick. Example: primes in `[100, 120]` → `101,103,107,109,113`.

### Single-number factorisation — trial division

```text
# Factorise n                                 Time O(sqrt(n))
for d from 2 while d*d <= n:
    while n % d == 0: record d; n /= d
if n > 1: record n        # leftover prime factor
```

- **Euler's totient `φ(n)`** = count of integers ≤ n coprime to n;
  `φ(n) = n · Π (1 − 1/p)` over distinct prime factors `p`.

**Euler totient — worked.** `φ(36)`: factorise `36 = 2²·3²`, distinct primes
`{2,3}`.

```text
φ(36) = 36 · (1 − 1/2) · (1 − 1/3) = 36 · (1/2) · (2/3) = 12
```

- So exactly **12** numbers in `1..36` are coprime to 36. Compute it while trial-
  dividing: for each distinct prime factor `p`, do `result -= result / p`.
- **Handy facts:** `φ(p) = p−1` for prime `p`; `φ(p^k) = p^k − p^(k−1)`; φ is
  **multiplicative** — `φ(mn) = φ(m)φ(n)` when `gcd(m,n)=1`. Totient underpins
  **Euler's theorem** `a^φ(n) ≡ 1 (mod n)` used for inverses when `n` is not prime.

### MCQs

1. Sieve complexity? → **O(n log log n)**.
2. Why start crossing at `p*p`? → smaller multiples already crossed.
3. Trial-division factorisation time? → **O(√n)**.

---

## 16.4 Combinatorics

### Counting basics

- **Permutations:** `nPr = n!/(n−r)!` (order matters).
- **Combinations:** `nCr = n!/(r!(n−r)!)` (order doesn't).
- **Pascal's rule:** `C(n,r) = C(n−1,r−1) + C(n−1,r)` → build Pascal's triangle.

![Pascal's triangle: C(n,r)=C(n-1,r-1)+C(n-1,r); row n sums to 2ⁿ.](images/124_combinatorics.png)

- Row `n` of Pascal's triangle sums to **2ⁿ** (the number of subsets — Module 13).
- **nCr mod p:** precompute factorials + inverse factorials (via modular inverse,
  §16.2), then `nCr = fact[n]·invfact[r]·invfact[n−r] mod p`. **Lucas' theorem**
  handles `nCr mod p` when `n` is huge.

**nCr mod p — the standard O(n) precompute (memorise this template).**

```text
# one-time precompute up to N (p prime, e.g. 1e9+7)          Time O(N)
fact[0] = 1
for i in 1..N: fact[i] = fact[i-1] * i % p
invfact[N] = modpow(fact[N], p-2, p)          # one Fermat inverse
for i in N-1 down to 0: invfact[i] = invfact[i+1] * (i+1) % p

# then each query is O(1):
nCr(n, r): return 0 if r<0 or r>n else fact[n] * invfact[r] % p * invfact[n-r] % p
```

- The trick: **only one** modular-inverse call (for `fact[N]`); every smaller
  `invfact[i]` comes from `invfact[i+1]·(i+1)` — so precompute is O(N), each query
  O(1). Example: `C(5,2) = fact[5]·invfact[2]·invfact[3] = 120·(1/2)·(1/6) = 10`.
- **Overflow-safe nCr (no modulus):** compute iteratively, dividing as you go (the
  running product is always an integer): `for i in 1..r: result = result *
  (n−r+i) / i`. Used in Unique Paths (LC 62) and Pascal's Triangle (118/119).

### Famous sequences & principles

- **Catalan numbers:** `Cₙ = C(2n,n)/(n+1)` → balanced parentheses, BSTs with n
  nodes, triangulations, monotonic paths. `1,1,2,5,14,42,…`.
- **Inclusion–Exclusion:** `|A∪B| = |A|+|B|−|A∩B|` (generalises to n sets with
  alternating signs) — count "at least one of" by adding/subtracting overlaps.

  **Three-set form & worked example.** `|A∪B∪C| = |A|+|B|+|C| − |A∩B| − |A∩C| −
  |B∩C| + |A∩B∩C|` (add singles, subtract pairs, add the triple — signs alternate).

  *Count integers in `1..100` divisible by 2, 3, or 5.*

  ```text
  |div2| = 50, |div3| = 33, |div5| = 20
  |div6| = 16, |div10| = 10, |div15| = 6        # pairwise (lcm)
  |div30| = 3                                   # all three
  answer = 50+33+20 − 16−10−6 + 3 = 74
  ```

  So **74** numbers, and `100 − 74 = 26` are divisible by none of 2, 3, 5.
- **Pigeonhole principle:** if `n+1` items go into `n` boxes, some box has ≥ 2 →
  powers many existence proofs (e.g. two subarrays with equal sum mod n).

### MCQs

1. `nCr` formula & Pascal's rule? → `n!/(r!(n−r)!)`; `C(n-1,r-1)+C(n-1,r)`.
2. Catalan number formula? → `C(2n,n)/(n+1)`.
3. Inclusion–exclusion for two sets? → `|A|+|B|−|A∩B|`.

---

## 16.4a Matrix Exponentiation for Linear Recurrences

Any **linear recurrence** (like Fibonacci) can be written as a matrix times the
previous state. Raising that matrix to the `n`-th power with **fast exponentiation**
(§16.2) computes the `n`-th term in **O(k³ log n)** where `k` is the state size —
far better than O(n) when `n` is astronomically large (`10¹⁸`).

**Fibonacci as a matrix.** From `F(n) = F(n−1) + F(n−2)`:

```text
[ F(n)   ]   [ 1  1 ] [ F(n-1) ]                  [ 1  1 ]^n   [ F(n+1)  F(n)   ]
[ F(n-1) ] = [ 1  0 ] [ F(n-2) ]      hence       [ 1  0 ]   = [ F(n)    F(n-1) ]
```

- So `F(n)` = top-right entry of `M^n` where `M = [[1,1],[1,0]]`. Compute `M^n` by
  **squaring the matrix** (`M, M², M⁴, …`) and multiplying the pieces for the set
  bits of `n` — exactly the square-and-multiply trace from §16.2, but with 2×2
  matrix multiply as the operation. Take `% m` after each multiply for `F(n) mod m`.

**The general recipe.** For `f(n) = c₁f(n−1) + … + c_k f(n−k)`:

```text
1. state vector v = [f(n-1), f(n-2), ..., f(n-k)]^T   (length k)
2. build the k×k transition matrix M (top row = coefficients c1..ck,
   an identity shifted below it to carry old values down)
3. answer = (M^(n-k+1) · initial_state)   via fast matrix power  -> O(k^3 log n)
```

- **Use it when:** the recurrence is linear and `n` is huge (`> 10⁷`), so plain DP
  is too slow. Count-of-paths / tilings / DFA-string-counting reduce to this too.

### MCQs

1. Fibonacci transition matrix? → `[[1,1],[1,0]]`; `F(n)` = its `M^n` corner.
2. Cost of matrix exponentiation for a k-term recurrence? → **O(k³ log n)**.
3. When to prefer it over O(n) DP? → when **n is huge** (`10¹⁸`) and recurrence
   is linear.

---

## 16.5 Number / Representation Problems (common FAANG warm-ups)

- **Happy Number (LC 202):** repeatedly sum the squares of digits; detect a cycle
  with **Floyd's fast/slow** (Module 4) or a seen-set → happy iff it reaches 1.
- **Ugly Number II (LC 264):** the n-th number whose only prime factors are 2,3,5;
  **three pointers** `i2,i3,i5` building the sequence in order (DP).
- **Excel Column ↔ Number (LC 168/171):** **bijective base-26** (A=1…Z=26, *no
  zero*) → the classic off-by-one (`n--` before each `% 26`).
- **Integer ↔ Roman (LC 12/13):** a **descending value/symbol table** processed
  greedily (include 900=CM, 400=CD, etc.).
- **Digital root** (Add Digits, LC 258): closed form `1 + (n−1) % 9`.

## 16.6 Randomized Algorithms (a Google favourite)

- **rand7 → rand10 (LC 470):** **rejection sampling** — map `(rand7−1)*7 + rand7`
  to `1..49`, **reject** the top tail (41..49) so the kept range is a clean
  multiple of 10 → uniform.
- **Reservoir Sampling (LC 382/398):** pick a uniform item from a stream of
  *unknown* length — keep the i-th item with probability `1/i` (replace the
  current pick). Each element ends with probability `1/n`.
- **Fisher–Yates shuffle (LC 384):** for `i` from 0..n−1, swap `a[i]` with a random
  `a[j], j∈[i,n)` → every permutation equally likely. (The naive "random index
  each time" is **biased**.)

### MCQs

1. Uniform `rand10` from `rand7`? → **rejection sampling** (reject the tail).
2. Sample from an unknown-length stream? → **reservoir sampling** (keep i-th w.p.
   1/i).
3. Unbiased shuffle? → **Fisher–Yates**.

## Module 16 — Concept Review (one page)

- **GCD** by Euclid `gcd(b, a%b)` O(log); LCM `a·b/gcd`; extended Euclid → modular
  inverse.
- **Modular arithmetic:** distribute over +/×; subtraction add m; **division =
  multiply by modular inverse** (`b^(m−2)` if m prime). Fast exponentiation
  O(log n).
- **Primes:** Sieve O(n log log n) (cross from p²); SPF sieve → O(log x)
  factorise; trial division O(√n); Euler φ.
- **Combinatorics:** `nCr=n!/(r!(n−r)!)`, Pascal's rule, row sum 2ⁿ; nCr mod p via
  inverse factorials (Lucas for huge n); **Catalan** `C(2n,n)/(n+1)`;
  inclusion–exclusion; pigeonhole.

## Module 16 — Flash Cards

- Q: GCD algorithm & time? **A: Euclid `gcd(b,a%b)`, O(log min).**
- Q: Modular inverse (m prime)? **A: b^(m−2) mod m (Fermat).**
- Q: Sieve time & why start at p²? **A: O(n log log n); smaller multiples done.**
- Q: Factorise n by trial division? **A: O(√n).**
- Q: nCr & Pascal's rule? **A: n!/(r!(n−r)!); C(n-1,r-1)+C(n-1,r).**
- Q: Catalan formula? **A: C(2n,n)/(n+1).**
- Q: nCr mod p precompute cost & query cost? **A: O(N) precompute (one inverse),
  O(1) per query via fact + invfact.**
- Q: Euclid's worst-case input? **A: adjacent Fibonacci numbers (Lamé).**
- Q: φ(n) formula? **A: n·Π(1−1/p) over distinct primes p; φ(36)=12.**
- Q: n-th term of a linear recurrence for huge n? **A: matrix exponentiation,
  O(k³ log n).**
- Q: |A∪B∪C|? **A: singles − pairs + triple.**

## Module 16 — Pattern Recognition

- "Reduce a fraction / sync cycles / common divisor" → **GCD/LCM**.
- "Huge answer, return mod 1e9+7" → **modular arithmetic** (+ inverse for ÷).
- "All primes up to n / many primality queries" → **sieve**; "factorise one n" →
  **trial division / SPF**.
- "Count ways / choose / arrange" → **combinatorics (nCr, Catalan)**.
- "Count 'at least one of' overlapping sets" → **inclusion–exclusion**.
- "Must two of these collide?" → **pigeonhole**.
- "Linear recurrence, n up to 1e18" → **matrix exponentiation** (O(k³ log n)).
- "Count coprime to n / order under a modulus" → **Euler totient φ(n)**.
- "Primes in a huge range [L,R], small window" → **segmented sieve**.
- "nCr mod prime, many queries" → **precompute fact + invfact** (O(1)/query).

## Module 16 — Interview Questions (with follow-ups)

1. *Pow(x, n).* FU: *negative n; modular version; O(log n).*
2. *Count primes < n.* FU: *sieve; memory; segmented sieve.*
3. *GCD / fraction reduction.* FU: *extended Euclid; LCM overflow.*
4. *nCr mod p.* FU: *precompute inverse factorials; Lucas for huge n.*
5. *Catalan-counting (BSTs / valid parentheses).* FU: *derive the recurrence.*

## Module 16 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** GCD/Euclid steps, modular arithmetic & **Fermat/Euler
  theorems**, sieve complexity, counting (nCr, Catalan, inclusion–exclusion),
  pigeonhole proofs. **SEBI/RBI-IT:** modular exponentiation underlies RSA/crypto
  — know `aⁿ mod m` and modular inverse.

---

*End of Module 16. Next: Module 17 — Advanced Data Structures (suffix array,
treap, skip list, persistent structures, KD-tree, wavelet tree) — with visuals.*
