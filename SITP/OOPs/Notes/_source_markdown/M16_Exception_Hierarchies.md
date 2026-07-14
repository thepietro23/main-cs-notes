---
title: "Module 16 — Exception Hierarchies & OOP Error Handling"
subtitle: "OOP with Python Mastery: FAANG Interviews / GATE / SEBI-RBI IT / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 16 — Exception Hierarchies & OOP Error Handling

> **Why this module matters.**
> Errors are **objects** — instances of exception **classes** arranged in an
> **inheritance hierarchy**. That single fact makes error handling an OOP topic: you
> catch by class (and its subclasses), and you design your own **exception
> hierarchies** so callers can catch a whole family or one specific error. Add
> `try/except/else/finally`, **exception chaining** (`raise ... from`), and the
> **EAFP** philosophy that pairs with duck typing, and you have robust, debuggable
> code — a real differentiator in backend interviews and code reviews.

**Importance ratings (out of 5):**

| Exam / Use  | FAANG Interview | GATE CS | SEBI/RBI IT | Backend Dev | LLD Rounds |
|-------------|:---------------:|:-------:|:-----------:|:-----------:|:----------:|
| This module | ★★★★            | ★★      | ★★          | ★★★★★       | ★★★        |

**Most-asked concepts:** the exception class hierarchy (`BaseException` →
`Exception`); catching a base catches subclasses; `try/except/else/finally`; custom
exception hierarchies; `raise ... from` (chaining, `__cause__`); **EAFP vs LBYL**;
why not to catch bare `Exception`/`except: pass`.

**What you must be able to do after this module:** design a custom exception
hierarchy; use `try/except/else/finally` correctly; chain exceptions; choose
specific over broad catches; and explain EAFP vs LBYL.

---

## 16.1 Exceptions Are Objects

Raising an exception **creates and throws an object** — an instance of an exception
class. `except` catches based on that object's **class** (respecting inheritance).

![raise ValueError('bad') creates a ValueError object (with .args) and throws it; except catches by the object's class and its subclasses.](images/m16_01_exceptions_are_objects.png)

```python
try:
    raise ValueError("bad input")
except ValueError as e:          # 'e' is the exception OBJECT
    print(type(e), e.args)       # <class 'ValueError'> ('bad input',)
```

Because they're objects, you can give them attributes, methods, and — crucially —
**subclass them** to build meaningful hierarchies.

---

## 16.2 The Built-in Exception Hierarchy

![The hierarchy: BaseException at the top; under it SystemExit/KeyboardInterrupt (system-level) and Exception; under Exception the everyday errors ValueError, TypeError, KeyError, OSError.](images/m16_02_hierarchy.png)

```text
BaseException
 ├── SystemExit          (sys.exit)      \  system-level — usually DON'T catch
 ├── KeyboardInterrupt   (Ctrl-C)        /
 └── Exception           <- catch THIS family for normal errors
      ├── ArithmeticError -> ZeroDivisionError
      ├── LookupError     -> KeyError, IndexError
      ├── ValueError, TypeError, OSError, RuntimeError, ...
```

> **Key rule:** catch **`Exception`**, never bare **`BaseException`** (or bare
> `except:`), because the latter also swallows `SystemExit`/`KeyboardInterrupt` —
> making your program impossible to exit or Ctrl-C.

---

## 16.3 `try / except / else / finally`

![Control flow: try runs risky code; except handles an error; else runs only if no error occurred; finally always runs (cleanup), error or not.](images/m16_03_try_flow.png)

```python
try:
    result = risky()             # code that might fail
except ValueError as e:
    handle(e)                    # runs only on ValueError
else:
    use(result)                  # runs only if NO exception
finally:
    cleanup()                    # ALWAYS runs (success or failure)
```

- **`except`** — runs on a matching error.
- **`else`** — runs only if the `try` block **succeeded** (keeps the "success path"
  out of `try`, so you don't accidentally catch errors from `use(result)`).
- **`finally`** — **always** runs; for releasing resources (though a `with` block is
  usually cleaner — Module 7/12).

---

## 16.4 Catching a Base Catches Its Subclasses

Because `except` respects inheritance, catching a **base** class catches **all its
subclasses**. This is polymorphism applied to error handling.

![except Exception catches ValueError and KeyError (both subclasses); specific handlers must come before general ones.](images/m16_04_catch_base.png)

```python
try:
    ...
except FileNotFoundError:        # SPECIFIC first
    ...
except OSError:                  # broader (FileNotFoundError is an OSError)
    ...
except Exception:                # broadest last
    ...
```

> **Order matters:** put **specific** exceptions **before** general ones. If
> `except Exception` came first, it would catch everything and the specific handlers
> would be dead code (Python evaluates `except` clauses top to bottom).

---

## 16.5 Designing Custom Exception Hierarchies

For an application/library, define **one base exception** and specific subclasses.
Callers can then catch the **whole family** or a **specific** error.

![An AppError base (subclass of Exception) with specific subclasses PaymentError, AuthError, NotFoundError; callers can catch AppError for all app errors or a specific one.](images/m16_05_custom_hierarchy.png)

```python
class AppError(Exception):
    """Base for all application errors."""

class PaymentError(AppError): ...
class InsufficientFunds(PaymentError):
    def __init__(self, needed, available):
        super().__init__(f"need {needed}, have {available}")
        self.needed, self.available = needed, available

# Caller choices:
try:
    charge()
except InsufficientFunds as e:   # very specific
    retry_with(e.available)
except AppError:                 # catch ANY application error
    log_and_alert()
```

**Benefits:** callers aren't forced to know every leaf type; a single `except
AppError` is a stable contract; and rich attributes (`e.needed`) carry structured
context. This is the OOP payoff for error handling.

---

## 16.6 Exception Chaining — `raise ... from`

When you catch a low-level error and raise a more meaningful one, **chain** them so
the original cause isn't lost.

![A low-level KeyError is wrapped via raise ConfigError(...) from err, producing a ConfigError whose __cause__ is the KeyError; the traceback shows both.](images/m16_06_chaining.png)

```python
def load_config(d):
    try:
        return d["host"]
    except KeyError as e:
        raise ConfigError("missing 'host'") from e   # preserves the cause

# Traceback shows:
#   KeyError: 'host'
#   The above exception was the direct cause of the following exception:
#   ConfigError: missing 'host'
```

- `raise New from original` sets **`__cause__`** and prints *"direct cause"*.
- An exception raised inside an `except` **without** `from` still records
  **`__context__`** ("During handling of the above exception…").
- `raise ... from None` **suppresses** the chain when the original is noise.

---

## 16.7 EAFP vs LBYL

Python culturally prefers **EAFP — "Easier to Ask Forgiveness than Permission"**:
just attempt the operation and catch the failure, rather than **LBYL — "Look Before
You Leap"** (check conditions first).

![EAFP (Pythonic): try d[k] / except KeyError — just do it and catch failure. LBYL: if k in d: d[k] — check first, which is race-prone.](images/m16_07_eafp_lbyl.png)

```python
# EAFP (Pythonic)
try:
    value = data[key]
except KeyError:
    value = default

# LBYL (check first) — verbose and racy in concurrent code
if key in data:
    value = data[key]
else:
    value = default
```

EAFP pairs with **duck typing** (Module 6): try to use the object, handle it if it
can't. It's also **race-safe** — LBYL's check-then-act can break if state changes
between the check and the use (e.g. a file deleted after `os.path.exists`).

---

## 16.8 Best Practices

![Do: catch specific types, use raise ... from, clean up in finally/with. Don't: except: pass (swallow errors), catch bare Exception, use exceptions for normal control flow.](images/m16_08_best_practices.png)

| Do | Don't |
|---|---|
| Catch **specific** exception types | `except:` / `except Exception: pass` (silent swallow) |
| **Chain** with `raise ... from` | lose the original cause |
| Clean up with **`with`** / `finally` | rely on `__del__` |
| Define a **custom hierarchy** | raise bare `Exception("...")` everywhere |
| Let unexpected errors **propagate** | catch-and-ignore |
| Use EAFP for expected failures | overuse exceptions for normal control flow |

> **Golden rule:** **never silently swallow** an exception. If you catch it, handle
> it, log it, or re-raise it — but don't make failures invisible.

---

## Module 16 — Interview Mapping

| Question | Junior answer | Senior answer |
|---|---|---|
| "Why custom exceptions?" | "Nicer errors." | "A base app exception + specific subclasses lets callers catch a family or one case; carries structured context; a stable API contract." |
| "`except Exception` vs `except:`?" | (unsure) | "Bare `except`/`BaseException` also catches `SystemExit`/`KeyboardInterrupt` — never do it; catch `Exception` and be specific." |
| "EAFP vs LBYL?" | "Try vs check." | "Python prefers EAFP (try/except) — cleaner, race-safe, pairs with duck typing; LBYL's check-then-act can race." |
| "`raise ... from`?" | (unaware) | "Chains exceptions, setting `__cause__`; wraps a low-level error in a meaningful one while preserving the original in the traceback." |

---

## Module 16 — Exam Mapping

- **GATE CS:** exception-handling flow (`try/except/else/finally`), hierarchy basics.
- **SEBI / RBI IT:** basic exception syntax and terms.
- **FAANG / backend:** custom hierarchies, chaining, EAFP, and error-handling
  hygiene in code.

---

## Module 16 — Common Mistakes & Misconceptions

- **`except: pass`** — swallows everything (including `KeyboardInterrupt`); hides
  bugs.
- **Catching `Exception` too broadly** when a specific type is meant.
- **Wrong `except` order** — general before specific makes specific unreachable.
- **Losing the cause** — re-raising without `from` (though `__context__` still
  records it).
- **Using exceptions for normal control flow** everywhere (overuse).
- **Relying on `finally` for resource cleanup** where a `with` block is clearer.
- **Raising bare `Exception`** instead of a specific/custom type.

---

## Module 16 — MCQs (with answers & explanations)

**Q1.** Which should you generally catch?
a) `BaseException`  b) **`Exception`**  c) bare `except:`  d) `object`

<details><summary>Answer</summary>**b.** `Exception` excludes `SystemExit`/`KeyboardInterrupt`.</details>

**Q2.** `finally` runs:
a) only on error  b) only on success  c) **always**  d) never

<details><summary>Answer</summary>**c.** It always executes, for cleanup.</details>

**Q3.** `except OSError` will also catch:
a) nothing else  b) **FileNotFoundError (a subclass)**  c) ValueError  d) SystemExit

<details><summary>Answer</summary>**b.** Catching a base catches its subclasses.</details>

**Q4.** Handlers should be ordered:
a) general first  b) **specific first, general last**  c) alphabetical  d) any order

<details><summary>Answer</summary>**b.** Otherwise the general clause shadows specific ones.</details>

**Q5.** `raise NewError from original` sets:
a) `__context__`  b) **`__cause__`**  c) `args`  d) nothing

<details><summary>Answer</summary>**b.** Explicit chaining sets `__cause__` ("direct cause").</details>

**Q6.** EAFP stands for:
a) check first  b) **Easier to Ask Forgiveness than Permission**  c) an exception type  d) a decorator

<details><summary>Answer</summary>**b.** Try the operation, handle failure — the Pythonic style.</details>

**Q7.** `except: pass` is bad because it:
a) is slow  b) **silently swallows all errors, including Ctrl-C**  c) is a syntax error  d) is required

<details><summary>Answer</summary>**b.** It hides bugs and catches `KeyboardInterrupt`/`SystemExit`.</details>

**Q8.** The `else` clause of `try` runs:
a) on error  b) always  c) **only if no exception occurred**  d) before try

<details><summary>Answer</summary>**c.** It runs on the success path.</details>

---

## Module 16 — Design/Practice Exercises (easy → hard)

1. **(easy)** Write `try/except/else/finally` around a division and show which clauses
   run for `4/2` and `4/0`.
2. **(easy)** Show that `except OSError` catches a `FileNotFoundError`.
3. **(medium)** Design an `AppError` hierarchy with `ValidationError` and
   `DatabaseError`; catch the family in one handler.
4. **(medium)** Wrap a low-level `KeyError` in a `ConfigError` using `raise ... from`
   and print the chained traceback.
5. **(hard)** Rewrite an LBYL file-existence check as EAFP and explain the race it
   avoids.
6. **(hard, interview)** Critique a snippet with `except Exception: pass`, then fix it
   with specific catches, chaining, and proper cleanup.

---

## Module 16 — Concept Review (one page)

Exceptions are **objects** — instances of classes in an **inheritance hierarchy**
rooted at **`BaseException`**, with **`Exception`** as the base for normal errors
(catch `Exception`, never bare `BaseException`/`except:`, which swallow
`SystemExit`/`KeyboardInterrupt`). **`try/except/else/finally`**: `except` handles
matching errors, `else` runs on success, `finally` always runs (cleanup). Catching a
**base** catches its **subclasses**, so order handlers **specific-first**. Design a
**custom hierarchy** — one base app exception plus specific subclasses carrying
structured attributes — so callers can catch a **family or a single case**. **Chain**
wrapped errors with **`raise New from original`** (sets `__cause__`) to preserve the
root cause. Python favours **EAFP** (try/except) over **LBYL** (check-first) — cleaner,
race-safe, and aligned with duck typing. Above all: **never silently swallow**
exceptions.

---

## Module 16 — Flash Cards (Q → A)

| Front | Back |
|-------|------|
| Exceptions are | objects (instances of exception classes) |
| Root of hierarchy | `BaseException`; catch `Exception` |
| Catch a base → | catches all its subclasses |
| Handler order | specific first, general last |
| `else` clause | runs only if no exception |
| `finally` | always runs (cleanup) |
| Custom hierarchy | base app exception + specific subclasses |
| `raise New from e` | chains; sets `__cause__` |
| Implicit chain | `__context__` (raised during handling) |
| EAFP | try, then handle failure (Pythonic) |
| LBYL | check conditions first (race-prone) |
| Never do | `except: pass` (silent swallow) |

---

## Module 16 — Pattern Recognition

- **See "callers need to catch all my library's errors"** → custom base exception.
- **See a low-level error leaking to users** → wrap + `raise ... from`.
- **See `if os.path.exists(...)` then open** → EAFP (`try open except`).
- **See `except Exception: pass`** → catch specific, handle/log/re-raise.
- **See resource that must always close** → `with` (or `finally`).
- **See general `except` before specific** → reorder (specific first).

---

## Module 16 — Revision Notes / Mini Cheat Sheet

```
EXCEPTIONS = objects; classes in a hierarchy (BaseException -> Exception -> ...).
CATCH Exception (normal errors). NEVER bare except / BaseException (eats SystemExit, Ctrl-C).

try: risky()
except Specific as e: handle        # specific FIRST
except Broad: ...                   # broad LAST
else: on-success                    # only if no error
finally: cleanup                    # ALWAYS (prefer 'with')

catch BASE => catches SUBCLASSES. Custom hierarchy: class AppError(Exception); subclasses.
  -> callers 'except AppError' (family) or a specific type; attach context attributes.

CHAINING: raise New from original  -> __cause__ ("direct cause"); ... from None suppresses.
EAFP (try/except, Pythonic, race-safe) > LBYL (check-first, race-prone). Pairs with duck typing.
DON'T: except: pass (swallow), overuse exceptions for control flow, lose the cause.
```

> **Next module:** **Module 17 — UML & Object-Oriented Design (OOAD).** We step back to
> *modelling*: reading and drawing **UML class diagrams**, notating **association,
> aggregation, composition, inheritance, and dependency**, plus value objects,
> multiplicity, and how to go from a problem statement to a class model — the bridge
> into the LLD interview module.

---

## Module 16 — Summary

Error handling is an OOP topic because **exceptions are objects** in a **class
hierarchy**. Catch **`Exception`** (never bare `BaseException`/`except:`), use
**`try/except/else/finally`** correctly, and remember that catching a **base**
catches its **subclasses** — so order handlers **specific-first**. Design a **custom
exception hierarchy** (one base plus specific subclasses with structured context) so
callers can catch a family or a single case; **chain** wrapped errors with **`raise
... from`** to keep the root cause; and prefer **EAFP** over check-first **LBYL** for
cleaner, race-safe code. The overriding discipline: **never silently swallow errors**
— handle, log, or re-raise. Done well, this makes OOP systems robust and debuggable.

> **You have mastered this module when** you can: design a custom exception
> hierarchy; use `try/except/else/finally` and correct handler ordering; chain
> exceptions with `raise ... from`; and explain EAFP vs LBYL with an example.
