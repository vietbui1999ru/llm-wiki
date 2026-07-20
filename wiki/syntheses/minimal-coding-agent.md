---
title: "The Minimal Coding Agent: LLM + Loop + Tools"
type: synthesis
tags: [agent-engineering, coding-agent, tool-use, agent-loop, synthesis, minimal-agent]
sources:
  - "How to Build an Agent.md"
  - "The Emperor Has No Clothes How to Code Claude Code in 200 Lines of Code.md"
created: 2026-07-20
updated: 2026-07-20
---

# The Minimal Coding Agent: LLM + Loop + Tools

Two 2026 "build a coding agent from scratch" walkthroughs — Thorsten Ball's Go version ([[summaries/how-to-build-an-agent]], ~300 lines, Amp) and Mihai Eric's Python version ([[summaries/coding-agent-200-lines]], ~200 lines) — arrive at the same claim from opposite ends: a code-editing agent has **no secret**. It is an LLM, a loop, and enough tokens, plus three file tools. Everything a production agent (Claude Code, Amp) adds on top is engineering, not magic.

## The invariant core

Both implementations share an identical skeleton, independent of language and SDK:

1. **Stateless server, client-owned conversation.** The model provider sees only the message list you resend every turn. Conversation memory is the harness's job, not the model's.
2. **The agentic loop.** Outer loop reads user input; inner loop calls the model, and *keeps calling* as long as the model requests tools — feeding each tool result back — until the model answers with no tool call. The inner loop is what lets one user turn chain read → edit → verify.
3. **Three tools are enough.** `read_file`, `list_files`, `edit_file`. Editing is **string replacement** (`old_str` → `new_str`; empty `old_str` = create file), not diffs or ASTs. Both authors note production agents add `bash`, `grep`, `websearch`, approval gates — but the loop is unchanged.
4. **Tool description is the whole interface.** The model decides *when* to use a tool entirely from its name + description (Ball) or docstring (Eric). Neither author writes routing logic like "if the user mentions a file, read it." The model chains tools unprompted. See [[concepts/tool-design-for-agents]].

This is the concrete, minimal instantiation of Agent = Model + Harness from [[concepts/agent-harness]]: here the harness is a few hundred lines.

## The one axis that differs: tool-call protocol

| | Ball (Go / Amp) | Eric (Python) |
|---|---|---|
| Protocol | **Native** SDK tool-use API | **Prompt-based**, text-parsed |
| Model signals tool | structured `tool_use` content block | a line `tool: NAME({json})` in its text |
| Tool defs | `ToolUnionParam` + JSON schema, sent via API | function signature + docstring, injected into system prompt |
| Parsing | SDK gives typed blocks | hand-rolled `str.split` + `json.loads` |
| Result return | `NewToolResultBlock(id, ...)` | fake user message `tool_result(...)` |
| Model | Claude 3.7 Sonnet | Claude Sonnet 4 |

These are the **two layers of one idea**, not rival designs. Ball says the native tool API is "just abstraction on top of" telling the model to "wink" — and Eric's code *is* that raw wink protocol made explicit. Reading them together shows exactly what the provider's tool API does for you server-side.

**Trade-off.** Native API: structured, validated, provider-optimized, less brittle parsing — but provider-coupled. Prompt-parsed: fully portable and transparent (any text-completion model), pedagogically clearer — but brittle (depends on the model emitting the exact format; no schema validation; ad-hoc error handling). For anything real, prefer the native API; the prompt-parsed version is the better *teaching* artifact for seeing the mechanism.

## Why it matters

The shared punchline — Ball's "that's *it*," Eric's "the emperor has no clothes" — is a useful corrective against over-mystifying agents. The leverage in a production coding agent is not the loop (a weekend's work) but the surrounding elbow grease: context management, UX/streaming, tool breadth, error recovery, approval workflows, system-prompt tuning. Knowing the core is trivial reframes where engineering effort actually goes.

## See also

- [[concepts/agent-harness]] — the general Model + Harness framing this instantiates.
- [[concepts/tool-design-for-agents]] — description-as-interface, error-message-as-recovery-instruction.
- [[summaries/pi-building-in-world-of-slop]] — a related minimal-harness / 4-tool thesis from the Pi project.
