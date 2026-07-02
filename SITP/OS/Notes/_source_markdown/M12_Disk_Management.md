---
title: "Module 12 — Disk Management"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 12 — Disk Management

> **Where this module sits.**
> Module 11 gave us the **logical** file system — files, inodes, directories. But all
> of that eventually turns into **physical block reads and writes** on a spinning
> platter or a flash chip, and disk is **~100,000× slower than RAM**. This module is
> the OS's job of making that slow device **as fast and as fair as possible**: the
> physical structure of **HDD vs SSD vs NVMe**, the **disk-scheduling** algorithms
> that reorder pending requests to cut head travel, disk **formatting/partitions**,
> and a recap of **RAID**. The **disk-scheduling head-movement numericals** (FCFS,
> SSTF, SCAN, C-SCAN, LOOK, C-LOOK) are a near-guaranteed GATE/C-DAC question and a
> classic interview warm-up.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★     | ★★★    | ★★★★★   | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **disk-scheduling head
movement** for FCFS / SSTF / SCAN / C-SCAN / LOOK / C-LOOK on a request queue;
**seek time / rotational latency / transfer time** breakdown; **why SSDs have no
seek time**; **HDD vs SSD vs NVMe**; **RAID levels** (0/1/5/6/10) recap; **disk
formatting** (low-level vs logical) and **partitioning / boot block / MBR vs GPT**.

---

## 12.1 The Disk as a Physical Device

A hard disk drive (**HDD**) stores bits as magnetic patterns on spinning **platters**.
To read a block, three mechanical things must happen — and only the third moves data:

![Reading a disk block costs seek time (move the arm to the track) + rotational latency (wait for the sector to spin under the head) + transfer time (read the bytes); seek dominates and is why request ordering matters.](images/121_hdd_vs_ssd.png)

| Term | Meaning |
|------|---------|
| **Platter** | a spinning magnetic disk (data on both surfaces) |
| **Track** | one concentric ring on a platter |
| **Sector** | an arc of a track — the **smallest addressable unit** (512 B / 4 KB) |
| **Cylinder** | the **same track across all platters** (no arm movement to switch) |
| **Head / arm** | floats over the surface; the arm moves it in/out to a track |

**Disk access time has three parts:**

```text
1. SEEK time         — move the arm to the target TRACK/cylinder (mechanical, BIGGEST)
2. ROTATIONAL latency — wait for the SECTOR to spin under the head (avg = 1/2 rotation)
3. TRANSFER time     — read the bytes as they pass the head

Average rotational latency = (1/2) x (60 / RPM) seconds
```

> **Why this whole module exists:** **seek time dominates** and it depends on **how
> far** the arm must move. If we cleverly **reorder** the pending requests so the arm
> sweeps smoothly instead of jumping around, we cut total seek distance dramatically.
> That reordering is **disk scheduling** (§12.3). On an **SSD there is no arm** — so
> the story changes completely (§12.2).

### MCQs

1. Smallest addressable unit on a disk? → **sector**.
2. Largest component of disk access time? → **seek time**.
3. Average rotational latency? → **½ × (60/RPM)** (half a rotation).

---

## 12.2 HDD vs SSD vs NVMe

### HDD — mechanical, cheap, sequential-friendly
Moving arm + spinning platter. Random access is slow because every non-adjacent
request pays **seek + rotational latency** (~5–10 ms). Great **capacity per rupee**;
poor random IOPS (~100–200).

### SSD — flash memory, no moving parts
An SSD stores bits in **NAND flash cells**; there is **no arm and no platter**, so a
read is a purely **electronic address lookup**. This is the key exam line:

> **Why an SSD has no seek time.** There is **nothing to move** — no mechanical head,
> no rotating platter. Any flash page is reached by **addressing it electronically**,
> so access time is **roughly the same regardless of location**. This collapses the
> huge random-vs-sequential gap that dominates HDDs; SSD random reads are ~100× faster
> than HDD.

But flash has its own quirks the OS must manage:
- **Erase-before-write / P/E cycles:** flash is written in **pages** but erased in
  larger **blocks**, and each cell wears out after a limited number of program/erase
  cycles.
- **FTL (Flash Translation Layer):** firmware that maps logical blocks to physical
  pages, doing **wear levelling** (spread writes) and **garbage collection**.
- **TRIM:** the OS tells the SSD which blocks are no longer used so the FTL can
  reclaim them efficiently.
- **Write amplification:** one logical write can trigger several physical
  writes (relocation during GC) — a durability/perf concern.

### NVMe — a *protocol*, not a medium
**NVMe (Non-Volatile Memory express)** is the modern **protocol** for talking to an
SSD over the **PCIe** bus, replacing the old **SATA/AHCI** interface that was designed
for slow spinning disks. It exposes **thousands of parallel queues** with deep depth,
matching flash's parallelism, so NVMe SSDs reach **multiple GB/s** and very low
latency.

> **Common confusion (interview):** "SATA vs NVMe" is not medium vs medium — both can
> be SSDs. **SATA** is the legacy interface (one queue, ~550 MB/s ceiling); **NVMe**
> is the PCIe protocol built for flash's parallelism (GB/s). An NVMe SSD is a
> flash SSD spoken to over PCIe with the NVMe command set.

| | **HDD** | **SATA SSD** | **NVMe SSD** |
|---|---|---|---|
| Medium | magnetic platters | NAND flash | NAND flash |
| Moving parts | **yes** (arm+platter) | no | no |
| Seek time | ~5–10 ms | **none** | **none** |
| Interface | SATA | SATA/AHCI | **PCIe/NVMe** |
| Throughput | ~100–200 MB/s | ~550 MB/s | **GB/s (several)** |
| Random IOPS | ~100–200 | ~50–100 K | **100 K–1 M+** |
| Best for | bulk/cold storage | general use | databases, AI, hot data |

> **Big implication for the rest of this module:** the classic **disk-scheduling
> algorithms exist to minimise arm movement — an HDD concern.** On SSD/NVMe there is
> no arm, so the OS mostly **passes requests straight through** (Linux `none`/`mq-
> deadline` schedulers) and instead worries about **parallelism, wear, and TRIM**.
> Scheduling algorithms are still the #1 exam topic, but know *why* they matter less
> on flash.

### MCQs

1. Why does an SSD have **no seek time**? → **no moving parts** — data is addressed
   electronically.
2. NVMe is a ___ , not a storage medium → **protocol** (over PCIe).
3. SSD firmware that maps logical→physical and levels wear? → the **FTL**.
4. Command telling an SSD which blocks are free? → **TRIM**.

---

## 12.3 Disk Scheduling — the Problem and the Metric

When many processes request disk blocks, they pile up in a **request queue** of
**cylinder numbers**. The OS chooses the **order** to serve them, aiming to
**minimise total head (arm) movement** — because seek time ∝ distance travelled.

**The metric we compute:** **total head movement** = sum of `|next − current|`
cylinder distances as the head visits each request. Fewer cylinders travelled →
less seek time → higher throughput.

> **The running example (used for every algorithm below).**
> Disk cylinders **0–199**. Head starts at **53**. Pending request queue (arrival
> order):
>
> ```text
> 98, 183, 37, 122, 14, 124, 65, 67
> ```
>
> Sorted for convenience: `14, 37, [53=head], 65, 67, 98, 122, 124, 183`.
> For the directional algorithms we assume the head is initially moving **toward
> larger cylinder numbers (up)**. **State the direction — it changes the answer.**

### MCQs

1. Disk scheduling minimises? → **total head (seek) movement**.
2. The queue holds? → **cylinder numbers** to be served.
3. Why must you state the initial **direction** for SCAN/LOOK? → it **changes** the
   total movement.

---

## 12.4 FCFS and SSTF

### FCFS — First-Come, First-Served
Serve requests in **arrival order**. Fair and simple, but the head can **bounce wildly**
back and forth.

```text
Order: 53 -> 98 -> 183 -> 37 -> 122 -> 14 -> 124 -> 65 -> 67
Jumps:   45    85    146    85   108    110    59     2
Total head movement = 45+85+146+85+108+110+59+2 = 640 cylinders
```

- **Pro:** fair (no starvation), trivial. **Con:** ignores distance → **worst
  movement** (640 here). Note the huge 183→37 = 146 swing.

### SSTF — Shortest Seek Time First
Always serve the **closest** pending request to the current head position (greedy
nearest-neighbour).

```text
From 53: nearest is 65 (dist 12)   -> 65
From 65: 67 (2)                     -> 67
From 67: 37 (30)                    -> 37
From 37: 14 (23)                    -> 14
From 14: 98 (84)                    -> 98
From 98: 122 (24)                   -> 122
From 122: 124 (2)                   -> 124
From 124: 183 (59)                  -> 183
Total = 12+2+30+23+84+24+2+59 = 236 cylinders
```

- **Pro:** far less movement than FCFS (**236** vs 640). **Con:** **starvation** — a
  request in a far corner can wait forever if closer requests keep arriving; it's the
  disk analogue of SJF's starvation (M6).

> **Memory hook:** **SSTF = always grab the nearest snack.** Efficient, but the food
> in the far cupboard may never get eaten (starvation).

### MCQs

1. FCFS total for our queue? → **640**.
2. SSTF total? → **236**.
3. SSTF's fairness flaw? → **starvation** of far requests.

---

## 12.5 SCAN and C-SCAN (the elevator algorithms)

### SCAN — the elevator
The head moves in **one direction** serving every request in its path until it
reaches the **end of the disk**, then **reverses** and serves the rest — exactly like
a **lift** going to the top floor then coming down.

Head at 53, moving **up** first, disk end = 199:

```text
Up:   53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 -> 199 (reach end)
Down: 199 -> 37 -> 14
Movement = (199 - 53) + (199 - 14) = 146 + 185 = 331 cylinders
```

![SCAN sweeps up to cylinder 199 servicing 65,67,98,122,124,183, then reverses and services 37,14; total head movement 331 cylinders. It reaches the disk end before turning, unlike LOOK.](images/119_scan_path.png)

- **Pro:** no starvation; smooth. **Con:** goes all the way to cylinder **199 even if
  no request is there** (wasteful) — LOOK fixes this. Also, cylinders **just behind**
  the head wait almost a full sweep.

### C-SCAN — Circular SCAN (fairer wait times)
Like SCAN, but when it hits the end it **jumps straight back to the start (0)**
without servicing on the return, then sweeps in the **same direction** again. This
treats the cylinders as a **circular list**, giving **more uniform wait times** (the
just-missed cylinders don't wait a whole double-sweep).

Head at 53, up, end = 199, then wrap to 0:

```text
Up:   53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 -> 199 (end)
Wrap: 199 -> 0                (jump back, no service)
Up:   0 -> 14 -> 37
Movement = (199 - 53) + (199 - 0) + (37 - 0) = 146 + 199 + 37 = 382 cylinders
```

![C-SCAN sweeps up to 199, jumps back to cylinder 0 without servicing, then sweeps up again to service 14 and 37; total head movement 382 cylinders. The wrap gives more uniform waiting times than SCAN.](images/120_cscan_path.png)

- **Pro:** **uniform waiting time** (no cylinder waits a full round trip). **Con:**
  the **return jump** (199→0) is extra movement (382 > 331), and like SCAN it visits
  the disk ends even with no request there.

> **Convention note (read carefully for GATE):** we **count the return jump 199→0** as
> head movement (it's real arm travel). Some textbooks report C-SCAN/C-LOOK **excluding**
> the jump — always **state your convention**. Here we include it.

> **Memory hook:** **SCAN = lift that stops on the way down too.** **C-SCAN = lift
> that only picks up going UP** — express ride back to the ground floor, then up again
> (fairer for everyone, but the express ride is wasted distance).

### MCQs

1. SCAN total (up first, end 199)? → **331**.
2. Which algorithm gives the most **uniform** waiting time? → **C-SCAN**.
3. C-SCAN's extra cost vs SCAN? → the **return jump** to cylinder 0.

---

## 12.6 LOOK and C-LOOK (the practical versions)

**LOOK** and **C-LOOK** are the *smart* versions of SCAN/C-SCAN: instead of driving
to the physical **end of the disk**, the head only goes as far as the **last request**
in that direction, then turns. (The head "**looks** ahead" — if nothing's there, don't
go.) These are what real HDDs actually use.

### LOOK
Head at 53, up first; highest request is 183 (not 199), lowest is 14:

```text
Up:   53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 (last up-request, turn HERE)
Down: 183 -> 37 -> 14
Movement = (183 - 53) + (183 - 14) = 130 + 169 = 299 cylinders
```

### C-LOOK
Head at 53, up; go to highest request 183, jump back to **lowest request 14** (not 0),
then continue up:

```text
Up:   53 -> 65 -> 67 -> 98 -> 122 -> 124 -> 183 (highest request)
Jump: 183 -> 14                (to lowest request, not cylinder 0)
Up:   14 -> 37
Movement = (183 - 53) + (183 - 14) + (37 - 14) = 130 + 169 + 23 = 322 cylinders
```

- **LOOK vs SCAN:** LOOK saved the trip to cylinder 199 → **299 vs 331**.
- **C-LOOK vs C-SCAN:** C-LOOK jumps only to the lowest *request* (14), not to 0 →
  **322 vs 382**.

> **Memory hook:** **SCAN/C-SCAN go to the WALL; LOOK/C-LOOK stop at the LAST
> person.** LOOK is "look before you leap — don't drive to an empty end of the disk."

### Full comparison for our queue (head = 53, up-first, disk 0–199)

| Algorithm | Service order | Total head movement | Note |
|-----------|---------------|:-------------------:|------|
| **FCFS** | 98,183,37,122,14,124,65,67 | **640** | fair, worst movement |
| **SSTF** | 65,67,37,14,98,122,124,183 | **236** | greedy, can starve |
| **SCAN** | 65,67,98,122,124,183,→199,37,14 | **331** | elevator, hits end |
| **C-SCAN** | 65,67,98,122,124,183,→199,→0,14,37 | **382** | uniform wait, wrap cost |
| **LOOK** | 65,67,98,122,124,183,37,14 | **299** | SCAN without the wall |
| **C-LOOK** | 65,67,98,122,124,183,→14,37 | **322** | C-SCAN without the wall |

> **Sanity ranking for this queue:** SSTF (236) < LOOK (299) < SCAN (331) <
> C-LOOK (322... note C-LOOK > SCAN here) — orderings depend on the queue, so
> **always compute**. The only guaranteed winner in movement is often SSTF (greedy),
> but it starves; SCAN-family avoid starvation. FCFS is almost always the worst.

### MCQs

1. LOOK total? → **299**. C-LOOK total? → **322**.
2. Difference SCAN vs LOOK? → LOOK **turns at the last request**, not the disk end.
3. Difference C-SCAN vs C-LOOK? → C-LOOK **jumps to the lowest request**, not
   cylinder 0.
4. Which two avoid starvation *and* don't drive to empty disk ends? → **LOOK /
   C-LOOK**.

---

## 12.7 Disk Formatting, Partitions, and Booting

Before a disk can hold files it must be prepared in stages:

- **Low-level (physical) formatting:** the manufacturer divides each track into
  **sectors** with headers, data areas, and **ECC** (error-correcting codes). Defines
  the sector layout.
- **Partitioning:** split the disk into one or more **partitions** (logical disks),
  each of which can hold a different filesystem/OS. The partition table lives in the
  **MBR** or **GPT**:
  - **MBR (Master Boot Record):** legacy; ≤ 4 primary partitions, **max 2 TB** disk
    (32-bit LBA).
  - **GPT (GUID Partition Table):** modern (UEFI); many partitions, **huge disks**,
    redundant headers/CRC. Preferred today.
- **Logical formatting:** write the chosen **filesystem** structures (superblock,
  inode/FAT tables, root directory) into a partition — this is `mkfs`/"Format…".
- **Boot block:** a fixed location the firmware reads at power-on; it holds the
  **bootstrap loader** (e.g. GRUB) that finds and loads the OS kernel.
- **Bad-block management:** the OS/FTL marks defective sectors and remaps them to
  spare sectors so they're never used.
- **Swap space:** a partition or file the OS uses as backing store for **virtual
  memory** paging (ties back to M10).

> **Memory hook:** low-level format = **draw the parking-lot lines** (sectors);
> partition = **fence off sections** (MBR/GPT); logical format = **install the
> filing cabinets** (filesystem); boot block = **the note at the entrance telling
> you where the manager's office is** (bootstrap).

### MCQs

1. Legacy partition scheme capped at 2 TB / 4 primaries? → **MBR**.
2. Modern UEFI partition scheme? → **GPT**.
3. `mkfs` / "Format" performs which step? → **logical formatting** (write the
   filesystem).
4. What does the boot block hold? → the **bootstrap loader**.

---

## 12.8 RAID — a Quick Recap

**RAID (Redundant Array of Independent Disks)** combines several physical disks into
one logical unit for **speed** (parallel I/O), **reliability** (redundancy), or both.
Remember: **RAID protects against disk failure, it is NOT a backup** (it won't undo an
accidental delete or corruption).

| RAID | Technique | Min disks | Usable | Survives | Best for |
|------|-----------|:---------:|:------:|:--------:|----------|
| **0** | striping | 2 | 100% | **nothing** | raw speed |
| **1** | mirroring | 2 | 50% | 1 disk | critical data |
| **5** | stripe + 1 rotated parity | 3 | (n−1)/n | 1 disk | read-heavy, balanced |
| **6** | stripe + 2 parities | 4 | (n−2)/n | 2 disks | high availability |
| **10 (1+0)** | mirror **then** stripe | 4 | 50% | 1 per mirror | speed **and** safety |

> **XOR parity (RAID 5/6):** `P = A1 ⊕ A2 ⊕ A3`; if a disk dies, rebuild it as
> `A3 = A1 ⊕ A2 ⊕ P` — XOR is its own inverse. **Write penalty:** a single small
> write on RAID 5 costs **4 I/Os** (read old data + read old parity + write new data
> + write new parity), so RAID 5/6 favour **read-heavy** loads and **RAID 10** is
> preferred for **write-heavy** databases (~2 I/Os per write).

> **Exam nuggets:** RAID 0 = **no** fault tolerance. RAID 5 needs **≥3** disks, RAID 6
> **≥4**. RAID 1/10 have **50%** overhead. (Full treatment with worked numericals is
> in DBMS Module 6.)

### MCQs

1. RAID level with striping and **no** redundancy? → **RAID 0**.
2. Minimum disks for RAID 5 / RAID 6? → **3 / 4**.
3. Best RAID for a **write-heavy** DB? → **RAID 10** (no parity read-modify-write).

---

## 12.9 Real-World & Backend Perspectives

- **Linux I/O schedulers** implement these ideas: `mq-deadline` and `bfq` (fair,
  latency-bounded) for HDDs; `none` for NVMe (the device's own parallelism beats any
  arm-movement heuristic — there is no arm).
- **SSD-aware everything:** databases and filesystems now assume random reads are
  cheap, but still batch/sequentialise **writes** to reduce write amplification and
  flash wear.
- **Cloud block storage** (AWS EBS, GCP PD) sells you IOPS and throughput tiers —
  literally the seek/transfer trade-offs of this module, abstracted and metered.
- **`iostat` / `iotop`** show per-device utilisation, average queue length, and
  await time — the practical face of "is the disk the bottleneck?".
- **Alignment matters:** partitions/filesystems aligned to the SSD's erase-block or
  the RAID stripe avoid extra read-modify-write cycles — a real performance win.

---

## 12.10 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- **Not stating the direction** for SCAN/LOOK/C-SCAN/C-LOOK — the answer depends on
  it. Always write "moving up" or "moving down".
- Forgetting **SCAN/C-SCAN go to the disk end (0 or 199)** while **LOOK/C-LOOK stop
  at the last request**.
- Mishandling the **C-SCAN/C-LOOK return jump** — decide whether you count it and say
  so (we count it).
- Claiming SSTF is always optimal — it usually has low movement **but can starve**.
- Thinking disk scheduling helps an **SSD** — it barely does (no arm).
- Treating **RAID as a backup** (it isn't).

**Edge cases**
- If the head is **at** a requested cylinder, that request is served with **0**
  movement.
- If **all** requests are on one side of the head, SCAN and LOOK behave identically in
  that direction.
- On SSD/NVMe the "optimal order" is essentially **any** order — throughput is bound
  by parallelism, not seek distance.

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| SSTF | low total movement | **starvation** of far requests |
| SCAN/C-SCAN | no starvation, smooth | travels to disk ends unnecessarily |
| LOOK/C-LOOK | no wasted end trips | slightly more bookkeeping |
| C-SCAN vs SCAN | uniform wait times | extra return-jump distance |

---

## 12.11 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** compute **total head movement** for all six
algorithms on a given queue (the §12.5–12.6 table is the template); seek/rotational/
transfer breakdown; **why SSD has no seek**; MBR vs GPT; RAID recap.

**Interview:** "Walk me through the disk-scheduling algorithms" (elevator analogy);
"Why don't SSDs need them?" (no moving arm); "SATA vs NVMe" (interface vs protocol,
parallelism); "Is RAID a backup?" (no).

**Coding/practical:**
- `cat /sys/block/sda/queue/scheduler` shows (and lets you change) the active Linux
  I/O scheduler.
- `iostat -x 1` → watch `%util`, `await`, `aqu-sz` to spot a disk bottleneck.
- `lsblk`, `fdisk -l`, `parted` show partitions (MBR/GPT); `mkfs.ext4` does logical
  formatting.

---

## 12.12 Concept Checks & MCQs

1. Metric disk scheduling minimises? → **total head movement**.
2. FCFS total (head 53; 98,183,37,122,14,124,65,67)? → **640**.
3. SSTF total (same)? → **236**.
4. SCAN total (up, end 199)? → **331**.
5. C-SCAN total (up, wrap via 0)? → **382**.
6. LOOK total (up)? → **299**.
7. C-LOOK total (up)? → **322**.
8. Which algorithm can **starve** far requests? → **SSTF**.
9. Difference SCAN vs LOOK? → LOOK turns at the **last request**, not the disk end.
10. Difference C-SCAN vs C-LOOK? → C-LOOK jumps to the **lowest request**, not 0.
11. Which gives the most **uniform waiting time**? → **C-SCAN**.
12. Why does an SSD have no seek time? → **no moving parts** (electronic addressing).
13. NVMe is a ___ over ___ → **protocol** over **PCIe**.
14. SSD firmware doing wear levelling / GC? → the **FTL**.
15. Command telling an SSD which blocks are free? → **TRIM**.
16. Legacy 2 TB / 4-primary partition scheme? → **MBR**; modern? → **GPT**.
17. `mkfs` performs? → **logical formatting**.
18. Boot block holds? → the **bootstrap loader**.
19. RAID with no fault tolerance? → **RAID 0**.
20. Min disks RAID 5 / 6? → **3 / 4**.
21. Best RAID for write-heavy DB? → **RAID 10**.
22. Average rotational latency at 7200 RPM? → ½ × (60/7200) s = ½ × 8.33 ms ≈
    **4.17 ms**.

**True/False**
- SSTF always gives the minimum total head movement. → **False** (usually low, but
  not guaranteed optimal, and it starves).
- SCAN reaches the physical end of the disk before reversing. → **True**.
- LOOK drives to cylinder 0/199 even with no request there. → **False** (that's
  SCAN).
- SSDs benefit greatly from SCAN/C-SCAN. → **False** (no arm to schedule).
- RAID 0 survives one disk failure. → **False**.

**Numerical (do it):**
> Same queue, but head starts at **50** and moves **down** first (disk 0–199).
> Requests: sorted `14,37,50*,65,67,98,122,124,183`. **LOOK down:** 50→37→14 (turn),
> then →65→67→98→122→124→183. Movement = (50−14) + (183−14) = 36 + 169 = **205**
> cylinders. (Direction and start position change everything — always recompute.)

---

## 12.13 One-Page Revision Sheet

```
DISK ACCESS TIME = SEEK(move arm, BIGGEST) + ROTATIONAL LATENCY(avg 1/2 rot = 1/2*60/RPM)
  + TRANSFER(bytes/rate). Seek ∝ distance => reorder requests = DISK SCHEDULING.

HDD: platters+arm, seek+rotate, ~100-200 IOPS, cheap capacity.
SSD: NAND flash, NO moving parts => NO SEEK (electronic address), ~100x faster random.
  FTL(wear leveling+GC), TRIM(mark free), write amplification, erase-before-write.
NVMe = PROTOCOL over PCIe (not a medium); many parallel queues; GB/s. SATA=legacy iface.

DISK SCHEDULING  (queue 98,183,37,122,14,124,65,67 ; head=53 ; up-first ; disk 0-199):
  metric = TOTAL HEAD MOVEMENT = sum |next-curr|.  STATE THE DIRECTION.
  FCFS   arrival order                    -> 640   (fair, worst; big 183->37 swing)
  SSTF   nearest first (greedy)           -> 236   (low, but STARVES far reqs)
  SCAN   elevator to END(199) then reverse-> 331   (no starve; hits the wall)
  C-SCAN up to 199, JUMP to 0, up again   -> 382   (uniform wait; wrap cost)
  LOOK   like SCAN but turn at LAST req    -> 299   (no wasted end trip)
  C-LOOK up to last req, JUMP to lowest req-> 322   (C-SCAN w/o wall)
  SCAN/C-SCAN go to the WALL(0/199); LOOK/C-LOOK stop at LAST person.
  (count the wrap jump as movement; state convention.)

FORMATTING: low-level(sectors+ECC, factory) -> PARTITION(MBR<=2TB/4prim | GPT huge/UEFI)
  -> logical format(mkfs: superblock/inode/FAT) . BOOT BLOCK = bootstrap loader(GRUB).
  swap = paging backing store; bad-block remap.

RAID (availability, NOT backup): 0 stripe(100%,survive0) | 1 mirror(50%,1) |
  5 stripe+1parity(min3,(n-1)/n,1; write penalty 4 I/Os) | 6 +2parity(min4,(n-2)/n,2)
  | 10 mirror+stripe(min4,50%, speed+safety, ~2 I/Os/write). XOR: A3 = A1^A2^P.
```

### Flash cards

| Front | Back |
|-------|------|
| Biggest disk-access component? | Seek time |
| FCFS total (our queue)? | 640 |
| SSTF total? | 236 (can starve) |
| SCAN total (up, end 199)? | 331 |
| C-SCAN total? | 382 (wrap to 0) |
| LOOK / C-LOOK total? | 299 / 322 |
| SCAN vs LOOK? | LOOK turns at last request, not disk end |
| Why no SSD seek time? | No moving parts (electronic) |
| NVMe is a…? | Protocol over PCIe (not a medium) |
| MBR vs GPT? | Legacy ≤2 TB/4 primaries vs modern/huge |
| Is RAID a backup? | No (availability only) |

### Spaced repetition
- **24-hour:** recompute all six algorithms on the queue `98,183,37,122,14,124,65,67`
  (head 53) from memory; recite HDD vs SSD vs NVMe.
- **7-day:** explain why SSDs don't need disk scheduling; MBR vs GPT; RAID recap with
  min disks/usable/survives.
- **30-day:** given a **new** queue + head + direction, produce the full six-row
  comparison table with totals.

---

## 12.14 Summary

Disk management is the OS's fight against a **slow, mechanical device**. On an **HDD**,
access time is **seek + rotational latency + transfer**, and **seek (arm movement)
dominates** — so the OS **reorders the request queue** to cut total head travel. On
our queue (head 53, disk 0–199, moving up) we computed **FCFS = 640**, **SSTF = 236**
(low but starves), **SCAN = 331** and **C-SCAN = 382** (elevator; C-SCAN wraps for
uniform waits), and the practical **LOOK = 299** / **C-LOOK = 322** (stop at the last
request instead of the disk end). On **SSD/NVMe** there is **no arm and no seek** —
flash is addressed electronically — so scheduling barely matters and the OS instead
manages **parallelism, TRIM, and wear** (NVMe being a **PCIe protocol**, not a
medium). We covered **formatting and partitions** (low-level → MBR/GPT → logical
format → boot block) and recapped **RAID 0/1/5/6/10**.

Next, **Module 13 — I/O Systems** zooms out from the disk to **all** devices: how the
CPU actually talks to hardware via **polling, interrupts, and DMA**, and how the
**kernel I/O subsystem** ties buffering, caching, and spooling together.

> **You have mastered this module when** you can: compute total head movement for all
> six scheduling algorithms on any queue (stating the direction); explain why an SSD
> has no seek time and how NVMe differs from SATA; walk the formatting/partition
> stages (MBR vs GPT); and recap the RAID levels — all without notes.
