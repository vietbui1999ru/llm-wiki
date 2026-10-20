---
title: "Jujutsu (jj)"
type: entity
tags: [jujutsu, jj, version-control, git, dotfiles]
sources: ["jj-vcsjj A Git-compatible VCS that is both simple and powerful.md", "Jujutsu docs.md"]
created: 2026-10-19
updated: 2026-10-20
---

# Jujutsu (jj)

Git-compatible version control system (`jj-vcs/jj`, CLI `jj`, Apache-2.0). It uses Git repositories as its
storage layer but has its own model: the working copy is a commit, every operation is logged and undoable,
conflicts are stored in commits, and descendants rebase automatically. Source summary: [[summaries/jujutsu]].

## Facts

| | |
|---|---|
| Kind | Rust CLI VCS; Git backend via `gitoxide`. Only the Git backend is production-ready. |
| Version used here | 0.46.0 (`jj --version`, Homebrew, 2026-10-20). Captured README news stops at 0.24 (Dec 2024). |
| Repo / docs | github.com/jj-vcs/jj; docs at docs.jj-vcs.dev/latest (and `/prerelease` for `main`) |
| Maturity | Experimental, pre-1.0; on-disk format may change. No Git submodule support. |
| Help | `jj help <cmd>`, `jj help -k <keyword>` |

## Git-to-jj mental model

| Git | jj |
|---|---|
| index / staging area, `git stash` | working-copy commit (auto-amended) |
| branch | bookmark (stored outside Git); changes can stay anonymous |
| `git reflog` | operation log (`jj undo`, revert an older operation) |
| `git rebase --update-refs` + `git rerere` | automatic descendant rebase with propagated conflict resolutions |
| interrupted rebase / merge state | conflicts recorded in commits, resolved later |
| `git blame` | `jj file annotate` (since 0.24) |

## Local setup

- Installed at `/opt/homebrew/bin/jj`, 0.46.0 (2026-10-20).
- `~/dotfiles` is a colocated repo: `.jj/` sits next to `.git/` (colocated since 2026-07-02), so plain Git keeps
  working in that checkout.
- Config stowed from the dotfiles `jj` package: `~/dotfiles/jj/.config/jj/config.toml` sets the user identity
  and `ui.diff-editor = ["nvim", "-c", "DiffEditor $left $right $output"]` with `diff-instructions = false`, so
  `jj split` / `jj diffedit` open Neovim instead of jj's built-in editor. `hunk.nvim` provides the `DiffEditor`
  command. See [[systems/dotfiles-agent-harness-layout]].
- **Decision (2026-10-20):** jj is human-only, used in the main `~/dotfiles` checkout for history editing.
  Agents use Git only ([[concepts/worktree-isolation]]), and Claude's settings deny `Bash(jj ...)`. Reason:
  `agent-review`, `ac-run`, `floor-guard`, `session-band` and the rtk/safety hooks are all git-specific.

## Gotchas

1. In a colocated repo jj detaches Git `HEAD` at `@-`, so `ac-run`'s branch check and starship's branch segment
   break until you run `git switch`.
2. By default auto-track snapshots every untracked file (the same as `git add -A`). The config sets
   `snapshot.auto-track = "none()"`.
3. Every jj command writes, even `jj st`, which snapshots and imports Git refs. jj is unsafe in read-only or
   plan-mode agents.
4. Rewriting a branch that another Git worktree has checked out leaves that worktree stale.
5. jj workspaces are not Git worktrees, so the harness cannot see them.

## Workflows

- Rewrite Pi commits instead of reverting them.
- `jj rebase -b X -d main@origin` instead of merging `main` into the branch.
- Quick tweak: `jj new main` plus a bookmark.
- Safety net: `jj op log` / `jj op restore`.
