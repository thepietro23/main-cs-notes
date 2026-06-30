---
title: "Module 1 — Programming Fundamentals"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Programming Fundamentals

> **Why this module comes first.**
> Every data structure and algorithm runs on a *real machine*. If you do not
> know *where* data lives, *how* a function call works, and *how* we measure
> speed, then recursion, trees, and DP will all feel like magic later. This
> module removes the magic. We start from bits and build up to Big-O, so you
> never have to memorise anything later — you will understand it.

This module is **P0** (most important). It appears directly in GATE/ISRO and
indirectly in *every* FAANG interview — the moment you say "this is O(n)", you
are using this module.

---

## 1.1 Computer & Memory Model (where does data live?)

### Definition

A computer stores everything — numbers, characters, instructions — as **bits**
(0/1). 8 bits = 1 **byte**. RAM (main memory) is basically one very long
**1-dimensional array of bytes**, and each byte has a unique **address**
(0, 1, 2, …).

![RAM is like a long street of lockers; each locker holds 1 byte and has a number (address).](images/01_ram_lockers.png)

### Intuition (simple example)

Think of RAM as a **long street of lockers**. Each locker holds 1 byte and has a
number (address). The CPU is a courier that does only two things:

1. *"Give me what is in locker #N"* → **read**
2. *"Put this into locker #N"* → **write**

**Every** data structure is, at heart, a clever scheme for *which lockers to use
and how to find them again.*

### Internal working — how `int x = 5;` is stored

When you write `int x = 5;`:

1. The compiler reserves space for `x` (a 32-bit int = 4 bytes).
2. It records in a table: name `x` → some address (say `1000`).
3. The value `5` is written in binary into those 4 bytes.

![The same number 5 can be laid out in bytes two ways: little-endian and big-endian.](images/02_endianness.png)

#### Endianness (an interview favourite)

The same integer `5` can be stored in its bytes in **two ways**:

- **Little-endian** (x86, ARM): smallest byte first → `05 00 00 00`
- **Big-endian** (network / internet order): biggest byte first → `00 00 00 05`

> **Why it matters:** If a big-endian machine writes a file/packet and a
> little-endian machine reads it without converting, you get **garbage**. This
> is why network protocols define a fixed byte order (`htonl`, `ntohl`).

### Two's complement (how negative numbers work)

Signed integers use **two's complement**: to negate a number, flip all bits and
add 1.

```
 5  =  0000 0101
-5  =  1111 1011     (flip 5's bits -> 1111 1010, then +1)
```

Why two's complement? Because addition "just works" with no special cases, and
there is only **one** representation of zero. A 32-bit `int` ranges from
`-2^31` to `2^31 - 1`, i.e. `-2,147,483,648 .. 2,147,483,647`.

> **The most common bug:** `INT_MAX + 1` **overflows** and becomes `INT_MIN`.
> In competitive programming this silently breaks `mid = (low + high) / 2`.
> **Fix:** `mid = low + (high - low) / 2`.

### Complexity

We treat one RAM access as **O(1)** (this is the "RAM model" used in CLRS and
most analysis). In reality, speed depends on caches (see §1.6).

### Common mistakes

- Assuming `int` is always 4 bytes — size is machine-dependent (use
  `int32_t`/`int64_t` when size matters).
- Forgetting overflow (e.g. `n*n` where `n` is an int but the product exceeds
  `2^31`).
- Confusing an **address** with a **value**.

### MCQs

1. On a little-endian machine, how is `0x01020304` stored?
   **(a)** `01 02 03 04`  **(b)** `04 03 02 01` → **Answer: (b)**
2. Range of a signed 32-bit int? → `-2^31 .. 2^31 - 1`
3. Why is `(low+high)/2` risky? → possible **integer overflow**.

---

## 1.2 Stack vs Heap (the single most important memory concept)

### Definition

A program's memory is divided into segments. The two that matter most for DSA:

- **Stack** — the area for function calls: local variables, parameters, return
  address. Managed **automatically** (LIFO — last in, first out). It grows on a
  call and shrinks on return.
- **Heap** — the area for *dynamic* memory (`malloc`/`new`). Managed
  **manually** (C/C++) or by a **garbage collector** (Java/Python/Go). Its
  lifetime is controlled by you/the GC, not by scope.

![A program's memory: Stack on top (grows down), Heap below (grows up), then globals and code.](images/03_stack_heap.png)

### Intuition (two simple examples)

- **Stack = a pile of plates.** A function call puts a plate (frame) on top.
  Returning removes the top plate. You can only touch the top plate. That is why
  it is *fast* (just move a pointer) and *automatic*.
- **Heap = a big warehouse.** You ask the manager (allocator) for a shelf of
  size N; it finds free space and gives you the address. You must return it
  (`free`/`delete`) — or the GC does it. Flexible, but slower and prone to
  leaks/fragmentation.

### Why it exists

The stack is perfect when data's lifetime matches the function call. But
sometimes data must **outlive the function** that made it (e.g. a function that
builds and returns a linked-list node), or its size is **only known at runtime**
(e.g. an array of `n` elements where `n` comes from input). That is what the
**heap** is for.

### Comparison table

| Property        | Stack                          | Heap                                |
|-----------------|--------------------------------|-------------------------------------|
| Allocation     | Move a pointer (1 instruction) | Find free space (allocator logic)   |
| Speed          | Very fast, cache-hot           | Slower; may need a syscall          |
| Lifetime       | Automatic (scope/LIFO)         | Manual (`free`) or GC               |
| Size           | Small (~1–8 MB)                | Large (most of RAM)                 |
| Fragmentation  | None                           | Possible                            |
| Threads        | Each thread has its own stack  | Shared across threads (needs locks) |
| Common error   | Stack overflow (deep recursion)| Memory leak, dangling pointer       |

### Dry run

```c
int* make() {
    int local = 10;        // on the STACK (inside make())
    int* p = malloc(4);    // 4 bytes on the HEAP
    *p = 99;
    return p;              // 'local' dies here; the heap block survives
}                          // returning &local would be a BUG (dangling pointer)
```

When `make()` returns, its stack frame (holding `local` and the pointer `p`) is
destroyed. But the **heap** block that `*p` points to still exists — that is why
returning `p` is fine, while returning `&local` is undefined behaviour.

### Production usage

- **C/C++:** prefer the stack/RAII; use the heap (`new`, smart pointers) only
  when needed.
- **Java/Python/Go:** objects live on the heap; locals/primitives on the stack;
  a GC reclaims unreachable objects.
- **Embedded/real-time:** the heap is often **banned** (unpredictable timing +
  fragmentation) → everything is pre-allocated.

### Common mistakes

- **Dangling pointer:** returning the address of a local.
- **Memory leak:** `malloc` with no matching `free`.
- **Double free / use-after-free:** classic security bugs (CWE-416/415).
- **Stack overflow:** unbounded / too-deep recursion.

### Interview perspective

> *"Where does `int a[1000000]` live, and why might it crash?"* — On the stack;
> 4 MB can exceed the default stack limit → segfault. Fix: allocate on the heap,
> or make it `static`/global. **Google/Meta** ask this to check that you know
> *where memory comes from.*

### MCQs

1. Recursion with no base case usually causes? → **stack overflow**
2. Which memory must be freed manually in C? → **heap**
3. Each thread gets its own ___? → **stack** (the heap is shared)

---

## 1.3 Variables, Functions & Pointers/References

### What is a variable?

A variable is a **named, typed box** in memory. The *type* tells the compiler two
things: (a) how many bytes, and (b) how to interpret those bytes (e.g. `float`
and `int` are both 4 bytes but mean different things).

### Pass by value vs pass by reference

![Pass by value makes a copy (caller unchanged); pass by reference passes the address of the same box (caller changes).](images/04_pass_by.png)

```c
void inc_val(int x) { x++; }       // a copy; caller is unaffected
void inc_ref(int* x){ (*x)++; }    // a pointer; caller's variable changes

int a = 5;
inc_val(a);   // a is still 5
inc_ref(&a);  // a is now 6
```

| Mechanism        | What is passed         | Cost            | Caller changes? |
|------------------|------------------------|-----------------|-----------------|
| By value         | A copy of the data     | O(data size)    | No              |
| By reference/ptr | The address (one word) | O(1)            | Yes             |

> **Why this matters in DSA:** Passing a large `vector`/array **by value** copies
> all `n` elements → an accidental O(n) per call, which can turn an O(n)
> algorithm into O(n²). In C++, pass big objects by `const&`. This is a *real*
> interview performance bug.

### MCQs

1. Passing a `std::vector<int>` by value n times in a loop? → a hidden **O(n)**
   copy each call.
2. To change the caller's variable in C, you pass? → its **address** (pointer).

---

## 1.4 Recursion (the heart of DSA)

### Definition

**Recursion** is when a function solves a problem by calling itself on a
**smaller** input, until it reaches a **base case** (the smallest input, solved
directly).

Two required ingredients:

1. **Base case** — the smallest input, solved without recursion (this stops the
   recursion).
2. **Recursive case** — shrinks the problem toward the base case and combines
   the sub-results.

### Intuition

Many structures are **self-similar**: a tree's subtree is a tree; a list's tail
is a list; `n!` = `n × (n−1)!`. Recursion lets the *code shape* match the
*problem shape* — short and clearly correct.

> **Mantra:** *"Assume the recursive call already works correctly for the smaller
> input"* (the recursive leap of faith / induction). Then you only need to handle
> (a) the base case and (b) combining one level correctly.

![Flowchart: every recursive call first checks the base case; if not, it does work, calls itself on a smaller input, combines, and returns.](images/20_fc_recursion.png)

### Internal working — the call stack & stack frames

Every function call pushes a **stack frame** (activation record) containing the
**parameters**, **local variables**, the **return address** (where to continue
in the caller), and saved registers. On return, the frame is **popped**. So
recursion uses **O(depth)** stack memory — even if it returns a single number.

![Factorial fact(4): calls go down (push), then results come up (pop). Depth = n.](images/05_recursion_stack.png)

### Dry run — factorial

```c
int fact(int n) {
    if (n <= 1) return 1;        // base case
    return n * fact(n - 1);      // recursive case
}
```

`fact(4)` is **linear** recursion → the recursion tree is a single chain of
depth `n`. First the calls go 4→3→2→1 (push), then the results come back
`1 → 2 → 6 → 24` (pop).

### Branching recursion — naive Fibonacci

```c
int fib(int n){ return n < 2 ? n : fib(n-1) + fib(n-2); }
```

![fib(5) tree: the orange nodes are calls that repeat — this wasted work is what DP fixes.](images/06_recursion_tree.png)

This tree has about `2^n` nodes → **O(φ^n)** time (φ ≈ 1.618). But at any moment
the stack depth is only **O(n)**. Notice the same subproblems (`fib(3)`,
`fib(2)`…) are computed again and again — this is exactly what motivates
**Dynamic Programming** (Module 14).

#### Brute force → Optimal (Fibonacci)

```text
# BRUTE FORCE: plain recursion        Time O(φ^n), Space O(n) stack
fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# BETTER: memoisation (top-down DP)    Time O(n), Space O(n)
memo = {}
fib(n):
    if n < 2: return n
    if n in memo: return memo[n]
    memo[n] = fib(n-1) + fib(n-2)
    return memo[n]

# OPTIMAL: iterative, two variables    Time O(n), Space O(1)
fib(n):
    a, b = 0, 1
    repeat n times:
        a, b = b, a + b
    return a
```

*Why each step helps:* memoisation removes the repeated subtrees (orange nodes);
the iterative version also drops the recursion stack down to two variables.

### Complexity (from the recurrence)

- `fact`: `T(n) = T(n−1) + O(1)` → **O(n)** time, **O(n)** stack
- `fib`:  `T(n) = T(n−1) + T(n−2) + O(1)` → **O(φ^n)** time
- Halving recursion: `T(n) = 2T(n/2) + O(n)` → **O(n log n)** (merge sort) —
  solved by the Master Theorem (Modules 12/18).

### Stack overflow

- Each frame costs some bytes; depth `d` → `O(d)` stack memory.
- The default stack is about 1 MB (Windows) / 8 MB (Linux). Recursing ~10⁵–10⁶
  deep can overflow → crash. In CP, deep DFS on a 10⁶-node graph may need an
  **explicit stack** or a larger stack limit.

### Tail recursion & converting to iteration

A call is **tail-recursive** if the recursive call is the *last* operation
(nothing pending after it returns).

```c
int fact_tail(int n, int acc) {       // tail recursive
    if (n <= 1) return acc;
    return fact_tail(n - 1, n * acc); // nothing happens after this call
}
```

Some compilers do **tail-call optimisation (TCO)** (reuse the same frame →
O(1) stack). C/C++ *may* (with `-O2`); **Python and Java do not**. Any recursion
can be turned into iteration with an **explicit stack** — a key interview skill
(iterative tree traversal, iterative DFS).

### Common mistakes

- **Wrong/missing base case** → infinite recursion → overflow.
- **Base case never reached** (recurse on `n` but never decrease it).
- **Recomputation** (Fibonacci) — fix with memoisation.
- **Changing shared state without restoring it** (a backtracking bug — Module 13).

### Production usage

Parsers, tree/graph traversal, divide-and-conquer (sort, FFT), file-system walks,
JSON traversal. In production, depth is bounded or converted to iteration so
adversarial input cannot crash it.

### Interview / CP / Exam perspective

- **Google/Meta:** "Write it recursively, then convert to iterative." Follow-up:
  **stack depth** and **overflow**.
- **Amazon:** clean base case + a complexity statement is a scored signal.
- **GATE/ISRO:** solve the recurrence; count the calls; find the stack depth.
- **CP:** iterative DFS / stack-size tricks; memoise to turn exponential into
  polynomial.

### MCQs

1. Naive `fib(n)` time? → **O(φ^n)** (exponential)
2. Max stack depth of `fact(n)`? → **O(n)**
3. Which language commonly does NOT optimise tail calls? → **Python**
4. Missing base case → ? → **stack overflow**

### Coding exercises (Easy → Hard)

- **Easy:** sum of first n natural numbers; reverse a string recursively; power
  `x^n`.
- **Medium:** Tower of Hanoi; generate all subsets; flatten a nested list.
- **Hard:** convert recursive DFS to iterative with an explicit stack;
  `fib`/grid-paths with memoisation; mutual recursion (is-even/is-odd).

---

## 1.5 Asymptotic Analysis — Big-O, Big-Θ, Big-Ω

### Why it exists

We need to compare algorithms **independent of hardware, language, and the
input's actual values** — looking only at how cost **grows** with input **size**
`n`. This notation answers: *"As n gets large, how fast does the cost grow?"*

![Different growth rates: O(1) and O(log n) stay flat; O(n²) and O(2ⁿ) shoot up fast.](images/07_bigo_growth.png)

### Definitions (precise, GATE-level)

Let `f(n)` be the actual cost and `g(n)` a reference function:

- **Big-O (upper bound):** `f(n) = O(g(n))` if constants `c>0, n₀` exist so that
  `0 ≤ f(n) ≤ c·g(n)` for all `n ≥ n₀`. *"f grows no faster than g."*
- **Big-Ω (lower bound):** `c·g(n) ≤ f(n)`. *"f grows at least as fast as g."*
- **Big-Θ (tight):** `f = O(g)` **and** `f = Ω(g)`. *"f grows exactly like g."*
- **little-o:** strictly slower (`lim f/g = 0`).

### Intuition — "drop constants and lower-order terms"

`3n² + 5n + 100` is really **Θ(n²)**: for large `n`, the `n²` term dominates;
constants (3) and lower terms (5n, 100) are noise. Big-O cares about the
**shape** of growth, not the exact count.

> **Subtle (for GATE):** "worst case" and "Big-O" are different ideas. You can
> give the Big-O of the *best* case too. In casual interview talk, "O" means
> "tight worst case", but remember the distinction.

### The growth ladder (memorise this)

| Notation     | Name          | n=10 | n=1000 | Example                       |
|--------------|---------------|------|--------|-------------------------------|
| O(1)         | constant      | 1    | 1      | array index, hashmap get      |
| O(log n)     | logarithmic   | ~3   | ~10    | binary search                 |
| O(n)         | linear        | 10   | 1000   | single loop                   |
| O(n log n)   | linearithmic  | ~33  | ~10⁴   | merge sort, good sorts        |
| O(n²)        | quadratic     | 100  | 10⁶    | nested loops, bubble sort     |
| O(n³)        | cubic         | 1000 | 10⁹    | Floyd-Warshall, naive matmul  |
| O(2ⁿ)        | exponential   | 1024 | huge   | subsets, naive fib            |
| O(n!)        | factorial     | 3.6M | huge   | permutations, brute TSP       |

Order: `1 < log n < √n < n < n log n < n² < n³ < 2ⁿ < n!`

### Logarithm refresher (why `log n` keeps appearing)

A logarithm answers: *"how many times do I divide n by 2 before I reach 1?"* —
that count is `log₂ n`. So **anything that halves the problem each step is
O(log n)** (binary search, balanced trees, heap height).

> **Memory hook:** `log₂(1,000,000) ≈ 20`. A million items → only ~20 steps to
> binary-search. That is why `log n` is almost as good as constant time.

Useful rules (handy for GATE):

- `log(a·b) = log a + log b`,  `log(a/b) = log a − log b`,  `log(aᵏ) = k·log a`
- Base doesn't matter for Big-O: `log₂ n` and `log₁₀ n` differ by a constant, so
  both are just `O(log n)`.
- `2^(log₂ n) = n`. A tree of height `h` has up to `2^h` nodes → `n` nodes ⇒
  height `log₂ n`.

### Proof example

**Claim:** `3n² + 5n + 100 = O(n²)`.
**Proof:** take `c = 5, n₀ = 10`. For `n ≥ 10`: `5n ≤ n²` and `100 ≤ n²`, so
`3n² + 5n + 100 ≤ 3n² + n² + n² = 5n²`. Hence `O(n²)`. (Also `= Ω(n²)`, so
`Θ(n²)`.) ∎

### Recipe to analyse code

![Flowchart: a quick decision tree to read off the Big-O of a piece of code.](images/19_fc_complexity.png)

1. **Sequential statements** → add: `O(a) + O(b) = O(max(a,b))`
2. **A loop** → multiply by the iteration count
3. **Nested loops** → multiply the nesting
4. **Recursion** → write a recurrence, then solve it
5. Keep the **dominant** term; drop constants

```c
// O(n^2): outer n times, inner n times
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        work();

// i doubles each step => log n iterations => O(log n)
for (int i = 1; i < n; i *= 2)  work();
```

> **Space complexity — same recipe.** Count the *extra* memory you allocate as a
> function of `n` (do not count the input itself unless asked). Recursion's stack
> counts: a recursion of depth `d` uses **O(d)** space even if it returns one
> number. Example: building a hashset of all elements = O(n) space; an in-place
> two-pointer scan = O(1) space.

### Recurrences & the Master Theorem (for divide-and-conquer)

When a function splits its input, its running time is a **recurrence** like
`T(n) = a·T(n/b) + f(n)` — `a` sub-calls, each on size `n/b`, plus `f(n)` work to
split/combine. The **Master Theorem** reads off the answer by comparing `f(n)`
with `n^(log_b a)`:

![Master Theorem: compare f(n) with n^(log_b a); the three cases give the final bound.](images/28_master_theorem.png)

The most useful case is **merge sort**: `T(n) = 2T(n/2) + n`. Here each *level*
of the recursion tree costs `n`, and there are `log n` levels → **O(n log n)**:

![Merge-sort recurrence tree: each level totals n, and there are log n levels, so the total is n log n.](images/29_mergesort_tree.png)

> **Memory hook:** *"work per level × number of levels."* For merge sort that is
> `n × log n`. This single picture explains why all good comparison sorts are
> `O(n log n)`.

### Time vs Space tradeoff

You can often **buy speed with memory**, or the reverse:

- A hash set makes lookups O(1) → costs O(n) extra space (Two-Sum).
- Memoisation stores sub-results → faster but more memory (DP).
- In-place algorithms save memory but may be slower or destroy the input.

> **A line that scores in interviews:** *"We can trade space for time here — a
> hashmap takes this from O(n²) to O(n), at the cost of O(n) memory."*

### Amortised analysis (preview)

Some operations are *occasionally* expensive but *cheap on average over a
sequence*. Classic: appending to a **dynamic array** — usually O(1), but O(n)
when it doubles. Averaged over many appends → **O(1) amortised**. (Full
treatment: Module 18.) Don't confuse *amortised* (guaranteed average over a
sequence) with *average-case* (probability over inputs).

### Common mistakes

- Writing "O(2n)" — you forgot to drop the constant.
- Confusing **worst** vs **average** (quicksort: O(n²) worst, O(n log n)
  average).
- The "size" of a number `m` is `log m` bits → "pseudo-polynomial" algorithms
  (knapsack O(nW)).
- Forgetting space when only time was asked (interviewers expect both).

### Production usage

Asymptotics decide scalability: an O(n²) function is fine at n=1000 but dies at
n=10⁷. But for small n, an O(n²) algorithm with tiny constants can beat an
O(n log n) one (that is why Timsort uses insertion sort on small runs).

### MCQs

1. `T(n) = 2T(n/2) + n` solves to? → **Θ(n log n)**
2. Tight bound of `n + log n`? → **Θ(n)**
3. Is `n² = O(n³)`? → **Yes** (O is an upper bound, not tight)
4. Worst case of quicksort? → **O(n²)**
5. `for(i=1;i<n;i*=2)` runs how many times? → **≈ O(log n)**

---

## 1.6 Cache Friendliness (the hidden "constant")

### Why it matters

The RAM model says every access is O(1). **Reality:** memory has a **hierarchy**
with very different speeds. Two algorithms with the *same* Big-O can differ 10×
in wall-clock time, purely due to cache behaviour. FAANG senior/staff and
NVIDIA/HFT interviews probe this.

![Memory hierarchy: small and fast at the top (registers/cache), big and slow at the bottom (RAM/disk).](images/08_cache_hierarchy.png)

### Two principles of locality

- **Spatial locality:** if you access address X, you will likely access X+1 soon.
  The CPU loads a whole **cache line** (~64 bytes) at once.
- **Temporal locality:** recently used data is likely reused soon → keep it in
  cache.

### Practical consequences (interview gold)

![An array is contiguous (one cache line holds many elements); a linked list is scattered (each node is a cache miss).](images/09_array_vs_list.png)

- **Array beats linked list** for traversal even at the same O(n): array
  elements sit together (many per cache line), while list nodes are scattered
  (a cache miss per node). This is why `std::vector` usually beats `std::list`.
- **Row-major vs column-major:** in C, iterating `a[i][j]` with `j` in the inner
  loop is cache-friendly (row-major); swapping the loops can be **5–10× slower**
  for the same Big-O.

```c
// CACHE-FRIENDLY (row-major C/C++)
for (i...) for (j...) sum += a[i][j];

// CACHE-HOSTILE (same O(n^2), but much slower)
for (j...) for (i...) sum += a[i][j];
```

### MCQs

1. Why does `vector` beat `list` at the same O(n)? → **contiguous memory →
   spatial locality → fewer cache misses.**
2. Cache-friendly 2D loop order in C? → **i outer, j inner** (row-major).

---

## Module 1 — Concept Review (one page)

- Memory = addressable bytes; the type interprets the bytes; signed ints use
  two's complement; beware **overflow**.
- **Stack** (auto, fast, LIFO, per-thread, small) vs **Heap** (manual/GC,
  flexible, large, can fragment). Returning a local's address = bug.
- Pass-by-value copies (cost!); by-reference shares. Pass big objects by `const&`.
- **Recursion** = base case + smaller subproblem; uses O(depth) **stack**;
  recurrence gives the time; watch overflow and recomputation.
- **Asymptotics:** O (upper), Ω (lower), Θ (tight). Drop constants/lower terms.
  Memorise the growth ladder. Analyse with the recipe.
- **Cache:** same Big-O ≠ same speed; prefer contiguous, locality-friendly access.

## Module 1 — Flash Cards (revision)

- Q: `INT_MAX+1`? **A: INT_MIN (overflow).**
- Q: Safe midpoint? **A: `low + (high-low)/2`.**
- Q: Where do locals live? **A: stack.** The heap needs `free`/GC.
- Q: Stack space for recursion depth d? **A: O(d).**
- Q: `2T(n/2)+n`? **A: Θ(n log n).**
- Q: Growth order? **A: 1 < log n < √n < n < n log n < n² < 2ⁿ < n!.**
- Q: Array vs list speed at the same O(n)? **A: array — cache locality.**

## Module 1 — Pattern Recognition

- "Change the caller's variable" → pass a pointer/reference.
- "Self-similar problem (tree/list/`n!`)" → recursion.
- "Same subproblem computed again" → memoise → DP.
- "Nested loops over n" → suspect O(n²); look for hashing/two-pointer to cut it.
- "Need O(1) lookup" → trade space for time with a hashset/hashmap.

## Module 1 — Interview Questions (with follow-ups)

1. *Explain stack vs heap.* FU: *where does `int a[10⁶]` go and why might it
   crash?*
2. *What is two's complement and why?* FU: *what is the negation of `INT_MIN`?*
3. *Convert this recursion to iteration.* FU: *what is the stack depth?*
4. *Define Big-O vs Big-Θ.* FU: *prove `3n²+5n = Θ(n²)`.*
5. *Why is vector faster than list here?* FU: *what is a cache line?*

## Module 1 — GATE / SEBI / RBI / ISRO Perspective

- **Very common:** solving recurrences, identifying the Θ of code with loops,
  two's-complement ranges, the contents of an activation record, recursion depth,
  and comparing growth rates.
- **SEBI/RBI IT:** conceptual MCQs on time complexity, stack vs heap, recursion.

---

*End of Module 1. Next: Module 2 — Arrays (internals, prefix sums, two pointers,
sliding window, Kadane, Dutch National Flag, matrix) — with visuals.*
