---
title: "Module 18 — Responsible & Trustworthy AI"
subtitle: "ML System Design Mastery: FAANG / AI-Engineer / Staff-Level — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 18 — Responsible & Trustworthy AI

> **Why this module matters.**
> A model can be accurate and still be *wrong to ship*. It can quietly deny loans
> to one group, leak the private data it was trained on, be fooled by a sticker
> on a stop sign, or make a life-changing decision that no one — not even its
> builders — can explain. Responsible AI is the discipline of building systems
> that are **fair, private, explainable, secure, governed, and safe**. For a
> Staff-level engineer this is not optional garnish: in regulated domains
> (finance, hiring, healthcare) it is a *hard requirement* that decides whether
> the system is allowed to exist at all. And for the **SEBI / RBI IT** exams,
> the governance, privacy, and security ideas here carry **real, direct exam
> value** — flagged throughout. We build every idea from first principles, in
> plain English.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS/DA | Interview | AI/MLE role |
|----------------|:-------:|:------:|:----------:|:---------:|:-----------:|
| This module    | ★★★★    | ★★★★   | ★★         | ★★★★      | ★★★★★       |

**What you must be able to do after this module:**
name the three sources of bias and the three fairness metrics (with their
formulas) and say when each applies; place a mitigation as pre-, in-, or
post-processing; explain differential privacy as a *privacy budget* (epsilon)
and describe federated learning + secure aggregation; pick SHAP vs LIME vs
attention and distinguish global from local explanations; name the four main
ML attacks (poisoning, evasion, model stealing, membership inference) and one
defense each; describe governance artifacts (model cards, datasheets, audit
logs) and the **EU AI Act risk tiers** and **GDPR**; and sketch the safety
stack for an LLM (RLHF + guardrails).

> **How to read this module.** For every idea we go **problem → simplest
> attempt → why it breaks → the fix**, and we tie each concept to how it shows
> up in a real interview *and* on the SEBI/RBI syllabus.

---

## 18.1 Fairness & Bias — where unfairness comes from

### Motivation (the problem that existed)

Suppose you train a hiring model on ten years of a company's past hires. The
model learns to predict "would we hire this person?" and it is 90% accurate on
held-out data. You ship it. Six months later a journalist shows that the model
rejects almost every woman who applies for engineering roles. Nothing in your
code says "reject women" — so how did this happen?

The answer: **the model faithfully learned the patterns in the data, and the
data was unfair.** The company historically hired mostly men, so "looks like a
past hire" quietly became "looks like a man". The model did exactly what it was
told; the *training signal* was poisoned by history. This is the core lesson of
fairness: **a model is a mirror of its data, and if the data encodes past
injustice, the model will scale it up.**

### Three sources of bias

Bias does not come from one place. There are three main entry points, and a
good design blocks all three.

![Three sources of bias — data bias, label bias, and feedback loops — all flow into a biased model, and the feedback loop re-injects the bias over time.](images/m18_01_bias_sources.png)

As the diagram shows:

1. **Data bias (sampling bias).** The training data does not represent the real
   population. A face model trained mostly on light-skinned faces performs worse
   on dark-skinned faces. The *who is in the sample* question.
2. **Label bias.** The labels themselves carry human prejudice. If past loan
   officers rejected certain groups unfairly, "approved / rejected" labels
   encode that prejudice, and the model copies it.
3. **Feedback loops.** The model's own outputs shape the next batch of training
   data (recall Module 1). A model that under-serves a group collects less good
   data about that group, gets even worse for them, and the loop tightens. The
   dashed red arrow in the diagram is this amplification.

> **First-principles takeaway:** you cannot fix bias only at the model. If the
> data and labels are biased, "fixing the model" just re-launders the same
> unfairness. Fix it at the *source* where you can, and break the feedback loop.

### Protected attributes

A **protected attribute** is a feature the law (or ethics) says you must not
discriminate on: race, sex, age, religion, disability, etc. A common rookie
mistake is "just delete the protected column and we're fair". This fails,
because other features are **proxies**: postal code proxies for race, first name
proxies for gender. The model reconstructs the protected attribute from proxies.
Fairness must be *measured*, not assumed away.

---

## 18.2 Fairness Metrics — what exactly must be equal?

### Motivation

"Be fair" is a slogan, not a spec. To *test* fairness you need a number. But
here is the subtle part that separates senior candidates: **there are several
definitions of fairness, they are not the same, and you usually cannot satisfy
them all at once.** You must choose the one that matches the harm you care
about.

Let the model output be $\hat{Y}\in\{0,1\}$ (e.g. approve = 1), the true label
be $Y$, and $A$ be the protected group ($a$ vs $b$).

![Three fairness metrics: demographic parity (equal positive rate), equal opportunity (equal true-positive rate), and equalized odds (equal TPR and FPR). You usually cannot satisfy all at once.](images/m18_02_fairness_metrics.png)

### The three main metrics (with formulas)

**1. Demographic (statistical) parity.** The positive rate is equal across
groups, regardless of the truth:
$$P(\hat{Y}=1 \mid A=a) = P(\hat{Y}=1 \mid A=b)$$
*"Each group gets approved at the same rate."* Good when you want equal access
(e.g. equal share of ads shown). Weakness: it ignores whether people actually
qualify, so it can force accepting unqualified applicants from one group.

**2. Equal opportunity.** The true-positive rate (recall) is equal across
groups:
$$P(\hat{Y}=1 \mid Y=1, A=a) = P(\hat{Y}=1 \mid Y=1, A=b)$$
*"Among people who truly qualify, each group is caught at the same rate."*
Good for opportunities (loans, jobs) where missing a qualified person is the
harm.

**3. Equalized odds.** *Both* the true-positive rate **and** the false-positive
rate are equal across groups:
$$P(\hat{Y}=1 \mid Y=y, A=a) = P(\hat{Y}=1 \mid Y=y, A=b)\quad\text{for } y\in\{0,1\}$$
The strongest of the three: it balances both kinds of error. Hardest to
achieve.

### The impossibility result (a senior signal)

There is a proven **impossibility**: except in trivial cases you cannot have
demographic parity *and* equalized odds *and* calibrated scores all at once. So
fairness is a **choice**, not a checkbox. In an interview, saying *"which
fairness definition do we optimise, given the harm, and what do we trade away?"*
is a strong signal. A related legal rule of thumb is the **80% (four-fifths)
rule**: if one group's selection rate is below 80% of the top group's, that is
evidence of adverse impact.

---

## 18.3 Bias Mitigation — pre-, in-, and post-processing

### Motivation

Once you can *measure* unfairness, you must *reduce* it. There are exactly three
places you can intervene, matching the pipeline stages: before training, during
training, and after training.

![Bias mitigation at three points: pre-processing (re-sample or re-weight the data), in-processing (add a fairness term to the loss), and post-processing (adjust thresholds per group).](images/m18_03_mitigations.png)

### The three families

- **Pre-processing (fix the data).** Re-sample or re-weight so under-represented
  groups are properly present; remove biased labels; learn representations that
  drop protected information. *Most effective* because it attacks the root, but
  needs access and rights to modify the training data.
- **In-processing (fix the training).** Add a **fairness penalty** to the loss
  so the optimiser is punished for unfair outcomes:
  $$\mathcal{L} = \mathcal{L}_{\text{accuracy}} + \lambda \cdot \mathcal{L}_{\text{fairness}}$$
  Also adversarial debiasing (a second network tries to predict the protected
  attribute from the prediction; you train so it *cannot*). Powerful, but
  requires changing the model and training code.
- **Post-processing (fix the outputs).** Leave the model alone and adjust
  **decision thresholds per group** so a chosen fairness metric is met. Easy,
  works on a black-box model, and needs no retraining — but it is blunt and can
  feel like explicit different treatment, which may itself be legally sensitive.

> **Trade-off to state out loud:** earlier interventions are more effective but
> need more access; post-processing is the easiest lever when the model is a
> vendor black box. There is also an **accuracy–fairness trade-off** — expect
> to give up a little accuracy for a fairer system, and justify it with the cost
> of the unfairness.

---

## 18.4 Privacy — differential privacy, federated learning

> **SEBI / RBI flag — HIGH value.** Data privacy, consent, and data-protection
> law are core to financial-regulator IT syllabi. Know differential privacy and
> federated learning at the conceptual level here.

### Motivation

Models memorise. A language model can regurgitate a credit-card number it saw in
training; an attacker can sometimes tell whether *your* record was in the
training set (Section 18.5). If the data is medical, financial, or personal,
that is a serious breach. We need training that is **useful in aggregate but
reveals nothing about any single person.**

### Differential privacy (DP) — the epsilon idea

The core promise of DP: **the released result should be (almost) the same
whether or not any one person's data was included.** If your row cannot change
the output much, an attacker cannot learn about you from the output.

![Differential privacy: take the real answer to a query, add calibrated random noise, and release the noisy answer. A smaller epsilon means more noise, more privacy, and less accuracy.](images/m18_04_differential_privacy.png)

The mechanism is simple: compute the true answer, then **add carefully
calibrated random noise** before releasing it. Formally, a mechanism $M$ is
$\varepsilon$-differentially private if for any two datasets $D$, $D'$ that
differ by one record and any output $S$:
$$P(M(D)\in S) \le e^{\varepsilon}\, P(M(D')\in S)$$

- **Epsilon ($\varepsilon$) is the privacy budget.** Small $\varepsilon$ (e.g.
  0.1) = strong privacy, lots of noise, lower accuracy. Large $\varepsilon$ =
  weak privacy, little noise, higher accuracy. It is a **dial** between privacy
  and utility.
- In deep learning we use **DP-SGD**: clip each example's gradient and add
  Gaussian noise, so no single example dominates the update.
- The budget **composes**: each query spends some $\varepsilon$; run too many
  queries and privacy is used up.

> **One-line intuition:** DP adds just enough noise that "you" are hidden in the
> crowd, and $\varepsilon$ measures how big the crowd effectively is.

### Federated learning + secure aggregation

DP hides individuals inside an answer. **Federated learning** goes further: the
raw data *never leaves the device at all.*

![Federated learning: the central server sends the global model to each phone; each phone trains locally and sends back only model updates (never raw data); secure aggregation lets the server see only the summed update.](images/m18_05_federated.png)

The loop, as drawn:

1. The server sends the current **global model** down to many devices (phones).
2. Each device **trains locally** on its own private data.
3. Each device sends back **only the model update** (gradients/weights) — never
   the raw data (the green arrows up).
4. The server **averages** the updates (Federated Averaging) into a new global
   model, and repeats.

**Secure aggregation** adds a cryptographic layer so the server sees only the
*sum* of all updates, not any single device's update — so even the server
cannot reverse-engineer one user. Google's mobile keyboard (Gboard) is the
classic real example. Federated learning and DP are often **combined**: train
federated, and add DP noise to the aggregate.

---

## 18.5 Explainability & Interpretability

### Motivation

A regulator asks: *"Why was this specific customer denied a loan?"* "The neural
network said so" is not an acceptable answer — and under GDPR it may be
illegal. **Explainability** is the ability to give a human-understandable reason
for a model's behaviour. It is needed for debugging, trust, appeals, and legal
compliance.

Two questions, two scopes:

- **Global explanation:** *how does the model behave overall?* Which features
  matter across all predictions.
- **Local explanation:** *why THIS one prediction?* Which features pushed this
  single decision. Appeals and audits need **local** explanations.

![Explainability tools mapped to scope: global tools (feature importance, SHAP summary) explain the whole model; local tools (LIME, SHAP values) explain one prediction; attention gives hints for text and images but is not a true explanation.](images/m18_06_explainability.png)

### The main tools and when to use each

- **Feature importance (global).** Ranks features by overall contribution (e.g.
  permutation importance, tree gain). Cheap, coarse, model-level. Use for a
  quick "what drives this model?".
- **SHAP (SHapley Additive exPlanations).** Based on game theory: it fairly
  splits a prediction into per-feature **contributions** that add up to the
  output. **Local** per row *and* can be averaged for a **global** view.
  Theoretically grounded and consistent, but slow on large models. The go-to
  when you need trustworthy per-decision credit.
- **LIME (Local Interpretable Model-agnostic Explanations).** Fits a simple
  linear model *around one prediction* by perturbing the input and watching the
  output. **Local** only, model-agnostic, fast, but the explanation can be
  unstable (re-run gives a slightly different story). Good for a quick local
  peek at any black box.
- **Attention weights (for transformers).** Show which input tokens the model
  "looked at". Useful **hints** for text/images — but note: **attention is not a
  faithful explanation**; high attention does not prove causation. Treat it as a
  diagnostic, not proof.

> **Interview line:** *"For a loan denial appeal I'd use SHAP for a faithful,
> additive, per-customer reason; for a fast sanity check on any black box, LIME;
> attention is only a hint, not a legal explanation."*

---

## 18.6 Security — attacks on ML systems and defenses

> **SEBI / RBI flag — HIGH value.** Cyber-security of IT systems is central to
> regulator exams; ML-specific attacks are increasingly examinable and are
> directly relevant to financial fraud systems.

### Motivation

Classic security protects the *software*. ML adds a new attack surface: the
**data** and the **model** themselves can be attacked. An attacker may never
touch your servers and still break your model.

![Four attacks on ML systems: data poisoning corrupts training data; evasion tricks the model at inference; model stealing copies the model via queries; membership inference asks whether a record was in the training data. Defenses include robust training, rate-limiting, and differential privacy.](images/m18_07_security_attacks.png)

### The four main attacks

1. **Data poisoning (attacks training).** The attacker injects corrupted
   examples into the training set so the model learns a wrong or backdoored
   behaviour (e.g. "classify anything with this trigger patch as safe"). Common
   when you train on scraped or user-submitted data.
2. **Evasion / adversarial examples (attacks inference).** The attacker makes a
   tiny, often invisible change to a legitimate input that flips the prediction
   — a few pixels, or a sticker on a stop sign that a vision model reads as
   "speed limit". The model was never retrained; the *input* was crafted.
3. **Model stealing / extraction.** By sending many queries and recording
   outputs, an attacker trains a copy ("clone") of your model — stealing your IP
   or building a local model to craft further attacks against.
4. **Membership inference.** The attacker asks *"was this specific record in the
   training data?"* If yes, that can itself be a privacy breach (e.g. "this
   person was in the HIV-patients training set"). Overfit models leak more.

### Defenses (name at least one per attack)

- **Poisoning:** validate and sanitise training data; anomaly detection on
  inputs; provenance/lineage tracking; robust training.
- **Evasion:** **adversarial training** (train on adversarial examples), input
  preprocessing, ensembles, detecting out-of-distribution inputs.
- **Model stealing:** **rate-limit** and authenticate the API, add small output
  noise, watermark the model, monitor for scraping patterns.
- **Membership inference:** train with **differential privacy**, reduce
  overfitting (regularisation), limit output confidence detail.

> **Cross-link:** these defenses reuse ideas from Module 10 (monitoring for
> anomalous inputs) and Section 18.4 (DP protects against membership inference).

---

## 18.7 Governance — model cards, datasheets, regulation

> **SEBI / RBI flag — HIGH value.** Governance, auditability, and regulatory
> compliance are the single most exam-relevant part of this module for
> financial-regulator IT roles. Learn the artifacts and the risk tiers.

### Motivation

Fairness, privacy, and security are *properties*. **Governance** is the
*process* that makes an organisation prove and maintain them: documentation,
audit trails, sign-offs, and legal compliance. When a regulator investigates,
governance artifacts are the evidence.

### Documentation artifacts

- **Model cards.** A short standard document that ships *with* a model: what it
  does, intended use, training data, evaluation results **broken down by group**
  (fairness), known limitations, and ethical considerations. Think "nutrition
  label for a model".
- **Datasheets for datasets.** The same idea for data: how it was collected,
  who is in it, consent, known biases, and appropriate uses. Answers "should we
  even train on this?".
- **Audit logs / lineage.** Immutable records of *which model version, trained
  on which data, made which decision, when*. This is what makes a decision
  **auditable** and reproducible — essential in finance.

### Regulation you must be able to name

![Governance and the EU AI Act risk tiers: unacceptable risk (banned), high risk (credit and hiring, strict duties), limited risk (chatbots must disclose), and minimal risk (spam filters, no extra rules). Also model cards, datasheets, audit logs, and GDPR right-to-explanation.](images/m18_08_governance.png)

- **EU AI Act — risk tiers** (the diagram): the more potential harm, the more
  legal duty.
  - **Unacceptable** → banned (e.g. government social scoring).
  - **High risk** → allowed but heavily regulated (credit scoring, hiring,
    biometric ID): risk management, documentation, human oversight, logging.
    **Most finance ML lands here.**
  - **Limited risk** → transparency duty (a chatbot must disclose it is AI).
  - **Minimal risk** → no extra obligations (spam filter, game AI).
- **GDPR** (EU data-protection law): lawful basis and consent for personal data,
  data minimisation, the **right to explanation** for automated decisions, and
  the **right to erasure**. Directly motivates DP, model cards, and
  explainability above.
- **Sector rules (India-relevant):** RBI and SEBI issue their own IT, data
  localisation, model-risk, and outsourcing guidelines; the DPDP Act 2023 is
  India's data-protection law. The *pattern* is the same everywhere: document,
  justify, audit, and keep a human accountable.

---

## 18.8 Safety & Alignment for LLM Systems

### Motivation

Generative models add new risks: they can produce toxic, false ("hallucinated"),
biased, or dangerous text, and they can be manipulated by cleverly worded
prompts. **Alignment** is making the model *want* to do what we intend; **safety
guardrails** are the surrounding controls that catch failures anyway. (Deep
LLM-serving detail is in **Module 16** — here we cover the responsible-AI core.)

### The alignment idea — RLHF

Base language models predict the next token; they are not naturally helpful or
harmless. **RLHF (Reinforcement Learning from Human Feedback)** aligns them in
three steps:

1. **Supervised fine-tuning:** train on human-written good answers.
2. **Reward model:** humans rank pairs of answers; train a model to predict
   "which answer humans prefer".
3. **RL optimisation:** fine-tune the LLM to maximise that reward (e.g. PPO), so
   it produces answers humans prefer. A newer variant, **DPO**, skips the
   separate RL step and optimises preferences directly.

The result is a model that is more helpful, honest, and harmless — though never
perfectly so.

### Guardrails (defense in depth)

Alignment is not enough; wrap the model in controls:

- **Input filtering:** block prompt-injection and jailbreak attempts, and unsafe
  requests, *before* they reach the model.
- **Output filtering:** a safety classifier checks generations for toxicity,
  PII, or policy violations *after* the model, before the user sees them.
- **Grounding / RAG + citations:** reduce hallucination by forcing answers to
  cite retrieved sources.
- **Human-in-the-loop** for high-stakes actions, plus rate limits and abuse
  monitoring.

> **Senior signal:** treat safety as **defense in depth** — alignment (RLHF) +
> input guard + output guard + monitoring — not a single filter. Cross-link
> Module 16 for the serving mechanics.

---

## Module 18 — Interview Mapping (what companies probe)

| Company | How Module 18 shows up | Junior answer | Staff answer |
|---------|-----------------------|---------------|--------------|
| **Google / Meta** | "How would you make this recommender/loan model fair?" | "Delete the race column" | Names bias sources, picks a fairness metric for the harm, measures + mitigates, breaks the feedback loop |
| **Amazon** | Ties to trust / customer harm | Talks accuracy only | Reasons about cost of a wrong decision to the customer + human-in-loop |
| **OpenAI / Anthropic** | LLM safety, alignment, jailbreaks | "Add a keyword filter" | Defense in depth: RLHF + input/output guards + monitoring |
| **Stripe / banks / fintech** | Privacy, auditability, model risk | Ignores compliance | Model cards, audit logs, DP, explainability for appeals, EU AI Act high-risk duties |

**Common opening:** *"Your model works — what could make it irresponsible to
ship?"* Cover the six pillars: **fairness, privacy, explainability, security,
governance, safety.** Naming that checklist is itself the senior signal.

---

## Module 18 — Exam Mapping (SEBI / RBI / GATE / ISRO)

- **SEBI IT / RBI IT — HIGH value (flagged).** Expect direct questions on:
  **data privacy & protection law** (GDPR ideas, DPDP Act, consent, data
  localisation); **cyber-security** (attack types, defenses); **governance,
  auditability, and model risk**. Sections 18.4, 18.6, and 18.7 are the money
  sections for these exams — study them closely.
- **GATE CS / DA:** may touch fairness metrics and privacy at a conceptual
  level; formulas for demographic parity / equal opportunity are fair game.
  Heavy regulation detail is not tested.
- **ISRO / DRDO:** occasional definitions (adversarial examples, differential
  privacy) only.

> **Flag:** Unlike most interview-only modules, **this module carries genuine
> written-exam value for SEBI/RBI** via privacy, security, and governance. Do
> not skip 18.4–18.7 for those exams.

---

## Module 18 — Common Mistakes & Misconceptions

1. **"Delete the protected attribute → fair."** No — proxies (zip code, name)
   let the model reconstruct it. Fairness must be *measured*. (18.1–18.2.)
2. **"There is one fairness metric."** No — parity, equal opportunity, and
   equalized odds differ, and you cannot satisfy all at once. Choose by harm.
3. **"Anonymising by dropping names = private."** No — re-identification and
   membership inference defeat naive anonymisation; use DP. (18.4–18.5.)
4. **"Attention weights explain the model."** No — they are hints, not faithful
   explanations. Use SHAP/LIME for real local explanations. (18.5.)
5. **"Security is just the servers."** No — data poisoning and adversarial
   inputs attack the ML itself without touching infrastructure. (18.6.)
6. **"Governance is paperwork we can skip."** No — for high-risk (finance,
   hiring) systems it is a legal precondition to deploy. (18.7.)
7. **"RLHF makes an LLM safe."** It helps but is not enough; you still need
   input/output guardrails and monitoring. (18.8.)

---

## Module 18 — MCQs (with answers & explanations)

**Q1.** A model rejects far more women than men though sex is not a feature. Most
likely cause?
a) A compile bug  b) Proxy features + biased historical labels  c) Too little RAM  d) Wrong learning rate

<details><summary>Answer</summary>**b.** Features like name or career gaps proxy
for sex, and historical labels encode past bias, so the model reconstructs and
scales the unfairness. Deleting the column does not fix it.</details>

**Q2.** "Among applicants who truly qualify, each group is approved at the same
rate." Which metric?
a) Demographic parity  b) Equal opportunity  c) Equalized odds  d) Calibration

<details><summary>Answer</summary>**b.** Equal opportunity equalises the
true-positive rate ($P(\hat{Y}=1\mid Y=1)$) across groups. Demographic parity
ignores the true label; equalized odds also equalises the false-positive
rate.</details>

**Q3.** In differential privacy, decreasing epsilon ($\varepsilon$) does what?
a) More privacy, more noise, less accuracy
b) Less privacy, less noise
c) No effect
d) Removes the need for consent

<details><summary>Answer</summary>**a.** Epsilon is the privacy budget. Smaller
$\varepsilon$ means the output changes even less when one record is added/removed
— stronger privacy — achieved by adding more noise, costing accuracy.</details>

**Q4.** A phone trains on-device and sends only model updates to a server that
sees only their sum. This is:
a) Batch inference  b) Federated learning with secure aggregation  c) Model
stealing  d) A/B testing

<details><summary>Answer</summary>**b.** Raw data never leaves the device
(federated learning); secure aggregation ensures the server sees only the summed
update, not any individual's.</details>

**Q5.** A sticker on a stop sign makes a vision model read "speed limit". This is:
a) Data poisoning  b) Evasion / adversarial example  c) Membership inference  d) Model stealing

<details><summary>Answer</summary>**b.** The model is unchanged; the *input* is
crafted at inference time to flip the prediction — an evasion / adversarial
attack. Defense: adversarial training.</details>

**Q6.** Under the EU AI Act, a credit-scoring model is typically classed as:
a) Minimal risk  b) Limited risk  c) High risk  d) Unacceptable (banned)

<details><summary>Answer</summary>**c.** Credit scoring and hiring are high-risk:
allowed but with strict duties — risk management, documentation, human
oversight, and logging. This is why finance ML needs heavy governance.</details>

**Q7.** Which tool gives a *faithful, additive, per-prediction* explanation you
could show in a loan-denial appeal?
a) Attention weights  b) SHAP values  c) Overall accuracy  d) The confusion matrix

<details><summary>Answer</summary>**b.** SHAP splits a single prediction into
per-feature contributions that sum to the output (game-theoretic, consistent).
Attention is only a hint; accuracy and confusion matrices are global, not
per-decision.</details>

**Q8.** Best defense against membership-inference attacks?
a) Bigger model  b) Train with differential privacy + reduce overfitting  c) More
epochs  d) Remove the API rate limit

<details><summary>Answer</summary>**b.** Overfit models leak whether a record was
in training; DP and regularisation reduce that leakage. More epochs and bigger
models usually *increase* memorisation.</details>

---

## Module 18 — Design Exercises (easy → hard)

- **Easy.** For a hiring model, list the three sources of bias and one concrete
  example of each in that setting.
- **Easy.** Given approval rates of 60% (group A) and 42% (group B), does this
  pass the four-fifths (80%) rule? *(42/60 = 70% < 80% → fails.)*
- **Medium.** You must explain individual loan denials to customers. Choose an
  explainability tool, say global vs local, and justify it against a regulator's
  needs.
- **Medium.** Design a privacy strategy for training a next-word keyboard across
  millions of phones. Combine federated learning, secure aggregation, and DP;
  say what each one protects against.
- **Hard.** A fraud model is under attack. Describe how an adversary could use
  (1) evasion and (2) model stealing against it, and give a layered defense for
  each.
- **Hard.** Draft the outline of a **model card** for a credit-scoring model
  under the EU AI Act high-risk tier: list the sections and the fairness
  evidence you would include.

---

## Module 18 — Concept Review (one page)

- **Bias** enters via **data**, **labels**, and **feedback loops**; a model
  mirrors and amplifies its data. Deleting protected attributes fails (proxies).
- **Fairness metrics:** demographic parity (equal positive rate) · equal
  opportunity (equal TPR) · equalized odds (equal TPR **and** FPR). You cannot
  satisfy all at once — **choose by the harm**.
- **Mitigation** happens at three stages: **pre** (fix data) · **in** (fairness
  term in the loss) · **post** (adjust thresholds). Earlier = stronger but needs
  more access.
- **Differential privacy:** add noise so one record barely changes the output;
  **epsilon** is the privacy budget (small = private, noisy, less accurate).
- **Federated learning:** train on-device, send only updates; **secure
  aggregation** hides each individual update. Often combined with DP.
- **Explainability:** **global** (feature importance, SHAP summary) vs **local**
  (SHAP values, LIME). SHAP = faithful additive credit; LIME = fast local;
  attention = hint only.
- **Attacks:** poisoning (training) · evasion (inference) · model stealing
  (queries) · membership inference (privacy). Defenses: data validation,
  adversarial training, rate-limit, DP.
- **Governance:** model cards · datasheets · audit logs; **EU AI Act** risk
  tiers (unacceptable/high/limited/minimal); **GDPR** right-to-explanation.
  Finance ML is usually **high risk**.
- **LLM safety:** **RLHF** aligns; **guardrails** (input + output filters +
  monitoring) are defense in depth.

---

## Module 18 — Flash Cards (Q → A)

1. Three sources of bias? → *Data bias, label bias, feedback loops.*
2. Demographic parity in one line? → *Equal positive rate across groups.*
3. Equal opportunity vs equalized odds? → *Opportunity equalises TPR only; odds
   equalises TPR **and** FPR.*
4. What is epsilon in DP? → *The privacy budget; smaller = more noise, more
   privacy, less accuracy.*
5. Federated learning sends what to the server? → *Model updates, never raw
   data; secure aggregation hides individual updates.*
6. SHAP vs LIME vs attention? → *SHAP = faithful additive (local+global); LIME =
   fast local approx; attention = hint, not explanation.*
7. Four ML attacks? → *Poisoning, evasion, model stealing, membership
   inference.*
8. EU AI Act tier for credit/hiring? → *High risk (strict duties).*
9. RLHF in one line? → *Fine-tune an LLM to maximise human-preference reward.*

---

## Module 18 — Pattern Recognition (how to spot it in an interview)

- Hear **"is this model fair?"** → name bias sources, pick a fairness metric for
  the harm, measure + mitigate, break the feedback loop.
- Hear **"the data is sensitive / medical / financial"** → say differential
  privacy and/or federated learning, and mention consent + GDPR.
- Hear **"why did the model decide this for this person?"** → say **local**
  explanation; propose SHAP (or LIME for a quick check).
- Hear **"could someone attack this model?"** → name evasion, poisoning, model
  stealing, membership inference + one defense each.
- Hear **"we operate in a regulated industry"** → model cards, audit logs,
  human-in-loop, EU AI Act high-risk duties.
- Hear **"the chatbot said something harmful"** → defense in depth: RLHF + input
  guard + output guard + monitoring (link Module 16).

---

## Module 18 — Revision Notes / Mini Cheat Sheet

```
RESPONSIBLE AI = FAIR + PRIVATE + EXPLAINABLE + SECURE + GOVERNED + SAFE

BIAS SOURCES:   data | labels | feedback-loop   (deleting protected attr FAILS: proxies)
FAIRNESS:       demographic parity  P(Y'=1|A) equal
                equal opportunity   P(Y'=1|Y=1,A) equal   (TPR)
                equalized odds      TPR AND FPR equal      (strongest)
                -> can't satisfy all (impossibility); 4/5 rule = adverse impact
MITIGATION:     PRE (fix data) | IN (fairness loss term) | POST (adjust thresholds)

PRIVACY:        DP -> add noise; epsilon = privacy budget (small=private,noisy)
                Federated -> train on-device, send updates not data
                Secure aggregation -> server sees only the SUM

EXPLAIN:        global = feature importance / SHAP summary
                local  = SHAP values (faithful) | LIME (fast) | attention (hint only)

ATTACKS:        poisoning(train) | evasion(inference) | stealing(queries) | membership(privacy)
DEFENSES:       data validation | adversarial training | rate-limit+auth | DP

GOVERNANCE:     model cards | datasheets | audit logs
                EU AI Act: unacceptable(ban) > high(credit,hiring) > limited(disclose) > minimal
                GDPR: consent + right-to-explanation + erasure   (finance ML = HIGH risk)

LLM SAFETY:     RLHF (align) + guardrails (input/output filters) + monitoring = defense in depth
```

---

> **Next module:** *Module 19 — Systems Foundations for ML.* We come back down to
> the classic-system-design layer every ML system rests on — load balancing,
> caching, databases, queues, replication, gRPC/REST, SLAs/SLOs, and
> back-of-the-envelope capacity math — so you can size and scale the serving
> layer you now know how to make responsible.
