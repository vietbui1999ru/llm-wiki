---
title: "obsidian-claude-code-mcp"
type: entity
tags: [obsidian, mcp, claude-code, agentic-vault-access, websocket]
sources: ["The Obsidian CLI Complete Guide - Frank Anaya.md"]
status: stub
created: 2026-07-01
updated: 2026-07-01
---

# obsidian-claude-code-mcp

A community Obsidian plugin ("Claude Code MCP" in the Community Plugins browser) implementing an MCP server inside Obsidian that Claude Code connects to automatically over **WebSocket** — no manual HTTP config needed from the Claude Code CLI side.

*(single-source claim from a third-party guide, not independently verified — re-check the plugin still exists/is maintained before depending on it)*

## Setup (as described in the source)

1. In Obsidian: Community Plugins → Browse → "Claude Code MCP" → Install → Enable
2. Claude Desktop: add to `claude_desktop_config.json` — `{"mcpServers": {"obsidian": {"command": "npx", "args": ["mcp-remote", "http://localhost:22360/sse"]}}}`
3. Claude Code CLI: launch `claude`, run `/ide` → select Obsidian → auto-connects via WebSocket
4. Test: `claude "How many notes are in my vault and what are my top 5 tags?"`

## Why this is the better fit for agentic-spec workflows

Unlike shelling out to [[entities/obsidian-cli]] per command or hitting [[entities/obsidian-cli-rest-mcp]]'s HTTP server, this path gives Claude Code a standing, no-subprocess connection to the live vault — read/search/write happen as ordinary MCP tool calls inside the same session, no per-command process spawn. For a vault used as the source of truth for agentic-coding spec notes (planning, implementation, review, PR, design, docs, architecture), this is the natural way to let an agent open/query/update those notes mid-session rather than scripting around the CLI.

## Related

- [[entities/obsidian-cli]] — the underlying CLI; this plugin is one of at least two MCP bridges built on the same idea
- [[entities/obsidian-cli-rest-mcp]] — the other, independently-built MCP bridge (HTTP/StreamableHTTP instead of WebSocket)
- [[concepts/cli-driven-vault-automation]] — automation patterns for the non-MCP, script/cron side of this ecosystem

*Stub — expand once this plugin is actually installed and tested against a real vault (current pass is guide-sourced only).*
