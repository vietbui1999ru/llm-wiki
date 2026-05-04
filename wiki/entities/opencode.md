---
title: "OpenCode"
type: entity
tags: [agent-harness, plugins, CLI, compaction, alternative-to-claude-code]
sources: ["Plugins for Opencode.md"]
created: 2026-05-04
updated: 2026-05-04
---

# OpenCode

Open-source AI coding CLI (opencode.ai). Direct competitor to Claude Code. Plugin system built with Bun/TypeScript; substantially more extensible than Claude Code's hook system for certain use cases — especially compaction control.

---

## Plugin System Architecture

Plugins are JS/TS modules, loaded from:
1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin dir (`~/.config/opencode/plugins/`)
4. Project plugin dir (`.opencode/plugins/`)

npm plugins auto-install at startup via Bun. Local plugins load directly. Duplicate npm packages (same name + version) are deduplicated; local and npm plugins with similar names both load.

```typescript
export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => { /* intercept tool calls */ },
    "session.compacted": async (event) => { /* react to compaction */ },
    // ...more hooks
  }
}
```

---

## Event Surface

Claude Code hooks cover: PreToolUse, PostToolUse, Stop, Notification. OpenCode exposes a much broader surface:

**Tool events**: `tool.execute.before`, `tool.execute.after`
**Session events**: `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`
**File events**: `file.edited`, `file.watcher.updated`
**LSP events**: `lsp.client.diagnostics`, `lsp.updated`
**TUI events**: `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`
**Shell events**: `shell.env`
**Permission events**: `permission.asked`, `permission.replied`
**Todo events**: `todo.updated`

---

## Compaction Hooks — Key Differentiator

OpenCode exposes `experimental.session.compacting`, which fires before the LLM generates a continuation summary. Plugins can:

1. **Inject additional context** (`output.context.push(...)`) — domain-specific state the default compaction prompt would miss
2. **Replace the entire compaction prompt** (`output.prompt = "..."`) — full control over what survives context compression

```typescript
"experimental.session.compacting": async (input, output) => {
  output.context.push(`
## Active Task Status
Currently implementing: payment webhook handler
Files modified: src/webhooks/stripe.ts, src/models/payment.ts
Next: write integration tests
  `)
}
```

Claude Code has no equivalent. This is the most significant architectural difference. See [[comparisons/claude-code-vs-opencode-plugins]].

---

## Custom Tools

Plugins can register tools that become available to the AI alongside built-in tools:

```typescript
tool: {
  mytool: tool({
    description: "...",
    args: { foo: tool.schema.string() },
    async execute(args, context) { return `result` }
  })
}
```

Claude Code's equivalent is MCP server registration — a heavier setup. OpenCode makes custom tools a first-class plugin concern.

---

## Relation to Existing Wiki

- [[comparisons/claude-code-vs-opencode-plugins]] — side-by-side plugin architecture comparison
- [[concepts/context-compression]] — OpenCode's compaction hook directly extends this concept
- [[concepts/agent-harness]] — OpenCode is a complete harness implementation; compare components
- [[entities/ai-coding-agents]] — OpenCode is part of the AI coding agent ecosystem
- [[concepts/claude-code-plugins]] — Claude Code's plugin system (what OpenCode extends)
