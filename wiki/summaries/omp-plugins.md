---
title: "omp Plugin System"
type: summary
tags: [omp, pi, plugin, extension, hook, custom-tool, mcp, marketplace]
sources: ["omp.sh/docs/plugins (ingested 2026-06-18)"]
created: 2026-06-18
---

# omp Plugin System

omp (oh-my-pi) supports a unified plugin format that bundles skills, commands, hooks, custom tools, MCP servers, and themes in a single installable package. The surface is Claude-Code-compatible — existing `.claude-plugin/` catalogs work as-is.

## Commands

| Command | Effect |
|---|---|
| `omp install <source>` | Install plugin into `~/.omp/plugins/` |
| `omp remove <name>` | Uninstall and unregister surfaces |
| `omp update [name]` | Re-fetch one or all plugins |
| `omp list` | Show installed plugins with source, version, scope |
| `omp install -l <source>` | Project-scoped install into `.omp/plugins/` |

Sources: npm package (`@scope/plugin`), Git repo (`github:user/repo`), local path (`./path`), marketplace (`name@catalog`).

## Plugin Layout

```
my-plugin/
  plugin.json              # name, version, description, entry points
  skills/<name>/SKILL.md   # on-demand playbooks
  commands/<name>.md       # slash-command prompt templates
  hooks/pre/*.ts           # lifecycle handlers (blocking/rewriting)
  hooks/post/*.ts
  tools/<name>/index.ts    # custom tools (TypeBox/Zod schema)
  mcp.json                 # extra mcpServers entries
  themes/<name>.json       # color palettes
  README.md
```

At install time, omp merges each subdirectory into its corresponding discovery surface. Uninstall reverses everything.

## Hook Surfaces

| Event | Return Contract | Use Case |
|---|---|---|
| `tool_call` | `{ block: true, reason }` | Gate dangerous commands (e.g. `rm -rf`) |
| `tool_result` | `{ content?, details?, isError? }` | Redact secrets, rewrite output |
| `context` | `{ messages }` | Replace message array before provider call |
| `session_before_compact` | `{ cancel: true }` | Veto compaction |
| `session_start`, `turn_start`, etc. | observational | Telemetry, logging |

HookAPI is the narrow event-handler surface. ExtensionAPI is the superset that also registers commands, tools, renderers.

## Custom Tools

Default-export a factory receiving `(pi)` with injected `pi.zod`. Fields:

| Field | Purpose |
|---|---|
| `name` | Tool name (must not collide with built-ins) |
| `label` | Human-readable TUI label |
| `description` | What the model sees when deciding to call |
| `parameters` | Zod/TypeBox schema |
| `execute` | Async handler; forward `signal` for cancellation |
| `renderCall` / `renderResult` | Optional TUI custom renderers |

## Discovery Paths

| Scope | Hooks | Tools |
|---|---|---|
| Global | `~/.omp/agent/hooks/pre/*.ts` | `~/.omp/agent/tools/<name>/index.ts` |
| Project | `.omp/hooks/pre/*.ts` | `.omp/tools/<name>/index.ts` |
| Plugin | Merged at install time | Merged at install time |

`.claude/tools/` and `.codex/tools/` are also picked up for cross-tool compatibility.

## Security

Plugins run arbitrary TypeScript on every turn. Audit before installing: read `hooks/` and `tools/`, skim `mcp.json`. Prefer project-scoped installs (`-l`) for unvetted code. Pin to specific Git tags or npm versions.

## Example: Headroom Compression Plugin

See `pi-headroom/` in this repo for a working plugin that:
- Registers a `context` hook for transparent compression
- Registers a `headroom_retrieve` custom tool for on-demand decompression
- Uses Headroom's CCR (Compress-Cache-Retrieve) for reversible 60–95% token reduction

## Related

- [[entities/omp]] — full omp entity page
- [[entities/pi-agent]] — upstream pi-mono; same plugin surface
- [[comparisons/our-stack-vs-omp]] — feature gap analysis
