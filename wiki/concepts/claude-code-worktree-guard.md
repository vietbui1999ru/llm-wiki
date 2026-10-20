---
title: "Claude Code Worktree-Isolation Guard"
type: concept
tags: [claude-code, worktree-isolation, bash-guard, agent-harness, rtk, hook, git]
sources:
  - "claude-code-worktree-guard-issues-2026-10-20.md"
  - "Bug Worktree isolation guard rejects non-git commands due to early AST complexity check · Issue 84720.md"
  - "BUG 2.1.222 escalates 82966 to ordinary sessions worktree isolation refuses every `source``.` via an interpreter denylist, with no opt-out · Issue 84530 1.md"
  - "BUG 2.1.222 escalates 82966 to ordinary sessions worktree isolation refuses every `source``.` via an interpreter denylist, with no opt-out · Issue 84530.md"
created: 2026-10-20
updated: 2026-10-20
---

# Claude Code Worktree-Isolation Guard

When a Claude Code session is isolated in a worktree (`EnterWorktree`, `isolation: "worktree"` subagents, background jobs), the harness statically checks every Bash command before it runs. If it cannot prove that git operations stay inside the session's own worktree, it refuses the command with "Refusing to run it — a worktree-isolated session's git operations must target its own worktree." Since 2.1.222 this applies to every session type, and it cannot be switched off. Evidence: [[summaries/claude-code-worktree-guard-issues]].

The guard is conservative by design: it does not run or simulate the command, so anything whose target directory or executable is only known at runtime counts as unverifiable.

## Refusal classes (as of 2.1.304)

| Class | Example | Status |
|---|---|---|
| Launcher-wrapped git | `rtk git status` (from the rtk hook rewrite), `rtk proxy git …` | Refused. rtk PR #3879 stops the rewrite in worktrees; typing `rtk git` yourself stays refused |
| Tilde paths | `git -C ~/repo/wt status` | Refused (#88550, open). `$HOME/…` passes |
| git aimed outside the worktree | `git -C <main checkout>`, `cd <main> && git …`, `GIT_DIR=…` | Refused by design (2.1.216) |
| Interpreter builtins | `source x.sh`, `. x.sh`, `eval …` | Refused by denylist (#84530) |
| Runtime-computed paths | `cd $(…)`, `$T` in a path | Often refused |
| Nested expansions | `"$(… $(…) …)"` | Refused again since 2.1.274 |
| The word "git" inside argument prose | `pueue add "… git …"`, `--body "…git…"` | Can be refused; text is scanned |

No longer refused (fixed 2.1.257/2.1.259): plain loops, heredocs, `$VAR` reads and `"$(…)"` that never touch git. `&&`, pipes and redirects pass on their own.

## Workaround matrix

| Workaround | Effect | Keep isolation? |
|---|---|---|
| Hook wrapper: skip the rtk rewrite when cwd is under `*/.claude/worktrees/*` | Removes the commonest refusal at the source | Yes |
| Call `/usr/bin/git` by absolute path | rtk does not rewrite it | Yes |
| `$HOME` or absolute paths instead of `~` | Satisfies the path check | Yes |
| Commit message and PR body in files (`git commit -F`, `gh pr create --body-file`) | Keeps "git" prose out of arguments | Yes |
| Multi-step logic in a script run as `bash script.sh` | Passes, but hides the commands from the check | Technically, but it defeats the check rather than satisfying it |
| `ExitWorktree(keep)` then `cd` into the worktree | Guard no longer applies | No; needs explicit user consent |
| Disable isolation, WorktreeCreate hooks | Not possible / no effect | — |

## Removal criteria

These are bandaids for specific bugs. Remove each one when its bug is fixed:

- rtk stable release containing PR #3879 → drop the hook wrapper and the `/usr/bin/git` rule.
- claude-code#88550 closed → drop the "no `~`" rule.
- The other rules (no git outside own worktree, no `source`) are by design and stay.

## Related

- [[entities/rtk]] — the PreToolUse rewrite that collides with the guard.
- [[concepts/worktree-isolation]] — the isolation model the guard enforces.
- [[concepts/agent-subagents]] — `isolation: "worktree"` subagents.
- [[concepts/agentic-sandbox-controls]] — the broader sandboxing picture.
- Local record: `mistakes/2026-10-20-claude-code-worktree-guard-compound-bash.md`; dotfiles workflow `docs/workflows/worktree-guard-bandaid.md`.
