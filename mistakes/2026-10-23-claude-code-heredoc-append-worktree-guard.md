---
date: 2026-10-23
type: tool-misuse
domain: claude-code
severity: low
---

# Heredoc append plus a test command refused by the worktree guard

## What happened
In a worktree-isolated session, one Bash call appended tests with `cat >> file <<'EOF' … EOF` and then ran `bun test`. The worktree guard refused it as too complex to verify. This was the third such refusal in 14 days.

It recurred minutes later in the same session as a heredoc feeding `python3 -I -` to edit the test file: the rule covers any heredoc, not only `cat`. Then `zsh -f <script>` was refused too (the guard cannot see what a shell script runs), which the old prevention rule had recommended; the rule now says to run such scripts with `python3 -I` instead.

## What the fix was
Append or change files with the Edit and Write tools, and run each test command as its own plain Bash call.

## Prevention rule
Already covered by `global-prevention-rules.md` (CLI / Shell, the 2026-10-20 addition): in a worktree-isolated session, never put heredocs or compound forms in Bash; edit files with Edit and Write.

## Context
Implementing plan A (agent-review absorb) in `~/dotfiles/.claude/worktrees/review-absorb`, adding Task 2 tests to `agent-review.absorb.test.ts`.
