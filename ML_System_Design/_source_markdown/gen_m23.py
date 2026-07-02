# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 23 (Competitive Exam Mapping).
Reuses viz_style.py helpers (same Office palette as the rest of the course).
Outputs into ../images/ as m23_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The exam landscape — six exams grouped by flavour
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The Competitive Exam Landscape for ML / IT")
    note(ax, 27, 82, "Recruitment (banking/reg.)", color=NAVY, size=12, bold=True)
    note(ax, 74, 82, "Technical / academic", color=GREEN, size=12, bold=True)
    # left group
    box(ax, 20, 68, 22, 10, "SEBI Grade A\n(IT stream)", fill=BLUE_F, edge=NAVY, size=11)
    box(ax, 20, 52, 22, 10, "RBI Grade B\n(IT / DEPR)", fill=BLUE_F, edge=NAVY, size=11)
    # right group
    box(ax, 62, 68, 22, 10, "GATE CS", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 86, 68, 22, 10, "GATE DA\n(Data Sci + AI)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 62, 52, 22, 10, "ISRO\n(Sci/Engr)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 86, 52, 22, 10, "DRDO\n(RAC / CEPTAM)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 50, 24, 44, 12, "Shared core: ML basics + data +\nstatistics + systems foundations",
        fill=GREEN, tcolor="white", size=12)
    caption(ax, "Different exams, one shared core: the foundations decide most of your exam marks.")
    save(fig, p("m23_01_exam_landscape.png"))


# ----------------------------------------------------------------------
# 02  Topic -> exam coverage matrix (simple grid of ticks)
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Topic vs Exam — where each topic is tested")
    exams = ["SEBI", "RBI", "GATE\nCS", "GATE\nDA", "ISRO", "DRDO"]
    topics = ["ML basics", "DBMS", "Data / ETL", "Metrics", "Stats + Prob", "Systems / CAP"]
    x0, dx = 40, 9.5
    y0, dy = 74, 9.5
    # column headers
    for j, e in enumerate(exams):
        note(ax, x0 + j*dx, y0 + 8, e, color=NAVY, size=10, bold=True)
    # coverage: 2=strong(green), 1=some(orange), 0=rare(blank)
    cov = [
        [1, 1, 2, 2, 1, 1],  # ML basics
        [2, 2, 2, 1, 2, 2],  # DBMS
        [1, 1, 1, 2, 1, 1],  # Data/ETL
        [1, 1, 1, 2, 0, 1],  # Metrics
        [1, 2, 2, 2, 1, 1],  # Stats+Prob
        [2, 1, 2, 1, 2, 2],  # Systems/CAP
    ]
    for i, t in enumerate(topics):
        note(ax, 8, y0 - i*dy, t, color=BLACK, size=10, ha="left", bold=True)
        for j in range(len(exams)):
            v = cov[i][j]
            f = GREEN if v == 2 else (ORANGE_F if v == 1 else "white")
            e = GREEN if v == 2 else (ORANGE if v == 1 else GRAY)
            box(ax, x0 + j*dx, y0 - i*dy, 8, 7, "", fill=f, edge=e)
    note(ax, 40, 12, "Green = core / heavy      Orange = appears sometimes      Blank = rare",
         color=BLACK, size=11)
    save(fig, p("m23_02_topic_exam_matrix.png"))


# ----------------------------------------------------------------------
# 03  Frequently-asked high-overlap concepts
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Highest-Overlap Concepts (study these first)")
    items = [
        (25, 72, "ML basics\nsupervised vs\nunsupervised", GREEN_F, GREEN),
        (50, 72, "DBMS for ML\nSQL, joins,\nnormalization", BLUE_F, NAVY),
        (75, 72, "Data pipelines\nETL vs ELT,\nbatch/stream", ORANGE_F, ORANGE),
        (25, 46, "Evaluation\nmetrics: P/R,\nF1, ROC-AUC", GREEN_F, GREEN),
        (50, 46, "Statistics +\nprobability,\nBayes rule", BLUE_F, NAVY),
        (75, 46, "Systems: cache,\nCAP, indexing,\nreplication", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in items:
        box(ax, x, y, 21, 15, t, fill=f, edge=e, size=10, bold=False)
    box(ax, 50, 22, 46, 9, "These six areas repeat across ALL six exams",
        fill=NAVY, tcolor="white", size=12)
    caption(ax, "Master these and you cover the bulk of the ML / data / IT marks in any exam.")
    save(fig, p("m23_03_high_overlap.png"))


# ----------------------------------------------------------------------
# 04  Exam value vs interview value (2x2)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Exam Value vs Interview Value — where each module sits")
    arrow(ax, 20, 20, 20, 82, color=BLACK)
    arrow(ax, 20, 20, 88, 20, color=BLACK)
    note(ax, 54, 12, "Interview value  ->", size=11)
    note(ax, 11, 50, "Exam\nvalue ->", size=11)
    box(ax, 38, 40, 26, 15, "Low exam,\nlow interview\n(rare)", fill=GRAY, tcolor="white", size=10, bold=False)
    box(ax, 71, 40, 26, 15, "Interview-centric\ncase studies,\nframeworks (M02,M13+)",
        fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 38, 65, 26, 15, "Pure exam\ntheory (some\nstats corners)", fill=BLUE_F, size=10, bold=False)
    box(ax, 71, 65, 26, 15, "Foundations that\nserve BOTH: M01,\nM04-07,M18,M19",
        fill=GREEN, tcolor="white", size=10, bold=False)
    caption(ax, "ML system design is interview-centric; the exam marks live in the foundation modules.")
    save(fig, p("m23_04_exam_vs_interview.png"))


# ----------------------------------------------------------------------
# 05  Which modules carry exam value (funnel)
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Where the Exam Value Lives in this Course")
    box(ax, 50, 78, 62, 10, "26 modules of ML System Design (interview-first)",
        fill=BLUE_F, edge=NAVY, size=12)
    arrow(ax, 50, 73, 50, 66, color=NAVY)
    box(ax, 50, 60, 48, 10, "Filter: which have written-exam value?",
        fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 50, 55, 50, 48, color=NAVY)
    row = [
        (16, "M01\nFoundations"), (33, "M04\nData"), (50, "M05/06\nML basics"),
        (67, "M07\nMetrics"), (84, "M18/19\nGovern +\nSystems"),
    ]
    for x, t in row:
        box(ax, x, 40, 15, 12, t, fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 50, 20, 52, 10, "These carry ~90% of the exam-relevant marks",
        fill=GREEN, tcolor="white", size=12)
    caption(ax, "For exams, revise these first; the rest of the course is interview / industry depth.")
    save(fig, p("m23_05_exam_value_funnel.png"))


# ----------------------------------------------------------------------
# 06  Final module -> revision cycle
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "You Finished the Course — now the Revision Cycle")
    circle(ax, 28, 66, 12, "Learn\n(M01-M22)", fill=BLUE_F)
    circle(ax, 72, 66, 12, "Revise\n(M22 wrap)", fill=GREEN_F, edge=GREEN)
    circle(ax, 72, 30, 12, "Map to\nexams\n(M23)", fill=ORANGE_F, edge=ORANGE)
    circle(ax, 28, 30, 12, "Practice\nMCQs +\nmocks", fill=BLUE_F)
    arrow(ax, 40, 66, 60, 66)
    arrow(ax, 72, 54, 72, 42)
    arrow(ax, 60, 30, 40, 30)
    arrow(ax, 28, 42, 28, 54)
    caption(ax, "This is the final module: loop back to M22 revision and keep the cycle spinning.")
    save(fig, p("m23_06_revision_cycle.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06()
    print("All Module 23 diagrams generated.")
