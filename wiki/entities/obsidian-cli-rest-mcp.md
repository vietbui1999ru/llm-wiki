---
title: "Obsidian CLI REST MCP"
type: entity
tags: [obsidian, mcp, rest-api, agentic-vault-access, code-mode]
sources: ["Obsidian CLI REST MCP (developassion).md"]
created: 2026-07-01
updated: 2026-07-01
---

# Obsidian CLI REST MCP

Community plugin (by Sebastien Dubois, dsebastien.net; MIT licensed) that wraps [[entities/obsidian-cli]] as a local HTTP API and MCP server, so scripts and AI assistants don't have to shell out to the `obsidian` binary per call.

## How it works

- Requires the official CLI already installed on `$PATH` and Obsidian 1.4.0+
- Installed as an Obsidian community plugin; starts an HTTP server automatically on `http://127.0.0.1:27124`
- **REST API**: every CLI command is available at `/api/v1/cli/*`, Bearer-token authenticated (auto-generated API key, copyable from plugin settings)
- **MCP server**: same HTTP server, `/mcp` path, StreamableHTTP transport (stateless, request-per-connection)

## The Code Mode pattern (2 tools, not 100+)

Rather than registering one MCP tool per CLI command — which would dump 100+ tool definitions into every agent's context — the server exposes exactly two:

- **`search`** — discover commands by name/description/category (`{query?, category?}`); always returns the full category list so the agent knows what to explore next
- **`execute`** — run any command by name (`{command, vault?, params?, flags?}`), colon notation (`daily:append`, `property:set`)

Recommended agent loop: `search()` for an overview → `search(category: "daily")` to narrow → `execute(command: "help", params: {command: "daily:append"})` to learn parameters → `execute(command: "daily:append", params: {...})` to run it. This progressive-discovery shape keeps token overhead flat regardless of how many underlying commands exist — a pattern worth reusing anywhere a tool surface is large and mostly-unused per session (see [[concepts/tool-design-for-agents]]).

## Safety controls

Per-command blocklist (blocked commands are hidden from `search` and error from `execute`) plus a separate `allowDangerousCommands` gate for the ~15 commands marked "Dangerous" in the reference (`eval`, `dev:*`, `reload`, `restart`, `command`, `plugins:restrict`) — mirrors the CLI's own eval-is-risky guidance in [[entities/obsidian-cli]].

## Setup (Claude Code)

```json
{
  "mcpServers": {
    "obsidian": {
      "type": "url",
      "url": "http://127.0.0.1:27124/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

## Positioning vs. the other integration paths

*(community plugin — single-source claim, not independently cross-verified; re-check current install/adoption status before depending on it)*

- vs. raw [[entities/obsidian-cli]]: same command surface, but no subprocess-per-call overhead and works over HTTP (remote/headless-friendly) instead of requiring a local shell
- vs. [[entities/obsidian-claude-code-mcp]]: different plugin, different transport (StreamableHTTP here vs. WebSocket there), different port (27124 vs. 22360) — appear to be two independent community solutions to the same problem rather than the same project under two names

## Related

- [[entities/obsidian-cli]] — the underlying CLI this plugin wraps
- [[entities/obsidian-claude-code-mcp]] — the alternate WebSocket-based bridge
- [[concepts/tool-design-for-agents]] — the search+execute "Code Mode" pattern as a general large-tool-surface strategy
