---
title: "Module 2 — The Python Object Model"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — The Python Object Model

> **Why this module comes second.**
> Module 1 said "everything in Python is an object." This module makes that
> *precise* — because almost every confusing Python OOP bug traces back to one
> misunderstanding: **a variable is a name bound to an object, not a box that
> holds a value.** Once you see that, mutable-default-argument bugs, "why did my
> two lists change together?", `is` vs `==`, and copy semantics all become
> obvious instead of scary. This is the bedrock under every later feature.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★★     | ★★          | ★★★★★       | ★★★        |

**Most-asked concepts:** `is` vs `==`; **mutable vs immutable** types; the
**mutable default argument** trap; "is Python pass-by-value or pass-by-reference?";
shallow vs deep copy; why `a = b` on a list makes them change together; integer/
string interning; `id()` and `type()`.

**What you must be able to do after this module:** predict the output of any
aliasing/mutation snippet; explain "pass by object reference" with an example;
choose `is` vs `==` correctly; know which built-in types are mutable; and avoid
the mutable-default-argument bug on sight.

---

## 2.1 Names and Objects — the mental model that fixes everything

In many languages, `x = 5` means "the box called `x` now contains 5." **In Python
this model is wrong.** In Python, `5` is an **object** living in memory, and `x`
is a **name** (a label) **bound** to that object. Assignment binds a name to an
object; it never copies the object.

![Names live in a namespace and point to objects on the heap; x = 42 and y = x make both names reference one int object.](images/m02_01_name_vs_object.png)

```python
x = 42          # create int object 42; bind name x to it
y = x           # bind name y to the SAME object (no copy)
print(x is y)   # True  -> same object
```

> **The one sentence to memorise:** *"Variables are names bound to objects.
> Assignment binds; it does not copy."* Everything else in this module follows
> from this.

---

## 2.2 The Three Questions About Any Object: id, type, value

Every Python object answers three questions:

![An object answers three questions: id() gives identity, type() gives its class, and value is its contents.](images/m02_02_id_type_value.png)

| Question | Operator/function | Example |
|---|---|---|
| **Which object is it?** (identity) | `id(obj)` / `is` | `id(x)` → `140...` (unique while it lives) |
| **What kind is it?** (type) | `type(obj)` / `isinstance` | `type([1,2])` → `list` |
| **What are its contents?** (value) | `==`, printing | `[1,2] == [1,2]` → `True` |

```python
nums = [1, 2, 3]
print(id(nums))     # e.g. 140234567 — its identity (address-like)
print(type(nums))   # <class 'list'>
print(nums == [1, 2, 3])   # True — same value
print(nums is [1, 2, 3])   # False — different object with equal value
```

`id()` returns a unique integer for the object **for its lifetime** (in CPython,
the memory address). Two objects that are alive at the same time never share an
`id`; but an `id` *can* be reused after an object is garbage-collected.

---

## 2.3 Reference Semantics — why two names can change together

Because assignment binds (never copies), `b = a` makes `b` and `a` point at the
**same object**. If that object is **mutable**, a change through one name is
visible through the other.

![a = [10,20]; b = a binds both names to the same list, so a.append(30) is visible through b.](images/m02_03_assignment_reference.png)

```python
a = [10, 20]
b = a               # SAME list, not a copy
a.append(30)
print(b)            # [10, 20, 30]  <-- surprised beginners live here
print(a is b)       # True
```

To get an independent list, you must **explicitly copy** (see §2.8):

```python
b = a.copy()        # or list(a) or a[:]
a.append(99)
print(b)            # [10, 20, 30] — unaffected now
```

---

## 2.4 Mutable vs Immutable — the great divide

An object is **mutable** if its value can change *in place* (same `id` before and
after), and **immutable** if it cannot — any "change" actually creates a **new
object**.

![Immutable types (int, float, bool, str, tuple, frozenset, bytes) cannot change; mutable types (list, dict, set, bytearray, most custom objects) can change in place.](images/m02_04_mutable_immutable.png)

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool`, `complex` | `list` |
| `str`, `bytes` | `dict`, `set` |
| `tuple`, `frozenset` | `bytearray` |
| `None`, `range` | most **custom class instances** |

Watch immutability with `id()`:

```python
s = "hi"
print(id(s))
s += "!"            # does NOT edit "hi"; builds a NEW string "hi!"
print(id(s))        # different id — s was REBOUND to a new object

lst = [1]
print(id(lst))
lst.append(2)       # edits the SAME list in place
print(id(lst))      # same id — mutated, not rebound
```

> **Why it matters for OOP:** immutable objects are **safe to share** (no one can
> corrupt them) and are **hashable** (usable as dict keys / set members). Mutable
> objects are flexible but must be copied carefully and generally can't be dict
> keys. This drives design choices throughout the course (e.g. `__hash__` in M07).

---

## 2.5 `is` vs `==` — two different questions

- `==` asks **"do these have the same *value*?"** (calls `__eq__`, Module 7).
- `is` asks **"are these the *same object*?"** (compares `id`).

![Two separate lists [1,2] and [1,2]: a == b is True (same value) but a is b is False (different objects).](images/m02_05_is_vs_eq.png)

```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True  — equal values
print(a is b)   # False — different objects

x = a
print(x is a)   # True  — same object
```

**Rule of thumb:**

- Use `==` for **content comparison** (99% of the time).
- Use `is` **only** for **singletons** — especially `is None`, `is True`,
  `is False`. Never write `x == None`; write `x is None`.

```python
if result is None:      # correct, idiomatic, fast
    ...
```

---

## 2.6 Interning — why `is` on numbers/strings is a trap

CPython **caches** (interns) some immutable objects so they can be reused. Small
integers **-5 to 256** and many short string literals are pre-created and shared.

![Python pre-caches small ints so a=100 and b=100 share one object; but 1000 may not be cached, so 'is' is unreliable.](images/m02_06_interning.png)

```python
a = 100
b = 100
print(a is b)     # True  — 100 is in the cached range (-5..256)

a = 1000
b = 1000
print(a is b)     # often False — outside the cache; two objects
print(a == b)     # True — values are equal (what you actually meant)
```

> **Interview trap:** *"Why does `a is b` print `True` for 100 but `False` for
> 1000?"* Answer: **small-integer interning** — an implementation detail of
> CPython. **Never use `is` to compare numbers or strings for equality; use `==`.**

---

## 2.7 Argument Passing — "pass by object reference"

Python is neither classic "pass by value" (copy the value) nor "pass by reference"
(alias the variable). It is **pass by object reference** (a.k.a. "pass by
assignment"): the function parameter becomes a **new name bound to the same
object** the caller passed.

The consequence splits on *what you do inside*:

![Mutating the passed object (lst.append) changes the caller's object; rebinding the parameter (lst = [9]) only changes the local name.](images/m02_07_arg_passing.png)

```python
def mutate(lst):
    lst.append(99)      # MUTATES the shared object -> caller sees it

def rebind(lst):
    lst = [99]          # REBINDS the local name -> caller unaffected

data = [1, 2]
mutate(data);  print(data)   # [1, 2, 99]  <-- changed
rebind(data);  print(data)   # [1, 2, 99]  <-- unchanged by rebind
```

**Immutable arguments** (int, str, tuple) *look* pass-by-value because you can't
mutate them at all — any "change" rebinds the local name only.

### The infamous mutable default argument bug

```python
def add_item(item, bucket=[]):     # DANGER: default list created ONCE
    bucket.append(item)
    return bucket

print(add_item(1))   # [1]
print(add_item(2))   # [1, 2]   <-- SAME list reused across calls!
```

The default `[]` is evaluated **once**, when the function is defined, and shared by
every call. **Fix** with the `None` sentinel:

```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []                # fresh list each call
    bucket.append(item)
    return bucket
```

> This is one of the most common Python interview "gotchas" — and a real bug source
> in production code.

---

## 2.8 Copying — shallow vs deep

Because `b = a` shares the object, real copies are explicit. There are **two
depths**:

![Shallow copy duplicates the outer container but shares nested objects; deepcopy clones the entire object tree.](images/m02_08_shallow_vs_deep.png)

- **Shallow copy** — new outer object, but **nested objects are shared**.
  Made by `list(a)`, `a[:]`, `a.copy()`, `dict(a)`, `copy.copy(a)`.
- **Deep copy** — recursively clones everything. `copy.deepcopy(a)`.

```python
import copy
original = [[1, 2], [3, 4]]

shallow = copy.copy(original)      # or original[:]
shallow[0].append(99)
print(original)   # [[1, 2, 99], [3, 4]]  <-- inner list was SHARED!

deep = copy.deepcopy(original)
deep[0].append(7)
print(original)   # unchanged — deep clone is fully independent
```

> **Decision rule:** if your object contains **only immutables**, a shallow copy is
> enough. If it contains **nested mutables** you intend to modify independently,
> use `deepcopy`. Custom classes control copy behaviour via `__copy__` /
> `__deepcopy__` (Module 12).

---

## 2.9 `None`, Singletons, and Truthiness

- `None` is a **singleton** — exactly one `None` object exists; that's why
  `x is None` is correct and fast.
- `True`/`False` are also singletons (`is True` works, but usually test truthiness
  directly: `if flag:`).
- **Truthiness:** empty containers (`[]`, `{}`, `""`, `0`, `None`) are *falsy*;
  most other objects are *truthy*. Custom classes define this via `__bool__` /
  `__len__` (Module 7).

```python
if not items:        # Pythonic "is the list empty?"
    print("empty")
```

---

## 2.10 Namespaces & Scope (LEGB) — where names live

A **namespace** is a mapping from names to objects. Name lookups follow **LEGB**:

| Level | Meaning |
|---|---|
| **L**ocal | inside the current function |
| **E**nclosing | any outer (enclosing) function |
| **G**lobal | module top level |
| **B**uilt-in | Python's built-ins (`len`, `print`, …) |

```python
x = "global"
def outer():
    x = "enclosing"
    def inner():
        # reads x via LEGB: finds "enclosing"
        print(x)
    inner()
outer()             # enclosing
```

`global` and `nonlocal` let you *rebind* names in outer scopes (use sparingly —
they often signal that state wants to be an object attribute instead). Every object
also has its **own namespace**: `obj.__dict__` (Module 3/8).

---

## Module 2 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Is Python pass-by-value or reference?" | (often guesses) | "Neither — **pass by object reference**: the parameter is a new name bound to the same object. Mutating the object is visible to the caller; rebinding the parameter is not." + the mutate/rebind example. |
| "`is` vs `==`?" | "`is` is identity, `==` is equality." | Adds: `==` calls `__eq__`; `is` compares `id`; use `is` only for `None`/singletons; mentions interning trap. |
| "Why did my two lists change together?" | (stuck) | "`b = a` aliases one mutable object; use `.copy()`/`deepcopy` for independence." |
| "Mutable default argument?" | (surprised) | Explains default is evaluated once at def-time; fixes with `None` sentinel. |

---

## Module 2 — Exam Mapping

- **GATE CS:** output-prediction on aliasing/mutation; mutable vs immutable
  classification; scope/LEGB questions.
- **SEBI / RBI IT:** which types are mutable/immutable; `is` vs `==` basics.
- **FAANG:** the mutable-default bug, deep vs shallow copy in code, "pass by
  object reference" explained crisply, interning trivia.

---

## Module 2 — Common Mistakes & Misconceptions

- **"Variables hold values."** No — names are bound to objects.
- **Using `is` for value equality** (`x is 1000`, `s is "abc"`). Use `==`.
- **`x == None`.** Use `x is None`.
- **Expecting `b = a` to copy a list.** It aliases; copy explicitly.
- **Mutable default arguments.** Use the `None` sentinel.
- **Thinking `deepcopy` is always needed.** Only for nested mutables you'll modify.
- **"Tuples are always immutable, so a tuple is safe."** The *tuple* is immutable,
  but a tuple *of lists* still has mutable contents: `t = ([1],); t[0].append(2)`
  works.

---

## Module 2 — MCQs (with answers & explanations)

**Q1.** `a = [1,2]; b = a; a.append(3); print(b)` →
a) `[1,2]`  b) **`[1,2,3]`**  c) error  d) `[3]`

<details><summary>Answer</summary>**b.** `b = a` aliases the same list; the append is visible through both names.</details>

**Q2.** Which is immutable?
a) list  b) dict  c) set  d) **tuple**

<details><summary>Answer</summary>**d.** Tuples are immutable (though they may contain mutable elements).</details>

**Q3.** `x = 256; y = 256; print(x is y)` in CPython →
a) **True**  b) False  c) error  d) sometimes

<details><summary>Answer</summary>**a.** 256 is within the interned small-int range (-5..256), so both names share one object. (`257` would likely be `False`.)</details>

**Q4.** The correct None check is:
a) `x == None`  b) **`x is None`**  c) `x = None`  d) `None(x)`

<details><summary>Answer</summary>**b.** `None` is a singleton; identity check `is None` is correct and idiomatic.</details>

**Q5.** `def f(a=[]): a.append(1); return a`; calling `f()` twice returns:
a) `[1]` then `[1]`  b) **`[1]` then `[1,1]`**  c) error  d) `[]` then `[]`

<details><summary>Answer</summary>**b.** The default list is created once at def-time and shared across calls.</details>

**Q6.** After `import copy; b = copy.copy([[1],[2]])`, mutating `b[0]` affects the original because:
a) it's a deep copy  b) **shallow copy shares nested objects**  c) lists are immutable  d) it doesn't

<details><summary>Answer</summary>**b.** `copy.copy` is shallow; the inner lists are shared. Use `deepcopy` for independence.</details>

**Q7.** `id(x)` returns:
a) the value  b) the type  c) **a unique identifier (address in CPython) for the object's lifetime**  d) the hash

<details><summary>Answer</summary>**c.** It's the object's identity; unique among live objects (may be reused after GC).</details>

**Q8.** Name resolution order in Python is:
a) GLEB  b) **LEGB**  c) BEGL  d) ELGB

<details><summary>Answer</summary>**b.** Local → Enclosing → Global → Built-in.</details>

---

## Module 2 — Design/Practice Exercises (easy → hard)

1. **(easy)** Predict the output, then run it: `a=(1,2); b=a; print(a is b)`.
2. **(easy)** Classify as mutable/immutable: `str`, `list`, `tuple`, `dict`, `set`,
   `frozenset`, `int`.
3. **(medium)** Write `safe_append(item, bucket=None)` that never shares state
   across calls; prove it with two calls.
4. **(medium)** Given `grid = [[0]*3]*3`, explain why `grid[0][0] = 1` sets a whole
   column to 1, and fix the construction.
5. **(hard)** Implement a function that returns a truly independent copy of a
   `dict` mapping strings to lists; demonstrate shallow copy fails and deepcopy
   works.
6. **(hard, interview)** Explain to a Java developer why Python is "pass by object
   reference" using one mutate example and one rebind example.

---

## Module 2 — Concept Review (one page)

A Python **variable is a name bound to an object**; assignment **binds, never
copies**. Every object has **identity (`id`), type (`type`), and value**. `b = a`
makes both names reference **one** object, so mutating a **mutable** object is
visible through every alias. Types split into **immutable** (int, float, str,
tuple, frozenset, bytes — "change" makes a new object) and **mutable** (list,
dict, set, custom instances — edited in place). `==` compares **value**; `is`
compares **identity** — use `is` only for `None`/singletons, never for numbers or
strings (**interning** makes `is` unreliable there). Argument passing is **pass by
object reference**: mutate → caller sees it; rebind → caller doesn't; hence the
**mutable-default-argument** bug, fixed with a `None` sentinel. Copies are explicit
and come in **shallow** (shares nested objects) and **deep** (clones everything)
depths. Names resolve by **LEGB**.

---

## Module 2 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Variable in Python is… | a name bound to an object (not a box holding a value) |
| Three facets of an object | id (identity), type, value |
| `==` vs `is` | value equality vs same-object identity |
| When to use `is` | only for singletons: `is None`, `is True/False` |
| Mutable types | list, dict, set, bytearray, most custom objects |
| Immutable types | int, float, bool, str, bytes, tuple, frozenset |
| `b = a` on a list does what? | aliases the same list (no copy) |
| Fix mutable default arg | use `def f(x=None): x = x or []` (None sentinel) |
| Shallow vs deep copy | shallow shares nested objects; deep clones the tree |
| Why `100 is 100` but `1000 is 1000` may differ | small-int interning (-5..256) |
| Argument passing model | pass by object reference |
| Scope lookup order | LEGB |

---

## Module 2 — Pattern Recognition

- **See "two variables changed unexpectedly together"** → aliasing of a mutable;
  copy explicitly.
- **See a function with `=[]`, `={}`, or `=set()` default** → mutable-default bug;
  switch to `None`.
- **See `x == None` / `x is 5`** → wrong operator; use `is None` / `==` for values.
- **See nested lists/dicts being copied then mutated** → decide shallow vs deep.
- **See `[[0]*n]*m` grids** → all rows are the *same* list; build with a
  comprehension `[[0]*n for _ in range(m)]`.

---

## Module 2 — Revision Notes / Mini Cheat Sheet

```
VARIABLE = a NAME bound to an OBJECT. Assignment BINDS, never copies.
OBJECT   = id (identity) + type + value.

b = a         -> same object (alias). Mutating a mutable is seen via both.
== vs is      -> value equality vs same-object. Use 'is' ONLY for None/singletons.
INTERNING     -> ints -5..256 & some strings cached; NEVER use 'is' for num/str eq.

MUTABLE   : list, dict, set, bytearray, custom instances  (edit in place, id stays)
IMMUTABLE : int, float, bool, str, bytes, tuple, frozenset (change = NEW object)

ARG PASSING = pass by object reference:
   mutate(obj)  -> caller sees change      rebind(param) -> local only
MUTABLE DEFAULT BUG: def f(x=[]) shares one list -> use x=None sentinel.

COPY: shallow (copy()/[:]/list()) shares nested; deep (copy.deepcopy) clones all.
[[0]*n]*m  -> rows aliased! use [[0]*n for _ in range(m)].
SCOPE: LEGB (Local, Enclosing, Global, Built-in). global/nonlocal to rebind outer.
```

> **Next module:** **Module 3 — Classes & Objects (the mechanics).** Now that we
> understand names and objects, we build classes properly: `__init__` and `self`,
> **instance vs class attributes** (and the shared-mutable-class-attribute trap
> that reuses this module's aliasing idea), and **instance vs class vs static
> methods** — the everyday grammar of Python OOP.

---

## Module 2 — Summary

The Python object model rests on one idea: **a variable is a name bound to an
object; assignment binds, it never copies.** Every object has an **identity
(`id`)**, a **type**, and a **value**. Aliasing (`b = a`) means two names share one
object, so mutating a **mutable** object shows through all aliases — while
**immutable** objects (int, str, tuple, …) create a new object on any "change."
`==` compares value and `is` compares identity; use `is` only for singletons like
`None`, and never trust it for numbers/strings because of **interning**. Argument
passing is **pass by object reference**, which explains both in-place mutation
visibility and the classic **mutable-default-argument** bug. Real copies are
explicit and either **shallow** or **deep**. Master this and Python's OOP stops
surprising you.

> **You have mastered this module when** you can: predict any aliasing/mutation
> snippet's output; explain pass-by-object-reference with a mutate and a rebind
> example; pick `is` vs `==` correctly every time; list the mutable and immutable
> built-ins; and spot-and-fix the mutable-default-argument bug instantly.
