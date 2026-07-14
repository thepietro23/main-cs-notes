---
title: "Module 20 — Exam & Interview Mapping + Master Question Bank"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 20 — Exam & Interview Mapping + Master Question Bank

> **Why this module matters.**
> This is your **drill-and-revise** hub. Every prior module ends with its own MCQs;
> here we consolidate the whole subject into an **exam/interview map**, an **answer
> framework**, and a **large, graded question bank** — conceptual, output-prediction,
> coding, and design — with answers. Work through this before any interview or exam;
> it converts *understanding* into *fast, confident answers*.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★★★    | ★★★★        | ★★★★        | ★★★★★      |

---

## 20.1 Topic Priority

![Topic priority: P0 = four pillars, dunders, inheritance/MRO, SOLID, patterns, LLD; P1 = object model, descriptors, dataclasses, typing/Protocols, exceptions, memory; P2 = metaclasses, __slots__, UML notation.](images/m20_01_topic_importance.png)

- **P0 (must nail):** four pillars; class/object mechanics; inheritance + MRO;
  polymorphism/dunders; SOLID; core patterns; LLD process.
- **P1 (strong):** object model (`is`/`==`, mutability); descriptors/`@property`;
  dataclasses/enums; typing/Protocols; exceptions; memory.
- **P2 (depth / senior):** metaclasses; `__slots__`; UML notation; advanced typing.

---

## 20.2 How Questions Escalate

![Interview escalation: Define (pillars) -> Explain + example -> Predict output / code -> Design (LLD); depth rises with seniority.](images/m20_02_interview_flow.png)

![Top FAANG OOP questions: 4 pillars + example; is vs == and mutable default bug; MRO/diamond; classmethod vs staticmethod; eq/hash contract; SOLID applied; Strategy/Observer/Factory; design a parking lot/elevator.](images/m20_03_most_asked.png)

![Four question types: Conceptual (define/compare), Output prediction (trace aliasing/MRO/defaults), Code/implement (write a class/dunders/pattern), Design/LLD (model a system end-to-end).](images/m20_04_question_types.png)

---

## 20.3 The Answer Framework

![Answer framework for 'Explain X': 1) one-line definition, 2) why it exists (problem), 3) tiny Python example, 4) trade-off / when NOT to use, 5) relate to a pillar/principle.](images/m20_05_answer_framework.png)

Use this five-beat structure for any "explain/compare" question: **definition →
motivation → example → trade-off → connection**. It reads as senior and complete.

---

## 20.4 Conceptual Question Bank (with answers)

**C1.** Name the four pillars and define each in one line.
<details><summary>Answer</summary>Encapsulation (bundle + hide), Abstraction (expose what, hide how), Inheritance (reuse via is-a), Polymorphism (one interface, many forms).</details>

**C2.** Class vs object?
<details><summary>Answer</summary>Class = blueprint/type; object = instance with its own state + identity + shared behaviour.</details>

**C3.** `is` vs `==`?
<details><summary>Answer</summary>`is` = identity (same object, `id`); `==` = value (`__eq__`). Use `is` only for singletons like `None`.</details>

**C4.** Explain the diamond problem and how Python solves it.
<details><summary>Answer</summary>Two paths to a shared ancestor; Python uses a deterministic MRO via C3 linearisation, and `super()` follows it so each ancestor runs once.</details>

**C5.** `@classmethod` vs `@staticmethod` vs instance method?
<details><summary>Answer</summary>Instance → `self` (state); classmethod → `cls` (factories/subclass-aware); staticmethod → neither (namespaced helper).</details>

**C6.** Does Python have private variables?
<details><summary>Answer</summary>No true private. `_x` is convention; `__x` is name-mangled to `_Class__x` (avoids subclass clashes, still accessible).</details>

**C7.** Encapsulation vs abstraction?
<details><summary>Answer</summary>Encapsulation = data protection / access control (implementation); abstraction = simple interface hiding complexity (design).</details>

**C8.** Composition vs inheritance — which to prefer and why?
<details><summary>Answer</summary>Favour composition (has-a): loose coupling, runtime-swappable, avoids fragile base classes; use inheritance for genuine is-a.</details>

**C9.** What is duck typing?
<details><summary>Answer</summary>Compatibility depends on having the right methods, not the class ("if it quacks…"); pairs with EAFP.</details>

**C10.** Why does defining `__eq__` require `__hash__`?
<details><summary>Answer</summary>Defining `__eq__` sets `__hash__=None` → unhashable; add `__hash__` over the same fields (value-immutable objects) to keep it usable in sets/dicts.</details>

**C11.** ABC vs Protocol?
<details><summary>Answer</summary>ABC = nominal (must inherit; explicit is-a; can hold concrete methods); Protocol = structural (matches by method shape; no inheritance; static duck typing).</details>

**C12.** What is a metaclass?
<details><summary>Answer</summary>The class of a class (`type` by default); it creates classes. `class` is sugar for `type(name, bases, ns)`.</details>

**C13.** EAFP vs LBYL?
<details><summary>Answer</summary>EAFP (try/except, Pythonic, race-safe) vs LBYL (check-first, race-prone). Python prefers EAFP.</details>

**C14.** State the five SOLID principles.
<details><summary>Answer</summary>SRP (one reason to change), OCP (extend not modify), LSP (subtype substitutable), ISP (small interfaces), DIP (depend on abstractions).</details>

**C15.** Strategy vs State pattern?
<details><summary>Answer</summary>Same structure; Strategy = client-chosen algorithm; State = behaviour driven by internal state transitions.</details>

---

## 20.5 Output-Prediction Bank (rehearse these!)

![Output-prediction traps: mutable default reused; b = a aliasing; is vs == interning (256 vs 1000); MRO order; mutable class attribute shared; instance shadowing a class attr; __eq__ without __hash__.](images/m20_06_output_traps.png)

**O1.** `def f(x=[]): x.append(1); return x` — output of `f(); f()`?
<details><summary>Answer</summary>`[1]` then `[1, 1]` — the default list is created once and shared.</details>

**O2.** `a=[1]; b=a; a.append(2); print(b)`?
<details><summary>Answer</summary>`[1, 2]` — `b` aliases the same list.</details>

**O3.** `print(256 is 256, 1000 is 1000)` (CPython)?
<details><summary>Answer</summary>`True` and (usually) `False` — small ints -5..256 are interned; 1000 may not be.</details>

**O4.** Diamond `D(B, C)`, `B(A)`, `C(A)` — `D.__mro__`?
<details><summary>Answer</summary>`(D, B, C, A, object)`.</details>

**O5.** `class Dog: tricks=[]` then two dogs each `add_trick` — do they share?
<details><summary>Answer</summary>Yes — the mutable class attribute is shared; both dogs see all tricks.</details>

**O6.** Class attr `species="canine"`; `a.species="wolf"`; does `b.species` change?
<details><summary>Answer</summary>No — assignment created an instance attr on `a` shadowing the class attr; `b` still sees "canine".</details>

**O7.** `s="hi"; id1=id(s); s+="!"; id2=id(s)` — equal ids?
<details><summary>Answer</summary>No — strings are immutable; `+=` rebinds `s` to a new object.</details>

**O8.** `print("a"+"b", [1]+[2], 1+2)` — one operator, three results?
<details><summary>Answer</summary>`'ab' [1, 2] 3` — operator overloading via `__add__` per type.</details>

**O9.** Define `__eq__` only, then `{obj}` — result?
<details><summary>Answer</summary>`TypeError: unhashable type` — need `__hash__` too.</details>

**O10.** `grid=[[0]*3]*3; grid[0][0]=1; print(grid)`?
<details><summary>Answer</summary>`[[1,0,0],[1,0,0],[1,0,0]]` — all rows are the same list; use a comprehension.</details>

---

## 20.6 Coding Question Bank

**K1.** Implement a `Stack` class with `push`, `pop`, `peek`, `is_empty`, `__len__`.

**K2.** Make a `Money` class supporting `+`, `==`, `<`, `__hash__`, `__repr__`,
rejecting mismatched currencies.

**K3.** Write a `@classmethod from_string` factory for a `Date` class.

**K4.** Implement an `Observer`-based `Stock` that notifies displays on price change.

**K5.** Build a validating `@property` (`Temperature.celsius` rejecting < -273.15).

**K6.** Implement a reusable `Positive` **descriptor** and use it on two fields.

**K7.** Write a context manager `Timer` using `__enter__`/`__exit__`.

**K8.** Implement `Strategy` for sorting (asc/desc) both as classes and as functions.

<details><summary>Sample answer — K2 (Money)</summary>

```python
from functools import total_ordering
@total_ordering
class Money:
    def __init__(self, amount, currency):
        self.amount, self.currency = amount, currency
    def _check(self, o):
        if self.currency != o.currency: raise ValueError("currency mismatch")
    def __add__(self, o): self._check(o); return Money(self.amount + o.amount, self.currency)
    def __eq__(self, o): return (self.amount, self.currency) == (o.amount, o.currency)
    def __lt__(self, o): self._check(o); return self.amount < o.amount
    def __hash__(self): return hash((self.amount, self.currency))
    def __repr__(self): return f"Money({self.amount}, {self.currency!r})"
```
</details>

---

## 20.7 Design (LLD) Question Bank

**D1.** Design a **parking lot** (levels, vehicle types, pluggable allocation, ticket).
**D2.** Design an **elevator** system (requests, scheduling Strategy, State modes).
**D3.** Design a **deck of cards** + a card game (Enums, frozen Card, Deck).
**D4.** Design a **rate limiter** (token bucket; inject the clock).
**D5.** Design a **vending machine** (State: idle/paid/dispensing).
**D6.** Design a **notification service** (Observer + Strategy channels + Factory).
**D7.** Design **Splitwise** (users, groups, split Strategies, balances).
**D8.** Design a **logging framework** (levels via Chain of Responsibility, Singleton/module).

> For each: **clarify → entities → relationships (UML) → SOLID + patterns → code →
> extensions.** (Full worked solutions in Module 18.)

---

## 20.8 Exam Mapping (written exams)

| Exam | OOP focus |
|---|---|
| **GATE CS** | pillar definitions; class vs object; inheritance/overriding; access; output prediction |
| **SEBI / RBI / NABARD IT** | definitions; features of OOP; encapsulation; which language is OO |
| **UGC-NET / PSU** | pillars; UML relationship notation; patterns (definitional) |
| **FAANG / product** | *apply* pillars/SOLID/patterns; output prediction; LLD design |

---

## 20.9 Revision & Prep Plan

![Spaced revision: 24 hours — recite pillars, is vs ==, MRO rule; 1 week — SOLID, top patterns, output traps; 1 month — design 2 LLD systems; before interview — cheat sheet + 1 mock design.](images/m20_07_revision_priority.png)

![Two-week sprint: Days 1-3 pillars + object model + classes; Days 4-6 inheritance, polymorphism, dunders; Days 7-9 SOLID + patterns; Days 10-12 LLD practice; Days 13-14 mock interviews + cheat-sheet drill.](images/m20_08_prep_plan.png)

---

## Module 20 — Concept Review (one page)

Interviews and exams test OOP in a **predictable ladder**: **define** (pillars),
**explain with an example**, **predict output / write code**, then **design** (LLD).
Prioritise **P0** (four pillars, class mechanics, inheritance/MRO, polymorphism/
dunders, SOLID, patterns, LLD), then **P1** (object model, descriptors, dataclasses,
typing, exceptions, memory), then **P2** (metaclasses, `__slots__`, UML). Answer
"explain X" in five beats — **definition → motivation → example → trade-off →
connection**. Rehearse the recurring **output-prediction traps** (mutable defaults,
aliasing, `is`/`==` interning, MRO, shared class attributes, `__eq__`/`__hash__`) and
practise the classic **LLD prompts** end-to-end. Revise on a spaced schedule and, for
interviews, run a **two-week sprint** front-loading pillars and ending on live design.

---

## Module 20 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Four pillars | Encapsulation, Abstraction, Inheritance, Polymorphism |
| `is` vs `==` | identity vs value |
| Mutable default fix | `None` sentinel |
| MRO of `D(B,C)` | D, B, C, A, object |
| classmethod vs staticmethod | `cls` (factory) vs nothing (helper) |
| `__eq__` implies | must define `__hash__` too |
| SOLID | SRP, OCP, LSP, ISP, DIP |
| Strategy vs State | client algorithm vs state-driven behaviour |
| Favour | composition over inheritance |
| ABC vs Protocol | nominal (inherit) vs structural (shape) |
| Answer framework | define → motivate → example → trade-off → connect |
| LLD process | clarify → entities → UML → patterns → code → extend |

---

## Module 20 — Revision Notes / Mini Cheat Sheet

```
QUESTION LADDER: define -> explain+example -> output/code -> design(LLD).
PRIORITY: P0 pillars/classes/MRO/dunders/SOLID/patterns/LLD ; P1 object model/descriptors/
          dataclasses/typing/exceptions/memory ; P2 metaclasses/__slots__/UML.

ANSWER 'EXPLAIN X': definition -> why (problem) -> tiny example -> trade-off -> connect to pillar.

OUTPUT TRAPS: mutable default (=[]), b=a aliasing, 256 is 256 / 1000 maybe not,
  MRO order, mutable class attr shared, instance shadows class attr, __eq__ w/o __hash__,
  [[0]*n]*m rows aliased.

DESIGN: clarify -> entities(nouns) -> relationships(UML) -> SOLID+patterns -> code -> extend.
  parking lot | elevator | deck | rate limiter | vending | notifications | splitwise | logger.

PREP: daily recall (pillars/MRO), weekly drill (SOLID/patterns/traps), monthly design,
      pre-interview: cheat sheet (M21) + a mock design.
```

> **Next module:** **Module 21 — Revision Kit & Master Cheat Sheets.** The final
> module distils the entire course into dense one-page recall sheets — the four
> pillars, dunder table, MRO/`super()`, SOLID, patterns, and a full glossary — the
> single document to review the night before an interview or exam.

---

## Module 20 — Summary

This module turns knowledge into interview performance. OOP questions follow a
**ladder** — define, explain, predict/code, design — and you should prioritise **P0**
topics first. Use the **five-beat answer framework** for explanations, and rehearse
the **conceptual, output-prediction, coding, and design** banks here until answers
are automatic. The **output-prediction traps** (mutable defaults, aliasing,
interning, MRO, shared class attributes, `__eq__`/`__hash__`) and the **classic LLD
prompts** are the highest-yield drills. Combine with a **spaced revision** schedule
and a focused **two-week sprint** and you'll walk into any OOP round prepared.

> **You have mastered this module when** you can: answer any P0 conceptual question in
> the five-beat framework; predict the output of every trap here and say why; code the
> listed classes cleanly; and run a full LLD design under time pressure.
