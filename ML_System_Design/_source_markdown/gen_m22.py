# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 22 (Revision, Cheat Sheets & Roadmap).
Reuses viz_style.py helpers (same Office palette as the rest of the course).
Outputs into ../images/ as m22_*.png at 150 dpi on white.
KEEP IT SIMPLE: <=10 boxes per diagram, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)

def spoke(ax, cx, cy, x, y, pull=9.0):
    """Draw an arrow from a hub centre toward a box, stopping short of the box."""
    import math
    dx, dy = x - cx, y - cy
    d = math.hypot(dx, dy)
    x2 = x - dx / d * pull
    y2 = y - dy / d * pull
    arrow(ax, cx, cy, x2, y2, color=GRAY)


# ----------------------------------------------------------------------
# 01  The "ML System Design in 60 seconds" framework card (7 steps)
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "ML System Design in 60 Seconds — the 7-step card")
    # top row: steps 1-4
    r1 = [
        (15, 68, "1. Clarify\n& scope", BLUE_F, NAVY),
        (38, 68, "2. Frame the\nML problem", GREEN_F, GREEN),
        (61, 68, "3. Data\n& labels", BLUE_F, NAVY),
        (84, 68, "4. Features", GREEN_F, GREEN),
    ]
    for x, y, t, f, e in r1:
        box(ax, x, y, 19, 12, t, fill=f, edge=e, size=11)
    for a in range(3):
        arrow(ax, r1[a][0] + 9.5, 68, r1[a+1][0] - 9.5, 68)
    # connector down
    arrow(ax, 84, 62, 73, 46, color=NAVY)
    # bottom row: steps 5-7
    r2 = [
        (73, 40, "5. Model\n& loss", ORANGE_F, ORANGE),
        (50, 40, "6. Evaluate\n(metric + A/B)", ORANGE_F, ORANGE),
        (27, 40, "7. Serve, scale,\nmonitor", BLUE_F, NAVY),
    ]
    for x, y, t, f, e in r2:
        box(ax, x, y, 20, 12, t, fill=f, edge=e, size=11)
    arrow(ax, r2[0][0] - 10, 40, r2[1][0] + 10, 40)
    arrow(ax, r2[1][0] - 10, 40, r2[2][0] + 10, 40)
    # feedback loop back to data
    arrow(ax, 27, 34, 27, 21, color=RED, dashed=True)
    arrow(ax, 30, 18, 40, 18, color=RED, dashed=True)
    box(ax, 62, 18, 30, 8, "monitoring -> retrain", fill="white", edge=RED, size=10)
    caption(ax, "Say this out loud in the first minute of ANY ML design interview.")
    save(fig, p("m22_01_framework_card.png"))


# ----------------------------------------------------------------------
# 02  Metric-selection flowchart: task -> metric
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Pick the Metric — task decides the number you optimise")
    box(ax, 50, 82, 30, 9, "What is the task?", fill=ORANGE_F, edge=ORANGE, size=12)
    tasks = [
        (16, "Classification", BLUE_F, NAVY),
        (39, "Regression", GREEN_F, GREEN),
        (62, "Ranking /\nReco", BLUE_F, NAVY),
        (85, "LLM /\nGenerative", ORANGE_F, ORANGE),
    ]
    for x, t, f, e in tasks:
        box(ax, x, 60, 19, 11, t, fill=f, edge=e, size=11)
        arrow(ax, 50, 77, x, 66)
    metrics = [
        (16, "Precision/Recall\nF1, PR-AUC,\nROC-AUC"),
        (39, "RMSE, MAE,\nMAPE, R^2"),
        (62, "NDCG, MAP,\nRecall@K, MRR"),
        (85, "Human eval,\nLLM-as-judge,\nROUGE/BLEU"),
    ]
    for x, t in metrics:
        box(ax, x, 34, 19, 15, t, fill="white", edge=GRAY, size=10, bold=False)
        arrow(ax, x, 54, x, 42)
    caption(ax, "Then map to a BUSINESS metric (revenue, retention) and confirm with an online A/B test.")
    save(fig, p("m22_02_metric_selector.png"))


# ----------------------------------------------------------------------
# 03  Decision tree: batch vs online vs streaming
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Batch vs Online vs Streaming — how to choose")
    box(ax, 50, 82, 42, 9, "Must the prediction reflect\nwhat just happened?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 22, 60, 24, 10, "BATCH\n(scheduled, cheap)", fill=BLUE_F, edge=NAVY, size=11)
    arrow(ax, 40, 79, 25, 65); note(ax, 27, 73, "no", color=NAVY, size=10)
    box(ax, 68, 60, 40, 9, "React to a stream\nof events (Kafka/Flink)?", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 60, 79, 68, 65); note(ax, 66, 73, "yes", color=GREEN, size=10)
    box(ax, 50, 36, 24, 10, "ONLINE\n(per-request, ms)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 60, 55, 52, 41); note(ax, 52, 49, "no", color=NAVY, size=10)
    box(ax, 84, 36, 24, 10, "STREAMING\n(event-driven)", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 76, 55, 84, 41); note(ax, 84, 49, "yes", color=GREEN, size=10)
    caption(ax, "Big systems go HYBRID: precompute candidates in batch, then re-rank online per request.")
    save(fig, p("m22_03_batch_vs_online.png"))


# ----------------------------------------------------------------------
# 04  Decision tree: prompt vs RAG vs fine-tune
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Prompt vs RAG vs Fine-tune — the LLM decision")
    box(ax, 50, 83, 44, 9, "Does the task need external or\nfast-changing knowledge?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 20, 60, 24, 10, "RAG\n(retrieve + prompt)", fill=BLUE_F, edge=NAVY, size=11)
    arrow(ax, 38, 80, 23, 65); note(ax, 26, 73, "yes", color=GREEN, size=10)
    box(ax, 66, 60, 42, 9, "Need new skill, style,\nor strict output format?", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 60, 80, 66, 65); note(ax, 63, 73, "no", color=NAVY, size=10)
    box(ax, 48, 34, 26, 10, "PROMPTING\n(few-shot / instructions)", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 58, 55, 50, 40); note(ax, 51, 48, "no", color=NAVY, size=10)
    box(ax, 84, 34, 24, 10, "FINE-TUNE\n(LoRA / SFT)", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 76, 55, 84, 40); note(ax, 84, 48, "yes", color=GREEN, size=10)
    caption(ax, "Cost & speed order: Prompt < RAG < Fine-tune. Always try the cheaper option first.")
    save(fig, p("m22_04_rag_vs_finetune.png"))


# ----------------------------------------------------------------------
# 05  Decision tree: GBDT vs DNN
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "GBDT vs Deep Net — pick the model family")
    box(ax, 50, 83, 40, 9, "Is the data mostly\ntabular / structured?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 22, 58, 26, 11, "GBDT\n(XGBoost /\nLightGBM)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 40, 80, 25, 64); note(ax, 28, 72, "yes", color=GREEN, size=10)
    box(ax, 70, 60, 42, 9, "Unstructured (text/image/\naudio) or huge data?", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 60, 80, 70, 65); note(ax, 66, 73, "no", color=NAVY, size=10)
    box(ax, 52, 34, 26, 10, "GBDT baseline\nfirst, then tune", fill=BLUE_F, edge=NAVY, size=10)
    arrow(ax, 62, 55, 54, 40); note(ax, 55, 48, "no", color=NAVY, size=10)
    box(ax, 84, 34, 24, 11, "DEEP NET\n(CNN / RNN /\nTransformer)", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 76, 55, 84, 41); note(ax, 84, 49, "yes", color=GREEN, size=10)
    caption(ax, "GBDT usually wins on tabular data; deep nets win on unstructured data and at massive scale.")
    save(fig, p("m22_05_gbdt_vs_dnn.png"))


# ----------------------------------------------------------------------
# 06  Decision tree: when to use ML at all
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "When to Use ML at All — say NO when you can")
    box(ax, 42, 84, 40, 9, "Does a simple rule\nsolve it well?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 84, 22, 9, "Use RULES,\nnot ML", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 62, 84, 71, 84); note(ax, 67, 88, "yes", color=GREEN, size=10)
    box(ax, 42, 62, 42, 9, "Pattern exists AND\nenough data?", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 42, 79, 42, 67); note(ax, 36, 73, "no", color=NAVY, size=10)
    box(ax, 82, 62, 22, 9, "Not ready\nfor ML", fill=RED, tcolor="white", size=10)
    arrow(ax, 63, 62, 71, 62); note(ax, 67, 66, "no", color=RED, size=10)
    box(ax, 42, 40, 42, 9, "Can tolerate error AND\nmeasure success?", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 42, 57, 42, 45); note(ax, 36, 51, "yes", color=NAVY, size=10)
    box(ax, 82, 40, 22, 9, "Add human /\nrethink", fill=RED, tcolor="white", size=10)
    arrow(ax, 63, 40, 71, 40); note(ax, 67, 44, "no", color=RED, size=10)
    box(ax, 42, 20, 28, 10, "USE ML", fill=GREEN, tcolor="white", size=13)
    arrow(ax, 42, 35, 42, 25); note(ax, 36, 30, "yes", color=NAVY, size=10)
    caption(ax, "ML earns its complexity only when rules fail, data exists, and some error is acceptable.")
    save(fig, p("m22_06_when_ml.png"))


# ----------------------------------------------------------------------
# 07  Course mind map — Part 1 (the core pipeline, M1-M11)
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Course Mind Map (1/2) — the core ML pipeline")
    circle(ax, 50, 52, 13, "ML System\nDesign\nCORE", fill=ORANGE, edge=RED, tcolor="white", size=12)
    spokes = [
        (18, 78, "Foundations &\nFraming (M1-3)", BLUE_F, NAVY),
        (82, 78, "Data &\nFeatures (M4-5)", GREEN_F, GREEN),
        (86, 40, "Train &\nEvaluate (M6-7)", BLUE_F, NAVY),
        (50, 20, "Serving &\nInference (M8)", GREEN_F, GREEN),
        (14, 40, "MLOps, Monitor,\nScale (M9-11)", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in spokes:
        box(ax, x, y, 24, 12, t, fill=f, edge=e, size=10)
        spoke(ax, 50, 52, x, y, pull=14)
    caption(ax, "Every core module slots into one stage of the Module-1 lifecycle loop.")
    save(fig, p("m22_07_mindmap_core.png"))


# ----------------------------------------------------------------------
# 08  Course mind map — Part 2 (applications & advanced, M12-M21)
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Course Mind Map (2/2) — applications & advanced")
    circle(ax, 50, 52, 13, "APPLIED\n& ADVANCED", fill=NAVY, edge=NAVY, tcolor="white", size=12)
    spokes = [
        (17, 78, "Reco & Search\n(M12-14)", BLUE_F, NAVY),
        (50, 82, "LLM, RAG,\nFine-tune (M15-17)", ORANGE_F, ORANGE),
        (84, 78, "Responsible AI\n(M18)", GREEN_F, GREEN),
        (86, 38, "Systems\nFoundations (M19)", BLUE_F, NAVY),
        (50, 20, "CV & Multimodal\n(M20)", GREEN_F, GREEN),
        (14, 38, "Ads, Fraud,\nAnomaly (M21)", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in spokes:
        box(ax, x, y, 25, 12, t, fill=f, edge=e, size=10)
        spoke(ax, 50, 52, x, y, pull=14)
    caption(ax, "Applications reuse the core: retrieve-then-rank, two-tower, funnels, and the feedback loop.")
    save(fig, p("m22_08_mindmap_applied.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 22 diagrams generated.")
