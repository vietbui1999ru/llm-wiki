---
title: "Jujutsu (jj): Git-compatible VCS (README + docs index)"
type: summary
tags: [jujutsu, jj, version-control, git, rebase, conflicts, stacked-diffs]
sources: ["jj-vcsjj A Git-compatible VCS that is both simple and powerful.md", "Jujutsu docs.md"]
created: 2026-10-19
updated: 2026-10-19
---

# Jujutsu (jj): Git-compatible VCS

GitHub README of `jj-vcs/jj` (Apache-2.0), plus the docs landing page (`docs.jj-vcs.dev`), both captured
2026-10-18. The docs page is only a link hub (install, tutorial, Git comparison, GitHub/Gerrit guides,
roadmap, changelog) and adds no claims. See [[entities/jujutsu]] for the identity page and local setup.

> **Stale capture:** the README's "News" section ends at December 2024 (v0.24), but the version installed
> here is 0.45.1. Treat the release history below as old; check the changelog for current behaviour.

## Problem

Git exposes several separate mechanisms (index, stash, dirty-working-copy errors, interrupted rebases,
reflog) that users have to keep track of. jj aims for one simpler model that still works with Git remotes and
tools, and that scales from solo projects to large histories.

## Design

- **Storage-abstracted.** The UI and the VCS algorithms are separate from the storage backend. Only the Git
  backend (built on the `gitoxide` Rust library) is production-ready. Commits and files live in Git;
  bookmarks (branches) and other higher-level metadata live in jj's own storage outside Git.
- **Git interop.** Commits are ordinary Git commits. jj fetches from and pushes to any Git remote, and you can
  switch back to Git at any time. A *colocated workspace* lets you run `jj` and `git` commands in the same
  directory.
- **Borrowed ideas.** From Git: speed and the Git storage format. From Mercurial/Sapling: the revset language
  for selecting commits, no staging area, anonymous branches (no name needed per change), and a template
  language for output. From Darcs: conflicts as first-class objects (snapshot-based, not patch theory).

## jj's own features

| Feature | What it means | Git equivalent it replaces |
|---|---|---|
| Working copy is a commit | File changes are recorded as a real commit, amended on every command. Commands never fail on a dirty tree. You can describe the commit before you finish it. | index/staging area, `git stash` |
| Repo is the source of truth | Commands snapshot the working copy, act on commits in the repo, then update the working copy. `jj restore` and `jj describe` work on any commit. | checkout-centric commands |
| Operation log + undo | Every operation (commit, pull, push) is recorded with a repo snapshot. You can undo step by step, or revert an older operation that isn't the latest. | `git reflog` (only per-ref, and not for every operation) |
| Conflicts recorded in commits | A conflicting operation still succeeds; the conflict is stored in the commit and resolved later. No "continue an interrupted operation" state. Merge commits rebase correctly. | `git rebase --continue`, conflict markers in the working tree |
| Automatic rebase | Editing a commit rebases all descendants, even when there are conflicts; bookmarks and the working copy follow. A resolution propagates to descendants. | `git rebase --update-refs` + `git rerere` |
| Concurrent-safe replication *(experimental)* | Repos are designed to stay uncorrupted under Dropbox/rsync-style concurrent copies; at worst you see conflicts between local and remote state. | none (Git assumes atomic local fs ops) |

History-rewrite commands named in the README: `jj describe` (edit any commit's message), `jj diffedit` (edit a
commit's changes without checking it out), `jj split`, and `jj squash -i --from X --into Y` (move part of one
commit into another).

## Status and limits (as of the capture)

- Described as experimental; Git compatibility stable; core developers use it daily.
- Not yet supported: Git submodules, native email-based workflows. Known performance bugs.
- Backward-incompatible on-disk format and workflow changes are expected before 1.0.0; the project tries to
  upgrade formats transparently.
- Started by Martin von Zweigbergk (2019), now his full-time project at Google, but "not a supported Google
  product". Contributions need a CLA that does not transfer copyright.

## Wiki connections

- [[concepts/worktree-isolation]]: that page recommends `git rerere` for agents editing the same files in
  sequential waves. jj's propagated conflict resolution does this by design, though no agent setup here uses
  jj that way yet.
- `gh-stack` / stacked PRs: jj's automatic descendant rebase is the core operation stacked-diff tools emulate
  on top of Git.
- [[systems/dotfiles-agent-harness-layout]]: dotfiles stows a `jj` package (see [[entities/jujutsu]]).
