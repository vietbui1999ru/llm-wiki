---
date: 2026-11-09
type: bad-assumption
domain: rg
severity: low
---

# rg named a file that was assumed to exist

## What happened
Ran `rg -n ... CLAUDE.md shared/AGENTS.md` from the dotfiles worktree. The repo has no root `CLAUDE.md`, so rg exited 2 with "No such file or directory", although `shared/AGENTS.md` still returned matches.

## What the fix was
Search only paths confirmed to exist. In dotfiles the agent rules live in `shared/AGENTS.md` and under `claude/.claude/`.

## Prevention rule
Before naming a specific file in `rg`, confirm it exists with `fd` or `eza`, or search the containing directory with a `-g` glob.

## Context
Checking where the repo keeps plan documents while inventorying worktree assumptions for the jj workspaces work on `feat/jj-ws`. The PostToolUseFailure hook reported the pattern `bash|rg -n|not-found` as 3 hits in 14 days.
