---
title: "Claude Code Plugins"
type: concept
tags: [claude-code, plugins, skills, namespacing, dotfiles]
sources:
  - "Claude Code Plugins - llm-wiki as plugin.md"
  - "wshobsonagents Intelligent automation and multi-agent orchestration for Claude Code.md"
created: 2026-04-26
updated: 2026-04-26
---

# Claude Code Plugins

Claude Code plugins are self-contained directories that bundle skills, agents, hooks, and resources under a shared namespace. They extend Claude Code's capabilities in a portable, versioned, and shareable form beyond what personal `~/.claude/` config offers.

## Structure

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json        ← manifest (required)
├── skills/
│   └── <skill-name>/
│       └── SKILL.md       ← auto-discovered
├── agents/                ← optional
└── docs/                  ← optional bundled resources
```

The `.claude-plugin/` directory marks the root as a plugin. All other components live at the plugin root.

## Manifest (`plugin.json`)

Minimal valid manifest:
```json
{
  "name": "my-plugin",
  "description": "One-line description shown in plugin listings",
  "version": "1.0.0"
}
```

`name` becomes the namespace. Skills inside become `/my-plugin:<skill-name>` — no collision with other installed skills.

## Scopes Comparison

| Location | Type | Namespace | Scope |
|---|---|---|---|
| `~/.claude/skills/<name>/` | Personal config | `/<name>` | All projects |
| `.claude/skills/<name>/` | Project config | `/<name>` | Current project |
| Plugin `skills/<name>/` | Plugin | `/<plugin-name>:<name>` | Where plugin is active |

## Invocation

**Local testing:**
```bash
claude --plugin-dir ~/path/to/my-plugin
```

**Installed plugins:** registered via `~/.claude/plugins/` config; auto-loaded on every session.

**After edits:**
```text
/reload-plugins
```
Reloads all plugins without restarting Claude Code — essential during development.

## Skill Discovery

Claude auto-discovers skills via `skills/<name>/SKILL.md`. The `name` field in `SKILL.md` frontmatter is used as the sub-command; if omitted, the directory name is used. Supporting files (scripts, references, assets) can live beside `SKILL.md`.

## Symlink Gotcha

Installed plugins are cached. They **cannot** reliably reference files outside the plugin directory via relative paths. Workarounds:
1. **Copy** wiki/docs into the plugin directory
2. **Symlink** from inside the plugin to files elsewhere: `ln -s ~/repos/llm-wiki/wiki skills/wiki/references`
3. **Absolute paths** work for local-only plugins (not distributable)

For distributable plugins: all referenced content must live inside the plugin directory.

## When to Use Plugins vs. Personal Config

Use a plugin when:
- Same skill set needed across multiple projects
- Want namespacing to avoid skill name collisions
- Plan to share or version the skill collection
- Skills have bundled resources (scripts, reference docs) that should travel with them

Use personal `~/.claude/skills/` when:
- Skills are personal conventions not worth packaging
- One machine, personal productivity only
- No need for namespacing

## wshobson Plugin Ecosystem

The wshobson/agents repo (184 agents, 78 plugins) demonstrates large-scale plugin use: plugins group related agents and skills by domain, with a `PluginEval` framework for testing plugin quality gates. See [[summaries/wshobson-agent-orchestration]].

## Related Pages

- [[concepts/agent-skills]] — SKILL.md format, progressive disclosure, three loading levels
- [[concepts/agent-subagents]] — agents bundled in plugins follow the same YAML frontmatter format
- [[summaries/claude-code-plugins-llm-wiki]] — practical guide for wrapping llm-wiki as a plugin
- [[summaries/wshobson-agent-orchestration]] — large-scale plugin ecosystem example
