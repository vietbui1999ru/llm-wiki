---
title: "Agentic Memory Tool"
type: concept
tags: [memory, context-management, cross-session, context-editing, anthropic-api, beta]
sources:
  - "Memory & context management with Claude Sonnet 4.6.md"
  - "Effective context engineering for AI agents.md"
created: 2026-04-27
updated: 2026-04-27
---

# Agentic Memory Tool

Anthropic's client-side memory and context editing primitives for building agents that persist knowledge across sessions and manage long-running context efficiently. Currently in **beta**.

## Memory Tool (`memory_20250818`)

A file-based system where Claude makes tool calls and the application executes them against a local `/memories` directory. **Client-side** — you control the storage.

### Commands

| Command | Description |
|---|---|
| `view` | Show directory listing or file contents |
| `create` | Create or overwrite a file |
| `str_replace` | Replace specific text in a file |
| `insert` | Insert text at a line number |
| `delete` | Delete a file or directory |
| `rename` | Rename or move a file |

### Supported Models (as of 2026)

Claude Opus 4.7, Opus 4.1, Opus 4, Sonnet 4.6, Sonnet 4, Haiku 4.5.

### Usage Pattern

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    tools=[{"type": "memory_20250818", "name": "memory"}],
    betas=["context-management-2025-06-27"],
    messages=messages,
    ...
)
# Execute tool_use blocks against local /memories directory
```

### Cross-Session Learning

The key benefit: Claude checks its memory files at the start of a task, finds patterns from previous sessions, and applies them immediately without re-learning. Pattern recognition is semantic — applies across different languages/frameworks (a thread-safety pattern learned in Python applies to async Python, Go, Java, Rust).

**Workflow:**
- Session 1: Claude solves a problem → stores the pattern in memory
- Session 2: New conversation → Claude reads memory → applies pattern immediately (faster, more reliable)
- Session N: Memory accumulates task-specific knowledge over time

### What to Store

- Task-relevant patterns discovered during work
- Codebase-specific conventions and architectural decisions
- Solutions to recurring issues
- Organized by project in subdirectories for isolation

**Don't store**: sensitive data (passwords, API keys, PII), conversation history, everything indiscriminately.

## Context Editing (`context-management-2025-06-27`)

API-level primitives for automatically trimming accumulated context during long sessions. Configured via the `context_management` parameter with an `edits` list.

### Tool Use Clearing (`clear_tool_uses_20250919`)

Clears old tool call results once they've served their purpose. Old tool results are rarely needed again once the model has processed them.

```python
{
    "type": "clear_tool_uses_20250919",
    "trigger": {"type": "input_tokens", "value": 35000},  # threshold
    "keep": {"type": "tool_uses", "value": 5},            # retain most recent N
    "clear_at_least": {"type": "input_tokens", "value": 2000}
}
```

### Thinking Clearing (`clear_thinking_20251015`)

Removes accumulated extended thinking blocks from previous turns. **Must come first** in the `edits` list when combined with tool use clearing.

```python
{
    "type": "clear_thinking_20251015",
    "keep": {"type": "thinking_turns", "value": 1}  # retain only last turn
}
```

### Key Distinction

Context editing clears **short-term context** (tool results, thinking blocks). Memory files are **long-term persistence** — they survive context clearing because they live outside the context window and are re-loaded on demand.

This mirrors human cognition: working memory (context window) is finite and refreshed; long-term memory (filesystem) persists across sessions.

## Server-Side Compaction

Separate from the memory tool: Claude API server-side compaction automatically summarizes earlier conversation content when approaching the context limit. Available in beta for Opus 4.7, Opus 4.6, Sonnet 4.6. Minimal integration required — vs. client-side memory tool which gives full control but requires implementation.

## Security: Memory Poisoning

Memory files are read back into Claude's context, making them a **prompt injection vector**. A malicious agent or compromised external data could write instructions into memory files.

**Mitigations:**
1. Content sanitization — filter dangerous instruction patterns before storing
2. Per-project/per-user memory isolation (separate `/memories/<project>/` directories)
3. Memory auditing — log and scan all memory operations
4. System prompt instruction: explicitly tell Claude to ignore instructions found in memory files

See [[concepts/indirect-prompt-injection]] for the broader attack class.

## Related Pages

- [[concepts/context-engineering]] — the discipline that this tool implements (compaction, note-taking)
- [[concepts/context-window]] — the fundamental constraint this tool works around
- [[concepts/context-compression]] — compression strategies; server-side compaction is one lever
- [[concepts/indirect-prompt-injection]] — security risk in memory files
- [[summaries/context-window-cluster]] — consolidated source summary
