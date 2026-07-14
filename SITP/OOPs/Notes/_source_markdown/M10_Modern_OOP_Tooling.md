---
title: "Module 10 — Modern Python OOP Tooling (dataclasses, NamedTuple, Enum)"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 10 — Modern Python OOP Tooling

> **Why this module matters.**
> Modules 7–9 explained the *machinery*. This module is the **payoff**: the tools
> that let you write real-world classes with almost **zero boilerplate**. Instead of
> hand-writing `__init__`, `__repr__`, and `__eq__` for the hundredth time, you
> declare typed fields and let **`@dataclass`** generate them. You'll also meet
> **`NamedTuple`** (immutable records), **`Enum`** (named constants instead of magic
> numbers), and the third-party **`attrs`**. These are what modern Python code
> *actually looks like* — and interviewers expect you to reach for them.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★       | ★           | ★★★★★       | ★★★★       |

**Most-asked concepts:** what `@dataclass` generates; `field(default_factory=...)`
(the mutable-default fix); `frozen=True` (immutable + hashable); `__post_init__`;
`NamedTuple` vs `dataclass`; `Enum` for constants; when to use which.

**What you must be able to do after this module:** replace a boilerplate class with a
`@dataclass`; safely give a field a mutable default; make a frozen (value-object)
dataclass; define an `Enum`; and choose between dataclass / NamedTuple / Enum /
plain class for a given need.

---

## 10.1 The Boilerplate Problem `@dataclass` Solves

A simple "record" class by hand needs `__init__`, `__repr__`, and `__eq__` — a dozen
lines of repetitive, error-prone code:

![By hand a record class needs __init__, __repr__, __eq__ (15+ lines, error-prone); @dataclass reduces it to 3 lines of typed fields with everything generated.](images/m10_01_before_after.png)

```python
# By hand (verbose, easy to get __eq__/__repr__ wrong)
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Point(x={self.x}, y={self.y})"
    def __eq__(self, o): return isinstance(o, Point) and (self.x, self.y) == (o.x, o.y)

# With @dataclass (declarative, generated)
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

Both give the same behaviour — but the dataclass is 3 lines and can't drift out of
sync.

---

## 10.2 What `@dataclass` Generates

The decorator reads the **type-annotated class attributes** as **fields** and writes
the dunders:

![From @dataclass class Point with x:int, y:int, Python generates __init__(self, x, y), __repr__ -> Point(x=1, y=2), __eq__ comparing fields, and optionally __lt__, __hash__, __slots__.](images/m10_02_dataclass_generated.png)

```python
@dataclass
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)              # Point(x=1, y=2)      <- generated __repr__
print(p == Point(1, 2))  # True             <- generated __eq__
```

- **Fields** come from class-level **type annotations** (`x: int`). An attribute
  without an annotation is *not* a field.
- Defaults work like function defaults: `y: int = 0`. **Non-default fields cannot
  follow default fields** (same rule as function parameters).

---

## 10.3 `field()` and Decorator Options

![dataclass options: default_factory=list (fresh list per instance), frozen=True (immutable+hashable), order=True (adds comparisons), field(compare=False) (exclude a field from ==/order).](images/m10_03_field_options.png)

### The mutable-default fix: `default_factory`

Recall Module 2's mutable-default bug. A dataclass field **forbids** a mutable
default directly and makes you use `default_factory`:

```python
from dataclasses import dataclass, field

@dataclass
class Cart:
    items: list = field(default_factory=list)   # fresh list PER instance
    # items: list = []      # ValueError: mutable default not allowed

a, b = Cart(), Cart()
a.items.append("apple")
print(b.items)               # []  -> independent, bug avoided by design
```

### Decorator options

| Option | Effect |
|---|---|
| `frozen=True` | immutable instances + generates `__hash__` |
| `order=True` | generates `__lt__/__le__/__gt__/__ge__` (sortable by field tuple) |
| `eq=True` (default) | generates `__eq__` |
| `slots=True` (3.10+) | uses `__slots__` (memory savings, Module 8) |
| `kw_only=True` (3.10+) | all fields keyword-only |

### Per-field control with `field()`

```python
@dataclass
class User:
    name: str
    password: str = field(repr=False)          # hide from __repr__
    id: int = field(compare=False, default=0)  # exclude from ==/order
    tags: list = field(default_factory=list)
```

---

## 10.4 `__post_init__` — derived fields & validation

The generated `__init__` only assigns fields. For **computed values** or
**validation**, define `__post_init__`, which runs immediately after:

![__post_init__ runs right after the generated __init__ set x and y, letting you compute a derived distance field or validate cross-field constraints.](images/m10_04_post_init.png)

```python
from dataclasses import dataclass, field
import math

@dataclass
class Vector:
    x: float
    y: float
    magnitude: float = field(init=False)     # not a constructor argument
    def __post_init__(self):
        if self.x == self.y == 0:
            raise ValueError("zero vector not allowed")   # validation
        self.magnitude = math.hypot(self.x, self.y)       # derived field

v = Vector(3, 4)
print(v.magnitude)      # 5.0
```

`field(init=False)` keeps `magnitude` out of the constructor signature; you compute
it in `__post_init__`.

---

## 10.5 `NamedTuple` — immutable records

A `NamedTuple` is a **tuple with named fields**: immutable, hashable, memory-light,
and both **name- and index-accessible**.

![Point defined as a NamedTuple supports both named access (p.x, p.y) and tuple access (p[0], p[1]); it is immutable, hashable, and memory-light.](images/m10_05_namedtuple.png)

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

p = Point(1, 2)
print(p.x, p[0])        # 1 1  -> named AND indexed access
print(p == Point(1, 2)) # True
# p.x = 9               # AttributeError: immutable
a, b = p                # unpacks like a tuple
```

**`dataclass` vs `NamedTuple`:**

| | `@dataclass` | `NamedTuple` |
|---|---|---|
| Mutable? | yes (unless `frozen=True`) | **no** (always immutable) |
| Base | plain object | **tuple** (indexable, unpackable) |
| Methods | easy to add | can add, but tuple semantics |
| Memory | normal (or `slots=True`) | very small |
| Use when | a record you may mutate / add behaviour | a fixed, immutable value/record |

---

## 10.6 `Enum` — named constants (no magic values)

An **`Enum`** defines a fixed set of **named, singleton** constants — replacing
error-prone "magic numbers/strings".

![A Color Enum with RED=1, GREEN=2, BLUE=3: each member is a unique singleton, readable and comparable, used instead of magic numbers or strings.](images/m10_06_enum.png)

```python
from enum import Enum, auto

class Status(Enum):
    PENDING  = auto()      # auto-numbered 1, 2, 3...
    ACTIVE   = auto()
    CLOSED   = auto()

print(Status.ACTIVE)        # Status.ACTIVE
print(Status.ACTIVE.name)   # 'ACTIVE'
print(Status.ACTIVE.value)  # 2
print(Status.ACTIVE is Status.ACTIVE)   # True (singletons)

def handle(s: Status):      # type-safe, self-documenting
    if s is Status.CLOSED:
        ...
```

Variants: **`IntEnum`** (members are ints, comparable to ints), **`Flag`/`IntFlag`**
(bitwise-combinable), and **`StrEnum`** (3.11+, string members). Enums prevent bugs
like passing `"activ"` (typo) or `2` (meaningless) where a status is expected.

---

## 10.7 Frozen Dataclasses = Value Objects

![frozen=True makes a dataclass immutable and hashable: it can be used as a dict key or set member, and attribute writes (p.x = 5) raise FrozenInstanceError.](images/m10_07_frozen_hashable.png)

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

m = Money(100, "INR")
# m.amount = 200        # dataclasses.FrozenInstanceError
d = {m: "receipt"}       # hashable -> usable as a dict key / set member
```

Frozen dataclasses model **value objects** (Module 17): identity is defined by
value, they're safe to share, and they're hashable — the dataclass analogue of a
`NamedTuple` but with `object` semantics and easy method addition.

> **`attrs`:** the third-party library `attrs` inspired dataclasses and offers more
> (converters, richer validators, `__slots__` by default). Use `@dataclass` for the
> standard-library default; reach for `attrs` when you need its extra power.

---

## 10.8 Which Tool When?

![Decision: @dataclass for a mutable record with methods; NamedTuple for an immutable tuple-like record; Enum for a fixed set of named constants; a plain class for rich behaviour or complex logic.](images/m10_08_when_which.png)

| Need | Use |
|---|---|
| A record you'll mutate, maybe with methods | **`@dataclass`** |
| An immutable record, tuple-like, tiny | **`NamedTuple`** (or `frozen` dataclass) |
| A fixed set of named constants | **`Enum`** |
| A value object (hashable, immutable) | **`@dataclass(frozen=True)`** |
| Rich behaviour, complex invariants, inheritance-heavy | **plain class** |
| Millions of instances, memory-critical | dataclass with `slots=True` / `NamedTuple` |

---

## Module 10 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "What does `@dataclass` do?" | "Auto `__init__`." | "Generates `__init__`, `__repr__`, `__eq__` (and optionally ordering/hash/slots) from typed fields; reduces boilerplate and drift." |
| "Mutable default in a dataclass?" | (bug) | "Not allowed directly — use `field(default_factory=list)` for a fresh value per instance (fixes the shared-default bug)." |
| "`dataclass` vs `NamedTuple`?" | "Both hold data." | "NamedTuple is an immutable tuple subclass (indexable, unpackable, tiny); dataclass is a mutable object (unless frozen) with easy methods; pick by mutability/behaviour." |
| "Why `Enum`?" | "Constants." | "Named singletons instead of magic values — type-safe, self-documenting, comparable by identity." |

---

## Module 10 — Exam Mapping

- **GATE CS:** minimal (library feature).
- **SEBI / RBI IT:** minimal.
- **FAANG / backend:** expected fluency — refactor to dataclasses, know
  `default_factory`/`frozen`/`__post_init__`, choose the right container, use enums
  over magic values.

---

## Module 10 — Common Mistakes & Misconceptions

- **Mutable default without `default_factory`** — raises at class definition (good!);
  always use the factory.
- **Missing type annotation** on a field — it won't become a dataclass field.
- **A non-default field after a default field** — `TypeError` (parameter-order rule).
- **Expecting `NamedTuple` to be mutable** — it never is.
- **Using magic numbers/strings** where an `Enum` belongs.
- **Comparing `Enum` members with `==` to raw values** — use `is`/the member (unless
  `IntEnum`).
- **Making a mutable dataclass hashable** — only `frozen=True` gives a safe hash.

---

## Module 10 — MCQs (with answers & explanations)

**Q1.** `@dataclass` automatically generates:
a) only `__init__`  b) **`__init__`, `__repr__`, `__eq__`**  c) `__hash__` always  d) nothing

<details><summary>Answer</summary>**b.** Plus optional ordering/hash/slots via options.</details>

**Q2.** The correct way to default a list field:
a) `items: list = []`  b) **`items: list = field(default_factory=list)`**  c) `items = []`  d) `items: list = None`

<details><summary>Answer</summary>**b.** `default_factory` creates a fresh list per instance; a literal `[]` is rejected.</details>

**Q3.** `@dataclass(frozen=True)` makes instances:
a) faster only  b) **immutable and hashable**  c) mutable  d) abstract

<details><summary>Answer</summary>**b.** Writes raise `FrozenInstanceError`; a `__hash__` is generated.</details>

**Q4.** A `NamedTuple` is:
a) mutable  b) a dict  c) **an immutable tuple subclass with named fields**  d) a metaclass

<details><summary>Answer</summary>**c.** Immutable, indexable, unpackable, and name-accessible.</details>

**Q5.** `__post_init__` is used to:
a) replace `__init__`  b) **run validation / compute derived fields after init**  c) delete fields  d) serialize

<details><summary>Answer</summary>**b.** It runs right after the generated `__init__`.</details>

**Q6.** Best replacement for magic strings like `"pending"`, `"active"`:
a) constants module  b) **an `Enum`**  c) a dict  d) a list

<details><summary>Answer</summary>**b.** Enums give named, type-safe singletons.</details>

**Q7.** `field(compare=False)` on `id` means:
a) id is hidden from repr  b) **id is excluded from `__eq__`/ordering**  c) id is required  d) id is frozen

<details><summary>Answer</summary>**b.** The field won't participate in equality/comparison.</details>

**Q8.** For millions of small records, memory-critical, choose:
a) plain class with `__dict__`  b) **dataclass with `slots=True` or NamedTuple**  c) dict of dicts  d) list of lists

<details><summary>Answer</summary>**b.** Slots/NamedTuple avoid per-instance `__dict__`.</details>

---

## Module 10 — Design/Practice Exercises (easy → hard)

1. **(easy)** Rewrite a hand-written `Point` class as a `@dataclass`.
2. **(easy)** Add a safely-defaulted `tags: list` field using `default_factory`.
3. **(medium)** Make a `frozen` `Money` dataclass usable as a dict key; add a method
   that returns a new `Money` with a different amount.
4. **(medium)** Add `__post_init__` validation to reject negative prices.
5. **(hard)** Model a card game: a `Suit`/`Rank` `Enum`, a frozen `Card` dataclass,
   and a mutable `Deck` dataclass; make cards hashable and sortable.
6. **(hard, interview)** Given a class using magic status strings and manual dunders,
   refactor it to dataclass + Enum and explain each improvement.

---

## Module 10 — Concept Review (one page)

Modern Python replaces record boilerplate with declarative tools. **`@dataclass`**
reads **type-annotated fields** and generates `__init__`, `__repr__`, and `__eq__`
(plus optional ordering, hashing, and `__slots__`), keeping code short and in sync.
Mutable defaults are handled safely with **`field(default_factory=...)`**, and
**`__post_init__`** adds validation/derived fields. **`frozen=True`** yields
immutable, hashable **value objects**. **`NamedTuple`** is an immutable, tuple-based
record (indexable, unpackable, tiny); **`Enum`** provides named singleton constants
that eliminate magic values. Choose **dataclass** for mutable records, **NamedTuple**
or **frozen dataclass** for immutable ones, **Enum** for constant sets, and a
**plain class** for rich behaviour — all built atop the descriptor/decorator/
metaclass machinery of Modules 8–9.

---

## Module 10 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| `@dataclass` generates | `__init__`, `__repr__`, `__eq__` (opt: order/hash/slots) |
| Fields come from | type-annotated class attributes |
| Mutable default fix | `field(default_factory=list)` |
| Immutable + hashable dataclass | `@dataclass(frozen=True)` |
| Post-construction hook | `__post_init__` |
| Exclude field from `__init__` | `field(init=False)` |
| NamedTuple is | immutable tuple subclass with named fields |
| dataclass vs NamedTuple | mutable object vs immutable tuple |
| Enum gives | named singleton constants (no magic values) |
| Auto-number enum members | `auto()` |
| Memory-critical records | `slots=True` dataclass / NamedTuple |
| `attrs` is | third-party lib that inspired dataclasses (more features) |

---

## Module 10 — Pattern Recognition

- **See a class that's "just data" with manual dunders** → `@dataclass`.
- **See `= []`/`= {}` as a field default** → `field(default_factory=...)`.
- **See "must be immutable / hashable / dict key"** → `frozen=True` or `NamedTuple`.
- **See magic numbers/strings for a fixed set** → `Enum`.
- **See "compute a field from others at construction"** → `__post_init__`.
- **See millions of tiny records** → `slots=True` / `NamedTuple`.

---

## Module 10 — Revision Notes / Mini Cheat Sheet

```
@dataclass: typed fields -> auto __init__/__repr__/__eq__.
  y: int = 0            default (non-default cannot follow default)
  field(default_factory=list)   fresh mutable default (fixes shared-default bug)
  field(init=False / repr=False / compare=False)   per-field control
OPTIONS: frozen=True (immutable+hashable), order=True (comparisons),
         slots=True (3.10, memory), kw_only=True (3.10).
__post_init__: validation + derived fields after generated __init__.

NamedTuple (typing): immutable tuple subclass; p.x AND p[0]; tiny; unpackable.
Enum: named singleton constants. .name/.value; auto(); IntEnum/Flag/StrEnum.
  use instead of magic numbers/strings; compare by identity (is).

CHOOSE: dataclass(mutable record) | NamedTuple/frozen(immutable) |
        Enum(constants) | plain class(rich behaviour) | slots/NT(memory).
attrs = 3rd-party, richer superset that inspired dataclasses.
```

> **Next module:** **Module 11 — Object Typing & Protocols.** We add *type safety*
> to our objects: type hints, **Generics** (`list[T]`, `TypeVar`), and **`Protocol`**
> — structural typing that formalises duck typing so tools like `mypy` can check
> "has the right methods" without inheritance. Dataclasses and Protocols together are
> how modern typed Python OOP is written.

---

## Module 10 — Summary

Modern Python OOP is **declarative**: **`@dataclass`** turns type-annotated fields
into a full record class — generating `__init__`, `__repr__`, and `__eq__`, with
options for **ordering, `frozen` immutability/hashability, and `__slots__`** — while
**`field(default_factory=...)`** safely handles mutable defaults and
**`__post_init__`** adds validation and derived state. **`NamedTuple`** offers a
tiny, immutable, tuple-based record; **`Enum`** replaces magic values with named
singleton constants; and the third-party **`attrs`** provides a richer superset.
Knowing **which** to reach for — dataclass, NamedTuple, Enum, or a plain class — is
the practical skill this module builds, and it's exactly the fluency modern Python
interviews and codebases expect.

> **You have mastered this module when** you can: convert a boilerplate class to a
> dataclass; use `default_factory` and `frozen` correctly; add `__post_init__`
> validation; define an `Enum`; and justify dataclass vs NamedTuple vs Enum vs plain
> class for a given requirement.
