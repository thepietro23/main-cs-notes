# -*- coding: utf-8 -*-
"""Generate PNG diagrams for ML System Design — Module 14 (Computer Vision).
Reuses viz_style.py helpers (same Office palette as M01).
Outputs into ../images/ as m14_*.png at 150 dpi on white.
"""
import os
from viz_style import (new_canvas, title, caption, note, box, circle, arrow, save,
                       NAVY, BLUE_F, ORANGE, ORANGE_F, GREEN, GREEN_F, RED, GRAY, BLACK)

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
def p(name): return os.path.join(OUT, name)


# ----------------------------------------------------------------------
# 01  The three core CV tasks
# ----------------------------------------------------------------------
def d01():
    fig, ax = new_canvas()
    title(ax, "Three Core Vision Tasks — what each one outputs")
    box(ax, 20, 68, 24, 12, "CLASSIFICATION", fill=NAVY, tcolor="white", size=11)
    box(ax, 50, 68, 24, 12, "DETECTION", fill=ORANGE, tcolor="white", size=11)
    box(ax, 80, 68, 24, 12, "SEGMENTATION", fill=GREEN, tcolor="white", size=11)
    box(ax, 20, 45, 24, 18, "One label\nfor whole image\n\n\"cat\"", fill=BLUE_F, size=10, bold=False)
    box(ax, 50, 45, 24, 18, "Boxes + labels\nfor each object\n\n\"cat @ (x,y,w,h)\"", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 80, 45, 24, 18, "Label for every\npixel (a mask)\n\n\"which pixels\nare cat\"", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    note(ax, 20, 28, "Question:\nWHAT is it?", size=10)
    note(ax, 50, 28, "Question:\nWHERE are they?", size=10)
    note(ax, 80, 28, "Question:\nWHICH pixels?", size=10)
    caption(ax, "Output gets richer left to right; cost and label effort rise too.")
    save(fig, p("m14_01_cv_tasks.png"))


# ----------------------------------------------------------------------
# 02  The CV pipeline: raw image -> preprocess -> model -> postprocess
# ----------------------------------------------------------------------
def d02():
    fig, ax = new_canvas()
    title(ax, "The Computer-Vision Pipeline (end to end)")
    box(ax, 12, 55, 17, 13, "Raw image\n(bytes /\ncamera)", fill=BLUE_F, size=10)
    box(ax, 34, 55, 17, 13, "Preprocess\n(decode, resize,\nnormalize)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 56, 55, 17, 13, "Model\n(CNN / ViT\nbackbone)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 78, 55, 18, 13, "Postprocess\n(softmax, NMS,\nthreshold)", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 20, 55, 26, 55)
    arrow(ax, 42, 55, 48, 55)
    arrow(ax, 64, 55, 70, 55)
    box(ax, 50, 28, 26, 12, "Prediction\n(label / boxes / mask)", fill=NAVY, tcolor="white", size=11)
    arrow(ax, 78, 49, 55, 34, color=NAVY)
    caption(ax, "Preprocess and postprocess are code, not the model — but they cause most bugs.")
    save(fig, p("m14_02_cv_pipeline.png"))


# ----------------------------------------------------------------------
# 03  CNN -> ViT (how the backbone sees an image)
# ----------------------------------------------------------------------
def d03():
    fig, ax = new_canvas()
    title(ax, "Backbones: CNN vs Vision Transformer (ViT)")
    note(ax, 27, 82, "CNN", color=NAVY, size=13, bold=True)
    box(ax, 27, 70, 26, 10, "Slide small filters\nover the image", fill=BLUE_F, size=10, bold=False)
    box(ax, 27, 55, 26, 10, "Stack layers ->\nlocal to global", fill=BLUE_F, size=10, bold=False)
    box(ax, 27, 40, 26, 10, "Good with less\ndata; fast", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 27, 65, 27, 60); arrow(ax, 27, 50, 27, 45)
    note(ax, 73, 82, "Vision Transformer", color=RED, size=13, bold=True)
    box(ax, 73, 70, 26, 10, "Cut image into\npatches (tokens)", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 73, 55, 26, 10, "Attention: every\npatch sees all", fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    box(ax, 73, 40, 26, 10, "Needs more data;\nscales strongly", fill=GREEN_F, edge=GREEN, size=10, bold=False)
    arrow(ax, 73, 65, 73, 60); arrow(ax, 73, 50, 73, 45)
    caption(ax, "CNN = local filters; ViT = patches + attention. Both output a feature vector (embedding).")
    save(fig, p("m14_03_cnn_vs_vit.png"))


# ----------------------------------------------------------------------
# 04  Visual search: embed image -> ANN lookup
# ----------------------------------------------------------------------
def d04():
    fig, ax = new_canvas()
    title(ax, "Visual Search — embed the image, then nearest-neighbour lookup")
    box(ax, 14, 60, 18, 12, "Query\nimage", fill=BLUE_F, size=11)
    box(ax, 38, 60, 18, 12, "CV model\n-> embedding\n(vector)", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 64, 60, 18, 12, "ANN index\n(vector DB)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 88, 60, 18, 12, "Top-K\nsimilar\nimages", fill=NAVY, tcolor="white", size=10)
    arrow(ax, 23, 60, 29, 60)
    arrow(ax, 47, 60, 55, 60)
    arrow(ax, 73, 60, 79, 60)
    box(ax, 64, 34, 30, 12, "Offline: embed the\nwhole catalog once,\nbuild the index", fill=BLUE_F, size=10, bold=False)
    arrow(ax, 64, 40, 64, 54, color=GRAY, dashed=True)
    caption(ax, "Same trick as text search (see M13/M16): map to a vector, compare by distance.")
    save(fig, p("m14_04_visual_search.png"))


# ----------------------------------------------------------------------
# 05  Data augmentation for images
# ----------------------------------------------------------------------
def d05():
    fig, ax = new_canvas()
    title(ax, "Image Augmentation — one image becomes many")
    box(ax, 16, 62, 20, 14, "Original\ntraining\nimage", fill=BLUE_F, size=11)
    augs = [
        (48, 78, "Flip\n(left-right)"),
        (48, 60, "Random crop\n/ resize"),
        (48, 42, "Color jitter\n(brightness)"),
        (78, 78, "Rotate /\nshift"),
        (78, 60, "Cutout /\nerase patch"),
        (78, 42, "Add noise /\nblur"),
    ]
    for x, y, t in augs:
        box(ax, x, y, 22, 12, t, fill=ORANGE_F, edge=ORANGE, size=10, bold=False)
    arrow(ax, 26, 62, 37, 76)
    arrow(ax, 26, 62, 37, 60)
    arrow(ax, 26, 62, 37, 44)
    caption(ax, "Why: more variety = model generalizes; label stays the same (a flipped cat is still a cat).")
    save(fig, p("m14_05_augmentation.png"))


# ----------------------------------------------------------------------
# 06  Serving CV models: batching on the GPU
# ----------------------------------------------------------------------
def d06():
    fig, ax = new_canvas()
    title(ax, "Serving CV Models — batch requests to fill the GPU")
    box(ax, 14, 74, 14, 9, "Req A", fill=BLUE_F, size=10)
    box(ax, 14, 62, 14, 9, "Req B", fill=BLUE_F, size=10)
    box(ax, 14, 50, 14, 9, "Req C", fill=BLUE_F, size=10)
    box(ax, 40, 62, 20, 16, "Batcher\n(wait a few ms,\ngroup requests)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 70, 62, 20, 16, "GPU\nruns batch\nin parallel", fill=GREEN, tcolor="white", size=11)
    arrow(ax, 21, 74, 30, 65)
    arrow(ax, 21, 62, 30, 62)
    arrow(ax, 21, 50, 30, 59)
    arrow(ax, 50, 62, 60, 62)
    note(ax, 50, 34, "Trade-off:  bigger batch = higher throughput  BUT  more waiting = higher latency", size=11, color=RED, bold=True)
    note(ax, 50, 24, "Also: smaller image size + FP16/INT8 = faster, cheaper inference", size=10)
    caption(ax, "GPUs are fast only when fed full batches; a lone image wastes the chip.")
    save(fig, p("m14_06_serving_batching.png"))


# ----------------------------------------------------------------------
# 07  Content moderation flow (case study)
# ----------------------------------------------------------------------
def d07():
    fig, ax = new_canvas()
    title(ax, "Case Study: Image Content Moderation")
    box(ax, 14, 62, 17, 12, "User\nuploads\nimage", fill=BLUE_F, size=10)
    box(ax, 37, 62, 17, 12, "CV model\nscores\nrisk", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 60, 62, 17, 12, "Threshold\n+ policy\nrules", fill=ORANGE_F, edge=ORANGE, size=10)
    arrow(ax, 22, 62, 29, 62)
    arrow(ax, 45, 62, 52, 62)
    box(ax, 84, 76, 17, 10, "Allow\n(low risk)", fill=GREEN, tcolor="white", size=10)
    box(ax, 84, 62, 17, 10, "Auto-block\n(high risk)", fill=RED, tcolor="white", size=10)
    box(ax, 84, 48, 17, 10, "Human\nreview\n(gray zone)", fill=BLUE_F, size=9)
    arrow(ax, 68, 64, 76, 75)
    arrow(ax, 68, 62, 76, 62)
    arrow(ax, 68, 60, 76, 50)
    note(ax, 50, 30, "Reviewer labels feed back -> retrain the model (the loop from M01)", size=10, color=NAVY)
    caption(ax, "High volume + high stakes: tune recall for harmful content, keep humans on the gray zone.")
    save(fig, p("m14_07_moderation.png"))


# ----------------------------------------------------------------------
# 08  OCR pipeline (case study)
# ----------------------------------------------------------------------
def d08():
    fig, ax = new_canvas()
    title(ax, "Case Study: OCR — turning a picture of text into text")
    box(ax, 13, 58, 17, 13, "Document\nimage", fill=BLUE_F, size=10)
    box(ax, 35, 58, 17, 13, "Detect\ntext regions\n(boxes)", fill=ORANGE_F, edge=ORANGE, size=10)
    box(ax, 57, 58, 17, 13, "Recognize\ncharacters\nin each box", fill=GREEN_F, edge=GREEN, size=10)
    box(ax, 80, 58, 18, 13, "Assemble\ntext + layout", fill=NAVY, tcolor="white", size=10)
    arrow(ax, 21, 58, 27, 58)
    arrow(ax, 43, 58, 49, 58)
    arrow(ax, 65, 58, 71, 58)
    note(ax, 50, 32, "Detection task  +  sequence recognition task, chained together", size=11, color=NAVY)
    caption(ax, "OCR = find where text is, then read it. Used in receipts, IDs, medical forms, search.")
    save(fig, p("m14_08_ocr.png"))


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05(); d06(); d07(); d08()
    print("All Module 14 diagrams generated.")
