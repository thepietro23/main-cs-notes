"""Module 21 — Revision Kit & Cheat Sheets: diagram generator."""
import viz_style as V
IMG = "../images/"


def d01_pillars_recall():
    fig, ax = V.new_canvas()
    V.title(ax, "The four pillars at a glance (A PIE)")
    data = [(18, "Abstraction", "what, not how", V.ORANGE_F, V.ORANGE),
            (39, "Polymorphism", "one name,\nmany forms", V.BLUE_F, V.NAVY),
            (61, "Inheritance", "reuse via\nis-a", V.GREEN_F, V.GREEN),
            (82, "Encapsulation", "bundle +\nhide", V.BLUE_F, V.NAVY)]
    for x, name, sub, f, e in data:
        V.box(ax, x, 52, 19, 34, "", fill=f, edge=e)
        V.note(ax, x, 61, name, color=e, bold=True, size=10)
        V.note(ax, x, 48, sub, size=10)
    V.caption(ax, "A PIE: Abstraction, Polymorphism, Inheritance, Encapsulation.")
    V.save(fig, IMG + "m21_01_pillars_recall.png")


def d02_dunder_table():
    fig, ax = V.new_canvas()
    V.title(ax, "Dunder quick-reference")
    rows = [(76, "__init__/__new__", "init / create"),
            (65, "__repr__/__str__", "dev / user string"),
            (54, "__eq__ + __hash__", "value equality (+ hashable)"),
            (43, "__lt__ ... / total_ordering", "comparison / sort"),
            (32, "__len__/__getitem__/__iter__", "container / iterable"),
            (21, "__enter__/__exit__ ; __call__", "context mgr ; callable")]
    for y, d, w in rows:
        V.box(ax, 32, y, 42, 8, d, fill=V.GREEN_F, edge=V.GREEN, size=9)
        V.note(ax, 80, y, w, size=9)
    V.caption(ax, "Implement the dunder -> your object plugs into Python syntax.")
    V.save(fig, IMG + "m21_02_dunder_table.png")


def d03_mro_super():
    fig, ax = V.new_canvas()
    V.title(ax, "MRO & super() rules")
    V.box(ax, 50, 74, 60, 10, "D(B, C), B(A), C(A) -> MRO: D, B, C, A, object", fill=V.BLUE_F, size=10)
    rows = ["C3: subclass first, left-to-right, ancestor after ALL descendants, each once",
            "super() -> NEXT class in the MRO (not always literal parent)",
            "always super().__init__(...) for cooperative multiple inheritance",
            "check with Cls.__mro__ / Cls.mro()"]
    for i, t in enumerate(rows):
        V.note(ax, 12, 58 - i * 10, "- " + t, size=10, ha="left")
    V.caption(ax, "One deterministic order; super() walks it so each ancestor runs once.")
    V.save(fig, IMG + "m21_03_mro_super.png")


def d04_solid_recall():
    fig, ax = V.new_canvas()
    V.title(ax, "SOLID in one glance")
    rows = [(74, "S", "one reason to change"),
            (60, "O", "extend, don't modify (polymorphism)"),
            (46, "L", "subtype substitutable for base"),
            (32, "I", "small, focused interfaces"),
            (18, "D", "depend on abstractions (inject)")]
    for y, l, t in rows:
        V.circle(ax, 16, y, 5.5, l, fill=V.NAVY, tcolor="white", size=13)
        V.note(ax, 60, y, t, size=11)
    V.caption(ax, "SRP, OCP, LSP, ISP, DIP — the pillars applied with intent.")
    V.save(fig, IMG + "m21_04_solid_recall.png")


def d05_patterns_map():
    fig, ax = V.new_canvas()
    V.title(ax, "Patterns map (problem -> pattern)")
    rows = [(74, "pluggable policy", "Strategy"),
            (62, "mode / status behaviour", "State"),
            (50, "create by type", "Factory"),
            (38, "notify many", "Observer"),
            (26, "add behaviour by wrapping", "Decorator"),
            (14, "simplify a subsystem", "Facade")]
    for y, prob, pat in rows:
        V.note(ax, 20, y, prob, size=10, ha="left")
        V.arrow(ax, 52, y, 60, y, color=V.GRAY)
        V.box(ax, 76, y, 26, 9, pat, fill=V.BLUE_F, size=10)
    V.caption(ax, "Recognise the sub-problem, reach for the matching pattern.")
    V.save(fig, IMG + "m21_05_patterns_map.png")


def d06_method_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Methods & @property recall")
    data = [(20, "instance", "self (state)", V.GREEN_F, V.GREEN),
            (40, "@classmethod", "cls (factory)", V.ORANGE_F, V.ORANGE),
            (60, "@staticmethod", "nothing (helper)", V.BLUE_F, V.NAVY),
            (82, "@property", "attr syntax +\nvalidation", V.GREEN_F, V.GREEN)]
    for x, name, sub, f, e in data:
        V.box(ax, x, 52, 19, 32, "", fill=f, edge=e)
        V.note(ax, x, 60, name, color=e, bold=True, size=10)
        V.note(ax, x, 47, sub, size=9)
    V.caption(ax, "self=state, cls=factory, static=helper, property=method as attribute.")
    V.save(fig, IMG + "m21_06_method_types.png")


def d07_tooling_recall():
    fig, ax = V.new_canvas()
    V.title(ax, "Modern tooling recall")
    rows = [(72, "@dataclass", "auto init/repr/eq; frozen; default_factory"),
            (58, "NamedTuple", "immutable tuple record"),
            (44, "Enum", "named singleton constants"),
            (30, "Protocol", "structural typing (static duck typing)"),
            (16, "__slots__", "no __dict__ -> memory/speed")]
    for y, name, w in rows:
        V.box(ax, 22, y, 24, 9, name, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.note(ax, 74, y, w, size=9)
    V.caption(ax, "Reach for these before hand-rolling boilerplate classes.")
    V.save(fig, IMG + "m21_07_tooling_recall.png")


def d08_course_map():
    fig, ax = V.new_canvas()
    V.title(ax, "The journey: 21 modules")
    blocks = [(18, "Foundations", "M1-M4\nintro, object model,\nclasses, encap/abstr", V.GREEN_F, V.GREEN),
              (39, "Core OOP", "M5-M9\ninherit, poly, dunders,\ndescriptors, metaclass", V.BLUE_F, V.NAVY),
              (61, "Modern + Design", "M10-M17\ntooling, typing, memory,\nSOLID, patterns, UML", V.ORANGE_F, V.ORANGE),
              (82, "Mastery", "M18-M21\nLLD, refactoring,\nQ-bank, cheat sheets", V.GREEN_F, V.GREEN)]
    for x, name, sub, f, e in blocks:
        V.box(ax, x, 52, 20, 40, "", fill=f, edge=e)
        V.note(ax, x, 63, name, color=e, bold=True, size=10)
        V.note(ax, x, 48, sub, size=8)
        if x < 82:
            V.arrow(ax, x + 10, 52, x + 11, 52, color=V.GRAY)
    V.caption(ax, "Foundations -> core OOP -> modern & design -> interview mastery.")
    V.save(fig, IMG + "m21_08_course_map.png")


if __name__ == "__main__":
    for f in [d01_pillars_recall, d02_dunder_table, d03_mro_super, d04_solid_recall,
              d05_patterns_map, d06_method_types, d07_tooling_recall, d08_course_map]:
        f()
    print("M21 diagrams done.")
