---
title: "System Design Process"
type: concept
tags: [system-design, requirements, capacity-estimation, api-design, tradeoffs]
sources: ["system-design-primerREADME.md at master.md", "Machine-Learning-InterviewssrcMLSDml-system-design.md at main.md"]
created: 2026-05-06
updated: 2026-05-06
---

# System Design Process

A structured process for moving from a problem statement to a defensible system design. Applies equally to software design interviews, architecture reviews, and agent-assisted design tasks. The process is iterative — revisit earlier steps as constraints sharpen.

---

## Step 1: Requirements Clarification

Before drawing any boxes, define what the system must do and what constraints it operates under. Ambiguous requirements produce the wrong architecture.

### Functional requirements (what the system does)

- Who uses this system and how? (end users, internal services, third-party integrations)
- What are the core use cases? List the 3–5 most critical user flows.
- What are the inputs and outputs?
- What operations must be supported? (read, write, delete, search, stream, etc.)

### Non-functional requirements (how well the system does it)

| Dimension | Questions to ask |
|---|---|
| **Scale** | How many users? How many requests per second? Peak vs. average? |
| **Latency** | What is the acceptable p99 response time? Read latency vs. write latency? |
| **Availability** | What uptime is required? 99.9%? 99.99%? (see [[systems/scalability-reliability]]) |
| **Consistency** | Can the system tolerate stale reads? For how long? |
| **Durability** | What is the cost of data loss? |
| **Data volume** | How much data is stored? How fast does it grow? |
| **Read/write ratio** | 10:1? 100:1? 1:1? This drives storage and caching choices. |

### Common mistakes at this step

- Jumping to solutions before requirements are clear
- Treating all requirements as equally important — force-rank them
- Ignoring failure cases: what happens when a dependency is down?
- Not asking about the read/write ratio — it drives almost every subsequent decision

---

## Step 2: Capacity Estimation

Back-of-the-envelope calculations to bound the design space. Do not skip this — it determines whether you need sharding, caching, a CDN, or none of the above.

### QPS estimation

```
Daily active users (DAU) × actions per user per day
÷ 86,400 seconds
= average QPS

Peak QPS ≈ average × 2–10 (depending on traffic pattern)
```

### Storage estimation

```
Records per day × record size × retention period = total storage
```

Example: 10M messages/day × 1 KB/message × 5 years ≈ 18 TB

### Bandwidth estimation

```
QPS × average response size = outbound bandwidth
```

### Latency reference numbers (memorize these)

| Operation | Approximate latency |
|---|---|
| L1 cache | 0.5 ns |
| Main memory | 100 ns |
| SSD random read | 150 µs |
| Datacenter round trip | 500 µs |
| HDD seek | 10 ms |
| Cross-continent round trip | 150 ms |

These numbers constrain which designs are viable. If your design requires 5 database reads per request and each read is 1 ms, you cannot achieve a 2 ms p99.

---

## Step 3: High-Level Component Decomposition

Sketch the major components and their interactions before designing any one of them in detail.

### Standard component checklist

- **Client layer**: web, mobile, third-party API consumers
- **Load balancer / reverse proxy**: traffic distribution, SSL termination
- **Application servers**: stateless services handling business logic
- **Caching layer**: Redis/Memcached for hot reads
- **Primary datastore(s)**: SQL or NoSQL per access pattern
- **Message queue**: async work, decoupling producers from consumers
- **CDN**: static assets, geographically distributed content
- **Background workers**: jobs, batch processing, retries

### Decomposition heuristics

- One box per bounded responsibility — if a box does two things, split it
- Draw the data flow, not just the components: where does data enter, transform, and exit?
- Identify the single point of failure in your first sketch — every design has one; acknowledge it
- Ask: which component fails most often? Design for that failure first.

---

## Step 4: Data Flow Mapping

Trace the path of a request from client to storage and back. For each hop, identify:

- What protocol is used? (HTTP/REST, gRPC, message queue, WebSocket)
- Is this synchronous or asynchronous?
- What are the consistency requirements at this boundary?
- What happens if this hop fails?

### API contract design first

Define the API before implementing the internals. This forces clarity on:
- What data does the client actually need?
- What operations are exposed?
- What are the latency SLAs for each endpoint?

API-first prevents over-building: internal services often end up exposing data that no client uses, creating maintenance burden.

Example structure for a REST endpoint spec:
```
GET /posts/{userId}/feed
Response: { posts: [{ id, content, timestamp, authorName }], cursor }
Latency target: p99 < 200ms
Consistency: eventual (stale reads up to 5s acceptable)
```

---

## Step 5: Tradeoff Articulation

Every design decision involves competing constraints. A good design articulates these explicitly rather than pretending they don't exist.

### Common tradeoff axes

| Dimension A | Dimension B | Typical resolution |
|---|---|---|
| Consistency | Availability | CAP theorem — choose based on business requirement |
| Latency | Throughput | Optimize for the bottleneck; they are often inversely related |
| Read performance | Write performance | Denormalize for reads; normalize for writes |
| Simplicity | Flexibility | Prefer simplicity until a concrete driver for flexibility exists |
| Cost | Performance | Cache aggressively; the cheapest DB operation is the one you don't make |

### How to reason about competing constraints

1. State the constraint: "we need < 100ms p99 latency"
2. Identify what violates it: "5 synchronous DB reads per request at 20ms each = 100ms before any compute"
3. Name the tradeoff: "we can cache the top 80% of hot reads in Redis at the cost of up to 1s staleness"
4. Assert acceptability: "1s staleness is acceptable because [business reason]"

Tradeoffs that are not articulated are not made consciously — they are hidden risks.

---

## Step 6: Scale the Design

Only after a working baseline exists, identify bottlenecks and address them with targeted techniques.

Scaling interventions in rough order of complexity:
1. **Add caching** (cheapest; reduces DB load significantly)
2. **Add read replicas** (read-heavy workloads)
3. **Vertical scale** (buy time; not a long-term solution)
4. **Horizontal scale / stateless services** (application layer)
5. **Database sharding** (when a single DB node is the bottleneck)
6. **CDN** (static assets, geographically distributed reads)
7. **Async offload via message queue** (decouple slow operations)

See [[systems/scalability-reliability]] for implementation detail on each.

---

## Common Interview / Design Mistakes

| Mistake | Correction |
|---|---|
| Starting with architecture before requirements | Ask questions first; let requirements drive the design |
| Over-engineering from the start | Design the MVP first; add complexity only where a specific driver exists |
| Ignoring failure modes | Every component fails; identify SPOF in every design |
| "It can be cached" as a magic answer | Cache invalidation is hard; specify the invalidation strategy |
| Proposing microservices without justification | Monolith is correct by default; state the specific driver for decomposition |
| Skipping capacity estimation | You cannot choose the right database or caching strategy without knowing the scale |
| Not defining consistency requirements | Eventual vs. strong consistency has major architectural implications |

---

## Cross-references

- [[systems/architectural-patterns]] — monolith, microservices, CQRS — structural choices made after requirements are clear
- [[systems/distributed-systems]] — CAP, eventual consistency, saga — constraints that shape distributed designs
- [[systems/scalability-reliability]] — caching, sharding, load balancing, observability — scaling mechanics
- [[patterns/api-design]] — REST, gRPC, API contract conventions
