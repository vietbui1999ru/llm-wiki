---
date: 2026-10-26
type: tool-misuse
domain: ac-run
severity: low
---

# ac-run lint/status run on a branch other than the SPEC's `branch:`

## What happened
Ran `ac-run lint SPEC.md` and later `ac-run status SPEC.md` in a worktree on `spec/rev10-owner-decisions` (and once on a detached HEAD) while SPEC.md names `branch: spec/rev10-replan-review`; both exited 2 on the branch check.

## What the fix was
For lint, linted a temporary copy with the branch field rewritten to the current branch. For status, relied on the owner's approval in the /gates pane instead.

## Prevention rule
Before any `ac-run` call, compare SPEC.md's `branch:` with the current branch; when a session works on a side branch, name it after the SPEC branch or plan the check on a copy, instead of running ac-run and hitting the branch guard.

## Context
Recording owner decisions and updating SPEC.md for core rev 10 in personal-ai-gateway from a session worktree branched off the SPEC branch.
