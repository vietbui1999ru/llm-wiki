---
title: "Builder.io Agent-Native"
type: summary
tags: [agent-native, agentic-apps, ui, actions, mcp, a2a]
sources: ["BuilderIOagent-native A framework for building agent-native applications..md"]
created: 2026-06-17
updated: 2026-06-17
---

# Builder.io Agent-Native

Builder.io's Agent-Native framework argues that agentic products should not choose between a rich UI and an autonomous agent. The central primitive is a shared action surface: one action powers UI clicks, agent tools, HTTP, MCP, A2A, and CLI calls.

## Core claim

The agent and UI should be equal citizens of the same application state:

- Shared SQL-backed state: UI changes and agent changes sync both ways.
- Context-aware agent operations: selection, current screen, and workspace state are part of the agent context.
- Multiplayer collaboration: humans and agents edit the same document with CRDT-style merging and live presence.
- Per-user workspace: skills, memory, instructions, subagents, and MCP servers are customized per user but stored in product infrastructure.
- Multi-surface deployment: the same agent can be shipped as headless API, rich chat, or full application.

## Architecture pattern

Agent-Native treats protocol surfaces as adapters over the same domain action:

```ts
defineAction({
  schema,
  run: async (input) => { /* domain mutation */ },
})
```

That action can then be invoked from UI, agent runtime, HTTP, MCP, A2A, or CLI. This is a product-level version of the [[concepts/deep-modules]] pattern: narrow shared interface, many execution surfaces.

## Product shapes

| Shape | Use case |
|---|---|
| Headless | API, CLI, MCP, A2A, or code-driven automation |
| Rich chat | Chat with native tables, charts, approvals, setup flows, and rendered tool results |
| Whole app | Full SaaS UI where chat is one interaction mode over synchronized app state |

## Wiki connections

- [[entities/agent-native]] — entity page for the framework.
- [[concepts/agent-harness]] — Agent-Native is a product harness: actions, state, identity, jobs, observability, skills, and UI surfaces.
- [[concepts/agent-context-instructions]] — per-user skills/instructions become product state instead of local files only.
- [[concepts/tool-design-for-agents]] — shared action schemas are tool contracts for both humans and agents.
