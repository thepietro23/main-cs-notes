# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 21 (Hands-On Projects).
Reuses viz_style.py helpers (same Office palette as Module 1).
Outputs into ../images/ as m21_*.png at 150 dpi on white.
Rule #1: keep diagrams SIMPLE — <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Recommender — candidate generation + ranking (two-stage)
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Project 1 — Recommender: Candidates then Ranking")
    box(ax, 14, 55, 18, 12, "User\nrequest", fill=BLUE_F)
    box(ax, 40, 72, 22, 13, "Candidate gen\n(millions -> ~500)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 40, 38, 22, 13, "ANN index\n(two-tower\nembeddings)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 70, 55, 20, 13, "Ranker\n(~500 -> top 10)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 92, 55, 14, 12, "Top-10\nfeed", fill=BLUE_F)
    arrow(ax, 23, 57, 29, 70)
    arrow(ax, 29, 72, 29, 42, color=GRAY, dashed=True)
    arrow(ax, 51, 72, 62, 60)
    arrow(ax, 51, 40, 62, 52)
    arrow(ax, 80, 55, 85, 55)
    note(ax, 40, 20, "cheap recall stage  +  expensive precision stage", color=NAVY, size=11)
    caption(ax, "Two-stage: fast candidate generation narrows millions, then a heavy ranker orders the few. (see M12)")
    save(fig, p("m21_01_recommender.png"))


# ----------------------------------------------------------------------
# 02  Semantic search — embed -> vector DB (FAISS/HNSW) -> query
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Project 2 — Semantic Search with a Vector DB")
    note(ax, 28, 84, "Offline: index build", color=GREEN, size=12, bold=True)
    box(ax, 16, 70, 18, 11, "Documents", fill=BLUE_F)
    box(ax, 42, 70, 20, 11, "Embed model\n(encoder)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 70, 70, 22, 12, "Vector DB\n(FAISS / HNSW)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 25, 70, 32, 70)
    arrow(ax, 52, 70, 59, 70)
    note(ax, 28, 44, "Online: query time", color=NAVY, size=12, bold=True)
    box(ax, 16, 30, 18, 11, "User query", fill=BLUE_F)
    box(ax, 42, 30, 20, 11, "Embed query", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 70, 30, 22, 11, "Top-k nearest\n(ANN search)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 25, 30, 32, 30)
    arrow(ax, 52, 30, 59, 30)
    arrow(ax, 70, 64, 70, 36, color=GRAY, dashed=True)
    caption(ax, "Embed both docs and query into one space; approximate nearest-neighbour returns similar items. (see M13, M16)")
    save(fig, p("m21_02_semantic_search.png"))


# ----------------------------------------------------------------------
# 03  RAG chatbot — chunk/embed/retrieve/generate with evals
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Project 3 — RAG Chatbot over a Document Corpus")
    box(ax, 14, 68, 16, 11, "User\nquestion", fill=BLUE_F)
    box(ax, 38, 68, 18, 11, "Retriever\n(top-k chunks)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 64, 68, 18, 11, "Prompt\n+ context", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 88, 68, 16, 11, "LLM\nanswer", fill=BLUE_F)
    arrow(ax, 22, 68, 29, 68)
    arrow(ax, 47, 68, 55, 68)
    arrow(ax, 73, 68, 80, 68)
    box(ax, 38, 42, 18, 11, "Vector store\n(chunks)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 38, 47, 38, 62, color=GRAY, dashed=True)
    box(ax, 74, 30, 24, 12, "Eval harness\n(faithfulness,\ncontext recall)", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 88, 62, 82, 36, color=RED, dashed=True)
    caption(ax, "Ground answers in retrieved chunks; evaluate faithfulness and retrieval quality offline. (see M16)")
    save(fig, p("m21_03_rag_chatbot.png"))


# ----------------------------------------------------------------------
# 04  Real-time fraud detection — streaming features (Kafka/Flink)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Project 4 — Real-Time Fraud Detection Pipeline")
    box(ax, 13, 55, 16, 12, "Txn\nevents", fill=BLUE_F)
    box(ax, 35, 55, 16, 12, "Kafka\n(event bus)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 57, 55, 18, 13, "Flink\n(streaming\nfeatures)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 81, 55, 18, 12, "Model\nscoring", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 21, 55, 27, 55)
    arrow(ax, 43, 55, 49, 55)
    arrow(ax, 66, 55, 72, 55)
    box(ax, 57, 28, 18, 11, "Online\nfeature store", fill=BLUE_F, size=11)
    arrow(ax, 57, 48, 57, 34, color=GRAY, dashed=True)
    box(ax, 81, 28, 18, 11, "Block / allow\n+ alert", fill=RED, tcolor="white", size=10)
    arrow(ax, 81, 49, 81, 34)
    caption(ax, "Events stream through Kafka; Flink builds fresh features; the model scores in milliseconds. (see M04, M10)")
    save(fig, p("m21_04_fraud_pipeline.png"))


# ----------------------------------------------------------------------
# 05  Feature store — offline + online, point-in-time
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Project 5 — Feature Store: Offline + Online")
    box(ax, 16, 66, 18, 12, "Raw data\nsources", fill=BLUE_F)
    box(ax, 44, 66, 20, 12, "Feature\ncompute", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 25, 66, 34, 66)
    box(ax, 76, 80, 22, 12, "Offline store\n(point-in-time\ntraining)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 76, 52, 22, 12, "Online store\n(low-latency\nlookup)", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 54, 68, 65, 78)
    arrow(ax, 54, 64, 65, 54)
    box(ax, 44, 26, 20, 11, "Training job", fill=BLUE_F, size=11)
    box(ax, 76, 26, 22, 11, "Serving\n(prediction)", fill=BLUE_F, size=11)
    arrow(ax, 76, 74, 54, 32, color=GRAY, dashed=True)
    arrow(ax, 76, 46, 76, 32)
    caption(ax, "One definition, two stores; point-in-time joins prevent leakage and training-serving skew. (see M05)")
    save(fig, p("m21_05_feature_store.png"))


# ----------------------------------------------------------------------
# 06  A/B testing & monitoring dashboard
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Project 6 — A/B Testing & Monitoring Dashboard")
    box(ax, 16, 60, 16, 12, "Traffic\nsplitter", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 42, 76, 18, 11, "Control (A)\nold model", fill=BLUE_F, size=11)
    box(ax, 42, 44, 18, 11, "Treatment (B)\nnew model", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 24, 62, 33, 74)
    arrow(ax, 24, 58, 33, 47)
    box(ax, 70, 60, 20, 12, "Metrics log\n(events)", fill=BLUE_F, size=11)
    arrow(ax, 51, 76, 61, 63)
    arrow(ax, 51, 44, 61, 57)
    box(ax, 70, 30, 24, 12, "Dashboard\n(lift, p-value,\nguardrails)", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 70, 54, 70, 36)
    caption(ax, "Split traffic, log outcomes, compute lift with significance and guardrail metrics. (see M07, M10)")
    save(fig, p("m21_06_ab_dashboard.png"))


# ----------------------------------------------------------------------
# 07  LLM serving with batching & caching
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Project 7 — LLM Serving: Batching + Caching")
    box(ax, 14, 55, 16, 12, "Requests", fill=BLUE_F)
    box(ax, 37, 55, 18, 12, "Cache\n(prompt hit?)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 62, 55, 18, 13, "Batch\nscheduler", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 87, 55, 16, 12, "GPU\nLLM", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 22, 55, 28, 55)
    arrow(ax, 46, 55, 53, 55)
    arrow(ax, 71, 55, 79, 55)
    box(ax, 37, 28, 18, 11, "Cached\nresponse", fill=BLUE_F, size=11)
    arrow(ax, 37, 49, 37, 34, color=GREEN, dashed=True)
    note(ax, 46, 41, "hit", color=GREEN, size=10)
    note(ax, 62, 33, "batch many requests -> one GPU pass (throughput)", color=NAVY, size=10)
    caption(ax, "Cache repeats and batch concurrent requests to raise throughput and cut cost. (see M08, M16)")
    save(fig, p("m21_07_llm_serving.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07()
    print("All Module 21 diagrams generated.")
