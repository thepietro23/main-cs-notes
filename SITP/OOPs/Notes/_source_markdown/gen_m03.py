"""Module 3 — Classes & Objects: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_anatomy_class():
    fig, ax = V.new_canvas()
    V.title(ax, "Anatomy of a class definition")
    V.box(ax, 50, 55, 74, 58, "", fill=V.BLUE_F, edge=V.NAVY)
    V.note(ax, 50, 78, "class BankAccount:", color=V.NAVY, bold=True, size=13)
    V.note(ax, 22, 70, "class keyword", color=V.GRAY, size=9)
    V.box(ax, 50, 63, 60, 8, "def __init__(self, owner): ...", fill="white", edge=V.ORANGE, size=11)
    V.note(ax, 88, 63, "constructor", color=V.ORANGE, size=9)
    V.box(ax, 50, 51, 60, 8, "self.owner = owner", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.note(ax, 88, 51, "instance attr", color=V.ORANGE, size=9)
    V.box(ax, 50, 39, 60, 8, "def deposit(self, amt): ...", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 88, 39, "method", color=V.GREEN, size=9)
    V.note(ax, 50, 30, "MIN_BALANCE = 0", color=V.NAVY, size=11)
    V.note(ax, 24, 30, "class attr", color=V.NAVY, size=9)
    V.caption(ax, "A class body holds a constructor, methods, and class-level attributes.")
    V.save(fig, IMG + "m03_01_anatomy_class.png")


def d02_self_binding():
    fig, ax = V.new_canvas()
    V.title(ax, "self: obj.method(x) becomes Class.method(obj, x)")
    V.box(ax, 25, 62, 30, 12, "acc.deposit(100)", fill=V.BLUE_F, size=12)
    V.arrow(ax, 41, 62, 60, 62, color=V.NAVY)
    V.box(ax, 78, 62, 38, 12, "BankAccount.deposit(acc, 100)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 50, 44, "the object before the dot is passed as the first\nparameter 'self' automatically", color=V.RED, size=11)
    V.note(ax, 50, 28, "self is just a name (a convention) — but ALWAYS use it", color=V.GRAY, size=11)
    V.caption(ax, "'self' is the current object; Python passes it for you on every call.")
    V.save(fig, IMG + "m03_02_self_binding.png")


def d03_instance_vs_class_attr():
    fig, ax = V.new_canvas()
    V.title(ax, "Instance attributes vs Class attributes")
    V.box(ax, 50, 78, 40, 12, "class Dog:\n  species = 'canine'  (CLASS attr)", fill=V.BLUE_F, size=11)
    V.box(ax, 22, 48, 26, 20, "dog1\nname='Rex'\n(instance)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 78, 48, 26, 20, "dog2\nname='Fifi'\n(instance)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 40, 72, 26, 59, dashed=True, color=V.NAVY)
    V.arrow(ax, 60, 72, 74, 59, dashed=True, color=V.NAVY)
    V.note(ax, 50, 30, "species SHARED by all dogs;  name is PER-object", color=V.RED, size=11)
    V.caption(ax, "Class attrs are shared by every instance; instance attrs are unique per object.")
    V.save(fig, IMG + "m03_03_instance_vs_class_attr.png")


def d04_attr_lookup():
    fig, ax = V.new_canvas()
    V.title(ax, "Attribute lookup: instance first, then class")
    V.box(ax, 50, 80, 30, 10, "obj.x", fill=V.BLUE_F, size=13)
    V.box(ax, 50, 60, 40, 10, "in obj.__dict__ ?", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 50, 75, 50, 65)
    V.box(ax, 22, 38, 28, 10, "found -> use it", fill=V.GREEN_F, edge=V.GREEN, tcolor=V.GREEN, size=11)
    V.box(ax, 74, 38, 34, 10, "in Class.__dict__ ?", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 40, 56, 24, 44, color=V.GREEN)
    V.arrow(ax, 60, 56, 74, 44, color=V.RED)
    V.note(ax, 32, 51, "yes", color=V.GREEN, size=9, bold=True)
    V.note(ax, 68, 51, "no", color=V.RED, size=9, bold=True)
    V.box(ax, 74, 18, 34, 9, "then bases (MRO), else AttributeError", fill="white", edge=V.GRAY, size=10, bold=False)
    V.arrow(ax, 74, 33, 74, 23, color=V.NAVY)
    V.caption(ax, "Python checks the instance dict, then the class, then parent classes (MRO).")
    V.save(fig, IMG + "m03_04_attr_lookup.png")


def d05_shared_mutable_trap():
    fig, ax = V.new_canvas()
    V.title(ax, "Trap: a MUTABLE class attribute is shared")
    V.box(ax, 50, 80, 44, 10, "class Dog:  tricks = []   (mutable CLASS attr)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 25, 56, 24, 12, "dog1.tricks\n.append('sit')", fill=V.BLUE_F, size=10)
    V.box(ax, 75, 56, 24, 12, "dog2.tricks", fill=V.BLUE_F, size=10)
    V.box(ax, 50, 34, 30, 12, "ONE shared list\n['sit']", fill=V.RED, tcolor="white", size=11)
    V.arrow(ax, 30, 50, 44, 40, color=V.RED)
    V.arrow(ax, 70, 50, 56, 40, color=V.RED)
    V.note(ax, 50, 20, "dog2 unexpectedly has 'sit' too! Put mutables in __init__.", color=V.RED, size=11)
    V.caption(ax, "Mutable class attributes are shared by all instances — a classic bug.")
    V.save(fig, IMG + "m03_05_shared_mutable_trap.png")


def d06_method_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Three kinds of methods — what each receives")
    data = [
        (20, "Instance\nmethod", "def m(self):", "gets the OBJECT\n(self)", V.GREEN_F, V.GREEN),
        (50, "Class\nmethod", "@classmethod\ndef m(cls):", "gets the CLASS\n(cls)", V.ORANGE_F, V.ORANGE),
        (80, "Static\nmethod", "@staticmethod\ndef m():", "gets NOTHING\nautomatic", V.BLUE_F, V.NAVY),
    ]
    for x, title_t, sig, desc, fill, edge in data:
        V.box(ax, x, 55, 26, 40, "", fill=fill, edge=edge)
        V.note(ax, x, 68, title_t, color=edge, bold=True, size=12)
        V.note(ax, x, 56, sig, size=10)
        V.note(ax, x, 44, desc, color=V.GRAY, size=10)
    V.caption(ax, "Instance -> self (data); classmethod -> cls (factories); static -> plain helper.")
    V.save(fig, IMG + "m03_06_method_types.png")


def d07_factory_classmethod():
    fig, ax = V.new_canvas()
    V.title(ax, "classmethod as an alternative constructor (factory)")
    V.box(ax, 22, 62, 30, 14, "'2026-07-10'\n(a string)", fill=V.BLUE_F, size=11)
    V.arrow(ax, 38, 62, 58, 62, color=V.NAVY)
    V.note(ax, 48, 69, "from_string()", color=V.ORANGE, size=10, bold=True)
    V.box(ax, 78, 62, 34, 16, "Date(2026, 7, 10)\nobject", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 50, 40, "@classmethod  def from_string(cls, s):  return cls(...)", color=V.NAVY, size=11)
    V.note(ax, 50, 28, "cls lets subclasses build the RIGHT type", color=V.RED, size=11)
    V.caption(ax, "classmethods build objects from alternative inputs — named constructors.")
    V.save(fig, IMG + "m03_07_factory_classmethod.png")


def d08_object_creation():
    fig, ax = V.new_canvas()
    V.title(ax, "Creating an object: __new__ then __init__")
    V.box(ax, 16, 60, 22, 12, "acc = \nBankAccount(..)", fill=V.BLUE_F, size=10)
    V.arrow(ax, 27, 60, 40, 60, color=V.NAVY)
    V.box(ax, 53, 60, 22, 12, "__new__\nallocates object", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 64, 60, 78, 60, color=V.NAVY)
    V.box(ax, 89, 60, 20, 12, "__init__\nsets state", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 38, "__new__ = CREATE (rarely overridden)", color=V.ORANGE, size=11)
    V.note(ax, 50, 30, "__init__ = INITIALISE (what you usually write)", color=V.GREEN, size=11)
    V.note(ax, 50, 20, "__init__ returns None; it configures an already-made object", color=V.GRAY, size=10)
    V.caption(ax, "Construction is two steps: allocate (__new__), then initialise (__init__).")
    V.save(fig, IMG + "m03_08_object_creation.png")


if __name__ == "__main__":
    for f in [d01_anatomy_class, d02_self_binding, d03_instance_vs_class_attr,
              d04_attr_lookup, d05_shared_mutable_trap, d06_method_types,
              d07_factory_classmethod, d08_object_creation]:
        f()
    print("M03 diagrams done.")
