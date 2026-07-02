# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 10
(Monitoring, Drift & Reliability).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m10_*.png at 150 dpi on white.
"""
import os
import numpy as np
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The monitoring stack — what to watch, bottom to top
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The ML Monitoring Stack — what to watch")
    layers = [
        (74, "Business / Product metric", "revenue, engagement, CTR", GREEN_F, GREEN),
        (61, "Model performance", "accuracy, AUC, calibration", ORANGE_F, ORANGE),
        (48, "Prediction drift", "output distribution shifts", ORANGE_F, ORANGE),
        (35, "Feature / data drift", "input distribution shifts", BLUE_F, NAVY),
        (22, "System health", "latency, errors, saturation", BLUE_F, NAVY),
    ]
    for y, head, sub, f, e in layers:
        box(ax, 40, y, 46, 10, head, fill=f, edge=e, size=12)
        note(ax, 78, y, sub, size=10, ha="center")
    note(ax, 40, 82, "harder to detect, closer to $$$", color=RED, size=11, bold=True)
    note(ax, 40, 15, "easy to detect, far from $$$", color=NAVY, size=11)
    caption(ax, "Watch bottom-up: system health is instant; model quality lags until labels arrive.")
    save(fig, p("m10_01_monitoring_stack.png"))


# ----------------------------------------------------------------------
# 02  Data drift — two distributions shifting apart
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Data Drift — the live input distribution moves")
    xs = np.linspace(10, 90, 300)
    def gauss(mu, sd, amp):
        return amp * np.exp(-0.5 * ((xs - mu) / sd) ** 2)
    base = 20 + gauss(40, 9, 45)
    live = 20 + gauss(62, 11, 40)
    ax.plot(xs, base, color=NAVY, lw=2.5)
    ax.fill_between(xs, 20, base, color=BLUE_F, alpha=0.6)
    ax.plot(xs, live, color=RED, lw=2.5, linestyle="--")
    ax.fill_between(xs, 20, live, color=ORANGE_F, alpha=0.5)
    note(ax, 34, 70, "training\n(reference)", color=NAVY, size=11, bold=True)
    note(ax, 74, 64, "live traffic\n(now)", color=RED, size=11, bold=True)
    arrow(ax, 44, 30, 60, 30, color=BLACK)
    note(ax, 52, 25, "mean shifts right", size=10)
    caption(ax, "Same feature, new shape. PSI / KL / KS measure HOW FAR the two curves have moved.")
    save(fig, p("m10_02_data_drift_curves.png"))


# ----------------------------------------------------------------------
# 03  PSI worked example — per-bin contributions
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Population Stability Index (PSI) — worked bins")
    bins = ["B1", "B2", "B3", "B4", "B5"]
    exp = [0.20, 0.20, 0.20, 0.20, 0.20]      # expected (training)
    act = [0.10, 0.15, 0.20, 0.25, 0.30]      # actual (live)
    x0, w = 22, 12
    for i, b in enumerate(bins):
        x = x0 + i * w
        box(ax, x, 78, 9, 8, b, fill=GREEN_F, edge=GREEN, size=11)
        # expected bar
        ax.bar(x - 2.2, exp[i] * 120, width=3.6, bottom=30, color=BLUE_F, edgecolor=NAVY)
        # actual bar
        ax.bar(x + 2.2, act[i] * 120, width=3.6, bottom=30, color=ORANGE_F, edgecolor=ORANGE)
    note(ax, 78, 74, "expected", color=NAVY, size=11, bold=True)
    note(ax, 78, 68, "actual", color=ORANGE, size=11, bold=True)
    note(ax, 50, 20, "PSI = Σ (actual − expected) · ln(actual / expected)  ≈  0.14",
         size=12, bold=True, color=BLACK)
    caption(ax, "PSI<0.1 stable · 0.1–0.25 moderate shift · >0.25 major drift, investigate now.")
    save(fig, p("m10_03_psi_bins.png"))


# ----------------------------------------------------------------------
# 04  Data drift vs concept drift
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Data Drift vs Concept Drift")
    note(ax, 27, 82, "DATA drift", color=NAVY, size=13, bold=True)
    note(ax, 75, 82, "CONCEPT drift", color=RED, size=13, bold=True)
    box(ax, 27, 68, 34, 11, "Inputs P(X) change", fill=BLUE_F, size=11)
    box(ax, 27, 52, 34, 11, "Input–label link\nP(Y|X) stays same", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 27, 34, 34, 12, "e.g. new user\nregion, new\ntraffic mix", fill=BLUE_F, size=10, bold=False)
    box(ax, 75, 68, 34, 11, "Meaning P(Y|X)\nchanges", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 75, 52, 34, 11, "Same input now\nmaps to new label", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 75, 34, 34, 12, "e.g. fraud tactic\nchanges, tastes\nshift", fill=RED, tcolor="white", size=10, bold=False)
    caption(ax, "Data drift: the world you SEE moved. Concept drift: the RULE you learned is now wrong.")
    save(fig, p("m10_04_data_vs_concept.png"))


# ----------------------------------------------------------------------
# 05  Retraining strategies
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Retraining Strategies — when to refit the model")
    cols = [
        (22, "SCHEDULED", "Retrain on a\nfixed cadence\n(daily / weekly)", "simple; may\nretrain too\noften or late", BLUE_F, NAVY),
        (50, "TRIGGERED", "Retrain when\ndrift or perf\ndrop is detected", "efficient; needs\ngood monitors\n+ thresholds", GREEN_F, GREEN),
        (78, "CONTINUAL\n/ ONLINE", "Update model\nas each new\nbatch arrives", "freshest; risk\nof instability\n& bad-data harm", ORANGE_F, ORANGE),
    ]
    for x, head, body, tradeoff, f, e in cols:
        box(ax, x, 74, 22, 12, head, fill=e, tcolor="white", size=12)
        box(ax, x, 52, 22, 18, body, fill=f, edge=e, size=10, bold=False)
        note(ax, x, 30, tradeoff, size=10)
    caption(ax, "Cadence trades cost & stability vs freshness. Always validate before promoting a new model.")
    save(fig, p("m10_05_retraining.png"))


# ----------------------------------------------------------------------
# 06  Degenerate feedback loop
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Degenerate Feedback Loop — bias amplifies itself")
    circle(ax, 28, 66, 11, "Model\nshows\npopular", fill=ORANGE_F, edge=ORANGE)
    circle(ax, 72, 66, 11, "Users\nclick only\nwhat's shown", fill=BLUE_F)
    circle(ax, 72, 30, 11, "Logs say\npopular =\ngood", fill=BLUE_F)
    circle(ax, 28, 30, 11, "Retrain\nfavours\npopular", fill=RED, tcolor="white")
    arrow(ax, 39, 66, 61, 66, color=RED)
    arrow(ax, 72, 55, 72, 41, color=RED)
    arrow(ax, 61, 30, 39, 30, color=RED)
    arrow(ax, 28, 41, 28, 55, color=RED)
    caption(ax, "The model biases its own future training data. Fix: exploration, position debiasing, hold-outs.")
    save(fig, p("m10_06_feedback_loop.png"))


# ----------------------------------------------------------------------
# 07  Safe rollout ladder
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Safe Rollout — shadow, canary, rollback, kill switch")
    steps = [
        (18, "SHADOW", "New model runs\nbut serves 0%;\ncompare offline", BLUE_F, NAVY),
        (40, "CANARY", "Serve to small\n% of traffic;\nwatch metrics", GREEN_F, GREEN),
        (62, "RAMP UP", "Grow to 100%\nif metrics\nstay healthy", GREEN_F, GREEN),
        (84, "FULL", "New model is\nnow default", ORANGE_F, ORANGE),
    ]
    for x, head, body, f, e in steps:
        box(ax, x, 66, 18, 10, head, fill=e, tcolor="white", size=12)
        box(ax, x, 46, 18, 16, body, fill=f, edge=e, size=10, bold=False)
    for i in range(3):
        arrow(ax, steps[i][0] + 9, 56, steps[i + 1][0] - 9, 56)
    box(ax, 50, 24, 46, 11, "KILL SWITCH / ROLLBACK\nrevert to last good model instantly",
        fill=RED, tcolor="white", size=11)
    arrow(ax, 50, 40, 50, 30, color=RED, dashed=True)
    note(ax, 66, 35, "on any red metric", color=RED, size=10)
    caption(ax, "Never flip 100% at once. Keep the previous model warm so rollback is one click.")
    save(fig, p("m10_07_rollout_safety.png"))


# ----------------------------------------------------------------------
# 08  Incident response runbook
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Production ML Incident — a runbook")
    steps = [
        (80, "1. DETECT", "alert fires: metric / drift / errors", BLUE_F, NAVY),
        (64, "2. STABILISE", "rollback or kill switch first", RED, None),
        (48, "3. TRIAGE", "data? feature? model? infra?", ORANGE_F, ORANGE),
        (32, "4. ROOT CAUSE", "check drift, skew, upstream schema", GREEN_F, GREEN),
        (16, "5. FIX + POSTMORTEM", "patch, add a monitor, write it up", BLUE_F, NAVY),
    ]
    for y, head, body, f, e in steps:
        tc = "white" if f == RED else BLACK
        ee = e if e else RED
        box(ax, 30, y, 30, 11, head, fill=f, edge=ee, tcolor=tc, size=11)
        note(ax, 74, y, body, size=10, ha="center")
    for i in range(4):
        arrow(ax, 30, steps[i][0] - 5.5, 30, steps[i + 1][0] + 5.5)
    caption(ax, "Stop the bleeding first (rollback), diagnose second. Every incident adds a new monitor.")
    save(fig, p("m10_08_incident_runbook.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 10 diagrams generated.")
