---
title: "Scalability and Reliability"
type: concept
tags: [scalability, reliability, caching, sharding, rate-limiting, load-balancing, observability, slo, sla]
sources: ["system-design-primerREADME.md at master.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Scalability and Reliability

Implementation reference for the standard techniques that make systems handle more load and survive failures. Covers where each technique lives in the stack, when to apply it, and the invalidation / failure tradeoffs that come with it.

---

## Caching Strategies

Caching stores copies of computed or retrieved data closer to the requester. The fundamental tradeoff: cache improves read latency and reduces backend load, at the cost of potential staleness.

### Where caches live

| Layer | What is cached | Invalidation trigger |
|---|---|---|
| **Client (browser/OS)** | HTTP responses, DNS | TTL in Cache-Control header |
| **CDN** | Static assets, cacheable API responses | TTL, manual purge, content hash |
| **Reverse proxy** | Rendered responses, upstream API responses | TTL, manual purge |
| **Application** (Redis, Memcached) | DB query results, computed objects, sessions | TTL, write-through, explicit delete |
| **Database** | Query result sets, buffer pool | Internal to DB engine |

### Cache update strategies

**Cache-aside (lazy loading)** — application manages cache explicitly:
```
read: miss → load from DB → populate cache → return
write: update DB → (optionally) invalidate or update cache
```
Most common pattern. Cache only holds requested data. Miss adds 3 round trips (check cache, read DB, write cache). Stale on write unless you invalidate.

**Write-through** — cache is always updated on write:
```
write: update cache → cache synchronously writes to DB
read: always cache-warm for recently written data
```
No staleness on written data. New nodes (after failure/scaling) start cold — pair with cache-aside as fallback.

**Write-behind (write-back)** — writes go to cache first, asynchronously to DB:
```
write: update cache → return → async write to DB (batched)
```
Lower write latency. Risk: data loss if cache node fails before async write completes. Complex to implement correctly.

**Refresh-ahead** — proactively refresh cache entries before TTL expires based on predicted access patterns. Reduces miss-induced latency spikes for predictable hot data.

### Cache invalidation is the hard problem

"There are only two hard things in CS: cache invalidation and naming things." The practical issue: you must decide invalidation granularity. Invalidate by key (precise, misses related data), by tag (broader, safer for relational data), or by TTL alone (simplest, accepts bounded staleness).

---

## Database Sharding

Sharding distributes data across multiple database nodes (shards). Each shard owns a non-overlapping subset of the data. Sharding is the last resort for scaling a database — exhaust read replicas, caching, and hardware scaling first.

### Horizontal vs vertical partitioning

| Type | What it splits | When to use |
|---|---|---|
| **Horizontal (sharding)** | Rows across nodes (same schema, different data) | Row count exceeds single node capacity; write throughput ceiling |
| **Vertical** | Tables/columns across nodes (functional decomposition) | Different tables have very different access patterns; federation by feature |

### Shard key selection — the critical decision

The shard key determines which node a record lives on. A bad shard key creates **hotspots** (all traffic hitting one shard).

| Shard key type | Pros | Cons |
|---|---|---|
| **User ID** | Predictable, co-locates user data | Celebrities/power users cause hotspot shards |
| **Geographic** | Low latency for regional data | Uneven distribution if data is geographically skewed |
| **Hash of ID** | Even distribution | Cannot do range queries; losing a shard requires rehashing |
| **Consistent hashing** | Minimizes data movement on rebalancing | More complex to implement |

**Avoid**: shard keys that are monotonically increasing (e.g., auto-increment IDs with range sharding) — all writes go to the last shard.

### Sharding failure modes

- **Cross-shard joins**: joins across shards require application-level aggregation — expensive
- **Cross-shard transactions**: no single transaction across shards without 2PC (avoid) or Saga
- **Rebalancing**: resharding is operationally painful; consistent hashing reduces data movement
- **Hot shard**: power user data all lands on one shard — add a prefix or sub-shard

---

## Rate Limiting

Protects a service from being overwhelmed by a single client or class of requests. Also enforces fair usage in multi-tenant APIs.

### Algorithms

**Token bucket**: bucket holds up to N tokens; tokens added at fixed rate R; each request consumes 1 token. Allows bursting up to bucket capacity. Most common for API rate limiting.

**Leaky bucket**: requests enter a FIFO queue; processed at constant rate. Smooths bursty traffic to a steady stream — useful when the backend cannot handle bursts. Requests that overflow the queue are dropped/rejected.

**Fixed window counter**: count requests in a fixed time window (e.g., per minute). Simple. Failure mode: a client can double the rate by sending requests at the end of window N and start of window N+1.

**Sliding window log**: store timestamp of each request; count requests in the rolling window. Accurate but memory-intensive at scale.

**Sliding window counter**: approximation combining fixed window counts with interpolation. Accurate enough for most uses, memory efficient.

### Implementation

Rate limiting state must be shared across application server replicas — store counters in Redis. Use a Lua script for atomic check-and-increment. Return `HTTP 429` with `Retry-After` header.

Rate limiting can be applied per: IP, user ID, API key, endpoint, or request class. Apply multiple limits (per-second and per-day) for defense in depth.

---

## Load Balancing

Distributes incoming requests across a pool of servers. Eliminates single points of failure and enables horizontal scaling.

### Algorithms

| Algorithm | When to use |
|---|---|
| **Round robin** | Servers are homogeneous; requests are similar weight |
| **Weighted round robin** | Servers have different capacity |
| **Least connections** | Requests have highly variable duration (long-lived connections) |
| **IP hash / sticky sessions** | Session state is stored in application server memory (stateful apps — prefer to eliminate this) |
| **Random** | Simple, works well with large homogeneous pools |

### Layer 4 vs Layer 7

**Layer 4** (transport): routes by IP + port only; does not inspect packet contents. Faster, less CPU overhead. Cannot route based on URL, headers, or cookies.

**Layer 7** (application): inspects HTTP headers, URL, cookies. Can route `/api/video` to video servers and `/api/payment` to payment servers. Enables canary deployments, A/B routing. Higher CPU cost — negligible on modern hardware for most workloads.

### Sticky sessions

When session state lives in application memory, the load balancer must route a user's requests to the same instance (sticky sessions via cookie). This creates an uneven distribution problem and makes scaling and failover harder. **Prefer stateless application servers**: store sessions in a shared cache (Redis) so any instance can handle any request.

---

## Observability: Metrics, Logs, Traces

Observability is the ability to understand a system's internal state from its external outputs. Three signals, three different questions:

| Signal | Question it answers | Tool examples |
|---|---|---|
| **Metrics** | Is the system healthy right now? What is trending? | Prometheus, Datadog, CloudWatch |
| **Logs** | What happened during this event? What was the error message? | ELK stack, Loki, CloudWatch Logs |
| **Traces** | Where did this specific request spend its time? Which service was slow? | Jaeger, Zipkin, AWS X-Ray, OpenTelemetry |

### Metrics: what to measure

Use the **RED method** for services:
- **Rate**: requests per second
- **Errors**: error rate (4xx + 5xx / total)
- **Duration**: latency distribution (p50, p95, p99 — never just average)

Use the **USE method** for resources:
- **Utilization**: % of time resource is busy
- **Saturation**: queue depth or wait time
- **Errors**: error count for the resource

### Logs: structured over plaintext

Plaintext logs are hard to query at scale. Use structured JSON logs with consistent fields: `timestamp`, `level`, `trace_id`, `user_id`, `service`, `message`. This enables efficient querying and correlation with traces.

### Traces: distributed tracing

Each request gets a `trace_id`. Each service hop gets a `span_id` with start/end time. Traces answer: "why was this request slow?" — you can see which service added 200ms of latency. Requires instrumentation at every service boundary.

---

## SLO, SLA, and Error Budget

See [[concepts/error-budget]] for the full treatment. Summary for this page:

| Term | Definition |
|---|---|
| **SLI** (Service Level Indicator) | The metric being measured (e.g., request success rate) |
| **SLO** (Service Level Objective) | The target value for the SLI (e.g., 99.9% of requests succeed) |
| **SLA** (Service Level Agreement) | A contractual commitment to the SLO, with penalties for breach |
| **Error budget** | 1 - SLO; the allowance for unreliability before SLO is breached |

### Availability in numbers

| SLO | Annual downtime | Monthly downtime |
|---|---|---|
| 99% (two 9s) | 87.6 hours | 7.3 hours |
| 99.9% (three 9s) | 8.76 hours | 43.8 minutes |
| 99.99% (four 9s) | 52.6 minutes | 4.4 minutes |

**Components in series multiply availability downward**: two components each at 99.9% in series yields 99.8% overall. Parallel redundancy improves it: `1 - (1 - A₁)(1 - A₂)`.

---

## Cross-references

- [[systems/distributed-systems]] — backpressure, circuit breaker, CAP — underlying consistency/reliability contracts
- [[patterns/database]] — replication, indexing, query optimization
- [[concepts/error-budget]] — SRE error budget: retry, token, runtime, session budget axes
- [[concepts/self-healing-loop]] — failure detection, bounded retry, rollback, escalation
- [[concepts/agentic-cicd]] — CI as external watchdog when agents are the developer; staging-first, diff size caps
