---
name: save-session
description: Full session summary save. Use before clearing context, compacting, or ending a long session. Writes detailed state to .claude/session-state.md.
---

# Save Session — Full Context Capture

## Purpose
Write a complete, resumable snapshot of the current session to `.claude/session-state.md`.
The stop hook writes lightweight checkpoints automatically. This skill writes the full human+agent-readable summary.

## When to Use
- Before `/clear` or context compact
- Before closing Claude Code after significant work
- When user says "save", "wrapping up", "done for now", "save state"
- After any session where decisions were made or significant files changed

## Step 0 — Detect context (agent vs orchestrator)

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
MAIN_REPO=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)
# Env vars don't cross hook/skill process boundaries — use sentinel file instead
TASK_ID=$(cat "${REPO_ROOT}/.agent-task-id" 2>/dev/null)
if [[ -n "$TASK_ID" ]]; then
  STATE_FILE="${MAIN_REPO}/.agents/claimed/${TASK_ID}.state.md"
  CONTEXT="agent (task: $TASK_ID)"
else
  STATE_FILE="${MAIN_REPO}/.claude/session-state.md"
  CONTEXT="orchestrator"
fi
```

Use `$STATE_FILE` for all reads and writes below. In agent context, the state lands in
`.agents/claimed/<TASK-ID>.state.md` — no contention with other agents or the orchestrator.

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

Overwrite `$STATE_FILE` with:

```markdown
# Session State
status: active
saved_at: <ISO8601 timestamp e.g. 2026-05-19T14:30:00Z>
updated: <YYYY-MM-DD HH:MM UTC>
branch: <current branch>
agent_task: <AGENT_TASK_ID if set, else omit this line>

## Goal
<one sentence: what this session was trying to accomplish>

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

## Step 3 — Confirm

Tell user: "Session state saved to `$STATE_FILE`. Resume anytime — next session will inject this automatically."

Do NOT commit the state file unless user asks.

## Step 4 — Flip to Idle (when work is done)

If the user says work is complete, paused indefinitely, or says "mark session idle" / "clear session state":

```bash
sed -i '' 's/^status: active$/status: idle/' "$STATE_FILE"
```

Tell user: "Session state marked idle — next session will start fresh."
