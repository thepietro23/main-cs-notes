---
title: "Module 6 — Polymorphism"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — Polymorphism

> **Why this module matters.**
> Polymorphism ("many forms") is the pillar that makes inheritance and abstraction
> *pay off*: you write code against **one interface**, and it works for **many
> different types** — present and future — without `if`/`elif` type-checking. In
> Python this is supercharged by **duck typing**: an object doesn't even need to
> inherit from anything — it just needs the right method. This module also clears
> up two things interviewers probe: why Python has **no method overloading**, and
> the difference between **compile-time** and **run-time** polymorphism.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★★★    | ★★★         | ★★★★        | ★★★★★      |

**Most-asked concepts:** definition + types of polymorphism (ad-hoc, parametric,
subtype, coercion); **duck typing**; method overriding = **runtime** polymorphism;
**operator overloading** (dunders); "does Python support method overloading?" (no —
and the workarounds); compile-time vs run-time.

**What you must be able to do after this module:** write polymorphic code using a
shared method name across types; explain duck typing with an example; overload an
operator with a dunder; explain why Python lacks overloading and show
`singledispatch`/default-arg alternatives; and classify a given example by
polymorphism type.

---

## 6.1 What Is Polymorphism?

**Polymorphism** = the ability of **one interface (name/operation) to work with
objects of many different types**, each responding in its own way. The calling code
stays the same; the behaviour varies with the object.

![A single loop calling a.speak() produces Woof, Meow, or Moo depending on whether a is a Dog, Cat, or Cow — one interface, many forms.](images/m06_01_one_interface_many.png)

```python
class Dog:
    def speak(self): return "Woof"
class Cat:
    def speak(self): return "Meow"
class Cow:
    def speak(self): return "Moo"

for animal in [Dog(), Cat(), Cow()]:
    print(animal.speak())        # Woof / Meow / Moo — same call, many forms
```

The loop doesn't check types or branch — it just calls `speak()`. Add a new animal
tomorrow and the loop works unchanged. **That absence of type-checking `if`s is the
whole point.**

---

## 6.2 The Four Kinds of Polymorphism

![Four kinds: subtype (overriding), ad-hoc (overloading / operators), parametric (generics), and coercion (implicit casting).](images/m06_02_poly_types.png)

| Kind | Meaning | Python example |
|---|---|---|
| **Subtype** (inclusion) | subclass overrides a base method; resolved at runtime | `Dog.speak()` overriding `Animal.speak()` |
| **Ad-hoc** (overloading) | same operator/name, type-specific behaviour | `+` on ints vs strings (`__add__`) |
| **Parametric** (generics) | one implementation works for any type | `list`, `dict`, `TypeVar` (Module 11) |
| **Coercion** | implicit type conversion | `1 + 2.0` → `float`; truthiness |

Python emphasises **subtype** (overriding) and **ad-hoc** (dunder operators),
generalised by **duck typing**.

---

## 6.3 Subtype Polymorphism — overriding (runtime dispatch)

When a subclass **overrides** a method, calling it on an object runs the version
matching the object's **actual runtime type** — **dynamic dispatch**.

![shape.area() dispatches at run time: if the object is a Circle it computes pi*r^2, if a Square it computes s*s — decided by the object's real class.](images/m06_03_overriding_runtime.png)

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

class Square(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2

def total_area(shapes):
    return sum(s.area() for s in shapes)   # polymorphic — no type checks

print(total_area([Circle(1), Square(2)]))  # 3.14159 + 4
```

`total_area` neither knows nor cares which concrete shapes it gets — it relies on
the shared `area()` interface. This is the engine behind the **Open/Closed
Principle** (M13): add a new `Shape` subclass and `total_area` still works.

---

## 6.4 Duck Typing — Python's superpower

> *"If it walks like a duck and quacks like a duck, it's a duck."*

**Duck typing** means Python cares about **what an object can do** (its methods),
**not what it is** (its class). No shared base class or interface is required — just
the right method.

![make_it_quack(x) calls x.quack(); a Duck and a Person both have quack() so both work, while a Dog without quack() fails — type is irrelevant, behaviour matters.](images/m06_04_duck_typing.png)

```python
class Duck:
    def quack(self): return "Quack!"
class Person:
    def quack(self): return "I'm imitating a duck!"

def make_it_quack(thing):
    return thing.quack()          # no isinstance check; just needs .quack()

print(make_it_quack(Duck()))      # Quack!
print(make_it_quack(Person()))    # I'm imitating a duck!  (unrelated class!)
```

This is why Python's file-like objects, iterables, and context managers work so
uniformly: any object implementing the right dunder methods (`__iter__`, `read`,
`__enter__`, …) "is" that kind of thing. **EAFP** ("Easier to Ask Forgiveness than
Permission") is the matching style: just *try* the operation and catch failure,
rather than checking types first.

```python
try:
    thing.quack()
except AttributeError:
    print("can't quack")
```

---

## 6.5 Operator Overloading — ad-hoc polymorphism

The same operator behaves differently by type because operators dispatch to
**dunder methods** (Module 7). `a + b` really calls `a.__add__(b)`.

![The '+' operator: int + int adds, str + str joins, list + list merges — each type defines its own __add__, so one symbol has many meanings.](images/m06_05_operator_overload.png)

```python
print(1 + 2)            # 3     -> int.__add__
print("a" + "b")        # 'ab'  -> str.__add__
print([1] + [2])        # [1,2] -> list.__add__

class Vector:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, other):                 # define + for our type
        return Vector(self.x + other.x, self.y + other.y)
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

print(Vector(1, 2) + Vector(3, 4))            # Vector(4, 6)
```

You **overload** `+`, `==`, `<`, `[]`, `len()`, and more for your own classes by
implementing the matching dunder — covered fully in Module 7.

---

## 6.6 Python Has NO Method Overloading

In Java/C++, you can define several methods with the **same name but different
parameter lists**; the compiler picks by argument types (**compile-time / ad-hoc**
polymorphism). **Python does not do this** — a second `def` with the same name
simply **replaces** the first.

![Two defs named area with different parameters: the second definition wins and erases the first — Python has no overloading; use default args, *args, or singledispatch instead.](images/m06_06_no_overloading.png)

```python
class Calc:
    def area(self, r):            # this is...
        return 3.14159 * r * r
    def area(self, l, w):         # ...silently REPLACED by this
        return l * w

# Calc().area(5)     -> TypeError: missing 'w'  (only the 2nd area exists)
```

**Pythonic alternatives:**

```python
# 1) default arguments
def area(l, w=None):
    return l * l if w is None else l * w

# 2) *args / **kwargs for variable signatures
def area(*dims):
    return dims[0] ** 2 if len(dims) == 1 else dims[0] * dims[1]

# 3) functools.singledispatch — dispatch by first-arg TYPE
```

![functools.singledispatch routes process(x) to different implementations by the type of x: int doubles, str uppercases, list reverses.](images/m06_07_singledispatch.png)

```python
from functools import singledispatch

@singledispatch
def process(x):
    raise TypeError("unsupported")

@process.register
def _(x: int):   return x * 2
@process.register
def _(x: str):   return x.upper()
@process.register
def _(x: list):  return x[::-1]

print(process(10), process("hi"), process([1, 2]))   # 20 HI [2, 1]
```

> **Interview answer:** *"Python doesn't support method overloading — the last
> definition wins. Use default/keyword/`*args` for flexible signatures, or
> `functools.singledispatch` for type-based dispatch."*

---

## 6.7 Compile-time vs Run-time Polymorphism

![Compile-time (static, ad-hoc): overloading and operator resolution decided early. Run-time (dynamic, subtype): overriding and duck typing decided late. Python resolves almost everything at run time.](images/m06_08_compile_vs_runtime.png)

| | Compile-time (static) | Run-time (dynamic) |
|---|---|---|
| A.k.a. | ad-hoc | subtype / inclusion |
| Mechanism | overloading, operator resolution | **overriding, duck typing** |
| Decided | at compile time (in static langs) | at run time, by object's type |
| Python | mostly N/A (interpreted, dynamic) | **this is Python's world** |

Because Python is dynamically typed and interpreted, **method dispatch happens at
run time** by the object's actual type. There's no compile step choosing overloads.
This makes Python overwhelmingly a **run-time (subtype + duck-typed)** polymorphism
language.

---

## Module 6 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "What is polymorphism?" | "One name, many forms." | "One interface working across many types; caller code is uniform, behaviour varies by object; eliminates type-checking `if`s and enables Open/Closed." |
| "Duck typing?" | "If it quacks it's a duck." | Adds: cares about behaviour not class; no base class needed; underpins Python's iterables/file-likes; pairs with EAFP. |
| "Does Python have overloading?" | "No." | "Correct — last def wins. Use defaults/`*args` or `functools.singledispatch` for type dispatch." |
| "Runtime vs compile-time?" | (unsure) | "Overriding + duck typing = run-time (dynamic dispatch by real type); overloading/operator resolution = compile-time in static langs. Python is almost all run-time." |

---

## Module 6 — Exam Mapping

- **GATE CS:** classify polymorphism types; overriding vs overloading; static vs
  dynamic binding.
- **SEBI / RBI IT:** definition; examples of polymorphism; operator overloading.
- **FAANG:** write duck-typed/polymorphic code; explain no-overloading + fixes;
  connect polymorphism to Open/Closed and Strategy.

---

## Module 6 — Common Mistakes & Misconceptions

- **Thinking Python supports method overloading** — it doesn't; the last def wins.
- **Confusing overriding (runtime, subclass) with overloading (compile-time, same
  class, different params).**
- **Adding `isinstance` ladders** where duck typing/overriding would remove the
  branching.
- **Believing duck typing needs inheritance** — it needs only the *method*.
- **Forgetting `__add__` etc. must return a value** (often a new object), not
  mutate in place (unless it's `__iadd__`).

---

## Module 6 — MCQs (with answers & explanations)

**Q1.** Method overriding is which kind of polymorphism?
a) ad-hoc  b) **subtype (runtime)**  c) parametric  d) coercion

<details><summary>Answer</summary>**b.** Overriding is subtype polymorphism, resolved at run time by the object's type.</details>

**Q2.** Duck typing means:
a) checking `isinstance`  b) **caring about behaviour (methods), not the class**  c) casting types  d) using ABCs

<details><summary>Answer</summary>**b.** If the object has the needed method, it works — regardless of its type.</details>

**Q3.** Defining two same-named methods with different parameters in one class:
a) overloads them  b) errors  c) **keeps only the last definition**  d) merges them

<details><summary>Answer</summary>**c.** Python has no overloading; the second `def` replaces the first.</details>

**Q4.** `a + b` on custom objects calls:
a) `a.plus(b)`  b) **`a.__add__(b)`**  c) `add(a, b)`  d) `a.concat(b)`

<details><summary>Answer</summary>**b.** Operators dispatch to dunder methods.</details>

**Q5.** For type-based function dispatch in Python, use:
a) method overloading  b) `if isinstance` only  c) **`functools.singledispatch`**  d) macros

<details><summary>Answer</summary>**c.** `singledispatch` selects an implementation by the first argument's type.</details>

**Q6.** Polymorphism helps most by:
a) saving memory  b) **removing type-checking branches and enabling extension**  c) enforcing privacy  d) speeding compilation

<details><summary>Answer</summary>**b.** Uniform interface → no `if type ==` ladders; new types slot in (Open/Closed).</details>

**Q7.** `1 + 2.0 == 3.0` demonstrates which polymorphism?
a) subtype  b) parametric  c) **coercion**  d) overriding

<details><summary>Answer</summary>**c.** The int is coerced to float before addition.</details>

**Q8.** Python method dispatch happens:
a) at compile time  b) **at run time by the object's type**  c) never  d) at import only

<details><summary>Answer</summary>**b.** Dynamic dispatch — decided at run time.</details>

---

## Module 6 — Design/Practice Exercises (easy → hard)

1. **(easy)** Write `Dog`, `Cat`, `Duck` each with `speak()`; loop and print
   polymorphically.
2. **(easy)** Write `describe(x)` that calls `x.area()` and works for any shape with
   an `area` method (duck typing) — no base class.
3. **(medium)** Add `__add__` and `__eq__` to a `Money` class so `Money(5) +
   Money(3) == Money(8)`.
4. **(medium)** Replace an `if isinstance(x, int)/str/list` ladder with
   `functools.singledispatch`.
5. **(hard)** Implement a `Vector` supporting `+`, `-`, `*` (scalar), `==`, and
   `len`-style magnitude; make it print nicely.
6. **(hard, interview)** Explain, with code, the difference between overriding and
   "overloading" in Python, and show two Pythonic ways to fake overloading.

---

## Module 6 — Concept Review (one page)

**Polymorphism** lets **one interface serve many types**: the caller writes uniform
code and each object responds in its own way, eliminating type-checking branches.
Its kinds are **subtype** (overriding, resolved at **run time** by the object's real
type — dynamic dispatch), **ad-hoc** (operator/name overloading via **dunder
methods**), **parametric** (generics), and **coercion**. Python generalises subtype
polymorphism with **duck typing** — behaviour, not class, decides compatibility, so
no shared base is required (pairs with the **EAFP** style). **Operators are
overloaded** by implementing dunders like `__add__`. Python has **no method
overloading** (the last `def` wins); use **default/`*args`** or
**`functools.singledispatch`** instead. Because Python is dynamic, **dispatch is a
run-time decision** — it is overwhelmingly a run-time-polymorphism language.

---

## Module 6 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Polymorphism (1 line) | one interface, many types/forms |
| Overriding is which type | subtype / run-time |
| Duck typing | behaviour (methods) matters, not the class |
| EAFP | try the op, catch failure (vs check-first LBYL) |
| Operator overloading via | dunder methods (`__add__`, `__eq__`, …) |
| Does Python overload methods? | No — last def wins |
| Overloading alternatives | default args, `*args`, `functools.singledispatch` |
| Overriding vs overloading | subclass-runtime vs same-name-different-params (compile-time) |
| Coercion example | `1 + 2.0` → float |
| Dispatch timing in Python | run time, by object's actual type |
| Polymorphism enables which SOLID principle | Open/Closed |

---

## Module 6 — Pattern Recognition

- **See `if isinstance(x, A): ... elif isinstance(x, B): ...`** → replace with
  overriding or `singledispatch`.
- **See "make this work for any object that can X"** → duck typing (call the method).
- **See "same operator for my custom type"** → operator overloading via dunders.
- **See "one function, several argument shapes"** → default/`*args` or
  `singledispatch` (not overloading).
- **See "add new types without touching existing code"** → polymorphism +
  Open/Closed.

---

## Module 6 — Revision Notes / Mini Cheat Sheet

```
POLYMORPHISM = one interface, many types. Uniform caller; behaviour varies by object.
KINDS: subtype(overriding, RUNTIME), ad-hoc(overloading/operators), parametric(generics), coercion.

SUBTYPE: override base method -> dynamic dispatch by object's real class.
DUCK TYPING: needs only the METHOD, not a shared base. "quacks -> duck." EAFP style.
OPERATOR OVERLOAD: a + b -> a.__add__(b). Define dunders for your type (M7).

NO METHOD OVERLOADING in Python (2nd def replaces 1st). Instead:
  - default args:  def f(a, b=None)
  - *args/**kwargs
  - functools.singledispatch  (dispatch by first arg TYPE)

COMPILE-TIME (ad-hoc: overloading) vs RUN-TIME (subtype: overriding, duck typing).
Python = dynamic -> nearly all dispatch is RUN TIME. Powers Open/Closed (M13).
```

> **Next module:** **Module 7 — Dunder (Magic) Methods & the Data Model.** We go
> deep on the special methods that made this module's operator overloading and duck
> typing possible: `__repr__`/`__str__`, `__eq__`/`__hash__`, comparison and
> arithmetic operators, containers (`__len__`, `__getitem__`), iterators, callables,
> and context managers — the protocols that let *your* objects behave like built-ins.

---

## Module 6 — Summary

**Polymorphism** — "many forms" — lets one interface work across many types so the
caller writes uniform code while each object behaves appropriately, removing
type-checking branches and enabling extension (**Open/Closed**). Its main flavours
are **subtype** (method **overriding**, resolved at **run time** via dynamic
dispatch) and **ad-hoc** (**operator overloading** through dunder methods), with
**parametric** and **coercion** rounding out the theory. Python's signature twist is
**duck typing**: compatibility depends on having the right *method*, not the right
*class*, so no shared base is needed. Python deliberately lacks **method
overloading** (the last `def` wins), offering **default/`*args`** and
**`functools.singledispatch`** instead. Since Python is dynamic, method resolution
is a **run-time** decision — making it, above all, a run-time-polymorphism language.

> **You have mastered this module when** you can: write polymorphic and duck-typed
> code without `isinstance` ladders; overload an operator with a dunder; explain why
> Python has no overloading and demonstrate two workarounds; and correctly classify
> overriding vs overloading and run-time vs compile-time.
