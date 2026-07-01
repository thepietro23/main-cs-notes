---
title: "Module 2 — Entity-Relationship (ER) & Enhanced ER (EER) Model"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 2 — Entity-Relationship (ER) & Enhanced ER (EER) Model

> **Where this module sits.**
> In Module 1 we said the **conceptual schema** is the single, storage-free
> description of *what* data the whole organization holds. But *how do you create
> that schema* in the first place — before a single `CREATE TABLE` exists? You
> draw a picture. The **ER model** is that picture: a high-level, visual way to
> design a database that both a non-technical manager and a programmer can read.
> This module teaches you to *design* a database the way professionals actually
> do — diagram first, tables later.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★★★★    | ★★★       | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** cardinality ratios (1:1, 1:N,
M:N), weak entities & identifying relationships, total vs partial participation,
which symbol means what (oval/diamond/rectangle/underline), **how many tables an
ER diagram maps to** (especially "M:N needs a separate table"), and
specialization/generalization (ISA) in EER, **recursive (unary) relationships**,
and the **Chen vs Crow's-foot** notations.

---

## 2.1 Motivation — Why a *Picture* Before Tables?

### The problem

Suppose a college director tells you: *"Students enroll in courses and get grades;
instructors teach courses and belong to departments."* If you jump straight to
SQL, three different developers will produce three different table designs, and
you'll discover mistakes (missing relationships, wrong keys) only after data is
loaded — when fixing them is expensive.

We need a **design language** that is:

1. **Visual** — a manager can verify it without knowing SQL.
2. **DBMS-independent** — not tied to Oracle/MySQL/Postgres.
3. **Precise enough** to be *mechanically converted* into tables later.

### The solution — the ER model

Peter Chen introduced the **Entity-Relationship model in 1976**. Its genius: the
real world is made of **things** (entities) and **connections between things**
(relationships). Draw those, annotate them, and you have a blueprint that maps to
tables by fixed rules.

> **First-principles view:** an ER diagram is just a *typed graph*. Nodes =
> entities, edges = relationships, labels = attributes and constraints. Everything
> else is notation on top of that graph.

```
Real-world sentence:  "A STUDENT enrolls in a COURSE and receives a GRADE."
                          │              │            │
                       entity        relationship   attribute (of the relationship)
```

> **Exam nugget:** *Peter Chen, 1976* → ER model. (Pairs with Codd 1970 →
> relational model, from Module 1.)

---

## 2.2 The Three Building Blocks + Notation

Everything in an ER diagram is built from three shapes. Memorize this legend —
SEBI/RBI ask "which symbol represents X" directly.

![ER notation cheat sheet: rectangle=entity, double rectangle=weak entity, oval=attribute, underlined=key, dashed oval=derived, double oval=multivalued, diamond=relationship, double diamond=identifying, single/double line=partial/total participation.](images/11_er_notation.png)

| Shape                    | Means                              |
|--------------------------|------------------------------------|
| **Rectangle**            | Entity (strong)                    |
| **Double rectangle**     | Weak entity                        |
| **Oval/Ellipse**         | Attribute                          |
| **Underlined oval**      | Key attribute                      |
| **Dashed oval**          | Derived attribute                  |
| **Double oval**          | Multivalued attribute              |
| **Diamond**              | Relationship                       |
| **Double diamond**       | Identifying relationship (for weak entity) |
| **Single line**          | Partial participation              |
| **Double line**          | Total participation                |
| **1, N, M on a line**    | Cardinality ratio                  |

### Two notations: Chen (exam) vs Crow's Foot (industry)

The shapes above are **Chen notation** (1976) — what GATE/SEBI exams use. But
*real tools* (ERwin, Lucidchart, dbdiagram.io, MySQL Workbench) and most
interviews use **Crow's Foot notation**, where cardinality is drawn as **symbols
on the line ends** instead of diamonds and 1/N/M labels. You must recognize both.

![Crow's foot notation: line-end symbols — bar = one, crow's foot = many, double bar = exactly one, circle+bar = zero or one, circle+crow's foot = zero or many; example CUSTOMER 1:N ORDER.](images/23_crows_foot.png)

| Meaning | Crow's foot symbol | Chen equivalent |
|---------|--------------------|-----------------|
| exactly one | `──┤` (bar) | `1` |
| many | `──<` (crow's foot) | `N` / `M` |
| one and only one | `──╫` (double bar) | `1`, total |
| zero or one | `──o┤` (circle + bar) | `1`, partial |
| zero or many | `──o<` (circle + crow's foot) | `N`, partial |

> **The circle (o) = optional/zero = partial participation.** A bar/crow's-foot
> *without* a circle = mandatory = total participation. So crow's foot encodes
> **cardinality AND participation together** on each end — very compact.

> **How to read a crow's-foot end precisely (min, max):** each end carries **two**
> markers. The **inner** marker (closer to the entity box: a single bar `|` or the
> crow's foot `<`) gives the **maximum** (one vs many). The **outer** marker (a
> circle `o` or a bar `|`) gives the **minimum** (0 = optional, 1 = mandatory). So
> `o<` = "(0, many)" and `╫`/`||` = "(1, 1) exactly one". This matches the
> `(min,max)` notation in §2.5.

> **Interview tip:** if asked to "draw the schema", crow's foot looks more
> professional; if it's a written exam, stick to Chen (diamonds + 1/N/M).

---

## 2.3 Entities and Entity Sets

### Definition

- An **entity** is a real-world *object* that is distinguishable from others — a
  specific student "Asha", a specific course "DBMS-101".
- An **entity set (entity type)** is a *collection of entities of the same kind* —
  the set of all STUDENTs. In an ER diagram, the **rectangle** labelled `STUDENT`
  represents the entity *set*, not one student.

> **Subtle but tested:** the rectangle is the **entity type/set**; the rows of
> data later are the **entity instances**. (Recall Module 1's *schema vs
> instance* — same idea.)

### Strong vs Weak entities

- A **strong entity** has a **key attribute** of its own that uniquely identifies
  each instance (e.g. `STUDENT.roll_no`).
- A **weak entity** has **no key of its own**. It can only be identified in
  combination with a related **owner (identifying) entity**, using a **partial
  key** (a.k.a. discriminator). It is drawn as a **double rectangle** and connects
  to its owner through a **double diamond** (identifying relationship), always with
  **total participation**.

![Strong entity LOAN (key loan_no) owns weak entity PAYMENT (partial key pay_no, dashed underline) through identifying relationship Loan-Payment (double diamond, double line for total participation).](images/13_strong_weak_entity.png)

**Classic example.** A `PAYMENT` for a loan: payment #1, #2, #3 … restart for
*each* loan, so `pay_no` alone is not unique across all loans. A payment is
identified only as *(loan_no, pay_no)*. Hence PAYMENT is weak, owned by LOAN.

> **Why it matters (first principles):** a weak entity models a "part" whose
> identity depends on a "whole". If the owner row is deleted, the weak rows make
> no sense — this is why weak entities map to tables with the owner's key as part
> of their primary key *and* a foreign key (you'll see this in §2.9).

### Concept check

> *Q:* A `ROOM` is numbered 101, 102 … but every building restarts at 101. Is
> ROOM weak or strong? *A:* **Weak** — identified only as *(building_id,
> room_no)*; owner = BUILDING.

---

## 2.4 Attributes — Every Flavour

![Types of attributes: simple, composite, single-valued, multivalued, derived, key; plus stored-vs-derived and NULL meaning.](images/12_attribute_types.png)

| Type            | Meaning                                         | Symbol            | Example                         |
|-----------------|-------------------------------------------------|-------------------|---------------------------------|
| **Simple/atomic** | Cannot be divided                             | oval              | `age`, `gender`                 |
| **Composite**   | Splits into sub-parts                            | oval with sub-ovals | `name → {first, last}`        |
| **Single-valued** | One value per entity                           | oval              | `date_of_birth`                 |
| **Multivalued** | Many values per entity                           | **double** oval   | `phone_numbers {…}`             |
| **Derived**     | Computed from other data, not stored             | **dashed** oval   | `age` (from `dob` + today)      |
| **Stored**      | Actually stored (the opposite of derived)        | oval              | `dob`                           |
| **Key**         | Uniquely identifies the entity                   | **underlined** oval | `roll_no`                     |
| **NULL**        | Value unknown / not applicable / missing         | —                 | `middle_name = NULL`            |

> **Composite vs multivalued — the classic confusion:** *composite* = one value
> made of parts (one full name). *Multivalued* = several independent values (three
> phone numbers). Composite splits *down*; multivalued repeats *across*.

> **Why derived attributes exist:** storing `age` would go stale every birthday.
> Store the stable fact (`dob`) and **derive** the volatile one (`age`). This is a
> first-principles design rule: *store the source of truth, compute the rest.*

### MCQs

1. `phone_numbers` for a person is best modelled as ___ → **multivalued (double oval)**.
2. `age` computed from `dob` is a ___ attribute → **derived (dashed oval)**.
3. A key attribute is shown by ___ → **underlining** it.

---

## 2.5 Relationships, Degree, Cardinality, Participation

### Relationship and relationship set

A **relationship** is an association among entities ("Asha *enrolls in* DBMS-101").
A **relationship set** is the collection of such associations of the same type,
drawn as a **diamond** (`ENROLLS`). Relationships can themselves have
**attributes** — e.g. the `grade` belongs to the *enrollment*, not to the student
or the course alone.

### Degree of a relationship (how many entity types participate)

```
Unary   (degree 1): EMPLOYEE  --supervises-->  EMPLOYEE   (recursive / self relationship)
Binary  (degree 2): STUDENT   --enrolls-->     COURSE      (the most common)
Ternary (degree 3): DOCTOR -- prescribes --> PATIENT, and the DRUG too
```

> **Exam line:** most relationships are **binary**. A relationship connecting an
> entity *to itself* is **recursive (unary)** and needs **role names** (e.g.
> "supervisor"/"subordinate").

### Cardinality ratio — the most-tested ER concept

Cardinality answers: *how many* entities of one set can relate to *how many* of
the other?

![Three cardinality ratios: 1:1 (Employee–Manages–Dept), 1:N (Dept–Has–Employee), M:N (Student–Enrolls–Course).](images/14_cardinality.png)

| Ratio  | Reads as                                   | Example                                  |
|--------|--------------------------------------------|------------------------------------------|
| **1:1**| one ↔ one                                  | an employee manages **one** dept; a dept has **one** manager |
| **1:N**| one → many                                 | a dept has **many** employees; an employee is in **one** dept |
| **M:N**| many ↔ many                                | a student takes **many** courses; a course has **many** students |

> **The single most important mapping fact (memorize):** a **M:N** relationship
> *always* becomes its **own separate table**; a **1:N** does **not** (you just
> add a foreign key on the "many" side). This is asked in nearly every PSU/GATE
> paper.

### Participation constraint — total vs partial

Participation asks: *must every* entity take part in the relationship, or only
*some*?

![Participation: double line (total) = every employee must work for a dept; single line (partial) = not every dept needs an employee here.](images/15_participation.png)

- **Total participation (double line):** *every* entity instance **must**
  participate. Example: every `EMPLOYEE` **must** `Works-for` some `DEPT`. Also
  called **existence dependency**.
- **Partial participation (single line):** participation is **optional**. Example:
  not every `EMPLOYEE` `Manages` a dept (only managers do).

> Weak entities **always** have **total** participation in their identifying
> relationship (they cannot exist without the owner).

### Min-max (look-here) notation — alternative you may see

Some books write `(min, max)` on each edge, e.g. `(1,1)`, `(0,N)`. Here `min=1`
means total participation, `min=0` means partial. `max=N` means many. It encodes
cardinality *and* participation together.

> ⚠️ **Trap:** in `(min,max)` notation the numbers attach to the **near** entity
> and read "looking from that entity"; in the simple `1/N/M` notation the label is
> placed on the line. Read the question's convention carefully.

**Concrete contrast (the classic GATE side-flip trap).** Take "every DEPT has
many EMPLOYEEs; every EMPLOYEE belongs to exactly one DEPT" (a 1:N):

```
Chen:        DEPT ──1──< Works >──N── EMPLOYEE      (label on the line)
(min,max):   DEPT (1,N) ── Works ── (1,1) EMPLOYEE  (label on the near entity)
```

Notice the numbers appear on **opposite sides** in the two notations! In Chen the
"N" sits near the relationship on the EMPLOYEE side (many employees per dept); in
`(min,max)` the EMPLOYEE end reads `(1,1)` (each employee → exactly one dept).
Same reality, mirrored placement — *this is precisely what trips students up in
exams.*

**Why they mirror: "look-across" vs "look-here".** This is the deep reason, and it
is a genuine GATE/theory point:

- **Chen's `1/N/M` labels are "look-across".** The number on EMPLOYEE's line tells
  you how many DEPTs an employee sees *across* the relationship (one), so you write
  it near the *far* entity.
- **`(min,max)` is "look-here" (a.k.a. Merise notation).** The pair on EMPLOYEE
  reads "looking *from here*, how many relationship instances does one employee take
  part in?" → `(1,1)`. It attaches to the *near* entity.

That single difference — *count the partner across* vs *count my own participation
here* — is exactly why the two numbers land on opposite ends for the same reality.

> ⚠️ **Ternary trap (why min-max wins for degree ≥ 3):** for **binary**
> relationships the two styles are interchangeable (just swap the labels). But for
> a **ternary**, look-across breaks down — from one entity there are **two** other
> entities "across", so a single number is ambiguous. Therefore **participation on
> n-ary relationships must use the look-here `(min,max)` convention.** If an exam
> shows `(min,max)` on a ternary, read each pair as "this entity's minimum and
> maximum participation in the whole ternary relationship."

### Recursive (unary) relationships — in depth

A **recursive relationship** connects an entity set **to itself**. The same entity
plays **two different roles**, so we *must* label the roles to read it.

![Recursive relationship: EMPLOYEE SUPERVISES EMPLOYEE; one end is the role "supervisor" (1), the other "subordinate" (N). Maps to a self-referencing foreign key mgr_id.](images/24_recursive_relationship.png)

**Classic example — employee hierarchy.** An `EMPLOYEE` *supervises* other
`EMPLOYEE`s. One employee is the **supervisor** (the "1" side), many are
**subordinates** (the "N" side). Without role names the diagram is ambiguous.

**How it maps to a table (very common interview question):** a recursive 1:N
becomes a **self-referencing foreign key** — the table points back to its own
primary key:

```
EMPLOYEE(emp_id PK, name, dept_id, mgr_id FK -> EMPLOYEE.emp_id)
                                    └── mgr_id of an employee = emp_id of their boss
```

> **Why this matters in practice:** org charts, threaded comments (a comment
> replies to a comment), category trees (a category has a parent category), and
> "friends/follows" graphs are all recursive relationships. The self-FK pattern is
> something backend engineers write constantly.

> **Exam trap:** the *degree* of a recursive relationship is **1 (unary)** — it
> involves **one** entity set, even though two "lines" are drawn to it.

### Ternary vs binary — and why you *can't always* decompose (worked example)

A tempting shortcut is to replace one **ternary** (degree-3) relationship with
**three binary** ones. Usually this **loses information** — a classic GATE trap.

**Setup.** A `SUPPLIER` **supplies** a `PART` **for** a `PROJECT`. The real fact
is a *triple*: "Supplier S supplies Part P to Project J." Suppose reality is:

```text
SUPPLIES (the true ternary fact)
supplier | part  | project
---------+-------+---------
   S1    |  P1   |   J1
   S2    |  P1   |   J2
```

Now try to store it as **three separate binary** relationships instead:

```text
CAN_SUPPLY (S–P)   USED_IN (P–J)     WORKS_ON (S–J)
S1 | P1            P1 | J1           S1 | J1
S2 | P1            P1 | J2           S2 | J2
```

**The information is now gone.** Join the three binaries back and you *also*
generate the false triple **(S1, P1, J2)** — the binaries say "S1 can supply P1",
"P1 is used in J2", "S1... " but they can **no longer distinguish** whether S1
actually supplies P1 *specifically to* J2. The ternary carried a fact that no
combination of pairwise facts can reconstruct.

> **First-principles rule:** a ternary is decomposable into binaries **only** when
> the triple is functionally implied by its pairs (a "lossless" special case). In
> general it is **not** — so keep it ternary and map it by **rule 8** (§2.9): one
> table with **all three keys** as the composite primary key.

> **Exam nugget:** *"Can every ternary relationship be replaced by three binary
> relationships?"* → **No** (generally lossy). This one-word answer wins marks.

### Concept check

> *Q:* "Every account must belong to a branch, but a branch may have zero
> accounts." Translate to constraints.
> *A:* ACCOUNT side = **total** (double line); BRANCH side = **partial**;
> cardinality BRANCH:ACCOUNT = **1:N**.

---

## 2.6 Worked Example — A Full University ER Diagram

Let's apply everything to one realistic schema and *read it aloud*.

![University ER diagram: STUDENT (roll_no key, name, cgpa derived) ENROLLS (grade) in COURSE (course_id key, title) as M:N; INSTRUCTOR (emp_id) TEACHES courses (1:N) and WORKS-IN DEPT (dept_id) as N:1.](images/16_sample_er_university.png)

**How to read it:**

- `STUDENT` has key `roll_no`, attribute `name`, and a **derived** `cgpa` (dashed).
- `STUDENT` **ENROLLS** in `COURSE`; the ratio is **M:N**, and `grade` is an
  attribute **on the relationship** (it depends on the *pair* student+course).
- `INSTRUCTOR` **TEACHES** `COURSE` with ratio **1:N** (one instructor, many
  courses).
- `INSTRUCTOR` **WORKS-IN** exactly one `DEPT` (**N:1**, with total participation
  on the instructor side — every instructor must be in a department).

> **Active recall:** before reading the next section, predict *how many tables*
> this diagram produces. (Answer in §2.9.)

---

## 2.7 EER — Enhanced ER: Specialization, Generalization, Aggregation

Basic ER struggles with **"is-a"** hierarchies and with relationships that involve
*other relationships*. **EER** adds three features.

### Specialization / Generalization (the ISA hierarchy)

![EER ISA hierarchy: PERSON superclass (person_id, name) specializes into STUDENT (cgpa), STAFF (salary), ALUMNI (grad_year) via an ISA triangle; subclasses inherit superclass attributes.](images/17_eer_specialization.png)

- **Specialization (top-down):** start with a general entity `PERSON` and split it
  into sub-types `STUDENT`, `STAFF`, `ALUMNI` that each add their own attributes.
- **Generalization (bottom-up):** notice that `CAR` and `TRUCK` share attributes,
  and combine them into a general `VEHICLE`. *Same picture, opposite thinking
  direction.*
- **Inheritance:** subclasses inherit all superclass attributes and relationships
  (`STUDENT` automatically has `person_id`, `name`), then add their own (`cgpa`).
- The relationship is drawn with an **ISA triangle**.

**Two constraint dimensions (frequently tested):**

| Dimension                | Options                | Meaning                                                |
|--------------------------|------------------------|--------------------------------------------------------|
| **Disjointness**         | **Disjoint (d)** / **Overlapping (o)** | can an entity be in *more than one* subclass? d = no, o = yes |
| **Completeness**         | **Total** / **Partial**| must *every* superclass entity be in *some* subclass?  |

> Example: a `PERSON` could be both `STUDENT` and `STAFF` → **overlapping**.
> A `SHAPE` is exactly one of `CIRCLE/SQUARE/TRIANGLE` → **disjoint, total**.

**How membership is decided (GATE EER point):**

- **Attribute-defined (predicate-defined) specialization:** a value of a
  **defining attribute** of the superclass decides the subclass — e.g.
  `EMPLOYEE.job_type = 'engineer'` puts the row in the `ENGINEER` subclass. The
  discriminator attribute is shown on the ISA line.
- **User-defined specialization:** there is **no** defining attribute; the database
  user explicitly assigns each entity to a subclass.

> **Shared subclass / specialization lattice (multiple inheritance):** a subclass
> can inherit from **more than one** superclass (e.g. `TEACHING_ASSISTANT` is both
> a `STUDENT` and an `EMPLOYEE`). This turns the hierarchy (tree) into a
> **lattice**, and the shared subclass inherits attributes from all its parents.

### Aggregation

![EER aggregation: the relationship (EMPLOYEE WORKS-ON PROJECT), enclosed in a dashed box, is treated as a higher-level entity that participates in the USES relationship with MACHINERY.](images/18_aggregation.png)

**Problem aggregation solves:** ER does **not** allow a relationship to connect to
*another relationship*. But sometimes a fact about a relationship needs its own
relationship. Example: the fact "(EMPLOYEE WORKS-ON PROJECT)" itself **USES**
some `MACHINERY`. We **aggregate** the `WORKS-ON` relationship into a single
higher-level entity (the dashed box), which can then participate in `USES`.

> **Interview soundbite:** "Aggregation = treating a relationship as if it were an
> entity, so it can take part in further relationships."

### Category / Union type (the fourth EER feature)

A **category** (or **union type**) is a subclass whose members come from the
**union of several different superclasses**. Contrast with normal specialization,
where one superclass splits into subclasses.

- *Specialization:* `PERSON` → {`STUDENT`, `STAFF`} — subclasses share **one**
  superclass.
- *Category:* `OWNER` is a subclass of the **union** of `PERSON`, `BANK`, and
  `COMPANY` (a vehicle's owner could be a person *or* a bank *or* a company).
  Drawn with a **∪ (union) circle**, sometimes labelled `U`.

```
 PERSON ┐
 BANK   ├──∪──►  OWNER   (an OWNER is a member of ONE of these superclasses)
 COMPANY┘
```

> **Specialization vs Category (don't confuse):** in specialization an instance
> inherits from **one** superclass and the subclass adds attributes. In a
> category, an instance belongs to **exactly one of several** different
> superclasses (selective inheritance). Category is rarely asked but appears in
> GATE EER theory.

---

## 2.8 First-Principles: How the DBMS *Uses* the ER Design

The ER diagram is a **conceptual** artifact — it never runs. But it directly
becomes the **logical schema** (Module 1's middle layer) through a mechanical
translation, and from there the storage engine builds the **physical** layer.

```
ER diagram (conceptual)  --8 rules-->  Relational tables (logical)  --engine-->  files/indexes (physical)
```

This is why getting the ER model right matters so much: errors here propagate all
the way down. A missing relationship means a missing foreign key means an
application that can't answer a question it should.

---

## 2.9 ER → Relational Mapping (the 8 Rules)

This is the bridge from "picture" to "tables". Learn these eight rules; SEBI/GATE
test them as "how many tables / which foreign key goes where".

![ER-to-relational mapping: 8 rules covering strong entity, weak entity, 1:1, 1:N, M:N, multivalued attribute, specialization, and ternary relationship.](images/19_er_to_relational.png)

1. **Strong entity → its own table.** The entity's key attribute becomes the
   **primary key**. (`STUDENT(roll_no, name)`.)
2. **Weak entity → its own table**, whose **primary key = owner's PK + the partial
   key**, with the owner's PK also a **foreign key**.
   (`PAYMENT(loan_no, pay_no, amount)`, PK = (loan_no, pay_no).)
3. **1:1 relationship → no new table**; put a foreign key on **either** side
   (prefer the side with *total* participation, to avoid NULLs). **Special case:**
   if **both** sides have **total** participation, you can **merge both entities
   into a single table** with no loss.
4. **1:N relationship → no new table**; put the foreign key on the **"N" (many)**
   side. (`EMPLOYEE(emp_id, …, dept_id FK)`.) **Any attributes of a 1:N
   relationship also migrate to the "N"-side table** (they're determined by the N
   side).
5. **M:N relationship → a NEW table** whose primary key is the **combination of
   both entities' keys**, plus any relationship attributes.
   (`ENROLLS(roll_no, course_id, grade)`, PK = (roll_no, course_id).)
6. **Multivalued attribute → a separate table** (entity's PK + the value). One row
   per value. (`PHONE(emp_id, phone_no)`.)
7. **Specialization (ISA) → one of three strategies:** (a) one table for the
   whole hierarchy with a type discriminator; (b) one table per subclass (each
   includes inherited attributes); (c) one table for superclass + one per
   subclass (joined by the shared key).
8. **Ternary (degree-3) relationship → a NEW table** whose **primary key is the
   combination of all THREE participating entities' keys** (plus any relationship
   attributes). E.g. `SUPPLIES(supplier_id, part_id, project_id, qty)`, PK =
   (supplier_id, part_id, project_id). *(This is a classic GATE/SEBI trap — a
   ternary always becomes its own table; you cannot fold it into a single FK.)*

**Answer to §2.6's active-recall question** — the university diagram maps to:

```
STUDENT(roll_no, name)                          -- rule 1
COURSE(course_id, title, emp_id FK)             -- rule 1 + rule 4: TEACHES is 1:N,
                                                --   so instructor emp_id is a FK here
INSTRUCTOR(emp_id, name, dept_id FK)            -- rule 1 + rule 4: WORKS-IN is N:1
DEPT(dept_id, dname)                            -- rule 1
ENROLLS(roll_no, course_id, grade)              -- rule 5: M:N -> new table
```

So: **5 tables** (STUDENT, COURSE, INSTRUCTOR, DEPT, ENROLLS). The 1:N
relationships (TEACHES, WORKS-IN) became foreign keys, not tables; only the M:N
(ENROLLS) became a table. *This is the exact reasoning a numerical question
expects.*

### Dry run — count the tables (exam-style)

> *Given:* entities A, B, C. Relationships: A–B is 1:N, B–C is M:N, A has a
> multivalued attribute.
> *Tables?* A, B, C (3) + the M:N B–C (1) + the multivalued attribute (1) = **5
> tables**. A–B 1:N adds only a foreign key in B. ✔
>
> *Variant:* entities A, B, C with **one ternary** relationship among all three.
> *Tables?* A, B, C (3) + the ternary (1) = **4 tables**; the ternary table's PK =
> (key_A, key_B, key_C). ✔ *(Don't fold a ternary into a foreign key — common
> mistake.)*

> **Interview follow-up (M:N → two 1:N):** you can always replace an M:N
> relationship by introducing an **associative (junction) entity** in the middle,
> turning it into two 1:N relationships. `STUDENT —1:N→ ENROLLMENT ←N:1— COURSE`.
> This is exactly what the M:N join table *is*, viewed as an entity. Useful when
> the relationship itself gains its own attributes/keys (e.g. an enrollment gets
> an `enrollment_id`, timestamp, status).

---

## 2.10 Flowchart — How to Design an ER Diagram from Requirements

![Flowchart for ER design: read requirements → find entities (nouns) → list attributes + mark keys → spot weak entities → find relationships (verbs) → set cardinality + participation → add EER (ISA/aggregation) → apply 8 mapping rules → schema ready.](images/20_fc_er_design.png)

**The practical heuristic (works in interviews and exams):**

- **Nouns** in the requirement → candidate **entities** / attributes.
- **Verbs** → candidate **relationships**.
- Ask of each entity: *does it have its own key?* If no → **weak**.
- Ask of each relationship: *how many ↔ how many?* (cardinality) and *must all
  participate?* (participation).

---

## 2.11 Real-World & Backend Perspectives

- **Real-world / backend:** ER diagrams are the standard first step in any product
  database design. Tools (dbdiagram.io, MySQL Workbench, draw.io) let teams agree
  on the model before coding. The "M:N needs a join table" rule is something
  backend engineers apply weekly (e.g. `users` ↔ `roles` → `user_roles`).
- **System design:** the ER model is how you communicate a data model in a design
  interview — draw entities and relationships before discussing sharding or
  caching.

---

## 2.12 Tradeoffs, Common Mistakes, Edge Cases

**Tradeoffs**

| Strength of ER model                          | Limitation                                    |
|-----------------------------------------------|-----------------------------------------------|
| Visual, intuitive, DBMS-independent           | No standard for *operations*/behavior (it's structural only) |
| Maps mechanically to tables                   | Many notations exist (Chen vs Crow's-foot vs UML) → confusion |
| Great for communication with non-engineers    | Hard to show complex constraints precisely    |

**Common mistakes (exam + real life)**
- Treating an **M:N** relationship as if it needs no table — it **always** needs
  one.
- Putting a 1:N foreign key on the **wrong (one) side** — it goes on the **many**
  side.
- Drawing a relationship's attribute (like `grade`) on an entity instead of on the
  diamond.
- Forgetting that a **weak entity** has **total participation** and a **partial
  key** (dashed underline), not a full key.
- Confusing **composite** (one value, many parts) with **multivalued** (many
  values).

**Edge cases**
- **Ternary relationships** generally cannot be replaced by three binary ones
  without losing meaning (a frequent GATE trap). When mapped, a ternary becomes
  **its own table with all three keys as the composite PK** (mapping rule 8).
- A **recursive** relationship needs **role labels** to be readable.
- A 1:1 relationship with total participation on both sides *can* be merged into a
  single table.

---

## 2.13 Concept Checks & MCQs

1. A diamond in an ER diagram represents ___ → **a relationship**.
2. A double oval represents a ___ attribute → **multivalued**.
3. Which relationship type always needs a separate relation when mapped? → **M:N**.
4. A weak entity's key in the table is ___ → **owner's PK + partial key**.
5. "Every loan must have a customer" is which constraint? → **total participation**
   (of LOAN).
6. ER model was proposed by ___ in ___ → **Peter Chen, 1976**.
7. The ISA triangle in EER represents ___ → **specialization/generalization
   (inheritance)**.
8. Aggregation is used when ___ → **a relationship must participate in another
   relationship**.
9. A relationship of degree 3 is called ___ → **ternary**.
   *(When mapped → one table with all THREE keys as the composite primary key.)*
10. `name = {first, last}` is a ___ attribute → **composite**.
11. Can every ternary relationship be replaced by three binary relationships
    without losing information? → **No** (generally lossy; keep it ternary).
12. In `(min,max)` notation on an EMPLOYEE that belongs to exactly one DEPT, the
    EMPLOYEE end reads ___ → **(1,1)**.
13. Chen's `1/N/M` labels use the ___ convention; `(min,max)` uses the ___
    convention → **look-across** / **look-here (Merise)**.
14. For a **ternary** relationship, which convention must participation constraints
    use, and why? → **look-here `(min,max)`** — because there are *two* entities
    "across", so look-across is ambiguous.

**True/False**
- A 1:N relationship is mapped to its own table. → **False** (FK on the N side).
- A derived attribute is physically stored. → **False**.
- Overlapping specialization allows an entity in two subclasses. → **True**.

**Scenario (interview)**
> *"Model a hospital where a PATIENT can have many APPOINTMENTs, each with one
> DOCTOR, and we record the appointment's date and diagnosis."* Identify entities,
> relationships, cardinalities.
> *Sketch:* PATIENT (1) — has — (N) APPOINTMENT (N) — with — (1) DOCTOR;
> `date`, `diagnosis` are attributes of APPOINTMENT. Two 1:N relationships →
> APPOINTMENT carries `patient_id` and `doctor_id` as foreign keys.

---

## 2.14 One-Page Revision Sheet

```
ER MODEL (Peter Chen, 1976) = visual conceptual design.

SHAPES:
 rectangle = entity        double rectangle = weak entity
 oval = attribute          underlined = key   dashed = derived
 double oval = multivalued  diamond = relationship
 double diamond = identifying (weak)  triangle = ISA (EER)
 single line = partial      double line = total participation

ENTITY: strong (own key) | weak (no key -> owner PK + PARTIAL key, dashed underline,
        identifying double-diamond, ALWAYS total participation)

ATTRIBUTES: simple | composite(one value,parts) | single | multivalued(many values)
            | derived(not stored, dashed) | stored | key(underlined) | NULL

RELATIONSHIP:
 degree: unary(recursive, SAME entity, 2 roles, self-FK mgr_id)/binary/ternary
 cardinality: 1:1 | 1:N | M:N
 participation: total(double line)/partial(single line)

NOTATIONS: Chen(exam: diamonds + 1/N/M) vs Crow's foot(industry: line-end symbols;
 bar=one, crow=many, circle=optional/partial)

EER: specialization(top-down)/generalization(bottom-up); inheritance;
     disjoint(d)/overlapping(o); total/partial; aggregation(relationship as entity);
     category/union(subclass of UNION of many superclasses)

MAPPING TO TABLES (8 rules):
 strong->table(PK=key)          weak->table(PK=owner PK+partial key, FK)
 1:1->FK either side            1:N->FK on MANY side (NO new table)
 M:N->NEW table(PK=both keys+attrs)   multivalued->separate table
 specialization->single/per-subclass/superclass+subclass tables
 ternary->NEW table, PK = all THREE entity keys
EER specialization membership: attribute-defined (discriminator attr) vs user-defined;
 shared subclass = multiple inheritance (lattice).

TERNARY (degree 3) -> its own table, PK = all THREE entity keys (don't fold!).
1:N relationship attributes -> migrate to the N-side table.
M:N <-> two 1:N via an associative/junction entity (same thing as the join table).

GOLDEN RULE: only M:N (and multivalued, and weak, and ternary) create EXTRA tables;
             1:1 and 1:N become foreign keys.
```

### Flash cards

| Front                                       | Back                                         |
|---------------------------------------------|----------------------------------------------|
| Which ratio needs a separate table?         | M:N                                          |
| 1:N foreign key goes on which side?         | The "many" (N) side                          |
| Weak entity participation?                  | Always total                                 |
| Symbol for derived attribute?               | Dashed oval                                  |
| ISA triangle means?                         | Specialization/generalization (inheritance) |
| Aggregation solves?                         | Relationship participating in a relationship |
| Recursive relationship degree?              | Unary (1) — same entity, 2 roles, self-FK    |
| Crow's foot: circle (o) means?              | Optional / zero / partial participation      |
| Category (union type) is?                   | Subclass of the union of many superclasses   |
| ER model author & year?                     | Peter Chen, 1976                             |

### Spaced repetition
- **24-hour:** redraw the university ER diagram from memory; map it to 5 tables.
- **7-day:** explain weak entity, total participation, and M:N mapping aloud.
- **30-day:** given a 4-line requirement, produce a full ER diagram + table count.

---

## 2.15 Summary

The ER model lets us **design** a database as a picture before writing any SQL.
We learned its three building blocks — **entities** (strong/weak), **attributes**
(simple, composite, multivalued, derived, key), and **relationships** (with
**degree**, **cardinality** 1:1/1:N/M:N, and **participation** total/partial) —
and the exact **notation** for each. We extended to **EER** with
specialization/generalization (the **ISA** hierarchy, with disjoint/overlapping
and total/partial constraints) and **aggregation**. Finally, we crossed the
bridge from picture to logical schema with the **8 mapping rules**, and saw the
golden exam fact: **only M:N relationships (plus weak entities and multivalued
attributes) create extra tables; 1:1 and 1:N become foreign keys.**

In Module 1 we learned the *layers* of a database; here we learned to *design* the
conceptual layer. Next, in **Module 3 — the Relational Model & Algebra**, we make
those tables mathematically precise (keys, integrity constraints) and learn the
**relational algebra** that every SQL query is secretly compiled into.

> **You have mastered this module when** you can, from a one-paragraph
> requirement, draw a correct ER diagram (right shapes, cardinalities,
> participation), extend it with ISA/aggregation where needed, and convert it to
> the exact set of tables — stating *why* each table exists — without notes.
