# Worktree Guard and Commit-Mechanics Rules

Pull page promoted from `global-prevention-rules.md` on 2026-11-01, when that file passed its
45-line cap. These rules apply to agent sessions that commit from git worktrees, spec branches or
the commit funnel. Load them with `qmd query "worktree guard"` when a session works in a
`.claude/worktrees/` checkout or hands a checkout back to the owner.

## Worktree-isolated shell commands
- Commit messages and PR/issue bodies go in a file passed via `-F`/`--body-file`; never inline them
  with double-quoted shell args (2026-06-15).
- In worktree-isolated Claude sessions, run git/gh/rtk-rewritten tools as single literal-path
  commands. Move loops, variables, heredocs and `$(...)` into a `$CLAUDE_JOB_DIR/tmp` script run
  with `python3 -I`, or edit files with Edit/Write. The guard refuses compound forms, any heredoc,
  and `zsh`/`bash` running a script file; rtk can drop variables (2026-10-20; 2026-10-23).
- The session cwd is already the worktree: use relative paths, never `$HOME` in arguments or
  `cd ... &&` chains (2026-10-26).

## Spec branches
- `ac-run` refuses when the current branch differs from SPEC.md's `branch:` (and on detached HEAD):
  check the match first; a side-branch worktree lints a copy with the field rewritten (2026-10-26).

## New files through the commit funnel
- New markdown note in a repo with frontmatter properties (e.g. `status.py` hooks): copy a sibling
  file's frontmatter first; pasted tool output never has it (2026-10-26).

## Handing a checkout back
- Before handing the owner a `switch`/`pull`/`merge` for a checkout, diff its tracked files against
  HEAD now (not a start-of-session snapshot); approval gates and formatters edit tracked files such
  as SPEC.md `status:` (2026-10-26).

Source entries: `mistakes/2026-10-23-claude-code-heredoc-append-worktree-guard.md`,
`mistakes/2026-10-26-worktree-guard-home-expansion.md`, `mistakes/2026-10-26-ac-run-branch-mismatch.md`,
`mistakes/2026-10-26-commit-funnel-missing-frontmatter.md`,
`mistakes/2026-10-26-switch-command-local-changes.md`.
