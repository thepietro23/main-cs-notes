---
title: "Module 11 — Object Typing & Protocols"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — Object Typing & Protocols

> **Why this module matters.**
> Python is dynamically typed, but modern professional Python is **gradually typed**
> — real codebases (and interviewers) expect **type hints**. For OOP the key ideas
> are **Generics** (a `Stack` that works for any element type while staying
> type-safe) and **`Protocol`** — which turns Module 6's *duck typing* into
> something a checker like **mypy** can verify **without inheritance**. Understanding
> **ABC (nominal) vs Protocol (structural)** typing is a modern-Python differentiator
> and directly shapes how you design flexible, checkable interfaces.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★       | ★           | ★★★★★       | ★★★★       |

**Most-asked concepts:** are type hints enforced at runtime? (no); **Generics** and
**`TypeVar`**; **`Protocol`** / structural typing; **ABC vs Protocol**; `Optional`/
`Union`/`|`; `ClassVar`, `Final`, `Self`; what `mypy` does.

**What you must be able to do after this module:** annotate a class fully; write a
generic class with `TypeVar`; define a `Protocol` and explain how it formalises duck
typing; and choose ABC vs Protocol for an interface.

---

## 11.1 Type Hints — for tools, not the interpreter

**Type hints** annotate variables, parameters, and returns. Crucially, **Python does
not enforce them at run time** — they're for **IDEs, static checkers (mypy/pyright),
and human readers**.

![A type-hinted function feeds three benefits — IDE autocomplete, mypy static checking, documentation — but calling it with a wrong type still runs, because Python ignores hints at run time.](images/m11_01_why_hints.png)

```python
def area(r: float) -> float:
    return 3.14159 * r * r

area("oops")     # RUNS anyway (then crashes on *) — Python ignores the hint
```

Benefits: **autocomplete**, **early error detection** (via mypy), **self-documenting
code**, and safer refactoring. Costs: some verbosity; hints can drift if not checked.
The consensus in professional Python: **hint public APIs and non-trivial code.**

---

## 11.2 Annotating a Class

![Annotating class Account: owner: str, balance: float = 0.0, and def deposit(self, amt: float) -> None — attributes, parameters, and returns all typed.](images/m11_02_annotate_class.png)

```python
class Account:
    owner: str                         # annotated attribute
    balance: float = 0.0

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> None:      # param + return typed
        self.balance += amount

    def is_rich(self) -> bool:
        return self.balance > 1_000_000
```

Common building blocks: `list[int]`, `dict[str, float]`, `tuple[int, ...]`,
`Optional[str]` (= `str | None`), `Union[int, str]` (= `int | str`), `Callable[[int],
str]`.

---

## 11.3 Generic Classes & `TypeVar`

A **generic** class is parameterised by a **type variable** so it works with *any*
element type while the checker still tracks *which* type.

![A generic class Stack(Generic[T]) can be used as Stack[int], Stack[str], or Stack[User]; T is a type variable the checker tracks per usage.](images/m11_03_generic.png)

```python
from typing import Generic, TypeVar

T = TypeVar("T")                       # a type variable

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()

s: Stack[int] = Stack()
s.push(1)          # OK
# s.push("x")      # mypy error: expected int
x: int = s.pop()   # checker knows pop() returns int
```

(In Python 3.12+ you can write `class Stack[T]:` directly — the same idea, cleaner
syntax.)

### `TypeVar` bounds link and restrict types

![A plain TypeVar('T') stands for any type; a bounded TypeVar('N', bound=Number) accepts only Number subtypes; reusing the same T links parameter and return types.](images/m11_04_typevar.png)

```python
from typing import TypeVar

N = TypeVar("N", bound=int | float)    # only numbers
def double(x: N) -> N:                 # returns the SAME type it received
    return x * 2

reveal = double(3)      # type is int
reveal2 = double(3.0)   # type is float
```

Reusing one `TypeVar` across parameters/return **links** them — the checker enforces
that `double(int)` returns `int`, not just "a number".

---

## 11.4 `Protocol` — structural typing (static duck typing)

Module 6's **duck typing** says "if it has `draw()`, it's drawable." A **`Protocol`**
lets a type checker verify that **statically** — **no inheritance required**.

![A Drawable Protocol declares def draw(self); any class with a matching draw() method (Circle, Button) satisfies it, with no inheritance — matching methods = matching type.](images/m11_05_protocol.png)

```python
from typing import Protocol

class Drawable(Protocol):              # a structural interface
    def draw(self) -> None: ...

class Circle:                          # does NOT inherit Drawable...
    def draw(self) -> None: print("O")
class Button:
    def draw(self) -> None: print("[OK]")

def render(item: Drawable) -> None:    # accepts anything with draw()
    item.draw()

render(Circle())    # OK — structural match
render(Button())    # OK — no inheritance needed
```

Add `@runtime_checkable` to allow `isinstance(x, Drawable)` at run time (checks method
presence only). Protocols are how the standard library types things like "anything
iterable" (`Iterable`, `Sized`, `SupportsInt`).

---

## 11.5 ABC vs Protocol — nominal vs structural

![ABC is nominal typing: a class must explicitly inherit it (an 'is-a', declared contract). Protocol is structural typing: any class with matching methods qualifies (a 'behaves-like', implicit contract).](images/m11_06_abc_vs_protocol.png)

| | **ABC** (Module 4) | **Protocol** |
|---|---|---|
| Typing style | **nominal** (by name/inheritance) | **structural** (by shape) |
| Must inherit? | **yes** (`class C(MyABC)`) | **no** — just match the methods |
| Contract | explicit, declared | implicit, duck-typed |
| Enforced at | instantiation (missing methods) | static check (mypy); runtime with `@runtime_checkable` |
| Use when | you control the classes and want an explicit hierarchy | you want to accept **any** compatible object, including third-party classes you can't modify |

> **Rule of thumb:** use a **Protocol** to type "accepts anything that behaves like
> X" (great for decoupling and for third-party objects); use an **ABC** when you want
> a shared base with **concrete helper methods** and an explicit is-a relationship.

---

## 11.6 `mypy` — static checking

`mypy` (or `pyright`) reads your hints and flags type mismatches **before** the code
runs — turning a class of runtime bugs into check-time errors.

![Code with hints feeds into mypy's static check; it either reports an error (caught before running) or passes — type bugs are caught at check time, not in production.](images/m11_07_mypy_flow.png)

```bash
$ mypy account.py
account.py:12: error: Argument 1 to "deposit" has incompatible type "str";
                      expected "float"
```

This is especially valuable in large OOP codebases: refactors, interface changes,
and `None`-handling bugs are caught early. CI pipelines routinely run mypy as a gate.

---

## 11.7 Useful Typing Constructs for OOP

![Handy constructs: Optional[X] / X | None (value or None), ClassVar[X] (class attribute, not a dataclass field), Final (constant, no reassignment), Self (return type meaning 'this class', for chaining).](images/m11_08_special_types.png)

```python
from typing import ClassVar, Final, Optional
from typing import Self          # 3.11+ (or typing_extensions)

class Config:
    VERSION: Final = "1.0"                 # constant; reassigning flagged
    instances: ClassVar[int] = 0           # class-level, NOT a per-instance field
    name: Optional[str] = None             # str or None

    def set_name(self, n: str) -> Self:    # returns "this class" -> enables chaining
        self.name = n
        return self

Config().set_name("a").set_name("b")       # fluent chaining, correctly typed
```

- **`Optional[X]`** / **`X | None`** — may be `None` (forces you to handle it).
- **`ClassVar[X]`** — a class attribute; tells dataclasses it's **not** a field.
- **`Final`** — must not be reassigned/overridden.
- **`Self`** — the return type is the current class (subclass-correct for chaining/
  factories).

---

## Module 11 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Are hints enforced at runtime?" | (unsure) | "No — Python ignores them at run time; they exist for mypy/IDEs/docs. Use `pydantic`/manual checks if you need runtime validation." |
| "What's a Protocol?" | "An interface." | "**Structural** typing — static duck typing: any object with the right methods satisfies it, **no inheritance**; `@runtime_checkable` allows `isinstance`." |
| "ABC vs Protocol?" | "Both interfaces." | "ABC = nominal (must inherit, explicit is-a, can carry concrete methods); Protocol = structural (matches by shape, works with third-party classes). Prefer Protocol for 'accepts anything that behaves like X'." |
| "Why Generics?" | "Reuse." | "Type-safe reuse: `Stack[int]` vs `Stack[str]` while the checker tracks element types via a `TypeVar`." |

---

## Module 11 — Exam Mapping

- **GATE CS:** not tested (Python-library topic).
- **SEBI / RBI IT:** not tested.
- **FAANG / backend:** strong signal — Generics, Protocols, ABC-vs-Protocol, mypy in
  CI, and correct `Optional`/`Self` usage.

---

## Module 11 — Common Mistakes & Misconceptions

- **Believing hints are enforced at runtime** — they aren't; use validation libs if
  needed.
- **Using an ABC (forcing inheritance)** when a **Protocol** (structural) would
  decouple better.
- **Mutable/`Optional` confusion** — annotating `x: str` but assigning `None`.
- **Forgetting `ClassVar`** on a dataclass class-attribute → it becomes a field.
- **Overusing `Any`** — erases the benefit of typing.
- **Not running mypy** — hints without a checker only document, they don't catch
  bugs.

---

## Module 11 — MCQs (with answers & explanations)

**Q1.** Python type hints are enforced:
a) at runtime  b) **not at runtime (tools only)**  c) at import  d) by the GIL

<details><summary>Answer</summary>**b.** They're for static checkers/IDEs/docs; the interpreter ignores them.</details>

**Q2.** A `Protocol` uses which kind of typing?
a) nominal  b) **structural**  c) dynamic only  d) none

<details><summary>Answer</summary>**b.** Structural — matches by method shape, no inheritance needed.</details>

**Q3.** To make a class satisfy an ABC you must:
a) match methods only  b) **inherit the ABC**  c) use `@runtime_checkable`  d) nothing

<details><summary>Answer</summary>**b.** ABCs are nominal — explicit inheritance is required.</details>

**Q4.** `Stack(Generic[T])` lets you:
a) store only ints  b) **parameterise the element type (Stack[int], Stack[str])**  c) subclass type  d) skip hints

<details><summary>Answer</summary>**b.** Generics track element types per usage.</details>

**Q5.** `Optional[str]` is equivalent to:
a) `str`  b) `list[str]`  c) **`str | None`**  d) `Any`

<details><summary>Answer</summary>**c.** Optional means "this type or None".</details>

**Q6.** `@runtime_checkable` on a Protocol allows:
a) enforcing types at runtime fully  b) **`isinstance` checks (method presence)**  c) faster code  d) inheritance

<details><summary>Answer</summary>**b.** It enables `isinstance`, checking that methods exist (not signatures).</details>

**Q7.** `ClassVar[int]` on a dataclass attribute means:
a) it's a field  b) **it's a class-level variable, not a field**  c) it's frozen  d) it's private

<details><summary>Answer</summary>**b.** Dataclasses skip `ClassVar`-annotated names as fields.</details>

**Q8.** Best type for accepting "any object with a `.read()` method (incl. third-party)":
a) a concrete class  b) an ABC they must inherit  c) **a Protocol**  d) `Any`

<details><summary>Answer</summary>**c.** A Protocol matches by shape without requiring inheritance.</details>

---

## Module 11 — Design/Practice Exercises (easy → hard)

1. **(easy)** Fully annotate an `Account` class (attributes, params, returns).
2. **(easy)** Write `first(items: list[T]) -> T` using a `TypeVar`.
3. **(medium)** Implement a generic `Pair(Generic[K, V])` with typed `key`/`value`.
4. **(medium)** Define a `Comparable` Protocol with `__lt__` and a `max_of(items)`
   that accepts anything comparable.
5. **(hard)** Refactor a function that takes a concrete `FileReader` into one that
   takes a `Readable` Protocol; show a third-party object satisfies it.
6. **(hard, interview)** Explain, with code, when you'd choose a Protocol over an ABC
   for a `Serializer` interface, and vice versa.

---

## Module 11 — Concept Review (one page)

**Type hints** annotate attributes, parameters, and returns but are **not enforced at
run time** — they serve **IDEs, static checkers (`mypy`), and readers**. **Generic
classes** (`Generic[T]` with a **`TypeVar`**) give **type-safe reuse**: `Stack[int]`
vs `Stack[str]` while the checker tracks element types; a `TypeVar` reused across
signature positions **links** them, and `bound=` **restricts** it. **`Protocol`**
brings **structural typing** — *static duck typing* — so any object with the right
methods qualifies **without inheritance** (`@runtime_checkable` enables `isinstance`).
This contrasts with **ABCs**, which use **nominal** typing (explicit inheritance,
concrete helper methods, an is-a contract). Use a **Protocol** to accept "anything
that behaves like X" (great for decoupling and third-party objects), an **ABC** for a
shared, declared base. Supporting constructs — `Optional`/`|`, `ClassVar`, `Final`,
`Self` — express nullability, class-level attributes, constants, and self-returning
methods.

---

## Module 11 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Are hints enforced at runtime? | No — tools/docs only |
| Benefits of hints | IDE autocomplete, mypy checks, readability |
| Generic class | `Generic[T]` + `TypeVar` — type-safe reuse |
| `TypeVar` bound | restricts the type (`bound=Number`) |
| Protocol typing style | structural (static duck typing) |
| ABC typing style | nominal (must inherit) |
| Protocol vs ABC | shape-match, no inheritance vs explicit inheritance |
| `@runtime_checkable` | enables `isinstance` on a Protocol (method presence) |
| `Optional[X]` | `X | None` |
| `ClassVar[X]` | class attribute, not a dataclass field |
| `Final` | cannot be reassigned/overridden |
| `Self` | return type = current class (chaining/factories) |

---

## Module 11 — Pattern Recognition

- **See "accept anything with method X (incl. third-party)"** → `Protocol`.
- **See "a container/algorithm that works for any element type"** → Generics +
  `TypeVar`.
- **See "shared base with concrete helpers + explicit is-a"** → ABC.
- **See "a value that might be missing"** → `Optional`/`| None`.
- **See "fluent builder returning self"** → `-> Self`.
- **See hints but bugs still ship** → wire `mypy` into CI.

---

## Module 11 — Revision Notes / Mini Cheat Sheet

```
HINTS: annotate attrs/params/returns. NOT enforced at runtime (tools/docs/IDE only).
  list[int], dict[str,float], Optional[X]==X|None, Union[a,b]==a|b, Callable[[int],str].

GENERICS: class Stack(Generic[T]) -> Stack[int], Stack[str]. (3.12: class Stack[T].)
  TypeVar('T')            any type
  TypeVar('N', bound=X)   only X-subtypes ; reuse same T -> links in/out types.

PROTOCOL (structural / static duck typing): match methods, NO inheritance.
  @runtime_checkable -> isinstance(x, Proto) (presence only).
ABC (nominal): must inherit; explicit is-a; can carry concrete methods.
  Protocol = "behaves-like X (incl third-party)"; ABC = "declared base".

mypy/pyright: static check hints -> catch type bugs before running (use in CI).
EXTRAS: ClassVar (class attr, not field), Final (constant), Self (return this class).
```

> **Next module:** **Module 12 — Object Lifecycle & Memory.** We follow an object from
> birth to death: reference counting and the cyclic garbage collector, `__del__`
> finalisers (and why they're tricky), **`weakref`** for caches/observers without
> keeping objects alive, and `copy`/`deepcopy` internals (`__copy__`/`__deepcopy__`).

---

## Module 11 — Summary

Modern Python OOP is **gradually typed**. **Type hints** document intent and power
**static checkers** and IDEs, but Python **does not enforce them at run time**.
**Generics** (`Generic[T]`/`TypeVar`) deliver **type-safe reuse** so one class serves
many element types while the checker tracks each. **`Protocol`** formalises Module 6's
duck typing as **structural typing** — objects match by **shape**, not inheritance —
which contrasts with the **nominal**, inheritance-based **ABC**. Choosing Protocol vs
ABC (behaves-like vs is-a) is a core modern-design decision, and constructs like
`Optional`, `ClassVar`, `Final`, and `Self` round out expressive, checkable OOP.
Wiring **`mypy`** into CI turns these hints into real bug prevention.

> **You have mastered this module when** you can: fully annotate a class; write a
> generic class with `TypeVar` and a bound; define and use a `Protocol`; explain ABC
> vs Protocol and pick correctly; and describe what mypy buys you.
