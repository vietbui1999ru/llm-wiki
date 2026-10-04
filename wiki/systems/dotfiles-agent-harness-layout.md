---
title: "Dotfiles Layout for the Agent Harnesses"
type: concept
tags: [dotfiles, stow, claude-code, codex, pi, opencode, agents, configuration, macos]
sources: ["dotfiles README.md (Packages table)", "dotfiles scripts/restow.sh, bootstrap-dirs.sh, sync-agent-rules.sh", "dotfiles docs/workflows/sync-agents-disk-roster.md", "dotfiles shared/"]
created: 2026-10-04
updated: 2026-10-04
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

There is effectively **no custom agent roster**. `~/.claude/agents/` is an empty real directory; `~/.pi/agent/agents/` and `~/.config/opencode/agents/` do not exist (Pi gets subagents from the `pi-subagents` npm package; OpenCode defines one inline agent in `opencode.json`). The only definition file on disk is `~/.codex/agents/career-outreach.toml`, unmanaged and untracked. The llm-wiki canonical roster (`claude-setup/agents/`) is empty because commit `d9794e4` (2026-09-16) deleted 18 canonical and 22 generated agents; the owner intends to reintroduce agents later.

**Agent blueprints** (drafts from the `build-agent` skill) go to `~/dotfiles/docs/agents/<slug>.md`: tracked, next to the builder's spec, and loaded by no harness, so a draft is never mistaken for an installed agent. They are deliberately kept out of the wiki (the skill promises not to modify it) and out of `claude-setup/agents/` (the canonical roster that `sync-agents.py` consumes).

## About "AgentOps"

The older personal Pi/Obsidian project at `~/repos/AgentOps` was torn down deliberately (commits `ece33a9`, `376727f`); the directory no longer exists and the default vault is now `~/repos/Obsidian`. It is unrelated to the external tool on [[entities/agentops]], which is documented-not-adopted. Remaining references in the dotfiles docs were retired in the 2026-10 cleanup, apart from historical teardown notes.

## Related

- [[systems/agent-review]]: the per-run Neovim review gate that lives across `scripts/`, `pi/`, and `nvim/` in this repo.
- [[entities/pi-agent]], [[entities/opencode]], [[entities/codex]]: the harnesses configured here.
- [[concepts/linux-setup-guide]]: bootstrapping this setup on a fresh machine.
