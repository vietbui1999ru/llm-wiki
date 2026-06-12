---
title: "Database Patterns"
type: pattern
tags: [patterns, database, sql, software-engineering]
sources:
  - "A detailed guide on Database Indexes.md"
created: 2026-05-06
updated: 2026-05-06
---

# Database Patterns

Reference and agent guide for indexing strategies, query optimization, transaction patterns, connection pooling, and read/write architecture.

## Agent Trigger

**Apply when:** Writing or reviewing schema, queries, indexes, transactions, or connection pooling.
**Rule of thumb:** Read the query plan, index for access patterns, kill N+1s, pick the right isolation level.

---

## Indexing Strategies

An index is a separate data structure that maps indexed column values to row locations, enabling the database to skip full table scans.

**Cost:** Every index adds write overhead (insert/update/delete must also update the index) and disk space. Over-indexing slows writes more than it helps reads.

### B-Tree Index (default)

Self-balancing tree. All major RDBMS (PostgreSQL, MySQL, SQL Server) use B+ tree variants where all data values live in leaf nodes.

**Supports:** Equality (`=`), range (`<`, `>`, `BETWEEN`), `ORDER BY`, prefix `LIKE 'foo%'`.

**Does not support:** `LIKE '%foo'` (trailing wildcard), non-orderable types.

**When to use:** Default choice for any column in a `WHERE`, `JOIN`, or `ORDER BY` clause with reasonable cardinality.

### Hash Index

Maps keys to bucket locations via a hash function. O(1) lookup.

**Supports:** Equality only (`=`).

**Does not support:** Range queries, sorting.

**When to use:** Exact-match-only lookups on very high cardinality columns where range is never needed (UUIDs, session tokens). PostgreSQL builds hash indexes; MySQL InnoDB does not.

### Composite (Multi-Column) Index

Index on two or more columns together: `(a, b, c)`.

**Key rule — leftmost prefix:** The index can be used by queries that filter on `(a)`, `(a, b)`, or `(a, b, c)` — but NOT on `(b)` or `(c)` alone.

**When to use:** Queries that always filter on multiple columns together. Column order matters: put the most selective / most frequently filtered column first.

**Anti-pattern:** Creating `(a, b)` and `(b, a)` separately when one order covers all queries; having many single-column indexes when a composite would serve the actual query patterns.

### Covering Index

An index that includes all columns a query needs, so the database never touches the underlying table (index-only scan).

```sql
-- Query: SELECT email FROM users WHERE last_name = 'Smith'
-- Covering index: (last_name, email)
-- DB reads only the index; no table access needed
```

**When to use:** Hot queries that select a small, predictable set of columns. Large performance gain for read-heavy tables.

**Anti-pattern:** Including too many columns in the covering index — defeats the write-overhead trade-off.

### Bitmap Index

Stores a bit vector per distinct value. Bitwise AND/OR operations filter multiple conditions simultaneously.

**When to use:** Low cardinality columns (status, gender, country) in analytical / OLAP workloads with complex multi-condition filters.

**When NOT to use:** OLTP tables with frequent writes (bitmap index locks rows on update; high contention).

### Filtered / Partial Index

Indexes only a subset of rows matching a `WHERE` condition.

```sql
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

**When to use:** When queries almost always filter on a specific value (active records, unprocessed queue items). Smaller index = faster lookup + less write overhead.

### Full-Text Index

Inverted index for text search. Tokenizes text, indexes individual words.

**When to use:** Free-text search over document content. Not a substitute for Elasticsearch for complex search — but adequate for moderate use cases.

### Smart indexing rules

1. Index columns used in `WHERE`, `JOIN ON`, and `ORDER BY` clauses of frequent queries.
2. Prefer high-cardinality columns (unique values spread widely). Indexing a boolean column with 50/50 split rarely helps.
3. Analyze query patterns before creating indexes — don't guess.
4. Remove unused indexes. `pg_stat_user_indexes` (PostgreSQL) shows index usage counts.
5. Don't index every column — writes pay for every index on the table.

---

## Query Optimization

### EXPLAIN / EXPLAIN ANALYZE

`EXPLAIN` shows the query plan the optimizer chose. `EXPLAIN ANALYZE` actually runs the query and shows real execution times.

**Key things to look for:**
- `Seq Scan` on a large table — likely missing an index
- `Nested Loop` with large row estimates — may indicate N+1 or missing join index
- High `rows` estimates that diverge from `actual rows` — stale statistics; run `ANALYZE`
- Sort / Hash operations on large datasets — may need an index to support `ORDER BY`

### N+1 Problem

**Pattern:** Fetch N parent records, then issue one query per parent to fetch related children. Results in N+1 round trips.

```sql
-- 1 query: SELECT * FROM posts  (returns 100 posts)
-- 100 queries: SELECT * FROM comments WHERE post_id = ?  (one per post)
```

**Fix:** Use a JOIN or an ORM eager-load mechanism.

```sql
SELECT posts.*, comments.*
FROM posts
LEFT JOIN comments ON comments.post_id = posts.id
WHERE posts.author_id = ?
```

Or in ORMs: `Post.includes(:comments)` (Rails), `.prefetch_related('comments')` (Django), `query.options(joinedload(Post.comments))` (SQLAlchemy).

**Detection:** Log slow queries; look for patterns of repeated identical queries with different IDs. Tools like Bullet (Rails) or Django Debug Toolbar flag N+1 automatically.

### Query Plan Reading

- `Index Scan` — good; uses index to find rows, then fetches from table
- `Index Only Scan` — best; covering index, no table access
- `Seq Scan` — full table scan; bad on large tables (acceptable on small ones)
- `Hash Join` — efficient for joining large sets
- `Nested Loop` — efficient when inner set is small; bad when outer set is large and inner is un-indexed

---

## Connection Pooling

Each database connection is a TCP connection + server-side process/thread. Creating connections per request is slow and resource-intensive.

A connection pool maintains a set of pre-established connections shared across application instances.

**Key parameters:**
- `min_connections` — connections kept alive even when idle (warmup)
- `max_connections` — hard ceiling; must be < DB server's `max_connections`
- `connection_timeout` — how long to wait for a free connection before erroring
- `idle_timeout` — close connections idle longer than this

**Common tools:** PgBouncer (PostgreSQL), HikariCP (Java), pgpool-II, application-level pools (SQLAlchemy, ActiveRecord, Prisma).

**Anti-patterns:**
- No pool at all (new connection per request)
- Pool max > DB server max (connections queue or error)
- Not returning connections to pool on error paths (pool exhaustion)

**PgBouncer modes:**
- Session mode — one client gets one server connection for the entire session (safe, minimal savings)
- Transaction mode — connection returned to pool after each transaction (more efficient; incompatible with session-level state like `SET LOCAL`)
- Statement mode — returned after each statement (very restrictive; rarely used)

---

## Transaction Patterns

### ACID Properties

- **Atomicity** — all operations in a transaction succeed or all are rolled back
- **Consistency** — transaction brings the database from one valid state to another
- **Isolation** — concurrent transactions don't see each other's intermediate state
- **Durability** — committed transactions survive crashes

### Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| Read Uncommitted | yes | yes | yes |
| Read Committed (default most DBs) | no | yes | yes |
| Repeatable Read | no | no | yes |
| Serializable | no | no | no |

**Practical guidance:**
- `Read Committed` is the PostgreSQL default and sufficient for most OLTP workloads.
- `Repeatable Read` when you need consistent reads across multiple statements in a transaction (e.g., report generation).
- `Serializable` for financial transactions where phantom reads would cause correctness problems. Higher contention cost.

### Optimistic Locking

Read a row with a version field. Before updating, check that the version hasn't changed. Retry if it has (conflict detected).

**When to use:** Low-contention workloads; scenarios where most transactions succeed without conflict. Avoids holding locks during user think-time.

```sql
-- Read
SELECT id, balance, version FROM accounts WHERE id = ?
-- Update (fails if another transaction changed version)
UPDATE accounts SET balance = ?, version = version + 1
WHERE id = ? AND version = ?
-- If 0 rows updated → conflict → retry
```

### Pessimistic Locking

Lock the row on read to prevent other transactions from modifying it.

```sql
SELECT * FROM accounts WHERE id = ? FOR UPDATE;
```

**When to use:** High-contention resources where conflicts are frequent and retrying is expensive; when correctness is critical and retries are unacceptable.

**Anti-pattern:** Holding a `FOR UPDATE` lock while doing external I/O (HTTP call, file write) — starves other transactions.

### Short Transactions

Keep transactions as short as possible. Long-running transactions hold locks, block vacuuming (PostgreSQL), and increase the chance of conflict.

**Anti-pattern:** Opening a transaction, calling an external API, then committing — the lock is held for the entire API round-trip.

---

## Read / Write Splitting

Route write operations to a primary replica and read operations to one or more read replicas.

**When to use:** Read-heavy workloads where the primary is CPU/IO bound; reporting queries that would slow down OLTP primary.

**Caveats:**
- Replication lag — reads from replica may see stale data. For writes that must immediately read their own writes, route to primary.
- Failover complexity — application must handle primary failure and replica promotion.

**Implementation:** Application-level (connection routing in ORM), middleware (ProxySQL, PgBouncer with routing), or cloud managed (AWS RDS read replicas).

---

## When to Denormalize

Normalized (3NF) schema reduces redundancy and makes writes clean. Denormalized schema duplicates data to speed reads.

**Reasons to denormalize:**
- A JOIN across multiple large tables is too slow even with indexes
- A derived value (total_count, last_activity_at) is queried on every request but expensive to compute
- Read throughput vastly exceeds write throughput (OLAP, dashboards)

**Patterns:**
- Precomputed aggregate columns (`orders.total_item_count` updated on order item insert/delete)
- Materialized views (DB-native precomputed JOIN result, refreshed on schedule or on change)
- Event sourcing with a read model (separate read-optimized projection updated from events)

**Anti-patterns:**
- Denormalizing prematurely before measuring the query performance problem
- Denormalizing without a clear consistency strategy (how is the redundant data kept in sync?)

---

## Cross-references

- [[systems/data-modeling]] — normalization, schema design, entity relationships
- [[systems/scalability-reliability]] — sharding, replication, caching layers, CAP trade-offs
- [[patterns/principles]] — trade-offs between write overhead and read performance are a general engineering principle
