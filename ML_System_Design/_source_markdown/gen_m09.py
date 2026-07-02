# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 9 (ML Infrastructure & MLOps).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m09_*.png at 150 dpi on white.
KEEP DIAGRAMS SIMPLE: <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The MLOps maturity ladder
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The MLOps Maturity Ladder — climb one rung at a time")
    # three rising steps (a staircase)
    steps = [
        (24, 38, "Level 0\nMANUAL", "Notebooks by hand\nDeploy by hand\nNo monitoring", BLUE_F, NAVY),
        (50, 56, "Level 1\nAUTOMATED\nTRAINING", "Reusable pipeline\nAuto retrain\nModel registry", ORANGE_F, ORANGE),
        (76, 74, "Level 2\nCI/CD/CT", "Tests + auto deploy\nContinuous training\nFull monitoring", GREEN_F, GREEN),
    ]
    for x, y, head, body, f, e in steps:
        box(ax, x, y, 20, 12, head, fill=e, tcolor="white", size=11)
        box(ax, x, y - 16, 20, 13, body, fill=f, edge=e, size=10, bold=False)
    arrow(ax, 34, 41, 40, 53, color=NAVY)
    arrow(ax, 60, 59, 66, 71, color=NAVY)
    note(ax, 15, 82, "more\nautomation ->", color=RED, size=11, bold=True)
    caption(ax, "Higher rungs = less manual toil, faster & safer releases. Most teams start at Level 0.")
    save(fig, p("m09_01_maturity_ladder.png"))


# ----------------------------------------------------------------------
# 02  Experiment tracking
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Experiment Tracking — log every run so you can compare")
    box(ax, 20, 66, 22, 12, "Training run\n(code + config)", fill=BLUE_F)
    box(ax, 55, 66, 24, 14, "Tracking server\n(MLflow / W&B)", fill=ORANGE, edge=RED, tcolor="white", size=11)
    arrow(ax, 31, 66, 43, 66)
    note(ax, 37, 71, "logs", color=NAVY, size=10)
    # logged items
    items = [
        (22, 34, "Params\n(lr, depth)"),
        (44, 34, "Metrics\n(acc, loss)"),
        (66, 34, "Artifacts\n(model file)"),
        (86, 34, "Code + data\nversion"),
    ]
    for x, y, t in items:
        box(ax, x, y, 18, 12, t, fill=GREEN_F, edge=GREEN, size=10, bold=False)
    for x, _, _ in items:
        arrow(ax, 55, 59, x, 41, color=GRAY)
    caption(ax, "Every run is recorded -> compare experiments, reproduce the best, share with the team.")
    save(fig, p("m09_02_experiment_tracking.png"))


# ----------------------------------------------------------------------
# 03  Model registry & versioning (lifecycle stages)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Model Registry — one home, versioned stages")
    box(ax, 15, 60, 18, 12, "Trained\nmodel v3", fill=BLUE_F, size=11)
    stages = [
        (40, 60, "STAGING\n(test)", ORANGE_F, ORANGE),
        (64, 60, "PRODUCTION\n(serving)", GREEN_F, GREEN),
        (88, 60, "ARCHIVED\n(rollback)", BLUE_F, NAVY),
    ]
    for x, y, t, f, e in stages:
        box(ax, x, y, 18, 12, t, fill=f, edge=e, size=11)
    arrow(ax, 24, 60, 31, 60); note(ax, 27, 65, "register", size=9)
    arrow(ax, 49, 60, 55, 60); note(ax, 52, 65, "promote", size=9)
    arrow(ax, 73, 60, 79, 60); note(ax, 76, 65, "retire", size=9)
    # rollback arrow
    arrow(ax, 88, 54, 64, 54, color=RED, dashed=True)
    note(ax, 76, 49, "rollback if bad", color=RED, size=10, bold=True)
    caption(ax, "Registry tracks versions + stage + lineage. Promote good models, roll back bad ones fast.")
    save(fig, p("m09_03_model_registry.png"))


# ----------------------------------------------------------------------
# 04  CI/CD/CT pipeline for ML
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "CI / CD / CT — three loops that keep ML fresh")
    row = [
        (15, "Code\ncommit", BLUE_F, NAVY),
        (37, "CI\ntest + build", ORANGE_F, ORANGE),
        (59, "CD\ndeploy", GREEN_F, GREEN),
        (83, "Serve\nin prod", BLUE_F, NAVY),
    ]
    for x, t, f, e in row:
        box(ax, x, 60, 18, 12, t, fill=f, edge=e, size=11)
    arrow(ax, 24, 60, 28, 60)
    arrow(ax, 46, 60, 50, 60)
    arrow(ax, 68, 60, 74, 60)
    # CT loop: monitoring -> retrain -> back to CI
    box(ax, 59, 30, 20, 12, "CT: new data\ntriggers retrain", fill=RED, tcolor="white", size=10)
    arrow(ax, 83, 54, 69, 36, color=RED, dashed=True)
    arrow(ax, 49, 32, 37, 54, color=RED, dashed=True)
    caption(ax, "CI = test code. CD = ship model. CT = auto-retrain when data drifts. The ML-only loop is CT.")
    save(fig, p("m09_04_cicd_ct.png"))


# ----------------------------------------------------------------------
# 05  Reproducibility — pin data + code + env
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Reproducibility — pin all THREE or it won't reproduce")
    circle(ax, 30, 58, 13, "CODE\n(git SHA)", fill=BLUE_F)
    circle(ax, 70, 58, 13, "DATA\n(version /\nhash)", fill=GREEN_F, edge=GREEN)
    circle(ax, 50, 32, 13, "ENV\n(container\n+ seed)", fill=ORANGE_F, edge=ORANGE)
    box(ax, 50, 58, 14, 10, "SAME\nMODEL", fill=RED, tcolor="white", size=11)
    caption(ax, "Pin code + data + environment (and random seed). Miss any one and results silently differ.")
    save(fig, p("m09_05_reproducibility.png"))


# ----------------------------------------------------------------------
# 06  Orchestration — a pipeline DAG
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Orchestration — a pipeline is a DAG of steps")
    box(ax, 14, 60, 16, 12, "Ingest\ndata", fill=BLUE_F, size=11)
    box(ax, 36, 60, 16, 12, "Validate\n+ features", fill=BLUE_F, size=11)
    box(ax, 58, 72, 16, 12, "Train\nmodel", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 58, 44, 16, 12, "Evaluate", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 84, 60, 16, 12, "Register\nmodel", fill=GREEN, tcolor="white", size=11)
    arrow(ax, 22, 60, 28, 60)
    arrow(ax, 44, 62, 50, 70)
    arrow(ax, 44, 58, 50, 46)
    arrow(ax, 66, 70, 76, 62)
    arrow(ax, 66, 46, 76, 58)
    note(ax, 50, 24, "Kubeflow · Metaflow · TFX · Vertex · SageMaker Pipelines",
         color=NAVY, size=11, bold=True)
    caption(ax, "An orchestrator runs each step in order, retries failures, and reruns only what changed.")
    save(fig, p("m09_06_orchestration.png"))


# ----------------------------------------------------------------------
# 07  Containerization & Kubernetes for ML
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Containers + Kubernetes — package once, scale anywhere")
    box(ax, 22, 68, 24, 14, "Container image\n(code+env+libs)", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 34, 68, 44, 68); note(ax, 39, 73, "run on", size=9)
    box(ax, 62, 68, 26, 14, "Kubernetes\ncluster", fill=NAVY, tcolor="white", size=12)
    # pods on GPUs
    pods = [(40, 34, "Train pod\n(GPU)"), (62, 34, "Serving pod"), (84, 34, "Serving pod")]
    for x, y, t in pods:
        box(ax, x, y, 18, 12, t, fill=GREEN_F, edge=GREEN, size=10, bold=False)
    for x, _, _ in pods:
        arrow(ax, 62, 61, x, 41, color=GRAY)
    note(ax, 18, 34, "autoscale\n+ heal", color=RED, size=10, bold=True)
    caption(ax, "One image runs identically everywhere; K8s schedules pods, autoscales, and restarts crashes.")
    save(fig, p("m09_07_k8s.png"))


# ----------------------------------------------------------------------
# 08  Platform case-study comparison
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "ML Platforms — same idea, different flavours")
    plats = [
        (20, "Uber\nMichelangelo", "End-to-end,\nfeature store\nfirst", BLUE_F, NAVY),
        (43, "Netflix\nMetaflow", "Data-scientist\nfriendly,\nPython DAGs", GREEN_F, GREEN),
        (66, "Meta\nFBLearner", "Reusable\nworkflows at\nhuge scale", ORANGE_F, ORANGE),
        (88, "Google\nTFX", "Production\npipelines on\nTensorflow", BLUE_F, NAVY),
    ]
    for x, head, body, f, e in plats:
        box(ax, x, 66, 19, 13, head, fill=e, tcolor="white", size=10)
        box(ax, x, 42, 19, 18, body, fill=f, edge=e, size=9, bold=False)
    caption(ax, "All solve the same job: pipelines + feature store + registry + serving + monitoring.")
    save(fig, p("m09_08_platforms.png"))


# ----------------------------------------------------------------------
# 09  End-to-end MLOps architecture (the money diagram)
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "End-to-End MLOps Architecture — training to monitoring")
    box(ax, 16, 70, 18, 12, "Data +\nFeature store", fill=BLUE_F, size=10)
    box(ax, 42, 70, 18, 12, "Training\npipeline", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 68, 70, 18, 12, "Model\nregistry", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 68, 42, 18, 12, "CI/CD\ndeploy", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 42, 42, 18, 12, "Serving\nAPI", fill=GREEN, tcolor="white", size=10)
    box(ax, 16, 42, 18, 12, "Monitoring\n(drift/latency)", fill=RED, tcolor="white", size=9)
    arrow(ax, 25, 70, 33, 70)
    arrow(ax, 51, 70, 59, 70)
    arrow(ax, 68, 64, 68, 48)
    arrow(ax, 59, 42, 51, 42)
    arrow(ax, 33, 42, 25, 42)
    # feedback: monitoring back to data/training
    arrow(ax, 16, 48, 16, 64, color=RED, dashed=True)
    note(ax, 8, 56, "retrain\nfeedback", color=RED, size=9, bold=True)
    caption(ax, "The full loop: data -> train -> registry -> deploy -> serve -> monitor -> back to training.")
    save(fig, p("m09_09_e2e_architecture.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09()
    print("All Module 9 diagrams generated.")
