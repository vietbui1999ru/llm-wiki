---
title: "Dotfiles Layout for the Agent Harnesses"
type: concept
tags: [dotfiles, stow, claude-code, codex, pi, opencode, agents, configuration, macos]
sources: ["dotfiles README.md (Packages table)", "dotfiles scripts/restow.sh, bootstrap-dirs.sh, sync-agent-rules.sh", "dotfiles docs/workflows/sync-agents-disk-roster.md", "dotfiles shared/", "dotfiles scripts/firecrawl, scripts/firecrawl-mcp (verification run 2026-10-15)"]
created: 2026-10-04
updated: 2026-10-15
---

# Dotfiles Layout for the Agent Harnesses

How the `~/dotfiles` repo provisions the config of each coding-agent harness, and which dot-folders under `$HOME` are config versus runtime state. Verified by listing the directories and resolving symlinks on 2026-10-04; macOS, zsh, GNU stow.

## Three provisioning mechanisms

| Mechanism | What it does | Drift risk |
|---|---|---|
| **stow** (symlink) | `scripts/restow.sh` links a package's files into `$HOME`. Packages: zsh, starship, nvim, tmux, tmuxinator, kitty, git, jj, claude, opencode, pi, codex. aerospace, mouseless, sketchybar, herdr and launchd are stowed by hand. | None; the repo file is the file. |
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
| `~/.agents` | Four skills linked from `dotfiles/shared/skills` (approval-workflow, delegate-pi, gh-stack, kanban-status). | The other skills (real directories) and `.skill-lock.json`. |
| `dotfiles/.agents/` | None. | Per-repo workflow state (sessions, `events.jsonl`, approvals), gitignored. |

`dotfiles/shared/` is the harness-neutral source of truth (not a stow package): `AGENTS.md`, `mcp-servers.json`, `agent-workflow.default.json`, `research-tool-routing.md`, `skills/`, `templates/`.

## Where agent definitions live today

There is effectively **no general custom agent roster**, with one deliberate exception, the `firecrawl` agent (below). Before it, `~/.claude/agents/` was an empty real directory and `scout.md` and `worker.md` sat in `dotfiles/claude/.claude/agents/` without being linked into it (checked 2026-10-15); `~/.pi/agent/agents/` and `~/.config/opencode/agents/` did not exist (Pi gets subagents from the `pi-subagents` npm package; OpenCode defines one inline agent in `opencode.json`). The only other definition on disk is `~/.codex/agents/career-outreach.toml`, unmanaged and untracked. The llm-wiki canonical roster (`claude-setup/agents/`) is empty because commit `d9794e4` (2026-09-16) deleted 18 canonical and 22 generated agents; the owner intends to reintroduce agents later.

## Firecrawl across the four harnesses

Added 2026-10-15 so web research does not depend on one harness's MCP config. The common surface is the `firecrawl` CLI run through each harness's shell tool, plus the `firecrawl*` skills the CLI installs into `~/.agents/skills`, plus one thin `firecrawl` agent per harness. The CLI and skills cost nothing per session beyond the skill list; the MCP server (28 tools) is optional.

| Piece | Where it lives | Notes |
|---|---|---|
| Credential shim | `dotfiles/scripts/firecrawl`, linked to `~/.local/bin/firecrawl` | Reads only `FIRECRAWL_API_KEY` from `~/secrets/.env` and overrides the inherited value, then runs `/opt/homebrew/bin/firecrawl` |
| MCP launcher | `dotfiles/scripts/firecrawl-mcp`, linked to `~/.local/bin/firecrawl-mcp` | Same key loading, then `npx -y firecrawl-mcp`. Used as the MCP `command` so no config file holds a literal key |
| Agent, Claude Code | `dotfiles/claude/.claude/agents/firecrawl.md` (symlink) | Haiku 5.5, tools Bash/Read/Grep/Glob |
| Agent, Codex | `dotfiles/codex/.codex/agents/firecrawl.toml`, **copied** by `sync-agent-rules.sh` | Must be a regular file, see below |
| Agent, OpenCode | `dotfiles/opencode/.config/opencode/agents/firecrawl.md` (symlink) | Subagent; bash denied except `firecrawl *` |
| Agent, Pi | `dotfiles/pi/.pi/agent/agents/firecrawl.md` (symlink) | Spawned through the `subagent` tool |

**Why a shim.** `~/secrets/.env` is sourced only by interactive zsh (`.zshrc`), and a process started before the key was rotated keeps the old value. The CLI prefers the environment variable over any stored login, so a stale inherited key beats the good one on disk and the API answers 401. Measured on 2026-10-15: the key in `.env` returned HTTP 200 while the key in the Claude Code session's environment returned 401. With the shim, a deliberately stale key planted in the environment of each harness process was overridden in every run that got far enough to call Firecrawl. The Claude Code MCP entry, project-scoped to llm-wiki, had the stale key as a literal in `~/.claude.json`; it now points at the launcher.

**Verification (independent agent plus a re-check of the Codex items, 2026-10-15).** T1 = scrape example.com through the CLI, T2 = list visible `firecrawl*` skills, T3 = run the `firecrawl` agent.

| Harness | T1 CLI | T2 skills | T3 agent | What blocked |
|---|---|---|---|---|
| Claude Code | pass | pass (34 listed) | pass | A depleted `ANTHROPIC_API_KEY` inherited from the launching process tree (commented out in `~/secrets/.env`, in no shell or harness file) made every headless `claude -p` fail with "Credit balance is too low"; passed with `env -u ANTHROPIC_API_KEY`, and a fresh terminal should clear it |
| Pi | pass | pass (34) | pass | Default provider (openai-codex) token expired; passed with `--model opencode-go/deepseek-v4-pro` |
| Codex | **fail** | pass (34) | spawns after fix; cannot research while T1 fails | Sandbox network (below) |
| OpenCode | not run | not run | not run | `opencode run` (1.18.30) crashes on every invocation: `TypeError: undefined is not an object (evaluating 'a.name')` in `SystemPrompt.environment`. It crashed the same way with an empty config dir, a fresh data dir, three different models, no skills, plugins, commands or `AGENTS.md`, and no firecrawl agent, so it looks like an OpenCode bug rather than a setup fault. Not ruled out: skill discovery from `~/.claude/skills` or `~/.agents/skills`, because `HOME` could not be changed in the test. Static checks pass: `opencode debug agent firecrawl` resolves it and `opencode debug skill` lists 34 firecrawl skills |

**Codex findings.**

- A symlinked `~/.codex/agents/*.toml` is listed as an available agent type but cannot be spawned ("agent type is currently not available"). Plain-file copies spawn fine, including a copy of the same TOML. Fixed by copying (the sync script now does it); a direct spawn after the fix returned the subagent's reply. The cause is inferred, not confirmed in Codex source: its role loader checks `is_file()` on directory entries.
- The CLI path is blocked: `features.network_proxy = true` in `~/.codex/config.toml` sets no domain allowlist, so the sandbox rejects `api.firecrawl.dev` (`getaddrinfo ENOTFOUND`, then "domain is not on the allowlist for the current sandbox mode"). It passes only with `-c features.network_proxy=false` plus `-s workspace-write -c sandbox_workspace_write.network_access=true`. Switching the proxy off is a security decision and was not applied.
- Tried and failed: a per-profile allowlist (`[permissions.<name>.network.domains]`) as a one-off override. The `-c` parser split the quoted hostname on its dots, and an inline-table form switched Codex onto a profile with no filesystem rules, so the session failed to start. The documented profile route needs a complete profile, not just one domain.
- The MCP launcher started under Codex and its tool was resolved, but headless `codex exec` refused the call with "MCP tool call requires approval, but approval policy is never". That is an approval-policy refusal, so interactive behavior is untested.

**Skill cost.** The CLI installed 34 `firecrawl*` skills into `~/.agents/skills`; their descriptions total about 10,700 characters, roughly 2,700 tokens listed in every session that scans that directory. Codex printed "Skill descriptions were shortened to fit the skills context budget". It also overwrote the `firecrawl` routing skill that `bootstrap-dirs.sh` copies there from `dotfiles/shared/skills/firecrawl`, so the next bootstrap run overwrites the CLI's newer version.

**Agent blueprints** (drafts from the `build-agent` skill) go to `~/dotfiles/docs/agents/<slug>.md`: tracked, next to the builder's spec, and loaded by no harness, so a draft is never mistaken for an installed agent. They are deliberately kept out of the wiki (the skill promises not to modify it) and out of `claude-setup/agents/` (the canonical roster that `sync-agents.py` consumes).

## About "AgentOps"

The older personal Pi/Obsidian project at `~/repos/AgentOps` was torn down deliberately (commits `ece33a9`, `376727f`); the directory no longer exists and the default vault is now `~/repos/Obsidian`. It is unrelated to the external tool on [[entities/agentops]], which is documented-not-adopted. Remaining references in the dotfiles docs were retired in the 2026-10 cleanup, apart from historical teardown notes.

## Related

- [[systems/agent-review]]: the per-run Neovim review gate that lives across `scripts/`, `pi/`, and `nvim/` in this repo.
- [[entities/pi-agent]], [[entities/opencode]], [[entities/codex]]: the harnesses configured here.
- [[concepts/linux-setup-guide]]: bootstrapping this setup on a fresh machine.
