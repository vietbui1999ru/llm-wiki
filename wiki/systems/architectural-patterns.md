---
title: "Architectural Patterns"
type: concept
tags: [architecture, microservices, monolith, event-driven, cqrs, event-sourcing, hexagonal, strangler-fig, modular-monolith, vertical-slice]
sources: ["system-design-primerREADME.md at master.md", "Decompose monoliths into microservices by using CQRS and event sourcing - AWS Prescriptive Guidance.md", "mehdihadeliawesome-software-architecture 📚 A curated list of awesome articles, videos, and other resources to learn and practice software architecture, patterns, and principles..md"]
created: 2026-05-06
updated: 2026-05-06
---

# Architectural Patterns

Design-time reference for structural patterns that govern how a system's components are organized, coupled, and evolved. Covers decision criteria rather than just definitions — the goal is knowing when to apply each pattern, not just what it is.

---

## Monolith vs Microservices

### Monolith

A single deployable unit containing all application logic. Not inherently bad — it is the correct starting point for most systems.

**Choose monolith when**:
- Team is small (< ~8 engineers working on the same codebase)
- Domain boundaries are not yet clear — premature decomposition creates the wrong services
- Operational overhead of distributed systems is not justified by the scale
- Latency between components matters (monolith avoids network hops)

**Monolith failure modes at scale**:
- Deployment coupling: any change requires redeploying the whole system
- Scaling bottleneck: cannot scale high-traffic components independently
- Technology lock-in: entire system must use the same language/runtime
- Team coordination overhead grows superlinearly as engineers multiply

### Microservices

A suite of independently deployable, small, modular services. Each owns its data, runs its own process, and communicates over a well-defined interface (REST, gRPC, message queue).

**Choose microservices when**:
- Teams need to deploy independently without coordinating with other teams
- Different components have different scaling requirements (read-heavy vs write-heavy)
- You need independent technology choices per service
- The domain is well-understood enough that service boundaries can be drawn without constant revision

**Microservices complexity costs**:
- Distributed systems problems: network failures, latency, partial failures (see [[systems/distributed-systems]])
- Data consistency: no cross-service transactions without Saga or 2PC
- Operational overhead: service discovery, observability, deployment pipelines per service
- Testing complexity: integration tests across service boundaries are harder

### Decision heuristic

Start with a modular monolith. Extract a service only when a specific, concrete driver exists: independent deployment, independent scaling, team autonomy. Never decompose speculatively.

---

## Event-Driven Architecture

Services communicate by producing and consuming events rather than calling each other directly.

**Core components**:
- **Event producer**: emits events when state changes (e.g., "OrderPlaced")
- **Event broker**: durable, ordered event log (Kafka, Kinesis, SQS)
- **Event consumer**: subscribes to events and reacts

**Advantages**:
- Loose temporal and spatial coupling — producer doesn't know or wait for consumers
- Easy to add new consumers without changing producers
- Natural audit log when events are durable
- Enables fan-out: one event triggers multiple independent downstream processes

**Failure modes**:
- Event schema evolution: consumers must handle old event shapes gracefully
- Ordering guarantees: most brokers guarantee order per partition/shard, not globally
- At-least-once delivery: consumers must be idempotent (see [[systems/distributed-systems]])
- Observability: tracing request flows across async boundaries requires correlation IDs

---

## CQRS (Command Query Responsibility Segregation)

Separates the model for **writes** (commands) from the model for **reads** (queries).

```
Client → Command Service → Write DB (normalized, optimized for writes)
                        → (event/stream) → Sync function
Client → Query Service  → Read DB  (denormalized, optimized for reads)
```

### When CQRS is warranted

CQRS adds operational complexity. It is justified when:
- Read and write load patterns are significantly different (e.g., 100:1 read:write ratio)
- Read and write models have divergent schema needs (aggregated reports vs. transactional records)
- You need to scale reads and writes independently
- The domain is complex enough that a single CRUD model becomes a bottleneck for both teams and performance

**Do not apply CQRS globally**. It applies to specific bounded contexts, not the whole application. Applied where it doesn't fit, it increases risk and reduces productivity.

### CQRS + Event Sourcing on AWS (reference implementation)

The AWS prescriptive guidance pattern uses:
- **Lambda functions** for command handlers (write operations: create, update, delete)
- **Separate Lambda functions** for query handlers (read operations: get, select)
- **Separate DynamoDB tables** for command DB and query DB
- **DynamoDB Streams** as the event sourcing mechanism to synchronize command DB changes to query DB

The event subscriber Lambda reads the stream and updates the query table — implementing eventual consistency between command and query models. See [[systems/architectural-patterns#event-sourcing]] below for the data model angle.

---

## Event Sourcing

Instead of storing current state, store an **append-only log of events** that led to the current state. Current state is derived by replaying events.

**Benefits**:
- Full audit trail by default — every state change is recorded
- Temporal queries: reconstruct state at any past point in time
- Replay: reprocess events through a new projection to build a new query model
- Decoupling: downstream consumers derive their own views from the same event stream
- Avoids update conflicts — writers append, never overwrite

**Complexity costs**:
- Schema evolution: old events must be interpretable by new code (versioned event schemas)
- Eventually consistent query models — there is a lag between write and query DB sync
- Undo requires a compensating event, not a DELETE
- Learning curve: different from CRUD thinking

**When to use**: high-value domains where audit trails matter (financial transactions, order history, compliance-sensitive operations), or when multiple downstream systems need to derive different views from the same source of truth.

---

## Hexagonal Architecture (Ports and Adapters)

The core application logic (domain) is isolated at the center. All external interactions (HTTP, DB, message queues, third-party APIs) connect through defined **ports** (interfaces) implemented by **adapters** (concrete implementations).

```
[HTTP Adapter] → [Port: UserRepository interface] → [Domain Logic]
[DB Adapter]   →                                  ←→ [Port: EventPublisher interface]
[Queue Adapter]→                                                   ↑
                                                            [Kafka Adapter]
```

**Value**: domain logic can be tested in isolation without real databases or HTTP stacks. Adapters can be swapped (e.g., SQL → NoSQL) without touching domain logic. Forces explicit dependency boundaries.

**When to apply**: any system where testability and long-term maintainability matter more than initial development speed. Especially valuable in ML systems where the model/inference engine is an adapter that can be swapped.

---

## Layered Architecture

The classic N-tier: Presentation → Application/Business Logic → Data Access → Database.

Each layer only calls the layer directly below it. Dependencies flow in one direction.

**Tradeoffs**:
- Simple to understand and reason about
- Works well for CRUD applications with straightforward flows
- Can become an anti-pattern when strict layering forces data to traverse unnecessary abstractions ("anemic domain model")
- Does not enforce dependency inversion — layers often end up tightly coupled despite the appearance of separation

**When layered is sufficient**: small-to-medium applications, teams new to the codebase, CRUD-heavy domains without complex business logic.

---

## Modular Monolith

An architectural middle ground: a single deployable unit (monolith) internally organized into strictly separated modules, each with its own bounded context, clear public API, and no direct access to another module's internals or database tables.

```
[Monolith binary]
  ├── module: Orders   (owns orders schema)
  ├── module: Billing  (owns billing schema)
  └── module: Inventory (owns inventory schema)
  
Cross-module calls: only via public module APIs, never via shared DB tables or direct object references.
```

**When to choose over plain monolith**: team has identified bounded contexts but isn't ready for microservices operational overhead. The modular structure allows extracting a module as a service later with minimal refactoring — the boundary is already enforced in code.

**When to choose over microservices**: domain boundaries are clear but deployment independence isn't required yet. Avoids distributed systems problems (network failures, eventual consistency, distributed tracing) while maintaining modularity.

**Failure mode**: modules that call each other's internal packages, share database tables, or import private types — these eliminate the modularity benefit and create a "distributed monolith" when later extracted.

---

## Vertical Slice Architecture

Organizes code around **features** (vertical slices through all layers) rather than technical layers (horizontal slices). Each feature owns its own handler, service, repository, and data model.

```
Horizontal (layered):           Vertical (sliced):
  Controllers/                    features/
  Services/                         PlaceOrder/
  Repositories/                       PlaceOrderHandler.ts
                                       PlaceOrderService.ts
                                       PlaceOrderRepository.ts
                                   GetOrderHistory/
                                       GetOrderHistoryQuery.ts
                                       ...
```

**Value**: each feature can be understood, tested, and changed in isolation. Adding a feature means adding a new folder, not modifying existing shared layers. Reduces the risk of regressions when changing unrelated features.

**Tradeoff**: cross-feature shared code (auth, validation utilities, DB connection) still needs a shared module. Without discipline this becomes a "shared" folder that grows into a second monolith inside the slice structure.

**Pairs well with**: CQRS (each command/query is a slice), Mediator pattern (slices register handlers, a mediator routes requests to them without coupling callers to handlers).

---

## Strangler Fig Pattern

A migration strategy for decomposing a monolith incrementally, without a big-bang rewrite.

1. Place a **facade** (reverse proxy or router) in front of the monolith
2. Implement one feature as a new microservice
3. Route that feature's traffic to the new service through the facade
4. Repeat — incrementally strangle the monolith until it no longer handles any traffic

**Why it works**: the monolith continues running throughout. Risk is per-feature, not per-migration. The facade absorbs routing complexity so clients are unaware of the transition.

**Failure modes**: the facade becomes a bottleneck or single point of failure. Shared data between monolith and new service creates coupling — plan data ownership carefully before extracting each feature.

See also: [[concepts/agentic-cicd]] for how CI gates apply during incremental architectural migrations.

---

## Cross-references

- [[systems/distributed-systems]] — consistency, saga, idempotency — required reading before adopting microservices
- [[systems/system-design-process]] — requirements clarification before choosing an architecture
- [[patterns/principles]] — SOLID, single responsibility, dependency inversion — underpins hexagonal and layered patterns
- [[concepts/agentic-cicd]] — CI as external watchdog when agents are building or migrating systems
