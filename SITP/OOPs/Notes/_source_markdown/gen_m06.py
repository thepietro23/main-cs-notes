"""Module 6 — Polymorphism: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_one_interface_many():
    fig, ax = V.new_canvas()
    V.title(ax, "Polymorphism: one interface, many forms")
    V.box(ax, 50, 76, 34, 11, "for a in animals:\n    a.speak()", fill=V.BLUE_F, size=11)
    V.box(ax, 20, 44, 22, 12, "Dog\n-> Woof", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 50, 44, 22, 12, "Cat\n-> Meow", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 80, 44, 22, 12, "Cow\n-> Moo", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 42, 71, 22, 51, color=V.NAVY)
    V.arrow(ax, 50, 71, 50, 51, color=V.NAVY)
    V.arrow(ax, 58, 71, 80, 51, color=V.NAVY)
    V.note(ax, 50, 28, "same call a.speak() -> different behaviour per object", color=V.RED, size=11)
    V.caption(ax, "The caller uses one uniform call; each object responds in its own way.")
    V.save(fig, IMG + "m06_01_one_interface_many.png")


def d02_poly_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Four kinds of polymorphism")
    data = [
        (27, 62, "Subtype\n(overriding)", "Dog.speak()\noverrides Animal", V.GREEN_F, V.GREEN),
        (73, 62, "Ad-hoc\n(overloading)", "+ adds ints,\njoins strings", V.ORANGE_F, V.ORANGE),
        (27, 34, "Parametric\n(generics)", "list[T] works\nfor any T", V.BLUE_F, V.NAVY),
        (73, 34, "Coercion\n(casting)", "int + float\n-> float", V.BLUE_F, V.NAVY),
    ]
    for x, y, name, ex, fill, edge in data:
        V.box(ax, x, y, 40, 20, "", fill=fill, edge=edge)
        V.note(ax, x, y + 5, name, color=edge, bold=True, size=11)
        V.note(ax, x, y - 4, ex, size=10)
    V.caption(ax, "Python leans on subtype (overriding) + ad-hoc (dunders) + duck typing.")
    V.save(fig, IMG + "m06_02_poly_types.png")


def d03_overriding_runtime():
    fig, ax = V.new_canvas()
    V.title(ax, "Runtime dispatch: actual object type decides")
    V.box(ax, 25, 66, 30, 12, "shape.area()", fill=V.BLUE_F, size=12)
    V.note(ax, 25, 52, "which area()?", color=V.GRAY, size=10)
    V.arrow(ax, 40, 62, 60, 70, color=V.GREEN)
    V.arrow(ax, 40, 60, 60, 44, color=V.GREEN)
    V.box(ax, 78, 72, 30, 10, "if Circle -> pi r^2", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 42, 30, 10, "if Square -> s*s", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 26, "decided at RUN time by the object's real class (dynamic dispatch)", color=V.RED, size=10)
    V.caption(ax, "Python resolves the overridden method by the object's runtime type.")
    V.save(fig, IMG + "m06_03_overriding_runtime.png")


def d04_duck_typing():
    fig, ax = V.new_canvas()
    V.title(ax, "Duck typing: behaviour matters, not the type")
    V.box(ax, 50, 74, 46, 11, "def make_it_quack(x): x.quack()", fill=V.BLUE_F, size=11)
    V.box(ax, 22, 46, 22, 12, "Duck\nhas quack()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 46, 22, 12, "Person\nhas quack()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 46, 22, 12, "Dog\nno quack()", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 40, 69, 24, 53, color=V.GREEN)
    V.arrow(ax, 50, 69, 50, 53, color=V.GREEN)
    V.arrow(ax, 60, 69, 76, 53, color=V.RED)
    V.note(ax, 50, 28, "'If it quacks, it's a duck.' No inheritance needed — just the method.", color=V.RED, size=10)
    V.caption(ax, "Duck typing: if the object supports the operation, it works — type ignored.")
    V.save(fig, IMG + "m06_04_duck_typing.png")


def d05_operator_overload():
    fig, ax = V.new_canvas()
    V.title(ax, "Operator overloading: '+' means many things")
    V.box(ax, 50, 78, 20, 10, "a + b", fill=V.BLUE_F, size=13)
    V.box(ax, 18, 52, 26, 12, "int + int\n= 5 (add)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 52, 26, 12, "str + str\n= 'ab' (join)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 82, 52, 26, 12, "list+list\n= merge", fill=V.BLUE_F, size=10)
    V.arrow(ax, 44, 74, 20, 58, color=V.NAVY)
    V.arrow(ax, 50, 74, 50, 58, color=V.NAVY)
    V.arrow(ax, 56, 74, 80, 58, color=V.NAVY)
    V.note(ax, 50, 32, "a + b really calls a.__add__(b) — each type defines its own", color=V.RED, size=11)
    V.caption(ax, "The '+' operator dispatches to __add__, so each type gives it meaning.")
    V.save(fig, IMG + "m06_05_operator_overload.png")


def d06_no_overloading():
    fig, ax = V.new_canvas()
    V.title(ax, "Python has NO method overloading")
    V.box(ax, 27, 66, 30, 12, "def area(r):\ndef area(l, w):", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 43, 66, 58, 66, color=V.NAVY)
    V.box(ax, 78, 66, 30, 12, "2nd def WINS;\n1st is erased", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.note(ax, 50, 44, "Same name = redefinition, not overloading.", color=V.RED, size=11)
    V.note(ax, 50, 32, "Instead use: default args | *args | @singledispatch", color=V.GREEN, size=11)
    V.caption(ax, "Two defs with one name -> the last replaces the first; use flexible args.")
    V.save(fig, IMG + "m06_06_no_overloading.png")


def d07_singledispatch():
    fig, ax = V.new_canvas()
    V.title(ax, "functools.singledispatch: pick impl by 1st arg type")
    V.box(ax, 50, 76, 26, 10, "process(x)", fill=V.BLUE_F, size=12)
    V.box(ax, 20, 48, 22, 12, "x is int\n-> double", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 48, 22, 12, "x is str\n-> upper", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 80, 48, 22, 12, "x is list\n-> reverse", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 71, 22, 55, color=V.NAVY)
    V.arrow(ax, 50, 71, 50, 55, color=V.NAVY)
    V.arrow(ax, 58, 71, 80, 55, color=V.NAVY)
    V.note(ax, 50, 30, "@singledispatch + @process.register(str) etc.", color=V.RED, size=11)
    V.caption(ax, "singledispatch gives function 'overloading' by the type of the first argument.")
    V.save(fig, IMG + "m06_07_singledispatch.png")


def d08_compile_vs_runtime():
    fig, ax = V.new_canvas()
    V.title(ax, "Compile-time vs Run-time polymorphism")
    V.box(ax, 27, 60, 38, 30, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 72, "COMPILE-TIME", color=V.ORANGE, bold=True, size=11)
    V.note(ax, 27, 62, "overloading,\noperator overload\n(resolved early)", size=10)
    V.note(ax, 27, 48, "static / 'ad-hoc'", color=V.GRAY, size=9)
    V.box(ax, 73, 60, 38, 30, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 72, "RUN-TIME", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 62, "overriding,\nduck typing\n(resolved late)", size=10)
    V.note(ax, 73, 48, "dynamic / 'subtype'", color=V.GRAY, size=9)
    V.note(ax, 50, 30, "Python is dynamic: nearly ALL dispatch is at run time", color=V.RED, size=11)
    V.caption(ax, "Static languages resolve overloading early; Python resolves by type at run time.")
    V.save(fig, IMG + "m06_08_compile_vs_runtime.png")


if __name__ == "__main__":
    for f in [d01_one_interface_many, d02_poly_types, d03_overriding_runtime,
              d04_duck_typing, d05_operator_overload, d06_no_overloading,
              d07_singledispatch, d08_compile_vs_runtime]:
        f()
    print("M06 diagrams done.")
