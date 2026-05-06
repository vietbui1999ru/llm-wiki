---
title: "Worktree Isolation"
type: concept
tags: [agent-harness, parallelization, git, orchestration, context-management]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md", "Exit Code 0 Is Not Quality What 198 Autonomous Agents Taught Me About AI Orchestration.md"]
created: 2026-05-05
updated: 2026-05-05
---

# Worktree Isolation

Using separate git worktrees to give each parallel agent its own filesystem checkout. Agents literally cannot touch each other's files. The ToS-compliant, host-native alternative to container-based sandboxing.

---

## What a Git Worktree Is

A git worktree is a second (or third, Nth) checkout of the same repository in a different directory. All worktrees share the same `.git` object store — commits, history, refs — but each has its own working tree and HEAD.

```zsh
# Create worktree on a new branch
git worktree add /tmp/task-auth -b agent/auth-middleware

# Agent works in /tmp/task-auth — isolated from main checkout
# When done:
git worktree remove /tmp/task-auth
git worktree prune  # clean up stale entries
```

One repo, multiple simultaneous checkouts, zero file conflicts between agents.

---

## Why Agents Need It

Without worktree isolation, parallel agents editing the same repo share a working directory. Agent A edits `src/auth.ts`. Agent B, working on a different task, reads `src/auth.ts` and gets A's half-finished state. Both commit. Conflict.

With worktree isolation:
- Each agent has its own filesystem state
- Agents can't observe each other's in-progress edits
- Each agent starts from a known clean commit
- Merge happens after each agent completes — not mid-task

This is also what makes [[concepts/context-compression]] clear-over-compact safe: the agent starts fresh each task, but state is preserved in commits and branch, not in agent memory.

---

## Scope Overlap Detection

The precondition for safe worktree isolation is **non-overlapping file scope** between agents. Before assigning tasks to parallel agents, check that their target directories don't overlap:

```
✓ Agent A: src/auth/           Agent B: src/payments/       — safe
✗ Agent A: src/domains/        Agent B: src/domains/auth/   — overlap: B is inside A's scope
```

Scope overlap causes merge conflicts even with worktree isolation — agents edit different checkouts of the same files, then both try to merge. [[summaries/exit-code-0-quality]] documents scope overlap detection as a required orchestration primitive.

---

## Merge Protocol

**Merge-before-cleanup** rule (from [[summaries/exit-code-0-quality]]): always merge the worktree branch before removing the worktree. Removing first loses any uncommitted or unmerged work.

```zsh
# Correct order
git merge agent/auth-middleware   # merge first
git worktree remove /tmp/task-auth  # then clean up
git branch -d agent/auth-middleware
```

Merge strategy after isolation depends on [[concepts/branch-strategy-for-agents]]:
- `head` — merge directly to current HEAD (low risk, non-overlapping files)
- `merge-to-head` — standard merge (default for parallel work)
- `branch` — open a PR for human review before merging (security changes, shared interfaces)

---

## Relation to ToS and Sandboxing

[[concepts/agentic-sandbox-controls]] recommends OS-level sandboxing (containers, Bubblewrap) per the NVIDIA AI Red Team guidance. But Anthropic's ToS restricts Claude Code subscription keys inside Docker containers.

Worktree isolation is the **ToS-compliant host-native alternative**:

| Mechanism | Isolation type | ToS-compliant | Requires container |
|---|---|---|---|
| Docker/container | Full OS isolation | No (subscription key) | Yes |
| Worktree | Filesystem isolation | Yes | No |
| `permissions.allow`/`permissions.deny` | Tool-level restriction | Yes | No |

Dangeresque (host-native) uses worktrees + tool filtering. SandCastle runs Claude on the host (worktree isolation) and only containers for tool execution — Claude itself never runs inside Docker. Note: CC's native settings.json schema uses `permissions.allow`/`permissions.deny`, not the older `allowedTools`/`disallowedTools` names. See [[summaries/claude-code-permissions-settings]].

---

## Implementations

| Tool | How it uses worktrees |
|---|---|
| [[entities/dangeresque]] | One worktree per task; worker runs in isolation; adversarial reviewer reads result |
| [[entities/sandcastle]] | Worktree + sandboxed container per task; branch strategy as a first-class parameter |
| [[concepts/agent-subagents]] | `isolation: "worktree"` in frontmatter; cleaned up automatically if no changes |
| [[summaries/exit-code-0-quality]] | Strict directory scope + separate worktree; discovery relay between waves |

---

## Fresh Context Window Per Task

Each worktree task gets a fresh agent session — no accumulated context from prior tasks. This is the mechanical basis for [[concepts/context-compression]] clear-over-compact in AFK workflows:

```
task 1 → worktree A → agent (fresh context) → commit → merge → worktree removed
task 2 → worktree B → agent (fresh context) → commit → merge → worktree removed
```

State carried between tasks lives in: commits, branch history, `.agents/decisions.md`, issue files — not in agent memory. This is what Pocock means by "make clearing safe, then prefer clearing."

---

## Related Pages

- [[concepts/branch-strategy-for-agents]] — merge strategy after worktree work completes
- [[concepts/agentic-sandbox-controls]] — ToS constraint driving host-native isolation
- [[concepts/context-compression]] — clear-over-compact; worktrees make clearing safe
- [[entities/dangeresque]] — lightweight host-native orchestrator using worktrees
- [[entities/sandcastle]] — TypeScript lib; worktree + container combination
- [[summaries/exit-code-0-quality]] — scope overlap detection, merge-before-cleanup protocol
- [[concepts/agent-subagents]] — `isolation: "worktree"` parameter
