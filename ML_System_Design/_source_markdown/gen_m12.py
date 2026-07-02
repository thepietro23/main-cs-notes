# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 12 (Recommendation Systems).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m12_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The recsys problem & business framing
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The Recommendation Problem — pick a few from millions")
    box(ax, 16, 62, 20, 12, "One user\n(history,\ncontext)", fill=BLUE_F)
    box(ax, 16, 38, 20, 12, "Huge catalog\n(millions of\nitems)", fill=BLUE_F)
    box(ax, 50, 50, 22, 14, "Recommender\n(score & rank)", fill=ORANGE_F, edge=ORANGE, size=12)
    box(ax, 84, 50, 20, 14, "Top-N list\nshown to\nuser", fill=GREEN_F, edge=GREEN)
    arrow(ax, 26, 62, 39, 53)
    arrow(ax, 26, 38, 39, 47)
    arrow(ax, 61, 50, 74, 50)
    note(ax, 50, 24, "Goal: show items the user will engage with -> more watch time / sales / retention",
         color=NAVY, size=11)
    caption(ax, "A recsys turns 'one user + millions of items' into a short, personalized ranked list.")
    save(fig, p("m12_01_recsys_problem.png"))


# ----------------------------------------------------------------------
# 02  Collaborative filtering: user-user vs item-item
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Collaborative Filtering — 'people like you liked...'")
    note(ax, 28, 82, "User-User", color=NAVY, size=13, bold=True)
    box(ax, 28, 68, 20, 10, "Find users\nsimilar to me", fill=BLUE_F, size=11)
    box(ax, 28, 52, 20, 10, "Recommend\nwhat THEY\nliked", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 28, 63, 28, 57)
    note(ax, 74, 82, "Item-Item", color=RED, size=13, bold=True)
    box(ax, 74, 68, 20, 10, "Find items\nsimilar to\nwhat I liked", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 74, 52, 20, 10, "Recommend\nthose items", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 74, 63, 74, 57)
    note(ax, 50, 34, "Both learn ONLY from the user-item interaction matrix\n(no item content needed)",
         color=NAVY, size=11)
    caption(ax, "Item-item is more stable & scalable (items change less than tastes) -> Amazon's classic choice.")
    save(fig, p("m12_02_collaborative_filtering.png"))


# ----------------------------------------------------------------------
# 03  Matrix factorization  R ~= U . V^T
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Matrix Factorization — learn latent user & item vectors")
    box(ax, 20, 55, 22, 30, "R\nrating matrix\n(users x items)\nMOSTLY EMPTY", fill=BLUE_F, size=11)
    note(ax, 37, 55, "~=", color=BLACK, size=20, bold=True)
    box(ax, 52, 55, 16, 30, "U\nuser\nvectors", fill=ORANGE_F, edge=ORANGE, size=11)
    note(ax, 64, 55, "x", color=BLACK, size=18, bold=True)
    box(ax, 80, 55, 24, 14, "V^T\nitem vectors", fill=GREEN_F, edge=GREEN, size=11)
    note(ax, 50, 26, "Predict rating:  r_ui  =  u_i . v_j   (dot product of two k-dim vectors)",
         color=NAVY, size=12, bold=True)
    note(ax, 50, 17, "Fit by minimizing   sum (r_ui - u_i . v_j)^2  +  lambda(||u||^2+||v||^2)   via ALS or SGD",
         color=RED, size=11)
    caption(ax, "Compress a giant sparse matrix into small dense vectors; closeness in latent space = taste match.")
    save(fig, p("m12_03_matrix_factorization.png"))


# ----------------------------------------------------------------------
# 04  Content-based + hybrid
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Content-Based & Hybrid Recommenders")
    box(ax, 22, 70, 24, 12, "Content-based\n(item features:\ngenre, text, tags)", fill=BLUE_F, size=10)
    box(ax, 22, 48, 24, 10, "Match to user's\npast likes", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 22, 64, 22, 53)
    box(ax, 78, 70, 24, 12, "Collaborative\n(interaction\nmatrix)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 78, 48, 24, 10, "Learn from crowd\nbehaviour", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 78, 64, 78, 53)
    box(ax, 50, 28, 30, 12, "HYBRID\ncombine both", fill=NAVY, tcolor="white", size=12)
    arrow(ax, 30, 46, 44, 34)
    arrow(ax, 70, 46, 56, 34)
    caption(ax, "Content-based works for cold items; collaborative captures crowd taste. Hybrid gets the best of both.")
    save(fig, p("m12_04_content_vs_hybrid.png"))


# ----------------------------------------------------------------------
# 05  THE TWO-STAGE ARCHITECTURE (centrepiece)
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "The Two-Stage Recommender — Retrieval then Ranking")
    box(ax, 12, 55, 16, 14, "Catalog\nMILLIONS\nof items", fill=BLUE_F, size=10)
    box(ax, 38, 55, 20, 16, "STAGE 1\nCandidate\nGeneration\n(fast, cheap)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 66, 55, 20, 16, "STAGE 2\nRanking\n(heavy DNN,\naccurate)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 90, 55, 14, 14, "Top-N\nto user", fill=BLUE_F, size=10)
    arrow(ax, 20, 55, 28, 55); note(ax, 24, 62, "millions", size=9)
    arrow(ax, 48, 55, 56, 55); note(ax, 52, 62, "~hundreds", size=9, color=RED)
    arrow(ax, 76, 55, 83, 55); note(ax, 80, 62, "~10s", size=9, color=GREEN)
    note(ax, 38, 40, "cheap recall:\nANN / co-visit /\nmany sources", size=10, color=ORANGE)
    note(ax, 66, 40, "rich features:\nuser+item+context,\nprecise scores", size=10, color=GREEN)
    note(ax, 50, 24, "Why two stages? One heavy model over millions of items per request is too slow & costly.",
         color=NAVY, size=11)
    caption(ax, "Funnel: recall many cheaply (Stage 1), then rank the survivors precisely (Stage 2).")
    save(fig, p("m12_05_two_stage.png"))


# ----------------------------------------------------------------------
# 06  Two-tower / dual-encoder retrieval
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Two-Tower (Dual-Encoder) Retrieval Model")
    box(ax, 22, 78, 20, 10, "User & context\nfeatures", fill=BLUE_F, size=10)
    box(ax, 22, 60, 20, 10, "USER TOWER\n(neural net)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 22, 44, 20, 9, "user vector", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 22, 73, 22, 65); arrow(ax, 22, 55, 22, 49)
    box(ax, 78, 78, 20, 10, "Item\nfeatures", fill=BLUE_F, size=10)
    box(ax, 78, 60, 20, 10, "ITEM TOWER\n(neural net)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 78, 44, 20, 9, "item vector", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 78, 73, 78, 65); arrow(ax, 78, 55, 78, 49)
    box(ax, 50, 28, 30, 11, "dot product =\nsimilarity score", fill=NAVY, tcolor="white", size=11)
    arrow(ax, 32, 44, 44, 33); arrow(ax, 68, 44, 56, 33)
    note(ax, 50, 16, "Item vectors precomputed -> ANN index. At serving, embed user once, ANN-lookup nearest items.",
         color=RED, size=10)
    caption(ax, "Towers trained together; kept separate at serving so retrieval is a fast nearest-neighbour search.")
    save(fig, p("m12_06_two_tower.png"))


# ----------------------------------------------------------------------
# 07  Deep recommenders family
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Deep Recommender Ranking Models — what each adds")
    box(ax, 20, 68, 22, 14, "Wide & Deep\nwide=memorize\ndeep=generalize", fill=BLUE_F, size=10)
    box(ax, 50, 68, 22, 14, "DeepFM\nadds FM for\nfeature pairs\n(no manual cross)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 80, 68, 22, 14, "DCN\nexplicit feature\ncrosses via\ncross network", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 35, 40, 24, 14, "DLRM (Meta)\nembeddings +\ndot interactions\n+ MLP", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 68, 40, 24, 14, "All: turn sparse\nIDs -> embeddings\nthen learn\ninteractions", fill=BLUE_F, size=10)
    note(ax, 50, 22, "Common theme: automatically model FEATURE INTERACTIONS on top of embeddings",
         color=NAVY, size=11, bold=True)
    caption(ax, "They differ in HOW they cross features; all are used as the Stage-2 ranker at scale.")
    save(fig, p("m12_07_deep_recommenders.png"))


# ----------------------------------------------------------------------
# 08  Sequential / session-based
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Sequential Recommendation — order matters")
    seq = [(16, "item 1"), (33, "item 2"), (50, "item 3"), (67, "item 4")]
    for x, t in seq:
        box(ax, x, 66, 13, 9, t, fill=BLUE_F, size=10)
    for a, b in [(16, 33), (33, 50), (50, 67)]:
        arrow(ax, a + 6.5, 66, b - 6.5, 66)
    box(ax, 84, 66, 14, 10, "predict\nNEXT item", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 73.5, 66, 77, 66)
    box(ax, 50, 42, 40, 11, "Model: GRU4Rec (RNN) / SASRec / BERT4Rec (transformer)",
        fill=ORANGE_F, edge=ORANGE, size=11)
    note(ax, 50, 24, "Uses the ORDER of recent actions (a session) to predict the next click -- great for cold users",
         color=NAVY, size=11)
    caption(ax, "Self-attention (SASRec) weighs which past items matter most for the next action.")
    save(fig, p("m12_08_sequential.png"))


# ----------------------------------------------------------------------
# 09  Cold start strategies
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "Cold Start — no interaction history yet")
    note(ax, 28, 80, "New USER", color=NAVY, size=13, bold=True)
    box(ax, 28, 66, 24, 9, "Ask onboarding\npreferences", fill=BLUE_F, size=10)
    box(ax, 28, 53, 24, 9, "Use profile /\ncontext features", fill=BLUE_F, size=10)
    box(ax, 28, 40, 24, 9, "Show popular /\ntrending items", fill=GREEN_F, edge=GREEN, size=10)
    note(ax, 74, 80, "New ITEM", color=RED, size=13, bold=True)
    box(ax, 74, 66, 24, 9, "Use content\nfeatures", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 74, 53, 24, 9, "Similar-item\nembedding", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 74, 40, 24, 9, "Explore: show it\nto some users", fill=GREEN_F, edge=GREEN, size=10)
    caption(ax, "Pure collaborative filtering fails with no history -> lean on content, context, popularity & exploration.")
    save(fig, p("m12_09_cold_start.png"))


# ----------------------------------------------------------------------
# 10  Exploration vs exploitation (bandits)
# ----------------------------------------------------------------------
def d10():
    fig, ax = new_canvas()
    title(ax, "Exploration vs Exploitation — bandits in recsys")
    box(ax, 26, 62, 26, 14, "EXPLOIT\nshow known\nwinners\n(safe engagement)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 74, 62, 26, 14, "EXPLORE\ntry uncertain\nitems (learn\ntheir value)", fill=ORANGE_F, edge=ORANGE, size=10)
    note(ax, 50, 62, "vs", color=BLACK, size=16, bold=True)
    box(ax, 50, 36, 44, 11, "Bandits balance both: epsilon-greedy,\nUCB, Thompson sampling", fill=NAVY, tcolor="white", size=11)
    arrow(ax, 30, 55, 44, 42); arrow(ax, 70, 55, 56, 42)
    note(ax, 50, 20, "Too much exploit -> stale filter bubble.  Too much explore -> annoy users. Balance!",
         color=RED, size=11)
    caption(ax, "Recommending is a feedback loop: you only get data on what you show, so you must explore.")
    save(fig, p("m12_10_bandit.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09(); d10()
    print("All Module 12 diagrams generated.")
