---
title: "Branch Strategy for Agents"
type: concept
tags: [orchestration, git, worktrees, parallelization, agent-harness]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Branch Strategy for Agents

When running parallel agents in isolated git worktrees, the merge strategy is a first-class parameter that determines safety, speed, and human involvement. Formalized by [[entities/sandcastle]]; the underlying decision exists in any multi-agent worktree setup.

---

## Three Strategies

### `head`
Each agent works directly off main HEAD. No branch created.

- Fastest — no merge step
- Risky — file scope must be truly non-overlapping; any overlap causes conflicts
- Appropriate for: tasks with clear, provably non-overlapping file scope (e.g., agents owning separate modules)

### `merge-to-head`
Agent creates a branch, implements, auto-merges back to HEAD when verification passes.

- Default for parallel work
- Handles light merge conflicts automatically
- Verification gate (tests + types) must pass before auto-merge
- Appropriate for: standard parallel AFK implementation

### `branch`
Agent creates a branch, stops. Human reviews diff and merges manually.

- Maximum control — human sees everything before integration
- Required when: changes affect shared interfaces, high-risk changes, uncertainty about scope
- Matches [[entities/dangeresque]]'s mandatory human-merge gate philosophy

---

## Decision Heuristic

```
Are files guaranteed non-overlapping?
  Yes + low risk → head
  Yes + medium risk → merge-to-head

Is human review required before merge?
  Yes → branch
  No → merge-to-head (default)
```

---

## Relation to Worktrees

Branch strategy is distinct from worktree isolation. Worktrees provide filesystem isolation during implementation — each agent works in its own checkout. Branch strategy determines what happens at merge time, after implementation completes.

All three strategies can use worktree isolation during implementation. The branch parameter only affects the merge step.

---

## Relation to Existing Wiki

- [[entities/sandcastle]] — formalizes this taxonomy as a first-class parameter
- [[entities/dangeresque]] — implements the `branch` strategy (mandatory human-merge gate)
- [[concepts/agent-harness]] — worktree isolation as a harness component
- [[concepts/ralph-loop]] — the loop that branch strategy is embedded in
- [[concepts/verification-pipeline]] — verification runs before merge; strategy determines what follows
