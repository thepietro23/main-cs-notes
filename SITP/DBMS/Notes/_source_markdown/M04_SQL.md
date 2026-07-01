---
title: "Module 4 — SQL (Structured Query Language)"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 4 — SQL (Structured Query Language)

> **Where this module sits.**
> Module 3 gave us the *theory* (relational algebra). SQL is the *language* you
> actually type — the declarative front-end that the database translates into
> algebra and runs. SQL is the **single most practical** topic in this entire
> course: it is asked in almost every IT exam, every backend interview, and used
> every day on the job. We'll connect every SQL feature back to the algebra you
> already learned, so nothing feels arbitrary.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★★  | ★★★★    | ★★★★★     | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** output prediction of a given
query; **WHERE vs HAVING**; **GROUP BY** rules; **join types** & their results
(inner/outer/self); **correlated vs non-correlated subqueries**; **aggregate
functions + NULL behaviour**; **UNION vs UNION ALL**; **DDL vs DML vs DCL vs
TCL** classification; constraints; the **logical execution order** of clauses;
and `DELETE` vs `TRUNCATE` vs `DROP`.

---

## 4.1 What SQL Is, and Its Sub-Languages

**SQL** (originally **SEQUEL**, from IBM's System R) is a **declarative** language:
you say *what* you want, not *how* to get it. The optimizer picks the *how*.

SQL groups into four sub-languages (you met these in Module 1 — here we use them):

| Family | Commands | Purpose |
|--------|----------|---------|
| **DDL** (Definition) | `CREATE, ALTER, DROP, TRUNCATE, RENAME` | define/modify **structure** |
| **DML** (Manipulation) | `SELECT, INSERT, UPDATE, DELETE` | query/change **data** |
| **DCL** (Control) | `GRANT, REVOKE` | **permissions** |
| **TCL** (Transaction) | `COMMIT, ROLLBACK, SAVEPOINT` | **transaction** boundaries |

> **Set-based, not row-based.** Unlike algebra (pure sets), SQL works on
> **multisets (bags)** — it can return **duplicate rows** unless you use
> `DISTINCT`. Remember this; it explains many "why did I get extra rows?" bugs.

> **`DELETE` vs `TRUNCATE` vs `DROP` (guaranteed exam question):**
> `DELETE` (DML) removes chosen rows, can have `WHERE`, is logged, **rollback-able**;
> `TRUNCATE` (DDL) removes **all** rows fast, no `WHERE`, resets identity;
> `DROP` (DDL) removes the **table itself** (structure + data).
>
> ⚠️ **TRUNCATE rollback is vendor-dependent:** in **Oracle/MySQL** it auto-commits
> (cannot be rolled back). In **PostgreSQL & SQL Server** it is **transactional** —
> you *can* roll it back inside a transaction. For a written exam the expected
> answer is usually "TRUNCATE can't be rolled back" (Oracle view); in an interview,
> state the vendor difference.

---

## 4.2 DDL — Defining Structure

```sql
CREATE TABLE student (
  roll     INT          PRIMARY KEY,
  name     VARCHAR(50)  NOT NULL,
  email    VARCHAR(80)  UNIQUE,
  cgpa     DECIMAL(3,1) CHECK (cgpa >= 0 AND cgpa <= 10),
  dept_id  INT          REFERENCES dept(id),
  active   BOOLEAN      DEFAULT TRUE
);

ALTER TABLE student ADD COLUMN phone VARCHAR(15);   -- add a column
ALTER TABLE student DROP COLUMN phone;              -- remove a column
DROP TABLE student;                                 -- remove table entirely
```

Common data types: `INT/BIGINT`, `DECIMAL(p,s)`/`NUMERIC`, `FLOAT`,
`CHAR(n)` (fixed) vs `VARCHAR(n)` (variable), `DATE/TIME/TIMESTAMP`,
`BOOLEAN`, `TEXT`.

> **`CHAR(n)` vs `VARCHAR(n)`:** `CHAR` is **padded** to a fixed length (good when
> values are all the same size, e.g. country codes); `VARCHAR` stores only what you
> put in (good for variable text). A frequent 1-marker.

---

## 4.3 DML — Inserting, Updating, Deleting

```sql
INSERT INTO student (roll, name, cgpa) VALUES (101, 'Asha', 8.7);
INSERT INTO toppers (roll, name)                 -- INSERT ... SELECT: bulk-copy
  SELECT roll, name FROM student WHERE cgpa >= 9; --   rows from a query
UPDATE student SET cgpa = 9.0 WHERE roll = 101;
DELETE FROM student WHERE cgpa < 5.0;
```

> **The most dangerous SQL mistake:** `UPDATE`/`DELETE` **without a `WHERE`** changes
> **every row**. `DELETE FROM student;` empties the whole table. Always write the
> `WHERE` first.

### DCL — controlling access (GRANT / REVOKE)

```sql
GRANT SELECT, INSERT ON student TO analyst;   -- give privileges
GRANT ALL PRIVILEGES ON student TO admin_user;
REVOKE INSERT ON student FROM analyst;         -- take them back
```

> **Principle of least privilege:** give each user/role only the rights it needs
> (e.g. a reporting account gets `SELECT` only). A frequent SEBI-IT security point.

### TCL — transaction boundaries (COMMIT / ROLLBACK / SAVEPOINT)

```sql
BEGIN;                                  -- start a transaction
UPDATE account SET bal = bal - 500 WHERE id = 1;
UPDATE account SET bal = bal + 500 WHERE id = 2;
SAVEPOINT after_debit;                   -- optional checkpoint
-- ROLLBACK TO after_debit;             -- undo to the savepoint
COMMIT;                                  -- make all changes permanent
-- ROLLBACK;                            -- or undo the WHOLE transaction
```

`COMMIT` makes changes permanent (durable); `ROLLBACK` undoes the transaction;
`SAVEPOINT` marks a point you can partially roll back to. *(Full transaction
theory — ACID, isolation, concurrency — is Module 9.)*

---

## 4.4 The SELECT Statement — Structure & Execution Order

This is the heart of SQL. The clauses are **written** in one order but
**executed** in another — understanding this removes 90% of beginner confusion.

![SELECT anatomy: the clauses SELECT/FROM/WHERE/GROUP BY/HAVING/ORDER BY/LIMIT, with their logical execution order numbered FROM→WHERE→GROUP BY→HAVING→SELECT→ORDER BY→LIMIT.](images/35_select_anatomy.png)

```sql
SELECT   dept, COUNT(*)        -- 5. choose/compute columns
FROM     student               -- 1. row source
WHERE    cgpa > 6              -- 2. filter rows
GROUP BY dept                  -- 3. form groups
HAVING   COUNT(*) > 5          -- 4. filter groups
ORDER BY dept                  -- 6. sort
LIMIT    10;                    -- 7. cut
```

**Logical execution order:** `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER
BY → LIMIT`.

![Flowchart of logical query processing: FROM/JOIN, then WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT — in that execution order.](images/43_fc_query_order.png)

> **Why this matters (classic interview question):** *"Can I use a column alias
> defined in SELECT inside the WHERE clause?"* **No** — `WHERE` runs **before**
> `SELECT`, so the alias doesn't exist yet. But you **can** use it in `ORDER BY`
> (which runs after `SELECT`). Mnemonic: **F-W-G-H-S-O-L**.

**Basic building blocks:**

```sql
SELECT DISTINCT city FROM student;        -- DISTINCT removes duplicate rows (like π)
SELECT * FROM student WHERE cgpa BETWEEN 6 AND 8;
SELECT * FROM student WHERE name LIKE 'A%';   -- pattern: % = any chars, _ = one char
SELECT * FROM student WHERE dept_id IN (1, 2, 3);
SELECT * FROM student WHERE email IS NULL;    -- never  = NULL
SELECT name, cgpa*10 AS percentage FROM student ORDER BY cgpa DESC;
```

> **Operators worth memorizing:** `BETWEEN a AND b` (inclusive), `IN (list)`,
> `LIKE` (`%` = any string, `_` = single char), `IS NULL`/`IS NOT NULL`,
> `AND/OR/NOT`. `ORDER BY col DESC` for descending.

---

## 4.5 Joins — Combining Tables

Joins are SQL's version of the algebra joins from Module 3. This is one of the
most heavily tested and most practically used topics.

![SQL joins: INNER (matching rows only), LEFT (all left + matched right), RIGHT (all right + matched left), FULL OUTER (all rows); plus CROSS and SELF joins, with a worked emp/dept example.](images/36_sql_joins.png)

| Join | Keeps | Algebra equivalent |
|------|-------|---------------------|
| **INNER JOIN** | only rows that **match** in both | theta/equi/natural join |
| **LEFT (OUTER) JOIN** | **all left** rows + matched right (NULLs if none) | left outer |
| **RIGHT (OUTER) JOIN** | **all right** rows + matched left | right outer |
| **FULL OUTER JOIN** | **all rows** from both, matched where possible | full outer |
| **CROSS JOIN** | every pair (no condition) | Cartesian product `×` |
| **SELF JOIN** | a table joined **to itself** (use aliases) | join on same table |

```sql
-- INNER: employees with their department name (unmatched dropped)
SELECT e.name, d.dname
FROM   emp e JOIN dept d ON e.dno = d.dno;

-- LEFT: ALL employees, even those with no department (dname = NULL)
SELECT e.name, d.dname
FROM   emp e LEFT JOIN dept d ON e.dno = d.dno;

-- SELF: each employee with their manager's name
SELECT e.name AS employee, m.name AS manager
FROM   emp e JOIN emp m ON e.mgr_id = m.eid;
```

> **Interview gold — find rows with NO match:** a `LEFT JOIN` + `WHERE
> right.key IS NULL` returns left rows that have **no** matching right row
> ("employees with no department", "customers with no orders"). This "anti-join"
> pattern comes up constantly.

**`NATURAL JOIN` and `USING` (GATE/SEBI favourite — and a real gotcha):**

```sql
SELECT * FROM emp NATURAL JOIN dept;     -- auto-joins on ALL same-named columns
SELECT * FROM emp JOIN dept USING (dno); -- join on the named common column(s)
```

- **`NATURAL JOIN`** automatically equi-joins on **every column with the same name**
  in both tables, and keeps **one** copy of each. It's the algebra natural join.
- ⚠️ **The gotcha:** if the tables happen to share an *unintended* same-named
  column (e.g. both have `created_at`), `NATURAL JOIN` silently joins on it too,
  giving **wrong results**. Prefer explicit `JOIN ... ON` or `USING(col)` in
  production. This is a classic PYQ "predict the output" trap.

> **Exam trap:** an INNER JOIN can return **more** rows than either table if the
> join column has duplicates (rows multiply), or **fewer** if many rows don't
> match. Never assume the count.

---

## 4.6 Aggregates, GROUP BY and HAVING

**Aggregate functions** collapse many rows into one value: `COUNT, SUM, AVG, MIN,
MAX`.

![Aggregate functions and NULL: COUNT(*) counts all rows including NULL; COUNT(col), SUM, AVG, MIN, MAX all ignore NULLs — so AVG = SUM/COUNT(non-null).](images/39_aggregates_null.png)

> **The NULL trap (asked everywhere):** all aggregates **except `COUNT(*)` ignore
> NULLs**. So `AVG(sal)` = `SUM(sal) / COUNT(sal)` (non-null count), **not** divided
> by the total number of rows. `COUNT(*)` counts every row; `COUNT(col)` counts only
> non-NULL values.

> **`COUNT(DISTINCT col)`** counts the number of **distinct non-NULL** values —
> e.g. `COUNT(DISTINCT dept)` = how many different departments. `SUM(DISTINCT …)`
> and `AVG(DISTINCT …)` exist too. A common PYQ and reporting pattern.

**GROUP BY** partitions rows into groups; the aggregate is computed **per group**.
**HAVING** then filters those groups.

![GROUP BY + HAVING: rows are grouped by a column, aggregates computed per group, then HAVING filters groups (whereas WHERE filtered individual rows before grouping).](images/37_groupby_having.png)

```sql
SELECT   dept, COUNT(*) AS n, AVG(sal) AS avg_sal
FROM     emp
WHERE    sal > 0          -- filter ROWS first
GROUP BY dept             -- then group
HAVING   COUNT(*) > 2     -- then filter GROUPS
ORDER BY avg_sal DESC;
```

| | **WHERE** | **HAVING** |
|---|-----------|------------|
| Filters | individual **rows** | **groups** |
| Runs | **before** GROUP BY | **after** GROUP BY |
| Aggregates allowed? | **No** | **Yes** |

> **The golden GROUP BY rule:** every column in `SELECT` that is **not** inside an
> aggregate **must** appear in `GROUP BY`. Otherwise it's ambiguous (which row's
> value would it show?). This is a guaranteed exam/interview point.

> **Why a SELECT alias usually can't be used in `HAVING`:** `HAVING` (step 4) runs
> **before** `SELECT` (step 5) in the execution order, so the alias doesn't exist
> yet — repeat the aggregate expression (`HAVING COUNT(*) > 2`) instead of its
> alias. (Same reason aliases fail in `WHERE`; they *do* work in `ORDER BY`.)

### 4.6A GROUP BY + HAVING vs WHERE — worked with sample output

Trace the exact clauses `WHERE → GROUP BY → HAVING` on real rows so you can see
each one act on a different thing (rows, then groups).

```text
emp
name | dept | sal
A    | HR   | 30
B    | HR   | 50
C    | HR   | 0        <- sal = 0
D    | IT   | 90
E    | IT   | 70
F    | FIN  | 60

Query:
  SELECT   dept, COUNT(*) AS n, AVG(sal) AS avg_sal
  FROM     emp
  WHERE    sal > 0          -- (1) drop ROWS first: removes C
  GROUP BY dept             -- (2) form groups
  HAVING   COUNT(*) >= 2    -- (3) drop GROUPS with < 2 members
  ORDER BY avg_sal DESC;

Step 1 (WHERE sal>0): rows kept = A,B,D,E,F   (C removed BEFORE grouping)
Step 2 (GROUP BY dept):
   HR  -> {A(30), B(50)}      n=2  avg=40
   IT  -> {D(90), E(70)}      n=2  avg=80
   FIN -> {F(60)}             n=1  avg=60
Step 3 (HAVING n>=2): FIN dropped (only 1 member)
Step 6 (ORDER BY avg_sal DESC):

Output:
  dept | n | avg_sal
  IT   | 2 | 80
  HR   | 2 | 40
```

> **The key contrast this makes concrete:** `WHERE` removed a *row* (C) **before**
> grouping — so C never even reaches its group's average. `HAVING` removed a whole
> *group* (FIN) **after** grouping. Put a row-level test in `WHERE`, a group-level
> (aggregate) test in `HAVING`. Note also HR's avg is `40`, computed over the two
> **surviving** rows — proof that `WHERE` ran first.

---

## 4.7 Subqueries (Nested Queries)

A **subquery** is a query inside another. Closure (Module 3) is what makes this
possible — a query returns a relation, which another query can use.

![Subqueries: non-correlated (inner runs once, independent) vs correlated (inner re-runs per outer row, references it); by result shape — scalar, row, table — used with =, IN, ANY, ALL, EXISTS.](images/38_subqueries.png)

**Non-correlated** — inner query runs **once**, independently:

```sql
SELECT name FROM emp
WHERE sal > (SELECT AVG(sal) FROM emp);     -- "above average"
```

**Correlated** — inner query references the outer row, so it **re-runs for each
outer row**:

```sql
SELECT name FROM emp e
WHERE sal > (SELECT AVG(sal) FROM emp WHERE dno = e.dno);   -- above own-dept average
```

**Worked (same data, both queries) — see the difference in the output:**

```text
emp
name | dno | sal
A    | 10  | 60
B    | 10  | 40
C    | 20  | 90
D    | 20  | 50

Non-correlated: sal > (SELECT AVG(sal) FROM emp)   -- global avg = 60
  inner runs ONCE  ->  60.  Keep rows with sal > 60:
  result = { C(90) }

Correlated: sal > (SELECT AVG(sal) FROM emp WHERE dno = e.dno)  -- per-dept avg
  inner RE-RUNS per outer row, using that row's dno:
    A: dept-10 avg = 50 -> 60 > 50 ✓
    B: dept-10 avg = 50 -> 40 > 50 ✗
    C: dept-20 avg = 70 -> 90 > 70 ✓
    D: dept-20 avg = 70 -> 50 > 70 ✗
  result = { A(60), C(90) }
```

> **The tell (how to spot a correlated subquery):** the inner query **references a
> column of the outer table** (here `e.dno`). That reference forces it to re-run
> per outer row, so it cannot be evaluated on its own. A non-correlated subquery
> has no such reference and could be run and cached once.

**By result shape & operators:**

- **Scalar** (1 row, 1 col) → use with `=, >, <`.
- **Column/Table** (many rows) → use with `IN`, `ANY`/`SOME`, `ALL`, `EXISTS`.

```sql
-- IN: employees in departments located in 'Mumbai'
SELECT name FROM emp WHERE dno IN (SELECT dno FROM dept WHERE city='Mumbai');

-- EXISTS: departments that HAVE at least one employee (correlated)
SELECT dname FROM dept d WHERE EXISTS (SELECT 1 FROM emp e WHERE e.dno = d.dno);
```

> **`IN` vs `EXISTS` vs `NOT IN`:** `EXISTS` stops at the first match (often faster
> for correlated checks). **`NOT IN` is dangerous with NULLs** — if the subquery
> returns any NULL, `NOT IN` yields no rows (because `x <> NULL` is UNKNOWN). Prefer
> `NOT EXISTS` for "anti" queries. (Recall NULL 3-valued logic from Module 3.)

> **Division in SQL** ("students who took **every** course") = **double `NOT
> EXISTS`** — there is no required course that the student has *not* taken. This is
> the SQL realization of algebra's `÷`.

### 4.7A The `NOT IN` + NULL trap and `EXISTS`/`NOT EXISTS` — worked

This is one of the most-tested and most-real SQL bugs. Watch a `NOT IN` return
**zero rows** the moment its subquery contains a single NULL.

![The NOT IN + NULL trap: NOT IN over a set containing NULL becomes (...) AND UNKNOWN, which is never TRUE, so WHERE keeps no rows.](images/146_not_in_null_trap.png)

```text
emp                       dept
name | dno                dno
A    | 10                 10
B    | 20                 NULL     <- dept table has a NULL dno
C    | 30

Goal: employees whose dno is NOT in dept.

BUGGY:  SELECT name FROM emp
        WHERE dno NOT IN (SELECT dno FROM dept);   -- {10, NULL}

Expand for employee C (dno=30):
   30 NOT IN (10, NULL)
 = 30<>10  AND  30<>NULL
 = TRUE    AND  UNKNOWN
 = UNKNOWN            -> WHERE keeps only TRUE, so C is dropped too.
Result: 0 rows   (even though C clearly should qualify)
```

Why: `x <> NULL` is **UNKNOWN** (three-valued logic — Module 3). `NOT IN` is an
`AND` of `<>` tests, and `anything AND UNKNOWN` can never be TRUE. So a single NULL
in the list poisons **every** row's result.

```text
CORRECT (NULL-safe) with NOT EXISTS:
  SELECT name FROM emp e
  WHERE NOT EXISTS (SELECT 1 FROM dept d WHERE d.dno = e.dno);
Result: { C }        -- correct

NOT EXISTS just asks "did any matching row appear?" (a plain yes/no), so a NULL in
dept.dno simply fails to match and is ignored — no UNKNOWN poisoning.
```

> **`EXISTS` vs `IN` performance:** both can be correct (when no NULLs), but
> `EXISTS` short-circuits at the **first** matching inner row, which is often
> cheaper for a correlated check. For **anti**-queries ("not in / no match"),
> **always reach for `NOT EXISTS`** — it is both NULL-safe and usually optimizer-friendly.

> **Quick NULL truth reminder (full tables in Module 3):** `NOT UNKNOWN =
> UNKNOWN`; `TRUE OR UNKNOWN = TRUE`; `FALSE AND UNKNOWN = FALSE`; everything else
> touching UNKNOWN stays UNKNOWN. `WHERE` and `HAVING` keep a row **only when the
> predicate is TRUE** — UNKNOWN behaves like FALSE for filtering, but *not* under
> `NOT` (that is the whole trap above).

---

## 4.8 Set Operations

![Set operations in SQL: UNION (combine, remove duplicates), UNION ALL (keep duplicates, faster), INTERSECT (common rows), EXCEPT/MINUS (in A not B).](images/40_set_ops_sql.png)

```sql
SELECT city FROM customer
UNION                       -- removes duplicates (sorts → costly)
SELECT city FROM supplier;

SELECT city FROM customer
UNION ALL                   -- keeps duplicates (faster, no sort)
SELECT city FROM supplier;
```

- **UNION** — combine, **remove duplicates**. **UNION ALL** — combine, **keep
  duplicates** (faster; use when duplicates are impossible or acceptable).
- **INTERSECT** — rows in both. **EXCEPT** (Oracle: **MINUS**) — rows in the first
  but not the second.
- All require the two queries to be **union-compatible** (same number of columns,
  compatible types).

> **Exam nugget:** `UNION` does extra work (sort + de-dup); `UNION ALL` is cheaper.
> If you *know* there are no duplicates, always prefer `UNION ALL`.

---

## 4.8A More Query Tools (ANY/ALL, CASE, LIMIT/OFFSET, Window Functions)

### ANY / ALL (with subqueries)

- **`> ALL (subquery)`** → greater than **every** value = greater than the **max**.
- **`> ANY (subquery)`** (a.k.a. `SOME`) → greater than **at least one** = greater
  than the **min**.

```sql
SELECT name FROM emp WHERE sal > ALL (SELECT sal FROM emp WHERE dno = 20);
   -- earns more than EVERY employee in dept 20  (i.e. > max of dept 20)
```

> **GATE trap:** `= ANY` is equivalent to `IN`; `<> ALL` is equivalent to `NOT IN`.

### CASE (conditional expression)

```sql
SELECT name,
  CASE WHEN cgpa >= 9 THEN 'A'
       WHEN cgpa >= 7 THEN 'B'
       ELSE 'C' END AS grade
FROM student;
```

`CASE` adds if-then-else logic inside `SELECT` (and even inside aggregates for
"conditional counting": `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`).

### LIMIT / OFFSET (pagination) and multi-key ORDER BY

```sql
SELECT * FROM student ORDER BY cgpa DESC, name ASC   -- tie-break by name
LIMIT 10 OFFSET 20;     -- rows 21–30 (page 3 of size 10)
```

`ORDER BY a, b` sorts by `a`, breaking ties with `b`. `LIMIT n OFFSET m` is the
standard **pagination** pattern. (Use `NULLS FIRST/LAST` to control where NULLs
sort.)

### Window functions (interview-tier — beyond core GATE, but FAANG-frequent)

A **window function** computes a value **across a set of rows related to the
current row**, *without collapsing them into one row* (unlike `GROUP BY`).

```sql
SELECT name, dept, sal,
       RANK()       OVER (PARTITION BY dept ORDER BY sal DESC) AS rnk,
       ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sal DESC) AS rn
FROM emp;
```

- `PARTITION BY` = the groups; `ORDER BY` = ordering within each group.
- `ROW_NUMBER()` → 1,2,3… (unique). `RANK()` → ties share a rank, then skips
  (1,1,3). `DENSE_RANK()` → ties share, no skip (1,1,2).

> **The famous "Nth highest salary" interview question:** wrap the window query and
> filter `WHERE rnk = 2` (use `DENSE_RANK` if ties should count as one salary).
> This is the modern, clean answer; the older way is a nested subquery (§4.15).

**Worked — ranking and a running total on the same data:**

```text
emp
name | dept | sal
A    | IT   | 90
B    | IT   | 90       <- tie with A
C    | IT   | 70
D    | HR   | 50

SELECT name, dept, sal,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY sal DESC) AS rn,
  RANK()       OVER (PARTITION BY dept ORDER BY sal DESC) AS rnk,
  DENSE_RANK() OVER (PARTITION BY dept ORDER BY sal DESC) AS drnk,
  SUM(sal)     OVER (PARTITION BY dept ORDER BY sal DESC) AS running
FROM emp;

Output:
 name|dept|sal| rn |rnk|drnk|running
  A  | IT | 90|  1 | 1 |  1 |  180   <- 90+90 (both tied rows in this frame)
  B  | IT | 90|  2 | 1 |  1 |  180
  C  | IT | 70|  3 | 3 |  2 |  250   <- 180+70
  D  | HR | 50|  1 | 1 |  1 |   50   <- HR partition restarts
```

- `ROW_NUMBER` always gives distinct `1,2,3` (tie broken arbitrarily).
- `RANK` gives `1,1,3` (ties share, then **skips**); `DENSE_RANK` gives `1,1,2`
  (ties share, **no skip**).
- `SUM(...) OVER (... ORDER BY ...)` is a **running total** within each partition;
  tied rows share the same cumulative value. Drop the `ORDER BY` inside `OVER` and
  `SUM` becomes a **whole-partition total** on every row instead.

## 4.9 Constraints

Constraints enforce data integrity at the schema level (the SQL realization of
Module 3's integrity rules).

![SQL constraints: NOT NULL, UNIQUE, PRIMARY KEY (= UNIQUE + NOT NULL, one per table), FOREIGN KEY (references a PK), CHECK (condition), DEFAULT (fallback value).](images/41_constraints_sql.png)

| Constraint | Enforces |
|------------|----------|
| `NOT NULL` | value must be present |
| `UNIQUE` | no duplicates (NULLs allowed) |
| `PRIMARY KEY` | `UNIQUE + NOT NULL`, **one per table** |
| `FOREIGN KEY ... REFERENCES` | must match a PK in another table (referential integrity) |
| `CHECK (condition)` | value must satisfy a condition |
| `DEFAULT value` | value used when none is supplied |

```sql
FOREIGN KEY (dept_id) REFERENCES dept(id) ON DELETE CASCADE;
```

> Recall from Module 3: `ON DELETE CASCADE / SET NULL / RESTRICT` control what
> happens to child rows when a parent is deleted.

---

## 4.10 Views

![Views: a CREATE VIEW makes a virtual table from a query (e.g. hiding the ssn column); virtual views recompute each use, materialized views store the result on disk.](images/42_views.png)

A **view** is a **stored query** that you can use like a table.

```sql
CREATE VIEW pub_emp AS
SELECT name, dept FROM employee;     -- hides salary, ssn
SELECT * FROM pub_emp WHERE dept = 'CSE';   -- query it like a table
```

**Why views matter:**
- **Security** — expose only certain columns/rows (hide `salary`, `ssn`).
- **Simplicity** — name a complex join once, reuse it.
- **Logical data independence** (Module 1) — the base tables can change while the
  view's interface stays stable.

**Virtual vs Materialized:**
- **Virtual view** (default) — not stored; recomputed every time it's queried
  (always fresh).
- **Materialized view** — the result is **stored on disk** (fast reads), but must
  be **refreshed** and can be **stale**.

> **Updatable views:** you can `INSERT/UPDATE` through a view only if it maps
> cleanly to **one** base table — **no** aggregates, `GROUP BY`, `DISTINCT`, or
> joins. A common exam/interview question.

---

## 4.11 Indexes, Triggers, Procedures (overview)

**Index** — a structure that speeds up lookups (`CREATE INDEX idx ON emp(dno);`).
It makes reads faster but writes slightly slower and uses extra space. *(Full
internals — B+ trees, hashing — are Module 7.)*

**Trigger** — code that runs **automatically** on an `INSERT/UPDATE/DELETE` event.

![Triggers: an event (INSERT/UPDATE/DELETE) at a timing (BEFORE/AFTER/INSTEAD OF) fires the trigger body — e.g. write an audit row; NEW/OLD hold the new and old row values.](images/44_triggers.png)

```sql
CREATE TRIGGER audit_sal AFTER UPDATE ON emp
FOR EACH ROW
INSERT INTO audit(eid, old_sal, new_sal) VALUES (OLD.eid, OLD.sal, NEW.sal);
```

- **Event:** INSERT / UPDATE / DELETE. **Timing:** BEFORE / AFTER / INSTEAD OF.
- `NEW`/`OLD` refer to the new and old row values.
- Uses: **audit logs**, complex validation, auto-maintaining derived columns.

**Stored procedure** — a named block of SQL you **call explicitly**
(`CALL my_proc(...)`).

> **Trigger vs Stored Procedure (interview):** a **trigger** fires
> **automatically** on an event; a **stored procedure** runs only when you
> **call** it.

**Cursor** — a mechanism to process a query result **row by row** (procedural).
Avoid when a set-based query works — cursors are slow.

---

## 4.12 Real-World & Backend Perspectives

- **`EXPLAIN`/`EXPLAIN ANALYZE`** shows the query plan (the algebra tree + chosen
  joins/indexes). Reading it is the core skill of SQL performance tuning.
- **The N+1 query problem:** running one query per row in a loop instead of a
  single join — a top backend performance bug. Fix with a `JOIN` or `IN`.
- **Indexes** make `WHERE`/`JOIN`/`ORDER BY` fast; the optimizer uses them
  automatically. Over-indexing slows writes.
- **Parameterized queries** (not string concatenation) prevent **SQL injection** —
  a critical security practice (see §4.14).

---

## 4.13 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes**
- `UPDATE`/`DELETE` **without `WHERE`** (changes all rows).
- Using `= NULL` instead of `IS NULL`.
- Putting an aggregate in `WHERE` (must be `HAVING`).
- Forgetting non-aggregated SELECT columns must be in `GROUP BY`.
- Assuming `UNION` keeps duplicates (it doesn't — `UNION ALL` does).
- `NOT IN` with a subquery that can return NULL (returns nothing) — use `NOT
  EXISTS`.
- Expecting a column alias to work in `WHERE` (it runs before SELECT).

**Edge cases**
- `COUNT(*)` vs `COUNT(col)` differ when NULLs exist.
- An INNER JOIN on a duplicated key **multiplies** rows.
- `CROSS JOIN` / a join with a missing `ON` becomes a Cartesian product (row
  explosion).
- `NULL` in `GROUP BY` forms its **own** group.

**Tradeoffs**

| Strength | Cost |
|----------|------|
| Declarative — optimizer finds fast plans | accidental Cartesian products / N+1 are easy to write |
| Powerful joins/aggregation/subqueries | complex queries get hard to read |
| Constraints enforce integrity | add write-time overhead |

---

## 4.14 Security — SQL Injection (must-know)

**SQL injection** happens when user input is concatenated directly into a query:

```sql
-- VULNERABLE: if user types  ' OR '1'='1
"SELECT * FROM users WHERE name = '" + input + "'"
   → SELECT * FROM users WHERE name = '' OR '1'='1'   -- returns everyone!
```

**Fix:** use **parameterized queries / prepared statements** (the driver sends
data separately from code), grant least-privilege DB accounts, and validate
input. This is the **#1 web vulnerability** historically and a frequent SEBI-IT /
interview topic.

### 4.14A Parameterized queries — how they actually stop injection

The core idea: **send the SQL text and the user data over separate channels**, so
the input can never be *parsed as code*. The query is compiled (prepared) once with
`?`/`$1` placeholders; the driver then binds each value as a pure data literal.

```text
VULNERABLE (string-built):  the input becomes part of the SQL text -> parsed as code
  "... WHERE name = '" + input + "'"

SAFE (parameterized):       the ? is a data slot -> input is never parsed as SQL
```

```sql
-- Prepared/parameterized (placeholders vary by driver: ?, $1, :name)
PREPARE q AS SELECT * FROM users WHERE name = $1;   -- SQL fixed & compiled first
EXECUTE q('  '' OR ''1''=''1  ');   -- the whole string is one literal value
   -- searches for a user literally named  ' OR '1'='1  -> returns nobody
```

With a placeholder, `' OR '1'='1` is treated as **the value to compare**, not as
extra SQL — the `OR` never becomes an operator, so the attack collapses.

**Defense-in-depth (state these together in an interview):**

| Layer | What it does |
|-------|--------------|
| **Parameterized / prepared statements** | the primary fix — data can't become code |
| **Stored procedures (with bound params)** | same benefit *if* they don't build dynamic SQL internally |
| **Least-privilege DB account** | a compromised query can't `DROP`/read other tables |
| **Input validation / allow-lists** | reject obviously bad input early (defense in depth, not a substitute) |
| **ORMs / query builders** | parameterize by default — but raw-SQL escape hatches re-open the risk |

> **Interview trap:** "Isn't *escaping* the input enough?" — Escaping is fragile
> (easy to miss a spot, charset edge cases). **Parameterized queries are the
> correct, complete fix**; escaping is a fallback only where placeholders truly
> can't be used (e.g. a dynamic table/column name — which should then be checked
> against an allow-list, never bound as a parameter).

---

## 4.15 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** predict the output of a query; WHERE vs HAVING; GROUP BY
rules; join results & counts; correlated vs non-correlated subqueries; aggregate +
NULL behaviour; UNION vs UNION ALL; DDL/DML/DCL/TCL; DELETE vs TRUNCATE vs DROP;
constraint identification.

**Interview:** "Find the 2nd highest salary" (subquery / `LIMIT OFFSET` /
window function); "customers with no orders" (LEFT JOIN ... IS NULL / NOT EXISTS);
"WHERE vs HAVING"; "what is a correlated subquery"; "how do you prevent SQL
injection"; "INNER vs LEFT JOIN".

**Coding (try in PostgreSQL):**
- 2nd highest salary: `SELECT MAX(sal) FROM emp WHERE sal < (SELECT MAX(sal) FROM
  emp);`
- Department-wise average, only depts with >2 employees: a `GROUP BY ... HAVING`.
- Anti-join: customers with no orders via `LEFT JOIN ... WHERE o.id IS NULL`.

---

## 4.16 Concept Checks & MCQs

1. Which runs first: `WHERE` or `SELECT`? → **WHERE**.
2. Aggregate in a row filter → must use ___ not WHERE → **HAVING**.
3. `COUNT(*)` vs `COUNT(col)` differ when ___ → **NULLs exist** (col has NULLs).
4. `UNION` vs `UNION ALL`: which removes duplicates? → **UNION**.
5. `DELETE` vs `TRUNCATE`: which can be rolled back? → **DELETE** always; **TRUNCATE
   is vendor-dependent** (rolls back in PostgreSQL/SQL Server, not in Oracle/MySQL).
6. A LEFT JOIN + `WHERE right.key IS NULL` finds ___ → **left rows with no match**.
7. Subquery that re-runs per outer row is ___ → **correlated**.
8. To prevent SQL injection use ___ → **parameterized / prepared statements**.
9. Can a SELECT alias be used in WHERE? → **No** (in ORDER BY → yes).
10. Updatable view requires ___ → **maps to one base table** (no agg/join/distinct).
11. `> ALL (subquery)` means greater than the ___ → **maximum**. `> ANY` → **minimum**.
12. `= ANY` is equivalent to ___ ; `<> ALL` to ___ → **IN** ; **NOT IN**.
13. Which gives 1,1,3 for ties: RANK or DENSE_RANK? → **RANK** (DENSE_RANK gives 1,1,2).
14. `GRANT`/`REVOKE` belong to which family? → **DCL**. `COMMIT`/`ROLLBACK`? → **TCL**.
15. Page 3 of size 10 → `LIMIT 10 OFFSET ___` → **20**.
16. `NATURAL JOIN` joins on ___ → **all columns with the same name** (keeps one copy).
17. `COUNT(DISTINCT dept)` returns ___ → **number of distinct non-NULL departments**.
18. Can a SELECT alias be used in HAVING? → **No** (HAVING runs before SELECT).
19. `dno NOT IN (SELECT dno FROM dept)` returns no rows even for valid data. Why? → the subquery contains a **NULL**, so `NOT IN` yields **UNKNOWN** for every row; use **NOT EXISTS**.
20. In `... WHERE sal > (SELECT AVG(sal) FROM emp WHERE dno = e.dno)`, the subquery runs ___ → **once per outer row** (it's **correlated** via `e.dno`).
21. `WHERE` removes rows ___ grouping; `HAVING` removes groups ___ grouping → **before** / **after**.
22. `SUM(sal) OVER (PARTITION BY dept ORDER BY sal)` computes a ___ → **running (cumulative) total** per department.
23. The primary defense against SQL injection is ___ → **parameterized / prepared statements** (input sent as data, not code).
24. For an aggregate over rows with NULLs, `AVG(sal)` divides `SUM(sal)` by ___ → the count of **non-NULL** sal values.

**True/False**
- `AVG(col)` divides by the number of rows including NULLs. → **False** (ignores NULLs).
- `TRUNCATE` is DML. → **False** (DDL).
- `HAVING` can use aggregate functions. → **True**.
- A column alias defined in SELECT can be used in HAVING (most DBs). → Often **False**; use the aggregate expression.

**Scenario / output prediction**
> `emp(name, dno)` has rows (A,10)(B,10)(C,20)(D,NULL).
> `SELECT dno, COUNT(*) FROM emp GROUP BY dno;` →
> `(10,2) (20,1) (NULL,1)`. NULL forms its **own** group; COUNT(*) counts the row.

---

## 4.17 One-Page Revision Sheet

```
SQL = declarative; works on MULTISETS (dups allowed unless DISTINCT).
SUBLANGUAGES: DDL(create/alter/drop/truncate) DML(select/insert/update/delete)
              DCL(grant/revoke) TCL(commit/rollback/savepoint)
DELETE(DML,WHERE,rollback) | TRUNCATE(DDL,all,fast,no rollback) | DROP(DDL,kills table)

EXECUTION ORDER (F-W-G-H-S-O-L):
  FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT
  (alias works in ORDER BY, NOT in WHERE — SELECT runs after WHERE)

WHERE filters ROWS (before group, no aggregates) | HAVING filters GROUPS (after, aggregates ok)
GROUP BY rule: every non-aggregated SELECT col must be in GROUP BY

JOINS: INNER(matches) LEFT(all left+NULL) RIGHT(all right) FULL(all)
  CROSS(cartesian) SELF(alias). NATURAL(auto on same-named cols, keep 1 copy; gotcha!)
  USING(col). Anti-join: LEFT JOIN ... WHERE r.key IS NULL.

AGGREGATES: COUNT(*) counts ALL rows; COUNT(col)/SUM/AVG/MIN/MAX ignore NULL.
  AVG = SUM/COUNT(non-null).

SUBQUERY: non-correlated(once) vs correlated(per outer row).
  scalar(=,>) | many-row(IN/ANY/ALL/EXISTS). NOT IN + NULL = empty -> use NOT EXISTS.
  division ("for all") = double NOT EXISTS.

SET OPS: UNION(dedup) UNION ALL(keep dups,faster) INTERSECT EXCEPT/MINUS. union-compatible.

ANY/ALL: >ALL = > max ; >ANY = > min ; =ANY = IN ; <>ALL = NOT IN.
CASE = if-then-else in SELECT. LIMIT n OFFSET m = pagination. ORDER BY a,b = tie-break.
WINDOW FN (interview): RANK/ROW_NUMBER/DENSE_RANK OVER(PARTITION BY.. ORDER BY..);
  ROW_NUMBER=unique; RANK=ties skip(1,1,3); DENSE_RANK=ties no skip(1,1,2). "Nth highest".
DCL: GRANT/REVOKE (least privilege). TCL: BEGIN/COMMIT/ROLLBACK/SAVEPOINT (ACID->M9).

CONSTRAINTS: NOT NULL | UNIQUE(nulls ok) | PRIMARY KEY(unique+not null,1/table)
  | FOREIGN KEY(refs PK, ON DELETE CASCADE/SET NULL) | CHECK | DEFAULT

VIEW = stored query (security/simplicity/independence). virtual(recompute) vs
  materialized(stored, refresh). updatable only if maps to ONE table.

TRIGGER = auto on event(INSERT/UPDATE/DELETE), timing BEFORE/AFTER, NEW/OLD.
  vs PROCEDURE = called explicitly. CURSOR = row-by-row (slow).

SECURITY: SQL injection -> use PARAMETERIZED / PREPARED statements.
```

### Flash cards

| Front | Back |
|-------|------|
| WHERE vs HAVING? | WHERE = rows (pre-group); HAVING = groups (post-group, aggregates) |
| Execution order? | FROM-WHERE-GROUP-HAVING-SELECT-ORDER-LIMIT |
| COUNT(*) vs COUNT(col)? | * counts all rows; col ignores NULLs |
| UNION vs UNION ALL? | UNION de-dups; UNION ALL keeps dups (faster) |
| Find "no match" rows? | LEFT JOIN + WHERE right IS NULL (or NOT EXISTS) |
| Correlated subquery? | Inner re-runs per outer row, references it |
| Prevent SQL injection? | Parameterized / prepared statements |
| TRUNCATE vs DELETE? | DELETE=DML,WHERE,rollback; TRUNCATE=DDL,all,fast (rollback vendor-dependent) |
| Updatable view needs? | Maps to one table, no agg/join/distinct |
| Trigger vs procedure? | Trigger auto on event; procedure called explicitly |

### Spaced repetition
- **24-hour:** write 10 queries (join, group+having, correlated subquery, anti-join).
- **7-day:** predict output of 10 tricky queries (NULLs, UNION, GROUP BY).
- **30-day:** solve "2nd highest salary", "dept-wise top earner", "customers with no
  orders", "students who took every course" from scratch.

---

## 4.18 Summary

SQL is the **declarative** language that turns relational algebra into something
you type. We covered the four sub-languages (**DDL/DML/DCL/TCL**), the all-important
**SELECT** with its **logical execution order** (`FROM→WHERE→GROUP BY→HAVING→
SELECT→ORDER BY→LIMIT`), every **join** (inner/left/right/full/cross/self and the
anti-join pattern), **aggregates + GROUP BY/HAVING** with the **NULL** rules,
**subqueries** (correlated vs non-correlated, and division via double `NOT
EXISTS`), **set operations** (UNION vs UNION ALL), **constraints**, **views**
(virtual vs materialized), and **triggers/procedures/cursors**. Finally we covered
the production essentials — `EXPLAIN`, the N+1 problem, and **SQL injection**
defense.

Every feature ties back to Module 3's algebra: `WHERE` = σ, `SELECT cols` = π,
`JOIN` = ⋈, `UNION/EXCEPT` = set ops, `GROUP BY` = aggregation. Next, **Module 5 —
Normalization** uses functional dependencies and keys to design schemas these
queries run against without redundancy.

> **You have mastered this module when** you can: write a multi-table query with
> `GROUP BY/HAVING` and a correlated subquery; explain the execution order and why
> aliases fail in WHERE; produce the "no-match" and "every-Y" patterns; predict a
> query's output with NULLs and GROUP BY; and explain SQL injection defense — all
> without notes.
