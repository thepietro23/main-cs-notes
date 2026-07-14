"""Module 5 — Inheritance & Composition: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_is_a():
    fig, ax = V.new_canvas()
    V.title(ax, "Inheritance = an 'is-a' relationship")
    V.box(ax, 50, 74, 30, 12, "Animal\neat(), sleep()", fill=V.BLUE_F, size=12)
    V.box(ax, 25, 42, 26, 14, "Dog\n+ bark()", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 75, 42, 26, 14, "Cat\n+ meow()", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 33, 49, 44, 68, color=V.NAVY, style="-|>")
    V.arrow(ax, 67, 49, 56, 68, color=V.NAVY, style="-|>")
    V.note(ax, 50, 26, "Dog IS-A Animal -> inherits eat()/sleep(), adds bark()", color=V.RED, size=11)
    V.caption(ax, "A subclass reuses the parent's members and adds/overrides its own.")
    V.save(fig, IMG + "m05_01_is_a.png")


def d02_override_super():
    fig, ax = V.new_canvas()
    V.title(ax, "Overriding + super(): extend, don't replace")
    V.box(ax, 25, 70, 30, 14, "Employee.raise_pay()\nbase logic", fill=V.BLUE_F, size=11)
    V.box(ax, 25, 40, 32, 16, "Manager.raise_pay()\nsuper().raise_pay()\n+ bonus", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 25, 48, 25, 63, color=V.ORANGE, style="-|>")
    V.note(ax, 55, 55, "super() calls the\nparent version,\nthen adds to it", color=V.ORANGE, size=11, ha="left")
    V.caption(ax, "Override to change behaviour; call super() to reuse the parent's part.")
    V.save(fig, IMG + "m05_02_override_super.png")


def d03_inheritance_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Types of inheritance")
    # single
    V.note(ax, 15, 82, "Single", color=V.NAVY, bold=True, size=10)
    V.box(ax, 15, 70, 12, 7, "A", fill=V.BLUE_F, size=10)
    V.box(ax, 15, 56, 12, 7, "B", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 15, 60, 15, 66, color=V.NAVY)
    # multilevel
    V.note(ax, 40, 82, "Multilevel", color=V.NAVY, bold=True, size=10)
    V.box(ax, 40, 72, 12, 7, "A", fill=V.BLUE_F, size=10)
    V.box(ax, 40, 60, 12, 7, "B", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 40, 48, 12, 7, "C", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 40, 51, 40, 56, color=V.NAVY)
    V.arrow(ax, 40, 63, 40, 68, color=V.NAVY)
    # hierarchical
    V.note(ax, 65, 82, "Hierarchical", color=V.NAVY, bold=True, size=10)
    V.box(ax, 65, 72, 12, 7, "A", fill=V.BLUE_F, size=10)
    V.box(ax, 58, 56, 12, 7, "B", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 56, 12, 7, "C", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 60, 60, 64, 68, color=V.NAVY)
    V.arrow(ax, 70, 60, 66, 68, color=V.NAVY)
    # multiple
    V.note(ax, 88, 82, "Multiple", color=V.NAVY, bold=True, size=10)
    V.box(ax, 82, 72, 12, 7, "A", fill=V.BLUE_F, size=10)
    V.box(ax, 94, 72, 12, 7, "B", fill=V.BLUE_F, size=10)
    V.box(ax, 88, 56, 12, 7, "C", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 84, 60, 87, 68, color=V.NAVY)
    V.arrow(ax, 92, 60, 89, 68, color=V.NAVY)
    V.caption(ax, "Python supports all forms, including multiple inheritance (two+ parents).")
    V.save(fig, IMG + "m05_03_inheritance_types.png")


def d04_mro_diamond():
    fig, ax = V.new_canvas()
    V.title(ax, "The diamond problem")
    V.box(ax, 50, 78, 16, 9, "A", fill=V.BLUE_F, size=11)
    V.box(ax, 28, 56, 16, 9, "B", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 72, 56, 16, 9, "C", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 50, 34, 16, 9, "D", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.arrow(ax, 34, 60, 46, 74, color=V.NAVY)
    V.arrow(ax, 66, 60, 54, 74, color=V.NAVY)
    V.arrow(ax, 46, 38, 34, 52, color=V.NAVY)
    V.arrow(ax, 54, 38, 66, 52, color=V.NAVY)
    V.note(ax, 50, 20, "D inherits A twice (via B and C). Which A.method() wins?", color=V.RED, size=11)
    V.caption(ax, "Multiple paths to a shared ancestor -> Python resolves it with the MRO.")
    V.save(fig, IMG + "m05_04_mro_diamond.png")


def d05_c3():
    fig, ax = V.new_canvas()
    V.title(ax, "C3 linearisation gives one clear order (MRO)")
    order = ["D", "B", "C", "A", "object"]
    xs = [12, 30, 48, 66, 86]
    for x, name in zip(xs, order):
        f = V.ORANGE_F if name == "D" else (V.BLUE_F if name in ("A", "object") else V.GREEN_F)
        e = V.ORANGE if name == "D" else (V.NAVY if name in ("A", "object") else V.GREEN)
        V.box(ax, x, 58, 15, 10, name, fill=f, edge=e, size=11)
    for i in range(len(xs) - 1):
        V.arrow(ax, xs[i] + 8, 58, xs[i + 1] - 8, 58, color=V.NAVY)
    V.note(ax, 50, 40, "D.mro() = [D, B, C, A, object]", color=V.NAVY, bold=True, size=12)
    V.note(ax, 50, 30, "super() walks THIS list, left to right — each class once", color=V.RED, size=11)
    V.caption(ax, "MRO: depth-first, left-to-right, keeping each class after its subclasses.")
    V.save(fig, IMG + "m05_05_c3.png")


def d06_mixin():
    fig, ax = V.new_canvas()
    V.title(ax, "Mixins: bolt on a capability")
    V.box(ax, 25, 72, 28, 10, "JSONMixin\nto_json()", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 72, 72, 24, 10, "User\n(main class)", fill=V.BLUE_F, size=11)
    V.box(ax, 50, 44, 34, 12, "class User(JSONMixin):\n gets to_json() free", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 33, 67, 45, 51, color=V.NAVY)
    V.arrow(ax, 70, 67, 56, 51, color=V.NAVY)
    V.note(ax, 50, 28, "Mixin = small class adding ONE ability; not used alone", color=V.RED, size=11)
    V.caption(ax, "A mixin injects reusable behaviour into many unrelated classes.")
    V.save(fig, IMG + "m05_06_mixin.png")


def d07_composition_vs_inheritance():
    fig, ax = V.new_canvas()
    V.title(ax, "Composition (has-a) vs Inheritance (is-a)")
    V.note(ax, 27, 82, "INHERITANCE (is-a)", color=V.ORANGE, bold=True, size=11)
    V.box(ax, 27, 66, 22, 9, "Vehicle", fill=V.BLUE_F, size=11)
    V.box(ax, 27, 50, 22, 9, "Car(Vehicle)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 27, 54, 27, 61, color=V.NAVY, style="-|>")
    V.note(ax, 27, 38, "Car IS-A Vehicle", color=V.GRAY, size=10)
    ax.plot([50, 50], [30, 80], color=V.GRAY, linewidth=1.2, linestyle="--")
    V.note(ax, 74, 82, "COMPOSITION (has-a)", color=V.GREEN, bold=True, size=11)
    V.box(ax, 74, 66, 22, 9, "Car", fill=V.BLUE_F, size=11)
    V.box(ax, 74, 50, 22, 9, "Engine", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 74, 61, 74, 55, color=V.GREEN, style="-|>")
    V.note(ax, 74, 38, "Car HAS-A Engine", color=V.GRAY, size=10)
    V.caption(ax, "Prefer composition (flexible, swappable parts) over deep inheritance trees.")
    V.save(fig, IMG + "m05_07_composition_vs_inheritance.png")


def d08_aggregation_composition():
    fig, ax = V.new_canvas()
    V.title(ax, "Aggregation vs Composition (part lifecycles)")
    V.note(ax, 27, 82, "AGGREGATION", color=V.ORANGE, bold=True, size=11)
    V.box(ax, 27, 64, 20, 10, "Team", fill=V.BLUE_F, size=11)
    V.box(ax, 27, 46, 22, 10, "Player", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 27, 51, 27, 59, color=V.ORANGE, style="-|>", dashed=True)
    V.note(ax, 27, 33, "player OUTLIVES team\n(shared, independent)", color=V.GRAY, size=10)
    ax.plot([50, 50], [28, 80], color=V.GRAY, linewidth=1.2, linestyle="--")
    V.note(ax, 74, 82, "COMPOSITION", color=V.GREEN, bold=True, size=11)
    V.box(ax, 74, 64, 20, 10, "House", fill=V.BLUE_F, size=11)
    V.box(ax, 74, 46, 22, 10, "Room", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 74, 51, 74, 59, color=V.GREEN, style="-|>")
    V.note(ax, 74, 33, "room DIES with house\n(owned, exclusive)", color=V.RED, size=10)
    V.caption(ax, "Aggregation = parts live independently; Composition = parts owned & die together.")
    V.save(fig, IMG + "m05_08_aggregation_composition.png")


if __name__ == "__main__":
    for f in [d01_is_a, d02_override_super, d03_inheritance_types, d04_mro_diamond,
              d05_c3, d06_mixin, d07_composition_vs_inheritance,
              d08_aggregation_composition]:
        f()
    print("M05 diagrams done.")
