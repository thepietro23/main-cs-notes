---
title: "Module 20 — ML System Design Interview Mastery"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 20 — ML System Design Interview Mastery

> **Why this module exists.**
> You have now learned the whole toolkit: the lifecycle (M1), the 7-step
> framework (M2), framing, data, features, training, evaluation, serving,
> MLOps, monitoring, scaling, and the deep-dive systems (recommendation,
> search, vision, NLP, LLMs), and you have seen flagship designs assembled end
> to end (M17). **Knowing all of that is necessary but not sufficient.** The
> interview is a *performance*: 45 minutes, a blank whiteboard, a stranger
> grading you, and a wide-open prompt. This module is about **winning that
> performance** — recognising which of a small set of question patterns you are
> facing, budgeting your time, tuning your answer to the company in the room,
> running a clean mock from problem to follow-ups, recovering when you get
> stuck, avoiding the red flags that quietly fail people, and layering the
> extra reasoning that earns the *Staff* bar. Everything here is in plain
> English, and every idea is something you can *do out loud* under pressure.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★       | ★      | ★          | ★★★★★     | ★★★★★       |

> **Flag — this is an interview-only module.** Written exams (SEBI / RBI / GATE
> / ISRO) do not test how you drive a design conversation, tune to a company,
> or recover from a curveball. If you are studying purely for a written paper,
> skim this. If you are preparing for FAANG / AI-engineer / staff interviews,
> this is one of the highest-leverage modules in the whole course — it converts
> knowledge into offers.

**What you must be able to do after this module:**
map any cold prompt to one of eight question patterns in the first minute and
name the module to borrow the blueprint from; run a clean 45-minute timeline
that never starves serving and monitoring; adapt the *same* core answer to
Google, Meta, Amazon, Netflix, Apple, OpenAI/Anthropic, NVIDIA, and
Uber/Airbnb/Stripe; run a full mock — problem → clarifying questions → 7-step
design → follow-ups → what a Staff answer adds; recover gracefully from "I
don't know", scope creep, and curveballs; self-audit against the red-flag
checklist; and know exactly what separates a junior, senior, and staff answer.

> **How to read this module.** Treat it as a *rehearsal manual*, not a reading.
> For each section, close the book and try to perform it out loud. The mock
> walkthroughs in 20.4 are the core — do them like flashcards until the *shape*
> is automatic. We cross-link to Module 17 for the full designs rather than
> repeating them; here we focus on the *delivery*.

---

## 20.1 The Eight Question Patterns (Recognise, Then Reuse)

### Motivation (the problem that existed)

Every candidate fears the "unseen" question. But here is the secret that calms
you down: **almost every ML system design prompt is one of about eight
patterns.** "Design TikTok's For-You feed", "rank Instagram posts", "recommend
who to follow" — all the same recommendation/ranking skeleton. Once you can map
a prompt to its pattern in the first sixty seconds, you are no longer improvising
from nothing; you are *adapting a blueprint you already own*.

![Eight labelled boxes grouping the interview question patterns: recsys (feed, PYMK), ranking/search, CTR/ads, fraud/anomaly, ETA/regression, LLM/RAG, serving/infra, and graph/PYMK — with a caption that most prompts are one of these eight, so you map prompt to pattern to a known blueprint.](images/m20_01_question_patterns.png)

### The pattern → company → module map (memorise the shape)

This is your **question bank**. Read a prompt, find the row, and you instantly
know the skeleton, the metric, the gotcha, and which module holds the full
design.

| Pattern | Sounds like… | Companies that love it | Study module |
|---------|--------------|------------------------|--------------|
| **Recsys (feed, home, PYMK)** | "For-You feed", "home recommendations", "who to follow" | Meta, YouTube/Google, TikTok, LinkedIn, Netflix, Spotify | **M12**, M17.2–17.3 |
| **Ranking / Search** | "rank search results", "product search", "similar listings" | Google, Amazon, Airbnb, Etsy, Pinterest | **M13**, M17.7 |
| **CTR / Ads** | "predict click probability", "ad ranking", "auction" | Google, Meta, Amazon Ads, Criteo | **M12**, M17.4 |
| **Fraud / Anomaly** | "detect fraud", "flag abuse", "spam / harmful content" | Stripe, PayPal, banks, Meta integrity | **M10**, M17.5 |
| **ETA / Regression** | "predict delivery time", "estimate price", "forecast demand" | Uber, DoorDash, Lyft, Instacart | **M6/M7**, M17.6 |
| **LLM / RAG** | "answer from our docs", "build an assistant", "summarise" | OpenAI, Anthropic, startups, enterprises | **M16**, M17.8 |
| **Serving / Infra** | "serve this at 1M QPS", "cut latency/cost", "on-device" | NVIDIA, infra teams, Apple (edge) | **M8/M11/M19** |
| **Graph / PYMK** | "people you may know", "link prediction", "fraud rings" | LinkedIn, Meta, payments risk | **M12**, M17.9 |

> **Senior signal:** open your answer by *naming the pattern out loud* — "This
> is a two-stage retrieval-and-ranking problem, like a feed; I'll reuse that
> funnel." The interviewer immediately sees you have a map, not just facts.

### First-principles: why so few patterns exist

There are only a handful of *shapes* an ML product can take, because there are
only a handful of things a model can output: **a label** (classification →
fraud, CTR), **a number** (regression → ETA), **an ordering** (ranking →
search, feed), **a retrieved set** (retrieval → recsys candidates, RAG), or
**generated text** (generation → LLM). Every business prompt is one of these
wearing different clothes. Learn the five outputs and the eight patterns fall
out naturally.

---

## 20.2 The Ideal 45-Minute Timeline

### Motivation

The most common way a *knowledgeable* candidate fails is **time**. They spend 25
minutes lovingly designing the model, then the interviewer says "we're almost out
of time" and they never mentioned serving, scale, or monitoring — the exact
things that separate senior from junior. Managing the clock is itself a graded
skill, and you must manage it *out loud*.

![A five-stage vertical timeline for a 45-minute interview: 0-5 min clarify goal/scope/constraints; 5-10 min frame as ML and pick the metric; 10-25 min data, features, and model (marked spend MOST time here); 25-38 min serving, scale, and monitoring; 38-45 min trade-offs, follow-ups, and wrap, with a caption to budget time out loud and never spend 40 minutes on the model.](images/m20_02_45min_timeline.png)

### The budget, phase by phase

| Time | Phase | What you actually do |
|------|-------|----------------------|
| **0–5 min** | Clarify | Ask about goal, users, scale, constraints, and *scope for today*. Recap assumptions. |
| **5–10 min** | Frame + metric | State the ML task (or a rule), and name business + ML + offline + online metrics + a guardrail. |
| **10–25 min** | Data, features, model | The core. Data sources, labels, features (avoid leakage/skew), baseline → complex model. |
| **25–38 min** | Serving, scale, monitoring | Batch vs online, funnel, latency budget, QPS sizing, drift + retraining + failure path. |
| **38–45 min** | Trade-offs + wrap | Own the trade-offs, answer follow-ups, say "what I'd do next". |

### How to actually stay on time

- **Announce the plan in the first 30 seconds.** "I'll clarify, frame, define
  metrics, then design data → model → serving → monitoring, and leave time for
  trade-offs." This *is* time management made visible.
- **Narrate transitions.** "That's the model; I've got about 15 minutes left, so
  I'll move to serving unless you want more depth here." You just showed a grader
  you are pacing yourself.
- **Protect the last 5 minutes.** Trade-offs and "what breaks at 100×" are where
  the staff signal lives — never let the clock eat them.

> **The single most common failure:** spending 40 minutes on the model and
> skipping serving + monitoring. Budgeting time out loud is the fix, and it costs
> you nothing but a sentence.

---

## 20.3 Company-Specific Styles (Tune the Same Answer)

### Motivation

The 7-step core never changes — but *where you spend your emphasis* should shift
with the company in the room. The same "design recommendations" answer should
sound a little different at Amazon (customer + Leadership Principles) than at
NVIDIA (throughput + GPUs). Knowing the house style lets you land your strongest
points on the axes that company rewards.

![Four coloured header boxes — Google/Meta, Amazon, OpenAI/Anthropic, NVIDIA — each over a description: Google/Meta value depth, scale, and trade-offs; Amazon values Leadership Principles and customer focus; OpenAI/Anthropic value LLM, RAG, evals, and safety; NVIDIA values infra, GPUs, and throughput; with notes that Netflix rewards metrics plus A/B, Apple rewards privacy plus on-device, and Uber/Airbnb/Stripe reward real-time, fraud, ETA, and cost, all over the same 7-step core.](images/m20_03_company_styles.png)

### The comparison table

| Company | What they reward most | Tune your answer by… | Favourite prompts |
|---------|----------------------|----------------------|-------------------|
| **Google / Meta** | Depth, scale, clean trade-offs | Going deep on the funnel, latency budget per stage, feedback loops | Search ranking, feed, YouTube reco, ads CTR |
| **Amazon** | Customer Obsession + Leadership Principles | Starting from the customer/business impact; use LP language ("dive deep", "bias for action"); quantify cost of errors | Product search, "customers also bought", forecasting |
| **Netflix** | Metrics discipline + A/B rigour | Being crisp on business vs ML metrics, guardrails, and experiment design | Reco, thumbnail selection, watch-time ranking |
| **Apple** | Privacy + on-device | Proposing on-device/edge inference, federated learning, no raw data leaving the phone | Keyboard, photos, face unlock, on-device ranking |
| **OpenAI / Anthropic** | LLM/RAG depth, evals, safety | Retrieval + grounding, faithfulness/eval sets, guardrails, when NOT to fine-tune | RAG assistants, LLM agents, eval design, safety |
| **NVIDIA / infra teams** | Throughput, GPUs, latency, cost | Batching, quantization/distillation, kernel/hardware utilisation, cost per query | "Serve this at 1M QPS", cut latency/cost, inference infra |
| **Uber / Airbnb / Stripe** | Real-time, cost of errors | Streaming features, quantile/asymmetric loss, fraud fail-open/closed, per-segment bias | ETA, dispatch, fraud, marketplace search |

### First-principles: it's still one answer

Do **not** memorise eight different scripts. Run the *same* 7 steps every time;
just **spend a little longer on the step that company cares about** and use its
vocabulary. Amazon still wants your metrics and serving — they just want you to
open from the customer. NVIDIA still wants the ML framing — they just want you to
go deep on serving. Same core, shifted emphasis.

> **Senior signal:** at Amazon, tie a design decision to a Leadership Principle
> explicitly ("declining a good customer violates Customer Obsession, so I'll
> optimise recall at a fixed low false-positive rate"). At OpenAI/Anthropic,
> raise safety/faithfulness *before* being asked.

---

## 20.4 Anatomy of a Mock Answer (Plus Worked Walkthroughs)

### The structure of every strong mock run

![A left-to-right flow of four boxes — problem statement, clarifying questions, full 7-step design, follow-ups (deep dive) — with a red arrow dropping from follow-ups to a highlighted box reading "what a Staff answer adds: trade-offs, cost, failure modes", and a caption that a junior stops at the design while staff layers trade-offs and what breaks at 100x.](images/m20_04_mock_flow.png)

Every good answer has the same four beats, then a Staff layer:

1. **Problem statement** — the prompt, restated in one line so both of you agree.
2. **Clarifying questions** — 5 minutes pinning goal, scale, constraints, scope.
3. **Full 7-step design** — Clarify → Frame → Metrics → Data → Model → Serve →
   Monitor, driven and narrated.
4. **Follow-ups (deep dive)** — the interviewer pushes on one step; you go deep.
5. **What a Staff answer adds** — trade-offs, cost, and failure modes, offered
   *without being asked*.

Below are **four fully worked mocks**. For the complete architectures, we point
to Module 17; here the focus is on *how the conversation runs*.

---

### Mock 1 — "Design the TikTok For-You feed" (Recsys pattern → M12, M17.2)

**Restate:** "So: a personalised, infinitely-scrolling video feed that maximises
long-term engagement, at very large scale."

**Clarifying questions (say these out loud):**
- What's the business goal — watch time, retention, or something else? *(Assume
  long-term retention, proxied by watch time; clickbait hurts it.)*
- Scale? *(Assume ~1B users, billions of videos, hundreds of thousands of QPS.)*
- Latency budget for a feed load? *(A few hundred ms.)*
- Cold start for new users and brand-new videos? *(Yes, both matter.)*
- Scope for today — the ranking pipeline, not the video-upload path? *(Confirm.)*

**7-step design (one or two lines each):**
1. **Clarify** — above; recap: "personalised feed, optimise retention via
   watch-time, ~500k QPS, few-hundred-ms budget, handle cold start."
2. **Frame** — two-stage **retrieval → ranking**; ranking target is
   **multi-objective** (watch time *and* positive engagement, minus "not
   interested"), because pure watch time breeds doomscroll bait.
3. **Metrics** — business: retention, session length (A/B). ML offline:
   NDCG, watch-time regression error, retrieval recall@k. Guardrails:
   **diversity**, freshness, "not interested" rate.
4. **Data & features** — implicit feedback (watch %, likes, skips, shares).
   User/video/context features. Beware **feedback loops** and **position bias**
   — log position, add exploration. No post-impression leakage.
5. **Model** — baseline: popularity + followed accounts. Retrieval: **two-tower**
   + ANN (video embeddings precomputed, user embedding fresh). Ranking: deep
   multi-head network.
6. **Serve** — hybrid batch+online funnel: batch-refresh embeddings/candidate
   pools, online retrieval (~10–20 ms) + ranking (~30–50 ms). Cache per-user for
   a short TTL. Thousands of replicas, accelerators for ranking.
7. **Monitor** — watch retention + guardrails live; drift in feature/video mix;
   retrain daily; refresh embeddings continuously (item cold start). Fallback:
   popularity if the ranker is down; canary new models.

**Likely follow-ups:** "How do you handle a brand-new video with no history?"
(content embeddings + exploration slots). "How do you stop the feed collapsing
to a few viral videos?" (diversity guardrail + exploration + debias position).

**What a Staff answer adds:** names the feedback-loop/filter-bubble risk
unprompted, proposes an **explore/exploit** budget with a diversity guardrail,
estimates the retrieval index size and the cost of daily retraining, and states
the failure path explicitly. Ties it together: *"cheap two-tower retrieval
(ML) + ANN over a sharded index (systems) serves fresh personalised feeds at
500k QPS (business) — and I'd guardrail diversity so we don't trade long-term
retention for short-term watch time."*

---

### Mock 2 — "Design fraud detection for a payments company" (Fraud pattern → M10, M17.5)

**Restate:** "Real-time scoring of card transactions to block fraud without
wrongly declining good customers."

**Clarifying questions:**
- Cost of a false negative vs a false positive? *(A missed fraud costs the
  chargeback; a false decline costs a lost sale + churn — both painful,
  business decides the ratio.)*
- Latency? *(Inline with the transaction — tens of ms.)*
- Scale? *(~tens of thousands of transactions/sec.)*
- Do we have clean labels? *(Chargeback labels arrive weeks late — delayed &
  partial.)*
- Scope — the real-time scorer + decision layer? *(Confirm.)*

**7-step design:**
1. **Clarify** — recap the asymmetric cost, tens-of-ms budget, delayed labels.
2. **Frame** — **binary classification with extreme imbalance** (<0.1% fraud),
   feeding a **decision policy** (approve / decline / step-up / human review),
   not a raw label. Combine supervised model + anomaly signals + hard rules.
3. **Metrics** — **never accuracy.** Recall at a fixed low false-positive rate,
   PR-AUC (offline); fraud loss $, false-decline rate (online). Guardrail:
   customer-friction rate.
4. **Data & features** — transaction stream; **streaming velocity aggregates**
   (# tx from card/device/IP in last 1m/1h/24h), amount vs user norm, geo/device
   mismatch, merchant risk. Labels are delayed — recent data is only partly
   labelled. Watch post-transaction leakage.
5. **Model** — baseline: **rules** (block if amount > X and new device) — real
   and always deployed alongside ML. Then **gradient-boosted trees** (tabular
   default), optionally ensembled with an anomaly detector for novel attacks.
   Handle imbalance with class weights / thresholding.
6. **Serve** — **online + streaming**: Kafka/Flink maintains velocity features;
   model scores inline in tens of ms; decision engine routes. The feature
   store's freshness is the bottleneck, not the model.
7. **Monitor** — the adversary makes drift fast and deliberate. Watch score
   distributions and precision/recall on the trickle of confirmed labels;
   fast path to add rules for new attacks. **Fail closed** for high-risk,
   **fail open** for low-risk.

**Likely follow-ups:** "Labels come weeks late — how do you train and evaluate?"
(delayed-feedback modelling, short retrain windows, careful temporal splits).
"An attacker changes tactics overnight — what happens?" (anomaly path + rules +
frequent retrain; monitor challenge/decline rates).

**What a Staff answer adds:** names **imbalance + delayed labels + adversarial
drift** as the three defining hardships in one breath; reasons about the
*business* cost ratio to set the operating threshold rather than picking an
arbitrary one; and designs the fail-open/fail-closed policy per risk tier so a
model outage doesn't block every customer or wave through every fraudster.

---

### Mock 3 — "Design an enterprise RAG assistant over internal docs" (LLM/RAG pattern → M16, M17.8)

**Restate:** "Employees ask questions in natural language and get accurate,
grounded, cited answers from our wikis/tickets/PDFs — never seeing docs they
lack permission for."

**Clarifying questions:**
- Hard constraints? *(Permissions must be respected, answers must be grounded and
  cited, docs change so freshness matters.)*
- Scale? *(Thousands–millions of docs, moderate QPS.)*
- Latency + cost tolerance? *(A few seconds is OK; LLM cost is the real budget.)*
- Scope — the RAG pipeline, not training a base model? *(Confirm.)*

**7-step design:**
1. **Clarify** — recap: grounded, cited, permission-safe QA over internal docs.
2. **Frame** — **retrieval + generation**, not one model. Retrieval = a search
   problem (find the few relevant, *permitted* chunks); generation = an LLM
   grounded on those chunks, told to answer only from context, cite, and say
   "I don't know" when context is insufficient.
3. **Metrics** — retrieval recall@k / precision@k (offline); **faithfulness /
   groundedness**, citation accuracy, answer correctness via **LLM-as-judge** +
   a human eval set. Guardrails: hallucination rate and permission leaks ≈ zero.
4. **Data & features** — corpus chunked (with overlap) and embedded; each chunk
   carries **access-control metadata**, source, timestamp. Re-embed changed docs.
   Chunk size matters (too big dilutes, too small loses context).
5. **Model** — retrieval: **hybrid** dense (ANN over a vector DB) + keyword,
   permission-filtered, then a cross-encoder re-ranker. Generation: a strong
   instruction-following LLM with a grounding prompt. Baseline: hosted model +
   good prompting *before* any fine-tuning.
6. **Serve** — offline: ingest → chunk → embed → upsert. Online: embed query →
   permission-filtered hybrid retrieval (~tens of ms) → re-rank → assemble prompt
   → LLM generate (1–5 s, dominant cost). Retrieve *tightly* to keep prompts
   short and cheap.
7. **Monitor** — thumbs up/down, groundedness, citation clicks, and — critically
   — **permission-leak incidents** and hallucination rate. Regression eval set on
   every prompt/model change (prompts are code — version them). Fallback: "I
   couldn't find this" rather than inventing an answer.

**Likely follow-ups:** "Where exactly do you enforce permissions?" (filter at
retrieval time on chunk ACL metadata, *before* anything reaches the LLM — never
rely on the LLM to withhold). "How do you know it's not hallucinating?"
(faithfulness eval set + LLM-judge + human spot checks; guardrail model on
output).

**What a Staff answer adds:** treats RAG as *"search + a grounded generation
head with strict access control"*, evaluates **faithfulness not fluency**, is
explicit that permissions are enforced at retrieval (defence in depth), and
reasons about cost being LLM-bound so the whole design pushes toward tight,
high-quality retrieval and short prompts.

---

### Mock 4 — "Design ETA prediction for food delivery" (Regression pattern → M6/M7, M17.6)

**Restate:** "Predict, and show the user, an accurate delivery time that dispatch
can also plan on."

**Clarifying questions:**
- Cost of error — is late worse than early? *(Yes — a broken promise; loss should
  be asymmetric.)*
- One number or a range? *(A trustworthy p50/p90 range is better than a point.)*
- Latency + scale? *(Tens of ms, high QPS, per-city patterns.)*
- Scope — the point/quantile ETA model, not full dispatch optimisation? *(Confirm.)*

**7-step design:**
1. **Clarify** — recap asymmetric cost, need for a reliable range, per-city.
2. **Frame** — **regression**; predict total minutes, optionally decomposed
   (to-restaurant + prep + to-customer). Prefer **quantile regression** (p50,
   p90) so the app shows a range and dispatch plans for the tail.
3. **Metrics** — MAE/RMSE, **quantile loss / calibration**, and the **late-error
   rate** (offline); on-time rate, cancellations (online). Guardrail: systematic
   bias per city/time.
4. **Data & features** — historical trips with actual durations (clean, abundant
   labels). Routing-engine base time, real-time traffic, weather, driver
   supply/demand, restaurant prep time/load, historical segment speeds. Traffic
   and supply are streaming. No post-completion leakage.
5. **Model** — baseline: the **routing engine's physics estimate** (always
   available); ML *corrects* it. Then GBDTs (great for tabular spatio-temporal)
   or a neural model with **asymmetric/quantile loss**.
6. **Serve** — online, low latency, real-time feature store for traffic/supply;
   precompute slow features (segment speeds) in batch; cache ETAs for near-identical
   routes for a short TTL.
7. **Monitor** — MAE, late-rate, and bias **per city/segment/time** (great
   globally, terrible at airport-at-5pm). Drift from road changes and demand
   shocks; retrain per-region. Fallback: routing-engine estimate.

**Likely follow-ups:** "Your MAE looks fine but users complain — why?" (average
error hides the painful tail; monitor late-rate and per-segment bias). "New city
launch, no data?" (start from the routing baseline + transfer/global features).

**What a Staff answer adds:** raises **asymmetric error and the tail** unprompted,
chooses quantile/asymmetric loss with a business reason, and monitors
per-segment bias rather than a single global MAE — because a chronically
optimistic ETA erodes trust even when the average looks great.

---

## 20.5 When You Get Stuck (Recover, Don't Freeze)

### Motivation

Every hard interview has a moment where you don't know something, the interviewer
throws a twist, or the problem balloons. **How you recover is graded more than
whether you hit the snag.** Silence and bluffing both fail; narrated reasoning
wins.

![Two orange trigger boxes — "I don't know" and "Scope creep" — each with a green arrow to a response box ("reason out loud from first principles"; "state assumptions, cut scope explicitly"), both feeding a blue box "curveball: restate it, link to a pattern you know", under a caption that silence and guessing both fail so narrate your thinking and steer back to solid ground.](images/m20_05_curveballs.png)

### The three recovery moves

**1. "I don't know" → reason out loud from first principles.** Never freeze or
bluff. Say what you *do* know and derive the rest: *"I haven't used that exact
index, but the requirement is fast nearest-neighbour search over millions of
vectors, so I'd reach for an ANN structure like HNSW and benchmark recall vs
latency."* You just turned a gap into a display of reasoning — which is what is
actually being scored.

**2. Scope creep → state assumptions and cut scope explicitly.** Interviews
sprawl; you can end up designing five subsystems at once. The senior move:
*"There are several directions here; the highest-impact one for our metric is X,
so I'll focus there and mention the others briefly."* Explicitly choosing scope is
a seniority signal; trying to do everything shallowly is not.

**3. Curveball → restate it, then link it to a pattern you know.** When the
interviewer changes the problem ("now it must run on-device", "now the labels are
adversarial"), don't panic. Restate the new constraint in your own words, then
map it to a known pattern or module: *"On-device changes serving, not framing —
that's a model-compression + edge problem (M8): quantize/distill, ship a small
model, update over the air."*

### First-principles: why narration beats silence

The interviewer cannot grade thoughts you don't say. A wrong idea *reasoned aloud*
gives them something to correct and shows how you think; silence gives them
nothing and reads as "stuck". **Always keep talking your reasoning** — even "let
me think about the trade-off here for a second" is better than a dead pause.

> **Reframe interruptions as hints.** When an interviewer pushes on a step,
> they are usually telling you where they want depth. Follow the pull; don't
> defend your original plan.

---

## 20.6 Red Flags That Fail Candidates

### Motivation

Interviewers keep a mental checklist of *disqualifiers*. You can know a lot and
still fail by tripping two or three of these. Knowing the list lets you **audit
yourself in real time** and catch the mistake before it costs you the loop.

![Six red-X checklist items in two columns: jumps to model and skips the metric; no clarifying questions; forgets serving and monitoring; ignores scale and cost; silent when stuck; never mentions trade-offs — with a caption that any two of these on a loop usually means a no-hire, so audit yourself against the list.](images/m20_06_red_flags.png)

### The checklist (say "not me" to each)

| Red flag | Why it fails you | The fix |
|----------|------------------|---------|
| **Jumps to a model, skips the metric** | You're optimising nothing you can measure | Define business + ML + offline + online metrics before modelling |
| **No clarifying questions** | You'll design the wrong thing | Spend the first 5 minutes clarifying and recap assumptions |
| **Forgets serving & monitoring** | Half the system is missing; models decay | Always reach steps 6–7; budget time for them |
| **Ignores scale & cost** | The design won't survive production | Put numbers on QPS, latency, and cost; size the system |
| **Silent when stuck** | Grader sees "can't cope", not "thinking" | Narrate reasoning from first principles |
| **Never mentions trade-offs** | Reads as junior; no ownership | Say "the trade-off is X, and here's my call, because…" |

### First-principles: what these have in common

Every red flag is a form of **not connecting the dots** — model without metric,
design without scale, choice without trade-off, or thinking without speaking. The
antidote is the same everywhere: *make the connection explicit and out loud.*

> **Self-audit:** any **two** of these on a single loop usually reads as a
> no-hire. After each practice mock, tick this list honestly. Fixing red flags is
> faster than learning new content and moves your score more.

---

## 20.7 What Earns the Staff Bar

### Motivation

The *same* question is asked of a new grad and a staff engineer. The difference is
entirely in *how* they answer. Knowing the target behaviour lets you deliberately
aim one level up.

![A three-step rising staircase: JUNIOR builds the happy path, then SENIOR handles scale and failure modes, then STAFF drives ambiguity and owns trade-offs, with a caption that staff answers connect ML choice to systems choice to business impact without being prompted.](images/m20_07_staff_bar.png)

### The ladder in words

| Level | What they deliver | What's missing |
|-------|-------------------|----------------|
| **Junior** | Builds the "happy path" — a reasonable design that works when nothing goes wrong | Scale, failure modes, trade-offs, business tie-in |
| **Senior** | Handles scale and failure modes; follows the framework; weighs the obvious trade-offs | Proactive ambiguity resolution; owning the *call* |
| **Staff** | Drives ambiguity, owns trade-offs, connects ML ↔ systems ↔ business *without being asked* | — (this is the bar) |

### What "staff" actually is (it's not more math)

Seniority in this interview is **breadth plus ownership**, not deeper equations.
The staff behaviours you can *practise*:

- **Drive the ambiguity.** Don't wait to be told the scope — propose it: "I'll
  assume X and Y; stop me if that's wrong."
- **Own the trade-off and decide.** A junior lists options ("we could use A or
  B"); a staff engineer *decides* ("I'd use A because latency dominates here, and
  accept the small accuracy loss").
- **Connect three layers unprompted.** Every big choice ties the **business goal
  ↔ the ML choice ↔ the systems constraint** in one sentence.
- **Design for failure and the future.** Shadow, canary, kill switch, fallback;
  and "what breaks at 100× and what I'd do next".

> **Aim one level up.** If you're targeting senior, don't just follow the
> framework — start weighing trade-offs aloud. If you're targeting staff, resolve
> ambiguity and make decisions before you're asked. The staff answer *connects ML
> choice ↔ systems choice ↔ business impact without prompting.*

---

## 20.8 Whiteboarding & Communication

### Motivation

Two candidates with the *same* design can score very differently based purely on
**how they present it**. A clear, narrated whiteboard is genuinely half the
score; a brilliant idea drawn as an unreadable tangle is a weak answer.

![Three top boxes describing a whiteboard layout — left: goal, metric, constraints; center: the data → model → serve flow; right: open questions and follow-ups — with an arrow from the center box to a wide box reading "talk while you draw: state each choice AND why", a signpost line "First I'll clarify, then design, then trade-offs", and a caption that a clear narrated whiteboard is half the score and structure beats a messy genius sketch.](images/m20_08_whiteboard.png)

### A whiteboard layout that always works

Divide the board into three zones up front:

- **Left — the frame:** goal, business + ML metric, constraints (latency, QPS,
  cost). This anchors every later decision.
- **Center — the flow:** the **data → model → serve** pipeline (or the
  retrieval → ranking funnel). This is the heart; keep it a clean left-to-right
  flow with labelled boxes and arrows.
- **Right — open questions & follow-ups:** park tangents and "things I'd revisit"
  here so you don't lose them or get derailed.

### Communication rules that raise your score

- **Signpost first:** *"First I'll clarify, then design, then trade-offs."* The
  interviewer now knows the shape of the next 40 minutes.
- **Talk while you draw** — state each choice **and the why**: "I'll put an ANN
  index here *because* brute-force search over millions of items blows the latency
  budget." The *why* is the seniority signal.
- **Keep boxes labelled and arrows directional.** A grader should understand your
  system from the board alone.
- **Check in at transitions:** "That's the serving path — deeper here, or on to
  monitoring?"

### First-principles: structure beats brilliance

The grader is reconstructing your *thinking* from what they see and hear. A tidy,
narrated, averagely-clever design is easy to follow and scores well; a genius
insight buried in a messy sketch with no narration is hard to credit. **Optimise
for legibility and narration, not artistry.**

> **Remote-interview note:** on a shared doc or virtual whiteboard the same rules
> hold — use headings for the three zones, keep the flow linear, and narrate
> even more, since the interviewer has fewer cues.

---

## Module 20 — Interview Mapping (what companies probe)

| Company | How Module 20 shows up | Junior answer | Staff answer |
|---------|------------------------|---------------|--------------|
| **Google / Meta** | Grades structure + depth on a pattern | Wanders, model-first | Names the pattern, drives the timeline, deep on the funnel with a latency budget |
| **Amazon** | Ties to Leadership Principles; "dive deep" | Tech-only, shallow | Opens from the customer, uses LP language, quantifies cost of errors |
| **OpenAI / Anthropic** | RAG/LLM depth + safety + evals | "just prompt an LLM" | Retrieval + grounding + faithfulness eval + permissions, raises safety unprompted |
| **NVIDIA / infra** | Serving throughput, GPU/cost | Ignores latency/QPS | Batching, quantization/distillation, cost per query, sizes the fleet |
| **Uber / Airbnb / Stripe** | Real-time, cost of errors | One metric, one mode | Streaming features, asymmetric/quantile loss, fail-open/closed, per-segment bias |

**The single most common opening:** *"Design an ML system for X."* Map X to a
pattern (20.1), announce the timeline (20.2), tune the emphasis to the company
(20.3), and drive the mock (20.4). Structure plus one named gotcha is most of the
score.

---

## Module 20 — Exam Mapping (interview-only)

- **This is an interview-only module.** Written exams (SEBI IT / RBI IT / GATE
  CS-DA / ISRO) do **not** test how you run a mock, budget 45 minutes, tune to a
  company, or recover from a curveball. There is essentially **zero** written-exam
  content here.
- If you are preparing solely for a written paper, skip to the exam-heavy modules
  (foundations, data, features, evaluation metrics, systems foundations).
- If you are preparing for **FAANG / AI-engineer / staff interviews**, this
  module is where knowledge becomes an offer — treat it as the most practical
  chapter in the course and *rehearse it out loud*.

> **Bottom line:** exam value ≈ none; interview and on-the-job value ≈ maximum.

---

## Module 20 — Common Mistakes & Misconceptions

1. **Treating each prompt as brand-new.** Almost every question is one of eight
   patterns — map it first. (20.1)
2. **No time budget.** Spending 40 minutes on the model and skipping serving +
   monitoring. Announce and manage the clock out loud. (20.2)
3. **One-size-fits-all delivery.** Not tuning emphasis to Amazon (customer/LP),
   NVIDIA (infra), or OpenAI (safety/evals). Same core, shifted emphasis. (20.3)
4. **Skipping clarifying questions.** Designing the wrong thing because you
   assumed the goal, scale, or scope. (20.4)
5. **Freezing or bluffing when stuck.** Narrate first-principles reasoning and
   say how you'd find out. (20.5)
6. **Never naming trade-offs or failure modes.** The clearest junior tell; owning
   trade-offs is the staff bar. (20.6, 20.7)
7. **A messy, silent whiteboard.** Structure and narration are half the score;
   don't bury a good design in an unreadable sketch. (20.8)
8. **Listing options instead of deciding.** A staff engineer makes the call and
   justifies it; a junior enumerates. (20.7)

---

## Module 20 — MCQs (with answers & explanations)

**Q1.** You are given an unfamiliar prompt: "design a system to recommend which
push notification to send each user." The best *first* move is to:
a) Start designing a neural network
b) Map it to a known pattern (recsys/ranking) and announce the 7 steps
c) Ask about the programming language
d) Estimate GPU cost immediately

<details><summary>Answer</summary>**b.** Nearly every prompt is one of ~8
patterns. Recognising this is a recsys/ranking problem lets you reuse the funnel
blueprint (20.1) instead of improvising.</details>

**Q2.** Halfway through a 45-minute interview you have only covered clarify,
frame, and the model. The best move is to:
a) Keep polishing the model — depth matters most
b) Explicitly re-budget the remaining time and move to serving + monitoring
c) Stay silent and think
d) Skip straight to trade-offs

<details><summary>Answer</summary>**b.** Forgetting serving and monitoring is a
top red flag. Announce the re-budget out loud and cover the rest of the pipeline;
completeness beats over-polishing one step. (20.2, 20.6)</details>

**Q3.** At **Amazon**, the strongest way to frame a fraud design decision is to:
a) Talk only about model architecture
b) Tie it to a Leadership Principle and the customer (e.g. false declines violate
   Customer Obsession)
c) Focus on GPU throughput
d) Avoid mentioning cost

<details><summary>Answer</summary>**b.** Amazon rewards Customer Obsession and LP
language. Framing the false-decline cost as a customer issue lands on the axis
they grade. (20.3)</details>

**Q4.** The interviewer asks about an index you have never used. The best
response is to:
a) Pretend you know it in detail
b) Say "no idea" and stop
c) State the requirement, reason from first principles, name a plausible approach,
   and say how you'd validate it
d) Change the subject

<details><summary>Answer</summary>**c.** Turning a gap into visible first-principles
reasoning ("fast NN search over millions of vectors → ANN like HNSW → benchmark
recall vs latency") scores well; freezing and bluffing both fail. (20.5)</details>

**Q5.** Which set of behaviours is most likely a **no-hire** on a single loop?
a) Names the metric, sizes the system, discusses trade-offs
b) Jumps to a model, asks no clarifying questions, and never mentions serving
c) Proposes a baseline, then a complex model
d) Announces a plan and manages time

<details><summary>Answer</summary>**b.** Those are three red flags at once — no
metric, no clarification, no serving. Any two on a loop usually reads as a
no-hire. (20.6)</details>

**Q6.** What most distinguishes a **staff** answer from a senior one?
a) Knowing more math
b) Using a bigger model
c) Proactively resolving ambiguity, owning trade-offs, and connecting ML ↔
   systems ↔ business without being asked
d) Talking faster

<details><summary>Answer</summary>**c.** Staff is breadth plus ownership: drive
ambiguity, make the call, and tie the three layers together unprompted — not
deeper equations. (20.7)</details>

**Q7.** In an **enterprise RAG** design, where should document permissions be
enforced?
a) Inside the LLM prompt, trusting the model to withhold
b) At retrieval time, filtering on chunk access-control metadata before anything
   reaches the LLM
c) Not needed
d) Only in the UI

<details><summary>Answer</summary>**b.** Never rely on the LLM to keep secrets;
filter permitted chunks at retrieval so forbidden content never enters the prompt
(defence in depth). (20.4, M17.8)</details>

**Q8.** Why is a clear, narrated whiteboard "half the score"?
a) Interviewers grade artistry
b) The grader reconstructs your *thinking* from what they see and hear, so
   legibility + the "why" behind each choice drive the score
c) It saves time
d) It replaces the need for metrics

<details><summary>Answer</summary>**b.** A tidy, narrated, averagely-clever design
is easy to credit; a genius idea in a messy silent sketch is not. Optimise for
legibility and narration. (20.8)</details>

---

## Module 20 — Design Exercises (easy → hard)

- **Easy.** For each prompt, name the pattern (20.1) and the module to borrow the
  blueprint from: (1) "rank the LinkedIn feed"; (2) "predict surge pricing";
  (3) "answer questions from our legal docs"; (4) "serve a ranking model at 1M
  QPS"; (5) "detect payment fraud".
- **Easy.** Write your 30-second opening "plan announcement" for any design
  prompt, from memory.
- **Medium.** Take "design YouTube reco" and write the *same* answer twice —
  once tuned for **Google** (depth, funnel, latency budget) and once for
  **Amazon** (customer, LP, cost of errors). What actually changes?
- **Medium.** You're at 30/45 minutes and have only done clarify + frame + model.
  Write out loud how you'd re-budget the last 15 minutes and what you'd
  deliberately cut.
- **Medium.** Run a full mock for "design Spotify Discover Weekly": restate →
  5 clarifying questions → 7-step design → 2 likely follow-ups → what a staff
  answer adds. (Hint: it's a recsys pattern with a weekly-batch twist.)
- **Hard.** Take a curveball: you designed an online fraud scorer, and the
  interviewer says "now it must run fully on-device with no network". Restate the
  new constraint and adapt the design, naming what changes and what stays.
- **Hard.** Audit a recording (or a friend's mock) against the six red flags
  (20.6). For each flag tripped, write the exact sentence that would have fixed
  it.
- **Hard.** For "design an enterprise RAG assistant", write the three sentences
  that connect **business ↔ ML ↔ systems** and the one sentence that names the
  defining gotcha — i.e., the staff layer.

---

## Module 20 — Concept Review (one page)

- **Eight patterns** cover almost every prompt: recsys/feed, ranking/search,
  CTR/ads, fraud/anomaly, ETA/regression, LLM/RAG, serving/infra, graph/PYMK.
  Map the prompt to a pattern in the first minute and reuse the blueprint (module
  in 20.1).
- **The 45-minute timeline:** clarify (0–5) → frame + metric (5–10) → data /
  features / model (10–25, the bulk) → serving / scale / monitoring (25–38) →
  trade-offs + wrap (38–45). Budget it *out loud*; never starve serving +
  monitoring.
- **Company styles:** same 7-step core, shifted emphasis — Google/Meta (depth,
  scale), Amazon (customer + LP), Netflix (metrics + A/B), Apple (privacy +
  on-device), OpenAI/Anthropic (LLM/RAG + safety + evals), NVIDIA (infra + GPUs
  + cost), Uber/Airbnb/Stripe (real-time, fraud, ETA, cost).
- **Mock anatomy:** restate → clarify → full 7-step design → follow-ups → the
  staff layer (trade-offs, cost, failure modes). Practise the four worked mocks
  (reco, fraud, RAG, ETA) until the shape is automatic.
- **Recover, don't freeze:** "I don't know" → reason from first principles;
  scope creep → cut scope explicitly; curveball → restate + link to a known
  pattern. Narrate always.
- **Red flags** (any two ≈ no-hire): jumps to model / no clarification / forgets
  serving + monitoring / ignores scale + cost / silent when stuck / no trade-offs.
- **Staff bar** = breadth + ownership: drive ambiguity, decide (don't list),
  connect ML ↔ systems ↔ business unprompted, design for failure and the future.
- **Whiteboard:** three zones (frame / flow / open questions); signpost; talk
  while you draw and always say the *why*. Structure beats a messy genius sketch.

---

## Module 20 — Flash Cards (Q → A)

1. First move on any prompt? → *Map it to one of the eight patterns and announce
   the plan.*
2. The 45-min bulk goes where? → *Data, features, and model (10–25 min).*
3. Most common time failure? → *40 min on the model, skipping serving +
   monitoring.*
4. One answer or eight scripts? → *One 7-step core; shift emphasis per company.*
5. Amazon's tuning knob? → *Customer Obsession + Leadership-Principle language.*
6. OpenAI/Anthropic tuning knob? → *LLM/RAG depth, faithfulness evals, safety.*
7. NVIDIA tuning knob? → *Throughput, GPUs, latency, cost per query.*
8. Handle "I don't know"? → *Reason from first principles; say how you'd find
   out.*
9. Handle scope creep? → *Pick the highest-impact scope explicitly; mention the
   rest briefly.*
10. Handle a curveball? → *Restate it, then link it to a pattern/module you
    know.*
11. Two red flags on a loop means? → *Usually a no-hire — audit yourself.*
12. Staff in one line? → *Breadth + ownership: drive ambiguity, decide, connect
    ML ↔ systems ↔ business.*
13. Why is the whiteboard half the score? → *The grader reconstructs your
    thinking; legibility + the "why" carry it.*
14. The four mock beats + staff layer? → *Restate → clarify → 7-step → follow-ups
    → trade-offs/cost/failure.*

---

## Module 20 — Pattern Recognition (how to spot it in an interview)

- Hear **"design a feed / recommendations / who to follow"** → recsys pattern;
  two-stage funnel (M12); say *feedback loops + multi-objective + diversity
  guardrail*.
- Hear **"rank search results / product search / similar items"** → ranking
  pattern (M13); *lexical + semantic retrieval, NDCG, debias clicks*.
- Hear **"predict clicks / serve ads"** → CTR pattern (M17.4); *calibration +
  delayed labels + auction*.
- Hear **"detect fraud / abuse / spam"** → fraud pattern (M17.5); *imbalance,
  adversary, recall@FPR, fail-open/closed*.
- Hear **"estimate time / price / demand"** → regression pattern (M17.6);
  *asymmetric/quantile loss, the tail, per-segment bias*.
- Hear **"answer from our documents / build an assistant"** → RAG pattern
  (M16/M17.8); *retrieval + grounding + faithfulness + permissions*.
- Hear **"serve at N QPS / cut latency or cost / on-device"** → serving pattern
  (M8/M11/M19); *batching, quantize/distill, cache, cost per query*.
- Hear **"almost out of time"** → protect the last 5 min for trade-offs + next
  steps.
- Feel yourself **freezing** → narrate first-principles reasoning out loud.
- Notice the **company** → shift emphasis (Amazon→customer/LP, NVIDIA→infra,
  OpenAI→safety/evals) over the same 7-step core.

---

## Module 20 — Revision Notes / Mini Cheat Sheet

```
8 PATTERNS (map the prompt in <60s):
  recsys/feed  ranking/search  CTR/ads  fraud/anomaly
  ETA/regress  LLM/RAG         serving/infra  graph/PYMK
  -> each has a known blueprint (M12/M13/M17/M16/M8-11-19)

45-MIN TIMELINE (announce it out loud):
  0-5  clarify goal/scope/constraints
  5-10 frame as ML + pick metric (biz+ML, offline+online, +guardrail)
  10-25 DATA + FEATURES + MODEL   <- spend MOST time here
  25-38 SERVING + SCALE + MONITORING   <- never skip these
  38-45 trade-offs, follow-ups, wrap

COMPANY STYLES (same core, shift emphasis):
  Google/Meta  depth, scale, funnel, latency budget
  Amazon       Customer Obsession + Leadership Principles
  Netflix      metrics + A/B rigor
  Apple        privacy + on-device / federated
  OpenAI/Anthro  LLM/RAG, faithfulness evals, safety
  NVIDIA       throughput, GPUs, cost per query
  Uber/Airbnb/Stripe  real-time, fraud, ETA, cost of errors

MOCK ANATOMY:  restate -> clarify -> 7-step design -> follow-ups
               -> STAFF layer = trade-offs + cost + failure modes

STUCK? (recover, never freeze)
  "I don't know" -> reason from first principles + how to find out
  scope creep    -> cut scope EXPLICITLY, highest-impact first
  curveball      -> restate it, link to a pattern you know
  NARRATE ALWAYS. silence and bluffing both fail.

RED FLAGS (any 2 on a loop ~ no-hire):
  jumps to model | no clarifying Qs | forgets serve+monitor
  ignores scale+cost | silent when stuck | no trade-offs

STAFF BAR = breadth + OWNERSHIP:
  drive ambiguity | DECIDE (don't list) | connect ML<->systems<->business
  design for failure + "what breaks at 100x"

WHITEBOARD:  3 zones (frame | flow | open Qs) | signpost first
  talk while you draw + always say WHY | structure > messy genius
```

---

> **Next module:** *Module 21 — Behavioural & Cross-Functional Signals.* The
> design whiteboard is only half of a staff interview. Module 21 covers the
> *other* half: telling crisp project stories (STAR), showing leadership and
> influence without authority, handling disagreement and ambiguity, and the
> cross-functional signals — working with product, data, and infra teams — that
> hiring committees weigh just as heavily as your architecture.
