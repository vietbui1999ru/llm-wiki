---
date: 2026-10-23
type: cli-flag
domain: zsh
severity: low
---

# zsh `=` expansion broke an `echo =====` separator again (third hit)

## What happened
Ran `sed ... README.md; echo =====; sed ... README.md` in the Bash tool. zsh read `=====` as `=command` expansion and failed with `(eval):1: ==== not found`, so the second file was never printed.

## What the fix was
Quote the separator (`echo '-----'`) or use dashes, or run the two reads as separate tool calls.

## Prevention rule
Already in global-prevention-rules.md (CLI / Shell, 2026-10-21): quote any word starting with `=`. This is a repeat, so the rule is not being applied when typing ad-hoc separators; prefer separate parallel tool calls over echo separators.

## Context
Reading the V3 and V5 phase READMEs while implementing the core rev 9 consolidation in personal-ai-gateway.
