# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 4 (Data Engineering for ML).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m04_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Batch vs Streaming ingestion architecture
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Ingestion: Batch vs Streaming")
    # Batch (top row)
    note(ax, 12, 82, "BATCH", color=NAVY, size=13, bold=True)
    box(ax, 20, 68, 20, 11, "Sources\n(DBs, files,\nlogs)", fill=BLUE_F)
    box(ax, 50, 68, 20, 11, "Scheduled\nload\n(hourly/daily)", fill=ORANGE_F, edge=ORANGE)
    box(ax, 82, 68, 20, 11, "Warehouse\n/ lake", fill=GREEN_F, edge=GREEN)
    arrow(ax, 30, 68, 40, 68)
    arrow(ax, 60, 68, 72, 68)
    # Streaming (bottom row)
    note(ax, 12, 40, "STREAMING", color=RED, size=13, bold=True)
    box(ax, 20, 26, 20, 11, "Events\n(clicks,\ntxns)", fill=BLUE_F)
    box(ax, 50, 26, 20, 11, "Message bus\n(Kafka/Kinesis\n/Pub-Sub)", fill=ORANGE_F, edge=ORANGE)
    box(ax, 82, 26, 20, 11, "Consumers\n(features,\nmodel)", fill=GREEN_F, edge=GREEN)
    arrow(ax, 30, 26, 40, 26)
    arrow(ax, 60, 26, 72, 26)
    caption(ax, "Batch = big chunks on a schedule (high latency, cheap). Streaming = event-by-event (fresh, complex).")
    save(fig, p("m04_01_batch_vs_stream.png"))


# ----------------------------------------------------------------------
# 02  Pipeline orchestration (Airflow DAG) + batch vs stream engines
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Pipeline Orchestration — a DAG of tasks")
    box(ax, 15, 62, 18, 11, "Extract\n(ingest)", fill=BLUE_F)
    box(ax, 40, 62, 18, 11, "Clean /\nValidate", fill=ORANGE_F, edge=ORANGE)
    box(ax, 65, 74, 18, 11, "Build\nFeatures", fill=GREEN_F, edge=GREEN)
    box(ax, 65, 50, 18, 11, "Aggregate", fill=GREEN_F, edge=GREEN)
    box(ax, 88, 62, 18, 11, "Load /\nTrain", fill=BLUE_F)
    arrow(ax, 24, 62, 31, 62)
    arrow(ax, 49, 62, 56, 68)
    arrow(ax, 49, 62, 56, 55)
    arrow(ax, 74, 74, 81, 66)
    arrow(ax, 74, 50, 81, 58)
    note(ax, 40, 40, "Airflow / Kubeflow schedule + retry + monitor this DAG",
         color=NAVY, size=11, bold=True)
    note(ax, 30, 30, "Batch engines: Spark, Beam", color=GRAY, size=11)
    note(ax, 72, 30, "Stream engines: Flink, Beam", color=GRAY, size=11)
    caption(ax, "Orchestrators run tasks in dependency order, retry failures, and alert on breakage.")
    save(fig, p("m04_02_orchestration_dag.png"))


# ----------------------------------------------------------------------
# 03  Lake vs Warehouse vs Lakehouse
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Data Lake vs Warehouse vs Lakehouse")
    cols = [
        (20, "DATA LAKE", "Raw, any format\n(S3, HDFS).\nCheap, schema\n-on-read", BLUE_F, NAVY),
        (50, "WAREHOUSE", "Structured,\nschema-on-write\n(BigQuery,\nSnowflake). Fast SQL", GREEN_F, GREEN),
        (80, "LAKEHOUSE", "Lake + ACID +\nschema\n(Delta Lake).\nBest of both", ORANGE_F, ORANGE),
    ]
    for x, head, body, f, e in cols:
        box(ax, x, 70, 24, 11, head, fill=e, tcolor="white", size=12)
        box(ax, x, 46, 24, 22, body, fill=f, edge=e, size=10, bold=False)
    note(ax, 20, 28, "store first,\nstructure later", size=10)
    note(ax, 50, 28, "clean, queryable,\ngoverned", size=10)
    note(ax, 80, 28, "cheap storage +\nreliable tables", size=10)
    caption(ax, "Lake = cheap raw dump. Warehouse = clean SQL. Lakehouse = one system that does both.")
    save(fig, p("m04_03_storage_tiers.png"))


# ----------------------------------------------------------------------
# 04  Data labeling approaches
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Getting Labels — four approaches")
    box(ax, 20, 68, 22, 13, "Human\nlabeling", fill=BLUE_F, size=11)
    box(ax, 50, 68, 22, 13, "Weak\nsupervision\n(Snorkel)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 80, 68, 22, 13, "Active\nlearning", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 35, 40, 22, 13, "Programmatic\n/ heuristic\nrules", fill=BLUE_F, size=11)
    box(ax, 65, 40, 22, 13, "Semi-\nsupervised", fill=GREEN_F, edge=GREEN, size=11)
    note(ax, 20, 55, "accurate,\nslow, costly", size=10)
    note(ax, 50, 55, "noisy rules\ncombined", size=10)
    note(ax, 80, 55, "label only the\nhard cases", size=10)
    note(ax, 35, 27, "label functions", size=10)
    note(ax, 65, 27, "few labels +\nmany unlabeled", size=10)
    caption(ax, "Trade cost vs quality vs speed: humans are gold but slow; weak/programmatic labels scale cheaply.")
    save(fig, p("m04_04_labeling.png"))


# ----------------------------------------------------------------------
# 05  Data quality & validation gate
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Data Validation — a gate before training")
    box(ax, 15, 60, 18, 11, "Incoming\ndata", fill=BLUE_F)
    box(ax, 45, 60, 22, 13, "Validation\n(Great Expect.\n/ TFDV)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 80, 74, 18, 11, "PASS ->\ntrain", fill=GREEN, tcolor="white", size=11)
    box(ax, 80, 46, 18, 11, "FAIL ->\nalert/stop", fill=RED, tcolor="white", size=11)
    arrow(ax, 24, 60, 34, 60)
    arrow(ax, 56, 63, 71, 72, color=GREEN)
    arrow(ax, 56, 57, 71, 48, color=RED)
    note(ax, 45, 40, "Checks: schema, types, ranges,\nnulls, distribution drift, uniqueness",
         color=NAVY, size=11, bold=True)
    caption(ax, "Catch bad data at the door: a silent schema change is the #1 cause of production ML bugs.")
    save(fig, p("m04_05_validation.png"))


# ----------------------------------------------------------------------
# 06  Class imbalance & fixes
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Class Imbalance — problem and fixes")
    # imbalance bar picture
    note(ax, 25, 80, "Problem: 99% vs 1%", color=RED, size=12, bold=True)
    box(ax, 25, 66, 34, 10, "Majority (negatives) 99%", fill=BLUE_F, size=10)
    box(ax, 16, 54, 16, 8, "Minority 1%", fill=RED, tcolor="white", size=9)
    note(ax, 25, 44, "Model can score 99% by\nalways saying 'no'", color=GRAY, size=10)
    # fixes
    note(ax, 75, 80, "Fixes", color=GREEN, size=12, bold=True)
    box(ax, 75, 68, 30, 9, "Oversample minority /\nundersample majority", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 75, 54, 30, 9, "Class weights in loss", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 75, 40, 30, 9, "Negative sampling\n(retrieval)", fill=GREEN_F, edge=GREEN, size=10)
    caption(ax, "Accuracy lies under imbalance. Rebalance data, weight the loss, or use PR-AUC / F1 instead.")
    save(fig, p("m04_06_imbalance.png"))


# ----------------------------------------------------------------------
# 07  Data versioning & lineage
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Data Versioning & Lineage — reproducibility")
    box(ax, 18, 60, 20, 11, "Dataset v1", fill=BLUE_F)
    box(ax, 50, 60, 20, 11, "Dataset v2", fill=BLUE_F)
    box(ax, 82, 60, 20, 11, "Dataset v3", fill=BLUE_F)
    arrow(ax, 28, 60, 40, 60)
    arrow(ax, 60, 60, 72, 60)
    box(ax, 50, 34, 46, 12, "Tools: DVC, lakeFS, Delta time-travel\npin data + code + model together",
        fill=ORANGE_F, edge=ORANGE, size=11)
    note(ax, 18, 46, "each commit\ntracked", color=GRAY, size=10)
    caption(ax, "Version data like code so any past model can be reproduced, audited, and rolled back.")
    save(fig, p("m04_07_versioning.png"))


# ----------------------------------------------------------------------
# 08  Privacy-aware data handling
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Privacy-Aware Data (PII, GDPR)")
    box(ax, 20, 66, 20, 12, "Raw data\nwith PII\n(name, PAN)", fill=RED, tcolor="white", size=10)
    box(ax, 52, 66, 22, 12, "Protect:\nmask / hash /\nanonymize", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 84, 66, 20, 12, "Safe to\ntrain / share", fill=GREEN, tcolor="white", size=10)
    arrow(ax, 30, 66, 41, 66)
    arrow(ax, 63, 66, 74, 66)
    note(ax, 50, 42, "Principles: minimize, consent, purpose-limit,\nright-to-be-forgotten, access control, audit",
         color=NAVY, size=11, bold=True)
    note(ax, 50, 30, "Exam value: SEBI / RBI data-protection rules, GDPR, DPDP Act",
         color=RED, size=11, bold=True)
    caption(ax, "Never train on raw PII. Anonymize early; log who accessed what; honor deletion requests.")
    save(fig, p("m04_08_privacy.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 4 diagrams generated.")
