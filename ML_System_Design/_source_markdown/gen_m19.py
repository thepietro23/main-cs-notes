# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 19
(Systems & Distributed Systems Foundations for ML).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m19_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Load balancing + horizontal scaling
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Load Balancing — spread traffic over many servers")
    box(ax, 15, 55, 18, 11, "Clients\n(many QPS)", fill=BLUE_F)
    box(ax, 44, 55, 18, 12, "Load\nBalancer", fill=ORANGE_F, edge=ORANGE, size=13)
    box(ax, 80, 78, 20, 10, "Model\nServer 1", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 55, 20, 10, "Model\nServer 2", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 80, 32, 20, 10, "Model\nServer 3", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 24, 55, 35, 55)
    arrow(ax, 53, 57, 70, 76)
    arrow(ax, 53, 55, 70, 55)
    arrow(ax, 53, 53, 70, 34)
    note(ax, 44, 40, "health checks\nremove dead\nservers", color=RED, size=10)
    caption(ax, "One entry point, N identical servers: scale OUT, survive a dead node, even out load.")
    save(fig, p("m19_01_load_balancing.png"))


# ----------------------------------------------------------------------
# 02  Caching — hit vs miss path
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Caching — fast memory in front of a slow store")
    box(ax, 16, 55, 18, 11, "Request", fill=BLUE_F)
    box(ax, 46, 55, 20, 12, "Cache\n(Redis /\nMemcached)", fill=ORANGE_F, edge=ORANGE, size=11)
    box(ax, 82, 55, 20, 12, "Database\n(slow, disk)", fill=GREEN_F, edge=GREEN, size=11)
    arrow(ax, 25, 55, 36, 55)
    arrow(ax, 56, 58, 72, 58); note(ax, 64, 63, "MISS -> read DB", color=RED, size=10)
    arrow(ax, 72, 52, 56, 52, color=GREEN); note(ax, 64, 47, "fill cache", color=GREEN, size=10)
    note(ax, 46, 38, "HIT -> return\nin ~1 ms", color=GREEN, size=11, bold=True)
    note(ax, 50, 24, "Evict when full (LRU) + TTL so stale data expires.", color=NAVY, size=11)
    caption(ax, "Most reads hit the cache; only misses touch the slow DB. Watch stampede on cold keys.")
    save(fig, p("m19_02_caching.png"))


# ----------------------------------------------------------------------
# 03  Databases for ML — pick by shape of data / query
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Databases for ML — pick by data shape & query")
    rows = [
        (74, "SQL / Relational", "joins, txns, strong schema", BLUE_F, NAVY),
        (60, "NoSQL (document)", "flexible schema, huge scale", GREEN_F, GREEN),
        (46, "Key-Value store", "fast lookups (feature store)", ORANGE_F, ORANGE),
        (32, "Vector DB", "embeddings, similarity search", BLUE_F, NAVY),
        (18, "Time-series DB", "metrics, events over time", GREEN_F, GREEN),
    ]
    for y, name, use, f, e in rows:
        box(ax, 30, y, 30, 10, name, fill=f, edge=e, size=12)
        box(ax, 72, y, 40, 10, use, fill="white", edge=GRAY, size=10, bold=False)
    caption(ax, "No single 'best' DB: match the store to how you write and read the data.")
    save(fig, p("m19_03_databases.png"))


# ----------------------------------------------------------------------
# 04  Kafka log — partitions & consumer groups
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Log-based Queue (Kafka) — partitions & consumers")
    box(ax, 15, 78, 18, 10, "Producers\n(events)", fill=BLUE_F, size=11)
    # topic partitions as append-only logs
    note(ax, 50, 68, "Topic (append-only log)", color=NAVY, size=12, bold=True)
    box(ax, 45, 58, 40, 8, "Partition 0:  e1  e2  e3  e4 ->", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 45, 47, 40, 8, "Partition 1:  e5  e6  e7 ->", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 85, 58, 18, 9, "Consumer A", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 85, 47, 18, 9, "Consumer B", fill=GREEN_F, edge=GREEN, size=10)
    arrow(ax, 24, 74, 40, 62)
    arrow(ax, 65, 58, 76, 58)
    arrow(ax, 65, 47, 76, 47)
    note(ax, 50, 30, "Each consumer tracks its own OFFSET.\nReplay by rewinding. Order kept WITHIN a partition.", color=NAVY, size=11)
    caption(ax, "Decouples producers from consumers; buffers spikes; lets many readers replay the same stream.")
    save(fig, p("m19_04_kafka_log.png"))


# ----------------------------------------------------------------------
# 05  CAP theorem
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "CAP Theorem — during a partition, pick C or A")
    circle(ax, 50, 74, 12, "C\nConsistency", fill=BLUE_F, size=11)
    circle(ax, 26, 34, 12, "A\nAvailability", fill=GREEN_F, edge=GREEN, size=11)
    circle(ax, 74, 34, 12, "P\nPartition\ntolerance", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 42, 66, 32, 44, color=GRAY, style="-")
    arrow(ax, 58, 66, 68, 44, color=GRAY, style="-")
    arrow(ax, 38, 34, 62, 34, color=GRAY, style="-")
    note(ax, 22, 74, "CP:\nbanks", color=NAVY, size=11, bold=True)
    note(ax, 78, 74, "AP:\ncaches,\nfeeds", color=NAVY, size=11, bold=True)
    caption(ax, "Networks WILL partition, so P is mandatory. Real choice: strong consistency OR stay available.")
    save(fig, p("m19_05_cap_theorem.png"))


# ----------------------------------------------------------------------
# 06  REST vs gRPC for ML serving
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "REST vs gRPC — why ML serving prefers gRPC")
    note(ax, 28, 82, "REST / JSON", color=NAVY, size=13, bold=True)
    note(ax, 74, 82, "gRPC / protobuf", color=RED, size=13, bold=True)
    left = ["Text JSON\n(bulky, slow parse)", "HTTP/1.1\none call at a time", "Human-readable,\neasy to debug"]
    right = ["Binary protobuf\n(small, fast)", "HTTP/2 multiplexing\n+ streaming", "Typed contract,\nlow latency"]
    for i, t in enumerate(left):
        box(ax, 28, 68 - i*17, 32, 12, t, fill=BLUE_F, size=10, bold=False)
    for i, t in enumerate(right):
        box(ax, 74, 68 - i*17, 34, 12, t, fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    caption(ax, "gRPC's compact binary payloads + HTTP/2 win for high-QPS, low-latency internal model calls.")
    save(fig, p("m19_06_rest_vs_grpc.png"))


# ----------------------------------------------------------------------
# 07  Reliability — timeout, retry, circuit breaker, degrade
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Reliability — protect the caller from a slow model")
    box(ax, 16, 60, 18, 11, "Caller", fill=BLUE_F)
    box(ax, 46, 60, 20, 12, "Circuit\nBreaker", fill=ORANGE_F, edge=ORANGE, size=12)
    box(ax, 80, 60, 20, 12, "Model\nService", fill=GREEN_F, edge=GREEN, size=12)
    arrow(ax, 25, 60, 36, 60)
    arrow(ax, 56, 60, 70, 60)
    note(ax, 22, 44, "timeout + retry\n(with backoff)", color=NAVY, size=10)
    box(ax, 46, 26, 30, 11, "Fallback:\ndefault / cached\nprediction", fill=RED, tcolor="white", size=10, bold=False)
    arrow(ax, 46, 54, 46, 32, color=RED, dashed=True)
    note(ax, 80, 44, "if failing:\nbreaker OPENS,\nstop calling", color=RED, size=10)
    caption(ax, "Timeout -> retry -> open the breaker -> degrade gracefully. Never let one slow dependency stall everything.")
    save(fig, p("m19_07_reliability.png"))


# ----------------------------------------------------------------------
# 08  Latency ladder — the numbers every engineer should know
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Latency Ladder — numbers you must memorise")
    rows = [
        (78, "L1 / L2 cache", "~1 ns", GREEN_F, GREEN),
        (66, "Main memory (RAM)", "~100 ns", GREEN_F, GREEN),
        (54, "SSD random read", "~100 us", BLUE_F, NAVY),
        (42, "Datacenter round trip", "~0.5 ms", ORANGE_F, ORANGE),
        (30, "Disk (HDD) seek", "~10 ms", ORANGE_F, ORANGE),
        (18, "Cross-region network", "~50-150 ms", RED, "white"),
    ]
    for y, label, val, f, e in rows:
        tc = "white" if f == RED else BLACK
        ec = RED if f == RED else e
        box(ax, 38, y, 44, 9, label, fill=f, edge=ec, tcolor=tc, size=11, bold=False)
        note(ax, 78, y, val, color=NAVY, size=12, bold=True)
    caption(ax, "Rule of thumb: memory is ~1000x faster than SSD, SSD ~100x faster than a cross-region hop.")
    save(fig, p("m19_08_latency_ladder.png"))


# ----------------------------------------------------------------------
# 09  Back-of-the-envelope estimation recipe
# ----------------------------------------------------------------------
def d09():
    fig, ax = new_canvas()
    title(ax, "Back-of-the-Envelope — a 4-step recipe")
    box(ax, 20, 62, 22, 14, "1. Traffic\nDAU x actions\n-> QPS\n(peak = 2-3x)", fill=BLUE_F, size=10, bold=False)
    box(ax, 46, 62, 22, 14, "2. Storage\nrows x bytes\nx retention", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 72, 62, 22, 14, "3. Bandwidth\nQPS x\npayload size", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 50, 32, 26, 13, "4. Machines\ntotal load /\nper-box capacity\n(+ headroom)", fill=BLUE_F, size=10, bold=False)
    arrow(ax, 31, 62, 35, 62)
    arrow(ax, 57, 62, 61, 62)
    arrow(ax, 72, 55, 55, 39, color=NAVY)
    caption(ax, "Round aggressively (1 day ~ 100k s). Aim for the right power of ten, not exact digits.")
    save(fig, p("m19_09_estimation.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08(); d09()
    print("All Module 19 diagrams generated.")
