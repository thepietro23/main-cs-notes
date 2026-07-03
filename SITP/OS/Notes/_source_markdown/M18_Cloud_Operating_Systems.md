---
title: "Module 18 — Cloud Operating Systems"
subtitle: "OS Mastery: SEBI IT / RBI / NABARD / GATE / C-DAC / Interview / Backend — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 18 — Cloud Operating Systems

> **Where this module sits.**
> Module 17 gave us the two building blocks — **virtual machines** and
> **containers**. This module scales them up to the **data centre**. The big idea:
> the same jobs a normal OS does for *one computer* — allocate CPU/RAM, schedule
> work, isolate users, meter usage — the **cloud** does for a **fleet of thousands
> of computers**. That is why we can call the cloud platform an **"operating system
> for the data centre."** We cover the service models **IaaS / PaaS / SaaS**, cloud
> **compute** (EC2 / Azure VMs / GCP), **serverless / FaaS**, cloud **scheduling**
> (bin-packing), **autoscaling**, and **multi-tenancy**. This is the highest-yield
> module for **backend and AI-infra interviews** and appears in **SEBI/RBI** cloud
> MCQs.

**Importance ratings (out of 5):**

| Exam / Use     | SEBI IT | RBI IT | GATE CS | Interview | Backend |
|----------------|:-------:|:------:|:-------:|:---------:|:-------:|
| This module    | ★★★★★   | ★★★★   | ★       | ★★★★★     | ★★★★★   |

**Most-asked PYQ concepts (SEBI / RBI / NABARD):** the **NIST definition** and its
**5 essential characteristics**; the **three service models IaaS / PaaS / SaaS**
(with examples and *who manages what*); **deployment models** (public / private /
hybrid / community); the **shared-responsibility** model; **serverless / FaaS**
(pay-per-use, auto-scale, no server to manage); **horizontal vs vertical scaling**
(elasticity); **multi-tenancy**; that a **cloud VM = a guest OS on a Type-1
hypervisor**.

---

## 18.1 The "Operating System for the Data Centre" (first principles)

### The problem

A single OS turns **one computer** into a friendly, shared, isolated service for
many processes. But a modern application runs on **thousands of machines** in a data
centre. Who decides **which machine** runs your web server? Who **restarts** it when
a machine dies? Who **isolates** your workload from another customer's? Who
**meters** and **bills** your usage? Managing this by hand is impossible.

### The idea

**Cloud computing** delivers computing resources (compute, storage, networking) as
an **on-demand, pay-as-you-go service over the internet**, backed by software that
manages the whole fleet. That fleet-management software plays the role of an OS —
one level up:

| A normal OS (one machine) | The cloud (whole data centre) |
|---|---|
| schedules **threads** onto **cores** | schedules **containers/VMs** onto **machines** |
| allocates **RAM/CPU** to processes | allocates **instances/quotas** to tenants |
| **isolates** processes (user/kernel mode) | **isolates** tenants (VMs, namespaces) |
| **meters** CPU time | **meters** usage and **bills** it |
| provides **abstraction** (files, sockets) | provides **abstraction** (APIs: "give me a server") |

> **Memory hook:** **the cloud is an OS whose "processes" are whole virtual machines
> and containers, and whose "computer" is the entire data centre.** Google's own
> phrase is *"The Datacenter as a Computer."*

### NIST's five essential characteristics (memorise for SEBI/RBI)

The US **NIST** definition is the exam-standard checklist for "is it really cloud?":

1. **On-demand self-service** — provision resources yourself, instantly, no human.
2. **Broad network access** — reachable over the network from any device.
3. **Resource pooling** — a shared pool serves many customers (**multi-tenancy**),
   assigned dynamically.
4. **Rapid elasticity** — scale out/in quickly, seemingly unlimited.
5. **Measured service** — usage is **metered** and you **pay for what you use**.

> **Memory hook (NIST 5):** *"**O**n-demand, **B**road access, **R**esource
> pooling, **E**lasticity, **M**easured"* → **"OB-REM."**

### MCQs

1. Who published the standard cloud definition + 5 characteristics? → **NIST**.
2. "Pay only for what you use" is which characteristic? → **measured service**.
3. Many customers sharing one pool of hardware is called? → **resource pooling /
   multi-tenancy**.

---

## 18.2 Cloud Service Models — IaaS / PaaS / SaaS

The three models differ by **how much the provider manages vs how much you manage**.
As you go IaaS → PaaS → SaaS, the provider takes over **more of the stack**.

![As you move IaaS to PaaS to SaaS, the provider manages more of the stack (hardware, virtualization, OS, runtime) and you manage less; on-prem you manage everything.](images/167_iaas_paas_saas.png)

| Model | You manage | Provider manages | Analogy | Examples |
|-------|-----------|------------------|---------|----------|
| **On-prem** | **everything** | nothing | own the car | your own servers |
| **IaaS** (Infrastructure) | OS, runtime, app, data | HW, virtualization | **rent the car** | **AWS EC2, Azure VMs, GCP Compute Engine** |
| **PaaS** (Platform) | app + data only | HW…**up to the runtime** | **taxi** (you say where) | **Google App Engine, Heroku, Azure App Service, Elastic Beanstalk** |
| **SaaS** (Software) | just **use it** (settings/data) | **the whole stack** | **bus** (fixed route) | **Gmail, Salesforce, Office 365, Dropbox** |

> **Memory hook — pizza-as-a-service:** **On-prem** = cook at home (you buy
> everything). **IaaS** = take-and-bake (they give oven+ingredients, you cook).
> **PaaS** = pizza delivery (you just supply the table/drinks = your app+data).
> **SaaS** = eat at the restaurant (you just show up).

> **The exam trap — match example to model:** **EC2 = IaaS**, **App Engine/Heroku =
> PaaS**, **Gmail = SaaS**. A very common MCQ gives you a product and asks the model.

> **Shared-responsibility model (RBI/SEBI + real life):** security is **split**. The
> provider secures the cloud **infrastructure** ("security *of* the cloud"); the
> customer secures their **data, access, and configuration** ("security *in* the
> cloud"). The higher you go (IaaS→SaaS), the more the provider handles — but
> **data governance is always yours** (why RBI/SEBI insist on data localisation,
> auditability, and exit clauses).

### MCQs

1. EC2 is which model? → **IaaS**. App Engine? → **PaaS**. Gmail? → **SaaS**.
2. In which model do you manage the **OS**? → **IaaS** (not PaaS/SaaS).
3. Who secures customer **data** in the shared-responsibility model? → the
   **customer** (always).

---

## 18.3 Deployment Models (a quick MCQ section)

Cloud is also classified by **who owns and can use** the infrastructure:

- **Public cloud** — owned by a provider, shared by the general public over the
  internet (AWS, Azure, GCP). Cheapest, most elastic.
- **Private cloud** — dedicated to **one organisation** (on-prem or hosted). More
  control and compliance; costlier. (Banks/regulators often prefer this.)
- **Hybrid cloud** — **combines public + private**, with data/apps moving between
  them (e.g. sensitive data private, burst traffic to public).
- **Community cloud** — shared by **several organisations with common concerns**
  (e.g. a group of banks or government bodies).

> **Memory hook:** **public = shared apartment; private = own house; hybrid = house
> + rented storage unit; community = housing co-op.**

### MCQs

1. Cloud dedicated to a single organisation? → **private cloud**.
2. Mix of public and private? → **hybrid cloud**.

---

## 18.4 Cloud Compute — EC2 / Azure VMs / GCP (a VM on a hypervisor)

The core IaaS product is the **cloud virtual machine** — you rent a running
**guest OS** by the second.

- **AWS EC2** ("Elastic Compute Cloud") — instances (t3, m6i, c7g…) sized by
  **vCPU + RAM**. Modern EC2 runs on the **AWS Nitro** hypervisor (a **KVM-based
  Type-1** hypervisor with hardware offload; older EC2 used **Xen**).
- **Azure Virtual Machines** — VMs on Microsoft's **Hyper-V** (Type-1) hypervisor.
- **GCP Compute Engine** — VMs on Google's **KVM**-based (Type-1) hypervisor.

> **The one line that ties M17 to M18:** **a cloud VM is literally a guest OS running
> on a Type-1 (bare-metal) hypervisor** in the provider's data centre. When you
> "launch an EC2 instance," the provider's scheduler picks a physical host, the
> hypervisor carves out virtual CPU/RAM/disk/NIC, and your chosen OS image boots
> inside it. Everything from **Module 17 §17.2–17.4** is happening under the hood.

**What you get and manage on a cloud VM:**

- **You** choose the OS image (AMI/VM image), install software, patch the OS, and
  scale the count — **it's IaaS** (§18.2).
- **The provider** gives elasticity (start/stop in seconds), pay-per-second billing,
  snapshots, and live-migration behind the scenes.

> **Instance families = matching hardware to workload:** general-purpose (balanced),
> compute-optimised (CPU-heavy), memory-optimised (in-memory DBs), and
> **GPU/accelerated** (ML training/inference — the entry point to **M19 AI infra**).

### MCQs

1. EC2 stands for? → **Elastic Compute Cloud**.
2. A cloud VM runs on what? → a **Type-1 (bare-metal) hypervisor**.
3. Azure VMs use which hypervisor? → **Hyper-V**. GCP? → **KVM**.
4. Who patches the OS on an IaaS VM? → **you** (the customer).

---

## 18.5 Serverless / Functions-as-a-Service (FaaS)

**Serverless** flips the model: you upload **just a function**, and the platform
runs it **only when an event fires**, **auto-scales** it, and **bills per
invocation** (down to the millisecond). There are still servers — **you** just never
see or manage them.

- **Examples:** **AWS Lambda**, **Azure Functions**, **Google Cloud Functions /
  Cloud Run**.
- **Event-driven:** a function runs in response to an HTTP request, a file upload, a
  queue message, a timer, etc.
- **Scale to zero:** if no events arrive, **nothing runs and you pay nothing**; a
  burst of events spins up **many parallel instances** automatically.
- **Stateless & ephemeral:** each invocation may run in a **fresh sandbox**; keep no
  local state (use a database/object store).

### The OS view — sandboxes and cold starts

![On the first invocation the platform must start a sandbox (a Firecracker microVM/container), load the runtime and your code, and initialise — this is the cold start; warm invocations reuse the running sandbox.](images/168_serverless_cold_start.png)

Under the hood the provider runs your function inside a tiny, fast-booting sandbox —
AWS Lambda uses **Firecracker microVMs** (a §17.9 microVM: VM-grade isolation at
container speed). The lifecycle:

- **Cold start** — the **first** call (or after idle/scale-out) must **create the
  sandbox, load the language runtime, load your code, and run init**. This adds
  **latency (tens of ms to a few seconds)**.
- **Warm start** — the platform **keeps the sandbox alive** for a while, so the next
  call **reuses it** and skips straight to your handler → **fast**.

> **Memory hook:** **cold start = starting a cold car engine** (choke, warm up);
> **warm start = the engine's already running, just drive.** Reducing cold starts
> (smaller packages, provisioned concurrency, lightweight runtimes) is a core
> serverless-tuning skill.

> **From the OS perspective:** serverless is the ultimate abstraction — the cloud
> hides the machine, the OS, *and* the process. You hand over a **function**; the
> platform handles **placement, isolation, scaling, and metering** — exactly the OS
> jobs of §18.1, now completely invisible.

### MCQs

1. What do you deploy in FaaS? → **a function** (no server to manage).
2. Serverless billing model? → **pay per invocation / execution time** (scale to
   zero).
3. What is a **cold start**? → latency to **create + initialise the sandbox** on the
   first/scaled-out call.
4. What isolates an AWS Lambda invocation? → a **Firecracker microVM** (a microVM).

---

## 18.6 Resource Scheduling in the Cloud — Bin-Packing

With thousands of machines and millions of workloads, the platform must decide
**which workload runs on which machine**. This is the cloud's version of **CPU
scheduling (M6)** — but the "jobs" are containers/VMs with **CPU + memory requests**
and the "CPUs" are whole **nodes**.

![The cluster scheduler bin-packs pending pods onto nodes according to their CPU and memory requests, filling machines efficiently so the datacentre behaves like one big computer.](images/170_bin_packing.png)

- **Bin-packing:** treat each node as a **bin** with a fixed CPU/RAM capacity, and
  each workload as an **item** of a given size. The scheduler **packs items into as
  few bins as possible** to maximise utilisation (fewer idle machines = lower cost).
  (Bin-packing is a classic **NP-hard** problem, so schedulers use fast heuristics
  like best-fit / most-requested.)
- **Constraints beyond size:** affinity/anti-affinity ("keep replicas on *different*
  nodes for fault tolerance"), taints/tolerations, GPU or zone requirements,
  headroom for spikes.
- **Cluster-as-a-computer:** systems like Google **Borg**, **Kubernetes** (§17.8),
  and Apache **Mesos** present the whole fleet as **one giant computer** — you submit
  work with a resource request and the scheduler finds a home for it.

> **Memory hook:** **the cloud scheduler is Tetris for servers** — fit the workload
> blocks tightly so few machines sit half-empty. Pack too tightly, though, and a
> traffic spike has nowhere to go (leave **headroom**).

> **The scheduling tension (interview):** **utilisation vs reliability/latency.**
> Packing tightly saves money but risks **resource contention** and no room for
> spikes; leaving slack wastes money but improves resilience. Real schedulers tune
> this balance with requests/limits and reserved headroom.

### MCQs

1. Placing workloads onto machines to maximise utilisation is called? →
   **bin-packing**.
2. Google's internal cluster manager (K8s' ancestor)? → **Borg**.
3. The trade-off in tight bin-packing? → **utilisation vs contention/headroom**.

---

## 18.7 Autoscaling — Elasticity in Practice

**Elasticity** (the NIST characteristic) is realised by **autoscaling**: adding or
removing capacity automatically as load changes. There are two directions.

![Vertical scaling makes one machine bigger (scale up, has a ceiling and needs a reboot); horizontal scaling adds more identical machines behind a load balancer (scale out, the cloud default).](images/169_autoscaling.png)

- **Vertical scaling (scale up/down)** — give the **same instance more resources**
  (more vCPU/RAM). Simple, but has a **hardware ceiling** and usually needs a
  **restart** (downtime). Good for databases that are hard to distribute.
- **Horizontal scaling (scale out/in)** — add/remove **more identical instances**
  behind a **load balancer**. **Near-unlimited**, no downtime, resilient — the
  **cloud default** for stateless web/app tiers.

| | Vertical (scale up) | Horizontal (scale out) |
|---|---|---|
| Change | bigger machine | more machines |
| Limit | hardware ceiling | ~unlimited |
| Downtime | usually (reboot) | none |
| Resilience | single point of failure | high (many replicas) |
| Best for | stateful DBs | stateless services |

> **Memory hook:** **vertical = a bigger truck; horizontal = more trucks.** One truck
> can only get so big; you can always add more trucks.

**What triggers scaling — the metrics:**

- **CPU utilisation** (the classic: "scale out above 70% CPU"), **memory**, **request
  rate / concurrency**, **queue length**, **response latency**, or **custom
  business metrics**.
- **Target tracking:** keep a metric near a target (e.g. keep CPU ≈ 60%) — the
  autoscaler adds/removes instances to hold it.

> **The Kubernetes trio (interview):** **HPA** (Horizontal Pod Autoscaler — more
> pods), **VPA** (Vertical Pod Autoscaler — bigger pods), and the **Cluster
> Autoscaler** (more *nodes* when pods can't be placed). AWS's equivalent is an
> **Auto Scaling Group** with a target-tracking policy.

> **Edge cases:** scaling isn't instant (new instances take time to boot/warm — the
> §18.5 cold-start problem again), and bad policies cause **thrashing** (flapping up
> and down). Cooldowns and predictive scaling smooth this.

### MCQs

1. Horizontal vs vertical scaling? → **more machines** vs a **bigger machine**.
2. Cloud default for stateless web tiers? → **horizontal** (behind a load balancer).
3. Common autoscaling metric? → **CPU utilisation** (also memory, request rate,
   queue length).
4. Kubernetes component that adds **nodes**? → the **Cluster Autoscaler** (HPA adds
   pods).

---

## 18.8 Multi-Tenancy & Isolation

**Multi-tenancy** = **many customers (tenants) share the same physical
infrastructure** — the engine of cloud economics (resource pooling). The hard part
is keeping tenants **isolated** so they cannot see, affect, or attack each other.

**Isolation layers (strongest → lightest):**

| Boundary | Isolation | Used for |
|----------|-----------|----------|
| **Separate hardware** | strongest | dedicated/regulated tenants |
| **VM (hypervisor)** | strong (hardware-enforced) | standard IaaS tenant separation |
| **microVM** (Firecracker) | strong + fast | serverless / function tenants |
| **Container (namespaces + cgroups)** | lighter (shared kernel) | tasks within one tenant |
| **Process** | weakest | same-app workers |

- **The "noisy neighbour" problem:** one tenant's heavy CPU/IO/network use degrades
  another's performance. **Solution:** **cgroups**-style resource **limits/quotas**
  (M17 §17.6) and careful **bin-packing** (§18.6) with headroom.
- **Security isolation:** because containers share a kernel, untrusted multi-tenant
  workloads use **VMs or microVMs** for a hardware boundary (why Lambda uses
  Firecracker).

> **Memory hook:** **multi-tenancy = an apartment building.** Everyone shares the
> foundation and plumbing (hardware), but strong **walls** (VMs/namespaces) stop
> neighbours seeing each other, and **metered utilities** (cgroups/quotas) stop one
> flat draining all the water.

### MCQs

1. Many customers sharing one infrastructure? → **multi-tenancy**.
2. One tenant hogging shared resources? → the **noisy-neighbour** problem (fix with
   **cgroups/quotas**).
3. Strongest common isolation for untrusted tenants? → **VM / microVM** (hardware
   boundary).

---

## 18.9 Real-World & Backend Perspectives

- **The whole stack, top to bottom:** your app runs in a **container** (M17), packed
  by a **scheduler** (§18.6) onto a **VM** (§18.4) that is a **guest OS on a Type-1
  hypervisor** — and the platform **autoscales** (§18.7), **meters**, and **isolates**
  (§18.8) it. Every OS concept in this course reappears at data-centre scale.
- **Backend deployment reality:** most teams ship containers to **Kubernetes**
  (EKS/GKE/AKS) or a PaaS (Cloud Run, App Engine); latency-insensitive glue and
  event handlers go to **serverless (Lambda)**.
- **Cost engineering** is scheduling: right-sizing instances, bin-packing density,
  autoscaling policies, and **spot/preemptible** instances directly shape the bill.
- **AI infra (M19):** training and inference run as **GPU containers** scheduled onto
  **GPU instances**; the same bin-packing/autoscaling ideas apply, plus GPU-aware
  scheduling and model-serving cold starts.
- **Regulated finance (SEBI/RBI context):** banks use **private/hybrid** clouds,
  demand **data localisation**, **auditability**, and **exit/portability**, and lean
  on the **shared-responsibility** model — the exam angle for these agencies.

---

## 18.10 Tradeoffs, Common Mistakes, Edge Cases

- **Mistake:** thinking "serverless = no servers." There **are** servers — **you**
  just don't manage them (the provider does).
- **Mistake:** mixing up service models. **EC2 = IaaS**, **App Engine/Heroku =
  PaaS**, **Gmail = SaaS.** Memorise one example each.
- **Mistake:** believing the provider secures **your data**. **Shared
  responsibility** — the provider secures the infra; **you** secure data, access, and
  config.
- **Mistake:** "vertical scaling is unlimited." It hits a **hardware ceiling** and
  usually needs a **reboot**; **horizontal** is the near-unlimited path.
- **Edge case:** **cold starts** add latency to serverless (and to any freshly
  scaled-out instance) — mitigate with provisioned/pre-warmed capacity.
- **Edge case:** aggressive **bin-packing** raises utilisation but risks **noisy
  neighbours** and no headroom for spikes.
- **Edge case:** autoscaling **thrashing** (flapping) from twitchy metrics — use
  cooldowns/target-tracking.
- **Tradeoff:** control vs convenience — **IaaS** gives control (and toil); **SaaS**
  gives convenience (and lock-in). **Public** is cheap/elastic; **private** is
  controlled/compliant.

---

## 18.11 Exam, Interview & Coding Perspectives

- **SEBI / RBI / NABARD (high yield):** the **NIST 5 characteristics**; **IaaS/PaaS/
  SaaS** with examples and *who manages what*; **deployment models** (public/private/
  hybrid/community); **shared-responsibility**; **elasticity/scaling**; **multi-
  tenancy**; that a cloud VM is a **guest OS on a Type-1 hypervisor**.
- **GATE:** cloud is light in GATE, but **virtualization**, **scheduling** (bin-
  packing ≈ scheduling), and **elasticity** connect to core OS topics.
- **Interview (backend/AI-infra — very high yield):**
  - "IaaS vs PaaS vs SaaS?" → **who manages the stack** (+ EC2 / App Engine / Gmail).
  - "What is serverless / a cold start?" → deploy a **function**; latency to
    **provision + init the sandbox** on first/scaled-out call.
  - "Horizontal vs vertical scaling — which and why?" → **horizontal** for stateless
    services (no ceiling, no downtime, resilient).
  - "How does the cloud decide where to run my container?" → a **scheduler**
    **bin-packs** by CPU/RAM requests + constraints.
  - "How do you isolate tenants?" → **VMs/microVMs** (hardware) + **namespaces/
    cgroups** (limits), guarding against **noisy neighbours**.
- **Coding/practical:**
  - `aws ec2 run-instances …`, an **Auto Scaling Group** with a target-tracking
    policy on CPU.
  - `kubectl autoscale deployment web --min=2 --max=10 --cpu-percent=70` (HPA).
  - A Lambda function behind an API Gateway; observe the **cold start** on the first
    request.

---

## 18.12 Concept Checks & MCQs (test yourself)

1. Who defines the standard "cloud" + 5 characteristics? → **NIST**.
2. List the NIST 5. → **on-demand self-service, broad network access, resource
   pooling, rapid elasticity, measured service**.
3. IaaS / PaaS / SaaS — one example each. → **EC2 / App Engine (Heroku) / Gmail**.
4. In which model do **you** manage the OS? → **IaaS**.
5. "Pay only for what you use" = which characteristic? → **measured service**.
6. Private vs public vs hybrid cloud? → **one org** vs **shared/public** vs **mix**.
7. A cloud VM runs on a ___ hypervisor. → **Type-1 (bare-metal)**.
8. EC2 / Azure / GCP hypervisors? → **Nitro(KVM) / Hyper-V / KVM**.
9. What do you deploy in FaaS? → **a function** (serverless).
10. What is a cold start? → latency to **create + initialise the sandbox** on first
    call.
11. What isolates a Lambda invocation? → a **Firecracker microVM**.
12. Horizontal vs vertical scaling? → **more machines** vs a **bigger machine**.
13. Cloud default for stateless services? → **horizontal** (behind a load balancer).
14. A common autoscaling metric? → **CPU utilisation** (also memory / request rate).
15. Placing workloads on machines to maximise utilisation? → **bin-packing**.
16. Google's cluster manager (K8s ancestor)? → **Borg**.
17. Many tenants sharing hardware? → **multi-tenancy** (resource pooling).
18. One tenant hogging shared resources? → **noisy neighbour** (fix: **cgroups/
    quotas**).
19. Who secures customer **data**? → the **customer** (shared responsibility).
20. Kubernetes autoscalers? → **HPA** (pods), **VPA** (pod size), **Cluster
    Autoscaler** (nodes).

**True/False**
- Serverless means there are no servers. → **False** (you just don't manage them).
- EC2 is a PaaS. → **False** (it's **IaaS**).
- Vertical scaling is unlimited. → **False** (hardware ceiling + reboot).
- A cloud VM is a guest OS on a Type-1 hypervisor. → **True**.
- The provider secures your data in SaaS. → **False** (data is always the
  customer's responsibility).
- Horizontal scaling adds more instances behind a load balancer. → **True**.

---

## 18.13 One-Page Revision Sheet

```
CLOUD = on-demand, pay-as-you-go compute/storage/network over the internet.
  "OS FOR THE DATA CENTRE": schedules VMs/containers onto machines, isolates tenants,
   meters + bills usage, abstracts hardware behind APIs.  ("Datacenter as a Computer")

NIST 5 (OB-REM): On-demand self-service | Broad network access | Resource pooling |
  rapid Elasticity | Measured service.

SERVICE MODELS (provider manages MORE as you go down):
  IaaS  you manage OS+runtime+app; provider = HW+virt    -> EC2, Azure VMs, GCP Compute
  PaaS  you manage app+data only                          -> App Engine, Heroku, Beanstalk
  SaaS  you just use it                                   -> Gmail, Salesforce, Office365
  (pizza-as-a-service). SHARED RESPONSIBILITY: provider = security OF cloud;
   customer = security IN cloud (DATA always yours).

DEPLOYMENT: public(shared) | private(1 org) | hybrid(mix) | community(group).

COMPUTE: a cloud VM = a GUEST OS on a TYPE-1 (bare-metal) HYPERVISOR.
  EC2->Nitro(KVM) / Azure->Hyper-V / GCP->KVM. Instance families = match HW to workload.

SERVERLESS / FaaS: deploy a FUNCTION; event-driven; auto-scale (to ZERO); pay per call.
  Lambda / Azure Functions / Cloud Functions. Sandbox = Firecracker microVM.
  COLD START = create+init sandbox+runtime+code on 1st/scaled call (latency).
  WARM START = reuse the running sandbox (fast). Stateless + ephemeral.

SCHEDULING = BIN-PACKING: pack workloads (CPU/RAM requests) onto nodes (bins) to
  maximise utilisation (NP-hard heuristics) + constraints (affinity/GPU/zone) + headroom.
  Cluster-as-a-computer: Borg / Kubernetes / Mesos. Tension: utilisation vs contention.

AUTOSCALING (= elasticity):
  VERTICAL scale up = bigger machine (ceiling + reboot; stateful DBs)
  HORIZONTAL scale out = more machines behind LB (near-unlimited, no downtime; DEFAULT)
  metrics: CPU util / memory / request rate / queue / latency (target tracking).
  K8s: HPA(pods) VPA(pod size) Cluster Autoscaler(nodes); AWS Auto Scaling Group.

MULTI-TENANCY = many tenants share HW (resource pooling). Isolate strongest->lightest:
  separate HW > VM > microVM > container(ns+cgroups) > process.
  NOISY NEIGHBOUR: one tenant hogs resources -> fix with cgroups/quotas + headroom.
```

### Flash cards

| Front | Back |
|-------|------|
| Standard cloud definition body? | NIST (5 characteristics) |
| NIST 5? | On-demand, broad access, pooling, elasticity, measured |
| IaaS / PaaS / SaaS example? | EC2 / App Engine / Gmail |
| Who manages the OS in IaaS? | You (the customer) |
| A cloud VM runs on? | A Type-1 (bare-metal) hypervisor |
| EC2 / Azure / GCP hypervisor? | Nitro(KVM) / Hyper-V / KVM |
| Serverless deploys what? | A function (FaaS) |
| Cold start? | Latency to create + init the sandbox |
| Lambda sandbox? | Firecracker microVM |
| Horizontal vs vertical? | More machines vs a bigger machine |
| Cloud scheduling problem? | Bin-packing (workloads → nodes) |
| Multi-tenancy risk? | Noisy neighbour (fix: cgroups/quotas) |
| Shared responsibility — your data? | Always the customer's |

### Spaced repetition
- **24-hour:** recite NIST-5 (OB-REM) and the IaaS/PaaS/SaaS examples + who-manages-
  what.
- **7-day:** explain serverless + cold start; horizontal vs vertical scaling with
  reasons; bin-packing; multi-tenancy isolation layers.
- **30-day:** given a workload (stateful DB, spiky web API, event handler, untrusted
  multi-tenant code), choose the service model + scaling strategy + isolation and
  justify it.

---

## 18.14 Summary

The **cloud** delivers compute on demand and, in doing so, acts as an **operating
system for the whole data centre** — scheduling, isolating, metering, and abstracting
a fleet of machines just as an OS does for one. The **NIST** definition (on-demand,
broad access, **resource pooling**, elasticity, **measured** service) frames it, and
the **three service models** — **IaaS** (rent the VM: EC2/Azure/GCP), **PaaS** (rent
the platform: App Engine/Heroku), **SaaS** (rent the app: Gmail) — differ by **who
manages the stack**, under a **shared-responsibility** split where **your data is
always yours**. Cloud **compute** is a **guest OS on a Type-1 hypervisor**;
**serverless/FaaS** hides even the OS and process, running your **function** in a
**Firecracker microVM** with a **cold-start** cost. Behind the scenes a **scheduler
bin-packs** workloads onto nodes, **autoscaling** adds capacity **horizontally**
(more machines) or **vertically** (bigger machines) by metrics like CPU, and
**multi-tenancy** shares hardware while **VMs/microVMs + cgroups/namespaces** keep
tenants isolated and tame the **noisy neighbour**.

This closes the systems arc that began in Module 1: from one machine and one kernel,
through processes, memory, and files, up to **virtualization (M17)** and now the
**cloud** — the platform on which **Module 19 — AI Infrastructure** builds GPU
scheduling and model serving.

> **You have mastered this module when** you can: state the NIST-5 and classify a
> product as IaaS/PaaS/SaaS with the right example; explain the shared-responsibility
> model; describe a cloud VM as a guest OS on a Type-1 hypervisor; explain serverless
> and cold starts; contrast horizontal vs vertical autoscaling with reasons; explain
> bin-packing scheduling; and describe multi-tenancy isolation and the noisy-neighbour
> problem — all without notes.
