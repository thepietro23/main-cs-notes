---
title: "Module 20 — The Backend-Engineering Perspective (High-Concurrency Servers as OS Problems)"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 20 — The Backend-Engineering Perspective (High-Concurrency Servers as OS Problems)

> **Where this module sits.**
> A web server has one job: **handle thousands of network connections at once**,
> fast and without falling over. Every technique that makes that possible is a
> direct application of this course. A connection is a **file descriptor** (M11);
> serving it is **I/O management** (M13); choosing who runs next is **CPU
> scheduling** (M6); a worker is a **process/thread** (M4/M5); protecting shared
> state needs **synchronization** (M7). This module retraces the evolution of
> server architecture — **process-per-connection → thread-per-connection →
> event loop** — through the famous **C10k problem**, the I/O-multiplexing
> syscalls (**select / poll / epoll / io_uring**), the two canonical servers
> (**Nginx** vs **Apache**), and **load balancing**. The goal: when an interviewer
> asks "why is Nginx faster than Apache?" or "what is `epoll`?", you answer with
> **OS first principles**, not buzzwords.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★       | ★      | ★★      | ★★★★★     | ★★★★★   |

**Most-asked interview/backend concepts:** **process vs thread vs event-loop**
server models and their memory/CPU cost; the **C10k problem** and why
thread-per-connection doesn't scale; **blocking vs non-blocking I/O**; **I/O
multiplexing** — **select / poll (O(n)) vs epoll (O(1))**, **edge- vs
level-triggered**; **io_uring** (shared submission/completion rings, fewer
syscalls); **Nginx** (master + event-driven workers) vs **Apache MPMs**
(prefork / worker / event); **load balancing** (**L4 vs L7**, round-robin / least-
connections / IP-hash); **worker/thread/connection pools**; **keep-alive** and
**graceful restarts**.

---

## 20.1 A Backend Server Is Just an OS Program

### First principles: what "handling a request" really is

Strip away the framework and a TCP server is a short sequence of **system calls**
(M2/M13) on **file descriptors** (M11) — a network socket is a file descriptor:

```c
int s = socket(AF_INET, SOCK_STREAM, 0);   // create a socket (an fd)
bind(s, ...); listen(s, backlog);          // claim a port, set accept queue
for (;;) {
    int c = accept(s, ...);                // get next client connection (a new fd)
    read(c, buf, n);                       // read the request  (I/O -> may BLOCK)
    /* ... produce response ... */
    write(c, resp, m);                      // write the response (I/O -> may BLOCK)
    close(c);
}
```

The entire art of a high-performance server is answering **one question**: while
one connection is **blocked on I/O** (waiting for the client's bytes to arrive over
the slow network), **what should the CPU do?** That is the *exact* question **M1**
asked about the fast CPU and slow I/O, and every server model below is a different
answer — just like every OS type was a different answer to "keep the CPU busy."

> **Memory hook:** a server is **multiprogramming for network I/O**. The network is
> the "slow disk"; connections are the "jobs"; the challenge is never letting the
> CPU idle while a socket waits. Servers differ only in **how** they overlap
> waiting connections.

### MCQs

1. A network connection is represented by? → a **file descriptor (socket)**.
2. The core problem a server solves? → what the CPU does while a connection is
   **blocked on I/O** (overlap many slow connections).
3. Which syscall returns a new fd per client? → **`accept()`**.

---

## 20.2 Three Concurrency Models — Process vs Thread vs Event Loop

There are three ways to serve many connections at once. Know **what each spends**
(memory, context switches) and **where each breaks**.

![Processes/threads cost RAM and context switches; an event loop multiplexes thousands of connections on one thread.](images/185_server_models.png)

| Model | Unit per connection | Cost | Breaks when |
|-------|--------------------|------|-------------|
| **Process-per-conn** | a **process** (fork) | heaviest: MBs each, slow context switch, no shared memory | ~hundreds of conns |
| **Thread-per-conn** | a **thread** | lighter: shared address space, but ~1 MB stack each + context switches | **~10k conns (C10k)** |
| **Event loop** | **none** — one thread multiplexes all via `epoll` | tiny per-conn state; but code must be **non-blocking** | CPU-bound work or a blocking call |

- **Process-per-connection** (the oldest model, classic CGI / Apache **prefork**):
  simple and crash-isolated (one connection's bug can't corrupt another — the
  **protection** benefit of separate address spaces from M4), but a process costs
  **megabytes** and its **context switch** is expensive (flush TLB, swap address
  space — M9/M10). Doesn't scale past a few hundred.
- **Thread-per-connection:** threads share one address space (M5), so they're
  **cheaper** than processes, but each still needs a **stack** (~1 MB here for
  illustration; the Linux default is often 8 MB)
  and the scheduler must **context-switch** among thousands of them. This is what
  hits the **C10k** wall (§20.3). It also needs **locks** (M7) around shared state.
- **Event loop (reactor):** **one thread** (or one per core) uses **I/O
  multiplexing** (`epoll`) to watch **all** connections and only touches a
  connection when it's **actually ready**. No per-connection thread, no giant stack,
  no thundering context switches — thousands of connections on a **single thread**.
  The catch: **every operation must be non-blocking**, or the one thread stalls and
  *all* connections freeze.

> **Memory hook (the trap):** the event loop is a **short-order cook** working
> **many orders alone** — start the fries, flip a burger while they cook, plate a
> ready order — never *standing and waiting* on any one. The moment the cook
> **blocks** (waits for one pot to boil doing nothing else), **every** customer
> waits. That is why event-loop code must never make a blocking call.

### MCQs

1. Cheapest per-connection state? → the **event loop** (no thread/process per conn).
2. Why does thread-per-connection cost so much at scale? → each thread's **stack
   (~1 MB)** + **context-switch** overhead.
3. The one rule of event-loop code? → **never block** the single thread.
4. One advantage of process-per-connection? → **crash isolation** (separate address
   spaces).

---

## 20.3 The C10k Problem

**C10k** (Dan Kegel, ~1999) named the challenge of handling **10,000 concurrent
connections** on one server. The point isn't the exact number — it's that the
**thread/process-per-connection** model has costs that grow **linearly with
connections**, so it collapses well before the *hardware's* limit.

**Worked numerical — why thread-per-connection dies at 10k:**

```text
Memory:   10,000 connections x ~1 MB thread stack  = ~10 GB  just for stacks
Scheduler: the OS must time-slice 10,000 threads   -> constant CONTEXT SWITCHES
          each switch ~1-5 us of pure overhead (save/restore, cache/TLB churn, M6/M9)
Result:   the CPU spends more time SWITCHING than WORKING  (thrashing-like collapse)
```

Most of those 10,000 connections are **idle at any instant** (waiting on the
network), yet each still costs a **whole thread**. The insight that broke C10k:
**decouple the number of connections from the number of threads.** Watch all
10,000 fds with **one** call and only do work for the **few** that are ready — i.e.
**I/O multiplexing with `epoll`** (§20.4), which is the foundation of the event-loop
model.

> **Memory hook:** C10k is the **"one waiter per table" problem**. Hiring 10,000
> waiters (threads) for a 10,000-table restaurant is madness when most tables are
> just *thinking*. One sharp waiter who visits **only tables with a raised hand**
> (ready fds via `epoll`) serves them all. C10k → C10M is the same idea pushed
> further.

### MCQs

1. What does the C10k problem describe? → serving **10,000 concurrent connections**
   on one machine.
2. Why does thread-per-connection fail C10k? → **memory (stacks)** + **context-
   switch** overhead grow with connection count.
3. The key idea that solved it? → **decouple connections from threads** via **I/O
   multiplexing (epoll)**.

---

## 20.4 Blocking vs Non-Blocking I/O, and I/O Multiplexing (select / poll / epoll)

### Blocking vs non-blocking

- **Blocking I/O:** `read()` on a socket with no data **puts the thread to sleep**
  until data arrives (the thread moves to the **blocked/waiting** state, M4). One
  thread can wait on **one** fd — hence one-thread-per-connection.
- **Non-blocking I/O:** with `O_NONBLOCK`, `read()` returns **immediately** —
  either data or the error **`EAGAIN`/`EWOULDBLOCK`** ("nothing right now"). Now a
  single thread can *poll* many fds — but naive polling **busy-waits** (burns CPU).
  The right tool is to ask the **kernel** to tell you which fds are ready: **I/O
  multiplexing.**

### select / poll — O(n) per call

`select()` and `poll()` let one thread wait on **many** fds at once. But their cost
**grows with the number of fds watched**:

- You pass the **entire set of fds** to the kernel on **every** call.
- The kernel **scans all N** fds to see which are ready.
- On return, **you scan all N** again to find the ready ones.

So each call is **O(N)** even if only **one** fd is ready. `select()` also caps out
at **`FD_SETSIZE` (typically 1024)** fds. `poll()` removes the 1024 limit (uses an
array instead of a bitmask) but is **still O(N)**. At C10k, doing O(10,000) work
per event, thousands of times a second, is the bottleneck.

### epoll — O(1) ready notification (the Linux fix)

**`epoll`** (Linux) splits the work so the per-call cost depends on the number of
**ready** fds, **not** the number **watched**:

```text
epoll_create()  -> make an epoll instance (a kernel object)
epoll_ctl(ADD)  -> register an fd ONCE (kernel keeps it in an interest set, rbtree)
epoll_wait()    -> returns ONLY the fds that are READY  (kernel maintains a ready list)
```

![select/poll rescan every fd each call (O(n)); epoll registers once and returns only ready fds (O(1)) — the C10k fix.](images/186_select_vs_epoll.png)

Because you **register fds once** and the kernel **pushes ready fds onto a ready
list** (via the same callback that wakes a blocked thread), `epoll_wait` returns in
time **proportional to the number of ready events**, not the number of watched fds.
Watching 10,000 mostly-idle connections costs almost nothing until they have work.

| | `select` | `poll` | `epoll` |
|---|---|---|---|
| fd limit | **1024** (`FD_SETSIZE`) | none | none |
| cost per call | **O(N)** | **O(N)** | **O(ready)** ≈ O(1) |
| fd set passed each call | yes (rebuilt) | yes | **no** (registered once) |
| portability | all POSIX | all POSIX | **Linux only** (BSD: `kqueue`) |

> **Memory hook:** `select`/`poll` = **roll call every round** ("Are you ready?
> You? You?" through all 10,000). `epoll` = a **ticket system**: register once,
> and the kernel only calls the numbers that are **actually ready**.

### Level-triggered vs edge-triggered (the epoll trap)

`epoll` (and `kqueue`) support two notification modes — a favourite gotcha:

- **Level-triggered (LT, default):** `epoll_wait` keeps reporting an fd **as long as
  it is ready** (data remains in the buffer). Forgiving — you may read part of the
  data and get told again next time. Behaves like `select`/`poll`.
- **Edge-triggered (ET):** you're notified **only on the transition** from
  not-ready → ready (the "edge"). You **must drain** the fd (read/write in a loop
  until `EAGAIN`), or you'll **miss** data because you won't be told again. Fewer
  wakeups (higher performance), but **easy to get wrong**.

> **The ET rule:** with edge-triggered, **always use non-blocking fds and loop
> until `EAGAIN`.** Forgetting to drain is the classic "my server hangs under load"
> bug.

### MCQs

1. Non-blocking `read()` with no data returns? → **`EAGAIN`/`EWOULDBLOCK`**.
2. Why is `select` O(N)? → it **passes and scans all N fds every call**; also capped
   at **1024**.
3. Why is `epoll` ≈ O(1)? → fds **registered once**; `epoll_wait` returns **only
   ready** fds from a kernel **ready list**.
4. Edge-triggered requires you to? → **drain the fd (loop until `EAGAIN`)**, using
   **non-blocking** fds.
5. BSD/macOS equivalent of epoll? → **`kqueue`**.

---

## 20.5 io_uring — Asynchronous I/O Done Right

`epoll` has a residual cost: it tells you an fd is **ready**, but you **still make a
separate syscall** (`read`/`write`) to do the actual I/O — and syscalls have
overhead (mode switches, and post-Spectre mitigations made them pricier). It also
never made **disk** I/O truly asynchronous.

**`io_uring`** (Jens Axboe, Linux **5.1**, 2019) changes the contract from *"tell me
when I can do I/O"* to *"here is the I/O I want; wake me when it's done."* It uses
**two shared ring buffers** mapped between user space and the kernel:

```text
Submission Queue (SQ):  app WRITES I/O requests here   (read/write/accept/...)
Completion Queue (CQ):  kernel WRITES results here      (app reads when ready)
Both rings are SHARED memory -> often NO syscall per operation (batch many, one io_uring_enter)
```

- **Fewer syscalls:** batch many operations and submit them with **one** call (or
  even zero, in polled mode) — versus `epoll`'s syscall-per-I/O.
- **Truly async for everything:** network **and** disk/file I/O, unlike `epoll`
  (which never handled regular-file reads asynchronously).
- **Zero-copy friendly** (registered buffers/fds).

This is the **shared-memory IPC** idea (M4) applied to the app↔kernel boundary, plus
a **producer–consumer** ring (M7) — the app produces requests, the kernel produces
completions.

> **Memory hook:** `epoll` is a **doorbell** ("someone's ready — go answer it
> yourself"); `io_uring` is a **drop-box + out-tray**: you leave your requests in
> the in-box and pick up finished results from the out-box, rarely bothering the
> kernel at all.

### MCQs

1. What does io_uring share between user and kernel? → two **ring buffers**
   (**submission** + **completion** queues) in shared memory.
2. io_uring's main win over epoll? → **far fewer syscalls** and **true async** for
   disk *and* network I/O.
3. Which kernel introduced it? → **Linux 5.1**.

---

## 20.6 Nginx vs Apache — Two Architectures, One OS Lesson

The classic comparison makes all the above concrete.

### Nginx — master + event-driven workers

![Nginx: one master + N non-blocking workers (about one per CPU core); each worker's epoll loop serves thousands of connections.](images/187_nginx_architecture.png)

- A **master process** (runs as root) reads config, **binds the ports**, and
  **spawns/manages worker processes** — but does **not** handle requests itself.
- Each **worker** runs a **single-threaded, non-blocking event loop** on `epoll`,
  and there is typically **one worker per CPU core** (so no oversubscription; the
  scheduler rarely context-switches them). Each worker juggles **thousands** of
  connections.
- Result: connection count is **decoupled** from thread count → low memory, few
  context switches, excellent at **many idle/keep-alive connections** and **static
  content / reverse proxying**. This is the **event-loop model** (§20.2) in
  production.

### Apache — MPMs (Multi-Processing Modules)

Apache is configurable via **MPMs** that pick the concurrency model:

| MPM | Model | Notes |
|-----|-------|-------|
| **prefork** | **process-per-connection** (pool of pre-forked processes, no threads) | most compatible (safe for non-thread-safe modules like old `mod_php`); **heaviest** memory |
| **worker** | **hybrid**: several processes, each with many **threads** (thread-per-connection) | lighter than prefork; needs thread-safe modules |
| **event** | like `worker` but a **dedicated thread** manages **keep-alive** connections via a poll loop | frees worker threads from idle keep-alives — Apache's answer to C10k |

> **The interview answer — "Why is Nginx faster than Apache under high
> concurrency?"** → Traditional Apache (prefork/worker) ties **one process/thread
> per connection**, so **10k mostly-idle keep-alive connections** cost 10k
> threads' worth of **memory + context switches (C10k)**. Nginx uses a **fixed,
> small pool of event-loop workers on `epoll`**, so idle connections are nearly
> free. (Apache's **event MPM** narrows the gap by handling keep-alives in a poll
> loop, but the fundamental model still differs.) It's **thread-per-connection vs
> event loop** — the §20.2 tradeoff.

### MCQs

1. What does the Nginx master process do (and not do)? → binds ports & manages
   workers; **does not** serve requests.
2. How many Nginx workers, typically? → about **one per CPU core**, each an
   **`epoll` event loop**.
3. Apache **prefork** vs **worker** vs **event** MPM? → **process-per-conn** vs
   **process+threads** vs **worker + dedicated keep-alive poll thread**.
4. Why can Apache prefork exhaust memory under load? → **one process per
   connection** (MBs each).

---

## 20.7 Load Balancing — Spreading Connections Across Servers

One server isn't enough, so a **load balancer (LB)** fans connections across a pool
of backends. LBs come in two layers (named after the OSI model) and use several
**algorithms**.

![L4 balances by IP/port (fast, opaque); L7 reads HTTP to route by URL/header (smart, heavier).](images/188_l4_vs_l7_lb.png)

### L4 vs L7

| | **L4 (transport)** | **L7 (application)** |
|---|---|---|
| Operates on | **TCP/UDP**: IP + port | **HTTP(S)**: URL, headers, cookies |
| Can it read the payload? | **No** (opaque passthrough) | **Yes** (parses HTTP) |
| Routing power | by connection (fast) | **content-based** (`/api`→A, `/img`→B), sticky sessions |
| Cost | **lower latency**, cheap | more CPU (parses/TLS-terminates), smarter |
| Examples | LVS/IPVS, AWS **NLB** | Nginx, HAProxy, AWS **ALB** |

- **L4** just forwards packets/connections by **IP:port** — fast and protocol-
  agnostic, but "dumb" (can't route by URL).
- **L7** understands **HTTP**, so it can do **path/host-based routing**, **TLS
  termination**, **sticky sessions** (route a user to the same backend via a
  cookie), and health-aware routing — at higher CPU cost.

### Balancing algorithms (know these one-liners)

| Algorithm | How it picks a backend | Good when |
|-----------|------------------------|-----------|
| **Round robin** | next server in rotation | backends roughly equal |
| **Weighted round robin** | rotation biased by capacity | mixed-size servers |
| **Least connections** | server with **fewest active** conns | long-lived/uneven requests |
| **IP hash** | `hash(client IP)` → server | **session stickiness** without cookies |
| **Least response time** | fastest-responding server | latency-sensitive |

> **Memory hook:** these are the **CPU-scheduling policies (M6)** wearing a network
> hat. **Round robin** is literally RR; **least connections** is "shortest queue
> next" (like SJF's spirit); **IP hash** is affinity/**processor affinity**. Load
> balancing = **scheduling connections onto servers**.

### MCQs

1. L4 vs L7 LB — what can each see? → **IP+port only** vs **full HTTP (URL/
   headers/cookies)**.
2. Which algorithm gives session stickiness without cookies? → **IP hash**.
3. Best algorithm for uneven, long-lived connections? → **least connections**.
4. Where does TLS termination usually happen? → the **L7** load balancer.

---

## 20.8 Pools, Keep-Alive, and Graceful Restarts

- **Worker / thread / connection pools:** creating a thread or a DB connection
  per request is expensive, so servers **pre-create a fixed pool** and **reuse**
  them. This is **resource pooling** — bounding concurrency to protect the machine
  (an admission-control/scheduling decision, M6). A too-small pool queues requests;
  a too-large one thrashes (context switches, M6/M9). The **database connection
  pool** is the most important one in practice (DB connections are heavy).
- **HTTP keep-alive:** reuse **one TCP connection** for many requests instead of
  paying the **3-way handshake** (and TLS handshake) each time. Great for latency,
  but keep-alive connections **sit idle holding a slot** — which is *exactly* why
  the **event-loop model** (cheap idle connections) beats thread-per-connection for
  keep-alive-heavy traffic (§20.6).
- **Graceful restart / zero-downtime deploy:** to update config or binary without
  dropping connections, the server **starts new workers**, lets **old workers
  finish their in-flight requests** ("drain"), then exits them. Nginx does this by
  having the **master fork new workers** and signal old ones to stop accepting new
  connections while finishing current ones — an orderly **process lifecycle** (M4)
  operation. (Contrast a **hard restart**, which drops live connections.)

> **Memory hook:** a pool is a **fixed fleet of taxis** — reused, not bought
> per-trip; keep-alive is **keeping the meter running** for a returning passenger;
> graceful restart is **swapping drivers at a red light**, not mid-highway.

### MCQs

1. Why use a thread/connection **pool**? → avoid **per-request creation cost** and
   **bound concurrency**.
2. What does HTTP keep-alive save? → the repeated **TCP (and TLS) handshake**.
3. Graceful restart avoids? → **dropping in-flight connections** (old workers
   **drain** first).

---

## 20.9 Real-World & Backend Perspectives

- **Node.js / Redis / Nginx** are all **single-threaded event loops** on `epoll` —
  which is why "**don't block the event loop**" is the #1 Node rule (a CPU-heavy
  handler freezes *all* connections, §20.2).
- **Go** hides the model: goroutines look like thread-per-connection, but the Go
  runtime multiplexes millions of them onto a few OS threads using an internal
  **`epoll`/`netpoller`** — you write blocking-style code, the runtime does the
  event loop. Same for async/await runtimes (Rust `tokio`, Python `asyncio`).
- **Thundering herd:** if many workers `accept()` on the same socket, one event can
  wake them **all** to fight over one connection. Fixes: `SO_REUSEPORT` (each worker
  its own accept queue), or `EPOLLEXCLUSIVE`. This is a **synchronization/wakeup**
  problem (M7).
- **Backpressure:** when downstreams are slow, a good server **limits accepts /
  queues** rather than accepting infinitely and running out of memory — admission
  control, again scheduling (M6).
- **Observability:** `ss`/`netstat` (socket states), `strace` (the syscalls from
  §20.1), and load-testing tools (`wrk`, `ab`) reveal whether you're bound by
  **CPU, I/O, or context switches** — the OS triad.

---

## 20.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** blocking inside an event loop (a slow DB call, `JSON.parse` of a huge
  body, `fs` sync call) — **all** connections stall. Offload CPU work to a
  **worker/thread pool**.
- **Mistake:** using edge-triggered `epoll` without **draining to `EAGAIN`** on
  non-blocking fds → lost events, hung connections.
- **Mistake:** "more threads = faster." Past ~cores, extra threads add **context-
  switch overhead** (M6) and **lock contention** (M7), *reducing* throughput.
- **Mistake:** unbounded connection/thread pools → memory exhaustion under a load
  spike (no backpressure).
- **Edge case:** keep-alive connections **hold slots** while idle — fine for event
  loops, deadly for thread-per-connection.
- **Edge case:** `select`'s **1024** fd cap silently breaks at scale — use `epoll`.
- **Tradeoff:** **L7** LB (smart routing, TLS, content) vs **L4** LB (lower latency,
  cheaper). Pick by whether you need to *read* the request.
- **Tradeoff:** event loop = max throughput but **hard to program** (callback/async);
  thread-per-connection = simple blocking code but **limited scale**. (Go/async
  runtimes try to give you both.)

---

## 20.11 Exam, Interview & Coding Perspectives

- **Interview (very common):**
  - *"select vs poll vs epoll?"* → O(N) + 1024 cap / O(N) no cap / **O(ready),
    register once** (§20.4). Mention **edge vs level triggered**.
  - *"Why is Nginx faster than Apache?"* → **event loop vs thread-per-connection**;
    idle keep-alives are cheap on Nginx (§20.6).
  - *"What is the C10k problem?"* → thread/process-per-conn costs scale with
    connections; solved by **epoll + event loop** (§20.3).
  - *"L4 vs L7 load balancer?"* → transport (IP:port) vs application (HTTP-aware)
    (§20.7).
  - *"Why not block the event loop?"* → one thread serves all; blocking freezes
    everyone (§20.2).
- **Coding/practical:** know the `socket → bind → listen → accept → read/write →
  close` skeleton (§20.1); set `O_NONBLOCK`; handle `EAGAIN`; size **thread/DB
  pools** to cores/DB limits; enable **keep-alive** and **`SO_REUSEPORT`**.
- **GATE/SEBI/RBI:** not core syllabus, but this module is where **scheduling (M6)**,
  **I/O (M13)**, **processes/threads (M4/M5)**, and **synchronization (M7)** all
  cash out — great for cementing those concepts.

---

## 20.12 Concept Checks & MCQs (test yourself)

1. A socket is a? → **file descriptor**.
2. Server skeleton syscalls? → `socket → bind → listen → accept → read/write →
   close`.
3. Three concurrency models? → **process-per-conn / thread-per-conn / event loop**.
4. Cheapest per-connection cost? → **event loop** (no per-conn thread).
5. C10k problem? → serving **10,000 concurrent connections**; thread-per-conn scales
   poorly (memory + context switches).
6. ~Memory for 10k threads' stacks (1 MB each)? → **~10 GB**.
7. Blocking vs non-blocking `read` with no data? → **sleeps** vs returns **`EAGAIN`**.
8. select fd limit? → **1024** (`FD_SETSIZE`).
9. Why is select/poll O(N)? → **pass & scan all N fds each call**.
10. Why is epoll ~O(1)? → **register once**, kernel returns only **ready** fds.
11. Level- vs edge-triggered? → notified **while ready** vs **only on the ready
    transition** (ET must **drain to `EAGAIN`**).
12. epoll's BSD counterpart? → **`kqueue`**.
13. io_uring's two rings? → **submission** + **completion** queues (shared memory).
14. io_uring vs epoll main win? → **fewer syscalls** + **true async disk+net I/O**.
15. Nginx architecture? → **master** + **event-loop workers** (~1/core) on `epoll`.
16. Apache prefork model? → **process-per-connection**.
17. Apache event MPM adds? → a **dedicated thread for keep-alive** connections.
18. L4 vs L7 LB? → **IP:port (opaque)** vs **HTTP-aware (URL/header/cookie)**.
19. Sticky sessions without cookies? → **IP hash**.
20. Algorithm for uneven long connections? → **least connections**.
21. What does keep-alive save? → repeated **TCP/TLS handshake**.
22. Purpose of a thread/connection pool? → **reuse** + **bound concurrency**.
23. Graceful restart does? → new workers start; old workers **drain** in-flight
    requests before exiting.
24. Why "don't block the event loop"? → one thread serves all conns; blocking
    **freezes everyone**.
25. How does Go scale connections? → millions of **goroutines** multiplexed onto few
    OS threads via an internal **netpoller (epoll)**.

**True/False**
- poll removes select's 1024 fd limit but is still O(N). → **True**.
- epoll cost grows with the number of **watched** fds. → **False** (grows with
  **ready** fds).
- Edge-triggered epoll works fine with blocking fds and a single read. → **False**
  (need non-blocking + drain to `EAGAIN`).
- Nginx serves requests from its master process. → **False** (workers do).
- An L4 load balancer can route by URL path. → **False** (that's L7).
- More threads always increase throughput. → **False** (context switches + lock
  contention).

---

## 20.13 One-Page Revision Sheet

```
SERVER = OS PROGRAM: socket->bind->listen->accept->read/write->close. socket = an fd.
  Core question: what does CPU do while a conn is BLOCKED on network I/O? (multiprogramming, M1)

CONCURRENCY MODELS:
  process-per-conn : MBs each, slow ctx switch, crash-isolated  -> ~hundreds
  thread-per-conn  : ~1MB stack each + ctx switches + locks     -> dies at C10k
  EVENT LOOP       : 1 thread + epoll, tiny per-conn state       -> 1000s (must NOT block)

C10k: 10k conns; thread-per-conn = 10k x 1MB (~10GB) + constant ctx switches -> collapse.
  FIX = decouple #conns from #threads = I/O MULTIPLEXING (epoll) + event loop.

BLOCKING vs NON-BLOCKING: blocking read sleeps ; non-blocking (O_NONBLOCK) returns EAGAIN.

I/O MULTIPLEXING:
  select : O(N), pass+scan all N each call, FD_SETSIZE=1024 cap
  poll   : O(N), no 1024 cap (array)
  EPOLL  : register ONCE (epoll_ctl), epoll_wait returns ONLY READY fds -> ~O(ready)=O(1). Linux.
           (BSD/mac = kqueue). LEVEL-triggered (default, notified while ready) vs
           EDGE-triggered (only on transition -> MUST drain to EAGAIN, non-blocking fds).
  io_uring (Linux 5.1): shared SUBMISSION+COMPLETION rings -> few/no syscalls, TRUE async disk+net.

NGINX: master(binds ports, mgr) + WORKERS(~1/core, single-thread epoll event loop). idle conns cheap.
APACHE MPMs: prefork(process/conn, heavy) | worker(procs x threads) | event(worker + keep-alive poll thread).
  "Nginx > Apache under load" = event loop vs thread-per-conn (C10k).

LOAD BALANCING:
  L4 = TCP/UDP IP:port, opaque, fast  |  L7 = HTTP-aware (URL/header/cookie), TLS-term, smart, costlier.
  Algos: round-robin, weighted-RR, LEAST-CONNECTIONS, IP-HASH(stickiness), least-response-time.
  (= CPU scheduling M6 for connections)

POOLS: pre-create+reuse threads/DB-conns, BOUND concurrency (too small=queue, too big=thrash).
KEEP-ALIVE: reuse 1 TCP conn (skip handshake) -> idle conns favor event loop.
GRACEFUL RESTART: start new workers, old workers DRAIN in-flight, then exit (zero downtime).
```

### Flash cards

| Front | Back |
|-------|------|
| A socket is? | A file descriptor |
| Three server models? | Process- / thread-per-conn / event loop |
| C10k solved by? | epoll + event loop (decouple conns from threads) |
| select fd cap? | 1024 (FD_SETSIZE), O(N) |
| Why epoll ~O(1)? | Register once; returns only ready fds |
| ET epoll requires? | Non-blocking fds + drain to EAGAIN |
| io_uring rings? | Submission + completion (shared memory) |
| Nginx model? | Master + epoll event-loop workers (~1/core) |
| Apache prefork? | Process-per-connection |
| L4 vs L7? | IP:port (opaque) vs HTTP-aware |
| Sticky sessions w/o cookie? | IP hash |
| Don't ___ the event loop | Block |

### Spaced repetition
- **24-hour:** recite the three concurrency models + costs, and select/poll/epoll
  complexities (O(N)/O(N)/O(1), 1024 cap).
- **7-day:** explain the C10k memory numerical; edge vs level triggered; why Nginx
  beats Apache under high concurrency; L4 vs L7.
- **30-day:** given a server-scaling scenario, choose the model, multiplexing API,
  and LB (layer + algorithm) and justify each in OS terms (M4/M5/M6/M7/M13).

---

## 20.14 Summary

A backend server is an **OS program** whose whole job is deciding what the CPU does
while connections **block on network I/O** — the **multiprogramming** question from
**M1**, applied to sockets (**file descriptors**, M11). Serving one connection per
**process** is crash-isolated but heavy; one per **thread** is lighter but hits the
**C10k** wall (memory + **context switches**, M6/M9); the **event loop** decouples
connections from threads by using **I/O multiplexing**. `select`/`poll` are
**O(N)** (and `select` caps at 1024), while **`epoll`** registers fds once and
returns only the **ready** ones (**~O(1)** — the C10k fix), with **level- vs
edge-triggered** modes to master; **`io_uring`** goes further with shared
**submission/completion rings** for near-syscall-free, truly async I/O. **Nginx**
(master + `epoll` event-loop workers) beats classic **Apache** (prefork/worker
**thread-per-connection**) under high, keep-alive-heavy concurrency — the same §20.2
tradeoff. Above the server, **load balancers** spread connections at **L4 (IP:port)**
or **L7 (HTTP-aware)** using algorithms that are **CPU scheduling (M6) for
connections**; and **pools, keep-alive, and graceful restarts** are resource
management and **process lifecycle** (M4) in production. Every one of these is a
concept from earlier modules, cashed out where performance is money.

This completes the perspective pair with **Module 19 — the AI-Engineering
Perspective**: GPUs and LLM serving on one side, high-concurrency servers on the
other, both showing that **the operating system is the substrate of all modern
systems engineering**.

> **You have mastered this module when** you can: write the `socket→…→close`
> skeleton and say where it blocks; contrast the three concurrency models with
> their costs; explain the **C10k** problem and its fix; compare **select/poll/
> epoll** (complexity, fd cap, edge vs level) and place **io_uring**; explain why
> **Nginx** beats **Apache** under load; and choose an **L4/L7** load balancer and
> algorithm — all grounded in scheduling (M6), I/O (M13), and processes/threads
> (M4/M5), without notes.
