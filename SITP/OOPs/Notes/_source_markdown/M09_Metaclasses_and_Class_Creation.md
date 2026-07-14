---
title: "Module 9 — Metaclasses & Class Creation"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 9 — Metaclasses & Class Creation

> **Why this module matters.**
> This is the deepest layer of Python OOP — and the one that scares people. The key
> unlock: **a class is itself an object**, and just as objects are created by
> classes, **classes are created by metaclasses** (`type` by default). Once you see
> that `class` is *sugar* for a call to `type(...)`, metaclasses stop being magic.
> They power frameworks you use daily (Django models, SQLAlchemy, ABCs, enums). But
> the senior lesson is **restraint**: modern Python (`__init_subclass__`, class
> decorators) covers most needs, so metaclasses are a last resort. Interviewers use
> this topic to separate "reads the docs" from "understands the model."

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★       | ★           | ★★★★        | ★★★        |

**Most-asked concepts:** "classes are objects" / `type(Dog) is type`; `type` as the
class factory (`type(name, bases, dict)`); what a metaclass is and when it fires;
metaclass `__new__`/`__init__`/`__call__`; `__init_subclass__` vs metaclass vs class
decorator; real use cases (registries, ABCs, ORMs); when NOT to use metaclasses.

**What you must be able to do after this module:** explain the object→class→
metaclass chain; build a class dynamically with `type(...)`; write a simple
metaclass and an `__init_subclass__` hook; and choose the *lightest* tool for a
class-customisation task.

---

## 9.1 Classes Are Objects

In Python, a class is a **first-class object** — you can assign it to a variable,
pass it to functions, and inspect its type. And its type is **`type`**.

![Chain: dog1 is an instance of Dog; Dog is an instance of type. type(dog1) is Dog and type(Dog) is type — a class is an instance of its metaclass.](images/m09_01_classes_are_objects.png)

```python
class Dog: pass
d = Dog()

print(type(d))       # <class '__main__.Dog'>  -> d is an instance of Dog
print(type(Dog))     # <class 'type'>           -> Dog is an instance of type!
print(isinstance(Dog, type))  # True

Alias = Dog          # classes are objects: assignable
print(Alias().__class__)      # Dog
```

So there are **two levels**: objects are instances of classes; **classes are
instances of metaclasses**. The default metaclass is **`type`**.

---

## 9.2 `type` — the Class Factory

`type` has two jobs. Called with **one** argument it returns an object's type. Called
with **three** arguments it **creates a new class dynamically**:

```python
type(name, bases, namespace)
```

![type('Dog', (Animal,), {'bark': fn}) — name, tuple of bases, and a namespace dict — returns a brand-new class object; the class statement is sugar for this call.](images/m09_02_type_factory.png)

```python
def bark(self): return "Woof"

# These two are EQUIVALENT:
class Dog(Animal):          # (A) the familiar statement
    x = 1
    def bark(self): return "Woof"

Dog = type("Dog", (Animal,), {"x": 1, "bark": bark})   # (B) the raw call
```

- **name** — the class's `__name__` (a string).
- **bases** — a tuple of parent classes.
- **namespace** — a dict of attributes/methods (the class body).

> **The big reveal:** the `class` statement is **syntactic sugar** — Python executes
> the class body into a namespace dict, then calls the metaclass (`type` by default)
> to build the class object. Metaclasses hook *that* call.

---

## 9.3 What Is a Metaclass?

A **metaclass** is "the class of a class" — the thing that **creates classes**. Since
`type` is the default, a custom metaclass **subclasses `type`** and overrides its
creation hooks.

![A metaclass Meta(type) can override __new__ (create the class object), __init__ (initialise the new class), and __call__ (runs when you instantiate the class).](images/m09_03_metaclass_hooks.png)

| Hook | Fires when | Receives |
|---|---|---|
| `__new__(mcs, name, bases, ns)` | the class is **created** | metaclass, class name, bases, namespace |
| `__init__(cls, name, bases, ns)` | right after creation | the new class |
| `__call__(cls, *args, **kw)` | you **instantiate** the class (`MyClass()`) | the class + constructor args |

```python
class UpperMeta(type):
    def __new__(mcs, name, bases, ns):
        # force all method names to be recorded, add a marker, etc.
        ns["created_by"] = "UpperMeta"
        return super().__new__(mcs, name, bases, ns)

class Service(metaclass=UpperMeta):
    pass

print(Service.created_by)     # UpperMeta  -> injected at class-creation time
```

The `metaclass=` keyword tells Python which metaclass to use to build the class.

---

## 9.4 The Class-Creation Flow

![When Python reads a class statement: it executes the class body, builds the namespace dict, calls the metaclass (type by default) to create the class, and returns the class object.](images/m09_04_class_creation_flow.png)

Step by step, when Python encounters `class X(Base, metaclass=Meta): ...`:

1. **Determine the metaclass** (`Meta`, or `type`, or inherited from bases).
2. **`__prepare__`** (optional) returns the namespace mapping to use for the body.
3. **Execute the class body** into that namespace (methods, class attrs).
4. **Call the metaclass**: `Meta(name, bases, namespace)` → runs `__new__` then
   `__init__`.
5. **Bind** the resulting class object to the name `X`.

All of this happens **once, at definition time** — not per instance. (Instance
creation later goes through the metaclass's `__call__`, which by default runs the
class's `__new__` + `__init__` — connecting back to Module 3.)

---

## 9.5 Real Use Cases

Metaclasses aren't academic — they run real frameworks:

- **`ABCMeta`** (Module 4's ABCs) is a metaclass that enforces abstract methods.
- **Django ORM / SQLAlchemy**: a model class's fields are turned into columns/
  descriptors by a metaclass at class-creation time.
- **Enums** (`enum.EnumMeta`): converts class attributes into singleton members.
- **Registries / plugins**: auto-collect subclasses.
- **Enforcing constraints**: require certain methods/attributes on every subclass.

### Example: an auto-registering plugin registry

![A PluginMeta metaclass causes each subclass (CsvPlugin, JsonPlugin) to add itself to a central REGISTRY dict automatically as it is defined.](images/m09_05_registry_pattern.png)

```python
class PluginMeta(type):
    registry = {}
    def __init__(cls, name, bases, ns):
        super().__init__(name, bases, ns)
        if bases:                          # skip the base class itself
            PluginMeta.registry[cls.format] = cls

class Plugin(metaclass=PluginMeta):
    format = None

class CsvPlugin(Plugin):  format = "csv"
class JsonPlugin(Plugin): format = "json"

print(PluginMeta.registry)   # {'csv': <CsvPlugin>, 'json': <JsonPlugin>}
```

Every subclass registers itself **automatically** at definition — no manual list to
maintain. This is the canonical "why a metaclass" example.

---

## 9.6 The Lighter Alternatives (prefer these!)

Most "do something per subclass" or "tweak a class" needs **don't require a
metaclass** anymore.

### `__init_subclass__` — hook subclass creation

![A Base class defining __init_subclass__ runs that hook automatically for each subclass created — covering most registry use-cases without a metaclass.](images/m09_06_init_subclass.png)

```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, **kwargs):     # runs for EACH subclass
        super().__init_subclass__(**kwargs)
        Plugin.registry[cls.__name__] = cls

class CsvPlugin(Plugin): pass                 # auto-registered, no metaclass!
print(Plugin.registry)                        # {'CsvPlugin': <CsvPlugin>}
```

Added in Python 3.6, `__init_subclass__` covers the registry/validation cases that
used to need a metaclass — with far less complexity.

### Class decorators — post-process a finished class

![A class decorator like @register receives the User class after creation and can modify or wrap it, then return it — exactly what @dataclass does.](images/m09_07_class_decorator.png)

```python
def register(cls):
    REGISTRY[cls.__name__] = cls
    return cls                     # return the (possibly modified) class

@register
class User: ...
```

`@dataclass` (Module 10) is exactly this pattern — a class decorator that rewrites
the class to add `__init__`, `__repr__`, etc.

---

## 9.7 Which Tool? (choose the simplest)

![Decision: for a per-subclass hook use __init_subclass__; to tweak one class use a class decorator; only for deep control of class creation use a metaclass. Tim Peters: 'If you wonder whether you need metaclasses, you don't.'](images/m09_08_when_metaclass.png)

| Need | Tool |
|---|---|
| Run code for **each subclass** | `__init_subclass__` |
| Customise attribute at class level | `__set_name__` descriptor (Module 8) |
| Modify **one** class after creation | **class decorator** |
| Deep control of the **creation process** for a family of classes | **metaclass** |

> **Tim Peters' rule:** *"Metaclasses are deeper magic than 99% of users should ever
> worry about. If you wonder whether you need them, you don't (the people who
> actually need them know with certainty, and don't need an explanation about why)."*

---

## Module 9 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "What's a metaclass?" | "A class of a class." | "The type that creates classes — `type` by default. The `class` statement is sugar for `type(name, bases, ns)`; a metaclass overrides `__new__`/`__init__` to hook class creation." |
| "`type(Dog)`?" | (unsure) | "`type` — because `Dog` is an instance of the metaclass `type`; objects→classes→metaclasses." |
| "When would you use one?" | "Never?" | "Rarely — for framework-level auto-registration, enforcing subclass contracts, ORMs. But I'd try `__init_subclass__` or a class decorator first." |
| "`__init_subclass__` vs metaclass?" | (unaware) | "`__init_subclass__` (3.6+) hooks subclass creation without a metaclass and covers most registry/validation cases with far less complexity." |

---

## Module 9 — Exam Mapping

- **GATE CS:** essentially untested at depth; "class is an object" may appear.
- **SEBI / RBI IT:** not tested.
- **FAANG / senior backend:** conceptual — "explain metaclasses," "how does Django
  build models," "class vs metaclass," and the judgment to *avoid* them.

---

## Module 9 — Common Mistakes & Misconceptions

- **Reaching for a metaclass** when `__init_subclass__` or a decorator suffices.
- **Confusing `__new__` on a class (instance creation) with `__new__` on a metaclass
  (class creation).**
- **Metaclass conflicts** in multiple inheritance: all bases must have compatible
  metaclasses (`metaclass conflict` error).
- **Thinking metaclass code runs per instance** — it runs at **class definition**.
- **Overriding `__call__` incorrectly** and breaking normal instantiation.

---

## Module 9 — MCQs (with answers & explanations)

**Q1.** `type(Dog)` where `class Dog: pass` returns:
a) `Dog`  b) `object`  c) **`type`**  d) `class`

<details><summary>Answer</summary>**c.** `Dog` is an instance of the metaclass `type`.</details>

**Q2.** The `class` statement is essentially sugar for:
a) `object(...)`  b) **`type(name, bases, namespace)`**  c) `class(...)`  d) `new(...)`

<details><summary>Answer</summary>**b.** Python builds the class by calling the metaclass with these three arguments.</details>

**Q3.** A custom metaclass typically:
a) inherits `object`  b) **inherits `type`**  c) uses `@dataclass`  d) is a function

<details><summary>Answer</summary>**b.** Metaclasses subclass `type` and override its hooks.</details>

**Q4.** Metaclass `__new__`/`__init__` run:
a) per instance  b) **at class definition**  c) at import of any module  d) never

<details><summary>Answer</summary>**b.** They fire once when the class is created.</details>

**Q5.** To run code for every subclass without a metaclass, use:
a) `__new__`  b) **`__init_subclass__`**  c) `__slots__`  d) `__call__`

<details><summary>Answer</summary>**b.** `__init_subclass__` (3.6+) hooks subclass creation.</details>

**Q6.** `@dataclass` is an example of a:
a) metaclass  b) **class decorator**  c) descriptor  d) mixin

<details><summary>Answer</summary>**b.** It post-processes the class to add methods.</details>

**Q7.** Which real feature is powered by a metaclass?
a) list comprehension  b) f-strings  c) **ABCs (`ABCMeta`)**  d) decorators

<details><summary>Answer</summary>**c.** `ABCMeta` enforces abstract methods.</details>

**Q8.** Instantiating a class (`MyClass()`) invokes the metaclass's:
a) `__new__`  b) `__init__`  c) **`__call__`**  d) `__prepare__`

<details><summary>Answer</summary>**c.** `type.__call__` orchestrates the class's `__new__` + `__init__`.</details>

---

## Module 9 — Design/Practice Exercises (easy → hard)

1. **(easy)** Create a class dynamically with `type("Cat", (), {"speak": lambda
   self: "Meow"})` and instantiate it.
2. **(easy)** Show `type(int)`, `type(type)`, and `isinstance(str, type)`.
3. **(medium)** Write an auto-registry using `__init_subclass__`, then rewrite it
   using a metaclass — compare complexity.
4. **(medium)** Write a metaclass that raises if a subclass forgets to define a
   `handle()` method.
5. **(hard)** Write a metaclass that automatically wraps every method with timing
   logging.
6. **(hard, interview)** Explain, with the object→class→metaclass chain, why
   `type(type) is type`, and why that isn't an infinite regress.

---

## Module 9 — Concept Review (one page)

A **class is an object** — an **instance of a metaclass**, which is **`type`** by
default (so `type(Dog) is type`). The `class` statement is **sugar** for
**`type(name, bases, namespace)`**: Python runs the class body into a namespace dict,
then calls the metaclass to build the class object — **once, at definition time**. A
**custom metaclass** subclasses `type` and overrides **`__new__`** (create class),
**`__init__`** (init class), and **`__call__`** (control instantiation). Metaclasses
power **ABCs, ORMs, enums, and registries**. But modern Python offers lighter tools:
**`__init_subclass__`** (per-subclass hook), **`__set_name__`** descriptors, and
**class decorators** (like `@dataclass`) — which cover most needs. Prefer the
lightest tool; a metaclass is a **last resort** for deep, family-wide control of
class creation.

---

## Module 9 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| `type(Dog)` where Dog is a class | `type` (the metaclass) |
| A metaclass is | the class of a class; creates classes |
| Default metaclass | `type` |
| `class` statement ≡ | `type(name, bases, namespace)` |
| Custom metaclass inherits | `type` |
| Metaclass hooks | `__new__`, `__init__` (class creation), `__call__` (instantiation) |
| When metaclass code runs | at class definition time |
| Per-subclass hook without metaclass | `__init_subclass__` (3.6+) |
| Post-process one class | class decorator (`@dataclass`) |
| Real metaclass users | ABCs (`ABCMeta`), Django/SQLAlchemy, Enum |
| Metaclass rule of thumb | if unsure you need one, you don't |

---

## Module 9 — Pattern Recognition

- **See "auto-collect all subclasses"** → `__init_subclass__` (or metaclass).
- **See "enforce every subclass defines X"** → `__init_subclass__`/metaclass check.
- **See "rewrite a class to add methods"** → class decorator (`@dataclass`).
- **See "type(Dog) is type"** → classes are instances of metaclasses.
- **See framework "declare fields as class attributes → become columns"** →
  metaclass/descriptors (ORM style).
- **See a metaclass where a decorator would do** → simplify.

---

## Module 9 — Revision Notes / Mini Cheat Sheet

```
CLASSES ARE OBJECTS: type(obj)=Class ; type(Class)=metaclass (type by default).
type(name, bases, namespace) -> builds a class. 'class' statement is SUGAR for this.

METACLASS = subclass of type; overrides:
  __new__(mcs, name, bases, ns)  create class object
  __init__(cls, ...)             init the new class
  __call__(cls, *a)              runs on INSTANTIATION (MyClass())
Runs at CLASS DEFINITION time (not per instance). Set via class X(metaclass=Meta).

USE CASES: ABCMeta, Django/SQLAlchemy ORMs, Enum, plugin registries, subclass constraints.

PREFER LIGHTER TOOLS:
  __init_subclass__(cls)  -> per-subclass hook (3.6+) — covers most registries
  __set_name__            -> descriptor knows its attr name (M8)
  class decorator         -> post-process one class (@dataclass)
RULE: metaclass is a LAST RESORT. "If you wonder if you need one, you don't."
```

> **Next module:** **Module 10 — Modern Python OOP Tooling.** We come back down to
> earth with the classes you'll actually write daily: **`@dataclass`** (auto
> `__init__`/`__repr__`/`__eq__`), **`NamedTuple`**, **`Enum`**, and **`attrs`** —
> all built on the descriptor/decorator/metaclass machinery of the last two modules,
> but packaged so you write almost no boilerplate.

---

## Module 9 — Summary

The deepest layer of Python OOP rests on one fact: **classes are objects**, created
by **metaclasses** — `type` by default, so `type(Dog) is type`. The `class`
statement is **sugar** for **`type(name, bases, namespace)`**, and a custom
**metaclass** (subclassing `type`) can hook **class creation** via
`__new__`/`__init__` and **instantiation** via `__call__`, all at **definition
time**. This machinery powers **ABCs, ORMs, enums, and auto-registries**. Yet the
mark of a strong Python engineer is **restraint**: `__init_subclass__`, `__set_name__`
descriptors, and **class decorators** now handle most cases with far less
complexity, leaving metaclasses as a rarely-needed last resort. Understanding the
chain — objects → classes → metaclasses — completes your mental model of how Python
OOP actually works.

> **You have mastered this module when** you can: explain the object→class→metaclass
> chain and why `type(type) is type`; build a class with `type(...)`; write a simple
> metaclass and an `__init_subclass__` hook; and pick the lightest tool for a
> class-customisation task.
