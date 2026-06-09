---
title: "Gemini CLI"
type: entity
tags: [gemini, cli, agent, cross-platform, tools, skills, hooks]
sources:
  - "Gemini CLI documentation.md"
  - "Provide context with GEMINI.md files.md"
  - "Gemini CLI Custom slash commands  Google Cloud Blog.md"
  - "Custom commands.md"
  - "Tools reference.md"
created: 2026-05-07
updated: 2026-05-27
---

# Gemini CLI

Google's open-source CLI for the Gemini model family. Significantly more capable than early wiki assessments suggested — has native equivalents for most CC features.

**Install:** `npm install -g @google/gemini-cli`

---

## Feature Parity with Claude Code

| CC Feature | Gemini Equivalent | Parity |
|---|---|---|
| `CLAUDE.md` rules | `GEMINI.md` hierarchical discovery | High |
| `@file.md` imports | `@file.md` imports (same syntax) | High |
| Skills | `activate_skill` tool + `.gemini/skills/` | High |
| Custom commands | TOML files in `.gemini/commands/` | High |
| Subagents | Experimental subagents | Medium |
| Hooks | Hooks support | Medium |
| Headless mode | Headless mode (`--headless`) | High |
| Sandboxing | Sandboxing (containerized) | Medium |
| MCP servers | MCP servers (HTTP + stdio) | High |
| Plan mode | `enter_plan_mode` tool | High |

---

## Context System: GEMINI.md

Hierarchical instruction loading:

1. `~/.gemini/GEMINI.md` — global, all sessions
2. Project-root `GEMINI.md` — workspace scope
3. Subdirectory `GEMINI.md` — JIT loaded when agent navigates into dir

Supports `@file.md` imports (relative paths). `/memory add <text>` appends to global file.

`context.fileName` in `settings.json` can be configured to also read `["AGENTS.md", "GEMINI.md"]`, making Gemini natively read AGENTS.md files.

---

## Custom Commands: TOML Format

`.toml` files in `.gemini/commands/` (project) or `~/.gemini/commands/` (global).

```toml
description = "Reviews a pull request."
prompt = """
Review PR: {{args}}
Run: !{git log --pretty=format:"%s" -n 5}
"""
```

**Syntax features:**
- `{{args}}` — user arguments injected into prompt (raw outside `!{}`, shell-escaped inside)
- `!{command}` — shell command executed, output injected; security confirmation required
- `@{path/to/file}` — file content injected into prompt (processed before `!{}`)
- Namespacing: `.gemini/commands/git/commit.toml` → `/git:commit`
- MCP prompts also appear as slash commands

---

## Skills: `activate_skill` Tool

Gemini has a native skill system via the `activate_skill` tool. Skills live in `.gemini/skills/` directory. When triggered, Gemini loads the skill's instructions into context (same progressive disclosure principle as CC).

```
/tools             # List all tools including activate_skill
```

**Key difference from CC**: Gemini uses `activate_skill` as a native tool; CC uses the `Skill` meta-tool with `isMeta: true` message injection.

---

## Built-in Tool Set

Full list from official docs:

| Tool | Category | Description |
|---|---|---|
| `run_shell_command` | Execute | Arbitrary shell; manual confirmation |
| `glob`, `grep_search`, `list_directory` | Search/Read | File navigation |
| `read_file`, `read_many_files` | Read | File content; `@` shorthand |
| `write_file`, `replace` | Edit | File modification; confirmation |
| `ask_user`, `write_todos` | Interaction | Clarification, task tracking |
| `save_memory` | Memory | Persists to GEMINI.md |
| `activate_skill` | Memory | Loads skill from `.gemini/skills/` |
| `get_internal_docs` | Memory | Accesses Gemini CLI own docs |
| `enter_plan_mode`, `exit_plan_mode` | Planning | Read-only planning phase |
| `google_web_search`, `web_fetch` | Web | Search + URL fetch |
| `list_mcp_resources`, `read_mcp_resource` | MCP | MCP server integration |
| Tracker tools (`tracker_*`) | Experimental | Task graph tracking |

Shell shorthand: `!command` runs `run_shell_command`. `@path` triggers `read_many_files`.

---

## Migration Mapping (CC → Gemini)

| CC asset | Gemini equivalent |
|---|---|
| `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` |
| `claude-setup/rules/*.md` | Same files, referenced via `@rules/*.md` imports |
| `claude-setup/skills/*/SKILL.md` | `.gemini/skills/*/SKILL.md` + `activate_skill` |
| `.claude/commands/*.toml` | `.gemini/commands/*.toml` (same format) |
| `claude-setup/agents/*.md` | Experimental subagents (not production-ready) |
| `templates/AGENTS.md` | Not natively read; use GEMINI.md or configure `context.fileName` |

## Related Pages

- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[entities/agents-md-format]] — AGENTS.md; Gemini can be configured to read it
- [[concepts/agent-skills]] — skill architecture comparison (CC vs Gemini)
