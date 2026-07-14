"""Module 14 — Design Patterns I (Creational & Structural): diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_categories():
    fig, ax = V.new_canvas()
    V.title(ax, "GoF design patterns — three families")
    data = [
        (20, "CREATIONAL", "how objects are\nMADE", "Singleton, Factory,\nBuilder, Prototype", V.GREEN_F, V.GREEN),
        (50, "STRUCTURAL", "how objects are\nCOMPOSED", "Adapter, Decorator,\nFacade, Proxy", V.ORANGE_F, V.ORANGE),
        (80, "BEHAVIORAL", "how objects\nINTERACT", "Strategy, Observer,\n(Module 15)", V.BLUE_F, V.NAVY),
    ]
    for x, name, what, ex, f, e in data:
        V.box(ax, x, 52, 27, 44, "", fill=f, edge=e)
        V.note(ax, x, 66, name, color=e, bold=True, size=11)
        V.note(ax, x, 56, what, size=10)
        V.note(ax, x, 42, ex, color=V.GRAY, size=9)
    V.caption(ax, "Creational (make), Structural (compose), Behavioral (interact) — this module: first two.")
    V.save(fig, IMG + "m14_01_categories.png")


def d02_singleton():
    fig, ax = V.new_canvas()
    V.title(ax, "Singleton: exactly one instance")
    V.box(ax, 20, 70, 16, 9, "a = Cfg()", fill=V.BLUE_F, size=10)
    V.box(ax, 20, 50, 16, 9, "b = Cfg()", fill=V.BLUE_F, size=10)
    V.box(ax, 65, 60, 28, 16, "ONE Config\ninstance", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.arrow(ax, 28, 70, 51, 63, color=V.GREEN)
    V.arrow(ax, 28, 50, 51, 57, color=V.GREEN)
    V.note(ax, 65, 40, "a is b -> True", color=V.RED, size=11)
    V.note(ax, 50, 26, "in Python, a MODULE is already a singleton — often no class needed", color=V.NAVY, size=10)
    V.caption(ax, "Singleton guarantees a single shared instance (config, logger, pool).")
    V.save(fig, IMG + "m14_02_singleton.png")


def d03_factory():
    fig, ax = V.new_canvas()
    V.title(ax, "Factory: create objects by a key, hide the class")
    V.box(ax, 25, 62, 30, 14, "make('circle')\n(client)", fill=V.BLUE_F, size=10)
    V.arrow(ax, 41, 62, 55, 62, color=V.NAVY)
    V.box(ax, 66, 62, 20, 12, "Factory", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 66, 40, 20, 9, "Circle", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 90, 40, 18, 9, "Square", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 66, 56, 66, 45, color=V.GREEN)
    V.arrow(ax, 70, 56, 88, 45, color=V.GREEN)
    V.note(ax, 45, 30, "client asks for WHAT, not HOW to build it", color=V.RED, size=10)
    V.caption(ax, "A factory centralises object creation; clients depend on a key, not classes.")
    V.save(fig, IMG + "m14_03_factory.png")


def d04_builder():
    fig, ax = V.new_canvas()
    V.title(ax, "Builder: step-by-step construction")
    steps = [(16, "Burger\nBuilder()"), (38, ".bun()"), (58, ".patty()"), (78, ".build()")]
    for i, (x, t) in enumerate(steps):
        f = V.GREEN_F if i == len(steps) - 1 else V.BLUE_F
        e = V.GREEN if i == len(steps) - 1 else V.NAVY
        V.box(ax, x, 58, 18, 12, t, fill=f, edge=e, size=10)
        if i < len(steps) - 1:
            V.arrow(ax, x + 9, 58, steps[i + 1][0] - 9, 58, color=V.NAVY)
    V.note(ax, 50, 34, "chain optional steps -> a complex object, readably", color=V.RED, size=11)
    V.caption(ax, "Builder assembles a complex object piece by piece with a fluent API.")
    V.save(fig, IMG + "m14_04_builder.png")


def d05_adapter():
    fig, ax = V.new_canvas()
    V.title(ax, "Adapter: make incompatible interfaces fit")
    V.box(ax, 18, 60, 20, 12, "Client\nwants .pay()", fill=V.BLUE_F, size=10)
    V.box(ax, 50, 60, 22, 12, "Adapter\n.pay()->.charge()", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.box(ax, 84, 60, 22, 12, "Legacy\n.charge()", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 28, 60, 39, 60, color=V.NAVY)
    V.arrow(ax, 61, 60, 73, 60, color=V.NAVY)
    V.note(ax, 50, 34, "wraps an old/foreign API into the interface the client expects", color=V.RED, size=10)
    V.caption(ax, "Adapter translates one interface into another so they can work together.")
    V.save(fig, IMG + "m14_05_adapter.png")


def d06_decorator():
    fig, ax = V.new_canvas()
    V.title(ax, "Decorator: wrap to add behaviour dynamically")
    V.circle(ax, 25, 58, 9, "Coffee", fill=V.BLUE_F, size=10)
    V.circle(ax, 50, 58, 13, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 50, 58, "+Milk", size=10, color=V.BLACK)
    V.circle(ax, 78, 58, 17, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 78, 58, "+Sugar", size=10, color=V.BLACK)
    V.arrow(ax, 34, 58, 38, 58, color=V.NAVY)
    V.arrow(ax, 62, 58, 62, 58, color=V.NAVY)
    V.note(ax, 50, 30, "each layer adds cost()/behaviour without changing Coffee", color=V.RED, size=10)
    V.caption(ax, "Decorator layers new behaviour around an object (same interface).")
    V.save(fig, IMG + "m14_06_decorator.png")


def d07_facade():
    fig, ax = V.new_canvas()
    V.title(ax, "Facade: one simple door to a complex subsystem")
    V.box(ax, 20, 60, 20, 12, "Client", fill=V.BLUE_F, size=11)
    V.box(ax, 50, 60, 20, 12, "Facade\n.watch()", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 30, 60, 39, 60, color=V.NAVY)
    for y, t in [(76, "Amplifier"), (60, "Projector"), (44, "Lights")]:
        V.box(ax, 82, y, 22, 9, t, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.arrow(ax, 60, 60, 70, y, color=V.GREEN, dashed=True)
    V.note(ax, 45, 28, "facade.watch() drives all subsystems in the right order", color=V.RED, size=10)
    V.caption(ax, "Facade hides a messy multi-part subsystem behind one easy method.")
    V.save(fig, IMG + "m14_07_facade.png")


def d08_proxy_composite():
    fig, ax = V.new_canvas()
    V.title(ax, "Proxy (stand-in) & Composite (tree)")
    V.note(ax, 27, 82, "PROXY", color=V.ORANGE, bold=True, size=11)
    V.box(ax, 12, 60, 14, 10, "Client", fill=V.BLUE_F, size=9)
    V.box(ax, 30, 60, 14, 10, "Proxy", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.box(ax, 46, 60, 14, 10, "Real", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 19, 60, 23, 60, color=V.NAVY)
    V.arrow(ax, 37, 60, 39, 60, color=V.NAVY)
    V.note(ax, 29, 46, "lazy / access\ncontrol / cache", color=V.GRAY, size=8)
    ax.plot([62, 62], [40, 78], color=V.GRAY, linewidth=1.2, linestyle="--")
    V.note(ax, 80, 82, "COMPOSITE", color=V.GREEN, bold=True, size=11)
    V.box(ax, 80, 70, 16, 8, "Folder", fill=V.BLUE_F, size=9)
    V.box(ax, 70, 52, 14, 8, "File", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 90, 52, 16, 8, "Folder", fill=V.BLUE_F, size=9)
    V.arrow(ax, 76, 66, 71, 56, color=V.NAVY)
    V.arrow(ax, 84, 66, 90, 56, color=V.NAVY)
    V.note(ax, 80, 40, "treat leaf & group alike", color=V.GRAY, size=8)
    V.caption(ax, "Proxy: a controlled stand-in. Composite: treat single & grouped objects uniformly.")
    V.save(fig, IMG + "m14_08_proxy_composite.png")


if __name__ == "__main__":
    for f in [d01_categories, d02_singleton, d03_factory, d04_builder, d05_adapter,
              d06_decorator, d07_facade, d08_proxy_composite]:
        f()
    print("M14 diagrams done.")
