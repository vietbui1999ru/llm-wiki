---
title: "Subagent Cost Model"
type: concept
tags: [subagents, cost, model-routing, context-isolation, claude-code, prompt-caching]
sources:
  - "How I use Claude Code subagents to make my Claude Pro limits last longer.md"
  - "Building agents When to fold subagents into your main agent loop.md"
  - "anyone actually fold their subagents back in after that anthropic guide?  rClaudeAI.md"
created: 2026-10-09
updated: 2026-11-01
---

> **Contradiction (2026-11-01):** Anthropic's guide ([[summaries/fold-subagents-into-main-loop]]) says a single agent loop with skills "often" costs less and runs faster per task than a subagent design (claimed, unverified; one customer about 2x faster). This page says delegation lowers cost. The scopes differ: the guide targets enterprise agents split by team or domain, where each subagent is a nested model loop returning a lossy summary; this page targets coding loops whose edit-and-test output would otherwise grow the main context. The guide's own first keep-condition, measurable degradation from context bloat, is the context lever below. Treat the two as complementary until a measured comparison on coding work exists.

# Subagent Cost Model

Why delegating work to subagents lowers cost in Claude Code, how much of it is the cheaper model versus the smaller context, and when delegation does not pay. Prices are Anthropic first-party rates as published 2026-10-09 and change; recheck https://platform.claude.com/docs/en/about-claude/pricing before relying on a ratio.

## Mechanics

Every request sends the whole conversation again. With prompt caching, the resent prefix is billed at the cache-read price and only new tokens are billed at the write price, so session cost is dominated by **context size multiplied by number of requests**, not by output. Two levers follow:

1. **Context lever.** Run a loop that would grow the main context (edit, test, fix, test) inside a subagent. The subagent starts small, its context is discarded when it returns, and the main session keeps only the plan and a short report. Every later main-session request stays smaller.
2. **Price lever.** Run the loop on a cheaper model. Cache reads are the bulk of tokens, so the benefit depends on the cache-read price gap, not the headline input price.

Measured in [[summaries/claude-code-subagents-pro-limits]]: re-pricing the subagents' tokens at Opus rates raised cost only about 5%, while total cost per PR fell about 40%. Requests per Opus session fell 75 to 54 and context per request 119k to 107k. Most of that saving was the context lever. One user and a selected sample, so indicative only.

## Price table (per million tokens, 2026-10-09)

| Model | Input | Output | Cache read | Notes |
|---|---|---|---|---|
| Opus 5.5 | $4 | $20 | $0.20 | Fast mode $8 / $40 |
| Sonnet 5.5 | $2 | $10 | $0.10 | Cache read cut from $0.20 on 2026-10-07 |
| Haiku 5.5 | $0.10 | $0.50 | $0.01 | Prompts up to 100k; above that $0.50 / $2.50 / $0.05 |

Opus 5.5 is only about 2x Sonnet 5.5 on input and output, so "Opus costs several times Sonnet" is out of date. Haiku 5.5 is roughly 20x cheaper than Sonnet on input and 10x on cache read, which is why read-only exploration is the cleanest place to downgrade.

## Worked example (illustrative, not measured)

A 20-request edit-and-test loop that adds 3k tokens of context per request, counting cache reads only (cache writes and output excluded).

| | Starting context | Context summed over 20 requests | Cache-read price | Cost |
|---|---|---|---|---|
| In an Opus main session | 100k | 2.63M | $0.20 | about $0.53 |
| In a Sonnet subagent | 15k | 0.93M | $0.10 | about $0.09 |

The context lever contributes about 2.8x and the price lever about 2x. The 60k tokens the loop would have added to the main context also vanish from every later main request. The subagent's starting 15k assumes CLAUDE.md, the system prompt and the handoff; a large CLAUDE.md raises it unless the agent sets `omitClaudeMd: true`.

## When delegation does not pay

- **Handoff cost equals edit cost.** A small, fully known change is cheaper to write than to brief and then review. Keep it in the main session.
- **Stacked review.** A second review by another large model can cost nearly as much as writing the code. One default review in the main session; a dedicated reviewer only for risky changes.
- **Git steps.** A few hundred tokens of commands do not justify a handoff.
- **Agent teams.** About 7x the tokens in plan mode per the docs; use Sonnet teammates and keep teams small (https://code.claude.com/docs/en/agent-teams).
- **Judgment-heavy work.** Architecture, root cause, and security-sensitive changes stay with the strongest model; a cheaper model that redoes the work costs more than it saved.
- **Split by problem type, not context.** A subagent that needs much of the main context back, or whose output the main agent must re-verify in full, adds a nested loop's latency and tokens without shrinking the main context. Fold it into a skill plus tools ([[summaries/fold-subagents-into-main-loop]]).
- **A reviewer that rarely blocks anything.** Practitioners log what an independent checker blocks for about two weeks; if it is only nits and stale comments, its cost is not earned (anecdotal method from the same summary).

## Delegation that never fires costs the most

A subagent that the main session should use but does not is pure overhead: its definition sits in context and the main session does the reads itself. One practitioner reported a subagent whose description nearly matched the prompt was never auto-selected in 2 of 2 runs (the main thread made 19 reads); naming it explicitly gave one Agent call and 6.2k versus 18.1k context (single anecdote, unverified). This agrees with [[summaries/claude-code-subagents-pro-limits]], where a standing CLAUDE.md instruction, not the description, made delegation reliable.

## Controls that decide which model runs

Precedence for a subagent's model (https://code.claude.com/docs/en/sub-agents): the per-invocation `model` parameter, then the agent's frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main conversation model. The environment variable only fills gaps; it does not override frontmatter, and it does not change the built-in Explore and Plan agents unless `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` is set.

Effort resolves in this order (https://code.claude.com/docs/en/model-config): `CLAUDE_CODE_EFFORT_LEVEL` or `--effort` or `/effort`; then `modelSettings` or `effortLevel`; then the model default, which is medium for Opus 5.5, Sonnet 5.5 and Haiku 5.5. A subagent's `effort` frontmatter overrides the session level but not the environment variable. A top-level `effortLevel` in user settings does not apply to Opus 5.5.

Other cost keys on a subagent: `omitClaudeMd`, `maxTurns`, `permissionMode: plan` for read-only scouts, `background`, and `skills` preloading. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (default 3 layers) and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default 20) bound runaway fan-out.

## Measure before and after

Statusline JSON supplies `rate_limits.five_hour.used_percentage`, `rate_limits.seven_day.used_percentage`, `cost.total_cost_usd` and `session_id` (the rate-limit fields only for Pro/Max subscribers, after the first response). Logging a line whenever a percentage changes and matching sessions to PRs gives a cost-per-PR figure for your own workload. `cost.total_cost_usd` is a client-side estimate and resets on `/clear`. The docs do not state that it includes subagent requests, though subagent usage counts toward limits and appears in `/usage`.

## Application in this setup (as of 2026-10-09)

Implementation is dispatched to Pi under the plan-handoff rule, which moves it out of Claude usage entirely and is a stronger form of the context lever. In-Claude subagents are therefore mainly for read-only exploration and review. No custom agent roster is installed; `CLAUDE_CODE_SUBAGENT_MODEL` is set as a gap filler. No cost logging exists yet.

## Related Pages

- [[summaries/claude-code-subagents-pro-limits]] — the measured source and its caveats
- [[summaries/fold-subagents-into-main-loop]] — Anthropic's case for folding subagents into a single loop, and when not to
- [[concepts/agent-subagents]] — frontmatter, scopes, invocation
- [[concepts/model-tier-routing]] — which tier for which task
- [[concepts/context-compression]] — KV-cache stability and compaction
- [[syntheses/agent-primitive-selection]] — skill vs subagent vs team
