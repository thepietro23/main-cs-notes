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

**True/False**
- RAID 0 can survive one disk failure. → **False**.
- Rotational latency averages a full rotation. → **False** (½ rotation).
- Hashed files are great for range queries. → **False**.
- Heap files have O(1) insert. → **True**.

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
  DOUBLE BUFFERING / prefetch: read next block while CPU processes current (sequential scans).

RECORDS: fixed(offset = i*size) vs variable(length prefix/delimiter).
  bfr = floor(Block/Record); #blocks = ceil(r/bfr).
  UNSPANNED(no cross block, wastes leftover) vs SPANNED(crosses, no waste, needs pointer;
    required if record > block).

FILE ORG: HEAP(unordered, O(1) insert, O(n) search) | SEQUENTIAL(ordered, O(log n), range-good)
  | HASHED(O(1) equality, range-BAD) | CLUSTERED(related tables together, join-good).

BUFFER MANAGER: pool of pages in RAM. hit(~100ns)/miss(~10ms). DIRTY bit(flush before evict),
  PIN(don't evict in use). Replacement: LRU(common), MRU, CLOCK, FIFO(Belady). maximize hit ratio.
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
