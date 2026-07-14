"""Module 13 — SOLID Principles: diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_solid_overview():
    fig, ax = V.new_canvas()
    V.title(ax, "SOLID — five principles of maintainable OOP")
    rows = [(74, "S", "Single Responsibility", "one reason to change"),
            (60, "O", "Open/Closed", "open to extend, closed to modify"),
            (46, "L", "Liskov Substitution", "subtype usable as base type"),
            (32, "I", "Interface Segregation", "many small interfaces"),
            (18, "D", "Dependency Inversion", "depend on abstractions")]
    for y, letter, name, desc in rows:
        V.circle(ax, 14, y, 5.5, letter, fill=V.NAVY, tcolor="white", size=14)
        V.box(ax, 40, y, 30, 10, name, fill=V.BLUE_F, size=11)
        V.note(ax, 78, y, desc, size=10)
    V.caption(ax, "SOLID turns working code into code that survives change.")
    V.save(fig, IMG + "m13_01_solid_overview.png")


def d02_srp():
    fig, ax = V.new_canvas()
    V.title(ax, "S - Single Responsibility Principle")
    V.box(ax, 25, 58, 30, 30, "", fill=V.RED, edge=V.RED)
    V.note(ax, 25, 72, "God class", color="white", bold=True, size=11)
    V.note(ax, 25, 60, "parse + validate\n+ save + email", color="white", size=10)
    V.note(ax, 25, 44, "many reasons to change", color="white", size=9)
    V.arrow(ax, 43, 58, 55, 58, color=V.NAVY)
    for i, (y, t) in enumerate([(74, "Parser"), (58, "Validator"), (42, "Repository")]):
        V.box(ax, 78, y, 26, 10, t, fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.note(ax, 78, 30, "each: one job, one reason to change", color=V.GREEN, size=10)
    V.caption(ax, "Split a class that does many jobs into focused single-purpose classes.")
    V.save(fig, IMG + "m13_02_srp.png")


def d03_ocp():
    fig, ax = V.new_canvas()
    V.title(ax, "O - Open/Closed Principle")
    V.box(ax, 50, 74, 34, 10, "Shape (abstract area())", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 22, 50, 20, 10, "Circle", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 50, 50, 20, 10, "Square", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 50, 20, 10, "Triangle\n(NEW)", fill=V.BLUE_F, size=10)
    for x in (22, 50, 78):
        V.arrow(ax, x, 55, 46 if x < 50 else (50 if x == 50 else 54), 69, color=V.NAVY)
    V.note(ax, 50, 32, "add a new shape WITHOUT editing existing code / total_area()", color=V.RED, size=10)
    V.caption(ax, "Open to extension (new subclasses), closed to modification of tested code.")
    V.save(fig, IMG + "m13_03_ocp.png")


def d04_lsp():
    fig, ax = V.new_canvas()
    V.title(ax, "L - Liskov Substitution Principle")
    V.box(ax, 25, 62, 30, 12, "expects a Bird\n(can fly)", fill=V.BLUE_F, size=10)
    V.box(ax, 72, 74, 26, 10, "Sparrow -> flies OK", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 50, 26, 12, "Penguin -> fly()\nbreaks!", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 40, 64, 58, 74, color=V.GREEN)
    V.arrow(ax, 40, 60, 58, 53, color=V.RED)
    V.note(ax, 50, 30, "a subtype must be usable wherever the base type is expected", color=V.RED, size=10)
    V.caption(ax, "If a subclass violates the base's contract, it breaks substitutability.")
    V.save(fig, IMG + "m13_04_lsp.png")


def d05_isp():
    fig, ax = V.new_canvas()
    V.title(ax, "I - Interface Segregation Principle")
    V.box(ax, 25, 60, 30, 26, "", fill=V.RED, edge=V.RED)
    V.note(ax, 25, 70, "fat interface", color="white", bold=True, size=11)
    V.note(ax, 25, 58, "work + eat + sleep\n(robot forced to eat)", color="white", size=9)
    V.arrow(ax, 43, 60, 55, 60, color=V.NAVY)
    for y, t in [(74, "Workable"), (58, "Eatable"), (42, "Sleepable")]:
        V.box(ax, 78, y, 24, 10, t, fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.note(ax, 78, 30, "clients implement only what they need", color=V.GREEN, size=10)
    V.caption(ax, "Prefer many small, focused interfaces over one fat, do-everything one.")
    V.save(fig, IMG + "m13_05_isp.png")


def d06_dip():
    fig, ax = V.new_canvas()
    V.title(ax, "D - Dependency Inversion Principle")
    V.note(ax, 27, 82, "BAD (concrete)", color=V.RED, bold=True, size=10)
    V.box(ax, 27, 66, 22, 9, "Service", fill=V.BLUE_F, size=10)
    V.box(ax, 27, 48, 24, 9, "MySQLDb", fill=V.RED, tcolor="white", size=10)
    V.arrow(ax, 27, 61, 27, 53, color=V.RED)
    V.note(ax, 27, 38, "tied to MySQL", color=V.RED, size=9)
    ax.plot([50, 50], [34, 80], color=V.GRAY, linewidth=1.2, linestyle="--")
    V.note(ax, 74, 82, "GOOD (abstraction)", color=V.GREEN, bold=True, size=10)
    V.box(ax, 74, 66, 22, 9, "Service", fill=V.BLUE_F, size=10)
    V.box(ax, 74, 55, 26, 9, "Database (ABC)", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.box(ax, 74, 42, 26, 9, "MySQL / Postgres", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 74, 61, 74, 60, color=V.NAVY)
    V.arrow(ax, 74, 47, 74, 51, color=V.GREEN, style="-|>")
    V.caption(ax, "Depend on an abstraction (interface), not a concrete implementation.")
    V.save(fig, IMG + "m13_06_dip.png")


def d07_di():
    fig, ax = V.new_canvas()
    V.title(ax, "Dependency Injection makes DIP practical")
    V.box(ax, 25, 60, 30, 14, "Service(db)\ndb passed IN", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 41, 60, 58, 60, color=V.NAVY)
    V.box(ax, 78, 60, 30, 14, "swap MySQL /\nMock in tests", fill=V.BLUE_F, size=10)
    V.note(ax, 50, 38, "the caller provides the dependency (constructor injection)", color=V.RED, size=11)
    V.note(ax, 50, 28, "easy to test, easy to swap implementations", color=V.GRAY, size=10)
    V.caption(ax, "Inject dependencies from outside instead of hard-creating them inside.")
    V.save(fig, IMG + "m13_07_di.png")


def d08_solid_payoff():
    fig, ax = V.new_canvas()
    V.title(ax, "Why SOLID: change without fear")
    V.box(ax, 27, 58, 40, 34, "", fill=V.RED, edge=V.RED)
    V.note(ax, 27, 70, "NOT SOLID", color="white", bold=True, size=12)
    V.note(ax, 27, 58, "one change ripples\neverywhere; fragile", color="white", size=10)
    V.box(ax, 73, 58, 40, 34, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 70, "SOLID", color=V.GREEN, bold=True, size=12)
    V.note(ax, 73, 58, "changes are local;\nextend by adding", size=10)
    V.note(ax, 73, 46, "testable, flexible", color=V.GREEN, size=9)
    V.caption(ax, "SOLID localises change and enables safe extension — the goal of good design.")
    V.save(fig, IMG + "m13_08_solid_payoff.png")


if __name__ == "__main__":
    for f in [d01_solid_overview, d02_srp, d03_ocp, d04_lsp, d05_isp, d06_dip,
              d07_di, d08_solid_payoff]:
        f()
    print("M13 diagrams done.")
