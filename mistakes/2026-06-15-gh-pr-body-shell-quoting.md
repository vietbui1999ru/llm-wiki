---
date: 2026-06-15
type: cli-flag
domain: gh
severity: medium
---

# GitHub PR body shell quoting mangled Markdown

## What happened
Ran `gh pr create --body "..."` with Markdown containing backticks, so zsh executed the backtick contents before `gh` received the body.

## What the fix was
Rewrite the PR body from a file using `gh pr edit --body-file`, avoiding shell interpolation of Markdown.

## Prevention rule
When passing Markdown containing backticks, `$`, or command-looking text to shell CLIs, write it to a file and use `--body-file`/equivalent instead of inline double-quoted arguments.

## Context
Creating a DiffViewer Architecture View PR with Markdown body containing inline code spans like `/api/architecture`, `analysis.json`, and branch names.
