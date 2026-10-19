---
title: "Jujutsu (jj)"
type: entity
tags: [jujutsu, jj, version-control, git, dotfiles]
sources: ["jj-vcsjj A Git-compatible VCS that is both simple and powerful.md", "Jujutsu docs.md"]
created: 2026-10-19
updated: 2026-10-19
---

# Jujutsu (jj)

Git-compatible version control system (`jj-vcs/jj`, CLI `jj`, Apache-2.0). It uses Git repositories as its
storage layer but has its own model: the working copy is a commit, every operation is logged and undoable,
conflicts are stored in commits, and descendants rebase automatically. Source summary: [[summaries/jujutsu]].

## Facts

| | |
|---|---|
| Kind | Rust CLI VCS; Git backend via `gitoxide`. Only the Git backend is production-ready. |
| Version used here | 0.45.1 (`jj --version`, Homebrew, 2026-10-19). Captured README news stops at 0.24 (Dec 2024). |
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

- Installed at `/opt/homebrew/bin/jj`.
- Config stowed from the dotfiles `jj` package: `~/dotfiles/jj/.config/jj/config.toml` sets the user identity
  and `ui.diff-editor = ["nvim", "-c", "DiffEditor $left $right $output"]` with `diff-instructions = false`, so
  `jj split` / `jj diffedit` open Neovim instead of jj's built-in editor. See
  [[systems/dotfiles-agent-harness-layout]].
- Agent workflows here still run on plain Git worktrees ([[concepts/worktree-isolation]]); jj is not part of
  the agent harness.
