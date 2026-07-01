---
title: "Module 1 — Introduction to DBMS & Database Architecture"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 1 — Introduction to DBMS & Database Architecture

> **Why this module comes first.**
> Before you can normalize a table, tune an index, or reason about a transaction,
> you must understand *what a database actually is*, *why humanity invented it*,
> and *how it is structured inside*. Almost every other DBMS topic is an answer
> to a problem first raised in this module. Students who skip the foundations
> later confuse "schema" with "instance", "logical" with "physical", and fail
> easy 1-mark exam questions. We will not let that happen. We start from the
> world *before* databases and build the whole architecture brick by brick.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★★★     | ★★★       | ★★★     |

**Most-asked PYQ concepts from this module (SEBI/RBI/GATE):**
data independence (logical vs physical), the three-schema (ANSI-SPARC)
architecture, levels of data abstraction, schema vs instance, DDL/DML/DCL/TCL
classification, DBMS vs file system advantages, **data models (hierarchical/
network/relational)**, **DBMS vs RDBMS + Codd's 12 rules**, **2-tier vs 3-tier
architecture**, and roles of the DBA.

---

## 1.1 The World Before Databases — Why DBMS Was Invented

### Motivation (the problem that existed)

Imagine a bank in 1965. It has three departments — **Savings**, **Loans**, and
**Accounts**. Each department wrote its own programs (in COBOL) and each kept its
own **files** on tape or disk. The savings program had a file with customer
name, address, and balance. The loans program *also* stored the customer's name
and address (because it needed them too). So did accounts.

This "every-application-owns-its-files" style is called the **file-processing
system**. It worked — until it didn't. Here is what went wrong, and *each pain
point below is literally the reason a DBMS feature exists*:

| Problem in file systems        | What actually happened                                              | DBMS feature that fixes it |
|--------------------------------|--------------------------------------------------------------------|----------------------------|
| **Data redundancy**            | Customer address stored in 3 files = 3× storage                    | Single shared database     |
| **Data inconsistency**         | Customer moves; address updated in 1 file, not the others          | Centralized control + constraints |
| **Difficulty accessing data**  | New report ("customers in PIN 110001 with balance > 1L") needs a *new program* each time | Query language (SQL)       |
| **Data isolation**             | Data scattered in many files/formats; hard to combine             | One integrated model       |
| **Integrity problems**         | "balance ≥ 0" rule buried inside program code, easy to violate    | Integrity constraints      |
| **Atomicity problems**         | Transfer ₹500: debit succeeds, then crash before credit → money vanishes | Transactions (atomicity)   |
| **Concurrent-access anomalies**| Two clerks update the same balance at once → one update lost       | Concurrency control        |
| **Security problems**          | Hard to give a teller access to balances but *not* to loan data    | Authorization / views      |

> **First-principles takeaway:** A DBMS is not magic. It is the *accumulated
> set of solutions* to these eight concrete failures of file processing. Memorize
> this table — SEBI/RBI love "Which of the following is NOT an advantage of DBMS?"

![Left: each application owns duplicate files (redundant, inconsistent). Right: all applications share one DBMS-controlled database.](images/01_filesystem_vs_dbms.png)

### Definition

A **Database** is an organized, related collection of data representing some
aspect of the real world (called the **mini-world** or **Universe of Discourse**).

A **Database Management System (DBMS)** is the *software* that lets you
**define**, **construct**, **manipulate**, and **share** a database while
enforcing **integrity**, **security**, **concurrency**, and **recovery**.

> Database + DBMS software + applications + users = a **Database System**.

### Intuition

Think of a DBMS as a **librarian for data**:

- You don't walk into the stacks and grab books yourself (you don't read raw disk
  blocks). You ask the librarian (you write SQL).
- The librarian knows *where* every book is (indexes), keeps the catalog
  consistent (constraints), won't let two people check out the last copy
  (concurrency control), and can rebuild the catalog after a fire (recovery).

### Historical background (so the names make sense)

```
1963   Charles Bachman — IDS (at GE), the first DBMS; forerunner of the
       network/CODASYL model (CODASYL formalized it ~1969-71)
1968   IMS (IBM) — hierarchical model (tree-structured), used for Apollo program
1970   E. F. Codd (IBM) publishes "A Relational Model of Data for Large Shared
       Data Banks" — the relational model. (Turing Award, 1981.)
1974   System R (IBM) and Ingres (Berkeley) — first relational prototypes;
       System R gives birth to SEQUEL, later renamed SQL.
1979   Oracle ships the first commercial relational DBMS.
1986   SQL becomes an ANSI standard.
2000s  NoSQL rises for web-scale (Google Bigtable, Amazon Dynamo, MongoDB).
2010s+ NewSQL & distributed SQL (Google Spanner, CockroachDB).
```

> **Exam nugget:** *Codd = relational model.* *Bachman = network model (and an
> early Turing Award).* These two names appear in PSU IT papers.

---

## 1.1A Data Models — The Evolution (Hierarchical → Network → Relational → …)

### Motivation

A **data model** is a *set of concepts for describing data, relationships, and
constraints* — i.e. the "shape" in which we organize data. Over 60 years the
dominant shape changed as engineers hit walls. Knowing this evolution answers a
recurring SEBI/RBI question ("Which model uses a tree structure?") *and* gives you
the intuition for *why* the relational model won.

![Three classic data models: hierarchical (tree, parent→child 1:N), network (graph, M:N allowed), relational (tables with keys).](images/21_data_models.png)

| Model | Shape | Idea | Pain that killed it / Note |
|-------|-------|------|----------------------------|
| **Hierarchical** | Tree | Each child has exactly **one** parent (1:N only). IBM **IMS** (1968), used in Apollo. | Cannot model M:N naturally; rigid; navigation by pointers. |
| **Network** | Graph | A child can have **many** parents (M:N). **Bachman**/CODASYL. | Very complex pointer "navigation"; hard to change. |
| **Relational** | Tables (relations) | Data as **rows & columns**, linked by **keys**, queried **declaratively**. **Codd, 1970**. | The winner — simple, math-backed, SQL. (Modules 3–5.) |
| **Object-Oriented** | Objects | Stores objects directly (with methods). | Good for complex types; niche. |
| **Object-Relational** | Tables + object types | Relational core + user-defined types (e.g. **PostgreSQL**). | Mainstream extension of relational. |
| **Semi-structured / NoSQL** | JSON, key-value, column, graph | Flexible/schema-light, web-scale. | Module 11 (MongoDB, Cassandra, Neo4j). |

> **First-principles "why relational won":** the older models forced the
> programmer to *navigate* pointers (procedural — "how to get there"). Codd's
> insight was to make queries **declarative** ("what I want"), letting the system
> figure out the path. That separation is the same idea as data independence —
> hide the "how", expose the "what".

> **Exam nuggets:** Hierarchical = **tree** (one parent). Network = **graph**
> (many parents, Bachman/CODASYL). Relational = **tables** (Codd). These three
> are the most-tested.

---

## 1.2 Data Abstraction — Hiding Complexity in Three Layers

### Motivation

A modern database may store billions of rows in compressed B+-tree files across
many disks. If an application programmer had to know *all* of that just to read a
customer's name, nobody would ever finish writing software. The DBMS therefore
**hides** the messy details behind layers — exactly like how you drive a car
without understanding combustion. This hiding is called **data abstraction**.

### The three levels

![Three levels of abstraction: physical (how stored) → logical (what data) → view (what a user sees).](images/03_data_abstraction.png)

1. **Physical level (lowest / internal):** *How* data is actually stored — files,
   pages/blocks, B+-tree indexes, compression, record layout. Concerns the DBA
   and the storage engine. Example: "Customer rows are stored in a heap file,
   with a B+-tree index on `customer_id`, blocks of 8 KB."

2. **Logical level (middle / conceptual):** *What* data is stored and *what
   relationships* exist — tables, columns, datatypes, keys, constraints. This is
   the developer's world. Example: `Customer(id INT, name VARCHAR(50), city VARCHAR(30))`.

3. **View level (highest / external):** *What a particular user sees* — a tailored
   slice that hides the rest for simplicity and security. Example: a teller's view
   exposes `name, balance` but hides `loan_history`.

> **Analogy (locks it in):** Physical = the engine and gearbox. Logical = the
> dashboard (speed, fuel — meaningful quantities). View = a chauffeur who only
> tells the passenger "we'll arrive in 10 minutes."

### Concept check (think before reading on)

> *Q:* When you write `SELECT name FROM Customer;`, which level of abstraction are
> you operating at?
> *A:* The **logical** level. You name a table and a column; you neither create a
> personal view nor touch storage details.

---

## 1.3 Schema vs Instance — The Single Most Confused Pair

### Definition

- **Schema:** the *overall design / structure* of the database — the table
  definitions, columns, types, and constraints. Set up once, changes **rarely**.
- **Instance (a.k.a. state / snapshot):** the *actual data* stored at a
  particular moment. Changes **constantly** (every INSERT/UPDATE/DELETE).

![Schema is the blueprint (like a class); an instance is the data right now (like an object).](images/07_schema_vs_instance.png)

### Intuition

The cleanest analogy in all of DBMS:

```
Schema    ≈  a CLASS in OOP        (the template / type)
Instance  ≈  an OBJECT in OOP      (a concrete value at runtime)

Schema    ≈  an empty exam answer sheet (the printed form)
Instance  ≈  all the answer sheets filled in by students today
```

### Three kinds of schema (maps onto the three levels)

- **Physical schema** — design at the physical level.
- **Logical schema** — design at the logical level (the one we usually mean).
- **View schema (subschema)** — design at the view level.

> **Why SEBI/GATE test this:** a typical 1-marker is *"Which changes more
> frequently — schema or instance?"* → **instance**. Or *"The logical schema is
> also called ___"* → **conceptual schema**.

### Worked example — one schema, many instances

The distinction becomes obvious the moment you see it in code. The **schema** is
the `CREATE TABLE` line; the **instance** is whatever rows happen to be inside
*right now*:

```sql
-- SCHEMA (the design; you write this once)
CREATE TABLE Student (
    roll_no INT PRIMARY KEY,
    name    VARCHAR(50),
    cgpa    DECIMAL(3,2)
);
```

```text
INSTANCE at 9:00 AM                    INSTANCE at 5:00 PM (after edits)
roll_no | name  | cgpa                 roll_no | name  | cgpa
--------+-------+-----                 --------+-------+-----
  1     | Asha  | 8.10                    1    | Asha  | 8.40   <- cgpa updated
  2     | Ravi  | 7.55                    3    | Meera | 9.02   <- new row inserted
                                         (row 2 was deleted)
```

The `CREATE TABLE` (schema) never changed all day — but the **instance** changed
with *every* INSERT / UPDATE / DELETE. That is the whole point: **schema = stable
type, instance = live value.** A database has **exactly one schema** but passes
through **countless instances** over its lifetime.

> **Interview follow-up:** *"Can two databases share a schema but differ in
> instance?"* → **Yes** — a `staging` and a `production` database can run the
> identical `CREATE TABLE` script (same schema) yet hold completely different
> rows (different instances). This is exactly how test environments are built.

---

## 1.4 The Three-Schema (ANSI-SPARC) Architecture

### Motivation & problem statement

We now formalize the three levels into the famous **ANSI/SPARC three-schema
architecture** (1975). Its single purpose: **separate the user's view of data
from how it is physically stored, so that changes at one layer don't break the
layers above.** That separation is called **data independence** (next section),
and it is the crown jewel of database design.

### The architecture

![ANSI-SPARC three-schema architecture: external views map to one conceptual schema, which maps to one internal schema, which maps to disk.](images/02_three_schema_architecture.png)

- **External level (views):** many external schemas, one per user group. Each
  view shows only the relevant part of the database.
- **Conceptual level:** exactly **one** conceptual schema describing the whole
  database for the community of users — entities, relationships, constraints,
  *without* storage details.
- **Internal level:** exactly **one** internal schema — physical storage
  structures, file organizations, indexes.

The DBMS maintains **mappings** between the levels:

- **External/Conceptual mapping** — connects each view to the conceptual schema.
- **Conceptual/Internal mapping** — connects the conceptual schema to storage.

> **Memory trick:** **"E-C-I"** from top to bottom = **E**xternal, **C**onceptual,
> **I**nternal. "Many views, one logical truth, one physical reality."

### Internal working (how a read travels the layers)

```
User asks (external view)
      │  external/conceptual mapping
      ▼
Conceptual schema decides which tables/relationships
      │  conceptual/internal mapping
      ▼
Internal schema locates files/blocks/indexes on disk
      ▼
Bytes come back up, reshaped into the user's view
```

---

## 1.4A Two-Tier vs Three-Tier Architecture (Client–Server)

### ⚠️ First, kill the #1 confusion

Students mix up **two different "architectures"**:

- The **three-schema (ANSI-SPARC) architecture** (§1.4) is about **levels of
  abstraction** *inside* the DBMS (external / conceptual / internal). It answers
  *"how is the data described?"*
- The **tier architecture** (this section) is about **physical deployment** — how
  many *machines/layers* sit between the user and the database. It answers *"who
  talks to whom over the network?"*

> **Memory hook:** *Schemas = how data is **described**. Tiers = where software is
> **deployed**.* Different questions, often asked back-to-back to trick you.

### Motivation & the tiers

![Two-tier: client (UI + logic) talks directly to the DB server via SQL/ODBC. Three-tier: presentation (browser) → application server (logic) → database server; client never touches the DB.](images/22_two_vs_three_tier.png)

**One-tier:** everything (UI, logic, DB) on a single machine — e.g. a local
SQLite app. Simplest, single user.

**Two-tier (Client–Server):** the **client** holds the UI *and* business logic and
talks **directly** to the **database server** using SQL (often over ODBC/JDBC).

- 👍 Simple, fast for small LANs.
- 👎 Poor scaling (each client opens a DB connection), and **security risk** —
  DB credentials and logic live on every client.

**Three-tier:** insert a middle **application/logic tier** between client and DB:

1. **Presentation tier** — the client (browser/mobile UI). Knows nothing about
   the DB.
2. **Application (logic) tier** — the server with business rules, an API; the
   *only* layer that talks to the DB.
3. **Data tier** — the DBMS.

- 👍 **Scalable** (add app servers behind a load balancer), **secure** (clients
  never see the DB), **maintainable** (change logic without touching clients).
- 👎 More moving parts.
- This is the **standard architecture of essentially every web application.**

| | Two-Tier | Three-Tier |
|---|----------|------------|
| Layers | Client ↔ DB | Client ↔ App server ↔ DB |
| Business logic | on the client | on the app server |
| Scalability | limited | high |
| Security | weak (DB exposed) | strong (DB hidden) |
| Typical use | small LAN tools | web/enterprise apps |

> **Interview soundbite:** "We use three-tier so the browser never holds DB
> credentials and we can scale the stateless app tier horizontally." This single
> line shows you understand *why* the middle tier exists.

### Concept check

> *Q:* A bank's internet-banking site has a browser, a set of API servers, and an
> Oracle database. Which tier model, and which tier enforces "withdraw ≤ balance"?
> *A:* **Three-tier**; the rule lives in the **application (logic) tier**.

---

## 1.5 Data Independence — The Crown Jewel

### Definition

**Data independence** is the capacity to change the schema at one level **without
having to change the schema at the next higher level**. There are two kinds:

![Logical data independence shields views from logical changes; physical data independence shields the logical schema from storage changes.](images/04_data_independence.png)

1. **Physical Data Independence (PDI):** change the **internal/physical** schema
   (add an index, switch from a heap to a hashed file, move to a new disk)
   **without** changing the **conceptual/logical** schema.
   - *Easier to achieve* — and almost every DBMS provides it well.
   - Example: you create an index on `Customer(city)` to speed up queries. No
     table definition changes; no application changes.

2. **Logical Data Independence (LDI):** change the **conceptual/logical** schema
   (add a new column, add a new table, split a table) **without** changing the
   **external/view** schemas (and thus without changing existing applications).
   - *Harder to achieve* — because applications depend closely on the logical
     structure.
   - Example: you add a `loyalty_points` column to `Customer`. The teller's old
     view (`name, balance`) still works untouched.

> **The exam mnemonic that never fails:**
> **"Logical is harder, Physical is easier."**
> And remember the *direction*: each kind protects the level **above** it from a
> change **below** it.

### First-principles: *why* do we even want this?

Software outlives hardware. A logical schema designed in 2010 may run on disks,
SSDs, and cloud storage across its life. If every storage upgrade forced a
rewrite of all applications, software maintenance would be impossible. Data
independence is what lets the storage team and the application team evolve
**separately**. It is the database world's version of "program to an interface,
not an implementation."

### Common mistake (very frequently tested)

> ✗ "Adding an index requires changing the logical schema." **Wrong.** Adding an
> index is a *physical* change; thanks to **physical data independence**, the
> logical schema is untouched.

### Concept check

> *Q:* You migrate the database to faster NVMe disks and re-block the files. Which
> data independence makes this painless for application programmers?
> *A:* **Physical data independence** (storage changed; logical schema unchanged).

---

## 1.6 Database Languages (DDL / DML / DCL / TCL)

### Motivation

A DBMS needs commands to (a) *define* structure, (b) *change* data, (c) *control
access*, and (d) *bound transactions*. SQL bundles all four families into one
language, but exams test you on the **classification**.

![SQL sub-languages: DDL defines structure, DML changes data, DCL controls permissions, TCL bounds transactions.](images/06_sql_sublanguages.png)

| Family | Full form               | Commands                                   | Purpose                          | Auto-commit? |
|--------|-------------------------|--------------------------------------------|----------------------------------|--------------|
| **DDL**| Data Definition Language| `CREATE, ALTER, DROP, TRUNCATE, RENAME`    | define/modify **structure**      | Usually yes* |
| **DML**| Data Manipulation Lang. | `SELECT, INSERT, UPDATE, DELETE`           | query/change **data**            | No           |
| **DCL**| Data Control Language   | `GRANT, REVOKE`                            | **permissions** / security       | Usually yes* |
| **TCL**| Transaction Control Lang| `COMMIT, ROLLBACK, SAVEPOINT`              | **transaction** boundaries       | —            |

> Some books call the query part (`SELECT`) **DQL** (Data Query Language). If you
> see DQL in an option, it means "SELECT".

> **\*Accuracy note (vendor-dependent — interview gotcha):** DDL/DCL auto-commit
> is **not** universal. In **Oracle & MySQL**, DDL like `CREATE`/`DROP` issues an
> *implicit commit* (you can't roll it back). In **PostgreSQL & SQL Server**, DDL
> and `GRANT`/`REVOKE` are **transactional** — you *can* wrap them in a
> transaction and `ROLLBACK`. For a written exam, "DDL auto-commits" is the
> expected answer; in an interview, mention the PostgreSQL exception — it signals
> depth. Also, `RENAME` is vendor-specific (standard SQL uses `ALTER TABLE …
> RENAME`).

### Internal working — DDL builds the *data dictionary*

When you run a DDL statement like `CREATE TABLE`, the DBMS doesn't just allocate
storage — it records the new structure in the **data dictionary** (a.k.a. **system
catalog**): a special set of tables describing *all* tables, columns, types,
constraints, indexes, and users. This "data about data" is **metadata**. Every
query consults the dictionary first ("does this table exist? is this user
allowed?").

> **Active vs passive data dictionary (a classic PSU/GATE MCQ):** an **active**
> data dictionary is **managed automatically by the DBMS** and stays in sync with
> the schema (any DDL change updates it instantly) — this is what modern RDBMSs
> have. A **passive** data dictionary is maintained **separately/manually** (e.g. as
> documentation) and can fall out of sync. *Active = self-updating by the DBMS;
> passive = manual, may be stale.*

### Classic traps (memorize)

- **`DELETE` vs `TRUNCATE` vs `DROP`:**
  - `DELETE FROM T;` → DML, removes rows (can have `WHERE`), logged, can be rolled
    back, keeps the table structure.
  - `TRUNCATE TABLE T;` → DDL, removes *all* rows fast (no `WHERE`), minimally
    logged, usually **cannot** be rolled back, keeps the structure.
  - `DROP TABLE T;` → DDL, removes the **structure + data** entirely.
- `TRUNCATE` resets identity counters; `DELETE` does not.

### MCQs

1. `GRANT SELECT ON Account TO teller;` belongs to which family? → **DCL**.
2. Which is a DDL command: `UPDATE`, `COMMIT`, `ALTER`, `GRANT`? → **`ALTER`**.
3. Which can be rolled back: `TRUNCATE` or `DELETE`? → **`DELETE`** (generally).

---

## 1.6A DBMS vs RDBMS, and Codd's 12 Rules

### DBMS vs RDBMS (a guaranteed exam comparison)

A **DBMS** stores data and lets you manage it. An **RDBMS** (Relational DBMS) is a
DBMS that follows Codd's **relational model** — data in **tables** with
**relationships** enforced by **keys**, queried with **SQL**.

| Feature | DBMS | RDBMS |
|---------|------|-------|
| Data storage | files / hierarchical / network | **tables (relations)** |
| Relationships | via navigation/pointers | via **foreign keys** |
| Keys & constraints | weak / manual | **enforced** (PK/FK/UNIQUE/CHECK) |
| Normalization | not really supported | **supported** |
| Multi-user / ACID | limited | **full** support |
| Data volume | small | large |
| Examples | file systems, XML stores, older IMS | **MySQL, PostgreSQL, Oracle, SQL Server** |

> **One-liner to remember:** *Every RDBMS is a DBMS, but not every DBMS is an
> RDBMS.* RDBMS = DBMS **+ tables + keys + SQL + ACID**.

### Codd's 12 Rules (actually 13: Rule 0 to Rule 12)

E. F. Codd published **12 rules** (numbered **0–12**, so 13 total) that a system
must satisfy to be called *truly relational*. You don't need to memorize all 13
verbatim, but SEBI/PSU papers ask "Codd gave how many rules?" (**12**, with a
Rule 0) and occasionally name one. The most important to *recognize*:

- **Rule 0 — Foundation:** must manage the DB entirely through its relational
  capabilities.
- **Rule 1 — Information:** all data represented as **values in tables**.
- **Rule 2 — Guaranteed access:** every value reachable by **table + primary key +
  column** (no pointers).
- **Rule 3 — Systematic NULL treatment:** NULLs handled uniformly (unknown / not
  applicable), independent of datatype.
- **Rule 4 — Active online catalog:** the **data dictionary** itself is relational
  and queryable with the same language.
- **Rule 5 — Comprehensive sub-language:** one language (SQL) for definition,
  manipulation, control, transactions.
- **Rule 6 — View updating;** **Rule 7 — High-level insert/update/delete** (set at
  a time, not row-by-row).
- **Rules 8 & 9 — Physical & Logical data independence** (the §1.5 ideas — note
  Codd named them explicitly!).
- **Rule 10 — Integrity independence;** **Rule 11 — Distribution independence;**
  **Rule 12 — Non-subversion** (no low-level bypass of the rules).

> **Fun fact for interviews:** *no commercial RDBMS fully satisfies all 12 rules.*
> They're an ideal benchmark, not a checklist any product fully passes.

> **Exam nuggets:** Codd = **12 rules (0–12)**. Rules **8 & 9** are exactly
> physical & logical **data independence**. Rule 4 = the relational **catalog**.

---

## 1.6B Quick Previews & Classifications (ACID, Keys, DBMS Types, OLTP vs OLAP)

This module name-drops a few terms that deserve a one-line anchor now (full depth
comes in later modules). These are **high-frequency 1-mark exam questions**.

### ACID — the four transaction guarantees (full detail: Module 9)

When a DBMS runs a **transaction** (a logical unit of work, e.g. a money
transfer), it guarantees **ACID**:

| Letter | Property | Plain meaning | Bank-transfer example |
|--------|----------|---------------|------------------------|
| **A** | **Atomicity** | all-or-nothing | debit + credit both happen, or neither |
| **C** | **Consistency** | DB moves from one valid state to another | total money unchanged; constraints hold |
| **I** | **Isolation** | concurrent txns don't corrupt each other | two transfers at once ≠ wrong balance |
| **D** | **Durability** | once committed, survives crashes | after "success", power loss can't undo it |

> **Memory hook:** **A**ll-or-nothing, **C**orrect state, **I**solated from others,
> **D**urable forever. Guaranteed by the **transaction manager** + **recovery**
> (Modules 9–10).

### Keys — the one-line preview (full detail: Module 3)

- **Super key:** any set of attributes that uniquely identifies a row.
- **Candidate key:** a *minimal* super key (no extra attributes).
- **Primary key:** the one candidate key you choose (unique + not NULL).
- **Foreign key:** an attribute referencing another table's primary key (the glue
  between tables).

### Types of DBMS (by location & users — common SEBI/RBI MCQ)

| Type | Meaning |
|------|---------|
| **Centralized** | data + DBMS on a single site/machine |
| **Distributed** | data spread across multiple sites, appears as one DB (Module 11) |
| **Parallel** | multiple CPUs/disks work on one query for speed |
| **Cloud / Hosted** | DBMS as a managed service (e.g. Amazon RDS, Aurora) |
| **Single-user vs Multi-user** | one user at a time vs many concurrent users |

### OLTP vs OLAP (very frequently asked; full detail: Module 11)

| | **OLTP** (Online Transaction Processing) | **OLAP** (Online Analytical Processing) |
|---|------------------------------------------|------------------------------------------|
| Purpose | day-to-day **transactions** | **analysis** / reporting / BI |
| Operations | many short INSERT/UPDATE/DELETE | few, complex, read-heavy queries |
| Data | current, detailed | historical, aggregated |
| Example | ATM withdrawal, order placement | "total sales by region last 5 years" |
| Schema | highly **normalized** | **star/snowflake** (denormalized) |

> **Memory hook:** **OLTP = writes/operations** (running the business). **OLAP =
> reads/analysis** (understanding the business).

> **Two more dimensions exams love (append to the table above mentally):**
> **Users** — OLTP serves *thousands* of clerks/customers; OLAP serves a *handful*
> of analysts/managers. **Response time** — OLTP must reply in *milliseconds*;
> OLAP queries may run for *seconds to minutes*. **Source of data** — OLTP is the
> *original* source; an OLAP **data warehouse** is *loaded (ETL) from* the OLTP
> systems. **Backup criticality** — losing OLTP data loses live business; OLAP can
> be re-derived from OLTP.

---

## 1.6C Why Concurrency Control & Recovery Are Needed (Teasers)

Two of the eight file-system problems in §1.1 — *concurrent-access anomalies* and
*atomicity problems* — are so important that every serious DBMS dedicates a whole
subsystem to each. Full treatment is in **Modules 9 (Transactions/Concurrency)**
and **10 (Recovery)**, but here is the *why*, made concrete, so the rest of the
course has a hook to hang on.

### Why concurrency control? (the "lost update" walkthrough)

Two ATM clerks read the same account (balance ₹1000) at the same moment and each
adds a deposit. Without control, one update silently vanishes:

```text
Time  Clerk A (deposit ₹200)      Clerk B (deposit ₹500)      balance on disk
----  -------------------------   -------------------------   ---------------
 t1   read balance = 1000                                          1000
 t2                               read balance = 1000              1000
 t3   compute 1000+200 = 1200                                      1000
 t4                               compute 1000+500 = 1500          1000
 t5   write 1200                                                   1200
 t6                               write 1500  (overwrites!)        1500
```

The correct final balance is **₹1700**, but the result is **₹1500** — Clerk A's
₹200 deposit is **lost**. This is the **lost-update anomaly**. **Concurrency
control** (locking / MVCC, Module 9) prevents it by forcing the two transactions
to interleave *safely*, as if they ran one after another (**serializability**).

> **First principles:** the bug is not in either program — each is correct alone.
> It appears *only* because they overlap. That is why concurrency is a DBMS
> responsibility, not the application programmer's.

### Why recovery? (the "crash mid-transfer" walkthrough)

A transfer of ₹500 is two writes: **debit** A, then **credit** B. If the machine
crashes *between* them, money simply disappears:

```text
BEGIN transfer ₹500 from A to B
   debit  A: 1000 -> 500     ✓ written
   *** POWER FAILURE ***           <- credit to B never happened
   credit B: ...             ✗
Result without recovery: A lost 500, B gained nothing → ₹500 vanished.
```

The **recovery manager** (Module 10) fixes this using a **write-ahead log**: on
restart it sees the transfer never reached `COMMIT`, so it **undoes** the partial
debit, restoring A to ₹1000. This is **atomicity** (the *A* in ACID) in action —
*all-or-nothing.* Durability (the *D*) is the mirror image: once `COMMIT` is
logged, a crash can never *lose* the change.

> **Exam nugget:** concurrency control protects against *other transactions*
> (interference); recovery protects against *failures* (crashes/power loss).
> Different enemies, different subsystems — do not confuse them.

---

## 1.7 DBMS Architecture — How the Engine Is Built Inside

### The overall structure

A DBMS is internally organized into two big subsystems sitting above the disk:
the **Query Processor** (turns your SQL into actions) and the **Storage Manager**
(moves data between disk and memory safely).

![Overall DBMS structure: users on top, Query Processor, Storage Manager, then disk storage with data files, dictionary, and indices.](images/05_dbms_structure.png)

**Query Processor components**

- **DDL interpreter** — processes DDL, updates the data dictionary.
- **DML compiler / optimizer** — translates DML into a low-level **evaluation
  plan**, and *optimizes* it (picks the cheapest plan using indexes & statistics).
- **Query evaluation engine** — executes the chosen plan.

**Storage Manager components**

- **Authorization & integrity manager** — checks the user's rights and that
  integrity constraints hold.
- **Transaction manager** — guarantees ACID: keeps the DB consistent despite
  crashes, and isolates concurrent transactions.
- **File manager** — manages disk space allocation and on-disk data structures.
- **Buffer manager** — fetches blocks from disk into RAM and decides what to keep
  cached (this is *the* performance-critical component).

**On disk**

- **Data files** (the actual rows), **data dictionary** (metadata),
  **indices** (for fast lookup), and **statistics** (used by the optimizer).

### Dry run — the life of one query

Let's trace `SELECT name FROM Customer WHERE city = 'Mumbai';` end to end:

```
1. Parser checks syntax → builds a parse tree.
2. Semantic check + authorization: does Customer exist? is 'city' a column?
   is this user allowed to SELECT?   (consults data dictionary)
3. Optimizer: is there an index on city? If yes, plan = "index scan";
   else plan = "full table scan". Picks the cheaper plan using statistics.
4. Evaluation engine runs the plan.
5. Buffer manager: needed block already in RAM? -> use it (fast, ~100 ns).
   Else read it from disk (slow, ~10 ms) into the buffer pool.
6. Transaction manager ensures this read sees a consistent snapshot.
7. Rows with city='Mumbai' are projected to just 'name' and returned.
```

![Flowchart — life of a SQL query: parse → authorize → optimize → execute → fetch blocks → ACID → result.](images/09_fc_query_flow.png)

> **Why the buffer manager matters most:** a RAM hit is ~100,000× faster than a
> disk read. Almost all of database performance engineering is "keep the right
> blocks in RAM." We will return to this in the Storage and Indexing modules.

---

## 1.8 Database Users and the DBA

![Database users (naive, application programmers, sophisticated, specialized) and the DBA who administers everything.](images/10_users_dba.png)

- **Naive / naïve users:** interact through ready-made apps (ATM screen, railway
  booking). They never see SQL.
- **Application programmers:** write the programs those users click through
  (embedding SQL in Java/Python, etc.).
- **Sophisticated users:** analysts/data scientists who write **ad-hoc** SQL and
  build reports directly.
- **Specialized users:** build complex domain apps (CAD, GIS, ML pipelines).

**The Database Administrator (DBA)** is the central authority who:

- defines the **schema** and storage structure,
- grants/revokes **authorization** (security),
- monitors and **tunes performance** (indexes, query plans),
- handles **backup and recovery**,
- plans **capacity** and upgrades.

### Data Administrator (DA) vs Database Administrator (DBA) — a tested distinction

Textbooks (and GfG) split the role into two, and exams ask the difference:

| | **Data Administrator (DA)** | **Database Administrator (DBA)** |
|---|------------------------------|----------------------------------|
| Nature | **managerial / policy** | **technical / operational** |
| Scope | the whole **organization's data** | a **specific database** + its apps |
| Focuses on | data *meaning*, governance, standards, privacy policy | install, tune, index, backup, secure the DBMS |
| Sample task | "define the enterprise data-retention policy" | "add an index, fix a slow query, restore a backup" |

> **One-liner:** *DA decides **what** the data should be and **who may** use it
> (policy); DBA makes the database **run** it (technology).* In small companies one
> person wears both hats.

**Common DBA sub-specializations (interview colour):** an **Administrative/System
DBA** (installs, patches, backs up), an **Application DBA** (owns schemas & tuning
for one app), and a **Performance DBA** (indexes, query plans, capacity). Larger
shops split these; smaller shops merge them.

> **Interview line:** "The DBA owns the *non-functional* guarantees — security,
> availability, performance, recoverability — so application teams can focus on
> business logic."

---

## 1.9 Should You Even Use a DBMS? (Decision Flowchart)

A DBMS is powerful but not free — it adds cost, complexity, and overhead. Use this
decision flow:

![Flowchart — Do I need a DBMS? Multiple users, ACID, complex queries, or large secured data → yes; otherwise a flat file may do.](images/08_fc_need_dbms.png)

**When a DBMS is overkill:** tiny config files, single-user throwaway scripts,
write-once log files. Here a flat file or SQLite-style embedded store is enough.

**When a DBMS is essential:** concurrent users, money/medical/legal data needing
integrity & audit, complex relationships and queries, security and backup
requirements — i.e. virtually every serious backend system.

---

## 1.10 DBMS Across the Industry (Real-World Lenses)

- **Real-world example (banking):** the eight file-system problems in §1.1 are
  exactly why core banking runs on RDBMS — atomic transfers, audit, concurrency
  for millions of users.
- **Backend example:** a typical web app uses **PostgreSQL/MySQL**. The
  three-schema idea shows up directly: ORM models = logical schema; database
  *views* = external schema; storage engine + indexes = internal schema.
- **System-design perspective:** "single source of truth", read replicas
  (external-level scaling), and schema migrations (logical data independence in
  action) are all this module's ideas at scale.

---

## 1.11 Tradeoffs, Performance, Security, Edge Cases

**Tradeoffs of using a DBMS**

| Gain                                    | Cost                                          |
|-----------------------------------------|-----------------------------------------------|
| Integrity, concurrency, recovery, security | Software + license + hardware cost          |
| Single source of truth, less redundancy | Added complexity, need for a DBA              |
| Powerful declarative queries (SQL)      | Overhead vs a raw file for trivial workloads  |

**Performance:** dominated by disk vs RAM access (buffer manager) and by good
indexing/optimization (Modules 6–8). Declarative SQL lets the optimizer choose
fast plans you didn't hand-code.

**Security:** authorization (DCL `GRANT`/`REVOKE`), **views** to expose only
permitted columns, and the integrity manager enforcing constraints. The DBA is
accountable for all of this.

**Common mistakes (exam + real life)**
- Confusing **schema** (rarely changes) with **instance** (constantly changes).
- Swapping the two data independences — *logical is harder; physical is easier.*
- Calling `TRUNCATE` a DML command (it's **DDL**).
- Thinking the logical schema knows about indexes (it doesn't — that's physical).

**Edge cases**
- A database can have **many** external schemas but only **one** conceptual and
  **one** internal schema.
- Some lightweight stores (SQLite) blur the layers, but the conceptual model
  still applies.

---

## 1.12 Exam, Interview & Coding Perspectives

**Competitive-exam (SEBI / RBI / GATE) perspective — what gets asked**
- Definitions: DBMS advantages over file systems (the 8-row table).
- Three-schema architecture & the two mappings.
- Data independence (logical vs physical) — *which is harder, which protects what.*
- Schema vs instance; conceptual = logical synonym.
- Classify a command into DDL/DML/DCL/TCL.
- `DELETE` vs `TRUNCATE` vs `DROP`.
- Codd → relational model; Bachman → network model.

**Interview perspective**
- "Why not just use files?" → recite the 8 problems.
- "What is data independence and why do you care?" → maintainability/evolution.
- "Walk me through what happens when I run a SELECT." → §1.7 dry run.

**Coding/practical perspective**
- Install PostgreSQL; run `CREATE TABLE`, then inspect the catalog:
  `SELECT * FROM information_schema.tables;` — you are literally reading the
  **data dictionary**.
- Create a `VIEW` and notice you've built an *external schema*.

---

## 1.13 Concept Checks & MCQs (test yourself)

1. **T/F:** A database can have multiple conceptual schemas. → **False** (one
   conceptual, many external).
2. Adding an index on a column relies on which independence? → **Physical**.
3. The "data about data" stored by the DBMS is called ___. → **metadata / data
   dictionary / system catalog**.
4. Which changes more often, schema or instance? → **Instance**.
5. `COMMIT` belongs to which language family? → **TCL**.
6. Which level does an end user of an ATM operate at? → **View (external)**.
7. Logical data independence is *(easier / harder)* than physical. → **Harder**.
8. Who published the relational model? → **E. F. Codd (1970)**.
9. Which component decides which disk blocks stay in RAM? → **Buffer manager**.
10. `TRUNCATE` is a ___ command. → **DDL**.
11. Which data model uses a **tree** structure (one parent per child)? → **Hierarchical**.
12. In three-tier architecture, where does business logic live? → **Application
    (middle) tier**.
13. "Every RDBMS is a DBMS but not vice-versa" — what does RDBMS add? → **tables +
    keys + SQL + ACID** (relational model).
14. Codd gave how many rules? → **12 (numbered 0–12)**; rules **8 & 9** are
    physical & logical data independence.
15. Network model (many parents per child) is associated with ___ → **Bachman /
    CODASYL**.
16. ACID stands for ___ → **Atomicity, Consistency, Isolation, Durability**.
17. "Once committed, survives a crash" is which ACID property? → **Durability**.
18. OLTP is for ___ and OLAP is for ___ → **transactions (writes)** / **analysis
    (reads)**.
19. A *minimal* super key is called a ___ → **candidate key**.
20. Data spread across many sites but appearing as one DB = ___ DBMS → **distributed**.
21. Two transactions both read balance ₹1000, add deposits, and write back; one
    deposit disappears. This anomaly is called ___ → **lost update** (fixed by
    **concurrency control**).
22. A crash occurs after debiting A but before crediting B in a transfer. Which
    subsystem restores atomicity, and how? → **recovery manager**, by **undoing**
    the partial transaction using the **write-ahead log**.
23. Concurrency control protects against ___; recovery protects against ___. →
    **other transactions (interference)** / **failures (crashes)**.
24. Which role is *managerial and org-wide* — DA or DBA? → **Data Administrator
    (DA)**; the **DBA** is technical and database-specific.
25. Same `CREATE TABLE` script, different rows — same ___, different ___. →
    **schema** / **instance**.
26. An OLAP data warehouse is typically *loaded from* which kind of system? →
    **OLTP** (via ETL).

**Fill in the blanks**
- The architecture with external/conceptual/internal levels is the ___ → *ANSI-SPARC three-schema*.
- The mapping between views and the logical schema is the ___ mapping → *external/conceptual*.

**Scenario question**
> A new compliance rule requires storing each customer's PAN. You add a `pan`
> column to `Customer`. Existing teller applications, which use a view of
> `(name, balance)`, keep running with **no change**. *Which property made this
> possible?* → **Logical data independence.**

---

## 1.14 One-Page Revision Sheet

```
DBMS = software to define/construct/manipulate/share a database with
       integrity, security, concurrency, recovery.

8 FILE-SYSTEM PROBLEMS DBMS SOLVES:
redundancy, inconsistency, hard access, isolation, integrity,
atomicity, concurrency anomalies, security.

DATA MODELS: Hierarchical(tree,1 parent,IMS) | Network(graph,M:N,Bachman/CODASYL)
  | Relational(tables,keys,Codd 1970) | Object | Object-Relational | NoSQL
DBMS vs RDBMS: RDBMS = DBMS + tables + keys + SQL + ACID. Codd's 12 rules(0-12);
  rules 8&9 = physical & logical data independence; rule 4 = relational catalog.

ABSTRACTION (top→bottom):  VIEW → LOGICAL → PHYSICAL
3-SCHEMA (ANSI-SPARC):     EXTERNAL(many) → CONCEPTUAL(one) → INTERNAL(one)
  mappings: external/conceptual, conceptual/internal
TIERS (deployment, NOT schemas!): 1-tier(all one box) | 2-tier(client<->DB) |
  3-tier(client<->APP server<->DB; web standard; logic in middle tier)

ACID (txn guarantees): Atomicity(all-or-nothing) Consistency(valid state)
  Isolation(concurrent safe) Durability(survives crash). [Modules 9-10]
KEYS: super >= candidate(minimal) >= primary(chosen, not null); foreign(ref PK).
DBMS TYPES: centralized | distributed | parallel | cloud | single/multi-user.
OLTP(writes, day-to-day, normalized) vs OLAP(reads, analysis, star schema).

SCHEMA = design (rarely changes) ≈ class
INSTANCE = data now (changes a lot) ≈ object
conceptual schema = logical schema (synonyms)

DATA INDEPENDENCE:
  Physical DI = change storage, logical unaffected   (EASIER)
  Logical  DI = change logical, views/apps unaffected (HARDER)

LANGUAGES:
  DDL: CREATE ALTER DROP TRUNCATE RENAME   (structure; auto-commit)
  DML: SELECT INSERT UPDATE DELETE         (data)
  DCL: GRANT REVOKE                        (permissions)
  TCL: COMMIT ROLLBACK SAVEPOINT           (transactions)
  DELETE(DML, rollback-able) | TRUNCATE(DDL, fast, no WHERE) | DROP(DDL, kills table)

ENGINE: Query Processor (DDL interp, DML optimizer, eval engine)
        Storage Manager (authz/integrity, transaction, file, BUFFER mgr)
        Disk: data files, data dictionary(metadata), indices, statistics

HISTORY: Bachman→network; Codd(1970)→relational; SQL from System R/SEQUEL.
DBA: schema, security, tuning, backup/recovery, capacity.
```

### Flash cards (cover the right side)

| Front                                   | Back                                              |
|-----------------------------------------|---------------------------------------------------|
| Logical vs physical DI — which is harder?| Logical (apps depend on logical structure)       |
| Conceptual schema synonym?              | Logical schema                                     |
| Many or one conceptual schema?          | One (many external, one conceptual, one internal) |
| TRUNCATE is which family?               | DDL                                                |
| Who invented the relational model?      | E. F. Codd (1970)                                  |
| Fastest-impact perf component?          | Buffer manager (RAM vs disk)                       |
| Metadata lives in?                      | Data dictionary / system catalog                   |

### Spaced-repetition schedule

- **24-hour revision:** redo all 20 MCQs + the one-page sheet from memory.
- **7-day revision:** re-explain the three-schema architecture and both data
  independences aloud, as if teaching a junior.
- **30-day revision:** classify 15 mixed SQL commands into DDL/DML/DCL/TCL and
  re-derive the 8 file-system problems unaided.

---

## 1.15 Summary

We started in the pre-database world and watched eight concrete failures of file
processing force the invention of the DBMS. We then climbed the **three levels of
abstraction** (view → logical → physical), formalized them as the **ANSI-SPARC
three-schema architecture**, and saw why the separation between them — **data
independence** — is the most valuable property in database design (logical
harder, physical easier). We distinguished **schema** (design) from **instance**
(data), classified the **DDL/DML/DCL/TCL** languages, opened up the DBMS engine
(**query processor + storage manager**, with the **buffer manager** as the
performance heart), and traced one query through it. Finally we met the **users
and the DBA**, and learned when a DBMS is and isn't worth it.

Everything that follows — the ER model, the relational model, SQL, normalization,
indexing, transactions, recovery — is a deep dive into one of the boxes you just
saw in the engine diagram. You now have the map. Next module: **the ER model**,
where we learn to *design* the conceptual schema before a single table exists.

> **You have mastered this module when** you can, from a blank page: draw the
> three-schema architecture, explain both data independences with an example
> each, list the eight file-system problems, classify any SQL command, and trace
> a query through the engine — all without notes.
