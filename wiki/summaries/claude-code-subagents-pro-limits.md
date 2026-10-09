---
title: "Claude Code Subagents to Stretch Pro Limits"
type: summary
tags: [subagents, cost, model-routing, claude-code, context-isolation, measurement]
sources: ["How I use Claude Code subagents to make my Claude Pro limits last longer.md"]
created: 2026-10-09
updated: 2026-10-09
---

# Claude Code Subagents to Stretch Pro Limits

A single developer's write-up (the author appears to own github.com/andreagrandi, inferred from the repo links; no byline in the capture) of moving a Claude Code workflow from Opus-only to Opus plus delegated subagents on the 20 EUR Pro plan, with measured cost per pull request. Captured 2026-10-09. The article states the cache-read price change as "today"; the release notes date it 2026-10-07.

## Setup

The main session runs Opus 5.5 at medium effort and makes decisions. Four custom agents live in `~/.claude/agents/`:

| Agent | Model | Effort | Tools | Job |
|---|---|---|---|---|
| `implementer` | Sonnet 5.5 | medium | Read, Write, Edit, Grep, Glob, Bash | Writes code and tests, runs checks |
| `reviewer` | Opus 5.5 | medium | Read, Grep, Glob, Bash | Reviews risky changes, only when asked |
| `scoper` | Haiku 5.5 | medium | Read, Grep, Glob, Bash; `permissionMode: plan`, `maxTurns: 12` | Gathers facts before planning an unfamiliar task |
| `shipper` | Haiku 5.5 | low | Read, Bash; `maxTurns: 10` | Commit, push, open the PR |

Delegation is not left to chance: the user `CLAUDE.md` carries a standing instruction naming when to delegate, what the handoff must contain (issue, acceptance criteria, files, decisions taken, validation commands), and how to review what comes back. Claude Code chooses subagents by their `description`, so the instruction is what makes delegation reliable.

## Rules that carry the saving

- **Break-even rule.** Small, fully known changes stay in the main session, because writing the handoff and reviewing the diff costs about as much as the edit.
- **One review.** The main session reads every diff and reruns the tests. The `reviewer` agent runs only on request or for security, concurrency, migrations and public-API changes. A second Opus review "can cost almost as much as writing the code".
- **Constrained scoper.** Plan mode, no edit tools, 12-turn cap, every claim must cite a file, and the main session spot-checks the files before trusting the brief.
- **Implementer reports, does not redesign.** A plan that conflicts with the code is reported back; the fix goes back to the same instance with `SendMessage` so it keeps context.
- **Shipper stops on anything odd** (unrelated file, default branch, missing changelog) and never edits files or force-pushes.

## Measured result

Per-session cost and the 5-hour and 7-day usage percentages come from a statusline script that appends to `~/.claude/usage-log.jsonl` whenever either percentage changes. Sessions are matched to PRs from `gh pr create` calls in transcripts.

| | Opus only | Opus + subagents |
|---|---|---|
| Sessions | 24 | 10 |
| PRs | 24 | 13 |
| Average lines added per PR | 248 | 392 |
| Average cost per PR | $3.59 | $2.14 |

Roughly 6% of a 5-hour window per PR, against about 10% Opus-only, so about 16 PRs per window instead of about 10. The arithmetic in the article is internally consistent (80% over 13 PRs, $27.84 over 13 PRs).

**Where the saving comes from.** Not from the cheaper model: pricing the subagents' tokens at Opus rates raises the ten sessions' cost only about 5%. Most session tokens are cache reads, which cost the same on Opus 5.5 and Sonnet 5.5 when these sessions ran ($0.20 per million). The saving is that the main context stays small: every request resends the whole conversation, so an edit-and-test loop in the main session inflates every later request. With the loop in a subagent, the main session sees the plan and a short report. Requests per Opus session fell from 75 to 54 and context per request from 119k to 107k tokens.

**Caveats.** One user, one workload, small samples. The delegating group is selected (sessions where a subagent was used) and the PRs are larger. The scoper and shipper were added days before measurement, so most rows use only the implementer. The cost is the author's own estimate and runs a few percent below Claude Code's figure; the dollar amount is not what Pro costs. One release-day session (eight PRs, 25% of a window) was excluded. Treat the 40% as indicative, not a benchmark.

## Verification against Anthropic docs (2026-10-09)

| Claim | Result | Source |
|---|---|---|
| Frontmatter keys `model`, `effort`, `tools`, `permissionMode: plan`, `maxTurns`, `color` | Verified; the docs list about ten more keys | https://code.claude.com/docs/en/sub-agents |
| Subagent starts with empty context | Verified; it does receive CLAUDE.md and a git status snapshot (built-in Explore and Plan skip both; `omitClaudeMd: true` opts a custom agent out) | same |
| Continue a subagent with `SendMessage` | Verified; does not require agent teams | same |
| `modelSettings` per-model effort in settings.json | Verified, v2.1.251+. A top-level `effortLevel` in user settings does not count for Opus 5.5 | https://code.claude.com/docs/en/settings-reference#modelsettings, https://code.claude.com/docs/en/model-config |
| Statusline JSON has `rate_limits.*.used_percentage`, `cost.total_cost_usd`, `session_id` | Verified; `rate_limits` appears only for Pro/Max subscribers, after the first API response | https://code.claude.com/docs/en/statusline |
| "Use proactively" in `description` drives automatic delegation | Verified | sub-agents page |
| Sonnet 5.5 cache read lowered $0.20 to $0.10 | Verified; effective 2026-10-07. Opus 5.5 stays $0.20, Haiku 5.5 is $0.01 (prompts up to 100k) | https://platform.claude.com/docs/en/release-notes/overview, https://platform.claude.com/docs/en/about-claude/pricing |
| Subagent cost included in the session total | Not stated. Docs say subagent requests count toward the same usage limits and show in the `/usage` breakdown | https://code.claude.com/docs/en/costs |

## Cost levers the article does not use

From the docs: the `omitClaudeMd`, `background`, `skills` and `hooks` subagent keys; PreToolUse hooks that filter test and log output; moving long CLAUDE.md sections into on-demand skills; `/clear` between tasks; and `/usage` cache-miss flags. Agent teams cost about 7x the tokens in plan mode, so teammates should use Sonnet and teams stay small (https://code.claude.com/docs/en/agent-teams).

## Wiki connections

- [[concepts/subagent-cost-model]] — the mechanics distilled from this source and the docs
- [[concepts/agent-subagents]] — frontmatter, scopes, invocation; corrected by this ingest
- [[concepts/model-tier-routing]] — tier table; precedence and price ratios added
- [[syntheses/agent-primitive-selection]] — decision tree
- [[concepts/context-degradation]] — why a small main context also helps quality
