---
title: "OpenCode Plugins Overview"
type: summary
tags: [opencode, plugins, extensibility, compaction, custom-tools, npm]
sources:
  - "Plugins for Opencode.md"
created: 2026-05-25
updated: 2026-05-25
---

# OpenCode Plugins Overview

Official docs for writing and loading OpenCode plugins. Covers plugin loading, event surface, custom tools, and compaction hooks.

Source: opencode.ai docs. See [[entities/opencode]] for the full entity page.

---

## Loading Plugins

Two mechanisms:

**Local files**: place JS/TS in plugin directories — auto-loaded at startup.

**npm packages**: list in `opencode.json`:
```json
{ "plugin": ["opencode-helicone-session", "opencode-wakatime", "@my-org/custom-plugin"] }
```

npm plugins install automatically via Bun at startup; cached at `~/.cache/opencode/node_modules/`.

### Load Order

1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin dir (`~/.config/opencode/plugins/`)
4. Project plugin dir (`.opencode/plugins/`)

Duplicate npm packages (same name + version) deduplicated. Local + npm plugins with similar names both load separately.

---

## Plugin Structure

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => { /* intercept tool calls */ },
    "session.compacted": async (event) => { /* react to compaction */ },
  }
}
```

Context object fields: `project`, `client` (opencode SDK), `$` (Bun shell API), `directory`, `worktree`.

**Dependencies**: add `package.json` to config dir; OpenCode runs `bun install` at startup.

---

## Event Surface

Full event list by category:

- **Tool**: `tool.execute.before`, `tool.execute.after`
- **Session**: `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`
- **File**: `file.edited`, `file.watcher.updated`
- **Message**: `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated`
- **LSP**: `lsp.client.diagnostics`, `lsp.updated`
- **TUI**: `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`
- **Shell**: `shell.env`
- **Permission**: `permission.asked`, `permission.replied`
- **Todo**: `todo.updated`
- **Command**: `command.executed`
- **Installation**: `installation.updated`
- **Server**: `server.connected`

Claude Code hooks cover: PreToolUse, PostToolUse, Stop, Notification. OpenCode's surface is substantially broader.

---

## Key Plugin Patterns

### .env Protection

```javascript
export const EnvProtection = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    },
  }
}
```

### Env Variable Injection

```javascript
"shell.env": async (input, output) => {
  output.env.MY_API_KEY = "secret"
  output.env.PROJECT_ROOT = input.cwd
}
```

Injects into all shell execution — both AI tools and user terminals.

### Custom Tools

```typescript
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "...",
        args: { foo: tool.schema.string() },
        async execute(args, context) {
          return `Hello ${args.foo} from ${context.directory}`
        },
      }),
    },
  }
}
```

Custom tools become available to the AI alongside built-in tools. Claude Code equivalent: MCP server registration (heavier setup).

---

## Compaction Hooks — Key Differentiator

`experimental.session.compacting` fires before the LLM generates a continuation summary.

**Inject additional context**:
```typescript
"experimental.session.compacting": async (input, output) => {
  output.context.push(`
## Active Task Status
Currently implementing: payment webhook handler
Files modified: src/webhooks/stripe.ts
Next: write integration tests
  `)
}
```

**Replace the entire prompt**:
```typescript
"experimental.session.compacting": async (input, output) => {
  output.prompt = `You are generating a continuation prompt...`
}
```

When `output.prompt` is set, it completely replaces the default compaction prompt; `output.context` is ignored.

Claude Code has no equivalent hook. This is the most significant architectural difference between the two tools. See [[entities/opencode]] and [[comparisons/claude-code-vs-opencode-plugins]].

---

## Logging

Use `client.app.log()` instead of `console.log` for structured logging. Levels: `debug`, `info`, `warn`, `error`.

---

## Community Plugins

Browse at opencode.ai/docs/ecosystem#plugins. No official plugin registry at time of source.

---

## Related Pages

- [[entities/opencode]] — full entity page: plugin architecture, agent model, config system, AGENTS.md
- [[entities/opencode-dcp]] — DCP plugin (if page exists)
- [[comparisons/claude-code-vs-opencode-plugins]] — side-by-side comparison of hook/plugin architectures
- [[concepts/context-compression]] — compaction strategies; OpenCode's hook directly extends this
