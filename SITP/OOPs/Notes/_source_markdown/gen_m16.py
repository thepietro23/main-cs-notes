"""Module 16 — Exception Hierarchies & OOP Error Handling: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_exceptions_are_objects():
    fig, ax = V.new_canvas()
    V.title(ax, "Exceptions are objects (instances of classes)")
    V.box(ax, 25, 60, 30, 14, "raise ValueError('bad')", fill=V.BLUE_F, size=10)
    V.arrow(ax, 41, 60, 58, 60, color=V.NAVY)
    V.box(ax, 78, 60, 30, 14, "a ValueError\nOBJECT with .args", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 36, "raising = creating & throwing an exception instance", color=V.RED, size=11)
    V.note(ax, 50, 26, "except catches by the object's CLASS (and its subclasses)", color=V.GRAY, size=10)
    V.caption(ax, "An exception is a normal object; raising it throws that instance up the stack.")
    V.save(fig, IMG + "m16_01_exceptions_are_objects.png")


def d02_hierarchy():
    fig, ax = V.new_canvas()
    V.title(ax, "The built-in exception hierarchy")
    V.box(ax, 50, 82, 26, 8, "BaseException", fill=V.NAVY, tcolor="white", size=10)
    V.box(ax, 25, 66, 22, 8, "SystemExit /\nKeyboardInterrupt", fill=V.ORANGE_F, edge=V.ORANGE, size=8)
    V.box(ax, 68, 66, 20, 8, "Exception", fill=V.BLUE_F, size=10)
    V.arrow(ax, 44, 78, 28, 70, color=V.NAVY)
    V.arrow(ax, 56, 78, 66, 70, color=V.NAVY)
    kids = [(28, "ValueError"), (48, "TypeError"), (68, "KeyError"), (88, "OSError")]
    for x, t in kids:
        V.box(ax, x, 46, 17, 8, t, fill=V.GREEN_F, edge=V.GREEN, size=9)
        V.arrow(ax, 66, 62, x, 50, color=V.GRAY)
    V.note(ax, 50, 28, "catch Exception (not BaseException) — don't swallow SystemExit/KeyboardInterrupt", color=V.RED, size=10)
    V.caption(ax, "All catchable errors derive from Exception; catch that, never bare BaseException.")
    V.save(fig, IMG + "m16_02_hierarchy.png")


def d03_try_flow():
    fig, ax = V.new_canvas()
    V.title(ax, "try / except / else / finally")
    V.box(ax, 20, 66, 18, 10, "try:\nrisky()", fill=V.BLUE_F, size=10)
    V.box(ax, 44, 80, 20, 9, "except: handle", fill=V.RED, tcolor="white", size=9)
    V.box(ax, 44, 58, 20, 9, "else: ran OK", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 78, 66, 22, 10, "finally:\nALWAYS runs", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.arrow(ax, 29, 68, 34, 78, color=V.RED)
    V.arrow(ax, 29, 64, 34, 60, color=V.GREEN)
    V.arrow(ax, 54, 78, 70, 70, color=V.NAVY)
    V.arrow(ax, 54, 60, 70, 64, color=V.NAVY)
    V.note(ax, 50, 36, "except: on error | else: on success | finally: cleanup either way", color=V.RED, size=10)
    V.caption(ax, "except handles errors, else runs on success, finally always runs (cleanup).")
    V.save(fig, IMG + "m16_03_try_flow.png")


def d04_catch_base():
    fig, ax = V.new_canvas()
    V.title(ax, "Catching a base class catches its subclasses")
    V.box(ax, 30, 70, 26, 10, "except Exception", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 20, 46, 18, 9, "ValueError", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 45, 46, 18, 9, "KeyError", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 25, 50, 28, 65, color=V.GREEN)
    V.arrow(ax, 42, 50, 34, 65, color=V.GREEN)
    V.note(ax, 78, 66, "all caught", color=V.GREEN, size=10)
    V.note(ax, 50, 28, "order matters: put SPECIFIC excepts before general ones", color=V.RED, size=11)
    V.caption(ax, "except Base catches all subclasses — list specific handlers first.")
    V.save(fig, IMG + "m16_04_catch_base.png")


def d05_custom_hierarchy():
    fig, ax = V.new_canvas()
    V.title(ax, "Design a custom exception hierarchy")
    V.box(ax, 50, 76, 30, 9, "AppError(Exception)", fill=V.NAVY, tcolor="white", size=10)
    kids = [(20, "PaymentError"), (50, "AuthError"), (80, "NotFoundError")]
    for x, t in kids:
        V.box(ax, x, 52, 24, 9, t, fill=V.GREEN_F, edge=V.GREEN, size=9)
        V.arrow(ax, 50, 71, x, 57, color=V.NAVY)
    V.note(ax, 50, 34, "callers can 'except AppError' to catch ALL app errors,", color=V.RED, size=10)
    V.note(ax, 50, 26, "or a specific one for fine control", color=V.RED, size=10)
    V.caption(ax, "One base app exception + specific subclasses = flexible, catchable families.")
    V.save(fig, IMG + "m16_05_custom_hierarchy.png")


def d06_chaining():
    fig, ax = V.new_canvas()
    V.title(ax, "Exception chaining: raise ... from")
    V.box(ax, 22, 60, 24, 12, "low-level\nKeyError", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 35, 60, 55, 60, color=V.NAVY)
    V.note(ax, 45, 67, "raise ... from", color=V.ORANGE, size=9)
    V.box(ax, 76, 60, 30, 14, "ConfigError\n(__cause__ = KeyError)", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.note(ax, 50, 36, "wrap a low-level error in a meaningful one, keeping the original", color=V.RED, size=10)
    V.note(ax, 50, 26, "traceback shows BOTH: 'The above ... direct cause'", color=V.GRAY, size=9)
    V.caption(ax, "raise NewError from err preserves the original cause for debugging.")
    V.save(fig, IMG + "m16_06_chaining.png")


def d07_eafp_lbyl():
    fig, ax = V.new_canvas()
    V.title(ax, "EAFP vs LBYL")
    V.box(ax, 27, 58, 40, 36, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 27, 72, "EAFP (Pythonic)", color=V.GREEN, bold=True, size=11)
    V.note(ax, 27, 61, "try: d[k]\nexcept KeyError:", size=10)
    V.note(ax, 27, 46, "just do it, catch failure", color=V.GRAY, size=9)
    V.box(ax, 73, 58, 40, 36, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 73, 72, "LBYL", color=V.ORANGE, bold=True, size=11)
    V.note(ax, 73, 61, "if k in d:\n    d[k]", size=10)
    V.note(ax, 73, 46, "check first (race-prone)", color=V.GRAY, size=9)
    V.caption(ax, "Python favours EAFP (try/except) over check-first LBYL — pairs with duck typing.")
    V.save(fig, IMG + "m16_07_eafp_lbyl.png")


def d08_best_practices():
    fig, ax = V.new_canvas()
    V.title(ax, "Error-handling do's and don'ts")
    V.box(ax, 27, 58, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 27, 72, "DO", color=V.GREEN, bold=True, size=12)
    V.note(ax, 27, 60, "catch SPECIFIC types\nraise ... from\nclean up in finally/with", size=9)
    V.box(ax, 73, 58, 40, 40, "", fill=V.RED, edge=V.RED)
    V.note(ax, 73, 72, "DON'T", color="white", bold=True, size=12)
    V.note(ax, 73, 60, "except: pass (swallow)\ncatch bare Exception\nuse errors for flow", color="white", size=9)
    V.caption(ax, "Catch narrowly, chain causes, clean up reliably; never silently swallow errors.")
    V.save(fig, IMG + "m16_08_best_practices.png")


if __name__ == "__main__":
    for f in [d01_exceptions_are_objects, d02_hierarchy, d03_try_flow, d04_catch_base,
              d05_custom_hierarchy, d06_chaining, d07_eafp_lbyl, d08_best_practices]:
        f()
    print("M16 diagrams done.")
