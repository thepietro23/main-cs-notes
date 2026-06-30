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

### MCQs

1. Dijkstra time with a binary heap? → **O((V+E) log V)**.
2. Dijkstra fails when? → there are **negative edges**.
3. What data structure drives it? → a **min-heap / priority queue**.

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

### MCQs

1. Floyd-Warshall time/space? → **O(V³) / O(V²)**.
2. The relaxation core? → `dist[i][j] = min(dist[i][j], dist[i][k]+dist[k][j])`.
3. When prefer it over Dijkstra-from-each-node? → **small/dense**, need all pairs.

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

### MCQs

1. Kruskal uses which structure to avoid cycles? → **union-find**.
2. Kruskal vs Prim time? → **O(E log E)** vs **O((V+E) log V)**.
3. Why does greedy give the MST? → the **cut property**.

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

## Module 10b — Pattern Recognition

- "Cheapest route, non-negative weights" → **Dijkstra**.
- "Edges can be negative / detect arbitrage" → **Bellman-Ford**.
- "Shortest path between every pair / small dense graph" → **Floyd-Warshall**.
- "Weights are only 0/1" → **0-1 BFS**; "single target with a map" → **A\***.
- "Connect everything at minimum cost" → **MST (Kruskal/Prim)**.

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
