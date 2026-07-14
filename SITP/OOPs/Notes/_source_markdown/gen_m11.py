"""Module 11 — Object Typing & Protocols: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_why_hints():
    fig, ax = V.new_canvas()
    V.title(ax, "Type hints: help tools, NOT enforced at run time")
    V.box(ax, 50, 76, 34, 9, "def area(r: float) -> float:", fill=V.BLUE_F, size=11)
    V.box(ax, 20, 52, 22, 12, "IDE\nautocomplete", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 52, 22, 12, "mypy\nstatic check", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 80, 52, 22, 12, "docs /\nreadability", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 71, 22, 59, color=V.NAVY)
    V.arrow(ax, 50, 71, 50, 59, color=V.NAVY)
    V.arrow(ax, 58, 71, 80, 59, color=V.NAVY)
    V.note(ax, 50, 32, "area('x') still RUNS — Python ignores hints at run time", color=V.RED, size=11)
    V.caption(ax, "Hints are for humans and tools; the interpreter does not enforce them.")
    V.save(fig, IMG + "m11_01_why_hints.png")


def d02_annotate_class():
    fig, ax = V.new_canvas()
    V.title(ax, "Annotating a class")
    V.box(ax, 50, 58, 60, 50, "", fill=V.BLUE_F, edge=V.NAVY)
    V.note(ax, 50, 77, "class Account:", color=V.NAVY, bold=True, size=12)
    V.box(ax, 50, 66, 48, 8, "owner: str", fill="white", edge=V.GRAY, size=11, bold=False)
    V.box(ax, 50, 55, 48, 8, "balance: float = 0.0", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 50, 44, 48, 8, "def deposit(self, amt: float) -> None", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 50, 26, "annotate attributes, parameters, and return types", color=V.RED, size=11)
    V.caption(ax, "Type each attribute, parameter, and return value for clarity and checking.")
    V.save(fig, IMG + "m11_02_annotate_class.png")


def d03_generic():
    fig, ax = V.new_canvas()
    V.title(ax, "Generic class: one definition, many element types")
    V.box(ax, 50, 74, 34, 10, "class Stack(Generic[T]):", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 22, 48, 24, 12, "Stack[int]\npush ints", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 48, 24, 12, "Stack[str]\npush strs", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 48, 24, 12, "Stack[User]\npush Users", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 69, 24, 55, color=V.NAVY)
    V.arrow(ax, 50, 69, 50, 55, color=V.NAVY)
    V.arrow(ax, 58, 69, 78, 55, color=V.NAVY)
    V.note(ax, 50, 30, "T is a type VARIABLE; the checker tracks the element type", color=V.RED, size=10)
    V.caption(ax, "Generics parameterise a class by type so tools track element types precisely.")
    V.save(fig, IMG + "m11_03_generic.png")


def d04_typevar():
    fig, ax = V.new_canvas()
    V.title(ax, "TypeVar & bounds")
    V.box(ax, 27, 62, 30, 12, "T = TypeVar('T')", fill=V.BLUE_F, size=10)
    V.note(ax, 27, 46, "any type", color=V.GRAY, size=10)
    ax.plot([50, 50], [30, 76], color=V.GRAY, linewidth=1.2, linestyle="--")
    V.box(ax, 73, 62, 34, 12, "N = TypeVar('N',\n bound=Number)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.note(ax, 73, 46, "only Number subtypes", color=V.GRAY, size=10)
    V.note(ax, 50, 30, "same T across params/return -> checker enforces consistency", color=V.RED, size=10)
    V.caption(ax, "A TypeVar links input and output types; 'bound' restricts what it can be.")
    V.save(fig, IMG + "m11_04_typevar.png")


def d05_protocol():
    fig, ax = V.new_canvas()
    V.title(ax, "Protocol: structural typing (static duck typing)")
    V.box(ax, 50, 76, 40, 9, "class Drawable(Protocol): def draw(self)...", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 25, 48, 26, 12, "Circle\nhas draw()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 48, 26, 12, "Button\nhas draw()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 35, 71, 28, 55, color=V.GREEN, dashed=True)
    V.arrow(ax, 62, 71, 70, 55, color=V.GREEN, dashed=True)
    V.note(ax, 50, 30, "NO inheritance needed — matching methods = matching type", color=V.RED, size=10)
    V.caption(ax, "A Protocol matches any object with the right methods — duck typing, checked.")
    V.save(fig, IMG + "m11_05_protocol.png")


def d06_abc_vs_protocol():
    fig, ax = V.new_canvas()
    V.title(ax, "ABC vs Protocol")
    V.box(ax, 27, 58, 40, 40, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 72, "ABC (nominal)", color=V.ORANGE, bold=True, size=12)
    V.note(ax, 27, 61, "must INHERIT it\nexplicit contract", size=11)
    V.note(ax, 27, 47, "'is-a', declared", color=V.GRAY, size=10)
    V.box(ax, 73, 58, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 72, "Protocol (structural)", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 61, "no inheritance;\njust match methods", size=11)
    V.note(ax, 73, 47, "'behaves-like', implicit", color=V.GRAY, size=10)
    V.caption(ax, "ABC = explicit inheritance contract; Protocol = implicit shape match.")
    V.save(fig, IMG + "m11_06_abc_vs_protocol.png")


def d07_mypy_flow():
    fig, ax = V.new_canvas()
    V.title(ax, "mypy catches type errors before you run")
    V.box(ax, 18, 60, 22, 12, "code with\nhints", fill=V.BLUE_F, size=11)
    V.arrow(ax, 29, 60, 42, 60, color=V.NAVY)
    V.box(ax, 55, 60, 22, 12, "mypy checks\n(static)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 66, 66, 80, 74, color=V.RED)
    V.arrow(ax, 66, 54, 80, 46, color=V.GREEN)
    V.box(ax, 90, 74, 16, 9, "error\nfound", fill=V.RED, tcolor="white", size=9)
    V.box(ax, 90, 46, 16, 9, "all\ngood", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.note(ax, 45, 30, "type bugs caught at check time, not in production", color=V.RED, size=11)
    V.caption(ax, "Static type checkers flag mismatches before the code ever runs.")
    V.save(fig, IMG + "m11_07_mypy_flow.png")


def d08_special_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Handy typing constructs")
    rows = [(72, "Optional[X] / X | None", "value or None"),
            (58, "ClassVar[X]", "class attr, not a dataclass field"),
            (44, "Final", "constant; cannot be reassigned"),
            (30, "Self", "return type = 'this class' (chaining)")]
    for y, t, desc in rows:
        V.box(ax, 26, y, 34, 9, t, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.note(ax, 76, y, desc, size=10)
    V.caption(ax, "These annotations express nullability, class-level, immutability, and self-return.")
    V.save(fig, IMG + "m11_08_special_types.png")


if __name__ == "__main__":
    for f in [d01_why_hints, d02_annotate_class, d03_generic, d04_typevar,
              d05_protocol, d06_abc_vs_protocol, d07_mypy_flow, d08_special_types]:
        f()
    print("M11 diagrams done.")
