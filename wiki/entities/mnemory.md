---
title: "Mnemory"
type: entity
tags: [memory, cross-session, MCP, self-hosted, vector-search, context-management]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Mnemory

Self-hosted MCP cross-session memory backend. OSS alternative to Anthropic's `memory_20250818` tool. Vendor-neutral: works with Claude Code, ChatGPT, Cursor, OpenWebUI, any MCP-capable client.

GitHub: https://github.com/fpytloun/mnemory

---

## Architecture

Two-tier storage:

```
Tier 1: Qdrant (vector database)
  → semantic embeddings of memory entries
  → similarity search for context-relevant retrieval
  → deduplication via embedding proximity

Tier 2: S3 / MinIO (artifact store)
  → long-form artifacts too large for vector storage
  → referenced by ID from tier 1
```

Memory lifecycle (single LLM call):
1. Extract candidate facts from conversation
2. Classify by type (decision, pattern, constraint, etc.)
3. Deduplicate against existing vectors
4. Handle contradictions (flag or overwrite depending on confidence)
5. Store in appropriate tier

---

## 16 MCP Tools

Exposed to agents via MCP server. Categories:
- **Read**: search by semantic query, retrieve by ID, list recent
- **Write**: store fact, store artifact, update entry
- **Manage**: list memories, delete, get contradictions, dedupe scan

Agents call these explicitly — memory extraction is not automatic. This is a deliberate design: automatic extraction creates noise; explicit calls ensure signal quality.

---

## Compared to Anthropic's memory_20250818

| Dimension | Mnemory | memory_20250818 |
|---|---|---|
| Hosting | Self-hosted (Qdrant + MinIO) | Client-side filesystem (`/memories/`) |
| Retrieval | Semantic vector search | File read (flat structure) |
| Deduplication | Built-in (vector proximity) | Manual (agent-written) |
| Contradiction handling | Automatic flagging | Manual (agent-written) |
| Vendor lock-in | None — any MCP client | Anthropic API only |
| Setup cost | High (Qdrant + S3 infra) | Low (flat files) |
| Context injection | Agent-requested retrieval | Agent-requested retrieval |

Neither is fully automatic. Both require the agent to make explicit tool calls to read/write. The difference is semantic search (Mnemory) vs. flat file navigation (Anthropic tool).

---

## Lifecycle Management — The Core Value

The key insight from the Mnemory author:

> "The useful part is not 'more context'; it is lifecycle management: deduping decisions, handling contradictions when a fact changes, expiring short-term context, and keeping longer details as artifacts instead of stuffing everything back into the prompt. If memory becomes a second messy knowledge base, it eventually hurts more than it helps."

This matches the [[concepts/context-compression]] principle: optimize for signal density, not volume.

---

## When to Use Mnemory vs Filesystem State

The Pocock workflow stores all state in git (PRD files, issue files, commits) — no memory system needed because the filesystem is the memory. Mnemory makes sense when:

- Working across multiple repos (memory doesn't belong to any one repo)
- Vendor-neutral (switching between Claude, Codex, Cursor on the same project)
- Decisions need semantic retrieval, not just file navigation
- Contradiction tracking is important (long-lived projects with changing constraints)

---

## Related Pages

- [[concepts/agentic-memory-tool]] — Anthropic's memory_20250818 tool; architecture comparison
- [[concepts/context-compression]] — compression strategies; Mnemory adds a memory-lifecycle layer
- [[concepts/context-engineering]] — the discipline Mnemory implements
- [[concepts/indirect-prompt-injection]] — memory files as injection vector (applies to both systems)
