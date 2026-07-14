---
title: "Module 3 — Classes & Objects (the mechanics)"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — Classes & Objects (the mechanics)

> **Why this module matters.**
> Module 1 gave the *idea* of classes; Module 2 gave the *object model*. Now we
> write real classes correctly. Ninety percent of everyday Python OOP is here:
> `__init__` and `self`, **instance vs class attributes** (and the shared-mutable
> trap that reuses Module 2's aliasing lesson), and the **three method types**
> (`instance`, `@classmethod`, `@staticmethod`). Get these exactly right and the
> advanced modules become easy; get them fuzzy and you'll fight subtle bugs
> forever.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★★           | ★★★     | ★★★         | ★★★★★       | ★★★★★      |

**Most-asked concepts:** what is `self` (and why explicit); **instance vs class
attribute** difference + the **mutable-class-attribute bug**; `@classmethod` vs
`@staticmethod` vs instance method (when to use each); `__init__` vs `__new__`;
factory methods; `__dict__`.

**What you must be able to do after this module:** write a correct class with a
constructor, instance state, and methods; explain `self`; choose the right method
type for a job; explain and avoid the shared-mutable-class-attribute bug; and add
a `@classmethod` "alternative constructor."

---

## 3.1 Defining a Class — the anatomy

![Anatomy of a class: the class keyword, the __init__ constructor, self-assigned instance attributes, methods, and a class-level attribute.](images/m03_01_anatomy_class.png)

```python
class BankAccount:                    # 1. class statement + name (PascalCase)
    MIN_BALANCE = 0                   # 4. class attribute (shared by all instances)

    def __init__(self, owner, balance=0):   # 2. constructor (initialiser)
        self.owner = owner            # 3. instance attribute (per object)
        self.balance = balance

    def deposit(self, amount):        # a method (behaviour)
        self.balance += amount
```

- **`class BankAccount:`** — introduces a new type. Convention: **PascalCase**.
- **`__init__`** — the **initialiser**, run automatically right after a new object
  is created; it sets up the object's starting state.
- **`self.owner = owner`** — creates an **instance attribute** on *this* object.
- **`MIN_BALANCE = 0`** — a **class attribute**, shared by all instances.

Create objects by "calling" the class:

```python
acc = BankAccount("Nidhi", 1000)      # builds an object, runs __init__
print(acc.owner, acc.balance)         # Nidhi 1000
```

---

## 3.2 `self` — the most-asked beginner question

`self` is **the current object** — the specific instance the method is working on.
When you call `acc.deposit(100)`, Python rewrites it to
`BankAccount.deposit(acc, 100)` — the object before the dot is passed as the first
argument, which we conventionally name `self`.

![obj.deposit(100) is transformed by Python into BankAccount.deposit(obj, 100); the object becomes the self parameter automatically.](images/m03_02_self_binding.png)

```python
acc.deposit(100)              # you write this...
BankAccount.deposit(acc, 100) # ...Python effectively runs this
```

Key facts:

- `self` is **not a keyword** — it's a naming *convention*. You *could* name it
  anything, but **always use `self`** (readers expect it).
- Python makes the object-passing **explicit** (unlike Java's implicit `this`)
  because "explicit is better than implicit" — it makes method resolution and
  binding obvious.
- Inside a method, **every access to the object's own state goes through `self`**:
  `self.balance`, `self.deposit(...)`.

> **Interview one-liner:** *"`self` is the instance the method was called on;
> Python passes it automatically as the first parameter."*

---

## 3.3 Instance Attributes vs Class Attributes

- **Instance attribute** — belongs to **one object**; set via `self.x = ...`
  (usually in `__init__`). Each object has its own copy.
- **Class attribute** — belongs to **the class**; shared by **all** instances;
  defined in the class body.

![A class attribute species='canine' is shared by every Dog, while each dog has its own instance attribute name.](images/m03_03_instance_vs_class_attr.png)

```python
class Dog:
    species = "canine"            # class attribute (shared)
    def __init__(self, name):
        self.name = name          # instance attribute (per dog)

a = Dog("Rex"); b = Dog("Fifi")
print(a.species, b.species)       # canine canine  (shared)
print(a.name, b.name)             # Rex Fifi        (independent)

Dog.species = "Canis familiaris"  # change the class attr -> affects all
print(a.species)                  # Canis familiaris
```

**Reading vs writing (the subtle rule):** reading `a.species` falls back to the
class if the instance has no such attribute. But **assigning** `a.species = "wolf"`
creates a *new instance attribute* that **shadows** the class one — it does **not**
change the class attribute:

```python
a.species = "wolf"     # creates an INSTANCE attr on a, shadowing the class attr
print(a.species)       # wolf
print(b.species)       # canine  (b still sees the class attr)
print(Dog.species)     # canine  (class attr untouched)
```

This shadowing behaviour is a direct consequence of the **lookup order** below.

---

## 3.4 Attribute Lookup Order (and `__dict__`)

When you access `obj.x`, Python searches in order: the **instance's `__dict__`**,
then the **class's `__dict__`**, then **parent classes** (the MRO, Module 5), and
finally raises `AttributeError`.

![Attribute lookup: check the instance __dict__ first; if missing, the class __dict__; then base classes via the MRO; else AttributeError.](images/m03_04_attr_lookup.png)

```python
d = Dog("Rex")
print(d.__dict__)         # {'name': 'Rex'}          -> instance namespace
print(Dog.__dict__.keys())# dict_keys([... 'species', '__init__', ...])
```

Every object stores its instance attributes in `__dict__` (a plain dict). This is
why Python objects are so dynamic — you can add attributes at runtime:

```python
d.color = "brown"         # add a new attribute on the fly
print(d.__dict__)         # {'name': 'Rex', 'color': 'brown'}
```

(Module 8 shows how `__slots__` turns this off to save memory and lock the
attribute set.)

---

## 3.5 The Shared Mutable Class Attribute Bug (must-know)

Combine §3.3 with Module 2's aliasing lesson and you get a famous bug: a
**mutable** class attribute is **one object shared by every instance**.

![A mutable class attribute tricks=[] is a single shared list; dog1 appending 'sit' makes dog2 see it too.](images/m03_05_shared_mutable_trap.png)

```python
class Dog:
    tricks = []               # BUG: one list shared by ALL dogs
    def __init__(self, name):
        self.name = name
    def add_trick(self, t):
        self.tricks.append(t) # mutates the SHARED class list!

a = Dog("Rex"); b = Dog("Fifi")
a.add_trick("sit")
print(b.tricks)               # ['sit']  <-- Fifi has Rex's trick!
```

**Fix:** give each object its **own** mutable state in `__init__`:

```python
class Dog:
    def __init__(self, name):
        self.name = name
        self.tricks = []      # fresh list per dog
```

> **Rule:** class attributes are fine for **constants / shared immutables**
> (`MAX_SPEED = 120`), but **never** put mutable state (lists, dicts, sets) at
> class level unless you deliberately want it shared. This is the class-level twin
> of the mutable-default-argument bug (Module 2).

---

## 3.6 Three Kinds of Methods

![Three method kinds: an instance method receives self (the object); a classmethod receives cls (the class); a staticmethod receives nothing automatically.](images/m03_06_method_types.png)

| Kind | Decorator | First arg | Use when… |
|---|---|---|---|
| **Instance method** | (none) | `self` | you need the **object's state** (the default) |
| **Class method** | `@classmethod` | `cls` | you need the **class** — factories, per-class data |
| **Static method** | `@staticmethod` | none | it's a **helper** logically grouped with the class but uses neither `self` nor `cls` |

```python
class Pizza:
    sizes = {"S": 8, "M": 10, "L": 12}

    def __init__(self, size, toppings):
        self.size = size
        self.toppings = toppings

    def price(self):                       # instance: uses self (state)
        return Pizza.sizes[self.size] + 2 * len(self.toppings)

    @classmethod
    def margherita(cls, size):             # classmethod: alt constructor (factory)
        return cls(size, ["tomato", "mozzarella"])

    @staticmethod
    def is_valid_size(size):               # staticmethod: pure helper
        return size in Pizza.sizes

p = Pizza.margherita("M")                  # factory, returns a Pizza
print(p.price())                           # 10 + 2*2 = 14
print(Pizza.is_valid_size("XL"))           # False
```

> **Decision rule:** use `self` if you touch instance data; `cls` if you build/
> query the class (factories, subclass-aware); `@staticmethod` if you touch neither
> (and ask yourself whether it should just be a module-level function).

---

## 3.7 `@classmethod` as an Alternative Constructor (factory)

A very common Pythonic pattern: `__init__` takes the "canonical" arguments, and
`@classmethod` factories build objects from **other** inputs. Because they receive
`cls`, they build the **right subclass** automatically.

![A classmethod from_string parses '2026-07-10' and returns a Date object; using cls means subclasses get the correct type.](images/m03_07_factory_classmethod.png)

```python
class Date:
    def __init__(self, y, m, d):
        self.y, self.m, self.d = y, m, d

    @classmethod
    def from_string(cls, s):               # "2026-07-10" -> Date
        y, m, d = map(int, s.split("-"))
        return cls(y, m, d)                # cls, not Date -> subclass-friendly

    @classmethod
    def today(cls):
        import datetime
        t = datetime.date.today()
        return cls(t.year, t.month, t.day)

d = Date.from_string("2026-07-10")
```

The standard library uses this everywhere: `dict.fromkeys(...)`,
`datetime.fromtimestamp(...)`, `int.from_bytes(...)`.

---

## 3.8 Object Creation: `__init__` vs `__new__`

Creating an object is **two steps**:

![Object creation runs __new__ (allocate the object) then __init__ (initialise its state); __init__ returns None.](images/m03_08_object_creation.png)

1. **`__new__(cls, ...)`** — **allocates and returns** a new, empty object. Rarely
   overridden (used for immutables, singletons, metaclasses — Module 9).
2. **`__init__(self, ...)`** — **initialises** the already-created object's state.
   Returns `None` (returning anything else is a `TypeError`).

```python
class Point:
    def __new__(cls, *args):
        print("allocating")
        return super().__new__(cls)     # make the object
    def __init__(self, x, y):
        print("initialising")
        self.x, self.y = x, y

p = Point(1, 2)      # prints: allocating, then initialising
```

> **Interview trap:** *"Is `__init__` the constructor?"* Precisely, `__new__` is the
> constructor (it *creates*); `__init__` is the **initialiser** (it *configures*).
> In everyday speech people call `__init__` "the constructor," which is fine, but
> know the distinction.

---

## 3.9 Deleting & Inspecting Attributes

```python
del acc.balance           # remove an instance attribute
hasattr(acc, "balance")   # False
getattr(acc, "owner")     # 'Nidhi'  (like acc.owner)
setattr(acc, "owner", "X")# like acc.owner = "X"
vars(acc)                 # same as acc.__dict__
```

`getattr`/`setattr`/`hasattr` are the dynamic, string-keyed versions of dot access
— useful for frameworks, serialisation, and plugins (and the basis for Module 8's
`__getattr__` hooks).

---

## Module 3 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "What is `self`?" | "The object." | "The instance the method was called on; passed automatically as the first arg; a convention, not a keyword; explicit by design." |
| "Instance vs class attribute?" | "One per object vs shared." | Adds the read-fallback + write-shadowing rule and the **mutable class attribute bug**. |
| "`@classmethod` vs `@staticmethod`?" | "cls vs nothing." | "classmethod for factories/subclass-aware behaviour (gets `cls`); staticmethod for a namespaced helper touching neither state nor class — often better as a function." |
| "`__init__` vs `__new__`?" | "init sets values." | "`__new__` allocates/returns the object (the real constructor); `__init__` initialises it and returns None." |

---

## Module 3 — Exam Mapping

- **GATE CS:** output prediction with class vs instance attributes; method-binding
  questions; `__dict__` lookups.
- **SEBI / RBI IT:** definition of constructor; `self`; class vs object.
- **FAANG:** the mutable-class-attribute bug, classmethod factories, and clean
  choice of method type in a design.

---

## Module 3 — Common Mistakes & Misconceptions

- **Forgetting `self`** in a method signature (`def deposit(amount):`) →
  `TypeError` on call.
- **Mutable class attributes** for per-object state → shared-state bug (§3.5).
- **Thinking `a.species = x` changes the class attribute** — it creates an instance
  attribute that shadows it.
- **Using `@staticmethod` when you need `cls`** (breaks subclass factories).
- **Believing `__init__` creates the object** — `__new__` does; `__init__` only
  initialises.
- **Returning a value from `__init__`** → `TypeError`.

---

## Module 3 — MCQs (with answers & explanations)

**Q1.** `self` is:
a) a keyword  b) **a conventional name for the current instance**  c) a class  d) global

<details><summary>Answer</summary>**b.** It's the instance passed automatically as the first parameter; not a keyword.</details>

**Q2.** A mutable class attribute (`tricks = []`) shared by all instances is:
a) fine  b) **a bug — put per-object mutables in `__init__`**  c) impossible  d) faster

<details><summary>Answer</summary>**b.** All instances share one list; give each object its own in `__init__`.</details>

**Q3.** Which method should be a `@classmethod`?
a) one using `self.balance`  b) **an alternative constructor `from_string`**  c) a pure math helper  d) `__init__`

<details><summary>Answer</summary>**b.** Factories that build instances (and should respect subclasses) take `cls`.</details>

**Q4.** `a.species = "wolf"` when `species` is a class attribute:
a) changes it for all instances  b) errors  c) **creates an instance attr shadowing the class attr**  d) deletes it

<details><summary>Answer</summary>**c.** Assignment creates/updates an instance attribute; the class attribute is untouched.</details>

**Q5.** The real object-*creation* hook is:
a) `__init__`  b) **`__new__`**  c) `__call__`  d) `__create__`

<details><summary>Answer</summary>**b.** `__new__` allocates and returns the object; `__init__` initialises it.</details>

**Q6.** `@staticmethod` receives:
a) self  b) cls  c) **nothing automatically**  d) both

<details><summary>Answer</summary>**c.** It's a plain function namespaced under the class.</details>

**Q7.** Where are an instance's attributes stored (by default)?
a) `Class.__dict__`  b) **`instance.__dict__`**  c) a global table  d) `__slots__`

<details><summary>Answer</summary>**b.** In the per-instance `__dict__` (unless `__slots__` is used).</details>

**Q8.** Calling `acc.deposit(100)` is equivalent to:
a) `deposit(100)`  b) **`BankAccount.deposit(acc, 100)`**  c) `deposit(acc)`  d) `acc(100)`

<details><summary>Answer</summary>**b.** The instance is passed as `self`.</details>

---

## Module 3 — Design/Practice Exercises (easy → hard)

1. **(easy)** Write a `Circle` class with `radius`, an instance method `area()`, and
   a class attribute `PI = 3.14159`.
2. **(easy)** Add a `@staticmethod` `is_positive(r)` and a `@classmethod`
   `unit_circle(cls)` to `Circle`.
3. **(medium)** Demonstrate the shared-mutable-class-attribute bug with a `Team`
   class holding `members = []`, then fix it.
4. **(medium)** Add `@classmethod from_diameter(cls, d)` to `Circle` and show it
   returns the correct type when subclassed.
5. **(hard)** Implement a `Temperature` class storing Celsius, with class methods
   `from_fahrenheit` and `from_kelvin`, and an instance method `to_fahrenheit`.
6. **(hard, interview)** Given a bug report "all users share the same shopping
   cart," identify the likely cause in class code and fix it in two lines.

---

## Module 3 — Concept Review (one page)

A **class** bundles **class attributes** (shared) and **methods**; each **object**
built from it has its own **instance attributes** (set via `self` in `__init__`).
**`self`** is the current instance, passed automatically; `acc.m(x)` ≡
`Class.m(acc, x)`. Attribute access searches **instance `__dict__` → class → bases
(MRO)**; reading a class attribute falls back to the class, but **assigning**
creates a shadowing instance attribute. Putting **mutable** state at class level
shares one object across all instances — a classic bug; keep per-object mutables in
`__init__`. Methods come in three kinds: **instance** (`self`), **`@classmethod`**
(`cls`, for factories/subclass-aware code), and **`@staticmethod`** (a namespaced
helper). Object creation is **`__new__`** (allocate) then **`__init__`**
(initialise).

---

## Module 3 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| `self` is… | the current instance, passed automatically as first arg |
| `acc.deposit(100)` ≡ | `BankAccount.deposit(acc, 100)` |
| Instance vs class attribute | per-object (via `self`) vs shared (class body) |
| Reading vs writing a class attr on an instance | read falls back to class; write creates shadowing instance attr |
| Mutable class attribute danger | one object shared by all instances (bug) |
| Instance method gets | `self` |
| `@classmethod` gets | `cls` (factories, subclass-aware) |
| `@staticmethod` gets | nothing automatically (namespaced helper) |
| Real constructor hook | `__new__` (allocates); `__init__` initialises |
| Where instance attrs live | `instance.__dict__` |
| Alternative constructor pattern | `@classmethod from_x(cls, ...)` returning `cls(...)` |

---

## Module 3 — Pattern Recognition

- **See "build an object from a string / timestamp / other type"** → `@classmethod`
  factory.
- **See "helper that uses neither self nor cls"** → `@staticmethod` (or a module
  function).
- **See "all instances unexpectedly share data"** → mutable class attribute; move
  to `__init__`.
- **See "constant used by every instance"** → class attribute (`MAX_SIZE = ...`).
- **See "add/read attributes by name at runtime"** → `getattr`/`setattr`/`hasattr`.

---

## Module 3 — Revision Notes / Mini Cheat Sheet

```
CLASS body: class attributes (shared) + methods.  Instance attrs via self in __init__.
self  = current instance, auto-passed.  acc.m(x) == Class.m(acc, x).  (convention, not keyword)

ATTR LOOKUP: instance __dict__ -> class __dict__ -> bases (MRO) -> AttributeError.
READ class attr via instance -> fallback OK.  WRITE -> makes shadowing INSTANCE attr.

MUTABLE CLASS ATTR = shared by all instances (BUG). Constants OK; mutables -> __init__.

METHODS:
  instance   def m(self):      uses object state (default)
  @classmethod def m(cls):     factories / subclass-aware / per-class data
  @staticmethod def m():       helper, no self/cls (consider a plain function)

CREATION: __new__ (allocate, rare to override) -> __init__ (initialise, returns None).
DYNAMIC: getattr/setattr/hasattr/delattr; vars(obj) == obj.__dict__.
```

> **Next module:** **Module 4 — Encapsulation & Abstraction.** We take the class
> we can now write and *protect* it: public/`_protected`/`__private` conventions,
> **name mangling**, `@property` for computed and validated attributes, and
> **abstract base classes** to define interfaces — turning "a bag of attributes"
> into a well-guarded, well-abstracted type.

---

## Module 3 — Summary

A **class** defines shared **class attributes** and **methods**; each **object**
carries its own **instance attributes**, set through **`self`** (the current
instance, passed automatically) inside **`__init__`**. Attribute access follows
**instance → class → bases**, so reading a class attribute falls back to the class
while assigning creates a shadowing instance attribute. Never place **mutable**
state at class level unless you mean to share it — otherwise every instance shares
one object. Python offers **three method kinds**: instance methods (`self`),
**class methods** (`cls`, ideal for factories), and **static methods** (namespaced
helpers). Finally, object creation is really **`__new__`** (allocate) followed by
**`__init__`** (initialise). These mechanics are the everyday grammar of Python
OOP.

> **You have mastered this module when** you can: write a correct class with a
> constructor, instance state, and methods; explain `self` and method binding;
> choose instance/class/static methods correctly; reproduce and fix the
> shared-mutable-class-attribute bug; and add a `@classmethod` factory that works
> under subclassing.
