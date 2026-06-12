---
title: "Pi Orchestration Architecture"
type: synthesis
tags: [agent-harness, orchestration, pi-agent, opencode, pueue, diff-review, multi-agent, human-in-the-loop]
sources: []
created: 2026-06-05
updated: 2026-06-05
---

# Pi Orchestration Architecture

Design of a human-gated multi-agent coding system using Claude Code or OpenCode as orchestrator, pi workers dispatched via pueue, and the `pi-diff-review` extension as the review gate.

All design decisions derived from a structured grill session.

---

## System Overview

```
Human → high-level goal
  ↓
Orchestrator (Claude Code or OpenCode — contextual/manual choice)
  → decomposes into structured specs: {task, scope, done-when}
  → verifies diff-review extension installed (fail fast if missing)
  → presents decomposition to human for approval
  ↓
pueue fires N pi workers in parallel
  cmd: PUEUE_TASK_ID=<id> DIFF_REVIEW_RETRY_COUNT=<n> \
       pi -p "Task: ... Scope: ... Done when: ..."
  workers self-route models via AGENTS.md (OpenCode Go subscription)
  workers spawn read-only Scouts for codebase exploration
  diff-review: headless mode → audit log only (auto-accept)
  ↓
pueue tasks complete → orchestrator reads per-worker:
  .pi/diff-review/status-<id>.json   → resolved? needsHuman?
  .pi/diff-review/decisions.jsonl    → per-file audit trail
  git diff                           → what landed on disk
  ↓
All resolved → orchestrator presents git diff → human commits manually
Any needsHuman=true → orchestrator halts, presents unresolved files
  → human provides guidance
  → orchestrator re-runs worker: DIFF_REVIEW_RETRY_COUNT incremented,
    "Previously unresolved: <files>" appended to prompt
  → max 3 total attempts; needsHuman=true on attempt 2 → stop
```

---

## Key Design Decisions

### Orchestrator choice
Claude Code or OpenCode — contextual or manual. No automated routing between them. Both dispatch pi workers identically. Orchestrator choice is about what model family runs the planning layer (Claude judgment vs GPT-5.x), not about task type.

### Dispatch mechanism
`pueue` — background task queue. Orchestrator fires N workers simultaneously, each as an independent `pi -p "..."` process. `pueue wait <id>` blocks until completion; `pueue log <id>` captures stdout for debugging.

### Task prompt format
Structured spec, not free text:
```
Task: <description>
Scope: <files or directories worker is allowed to touch>
Done when: <acceptance criteria>
```
Scope enforcement is prompt-level only — no filesystem isolation (no worktrees). Non-overlapping scope assignments prevent parallel workers from conflicting.

### File isolation
Task scoping (not git worktrees). Orchestrator assigns non-overlapping file/module scopes per worker. Worktrees add overhead not justified for ≤5 parallel tasks with clean module boundaries. See [[concepts/shared-task-queue]] for when worktree pools are needed instead.

### Model routing
Workers self-route via `~/.pi/agent/AGENTS.md` difficulty-tier routing. Orchestrator passes the task; worker picks the model. OpenCode Go subscription ($10/mo) provides the model pool: DeepSeek V4 Pro (high), Flash (medium/low). See [[entities/pi-agent]] for the full routing table.

### Worker subagents
Scouts only (read-only, Haiku-class, depth-limited). Write-capable sub-workers not enabled — creates nested task-scope coordination problem the architecture doesn't solve. See [[entities/pi-agent]] for Scout/Researcher/Worker tier definitions.

### Review modes — two distinct paths

**Interactive pi sessions** (human runs pi with TUI):
- `pi-diff-review` fires per write/edit
- Human reviews line-by-line: accept/deny/edit per changed row
- Model self-corrects within session when lines are denied
- After session: manual git review + commit

**Headless pueue workers** (`pi -p "..."`):
- `ctx.hasUI = false` → extension auto-accepts, writes audit log only
- Human gate happens post-completion at orchestrator level
- Orchestrator reads `git diff` + `status-<id>.json` and presents to human
- Human commits manually after review

### Status artifact

Written on `session_shutdown`. Named `status-<PUEUE_TASK_ID>.json` (falls back to `status.json`). Fields:

```json
{
  "resolved": false,
  "unresolvedFiles": ["auth/login.ts"],
  "retryCount": 1,
  "needsHuman": false
}
```

- `resolved`: all files' last decision was `"accepted"`
- `unresolvedFiles`: files whose last `applyReview` action ≠ `"accepted"`
- `retryCount`: value of `DIFF_REVIEW_RETRY_COUNT` env var at time of write
- `needsHuman`: `!resolved && retryCount >= 2` — orchestrator stops retrying

"Last decision" = last `decisions.jsonl` entry per file path. Earlier denials followed by a final acceptance = resolved. See `apply-decisions.ts:writeStatusArtifact`.

### Retry strategy
Orchestrator re-runs failed workers with added context, up to 3 total attempts (retry counts 0, 1, 2). On attempt 2 with unresolved files: `needsHuman=true` in status artifact → orchestrator halts, human takes over manually.

Re-run prompt pattern:
```
Task: <original task>
Scope: <original scope>
Done when: <original criteria>
Previously unresolved: <unresolvedFiles from last status artifact>
```

### Commit strategy
No auto-commit. Orchestrator presents full `git diff` after all workers complete. Human reviews and commits manually. Per [[summaries/pi-building-in-world-of-slop]]: "critical code, read every line."

### Extension loading
`pi-diff-review` installed globally via `pi install`. Orchestrator verifies extension presence at startup (fail-fast gate) before firing any workers. Silent absence of the review gate is worse than a loud startup failure.

---

## Artifact Layout

```
.pi/diff-review/
  status-<pueue-task-id>.json    # resolved, unresolvedFiles, retryCount, needsHuman
  decisions.jsonl                # append-only; one record per write/edit tool call
  latest.md                      # human-readable summary of most recent decision
```

---

## Orchestrator Dispatch Snippet

```bash
# Decompose → approve → dispatch
TASK_ID=$(pueue add --print-task-id -- \
  env PUEUE_TASK_ID=__PLACEHOLDER__ DIFF_REVIEW_RETRY_COUNT=0 \
  pi -p "Task: refactor auth module
Scope: src/auth/
Done when: all auth functions have error handling")

# Wait and collect
pueue wait "$TASK_ID"
STATUS=$(cat .pi/diff-review/status-${TASK_ID}.json)

# Route
if jq -e '.needsHuman' <<< "$STATUS"; then
  echo "Escalate: $(jq -r '.unresolvedFiles[]' <<< "$STATUS")"
elif jq -e '.resolved | not' <<< "$STATUS"; then
  # retry with incremented count + unresolved context
else
  git diff  # present to human → manual commit
fi
```

---

## Related Pages

- [[entities/pi-agent]] — pi-mono architecture, AGENTS.md routing, subagents extension
- [[entities/opencode]] — OpenCode as orchestrator; headless `run`/`serve` modes
- [[entities/opencode-go]] — OpenCode Go subscription; model pool for pi workers
- [[summaries/pi-building-in-world-of-slop]] — Pi design philosophy; minimal harness, self-modifying extensions
- [[concepts/agent-harness]] — harness primitives; filesystem as coordination layer
- [[syntheses/agent-primitive-selection]] — decision tree for orchestration patterns
- [[concepts/shared-task-queue]] — when to use worktrees instead of task scoping
