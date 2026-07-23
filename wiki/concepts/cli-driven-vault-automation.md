---
title: "CLI-Driven Vault Automation"
type: concept
tags: [obsidian, automation, cli, cron, wrapper-script, agentic-vault-access]
sources: ["The Obsidian CLI Complete Guide - Frank Anaya.md", "Obsidian CLI - kepano Agent Skill.md", "Obsidian CLI REST MCP (developassion).md"]
created: 2026-07-01
updated: 2026-07-01
---

# CLI-Driven Vault Automation

The pattern of scripting a running Obsidian vault via [[entities/obsidian-cli]] (or its MCP wrappers) instead of touching the GUI: shell scripts, cron jobs, and agent wrapper scripts that treat vault operations as ordinary CLI calls with structured (`format=json`) output piped into `jq`.

## Wrapper-script conventions (from two real-world examples)

Two independent GitHub projects wrapping the CLI converge on the same shape, worth treating as the default template for any new wrapper:

**1. Doctor/health-check pattern** (`lacp-obsidian-cli`, part of a larger agent-config-management CLI): a `check`/`doctor` subcommand that verifies, in order — CLI binary on PATH, Obsidian.app actually running (`pgrep`), vault directory exists — before any real command runs, with `--json` output for scripted consumption:

```bash
resolve_vault() { ... }              # env var -> manifest.json -> default fallback
require_obsidian_cli() {
  command -v obsidian >/dev/null 2>&1 || die "obsidian CLI not found on PATH."
}
check_cmd_fn() {
  # PASS/FAIL/WARN checks: cli_binary, obsidian_app (pgrep), vault_path
  # exits 1 if any check is FAIL
}
```

**2. Explicit "wrapper for AI agents" pattern** (`obs-helper.sh`, titled literally "Obsidian CLI Wrapper for AI Agents"): a thin dispatch script mapping short verbs to CLI invocations, with the "Obsidian not running" guard as the very first line before anything else runs:

```bash
if ! pgrep -x "Obsidian" > /dev/null; then
    echo "Error: Obsidian is not running"
    exit 1
fi
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
case "$ACTION" in
    daily)       obsidian daily ;;
    daily-add)   obsidian daily:append content="$1" ;;
    note-create) obsidian create name="$1" content="$2" ;;
    note-read)   obsidian read file="$1" ;;
    search)      obsidian search query="$1" ;;
    tasks)       obsidian tasks daily todo ;;
    task-toggle) obsidian task daily line="$1" toggle ;;
esac
```

Both independently arrived at: **guard on "is Obsidian running" first**, **resolve vault/PATH before dispatch**, **expose a small stable verb set rather than the full 100+-command surface**. That last point is the same instinct behind the MCP `search`+`execute` Code Mode pattern in [[entities/obsidian-cli-rest-mcp]] — a large underlying command surface gets collapsed to a small stable interface for the calling agent/script, whether the caller is a human's cron job or an LLM.

## Common automation shapes

- **Morning/daily setup** — prepend a template into today's daily note, pull yesterday's unfinished `- [ ]` tasks forward
- **Inbox auto-sort** — read a folder as `format=json`, branch on `properties file=... format=json | jq` tag values, `move` into PARA-style folders
- **Tag-to-publish pipeline** — search `[tag:ready-to-publish]` → `properties:set` a published date/status → `publish:add`
- **Vault health report** — `files total` + `orphans format=json | jq length` + `unresolved format=json | jq length` + `tags sort=count` → written back as a new note
- **Cron-fed external data** — fetch from any API (weather, HN, etc.) and `daily:append`/`create` the result; this is the shape that most needs the "Obsidian must be running" guard since cron runs unattended

## Safety rules (apply whether the caller is a human's script or an agent)

1. Run every command manually once before wiring it into a script — a misunderstood command fails silently when automated.
2. Prefer plain `delete` (trash) over `delete --permanent` until the automation has proven it targets the right notes.
3. Guard on "Obsidian is running" at the top of any unattended script (cron, agent loop) — start it or fail loudly rather than run partial operations.
4. Treat `eval`/`dev:*` (JavaScript-in-runtime) as the highest-risk command class — both REST/MCP bridges gate these behind a separate `allowDangerousCommands`/"Dangerous" flag; read generated `eval` code before running it.
5. Don't over-scope a wrapper to the full command surface — both real examples above expose a handful of verbs, not the 100+ raw commands.

## Related

- [[entities/obsidian-cli]] — the underlying command surface these scripts wrap
- [[entities/obsidian-cli-rest-mcp]] — the same "small stable interface over a big command surface" instinct, applied via MCP's Code Mode instead of a shell wrapper
- [[entities/obsidian-claude-code-mcp]] — the standing-connection alternative to scripting per-invocation
- [[concepts/tool-design-for-agents]] — general principle: collapse large tool/command surfaces into a small, stable, discoverable interface
