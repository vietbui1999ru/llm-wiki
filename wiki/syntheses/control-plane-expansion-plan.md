---
title: "Control Plane Expansion Plan — Gap Analysis and Phase 0.5 Roadmap"
type: synthesis
tags: [agent-orchestration, control-plane, multi-agent, planning, gap-analysis]
sources: []
created: 2026-05-19
updated: 2026-05-19
---

# Control Plane Expansion Plan

Synthesizes gap analysis, tool landscape research, and concrete Phase 0.5 implementation steps for expanding the current agent setup toward a full Agentic Engineering Control Plane.

Source concept: [[summaries/agentic-control-plane-concept]]

## Current Setup Inventory

What already exists:

| Component | How Implemented |
|---|---|
| Execution | `claude --bg`, `claude agents` TUI (v2.1.144+) |
| Task state machine | `.agents/inbox/`, `claimed/`, `done/` dirs |
| Task model | YAML frontmatter in `.agents/*.md` files |
| Atomic claim (single-machine) | POSIX `mv` from inbox → claimed |
| Quality gate | Hooks: biome, lint-autofix, pre-commit |
| Context compression | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` |
| Council primitive | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Agent isolation | `isolation: "worktree"` on Agent tool |

## Phase 1 Gap Analysis

| Requirement | Coverage | Gap |
|---|---|---|
| Kanban v1 | Partial — dirs exist | No board view / status skill |
| Task schema | YES — YAML frontmatter | No validation layer |
| Agent registry v1 | Partial — TUI shows sessions | No persistent `.agents/registry.json` |
| Single-provider quality gate | YES — hooks | No approval UI or policy file |
| Human approval v1 | **Missing** | Entire workflow absent |
| Observability v1 | Partial — session output only | No centralized append-only log |
| Multi-machine coordination | **Missing** | POSIX `mv` fails across machines |
| Council quality gate | Partial — AGENT_TEAMS env set | No council evaluator agents wired |

Gaps cluster into two areas:
- **Visibility**: kanban board, registry, event log
- **Control**: approval workflow, council quality gate

## Tool Landscape — Buy vs Build

### Buy

| Need | Tool | Rationale |
|---|---|---|
| Code review | CodeRabbit | 2M+ repos, PR comments out of box, not worth building |
| Eval framework | PromptFoo or Braintrust | CLI-first gates (PromptFoo) vs production dashboards (Braintrust) |
| Observability | Langfuse | Open source, self-hostable, LLM-aware trace model |
| Kanban UI | GitHub Projects | Free, already integrated with repo, no infra |
| Workflow orchestration | LangGraph (if needed) | Production v1.0, battle-tested; only needed at Phase 2+ |

### Build

| Component | Why build |
|---|---|
| `/kanban-status` skill | Trivial board renderer — 1 skill file |
| Agent registry + event log | JSON files — nothing to install |
| Approval workflow skill | Agentic decision logic — domain-specific |
| Council aggregation | Glue between parallel evaluators + majority vote |
| Model tier routing | Already partially in model-routing.md rules |

## Phase 0.5 — Implementation Steps

### Step 1: Event Log

Create `.agents/events.jsonl` — append-only, one JSON object per line:

```json
{"ts": "2026-05-19T10:00:00Z", "event": "task_claimed", "task": "TASK-001", "agent": "session-abc"}
{"ts": "2026-05-19T10:45:00Z", "event": "task_complete", "task": "TASK-001", "result": "pass"}
```

Wire to Stop hook: emit `session_end` event with files changed, exit status.

### Step 2: Agent Registry

Create `.agents/registry.json`:

```json
{
  "agents": [
    {"id": "session-abc", "task": "TASK-001", "status": "running", "started_at": "...", "machine": "hostname"}
  ]
}
```

Orchestrator writes on spawn; Stop hook writes on completion.

### Step 3: `/kanban-status` Skill

Skill reads `.agents/inbox/`, `claimed/`, `done/`, `registry.json` and renders:

```
INBOX          CLAIMED        DONE
────────────   ────────────   ────────────
TASK-003       TASK-001 @abc  TASK-002 ✓
TASK-004       TASK-005 @def
```

### Step 4: Approval Workflow Skill

Invoked before any agent auto-commit. Renders diff, blocks on stdin approval:

```
Agent: session-abc
Task: TASK-001
Files: src/auth/middleware.ts (+42 -8)
Approve? [y/n/diff]:
```

On approval: writes approval token to `.agents/approvals/<task>.approved`. Agent's commit hook checks for token before proceeding.

### Step 5: Stop Hook Quality Summary

Append to Stop hook: emit structured summary to stdout and to `.agents/events.jsonl`:

```
Session: session-abc | Task: TASK-001
Files changed: 3 | Tests run: 47 passed, 0 failed
Status: COMPLETE
```

## Phase 2 Preview — Multi-Machine Coordination

POSIX `mv` for atomic claim only works on single machine (same filesystem).

Multi-machine atomic claim: **git branch creation race on `refs/tasks/*`**:

```bash
git push origin HEAD:refs/tasks/TASK-001  # succeeds for first claimer
# fails for others: "remote: error: cannot lock ref"
```

This is atomic across machines without a shared filesystem. No external coordination service needed.

Task inbox becomes git branch per task. Orchestrator pulls `refs/tasks/*`, picks unclaimed (no corresponding `refs/tasks-claimed/*`), races to claim.

## Phase 3 Preview — Council Quality Gate

Already have: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` as council engine primitive.

Pattern: spawn 3 Haiku evaluators in parallel (acceptance criteria, code quality, style), collect PASS/FAIL + reasoning, majority vote, write signal file.

See [[concepts/council-pattern]] for full 3-stage structure and cost model (~15K tokens vs ~1K single-model).

## Critical Path

Phase 0 → 0.5: **5 concrete deliverables, no new infra** — all implemented as SKILL.md files and JSON files.

Phase 0.5 → 1: Buy Langfuse + GitHub Projects. Build approval UI. Schema validation layer.

Phase 1 → 2: Git-based inbox migration. Multi-machine agent orchestrator.

Phase 2 → 3: Wire council evaluators into Stop hook quality check.

## Related Pages

- [[summaries/agentic-control-plane-concept]] — source product document
- [[concepts/shared-task-queue]] — current coordination primitive
- [[concepts/worktree-isolation]] — agent filesystem isolation
- [[concepts/council-pattern]] — quality deliberation layer
- [[concepts/agent-teams]] — team coordination mechanics
- [[concepts/rules-vs-hooks]] — static rules vs dynamic hook injection
- [[concepts/agentic-cicd]] — CI as external watchdog pattern
