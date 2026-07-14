"""Module 10 — Modern OOP Tooling: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_before_after():
    fig, ax = V.new_canvas()
    V.title(ax, "@dataclass kills boilerplate")
    V.box(ax, 27, 55, 40, 46, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 74, "BY HAND", color=V.ORANGE, bold=True, size=12)
    V.note(ax, 27, 60, "__init__\n__repr__\n__eq__\n(15+ lines)", size=11)
    V.note(ax, 27, 40, "error-prone, verbose", color=V.RED, size=10)
    V.arrow(ax, 49, 55, 60, 55, color=V.NAVY)
    V.box(ax, 76, 55, 38, 46, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 76, 74, "@dataclass", color=V.GREEN, bold=True, size=12)
    V.note(ax, 76, 60, "class Point:\n  x: int\n  y: int", size=11)
    V.note(ax, 76, 40, "3 lines; all generated", color=V.GREEN, size=10)
    V.caption(ax, "@dataclass generates __init__, __repr__, __eq__ from typed fields.")
    V.save(fig, IMG + "m10_01_before_after.png")


def d02_dataclass_generated():
    fig, ax = V.new_canvas()
    V.title(ax, "What @dataclass generates for you")
    V.box(ax, 50, 76, 40, 10, "@dataclass class Point: x:int; y:int", fill=V.BLUE_F, size=10)
    gens = [(60, "__init__(self, x, y)", V.GREEN_F, V.GREEN),
            (48, "__repr__ -> Point(x=1, y=2)", V.GREEN_F, V.GREEN),
            (36, "__eq__ (compares fields)", V.GREEN_F, V.GREEN),
            (24, "(opt) __lt__, __hash__, __slots__", V.ORANGE_F, V.ORANGE)]
    for y, txt, f, e in gens:
        V.box(ax, 50, y, 52, 9, txt, fill=f, edge=e, size=10)
        V.arrow(ax, 50, min(71, y + 8), 50, y + 5, color=V.GRAY)
    V.caption(ax, "Typed class attributes become fields; the dunders are written for you.")
    V.save(fig, IMG + "m10_02_dataclass_generated.png")


def d03_field_options():
    fig, ax = V.new_canvas()
    V.title(ax, "dataclass options & field()")
    rows = [(72, "default_factory=list", "fresh list per instance (no shared-default bug)"),
            (58, "frozen=True", "immutable + hashable"),
            (44, "order=True", "adds < <= > >= (sortable)"),
            (30, "field(compare=False)", "exclude a field from ==/order")]
    for y, opt, desc in rows:
        V.box(ax, 24, y, 32, 9, opt, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.note(ax, 76, y, desc, size=9)
    V.caption(ax, "Options tune what's generated; field() configures individual fields.")
    V.save(fig, IMG + "m10_03_field_options.png")


def d04_post_init():
    fig, ax = V.new_canvas()
    V.title(ax, "__post_init__: derived fields & validation")
    V.box(ax, 22, 62, 26, 12, "__init__\n(generated)\nsets x, y", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 35, 62, 55, 62, color=V.NAVY)
    V.box(ax, 78, 62, 30, 14, "__post_init__\ncompute dist,\nvalidate", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.note(ax, 50, 38, "runs right AFTER the generated __init__", color=V.RED, size=11)
    V.note(ax, 50, 28, "use for: derived values, cross-field checks", color=V.GRAY, size=10)
    V.caption(ax, "__post_init__ hooks the generated constructor for derived/validated state.")
    V.save(fig, IMG + "m10_04_post_init.png")


def d05_namedtuple():
    fig, ax = V.new_canvas()
    V.title(ax, "NamedTuple: immutable, named + indexable")
    V.box(ax, 50, 72, 40, 10, "Point = NamedTuple('Point', x=int, y=int)", fill=V.BLUE_F, size=10)
    V.box(ax, 25, 50, 26, 12, "p.x , p.y\n(named access)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 50, 26, 12, "p[0], p[1]\n(tuple access)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 67, 28, 57, color=V.NAVY)
    V.arrow(ax, 58, 67, 70, 57, color=V.NAVY)
    V.note(ax, 50, 30, "immutable, hashable, tiny memory — great for fixed records", color=V.RED, size=11)
    V.caption(ax, "NamedTuple = a tuple with named fields; immutable and lightweight.")
    V.save(fig, IMG + "m10_05_namedtuple.png")


def d06_enum():
    fig, ax = V.new_canvas()
    V.title(ax, "Enum: named, singleton constants")
    V.box(ax, 50, 74, 34, 10, "class Color(Enum):", fill=V.BLUE_F, size=11)
    V.box(ax, 22, 52, 20, 10, "RED = 1", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 52, 20, 10, "GREEN = 2", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 52, 20, 10, "BLUE = 3", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 44, 69, 24, 58, color=V.NAVY)
    V.arrow(ax, 50, 69, 50, 58, color=V.NAVY)
    V.arrow(ax, 56, 69, 78, 58, color=V.NAVY)
    V.note(ax, 50, 32, "Color.RED is a unique singleton; use instead of magic numbers/strings", color=V.RED, size=10)
    V.caption(ax, "Enum gives readable, comparable, singleton constants — no magic values.")
    V.save(fig, IMG + "m10_06_enum.png")


def d07_frozen_hashable():
    fig, ax = V.new_canvas()
    V.title(ax, "frozen=True -> immutable & hashable")
    V.box(ax, 25, 62, 30, 14, "@dataclass(frozen=True)\nclass Point", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 41, 68, 58, 74, color=V.GREEN)
    V.arrow(ax, 41, 56, 58, 50, color=V.RED)
    V.box(ax, 78, 74, 30, 9, "usable as dict key / set", fill=V.BLUE_F, size=10)
    V.box(ax, 78, 50, 30, 9, "p.x = 5 -> FrozenError", fill=V.RED, tcolor="white", size=9)
    V.note(ax, 50, 30, "frozen adds __hash__ and blocks attribute writes", color=V.RED, size=11)
    V.caption(ax, "Frozen dataclasses behave like value objects: immutable and hashable.")
    V.save(fig, IMG + "m10_07_frozen_hashable.png")


def d08_when_which():
    fig, ax = V.new_canvas()
    V.title(ax, "Which container type?")
    data = [
        (27, 62, "@dataclass", "mutable record\n+ methods", V.GREEN_F, V.GREEN),
        (73, 62, "NamedTuple", "immutable record,\ntuple-like", V.BLUE_F, V.NAVY),
        (27, 32, "Enum", "fixed set of\nnamed constants", V.ORANGE_F, V.ORANGE),
        (73, 32, "plain class", "rich behaviour /\ncomplex logic", V.BLUE_F, V.NAVY),
    ]
    for x, y, name, desc, f, e in data:
        V.box(ax, x, y, 40, 20, "", fill=f, edge=e)
        V.note(ax, x, y + 5, name, color=e, bold=True, size=11)
        V.note(ax, x, y - 4, desc, size=10)
    V.caption(ax, "dataclass for records, NamedTuple for immutable ones, Enum for constants.")
    V.save(fig, IMG + "m10_08_when_which.png")


if __name__ == "__main__":
    for f in [d01_before_after, d02_dataclass_generated, d03_field_options,
              d04_post_init, d05_namedtuple, d06_enum, d07_frozen_hashable,
              d08_when_which]:
        f()
    print("M10 diagrams done.")
