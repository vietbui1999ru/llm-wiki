---
title: "Dotfiles Layout for the Agent Harnesses"
type: concept
tags: [dotfiles, stow, claude-code, codex, pi, opencode, agents, configuration, macos]
sources: ["dotfiles README.md (Packages table)", "dotfiles scripts/restow.sh, bootstrap-dirs.sh, sync-agent-rules.sh", "dotfiles docs/workflows/sync-agents-disk-roster.md", "dotfiles shared/", "dotfiles scripts/firecrawl, scripts/firecrawl-mcp (verification run 2026-10-15)"]
created: 2026-10-04
updated: 2026-10-19
---

# Dotfiles Layout for the Agent Harnesses

How the `~/dotfiles` repo provisions the config of each coding-agent harness, and which dot-folders under `$HOME` are config versus runtime state. Verified by listing the directories and resolving symlinks on 2026-10-04; macOS, zsh, GNU stow.

## Three provisioning mechanisms

| Mechanism | What it does | Drift risk |
|---|---|---|
| **stow** (symlink) | `scripts/restow.sh` links a package's files into `$HOME`. Packages: zsh, starship, nvim, tmux, tmuxinator, kitty, git, jj ([[entities/jujutsu]]), claude, opencode, pi, codex. aerospace, mouseless, sketchybar, herdr and launchd are stowed by hand. | None; the repo file is the file. |
| **materialized** | `scripts/bootstrap-dirs.sh` creates directories and per-skill links once. | Drifts after creation. |
| **sync-pushed** | `scripts/sync-agent-rules.sh` copies `shared/AGENTS.md` and MCP server config one way into OpenCode and Codex (runs on dotfiles commits). | Edits made in the target are overwritten. |

## The dot-folders

The harness homes are **real directories, not symlinks**; only individual children are stow links. That is why most of each folder is runtime state.

| Path | Config (managed) | Runtime / unmanaged |
|---|---|---|
| `~/.claude` | Symlinks into `dotfiles/claude/.claude`: `CLAUDE.md`, `RTK.md`, `rules/`, `docs/`, `keybindings.json`, `plugins/config.json`, individual hook files. `skills/` is a real directory of per-skill links from **three sources**: `dotfiles/claude/.claude/skills`, `dotfiles/shared/skills`, and `repos/llm-wiki/claude-setup/skills`. | `history.jsonl`, `projects/`, `sessions/`, `cache/`, `backups/`, `file-history/` (excluded by the package's `.gitignore`). Not a git repo. |
| `~/.codex` | Only `hooks.json` (symlink). `AGENTS.md` is a sync-pushed copy. | sqlite DBs, `sessions/`, `auth.json`, `config.toml`, `history.jsonl`. |
| `~/.pi` | `agent/AGENTS.md`, plus `extensions/` and `extensions-available/` from the `pi` package. | `agent/sessions/`, `auth.json`, `settings.json`, `mcp*.json`, `models-store.json`, logs; `~/.pi/.pi/` and `.pi-subagents/` hold runtime state. |
| `~/.config/opencode` | `opencode.json` and `plugins/` (symlinks). `AGENTS.md` is sync-pushed. | `commands/`, `skills/`, `node_modules`, `bun.lock`. |
| `~/.agents` | Skills linked from `dotfiles/shared/skills` by `scripts/bootstrap-dirs.sh` (approval-workflow, delegate-pi, gh-stack, grill-me, kanban-status, verify-spec; [[entities/pele]] once dotfiles #124 merges, which also installs its pinned npm dependency). | The other skills (real directories) and `.skill-lock.json`. |
| `dotfiles/.agents/` | None. | Per-repo workflow state (sessions, `events.jsonl`, approvals), gitignored. |

`dotfiles/shared/` is the harness-neutral source of truth (not a stow package): `AGENTS.md`, `mcp-servers.json`, `agent-workflow.default.json`, `research-tool-routing.md`, `skills/`, `templates/`.

## Where agent definitions live today

There is effectively **no general custom agent roster**, with one deliberate exception, the `firecrawl` agent (below). Before it, `~/.claude/agents/` was an empty real directory and `scout.md` and `worker.md` sat in `dotfiles/claude/.claude/agents/` without being linked into it (checked 2026-10-15); `~/.pi/agent/agents/` and `~/.config/opencode/agents/` did not exist (Pi gets subagents from the `pi-subagents` npm package; OpenCode defines one inline agent in `opencode.json`). The only other definition on disk is `~/.codex/agents/career-outreach.toml`, unmanaged and untracked. The llm-wiki canonical roster (`claude-setup/agents/`) is empty because commit `d9794e4` (2026-09-16) deleted 18 canonical and 22 generated agents; the owner intends to reintroduce agents later.

## Firecrawl across the four harnesses

Added 2026-10-15 so web research does not depend on one harness's MCP config. The common surface is the `firecrawl` CLI run through each harness's shell tool, plus the `firecrawl*` skills the CLI installs into `~/.agents/skills`, plus one thin `firecrawl` agent per harness. The CLI and skills cost nothing per session beyond the skill list; the MCP server (28 tools) is optional.

| Piece | Where it lives | Notes |
|---|---|---|
| Setup | `dotfiles/scripts/firecrawl-setup.sh`, called by `bootstrap-dirs.sh` | Links the two shims below, installs the CLI with npm if missing, runs `firecrawl init` for claude-code, codex and opencode only, then keeps the skills listed in `shared/firecrawl-skills.txt` (15) and moves the rest to `~/.agents/skills-disabled`. `--refresh` reinstalls |
| Credential shim | `dotfiles/scripts/firecrawl`, linked to `~/.local/bin/firecrawl` | Reads only `FIRECRAWL_API_KEY` from `~/secrets/.env` and overrides the inherited value, then runs the first real `firecrawl` on `PATH` (no hard-coded path; works with a sparse `PATH`) |
| MCP launcher | `dotfiles/scripts/firecrawl-mcp`, linked to `~/.local/bin/firecrawl-mcp` | Same key loading, then `npx -y firecrawl-mcp`. Used as the MCP `command` so no config file holds a literal key |
| Agent, Claude Code | `dotfiles/claude/.claude/agents/firecrawl.md` (symlink) | Haiku 5.5, tools Bash/Read/Grep/Glob |
| Agent, Codex | `dotfiles/codex/.codex/agents/firecrawl.toml`, **copied** by `sync-agent-rules.sh` | Must be a regular file, see below |
| Agent, OpenCode | `dotfiles/opencode/.config/opencode/agents/firecrawl.md` (symlink) | Subagent; bash denied except `firecrawl *` |
| Agent, Pi | `dotfiles/pi/.pi/agent/agents/firecrawl.md` (symlink) | Spawned through the `subagent` tool |

**Why a shim.** `~/secrets/.env` is sourced only by interactive zsh (`.zshrc`), and a process started before the key was rotated keeps the old value. The CLI prefers the environment variable over any stored login, so a stale inherited key beats the good one on disk and the API answers 401. Measured on 2026-10-15: the key in `.env` returned HTTP 200 while the key in the Claude Code session's environment returned 401. With the shim, a deliberately stale key planted in the environment of each harness process was overridden in every run that got far enough to call Firecrawl. The Claude Code MCP entry, project-scoped to llm-wiki, had the stale key as a literal in `~/.claude.json`; it now points at the launcher.

**First-run verification (independent agent plus a re-check of the Codex items, 2026-10-15; this is the state before the fixes described below).** T1 = scrape example.com through the CLI, T2 = list visible `firecrawl*` skills, T3 = run the `firecrawl` agent.

| Harness | T1 CLI | T2 skills | T3 agent | What blocked |
|---|---|---|---|---|
| Claude Code | pass | pass (34 listed) | pass | A depleted `ANTHROPIC_API_KEY` inherited from the launching process tree (commented out in `~/secrets/.env`, in no shell or harness file) made every headless `claude -p` fail with "Credit balance is too low"; passed with `env -u ANTHROPIC_API_KEY`, and a fresh terminal should clear it |
| Pi | pass | pass (34) | pass | Default provider (openai-codex) token expired; passed with `--model opencode-go/deepseek-v4-pro` |
| Codex | fail; **pass after the `dev` permission profile** | pass (34 at the time) | spawns after the copy fix | Sandbox network; fixed, see "Codex findings and fixes" |
| OpenCode | not run | not run | not run | `opencode run` (1.18.30) crashes on every invocation: `TypeError: undefined is not an object (evaluating 'a.name')` in `SystemPrompt.environment`. It crashed the same way with an empty config dir, a fresh data dir, three different models, no skills, plugins, commands or `AGENTS.md`, and no firecrawl agent, so it looks like an OpenCode bug rather than a setup fault. Not ruled out: skill discovery from `~/.claude/skills` or `~/.agents/skills`, because `HOME` could not be changed in the test. Static checks passed on 1.18.30. After `brew upgrade opencode` to 2.0.25 the crash is gone: `opencode run` works and both `grill-me` and `verify-spec` are visible; the default model is a Gemini free tier with a zero quota, so pass `-m opencode-go/deepseek-v4-pro`. The `opencode debug skill` subcommand no longer exists in 2.0.25 |

**Codex findings.**

- A symlinked `~/.codex/agents/*.toml` is listed as an available agent type but cannot be spawned ("agent type is currently not available"). Plain-file copies spawn fine, including a copy of the same TOML. Fixed by copying (the sync script now does it); a direct spawn after the fix returned the subagent's reply. The cause is inferred, not confirmed in Codex source: its role loader checks `is_file()` on directory entries.
- The CLI path was blocked: `features.network_proxy = true` in `~/.codex/config.toml` sets no domain allowlist, so the sandbox rejected `api.firecrawl.dev` (`getaddrinfo ENOTFOUND`, then "domain is not on the allowlist for the current sandbox mode"). It passed only with the proxy switched off, which is a security decision that was not taken.
- **Fix: a permission profile.** `[permissions.dev]` extends Codex's built-in `:workspace` profile (so the filesystem rules are Codex's own) and adds a network allowlist: `api.firecrawl.dev`, GitHub hosts, PyPI, npm, crates.io, the Go proxy and loopback. Template and install steps: `dotfiles/shared/templates/codex-permissions.toml` and `dotfiles/docs/codex-permissions.md` (`config.toml` is not stowed, so it is applied once per machine). It was tested in a scratch `CODEX_HOME` first, then applied: `firecrawl scrape` returns the page, an off-list host is blocked, a write outside the workspace is denied, a write inside it works, and `~/secrets/.env` stays readable, which the key shim needs.
- The two earlier attempts that did not work, kept as lessons: a one-off `-c` override of a per-profile domain (the parser split the quoted hostname on its dots) and a profile defined with only a network table (Codex then had no filesystem rules and could not start a session). `extends = ":workspace"` avoids both.
- The MCP launcher started under Codex and its tool was resolved, but headless `codex exec` refused the call with "MCP tool call requires approval, but approval policy is never". That is an approval-policy refusal, so interactive behavior is untested.

**Skills, after the cleanup.** `firecrawl init` installs 34 skills (about 10,700 characters of descriptions, roughly 2,700 tokens listed in every session that scans the folder; Codex printed "Skill descriptions were shortened to fit the skills context budget"). Scope was set to development, documentation, research, downloading information and comparison, which leaves 15, listed in `dotfiles/shared/firecrawl-skills.txt`. Pruned ones are moved to `~/.agents/skills-disabled`, not deleted.

- **The CLI's own skill is now the default.** `bootstrap-dirs.sh` used to copy a dotfiles `firecrawl` skill over the CLI's newer one on every run; that copy (and the Claude link to it) is removed. The Context7 / Ketch / Firecrawl routing policy stays in `shared/research-tool-routing.md`.
- **`firecrawl init` without `--agent` writes into the config folder of every agent it knows**, installed or not: on this machine it created skills-only folders for Continue, Roo, OpenClaw, OpenHands and Hermes, and filled Cursor, Gemini and Copilot. The setup script now passes `--agent` for claude-code, codex and opencode only (override with `FIRECRAWL_AGENTS`). Links were removed from Cursor, Gemini and Copilot at the owner's request; Hermes and OpenClaw were left as they were; Continue, Roo and OpenHands still hold only Firecrawl symlinks.
- **Not done on purpose:** `firecrawl make default`, which would disable the native web tools in agent configs.
- The same change set tracks the dotfiles `post-commit` hook in `scripts/hooks/` (it was untracked, so it did not exist on other clones) and makes it skip commits from linked worktrees, because it runs `sync-agent-rules.sh`, which rewrites live config.

**Agent blueprints** (drafts from the `build-agent` skill) go to `~/dotfiles/docs/agents/<slug>.md`: tracked, next to the builder's spec, and loaded by no harness, so a draft is never mistaken for an installed agent. They are deliberately kept out of the wiki (the skill promises not to modify it) and out of `claude-setup/agents/` (the canonical roster that `sync-agents.py` consumes).

## About "AgentOps"

The older personal Pi/Obsidian project at `~/repos/AgentOps` was torn down deliberately (commits `ece33a9`, `376727f`); the directory no longer exists and the default vault is now `~/repos/Obsidian`. It is unrelated to the external tool on [[entities/agentops]], which is documented-not-adopted. Remaining references in the dotfiles docs were retired in the 2026-10 cleanup, apart from historical teardown notes.

## Related

- [[systems/agent-review]]: the per-run Neovim review gate that lives across `scripts/`, `pi/`, and `nvim/` in this repo.
- [[entities/pi-agent]], [[entities/opencode]], [[entities/codex]]: the harnesses configured here.
- [[concepts/linux-setup-guide]]: bootstrapping this setup on a fresh machine.
