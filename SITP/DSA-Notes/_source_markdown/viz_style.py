"""Shared matplotlib style for DSA notes diagrams — matches existing images/*.png.
Office theme palette. Import helpers to draw boxes, arrows, titles, captions.
Output ~932x466 @ ~150 dpi, RGBA on white.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

NAVY   = "#1F4E78"
BLUE_F = "#DDEBF7"
ORANGE = "#ED7D31"; ORANGE_F = "#FCE4D6"
GREEN  = "#70AD47"; GREEN_F  = "#E2EFDA"
RED    = "#C00000"
GRAY   = "#808080"
BLACK  = "#000000"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "figure.dpi": 150,
    "savefig.dpi": 150,
})

def new_canvas(w=9.32, h=4.66):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax

def title(ax, text, y=94):
    ax.text(50, y, text, ha="center", va="center", color=NAVY,
            fontsize=15, fontweight="bold")

def caption(ax, text, y=6, color=RED, size=13, bold=True):
    ax.text(50, y, text, ha="center", va="center", color=color,
            fontsize=size, fontweight="bold" if bold else "normal")

def note(ax, x, y, text, color=NAVY, size=12, ha="center", bold=False):
    ax.text(x, y, text, ha=ha, va="center", color=color, fontsize=size,
            fontweight="bold" if bold else "normal")

def box(ax, x, y, w, h, text, fill=BLUE_F, edge=NAVY, tcolor=BLACK,
        size=13, bold=True, round=True):
    style = "round,pad=0.02,rounding_size=1.2" if round else "square,pad=0.02"
    p = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle=style,
                       linewidth=2, edgecolor=edge, facecolor=fill)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", color=tcolor,
            fontsize=size, fontweight="bold" if bold else "normal")

def circle(ax, x, y, r, text="", fill=BLUE_F, edge=NAVY, tcolor=BLACK, size=13):
    ax.add_patch(Circle((x, y), r, linewidth=2, edgecolor=edge, facecolor=fill))
    if text:
        ax.text(x, y, text, ha="center", va="center", color=tcolor,
                fontsize=size, fontweight="bold")

def arrow(ax, x1, y1, x2, y2, color=NAVY, style="-|>", lw=2, dashed=False):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                        mutation_scale=18, linewidth=lw, color=color,
                        linestyle="--" if dashed else "-")
    ax.add_patch(a)

def save(fig, path):
    fig.savefig(path, dpi=150, facecolor="white", bbox_inches="tight",
                pad_inches=0.15)
    plt.close(fig)
    print("wrote", path)
