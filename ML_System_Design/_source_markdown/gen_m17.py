# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 17 (Flagship Case Studies).
Reuses viz_style.py helpers (same Office palette as the rest of the course).
Outputs into ../images/ as m17_*.png at 150 dpi on white.
One architecture diagram per major case study + a master-pattern and cheat map.
KEEP IT SIMPLE: <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The master pattern that recurs: two-stage retrieval -> ranking funnel
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The Master Pattern — a Retrieval -> Ranking Funnel")
    box(ax, 13, 58, 16, 14, "Catalog\nmillions\nof items", fill=BLUE_F)
    box(ax, 35, 58, 16, 14, "Candidate\ngeneration\n~ 100s-1000s", fill=GREEN_F, edge=GREEN)
    box(ax, 57, 58, 16, 14, "Ranking\nmodel\n~ 100s", fill=ORANGE_F, edge=ORANGE)
    box(ax, 79, 58, 16, 14, "Re-rank\n+ policy\ntop 10", fill=BLUE_F)
    circle(ax, 94, 58, 5, "User", fill=GREEN_F, edge=GREEN, size=10)
    for x1, x2 in [(21, 27), (43, 49), (65, 71), (87, 89)]:
        arrow(ax, x1, 58, x2, 58)
    note(ax, 35, 44, "cheap, high recall\n~ 10-20 ms", size=10)
    note(ax, 57, 44, "expensive, precise\n~ 20-50 ms", size=10)
    note(ax, 79, 44, "diversity, rules\nbusiness policy", size=10)
    note(ax, 50, 30, "Used by: YouTube recs, feed ranking, web/product search,\n"
                     "ads, 'also bought', People-You-May-Know.", color=NAVY, size=11, bold=True)
    caption(ax, "Narrow millions -> thousands -> hundreds -> ten. Each stage trades recall for precision.")
    save(fig, p("m17_01_master_funnel.png"))


# ----------------------------------------------------------------------
# 02  YouTube video recommendation
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "YouTube Video Recommendation")
    box(ax, 14, 72, 18, 11, "Watch history\n+ context", fill=BLUE_F, size=11)
    box(ax, 14, 46, 18, 11, "Video corpus\n(billions)", fill=BLUE_F, size=11)
    box(ax, 40, 59, 20, 15, "Candidate gen\ntwo-tower ANN\n+ co-watch\n~ hundreds", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 66, 59, 18, 13, "Ranking DNN\nwatch-time\nweighted", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 88, 59, 16, 13, "Re-rank\ndiversity,\nfreshness", fill=BLUE_F, size=10)
    box(ax, 66, 30, 18, 9, "Serve top 10\nto homepage", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 23, 72, 30, 62)
    arrow(ax, 23, 46, 30, 56)
    arrow(ax, 50, 59, 57, 59)
    arrow(ax, 75, 59, 79, 59)
    arrow(ax, 66, 52, 66, 35)
    caption(ax, "Batch-precomputed candidates + online re-rank. Optimise expected WATCH TIME, not raw clicks.")
    save(fig, p("m17_02_youtube_reco.png"))


# ----------------------------------------------------------------------
# 03  Facebook / Instagram feed ranking (multi-task + value model)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Facebook / Instagram Feed Ranking")
    box(ax, 15, 60, 18, 13, "Candidate posts\nfriends, groups,\npages", fill=BLUE_F, size=10)
    box(ax, 39, 60, 17, 13, "Feature\nassembly\n(user x post)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 63, 60, 20, 15, "Multi-task DNN\nP(like) P(comment)\nP(share) P(hide)", fill=ORANGE_F, edge=ORANGE, size=9)
    box(ax, 87, 60, 16, 13, "Value model\nweighted\nsum", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 63, 34, 20, 10, "Integrity filter\n(spam, harmful)", fill=RED, tcolor="white", size=10)
    box(ax, 87, 34, 16, 9, "Ranked feed", fill=BLUE_F, size=11)
    arrow(ax, 24, 60, 30, 60)
    arrow(ax, 48, 60, 53, 60)
    arrow(ax, 73, 60, 79, 60)
    arrow(ax, 87, 53, 87, 39)
    arrow(ax, 73, 34, 79, 34)
    caption(ax, "Predict MANY actions, combine into one 'value' score. Integrity filter can veto any post.")
    save(fig, p("m17_03_feed_ranking.png"))


# ----------------------------------------------------------------------
# 04  Ad click-through-rate (CTR) prediction
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Ad Click-Through-Rate (CTR) Prediction")
    box(ax, 14, 60, 17, 12, "Ad request\nuser + context", fill=BLUE_F, size=10)
    box(ax, 37, 60, 17, 12, "Candidate ads\n(targeting)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 60, 60, 18, 13, "CTR model\nDCN / DeepFM\n-> pCTR", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 85, 60, 17, 12, "Rank by\npCTR x bid\n(eCPM)", fill=BLUE_F, size=10)
    box(ax, 60, 34, 18, 11, "Calibration\n(pCTR = true\nrate)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 85, 34, 17, 9, "Show ads\n+ auction", fill=BLUE_F, size=10)
    arrow(ax, 23, 60, 28, 60)
    arrow(ax, 46, 60, 51, 60)
    arrow(ax, 69, 60, 76, 60)
    arrow(ax, 60, 54, 60, 40)
    arrow(ax, 69, 34, 76, 34)
    caption(ax, "Sparse ID features dominate. CALIBRATION matters: pCTR feeds the auction price directly.")
    save(fig, p("m17_04_ctr_prediction.png"))


# ----------------------------------------------------------------------
# 05  Fraud / anomaly detection (payments)
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Fraud / Anomaly Detection (Payments)")
    box(ax, 14, 60, 17, 11, "Transaction\nevent", fill=BLUE_F, size=10)
    box(ax, 37, 60, 18, 13, "Streaming\nfeatures\n(velocity, geo)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 61, 60, 17, 12, "Rules engine\n(hard blocks)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 61, 38, 17, 12, "ML model\nGBDT +\nanomaly", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 85, 49, 17, 14, "Decision\napprove /\nreview /\ndecline", fill=BLUE_F, size=10)
    box(ax, 37, 34, 18, 10, "Delayed labels\n(chargebacks)", fill=RED, tcolor="white", size=9)
    arrow(ax, 23, 60, 28, 60)
    arrow(ax, 46, 60, 52, 60)
    arrow(ax, 61, 54, 61, 44)
    arrow(ax, 70, 60, 76, 53)
    arrow(ax, 70, 38, 76, 46)
    arrow(ax, 46, 42, 55, 55, color=RED, dashed=True)
    caption(ax, "Milliseconds + very imbalanced + labels arrive weeks late. Rules catch known, ML catches novel.")
    save(fig, p("m17_05_fraud_detection.png"))


# ----------------------------------------------------------------------
# 06  Uber / DoorDash ETA prediction
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Uber / DoorDash ETA Prediction")
    box(ax, 14, 60, 17, 12, "Trip / order\nrequest", fill=BLUE_F, size=10)
    box(ax, 37, 60, 18, 13, "Features\ntraffic, distance,\nprep time", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 61, 60, 17, 12, "Route ETA\n(map graph\nbaseline)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 85, 60, 17, 12, "ML residual\nmodel (GBDT)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 61, 34, 17, 11, "Quantile loss\n(P50 / P90)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 85, 34, 17, 10, "Final ETA\n+ uncertainty", fill=BLUE_F, size=10)
    arrow(ax, 23, 60, 28, 60)
    arrow(ax, 46, 60, 52, 60)
    arrow(ax, 70, 60, 76, 60)
    arrow(ax, 85, 54, 85, 39)
    arrow(ax, 69, 34, 76, 34)
    caption(ax, "Regression, but LATENESS hurts more than earliness -> use quantile loss, report a range.")
    save(fig, p("m17_06_eta_prediction.png"))


# ----------------------------------------------------------------------
# 07  Web search ranking funnel (serpentine)
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Web Search Ranking Funnel")
    box(ax, 14, 68, 16, 11, "Query", fill=BLUE_F, size=11)
    box(ax, 38, 68, 18, 12, "Query\nunderstanding\n(spell, intent)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 63, 68, 18, 13, "Retrieval\ninverted index\n+ dense ANN", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 87, 68, 16, 12, "L1 pre-rank\n(cheap)", fill=BLUE_F, size=10)
    box(ax, 63, 38, 18, 13, "L2 rank LTR\n(LambdaMART\n/ DNN)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 38, 38, 18, 12, "Re-rank\n(freshness,\ndiversity)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 14, 38, 16, 11, "Results\npage", fill=BLUE_F, size=11)
    arrow(ax, 22, 68, 29, 68)
    arrow(ax, 47, 68, 54, 68)
    arrow(ax, 72, 68, 79, 68)
    arrow(ax, 87, 62, 72, 45)
    arrow(ax, 54, 38, 47, 38)
    arrow(ax, 29, 38, 22, 38)
    caption(ax, "Optimise NDCG on relevance. Each stage shrinks the set so the costly ranker sees few docs.")
    save(fig, p("m17_07_web_search.png"))


# ----------------------------------------------------------------------
# 08  Enterprise RAG knowledge assistant (LLM)
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Enterprise RAG Knowledge Assistant")
    note(ax, 20, 82, "Offline: ingest", color=NAVY, size=12, bold=True)
    box(ax, 14, 68, 15, 10, "Company\ndocs", fill=BLUE_F, size=10)
    box(ax, 34, 68, 15, 10, "Chunk +\nclean", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 54, 68, 15, 10, "Embed", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 74, 68, 16, 10, "Vector DB\n(index)", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 21, 68, 27, 68)
    arrow(ax, 41, 68, 47, 68)
    arrow(ax, 61, 68, 67, 68)
    note(ax, 20, 48, "Online: query", color=RED, size=12, bold=True)
    box(ax, 14, 34, 15, 11, "User\nquestion", fill=BLUE_F, size=10)
    box(ax, 34, 34, 16, 11, "Retrieve\ntop-k chunks", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 55, 34, 16, 11, "Prompt +\ncontext", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 78, 34, 16, 11, "LLM ->\nanswer +\ncitations", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 74, 63, 40, 40, color=NAVY, dashed=True)
    arrow(ax, 22, 34, 26, 34)
    arrow(ax, 42, 34, 47, 34)
    arrow(ax, 63, 34, 70, 34)
    caption(ax, "Retrieval grounds the LLM. Measure retrieval hit-rate AND answer faithfulness (no hallucination).")
    save(fig, p("m17_08_enterprise_rag.png"))


# ----------------------------------------------------------------------
# 09  The six brief case studies mapped to their core pattern
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "Six More Case Studies -> Their Core Pattern")
    items = [
        (26, 70, "Airbnb search /\nsimilar listings", "LTR + listing\nembeddings", GREEN_F, GREEN),
        (54, 70, "Spam / harmful\ncontent", "Classification +\nadversarial", ORANGE_F, ORANGE),
        (82, 70, "'Customers\nalso bought'", "Item-item CF /\nco-occurrence", BLUE_F, NAVY),
        (26, 40, "People-You-\nMay-Know", "Graph link\nprediction", GREEN_F, GREEN),
        (54, 40, "Autocomplete /\ntypeahead", "Prefix trie +\nranking", ORANGE_F, ORANGE),
        (82, 40, "Multimodal\nsearch / recs", "Shared\nembedding space", BLUE_F, NAVY),
    ]
    for x, y, head, patt, f, e in items:
        box(ax, x, y, 22, 12, head, fill=e, tcolor="white", size=10)
        box(ax, x, y - 15, 22, 10, patt, fill=f, edge=e, size=10, bold=False)
    caption(ax, "Most 'new' problems are an old pattern in disguise — name the pattern first, then adapt.")
    save(fig, p("m17_09_brief_patterns.png"))


# ----------------------------------------------------------------------
# 10  Pattern recognition cheat map: hear this -> reach for that
# ----------------------------------------------------------------------
def d10():
    fig, ax = new_canvas()
    title(ax, "Pattern Recognition — Hear This, Reach For That")
    cues = [
        (74, "short list from a\nhuge catalog", "two-stage\nretrieval + rank"),
        (60, "yes/no with\nasymmetric cost", "calibrated\nclassification"),
        (46, "predict a number\n/ a time", "regression +\nquantile loss"),
        (32, "answer from\nprivate documents", "RAG (retrieve\n+ LLM)"),
        (18, "who should\nconnect to whom", "graph link\nprediction"),
    ]
    for y, cue, patt in cues:
        box(ax, 28, y, 30, 11, cue, fill=BLUE_F, size=11)
        box(ax, 72, y, 30, 11, patt, fill=ORANGE_F, edge=ORANGE, size=11)
        arrow(ax, 43, y, 57, y)
    caption(ax, "Interviews reward fast, correct pattern-matching — then you spend time on the trade-offs.")
    save(fig, p("m17_10_pattern_cheatsheet.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09(); d10()
    print("All Module 17 diagrams generated.")
