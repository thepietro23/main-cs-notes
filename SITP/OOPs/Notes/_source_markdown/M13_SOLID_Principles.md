---
title: "Module 13 — SOLID Principles"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 13 — SOLID Principles

> **Why this module matters.**
> So far you can *write* OOP. SOLID is how you write OOP that **survives change**.
> These five principles (coined by Robert C. Martin) are the single most-cited
> design framework in interviews and code reviews. They're not academic: each one
> fixes a concrete pain (the god class, the shotgun edit, the broken subtype, the
> fat interface, the un-testable dependency). And in Python they lean directly on
> the pillars you've built — **abstraction, polymorphism, composition** — often with
> **less ceremony** than in Java. Expect "tell me about SOLID / apply SRP here" in
> nearly every OOP design interview.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★      | ★★          | ★★★★★       | ★★★★★      |

**Most-asked concepts:** what each SOLID letter stands for + a one-line example;
SRP ("one reason to change"); OCP (extend without modifying); LSP (subtype
substitutability + the Penguin/Rectangle-Square examples); ISP; DIP + **dependency
injection**; how SOLID relates to the four pillars.

**What you must be able to do after this module:** name and define all five; give a
Python before/after for each; spot which principle a piece of bad code violates; and
apply DIP via constructor injection.

---

## 13.1 SOLID at a Glance

![The five SOLID principles: S Single Responsibility (one reason to change), O Open/Closed (open to extend, closed to modify), L Liskov Substitution (subtype usable as base), I Interface Segregation (many small interfaces), D Dependency Inversion (depend on abstractions).](images/m13_01_solid_overview.png)

| Letter | Principle | One line |
|---|---|---|
| **S** | Single Responsibility | a class should have **one reason to change** |
| **O** | Open/Closed | **open to extension, closed to modification** |
| **L** | Liskov Substitution | a subtype must be **usable wherever its base is** |
| **I** | Interface Segregation | prefer **many small interfaces** over one fat one |
| **D** | Dependency Inversion | depend on **abstractions**, not concretions |

---

## 13.2 S — Single Responsibility Principle (SRP)

**A class should have one, and only one, reason to change.** If a class does
parsing *and* validation *and* persistence *and* emailing, four different concerns
can force edits to it — and they'll step on each other.

![A god class that parses, validates, saves, and emails (many reasons to change) is split into focused Parser, Validator, and Repository classes, each with one job.](images/m13_02_srp.png)

```python
# VIOLATION: one class, many reasons to change
class Report:
    def parse(self, raw): ...
    def validate(self): ...
    def save_to_db(self): ...
    def email_to(self, addr): ...      # persistence, I/O, formatting all mixed

# SRP: one responsibility each
class ReportParser:     ...
class ReportValidator:  ...
class ReportRepository: ...            # each changes for exactly one reason
```

> **Test:** describe the class in one sentence *without* using "and". If you need
> "and", it likely has multiple responsibilities.

---

## 13.3 O — Open/Closed Principle (OCP)

**Software entities should be open for extension but closed for modification.** You
should add new behaviour by **adding code** (new subclass/strategy), not by editing
tested code with more `if`/`elif`.

![A Shape abstraction with area(); Circle, Square, and a NEW Triangle all subclass it, so total_area() gains support for a new shape without editing existing code.](images/m13_03_ocp.png)

```python
# VIOLATION: adding a shape means editing this function every time
def area(shape):
    if shape.type == "circle": ...
    elif shape.type == "square": ...
    # elif ... (edit forever)

# OCP: polymorphism — add a subclass, touch nothing existing
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Circle(Shape):   ...
class Triangle(Shape): ...            # NEW — total_area() below is untouched

def total_area(shapes): return sum(s.area() for s in shapes)
```

OCP is **polymorphism (Module 6) applied as a design rule**. The abstraction
(`Shape`) is the stable "closed" part; subclasses are the "open" extension points.

---

## 13.4 L — Liskov Substitution Principle (LSP)

**Objects of a subtype must be substitutable for their base type without breaking
the program.** A subclass must honour the base's **contract** — same expected
behaviour, no stricter inputs, no weaker outputs, no surprise exceptions.

![Code expecting a Bird that can fly works with Sparrow (flies) but breaks with Penguin, whose fly() cannot fulfil the contract — a Liskov violation.](images/m13_04_lsp.png)

```python
class Bird:
    def fly(self): ...

class Sparrow(Bird):
    def fly(self): return "flap flap"

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError   # VIOLATION: breaks code expecting Bird.fly()
```

The classic fixes: **model the hierarchy honestly** — e.g. split `Bird` into
`FlyingBird` / `FlightlessBird`, or use composition (`Bird` *has-a* movement
strategy). The famous **Rectangle/Square** example is another LSP trap: a `Square`
that inherits `Rectangle` breaks code that sets width and height independently.

> **Rule:** inheritance must be a true **is-a with behavioural compatibility**, not
> just shared attributes. If a subclass has to weaken/break a base method, it
> shouldn't inherit.

---

## 13.5 I — Interface Segregation Principle (ISP)

**Clients should not be forced to depend on methods they don't use.** Prefer several
small, role-specific interfaces over one big "do everything" interface.

![A fat interface with work + eat + sleep forces a robot to implement eat(); splitting into Workable, Eatable, and Sleepable lets each client implement only what it needs.](images/m13_05_isp.png)

```python
# VIOLATION: fat interface forces irrelevant methods
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...            # a RobotWorker has no business eating

# ISP: small, focused protocols/ABCs
class Workable(Protocol):
    def work(self) -> None: ...
class Eatable(Protocol):
    def eat(self) -> None: ...

class Human:  # implements both
    def work(self): ...
    def eat(self):  ...
class Robot:  # implements only Workable
    def work(self): ...
```

In Python, `Protocol`s (Module 11) make ISP cheap: define small structural
interfaces and let each class satisfy only the ones it needs.

---

## 13.6 D — Dependency Inversion Principle (DIP)

**High-level modules should not depend on low-level modules; both should depend on
abstractions.** Don't hard-wire a service to a concrete class — depend on an
interface, and let the concrete implementation be supplied.

![Bad: a Service depends directly on a concrete MySQLDb (tied to MySQL). Good: Service depends on a Database abstraction, and MySQL/Postgres implement it — the concrete detail is swappable.](images/m13_06_dip.png)

```python
# VIOLATION: high-level Service welded to a concrete database
class Service:
    def __init__(self):
        self.db = MySQLDatabase()      # can't swap; hard to test

# DIP: depend on an abstraction
class Database(ABC):
    @abstractmethod
    def save(self, data): ...

class MySQLDatabase(Database):    ...
class PostgresDatabase(Database): ...

class Service:
    def __init__(self, db: Database):   # depends on the ABSTRACTION
        self.db = db
```

### Dependency Injection — how DIP is applied

![Dependency injection: Service(db) receives its database from the caller, so you can swap MySQL, Postgres, or a Mock in tests — decoupled and testable.](images/m13_07_di.png)

**Dependency Injection (DI)** is the technique: the dependency is **passed in**
(constructor injection) rather than created inside. This makes code **testable** (inject
a mock) and **flexible** (swap implementations). It's the composition-over-inheritance
idea (Module 5) applied to collaborators.

```python
Service(MySQLDatabase())      # production
Service(MockDatabase())       # tests — no real DB needed
```

---

## 13.7 The Payoff — and SOLID ↔ the Four Pillars

![Non-SOLID code: one change ripples everywhere, fragile. SOLID code: changes are local, extend by adding, testable and flexible.](images/m13_08_solid_payoff.png)

SOLID isn't separate from the pillars — it's the pillars used with intent:

| Principle | Leans on |
|---|---|
| SRP | encapsulation (cohesion) |
| OCP | **polymorphism** + abstraction |
| LSP | **inheritance** done honestly |
| ISP | abstraction (small interfaces) |
| DIP | **abstraction + composition** (injection) |

> **Balance:** SOLID is guidance, not law. Over-applying it (an interface for every
> class, indirection everywhere) is its own anti-pattern (M19). Apply it where change
> is likely; keep simple things simple.

---

## Module 13 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Explain SOLID." | Lists the five words. | Defines each **with a one-line Python example** and the pain it fixes; connects OCP→polymorphism, DIP→injection. |
| "Apply SRP to this class." | (splits vaguely) | Identifies distinct reasons-to-change and extracts a class per concern. |
| "LSP example?" | "Subtype works as base." | Penguin/`fly()` or Square/Rectangle; explains the broken contract and the honest-hierarchy fix. |
| "DIP vs DI?" | (conflates) | "DIP = principle (depend on abstractions); DI = technique (pass dependencies in). DI enables DIP and testing." |

---

## Module 13 — Exam Mapping

- **GATE CS:** occasionally definitional (what SRP/OCP mean).
- **SEBI / RBI IT:** rarely, as software-engineering theory.
- **FAANG / LLD rounds:** heavily used — you'll be asked to *apply* SOLID while
  designing, and to critique code against it.

---

## Module 13 — Common Mistakes & Misconceptions

- **SRP = "one method"** — no; it's **one reason to change** (a class may have many
  cohesive methods).
- **OCP = "never edit code"** — you edit for bugs; OCP is about not editing for
  *new variations* you could add via extension.
- **LSP = "shares attributes"** — it's about **behavioural** substitutability, not
  data.
- **DIP = "use interfaces everywhere"** — it's about **direction** of dependency
  (toward abstractions), applied where it pays.
- **Over-engineering** — abstractions/injection for code that never varies (YAGNI).
- **Confusing DIP and DI** — principle vs technique.

---

## Module 13 — MCQs (with answers & explanations)

**Q1.** "A class should have one reason to change" is:
a) OCP  b) **SRP**  c) LSP  d) DIP

<details><summary>Answer</summary>**b.** Single Responsibility Principle.</details>

**Q2.** Adding a new shape by writing a subclass, not editing `total_area()`, follows:
a) SRP  b) **OCP**  c) ISP  d) LSP

<details><summary>Answer</summary>**b.** Open for extension, closed for modification.</details>

**Q3.** A `Penguin(Bird)` whose `fly()` raises breaks:
a) SRP  b) OCP  c) **LSP**  d) ISP

<details><summary>Answer</summary>**c.** It's not substitutable for `Bird` — a Liskov violation.</details>

**Q4.** Splitting a fat `Worker` interface into `Workable`/`Eatable` follows:
a) DIP  b) **ISP**  c) SRP  d) OCP

<details><summary>Answer</summary>**b.** Interface Segregation Principle.</details>

**Q5.** `Service(db: Database)` receiving a `Database` abstraction follows:
a) SRP  b) LSP  c) **DIP**  d) ISP

<details><summary>Answer</summary>**c.** Depend on an abstraction, not a concrete class.</details>

**Q6.** Dependency Injection is:
a) a principle  b) **a technique to supply dependencies from outside**  c) a pattern only for DBs  d) inheritance

<details><summary>Answer</summary>**b.** It's how DIP is realised (e.g. constructor injection).</details>

**Q7.** OCP is most directly enabled by:
a) encapsulation  b) **polymorphism**  c) `__slots__`  d) metaclasses

<details><summary>Answer</summary>**b.** Overriding/duck-typing lets you extend without modifying callers.</details>

**Q8.** The Rectangle/Square problem illustrates:
a) SRP  b) OCP  c) **LSP**  d) DIP

<details><summary>Answer</summary>**c.** A `Square` subtype breaks code relying on `Rectangle`'s width/height contract.</details>

---

## Module 13 — Design/Practice Exercises (easy → hard)

1. **(easy)** Identify the responsibilities in a `User` class that logs in, sends
   email, and writes to a DB; split it.
2. **(easy)** Refactor an `area()` function with an `if/elif` type ladder into an OCP
   design with `Shape` subclasses.
3. **(medium)** Fix an LSP violation where `Square(Rectangle)` breaks a resize test.
4. **(medium)** Split a fat `Machine` interface (print/scan/fax) using ISP so a
   simple printer isn't forced to fax.
5. **(hard)** Apply DIP + DI to a `NotificationService` so it can send via Email, SMS,
   or a Mock, chosen by the caller.
6. **(hard, interview)** Given a 60-line "god" class, refactor it against all five
   SOLID principles and explain each change.

---

## Module 13 — Concept Review (one page)

**SOLID** is five design principles for change-resilient OOP. **SRP**: a class should
have **one reason to change** (split mixed concerns). **OCP**: **open to extension,
closed to modification** — add behaviour via new subclasses/strategies (polymorphism)
rather than editing tested code. **LSP**: a **subtype must be substitutable** for its
base without breaking the base's **behavioural contract** (Penguin/`fly`,
Square/Rectangle) — model hierarchies honestly. **ISP**: prefer **many small, focused
interfaces** so clients depend only on what they use (cheap in Python via
`Protocol`s). **DIP**: **depend on abstractions, not concretions**, realised through
**Dependency Injection** (pass collaborators in) for testability and flexibility.
SOLID is the four pillars applied with intent — powerful, but to be applied where
change is likely, not everywhere (avoid over-engineering).

---

## Module 13 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| S | Single Responsibility — one reason to change |
| O | Open/Closed — extend without modifying |
| L | Liskov Substitution — subtype usable as base |
| I | Interface Segregation — small, focused interfaces |
| D | Dependency Inversion — depend on abstractions |
| OCP enabled by | polymorphism + abstraction |
| LSP is about | behavioural substitutability (not shared data) |
| Classic LSP examples | Penguin/`fly`, Square/Rectangle |
| DIP vs DI | principle vs technique (inject dependencies) |
| ISP in Python | small `Protocol`s |
| SRP test | describe the class without "and" |
| SOLID risk | over-engineering / needless abstraction |

---

## Module 13 — Pattern Recognition

- **See a class described with "and…and…"** → SRP; split it.
- **See a growing `if/elif` on a type field** → OCP; use polymorphism.
- **See a subclass that overrides a method to raise/no-op** → LSP smell; rethink the
  hierarchy.
- **See classes implementing methods they leave empty** → ISP; split the interface.
- **See `self.x = ConcreteThing()` inside a class** → DIP; inject an abstraction.
- **See "hard to unit test because of a real DB/HTTP call"** → DI a mock.

---

## Module 13 — Revision Notes / Mini Cheat Sheet

```
SOLID = maintainable OOP.
S  Single Responsibility  one reason to change (split mixed concerns; no "and").
O  Open/Closed            extend via subclass/strategy; don't edit tested code (polymorphism).
L  Liskov Substitution    subtype substitutable for base; honour the CONTRACT.
                          smells: Penguin.fly() raises; Square(Rectangle).
I  Interface Segregation  many small interfaces; clients depend only on what they use.
D  Dependency Inversion   depend on ABSTRACTIONS not concretions.
                          realise via Dependency Injection (pass collaborators in).

MAP: SRP->cohesion/encapsulation, OCP->polymorphism, LSP->honest inheritance,
     ISP->small abstractions, DIP->abstraction+composition (injection).
BALANCE: apply where change is likely; over-abstracting is its own anti-pattern (M19).
```

> **Next module:** **Module 14 — Design Patterns I (Creational & Structural).** With
> SOLID as the "why", patterns are proven "how"s. We'll cover **creational** patterns
> (Singleton, Factory, Builder, Prototype) and **structural** patterns (Adapter,
> Decorator, Facade, Proxy, Composite) — each with a Pythonic implementation and a
> note on when Python's features make the classic version unnecessary.

---

## Module 13 — Summary

**SOLID** — **S**ingle Responsibility, **O**pen/Closed, **L**iskov Substitution,
**I**nterface Segregation, **D**ependency Inversion — is the canonical framework for
OOP that **absorbs change gracefully**. SRP keeps classes cohesive; OCP uses
**polymorphism** so new variations are added, not edited in; LSP demands **honest,
behaviour-compatible** subtyping; ISP favours **small interfaces**; and DIP points
dependencies at **abstractions**, applied through **Dependency Injection** for
testable, swappable code. These principles are the four pillars wielded deliberately —
and knowing them, with crisp Python examples and the ability to *apply* them under
questioning, is central to every serious OOP and low-level-design interview.

> **You have mastered this module when** you can: define all five principles with a
> Python example each; identify which principle a bad snippet violates; refactor a
> god class against SOLID; and apply DIP via constructor injection to make code
> testable.
