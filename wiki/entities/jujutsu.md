---
title: "Jujutsu (jj)"
type: entity
tags: [jujutsu, jj, version-control, git, dotfiles]
sources: ["jj-vcsjj A Git-compatible VCS that is both simple and powerful.md", "Jujutsu docs.md", "jj-agents-research-2026-10-21/panozzaj-jj.md", "jj-agents-research-2026-10-21/geirsson-jj-workspaces.md", "jj-agents-research-2026-10-21/cc-issue-66503.md", "jj-agents-research-2026-10-21/cc-hooks.md"]
created: 2026-10-19
updated: 2026-11-01
---

> **Contradiction (2026-11-01): the 2026-10-20 decision is superseded.** On 2026-10-20 this page and log.md
> ("jj is human-only, agents stay on Git") recorded that agents use Git only and Claude's settings deny
> `Bash(jj ...)`. That is no longer true. The current global rules (`~/.claude/rules/tool-routing.md`,
> "Git history") make jj the default VCS for agent sessions, colocated with Git, with commits only through
> `~/dotfiles/scripts/commit-funnel`. See "Agent use (current)" below; the old decision is kept for history.

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
- **Decision (2026-10-20), superseded:** jj is human-only, used in the main `~/dotfiles` checkout for history
  editing. Agents use Git only ([[concepts/worktree-isolation]]), and Claude's settings deny `Bash(jj ...)`.
  Reason: `agent-review`, `ac-run`, `floor-guard`, `session-band` and the rtk/safety hooks are all git-specific.

## Agent use (current, as of 2026-11-01)

jj is the default VCS for agent sessions, colocated with Git so the Git-based gates keep working. The
git-specific-gates objection behind the 2026-10-20 decision is answered by colocation plus the commit funnel,
which leaves Git on a named branch after every commit. Research behind the switch:
[[summaries/jj-for-coding-agents]].

- **Colocation per worktree.** `~/.claude/hooks/jj-colocate-worktree.sh`, a `PreToolUse` hook on `Bash`, runs
  `jj git init --colocate` on the first Bash call in a `.claude/worktrees/` checkout. A hook does it because the
  worktree guard refuses every typed `jj git ...` command ([[concepts/claude-code-worktree-guard]]). This works
  on 0.46.0 even though a commenter on Claude Code issue #66503 reported jj refusing to colocate inside a Git
  worktree. Pi runs the init itself.
- **Commits only through the funnel.** `commit-funnel --worktree <path> -F <msg> <path>...` in jj mode runs
  `jj file track`, `jj commit -m ... <paths>`, `jj bookmark move <branch> --to @-` and `git switch <branch>`,
  so `HEAD` is reattached (fixing gotcha 1 for funnel commits). A plain `git commit` or `jj commit` is blocked
  in a `.claude/worktrees/` checkout.
- **Allowed commands.** Claude's settings allow only the subcommands the protocol uses (`st`, `log`, `diff`,
  `show`, `file track`/`list`, `commit`, `describe`, `new`, `squash`, `rebase`, `tug`, `bookmark`,
  `git init`/`fetch`/`push`, `op log`, `undo`). `jj squash` and `jj rebase` are for unpushed commits only;
  the stowed `immutable_heads()` refuses pushed commits and `main`/`master`. `jj util`, `--config`,
  `config set`/`edit`, `--ignore-immutable` and `op abandon` are denied.
- **Not jj workspaces.** Claude Code's `EnterWorktree` validates against `git worktree list` and refuses jj
  workspaces made by a `WorktreeCreate` hook (issue #66503, open as of 2026-09-03). The harness therefore keeps
  Claude Code's Git worktrees and colocates jj inside each one.

## Gotchas

1. In a colocated repo jj detaches Git `HEAD` at `@-`, so `ac-run`'s branch check and starship's branch segment
   break until you run `git switch`.
2. By default auto-track snapshots every untracked file (the same as `git add -A`). The config sets
   `snapshot.auto-track = "none()"`.
3. Every jj command writes, even `jj st`, which snapshots and imports Git refs. jj is unsafe in read-only or
   plan-mode agents.
4. Rewriting a branch that another Git worktree has checked out leaves that worktree stale.
5. jj workspaces are not Git worktrees, so the harness cannot see them. Claude Code's `EnterWorktree` refuses
   them too (issue #66503).
6. **New files over 1 MiB are silently skipped (2026-11-01).** jj's default `snapshot.max-new-file-size` is
   1 MiB. commit-funnel in jj mode, asked to commit a new 10 MB PDF, printed its normal success line, but the
   file was not in the commit and stayed untracked in `jj st`. Raise the limit in the jj config or commit large
   binaries with plain git, and check the commit's file list after committing.
7. **No snapshot daemon.** jj snapshots only when a jj command runs, so edits lost between two jj invocations
   are not recoverable from the op log. Hooks that run `jj status` on `SessionStart`/`PreCompact` (or a shell
   `preexec`) narrow that gap ([[summaries/jj-for-coding-agents]]).
8. **Each worktree's colocated jj repo is independent** (own op log and change ids) while sharing Git refs with
   the main checkout. A commenter on #66503 expects ref import/export between such repos to fight; not observed
   here yet (unverified).
9. Agents debugging jj have run `rm -rf .jj`. Keep durable work in Git commits so jj state stays disposable.

## Workflows

- Rewrite Pi commits instead of reverting them.
- `jj rebase -b X -d main@origin` instead of merging `main` into the branch.
- Quick tweak: `jj new main` plus a bookmark.
- Safety net: `jj op log` / `jj op restore`.
