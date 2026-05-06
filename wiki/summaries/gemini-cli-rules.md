---
title: "Gemini CLI — GEMINI.md Rules System"
type: summary
tags: [gemini, cross-platform, rules, agent-config, @-imports, toml-commands]
sources:
  - "Provide context with GEMINI.md files.md"
  - "Gemini CLI Custom slash commands  Google Cloud Blog.md"
  - "Custom commands.md"
urls:
  - "https://geminicli.com/docs/cli/gemini-md/"
created: 2026-05-06
updated: 2026-05-07
---

# Gemini CLI — GEMINI.md Rules System

Gemini CLI's instruction file system. Closer to Claude Code's `CLAUDE.md` + `@-imports` than to AGENTS.md — supports modular composition via `@file.md` imports, hierarchical discovery, and JIT loading.

---

## Instruction File: `GEMINI.md`

Gemini CLI reads `GEMINI.md` as its primary rules file. Discovery order:

1. **Global**: `~/.gemini/GEMINI.md` — user-level, loaded in every session
2. **Workspace**: project root `GEMINI.md` — loaded when Gemini CLI runs in that directory
3. **Subdirectory**: `subdir/GEMINI.md` — loaded JIT when agent navigates into that directory

This is hierarchical loading: global < workspace < subdirectory. JIT loading means subdirectory instructions load on demand, not at startup — same principle as CC's `@-import` deferred loading.

---

## `@file.md` Import Syntax

`GEMINI.md` supports importing other markdown files:

```markdown
# GEMINI.md
@rules/communication.md
@rules/editing.md
@wiki/ai-kb/00-index.md
```

Paths are relative to the file containing the import. This enables the same modular rule composition pattern as CC's `@~/.claude/rules/*.md` — each rule file stays focused; the root file orchestrates imports.

**Migration note**: CC's `@~/.claude/rules/core.md` → Gemini's `@rules/core.md` (relative path, same content).

---

## Custom Commands: TOML Files

**This was missing from the prior wiki entry.** Gemini also has a TOML-based custom commands system — equivalent in many ways to CC skills.

Files in `~/.gemini/commands/` (global) or `.gemini/commands/` (project). Filename = command name. Subdirectories create namespaced commands (`git/commit.toml` → `/git:commit`).

```toml
description = "Investigates and creates a plan."
prompt = """
Your task is to plan: {{args}}

Current commits: !{git log --pretty=format:"%s" -n 5}

Read {baseDir}/docs/best-practices.md and apply them.
@{docs/best-practices.md}
"""
```

**Injection syntax:**
- `{{args}}` — user input (raw outside `!{}`, shell-escaped inside)
- `!{shell}` — shell command output injected; security confirmation required
- `@{path}` — file content injected; processed before `!{}`
- No `{{args}}` → args appended to prompt after two newlines (default behavior)

**MCP prompts** also appear as slash commands. The `name` and `description` of MCP prompts become the command.

---

## Key Differences from CLAUDE.md

| Feature | Claude Code | Gemini CLI |
|---|---|---|
| Root file | `CLAUDE.md` | `GEMINI.md` |
| Global location | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` |
| Import syntax | `@path/to/file.md` | `@file.md` (relative) |
| Subdirectory JIT | Yes (scoped CLAUDE.md files) | Yes (scoped GEMINI.md files) |
| Skills system | Yes (SKILL.md + Skill tool) | Yes (`activate_skill` + `.gemini/skills/`) |
| Custom commands | Yes (TOML in `.claude/commands/`) | Yes (TOML in `.gemini/commands/`) |
| Subagents | Yes (agents/*.md YAML) | Experimental |
| Hooks | Yes | Yes |
| Headless mode | Yes (`-p`) | Yes (`--headless`) |

---

## Migration Mapping (CC → Gemini)

| CC asset | Gemini equivalent |
|---|---|
| `claude-setup/CLAUDE.md` | `~/.gemini/GEMINI.md` |
| `claude-setup/rules/*.md` | Same files, referenced via `@rules/*.md` imports |
| `claude-setup/skills/wiki-context/SKILL.md` | `.gemini/skills/wiki-context/SKILL.md` + `activate_skill` |
| `.claude/commands/*.toml` | `.gemini/commands/*.toml` (same format) |
| `claude-setup/agents/*.md` | Experimental subagents (not production-ready) |
| Hooks | Hooks (supported) |
| `templates/AGENTS.md` | Not natively read; use GEMINI.md (or configure `context.fileName`) |

---

## Related Pages

- [[entities/gemini-cli]] — full Gemini CLI entity (tools, features, parity)
- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-context-instructions]] — what GEMINI.md implements
- [[entities/agents-md-format]] — AGENTS.md format; Gemini can be configured to read it
