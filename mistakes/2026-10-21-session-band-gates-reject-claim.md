---
date: 2026-10-21
type: wrong-answer
domain: session-band
severity: low
---

# Claimed the /gates "Reject all" button always runs agent-review skip

## What happened
I told the user that pressing `x` ("Reject all") twice on a review row in the session-band
`/gates` pane runs `agent-review skip`. The claim came from an `rg` hit on `skipArgv` at
`gates.tsx:173`. That call sits inside an `if (row.entry.orphan)` branch. For a normal review
the button sends `:AgentReviewRejectAll <runId>` to a Neovim server in the review's worktree,
so the user got "Could not send Reject all to Neovim" on two runs with no Neovim open.

## What the fix was
Read `gates.tsx:158-190` in full, gave the user the `agent-review skip <runId>` CLI command for
both runs, and corrected the claim in the dotfiles gates-bulk spec.

## Prevention rule
A grep hit is not a read: before saying what code does, read the enclosing branch or function.

## Context
Helping the user clear two pending agent-review runs (docs-sync 35ad8ce7, jj-adoption-decision
f6073a37) and writing the spec for bulk Approve/Skip/Reject in `/gates`.
