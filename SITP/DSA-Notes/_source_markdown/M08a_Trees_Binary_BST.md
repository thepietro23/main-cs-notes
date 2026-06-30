---
title: "Module 8a — Trees: Binary Trees & BST"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8a — Trees: Binary Trees & BST

> **Why trees matter so much.**
> Arrays and lists are *linear* — one thing after another. A **tree** is the
> first **hierarchical** structure: it branches, like a family tree or a folder
> system. Trees give us O(log n) search/insert/delete (when balanced), power
> databases (B+ trees), file systems, compilers (parse trees), and a huge share
> of FAANG interview questions. This part covers binary trees, traversals, and
> the Binary Search Tree. Part **M08b** covers balancing (AVL, Red-Black) and
> range trees (Segment, Fenwick, B/B+).

This module is **P0**. Tree traversal and BST questions are interview staples and
GATE favourites.

> **How to read each technique.** Brute force → Better → Optimal with pseudocode +
> complexity, plus a memory hook.

---

## 8a.1 Tree Terminology

### Definition

A **tree** is a set of **nodes** connected by edges, with exactly one **root**
(top node) and no cycles. Each node has **children** below it and one **parent**
above (except the root). A **binary tree** restricts each node to **at most two
children** (left and right).

![Binary tree terminology: root at top, internal nodes, leaves at the bottom, and height as the longest root-to-leaf path.](images/62_tree_terms.png)

| Term | Meaning |
|---|---|
| Root | the top node (no parent) |
| Leaf | a node with no children |
| Internal node | a node with at least one child |
| Depth of a node | edges from the **root** down to it |
| Height of a node | edges on the longest path **down** to a leaf |
| Height of tree | height of the root |

> **Memory hook:** an **upside-down family tree** — the ancestor (root) is on top,
> descendants branch downward; leaves are the youngest with no children.

### Types of binary trees (know these names)

- **Full:** every node has 0 or 2 children.
- **Complete:** all levels full except possibly the last, filled left to right
  (this is what a **heap** uses — Module 6).
- **Perfect:** all internal nodes have 2 children and all leaves are at the same
  level.
- **Balanced:** height is O(log n) (no long thin branches).

### Key fact (used everywhere)

A binary tree of height `h` has at most `2^(h+1) − 1` nodes; so `n` nodes need
height **≥ log₂(n)**. **Balanced ⇒ O(log n) height ⇒ fast operations.** A
**degenerate** tree (a straight line) has height `n−1` → behaves like a linked
list.

### MCQs

1. Max nodes in a binary tree of height h? → **2^(h+1) − 1**.
2. Which tree type does a heap use? → **complete** binary tree.
3. Height of a balanced tree with n nodes? → **O(log n)**.

---

## 8a.2 Tree Traversals

Visiting every node in some order. There are two families: **DFS** (depth-first,
uses recursion/stack) and **BFS** (breadth-first, uses a queue).

### DFS: preorder, inorder, postorder

The only difference is **when you visit the root** relative to its subtrees.

![Three DFS orders on the same tree: preorder (Root,L,R), inorder (L,Root,R), postorder (L,R,Root).](images/63_tree_traversals.png)

```text
preorder(node):  visit(node); preorder(left); preorder(right)   # Root first
inorder(node):   inorder(left); visit(node); inorder(right)     # Root middle
postorder(node): postorder(left); postorder(right); visit(node) # Root last
```

- **Inorder of a BST gives sorted order** — a hugely useful fact.
- **Preorder** is used to *copy/serialize* a tree; **postorder** to *delete/free*
  a tree (children before parent) or evaluate an expression tree.
- All are **O(n)** time, **O(h)** space (the recursion stack; h = height).

> **Memory hook:** "pre/in/post" = **where the Root sits**: before, between, or
> after its children.

### Iterative traversals (interview follow-up)

Any recursive traversal can be made **iterative with an explicit stack**
(Module 1). Inorder iterative: push lefts, pop & visit, go right. Morris
traversal even does inorder in **O(1) space** by temporarily threading the tree.

### BFS: level-order (uses a queue)

![Level-order (BFS) visits the tree level by level using a queue.](images/64_level_order.png)

```text
# Level order                                Time O(n), Space O(n)
queue = [root]
while queue:
    node = queue.pop_front()
    visit(node)
    if node.left:  queue.push(node.left)
    if node.right: queue.push(node.right)
```

- BFS is the tool for **"level by level"** questions: level averages, right-side
  view, zig-zag order, minimum depth.

### MCQs

1. Which traversal gives a BST in sorted order? → **inorder**.
2. Level-order uses which structure? → a **queue** (BFS).
3. Traversal space complexity (recursive)? → **O(h)**.

### Problems

- Binary Tree Inorder/Preorder/Postorder (94/144/145); Level Order (102); Zigzag
  Level Order (103); Right Side View (199); Max Depth (104); Diameter (543).

---

## 8a.3 Binary Search Tree (BST)

### Definition

A **BST** is a binary tree with an ordering rule at **every** node:

> all values in the **left** subtree < node's value < all values in the **right**
> subtree.

This rule turns search into a series of "go left or go right" decisions.

![BST: left < node < right; searching for a value just follows the comparisons down one path.](images/65_bst_search.png)

### Search / Insert (follow the comparison)

```text
# Search / Insert                            O(h): O(log n) balanced, O(n) worst
search(node, key):
    while node:
        if key == node.val: return node
        node = node.left if key < node.val else node.right
    return null
# Insert: walk the same way; attach a new node where you fall off.
```

> **Memory hook:** a BST is the **"higher or lower?" guessing game** — each
> comparison throws away half the remaining numbers (when balanced).

### Delete (three cases)

![BST delete: leaf → just remove; one child → splice it in; two children → replace with inorder successor.](images/66_bst_delete.png)

1. **Leaf:** remove it.
2. **One child:** replace the node with that child.
3. **Two children:** replace the node's value with its **inorder successor** (the
   smallest value in the right subtree), then delete that successor.

### The catch: balance

A BST is only fast if it stays **balanced**. Inserting **sorted** data
(1,2,3,4,5) makes a degenerate "linked list" → O(n). The fix is **self-balancing
trees (AVL, Red-Black)** — Module **M08b**.

### BST complexity

| Operation | Balanced | Worst (degenerate) |
|---|---|---|
| search / insert / delete | O(log n) | O(n) |

### Classic BST interview problems

- **Validate BST (LC 98):** inorder must be strictly increasing (or pass
  min/max bounds down). Common bug: only checking immediate children, not the
  whole subtree range.
- **Kth smallest (LC 230):** inorder traversal, stop at k.
- **Lowest Common Ancestor in a BST (LC 235):** walk down; the split point (where
  one target is left and the other right) is the LCA — O(h).

### MCQs

1. BST search time when balanced vs degenerate? → **O(log n) vs O(n)**.
2. How to validate a BST? → **inorder is strictly increasing** (or min/max
   bounds).
3. Two-children delete uses the? → **inorder successor**.

### Problems

- Validate BST (98); Kth Smallest (230); LCA of BST (235); Insert/Delete/Search
  in BST (701/450/700); Convert Sorted Array to BST (108); Range Sum of BST (938).

---

## 8a.4 Common Binary-Tree Problems (patterns)

Most tree problems are solved with **recursion that returns info up from the
children** ("postorder thinking"):

```text
# Template: solve children first, then combine
solve(node):
    if node is null: return base_value
    L = solve(node.left)
    R = solve(node.right)
    return combine(L, R, node)
```

- **Max depth / height (104):** `1 + max(L, R)`.
- **Diameter (543):** longest path = best `L_height + R_height` over all nodes.
- **Balanced check (110):** return height, mark unbalanced if `|L−R| > 1`.
- **Max path sum (124, hard):** at each node, `node + max(0,L) + max(0,R)` is a
  candidate; return `node + max(0, max(L,R))` upward.
- **Lowest Common Ancestor (236):** return the node where left and right searches
  both succeed.
- **Serialize / Deserialize (297):** preorder with null markers.

> **Memory hook:** "**ask the children, then decide**" — almost every tree problem
> is postorder: gather answers from both subtrees, combine at the current node.

### MCQs

1. Tree height recurrence? → `1 + max(left, right)`.
2. Diameter at a node uses? → **left height + right height**.
3. Most tree problems follow which traversal style? → **postorder** (children
   first).

---

## 8a.5 Reconstructing a Tree from Traversals (a FAANG favourite)

### The idea

Given two traversals, rebuild the unique tree. **Preorder** (or postorder) tells
you the **root**; **inorder** tells you which nodes fall in the **left** vs
**right** subtree. (Inorder is essential — preorder+postorder alone is *not*
enough for a general binary tree.)

![Build tree from preorder + inorder: preorder's first element is the root; inorder splits left/right subtrees.](images/89_build_tree.png)

```text
# Build from preorder + inorder              Time O(n), Space O(n)
root = preorder[0]                           # first preorder element
i = index of root in inorder                 # use a hashmap: value -> index
left subtree  = build(next preorder slice, inorder[:i])
right subtree = build(rest preorder slice,  inorder[i+1:])
```

- The **hashmap (value → inorder index)** turns the repeated "find root in
  inorder" search from O(n) into O(1), giving overall **O(n)**.

> **Memory hook:** preorder shouts "I'm the root!"; inorder quietly says "these
> are on my left, those on my right."

### MCQs

1. Which traversal identifies the root? → **preorder** (first) / **postorder**
   (last).
2. Which traversal splits left/right subtrees? → **inorder**.
3. Build time with a hashmap? → **O(n)**.

### Problems

- Construct Binary Tree from Preorder & Inorder (LC 105); from Inorder &
  Postorder (LC 106); from Preorder & Postorder (LC 889, not unique in general).

---

## Module 8a — Concept Review (one page)

- **Tree** = hierarchical, one root, no cycles; **binary** = ≤ 2 children.
- Height `h` ⇒ ≤ `2^(h+1)−1` nodes; balanced ⇒ height O(log n).
- **DFS traversals** differ by root position: pre (R,L,R), in (L,R,R… i.e.
  L,Root,R), post (L,R,Root). **Inorder of a BST = sorted.** All O(n), O(h) space.
- **BFS / level-order** uses a queue → "level by level" problems.
- **BST:** left < node < right; search/insert/delete O(h); delete has 3 cases
  (leaf / one child / two children → inorder successor).
- BST degenerates to O(n) on sorted input → need balancing (M08b).
- Most tree problems = **postorder recursion**: combine children's answers.

## Module 8a — Flash Cards

- Q: Inorder of a BST? **A: sorted order.**
- Q: Level-order structure? **A: queue (BFS).**
- Q: Traversal time/space? **A: O(n) / O(h).**
- Q: BST search balanced vs worst? **A: O(log n) vs O(n).**
- Q: Validate a BST? **A: inorder strictly increasing / min-max bounds.**
- Q: Two-children delete? **A: replace with inorder successor.**
- Q: Tree height recurrence? **A: 1 + max(L, R).**

## Module 8a — Pattern Recognition

- "Sorted output / kth smallest in a BST" → **inorder**.
- "Level by level / shortest path in an unweighted tree" → **BFS (queue)**.
- "Height / diameter / balanced / path sum" → **postorder recursion**.
- "Copy or serialize a tree" → **preorder**.
- "Find a value fast in a dynamic ordered set" → **BST (balanced)**.

## Module 8a — Interview Questions (with follow-ups)

1. *Inorder traversal — recursive and iterative.* FU: *O(1) space (Morris)?*
2. *Validate a BST.* FU: *why is checking only children wrong?*
3. *Lowest common ancestor.* FU: *BST version vs general binary tree.*
4. *Diameter / max path sum.* FU: *why postorder?*
5. *Level order / right-side view.* FU: *do it in one BFS pass.*

## Module 8a — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** number of nodes/height relations, counting binary trees
  (**Catalan numbers** — Module 16), traversal output given a tree (and
  reconstructing a tree from two traversals), BST insert/delete tracing.
- **SEBI/RBI IT:** conceptual MCQs on traversals, BST properties, tree height.

---

*End of Module 8a. Next: Module 8b — Balanced & Range Trees (AVL rotations,
Red-Black trees, Segment Tree, Fenwick/BIT, B & B+ trees) — with visuals.*
