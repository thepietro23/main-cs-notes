---
title: "Module 7 — Dunder (Magic) Methods & the Data Model"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 7 — Dunder (Magic) Methods & the Data Model

> **Why this module matters.**
> This is where Python OOP becomes *magical*: **dunder methods** ("double
> underscore", also called *magic* or *special* methods) are the hooks that let
> **your** objects behave like built-ins — support `len()`, `+`, `[]`, `==`,
> iteration, `with`, and even being *called* like a function. Python's whole "data
> model" is: syntax and built-ins quietly delegate to dunders. Learn these and you
> can make objects that feel native — and you'll ace the very common interview
> task *"make this class support `==` / sorting / `in` / iteration."*

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★      | ★★          | ★★★★★       | ★★★★       |

**Most-asked concepts:** `__repr__` vs `__str__`; the **`__eq__`/`__hash__`
contract** (and why overriding `__eq__` alone makes objects unhashable);
comparison + `functools.total_ordering`; container protocol (`__len__`,
`__getitem__`); iterator protocol (`__iter__`/`__next__`); context managers
(`__enter__`/`__exit__`); `__call__`.

**What you must be able to do after this module:** implement `__repr__`,
`__eq__`+`__hash__`, ordering, container and iterator protocols, a context manager,
and a callable — correctly and idiomatically.

---

## 7.1 The Data Model — syntax delegates to dunders

Python's operators and built-ins are **syntactic sugar** over method calls. `len(x)`
calls `x.__len__()`; `x + y` calls `x.__add__(y)`; `x[i]` calls
`x.__getitem__(i)`. Implement the dunder, and the syntax "just works" for your type.

![Python syntax maps to dunder methods: len(x) -> x.__len__(), x+y -> x.__add__(y), x[i] -> x.__getitem__(i), print(x) -> x.__str__().](images/m07_01_data_model.png)

> **Mental model:** you don't call dunders directly (`x.__len__()`); you use the
> *syntax* (`len(x)`) and Python calls the dunder for you. Defining them makes your
> object a first-class citizen of the language.

---

## 7.2 `__repr__` vs `__str__` — always define `__repr__`

Both produce a string form of an object, for different audiences:

![__repr__ is for developers (unambiguous, e.g. Point(x=1, y=2)); __str__ is for users (readable, e.g. (1, 2)); str() falls back to repr().](images/m07_02_repr_vs_str.png)

- **`__repr__`** — **unambiguous**, for **developers/debugging**. Ideally looks like
  valid code to recreate the object. Used by the REPL, `repr()`, containers, and
  logging.
- **`__str__`** — **readable**, for **end users**. Used by `str()` and `print()`.

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Point(x={self.x}, y={self.y})"   # dev
    def __str__(self):  return f"({self.x}, {self.y})"            # user

p = Point(1, 2)
print(repr(p))   # Point(x=1, y=2)
print(str(p))    # (1, 2)
print(p)         # (1, 2)      -> print uses __str__
print([p])       # [Point(x=1, y=2)]  -> containers use __repr__
```

> **Rule:** **always** define `__repr__` (the debugging default). Define `__str__`
> only if a user-facing form differs. If `__str__` is missing, `str()` falls back to
> `__repr__` — so `__repr__` gives you both cheaply.

---

## 7.3 `__eq__` and `__hash__` — the contract you must not break

By default, `==` compares **identity** (like `is`). To compare by **value**, define
`__eq__`. But there's a **contract with `__hash__`**:

![The contract: if a == b then hash(a) == hash(b). Defining __eq__ without __hash__ makes the object unhashable — no dict keys or set members.](images/m07_03_eq_hash_contract.png)

**The rules:**

1. If `a == b` then `hash(a) == hash(b)` (equal objects **must** hash equal).
2. Unequal objects *may* share a hash (collisions are allowed).
3. **If you define `__eq__`, Python sets `__hash__ = None`** → the object becomes
   **unhashable** (can't be a dict key or set member) unless you also define
   `__hash__`.

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
    def __hash__(self):
        return hash((self.x, self.y))     # base it on the SAME fields as __eq__

a, b = Point(1, 2), Point(1, 2)
print(a == b)          # True
print(hash(a) == hash(b))  # True
s = {a, b}
print(len(s))          # 1  -> treated as equal, hashable
```

> **Interview trap:** *"You defined `__eq__` and now your objects can't go in a
> set — why?"* → "Defining `__eq__` drops the default `__hash__`; you must define
> `__hash__` (over the same fields) to keep it hashable — or the object is
> intentionally mutable and should stay unhashable." Only immutable-by-value objects
> should be hashable.

---

## 7.4 Comparison Operators & `@total_ordering`

Rich comparison dunders: `__lt__` (`<`), `__le__` (`<=`), `__gt__` (`>`),
`__ge__` (`>=`), `__eq__` (`==`), `__ne__` (`!=`). Defining these makes objects
**sortable** (`sorted()`, `min`, `max`).

![You write __eq__ and __lt__; the @total_ordering decorator derives <=, >, >=, != for free, reducing boilerplate.](images/m07_04_total_ordering.png)

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor): self.major, self.minor = major, minor
    def __eq__(self, o): return (self.major, self.minor) == (o.major, o.minor)
    def __lt__(self, o): return (self.major, self.minor) <  (o.major, o.minor)

print(Version(1, 2) < Version(1, 5))   # True
print(sorted([Version(2, 0), Version(1, 9)], key=lambda v: (v.major, v.minor)))
```

`@total_ordering` derives the remaining operators from `__eq__` + one of
(`__lt__`/`__le__`/`__gt__`/`__ge__`). It trades a little speed for a lot less
boilerplate.

---

## 7.5 Arithmetic Operators (and reflected/in-place variants)

`__add__` (`+`), `__sub__` (`-`), `__mul__` (`*`), `__truediv__` (`/`), etc. Two
important companions:

- **Reflected** (`__radd__`): used when the left operand doesn't know how to add the
  right — e.g. `3 + vector` tries `int.__add__` (fails) then `vector.__radd__(3)`.
- **In-place** (`__iadd__`): used by `+=` to mutate in place (falls back to
  `__add__` if absent).

```python
class Vector:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, o):  return Vector(self.x + o.x, self.y + o.y)
    def __mul__(self, k):  return Vector(self.x * k, self.y * k)   # scalar
    def __repr__(self):    return f"Vector({self.x}, {self.y})"

print(Vector(1, 2) + Vector(3, 4))   # Vector(4, 6)
print(Vector(1, 2) * 3)              # Vector(3, 6)
```

> Arithmetic dunders should usually **return a new object** (immutability-friendly),
> not mutate `self` — except `__iadd__` and friends, which may mutate.

---

## 7.6 Container Protocol — behave like a list/dict

![Container protocol: len(c) -> __len__, c[i] -> __getitem__, c[i]=v -> __setitem__, x in c -> __contains__.](images/m07_05_container_protocol.png)

```python
class Playlist:
    def __init__(self): self._songs = []
    def add(self, s):            self._songs.append(s)
    def __len__(self):           return len(self._songs)          # len(pl)
    def __getitem__(self, i):    return self._songs[i]            # pl[0], slicing, iteration!
    def __setitem__(self, i, v): self._songs[i] = v              # pl[0] = x
    def __contains__(self, s):   return s in self._songs         # x in pl

pl = Playlist(); pl.add("A"); pl.add("B")
print(len(pl), pl[0], "A" in pl)     # 2 A True
for song in pl:                       # __getitem__ alone enables iteration!
    print(song)
```

> **Bonus:** implementing just `__getitem__` (with integer indexing from 0) gives
> you iteration *and* `in` for free — Python falls back to it when `__iter__` is
> absent.

---

## 7.7 Iterator Protocol — power the `for` loop

A **for loop** calls `iter(obj)` (→ `__iter__`) to get an **iterator**, then calls
`next()` (→ `__next__`) repeatedly until `StopIteration` is raised.

![for x in obj calls __iter__() to get an iterator, then __next__() yields items until it raises StopIteration.](images/m07_06_iterator_protocol.png)

```python
class Countdown:
    def __init__(self, start): self.start = start
    def __iter__(self):                 # return an iterator (here, self)
        self.n = self.start
        return self
    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

for x in Countdown(3):
    print(x)         # 3, 2, 1
```

- **Iterable** = has `__iter__` (can produce an iterator). **Iterator** = has
  `__next__` (produces values, tracks position).
- For most cases a **generator** (`yield`) is simpler than a manual iterator:

```python
class Countdown:
    def __init__(self, start): self.start = start
    def __iter__(self):
        n = self.start
        while n > 0:
            yield n          # generator: __iter__/__next__ built for you
            n -= 1
```

---

## 7.8 Context Managers — `with` via `__enter__`/`__exit__`

A **context manager** guarantees setup and cleanup around a block, even if it
raises. The `with` statement calls `__enter__` on entry and `__exit__` on exit.

![with open(f) as fh runs __enter__ (acquire, e.g. open) before the body and __exit__ (release, e.g. close) after — __exit__ always runs, even on exceptions.](images/m07_07_context_manager.png)

```python
class Timer:
    def __enter__(self):
        import time; self.t0 = time.perf_counter()
        return self                       # value bound to 'as'
    def __exit__(self, exc_type, exc, tb):
        import time; self.elapsed = time.perf_counter() - self.t0
        print(f"took {self.elapsed:.4f}s")
        return False                      # False -> propagate any exception

with Timer():
    sum(range(1_000_000))                 # prints "took 0.02s" afterwards
```

- `__exit__(exc_type, exc, tb)` receives exception info (or three `None`s if the
  block succeeded). **Return `True`** to *suppress* the exception; **`False`/`None`**
  to let it propagate.
- The `contextlib.contextmanager` decorator turns a generator into a context
  manager, avoiding the class boilerplate.

---

## 7.9 `__call__` — make an instance behave like a function

Defining `__call__` lets you call an **instance** like a function while it keeps
**state** — a "function object."

![Adder(10) is an object; calling adder(5) runs __call__(self, 5) returning 15 — a callable that remembers state, used for decorators and ML layers.](images/m07_08_callable.png)

```python
class Adder:
    def __init__(self, base): self.base = base
    def __call__(self, x):    return self.base + x   # obj(x)

add10 = Adder(10)
print(add10(5))       # 15
print(callable(add10))# True
```

Used for stateful callbacks, class-based decorators, memoisers, and (in PyTorch)
`nn.Module` layers where `layer(x)` runs `forward`.

---

## 7.10 Other Useful Dunders (quick reference)

| Dunder | Triggered by | Purpose |
|---|---|---|
| `__bool__` / `__len__` | `if obj:` / `bool(obj)` | truthiness (len 0 → falsy) |
| `__format__` | `f"{obj:spec}"`, `format()` | custom formatting |
| `__getitem__` | `obj[k]`, slicing, iteration | indexing |
| `__contains__` | `x in obj` | membership |
| `__enter__`/`__exit__` | `with` | resource management |
| `__del__` | garbage collection | finaliser (Module 12) |
| `__getattr__`/`__setattr__` | missing/any attr access | dynamic attributes (Module 8) |

---

## Module 7 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "`__repr__` vs `__str__`?" | "repr for debug, str for print." | Adds: repr should be unambiguous/recreatable; str falls back to repr; containers use repr; always define repr. |
| "Why unhashable after `__eq__`?" | (stuck) | "Defining `__eq__` sets `__hash__=None`; must define `__hash__` over the same fields (only for value-immutable objects) to stay hashable." |
| "Make this class iterable?" | "Add a loop." | Implements `__iter__`/`__next__` (or a generator `__iter__`); notes `__getitem__` fallback. |
| "How does `with` guarantee cleanup?" | "It closes files." | "`__enter__`/`__exit__`; `__exit__` runs even on exception; return True to suppress." |

---

## Module 7 — Exam Mapping

- **GATE CS:** operator overloading via dunders; iterator vs iterable; special
  methods triggered by syntax.
- **SEBI / RBI IT:** basic magic-method definitions; `__init__`/`__str__`.
- **FAANG:** implement `__eq__`+`__hash__`, ordering, containers, context managers
  in live code; the hashability contract.

---

## Module 7 — Common Mistakes & Misconceptions

- **Only defining `__eq__`** → object becomes unhashable; add `__hash__`.
- **Making a mutable object hashable** with a hash over mutable fields → breaks sets/
  dicts when it changes. Hash only value-immutable objects.
- **Skipping `__repr__`** → unhelpful `<obj at 0x...>` in logs/debuggers.
- **Calling dunders directly** (`x.__len__()`) instead of `len(x)`.
- **Returning nothing from arithmetic dunders** or mutating `self` in `__add__`.
- **`__exit__` accidentally returning `True`** → silently swallows exceptions.

---

## Module 7 — MCQs (with answers & explanations)

**Q1.** `len(x)` calls:
a) `x.length()`  b) **`x.__len__()`**  c) `x.size()`  d) `len.__call__(x)`

<details><summary>Answer</summary>**b.** Built-ins delegate to dunders.</details>

**Q2.** Defining `__eq__` without `__hash__` makes the object:
a) faster  b) immutable  c) **unhashable**  d) iterable

<details><summary>Answer</summary>**c.** Python sets `__hash__ = None`; add `__hash__` to keep hashability.</details>

**Q3.** Which is used by the REPL/containers to show an object?
a) `__str__`  b) **`__repr__`**  c) `__format__`  d) `__show__`

<details><summary>Answer</summary>**b.** Containers and the REPL use `__repr__`.</details>

**Q4.** A `for` loop first calls:
a) `__next__`  b) **`__iter__`**  c) `__len__`  d) `__getitem__`

<details><summary>Answer</summary>**b.** It obtains an iterator via `__iter__`, then calls `__next__`.</details>

**Q5.** `__next__` signals the end of iteration by:
a) returning None  b) returning -1  c) **raising StopIteration**  d) returning False

<details><summary>Answer</summary>**c.** `StopIteration` ends the loop.</details>

**Q6.** In a context manager, `__exit__` returning `True`:
a) re-raises  b) **suppresses the exception**  c) closes twice  d) is illegal

<details><summary>Answer</summary>**b.** Truthy return suppresses the propagating exception.</details>

**Q7.** `@total_ordering` requires you to define:
a) all six operators  b) **`__eq__` and one ordering method**  c) only `__lt__`  d) `__cmp__`

<details><summary>Answer</summary>**b.** `__eq__` plus one of `__lt__/__le__/__gt__/__ge__`.</details>

**Q8.** `__call__` lets you:
a) delete an object  b) **call an instance like a function**  c) compare objects  d) hash an object

<details><summary>Answer</summary>**b.** `obj(args)` runs `obj.__call__(args)`.</details>

---

## Module 7 — Design/Practice Exercises (easy → hard)

1. **(easy)** Add `__repr__` and `__str__` to a `Point` class with distinct outputs.
2. **(easy)** Make `Point` support `==` and be usable in a `set` (add `__hash__`).
3. **(medium)** Use `@total_ordering` to make a `Card` class fully comparable from
   `__eq__` + `__lt__`.
4. **(medium)** Implement a `Matrix` supporting `m[i, j]` via `__getitem__` and
   `len(m)`.
5. **(hard)** Write a `FileLines` iterable that yields lines, plus a `Timer` context
   manager; combine them.
6. **(hard, interview)** Build a `Money` class with `+`, `-`, `==`, `<`, `__hash__`,
   `__repr__`, and rejection of adding different currencies.

---

## Module 7 — Concept Review (one page)

Python's **data model** routes syntax and built-ins to **dunder methods**, letting
your objects act like natives. Always define **`__repr__`** (unambiguous, dev-facing;
the fallback for `str`), and **`__str__`** only when a user-facing form differs.
Override **`__eq__`** for value equality — but then you **must** define **`__hash__`**
(over the same fields, for value-immutable objects) or the object becomes
**unhashable**. Comparison dunders make objects sortable; **`@total_ordering`**
derives the rest from `__eq__` + one ordering. **Arithmetic** dunders (`__add__`,
reflected `__radd__`, in-place `__iadd__`) implement operators. The **container
protocol** (`__len__`, `__getitem__`, `__setitem__`, `__contains__`) makes objects
list/dict-like; the **iterator protocol** (`__iter__`/`__next__`, or a generator)
powers `for`; **context managers** (`__enter__`/`__exit__`) guarantee cleanup; and
**`__call__`** makes instances callable.

---

## Module 7 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| `len(x)` really calls | `x.__len__()` |
| `__repr__` vs `__str__` | dev/unambiguous vs user/readable; str falls back to repr |
| Always define which? | `__repr__` |
| Override `__eq__` → must also | define `__hash__` (or object is unhashable) |
| Hash contract | `a == b` ⇒ `hash(a) == hash(b)` |
| Make objects sortable | comparison dunders (`__lt__`, …) |
| `@total_ordering` needs | `__eq__` + one ordering method |
| `+` custom / reflected / in-place | `__add__` / `__radd__` / `__iadd__` |
| Iterable vs iterator | has `__iter__` vs has `__next__` |
| End iteration by | raising `StopIteration` |
| `with` uses | `__enter__` / `__exit__` (exit always runs) |
| Callable instance | define `__call__` |

---

## Module 7 — Pattern Recognition

- **See "objects print as `<X at 0x..>`"** → add `__repr__`.
- **See "can't put my objects in a set/dict"** → add `__hash__` (with `__eq__`).
- **See "need to sort my objects"** → comparison dunders / `@total_ordering`.
- **See "want `obj[i]` / `for x in obj` / `x in obj`"** → container/iterator
  protocol.
- **See "acquire then always release a resource"** → context manager.
- **See "a stateful thing that's called repeatedly"** → `__call__`.

---

## Module 7 — Revision Notes / Mini Cheat Sheet

```
DATA MODEL: syntax -> dunders. len(x)->__len__, x+y->__add__, x[i]->__getitem__.
Don't call dunders directly; use the syntax.

__repr__  dev, unambiguous, recreatable  (ALWAYS define; str() falls back to it)
__str__   user, readable                 (define only if different)

__eq__ (value ==). DEFINE __eq__ => also define __hash__ (same fields) or UNHASHABLE.
  contract: a==b => hash(a)==hash(b). Hash only value-immutable objects.

ORDERING: __lt__ __le__ __gt__ __ge__ __ne__.  @total_ordering: __eq__ + 1 ordering.
ARITH: __add__/__sub__/__mul__/__truediv__ ; reflected __radd__ ; in-place __iadd__.

CONTAINER: __len__ __getitem__ __setitem__ __contains__  (getitem alone -> iterate + in)
ITERATOR: __iter__ (returns iterator) + __next__ (StopIteration to end); or generator.
CONTEXT MGR: __enter__ (setup, returns 'as' val) / __exit__ (cleanup, ALWAYS runs;
             return True to suppress exception). contextlib.contextmanager for gens.
CALLABLE: __call__ -> obj(args). __bool__/__len__ -> truthiness.
```

> **Next module:** **Module 8 — Descriptors, `__slots__` & Attribute Access.** We go
> one level deeper than dunders into *how attribute access itself works*:
> `__getattr__`/`__getattribute__`/`__setattr__`, the **descriptor protocol** (what
> actually powers `@property`, methods, and `classmethod`), and **`__slots__`** for
> memory savings and locked attribute sets.

---

## Module 7 — Summary

**Dunder methods** are the hooks of Python's **data model**: implement them and your
objects support the language's syntax and built-ins natively. Define **`__repr__`**
always (and `__str__` when a user form differs); override **`__eq__`** together with
**`__hash__`** to preserve the hashability **contract**; add comparison dunders (or
**`@total_ordering`**) for sorting, and arithmetic dunders (with reflected/in-place
variants) for operators. The **container** and **iterator** protocols make objects
behave like lists/dicts and drive `for` loops; **context managers**
(`__enter__`/`__exit__`) guarantee cleanup; and **`__call__`** turns instances into
stateful callables. Together these let you build objects that feel exactly like
Python's own.

> **You have mastered this module when** you can: implement `__repr__`,
> `__eq__`+`__hash__`, ordering, the container and iterator protocols, a context
> manager, and `__call__` correctly — and explain the hashability contract and the
> repr/str fallback from memory.
