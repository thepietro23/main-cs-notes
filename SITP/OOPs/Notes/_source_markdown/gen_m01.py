"""Module 1 — Introduction to OOP: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_paradigms():
    fig, ax = V.new_canvas()
    V.title(ax, "Programming Paradigms — where OOP sits")
    V.box(ax, 50, 82, 34, 11, "Programming\nParadigms", fill=V.BLUE_F, size=13)
    # two branches
    V.box(ax, 26, 60, 30, 11, "Imperative\n(HOW to do it)", fill=V.ORANGE_F, edge=V.ORANGE, size=12)
    V.box(ax, 74, 60, 30, 11, "Declarative\n(WHAT you want)", fill=V.GREEN_F, edge=V.GREEN, size=12)
    V.arrow(ax, 44, 77, 30, 66)
    V.arrow(ax, 56, 77, 70, 66)
    # leaves
    V.box(ax, 15, 34, 22, 12, "Procedural\n(C, Pascal)", fill=V.BLUE_F, size=11)
    V.box(ax, 40, 34, 22, 12, "Object-\nOriented\n(Python, Java)", fill=V.BLUE_F, edge=V.RED, tcolor=V.RED, size=11)
    V.box(ax, 63, 34, 20, 12, "Functional\n(Haskell)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 85, 34, 18, 12, "Logic\n(Prolog)", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 22, 54, 16, 41)
    V.arrow(ax, 30, 54, 39, 41)
    V.arrow(ax, 70, 54, 63, 41)
    V.arrow(ax, 78, 54, 85, 41)
    V.caption(ax, "OOP is an imperative paradigm: you bundle data with the code that acts on it.")
    V.save(fig, IMG + "m01_01_paradigms.png")


def d02_procedural_vs_oop():
    fig, ax = V.new_canvas()
    V.title(ax, "Procedural vs Object-Oriented — the core shift")
    # left: procedural
    V.note(ax, 26, 84, "PROCEDURAL", color=V.ORANGE, bold=True, size=13)
    V.box(ax, 15, 66, 16, 9, "data1", fill=V.BLUE_F, size=11)
    V.box(ax, 37, 66, 16, 9, "data2", fill=V.BLUE_F, size=11)
    V.box(ax, 15, 50, 16, 9, "func_a()", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 37, 50, 16, 9, "func_b()", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 18, 55, 18, 61, dashed=True)
    V.arrow(ax, 34, 55, 34, 61, dashed=True)
    V.arrow(ax, 22, 52, 30, 63, dashed=True, color=V.GRAY)
    V.note(ax, 26, 34, "Data & functions\nlive apart; anyone\ncan touch the data", color=V.RED, size=11)
    # divider
    ax.plot([50, 50], [22, 78], color=V.GRAY, linewidth=1.5, linestyle="--")
    # right: OOP
    V.note(ax, 74, 84, "OBJECT-ORIENTED", color=V.GREEN, bold=True, size=13)
    V.box(ax, 74, 58, 34, 30, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 74, 70, "Object", color=V.GREEN, bold=True, size=12)
    V.box(ax, 66, 58, 13, 8, "state", fill=V.BLUE_F, size=10)
    V.box(ax, 82, 58, 13, 8, "state", fill=V.BLUE_F, size=10)
    V.box(ax, 74, 48, 24, 8, "methods()", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.note(ax, 74, 34, "Data + behavior\nbundled; access is\ncontrolled", color=V.GREEN, size=11)
    V.caption(ax, "OOP bundles state and behaviour into one unit and guards the data.")
    V.save(fig, IMG + "m01_02_procedural_vs_oop.png")


def d03_class_vs_object():
    fig, ax = V.new_canvas()
    V.title(ax, "Class vs Object — blueprint vs the real thing")
    V.box(ax, 22, 60, 30, 34, "", fill=V.BLUE_F)
    V.note(ax, 22, 74, "class Car", color=V.NAVY, bold=True, size=13)
    V.note(ax, 22, 64, "- brand\n- speed", size=11)
    V.note(ax, 22, 52, "+ drive()\n+ brake()", size=11)
    V.note(ax, 22, 41, "BLUEPRINT", color=V.RED, bold=True, size=11)
    # one "instantiate" arrow, then well-spaced instances
    V.arrow(ax, 37, 60, 52, 60, color=V.GREEN)
    V.note(ax, 46, 66, "Car()", color=V.GREEN, size=10, bold=True)
    for x, txt in [(61, "car1\nTesla, 0"), (77, "car2\nBMW, 0"), (93, "car3\nAudi, 0")]:
        V.box(ax, x, 60, 12, 16, txt, fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 77, 45, "OBJECTS (instances) — each has its own data", color=V.GREEN, bold=True, size=10)
    V.caption(ax, "One class (blueprint) can create many independent objects (instances).")
    V.save(fig, IMG + "m01_03_class_vs_object.png")


def d04_object_anatomy():
    fig, ax = V.new_canvas()
    V.title(ax, "Anatomy of an Object — identity, state, behaviour")
    V.box(ax, 50, 55, 44, 46, "", fill=V.BLUE_F)
    V.note(ax, 50, 73, "a BankAccount object", color=V.NAVY, bold=True, size=13)
    V.box(ax, 50, 62, 30, 8, "IDENTITY: id 0x7f3a", fill="white", edge=V.GRAY, size=11, bold=False)
    V.box(ax, 50, 51, 30, 8, "STATE: balance = 500", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 50, 40, 30, 8, "BEHAVIOUR: deposit()", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 88, 62, "who", color=V.GRAY, size=10)
    V.note(ax, 88, 51, "what it\nknows", color=V.ORANGE, size=10)
    V.note(ax, 88, 40, "what it\ncan do", color=V.GREEN, size=10)
    V.caption(ax, "Every object = a unique identity + its own state + shared behaviour.")
    V.save(fig, IMG + "m01_04_object_anatomy.png")


def d05_four_pillars():
    fig, ax = V.new_canvas()
    V.title(ax, "The Four Pillars of OOP")
    V.box(ax, 50, 78, 30, 10, "OOP", fill=V.NAVY, tcolor="white", size=14)
    pillars = [
        (18, "Encapsulation", "bundle + hide\ndata", V.BLUE_F, V.NAVY),
        (39, "Abstraction", "show essentials,\nhide detail", V.ORANGE_F, V.ORANGE),
        (61, "Inheritance", "reuse via\nis-a", V.GREEN_F, V.GREEN),
        (82, "Polymorphism", "one name,\nmany forms", V.BLUE_F, V.NAVY),
    ]
    for x, name, sub, fill, edge in pillars:
        V.box(ax, x, 48, 19, 30, "", fill=fill, edge=edge)
        V.note(ax, x, 57, name, color=edge, bold=True, size=11)
        V.note(ax, x, 44, sub, size=10)
        V.arrow(ax, 50, 73, x, 64, color=edge)
    V.caption(ax, "Master these four and you understand 90% of OOP interview questions.")
    V.save(fig, IMG + "m01_05_four_pillars.png")


def d06_real_world_model():
    fig, ax = V.new_canvas()
    V.title(ax, "Modelling the real world as objects")
    V.note(ax, 22, 82, "REAL WORLD", color=V.GRAY, bold=True, size=12)
    V.circle(ax, 22, 60, 12, "Car", fill=V.ORANGE_F, edge=V.ORANGE, size=13)
    V.note(ax, 22, 40, "a physical car:\nbrand, colour,\ncan drive", size=11)
    V.arrow(ax, 37, 60, 55, 60, color=V.NAVY)
    V.note(ax, 46, 66, "model as", color=V.NAVY, size=10)
    V.note(ax, 80, 82, "CODE", color=V.GREEN, bold=True, size=12)
    V.box(ax, 80, 58, 36, 36, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 80, 72, "class Car:", color=V.NAVY, bold=True, size=12)
    V.note(ax, 80, 62, "brand, colour", color=V.ORANGE, size=11)
    V.note(ax, 80, 54, "= attributes (nouns)", color=V.GRAY, size=9)
    V.note(ax, 80, 47, "drive(), paint()", color=V.GREEN, size=11)
    V.note(ax, 80, 42, "= methods (verbs)", color=V.GRAY, size=9)
    V.caption(ax, "Nouns become attributes; verbs become methods. That is how you find classes.")
    V.save(fig, IMG + "m01_06_real_world_model.png")


def d07_when_oop_flowchart():
    fig, ax = V.new_canvas()
    V.title(ax, "When should you reach for OOP?")
    V.box(ax, 50, 80, 46, 10, "Does the problem have 'things' with\nstate + behaviour that repeats?", fill=V.BLUE_F, size=11)
    # decision 1
    V.box(ax, 30, 58, 26, 10, "Many entities\ninteracting?", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 76, 58, 30, 10, "Simple script /\none-off transform?", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 75, 30, 64)
    V.arrow(ax, 58, 75, 74, 64)
    V.note(ax, 33, 70, "yes", color=V.GREEN, size=10, bold=True)
    V.note(ax, 68, 70, "no", color=V.RED, size=10, bold=True)
    V.box(ax, 30, 34, 30, 12, "USE OOP\nclasses + objects", fill=V.GREEN_F, edge=V.GREEN, tcolor=V.GREEN, size=11)
    V.box(ax, 76, 34, 30, 12, "Functions /\nprocedural is fine", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 30, 53, 30, 40, color=V.GREEN)
    V.arrow(ax, 76, 53, 76, 40, color=V.ORANGE)
    V.caption(ax, "OOP shines when you have many stateful entities; not every script needs a class.")
    V.save(fig, IMG + "m01_07_when_oop_flowchart.png")


def d08_message_passing():
    fig, ax = V.new_canvas()
    V.title(ax, "Objects collaborate by sending messages")
    V.box(ax, 20, 55, 24, 18, "order\nobject", fill=V.BLUE_F, size=12)
    V.box(ax, 80, 55, 24, 18, "payment\nobject", fill=V.GREEN_F, edge=V.GREEN, size=12)
    V.arrow(ax, 32, 60, 68, 60, color=V.NAVY)
    V.note(ax, 50, 66, "charge(amount)", color=V.NAVY, bold=True, size=11)
    V.arrow(ax, 68, 50, 32, 50, color=V.GREEN, style="-|>")
    V.note(ax, 50, 44, "returns receipt", color=V.GREEN, size=11)
    V.note(ax, 50, 26, "The order does NOT touch payment's internals —\nit just calls a method (sends a message).", color=V.RED, size=11)
    V.caption(ax, "Calling obj.method(args) IS message passing — the heart of OOP collaboration.")
    V.save(fig, IMG + "m01_08_message_passing.png")


if __name__ == "__main__":
    d01_paradigms()
    d02_procedural_vs_oop()
    d03_class_vs_object()
    d04_object_anatomy()
    d05_four_pillars()
    d06_real_world_model()
    d07_when_oop_flowchart()
    d08_message_passing()
    print("M01 diagrams done.")
