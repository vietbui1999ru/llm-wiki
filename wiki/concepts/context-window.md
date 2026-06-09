---
title: "Context Window"
type: concept
tags: [context-window, transformers, kv-cache, context-rot, llm-architecture]
sources:
  - "Context windows.md"
  - "LLM context windows what they are & how they work.md"
  - "Top techniques to Manage Context Lengths in LLMs.md"
  - "Effective context engineering for AI agents.md"
  - "Memory & context management with Claude Sonnet 4.6.md"
created: 2026-04-27
updated: 2026-05-27
---

# Context Window

A **context window** is the maximum number of tokens an LLM can process in a single request — both input and generated output combined. It is the model's "working memory": everything the model can attend to at once.

**Key formula**: `input_tokens + output_tokens ≤ context_window_size`

## Why Context Windows Are Bounded

Three hardware/architectural constraints create the limit:

1. **O(n²) attention complexity** — every token attends to every other; n tokens → n² pairwise relationships. Doubling context quadruples computation. At 10K tokens: 100M comparisons. At 100K tokens: 10B.

2. **KV cache memory growth** — each new generated token appends to the KV cache in GPU VRAM. As the cache fills, inference shifts data from fast SRAM → slow HBM (the memory bandwidth bottleneck). At some point, VRAM is exhausted and inference crawls.

3. **Training distribution** — models are trained on data distributions where shorter sequences dominate. Position encoding (e.g., RoPE) breaks down on sequences longer than what was seen during training without extension techniques.

## Context Rot

More context is not automatically better. As token count grows:
- Accuracy and recall degrade — called **context rot**
- **Lost-in-the-middle effect**: LLMs weight beginning and end of context more heavily (primacy and recency bias); middle content gets underweighted
- Most long-context models show sharp performance drops past ~32K tokens regardless of advertised context size

**Implication**: curating *what* is in context matters as much as *how much* fits. See [[concepts/context-engineering]].

## Current Model Sizes (as of 2026)

| Model | Context Window |
|---|---|
| Gemini 2.5 Pro | 2M tokens |
| Claude Sonnet 4.6 / Opus 4.7 | 1M tokens |
| GPT-4o | 128K tokens |
| Llama 3.1 | 128K tokens |

## Extended Thinking

When extended thinking is enabled, thinking tokens count toward the context window *during generation* but are **automatically stripped** from subsequent turns by the API. You don't pay for thinking tokens in future turns; the effective calculation becomes:
`context_window = input_tokens - previous_thinking_tokens + current_turn_tokens`

**Exception**: during tool use, the thinking block accompanying a tool request **must** be returned with tool results (cryptographic signature verification). The API strips it automatically on the next non-tool turn.

## Context Awareness (Claude Sonnet 4.6+)

Newer Claude models receive an explicit token budget at the start of each conversation:
```
<budget:token_budget>1000000</budget:token_budget>
```
And after each tool call:
```
<system_warning>Token usage: 35000/1000000; 965000 remaining</system_warning>
```
This enables models to self-pace on long-horizon tasks rather than guessing when they'll run out.

## Validation Behavior (Claude Sonnet 3.7+)

Newer models return a **validation error** when prompt + output tokens exceed the window rather than silently truncating. Use the token counting API to pre-check before sending large requests.

## Product vs. API Context Window

The **claude.ai product** (chat, Claude Code) enforces a separate, lower limit than the raw API:
- claude.ai paid plans (Pro, Max, Team): **200K tokens**
- Enterprise (some models): **500K tokens**
- API access (Sonnet/Opus): **1M tokens**

This means the same model has different effective context depending on how you access it. For agent workflows hitting the API directly, the 1M limit applies. For workflows using claude.ai UI or Claude Code, 200K is the ceiling.

See [[summaries/claude-usage-limits]] for the full product-level limit model.

## MCP Server Context Cost

In Claude Code, each enabled MCP server contributes its tool descriptions to the system prompt, consuming tokens from the context window. ECC reports that running too many MCP servers can reduce the effective 200K window to approximately 70K tokens (claimed, unverified — no independent methodology cited).

Practical limits recommended by ECC:
- Keep under 10 MCP servers enabled per project
- Keep under 80 active tools total

Disable unused MCP servers via `/mcp` in Claude Code — these choices persist in `~/.claude.json`, not `settings.json` (which is not a reliable toggle for already-loaded servers).

This is a practical instance of [[concepts/context-engineering]]: curating what's in context includes curating which tools are loaded, not just what content you send.

---

## Six Management Techniques

| Technique | Mechanism | Pros | Cons |
|---|---|---|---|
| Truncation | Cut tokens once limit reached; prioritize must-have content | Simple, low overhead | May cut critical info |
| Model routing | Route large inputs to higher-context models (LiteLLM) | No data loss | Higher cost |
| Memory buffering | Summarize every N messages; preserve key entities | Adaptive, customizable | Short-term only |
| Hierarchical summarization | Chunk → summarize → re-summarize (pyramid) | Scalable, flexible | Cumulative error risk |
| Context compression | Remove redundancy; 40-60% token reduction | Maintains continuity | Quality-dependent |
| RAG | Retrieve only relevant chunks at query time | Scales to large corpora | Retrieval latency, setup complexity |

**Decision guide:**
- Sourced Q&A → RAG
- Multi-session chat → memory buffering
- Long documents (books, legal) → hierarchical summarization
- High token cost → context compression
- Sensitive/regulated content → RAG with exact retrieval (no summarization)

---

## Related Pages

- [[concepts/context-engineering]] — engineering discipline for curating what's in context
- [[concepts/context-degradation]] — five named failure modes when context fills up
- [[concepts/context-compression]] — strategies for compressing context to extend effective window
- [[concepts/agentic-memory-tool]] — API primitives for managing long-running agent context
- [[entities/everything-claude-code]] — ECC's MCP count recommendations and token optimization settings
