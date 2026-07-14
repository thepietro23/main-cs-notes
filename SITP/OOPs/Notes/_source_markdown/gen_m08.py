"""Module 8 — Descriptors, __slots__ & Attribute Access: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_attr_hooks():
    fig, ax = V.new_canvas()
    V.title(ax, "obj.x access flow")
    V.box(ax, 50, 80, 22, 9, "obj.x", fill=V.BLUE_F, size=13)
    V.box(ax, 50, 62, 40, 10, "__getattribute__ (ALWAYS called)", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 50, 75, 50, 67)
    V.box(ax, 25, 42, 28, 10, "found -> return value", fill=V.GREEN_F, edge=V.GREEN, tcolor=V.GREEN, size=10)
    V.box(ax, 76, 42, 30, 10, "not found?", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 40, 57, 27, 47, color=V.GREEN)
    V.arrow(ax, 60, 57, 76, 47, color=V.RED)
    V.box(ax, 76, 22, 30, 10, "__getattr__ fallback", fill=V.BLUE_F, size=10)
    V.arrow(ax, 76, 37, 76, 27, color=V.NAVY)
    V.note(ax, 25, 30, "AttributeError if\nneither yields it", color=V.GRAY, size=9)
    V.caption(ax, "__getattribute__ runs first; __getattr__ is the fallback only when it fails.")
    V.save(fig, IMG + "m08_01_attr_hooks.png")


def d02_getattr_vs_getattribute():
    fig, ax = V.new_canvas()
    V.title(ax, "__getattr__ vs __getattribute__")
    V.box(ax, 27, 58, 40, 40, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 72, "__getattribute__", color=V.ORANGE, bold=True, size=12)
    V.note(ax, 27, 61, "called on EVERY\naccess", size=11)
    V.note(ax, 27, 47, "override with care\n(recursion risk)", color=V.RED, size=10)
    V.box(ax, 73, 58, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 72, "__getattr__", color=V.GREEN, bold=True, size=12)
    V.note(ax, 73, 61, "called ONLY when\nnormal lookup fails", size=11)
    V.note(ax, 73, 47, "safe for defaults,\nproxies, lazy attrs", color=V.GRAY, size=10)
    V.caption(ax, "__getattribute__ = every time (dangerous); __getattr__ = on miss (handy).")
    V.save(fig, IMG + "m08_02_getattr_vs_getattribute.png")


def d03_descriptor_protocol():
    fig, ax = V.new_canvas()
    V.title(ax, "Descriptor protocol: an object that manages access")
    V.box(ax, 50, 74, 46, 10, "class C:  age = Descriptor()  (class attr)", fill=V.BLUE_F, size=11)
    rows = [(54, "__get__(self, obj, owner)", "read c.age", V.GREEN_F, V.GREEN),
            (40, "__set__(self, obj, value)", "write c.age = v", V.ORANGE_F, V.ORANGE),
            (26, "__delete__(self, obj)", "del c.age", V.BLUE_F, V.NAVY)]
    for y, sig, desc, fill, edge in rows:
        V.box(ax, 34, y, 40, 9, sig, fill=fill, edge=edge, size=10)
        V.note(ax, 80, y, desc, size=10)
    V.caption(ax, "A descriptor is a class attribute defining __get__/__set__/__delete__.")
    V.save(fig, IMG + "m08_03_descriptor_protocol.png")


def d04_data_vs_nondata():
    fig, ax = V.new_canvas()
    V.title(ax, "Data vs non-data descriptors")
    V.box(ax, 27, 58, 40, 40, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 72, "DATA descriptor", color=V.ORANGE, bold=True, size=11)
    V.note(ax, 27, 62, "__get__ + __set__\n(or __delete__)", size=10)
    V.note(ax, 27, 49, "WINS over instance dict", color=V.RED, size=10)
    V.box(ax, 73, 58, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 72, "NON-DATA descriptor", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 62, "__get__ only", size=10)
    V.note(ax, 73, 49, "instance dict WINS", color=V.GRAY, size=10)
    V.note(ax, 50, 28, "@property = data descriptor; a plain method = non-data", color=V.NAVY, size=11)
    V.caption(ax, "Data descriptors override instance attributes; non-data ones are overridden.")
    V.save(fig, IMG + "m08_04_data_vs_nondata.png")


def d05_property_is_descriptor():
    fig, ax = V.new_canvas()
    V.title(ax, "Everything is built on descriptors")
    items = [(72, "@property", "data descriptor"),
             (56, "methods", "non-data descriptor (functions)"),
             (40, "classmethod / staticmethod", "descriptors"),
             (24, "super()", "uses descriptors")]
    for y, name, kind in items:
        V.box(ax, 30, y, 34, 10, name, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.arrow(ax, 47, y, 58, y, color=V.NAVY)
        V.note(ax, 78, y, kind, size=10)
    V.caption(ax, "properties, methods, classmethod & staticmethod are all descriptors underneath.")
    V.save(fig, IMG + "m08_05_property_is_descriptor.png")


def d06_validator_descriptor():
    fig, ax = V.new_canvas()
    V.title(ax, "One validator descriptor, reused on many fields")
    V.box(ax, 50, 74, 40, 10, "class Product:", fill=V.BLUE_F, size=12)
    V.box(ax, 22, 54, 26, 12, "price =\nPositive()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 54, 26, 12, "weight =\nPositive()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 40, 69, 24, 61, color=V.NAVY)
    V.arrow(ax, 60, 69, 78, 61, color=V.NAVY)
    V.box(ax, 50, 32, 40, 12, "class Positive: __set__ checks >0", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 30, 48, 45, 38, color=V.RED, dashed=True)
    V.arrow(ax, 70, 48, 55, 38, color=V.RED, dashed=True)
    V.note(ax, 50, 18, "write the validation ONCE; apply to every field. DRY!", color=V.RED, size=11)
    V.caption(ax, "Descriptors factor out repeated validation/logic into one reusable class.")
    V.save(fig, IMG + "m08_06_validator_descriptor.png")


def d07_slots_memory():
    fig, ax = V.new_canvas()
    V.title(ax, "__slots__ removes the per-instance __dict__")
    V.note(ax, 27, 80, "DEFAULT (__dict__)", color=V.ORANGE, bold=True, size=11)
    V.box(ax, 27, 58, 34, 26, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 66, "each instance carries\na full dict\n(flexible, heavier)", size=10)
    V.note(ax, 27, 40, "~big memory / object", color=V.RED, size=10)
    V.note(ax, 74, 80, "__slots__", color=V.GREEN, bold=True, size=11)
    V.box(ax, 74, 58, 34, 26, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 74, 66, "fixed slots array\nno __dict__\n(compact, faster)", size=10)
    V.note(ax, 74, 40, "~40-50% less memory", color=V.GREEN, size=10)
    V.caption(ax, "__slots__ = ('a','b') trades dynamic attributes for big memory/speed gains.")
    V.save(fig, IMG + "m08_07_slots_memory.png")


def d08_precedence():
    fig, ax = V.new_canvas()
    V.title(ax, "Attribute lookup precedence (read)")
    order = ["1. data descriptor (class)", "2. instance __dict__",
             "3. non-data descriptor / class attr", "4. __getattr__", "5. AttributeError"]
    ys = [74, 60, 46, 32, 18]
    cols = [(V.ORANGE_F, V.ORANGE), (V.BLUE_F, V.NAVY), (V.GREEN_F, V.GREEN),
            (V.BLUE_F, V.NAVY), (V.RED, V.RED)]
    for y, txt, (f, e) in zip(ys, order, cols):
        tc = "white" if f == V.RED else V.BLACK
        V.box(ax, 50, y, 62, 10, txt, fill=f, edge=e, tcolor=tc, size=11)
    for i in range(len(ys) - 1):
        V.arrow(ax, 50, ys[i] - 5, 50, ys[i + 1] + 5, color=V.GRAY)
    V.caption(ax, "Data descriptors beat the instance dict; the dict beats non-data descriptors.")
    V.save(fig, IMG + "m08_08_precedence.png")


if __name__ == "__main__":
    for f in [d01_attr_hooks, d02_getattr_vs_getattribute, d03_descriptor_protocol,
              d04_data_vs_nondata, d05_property_is_descriptor, d06_validator_descriptor,
              d07_slots_memory, d08_precedence]:
        f()
    print("M08 diagrams done.")
