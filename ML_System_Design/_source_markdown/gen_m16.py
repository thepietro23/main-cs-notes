# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 16 (LLM System Design).
Reuses viz_style.py helpers (same Office palette as the rest of the course).
Outputs into ../images/ as m16_*.png at 150 dpi on white.
KEEP DIAGRAMS SIMPLE: <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  LLM basics: text -> tokens -> context window; cost model
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "LLM Basics — Tokens, Context Window, Cost")
    box(ax, 15, 68, 20, 10, "Text\n(prompt)", fill=BLUE_F)
    box(ax, 42, 68, 22, 10, "Tokenizer\n(~4 chars/token)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 72, 68, 22, 10, "Tokens\n(numbers)", fill=ORANGE_F, edge=ORANGE)
    arrow(ax, 25, 68, 31, 68)
    arrow(ax, 53, 68, 61, 68)
    box(ax, 50, 45, 62, 12, "Context window = input tokens + output tokens\n(the model's short-term memory, fixed size)",
        fill=BLUE_F, size=11, bold=False)
    arrow(ax, 72, 62, 60, 51)
    box(ax, 27, 24, 30, 11, "INPUT tokens\ncheap ($ / 1M)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 72, 24, 30, 11, "OUTPUT tokens\n3-5x pricier", fill=RED, tcolor="white", size=11)
    caption(ax, "You pay per token. Output costs far more than input — long answers dominate the bill.")
    save(fig, p("m16_01_llm_basics.png"))


# ----------------------------------------------------------------------
# 02  Decision framework: prompt vs RAG vs fine-tune vs continued pretrain
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Prompt vs RAG vs Fine-tune vs Pretrain — pick one")
    box(ax, 50, 84, 40, 9, "Does a good prompt\nalready solve it?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 85, 84, 22, 9, "PROMPTING\n(start here)", fill=GREEN, tcolor="white", size=10)
    box(ax, 50, 64, 40, 9, "Need private / fresh\nFACTS from your data?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 85, 64, 22, 9, "RAG\n(retrieval)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 50, 44, 40, 9, "Need new STYLE /\nformat / behaviour?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 85, 44, 22, 9, "FINE-TUNE\n(LoRA)", fill=BLUE_F, size=10)
    box(ax, 50, 24, 40, 9, "Need a whole new\nDOMAIN / language?", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 85, 24, 22, 9, "CONTINUED\nPRETRAIN", fill=RED, tcolor="white", size=10)
    for y in (84, 64, 44, 24):
        arrow(ax, 70, y, 74, y); note(ax, 66, y+3.5, "yes", color=GREEN, size=9)
    arrow(ax, 50, 79.5, 50, 68.5); note(ax, 45, 74, "no", size=9)
    arrow(ax, 50, 59.5, 50, 48.5); note(ax, 45, 54, "no", size=9)
    arrow(ax, 50, 39.5, 50, 28.5); note(ax, 45, 34, "no", size=9)
    caption(ax, "Climb the ladder only when the cheaper rung fails. Most needs stop at prompting or RAG.")
    save(fig, p("m16_02_decision_framework.png"))


# ----------------------------------------------------------------------
# 03  RAG end-to-end architecture (centrepiece)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Retrieval-Augmented Generation (RAG) — End to End")
    note(ax, 20, 86, "OFFLINE: index build", color=GRAY, size=11, bold=True)
    box(ax, 15, 74, 20, 9, "Documents", fill=BLUE_F, size=11)
    box(ax, 42, 74, 20, 9, "Chunk", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 69, 74, 20, 9, "Embed", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 88, 55, 20, 9, "Vector DB", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 25, 74, 32, 74)
    arrow(ax, 52, 74, 59, 74)
    arrow(ax, 79, 70, 87, 60)
    note(ax, 20, 44, "ONLINE: query time", color=GRAY, size=11, bold=True)
    box(ax, 15, 32, 20, 9, "User query", fill=BLUE_F, size=11)
    box(ax, 42, 32, 20, 9, "Retrieve\ntop-k", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 66, 32, 18, 9, "Re-rank", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 66, 15, 18, 9, "LLM\ngenerate", fill=GREEN, tcolor="white", size=11)
    box(ax, 15, 15, 18, 9, "Answer\n+ sources", fill=BLUE_F, size=11)
    arrow(ax, 25, 32, 32, 32)
    arrow(ax, 88, 50, 50, 36, color=ORANGE, dashed=True)
    arrow(ax, 52, 32, 57, 32)
    arrow(ax, 66, 27, 66, 20)
    arrow(ax, 57, 15, 24, 15)
    caption(ax, "Index once offline; at query time retrieve relevant chunks and feed them to the LLM as context.")
    save(fig, p("m16_03_rag_architecture.png"))


# ----------------------------------------------------------------------
# 04  Hybrid search + query rewriting + HyDE + rerank
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Better Retrieval — Hybrid Search, Rewrite, Re-rank")
    box(ax, 16, 74, 22, 10, "Raw query", fill=BLUE_F, size=11)
    box(ax, 50, 74, 26, 10, "Query rewrite\n/ HyDE", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 27, 74, 37, 74)
    box(ax, 38, 52, 26, 11, "Dense search\n(embeddings)", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 72, 52, 26, 11, "Sparse search\n(BM25 keywords)", fill=BLUE_F, size=11)
    arrow(ax, 50, 69, 42, 58)
    arrow(ax, 50, 69, 68, 58)
    box(ax, 55, 30, 26, 10, "Merge (fuse)", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 40, 46.5, 52, 35)
    arrow(ax, 72, 46.5, 62, 35)
    box(ax, 55, 15, 26, 9, "Re-rank -> LLM", fill=GREEN, tcolor="white", size=11)
    arrow(ax, 55, 25, 55, 20)
    caption(ax, "Dense catches meaning, sparse catches exact terms; fuse then re-rank for the best top-k.")
    save(fig, p("m16_04_hybrid_search.png"))


# ----------------------------------------------------------------------
# 05  ANN indexes: HNSW / IVF / PQ
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "ANN Indexes — how vector search stays fast")
    box(ax, 22, 72, 26, 12, "HNSW", fill=GREEN, tcolor="white", size=13)
    note(ax, 22, 54, "Graph of nearest\nneighbours; hop\ntoward the query.\nFast, high recall,\nlots of RAM.", size=10)
    box(ax, 55, 72, 26, 12, "IVF", fill=NAVY, tcolor="white", size=13)
    note(ax, 55, 54, "Cluster vectors into\ncells; search only\nthe nearest cells.\nLess memory,\nsome recall loss.", size=10)
    box(ax, 85, 72, 26, 12, "PQ", fill=ORANGE, tcolor="white", size=13)
    note(ax, 85, 54, "Compress vectors\ninto codes.\nTiny memory,\nfaster but\nlower precision.", size=10)
    box(ax, 50, 24, 74, 12, "FAISS / ScaNN = libraries that combine these\n(e.g. IVF + PQ) to trade recall vs latency vs memory",
        fill=BLUE_F, size=11, bold=False)
    caption(ax, "All three approximate the true nearest neighbours — you trade a little recall for big speed/memory wins.")
    save(fig, p("m16_05_ann_indexes.png"))


# ----------------------------------------------------------------------
# 06  Fine-tuning: full vs LoRA / QLoRA (PEFT)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Fine-tuning — Full vs LoRA vs QLoRA")
    box(ax, 20, 70, 26, 14, "FULL\nfine-tune", fill=RED, tcolor="white", size=12)
    note(ax, 20, 50, "Update ALL\nweights.\nBest quality,\nhuge GPU cost,\none copy/task.", size=10)
    box(ax, 52, 70, 26, 14, "LoRA (PEFT)", fill=GREEN, tcolor="white", size=12)
    note(ax, 52, 50, "Freeze model,\ntrain small\nadapters (<1%).\nCheap, swappable\nper task.", size=10)
    box(ax, 84, 70, 26, 14, "QLoRA", fill=NAVY, tcolor="white", size=12)
    note(ax, 84, 50, "LoRA on a\n4-bit quantized\nmodel. Fits big\nmodels on one\nGPU.", size=10)
    box(ax, 50, 22, 70, 11, "Rule: adapters (LoRA/QLoRA) first; full fine-tune\nonly when adapters plateau and budget allows",
        fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    caption(ax, "PEFT trains a tiny fraction of parameters — near-full quality at a fraction of the compute and storage.")
    save(fig, p("m16_06_finetuning.png"))


# ----------------------------------------------------------------------
# 07  Inference optimization
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "LLM Inference Optimization — go faster & cheaper")
    items = [
        (20, 70, "KV cache", "Reuse past\nattention;\ndon't recompute", BLUE_F, NAVY),
        (50, 70, "Continuous\nbatching", "Pack many\nrequests per\nGPU pass", GREEN_F, GREEN),
        (80, 70, "Paged\nattention", "vLLM: paged\nKV memory,\nless waste", ORANGE_F, ORANGE),
        (20, 34, "Speculative\ndecoding", "Small model\ndrafts, big\nmodel checks", BLUE_F, NAVY),
        (50, 34, "Quantization", "GPTQ / AWQ:\n4-8 bit, less\nmemory", GREEN_F, GREEN),
        (80, 34, "Tensor\nparallelism", "Split model\nacross many\nGPUs", ORANGE_F, ORANGE),
    ]
    for x, y, head, body, f, e in items:
        box(ax, x, y, 24, 10, head, fill=e, tcolor="white", size=11)
        note(ax, x, y-11, body, size=10)
    caption(ax, "Together these raise throughput (tokens/sec) and cut cost/latency without changing model quality much.")
    save(fig, p("m16_07_inference_opt.png"))


# ----------------------------------------------------------------------
# 08  Agents & tool use loop + MCP
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Agents — plan, act with tools, remember")
    circle(ax, 30, 66, 12, "LLM\nplanner", fill=GREEN_F, edge=GREEN)
    circle(ax, 72, 66, 12, "Tools\n(APIs)", fill=ORANGE_F, edge=ORANGE)
    arrow(ax, 42, 68, 60, 68); note(ax, 51, 73, "call", color=NAVY, size=10)
    arrow(ax, 60, 63, 42, 63); note(ax, 51, 58, "result", color=NAVY, size=10)
    box(ax, 30, 38, 24, 10, "Memory\n(state / history)", fill=BLUE_F, size=11)
    arrow(ax, 30, 54, 30, 43)
    box(ax, 72, 38, 26, 10, "MCP\n(standard tool\nconnector)", fill=NAVY, tcolor="white", size=10)
    arrow(ax, 72, 54, 72, 43)
    caption(ax, "Agent loops: plan -> call a tool -> observe -> update memory -> repeat until the goal is met.")
    save(fig, p("m16_08_agents.png"))


# ----------------------------------------------------------------------
# 09  Guardrails, safety, prompt injection, PII
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "Guardrails — safety around the LLM")
    box(ax, 15, 62, 20, 10, "User input", fill=BLUE_F, size=11)
    box(ax, 42, 62, 24, 10, "INPUT guard\n(injection, PII)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 72, 62, 18, 10, "LLM", fill=GREEN, tcolor="white", size=12)
    arrow(ax, 25, 62, 30, 62)
    arrow(ax, 54, 62, 63, 62)
    box(ax, 55, 38, 24, 10, "OUTPUT guard\n(toxicity, leaks)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 20, 38, 22, 10, "Safe\nresponse", fill=BLUE_F, size=11)
    arrow(ax, 72, 57, 60, 43)
    arrow(ax, 43, 38, 31, 38)
    note(ax, 50, 18, "Never trust retrieved text or user text as instructions;\nredact PII; keep a blocklist + human escalation.",
         color=RED, size=11, bold=True)
    caption(ax, "Filter on the way in AND out — treat all external text as data, not commands.")
    save(fig, p("m16_09_guardrails.png"))


# ----------------------------------------------------------------------
# 10  Cost optimization: caching + model routing
# ----------------------------------------------------------------------
def d10():
    fig, ax = new_canvas()
    title(ax, "Cost Optimization — cache & route")
    box(ax, 16, 66, 20, 10, "Request", fill=BLUE_F, size=11)
    box(ax, 44, 66, 22, 10, "Cache?\n(seen before)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 78, 80, 22, 9, "Cached answer\n(near-free)", fill=GREEN, tcolor="white", size=10)
    arrow(ax, 26, 66, 33, 66)
    arrow(ax, 55, 70, 67, 79); note(ax, 60, 76, "hit", color=GREEN, size=9)
    box(ax, 44, 44, 22, 10, "Router\n(easy vs hard)", fill=NAVY, tcolor="white", size=10)
    arrow(ax, 44, 61, 44, 49); note(ax, 39, 55, "miss", color=RED, size=9)
    box(ax, 76, 52, 24, 9, "Small model\n(cheap, fast)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 76, 34, 24, 9, "Large model\n(hard queries)", fill=BLUE_F, size=10)
    arrow(ax, 55, 46, 64, 52)
    arrow(ax, 55, 42, 64, 36)
    caption(ax, "Cache repeats; route easy queries to a small/distilled model; reserve the big model for hard ones.")
    save(fig, p("m16_10_cost_routing.png"))


# ----------------------------------------------------------------------
# 11  Enterprise RAG knowledge assistant — 7 steps
# ----------------------------------------------------------------------
def d11():
    fig, ax = new_canvas()
    title(ax, "Enterprise RAG Assistant — 7-Step Design")
    steps = [
        (18, 74, "1. Frame\n& metrics", BLUE_F, NAVY),
        (50, 78, "2. Ingest\n& chunk", GREEN_F, GREEN),
        (82, 74, "3. Embed\n& index", GREEN_F, GREEN),
        (84, 48, "4. Retrieve\n+ re-rank", ORANGE_F, ORANGE),
        (66, 26, "5. Generate\n+ cite", GREEN, NAVY),
        (38, 24, "6. Guardrails\n& access", BLUE_F, NAVY),
        (16, 44, "7. Eval &\nmonitor", ORANGE_F, ORANGE),
    ]
    for x, y, t, f, e in steps:
        tc = "white" if f in (GREEN, NAVY, RED) else BLACK
        box(ax, x, y, 18, 11, t, fill=f, edge=e, tcolor=tc, size=10)
    seq = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6)]
    for a, b in seq:
        arrow(ax, steps[a][0], steps[a][1], steps[b][0], steps[b][1], color=NAVY)
    arrow(ax, 16, 50, 30, 74, color=RED, dashed=True)
    note(ax, 8, 62, "feedback", color=RED, size=10, bold=True)
    caption(ax, "Same lifecycle loop as any ML system, specialized for retrieval + generation over private docs.")
    save(fig, p("m16_11_enterprise_rag.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09(); d10(); d11()
    print("All Module 16 diagrams generated.")
