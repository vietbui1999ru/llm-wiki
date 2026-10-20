---
date: 2026-10-20
type: tool-misuse
domain: claude-code
severity: low
---

# Worktree guard refuses compound Bash that runs git, gh or rtk

## What happened
In a worktree-isolated Claude Code session, several Bash calls were refused with "too complex to verify that it stays inside the worktree":
- a `for` loop that ran `bat` over a variable (rtk rewrites it)
- `gh pr create --body "$(printf ...)"`
- a `python3 -` heredoc whose text mentioned `git`
- `git add && git commit && git push` chained with heredoc input

A related failure: rtk's rewrite of a compound command dropped shell variables (`$W` came through empty), so a config check silently ran against the live config instead of the file under test.

## What the fix was
Each step ran as a plain single command with literal paths. Commit messages and PR bodies went to files passed with `git commit -F` and `gh pr create --body-file`. Multi-step logic went into a script under `$CLAUDE_JOB_DIR/tmp`, run with `zsh <script>`.

## Prevention rule
In worktree-isolated sessions, run git, gh and rtk-rewritten tools as single commands with literal paths. Put loops, variables, heredocs and `$(...)` in a script file, and pass message and body text with `-F`/`--body-file`.

## Context
Making jj the default VCS and running a Pi model bake-off in `~/dotfiles`, from the worktree `.claude/worktrees/jj-agent-default`.
