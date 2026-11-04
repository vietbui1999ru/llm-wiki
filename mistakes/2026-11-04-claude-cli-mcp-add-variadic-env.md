---
date: 2026-11-04
type: cli-flag
domain: claude-cli
severity: low
---

# `claude mcp add -e` is variadic and swallows the server name

## What happened
Ran `claude mcp add -s user -e WIKI_ROOT=... wiki-ops -- <cmd>`. The variadic `-e/--env` option consumed `wiki-ops` as a second env value, and the CLI failed with `missing required argument 'commandOrUrl'`. Before that, plain `claude` failed in the agent shell with `command not found: _with_mcp_keys`, because `claude` is an interactive zsh wrapper function.

## What the fix was
Put the server name before any variadic option: `claude mcp add wiki-ops -s user -e KEY=VALUE -- <cmd>`. In agent shells call the binary by path (`/Users/vietquocbui/.local/bin/claude`), not the wrapper.

## Prevention rule
Place positional arguments before variadic options (`-e`, `--env`, `--header`), or end the option list with `--`. In agent shells, resolve a CLI to its binary path when the interactive name is a wrapper function.

## Context
Registering the new `wiki-ops` MCP server (PR #79) at Claude user scope after merging the wiki ops wiring.
