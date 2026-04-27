# Claude Code Plugins — Turning llm-wiki into a Plugin

Source: conversation with Claude (2026-04-26)
Topic: How to wrap a personal knowledge wiki as a Claude Code plugin

---

## Background

Your `dotfiles/llm-wiki` can become a Claude Code plugin, but the cleanest answer is: if it's mainly your personal knowledge/instructions, you may not even need a plugin; if you want it reusable and namespaced, wrap it as a plugin with `skills/`, `agents/`, or hooks.

## Best fit

Use **standalone `.claude/` config** if `llm-wiki` is just for your own machine or one repo, because Claude Code already supports personal/project instructions there and gives shorter names.

Use a **plugin** if you want the same knowledge system reused across projects, versioned, shareable, and invoked as namespaced commands like `/llm-wiki:architecture`.

## Minimal plugin shape

Plugin directory structure — only `plugin.json` inside `.claude-plugin/`, components like `skills/` at the plugin root:

```text
dotfiles/
└── llm-wiki-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── skills/
    │   ├── orchestration/
    │   │   └── SKILL.md
    │   ├── behavior/
    │   │   └── SKILL.md
    │   └── system/
    │       └── SKILL.md
    └── docs/
        └── your-existing-wiki-files.md
```

A valid manifest can be as small as:

```json
{
  "name": "llm-wiki",
  "description": "Knowledge graph and operating guidance for AI orchestration, behavior, and system design",
  "version": "1.0.0"
}
```

`name` is the namespace, so skills become `/llm-wiki:orchestration`, `/llm-wiki:behavior`, etc.

## Mapping a wiki to skills

Split by **task boundary**, not by file count: one skill for "system architecture," one for "agent behavior," one for "orchestration policy." Each `SKILL.md` references nearby support files. Claude auto-discovers skills from `skills/<name>/SKILL.md`, and supporting files can live beside them.

Example SKILL.md:

```md
---
description: Use when reasoning about AI orchestration patterns, agent coordination, routing, memory, and tool flows.
---

Read the local reference files in this skill folder before answering.

Focus on:
- orchestration patterns
- routing strategies
- memory boundaries
- failure handling
- observability

When relevant, synthesize guidance from the wiki into concrete recommendations.
```

If existing docs are already good, copy them into each skill folder and make `SKILL.md` the entrypoint/instruction layer.

## How to run it

For local testing, start Claude Code with your plugin directory:

```bash
claude --plugin-dir ~/dotfiles/llm-wiki-plugin
```

Invoke a skill:

```text
/llm-wiki:orchestration
```

After edits, use `/reload-plugins` so Claude picks up changes without restarting.

## Migration path from dotfiles

1. Keep original wiki in `~/dotfiles/llm-wiki/`.
2. Create `~/dotfiles/llm-wiki-plugin/`.
3. Add `.claude-plugin/plugin.json`.
4. Create `skills/` folders that point Claude to the right pieces of your wiki.
5. Optionally symlink shared docs into the plugin, since installed plugins can't rely on files outside their directory unless you use symlinks.

## Important gotcha

If you eventually install/distribute the plugin, Claude caches installed plugins and they cannot reliably reference files outside the plugin directory with paths like `../llm-wiki`; symlinks are the supported workaround.
For long-term reliability, either copy the needed wiki files into the plugin or symlink them inside the plugin folder.

## Decision heuristic

- `llm-wiki` is mainly **personal brain/config** → put the active version in `~/.claude/skills` or project `.claude/skills`.
- Want **portable, reusable, versioned behavior** across many repos → wrap as `llm-wiki` plugin and launch with `--plugin-dir` first.
