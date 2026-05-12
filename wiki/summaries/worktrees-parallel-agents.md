---
title: "Git Worktrees for Parallel AI Agent Execution"
type: summary
tags: [worktrees, parallelization, agent-harness, git, coordination, multi-agent]
sources:
  - "How to Use Git Worktrees for Parallel AI Agent Execution.md"
  - "Parallel agents + git worktrees real-world experience?.md"
created: 2026-05-12
updated: 2026-05-12
---

# Git Worktrees for Parallel AI Agent Execution

Two sources: a technical guide from Augment Code (Intent product) and a Reddit practitioner thread. Both converge on the same conclusions.

---

## The Four Failure Modes (Shared Repo, Multiple Agents)

| Failure | Detection | Impact |
|---|---|---|
| Concurrent file overwrites | Undetected until compile/runtime | Silent data loss |
| Context contamination | No signal to affected agent | Cascading breakage across interdependent changes |
| Race conditions on shared state | Silent | Corrupted build artifacts, test state |
| Git lock contention | Immediate error | System-wide git freeze until manual intervention |

Agents do not notice when something goes wrong. These failures scale with participant count regardless of whether participants are humans or LLMs.

---

## What Worktrees Fix

- **File overwrites** → converted into visible merge-time conflicts (standard git tooling handles them)
- **Context contamination** → each agent's working directory is isolated; incomplete edits from agent A are invisible to agent B
- **Git lock contention** → each worktree has its own `index` file; staging operations don't compete

**Core mechanic:** each worktree gets private `HEAD`, private `index`, private working directory. The shared `.git` object store means isolation costs only working-directory-level disk — not full repo duplication.

---

## What Worktrees Do NOT Fix

### Runtime conflicts
Port collisions when two agents start dev servers on `:3000`. Shared databases, test state, build caches, environment variables. Worktrees give filesystem isolation — zero network or process isolation.

**Emerging composite pattern:** combine worktrees (git isolation) with lightweight runtime isolation for full-stack agents. Dagger's Container-Use combines the two. Galactic (github.com/idolaman/galactic) assigns a unique local IP per worktree (127.0.0.2, 127.0.0.3, etc.) so multiple backends can run simultaneously without port juggling.

### Logical/semantic conflicts
Agent A writes `formatDate()` in `utils/dates.ts`; agent B writes an equivalent `parseDate()` in `helpers/time.ts`. No git conflict — both pass CI — but duplicate code that surfaces only in review. Community rule: assign agents to strictly non-overlapping **file domains** before work begins; scope overlap at the task planning stage, not after.

### Shared state coordination
DB migrations, shared config files, test fixtures. These need upfront coordination (locks, sequencing) — not something worktrees provide. Block built `agent-task-queue` specifically to prevent multiple parallel agents from independently triggering expensive operations (`./gradlew test`): FIFO coordination queue prevents resource thrashing.

---

## Worktree-Per-Task vs Worktree-Per-Agent

| Factor | Worktree-Per-Task | Worktree-Per-Agent |
|---|---|---|
| Task duration | Short (minutes to ~1 hour) | Long (multi-hour sessions) |
| Cache reuse | None; fresh install per task | Warm; dependencies persist |
| Cleanup model | Destroy after each task | Destroy after session ends |
| Best fit | Ephemeral code generation, one-shot refactors | Dedicated test writers, ongoing refactoring agents |

**Default:** worktree-per-task. Use worktree-per-agent only when the agent persists across multiple tasks and benefits from warm dependency caches or accumulated environment state.

---

## Dependency Handling

Dependencies (`node_modules`) are not shared or auto-created in new worktrees. Four strategies:

1. **`npm ci --prefer-offline`** (safe default) — uses npm's shared user-level cache; works on all platforms
2. **Symlink** — only safe when `package-lock.json` is byte-identical between worktrees
3. **Copy-on-write** (`cp -c`) — near-zero upfront cost; macOS APFS only, not portable
4. **npm workspaces** — if the repo is already a monorepo workspace

Start with `npm ci --prefer-offline`. Symlinks only when install time exceeds task duration and lockfiles are guaranteed identical.

---

## Operational Patterns

### Bootstrap script
```bash
#!/usr/bin/env bash
# create-agent-worktree.sh <task-id> [base-branch]
TASK_ID="${1:?}"
BASE_BRANCH="${2:-main}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
BRANCH_NAME="agent/$(echo "$TASK_ID" | sed 's/[^a-zA-Z0-9-]/-/g' | cut -c1-50)"
WORKTREE_PATH="${REPO_ROOT}/.trees/${TASK_ID}"

mkdir -p "${REPO_ROOT}/.trees"
grep -qxF '.trees/' "${REPO_ROOT}/.gitignore" || echo '.trees/' >> "${REPO_ROOT}/.gitignore"

git fetch origin "${BASE_BRANCH}"
git worktree add -b "${BRANCH_NAME}" "${WORKTREE_PATH}" "origin/${BASE_BRANCH}"
cd "${WORKTREE_PATH}" && npm ci --prefer-offline

# Assign deterministic port from branch name hash
PORT=$(( 3100 + $(echo "${BRANCH_NAME}" | cksum | cut -d' ' -f1) % 6899 ))
echo "DEV_PORT=${PORT}" >> .env.local

# Lock while agent is running
git worktree lock --reason "Agent running" "${WORKTREE_PATH}"
```

### Cleanup
```bash
# Always prefer git worktree remove over rm -rf (prevents stale .git/worktrees/ metadata)
git worktree unlock .trees/TASK-123
git worktree remove .trees/TASK-123
git worktree prune --verbose

# For repos used exclusively for ephemeral worktrees
git config gc.worktreePruneExpire now
```

### Conflict resolution recording
Enable `git rerere` so resolved conflicts are recorded and auto-reapplied on recurrence:
```bash
git config rerere.enabled true
```

### Monorepo sparse checkout
Constrain each worktree to files the agent actually needs:
```bash
git worktree add .trees/TASK-123 -b agent/TASK-123 origin/main
cd .trees/TASK-123
git sparse-checkout set src/payments/ tests/payments/
```

---

## Community Convergence

From the Reddit thread (practitioners, March 2026):

- **Parallelize only truly independent tasks.** If two tasks share a directory or import the same modules, sequence them — conflict resolution cost eats the speed win.
- **Logical duplication is the second failure mode.** Two agents writing near-identical helper functions in different modules — caught in review, costs cleanup time.
- **Worktrees + coordinator is the full stack.** Worktrees = isolation; parallel agents = parallelism; a coordinator (Switchman, Overstory, or a planner agent) = coordination. Without coordination, it's still last-write-wins for logical conflicts.

---

## Tooling Landscape

| Tool | Role |
|---|---|
| Galactic (idolaman/galactic) | Per-worktree local IP; solves port conflicts |
| Block agent-task-queue | FIFO coordination for expensive shared operations |
| Switchman | File claiming; prevents logical overlap upfront |
| Overstory (jayminwest/overstory) | FIFO merge queue + watchdog for larger agent fleets |
| Dagger Container-Use | Worktrees + container runtime isolation composite |
| Intent (Augment Code) | Full orchestration: living spec + coordinator + specialist + verifier + worktrees |

---

## Intent Architecture (Reference Implementation)

Three-tier agent structure built on worktrees:

- **Coordinator** — decomposes spec into dependency-ordered tasks, delegates in waves
- **Specialists** (6 built-in: Investigate, Implement, Verify, Critique, Debug, Code Review) — execute in parallel, each in an isolated worktree
- **Verifier** — quality gate; checks output against spec before developer review

The **living spec** is the coordination artifact: shared document that auto-updates as agents complete work. Human approval gate before execution; human review before merge. BYOA (Bring Your Own Agent) supported — Claude Code, Codex, OpenCode as drop-in implementers.

---

## Related Pages

- [[concepts/worktree-isolation]] — mechanics, ToS constraint, scope overlap, merge protocol
- [[concepts/shared-task-queue]] — filesystem-based inbox with atomic claim semantics (cross-worktree coordination)
- [[concepts/worker-coordination]] — partial result passing between agents; blackboard pattern
- [[entities/sandcastle]] — parallel agent loop using worktrees + containers
- [[entities/dangeresque]] — host-native orchestrator; worktrees without containers
- [[summaries/mattpocockworkflow]] — AFK parallel loop; issue files as task source
- [[concepts/branch-strategy-for-agents]] — head/merge-to-head/branch after worktree work
