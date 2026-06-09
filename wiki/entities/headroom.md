---
title: "Headroom"
type: entity
tags: [context-compression, agent-tooling, kv-cache, proxy, mcp, memory, token-optimization]
sources: ["chopratejasheadroom Compress tool outputs, logs, files, and RAG chunks before they reach the LLM. 60-95% fewer tokens, same answers. Library, proxy, MCP server..md"]
created: 2026-06-08
updated: 2026-06-08
---

# Headroom

Context compression layer for AI agents. Sits between the agent and the LLM provider, compressing tool outputs, logs, RAG chunks, files, and conversation history before they reach the model.

Repo: `chopratejas/headroom` · License: Apache 2.0

Claimed savings: 60–95% token reduction (self-reported; unverified independently). See [[concepts/context-compression]] for methodology context.

---

## Four Deployment Modes

**Library** — inline in any app:
```python
from headroom import compress
messages = compress(messages, model="claude-sonnet-4-6")
```

**Proxy** — zero code changes, any language:
```bash
headroom proxy --port 8787
# point ANTHROPIC_BASE_URL at localhost:8787
```

**Agent wrap** — one command wraps a coding agent:
```bash
headroom wrap claude     # wraps Claude Code
headroom wrap codex
headroom wrap cursor
```

**MCP server** — for any MCP client:
- `headroom_compress` — compress context
- `headroom_retrieve` — fetch original (CCR)
- `headroom_stats` — compression metrics

---

## Pipeline Internals

Single lifecycle across all modes:

`Setup` → `Pre-Start` → `Post-Start` → `Input Received` → `Input Cached` → `Input Routed` → `Input Compressed` → `Input Remembered` → `Pre-Send` → `Post-Send` → `Response Received`

Key components:

**ContentRouter** — detects content type, dispatches to the right compressor.

**SmartCrusher** — JSON compression: arrays of dicts, nested objects, mixed types.

**CodeCompressor** — AST-aware for Python, JS, Go, Rust, Java, C++.

**Kompress-base** — HuggingFace model trained on agentic traces; handles prose and unstructured text.

**CacheAligner** — stabilizes prompt prefixes so provider KV caches actually hit. Runs before compression. Addresses the same problem as [[concepts/context-compression#kv-cache-optimization]] but as an automated transform rather than a design guideline.

**IntelligentContext** — score-based context fitting; learned importance weighting.

**CCR (Contextual Compression with Retrieval)** — reversible compression. Originals stored locally; LLM calls `headroom_retrieve` on demand. See [[#ccr-reversible-compression]] below.

---

## CCR — Reversible Compression

Standard compression is lossy — dropped tokens are gone. CCR is a different trade-off: compress aggressively into the context window, store originals locally, expose a retrieval tool so the LLM can fetch the full content when it needs it.

**When CCR wins over anchored summarization**: the agent can't predict in advance which details it will need — e.g., large tool output where only 10% matters but the 10% varies by query. CCR lets the LLM decide what to retrieve at inference time rather than requiring the compressor to predict relevance upfront.

**Limitation**: requires the LLM to correctly identify when to call `headroom_retrieve`. If the model doesn't know it's missing information, it won't ask. Anchored summarization is more reliable when critical information is predictable and structurally defined.

See [[concepts/context-compression]] — CCR maps to a fifth compression pattern not covered by the four strategies in that page.

---

## CacheAligner

Dedicated prefix-stabilization transform. Reorders and normalizes prompt content so that the stable prefix (system prompt, tool defs) is byte-identical across requests. Automates the KV-cache design rules in [[concepts/context-compression#kv-cache-optimization]].

Relevant if using `headroom proxy` — CacheAligner runs on every intercepted request.

---

## `headroom learn`

Mines failed agent sessions and writes corrections directly to `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`. Automated version of the manual [[concepts/preference-feedback-loop]] pattern.

Difference from manual `capture-mistake` + `synthesize-mistakes` workflow:
- Manual: mistake logged during session, synthesized into rules periodically by Claude
- `headroom learn`: post-session batch analysis, correction written directly to config files without human review step

Trade-off: faster feedback loop vs less curation control. For a personal wiki where rule quality matters, the manual workflow with human approval likely produces better rules.

---

## Cross-Agent Memory

`SharedContext` — shared compressed memory store across Claude, Codex, Gemini. Auto-dedup on write. Agent provenance tracked.

```python
ctx = SharedContext()
ctx.put("key", value, agent="claude")
result = ctx.get("key")  # available to any agent
```

Relevant for multi-agent harnesses where workers need shared state. See [[concepts/agent-harness]].

---

## Benchmark Claims (Self-Reported)

All numbers from README — not independently verified. Mark as (claimed, unverified).

| Workload | Before | After | Savings |
|---|---|---|---|
| Code search (100 results) | 17,765 | 1,408 | 92% (claimed) |
| SRE incident debugging | 65,694 | 5,118 | 92% (claimed) |
| GitHub issue triage | 54,174 | 14,761 | 73% (claimed) |
| Codebase exploration | 78,502 | 41,254 | 47% (claimed) |

Accuracy benchmarks (GSM8K, TruthfulQA, SQuAD v2, BFCL) claim ≥97% preservation at 19–32% compression. Methodology: `python -m headroom.evals suite --tier 1` — reproducible but self-administered.

---

## Related Pages

- [[concepts/context-compression]] — five compression strategies; CCR is the fifth
- [[concepts/agent-harness]] — where Headroom fits in a harness stack
- [[concepts/preference-feedback-loop]] — manual counterpart to `headroom learn`
- [[entities/opencode-dcp]] — similar prefix-rewriting approach but OpenCode-specific
