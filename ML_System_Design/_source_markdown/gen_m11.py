# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 11 (Scaling ML Systems).
Reuses viz_style.py helpers (same Office palette as DSA/DBMS notes).
Outputs into ../images/ as m11_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  Three independent axes of scaling
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Scale Data, Training, and Serving INDEPENDENTLY")
    box(ax, 50, 78, 26, 11, "ML System", fill=NAVY, tcolor="white", size=13)
    # three axes as three columns
    box(ax, 20, 55, 24, 11, "DATA\nscaling", fill=BLUE_F, edge=NAVY, size=12)
    box(ax, 50, 55, 24, 11, "TRAINING\nscaling", fill=GREEN_F, edge=GREEN, size=12)
    box(ax, 80, 55, 24, 11, "SERVING\nscaling", fill=ORANGE_F, edge=ORANGE, size=12)
    arrow(ax, 44, 74, 24, 61)
    arrow(ax, 50, 72, 50, 61)
    arrow(ax, 56, 74, 76, 61)
    box(ax, 20, 32, 24, 13, "shard,\npartition,\nreplicate", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    box(ax, 50, 32, 24, 13, "more GPUs,\ndata / model\nparallel", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 80, 32, 24, 13, "more replicas,\nautoscale on\nQPS", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 20, 49, 20, 39)
    arrow(ax, 50, 49, 50, 39)
    arrow(ax, 80, 49, 80, 39)
    caption(ax, "Each axis has its own bottleneck and its own fix — scale the one that hurts.")
    save(fig, p("m11_01_three_axes.png"))


# ----------------------------------------------------------------------
# 02  Sharding, replication, partitioning
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "Sharding vs Replication (two different jobs)")
    # Sharding (top): split data across nodes
    note(ax, 18, 82, "SHARDING", color=NAVY, size=13, bold=True)
    note(ax, 18, 76, "split data\n(more capacity)", color=NAVY, size=10)
    box(ax, 45, 78, 16, 10, "Shard A\nkeys 0-9", fill=BLUE_F, edge=NAVY, size=10)
    box(ax, 66, 78, 16, 10, "Shard B\nkeys 10-19", fill=BLUE_F, edge=NAVY, size=10)
    box(ax, 87, 78, 16, 10, "Shard C\nkeys 20-29", fill=BLUE_F, edge=NAVY, size=10)
    # Replication (bottom): copies for throughput / HA
    note(ax, 18, 42, "REPLICATION", color=GREEN, size=13, bold=True)
    note(ax, 18, 36, "copy same data\n(more reads, HA)", color=GREEN, size=10)
    box(ax, 45, 38, 16, 10, "Replica 1\n(full copy)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 66, 38, 16, 10, "Replica 2\n(full copy)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 87, 38, 16, 10, "Replica 3\n(full copy)", fill=GREEN_F, edge=GREEN, size=10)
    caption(ax, "Shard when data is too BIG for one node; replicate when reads/uptime need more copies.")
    save(fig, p("m11_02_shard_replicate.png"))


# ----------------------------------------------------------------------
# 03  Distributed training & the all-reduce bottleneck
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Distributed Training — communication is the bottleneck")
    # 4 GPUs each with a data shard
    xs = [18, 41, 64, 87]
    for i, x in enumerate(xs):
        box(ax, x, 74, 18, 11, "GPU %d\ndata shard" % (i+1), fill=GREEN_F, edge=GREEN, size=10)
        box(ax, x, 55, 18, 9, "compute\ngradient", fill=BLUE_F, edge=NAVY, size=10, bold=False)
        arrow(ax, x, 68, x, 60)
    # all-reduce bar
    box(ax, 52, 38, 74, 10, "ALL-REDUCE: sum + share gradients across ALL GPUs", fill=ORANGE, tcolor="white", size=11)
    for x in xs:
        arrow(ax, x, 50, x if x == 52 else (48 if x < 52 else 56), 43, color=ORANGE)
    box(ax, 52, 22, 40, 9, "updated weights\n(everyone in sync)", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    arrow(ax, 52, 33, 52, 27)
    caption(ax, "Every step must sync gradients — network bandwidth, not FLOPs, caps 1000s-of-GPUs jobs. (see M06)")
    save(fig, p("m11_03_distributed_training.png"))


# ----------------------------------------------------------------------
# 04  Sharded embedding tables + hashing trick
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Huge Embedding Tables — shard them, or hash the vocab")
    # sizing box
    box(ax, 25, 74, 40, 14, "SIZE = N x d x 4 bytes\n100M items x 128 x 4B\n= 51 GB (too big!)",
        fill=ORANGE_F, edge=ORANGE, size=11, bold=False)
    # sharded across servers
    note(ax, 74, 82, "Fix A: SHARD the table", color=NAVY, size=11, bold=True)
    box(ax, 58, 70, 15, 9, "PS 1\nrows 0-33M", fill=BLUE_F, edge=NAVY, size=9)
    box(ax, 74, 70, 15, 9, "PS 2\n33-66M", fill=BLUE_F, edge=NAVY, size=9)
    box(ax, 90, 70, 15, 9, "PS 3\n66-100M", fill=BLUE_F, edge=NAVY, size=9)
    # hashing trick
    note(ax, 50, 48, "Fix B: HASHING TRICK — map any id into a fixed small table", color=GREEN, size=11, bold=True)
    box(ax, 22, 34, 22, 11, "raw id\n(billions\npossible)", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    box(ax, 50, 34, 20, 11, "hash(id)\nmod M", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 78, 34, 24, 11, "fixed table\nof M rows\n(collisions OK)", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 33, 34, 40, 34)
    arrow(ax, 60, 34, 66, 34)
    caption(ax, "Sharding spreads a big table across servers; hashing caps memory by allowing a few collisions.")
    save(fig, p("m11_04_embeddings.png"))


# ----------------------------------------------------------------------
# 05  Horizontal vs vertical scaling
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Vertical vs Horizontal Scaling")
    note(ax, 25, 82, "VERTICAL (scale UP)", color=NAVY, size=12, bold=True)
    box(ax, 25, 68, 20, 9, "small box", fill=BLUE_F, edge=NAVY, size=10)
    box(ax, 25, 52, 26, 15, "BIGGER box\n(more CPU/RAM/GPU)", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    arrow(ax, 25, 63, 25, 60)
    note(ax, 25, 38, "simple, but hits a\nhard ceiling + costly", color=RED, size=10)

    note(ax, 74, 82, "HORIZONTAL (scale OUT)", color=GREEN, size=12, bold=True)
    for i, x in enumerate([62, 74, 86]):
        box(ax, x, 62, 10, 10, "box", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 74, 46, 30, 8, "load balancer", fill=NAVY, tcolor="white", size=10)
    for x in [62, 74, 86]:
        arrow(ax, 74, 50, x, 57, color=GREEN)
    note(ax, 74, 38, "add many nodes;\npreferred for serving", color=GREEN, size=10)
    caption(ax, "Vertical is easy but capped; horizontal scales far but needs statelessness + a balancer.")
    save(fig, p("m11_05_horiz_vs_vert.png"))


# ----------------------------------------------------------------------
# 06  Autoscaling inference on QPS / latency
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Autoscaling Inference — add replicas when load rises")
    box(ax, 18, 60, 20, 11, "Incoming\ntraffic (QPS)", fill=BLUE_F, edge=NAVY, size=10)
    box(ax, 46, 60, 22, 12, "Autoscaler\nwatches QPS\n& p99 latency", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 28, 60, 35, 60)
    # decision outcomes
    box(ax, 80, 76, 24, 10, "load HIGH ->\nadd replicas", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    box(ax, 80, 44, 24, 10, "load LOW ->\nremove replicas\n(save cost)", fill=BLUE_F, edge=NAVY, size=9, bold=False)
    arrow(ax, 57, 63, 68, 74)
    arrow(ax, 57, 57, 68, 47)
    note(ax, 50, 26, "Set a target: e.g. keep p99 < 100 ms and each pod < 200 QPS", color=NAVY, size=11)
    note(ax, 50, 18, "Beware cold starts — keep a warm minimum pool", color=RED, size=11, bold=True)
    caption(ax, "Scale out on a signal (QPS or latency), scale in when quiet — pay for what you use.")
    save(fig, p("m11_06_autoscaling.png"))


# ----------------------------------------------------------------------
# 07  Cost / Latency / Throughput trade-off triangle
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "The Trade-off Triangle — you cannot max all three")
    # triangle vertices
    ax_pts = [(50, 78), (22, 30), (78, 30)]
    # draw edges
    arrow(ax, 50, 78, 22, 30, color=GRAY, style="-", lw=2)
    arrow(ax, 22, 30, 78, 30, color=GRAY, style="-", lw=2)
    arrow(ax, 78, 30, 50, 78, color=GRAY, style="-", lw=2)
    box(ax, 50, 78, 22, 10, "LOW LATENCY", fill=BLUE_F, edge=NAVY, size=11)
    box(ax, 22, 27, 22, 10, "LOW COST", fill=GREEN_F, edge=GREEN, size=11)
    box(ax, 78, 27, 24, 10, "HIGH\nTHROUGHPUT", fill=ORANGE_F, edge=ORANGE, size=10)
    note(ax, 50, 52, "pick 2,\ngive on\nthe 3rd", color=RED, size=13, bold=True)
    caption(ax, "Batching lifts throughput but adds latency; more replicas cut latency but cost more. Choose.")
    save(fig, p("m11_07_tradeoff_triangle.png"))


# ----------------------------------------------------------------------
# 08  Worked example: 1k QPS -> 100k QPS
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Worked Example: scaling from 1k QPS to 100k QPS (100x)")
    box(ax, 18, 74, 22, 11, "1k QPS\n1 server,\nsimple", fill=BLUE_F, edge=NAVY, size=10, bold=False)
    box(ax, 82, 74, 22, 11, "100k QPS\nwhat must\nchange?", fill=ORANGE, tcolor="white", size=10, bold=False)
    arrow(ax, 29, 74, 71, 74)
    changes = [
        (17, 52, "Replicate\nstateless\nservers + LB", GREEN_F, GREEN),
        (39, 52, "Cache hot\npredictions\n(cut compute)", BLUE_F, NAVY),
        (61, 52, "Batch requests\n+ use GPU\nefficiently", GREEN_F, GREEN),
        (84, 52, "Shard\nembedding /\nfeature store", BLUE_F, NAVY),
    ]
    for x, y, t, f, e in changes:
        box(ax, x, y, 20, 15, t, fill=f, edge=e, size=10, bold=False)
    box(ax, 30, 28, 26, 11, "Autoscale on\nQPS + p99", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 66, 28, 30, 11, "Watch the triangle:\ncost vs latency", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    caption(ax, "100x traffic is a SYSTEMS problem: replicate, cache, batch, shard, autoscale — not a bigger model.")
    save(fig, p("m11_08_scaling_example.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 11 diagrams generated.")
