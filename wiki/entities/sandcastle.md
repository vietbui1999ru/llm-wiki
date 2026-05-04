---
title: "SandCastle"
type: entity
tags: [orchestration, parallelization, worktrees, agent-harness, typescript]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# SandCastle

TypeScript library by Matt Pocock for running Claude Code agents in parallel across isolated git worktrees and sandboxed containers. The production-grade implementation of the AFK parallelization pattern described in [[summaries/mattpocockworkflow]].

GitHub: https://github.com/mattpocock/sandcastle

---

## What It Does

SandCastle manages the full parallel agent loop:

```
Planner agent
  → reads all open issue files
  → selects batch of parallelizable tasks (respects DAG blocking)

For each selected task:
  → create isolated git worktree
  → sandbox in Docker/Podman/Vercel environment
  → run implementation agent with issue context (fresh context window)

For each completed worktree:
  → run reviewer agent (Opus, pushed coding standards)

Merger agent
  → merges passing branches
  → resolves type/test conflicts
  → closes completed issues
```

---

## Branch Strategy Taxonomy

SandCastle formalizes three deployment strategies as first-class parameters:

| Strategy | Description | When to use |
|---|---|---|
| `head` | Each agent works directly off main HEAD | Fast, risky — works when tasks are truly non-overlapping |
| `merge-to-head` | Agent branches, auto-merges back to head when passing | Default for parallel work; handles light conflicts |
| `branch` | Agent produces a branch, human reviews and merges | For changes needing human judgment before integration |

This is the first tool to formalize branch strategy as a parameter rather than a convention. Compare to [[concepts/branch-strategy-for-agents]].

---

## Provider Abstraction

Supports Docker, Podman, and Vercel sandbox environments. Designed so implementation agents run in container isolation without hitting the Anthropic ToS constraint that blocks Claude Code subscription keys in containers.

Pocock's workaround: run Claude Code on the host (subscription key), have SandCastle manage the worktree isolation. The containers are for tool execution, not the Claude process itself.

Contrast with [[entities/dangeresque]], which takes the host-native approach entirely.

---

## IterationUsage Telemetry

Each iteration reports token usage:

```typescript
interface IterationUsage {
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens: number;
  cacheWriteTokens: number;
}
```

Enables per-task cost tracking — useful for calibrating which task types justify parallel AFK runs vs. sequential HITL.

---

## Relation to Existing Wiki

- [[summaries/mattpocockworkflow]] — SandCastle implements the AFK parallel pattern described there
- [[entities/dangeresque]] — host-native alternative; simpler setup, no container dependency
- [[concepts/agent-harness]] — SandCastle is a harness implementation
- [[concepts/ralph-loop]] — same loop pattern, different implementation
- [[concepts/branch-strategy-for-agents]] — branch strategy as a parameter
- [[concepts/verification-pipeline]] — reviewer agent = verification gate
