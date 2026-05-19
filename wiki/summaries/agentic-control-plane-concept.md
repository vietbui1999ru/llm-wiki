---
title: "Agentic Engineering Control Plane (product concept)"
type: summary
tags: [agent-orchestration, control-plane, multi-agent, workflow, planning]
sources: []
created: 2026-05-19
updated: 2026-05-19
---

# Agentic Engineering Control Plane

Product concept document exploring the scaling gap between single-agent assistance and coordinated multi-agent engineering systems, and a phased roadmap to close it.

## Problem

Current ad hoc agent setups (worktrees + hooks + task dirs) break down as agent count and task complexity grow:

- No unified visibility: agents invisible unless you know the session ID
- No coordination primitive: tasks claimed via filesystem race (POSIX `mv`), which fails across machines
- No quality policy: hooks enforce linting but nothing enforces approval, review, or deliberation
- No governance: no audit trail, no cost accounting, no failure recovery at the system level

## Four-Layer Architecture

```
┌─────────────────────────────────────────┐
│ 4. Experience Layer                     │  Kanban UI, observability, control surface
├─────────────────────────────────────────┤
│ 3. Quality & Governance Layer           │  Councils, CI gates, approval workflows
├─────────────────────────────────────────┤
│ 2. Coordination Layer                   │  Task queues, agent registry, mailboxes
├─────────────────────────────────────────┤
│ 1. Execution Layer                      │  Agent sessions on machines (Claude Code)
└─────────────────────────────────────────┘
```

### Execution Layer
Agent sessions — Claude Code background sessions (`claude --bg`), worktree-isolated, persistent through supervisor. Each agent has an ID, status, and assigned task.

### Coordination Layer
Task state machine: `inbox → claimed → done` (or `failed`). Claim mechanism must be atomic. Single-machine: POSIX `mv`. Multi-machine: git branch creation race on `refs/tasks/*` branches — atomic without shared filesystem.

Agent registry: persistent record of who is running, on what machine, assigned to what task. Current gap: `claude agents` TUI shows running sessions but no durable file.

### Quality & Governance Layer
Three primitives:
1. **CI gates** — linting, typecheck, tests (already have via hooks)
2. **Council deliberation** — multi-model parallel evaluation + synthesis (already have `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
3. **Human approval gateway** — missing; blocks auto-commit until explicit approval

### Experience Layer
Kanban board showing task states, agent assignments, and completion. Currently: directory listing. Target: `/kanban-status` skill rendering a board view.

Observability: centralized append-only event log (`.agents/events.jsonl`). Currently: session output only.

## Phase Roadmap

| Phase | Name | Key Additions | Status |
|---|---|---|---|
| 0 | Validation | Manual worktrees + hooks + `.agents/` dirs | **Current** |
| 0.5 | Instrumentation | Registry, event log, kanban skill, approval workflow | Next |
| 1 | MVP | Structured task model, human approval gateway, Kanban v1, observability v1 | — |
| 2 | Multi-machine | Git-based inbox (`refs/tasks/*`), no shared FS | — |
| 3 | Multi-provider councils | 3-stage deliberation, council aggregation logic | — |
| 4 | Governance | Policies, audit trail, cost controls, failure recovery | — |
| 5 | Ecosystem | Shared agent pools, community registries | — |

## Phase 0.5 — Immediate Additions

Five concrete additions to current setup without architectural changes:

1. **`/kanban-status` skill** — reads `.agents/inbox/`, `claimed/`, `done/` and renders board view
2. **`.agents/registry.json`** — persistent agent registry: id, machine, task, status, started_at
3. **`.agents/events.jsonl`** — append-only event log: claim, start, complete, fail events
4. **Approval workflow skill** — human gate before any agent auto-commit; blocks until approved
5. **Stop hook quality summary** — at session end, hook emits summary (files changed, tests run, status)

## Buy vs Build Decisions

Do not build:
- Code review engine → CodeRabbit or PR-Agent
- Kanban UI → GitHub Projects or Linear
- Evals framework → Braintrust or PromptFoo
- Observability backend → Langfuse or Helicone
- Workflow orchestration → LangGraph or Temporal (if needed)

Build:
- Thin glue layer connecting agent hooks to event log
- Agentic approval decision logic
- Council aggregation (parallel Haiku evaluators + majority vote)
- Cost routing (model tier selection per task complexity)

## Connections

- Current coordination primitive: [[concepts/shared-task-queue]]
- Filesystem isolation for agents: [[concepts/worktree-isolation]]
- Quality deliberation layer: [[concepts/council-pattern]]
- Quality gate hooks: [[concepts/rules-vs-hooks]]
- Agent visibility: `claude agents` TUI (v2.1.144+)
- Expansion plan with gap analysis: [[syntheses/control-plane-expansion-plan]]
