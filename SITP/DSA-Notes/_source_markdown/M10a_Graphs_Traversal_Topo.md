---
title: "Module 10a — Graphs: Representation, BFS/DFS, Topo Sort, Union-Find"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10a — Graphs: Traversal, Topological Sort, Union-Find

> **Why graphs are the boss level.**
> A **graph** models *relationships*: friends, roads, web links, course
> prerequisites, package dependencies. Trees are just special graphs (no cycles,
> one parent). Once you can think in graphs, a huge range of problems — mazes,
> networks, scheduling, maps — become the same few algorithms. Graphs are the
> **#1 topic** at Google/Meta and heavily tested in GATE.

This module is **P0**. Part **a** covers the foundation (representation, BFS/DFS,
topological sort, union-find); **b** covers shortest paths & MST; **c** covers
advanced (SCC, bridges, LCA, HLD).

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

---

## 10a.1 What is a Graph & How to Store It

### Definition

A **graph** `G = (V, E)` is a set of **vertices** (nodes) `V` and **edges** `E`
connecting them. Edges can be:

- **Undirected** (two-way, like friendship) or **directed** (one-way, like a
  Twitter follow).
- **Unweighted** or **weighted** (each edge has a cost, like road distance).

### Two ways to store a graph

![Adjacency list vs adjacency matrix for the same graph.](images/75_graph_repr.png)

| | Adjacency **list** | Adjacency **matrix** |
|---|---|---|
| Space | **O(V + E)** | O(V²) |
| "Is there an edge u–v?" | O(degree) | **O(1)** |
| Iterate a node's neighbours | **O(degree)** | O(V) |
| Best for | **sparse** graphs (most real ones) | dense graphs / fast edge checks |

> **Memory hook:** the **list** is a contact book ("who do I know?"); the
> **matrix** is a giant yes/no grid of every possible pair.

### MCQs

1. Space of an adjacency list? → **O(V + E)**.
2. O(1) edge existence check uses? → **adjacency matrix**.
3. Best representation for a sparse graph? → **adjacency list**.

---

## 10a.2 BFS and DFS (the two core traversals)

![BFS explores level by level (queue); DFS goes deep then backtracks (stack/recursion).](images/76_bfs_dfs.png)

### BFS — Breadth-First Search (a queue)

Explore **level by level**: visit all neighbours, then their neighbours, etc.
**Key property:** in an **unweighted** graph, BFS finds the **shortest path**
(fewest edges) from the source.

```text
# BFS                                        Time O(V+E), Space O(V)
queue = [start]; visited = {start}
while queue:
    u = queue.pop_front()
    for v in neighbours(u):
        if v not visited: visited.add(v); queue.push(v)
```

### DFS — Depth-First Search (recursion/stack)

Go **as deep as possible**, then **backtrack**. Great for connectivity, cycle
detection, topological sort, and exploring all paths.

```text
# DFS (recursive)                            Time O(V+E), Space O(V)
dfs(u):
    visited.add(u)
    for v in neighbours(u):
        if v not visited: dfs(v)
```

> **Memory hook:** **BFS = ripples** spreading outward on water; **DFS = walking a
> maze** down one corridor until you hit a dead end, then backtracking.

### What they solve

- **Connected components / number of islands:** run DFS/BFS from each unvisited
  node; count how many times you start.
- **Shortest path (unweighted):** BFS.
- **Cycle detection:** DFS (undirected: a visited non-parent neighbour; directed:
  a node currently on the recursion stack).
- **Bipartite check (2-coloring):** BFS/DFS coloring neighbours opposite colors.

### Grid problems are graph problems

![A grid is a graph: each cell connects to its 4 neighbours; islands = connected components.](images/79_grid_graph.png)

Many "matrix" problems (islands, flood fill, shortest path in a maze, rotting
oranges) are just **BFS/DFS on a grid** where each cell's neighbours are
`(r±1, c)` and `(r, c±1)`.

### Worked trace — BFS and DFS on the same small graph

Take this undirected graph (neighbour lists kept in sorted order):

```text
        A
       / \
      B   C
     / \   \
    D   E   F
Adjacency: A:[B,C]  B:[A,D,E]  C:[A,F]  D:[B]  E:[B]  F:[C]
```

**BFS from A** (queue, level by level):

```text
step  pop  queue after         visited
 1     A   [B, C]              A B C
 2     B   [C, D, E]           A B C D E
 3     C   [D, E, F]           A B C D E F
 4     D   [E, F]              (no new)
 5     E   [F]                 (no new)
 6     F   []                  done
BFS visit order: A B C D E F     (level 0: A | level 1: B C | level 2: D E F)
```

**DFS from A** (recursion, first-unvisited neighbour first):

```text
enter A -> enter B -> enter D (dead end, back to B)
        -> enter E (dead end, back to B, back to A)
        -> enter C -> enter F (dead end)
DFS visit order: A B D E C F
```

> **Memory hook:** BFS output is **wide** (siblings together); DFS output is
> **deep** (one whole branch, then the next).

### Cycle detection: directed vs undirected

The rule differs by graph type — a classic GATE trap.

```text
UNDIRECTED (DFS): a cycle exists if you meet an ALREADY-visited neighbour
                  that is NOT the parent you came from.
    dfs(u, parent):
        visited[u] = true
        for v in neighbours(u):
            if not visited[v]: if dfs(v, u): return true
            else if v != parent: return true      # back edge -> cycle
        return false

DIRECTED (DFS 3 colors): a cycle exists if you reach a node that is
                  currently ON the recursion stack (GRAY).
    WHITE = unvisited, GRAY = in progress (on stack), BLACK = finished
    dfs(u):
        color[u] = GRAY
        for v in neighbours(u):
            if color[v] == GRAY: return true       # back edge -> cycle
            if color[v] == WHITE and dfs(v): return true
        color[u] = BLACK; return false
```

> **Why undirected needs the "not parent" check:** the edge u–v shows up in both
> lists, so seeing your own parent again is normal, not a cycle. In a **directed**
> graph edges are one-way, so "parent" does not apply — you track the *stack*
> instead. (Union-Find also detects undirected cycles: an edge whose two ends
> already share a root closes a cycle.)

### Connected components (count the pieces)

Run DFS/BFS from every still-unvisited node; each fresh start is one component.

```text
count = 0
for u in all nodes:
    if not visited[u]: count++; dfs(u)   # or bfs(u)
# count = number of connected components         Time O(V+E)
```

### Bipartite check (2-coloring)

A graph is **bipartite** if you can 2-color it so no edge joins same-color nodes
(equivalently: no odd-length cycle). Color the source, then color every neighbour
the **opposite**; a conflict means "not bipartite".

```text
color[start] = 0; BFS/DFS:
    for each neighbour v of u:
        if v uncolored: color[v] = 1 - color[u]; recurse/enqueue
        else if color[v] == color[u]: return NOT bipartite
# Time O(V+E). Uses: two-team split, "is graph bipartite" (LC 785).
```

> **Memory hook:** bipartite = **two teams**; every edge must go *across* teams,
> never within one. An **odd cycle** is what makes a clean 2-coloring impossible.

### MCQs

1. BFS vs DFS data structure? → **queue** vs **stack/recursion**.
2. Shortest path in an unweighted graph? → **BFS**.
3. BFS/DFS time? → **O(V + E)**.
4. Undirected cycle rule? → a **visited neighbour that is not the parent**.
5. Directed cycle rule? → an edge to a node **on the recursion stack** (GRAY).
6. A graph is bipartite iff it has? → **no odd-length cycle**.

### Problems

- Number of Islands (200); Flood Fill (733); Rotting Oranges (994); Clone Graph
  (133); Word Ladder (127); Is Graph Bipartite (785); Pacific Atlantic (417).

---

## 10a.3 Topological Sort (ordering a DAG)

### The problem

Given tasks with dependencies ("A must come before C"), produce a valid **linear
order**. Only possible if the graph is a **DAG** (Directed Acyclic Graph) — a
cycle means no valid order.

![Topological sort: order the DAG so every edge points forward (A, B, C, D, E).](images/77_topo_sort.png)

### Two ways

```text
# Kahn's algorithm (BFS with in-degrees)     Time O(V+E)
compute in-degree of every node
queue = all nodes with in-degree 0
while queue:
    u = queue.pop(); output u
    for v in neighbours(u):
        in_degree[v]--; if in_degree[v]==0: queue.push(v)
# if output has fewer than V nodes -> there was a CYCLE

# DFS method                                 Time O(V+E)
DFS the graph; push each node on a stack when it FINISHES;
the reverse of finish order is a topological order.
```

> **Memory hook:** Kahn's = "do the tasks that have **no remaining
> prerequisites** first," then unlock the next ones.

### Worked trace — Kahn's algorithm

DAG with edges `A→C, B→C, C→D, C→E, D→F, E→F`:

```text
in-degree:  A:0  B:0  C:2  D:1  E:1  F:2
queue (in-degree 0): [A, B]

pop A -> output A; C's in-degree 2->1
pop B -> output B; C's in-degree 1->0 -> push C          queue:[C]
pop C -> output C; D:1->0 push D, E:1->0 push E          queue:[D, E]
pop D -> output D; F:2->1
pop E -> output E; F:1->0 -> push F                       queue:[F]
pop F -> output F
Topological order: A B C D E F   (6 nodes ordered = no cycle)
```

**DFS method on the same DAG** — push each node when it *finishes*, then reverse:

```text
dfs(A)->dfs(C)->dfs(D)->dfs(F) finish F, finish D,
              ->dfs(E) finish E, finish C, finish A ; then dfs(B) finish B
finish order: F D E C A B    ->  reverse: B A C E D F   (also valid)
```

> **Note:** a DAG can have **many** valid topological orders (both outputs above
> are correct). GATE loves "how many distinct topological orderings?" questions.

### Kahn's vs DFS topo — quick comparison

| | Kahn's (BFS) | DFS finish order |
|---|---|---|
| Driver | queue of **in-degree 0** nodes | recursion + a stack |
| Cycle detection | output size **< V** | a **back edge** (GRAY node) |
| Order produced | natural "ready first" order | **reverse** of finish times |
| Time / space | **O(V+E)** / O(V) | **O(V+E)** / O(V) |

### Uses

Build systems (Make, Maven), course prerequisites (LC 207/210), package managers,
spreadsheet recalculation, task schedulers.

### MCQs

1. Topological sort needs the graph to be a? → **DAG**.
2. Kahn's algorithm starts with nodes of in-degree? → **0**.
3. How does topo sort detect a cycle? → fewer than V nodes get ordered.
4. DFS topo order = ? → the **reverse of DFS finish order**.
5. Can one DAG have several valid topological orders? → **yes**.

### Problems

- Course Schedule I/II (207/210); Alien Dictionary (269); Parallel Courses
  (1136); Minimum Height Trees (310).

---

## 10a.4 Union-Find (Disjoint Set Union, DSU)

### The idea

Union-Find tracks a partition of items into **disjoint groups** and answers "are
x and y in the same group?" and "merge the groups of x and y" — almost in
**O(1)**.

![Union-Find: find follows parents to the root; path compression flattens the tree for near-O(1) operations.](images/78_union_find.png)

```text
# Union-Find with the two optimisations      ~O(alpha(n)) per op ~ O(1)
find(x):  while x != parent[x]:
              parent[x] = parent[parent[x]]   # path compression (halving)
              x = parent[x]
          return x
union(a,b):
    ra, rb = find(a), find(b)
    if ra == rb: return
    attach the smaller-rank root under the larger  # union by rank/size
```

- **Two optimisations together** — *union by rank/size* + *path compression* —
  give **O(α(n))** amortised, where α is the inverse Ackermann function (≤ 4 for
  any practical n). Effectively constant.

> **Memory hook:** everyone in a group points (eventually) to one **group
> leader**; "same group?" = "same leader?". Path compression makes everyone point
> straight at the leader.

### Worked trace — union by rank + path compression

Start with 5 singletons `{0}{1}{2}{3}{4}`, all `parent[i]=i`, `rank=0`.

```text
op            action                                 forest (parent)
union(0,1)    ranks tie -> 1 under 0, rank[0]=1      0<-1
union(2,3)    ranks tie -> 3 under 2, rank[2]=1      2<-3
union(0,2)    ranks tie -> 2 under 0, rank[0]=2      0<-{1, 2<-3}
union(0,4)    rank0=2 > rank4=0 -> 4 under 0         0<-{1, 4, 2<-3}
find(3)       path 3->2->0; compress: parent[3]=0    3 now points at 0 directly
```

See the before/after of that `find(3)` below.

![find(3) compresses the path so every node points straight at the root, keeping later operations near O(1).](images/211_dsu_compression.png)

- **Union by rank** always hangs the *shorter* tree under the *taller* one, so
  height grows only when two equal-rank trees merge — that keeps trees shallow.
- **Path compression** then flattens whatever path `find` walked. Together they
  give the **O(α(n))** amortised bound.
- **Cycle detection with DSU:** while adding undirected edges, if `find(u) ==
  find(v)` *before* the union, that edge closes a **cycle** (this is exactly the
  test Kruskal uses).

### Uses

- **Kruskal's MST** (Module 10b) — add edges, skip those that would form a cycle.
- **Cycle detection** in an undirected graph.
- **Connected components**, "number of provinces" (LC 547), "accounts merge".

### MCQs

1. Union-Find amortised cost with both optimisations? → **O(α(n)) ≈ O(1)**.
2. The two optimisations? → **path compression** + **union by rank/size**.
3. Which MST algorithm uses it? → **Kruskal's**.
4. DSU cycle test when adding edge (u,v)? → `find(u) == find(v)` before union.
5. Union by rank attaches the? → **shorter tree under the taller one**.

### Problems

- Number of Provinces (547); Redundant Connection (684); Accounts Merge (721);
  Number of Connected Components (323); Most Stones Removed (947).

---

## Module 10a — Concept Review (one page)

- **Graph** = vertices + edges (directed/undirected, weighted/unweighted).
- **Store as:** adjacency **list** O(V+E) for sparse (default); **matrix** O(V²)
  for dense / O(1) edge checks.
- **BFS** (queue, level-by-level) → shortest path in **unweighted** graphs;
  **DFS** (stack/recursion) → connectivity, cycles, paths. Both **O(V+E)**.
- **Grids** are graphs (4-neighbour); islands = connected components.
- **Topological sort** (DAG only): Kahn's (in-degree 0 queue) or DFS finish
  order; detects cycles.
- **Union-Find**: near-O(1) group merge/query with path compression + union by
  rank; powers Kruskal & connectivity.

## Module 10a — Flash Cards

- Q: Adjacency list vs matrix space? **A: O(V+E) vs O(V²).**
- Q: Shortest path, unweighted? **A: BFS.**
- Q: BFS/DFS structure? **A: queue / stack(recursion).**
- Q: Topo sort needs? **A: a DAG; Kahn's uses in-degree 0.**
- Q: Union-Find cost? **A: O(α(n)) ≈ O(1) with both optimisations.**
- Q: Detect cycle in undirected graph fast? **A: union-find (or DFS).**
- Q: Directed cycle via DFS? **A: edge to a GRAY (on-stack) node.**
- Q: Bipartite iff? **A: no odd-length cycle (2-colorable).**
- Q: DFS topo order? **A: reverse of finish order.**

## Module 10a — Pattern Recognition

- "Shortest path / fewest steps, unweighted (incl. grids/mazes)" → **BFS**.
- "Explore all / connectivity / cycles / paths" → **DFS**.
- "Ordering with dependencies / prerequisites" → **topological sort**.
- "Group / connected / 'are these joined?' / merge sets" → **union-find**.
- "Count islands / regions in a matrix" → **DFS/BFS flood fill**.
- "Split into two teams / no same-color edge" → **bipartite 2-coloring**.
- "Does a directed graph have a cycle?" → **DFS colors** (or Kahn's < V).

## Module 10a — Interview Questions (with follow-ups)

1. *Number of islands.* FU: *BFS vs DFS; in-place vs visited set.*
2. *Course schedule (can you finish?).* FU: *return an order (topo sort).*
3. *Detect a cycle.* FU: *directed vs undirected — how do they differ?*
4. *Number of connected components.* FU: *union-find vs DFS.*
5. *Word ladder.* FU: *why BFS; build the implicit graph.*

## Module 10a — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** BFS/DFS traversal orders & trees, **counting edges/
  degrees**, topological orderings (how many valid?), graph representation space,
  union-find operations. Very frequently tested.
- **SEBI/RBI IT:** conceptual MCQs on BFS/DFS, representations, DAGs.

---

*End of Module 10a. Next: Module 10b — Shortest Paths (Dijkstra, Bellman-Ford,
Floyd-Warshall, 0-1 BFS, A*) and MST (Kruskal, Prim) — with visuals.*
