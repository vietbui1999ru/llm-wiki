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

## Step 1 — Gather State

Run in parallel:
```bash
git status --short
git log --oneline -5
cat .claude/session-state.md 2>/dev/null || echo "NO_PRIOR_STATE"
```

Also read from current conversation context:
- What was the original goal this session?
- What was completed?
- What decisions were made (and why)?
- What is blocked or in progress?
- What should the next session start with?

## Step 2 — Write `.claude/session-state.md`

Overwrite the full file:

```markdown
# Session State
updated: <YYYY-MM-DD HH:MM UTC>
branch: <current branch>

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

## Step 3 — Confirm

Tell user: "Session state saved to `.claude/session-state.md`. Resume anytime — next session will load this automatically."

Do NOT commit the state file unless user asks.
