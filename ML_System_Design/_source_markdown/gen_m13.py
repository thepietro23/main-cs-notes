# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 13 (Search & Ranking).
Reuses viz_style.py helpers (same Office palette as the rest of the course).
Outputs into ../images/ as m13_*.png at 150 dpi on white.
KEEP IT SIMPLE: <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Inverted index
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Inverted Index — from words to document lists")
    # documents on the left
    note(ax, 17, 84, "Documents", color=NAVY, size=13, bold=True)
    box(ax, 17, 74, 22, 8, "D1: cat sat mat", fill=BLUE_F, size=11, bold=False)
    box(ax, 17, 62, 22, 8, "D2: cat and dog", fill=BLUE_F, size=11, bold=False)
    box(ax, 17, 50, 22, 8, "D3: dog ran fast", fill=BLUE_F, size=11, bold=False)
    # the index on the right
    note(ax, 68, 84, "Inverted index", color=RED, size=13, bold=True)
    box(ax, 68, 74, 34, 8, "cat  ->  D1, D2", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 68, 62, 34, 8, "dog  ->  D2, D3", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 68, 50, 34, 8, "mat  ->  D1", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 68, 38, 34, 8, "ran  ->  D3", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    arrow(ax, 29, 62, 50, 62, color=NAVY)
    note(ax, 40, 68, "build", color=GREEN, size=11, bold=True)
    caption(ax, "Term -> posting list of docs. A query looks up terms and intersects lists in ms.")
    save(fig, p("m13_01_inverted_index.png"))


# ----------------------------------------------------------------------
# 02  TF-IDF vs BM25
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "TF-IDF vs BM25 — why BM25 wins")
    box(ax, 28, 68, 34, 16, "TF-IDF\nscore grows\nLINEARLY with\nterm frequency",
        fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 72, 68, 34, 16, "BM25\nterm frequency\nSATURATES +\nlength norm",
        fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 28, 40, 34, 12, "10x a word\n= 10x weight\n(over-rewards)",
        fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 72, 40, 34, 12, "10x a word\n= small extra\n(diminishing)",
        fill=GREEN_F, edge=GREEN, size=11, bold=False)
    arrow(ax, 28, 62, 28, 46, color=NAVY)
    arrow(ax, 72, 62, 72, 46, color=ORANGE)
    caption(ax, "BM25 = TF-IDF + saturation (k1) + document-length normalization (b). It ranks better.")
    save(fig, p("m13_02_tfidf_vs_bm25.png"))


# ----------------------------------------------------------------------
# 03  Learning-to-Rank families
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Learning to Rank — three families")
    box(ax, 20, 66, 24, 16, "POINTWISE\nscore each doc\nalone\n(regression)",
        fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 50, 66, 24, 16, "PAIRWISE\ncorrect ORDER\nof doc pairs\n(RankNet)",
        fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 80, 66, 24, 16, "LISTWISE\nwhole list at\nonce (Lambda-\nMART, NDCG)",
        fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 20, 36, 24, 10, "simplest,\nignores order", fill=BLUE_F, size=10, bold=False)
    box(ax, 50, 36, 24, 10, "learns A > B", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 80, 36, 24, 10, "optimizes the\nrank metric", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    for x in (20, 50, 80):
        arrow(ax, x, 58, x, 42, color=GRAY)
    note(ax, 50, 24, "weaker  ------------------------->  stronger for ranking", color=NAVY, size=11, bold=True)
    caption(ax, "Move left to right: from scoring docs alone to directly optimizing the ranked list.")
    save(fig, p("m13_03_ltr_families.png"))


# ----------------------------------------------------------------------
# 04  Dense / semantic retrieval (dual-encoder + ANN)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Dense Retrieval — dual-encoder + ANN search")
    box(ax, 18, 72, 22, 10, "Query text", fill=BLUE_F, size=11, bold=False)
    box(ax, 18, 40, 22, 10, "Documents", fill=BLUE_F, size=11, bold=False)
    box(ax, 46, 72, 22, 10, "Query\nencoder", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 46, 40, 22, 10, "Doc\nencoder", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 74, 72, 22, 10, "query vector", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 74, 40, 22, 10, "doc vectors\n(indexed)", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 74, 20, 22, 10, "ANN index\n-> top-K", fill=ORANGE, tcolor="white", size=11, bold=True)
    arrow(ax, 29, 72, 35, 72); arrow(ax, 57, 72, 63, 72)
    arrow(ax, 29, 40, 35, 40); arrow(ax, 57, 40, 63, 40)
    arrow(ax, 74, 67, 74, 25, color=RED)
    arrow(ax, 74, 35, 74, 25, color=RED)
    caption(ax, "Two towers embed query + docs into one space; ANN finds nearest doc vectors fast (see M12, M16).")
    save(fig, p("m13_04_dense_retrieval.png"))


# ----------------------------------------------------------------------
# 05  Multi-stage ranking funnel
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Multi-Stage Ranking — the funnel")
    box(ax, 22, 72, 30, 11, "RETRIEVAL\nmillions -> ~1000", fill=BLUE_F, edge=NAVY, size=11, bold=False)
    box(ax, 22, 54, 30, 11, "PRE-RANK\n~1000 -> ~100", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 22, 36, 30, 11, "RANK\n~100 -> ~10", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 22, 18, 30, 11, "RE-RANK\nfinal order", fill=ORANGE, tcolor="white", size=11, bold=True)
    for y in (66.5, 48.5, 30.5):
        arrow(ax, 22, y, 22, y - 6, color=NAVY)
    # latency budget notes on the right
    note(ax, 62, 72, "cheap, fast\n(BM25 / ANN)", size=11)
    note(ax, 62, 54, "light model\nfew features", size=11)
    note(ax, 62, 36, "heavy model\nmany features", size=11)
    note(ax, 62, 18, "business rules\ndiversity, freshness", size=11)
    caption(ax, "Each stage keeps fewer items but spends more compute per item; total stays inside the latency budget.")
    save(fig, p("m13_05_multistage_funnel.png"))


# ----------------------------------------------------------------------
# 06  Query understanding, personalization, freshness
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Signals beyond the query text")
    box(ax, 50, 78, 30, 10, "Raw query", fill=BLUE_F, size=12, bold=True)
    box(ax, 20, 56, 26, 12, "QUERY\nUNDERSTAND\nspell, intent,\nsynonyms", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 50, 56, 26, 12, "PERSONALIZE\nuser history,\nlocation", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 80, 56, 26, 12, "FRESHNESS\nrecency,\ntrending", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    box(ax, 50, 30, 30, 11, "Ranking model", fill=ORANGE, tcolor="white", size=12, bold=True)
    arrow(ax, 42, 78, 24, 62); arrow(ax, 50, 73, 50, 62); arrow(ax, 58, 78, 76, 62)
    arrow(ax, 20, 50, 42, 36); arrow(ax, 50, 50, 50, 36); arrow(ax, 80, 50, 58, 36)
    caption(ax, "Good search fuses query meaning + who is asking + how fresh results must be.")
    save(fig, p("m13_06_signals.png"))


# ----------------------------------------------------------------------
# 07  NDCG worked example
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "NDCG — reward relevant docs near the top")
    note(ax, 20, 82, "rank", color=NAVY, size=12, bold=True)
    note(ax, 42, 82, "relevance", color=NAVY, size=12, bold=True)
    note(ax, 72, 82, "gain / log2(1+rank)", color=NAVY, size=12, bold=True)
    rows = [(1, "3", "3 / 1.00 = 3.00"),
            (2, "2", "2 / 1.58 = 1.26"),
            (3, "3", "3 / 2.00 = 1.50"),
            (4, "0", "0 / 2.32 = 0.00")]
    for i, (r, rel, dg) in enumerate(rows):
        y = 72 - i * 12
        box(ax, 20, y, 10, 9, str(r), fill=BLUE_F, size=12)
        box(ax, 42, y, 12, 9, rel, fill=ORANGE_F, edge=ORANGE, size=12)
        box(ax, 72, y, 34, 9, dg, fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 50, 16, 60, 9, "DCG = 5.76 ;  NDCG = DCG / ideal-DCG", fill=ORANGE, tcolor="white", size=12, bold=True)
    caption(ax, "Discount by position, then divide by the best possible ordering -> NDCG in [0, 1].")
    save(fig, p("m13_07_ndcg.png"))


# ----------------------------------------------------------------------
# 08  Worked design: product/web search ranking (7-step)
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Design: Product Search Ranking (end to end)")
    box(ax, 15, 70, 22, 12, "User query\n+ context", fill=BLUE_F, size=11, bold=False)
    box(ax, 43, 70, 22, 12, "Retrieval\nBM25 + ANN", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    box(ax, 71, 70, 22, 12, "Rank\nLambdaMART /\nneural", fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    box(ax, 71, 42, 22, 12, "Re-rank\nfreshness,\ndiversity", fill=ORANGE, tcolor="white", size=11, bold=True)
    box(ax, 43, 42, 22, 12, "Results\npage", fill=BLUE_F, size=11, bold=False)
    box(ax, 15, 42, 22, 12, "Logs\nclicks, buys", fill=GREEN_F, edge=GREEN, size=11, bold=False)
    arrow(ax, 26, 70, 32, 70); arrow(ax, 54, 70, 60, 70)
    arrow(ax, 71, 64, 71, 48, color=NAVY)
    arrow(ax, 60, 42, 54, 42); arrow(ax, 32, 42, 26, 42)
    arrow(ax, 15, 48, 15, 64, color=RED, dashed=True)
    note(ax, 6, 56, "retrain\nloop", color=RED, size=10, bold=True)
    caption(ax, "Offline: NDCG. Online: A/B test click-through and conversion; logs feed the retrain loop.")
    save(fig, p("m13_08_design_pipeline.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 13 diagrams generated.")
