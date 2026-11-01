---
title: "Build Your Own AI Coding Agent Harness (Vercel Academy)"
type: summary
tags: [agent-harness, tool-design, sandbox, context-management, subagents, course]
sources: ["Build Your Own AI Coding Agent Harness.md"]
created: 2026-11-01
updated: 2026-11-01
---

# Build Your Own AI Coding Agent Harness (Vercel Academy)

Course landing page by Joel Hooks on Vercel Academy. Only the syllabus page was captured, not the 38 lessons, so this summary records the course's structure and claims, not the lesson content. The course builds `TeensyCode`, a small TypeScript coding-agent harness on the AI SDK (`ToolLoopAgent`, `pruneMessages`), AI Gateway, Vercel Sandbox, `just-bash` (an in-memory virtual filesystem with simulated bash) and Vercel Workflow.

## Framing: each harness piece answers a failure

The course's thesis is that "a tool loop with three tools is a demo." Each step exists because the previous one broke something:

| Failure of the bare loop | Harness piece that answers it |
|---|---|
| A 5,000-line file read stays in context forever | Pruning old tool results, bounded tool output, cache control |
| `bash` can run `rm -rf` | Execute-level gates: safe-command allowlist, then configurable approval |
| Asked to refactor, the agent explains how to refactor | System prompt with Agency and Guardrails sections ("act, don't explain") |
| One long task fills the window and the agent loses its instructions | Context management plus subagent delegation |
| Cloud sandbox costs money per minute and loses work on timeout | Sandbox lifecycle: state machine, snapshot/restore, durable workflows |

This causal ordering is the same argument [[summaries/state-of-harness-engineering-2026]] makes as a best practice: build each harness piece in reaction to an observed failure.

## Module map (11 modules plus capstone)

1. **Agent loop**: zero tools (a chatbot) to `read` and `grep` (an agent) to gated `bash`.
2. **Tool design**: descriptions become a five-section contract (WHEN TO USE, WHEN NOT TO USE, DO NOT USE FOR, EXAMPLES); a factory separates the tool contract from execution; approval evolves from boolean to function to discriminated union.
3. **System prompt**: Agency, Guardrails and Handling Ambiguity sections; `buildSystemPrompt()` adapts to runtime; a verification-gate contract (typecheck, lint, test, build); `AGENTS.md` injection per project.
4. **Sandbox abstraction**: one `Sandbox` interface (`readFile`, `exec`, `stop`) with local, in-memory (copy-on-write) and cloud implementations. Tools call `sandbox.exec()`, never `child_process.exec()`. Lifecycle hooks `afterStart`, `beforeStop`, `onTimeout`.
5. **Context management**: token logging shows linear growth; fixes are `pruneMessages`, "prevention over cleanup" via caps on every tool's output, and provider cache-control headers.
6. **Subagent delegation**: the parent plans, subagents execute. An *explorer* is read-only on a cheap model; an *executor* has full tools on a stronger model; a `task` tool routes with per-role permissions and model.
7. **Sandbox lifecycle** (concept only): state transitions, timeouts, snapshot/restore idempotency hazards, durable workflows with `sleep()`.
8. **Human in the loop**: `askUser` with multiple-choice options and an ambiguity protocol: search first, then ask, then act.
9. **Planning and verification**: a todo tool; "grep first, read only what you'll change"; a verification contract with scoped claims.
10. **Surfaces**: the agent is headless; CLI, TUI and web are renderers.
11. **Extensibility**: event bus ("events, not inheritance"), skills as progressive disclosure (names in the prompt, content on demand), custom tool registration, lifecycle events that can subscribe, block or modify.

Capstone: run the harness on a real task ("add rate limiting to the auth routes") and fix where context overflows, tools are misselected, or subagents get bad instructions.

## The "80% of tools removed" claim

[[summaries/state-of-harness-engineering-2026]] cites this course for "stripped 80% of the tools out of an agent and watched its success rate go from 80% to 100% on the same model, with tokens more than halved and latency down from 724 seconds to 141." That figure is **not on the captured landing page**; it would be in a lesson. The State of Harness Engineering report itself notes that Vercel's page marks the figure as second-hand and nobody reproduces it. Treat it as *(claimed, unverified)*.

## Wiki connections

- [[concepts/agent-harness]]: the course is a build-along version of the component model (filesystem, bash, sandbox, context management, loop).
- [[concepts/tool-design-for-agents]]: the five-section description contract and bounded output.
- [[concepts/context-engineering]]: pruning, bounded outputs and cache control as the three context levers.
- [[concepts/agent-subagents]]: explorer/executor split with per-role model and tool restriction.
- [[concepts/agentic-sandbox-controls]]: execute-level gates and the sandbox interface.
- [[concepts/agent-skills]]: skills as progressive disclosure.
