---
title: "Module 21 — Revision Kit & Master Cheat Sheets"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 21 — Revision Kit & Master Cheat Sheets

> **Why this module matters.**
> This is the **night-before-the-interview** document — the entire course distilled
> into dense, at-a-glance recall sheets and a glossary. Nothing new is taught here;
> everything is compressed for **fast final review**. Read it top to bottom in ~30
> minutes to reactivate the whole subject.

**How to use:** skim the visuals first (each is a full cheat sheet), then read the
code-block summaries, then self-test with the glossary and the 60-second checklist.

---

## 21.1 The Four Pillars

![The four pillars (A PIE): Abstraction (what, not how), Polymorphism (one name, many forms), Inheritance (reuse via is-a), Encapsulation (bundle + hide).](images/m21_01_pillars_recall.png)

```
ENCAPSULATION  bundle data + methods; hide internals behind an API (_x, __x, @property)
ABSTRACTION    expose WHAT, hide HOW (ABCs, Protocols, clean interfaces)
INHERITANCE    reuse/extend via is-a (super(), MRO); favour composition for has-a
POLYMORPHISM   one interface, many forms (overriding, duck typing, operator dunders)
```

---

## 21.2 Object Model & Classes

```
VARIABLE = a NAME bound to an OBJECT. Assignment BINDS, never copies.
OBJECT = id (identity) + type + value. b=a -> alias; mutate visible via both.
== value (calls __eq__)  |  is identity (id). Use 'is' ONLY for None/singletons.
MUTABLE: list/dict/set/instances | IMMUTABLE: int/float/str/tuple/frozenset/bytes.
Interning: ints -5..256 cached -> never use 'is' for numbers/strings.
Pass by OBJECT REFERENCE: mutate -> caller sees; rebind param -> local only.
Mutable default bug: def f(x=[]) -> use x=None sentinel.

class body: class attrs (shared) + methods. instance attrs via self in __init__.
self = current instance (auto first arg). acc.m(x) == Class.m(acc, x).
Lookup: instance __dict__ -> class -> bases(MRO). MUTABLE class attr = shared (bug).
Creation: __new__ (allocate) -> __init__ (initialise, returns None).
```

![Methods & property recall: instance -> self (state); @classmethod -> cls (factory); @staticmethod -> nothing (helper); @property -> attribute syntax + validation.](images/m21_06_method_types.png)

---

## 21.3 Inheritance, MRO & super()

![MRO & super() rules: D(B,C) B(A) C(A) -> MRO D,B,C,A,object; C3 = subclass first, left-to-right, ancestor after all descendants, each once; super() = next in MRO; always super().__init__; check with __mro__.](images/m21_03_mro_super.png)

```
is-a -> inheritance ; has-a -> composition (FAVOUR it).
super() -> NEXT class in MRO (not always literal parent). Always super().__init__(...).
MRO (C3): subclass before parents, left-to-right, ancestor after ALL descendants, once.
Aggregation (parts independent, ◇) vs Composition (parts owned/die together, ◆).
```

---

## 21.4 Dunder Methods (Data Model)

![Dunder quick-reference: __init__/__new__ (init/create); __repr__/__str__ (dev/user string); __eq__ + __hash__ (value equality + hashable); __lt__/total_ordering (comparison/sort); __len__/__getitem__/__iter__ (container/iterable); __enter__/__exit__ and __call__ (context manager; callable).](images/m21_02_dunder_table.png)

```
ALWAYS define __repr__. __str__ falls back to it.
Define __eq__ -> ALSO define __hash__ (or object is unhashable). Hash value-immutables only.
Container: __len__ __getitem__ __setitem__ __contains__ (getitem alone -> iterate + in).
Iterator: __iter__ + __next__ (StopIteration) or a generator (yield).
Context mgr: __enter__/__exit__ (exit ALWAYS runs; return True suppresses). __call__ -> callable.
Operators: __add__ (+), __radd__ (reflected), __iadd__ (+=), __lt__ ... .
```

---

## 21.5 Advanced: Descriptors, __slots__, Metaclasses

```
ACCESS: __getattribute__ (every read) ; __getattr__ (only on miss) ; __setattr__ (write).
DESCRIPTOR = class attr with __get__/__set__/__delete__ (+ __set_name__).
  DATA desc (has __set__) BEATS instance dict ; NON-DATA (get only) loses to it.
  Read precedence: data desc -> instance dict -> non-data/class -> __getattr__ -> error.
  @property, methods, classmethod, staticmethod are ALL descriptors.
__slots__ = ('a','b'): no per-instance __dict__ -> memory/speed; no dynamic attrs.
METACLASS: class of a class (type). 'class' == type(name, bases, ns). Prefer
  __init_subclass__ / class decorators; metaclass is a last resort.
```

---

## 21.6 Modern Tooling & Typing

![Modern tooling recall: @dataclass (auto init/repr/eq, frozen, default_factory); NamedTuple (immutable tuple record); Enum (named singleton constants); Protocol (structural typing); __slots__ (no __dict__, memory/speed).](images/m21_07_tooling_recall.png)

```
@dataclass: typed fields -> init/repr/eq. field(default_factory=list); frozen=True (immutable+hashable);
  order=True; __post_init__ (validate/derive). slots=True (3.10).
NamedTuple: immutable tuple record. Enum: named singletons (auto(), IntEnum, StrEnum).
TYPING (not enforced at runtime): list[int], Optional[X]==X|None, Callable.
  Generic[T]+TypeVar (bound=) ; Protocol = structural (static duck typing) vs ABC = nominal.
  ClassVar, Final, Self. mypy = static check in CI.
MEMORY: refcount (free at 0) + cyclic GC. del = unbind name + drop ref.
  __del__ unreliable -> use 'with'/finally. weakref = ref w/o keeping alive (caches/observers).
```

---

## 21.7 SOLID & Design Patterns

![SOLID in one glance: S one reason to change; O extend don't modify (polymorphism); L subtype substitutable; I small focused interfaces; D depend on abstractions (inject).](images/m21_04_solid_recall.png)

![Patterns map: pluggable policy -> Strategy; mode/status behaviour -> State; create by type -> Factory; notify many -> Observer; add behaviour by wrapping -> Decorator; simplify a subsystem -> Facade.](images/m21_05_patterns_map.png)

```
SOLID: SRP(one reason) OCP(extend not modify) LSP(substitutable) ISP(small ifaces) DIP(abstractions+inject).
CREATIONAL: Singleton(one; a module often), Factory(create by key), Builder(stepwise), Prototype(clone).
STRUCTURAL: Adapter(change iface), Decorator(add behaviour), Facade(simplify), Proxy(stand-in), Composite(tree).
BEHAVIORAL: Strategy(swap algo), Observer(pub/sub), Command(undo/queue), State(state machine),
  Template Method(skeleton+steps), Chain of Responsibility(pass along).
Python: functions-as-strategies; module-as-singleton; @ for decorators.
```

---

## 21.8 Errors, UML, LLD, Refactoring

```
EXCEPTIONS: objects in a hierarchy (BaseException->Exception). Catch Exception, never bare.
  try/except(specific first)/else(success)/finally(always). Custom hierarchy: AppError + subclasses.
  raise New from e (chain, __cause__). EAFP > LBYL. NEVER except: pass.
UML: box = name|attrs|methods (+public -private #protected).
  dependency(dashed) < association(line) < aggregation(◇) < composition(◆); inheritance(▷ solid);
  realization(▷ dashed). Multiplicity 1, 0..1, *, 1..*. Diamond sits on the WHOLE.
LLD: clarify -> entities(nouns) -> relationships(UML) -> SOLID+patterns -> code -> extend.
  Strategy(policy) State(mode) Factory(create) Observer(notify) Singleton(manager).
REFACTOR (structure not behaviour, tests green): Extract Method/Class, Replace Conditional w/
  Polymorphism, Introduce Parameter Object, composition over inheritance, value objects.
SMELLS: god object, long method/params, primitive obsession, feature envy, deep inheritance.
```

---

## 21.9 The Course Map

![The 21-module journey: Foundations (M1-M4: intro, object model, classes, encapsulation/abstraction) -> Core OOP (M5-M9: inheritance, polymorphism, dunders, descriptors, metaclasses) -> Modern + Design (M10-M17: tooling, typing, memory, SOLID, patterns, UML) -> Mastery (M18-M21: LLD, refactoring, question bank, cheat sheets).](images/m21_08_course_map.png)

---

## 21.10 Glossary (rapid recall)

| Term | Meaning |
|---|---|
| Class / Object | blueprint / instance with own state |
| Encapsulation | bundle + hide behind an API |
| Abstraction | expose what, hide how |
| Inheritance | reuse via is-a (`super()`, MRO) |
| Polymorphism | one interface, many forms |
| Duck typing | needs the method, not the class |
| MRO / C3 | deterministic ancestor order |
| Composition | has-a (favour over inheritance) |
| Aggregation vs Composition | parts independent vs owned |
| `self` / `cls` | current instance / current class |
| `@property` | method as attribute (validate/compute) |
| Descriptor | class attr with `__get__`/`__set__` |
| `__slots__` | no `__dict__`; memory/speed |
| Metaclass | class of a class (`type`) |
| dataclass | auto init/repr/eq from fields |
| Enum | named singleton constants |
| Protocol / ABC | structural / nominal interface |
| Reference counting / GC | free at 0 + cyclic collector |
| `weakref` | reference without keeping alive |
| SOLID | SRP, OCP, LSP, ISP, DIP |
| Strategy / State | swappable algo / state-driven behaviour |
| Observer / Command | pub-sub / request-as-object |
| Factory / Singleton | create-by-key / one instance |
| EAFP / LBYL | try-then-handle / check-first |
| Value object / Entity | value-defined immutable / persistent id |
| Refactoring | change structure, not behaviour |

---

## 21.11 60-Second Pre-Interview Checklist

```
[ ] Four pillars + one example each ("A PIE")
[ ] class vs object ; self ; instance vs class attribute (mutable trap)
[ ] is vs == ; mutable default bug ; aliasing
[ ] super() + MRO (D,B,C,A,object) ; composition over inheritance
[ ] __repr__ ; __eq__ needs __hash__ ; container/iterator/context-manager dunders
[ ] @classmethod vs @staticmethod vs instance ; @property validation
[ ] @dataclass (default_factory, frozen) ; Enum ; Protocol vs ABC
[ ] SOLID (apply, not recite) ; Strategy/Observer/Factory/State
[ ] LLD process: clarify -> entities -> UML -> patterns -> code -> extend
[ ] refactoring: replace conditional w/ polymorphism ; extract class
```

---

## Module 21 — Concept Review (one page)

This kit compresses the whole course. **Pillars** — Encapsulation, Abstraction,
Inheritance, Polymorphism ("A PIE"). **Object model** — names bind to objects,
`is` vs `==`, mutability, pass-by-object-reference, the mutable-default trap.
**Classes** — `self`, instance vs class attributes, three method kinds, `__new__`/
`__init__`. **Inheritance** — `super()`, the **MRO/C3**, composition over
inheritance. **Dunders** — always `__repr__`, `__eq__`+`__hash__`, containers,
iterators, context managers, `__call__`. **Advanced** — descriptors (data vs
non-data precedence), `__slots__`, metaclasses (last resort). **Modern** —
dataclasses, enums, typing/Protocols; memory (refcount + cyclic GC, `weakref`).
**Design** — SOLID, creational/structural/behavioral patterns, UML notation. **Mastery**
— the LLD process, exception hygiene, and safe refactoring. Know these cold and you
have OOP mastery.

---

## Module 21 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Pillars mnemonic | A PIE (Abstraction, Polymorphism, Inheritance, Encapsulation) |
| `is` vs `==` | identity vs value |
| MRO of `D(B,C)` | D, B, C, A, object |
| `super()` | next class in the MRO |
| Always define | `__repr__` |
| `__eq__` implies | define `__hash__` |
| self / cls | instance / class |
| data vs non-data descriptor | beats vs loses to instance dict |
| dataclass mutable default | `field(default_factory=...)` |
| Protocol vs ABC | structural vs nominal |
| memory model | refcount + cyclic GC |
| SOLID | SRP OCP LSP ISP DIP |
| pluggable policy pattern | Strategy |
| LLD first step | clarify requirements |
| refactoring definition | change structure, not behaviour |

---

## Module 21 — Revision Notes / Master Cheat Sheet

```
PILLARS (A PIE): Encapsulation(bundle+hide) Abstraction(what not how)
                 Inheritance(is-a, super/MRO) Polymorphism(one iface, many forms; duck typing).
OBJECT MODEL: names bind to objects; is(id) vs ==(value); mutable vs immutable;
              pass-by-object-reference; mutable default -> None sentinel; interning.
CLASSES: self=instance; instance vs class attr (mutable trap); instance/classmethod/staticmethod;
         @property (validate); __new__ then __init__.
INHERIT: super()=next in MRO; C3 order D,B,C,A,object; composition > inheritance; agg ◇ / comp ◆.
DUNDERS: __repr__ always; __eq__+__hash__; container/iter/context-mgr/__call__; operators.
ADVANCED: descriptors (data beats instance dict); __slots__; metaclass (last resort, prefer __init_subclass__).
MODERN: @dataclass(frozen, default_factory, __post_init__); Enum; Protocol(structural) vs ABC(nominal);
        typing (not enforced); refcount+cyclic GC; weakref; 'with' over __del__.
DESIGN: SOLID(SRP/OCP/LSP/ISP/DIP); patterns Strategy/Observer/Factory/State/Decorator/Facade...;
        UML boxes+relationships+multiplicity.
MASTERY: LLD (clarify->entities->UML->patterns->code->extend); exceptions (specific, chain, EAFP,
         never swallow); refactor (structure not behaviour, tests green).
```

> **This is the final module.** You now have the complete OOP-with-Python course:
> from *what an object is* to *designing production systems*. Revise this kit, drill
> Module 20's question bank, and design two LLD systems from scratch — and you're
> ready for any OOP exam or FAANG interview.

---

## Module 21 — Summary

The **Revision Kit** is the course in one sitting: the **four pillars ("A PIE")**;
the **object model** (`is`/`==`, mutability, references, the mutable-default trap);
**class mechanics** (`self`, attribute kinds, method types, `@property`,
`__new__`/`__init__`); **inheritance** (`super()`, **MRO/C3**, composition over
inheritance); the **dunder** data model (always `__repr__`, the `__eq__`/`__hash__`
contract, containers/iterators/context managers/`__call__`); **advanced** internals
(descriptors, `__slots__`, metaclasses); **modern tooling** (dataclasses, enums,
typing/Protocols, memory & `weakref`); and **design mastery** (SOLID, patterns, UML,
LLD, exceptions, refactoring). Keep this document for final review — it is the single
page that reactivates the entire subject before any exam or interview.

> **You have mastered this course when** you can teach each pillar with an example,
> predict any output-trap, choose the right pattern/principle for a design, run a full
> LLD from scratch, and refactor bad code safely — all in Python, from first
> principles.
