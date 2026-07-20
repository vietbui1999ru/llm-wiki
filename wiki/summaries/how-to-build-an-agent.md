---
title: "How to Build an Agent (Thorsten Ball / Amp)"
type: summary
tags: [agent-engineering, coding-agent, tool-use, anthropic-sdk, go, tutorial, minimal-agent]
sources: ["How to Build an Agent.md"]
created: 2026-07-20
updated: 2026-07-20
---

# How to Build an Agent (Thorsten Ball / Amp)

Thorsten Ball (Amp, ampcode.com) demystifies the code-editing agent: it is "an LLM, a loop, and enough tokens." A fully functioning code-editing agent fits in under ~400 lines of Go (the meaningful core is ~300, mostly boilerplate). Everything that makes a production agent like Amp addictive is "elbow grease" — practical engineering on top of this same inner loop, not a moment of genius.

**Definition of agent** (Ball's): an LLM with *access to tools* — the ability to modify something outside the context window.

## The build, in four moves

1. **Chat loop (~90 lines).** Read stdin → append to `conversation` slice → `client.Messages.New(...)` → append reply → print. The Anthropic server is **stateless**: it only sees what's in `conversation`, which you resend in full every turn. This is "every AI chat app you've ever used, except in the terminal."
2. **Tools = wink protocol.** Ball's mental model: "in the following conversation, wink if you want me to raise my arm." You tell the model what tools exist; when it wants one it says so; you execute it and reply with the result. He demonstrates this *with zero code changes* — instructing Claude to emit `get_weather(<location>)` in plain prose, then manually feeding back a result. The native SDK tool API is "just abstraction on top of" this.
3. **Tool definitions.** Each tool = name + description + JSON-schema input + a Go function. Sent via `anthropic.ToolUnionParam`; Anthropic wraps them in a tool-use system prompt server-side. The model then returns `content.Type == "tool_use"` blocks.
4. **Execute loop.** In `Run()`, iterate `message.Content`: on `text` print it, on `tool_use` call `executeTool` (look up by name in the local registry, unmarshal input, run, return `NewToolResultBlock`). If any tool ran, don't read new user input — resend the tool results and let the model continue. Repeat until the model stops requesting tools.

## The three tools

- **`read_file`** — read a relative path.
- **`list_files`** — walk a directory; directories marked with a trailing `/`. Ball stresses there is **no fixed result format** — JSON list, Markdown, prefixed strings all work; pick whatever the model makes sense of, balancing tokens and speed. Format is an experimental choice, not a spec.
- **`edit_file`** — **string replacement**: replace `old_str` with `new_str`; empty `old_str` + missing file ⇒ create the file. Ball notes Claude 3.7 "loves replacing strings" — you discover model preferences by experimentation.

Model used: `ModelClaude3_7SonnetLatest`.

## What's striking

Given only the tools, the model *chains* them unprompted: asked "solve the riddle in secret-file.txt," it reads the file on its own; asked about Go files, it lists then reads `go.mod` and `main.go`; it edits FizzBuzz and *also* updates the stale comment. No "if a user mentions a file, read it" instruction was given. The tool description + the model's training to use tools is enough.

## Connections

- Concrete instantiation of the inner loop described abstractly in [[concepts/agent-harness]] (Agent = Model + Harness; here the harness is ~300 lines of Go).
- Tool-description-as-interface matches [[concepts/tool-design-for-agents]] — the description is the model's only instruction on when/how to use the tool.
- Python twin, same three tools but a **prompt-parsed** protocol instead of the native tool API: [[summaries/coding-agent-200-lines]].
- Cross-source thesis distilled in [[syntheses/minimal-coding-agent]].
