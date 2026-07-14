---
title: "Module 8 — Descriptors, __slots__ & Attribute Access"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 8 — Descriptors, `__slots__` & Attribute Access

> **Why this module matters.**
> Module 7 showed dunders for *operations*. This module reveals the machinery under
> **attribute access itself** — the thing that happens every time you write
> `obj.x`. Understanding `__getattribute__`/`__getattr__` and the **descriptor
> protocol** is what turns `@property`, methods, `classmethod`, and `staticmethod`
> from magic into mechanism (they are *all* descriptors). It also unlocks reusable
> validation and, via **`__slots__`**, real memory/speed wins. This is
> senior/staff-level Python — a strong differentiator in interviews.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★       | ★           | ★★★★        | ★★★        |

**Most-asked concepts:** `__getattr__` vs `__getattribute__`; the **descriptor
protocol** (`__get__`/`__set__`/`__delete__`); **data vs non-data descriptors** and
precedence; "how does `@property` work?" (it's a data descriptor); `__slots__`
(memory savings + trade-offs); `__set_name__`.

**What you must be able to do after this module:** explain the full `obj.x` lookup
order; write `__getattr__` for defaults/proxies safely; implement a reusable
validator descriptor; explain why `@property` beats an instance attribute; and use
`__slots__` with awareness of its trade-offs.

---

## 8.1 Attribute Access Hooks

When you access `obj.x`, Python calls **`__getattribute__`** — *unconditionally, on
every access*. Only if that raises `AttributeError` does Python fall back to
**`__getattr__`** (if defined).

![obj.x always calls __getattribute__ first; if it succeeds you get the value, and only if it raises AttributeError does the __getattr__ fallback run.](images/m08_01_attr_hooks.png)

| Hook | When called | Typical use |
|---|---|---|
| `__getattribute__(self, name)` | **every** attribute read | rarely overridden (easy to break; recursion risk) |
| `__getattr__(self, name)` | only when normal lookup **fails** | defaults, lazy attributes, proxies |
| `__setattr__(self, name, value)` | every attribute **write** | validation, logging, read-only objects |
| `__delattr__(self, name)` | every `del obj.x` | guard deletions |

![__getattribute__ is called on every access (override with care — recursion risk); __getattr__ is called only when normal lookup fails (safe for defaults/proxies).](images/m08_02_getattr_vs_getattribute.png)

```python
class Config:
    def __init__(self): self._data = {"host": "localhost"}
    def __getattr__(self, name):          # only for MISSING attributes
        return self._data.get(name, "DEFAULT")

c = Config()
print(c.host)      # __getattribute__ finds nothing normal... wait:
print(c.port)      # 'DEFAULT'  -> __getattr__ fallback (port not a real attr)
```

> **Danger:** overriding `__getattribute__` naively causes infinite recursion
> (accessing `self.x` inside it re-triggers it). Always delegate to
> `super().__getattribute__(name)`. Prefer `__getattr__` unless you truly must
> intercept *every* access.

**`__setattr__` for validation** (note: also self-recursive — use
`super().__setattr__` or `self.__dict__`):

```python
class Frozen:
    def __init__(self, x): self.__dict__["x"] = x
    def __setattr__(self, name, value):
        raise AttributeError("immutable")   # read-only object
```

---

## 8.2 The Descriptor Protocol

A **descriptor** is an object (assigned as a **class attribute**) that defines one
or more of `__get__`, `__set__`, `__delete__`. When you access that attribute on an
instance, Python routes the access **through the descriptor's methods**.

![A descriptor placed as a class attribute defines __get__ (read), __set__ (write), and __delete__ (del), intercepting access to that attribute on instances.](images/m08_03_descriptor_protocol.png)

```python
class Descriptor:
    def __set_name__(self, owner, name):   # Python tells us the attr name (3.6+)
        self.name = "_" + name
    def __get__(self, obj, owner):
        if obj is None: return self         # accessed on the class, not instance
        return getattr(obj, self.name)
    def __set__(self, obj, value):
        setattr(obj, self.name, value)

class C:
    x = Descriptor()                        # descriptor lives on the CLASS
```

- `__get__(self, obj, owner)` — `obj` is the instance (or `None` if accessed on the
  class); `owner` is the class.
- `__set__(self, obj, value)` — intercepts assignment.
- `__set_name__(self, owner, name)` — called automatically at class creation with
  the attribute's name (so one descriptor knows where it lives).

---

## 8.3 Data vs Non-Data Descriptors (and precedence)

The **kind** of descriptor decides whether it beats the instance `__dict__`:

![Data descriptors define __get__ + __set__ (or __delete__) and WIN over the instance dict; non-data descriptors define __get__ only and are overridden by the instance dict.](images/m08_04_data_vs_nondata.png)

- **Data descriptor** = defines `__set__` (or `__delete__`). **Takes priority over
  the instance dict.** (`@property` is a data descriptor.)
- **Non-data descriptor** = defines only `__get__`. **The instance dict wins over
  it.** (A plain function/method is a non-data descriptor.)

The full **read precedence**:

![Read precedence: 1) data descriptor on the class, 2) instance __dict__, 3) non-data descriptor / class attribute, 4) __getattr__, 5) AttributeError.](images/m08_08_precedence.png)

```text
1. data descriptor found on the class      (e.g. @property)
2. instance __dict__                        (normal instance attribute)
3. non-data descriptor / plain class attr   (e.g. a method)
4. __getattr__ fallback
5. AttributeError
```

> **Why this matters:** it explains why you *can't* shadow a `@property` by setting
> an instance attribute of the same name (the data descriptor wins), but you *can*
> shadow a method by assigning an instance attribute (a non-data descriptor loses to
> the instance dict).

---

## 8.4 Everything Familiar Is a Descriptor

The features you already use are built on descriptors:

![property is a data descriptor; methods are non-data descriptors (functions); classmethod and staticmethod are descriptors; even super() uses descriptors.](images/m08_05_property_is_descriptor.png)

- **`@property`** → a **data descriptor** whose `__get__`/`__set__` call your
  getter/setter. That's *why* properties override instance attributes.
- **Methods** → functions are **non-data descriptors**; `obj.method` invokes the
  function's `__get__` to produce a **bound method** (binding `self`).
- **`classmethod` / `staticmethod`** → descriptors that adjust what gets passed
  (`cls` / nothing).

So Module 3's method binding (`acc.deposit` → bound) and Module 4's `@property` are
the *same* descriptor mechanism. Learn it once, understand all of them.

---

## 8.5 A Reusable Validator Descriptor (the killer use case)

Descriptors shine when the **same logic** (validation, type-checking, logging)
applies to **many attributes**. Write it once as a descriptor, reuse everywhere —
DRY, unlike repeating `@property` setters.

![One Positive descriptor is assigned to both price and weight on a Product class; its __set__ enforces value > 0 for every field, written once.](images/m08_06_validator_descriptor.png)

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name
    def __get__(self, obj, owner):
        if obj is None: return self
        return getattr(obj, self.name)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name[1:]} must be positive, got {value}")
        setattr(obj, self.name, value)

class Product:
    price  = Positive()          # same validation...
    weight = Positive()          # ...reused, zero duplication
    def __init__(self, price, weight):
        self.price = price       # goes through Positive.__set__
        self.weight = weight

p = Product(10, 2)
# Product(-5, 2)   -> ValueError: price must be positive, got -5
```

Compare: doing this with `@property` would need a **separate getter/setter pair per
field**. The descriptor collapses that into one class — this is the standard
"why descriptors?" interview answer.

---

## 8.6 `__slots__` — memory & speed

By default every instance has a `__dict__` (a full dict) for its attributes —
flexible but memory-heavy. **`__slots__`** replaces it with a fixed, array-like
layout: no per-instance `__dict__`, less memory, faster attribute access, and a
**locked set of allowed attributes**.

![Default instances carry a full __dict__ (flexible but heavier); __slots__ uses a compact fixed slot layout with no __dict__, cutting memory ~40-50%.](images/m08_07_slots_memory.png)

```python
class PointDict:                # default: has __dict__
    def __init__(self, x, y): self.x, self.y = x, y

class PointSlots:
    __slots__ = ("x", "y")      # no __dict__; only x and y allowed
    def __init__(self, x, y): self.x, self.y = x, y

p = PointSlots(1, 2)
# p.z = 3      -> AttributeError: 'PointSlots' object has no attribute 'z'
```

**Trade-offs:**

| Benefit | Cost |
|---|---|
| ~40–50% less memory per instance | can't add attributes not in `__slots__` |
| faster attribute get/set | no `__dict__` (some tools/pickling assume it) |
| accidental-attribute typos become errors | subclasses need their own `__slots__`, else `__dict__` returns |

> **When to use:** classes with **many instances** (millions of small objects — data
> points, tree nodes, game entities). For ordinary classes, the flexibility of
> `__dict__` usually wins; don't add `__slots__` reflexively.

---

## 8.7 Putting It Together — a lazy/cached property

A classic descriptor use: compute an expensive value once, then cache it. (`functools.cached_property` does this for you since 3.8.)

```python
class DataSet:
    def __init__(self, rows): self.rows = rows

    @property
    def total(self):                       # recomputed every access
        print("computing...")
        return sum(self.rows)

from functools import cached_property
class DataSet2:
    def __init__(self, rows): self.rows = rows
    @cached_property
    def total(self):                       # computed once, then stored in __dict__
        print("computing once")
        return sum(self.rows)

d = DataSet2([1, 2, 3])
d.total; d.total    # "computing once" prints only ONCE
```

`cached_property` is a **non-data descriptor**, so after the first access it stores
the result in the instance `__dict__`, which then wins on subsequent reads — a neat
demonstration of §8.3's precedence.

---

## Module 8 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "`__getattr__` vs `__getattribute__`?" | "Both get attrs." | "`__getattribute__` runs on **every** access (dangerous, recursion-prone); `__getattr__` runs **only on miss** (safe for defaults/proxies)." |
| "How does `@property` work?" | "Getter/setter." | "It's a **data descriptor**: its `__get__`/`__set__` call your methods; being a data descriptor is why it overrides instance attributes." |
| "Why use descriptors over properties?" | (unsure) | "To reuse the same access logic across many attributes without duplicating getter/setter pairs — one descriptor class, applied to many fields." |
| "What does `__slots__` do?" | "Saves memory." | "Removes per-instance `__dict__`, cutting memory ~40–50% and speeding access, at the cost of dynamic attributes and some tooling compatibility; use for many-instance classes." |

---

## Module 8 — Exam Mapping

- **GATE CS:** rarely deep here; attribute lookup order may appear.
- **SEBI / RBI IT:** minimal.
- **FAANG / senior backend:** descriptors, `@property` internals, `__slots__`
  trade-offs, and the lookup-precedence rules are strong signal questions.

---

## Module 8 — Common Mistakes & Misconceptions

- **Infinite recursion** in `__getattribute__`/`__setattr__` (accessing `self.x`
  re-triggers the hook) — delegate to `super()` or use `self.__dict__`.
- **Putting a descriptor on the instance** — descriptors only work as **class**
  attributes.
- **Expecting an instance attribute to shadow a `@property`** — it can't (data
  descriptor wins).
- **Adding `__slots__` but forgetting subclasses** — a subclass without its own
  `__slots__` regains a `__dict__`, erasing the savings.
- **Using `__slots__` on rarely-instantiated classes** — needless rigidity for no
  real gain.

---

## Module 8 — MCQs (with answers & explanations)

**Q1.** `__getattr__` is called:
a) on every access  b) **only when normal lookup fails**  c) on write  d) never

<details><summary>Answer</summary>**b.** It's the fallback; `__getattribute__` runs on every access.</details>

**Q2.** A data descriptor defines:
a) only `__get__`  b) **`__set__` (or `__delete__`), possibly with `__get__`**  c) `__call__`  d) `__slots__`

<details><summary>Answer</summary>**b.** Presence of `__set__`/`__delete__` makes it a data descriptor.</details>

**Q3.** Between a data descriptor and an instance attribute of the same name, the winner is:
a) instance attribute  b) **data descriptor**  c) whichever is newer  d) error

<details><summary>Answer</summary>**b.** Data descriptors take precedence over the instance `__dict__`.</details>

**Q4.** `@property` is implemented as a:
a) metaclass  b) function  c) **data descriptor**  d) mixin

<details><summary>Answer</summary>**c.** That's why it overrides instance attributes.</details>

**Q5.** `__slots__` primarily:
a) speeds imports  b) **removes the per-instance `__dict__` to save memory**  c) enforces types  d) enables inheritance

<details><summary>Answer</summary>**b.** Fixed layout, no `__dict__`; restricts attributes.</details>

**Q6.** Descriptors must be assigned as:
a) instance attributes  b) **class attributes**  c) globals  d) module functions

<details><summary>Answer</summary>**b.** The protocol triggers only for class-level descriptors.</details>

**Q7.** A plain method is a:
a) data descriptor  b) **non-data descriptor**  c) metaclass  d) property

<details><summary>Answer</summary>**b.** Functions define only `__get__` (binding `self`), so they are non-data.</details>

**Q8.** To avoid recursion when overriding `__setattr__`, use:
a) `self.x = v`  b) **`super().__setattr__` or `self.__dict__[name] = v`**  c) `setattr(self, ...)`  d) a global

<details><summary>Answer</summary>**b.** Direct dict access or the parent hook avoids re-triggering `__setattr__`.</details>

---

## Module 8 — Design/Practice Exercises (easy → hard)

1. **(easy)** Write a class whose `__getattr__` returns `"N/A"` for any missing
   attribute.
2. **(easy)** Add `__slots__` to a `Point` class and show that adding `p.z` fails.
3. **(medium)** Implement a `Typed` descriptor that enforces a given type on
   assignment; use it for `name: str` and `age: int`.
4. **(medium)** Implement a read-only object via `__setattr__` that blocks all
   writes after construction.
5. **(hard)** Write a `LoggedAccess` descriptor that prints every read/write, and
   attach it to two fields.
6. **(hard, interview)** Explain, with a demo, why an instance attribute can shadow
   a method but not a `@property`.

---

## Module 8 — Concept Review (one page)

Every `obj.x` read calls **`__getattribute__`** first; only on failure does
**`__getattr__`** run (safe for defaults/proxies). Writes go through
**`__setattr__`** (mind recursion — delegate to `super()`/`__dict__`). A
**descriptor** is a **class attribute** defining `__get__`/`__set__`/`__delete__`
that intercepts access; **`__set_name__`** tells it its attribute name.
**Data descriptors** (with `__set__`) **beat the instance `__dict__`**; **non-data
descriptors** (only `__get__`) lose to it — giving the precedence: **data descriptor
→ instance dict → non-data/class attr → `__getattr__` → AttributeError**.
`@property`, methods, `classmethod`, and `staticmethod` are **all descriptors**;
that's why `@property` overrides instance attributes and methods bind `self`.
Descriptors let you **reuse access logic across many fields** (validators),
something `@property` can't do without duplication. **`__slots__`** removes the
per-instance `__dict__` to cut memory (~40–50%) and speed access, at the cost of
dynamic attributes — ideal for many-instance classes.

---

## Module 8 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| `__getattribute__` runs when? | on every attribute read |
| `__getattr__` runs when? | only when normal lookup fails |
| Descriptor = | class attribute with `__get__`/`__set__`/`__delete__` |
| Data descriptor | has `__set__`/`__delete__`; beats instance dict |
| Non-data descriptor | only `__get__`; instance dict beats it |
| `@property` is a | data descriptor |
| Methods are | non-data descriptors (bind `self` via `__get__`) |
| Read precedence | data desc → instance dict → non-data/class → `__getattr__` → error |
| `__set_name__` gives | the attribute's name at class creation |
| `__slots__` does | removes `__dict__`, saves memory, locks attribute set |
| Descriptor over property when | same logic reused across many fields |
| `cached_property` is a | non-data descriptor (caches into instance dict) |

---

## Module 8 — Pattern Recognition

- **See "default value for any missing attribute / proxy object"** → `__getattr__`.
- **See "same validation on many fields"** → a reusable descriptor (not N properties).
- **See "instance attribute won't override my property"** → data-descriptor
  precedence.
- **See "millions of small objects, tight on RAM"** → `__slots__`.
- **See "compute once, cache"** → `functools.cached_property`.
- **See "read-only object"** → override `__setattr__` to block writes.

---

## Module 8 — Revision Notes / Mini Cheat Sheet

```
ACCESS HOOKS:
  __getattribute__  every read (careful: recursion -> use super())
  __getattr__       only on MISS (defaults, proxies, lazy)
  __setattr__       every write (validate/log; avoid recursion)

DESCRIPTOR = class attr with __get__/__set__/__delete__ (+ __set_name__).
  DATA descriptor  (__set__/__delete__)  -> beats instance __dict__
  NON-DATA (__get__ only)                -> instance __dict__ beats it
READ PRECEDENCE: data desc -> instance dict -> non-data/class attr -> __getattr__ -> error.

@property = data descriptor. methods = non-data descriptors. classmethod/staticmethod = descriptors.
USE descriptors to REUSE access logic across many fields (validators) — DRY vs many @property.

__slots__ = ('a','b'): no per-instance __dict__ -> ~40-50% less memory + faster,
  but no dynamic attrs; subclasses need own __slots__ or __dict__ returns.
functools.cached_property: compute once, cache into instance dict (non-data desc).
```

> **Next module:** **Module 9 — Metaclasses & Class Creation.** We climb one final
> level: if descriptors control attribute access, **metaclasses control class
> creation itself.** We'll see that classes are objects too (instances of `type`),
> how `type(name, bases, dict)` builds a class, `__new__`/`__init__` on metaclasses,
> `__init_subclass__`, and class decorators — plus when a metaclass is genuinely the
> right tool (and when it's overkill).

---

## Module 8 — Summary

Attribute access is not magic — it's a defined pipeline. Every read runs
**`__getattribute__`**, with **`__getattr__`** as a miss-only fallback; writes run
**`__setattr__`**. **Descriptors** — class attributes implementing
`__get__`/`__set__`/`__delete__` — sit at the heart of this pipeline and power
**`@property`, methods, `classmethod`, and `staticmethod`**. The **data vs non-data**
distinction sets the **lookup precedence** (data descriptor → instance dict →
non-data → `__getattr__`), explaining why properties override instance attributes
but methods don't. Descriptors let you **factor repeated access logic** (like
validation) into one reusable class, and **`__slots__`** trades dynamic attributes
for substantial **memory and speed** gains on high-instance-count classes. This is
the machinery beneath Python OOP.

> **You have mastered this module when** you can: state the full `obj.x` precedence;
> write safe `__getattr__`/`__setattr__`; implement a reusable validator descriptor;
> explain why `@property` overrides instance attributes; and weigh `__slots__`'
> trade-offs.
