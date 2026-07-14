"""Module 7 — Dunder Methods & the Data Model: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_data_model():
    fig, ax = V.new_canvas()
    V.title(ax, "The data model: syntax -> dunder methods")
    pairs = [
        (72, "len(x)", "x.__len__()"),
        (58, "x + y", "x.__add__(y)"),
        (44, "x[i]", "x.__getitem__(i)"),
        (30, "print(x)", "x.__str__()"),
    ]
    for y, syn, dun in pairs:
        V.box(ax, 26, y, 26, 9, syn, fill=V.BLUE_F, size=12)
        V.arrow(ax, 39, y, 58, y, color=V.NAVY)
        V.box(ax, 76, y, 34, 9, dun, fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.caption(ax, "Implement the dunder and your object plugs into Python's built-in syntax.")
    V.save(fig, IMG + "m07_01_data_model.png")


def d02_repr_vs_str():
    fig, ax = V.new_canvas()
    V.title(ax, "__repr__ vs __str__")
    V.box(ax, 27, 60, 40, 40, "", fill=V.BLUE_F, edge=V.NAVY)
    V.note(ax, 27, 74, "__repr__", color=V.NAVY, bold=True, size=13)
    V.note(ax, 27, 63, "for DEVELOPERS\nunambiguous, debug", size=11)
    V.note(ax, 27, 48, "Point(x=1, y=2)", color=V.GRAY, size=11)
    V.box(ax, 73, 60, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 74, "__str__", color=V.GREEN, bold=True, size=13)
    V.note(ax, 73, 63, "for USERS\nreadable, friendly", size=11)
    V.note(ax, 73, 48, "(1, 2)", color=V.GRAY, size=11)
    V.note(ax, 50, 28, "str() falls back to repr(); ALWAYS define __repr__", color=V.RED, size=11)
    V.caption(ax, "repr = precise for debugging; str = friendly for users; repr is the fallback.")
    V.save(fig, IMG + "m07_02_repr_vs_str.png")


def d03_eq_hash_contract():
    fig, ax = V.new_canvas()
    V.title(ax, "The __eq__ / __hash__ contract")
    V.box(ax, 50, 74, 50, 10, "if a == b  THEN  hash(a) == hash(b)", fill=V.GREEN_F, edge=V.GREEN, size=12)
    V.note(ax, 50, 60, "define __eq__ but NOT __hash__", color=V.NAVY, size=11)
    V.arrow(ax, 50, 56, 50, 48)
    V.box(ax, 50, 42, 44, 9, "object becomes UNHASHABLE", fill=V.RED, tcolor="white", size=11)
    V.note(ax, 50, 28, "no dict keys / set members until you add __hash__", color=V.RED, size=11)
    V.note(ax, 50, 20, "equal objects MUST share a hash; unequal MAY collide", color=V.GRAY, size=10)
    V.caption(ax, "Override __eq__ and you must define __hash__ too (or lose hashability).")
    V.save(fig, IMG + "m07_03_eq_hash_contract.png")


def d04_total_ordering():
    fig, ax = V.new_canvas()
    V.title(ax, "@total_ordering fills in comparison operators")
    V.box(ax, 25, 62, 26, 14, "you write:\n__eq__ + __lt__", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 38, 62, 58, 62, color=V.NAVY)
    V.note(ax, 48, 69, "@total_ordering", color=V.ORANGE, size=9)
    V.box(ax, 78, 62, 32, 14, "get for free:\n<= > >= !=", fill=V.BLUE_F, size=11)
    V.note(ax, 50, 38, "less boilerplate; define the two, derive the rest", color=V.RED, size=11)
    V.caption(ax, "Define __eq__ and one ordering (__lt__); total_ordering derives the others.")
    V.save(fig, IMG + "m07_04_total_ordering.png")


def d05_container_protocol():
    fig, ax = V.new_canvas()
    V.title(ax, "Container protocol")
    rows = [
        (70, "len(c)", "__len__", "how many items"),
        (54, "c[i]", "__getitem__", "read by key/index"),
        (38, "c[i] = v", "__setitem__", "write by key/index"),
        (22, "x in c", "__contains__", "membership test"),
    ]
    for y, syn, dun, desc in rows:
        V.box(ax, 20, y, 20, 10, syn, fill=V.BLUE_F, size=11)
        V.box(ax, 50, y, 26, 10, dun, fill=V.GREEN_F, edge=V.GREEN, size=11)
        V.note(ax, 85, y, desc, size=10)
        V.arrow(ax, 30, y, 37, y, color=V.NAVY)
    V.caption(ax, "Implement these and your object behaves like a list/dict to Python.")
    V.save(fig, IMG + "m07_05_container_protocol.png")


def d06_iterator_protocol():
    fig, ax = V.new_canvas()
    V.title(ax, "Iterator protocol powers the for-loop")
    V.box(ax, 16, 60, 20, 12, "for x in obj", fill=V.BLUE_F, size=11)
    V.arrow(ax, 26, 60, 38, 60, color=V.NAVY)
    V.box(ax, 51, 60, 22, 12, "__iter__()\nreturns iterator", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 62, 60, 74, 60, color=V.NAVY)
    V.box(ax, 87, 60, 20, 12, "__next__()\nyields items", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 87, 54, 87, 44, color=V.RED)
    V.box(ax, 87, 38, 22, 9, "raise StopIteration", fill=V.RED, tcolor="white", size=9)
    V.note(ax, 45, 30, "__next__ returns the next value until it raises StopIteration", color=V.RED, size=10)
    V.caption(ax, "__iter__ hands back an iterator; __next__ produces values then stops.")
    V.save(fig, IMG + "m07_06_iterator_protocol.png")


def d07_context_manager():
    fig, ax = V.new_canvas()
    V.title(ax, "Context manager: with-statement lifecycle")
    V.box(ax, 50, 78, 34, 9, "with open(f) as fh:", fill=V.BLUE_F, size=11)
    V.box(ax, 25, 58, 26, 11, "__enter__()\nacquire (open)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 75, 58, 26, 11, "__exit__()\nrelease (close)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 50, 40, 28, 9, "your code runs", fill="white", edge=V.GRAY, size=10, bold=False)
    V.arrow(ax, 42, 74, 28, 64, color=V.NAVY)
    V.arrow(ax, 30, 53, 45, 44, color=V.NAVY)
    V.arrow(ax, 55, 44, 72, 53, color=V.NAVY)
    V.note(ax, 50, 24, "__exit__ ALWAYS runs — even if the body raises", color=V.RED, size=11)
    V.caption(ax, "with guarantees setup (__enter__) and cleanup (__exit__), exceptions or not.")
    V.save(fig, IMG + "m07_07_context_manager.png")


def d08_callable():
    fig, ax = V.new_canvas()
    V.title(ax, "__call__ makes an instance callable")
    V.box(ax, 25, 60, 26, 14, "adder = Adder(10)\n(an object)", fill=V.BLUE_F, size=10)
    V.arrow(ax, 38, 60, 58, 60, color=V.NAVY)
    V.note(ax, 48, 67, "adder(5)", color=V.ORANGE, size=10, bold=True)
    V.box(ax, 78, 60, 30, 14, "runs __call__(self, 5)\n-> 15", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 36, "the object behaves like a function, but keeps state", color=V.RED, size=11)
    V.note(ax, 50, 26, "used for: decorators, function objects, ML layers", color=V.GRAY, size=10)
    V.caption(ax, "Define __call__ and obj(args) works — a stateful 'function object'.")
    V.save(fig, IMG + "m07_08_callable.png")


if __name__ == "__main__":
    for f in [d01_data_model, d02_repr_vs_str, d03_eq_hash_contract,
              d04_total_ordering, d05_container_protocol, d06_iterator_protocol,
              d07_context_manager, d08_callable]:
        f()
    print("M07 diagrams done.")
