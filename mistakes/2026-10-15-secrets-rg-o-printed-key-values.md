---
date: 2026-10-15
type: tool-misuse
domain: secrets / ripgrep
severity: high
---

# `rg -o` with a trailing `.*` printed two full API keys from ~/secrets/.env

## What happened
To "show the definition line shape without the value" the command used `rg -o -e "^\s*(export\s+)?ANTHROPIC_API_KEY=" -e "^\s*#.*ANTHROPIC_API_KEY.*" ~/secrets/.env`. The second pattern ended in `.*`, and `-o` prints the whole match, so both commented-out lines were output with their key values (`ANTHROPIC_API_KEY` and `ANTHROPIC_API_KEY_WIKI`). The keys landed in the session transcript.

## What the fix was
Disclosed it to the user immediately, told them to revoke both keys, deleted the two lines by line number (`sed -i '' '4,5d'`) and from then on matched names only (`rg -o '^ANTHROPIC[A-Z_]*'`, `cut -c1-22`, `awk` printing pids).

## Prevention rule
When inspecting a secrets file or an environment for a credential, never use a pattern that can match past the variable name. Print names or lengths only: `rg -o '^NAME'`, `cut -c1-N`, `wc -c`, or `awk` printing a pid. A `.*` after the name with `-o` (or any match-printing mode) leaks the value. Commented-out lines still hold live keys.

## Context
Task was to find why `ANTHROPIC_API_KEY` was set in every Claude session despite being commented out in `~/secrets/.env`.
