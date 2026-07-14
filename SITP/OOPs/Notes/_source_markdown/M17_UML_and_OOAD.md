---
title: "Module 17 — UML & Object-Oriented Analysis and Design (OOAD)"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 17 — UML & Object-Oriented Analysis and Design (OOAD)

> **Why this module matters.**
> Before you write classes, you **model** them — and the shared language for that is
> **UML class diagrams**. In an LLD interview you'll sketch classes and their
> relationships on a whiteboard; getting the **relationship arrows** right
> (inheritance vs composition vs association vs dependency) signals design maturity.
> This module teaches you to **read and draw** UML, notate every relationship, use
> **multiplicity**, and go from a **problem statement to a class model** — the direct
> bridge into Module 18's full LLD problems.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★★★     | ★★          | ★★★         | ★★★★★      |

**Most-asked concepts:** UML class box (visibility `+`/`-`/`#`); the six
relationships (association, aggregation, composition, generalization/inheritance,
realization, dependency) + their arrows; **aggregation vs composition** notation;
**multiplicity**; deriving classes from requirements (nouns/verbs).

**What you must be able to do after this module:** read/draw a UML class diagram;
pick and notate the correct relationship; label multiplicity; and turn a short
requirements paragraph into a class model.

---

## 17.1 The UML Class Box

A class is drawn as a **three-compartment box**: **name**, **attributes**, **methods**.
Visibility is marked with symbols.

![A UML class box for BankAccount with three compartments: name (BankAccount), attributes (- balance: float, + owner: str), methods (+ deposit(amt): None, # _validate(): bool); + public, - private, # protected.](images/m17_01_class_box.png)

| Symbol | Visibility |
|---|---|
| `+` | public |
| `-` | private |
| `#` | protected |
| `~` | package |

Attributes: `visibility name: Type`. Methods: `visibility name(params): ReturnType`.
(In Python, "private/protected" are conventions — Module 4 — but UML still uses the
symbols to express *intent*.)

---

## 17.2 The Six Relationships

![The six UML relationships from loosest to strongest: Association (uses/knows, plain line), Aggregation (has-a weak, hollow diamond), Composition (owns-a strong, filled diamond), Inheritance (is-a, hollow triangle), Realization (implements interface, dashed+triangle), Dependency (temporarily uses, dashed arrow).](images/m17_02_relationships.png)

| Relationship | Meaning | Notation |
|---|---|---|
| **Dependency** | temporarily uses (e.g. a parameter) | dashed arrow `- - ->` |
| **Association** | a lasting link (a stored reference) | solid line |
| **Aggregation** | has-a, **weak** ownership | **hollow** diamond ◇ |
| **Composition** | owns-a, **strong** ownership | **filled** diamond ◆ |
| **Generalization** | is-a (inheritance) | solid line + **hollow triangle** ▷ |
| **Realization** | implements an interface | **dashed** line + hollow triangle |

---

## 17.3 Generalization vs Realization

![Generalization: Dog inherits Animal via a solid line + hollow triangle (is-a). Realization: Circle implements the <<Drawable>> interface via a dashed line + hollow triangle (implements).](images/m17_03_inheritance_realization.png)

- **Generalization (inheritance)** — a subclass **is-a** superclass. **Solid** line,
  hollow triangle pointing at the parent. (Python: `class Dog(Animal)`.)
- **Realization** — a class **implements** an interface/ABC. **Dashed** line, hollow
  triangle pointing at the interface. (Python: implementing a `Protocol`/ABC.)

The triangle always points **to the more abstract** end (the parent/interface).

---

## 17.4 Aggregation vs Composition (the arrow that trips people)

![Aggregation: Team has Players via a hollow diamond on the Team end (shared, independent parts). Composition: House has Rooms via a filled diamond on the House end (owned parts that die with the whole).](images/m17_04_agg_comp.png)

- **Aggregation (◇ hollow)** — the whole **has** parts that can **exist
  independently** and be shared. `Team` ◇— `Player` (players outlive teams).
- **Composition (◆ filled)** — the whole **owns** parts whose **lifecycle it
  controls**; parts die with the whole. `House` ◆— `Room`.

**The diamond sits on the WHOLE** (the container), pointing to the part. (Recall
Module 5's Python examples — passing parts in = aggregation; creating/owning them =
composition.)

---

## 17.5 Multiplicity

Each association end can carry a **multiplicity** — how many objects participate.

![An Order—LineItem association labelled 1 on the Order end and 1..* on the LineItem end: one Order has one-or-more LineItems. Legend: 1 (exactly one), 0..1 (optional), * (many), 1..* (one or more).](images/m17_05_multiplicity.png)

| Notation | Meaning |
|---|---|
| `1` | exactly one |
| `0..1` | optional (zero or one) |
| `*` or `0..*` | many (zero or more) |
| `1..*` | one or more |
| `2..5` | a specific range |

Example: `Order (1) —— (1..*) LineItem` means "an order has at least one line item;
each line item belongs to exactly one order."

---

## 17.6 Dependency vs Association

![Dependency (dashed arrow): Order uses PriceService transiently, e.g. as a method parameter. Association (solid line): Customer has a lasting link to Address, e.g. a stored field.](images/m17_06_dependency_assoc.png)

- **Dependency (dashed)** — a **transient** use: the class uses another **inside a
  method** (as a parameter, local, or return) but doesn't keep a reference.
- **Association (solid)** — a **structural, lasting** link: the class **stores** a
  reference (an attribute) to the other.

```python
class Order:
    def total(self, price_service):    # DEPENDENCY: uses it, doesn't store it
        return price_service.calc(self)

class Customer:
    def __init__(self, address):
        self.address = address         # ASSOCIATION: stores the reference
```

---

## 17.7 From Requirements to a Class Model (OOAD)

**Object-Oriented Analysis and Design** turns a problem statement into classes. The
starting heuristic (Module 1): **nouns → classes/attributes; verbs → methods/
associations.**

![The sentence 'A member borrows a book from the library' yields nouns Member/Book/Library (classes) and the verb 'borrows' (a method or association); then assign responsibilities and draw relationships.](images/m17_07_reqs_to_model.png)

**Process:**

1. **Find candidate classes** — the important **nouns** (Member, Book, Library).
2. **Find attributes** — nouns describing a thing (a book's `title`, `isbn`).
3. **Find behaviour** — the **verbs** (`borrow`, `return`) → methods.
4. **Find relationships** — who owns/uses/knows whom → association/aggregation/
   composition.
5. **Assign responsibilities** — each class owns the data and behaviour it's best
   placed to handle (high cohesion, low coupling).
6. **Add multiplicity** and refine (apply SOLID, Module 13).

> **Entities vs value objects:** an **entity** has identity that persists (a `User`
> with an id); a **value object** is defined by its values and is usually immutable
> (a `Money`, a `Point`) — model value objects as `frozen` dataclasses (Module 10).

---

## 17.8 A Worked Class Diagram

![A small library class diagram: Library composes Books (filled diamond) and is associated with Members; a Loan connects a Book (1..*) with a Member (1) for a period.](images/m17_08_full_example.png)

Reading the diagram:

- **Library ◆— Book** — composition: the library owns its book copies.
- **Library —— Member** — association: members are linked to, not owned by, the
  library.
- **Loan** — an **association class** connecting a `Book` and a `Member` with loan
  data (dates). Loans have a **1..\*** / **1** multiplicity to books/members.

```python
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Book:    title: str; isbn: str
@dataclass
class Member:  name: str; member_id: str
@dataclass
class Loan:    book: Book; member: Member; due: date
@dataclass
class Library:
    books: list[Book] = field(default_factory=list)   # composition
    loans: list[Loan] = field(default_factory=list)
```

*(Other UML diagrams exist — **use-case** (actors vs features), **sequence**
(message order over time), **state** (Module 15's State pattern) — but the **class
diagram** is the one you draw most in OOP/LLD interviews.)*

---

## Module 17 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Aggregation vs composition in UML?" | "Diamonds." | "Hollow diamond = aggregation (parts independent/shared); filled = composition (parts owned, die with the whole); diamond sits on the whole." |
| "Association vs dependency?" | (blurs) | "Association = stored, lasting link (attribute); dependency = transient use (parameter/local); solid vs dashed." |
| "How do you model X?" | (jumps to code) | Extracts nouns→classes, verbs→methods, identifies relationships + multiplicity, assigns responsibilities (cohesion/coupling), then codes. |
| "Entity vs value object?" | (unaware) | "Entity has persistent identity (id); value object is defined by value and usually immutable (frozen dataclass)." |

---

## Module 17 — Exam Mapping

- **GATE CS:** UML relationship notation; class diagram reading; multiplicity.
- **SEBI / RBI IT:** basic UML terms.
- **FAANG / LLD rounds:** you'll **draw** class diagrams and be judged on correct
  relationships and responsibility assignment.

---

## Module 17 — Common Mistakes & Misconceptions

- **Confusing aggregation and composition diamonds** (hollow vs filled; lifecycle).
- **Putting the diamond on the part** instead of the whole.
- **Using inheritance where composition fits** (Module 5) — modelled as a triangle
  when it should be a diamond/line.
- **Association vs dependency** — storing a reference (association) vs using in a
  method (dependency).
- **Over-modelling** — a diagram with every getter/setter; show what matters.
- **Triangle pointing the wrong way** — it points to the **parent/interface**.

---

## Module 17 — MCQs (with answers & explanations)

**Q1.** A **filled** diamond denotes:
a) aggregation  b) **composition**  c) dependency  d) inheritance

<details><summary>Answer</summary>**b.** Filled diamond = composition (owned parts).</details>

**Q2.** Inheritance is shown by:
a) dashed arrow  b) **solid line + hollow triangle**  c) filled diamond  d) plain line

<details><summary>Answer</summary>**b.** Generalization: solid line, hollow triangle to the parent.</details>

**Q3.** `1..*` means:
a) exactly one  b) zero or one  c) **one or more**  d) zero or more

<details><summary>Answer</summary>**c.** At least one.</details>

**Q4.** A **dashed** line with a hollow triangle means:
a) dependency  b) association  c) **realization (implements interface)**  d) aggregation

<details><summary>Answer</summary>**c.** Realization — implementing an interface/ABC.</details>

**Q5.** Storing another object as an attribute is best shown as:
a) dependency  b) **association**  c) realization  d) nothing

<details><summary>Answer</summary>**b.** A lasting structural link = association.</details>

**Q6.** In OOAD, nouns typically map to:
a) methods  b) **classes/attributes**  c) loops  d) exceptions

<details><summary>Answer</summary>**b.** Nouns → classes/attributes; verbs → methods.</details>

**Q7.** The diamond in aggregation/composition sits on:
a) the part  b) **the whole (container)**  c) both ends  d) neither

<details><summary>Answer</summary>**b.** On the whole, pointing to the part.</details>

**Q8.** A value object is best characterised as:
a) has a persistent id  b) **defined by its values, usually immutable**  c) always mutable  d) a metaclass

<details><summary>Answer</summary>**b.** E.g. a `Money`/`Point` modelled as a frozen dataclass.</details>

---

## Module 17 — Design/Practice Exercises (easy → hard)

1. **(easy)** Draw a UML class box for a `Car` with `brand`, `speed`, `drive()`, and
   correct visibility symbols.
2. **(easy)** Name the notation for each: is-a, owns-a, has-a (weak), implements,
   transient use.
3. **(medium)** Model "A playlist contains many songs; a song can be in many
   playlists" — pick the relationship and multiplicity.
4. **(medium)** From "A customer places orders; each order has line items and one
   shipping address," draw the class diagram.
5. **(hard)** Model a parking lot at class-diagram level (Vehicle, Spot, Ticket, Lot)
   with correct relationships and multiplicity.
6. **(hard, interview)** Given a two-paragraph spec, produce a class diagram and
   justify each aggregation/composition/association choice.

---

## Module 17 — Concept Review (one page)

**UML class diagrams** are the shared language for modelling OOP. A class is a
**three-compartment box** (name, attributes, methods) with visibility markers
(`+`/`-`/`#`). Six **relationships**, from loosest to strongest: **dependency**
(dashed arrow — transient use), **association** (solid line — a stored, lasting
link), **aggregation** (hollow diamond — weak, shared ownership), **composition**
(filled diamond — strong ownership; parts die with the whole; diamond on the whole),
**generalization/inheritance** (solid line + hollow triangle — is-a), and
**realization** (dashed line + triangle — implements an interface). **Multiplicity**
(`1`, `0..1`, `*`, `1..*`) labels each end. **OOAD** turns requirements into a model:
**nouns → classes/attributes, verbs → methods/associations**, then assign
responsibilities (high cohesion, low coupling), add multiplicity, and refine with
SOLID. Distinguish **entities** (persistent identity) from **value objects** (defined
by value, immutable).

---

## Module 17 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Class box compartments | name / attributes / methods |
| Visibility symbols | `+` public, `-` private, `#` protected |
| Dependency notation | dashed arrow (transient use) |
| Association notation | solid line (stored link) |
| Aggregation notation | hollow diamond ◇ (weak, shared) |
| Composition notation | filled diamond ◆ (owned, dies with whole) |
| Inheritance notation | solid line + hollow triangle (is-a) |
| Realization notation | dashed line + hollow triangle (implements) |
| Diamond sits on | the whole (container) |
| Multiplicity examples | 1, 0..1, *, 1..* |
| OOAD heuristic | nouns → classes/attrs; verbs → methods |
| Entity vs value object | persistent id vs value-defined/immutable |

---

## Module 17 — Pattern Recognition

- **See "X owns Y; Y dies with X"** → composition (filled diamond).
- **See "X has Y; Y lives independently"** → aggregation (hollow diamond).
- **See "X is a kind of Y"** → generalization (triangle).
- **See "X implements interface I"** → realization (dashed + triangle).
- **See "X uses Y only inside a method"** → dependency (dashed arrow).
- **See a requirements paragraph** → extract nouns/verbs → classes/methods.

---

## Module 17 — Revision Notes / Mini Cheat Sheet

```
CLASS BOX: [Name | attributes | methods]; visibility + public / - private / # protected.
  attr:  vis name: Type      method: vis name(params): ReturnType

RELATIONSHIPS (loose -> strong):
  Dependency    dashed arrow      transient use (parameter/local)
  Association   solid line        stored, lasting link (attribute)
  Aggregation   hollow diamond ◇  has-a, weak, parts independent/shared
  Composition   filled diamond ◆  owns-a, parts die with whole (diamond on WHOLE)
  Generalization solid + hollow triangle ▷   is-a (inheritance)
  Realization   dashed + hollow triangle     implements interface/ABC
  (triangle/diamond point to the MORE ABSTRACT / WHOLE end)

MULTIPLICITY: 1 | 0..1 | * (0..*) | 1..* | 2..5.
OOAD: nouns->classes/attrs, verbs->methods/associations; assign responsibilities
      (high cohesion, low coupling); add multiplicity; refine with SOLID.
Entity (persistent id) vs Value object (value-defined, immutable -> frozen dataclass).
```

> **Next module:** **Module 18 — Low-Level Design (LLD): FAANG Systems.** We put it
> all together on the interview's marquee question type: designing real systems
> (parking lot, elevator, deck of cards, rate limiter) from requirements to a class
> model to Python code — applying pillars, SOLID, patterns, and UML end to end.

---

## Module 17 — Summary

**UML class diagrams** are how you model and communicate OOP designs. Classes are
**three-compartment boxes** with visibility markers; their **relationships** —
**dependency** (dashed, transient), **association** (solid, stored link),
**aggregation** (hollow diamond, weak ownership), **composition** (filled diamond,
strong ownership), **generalization** (triangle, is-a), and **realization** (dashed +
triangle, implements) — capture how objects connect, refined with **multiplicity**.
**OOAD** derives a model from requirements by turning **nouns into classes** and
**verbs into methods**, assigning responsibilities for cohesion and low coupling, and
distinguishing **entities** from **value objects**. This modelling fluency is exactly
what you'll deploy — on a whiteboard — in the low-level-design interview.

> **You have mastered this module when** you can: draw a correct UML class box;
> choose and notate the right relationship (and put diamonds/triangles the right way
> round); label multiplicity; and convert a requirements paragraph into a class
> model.
