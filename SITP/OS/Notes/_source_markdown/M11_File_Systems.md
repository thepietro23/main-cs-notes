---
title: "Module 11 — File Systems"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 11 — File Systems

> **Where this module sits.**
> Memory management (M9–M10) taught the OS to give each program a clean, private
> view of **RAM**. But RAM is **volatile** — pull the plug and it's gone. The file
> system is the OS's answer to the other half of storage: how to keep data **safe,
> named, and organised on disk** so it survives reboots and can be shared. This
> module is the **logical** view — files, directories, allocation, inodes,
> permissions, journaling — and it sits directly on top of the **physical** disk we
> study next in **M12 (Disk Management)** and the **I/O path** of **M13**. GATE and
> the banking IT papers love **file-allocation methods**, the **inode
> indirect-pointer max-file-size** numerical, and **UNIX octal permissions**.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★    | ★★★    | ★★★★    | ★★★       | ★★★★    |

**Most-asked PYQ concepts (SEBI / RBI / GATE / C-DAC):** **file allocation
methods** (contiguous / linked / indexed — pros, cons, fragmentation);
**inode / index-block indirect pointers** and the **maximum file size**
numerical; **access methods** (sequential vs direct/random vs indexed);
**directory structures** (single / two-level / tree / acyclic-graph);
**UNIX permissions** (rwx, octal like 755, `chmod`); **hard vs symbolic (soft)
links** (inode & link-count difference); **journaling / write-ahead logging**;
**FAT vs NTFS vs ext4** feature comparison.

---

## 11.1 What Is a File? (first principles)

A **file** is the OS's fundamental abstraction for **persistent, named storage**.
Raw disk is just a huge array of numbered blocks with no meaning. The file system
turns that into something humans and programs can use: **named containers of bytes**
that live independently of any running process.

> **Memory hook:** a file is a **labelled box in a warehouse**. You ask for it by
> **name** (not "shelf 4021, bin 12"); the warehouse clerk (file system) knows where
> the box physically sits and fetches it. Naming + location-hiding is the whole game.

### File attributes (the metadata every file carries)

| Attribute | Meaning |
|-----------|---------|
| **Name** | human-readable identifier |
| **Identifier** | unique internal number (the **inode number** on UNIX) |
| **Type** | text / executable / directory / device (from extension or magic bytes) |
| **Location** | pointer to the file's blocks on disk |
| **Size** | current size in bytes (and blocks allocated) |
| **Protection** | owner, permissions (rwx), ACLs |
| **Timestamps** | created / last-modified (**mtime**) / last-accessed (**atime**) |

> **Key idea:** the *bytes* of a file are its **data**; everything else in the table
> above is **metadata** — data *about* the file, stored separately (in the **inode**
> on UNIX, §11.6). Exams love the data-vs-metadata split.

### File operations (the system-call verbs)

The OS exposes files through a small set of **system calls**:

| Operation | UNIX syscall | What it does |
|-----------|-------------|--------------|
| **Create** | `creat`/`open` (O_CREAT) | make a new file, allocate an inode |
| **Open** | `open` | set up an entry, return a **file descriptor** |
| **Read** | `read` | copy bytes from file into a buffer |
| **Write** | `write` | copy bytes from a buffer into the file |
| **Seek** | `lseek` | move the **file offset** (the read/write cursor) |
| **Close** | `close` | release the file descriptor |
| **Delete** | `unlink` | remove a directory entry (drops link count) |

> **The open-file table (why `open` matters).** `open` does the expensive work
> **once** — resolve the name to an inode, check permissions — and returns a small
> integer **file descriptor (fd)**. Later `read`/`write` just pass the fd, so the OS
> skips re-parsing the path every time. The kernel keeps a **per-process fd table**
> and a **system-wide open-file table** holding the current **offset** and inode
> pointer. This is why two processes can open the same file with independent cursors.

### MCQs

1. Metadata about a file on UNIX is stored in the? → **inode**.
2. `open()` returns a? → **file descriptor** (small integer).
3. Which call moves the read/write cursor? → **`lseek`** (seek).

---

## 11.2 File Types and Structure

A file is *just bytes* to the OS, but the **meaning** of those bytes comes from a
**type**:

- **Regular files** — ordinary data: text, images, executables.
- **Directory** — a special file whose contents are a **list of (name → inode)**
  entries (it's a file that lists other files).
- **Special / device files** — represent devices (`/dev/sda`, `/dev/null`); reads and
  writes go to a driver, not disk (see M13).
- **Symbolic link** — a file whose content is a **path** to another file (§11.8).

How does the OS know a file's type? Two schemes:

- **Extension (Windows):** `.exe`, `.txt`, `.jpg` — a naming convention, easily
  faked/renamed.
- **Magic number (UNIX):** the first few bytes identify the format (e.g. `0x7F ELF`
  for Linux executables, `%PDF` for PDFs). The `file` command uses this.

> **Memory hook:** Windows trusts the **name tag** (extension); UNIX peeks in the
> **box** (magic number). That's why renaming `photo.jpg` to `photo.txt` fools
> Explorer's icon but not `file photo.txt`.

**File structure** — internally the OS treats a file as an **unstructured stream of
bytes** (the UNIX model). Any record/line structure is imposed by the *application*,
not the OS. (Older mainframe OSes supported OS-level record structures; the byte-
stream model won because it's simplest and most flexible.)

### MCQs

1. A directory is really a? → **file listing (name → inode) entries**.
2. UNIX identifies file type via? → **magic number** (first bytes), not extension.
3. UNIX file model treats a file as a? → **byte stream** (no OS-imposed records).

---

## 11.3 Access Methods

Once a file is open, *how* do you move through its bytes? Three classic methods:

### Sequential access
Read/write **in order**, front to back; each operation advances the cursor. This is
the natural, most common pattern (reading a log, streaming a video).
- **Pro:** simple, matches disk's fast sequential I/O. **Con:** to reach byte *N* you
  pass through everything before it (like a **cassette tape**).

### Direct (random / relative) access
Jump straight to **any record/block number** in constant time via `lseek` — the file
is viewed as a numbered array of fixed-size records. Essential for **databases**.
- **Pro:** O(1) to any position. **Requires** a device that supports it (disk yes,
  tape no). Think **audio CD** — skip to any track instantly.

### Indexed access
Keep an **index** (like a book's index) mapping a **key** → the block holding that
record. To find a record, search the index, then jump directly to its block. Used by
**ISAM** and database indexes (DBMS M7). Often layered **on top of** direct access.

> **Memory hook:** **sequential = cassette tape** (must fast-forward); **direct = CD
> track skip** (jump anywhere); **indexed = book index** (look up key, jump to page).

### MCQs

1. Access method that must pass through earlier bytes? → **sequential**.
2. `lseek` to any offset in O(1) is? → **direct / random access**.
3. Which method needs an auxiliary key→block table? → **indexed**.

---

## 11.4 Directory Structures

A **directory** organises files into a namespace. Four historical designs, each
fixing the previous one's flaw:

```text
1. SINGLE-LEVEL          2. TWO-LEVEL              3. TREE (hierarchical)
   one dir for ALL          one dir PER USER          nested dirs, arbitrary depth

   [ root ]                 [ master file dir ]        /
    a  b  c  d               |     |     |            ├─ home/
    (name clashes!)         u1    u2    u3            │   ├─ nidhi/
                            a b   a c   b d           │   │   └─ notes.txt
                            (u1/a != u2/a)            │   └─ ravi/
                                                       └─ etc/
                                                           └─ passwd
```

| Structure | Idea | Problem it solves / leaves |
|-----------|------|----------------------------|
| **Single-level** | one flat directory for everyone | simplest; **name collisions**, no grouping |
| **Two-level** | a separate directory per user | fixes collisions across users; **no sub-grouping** |
| **Tree** | nested subdirectories, arbitrary depth | grouping + unique **path names**; **no sharing** of one file under two names |
| **Acyclic graph** | allow a file/dir to have **multiple parents** (via links) | enables **sharing**; must avoid **cycles** & handle **dangling** references on delete |

### Acyclic-graph directories and the sharing problem

A **tree** gives every file exactly **one** path. But teams need to **share** a file
under two names/locations. Allowing multiple directory entries to point to the same
file turns the tree into an **acyclic graph** (a DAG). This is exactly what **hard
links** do (§11.8).

Two dangers appear:

- **Dangling references:** if user A deletes the file, user B's entry may point to
  freed space. **Solution:** a **reference (link) count** — free the data only when
  the count hits **0** (UNIX does this).
- **Cycles:** if directories can link to ancestors, you get infinite loops in
  traversal (`find`, backup). **Solution:** forbid hard-linking **directories** (only
  the symlink form, which is allowed to dangle, may point to a directory).

> **Memory hook:** single → two-level → tree → acyclic-graph is a story of *"more
> flexibility, more sharing, but now I must count references and ban cycles."*

### MCQs

1. Directory structure that first eliminated cross-user name clashes? → **two-level**.
2. What makes a directory an **acyclic graph**? → a file with **multiple parents**
   (shared via links).
3. Mechanism that prevents deleting shared data too early? → **reference/link count**.

---

## 11.5 File Allocation Methods

**The core disk question:** given a file that grows over time, *which blocks* on disk
do we give it, and *how do we remember* which ones? Three methods — this is a
top-tier GATE/interview topic.

![Three disk-allocation methods: contiguous (one run of blocks, fast but fragments), linked (each block points to the next, no random access), and indexed (one index block lists all data blocks, random access with no external fragmentation).](images/116_file_allocation.png)

### Contiguous allocation
Give the file **one continuous run** of blocks (start block + length).
- **Pros:** excellent **sequential *and* direct** access (block *i* = start + *i*);
  minimal seek. Directory entry is tiny (start, length).
- **Cons:** suffers **external fragmentation** (free space breaks into small unusable
  gaps); a file can't **grow** past its neighbour without moving; must know size up
  front. Like booking a **row of adjacent cinema seats**.

### Linked allocation
Scatter blocks anywhere; **each block stores a pointer to the next** (a linked list).
- **Pros:** **no external fragmentation**; files grow easily (just link a new block).
- **Cons:** **no efficient direct access** — to reach block *N* you follow *N*
  pointers from the start; a single **corrupt pointer** loses the rest of the file;
  pointers waste some space in each block. **FAT** is a smarter variant that pulls all
  the pointers into one **File Allocation Table** in memory (so you can follow the
  chain without reading every data block).

### Indexed allocation
Give each file one **index block** that holds the **list of all its data-block
addresses**. `block[i]` = the *i*-th entry of the index block.
- **Pros:** **direct access** (index it like an array) **and** no external
  fragmentation. This is the basis of the UNIX **inode** (§11.6).
- **Cons:** the index block itself is **overhead** (wasteful for tiny files); a single
  index block **limits max file size** — solved by **indirect blocks** (next section).

| Method | Direct access | External frag. | Grows easily | Weakness |
|--------|:-------------:|:--------------:|:------------:|----------|
| **Contiguous** | **best** | **yes** | no | fragmentation, must know size |
| **Linked** | **no** (O(N) walk) | no | yes | pointer chase, corruption spreads |
| **Indexed** | yes | no | yes | index-block overhead / size cap |

> **Memory hook:** **Contiguous = a row of seats** (fast, but can't extend).
> **Linked = a treasure hunt** (each clue points to the next; can't skip ahead).
> **Indexed = a table of contents** (jump to any chapter; but the ToC has a page
> limit — fixed by indirection).

### MCQs

1. Allocation method with the **best direct access**? → **contiguous**.
2. Which method has **no external fragmentation** but **no random access**? →
   **linked**.
3. FAT improves linked allocation by? → keeping all **pointers in one table** in
   memory.
4. The UNIX inode uses which allocation method? → **indexed** (with indirect blocks).

---

## 11.6 Inodes and Indirect Pointers (the key numerical)

On UNIX/Linux, every file has an **inode** (index node) — the on-disk structure that
holds **all the metadata plus the pointers to the data blocks**. Crucially, **the
file name is NOT in the inode**; names live in *directories* and map to inode
numbers. That separation is what makes hard links possible (§11.8).

### What's in an inode

- Metadata: **type + permissions**, owner (**uid**/**gid**), **size**, timestamps,
  and the **link count** (`st_nlink`).
- **15 block pointers** (`i_block[15]`): **12 direct**, **1 single-indirect**,
  **1 double-indirect**, **1 triple-indirect**.

![An inode holds metadata plus 12 direct pointers and one single, one double, and one triple indirect pointer; each indirect level points to a block full of further pointers, multiplying the reachable data blocks.](images/117_inode_pointers.png)

- **Direct pointers (12):** point straight to the first 12 data blocks. Small files
  (the vast majority) need **no** extra reads — very fast.
- **Single indirect (1):** points to a block that is **full of pointers** to data
  blocks. Adds (pointers-per-block) more blocks.
- **Double indirect (1):** points to a block of pointers to **single-indirect**
  blocks → squares the reach.
- **Triple indirect (1):** one more level → cubes the reach. This is what lets a small
  inode address a **multi-terabyte** file.

> **Memory hook:** the inode is a filing cabinet. The **12 direct** pointers are
> documents in the top drawer (grab instantly). The indirect pointers are notes
> saying *"more documents in room X"* — one room (single), a floor of rooms (double),
> a building of floors (triple).

### The maximum-file-size numerical (do it cold)

> *Given:* block size **B = 4 KB (4096 B)**, block pointer size **4 B**.
> Pointers that fit in one block: **k = 4096 / 4 = 1024**.

```text
Direct blocks          = 12
Single-indirect blocks = k        = 1,024
Double-indirect blocks = k^2       = 1,048,576
Triple-indirect blocks = k^3       = 1,073,741,824
Total data blocks      = 12 + k + k^2 + k^3 = 1,074,791,436 blocks

Max file size = total blocks × B
              = 1,074,791,436 × 4 KB
              ≈ 4,402,345,721,856 bytes  ≈  4.0 TiB
```

**Level-by-level (memorise the pattern):**

| Level | Blocks reached | Bytes (× 4 KB) |
|-------|---------------:|---------------:|
| 12 direct | 12 | 48 KiB |
| single indirect | 1,024 | 4 MiB |
| double indirect | 1,048,576 | **4 GiB** |
| triple indirect | 1,073,741,824 | **4 TiB** |

> **The shortcut:** the **triple-indirect term dominates**. With 4 KB blocks and
> 4-byte pointers, triple alone = `k³ × B = 2³⁰ × 2¹² = 2⁴² =` **4 TiB**. The other
> terms (4 GiB + 4 MiB + 48 KiB) barely nudge it, so the answer is **≈ 4 TiB**.

> **Practice variant (1 KB blocks, 4-B pointers → k = 256):** triple alone =
> `256³ × 1 KiB = 2²⁴ × 2¹⁰ = 2³⁴ =` **16 GiB**, and the grand total ≈ **16.06 GiB**.
> Same method, different k.

> **Reality check (backend note):** modern **ext4** actually replaces this classic
> indirect scheme with **extents** (contiguous ranges), and caps a single file at
> **16 TiB** (with 4 KB blocks). The 12/single/double/triple calculation is the
> **textbook/GATE model** (ext2/ext3) and is still exactly what exams ask.

### MCQs

1. The UNIX inode holds the file's ___ but **not** its ___ → **metadata + data
   pointers**; **name** (names live in directories).
2. Standard inode pointer layout? → **12 direct + 1 single + 1 double + 1 triple**.
3. Block = 4 KB, pointer = 4 B — max file size? → **≈ 4 TiB** (triple indirect
   dominates: 2⁴²).
4. Which term dominates max file size? → the **triple-indirect** block.

---

## 11.7 UNIX Permissions (rwx, octal, chmod)

UNIX protects each file with **three permission bits — read (r), write (w), execute
(x)** — for **three classes — owner (user), group, others**. Nine bits in all.

```text
   -   rwx   r-x   r--
   |    |     |     |
 type owner group others
```

Each triad is a **3-bit binary number → one octal digit**:

```text
r = 4    w = 2    x = 1        (add them up per class)
rwx = 4+2+1 = 7    r-x = 4+0+1 = 5    r-- = 4+0+0 = 4    rw- = 6
```

> **Worked example — read a mode string.** `rwxr-xr-x`
> = owner `rwx` = **7**, group `r-x` = **5**, others `r-x` = **5** → **755**.
> This is the classic **755** ("everyone can read/execute, only owner can write") —
> the default for programs and directories.

> **Worked example — the other direction.** `chmod 644 file.txt`
> = **6** `rw-`, **4** `r--`, **4** `r--` → `rw-r--r--`: owner can read+write,
> everyone else read-only. The default for **data files**.

**`chmod` two ways:**

```text
chmod 754 file      # numeric (absolute): owner rwx, group r-x, others r--
chmod u+x file      # symbolic (relative): add execute for the owner
chmod go-w file     # remove write from group and others
```

**On a directory, the bits mean something subtly different:**

| Bit | On a file | On a directory |
|-----|-----------|----------------|
| **r** | read contents | **list** the names inside |
| **w** | modify contents | **create/delete** entries inside |
| **x** | execute it | **enter/traverse** it (`cd`, access a path through it) |

> **Trap:** you can have **r** on a directory (see the names) but without **x** you
> **can't cd into it or stat the files** — and with **x** but no **r** you can access
> a file **if you already know its exact name**. Bank/GATE questions test this.

**Special bits (4th octal digit):** **setuid (4)**, **setgid (2)**, **sticky (1)**.
The classic is the **sticky bit on `/tmp` → mode 1777**: everyone can create files,
but you can only **delete your own** — stops users deleting each other's temp files.

### MCQs

1. `rwxr-xr-x` in octal? → **755**.
2. `chmod 644` gives? → `rw-r--r--` (owner read/write, others read-only).
3. On a **directory**, the **x** bit means? → **traverse/enter** it (cd through it).
4. `/tmp` is mode **1777** — what is the leading **1**? → the **sticky bit**.

---

## 11.8 Hard Links vs Symbolic (Soft) Links

Both let a file appear under more than one name, but they work **completely
differently** — a favourite interview and GATE distinction.

![A hard link is a second directory entry pointing to the SAME inode, so both names are equal and the inode link count is 2; a symbolic link is a separate file whose data is the target's path, with its own inode, and it dangles if the target is removed.](images/118_links.png)

### Hard link — a second name for the *same inode*
`ln target new_name` creates another **directory entry pointing to the same inode
number**. Both names are **equal peers** — there is no "original". The inode's
**link count** (`st_nlink`) goes up by one. The data is freed only when the link
count reaches **0** *and* no process has it open.
- **Cannot** cross filesystems (inode numbers are per-filesystem).
- **Cannot** (normally) link a **directory** (would risk cycles — §11.4).

### Symbolic (soft) link — a tiny file holding a *path*
`ln -s target new_name` creates a **new file with its own inode** whose *contents*
are the **path string** of the target. Following it means "go read that path".
- **Can** cross filesystems and **can** point to a **directory**.
- If the target is deleted/moved, the symlink **dangles** (points to nothing).

### Worked walk-through (watch the inode number and link count)

```text
$ echo hello > file.txt
$ ls -li file.txt
  1234567 -rw-r--r-- 1 nidhi ...  file.txt        # inode 1234567, link count = 1

$ ln file.txt hard.txt              # HARD link
$ ls -li file.txt hard.txt
  1234567 -rw-r--r-- 2 nidhi ... file.txt          # same inode 1234567,
  1234567 -rw-r--r-- 2 nidhi ... hard.txt          # link count now = 2

$ ln -s file.txt soft.txt           # SOFT link
$ ls -li soft.txt
  1234999 lrwxrwxrwx 1 nidhi ... soft.txt -> file.txt   # DIFFERENT inode, type 'l'

$ rm file.txt                        # remove the original name
$ cat hard.txt                       # -> "hello"  (data alive; link count now 1)
$ cat soft.txt                       # -> error: No such file  (DANGLING symlink)
```

| Property | Hard link | Symbolic (soft) link |
|----------|-----------|----------------------|
| Points to | the **inode** (data itself) | a **path/name** |
| Own inode? | **no** (shares target's) | **yes** (separate small file) |
| Affects link count? | **yes** (+1) | **no** |
| Cross filesystem? | **no** | **yes** |
| Link a directory? | **no** | **yes** |
| Target deleted → | data survives (count>0) | **dangles** (broken) |
| `ls -l` type char | `-` (normal) | `l` (link, shows `-> target`) |

> **Memory hook:** a **hard link is a joint bank account** (two names, one balance —
> money gone only when *both* close it). A **symlink is a sticky note saying "cash is
> in account #123"** — tear up the account and the note points to nothing.

### MCQs

1. Which link **shares the target's inode**? → **hard link**.
2. Which link **dangles** if the target is deleted? → **symbolic (soft) link**.
3. Creating a hard link changes the inode's? → **link count** (+1).
4. Which link can **cross filesystems / point to a directory**? → **symbolic**.

---

## 11.9 Metadata, Journaling, and Crash Consistency

### The consistency problem
A single logical operation (say **creating a file**) touches **several** on-disk
structures: allocate an inode, mark blocks used in the **bitmap**, add a **directory
entry**, update **free-space counts**. If the machine **crashes halfway** (after the
directory entry but before the bitmap update), the filesystem is now **inconsistent**
— e.g. a block marked free but actually in use. The old fix was **`fsck`**, a full
scan of the whole disk at boot — which took **hours** on large volumes.

### Journaling = write-ahead logging (the fix)
A **journaling filesystem** first writes a description of the intended changes to a
special **journal (log)** on disk, **then** applies them to their real locations.

```text
1. Write the intended metadata changes to the JOURNAL   (write-ahead)
2. Mark the journal transaction COMMITTED
3. Apply ("checkpoint") the changes to their real disk locations
4. Clear the journal entry
```

After a crash, the OS just **replays the journal** at boot: committed transactions
are re-applied; incomplete ones are discarded. Recovery takes **seconds**, not hours,
and the filesystem is always brought to a consistent state.

> **Memory hook:** journaling is **"write your intentions in a diary before you act."**
> If you faint mid-action, someone reads the diary and either finishes the job or
> tears out the unfinished page. This is the same **write-ahead logging (WAL)** idea
> as database recovery (DBMS M10) — first log, then do.

**ext4 journaling modes** (the classic trade-off):

| Mode | What's journaled | Safety | Speed |
|------|------------------|--------|-------|
| **journal** | **metadata + data** | safest | slowest (data written twice) |
| **ordered** (default) | **metadata only**, but data written **before** its metadata | good | good |
| **writeback** | **metadata only**, no ordering | weakest | fastest |

> **Copy-on-write (CoW) alternative:** newer filesystems (**ZFS, Btrfs, APFS**)
> never overwrite live data — they write new blocks and atomically flip a pointer, so
> the old version stays consistent until the switch. This gives crash consistency
> **plus** cheap **snapshots**, without a separate journal.

### MCQs

1. Journaling is another name for? → **write-ahead logging** (log first, then apply).
2. What does the OS do with the journal after a crash? → **replay** committed
   transactions (discard incomplete ones).
3. Default ext4 mode? → **ordered** (metadata journaled, data written first).
4. What replaces journaling in ZFS/Btrfs/APFS? → **copy-on-write** (+ snapshots).

---

## 11.10 Real File Systems Compared (FAT / NTFS / ext4 / XFS / APFS)

| Feature | **FAT32** | **NTFS** | **ext4** | **XFS** | **APFS** |
|---------|-----------|----------|----------|---------|----------|
| OS | DOS/Windows, USB drives | Windows | Linux (default many distros) | Linux (RHEL default) | macOS/iOS (2017+) |
| Core structure | **File Allocation Table** (linked) | **MFT** (Master File Table) | **inodes + extents** | **B+-tree extents**, allocation groups | **B-tree, copy-on-write** |
| **Journaling** | **none** | yes (metadata) | yes | yes (metadata) | **no — copy-on-write** |
| **Max file size** | **4 GB** | 16 EB (theory; huge) | **16 TiB** | **8 EiB** | 8 EiB |
| **Max volume** | ~2 TB | 256 TB+ | 1 EiB | 8 EiB | 8 EiB |
| Permissions/ACLs | **none** | **ACLs** | UNIX rwx + ACLs | UNIX rwx + ACLs | UNIX rwx + ACLs |
| Snapshots | no | shadow copies (VSS) | no | no (uses LVM) | **yes (native, cheap)** |
| Best at | **universal compatibility** | Windows features (encryption, compression) | reliable general Linux use | **huge files, parallel I/O** | **SSD, snapshots, encryption** |

> **The one everyone trips on: FAT32's 4 GB file limit.** Because FAT32 stores a
> file's size in a **32-bit** field, no single file can exceed **2³² − 1 ≈ 4 GB**.
> That's why you can't copy a 5 GB movie to a FAT32 USB stick — the fix is **exFAT**
> or **NTFS**. Also FAT has **no permissions and no journaling** — great for
> portability, poor for a system disk.

> **Quick picks:** cross-device USB → **exFAT/FAT**; Windows system → **NTFS**;
> general Linux → **ext4**; big-data / large-file Linux servers → **XFS**;
> Apple / SSD-first → **APFS**.

### MCQs

1. Filesystem with a **4 GB max file size**? → **FAT32**.
2. NTFS's central metadata structure? → the **MFT** (Master File Table).
3. Which filesystem uses **copy-on-write instead of journaling**? → **APFS**
   (also ZFS/Btrfs).
4. RHEL's default filesystem, tuned for large files? → **XFS**.

---

## 11.11 Real-World & Backend Perspectives

- **Everything is a file (UNIX philosophy).** Devices (`/dev/sda`), pipes, sockets,
  and even kernel state (`/proc`, `/sys`) present a **file interface** — so the same
  `read`/`write`/`fd` API drives disk, terminal, and network. This uniformity is why
  UNIX I/O feels so composable (pipes in M13/M14).
- **`inotify` / file watchers** power dev tools (webpack, `nodemon`) that rebuild on
  save — they hook the filesystem's change notifications.
- **fsync and durability.** A backend that must not lose data (a database, a message
  queue) calls **`fsync`** to force the OS page cache to disk — the same durability
  concern as journaling. Skipping it is a classic data-loss bug.
- **Object storage (S3) is not a filesystem.** It's a flat **key → blob** store with
  no real directories, no partial writes, and eventual consistency — understanding
  POSIX file semantics is exactly what tells you where S3 differs.
- **Containers** layer filesystems (OverlayFS): a read-only image layer + a writable
  top layer, using **copy-on-write** — the §11.9 idea again.

---

## 11.12 Tradeoffs, Common Mistakes, Edge Cases

**Common mistakes (exam + real life)**
- Saying the **inode stores the file name** — it does **not**; the *directory* maps
  name → inode number.
- Thinking a **hard link** is "a copy" — it's the **same inode**; edits show through
  both names.
- Forgetting **contiguous** allocation is the one with **external fragmentation**.
- Forgetting **linked** allocation has **no random access** (O(N) to reach block N).
- Reading `chmod` octal wrong: **r=4, w=2, x=1** (not r=1).
- Assuming FAT32 can hold a file > **4 GB** (it can't).

**Edge cases**
- A symlink can be **dangling** (target gone) yet still exist as a file.
- On a directory: **x without r** = you can open a file by exact name but can't
  **list** the directory; **r without x** = you can list names but can't **access**
  them.
- Deleting a file that a process still has **open** frees the *name* but not the
  *data* until the last fd closes (link count vs open count).

**Tradeoffs**

| Choice | Gains | Costs |
|--------|-------|-------|
| Contiguous allocation | fast sequential + direct access | external fragmentation, hard to grow |
| Indexed (inode) allocation | random access, no external frag. | index-block overhead, indirect reads for big files |
| Journaling (data mode) | crash-safe data | writes everything twice (slower) |
| Copy-on-write (APFS/ZFS) | snapshots + consistency | fragmentation, more space churn |

---

## 11.13 Exam, Interview & Coding Perspectives

**Exam (SEBI/RBI/GATE/C-DAC):** file-allocation method pros/cons and which one
fragments; the **inode indirect-pointer max-file-size** numerical; access methods;
directory-structure evolution; **octal permissions** and `chmod`; **hard vs soft
link** differences; journaling = write-ahead logging; FAT32's 4 GB limit.

**Interview:** "Hard vs symbolic link?" (same inode vs a path; link count; dangling);
"What's in an inode?" (metadata + block pointers, **not** the name); "How does a
journaling filesystem survive a crash?" (WAL + replay); "Why can't FAT32 hold a 5 GB
file?" (32-bit size field).

**Coding/practical:**
- `ls -li` shows the **inode number** and **link count** — the fastest way to *prove*
  hard vs soft links.
- `stat file` prints size, blocks, inode, permissions, and all timestamps.
- `df -i` shows **inode usage** — a disk can be "full" because it's **out of inodes**
  even with free space (millions of tiny files).
- `du` vs `ls`: `du` counts **blocks allocated** (may exceed apparent size for sparse
  files).

---

## 11.14 Concept Checks & MCQs

1. Where is a file's metadata stored on UNIX? → the **inode**.
2. Where is the file **name** stored? → in the **directory** (name → inode number).
3. Allocation method with best direct access but external fragmentation? →
   **contiguous**.
4. Allocation method with no random access? → **linked**.
5. Allocation method behind the UNIX inode? → **indexed**.
6. Inode pointer layout? → **12 direct + single + double + triple** indirect.
7. Block = 4 KB, pointer = 4 B → max file size? → **≈ 4 TiB** (2⁴², triple
   dominates).
8. Which indirect term dominates max file size? → **triple indirect**.
9. `rwxr-xr-x` in octal? → **755**.
10. `chmod 644` → symbolic? → `rw-r--r--`.
11. On a directory, **x** means? → **traverse/enter** it.
12. Leading **1** in mode `1777`? → **sticky bit**.
13. Hard link vs symlink — which shares the inode? → **hard link**.
14. Which link dangles when the target is deleted? → **symbolic**.
15. Journaling ≈ ? → **write-ahead logging** (log then apply).
16. Default ext4 journaling mode? → **ordered**.
17. Filesystem with a **4 GB** max file? → **FAT32** (32-bit size field).
18. NTFS's master metadata table? → **MFT**.
19. Filesystem using **copy-on-write** instead of journaling? → **APFS** (ZFS/Btrfs).
20. Access method that jumps to any block in O(1)? → **direct/random**.
21. Structure that makes a directory an **acyclic graph**? → a file with **multiple
    parents** (links).
22. Mechanism preventing early deletion of shared data? → **link/reference count**.
23. `df -i` reports? → **inode usage** (a disk can run out of inodes).
24. Practice: block = 1 KB, pointer = 4 B → max file size? → **≈ 16 GiB** (2³⁴, k=256).

**True/False**
- The inode stores the file name. → **False** (the directory does).
- A hard link creates a second copy of the data. → **False** (same inode).
- Contiguous allocation causes external fragmentation. → **True**.
- Linked allocation supports fast random access. → **False** (O(N) walk).
- FAT32 can store a 5 GB file. → **False** (4 GB cap).
- Journaling replays committed transactions after a crash. → **True**.

**Numerical (do it):**
> Block = **8 KB**, pointer = **8 B** → k = 8192/8 = **1024** pointers/block. Triple
> indirect = k³ × B = 2³⁰ × 2¹³ = **2⁴³ = 8 TiB** (dominant term), so max file size
> **≈ 8 TiB**. (Same shortcut: find k, then triple = k³ × B.)

---

## 11.15 One-Page Revision Sheet

```
FILE = named, persistent byte stream. Data = bytes; METADATA (type,size,perms,times,
  LINK COUNT) lives in the INODE. NAME lives in the DIRECTORY (name -> inode #).
  open() -> file descriptor (fd); kernel keeps per-proc fd table + system open-file
  table holding the OFFSET. read/write use the fd (no re-parsing the path).

TYPES: regular, directory(=list of name->inode), device/special, symlink.
  Windows types by EXTENSION; UNIX by MAGIC NUMBER (first bytes).

ACCESS: SEQUENTIAL(cassette, in-order) | DIRECT/RANDOM(CD skip, lseek O(1)) |
  INDEXED(book index: key->block).

DIRECTORIES: single(flat, clashes) -> two-level(per user) -> TREE(nested, one path)
  -> ACYCLIC GRAPH(multiple parents via links; needs LINK COUNT, ban dir cycles).

ALLOCATION:
  CONTIGUOUS  start+len; best seq+direct; EXTERNAL FRAG, can't grow  (row of seats)
  LINKED      each block -> next; NO random access; corrupt ptr kills rest  (FAT=ptrs in table)
  INDEXED     one index block lists data blocks; random access, no ext frag  (UNIX inode)

INODE = 12 DIRECT + 1 SINGLE + 1 DOUBLE + 1 TRIPLE indirect.  k = B / ptrsize.
  MAX SIZE (B=4KB, ptr=4B, k=1024): 12 + k + k^2 + k^3 blocks x B ≈ 4 TiB.
  Shortcut: triple dominates = k^3 x B = 2^30 x 2^12 = 2^42 = 4 TiB.
  (1KB block,k=256 -> 16 GiB.  8KB block,k=1024 -> 8 TiB.)

PERMISSIONS: rwx x (owner,group,others). r=4 w=2 x=1.  rwxr-xr-x=755, rw-r--r--=644.
  DIR: r=list names, w=create/delete, x=enter/traverse.  Sticky bit /tmp = 1777.
  chmod 754 file | chmod u+x file | chmod go-w file.

LINKS: HARD = same INODE, +1 link count, no cross-FS, no dir  (joint bank account).
  SOFT/symlink = own inode holding a PATH; cross-FS + dir OK; DANGLES if target gone
  (sticky note with an account number).

JOURNALING = WRITE-AHEAD LOG: log intent -> commit -> apply -> clear. Crash = REPLAY.
  ext4 modes: journal(data+meta,safe/slow) | ordered(default) | writeback(fast/weak).
  CoW (ZFS/Btrfs/APFS) = never overwrite + snapshots, no journal.

FILESYSTEMS: FAT32(no journal/perms, MAX FILE 4GB) | NTFS(MFT,journal,ACLs) |
  ext4(inode+extents,16TiB) | XFS(huge files,8EiB) | APFS(CoW,snapshots,SSD).
```

### Flash cards

| Front | Back |
|-------|------|
| Where is file metadata? | The inode |
| Where is the file name? | The directory (name → inode #) |
| Best direct access allocation? | Contiguous |
| No-random-access allocation? | Linked |
| UNIX inode uses which allocation? | Indexed (indirect blocks) |
| Inode pointers layout? | 12 direct + single + double + triple |
| Max size, 4 KB block, 4 B ptr? | ≈ 4 TiB (triple = 2⁴²) |
| `rwxr-xr-x` octal? | 755 |
| Hard link shares? | The inode (link count +1) |
| Symlink stores? | A path (dangles if target gone) |
| Journaling = ? | Write-ahead logging → replay on crash |
| FAT32 max file? | 4 GB (32-bit size field) |

### Spaced repetition
- **24-hour:** redo the inode max-file-size numerical for 4 KB and 1 KB blocks;
  recite the three allocation methods' pros/cons.
- **7-day:** explain hard vs soft links (inode/link count/dangling); convert three
  mode strings to octal and back; explain journaling as WAL.
- **30-day:** given a workload (USB stick, Windows disk, big-data Linux server,
  Apple SSD), pick the filesystem and justify it; walk the directory-structure
  evolution.

---

## 11.16 Summary

A **file system** turns a raw array of disk blocks into **named, persistent files**.
Metadata (type, size, permissions, timestamps, **link count**) lives in the
**inode**; the **name** lives in a **directory** that maps name → inode number — a
separation that makes **hard links** possible. Files are reached by **sequential,
direct, or indexed** access, and organised in directories that evolved
**single → two-level → tree → acyclic-graph**. Disk space is handed out by
**contiguous** (fast, fragments), **linked** (grows freely, no random access), or
**indexed** allocation — the last being the UNIX **inode** with **12 direct + single
+ double + triple indirect** pointers, giving a **≈ 4 TiB** max file on a 4 KB/4-byte
system (triple indirect dominates: **2⁴²**). We read **UNIX permissions** as octal
(**755, 644**), distinguished **hard vs symbolic links** by inode and link count,
and saw **journaling = write-ahead logging** keep the filesystem consistent across
crashes. Finally we compared **FAT32, NTFS, ext4, XFS, and APFS**.

Next, **Module 12 — Disk Management** goes one layer down to the **physical** device
these files sit on: HDD vs SSD vs NVMe, and the **disk-scheduling** algorithms
(FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK) that decide the order of head movement — the
performance floor beneath everything we just built.

> **You have mastered this module when** you can: state what lives in an inode vs a
> directory; compare the three allocation methods and name the one that fragments;
> compute a max file size from block and pointer sizes cold; convert permission
> strings to octal and back; explain hard vs soft links with the inode/link-count
> difference; and explain journaling as write-ahead logging — all without notes.
