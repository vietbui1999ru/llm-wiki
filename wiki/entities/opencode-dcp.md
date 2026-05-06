---
title: "opencode-dcp"
type: entity
tags: [opencode, plugin, npm, context-management]
sources:
  - "Opencode-DCPopencode-dynamic-context-pruning Dynamic context pruning plugin for OpenCode - intelligently manages conversation context to optimize token usage.md"
  - "Quick Start Install DCP Plugin  opencode-dynamic-context-pruning.md"
created: 2026-05-06
updated: 2026-05-06
---

# opencode-dcp

Published [[entities/opencode]] plugin that implements [[concepts/dynamic-context-pruning]]. Reduces token usage in long sessions by rewriting outgoing LLM requests — replaces stale content with placeholders without modifying session history on disk.

## Identity

- **npm package**: `@tarquinen/opencode-dcp`
- **GitHub org**: `Opencode-DCP`
- **Repo**: `Opencode-DCP/opencode-dynamic-context-pruning`
- **Author handle**: `tarquinen`
- **Docs site**: `opencodedocs.com/Opencode-DCP/opencode-dynamic-context-pruning/`

## Install

```bash
opencode plugin @tarquinen/opencode-dcp@latest --global
```

Or manually add to `opencode.jsonc`:

```jsonc
{
  "plugin": ["@tarquinen/opencode-dcp@latest"]
}
```

Restart OpenCode. Verify with `/dcp`.

## Key Mechanisms (one-line each)

- **Compress** — model-driven `compress` tool that summarizes closed conversation spans (`range` or experimental `message` mode)
- **Deduplication** — automatic; on LLM fetch, keeps only the most recent output for identical (tool, args) pairs
- **Purge Errors** — automatic; prunes the input of errored tool calls after N turns (default 4), keeps the error message

## Config File Locations

DCP-specific config (separate from `opencode.jsonc`), searched in order, later overrides earlier:

1. `~/.config/opencode/dcp.jsonc` — global (auto-created on first run, contains only `$schema` initially)
2. `$OPENCODE_CONFIG_DIR/dcp.jsonc` — when env var is set
3. `.opencode/dcp.jsonc` — project-local

`.json` variants are also accepted at every level.

## Default Protected Tools

`task`, `skill`, `todowrite`, `todoread`, `compress`, `batch`, `plan_enter`, `plan_exit`, `write`, `edit`

## Slash Commands

`/dcp`, `/dcp context`, `/dcp stats`, `/dcp sweep [n]`, `/dcp manual [on|off]`, `/dcp compress [focus]`, `/dcp decompress <n>`, `/dcp recompress <n>`

## Logs

`~/.config/opencode/logs/dcp/daily/` — when `debug: true` is set in config.

## Related Pages

- [[concepts/dynamic-context-pruning]] — what it does and why
- [[summaries/opencode-dcp]] — full source synthesis
- [[entities/opencode]] — host harness
