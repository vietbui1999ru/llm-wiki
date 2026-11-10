---
date: 2026-11-05
type: bad-assumption
domain: agent-review
severity: medium
---

# Read an untagged `agent-review list` row as an unresolved review

## What happened
After the person accepted every file in a Pi run's review in Neovim, `agent-review list` still
showed the run with no tag. Claude reported it twice as an unresolved review that would refuse
the next Pi dispatch, and asked the person to resolve it again, even though they already had.

## What the fix was
An accept-all decision is "quiet" and is never tagged `decided` (`scripts/agent-review`
`scan` :176-178 and `quiet_decision` :312). Its pending file stays until the next Pi
`session_start` consumes the decision (`pi/.pi/agent/extensions/agent-review/index.ts:681-694`).
A trivial Pi run (pueue task 49) confirmed it: at startup it consumed the decision and was not
refused.

## Prevention rule
Before telling the person that a tool's state needs their action, read in the tool's source what
an absent tag or status means. For agent-review, an untagged pending row plus an existing
`decisions/<run>.json` is a quiet decision, and a dispatch proceeds.

## Context
feat/focus in dotfiles: gating Dispatch 2 (hook registration) on review a4aece93 of Dispatch 1b.
