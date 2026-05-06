---
title: "OpenCode"
type: entity
tags: [agent-harness, plugins, CLI, compaction, alternative-to-claude-code]
sources: ["Plugins for Opencode.md", "Agents-opencode.md", "Rules.md"]
created: 2026-05-04
updated: 2026-05-06
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

## Agent Model

OpenCode distinguishes three modes:

**Primary agents** (user-selectable via Tab/`switch_agent`): `Build` (all tools, default) and `Plan` (read-only, file edits and bash set to `ask`).

**Subagents** (invoked via `@name` or by primary agents via Task tool): `General` (full tools, for parallel multi-step work) and `Explore` (read-only, fast codebase search).

**Hidden agents** (system-managed, not user-selectable): `compaction`, `title`, `summary`. Can still be invoked programmatically via the Task tool.

Custom agents: defined in `opencode.json` or as markdown files in `~/.config/opencode/agents/` (global) or `.opencode/agents/` (per-project). Markdown file name becomes agent name. Key options: `mode` (primary/subagent/all), `model`, `temperature`, `steps` (max iterations), `permission`, `hidden`, `color`.

### Permission System

Per-tool permissions: `allow`, `ask`, `deny`. Can be set globally or per-agent, with bash command glob patterns:

```json
"permission": {
  "bash": { "*": "ask", "git status *": "allow" }
}
```

Available permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `todowrite`, `webfetch`, `websearch`, `lsp`, `skill`, `question`, `doom_loop`.

### `{file:./path}` Prompt Injection

Agent prompts can reference external files:

```json
{ "prompt": "{file:./prompts/build.txt}" }
```

Path is relative to the config file location — works for both global and project-level configs.

---

## AGENTS.md Support

OpenCode reads AGENTS.md natively with the following precedence (per directory):

```
AGENTS.md > CLAUDE.md
```

Global: `~/.config/opencode/AGENTS.md` > `~/.claude/CLAUDE.md`

Claude Code compatibility can be disabled:
```bash
OPENCODE_DISABLE_CLAUDE_CODE=1        # disable all .claude support
OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1 # disable only ~/.claude/CLAUDE.md
OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 # disable only skills
```

### Multi-file Instructions via `opencode.json`

The `instructions` field escapes the single-file limitation — accepts glob patterns and remote URLs:

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md",
    "https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"
  ]
}
```

All instruction files are combined with AGENTS.md. Remote instructions fetched with 5-second timeout.

---

## Relation to Existing Wiki

- [[comparisons/claude-code-vs-opencode-plugins]] — side-by-side plugin architecture comparison
- [[concepts/context-compression]] — OpenCode's compaction hook directly extends this concept
- [[concepts/agent-harness]] — OpenCode is a complete harness implementation; compare components
- [[entities/ai-coding-agents]] — OpenCode is part of the AI coding agent ecosystem
- [[concepts/claude-code-plugins]] — Claude Code's plugin system (what OpenCode extends)
