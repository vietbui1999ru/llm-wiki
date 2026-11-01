---
date: 2026-10-26
type: tool-misuse
domain: claude-code-worktree-guard
severity: low
---

# Worktree Bash guard refuses `$HOME` expansion and `cd &&` chains

## What happened
In a worktree-isolated session, several Bash calls were refused: `cd "$HOME/..." && ac-run lint`, a `sed ... "$HOME/..."` redirect, and a combined `git switch && ac-run && sed` command. A follow-up `cd ... && ac-run lint .lint-SPEC.md` then failed because the earlier `sed` that should have created the file had been refused.

## What the fix was
Ran plain single commands with paths relative to the worktree cwd (the session cwd is already the worktree), or literal absolute paths with no variables.

## Prevention rule
In worktree-isolated sessions, run each command alone from the worktree cwd with relative or literal absolute paths; never use `$HOME`/variables in arguments or `cd ... &&` chains.

## Context
Updating SPEC.md on branch spec/rev10-owner-decisions in personal-ai-gateway and linting it with ac-run.
