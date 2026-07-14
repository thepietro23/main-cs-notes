---
title: "Module 19 — Anti-patterns, Code Smells & Refactoring"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 19 — Anti-patterns, Code Smells & Refactoring

> **Why this module matters.**
> Knowing good design (pillars, SOLID, patterns) is half the job; the other half is
> **recognising bad design and fixing it safely**. Code reviews and interviews often
> ask you to *critique* code: spot the **god object**, the `if/elif` type ladder, the
> deep inheritance chain — and name the **refactoring** that cures each. This module
> gives you a vocabulary of **anti-patterns** and **code smells** plus the standard
> **refactoring moves**, all with Python examples. It's the practical capstone that
> ties Modules 13–18 together.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★       | ★           | ★★★★★       | ★★★★       |

**Most-asked concepts:** god object; spaghetti/deep inheritance (yo-yo); replace
conditional with polymorphism; common code smells + their cures; extract
method/class; composition over inheritance as a refactor; Python-specific smells
(mutable defaults, `__del__`, not using dataclasses); safe (test-backed) refactoring.

**What you must be able to do after this module:** name and recognise the major
anti-patterns/smells; apply the matching refactoring; explain "replace conditional
with polymorphism"; and describe how to refactor safely with tests.

---

## 19.1 Anti-patterns vs Code Smells

- **Anti-pattern** — a *commonly-used but counterproductive* design (a "solution"
  that causes more problems). Examples: **God Object**, **Spaghetti Code**, **Golden
  Hammer**, **Singleton abuse**, **Copy-paste programming**, **Lava Flow** (dead code
  nobody dares remove).
- **Code smell** — a *surface symptom* hinting at a deeper design problem. Not a bug,
  but a signal to look closer (Kent Beck / Martin Fowler).
- **Refactoring** — changing a program's **internal structure without changing its
  external behaviour**, to remove smells and improve design.

---

## 19.2 The God Object (the #1 anti-pattern)

A **God Object** knows too much and does too much — it violates **SRP** and becomes
a bottleneck for every change.

![A GodManager class doing UI + DB + auth + email + logging is decomposed into focused UserService, AuthService, and MailService — each with one responsibility.](images/m19_01_god_object.png)

```python
# ANTI-PATTERN: one class does everything
class AppManager:
    def parse_request(self): ...
    def query_db(self): ...
    def authenticate(self): ...
    def send_email(self): ...
    def render_html(self): ...        # any change touches this monster

# FIX: Extract Class — one responsibility each (SRP)
class RequestParser: ...
class UserRepository: ...
class Authenticator: ...
class Mailer: ...
```

**Cure:** **Extract Class** — split by responsibility; compose the pieces.

---

## 19.3 A Catalogue of Common Code Smells

![Common smells and cures: Long method -> Extract Method; Large class/God object -> Extract Class (SRP); Long parameter list -> Introduce Parameter Object; Primitive obsession -> value object/Enum; Feature envy -> move method to the data it uses; Duplicated code -> extract + reuse (DRY).](images/m19_02_smells_list.png)

| Smell | What it looks like | Cure |
|---|---|---|
| **Long method** | a function doing 5 things over 80 lines | **Extract Method** |
| **Large class / God object** | dozens of methods, many concerns | **Extract Class** (SRP) |
| **Long parameter list** | `f(a, b, c, d, e, f)` | **Introduce Parameter Object** / dataclass |
| **Primitive obsession** | passing `(amount, currency)` everywhere | a **value object** / Enum |
| **Feature envy** | a method mostly uses *another* object's data | **Move Method** to that object |
| **Data clumps** | the same group of fields travels together | bundle into a class |
| **Duplicated code** | copy-paste logic | **Extract** + reuse (DRY) |
| **Shotgun surgery** | one change forces edits in many places | consolidate responsibility |
| **Refused bequest** | subclass ignores/overrides most of the base | favour **composition** |
| **Message chains** | `a.b().c().d().e()` | **Hide Delegate** (Law of Demeter) |

---

## 19.4 Replace Conditional with Polymorphism (the key move)

A growing **`if/elif` ladder on a type** is a smell — it violates **OCP** (every new
type edits the ladder). Replace it with **subclasses overriding a method**.

![A smell — if t=='dog': bark / elif t=='cat': meow / elif ... — becomes Animal.speak() with Dog and Cat subclasses overriding it, so new types are added without editing existing code.](images/m19_03_replace_conditional.png)

```python
# SMELL: type-switch ladder (edit it for every new animal)
def speak(animal):
    if animal.type == "dog":  return "Woof"
    elif animal.type == "cat": return "Meow"
    # elif ... forever

# REFACTORED: polymorphism (add a subclass, touch nothing)
class Animal:
    def speak(self): raise NotImplementedError
class Dog(Animal):
    def speak(self): return "Woof"
class Cat(Animal):
    def speak(self): return "Meow"
```

This single refactor recurs constantly — in LLD it turns brittle policy ladders into
clean Strategy/subclass designs.

---

## 19.5 Deep Inheritance (Yo-Yo) → Composition

Tall inheritance chains (`D(C(B(A)))`) are fragile: a change high up ripples down,
and you "yo-yo" up and down the hierarchy to understand behaviour. This is the smell
**composition over inheritance** (Module 5) exists to fix.

![A deep chain A -> B(A) -> C(B) -> D(C) (fragile, hard to follow) is replaced by D composing swappable parts EngineA/EngineB (flat, swappable).](images/m19_04_deep_inheritance.png)

```python
# SMELL: deep, rigid hierarchy
class Vehicle: ...
class LandVehicle(Vehicle): ...
class Car(LandVehicle): ...
class ElectricCar(Car): ...          # behaviour scattered up 4 levels

# FIX: compose behaviours (Strategy-like)
class Car:
    def __init__(self, engine, transmission):
        self.engine = engine          # swap ElectricEngine / PetrolEngine at runtime
        self.transmission = transmission
```

Also called **refused bequest** when a subclass overrides away most of the parent —
a sign it shouldn't inherit at all.

---

## 19.6 Extract Class & Introduce Parameter Object

![Extract Class: a Person class holding name/email AND street/city/zip is split so Person has-a separate Address class holding the address fields.](images/m19_05_extract_class.png)

**Extract Class** — when a class has a **cohesive cluster** of fields/methods that
form their own concept, pull them into a new class.

```python
# BEFORE: address fields clutter Person
class Person:
    def __init__(self, name, email, street, city, zip): ...

# AFTER: Address is its own value/class; Person HAS-A Address
@dataclass
class Address:
    street: str; city: str; zip: str
@dataclass
class Person:
    name: str; email: str; address: Address
```

**Introduce Parameter Object** — a **long parameter list** becomes a single object
(often the same as Extract Class). `create_user(name, email, street, city, zip)` →
`create_user(user_data)`.

---

## 19.7 Primitive Obsession → Value Object

Passing bare primitives (`float amount`, `str currency`) everywhere scatters
validation and meaning. Wrap them in a **value object** with rules and behaviour.

![Primitive obsession — amount: float and currency: str scattered and unchecked — becomes a Money(amount, currency) value object with validation and an add() method.](images/m19_06_primitive_obsession.png)

```python
# SMELL: primitives everywhere, no validation, easy to mix up
def transfer(amount: float, currency: str): ...

# FIX: a value object encapsulates the rules
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
    def __post_init__(self):
        if self.amount < 0: raise ValueError("negative")
    def add(self, other):
        if self.currency != other.currency: raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

---

## 19.8 Python-Specific Smells

| Smell | Fix |
|---|---|
| **Mutable default argument** (`def f(x=[])`) | `None` sentinel (Module 2) |
| **Mutable class attribute** for per-object state | init in `__init__` (Module 3) |
| **`__del__` for cleanup** | context manager (Module 12) |
| **Java-style getters/setters** everywhere | public attrs → `@property` (Module 4) |
| **Hand-written `__init__/__repr__/__eq__`** boilerplate | `@dataclass` (Module 10) |
| **`if/elif isinstance(...)` ladders** | polymorphism / `singledispatch` (Module 6) |
| **`except: pass`** | catch specific, handle/log (Module 16) |
| **Deep inheritance / mixin soup** | composition (Module 5) |

---

## 19.9 Refactoring Safely

![Key refactoring moves: Extract Method/Class (break up long code), Replace conditional with polymorphism (kill type ladders), Introduce Parameter Object (bundle long arg lists), Replace inheritance with delegation (prefer composition), Rename/Inline (clarity).](images/m19_07_refactoring_moves.png)

Refactoring changes **structure, not behaviour** — so you need a safety net:

![Safe refactoring cycle: with tests passing, make one small behaviour-preserving change, re-run tests (stay green), repeat; refactoring changes structure, not behaviour.](images/m19_08_refactor_cycle.png)

1. **Have tests** that pin the current behaviour.
2. Make **one small, behaviour-preserving change**.
3. **Re-run tests** — they must stay green.
4. Repeat.

> **Golden rule:** **never mix refactoring with new features** in the same step. Get
> to green, refactor to green, *then* add the feature. Small steps keep you always a
> `Ctrl-Z` away from a working state.

---

## Module 19 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Critique this class." | "It's long." | Names the smell (**god object / feature envy / primitive obsession**) and the **specific refactoring** to fix it. |
| "This `if/elif` on type?" | "Add another branch." | "**Replace conditional with polymorphism** — subclasses override a method; supports OCP." |
| "Deep inheritance issues?" | (unsure) | "Fragile base class, yo-yo problem, refused bequest — refactor to **composition**." |
| "How do you refactor safely?" | "Carefully." | "Behaviour-preserving small steps backed by tests; never mix refactor with feature work." |

---

## Module 19 — Exam Mapping

- **GATE / PSU:** minimal; occasionally "what is refactoring / a code smell".
- **FAANG / backend / code review:** heavily practical — critique code, name smells,
  and propose refactorings live.

---

## Module 19 — Common Mistakes & Misconceptions

- **Thinking a smell is a bug** — it's a *hint*; judge in context (sometimes a long
  method is fine).
- **Refactoring without tests** — you can't prove behaviour was preserved.
- **Mixing refactoring with feature changes** — hides regressions.
- **Over-refactoring / pattern-itis** — adding abstraction the problem doesn't need.
- **Keeping a god object because "it works"** — it's a change bottleneck.
- **Chasing every smell** — prioritise ones that hurt change/readability now.

---

## Module 19 — MCQs (with answers & explanations)

**Q1.** A class that does far too much is a:
a) value object  b) **god object**  c) mixin  d) singleton

<details><summary>Answer</summary>**b.** God object — violates SRP; cure with Extract Class.</details>

**Q2.** A growing `if/elif` on an object's type should be refactored to:
a) a dict  b) **polymorphism (subclasses overriding a method)**  c) a metaclass  d) a global

<details><summary>Answer</summary>**b.** Replace conditional with polymorphism (supports OCP).</details>

**Q3.** Passing `(amount, currency)` everywhere is:
a) feature envy  b) **primitive obsession**  c) shotgun surgery  d) lava flow

<details><summary>Answer</summary>**b.** Wrap them in a value object (`Money`).</details>

**Q4.** A method that mostly uses another object's data has:
a) primitive obsession  b) **feature envy**  c) refused bequest  d) long method

<details><summary>Answer</summary>**b.** Move the method to the class whose data it uses.</details>

**Q5.** Refactoring is defined as changing:
a) behaviour, not structure  b) **structure, not behaviour**  c) both  d) neither

<details><summary>Answer</summary>**b.** Internal structure changes; external behaviour is preserved.</details>

**Q6.** A subclass that overrides away most of its parent's behaviour shows:
a) **refused bequest**  b) feature envy  c) god object  d) data clump

<details><summary>Answer</summary>**a.** Sign it shouldn't inherit — prefer composition.</details>

**Q7.** The cure for a long parameter list is:
a) more globals  b) **Introduce Parameter Object**  c) a metaclass  d) inheritance

<details><summary>Answer</summary>**b.** Bundle the params into an object/dataclass.</details>

**Q8.** The safe way to refactor is:
a) big rewrite  b) **small behaviour-preserving steps with tests green**  c) without tests  d) with new features

<details><summary>Answer</summary>**b.** Tiny steps, tests green, no feature mixing.</details>

---

## Module 19 — Design/Practice Exercises (easy → hard)

1. **(easy)** Identify three smells in a 50-line god class and name their cures.
2. **(easy)** Refactor an `if type == ...` payment ladder into polymorphic
   `PaymentMethod` subclasses.
3. **(medium)** Extract an `Address` class from a bloated `Customer`.
4. **(medium)** Replace a 6-parameter `create_order(...)` with a parameter object.
5. **(hard)** Turn a 4-level inheritance chain into a composition design and list what
   improved.
6. **(hard, interview)** Given messy code with a mutable default, `except: pass`, and a
   type ladder, refactor all three and explain each move.

---

## Module 19 — Concept Review (one page)

**Anti-patterns** are counterproductive designs (god object, spaghetti/deep
inheritance, golden hammer, singleton abuse); **code smells** are surface symptoms
(long method, large class, long parameter list, **primitive obsession**, feature
envy, duplicated code, refused bequest, message chains); **refactoring** changes
**structure without changing behaviour** to remove them. The signature moves:
**Extract Method/Class** (break up bloat, restore SRP), **Replace Conditional with
Polymorphism** (kill type ladders, honour OCP), **Introduce Parameter Object** (bundle
long arg lists), **Replace Inheritance with Delegation** (composition over deep
hierarchies), and wrapping loose primitives in **value objects**. Python adds its own
smells — mutable defaults, `__del__` cleanup, hand-rolled dunders, `except: pass` —
each with a known cure. Refactor **safely**: tests green, one small behaviour-
preserving change at a time, never mixing refactor with new features.

---

## Module 19 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Anti-pattern | common but counterproductive design |
| Code smell | surface symptom of a deeper design issue |
| Refactoring | change structure, not behaviour |
| God object cure | Extract Class (SRP) |
| `if/elif` type ladder cure | Replace Conditional with Polymorphism |
| Long parameter list cure | Introduce Parameter Object / dataclass |
| Primitive obsession cure | value object / Enum |
| Feature envy cure | Move Method to the data it uses |
| Deep inheritance cure | composition (delegation) |
| Refused bequest | subclass overrides away the base → don't inherit |
| Python smell examples | mutable default, `__del__` cleanup, `except: pass` |
| Safe refactoring | small steps, tests green, no feature mixing |

---

## Module 19 — Pattern Recognition

- **See one class doing everything** → god object → Extract Class.
- **See `if/elif` on a type field** → Replace Conditional with Polymorphism.
- **See `(amount, currency)` passed around** → value object.
- **See a method using another object's fields** → Move Method (feature envy).
- **See a 4-level class chain** → composition.
- **See copy-pasted logic** → extract + reuse.
- **See `def f(x=[])` / `except: pass`** → Python smell; apply the known cure.

---

## Module 19 — Revision Notes / Mini Cheat Sheet

```
ANTI-PATTERN = counterproductive design (God Object, Spaghetti, Golden Hammer,
               Singleton abuse, Copy-paste, Lava Flow).
CODE SMELL   = symptom (long method, large class, long param list, primitive obsession,
               feature envy, data clumps, duplicated code, shotgun surgery, refused bequest).
REFACTORING  = change STRUCTURE, not BEHAVIOUR.

CURES:
  god object / large class      -> Extract Class (SRP)
  long method                   -> Extract Method
  if/elif on type               -> Replace Conditional w/ Polymorphism (OCP)
  long parameter list           -> Introduce Parameter Object / dataclass
  primitive obsession           -> value object / Enum
  feature envy                  -> Move Method
  deep inheritance / refused bequest -> composition (delegation)
  message chains                -> Hide Delegate (Law of Demeter)

PYTHON SMELLS: mutable default (=None), __del__ cleanup (use with), hand dunders (dataclass),
  Java getters (@property), isinstance ladders (polymorphism/singledispatch), except: pass.

SAFE REFACTOR: tests green -> ONE small behaviour-preserving change -> re-run -> repeat.
               NEVER mix refactoring with new features.
```

> **Next module:** **Module 20 — Exam & Interview Mapping + Master Question Bank.** We
> consolidate the whole course into an exam/interview map and a large, graded question
> bank (conceptual, output-prediction, code, and design) with answers — your primary
> revision-and-drill resource.

---

## Module 19 — Summary

Great OOP means not only building good designs but **spotting and fixing bad ones**.
**Anti-patterns** (god object, deep inheritance, singleton abuse) and **code smells**
(long method/class, long parameter list, primitive obsession, feature envy, refused
bequest) are the recognisable failure modes, and each has a standard **refactoring**:
Extract Method/Class, **Replace Conditional with Polymorphism**, Introduce Parameter
Object, composition over inheritance, and value objects. Python contributes its own
smells (mutable defaults, `__del__` cleanup, hand-rolled dunders, `except: pass`) with
known cures. Above all, refactor **safely** — behaviour-preserving small steps backed
by tests, never mixed with feature work. This is the skill that turns code that
*works* into code that **lasts**.

> **You have mastered this module when** you can: name the major anti-patterns/smells
> on sight; apply the correct refactoring to each; explain "replace conditional with
> polymorphism"; and describe a safe, test-backed refactoring workflow.
