---
title: "Module 3 — Relational Model, Keys, Integrity & Relational Algebra"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — Relational Model, Keys, Integrity & Relational Algebra

> **Where this module sits.**
> In Module 2 we *designed* a database as a picture (ER) and mapped it to tables.
> Now we make those tables **mathematically precise**. The relational model is the
> theory underneath every SQL database on earth. Relational **algebra** is the
> secret language your queries are compiled into — when you understand it, SQL
> stops being magic and query optimization (Module 8) becomes obvious. This module
> is the theoretical heart of the whole subject and one of the **highest-scoring**
> areas in SEBI/GATE.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★★★★★   | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** definitions of **degree &
cardinality**; **super / candidate / primary / foreign key** differences;
**prime vs non-prime** attribute; **entity & referential integrity**; the
**relational algebra operators** and what each outputs; **which operators are
fundamental vs derived**; **natural join** result and tuple counts;
**division** ("for all" queries); **TRC vs DRC**; and the fact that algebra and
calculus have **equal expressive power**.

---

## 3.1 The Relational Model — Basics

### Motivation & first principles

Codd's 1970 idea was radical in its simplicity: **store all data as
mathematical relations (tables), and query them with operations from set
theory and logic.** No pointers, no navigation — just tables and operators that
take tables in and give tables out. That "tables in → table out" property is
called **closure**, and it is *why* you can nest queries.

### Definitions (learn this vocabulary cold — it is tested directly)

![Anatomy of a relation: columns are attributes, rows are tuples, degree = number of columns, cardinality = number of rows, each column draws from a domain.](images/25_relation_anatomy.png)

- **Relation:** a table. Formally, a subset of the Cartesian product of domains.
- **Tuple:** a row (a single record).
- **Attribute:** a column (a named field).
- **Domain:** the set of allowed atomic values for an attribute (e.g. `cgpa ∈
  [0.0, 10.0]`). Domains must be **atomic** (indivisible) — this is the **1NF**
  requirement (Module 5).
- **Degree (arity):** the **number of attributes (columns)**.
- **Cardinality:** the **number of tuples (rows)**.
- **Relation schema:** the design — `STUDENT(roll_no, name, cgpa)`.
- **Relation instance / state:** the actual set of tuples at a moment.
- **Relational database schema:** the set of all relation schemas together.

> **Exam trap (memorize):** **Degree = columns, Cardinality = rows.** Students
> swap these constantly. *Degree* sounds like "degree of complexity = how many
> attributes"; *cardinality* is "how many things (rows)".

### Properties of relations (each one is a possible MCQ)

1. **No duplicate tuples** — a relation is a *set*, so every row is unique.
2. **Tuples are unordered** — there is no "first" row.
3. **Attributes are unordered** — columns are referenced by name, not position.
4. **All values are atomic** — no lists/sets inside a cell (1NF).
5. **Each attribute has a distinct name** within a relation.

> **Why "no duplicates & unordered" matters:** it is exactly why `SELECT` can
> return rows in any order unless you say `ORDER BY`, and why `π` (projection)
> automatically removes duplicates. SQL relaxes the "set" rule to a **multiset
> (bag)** — it *can* keep duplicates unless you write `DISTINCT`. (A classic
> algebra-vs-SQL difference.)

### Concept check

> *Q:* A relation has 6 columns and 100 rows. Its degree and cardinality?
> *A:* **Degree = 6, cardinality = 100.**

---

## 3.2 Keys — The Complete Picture

Keys are how we *uniquely identify* rows and *link* tables. This is one of the
most frequently tested topics in the entire syllabus.

![Keys hierarchy: super key ⊇ candidate key (minimal) ⊇ primary key (the chosen one). Alternate keys are unchosen candidates; foreign keys reference another table's PK.](images/26_keys_hierarchy.png)

### The hierarchy (think nested boxes)

| Key | Definition | Example on `STUDENT(roll_no, email, name, dob)` |
|-----|------------|--------------------------------------------------|
| **Super key** | *Any* set of attributes that uniquely identifies a tuple | `{roll_no}`, `{roll_no, name}`, `{email, dob}` … |
| **Candidate key** | A **minimal** super key (remove any attribute and it stops being unique) | `{roll_no}`, `{email}` |
| **Primary key** | The **one** candidate key chosen as the main identifier; **unique + NOT NULL** | `{roll_no}` |
| **Alternate key** | A candidate key **not** chosen as primary | `{email}` |
| **Foreign key** | An attribute that **references another relation's primary key** | `dept_id` in `EMPLOYEE` → `DEPT.dept_id` |
| **Composite key** | A key made of **two or more** attributes | `{roll_no, course_id}` in `ENROLLS` |
| **Surrogate key** | An artificial, system-generated id (e.g. auto-increment) | `id SERIAL` |

> **Super key vs candidate key (the #1 confusion):** every candidate key is a
> super key, but a super key is a candidate key **only if it is minimal**.
> `{roll_no, name}` is a super key but **not** a candidate key (because `roll_no`
> alone already works — `name` is redundant).

### PRIMARY KEY vs UNIQUE constraint (frequent SEBI/interview question)

Both enforce uniqueness, but they are **not** the same:

| | **PRIMARY KEY** | **UNIQUE** |
|---|-----------------|------------|
| Uniqueness | yes | yes |
| NULLs allowed? | **No** (entity integrity) | **Yes** (usually one NULL, or several depending on DBMS) |
| How many per table? | **exactly one** | **many** |
| Role | the row's main identity | an alternate-key enforcement |

> So a primary key = **UNIQUE + NOT NULL + only one per table**. The other
> candidate keys are typically declared with a `UNIQUE` constraint (they are the
> **alternate keys**).

### Prime vs Non-prime attributes (heavily tested in normalization)

- **Prime attribute:** an attribute that is **part of *some* candidate key**.
- **Non-prime attribute:** an attribute that is **part of *no* candidate key**.

> Example: if candidate keys are `{roll_no}` and `{email}`, then `roll_no` and
> `email` are **prime**; `name` and `dob` are **non-prime**. You will need this
> exact definition for 2NF/3NF in Module 5.

### How many super keys? (a favourite GATE numerical)

A super key is *any* attribute set that **contains a candidate key**. So count the
subsets that include at least one full candidate key.

**Case 1 — exactly ONE candidate key of 1 attribute, n attributes total:**
number of super keys = **2^(n−1)** (the key attribute must be present; each of the
other n−1 attributes is independently in or out).

> *Worked example:* `R(A, B, C, D)` with the single candidate key `{A}`. Super
> keys = all subsets that contain `A` = `2^(4−1) = 8`.

**Case 2 — TWO disjoint candidate keys, each 1 attribute (e.g. `{A}` and `{B}`):**
count subsets containing `A` **OR** `B`, by inclusion–exclusion:
`2^(n−1) + 2^(n−1) − 2^(n−2) = 3 · 2^(n−2)`.

> *Worked example:* `R(A, B, C, D)` with candidate keys `{A}` and `{B}`. Super
> keys = `3 · 2^(4−2) = 3 · 4 = 12`.

**Case 3 — a COMPOSITE candidate key** (e.g. the only candidate key is `{A,B}` in
`R(A,B,C,D)`): a super key is any subset that **contains** `{A,B}`. Both A and B
must be present; the remaining `n − 2` attributes are each optional → super keys =
`2^(n−2) = 2^2 = 4` (namely `AB, ABC, ABD, ABCD`).

> **General principle (use this, not a memorized formula):** the number of super
> keys = the number of attribute subsets that **contain at least one candidate
> key**. For one key it's a clean power of two; for multiple/overlapping keys, use
> inclusion–exclusion over "contains key₁ OR key₂ OR …".

> **⚠️ Trap (the reason this is tested):** the simple `2^(n−1)` formula is valid
> **only when there is exactly one single-attribute candidate key.** The moment a
> relation has a second candidate key (like our `STUDENT` with both `{roll_no}`
> and `{email}`), you must use inclusion–exclusion. Always count "subsets
> containing *some* candidate key", never blindly apply `2^(n−1)`.

### Finding candidate keys (the algorithm you'll reuse in Module 5)

When a relation comes with **functional dependencies** (FDs — Module 5), you find
candidate keys systematically using **attribute closure**. The flow below is the
exact procedure; we go deep on closure in Module 5, but the *shape* of the
algorithm is worth seeing now.

![Flowchart for finding candidate keys: split attributes by where they appear in FDs, find essential attributes that must be in every key, take their closure, then extend minimally until the closure covers all attributes.](images/33_fc_candidate_keys.png)

**The intuition:** attributes that appear **only on the left** of FDs (or in no FD
at all) **must** be in every candidate key — nothing can determine them, so they
can't be derived. Start there, take the closure, and add the fewest extra
attributes needed to reach *all* attributes.

### MCQs

1. A minimal super key is a ___ → **candidate key**.
2. A primary key cannot be ___ → **NULL** (entity integrity).
3. `{roll_no, name}` where `roll_no` alone is unique — is it a candidate key? →
   **No** (not minimal; it's a super key only).
4. An attribute in some candidate key is called ___ → **prime**.

---

## 3.3 Integrity Constraints — Rules That Keep Data Valid

Constraints are conditions the DBMS **enforces automatically** so the database can
never reach an invalid state. This is one of the core advantages of a DBMS over
files (Module 1).

![Integrity constraints: domain (valid values), key (uniqueness), entity integrity (PK not NULL), referential integrity (FK must match an existing PK).](images/27_integrity_constraints.png)

| Constraint | Rule | Violation example |
|------------|------|-------------------|
| **Domain** | each value comes from the attribute's domain/type | putting `'abc'` in an `INT age` column |
| **Key** | candidate-key values are **unique** across all tuples | two students with the same `roll_no` |
| **Entity integrity** | the **primary key is never NULL** (and unique) | a row with `roll_no = NULL` |
| **Referential integrity** | a **foreign key** value must **match an existing primary-key** value in the referenced table, **or be NULL** | `EMPLOYEE.dept_id = 99` when no `DEPT` 99 exists |

### Referential integrity in depth (the one with the arrow)

A foreign key creates a **parent → child** link (e.g. `DEPT` is parent,
`EMPLOYEE` is child). The DBMS protects this link on three operations:

- **Insert/Update a child** with a `dept_id` that has no parent → **rejected**.
- **Delete/Update a parent** that still has children → controlled by a
  **referential action**:
  - `RESTRICT` / `NO ACTION` — block it.
  - `CASCADE` — delete/update the children too.
  - `SET NULL` — set the children's FK to NULL.
  - `SET DEFAULT` — set the children's FK to a default value.

> **Interview soundbite:** "A foreign key with `ON DELETE CASCADE` means deleting a
> parent automatically cleans up its children — convenient, but dangerous if you
> didn't expect a chain delete." This shows practical awareness backends care
> about.

> **Exam nuggets:** *Entity integrity = PK not NULL.* *Referential integrity = FK
> references an existing PK (or is NULL).* These two phrasings appear verbatim in
> SEBI/RBI papers.

### Concept check

> *Q:* Why can a foreign key be NULL but a primary key cannot?
> *A:* A NULL FK simply means "this row isn't linked to a parent yet" (optional
> relationship). A NULL PK would mean the row has no identity — forbidden by
> **entity integrity**.

### NULL and three-valued logic (a guaranteed gotcha)

`NULL` means "**unknown / not applicable / missing**" — it is **not** zero and
**not** an empty string. Because a value may be unknown, SQL logic has **three**
truth values: **TRUE, FALSE, UNKNOWN**.

- Any comparison with NULL yields **UNKNOWN**: `NULL = NULL` → **UNKNOWN** (not
  TRUE!), `NULL > 5` → UNKNOWN.
- A `WHERE` clause keeps a row only when the predicate is **TRUE** — so rows where
  the condition is UNKNOWN are **dropped**.
- To test for NULL you must use `IS NULL` / `IS NOT NULL`, never `= NULL`.
- **Aggregates ignore NULLs**: `COUNT(col)` skips NULLs (but `COUNT(*)` counts all
  rows); `AVG`/`SUM` ignore NULLs too.

| A | B | A AND B | A OR B |
|---|---|---------|--------|
| TRUE | UNKNOWN | UNKNOWN | TRUE |
| FALSE | UNKNOWN | FALSE | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

> **Exam/interview nugget:** `SELECT * FROM T WHERE age = NULL;` returns **zero
> rows** (the predicate is UNKNOWN for every row). The correct query is
> `WHERE age IS NULL`. This trips up nearly everyone once.

---

## 3.4 Relational Algebra — The Operators

Relational algebra is a **procedural** query language: you describe *a sequence of
operations*. Each operator takes one or two relations and returns a relation
(closure), so operations chain into expressions.

### The 6 FUNDAMENTAL operators (everything else is built from these)

| Op | Name | Picks / does | SQL analogue |
|----|------|--------------|--------------|
| **σ** (sigma) | **Selection** | filters **rows** by a predicate | `WHERE` |
| **π** (pi) | **Projection** | keeps chosen **columns** (and de-dups) | `SELECT cols` |
| **ρ** (rho) | **Rename** | renames a relation/attributes | `AS` |
| **∪** | **Union** | rows in A **or** B | `UNION` |
| **−** | **Set difference** | rows in A **but not** B | `EXCEPT` |
| **×** | **Cartesian product** | every row of A paired with every row of B | `CROSS JOIN` |

> **Exam favourite:** "Which of these is NOT a fundamental/primitive operator?"
> The fundamentals are **σ, π, ρ, ∪, −, ×**. **Intersection (∩), join (⋈), and
> division (÷) are DERIVED** (can be expressed using the six above).

### Selection (σ) and Projection (π)

![Selection σ keeps rows matching a predicate (horizontal filter); projection π keeps chosen columns and removes duplicates (vertical slice).](images/28_selection_projection.png)

- **σ_predicate(R):** keeps the rows where the predicate is true.
  `σ_cgpa > 8.0 (STUDENT)`.
- **π_attrlist(R):** keeps only those columns, **removing duplicate rows**.
  `π_name, cgpa (STUDENT)`.
- **Combine them:** `π_name ( σ_cgpa > 8.0 (STUDENT) )` = "names of students with
  cgpa above 8".

> **The classic π trap:** projection **removes duplicates** (because a relation is
> a set). So `π_dept(EMPLOYEE)` returns each department **once**, even if 100
> employees share it. In SQL you'd need `SELECT DISTINCT dept`.

### Set operations (∪, ∩, −) and union compatibility

![Set operations on union-compatible relations: union (all, de-duplicated), intersection (common), difference A−B and B−A (not commutative).](images/29_set_operations.png)

To apply ∪, ∩, or −, the two relations must be **union-compatible**:

1. **same number of attributes (same degree)**, and
2. **corresponding attributes have the same (compatible) domains**.

- **A ∪ B** — tuples in A or B (duplicates removed).
- **A ∩ B** — tuples in both. *(Derived: `A ∩ B = A − (A − B)`.)*
- **A − B** — tuples in A not in B. **Not commutative:** `A − B ≠ B − A`.

### Cartesian product (×) and Joins

![Join types: natural/inner join keeps only matching rows; theta join adds any condition; equi join uses '='; outer joins keep unmatched rows padded with NULL.](images/30_join_types.png)

- **Cartesian product `A × B`:** pairs **every** row of A with **every** row of B.
  Degree = degree(A)+degree(B); rows = |A|×|B|. Rarely useful alone (it's huge and
  meaningless), but it's the **basis of all joins**.
- **Theta join `R ⋈θ S` = σθ(R × S):** cross product, then keep rows satisfying
  condition θ (any comparison: `<, >, =, ≠`).
- **Equi join:** a theta join whose θ uses only **equality (=)**.
- **Natural join `R ⋈ S`:** an equi join on **all attributes with the same name**,
  automatically, keeping only **one copy** of each shared attribute. The most-used
  join.
- **Outer joins** keep unmatched rows, padding the missing side with **NULL**.
  They are **derived** operators (a natural/theta join *unioned* with the
  unmatched rows padded by NULLs):
  - **Left outer** — all rows of the left relation.
  - **Right outer** — all rows of the right relation.
  - **Full outer** — all rows of both.

> **Natural join tuple-count trap (GATE):** the result size depends purely on how
> many rows match on the join attribute(s). It can be **0** (no matches), up to
> **|R|×|S|** (if every row shares the same join value). Never assume natural join
> keeps |R| rows — if a join value repeats on both sides, rows **multiply**. And
> if R and S share **no** common attribute names, natural join degenerates into a
> **Cartesian product** (every pair, since the "match on shared attributes"
> condition is vacuously true).

> **Outer-join NULL rule (which side gets NULLs):** the **kept** side's unmatched
> rows are padded with NULL in the **other** side's columns. *Left* outer keeps all
> left rows (right columns become NULL when unmatched); *right* keeps all right
> rows; *full* keeps both. In the image above, `EMP` row `dno=99` is kept by the
> left outer join with `dname = NULL`.

### Division (÷) — "for ALL" queries

![Division R ÷ S returns values in R associated with every value in S — e.g. students who take all required courses.](images/31_division.png)

**`R ÷ S`** answers *"find the X that are related to **every** Y in S."*

> *Example:* `TAKES(sid, course) ÷ ALL_COURSES(course)` = students who have taken
> **every** course in `ALL_COURSES`. A student who took only some is excluded.

> **Why it matters:** "for all" is the one thing SQL has no direct keyword for —
> you implement division with **double `NOT EXISTS`** (there is no Y in S such
> that the pair (X,Y) is *not* in R). This exact pattern is a common interview
> question.

**Dry run with actual rows (work it, then check):**

```
TAKES (R)              ALL_COURSES (S)
sid | course          course
S1  | C1               C1
S1  | C2               C2
S2  | C1
S3  | C1
S3  | C2

R ÷ S  →  { S1, S3 }
```

Why: S1 took {C1, C2} ⊇ {C1, C2} ✔; S3 took {C1, C2} ✔; **S2 took only {C1}**, so
it is **excluded** (it did not take *every* course in S). The result schema is
`schema(R) − schema(S) = {sid}`. *(Requirement: schema(S) ⊆ schema(R).)*

### Extended relational algebra (aggregation, grouping, assignment)

Pure algebra has no "average" or "group by" — but real queries need them, so the
algebra is **extended** with a few more operators (these appear in GATE and map
directly to SQL):

- **Generalized projection** — projection that allows **computed expressions**,
  e.g. `π_(name, salary*12) (EMP)` (yearly salary). Maps to `SELECT salary*12`.
- **Aggregation / grouping `ᵍℱ`** (often written `γ` or `ℱ`):
  `dept ℱ COUNT(eid), AVG(salary) (EMP)` = "group by dept, then count employees and
  average salary per group". This is exactly SQL's `GROUP BY` + aggregate
  functions (`COUNT, SUM, AVG, MIN, MAX`).
- **Assignment `←`** — name an intermediate result to build a query in steps:
  `Temp ← σ_cgpa>8 (STUDENT)`, then `π_name (Temp)`. Purely for readability.

> **Mapping to SQL:** σ → `WHERE`, generalized π → `SELECT expr`, ℱ → `GROUP BY` +
> aggregates, aggregate-with-condition → `HAVING`. You'll use all of these
> constantly in Module 4 (SQL).

### Building an expression and reading it as a tree

![Relational algebra expression tree: leaves are base tables, then join, then selection, then projection at the root; read bottom-up.](images/34_ra_expression_tree.png)

Any algebra query can be drawn as a **tree**: base tables are leaves; operators are
internal nodes; you evaluate **bottom-up**. The optimizer later rearranges this
tree (e.g. **pushing σ down** so filtering happens before the expensive join) —
that's the bridge to Module 8.

**Core equivalence (transformation) rules — these are why two queries can give the
same answer (GATE/SEBI test these):**

- **σ cascade:** `σ_a(σ_b(R)) = σ_b(σ_a(R)) = σ_{a AND b}(R)` (selections commute
  and combine).
- **σ push-down through join:** `σ_θ(R ⋈ S) = (σ_θ(R)) ⋈ S` when θ uses only R's
  attributes — *filter early, join late* (the #1 optimization).
- **π cascade:** `π_a(π_b(R)) = π_a(R)` when `a ⊆ b`.
- **Join commutativity & associativity:** `R ⋈ S = S ⋈ R`;
  `(R ⋈ S) ⋈ T = R ⋈ (S ⋈ T)` — lets the optimizer pick the cheapest join order.

> These rewrites preserve the result (the relations are equal) but change the
> **cost**. Module 8 uses them for cost-based optimization.

### Dry run (do it yourself, then check)

> *Query:* "Names of employees in the 'CSE' department."
> Tables: `EMPLOYEE(eid, name, dno)`, `DEPT(dno, dname)`.
> *Algebra:* `π_name ( σ_dname='CSE' ( EMPLOYEE ⋈ DEPT ) )`.
> *Steps:* (1) natural join on `dno` → combined rows; (2) σ keeps CSE rows;
> (3) π keeps the `name` column. ✔

---

## 3.5 Relational Calculus — Saying *What*, Not *How*

Relational **calculus** is a **declarative** (non-procedural) language: you
describe the *properties* of the result with logic, not the steps to compute it.

![Relational algebra (procedural, operators) vs calculus (declarative, predicate); tuple calculus ranges over rows, domain calculus over attribute values; equal expressive power.](images/32_algebra_vs_calculus.png)

### Tuple Relational Calculus (TRC)

Variables range over **tuples (rows)**. Form: `{ t | P(t) }` — "the set of tuples
`t` such that predicate `P(t)` is true."

```
{ t.name | STUDENT(t) AND t.cgpa > 8 }
   → names of students with cgpa above 8
```

Uses quantifiers **∃ (there exists)** and **∀ (for all)**.

### Domain Relational Calculus (DRC)

Variables range over **individual attribute values (domains)**. Form:
`{ <x1, x2, …> | P(x1, x2, …) }`.

```
{ <n, c> | ∃ r ( STUDENT(r, n, c) AND c > 8 ) }
   → (name, cgpa) pairs for cgpa above 8
```

**A "for all" (∀) example** (the division query, in calculus):

```
{ <s> | ∃ ... ( TAKES(s, _) ) AND
        ∀ c ( ALL_COURSES(c) → TAKES(s, c) ) }
   → students s who have taken EVERY course c in ALL_COURSES
```

Read it as: "for every course `c`, if it's in `ALL_COURSES`, then `s` took it." The
`∀ … →` pattern is exactly how calculus expresses what algebra does with **÷** and
SQL does with **double `NOT EXISTS`**.

### Two key theorems (exam gold)

1. **Equivalence:** relational algebra, TRC, and (safe) DRC all have the **same
   expressive power** (Codd's theorem). Anything one can express, the others can.
   This common power defines what "relationally complete" means.
2. **Safety:** a calculus expression must be **safe** — it must produce a
   **finite** result that depends only on values actually in the database
   (e.g. `{ t | NOT STUDENT(t) }` is *unsafe* — infinitely many tuples aren't
   students).

> **SQL's lineage:** SQL is closer to **calculus** (you declare *what* you want),
> but it is implemented by translating to **algebra** (the *how*) for execution.
> So you write calculus-style, the engine runs algebra. Best of both worlds.

> **Exam nuggets:** *Algebra = procedural. Calculus = declarative. TRC ranges over
> tuples; DRC over domain values. All three are equally powerful.* SQL ≈ calculus
> in style, algebra in execution.

---

## 3.6 Real-World & Backend Perspectives

- **Backend:** every `WHERE` is a σ, every `SELECT col` is a π, every `JOIN ... ON`
  is a theta/equi join, `UNION`/`EXCEPT` are the set ops. When you read an
  `EXPLAIN` plan, you are literally reading an algebra **expression tree** the
  optimizer chose.
- **Performance intuition:** "filter early, join late" — pushing σ below ⋈ is the
  single most important hand-optimization, and it comes straight from algebra
  equivalence rules.
- **Constraints in production:** foreign keys with the right `ON DELETE` action
  prevent orphaned rows; choosing a **surrogate key** vs a **natural key** is a
  real design debate (surrogates are stable; natural keys carry meaning).

---

## 3.7 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Swapping **degree** (columns) and **cardinality** (rows).
- Calling a non-minimal super key a "candidate key".
- Forgetting that **projection removes duplicates** (algebra is set-based).
- Thinking **natural join** always keeps |R| rows (it depends on matches; can
  multiply, or become a Cartesian product if no shared attribute).
- Listing **∩, ⋈, ÷** as *fundamental* operators — they are **derived**.
- Believing SQL = relational algebra exactly — SQL is a **multiset (bag)**, allows
  duplicates, and has NULL 3-valued logic.

**Edge cases**
- `A − B` is **not** the same as `B − A` (difference isn't commutative); union and
  intersection **are** commutative.
- Natural join with **no common attributes** = Cartesian product.
- A foreign key may reference its **own** table (recursive, e.g. `mgr_id`).
- `NULL` complicates everything: `NULL = NULL` is **unknown**, not true.

**Tradeoffs**

| Relational model strength | Limitation |
|---------------------------|------------|
| Simple, math-backed, closure enables nesting | Flat tables don't fit hierarchical/graph data as naturally (Module 11 NoSQL) |
| Declarative SQL → optimizer picks fast plans | Abstraction can hide expensive operations (accidental Cartesian products) |
| Strong integrity guarantees | Constraints add write-time overhead |

---

## 3.8 Exam, Interview & Coding Perspectives

**Competitive-exam (SEBI/RBI/GATE):** degree/cardinality; key definitions &
counting super keys (`2^(n−1)`); prime/non-prime; entity vs referential
integrity; fundamental vs derived operators; output of σ/π/⋈/÷; natural-join
tuple counts; algebra vs calculus & their equivalence; TRC vs DRC.

**Interview:** "Explain the difference between WHERE and a JOIN condition" (σ vs
join); "How would you express *find customers who bought every product*?"
(division → double `NOT EXISTS`); "What's the difference between a candidate key
and a primary key?"; "What does `ON DELETE CASCADE` do?".

**Coding/practical (PostgreSQL):**
- Write `π_name(σ_cgpa>8(STUDENT))` as `SELECT DISTINCT name FROM student WHERE
  cgpa > 8;` and observe `DISTINCT` mimicking projection's de-dup.
- Implement division with double `NOT EXISTS` and test it.
- Add a foreign key with `ON DELETE CASCADE`, delete a parent, watch children go.

---

## 3.9 Concept Checks & MCQs

1. Degree of `R(A,B,C,D,E)` → **5**.
2. Number of super keys of `R(A,B,C)` with candidate key `{A}` → **2^2 = 4**.
3. Which is NOT fundamental: σ, π, ⋈, − → **⋈ (join is derived)**.
4. Entity integrity says ___ → **primary key is not NULL**.
5. Referential integrity says ___ → **FK matches an existing PK, or is NULL**.
6. `π` in relational algebra automatically ___ → **removes duplicates**.
7. Natural join with no common attribute name becomes ___ → **Cartesian product**.
8. "Find students who took ALL courses" uses which operator → **division (÷)**.
9. TRC variables range over ___; DRC over ___ → **tuples** / **domain values**.
10. Algebra is ___ and calculus is ___ → **procedural** / **declarative**.
11. `SELECT * FROM T WHERE age = NULL;` returns ___ rows → **zero** (use `IS NULL`).
12. `NULL = NULL` evaluates to ___ → **UNKNOWN** (not TRUE).
13. PRIMARY KEY = UNIQUE + ___ + only one per table → **NOT NULL**.
14. Super keys of `R(A,B,C,D)` with candidate keys `{A}` and `{B}` → **3·2² = 12**.
15. SQL `GROUP BY` + `COUNT` corresponds to which extended-RA operator → **aggregation (ℱ/γ)**.

**True/False**
- `A − B = B − A`. → **False**.
- Every super key is a candidate key. → **False** (only minimal ones).
- Algebra and calculus have equal expressive power. → **True**.
- Projection keeps duplicate rows. → **False** (it removes them).

**Scenario**
> *"List the distinct cities of customers who have NOT placed any order."*
> *Algebra sketch:* `π_city(CUSTOMER) − π_city(CUSTOMER ⋈ ORDER)`
> (all customer cities, minus cities of customers who ordered). Uses **difference**
> and a **join**.

---

## 3.10 One-Page Revision Sheet

```
RELATION basics: relation=table, tuple=row, attribute=column, domain=allowed values
  DEGREE = # columns        CARDINALITY = # rows   (don't swap!)
  schema = design; instance = current rows
  Properties: no dup tuples, unordered rows, unordered cols, atomic values (1NF)
  (SQL relaxes to MULTISET/bag — allows dups unless DISTINCT)

KEYS (nested): SUPER >= CANDIDATE(minimal) ; PRIMARY = chosen candidate (unique+NOT NULL)
  ALTERNATE = unchosen candidate ; FOREIGN = ref another PK ; COMPOSITE = multi-attr
  PRIME attr = in SOME candidate key ; NON-PRIME = in NONE
  PK vs UNIQUE: PK = UNIQUE + NOT NULL + one per table; UNIQUE allows NULL & many
  # super keys: ONE 1-attr cand key -> 2^(n-1) ; TWO disjoint 1-attr keys -> 3·2^(n-2)
    (general: count subsets containing SOME candidate key, inclusion-exclusion)

NULL = unknown -> 3-valued logic (TRUE/FALSE/UNKNOWN). NULL=NULL is UNKNOWN.
  use IS NULL (never = NULL). Aggregates ignore NULL; COUNT(*) counts all rows.

INTEGRITY: domain | key(unique) | ENTITY(PK not null) | REFERENTIAL(FK=existing PK or NULL)
  FK actions on delete/update: RESTRICT | CASCADE | SET NULL | SET DEFAULT

RELATIONAL ALGEBRA (procedural):
  FUNDAMENTAL (6): sigma σ(rows) | pi π(cols,dedup) | rho ρ(rename) | ∪ | − | ×
  DERIVED: ∩ , ⋈ (theta/equi/NATURAL), ÷ , outer joins
  EXTENDED: generalized π (computed cols) | aggregation ℱ/γ (GROUP BY+COUNT/SUM/AVG)
            | assignment ← (name intermediate results)
  σ=WHERE, π=SELECT cols, ℱ=GROUP BY, ×=CROSS JOIN
  union-compatible (for ∪ ∩ −): same degree + compatible domains
  A−B ≠ B−A ; natural join w/ no common attr = ×
  DIVISION ÷ = "for ALL" = double NOT EXISTS in SQL

RELATIONAL CALCULUS (declarative):
  TRC { t | P(t) } over tuples ; DRC { <x,..> | P } over domain values
  must be SAFE (finite). Algebra = TRC = DRC in power (relationally complete).
  SQL: calculus in style, algebra in execution.
```

### Flash cards

| Front | Back |
|-------|------|
| Degree vs cardinality? | Degree = columns, cardinality = rows |
| Minimal super key? | Candidate key |
| Fundamental RA operators? | σ π ρ ∪ − × (join/∩/÷ are derived) |
| Entity integrity? | Primary key not NULL |
| Referential integrity? | FK = existing PK value, or NULL |
| π side effect? | Removes duplicate rows |
| "For all" operator? | Division ÷ (SQL: double NOT EXISTS) |
| Algebra vs calculus? | Procedural vs declarative (equal power) |
| Natural join, no common attr? | Becomes Cartesian product |
| Prime attribute? | Part of some candidate key |

### Spaced repetition
- **24-hour:** redo all 15 MCQs + write σ/π/⋈/÷ examples from memory.
- **7-day:** translate 5 English queries into relational algebra and into SQL.
- **30-day:** derive ∩ and ⋈ from the 6 fundamentals; explain division + its SQL.

---

## 3.11 Summary

The relational model represents all data as **relations (tables)** of **tuples**
over **attributes** drawn from **domains**, with **degree** = columns and
**cardinality** = rows. We learned the full **key hierarchy** (super ⊇ candidate ⊇
primary, plus alternate/foreign/composite/surrogate) and the **prime/non-prime**
distinction you'll reuse in normalization. We saw the four **integrity
constraints** — domain, key, **entity** (PK not NULL), and **referential** (FK
matches an existing PK) — and how foreign keys are protected with `CASCADE` /
`SET NULL` actions. Then we built up **relational algebra**: the **six
fundamental** operators (σ, π, ρ, ∪, −, ×) and the **derived** ones (∩, the
**joins**, and **division** for "for all" queries), reading queries as
**expression trees**. Finally, **relational calculus** (TRC over tuples, DRC over
domains) gave us the **declarative** side, with the key theorem that **algebra and
calculus are equally powerful** — and the insight that **SQL is calculus in style,
algebra in execution**.

Next, **Module 4 — SQL** turns all of this into the language you'll actually type;
then **Module 5 — Normalization** uses keys, FDs, and prime attributes to design
tables with no redundancy.

> **You have mastered this module when** you can: define degree/cardinality and
> every key type with an example; state entity vs referential integrity exactly;
> list which RA operators are fundamental vs derived; write σ/π/⋈/÷ for an English
> query; and explain why algebra and calculus have equal power — all without notes.
