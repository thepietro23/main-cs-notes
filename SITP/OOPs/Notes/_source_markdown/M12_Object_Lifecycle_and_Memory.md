---
title: "Module 12 — Object Lifecycle & Memory"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 12 — Object Lifecycle & Memory

> **Why this module matters.**
> Objects are born, live, and die — and Python manages that for you. But "for you"
> doesn't mean "invisibly": knowing **reference counting**, the **cyclic garbage
> collector**, `__del__`'s pitfalls, and **`weakref`** is the difference between code
> that leaks memory / holds files open and code that's clean. This is also a classic
> interview area ("how does Python manage memory?", "what's a reference cycle?") and
> essential for backend services that run for weeks without restarting.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★★      | ★★          | ★★★★        | ★★         |

**Most-asked concepts:** how Python manages memory (**reference counting +
cyclic GC**); reference cycles; what `del` really does; `__del__` and why it's
unreliable; `weakref` (and `WeakValueDictionary`); shallow vs deep copy hooks;
why context managers beat `__del__` for cleanup.

**What you must be able to do after this module:** explain reference counting and
cycles; describe when the cyclic GC runs; state what `del x` does; list `__del__`'s
pitfalls and use a context manager instead; and use `weakref` for a cache.

---

## 12.1 The Object Lifecycle

![Lifecycle: __new__ allocates, __init__ initialises, the object is used while referenced, and when its refcount hits 0 it is freed.](images/m12_01_lifecycle.png)

Every object goes through: **creation** (`__new__` allocates, `__init__`
initialises — Module 3), **use** (while something references it), and **destruction**
(freed when unreachable). In CPython, destruction is **immediate** the moment the
last reference goes away (via reference counting) — plus a periodic sweep for cycles.

---

## 12.2 Reference Counting (CPython's primary mechanism)

CPython gives every object a **reference count**: how many references point to it.
Creating a reference **increments** it; deleting/rebinding one **decrements** it. When
it hits **0**, the object is freed **instantly**.

![A list object with refcount 2: a = [] makes it 1, b = a makes it 2, del a drops it to 1; when the count reaches 0 the memory is reclaimed immediately.](images/m12_02_refcount.png)

```python
import sys
a = []                       # refcount 1
b = a                        # refcount 2
print(sys.getrefcount(a))    # shows 3 (getrefcount's own temp arg adds 1)
del b                        # refcount back to 1
```

- **Pros:** deterministic, immediate reclamation; memory freed as soon as possible.
- **Con:** cannot free **reference cycles** (below) — hence a second mechanism.

> Note: `sys.getrefcount(x)` reports one extra because passing `x` to it creates a
> temporary reference.

---

## 12.3 Reference Cycles & the Cyclic Garbage Collector

If two objects reference **each other**, their counts never reach 0 even when nothing
outside points to them — a **reference cycle** that pure refcounting can't reclaim.

![Objects A and B reference each other (A.b = B, B.a = A); each keeps the other's refcount above 0, so the cyclic generational garbage collector is needed to detect and free them.](images/m12_03_ref_cycle.png)

```python
class Node: pass
a, b = Node(), Node()
a.other = b
b.other = a                  # cycle: a <-> b
del a, b                     # outside refs gone, but they still reference each other
import gc
gc.collect()                 # the cyclic GC detects & frees the unreachable cycle
```

Python adds a **generational, cyclic garbage collector** (`gc` module) that
periodically finds unreachable cycles and frees them. It runs automatically based on
allocation thresholds; you can `gc.collect()` manually or `gc.disable()` in special
cases. **Avoiding cycles** (or using `weakref`) reduces GC pressure.

---

## 12.4 What `del x` Actually Does

`del x` **removes the name `x`** from its namespace and **decrements** the object's
refcount. It does **not** directly destroy the object — the object dies only if that
was its **last** reference.

![del a unbinds the name a and drops the object's refcount from 2 to 1; the object survives because b still references it.](images/m12_04_del_statement.png)

```python
a = [1, 2, 3]
b = a
del a            # name 'a' gone; object refcount 2 -> 1
print(b)         # [1, 2, 3]  -> object still alive via b
```

> **Interview one-liner:** *"`del` unbinds a name and drops a reference; the object is
> collected only when its refcount reaches 0 (or the cyclic GC reclaims it)."*

---

## 12.5 `__del__` — the finaliser and its pitfalls

`__del__` is called when an object is **about to be destroyed**. It's tempting to use
it for cleanup (closing files, releasing locks) — but it's **unreliable**:

![__del__ runs when the object is about to be destroyed, but has pitfalls: non-deterministic timing, may not run at interpreter exit, and exceptions inside it are ignored.](images/m12_05_del_method.png)

- **Non-deterministic timing** — you don't control *when* (or if) it runs.
- **May not run at interpreter exit** — pending finalisers can be skipped.
- **Exceptions inside `__del__` are ignored** (only printed) — bugs hide.
- **Cycles** historically delayed collection of objects with `__del__` (improved in
  modern Python but still a smell).

```python
class Bad:
    def __del__(self):
        self.file.close()     # DON'T rely on this for critical cleanup
```

> **Rule:** never depend on `__del__` for releasing important resources. Use a
> **context manager** or explicit `close()`/`try-finally`.

---

## 12.6 `weakref` — reference without keeping alive

A **weak reference** lets you refer to an object **without** increasing its refcount —
so it can still be garbage-collected. Perfect for **caches, observers, and back-
references** that must not keep objects alive.

![A weakref points at an object without raising its refcount; once the last strong reference is dropped, the object dies and the weakref becomes None.](images/m12_06_weakref.png)

```python
import weakref

class Data: pass
d = Data()
r = weakref.ref(d)           # weak reference — does NOT keep d alive
print(r() is d)              # <Data ...>  (dereference with r())
del d                        # last STRONG ref gone
print(r())                   # None  -> object was collected

# A cache that doesn't leak: entries vanish when values are no longer used elsewhere
cache = weakref.WeakValueDictionary()
```

- `weakref.ref(obj)` → call it (`r()`) to get the object or `None`.
- `WeakValueDictionary` / `WeakKeyDictionary` → auto-pruning caches.
- **Use case:** the **Observer** pattern (Module 15) uses weak refs so a subject
  doesn't keep dead observers alive.

---

## 12.7 Copying Objects — `copy` / `deepcopy` hooks

Recall Module 2's shallow-vs-deep distinction. Classes can **customise** how they're
copied via `__copy__` and `__deepcopy__`.

![copy.copy is shallow (shares nested objects; customise with __copy__); copy.deepcopy clones the whole object tree (customise with __deepcopy__).](images/m12_07_copy_deep.png)

```python
import copy

class Cache:
    def __init__(self, data):
        self.data = data
        self._conn = "db-connection"    # should NOT be copied
    def __deepcopy__(self, memo):
        clone = Cache(copy.deepcopy(self.data, memo))
        clone._conn = self._conn        # reuse the same connection, don't clone it
        return clone

c2 = copy.deepcopy(Cache([1, 2, 3]))
```

- `__copy__(self)` → return a shallow copy.
- `__deepcopy__(self, memo)` → return a deep copy; `memo` avoids infinite recursion on
  cycles (it caches already-copied objects).

---

## 12.8 Cleanup: Context Managers, not `__del__`

![For releasing resources, __del__ is unreliable (non-deterministic timing, may never run); a with-statement / try-finally is deterministic and guarantees cleanup — the right tool.](images/m12_08_cleanup_choice.png)

```python
# WRONG: relying on __del__
class FileWrapper:
    def __del__(self): self.f.close()     # may run late or never

# RIGHT: a context manager (deterministic)
class FileWrapper:
    def __enter__(self):
        self.f = open("data.txt")
        return self.f
    def __exit__(self, *exc):
        self.f.close()                    # guaranteed, immediately after the block

with FileWrapper() as f:
    data = f.read()
# file is definitely closed here
```

For files, sockets, locks, and DB connections: **always** use `with` /
`contextlib`, or explicit `close()` in a `finally`. `__del__` is a last-ditch safety
net, never the primary plan.

---

## Module 12 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "How does Python manage memory?" | "Garbage collection." | "Primarily **reference counting** (immediate free at count 0), plus a **generational cyclic GC** for reference cycles refcounting can't reclaim." |
| "What's a reference cycle?" | (unsure) | "Objects referencing each other so their counts never hit 0; the cyclic GC detects and frees them; `weakref` can avoid creating them." |
| "What does `del x` do?" | "Deletes the object." | "Unbinds the name and decrements the refcount; the object is freed only if that was the last reference." |
| "Use `__del__` for cleanup?" | "Sure." | "No — non-deterministic, may not run, swallows exceptions. Use a context manager / `try-finally`." |

---

## Module 12 — Exam Mapping

- **GATE CS:** garbage collection concepts, reference counting vs tracing, cycles.
- **SEBI / RBI IT:** basic memory-management terms.
- **FAANG / backend:** reference counting + cyclic GC, `weakref` for caches/observers,
  `__del__` pitfalls, context managers for cleanup.

---

## Module 12 — Common Mistakes & Misconceptions

- **Thinking `del x` frees memory directly** — it drops a reference; freeing happens
  at count 0.
- **Relying on `__del__`** for closing files/sockets.
- **Creating reference cycles unknowingly** (parent↔child, observers) — use
  `weakref` for back-references.
- **Assuming GC is purely tracing** (like Java) — CPython is refcount-first + cyclic
  GC.
- **Expecting `sys.getrefcount` to match your mental count** — it adds one for its own
  argument.
- **Copying an object that holds a connection/handle with `deepcopy`** — customise
  `__deepcopy__` to avoid duplicating non-copyable resources.

---

## Module 12 — MCQs (with answers & explanations)

**Q1.** CPython's primary memory-management mechanism is:
a) tracing GC only  b) **reference counting**  c) manual free()  d) arena allocation

<details><summary>Answer</summary>**b.** Reference counting, supplemented by a cyclic GC.</details>

**Q2.** A reference cycle is a problem because:
a) it's slow  b) **the objects' refcounts never reach 0**  c) it uses `__del__`  d) it's illegal

<details><summary>Answer</summary>**b.** Mutual references keep counts above 0; the cyclic GC handles it.</details>

**Q3.** `del x` primarily:
a) frees memory  b) **unbinds the name and decrements the refcount**  c) calls `__del__` always  d) collects cycles

<details><summary>Answer</summary>**b.** The object is freed only when the count hits 0.</details>

**Q4.** `__del__` is:
a) reliable cleanup  b) **non-deterministic; avoid for critical cleanup**  c) a constructor  d) required

<details><summary>Answer</summary>**b.** Timing is unpredictable; use context managers.</details>

**Q5.** A `weakref`:
a) increments refcount  b) **references without keeping the object alive**  c) prevents GC  d) copies the object

<details><summary>Answer</summary>**b.** It doesn't raise the count; the object can be collected.</details>

**Q6.** The best way to guarantee a file is closed:
a) `__del__`  b) **`with open(...)` / try-finally**  c) `gc.collect()`  d) hope

<details><summary>Answer</summary>**b.** Context managers give deterministic cleanup.</details>

**Q7.** `copy.deepcopy` uses `memo` to:
a) speed up  b) **avoid infinite recursion / duplicate copies on cycles**  c) log  d) skip fields

<details><summary>Answer</summary>**b.** `memo` caches already-copied objects.</details>

**Q8.** `WeakValueDictionary` is useful for:
a) permanent storage  b) **caches that auto-prune when values are unused**  c) ordering  d) hashing

<details><summary>Answer</summary>**b.** Entries disappear when their values are otherwise unreferenced.</details>

---

## Module 12 — Design/Practice Exercises (easy → hard)

1. **(easy)** Use `sys.getrefcount` to observe a count change across `b = a` and
   `del b`.
2. **(easy)** Create a two-object reference cycle and free it with `gc.collect()`.
3. **(medium)** Implement a context-manager `Resource` and prove cleanup runs even on
   exception.
4. **(medium)** Build a `weakref`-based cache; show entries vanish when the strong
   reference is dropped.
5. **(hard)** Write a `Node` tree where children hold **weak** back-references to
   parents to avoid cycles; verify no leak.
6. **(hard, interview)** Explain, with an example, why `__del__` is a poor cleanup
   mechanism and rewrite it as a context manager.

---

## Module 12 — Concept Review (one page)

Python objects are **created** (`__new__`/`__init__`), **used** while referenced, and
**destroyed** when unreachable. CPython's primary mechanism is **reference counting**:
each reference increments a count, each removal decrements it, and hitting **0** frees
the object **immediately**. Because refcounting can't reclaim **reference cycles**,
Python adds a **generational cyclic garbage collector** (`gc`). **`del x`** merely
unbinds a name and drops a reference — the object dies only at count 0. **`__del__`**
finalisers are **unreliable** (non-deterministic, may not run, swallow exceptions),
so use **context managers / `try-finally`** for resource cleanup. **`weakref`** refers
to objects **without** keeping them alive — ideal for caches (`WeakValueDictionary`)
and observer back-references, and for **breaking cycles**. Copying is customised via
**`__copy__`/`__deepcopy__`** (with `memo` guarding cycles).

---

## Module 12 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| CPython memory mechanism | reference counting + cyclic GC |
| Object freed when | refcount reaches 0 (or cyclic GC reclaims it) |
| Reference cycle | objects referencing each other; counts never hit 0 |
| Who frees cycles | the generational cyclic garbage collector (`gc`) |
| `del x` does | unbinds the name, decrements refcount |
| `__del__` reliability | non-deterministic; avoid for cleanup |
| Cleanup best practice | context manager / `try-finally` |
| `weakref` | reference that doesn't keep the object alive |
| Auto-pruning cache | `WeakValueDictionary` |
| Copy hooks | `__copy__` / `__deepcopy__` (memo for cycles) |
| `sys.getrefcount` quirk | reports +1 (its own argument) |
| Break a cycle | use a weak reference for the back-link |

---

## Module 12 — Pattern Recognition

- **See "memory grows over time in a long-running service"** → a leak: cycles or
  lingering references; consider `weakref`.
- **See "file/socket sometimes stays open"** → move cleanup from `__del__` to a
  context manager.
- **See parent↔child references** → weak back-reference to avoid a cycle.
- **See "cache that shouldn't keep objects alive"** → `WeakValueDictionary`.
- **See `deepcopy` duplicating a DB connection** → custom `__deepcopy__`.
- **See "why didn't my object get freed after `del`?"** → another reference exists.

---

## Module 12 — Revision Notes / Mini Cheat Sheet

```
LIFECYCLE: __new__ (allocate) -> __init__ (init) -> in use -> freed at refcount 0.
MEMORY = reference counting (immediate free at 0) + generational CYCLIC GC (gc module).

REFCOUNT: new ref ++ ; drop/rebind -- ; 0 -> freed now. sys.getrefcount reports +1.
CYCLE: A.b=B, B.a=A -> counts never 0 -> cyclic GC frees. gc.collect() to force.

del x = unbind NAME + decrement refcount (NOT destroy). Dies only if last ref.

__del__ finaliser: NON-deterministic, may not run at exit, swallows exceptions.
  -> DO NOT use for resource cleanup. Use 'with' / try-finally / close().

weakref.ref(obj) -> r(); does NOT keep obj alive; becomes None when obj dies.
  WeakValueDictionary/WeakKeyDictionary = auto-pruning caches; break cycles (observers).
COPY: copy.copy (shallow, __copy__) / copy.deepcopy (deep, __deepcopy__ + memo).
```

> **Next module:** **Module 13 — SOLID Principles.** We shift from *mechanics* to
> *design*: the five principles (Single Responsibility, Open/Closed, Liskov
> Substitution, Interface Segregation, Dependency Inversion) that turn working OOP
> into **maintainable** OOP — each with a Python before/after and the pillars we've
> built (abstraction, polymorphism, composition) put to work.

---

## Module 12 — Summary

Python manages object lifetimes with **reference counting** (freeing an object the
instant its count hits **0**) plus a **generational cyclic garbage collector** that
reclaims **reference cycles** refcounting can't. **`del x`** removes a name and
decrements a reference — it doesn't directly destroy anything. The **`__del__`**
finaliser is **unreliable** (unpredictable timing, possibly skipped, swallows
errors), so resource cleanup belongs in **context managers / `try-finally`**.
**`weakref`** lets you reference objects without keeping them alive — powering
non-leaking caches and observer back-references and helping break cycles — while
**`__copy__`/`__deepcopy__`** customise cloning. Understanding this keeps
long-running OOP systems leak-free and correct.

> **You have mastered this module when** you can: explain reference counting and the
> cyclic GC; state exactly what `del` does; list `__del__`'s pitfalls and replace it
> with a context manager; and use `weakref` to build a cache or break a cycle.
