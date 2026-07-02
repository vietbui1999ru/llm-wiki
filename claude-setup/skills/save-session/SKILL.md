---
name: save-session
description: Full session summary save. Use before clearing context, compacting, or ending a long session. Writes to the universal session inbox at .agents/sessions/ via the agent-session CLI.
---

# Save Session — Full Context Capture

## Purpose

Write a complete, resumable snapshot of the current session to the **universal
session inbox** at `.agents/sessions/` (one inbox per repo, shared across all
agent harnesses). Uses the `agent-session` CLI for consistent naming, tagging,
and index maintenance.

Legacy `.claude/session-state.md` is kept as a thin pointer for backward
compatibility.

## When to Use

- Before `/clear` or context compact
- Before closing Claude Code after significant work
- When user says "save", "wrapping up", "done for now", "save state"
- After any session where decisions were made or significant files changed

## Step 0 — Detect context (agent vs orchestrator)

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
MAIN_REPO=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
TASK_ID=$(cat "${REPO_ROOT}/.agent-task-id" 2>/dev/null)
```

**Agent context** (`.agent-task-id` sentinel present): state goes to
`.agents/claimed/<TASK-ID>.state.md` — unchanged, no contention with other agents.

**Orchestrator context** (no sentinel): state goes to the universal inbox via:

```bash
agent-session save --harness cc --goal "<one-sentence goal>" --body -
```

Pipe the full state body (see Step 2) via stdin (`--body -`). The CLI writes
`.agents/sessions/<timestamp>_cc_<work-type>_<slug>.md`, updates `index.json`,
and writes a 1-line pointer to `.claude/session-state.md` for backward compat.

Auto-derived: work-type from branch name, slug from goal. Override with
`--work-type feature|fix|refactor|...` and `--slug <slug>` as needed.

## Step 1 — Gather State

Run in parallel:

```bash
git status --short
git log --oneline -5
cat "$STATE_FILE" 2>/dev/null || echo "NO_PRIOR_STATE"
```

Also read from current conversation context:

- What was the original goal this session?
- What was completed?
- What decisions were made (and why)?
- What is blocked or in progress?
- What should the next session start with?

## Step 2 — Write state file

For **agent context** (sentinel): overwrite `$STATE_FILE` (`.agents/claimed/<TASK>.state.md`)
with the markdown below.

For **orchestrator context**: pipe the markdown below as stdin to:

```bash
agent-session save --harness cc --goal "<goal>" --body -
```

The markdown body:

```markdown
## Completed
- <item 1>
- <item 2>

## In Progress
- <item> — <where it was left, what the next step is>

## Decisions Made
- <decision> — <why>

## Blocked / Needs Input
- <item> — <what's needed to unblock>

## Files Modified This Session
<git status or manual list>

## Next Session Should
1. <first thing to do>
2. <second thing>

## Active Plugins This Session
<list from profile.md or inferred>
```

`status: active` signals the next session to inject this state into context.
(The CLI sets this automatically in frontmatter.)

## Step 3 — Confirm

Tell user: "Session state saved to `.agents/sessions/` (universal inbox).
Resume anytime — next session will inject this automatically."

Do NOT commit the state file unless user asks.

## Step 4 — Flip to Idle (when work is done)

For **agent context**: `sed -i '' 's/^status: active$/status: idle/' "$STATE_FILE"`

For **orchestrator context**:

```bash
agent-session idle
```

This flips the latest active session in the universal inbox to idle.

Tell user: "Session state marked idle — next session will start fresh."
