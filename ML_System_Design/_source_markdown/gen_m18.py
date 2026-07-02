# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 18 (Responsible & Trustworthy AI).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m18_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Where bias comes from
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Where Bias Comes From — three main sources")
    box(ax, 20, 68, 24, 13, "Data bias\n(who is in the\nsample?)", fill=BLUE_F, size=11)
    box(ax, 50, 68, 24, 13, "Label bias\n(human labels\ncarry prejudice)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 80, 68, 24, 13, "Feedback loop\n(model shapes\nnext data)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 50, 42, 30, 12, "Biased MODEL\n(unfair outcomes)", fill=RED, tcolor="white", size=12)
    arrow(ax, 20, 61, 42, 48)
    arrow(ax, 50, 61, 50, 48)
    arrow(ax, 80, 61, 58, 48)
    # loop back
    arrow(ax, 62, 44, 80, 61, color=RED, dashed=True)
    note(ax, 74, 50, "amplifies", color=RED, size=10)
    caption(ax, "Fix bias at the SOURCE (data + labels), not only at the model — else the loop re-injects it.")
    save(fig, p("m18_01_bias_sources.png"))


# ----------------------------------------------------------------------
# 02  Fairness metrics
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Three Fairness Metrics — what must be equal across groups?")
    box(ax, 20, 66, 24, 16, "Demographic\nparity\nP(Y'=1) equal", fill=BLUE_F, size=11)
    box(ax, 50, 66, 24, 16, "Equal\nopportunity\nTPR equal", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 66, 24, 16, "Equalized\nodds\nTPR & FPR equal", fill=ORANGE_F, edge=ORANGE, size=11)
    note(ax, 20, 44, "Same % positive\nfor each group", size=10)
    note(ax, 50, 44, "Same catch-rate\nfor those who\nqualify", size=10)
    note(ax, 80, 44, "Strongest:\nboth errors\nbalanced", size=10)
    box(ax, 50, 24, 60, 9, "You usually CANNOT satisfy all at once (impossibility)", fill=RED, tcolor="white", size=11)
    caption(ax, "Pick the metric that matches the harm; parity != opportunity != odds.")
    save(fig, p("m18_02_fairness_metrics.png"))


# ----------------------------------------------------------------------
# 03  Mitigation: pre / in / post processing
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Bias Mitigation — three points to intervene")
    box(ax, 18, 60, 20, 12, "Data", fill=BLUE_F)
    box(ax, 50, 60, 20, 12, "Training", fill=GREEN_F, edge=GREEN)
    box(ax, 82, 60, 20, 12, "Predictions", fill=ORANGE_F, edge=ORANGE)
    arrow(ax, 28, 60, 40, 60)
    arrow(ax, 60, 60, 72, 60)
    box(ax, 18, 36, 22, 13, "PRE-process\nre-sample /\nre-weight data", fill=BLUE_F, size=10)
    box(ax, 50, 36, 22, 13, "IN-process\nfairness term\nin the loss", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 82, 36, 22, 13, "POST-process\nadjust thresholds\nper group", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 18, 54, 18, 43)
    arrow(ax, 50, 54, 50, 43)
    arrow(ax, 82, 54, 82, 43)
    caption(ax, "Earlier = more effective but needs data access; post-processing is easy but blunt.")
    save(fig, p("m18_03_mitigations.png"))


# ----------------------------------------------------------------------
# 04  Differential privacy
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Differential Privacy — add noise so no one row shows")
    box(ax, 18, 64, 22, 12, "Real answer\n(query on data)", fill=BLUE_F, size=11)
    box(ax, 50, 64, 20, 12, "Add random\nnoise", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 64, 22, 12, "Noisy answer\n(released)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 29, 64, 40, 64)
    arrow(ax, 60, 64, 71, 64)
    box(ax, 50, 38, 66, 12, "Small epsilon = more noise = more privacy, less accuracy", fill=RED, tcolor="white", size=11)
    note(ax, 50, 24, "Guarantee: adding or removing ONE person\nbarely changes the output", size=11)
    caption(ax, "Epsilon is the privacy budget: it bounds how much any single record can move the result.")
    save(fig, p("m18_04_differential_privacy.png"))


# ----------------------------------------------------------------------
# 05  Federated learning + secure aggregation
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Federated Learning — data stays on the device")
    box(ax, 50, 72, 26, 11, "Central server\n(global model)", fill=NAVY, tcolor="white", size=11)
    box(ax, 18, 40, 20, 12, "Phone A\ntrains locally", fill=BLUE_F, size=10)
    box(ax, 50, 40, 20, 12, "Phone B\ntrains locally", fill=BLUE_F, size=10)
    box(ax, 82, 40, 20, 12, "Phone C\ntrains locally", fill=BLUE_F, size=10)
    # send model down
    arrow(ax, 42, 68, 22, 47, color=GRAY)
    arrow(ax, 50, 66, 50, 47, color=GRAY)
    arrow(ax, 58, 68, 78, 47, color=GRAY)
    # send updates up (not raw data)
    arrow(ax, 24, 46, 44, 68, color=GREEN)
    arrow(ax, 56, 46, 56, 66, color=GREEN)
    arrow(ax, 78, 46, 60, 68, color=GREEN)
    note(ax, 82, 24, "only UPDATES\ngo up, never\nraw data", color=GREEN, size=10)
    box(ax, 30, 22, 30, 9, "Secure aggregation:\nserver sees only the SUM", fill=ORANGE_F, edge=ORANGE, size=10)
    caption(ax, "Gradients/weights are averaged; secure aggregation hides each phone's individual update.")
    save(fig, p("m18_05_federated.png"))


# ----------------------------------------------------------------------
# 06  Explainability: global vs local, which tool
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Explainability — global vs local, which tool?")
    note(ax, 28, 82, "GLOBAL (whole model)", color=NAVY, size=12, bold=True)
    note(ax, 75, 82, "LOCAL (one prediction)", color=RED, size=12, bold=True)
    box(ax, 28, 66, 30, 12, "Feature importance\n(overall drivers)", fill=BLUE_F, size=10)
    box(ax, 28, 48, 30, 12, "SHAP summary\n(averaged)", fill=BLUE_F, size=10)
    box(ax, 75, 66, 30, 12, "LIME\n(local linear fit)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 75, 48, 30, 12, "SHAP values\n(per-row credit)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 50, 28, 40, 11, "Attention: hints for text/images,\nNOT a true explanation", fill=GREEN_F, edge=GREEN, size=10)
    caption(ax, "Global = 'what matters usually'; Local = 'why THIS decision' (needed for appeals/audits).")
    save(fig, p("m18_06_explainability.png"))


# ----------------------------------------------------------------------
# 07  Security: four attacks
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Four Attacks on ML Systems (and where they hit)")
    box(ax, 20, 66, 24, 14, "Data poisoning\ncorrupt TRAINING\ndata", fill=RED, tcolor="white", size=10)
    box(ax, 50, 66, 24, 14, "Evasion\ntrick model at\nINFERENCE", fill=RED, tcolor="white", size=10)
    box(ax, 80, 66, 24, 14, "Model stealing\ncopy model via\nqueries", fill=RED, tcolor="white", size=10)
    box(ax, 35, 40, 24, 14, "Membership\ninference: was I\nin the data?", fill=RED, tcolor="white", size=10)
    box(ax, 68, 40, 26, 14, "Defenses:\nrobust training,\nrate-limit, DP", fill=GREEN_F, edge=GREEN, size=10)
    caption(ax, "Attacks target training (poison), inference (evasion), or the model/data itself (steal, infer).")
    save(fig, p("m18_07_security_attacks.png"))


# ----------------------------------------------------------------------
# 08  Governance: EU AI Act risk tiers
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Governance — EU AI Act risk tiers")
    box(ax, 50, 74, 34, 10, "UNACCEPTABLE\n(banned: social scoring)", fill=RED, tcolor="white", size=11)
    box(ax, 50, 60, 40, 10, "HIGH RISK\n(credit, hiring: strict duties)", fill=ORANGE, tcolor="white", size=11)
    box(ax, 50, 46, 46, 10, "LIMITED RISK\n(chatbots: disclose it's AI)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 50, 32, 52, 10, "MINIMAL RISK\n(spam filter: no extra rules)", fill=GREEN_F, edge=GREEN, size=11)
    note(ax, 50, 20, "Also: model cards, datasheets, audit logs, GDPR right-to-explanation", size=11)
    caption(ax, "More potential harm = more legal duties. Finance/hiring models are usually HIGH risk.")
    save(fig, p("m18_08_governance.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 18 diagrams generated.")
