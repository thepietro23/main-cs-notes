---
title: "Module 10b — Graphs: Shortest Paths & MST"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10b — Graphs: Shortest Paths & MST

> **Why this part is interview & GATE gold.**
> "Find the cheapest route" is everywhere — maps, networks, flight prices,
> currency arbitrage. The trick is **choosing the right algorithm** for the
> constraints (negative edges? all pairs? unweighted?). This part covers the four
> shortest-path algorithms and the two MST algorithms, and exactly **when to use
> each**.

This module is **P0**. Dijkstra and "which algorithm when" are top FAANG +
GATE topics.

### Quick selector

![Flowchart: pick MST, BFS/0-1 BFS, Floyd-Warshall, Bellman-Ford, or Dijkstra based on the constraints.](images/84_fc_shortest_path.png)

> **First rule:** **unweighted graph → just BFS** (Module 10a). Weighted →
> read on.

---

## 10b.1 Dijkstra's Algorithm (non-negative weights)

### The idea

Grow shortest distances outward from the source, always **settling the closest
unsettled node next** (greedy), using a **min-heap** (priority queue). Once a node
is settled, its distance is final.

![Dijkstra: greedily settle the closest node using a min-heap; non-negative weights only.](images/80_dijkstra.png)

```text
# Dijkstra                                   Time O((V+E) log V), Space O(V)
dist[source] = 0; others = infinity
min-heap = {(0, source)}
while heap:
    (d, u) = pop-min
    if d > dist[u]: continue            # stale entry
    for (v, w) in neighbours(u):
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w; push (dist[v], v)
```

- **Crucial limitation:** **no negative edges**. A negative edge could make a
  *later* path cheaper than an already-"settled" node, breaking the greedy
  assumption.

> **Memory hook:** ripples that grow by **cheapest frontier** first (not by hop
> count like BFS).

### Worked trace — Dijkstra step by step

Source **A** on this graph (edges: A–B 4, A–C 1, C–B 2, B–D 1, C–D 8, C–E 5,
D–E 3):

![Dijkstra settles A, then C, then B, then D, then E; each settled distance is final.](images/210_dijkstra_trace.png)

```text
init  dist: A0  B∞  C∞  D∞  E∞     heap:{(0,A)}
pop A(0): relax B->4, C->1                 dist: A0 B4 C1 D∞ E∞
pop C(1): B via C =1+2=3 (<4) B->3; D->9; E->6   dist: A0 B3 C1 D9 E6
pop B(3): D via B =3+1=4 (<9) D->4                dist: A0 B3 C1 D4 E6
pop D(4): E via D =4+3=7 (not <6) no change       dist: A0 B3 C1 D4 E6
pop E(6): done
Final shortest distances: A0  B3  C1  D4  E6
```

Notice how **C settling before B** let us improve B from 4 down to 3 — the greedy
"closest first" order is what makes this correct.

### Why Dijkstra fails on negative edges (concrete)

```text
A --1--> B          Dijkstra settles B at 1 (closest), locks it in.
A --5--> C          Later it finds C=5, then edge C--(-4)-->B would give B=1... 
C -(-4)-> B         but B is already SETTLED, so the -4 shortcut is ignored.
Correct answer B=1 here, but with A->C=5, C->B=-10 the true B=-5 is MISSED.
```

The greedy invariant "a popped node's distance is final" only holds when adding
an edge can never *decrease* a total — i.e. when weights are **non-negative**.
For negatives, use **Bellman-Ford** (next).

### MCQs

1. Dijkstra time with a binary heap? → **O((V+E) log V)**.
2. Dijkstra fails when? → there are **negative edges**.
3. What data structure drives it? → a **min-heap / priority queue**.
4. Why does a settled node stay final? → because non-negative edges can only
   **increase** a total, never make a shortcut cheaper later.

### Problems

- Network Delay Time (743); Cheapest Flights Within K Stops (787); Path With
  Minimum Effort (1631); Swim in Rising Water (778).

---

## 10b.2 Bellman-Ford (negative edges allowed)

### The idea

**Relax every edge `V−1` times.** After `V−1` rounds, all shortest paths are
found (a shortest path has at most `V−1` edges). If a `V`-th round still improves
something, there is a **negative cycle**.

![Bellman-Ford: relax all edges V−1 times; an extra improving round means a negative cycle.](images/81_bellman_ford.png)

```text
# Bellman-Ford                               Time O(V*E), Space O(V)
dist[source] = 0; others = infinity
repeat V-1 times:
    for each edge (u, v, w):
        if dist[u] + w < dist[v]: dist[v] = dist[u] + w
# one more pass: if any edge still relaxes -> NEGATIVE CYCLE
```

- Slower than Dijkstra (O(VE)), but the **go-to when edges can be negative**, and
  the only simple way to **detect negative cycles** (e.g. currency arbitrage).

### Why exactly V−1 rounds?

A shortest path visits each node at most once, so it has **at most V−1 edges**.
One full relaxation round is guaranteed to extend every correct shortest path by
**at least one more edge**, so after **V−1** rounds even the longest shortest path
is fully built. A **V-th** round that still improves something proves a path with
≥ V edges is getting cheaper — only a **negative cycle** can do that.

### Worked trace — Bellman-Ford

Source **A**, edges processed in order `A→B(4), A→C(5), B→C(-6), C→D(3)`:

```text
init  A0  B∞  C∞  D∞
round 1: A->B: B=4 | A->C: C=5 | B->C: 4-6=-2 (<5) C=-2 | C->D: -2+3=1 D=1
round 2: A->B: 4 | A->C: 5 | B->C: -2 | C->D: 1  (no change)
round 3: (no change)  -> converged early
Final:  A0  B4  C-2  D1
Extra check round: nothing relaxes -> NO negative cycle.
```

Here the negative edge `B→C(-6)` is handled correctly — something Dijkstra
could not do. Convergence often happens before V−1 rounds; you may **stop early**
when a round makes no change.

### MCQs

1. Bellman-Ford time? → **O(V·E)**.
2. How many relaxation rounds? → **V − 1**.
3. What does a V-th improving round mean? → a **negative cycle**.

---

## 10b.3 Floyd-Warshall (all-pairs shortest paths)

### The idea

Find the shortest path between **every pair** of nodes. For each possible
**intermediate** node `k`, check if going *through* `k` improves each pair `(i,
j)`.

![Floyd-Warshall: for each intermediate k, relax every pair (i,j); O(V³).](images/82_floyd_warshall.png)

```text
# Floyd-Warshall                             Time O(V^3), Space O(V^2)
dist[i][j] = edge weight (or infinity; 0 on the diagonal)
for k in V:
    for i in V:
        for j in V:
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

- Handles **negative edges** (no negative cycle). Best for **small/dense** graphs
  or when you genuinely need *all* pairs. A negative value on the diagonal
  signals a negative cycle.

> **Memory hook:** "can I get from i to j cheaper by routing **through k**?" —
> asked for every k.

### The DP recurrence (what k really means)

Let `d_k[i][j]` = shortest i→j path allowed to use only intermediate nodes from
the set `{1..k}`. Then:

```text
d_0[i][j]  = weight(i,j)          # no intermediates: direct edge (or ∞)
d_k[i][j]  = min( d_{k-1}[i][j],                 # don't use k
                  d_{k-1}[i][k] + d_{k-1}[k][j]) # do route through k
answer     = d_V[i][j]
```

Because each layer only reads the previous layer's `[i][k]` and `[k][j]` — which
are unchanged when we overwrite `[i][j]` — the table can be updated **in place**
with a single `dist[][]`, which is why the code uses just O(V²) space. The loop
order **k outermost** is essential; swapping it breaks correctness.

### MCQs

1. Floyd-Warshall time/space? → **O(V³) / O(V²)**.
2. The relaxation core? → `dist[i][j] = min(dist[i][j], dist[i][k]+dist[k][j])`.
3. When prefer it over Dijkstra-from-each-node? → **small/dense**, need all pairs.
4. Which loop must be outermost? → the **intermediate node k**.
5. `k` in `d_k[i][j]` means? → paths using only intermediates from **{1..k}**.

---

## 10b.4 0-1 BFS and A* (the specialists)

- **0-1 BFS:** when every edge weight is **0 or 1**, use a **deque**: push 0-weight
  moves to the **front**, 1-weight to the **back**. Gives shortest paths in
  **O(V+E)** (faster than Dijkstra's log factor).
- **A\* search:** Dijkstra **plus a heuristic** `h(n)` estimating the distance to
  the goal. It expands nodes by `dist + h`, so it heads toward the target — much
  faster for single-target pathfinding (games, maps). Needs an *admissible*
  heuristic (never overestimates) to stay correct.
- **Multi-source BFS:** when you need the distance from the **nearest** of many
  sources (e.g. "rotting oranges" spreading, "walls and gates", "distance to
  nearest 0"), just **push ALL sources into the BFS queue at once** with distance
  0. One BFS then computes every cell's distance to its closest source in O(V+E)
  — no need to run BFS from each source separately. (A super common grid pattern.)

### MCQs

1. Edge weights 0/1 → fastest? → **0-1 BFS** (deque).
2. A* = Dijkstra + ? → a **heuristic** toward the goal.
3. Distance to the nearest of many sources? → **multi-source BFS** (push all
   sources first).

---

## 10b.4a Shortest-path algorithms — summary table

One table to pick the right tool. (V = nodes, E = edges.)

| Algorithm | Weights | Scope | Time | Negative cycle? |
|---|---|---|---|---|
| **BFS** | unweighted | single source | **O(V+E)** | n/a |
| **0-1 BFS** | 0 or 1 only | single source | **O(V+E)** | n/a |
| **Dijkstra** | non-negative | single source | **O((V+E) log V)** | can't handle |
| **Bellman-Ford** | any (incl. −ve) | single source | **O(V·E)** | **detects** it |
| **Floyd-Warshall** | any (no −ve cycle) | **all pairs** | **O(V³)** | flags via diagonal |

> **Decision order:** unweighted → BFS. 0/1 weights → 0-1 BFS. Non-negative →
> Dijkstra. Negative edges → Bellman-Ford. Need every pair on a small graph →
> Floyd-Warshall.

### MCQs

1. Fastest single-source on non-negative weights? → **Dijkstra**.
2. Only listed algorithm that *detects* a negative cycle directly? →
   **Bellman-Ford**.
3. All-pairs on a small dense graph? → **Floyd-Warshall**.

---

## 10b.5 Minimum Spanning Tree (MST)

### The problem

Connect **all** nodes with the **minimum total edge weight**, using no cycles
(a tree). Think: cheapest way to lay cable/roads connecting every city.

![MST: the cheapest set of edges connecting all nodes (green); built by Kruskal or Prim.](images/83_mst.png)

### Two greedy algorithms

```text
# KRUSKAL: sort edges, add cheapest that doesn't make a cycle
sort all edges by weight
for each edge (u,v) in order:
    if find(u) != find(v):       # union-find: no cycle
        add edge; union(u, v)
# Time O(E log E)

# PRIM: grow one tree from a start node
put start's edges in a min-heap
repeatedly pull the cheapest edge to a NEW node; add it; push its edges
# Time O((V+E) log V) with a heap
```

- **Both are greedy and both give a correct MST.** Kruskal (sort + union-find)
  shines on **sparse** graphs; Prim (grow + heap) on **dense** graphs.
- **Cut property** (why greedy works): the cheapest edge crossing any partition of
  the nodes is always safe to include.

### Prim vs Kruskal — comparison

| | **Kruskal** | **Prim** |
|---|---|---|
| Strategy | pick cheapest **edge** globally | grow one **tree** from a start node |
| Core structure | sort + **union-find** | **min-heap** (priority queue) |
| Cycle avoided by | `find(u) != find(v)` | only pull edges to a **new** node |
| Works on a forest? | **yes** (builds MST per component) | one component at a time |
| Time | **O(E log E)** | **O((V+E) log V)** |
| Best for | **sparse** graphs | **dense** graphs |

### Worked trace — Kruskal

Edges by weight: `(A,B,1) (B,C,2) (A,C,3) (C,D,4) (B,D,5)` on 4 nodes:

```text
sort:  AB1  BC2  AC3  CD4  BD5
AB1: find(A)!=find(B) -> ADD; union      tree={AB}       comps:{A,B}{C}{D}
BC2: find(B)!=find(C) -> ADD; union      tree={AB,BC}    comps:{A,B,C}{D}
AC3: find(A)==find(C) -> SKIP (cycle)
CD4: find(C)!=find(D) -> ADD; union      tree={AB,BC,CD} comps:{A,B,C,D}
BD5: all one component now -> stop (V-1=3 edges chosen)
MST edges: AB, BC, CD    total weight = 1+2+4 = 7
```

An MST on V nodes always has exactly **V−1 edges**; Kruskal stops once it has
picked that many.

### MCQs

1. Kruskal uses which structure to avoid cycles? → **union-find**.
2. Kruskal vs Prim time? → **O(E log E)** vs **O((V+E) log V)**.
3. Why does greedy give the MST? → the **cut property**.
4. How many edges in an MST of V nodes? → exactly **V − 1**.
5. Kruskal on a sparse graph vs Prim on a dense graph? → each is preferred there.

### Problems

- Min Cost to Connect All Points (1584); Connecting Cities With Min Cost (1135);
  Optimize Water Distribution (1168).

---

## Module 10b — Concept Review (one page)

- **Unweighted shortest path → BFS** (Module 10a).
- **Dijkstra:** non-negative weights, greedy + min-heap, **O((V+E) log V)**; fails
  on negative edges.
- **Bellman-Ford:** negative edges OK, detects negative cycles, **O(V·E)** (relax
  all edges V−1 times).
- **Floyd-Warshall:** all-pairs, **O(V³)**, `dist[i][j]=min(…, dist[i][k]+dist[k]
  [j])`.
- **0-1 BFS:** 0/1 weights → deque, O(V+E). **A\*:** Dijkstra + heuristic for
  single-target.
- **MST:** Kruskal (sort + union-find, O(E log E)) or Prim (grow + heap); both
  greedy, both correct (cut property).

## Module 10b — Flash Cards

- Q: Dijkstra restriction & time? **A: no negative edges; O((V+E) log V).**
- Q: Negative edges / cycle detection? **A: Bellman-Ford, O(VE), V−1 rounds.**
- Q: All-pairs shortest path? **A: Floyd-Warshall O(V³).**
- Q: 0/1 weights fastest? **A: 0-1 BFS (deque).**
- Q: A* adds what to Dijkstra? **A: an admissible heuristic.**
- Q: MST algorithms? **A: Kruskal (union-find), Prim (heap).**
- Q: Why V−1 rounds in Bellman-Ford? **A: a shortest path has ≤ V−1 edges.**
- Q: Edges in an MST of V nodes? **A: exactly V−1.**
- Q: Floyd-Warshall outermost loop? **A: the intermediate node k.**

## Module 10b — Pattern Recognition

- "Cheapest route, non-negative weights" → **Dijkstra**.
- "Edges can be negative / detect arbitrage" → **Bellman-Ford**.
- "Shortest path between every pair / small dense graph" → **Floyd-Warshall**.
- "Weights are only 0/1" → **0-1 BFS**; "single target with a map" → **A\***.
- "Connect everything at minimum cost" → **MST (Kruskal/Prim)**.
- "Sparse graph, connect all" → **Kruskal**; "dense graph, connect all" → **Prim**.

## Module 10b — Interview Questions (with follow-ups)

1. *Network delay time.* FU: *why Dijkstra; what if weights were negative?*
2. *Cheapest flights within K stops.* FU: *Bellman-Ford / modified BFS.*
3. *Min cost to connect all points.* FU: *Kruskal vs Prim choice.*
4. *Detect a negative cycle.* FU: *Bellman-Ford V-th round / Floyd diagonal.*

## Module 10b — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** Dijkstra/Bellman-Ford/Floyd-Warshall **tracing and
  complexity**, MST by Kruskal/Prim (and "is the MST unique?"), the cut property,
  and why Dijkstra fails on negative edges. Extremely frequently tested.

---

*End of Module 10b. Next: Module 10c — Advanced Graphs (SCC, bridges &
articulation points, Euler tour, LCA, Heavy-Light Decomposition) — with visuals.*
