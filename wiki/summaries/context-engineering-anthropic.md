---
title: "Context Engineering for AI Agents — Anthropic"
type: summary
tags: [context-engineering, agent-engineering, compaction, memory, sub-agents]
sources:
  - "Effective context engineering for AI agents.md"
  - "Memory & context management with Claude Sonnet 4.6.md"
created: 2026-05-07
updated: 2026-05-07
---

# Context Engineering for AI Agents — Anthropic

Anthropic's official framing of context engineering as the successor to prompt engineering. Published with the Claude Sonnet 4.6 launch alongside the memory tool beta.

---

## Context Engineering vs. Prompt Engineering

**Prompt engineering**: how to write and organize LLM instructions for optimal outputs.

**Context engineering**: strategies for curating and maintaining the optimal set of tokens during inference — including everything beyond the prompt (tools, MCP, external data, message history).

Key distinction: context engineering is iterative; curation happens at every turn, not once.

---

## Why Context Is a Finite Resource

- LLMs have an **attention budget** drawn on when parsing context
- Transformer architecture creates O(n²) pairwise relationships — attention quality degrades with length
- **Context rot** (from chroma research): as token count grows, model accuracy on recall decreases
- Models have less training on long sequences → performance gradient, not hard cliff

Guiding principle: **smallest possible set of high-signal tokens that maximize desired outcome**.

---

## System Prompt Design

Operate at the **right altitude** — Goldilocks between:
- Too brittle: hardcoded complex if-else logic; fragile, high maintenance
- Too vague: fails to give concrete signals; assumes shared context

Organize with clear sections (`<background_information>`, `<instructions>`, `## Tool guidance`). Use minimal prompt that fully outlines expected behavior — minimal ≠ short.

---

## Tool Design for Context Efficiency

- Minimal overlap in functionality; unambiguous trigger per tool
- Return token-efficient results (bloated tool output pollutes context)
- Few-shot examples: curate diverse canonical examples, not exhaustive edge cases

See [[concepts/tool-design-for-agents]].

---

## Context Retrieval: Just-in-Time Approach

Rather than pre-processing all data, agents maintain lightweight identifiers (file paths, queries, links) and load data on demand via tools.

Claude Code implements this: `CLAUDE.md` dropped in up front; `glob`/`grep` used for JIT file retrieval. Avoids stale indexing and complex syntax trees.

**Progressive disclosure**: each interaction yields context that informs the next decision. File sizes suggest complexity; names hint purpose; timestamps proxy relevance. Agents assemble understanding layer by layer.

Trade-off: runtime exploration is slower than pre-computed retrieval. Hybrid strategy (some data pre-loaded, some explored autonomously) is often optimal.

---

## Long-Horizon Techniques

Three strategies for tasks that exceed context window:

### 1. Compaction

Summarize nearing-limit context, reinitiate new window with summary.

CC implementation: pass message history to model → preserves architectural decisions, unresolved bugs, implementation details; discards redundant tool outputs. Resumes with compressed context + 5 most recently accessed files.

Art: what to keep vs. discard. Too aggressive = loss of subtle critical context. Start by maximizing recall, then improve precision. Safest form: **tool result clearing** (clear old tool call/result pairs, keep user messages).

### 2. Structured Note-Taking (Agentic Memory)

Agent writes notes persisted outside context window; pulled back in at later turns.

Examples: Claude Code todo lists, NOTES.md files, memory tool (`memory_20250818`). Claude playing Pokémon — maintains tallies, maps, strategies across thousands of steps and context resets.

Memory tool commands: `view`, `create`, `str_replace`, `insert`, `delete`, `rename`. Security concern: memory files are read back into context → prompt injection vector; use path validation and content sanitization.

### 3. Sub-Agent Architectures

Specialized sub-agents handle focused tasks with clean context windows. Each explores extensively (tens of thousands of tokens) but returns condensed summary (1,000–2,000 tokens) to lead.

Separation of concerns: detailed search context stays isolated in sub-agents; lead synthesizes. Showed substantial improvement over single-agent on complex research tasks.

---

## Context Editing API (Beta)

Two automated strategies via `betas: ["context-management-2025-06-27"]`:

**`clear_tool_uses_20250919`**: Clears old tool call/result pairs when context exceeds token threshold.
```python
{"type": "clear_tool_uses_20250919", "trigger": {"type": "input_tokens", "value": 35000}, "keep": {"type": "tool_uses", "value": 5}}
```

**`clear_thinking_20251015`**: Manages extended thinking blocks. Must come first when combining.
```python
{"type": "clear_thinking_20251015", "keep": {"type": "thinking_turns", "value": 1}}
```

Memory (files on disk) survives context editing — this is the key separation: short-term context is disposable, long-term memory persists.

---

## Related Pages

- [[concepts/context-compression]] — three compression strategies; clear-over-compact as consensus
- [[concepts/context-degradation]] — five failure modes (lost-in-middle, poisoning, distraction, confusion, clash)
- [[concepts/context-engineering]] — wiki concept page
- [[concepts/agentic-memory-tool]] — memory_20250818 API detail
- [[concepts/agent-subagents]] — sub-agent architecture for context isolation
- [[concepts/ralph-loop]] — harness pattern for long-horizon continuation
