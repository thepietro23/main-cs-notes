# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 20 (Interview Mastery).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m20_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The 8 question patterns you must recognise
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The 8 Question Patterns — recognise, then reuse")
    cells = [
        (20, 74, "Recsys\n(feed, PYMK)", BLUE_F, NAVY),
        (50, 74, "Ranking /\nSearch", GREEN_F, GREEN),
        (80, 74, "CTR /\nAds", ORANGE_F, ORANGE),
        (20, 52, "Fraud /\nAnomaly", BLUE_F, NAVY),
        (50, 52, "ETA /\nRegression", GREEN_F, GREEN),
        (80, 52, "LLM /\nRAG", ORANGE_F, ORANGE),
        (35, 30, "Serving /\nInfra", BLUE_F, NAVY),
        (65, 30, "Graph /\nPYMK", GREEN_F, GREEN),
    ]
    for x, y, t, f, e in cells:
        box(ax, x, y, 22, 13, t, fill=f, edge=e, size=11)
    caption(ax, "Most interview prompts are one of these 8. Map the prompt -> pattern -> known blueprint.")
    save(fig, p("m20_01_question_patterns.png"))


# ----------------------------------------------------------------------
# 02  Ideal 45-minute interview timeline (the Staff bar)
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "The Ideal 45-Minute Timeline")
    steps = [
        (50, 82, "0-5 min: Clarify goal, scope, constraints", GREEN_F, GREEN),
        (50, 68, "5-10 min: Frame as ML, pick metric", BLUE_F, NAVY),
        (50, 54, "10-25 min: Data, features, model", ORANGE_F, ORANGE),
        (50, 40, "25-38 min: Serving, scale, monitoring", BLUE_F, NAVY),
        (50, 26, "38-45 min: Trade-offs, follow-ups, wrap", GREEN_F, GREEN),
    ]
    for x, y, t, f, e in steps:
        box(ax, x, y, 62, 9, t, fill=f, edge=e, size=12)
    for i in range(len(steps) - 1):
        arrow(ax, 50, steps[i][1] - 4.5, 50, steps[i+1][1] + 4.5, color=NAVY)
    note(ax, 88, 54, "spend\nMOST\ntime\nhere", color=RED, size=10, bold=True)
    caption(ax, "Budget your time out loud. Never spend 40 min on the model and skip serving + monitoring.")
    save(fig, p("m20_02_45min_timeline.png"))


# ----------------------------------------------------------------------
# 03  Company interview styles (comparison)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Company Styles — tune the same answer")
    cols = [
        (18, "GOOGLE /\nMETA", "Depth,\nscale,\ntrade-offs", BLUE_F, NAVY),
        (40, "AMAZON", "Leadership\nPrinciples,\ncustomer", ORANGE_F, ORANGE),
        (62, "OpenAI /\nAnthropic", "LLM, RAG,\nevals,\nsafety", GREEN_F, GREEN),
        (84, "NVIDIA", "Infra,\nGPUs,\nthroughput", BLUE_F, NAVY),
    ]
    for x, head, body, f, e in cols:
        box(ax, x, 66, 19, 12, head, fill=e, tcolor="white", size=11)
        box(ax, x, 42, 19, 20, body, fill=f, edge=e, size=10, bold=False)
    note(ax, 30, 22, "Netflix: metrics + A/B  |  Apple: privacy + on-device",
         color=NAVY, size=11, ha="left")
    note(ax, 30, 16, "Uber/Airbnb/Stripe: real-time, fraud, ETA, cost",
         color=NAVY, size=11, ha="left")
    caption(ax, "Same 7-step core; shift emphasis to what each company rewards.")
    save(fig, p("m20_03_company_styles.png"))


# ----------------------------------------------------------------------
# 04  Anatomy of a mock answer (the flow)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Anatomy of a Strong Mock Answer")
    steps = [
        (16, 60, "Problem\nstatement", BLUE_F, NAVY),
        (38, 60, "Clarifying\nquestions", ORANGE_F, ORANGE),
        (60, 60, "Full 7-step\ndesign", GREEN_F, GREEN),
        (82, 60, "Follow-ups\n(deep dive)", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in steps:
        box(ax, x, y, 19, 13, t, fill=f, edge=e, size=11)
    for i in range(len(steps) - 1):
        arrow(ax, steps[i][0] + 9.5, 60, steps[i+1][0] - 9.5, 60, color=NAVY)
    box(ax, 50, 32, 40, 12, "What a STAFF answer adds:\ntrade-offs, cost, failure modes",
        fill=RED, tcolor="white", size=11, bold=False)
    arrow(ax, 82, 53, 60, 39, color=RED)
    caption(ax, "Junior stops at 'the design'. Staff layers trade-offs and 'what breaks at 100x'.")
    save(fig, p("m20_04_mock_flow.png"))


# ----------------------------------------------------------------------
# 05  Handling "I don't know", scope creep, curveballs
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "When You Get Stuck — recover, don't freeze")
    box(ax, 25, 74, 30, 11, "\"I don't know\"", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 25, 50, 34, 11, "Reason out loud from\nfirst principles", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 25, 68, 25, 56, color=NAVY)

    box(ax, 75, 74, 30, 11, "Scope creep", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 75, 50, 34, 11, "State assumptions,\ncut scope explicitly", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 75, 68, 75, 56, color=NAVY)

    box(ax, 50, 24, 40, 12, "Curveball -> restate it,\nlink to a pattern you know", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    arrow(ax, 25, 44, 45, 30, color=NAVY)
    arrow(ax, 75, 44, 55, 30, color=NAVY)
    caption(ax, "Silence and guessing both fail. Narrate your thinking and steer back to solid ground.")
    save(fig, p("m20_05_curveballs.png"))


# ----------------------------------------------------------------------
# 06  Red flags that fail candidates (checklist)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Red Flags That Fail Candidates")
    flags = [
        (28, 76, "Jumps to model,\nskips the metric"),
        (72, 76, "No clarifying\nquestions"),
        (28, 56, "Forgets serving\n& monitoring"),
        (72, 56, "Ignores scale\n& cost"),
        (28, 36, "Silent when\nstuck"),
        (72, 36, "Never mentions\ntrade-offs"),
    ]
    for x, y, t in flags:
        box(ax, x, y, 34, 12, t, fill=ORANGE_F, edge=RED, size=11, bold=False)
        note(ax, x - 21, y, "X", color=RED, size=16, bold=True)
    caption(ax, "Any two of these on a loop usually means a no-hire. Audit yourself against this list.")
    save(fig, p("m20_06_red_flags.png"))


# ----------------------------------------------------------------------
# 07  Junior vs Senior vs Staff ladder
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "What Gets You the Staff Bar")
    box(ax, 25, 30, 26, 14, "JUNIOR\nBuilds the\nhappy path", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 50, 48, 26, 14, "SENIOR\nHandles scale,\nfailure modes", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 75, 66, 26, 14, "STAFF\nDrives ambiguity,\nowns trade-offs", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 38, 34, 45, 43, color=NAVY)
    arrow(ax, 63, 52, 70, 61, color=NAVY)
    caption(ax, "Staff answers connect ML choice <-> systems choice <-> business impact, without prompting.")
    save(fig, p("m20_07_staff_bar.png"))


# ----------------------------------------------------------------------
# 08  Whiteboarding & communication layout
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Whiteboard Layout & Communication")
    box(ax, 20, 70, 26, 12, "Left: goal,\nmetric,\nconstraints", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 50, 70, 26, 12, "Center: the\ndata -> model\n-> serve flow", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    box(ax, 80, 70, 26, 12, "Right: open\nquestions,\nfollow-ups", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 50, 42, 60, 12, "Talk while you draw: state each choice AND why", fill=BLUE_F, edge=NAVY, size=12, bold=False)
    arrow(ax, 50, 64, 50, 48, color=NAVY)
    note(ax, 50, 26, "Signpost: \"First I'll clarify, then design, then trade-offs.\"",
         color=RED, size=12, bold=True)
    caption(ax, "A clear, narrated whiteboard is half the score. Structure beats a messy genius sketch.")
    save(fig, p("m20_08_whiteboard.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 20 diagrams generated.")
