"""Module 4 — Encapsulation & Abstraction: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_encapsulation_capsule():
    fig, ax = V.new_canvas()
    V.title(ax, "Encapsulation: data sealed inside; methods are the API")
    V.box(ax, 50, 52, 50, 44, "", fill=V.BLUE_F, edge=V.NAVY)
    V.box(ax, 50, 58, 26, 12, "_balance\n(hidden data)", fill=V.RED, tcolor="white", size=11)
    V.box(ax, 30, 40, 20, 8, "deposit()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 70, 40, 20, 8, "withdraw()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 30, "outside code talks ONLY to the green methods", color=V.GREEN, size=11)
    V.arrow(ax, 15, 40, 20, 40, color=V.GREEN)
    V.arrow(ax, 85, 40, 80, 40, color=V.GREEN)
    V.caption(ax, "Bundle data + methods; expose a safe API; hide and guard the internals.")
    V.save(fig, IMG + "m04_01_encapsulation_capsule.png")


def d02_access_levels():
    fig, ax = V.new_canvas()
    V.title(ax, "Python 'access levels' (all by convention)")
    rows = [
        (72, "name", "PUBLIC", "use freely, part of the API", V.GREEN_F, V.GREEN),
        (52, "_name", "PROTECTED", "internal; 'please don't touch'", V.ORANGE_F, V.ORANGE),
        (32, "__name", "PRIVATE-ish", "name-mangled to _Class__name", V.BLUE_F, V.NAVY),
    ]
    for y, code, label, desc, fill, edge in rows:
        V.box(ax, 18, y, 20, 12, code, fill=fill, edge=edge, size=13)
        V.note(ax, 40, y + 2, label, color=edge, bold=True, size=12, ha="center")
        V.note(ax, 74, y, desc, size=11, ha="center")
    V.note(ax, 50, 16, "Python has NO true 'private' — only conventions + mangling", color=V.RED, size=11)
    V.caption(ax, "One underscore = a hint; two = name mangling; nothing is truly locked.")
    V.save(fig, IMG + "m04_02_access_levels.png")


def d03_name_mangling():
    fig, ax = V.new_canvas()
    V.title(ax, "Name mangling: __x becomes _ClassName__x")
    V.box(ax, 25, 62, 30, 14, "class Account:\n  self.__balance", fill=V.BLUE_F, size=11)
    V.arrow(ax, 41, 62, 60, 62, color=V.NAVY)
    V.note(ax, 50, 69, "compiler", color=V.GRAY, size=9)
    V.box(ax, 79, 62, 34, 14, "stored as\n_Account__balance", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.note(ax, 50, 42, "acc.__balance    -> AttributeError (mangled away)", color=V.RED, size=11)
    V.note(ax, 50, 33, "acc._Account__balance -> works (but don't)", color=V.GRAY, size=11)
    V.note(ax, 50, 22, "purpose: avoid name CLASHES in subclasses, not security", color=V.NAVY, size=11)
    V.caption(ax, "Double underscore mangles the name to dodge subclass clashes — not to lock it.")
    V.save(fig, IMG + "m04_03_name_mangling.png")


def d04_property():
    fig, ax = V.new_canvas()
    V.title(ax, "@property: attribute syntax, method behaviour")
    V.box(ax, 22, 60, 28, 12, "obj.temp\n(looks like attr)", fill=V.BLUE_F, size=11)
    V.arrow(ax, 36, 60, 56, 60, color=V.NAVY)
    V.box(ax, 76, 60, 34, 14, "runs getter/setter\nmethod behind it", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 50, 38, "no parentheses needed; caller code never changes", color=V.NAVY, size=11)
    V.note(ax, 50, 28, "lets you add validation / computation later", color=V.RED, size=11)
    V.caption(ax, "A property makes a method callable with plain attribute syntax (obj.temp).")
    V.save(fig, IMG + "m04_04_property.png")


def d05_getter_setter_flow():
    fig, ax = V.new_canvas()
    V.title(ax, "A validating property setter")
    V.box(ax, 18, 60, 24, 12, "c.temp = -500", fill=V.BLUE_F, size=11)
    V.arrow(ax, 30, 60, 44, 60, color=V.NAVY)
    V.box(ax, 60, 60, 26, 12, "@temp.setter\ncheck value", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 73, 66, 86, 74, color=V.RED)
    V.arrow(ax, 73, 54, 86, 46, color=V.GREEN)
    V.box(ax, 90, 76, 16, 9, "reject\n(raise)", fill=V.RED, tcolor="white", size=10)
    V.box(ax, 90, 44, 16, 9, "store\nvalue", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 28, "below -273.15 C -> ValueError; else set _temp", color=V.RED, size=11)
    V.caption(ax, "Setters enforce invariants; bad values are rejected before state changes.")
    V.save(fig, IMG + "m04_05_getter_setter_flow.png")


def d06_abstraction_layers():
    fig, ax = V.new_canvas()
    V.title(ax, "Abstraction: expose WHAT, hide HOW")
    V.box(ax, 50, 72, 46, 12, "list.sort()   (what you call)", fill=V.GREEN_F, edge=V.GREEN, size=12)
    V.arrow(ax, 50, 66, 50, 56)
    V.box(ax, 50, 48, 60, 14, "Timsort: merge runs, insertion sort...\n(HOW — hidden from you)", fill=V.BLUE_F, size=10)
    V.note(ax, 50, 30, "you steer the car; you don't touch the engine", color=V.RED, size=11)
    V.caption(ax, "Abstraction gives a simple interface over complex hidden machinery.")
    V.save(fig, IMG + "m04_06_abstraction_layers.png")


def d07_abc():
    fig, ax = V.new_canvas()
    V.title(ax, "Abstract Base Class forces subclasses to implement")
    V.box(ax, 50, 76, 40, 12, "class Shape(ABC):\n  @abstractmethod area()", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.note(ax, 82, 76, "cannot\ninstantiate", color=V.RED, size=9)
    V.box(ax, 25, 46, 24, 12, "Circle\narea() defined", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 60, 46, 24, 12, "Square\narea() defined", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 88, 46, 20, 12, "Blob\n(no area)", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 42, 70, 27, 53, color=V.NAVY)
    V.arrow(ax, 55, 70, 60, 53, color=V.NAVY)
    V.arrow(ax, 62, 70, 86, 53, color=V.NAVY)
    V.note(ax, 50, 28, "Shape() -> TypeError;  Blob() -> TypeError (area not implemented)", color=V.RED, size=10)
    V.caption(ax, "An ABC defines a required interface; concrete subclasses MUST implement it.")
    V.save(fig, IMG + "m04_07_abc.png")


def d08_pythonic_property():
    fig, ax = V.new_canvas()
    V.title(ax, "Pythonic rule: start public, add property LATER")
    V.box(ax, 25, 62, 30, 14, "self.temp = t\n(just public)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 41, 62, 58, 62, color=V.NAVY)
    V.note(ax, 50, 69, "need validation?", color=V.GRAY, size=9)
    V.box(ax, 78, 62, 32, 14, "make temp a\n@property later", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.note(ax, 50, 40, "caller code (obj.temp) NEVER changes -> no upfront getters", color=V.RED, size=11)
    V.note(ax, 50, 28, "don't write Java-style get_x()/set_x() in Python", color=V.NAVY, size=11)
    V.caption(ax, "Expose attributes directly; upgrade to a property only when you need logic.")
    V.save(fig, IMG + "m04_08_pythonic_property.png")


if __name__ == "__main__":
    for f in [d01_encapsulation_capsule, d02_access_levels, d03_name_mangling,
              d04_property, d05_getter_setter_flow, d06_abstraction_layers,
              d07_abc, d08_pythonic_property]:
        f()
    print("M04 diagrams done.")
