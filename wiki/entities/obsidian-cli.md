---
title: "Obsidian CLI"
type: entity
tags: [obsidian, cli, pkm, automation, agentic-vault-access]
sources: ["Obsidian CLI.md", "Obsidian CLI - kepano Agent Skill.md", "Obsidian CLI - Official Command Reference (help.obsidian.md).md", "The Obsidian CLI Complete Guide - Frank Anaya.md"]
created: 2026-07-01
updated: 2026-07-01
---

# Obsidian CLI

The official command-line interface for Obsidian, shipped inside the desktop app since v1.12.4 (Feb 27, 2026) — free, no Catalyst license required. Enabled via **Settings → General → Command line interface**.

## Requirements

- Obsidian **1.12.4+** installer (not just the app version — the installer itself must be updated)
- The **Obsidian desktop app must be running**. The CLI is a client that talks to the live app instance — it does not read/write vault files directly. If Obsidian isn't running, commands silently fail or error; the first command run when it's closed launches it.
- Binary must be on `$PATH` (Obsidian attempts this automatically on enable; a new terminal window is required to pick up the PATH change).

## Why it's different from third-party vault scripts

Because commands go through Obsidian's own runtime (not raw file I/O), operations are link-safe and settings-aware: `move` updates all internal `[[wikilinks]]` automatically, `create` applies templates correctly, `property:set` writes valid YAML frontmatter. Third-party tools that edit `.md` files directly (older community `obsidian-cli` projects, `notesmd-cli`, etc.) don't get this — moving a file with them can silently break backlinks.

## Syntax

- **Parameters**: `key=value`, quote values containing spaces — `obsidian create name="My Note" content="Hello"`
- **Flags**: bare words, no dashes — `obsidian create name="Draft" silent overwrite`. `--copy` (copy output to clipboard) is the one documented flag that *does* use a dash.
- Multiline content: `\n` for newline, `\t` for tab
- File targeting: `file=<name>` resolves like a wikilink; `path=<path>` is exact vault-root-relative
- Vault targeting: `vault=<name>` as the first parameter (defaults to most recently focused vault)
- Output formats: `json` (scripts/jq), `csv`, `md`, `paths` (for xargs), `yaml`, `tree`, `tsv`

**Flag-syntax contradiction (flagged, not silently resolved):** the official docs (`help.obsidian.md/cli`) and kepano's canonical `obsidian-skills` SKILL.md both independently state flags are bare words with no dashes. Frank Anaya's guide writes them with a double dash throughout (`--silent --overwrite`) and calls that "Rule 3." Two independent primary-ish sources agree against one — treat bare-word flags (`silent`, `overwrite`) as correct, and Anaya's double-dash form as either an error in that guide or an undocumented alias. If a flag silently no-ops, this is the first thing to check.

## Command categories

Opening/reading, search (full-text + tag `[tag:x]` + property `[status:active]` query syntax), daily notes (`daily`, `daily:read`, `daily:append`, `daily:prepend`, `daily:path`), tasks, properties (YAML frontmatter), tags/links/backlinks/orphans/unresolved, plugins/themes/snippets, sync/publish/file history, and developer commands (`eval`, `dev:screenshot`, `dev:console`, `dev:dom`, `dev:css`, CDP/debugger). Over 100 commands total; `obsidian help` is always the current source of truth.

## Safety notes (from the guide's own "mistakes to avoid")

1. Run a command manually before scripting it — misunderstood commands fail silently in automation.
2. Use plain `delete` (moves to Obsidian trash) before ever using `delete --permanent`, which is irreversible.
3. Cron/background scripts must guard on "Obsidian is running" — either start it or log-and-exit-gracefully rather than run partial operations.
4. `eval` runs real JavaScript in Obsidian's runtime (sandboxed renderer, not system shell) — read AI-generated `eval` code before running it.
5. Don't try to memorize the full command surface; start from the 5 highest-value commands (`obsidian`, `daily`, `search query=`, `daily:append`, `files total`) and add commands as needed.

## Related

- [[entities/obsidian-cli-rest-mcp]] — community plugin exposing these same commands as a REST API + 2-tool MCP server (search/execute), for agents that shouldn't shell out per call
- [[entities/obsidian-claude-code-mcp]] — separate community plugin bridging Claude Code to a running vault via WebSocket
- [[concepts/cli-driven-vault-automation]] — the wrapper-script and cron patterns built on top of this CLI
- [[concepts/wikilink-graph-extraction]] — this wiki (`llm-wiki`) is itself an Obsidian vault (`.obsidian/` at repo root), so this CLI (or the MCP bridges below) can query/open its own notes too
