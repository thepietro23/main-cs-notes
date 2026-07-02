# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 5
(Feature Engineering & Feature Stores).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m05_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The six feature types
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Six Kinds of Features a Model Can Eat")
    cells = [
        (20, 64, "NUMERICAL", "age, price\n(a number)", BLUE_F, NAVY),
        (50, 64, "CATEGORICAL", "country, colour\n(a label)", GREEN_F, GREEN),
        (80, 64, "TEXT", "reviews, titles\n(words)", ORANGE_F, ORANGE),
        (20, 36, "IMAGE", "photos, frames\n(pixels)", BLUE_F, NAVY),
        (50, 36, "TEMPORAL", "day, hour,\ntime-since-last", GREEN_F, GREEN),
        (80, 36, "CROSS", "combine two\n(city x hour)", ORANGE_F, ORANGE),
    ]
    for x, y, head, body, f, e in cells:
        box(ax, x, y + 7, 24, 9, head, fill=e, tcolor="white", size=12)
        box(ax, x, y - 5, 24, 12, body, fill=f, edge=e, size=11, bold=False)
    caption(ax, "Every raw signal must become a NUMBER before a model can use it.")
    save(fig, p("m05_01_feature_types.png"))


# ----------------------------------------------------------------------
# 02  One-hot encoding vs the hashing trick
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "One-Hot Encoding vs the Hashing Trick")
    # One-hot (left)
    note(ax, 27, 84, "One-hot", color=NAVY, size=13, bold=True)
    box(ax, 27, 72, 26, 10, "colour = 'green'", fill=BLUE_F, size=11)
    box(ax, 27, 52, 30, 14, "[0, 1, 0, 0]\none slot per\nknown value", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    arrow(ax, 27, 67, 27, 59)
    note(ax, 27, 34, "exact, but blows up\nif millions of values", color=RED, size=10)
    # Hashing (right)
    note(ax, 73, 84, "Hashing trick", color=ORANGE, size=13, bold=True)
    box(ax, 73, 72, 26, 10, "id = 'user_9F2'", fill=BLUE_F, size=11)
    box(ax, 73, 52, 30, 14, "hash() mod K\n-> bucket 3 of K\nfixed-size vector", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 73, 67, 73, 59)
    note(ax, 73, 34, "fixed memory, no\nvocab; rare collisions", color=GREEN, size=10)
    caption(ax, "One-hot = one column per value. Hashing = squash any value into K fixed buckets.")
    save(fig, p("m05_02_onehot_hashing.png"))


# ----------------------------------------------------------------------
# 03  Normalization: which models care?
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Does Feature Scaling Matter? Depends on the Model")
    note(ax, 28, 82, "SCALE-SENSITIVE", color=RED, size=13, bold=True)
    note(ax, 74, 82, "SCALE-INVARIANT", color=GREEN, size=13, bold=True)
    left = ["Linear / Logistic\nRegression", "SVM / KNN\n(use distances)", "Neural Networks\n(gradient descent)"]
    right = ["Decision Trees", "Random Forest", "Gradient-Boosted\nTrees (XGBoost)"]
    for i, t in enumerate(left):
        box(ax, 28, 68 - i*17, 32, 12, t, fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    for i, t in enumerate(right):
        box(ax, 74, 68 - i*17, 32, 12, t, fill=GREEN_F, edge=GREEN, size=11, bold=False)
    note(ax, 28, 16, "MUST scale features", color=RED, size=11, bold=True)
    note(ax, 74, 16, "splits ignore scale", color=GREEN, size=11, bold=True)
    caption(ax, "Distance & gradient models need scaling; trees split on order, so scale is irrelevant.")
    save(fig, p("m05_03_normalization.png"))


# ----------------------------------------------------------------------
# 04  Sparse one-hot vs dense embedding
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Embeddings: Dense Vectors Instead of Sparse One-Hots")
    box(ax, 20, 68, 24, 11, "movie_id\n= 51,204", fill=BLUE_F, size=11)
    # sparse
    box(ax, 55, 78, 40, 12, "[0,0,...,1,...,0]\n1 million slots, all zero but one", fill=ORANGE_F, edge=RED, size=10, bold=False)
    note(ax, 55, 68, "SPARSE: huge, wasteful,\nno notion of 'similar'", color=RED, size=10)
    # dense
    box(ax, 55, 52, 40, 12, "[0.3, -0.8, 0.1, 0.6]\nlearned 4-dim vector", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    note(ax, 55, 42, "DENSE: small, similar items\nsit close together", color=GREEN, size=10)
    arrow(ax, 32, 70, 34, 78, color=RED)
    arrow(ax, 32, 66, 34, 54, color=GREEN)
    caption(ax, "An embedding maps each id to a short learned vector; nearby vectors = similar things.")
    save(fig, p("m05_04_embeddings.png"))


# ----------------------------------------------------------------------
# 05  Feature crosses
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Feature Crosses — Teaching a Linear Model Interactions")
    box(ax, 22, 70, 26, 12, "day_of_week\n= Saturday", fill=BLUE_F, size=11)
    box(ax, 22, 44, 26, 12, "hour\n= 8 pm", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 60, 57, 20, 12, "CROSS\n(combine)", fill=ORANGE, tcolor="white", size=12)
    box(ax, 88, 57, 24, 14, "'Sat & 8pm'\nas one\nnew feature", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 35, 68, 50, 60)
    arrow(ax, 35, 46, 50, 54)
    arrow(ax, 70, 57, 76, 57)
    caption(ax, "A cross lets a simple model learn 'Saturday nights are special' — an interaction it could not see alone.")
    save(fig, p("m05_05_feature_cross.png"))


# ----------------------------------------------------------------------
# 06  Training-serving skew (the centrepiece)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Training-Serving Skew — the Silent Killer")
    # training path
    note(ax, 25, 84, "TRAINING (offline)", color=NAVY, size=12, bold=True)
    box(ax, 25, 72, 30, 11, "Batch pipeline\n(SQL / Spark)", fill=BLUE_F, size=11)
    box(ax, 25, 54, 30, 11, "avg_spend =\nmean over 90 days", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 25, 66, 25, 60)
    # serving path
    note(ax, 75, 84, "SERVING (online)", color=NAVY, size=12, bold=True)
    box(ax, 75, 72, 30, 11, "App code\n(Python / Java)", fill=BLUE_F, size=11)
    box(ax, 75, 54, 30, 11, "avg_spend =\nmean over 30 days", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 75, 66, 75, 60)
    # the mismatch
    box(ax, 50, 30, 34, 13, "SAME feature,\nTWO different formulas\n= SKEW", fill=RED, tcolor="white", size=11)
    arrow(ax, 30, 49, 42, 37, color=RED, dashed=True)
    arrow(ax, 70, 49, 58, 37, color=RED, dashed=True)
    caption(ax, "Two teams code 'the same' feature differently -> model sees inputs it never trained on -> accuracy tanks.")
    save(fig, p("m05_06_training_serving_skew.png"))


# ----------------------------------------------------------------------
# 07  Feature store fixes the skew
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "A Feature Store: One Definition, Two Stores")
    box(ax, 50, 80, 34, 11, "ONE feature definition\n(written once)", fill=ORANGE, tcolor="white", size=11)
    # offline store
    box(ax, 24, 55, 28, 13, "OFFLINE store\n(warehouse)\nbig history", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    # online store
    box(ax, 76, 55, 28, 13, "ONLINE store\n(key-value)\nlatest, fast", fill=BLUE_F, size=11, bold=False)
    arrow(ax, 42, 76, 30, 62)
    arrow(ax, 58, 76, 70, 62)
    box(ax, 24, 30, 28, 11, "Training reads\nfrom OFFLINE", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 76, 30, 28, 11, "Serving reads\nfrom ONLINE", fill=BLUE_F, size=11, bold=False)
    arrow(ax, 24, 48, 24, 36)
    arrow(ax, 76, 48, 76, 36)
    caption(ax, "Feast / Tecton / Michelangelo: define once, serve both -> training and serving finally agree.")
    save(fig, p("m05_07_feature_store.png"))


# ----------------------------------------------------------------------
# 08  Point-in-time correctness (timeline)
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Point-in-Time Correctness — No Peeking at the Future")
    # timeline
    arrow(ax, 12, 55, 92, 55, color=BLACK)
    note(ax, 90, 49, "time ->", size=10)
    # label event marker
    box(ax, 55, 68, 22, 10, "LABEL event\n(did they churn?)", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 55, 63, 55, 56, color=ORANGE)
    note(ax, 55, 43, "prediction time T", color=NAVY, size=10, bold=True)
    # allowed region
    box(ax, 30, 30, 30, 9, "OK: use data\nBEFORE T", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    # leak region
    box(ax, 78, 30, 24, 9, "LEAK: data\nAFTER T", fill=RED, tcolor="white", size=10, bold=False)
    arrow(ax, 30, 51, 30, 55, color=GREEN)
    arrow(ax, 78, 51, 78, 55, color=RED)
    caption(ax, "A feature must use ONLY facts known at time T. A naive join pulls future rows -> leakage -> fake accuracy.")
    save(fig, p("m05_08_point_in_time.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 5 diagrams generated.")
