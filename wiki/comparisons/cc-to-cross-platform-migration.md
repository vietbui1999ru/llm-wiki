---
title: "Claude Code → Cross-Platform Migration Matrix"
type: comparison
tags: [cross-platform, migration, claude-code, opencode, codex, gemini, cursor, copilot, zed]
sources:
  - "vietbui1999rueverything-claude-code The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond..md"
urls:
  - "https://geminicli.com/docs/cli/gemini-md/"
  - "https://opencode.ai/docs/commands/"
  - "https://opencode.ai/docs/rules/"
  - "https://opencode.ai/docs/agents/"
  - "https://developers.openai.com/codex/subagents"
  - "https://developers.openai.com/codex/guides/agents-md"
  - "https://developers.openai.com/codex/skills"
  - "https://forum.cursor.com/t/cursor-rules-in-background-agents/105598"
created: 2026-05-06
updated: 2026-05-22
---

# Claude Code → Cross-Platform Migration Matrix

Layer-by-layer mapping of CC assets to equivalent mechanisms on Gemini CLI, OpenCode, Codex, and Cursor. "Parity" = how close the target mechanism is to the CC original.

---

## Rules / Ambient Instructions

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor |
|---|---|---|---|---|---|
| Root file | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` | `AGENTS.md` | `.cursor/rules/*.md` |
| Global location | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` | `~/.config/opencode/AGENTS.md` | `~/.codex/AGENTS.md` | None |
| Multi-file composition | `@path/to/file.md` imports | `@file.md` imports | `rules: [...]` in `opencode.json` | `AGENTS.override.md` layering | Multiple files in `.cursor/rules/` |
| Project-scoped | Yes (CLAUDE.md at project root) | Yes (GEMINI.md at project root) | Yes (AGENTS.md) | Yes (AGENTS.md + .codex/) | Yes (.cursor/rules/) |
| Subdirectory JIT loading | Yes | Yes | Yes (per-dir AGENTS.md) | Yes (global→CWD walk) | Unknown |
| **Parity** | — | High | High | High | Medium (no global file) |

**Migration action**: Content of `claude-setup/rules/*.md` → copy files, reference via platform's import syntax. Content is portable; only the loading mechanism changes.

---

## Skills (On-Demand Prompt Templates)

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor |
|---|---|---|---|---|---|
| Mechanism | `SKILL.md` + `Skill` tool invocation | `.gemini/commands/*.toml` + `activate_skill` | `.opencode/commands/*.md` slash commands | `skills/<name>/SKILL.md` + `skills/<name>/agents/openai.yaml` | None (inline only) |
| Invocation | `/skill-name` or Skill tool | `/command-name` (TOML) or `activate_skill` (skills) | `/command-name {{args}}` in chat | `$skill-name` or implicit skill injection | N/A |
| Arguments | Via skill prompt | `{{args}}`, `!{shell}`, `@{file}` in TOML | `{{argument_name}}` template slots | Via the skill body and optional default prompt | N/A |
| Shell execution | Bash tool | `!{shell}` injection with confirmation | `$(command)` injection | Via normal Codex tool use from skill instructions | N/A |
| Agent binding | Skill loads into current session | N/A | Command can route to specific agent | Native skill injection; optional MCP deps in metadata | N/A |
| **Parity** | — | High | High | Medium | Low (inline only) |

**Migration action**:
- Gemini: copy TOML commands to `.gemini/commands/`; content format is nearly identical; copy skills to `.gemini/skills/`
- OpenCode: create `.opencode/commands/wiki-context.md`, `.opencode/commands/security-patterns.md` etc.
- Codex: create `skills/<name>/SKILL.md` and optional `skills/<name>/agents/openai.yaml`
- Cursor: inline skill content as sections in rules file (ambient, not invokable)

---

## Subagents (Spawnable Specialized Agents)

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor |
|---|---|---|---|---|---|
| Format | YAML frontmatter in `agents/*.md` | None | JSON config + instructions `.md` | **TOML** in `.codex/agents/*.toml` | None |
| Global location | `~/.claude/agents/` | — | `~/.config/opencode/agents/` | `~/.codex/agents/` | — |
| Project location | `.claude/agents/` | — | `.opencode/agents/` | `.codex/agents/` | — |
| Model per agent | `model: sonnet` | — | `"model": "..."` | `model = "gpt-4.1"` | — |
| Tool restriction | `disallowedTools: Edit, Write` | — | `task_permissions: [read, shell]` | `[sandbox]` block | — |
| Isolation | `isolation: worktree` | — | Worktree per task (separate config) | `[sandbox]` | Remote execution |
| Invocation | Agent tool dispatch | — | `@agent-name` in chat | TOML agent name | Background agent |
| **Parity** | — | None | High | High | Low |

**Migration action**:
- OpenCode: rewrite 18 agent `.md` files → JSON config files + separate instruction `.md` files
- Codex: rewrite → TOML files; frontmatter `description` → `description =`; system prompt body → `developer_instructions = """`
- Gemini/Cursor: no equivalent — routing logic must be inlined in rules

---

## Hooks (Automated Triggers)

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor | GitHub Copilot |
|---|---|---|---|---|---|---|
| System | `PreToolUse`, `PostToolUse`, `Stop` in `settings.json` | None | Plugin event system (20+ event types) | `hooks` in `config.toml` | Project-local hook events (15 types) | None |
| Event count | 8 types | — | 20+ types | — | 15 types | — |
| Current setup | PostToolUse on Bash → `publish-ai-kb.sh` | — | Already done: lean-compaction-plugin.ts | Can mirror project-local shell hooks | — | — |
| **Parity** | — | None | Highest (more events than CC) | Medium | Medium (different events, DRY adapter) | None |

**OpenCode leads on hooks**: OpenCode has more hook event types than Claude Code. Additional events include `file.edited`, `file.watcher.updated`, `message.updated`, `lsp.client.diagnostics`. The compaction hook (`session.compacting`) has no CC equivalent.

**Cursor hook architecture**: Cursor has 15 hook types vs CC's 8. ECC uses a DRY adapter pattern — `adapter.js` transforms Cursor's stdin JSON to Claude Code's format, so the same `scripts/hooks/*.js` run on both harnesses. Notable Cursor-only hooks: `beforeSubmitPrompt` (secrets detection in prompts), `beforeTabFileRead` (blocks reading `.env`/`.pem` files).

**Migration action**: OpenCode hook equivalent is the plugin system — already done (`lean-compaction-plugin.ts`). Codex supports repo-local hooks via `.codex/config.toml`, but plugin parity is still separate. Gemini and Copilot still have no equivalent here.

---

## Plugins

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor |
|---|---|---|---|---|---|
| System | CC plugin marketplace (`enabledPlugins`) | None | npm packages (`@tarquinen/opencode-dcp`, etc.) | None | Extension marketplace |
| Specific plugins | superpowers, caveman, qmd, playwright, context7 | — | DCP plugin (already documented) | — | Cursor extensions |
| **Parity** | — | None | Parallel (different ecosystem) | None | Parallel (different ecosystem) |

**Migration action**: No migration — plugin ecosystems are fully separate. Identify equivalent functionality per platform separately.

---

## Settings / Config

| Asset | Claude Code | Gemini CLI | OpenCode | Codex | Cursor |
|---|---|---|---|---|---|
| Config file | `~/.claude/settings.json` | `~/.gemini/settings.json` | `~/.config/opencode/opencode.json` | `~/.codex/` | Cursor settings UI / JSON |
| Permission schema | `permissions.allow/ask/deny/defaultMode` | Not equivalent | `opencode.json` agent config | `[sandbox]` in TOML | Not user-configurable (remote) |
| Model selection | `"model": "sonnet"` | Gemini-specific | Model per agent/session | TOML `model =` | Cursor model settings |

---

## Council / Multi-Vendor Review

`templates/council.py` — **100% portable**. Runs anywhere Python + GITHUB_TOKEN available. Platform-agnostic by design.

---

## GitHub Copilot (VS Code)

No hook system, no subagent API. Instruction + prompt layer only.

| Component | Copilot equivalent |
|---|---|
| CLAUDE.md rules | `.github/copilot-instructions.md` (always-loaded) |
| Skills | `.github/prompts/*.prompt.md` (on-demand) |
| Per-task context | `.vscode/settings.json` per-task instruction files |
| Hook automations | Not supported |
| Subagents / agents | Not supported |

**Practical limit**: Copilot delivers the ECC *philosophy* (standards, security, TDD, workflow) but not the *enforcement* (hooks, agents, isolation). Use for basic coding discipline on VS Code-centric teams; use Claude Code or Cursor for full harness enforcement.

## Zed

Project-local `.zed/` adapter. Writes ECC-managed files under `.zed/`, flattened rules, agents, commands, skills. No dedicated hook system. BYOK/OpenRouter credentials must be configured through Zed's settings UI, not in the repo.

```bash
./install.sh --profile minimal --target zed
```

## What's Already Cross-Platform

| Asset | Status |
|---|---|
| `templates/AGENTS.md` | OpenCode + Codex: direct; Gemini: adapt to GEMINI.md; Cursor: adapt to .cursor/rules |
| `templates/council.py` | 100% portable |
| `templates/env-model-routing.sh` | 100% portable |
| Wiki knowledge base (`wiki/`) | 100% portable — markdown + qmd |
| qmd search | Portable (CLI + MCP) |
| Rule file *content* (`rules/*.md`) | Portable — only loading mechanism differs |
| Skill file *content* (`skills/*/SKILL.md`) | Portable to Codex native skills with small metadata shim |

---

## What Still Needs Official Sources

| Gap | Search term |
|---|---|
| Cursor official `.cursor/rules` spec | `Cursor official docs .cursor/rules format` |
| Cursor official background agents | `Cursor official docs background agents` |
| OpenCode agents schema full JSON spec | `OpenCode agents schema mode primary subagent` |
| Codex hook docs / examples | `Codex hooks config.toml PostToolUse matcher command` |

---

## Related Pages

- [[summaries/gemini-cli-rules]] — Gemini CLI GEMINI.md + @-imports
- [[summaries/opencode-commands-agents]] — OpenCode commands, rules, agents
- [[summaries/codex-agents-skills]] — Codex TOML agents + native skills
- [[summaries/cursor-rules-background-agents]] — Cursor .cursor/rules + background agents
- [[summaries/everything-claude-code]] — ECC cross-harness parity table (source for Cursor/Copilot/Zed data)
- [[entities/agents-md-format]] — AGENTS.md cross-tool compatibility table
- [[entities/everything-claude-code]] — ECC entity with full cross-harness matrix
- [[concepts/agent-context-instructions]] — the concept all these implement
- [[concepts/agent-skills]] — CC skills; what each platform replaces
- [[concepts/agent-subagents]] — CC subagents; migration target per platform
