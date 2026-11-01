---
date: 2026-11-01
type: tool-misuse
domain: claude-code-worktree-guard
severity: low
---

# Inline `python3 -I -c` refused because its strings mentioned git

## What happened
In a worktree-isolated session, ran `python3 -I -c "..."` to write six commit-message files. The
inline code contained the word "git" only inside string literals (message text). The worktree
guard refused it as "names git in a form too complex to verify".

## What the fix was
Wrote each message file with the Write tool, then committed through `commit-funnel -F <file>`.

## Prevention rule
In a worktree-isolated session, never inline code with `-c`/`-e` whose text contains "git", even
in strings: write content with Write, or put the script in a `$CLAUDE_JOB_DIR/tmp` file and run it
by path. Covered by `mistakes/worktree-guard-rules.md`; third hit in 14 days.

## Context
2026-11-01 ingest batch (PR #67): writing commit messages before committing per cluster.
