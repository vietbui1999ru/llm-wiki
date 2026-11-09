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
- The guard also refuses inline `python3 -c` (or any `-c`/`-e` code) whose text merely mentions
  "git", even inside string literals; write content with Write instead (2026-11-01).
- After one guard refusal, change the form of the command (a tmp script file, separate plain
  commands) instead of retrying near-identical variants (2026-10-27). Reports differ on `zsh
  <script>` (accepted 2026-10-27, refused 2026-10-23); `python3 -I <script>` is the reliable form.
- The session cwd is already the worktree: use relative paths, never `$HOME` in arguments or
  `cd ... &&` chains (2026-10-26).

## Spec branches
- `ac-run` refuses when the current branch differs from SPEC.md's `branch:` (and on detached HEAD):
  check the match first; a side-branch worktree lints a copy with the field rewritten (2026-10-26).

## New files through the commit funnel
- Run `commit-funnel` from the worktree root: it resolves path arguments against the shell's cwd,
  not `--worktree`, and a `cd` into a subdirectory for tests persists (2026-11-05).
- New markdown note in a repo with frontmatter properties (e.g. `status.py` hooks): copy a sibling
  file's frontmatter first; pasted tool output never has it (2026-10-26).
- In a jj-colocated worktree, `commit-funnel` skips new files over jj's 1 MiB
  `snapshot.max-new-file-size` and still prints success: after committing a large file, check it is
  in the commit (`git show --stat HEAD`) (2026-11-01). Fix without touching jj config (`--config`
  and `config set` are denied): `jj file track --include-ignored <path>` first, then the funnel
  (2026-11-02).
- `commit-funnel` in jj mode ignores a pending `git merge --no-commit` and makes a one-parent commit.
  To finish a merge, give your unpushed commit a second parent with `jj rebase -r <rev> -d <tip> -d
  <other>` and resolve with `jj restore --from <rev> --into <merge> <path>` (2026-11-01).
- A jj bookmark follows its own commit through a rebase, not the tip of the stack. `jj rebase -r
  <tip> -B <earlier>` leaves the bookmark mid-stack and a plain push drops every commit above it
  (dotfiles #237 lost its spec-archive commit). Before pushing after any reorder, check
  `jj log -r '<bookmark>+'` is empty; if not, `jj bookmark set <bookmark> -r <new tip>` (the
  owner's move) and push again (2026-11-03).

## Handing a checkout back
- Before handing the owner a `switch`/`pull`/`merge` for a checkout, diff its tracked files against
  HEAD now (not a start-of-session snapshot); approval gates and formatters edit tracked files such
  as SPEC.md `status:` (2026-10-26).

Source entries: `mistakes/2026-10-23-claude-code-heredoc-append-worktree-guard.md`,
`mistakes/2026-10-26-worktree-guard-home-expansion.md`, `mistakes/2026-10-26-ac-run-branch-mismatch.md`,
`mistakes/2026-10-26-commit-funnel-missing-frontmatter.md`,
`mistakes/2026-10-26-switch-command-local-changes.md`,
`mistakes/2026-10-27-worktree-guard-retry-variations.md`, `mistakes/2026-10-29-worktree-guard-for-loop.md`,
`mistakes/2026-11-01-worktree-guard-inline-python-git-text.md`, `mistakes/2026-11-01-commit-funnel-jj-gaps.md`.
