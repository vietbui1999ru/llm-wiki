---
title: "Agent-Native"
type: entity
tags: [agent-native, builderio, agentic-apps, mcp, a2a, ui]
sources: ["BuilderIOagent-native A framework for building agent-native applications..md"]
created: 2026-06-17
updated: 2026-06-17
---

# Agent-Native

Agent-Native is Builder.io's open-source framework for building applications where agents and rich UIs operate over the same state and action model.

## Positioning

The framework targets a gap between SaaS apps with rigid UIs and raw AI agents with no product surface. It offers cloneable product templates where the app owns the code, the agent can act inside the app, and the user can still use a conventional UI.

## Core primitives

- **Actions** — one schema-backed operation powers UI, agent, HTTP, MCP, A2A, and CLI.
- **Agent runtime** — chat, tools, skills, memory, jobs, observability, and handoffs.
- **SQL-backed state** — app state and agent state synchronize through normal product infrastructure.
- **Agent surfaces** — headless, rich chat, or whole app over the same primitives.
- **External agent compatibility** — Claude, ChatGPT, Codex, Cursor, OpenCode, GitHub Copilot / VS Code, and other MCP hosts can connect to hosted apps.

## Why it matters

Agent-Native makes the "agent as product peer" pattern explicit. Rather than bolting chat onto a SaaS app, it treats every meaningful product action as both human-operable and agent-operable.

## Related

- [[summaries/builderio-agent-native]] — source summary.
- [[concepts/agent-harness]] — broader harness architecture.
- [[concepts/tool-design-for-agents]] — action schemas as agent tool contracts.
- [[concepts/agent-context-instructions]] — per-user instructions and skills as product state.
