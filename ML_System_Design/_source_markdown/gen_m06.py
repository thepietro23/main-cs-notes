# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 6 (Model Development & Training).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m06_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Choosing a model — decision flow
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Choosing a Model — start simple, climb only if needed")
    box(ax, 50, 84, 34, 9, "What is the data?", fill=BLUE_F)
    # tabular branch
    box(ax, 20, 66, 26, 10, "Tabular /\nfew rows", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 20, 48, 26, 10, "Linear /\nLogistic model", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 20, 28, 26, 11, "Trees / GBDT\n(XGBoost)", fill=GREEN, tcolor="white", size=11)
    # perception branch
    box(ax, 80, 66, 26, 10, "Images / audio /\nsequences", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 80, 48, 26, 10, "Deep nets\n(CNN / RNN)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 28, 26, 11, "Transformers\n(text, big data)", fill=GREEN, tcolor="white", size=11)
    arrow(ax, 42, 82, 24, 71)
    arrow(ax, 58, 82, 76, 71)
    arrow(ax, 20, 61, 20, 53)
    arrow(ax, 20, 43, 20, 34)
    arrow(ax, 80, 61, 80, 53)
    arrow(ax, 80, 43, 80, 34)
    note(ax, 50, 46, "baseline\nfirst", color=RED, size=11, bold=True)
    caption(ax, "Tabular -> GBDT usually wins. Perception / language -> deep nets / transformers.")
    save(fig, p("m06_01_model_choice.png"))


# ----------------------------------------------------------------------
# 02  Baselines — why they matter
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Baselines — the yardstick every model must beat")
    box(ax, 20, 68, 26, 12, "Random /\nmajority class", fill=BLUE_F, size=11)
    box(ax, 50, 68, 26, 12, "Simple rule /\nheuristic", fill=BLUE_F, size=11)
    box(ax, 80, 68, 26, 12, "Linear model", fill=BLUE_F, size=11)
    box(ax, 50, 42, 30, 12, "Your fancy model", fill=ORANGE, tcolor="white", size=12)
    arrow(ax, 22, 62, 44, 48)
    arrow(ax, 50, 62, 50, 48)
    arrow(ax, 78, 62, 56, 48)
    box(ax, 50, 20, 44, 10, "Does it beat ALL baselines?", fill=GREEN_F, edge=GREEN, size=12)
    arrow(ax, 50, 36, 50, 25)
    caption(ax, "If a model cannot beat a cheap baseline, its complexity is not earning its cost.")
    save(fig, p("m06_02_baselines.png"))


# ----------------------------------------------------------------------
# 03  Bias-variance / under- vs over-fitting
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Underfitting vs Overfitting (the bias-variance trade-off)")
    box(ax, 18, 60, 26, 14, "UNDERFIT\nhigh bias\ntoo simple", fill=BLUE_F, size=11)
    box(ax, 50, 60, 26, 14, "JUST RIGHT\nlow bias +\nlow variance", fill=GREEN, tcolor="white", size=11)
    box(ax, 82, 60, 26, 14, "OVERFIT\nhigh variance\ntoo complex", fill=ORANGE_F, edge=ORANGE, size=11)
    note(ax, 18, 44, "train err: high\ntest err: high", color=NAVY, size=10)
    note(ax, 50, 44, "train err: low\ntest err: low", color=GREEN, size=10, bold=True)
    note(ax, 82, 44, "train err: low\ntest err: HIGH", color=RED, size=10)
    box(ax, 50, 24, 60, 12, "Model complexity  ---->\nincrease capacity to cut bias, but variance grows", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    caption(ax, "Total error = bias^2 + variance + noise. The sweet spot minimises test error.")
    save(fig, p("m06_03_bias_variance.png"))


# ----------------------------------------------------------------------
# 04  L1 vs L2 regularization
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Regularization — penalise big weights to fight overfitting")
    note(ax, 28, 82, "L2 (Ridge)", color=NAVY, size=13, bold=True)
    note(ax, 74, 82, "L1 (Lasso)", color=RED, size=13, bold=True)
    box(ax, 28, 68, 30, 10, "add  lambda * sum(w^2)", fill=BLUE_F, size=11)
    box(ax, 74, 68, 30, 10, "add  lambda * sum|w|", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 28, 50, 30, 12, "shrinks weights\nsmoothly toward 0\n(none exactly 0)", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 74, 50, 30, 12, "drives some weights\nEXACTLY to 0\n= feature selection", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 28, 30, 30, 10, "use when many\nsmall effects", fill=BLUE_F, size=10, bold=False)
    box(ax, 74, 30, 30, 10, "use when few\nfeatures matter", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    caption(ax, "Bigger lambda = stronger penalty = simpler model = more bias, less variance.")
    save(fig, p("m06_04_regularization.png"))


# ----------------------------------------------------------------------
# 05  Loss functions map
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Loss Functions — each one optimises a different goal")
    box(ax, 20, 70, 24, 12, "MSE\n(regression)", fill=BLUE_F, size=11)
    box(ax, 50, 70, 24, 12, "Cross-entropy\n(classification)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 70, 24, 12, "Ranking loss\n(pairwise/hinge)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 35, 42, 24, 12, "Contrastive\n(embeddings)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 65, 42, 24, 12, "Hinge\n(SVM margin)", fill=BLUE_F, size=11)
    note(ax, 20, 55, "predict a\nnumber", size=10)
    note(ax, 50, 55, "predict a\nprobability", size=10)
    note(ax, 80, 55, "get order\nright", size=10)
    note(ax, 35, 27, "pull similar close,\npush apart", size=10)
    note(ax, 65, 27, "max-margin\nseparation", size=10)
    caption(ax, "Pick the loss that matches the true business goal, not just what is convenient.")
    save(fig, p("m06_05_loss_functions.png"))


# ----------------------------------------------------------------------
# 06  Optimization: loss landscape & learning rate
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Gradient Descent — the learning rate decides the step size")
    # bowl outline via arrows going down to minimum
    circle(ax, 50, 30, 6, "min", fill=GREEN, tcolor="white", size=11)
    box(ax, 16, 72, 24, 11, "LR too small\nslow crawl", fill=BLUE_F, size=11)
    box(ax, 50, 78, 24, 11, "LR just right\nsteady descent", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 84, 72, 24, 11, "LR too large\novershoot / diverge", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 20, 66, 44, 34, color=NAVY)
    arrow(ax, 50, 72, 50, 37, color=GREEN)
    arrow(ax, 80, 66, 56, 34, color=RED)
    note(ax, 50, 15, "SGD = noisy small-batch steps    Adam = adaptive per-weight step + momentum",
         color=NAVY, size=11, bold=True)
    caption(ax, "Walk downhill along the negative gradient; step size = learning rate.")
    save(fig, p("m06_06_optimization.png"))


# ----------------------------------------------------------------------
# 07  Data parallelism vs model parallelism
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Data Parallelism vs Model Parallelism")
    note(ax, 27, 84, "DATA parallel", color=NAVY, size=13, bold=True)
    note(ax, 75, 84, "MODEL parallel", color=RED, size=13, bold=True)
    # data parallel: full model copy per GPU, different data shards
    box(ax, 18, 66, 18, 12, "GPU 1\nfull model", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 38, 66, 18, 12, "GPU 2\nfull model", fill=GREEN_F, edge=GREEN, size=10)
    note(ax, 18, 52, "data shard A", size=10)
    note(ax, 38, 52, "data shard B", size=10)
    box(ax, 28, 38, 30, 9, "all-reduce\nsync gradients", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 18, 60, 24, 43)
    arrow(ax, 38, 60, 32, 43)
    # model parallel: model split across GPUs
    box(ax, 66, 66, 18, 11, "GPU 1\nlayers 1-4", fill=BLUE_F, size=10)
    box(ax, 86, 66, 18, 11, "GPU 2\nlayers 5-8", fill=BLUE_F, size=10)
    arrow(ax, 75, 66, 77, 66)
    note(ax, 75, 50, "one big model\nsplit across GPUs", size=10)
    caption(ax, "Data parallel: model fits, data huge. Model parallel: model too big for one GPU.")
    save(fig, p("m06_07_parallelism.png"))


# ----------------------------------------------------------------------
# 08  Hyperparameter tuning methods
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Hyperparameter Tuning — four search strategies")
    box(ax, 20, 66, 24, 13, "Grid\ntry every combo\n(expensive)", fill=BLUE_F, size=10)
    box(ax, 46, 66, 24, 13, "Random\nsample combos\n(often better)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 72, 66, 24, 13, "Bayesian\nmodel-guided\n(sample-efficient)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 50, 38, 30, 13, "Hyperband\ncheap early-stop,\nkill bad trials", fill=GREEN, tcolor="white", size=10)
    note(ax, 33, 50, "smarter ->", color=NAVY, size=11, bold=True)
    note(ax, 59, 50, "smarter ->", color=NAVY, size=11, bold=True)
    caption(ax, "Random beats grid for many dims; Bayesian/Hyperband spend budget where it pays off.")
    save(fig, p("m06_08_hpo.png"))


# ----------------------------------------------------------------------
# 09  Transfer learning / fine-tuning
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "Transfer Learning — reuse a big pretrained model")
    box(ax, 24, 70, 30, 12, "Pretrain\non huge generic\ndata (self-supervised)", fill=BLUE_F, size=10)
    box(ax, 24, 44, 30, 12, "Base model\n(learned features)", fill=ORANGE, tcolor="white", size=11)
    arrow(ax, 24, 64, 24, 50)
    box(ax, 74, 70, 30, 12, "Freeze early layers", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 74, 44, 30, 12, "Fine-tune on\nyour small\ntask data", fill=GREEN, tcolor="white", size=10)
    arrow(ax, 39, 44, 59, 44)
    arrow(ax, 74, 64, 74, 50)
    caption(ax, "Pretraining learns general features once; fine-tuning adapts them with little data.")
    save(fig, p("m06_09_transfer_learning.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09()
    print("All Module 6 diagrams generated.")
