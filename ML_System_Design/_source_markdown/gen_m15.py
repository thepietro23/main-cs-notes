# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 15 (NLP Systems).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS/M01 notes).
Outputs into ../images/ as m15_*.png at 150 dpi on white.
Keep diagrams SIMPLE: <=10 boxes, generous spacing, short labels.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The text pipeline (raw text -> prediction)
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "The NLP Pipeline — from raw text to a prediction")
    steps = [
        (12, "Raw\ntext", BLUE_F, NAVY),
        (32, "Clean /\nnormalize", ORANGE_F, ORANGE),
        (52, "Tokenize", GREEN_F, GREEN),
        (72, "Embed\n(vectors)", ORANGE_F, ORANGE),
        (92, "Model +\noutput", BLUE_F, NAVY),
    ]
    for x, t, f, e in steps:
        box(ax, x, 55, 16, 14, t, fill=f, edge=e, size=11)
    for i in range(len(steps) - 1):
        arrow(ax, steps[i][0] + 8, 55, steps[i + 1][0] - 8, 55)
    note(ax, 12, 38, '"I love it"', size=10)
    note(ax, 32, 38, "i love it", size=10)
    note(ax, 52, 38, "[i][love][it]", size=10)
    note(ax, 72, 38, "[0.2, -1.1, ...]", size=10)
    note(ax, 92, 38, "positive", size=10, color=GREEN, bold=True)
    caption(ax, "Text must become NUMBERS before any model can use it. Each stage adds cost and latency.")
    save(fig, p("m15_01_pipeline.png"))


# ----------------------------------------------------------------------
# 02  Tokenization: word vs subword/BPE vs char
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Tokenization — how to split text into pieces")
    note(ax, 20, 80, "WORD", color=NAVY, size=13, bold=True)
    box(ax, 20, 66, 26, 12, "playing\n->\n[playing]", fill=BLUE_F, size=10, bold=False)
    note(ax, 20, 50, "huge vocab;\nbreaks on\nnew words", size=10, color=RED)

    note(ax, 50, 80, "SUBWORD (BPE)", color=GREEN, size=13, bold=True)
    box(ax, 50, 66, 26, 12, "playing\n->\n[play][ing]", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    note(ax, 50, 50, "small vocab;\nhandles rare\n+ new words", size=10, color=GREEN)

    note(ax, 80, 80, "CHARACTER", color=ORANGE, size=13, bold=True)
    box(ax, 80, 66, 26, 12, "playing\n->\n[p][l][a]...", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    note(ax, 80, 50, "tiny vocab;\nvery long\nsequences", size=10, color=RED)

    caption(ax, "Subword (BPE / WordPiece) is the modern default: no out-of-vocabulary words, reasonable length.")
    save(fig, p("m15_02_tokenization.png"))


# ----------------------------------------------------------------------
# 03  Embeddings evolution timeline
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Embeddings Evolution — words become vectors")
    arrow(ax, 8, 30, 94, 30, color=BLACK)
    stops = [
        (18, 55, "word2vec\n(2013)", "static:\none vector\nper word", BLUE_F, NAVY),
        (42, 55, "GloVe\n(2014)", "static:\nfrom co-\noccurrence", BLUE_F, NAVY),
        (66, 55, "BERT\n(2018)", "contextual:\ndepends on\nsentence", GREEN_F, GREEN),
        (88, 55, "Modern\n(2020+)", "big context\nencoders /\nLLM embeds", ORANGE_F, ORANGE),
    ]
    for x, y, head, body, f, e in stops:
        box(ax, x, y, 18, 12, head, fill=e, tcolor="white", size=10)
        arrow(ax, x, 49, x, 32, color=GRAY)
        note(ax, x, 20, body, size=9)
    note(ax, 30, 72, "STATIC", color=NAVY, size=12, bold=True)
    note(ax, 77, 72, "CONTEXTUAL", color=GREEN, size=12, bold=True)
    caption(ax, "Left to right: fixed word vectors -> vectors that change with surrounding words.")
    save(fig, p("m15_03_embeddings_timeline.png"))


# ----------------------------------------------------------------------
# 04  Static vs contextual embeddings (the "bank" example)
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, 'Static vs Contextual — the word "bank"')
    note(ax, 27, 82, "STATIC (word2vec)", color=NAVY, size=12, bold=True)
    box(ax, 27, 68, 30, 10, '"river bank"', fill=BLUE_F, size=10)
    box(ax, 27, 52, 30, 10, '"money bank"', fill=BLUE_F, size=10)
    box(ax, 27, 34, 24, 10, "SAME\nvector", fill=RED, tcolor="white", size=11)
    arrow(ax, 27, 63, 27, 40)
    arrow(ax, 27, 47, 27, 40)

    note(ax, 74, 82, "CONTEXTUAL (BERT)", color=GREEN, size=12, bold=True)
    box(ax, 74, 68, 30, 10, '"river bank"', fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 74, 52, 30, 10, '"money bank"', fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 62, 34, 20, 10, "vector A", fill=GREEN, tcolor="white", size=10)
    box(ax, 86, 34, 20, 10, "vector B", fill=ORANGE, tcolor="white", size=10)
    arrow(ax, 74, 63, 64, 40)
    arrow(ax, 74, 47, 86, 40)

    caption(ax, "Static gives one vector per word; contextual reads the sentence, so meaning depends on context.")
    save(fig, p("m15_04_static_vs_contextual.png"))


# ----------------------------------------------------------------------
# 05  NLP tasks map
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Core NLP Tasks — how each is framed")
    tasks = [
        (20, 68, "Classification", "text -> 1 label", BLUE_F, NAVY),
        (50, 68, "Sentiment", "text -> pos/neg", BLUE_F, NAVY),
        (80, 68, "NER", "tag each token", GREEN_F, GREEN),
        (20, 40, "QA", "find answer\nspan", GREEN_F, GREEN),
        (50, 40, "Summarization", "long -> short\n(generate)", ORANGE_F, ORANGE),
        (80, 40, "Translation", "seq -> seq\n(generate)", ORANGE_F, ORANGE),
    ]
    for x, y, head, body, f, e in tasks:
        box(ax, x, y, 24, 10, head, fill=e, tcolor="white", size=11)
        note(ax, x, y - 9, body, size=9)
    note(ax, 35, 22, "in -> ONE output", color=NAVY, size=10, bold=True)
    note(ax, 78, 22, "in -> SEQUENCE out", color=ORANGE, size=10, bold=True)
    caption(ax, "Two big families: predict a label/tag (understanding) vs generate new text (seq-to-seq).")
    save(fig, p("m15_05_nlp_tasks.png"))


# ----------------------------------------------------------------------
# 06  Semantic search / similarity (embed + cosine + ANN)
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Semantic Search — embed once, compare by cosine")
    box(ax, 18, 70, 22, 11, "Query\ntext", fill=BLUE_F, size=11)
    box(ax, 48, 70, 22, 11, "Encoder", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 70, 22, 11, "Query\nvector", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 29, 70, 37, 70)
    arrow(ax, 59, 70, 69, 70)

    box(ax, 18, 40, 24, 12, "Doc vectors\n(precomputed)", fill=BLUE_F, size=10)
    box(ax, 55, 40, 26, 12, "ANN index\n(cosine top-k)", fill=GREEN, tcolor="white", size=11)
    box(ax, 88, 40, 18, 12, "Best\nmatches", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 80, 64, 66, 46)
    arrow(ax, 30, 40, 42, 40)
    arrow(ax, 68, 40, 79, 40)
    caption(ax, "Similar meaning -> nearby vectors. See M13 (retrieval) and M16 (LLM / RAG) for scale.")
    save(fig, p("m15_06_semantic_search.png"))


# ----------------------------------------------------------------------
# 07  Serving latency: what costs time
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "NLP Serving Latency — where the milliseconds go")
    bars = [
        (30, "Tokenize", 14, GREEN_F, GREEN),
        (45, "Embed lookup", 18, BLUE_F, NAVY),
        (60, "Model forward\npass", 46, ORANGE_F, ORANGE),
    ]
    for y, label, w, f, e in bars:
        box(ax, 20 + w / 2, y, w, 9, "", fill=f, edge=e)
        note(ax, 20 + w / 2, y, label, size=10)
    note(ax, 88, 60, "grows with\nSEQUENCE\nLENGTH", color=RED, size=11, bold=True)
    arrow(ax, 80, 60, 68, 60, color=RED)
    box(ax, 50, 20, 60, 11, "Fixes: cap length | cache | batch | distill / quantize",
        fill=GREEN_F, edge=GREEN, size=11, bold=False)
    caption(ax, "Cost scales with sequence length (often ~ n^2 in attention). Short inputs = cheap, fast serving.")
    save(fig, p("m15_07_serving_latency.png"))


# ----------------------------------------------------------------------
# 08  Case study sketch: support ticket routing
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Case Study — support ticket routing (7-step sketch)")
    steps = [
        (18, 70, "1. Ticket\ntext in", BLUE_F, NAVY),
        (50, 70, "2. Clean +\ntokenize", GREEN_F, GREEN),
        (82, 70, "3. Embed", ORANGE_F, ORANGE),
        (82, 45, "4. Classify\nteam", BLUE_F, NAVY),
        (50, 45, "5. Confidence\ncheck", GREEN_F, GREEN),
        (18, 45, "6. Route or\nhuman", ORANGE_F, ORANGE),
        (50, 22, "7. Log +\nretrain", BLUE_F, NAVY),
    ]
    for x, y, t, f, e in steps:
        box(ax, x, y, 20, 11, t, fill=f, edge=e, size=10)
    # top row: left to right, edge to edge
    arrow(ax, 28, 70, 40, 70, color=NAVY)
    arrow(ax, 60, 70, 72, 70, color=NAVY)
    # down into second row (Embed -> Classify team)
    arrow(ax, 82, 64.5, 82, 50.5, color=NAVY)
    # second row: right to left
    arrow(ax, 72, 45, 60, 45, color=NAVY)
    arrow(ax, 40, 45, 28, 45, color=NAVY)
    # Route/human down to Log + retrain
    arrow(ax, 22, 39.5, 42, 27, color=NAVY)
    # feedback: Log+retrain back up to Classify team
    arrow(ax, 60, 25, 74, 40, color=RED, dashed=True)
    note(ax, 90, 30, "feedback", color=RED, size=10, bold=True)
    caption(ax, "Low confidence -> send to a human; those corrections become fresh labels to retrain on.")
    save(fig, p("m15_08_case_study.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 15 diagrams generated.")
