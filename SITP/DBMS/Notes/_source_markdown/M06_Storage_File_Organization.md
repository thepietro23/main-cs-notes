---
title: "Module 6 — Storage & File Organization"
subtitle: "DBMS Mastery: SEBI IT / RBI / GATE / Interview — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 6 — Storage & File Organization

> **Where this module sits.**
> Modules 2–5 were the *design* half (ER → relational → SQL → normalization). Now
> we go **under the floor**: where do tables physically live, and why is disk the
> villain of database performance? Everything about indexing (Module 7), query
> processing (Module 8), and recovery (Module 10) is shaped by one brutal fact —
> **disk is ~100,000× slower than RAM**. This module explains the hardware, how
> records are packed into blocks, the file-organization choices, **RAID**, and the
> **buffer manager** that hides disk latency. GATE loves the **disk-access-time**
> and **RAID** numericals.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★    | ★★        | ★★★     |

**Most-asked PYQ concepts (SEBI / RBI / GATE):** **disk access time** (seek +
rotational latency + transfer) numericals; **RAID levels** (min disks, usable
space, fault tolerance, RAID 0/1/5/6/10); **blocking factor** & number-of-blocks
calculations; **spanned vs unspanned**; **file organization** (heap vs sequential
vs hashed vs clustered); **buffer replacement** (LRU); primary vs secondary
storage (volatile vs non-volatile).

---

## 6.1 The Memory Hierarchy — Why Disk Is the Enemy

### Motivation (first principles)

A CPU can execute a billion instructions per second, but if it must wait ~10 ms
for a disk read, it wastes ~**10 million** instruction-cycles per read
(10⁹ /s × 0.01 s = 10⁷). The entire field of database storage exists to **avoid
touching the disk** — and when we must, to touch it **as few times and as
sequentially as possible.**

![The memory hierarchy pyramid: registers, cache, RAM (volatile) → SSD, disk, tape (non-volatile); faster/smaller/costlier at the top.](images/57_memory_hierarchy.png)

| Level | Speed | Size | Volatile? |
|-------|-------|------|-----------|
| **Registers** | ~1 ns | <1 KB | yes |
| **Cache (L1/L2/L3)** | ~1–10 ns | KB–MB | yes |
| **Main memory (RAM)** | ~100 ns | GB | **yes (volatile)** |
| **SSD (flash)** | ~100 µs | TB | no |
| **Magnetic disk (HDD)** | ~10 ms | TB | no |
| **Tape / archive** | seconds | PB | no |

> **The two great divides:**
> - **Volatile vs non-volatile:** RAM and above **lose data on power loss**; SSD/HDD
>   **persist**. This is *why* a database must write to disk to be **durable** (the
>   D in ACID) and why recovery (Module 10) exists.
> - **Primary (directly CPU-addressable: registers/cache/RAM)** vs **secondary
>   (disk/SSD)** vs **tertiary (tape)** storage.

> **The cost ratio that drives everything:** a RAM access (~100 ns) vs a disk
> access (~10 ms) is a **~100,000×** difference. Database performance ≈ "how often
> did we avoid the disk."

---

## 6.2 Magnetic Disk Geometry

Even in the SSD era, exams (and the cost model of query optimization) are taught on
**magnetic disks** because their access cost is easy to reason about.

![Disk geometry: platters, concentric tracks, sectors (arcs), a cylinder (same track across platters), spindle, and the read/write head on a moving arm.](images/58_disk_geometry.png)

| Term | Meaning |
|------|---------|
| **Platter** | a circular disk surface (data on both sides) |
| **Track** | one concentric ring on a platter |
| **Sector** | an arc of a track — the **smallest addressable unit** (e.g. 512 B / 4 KB) |
| **Cylinder** | the **same track on all platters** (readable with **no arm movement**) |
| **Read/write head** | floats just above the surface, on a moving **arm** |
| **Block / Page** | the DBMS's I/O unit — a group of contiguous sectors |

> **Key insight:** the DBMS never reads a single byte or row from disk — it reads a
> whole **block (page)**, typically **4–16 KB**. A **block is an integer multiple
> of the sector size** (e.g. 8 × 512 B sectors = a 4 KB block; the OS/DBMS chooses
> how many sectors form a block). So "how many **block accesses**?" is *the* cost
> metric, not "how many bytes". Storing related data in the **same block / same
> cylinder** minimizes expensive arm movement.

---

## 6.3 Disk Access Time (the GATE numerical)

The time to read a block has three parts. **Memorize the breakdown** — it is asked
almost every year.

![Disk access time = seek time (move arm to track) + rotational latency (wait for sector) + transfer time (read bytes).](images/59_disk_access_time.png)

1. **Seek time** — move the arm to the correct **track**. Mechanical, the
   **largest** component (~3–10 ms).
2. **Rotational latency** — wait for the desired **sector** to rotate under the
   head. **Average = ½ of one full rotation.**
3. **Transfer time** — time to actually read the bytes as they pass the head.

```
Average rotational latency = (1/2) × (60 / RPM)  seconds
Transfer time              = data size / transfer rate
Total access time          = seek + rotational latency + transfer (+ controller overhead)
```

> **Worked example:** disk at **6000 RPM**. One rotation = `60/6000 = 0.01 s = 10
> ms`. Average rotational latency = `10/2 = 5 ms`. If seek = 4 ms and transfer = 1
> ms, **total ≈ 4 + 5 + 1 = 10 ms** for that block.

> **Why sequential beats random:** reading 100 blocks scattered across the disk
> pays 100 seeks; reading 100 **contiguous** blocks pays ~**one** seek. This is why
> databases prize **sequential I/O** and why a full scan can beat random index
> lookups when many rows match.

---

## 6.4 RAID — Redundant Array of Independent Disks

**RAID** combines multiple physical disks into one logical unit for **speed**
(parallelism), **reliability** (redundancy), or both. **RAID is for availability,
NOT a backup** — it won't save you from an accidental `DELETE` or corruption.

### RAID 0 (striping) and RAID 1 (mirroring)

![RAID 0 stripes data across disks for speed with no redundancy; RAID 1 mirrors every block on a second disk for fault tolerance.](images/60_raid_0_1.png)

- **RAID 0 — Striping:** data split across disks → **parallel I/O (fastest)**, but
  **no redundancy** — *any* disk failure loses *all* data. Min **2** disks, **100%**
  usable.
- **RAID 1 — Mirroring:** every block copied on a second disk → survives **1**
  failure, fast reads. Min **2** disks, **50%** usable.

### RAID 5 and 6 (parity) — and how parity works

![RAID 5 distributes parity blocks across all disks; parity is computed with XOR, so a lost block is rebuilt from the surviving blocks plus parity.](images/61_raid_5_6.png)

- **RAID 5 — Striping + distributed parity:** one **parity** block per stripe,
  **rotated** across disks (no single parity bottleneck). Survives **1** disk
  failure. Min **3** disks, usable = **(n−1)/n**.
- **RAID 6 — Two parities:** survives **2** simultaneous failures. Min **4** disks,
  usable = **(n−2)/n**.

> **How XOR parity recovers data (a favourite exam point):**
> `P = A1 ⊕ A2 ⊕ A3`. If the disk holding `A3` dies, rebuild it:
> `A3 = A1 ⊕ A2 ⊕ P`. XOR is its own inverse, so any one missing block is
> recoverable from the rest. **Write penalty:** every write must also update parity
> (read-modify-write), so RAID 5/6 writes are slower than reads.

> **Why RAID 5 *rotates* parity — the RAID 4 baseline (GATE point):** **RAID 4** is
> block-level striping with **one dedicated parity disk**. Because *every* write
> must update that single parity disk, it becomes a **write bottleneck**. **RAID 5
> fixes this by distributing (rotating) the parity across all disks** — no single
> disk is the parity hotspot. (RAID 2 = bit-level/Hamming and RAID 3 = byte-level
> with dedicated parity are obsolete — know that they exist, but 0/1/5/6/10 are
> what's used and tested.)

### Comparison & RAID 10

![RAID comparison table: levels 0/1/5/6/10 with technique, minimum disks, usable space, fault tolerance, and best-use.](images/62_raid_comparison.png)

| RAID | Technique | Min disks | Usable | Survives | Best for |
|------|-----------|:---------:|:------:|:--------:|----------|
| **0** | striping | 2 | 100% | nothing | raw speed |
| **1** | mirroring | 2 | 50% | 1 disk | critical data |
| **5** | stripe + 1 parity | 3 | (n−1)/n | 1 disk | read-heavy, balanced |
| **6** | stripe + 2 parity | 4 | (n−2)/n | 2 disks | high availability |
| **10 (1+0)** | mirror then stripe | 4 | 50% | 1 per mirror | speed **and** safety |

> **Exam nuggets:** RAID 0 = no fault tolerance (despite the "0"). RAID 1 = 50%
> overhead. RAID 5 needs **≥3** disks; RAID 6 needs **≥4**. RAID 10 (a.k.a. 1+0) is
> the go-to for databases needing both performance and redundancy.

### RAID read/write performance & the RAID-5 write penalty (worked)

The comparison table above covers capacity and fault tolerance. Exams and interviews
also ask about **relative read/write speed** — and this is where RAID 5's famous
**write penalty** appears.

| RAID | Read speed | Write speed | Why |
|------|-----------|-------------|-----|
| **0** | **fastest** (n-way parallel) | **fastest** (n-way parallel) | no redundancy work |
| **1** | fast (read from either copy) | ~1 disk (write **both** mirrors) | mirror write in parallel |
| **5** | fast (stripe, n−1 data disks) | **slow — 4 I/Os per small write** | read-modify-write parity |
| **6** | fast | **slower — 6 I/Os per small write** | **two** parities to update |
| **10** | fast (stripe + pick a mirror) | fast (stripe, mirror in parallel) | no parity math |

> **The RAID-5 write penalty, step by step.** To change **one** data block you must
> keep parity correct. Using the XOR identity `P_new = P_old ⊕ D_old ⊕ D_new`, a
> single small (sub-stripe) write costs **4 physical I/Os**:
>
> ```text
> 1. READ  the old data block   D_old
> 2. READ  the old parity block P_old
> 3. WRITE the new data block   D_new
> 4. WRITE the new parity block P_new = P_old ⊕ D_old ⊕ D_new
> ```
>
> So one logical write = **2 reads + 2 writes = 4 I/Os** (RAID 5), or **3 reads + 3
> writes = 6 I/Os** (RAID 6, two parities). This is why **RAID 5/6 are chosen for
> read-heavy** workloads and **RAID 10** (no parity math, ~2 I/Os per write) for
> **write-heavy** databases.

> **Worked numerical:** an application issues **100 small random writes/second** to a
> RAID 5 array. Physical I/O load = `100 × 4 = 400 I/Os/s` on the array (vs `100 × 2
> = 200 I/Os/s` on RAID 10). If each disk sustains ~100 IOPS, RAID 5 needs the
> array to absorb 400 I/Os — the extra parity traffic is the hidden cost the "usable
> capacity" number never shows.

---

## 6.5 Records & Blocking

### Record types

- **Fixed-length records:** every record the same size → record *i* lives at offset
  `i × size` (easy, fast). Wastes space when fields vary.
- **Variable-length records:** fields vary (`VARCHAR`, optional/repeating fields) →
  need **length prefixes**, **delimiters**, or an **offset table**. Compact but
  harder to navigate.

### Blocking factor (the calculation)

![Records and blocking: fixed vs variable length, blocking factor = block size / record size, and spanned vs unspanned records.](images/63_records_blocking.png)

The **blocking factor** (`bfr`) = how many records fit in one block:

```
bfr = floor( Block size / Record size )          (unspanned)
Number of blocks to store r records = ceil( r / bfr )
```

> **Worked example:** Block = 4096 B, Record = 128 B → `bfr = floor(4096/128) = 32`
> records/block. To store 1,000 records: `ceil(1000/32) = 32` blocks.

### Spanned vs unspanned

- **Unspanned:** a record **never crosses** a block boundary. Leftover space at the
  block's end is **wasted**, but access is simple. (Used when records < block.)
- **Spanned:** a record **may cross** block boundaries (with a pointer to the
  continuation). **No wasted space**, and **required** when a record is *larger*
  than a block.

> **Exam trap:** with **unspanned** blocking, `bfr = floor(B/R)` and the leftover
> `B − (bfr × R)` bytes per block are wasted. With **spanned**, there's essentially
> no waste but you pay pointer-chasing overhead.

### Worked example — unspanned vs spanned block counts (side by side)

> *Given:* Block `B = 1024 B`, Record `R = 300 B`, `r = 10` records. Compare.

**Unspanned** (record never crosses a boundary):

```text
bfr        = floor(B/R)  = floor(1024/300) = floor(3.41) = 3 records/block
#blocks    = ceil(r/bfr) = ceil(10/3)      = 4 blocks
wasted/blk = B − bfr×R   = 1024 − 3×300    = 124 bytes wasted per block
```

**Spanned** (records packed end-to-end, splitting across blocks as needed):

```text
total data = r × R = 10 × 300 = 3000 bytes
#blocks    = ceil(total / B) = ceil(3000 / 1024) = ceil(2.93) = 3 blocks
```

> **Takeaway:** spanned stored the same 10 records in **3 blocks** vs unspanned's
> **4** — it reclaimed the 124 wasted bytes/block, at the cost of pointer-chasing
> when a record straddles a boundary. (Ignoring block-header/pointer overhead, which
> a strict GATE question may add.)

---

## 6.6 File Organization

A **file organization** is how a table's records are arranged in its data file.
Each choice optimizes a different access pattern.

![File organization methods: heap (unordered, fast insert), sequential (ordered, binary search), hashed (O(1) point lookup), clustered (related tables stored together for joins).](images/64_file_organization.png)

| Organization | How | Search | Insert | Best for |
|--------------|-----|--------|--------|----------|
| **Heap (unordered)** | append at end, no order | **O(n)** full scan | **O(1)** fast | bulk loads, small tables |
| **Sequential (ordered)** | sorted by a key | **O(log n)** binary search | costly (keep order / overflow) | range queries, sorted scans |
| **Hashed** | bucket = `hash(key)` | **O(1)** avg (equality) | O(1) avg | point lookups by key |
| **Clustered** | related rows of 2+ tables stored together | fast on cluster key | complex | frequent **joins** |

> **How to choose (decision):**
> - Many inserts / no search pattern → **heap**.
> - Range queries (`BETWEEN`, `ORDER BY`) → **sequential**.
> - Exact-match lookups by key → **hashed** (but **bad for ranges** — hashing
>   scatters neighbouring keys).
> - Frequent joins of related tables → **clustered**.

![Flowchart for choosing a file organization: point lookups → hashed; range queries → sequential; frequent joins → clustered; otherwise heap.](images/66_fc_file_org.png)

> **Reality check:** in practice you use a **heap + indexes** (Module 7). Indexes
> give you fast lookups *without* committing the base file to one access pattern.

---

## 6.7 The Buffer Manager — Hiding Disk Latency

The **buffer manager** is the performance heart of a DBMS (we met it in Module 1).
It keeps a pool of disk blocks (**pages**) cached in RAM so repeated accesses don't
hit the disk.

![Buffer manager: a buffer pool of page frames in RAM (some clean, some dirty, some pinned); a miss reads a page from disk, dirty pages are flushed back before eviction.](images/65_buffer_manager.png)

**Core concepts:**

- **Page hit** = the block is already in the pool (~100 ns). **Page miss** = fetch
  from disk (~10 ms). **Hit ratio** = `hits / (hits + misses)` — maximize it.
- **Dirty bit:** a page modified in RAM is **dirty** and must be **written back**
  to disk before its frame is reused.
- **Pin count:** a page in active use is **pinned** so it can't be evicted.
- **Replacement policy** (which page to evict when the pool is full):
  - **LRU** (Least Recently Used) — evict the page unused for longest (most common).
  - **MRU** (Most Recently Used) — better for some scan patterns.
  - **CLOCK** (second-chance) — an efficient LRU approximation.
  - **FIFO** — simplest; can suffer **Belady's anomaly**.

> **Why LRU usually wins:** databases have **temporal locality** — a page used
> recently is likely used again soon (e.g. an index root). LRU keeps hot pages and
> evicts cold ones.

> **Double buffering / prefetching (read-ahead):** during a **sequential scan** the
> DBMS reads the **next** block while the CPU is still processing the **current**
> one, overlapping I/O with computation so the CPU rarely stalls on the disk. This
> is why a large sequential scan can sustain near-disk-bandwidth throughput.

> **Force vs no-force / steal vs no-steal** (preview of Module 10 recovery): these
> policies decide *when* dirty pages reach disk relative to `COMMIT`. They directly
> shape what the recovery manager must undo/redo. We cover them in Module 10.

### 6.7A Buffer replacement — worked LRU & CLOCK traces

Given a page-reference string and a fixed number of frames, exams ask you to trace
the pool and **count hits/misses (faults)**. Here is the exact procedure for the two
you must know.

> *Given:* **3 frames**, reference string `A B C A D B E A B` (pages requested in
> order). All frames start empty.

**LRU (evict the Least Recently Used page):**

```text
ref | frames (MRU on right)      | hit? | evicted
----+----------------------------+------+--------
 A  | A                          | miss |
 B  | A B                        | miss |
 C  | A B C                      | miss |          (pool now full)
 A  | B C A                      | HIT  |          (A moves to MRU)
 D  | C A D                      | miss | B        (B was least recent)
 B  | A D B                      | miss | C
 E  | D B E                      | miss | A
 A  | B E A                      | miss | D
 B  | E A B                      | HIT  |
----+----------------------------+------+--------
Hits = 2, Misses = 7,  hit ratio = 2/9 ≈ 22%
```

**CLOCK (second-chance — an LRU approximation using a reference bit):** frames sit in
a ring; each has a **use bit**. On a miss, advance the hand; if the current frame's
use bit is 1, clear it to 0 and move on; evict the first frame found with use bit 0.
On a hit, just set that frame's use bit to 1.

```text
ref | ring [page:usebit]        | action
----+---------------------------+-------------------------------------------
 A  | [A:1]                     | miss, load A
 B  | [A:1][B:1]                | miss, load B
 C  | [A:1][B:1][C:1]           | miss, load C (full)
 A  | [A:1][B:1][C:1]           | HIT, set A:1 (already 1)
 D  | hand sees A:1→0, B:1→0,   | miss: give A,B second chances (clear bits),
    |   C:1→0, wraps A:0 → evict|   evict A; load D → [D:1][B:0][C:0]
 B  | [D:1][B:1][C:0]           | HIT, set B:1
 E  | hand at D:1→0, B:1→0,     | miss: clear D,B; C:0 → evict C;
    |   C:0 → evict C           |   load E → [D:0][B:0][E:1]
 A  | hand at D:0 → evict D     | miss, load A → [A:1][B:0][E:1]
 B  | [A:1][B:1][E:1]           | HIT, set B:1
----+---------------------------+-------------------------------------------
Hits = 3, Misses = 6 (CLOCK approximates LRU with O(1) bookkeeping, no timestamps)
```

> **Belady's anomaly (exam trap):** with **FIFO**, adding *more* frames can
> sometimes *increase* misses. **LRU and CLOCK are stack algorithms — immune** to
> Belady's anomaly. This is a common one-line MCQ.

### 6.7B Why a DBMS may NOT use plain LRU — sequential flooding

Plain LRU is great for **random/repeated** access but can be **catastrophic** for
one particular DBMS pattern.

> **Sequential flooding.** A large **sequential scan** (or a full-table join over a
> table bigger than the pool) reads pages `P1, P2, P3, …` once each and never reuses
> them soon. Under LRU, each new page evicts an **older, actually-hot** page (e.g. an
> index root, a small dimension table). The scan "floods" the pool with
> use-once pages, evicting exactly the pages that *would* have been reused — so the
> hit ratio **collapses**, and worse, adding frames barely helps because the scan is
> bigger than any reasonable pool.

> **How real DBMSs defend against it:**
> - **MRU** for the scanned relation — evict the *most recently used* scan page,
>   since it's the least likely to be needed again (protects the rest of the pool).
> - **Scan-resistant / ring buffers:** PostgreSQL routes large sequential scans and
>   `VACUUM` through a small **ring buffer** (a few hundred KB) so a big scan can't
>   evict the whole `shared_buffers`.
> - **2Q / LRU-K / ARC:** admission policies that separate "seen once" from "seen
>   again", keeping frequently-reused pages and cheaply discarding scan-only pages.

> **One-liner (interview):** *"Why not just use LRU in a database?"* → **sequential
> flooding** — a big scan of use-once pages evicts the hot working set; DBMSs use
> MRU / scan-resistant ring buffers / LRU-K to avoid it.

---

## 6.8 Real-World & Backend Perspectives

- **SSD vs HDD:** SSDs have **no seek/rotational latency** (no moving parts), so the
  "random vs sequential" gap shrinks — but sequential is still faster, and SSDs add
  concerns like **write amplification** and wear. The DBMS cost model is changing,
  but block-based I/O and the buffer pool remain.
- **Page size tuning:** PostgreSQL uses 8 KB pages; bigger pages help sequential
  scans, smaller pages reduce wasted I/O for random access.
- **`shared_buffers` / buffer pool size** is one of the first things a DBA tunes —
  it's literally the §6.7 buffer pool. Too small → thrashing (constant misses).
- **RAID in production:** databases commonly run on **RAID 10** (speed + redundancy)
  or RAID 6 (capacity + double-failure protection), with separate disks for data vs
  the write-ahead log.

---

## 6.9 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Forgetting rotational latency is the **average = ½ rotation**, not a full one.
- Thinking **RAID 0** gives fault tolerance (it gives **none**).
- Mixing up RAID min-disk counts (5 → ≥3, 6 → ≥4, 10 → ≥4).
- Treating RAID as a **backup** (it isn't — it protects against disk failure, not
  human error/corruption).
- Using **hashed** organization and expecting fast **range** queries (it's terrible
  at ranges).
- Forgetting unspanned blocking **wastes** the leftover bytes per block.

**Edge cases**
- A record **larger than a block** *forces* **spanned** organization.
- On SSD, "seek time" ≈ 0, so the classic disk cost model overestimates random-read
  cost.
- LRU can still thrash if the working set exceeds the pool (sequential flooding) —
  hence MRU/scan-resistant policies.

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Larger block/page | better sequential throughput | more wasted space on random access |
| More mirroring (RAID 1/10) | safety + read speed | 50% capacity overhead |
| Parity (RAID 5/6) | space-efficient redundancy | write penalty (parity update) |
| Bigger buffer pool | higher hit ratio | less RAM for everything else |

---

## 6.10 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE):** disk-access-time numericals; rotational latency = ½
rotation; RAID level properties (min disks, usable %, fault tolerance); XOR parity
recovery; blocking factor & block-count calculations; spanned vs unspanned; file
organization trade-offs; LRU.

**Interview:** "Why is sequential I/O faster than random?" (one seek vs many);
"What does the buffer pool do?"; "RAID 5 vs RAID 10?"; "Is RAID a backup?" (no).

**Coding/practical:**
- In PostgreSQL, inspect `SHOW shared_buffers;` and `SHOW block_size;` — that's the
  §6.7 pool and the §6.2 page.
- Use `EXPLAIN (ANALYZE, BUFFERS)` to see buffer **hits vs reads** for a query.

---

## 6.11 Concept Checks & MCQs

1. Smallest addressable unit on a disk? → **sector**.
2. Largest component of disk access time? → **seek time**.
3. Average rotational latency at 6000 RPM? → **5 ms** (½ × 10 ms).
4. RAID level with striping and NO redundancy? → **RAID 0**.
5. Minimum disks for RAID 5? → **3**. For RAID 6? → **4**.
6. Usable capacity of RAID 1? → **50%**. RAID 5 with n disks? → **(n−1)/n**.
7. `bfr` for Block=2048, Record=256 (unspanned)? → `floor(2048/256) =` **8**.
8. A record bigger than a block requires ___ organization → **spanned**.
9. Best file organization for equality lookups by key? → **hashed**.
10. Most common buffer replacement policy? → **LRU**.
11. Is RAID a backup? → **No** (availability, not backup).
12. Same track across all platters is a ___ → **cylinder**.
13. RAID level with a **dedicated** parity disk (write bottleneck)? → **RAID 4**
    (RAID 5 fixes it by rotating parity).
14. A block is an integer multiple of the ___ size → **sector**.
15. Reading the next block while processing the current one is called ___ →
    **double buffering / prefetching (read-ahead)**.
16. How many physical I/Os does **one small write** cost on RAID 5? → **4** (read
    old data + read old parity + write new data + write new parity).
17. How many for RAID 6? → **6** (two parities: 3 reads + 3 writes).
18. Which RAID is best for a **write-heavy** DB and why? → **RAID 10** — no parity
    read-modify-write, ~2 I/Os per write.
19. Block=1024 B, Record=300 B, **unspanned** — records per block? → `floor(1024/300)
    =` **3** (124 bytes/block wasted).
20. Same as above but **spanned**, 10 records — number of blocks? →
    `ceil(10×300/1024) =` **3** (vs 4 unspanned).
21. Reference string `A B C A D B E A B`, 3 frames, **LRU** — number of hits? → **2**
    (see §6.7A).
22. Which replacement policies are **immune to Belady's anomaly**? → **LRU and CLOCK**
    (stack algorithms); **FIFO is not**.
23. Why might a DBMS avoid plain LRU? → **sequential flooding** — a large scan of
    use-once pages evicts the hot working set.
24. What does CLOCK use instead of timestamps? → a **use (reference) bit** per frame,
    giving each page a "second chance" before eviction.
25. PostgreSQL's defense against a big scan trashing `shared_buffers`? → a small
    **ring buffer** for large sequential scans / `VACUUM`.

**True/False**
- RAID 0 can survive one disk failure. → **False**.
- Rotational latency averages a full rotation. → **False** (½ rotation).
- Hashed files are great for range queries. → **False**.
- Heap files have O(1) insert. → **True**.
- A single small write on RAID 5 costs 4 I/Os. → **True** (read-modify-write parity).
- LRU suffers Belady's anomaly. → **False** (FIFO does; LRU/CLOCK are stack algorithms).
- Sequential flooding makes LRU evict hot pages during a big scan. → **True**.

**Numerical (do it):**
> Disk: 10,000 RPM, avg seek 4 ms, transfer rate 100 MB/s, block = 4 KB.
> Avg rotational latency = ½ × (60/10000) s = ½ × 6 ms = **3 ms**.
> Transfer = 4 KB / 100 MB/s ≈ **0.04 ms**.
> Total ≈ 4 + 3 + 0.04 ≈ **7.04 ms** per random block.

---

## 6.12 One-Page Revision Sheet

```
MEMORY HIERARCHY (fast→slow): registers > cache > RAM (VOLATILE) | SSD > HDD > tape (non-volatile)
  RAM ~100ns vs disk ~10ms = ~100,000x. DBMS goal = avoid disk; read whole BLOCKS.
  primary(CPU-addressable) vs secondary(disk) vs tertiary(tape).

DISK GEOMETRY: platter, TRACK(ring), SECTOR(arc=smallest unit), CYLINDER(same track all platters),
  head on arm, BLOCK/PAGE = DBMS I/O unit.

DISK ACCESS TIME = SEEK(move arm, biggest) + ROTATIONAL LATENCY(avg = 1/2 rotation = 1/2 * 60/RPM)
  + TRANSFER(data/rate). Sequential >> random (1 seek vs many).

RAID (availability, NOT backup):
  0 stripe   min2  100%   survives 0   (speed only)
  1 mirror   min2  50%    survives 1
  4 stripe + DEDICATED parity disk -> that disk = write bottleneck (RAID 5 fixes it)
  5 stripe+1parity min3 (n-1)/n survives1   parity ROTATED (no bottleneck); write penalty
  6 stripe+2parity min4 (n-2)/n survives2
  10 mirror+stripe min4 50% survives 1/mirror   (speed+safety)
  XOR parity: P=A1^A2^A3 ; lost A3 = A1^A2^P.   (RAID 2/3 obsolete)
  WRITE PENALTY: 1 small write = RAID5 -> 4 I/Os (read D,read P,write D,write P);
    RAID6 -> 6 I/Os. => RAID5/6 for READ-heavy; RAID10 (~2 I/Os/write) for WRITE-heavy.
  DOUBLE BUFFERING / prefetch: read next block while CPU processes current (sequential scans).

RECORDS: fixed(offset = i*size) vs variable(length prefix/delimiter).
  bfr = floor(Block/Record); #blocks = ceil(r/bfr).
  UNSPANNED(no cross block, wastes leftover) vs SPANNED(crosses, no waste, needs pointer;
    required if record > block).

FILE ORG: HEAP(unordered, O(1) insert, O(n) search) | SEQUENTIAL(ordered, O(log n), range-good)
  | HASHED(O(1) equality, range-BAD) | CLUSTERED(related tables together, join-good).

BUFFER MANAGER: pool of pages in RAM. hit(~100ns)/miss(~10ms). DIRTY bit(flush before evict),
  PIN(don't evict in use). Replacement: LRU(common), MRU, CLOCK, FIFO(Belady). maximize hit ratio.
  CLOCK = use-bit second-chance (O(1), approximates LRU). LRU/CLOCK immune to Belady; FIFO not.
  SEQUENTIAL FLOODING: big scan of use-once pages evicts hot set under LRU -> DBMS uses MRU /
    ring buffer (Postgres) / LRU-K / 2Q / ARC for scan resistance.
  SPANNED vs UNSPANNED #blocks: spanned = ceil(r*R / B); unspanned = ceil(r / floor(B/R)).
```

### Flash cards

| Front | Back |
|-------|------|
| Biggest disk-access component? | Seek time |
| Avg rotational latency? | ½ × (60/RPM) |
| RAID 0 fault tolerance? | None |
| RAID 5 / 6 min disks? | 3 / 4 |
| RAID 5 usable space? | (n−1)/n |
| XOR parity recovery? | lost = XOR of the survivors + parity |
| Blocking factor? | floor(Block size / Record size) |
| Record > block needs? | Spanned organization |
| Hashed file weakness? | Range queries |
| Common eviction policy? | LRU |
| Is RAID a backup? | No (availability only) |

### Spaced repetition
- **24-hour:** redo the disk-access and bfr numericals; recite RAID min-disks/usable.
- **7-day:** explain seek vs rotational vs transfer; XOR parity recovery; LRU.
- **30-day:** given a workload, pick the file organization + RAID level with reasons.

---

## 6.13 Summary

Storage starts from one hard fact: the **memory hierarchy** makes disk ~100,000×
slower than RAM, so a DBMS reads whole **blocks (pages)** and works hard to avoid
the disk. We learned **disk geometry** (platter/track/sector/cylinder) and the
**disk-access-time** formula (**seek + rotational latency [½ rotation] + transfer**),
then **RAID** (0 striping, 1 mirroring, 5/6 parity with XOR recovery, 10 for
speed+safety — and that RAID is **not a backup**). We packed records into blocks via
the **blocking factor** (`floor(B/R)`) and distinguished **spanned vs unspanned**.
We compared **file organizations** (heap, sequential, hashed, clustered) by access
pattern, and saw the **buffer manager** cache pages in RAM with a **dirty bit**,
**pinning**, and an **LRU** replacement policy to maximize the hit ratio.

This sets up **Module 7 — Indexing & Hashing**, where we build the data structures
(B/B+ trees, hash indexes) that make the disk-bound lookups of Module 4's queries
fast — and **Module 8 — Query Processing**, whose cost model is literally counting
the block accesses we just learned about.

> **You have mastered this module when** you can: compute disk access time and
> blocking factor from given numbers; state every RAID level's min disks / usable
> space / fault tolerance and explain XOR parity recovery; choose a file
> organization for a workload; and explain what the buffer manager, dirty bit, and
> LRU do — all without notes.
