---
title: "Shared Task Queue (Cross-Worktree)"
type: concept
tags: [agent-harness, parallelization, worktrees, coordination, orchestration, task-management]
sources:
  - "How to Use Git Worktrees for Parallel AI Agent Execution.md"
  - "Parallel agents + git worktrees real-world experience?.md"
created: 2026-05-12
updated: 2026-05-12
---

# Shared Task Queue (Cross-Worktree)

A filesystem-based task inbox shared across all parallel worktree agents. Agents pull tasks at session start without a central dispatcher. The missing coordination layer between worktree isolation (filesystem) and the Pocock/SandCastle planner model (centralized assignment).

---

## The Problem

Worktrees are filesystem-isolated — a directory inside worktree A is not visible to worktree B. The natural instinct is to put the task inbox inside the repo, but that inbox lands inside each worktree's own checkout, so agents can't see each other's task state.

**The fix:** the inbox lives in the **main checkout**, not in any worktree. Every worktree can locate the main checkout via `git rev-parse --git-common-dir`, which always returns the path to the shared `.git` regardless of which worktree the agent is running in.

```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
# Works from any worktree:
# .trees/TASK-001/ → MAIN_REPO = /path/to/main-repo
# .trees/TASK-002/ → MAIN_REPO = /path/to/main-repo (same)
```

---

## Directory Layout

```
main-repo/               ← main checkout (not a worktree)
  .agents/
    inbox/               ← unclaimed tasks; agents read from here
      TASK-001.md
      TASK-002.md
    claimed/             ← atomically moved here when agent claims
      TASK-003.md        ← filename includes agent identity
    done/                ← moved here on completion
      TASK-004.md
  .trees/                ← gitignored; all worktrees live here
    TASK-001/            ← worktree A
    TASK-002/            ← worktree B
```

`.agents/` can be committed (tasks become part of repo history) or gitignored (ephemeral, recreated per session). Committing is preferred: the task state is auditable and survives machine restarts.

---

## Atomic Claim Protocol

`mv` is atomic on POSIX for renames within the same filesystem. Two agents racing to claim the same task file: exactly one `mv` succeeds, the other gets `ENOENT`. No lock files, no polling loop for the lock.

```bash
#!/usr/bin/env bash
# .agents/claim.sh

MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
INBOX="${MAIN_REPO}/.agents/inbox"
CLAIMED="${MAIN_REPO}/.agents/claimed"

for task_file in "${INBOX}"/*.md; do
  [ -f "$task_file" ] || { echo "inbox:empty"; exit 0; }
  task_name=$(basename "$task_file")
  # Include agent identity in claimed filename for debugging
  claimed_name="$(hostname)-$$-${task_name}"
  if mv "${task_file}" "${CLAIMED}/${claimed_name}" 2>/dev/null; then
    echo "claimed:${CLAIMED}/${claimed_name}"
    cat "${CLAIMED}/${claimed_name}"
    exit 0
  fi
  # mv failed = another agent got it first; try next
done
echo "inbox:empty"
```

### Completion

```bash
# .agents/complete.sh <claimed-file-path>
CLAIMED_FILE="${1:?}"
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
mv "${CLAIMED_FILE}" "${MAIN_REPO}/.agents/done/$(basename "${CLAIMED_FILE}")"
```

---

## Three Startup Layers

Pick the depth appropriate to your setup.

### Layer 1: CLAUDE.md instruction (lightest)

```markdown
## Startup: Claim Your Task

Before doing anything else in a new session:
1. Run: bash "$(dirname "$(git rev-parse --git-common-dir)")/.agents/claim.sh"
2. If output starts with `claimed:` — read the file path; that's your task
3. If output is `inbox:empty` — check with the coordinator before continuing
4. On completion: run bash "$(dirname "$(git rev-parse --git-common-dir)")/.agents/complete.sh <path>"
```

All worktrees inherit this CLAUDE.md from the main branch. The instruction is always in context. Relies on the agent following it.

### Layer 2: Orchestrator pre-claims (reliable)

The orchestrator claims tasks before spawning Claude. Claude never sees the inbox — it receives its task in the initial prompt.

```bash
#!/usr/bin/env bash
# spawn-agents.sh
MAIN_REPO=$(git rev-parse --show-toplevel)
INBOX="${MAIN_REPO}/.agents/inbox"
CLAIMED="${MAIN_REPO}/.agents/claimed"

for task_file in "${INBOX}"/*.md; do
  [ -f "$task_file" ] || continue
  task_name=$(basename "$task_file")
  mv "${task_file}" "${CLAIMED}/${task_name}" 2>/dev/null || continue

  WORKTREE="${MAIN_REPO}/.trees/${task_name%.md}"
  git worktree add -b "agent/${task_name%.md}" "$WORKTREE" origin/main
  git worktree lock --reason "Agent running" "$WORKTREE"
  cd "$WORKTREE" && npm ci --prefer-offline

  # Task baked into prompt — no inbox discovery needed in the agent
  claude --print "$(cat "${CLAIMED}/${task_name}")" &
  cd - > /dev/null
done
wait
```

This is the Pocock/SandCastle pattern extended with pre-claim. The planner populates inbox; the orchestrator claims and spawns.

### Layer 3: Skill (agent-pull model)

```markdown
# ~/.claude/skills/claim-task/SKILL.md
---
name: claim-task
description: Claim the next available task from the shared inbox. Invoke at the start of any new session before doing any work.
allowed-tools: Bash
---

Run the claim script and read your task:

MAIN=$(dirname "$(git rev-parse --git-common-dir)")
bash "${MAIN}/.agents/claim.sh"

If output is `claimed:<path>`, read the task file at that path.
That is your complete work specification. Do not start work until you've claimed a task.
```

Per [[concepts/agent-skills]]: skills are the right primitive for "do this at startup" — they're loaded on demand, show up as meta-tools, and the CLAUDE.md can instruct agents to invoke them before anything else.

---

## Task File Format

Task files should be self-contained — the agent should be able to start from nothing but the file.

```markdown
---
id: TASK-001
type: implementation
blocking: []
blocked-by: []
scope: src/payments/
---

# Implement Stripe Webhook Handler

## Context
[enough context for a fresh agent to proceed without prior conversation history]

## Acceptance criteria
- [ ] /api/webhooks/stripe handles checkout.session.completed
- [ ] Tests pass: npm test -- --testPathPattern=stripe
- [ ] No new TypeScript errors

## Files to touch
src/payments/webhook.ts (create)
tests/payments/webhook.test.ts (create)

## Do not touch
src/auth/ — another agent owns this
```

The `blocking/blocked-by` fields mirror the Pocock DAG — the orchestrator or planner uses these to decide what's claimable; agents don't need to parse them.

---

## Inbox Population Sources

| Source | How |
|---|---|
| `to-issues` skill output | Pocock's skill converts PRD → task files; drop into `.agents/inbox/` |
| Planner agent | Coordinator decomposes the spec, writes task files before spawning workers |
| Manual | Human writes task files directly |
| Previous wave output | Agents completing wave N write wave N+1 tasks as part of their completion step |

---

## State Machine

```
[created] → inbox/ → [claimable]
[claimed by agent] → claimed/ → [in-progress]
[agent completes] → done/ → [complete]
[agent fails/times out] → inbox/ (returned) → [claimable again]
```

Failure return: orchestrator monitors `claimed/` for tasks older than timeout threshold and `mv`s them back to `inbox/`.

---

## Relation to Existing Patterns

| Pattern | This design | Key difference |
|---|---|---|
| Pocock issue files | Task files = same format | Adds claim/done state machine; agents self-discover |
| SandCastle planner | Centralized pre-assignment | This: pull model; agents discover without dispatcher |
| CC agent teams task list | In-process only (`~/.claude/tasks/`) | This: cross-process, cross-worktree, filesystem-based |
| Worker-coordination blackboard | Partial results between running workers | This: task source at startup, not result destination |
| Block agent-task-queue | FIFO for expensive shared ops | This: task assignment, not resource coordination |

---

## Related Pages

- [[concepts/worktree-isolation]] — git worktree mechanics; how MAIN_REPO is found
- [[concepts/worker-coordination]] — blackboard pattern for results (complement to this)
- [[concepts/agent-skills]] — skills as the startup invocation mechanism
- [[concepts/ralph-loop]] — filesystem as durable state; same principle
- [[summaries/worktrees-parallel-agents]] — source; Block agent-task-queue; Switchman; worktree-per-task heuristic
- [[summaries/mattpocockworkflow]] — AFK loop; to-issues as inbox population source
- [[entities/sandcastle]] — planner model (centralized assignment; contrast with pull model here)
