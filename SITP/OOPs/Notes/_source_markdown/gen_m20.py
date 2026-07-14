"""Module 20 — Exam & Interview Mapping + Question Bank: diagram generator."""
import viz_style as V
IMG = "../images/"


def d01_topic_importance():
    fig, ax = V.new_canvas()
    V.title(ax, "Topic priority for interviews")
    rows = [(74, "P0", "4 pillars, dunders, inheritance/MRO", V.GREEN, V.GREEN_F),
            (60, "P0", "SOLID, patterns, LLD", V.GREEN, V.GREEN_F),
            (46, "P1", "object model, descriptors, dataclasses", V.ORANGE, V.ORANGE_F),
            (32, "P1", "typing/Protocols, exceptions, memory", V.ORANGE, V.ORANGE_F),
            (18, "P2", "metaclasses, __slots__, UML notation", V.NAVY, V.BLUE_F)]
    for y, p, topics, e, f in rows:
        V.box(ax, 16, y, 12, 10, p, fill=f, edge=e, size=12)
        V.note(ax, 62, y, topics, size=10)
    V.caption(ax, "Master P0 first (pillars + design); P1 next; P2 for depth/senior roles.")
    V.save(fig, IMG + "m20_01_topic_importance.png")


def d02_interview_flow():
    fig, ax = V.new_canvas()
    V.title(ax, "How OOP interview questions escalate")
    steps = [(16, "Define\n(pillars)"), (38, "Explain\n+ example"),
             (60, "Predict\noutput / code"), (84, "Design\n(LLD)")]
    for i, (x, t) in enumerate(steps):
        f = V.GREEN_F if i < 2 else (V.ORANGE_F if i == 2 else V.BLUE_F)
        e = V.GREEN if i < 2 else (V.ORANGE if i == 2 else V.NAVY)
        V.box(ax, x, 58, 20, 14, t, fill=f, edge=e, size=10)
        if i < 3:
            V.arrow(ax, x + 10, 58, steps[i + 1][0] - 10, 58, color=V.NAVY)
    V.note(ax, 50, 34, "easy warm-up -> deep design; depth increases with seniority", color=V.RED, size=10)
    V.caption(ax, "Expect the ladder: definition -> example -> code/output -> full design.")
    V.save(fig, IMG + "m20_02_interview_flow.png")


def d03_most_asked():
    fig, ax = V.new_canvas()
    V.title(ax, "Top FAANG OOP questions")
    qs = ["4 pillars + example each", "is vs == ; mutable default bug",
          "MRO / diamond problem", "@classmethod vs @staticmethod",
          "__eq__/__hash__ contract", "SOLID (apply, not recite)",
          "Strategy / Observer / Factory", "Design a parking lot / elevator"]
    for i, q in enumerate(qs):
        y = 76 - i * 8
        V.note(ax, 15, y, str(i + 1) + ".", color=V.NAVY, bold=True, size=11, ha="left")
        V.note(ax, 22, y, q, size=11, ha="left")
    V.caption(ax, "If you can nail these eight, you cover the vast majority of OOP rounds.")
    V.save(fig, IMG + "m20_03_most_asked.png")


def d04_question_types():
    fig, ax = V.new_canvas()
    V.title(ax, "Four question types")
    data = [(27, 62, "Conceptual", "define / compare\n(pillars, is vs ==)", V.GREEN_F, V.GREEN),
            (73, 62, "Output prediction", "trace aliasing,\nMRO, defaults", V.ORANGE_F, V.ORANGE),
            (27, 32, "Code / implement", "write a class,\ndunders, pattern", V.BLUE_F, V.NAVY),
            (73, 32, "Design (LLD)", "model a system\nend-to-end", V.BLUE_F, V.NAVY)]
    for x, y, name, desc, f, e in data:
        V.box(ax, x, y, 40, 20, "", fill=f, edge=e)
        V.note(ax, x, y + 5, name, color=e, bold=True, size=11)
        V.note(ax, x, y - 4, desc, size=9)
    V.caption(ax, "Practise all four; output-prediction and design separate strong candidates.")
    V.save(fig, IMG + "m20_04_question_types.png")


def d05_answer_framework():
    fig, ax = V.new_canvas()
    V.title(ax, "How to answer 'Explain X'")
    steps = [(78, "1. one-line definition"), (63, "2. why it exists (problem)"),
             (48, "3. tiny Python example"), (33, "4. trade-off / when NOT to use"),
             (18, "5. relate to a pillar / principle")]
    for y, t in steps:
        V.box(ax, 50, y, 56, 10, t, fill=V.BLUE_F, size=11)
    V.caption(ax, "Definition -> motivation -> example -> trade-off -> connection. Crisp and complete.")
    V.save(fig, IMG + "m20_05_answer_framework.png")


def d06_output_traps():
    fig, ax = V.new_canvas()
    V.title(ax, "Output-prediction traps to rehearse")
    traps = ["mutable default arg reused", "b = a aliasing a list",
             "is vs == (interning: 256 vs 1000)", "MRO order in a diamond",
             "mutable class attribute shared", "shadowing a class attr on instance",
             "__eq__ without __hash__ -> unhashable"]
    for i, t in enumerate(traps):
        y = 74 - i * 8
        V.note(ax, 14, y, "-", color=V.RED, bold=True, size=12, ha="left")
        V.note(ax, 18, y, t, size=10, ha="left")
    V.caption(ax, "These recur constantly; rehearse the exact output and the reason.")
    V.save(fig, IMG + "m20_06_output_traps.png")


def d07_revision_priority():
    fig, ax = V.new_canvas()
    V.title(ax, "Spaced-revision plan")
    rows = [(72, "24 hours", "recite 4 pillars, is vs ==, MRO rule"),
            (56, "1 week", "SOLID, top patterns, output traps"),
            (40, "1 month", "design 2 LLD systems from scratch"),
            (24, "before interview", "cheat sheet (M21) + 1 mock design")]
    for y, when, what in rows:
        V.box(ax, 22, y, 24, 10, when, fill=V.GREEN_F, edge=V.GREEN, size=10)
        V.note(ax, 72, y, what, size=10)
    V.caption(ax, "Space your revision: recall daily, drill weekly, design monthly.")
    V.save(fig, IMG + "m20_07_revision_priority.png")


def d08_prep_plan():
    fig, ax = V.new_canvas()
    V.title(ax, "A 2-week OOP interview sprint")
    rows = [(74, "Days 1-3", "pillars + object model + classes (M1-M4)"),
            (60, "Days 4-6", "inheritance, polymorphism, dunders (M5-M8)"),
            (46, "Days 7-9", "SOLID + patterns (M13-M15)"),
            (32, "Days 10-12", "LLD practice (M18) — parking, elevator"),
            (18, "Days 13-14", "mock interviews + cheat sheet drill")]
    for y, when, what in rows:
        V.box(ax, 20, y, 20, 10, when, fill=V.BLUE_F, size=10)
        V.note(ax, 70, y, what, size=10)
    V.caption(ax, "Two focused weeks, front-loading pillars and ending on live design.")
    V.save(fig, IMG + "m20_08_prep_plan.png")


if __name__ == "__main__":
    for f in [d01_topic_importance, d02_interview_flow, d03_most_asked,
              d04_question_types, d05_answer_framework, d06_output_traps,
              d07_revision_priority, d08_prep_plan]:
        f()
    print("M20 diagrams done.")
