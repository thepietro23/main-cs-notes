"""Module 9 — Metaclasses & Class Creation: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_classes_are_objects():
    fig, ax = V.new_canvas()
    V.title(ax, "Classes are objects too")
    V.box(ax, 20, 60, 24, 14, "dog1\n(instance)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 50, 60, 24, 14, "Dog\n(a class)", fill=V.BLUE_F, size=11)
    V.box(ax, 82, 60, 24, 14, "type\n(metaclass)", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 32, 60, 38, 60, color=V.NAVY)
    V.arrow(ax, 62, 60, 70, 60, color=V.NAVY)
    V.note(ax, 35, 66, "type()", color=V.GRAY, size=9)
    V.note(ax, 66, 66, "type()", color=V.GRAY, size=9)
    V.note(ax, 50, 38, "type(dog1) is Dog ;  type(Dog) is type", color=V.RED, size=11)
    V.note(ax, 50, 28, "a class is an INSTANCE of its metaclass (type by default)", color=V.NAVY, size=11)
    V.caption(ax, "Objects are instances of classes; classes are instances of metaclasses.")
    V.save(fig, IMG + "m09_01_classes_are_objects.png")


def d02_type_factory():
    fig, ax = V.new_canvas()
    V.title(ax, "type() is the class factory")
    V.box(ax, 25, 62, 34, 16, "type('Dog',\n  (Animal,),\n  {'bark': fn})", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 43, 62, 60, 62, color=V.NAVY)
    V.box(ax, 80, 62, 30, 14, "a new class\n'Dog'", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 25, 42, "name", color=V.GRAY, size=9)
    V.note(ax, 25, 36, "bases (parents)", color=V.GRAY, size=9)
    V.note(ax, 25, 30, "namespace (methods/attrs)", color=V.GRAY, size=9)
    V.note(ax, 50, 20, "class Dog(Animal): ...  is SUGAR for this call", color=V.RED, size=11)
    V.caption(ax, "type(name, bases, namespace) builds a class at run time — what 'class' does.")
    V.save(fig, IMG + "m09_02_type_factory.png")


def d03_metaclass_hooks():
    fig, ax = V.new_canvas()
    V.title(ax, "Metaclass hooks intercept class creation")
    V.box(ax, 50, 78, 40, 9, "class Meta(type):", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    rows = [(60, "__new__(mcs, name, bases, ns)", "create the class object"),
            (46, "__init__(cls, ...)", "initialise the new class"),
            (32, "__call__(cls, *args)", "runs when you make an INSTANCE")]
    for y, sig, desc in rows:
        V.box(ax, 34, y, 40, 9, sig, fill=V.GREEN_F, edge=V.GREEN, size=9)
        V.note(ax, 80, y, desc, size=9)
    V.caption(ax, "Metaclass __new__/__init__ shape the class; __call__ controls instance creation.")
    V.save(fig, IMG + "m09_03_metaclass_hooks.png")


def d04_class_creation_flow():
    fig, ax = V.new_canvas()
    V.title(ax, "What happens when Python reads 'class'")
    steps = [(15, "class body\nexecuted"), (38, "namespace\ndict built"),
             (62, "metaclass\ncalled"), (86, "class object\nreturned")]
    for i, (x, t) in enumerate(steps):
        f = V.ORANGE_F if i == 2 else V.BLUE_F
        e = V.ORANGE if i == 2 else V.NAVY
        V.box(ax, x, 58, 20, 14, t, fill=f, edge=e, size=10)
        if i < 3:
            V.arrow(ax, x + 10, 58, steps[i + 1][0] - 10, 58, color=V.NAVY)
    V.note(ax, 50, 34, "metaclass = type by default; override with class X(metaclass=Meta)", color=V.RED, size=11)
    V.caption(ax, "Defining a class calls its metaclass, which builds and returns the class object.")
    V.save(fig, IMG + "m09_04_class_creation_flow.png")


def d05_registry_pattern():
    fig, ax = V.new_canvas()
    V.title(ax, "Use case: metaclass auto-registers subclasses")
    V.box(ax, 22, 62, 26, 12, "PluginMeta\n(metaclass)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 22, 40, 26, 10, "CsvPlugin", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 22, 24, 26, 10, "JsonPlugin", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 35, 56, 30, 45, color=V.NAVY, dashed=True)
    V.arrow(ax, 35, 56, 30, 29, color=V.NAVY, dashed=True)
    V.box(ax, 72, 43, 30, 20, "REGISTRY\n{'csv': CsvPlugin,\n 'json': JsonPlugin}", fill=V.BLUE_F, size=10)
    V.arrow(ax, 48, 40, 57, 43, color=V.GREEN)
    V.arrow(ax, 48, 24, 57, 38, color=V.GREEN)
    V.note(ax, 60, 20, "each subclass adds itself automatically at definition", color=V.RED, size=10)
    V.caption(ax, "A metaclass runs code per subclass -> perfect for plugin/ORM registries.")
    V.save(fig, IMG + "m09_05_registry_pattern.png")


def d06_init_subclass():
    fig, ax = V.new_canvas()
    V.title(ax, "__init_subclass__: the lighter alternative")
    V.box(ax, 25, 62, 30, 14, "class Base:\n __init_subclass__", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 41, 62, 58, 62, color=V.NAVY)
    V.box(ax, 78, 62, 30, 14, "runs for EACH\nsubclass created", fill=V.BLUE_F, size=10)
    V.note(ax, 50, 40, "no metaclass needed for 'do X per subclass' tasks", color=V.RED, size=11)
    V.note(ax, 50, 30, "added in 3.6 — covers most metaclass registry use-cases", color=V.GRAY, size=10)
    V.caption(ax, "__init_subclass__ hooks subclass creation without writing a metaclass.")
    V.save(fig, IMG + "m09_06_init_subclass.png")


def d07_class_decorator():
    fig, ax = V.new_canvas()
    V.title(ax, "Class decorator: modify a class after creation")
    V.box(ax, 22, 62, 24, 12, "@register\nclass User:", fill=V.BLUE_F, size=10)
    V.arrow(ax, 34, 62, 52, 62, color=V.NAVY)
    V.box(ax, 70, 62, 28, 14, "register(User)\ntweaks/returns it", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 40, "simplest tool: takes a class, returns a (modified) class", color=V.RED, size=11)
    V.note(ax, 50, 30, "@dataclass is exactly this", color=V.GRAY, size=10)
    V.caption(ax, "A class decorator post-processes the finished class — often enough on its own.")
    V.save(fig, IMG + "m09_07_class_decorator.png")


def d08_when_metaclass():
    fig, ax = V.new_canvas()
    V.title(ax, "Which tool? (prefer the simplest)")
    V.box(ax, 50, 78, 44, 9, "Need to customise class behaviour?", fill=V.BLUE_F, size=11)
    V.box(ax, 20, 56, 26, 12, "per-subclass hook?\n__init_subclass__", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 50, 56, 24, 12, "tweak one class?\nclass decorator", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 80, 56, 26, 12, "deep control of\ncreation? metaclass", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.arrow(ax, 42, 74, 22, 63, color=V.NAVY)
    V.arrow(ax, 50, 74, 50, 63, color=V.NAVY)
    V.arrow(ax, 58, 74, 80, 63, color=V.NAVY)
    V.note(ax, 50, 34, "'If you wonder whether you need metaclasses, you don't.' — Tim Peters", color=V.RED, size=10)
    V.caption(ax, "Reach for __init_subclass__ or a decorator first; metaclasses are the last resort.")
    V.save(fig, IMG + "m09_08_when_metaclass.png")


if __name__ == "__main__":
    for f in [d01_classes_are_objects, d02_type_factory, d03_metaclass_hooks,
              d04_class_creation_flow, d05_registry_pattern, d06_init_subclass,
              d07_class_decorator, d08_when_metaclass]:
        f()
    print("M09 diagrams done.")
