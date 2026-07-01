---
title: "Module 10c — Graphs: Advanced (SCC, Bridges, LCA, HLD)"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10c — Advanced Graphs

> **Why this part.**
> These topics are **P2** — rarely needed in standard FAANG coding rounds, but
> they appear in **competitive programming**, hard interviews, and GATE. The goal
> here is to **understand the idea and when each applies**, not to memorise every
> line of code.

> **How to read.** Each topic: the idea, the key complexity, and when to use it.

---

## 10c.1 Strongly Connected Components (SCC)

### The idea

In a **directed** graph, an **SCC** is a maximal group of nodes where **every
node can reach every other** node in the group. Condensing each SCC into a single
node turns any directed graph into a **DAG**.

![SCCs: maximal groups where every node reaches every other; condensing them yields a DAG.](images/85_scc.png)

- **Kosaraju's algorithm:** DFS to get finish order → DFS the **reversed** graph
  in that order. Each tree in the second pass is an SCC. **O(V+E)**.
- **Tarjan's algorithm:** a single DFS tracking **discovery time** and a
  **low-link** value; pops an SCC off a stack when a "root" is found. **O(V+E)**.

> **Uses:** 2-SAT, dependency analysis, finding cycles/feedback in directed
> graphs, condensing a graph before further processing.

### Tarjan vs Kosaraju — quick comparison

| | **Kosaraju** | **Tarjan** |
|---|---|---|
| DFS passes | **two** (graph, then reversed graph) | **one** |
| Needs the reversed graph? | **yes** | no |
| Extra state | finish-order stack | discovery time + **low-link** + stack |
| Time | **O(V+E)** | **O(V+E)** |
| Easier to remember | **yes** (two plain DFS) | fewer passes, slightly trickier |

> **Memory hook:** Kosaraju = "DFS twice, reverse in between"; Tarjan = "one DFS,
> watch the low-link." Both are O(V+E) — pick whichever you recall under pressure.

### MCQs

1. SCC definition? → maximal set with **mutual reachability** (directed).
2. SCC algorithms & time? → **Kosaraju / Tarjan**, O(V+E).
3. Condensing SCCs gives a? → **DAG**.
4. Which SCC method needs the reversed graph? → **Kosaraju** (two passes).
5. Which uses a single DFS with low-link? → **Tarjan**.

---

## 10c.2 Bridges & Articulation Points

### The idea (network weak points)

In an **undirected** graph:

- A **bridge** is an **edge** whose removal disconnects the graph.
- An **articulation point** (cut vertex) is a **node** whose removal disconnects
  the graph.

![Bridges (cut-edges) and articulation points (cut-vertices) are single points of failure in a network.](images/86_bridges.png)

Both are found in a **single DFS** using **discovery times** and **low-link**
values (the earliest node reachable from a subtree). **O(V+E)**.

> **Uses:** finding **single points of failure** in networks (if this cable/router
> dies, who gets cut off?), and as building blocks for biconnected components.

### Why they matter (and the low-link test)

They pinpoint **fragility**. In a data-centre or road network, a bridge is a
cable whose failure splits the network; an articulation point is a router/junction
whose failure does the same. Redundant designs deliberately add edges so that
**no** bridges remain (every part stays reachable if any one link dies).

The DFS test uses `low[v]` = the earliest discovery time reachable from v's
subtree via one back edge:

```text
edge (u,v) in the DFS tree is a BRIDGE          if low[v] >  disc[u]
non-root u is an ARTICULATION POINT             if low[v] >= disc[u] for a child v
root of the DFS is an articulation point        if it has >= 2 DFS-tree children
```

> **Intuition:** if v's subtree has **no** back edge climbing above u, then u (or
> the edge u–v) is the *only* way in — remove it and the subtree is cut off.

### MCQs

1. A bridge is a? → an **edge** whose removal disconnects the graph.
2. An articulation point is a? → a **node** whose removal disconnects it.
3. Found using? → **DFS discovery + low-link** values, O(V+E).
4. Bridge condition for tree edge (u,v)? → **low[v] > disc[u]**.
5. Root is an articulation point when? → it has **≥ 2 DFS-tree children**.

---

## 10c.3 Euler Tour of a Tree

### The idea

An **Euler tour** records the order in which DFS **enters and leaves** each node,
flattening a tree into an **array**. This turns **subtree queries** into
**contiguous range queries** (then a segment tree / Fenwick from Module 8b
answers them in O(log n)).

> **Memory hook:** walk around the tree's outline; the entry/exit times turn "this
> whole subtree" into "this slice of the array".

- **Uses:** "sum/min over a subtree", "is u an ancestor of v?" (`in[u] ≤ in[v] ≤
  out[u]`), and as the basis for one LCA method.

### MCQs

1. Euler tour turns subtree queries into? → **range queries** on an array.
2. Ancestor check via tour times? → `in[u] ≤ in[v] ≤ out[u]`.

---

## 10c.4 Lowest Common Ancestor (LCA)

### The idea

The **LCA** of two nodes is their **deepest common ancestor**. Naively: bring both
to the same depth, then move up together — **O(height)** per query.

![LCA(4,5)=2: the deepest node that is an ancestor of both; binary lifting answers queries in O(log n).](images/87_lca.png)

- **Binary lifting:** precompute each node's **2^k-th ancestor** (a table of size
  `n log n`). Then any LCA query jumps up in **powers of two** → **O(log n)** per
  query after **O(n log n)** preprocessing.
- **Euler tour + RMQ:** another classic O(1)-query approach (with O(n log n)
  preprocessing).

### Binary lifting — the complexity, spelled out

```text
up[k][v] = the (2^k)-th ancestor of v      table size n × log n
up[0][v] = parent[v]                         # base: 2^0 = direct parent
up[k][v] = up[k-1][ up[k-1][v] ]             # jump 2^(k-1) twice = 2^k

Preprocess: fill the table          O(n log n) time, O(n log n) space
Query LCA(a,b):
  1. lift the deeper node up until depths match   (log n jumps)
  2. jump both up together in decreasing powers of 2 while ancestors differ
  3. their common parent is the LCA               -> O(log n) per query
```

- Total: **O(n log n)** build, **O(log n)** per query. The "powers of two" trick
  is the same idea as binary representation — any height difference is covered by
  a few jumps of size 2^k.

### MCQs

1. LCA = ? → the **deepest common ancestor** of two nodes.
2. Binary lifting query time after prep? → **O(log n)**.
3. What does binary lifting precompute? → each node's **2^k-th ancestors**.
4. Binary lifting table size / build time? → **O(n log n)** both.
5. Recurrence for the table? → `up[k][v] = up[k-1][ up[k-1][v] ]`.

---

## 10c.5 Heavy-Light Decomposition (HLD)

### The idea

**HLD** splits a tree into **chains** so that any root-to-node path crosses only
**O(log n) chains**. Each chain is stored in a segment tree, so **path queries**
(sum/max/update along a path between two nodes) run in **O(log² n)**.

> **Memory hook:** highways (heavy chains) connected by short ramps (light edges);
> any trip uses only a few highways.

- **Uses:** competitive-programming path-query problems (sum/max/update on tree
  paths). Almost never needed in standard interviews — know the *name and
  purpose*.

### MCQs

1. HLD makes any path cross how many chains? → **O(log n)**.
2. Path query time with HLD + segment tree? → **O(log² n)**.

---

## 10c.6 Network Flow (Max-Flow / Min-Cut) & Bipartite Matching

### The idea

Model a network of pipes: edges have **capacities**, and you want the **maximum
flow** from a **source `s`** to a **sink `t`**. The famous **Max-Flow Min-Cut
theorem** says the maximum flow equals the **minimum cut** — the cheapest set of
edges that, if removed, disconnects `s` from `t`.

![Max-flow / min-cut: most flow from s to t equals the cheapest cut separating them.](images/88_max_flow.png)

```text
# Ford-Fulkerson / Edmonds-Karp idea         Edmonds-Karp: O(V * E^2)
while there is an augmenting path s->t with spare capacity (find via BFS):
    push flow equal to the path's bottleneck capacity
    update residual capacities (forward down, backward up)
max flow = total pushed
```

- **Edmonds-Karp** (BFS augmenting paths): **O(V·E²)**. **Dinic's algorithm**:
  **O(V²·E)** (much faster in practice, the CP standard).
- **Bipartite matching** (assign workers↔jobs, students↔projects) reduces to
  max-flow with **capacity-1 edges** — or use **Hopcroft-Karp** in O(E·√V).
- **Uses:** scheduling, assignment, image segmentation, "minimum edges to cut",
  baseball elimination, and many CP problems.

> **Memory hook:** water pipes — the most water you can push from tap to drain is
> limited by the **tightest bottleneck** (the min cut).

### The two ideas that make it work

- **Augmenting path:** any s→t path in the *residual* graph that still has spare
  capacity. Push flow along it equal to its **bottleneck** (smallest spare edge).
- **Residual edge:** when you push `f` along `u→v`, you also add a **backward**
  edge `v→u` of capacity `f`. This lets a later path *undo* an earlier choice —
  the trick that guarantees the algorithm finds the true maximum, not a dead end.
- The algorithm stops when **no augmenting path remains**; by Max-Flow Min-Cut,
  the reachable-from-s set at that point defines the **minimum cut**, and its
  capacity equals the flow.

> **Max-Flow = Min-Cut (statement):** in any flow network the **maximum** s→t flow
> value equals the **minimum** total capacity of edges whose removal separates s
> from t. (Proof idea: a flow can never exceed any cut; when no augmenting path is
> left, one specific cut is saturated exactly to the flow.)

### Bipartite matching & König's theorem

- **Maximum bipartite matching** = the most worker↔job pairs with no one shared.
  Model it as flow: add source `s`→every worker (cap 1), every job→sink `t`
  (cap 1), each allowed pair as a cap-1 edge; the **max flow = maximum matching**.
- **König's theorem:** in a bipartite graph, the size of the **maximum matching**
  equals the size of the **minimum vertex cover**. This is the bipartite special
  case of Max-Flow Min-Cut and is a common GATE/CP fact.

### When (not) to use

This is **ICPC / advanced-interview** territory — rarely needed in standard FAANG
coding rounds. Recognise the **reduction** ("this assignment/matching problem *is*
a flow problem") even if you don't code Dinic from memory.

### MCQs

1. Max-Flow equals? → **Min-Cut** (the theorem).
2. Edmonds-Karp time? → **O(V·E²)**; Dinic **O(V²·E)**.
3. Bipartite matching reduces to? → **max-flow** (capacity-1 edges).
4. Why add backward residual edges? → to let a later path **undo** earlier flow.
5. König's theorem (bipartite)? → **max matching = min vertex cover**.

---

## Module 10c — Concept Review (one page)

- **SCC** (directed): mutual-reachability groups; Kosaraju/Tarjan, O(V+E);
  condensing → DAG.
- **Bridges / articulation points** (undirected): cut-edges / cut-vertices =
  single points of failure; DFS + low-link, O(V+E).
- **Euler tour:** flatten a tree → subtree queries become range queries (+ segment
  tree).
- **LCA:** deepest common ancestor; **binary lifting** → O(log n) per query after
  O(n log n) prep.
- **HLD:** tree into chains → path queries in O(log² n); CP-only.
- **Network flow:** Max-Flow = Min-Cut; Edmonds-Karp O(V·E²), Dinic O(V²·E);
  bipartite matching reduces to flow. ICPC/advanced.

## Module 10c — Flash Cards

- Q: SCC algorithms? **A: Kosaraju, Tarjan — O(V+E).**
- Q: Bridge vs articulation point? **A: cut-edge vs cut-vertex.**
- Q: Euler tour enables? **A: subtree queries as array ranges.**
- Q: LCA via binary lifting? **A: O(log n) query, O(n log n) prep.**
- Q: HLD path query time? **A: O(log² n).**
- Q: Kosaraju vs Tarjan passes? **A: two vs one DFS.**
- Q: Bridge condition? **A: low[v] > disc[u].**
- Q: Binary lifting build cost? **A: O(n log n) time and space.**
- Q: König's theorem? **A: max matching = min vertex cover (bipartite).**

## Module 10c — Pattern Recognition

- "Mutually reachable groups in a directed graph" → **SCC**.
- "Single point of failure / critical connection" → **bridges / articulation**.
- "Queries over a subtree" → **Euler tour + segment tree**.
- "Common ancestor / distance between tree nodes (many queries)" → **LCA (binary
  lifting)**.
- "Many path-sum/max/update queries on a tree" → **HLD**.
- "Assign workers to jobs / max pairings" → **bipartite matching (max-flow)**.
- "Most flow / cheapest set of edges to cut s from t" → **max-flow = min-cut**.

## Module 10c — Interview / CP Questions

1. *Critical connections in a network (LC 1192).* → **bridges** (Tarjan).
2. *Find SCCs / does a directed graph have a cycle reachable everywhere?*
3. *LCA of a binary tree (LC 236) / many-query LCA.* → binary lifting.
4. *Course/dependency analysis on a directed graph.* → SCC condensation + topo.

## Module 10c — GATE / SEBI / RBI / ISRO Perspective

- **GATE:** SCC concept, bridges/articulation as connectivity questions, LCA
  basics. These are **less frequent** than M10a/b but appear in advanced sets.
- For exams, **prioritise M10a/M10b**; treat M10c as "know the idea".

---

*End of Module 10 (Graphs complete: a + b + c). Next: Module 11 — Greedy
Algorithms — with visuals.*
