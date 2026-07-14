---
title: "Module 14 — Design Patterns I (Creational & Structural)"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14 — Design Patterns I (Creational & Structural)

> **Why this module matters.**
> If SOLID is the *why*, **design patterns** are proven *hows* — named solutions to
> recurring design problems (from the "Gang of Four"). Knowing them gives you a
> shared vocabulary ("let's use a Factory here") and battle-tested structures for
> LLD interviews. But there's a Python twist: several classic patterns exist to work
> around limitations Python doesn't have, so the **Pythonic** version is often
> simpler (a module is a Singleton; `@decorator`/first-class functions replace much
> ceremony). This module covers **creational** (how objects are made) and
> **structural** (how they're composed) patterns.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★      | ★★          | ★★★★        | ★★★★★      |

**Most-asked concepts:** Singleton (and Pythonic alternatives); Factory Method /
Abstract Factory; Builder; Adapter; Decorator (pattern vs Python `@`); Facade;
Proxy; Composite; when a pattern is overkill in Python.

**What you must be able to do after this module:** implement Singleton, Factory,
Builder, Adapter, Decorator, and Facade in Python; recognise the problem each solves;
and say when Python's features make the classic version unnecessary.

---

## 14.1 What Are Design Patterns?

A **design pattern** is a reusable, named **solution template** for a common design
problem. The GoF book groups 23 patterns into three families:

![The three GoF families: Creational (how objects are made — Singleton, Factory, Builder, Prototype), Structural (how objects are composed — Adapter, Decorator, Facade, Proxy), Behavioral (how objects interact — Strategy, Observer).](images/m14_01_categories.png)

- **Creational** — object **creation** mechanisms (this module).
- **Structural** — how objects/classes are **composed** into larger structures
  (this module).
- **Behavioral** — how objects **communicate/interact** (Module 15).

> Patterns are a **vocabulary and a toolkit**, not a checklist. Use one when it
> solves a real problem — forcing patterns everywhere is itself an anti-pattern.

---

## 14.2 Singleton (creational)

**Intent:** ensure a class has **exactly one instance** and provide a global access
point (config, logger, connection pool).

![Two calls Cfg() both return the one shared Config instance, so a is b is True; in Python a module is already a singleton, so often no class is needed.](images/m14_02_singleton.png)

```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

a, b = Singleton(), Singleton()
print(a is b)      # True — same object
```

**Pythonic alternatives (usually better):**

- **A module** is already a singleton — import it and its state is shared. Often you
  need *no class at all*.
- A **`@lru_cache`-decorated factory** or a module-level instance.
- Overusing Singleton is controversial (hidden global state, hard to test); prefer
  **dependency injection** (Module 13) where possible.

---

## 14.3 Factory Method & Abstract Factory (creational)

**Intent:** create objects **without exposing the concrete class** to the client —
the client asks for *what* it wants; the factory decides *how* to build it.

![A client calls make('circle'); a Factory maps the key to the concrete Circle or Square class and returns an instance — the client depends on a key, not on the classes.](images/m14_03_factory.png)

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def draw(self) -> str: ...

class Circle(Shape):
    def draw(self): return "O"
class Square(Shape):
    def draw(self): return "[]"

def shape_factory(kind: str) -> Shape:        # Factory
    registry = {"circle": Circle, "square": Square}
    return registry[kind]()                   # client never names the class

s = shape_factory("circle")
```

- **Factory Method** — a method (often on a base class) that subclasses override to
  choose the product (`@classmethod from_...` in Module 3 is a Pythonic factory).
- **Abstract Factory** — a factory that produces **families** of related objects
  (e.g. `WindowsUIFactory` vs `MacUIFactory`, each making matching buttons/menus).

**Why:** decouples creation from use → supports OCP/DIP (swap products without
touching clients).

---

## 14.4 Builder (creational)

**Intent:** construct a **complex object step by step**, separating construction from
representation — great when there are many optional parameters.

![A fluent chain BurgerBuilder().bun().patty().build() assembles a complex object step by step, ending in a build() that returns the finished product.](images/m14_04_builder.png)

```python
class Burger:
    def __init__(self):
        self.parts = []

class BurgerBuilder:
    def __init__(self):
        self._burger = Burger()
    def bun(self):   self._burger.parts.append("bun");   return self   # fluent
    def patty(self): self._burger.parts.append("patty"); return self
    def cheese(self):self._burger.parts.append("cheese");return self
    def build(self): return self._burger

burger = BurgerBuilder().bun().patty().cheese().build()
```

**When to use:** avoids "telescoping constructors" (`__init__` with 10 optional args).
In Python, **keyword arguments + dataclasses** often replace Builder — reach for it
mainly when construction has **ordered steps or validation stages**.

---

## 14.5 Adapter (structural)

**Intent:** convert one interface into another so incompatible classes can work
together — the "power plug adapter" pattern.

![A Client wants .pay(); an Adapter exposes .pay() and internally calls a Legacy object's .charge(); the adapter bridges the mismatched interfaces.](images/m14_05_adapter.png)

```python
class LegacyPayment:                 # the class you can't change
    def charge(self, amount): return f"charged {amount}"

class PaymentAdapter:                # adapts it to the interface you want
    def __init__(self, legacy): self._legacy = legacy
    def pay(self, amount):           # the interface the client expects
        return self._legacy.charge(amount)

client_api = PaymentAdapter(LegacyPayment())
client_api.pay(100)                  # -> "charged 100"
```

**When:** integrating third-party/legacy code whose interface you can't (or
shouldn't) modify. Adapter uses **composition** to wrap and translate.

---

## 14.6 Decorator (structural) — pattern vs Python `@`

**Intent:** attach **new behaviour** to an object **dynamically**, by wrapping it in
another object with the **same interface** — a flexible alternative to subclassing.

![Coffee wrapped by +Milk, then +Sugar: each layer adds cost/behaviour around the object while keeping the same interface, without modifying Coffee.](images/m14_06_decorator.png)

```python
class Coffee:
    def cost(self): return 5
    def desc(self): return "coffee"

class MilkDecorator:                 # same interface, wraps a Coffee-like object
    def __init__(self, drink): self._drink = drink
    def cost(self): return self._drink.cost() + 2
    def desc(self): return self._drink.desc() + " + milk"

drink = MilkDecorator(Coffee())
print(drink.cost(), drink.desc())    # 7  'coffee + milk'
```

> **Don't confuse** the **Decorator pattern** (wrapping objects) with Python's
> **`@decorator` syntax** (wrapping functions/classes). They share a name and spirit
> (adding behaviour by wrapping), but Python's `@` is a language feature for
> functions/classes, while the GoF Decorator is an object-composition pattern.

---

## 14.7 Facade (structural)

**Intent:** provide a **single, simplified interface** to a complex subsystem —
hide the moving parts behind one easy method.

![A Client calls Facade.watch(); the Facade orchestrates the Amplifier, Projector, and Lights in the right order, hiding the subsystem's complexity.](images/m14_07_facade.png)

```python
class Amplifier:  
    def on(self): ...
class Projector:  
    def on(self): ...
class Lights:     
    def dim(self): ...

class HomeTheaterFacade:             # one simple door
    def __init__(self):
        self.amp, self.proj, self.lights = Amplifier(), Projector(), Lights()
    def watch_movie(self):
        self.lights.dim(); self.proj.on(); self.amp.on()   # orchestrates the mess

HomeTheaterFacade().watch_movie()   # client does ONE call
```

**When:** you want to expose a clean API over a complicated set of collaborating
classes (libraries, subsystems). Facade **reduces coupling** between client and
subsystem.

---

## 14.8 Proxy & Composite (structural)

![Proxy: Client -> Proxy -> Real object; the proxy is a controlled stand-in (lazy loading, access control, caching). Composite: a Folder contains Files and other Folders, letting you treat single and grouped objects uniformly in a tree.](images/m14_08_proxy_composite.png)

**Proxy** — a **stand-in** that controls access to a real object (same interface).
Uses: **lazy loading** (create the heavy object only when needed), **access
control**, **caching**, **remote** objects.

```python
class ExpensiveImage:
    def __init__(self, path): self._load(path)     # heavy
    def display(self): ...
class ImageProxy:
    def __init__(self, path): self.path, self._img = path, None
    def display(self):
        if self._img is None:
            self._img = ExpensiveImage(self.path)   # load on first use
        self._img.display()
```

**Composite** — compose objects into **tree structures** and treat **individual
objects and groups uniformly** (files/folders, UI widgets, org charts).

```python
class File:
    def __init__(self, size): self.size = size
    def total(self): return self.size
class Folder:
    def __init__(self): self.children = []
    def total(self): return sum(c.total() for c in self.children)  # same method!
```

*(Bridge, Flyweight are also structural — Bridge separates an abstraction from its
implementation; Flyweight shares common state across many objects to save memory.)*

---

## Module 14 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Implement a Singleton." | Overrides `__new__`. | Shows `__new__`/metaclass **and** notes Python alternatives (module, DI) + downsides of global state. |
| "Factory vs Builder?" | (blurs) | "Factory chooses/creates *which* object; Builder assembles *one complex* object step-by-step. In Python, kwargs/dataclasses often replace Builder." |
| "Adapter vs Decorator?" | "Both wrap." | "Adapter **changes** an interface to fit; Decorator **keeps** the interface and **adds** behaviour." |
| "Decorator pattern vs `@decorator`?" | (conflates) | "Same spirit (wrap to add behaviour); the pattern wraps objects, `@` is Python syntax for wrapping functions/classes." |

---

## Module 14 — Exam Mapping

- **GATE CS:** occasionally definitional (name the pattern/category).
- **SEBI / RBI IT:** rarely.
- **FAANG / LLD rounds:** very common — implement/choose patterns during design, and
  justify Pythonic simplifications.

---

## Module 14 — Common Mistakes & Misconceptions

- **Overusing Singleton** → hidden global state, test pain; prefer DI/modules.
- **Building a class Singleton where a module would do.**
- **Confusing Adapter (change interface) with Decorator (add behaviour) with Facade
  (simplify subsystem) with Proxy (control access)** — all "wrap", different intents.
- **Reaching for Builder** when keyword args/dataclasses suffice.
- **Pattern-itis** — applying patterns to trivial code; patterns add indirection.
- **Confusing the Decorator *pattern* with `@` syntax.**

---

## Module 14 — MCQs (with answers & explanations)

**Q1.** Ensuring only one instance exists is the:
a) Factory  b) **Singleton**  c) Builder  d) Proxy

<details><summary>Answer</summary>**b.** Singleton.</details>

**Q2.** Creating objects without naming their concrete class is the:
a) **Factory**  b) Adapter  c) Facade  d) Composite

<details><summary>Answer</summary>**a.** The factory hides which concrete class is instantiated.</details>

**Q3.** Converting an incompatible interface to the expected one is:
a) Decorator  b) **Adapter**  c) Proxy  d) Builder

<details><summary>Answer</summary>**b.** Adapter translates interfaces.</details>

**Q4.** Adding behaviour by wrapping while keeping the same interface is:
a) Adapter  b) **Decorator**  c) Facade  d) Singleton

<details><summary>Answer</summary>**b.** Decorator keeps the interface and layers behaviour.</details>

**Q5.** A single simplified entry point to a complex subsystem is:
a) Proxy  b) **Facade**  c) Composite  d) Builder

<details><summary>Answer</summary>**b.** Facade.</details>

**Q6.** A stand-in that adds lazy loading / access control is:
a) Adapter  b) Facade  c) **Proxy**  d) Builder

<details><summary>Answer</summary>**c.** Proxy controls access to the real object.</details>

**Q7.** Treating individual objects and groups uniformly (files/folders) is:
a) **Composite**  b) Decorator  c) Singleton  d) Adapter

<details><summary>Answer</summary>**a.** Composite models part-whole trees.</details>

**Q8.** In Python, the simplest Singleton is often:
a) a metaclass  b) `__new__`  c) **a module**  d) a global list

<details><summary>Answer</summary>**c.** Modules are singletons — shared state without a class.</details>

---

## Module 14 — Design/Practice Exercises (easy → hard)

1. **(easy)** Implement a Singleton `Logger` two ways: via `__new__` and via a module.
2. **(easy)** Write a `shape_factory(kind)` returning `Circle`/`Square`/`Triangle`.
3. **(medium)** Build a fluent `QueryBuilder` (`.select().where().build()`).
4. **(medium)** Adapt a third-party `XmlParser.parse_xml()` to a `Parser.parse()`
   interface via an Adapter.
5. **(hard)** Implement beverage pricing with Decorators (`Milk`, `Sugar`, `Whip`)
   over a base `Coffee`.
6. **(hard, interview)** Design a file-system size calculator using Composite, then
   add a caching Proxy over an expensive `total()`.

---

## Module 14 — Concept Review (one page)

**Design patterns** are named solutions to recurring problems, grouped into
**creational**, **structural**, and **behavioral**. **Creational:** **Singleton**
(one instance — but a Python **module** or DI is often better), **Factory** (create
objects by key without naming concrete classes → supports OCP/DIP), **Builder**
(assemble a complex object step-by-step — often replaced by kwargs/dataclasses), and
Prototype (clone). **Structural:** **Adapter** (convert an interface to fit),
**Decorator** (wrap to *add* behaviour, same interface — distinct from Python's `@`
syntax), **Facade** (one simple entry to a complex subsystem), **Proxy** (a
controlled stand-in for lazy loading/access/caching), and **Composite** (treat single
and grouped objects uniformly in a tree). Patterns give shared vocabulary and proven
structure — used where they solve a real problem, not applied reflexively (Python's
features often make the classic form unnecessary).

---

## Module 14 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Singleton | exactly one instance (Python: a module often suffices) |
| Factory | create objects by key, hide concrete class |
| Abstract Factory | create families of related objects |
| Builder | assemble a complex object step-by-step (fluent) |
| Adapter | convert one interface into another |
| Decorator (pattern) | wrap to add behaviour, same interface |
| Decorator vs `@` | object-wrapping pattern vs Python function/class syntax |
| Facade | one simple interface over a complex subsystem |
| Proxy | controlled stand-in (lazy/access/cache) |
| Composite | uniform treatment of leaf & group (tree) |
| Pattern families | Creational / Structural / Behavioral |
| Pattern risk | pattern-itis / needless indirection |

---

## Module 14 — Pattern Recognition

- **See "must have exactly one shared X"** → Singleton (or a module).
- **See a `if kind == ...: return SomeClass()` creation ladder** → Factory.
- **See a constructor with many optional params / staged build** → Builder.
- **See "third-party API doesn't match my interface"** → Adapter.
- **See "add features in combinations without subclass explosion"** → Decorator.
- **See "expose a simple API over a messy subsystem"** → Facade.
- **See "delay/guard/cache access to a heavy or remote object"** → Proxy.
- **See "part-whole hierarchy, treat both the same"** → Composite.

---

## Module 14 — Revision Notes / Mini Cheat Sheet

```
PATTERNS = named solutions. Families: Creational / Structural / Behavioral(M15).

CREATIONAL:
  Singleton  one instance (__new__/metaclass). Python: a MODULE is a singleton; prefer DI.
  Factory    build by key; hide concrete class -> OCP/DIP. (@classmethod = Pythonic factory)
  Abstract Factory  families of related objects.
  Builder    step-by-step fluent build. Python: kwargs/dataclasses often replace it.

STRUCTURAL:
  Adapter    CHANGE interface to fit (wrap + translate).
  Decorator  ADD behaviour, SAME interface (wrap). != Python @ syntax.
  Facade     ONE simple door to a complex subsystem.
  Proxy      controlled STAND-IN (lazy/access/cache/remote).
  Composite  tree; treat leaf & group uniformly.
  (Bridge = split abstraction/impl; Flyweight = share state to save memory.)

RULE: use a pattern to solve a REAL problem; avoid pattern-itis.
```

> **Next module:** **Module 15 — Design Patterns II (Behavioral).** We cover the
> patterns about *interaction*: **Strategy** (swap algorithms — often the answer that
> replaces inheritance), **Observer** (publish/subscribe), **Command**, **Iterator**
> (already in Module 7), **State**, **Template Method**, and **Chain of
> Responsibility** — each with a Pythonic take.

---

## Module 14 — Summary

**Design patterns** are proven, named solutions grouped into creational, structural,
and behavioral families. **Creational** patterns govern object creation —
**Singleton** (one instance; often a module in Python), **Factory** (create by key,
hide the class; supports OCP/DIP), and **Builder** (stepwise assembly; frequently
replaced by kwargs/dataclasses). **Structural** patterns compose objects — **Adapter**
(convert an interface), **Decorator** (wrap to add behaviour, same interface —
distinct from `@`), **Facade** (simplify a subsystem), **Proxy** (a controlled
stand-in), and **Composite** (uniform part-whole trees). Patterns give you shared
vocabulary and tested structure for design and LLD interviews — applied judiciously,
with awareness that Python's own features often make the classic version leaner.

> **You have mastered this module when** you can: implement Singleton, Factory,
> Builder, Adapter, Decorator, and Facade in Python; state the problem each solves;
> distinguish Adapter/Decorator/Facade/Proxy by intent; and identify when Python makes
> a pattern unnecessary.
