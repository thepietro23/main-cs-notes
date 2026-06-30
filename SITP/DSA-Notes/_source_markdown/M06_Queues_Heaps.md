---
title: "Module 6 — Queues & Heaps (intro)"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — Queues & Heaps (intro)

> **Why queues and heaps together.**
> A **queue** serves items in the order they arrived (FIFO) — the backbone of
> BFS, scheduling, and buffering. A **heap** (priority queue) always serves the
> **most important** item first, no matter when it arrived — the backbone of
> Dijkstra, top-K, and streaming medians. Together they cover "process in order"
> and "process by priority", two of the most common needs in real systems and
> interviews.

This module is **P0**. Queues power BFS (Module 10); heaps power top-K, Dijkstra,
and "K-th largest" — among the most asked interview patterns.

> **How to read each technique.** We go **Brute force → Better → Optimal** with
> pseudocode + complexity, plus a memory hook.

### Quick technique selector

![Flowchart: choose a queue, deque, monotonic deque, or heap based on the need.](images/56_fc_queue_selector.png)

---

## 6.1 Queue Fundamentals

### Definition

A **queue** adds items at the **rear** and removes them from the **front**, giving
**FIFO** order: **F**irst **I**n, **F**irst **O**ut. Core operations: **enqueue**
(add at rear), **dequeue** (remove from front), **front/peek**.

![A queue is FIFO: enqueue at the rear, dequeue at the front, like a ticket line.](images/50_queue_basics.png)

> **Memory hook:** a **line at a ticket counter** — the first person to arrive is
> the first served. (Compare: a stack is a pile of plates, LIFO.)

### Where queues are used

- **BFS** (breadth-first search) — Module 10.
- **CPU / task scheduling**, print queues, **message queues** (Kafka, RabbitMQ).
- **Buffering** streaming data (producer–consumer).

### The problem with a simple array queue

If you dequeue by removing index 0 of an array, everything shifts → O(n). If you
just move a `front` pointer forward without reusing space, the front of the array
is wasted. The fix is a **circular queue**.

### Complexity

| Operation | Time |
|---|---|
| enqueue, dequeue, peek | O(1) |
| search | O(n) |

### MCQs

1. Queue order? → **FIFO**.
2. Which search uses a queue? → **BFS**.
3. Dequeue by shifting an array costs? → **O(n)** (use a circular queue instead).

---

## 6.2 Circular Queue (ring buffer)

### Idea

Treat the array as a **circle**: when `rear` reaches the end, it **wraps back to
index 0** using modulo. This reuses freed slots, so enqueue/dequeue stay O(1)
with no shifting and no wasted space.

![Circular queue: the rear wraps back to index 0 using modulo, reusing freed slots.](images/51_circular_queue.png)

```text
# Circular queue with a fixed capacity      All ops O(1)
enqueue(x): if full -> reject
            data[rear] = x; rear = (rear + 1) % capacity; size++
dequeue():  if empty -> reject
            x = data[front]; front = (front + 1) % capacity; size--; return x
```

- **Full vs empty** both can look like `front == rear` — track a `size` counter
  (or leave one slot empty) to tell them apart. (Classic GATE trap.)

> **Memory hook:** a **circular running track** — after the last lane you are back
> at lane 0.

### Production usage

Ring buffers in audio/video streaming, network packet buffers, OS I/O buffers.

### MCQs

1. Circular queue wrap formula? → `(index + 1) % capacity`.
2. How to distinguish full from empty? → keep a **size** counter (or leave one
   slot empty).

### Problems

- Design Circular Queue (LC 622); Design Circular Deque (LC 641).

---

## 6.3 Deque (double-ended queue)

### Idea

A **deque** lets you add and remove at **both** ends in O(1). It can act as a
stack *and* a queue, and it is the engine behind the **monotonic queue** trick.

![A deque allows push/pop at both the front and the back.](images/52_deque.png)

```text
push_front, pop_front, push_back, pop_back   # all O(1)
```

### Queue using stacks / stack using queues (classic interview)

- **Queue with two stacks:** an `in` stack and an `out` stack. Push to `in`; to
  pop, if `out` is empty, pour everything from `in` into `out` (reversing order),
  then pop `out`. **Amortised O(1)**.
- **Stack with two queues:** doable but one operation becomes O(n).

### MCQs

1. Deque op cost at both ends? → **O(1)**.
2. Queue from two stacks pop cost? → **amortised O(1)**.

### Problems

- Implement Queue using Stacks (LC 232); Implement Stack using Queues (LC 225);
  Design Circular Deque (LC 641).

---

## 6.4 Monotonic Queue → Sliding Window Maximum

### Problem

Given an array and a window size `k`, find the **maximum of every window** as it
slides. (The sliding-window sum was easy in Module 2; the *maximum* is harder
because when the max leaves the window, you need the next-best instantly.)

### Idea

Keep a **deque of indices** whose values are **decreasing**. The **front** is
always the current window's maximum. Before adding a new element, **pop from the
back** every smaller value (they can never be the max while this bigger one is
around). Also **pop the front** if it has slid out of the window.

![Sliding window maximum: a decreasing deque keeps the window max at its front; weaker values are popped from the back.](images/53_monotonic_queue.png)

```text
# BRUTE FORCE                                Time O(n*k)
for each window: scan k elements for the max

# OPTIMAL: monotonic deque                   Time O(n), Space O(k)
dq = deque of indices (values decreasing)
for i in 0..n-1:
    if dq.front <= i - k: dq.pop_front()           # drop indices out of window
    while dq and a[dq.back] <= a[i]: dq.pop_back()  # drop smaller values
    dq.push_back(i)
    if i >= k-1: output a[dq.front]                 # front is the window max
```

- **Why O(n):** each index is pushed once and popped once.

> **Memory hook:** a **VIP line** — when a stronger person arrives, everyone
> weaker standing behind is sent away; the strongest is always at the front.

### MCQs

1. Sliding-window-maximum optimal time? → **O(n)** with a monotonic deque.
2. The deque keeps values in what order? → **decreasing** (front = max).

### Problems

- Sliding Window Maximum (LC 239); Shortest Subarray with Sum ≥ K (LC 862, hard);
  Jump Game VI (LC 1696).

---

## 6.5 Priority Queue & Binary Heap

### What a heap is

A **heap** is a **complete binary tree** (filled level by level, left to right)
with the **heap property**:

- **Min-heap:** every parent ≤ its children → the **smallest** is at the root.
- **Max-heap:** every parent ≥ its children → the **largest** is at the root.

A **priority queue** is the *idea* ("always give me the most important next"); a
**heap** is the usual *implementation*.

![A min-heap is a complete tree where every parent is ≤ its children; stored compactly as an array.](images/54_heap.png)

### Stored as an array (no pointers!)

Because the tree is complete, we store it in a plain array:

```
parent(i) = (i - 1) / 2     left(i) = 2i + 1     right(i) = 2i + 2
```

This is cache-friendly (Module 1) and needs no node pointers.

### The two operations

![Heap push sifts a new value up; pop-min moves the last value to the root and sifts it down; both O(log n).](images/55_heap_ops.png)

```text
# push(x)                                    O(log n)
add x at the end; while x < parent: swap up        # "sift up"

# pop_min()                                  O(log n)
save root (the min); move last element to root;
while it is bigger than its smaller child: swap down  # "sift down"
return the saved min
```

- **peek (min/max):** O(1) — it's the root.
- **build-heap from an array:** O(n) (not O(n log n)!) — a classic GATE result
  (the leaves need no work; only the upper nodes sift down a little).
- **Heapsort:** build a heap, then pop the root n times → **O(n log n)**, in-place.

> **Memory hook:** a **company hierarchy** — the boss (min or max) is always on
> top; promotions (sift up) and demotions (sift down) follow the chain.

### Complexity summary

| Operation | Time |
|---|---|
| peek (top) | O(1) |
| push / pop | O(log n) |
| build-heap | O(n) |
| heapsort | O(n log n) |

### MCQs

1. Heap children of index i? → **2i+1 and 2i+2**.
2. build-heap time? → **O(n)**.
3. Min-heap root holds? → the **minimum**.

---

## 6.6 Heap Applications (the interview gold)

### A) Top-K elements

Find the K largest (or smallest) elements.

```text
# BRUTE FORCE: sort everything               O(n log n)
sort, take the last K

# OPTIMAL: a heap of size K                   O(n log k), Space O(k)
keep a MIN-heap of size k (for K largest):
for x in arr:
    push x; if heap size > k: pop the min
heap now holds the K largest
```

- **Why a min-heap for K *largest*?** The smallest of your current top-K sits at
  the root, ready to be kicked out when a bigger one arrives.

### B) K-th largest / smallest

Same idea — the root of a size-K heap is the K-th largest (LC 215). Quickselect
(Module 12) gives O(n) average as an alternative.

### C) Merge K sorted lists/arrays

Put the first element of each of the K lists into a min-heap; repeatedly pop the
smallest and push the next element from that list.

```text
# Merge K sorted                             O(N log k)   (N = total elements)
push the head of each list into a min-heap
while heap not empty:
    pop smallest -> append to result; push the next node from that list
```

### D) Median from a data stream (two heaps)

Keep a **max-heap** for the lower half and a **min-heap** for the upper half,
balanced in size. The median is the top of one heap (odd total) or the average of
both tops (even total). Each insert is O(log n); median is O(1). (LC 295.)

> **Memory hook:** two heaps **facing each other** — the biggest of the small
> half and the smallest of the big half meet exactly at the median.

### MCQs

1. K largest elements efficiently? → a **size-K min-heap**, O(n log k).
2. Merge K sorted lists time? → **O(N log k)**.
3. Streaming median structure? → **two heaps** (max-heap + min-heap).

### Problems

- Kth Largest Element (215); Top K Frequent Elements (347); K Closest Points
  (973); Merge k Sorted Lists (23); Find Median from Data Stream (295); Task
  Scheduler (621).

---

## Module 6 — Concept Review (one page)

- **Queue = FIFO**; enqueue rear, dequeue front, O(1); powers BFS & scheduling.
- **Circular queue** wraps with `% capacity` → O(1), no wasted space; track size
  to tell full from empty.
- **Deque** = both ends O(1); base for monotonic queue; queue-from-2-stacks is
  amortised O(1).
- **Monotonic deque** → sliding-window max/min in O(n) (decreasing deque, front =
  max).
- **Heap / priority queue** = complete tree, array-stored (`2i+1`, `2i+2`); push/
  pop O(log n), peek O(1), build O(n), heapsort O(n log n).
- **Heap uses:** Top-K (size-K heap, O(n log k)), K-th largest, merge K sorted
  (O(N log k)), streaming median (two heaps).

## Module 6 — Flash Cards

- Q: Queue vs stack order? **A: FIFO vs LIFO.**
- Q: Circular queue wrap? **A: (i+1) % capacity.**
- Q: Sliding window max in O(n)? **A: monotonic (decreasing) deque.**
- Q: Heap children of i? **A: 2i+1, 2i+2; parent (i-1)/2.**
- Q: push/pop/peek/build costs? **A: log n / log n / O(1) / O(n).**
- Q: K largest efficiently? **A: size-K min-heap, O(n log k).**
- Q: Streaming median? **A: two heaps (max-heap + min-heap).**

## Module 6 — Pattern Recognition

- "Process in arrival order / level-by-level (BFS)" → **queue**.
- "Add/remove at both ends" → **deque**.
- "Max/min of a sliding window" → **monotonic deque**.
- "Top-K / K-th largest / 'closest K'" → **heap (size K)**.
- "Always need the current smallest/largest" → **priority queue**.
- "Merge many sorted sequences" → **min-heap of heads**.
- "Median of a stream" → **two heaps**.

## Module 6 — Interview Questions (with follow-ups)

1. *Implement a queue with two stacks.* FU: *prove amortised O(1).*
2. *Sliding window maximum.* FU: *why O(n)? what does the deque store?*
3. *K-th largest element.* FU: *heap vs quickselect trade-offs.*
4. *Merge k sorted lists.* FU: *complexity with a heap?* → O(N log k).
5. *Median from a data stream.* FU: *which heap holds which half?*

## Module 6 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** circular-queue full/empty conditions and index formulas;
  **heap array index formulas**; **build-heap is O(n)** (not O(n log n));
  heapsort complexity; number of swaps in heap operations; min/max-heap tracing.
- **SEBI/RBI IT:** conceptual MCQs on FIFO, priority queues, heap properties.

---

*End of Module 6. Next: Module 7 — Hash Tables (hash functions, collisions:
chaining vs open addressing, load factor, Bloom filters) — with visuals.*
