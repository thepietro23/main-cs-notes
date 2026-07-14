"""Module 19 — Anti-patterns, Code Smells & Refactoring: diagram generator."""
import viz_style as V
IMG = "../images/"


def d01_god_object():
    fig, ax = V.new_canvas()
    V.title(ax, "God Object anti-pattern -> decompose")
    V.box(ax, 25, 58, 30, 34, "", fill=V.RED, edge=V.RED)
    V.note(ax, 25, 70, "GodManager", color="white", bold=True, size=11)
    V.note(ax, 25, 58, "does UI + DB +\nauth + email +\nlogging + ...", color="white", size=9)
    V.arrow(ax, 47, 58, 58, 58, color=V.NAVY)
    for i, (y, t) in enumerate([(74, "UserService"), (58, "AuthService"), (42, "MailService")]):
        V.box(ax, 80, y, 26, 10, t, fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 80, 30, "each: one responsibility (SRP)", color=V.GREEN, size=10)
    V.caption(ax, "A god object knows/does everything; split it into focused classes.")
    V.save(fig, IMG + "m19_01_god_object.png")


def d02_smells_list():
    fig, ax = V.new_canvas()
    V.title(ax, "Common code smells")
    rows = [(74, "Long method", "split with Extract Method"),
            (62, "Large class / God object", "Extract Class (SRP)"),
            (50, "Long parameter list", "Introduce Parameter Object"),
            (38, "Primitive obsession", "use a value object / Enum"),
            (26, "Feature envy", "move method to the data it uses"),
            (14, "Duplicated code", "extract + reuse (DRY)")]
    for y, smell, fix in rows:
        V.box(ax, 26, y, 32, 9, smell, fill=V.ORANGE_F, edge=V.ORANGE, size=10)
        V.note(ax, 75, y, "-> " + fix, size=9)
    V.caption(ax, "Smells are hints, not bugs — each has a standard refactoring cure.")
    V.save(fig, IMG + "m19_02_smells_list.png")


def d03_replace_conditional():
    fig, ax = V.new_canvas()
    V.title(ax, "Replace conditional with polymorphism")
    V.box(ax, 25, 58, 32, 36, "", fill=V.RED, edge=V.RED)
    V.note(ax, 25, 70, "SMELL", color="white", bold=True, size=11)
    V.note(ax, 25, 58, "if t=='dog': bark\nelif t=='cat': meow\nelif ...", color="white", size=9)
    V.arrow(ax, 43, 58, 56, 58, color=V.NAVY)
    V.box(ax, 76, 70, 28, 9, "Animal.speak()", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 70, 52, 18, 8, "Dog", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 90, 52, 18, 8, "Cat", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 70, 56, 74, 65, color=V.NAVY)
    V.arrow(ax, 90, 56, 82, 65, color=V.NAVY)
    V.note(ax, 50, 26, "each type owns its behaviour; add types without editing (OCP)", color=V.RED, size=9)
    V.caption(ax, "Turn a type-switch ladder into subclasses overriding one method.")
    V.save(fig, IMG + "m19_03_replace_conditional.png")


def d04_deep_inheritance():
    fig, ax = V.new_canvas()
    V.title(ax, "Deep inheritance (yo-yo) -> composition")
    for i, (y, t) in enumerate([(78, "A"), (64, "B(A)"), (50, "C(B)"), (36, "D(C)")]):
        V.box(ax, 25, y, 16, 8, t, fill=V.RED if i == 3 else V.ORANGE_F,
              edge=V.RED if i == 3 else V.ORANGE, tcolor="white" if i == 3 else V.BLACK, size=9)
        if i < 3:
            V.arrow(ax, 25, [78, 64, 50, 36][i + 1] + 4, 25, y - 4, color=V.NAVY)
    V.note(ax, 25, 24, "fragile, hard to follow", color=V.RED, size=9)
    V.arrow(ax, 40, 55, 52, 55, color=V.NAVY)
    V.box(ax, 74, 60, 30, 12, "D has-a EngineA,\nEngineB (compose)", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.note(ax, 74, 42, "flat, swappable parts", color=V.GREEN, size=9)
    V.caption(ax, "Replace tall inheritance chains with composition of small parts.")
    V.save(fig, IMG + "m19_04_deep_inheritance.png")


def d05_extract_class():
    fig, ax = V.new_canvas()
    V.title(ax, "Extract Class: split a bloated class")
    V.box(ax, 25, 58, 30, 34, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 25, 70, "Person", color=V.ORANGE, bold=True, size=11)
    V.note(ax, 25, 58, "name, email\nstreet, city, zip\n(address mixed in)", size=9)
    V.arrow(ax, 43, 58, 56, 58, color=V.NAVY)
    V.box(ax, 76, 68, 26, 12, "Person\nname, email", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 76, 46, 26, 12, "Address\nstreet, city, zip", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 76, 62, 76, 52, color=V.NAVY, style="-|>")
    V.note(ax, 50, 26, "cohesive data -> its own class (Person HAS-A Address)", color=V.RED, size=9)
    V.caption(ax, "Extract Class pulls a cohesive cluster of fields/methods into its own type.")
    V.save(fig, IMG + "m19_05_extract_class.png")


def d06_primitive_obsession():
    fig, ax = V.new_canvas()
    V.title(ax, "Primitive obsession -> value object")
    V.box(ax, 25, 58, 32, 30, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 25, 68, "amount: float\ncurrency: str", size=10)
    V.note(ax, 25, 52, "scattered, unchecked", color=V.RED, size=9)
    V.arrow(ax, 43, 58, 56, 58, color=V.NAVY)
    V.box(ax, 78, 58, 32, 20, "Money(amount, currency)\n+ validation + add()", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.note(ax, 50, 30, "wrap related primitives in a type with behaviour + rules", color=V.RED, size=10)
    V.caption(ax, "Replace loose primitives with a small value object that guards its rules.")
    V.save(fig, IMG + "m19_06_primitive_obsession.png")


def d07_refactoring_moves():
    fig, ax = V.new_canvas()
    V.title(ax, "Key refactoring moves")
    rows = [(74, "Extract Method / Class", "break up long code"),
            (60, "Replace conditional w/ polymorphism", "kill type ladders"),
            (46, "Introduce Parameter Object", "bundle long arg lists"),
            (32, "Replace inheritance w/ delegation", "prefer composition"),
            (18, "Rename / Inline", "clarity")]
    for y, name, why in rows:
        V.box(ax, 33, y, 44, 9, name, fill=V.BLUE_F, size=9)
        V.note(ax, 82, y, why, size=9)
    V.caption(ax, "Refactor in small, behaviour-preserving steps — tests stay green throughout.")
    V.save(fig, IMG + "m19_07_refactoring_moves.png")


def d08_refactor_cycle():
    fig, ax = V.new_canvas()
    V.title(ax, "Safe refactoring: keep tests green")
    V.box(ax, 20, 60, 20, 12, "tests\npass", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 30, 60, 44, 60, color=V.NAVY)
    V.box(ax, 55, 60, 22, 12, "small change\n(behaviour-\npreserving)", fill=V.BLUE_F, size=9)
    V.arrow(ax, 66, 60, 80, 60, color=V.NAVY)
    V.box(ax, 90, 60, 16, 12, "re-run\ntests", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 90, 54, 20, 54, color=V.GRAY, dashed=True)
    V.note(ax, 50, 44, "repeat", color=V.GRAY, size=9)
    V.note(ax, 50, 30, "refactoring changes STRUCTURE, not BEHAVIOUR", color=V.RED, size=11)
    V.caption(ax, "Refactor in tiny steps with tests green — never mix refactor + new features.")
    V.save(fig, IMG + "m19_08_refactor_cycle.png")


if __name__ == "__main__":
    for f in [d01_god_object, d02_smells_list, d03_replace_conditional,
              d04_deep_inheritance, d05_extract_class, d06_primitive_obsession,
              d07_refactoring_moves, d08_refactor_cycle]:
        f()
    print("M19 diagrams done.")
