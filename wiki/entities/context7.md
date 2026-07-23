---
title: "Context7"
type: entity
tags: [documentation, mcp, context7, live-docs, ai-agents, upstash]
sources: []
created: 2026-06-29
updated: 2026-06-29
---

# Context7

Live library documentation fetching service by Upstash. Pulls version-specific docs and code examples into AI agent context on demand, eliminating hallucinated or outdated API calls.

## Two Delivery Modes

| Mode | Endpoint / Package | Auth |
|---|---|---|
| **MCP server** | `https://mcp.context7.com/mcp` | `CONTEXT7_API_KEY` custom header |
| **ctx7 CLI** | `npm install -g ctx7` | `CONTEXT7_API_KEY` env var |

Both modes access the same upstream doc index; prefer MCP when the agent harness supports it natively, ctx7 CLI as fallback.

## Per-Platform Usage

| Platform | Integration | Notes |
|---|---|---|
| Claude Code | `context7@claude-plugins-official` plugin; tools available as `mcp__context7__*` | Also available via plugin:context7 namespace |
| Opencode | Remote MCP in `opencode.json`; `CONTEXT7_API_KEY` custom header | Declared under `mcpServers` |
| Codex | `context7@claude-plugins-official` plugin in `~/.codex/config.toml` | Same plugin as CC |
| Pi | `@upstash/context7-pi` extension + `ctx7` CLI fallback | Extension preferred; CLI when extension unavailable |
| OMP | `ctx7` CLI | No native MCP plugin; CLI-only |

Cross-platform setup: [[comparisons/cc-to-cross-platform-migration]] (MCP layer section). MCP ecosystem overview: [[comparisons/our-stack-vs-omp]].

## MCP Tools Reference

Two tools, always invoked in sequence:

| Tool | Input | Output |
|---|---|---|
| `resolve-library-id` | `{libraryName, query}` | Context7-compatible library ID (e.g. `/vercel/next.js`) |
| `query-docs` | `{libraryId, query}` | Docs text + code snippets for the query |

In Claude Code these surface as `mcp__context7__resolve-library-id` and `mcp__context7__query-docs`.

Usage pattern:
```
1. resolve-library-id: {libraryName: "next.js"}
   → returns: /vercel/next.js

2. query-docs: {libraryId: "/vercel/next.js", query: "app router middleware"}
   → returns: current docs excerpt + code examples
```

## CLI Commands Reference

```sh
# Resolve library name to Context7 ID
ctx7 library <name> "<query>" [--json]

# Fetch docs for a resolved ID
ctx7 docs /<org>/<project> "<query>" [--json]
```

`--json` returns structured output suitable for piping into scripts.

## REST API Reference

For scripting or non-MCP/CLI integrations.

**Auth**: `Authorization: Bearer <CONTEXT7_API_KEY>` on both endpoints.

| Operation | Request | Response shape |
|---|---|---|
| Search libraries | `GET https://context7.com/api/v2/libs/search?libraryName=<n>&query=<q>` | `{results: [{id, title, ...}]}` |
| Fetch docs | `GET https://context7.com/api/v2/context?libraryId=<id>&query=<q>` | Plain text docs |

## When to Use / When to Skip

**Use before**: implementing any library API, framework feature, CLI tool invocation, or external API call where flag/method names could have changed.

**Skip for**: pure reasoning tasks, git operations, file manipulation with no external library dependency, standard Unix tools (ls, grep, cat).

The CLAUDE.md rule (always-loaded): "Before using any library, framework, CLI tool, or API — resolve current docs via context7 MCP." Applied in this repo on every ingest that touches a library.

Similar tool (wiki search, not doc fetch): [[entities/qmd]].

Wrapped as one of three surfaces (alongside web/code search) in [[entities/ketch]]'s `ketch docs` command — same resolve → fetch flow, unified under a single agent-facing CLI.

## Key Storage and Rotation

Single source of truth: `~/secrets/.env`

Synced to:
- `~/.claude/.env` (Claude Code)
- `~/.config/opencode/.env` (Opencode)

Variable name: `CONTEXT7_API_KEY`. Rotate at [context7.com](https://context7.com), then update all three locations.

## Related Packages

| Package | Role |
|---|---|
| `@upstash/context7-mcp` | npm package backing the MCP server |
| `ctx7` | CLI tool (`npm install -g ctx7`) |
| `@upstash/context7-sdk` | Programmatic JS/TS SDK |
| `@upstash/context7-pi` | Pi extension for native integration |
