---
title: "Module 5 — Stacks"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — Stacks

> **Why stacks matter.**
> A **stack** is the simplest "remember and come back later" tool. It powers
> function calls (the call stack from Module 1!), undo buttons, expression
> evaluation, browser back, and — most importantly for interviews — the
> **monotonic stack**, which solves a whole family of "next greater / nearest
> smaller / largest rectangle" problems in O(n) that look O(n²) at first.

This module is **P0**. The monotonic stack is one of the highest-value interview
patterns, and stacks/expression evaluation are common in GATE.

> **How to read each technique.** We go **Brute force → Better → Optimal** with
> pseudocode + complexity, plus a memory hook.

### Quick technique selector

![Flowchart: when to use a plain stack, a monotonic stack, or a stack for expressions.](images/49_fc_stack_selector.png)

---

## 5.1 Stack Fundamentals

### Definition

A **stack** is a list where you add and remove only at **one end** (the **top**).
This gives **LIFO** order: **L**ast **I**n, **F**irst **O**ut. The two main
operations are **push** (add to top) and **pop** (remove from top); `peek/top`
looks at the top without removing.

![A stack is LIFO: push and pop happen only at the top, like a pile of plates.](images/43_stack_basics.png)

> **Memory hook:** a **pile of plates** — you put a new plate on top and take the
> top one off first. You never pull a plate from the middle.

### Two ways to implement it

| | Array-based | Linked-list-based |
|---|---|---|
| push/pop | O(1) amortised (resize) | O(1) (add/remove at head) |
| Memory | contiguous, cache-friendly | a pointer per node |
| Downside | may resize | scattered memory |

Both give **O(1)** push/pop. Arrays are usually preferred (cache locality —
Module 1).

### Implementing both (pseudocode)

```text
# ARRAY-BASED stack (top = index of last item)
push(x): if top+1 == cap: grow (double); data[++top] = x    # amortised O(1)
pop():   if top < 0: error (underflow); return data[top--]
peek():  return data[top]
empty(): return top < 0

# LINKED-LIST-BASED stack (top = head of the list)
push(x): node = new Node(x); node.next = head; head = node   # O(1)
pop():   if head == NULL: error; x = head.val; head = head.next; return x
peek():  return head.val
```

- **Array**: watch for **overflow** (fixed array) or pay an occasional resize
  (dynamic array — Module 2). One contiguous block → cache-friendly.
- **Linked list**: never "full" until memory runs out, but each node costs an
  extra pointer and lives in scattered memory (cache misses).

### The call stack — recursion *is* a stack

Every function call pushes a **stack frame** (its parameters, locals, and the
return address) onto the program's **call stack**; returning pops it. So a
recursive algorithm is secretly using a stack — the runtime manages it for you.

- **Depth = recursion depth.** Too-deep recursion overflows this stack
  (**stack overflow**). That is why very deep recursions are rewritten as loops
  with an **explicit stack**.
- Any recursion can be converted to iteration by simulating the call stack by
  hand (push the "work still to do", pop and process). Iterative DFS and the
  iterative tree traversals below (5.4a) do exactly this.

> **Memory hook:** the last function you *called* is the first one to *return* —
> pure LIFO.

### Where stacks are used (real life)

- **Function calls** (the call stack) — Module 1.
- **Undo/redo** in editors; **browser back** button.
- **Expression evaluation** and **syntax checking** in compilers.
- **DFS** (depth-first search) — Module 10 — is recursion = a stack.

### Complexity

| Operation | Time |
|---|---|
| push, pop, peek | O(1) |
| search | O(n) |

### MCQs

1. Stack order? → **LIFO**.
2. push/pop time? → **O(1)**.
3. Which traversal uses a stack? → **DFS** (recursion).
4. Recursion depth maps to what runtime resource? → the **call stack** (overflow
   if too deep).

---

## 5.1a Stack Using Two Queues (a classic interview twist)

You can build a LIFO stack out of two FIFO queues. There are two designs; pick
which operation you want to keep cheap.

```text
# Design A: costly PUSH, O(1) pop  ("push-heavy")
push(x): enqueue x into q2
         move everything from q1 into q2   # x ends up at the front
         swap names of q1 and q2
         # now q1's front is the most-recent element  -> O(n) push
pop():   dequeue from q1                    # O(1)

# Design B: O(1) push, costly POP  ("pop-heavy")
push(x): enqueue x into q1                  # O(1)
pop():   move all but the last from q1 into q2
         answer = dequeue the last one from q1   # the newest
         swap q1 and q2                     # O(n) pop
```

- One operation is unavoidably **O(n)**; you only choose *which*. (Contrast:
  queue-from-two-**stacks** in Module 6 achieves **amortised O(1)** — that
  direction is nicer.)
- LC 225 "Implement Stack using Queues". A common trick uses a **single** queue:
  after enqueuing `x`, rotate the queue by `size-1` so `x` sits at the front.

### MCQs

1. Stack from two queues — best you can do for the two ops? → one is **O(n)**,
   the other **O(1)** (you choose which).
2. Can it be done with one queue? → **yes** (rotate after each push).

---

## 5.2 Valid Parentheses (the classic warm-up)

### Problem

Given a string of brackets `()[]{}`, decide if every opener has a correct,
properly nested closer.

### Idea

Scan left to right. **Push** every opener. On a **closer**, the top of the stack
must be the matching opener — if it is, **pop**; if not (or the stack is empty),
the string is **invalid**. At the end the stack must be **empty**.

![Valid parentheses: push openers, and each closer must match the top opener; the stack must end empty.](images/44_valid_parentheses.png)

```text
# OPTIMAL                                   Time O(n), Space O(n)
match = { ')':'(' , ']':'[' , '}':'{' }
stack = []
for c in s:
    if c is an opener: push c
    else:                                    # c is a closer
        if stack empty or top != match[c]: return false
        pop
return stack is empty
```

> **Memory hook:** every opener must find its partner, and the **last opened**
> must be the **first closed** (LIFO).

### MCQs

1. What must be true at the end for validity? → the **stack is empty**.
2. Time and space? → **O(n) / O(n)**.

### Problems

- Valid Parentheses (LC 20); Min Add to Make Valid (921); Remove Invalid
  Parentheses (301, hard); Longest Valid Parentheses (32, hard).

---

## 5.3 Expression Evaluation (infix, postfix, prefix)

### The three notations

- **Infix:** `2 + 3 * 4` (operators between operands — what humans write; needs
  precedence and brackets).
- **Postfix (RPN):** `2 3 4 * +` (operator after operands — what machines love;
  no brackets needed).
- **Prefix:** `+ 2 * 3 4` (operator before operands).

### Evaluate postfix with a stack

![Evaluate postfix: push numbers; on an operator pop two, apply, and push the result.](images/45_postfix_eval.png)

```text
# Evaluate postfix                          Time O(n), Space O(n)
stack = []
for token in expr:
    if token is a number: push token
    else:                                    # an operator
        b = pop; a = pop
        push( apply(a, token, b) )
return pop
# "2 3 4 * +": push2, push3, push4, '*'->push12, '+'->push14  => 14
```

### Convert infix → postfix (Shunting-Yard, by Dijkstra)

Use a stack to hold operators while you output operands:

```text
for token in infix:
    if operand: output it
    if '(' : push
    if ')' : pop to output until '('
    if operator op:
        while top is an operator with >= precedence: pop to output
        push op
at end: pop all remaining operators to output
```

- **Why postfix?** No brackets, no precedence at evaluation time → a single
  stack pass. This is how calculators and compilers evaluate expressions.

### MCQs

1. Which notation needs no brackets? → **postfix / prefix**.
2. On an operator in postfix evaluation, you pop how many operands? → **two**.
3. Infix→postfix uses which algorithm? → **Shunting-Yard**.

### Problems

- Evaluate Reverse Polish Notation (LC 150); Basic Calculator I/II/III (224/227/
  772); Decode String (394).

---

## 5.4 Monotonic Stack (the high-value pattern)

### What it is

A **monotonic stack** keeps its elements in sorted order (always increasing, or
always decreasing). Before pushing a new element, you **pop everything that
breaks the order**. Those pops are exactly the answers to "what is the next/
previous greater/smaller element" — computed in **O(n)** total.

> **Key insight:** each element is **pushed once and popped once**, so even though
> there is a `while` loop inside the `for` loop, the total work is **O(n)** (the
> same amortised idea as the sliding window in Module 2).

### Next Greater Element

For each element, find the next element to its right that is bigger.

![Next greater element: a decreasing stack of waiting indices; a bigger value pops and answers all smaller ones.](images/46_next_greater.png)

```text
# BRUTE FORCE                                Time O(n^2), Space O(1)
for i in 0..n-1:
    for j in i+1..n-1:
        if a[j] > a[i]: answer[i] = a[j]; break

# OPTIMAL: monotonic (decreasing) stack      Time O(n), Space O(n)
stack = []                 # holds indices whose answer is still unknown
answer = [-1] * n
for i in 0..n-1:
    while stack and a[stack.top] < a[i]:
        answer[ stack.pop() ] = a[i]      # a[i] is their next greater
    stack.push(i)
return answer
```

> **Memory hook:** people waiting in a line for "someone taller". A tall person
> arriving serves (answers) everyone shorter who was waiting.

### Worked trace — next greater of [2, 1, 2, 4, 3]

The stack holds **indices** whose answer is still pending (values decreasing top
to bottom). `-1` means "no greater element to the right".

```text
i  a[i]  action                                stack(idx)   answer so far
-  ----  ------------------------------------  -----------  -------------------
0   2    push 0                                [0]          [_,_,_,_,_]
1   1    1 < a[0]=2, no pop; push 1            [0,1]        [_,_,_,_,_]
2   2    a[1]=1 < 2 -> pop 1 (ans[1]=2);
         a[0]=2 not < 2 -> stop; push 2       [0,2]        [_,2,_,_,_]
3   4    a[2]=2 < 4 -> pop 2 (ans[2]=4);
         a[0]=2 < 4 -> pop 0 (ans[0]=4);
         push 3                               [3]          [4,2,4,_,_]
4   3    3 < a[3]=4, no pop; push 4           [3,4]        [4,2,4,_,_]
end      indices 3,4 left -> ans = -1         -            [4,2,4,-1,-1]
```

Final answer: **[4, 2, 4, -1, -1]**. Notice each index is pushed once and popped
at most once → **O(n)** total.

### Variations (same template)

- **Next smaller / previous greater / previous smaller:** flip the comparison or
  scan right-to-left.
- **Stock span** (LC 901), **daily temperatures** (LC 739): "how many days until
  a warmer day" — same monotonic stack.

### Stock span (LC 901) — worked

The **span** of a day is how many consecutive days (including today) the price
was **≤ today's price**, looking back. Keep a **decreasing** stack of indices;
when today is ≥ the top's price, pop it (those days are covered by today).

```text
# Stock span                                 Time O(n), Space O(n)
stack = []          # indices, prices strictly decreasing
for i in 0..n-1:
    while stack and price[stack.top] <= price[i]:
        stack.pop()
    span[i] = (stack empty) ? (i + 1) : (i - stack.top)
    stack.push(i)

# prices = [100, 80, 60, 70, 60, 75, 85]
# spans   = [  1,  1,  1,  2,  1,  4,  6]
```

Day with price 75 pops 60, 70, 60 → span reaches back 4 days; then 85 pops 75
too → span 6.

### MCQs

1. Monotonic stack total time? → **O(n)** (each element pushed/popped once).
2. For "next greater", the stack is kept? → **decreasing**.

### Problems

- Daily Temperatures (739); Next Greater Element I/II (496/503); Online Stock
  Span (901); Remove K Digits (402); Sum of Subarray Minimums (907).

---

## 5.5 Largest Rectangle in Histogram (a hard favourite)

### Problem

Given bar heights, find the area of the largest rectangle that fits inside the
histogram.

![Largest rectangle in histogram: heights [2,1,5,6,2,3]; the best rectangle is height 5 across two bars = area 10.](images/47_histogram.png)

### Idea (why a stack)

For each bar, the biggest rectangle using that bar as the **shortest** one
extends left and right until it hits a shorter bar. A monotonic **increasing**
stack finds, for every bar, the nearest shorter bar on each side — in O(n).

```text
# BRUTE FORCE                                Time O(n^2)
for each bar i: expand left & right while bars >= h[i]; area = h[i]*width

# OPTIMAL: monotonic increasing stack        Time O(n), Space O(n)
stack = []                 # indices with increasing heights
maxArea = 0
for i in 0..n:                               # one extra step with height 0
    cur = (i == n) ? 0 : h[i]
    while stack and h[stack.top] >= cur:
        height = h[ stack.pop() ]
        width  = stack.empty ? i : i - stack.top - 1
        maxArea = max(maxArea, height * width)
    stack.push(i)
return maxArea
```

- The trailing height `0` flushes everything left in the stack at the end.
- **Follow-up:** "Maximal Rectangle" (LC 85) in a 0/1 matrix = run this histogram
  trick row by row.

### Dry run (heights = [2,1,5,6,2,3] → answer 10)

When we reach the bar of height 2 (index 4), we pop 6 (area 6) and 5 (area
`5 × 2 = 10`). That `10` is the answer — a rectangle of height 5 over the two
bars 5 and 6.

### MCQs

1. Largest-rectangle optimal time? → **O(n)** with a monotonic stack.
2. Why push a final height of 0? → to **flush** the remaining bars.

### Problems

- Largest Rectangle in Histogram (84); Maximal Rectangle (85).

---

## 5.6 Trapping Rain Water (stack / two-pointer)

### Problem

Given an elevation map (bar heights), how much rain water is trapped between the
bars?

![Trapping rain water: water above each bar = min(highest left, highest right) − its own height; total = 6.](images/48_trapping_rain.png)

### Key formula

Water sitting on top of bar `i` = `min(highestLeft[i], highestRight[i]) − h[i]`
(only if positive). Sum over all bars.

```text
# BRUTE FORCE                                Time O(n^2)
for each i: leftMax = max(h[0..i]); rightMax = max(h[i..n-1])
            water += max(0, min(leftMax,rightMax) - h[i])

# BETTER: precompute prefix max + suffix max  Time O(n), Space O(n)
build leftMax[] and rightMax[]; then sum min(...) - h[i]

# OPTIMAL: two pointers                       Time O(n), Space O(1)
L=0; R=n-1; leftMax=rightMax=0; water=0
while L < R:
    if h[L] < h[R]:
        leftMax = max(leftMax, h[L]); water += leftMax - h[L]; L += 1
    else:
        rightMax = max(rightMax, h[R]); water += rightMax - h[R]; R -= 1
```

- A **monotonic stack** also solves it (add water layer by layer as bars pop).
- The **two-pointer** version is the cleanest: O(n) time, O(1) space.

### MCQs

1. Water above bar i? → `min(leftMax, rightMax) − h[i]`.
2. Optimal space for trapping rain water? → **O(1)** (two pointers).

### Problems

- Trapping Rain Water (42); Container With Most Water (11 — two pointers,
  Module 2).

---

## 5.7 Min Stack — getMin() in O(1) (a common design question)

### Problem

Design a stack that also returns its **minimum** element in **O(1)**, alongside
normal push/pop/top in O(1).

### Idea

A normal stack can't find its min without scanning (O(n)). The trick: keep a
**second stack** that, at every level, stores the **minimum so far**. When you
push `x`, also push `min(x, currentMin)`. Now the min stack's top is always the
overall minimum.

```text
# OPTIMAL                                    All operations O(1), Space O(n)
push(x):
    stack.push(x)
    minStack.push( x if minStack empty else min(x, minStack.top) )
pop():
    stack.pop(); minStack.pop()
top():    return stack.top
getMin(): return minStack.top
```

> **Memory hook:** carry a "best score so far" sticker on every plate — the top
> sticker always shows the current minimum.

- **Variation:** store only when a new min appears (saves space), popping the min
  stack only when the popped value equals the current min.
- **Problems:** Min Stack (LC 155); Max Stack (LC 716).

---

## 5.8 Iterative Tree Traversal (recursion → explicit stack)

Recursive tree traversal (Module 8) uses the call stack. To avoid recursion (and
stack-overflow on deep trees), simulate that call stack **yourself** with an
explicit stack. This is a favourite "can you convert recursion to iteration"
interview ask.

### Iterative inorder (left, node, right)

```text
# Iterative inorder                          Time O(n), Space O(h)
stack = []; cur = root
while cur or stack:
    while cur:                # go as far left as possible, pushing on the way
        stack.push(cur); cur = cur.left
    cur = stack.pop()         # leftmost unvisited
    visit(cur)
    cur = cur.right           # then explore its right subtree
```

### Iterative preorder (node, left, right)

```text
# Iterative preorder                         Time O(n), Space O(h)
stack = [root]
while stack:
    node = stack.pop(); visit(node)
    if node.right: stack.push(node.right)   # push right FIRST
    if node.left:  stack.push(node.left)    # so left is processed first
```

- Push **right before left** so the **left** child is popped (and visited) first
  — the stack reverses order.
- **Postorder** is trickier: do a modified preorder (node, right, left) and
  **reverse** the output, or track a "last visited" node.
- **Space O(h)** where `h` is the tree height — the explicit stack mirrors the
  recursion depth exactly, proving the call-stack connection from 5.1.

### MCQs

1. Iterative inorder uses which structure? → an explicit **stack**.
2. In iterative preorder, push which child first? → the **right** child (so left
   is visited first).
3. Space of iterative traversal? → **O(h)** (tree height = recursion depth).

### Problems

- Binary Tree Inorder/Preorder/Postorder Traversal (LC 94 / 144 / 145).

---

## Module 5 — Concept Review (one page)

- **Stack = LIFO**; push/pop/peek are O(1); used by call stack, undo, DFS,
  expression evaluation.
- **Valid parentheses:** push openers, match+pop on closers, end empty.
- **Expressions:** postfix needs no brackets → evaluate with one stack pass;
  infix→postfix via Shunting-Yard.
- **Monotonic stack:** keep increasing/decreasing order; each element pushed/
  popped once → **O(n)**. Solves next greater/smaller, stock span, daily
  temperatures.
- **Largest rectangle in histogram:** increasing stack, O(n); push a final 0 to
  flush.
- **Trapping rain water:** `min(leftMax, rightMax) − h`; best with two pointers
  O(1) space.

## Module 5 — Flash Cards

- Q: Stack order & op cost? **A: LIFO; O(1) push/pop/peek.**
- Q: Valid string condition at the end? **A: stack empty.**
- Q: Postfix evaluation — operator pops how many? **A: two.**
- Q: Monotonic stack total time & why? **A: O(n); each element pushed/popped once.**
- Q: Next-greater uses which stack order? **A: decreasing.**
- Q: Largest rectangle trick? **A: increasing stack + final height 0.**
- Q: Trapping water optimal space? **A: O(1) two pointers.**
- Q: getMin() in O(1)? **A: a second "min-so-far" stack.**
- Q: Recursion uses which hidden structure? **A: the call stack (LIFO frames).**
- Q: Stack from two queues — cost? **A: one op O(n), the other O(1).**
- Q: Iterative traversal structure & space? **A: explicit stack, O(h).**
- Q: Preorder iterative — push which child first? **A: right (so left is visited first).**

## Module 5 — Pattern Recognition

- "Balanced brackets / undo / valid nesting" → **plain stack**.
- "Next/previous greater or smaller, span, warmer day" → **monotonic stack**.
- "Histogram area / maximal rectangle" → **monotonic (increasing) stack**.
- "Trap water / two walls" → **two pointers or stack**.
- "Evaluate / convert an expression" → **stack (postfix / Shunting-Yard)**.
- "Traverse a tree without recursion" → **explicit stack**.
- "Convert recursion to iteration" → **simulate the call stack with a stack**.

## Module 5 — Interview Questions (with follow-ups)

1. *Valid parentheses.* FU: *handle multiple bracket types; min insertions to fix.*
2. *Daily temperatures / next greater.* FU: *prove it is O(n).*
3. *Largest rectangle in histogram.* FU: *extend to a 0/1 matrix (LC 85).*
4. *Trapping rain water.* FU: *do it in O(1) space.*
5. *Evaluate an expression.* FU: *support brackets and precedence.*

## Module 5 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** infix↔postfix↔prefix **conversion and evaluation** (very
  frequently asked), tracing stack push/pop sequences, "which output sequences
  are possible from a stack", and stack-based DFS.
- **Also common:** the **call stack / activation record** (frame = params +
  locals + return address), recursion-to-iteration conversion, and iterative
  traversal order.
- **SEBI/RBI IT:** conceptual MCQs on LIFO, applications, and postfix evaluation.

---

*End of Module 5. Next: Module 6 — Queues & Heaps intro (circular queue, deque,
monotonic queue / sliding-window maximum, priority queue) — with visuals.*
