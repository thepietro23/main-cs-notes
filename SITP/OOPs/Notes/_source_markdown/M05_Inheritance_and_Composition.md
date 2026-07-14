---
title: "Module 5 — Inheritance & Composition"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — Inheritance & Composition

> **Why this module matters.**
> Inheritance is how classes **reuse and extend** each other — and it is where
> Python's OOP gets genuinely deep because Python allows **multiple inheritance**,
> which forces a precise answer to "if two parents define the same method, which
> wins?" That answer is the **MRO (Method Resolution Order)** computed by **C3
> linearisation** — a guaranteed FAANG interview topic. Just as important is the
> design wisdom that balances it: **"favour composition over inheritance."** Get
> both the mechanism (MRO, `super()`) and the judgment (is-a vs has-a) and you can
> design class hierarchies that don't rot.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★★★    | ★★★         | ★★★★        | ★★★★★      |

**Most-asked concepts:** `super()` and cooperative inheritance; the **diamond
problem** and **MRO/C3**; single vs multiple inheritance; **composition vs
inheritance** ("favour composition"); aggregation vs composition; mixins;
`isinstance`/`issubclass`; method overriding.

**What you must be able to do after this module:** write a subclass that overrides
and extends via `super()`; compute and explain an MRO for a diamond; decide is-a
vs has-a for a design; and explain *why* composition is usually safer than deep
inheritance.

---

## 5.1 Inheritance Basics — the "is-a" relationship

**Inheritance** lets a **subclass (child)** reuse and extend a **superclass
(parent)**. The child automatically gets the parent's attributes and methods, and
can **add** new ones or **override** existing ones. The relationship is **"is-a"**:
a `Dog` **is an** `Animal`.

![Animal defines eat() and sleep(); Dog and Cat inherit those and each add their own method (bark, meow) — an is-a relationship.](images/m05_01_is_a.png)

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def eat(self):
        return f"{self.name} is eating"

class Dog(Animal):              # Dog inherits from Animal
    def bark(self):
        return "Woof!"

d = Dog("Rex")
print(d.eat())                  # inherited: "Rex is eating"
print(d.bark())                 # own method: "Woof!"
print(isinstance(d, Animal))    # True — a Dog IS-A Animal
print(issubclass(Dog, Animal))  # True
```

Every class implicitly inherits from **`object`**, the root of all types.

---

## 5.2 Overriding + `super()`

A subclass can **override** a method by redefining it. Usually you don't want to
*replace* the parent's work but **extend** it — call `super()` to run the parent's
version, then add to it.

![Manager.raise_pay() overrides Employee.raise_pay() but calls super().raise_pay() to reuse the base logic, then adds a bonus.](images/m05_02_override_super.png)

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

class Manager(Employee):
    def __init__(self, name, salary, reports):
        super().__init__(name, salary)   # reuse parent's __init__
        self.reports = reports           # then add manager-specific state

m = Manager("Asha", 200000, ["Rob", "Sam"])
print(m.name, m.salary, m.reports)       # Asha 200000 ['Rob', 'Sam']
```

`super()` returns a proxy that dispatches to the **next class in the MRO** (§5.4) —
not necessarily the literal parent. This matters enormously under multiple
inheritance. **Always prefer `super().__init__(...)` over `Parent.__init__(self,
...)`** — the latter breaks cooperative multiple inheritance.

---

## 5.3 Types of Inheritance

![Four inheritance shapes: single (B from A), multilevel (C from B from A), hierarchical (B and C both from A), and multiple (C from both A and B).](images/m05_03_inheritance_types.png)

| Type | Shape | Example |
|---|---|---|
| **Single** | one parent | `Dog(Animal)` |
| **Multilevel** | chain | `Puppy(Dog(Animal))` |
| **Hierarchical** | many children, one parent | `Dog(Animal)`, `Cat(Animal)` |
| **Multiple** | two+ parents | `class C(A, B)` |
| **Hybrid** | a mix (often creates diamonds) | combos of the above |

Python supports **all** of these — including **multiple inheritance**, which
Java/C# deliberately forbid (they allow multiple *interfaces* only). Multiple
inheritance is powerful (mixins) but introduces the diamond problem.

---

## 5.4 The Diamond Problem & the MRO

The **diamond problem**: `D` inherits from `B` and `C`, both of which inherit from
`A`. If you call `d.method()` and every class defines it, **which one runs?**

![D inherits from B and C, which both inherit from A: a diamond. Calling a method D inherits along two paths raises the question of which ancestor's version wins.](images/m05_04_mro_diamond.png)

Python answers with the **MRO (Method Resolution Order)** — a single, deterministic
ordering of all ancestors, computed by the **C3 linearisation** algorithm.

![The MRO for the diamond is [D, B, C, A, object]; super() walks this list left to right, visiting each class exactly once.](images/m05_05_c3.png)

```python
class A:
    def who(self): return "A"
class B(A):
    def who(self): return "B -> " + super().who()
class C(A):
    def who(self): return "C -> " + super().who()
class D(B, C):
    def who(self): return "D -> " + super().who()

print(D.__mro__)     # (D, B, C, A, object)
print(D().who())     # D -> B -> C -> A   <-- each class once, in MRO order
```

**C3 rules (intuition):** the MRO is **depth-first, left-to-right**, but with the
constraint that **a class always appears before its parents**, and **each class
appears exactly once**. Crucially, `A` comes **after both B and C** — `super()` in
`B` goes to `C` (not straight to `A`), which is why every class's contribution runs
exactly once. This is **cooperative multiple inheritance**, and it only works if
everyone uses `super()`.

> **Interview gold:** *"How does Python resolve the diamond problem?"* → "With a
> deterministic **MRO** via **C3 linearisation**; `super()` follows the MRO, so
> each ancestor runs once. Check it with `Class.__mro__` or `Class.mro()`."

---

## 5.5 Mixins — capability injection via (multiple) inheritance

A **mixin** is a small class that provides **one focused capability** to be "mixed
into" other classes via inheritance. Mixins aren't meant to be instantiated alone
and usually hold no state.

![A JSONMixin providing to_json() is mixed into a User class via class User(JSONMixin, ...), giving User serialisation for free.](images/m05_06_mixin.png)

```python
class JSONMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class User(JSONMixin):               # User gains to_json() for free
    def __init__(self, name):
        self.name = name

print(User("Nidhi").to_json())       # {"name": "Nidhi"}
```

Django and DRF (`LoginRequiredMixin`, `ListModelMixin`) use this heavily. Mixins
are the *good* face of multiple inheritance: small, orthogonal, `super()`-friendly.

---

## 5.6 Composition — the "has-a" relationship

**Composition** builds complex objects by **containing other objects** rather than
inheriting from them. The relationship is **"has-a"**: a `Car` **has an** `Engine`.

![Inheritance models 'is-a' (Car is-a Vehicle); composition models 'has-a' (Car has-a Engine) by holding a reference to another object.](images/m05_07_composition_vs_inheritance.png)

```python
class Engine:
    def start(self): return "engine started"

class Car:
    def __init__(self):
        self.engine = Engine()       # Car HAS-A Engine (composition)
    def start(self):
        return self.engine.start()   # delegate to the part
```

### Why "favour composition over inheritance"

| Concern | Deep inheritance | Composition |
|---|---|---|
| Coupling | tight (subclass depends on parent internals) | loose (talks via the part's API) |
| Flexibility | fixed at class-definition time | swap parts at **runtime** |
| Fragility | "fragile base class" — parent change breaks children | isolated |
| Reuse | only along the is-a axis | any part, any class |

> **The maxim:** use **inheritance for genuine is-a** relationships with shared
> behaviour; use **composition for has-a** and for combining behaviours. Deep
> inheritance trees are a top source of unmaintainable OOP (see M13 Strategy
> pattern, which *replaces* inheritance with composition).

---

## 5.7 Aggregation vs Composition (a UML distinction)

Both are "has-a", but they differ in **ownership / lifecycle**:

![Aggregation: a Team has Players who outlive the team (shared, independent). Composition: a House has Rooms that are destroyed with the house (owned, exclusive).](images/m05_08_aggregation_composition.png)

| | Aggregation ("has-a", weak) | Composition ("owns-a", strong) |
|---|---|---|
| Lifecycle | part **outlives** the whole | part **dies with** the whole |
| Ownership | shared / independent | exclusive |
| Example | `Team` has `Player`s (players exist without the team) | `House` has `Room`s (rooms gone if house demolished) |
| UML | hollow diamond ◇ | filled diamond ◆ |

```python
# Aggregation: players passed in, live independently
class Team:
    def __init__(self, players):
        self.players = players       # references to external objects

# Composition: rooms created and owned by the house
class House:
    def __init__(self):
        self.rooms = [Room(), Room()]  # created + owned here
```

---

## 5.8 `isinstance`, `issubclass`, and `object`

```python
isinstance(d, Animal)      # True — instance check (respects inheritance)
issubclass(Dog, Animal)    # True — class relationship
type(d) is Dog             # True — EXACT type (does NOT respect inheritance)
```

Prefer `isinstance` over `type(x) == ...` because `isinstance` honours subclasses
(a `Puppy` *is an* `Animal`). Everything ultimately derives from **`object`**, which
supplies default `__init__`, `__str__`, `__eq__`, etc. (Module 7).

---

## Module 5 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Diamond problem?" | "Two parents, ambiguity." | "Python resolves it with a deterministic **MRO** via **C3 linearisation**; `super()` follows the MRO so each ancestor runs once — cooperative inheritance." + shows `__mro__`. |
| "`super()` — what does it do?" | "Calls the parent." | "Returns a proxy to the **next class in the MRO** (not always the literal parent); essential for cooperative multiple inheritance; use it over `Parent.__init__`." |
| "Composition vs inheritance?" | "has-a vs is-a." | Adds *why* composition is favoured: loose coupling, runtime swap, avoids fragile base class; inheritance only for true is-a. |
| "Aggregation vs composition?" | (often blurred) | Lifecycle/ownership: composition parts die with the whole; aggregation parts live independently. |

---

## Module 5 — Exam Mapping

- **GATE CS:** MRO computation; types of inheritance; `super()` behaviour; is-a vs
  has-a.
- **SEBI / RBI IT:** definitions; single vs multiple inheritance; which languages
  allow multiple inheritance.
- **FAANG:** compute an MRO live; refactor an inheritance smell into composition;
  design with mixins; justify design choices.

---

## Module 5 — Common Mistakes & Misconceptions

- **Using `Parent.__init__(self, ...)` instead of `super().__init__(...)`** —
  breaks cooperative multiple inheritance and can skip classes in the MRO.
- **Thinking `super()` always means the immediate parent** — it means the *next*
  class in the MRO.
- **Overusing inheritance** ("everything extends a base") → fragile, deep trees;
  prefer composition.
- **Confusing aggregation and composition** (lifecycle is the key).
- **`type(x) == Cls` for type checks** — misses subclasses; use `isinstance`.
- **Forgetting the child's `__init__` must call `super().__init__`** — parent state
  goes uninitialised.

---

## Module 5 — MCQs (with answers & explanations)

**Q1.** For `class D(B, C)` where `B(A)` and `C(A)`, the MRO is:
a) D, A, B, C  b) **D, B, C, A, object**  c) D, C, B, A  d) D, B, A, C

<details><summary>Answer</summary>**b.** C3 linearisation: subclass first, left-to-right, ancestor after all its descendants; `A` comes after both `B` and `C`.</details>

**Q2.** `super()` dispatches to:
a) the base `object`  b) the literal parent always  c) **the next class in the MRO**  d) a random parent

<details><summary>Answer</summary>**c.** It follows the MRO, which is why cooperative inheritance works.</details>

**Q3.** "A `Car` has an `Engine`" is:
a) inheritance  b) **composition**  c) polymorphism  d) an interface

<details><summary>Answer</summary>**b.** has-a = composition; is-a would be inheritance.</details>

**Q4.** Which best fits *aggregation*?
a) House–Room  b) **University–Student** (students exist without the university)  c) Car–Engine  d) Body–Heart

<details><summary>Answer</summary>**b.** Students outlive/exist independently of the university — weak ownership.</details>

**Q5.** Python allows multiple inheritance of:
a) interfaces only  b) **classes**  c) neither  d) abstract classes only

<details><summary>Answer</summary>**b.** Unlike Java, Python allows multiple inheritance of concrete classes.</details>

**Q6.** "Favour composition over inheritance" is advised mainly because:
a) it's faster  b) **it reduces coupling and avoids fragile base classes**  c) Python requires it  d) it uses less memory

<details><summary>Answer</summary>**b.** Composition is more flexible and less fragile than deep inheritance.</details>

**Q7.** A mixin is:
a) a large base class  b) **a small class adding one focused capability via inheritance**  c) a metaclass  d) a decorator

<details><summary>Answer</summary>**b.** Mixins inject orthogonal behaviour and aren't used standalone.</details>

**Q8.** To inspect a class's method resolution order:
a) `Cls.order()`  b) **`Cls.__mro__` / `Cls.mro()`**  c) `mro(Cls)`  d) `Cls.__bases__` only

<details><summary>Answer</summary>**b.** `__mro__` (tuple) or `mro()` (list). `__bases__` shows only direct parents.</details>

---

## Module 5 — Design/Practice Exercises (easy → hard)

1. **(easy)** Create `Animal` with `speak()`; subclass `Dog`/`Cat` overriding it;
   confirm `isinstance` and `issubclass`.
2. **(easy)** Add `super().__init__` to a `Manager(Employee)` and show parent state
   is set.
3. **(medium)** Build a diamond `A/B/C/D`, print `D.__mro__`, and trace the output
   of a cooperative `who()` chain.
4. **(medium)** Write a `TimestampMixin` adding a `created_at` and mix it into two
   unrelated classes.
5. **(hard)** Refactor a 3-level inheritance hierarchy (`Vehicle → Car →
   ElectricCar`) that's becoming fragile into a composition design with a
   swappable `Engine`/`Battery` part.
6. **(hard, interview)** Given `class Duck(Flyer, Swimmer)` where both define
   `move()` calling `super().move()`, predict the output and explain via the MRO.

---

## Module 5 — Concept Review (one page)

**Inheritance** models **is-a**: a subclass reuses and extends a superclass,
**overriding** methods and calling **`super()`** to reuse the parent's part.
`super()` dispatches to the **next class in the MRO**, not necessarily the literal
parent — critical under **multiple inheritance**, which Python allows. When
hierarchies form a **diamond**, Python resolves method lookup with a deterministic
**MRO** computed by **C3 linearisation** (subclass first, left-to-right, ancestor
after all descendants, each class once), enabling **cooperative** inheritance where
every ancestor runs once — the basis of **mixins**. **Composition** models
**has-a** by containing other objects and delegating to them; it is **favoured over
inheritance** because it's loosely coupled, runtime-swappable, and avoids fragile
base classes. **Aggregation vs composition** differ by ownership/lifecycle: composed
parts die with the whole; aggregated parts live independently.

---

## Module 5 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Inheritance relationship | "is-a" (Dog is-a Animal) |
| Composition relationship | "has-a" (Car has-a Engine) |
| `super()` dispatches to | the next class in the MRO |
| Diamond problem solution | deterministic MRO via C3 linearisation |
| MRO of `D(B,C)`, `B(A)`, `C(A)` | D, B, C, A, object |
| Inspect MRO | `Cls.__mro__` / `Cls.mro()` |
| Does Python allow multiple inheritance? | Yes (of concrete classes) |
| Mixin | small class adding one capability via inheritance |
| Aggregation vs composition | parts independent vs parts owned & die with whole |
| Favour composition because | loose coupling, runtime swap, no fragile base class |
| `isinstance` vs `type() ==` | isinstance respects subclasses; `type ==` is exact |
| Root of all classes | `object` |

---

## Module 5 — Pattern Recognition

- **See "X is a kind of Y with extra behaviour"** → inheritance (`class X(Y)`).
- **See "X is built from / uses a Y"** → composition (hold a `Y` instance).
- **See two parents defining the same method** → reason via the MRO.
- **See "add logging/serialisation/timestamps to many classes"** → a mixin.
- **See a deep, fragile class tree** → refactor toward composition (Strategy, M15).
- **See "part must be destroyed with the owner"** → composition; else aggregation.

---

## Module 5 — Revision Notes / Mini Cheat Sheet

```
INHERITANCE = is-a. class Child(Parent): ... reuse + override.
OVERRIDE + super().method() -> extend parent instead of replacing it.
ALWAYS super().__init__(...) (not Parent.__init__) for cooperative MI.

TYPES: single, multilevel, hierarchical, multiple (2+ parents), hybrid.
Python ALLOWS multiple inheritance of classes (Java: interfaces only).

DIAMOND: D(B,C), B(A), C(A) -> MRO via C3 linearisation:
  rule: subclass before parents; left-to-right; ancestor after ALL descendants; each once.
  D.__mro__ = (D, B, C, A, object).  super() walks it -> each ancestor runs once.
MIXIN = small capability class mixed in via inheritance (LoginRequiredMixin...).

COMPOSITION = has-a. Hold another object + delegate. FAVOUR over inheritance:
  loose coupling, runtime swap, no fragile base class.
AGGREGATION (weak, part independent, ◇) vs COMPOSITION (strong, part owned, ◆).
isinstance() respects subclasses; type(x) is C is exact. Root = object.
```

> **Next module:** **Module 6 — Polymorphism.** With inheritance in place, we study
> the pillar that makes it pay off: **one interface, many implementations** — method
> overriding, **duck typing** ("if it quacks like a duck…"), operator overloading,
> and the difference between compile-time and run-time polymorphism (and why Python
> has no true method overloading).

---

## Module 5 — Summary

**Inheritance** expresses **is-a**: a subclass reuses a superclass, **overrides**
methods, and calls **`super()`** to extend rather than replace parent behaviour.
Because Python permits **multiple inheritance**, it needs a precise **Method
Resolution Order**, computed by **C3 linearisation**, which resolves the **diamond
problem** deterministically and enables **cooperative** inheritance and **mixins** —
provided everyone uses `super()`. **Composition** expresses **has-a** by containing
and delegating to other objects, and is generally **favoured over inheritance** for
its loose coupling and flexibility; the finer **aggregation-vs-composition**
distinction turns on whether the part's lifecycle is independent of, or owned by,
the whole. Mastering both the mechanism (MRO/`super()`) and the judgment (is-a vs
has-a) is what separates durable class designs from fragile ones.

> **You have mastered this module when** you can: write cooperative subclasses with
> `super()`; compute and explain any diamond's MRO; choose is-a vs has-a for a
> design and justify it; and articulate why composition is usually the safer
> default.
