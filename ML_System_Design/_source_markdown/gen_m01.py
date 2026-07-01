# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 1 (Foundations).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m01_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Software 1.0 vs Software 2.0
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Software 1.0 vs Software 2.0 — who writes the rules?")
    # Software 1.0 (top)
    note(ax, 15, 82, "Software 1.0", color=NAVY, size=14, bold=True)
    box(ax, 15, 70, 20, 9, "Data\n(input)", fill=BLUE_F)
    box(ax, 15, 55, 20, 9, "Rules\n(hand-written\nby humans)", fill=ORANGE_F, edge=ORANGE)
    box(ax, 52, 62, 20, 12, "Program\n(if/else logic)", fill=GREEN_F, edge=GREEN)
    box(ax, 85, 62, 20, 9, "Output", fill=BLUE_F)
    arrow(ax, 25, 70, 42, 64)
    arrow(ax, 25, 55, 42, 60)
    arrow(ax, 62, 62, 75, 62)
    # Software 2.0 (bottom)
    note(ax, 15, 40, "Software 2.0 (ML)", color=RED, size=14, bold=True)
    box(ax, 15, 28, 20, 9, "Data\n(input)", fill=BLUE_F)
    box(ax, 15, 13, 20, 9, "Output\n(labels /\nexamples)", fill=BLUE_F)
    box(ax, 52, 20, 20, 12, "Training\nalgorithm", fill=GREEN_F, edge=GREEN)
    box(ax, 85, 20, 20, 9, "Rules\n(the MODEL)", fill=ORANGE_F, edge=ORANGE)
    arrow(ax, 25, 28, 42, 22)
    arrow(ax, 25, 13, 42, 18)
    arrow(ax, 62, 20, 75, 20)
    caption(ax, "1.0: humans write rules.  2.0: we give data + answers and the machine LEARNS the rules.")
    save(fig, p("m01_01_sw1_vs_sw2.png"))


# ----------------------------------------------------------------------
# 02  End-to-end ML lifecycle (the loop)
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "The End-to-End ML Lifecycle — it is a LOOP, not a line")
    steps = [
        (18, 74, "1. Business\nProblem", BLUE_F, NAVY),
        (50, 78, "2. Data\n(collect/label)", GREEN_F, GREEN),
        (82, 74, "3. Features", BLUE_F, NAVY),
        (86, 48, "4. Train\nModel", ORANGE_F, ORANGE),
        (68, 26, "5. Evaluate", GREEN_F, GREEN),
        (42, 22, "6. Deploy\n& Serve", BLUE_F, NAVY),
        (16, 40, "7. Monitor\n& Iterate", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in steps:
        box(ax, x, y, 17, 11, t, fill=f, edge=e, size=11)
    seq = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6)]
    for a, b in seq:
        arrow(ax, steps[a][0], steps[a][1], steps[b][0], steps[b][1], color=NAVY)
    # feedback arrow from monitor back to data
    arrow(ax, 16, 46, 30, 74, color=RED, dashed=True)
    note(ax, 8, 60, "feedback\nloop", color=RED, size=11, bold=True)
    caption(ax, "Monitoring feeds fresh data back in — the model must be RE-trained as the world drifts.")
    save(fig, p("m01_02_ml_lifecycle.png"))


# ----------------------------------------------------------------------
# 03  Anatomy: the tiny ML code vs the huge surrounding system
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Hidden Technical Debt: the ML code is the SMALL box")
    # big surrounding boxes
    surround = [
        (20, 78, "Data\nCollection"), (44, 78, "Data\nVerification"),
        (68, 78, "Feature\nExtraction"), (88, 60, "Serving\nInfra"),
        (88, 40, "Monitoring"), (68, 22, "Config"),
        (44, 22, "Process Mgmt\nTools"), (20, 22, "Analysis\nTools"),
        (12, 50, "Resource\nMgmt"), (32, 50, "Machine\nResources"),
    ]
    for x, y, t in surround:
        box(ax, x, y, 18, 11, t, fill=BLUE_F, edge=NAVY, size=10)
    # tiny ML box in centre
    box(ax, 56, 50, 16, 12, "ML\nCODE", fill=ORANGE, edge=RED, tcolor="white", size=13)
    caption(ax, "In real systems the actual ML model code is a few % of the work. (after Sculley et al., NeurIPS 2015)")
    save(fig, p("m01_03_hidden_debt.png"))


# ----------------------------------------------------------------------
# 04  Types of ML systems (by how predictions are produced)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Types of ML Systems — where does inference run?")
    cols = [
        (16, "BATCH\n(offline)", "Predict for ALL\nusers on a\nschedule; store\nresults in a DB", BLUE_F, NAVY),
        (38, "ONLINE\n(real-time)", "Predict per\nrequest, live,\nunder a strict\nlatency budget", GREEN_F, GREEN),
        (60, "STREAMING", "React to events\nas they arrive\n(Kafka/Flink);\nnear real-time", ORANGE_F, ORANGE),
        (82, "ON-DEVICE\n/ FEDERATED", "Model runs on\nphone/edge;\ndata stays\nprivate", BLUE_F, NAVY),
    ]
    for x, head, body, f, e in cols:
        box(ax, x, 70, 19, 12, head, fill=e, tcolor="white", size=11)
        box(ax, x, 45, 19, 22, body, fill=f, edge=e, size=10, bold=False)
    note(ax, 16, 26, "e.g. nightly\nrecs email", size=10)
    note(ax, 38, 26, "e.g. search\nranking", size=10)
    note(ax, 60, 26, "e.g. fraud\nalerts", size=10)
    note(ax, 82, 26, "e.g. keyboard\nautocomplete", size=10)
    caption(ax, "Choice is driven by: freshness needed vs latency budget vs cost vs privacy.")
    save(fig, p("m01_04_types.png"))


# ----------------------------------------------------------------------
# 05  The data flywheel / feedback loop
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "The Data Flywheel — why ML products compound")
    circle(ax, 30, 68, 11, "More\nUsers", fill=BLUE_F)
    circle(ax, 72, 68, 11, "More\nData", fill=GREEN_F, edge=GREEN)
    circle(ax, 72, 30, 11, "Better\nModel", fill=ORANGE_F, edge=ORANGE)
    circle(ax, 30, 30, 11, "Better\nProduct", fill=BLUE_F)
    arrow(ax, 41, 68, 61, 68)
    arrow(ax, 72, 57, 72, 41)
    arrow(ax, 61, 30, 41, 30)
    arrow(ax, 30, 41, 30, 57)
    caption(ax, "Good loop: better product -> more users -> more data -> better model. Beware BAD loops (bias amplification).")
    save(fig, p("m01_05_flywheel.png"))


# ----------------------------------------------------------------------
# 06  Flowchart: should you even use ML?
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Should you use ML? (a senior signal is saying NO)")
    box(ax, 50, 86, 30, 9, "New problem", fill=BLUE_F)
    box(ax, 50, 70, 40, 9, "Is there a simple rule\nthat solves it?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 70, 22, 9, "Use rules,\nNOT ML", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 50, 53, 40, 9, "Do patterns exist AND\nis there enough data?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 53, 22, 9, "Not ready\nfor ML", fill=RED, tcolor="white", size=10)
    box(ax, 50, 36, 40, 9, "Can you tolerate\nmistakes / uncertainty?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 36, 22, 9, "Rethink /\nkeep human", fill=RED, tcolor="white", size=10)
    box(ax, 50, 18, 30, 10, "USE ML", fill=GREEN, tcolor="white", size=13)
    arrow(ax, 50, 81, 50, 75)
    arrow(ax, 70, 70, 71, 70); note(ax, 66, 74, "yes", color=GREEN, size=10)
    arrow(ax, 50, 65, 50, 58); note(ax, 44, 62, "no", color=NAVY, size=10)
    arrow(ax, 70, 53, 71, 53); note(ax, 66, 57, "no", color=RED, size=10)
    arrow(ax, 50, 48, 50, 41); note(ax, 44, 45, "yes", color=NAVY, size=10)
    arrow(ax, 70, 36, 71, 36); note(ax, 66, 40, "no", color=RED, size=10)
    arrow(ax, 50, 31, 50, 23); note(ax, 44, 28, "yes", color=NAVY, size=10)
    caption(ax, "ML earns its complexity only when rules fail, data exists, and some error is acceptable.")
    save(fig, p("m01_06_fc_use_ml.png"))


# ----------------------------------------------------------------------
# 07  ML system design vs classic system design
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Classic System Design vs ML System Design")
    note(ax, 27, 82, "Classic system", color=NAVY, size=13, bold=True)
    note(ax, 75, 82, "ML system (adds all this)", color=RED, size=13, bold=True)
    left = ["Deterministic logic", "Correct / incorrect", "Behaviour fixed\nuntil code changes", "Test with unit tests"]
    right = ["Probabilistic outputs", "'Good enough' metrics", "Decays over time\n(drift) on its own", "Test + data checks +\nmonitoring + A/B"]
    for i, t in enumerate(left):
        box(ax, 27, 70 - i*14, 30, 10, t, fill=BLUE_F, size=10, bold=False)
    for i, t in enumerate(right):
        box(ax, 75, 70 - i*14, 34, 10, t, fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    caption(ax, "ML systems inherit ALL classic concerns and add data, non-determinism, and decay on top.")
    save(fig, p("m01_07_ml_vs_classic.png"))


# ----------------------------------------------------------------------
# 08  Cost of being wrong — the 2x2 risk quadrant
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Cost of Being Wrong — pick the metric this implies")
    # axes
    arrow(ax, 20, 20, 20, 82, color=BLACK)
    arrow(ax, 20, 20, 88, 20, color=BLACK)
    note(ax, 54, 12, "How OFTEN the model acts  (volume) ->", size=11)
    note(ax, 11, 50, "Cost per\nmistake ->", size=11)
    box(ax, 38, 40, 26, 14, "Low stakes\n(e.g. movie rec)\n-> ship fast", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 70, 40, 26, 14, "High volume,\nlow stakes\n-> guardrails", fill=BLUE_F, size=10, bold=False)
    box(ax, 38, 64, 26, 14, "High stakes,\nrare (e.g. loan)\n-> human review", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 70, 64, 26, 14, "High stakes +\nhigh volume\n(fraud) -> careful!", fill=RED, tcolor="white", size=10, bold=False)
    caption(ax, "Where the mistake lands decides precision-vs-recall, human-in-loop, and rollout caution.")
    save(fig, p("m01_08_cost_of_wrong.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 1 diagrams generated.")
