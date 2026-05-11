---
title: "OpenCode Configuration Reference"
type: summary
tags: [opencode, config, json, precedence, managed-settings, compaction]
sources: ["Config.md"]
created: 2026-05-11
updated: 2026-05-11
---

# OpenCode Configuration Reference

OpenCode uses JSON/JSONC config files. Multiple sources are **merged** (not replaced) — non-conflicting keys from all sources are preserved.

---

## Precedence Order (low → high)

1. Remote config (`.well-known/opencode`) — org defaults
2. Global config (`~/.config/opencode/opencode.json`) — user preferences
3. Custom config (`OPENCODE_CONFIG` env var)
4. Project config (`opencode.json` in project root)
5. `.opencode` directories — agents, commands, plugins
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed config files (`/Library/Application Support/opencode/` macOS, `/etc/opencode/` Linux)
8. **macOS managed preferences** (`.mobileconfig` via MDM) — highest, not user-overridable

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true
}
```

---

## TUI Config

TUI settings live in a **separate file** — `tui.json` / `tui.jsonc` (alongside `opencode.json`):

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "scroll_speed": 3,
  "diff_style": "auto",
  "mouse": true
}
```

Legacy `theme`, `keybinds`, `tui` keys in `opencode.json` are deprecated and auto-migrated.

---

## Variable Substitution

Two substitution forms available in config values:

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
    },
    "openai": {
      "options": { "apiKey": "{file:~/.secrets/openai-key}" }
    }
  }
}
```

- `{env:VAR}` — substitutes env var; empty string if unset
- `{file:path}` — substitutes file contents; paths relative to config file or absolute

---

## Key Options Quick Reference

| Key | Type | Description |
|---|---|---|
| `model` | string | Default model (`provider/name`) |
| `small_model` | string | Lightweight tasks (title generation, etc.) |
| `autoupdate` | bool / `"notify"` | Auto-download updates |
| `snapshot` | bool | Track file changes for undo (default: true; disable for large repos) |
| `share` | `"manual"` / `"auto"` / `"disabled"` | Session sharing behavior |
| `default_agent` | string | Agent used when none specified |
| `shell` | string | Shell for interactive terminal and tool calls |
| `disabled_providers` | string[] | Prevent providers loading even if credentials exist |
| `enabled_providers` | string[] | Allowlist of providers; all others ignored |

---

## Compaction Config

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

- `auto` — compact when context full (default: true)
- `prune` — remove old tool outputs (default: true)
- `reserved` — token buffer to leave before triggering compaction

---

## Permissions Config

Default: **all operations allowed** without approval.

```json
{
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

Values: `"allow"`, `"ask"`, `"deny"`. Bash supports glob patterns per command.

---

## Managed Settings (Enterprise)

Organizations can enforce settings users cannot override:

- **macOS**: deploy `.mobileconfig` via MDM (Jamf, Kandji, FleetDM) using `ai.opencode.managed` PayloadType
- Config keys map directly to `opencode.json` fields in the plist

```bash
opencode debug config  # shows resolved config including managed preferences
```

---

## Inline Agent Definition

Agents can be defined inline in config (or as markdown files in `.opencode/agents/`):

```jsonc
{
  "agent": {
    "code-reviewer": {
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer.",
      "tools": { "write": false, "edit": false }
    }
  }
}
```

---

## Related Pages

- [[entities/opencode]] — full OpenCode entity; plugin system, event surface
- [[summaries/opencode-commands-agents]] — commands, rules, agents migration from CC
- [[comparisons/cc-to-cross-platform-migration]] — full CC→OpenCode migration map
- [[concepts/context-compression]] — compaction config context
