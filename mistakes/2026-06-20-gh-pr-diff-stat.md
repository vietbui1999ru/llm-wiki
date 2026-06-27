---
date: 2026-06-20
type: cli-flag
domain: gh
severity: low
---

# Unsupported gh pr diff --stat Flag

## What happened
Ran `gh pr diff 10 --stat`, but `gh pr diff` does not support `--stat`.

## What the fix was
Use `gh pr diff --name-only` for file lists or `gh pr view --json files,statusCheckRollup` for structured PR inspection.

## Prevention rule
Before using an unfamiliar CLI flag, verify the subcommand's supported flags instead of assuming common git-style options exist.

## Context
Creating and validating a Commandr pull request before merging. The wrong flag produced a harmless usage error during PR inspection.
