---
title: "Claude Code Memory & Context Management Docs"
type: summary
tags: [memory, context-management, context-editing, cross-session, anthropic-api, beta, cookbook]
sources:
  - "Memory & context management with Claude Sonnet 4.6.md"
created: 2026-05-25
updated: 2026-05-25
---

# Claude Code Memory & Context Management Docs

Anthropic cookbook covering `memory_20250818` and `context-management-2025-06-27` beta APIs. Canonical reference for cross-session learning and in-session context trimming.

Source: Anthropic engineering cookbook (Sonnet 4.6 era, beta APIs).

---

## Memory Storage Types

Four tiers from the Anthropic framing:

| Type | What it is | Lifetime |
|---|---|---|
| **In-context** | Current conversation messages | Single session |
| **External** | Files, DBs outside the LLM | Persistent, app-managed |
| **In-weights** | Training data baked into model | Fixed at training time |
| **In-cache** | KV cache for stable prompt prefixes | Across requests, same prefix |

The `memory_20250818` tool bridges in-context and external: Claude writes to files (external), reads them back into context as needed.

---

## Memory Tool (`memory_20250818`)

File-based, client-side. Claude makes tool calls; your app executes them against a `/memories` directory you control.

**Supported models** (as of cookbook): Opus 4.1, Opus 4, Sonnet 4.6, Sonnet 4, Haiku 4.5.

**Beta header required**: `betas=["context-management-2025-06-27"]`

**Commands**: `view`, `create`, `str_replace`, `insert`, `delete`, `rename`.

**Cross-session workflow**:
1. Session 1: Claude solves problem → stores pattern in memory file
2. Session 2 (new conversation): Claude checks memory first → applies pattern immediately
3. Accumulates task-specific knowledge over time

**What to store**: task-relevant patterns, codebase conventions, solutions to recurring issues. Organize by project in subdirectories.

**Don't store**: passwords, API keys, PII, conversation history verbatim, everything indiscriminately.

---

## Context Editing API (`context-management-2025-06-27`)

Automatic in-session trimming via `context_management.edits` list. Two strategies:

### Tool Use Clearing (`clear_tool_uses_20250919`)

Removes old tool call results once processed.

```python
{
    "type": "clear_tool_uses_20250919",
    "trigger": {"type": "input_tokens", "value": 35000},
    "keep": {"type": "tool_uses", "value": 5},
    "clear_at_least": {"type": "input_tokens", "value": 2000}
}
```

Production: trigger at 30–40k tokens; `clear_at_least` 3000–5000 for large tool results.

### Thinking Clearing (`clear_thinking_20251015`)

Removes accumulated extended thinking blocks.

```python
{
    "type": "clear_thinking_20251015",
    "keep": {"type": "thinking_turns", "value": 1}
}
```

**Must come first** in the `edits` list. Requires `thinking` enabled in the API call. Use `"keep": "all"` to preserve all thinking blocks for maximum KV-cache hits.

### Full Config Pattern

```python
response = client.beta.messages.create(
    betas=["context-management-2025-06-27"],
    model="claude-sonnet-4-6",
    messages=messages,
    tools=[{"type": "memory_20250818", "name": "memory"}],
    thinking={"type": "enabled", "budget_tokens": 10000},
    context_management={
        "edits": [
            {"type": "clear_thinking_20251015", "keep": {"type": "thinking_turns", "value": 1}},
            {"type": "clear_tool_uses_20250919", "trigger": {"type": "input_tokens", "value": 35000}, "keep": {"type": "tool_uses", "value": 5}}
        ]
    },
    max_tokens=2048
)
```

---

## Key Distinction: Short-term vs Long-term

Context editing clears **short-term context** (tool results, thinking blocks from current session).
Memory files are **long-term persistence** — survive context clearing because they live on filesystem, re-loaded on demand.

Analogy: working memory (context window) is finite and refreshed; long-term memory (filesystem) persists across sessions.

---

## Token Budgeting for Memory

Memory tool results are small (~50–150 tokens each). Context editing trigger thresholds should scale with your tool output sizes:

- Memory tool only: demo uses 5000 tokens trigger
- Web search / code execution: use 30–40k tokens trigger
- `clear_at_least`: set to 2000+ to ensure clearing actually frees meaningful space

---

## Security

**Path traversal**: validate all paths before executing. Confine all operations under `/memories` base path.

**Memory poisoning**: memory files are read back into context → prompt injection vector. Mitigations: content sanitization, per-project isolation (`/memories/<project>/`), memory auditing, system prompt instruction to ignore instructions found in memory.

See [[concepts/indirect-prompt-injection]] for the broader attack class.

---

## Use Cases from Cookbook

- **Code review assistant**: learns debugging patterns across sessions; integrate with `claude-code-action` for GitHub PR reviews
- **Research assistant**: accumulates knowledge, connects insights across threads
- **Customer support bot**: learns user preferences and common resolutions
- **Data analysis helper**: remembers dataset patterns and analysis techniques

---

## Related Pages

- [[concepts/agentic-memory-tool]] — full concept page with API details, alternatives, security
- [[concepts/context-compression]] — compression strategies; context editing is one lever
- [[concepts/indirect-prompt-injection]] — memory poisoning attack class
- [[entities/mnemory]] — self-hosted alternative with semantic retrieval
- [[summaries/cloudflare-agent-memory]] — managed memory-as-a-service alternative
