"""Module 15 — Design Patterns II (Behavioral): diagram generator."""
import viz_style as V

IMG = "../images/"


def d01_overview():
    fig, ax = V.new_canvas()
    V.title(ax, "Behavioral patterns — how objects interact")
    rows = [(74, "Strategy", "swap algorithms at run time"),
            (61, "Observer", "publish/subscribe notifications"),
            (48, "Command", "request as an object (undo/queue)"),
            (35, "State", "behaviour changes with internal state"),
            (22, "Template / Chain", "skeleton steps / pass-the-request")]
    for y, name, desc in rows:
        V.box(ax, 28, y, 30, 10, name, fill=V.BLUE_F, size=11)
        V.note(ax, 76, y, desc, size=10)
    V.caption(ax, "Behavioral patterns organise communication and responsibility between objects.")
    V.save(fig, IMG + "m15_01_overview.png")


def d02_strategy():
    fig, ax = V.new_canvas()
    V.title(ax, "Strategy: swap interchangeable algorithms")
    V.box(ax, 25, 62, 30, 14, "Sorter(strategy)\n.sort(data)", fill=V.BLUE_F, size=10)
    V.box(ax, 72, 76, 26, 9, "QuickSort", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 62, 26, 9, "MergeSort", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 48, 26, 9, "BubbleSort", fill=V.GREEN_F, edge=V.GREEN, size=10)
    for y in (76, 62, 48):
        V.arrow(ax, 40, 62, 59, y, color=V.NAVY, dashed=True)
    V.note(ax, 45, 30, "pick the algorithm at run time; the client code is unchanged", color=V.RED, size=10)
    V.caption(ax, "Strategy makes algorithms interchangeable via composition (replaces if/elif).")
    V.save(fig, IMG + "m15_02_strategy.png")


def d03_observer():
    fig, ax = V.new_canvas()
    V.title(ax, "Observer: subject notifies its subscribers")
    V.box(ax, 25, 60, 26, 14, "Subject\n(publisher)", fill=V.ORANGE_F, edge=V.ORANGE, size=11)
    V.box(ax, 78, 78, 24, 9, "Observer A", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 60, 24, 9, "Observer B", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 78, 42, 24, 9, "Observer C", fill=V.GREEN_F, edge=V.GREEN, size=10)
    for y in (78, 60, 42):
        V.arrow(ax, 38, 60, 66, y, color=V.NAVY)
    V.note(ax, 55, 68, "notify()", color=V.GRAY, size=9)
    V.note(ax, 50, 28, "state change -> all subscribers auto-updated (pub/sub)", color=V.RED, size=10)
    V.caption(ax, "Observer: one-to-many auto-notification when the subject's state changes.")
    V.save(fig, IMG + "m15_03_observer.png")


def d04_command():
    fig, ax = V.new_canvas()
    V.title(ax, "Command: wrap a request as an object")
    V.box(ax, 18, 60, 18, 12, "Invoker\n(button)", fill=V.BLUE_F, size=10)
    V.box(ax, 50, 60, 22, 12, "Command\nexecute()/undo()", fill=V.ORANGE_F, edge=V.ORANGE, size=9)
    V.box(ax, 84, 60, 20, 12, "Receiver\n(does work)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 27, 60, 39, 60, color=V.NAVY)
    V.arrow(ax, 61, 60, 74, 60, color=V.NAVY)
    V.note(ax, 50, 34, "requests become objects -> undo, redo, queue, log, macro", color=V.RED, size=10)
    V.caption(ax, "Command turns an action into a stored object enabling undo/redo/queueing.")
    V.save(fig, IMG + "m15_04_command.png")


def d05_state():
    fig, ax = V.new_canvas()
    V.title(ax, "State: behaviour changes with internal state")
    V.box(ax, 20, 60, 20, 11, "Draft", fill=V.BLUE_F, size=11)
    V.box(ax, 50, 60, 22, 11, "Published", fill=V.GREEN_F, edge=V.GREEN, size=11)
    V.box(ax, 82, 60, 20, 11, "Archived", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.arrow(ax, 30, 60, 39, 60, color=V.NAVY)
    V.arrow(ax, 61, 60, 72, 60, color=V.NAVY)
    V.note(ax, 35, 68, "publish()", color=V.GRAY, size=9)
    V.note(ax, 66, 68, "archive()", color=V.GRAY, size=9)
    V.note(ax, 50, 34, "the same method behaves differently per state (state machine)", color=V.RED, size=10)
    V.caption(ax, "State lets an object alter its behaviour when its internal state changes.")
    V.save(fig, IMG + "m15_05_state.png")


def d06_template_method():
    fig, ax = V.new_canvas()
    V.title(ax, "Template Method: fixed skeleton, variable steps")
    V.box(ax, 50, 74, 44, 10, "Base.run(): step1(); step2(); step3()", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 28, 50, 30, 12, "SubA:\nstep2() = X", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 72, 50, 30, 12, "SubB:\nstep2() = Y", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.arrow(ax, 42, 69, 30, 57, color=V.NAVY)
    V.arrow(ax, 58, 69, 72, 57, color=V.NAVY)
    V.note(ax, 50, 30, "base fixes the ORDER; subclasses fill in specific steps", color=V.RED, size=10)
    V.caption(ax, "Template Method defines an algorithm's skeleton; subclasses override steps.")
    V.save(fig, IMG + "m15_06_template_method.png")


def d07_chain():
    fig, ax = V.new_canvas()
    V.title(ax, "Chain of Responsibility: pass it along")
    boxes = [(16, "L1 support"), (40, "L2 support"), (66, "Manager"), (90, "unhandled")]
    for i, (x, t) in enumerate(boxes):
        f = V.RED if i == 3 else V.GREEN_F
        e = V.RED if i == 3 else V.GREEN
        tc = "white" if i == 3 else V.BLACK
        V.box(ax, x, 60, 20, 11, t, fill=f, edge=e, tcolor=tc, size=10)
        if i < 3:
            V.arrow(ax, x + 10, 60, boxes[i + 1][0] - 10, 60, color=V.NAVY)
            V.note(ax, (x + boxes[i + 1][0]) / 2, 67, "can't?", color=V.GRAY, size=8)
    V.note(ax, 50, 34, "each handler either handles the request or passes it on", color=V.RED, size=10)
    V.caption(ax, "Chain of Responsibility passes a request along handlers until one handles it.")
    V.save(fig, IMG + "m15_07_chain.png")


def d08_strategy_pythonic():
    fig, ax = V.new_canvas()
    V.title(ax, "Pythonic Strategy: just pass a function")
    V.box(ax, 27, 58, 40, 34, "", fill=V.ORANGE_F, edge=V.ORANGE)
    V.note(ax, 27, 70, "CLASSIC (Java-y)", color=V.ORANGE, bold=True, size=10)
    V.note(ax, 27, 58, "Strategy ABC +\nconcrete classes", size=10)
    V.note(ax, 27, 45, "lots of boilerplate", color=V.RED, size=9)
    V.box(ax, 73, 58, 40, 34, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 73, 70, "PYTHONIC", color=V.GREEN, bold=True, size=11)
    V.note(ax, 73, 58, "pass a function:\nsort(data, key=fn)", size=10)
    V.note(ax, 73, 45, "functions are objects", color=V.GREEN, size=9)
    V.caption(ax, "In Python, a first-class function often IS the strategy — no class hierarchy.")
    V.save(fig, IMG + "m15_08_strategy_pythonic.png")


if __name__ == "__main__":
    for f in [d01_overview, d02_strategy, d03_observer, d04_command, d05_state,
              d06_template_method, d07_chain, d08_strategy_pythonic]:
        f()
    print("M15 diagrams done.")
