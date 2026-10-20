---
title: "Claude Code worktree-guard issues (rtk#3864, claude-code#84720, #88550, #84530, #40164)"
type: summary
tags: [claude-code, worktree-isolation, bash-guard, rtk, hook, agent-tooling, bug-report]
sources: ["raw/claude-code-worktree-guard-issues-2026-10-20.md"]
created: 2026-10-20
updated: 2026-10-20
---

# Claude Code worktree-guard issues

Five GitHub issues collected while debugging "...names git in a form too complex to verify that it stays inside the worktree. Refusing to run it" in a worktree-isolated `~/dotfiles` session. Captured 2026-10-20 against Claude Code 2.1.304 and rtk 1.0.1. The guard itself is described in [[concepts/claude-code-worktree-guard]].

## The five issues

| Issue | State | What it is really about | Fix status |
|---|---|---|---|
| rtk-ai/rtk#3864 | closed 2026-10-17 | `rtk hook claude` rewrites `git X` to `rtk git X`; the guard cannot prove the launcher-wrapped form is safe, so every git call is refused | rtk PR #3879 skips the rewrite when cwd is `<repo>/.claude/worktrees/<name>`. Merged after v1.0.1, so not in a stable release yet |
| claude-code#84720 | closed (stale) | An early "is this a simple command" AST check refused loops, heredocs, `$(…)` and `${VAR:-}` even with no git in them | Claude Code 2.1.257 and 2.1.259 fixed the non-git false positives; 2.1.274 tightened nested expansions again |
| claude-code#88550 | open | The guard never expands `~`; `$HOME` is expanded. Pipes, `&&`, redirects and `git -C <own worktree>` pass | None |
| claude-code#84530 | closed (stale) | `source`, `.`, `eval` and 12 other interpreter builtins are refused by a denylist; maintainer: "not switchable off" | None; use `bash -lc` or an executed script |
| claude-code#40164 | closed (stale) | Windows failing to *create* worktrees; unrelated to the Bash guard | n/a |

## Weighing a Google-AI summary of fixes

A Google AI answer proposed five fixes, citing these issues. Checked against the issue text:

| Suggestion | Verdict | Why |
|---|---|---|
| Replace `~` with `$HOME` or absolute paths | Accept | Directly reported in #88550, still open |
| Stop wrappers (rtk) rewriting git in worktrees | Accept | Root cause in rtk#3864; the wrapper-hook workaround is confirmed by several commenters |
| Split chained commands, pipes, `&&`, redirects | Partial | #88550 shows `&&` and pipes pass. Loops and heredocs were fixed in 2.1.257/2.1.259. What still fails: nested expansions, `source`/`.`/`eval`, runtime-computed paths, and launcher-wrapped git. The #84530 citation is about `source`, not chaining |
| Don't use `-C /other/path` | Accept, mis-cited | Refusing `git -C`, `--git-dir` and `GIT_DIR` into the shared checkout is by design since 2.1.216. `-C` aimed at the session's own worktree passes |
| Disable isolation or use WorktreeCreate hooks to bypass detection | Reject | The guard cannot be turned off (#84530). Changelog 2.1.144 says the guard still applies with WorktreeCreate hooks. #40164 is about Windows worktree creation, not the guard |

Lesson: AI-generated issue summaries attach plausible fixes to the wrong citations. Read the issue before acting on a claimed workaround.

## Version timeline

- 2.1.210: worktree-isolated subagents blocked from git-mutating the main checkout.
- 2.1.216: "too complex to verify" refusal appears; `git -C`/`GIT_DIR` redirection into the shared checkout refused.
- 2.1.222: isolation extended to file edits and Bash in every session type; interpreter denylist reaches ordinary sessions.
- 2.1.257, 2.1.259: non-git loops, heredocs, `$(…)`, xargs pipelines and launcher-wrapped commands that cannot reach the main checkout no longer refused.
- 2.1.274: some nested shell expansions refused again.
- 2.1.304: current at capture; #88550 still open; rtk 1.0.1 still rewrites git.

## Connections

- [[concepts/claude-code-worktree-guard]] — refusal classes, workaround matrix, removal criteria.
- [[entities/rtk]] — the rewrite hook behind the most common refusal.
- [[concepts/worktree-isolation]] — why sessions run in worktrees in the first place.
