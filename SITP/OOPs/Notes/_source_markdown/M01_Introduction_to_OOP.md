---
title: "Module 1 — Introduction to Object-Oriented Programming"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Introduction to Object-Oriented Programming

> **Why this module comes first.**
> Before we write a single `class`, we must answer three questions that trip up
> almost everyone: *What problem does OOP actually solve? Why did programmers
> invent it? And when should I NOT use it?* If you skip this, you end up writing
> "Java-style" classes for everything — wrapping one function in a class, making
> getters for everything — which is *cargo-cult OOP*. This module builds the
> mental model from first principles so that every later feature (inheritance,
> polymorphism, dunder methods, metaclasses) feels like an obvious answer to a
> real problem, not a rule to memorise.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★★★     | ★★★★        | ★★★★        | ★★★★★      |

**Most-asked concepts:** the **four pillars** (Encapsulation, Abstraction,
Inheritance, Polymorphism) and one-line definitions of each; **class vs object**;
**procedural vs OOP** (with a code example); **why OOP** (the four benefits);
"is everything in Python an object?"; **message passing** (`obj.method()`); and
the classic **"model this real-world thing as a class"** design opener.

**What you must be able to do after this module:** explain in plain English what
an object *is* (identity + state + behaviour), rewrite a small procedural program
in OOP style and justify *why*, name and define the four pillars with a concrete
example each, and decide out loud whether a given problem even *deserves* classes.

---

## 1.1 What Is a "Paradigm"? (setting the stage)

A **programming paradigm** is a *style* of structuring code — a set of ideas about
how to organise data and instructions. It is not a language; one language (like
Python) can support several paradigms.

![A tree of programming paradigms: imperative splits into procedural and object-oriented; declarative into functional and logic. OOP is an imperative style.](images/m01_01_paradigms.png)

The two big families:

- **Imperative** — you write *how* to do something, step by step, changing state
  as you go. Sub-styles: **procedural** (organise around *procedures/functions*)
  and **object-oriented** (organise around *objects*).
- **Declarative** — you describe *what* you want and let the system figure out how.
  Sub-styles: **functional** (Haskell, and Python's `map`/`filter`) and **logic**
  (Prolog).

> **Key point:** OOP is a way to **organise** an imperative program around *objects*
> — bundles of data and the operations on that data. Python is **multi-paradigm**:
> you can write procedural scripts, functional pipelines, and full OOP — often in
> the same file.

---

## 1.2 The Problem OOP Solves (first principles)

Let's *feel* the problem before we name the solution. Imagine a tiny banking
program written **procedurally** (functions + loose data):

```python
# Procedural style — data and functions live apart
balance = 1000          # just a global number

def deposit(amount):
    global balance
    balance += amount

def withdraw(amount):
    global balance
    balance -= amount   # BUG WAITING TO HAPPEN: no overdraft check enforced

deposit(500)
balance = -99999        # <-- ANYONE can corrupt the data directly. Nothing stops this.
```

Two accounts? Now you need `balance1`, `balance2`, or a dict, and *every* function
must be told which account it operates on. Ten accounts, each with an owner, a
currency, and an interest rate? The loose variables explode and nothing guarantees
the rules (no negative balance) are ever applied. **The data and the rules that
protect it are not glued together.**

![Procedural keeps data and functions apart so anything can mutate the data; OOP bundles state and behaviour into one guarded unit.](images/m01_02_procedural_vs_oop.png)

Now the **object-oriented** version:

```python
# OOP style — data + the rules that protect it live together
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner          # state
        self._balance = balance     # "_" hints: internal, don't touch directly

    def deposit(self, amount):      # behaviour
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:  # the RULE is enforced HERE, always
            raise ValueError("insufficient funds")
        self._balance -= amount

    def balance(self):
        return self._balance

acc = BankAccount("Nidhi", 1000)
acc.deposit(500)
print(acc.balance())                # 1500
# acc._balance = -99999   <-- possible, but clearly marked as "off-limits"; the
#                             normal API (withdraw) can never make it negative.
```

Each `BankAccount` object carries **its own** balance, and the only *intended* way
to change it goes through methods that **enforce the rules**. Ten accounts? Ten
objects — each self-contained. This is the whole point of OOP.

**The four benefits (exam-ready):**

1. **Modularity** — each object is a self-contained unit; fix one class without
   breaking others.
2. **Reusability** — reuse a class in many programs; extend it via inheritance.
3. **Maintainability** — rules live in one place, so bugs have one home.
4. **Data protection (encapsulation)** — invariants ("balance never negative")
   are guarded by the object, not by discipline.

---

## 1.3 Class vs Object (the single most important distinction)

A **class** is a **blueprint / template** — it describes *what* attributes and
methods a kind of thing has, but is not itself a thing. An **object** (or
**instance**) is a *concrete thing built from that blueprint*, with its **own
copy of the data**.

![A single class Car acts as a blueprint from which many independent car objects are instantiated, each with its own data.](images/m01_03_class_vs_object.png)

Analogy: the class is the **architect's blueprint** for a house; the objects are
the **actual houses** built from it. One blueprint → many houses, each painted a
different colour, each with its own furniture.

```python
class Car:                      # the blueprint
    def __init__(self, brand):
        self.brand = brand
        self.speed = 0

car1 = Car("Tesla")             # an object (instance)
car2 = Car("BMW")               # another, fully independent object
car1.speed = 80
print(car1.speed, car2.speed)   # 80 0  -> separate state, as expected
print(type(car1))               # <class '__main__.Car'>
print(isinstance(car1, Car))    # True
```

> **Interview one-liner:** *"A class is a definition; an object is an instance of
> that definition living in memory with its own state."*

---

## 1.4 Anatomy of an Object: Identity, State, Behaviour

Every object, in any OO language, has three facets. In Python this is literally
true and inspectable:

![An object has an identity (its id in memory), state (its attribute values), and behaviour (its methods).](images/m01_04_object_anatomy.png)

| Facet | Meaning | Python |
|---|---|---|
| **Identity** | *which* object it is (unique, unchanging) | `id(obj)` / the `is` operator |
| **State** | *what it currently knows* (data) | its attributes, e.g. `obj.balance` |
| **Behaviour** | *what it can do* (operations) | its methods, e.g. `obj.deposit()` |

```python
acc = BankAccount("Nidhi", 1000)
print(id(acc))          # identity: e.g. 140234... (address-like, unique)
print(acc.owner)        # state: 'Nidhi'
acc.deposit(500)        # behaviour: changes state via a method
```

Two objects can have **identical state** yet be **different objects** (different
identity) — this is exactly why `==` (compares state, if defined) and `is`
(compares identity) are different questions. We formalise this in Module 2.

---

## 1.5 Attributes vs Methods (state vs behaviour, named)

- **Attribute** — a *variable* attached to an object (or class). Represents state.
  Real-world: the **nouns** describing the thing (a car's `brand`, `colour`).
- **Method** — a *function* attached to a class, operating on an object. Represents
  behaviour. Real-world: the **verbs** the thing can do (`drive()`, `brake()`).

![To find classes from a problem statement, turn the nouns into attributes and the verbs into methods.](images/m01_06_real_world_model.png)

> **Design heuristic (used in every LLD interview):** read the problem statement;
> **nouns → candidate classes/attributes**, **verbs → candidate methods**. "A *user*
> can *place* an *order* and *pay* for it" → classes `User`, `Order`, `Payment`;
> methods `place_order()`, `pay()`.

---

## 1.6 Message Passing — How Objects Collaborate

Objects rarely work alone; they **collaborate** by calling each other's methods.
The original OOP vocabulary (from Smalltalk) calls this **sending a message**:
`receiver.message(arguments)`. Crucially, the caller does **not** reach inside the
other object — it only asks it to do something.

![Two objects collaborate: an order object calls charge() on a payment object and gets a receipt back, without touching the payment object's internals.](images/m01_08_message_passing.png)

```python
class Payment:
    def charge(self, amount):
        # ...talks to a gateway internally; caller need not know how...
        return f"receipt#{amount}"

class Order:
    def __init__(self, payment):     # Order collaborates WITH a Payment
        self.payment = payment
    def checkout(self, total):
        return self.payment.charge(total)   # sends a "message"

order = Order(Payment())
print(order.checkout(999))          # receipt#999
```

`Order` depends only on the *public method* `charge()`, not on how `Payment` works.
Swap in a `MockPayment` for testing and `Order` doesn't change — this loose coupling
is a direct payoff of OOP (and the seed of *dependency injection*, Module 18).

---

## 1.7 The Four Pillars of OOP (the map for the whole course)

Nearly every OOP concept is one of four big ideas. We introduce them here in one
line each; each gets its own deep-dive module later.

![The four pillars of OOP: Encapsulation, Abstraction, Inheritance, Polymorphism, each with a one-line meaning.](images/m01_05_four_pillars.png)

| Pillar | One line | Everyday analogy | Module |
|---|---|---|---|
| **Encapsulation** | bundle data + methods; hide internals | a **capsule/pill** — contents sealed inside | M04 |
| **Abstraction** | expose *what*, hide *how* | a **car's steering wheel** — you steer, not touch the engine | M04, M07 |
| **Inheritance** | a new class reuses/extends an existing one (**is-a**) | a **child inherits** traits from a parent | M05 |
| **Polymorphism** | one interface, many implementations | a **"+" that adds ints and joins strings** | M06 |

A 30-second taste of each in Python:

```python
# ENCAPSULATION: internals hidden behind a method (the _balance is guarded)
acc.deposit(100)              # you don't touch _balance directly

# ABSTRACTION: you call a simple method; the messy "how" is hidden
len([1, 2, 3])                # you don't care HOW length is computed

# INHERITANCE: SavingsAccount reuses BankAccount and adds to it
class SavingsAccount(BankAccount):
    def add_interest(self, rate):
        self.deposit(self.balance() * rate)

# POLYMORPHISM: the SAME len() works on many different types
len("abc"); len({1, 2}); len((1,))   # 3, 2, 1 — one name, many forms
```

> **Memory hook — "A PIE":** **A**bstraction, **P**olymorphism, **I**nheritance,
> **E**ncapsulation. If you can define these four and give one example each, you
> can answer the most common opening OOP interview question.

---

## 1.8 "Is Everything in Python an Object?" (yes — and it matters)

In Python, **everything is an object** — integers, strings, functions, even
classes themselves. Each has a type, an identity, and attributes/methods.

```python
print((5).bit_length())     # 3   -> even an int has methods
print("hi".upper())         # HI  -> strings are objects
def f(): pass
print(f.__name__)           # f   -> functions are objects with attributes
print(type(int))            # <class 'type'> -> classes are objects too (Module 9)
```

This is why Python OOP feels so uniform: there is no split between "primitive
types" and "real objects" like in some languages (e.g. Java's `int` vs `Integer`).
We unpack the deep consequences of this in **Module 2 (Python Object Model)**.

---

## 1.9 When to Use OOP — and When NOT To

OOP is a tool, not a religion. Overusing it (a class for every tiny function) is a
real anti-pattern (see M19).

![A decision flowchart: if the problem has many stateful entities that interact, use OOP; if it is a simple one-off script or pure transform, functions are fine.](images/m01_07_when_oop_flowchart.png)

**Reach for OOP when:**

- You have **many entities with state that changes over time** (users, orders,
  game characters, connections).
- Several **variants share behaviour** (different payment methods, shapes, file
  formats) — inheritance/polymorphism shine.
- You want to **protect invariants** (a balance must never go negative).

**Prefer functions / procedural / functional when:**

- It's a **short script** or a **pure data transformation** (parse a file, do a
  calculation) — a function is clearer and lighter than a class.
- The "class" would have **one method and no state** — that's just a function
  wearing a costume.

> **Pythonic wisdom:** *"Don't create a class when a function will do."* A class
> with only `__init__` and one `run()` method is usually better as a plain
> function. Reach for a class when there is genuine **state + behaviour** to bundle.

---

## 1.10 A Brief History (context that occasionally shows up)

- **1960s — Simula 67** introduced classes and objects (for simulations).
- **1970s — Smalltalk** made everything an object and coined "message passing".
- **1980s–90s — C++, then Java** brought OOP to the mainstream (with static typing
  and strict access control).
- **1991 — Python** built OOP in from the start but kept it *optional and dynamic*:
  duck typing over strict interfaces, and access control by *convention* (`_name`)
  rather than hard `private` keywords.

Knowing this explains Python's "flavour" of OOP: **pragmatic, dynamic, and
convention-based** rather than ceremony-heavy.

---

## Module 1 — Interview Mapping

| Question style | Junior answer | Senior answer |
|---|---|---|
| "What is OOP?" | "Programming with objects and classes." | "A paradigm that organises code around objects — bundles of state + behaviour — to get modularity, reuse, and protected invariants; contrasted with procedural code where data and functions are separate." |
| "Class vs object?" | "Class is blueprint, object is instance." | Adds: object has its *own* state + identity; one class → many independent instances; shows `type()`/`isinstance()`. |
| "Four pillars?" | Lists the four names. | Defines each **and gives a Python one-liner** and *when* each helps. |
| "Why not use OOP everywhere?" | (often stuck) | "For a one-off script or a pure transform a function is clearer; a single-method stateless class is an anti-pattern — Python favours functions when there's no state to bundle." |

The evergreen opener — **"Model a `___` (parking lot / library / deck of cards)
as classes"** — is really testing §1.5: nouns→classes/attributes, verbs→methods.
We drill full versions in **Module 18 (LLD)**.

---

## Module 1 — Exam Mapping

- **GATE CS:** definitions of the four pillars; class vs object; identifying
  paradigms. Usually 1-mark conceptual MCQs.
- **SEBI / RBI / NABARD IT:** direct one-liners — "which is NOT an OOP feature",
  "OOP language examples", pillar definitions. High-frequency, easy marks.
- **FAANG / product interviews:** less about definitions, more about *applying*
  them — model a system, justify class boundaries, spot when OOP is overkill.
- *Interview-only (rare in written exams):* message passing terminology, "is
  everything an object in Python", multi-paradigm nature.

---

## Module 1 — Common Mistakes & Misconceptions

- **"OOP = using classes."** No — OOP is using classes *to bundle state and
  behaviour*. Wrapping one function in a class is not OOP; it's clutter.
- **Confusing class and object.** The class is the type; the object is the
  instance. `Car` is the class; `car1` is an object.
- **Thinking OOP is always better.** For simple scripts and pure functions,
  procedural/functional is often cleaner. Python is multi-paradigm on purpose.
- **"Encapsulation = private variables."** Encapsulation is the *bundling +
  hiding* idea; private variables are one *mechanism* for it (and Python's are
  only by convention — Module 4).
- **Believing Python has real `private`.** It does not — `_x` is a hint,
  `__x` triggers *name mangling*, not true privacy (Module 4).

---

## Module 1 — MCQs (with answers & explanations)

**Q1.** Which is NOT one of the four pillars of OOP?
a) Encapsulation  b) Abstraction  c) **Compilation**  d) Polymorphism

<details><summary>Answer</summary>**c.** The four pillars are Encapsulation, Abstraction, Inheritance, Polymorphism. Compilation is unrelated.</details>

**Q2.** A class is best described as:
a) an object in memory  b) **a blueprint/template for objects**  c) a function  d) a module

<details><summary>Answer</summary>**b.** A class defines structure/behaviour; objects are concrete instances built from it.</details>

**Q3.** In Python, which of these is an object?
a) an int  b) a string  c) a function  d) **all of the above**

<details><summary>Answer</summary>**d.** In Python *everything* is an object — ints, strings, functions, and classes themselves.</details>

**Q4.** Bundling data with the methods that operate on it, and hiding internals, is:
a) Inheritance  b) Polymorphism  c) **Encapsulation**  d) Abstraction

<details><summary>Answer</summary>**c.** That is the definition of encapsulation. Abstraction is the related idea of exposing *what* while hiding *how*.</details>

**Q5.** "One interface, many implementations (e.g. `len()` works on lists, strings, dicts)" describes:
a) Encapsulation  b) **Polymorphism**  c) Inheritance  d) Abstraction

<details><summary>Answer</summary>**b.** Polymorphism — the same operation behaves appropriately for different types.</details>

**Q6.** Which situation is the *weakest* case for using a class?
a) modelling users with changing balances  b) several payment types sharing behaviour
c) **a one-off script that reads a file and prints its line count**  d) a game with many characters

<details><summary>Answer</summary>**c.** A stateless one-off transform is clearer as a function; a class here is over-engineering.</details>

**Q7.** `car1 = Car("Tesla")`. Here `car1` is a(n) ____ and `Car` is a(n) ____.
a) class, object  b) **object, class**  c) method, attribute  d) instance, method

<details><summary>Answer</summary>**b.** `car1` is an object (instance); `Car` is the class.</details>

**Q8.** Which paradigm family does OOP belong to?
a) declarative  b) logic  c) **imperative**  d) functional

<details><summary>Answer</summary>**c.** OOP is an *imperative* style (you mutate object state step by step), as opposed to declarative styles like functional/logic.</details>

---

## Module 1 — Design/Practice Exercises (easy → hard)

1. **(easy)** Rewrite this procedural snippet as a class `Counter` with `increment()`,
   `reset()`, and a `value` you read via a method:
   `count = 0` … `count += 1`.
2. **(easy)** From the sentence *"A student enrols in a course and submits an
   assignment"*, list the candidate classes, attributes, and methods.
3. **(medium)** Write a `Rectangle` class with `width`, `height`, and methods
   `area()` and `perimeter()`. Create three rectangles and print their areas —
   confirm each keeps its own state.
4. **(medium)** Give a concrete Python example of each pillar in *five lines total*.
5. **(hard)** Take a 40-line procedural "to-do list" program (global list + free
   functions) and refactor it into `Task` and `TodoList` classes. Write two
   sentences on *what improved* and *what got heavier*.
6. **(hard, interview-style)** Argue both sides: for a "resize every image in a
   folder" tool, when would you keep it as functions, and when would a class earn
   its place? What state would justify the class?

---

## Module 1 — Concept Review (one page)

OOP organises an **imperative** program around **objects** — bundles of **state
(attributes)** and **behaviour (methods)**. It exists to fix procedural pain:
data and the rules protecting it drift apart, and duplicating variables for each
entity doesn't scale. A **class** is a **blueprint**; an **object** is an
**instance** with its **own state + identity + shared behaviour**. Objects
**collaborate by message passing** — calling each other's public methods without
touching internals. The **four pillars** — **Encapsulation, Abstraction,
Inheritance, Polymorphism** ("A PIE") — are the recurring ideas. In Python,
**everything is an object**, and the language is **multi-paradigm**: use OOP when
you have many stateful, interacting entities or shared-behaviour variants; use
plain functions for short scripts and pure transforms.

---

## Module 1 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Four pillars (mnemonic) | Encapsulation, Abstraction, Inheritance, Polymorphism ("A PIE") |
| Class vs object | Class = blueprint/type; object = instance with its own state |
| Three facets of an object | Identity, State, Behaviour |
| Encapsulation (1 line) | Bundle data + methods; hide internals behind an API |
| Abstraction (1 line) | Expose *what*, hide *how* |
| Inheritance (1 line) | New class reuses/extends another (is-a) |
| Polymorphism (1 line) | One interface, many implementations |
| Message passing | `receiver.method(args)` — asking an object to act |
| Is everything an object in Python? | Yes — ints, strings, functions, classes |
| Nouns → ? , Verbs → ? | Nouns → attributes/classes; Verbs → methods |
| When NOT to use OOP | One-off scripts, pure transforms, stateless single-method "classes" |
| OOP's paradigm family | Imperative |

---

## Module 1 — Pattern Recognition

- **See "model / design a real-world system"** → nouns→classes/attributes,
  verbs→methods (§1.5); then think pillars.
- **See "several things that are almost the same but differ slightly"** → reach
  for **inheritance + polymorphism** (M05/M06).
- **See "this data must always stay valid"** → **encapsulation** (guard it behind
  methods, M04).
- **See "a class with just one method and no state"** → *stop* — use a **function**.
- **See "I keep passing the same 3 variables to every function"** → those
  variables + functions want to be an **object**.

---

## Module 1 — Revision Notes / Mini Cheat Sheet

```
OOP = organise an IMPERATIVE program around OBJECTS (state + behaviour).
WHY: procedural pain -> data & rules drift apart; per-entity vars don't scale.
BENEFITS: modularity, reusability, maintainability, data protection.

CLASS  = blueprint / type (definition).
OBJECT = instance built from a class, with its OWN state + identity.
OBJECT = IDENTITY (id/is) + STATE (attributes) + BEHAVIOUR (methods).

FIND CLASSES: nouns -> attributes/classes ; verbs -> methods.
COLLABORATION: message passing = receiver.method(args); don't touch internals.

FOUR PILLARS  ("A PIE")
  Encapsulation  bundle + hide          (M04)
  Abstraction    what, not how          (M04/M07)
  Inheritance    reuse via is-a         (M05)
  Polymorphism   one name, many forms   (M06)

PYTHON: everything is an object; multi-paradigm; access control by CONVENTION.
USE OOP: many stateful, interacting entities / shared-behaviour variants.
AVOID  : one-off scripts, pure transforms, stateless single-method classes.
```

> **Next module:** **Module 2 — The Python Object Model.** We go under the hood:
> how *everything is an object* actually works — `id`/`type`/`value`, the
> difference between a **variable (a name)** and an **object (a value in memory)**,
> references vs copies, **mutable vs immutable**, and why `is` and `==` answer two
> different questions. This is the bedrock every later Python-OOP feature stands on.

---

## Module 1 — Summary

**Object-oriented programming** organises an imperative program around **objects**:
bundles of **state (attributes)** and **behaviour (methods)** that model real-world
"things". It arose to cure procedural pain — data and the rules that protect it
living apart, and per-entity variables that don't scale — delivering
**modularity, reusability, maintainability, and data protection**. A **class** is
a **blueprint**; an **object** is a concrete **instance** with its own state,
identity, and shared behaviour. Objects **collaborate by message passing**. The
**four pillars — Encapsulation, Abstraction, Inheritance, Polymorphism ("A PIE")** —
are the ideas we will spend the rest of the course mastering. In Python,
**everything is an object** and the language is **multi-paradigm**, so the mark of
skill is knowing **when** OOP earns its keep and when a plain function is better.

> **You have mastered this module when** you can: define OOP and contrast it with
> procedural code using a small example; explain class vs object and the three
> facets of an object; name and illustrate the four pillars in Python; extract
> classes/attributes/methods from a problem statement; and argue when *not* to use
> OOP — all without notes.
