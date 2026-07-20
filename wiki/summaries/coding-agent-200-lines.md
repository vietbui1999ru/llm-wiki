---
title: "The Emperor Has No Clothes: Coding Agent in 200 Lines (Mihai Eric)"
type: summary
tags: [agent-engineering, coding-agent, tool-use, prompt-protocol, python, tutorial, minimal-agent]
sources: ["The Emperor Has No Clothes How to Code Claude Code in 200 Lines of Code.md"]
created: 2026-07-20
updated: 2026-07-20
---

# The Emperor Has No Clothes: Coding Agent in 200 Lines (Mihai Eric)

Mihai Eric builds a functional coding agent from scratch in ~200 lines of Python to show the core of tools like Claude Code "isn't magic." Companion to his Stanford-based *modern AI software engineering* course. Same thesis as Thorsten Ball's Go version ([[summaries/how-to-build-an-agent]]) — the difference is the **tool-call protocol**.

## The mental model

A coding agent is "a conversation with a powerful LLM that has a toolbox":

1. You send a message.
2. The LLM decides it needs a tool → responds with a tool call.
3. Your program executes the call locally.
4. The result is sent back to the LLM.
5. The LLM continues or responds.

"The LLM never actually touches your filesystem. It just *asks* for things to happen, and your code makes them happen."

## Key difference: prompt-based, text-parsed tool protocol

Unlike Ball (who uses the Anthropic SDK's **native** tool-use API with structured `tool_use` blocks and JSON-schema defs), Eric implements the "wink" **by hand**:

- The system prompt lists tools and instructs: *"reply with exactly one line in the format `tool: TOOL_NAME({JSON_ARGS})` and nothing else."*
- Tool defs are generated dynamically from Python **function signatures + docstrings** (`inspect.signature`, `tool.__doc__`) — so docstrings *are* the tool descriptions the model reasons over.
- `extract_tool_invocations` string-parses assistant text: split on `tool:`, take the name and the parenthesized single-line JSON, `json.loads` the args.
- Tool results are fed back as a fake user message: `tool_result({...})`.

This makes visible what the native API abstracts — Ball's point that tool use is "all just strings" is Eric's actual implementation.

## The three tools

Same trio as Ball: `read_file`, `list_files`, `edit_file` (empty `old_str` ⇒ create/overwrite; else find-and-replace **first** occurrence). Eric notes production agents add `grep`, `bash`, `websearch`, but three tools suffice for "incredible things."

## The loop

- **Outer loop**: get user input, append to conversation.
- **Inner loop**: call LLM → parse tool calls. No tools ⇒ print, break. Tools ⇒ execute each, append `tool_result(...)`, loop again. Inner loop runs until the model replies with no tool call — this is what lets it chain read→edit→confirm.

Model used: `claude-sonnet-4-20250514`.

## Contradiction to flag

The prose says "I'm using OpenAI here, but this works with any LLM provider," yet the code imports `anthropic`, constructs `anthropic.Anthropic(...)`, and calls `claude_client.messages.create(...)` with a Claude model. The **code is Anthropic-only as written**; the OpenAI claim is aspirational/portable, not what runs. (Source inconsistency — noted per wiki epistemic rules.)

## Connections

- Go twin using the native tool API: [[summaries/how-to-build-an-agent]].
- Prompt-parsed vs native-API tool protocols is the central axis of [[syntheses/minimal-coding-agent]].
- Inner loop = the harness core in [[concepts/agent-harness]]; docstring-as-tool-description is [[concepts/tool-design-for-agents]].
