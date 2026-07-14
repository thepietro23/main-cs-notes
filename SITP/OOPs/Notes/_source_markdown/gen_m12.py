"""Module 12 — Object Lifecycle & Memory: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_lifecycle():
    fig, ax = V.new_canvas()
    V.title(ax, "Object lifecycle: birth -> use -> death")
    steps = [(16, "__new__\nallocate", V.ORANGE_F, V.ORANGE),
             (38, "__init__\ninitialise", V.ORANGE_F, V.ORANGE),
             (61, "in use\n(referenced)", V.GREEN_F, V.GREEN),
             (85, "refcount 0\n-> freed", V.BLUE_F, V.NAVY)]
    for i, (x, t, f, e) in enumerate(steps):
        V.box(ax, x, 58, 20, 14, t, fill=f, edge=e, size=10)
        if i < 3:
            V.arrow(ax, x + 10, 58, steps[i + 1][0] - 10, 58, color=V.NAVY)
    V.note(ax, 50, 34, "CPython frees an object the instant its refcount hits 0", color=V.RED, size=11)
    V.caption(ax, "An object is created (new/init), used while referenced, freed when unreferenced.")
    V.save(fig, IMG + "m12_01_lifecycle.png")


def d02_refcount():
    fig, ax = V.new_canvas()
    V.title(ax, "Reference counting")
    V.box(ax, 55, 58, 26, 16, "list object\nrefcount = 2", fill=V.BLUE_F, size=11)
    V.box(ax, 18, 70, 12, 8, "a", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 18, 46, 12, 8, "b", fill="white", edge=V.NAVY, size=11)
    V.arrow(ax, 24, 70, 42, 62, color=V.GREEN)
    V.arrow(ax, 24, 46, 42, 54, color=V.GREEN)
    V.note(ax, 85, 66, "a = [] -> 1", color=V.GRAY, size=9)
    V.note(ax, 85, 58, "b = a  -> 2", color=V.GRAY, size=9)
    V.note(ax, 85, 50, "del a  -> 1", color=V.GRAY, size=9)
    V.note(ax, 50, 30, "count reaches 0 -> memory reclaimed immediately", color=V.RED, size=11)
    V.caption(ax, "Each new reference bumps the count; each removal drops it; 0 -> freed.")
    V.save(fig, IMG + "m12_02_refcount.png")


def d03_ref_cycle():
    fig, ax = V.new_canvas()
    V.title(ax, "Reference cycles need the cyclic GC")
    V.box(ax, 30, 58, 20, 12, "A", fill=V.ORANGE_F, edge=V.ORANGE, size=12)
    V.box(ax, 70, 58, 20, 12, "B", fill=V.ORANGE_F, edge=V.ORANGE, size=12)
    V.arrow(ax, 40, 62, 60, 62, color=V.NAVY)
    V.arrow(ax, 60, 54, 40, 54, color=V.NAVY)
    V.note(ax, 50, 66, "A.b = B", color=V.GRAY, size=9)
    V.note(ax, 50, 48, "B.a = A", color=V.GRAY, size=9)
    V.note(ax, 50, 34, "each keeps the other alive -> refcount never hits 0", color=V.RED, size=11)
    V.note(ax, 50, 26, "the generational cyclic GC (gc module) detects & frees cycles", color=V.GREEN, size=10)
    V.caption(ax, "Refcounting alone can't free cycles; the cyclic garbage collector does.")
    V.save(fig, IMG + "m12_03_ref_cycle.png")


def d04_del_statement():
    fig, ax = V.new_canvas()
    V.title(ax, "'del x' removes a NAME, not the object")
    V.box(ax, 20, 62, 12, 9, "a", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 20, 42, 12, 9, "b", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 62, 52, 26, 14, "object\nrefcount 2 -> 1", fill=V.BLUE_F, size=11)
    V.arrow(ax, 26, 62, 49, 56, color=V.RED, dashed=True)
    V.arrow(ax, 26, 42, 49, 48, color=V.GREEN)
    V.note(ax, 20, 74, "del a", color=V.RED, size=10, bold=True)
    V.note(ax, 50, 30, "object survives while b still references it", color=V.RED, size=11)
    V.caption(ax, "del just unbinds a name and drops the refcount; the object lives until it hits 0.")
    V.save(fig, IMG + "m12_04_del_statement.png")


def d05_del_method():
    fig, ax = V.new_canvas()
    V.title(ax, "__del__ finaliser (and its pitfalls)")
    V.box(ax, 50, 74, 40, 9, "def __del__(self): cleanup()", fill=V.BLUE_F, size=11)
    V.note(ax, 50, 60, "runs when the object is about to be destroyed", color=V.NAVY, size=11)
    pitfalls = [(46, "timing is NON-deterministic"),
                (37, "may not run at interpreter exit"),
                (28, "exceptions in it are ignored")]
    for y, t in pitfalls:
        V.note(ax, 50, y, "- " + t, color=V.RED, size=10)
    V.caption(ax, "__del__ is unreliable for cleanup — prefer context managers / try-finally.")
    V.save(fig, IMG + "m12_05_del_method.png")


def d06_weakref():
    fig, ax = V.new_canvas()
    V.title(ax, "weakref: reference without keeping alive")
    V.box(ax, 60, 58, 26, 16, "object\nrefcount = 1", fill=V.BLUE_F, size=11)
    V.box(ax, 18, 70, 14, 8, "strong", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 18, 44, 14, 8, "weakref", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 25, 70, 46, 62, color=V.GREEN)
    V.arrow(ax, 25, 44, 46, 54, color=V.ORANGE, dashed=True)
    V.note(ax, 60, 38, "weakref does NOT raise the count", color=V.RED, size=10)
    V.note(ax, 50, 26, "drop the strong ref -> object dies; weakref becomes None", color=V.RED, size=10)
    V.caption(ax, "Weak references observe an object without preventing its collection (caches).")
    V.save(fig, IMG + "m12_06_weakref.png")


def d07_copy_deep():
    fig, ax = V.new_canvas()
    V.title(ax, "copy vs deepcopy (custom hooks)")
    V.box(ax, 27, 58, 40, 34, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 70, "copy.copy", color=V.ORANGE, bold=True, size=11)
    V.note(ax, 27, 60, "shallow: shares\nnested objects", size=10)
    V.note(ax, 27, 48, "hook: __copy__", color=V.GRAY, size=9)
    V.box(ax, 73, 58, 40, 34, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 70, "copy.deepcopy", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 60, "deep: clones the\nwhole tree", size=10)
    V.note(ax, 73, 48, "hook: __deepcopy__", color=V.GRAY, size=9)
    V.note(ax, 50, 30, "define __copy__/__deepcopy__ to control cloning of your objects", color=V.RED, size=10)
    V.caption(ax, "copy module clones objects; classes customise via __copy__/__deepcopy__.")
    V.save(fig, IMG + "m12_07_copy_deep.png")


def d08_cleanup_choice():
    fig, ax = V.new_canvas()
    V.title(ax, "Cleanup: prefer 'with' over __del__")
    V.box(ax, 27, 58, 40, 34, "", fill=V.RED, edge=V.RED)
    V.note(ax, 27, 70, "__del__", color="white", bold=True, size=12)
    V.note(ax, 27, 58, "unreliable timing\nmay never run", color="white", size=10)
    V.note(ax, 27, 44, "avoid for resources", color="white", size=9)
    V.box(ax, 73, 58, 40, 34, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 70, "with / try-finally", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 58, "deterministic\nguaranteed cleanup", size=10)
    V.note(ax, 73, 44, "the right tool", color=V.GREEN, size=9)
    V.caption(ax, "For files/sockets/locks, use context managers — not the __del__ finaliser.")
    V.save(fig, IMG + "m12_08_cleanup_choice.png")


if __name__ == "__main__":
    for f in [d01_lifecycle, d02_refcount, d03_ref_cycle, d04_del_statement,
              d05_del_method, d06_weakref, d07_copy_deep, d08_cleanup_choice]:
        f()
    print("M12 diagrams done.")
