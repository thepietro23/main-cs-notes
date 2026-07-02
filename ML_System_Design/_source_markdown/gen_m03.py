# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 3 (Problem Framing & Requirements).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m03_*.png at 150 dpi on white.
Design rule #1: keep every diagram SIMPLE (<=10 boxes, generous spacing, short labels).
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  From business goal to a concrete ML objective
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "From Business Goal to a Concrete ML Objective")
    xs = [14, 38, 62, 86]
    heads = [
        ("Business\nGoal", BLUE_F, NAVY),
        ("Success\nMetric", ORANGE_F, ORANGE),
        ("ML Objective\n(the label)", GREEN_F, GREEN),
        ("ML Task", BLUE_F, NAVY),
    ]
    for x, (t, f, e) in zip(xs, heads):
        box(ax, x, 62, 19, 13, t, fill=f, edge=e, size=12)
    for i in range(3):
        arrow(ax, xs[i] + 9.5, 62, xs[i + 1] - 9.5, 62)
    examples = ["Keep users\nengaged", "Watch-time\nper session",
                "Predict a video's\nwatch-time", "Regression"]
    for x, t in zip(xs, examples):
        note(ax, x, 40, t, size=11)
    note(ax, 50, 30, "Example: video streaming", color=GRAY, size=11, bold=True)
    caption(ax, "Never optimize the business goal directly — translate it step by step into a label a model can predict.")
    save(fig, p("m03_01_business_to_ml.png"))


# ----------------------------------------------------------------------
# 02  Choosing the ML task — start from the OUTPUT
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Choosing the ML Task — start from the OUTPUT")
    box(ax, 17, 50, 22, 16, "What does the\nsystem\nOUTPUT?", fill=ORANGE, edge=RED, tcolor="white", size=12)
    leaves = [
        (81, "A class label", "Classification\n(spam / not)", GREEN_F, GREEN),
        (68, "A number", "Regression\n(predict ETA)", BLUE_F, NAVY),
        (55, "An ordering", "Ranking\n(order a feed)", GREEN_F, GREEN),
        (42, "A matching item", "Retrieval\n(find similar)", BLUE_F, NAVY),
        (29, "New content", "Generation\n(write a reply)", GREEN_F, GREEN),
        (16, "A rare event / action", "Anomaly / RL\n(fraud; control)", BLUE_F, NAVY),
    ]
    for y, lbl, t, f, e in leaves:
        box(ax, 74, y, 30, 10, t, fill=f, edge=e, size=11)
        arrow(ax, 28, 50, 58, y)
    caption(ax, "The shape of the output (a class, a number, an ordering, an item, new content) fixes the task.")
    save(fig, p("m03_02_task_decision.png"))


# ----------------------------------------------------------------------
# 03  When NOT to use ML (reinforce)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "When NOT to Use ML (a senior signal is saying NO)")
    conds = [
        (78, "A simple rule\nalready works"),
        (58, "Too little or no\nlabeled data"),
        (38, "Zero error tolerance\n& no human backup"),
        (18, "You cannot MEASURE\nsuccess (no metric)"),
    ]
    for y, t in conds:
        box(ax, 27, y, 34, 13, t, fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
        arrow(ax, 44, y, 66, 48)
    box(ax, 82, 48, 26, 18, "Don't use ML\n(use rules /\nheuristic)", fill=GREEN, tcolor="white", size=12)
    caption(ax, "If ANY of these holds, ML adds cost and risk without payoff. Reach for the simplest thing that works.")
    save(fig, p("m03_03_when_not_ml.png"))


# ----------------------------------------------------------------------
# 04  Defining the label — three failure modes
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Defining the Label — three things that bite you")
    cols = [
        (18, "PROXY\nLABELS", "True target is\nhard to measure,\nso you use a\nstand-in signal", ORANGE, ORANGE_F),
        (50, "LABEL\nLEAKAGE", "A feature secretly\ncontains the\nanswer -> fake\noffline accuracy", RED, ORANGE_F),
        (82, "DELAYED\nLABELS", "The true label\narrives weeks\nlater (e.g. loan\ndefault, churn)", NAVY, BLUE_F),
    ]
    for x, head, body, e, f in cols:
        box(ax, x, 70, 22, 13, head, fill=e, tcolor="white", size=12)
        box(ax, x, 44, 24, 22, body, fill=f, edge=e, size=10, bold=False)
    caption(ax, "Getting the label wrong quietly poisons everything downstream — this is where most ML projects fail.")
    save(fig, p("m03_04_label_pitfalls.png"))


# ----------------------------------------------------------------------
# 05  Label leakage — a feature that peeks at the future
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Label Leakage — a feature that peeks at the future")
    arrow(ax, 12, 42, 92, 42, color=BLACK)
    note(ax, 90, 36, "time", color=BLACK, size=11)
    # time markers
    circle(ax, 32, 42, 1.4, "", fill=NAVY, edge=NAVY)
    circle(ax, 74, 42, 1.4, "", fill=RED, edge=RED)
    note(ax, 32, 34, "t = now\n(we predict)", color=NAVY, size=11)
    note(ax, 74, 34, "t + 7 days\n(label known)", color=RED, size=11)
    box(ax, 32, 66, 26, 15, "OK feature:\nuses only data\nfrom <= now", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 74, 66, 26, 15, "LEAKY feature:\nuses data from\nAFTER now", fill=ORANGE_F, edge=RED, size=11, bold=False)
    arrow(ax, 32, 58, 32, 44)
    arrow(ax, 74, 58, 74, 44)
    caption(ax, "Fraud demo: 'account_was_closed' is only set AFTER fraud is confirmed -> using it leaks the label.")
    save(fig, p("m03_05_label_leakage.png"))


# ----------------------------------------------------------------------
# 06  Proxy metric vs true goal — misalignment
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Proxy Metric vs True Goal — when they diverge")
    box(ax, 16, 66, 22, 13, "Optimize\nCLICKS\n(proxy)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 50, 66, 24, 13, "Model learns to\nserve CLICKBAIT", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 85, 66, 22, 13, "Clicks up,\nTRUST down", fill=RED, tcolor="white", size=11)
    arrow(ax, 27, 66, 38, 66)
    arrow(ax, 62, 66, 74, 66)
    box(ax, 50, 30, 30, 13, "TRUE goal:\nlong-term\nsatisfaction", fill=GREEN_F, edge=GREEN, size=12)
    arrow(ax, 85, 59, 58, 37, color=RED, dashed=True)
    note(ax, 82, 46, "hurts the\nreal goal", color=RED, size=10, bold=True)
    caption(ax, "A proxy that is easy to measure can quietly work against the goal you actually care about.")
    save(fig, p("m03_06_proxy_misalignment.png"))


# ----------------------------------------------------------------------
# 07  Capacity estimation 1 — DAU -> QPS -> peak QPS
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Capacity Estimation (1):  DAU -> QPS -> Peak QPS")
    steps = [
        (16, "100M DAU\n(daily active\nusers)", BLUE_F, NAVY),
        (39, "x10 requests\n/user/day\n= 1B req/day", GREEN_F, GREEN),
        (62, "/ 86,400 s\n= ~11.6k QPS\n(average)", ORANGE_F, ORANGE),
        (85, "x3 peak\nfactor\n= ~35k QPS", RED, "white"),
    ]
    for x, t, f, tc in steps:
        tcolor = "white" if tc == "white" else BLACK
        edge = RED if tc == "white" else NAVY
        box(ax, x, 55, 20, 18, t, fill=f, edge=edge, tcolor=tcolor, size=11, bold=False)
    for i in range(3):
        arrow(ax, steps[i][0] + 10, 55, steps[i + 1][0] - 10, 55)
    note(ax, 50, 30, "Size the serving fleet for PEAK, not average.", color=NAVY, size=12, bold=True)
    caption(ax, "Back-of-envelope: turn users into requests, requests into QPS, then multiply by a peak factor.")
    save(fig, p("m03_07_qps_sizing.png"))


# ----------------------------------------------------------------------
# 08  Capacity estimation 2 — embedding table storage
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Capacity Estimation (2):  Embedding Table Size")
    steps = [
        (16, "10M items", BLUE_F, NAVY),
        (39, "x 128 dims", GREEN_F, GREEN),
        (62, "x 4 bytes\n(float32)", ORANGE_F, ORANGE),
        (85, "= 5.12 GB", RED, "white"),
    ]
    for x, t, f, tc in steps:
        tcolor = "white" if tc == "white" else BLACK
        edge = RED if tc == "white" else NAVY
        box(ax, x, 60, 20, 13, t, fill=f, edge=edge, tcolor=tcolor, size=12)
    for i in range(3):
        arrow(ax, steps[i][0] + 10, 60, steps[i + 1][0] - 10, 60)
    box(ax, 50, 34, 62, 13, "Also: 50M users x 64 dims x 4 B  =  12.8 GB", fill=BLUE_F, edge=NAVY, size=12, bold=False)
    caption(ax, "rows x dimension x bytes-per-float = table size. Decide if it fits in RAM or needs a param server.")
    save(fig, p("m03_08_storage_sizing.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 3 diagrams generated.")
