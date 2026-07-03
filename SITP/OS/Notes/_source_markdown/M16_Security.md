---
title: "Module 16 — Security & Protection"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 16 — Security & Protection

> **Where this module sits.**
> Every earlier module quietly assumed one thing: that programs **can't trample each
> other or the kernel**. Dual-mode operation (§M3), memory protection and paging
> (§M9–M10), file permissions (§M11), and the isolation of containers (§M14) are all
> *security mechanisms*. This module pulls them together into one coherent picture:
> **how an OS protects itself and its users** — the hardware **privilege rings** and
> **dual-mode** boundary; **authentication vs authorization**; the access-control
> models **DAC / MAC / RBAC**; Linux's fine-grained **capabilities**; the **MAC**
> systems **SELinux and AppArmor**; **secure boot**; **sandboxing** with **seccomp**;
> why **containers are a weaker security boundary** than VMs; and the **common OS
> attacks** (privilege escalation, buffer overflow, TOCTOU) these defenses exist to
> stop. For a SEBI IT / cyber / backend role, this is the module that ties the whole
> course to the real world of breaches and defenses.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★★      | ★★★★      | ★★★★    |

**Most-asked PYQ / interview concepts:** **protection rings** & **dual-mode**
(user/kernel); **authentication vs authorization** (the classic confusion);
**DAC vs MAC vs RBAC**; **principle of least privilege**; **Linux capabilities** (vs
all-or-nothing root); **SELinux vs AppArmor** (label vs path MAC); **secure boot** &
chain of trust; **seccomp** sandboxing; **container vs VM** as a security boundary;
**buffer overflow** (+ defenses: NX/DEP, ASLR, canaries), **privilege escalation**,
**TOCTOU** race.

---

## 16.1 Privilege Rings and Dual-Mode Operation

### The hardware foundation: rings

CPUs enforce protection with **privilege rings** — hardware modes with different
powers. x86 defines **four rings, 0–3**:

```text
   Ring 0  = KERNEL       (most privileged: all instructions, all memory, all I/O)
   Ring 1  = (device drivers — rarely used)
   Ring 2  = (rarely used)
   Ring 3  = USER          (least privileged: no direct hardware, restricted memory)
```

In practice mainstream OSes use only **two**: **Ring 0 (kernel)** and **Ring 3
(user)** — this is **dual-mode operation** (§M3). A **mode bit** in the CPU says
which mode you're in. **Privileged instructions** (halt, set the page table, do raw
I/O, mask interrupts) are **only legal in Ring 0**; attempting them from Ring 3
**traps** to the kernel.

> **Memory hook:** think of a **castle with concentric walls**. **Ring 0** is the
> keep (the kernel — full power); **Ring 3** is the outer courtyard (user programs).
> The **only gate** between them is the **system call** — a controlled, guarded
> doorway. Rings 1 and 2 are unused corridors most OSes skip. **Virtualization added
> "Ring −1"** (hypervisor mode, VMX root) *below* the guest kernel — the guest OS
> thinks it owns Ring 0, but the hypervisor sits beneath it (§M1, M17).

![Protection rings and the dual-mode boundary: user programs run in Ring 3 with no direct hardware access; the kernel runs in Ring 0 with full privilege. The only controlled crossing is a system call (trap), which switches the mode bit to kernel mode. A privileged instruction attempted from user mode traps. Hypervisor mode (Ring -1) sits below the guest kernel.](images/149_protection_rings.png)

### Why dual-mode is *the* core protection

Without a hardware user/kernel split, any buggy or malicious program could:
- run **privileged instructions** (halt the CPU, reprogram the MMU),
- read/write **any physical memory** (steal another process's data or the kernel's),
- talk to **devices** directly.

Dual-mode + the **MMU/paging** (§M9) confine each process to **its own virtual
address space** and force every hardware request through the **kernel via a system
call**, where it can be checked. **This single mechanism is the root of all OS
security.**

### MCQs

1. How many privilege rings on x86, and which two are actually used? → **four (0–3)**;
   OSes use **Ring 0 (kernel)** and **Ring 3 (user)**.
2. What is dual-mode operation? → CPU runs in **user** or **kernel** mode; privileged
   instructions only in kernel mode.
3. The only controlled way from user to kernel mode? → a **system call** (trap).
4. What confines a process to its own memory? → the **MMU / paging** (virtual address
   space).

---

## 16.2 Authentication vs Authorization

Two words constantly confused — keep them crisp.

- **Authentication (AuthN) — "Who are you?"** Proving **identity**. Factors:
  **something you know** (password, PIN), **something you have** (token, phone,
  smartcard), **something you are** (biometrics — fingerprint, face). **MFA** =
  combining two+ factors.
- **Authorization (AuthZ) — "What are you allowed to do?"** Deciding whether an
  *already-authenticated* identity may perform an action (read this file, call this
  API). This is what **access control** (§16.3) enforces.

> **Memory hook:** **AuthN = login (who you are); AuthZ = permissions (what you can
> do).** You **authenticate once** (prove identity), then get **authorized on every
> action**. Order matters: **authenticate first, authorize second** — you can't check
> permissions for an unknown identity.

- **Accounting/Audit** completes the trio (**AAA**): log *who did what, when* — the
  forensic trail after AuthN + AuthZ.

### MCQs

1. Authentication answers which question? → **"Who are you?"** (identity).
2. Authorization answers which question? → **"What may you do?"** (permissions).
3. The three authentication factors? → **know / have / are** (password / token /
   biometric).
4. What is MFA? → using **two or more different factors**.

---

## 16.3 Access Control Models — DAC, MAC, RBAC

**Access control** is how the OS enforces authorization: given a **subject** (user /
process) requesting an **operation** on an **object** (file, socket), decide
**allow/deny**. Three models dominate.

| Model | Who sets the policy? | Idea | Example |
|-------|----------------------|------|---------|
| **DAC** (Discretionary) | the **owner** | owners grant/revoke access at their discretion | UNIX `rwx` file permissions, ACLs |
| **MAC** (Mandatory) | a **central admin / system policy** | system-wide labels; users **cannot** override | SELinux, AppArmor, military "Top Secret" |
| **RBAC** (Role-Based) | admin assigns **roles** | permissions attach to **roles**, users get roles | AWS IAM roles, DB `GRANT role` |

- **DAC** is flexible and familiar (you `chmod` your own files) but **weak**: a
  tricked or compromised program runs with the user's rights and can leak/spread
  (malware, trojans).
- **MAC** is strict: even **root** is bound by the system policy — a process labeled
  "web-server" can touch *only* what the policy permits, no matter who owns the file.
  Strong against compromise, harder to administer.
- **RBAC** scales administration: instead of granting each user directly, you define
  **roles** (e.g. "teller", "auditor") and assign users to roles — the model behind
  most enterprise and cloud IAM.

> **Memory hook:** **DAC = the owner decides** (discretionary). **MAC = the system
> decides, and nobody — not even root — can override** (mandatory). **RBAC = your
> job/role decides**. DAC is a suggestion; MAC is the law; RBAC is your job title.

![Access control models: DAC — the file owner grants rights (UNIX rwx), flexible but a compromised process inherits the user's power. MAC — a central system policy labels subjects and objects; even root is confined. RBAC — permissions attach to roles, and users are assigned roles, scaling administration.](images/150_access_control_models.png)

- Related term: **ABAC** (Attribute-Based) — decisions from **attributes**
  (department, time, device, location); the most flexible/expressive, common in
  modern cloud policy engines.

### The principle of least privilege (PoLP)

The unifying rule behind all of this: **every subject should have the minimum
privileges needed to do its job — no more.** A web server shouldn't run as root; a
backup job needs read, not write; a container should drop every capability it doesn't
use. PoLP shrinks the **blast radius** of any bug or breach.

### MCQs

1. UNIX `rwx` permissions are which model? → **DAC** (owner's discretion).
2. Model where even root can't override policy? → **MAC**.
3. Model where permissions attach to roles? → **RBAC**.
4. State the principle of least privilege. → give each subject the **minimum
   privileges** it needs.

---

## 16.4 Linux Capabilities — Breaking Up Root

Traditional UNIX is **all-or-nothing**: you're either **root (UID 0, can do
anything)** or an ordinary user. That violates least privilege — a program that only
needs to **bind to port 80** (a privileged port) had to run as **full root**.

**Linux capabilities** split root's power into ~40 **independent units** you can grant
individually:

| Capability | Grants just… |
|------------|--------------|
| `CAP_NET_BIND_SERVICE` | bind to ports < 1024 |
| `CAP_NET_ADMIN` | configure networking (interfaces, routing) |
| `CAP_SYS_ADMIN` | a huge grab-bag (mounts, etc.) — the "new root", avoid it |
| `CAP_CHOWN` | change file ownership |
| `CAP_KILL` | send signals to any process |
| `CAP_SYS_TIME` | set the system clock |

So a web server can get **only `CAP_NET_BIND_SERVICE`** and run as an unprivileged
user — if it's hacked, the attacker gets that one power, not all of root.

> **Memory hook:** **capabilities shatter the single "root key" into a keyring of
> small keys.** Hand out only the keys a program needs (least privilege). Docker uses
> this: containers start with a **reduced capability set** and `--cap-drop` /
> `--cap-add` tune it. (Beware **`CAP_SYS_ADMIN`** — it's so broad it's effectively
> root.)

### MCQs

1. Problem with traditional root that capabilities fix? → root is **all-or-nothing**;
   capabilities give **fine-grained** privileges.
2. Capability to bind to port 80 without full root? → **`CAP_NET_BIND_SERVICE`**.
3. Which capability is so broad it's "the new root"? → **`CAP_SYS_ADMIN`**.

---

## 16.5 SELinux vs AppArmor — Mandatory Access Control in Linux

Standard Linux permissions are **DAC**. **SELinux** and **AppArmor** add a **MAC**
layer *on top* (via the **Linux Security Modules / LSM** hook framework): even if the
DAC `rwx` bits would allow an action, the MAC policy can still **deny** it — confining
each program to exactly what it should ever do.

| | **SELinux** | **AppArmor** |
|---|-------------|--------------|
| **Policy is by** | **labels/contexts** on every subject & object | **file paths** (profiles per program) |
| **Origin/default** | NSA; default on **RHEL/Fedora/Android** | Canonical; default on **Ubuntu/SUSE** |
| **Granularity** | very fine (types, roles, MLS) | coarser, per-program profiles |
| **Learning curve** | steep (labels everywhere) | gentler (readable path rules) |

- **SELinux** labels everything (`user:role:type:level`) and allows an action only if
  a rule permits that subject **type** to act on that object **type**. Powerful and
  precise, but complex — hence the meme "just `setenforce 0`" (which you should *not*
  do).
- **AppArmor** confines a program by a **profile listing the paths** it may read/
  write/execute — much easier to read and write, slightly less rigorous (path-based,
  so it can be fooled by hard links/renames in edge cases).

> **Memory hook:** **SELinux = label-based** ("what *type* are you?"), **AppArmor =
> path-based** ("what *files/paths* may you touch?"). SELinux is stricter and harder;
> AppArmor is simpler and friendlier. Both are **MAC via LSM** and both confine a
> compromised service so a web-server exploit can't read `/etc/shadow`.

### MCQs

1. Are default Linux permissions DAC or MAC? → **DAC**; SELinux/AppArmor add **MAC**.
2. SELinux enforces via ___; AppArmor via ___. → **labels/contexts** ; **file
   paths** (profiles).
3. What framework do they hook into? → **LSM (Linux Security Modules)**.
4. Why MAC on top of DAC? → to **confine** a compromised process to only its intended
   actions (even root/allowing DAC bits can be overruled).

---

## 16.6 Secure Boot and the Chain of Trust

Security must start **before the OS even loads** — otherwise malware in the
bootloader (a **rootkit/bootkit**) owns the machine beneath the OS's defenses.

**Secure Boot** (a **UEFI** feature) enforces a **chain of trust**: each stage
**cryptographically verifies the signature** of the next before running it.

```text
UEFI firmware (trusted, keys in hardware)
   -> verifies signature of  BOOTLOADER  (e.g. shim/GRUB)
        -> verifies signature of  KERNEL
             -> kernel verifies signed  MODULES/drivers
Any broken signature -> refuse to boot (or drop to recovery).
```

- Keys live in firmware (Platform Key, KEK, allowed/forbidden databases); only
  code signed by a trusted key runs.
- **Measured boot / TPM:** a **TPM** chip records a hash ("measurement") of each
  stage into **PCRs**; **remote attestation** lets a server prove *what* it booted.
  This underpins disk encryption unlock and confidential computing.

> **Memory hook:** **secure boot = a relay race where each runner checks the next
> runner's ID before handing off the baton.** The root of trust is the **firmware**;
> if any stage's **signature** fails, the chain breaks and boot stops — so a bootkit
> can't insert itself below the OS.

### MCQs

1. What does Secure Boot verify at each stage? → the **cryptographic signature** of
   the next stage (chain of trust).
2. Where is the root of trust? → the **UEFI firmware** (keys in hardware).
3. Chip that measures/attests boot state? → the **TPM** (PCRs, remote attestation).

---

## 16.7 Sandboxing and seccomp

A **sandbox** confines a program to a restricted environment so that even if it's
compromised, it **can't reach the rest of the system**. The tightest OS lever for
this is **limiting which system calls a process may make** — because the syscall
boundary (§16.1) is the *only* way a process asks the kernel to do anything.

**seccomp (secure computing mode)** does exactly that:

- **seccomp strict mode:** the process may call **only** `read`, `write`, `_exit`,
  and `sigreturn` — anything else → the kernel **kills** it.
- **seccomp-BPF (the useful mode):** attach a **BPF filter** that inspects each
  syscall (number + arguments) and returns **allow / deny / kill / trap / errno**.
  This lets you whitelist the ~40 syscalls a server actually needs and block the rest
  (e.g. block `ptrace`, `mount`, `keyctl`).

> **Memory hook:** **seccomp = a bouncer at the syscall door with a guest list.** The
> program can only make the calls on the list; every other request gets it thrown
> out (killed). Fewer allowed syscalls = smaller **kernel attack surface**.

**The modern sandbox stacks these layers** (defense in depth): **namespaces** (isolate
view) + **cgroups** (limit resources) + **capabilities** (drop root powers) +
**seccomp** (whitelist syscalls) + **MAC** (SELinux/AppArmor confine). This is exactly
how Docker/Kubernetes, Chrome's renderer processes, and systemd service hardening
sandbox untrusted code.

![Layered sandboxing (defense in depth): a process is wrapped by namespaces (isolate what it sees), cgroups (limit resources), capabilities (drop unneeded root powers), seccomp (whitelist allowed syscalls), and MAC/SELinux (confine actions). Each layer shrinks the attack surface so a compromise of the app can't reach the host.](images/151_sandboxing_layers.png)

### MCQs

1. What does seccomp restrict? → the **system calls** a process may make.
2. seccomp strict mode allows only? → `read`, `write`, `_exit`, `sigreturn`.
3. What makes seccomp-BPF flexible? → a **BPF filter** per-syscall (allow/deny/kill/
   errno by number + args).
4. Name the layers of a modern sandbox. → **namespaces + cgroups + capabilities +
   seccomp + MAC**.

---

## 16.8 Containers as a Security Boundary (weaker than a VM)

Because §M14's **namespaces + cgroups + capabilities + seccomp** wrap a process
tightly, containers *feel* isolated. But there is a fundamental limit:

> **Containers share the host kernel.** A **VM** runs its own **guest kernel** on a
> hypervisor, so the isolation boundary is the small, hardware-enforced
> **hypervisor** (Ring −1). A **container's** boundary is the **entire Linux kernel's
> syscall surface** — **millions of lines**. A single kernel bug (a "**container
> escape**") lets an attacker break out onto the host and every other container.

| | **VM** | **Container** |
|---|--------|---------------|
| Isolated by | **hypervisor** (own guest kernel) | **kernel namespaces/cgroups** (shared kernel) |
| Attack surface | small hypervisor interface | **huge** (all kernel syscalls) |
| Isolation strength | **strong** | **weaker** |
| Weight / startup | heavy / seconds | light / milliseconds |

> **Memory hook:** **a VM is a separate house; a container is a locked room in a
> shared house.** Rooms are cheap and fast, but they share the **same
> plumbing/wiring (the host kernel)** — break the shared infrastructure and you're
> into every room. For **untrusted, multi-tenant** workloads, use **VMs / micro-VMs
> (Firecracker) / gVisor (a user-space kernel)** for a stronger boundary; harden
> containers with seccomp + user namespaces + read-only rootfs + dropped
> capabilities + non-root.

### MCQs

1. Why is a container a weaker boundary than a VM? → it **shares the host kernel**;
   the attack surface is the whole kernel.
2. Breaking out of a container onto the host is called? → a **container escape**.
3. Stronger isolation for untrusted workloads? → **VMs / micro-VMs (Firecracker) /
   gVisor**.

---

## 16.9 Common OS Attacks (and the Defenses)

The protections above exist to stop specific attacks. Know these three cold.

### 16.9.1 Buffer overflow (memory-safety attack)

Writing **past the end of a buffer** overwrites adjacent memory. Classic **stack
smashing**: overflow a local array to overwrite the **return address**, redirecting
execution to attacker code (shellcode). This is the single most historically
important OS attack and ties directly to **memory protection (§M9/M10)**.

```text
void f(char *input) {
    char buf[64];
    strcpy(buf, input);   // NO bounds check!
}                         // if input > 64 bytes, it overwrites saved return
                          // address on the stack -> jump anywhere the attacker wants
```

**Defenses (layered):**
- **Stack canaries** — a random guard value placed before the return address;
  corrupted canary at return → abort.
- **NX / DEP (No-eXecute / Data Execution Prevention)** — mark the **stack/heap
  non-executable** (a paging permission bit, §M10) so injected data can't run as code.
- **ASLR (Address Space Layout Randomization)** — randomize stack/heap/library
  addresses each run, so the attacker can't predict where to jump.
- **Memory-safe languages** (Rust, Go, Java) — bounds-checked; eliminate the class.

> **Memory hook:** the buffer-overflow arms race: **canary** (detect the smash) +
> **NX/DEP** (can't run injected data) + **ASLR** (can't find the target) — three
> independent layers, all leaning on **hardware memory protection** from §M9/M10.

### 16.9.2 Privilege escalation

Gaining **more rights than you were granted** — the goal of most attacks.

- **Vertical:** normal user → **root/kernel** (e.g. exploit a **setuid** binary, a
  kernel bug, or an over-broad capability). This is why least privilege,
  capabilities, seccomp, and MAC matter — they cap what a compromised process can
  become.
- **Horizontal:** access **another user's** data at the same privilege level.

Common vectors: a **setuid-root** program with a bug (runs as root regardless of
caller), a vulnerable kernel driver, or a mis-set capability. Defense = **least
privilege everywhere** (drop privileges early, minimal setuid, capabilities not root,
MAC confinement, patching).

### 16.9.3 TOCTOU (Time-Of-Check to Time-Of-Use)

A **race condition** (§M15) used as a security exploit: a program **checks**
permission on a resource, then **uses** it — but the resource **changes in the gap**.

```text
if (access("/tmp/file", W_OK) == 0) {   // TIME-OF-CHECK: "may this user write it?"
    // <-- attacker swaps /tmp/file for a symlink to /etc/passwd here
    fd = open("/tmp/file", O_WRONLY);    // TIME-OF-USE: now writes /etc/passwd!
}
```

The check and the use are **not atomic**; an attacker exploits the window (often by
swapping a symlink). Defense: **operate atomically** — `open()` first then check the
**file descriptor** (`fstat` on the fd, not the path), use `O_NOFOLLOW`, avoid
check-then-act on filenames.

> **Memory hook:** **TOCTOU = "checked the ID at the door, but a different person
> walked in."** The fix is to **check and act on the *same* handle atomically**, not
> to re-look-up the name.

### MCQs

1. Overwriting a return address via a too-long input? → **(stack) buffer overflow**.
2. Three buffer-overflow defenses? → **canaries, NX/DEP, ASLR** (+ memory-safe
   languages).
3. Which paging bit powers NX/DEP? → the **no-execute** page permission (§M10).
4. User → root is which escalation? → **vertical** privilege escalation.
5. Check-then-use race on a file? → **TOCTOU**; fix by **atomic** fd-based operations.

---

## 16.10 Real-World & Backend Perspectives

- **Every production hardening checklist** is this module: run services **non-root**,
  **drop capabilities**, apply a **seccomp** profile, enable **SELinux/AppArmor**,
  use **read-only root filesystems**, and enforce **least privilege** IAM (RBAC/ABAC)
  in the cloud.
- **Container security (very common interview ground):** the layered sandbox (§16.7)
  plus the "container ≠ VM" boundary (§16.8) — real incidents (e.g. runc/Dirty
  COW-style bugs) are **container escapes**.
- **Cloud IAM** is **RBAC/ABAC + least privilege** at scale (AWS IAM roles/policies);
  most cloud breaches are **over-broad permissions** (a `*` policy) — an authorization
  failure, not a hacked password.
- **Memory-safety** is why the industry is moving security-critical code to **Rust**
  (browsers, kernels, Android) — it eliminates the buffer-overflow class from §16.9.1.
- **Secure/measured boot + TPM** underpin disk encryption, device attestation, and
  **confidential computing** (encrypted VMs) in modern data centres.
- **Zero trust / defense in depth:** never rely on one control; assume any single
  layer can fail (exactly why sandboxes stack §16.7's layers).

---

## 16.11 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** confusing **authentication** (who) with **authorization** (what) — the
  #1 exam and interview slip.
- **Mistake:** thinking **root = kernel mode**. Root is a **user-space** identity
  (still Ring 3); the kernel (Ring 0) is a separate boundary. A root process still
  makes syscalls.
- **Mistake:** treating a **container like a VM** for security — it's a **weaker**
  boundary (shared kernel).
- **Mistake:** running everything as **root** "to avoid permission errors" — the
  opposite of least privilege; use **capabilities**.
- **Mistake:** using `access()` then `open()` (TOCTOU) — operate on the **fd**.
- **Tradeoff:** **security vs usability/performance** — MAC (SELinux) is strong but
  hard to administer; more sandbox layers add overhead; canaries/ASLR add tiny cost.
  Good security minimizes friction (least privilege by default).
- **Edge case:** **DAC** lets a tricked program leak data with the user's rights —
  precisely why **MAC** exists to override it.
- **Edge case:** disabling SELinux (`setenforce 0`) "to make it work" removes your
  MAC layer — a common real-world security regression.

---

## 16.12 Exam, Interview & Coding Perspectives

- **SEBI IT / cyber / RBI (very high yield):** authentication vs authorization; DAC
  vs MAC vs RBAC; buffer overflow + defenses (ASLR/DEP/canary); privilege escalation;
  secure boot; least privilege; CIA triad (confidentiality/integrity/availability).
- **GATE:** lighter — mainly the protection/dual-mode and access-matrix (access
  control list vs capability list) concepts.
- **Interview (backend/infra/security):**
  - "AuthN vs AuthZ?" → who are you vs what can you do.
  - "DAC vs MAC vs RBAC?" → owner vs system-policy vs role.
  - "Why are containers less secure than VMs?" → shared host kernel, huge attack
    surface.
  - "How would you sandbox untrusted code?" → namespaces + cgroups + drop caps +
    seccomp + MAC (+ VM/gVisor if truly untrusted).
  - "Explain a buffer overflow and its defenses." → overwrite return addr; canary /
    NX / ASLR.
  - "What is TOCTOU?" → check-then-use race; fix with atomic fd operations.
- **Coding/practical:** `capsh --print`, `getcap`/`setcap`, `docker run
  --cap-drop=ALL --security-opt seccomp=profile.json`, `getenforce`/`aa-status`,
  `checksec` (canary/NX/PIE/ASLR of a binary), `mount /proc` for `/proc/<pid>/status`
  seccomp state.

---

## 16.13 Concept Checks & MCQs (test yourself)

1. x86 rings, and the two used? → **0–3**; **Ring 0 (kernel)** + **Ring 3 (user)**.
2. Dual-mode: privileged instructions run only in? → **kernel mode (Ring 0)**.
3. AuthN vs AuthZ? → **who you are** vs **what you may do**.
4. Three authentication factors? → **know / have / are**.
5. DAC vs MAC vs RBAC? → **owner decides** / **system policy (even root bound)** /
   **role-based**.
6. Principle of least privilege? → **minimum privileges** needed, no more.
7. Fix for all-or-nothing root? → **Linux capabilities**.
8. Capability to bind port 80? → **`CAP_NET_BIND_SERVICE`**.
9. SELinux enforces via ___; AppArmor via ___. → **labels** ; **paths**.
10. Framework SELinux/AppArmor hook into? → **LSM**.
11. What does Secure Boot verify? → each stage's **cryptographic signature** (chain
    of trust); root = **firmware**.
12. What does seccomp restrict? → the **syscalls** a process can make.
13. Modern sandbox layers? → **namespaces + cgroups + capabilities + seccomp + MAC**.
14. Container vs VM security? → container **shares host kernel** (weaker); VM has its
    **own kernel** (stronger).
15. Breaking out of a container? → a **container escape**.
16. Buffer overflow overwrites the ___? → **return address** (stack smashing).
17. Three overflow defenses? → **canary, NX/DEP, ASLR**.
18. Vertical vs horizontal escalation? → to **higher privilege (root)** vs **another
    peer user**.
19. Check-then-use file race? → **TOCTOU** (fix: atomic fd ops).
20. Is root the same as kernel mode? → **No** (root is a user identity, still Ring 3).

**True/False**
- Authorization happens before authentication. → **False** (authenticate first).
- Under MAC, root can override the policy. → **False** (that's the point).
- A container isolates as strongly as a VM. → **False** (shared kernel).
- NX/DEP relies on a page permission bit. → **True**.
- ASLR randomizes memory layout each run. → **True**.
- Linux capabilities are all-or-nothing like root. → **False** (fine-grained).
- TOCTOU is a type of race condition. → **True**.

---

## 16.14 One-Page Revision Sheet

```
RINGS: x86 has 0-3; OS uses Ring0=KERNEL + Ring3=USER = DUAL MODE.
  privileged instrs only in Ring0; user->kernel ONLY via SYSCALL (trap).
  MMU/paging confines each process to its own address space. (hypervisor = Ring -1)
  NOTE: root != kernel mode. Root is a user identity, still Ring 3.

AUTHN vs AUTHZ:  AuthN = WHO ARE YOU (identity; know/have/are; MFA=2+ factors).
  AuthZ = WHAT MAY YOU DO (permissions). Authenticate FIRST, authorize each action.
  AAA = + Accounting/audit.

ACCESS CONTROL:
  DAC = owner decides (UNIX rwx/ACL) - flexible, weak (compromised proc = user rights)
  MAC = system policy, EVEN ROOT BOUND (SELinux/AppArmor) - strong, complex
  RBAC = permissions via ROLES (cloud IAM). ABAC = attribute-based.
  PRINCIPLE OF LEAST PRIVILEGE = minimum rights needed -> smaller blast radius.

LINUX CAPABILITIES = split root into ~40 units (CAP_NET_BIND_SERVICE=port<1024,
  CAP_NET_ADMIN, CAP_SYS_ADMIN='new root'/avoid). Docker --cap-drop/--cap-add.

SELINUX vs APPARMOR (both MAC via LSM, on top of DAC):
  SELinux = LABEL/context based (strict, hard; RHEL/Android).
  AppArmor = PATH/profile based (simpler; Ubuntu/SUSE).

SECURE BOOT (UEFI): CHAIN OF TRUST - each stage verifies next's SIGNATURE
  firmware->bootloader->kernel->modules. root of trust=firmware. TPM=measure/attest.

SANDBOX = confine. SECCOMP = restrict SYSCALLS (strict: read/write/_exit/sigreturn;
  seccomp-BPF: filter per syscall). LAYERS (defense in depth):
  namespaces + cgroups + capabilities + seccomp + MAC.

CONTAINER vs VM (security): container SHARES host kernel -> huge attack surface,
  WEAKER; VM = own guest kernel on hypervisor -> STRONGER. escape=container escape.
  untrusted -> VM / micro-VM (Firecracker) / gVisor.

ATTACKS:
  BUFFER OVERFLOW: overwrite return addr (stack smash). Defenses: CANARY + NX/DEP
    (non-exec page bit) + ASLR (randomize) + memory-safe langs (Rust/Go).
  PRIV ESCALATION: vertical(user->root, setuid/kernel bug) / horizontal(peer user).
  TOCTOU: check-then-use RACE (access() then open()); fix = atomic fd ops (fstat fd).
```

### Flash cards

| Front | Back |
|-------|------|
| Rings used by an OS? | 0 (kernel) + 3 (user) = dual mode |
| Root vs kernel mode? | root = user identity (Ring 3), not kernel mode |
| AuthN vs AuthZ? | who you are vs what you may do |
| DAC / MAC / RBAC? | owner / system policy (root bound) / role |
| Least privilege? | minimum rights needed |
| Fix for all-or-nothing root? | Linux capabilities |
| SELinux vs AppArmor? | labels vs file paths (both MAC/LSM) |
| Secure boot verifies? | each stage's signature (chain of trust) |
| seccomp restricts? | which syscalls a process can make |
| Sandbox layers? | namespaces+cgroups+caps+seccomp+MAC |
| Container vs VM boundary? | shared kernel (weak) vs own kernel (strong) |
| Buffer overflow defenses? | canary, NX/DEP, ASLR |
| TOCTOU? | check-then-use race; fix with atomic fd ops |

### Spaced repetition
- **24-hour:** recite AuthN-vs-AuthZ, DAC/MAC/RBAC, and the three buffer-overflow
  defenses.
- **7-day:** explain capabilities, SELinux-vs-AppArmor, secure boot's chain of trust,
  and why a container is weaker than a VM.
- **30-day:** given "sandbox this untrusted binary" or "harden this service," list
  the layered controls (least privilege, caps, seccomp, MAC, non-root) from memory.

---

## 16.15 Summary

OS security rests on one hardware idea: **privilege rings / dual-mode**, where user
code (Ring 3) can reach the powerful kernel (Ring 0) **only through a system call**,
and the **MMU** confines each process to its own memory. On top of that, we separate
**authentication** ("who are you?") from **authorization** ("what may you do?"), and
enforce authorization with **access-control models — DAC** (owner decides, flexible
but weak), **MAC** (system policy binds even root — SELinux by **labels**, AppArmor
by **paths**), and **RBAC** (permissions via roles) — all governed by the **principle
of least privilege**. Linux refines this with **capabilities** (root split into
fine-grained powers), and hardens boot itself with **Secure Boot's chain of trust**
(each stage verifies the next's signature, rooted in firmware/TPM). Modern
**sandboxing stacks layers** — namespaces, cgroups, capabilities, **seccomp**
(syscall whitelisting), and MAC — but a **container remains a weaker boundary than a
VM** because it **shares the host kernel**. Finally, these defenses exist to stop real
**attacks**: **buffer overflows** (beaten by canaries, **NX/DEP**, **ASLR**),
**privilege escalation** (beaten by least privilege), and **TOCTOU** races (beaten by
atomic fd operations).

This module closes the core-OS arc: from what an OS *is* (M1) to how it stays *safe*.
Next, **Module 17 — Virtualization & Containers** builds directly on M14's namespaces/
cgroups and this module's isolation boundaries to explain the technology running the
entire cloud.

> **You have mastered this module when** you can: explain rings/dual-mode and why
> root ≠ kernel mode; distinguish authentication from authorization; compare
> DAC/MAC/RBAC and state least privilege; explain Linux capabilities, SELinux vs
> AppArmor, secure boot, and seccomp; argue why a container is a weaker boundary than
> a VM; and describe buffer overflow (with defenses), privilege escalation, and
> TOCTOU — all without notes.
