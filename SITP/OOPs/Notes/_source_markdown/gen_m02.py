"""Module 2 — Python Object Model: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_name_vs_object():
    fig, ax = V.new_canvas()
    V.title(ax, "A name is a label; the object lives on the heap")
    V.note(ax, 22, 78, "NAMES (namespace)", color=V.GRAY, bold=True, size=12)
    V.box(ax, 20, 62, 16, 9, "x", fill="white", edge=V.NAVY, size=13)
    V.box(ax, 20, 46, 16, 9, "y", fill="white", edge=V.NAVY, size=13)
    V.note(ax, 78, 78, "OBJECTS (heap)", color=V.GRAY, bold=True, size=12)
    V.box(ax, 78, 54, 26, 16, "int 42\nid 0x9a2", fill=V.BLUE_F, edge=V.NAVY, size=12)
    V.arrow(ax, 28, 62, 66, 56, color=V.GREEN)
    V.arrow(ax, 28, 46, 66, 52, color=V.GREEN)
    V.note(ax, 47, 40, "x = 42; y = x  ->  both names point to ONE object", color=V.RED, size=11)
    V.caption(ax, "Variables do not 'contain' values; they are names bound to objects.")
    V.save(fig, IMG + "m02_01_name_vs_object.png")


def d02_id_type_value():
    fig, ax = V.new_canvas()
    V.title(ax, "Every object has: identity, type, value")
    V.box(ax, 50, 60, 30, 22, "the object\n[1, 2, 3]", fill=V.BLUE_F, size=13)
    V.box(ax, 16, 78, 24, 10, "id()  -> identity", fill="white", edge=V.GRAY, size=11, bold=False)
    V.box(ax, 16, 42, 24, 10, "type() -> type", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 84, 60, 24, 10, "value -> contents", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 28, 76, 40, 64)
    V.arrow(ax, 28, 44, 40, 56)
    V.arrow(ax, 72, 60, 65, 60)
    V.note(ax, 50, 30, "id -> 0x7f.. (unique, fixed)   type -> list   value -> [1,2,3]", color=V.RED, size=11)
    V.caption(ax, "'is' compares identity; '==' compares value; type() names the class.")
    V.save(fig, IMG + "m02_02_id_type_value.png")


def d03_assignment_reference():
    fig, ax = V.new_canvas()
    V.title(ax, "Assignment copies the reference, not the object")
    V.box(ax, 18, 66, 14, 9, "a", fill="white", edge=V.NAVY, size=12)
    V.box(ax, 18, 48, 14, 9, "b", fill="white", edge=V.NAVY, size=12)
    V.box(ax, 60, 57, 28, 16, "list\n[10, 20]", fill=V.BLUE_F, edge=V.NAVY, size=12)
    V.arrow(ax, 26, 66, 46, 60, color=V.GREEN)
    V.arrow(ax, 26, 48, 46, 54, color=V.GREEN)
    V.note(ax, 60, 40, "b = a  ->  SAME object", color=V.NAVY, size=11, bold=True)
    V.note(ax, 60, 30, "a.append(30)  ->  b sees [10,20,30] too!", color=V.RED, size=11)
    V.caption(ax, "b = a does NOT copy the list; both names alias one mutable object.")
    V.save(fig, IMG + "m02_03_assignment_reference.png")


def d04_mutable_immutable():
    fig, ax = V.new_canvas()
    V.title(ax, "Mutable vs Immutable types")
    V.box(ax, 27, 60, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 27, 74, "IMMUTABLE", color=V.GREEN, bold=True, size=13)
    V.note(ax, 27, 62, "int, float, bool\nstr, tuple, frozenset\nbytes", size=11)
    V.note(ax, 27, 47, "value can NEVER change;\n'change' = new object", color=V.GRAY, size=10)
    V.box(ax, 73, 60, 40, 40, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 73, 74, "MUTABLE", color=V.ORANGE, bold=True, size=13)
    V.note(ax, 73, 62, "list, dict, set\nbytearray\nmost custom objects", size=11)
    V.note(ax, 73, 47, "can change in place;\nid() stays the same", color=V.GRAY, size=10)
    V.caption(ax, "Immutable: rebinding makes a new object. Mutable: edits happen in place.")
    V.save(fig, IMG + "m02_04_mutable_immutable.png")


def d05_is_vs_eq():
    fig, ax = V.new_canvas()
    V.title(ax, "'is' (identity) vs '==' (equality)")
    V.box(ax, 20, 62, 14, 9, "a", fill="white", edge=V.NAVY, size=12)
    V.box(ax, 20, 40, 14, 9, "b", fill="white", edge=V.NAVY, size=12)
    V.box(ax, 55, 62, 24, 12, "[1, 2]", fill=V.BLUE_F, size=12)
    V.box(ax, 55, 40, 24, 12, "[1, 2]", fill=V.BLUE_F, size=12)
    V.arrow(ax, 27, 62, 43, 62, color=V.GREEN)
    V.arrow(ax, 27, 40, 43, 40, color=V.GREEN)
    V.note(ax, 85, 62, "same value", color=V.NAVY, size=10)
    V.note(ax, 85, 40, "diff object", color=V.NAVY, size=10)
    V.note(ax, 50, 22, "a == b  ->  True  (same VALUE)", color=V.GREEN, size=11, bold=True)
    V.note(ax, 50, 15, "a is b  ->  False (different OBJECTS)", color=V.RED, size=11, bold=True)
    V.caption(ax, "Use == to compare contents; use 'is' only for None / identity checks.")
    V.save(fig, IMG + "m02_05_is_vs_eq.png")


def d06_interning():
    fig, ax = V.new_canvas()
    V.title(ax, "Interning: Python caches small ints & some strings")
    V.box(ax, 50, 62, 30, 14, "cached int 100\n(one shared object)", fill=V.BLUE_F, size=11)
    V.box(ax, 18, 78, 14, 8, "a=100", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 18, 46, 14, 8, "b=100", fill="white", edge=V.NAVY, size=11)
    V.arrow(ax, 25, 77, 40, 65, color=V.GREEN)
    V.arrow(ax, 25, 47, 40, 59, color=V.GREEN)
    V.note(ax, 50, 40, "a is b -> True  (ints -5..256 are pre-cached)", color=V.GREEN, size=11)
    V.note(ax, 50, 30, "a=1000; b=1000  ->  a is b MAY be False", color=V.RED, size=11)
    V.caption(ax, "Never rely on 'is' for numbers/strings — interning is an implementation detail.")
    V.save(fig, IMG + "m02_06_interning.png")


def d07_arg_passing():
    fig, ax = V.new_canvas()
    V.title(ax, "Argument passing = 'pass by object reference'")
    V.note(ax, 27, 80, "MUTATE the object", color=V.GREEN, bold=True, size=12)
    V.box(ax, 27, 64, 34, 10, "def f(lst): lst.append(9)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 27, 50, "caller's list\nCHANGES\n(same object)", color=V.GREEN, size=11)
    ax.plot([50, 50], [22, 78], color=V.GRAY, linewidth=1.5, linestyle="--")
    V.note(ax, 73, 80, "REBIND the name", color=V.RED, bold=True, size=12)
    V.box(ax, 73, 64, 34, 10, "def g(lst): lst = [9]", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.note(ax, 73, 50, "caller's list\nUNCHANGED\n(local rebind only)", color=V.RED, size=11)
    V.caption(ax, "Passing gives the function the SAME object; rebinding the parameter is local.")
    V.save(fig, IMG + "m02_07_arg_passing.png")


def d08_shallow_vs_deep():
    fig, ax = V.new_canvas()
    V.title(ax, "Shallow copy vs Deep copy")
    # shallow
    V.note(ax, 27, 82, "SHALLOW (copy / [:])", color=V.ORANGE, bold=True, size=11)
    V.box(ax, 15, 64, 14, 9, "orig", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 40, 64, 14, 9, "copy", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 27, 44, 26, 10, "inner [1,2]", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 15, 59, 24, 49, color=V.RED)
    V.arrow(ax, 40, 59, 31, 49, color=V.RED)
    V.note(ax, 27, 33, "inner list SHARED", color=V.RED, size=10)
    ax.plot([53, 53], [22, 80], color=V.GRAY, linewidth=1.2, linestyle="--")
    # deep
    V.note(ax, 77, 82, "DEEP (deepcopy)", color=V.GREEN, bold=True, size=11)
    V.box(ax, 65, 64, 14, 9, "orig", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 88, 64, 14, 9, "copy", fill="white", edge=V.NAVY, size=11)
    V.box(ax, 65, 44, 16, 9, "[1,2]", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 88, 44, 16, 9, "[1,2]", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 65, 59, 65, 49, color=V.GREEN)
    V.arrow(ax, 88, 59, 88, 49, color=V.GREEN)
    V.note(ax, 76, 33, "inner list CLONED", color=V.GREEN, size=10)
    V.caption(ax, "Shallow copies share nested objects; deepcopy clones the whole tree.")
    V.save(fig, IMG + "m02_08_shallow_vs_deep.png")


if __name__ == "__main__":
    for f in [d01_name_vs_object, d02_id_type_value, d03_assignment_reference,
              d04_mutable_immutable, d05_is_vs_eq, d06_interning,
              d07_arg_passing, d08_shallow_vs_deep]:
        f()
    print("M02 diagrams done.")
