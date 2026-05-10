---
title: "Cloudflare Agent Memory — Managed Cross-Session Memory Service"
type: summary
tags: [agent-memory, cloudflare, cross-session, retrieval, hyde, rrf]
sources:
  - "Agents that remember introducing Agent Memory.md"
created: 2026-05-07
updated: 2026-05-07
---

# Cloudflare Agent Memory — Managed Cross-Session Memory Service

Cloudflare Agent Memory is a managed memory-as-a-service for AI agents. Key differentiator from alternatives: a constrained, opinionated API over a 5-channel retrieval pipeline with Reciprocal Rank Fusion — rather than raw filesystem access or single-channel vector search.

## Core Abstraction: Memory Profile

A **memory profile** is an isolated store addressed by name. It is shared across sessions, agents, and users — enabling patterns like a code review bot and a coding agent sharing memory so that review feedback shapes future code generation.

### Operations

| Operation | Description |
|---|---|
| `ingest` | Bulk extract from a conversation chunk; called at compaction time |
| `remember` | Explicit single-fact storage |
| `recall` | Full 5-channel retrieval pipeline; returns synthesized answer |
| `list` | Enumerate stored memories |
| `forget` | Delete a memory entry |

`ingest` integrates with the compaction lifecycle: when a harness compacts context, it calls `ingest` on the content being discarded, preserving knowledge that would otherwise be lost.

## Memory Type Taxonomy

Four types, classified during the ingestion pipeline:

| Type | Description | Behavior |
|---|---|---|
| **Facts** | Atomic stable knowledge ("project uses GraphQL") | Keyed; superseded not deleted; version chain with forward pointer |
| **Events** | Timestamped occurrences (deployments, decisions) | Ordered by time |
| **Instructions** | Procedures, workflows, runbooks | Retrieved when task context matches |
| **Tasks** | Current in-progress work | Ephemeral; excluded from vector index |

The keyed supersession model for Facts is notable: rather than overwriting or creating duplicates, a new version is stored with a forward pointer to the prior version. This enables temporal reasoning ("what did the user prefer before they changed it?").

## Ingestion Pipeline

Five stages run sequentially on each `ingest` call:

1. **Deterministic ID generation** — SHA-256 of session + role + content, truncated to 128 bits. Idempotent: re-ingesting the same content is a no-op.
2. **Extraction** — Two passes: (a) full pass over 10K-char chunks, 4 chunks concurrently; (b) detail pass targeting concrete values (names, prices, version numbers). Results merged.
3. **Verification** — 8 checks: entity/object/location/temporal/org identity, completeness, relational consistency, inference support. Each item is passed, corrected, or dropped.
4. **Classification** — Assigned to one of the four memory types above.
5. **Storage** — `INSERT OR IGNORE` (content-addressed deduplication). Background async vectorization follows.

## 5-Channel Retrieval with RRF

`recall` runs five parallel retrieval channels, then merges via **Reciprocal Rank Fusion** with recency as tiebreaker:

| Channel | Mechanism | Strength |
|---|---|---|
| Full-text search | Porter stemming (BM25-style) | Exact term matching |
| Exact fact-key lookup | Direct topic match | Highest weight; precise fact retrieval |
| Raw message search | Verbatim content scan | Safety net for details extraction missed |
| Direct vector search | Semantic embedding similarity | Conceptual match |
| HyDE vector search | Hypothetical Document Embedding | Cross-vocabulary matching |

### HyDE — the key insight

HyDE rephrases the query as if it were the stored answer before embedding. Example: query "What package manager does the user prefer?" is transformed to "The user prefers pnpm" before embedding. This finds memories that use different vocabulary than the question, where direct embedding would fail or rank poorly.

HyDE is not unique to this service — it originates from the retrieval literature — but its combination with RRF fusion across 4 other channels is the architectural differentiator here.

## Design Philosophy

Cloudflare's explicit design choice: **constrained API over raw filesystem access**. Their claim (unverified against independent benchmarks): the constrained API outperforms raw filesystem access on reasoning tasks involving temporal logic, supersession, and instruction following, because the service can enforce invariants (dedup, versioning, type classification) that a raw filesystem agent cannot.

Compare: [[entities/mnemory]] gives raw Qdrant + S3 access; [[concepts/agentic-memory-tool]]'s `memory_20250818` gives raw flat file access. Cloudflare inserts a structured layer between the agent and storage.

## Documented Use Cases

- **Individual coding agents** — Claude Code, OpenCode: per-user memory profile accumulates project conventions, preferences, patterns across sessions.
- **Custom harnesses** — Ramp Inspect, Stripe Minions, Spotify background agent: long-horizon background agents use memory profiles to maintain state across task runs.
- **Shared team memory** — Code review bot and coding agent share a profile; review feedback (style violations, architectural preferences) is ingested and shapes future code generation without manual re-injection.

## Comparison to Alternatives

See [[concepts/agentic-memory-tool]] for the full 3-way comparison table (Mnemory / memory_20250818 / Cloudflare Agent Memory).

Short version: Cloudflare is the managed option with the most sophisticated retrieval but requires Cloudflare Workers or REST API integration. Mnemory is the self-hosted option with semantic retrieval but no memory taxonomy. `memory_20250818` is the lowest-friction option but tied to the Anthropic API and lacks structured retrieval.

## Related Pages

- [[concepts/agentic-memory-tool]] — concept page covering the full memory tool landscape
- [[entities/mnemory]] — self-hosted OSS parallel (Qdrant + S3)
- [[concepts/context-compression]] — compaction lifecycle; `ingest` integrates here
- [[concepts/agent-harness]] — harnesses that call `ingest` at compaction time
- [[concepts/contextual-retrieval]] — HyDE and RRF are retrieval techniques also used in RAG
