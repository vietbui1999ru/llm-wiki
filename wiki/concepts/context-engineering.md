---
title: "Context Engineering"
type: concept
tags: [context-engineering, agents, prompt-engineering, jit-retrieval, attention-budget]
sources:
  - "Effective context engineering for AI agents.md"
  - "Context windows.md"
created: 2026-04-27
updated: 2026-04-27
---

# Context Engineering

**Context engineering** is the discipline of curating and maintaining the optimal set of tokens during LLM inference. It is the natural progression of prompt engineering: where prompt engineering optimizes individual instructions, context engineering manages the entire token state (system prompts, tools, MCP servers, external data, message history) across multi-turn agent loops.

Coined formally by Anthropic's applied AI team; popularized alongside Karpathy's description as "the art and science of curating what will go into the limited context window."

## The Core Principle

**Find the smallest possible set of high-signal tokens that maximizes the likelihood of the desired outcome.**

This principle governs all four components of context:

### 1. System Prompts

Operate at the right **altitude** — the Goldilocks zone between two failure modes:

| Too brittle | Too vague |
|---|---|
| Hardcoded if-else logic for every edge case | High-level guidance with false assumptions of shared context |
| Fragile, expensive to maintain | Under-constrains model; unreliable outputs |

**Good prompt**: specific enough to guide behavior, flexible enough to give the model strong heuristics. Start minimal, test against the best available model, add instructions only to fix observed failure modes. Canonical diverse examples beat a laundry list of edge cases.

Structure with XML tags or Markdown headers (`<background_information>`, `<instructions>`, `## Tool guidance`).

### 2. Tools

Tools define the contract between agent and its information/action space. Bad tool design is one of the most common causes of agent failure.

Rules:
- Self-contained, robust to error, unambiguous in intended use
- No overlapping functionality between tools — if a human can't definitively choose which tool to use, neither can an agent
- Token-efficient return values — tool results go into context; bloat compounds
- Input parameters descriptive and unambiguous

See [[concepts/tool-design-for-agents]] for the dual-audience principle.

### 3. Just-in-Time (JIT) Retrieval

Rather than pre-loading all possible relevant data upfront, agents maintain lightweight **identifiers** (file paths, stored queries, web links) and dynamically load data at runtime via tools.

Benefits:
- Keeps base context small and focused
- Metadata of identifiers provides signals (file path hierarchy hints purpose; timestamps hint recency)
- Enables **progressive disclosure** — agent assembles understanding layer-by-layer, maintaining only what's necessary in working memory

**Example**: Claude Code drops CLAUDE.md files upfront but uses glob/grep for JIT file exploration — never loads the full codebase into context.

**Trade-off**: slower than pre-computed retrieval; requires well-designed tools and heuristics to avoid context waste from dead-ends.

**Hybrid strategy**: pre-load high-signal stable content (CLAUDE.md, system context); let agent retrieve dynamic content JIT.

### 4. Long-Horizon Techniques

For tasks spanning tens of minutes to hours:

**Compaction**: summarize conversation nearing the context limit; reinitiate new window with the summary plus 5 most recently accessed files. Art lies in selecting what to keep vs. discard — maximize recall first, then iterate to improve precision. Lightest form: tool result clearing (clear old tool results once they've served their purpose).

**Structured note-taking**: agent writes a persistent NOTES.md or similar; reads back on context reset. Provides durable memory with minimal overhead. Example: Claude playing Pokémon maintains accurate tallies across thousands of game steps via self-written notes.

**Sub-agent architectures**: specialist subagents with isolated context windows perform deep work; return distilled summaries (~1-2K tokens) to the lead agent. Lead agent maintains high-level plan; subagents handle parallel exploration. See [[concepts/agent-subagents]].

## Context Engineering vs. Prompt Engineering

| | Prompt Engineering | Context Engineering |
|---|---|---|
| Scope | Single instruction / system prompt | Full token state across all turns |
| Timing | One-time setup | Iterative curation each inference |
| Focus | How to write effective prompts | What information to include/exclude |
| Era | Early LLM applications | Multi-turn agentic workflows |

## Relationship to Existing Wiki Pages

- [[concepts/context-window]] — the constraint being engineered around
- [[concepts/context-degradation]] — failure modes context engineering prevents
- [[concepts/context-compression]] — one lever of context engineering (compression strategies)
- [[concepts/agentic-memory-tool]] — API primitives that implement compaction and note-taking
- [[concepts/agent-harness]] — the broader harness that orchestrates context management
- [[concepts/tool-design-for-agents]] — token-efficient tool design as context engineering
- [[summaries/context-window-cluster]] — consolidated source summary for this cluster
