---
date: 2026-10-29
type: tool-misuse
domain: worktree-guard
severity: low
---

# For-loop with unquoted variables refused by the worktree guard

## What happened
In a worktree-isolated Claude session, ran `for f in docs/specs/*.md; do ... rg -c '^- AC-' $f ...; done`.
The guard refused it: a runtime-computed value in an option position cannot be shown not to be git.

## What the fix was
Use one plain command over explicit paths (`rg -c '^- AC-' docs/specs/`), or move the loop into a
`$CLAUDE_JOB_DIR/tmp` script run with `python3 -I`.

## Prevention rule
Already covered in global-prevention-rules.md (CLI / Shell, worktree-isolated sessions): no loops or
variables in Bash commands there; use a single literal-path command or a tmp script. Third hit in 14 days.

## Context
Grilling the workflow benchmark spec; counting ACs per archived spec to choose pilot tasks.
