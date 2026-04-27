---
title: "Claude Code Plugins — Turning llm-wiki into a Plugin"
type: summary
tags: [claude-code, plugins, skills, dotfiles, knowledge-management]
sources:
  - "Claude Code Plugins - llm-wiki as plugin.md"
created: 2026-04-26
updated: 2026-04-26
---

# Claude Code Plugins — Turning llm-wiki into a Plugin

Practical guide for wrapping a personal knowledge wiki as a Claude Code plugin, with a decision heuristic for when to use plugins vs. standalone config.

## Core Decision

| Goal | Approach |
|---|---|
| Personal machine only, one repo | `~/.claude/skills/` or `.claude/skills/` — no plugin needed |
| Reusable across projects, versioned, shareable | Plugin with `.claude-plugin/plugin.json` + `skills/` |

The namespacing benefit: skills become `/llm-wiki:orchestration` instead of `/orchestration`, avoiding collisions with other skills.

## Plugin Structure

```text
llm-wiki-plugin/
├── .claude-plugin/
│   └── plugin.json          ← manifest (name, description, version)
├── skills/
│   ├── orchestration/
│   │   └── SKILL.md
│   ├── behavior/
│   │   └── SKILL.md
│   └── system/
│       └── SKILL.md
└── docs/                    ← optional wiki files bundled here
```

`plugin.json` minimal fields:
```json
{
  "name": "llm-wiki",
  "description": "Knowledge graph and operating guidance",
  "version": "1.0.0"
}
```

`name` becomes the namespace: `/llm-wiki:<skill-name>`.

## Mapping Wiki → Skills

Split by **task boundary**, not file count. Each `SKILL.md` references nearby support files. Skills discovered automatically from `skills/<name>/SKILL.md`.

Pattern: SKILL.md is the entrypoint/instruction layer; copy or symlink actual wiki docs beside it.

## Launch and Reload

```bash
claude --plugin-dir ~/dotfiles/llm-wiki-plugin
```
```text
/llm-wiki:orchestration
/reload-plugins          ← pick up SKILL.md edits without restart
```

## Symlink Gotcha

Installed/distributed plugins cannot reliably reference files **outside** the plugin directory via relative paths like `../llm-wiki`. Symlinks inside the plugin directory are the supported workaround. For purely local use, absolute paths also work.

## Related Pages

- [[concepts/claude-code-plugins]] — full plugin system concept
- [[concepts/agent-skills]] — SKILL.md format, progressive disclosure, scopes
- [[concepts/compounding-knowledge-base]] — why a compiled wiki beats per-query RAG
