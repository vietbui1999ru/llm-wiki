---
title: "Jujutsu (jj) for Coding Agents"
type: summary
tags: [jujutsu, jj, version-control, git, worktrees, claude-code, hooks, agent-harness]
sources:
  - "jj-agents-research-2026-10-21/panozzaj-jj.md"
  - "jj-agents-research-2026-10-21/geirsson-jj-workspaces.md"
  - "jj-agents-research-2026-10-21/cc-issue-66503.md"
  - "jj-agents-research-2026-10-21/cc-hooks.md"
created: 2026-11-01
updated: 2026-11-01
---

# Jujutsu (jj) for Coding Agents

Research cluster captured 2026-10-21 while deciding whether agents in this harness should use jj. Four sources:

| Source | Kind | Date | What it contributes |
|---|---|---|---|
| Anthony Panozzo, "Avoid Losing Work with Jujutsu (jj) for AI Coding Agents" | Blog post (updated 2026-01-23) | 2025-11-22 | jj as a passive safety net under an agent: snapshots, `obslog`, Claude Code hooks that force snapshots |
| Olafur Geirsson, "Operate a local autonomous GitHub with jj workspaces" | Blog post | 2026-01-25 | jj workspaces (not Git worktrees) as the isolation unit for parallel agents, with an agent doing the merging |
| anthropics/claude-code issue #66503 | GitHub issue (open, `area:hooks`, `has repro`) | 2026-06-09 to 2026-09-03 | `EnterWorktree` refuses jj workspaces created by a `WorktreeCreate` hook; workaround attempts and why they break |
| Claude Code hooks reference (code.claude.com/docs/en/hooks) | Official docs | captured 2026-10-21 | Contract for `WorktreeCreate`/`WorktreeRemove`, `SessionStart`, `PreCompact` |

All experience reports are single-author anecdotes with no measurements. For the tool itself see [[entities/jujutsu]]; for the general isolation pattern see [[concepts/worktree-isolation]].

## 1. jj as a safety net under an agent (Panozzo)

Problem: agents lose uncommitted work. Examples cited: a Gemini CLI session that ran `git clean` and deleted untracked files, an agent reverting its own changes, and context compaction clearing the terminal so the agent forgets what it changed.

Approach: `jj git init --colocate` in an existing Git repo. jj records the working copy as a commit (`@`) and keeps every prior snapshot in the operation log, so `jj obslog -r @ --patch` (newer jj: `jj evolog`) shows earlier states of the working copy and lets you restore them. Git users of the repo see nothing different.

The author's own correction (2026-01-23) is the important part: **jj has no file-watching daemon. It snapshots only when a `jj` command runs.** Edits made and lost between two jj invocations are not recoverable. To make snapshots frequent he uses:

- a zsh `preexec` hook running `jj status` before every shell command;
- Claude Code hooks running `[[ -d .jj ]] && jj status` on `SessionStart` and `PreCompact`, the two moments he judges most likely to precede lost context;
- optionally a `PreToolUse` hook doing the same; `jj status` took about 0.01 s on his blog repo (single `time` run, unverified), with unmeasured hook-invocation overhead.

He relies on the agent knowing enough jj to recover changes when asked, and notes agents do not otherwise reach for jj on their own. That observation predates this harness making jj the agent default (see [[entities/jujutsu]]).

## 2. jj workspaces for parallel agents (Geirsson)

Setup: Cursor CLI agents, each in its own jj workspace (`jj workspace add ../pet-store-N`), each with its own terminal tab and dev server on a separate port. A "merge-workspaces" skill (a gist) asks an agent to combine the workspaces' changes using revsets with `jj duplicate`, `jj rebase` and `jj squash`. The author reports 150 commits and 40k lines of TypeScript over five days, roughly 700 million tokens (claimed, unverified), merged entirely by agents and never code-reviewed by him; he tested only the product, and says himself it is undetermined whether the week was productive or "burnt a metric ton of tokens to produce slop".

Why he tried separate checkouts at all: a single shared checkout made the hot-reloading dev server show other agents' half-finished edits, the same failure [[concepts/worktree-isolation]] describes.

Rough edges he reports with jj workspaces:

1. Editing a change that is an ancestor of another workspace's working copy leaves that workspace "stale"; `jj workspace update-stale` usually fixes it.
2. All jj commands occasionally hung for several minutes, cause unknown.
3. `jj log` from one workspace does not snapshot the others, so it shows outdated state for them. Fix: an alias that snapshots every workspace first.
4. Asked to debug the hang, the agent ran `rm -rf .jj`. Nothing was lost because a colocated repo's commits live in Git, but jj-only state (op log, uncommitted snapshots) was gone.

His takeaway: keep jj state small and close to disposable; abandon dead experiments so `jj log` fits on one screen.

## 3. Claude Code's worktree hooks are Git-shaped (issue #66503 and hooks docs)

**Documented contract (hooks reference).** `WorktreeCreate` fires for `claude --worktree`, `EnterWorktree`, subagent `isolation: "worktree"`, workflow agents, background sessions and `claude remote-control` in worktree mode. A configured hook *replaces* the default `git worktree add`; the docs name SVN, Perforce and Mercurial as intended uses. A command hook prints the absolute worktree path as the last non-empty line of stdout (other output to stderr); a non-zero exit fails creation. `.worktreeinclude` is not processed when a hook is used. A `git worktree add` typed into the Bash tool does not fire the hook.

`WorktreeRemove` is the counterpart, with several Git assumptions that matter for jj:

- Claude Code checks for uncommitted work with git, so in a non-git directory it sees none even when work exists. The remove hook must check itself before deleting.
- Without a remove hook, cleanup falls back to `git worktree remove --force`, which leaves a non-git worktree on disk.
- Worktrees created for subagents and workflow agents are kept, and the remove hook is not run; clean them up yourself.
- Claude Code never deletes a branch for a hook-created worktree.

**The bug (#66503, Claude Code 2.1.169, macOS).** With a `WorktreeCreate` hook that runs `jj workspace add`, creation succeeds but `EnterWorktree` then validates the returned path against `git worktree list` and refuses it ("is not a registered worktree"). In a background session this is a hard block, because the write-isolation guard rejects every Write/Edit until `EnterWorktree` succeeds. Related: #36205 (hook not fired, since fixed) and #60497 (`isolation: "worktree"` does not fire the hook). As of the capture (last activity 2026-09-03) the issue was open, unassigned, with no maintainer response.

**Workaround attempts in the thread:**

- A commenter made each jj workspace *also* a Git worktree by hand-writing `.git/worktrees/<name>/` (`commondir`, `gitdir`, `HEAD` at `@-`), a `.git` pointer file, `git read-tree HEAD`, and `.jj/.gitignore` containing `/*`, plus a conservative remove hook that only deletes paths under `.claude/worktrees/` containing `.jj`. His reasons for not using a plain Git worktree: Claude Code cuts it from `origin/<default>`, which lagged `jj @` by 11 commits in his test, and with no `.jj` inside it `jj st` silently walks up to the main checkout and edits the main working copy.
- The same commenter then found the hybrid broken: jj's backing Git repo is the root repo, not the worktree, so `jj new` in the workspace never moves the worktree's Git `HEAD`, and Git commands there use the wrong index; `git checkout` can undo jj working-copy changes. His final advice was to use plain `git worktree` with `"worktree": {"baseRef": "head"}` in settings.
- He also reported that jj refuses `jj git init --colocate` inside a Git worktree ("Cannot create a colocated jj repo inside a Git worktree"). **This does not reproduce here** (see below).

## How this harness resolved it (2026-10/11)

The local setup takes a route none of the sources describe: keep Claude Code's own Git worktree, and colocate a separate jj repo inside it.

- `~/.claude/hooks/jj-colocate-worktree.sh`, a `PreToolUse` hook on `Bash`, runs `jj git init --colocate` the first time a session in a `.claude/worktrees/` checkout uses Bash. It exists because the worktree guard refuses every typed `jj git ...` command ([[concepts/claude-code-worktree-guard]]). On jj 0.46.0 this works: the ingest worktree for this page has `.jj/repo/store/git_target` pointing at the worktree's `.git` pointer file, which resolves to `.git/worktrees/<name>` in the main repo.
- Agents commit only through `~/dotfiles/scripts/commit-funnel`, which in jj mode runs `jj file track <paths>`, `jj commit -m <msg> <paths>`, `jj bookmark move <branch> --to @-` and `git switch <branch>` so Git-based gates (`ac-run`, `agent-review`) see a branch, not a detached `HEAD`.
- No `WorktreeCreate` hook is used, so issue #66503 does not apply, and the `jj st` walk-up problem does not arise because each worktree has its own `.jj`.

Unverified risk carried over from the issue thread: each worktree's jj repo is independent (own op log, own change ids) while sharing Git refs with the others, so ref import/export between them could conflict. No such conflict has been observed yet.

**Gotcha observed 2026-11-01.** jj's default `snapshot.max-new-file-size` is 1 MiB. commit-funnel in jj mode was asked to commit a new 10 MB PDF; it printed its normal success line, but the PDF was not in the commit and stayed untracked in `jj st`. jj skips new files above the limit when snapshotting or tracking, and the funnel does not check that every listed path landed in the commit. Mitigation: raise `snapshot.max-new-file-size` in the jj config, or commit large binaries with plain git, and verify the commit's file list after committing.

## Takeaways

1. jj's undo value depends on snapshot frequency; with no daemon, a hook (shell `preexec`, Claude Code `SessionStart`/`PreCompact`/`PreToolUse`) is what makes it a safety net.
2. Claude Code's isolation machinery (`EnterWorktree`, remove-time dirty checks, the worktree guard) assumes Git. jj workspaces fight it; jj colocated inside a Git worktree goes with it.
3. Agents are fluent enough in jj to do multi-workspace merging, and fluent enough to `rm -rf .jj` when debugging. Keep jj state disposable and keep commits in Git.
4. Any tool that commits through jj must verify the result: jj silently ignores oversized new files.

## Wiki connections

- [[entities/jujutsu]] — tool page; decision history and gotchas
- [[concepts/worktree-isolation]] — the isolation pattern these sources vary
- [[concepts/claude-code-worktree-guard]] — why typed `jj git` commands are refused in worktree sessions
- [[summaries/jujutsu]] — README and docs summary of jj itself
- [[concepts/rules-vs-hooks]] — hooks as the enforcement layer, here for snapshots and colocation
- [[concepts/context-compression]] — compaction as the moment work is forgotten (Panozzo's `PreCompact` hook)
