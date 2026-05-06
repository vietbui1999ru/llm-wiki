---
title: "Gemini CLI — GEMINI.md Rules System"
type: summary
tags: [gemini, cross-platform, rules, agent-config, @-imports]
sources: []
urls:
  - "https://geminicli.com/docs/cli/gemini-md/"
created: 2026-05-06
updated: 2026-05-06
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

## Key Differences from CLAUDE.md

| Feature | Claude Code | Gemini CLI |
|---|---|---|
| Root file | `CLAUDE.md` | `GEMINI.md` |
| Global location | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` |
| Import syntax | `@path/to/file.md` | `@file.md` (relative) |
| Subdirectory JIT | Yes (scoped CLAUDE.md files) | Yes (scoped GEMINI.md files) |
| Skills system | Yes (SKILL.md + Skill tool) | No — inline in GEMINI.md or imported files |
| Subagents | Yes (agents/*.md YAML) | No equivalent |

---

## Migration Mapping (CC → Gemini)

| CC asset | Gemini equivalent |
|---|---|
| `claude-setup/CLAUDE.md` | `~/.gemini/GEMINI.md` |
| `claude-setup/rules/*.md` | Same files, referenced via `@rules/*.md` imports |
| `claude-setup/skills/wiki-context/SKILL.md` | Import as `@skills/wiki-context.md`; no invocation mechanism |
| `claude-setup/agents/*.md` | No equivalent — embed routing logic in GEMINI.md prose |
| Hooks | No equivalent |
| `templates/AGENTS.md` | Not natively read; use GEMINI.md instead (or configure context.fileName) |

---

## Related Pages

- [[comparisons/cc-to-cross-platform-migration]] — full migration matrix
- [[concepts/agent-context-instructions]] — what GEMINI.md implements
- [[entities/agents-md-format]] — AGENTS.md format; Gemini reads differently from CC
