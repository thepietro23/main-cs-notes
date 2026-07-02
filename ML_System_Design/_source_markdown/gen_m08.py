# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 8 (Model Serving & Inference).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m08_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Batch vs Online vs Streaming inference
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Three Ways to Serve Predictions")
    cols = [
        (20, "BATCH\n(offline)", "Predict for ALL\nrows on a\nschedule; save\nto a table", BLUE_F, NAVY, "seconds-hours\nlatency OK"),
        (50, "ONLINE\n(real-time)", "One prediction\nper request,\nlive, tight\nms budget", GREEN_F, GREEN, "10-200 ms\nlatency"),
        (80, "STREAMING", "React to events\nas they arrive\n(Kafka / Flink),\ncontinuous", ORANGE_F, ORANGE, "sub-second\nper event"),
    ]
    for x, head, body, f, e, lat in cols:
        box(ax, x, 74, 22, 12, head, fill=e, tcolor="white", size=12)
        box(ax, x, 50, 22, 22, body, fill=f, edge=e, size=11, bold=False)
        note(ax, x, 30, lat, size=10, color=e, bold=True)
    caption(ax, "Pick by freshness needed vs latency budget vs cost (cross-link Module 1).")
    save(fig, p("m08_01_batch_online_streaming.png"))


# ----------------------------------------------------------------------
# 02  Serving patterns
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Four Serving Patterns — where does the model live?")
    # Embedded
    note(ax, 25, 84, "1. Embedded", color=NAVY, size=12, bold=True)
    box(ax, 25, 70, 30, 14, "App + Model\nin one process", fill=BLUE_F, size=11)
    # Model-as-a-service
    note(ax, 75, 84, "2. Model-as-a-Service", color=GREEN, size=12, bold=True)
    box(ax, 63, 70, 18, 11, "App", fill=BLUE_F, size=11)
    box(ax, 87, 70, 18, 11, "Model\nServer", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 72, 70, 78, 70, color=GREEN)
    # Microservice
    note(ax, 25, 44, "3. Microservice", color=ORANGE, size=12, bold=True)
    box(ax, 13, 30, 16, 11, "App", fill=BLUE_F, size=11)
    box(ax, 37, 30, 20, 11, "Model svc\n(own scaling)", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 21, 30, 27, 30, color=ORANGE)
    # Sidecar
    note(ax, 75, 44, "4. Sidecar", color=RED, size=12, bold=True)
    box(ax, 63, 30, 18, 11, "App", fill=BLUE_F, size=11)
    box(ax, 87, 30, 18, 11, "Model\nsidecar", fill=ORANGE_F, edge=RED, size=10)
    arrow(ax, 72, 30, 78, 30, color=RED)
    note(ax, 75, 20, "same pod / host", size=9, color=GRAY)
    caption(ax, "Embedded = fastest but coupled; service/microservice = scale model separately.")
    save(fig, p("m08_02_serving_patterns.png"))


# ----------------------------------------------------------------------
# 03  Tail latency & fan-out
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Tail Latency: why p99 matters under fan-out")
    box(ax, 20, 60, 20, 12, "Request", fill=BLUE_F, size=12)
    # fan out to 5 services
    ys = [82, 71, 60, 49, 38]
    labels = ["svc A", "svc B", "svc C", "svc D", "svc E"]
    for i, (y, l) in enumerate(zip(ys, labels)):
        fill = RED if i == 2 else GREEN_F
        tc = "white" if i == 2 else BLACK
        box(ax, 55, y, 16, 8, l, fill=fill, edge=GREEN if i != 2 else RED,
            tcolor=tc, size=10)
        arrow(ax, 30, 60, 47, y, color=GRAY)
    box(ax, 85, 60, 16, 12, "Slowest\nwins", fill=ORANGE_F, edge=ORANGE, size=11)
    for y in ys:
        arrow(ax, 63, y, 77, 60, color=GRAY)
    note(ax, 55, 27, "1 slow service (p99) -> the WHOLE request is slow", color=RED, size=11, bold=True)
    note(ax, 55, 20, "fan-out to N: P(fast) = p^N  ->  the tail dominates", color=NAVY, size=10)
    caption(ax, "p50=20ms, p99=200ms: with 100 calls, ~63% of requests hit at least one p99 tail.")
    save(fig, p("m08_03_tail_latency.png"))


# ----------------------------------------------------------------------
# 04  Model optimization techniques
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Model Optimization — smaller & faster, small accuracy cost")
    box(ax, 18, 62, 22, 13, "Big FP32\nmodel\n(slow, large)", fill=BLUE_F, size=11)
    techs = [
        (52, 80, "Quantization\nFP32 -> INT8", GREEN_F, GREEN),
        (52, 62, "Pruning\ndrop weights", ORANGE_F, ORANGE),
        (52, 44, "Distillation\nbig -> small", GREEN_F, GREEN),
    ]
    for x, y, t, f, e in techs:
        box(ax, x, y, 24, 11, t, fill=f, edge=e, size=10)
        arrow(ax, 29, 62, x - 12, y, color=GRAY)
        arrow(ax, x + 12, y, 78, 58, color=NAVY)
    box(ax, 88, 58, 16, 13, "Small fast\nmodel", fill=ORANGE, edge=RED, tcolor="white", size=11)
    box(ax, 52, 26, 24, 9, "ONNX / TensorRT\ncompile + fuse", fill=BLUE_F, edge=NAVY, size=10)
    caption(ax, "INT8: ~4x smaller, 2-4x faster, ~1% accuracy drop. Distillation trades size for a little quality.")
    save(fig, p("m08_04_optimization.png"))


# ----------------------------------------------------------------------
# 05  Request batching (throughput vs latency)
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Request Batching — throughput up, per-request latency up")
    # incoming requests
    note(ax, 18, 82, "Incoming requests", size=11, color=NAVY, bold=True)
    for i, y in enumerate([76, 68, 60, 52]):
        box(ax, 15, y, 10, 6, "req", fill=BLUE_F, size=9)
        arrow(ax, 20, y, 33, 64, color=GRAY)
    box(ax, 42, 64, 16, 16, "Batch\nqueue\n(wait Xms)", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 50, 64, 63, 64, color=ORANGE)
    box(ax, 74, 64, 18, 16, "GPU runs\n1 big batch\n(efficient)", fill=GREEN_F, edge=GREEN, size=10)
    note(ax, 50, 40, "Bigger batch  ->  higher throughput (util) BUT higher latency (wait)", color=RED, size=11, bold=True)
    note(ax, 50, 32, "Tune: max batch size + max wait time (e.g. 5 ms)", color=NAVY, size=10)
    caption(ax, "Dynamic batching groups requests that arrive close in time to fill the hardware.")
    save(fig, p("m08_05_request_batching.png"))


# ----------------------------------------------------------------------
# 06  Hardware choices
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Hardware — CPU vs GPU vs TPU vs Accelerator")
    cards = [
        (18, "CPU", "Cheap, flexible\nLow parallelism\nSmall models,\nlow QPS", BLUE_F, NAVY),
        (44, "GPU", "Massive parallel\nGreat for deep\nnets & batching\nCostly", GREEN_F, GREEN),
        (70, "TPU", "Google ASIC for\ntensor ops; huge\ntrain + serve\nscale", ORANGE_F, ORANGE),
        (90, "Edge\nNPU", "On-device\nlow power\nphone / IoT", BLUE_F, NAVY),
    ]
    for x, head, body, f, e in cards:
        w = 18 if x != 90 else 16
        box(ax, x, 72, w, 10, head, fill=e, tcolor="white", size=12)
        box(ax, x, 50, w, 20, body, fill=f, edge=e, size=9, bold=False)
    note(ax, 50, 30, "Rule: CPU for light/latency-simple, GPU/TPU for big models + batching, NPU for on-device",
         size=10, color=NAVY)
    caption(ax, "Match hardware to model size, batch size, QPS, and cost — not to hype.")
    save(fig, p("m08_06_hardware.png"))


# ----------------------------------------------------------------------
# 07  Shadow, canary, A/B request flow
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Safe Rollouts — Shadow, Canary, A/B routing")
    box(ax, 16, 55, 16, 12, "Live\ntraffic", fill=BLUE_F, size=11)
    box(ax, 42, 55, 16, 12, "Router", fill=ORANGE_F, edge=ORANGE, size=11)
    arrow(ax, 24, 55, 34, 55, color=NAVY)
    # model A (old) serves
    box(ax, 74, 76, 20, 11, "Model A (old)\n90% served", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 74, 58, 20, 11, "Model B (new)\n10% canary", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 74, 38, 20, 11, "Model C\nSHADOW\n(no user impact)", fill=BLUE_F, edge=NAVY, size=9)
    arrow(ax, 50, 57, 64, 76, color=GREEN)
    arrow(ax, 50, 55, 64, 58, color=ORANGE)
    arrow(ax, 50, 53, 64, 40, color=GRAY, dashed=True)
    note(ax, 42, 40, "shadow = copy\nof traffic,\nresults dropped", size=9, color=GRAY)
    caption(ax, "Shadow: test silently. Canary: small % real users. A/B: measure metric, then ramp or roll back.")
    save(fig, p("m08_07_rollouts.png"))


# ----------------------------------------------------------------------
# 08  Latency budget breakdown
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "A 100 ms Latency Budget — worked breakdown")
    rows = [
        ("Network in / auth", 10, BLUE_F, NAVY),
        ("Feature fetch (store)", 25, ORANGE_F, ORANGE),
        ("Preprocess", 10, GREEN_F, GREEN),
        ("Model inference", 35, ORANGE, RED),
        ("Post-process + rank", 12, GREEN_F, GREEN),
        ("Network out", 8, BLUE_F, NAVY),
    ]
    y = 78
    x0 = 22
    scale = 0.7  # 100 units -> 70 x-units
    for label, ms, f, e in rows:
        w = ms * scale
        tc = "white" if e == RED else BLACK
        box(ax, x0 + w/2, y, w, 7, f"{ms}ms", fill=f, edge=e, tcolor=tc, size=10)
        note(ax, 12, y, label, size=9, ha="right", color=NAVY)
        y -= 10
    note(ax, 55, 20, "Total = 100 ms   ->   must fit the p99 budget, not just p50", color=RED, size=11, bold=True)
    caption(ax, "Inference is only part of the budget — features + network often cost more than the model.")
    save(fig, p("m08_08_latency_budget.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 8 diagrams generated.")
