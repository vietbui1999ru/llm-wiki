---
title: "Claude Code vs OpenCode Plugin Systems"
type: comparison
tags: [claude-code, opencode, plugins, hooks, compaction, harness-design]
sources: ["Plugins for Opencode.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Claude Code vs OpenCode Plugin Systems

Side-by-side comparison of hook/plugin extensibility between Claude Code (Anthropic) and OpenCode (opencode.ai).

---

## Architecture Comparison

| Dimension | Claude Code | OpenCode |
|---|---|---|
| Extension format | Shell commands in `settings.json` | JS/TS modules (npm or local files) |
| Install mechanism | Manual config edit | npm auto-install (Bun) at startup |
| Hook surface | PreToolUse, PostToolUse, Stop, Notification | 30+ events across tools, sessions, files, LSP, TUI |
| Compaction control | None (not exposed) | `experimental.session.compacting` hook — inject context or replace entire prompt |
| Custom tools | Via MCP server (separate setup) | Native plugin registration |
| Env var injection | Via shell hook | `shell.env` hook |
| File protection | Via PreToolUse hook | `tool.execute.before` + explicit check |
| Load order | Settings hierarchy | Global config → project config → global dir → project dir |
| Language constraint | Any (shell) | JavaScript/TypeScript |
| State access | None (pure side effects) | `client`, `project`, `$` (Bun shell), `directory`, `worktree` |

---

## Compaction Hook — The Key Differentiator

OpenCode's `experimental.session.compacting` hook fires before the LLM generates a continuation summary. No Claude Code equivalent exists.

**Use case 1 — Inject domain state:**
```typescript
"experimental.session.compacting": async (input, output) => {
  output.context.push(`
## Task State
Currently implementing: auth middleware refactor
Files in progress: src/auth/middleware.ts, src/auth/session.ts
Last completed: extracted session validation to SessionService
Next: add rate limiting
  `)
}
```

**Use case 2 — Replace entire compaction prompt:**
```typescript
"experimental.session.compacting": async (input, output) => {
  output.prompt = `
You are generating a continuation for a multi-agent task.
Summarize: current task, files modified, blockers, next steps.
Format for a new agent to resume work immediately.
  `
}
```

This allows implementing custom [[concepts/context-compression]] strategies (anchored iterative summarization, opaque compression) at the harness level, not the system prompt level. Claude Code users must approximate this via CLAUDE.md instructions to the model — less reliable because the model can ignore prose instructions under context pressure.

---

## Custom Tools

**Claude Code approach**: Register an MCP server, configure it in settings, start it as a separate process. Full tool available to the model.

**OpenCode approach**: Declare a tool inside a plugin module, automatically available on next startup:

```typescript
tool: {
  mytool: tool({
    description: "Fetch PR status from Linear",
    args: { prId: tool.schema.string() },
    async execute(args, { directory }) {
      // linear API call
      return JSON.stringify(result)
    }
  })
}
```

OpenCode's approach is lower friction for simple custom tools; MCP is better for complex, reusable tool servers.

---

## Event Coverage

Claude Code's four events (PreToolUse, PostToolUse, Stop, Notification) cover the core tool execution loop. OpenCode's 30+ events cover the full session lifecycle — including LSP diagnostics, TUI interactions, and permission decisions. This matters for:

- **Observability**: react to `session.diff` to log what the agent changed
- **Security**: intercept `permission.asked` to audit what the agent is requesting
- **Integration**: fire on `file.edited` to trigger external sync

For most developer workflows, Claude Code's four events are sufficient. OpenCode's broader surface is useful for building production harnesses or complex integrations.

---

## When to Use Each

**Claude Code hooks** are sufficient for:
- Pre/post tool filtering and logging
- Stop-event notifications
- Simple env var injection via shell hooks

**OpenCode plugins** add value for:
- Custom compaction strategies (inject task state into context summaries)
- Custom tools without MCP overhead
- Observability hooks (session diffs, LSP diagnostics)
- Multi-agent session coordination via session events

---

## Related Pages

- [[entities/opencode]] — OpenCode entity page
- [[concepts/claude-code-plugins]] — Claude Code plugin system detail
- [[concepts/context-compression]] — what compaction hooks extend
- [[concepts/agent-harness]] — both systems are harness implementations
