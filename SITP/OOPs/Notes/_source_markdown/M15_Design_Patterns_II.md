---
title: "Module 15 — Design Patterns II (Behavioral)"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 15 — Design Patterns II (Behavioral)

> **Why this module matters.**
> Behavioral patterns are about **how objects talk to each other and divide
> responsibility** — and they're the ones that show up most in real design
> interviews. **Strategy** (swap algorithms) is the single most useful pattern for
> replacing `if/elif` ladders and deep inheritance; **Observer** underpins every
> event/notification system; **Command** powers undo/redo and job queues. As always,
> Python's first-class functions often let you implement these with far less
> ceremony than the textbook UML.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★      | ★★          | ★★★★        | ★★★★★      |

**Most-asked concepts:** Strategy (and its Pythonic function form); Observer
(pub/sub); Command (undo/redo); State (state machine); Template Method; Chain of
Responsibility; Strategy vs State; how these replace conditionals/inheritance.

**What you must be able to do after this module:** implement Strategy, Observer,
Command, State, and Template Method in Python; recognise which pattern a problem calls
for; and give the Pythonic (function-based) form of Strategy.

---

## 15.1 Behavioral Patterns Overview

![Behavioral patterns: Strategy (swap algorithms), Observer (publish/subscribe), Command (request as object with undo/queue), State (behaviour changes with internal state), Template/Chain (skeleton steps / pass the request).](images/m15_01_overview.png)

Behavioral patterns coordinate **communication and responsibility** among objects.
We focus on the six you'll actually use and be asked about.

---

## 15.2 Strategy — swap interchangeable algorithms

**Intent:** define a family of algorithms, encapsulate each, and make them
**interchangeable at run time**. The context delegates to a chosen strategy.

![A Sorter holds a strategy and calls .sort(data); the strategy can be QuickSort, MergeSort, or BubbleSort, chosen at run time without changing the client.](images/m15_02_strategy.png)

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data): ...

class QuickSort(SortStrategy):
    def sort(self, data): return sorted(data)          # (stand-in)
class ReverseSort(SortStrategy):
    def sort(self, data): return sorted(data, reverse=True)

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy
    def run(self, data):
        return self.strategy.sort(data)                # delegate

print(Sorter(ReverseSort()).run([3, 1, 2]))            # [3, 2, 1]
```

**Why it's the "big one":** Strategy is **composition instead of inheritance** and
the direct answer to OCP — it replaces `if algo == "x"` ladders and subclass
explosions. It's how you make behaviour pluggable.

---

## 15.3 Observer — publish/subscribe

**Intent:** define a **one-to-many** dependency so that when one object (the
**subject**) changes state, all its **observers** are notified automatically.

![A Subject (publisher) calls notify() to update Observer A, B, and C automatically whenever its state changes — one-to-many pub/sub.](images/m15_03_observer.png)

```python
class Subject:
    def __init__(self):
        self._observers = []
    def subscribe(self, obs):   self._observers.append(obs)
    def notify(self, event):
        for obs in self._observers:
            obs.update(event)                # push to all subscribers

class EmailObserver:
    def update(self, event): print(f"email: {event}")
class LogObserver:
    def update(self, event): print(f"log: {event}")

s = Subject()
s.subscribe(EmailObserver()); s.subscribe(LogObserver())
s.notify("order placed")     # both observers react
```

Powers event systems, GUI callbacks, model↔view sync, and message buses. **Tip:** use
**`weakref`** (Module 12) for observers so the subject doesn't keep dead observers
alive.

---

## 15.4 Command — request as an object

**Intent:** encapsulate a **request as an object**, letting you parameterise, queue,
log, and **undo/redo** operations.

![An Invoker (e.g. a button) holds a Command with execute()/undo(); the Command calls the Receiver that does the work — turning requests into objects for undo/redo/queue/log.](images/m15_04_command.png)

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AddText(Command):
    def __init__(self, doc, text): self.doc, self.text = doc, text
    def execute(self): self.doc.append(self.text)
    def undo(self):    self.doc.pop()

doc, history = [], []
cmd = AddText(doc, "hello"); cmd.execute(); history.append(cmd)
history.pop().undo()         # undo the last command
```

**Why:** decouples the **invoker** (button/menu) from the **receiver** (who does the
work); enables undo stacks, macro recording, and task queues.

---

## 15.5 State — behaviour changes with state

**Intent:** let an object **alter its behaviour when its internal state changes** — it
appears to change class. A clean **state machine** without giant `if` blocks.

![A document moves Draft -> Published -> Archived via publish() and archive(); the same method behaves differently depending on the current state.](images/m15_05_state.png)

```python
class State(ABC):
    @abstractmethod
    def publish(self, doc): ...

class Draft(State):
    def publish(self, doc): doc.state = Published()      # transition
class Published(State):
    def publish(self, doc): print("already published")   # different behaviour

class Document:
    def __init__(self): self.state = Draft()
    def publish(self): self.state.publish(self)          # delegate to state
```

**Strategy vs State (classic interview distinction):** structurally similar (both
delegate to a swappable object), but **Strategy** varies an *algorithm chosen by the
client*, while **State** varies *behaviour driven by the object's own state
transitions*.

---

## 15.6 Template Method — fixed skeleton, variable steps

**Intent:** define the **skeleton** of an algorithm in a base method, deferring some
**steps** to subclasses — the order is fixed; specifics vary.

![Base.run() calls step1(); step2(); step3() in a fixed order; SubA and SubB each override step2() with their own behaviour, keeping the skeleton constant.](images/m15_06_template_method.png)

```python
class DataPipeline(ABC):
    def run(self):                    # the template (fixed order)
        data = self.extract()
        data = self.transform(data)
        self.load(data)
    @abstractmethod
    def extract(self): ...
    @abstractmethod
    def transform(self, data): ...
    def load(self, data): print("saving", data)   # default step

class CsvPipeline(DataPipeline):
    def extract(self): return "csv-rows"
    def transform(self, d): return d.upper()
```

Uses **inheritance** (the one place it's clearly right): the base owns the invariant
sequence; subclasses fill the hooks. Contrast with **Strategy**, which uses
composition to vary the *whole* algorithm.

---

## 15.7 Chain of Responsibility

**Intent:** pass a request along a **chain of handlers** until one handles it —
decoupling sender from receiver.

![A request goes L1 support -> L2 support -> Manager, each either handling it or passing it on; if none can, it ends up unhandled.](images/m15_07_chain.png)

```python
class Handler:
    def __init__(self, successor=None): self.successor = successor
    def handle(self, level):
        if self.can_handle(level):
            return self.process(level)
        if self.successor:
            return self.successor.handle(level)      # pass it along
        return "unhandled"

# L1 -> L2 -> Manager chain; each Handler subclass defines can_handle/process
```

Uses: middleware pipelines (web frameworks), event bubbling, logging levels, approval
workflows. *(Also behavioral: **Mediator** centralises complex interactions;
**Memento** captures/restores state; **Visitor** adds operations to a class hierarchy;
**Iterator** — Module 7 — traverses a collection.)*

---

## 15.8 The Pythonic Shortcut: functions as strategies

![Classic Strategy needs a Strategy ABC plus concrete classes (boilerplate); the Pythonic form just passes a function, e.g. sort(data, key=fn), because functions are first-class objects.](images/m15_08_strategy_pythonic.png)

Because **functions are first-class objects**, many behavioral patterns collapse in
Python:

```python
# Strategy as a plain function — no class hierarchy needed
def process(data, strategy):
    return strategy(data)

process([3, 1, 2], sorted)                       # strategy = a function
process([3, 1, 2], lambda d: sorted(d, reverse=True))

# The stdlib already does this: sorted(data, key=...) IS Strategy.
# Observer -> a list of callbacks. Command -> a function/partial. State -> a dict of funcs.
```

> **Senior takeaway:** know the classic OO form (for interviews and Java-shaped
> codebases), but in Python prefer the **lighter function-based** version when it's
> clearer — that judgment is exactly what distinguishes idiomatic Python.

---

## Module 15 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Strategy pattern?" | "Swap algorithms." | "Encapsulate interchangeable algorithms; context delegates; composition over inheritance; replaces `if/elif`. In Python often just a passed function (`sorted(key=...)`)." |
| "Observer?" | "One notifies many." | "Subject keeps subscribers and pushes updates on state change; use weakrefs to avoid leaks; basis of event systems." |
| "Strategy vs State?" | (blurs) | "Same structure; Strategy = algorithm chosen by client; State = behaviour driven by the object's own state transitions." |
| "Command — why?" | "Encapsulate a request." | "Decouples invoker from receiver; enables undo/redo, queues, macros, logging." |

---

## Module 15 — Exam Mapping

- **GATE CS:** occasionally definitional / pattern-category matching.
- **SEBI / RBI IT:** rarely.
- **FAANG / LLD rounds:** Strategy, Observer, State, Command appear constantly in
  design questions (e.g. "design a notification system" → Observer; "design an
  undo feature" → Command; "pluggable pricing" → Strategy).

---

## Module 15 — Common Mistakes & Misconceptions

- **Confusing Strategy and State** — algorithm-choice vs state-driven behaviour.
- **Over-engineering Strategy with classes** where a function is clearer.
- **Observer memory leaks** — subject holds strong refs to dead observers (use
  `weakref`).
- **Template Method with too many abstract steps** — fragile base class; consider
  Strategy/composition.
- **Command without a receiver** — losing the decoupling benefit.
- **Chain with no terminal handler** — requests silently lost.

---

## Module 15 — MCQs (with answers & explanations)

**Q1.** Swapping interchangeable algorithms at run time is:
a) State  b) **Strategy**  c) Observer  d) Command

<details><summary>Answer</summary>**b.** Strategy encapsulates interchangeable algorithms.</details>

**Q2.** A one-to-many auto-notification on state change is:
a) Command  b) **Observer**  c) Chain  d) Template Method

<details><summary>Answer</summary>**b.** Observer (pub/sub).</details>

**Q3.** Encapsulating a request to support undo/redo is:
a) Strategy  b) State  c) **Command**  d) Facade

<details><summary>Answer</summary>**c.** Command turns actions into objects.</details>

**Q4.** The difference between Strategy and State is:
a) none  b) **algorithm chosen by client vs behaviour driven by internal state**  c) speed  d) memory

<details><summary>Answer</summary>**b.** Same structure, different intent/driver.</details>

**Q5.** A base method fixing the step order while subclasses fill steps is:
a) Strategy  b) **Template Method**  c) Observer  d) Proxy

<details><summary>Answer</summary>**b.** Template Method defines the skeleton; subclasses override steps.</details>

**Q6.** Passing a request through handlers until one handles it is:
a) **Chain of Responsibility**  b) Command  c) Mediator  d) State

<details><summary>Answer</summary>**a.** Chain of Responsibility.</details>

**Q7.** The Pythonic Strategy is often:
a) a metaclass  b) **a first-class function passed in (e.g. `key=`)**  c) a Singleton  d) a mixin

<details><summary>Answer</summary>**b.** Functions are objects; `sorted(key=...)` is Strategy.</details>

**Q8.** `sorted(data, key=fn)` is an example of which pattern?
a) Observer  b) **Strategy**  c) Command  d) State

<details><summary>Answer</summary>**b.** `key` is a pluggable strategy function.</details>

---

## Module 15 — Design/Practice Exercises (easy → hard)

1. **(easy)** Implement a `PaymentContext` with `CardStrategy`/`UpiStrategy`; swap at
   run time.
2. **(easy)** Rewrite that Strategy using plain functions.
3. **(medium)** Build an Observer `Stock` that notifies `Display` and `Alert`
   observers on price change.
4. **(medium)** Implement Command with `execute`/`undo` for a text editor and an undo
   stack.
5. **(hard)** Model a traffic light as a State machine (Red→Green→Yellow) where
   `next()` behaves per state.
6. **(hard, interview)** Design a support-ticket escalation with Chain of
   Responsibility, then discuss when Strategy would fit better.

---

## Module 15 — Concept Review (one page)

**Behavioral patterns** coordinate object interaction and responsibility.
**Strategy** encapsulates **interchangeable algorithms** and delegates to a chosen
one — composition over inheritance, the antidote to `if/elif` ladders (and often just
a **passed function** in Python). **Observer** defines **one-to-many** auto-
notification from a subject to its subscribers (event systems; use `weakref` to avoid
leaks). **Command** turns a **request into an object**, enabling undo/redo, queues,
and macros by decoupling invoker from receiver. **State** lets an object **change
behaviour with its internal state** (a clean state machine) — structurally like
Strategy but **driven by state transitions**, not client choice. **Template Method**
fixes an algorithm's **skeleton** in a base class while subclasses fill **steps**
(the right use of inheritance). **Chain of Responsibility** passes a request through
**handlers** until one handles it. Know the classic OO forms, but prefer Python's
lighter, function-based versions when clearer.

---

## Module 15 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Strategy | interchangeable algorithms, chosen at run time (composition) |
| Pythonic Strategy | pass a function (`sorted(key=...)`) |
| Observer | one-to-many auto-notification (pub/sub) |
| Command | request as an object → undo/redo/queue |
| State | behaviour changes with internal state (state machine) |
| Strategy vs State | client-chosen algorithm vs state-driven behaviour |
| Template Method | base fixes step order; subclasses fill steps |
| Chain of Responsibility | pass request along handlers until handled |
| Observer leak fix | hold observers via `weakref` |
| `sorted(key=fn)` is | Strategy |
| Template Method uses | inheritance (skeleton + hooks) |
| Command decouples | invoker from receiver |

---

## Module 15 — Pattern Recognition

- **See "pluggable algorithm / behaviour"** → Strategy (or a function).
- **See "notify many parts when something changes"** → Observer.
- **See "undo/redo, queue, or log actions"** → Command.
- **See "object behaves differently in different modes"** → State.
- **See "same overall steps, differing details per type"** → Template Method.
- **See "try handlers in order until one accepts"** → Chain of Responsibility.
- **See a big `if algo == ...` block** → replace with Strategy.

---

## Module 15 — Revision Notes / Mini Cheat Sheet

```
BEHAVIORAL = how objects interact / share responsibility.

Strategy   interchangeable algorithms; context delegates; composition; replaces if/elif.
           Pythonic: pass a function (sorted(key=...)).
Observer   subject notifies many subscribers on change (pub/sub). Use weakref -> no leaks.
Command    request -> object with execute()/undo(); decouple invoker/receiver; undo/redo/queue.
State      behaviour varies with internal state (state machine); delegate to state object.
           Strategy vs State: client-chosen ALGO vs state-driven BEHAVIOUR (same structure).
Template   base method fixes step ORDER; subclasses override steps (inheritance).
Chain      pass request along handlers until one handles it (middleware, escalation).
(Also: Mediator, Memento, Visitor, Iterator[M7].)

PYTHON: functions are objects -> Strategy=fn, Observer=list of callbacks, Command=partial.
```

> **Next module:** **Module 16 — Exception Hierarchies & OOP Error Handling.** Errors
> are objects too. We'll design **custom exception hierarchies**, use inheritance to
> catch families of errors, cover `try/except/else/finally`, exception chaining
> (`raise ... from`), and the **EAFP vs LBYL** philosophy that pairs with duck
> typing.

---

## Module 15 — Summary

**Behavioral patterns** structure how objects communicate. **Strategy** makes
algorithms interchangeable via composition (often just a function in Python) and is
the go-to replacement for conditionals and subclass explosions. **Observer**
implements one-to-many notification behind event systems; **Command** reifies
requests to enable undo/redo and queues; **State** models state-machine behaviour and
contrasts with Strategy by being **state-driven** rather than client-chosen.
**Template Method** rightly uses inheritance to fix an algorithm's skeleton while
varying steps, and **Chain of Responsibility** routes a request through handlers until
one handles it. Mastering these — and knowing Python's leaner function-based forms —
equips you for the interaction-design questions that dominate LLD interviews.

> **You have mastered this module when** you can: implement Strategy (class and
> function forms), Observer, Command, State, and Template Method in Python; pick the
> right pattern for a scenario; and articulate Strategy vs State.
