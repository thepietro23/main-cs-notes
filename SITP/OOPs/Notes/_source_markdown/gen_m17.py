"""Module 17 — UML & OOAD: diagram generator."""
import viz_style as V
from matplotlib.patches import Polygon
IMG = "../images/"


def _tri(ax, x, y, up=True, fill="white", edge=V.NAVY):
    if up:
        pts = [(x, y + 3), (x - 3, y - 2), (x + 3, y - 2)]
    else:
        pts = [(x - 3, y + 2), (x + 3, y + 2), (x, y - 3)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, linewidth=2))


def _diamond(ax, x, y, fill="white", edge=V.NAVY):
    pts = [(x, y + 3), (x + 4, y), (x, y - 3), (x - 4, y)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, linewidth=2))


def d01_class_box():
    fig, ax = V.new_canvas()
    V.title(ax, "UML class box notation")
    ax.add_patch(V.plt.Rectangle((35, 22), 30, 56, fill=True, facecolor=V.BLUE_F, edgecolor=V.NAVY, linewidth=2))
    ax.plot([35, 65], [66, 66], color=V.NAVY, linewidth=2)
    ax.plot([35, 65], [46, 46], color=V.NAVY, linewidth=2)
    V.note(ax, 50, 72, "BankAccount", bold=True, size=13)
    V.note(ax, 50, 60, "- balance: float", size=10)
    V.note(ax, 50, 54, "+ owner: str", size=10)
    V.note(ax, 50, 40, "+ deposit(amt): None", size=10)
    V.note(ax, 50, 34, "# _validate(): bool", size=10)
    V.note(ax, 78, 72, "name", color=V.GRAY, size=9, ha="left")
    V.note(ax, 78, 56, "attributes", color=V.GRAY, size=9, ha="left")
    V.note(ax, 78, 37, "methods", color=V.GRAY, size=9, ha="left")
    V.note(ax, 20, 40, "+ public\n- private\n# protected", color=V.RED, size=10, ha="left")
    V.caption(ax, "Three compartments: class name, attributes, methods; +/-/# = visibility.")
    V.save(fig, IMG + "m17_01_class_box.png")


def d02_relationships():
    fig, ax = V.new_canvas()
    V.title(ax, "The six UML class relationships")
    rows = [
        (76, "Association", "uses / knows", "plain line"),
        (64, "Aggregation", "has-a (weak)", "hollow diamond"),
        (52, "Composition", "owns-a (strong)", "filled diamond"),
        (40, "Inheritance", "is-a", "hollow triangle"),
        (28, "Realization", "implements interface", "dashed + triangle"),
        (16, "Dependency", "temporarily uses", "dashed arrow"),
    ]
    for y, name, mean, sym in rows:
        V.note(ax, 22, y, name, bold=True, color=V.NAVY, size=11, ha="center")
        V.note(ax, 55, y, mean, size=10, ha="center")
        V.note(ax, 85, y, sym, color=V.GRAY, size=9, ha="center")
    V.caption(ax, "From loosest (dependency) to strongest ownership (composition) + inheritance.")
    V.save(fig, IMG + "m17_02_relationships.png")


def d03_inheritance_realization():
    fig, ax = V.new_canvas()
    V.title(ax, "Generalization (is-a) vs Realization (implements)")
    V.box(ax, 27, 74, 22, 9, "Animal", fill=V.BLUE_F, size=11)
    V.box(ax, 27, 44, 22, 9, "Dog", fill=V.GREEN_F, edge=V.GREEN, size=11)
    ax.plot([27, 27], [49, 66], color=V.NAVY, linewidth=2)
    _tri(ax, 27, 68, up=True)
    V.note(ax, 27, 32, "solid line + hollow\ntriangle = inherits", color=V.GRAY, size=9)
    V.box(ax, 73, 74, 24, 9, "<<Drawable>>", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 73, 44, 22, 9, "Circle", fill=V.GREEN_F, edge=V.GREEN, size=11)
    ax.plot([73, 73], [49, 66], color=V.NAVY, linewidth=2, linestyle="--")
    _tri(ax, 73, 68, up=True)
    V.note(ax, 73, 32, "DASHED line + hollow\ntriangle = implements", color=V.GRAY, size=9)
    V.caption(ax, "Solid+triangle = inherit a class; dashed+triangle = realise an interface.")
    V.save(fig, IMG + "m17_03_inheritance_realization.png")


def d04_agg_comp():
    fig, ax = V.new_canvas()
    V.title(ax, "Aggregation vs Composition notation")
    V.box(ax, 22, 60, 20, 10, "Team", fill=V.BLUE_F, size=11)
    V.box(ax, 22, 34, 20, 10, "Player", fill=V.GREEN_F, edge=V.GREEN, size=10)
    ax.plot([22, 22], [39, 54], color=V.NAVY, linewidth=2)
    _diamond(ax, 22, 57, fill="white")
    V.note(ax, 22, 22, "hollow diamond\n(aggregation)", color=V.ORANGE, size=9)
    V.box(ax, 74, 60, 20, 10, "House", fill=V.BLUE_F, size=11)
    V.box(ax, 74, 34, 20, 10, "Room", fill=V.GREEN_F, edge=V.GREEN, size=10)
    ax.plot([74, 74], [39, 54], color=V.NAVY, linewidth=2)
    _diamond(ax, 74, 57, fill=V.NAVY)
    V.note(ax, 74, 22, "filled diamond\n(composition)", color=V.GREEN, size=9)
    V.caption(ax, "Diamond sits on the WHOLE: hollow = shared parts; filled = owned parts.")
    V.save(fig, IMG + "m17_04_agg_comp.png")


def d05_multiplicity():
    fig, ax = V.new_canvas()
    V.title(ax, "Multiplicity — how many on each end")
    V.box(ax, 22, 58, 20, 10, "Order", fill=V.BLUE_F, size=11)
    V.box(ax, 78, 58, 20, 10, "LineItem", fill=V.GREEN_F, edge=V.GREEN, size=10)
    ax.plot([32, 68], [58, 58], color=V.NAVY, linewidth=2)
    V.note(ax, 36, 63, "1", color=V.RED, size=11, bold=True)
    V.note(ax, 64, 63, "1..*", color=V.RED, size=11, bold=True)
    V.note(ax, 50, 42, "one Order has one-or-more LineItems", color=V.GRAY, size=10)
    rows = ["1  exactly one", "0..1  optional (zero or one)", "*  many (zero or more)", "1..*  one or more"]
    for i, t in enumerate(rows):
        V.note(ax, 30, 32 - i * 6, t, size=10, ha="left")
    V.caption(ax, "Multiplicity labels each association end: 1, 0..1, *, 1..* ...")
    V.save(fig, IMG + "m17_05_multiplicity.png")


def d06_dependency_assoc():
    fig, ax = V.new_canvas()
    V.title(ax, "Dependency vs Association")
    V.box(ax, 22, 64, 20, 10, "Order", fill=V.BLUE_F, size=11)
    V.box(ax, 74, 64, 22, 10, "PriceService", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 32, 64, 63, 64, color=V.NAVY, dashed=True)
    V.note(ax, 48, 70, "uses in a method", color=V.GRAY, size=9)
    V.note(ax, 48, 54, "DEPENDENCY (dashed): transient use, e.g. a parameter", color=V.RED, size=9)
    V.box(ax, 22, 34, 20, 10, "Customer", fill=V.BLUE_F, size=10)
    V.box(ax, 74, 34, 20, 10, "Address", fill=V.GREEN_F, edge=V.GREEN, size=10)
    ax.plot([32, 64], [34, 34], color=V.NAVY, linewidth=2)
    V.note(ax, 48, 24, "ASSOCIATION (solid): a lasting link, e.g. a stored field", color=V.RED, size=9)
    V.caption(ax, "Dependency = brief use (dashed); Association = a persistent structural link (solid).")
    V.save(fig, IMG + "m17_06_dependency_assoc.png")


def d07_reqs_to_model():
    fig, ax = V.new_canvas()
    V.title(ax, "From requirements to a class model")
    V.box(ax, 26, 66, 40, 16, "'A member borrows\na book from the library'", fill=V.BLUE_F, size=10)
    V.arrow(ax, 47, 66, 60, 66, color=V.NAVY)
    V.box(ax, 80, 74, 30, 8, "nouns -> Member, Book, Library", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 80, 60, 30, 8, "verb 'borrows' -> method / link", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.note(ax, 50, 40, "nouns = classes/attributes ; verbs = methods/associations", color=V.RED, size=11)
    V.note(ax, 50, 30, "then assign responsibilities and draw relationships", color=V.GRAY, size=10)
    V.caption(ax, "OOAD: extract nouns as classes and verbs as behaviour, then model links.")
    V.save(fig, IMG + "m17_07_reqs_to_model.png")


def d08_full_example():
    fig, ax = V.new_canvas()
    V.title(ax, "A small class diagram (library)")
    V.box(ax, 50, 78, 22, 9, "Library", fill=V.BLUE_F, size=10)
    V.box(ax, 22, 52, 20, 9, "Book", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 52, 20, 9, "Member", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 28, 22, 9, "Loan", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    # composition: library owns books
    ax.plot([44, 30], [74, 57], color=V.NAVY, linewidth=2)
    _diamond(ax, 46, 75, fill=V.NAVY)
    # association library-member
    ax.plot([56, 72], [74, 57], color=V.NAVY, linewidth=2)
    # loan links book & member
    ax.plot([30, 46], [47, 33], color=V.GRAY, linewidth=1.5)
    ax.plot([70, 54], [47, 33], color=V.GRAY, linewidth=1.5)
    V.note(ax, 30, 40, "1..*", color=V.RED, size=9)
    V.note(ax, 70, 40, "1", color=V.RED, size=9)
    V.note(ax, 50, 18, "Loan associates a Book with a Member for a period", color=V.GRAY, size=9)
    V.caption(ax, "Library composes Books, links Members; a Loan connects Book and Member.")
    V.save(fig, IMG + "m17_08_full_example.png")


if __name__ == "__main__":
    for f in [d01_class_box, d02_relationships, d03_inheritance_realization,
              d04_agg_comp, d05_multiplicity, d06_dependency_assoc,
              d07_reqs_to_model, d08_full_example]:
        f()
    print("M17 diagrams done.")
