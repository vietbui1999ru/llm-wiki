---
date: 2026-10-19
type: tool-misuse
domain: zsh
severity: low
---

# Unquoted `echo =====` in zsh aborts a chained command

## What happened
A chained read command used `echo =====` as a separator. zsh treats a leading `=` word as equals-expansion
(`=cmd` -> path of cmd), failed with `==== not found`, and the rest of the chain did not run. Earlier in the
same session `raw/*(.om[1,15])` (zsh glob qualifier, copied from CLAUDE.md) also failed with "no matches found".

## What the fix was
Quote separators (`echo '---'`). List newest raw files with `ls -t raw | head` instead of glob qualifiers.

## Prevention rule
In agent Bash calls (zsh), quote any literal word starting with `=` and avoid zsh glob qualifiers; prefer
`ls -t`/`fd` for time-ordered listings.

## Context
pele ingest: reading template pages and index anchors in the llm-wiki worktree.
