---
date: 2026-11-05
type: tool-misuse
domain: claude-code-worktree-guard
severity: low
---

# Worktree guard refused a for-loop running `bash "$t"` (recurrence)

## What happened
In a `.claude/worktrees/jj-wt` session, one Bash call ran `for t in .../*.test.sh; do bash "$t"; done; jj st`. The guard refused it: it cannot verify that shell text run by `bash` inside a loop does not run git.

## What the fix was
Ran each test script as a plain, separate `bash <path>` command, with an explicit `cd` into the worktree root.

## Prevention rule
Already covered by `mistakes/worktree-guard-rules.md` line 12: no loops, variables or `$(...)` around `bash`/git in a worktree session; list commands plainly or move the loop into a `$CLAUDE_JOB_DIR/tmp` script.

## Second hit, same session
Later, `for n in 243 239 252; do gh pr view $n --json ... --jq ...; done` was refused in the same way: any loop in a worktree session is unverifiable, even one that runs `gh` rather than git or bash. Run one `gh pr view <n>` per command.

## Context
Resolving the merge conflict in dotfiles PR #243 (feat/guard-log), while running the hook test suite.
