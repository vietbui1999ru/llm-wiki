---
date: 2026-10-21
type: cli-flag
domain: zsh
severity: low
---

# Unquoted `======` separator aborts a zsh command

## What happened
A Bash-tool command used `echo ======` as an output separator. The tool's shell is zsh, where an unquoted word starting with `=` is `=command` path expansion, so zsh failed with `(eval):1: ===== not found` and skipped the rest of the command.

## What the fix was
Quote the separator (`echo '====='`) or use one that does not start with `=` (`echo '---'`).

## Prevention rule
In zsh commands, quote any word that starts with `=` (separators, `=value` arguments); unquoted it becomes a command-path lookup.

## Context
Debugging a Pi 400 error (pi-lens injecting a one-shot message) in the dotfiles repo; the separator sat between two `sed`/`rg` reads of pi-lens's bundled `dist/index.js`. The PostToolUseFailure hook reported the bash/not-found pattern 3 times in 14 days.
