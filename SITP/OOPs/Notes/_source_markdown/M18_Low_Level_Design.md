---
title: "Module 18 — Low-Level Design (LLD): FAANG Systems"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 18 — Low-Level Design (LLD): FAANG Systems

> **Why this module matters.**
> This is the interview's marquee OOP question: *"Design a parking lot / elevator /
> deck of cards / rate limiter."* It's where **everything** from Modules 1–17 comes
> together — pillars, SOLID, patterns, UML — under time pressure, on a whiteboard.
> The good news: LLD is a **repeatable process**, not raw talent. This module gives
> you that process and three fully worked designs in Python so you can pattern-match
> any new prompt.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★       | ★           | ★★★★        | ★★★★★      |

**Most-asked concepts:** the LLD approach (clarify → entities → relationships →
patterns → code); classic problems (parking lot, elevator, deck of cards, rate
limiter, vending machine, BookMyShow, splitwise); which pattern fits which
sub-problem; designing for extensibility.

**What you must be able to do after this module:** run the LLD process on a fresh
prompt; identify entities and relationships; choose the right patterns; write clean,
extensible Python classes; and articulate trade-offs and extensions.

---

## 18.1 The LLD Process (do this every time)

![The LLD flow: clarify requirements, identify entities, define relationships + UML, apply SOLID + patterns, code the classes, discuss extensions — in order, top to bottom.](images/m18_01_approach.png)

1. **Clarify requirements** — ask about scope, scale, features. *Never jump to
   code.* (e.g. "Multiple floors? Payment? Vehicle types?")
2. **Identify entities** — nouns → classes (Module 17). List core objects.
3. **Define relationships & responsibilities** — who owns/uses whom; draw a quick
   UML class sketch; assign each class one job (SRP).
4. **Apply SOLID + patterns** — spot where Strategy/State/Factory/Observer fit.
5. **Code the classes** — interfaces first, then implementations; use enums/
   dataclasses.
6. **Discuss extensions & trade-offs** — "how would you add X?", concurrency,
   persistence.

> **Interviewers score communication as much as code.** Think out loud, state
> assumptions, and evolve the design.

---

## 18.2 Worked Example 1 — Parking Lot

**Clarified requirements:** multiple levels; spots sized for bike/car/truck; issue a
ticket on entry; pluggable spot-allocation policy; compute fee on exit.

![Parking Lot class model: ParkingLot composes Levels which compose ParkingSpots; a Vehicle hierarchy (Car/Bike/Truck) via inheritance; a Ticket issued on park.](images/m18_02_parking_classes.png)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

class VehicleSize(Enum):
    BIKE = auto(); CAR = auto(); TRUCK = auto()

class Vehicle(ABC):                       # inheritance: vehicle hierarchy
    def __init__(self, plate): self.plate = plate
    @property
    @abstractmethod
    def size(self) -> VehicleSize: ...

class Car(Vehicle):
    size = VehicleSize.CAR
class Bike(Vehicle):
    size = VehicleSize.BIKE

@dataclass
class ParkingSpot:
    id: str
    size: VehicleSize
    occupied_by: Vehicle | None = None
    def is_free(self, v): return self.occupied_by is None and self.size == v.size

@dataclass
class Ticket:
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: float
```

**Spot allocation as a Strategy** (so the policy is pluggable — OCP):

![Parking uses a Strategy: ParkingLot.park(vehicle) delegates to an allocation strategy (NearestSpot / RandomSpot / CheapestSpot) chosen without modifying the lot.](images/m18_03_parking_strategy.png)

```python
class AllocationStrategy(ABC):
    @abstractmethod
    def find_spot(self, spots, vehicle) -> ParkingSpot | None: ...

class NearestFirst(AllocationStrategy):
    def find_spot(self, spots, vehicle):
        return next((s for s in spots if s.is_free(vehicle)), None)

class ParkingLot:
    def __init__(self, spots, strategy: AllocationStrategy):
        self.spots = spots
        self.strategy = strategy          # Dependency Injection (DIP)
    def park(self, vehicle) -> Ticket:
        spot = self.strategy.find_spot(self.spots, vehicle)
        if spot is None:
            raise NoSpotAvailable(vehicle)
        spot.occupied_by = vehicle
        return Ticket(vehicle, spot, entry_time=0.0)
```

**Patterns used:** inheritance (Vehicle), composition (Lot→Level→Spot), **Strategy**
(allocation), **DIP/DI** (strategy injected). **Extensions to mention:** payment
(Strategy again), multiple levels, concurrency (locks per spot).

---

## 18.3 Worked Example 2 — Elevator System

**Clarified requirements:** N floors; internal + external requests; a scheduling
policy; the elevator has modes (idle/up/down).

![Elevator as a State machine: Idle transitions to MovingUp/MovingDown and back; a scheduler picks direction while State drives behaviour.](images/m18_04_elevator_states.png)

```python
from enum import Enum, auto
import heapq

class Direction(Enum):
    UP = auto(); DOWN = auto(); IDLE = auto()

class Elevator:
    def __init__(self):
        self.floor = 0
        self.direction = Direction.IDLE
        self._up = []                     # min-heap of up requests
        self._down = []                   # max-heap (negated) of down requests
    def request(self, floor):
        if floor > self.floor: heapq.heappush(self._up, floor)
        elif floor < self.floor: heapq.heappush(self._down, -floor)
    def step(self):                       # SCAN-like scheduling (Strategy-able)
        if self.direction == Direction.UP and self._up:
            self.floor = heapq.heappop(self._up)
        elif self._down:
            self.direction = Direction.DOWN
            self.floor = -heapq.heappop(self._down)
        else:
            self.direction = Direction.IDLE
```

**Patterns used:** **State** (direction drives behaviour), **Strategy** (scheduling
algorithm: FCFS vs SCAN), **Observer** (floor displays subscribe to position).
**Extensions:** multiple elevators + a dispatcher, capacity limits, priority requests.

---

## 18.4 Worked Example 3 — Deck of Cards

**Clarified requirements:** standard 52-card deck; shuffle; deal N; cards are
immutable/comparable.

![Deck of Cards model: Suit and Rank are Enums; Card is a frozen (immutable, hashable) dataclass of (Suit, Rank); Deck holds 52 Cards with shuffle() and deal(n).](images/m18_05_deck_cards.png)

```python
from dataclasses import dataclass
from enum import Enum
import random

class Suit(Enum):
    HEARTS = "H"; DIAMONDS = "D"; CLUBS = "C"; SPADES = "S"

class Rank(Enum):
    TWO = 2; THREE = 3; # ... 
    JACK = 11; QUEEN = 12; KING = 13; ACE = 14

@dataclass(frozen=True, order=True)       # immutable, hashable, sortable
class Card:
    rank: Rank
    suit: Suit

class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for s in Suit for r in Rank]   # 52 cards
    def shuffle(self): random.shuffle(self.cards)
    def deal(self, n): 
        dealt, self.cards = self.cards[:n], self.cards[n:]
        return dealt
```

**Patterns/tools used:** **Enum** (Suit/Rank), **frozen dataclass** value object
(Card), composition (Deck has Cards). **Extensions:** multiple decks, a `Hand` class,
a `Game` (Template Method for turn structure).

---

## 18.5 Worked Example 4 — Rate Limiter (Token Bucket)

**Clarified requirements:** allow up to R requests/sec per user; smooth bursts.

![Token bucket rate limiter: a bucket holds tokens (3/5) that refill over time; each request consumes a token — allow if one remains, reject if empty.](images/m18_06_rate_limiter.png)

```python
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate    # tokens per second
        self.last = 0.0                    # last refill timestamp (injected clock)
    def allow(self, now: float) -> bool:
        self.tokens = min(self.capacity,
                          self.tokens + (now - self.last) * self.refill_rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True                    # request allowed
        return False                       # rate limited
```

**Design notes:** inject the clock (`now`) for testability (DIP); one bucket per user
(a dict/`Factory`). **Alternatives to discuss:** fixed/sliding window, leaky bucket;
distributed limiting (Redis). This connects OOP to system design.

---

## 18.6 Which Pattern for Which Sub-Problem

![Patterns recurring in LLD: Strategy (pluggable policy — parking, scheduling, pricing), State (modes — elevator, order, vending), Factory (create by type — vehicles, notifications), Observer (notify — displays, tickers), Singleton (one manager — lot, logger, or a module).](images/m18_07_patterns_in_lld.png)

| Sub-problem | Pattern |
|---|---|
| Pluggable policy (allocation, pricing, scheduling) | **Strategy** |
| Object behaves differently by mode/status | **State** |
| Create objects by type/config | **Factory** |
| Notify many parts of a change | **Observer** |
| One shared manager/registry | **Singleton** (or a module) |
| Undo/redo, command queue | **Command** |
| Build a complex object stepwise | **Builder** |

Recognising these mappings *fast* is the core LLD skill — most designs are 2–4 of
these composed.

---

## 18.7 What Interviewers Score

![LLD scoring: they want clarified requirements, clean class boundaries, SOLID + right patterns, extensible design; red flags are jumping to code, one giant class, hard-coded if/elif, and no extensibility.](images/m18_08_lld_checklist.png)

- **Green:** you **clarify** first, define **clean class boundaries** (SRP), apply
  **SOLID** and the **right patterns**, and design for **extension**.
- **Red flags:** jumping straight to code, one **god class**, hard-coded `if/elif`
  ladders (should be Strategy/polymorphism), and a design that can't absorb the
  "now add X" follow-up.

---

## 18.8 A Bank of Classic LLD Prompts

Practice these (each maps to patterns you now know):

| Prompt | Key patterns |
|---|---|
| Parking Lot | Strategy, composition, Factory |
| Elevator / Lift system | State, Strategy, Observer |
| Deck of Cards / Card game | Enum, value object, Template Method |
| Rate Limiter | Strategy (algorithm), Factory (per-user) |
| Vending Machine | State (idle/paid/dispensing) |
| BookMyShow / movie booking | Strategy (seat pricing), Observer, locking |
| Splitwise | composition, Strategy (split types) |
| Logger | Singleton/module, Chain of Responsibility (levels) |
| Notification service | Observer, Strategy (channel), Factory |
| Chess / Tic-Tac-Toe | State, Strategy (rules), composition |

---

## Module 18 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Design a parking lot." | Jumps to classes. | **Clarifies** (levels, sizes, payment), sketches entities + UML, uses **Strategy** for allocation, **DI** for policy, discusses extensions & concurrency. |
| "Where's a pattern here?" | (misses) | Maps sub-problems to Strategy/State/Factory/Observer explicitly. |
| "How would you add feature X?" | (rewrites) | Shows the design already supports it via a new subclass/strategy (OCP). |
| "How do you avoid a god class?" | (unsure) | SRP: split responsibilities; composition; each class one job. |

---

## Module 18 — Exam Mapping

- **GATE / PSU:** not directly (this is interview-focused).
- **FAANG / product LLD rounds:** *the* core round — process, class design, patterns,
  and extensibility under time pressure.

---

## Module 18 — Common Mistakes & Misconceptions

- **Skipping clarification** — designing the wrong thing.
- **God class** — one class doing everything (violates SRP).
- **Hard-coded `if/elif`** for policies — use Strategy/polymorphism.
- **Over-engineering** — 15 patterns for a toy; match complexity to requirements.
- **Ignoring extensibility** — can't answer "now add trucks / a new pricing rule".
- **No enums/dataclasses** — verbose, error-prone models.
- **Forgetting concurrency** in shared-resource designs (mention locks).

---

## Module 18 — MCQs (with answers & explanations)

**Q1.** The first step in an LLD interview is:
a) write classes  b) **clarify requirements**  c) pick patterns  d) code the DB

<details><summary>Answer</summary>**b.** Clarify scope/features before designing.</details>

**Q2.** Pluggable spot-allocation in a parking lot is best modelled with:
a) State  b) **Strategy**  c) Singleton  d) Observer

<details><summary>Answer</summary>**b.** Interchangeable allocation policies = Strategy.</details>

**Q3.** An elevator's idle/up/down behaviour fits:
a) Factory  b) **State**  c) Builder  d) Adapter

<details><summary>Answer</summary>**b.** Behaviour changes with internal state.</details>

**Q4.** A `Card` should be modelled as:
a) mutable class  b) **frozen dataclass (immutable, hashable value object)**  c) dict  d) tuple of strings

<details><summary>Answer</summary>**b.** Cards are value objects — immutable and hashable.</details>

**Q5.** A token-bucket rate limiter's clock should be:
a) hard-coded  b) **injected (for testability)**  c) global  d) random

<details><summary>Answer</summary>**b.** Inject the clock (DIP) so you can test without real time.</details>

**Q6.** Hard-coded `if kind == 'car'...elif...` for vehicle behaviour should become:
a) a Singleton  b) **polymorphism / Strategy**  c) a metaclass  d) a global

<details><summary>Answer</summary>**b.** Replace conditionals with polymorphic types.</details>

**Q7.** A single shared `ParkingLot` manager is often:
a) a Factory  b) **a Singleton or a module**  c) an Observer  d) a mixin

<details><summary>Answer</summary>**b.** One instance — Singleton (or just a module).</details>

**Q8.** The biggest LLD red flag is:
a) using enums  b) **one giant god class**  c) drawing UML  d) asking questions

<details><summary>Answer</summary>**b.** A god class violates SRP and signals poor decomposition.</details>

---

## Module 18 — Design/Practice Exercises (easy → hard)

1. **(easy)** Design a `Deck`/`Card` with Enums + frozen dataclass; deal a poker hand.
2. **(easy)** Add a `PricingStrategy` to the parking lot (flat vs hourly).
3. **(medium)** Design a Vending Machine as a State machine (Idle→HasMoney→Dispensing).
4. **(medium)** Design a Logger with levels using Chain of Responsibility.
5. **(hard)** Design an elevator bank (multiple elevators + dispatcher) with a
   pluggable scheduling Strategy.
6. **(hard, interview)** Full parking-lot design: clarify, UML, code core classes,
   then extend to payments and multiple levels — narrate your choices.

---

## Module 18 — Concept Review (one page)

**Low-Level Design** applies all prior modules to real systems via a repeatable
**process**: **clarify requirements → identify entities (nouns) → define
relationships & responsibilities (UML, SRP) → apply SOLID + patterns → code clean
classes → discuss extensions.** Recurring patterns map to recurring sub-problems:
**Strategy** for pluggable policies (parking allocation, pricing, scheduling),
**State** for modes (elevator, vending machine), **Factory** for type-based creation,
**Observer** for notifications, and **Singleton/module** for shared managers. Model
data with **enums** and **dataclasses** (frozen value objects like `Card`), inject
dependencies for testability (**DIP/DI**), and replace `if/elif` policy ladders with
**polymorphism/Strategy**. Interviewers reward **clarification, clean boundaries,
principled use of patterns, and extensibility** — and penalise god classes, hard-coded
conditionals, and jumping straight to code.

---

## Module 18 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| First LLD step | clarify requirements |
| Entities from | nouns; behaviour from verbs |
| Pluggable policy | Strategy |
| Mode-driven behaviour | State |
| Create by type | Factory |
| Notify many | Observer |
| One shared manager | Singleton / module |
| Model a Card | frozen dataclass + Enums |
| Rate limiter clock | inject it (DIP, testable) |
| Replace `if/elif` policy | polymorphism / Strategy |
| Biggest red flag | god class |
| Score driver | clarify + clean classes + patterns + extensibility |

---

## Module 18 — Pattern Recognition

- **See "different policies/algorithms"** → Strategy.
- **See "behaves differently in states/modes"** → State.
- **See "create objects based on input type"** → Factory.
- **See "many parts react to a change"** → Observer.
- **See "one global manager/registry"** → Singleton/module.
- **See a growing `if/elif` on a type** → polymorphism.
- **See "immutable record with equality"** → frozen dataclass value object.

---

## Module 18 — Revision Notes / Mini Cheat Sheet

```
LLD PROCESS: clarify -> entities(nouns) -> relationships+UML(SRP) ->
             SOLID+patterns -> code classes -> extensions/trade-offs. (talk out loud!)

MODEL WITH: Enum (fixed sets), dataclass (records), frozen dataclass (value objects),
            ABC/Protocol (interfaces), composition over inheritance.

PATTERN MAP:
  pluggable policy -> Strategy      modes/status -> State
  create by type   -> Factory       notify many  -> Observer
  one manager      -> Singleton/module   undo/queue -> Command   stepwise build -> Builder

INJECT dependencies (DIP) for testability (clock, db, strategy).
REPLACE if/elif policy ladders with polymorphism/Strategy (OCP).

CLASSIC PROMPTS: parking lot, elevator, deck of cards, rate limiter, vending machine,
  BookMyShow, splitwise, logger, notification service, chess/tic-tac-toe.
RED FLAGS: jump to code | god class | hard-coded if/elif | no extensibility.
```

> **Next module:** **Module 19 — Anti-patterns, Code Smells & Refactoring.** The
> flip side of good design: recognising god objects, spaghetti inheritance, and other
> smells — and the refactoring moves (extract class, replace conditional with
> polymorphism, composition over inheritance) that fix them.

---

## Module 18 — Summary

**Low-Level Design** is where OOP mastery is proven. It's a **repeatable process** —
clarify, identify entities, model relationships, apply **SOLID and patterns**, code
clean classes, and discuss extensions — not a test of cleverness. The recurring
**pattern-to-problem mappings** (Strategy for policies, State for modes, Factory for
creation, Observer for notification, Singleton/module for managers) let you decompose
almost any prompt, while **enums, dataclasses, and dependency injection** keep the
code clean and testable. Interviewers reward clarification, clean class boundaries,
principled patterns, and extensibility — so practise the classic prompts (parking
lot, elevator, deck of cards, rate limiter) until the process is second nature.

> **You have mastered this module when** you can: run the full LLD process on an
> unseen prompt; map sub-problems to the right patterns; code clean, enum/dataclass-
> based, extensible classes; and confidently handle the "now add X" follow-up.
