---
title: "Module 14 — Computer Vision Systems"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 14 — Computer Vision Systems

> **Why this module exists.**
> A huge share of real-world ML is about *pixels*: recognising a product from a
> photo, flagging a harmful image, reading a receipt, spotting a tumour on a
> scan. Computer Vision (CV) is where ML first became magic for the public, and
> it is still one of the most common design-interview topics. The good news:
> once you understand the ML lifecycle from Module 1, CV is *the same lifecycle*
> with an image-shaped front end. The trap most candidates fall into is
> obsessing over model architectures (ResNet vs ViT vs YOLO) and forgetting the
> boring parts — preprocessing, augmentation, batching, latency — that actually
> decide whether the system ships. This module keeps you honest: we cover the
> tasks, the pipeline, embeddings, data, serving, and four case studies, all in
> plain English and first-principles style.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★★★        | ★★★★★     | ★★★★★       |

**What you must be able to do after this module:**
name the three core CV tasks (classification, detection, segmentation) and what
each *outputs*; draw the CV pipeline (raw image → preprocess → model →
postprocess); explain CNN vs ViT in one sentence each; design visual search with
image embeddings + an ANN index; justify why image augmentation matters and name
the common transforms; reason about CV serving (image size, batching, GPU,
latency vs throughput); and sketch a 7-step design for visual search, content
moderation, OCR, and medical imaging.

> **How to read this module.** As always: **problem → simplest attempt → why it
> breaks → the fix.** We tie every idea back to the lifecycle (M01) and forward
> to embeddings/retrieval (M13, M16) and serving/monitoring (M08, M10).

---

## 14.1 The Three Core Vision Tasks

### Motivation (the problem that existed)

"Do something with this image" is not a spec. Before you design anything, you
must pin down *what the system outputs*. There are three canonical tasks, and
they differ in how much detail the answer carries — and therefore in cost,
label effort, and latency.

![Three CV tasks side by side: classification outputs one label, detection outputs boxes plus labels, segmentation outputs a per-pixel mask.](images/m14_01_cv_tasks.png)

### The three tasks (what each one outputs)

- **Image classification** — one label for the *whole* image. "Is this a cat?"
  "Is this photo NSFW?" The output is a class (or a probability per class). This
  is the cheapest task: labels are just tags, and the model is a single forward
  pass ending in a softmax.
- **Object detection** — find *each* object and draw a **bounding box** around
  it, with a label. "There is a cat at (x, y, w, h) and a dog at (…)." Output is
  a *list* of boxes + labels + confidences. Harder to label (someone must draw
  boxes) and harder to serve (variable number of outputs, needs post-processing).
- **Semantic / instance segmentation** — assign a label to **every pixel** (a
  *mask*). "These pixels are road, those are pedestrian." The richest and most
  expensive output; labelling a single image can take many minutes.

### First-principles: pick the *cheapest* task that answers the question

Interviewers love this move. If the product only needs "is there a weapon in
this image?", that is **classification** — do not propose pixel-perfect
segmentation. Detection and segmentation cost more data, more label money, more
compute, and more latency. Match the task to the *decision the product must
make*, not to what looks impressive. As the diagram shows, output richness (and
cost) rises left to right.

> **Senior signal:** downgrading a task ("we can start with classification and
> only add detection if the box location actually changes a user decision")
> shows judgment about complexity and cost — exactly the M01 lesson.

---

## 14.2 The Computer-Vision Pipeline (End to End)

### Motivation

A model is a box in the middle of a pipeline. In CV, the code *around* the model
— decoding the image bytes, resizing, normalising, then turning raw model
outputs into a clean answer — is where most production bugs live. If you resize
differently in training and serving, you get **training-serving skew** (M05) and
your live accuracy quietly tanks.

![The CV pipeline: raw image goes through preprocess, then the model backbone, then postprocess, producing a label, boxes, or mask.](images/m14_02_cv_pipeline.png)

### The four stages

1. **Raw image.** Bytes from an upload, a camera frame, or a stored file. Could
   be JPEG/PNG, different sizes, different colour spaces, even corrupt.
2. **Preprocess (code, not model).** Decode the bytes, **resize** to the model's
   expected input (e.g. 224×224), convert colour (RGB order), and **normalize**
   pixel values (subtract mean, divide by std). *This exact recipe must match
   training.* Small mismatches (BGR vs RGB, wrong mean) silently degrade quality.
3. **Model (the backbone).** A CNN or Vision Transformer that turns pixels into a
   prediction — or, one layer earlier, into an **embedding** (a feature vector we
   reuse in Section 14.4).
4. **Postprocess (code, not model).** Turn raw outputs into a usable answer:
   **softmax** for classification, **Non-Max Suppression (NMS)** to remove
   duplicate boxes in detection, **thresholding** a mask in segmentation.

### Why the "boring" stages matter most

As the diagram's caption says: preprocess and postprocess are *code*, but they
cause most bugs. A model that scores 95% offline can score 70% live purely
because the serving path resizes with a different interpolation than training
did. The fix is to **share one preprocessing function** between training and
serving (the same lesson as the feature store in M05).

---

## 14.3 Backbones: CNN → ViT (Briefly)

### Motivation

The "model" box has a history worth one paragraph of your interview. You do not
need to derive backprop through convolutions — you need to explain *how* each
family looks at an image and *when* you'd pick which.

![CNN vs Vision Transformer: CNNs slide local filters and stack layers; ViTs cut the image into patches and use attention so every patch sees every other.](images/m14_03_cnn_vs_vit.png)

### CNN (Convolutional Neural Network)

A CNN **slides small filters** across the image, detecting edges, then textures,
then shapes, then objects as you stack more layers — moving from *local* detail
to *global* meaning. CNNs (ResNet, EfficientNet) are **data-efficient and fast**,
which is why they still dominate on-device and low-data settings.

### ViT (Vision Transformer)

A ViT **cuts the image into patches**, treats each patch like a word token, and
uses **attention** so *every patch can look at every other patch* from layer one.
ViTs are hungrier for data but **scale extremely well** — with enough data and
compute they beat CNNs, which is why large foundation vision models are
transformer-based.

### How to choose (one line)

- **Little data / tight latency / on-device** → CNN.
- **Lots of data / large-scale / transfer from a big pretrained model** → ViT.
- Both end in the same useful artifact: **a feature vector (embedding)** we can
  classify *or* search with. That bridge is the next section.

> **Practical note:** you almost never train a backbone from scratch. You take a
> model **pretrained** on a huge dataset and **fine-tune** it on your data —
> cheaper, faster, and better with limited labels (transfer learning).

---

## 14.4 Visual Search & Image Embeddings

### Motivation (the problem)

"Find products that look like this photo" cannot be solved by exact matching —
no two photos are identical. We need a notion of *visual similarity*. The trick
is the same one used for text search in Modules 13 and 16: turn the image into a
**vector (embedding)** where *similar images sit close together*, then find
nearest neighbours.

![Visual search flow: the query image is embedded into a vector, looked up in an ANN vector index, and the top-K most similar catalog images are returned.](images/m14_04_visual_search.png)

### How visual search works

1. **Embed the query.** Run the image through the CV model, but take the
   feature vector from just before the final classification layer. That vector
   is the image's "meaning" in a few hundred numbers.
2. **Search an index.** Compare that vector against millions of catalog vectors
   using **Approximate Nearest Neighbour (ANN)** search (FAISS, ScaNN, HNSW) —
   the same vector-DB machinery from M16. Exact search over millions of vectors
   is too slow; ANN trades a tiny bit of accuracy for huge speed.
3. **Return top-K.** The closest vectors are the most visually similar images.

### The offline/online split (crucial)

As the diagram shows, you **embed the whole catalog once, offline**, and build
the index ahead of time. At query time you only embed *one* image and do a fast
lookup. This is the same batch-precompute + online-serve hybrid from M01. When
the catalog changes, you re-embed the new items and update the index.

> **Cross-links:** embeddings and similarity are covered deeply in **Module 13**;
> ANN indexes and vector databases in **Module 16**. Visual search is just those
> tools with an *image* encoder in front. The same embeddings also power
> de-duplication, "more like this" recommendations, and reverse image search.

---

## 14.5 Data & Augmentation Pipelines for Images

### Motivation

Vision models are data-hungry and overfit easily — a model can memorise the
exact training photos (same lighting, same angle) and then fail on a slightly
different real photo. We rarely have enough labelled images to cover every
variation. **Augmentation** manufactures that variety for free.

![Image augmentation fan-out: one original training image produces flipped, cropped, colour-jittered, rotated, cutout, and noisy versions.](images/m14_05_augmentation.png)

### What augmentation is

Take one training image and produce many **label-preserving** variants by
applying random transforms *on the fly* during training:

- **Flip** (left-right) — a mirrored cat is still a cat.
- **Random crop / resize** — teaches the model that objects appear at different
  scales and positions.
- **Color jitter** — vary brightness, contrast, saturation, so lighting doesn't
  fool the model.
- **Rotate / shift**, **cutout / random erase** (hide a patch so the model can't
  rely on one feature), and **noise / blur** for robustness.

### Why it works (first principles)

Each transform is a variation the model *will* see in the real world. By showing
the model these variations at training time, you force it to learn the *object*
rather than the *photo*. The **label stays the same** — that is the whole trick,
and it is what makes augmentation "free" extra data.

### Pitfalls

- **Label-changing transforms.** A vertical flip of a "6" makes a "9"; flipping
  a road sign can change its meaning. Only use transforms that preserve the
  label for *your* task.
- **Train-only.** Augment during training, **not** at evaluation/serving —
  otherwise you measure the wrong thing.
- **Class imbalance still matters.** Augmentation adds variety, not new *classes*;
  a rare class with 5 images is still rare. Combine with resampling.

---

## 14.6 Serving CV Models: Latency, Batching, GPU

### Motivation

Image models are heavy. A single high-resolution inference can be tens of
milliseconds even on a GPU. Serve them naively — one image at a time — and you
waste the GPU and blow your latency budget under load. Serving is where a lot of
CV interviews are actually won.

![Serving CV models: incoming requests A, B, C are grouped by a batcher and run together on the GPU in parallel; a bigger batch means higher throughput but more waiting.](images/m14_06_serving_batching.png)

### The three serving levers

1. **Image size.** Inference cost grows roughly with the *number of pixels*.
   Halving each side quarters the compute. Serve the *smallest* resolution that
   still meets accuracy — a classic accuracy-vs-cost trade.
2. **Batching.** GPUs are parallel machines: they run 32 images almost as fast as
   1. A **dynamic batcher** waits a few milliseconds, groups pending requests,
   and runs them together. As the diagram warns, **bigger batch = higher
   throughput but more waiting = higher latency.** You tune the max batch size
   and max wait to hit your p99.
3. **Precision / hardware.** Use **FP16 or INT8** (quantization, M08) to run
   faster and cheaper with little accuracy loss; pick the right GPU; use
   optimised runtimes (TensorRT, ONNX Runtime).

### Latency vs throughput (the core tension)

- **Latency** = how long *one* request waits. Users feel this.
- **Throughput** = how many images/second the whole system handles. Cost feels
  this.
- Batching *raises throughput* but *adds latency* (requests wait to be grouped).
  A lone image wastes the chip; an over-large batch makes users wait. The art is
  a batch size and timeout that satisfy the p99 budget at peak QPS.

> **Design pattern:** for real-time paths (moderation on upload) keep batches
> small and latency low; for offline paths (re-embed the whole catalog nightly)
> use huge batches to maximise throughput and minimise cost. Same model, two
> serving modes — the hybrid idea from M01.

---

## 14.7 Case Study: Visual Search (7-step sketch)

Use the M02 framework, specialised for images.

1. **Clarify.** "Find visually similar products from a photo." Scale: 50M catalog
   images, 5k queries/sec peak, p99 < 200 ms, results must feel relevant.
2. **Frame.** Not classification — a **retrieval** problem. Metric offline:
   recall@K / precision@K; online: click-through and add-to-cart on results.
3. **Data.** Catalog images + labels/attributes; user click logs as weak
   relevance signals for training the embedding.
4. **Model.** A CNN/ViT backbone fine-tuned with a **contrastive / metric-learning**
   loss so similar items get close embeddings (see M13).
5. **Index (offline).** Embed all 50M images, build an **ANN index** (M16),
   refresh as the catalog changes.
6. **Serve (online).** Embed the query image, ANN lookup, return top-K, re-rank
   by business rules (in stock, price).
7. **Monitor & iterate.** Track click-through, embedding drift, index freshness;
   re-embed and rebuild on a schedule.

---

## 14.8 Case Study: Image Content Moderation (7-step sketch)

![Content moderation flow: user uploads an image, the CV model scores risk, threshold + policy rules route to allow, auto-block, or human review; reviewer labels feed back to retraining.](images/m14_07_moderation.png)

1. **Clarify.** Block harmful images (violence, nudity) at upload. Very high
   volume, real-time, legal stakes.
2. **Frame.** Multi-label **classification** (risk score per category). Cost of a
   **false negative** (harmful content slips through) is high → tune for
   **recall**.
3. **Data.** Labelled harmful/safe images; heavily imbalanced; sensitive — handle
   with care and reviewer well-being in mind.
4. **Model.** Fine-tuned classifier; augment safe class; calibrate scores.
5. **Decide.** As the diagram shows, apply **thresholds + policy rules**:
   low risk → **allow**, high risk → **auto-block**, gray zone → **human review**.
6. **Serve.** Real-time, low-latency, small batches on upload; kill-switch and
   shadow mode for new models (M10).
7. **Monitor & loop.** Reviewer decisions become fresh labels that **retrain** the
   model — the feedback loop from M01. Watch for adversarial evasion (drift).

> High volume **and** high stakes = the scariest quadrant from M01's cost-of-wrong
> 2×2. Humans stay in the loop on the gray zone.

---

## 14.9 Case Study: OCR (7-step sketch)

![OCR pipeline: a document image goes through text-region detection, then character recognition per box, then assembly into text plus layout.](images/m14_08_ocr.png)

Optical Character Recognition = *find where the text is, then read it*. It chains
**two** CV tasks, as the diagram shows.

1. **Clarify.** Extract text from receipts / IDs / forms; must handle skew, blur,
   many fonts and languages.
2. **Frame.** **Detection** (find text regions) **+ sequence recognition** (read
   characters in each region). Metric: character/word error rate.
3. **Data.** Real + synthetic documents (render text on backgrounds — cheap,
   scalable augmentation); box + transcript labels.
4. **Model.** Text detector (like object detection) → recognizer (CNN/transformer
   producing a character sequence).
5. **Postprocess.** Assemble characters into words, restore **layout** (lines,
   tables), apply a dictionary/language model to fix errors.
6. **Serve.** Often batch (process uploaded documents); GPU batching for scale.
7. **Monitor.** Track error rate by document type; new form layouts = drift →
   collect and retrain.

---

## 14.10 Case Study: Medical Imaging (7-step sketch)

1. **Clarify.** Flag a finding (e.g. a tumour) on an X-ray/CT. **Extremely high
   stakes**, regulated, must be explainable.
2. **Frame.** Classification ("finding present?") or **segmentation** (outline the
   region for a radiologist). Cost of a **false negative** is severe → optimise
   recall/sensitivity; keep a **human (doctor) in the loop** — the model
   *assists*, it does not decide.
3. **Data.** Small, expensive, expert-labelled datasets; strong **privacy** (HIPAA)
   constraints; class imbalance (few positives).
4. **Model.** Fine-tune a pretrained backbone (transfer learning shines with
   little data); heavy, *label-safe* augmentation.
5. **Evaluate.** Sensitivity/specificity, ROC-AUC; test across scanners and
   hospitals to avoid a model that only works on one machine (a subtle drift).
6. **Serve.** Latency is relaxed (not millisecond-critical); batch is fine.
   Provide **explainability** (heatmaps) so clinicians can trust and check it
   (M18).
7. **Monitor.** Watch performance across sites and over time; regulatory audit
   trail; retrain with new confirmed cases.

> Same lifecycle, but the **cost-of-wrong** dial is turned to maximum: human
> oversight, explainability, and rigorous evaluation are non-negotiable.

---

## Module 14 — Interview Mapping (what companies probe)

| Company | How Module 14 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | "Design visual search / a photo tagger" | Names a fancy backbone | Embeddings + ANN index, offline embed / online lookup, monitoring |
| **Amazon / Pinterest** | Product visual search at scale | Talks accuracy only | Latency budget, batching, index refresh, cost per query |
| **Meta / TikTok** | Image/video content moderation | Single threshold | Recall focus, human-in-loop gray zone, feedback loop, adversarial drift |
| **Health / fintech** | Medical imaging, document OCR | Model-centric | Cost-of-wrong, explainability, privacy, evaluation across sites |

**Common opener:** *"Design visual search for our app."* Your first 60 seconds:
clarify scale + latency, frame it as **retrieval** (embeddings + ANN), sketch the
**offline embed / online lookup** split, and name monitoring. That structure
alone beats most candidates.

---

## Module 14 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **GATE CS / DA:** may ask conceptual CV — what a CNN/convolution is,
  classification vs detection vs segmentation, what image augmentation does.
  Sections 14.1–14.3 and 14.5 cover this. Deep serving trade-offs are not tested.
- **SEBI IT / RBI IT / ISRO:** at most definitional AI/ML questions; CV *system
  design* is essentially **interview-only**.

> **Flag:** the case-study and serving material here is interview/role value; the
> task definitions, CNN/ViT idea, and augmentation carry the exam value.

---

## Module 14 — Common Mistakes & Misconceptions

1. **Jumping to the fanciest model.** The task choice (classification vs detection
   vs segmentation) and the pipeline matter more than ResNet-vs-ViT. (14.1–14.2.)
2. **Ignoring preprocessing skew.** Different resize/normalize in training vs
   serving silently kills live accuracy. Share one function. (14.2.)
3. **"Visual search = classify the image."** No — it is *retrieval*: embed + ANN
   nearest-neighbour. (14.4.)
4. **Forgetting the offline/online split.** Embed the catalog once offline;
   embed only the query online. (14.4.)
5. **Augmenting at eval/serving time**, or using **label-changing** transforms
   (flipping a "6"). (14.5.)
6. **Serving one image at a time.** Wastes the GPU; batching raises throughput —
   but adds latency, so tune it. (14.6.)
7. **Treating medical/moderation like movie recs.** High cost-of-wrong needs
   human-in-loop, recall focus, and explainability. (14.8, 14.10.)

---

## Module 14 — MCQs (with answers & explanations)

**Q1.** Which task outputs a label for *every pixel*?
a) Classification  b) Detection  c) Segmentation  d) Regression

<details><summary>Answer</summary>**c.** Segmentation produces a per-pixel mask.
Classification gives one label for the whole image; detection gives boxes +
labels. (Section 14.1.)</details>

**Q2.** A CV model scores 95% offline but 70% live, with no code change to the
model itself. The most likely cause is:
a) The GPU is too slow
b) Preprocessing (resize/normalize) differs between training and serving
c) The learning rate was wrong
d) Too much augmentation

<details><summary>Answer</summary>**b.** Training-serving skew in the *preprocess*
step is a classic CV bug. Share one preprocessing function. (Section 14.2.)</details>

**Q3.** Visual search over 50M images is best implemented as:
a) Compare the query to all 50M with exact distance every time
b) Classify the query into one of 50M classes
c) Embed images into vectors and use an ANN index (embed catalog offline)
d) Store images in a SQL table and use LIKE

<details><summary>Answer</summary>**c.** Embed to vectors, build an ANN index
offline, look up the query online. Exact search over 50M per query is too slow.
(Section 14.4; see M16.)</details>

**Q4.** Why do we use image augmentation?
a) To make training faster
b) To create label-preserving variety so the model generalises
c) To increase image resolution
d) To reduce the number of classes

<details><summary>Answer</summary>**b.** Random flips/crops/jitter add real-world
variety while keeping the label the same, reducing overfitting. (Section 14.5.)</details>

**Q5.** In CV serving, increasing the batch size generally:
a) Lowers both latency and throughput
b) Raises throughput but can raise latency (requests wait to be grouped)
c) Has no effect on a GPU
d) Always lowers latency

<details><summary>Answer</summary>**b.** Bigger batches use the GPU more
efficiently (higher throughput) but requests wait to be batched (higher latency).
Tune to the p99 budget. (Section 14.6.)</details>

**Q6.** For image content moderation of harmful content, you should usually tune
for high:
a) Precision, ignoring recall
b) Recall, because a false negative (harmful content slips through) is costly
c) Throughput only
d) Batch size

<details><summary>Answer</summary>**b.** Missing harmful content is the expensive
error, so favour recall, and route the gray zone to human review. (Section 14.8.)</details>

**Q7.** CNN vs ViT — which is generally more data-efficient?
a) ViT  b) CNN  c) They are identical  d) Neither uses data

<details><summary>Answer</summary>**b.** CNNs' local filters build in a helpful
prior, so they need less data; ViTs need more data but scale better with it.
(Section 14.3.)</details>

**Q8.** OCR is best framed as:
a) A single classification model
b) Detection (find text regions) + sequence recognition (read them)
c) Segmentation only
d) A database lookup

<details><summary>Answer</summary>**b.** OCR chains a text detector with a
character/sequence recognizer, then assembles text + layout. (Section 14.9.)</details>

---

## Module 14 — Design Exercises (easy → hard)

- **Easy.** For each, name the CV task: (1) "is this photo a dog?"; (2) "count
  and locate every car in a street photo"; (3) "colour each pixel road vs
  sidewalk"; (4) "find shirts that look like this one". *(1 classification,
  2 detection, 3 segmentation, 4 retrieval/embeddings.)*
- **Medium.** Draw the CV pipeline for a plant-identification app. Name one thing
  that could differ between training and serving preprocessing, and how you'd
  prevent it.
- **Medium.** List five augmentations you'd use for a *road-sign* classifier and
  one you must **avoid**, with reasons.
- **Hard.** Design visual search for 100M product images at 10k QPS, p99 < 150 ms.
  Specify the offline vs online split, the index, batch strategy, and what breaks
  at 10× traffic.
- **Hard.** Design an image-moderation system. Define your thresholds/routing,
  where humans sit, how the feedback loop works, and how you'd detect adversarial
  users trying to evade the model.

---

## Module 14 — Concept Review (one page)

- **Three tasks:** classification (one label) · detection (boxes + labels) ·
  segmentation (per-pixel mask). Pick the *cheapest* that answers the question.
- **Pipeline:** raw image → **preprocess** (decode/resize/normalize) → **model**
  (CNN/ViT) → **postprocess** (softmax/NMS/threshold). Preprocess/postprocess are
  code and cause most bugs; share one function to avoid **skew**.
- **CNN** = local sliding filters, data-efficient, fast. **ViT** = patches +
  attention, data-hungry, scales strongly. Both output an **embedding**.
- **Visual search** = embed image → **ANN** nearest-neighbour lookup. Embed the
  catalog **offline**, embed the query **online** (M13/M16).
- **Augmentation** = label-preserving random transforms (flip, crop, jitter,
  cutout) → more variety, less overfitting. Train-only; avoid label-changing ones.
- **Serving levers:** image size, **batching** (throughput ↑, latency ↑),
  precision (FP16/INT8). Balance latency vs throughput to the p99 budget.
- **Case studies:** visual search (retrieval), moderation (recall + human loop),
  OCR (detect + recognize), medical (high stakes, explainable, human-in-loop).

---

## Module 14 — Flash Cards (Q → A)

1. Three core CV tasks? → *Classification (label), detection (boxes),
   segmentation (per-pixel mask).*
2. CV pipeline in one line? → *raw → preprocess → model → postprocess.*
3. Why does live accuracy drop with no model change? → *Preprocessing skew
   (train vs serve resize/normalize differ).*
4. CNN vs ViT? → *CNN = local filters, data-efficient; ViT = patches + attention,
   scales with data.*
5. How does visual search work? → *Embed image → ANN nearest-neighbour lookup;
   catalog embedded offline.*
6. Why augment images? → *Label-preserving variety → better generalisation, less
   overfitting.*
7. Batching trade-off? → *Higher throughput but higher latency.*
8. Moderation metric focus? → *Recall (false negatives are costly); humans on the
   gray zone.*

---

## Module 14 — Pattern Recognition (how to spot it in an interview)

- Hear **"find similar images / photos"** → embeddings + ANN retrieval (M13/M16),
  offline embed + online lookup.
- Hear **"detect / locate objects"** → detection task, boxes + NMS in postprocess.
- Hear **"label every pixel / outline the region"** → segmentation.
- Hear **"real-time, high QPS, GPU cost"** → image size + dynamic batching +
  FP16/INT8; latency-vs-throughput trade.
- Hear **"harmful content / safety"** → recall focus, thresholds + human-in-loop,
  feedback loop, adversarial drift.
- Hear **"offline great, live bad"** → preprocessing skew; share one function.
- Hear **"few labels / expensive labels"** → transfer learning + augmentation.

---

## Module 14 — Revision Notes / Mini Cheat Sheet

```
CV TASKS:   classification (1 label) | detection (boxes+labels) | segmentation (per-pixel mask)
            -> pick the CHEAPEST task that answers the product question

PIPELINE:   raw image -> PREPROCESS(decode,resize,normalize) -> MODEL(CNN/ViT) -> POSTPROCESS(softmax/NMS/threshold)
            pre/post = CODE, not model -> #1 bug = train/serve SKEW -> share ONE function

BACKBONES:  CNN = local sliding filters, data-efficient, fast (on-device)
            ViT = image->patches + attention, data-hungry, scales best
            both END in an EMBEDDING (feature vector)  ->  usually FINE-TUNE a pretrained model

VISUAL SEARCH:  embed image -> ANN nearest-neighbour (FAISS/HNSW, see M16)
                embed CATALOG offline (batch) | embed QUERY online  -> top-K similar

AUGMENTATION:   flip | crop/resize | color jitter | rotate/shift | cutout | noise
                label-PRESERVING, TRAIN-only, avoid label-changing (flip a 6 -> 9)

SERVING:    levers = image SIZE | BATCHING | precision(FP16/INT8)
            batch: throughput UP but latency UP  -> tune to p99;  lone image wastes GPU

CASE STUDIES:  visual search(retrieval) | moderation(recall+human loop) | OCR(detect+recognize) | medical(high-stakes, explainable)
COST-OF-WRONG:  moderation & medical = HIGH -> human-in-loop, recall, explainability (M18), privacy
```

---

> **Next module:** *Module 15 — Natural Language Processing Systems.* We swap
> pixels for text: tokenization, text classification, embeddings for NLP, and how
> the same "embed → retrieve" pattern from visual search powers semantic text
> search — carrying us toward LLMs and RAG.
