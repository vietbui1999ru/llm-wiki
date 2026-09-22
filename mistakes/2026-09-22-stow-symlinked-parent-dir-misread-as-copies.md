---
date: 2026-09-22
type: bad-assumption
domain: stow / shell
severity: high
---

# Files under a symlinked directory misread as un-stowed copies

## What happened

While verifying a plan-first handoff in `~/dotfiles`, an audit loop classified deployed
dotfiles by testing `[ -L "$target" ]` on each file path. Four rule files
(`~/.claude/rules/{model-routing,plan-handoff,skill-invocation,startup}.md`) came back as
regular files, so they were reported as hand-written copies that stow no longer managed and
that would silently diverge from the repo.

The parent, `~/.claude/rules`, is itself a stow symlink to
`../dotfiles/claude/.claude/rules`. The "copies" were the repository's own tracked files,
reached through the linked directory. The supposed fix — `rm` each file and `ln -s` a
relative path in its place — therefore ran inside the repository and deleted four tracked
files, replacing them with links that resolved to nothing. `cmp` then reported exit 2
(cannot open) on every one, which is what exposed the error.

## What the fix was

`rm` the four broken links, `git checkout -- claude/.claude/rules/`, then confirm with
`git diff --quiet`, a directory listing, and `cmp -s` through the deployed path (exit 0 on
all four). The correct audit resolves the parent chain first:
`readlink ~/.claude/rules` would have shown the directory link and ended the investigation
before any write.

## Prevention rule

A file is only an un-managed copy if no ancestor directory is a symlink — check the parent
chain with `readlink`/`realpath` before treating a deployed dotfile as drift, and never
delete a config file whose real path has not been resolved and printed.

## Context

Task was closing out `docs/workflows/plan-first-pi-handoff.md`: all committed work verified
green (24 conformance, 123 package, 32 agent-review, 43 nvim checks), and this "drift"
finding was raised as an extra gap. The user approved the fix based on the faulty premise,
which made the bad premise more expensive than the command — flagging a premise as
*inferred, not resolved* matters most right before asking for approval to delete something.
