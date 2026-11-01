---
date: 2026-11-01
type: bad-assumption
domain: commit-funnel
severity: medium
---

# commit-funnel in jj mode: silent large-file skip and lost merge parent

## What happened
1. Committed three PDFs through `commit-funnel` in a jj-colocated worktree. It printed success, but
   the 10 MB PDF was not in the commit and stayed untracked in `jj st`: jj's default
   `snapshot.max-new-file-size` is 1MiB (`jj config get snapshot.max-new-file-size`).
2. To clear PR #67's conflict, ran `git merge --no-commit --no-ff origin/main`, resolved the file,
   and committed through the funnel. The new commit had one parent: jj mode ignored git's
   MERGE_HEAD, so GitHub would still have reported the add/add conflict.

## What the fix was
1. Left the PDF out of the PR (raising the limit needs `--config`/`config set`, which are denied);
   it stayed in the reconcile stash.
2. Before pushing, `jj rebase -r <commit> -d <branch tip> -d <main>` made it a two-parent merge,
   then `jj restore --from <tip> --into <merge> <path>` resolved the conflict. Push was a normal
   fast-forward.

## Prevention rule
Assumed the funnel's success line meant every listed path landed. Verify with `git show --stat HEAD`
after any funnel commit that adds large files or finishes a merge. Recorded in
`mistakes/worktree-guard-rules.md`. Suggested dotfiles fix: the funnel should fail when a listed
path is missing from the new commit.

## Context
2026-11-01 reconcile and ingest batch (PRs #66, #67).
