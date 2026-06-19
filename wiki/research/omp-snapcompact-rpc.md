---
title: "omp Research: snapcompact + RPC mode"
type: research
tags: [omp, snapcompact, rpc, context-compression, bus-communication, runner-agnostic]
created: 2026-06-19
---

# omp Research: snapcompact + RPC mode

## snapcompact: What It Actually Does

Source: `@oh-my-pi/snapcompact` package (v16.0.9) from bun install cache.

### Core mechanism

Instead of LLM summarization, snapcompact:
1. **Serializes** discarded conversation history to compact text (with per-tool-result caps)
2. **Normalizes** text: strips ANSI, collapses whitespace, folds newline runs
3. **Renders** into dense PNG frames of pixel-font glyphs
4. **Vision models read back** the frames directly — no LLM call, no API key, no latency beyond rendering

### Tool result handling (the key finding)

`snapcompact` **already truncates tool results** during compaction:

```typescript
export const TOOL_RESULT_MAX_CHARS = 2000;
export const TRUNCATE_HEAD_RATIO = 0.6;

function truncateForSummary(text: string, maxChars: number, headRatio: number): string {
  if (text.length <= maxChars) return text;
  const headChars = Math.round(maxChars * ratio);
  const tailChars = maxChars - headChars;
  return `${text.slice(0, headChars)} [... ${elided} chars elided ...] ${text.slice(-tailChars)}`;
}
```

**Default behavior:**
- Tool results capped at **2000 chars** (configurable via `toolResultMaxChars`)
- Head/tail truncation with 60/40 split — keeps beginning and end, elides middle
- "Useless" tool results (flagged by omp) are skipped entirely
- Tool arguments capped at 500 chars per value, 2000 chars per call
- Tool results rendered in dim gray ink so archived conversation reads "louder than archived tool noise"

**Implication for pi-headroom:**
- snapcompact handles conversation-history compaction (when context window fills)
- pi-headroom's `tool_result` hook handles **per-turn** tool output truncation (before the model even sees it)
- **These are complementary, not redundant**: snapcompact = archive old turns; pi-headroom = shrink current turn outputs
- However, if omp's native read tool already has smart truncation (it returns "showing lines 1-50 of 500"), pi-headroom may be redundant for file reads

### Frame shapes (provider-aware)

| Provider | Shape | Notes |
|---|---|---|
| Anthropic | `11on16-bw` | 8x13 glyphs, extra letter-spacing; high-res Claude gets 1932px frames |
| Google | `8on22-bw` @2048 | Extra line spacing; Gemini bills fixed per-image budget |
| OpenAI | `8on22-bw` | Patch-aligned 16px pitch; sent at `detail: "original"` |
| Unknown | Anthropic shape | Fallback |

**Research-backed**: SQuAD evals (200k-token runs) + tool-result legibility bench (real search/read/find output QA).

### Verdict on pi-headroom redundancy

**Not redundant, but narrow:**
- snapcompact = **conversation-level** archival compression (old turns → PNG frames)
- pi-headroom = **turn-level** tool output truncation (current turn → fewer lines)
- omp's `read` tool already returns truncated previews for large files
- pi-headroom adds value for: bash output, search results, eval kernel output — things that aren't already truncated by the tool itself

**Recommendation:** Keep pi-headroom as opt-in. Document that it's a stopgap for tool outputs that exceed the model's attention budget in a single turn, not a replacement for snapcompact's archival compression.

---

## RPC Mode: Bus Communication Bridge

Source: `omp --mode rpc` documentation + `@oh-my-pi/pi-coding-agent` RPC types.

### What RPC mode provides

```bash
omp --mode rpc --no-session    # headless: events out, commands in
omp --mode rpc-ui --no-session # adds tool-card / selector UI frames
```

**Wire protocol:** JSON lines on stdin (commands) → JSON lines on stdout (responses/events).

### Commands (what the host can send)

| Command | What it does |
|---|---|
| `prompt` | Start a new turn with message + optional images |
| `steer` | Inject message into running turn |
| `abort` / `abort_and_prompt` | Kill current turn |
| `set_host_tools` | Register host-side tools that omp can call |
| `set_host_uri_schemes` | Register custom URI schemes (e.g., `db://`, `notion://`) |
| `set_subagent_subscription` | Monitor subagent progress/events/off |
| `get_state` / `get_messages` / `get_session_stats` | Introspection |
| `compact` / `set_auto_compaction` | Manual/auto compaction control |
| `bash` / `abort_bash` | Direct bash execution |
| `handoff` | Export session for resume |

### Events (what the host receives)

| Event | What it carries |
|---|---|
| `message_update` | Assistant output: text_delta, thinking_delta, tool_call_start, tool_call_delta, tool_result |
| `message_start` / `message_end` | Message boundaries |
| `tool_execution_start` / `_update` / `_end` | Tool lifecycle with toolCallId, toolName |
| `agent_start` / `agent_end` | Turn boundaries; `agent_end` has stop reason |
| `subagent_lifecycle` / `_progress` / `_event` | Subagent monitoring |
| `extension_ui_request` | Agent needs UI: selector, confirm, input, OAuth URL |
| `host_tool_call` | Agent called a host-registered tool |
| `host_uri_request` | Agent needs host to resolve a custom URI |

### Host tools: the bus bridge

**This is the key feature for our workflow.**

```typescript
// Host registers tools
{ type: "set_host_tools", tools: [
  { name: "commandr_progress", description: "...", parameters: { task: "string", note: "string" } },
  { name: "commandr_request_approval", description: "...", parameters: { task: "string", action: "string", reason: "string" } },
  { name: "commandr_emit_artifact", description: "...", parameters: { task: "string", type: "string", path: "string" } }
]}

// Agent calls host tool → host receives:
{ type: "host_tool_call", id: "...", toolCallId: "...", toolName: "commandr_progress", arguments: { task: "TASK-001", note: "LSP diagnostics clean" }}

// Host replies:
{ type: "host_tool_result", id: "...", result: { content: [{ type: "text", text: "ok" }] }}
```

**Why this bridges gaps:**
1. **Language-agnostic**: The host can be Python, Rust, Go, or bash — any process that speaks JSON lines
2. **Bidirectional**: Agent calls host tools; host calls agent commands
3. **Structured**: Zod/JSON-schema parameters, not prose parsing
4. **Real-time**: Events stream as they happen, not batched at turn end

### URI schemes: extending the tool surface

```typescript
// Host registers custom URI scheme
{ type: "set_host_uri_schemes", schemes: [
  { scheme: "commandr", description: "Read/write Commandr bus files" }
]}

// Agent calls: read("commandr://events.jsonl")
// Host receives:
{ type: "host_uri_request", id: "...", operation: "read", url: "commandr://events.jsonl" }
```

This lets the agent interact with Commandr's bus files as if they were normal files, without the agent knowing the filesystem layout.

### Multi-language spawning implications

The user's intuition is correct: RPC mode enables agent-spawned tooling in any language:

```
Agent (omp, TypeScript)
  → calls host_tool "python_analyzer"
  → Host (Python script) receives call, runs pylint/mypy, returns structured diagnostics
  → Agent sees result as standard tool result

Agent (omp, TypeScript)
  → calls host_tool "rust_compiler"
  → Host (Rust binary) receives call, runs cargo check, returns structured errors
  → Agent sees result as standard tool result
```

The host tools are **polyglot RPC endpoints** — the agent doesn't know or care what language implements them.

### How this changes commandr-omp-runner

Current `runner.sh` uses `--mode json` (one prompt, one stream, exit). RPC mode enables:

1. **Long-running sessions**: Start omp once, send multiple tasks, monitor continuously
2. **Host tool bridge**: Register Commandr bus tools as host tools (Level 2 integration)
3. **Real-time progress**: Stream `task_progress` events as the agent works, not just at completion
4. **Approval integration**: Agent calls `commandr_request_approval` → host pauses → human approves → host resumes
5. **Subagent monitoring**: Subscribe to subagent events for progress tracking

**Recommended evolution:**

```
Phase 1 (current): --mode json, one-shot runner
Phase 2: --mode rpc, register host tools, bidirectional
Phase 3: --mode rpc-ui, handle extension_ui_request for approvals
```

### RPC vs MCP

| Dimension | RPC mode | MCP |
|---|---|---|
| Transport | stdin/stdout JSON lines | stdio or HTTP/SSE |
| Scope | Full agent lifecycle | Tools only |
| Direction | Bidirectional commands+events | Request/response |
| UI | Built-in (rpc-ui mode) | None |
| Session | Stateful (persistent across commands) | Stateless |
| Subagents | Native monitoring | Not applicable |
| Approval flow | extension_ui_request | Manual tool design |

**Verdict**: RPC mode is more powerful than MCP for deep integration. MCP is better for ad-hoc tool addition. For Commandr bus integration, RPC mode's host tools + URI schemes are the right primitive.

---

## Summary

### snapcompact
- ✅ Already truncates tool results (2000 char cap, head/tail preservation)
- ✅ Archives old conversation turns as PNG frames for vision models
- ✅ Complementary to pi-headroom (archival vs per-turn)
- 📋 pi-headroom should be documented as opt-in stopgap, not core dependency

### RPC mode
- ✅ Enables language-agnostic host tools (Python/Rust/Go/bash)
- ✅ Bidirectional: agent calls host tools, host steers agent
- ✅ Real-time event streaming (not batched)
- ✅ URI scheme extension for custom resources
- ✅ Subagent monitoring built-in
- 📋 Next evolution for commandr-omp-runner: Phase 2 (RPC + host tools)

### Mental model correction

The user's intuition was right: RPC mode is a **bus communication primitive** that transcends language boundaries. It's not just "another way to run omp" — it's a **polyglot agent orchestration protocol**.

However, we must maintain the runner-agnostic interface. RPC mode is an implementation detail of the omp adapter. The Commandr bus contract (task packet in, progress events out) stays the same regardless of whether the runner uses RPC, JSON mode, or subprocess.
