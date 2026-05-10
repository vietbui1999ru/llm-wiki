---
title: "Data Modeling"
type: concept
tags: [data-modeling, database, normalization, schema-evolution, polyglot-persistence, event-sourcing]
sources: ["system-design-primerREADME.md at master.md", "Decompose monoliths into microservices by using CQRS and event sourcing - AWS Prescriptive Guidance.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Data Modeling

Decision reference for choosing data storage types, structuring schemas, evolving them safely, and using multiple storage systems together. The central principle: **let your access patterns drive your data model**, not the other way around.

---

## Database Type Decision

### Relational (SQL)

**Core properties**: ACID transactions, structured schema, relational algebra (joins), strong consistency.

**When to choose**:
- Data is naturally relational with foreign key relationships
- You need complex joins across entities
- Transactions that must be atomic across multiple records (e.g., financial transfers)
- Strict schema is an asset — data integrity enforced at DB level
- Team has SQL expertise and established tooling

**Examples**: PostgreSQL, MySQL, SQLite, Amazon Aurora.

### Document Store

**Core properties**: schema-flexible, documents are self-contained JSON/BSON objects, good for nested/hierarchical data.

**When to choose**:
- Data has variable structure (not all records have the same fields)
- You're modeling "things" that are naturally contained (a product catalog item with varying attributes)
- Access pattern is typically "fetch the whole document" — limited cross-document joins
- Rapid iteration where schema changes frequently

**Watch out for**: data that is frequently joined across document types — this ends up as expensive application-level joins.

**Examples**: MongoDB, CouchDB, DynamoDB (with document semantics), Firestore.

### Wide Column Store

**Core properties**: data organized by row key + column families; designed for massive write throughput and linear horizontal scaling.

**When to choose**:
- Write-heavy, very large datasets (TB to PB scale)
- Time-series data, event logs, sensor data where rows are keyed by time
- Access pattern is known and narrow: you know your row key and column prefix
- High availability is a hard requirement

**Watch out for**: wide column stores sacrifice query flexibility. You design your table around your queries, not your entities. Schema changes are painful.

**Examples**: Cassandra, HBase, Google Bigtable.

### Graph Database

**Core properties**: nodes (entities) and edges (relationships) as first-class citizens; traversal queries are efficient.

**When to choose**:
- The domain is fundamentally relational between entities: social graphs, recommendation networks, fraud detection, knowledge graphs
- Many-to-many relationships are the rule, not the exception
- Queries traverse relationship paths (e.g., "friends of friends who bought X")

**Watch out for**: graph databases are less mature operationally than relational DBs; fewer ORMs and tooling options.

**Examples**: Neo4j, Amazon Neptune, TigerGraph.

### Time-Series Database

**Core properties**: optimized for appending timestamped data, efficient range queries by time, automatic retention policies and downsampling.

**When to choose**:
- Metrics, monitoring data, IoT sensor readings
- Access pattern is always "records in time range T1 to T2"
- Data volume grows continuously and old data can be aggregated or deleted

**Examples**: InfluxDB, TimescaleDB (PostgreSQL extension), Prometheus (pull-based metrics), Amazon Timestream.

### SQL vs NoSQL summary

| Choose SQL when | Choose NoSQL when |
|---|---|
| Structured, relational data | Semi-structured or variable schema |
| Complex joins needed | No cross-document joins needed |
| ACID transactions required | High throughput at the cost of eventual consistency |
| Data volume fits vertically scaled hardware | Very large data volumes (TB+) |
| Established query patterns | Rapidly evolving access patterns |

---

## Normalization vs Denormalization

### Normalization (1NF → 3NF)

The process of eliminating redundancy by decomposing tables so each fact is stored once.

- **1NF**: atomic column values, no repeating groups
- **2NF**: 1NF + no partial dependencies on a composite primary key
- **3NF**: 2NF + no transitive dependencies (non-key column depends only on primary key)

**Benefits**: no update anomalies (change a city name in one place, not thousands of rows), smaller storage footprint, easier to maintain data integrity.

**Cost**: reads require joins. At scale with 100:1 read:write ratios, those joins become expensive.

### Denormalization

Intentionally introducing redundancy to eliminate expensive joins. Store data in the shape you query it.

**When to denormalize**:
- Read:write ratio is very high (>10:1)
- Join latency is measurable and violates SLO
- The data being duplicated changes infrequently
- You are operating in a distributed environment where cross-shard joins are prohibitively expensive

**Cost**: updates must propagate to all copies. Use triggers, event sourcing, or application-level sync to keep copies consistent. A denormalized database under heavy write load can perform worse than its normalized counterpart.

**Materialized views** (PostgreSQL, Oracle): DB-managed denormalization — the DB maintains the redundant query result and updates it on writes. Lower application complexity than manual denormalization.

---

## Schema Evolution Strategies

Schemas must change as products evolve. The constraint: old readers must continue to work while new writers emit new shapes.

### Backwards-compatible migration patterns

**Additive changes only (safest)**:
- Add nullable columns — old code ignores them, new code uses them
- Never rename or delete columns in a deployed schema; add a new column and migrate data over time

**Expand-contract pattern** for breaking changes:
1. **Expand**: add the new column/field alongside the old one
2. **Migrate**: backfill data; update application code to write to both
3. **Cut over**: all reads switch to new column
4. **Contract**: drop the old column once no code reads it

**Versioned event schemas** (for event sourcing):
- Include a `schema_version` field in every event
- Consumers use the version to deserialize correctly
- Maintain upcasters that convert old event shapes to current form during replay

**Blue-green database migrations**: run two schema versions simultaneously during a deployment window. Both old and new application code must be able to read and write the schema. Simplifies rollback.

### What to avoid

- Renaming a column in a single deployment — guaranteed read failures during rolling deploy
- Adding NOT NULL columns without defaults — blocks all existing rows from satisfying the constraint
- Running migrations inside application startup — blocks deployment if migration is slow

---

## Event Sourcing as Data Model

Rather than storing current state, the database is an append-only log of events. Current state is computed by replaying events.

See [[systems/architectural-patterns]] for the architecture-level treatment. The data modeling implications:

- **Schema**: events are immutable; add new event types rather than modifying existing ones
- **Projections**: read models are derived by subscribing to the event stream and building materialized views optimized for specific queries
- **Temporal queries**: "what was the state at time T?" is free — replay events up to T
- **Data volume**: event logs grow indefinitely; implement snapshot checkpoints to avoid replaying the entire history on every restart

**When to use event sourcing as your primary data model**: high-value, audit-sensitive domains (finance, compliance, order management). Avoid for simple CRUD applications — the complexity is not warranted.

---

## Polyglot Persistence

Using multiple database types in a single system, each chosen for a specific access pattern.

**Example** (e-commerce):
- PostgreSQL — transactional order data, user accounts (ACID required)
- Redis — session storage, cart, rate limiting counters (fast key-value reads)
- Elasticsearch — product search (full-text, faceted search)
- Cassandra — user activity event log (high-write, time-ordered)
- S3 — product images, static assets (object storage)

### Tradeoffs

**Benefits**: each service uses the storage optimized for its access pattern; avoids forcing all data into one model that fits nothing well.

**Costs**:
- Operational overhead: multiple database systems to learn, monitor, back up, and scale
- Cross-store consistency: no single transaction spans multiple stores — requires Saga or eventual consistency
- Data duplication: the same logical entity may exist in multiple stores in different shapes; they can drift

**Decision heuristic**: start with one relational DB. Introduce a second storage type only when a specific, measured performance or modeling constraint requires it. Each additional store is an operational liability that must be justified.

---

## Data Access Pattern-Driven Design

The single most important principle: **design the schema around how data is queried, not how it is conceptually structured**.

This is especially critical for:

- **NoSQL stores**: no secondary index flexibility; query patterns must be known upfront
- **Sharded systems**: shard key must align with the most frequent access pattern
- **Distributed caches**: cache key must be derivable from the request without additional lookups

Process:
1. List the top 5 queries (by frequency or business criticality)
2. For each query, identify what the key lookup is
3. Design the primary key and secondary indexes to serve those queries efficiently
4. If two high-priority queries require conflicting key structures — consider maintaining two copies in different shapes (CQRS read model, materialized view, or denormalized table)

---

## Cross-references

- [[systems/architectural-patterns]] — CQRS, event sourcing at the architecture level
- [[patterns/database]] — indexing, query optimization, replication strategies
- [[systems/scalability-reliability]] — sharding, caching, and how they interact with data model choices
