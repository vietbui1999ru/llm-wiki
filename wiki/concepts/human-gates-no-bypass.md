---
title: "Human Gates: One Refusal Means Stop"
type: concept
tags: [gates, human-in-the-loop, agent-review, focus, worktree-guard, agent-harness]
sources:
  - "dotfiles shared/research-tool-routing.md (Gates)"
  - "dotfiles scripts/focus, scripts/agent-review, claude/.claude/hooks/enforce-bash-safety.sh"
created: 2026-11-10
updated: 2026-11-10
publish: false
---

# Human Gates: One Refusal Means Stop

A gate is any check in the agent harness that exists so the person, not the agent, makes a decision. When a gate refuses, the agent stops and hands the person the command that unblocks it. It never reaches the same effect another way.

## What counts as a gate

- The focus scripts and the focus guard (`scripts/focus`, the read-only guard for sessions started outside the focus worktree).
- `agent-review`, the per-run review gate for Pi (see [[systems/agent-review]]).
- The worktree and workspace guard on Bash (see [[concepts/claude-code-worktree-guard]]).
- Diff review, and every approval prompt: spec approve, permission prompts, approval dialogs.

## The rule

- **One refusal means stop.** Do not get the same effect with another tool, a copy, a hand edit, an env override, `scripts/focus allow`, or a checkout of a guarded file. Do not suggest those workarounds to the person either.
- **Hand over the unblock.** Report what was blocked (quoting the gate's message), why, and the exact commands the person can run, in order. Then wait.
- **The documented workflow is not a bypass.** Taking the next documented step (committing through the funnel, `scripts/focus switch` to a follow-up branch of the current focus item, `jw new`) is allowed; the agent says so in one line.

`scripts/focus allow` is the person's command only. An agent may propose it, filled in, but never runs it to keep working.

## The incident that prompted it (2026-11-10)

Pi run `5ffc58f4` on `feat/leader-keys` was waiting for approval. Claude committed a review fix inside the run's worktree, so `agent-review approve` refused with `tree-changed`: the tree no longer matched the snapshot the person was approving. Claude then tried three ways to put Pi's file back: `git checkout` (blocked by the focus read-only guard), `cp` (blocked), and the Edit tool. Each attempt treated a refusal as an obstacle rather than a decision point. The correct move was to stop after the first refusal and give the person the recovery steps.

## Why refusal messages name the person's step

The old focus guard message ended with "Unblock once: scripts/focus allow ...". An agent reads text in a tool result as instructions, so that line read as "run this to continue". The revised messages start with "Agent: stop" and address the unblock to the person:

- the focus guard's `deny_message` lists `jwc <branch>`, `scripts/focus switch <key>` and, for a genuine blocker, the filled-in `scripts/focus allow` as options for the person;
- `agent-review` appends a `NEXT` text per refusal reason (`tree-changed`, `already-decided`, `not-confirmed`) without changing the `reason` values that UIs branch on; `tree-changed` points to the person's steps in dotfiles `docs/workflows/agent-review.md#tree-changed`;
- the worktree guard's "aimed at another checkout" refusal tells the agent to stop and tell the person what it needed there.

The general principle matches [[concepts/tool-design-for-agents]]: an error message is a recovery instruction, so it must say whose recovery it is.

## Finishing a focus item

- **Follow-up of the same item: do it.** Once the item's PR is merged, run `scripts/focus drop <done key>` (never `--yes`), then `scripts/focus switch <repo>:<branch>` and `jw new <branch>`, say so in one line, and tell the person to continue in a session started there (`jwc <branch>`). A session can write only where it started.
- **Anything else: hand it over.** New work outside the item, or any step a gate refuses, goes to the person as exact commands.

## Where the rule lives

A marked block (`<!-- gates:start -->` … `<!-- gates:end -->`) kept byte-identical in dotfiles `shared/AGENTS.md` (Codex, OpenCode), `shared/research-tool-routing.md` (Claude Code) and the generated `pi/.pi/agent/AGENTS.md` (Pi, via `scripts/build-pi-agents`). `scripts/tests/test_gate_rules.py` checks the copies match, following the spec-loop block pattern. See [[systems/dotfiles-agent-harness-layout]] for which file each harness loads.

Status 2026-11-10: the rule text and refusal-message changes are in dotfiles PR 283 (draft); the worktree-guard message line is still pending. Codex and OpenCode copies refresh only after `scripts/sync-agent-rules.sh` runs post-merge.

## Related

- [[systems/agent-review]]: the review gate and its `tree-changed` refusal.
- [[concepts/claude-code-worktree-guard]]: the Bash guard that refuses git aimed at another checkout.
- [[systems/dotfiles-agent-harness-layout]]: where the rule files are provisioned.
- [[concepts/agent-harness]]: the harness these gates belong to.
