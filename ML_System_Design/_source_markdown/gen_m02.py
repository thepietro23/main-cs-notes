# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 2 (Interview Framework).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m02_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The universal 7-step framework (serpentine flow + feedback loop)
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The Universal 7-Step ML Design Framework")
    top = [
        (16, "1. Clarify\nRequirements", BLUE_F, NAVY),
        (40, "2. Frame as\nML Problem", ORANGE_F, ORANGE),
        (64, "3. Define\nMetrics", GREEN_F, GREEN),
        (88, "4. Data &\nFeatures", BLUE_F, NAVY),
    ]
    bot = [
        (88, "5. Model &\nTraining", ORANGE_F, ORANGE),
        (52, "6. Serving\n& Scaling", GREEN_F, GREEN),
        (16, "7. Monitor\n& Iterate", BLUE_F, NAVY),
    ]
    for x, t, f, e in top:
        box(ax, x, 68, 18, 12, t, fill=f, edge=e, size=11)
    for x, t, f, e in bot:
        box(ax, x, 34, 18, 12, t, fill=f, edge=e, size=11)
    # top row arrows (left -> right)
    for a, b in [(16, 40), (40, 64), (64, 88)]:
        arrow(ax, a + 9, 68, b - 9, 68)
    # down from step 4 to step 5
    arrow(ax, 88, 62, 88, 40)
    # bottom row arrows (right -> left)
    arrow(ax, 79, 34, 61, 34)
    arrow(ax, 43, 34, 25, 34)
    # feedback arrow: monitor -> clarify
    arrow(ax, 16, 40, 16, 62, color=RED, dashed=True)
    note(ax, 30, 51, "iterate on\nfresh data", color=RED, size=10)
    caption(ax, "Mnemonic: 'CFM-DMSM' — Clarify, Frame, Metrics, Data, Model, Serve, Monitor.")
    save(fig, p("m02_01_seven_steps.png"))


# ----------------------------------------------------------------------
# 02  Frame as an ML problem OR decide NOT to use ML
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Step 2 — Frame it, or Decide NOT to Use ML")
    box(ax, 30, 80, 30, 9, "Business goal", fill=BLUE_F)
    box(ax, 30, 62, 38, 10, "Can a simple rule\nsolve it well?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 62, 24, 10, "Use rules /\nheuristic", fill=GREEN, tcolor="white", size=11)
    box(ax, 30, 42, 38, 10, "Pick the ML task type", fill=NAVY, tcolor="white", size=12)
    tasks = [
        (14, "Classification\n(spam?)"),
        (38, "Ranking\n(recommend)"),
        (62, "Regression\n(ETA)"),
        (86, "Generation\n(LLM reply)"),
    ]
    for x, t in tasks:
        box(ax, x, 22, 19, 11, t, fill=BLUE_F, size=10, bold=False)
    arrow(ax, 30, 75, 30, 67)
    arrow(ax, 49, 62, 70, 62); note(ax, 60, 66, "yes", color=GREEN, size=10)
    arrow(ax, 30, 57, 30, 47); note(ax, 24, 52, "no", color=RED, size=10)
    for x, _ in tasks:
        arrow(ax, 30, 37, x, 28)
    caption(ax, "Always offer the 'no-ML' baseline first, then map the goal to ONE clear ML task.")
    save(fig, p("m02_02_frame_or_not.png"))


# ----------------------------------------------------------------------
# 03  Metrics 2x2: business vs ML, offline vs online
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Step 3 — Four Kinds of Metrics You Must Name")
    arrow(ax, 20, 20, 20, 82, color=BLACK)
    arrow(ax, 20, 20, 90, 20, color=BLACK)
    note(ax, 55, 12, "OFFLINE  (held-out data)   ->   ONLINE  (live users)", size=11)
    note(ax, 10, 50, "ML  ->\nBusiness", size=11)
    box(ax, 40, 62, 28, 14, "BUSINESS + OFFLINE\nproxy estimate\n(rarely enough)", fill=BLUE_F, size=10, bold=False)
    box(ax, 74, 62, 28, 14, "BUSINESS + ONLINE\nrevenue, CTR,\nretention (A/B test)", fill=GREEN, tcolor="white", size=10, bold=False)
    box(ax, 40, 40, 28, 14, "ML + OFFLINE\nAUC, F1, NDCG\non a holdout set", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 74, 40, 28, 14, "ML + ONLINE\nlive accuracy,\nlatency, coverage", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    caption(ax, "Offline metric guides iteration; the ONLINE business metric decides if you ship.")
    save(fig, p("m02_03_metrics_2x2.png"))


# ----------------------------------------------------------------------
# 04  Functional vs Non-functional requirements
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Functional vs Non-Functional Requirements")
    note(ax, 27, 82, "FUNCTIONAL (what it does)", color=NAVY, size=12, bold=True)
    note(ax, 75, 82, "NON-FUNCTIONAL (how well)", color=RED, size=12, bold=True)
    left = ["Recommend 10 items", "Flag fraud in real time", "Answer from our docs"]
    right = ["Latency  (p99 < 100 ms)", "Throughput  (50k QPS)", "Scale / cost / availability"]
    for i, t in enumerate(left):
        box(ax, 27, 68 - i*16, 32, 11, t, fill=BLUE_F, size=10, bold=False)
    for i, t in enumerate(right):
        box(ax, 75, 68 - i*16, 36, 11, t, fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    caption(ax, "In ML interviews the NON-functional requirements usually drive the hardest choices.")
    save(fig, p("m02_04_func_vs_nonfunc.png"))


# ----------------------------------------------------------------------
# 05  How NFRs drive design decisions
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "How Non-Functional Requirements Drive Design")
    rows = [
        (70, "Tight latency\n(p99 < 50 ms)", "Small model +\ncache + ANN index"),
        (48, "Huge throughput\n(100k QPS)", "Batch precompute +\nhorizontal scaling"),
        (26, "Low cost budget", "Simpler model /\ndistillation"),
    ]
    for y, req, dec in rows:
        box(ax, 24, y, 30, 13, req, fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
        box(ax, 76, y, 32, 13, dec, fill=GREEN_F, edge=GREEN, size=11, bold=False)
        arrow(ax, 40, y, 59, y, color=NAVY)
    note(ax, 24, 82, "requirement", color=RED, size=11, bold=True)
    note(ax, 76, 82, "design implication", color=GREEN, size=11, bold=True)
    caption(ax, "State the number first, then let it justify every architecture choice you make.")
    save(fig, p("m02_05_nfr_drives_design.png"))


# ----------------------------------------------------------------------
# 06  Managing the ~45-minute interview (timeline)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Driving the ~45-Minute Interview (a time budget)")
    phases = [
        (14, "Clarify &\nscope", "~5 min", BLUE_F, NAVY),
        (33, "Frame +\nmetrics", "~8 min", ORANGE_F, ORANGE),
        (52, "Data &\nfeatures", "~10 min", GREEN_F, GREEN),
        (71, "Model &\nserving", "~12 min", BLUE_F, NAVY),
        (90, "Scale, monitor\n& wrap-up", "~10 min", ORANGE_F, ORANGE),
    ]
    for x, t, mins, f, e in phases:
        box(ax, x, 58, 17, 14, t, fill=f, edge=e, size=10)
        note(ax, x, 44, mins, color=NAVY, size=11, bold=True)
    for a, b in [(14, 33), (33, 52), (52, 71), (71, 90)]:
        arrow(ax, a + 8.5, 58, b - 8.5, 58)
    note(ax, 50, 28, "Announce your plan up front. Leave the last 5 min\nfor trade-offs, failure modes and next steps.",
         color=NAVY, size=11)
    caption(ax, "Spend early minutes on scoping — a wrong frame wastes the whole session.")
    save(fig, p("m02_06_time_budget.png"))


# ----------------------------------------------------------------------
# 07  Junior vs Senior vs Staff answer patterns
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Junior vs Senior vs Staff — the Answer Pattern")
    cols = [
        (18, "JUNIOR", ["Jumps to a\nmodel", "Lists tools", "Ignores\ntrade-offs"], BLUE_F, NAVY),
        (50, "SENIOR", ["Follows the\nframework", "Names metrics", "Weighs\ntrade-offs"], GREEN_F, GREEN),
        (82, "STAFF", ["Clarifies +\nquestions ML", "Ties to business", "Plans failure\n& iteration"], ORANGE_F, ORANGE),
    ]
    for x, head, items, f, e in cols:
        box(ax, x, 74, 22, 11, head, fill=e, tcolor="white", size=13)
        for i, it in enumerate(items):
            box(ax, x, 58 - i*15, 24, 12, it, fill=f, edge=e, size=10, bold=False)
    caption(ax, "Seniority = breadth (business + ML + systems) and owning trade-offs, not more model math.")
    save(fig, p("m02_07_seniority.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07()
    print("All Module 2 diagrams generated.")
