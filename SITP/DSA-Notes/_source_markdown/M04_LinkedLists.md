---
title: "Module 4 — Linked Lists"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — Linked Lists

> **Why linked lists matter.**
> An array stores items back-to-back, so inserting in the middle means shifting
> everything. A **linked list** stores each item in its own little box (a
> **node**) that also holds the address of the **next** box. Now inserting or
> deleting is just "rewire a couple of pointers" — O(1) — no shifting. The price:
> you lose O(1) random access (no `arr[i]`); to reach the 5th node you must walk
> from the start. Linked lists also teach **pointer thinking**, which powers
> trees and graphs later.

This module is **P0** for interviews (pointer manipulation is a favourite test)
and **P0** for GATE (operations, complexity, and tracing).

> **How to read each technique.** We go **Brute force → Better → Optimal** with
> pseudocode + complexity, plus a memory hook.

### Quick technique selector

![Flowchart: which linked-list trick to use — fast/slow, reversal, merge, or LRU.](images/42_fc_ll_selector.png)

---

## 4.1 What is a Linked List?

### Definition

A **linked list** is a chain of **nodes**. Each node holds two things:

1. **data** (the value), and
2. **next** (the address/pointer of the next node).

The list is accessed through a **head** pointer (the first node). The last node's
`next` is **NULL** (nothing after it).

> **Memory hook:** a **treasure hunt** — each clue (node) holds a value *and*
> tells you where to find the **next** clue. You must follow them in order; you
> cannot jump straight to clue #5.

### Array vs Linked List (a key interview comparison)

| | Array | Linked List |
|---|---|---|
| Memory | one contiguous block | scattered nodes joined by pointers |
| Access `i`-th | **O(1)** (formula) | **O(n)** (must walk) |
| Insert/delete at front | O(n) (shift) | **O(1)** (rewire) |
| Insert/delete in middle | O(n) | O(1) *if you already have the node* |
| Extra memory | none | one pointer per node |
| Cache friendliness | **great** (contiguous) | poor (scattered → cache misses) |

> **Interview line:** "Use a linked list when you do many insert/deletes and
> rarely need random access; use an array when you need indexing and cache
> speed." (Recall Module 1: arrays usually win on speed due to cache locality.)

### MCQs

1. Access the i-th element of a linked list? → **O(n)** (walk from head).
2. Insert at the front of a linked list? → **O(1)**.
3. Why can arrays be faster than lists at the same O(n)? → **cache locality**.

---

## 4.2 Types of Linked Lists

![Three types: singly (next only), doubly (next + prev), circular (last points back to first).](images/36_ll_types.png)

- **Singly linked:** each node points to the **next** only. Light on memory; you
  can only go forward.
- **Doubly linked:** each node points to **next and prev**. Uses more memory but
  lets you go both ways and **delete a node in O(1)** when you have a pointer to
  it (you can reach its previous node). Used in LRU caches and browser history.
- **Circular:** the last node points **back to the first**. Great for round-robin
  scheduling and buffers.

### The dummy (sentinel) node trick

A **dummy head** is a fake node placed before the real first node. It removes
annoying "what if the list is empty / what if I delete the head" special cases,
because every real node now always has a node before it.

> **Memory hook:** a dummy node is a **placeholder zero** — like the extra `0` in
> a prefix-sum array (Module 2), it makes the edge cases disappear.

### MCQs

1. Which list lets you delete a known node in O(1)? → **doubly linked**.
2. What problem does a dummy head solve? → **head/empty edge cases**.

---

## 4.3 Core Operations

### Traversal, insert, delete

```text
# Traverse                                  O(n)
cur = head
while cur: visit(cur); cur = cur.next

# Insert after a node p                     O(1)
new.next = p.next
p.next  = new

# Delete the node after p                   O(1)
p.next = p.next.next     # (free the removed node in C/C++)
```

### Edge cases & common mistakes (these are where interviews catch you)

- **Losing the rest of the list:** set the new node's `next` **before** changing
  the previous node's `next`. Order matters.
- **NULL checks:** always check `cur` and `cur.next` before using them.
- **The head changing:** inserting/deleting at the front changes `head` — return
  the new head (or use a dummy).
- **Single node / empty list.**

### MCQs

1. Insert/delete given the position pointer? → **O(1)**.
2. Best tool to avoid head edge cases? → a **dummy node**.

---

## 4.4 Reversing a Linked List

### The idea

Walk the list and **flip each `next` pointer** to point backwards. You need three
pointers: `prev`, `cur`, and `nxt` (to remember the rest before you overwrite).

![Reverse: use prev/cur/next to flip each arrow backwards, one node at a time.](images/37_ll_reverse.png)

```text
# OPTIMAL: iterative reversal               Time O(n), Space O(1)
prev = NULL; cur = head
while cur:
    nxt = cur.next      # save the rest
    cur.next = prev     # flip the pointer
    prev = cur          # advance prev
    cur = nxt           # advance cur
return prev             # prev is the new head

# RECURSIVE version                          Time O(n), Space O(n) (call stack)
reverse(node):
    if node is NULL or node.next is NULL: return node
    newHead = reverse(node.next)
    node.next.next = node     # make the next node point back to me
    node.next = NULL
    return newHead
```

> **Memory hook:** "save next → flip → step forward." Say it out loud while
> coding; it prevents the classic *lost-list* bug.

### Reverse in k-groups (a hard favourite)

Reverse the list in chunks of `k` (LC 25). Reverse the first `k` nodes, then
recursively/iteratively connect to the reversed rest. Time O(n), Space O(1)
(iterative). This tests whether you really understand the 3-pointer reversal.

### MCQs

1. Iterative reversal space? → **O(1)**.
2. Recursive reversal space? → **O(n)** (call stack).
3. The three pointers used? → **prev, cur, next**.

### Problems

- **Easy:** Reverse Linked List (LC 206).
- **Medium:** Reverse Linked List II / a sublist (LC 92); Swap Nodes in Pairs
  (LC 24).
- **Hard:** Reverse Nodes in k-Group (LC 25).

---

## 4.5 Fast & Slow Pointers (Tortoise and Hare)

### The idea

Move two pointers at different speeds: **slow** by 1 node, **fast** by 2 nodes.
This one trick solves a whole family of problems.

![Fast & slow: fast moves 2 steps, slow moves 1; fast hits the end when slow is at the middle, and in a cycle they meet.](images/38_fast_slow.png)

### Use 1 — Find the middle node

When `fast` reaches the end, `slow` is exactly at the **middle**. One pass, O(n),
O(1) space. (Used in "sort list", "palindrome list", etc.)

### Use 2 — Detect a cycle (Floyd's algorithm)

If the list has a **loop**, the fast pointer keeps going around and eventually
**laps** the slow one — they **meet**. If `fast` reaches NULL, there is **no
cycle**.

```text
# Cycle detection                           Time O(n), Space O(1)
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast: return "cycle"
return "no cycle"
```

```text
# Brute force alternative (for contrast)    Time O(n), Space O(n)
seen = empty set
for each node: if node in seen: cycle; else add node
```

> Floyd's wins because it uses **O(1) space** instead of a hash set.

### Use 3 — Find where the cycle starts

After slow and fast meet, **reset one pointer to the head** and move both **one
step at a time**; they meet **at the cycle's start**.

![Why it works: with distances a (head→start), b (start→meet), c (meet→start), the math gives a = c, so resetting one pointer to head makes them meet at the start.](images/39_floyd_start.png)

**Why (short proof):** let `a` = head→start, `b` = start→meeting point,
`c` = meeting point→start (so loop length = `b+c`). Slow travelled `a+b`; fast
travelled `2(a+b)` and also `a+b+`(whole loops). Working it out gives **`a = c`**
(plus full loops). So a pointer from the head and a pointer from the meeting point
move the same distance to reach the start → they meet there.

> **Memory hook:** on a circular running track, the faster runner always catches
> the slower one — and the leftover distance equals the head-to-start distance.

### Use 4 — Palindrome linked list

Find the middle (fast/slow), reverse the second half, compare the two halves.
O(n) time, O(1) space (LC 234).

### MCQs

1. Fast/slow space for cycle detection? → **O(1)**.
2. When fast hits the end, slow is at the? → **middle**.
3. To find the cycle start, reset one pointer to? → the **head**, then move both
   by 1.

### Problems

- **Easy:** Linked List Cycle (141); Middle of the List (876).
- **Medium:** Linked List Cycle II / start (142); Palindrome Linked List (234);
  Remove Nth Node From End (19 — two pointers k apart); Happy Number (202 — same
  trick on numbers!).

---

## 4.6 Merge Two Sorted Lists

### The idea

Like the merge step of merge sort: keep a pointer to each list, repeatedly attach
the **smaller head** to the result, and advance that list. Use a **dummy head** so
you don't special-case the first node.

![Merge two sorted lists: repeatedly pick the smaller of the two heads and relink it.](images/40_merge_sorted.png)

```text
# OPTIMAL                                    Time O(n+m), Space O(1)
dummy = new Node; tail = dummy
while L1 and L2:
    if L1.val <= L2.val: tail.next = L1; L1 = L1.next
    else:                tail.next = L2; L2 = L2.next
    tail = tail.next
tail.next = L1 if L1 else L2     # attach whatever is left
return dummy.next
```

- We **relink** existing nodes (no new data nodes) → O(1) extra space.
- **Merge K sorted lists** (LC 23): put the heads in a min-heap and always pull
  the smallest → O(N log k) (heaps come in Module 6/9).

### MCQs

1. Merge two sorted lists time? → **O(n+m)**.
2. Why a dummy head here? → avoids the **first-node** special case.

### Problems

- **Easy:** Merge Two Sorted Lists (21).
- **Hard:** Merge k Sorted Lists (23); Sort List (148 — merge sort on a list,
  O(n log n)).

---

## 4.7 Application — LRU Cache (a top interview project)

### The problem

Build a cache with a fixed capacity that supports **get(key)** and **put(key,
value)** in **O(1)**, and when full, **evicts the Least Recently Used** item.

### The design (the classic answer)

Combine two structures:

- a **HashMap** `key → node` for O(1) lookup, and
- a **Doubly Linked List** ordered by recency: **most recently used at the head**,
  **least recently used at the tail**.

![LRU cache = HashMap (O(1) find) + Doubly Linked List (O(1) move/evict); MRU at head, LRU at tail.](images/41_lru_cache.png)

```text
get(key):
    if key not in map: return -1
    node = map[key]; move node to head (most recent); return node.value

put(key, value):
    if key in map: update value; move node to head
    else:
        if size == capacity: remove tail node; delete its key from map
        create node at head; map[key] = node
```

- **Why a doubly linked list?** To remove a node from the middle in **O(1)**, you
  need its **previous** node — a doubly linked list gives you that for free.
- **Why the hashmap?** Without it, finding a node would be O(n).
- Together: every operation is **O(1)**.

> **Memory hook:** a pile of recently-used cards — touch a card → move it to the
> **top**; when the pile is too tall → throw away the **bottom** card.

- **LFU cache** (LC 460): evict the *least frequently* used (harder — needs
  frequency buckets).

### MCQs

1. LRU cache uses which two structures? → **HashMap + doubly linked list**.
2. Why doubly (not singly) linked? → **O(1) removal from the middle**.
3. Where is the least-recently-used item? → at the **tail**.

### Problems

- **Medium:** LRU Cache (146).
- **Hard:** LFU Cache (460); All O(1) Data Structure (432).

---

## 4.8 Other Classics (quick hits)

- **Remove Nth node from end (LC 19):** move one pointer `n` steps ahead, then
  move both together; when the front hits the end, the back is at the node to
  remove. One pass.
- **Intersection of two lists (LC 160):** two pointers that switch lists after
  reaching the end meet at the intersection (clever length-equaliser).
- **Copy list with random pointer (LC 138):** either a hashmap `old → new`, or
  the O(1)-space trick of weaving copies between originals.
- **Add two numbers as lists (LC 2):** walk both lists carrying a `carry`.

---

## Module 4 — Concept Review (one page)

- A **node** = data + pointer to next; reach via **head**; last `next` = NULL.
- **List vs array:** list = O(1) insert/delete, O(n) access, poor cache; array =
  O(1) access, O(n) insert, great cache.
- **Types:** singly (forward), doubly (both ways, O(1) middle delete), circular
  (loops back). **Dummy node** kills edge cases.
- **Reverse** = save-next → flip → step forward (3 pointers), O(n)/O(1).
- **Fast & slow** (tortoise & hare): middle, cycle detect (Floyd, O(1) space),
  cycle start (reset to head), palindrome.
- **Merge sorted** = pick smaller head with a dummy, O(n+m).
- **LRU cache** = HashMap + doubly linked list → all O(1); evict the tail.

## Module 4 — Flash Cards

- Q: Access i-th node? **A: O(n).** Insert at front? **A: O(1).**
- Q: Reverse a list — which pointers? **A: prev, cur, next; O(1) space.**
- Q: Detect a cycle in O(1) space? **A: Floyd's fast & slow.**
- Q: Find the cycle start? **A: after meeting, reset one pointer to head, move both +1.**
- Q: Middle of a list in one pass? **A: fast/slow.**
- Q: Merge two sorted lists? **A: dummy head, pick smaller, O(n+m).**
- Q: LRU cache structures? **A: HashMap + doubly linked list (O(1)).**
- Q: Why doubly linked for LRU? **A: O(1) middle removal.**

## Module 4 — Pattern Recognition

- "Cycle / middle / nth-from-end / palindrome list" → **fast & slow pointers**.
- "Reverse / reorder parts of a list" → **3-pointer reversal**.
- "Combine sorted lists" → **merge with a dummy head** (k lists → min-heap).
- "O(1) get/put with eviction" → **HashMap + doubly linked list (LRU)**.
- "Avoid head/empty special cases" → **dummy node**.

## Module 4 — Interview Questions (with follow-ups)

1. *Reverse a linked list.* FU: *recursive too; reverse only nodes m..n.*
2. *Detect a cycle.* FU: *find the start; prove why it works.*
3. *Find the middle in one pass.* FU: *even length — which middle?*
4. *Design an LRU cache.* FU: *why doubly linked? make it thread-safe?*
5. *Merge k sorted lists.* FU: *complexity with a heap?* → O(N log k).

## Module 4 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** time complexity of insert/delete/search at head/middle/end
  for singly vs doubly; tracing pointer updates; circular-list questions; "what
  does this pointer code do" snippets.
- **Memory:** doubly linked uses an extra pointer per node — sometimes asked.
- **SEBI/RBI IT:** conceptual MCQs (list vs array, types, complexity).

---

*End of Module 4. Next: Module 5 — Stacks (monotonic stack, next greater element,
largest rectangle in histogram, expression parsing) — with visuals.*
