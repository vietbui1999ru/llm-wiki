---
title: "Making Claude Pro Limits Last with Opus and Subagents (Grandi)"
type: summary
tags: [claude-code, subagents, model-selection, usage-limits, cost, delegation, context-isolation]
sources: ["How I use Claude Code subagents to make my Claude Pro limits last longer.md"]
created: 2026-10-09
updated: 2026-10-09
---

# Making Claude Pro Limits Last with Opus and Subagents (Grandi)

A blog post by Andrea Grandi (the name is inferred from the `github.com/andreagrandi/...` repository links; the clipped text carries no byline or date). He runs Claude Code daily on side projects on the flat-fee Claude Pro plan, where the scarce resource is usage per 5-hour and weekly window, not money. Until the change he describes, every session ran on Opus 5.5 from start to finish, including reading files, running tests, fixing lint and opening the pull request. His fix: keep Opus on decisions and push the mechanical work to cheaper subagents. All numbers below are **self-reported by one author on his own projects**; see Caveats.

## The setup

Four custom subagents in `~/.claude/agents/*.md` (frontmatter sets model, effort and tools, the body is the system prompt). The main session stays on Opus 5.5 at medium effort; effort for Opus 5.5 and Sonnet 5.5 is set under `modelSettings` in `~/.claude/settings.json`.

| Agent | Model | Effort | Tools | Job |
|---|---|---|---|---|
| `scoper` | Haiku (reported as "5.5", see Caveats) | medium | Read, Grep, Glob, Bash; plan permission mode, 12-turn cap | Collects facts before planning an unfamiliar task |
| `implementer` | Sonnet 5.5 | medium | Read, Write, Edit, Grep, Glob, Bash | Writes code and tests, runs the checks |
| `reviewer` | Opus 5.5 | medium | Read, Grep, Glob, Bash | Independent review, only when asked or for risky changes |
| `shipper` | Haiku (same caveat) | low | Read, Bash; 10-turn cap | Commits, pushes, opens the pull request |

Creating the agents is not enough: Claude Code decides when to delegate from each agent's `description`, so he also put standing delegation instructions in his user `CLAUDE.md` (when to delegate, what a handoff contains, how to review what comes back).

## How a session runs

1. He hands the main session an issue number.
2. Unless the change touches a few files it has already read, `scoper` runs and writes a short brief (goal, acceptance criteria, relevant code, scope, validation, risks, possible split) in which every claim cites a file. The main session spot-checks a few of those files because a small model can be wrong. Checks that need the network stay in the main session.
3. The main session decides the implementation.
4. It hands `implementer` the plan with acceptance criteria, files, decisions already taken and commands to run. The implementer starts with an empty context, so nothing may be left for it to rediscover.
5. The main session reads the diff, compares it with the plan and runs the whole suite. Fixes go back to the same implementer with `SendMessage` so it keeps its context.
6. On request, `shipper` checks the tree, stages only the task's files by name, commits, pushes and opens the PR with a description.

## Rules that make it work

- **Small changes stay in the main session.** Writing a handoff and reviewing a diff cost tokens too; a few known lines are cheaper to write directly.
- **The implementer does not redesign.** If the plan and the code disagree it reports back instead of taking a large decision.
- **The scoper cannot change anything**: no edit tools, plan mode, capped turns. It flags a task as complex when it spans subsystems, changes a published format or API, involves concurrency, security, a migration or cached data, lacks acceptance criteria, or when it could not find where the behaviour lives.
- **The shipper stops instead of fixing**: unrelated file, missing changelog entry, default branch. It never edits files, force-pushes, bypasses hooks or merges, and has fallbacks for failed commit signing and refused SSH pushes.
- **One review by default.** The main session reviews every diff itself (inspect the diff, compare with the plan, check callers and tests, run the suite). `reviewer` runs only on request or for security, concurrency, data-migration, state-machine or public-API changes, because a second Opus review costs almost as much as writing the code.
- **Escalation:** architecture-heavy, concurrency, security, complex migrations, state machines, broad public API changes and tightly coupled subsystems stay in the main session, as does work where the implementer keeps diverging from the plan.

## How he measured

His status-line script appends to `~/.claude/usage-log.jsonl` whenever the 5-hour or 7-day used-percentage changes (Claude Code passes `rate_limits` and session cost to the script as JSON). He matched sessions to the PRs they opened by finding `gh pr create` calls in the transcripts, and priced the earlier Opus-only sessions from the token usage in their transcripts.

## Results (claimed, unverified)

- **Ten delegating sessions, 13 PRs:** 80% of a 5-hour window and $30.05 in total, about 6% and $2.31 per PR; a single-PR session moved the weekly counter by about 1%.
- **Before and after:** 24 earlier Opus-only single-PR sessions against those ten: average lines added per PR 248 against 392, average cost per PR $3.59 against $2.14, about 40% less. By his conversion this is roughly 16 PRs per 5-hour window instead of 10.
- **Where the saving comes from** (his claim, and the surprising part): not from Sonnet being cheaper. Pricing the subagents' tokens at Opus rates raises the ten sessions' cost by only about 5%, because most tokens in a Claude Code session are cache reads and those cost the same on Opus 5.5 and Sonnet 5.5 ($0.20 per million tokens when he measured). The saving is that the main session stays small: every request re-sends the whole conversation, so when Opus runs the edit-and-test loop itself each test output enlarges every later request. With the loop in a subagent the main session sees the plan and a short report; Opus sessions fell from 75 to 54 requests on average and from 119k to 107k tokens of context per request.
- **Price change (claimed, unverified):** he says Anthropic lowered the Sonnet 5.5 cache-read price to $0.10 per million tokens "today"; by his calculation that moves the ten sessions from $27.84 to $27.31 ($2.14 to $2.10 per PR), a small effect because subagents use few of each session's tokens.

## Caveats

- Dollar figures are the API-equivalent cost Claude Code computes, not what he pays (flat 20 EUR per month); his own recalculation ($27.84 for the ten sessions) is a few percent below the $30.05 Claude Code displayed, so he uses it only to compare groups.
- Small, non-randomised before/after comparison on one person's projects (10 against 24 sessions); PR size is the only control. No independent replication.
- Percentages are integers ("<1%" means no movement); limits are per account, so concurrent sessions bleed into each other's logs.
- He left out one release-day session (8 PRs in 4.5 hours, 25% of a window, $10.67) because including it would have flattered the numbers.
- `scoper` and `shipper` were added days before writing, so most rows use only `implementer`.
- Model names: Opus 5.5 and Sonnet 5.5 are current model ids; "Haiku 5.5" is *(reported, unverified in public catalogs)*: the newest Haiku id confirmed when this page was written is `claude-haiku-4-5`.

## Wiki connections

- [[concepts/model-tier-routing]]: agrees on tiering by task type (Haiku for mechanical and read-only work, Sonnet for implementation, Opus for decisions and review). Differs in the main-session default: he keeps the orchestrating session on Opus at medium effort as a standing role split, where our table makes Sonnet the default tier and reserves Opus for named task types. His cost finding also echoes the "wshobson finding" there that per-token price is not the whole story.
- [[concepts/agent-subagents]]: confirms the model-tiering table and the exploration-offloading pattern, and adds role-specialised agents (scoper, implementer, shipper) with hard turn caps, plan mode and the continue-the-same-agent-with-`SendMessage` habit.
- [[summaries/claude-usage-limits]]: that page lists the active model as a usage factor. Not a contradiction: this source argues that in long cache-heavy Claude Code sessions the size of the main session's context dominates the per-token price difference between tiers (claimed).
- [[concepts/context-compression]] and [[concepts/context-degradation]]: a smaller main-session context as a direct cost lever, via delegation instead of compaction.
- [[syntheses/agent-primitive-selection]]: a worked example of choosing subagents for context isolation and tool restriction.
