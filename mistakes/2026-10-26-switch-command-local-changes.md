---
date: 2026-10-26
type: bad-assumption
domain: git
severity: low
---

# Gave the owner a `git switch` command without checking their checkout for local edits

## What happened
Told the owner their main checkout had "only untracked folders, so the switch won't conflict" and gave them `git switch spec/rev10-replan-review`. The switch failed: the session-band `/gates` approval had rewritten `SPEC.md` frontmatter (`status: draft` → `status: approved`) in that checkout, and the branch changes `SPEC.md`. The "only untracked" claim came from the git status snapshot taken at session start, hours earlier.

## What the fix was
Diffed the checkout's `SPEC.md` against the committed version (no git in the foreign checkout), found the tool-written status line, and gave `git restore SPEC.md` before the switch, noting that the approval record lives outside the repo.

## Prevention rule
Before giving the owner any `switch`, `pull` or `merge` command for a checkout, diff that checkout's tracked files against HEAD now, not from a start-of-session snapshot; tools such as approval gates and formatters edit tracked files (SPEC.md status, tables) behind the scenes.

## Context
Moving the owner's main checkout to the rev 10 spec branch so they could read it in Obsidian.
