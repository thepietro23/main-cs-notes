---
title: "Module 5 — Normalization & Functional Dependencies"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 5 — Normalization & Functional Dependencies

> **Where this module sits.**
> Module 2 designed tables (ER), Module 3 made them precise (keys), Module 4
> queried them (SQL). But a *badly designed* table — even a valid one — causes
> **redundancy** and **anomalies**. Normalization is the theory that tells us how
> to split tables so each fact lives in exactly one place. It is built on
> **functional dependencies**. This is the **single highest-scoring topic** in
> SEBI/RBI/GATE DBMS — numericals on candidate keys, closures, and "highest
> normal form" appear almost every year.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★★★★★   | ★★★★      | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **attribute closure** &
**candidate keys** from FDs; **prime vs non-prime**; **identify the highest normal
form** of a given relation; **partial vs transitive dependency**; **3NF vs BCNF**;
**lossless join** test; **dependency preservation**; **minimal/canonical cover**;
**Armstrong's axioms**; **MVD & 4NF**.

---

## 5.1 The Problem — Redundancy and Anomalies

### Motivation (first principles)

Suppose we cram student *and* course *and* instructor data into one table. The
moment one fact (a course's name, an instructor) is stored in **many** rows, three
problems appear. **Each anomaly is the reason normalization exists.**

![Three anomalies on a redundant ENROLL table: insertion (can't add a course with no student), update (rename must touch many rows), deletion (removing last student loses the course).](images/45_anomalies.png)

| Anomaly | What goes wrong |
|---------|-----------------|
| **Insertion** | Can't add a new course until some student enrolls (the key needs a `sid`). |
| **Update** | Renaming a course means changing **many** rows; miss one → **inconsistency**. |
| **Deletion** | Deleting the last student of a course **loses the course's data** entirely. |

> **Root cause:** one table is storing facts about **two different things**
> (students *and* courses). **Normalization = decomposing tables so every fact
> lives in exactly one place**, removing redundancy and these anomalies.

> **Trade-off preview:** more normalization → less redundancy but **more joins**
> at query time. Sometimes we deliberately **denormalize** for read performance
> (Module 11). But you must know the normal forms first.

---

## 5.2 Functional Dependencies (FDs) — The Foundation

### Definition

A **functional dependency** `X → Y` means: *if two tuples agree on X, they must
agree on Y.* X **functionally determines** Y. X is the **determinant**.

![Functional dependency X→Y: X (determinant) determines Y (dependent); plus types — trivial, non-trivial, full, partial, transitive.](images/46_functional_dependency.png)

> *Example:* `roll → name` — the same roll number always maps to the same name.
> But `name → roll` is **false** (two students can share a name).

### Types of FD (each maps to a normal form)

| Type | Meaning | Matters for |
|------|---------|-------------|
| **Trivial** | `Y ⊆ X` (e.g. `AB → A`). Always true. | — |
| **Non-trivial** | `Y ⊄ X` (the useful kind). | everything |
| **Full** | Y depends on the **whole** key. | 2NF |
| **Partial** | Y depends on **part** of a composite key. | **breaks 2NF** |
| **Transitive** | `X → Y → Z` through a non-key Y. | **breaks 3NF** |

> **FDs are a property of the *schema/meaning*, not of one instance.** You assert
> `roll → name` because of the *rule* "one roll = one student", not because the
> current rows happen to satisfy it. A common conceptual mistake is "inferring"
> FDs from sample data — sample data can only *disprove* an FD, never prove it.

---

## 5.3 Armstrong's Axioms — Deriving All FDs

To reason about FDs formally (and compute closures), we use **Armstrong's
axioms** — a set of inference rules that are **sound** (derive only true FDs) and
**complete** (derive *all* implied FDs).

![Armstrong's axioms: primary rules (reflexivity, augmentation, transitivity) and derived rules (union, decomposition, pseudo-transitivity).](images/47_armstrong_axioms.png)

**Primary (the 3 you must memorize):**

1. **Reflexivity:** if `Y ⊆ X`, then `X → Y` (gives trivial FDs).
2. **Augmentation:** if `X → Y`, then `XZ → YZ` (add the same attribute to both
   sides).
3. **Transitivity:** if `X → Y` and `Y → Z`, then `X → Z` (chaining).

**Derived (from the three above):**

4. **Union:** `X → Y, X → Z ⟹ X → YZ`.
5. **Decomposition:** `X → YZ ⟹ X → Y and X → Z`.
6. **Pseudo-transitivity:** `X → Y, WY → Z ⟹ WX → Z`.

> **Why we care:** these rules let us compute **attribute closure**, find
> **candidate keys**, and test whether two FD sets are **equivalent** — the
> machinery behind every normalization question.

---

## 5.4 Attribute Closure (X⁺) — The Master Tool

The **closure** of an attribute set X, written **X⁺**, is the set of *all*
attributes functionally determined by X. This one algorithm answers almost every
FD question.

![Worked attribute closure: given R(A,B,C,D,E) with A→B, B→C, CD→E, computing A+ = {A,B,C} step by step, concluding A is not a key.](images/48_attribute_closure.png)

**Algorithm:** start with `X⁺ = X`; repeatedly, for any FD `L → R` where `L ⊆ X⁺`,
add R to X⁺; stop when nothing more can be added.

**Worked example** — `R(A,B,C,D,E)`, FDs `A→B, B→C, CD→E`:

```
A⁺ = {A}                start
A⁺ = {A,B}              apply A→B
A⁺ = {A,B,C}            apply B→C
   CD→E? need C AND D — D ∉ A⁺ — cannot apply
A⁺ = {A,B,C}            FINAL   ⟹ A is NOT a key (D,E missing)
```

**Uses of closure:**

1. **Is X a super key?** → yes iff `X⁺ = all attributes`.
2. **Find candidate keys** → minimal X with `X⁺ = all attributes`.
3. **Does `X → Y` hold?** → yes iff `Y ⊆ X⁺`.
4. **Are two FD sets equivalent?** → each FD of one is implied by the other
   (check via closures). **Worked example:** is `F = {A→B, B→C}` equivalent to
   `G = {A→B, A→C, B→C}`? Check `G ⊆ F⁺`: under F, `A⁺={A,B,C}` so `A→C` holds ✓
   (and `A→B`, `B→C` are in F). Check `F ⊆ G⁺`: under G, both `A→B` and `B→C` hold
   ✓. Both directions hold → **F ≡ G** (they cover the same FDs). `F` is the smaller
   (it's a cover of `G`).

> **Candidate-key shortcut (asked constantly):** attributes that appear **only on
> the left** of FDs (or in **no** FD) **must** be in *every* candidate key — start
> your search there. In the example, `D` appears only on a left side and never on a
> right side, so `D` must be in every key; indeed `(AD)⁺ = {A,B,C,D,E}` = all, and
> neither A nor D alone works → **AD is the candidate key**. (See the
> candidate-key flowchart in Module 3 §3.2.)

**Finding ALL candidate keys (systematic procedure):**

1. Classify each attribute by where it appears in the FDs:
   - **only on LHS / in no FD** → **essential** (must be in *every* key).
   - **only on RHS** → **never** in any candidate key.
   - **on both sides** → "middle" attributes (may or may not be needed).
2. Compute the closure of the **essential** set. If it's already all attributes,
   that's the **only** candidate key.
3. Otherwise, add **middle** attributes (one, then pairs, …) to the essential set;
   any *minimal* combination whose closure = all attributes is a candidate key.
   Stop adding to a set once it becomes a key (supersets of a key are super keys,
   not candidate keys).

> *Example:* `R(A,B,C,D,E)`, `A→B, BC→D, E→C, D→A`. Essential = `{E}` (E is only on
> a LHS). `E⁺={E,C}` ≠ all, so pair E with a middle attribute: `(A,E), (B,E),
> (D,E)` each close to all → **candidate keys = {A,E}, {B,E}, {D,E}**. `{B,C,E}`
> contains the key `{B,E}`, so it's a **super key, not a candidate key**.

---

## 5.5 Minimal (Canonical) Cover

A **minimal cover** is the smallest FD set equivalent to the original — handy for
3NF decomposition and for removing redundancy in constraints.

![Minimal cover in 3 steps: make right-hand sides single attributes, remove extraneous left-hand attributes, remove redundant FDs.](images/49_minimal_cover.png)

**Three steps:**

1. **Singleton RHS** — split every FD so the right side has **one** attribute
   (`A→BC` becomes `A→B, A→C`).
2. **Remove extraneous LHS attributes** — for each FD with a composite left side,
   drop any attribute that isn't needed. *Precise test:* attribute `B` is
   extraneous in `XB → Y` if `Y ⊆ (X)⁺` computed under the **current** FD set
   (i.e. you can still derive Y without B). If so, replace `XB → Y` with `X → Y`.
3. **Remove redundant FDs** — drop any FD that is still implied by the rest (check
   with closure).

> *Result for `{A→BC, B→C, A→B, AB→C}`* → minimal cover `{A→B, B→C}`. A minimal
> cover is **not always unique** (the result can depend on the order you process
> FDs), but all minimal covers are equivalent.

---

## 5.6 The Normal Forms — Overview

A **normal form** is a rule about which FDs are allowed. Each higher form is
**stricter** and removes more redundancy. Each form **includes** all lower forms.

![The normalization ladder: 1NF (atomic), 2NF (no partial dep), 3NF (no transitive dep), BCNF (every determinant a super key), 4NF (no MVD), 5NF (no join dependency).](images/50_normal_forms_ladder.png)

| Form | Requirement (on top of the previous) |
|------|--------------------------------------|
| **1NF** | all values **atomic** (no repeating groups / multivalued cells) |
| **2NF** | no **partial** dependency (non-prime depends on the *whole* key) |
| **3NF** | no **transitive** dependency (non-prime → non-prime) |
| **BCNF** | **every** determinant is a **super key** |
| **4NF** | no non-trivial **multivalued dependency** (MVD) |
| **5NF** | no **join dependency** (decomposable only via candidate keys) |

> **Practical target:** **3NF or BCNF**. 4NF/5NF matter in specific cases. Most
> real schemas aim for 3NF (always achievable losslessly *and* dependency-
> preserving) and go to BCNF only where redundancy demands it.

---

## 5.7 First Normal Form (1NF)

**1NF:** every attribute value is **atomic** — no lists, sets, or repeating groups
in a single cell.

> *Violation:* a `phones` column holding `"9991, 9992"`, or repeating columns
> `course1, course2, course3`. *Fix:* one value per cell — split the multivalued
> data into separate rows (or a separate table). This is the same **atomic-domain**
> rule from Module 3.

> **Note:** the relational model technically *assumes* 1NF. So "un-normalized" in
> exams usually means a table with repeating groups that you must flatten first.

---

## 5.8 Second Normal Form (2NF) — No Partial Dependency

**2NF:** in 1NF **and** no **non-prime** attribute is **partially** dependent on a
candidate key (i.e. every non-prime attribute depends on the **whole** key, not
part of it).

![2NF: a table keyed by (sid,cid) where sname depends only on sid (partial dependency) is split into STUDENT(sid,sname) and ENROLL(sid,cid,marks).](images/51_2nf_partial.png)

**Partial dependency** = a non-prime attribute depends on **part** of a composite
candidate key.

> *Example:* `ENROLL(sid, cid, sname, marks)` with key `{sid, cid}`. Here `sname`
> depends only on `sid` (part of the key) → **partial dependency** → not 2NF.
> *Fix:* split into `STUDENT(sid, sname)` and `ENROLL(sid, cid, marks)`.

> **Key fact (exam):** 2NF is only relevant when the candidate key is
> **composite**. If every candidate key is a **single attribute**, the relation is
> **automatically in 2NF** (there's no "part" of the key to depend on).

---

## 5.9 Third Normal Form (3NF) — No Transitive Dependency

**3NF:** in 2NF **and** no **transitive** dependency — no non-prime attribute
depends on another **non-prime** attribute.

![3NF: a table where sid→dept_id→dept_name (transitive) is split into STUDENT(sid,dept_id) and DEPT(dept_id,dept_name).](images/52_3nf_transitive.png)

**Transitive dependency** = `X → Y → Z` where Y is **not** a candidate key, so a
non-prime (Z) depends on a non-prime (Y).

> *Example:* `STUDENT(sid, dept_id, dept_name)` with `sid → dept_id → dept_name`.
> `dept_name` depends on `dept_id` (a non-key) → **transitive** → not 3NF.
> *Fix:* `STUDENT(sid, dept_id)` and `DEPT(dept_id, dept_name)`.

> **The formal 3NF test (memorize — this is the exact rule):** a relation is in
> 3NF if for **every** non-trivial FD `X → Y`, **either** X is a **super key**,
> **or** every attribute of Y is a **prime** attribute (part of some candidate
> key). The second clause is the "escape hatch" that BCNF removes.
>
> The phrase *"no non-prime depends on another non-prime"* is a handy **heuristic**
> for spotting violations, but the formal "super key OR Y is prime" test above is
> the precise definition — always apply the formal test in exams.

---

## 5.10 Boyce-Codd Normal Form (BCNF)

**BCNF:** for **every** non-trivial FD `X → Y`, **X must be a super key**. (It
removes 3NF's "Y is prime" exception — so BCNF is **stricter** than 3NF.)

![BCNF: for every non-trivial FD the determinant must be a super key; the classic violation is overlapping candidate keys (teacher→subject where teacher is not a super key).](images/53_bcnf.png)

> **Classic BCNF violation (overlapping candidate keys):**
> `R(student, subject, teacher)` with `teacher → subject` and
> `(student, subject) → teacher`. Candidate keys: `(student, subject)` and
> `(student, teacher)`. The FD `teacher → subject` has a determinant (`teacher`)
> that is **not** a super key → **3NF but not BCNF**.

> **The crucial trade-off (a guaranteed exam/interview point):**
> - **BCNF** decomposition is **always lossless**, but may **not** preserve all
>   dependencies.
> - **3NF** is **always achievable** with **both** lossless join **and**
>   dependency preservation.
> - So: if you *must* keep all FDs checkable on single tables, **stop at 3NF**;
>   go to BCNF only when the remaining redundancy is unacceptable.

---

## 5.11 Decomposition Properties — Lossless Join & Dependency Preservation

When we split a table, two properties decide whether the split is "good".

![Decomposition properties: lossless join (rejoining gives exactly the original, no spurious rows; test via common attributes being a key of one piece) and dependency preservation (every FD checkable on a single table).](images/54_lossless_dependency.png)

### Lossless join (non-additive) — MANDATORY

Rejoining the decomposed tables must give back **exactly** the original — no
**spurious (extra) tuples**.

> **The test for `R → R1, R2`:** the decomposition is lossless **iff** the common
> attributes form a key of at least one piece:
> `(R1 ∩ R2) → R1` **or** `(R1 ∩ R2) → R2`.

> *Worked example:* `R(A,B,C)` → `R1(A,B), R2(B,C)`, common attribute `B`. If
> `B → C`, then `B` is a key of `R2(B,C)` → **lossless**. If `B` determines
> nothing, the join produces spurious tuples → **lossy**.

> **For decomposition into 3+ tables**, the simple two-table rule isn't enough —
> use the **chase / tableau (matrix) algorithm**: build a grid of pieces × all
> attributes, fill matching symbols using the FDs, and the decomposition is
> lossless iff some **row becomes all-distinguished** (all original symbols). Know
> the name; GATE occasionally tests it.

### Dependency preservation — DESIRABLE

Every original FD should be checkable on **one** decomposed table (without a join).
Formally `(F1 ∪ F2 ∪ …) ≡ F`. If lost, enforcing a constraint needs a join every
time — slow.

> **Summary rule:** *Lossless join is non-negotiable* (else you corrupt data).
> *Dependency preservation is desirable* (else constraint-checking is expensive).
> 3NF guarantees both; BCNF guarantees only lossless.

---

## 5.11A Fully Worked GATE Numericals (do these until they're automatic)

This is the highest-yield section for SEBI/RBI/GATE. Everything above is theory;
here we grind the **exact keystrokes** of each computation. Cover the answer, redo
it, and check.

### (a) Closure X⁺ — every step shown

> *Given:* `R(A,B,C,D,E,F)`, `F = { A→B, B→C, CD→E, A→D, E→F }`. Compute `A⁺`.

```text
A⁺ = {A}                          start
  A→B?  A⊆A⁺  → add B             A⁺ = {A,B}
  A→D?  A⊆A⁺  → add D             A⁺ = {A,B,D}
  B→C?  B⊆A⁺  → add C             A⁺ = {A,B,C,D}
  CD→E? C,D⊆A⁺ → add E            A⁺ = {A,B,C,D,E}
  E→F?  E⊆A⁺  → add F             A⁺ = {A,B,C,D,E,F}
nothing left to add               A⁺ = {A,B,C,D,E,F} = ALL  ⟹ A is a SUPER KEY
```

> **Reading the result:** since `A⁺` = all attributes, `A` alone determines
> everything → `A` is a super key, and (being a single attribute) it is the
> **candidate key**. If we ask "does `A → E` hold?", the answer is **yes** because
> `E ∈ A⁺`.

### (b) Finding ALL candidate keys — the LHS/RHS/BOTH classification

> *Given:* `R(A,B,C,D,E)`, `F = { AB→C, C→D, D→B, A→E }`. Find all candidate keys.

**Step 1 — classify each attribute** by where it appears across the FDs:

```text
attr | appears on LHS? | appears on RHS? | verdict
-----+-----------------+-----------------+---------------------------
 A   |      yes        |      no         | ESSENTIAL (only-LHS) → in EVERY key
 B   |      yes        |     yes (D→B)   | middle
 C   |      yes        |     yes (AB→C)  | middle
 D   |      yes        |     yes (C→D)   | middle
 E   |      no         |     yes (A→E)   | only-RHS → NEVER in any key
```

**Step 2 — close the essential set `{A}`:**

```text
A⁺ = {A}; A→E → {A,E}.  AB→C needs B (∉); C→D needs C (∉); D→B needs D (∉).
A⁺ = {A,E} ≠ ALL  → A alone is NOT a key. Must add a middle attribute.
```

**Step 3 — add middle attributes minimally** (try `A` + one of B/C/D):

```text
(A,B)⁺: A,B,E then AB→C→C then C→D→D → {A,B,C,D,E} = ALL  ✓ candidate key
(A,C)⁺: A,C,E then C→D→D then D→B→B then AB→C(have) → {A,B,C,D,E} = ALL  ✓ candidate key
(A,D)⁺: A,D,E then D→B→B then AB→C→C → {A,B,C,D,E} = ALL  ✓ candidate key
```

Each is **minimal** (A alone failed, and A is mandatory). No need to test triples —
supersets of these are super keys, not candidate keys.

> **Answer: candidate keys = {A,B}, {A,C}, {A,D}.**
> **Prime attributes** = union of all candidate keys = **{A,B,C,D}**;
> **non-prime** = **{E}**.

### (c) Minimal (canonical) cover — all three passes worked

> *Given:* `F = { A→BC, B→C, AB→C, A→B }`. Find a minimal cover.

**Pass 1 — singleton RHS** (split multi-attribute right sides):

```text
A→BC  ⟹  A→B , A→C
Now F = { A→B, A→C, B→C, AB→C, A→B }   (A→B appears twice — keep the set)
Working set: { A→B, A→C, B→C, AB→C }
```

**Pass 2 — remove extraneous LHS attributes** (only FDs with composite LHS: `AB→C`):

```text
Is A extraneous in AB→C?  compute B⁺ under current set = {B,C}. C ∈ B⁺ → YES, A extraneous.
  ⟹ AB→C becomes B→C  (already present) → drop the duplicate.
Working set: { A→B, A→C, B→C }
```

**Pass 3 — remove redundant FDs** (drop each FD, test if still derivable):

```text
Remove A→C. Under { A→B, B→C }:  A⁺ = {A,B,C} ⊇ {C}. So A→C is REDUNDANT → drop it.
Remove A→B. Under { B→C }:       A⁺ = {A}. B ∉ A⁺ → NOT redundant → keep.
Remove B→C. Under { A→B }:       B⁺ = {B}. C ∉ B⁺ → NOT redundant → keep.
```

> **Answer: minimal cover = { A→B, B→C }.** (Process order matters — a different
> order can give a different but equivalent minimal cover.)

### (d) Lossless-join check — the tableau (matrix / chase) method, 3 tables

The two-table rule (`R1∩R2` is a key of a piece) can't handle 3+ pieces. Use the
**tableau**. Rows = decomposed tables, columns = all attributes. Put `aⱼ`
(distinguished) where the table has that attribute, `bᵢⱼ` (non-distinguished)
elsewhere. Then apply FDs: whenever two rows agree on the LHS, equate their RHS
symbols (prefer an `a`). **Lossless iff some row becomes all-`a`.**

> *Given:* `R(A,B,C,D,E)`, decomposition `R1(A,B)`, `R2(B,C,D)`, `R3(D,E)`;
> `F = { A→BC, C→D, D→E }`.

**Initial tableau:**

```text
        A     B     C     D     E
R1(AB)  a1    a2    b13   b14   b15
R2(BCD) b21   a2    a3    a4    b25
R3(DE)  b31   b32   b33   a4    a5
```

**Apply FDs (equate RHS where LHS matches):**

```text
C→D: rows R2,R3? they must agree on C first — only R2 has a3, R3 has b33 → no match yet.
D→E: R2 and R3 agree on D (both a4) → equate E: R2's b25 := a5 (take the 'a').
       R2 row: b21  a2  a3  a4  a5
C→D:  (no two rows share the same C symbol) → no change.
A→BC: (only R1 has a1 for A) → no change.
```

Recheck: does any row have all `a`'s? Not yet. But note **this particular
decomposition is lossy** — no row reaches all-`a`, and there is no way to recover
`A` into R2/R3 (A only appears in R1, and nothing determines A). 

> **Contrast — a lossless case:** decompose the same R as `R1(A,B,C)`, `R2(C,D)`,
> `R3(D,E)`. `R1∩R2 = C`, and `C→D` makes C a key of R2; `R2∩R3 = D`, and `D→E`
> makes D a key of R3; `A→BC` makes A a key of R1. Rejoining pairwise on a key each
> time is lossless at every step → **lossless overall.** (In the tableau, row R1
> would fill to all-`a`.)

> **Fast two-table reflex (use whenever there are exactly 2 pieces):** `R(A,B,C)`
> → `R1(A,B), R2(A,C)`. Common attr = `A`. If `A→BC` (so `A` is a key), then
> `(R1∩R2)→R1` holds → **lossless**. If instead only `B→C`, common attr `A`
> determines neither whole piece → **lossy** (spurious tuples on rejoin).

### (e) Dependency-preservation check — worked both ways

**Rule:** decomposition `{R1,…,Rk}` preserves `F` iff `(F1 ∪ F2 ∪ … ∪ Fk)⁺ = F⁺`,
where each `Fᵢ` is the projection of F onto `Rᵢ` (the FDs whose attributes all fit
inside `Rᵢ`). Practically: for **each** original FD `X→Y`, check `Y ⊆ X⁺` computed
**using only the preserved (local) FDs**.

> *Given:* `R(A,B,C)`, `F = { A→B, B→C, C→A }`, decomposition `R1(A,B)`, `R2(B,C)`.
> Projected FDs: `R1` keeps `A→B` (and `B→A` since `C→A,A→B,B→C` imply `B→A`…);
> `R2` keeps `B→C` (and `C→B`).

Check each original FD using the **local** FDs `{A→B, B→A, B→C, C→B}`:

```text
A→B : A⁺(local) = {A,B,...} ⊇ {B}  ✓
B→C : B⁺(local) = {B, A, C}          ⊇ {C}  ✓
C→A : C⁺(local) = {C, B, A}          ⊇ {A}  ✓  (C→B→A via local FDs)
```

All three hold → **dependency-preserving** (and, since `B` is a key of R2 via
`B→C`, also lossless).

> *Counter-example (dependency LOST):* `R(A,B,C)`, `F = { AB→C, C→B }`, candidate
> keys `{A,B}` and `{A,C}`. BCNF forces splitting off `C→B`: `R1(C,B)`, `R2(A,C)`.
> Now `AB→C` is **not** checkable on either single table (no table holds A, B, C
> together). So this BCNF decomposition is **lossless but NOT
> dependency-preserving** — the canonical illustration of the 3NF-vs-BCNF trade-off,
> continued in §5.11B.

---

## 5.11B Worked "Normalize this relation to BCNF" — every step

This is the capstone worked example: take one relation and drive it up the ladder,
showing why BCNF may **lose** a dependency that 3NF keeps.

> *Given:* `R(A,B,C)` with `F = { AB→C, C→B }`.
> (Read it as: `(student, course)→instructor` and `instructor→course` — the classic
> "one instructor teaches one course, a course has many instructors" case.)

**Step 1 — candidate keys.**

```text
AB⁺ = {A,B} → AB→C → {A,B,C} = ALL      → {A,B} is a super key (and minimal) → key
AC⁺ = {A,C} → C→B  → {A,B,C} = ALL      → {A,C} is a super key (and minimal) → key
A⁺  = {A} (nothing fires) ≠ ALL; B⁺={B}; C⁺={C,B}≠ALL → no single-attr key
```

**Candidate keys = {A,B} and {A,C}.** Prime = {A,B,C} (all three). Non-prime = ∅.

**Step 2 — 2NF?** Non-prime set is empty, so there is **no** partial dependency
possible → **2NF holds** (trivially).

**Step 3 — 3NF?** Test each FD: "LHS a super key OR every RHS attr prime".

```text
AB→C : AB is a super key ✓
C→B  : C is NOT a super key, BUT B is PRIME (B ∈ key {A,B}) ✓  ← 3NF escape hatch
```

Both pass → **R is in 3NF.**

**Step 4 — BCNF?** Test each FD: "LHS must be a super key" (no prime escape).

```text
AB→C : AB is a super key ✓
C→B  : C is NOT a super key (C⁺={C,B}≠ALL) ✗   ← BCNF VIOLATION
```

So **R is 3NF but not BCNF** — the violating FD is `C→B`.

**Step 5 — BCNF decomposition** on the violating `C→B`. Split on `C⁺ = {C,B}`:

```text
R1 = (C⁺)          = R1(C, B)          -- holds C→B
R2 = R − (C⁺ − C)  = R(A,B,C) − {B}    = R2(A, C)
```

- **Lossless?** `R1∩R2 = {C}`, and `C→B` makes `C` a key of `R1(C,B)` → **lossless** ✓
- **Dependency-preserving?** Projected FDs: R1 gives `C→B`; R2 gives nothing useful
  about `AB→C`. The original FD **`AB→C` is now un-checkable on any single table**
  (no table has A, B, C together) → **dependency preservation LOST** ✗

> **The trade-off, made concrete:**
> - Stay at **3NF** `R(A,B,C)` → keep **both** `AB→C` and `C→B` checkable, but
>   tolerate the small redundancy that `C→B` causes.
> - Go to **BCNF** `{R1(C,B), R2(A,C)}` → zero anomaly from `C→B`, but you can no
>   longer enforce `AB→C` without a **join** (or a costly assertion/trigger).
>
> This is *exactly* why the standard advice is **"decompose to 3NF (Bernstein
> synthesis, always lossless + dependency-preserving); go to BCNF only when the
> leftover redundancy is genuinely unacceptable."**

> **Exam phrasing to memorize:** *"Give a relation that is in 3NF but not in
> BCNF."* → `R(A,B,C)`, `AB→C`, `C→B`. *"Show its BCNF decomposition loses a
> dependency."* → split on `C→B` into `(C,B)` and `(A,C)`; `AB→C` is lost.

---

## 5.12 Higher Normal Forms — 4NF (MVD) and 5NF

### Multivalued dependency & 4NF

A **multivalued dependency (MVD)** `X ↠ Y` exists when, for each X, a **set** of Y
values exists **independently** of the other attributes. Two independent
multivalued facts in one table cause a **Cartesian explosion**.

![4NF: an employee with independent multivalued skills and hobbies forces rows to multiply; split into EMP_SKILL and EMP_HOBBY.](images/55_mvd_4nf.png)

> *Example:* `EMP(emp, skill, hobby)` where skills and hobbies are **independent**.
> Storing both forces every skill to pair with every hobby (rows multiply).
> **4NF** = BCNF + **no non-trivial MVD**. *Fix:* split into `EMP_SKILL(emp,
> skill)` and `EMP_HOBBY(emp, hobby)`.

### Fifth Normal Form (5NF / PJNF)

**5NF** (Project-Join NF) deals with **join dependencies**: a table is in 5NF if it
cannot be decomposed into smaller tables and rejoined without loss **except** via
its candidate keys. It addresses rare cases where a relation must be split into
**three or more** parts. Mostly theoretical; know the name and the one-line idea.

---

## 5.13 How to Normalize — The Procedure

![Flowchart for normalization: check atomic (1NF), partial dependency (2NF), transitive dependency (3NF), every determinant a super key (BCNF); each failure triggers a decomposition.](images/56_fc_normalization.png)

**The repeatable procedure:**

1. Make all values **atomic** → 1NF.
2. Find **candidate keys** (via closures), mark **prime/non-prime** attributes.
3. Remove **partial** dependencies → 2NF.
4. Remove **transitive** dependencies → 3NF.
5. Check **every determinant is a super key**; if not, decompose → BCNF.
6. (If needed) remove **MVDs** → 4NF; **join dependencies** → 5NF.

### The two decomposition algorithms (know which guarantees what)

| Algorithm | Produces | Guarantees |
|-----------|----------|------------|
| **3NF synthesis** (Bernstein) | a 3NF schema | **lossless join + dependency preserving** (always) |
| **BCNF decomposition** (analysis) | a BCNF schema | **lossless join** always; dependency preservation **not** guaranteed |

- **3NF synthesis:** compute a **minimal cover**; create one table per FD group
  (group FDs by identical left side, each group → table `XY₁Y₂…`); if no table
  contains a candidate key, add one table that **is** a candidate key. Done.
- **BCNF decomposition:** while some table has a violating FD `X → Y` (X not a super
  key), split it into `(X⁺)` and `(R − (X⁺ − X))`; repeat. Always lossless, but may
  drop a dependency.

> **Exam one-liner:** *"Which decomposition guarantees dependency preservation?"* →
> **3NF (synthesis)**, not BCNF.

### Dry run — "find the highest normal form" (the classic exam question)

> *Given:* `R(A,B,C,D)`, FDs `AB → C`, `C → D`, candidate key `{A,B}`.
> Prime = {A,B}; non-prime = {C,D}.
> - **1NF?** assume atomic → yes.
> - **2NF?** any non-prime on *part* of `{A,B}`? `AB→C` uses the whole key; no
>   partial dep → **2NF holds**.
> - **3NF?** `C → D`: C is **not** a super key (`C⁺ = {C,D}` ≠ all), and D is
>   **non-prime** → **transitive dependency** → **fails 3NF**.
> - **Highest NF = 2NF.** *Fix:* split into `R1(A,B,C)` and `R2(C,D)`.

> **Exam technique:** always (1) list candidate keys via closure, (2) mark
> prime/non-prime, (3) test each FD against 2NF→3NF→BCNF in order. The **highest**
> normal form is the last one that holds before the first failure.

---

## 5.14 Real-World & Backend Perspectives

- **Backend:** OLTP schemas are usually normalized to **3NF** to avoid update
  anomalies in transactional data (orders, payments, users).
- **Denormalization (deliberate):** read-heavy systems and **data warehouses**
  (Module 11) often *denormalize* (star schema) to avoid expensive joins — trading
  redundancy for read speed. You normalize for **writes**, denormalize for
  **reads**.
- **Migrations:** splitting a table to reach a higher normal form is a routine (but
  careful) schema migration; the lossless-join property is what guarantees you
  don't corrupt data.

---

## 5.15 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Confusing **partial** (depends on *part of a key*, 2NF) with **transitive**
  (non-prime → non-prime, 3NF).
- Forgetting that a **single-attribute key** relation is automatically **2NF**.
- Thinking BCNF is always achievable with dependency preservation (it's **not**).
- "Proving" an FD from sample rows (data can only *disprove* an FD).
- Forgetting to find **all** candidate keys before classifying prime/non-prime.
- Assuming a lossless decomposition is automatically dependency-preserving.

**Edge cases**
- A relation with **no non-trivial FDs** (only the full key determines things) is
  already in **BCNF**.
- A relation where **every attribute is prime** is automatically in **3NF**.
- 2NF/partial-dependency analysis is irrelevant when keys are single-attribute.
- **Every binary (two-attribute) relation is always in BCNF** — a classic
  one-liner exam fact (with only two attributes, any non-trivial FD's determinant
  is necessarily a super key).

**Tradeoffs**

| More normalization | Less normalization (denormalized) |
|--------------------|-----------------------------------|
| Less redundancy, fewer anomalies | Faster reads (fewer joins) |
| More tables, more joins | Redundancy + update anomalies return |
| Great for OLTP / writes | Great for OLAP / read-heavy reporting |

---

## 5.16 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** compute `X⁺`; find **all candidate keys**;
prime/non-prime; **identify the highest normal form**; partial vs transitive;
**3NF vs BCNF**; **lossless join** test; **dependency preservation**; minimal
cover; MVD/4NF.

**Interview:** "What is normalization and why?" (anomalies); "Difference between
3NF and BCNF?" (determinant must be super key; BCNF may lose dependency
preservation); "When would you denormalize?" (read-heavy/reporting); "What's a
partial dependency?".

**Coding/practical:**
- Take a wide spreadsheet-style table and decompose it to 3NF by hand, then write
  the `CREATE TABLE`s with the right primary/foreign keys.
- Verify your split is lossless by joining the pieces back and comparing.

---

## 5.17 Concept Checks & MCQs

1. `A→B, B→C`. Is `A→C` derivable? → **Yes** (transitivity).
2. `R(A,B,C,D)`, `A→B, B→C, C→D`. `A⁺` = ? → **{A,B,C,D}** (A is a key).
3. Partial dependency breaks which NF? → **2NF**.
4. Transitive dependency breaks which NF? → **3NF**.
5. BCNF requires every determinant to be a ___ → **super key**.
6. Which is stricter, 3NF or BCNF? → **BCNF**.
7. Lossless test for R→R1,R2: common attributes must be a ___ of one piece → **key**.
8. Which property does BCNF NOT always guarantee? → **dependency preservation**.
9. A relation with a single-attribute key is always in ___ → **2NF**.
10. MVD is removed by which NF? → **4NF**.
11. Which decomposition algorithm guarantees dependency preservation? → **3NF
    synthesis** (BCNF decomposition does not).
12. Every **binary** (2-attribute) relation is always in ___ → **BCNF**.
13. `{B,C,E}` contains key `{B,E}` — is it a candidate key? → **No** (super key,
    not minimal).
14. Two FD sets are equivalent iff ___ → **each implies the other** (every FD of one
    is derivable from the other, checked via closures).
15. Lossless decomposition into **3+** tables is tested with the ___ algorithm →
    **chase / tableau (matrix)**.
16. Given candidate key `{A,B}` in `R(A,B,C,D)`, number of super keys = ___ →
    **2^(4−2) = 4** (every super key must contain both A and B).
17. In `R(A,B,C,D,E,F)` with `A→B, B→C, CD→E, A→D, E→F`, is `A` a candidate key? →
    **Yes** — `A⁺` = all six attributes (see §5.11A(a)).
18. To make a right-hand side single-attribute is which minimal-cover step? →
    **Step 1 (singleton RHS)**.
19. In `AB→C`, if `B⁺ = {B,C}`, is `A` extraneous on the LHS? → **Yes** (you can
    derive C from B alone, so `AB→C` reduces to `B→C`).
20. A BCNF decomposition of `R(A,B,C)` with `AB→C, C→B` produces which two tables? →
    **`(C,B)` and `(A,C)`** (splitting on the violating `C→B`).
21. That BCNF split loses which dependency? → **`AB→C`** (not checkable on a single
    table).
22. To test lossless join for a decomposition into **3 tables**, which method? →
    **tableau / chase (matrix)** — lossless iff some row becomes all-distinguished.
23. Prime attributes of `R(A,B,C)` with keys `{A,B}` and `{A,C}` = ___ → **{A,B,C}**
    (union of all candidate keys → all attributes prime → automatically 3NF).
24. Dependency preservation is tested by ___ → checking `(F1∪…∪Fk)⁺ = F⁺`, i.e. every
    original FD `X→Y` still has **`Y ⊆ X⁺` using only the projected (local) FDs**.

**True/False**
- Every relation in BCNF is in 3NF. → **True** (BCNF is stricter).
- 3NF is always lossless *and* dependency-preserving. → **True**.
- BCNF is always dependency-preserving. → **False**.
- You can prove an FD holds by looking at sample data. → **False** (only disprove).

**Numerical (do it):**
> `R(A,B,C,D,E)`, FDs `A→B, BC→D, E→C, D→A`. Find **all** candidate keys.
> Hint: `E` appears only on the left of `E→C` and on no right side → `E` must be in
> **every** key. `E⁺ = {E,C}` (not all), so pair E with one "entry" attribute.
> *Answer: the candidate keys are `{A,E}`, `{B,E}`, and `{D,E}` — all size 2.*
> Check: `(A,E)⁺`: A→B, E→C, then BC→D, D→A → all ✓. Similarly `(B,E)` and `(D,E)`.
> Note `{B,C,E}` is a **super key but NOT a candidate key** — its subset `{B,E}` is
> already a key, so it isn't minimal.

---

## 5.18 One-Page Revision Sheet

```
WHY: redundancy -> INSERT / UPDATE / DELETE anomalies. Normalize = one fact, one place.

FD  X->Y: rows equal on X must be equal on Y. (schema rule, not from sample data)
  types: trivial(Y⊆X) | non-trivial | full | PARTIAL(part of key->breaks 2NF)
         | TRANSITIVE(non-prime->non-prime->breaks 3NF)

ARMSTRONG: Reflexivity, Augmentation, Transitivity (primary);
           Union, Decomposition, Pseudo-transitivity (derived). sound+complete.

CLOSURE X+: all attrs X determines. X super key iff X+ = all attrs.
  candidate key = minimal X with X+=all. Attrs only-on-LHS / in-no-FD MUST be in every key.

MINIMAL COVER (3 steps): singleton RHS | remove extraneous LHS attr | remove redundant FD.

NORMAL FORMS (each includes lower):
  1NF  atomic values
  2NF  1NF + no PARTIAL dep (non-prime on part of composite key)
       (single-attr key => automatically 2NF)
  3NF  2NF + no TRANSITIVE dep; test: for X->Y, X is super key OR Y is prime
  BCNF 3NF + EVERY determinant is a SUPER KEY (no "Y prime" escape)
  4NF  BCNF + no MVD (independent multivalued facts)
  5NF  no join dependency

DECOMPOSITION:
  LOSSLESS (mandatory): (R1∩R2)->R1 OR (R1∩R2)->R2  (common attrs = key of a piece)
  DEPENDENCY PRESERVATION (desirable): all FDs checkable on single tables.
  3NF: lossless + dep-preserving (always). BCNF: lossless always, dep-pres NOT always.

ALGORITHMS: 3NF = SYNTHESIS (Bernstein, minimal cover -> table per FD group + key table;
  lossless + dep-preserving). BCNF = DECOMPOSITION/analysis (split on violating X->Y into
  X+ and R-(X+-X); lossless, dep-pres NOT guaranteed).
FACTS: every binary (2-attr) relation is in BCNF. all-prime relation is in 3NF.
ALL candidate keys: essential attrs(only-LHS/no-FD) MUST be in every key; add middle attrs minimally.
FD-SET EQUIVALENCE: F ≡ G iff each implies the other (check every FD via closures).
LOSSLESS for 3+ tables: chase/tableau (matrix) algorithm.
  tableau: rows=pieces, cols=attrs; a=has-attr, b=not; apply FDs (equate RHS on matching LHS);
  LOSSLESS iff some ROW becomes ALL-a.
DEP-PRESERVATION: (F1∪...∪Fk)+ = F+  i.e. every X->Y has Y⊆X+ using only PROJECTED/local FDs.
3NF-not-BCNF canonical: R(A,B,C), AB->C, C->B. keys {A,B},{A,C}. C->B ok in 3NF (B prime)
  but fails BCNF (C not superkey). BCNF split (C,B)+(A,C) => LOSES AB->C (dep-pres lost).
#SUPERKEYS given a key: every super key must CONTAIN a candidate key (count subsets that do).

HIGHEST NF method: find candidate keys -> mark prime/non-prime -> test 2NF,3NF,BCNF in order.
DENORMALIZE for read-heavy/OLAP; normalize for write-heavy/OLTP.
```

### Flash cards

| Front | Back |
|-------|------|
| Partial dependency breaks? | 2NF |
| Transitive dependency breaks? | 3NF |
| BCNF condition? | every determinant is a super key |
| 3NF vs BCNF trade-off? | BCNF stricter but may lose dependency preservation |
| Lossless test? | common attrs are a key of one decomposed table |
| Closure X⁺ super-key check? | X⁺ = all attributes |
| Single-attribute key relation is in? | 2NF automatically |
| MVD removed by? | 4NF |
| Can sample data prove an FD? | No — only disprove |
| Minimal cover steps? | singleton RHS, remove extra LHS, remove redundant FD |

### Spaced repetition
- **24-hour:** compute 5 closures + find candidate keys; redo MCQs.
- **7-day:** classify 5 relations to their highest normal form, with reasons.
- **30-day:** decompose 3 relations to BCNF, prove each split lossless, and note
  any lost dependency.

---

## 5.19 Summary

Normalization removes **redundancy** and its three **anomalies** (insert, update,
delete) by decomposing tables using **functional dependencies**. We learned to
reason about FDs with **Armstrong's axioms**, compute **attribute closure (X⁺)** —
the master tool for finding **candidate keys** and testing super keys — and reduce
FD sets to a **minimal cover**. We climbed the **normal-form ladder**: **1NF**
(atomic), **2NF** (no partial dependency), **3NF** (no transitive dependency),
**BCNF** (every determinant a super key), **4NF** (no MVD), **5NF** (no join
dependency). We saw the decisive trade-off — **lossless join is mandatory,
dependency preservation is desirable; 3NF gives both, BCNF only the former** — and
a repeatable procedure for finding a relation's **highest normal form**.

This module completes the **design** half of DBMS (ER → relational → SQL →
normalization). Next, **Module 6 — Storage & File Organization** drops down to how
these tables physically live on disk, setting up **indexing** (Module 7) which
makes the queries from Module 4 fast.

> **You have mastered this module when** you can: compute any closure and list all
> candidate keys; mark prime/non-prime; identify the highest normal form of a
> relation with reasons; explain partial vs transitive dependency and 3NF vs BCNF;
> and test a decomposition for lossless join and dependency preservation — all
> without notes.
