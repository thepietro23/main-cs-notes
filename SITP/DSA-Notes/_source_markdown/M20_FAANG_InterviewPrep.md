---
title: "Module 20 — Google / FAANG Interview Preparation"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 20 — Google / FAANG Interview Preparation

> **Why this module.**
> M1–M18 gave you the toolbox. This module is about **using it under interview
> conditions**: a repeatable problem-solving framework, instant pattern
> recognition, the curated problem sets that cover ~90% of questions (Blind 75 /
> Neetcode 150 / Grind 169), and what each company actually optimises for. The
> bar isn't "did you solve it" — it's "did you communicate, justify complexity,
> handle edge cases, and write clean code."

This module is **P0** for your stated goal (Google/Meta/Amazon/...).

> **How to read.** The framework, the pattern map, the curated lists, company
> specifics, and a study plan. (Track problems in the Excel **"Top 300"** tab.)

---

## 20.1 The Universal Interview Framework

![Interview framework: Clarify → Examples → Approach (brute force first) → Code → Test → Complexity.](images/134_interview_framework.png)

Follow this **every single time** (never jump straight to code):

1. **Clarify** — restate the problem; ask about input ranges, types, duplicates,
   empty/negative inputs, expected output. (Interviewers *plant* ambiguity.)
2. **Examples** — walk one small example by hand to confirm understanding.
3. **Approach** — state the **brute force** + its complexity first, *then*
   optimise. Think aloud; name the pattern.
4. **Code** — clean, readable, helper functions, good names. Keep narrating.
5. **Test** — dry-run your code; check edge cases (empty, size 1, overflow,
   duplicates, max bounds). Fix bugs calmly.
6. **Complexity** — state final **time and space**, and discuss trade-offs.

> **Scored signals** (what actually gets you hired): communication, brute-force-
> then-optimise, complexity analysis, edge-case discipline, clean code. A correct
> answer in silence often *fails*.

### MCQs

1. First step on any problem? → **clarify** (restate + ask constraints).
2. Before optimising, state? → the **brute force + its complexity**.
3. Biggest non-coding scored signal? → **communication / think-aloud**.

### 20.1a The Clarify → Brute → Optimize → Code → Test loop, expanded

Each step has a purpose and something the interviewer is *scoring*. Here is what to
actually say and do at each one:

| Step | What you do (out loud) | What it scores |
|---|---|---|
| **1. Clarify** | Restate the problem in your words. Ask: input size/range? types? duplicates allowed? empty/negative/overflow? sorted? in-place needed? what to return on no answer? | you don't code the wrong problem; you spot planted ambiguity |
| **2. Examples** | Walk one small input by hand; make one **edge** example too (empty, size 1). | shared understanding, catches misreads early |
| **3. Brute force** | State the obvious solution and **its complexity**, e.g. "check all pairs, O(n²) time O(1) space." | a baseline; shows you can always produce *something* |
| **4. Optimize** | Name the bottleneck ("the inner loop re-scans"), name the **pattern** ("this is a two-sum → hash map"), argue the new complexity *before* coding. | the core problem-solving signal |
| **5. Code** | Clean names, small helpers, narrate as you type. Handle the edge cases you listed in step 2. | readable, correct, maintainable code |
| **6. Test** | Dry-run your code line by line on the small example, then the edge cases. Fix calmly. | edge-case discipline, self-review |

**Communicating the complexity of *your* solution (do this explicitly):**

- State **both time and space**, in Big-O of the input: "**O(n log n)** time from
  the sort, **O(n)** space for the hash map."
- Tie each term to a line of code: "the sort is n log n; the single pass is n; sort
  dominates → **O(n log n)**."
- Discuss the **trade-off** you chose: "I used O(n) extra space to get O(n) time;
  a pure in-place version would be O(n²)."
- If the interviewer asks "can you do better?", first say the **theoretical lower
  bound** if you know it ("we must read all n inputs, so at least O(n)"), then
  whether your solution already meets it.

> **Memory hook:** never say "it's fast." Say **the Big-O, why, and the trade-off**
> — that sentence is a scored signal.

### 20.1b How to handle being stuck (interviewers expect this)

Getting stuck is normal; the interviewer scores **how you get unstuck**, not
whether you were flawless. A recovery ladder:

1. **Say what you're thinking** — "I'm trying to avoid the O(n²) re-scan; let me
   think about what to precompute." Silence reads as freezing; a stuck-but-talking
   candidate still scores.
2. **Go back to a smaller/concrete example** and look for structure or a pattern.
3. **Try a known pattern out loud** — "would sorting help? a hash map? two
   pointers? can I binary-search the answer?" (walk the §20.2 table).
4. **Solve a simpler version first** (e.g. no duplicates, or 1-D before 2-D), then
   generalise.
5. **Accept a hint gracefully** — interviewers *want* to nudge you; take it, say
   thanks, and build on it. Fighting a hint hurts more than needing one.
6. **Fall back to brute force and improve** — a working slow solution beats a
   broken clever one, and often reveals the optimisation.

> **Memory hook:** stuck ≠ failing. Think aloud, shrink the problem, try the
> pattern menu, and take the hint. Progress + communication is the score.

### MCQs

1. Asked "can you do better?" first mention? → the **lower bound** ("must read all
   n → ≥ O(n)").
2. When stuck, worst move? → **going silent**; instead narrate and try patterns.
3. How to report your solution's cost? → **both time and space Big-O + the
   trade-off**.

---

## 20.2 Pattern Recognition (classify in seconds)

![Pattern map: keyword in the problem → the technique and module (binary search, sliding window, heap, DP, graphs, hashmap, ...).](images/135_pattern_map.png)

| The problem says… | Reach for… |
|---|---|
| sorted array / "find target" / "min-max that works" | **Binary search** (M12) |
| contiguous subarray/substring + condition | **Sliding window / two pointers** (M2) |
| top-K / K-th largest / "closest K" | **Heap** (M6) |
| next greater/smaller, histogram, spans | **Monotonic stack** (M5) |
| all subsets / permutations / combinations | **Backtracking** (M13) |
| count ways / min cost / can-reach (overlapping) | **DP** (M14) |
| shortest path / connectivity / grid / islands | **BFS/DFS/Dijkstra/DSU** (M10) |
| "subarray sum = k" / pair / dedupe / frequency | **Hashmap** (M7) |
| intervals / meetings / merge / scheduling | **Sort + sweep / greedy** (M11) |
| prefix / range-sum queries | **Prefix sum / Fenwick** (M2 / M8b) |
| string matching / autocomplete | **KMP/Z / Trie** (M3) |

> **Drill this table** until classification is automatic — most interview problems
> are a known pattern in disguise.

### MCQs

1. "Longest substring with ≤ k distinct" → ? → **sliding window**.
2. "K-th largest in a stream" → ? → **heap**.
3. "Number of ways to make change" → ? → **DP**.

### 20.2a The top-6 patterns — a 10-second quick-classify

If you only drill six patterns, drill these — they cover the majority of interview
questions. Learn the *trigger phrase* and the *tell* for each:

| Pattern | Trigger in the problem | The tell / when it fits |
|---|---|---|
| **Two pointers** | sorted array, pair/triplet, "in place", palindrome | move two indices toward/with each other; O(n) instead of O(n²) |
| **Sliding window** | *contiguous* subarray/substring + a condition (longest/shortest/≤k) | grow the right edge, shrink the left when the window breaks the rule |
| **BFS / DFS** | grid/graph/tree, "reachable", "connected", "islands", shortest in *unweighted* | BFS = shortest unweighted / level order; DFS = explore / paths / backtrack |
| **Heap (priority queue)** | "top K", "K-th largest/smallest", "K closest", merge K lists | keep a size-K heap, or pop the min/max repeatedly; O(n log k) |
| **Binary search** | sorted input **or** "minimum/maximum value that works" | search the answer space; check the "monotonic predicate" (M12) |
| **Dynamic programming** | "count the ways", "min/max cost", "can we reach", overlapping choices | define a state, a transition, and base cases; memoise |

**How to use it live:** read the problem, scan this list top to bottom, and say the
first match aloud: "*contiguous* + *longest with a condition* → this is a **sliding
window**." Naming the pattern is half the solution and a strong scored signal.

> **Memory hook:** *Two pointers, Window, BFS/DFS, Heap, Binary search, DP.* Six
> tools cover most rounds — classify first, then code.

### MCQs

1. "Longest contiguous subarray with sum ≤ k" → ? → **sliding window**.
2. "Minimum capacity to ship within D days" → ? → **binary search on the answer**.
3. "Shortest path in an unweighted grid" → ? → **BFS**.

---

## 20.3 The Curated Problem Sets

Don't grind 2000 random problems — these cover the space:

- **Blind 75** — the classic minimum set, ~75 problems across all core patterns.
  *If you only do one list, do this.*
- **Neetcode 150** — Blind 75 + 75 more, grouped by pattern (arrays, two pointers,
  sliding window, stack, binary search, linked list, trees, tries, heap,
  backtracking, graphs, DP, greedy, intervals, math, bit). **Best structured
  path.**
- **Grind 75 / 169** — schedule-based (adjustable by hours/week).
- **LeetCode company tags** — once a company is targeted, do its tagged "last 6
  months" set.

> **Your Excel "Top 300 Problems" tab** seeds this pattern-wise; mark Solved /
> Revisit there. Aim for **breadth across patterns first**, then depth.

### Study sequence (recommended order)

Arrays & Hashing → Two Pointers → Sliding Window → Stack → Binary Search →
Linked List → Trees → Tries → Heap → Backtracking → Graphs → 1-D DP → 2-D DP →
Greedy → Intervals → Math & Bit. (Mirrors Neetcode's grouping and this course's
module order.)

### MCQs

1. The single best minimal list? → **Blind 75**.
2. Best *structured-by-pattern* path? → **Neetcode 150**.
3. Breadth or depth first? → **breadth across patterns**, then depth.

---

## 20.4 Company-Specific Focus

| Company | Coding focus | Other rounds / notes |
|---|---|---|
| **Google** | graphs, DP, trees, hard recursion; **optimal + clean + complexity** | "Googleyness", system design (L5+); ask clarifying Qs |
| **Meta** | arrays/strings, BFS/DFS; **fast pace (≈2 Qs/round)** | behavioral signals, system design; communicate while coding |
| **Amazon** | trees, graphs, DP, heaps; clean working code | **Leadership Principles (STAR)** heavily; bar-raiser |
| **Microsoft** | arrays, strings, trees, linked lists; practical | design + behavioral; clarity valued, friendlier pace |
| **Apple** | domain + DSA, depth in your area | team-specific; strong fundamentals |
| **Netflix** | senior **system design** + DSA | culture ("freedom & responsibility"); fewer, senior rounds |
| **Uber/Stripe** | practical coding, API design, concurrency | Stripe: integration-style coding; system design |
| **OpenAI/Anthropic** | strong DSA + ML/AI eng + practical coding | research/eng depth (see Module 21) |
| **NVIDIA** | DSA + systems/CUDA/perf | cache/memory awareness valued (Module 1) |
| **Databricks/Palantir** | DSA + distributed/data systems | design; sometimes take-home |

- **Amazon LP tip:** prepare ~10 STAR stories mapped to the Leadership Principles;
  every behavioral answer ties to one.
- **Google tip:** they want the *optimal* solution and a crisp complexity
  argument; partial/brute-only often isn't enough at the bar.

### MCQs

1. Amazon's signature non-coding round? → **Leadership Principles (STAR)**.
2. Meta interview pace? → **fast** (~2 problems/round).
3. Google emphasises? → **optimal solution + clean code + complexity**.

### 20.4a Behavioral rounds: the STAR method

Behavioral questions ("Tell me about a time you…") are scored just like coding
rounds — with a rubric. **STAR** is the structure that answers them well:

| Letter | Means | What to say (keep it tight) |
|---|---|---|
| **S — Situation** | the context | 1–2 sentences: project, your role, the stakes |
| **T — Task** | your specific goal / responsibility | what *you* had to achieve, and the constraint |
| **A — Action** | what **you** personally did | the bulk of the answer; concrete steps, decisions, trade-offs — use "**I**", not "we" |
| **R — Result** | the outcome, **quantified** | metrics ("cut latency 40%", "shipped 2 weeks early"), and what you learned |

**Worked skeleton** (question: *"a time you handled a conflict"*):

```text
S: On the payments team, a teammate and I disagreed on the retry design
   two days before a launch.
T: I had to reach a decision we could both own without slipping the date.
A: I wrote up both designs with their failure modes, ran a quick load test on
   each, and proposed a hybrid; I set up a 20-min call to walk through the data.
R: We shipped on time; the hybrid cut failed payments ~30%. I learned to bring
   data to a disagreement instead of opinions.
```

- **Prepare ~8–10 stories** from real experience, each tagged to themes: conflict,
  failure, leadership, ambiguity, tight deadline, disagreed-with-manager, biggest
  achievement. One good story can answer several questions.
- **Amazon specifically:** map each story to a **Leadership Principle** (Customer
  Obsession, Ownership, Dive Deep, Bias for Action, …); state the outcome with
  **numbers**; expect follow-up "dive deep" questions, so know the details.
- **Common traps:** telling a team story in "we" (they score *your* actions),
  rambling with no result, or picking a fake weakness. Be specific and honest.

> **Memory hook:** **S**ituation, **T**ask, **A**ction, **R**esult — spend most of
> your words on **A** (what *I* did) and always land a **quantified R**.

### MCQs

1. STAR stands for? → **Situation, Task, Action, Result**.
2. Which part deserves the most detail? → **Action** (what *you* personally did).
3. Amazon behavioral tip? → **map each story to a Leadership Principle + quantify
   the result**.

---

## 20.5 A Realistic Study Plan

- **Foundation (weeks 1–8):** learn patterns (this course M1–M14) + ~100 problems
  across patterns.
- **Volume (weeks 9–16):** Neetcode 150 / Blind 75; ~150–200 problems; redo missed
  ones.
- **Polish (weeks 17–24):** **mock interviews** (Pramp/peers), company-tagged
  problems, behavioral prep, system design (for senior).
- **Daily:** 2–4 problems, always **timed** (35–45 min), always **think-aloud**.
- **Weakness log:** track every problem you missed and *why* (pattern? bug? edge
  case?) and re-drill it.

> See the Excel **"6-Month Roadmap"** and **"Interview Roadmap"** tabs for the
> week-by-week and company-by-company plans.

### MCQs

1. Practice problems how? → **timed + think-aloud**.
2. What to track? → a **weakness log** (what you missed and why).
3. Senior rounds add? → **system design** + behavioral.

### 20.5a Mock-interview cadence

Solving problems alone does not train the *interview* skill — talking while
solving, under a stranger's eyes, does. Build mocks into the plan:

- **When to start:** once you have covered the core patterns (≈ end of the Volume
  phase). Mocks before that just expose gaps you already know about.
- **Cadence:** **1–2 mocks per week** in the Polish phase, ramping to **~3 per
  week** in the last 2–3 weeks before real interviews. Fewer than one a week and
  the nerves never fade.
- **Where:** **Pramp** / **interviewing.io** (peer or paid), or a study partner;
  alternate being interviewer and interviewee — *giving* a mock sharpens your eye
  for the scored signals.
- **Make it realistic:** full 45-minute clock, think-aloud the whole time, a
  shared editor with **no autocomplete/run** (whiteboard-like), camera on.
- **Debrief every mock:** ask for one thing to keep and one to fix; log it in the
  weakness log. Track your **communication** and **complexity-articulation**, not
  just correctness.
- **Include behavioral mocks** and, for senior roles, **system-design mocks** —
  those rounds also need reps, not just reading.

> **Memory hook:** you can't cram the *performance*. Rehearse the room: real clock,
> think-aloud, a human watching — then debrief and log.

### MCQs

1. When should mocks begin? → **after core patterns are covered** (Polish phase).
2. Mock cadence near interviews? → **~2–3 per week**.
3. What to debrief after each mock? → **communication + complexity + one fix**,
   logged.

---

## Module 20 — Concept Review (one page)

- **Framework:** Clarify → Examples → Approach (brute force first) → Code → Test →
  Complexity. Communication + complexity + edge cases are scored.
- **Pattern map:** learn keyword → technique (binary search, sliding window, heap,
  monotonic stack, backtracking, DP, graphs, hashmap, intervals, prefix sum).
- **Lists:** Blind 75 (minimum), Neetcode 150 (structured), Grind (scheduled);
  breadth → depth; track in the Excel Top-300 tab.
- **Companies:** Google (optimal+clean), Meta (fast pace), Amazon (LP/STAR),
  Microsoft (practical), AI labs (DSA+ML).
- **Plan:** patterns → volume → mocks; daily timed think-aloud; keep a weakness
  log.

## Module 20 — Flash Cards

- Q: Steps before coding? **A: clarify, examples, approach (brute force first).**
- Q: Top scored signal? **A: communication / think-aloud.**
- Q: Best structured list? **A: Neetcode 150.**
- Q: Amazon's key round? **A: Leadership Principles (STAR).**
- Q: Practice style? **A: timed + think-aloud + weakness log.**
- Q: STAR = ? **A: Situation, Task, Action, Result (most detail on Action).**
- Q: When stuck in an interview? **A: think aloud, shrink the problem, try the
  pattern menu, take the hint.**
- Q: Report your solution's cost how? **A: time + space Big-O + the trade-off.**
- Q: The top-6 patterns? **A: two pointers, sliding window, BFS/DFS, heap, binary
  search, DP.**
- Q: Mock-interview cadence near D-day? **A: ~2–3 per week, then debrief.**

## Module 20 — Pattern Recognition

(See §20.2 table — the master keyword→technique map. This *is* the interview
skill: classify the problem, then apply the right module.)

## Module 20 — Interview Questions (meta-level)

1. *Walk me through how you'd approach an unfamiliar problem.* → the framework.
2. *Give the brute force, then optimise.* → always lead with brute + complexity.
3. *What's the time/space complexity, and the trade-off?* → state both, discuss.
4. *(Amazon)* *Tell me about a time you…* → STAR story mapped to an LP.

## Module 20 — GATE / SEBI / RBI / ISRO Perspective

- Different format (MCQ/written), but the **pattern-recognition** and
  **complexity** reflexes transfer directly. For exams, prioritise the
  module-by-module mastery (M1–M18) over interview-specific drills.

---

*End of Module 20. Next: Module 21 — AI Engineering DSA (vector search, ANN,
HNSW/FAISS, beam search, tokenization, RAG) — with visuals.*
