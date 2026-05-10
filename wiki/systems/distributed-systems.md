---
title: "Distributed Systems"
type: concept
tags: [distributed-systems, cap-theorem, consistency, idempotency, circuit-breaker, saga, backpressure]
sources: ["system-design-primerREADME.md at master.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Distributed Systems

Reference and design-time guide for the core guarantees, failure patterns, and coordination strategies every distributed system must handle. Each section pairs the concept with the tradeoff an agent or engineer must resolve when choosing it.

---

## CAP Theorem

In a distributed system you can guarantee at most two of three properties simultaneously:

| Property | Meaning |
|---|---|
| **Consistency (C)** | Every read returns the most recent write or an error |
| **Availability (A)** | Every request receives a response (may not be the latest version) |
| **Partition Tolerance (P)** | System continues operating despite network partitions |

Network partitions are a physical reality, so **P is non-negotiable**. The real choice is **CP vs AP**.

### Practical implications

**CP systems** (e.g., HBase, Zookeeper, traditional RDBMS with sync replication): sacrifice availability when a partition occurs — requests block or return errors rather than stale data. Use when: banking, inventory, anything requiring atomic reads/writes.

**AP systems** (e.g., Cassandra, DynamoDB, CouchDB): return possibly stale data during partitions, reconciling later. Use when: social feeds, DNS, shopping carts — any domain that tolerates temporary inconsistency.

The CAP theorem describes a binary boundary; real systems operate on a spectrum. Latency is the hidden third variable — strongly consistent systems pay in latency under load even without a partition.

---

## Consistency Patterns

| Level | Behavior | Use cases |
|---|---|---|
| **Strong** | All reads see latest write; synchronous replication | File systems, RDBMS transactions |
| **Eventual** | Reads will converge to latest write within milliseconds–seconds; async replication | DNS, email, highly available stores |
| **Weak** | No guarantee reads see recent writes | VoIP, realtime multiplayer (loss of recent state acceptable) |

### Conflict resolution strategies for eventual consistency

Eventual consistency pushes conflict resolution to the application layer. Common strategies:

- **Last-write-wins (LWW)**: timestamp decides winner — simple but loses data on concurrent writes
- **Vector clocks**: track causal history per node; detect concurrent writes explicitly (Amazon Dynamo approach)
- **CRDTs** (Conflict-free Replicated Data Types): data structures that merge deterministically — counters, sets, sequences
- **Application-level merge**: caller defines merge logic (e.g., union of sets, max of counters)

Choose LWW only if losing concurrent writes is acceptable. CRDTs when the data type maps naturally. Vector clocks when you need to expose conflicts to the user.

---

## Idempotency

An operation is **idempotent** if applying it multiple times produces the same result as applying it once.

Why it matters: networks fail, clients retry, message queues deliver at-least-once. Without idempotency, retries cause double-charges, duplicate records, or inconsistent state.

### Implementation patterns

- **Idempotency keys**: client sends a unique request ID; server stores `(key → result)` and returns cached result on duplicate. Used in Stripe and payment APIs.
- **Upsert semantics**: `INSERT ... ON CONFLICT DO UPDATE` instead of blind insert
- **Conditional writes**: `PUT /resource` with `If-None-Match` or optimistic locking (`UPDATE WHERE version = $expected`)
- **At-least-once with deduplication**: consumers check a seen-ids store before processing

HTTP method semantics: GET, PUT, DELETE are idempotent by spec. POST is not — wrap POST operations in idempotency keys when retries are possible.

---

## Circuit Breaker Pattern

Prevents cascading failures when a downstream service is degraded.

```
CLOSED → (failure threshold exceeded) → OPEN → (timeout) → HALF-OPEN → (success) → CLOSED
                                                                      → (failure) → OPEN
```

| State | Behavior |
|---|---|
| **Closed** | Requests pass through; failures counted |
| **Open** | Requests fail fast without calling the dependency |
| **Half-Open** | Limited probe requests allowed through to test recovery |

**When to use**: any synchronous service-to-service call where the callee can become slow or unavailable (databases, third-party APIs, downstream microservices).

**Failure mode without it**: thread pools exhaust waiting for slow downstream; entire call chain degrades.

Libraries: Resilience4j (Java), Polly (.NET), `pybreaker` (Python).

---

## Backpressure

When a producer outpaces a consumer, queue size grows unboundedly — eventually consuming all memory and degrading the entire system.

**Backpressure** is the mechanism by which a consumer signals capacity limits upstream, causing the producer to slow or shed load.

### Strategies

| Strategy | Mechanism | Tradeoff |
|---|---|---|
| **Bounded queue + reject** | Queue has max size; new requests get 503/429 | Visible failure, predictable latency |
| **Bounded queue + block** | Producer blocks when queue full | Back-pressure propagates upstream; risk of cascading stalls |
| **Rate limiting** | Token bucket / leaky bucket at ingress | Protects service; clients must handle 429 and retry with backoff |
| **Load shedding** | Drop lowest-priority requests under load | Requires request prioritization |

See [[systems/scalability-reliability]] for rate limiting algorithm details.

**Signal to caller**: return `HTTP 503` with `Retry-After` header, or use exponential backoff with jitter on the client side. Never silently queue indefinitely.

---

## Saga Pattern

Manages distributed transactions across multiple services without two-phase commit.

A saga is a sequence of local transactions. Each step publishes an event or message triggering the next. On failure, **compensating transactions** undo completed steps in reverse order.

### Choreography vs Orchestration

| | Choreography | Orchestration |
|---|---|---|
| **Control** | Each service reacts to events — no central coordinator | Central saga orchestrator drives the flow |
| **Coupling** | Low — services are event-driven | Higher — orchestrator knows the whole flow |
| **Observability** | Harder — flow is implicit in event chain | Easier — orchestrator tracks state explicitly |
| **Failure handling** | Each service emits its own compensating events | Orchestrator triggers compensations centrally |
| **Use when** | Simple flows, independently owned services | Complex flows with many steps, audit trail needed |

**Example** (order processing): Reserve inventory → Charge payment → Ship. If payment fails, emit "release inventory" compensating event.

---

## Two-Phase Commit (2PC) — and Why to Avoid It

2PC achieves distributed atomicity via a prepare phase and a commit phase coordinated across all participants.

**Problems**:
- **Blocking**: if coordinator fails after prepare but before commit, participants hold locks indefinitely
- **Single point of failure**: coordinator is critical path
- **Latency**: two network round trips for every transaction
- **Partition intolerance**: choosing CP at significant availability cost

**When it appears legitimately**: XA transactions within a single datacenter, legacy system integration with no alternative.

**Prefer instead**: Saga pattern for cross-service consistency. Design services to be idempotent and eventually consistent. Use a message queue (Kafka, SQS) as the coordination mechanism.

---

## Distributed Locks

Used when multiple nodes must not concurrently access a shared resource (job scheduling, inventory reservation, leader election).

| Approach | Tool | Notes |
|---|---|---|
| SETNX + TTL | Redis (Redlock) | Simple; has known correctness edge cases under clock drift |
| Ephemeral nodes | ZooKeeper | Strong consistency; operationally heavier |
| Leases | etcd | Strong consistency; good for Kubernetes-style workloads |
| Advisory locks | PostgreSQL `pg_advisory_lock` | Easy for single-DB systems; doesn't scale across services |

**Always set a TTL** to prevent lock starvation if holder crashes. **Always handle lock expiry**: the critical section must be shorter than the TTL, or implement lock heartbeat renewal.

**Fencing tokens**: use a monotonic counter issued with each lock grant. Pass the token to the resource being protected. Resource rejects operations from stale token holders — guards against process pauses (GC, OS) that expire the lock while the holder still runs.

---

## Cross-references

- [[systems/architectural-patterns]] — monolith vs microservices, event-driven architecture, CQRS
- [[systems/scalability-reliability]] — rate limiting algorithms, load balancing, caching, SLO/error budget
- [[patterns/concurrency]] — locking, optimistic concurrency, thread safety
- [[concepts/error-budget]] — SRE error budget adapted to distributed service reliability
- [[concepts/self-healing-loop]] — failure detection, retry, rollback patterns
