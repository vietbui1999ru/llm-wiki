---
date: 2026-10-21
type: bad-assumption
domain: shell
severity: low
---

# Read a per-worktree file without checking that it exists

## What happened
To check specs in two worktrees, one command ran `ac-run status` and `head` on `.claude/worktrees/pi-pueue-controls/SPEC.md`, assuming every worktree has a root SPEC.md. That worktree has none, so the command failed with "cannot read: No such file or directory" and exit 1.

## What the fix was
Check the path first (`fd`/`ls`, or `[ -f "$p" ] && …`) and report "no SPEC.md" as a finding rather than letting the read fail.

## Prevention rule
When a command reads the same file across several worktrees or repos, test that each path exists first; a missing file is a finding to report, not an error to hit.

## Context
Checking the specs and pending reviews on `spec/commit-funnel` and `feat/pi-pueue-controls` in the dotfiles repo. The PostToolUseFailure hook reported the bash/rtk/not-found pattern 3 times in 14 days.
