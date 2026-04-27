---
title: "Context Windows, Context Engineering, and Agentic Memory"
type: summary
tags: [context-window, context-engineering, memory, agents, compaction, kv-cache]
sources:
  - "Context windows.md"
  - "LLM context windows what they are & how they work.md"
  - "Top techniques to Manage Context Lengths in LLMs.md"
  - "Effective context engineering for AI agents.md"
  - "Memory & context management with Claude Sonnet 4.6.md"
created: 2026-04-27
updated: 2026-04-27
---

# Context Windows, Context Engineering, and Agentic Memory

Five sources consolidated into one cluster. Three distinct layers: hardware constraints → engineering discipline → API primitives.

## Layer 1: Fundamental Constraints

Context windows exist because of **transformer architecture constraints**:
- **O(n²) attention complexity** — every token attends to every other; doubling context quadruples work
- **KV cache memory growth** — GPU VRAM fills as sequence length grows; inference degrades from fast (SRAM) to slow (HBM)
- **Context rot** — accuracy degrades as token count grows, not at a hard cliff but a performance gradient

Current window sizes: Claude 4 = 1M tokens, GPT-4o = 128K, Gemini 2.5 Pro = 2M. Larger is not automatically better — accuracy degrades past ~32K for most long-context models ("lost-in-the-middle" effect).

**Context awareness (Sonnet 4.6+):** Model receives explicit `<budget:token_budget>` at start and `<system_warning>` after each tool call showing remaining tokens. Enables better self-managed pacing on long tasks.

## Layer 2: Context Engineering as Discipline

Anthropic's framing (from engineering blog): context engineering is the natural progression from prompt engineering. Where prompt engineering optimizes single-turn instructions, context engineering manages the full token state across multi-turn agent loops.

**Core principle:** Find the *smallest possible set of high-signal tokens* that maximizes desired outcome. Token budget is a finite resource with diminishing marginal returns.

### System prompts
Operate at the right "altitude": not brittle hardcoded if-else logic, not vague high-level gestures. Minimal instruction set that fully captures desired behavior. Diverse canonical examples beat a laundry list of edge cases.

### Tools
Token-efficient return values. One unambiguous trigger per tool. Bloated tool sets with overlapping functionality are a major failure mode.

### Just-in-time (JIT) retrieval
Rather than pre-loading all context upfront, agents maintain lightweight identifiers (file paths, query strings, URLs) and load data at runtime via tools. Claude Code uses this: CLAUDE.md pre-loaded, glob/grep for JIT file exploration. Mirrors human cognition (file systems, bookmarks, inboxes).

### Long-horizon techniques

| Technique | Mechanism | Best for |
|---|---|---|
| **Compaction** | Summarize conversation nearing limit; reinitiate with summary | Conversational flow requiring back-and-forth |
| **Structured note-taking** | Agent writes NOTES.md or similar; reads back on resume | Iterative development with clear milestones |
| **Sub-agent architectures** | Specialist subagents with isolated context return ~1-2K token summaries to lead | Complex research/analysis with parallel exploration |

## Layer 3: Six Management Techniques

| Technique | Mechanism | Pros | Cons |
|---|---|---|---|
| Truncation | Cut tokens once limit reached; prioritize must-have over optional | Simple, low overhead | Dumb — may cut critical info |
| Model routing | Route large inputs to higher-context models (LiteLLM) | No data loss | Higher cost |
| Memory buffering | Summarize every N messages; preserve key entities | Adaptive, customizable | Short-term only, not for large docs |
| Hierarchical summarization | Chunk → summarize → re-summarize (pyramid) | Scalable, flexible granularity | Cumulative error risk |
| Context compression | Remove redundancy via knowledge graph; 40-60% token reduction | Maintains continuity | Quality-dependent |
| RAG | Retrieve only relevant chunks at query time | Scales to large corpora, accurate | Retrieval latency, setup complexity |

**Decision guide:**
- Sourced Q&A → RAG
- Multi-session chat → memory buffering
- Long documents (books, legal) → hierarchical summarization
- High token cost → context compression
- Sensitive/regulated content → RAG with exact retrieval (no summarization)

## Layer 4: Anthropic API Primitives (beta)

**Memory tool** (`memory_20250818`): client-side file-based memory system. Claude makes `view`/`create`/`str_replace`/`insert`/`delete`/`rename` tool calls; application executes against a local `/memories` directory. Enables cross-session learning.

**Context editing** (`context-management-2025-06-27` beta):
- `clear_tool_uses_20250919` — clear old tool results when input token threshold exceeded; configurable `keep` value
- `clear_thinking_20251015` — clear accumulated extended thinking blocks; `clear_thinking` must come first in `edits` list

**Server-side compaction**: available in beta for Opus 4.7, Opus 4.6, Sonnet 4.6. Automatic summarization of earlier conversation content; minimal integration work.

**Security note**: Memory files are read back into context → prompt injection vector. Mitigations: content sanitization, per-project/per-user isolation, memory auditing, and instructing Claude to ignore instructions in memory.

## Relationship to Existing Wiki Pages

- [[concepts/context-degradation]] — five failure modes (lost-in-middle is the "context rot" discussed here)
- [[concepts/context-compression]] — three compression strategies (anchored iterative is the structured note-taking / compaction pattern)
- [[concepts/agent-harness]] — harness components including context management layer
- [[concepts/tool-design-for-agents]] — token-efficient tool return values; one unambiguous trigger per tool
- [[concepts/agent-subagents]] — sub-agent architectures for context isolation
