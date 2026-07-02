# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 7 (Model Evaluation).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m07_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Confusion matrix (the 2x2 that every metric comes from)
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The Confusion Matrix — where every metric is born")
    # column headers (predicted)
    note(ax, 58, 84, "PREDICTED", color=NAVY, size=12, bold=True)
    note(ax, 44, 78, "Positive", color=NAVY, size=11, bold=True)
    note(ax, 74, 78, "Negative", color=NAVY, size=11, bold=True)
    # row headers (actual)
    note(ax, 14, 60, "ACTUAL", color=NAVY, size=12, bold=True, ha="center")
    note(ax, 24, 60, "Positive", color=NAVY, size=11, bold=True)
    note(ax, 24, 36, "Negative", color=NAVY, size=11, bold=True)
    # cells
    box(ax, 44, 60, 26, 16, "TP\nTrue Positive\n(caught it)", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 74, 60, 26, 16, "FN\nFalse Negative\n(missed it)", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 44, 36, 26, 16, "FP\nFalse Positive\n(false alarm)", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 74, 36, 26, 16, "TN\nTrue Negative\n(correct pass)", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    caption(ax, "Precision = TP/(TP+FP) ... Recall = TP/(TP+FN). Green = correct, orange = the two error types.")
    save(fig, p("m07_01_confusion_matrix.png"))


# ----------------------------------------------------------------------
# 02  Precision vs Recall — when each one matters
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Precision vs Recall — which error hurts more?")
    box(ax, 28, 74, 34, 10, "PRECISION\nof what I flagged,\nhow much was right?", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 72, 74, 34, 10, "RECALL\nof all real positives,\nhow many did I catch?", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 28, 50, 34, 12, "Optimise PRECISION\nwhen a FALSE ALARM\nis costly", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 72, 50, 34, 12, "Optimise RECALL\nwhen a MISS\nis costly", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    note(ax, 28, 34, "e.g. spam filter:\ndon't junk a real email", size=10)
    note(ax, 72, 34, "e.g. cancer screen:\ndon't miss a sick patient", size=10)
    box(ax, 50, 18, 40, 10, "F1 = harmonic mean\nof precision & recall", fill=ORANGE, tcolor="white", size=11)
    caption(ax, "You usually trade one for the other; F1 balances them, cost of errors picks the winner.")
    save(fig, p("m07_02_precision_recall.png"))


# ----------------------------------------------------------------------
# 03  ROC and PR curves (drawn with ax.plot)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "ROC Curve and PR Curve — reading the sketch")

    # ---- ROC panel (left) ----
    ox, oy, W, H = 12, 26, 32, 50
    arrow(ax, ox, oy, ox, oy + H + 3, color=BLACK)
    arrow(ax, ox, oy, ox + W + 3, oy, color=BLACK)
    note(ax, ox + W/2, oy - 6, "FPR ->", size=10)
    note(ax, ox - 6, oy + H/2, "TPR", size=10)
    note(ax, ox + W/2, oy + H + 8, "ROC", color=NAVY, size=12, bold=True)
    # diagonal (random)
    ax.plot([ox, ox + W], [oy, oy + H], color=GRAY, ls="--", lw=2)
    # good ROC curve
    fpr = [0, 0.05, 0.12, 0.25, 0.45, 0.7, 1.0]
    tpr = [0, 0.45, 0.65, 0.82, 0.92, 0.97, 1.0]
    ax.plot([ox + f*W for f in fpr], [oy + t*H for t in tpr], color=NAVY, lw=2.5)
    note(ax, ox + 20, oy + 12, "random", color=GRAY, size=9)

    # ---- PR panel (right) ----
    ox2 = 62
    arrow(ax, ox2, oy, ox2, oy + H + 3, color=BLACK)
    arrow(ax, ox2, oy, ox2 + W + 3, oy, color=BLACK)
    note(ax, ox2 + W/2, oy - 6, "Recall ->", size=10)
    note(ax, ox2 - 7, oy + H/2, "Prec.", size=10)
    note(ax, ox2 + W/2, oy + H + 8, "PR", color=NAVY, size=12, bold=True)
    rec = [0, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0]
    prec = [1.0, 0.97, 0.92, 0.85, 0.72, 0.5, 0.3]
    ax.plot([ox2 + r*W for r in rec], [oy + pv*H for pv in prec], color=ORANGE, lw=2.5)
    # baseline = class prevalence
    ax.plot([ox2, ox2 + W], [oy + 0.2*H, oy + 0.2*H], color=GRAY, ls="--", lw=2)
    note(ax, ox2 + 18, oy + 0.2*H - 5, "prevalence", color=GRAY, size=9)

    caption(ax, "Higher curve = better. Use PR (not ROC) when positives are RARE (imbalanced data).")
    save(fig, p("m07_03_roc_pr_curves.png"))


# ----------------------------------------------------------------------
# 04  Calibration / reliability diagram
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Calibration (Reliability Diagram) — do the 0.7's happen 70%?")
    ox, oy, W, H = 26, 24, 48, 52
    arrow(ax, ox, oy, ox, oy + H + 3, color=BLACK)
    arrow(ax, ox, oy, ox + W + 3, oy, color=BLACK)
    note(ax, ox + W/2, oy - 6, "Predicted probability ->", size=11)
    note(ax, ox - 9, oy + H/2, "Observed\nfrequency", size=10)
    # perfect calibration diagonal
    ax.plot([ox, ox + W], [oy, oy + H], color=GREEN, ls="--", lw=2.5)
    note(ax, ox + W - 6, oy + H - 4, "perfect", color=GREEN, size=10)
    # overconfident model (below diagonal on the right)
    px = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    py = [0.02, 0.12, 0.28, 0.42, 0.6, 0.85]
    ax.plot([ox + a*W for a in px], [oy + b*H for b in py], color=RED, lw=2.5, marker="o", ms=4)
    note(ax, ox + 0.7*W, oy + 0.35*H, "over-\nconfident", color=RED, size=10)
    caption(ax, "A model can be ACCURATE yet MIS-CALIBRATED. Fix with Platt scaling or isotonic regression.")
    save(fig, p("m07_04_calibration.png"))


# ----------------------------------------------------------------------
# 05  Regression metrics — residuals picture
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Regression Metrics — all measure the residual (error)")
    ox, oy, W, H = 14, 24, 40, 50
    arrow(ax, ox, oy, ox, oy + H + 3, color=BLACK)
    arrow(ax, ox, oy, ox + W + 3, oy, color=BLACK)
    note(ax, ox + W/2, oy - 6, "x", size=11)
    note(ax, ox - 4, oy + H/2, "y", size=11)
    # fitted line
    ax.plot([ox + 2, ox + W - 2], [oy + 6, oy + H - 6], color=NAVY, lw=2.5)
    # points + residual sticks
    pts = [(0.15, 0.32), (0.35, 0.30), (0.55, 0.70), (0.8, 0.72)]
    line = [(0.15, 0.22), (0.35, 0.42), (0.55, 0.62), (0.8, 0.86)]
    for (xp, yp), (xl, yl) in zip(pts, line):
        X = ox + xp*W
        ax.plot([X, X], [oy + yp*H, oy + yl*H], color=RED, lw=2)
        ax.plot([X], [oy + yp*H], color=ORANGE, marker="o", ms=6)
    note(ax, ox + 0.55*W + 6, oy + 0.5*H, "residual\n= y - y_hat", color=RED, size=10)
    # formula panel
    box(ax, 80, 62, 32, 9, "MAE = mean |error|", fill=BLUE_F, size=11, bold=False)
    box(ax, 80, 50, 32, 9, "MSE = mean error^2", fill=BLUE_F, size=11, bold=False)
    box(ax, 80, 38, 32, 9, "RMSE = sqrt(MSE)", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 80, 26, 32, 9, "R^2 = 1 - SSE/SST", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    caption(ax, "MSE/RMSE punish big errors most; MAE is robust; R^2 is the fraction of variance explained.")
    save(fig, p("m07_05_regression_metrics.png"))


# ----------------------------------------------------------------------
# 06  NDCG worked example (ranking)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "NDCG — reward relevant items ranked HIGH")
    note(ax, 50, 84, "Ranked results (left = top of list)", size=11, bold=True)
    # ranked positions with relevance grades
    ranks = [
        (16, "rank 1\nrel = 3", GREEN_F, GREEN),
        (32, "rank 2\nrel = 2", GREEN_F, GREEN),
        (48, "rank 3\nrel = 3", GREEN_F, GREEN),
        (64, "rank 4\nrel = 0", BLUE_F, NAVY),
        (80, "rank 5\nrel = 1", BLUE_F, NAVY),
    ]
    for x, t, f, e in ranks:
        box(ax, x, 66, 13, 12, t, fill=f, edge=e, size=10, bold=False)
    # discount weights below
    note(ax, 50, 52, "discount by log2(1+rank)  ->  gain = (2^rel - 1) / log2(1+rank)", size=10)
    box(ax, 30, 38, 40, 11, "DCG = sum of\ndiscounted gains = 12.78", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 74, 38, 40, 11, "IDCG (ideal order)\n= 13.35", fill=BLUE_F, size=11, bold=False)
    box(ax, 50, 20, 40, 10, "NDCG = DCG / IDCG = 0.96", fill=GREEN, tcolor="white", size=12)
    caption(ax, "NDCG in [0,1]: 1 = perfect order. Top ranks weigh most (log discount), graded relevance allowed.")
    save(fig, p("m07_06_ndcg.png"))


# ----------------------------------------------------------------------
# 07  Splits: random vs temporal, and data leakage
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Train / Val / Test Splits — use TIME for production")
    # temporal split (good)
    note(ax, 12, 74, "Temporal", color=GREEN, size=12, bold=True, ha="left")
    box(ax, 30, 68, 30, 10, "TRAIN\n(past)", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 55, 68, 18, 10, "VAL", fill=BLUE_F, size=11, bold=False)
    box(ax, 76, 68, 18, 10, "TEST\n(future)", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 15, 58, 90, 58, color=NAVY)
    note(ax, 52, 54, "time ->", size=10)
    note(ax, 52, 46, "Train on the PAST, test on the FUTURE — matches how production really runs.", color=GREEN, size=10)
    # random split leakage (bad)
    note(ax, 12, 38, "Random split on time-series", color=RED, size=12, bold=True, ha="left")
    box(ax, 40, 28, 44, 10, "future rows leak into TRAIN\n-> LEAKAGE, too-good offline score", fill=RED, tcolor="white", size=10, bold=False)
    caption(ax, "Leakage = future/label info sneaks into features. Great offline, terrible live. Split by TIME.")
    save(fig, p("m07_07_splits.png"))


# ----------------------------------------------------------------------
# 08  A/B test flow
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Online Evaluation — the A/B Test flow")
    box(ax, 18, 66, 22, 12, "Live users\n(traffic)", fill=BLUE_F, size=11)
    box(ax, 50, 80, 24, 11, "Control (A)\nold model", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 50, 52, 24, 11, "Treatment (B)\nnew model", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 29, 68, 38, 80)
    arrow(ax, 29, 64, 38, 54)
    note(ax, 34, 74, "50%", size=9); note(ax, 34, 58, "50%", size=9)
    box(ax, 82, 66, 24, 12, "Compare\nguardrail +\ntarget metric", fill=BLUE_F, size=11, bold=False)
    arrow(ax, 62, 80, 74, 70)
    arrow(ax, 62, 52, 74, 62)
    box(ax, 50, 26, 52, 11, "Is the lift statistically significant?\n(p < 0.05, enough sample size)", fill=ORANGE, tcolor="white", size=11, bold=False)
    arrow(ax, 82, 60, 62, 32)
    caption(ax, "Randomly split traffic, run long enough for significance, watch guardrails before you ship.")
    save(fig, p("m07_08_ab_test.png"))


# ----------------------------------------------------------------------
# 09  Offline-online metric gap
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "The Offline-Online Gap — and how to bridge it")
    box(ax, 22, 66, 26, 14, "OFFLINE\nAUC / NDCG on\nheld-out data", fill=BLUE_F, size=11, bold=False)
    box(ax, 78, 66, 26, 14, "ONLINE\nclicks, revenue,\nretention (A/B)", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    arrow(ax, 35, 66, 65, 66, color=RED)
    note(ax, 50, 72, "often DISAGREE", color=RED, size=11, bold=True)
    note(ax, 50, 58, "gap causes: leakage, wrong metric,\nstale data, feedback loops, novelty effects", color=RED, size=10)
    box(ax, 22, 32, 30, 12, "Bridge:\npick offline metric\nthat tracks the goal", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 55, 32, 24, 12, "shadow /\nreplay on\nreal traffic", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 82, 32, 22, 12, "always confirm\nwith an A/B\ntest", fill=GREEN, tcolor="white", size=10, bold=False)
    caption(ax, "Offline decides what to SHIP to a test; the online A/B test decides what to LAUNCH.")
    save(fig, p("m07_09_offline_online_gap.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09()
    print("All Module 7 diagrams generated.")
