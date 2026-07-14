---
title: "Module 4 — Encapsulation & Abstraction"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — Encapsulation & Abstraction

> **Why this module matters.**
> Two of the four pillars live here. **Encapsulation** is *bundling data with the
> methods that guard it and hiding the internals*; **Abstraction** is *exposing a
> simple "what" while hiding the complex "how".* In Python both are done
> differently from Java/C++ — there is **no real `private`** — so the interesting
> question is *how Python achieves protection by convention*, when to reach for
> `@property`, and when NOT to (writing Java-style getters everywhere is an
> anti-pattern here). This module also introduces **Abstract Base Classes**, the
> tool for defining interfaces.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★★★     | ★★★         | ★★★★★       | ★★★★       |

**Most-asked concepts:** encapsulation vs abstraction (the difference!); `_x` vs
`__x` and **name mangling**; "does Python have private variables?"; `@property`
(getters/setters/validation, read-only); **ABCs** and `@abstractmethod`;
abstract class vs interface.

**What you must be able to do after this module:** explain encapsulation vs
abstraction crisply; describe `_protected`/`__private` and what name mangling does
(and doesn't) protect; convert a plain attribute into a validated `@property`
without changing caller code; and define an interface with an ABC.

---

## 4.1 Encapsulation — bundle + hide

**Encapsulation** = putting **data and the methods that operate on it in one unit
(the class)** and **restricting direct access to the data**, exposing a controlled
API instead. The goal: protect **invariants** (rules that must always hold, e.g.
"balance ≥ 0") by funnelling all changes through methods.

![An object like a capsule: the balance data is sealed inside; outside code interacts only through deposit()/withdraw() methods.](images/m04_01_encapsulation_capsule.png)

```python
class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance          # hidden state (by convention)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("must be positive")
        self._balance += amount          # the ONLY sanctioned way to change it

    @property
    def balance(self):                   # read-only view
        return self._balance
```

Without encapsulation, any code could do `acc._balance = -1_000_000` and break the
invariant. Encapsulation makes the *intended* path the *guarded* path.

> **Analogy:** a **medicine capsule** — the active ingredients (data) are sealed
> inside; you interact via the capsule (the API), not by touching the powder.

---

## 4.2 Access Levels in Python (all by convention)

Unlike Java/C++, Python has **no `private`/`protected`/`public` keywords**. It uses
**naming conventions** plus one mild mechanism (name mangling).

![Three conventions: public 'name' (use freely), _name (protected, internal), __name (private-ish, name-mangled); none is truly locked.](images/m04_02_access_levels.png)

| Convention | Meaning | Enforced? |
|---|---|---|
| `name` | **public** — part of the intended API | — |
| `_name` | **"protected"** — internal; "please don't touch from outside" | No (convention only) |
| `__name` | **"private-ish"** — triggers **name mangling** | Partially (mangled, not locked) |

```python
class Demo:
    def __init__(self):
        self.public = 1
        self._internal = 2      # convention: don't rely on this from outside
        self.__mangled = 3      # becomes _Demo__mangled
```

> **The Python philosophy** (PEP 8): *"We're all consenting adults here."* The
> language trusts you rather than locking doors. `_x` communicates intent; it does
> not prevent access.

---

## 4.3 Name Mangling — what `__x` really does

A name with **two leading underscores** (and at most one trailing) is **mangled**
by the compiler to `_ClassName__name`. Its purpose is **not security** — it is to
**avoid accidental name clashes** between a class and its subclasses.

![self.__balance in class Account is stored as _Account__balance; acc.__balance raises AttributeError, but acc._Account__balance still works.](images/m04_03_name_mangling.png)

```python
class Account:
    def __init__(self):
        self.__balance = 100        # stored as _Account__balance

acc = Account()
# print(acc.__balance)             # AttributeError
print(acc._Account__balance)        # 100  -> still reachable (not truly private)
print(acc.__dict__)                 # {'_Account__balance': 100}
```

Why it helps subclasses: if a base class uses `self.__id` and a subclass also uses
`self.__id`, mangling keeps them as `_Base__id` and `_Sub__id` — **no collision**.

> **Interview answer:** *"`__x` is name-mangled to `_Class__x` to prevent
> subclass name clashes, not to enforce privacy. Python has no true private members;
> `_x` is a convention and `__x` is mangling."*

---

## 4.4 `@property` — attribute syntax, method power

Often you start with a plain public attribute, then later need **validation** or a
**computed value**. In Java you'd have written getters/setters up front "just in
case." In Python you **don't** — you start public and *upgrade to a `@property`
later without changing any caller code*.

![obj.temp looks like a plain attribute access but runs a getter/setter method behind it; callers never use parentheses or change.](images/m04_04_property.png)

A `@property` turns a method into something accessed like an attribute:

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):                 # accessed as circle.area (NO parentheses)
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.area)                       # 314.159  -> computed on access, read-only
```

### Getter + setter + validation

![Assigning c.temp = -500 routes through the @temp.setter, which validates: below -273.15 it raises, otherwise it stores the value.](images/m04_05_getter_setter_flow.png)

```python
class Temperature:
    def __init__(self, celsius=0):
        self.celsius = celsius       # goes through the setter below

    @property
    def celsius(self):               # getter
        return self._celsius

    @celsius.setter
    def celsius(self, value):        # setter with validation
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):            # computed, read-only
        return self._celsius * 9 / 5 + 32

t = Temperature(25)
print(t.fahrenheit)                  # 77.0
t.celsius = 100                      # validated on the way in
# t.celsius = -500                   # ValueError
```

- **Read-only property:** define only a getter (like `fahrenheit`/`area`).
- **Deleter:** `@celsius.deleter` handles `del obj.celsius`.

> **Golden rule:** don't write `get_x()`/`set_x()` in Python. Expose the attribute
> publicly; if logic is needed later, convert it to a `@property` — callers keep
> writing `obj.x`.

---

## 4.5 Abstraction — expose *what*, hide *how*

**Abstraction** is presenting a **simple, essential interface** and hiding the
**complex implementation** behind it. You call `list.sort()`; you neither know nor
care that it runs Timsort.

![list.sort() is the simple 'what' you call; the Timsort algorithm underneath is the 'how', hidden from you.](images/m04_06_abstraction_layers.png)

- **Encapsulation** answers *"who can touch the data?"* (bundling + hiding).
- **Abstraction** answers *"what does the user need to see?"* (simplify + hide
  complexity).

They're related but distinct — a favourite interview distinction:

| | Encapsulation | Abstraction |
|---|---|---|
| Focus | **data protection** (access control) | **design simplicity** (hide complexity) |
| Level | implementation detail | design/interface level |
| Achieved by | `_`/`__`, properties, methods | ABCs, interfaces, clean method APIs |
| Question | "how do I protect state?" | "what should the caller see?" |

---

## 4.6 Abstract Base Classes (ABCs) — defining an interface

An **abstract class** cannot be instantiated; it defines a **contract** (methods
subclasses must implement). Use the `abc` module.

![An ABC Shape with an abstractmethod area() cannot be instantiated; Circle and Square implement area() and work, but a Blob without area() raises TypeError.](images/m04_07_abc.png)

```python
from abc import ABC, abstractmethod

class Shape(ABC):                    # inherit ABC
    @abstractmethod
    def area(self):                  # no body — subclasses MUST define it
        ...

    def describe(self):              # ABCs may also have concrete methods
        return f"A shape with area {self.area()}"

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

# Shape()          # TypeError: Can't instantiate abstract class Shape
c = Circle(10)
print(c.describe())                  # A shape with area 314.159

class Blob(Shape):                   # forgot to implement area()
    pass
# Blob()           # TypeError: abstract method 'area' not implemented
```

**Why ABCs help:** they turn "I hope subclasses implement `area`" into a
**guaranteed, checked contract** — you find missing methods at instantiation time,
not deep in production. They also enable **`isinstance` checks against an
interface** and can register virtual subclasses. (Structural alternatives —
`Protocol`s — come in Module 11.)

- **Abstract class** = a base with at least one `@abstractmethod`; may hold shared
  concrete methods + state.
- **"Interface"** = (informally) an abstract class whose methods are *all* abstract
  — Python has no `interface` keyword; ABCs and Protocols fill that role.

---

## 4.7 When NOT to Over-Encapsulate (Pythonic balance)

![Pythonic rule: start with a public attribute; only if you later need validation, convert it to a @property — caller code (obj.temp) never changes.](images/m04_08_pythonic_property.png)

- **Don't** wrap every attribute in a getter/setter "for safety." Start public.
- **Do** switch to `@property` the moment you need validation, computation, or a
  read-only view — callers are unaffected.
- **Don't** use `__x` reflexively; reserve it for genuine subclass-clash avoidance.
  `_x` is the usual "internal" marker.

> This restraint is a hallmark of *Pythonic* code and a thing senior interviewers
> listen for: "In Python I'd expose it directly and promote to a property if I need
> logic, rather than writing boilerplate accessors."

---

## Module 4 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Encapsulation vs abstraction?" | "Hiding data vs hiding complexity." | Adds the table: encapsulation = access control (implementation); abstraction = simple interface (design); one protects state, the other simplifies use. |
| "Does Python have private?" | "Use `__`." | "No true private. `_x` is convention; `__x` is **name mangling** to `_Class__x` to avoid subclass clashes, still reachable. Privacy is by convention — 'consenting adults.'" |
| "Why `@property`?" | "Getters/setters." | "To add validation/computation/read-only behind attribute syntax *without changing callers* — so you avoid upfront Java-style accessors." |
| "What's an ABC for?" | "A base class." | "To define a checked interface: abstract methods that subclasses must implement; can't instantiate the ABC; failures surface at instantiation." |

---

## Module 4 — Exam Mapping

- **GATE CS:** definitions and differences of encapsulation/abstraction; access
  specifiers (careful — Python differs from C++/Java theory).
- **SEBI / RBI IT:** encapsulation definition; access modifier concepts.
- **FAANG:** properties with validation in live code; ABC-based design; the
  Pythonic "start public" judgment; name-mangling trivia.

---

## Module 4 — Common Mistakes & Misconceptions

- **"`__x` makes it private."** It's name-mangled, still accessible via
  `_Class__x`.
- **Confusing encapsulation with abstraction.** Access control vs interface
  simplicity.
- **Writing `get_x()`/`set_x()` everywhere.** Un-Pythonic; use public attrs →
  `@property` when needed.
- **Calling a property with `()`** — `c.area()` fails; it's `c.area`.
- **Instantiating an ABC** — `TypeError`; ABCs are contracts, not concrete types.
- **Putting validation in `__init__` only** — direct later assignment bypasses it;
  a `@property` setter validates *every* assignment.

---

## Module 4 — MCQs (with answers & explanations)

**Q1.** In Python, `__balance` inside `class Account` is stored as:
a) `__balance`  b) **`_Account__balance`**  c) hidden/inaccessible  d) `private_balance`

<details><summary>Answer</summary>**b.** Name mangling rewrites it to `_Account__balance`.</details>

**Q2.** The main purpose of name mangling is:
a) security  b) speed  c) **avoiding name clashes in subclasses**  d) encryption

<details><summary>Answer</summary>**c.** It prevents accidental attribute collisions between base and subclass.</details>

**Q3.** Encapsulation is best described as:
a) hiding complexity behind a simple interface  b) **bundling data with methods and controlling access to it**  c) inheritance  d) overloading

<details><summary>Answer</summary>**b.** That's encapsulation; option (a) is abstraction.</details>

**Q4.** You access a `@property` named `area` via:
a) `obj.area()`  b) **`obj.area`**  c) `obj.get_area()`  d) `area(obj)`

<details><summary>Answer</summary>**b.** Properties use attribute syntax — no parentheses.</details>

**Q5.** Trying to instantiate an ABC with an unimplemented abstract method:
a) works  b) warns  c) **raises TypeError**  d) returns None

<details><summary>Answer</summary>**c.** Python refuses to instantiate until all abstract methods are implemented.</details>

**Q6.** The Pythonic approach to a field that might later need validation:
a) write getters/setters now  b) **expose it publicly, convert to `@property` later**  c) use `__field`  d) make it global

<details><summary>Answer</summary>**b.** Callers keep `obj.field`; you add logic transparently later.</details>

**Q7.** Which enforces a *checked* interface contract?
a) `_method`  b) a docstring  c) **`@abstractmethod` in an ABC**  d) a comment

<details><summary>Answer</summary>**c.** Abstract methods must be implemented by concrete subclasses.</details>

**Q8.** A read-only property is created by:
a) `@property.readonly`  b) **defining only a getter (no setter)**  c) using `__`  d) `final`

<details><summary>Answer</summary>**b.** With no setter, assignment raises `AttributeError`.</details>

---

## Module 4 — Design/Practice Exercises (easy → hard)

1. **(easy)** Give `BankAccount` a read-only `balance` property and a `deposit`
   method that validates positivity.
2. **(easy)** Show that `__x` is reachable via `_Class__x` and print `__dict__`.
3. **(medium)** Convert a public `Rectangle.width` into a validated property that
   rejects non-positive values — without changing existing caller code.
4. **(medium)** Define an ABC `PaymentMethod` with abstract `pay(amount)`; implement
   `CardPayment` and `UpiPayment`; prove `PaymentMethod()` fails.
5. **(hard)** Add a computed, read-only `Rectangle.area` and a settable `Rectangle.
   diagonal` that adjusts width/height proportionally, all via properties.
6. **(hard, interview)** Explain to a Java developer why you wouldn't add getters
   and setters to every field in Python, and demonstrate the "promote to property"
   upgrade path.

---

## Module 4 — Concept Review (one page)

**Encapsulation** bundles data with the methods that guard it and controls access
to protect invariants; **abstraction** presents a simple interface while hiding
complex implementation. Python has **no real access modifiers**: `name` is public,
`_name` is a "please don't touch" convention, and `__name` is **name-mangled** to
`_Class__name` to avoid subclass clashes (still reachable — privacy is by
convention). **`@property`** lets a method be used with attribute syntax, enabling
**validation, computed values, and read-only fields** *without changing callers* —
so Python code starts with public attributes and promotes to properties only when
logic is needed (never upfront getters/setters). **Abstract Base Classes** (`abc`
module, `@abstractmethod`) define **checked interfaces**: they can't be
instantiated, and concrete subclasses must implement every abstract method.

---

## Module 4 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Encapsulation (1 line) | bundle data + methods; control access to protect invariants |
| Abstraction (1 line) | expose a simple interface; hide complex implementation |
| `_x` means | "internal / protected" by convention (not enforced) |
| `__x` does what | name mangling to `_Class__x` (avoid subclass clashes) |
| Does Python have private? | No true private; convention + mangling only |
| `@property` gives you | method logic behind attribute syntax (validate/compute/read-only) |
| Access a property | `obj.x` (no parentheses) |
| Read-only property | define only a getter |
| ABC purpose | define a checked interface; can't instantiate; forces implementation |
| Abstract method decorator | `@abstractmethod` |
| Pythonic accessor rule | start public → promote to `@property` when logic is needed |

---

## Module 4 — Pattern Recognition

- **See "this value must always be valid"** → `@property` setter with validation.
- **See "computed from other fields, no storage"** → read-only `@property`.
- **See "several classes must all provide method X"** → ABC with `@abstractmethod`.
- **See "internal helper attribute"** → prefix `_`.
- **See "base and subclass both use `__id`"** → mangling keeps them separate.
- **See Java-style `get_/set_` in Python** → refactor to public attr / property.

---

## Module 4 — Revision Notes / Mini Cheat Sheet

```
ENCAPSULATION = bundle data + methods + control access (protect invariants).
ABSTRACTION   = simple interface, hide complexity. (encaps=access; abstr=design)

ACCESS (convention only):
  name    public (API)
  _name   "protected" internal hint
  __name  name-mangled -> _Class__name (avoid subclass clashes; NOT private)
Python has NO true private -> "we're all consenting adults".

@property: method used as attribute (obj.x, no parens).
  getter only            -> read-only / computed
  @x.setter def x(...)   -> validate on assignment
  @x.deleter             -> handle del obj.x
RULE: start public; promote to property later; NO upfront getters/setters.

ABC (abc module): class Shape(ABC); @abstractmethod def area(self): ...
  - cannot instantiate ABC or subclass missing an abstract method (TypeError)
  - defines a CHECKED interface; may include concrete methods/state.
```

> **Next module:** **Module 5 — Inheritance & Composition.** With encapsulated,
> abstracted classes in hand, we reuse and extend them: single/multiple
> inheritance, `super()`, the **Method Resolution Order (MRO)** and the **diamond
> problem**, and the crucial design maxim **"favour composition over
> inheritance."**

---

## Module 4 — Summary

**Encapsulation** and **abstraction** are two of OOP's four pillars.
Encapsulation **bundles data with the methods that guard it** and controls access
to protect invariants; abstraction **hides complex implementation behind a simple
interface**. Python enforces neither with keywords — it uses **conventions**
(`_name` for internal, `__name` for **name mangling** that dodges subclass clashes)
under the "consenting adults" philosophy. The **`@property`** decorator provides
validation, computed values, and read-only fields behind ordinary attribute
syntax, so Python code favours public attributes upgraded to properties on demand
rather than upfront accessors. **Abstract Base Classes** define **checked
interfaces** that concrete subclasses must fulfil. Together these give you classes
that are safe to use, clean to read, and reliable to extend.

> **You have mastered this module when** you can: state the difference between
> encapsulation and abstraction; explain `_x`, `__x`, and name mangling accurately;
> convert a plain attribute into a validated property with zero caller changes;
> and define and use an ABC as an interface.
