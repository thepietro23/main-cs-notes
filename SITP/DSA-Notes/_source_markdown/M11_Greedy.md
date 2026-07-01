---
title: "Module 11 — Greedy Algorithms"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — Greedy Algorithms

> **Why greedy matters (and why it's dangerous).**
> A **greedy** algorithm builds a solution one step at a time, always taking the
> choice that looks best **right now**, and never reconsidering. When it works,
> it's beautifully simple and fast. The danger: it is **often wrong**, and the
> hard part of an interview/exam is **proving** it's correct (or spotting that it
> isn't). This module teaches the classic greedy algorithms, the **theory of why
> greedy works** (matroids), and how to tell when greedy is safe.

This module is **P1**: greedy + interval problems are common at FAANG, and
greedy/exchange-argument proofs + Huffman numericals are GATE favourites.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

### Quick "can I use greedy?" selector

![Flowchart: greedy is valid only if a local best stays globally best; otherwise use DP.](images/94_fc_greedy.png)

---

## 11.1 The Greedy Idea (and how to trust it)

### Definition

A **greedy algorithm** makes a sequence of choices, each the **locally optimal**
one, hoping to reach a **globally optimal** solution. It **never backtracks**.

![Greedy takes the locally best choice; it works only with the greedy-choice property, and can fail (coins {1,3,4} for 6).](images/90_greedy_concept.png)

### When is greedy correct? (two properties)

1. **Greedy-choice property:** a globally optimal solution can be reached by
   making locally optimal choices. (The local best is *safe*.)
2. **Optimal substructure:** an optimal solution contains optimal solutions to
   subproblems.

If both hold, greedy is optimal. **DP also needs optimal substructure**, but DP
additionally explores choices — greedy commits to one. So greedy is "DP that's
allowed to never look back".

### Two proof styles (know both)

- **Exchange argument:** take any optimal solution, **swap** one of its choices
  for the greedy choice, show it's no worse; repeat until it *becomes* the greedy
  solution. (Used below for activity selection and Huffman.)
- **"Greedy stays ahead":** by induction, after `k` steps greedy is **at least as
  far along** as any other solution. (The cleanest proof for earliest-finish
  activity selection.)

### When greedy FAILS — always have a counterexample ready

- **Coin change** with coins `{1, 3, 4}` to make `6`: greedy takes `4+1+1` (3
  coins), but `3+3` (2 coins) is better. → needs **DP** (Module 14).
- **0/1 knapsack** (can't split items): greedy by ratio fails → **DP** (see §11.4
  for the exact numbers).

> **The flip side — when greedy coin change WORKS:** a coin system is
> **canonical** if greedy gives the fewest coins for *every* amount. Standard
> currencies like `{1, 5, 10, 25}` are canonical (each larger coin is a clean
> multiple), so greedy is optimal there. Arbitrary systems like `{1, 3, 4}` are
> not. Whether a system is canonical can be checked in polynomial time (Pearson's
> test); in general, "fewest coins" needs **DP**.

> **Interview rule:** never *assume* greedy works. Either give a one-line proof
> (exchange / stays-ahead) or test a counterexample. If it fails, fall back to
> **DP**.

### How to actually WRITE an exchange-argument proof (4-step recipe)

Examiners want the *structure*, not hand-waving. Every exchange proof follows the
same four beats — memorise them:

1. **Assume** an optimal solution `OPT` that **differs** from the greedy one `G`.
2. **Locate the first place they differ** (the first choice greedy makes that
   `OPT` does not).
3. **Exchange** that one choice in `OPT` for the greedy choice, and argue the
   result is **still valid and no worse** (same or better objective).
4. **Repeat / induct:** each exchange makes `OPT` agree with `G` one step more,
   without hurting it. After finitely many swaps `OPT` becomes `G`, so `G` is also
   optimal. ∎

> **Memory hook:** "**Assume, Find first diff, Swap-no-worse, Repeat**" — the same
> skeleton proves activity selection, Huffman, EDF lateness, and MST.

### Why greedy coin change fails — the actual trace

Coins `{1, 3, 4}`, target `6`. Greedy always grabs the **largest coin ≤ remaining**:

```text
remaining = 6 -> take 4 (largest <=6), remaining = 2
remaining = 2 -> take 1 (no 3 or 4 fits),  remaining = 1
remaining = 1 -> take 1,                    remaining = 0
greedy answer = {4,1,1} = 3 coins
optimal       = {3,3}   = 2 coins   (greedy is WORSE by 1 coin)
```

The greedy choice `4` was **locally** best but **globally** wrong: taking `4`
strands a remainder (`2`) that only `1`-coins can pay. No exchange argument works
because the choice is not safe → the greedy-choice property **fails** → use **DP**.

> **Memory hook:** a greedy hiker always steps uphill — great for reaching a
> nearby peak, but it can get stuck on a **small hill** instead of Everest (a
> local, not global, optimum).

### MCQs

1. Two properties that justify greedy? → **greedy-choice** + **optimal
   substructure**.
2. Two standard greedy proof styles? → **exchange argument** + **greedy stays
   ahead**.
3. Coins {1,3,4} make 6 — greedy vs optimal? → **3 coins vs 2 coins** (greedy
   fails); but `{1,5,10,25}` is **canonical** (greedy works).

---

## 11.1b Matroids — the Theory Behind Greedy (why it works)

Greedy is not magic: there is a precise structure that *guarantees* greedy
optimality, called a **matroid**.

### Definition

A **matroid** is a ground set `E` with a family `I` of "independent" subsets
satisfying:

1. **Hereditary (downward-closed):** every subset of an independent set is
   independent.
2. **Exchange/augmentation:** if `A, B ∈ I` with `|A| < |B|`, then some element of
   `B \ A` can be added to `A` keeping it independent.

**Rado–Edmonds theorem:** the greedy algorithm (sort elements by weight, add each
if it keeps the set independent) finds a **maximum-weight independent set** **if
and only if** the structure is a matroid. This is the deep reason greedy works.

### The canonical example (ties to Module 10b)

- **Graphic matroid:** `E` = edges of a graph; "independent" = acyclic (a forest).
  Greedy on this = **Kruskal's MST**! That is *why* Kruskal is correct.
- Activity selection and job-scheduling-with-deadlines also fit matroid-like
  structures.

> **Memory hook:** a matroid is the "shape" of problems where **greedy is
> guaranteed safe** — and Kruskal's MST is the poster child.

### MCQs

1. Theorem linking greedy and matroids? → **Rado–Edmonds** (greedy optimal ⇔
   matroid).
2. The graphic matroid's greedy algorithm is? → **Kruskal's MST**.

---

## 11.2 Interval Problems (scheduling, partitioning, merging)

There are **three different** interval problems — don't confuse them.

### (A) Interval Scheduling — maximise count (activity selection)

Select the **maximum number** of non-overlapping intervals (one resource).
**Sort by earliest finish time**, then take each interval that starts after the
last chosen one ends.

![Activity selection: sort by earliest finish time, then greedily take each activity starting after the last one ends.](images/91_activity_selection.png)

```text
# OPTIMAL                                    Time O(n log n) (sort), O(n) scan
sort intervals by finish time
last_end = -infinity; count = 0
for (start, end) in intervals:
    if start >= last_end:
        take it; count += 1; last_end = end
```

**Worked example.** Activities (start,finish):
`(1,4)(3,5)(0,6)(5,7)(3,9)(5,9)(6,10)(8,11)(8,12)(2,14)(12,16)` — already sorted
by finish. Trace `last_end`:

- take (1,4) → last_end=4 · skip (3,5),(0,6) · take **(5,7)** → 7 · skip
  (3,9),(5,9),(6,10) · take **(8,11)** → 11 · skip (8,12),(2,14) · take
  **(12,16)** → 16.
- Selected = `{(1,4),(5,7),(8,11),(12,16)}`, **count = 4**.

**Why optimal (greedy stays ahead):** the earliest-finishing activity leaves the
most room. After each pick, greedy's finish time is ≤ any other solution's →
greedy never falls behind.

> **Memory hook:** at a film festival, always watch the movie that **ends
> soonest** to fit in the most movies.

### (B) Interval Partitioning — minimise resources (meeting rooms)

Schedule **ALL** intervals using the **fewest rooms**. The answer equals the
**maximum overlap depth** (most intervals active at one time) — and that's a
matching lower bound.

```text
# Minimum meeting rooms (LC 253)             Time O(n log n)
sort intervals by start time
min-heap of end times
for (start, end) in intervals:
    if heap not empty and heap.top <= start: heap.pop()   # a room freed up
    heap.push(end)
answer = heap size at the end        # = max simultaneous overlap
```

### (C) Interval Merging (LC 56 / 57)

Merge all **overlapping** intervals. **Sort by start**, sweep, and extend the
current interval when the next one starts at/before the current end.

```text
# Merge Intervals                            Time O(n log n)
sort by start
result = [first]
for next in rest:
    if next.start <= result.last.end:
        result.last.end = max(result.last.end, next.end)   # overlap -> extend
    else:
        result.append(next)
# Insert Interval (LC 57): merge the new interval into an already-sorted list in O(n)
```

> **Interview trap:** **unweighted** interval scheduling is greedy (earliest
> finish). **Weighted** interval scheduling (each interval has a profit, maximise
> total profit) is **NOT greedy** — it needs **DP** (sort by finish + binary
> search for the last compatible interval). Same flavour as fractional-vs-0/1
> knapsack.

### MCQs

1. Max non-overlapping intervals — sort by? → **earliest finish time**.
2. Min rooms equals? → **maximum overlap depth**.
3. Weighted interval scheduling? → **DP**, not greedy.

### Problems

- Non-overlapping Intervals (435); Meeting Rooms I/II (252/253); Merge Intervals
  (56); Insert Interval (57); Minimum Arrows to Burst Balloons (452 — sort by
  end, count non-overlapping shots); Maximum Length of Pair Chain (646).

---

## 11.3 Huffman Coding (optimal prefix codes)

### Problem

Compress data: give **frequent** characters **short** codes and rare ones long
codes, with no code a prefix of another (so decoding is unambiguous). Minimise
total bits.

![Huffman coding: repeatedly merge the two lowest-frequency nodes; frequent letters end up near the root with short codes.](images/92_huffman.png)

### The greedy choice + the two lemmas

**Repeatedly merge the two lowest-frequency nodes** (use a **min-heap**) into a
new node with their summed frequency, until one tree remains. Left = `0`, right =
`1`.

```text
# Huffman                                    Time O(n log n)
min-heap of all (frequency, node)
while heap has > 1 node:
    a = pop-min; b = pop-min
    merge into a node with frequency a.freq + b.freq; push it
the remaining node is the root; read codes off the paths
```

**Why it's optimal (two lemmas):**

1. The two **lowest-frequency** symbols can be made **sibling leaves at maximum
   depth** in *some* optimal tree (exchange argument on depth).
2. **Optimal substructure:** merging them and optimally coding the smaller
   instance yields an optimal tree for the original.

### Worked numeric example (the classic GATE numerical)

Frequencies: `a:5, b:9, c:12, d:13, e:16, f:45` (total = 100). Merge the two
smallest each step:

| Step | Merge | New node |
|---|---|---|
| 1 | a(5) + b(9) | **14** |
| 2 | c(12) + d(13) | **25** |
| 3 | 14 + e(16) | **30** |
| 4 | 25 + 30 | **55** |
| 5 | f(45) + 55 | **100** (root) |

Resulting codes & lengths: `f=0` (1), `c=100` (3), `d=101` (3), `a=1100` (4),
`b=1101` (4), `e=111` (3).

- **Total bits** = Σ(freq × len) = 45·1 + 12·3 + 13·3 + 5·4 + 9·4 + 16·3
  = 45+36+39+20+36+48 = **224 bits**.
- **Fast trick (memorise for GATE):** total bits = **sum of all internal-node
  frequencies created during merging** = 14+25+30+55+100 = **224**. ✓ (same
  answer, no per-symbol arithmetic!)
- **Average code length** = 224 / 100 = **2.24 bits/symbol** (vs a fixed 3-bit
  code for 6 symbols → 300 bits; Huffman saves 25%).

### Key Huffman facts (exam)

- `n` symbols → **n−1 merges**, **2n−1 total nodes**.
- The code is **not unique** (depends on tie-breaking), but the **total bits /
  average length are unique**.
- It produces an **optimal prefix (prefix-free) code**.

### MCQs

1. Huffman merges which two nodes each step? → the **two smallest frequencies**.
2. Total-bits shortcut? → **sum of all internal-node frequencies**.
3. n symbols → how many nodes/merges? → **2n−1 nodes, n−1 merges**.

---

## 11.4 Fractional vs 0/1 Knapsack (the trap)

### Fractional knapsack — greedy is OPTIMAL

A knapsack of capacity `W`; items have value and weight; you **may take
fractions**. **Sort by value/weight ratio (descending)**; take whole items, then
a fraction of the last.

![Fractional knapsack: sort by value/weight ratio and fill greedily, taking a fraction of the last item.](images/93_fractional_knapsack.png)

**Worked example.** `W = 50`; items A(v=60,w=10), B(v=100,w=20), C(v=120,w=30).
Ratios: A=6, B=5, C=4 → order A,B,C.

- Take A (10kg, +$60) → used 10, value 60.
- Take B (20kg, +$100) → used 30, value 160.
- Room left = 20kg of C: take 20/30 of C → +$80 → **total value = $240**. ✅
  (greedy optimal for fractional).

### 0/1 knapsack — greedy FAILS, use DP

Same items, but items are **indivisible**:

- **Greedy by ratio** takes A+B (30kg, $160), can't fit C (30kg > 20 left) →
  **$160**.
- **Optimal (DP)** takes B+C (50kg exactly, $220) → **$220 > $160**. Greedy is
  **wrong** by $60.

> **This exact contrast is a favourite interview/exam trap.** Splittable → greedy
> by ratio. Indivisible → **DP** (Module 14).

> **Memory hook:** a thief stealing **gold dust** (pourable) grabs densest value
> first; a thief stealing **whole statues** (0/1) can't — that needs DP.

### MCQs

1. Fractional knapsack sort key & complexity? → **value/weight ratio, O(n log n)**.
2. 0/1 knapsack greedy result vs optimal (above)? → **$160 vs $220** → use **DP**.

---

## 11.5 Scheduling Greedy: Job Sequencing, Min Lateness, MST

### Job sequencing with deadlines (maximise profit)

Each job: **deadline** + **profit**, takes 1 time unit. **Sort by profit
descending**; place each job in the **latest free slot ≤ its deadline**.

**Worked example.** Jobs (deadline, profit): J1(2,100), J2(1,19), J3(2,27),
J4(1,25), J5(3,15). Sort by profit (descending): **J1(100), J3(27), J4(25),
J2(19), J5(15)**. Use 3 time slots [1,2,3]:

- J1 d=2 → latest free slot ≤2 = **slot 2**. · J3 d=2 → latest free ≤2 = **slot
  1**. · J4 d=1 → slot 1 taken → **skip**. · J2 d=1 → slot 1 taken → **skip**. ·
  J5 d=3 → **slot 3**.
- Scheduled: J1, J3, J5 → **profit = 100+27+15 = 142**. Complexity **O(n log n)**
  with a slot array (≈ O(n·α(n)) with union-find for the "latest free slot").

### Minimize maximum lateness — Earliest Deadline First (EDF)

Single machine; each job has processing time `t` and deadline `d`; lateness
`Lⱼ = max(0, finishⱼ − dⱼ)`. To **minimise the maximum lateness**: **sort by
deadline ascending (EDF)** and run jobs back-to-back with **no idle time**.

**Why (exchange argument):** an optimal schedule with no idle time and no
"inversions" exists; swapping any adjacent out-of-deadline-order pair never
increases the max lateness. *(Different from job sequencing — that maximises
profit and sorts by profit; this minimises lateness and sorts by deadline.)*

### MST is greedy (closing the loop with Module 10b)

Both MST algorithms are greedy, justified by the **cut property** (the cheapest
edge crossing any partition is safe):

- **Kruskal:** repeatedly add the globally **smallest** edge that doesn't form a
  cycle (union-find). This is exactly **greedy on the graphic matroid** (§11.1b).
- **Prim:** repeatedly add the smallest edge **crossing the cut** between the
  built tree and the rest.

MST has both the greedy-choice property and optimal substructure → greedy is
provably optimal.

### Dijkstra is greedy too (shortest paths)

**Dijkstra's shortest-path** algorithm (Module 10b) is the other famous greedy on
graphs. It repeatedly **finalises the unvisited vertex with the smallest tentative
distance** — once a vertex is popped from the min-heap, its distance is *locked in*
and never reconsidered. That "pop-the-nearest and commit" step is the greedy
choice.

- **Why it's correct:** when the closest unfinalised vertex `u` is popped, no
  shorter path to `u` can exist through a still-unfinalised vertex, because every
  such vertex is already **farther** than `u` and edge weights are
  **non-negative**. So committing to `u`'s distance is safe. This is an
  exchange-style argument.
- **The catch:** the proof **needs non-negative weights**. With a negative edge, a
  later, longer-looking path can turn out cheaper, breaking the greedy choice — so
  Dijkstra fails and you need **Bellman–Ford** (a DP, Module 10b).

> **Memory hook:** Prim and Dijkstra are twins — both "grow a set, always pull in
> the nearest outside vertex via a min-heap." Prim compares **edge weight**;
> Dijkstra compares **distance from source**.

### Other classic greedy problems (recognise the choice)

| Problem | Greedy choice |
|---|---|
| **Gas Station (134)** | if total gas ≥ total cost, a valid start is right after the lowest running deficit |
| **Jump Game (55)** | track the farthest reachable index; reachable iff it never falls behind `i` |
| **Jump Game II (45)** | extend the current "level" like BFS; count levels |
| **Best Time Buy/Sell II (122)** | sum every positive day-to-day gain |
| **Candy (135)** | two passes (L→R, R→L), take the max |
| **Task Scheduler (621)** | schedule the most frequent task first; fill idle gaps |
| **Reorganize String (767)** | repeatedly place the most frequent remaining char (max-heap) — sibling of Task Scheduler |
| **Partition Labels (763)** | extend the partition to the last occurrence of each seen char |
| **Assign Cookies (455)** | sort both; give the smallest sufficient cookie |

**Gas Station correctness (1 line):** if total gas ≥ total cost a solution
exists; any prefix whose running tank goes negative **cannot contain the start**,
so restart right after it. *(Note: the start need not be unique — e.g.
gas=cost everywhere gives several valid starts; the algorithm returns one.)*

**Jump Game correctness (1 line):** induct on `farthest = max(farthest, i +
nums[i])`; you can reach the end iff `farthest` never drops below the current
index `i`.

> **Pattern:** most greedy problems reduce to **"sort by the right key, then make
> one pass."** Finding *the right key* (finish time, ratio, deadline, frequency)
> is the whole game.

### MCQs

1. Minimise max lateness — sort by? → **deadline (EDF)**.
2. Job sequencing — sort by? → **profit**, place in latest free slot ≤ deadline.
3. Why are Kruskal/Prim greedy-correct? → the **cut property** (matroid).
4. Best Time to Buy/Sell Stock II greedy? → **sum all positive deltas**.
5. Dijkstra is greedy — its greedy choice? → **finalise the nearest unvisited
   vertex** (min-heap); needs **non-negative** weights.

### Problems

- Gas Station (134); Jump Game I/II (55/45); Best Time Buy/Sell II (122); Candy
  (135); Task Scheduler (621); Reorganize String (767); Partition Labels (763);
  Assign Cookies (455); Job Sequencing (classic).

---

## 11.6 Stable Matching — Gale–Shapley (greedy-flavoured)

### Problem

`n` proposers and `n` acceptors, each with a ranked preference list. Find a
**matching with no unstable pair** — no two people who both prefer each other
over their assigned partners. (Real use: the **medical residency match / NRMP**.)

### Algorithm (propose-and-reject)

```text
# Gale-Shapley                               Time O(n^2)
while some proposer is free:
    p proposes to the next acceptor on p's list it hasn't tried
    if that acceptor is free: tentatively match
    else if the acceptor prefers p to its current match: switch (old one is freed)
    else: reject p
```

**Key facts:** always terminates in ≤ `n²` proposals, always produces a **stable**
matching, and is **proposer-optimal** (every proposer gets the best partner
possible in any stable matching). It's "greedy" in spirit: each proposer always
goes for its best remaining option.

### MCQs

1. Gale–Shapley produces a? → **stable matching** (proposer-optimal).
2. Time complexity? → **O(n²)**.

---

## Module 11 — Concept Review (one page)

- **Greedy** = locally best choice, never backtrack; correct **only** with the
  **greedy-choice property** + **optimal substructure**; prove via **exchange
  argument** or **greedy-stays-ahead**, or break it with a **counterexample**.
- **Matroids** (Rado–Edmonds) are the exact structures where greedy is
  guaranteed optimal; **Kruskal's MST = greedy on the graphic matroid**.
- **If greedy fails → DP** (coins {1,3,4}→6; 0/1 knapsack; weighted interval
  scheduling). Canonical coin systems {1,5,10,25} are greedy-OK.
- **Intervals:** scheduling (max count → sort by finish); partitioning (min rooms
  = max overlap); merging (sort by start, sweep).
- **Huffman:** merge two smallest (min-heap), O(n log n); total bits = Σ(freq×len)
  = Σ(internal-node freqs); n symbols → 2n−1 nodes, n−1 merges.
- **Fractional knapsack** = greedy (ratio); **0/1 knapsack** = DP.
- **Scheduling:** job sequencing (sort by profit, latest slot); min max lateness
  (EDF, sort by deadline).
- **Theme:** most greedy = **sort by the right key + one pass**.

## Module 11 — Flash Cards

- Q: When is greedy correct? **A: greedy-choice + optimal substructure (formally:
  a matroid).**
- Q: Two proof styles? **A: exchange argument; greedy stays ahead.**
- Q: Greedy counterexample / when it works? **A: coins {1,3,4}→6 fails; {1,5,10,25}
  canonical works.**
- Q: Activity selection sort key? **A: earliest finish time.**
- Q: Min meeting rooms = ? **A: max overlap depth (min-heap of end times).**
- Q: Huffman total bits shortcut? **A: sum of all internal-node frequencies.**
- Q: Fractional vs 0/1 knapsack? **A: ratio-greedy vs DP.**
- Q: Min max lateness? **A: EDF (sort by deadline).**
- Q: Kruskal correct because? **A: cut property (graphic matroid).**
- Q: Exchange-argument recipe? **A: Assume OPT differs; find first diff; swap in
  the greedy choice no-worse; repeat until OPT = greedy.**
- Q: Dijkstra greedy choice & precondition? **A: pop the nearest unvisited vertex;
  needs non-negative edges (else Bellman-Ford).**

## Module 11 — Pattern Recognition

- "Maximum non-overlapping intervals" → **sort by finish**; "fewest rooms" →
  **max overlap / min-heap**; "merge overlaps" → **sort by start, sweep**.
- "Optimal prefix code / compression" → **Huffman (min-heap)**.
- "Maximise value, splittable" → **fractional knapsack**; *not* splittable or
  *weighted* intervals → **DP**.
- "Schedule by deadline/profit" → **job sequencing** (profit) / **EDF** (lateness).
- "Can I reach / fewest jumps / fill gaps" → **greedy reachability**.
- "Connect everything cheaply" → **MST (greedy / cut property)**.
- "Stable pairing / matching" → **Gale–Shapley**.
- "Can't prove the local choice is safe" → **switch to DP**.
- "Prove this greedy is optimal" → **exchange argument** (assume OPT differs, swap
  in greedy choice no-worse, repeat) or **greedy-stays-ahead**.
- "Shortest path, non-negative weights" → **Dijkstra** (greedy); negative edges →
  **Bellman–Ford**.

## Module 11 — Interview Questions (with follow-ups)

1. *Activity selection.* FU: *prove the earliest-finish choice via greedy-stays-
   ahead.*
2. *Jump Game.* FU: *min jumps (II); why is it BFS-like? prove the invariant.*
3. *Gas station.* FU: *prove the algorithm returns a valid start when total gas ≥
   total cost (note: start need not be unique).*
4. *Fractional vs 0/1 knapsack.* FU: *give numbers where 0/1 greedy is wrong.*
5. *Meeting Rooms II.* FU: *min-heap solution; why does heap size = rooms?*
6. *Huffman.* FU: *compute total bits & average length; prove the two-lemma
   optimality.*

## Module 11 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** **Huffman** (build the tree, total bits / average code
  length — the internal-node-sum shortcut), **proving/refuting** greedy,
  activity selection traces, fractional-vs-0/1 knapsack contrast, **MST as
  greedy / cut property**, and **matroid**-based "why greedy works" theory.
  Exchange-argument reasoning recurs in analysis questions.

---

*End of Module 11. Next: Module 12 — Divide & Conquer (merge sort, quicksort,
quickselect, binary search, closest pair, master theorem in action) — with
visuals.*
