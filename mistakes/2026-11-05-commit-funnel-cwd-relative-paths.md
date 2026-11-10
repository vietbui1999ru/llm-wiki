---
date: 2026-11-05
type: tool-misuse
domain: commit-funnel
severity: low
---

# commit-funnel resolves path arguments against the shell's cwd, not --worktree

## What happened
After running tests from `scripts/tests`, the shell's working directory stayed in that
subdirectory. `commit-funnel --worktree <root> -F msg scripts/spec` then looked for
`scripts/tests/scripts/spec` and refused: "path is not in the work tree, nor the parent commit".

## What the fix was
`cd` to the worktree root first, then rerun the same command; it committed.

## Prevention rule
Run commit-funnel from the worktree root (or pass absolute paths). `--worktree` only names the
checkout; it does not set the base for relative path arguments. A `cd` into a subdirectory for
tests persists into the next command.

## Context
dotfiles, band-only approval phase 1: committing the person-applied `scripts/spec` patch in the
`specapp` worktree.
